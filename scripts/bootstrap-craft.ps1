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
    throw 'Craft native distribution is currently qualified only for Windows x64; do not report deployment complete on this platform'
}
$manifestPath = Join-Path $repo 'components/craft-native/manifest.json'
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
$asset = $manifest.platforms.'windows-x64'
$binary = Assert-RepositoryWritePath $repo (Join-Path $repo $asset.local_path)
New-Item -ItemType Directory -Path (Split-Path -Parent $binary) -Force | Out-Null
if ($BuildFromSource) {
    $source = Assert-RepositoryWritePath $repo (Join-Path $repo 'vendor/craft/upstream')
    if (-not (Test-Path -LiteralPath (Join-Path $source '.git'))) {
        if ((Test-Path -LiteralPath $source) -and (Get-ChildItem -LiteralPath $source -Force | Select-Object -First 1)) { throw 'Craft source destination is not empty' }
        & git clone --filter=blob:none --no-checkout $manifest.upstream.repository $source
        Assert-NativeExit $LASTEXITCODE 'Craft source clone'
        & git -C $source checkout --detach $manifest.upstream.commit
        Assert-NativeExit $LASTEXITCODE 'Craft pinned checkout'
    }
    $head = (& git -C $source rev-parse HEAD | Out-String).Trim()
    Assert-NativeExit $LASTEXITCODE 'Craft source identity'
    if ($head -ne $manifest.upstream.commit) { throw 'Craft source HEAD differs from pin' }
    foreach ($patch in $manifest.patches) {
        $patchPath = Join-Path $repo $patch.path
        if ((Get-FileHash -LiteralPath $patchPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $patch.sha256) { throw 'Craft patch digest mismatch' }
        $previousErrorPolicy = $ErrorActionPreference
        try {
            $ErrorActionPreference = 'Continue'
            & git -C $source apply --reverse --check $patchPath 2>$null
            $alreadyApplied = $LASTEXITCODE -eq 0
        } finally { $ErrorActionPreference = $previousErrorPolicy }
        if (-not $alreadyApplied) {
            & git -C $source apply --check $patchPath
            Assert-NativeExit $LASTEXITCODE 'Craft patch precondition'
            & git -C $source apply $patchPath
            Assert-NativeExit $LASTEXITCODE 'Craft patch apply'
        }
    }
    $changed = @(& git -C $source diff HEAD --name-only)
    Assert-NativeExit $LASTEXITCODE 'Craft patch status'
    $untracked = @(& git -C $source ls-files --others --exclude-standard)
    Assert-NativeExit $LASTEXITCODE 'Craft untracked status'
    if ($untracked.Count -or @($changed | Where-Object { $_ -notin $manifest.patched_files.PSObject.Properties.Name }).Count) { throw 'Craft source contains changes outside recorded patches' }
    foreach ($file in $manifest.patched_files.PSObject.Properties) {
        $text = [IO.File]::ReadAllText((Join-Path $source $file.Name)).Replace("`r`n", "`n")
        $hasher = [Security.Cryptography.SHA256]::Create()
        try { $actual = [BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($text))).Replace('-', '').ToLowerInvariant() }
        finally { $hasher.Dispose() }
        if ($actual -ne $file.Value) { throw "Craft patched source mismatch: $($file.Name)" }
    }
    $previousRustc = $env:RUSTC
    $previousPath = $env:PATH
    $previousTarget = $env:CARGO_TARGET_DIR
    try {
        if ($RustcPath) { $env:RUSTC = $RustcPath }
        if ($GccDirectory) { $env:PATH = $GccDirectory + [IO.Path]::PathSeparator + $env:PATH }
        $env:CARGO_TARGET_DIR = Assert-RepositoryWritePath $repo (Join-Path $repo 'vendor/craft/build')
        & $CargoPath build --locked --manifest-path (Join-Path $repo 'components/craft-native/Cargo.toml') --target x86_64-pc-windows-gnu
        Assert-NativeExit $LASTEXITCODE 'Craft native build'
        Copy-Item -LiteralPath (Join-Path $env:CARGO_TARGET_DIR 'x86_64-pc-windows-gnu/debug/reverse-fusion-craft-native.exe') -Destination $binary -Force
    } finally {
        $env:RUSTC = $previousRustc
        $env:PATH = $previousPath
        $env:CARGO_TARGET_DIR = $previousTarget
    }
    $distribution = 'source-build'
} else {
    if (-not (Test-Path -LiteralPath $binary) -or (Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $asset.binary_sha256) {
        if ($asset.archive_sha256 -notmatch '^[a-f0-9]{64}$') { throw 'Craft release has not been packaged and verified' }
        $archive = Assert-RepositoryWritePath $repo (Join-Path $repo 'vendor/craft/native/craft-native-windows-x64.zip')
        if (-not (Test-Path -LiteralPath $archive) -or (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $asset.archive_sha256) {
            Invoke-WebRequest -Uri $asset.archive_url -OutFile $archive -UseBasicParsing
        }
        if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $asset.archive_sha256) { throw 'Craft archive digest mismatch' }
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [IO.Compression.ZipFile]::OpenRead($archive)
        try {
            $entries = @([IO.Path]::GetFileName($binary), 'THIRD-PARTY-NOTICES.txt')
            if ($zip.Entries.Count -ne 2 -or @($zip.Entries | Where-Object { $_.FullName -notin $entries }).Count) { throw 'Craft archive contains unexpected entries' }
            foreach ($entry in $zip.Entries) {
                [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, (Join-Path (Split-Path -Parent $binary) $entry.FullName), $true)
            }
        } finally { $zip.Dispose() }
        if ((Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $asset.binary_sha256) { throw 'Craft binary digest mismatch' }
        if ((Get-FileHash -LiteralPath (Join-Path (Split-Path -Parent $binary) 'THIRD-PARTY-NOTICES.txt') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $asset.notices_sha256) { throw 'Craft notices digest mismatch' }
    }
    $distribution = 'pinned-release'
}
$caps = '{"op":"capabilities"}' | & $binary
Assert-NativeExit $LASTEXITCODE 'Craft native capabilities'
$capability = $caps | ConvertFrom-Json
if (-not $capability.ok -or $capability.data.upstream_commit -ne $manifest.upstream.commit -or $capability.data.windows_command_tail_version -ne 1 -or $capability.data.adapter_version -ne $manifest.adapter_version -or 'abort' -notin $capability.data.capabilities) { throw 'Craft native engine identity mismatch' }
$inputs = @{}
foreach ($name in @('components/craft-native/src/main.rs','components/craft-native/Cargo.toml','components/craft-native/Cargo.lock','components/craft-native/manifest.json') + @($manifest.patches.path)) {
    $inputs[$name] = (Get-FileHash -LiteralPath (Join-Path $repo $name) -Algorithm SHA256).Hash.ToLowerInvariant()
}
$receipt = Assert-RepositoryWritePath $repo (Join-Path $repo 'state/craft-runtime.json')
New-Item -ItemType Directory -Path (Split-Path -Parent $receipt) -Force | Out-Null
$result = @{schema_version=1;repository_root=$repo;distribution=$distribution;binary_sha256=(Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash.ToLowerInvariant();source_inputs=$inputs;status='installed';capabilities=$capability.data;business_acceptance='not-performed'}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding utf8
$result | ConvertTo-Json -Depth 8 -Compress
