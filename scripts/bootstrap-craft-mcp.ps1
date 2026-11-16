param(
    [switch]$BuildFromSource,
    [string]$CargoPath = 'cargo',
    [string]$RustcPath = '',
    [string]$GccDirectory = ''
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib/ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
if ($env:OS -ne 'Windows_NT' -or [Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'X64') {
    throw 'Craft MCP distribution is qualified only for Windows x64; deployment is incomplete on this platform'
}
$manifestPath = Join-Path $repo 'components/craft-mcp/manifest.json'
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
$asset = $manifest.platforms.'windows-x64'
$binary = Assert-RepositoryWritePath $repo (Join-Path $repo $asset.local_path)
$destination = Split-Path -Parent $binary
New-Item -ItemType Directory -Path $destination -Force | Out-Null

if ($BuildFromSource) {
    $source = Assert-RepositoryWritePath $repo (Join-Path $repo 'vendor/craft/mcp-upstream')
    if (-not (Test-Path -LiteralPath (Join-Path $source '.git'))) {
        if ((Test-Path -LiteralPath $source) -and (Get-ChildItem -LiteralPath $source -Force | Select-Object -First 1)) {
            throw 'Craft source destination is not empty'
        }
        & git clone --filter=blob:none --no-checkout $manifest.upstream.repository $source
        Assert-NativeExit $LASTEXITCODE 'Craft MCP source clone'
        & git -C $source checkout --detach $manifest.upstream.commit
        Assert-NativeExit $LASTEXITCODE 'Craft MCP pinned checkout'
    }
    $head = (& git -C $source rev-parse HEAD | Out-String).Trim()
    Assert-NativeExit $LASTEXITCODE 'Craft MCP source identity'
    if ($head -ne $manifest.upstream.commit) { throw 'Craft source HEAD differs from MCP pin' }
    foreach ($patch in $manifest.patches) {
        $patchPath = Join-Path $repo $patch.path
        if ((Get-FileHash -LiteralPath $patchPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $patch.sha256) {
            throw 'Craft MCP patch digest mismatch'
        }
        $previousErrorPolicy = $ErrorActionPreference
        try {
            $ErrorActionPreference = 'Continue'
            & git -C $source apply --reverse --check $patchPath 2>$null
            $alreadyApplied = $LASTEXITCODE -eq 0
        } finally { $ErrorActionPreference = $previousErrorPolicy }
        if (-not $alreadyApplied) {
            & git -C $source apply --check $patchPath
            Assert-NativeExit $LASTEXITCODE 'Craft MCP patch precondition'
            & git -C $source apply $patchPath
            Assert-NativeExit $LASTEXITCODE 'Craft MCP patch apply'
        }
    }
    $changed = @(& git -C $source diff HEAD --name-only)
    Assert-NativeExit $LASTEXITCODE 'Craft MCP patch status'
    $untracked = @(& git -C $source ls-files --others --exclude-standard)
    Assert-NativeExit $LASTEXITCODE 'Craft MCP untracked status'
    if ($untracked.Count -or @($changed | Where-Object { $_ -notin $manifest.patched_files.PSObject.Properties.Name }).Count) {
        throw 'Craft source contains changes outside recorded MCP patch'
    }
    foreach ($file in $manifest.patched_files.PSObject.Properties) {
        $text = [IO.File]::ReadAllText((Join-Path $source $file.Name)).Replace("`r`n", "`n")
        $hasher = [Security.Cryptography.SHA256]::Create()
        try { $actual = [BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($text))).Replace('-', '').ToLowerInvariant() }
        finally { $hasher.Dispose() }
        if ($actual -ne $file.Value) { throw "Craft MCP patched source mismatch: $($file.Name)" }
    }
    $previousRustc = $env:RUSTC
    $previousPath = $env:PATH
    $previousTarget = $env:CARGO_TARGET_DIR
    try {
        if ($RustcPath) { $env:RUSTC = $RustcPath }
        if ($GccDirectory) { $env:PATH = $GccDirectory + [IO.Path]::PathSeparator + $env:PATH }
        $env:CARGO_TARGET_DIR = Assert-RepositoryWritePath $repo (Join-Path $repo 'vendor/craft/build')
        & $CargoPath build --release --locked --manifest-path (Join-Path $repo 'components/craft-mcp/Cargo.toml') --target x86_64-pc-windows-gnu
        Assert-NativeExit $LASTEXITCODE 'Craft MCP release build'
        Copy-Item -LiteralPath (Join-Path $env:CARGO_TARGET_DIR 'x86_64-pc-windows-gnu/release/reverse-fusion-craft-mcp.exe') -Destination $binary -Force
    } finally {
        $env:RUSTC = $previousRustc
        $env:PATH = $previousPath
        $env:CARGO_TARGET_DIR = $previousTarget
    }
    $distribution = 'source-build'
} else {
    $requiredSourceNames = @((Get-ChildItem -LiteralPath (Join-Path $repo 'components/craft-mcp/src') -Filter '*.rs' -File -Recurse | ForEach-Object { $_.FullName.Substring($repo.Length + 1).Replace('\','/') })) + @('components/craft-mcp/Cargo.toml', 'components/craft-mcp/Cargo.lock')
    if (@($manifest.adapter_source_sha256.PSObject.Properties).Count -ne $requiredSourceNames.Count) { throw 'Craft MCP packaged source binding is incomplete' }
    foreach ($name in $requiredSourceNames) {
        $expectedSource = $manifest.adapter_source_sha256.$name
        if ($expectedSource -notmatch '^[a-f0-9]{64}$') { throw "Craft MCP packaged source binding missing: $name" }
        $text = [IO.File]::ReadAllText((Join-Path $repo $name)).Replace("`r`n", "`n")
        $hasher = [Security.Cryptography.SHA256]::Create()
        try { $actualSource = [BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($text))).Replace('-', '').ToLowerInvariant() }
        finally { $hasher.Dispose() }
        if ($actualSource -ne $expectedSource) { throw "Craft MCP packaged source changed: $name; rebuild and qualify before using the pinned binary" }
    }
    foreach ($value in @($asset.binary_sha256, $asset.archive_sha256, $asset.notices_sha256, $asset.dependency_notices_sha256)) {
        if ($value -notmatch '^[a-f0-9]{64}$') { throw 'Craft MCP release has not been packaged and verified' }
    }
    $expected = @{}
    $expected[[IO.Path]::GetFileName($binary)] = $asset.binary_sha256
    $expected['THIRD-PARTY-NOTICES.txt'] = $asset.notices_sha256
    $expected['dependency-notices.json'] = $asset.dependency_notices_sha256
    $installedFilesMatch = $true
    foreach ($entryName in $expected.Keys) {
        $path = Join-Path $destination $entryName
        if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or
            (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected[$entryName]) {
            $installedFilesMatch = $false
        }
    }
    if (-not $installedFilesMatch) {
        $archive = Assert-RepositoryWritePath $repo (Join-Path $repo 'vendor/craft/mcp/craft-mcp-windows-x64.zip')
        if (-not (Test-Path -LiteralPath $archive) -or
            (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $asset.archive_sha256) {
            Invoke-WebRequest -Uri $asset.archive_url -OutFile $archive -UseBasicParsing
        }
        if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $asset.archive_sha256) {
            throw 'Craft MCP archive digest mismatch'
        }
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [IO.Compression.ZipFile]::OpenRead($archive)
        try {
            $entryNames = @($zip.Entries | ForEach-Object { $_.FullName })
            if ($zip.Entries.Count -ne 3 -or @($entryNames | Select-Object -Unique).Count -ne 3 -or
                @($entryNames | Where-Object { -not $expected.ContainsKey($_) }).Count) {
                throw 'Craft MCP archive contains unexpected or duplicate entries'
            }
            foreach ($entry in $zip.Entries) {
                $path = Assert-RepositoryWritePath $repo (Join-Path $destination $entry.FullName)
                [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $path, $true)
            }
        } finally { $zip.Dispose() }
        foreach ($entryName in $expected.Keys) {
            if ((Get-FileHash -LiteralPath (Join-Path $destination $entryName) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected[$entryName]) {
                throw "Craft MCP installed asset digest mismatch: $entryName"
            }
        }
    }
    $distribution = 'pinned-release'
}
$version = (& $binary --version | Out-String).Trim()
Assert-NativeExit $LASTEXITCODE 'Craft MCP executable identity'
$expectedVersion = "reverse-fusion-craft-mcp $($manifest.adapter_version) / Craft engine $($manifest.upstream.version) / $($manifest.upstream.commit)"
if ($version -ne $expectedVersion) { throw 'Craft MCP executable version does not match manifest' }
$inputs = @{}
foreach ($name in @($manifest.adapter_source_sha256.PSObject.Properties.Name) + @('components/craft-mcp/manifest.json') + @($manifest.patches.path)) {
    $inputs[$name] = (Get-FileHash -LiteralPath (Join-Path $repo $name) -Algorithm SHA256).Hash.ToLowerInvariant()
}
$receipt = Assert-RepositoryWritePath $repo (Join-Path $repo 'state/craft-mcp-runtime.json')
New-Item -ItemType Directory -Path (Split-Path -Parent $receipt) -Force | Out-Null
$result = @{schema_version=1; repository_root=$repo; distribution=$distribution; binary_sha256=(Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash.ToLowerInvariant(); source_inputs=$inputs; status='installed'; version=$version; protocol='stdio'; upstream_commit=$manifest.upstream.commit; business_acceptance='not-performed'}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding utf8
$result | ConvertTo-Json -Depth 8 -Compress
