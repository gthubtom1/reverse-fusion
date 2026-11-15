param(
    [string]$Destination = (Join-Path $PSScriptRoot '..\vendor\wabt\1.0.42\windows-x64')
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
$manifestPath = Join-Path $PSScriptRoot '..\vendor\wabt\1.0.42\manifest.json'
$manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json
$destination = Assert-RepositoryWritePath $repo $Destination
New-Item -ItemType Directory -Path $destination -Force | Out-Null
$archive = Assert-RepositoryWritePath $repo (Join-Path $destination 'wabt-1.0.42-windows-x64.tar.gz')
if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) {
    Invoke-WebRequest -Uri $manifest.source -OutFile $archive
}
$archiveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant()
if ($archiveHash -ne $manifest.archive_sha256) { throw "WABT archive SHA-256 mismatch: $archiveHash" }
$bin = Assert-RepositoryWritePath $repo (Join-Path $destination 'wabt-1.0.42\bin')
$extract = $false
foreach ($name in $manifest.required_tools) {
    $path = Join-Path $bin $name
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { $extract = $true; break }
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant() -ne $manifest.bin_sha256.$name) { $extract = $true; break }
}
if ($extract) {
    $expanded = Assert-RepositoryWritePath $repo (Join-Path $destination 'wabt-1.0.42')
    if (Test-Path -LiteralPath $expanded) { Remove-Item -LiteralPath $expanded -Recurse -Force }
    tar -xzf $archive -C $destination
    Assert-NativeExit $LASTEXITCODE 'WABT archive extraction'
}
foreach ($name in $manifest.required_tools) {
    $path = Join-Path $bin $name
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing WABT tool: $path" }
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
    if ($hash -ne $manifest.bin_sha256.$name) { throw "WABT tool SHA-256 mismatch: $name" }
    $version = (& $path --version | Out-String).Trim()
    Assert-NativeExit $LASTEXITCODE "WABT version probe: $name"
    if ($version -ne $manifest.version) { throw "Unexpected WABT version for $name`: $version" }
}
Write-Output (ConvertTo-Json @{ status = 'ready'; bin = $bin; archive_sha256 = $archiveHash; version = $manifest.version } -Compress)
