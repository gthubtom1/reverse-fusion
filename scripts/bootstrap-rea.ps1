param(
    [string]$Destination = (Join-Path $PSScriptRoot '..\vendor\rea'),
    [string]$NodePath = $env:REVERSE_FUSION_NODE
)
$ErrorActionPreference = 'Stop'
$manifestPath = Join-Path $PSScriptRoot '..\vendor\rea\manifest.json'
$manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json
$destination = [IO.Path]::GetFullPath($Destination)
New-Item -ItemType Directory -Path $destination -Force | Out-Null
$archive = Join-Path $destination ("{0}-{1}.tgz" -f $manifest.package, $manifest.version)
if (-not (Test-Path -LiteralPath $archive)) { npm pack ("{0}@{1}" -f $manifest.package, $manifest.version) --pack-destination $destination | Out-Null }
$hashHex = (Get-FileHash -Algorithm SHA512 -LiteralPath $archive).Hash
$hashBytes = for ($index = 0; $index -lt $hashHex.Length; $index += 2) { [Convert]::ToByte($hashHex.Substring($index, 2), 16) }
$actual = [Convert]::ToBase64String([byte[]]$hashBytes)
$expected = $manifest.integrity -replace '^sha512-', ''
if ($actual -ne $expected) { throw "REA package integrity mismatch" }
$packageRoot = Join-Path $destination 'package'
if (-not (Test-Path -LiteralPath (Join-Path $packageRoot $manifest.entry.Replace('package/','')))) {
    tar -xzf $archive -C $destination
}
if (-not $NodePath) { $NodePath = 'node' }
$entry = Join-Path $packageRoot 'scripts\rea.mjs'
if (-not (Test-Path -LiteralPath $entry)) { throw "REA entry missing: $entry" }
Write-Output (ConvertTo-Json @{ status='ready'; node=$NodePath; script=$entry; package=$manifest.package; version=$manifest.version; integrity=$manifest.integrity } -Compress)
