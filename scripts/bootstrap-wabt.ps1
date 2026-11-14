param(
    [string]$Destination = (Join-Path $PSScriptRoot '..\vendor\wabt\1.0.42\windows-x64')
)

$ErrorActionPreference = 'Stop'
$manifestPath = Join-Path $PSScriptRoot '..\vendor\wabt\1.0.42\manifest.json'
$manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json
$destination = [IO.Path]::GetFullPath($Destination)
New-Item -ItemType Directory -Path $destination -Force | Out-Null
$archive = Join-Path $destination 'wabt-1.0.42-windows-x64.tar.gz'
Invoke-WebRequest -Uri $manifest.source -OutFile $archive
$archiveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant()
if ($archiveHash -ne $manifest.archive_sha256) { throw "WABT archive SHA-256 mismatch: $archiveHash" }
tar -xzf $archive -C $destination
$bin = Join-Path $destination 'wabt-1.0.42\bin'
foreach ($name in $manifest.required_tools) {
    $path = Join-Path $bin $name
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing WABT tool: $path" }
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
    if ($hash -ne $manifest.bin_sha256.$name) { throw "WABT tool SHA-256 mismatch: $name" }
    $version = (& $path --version | Out-String).Trim()
    if ($version -ne $manifest.version) { throw "Unexpected WABT version for $name`: $version" }
}
Write-Output (ConvertTo-Json @{ status = 'ready'; bin = $bin; archive_sha256 = $archiveHash; version = $manifest.version } -Compress)
