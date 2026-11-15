param(
    [string]$Destination = (Join-Path $PSScriptRoot '..\vendor\rea'),
    [string]$NodePath = $env:REVERSE_FUSION_NODE
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
$manifestPath = Join-Path $PSScriptRoot '..\vendor\rea\manifest.json'
$manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json
$destination = Assert-RepositoryWritePath $repo $Destination
New-Item -ItemType Directory -Path $destination -Force | Out-Null
if (-not $NodePath) { $NodePath = 'node' }
$nodeVersionText = (& $NodePath --version 2>&1 | Out-String).Trim()
Assert-NativeExit $LASTEXITCODE 'Node version probe'
if ($nodeVersionText -notmatch '^v?(\d+)\.(\d+)\.(\d+)$') { throw "Unrecognized Node version: $nodeVersionText" }
$nodeVersion = [version]("{0}.{1}.{2}" -f $Matches[1],$Matches[2],$Matches[3])
$supported = (($nodeVersion.Major -eq 22 -and $nodeVersion -ge [version]'22.23.4') -or
    ($nodeVersion.Major -eq 24 -and $nodeVersion -ge [version]'24.22.1') -or
    ($nodeVersion -ge [version]'26.12.1'))
if ($manifest.node_engine -ne '^22.23.4 || ^24.22.1 || >=26.12.1' -or -not $supported) {
    throw "Node $nodeVersion does not satisfy REA engine $($manifest.node_engine)"
}
$archive = Assert-RepositoryWritePath $repo (Join-Path $destination ("{0}-{1}.tgz" -f $manifest.package, $manifest.version))
if (-not (Test-Path -LiteralPath $archive)) {
    npm pack ("{0}@{1}" -f $manifest.package, $manifest.version) --pack-destination $destination | Out-Null
    Assert-NativeExit $LASTEXITCODE 'REA npm pack'
}
$hashHex = (Get-FileHash -Algorithm SHA512 -LiteralPath $archive).Hash
$hashBytes = for ($index = 0; $index -lt $hashHex.Length; $index += 2) { [Convert]::ToByte($hashHex.Substring($index, 2), 16) }
$actual = [Convert]::ToBase64String([byte[]]$hashBytes)
$expected = $manifest.integrity -replace '^sha512-', ''
if ($actual -ne $expected) { throw "REA package integrity mismatch" }
$packageRoot = Assert-RepositoryWritePath $repo (Join-Path $destination 'package')
$packageJsonPath = Join-Path $packageRoot 'package.json'
$entry = Join-Path $destination $manifest.entry.Replace('/', [IO.Path]::DirectorySeparatorChar)
$extract = -not (Test-Path -LiteralPath $entry -PathType Leaf) -or -not (Test-Path -LiteralPath $packageJsonPath -PathType Leaf)
if (-not $extract) {
    try {
        $packageJson = Get-Content -Raw -LiteralPath $packageJsonPath | ConvertFrom-Json
        $extract = $packageJson.name -ne $manifest.package -or $packageJson.version -ne $manifest.version -or $packageJson.engines.node -ne $manifest.node_engine
    } catch { $extract = $true }
}
if ($extract) {
    if (Test-Path -LiteralPath $packageRoot) { Remove-Item -LiteralPath $packageRoot -Recurse -Force }
    tar -xzf $archive -C $destination
    Assert-NativeExit $LASTEXITCODE 'REA archive extraction'
}
if (-not (Test-Path -LiteralPath $entry)) { throw "REA entry missing: $entry" }
$packageJson = Get-Content -Raw -LiteralPath $packageJsonPath | ConvertFrom-Json
if ($packageJson.name -ne $manifest.package -or $packageJson.version -ne $manifest.version -or $packageJson.engines.node -ne $manifest.node_engine) {
    throw 'Extracted REA package identity or Node engine mismatch'
}
Write-Output (ConvertTo-Json @{ status='ready'; node=$NodePath; node_version=$nodeVersion.ToString(); node_engine=$manifest.node_engine; script=$entry; package=$manifest.package; version=$manifest.version; integrity=$manifest.integrity } -Compress)
