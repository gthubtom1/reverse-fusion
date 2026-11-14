param(
    [string]$Destination = (Join-Path $PSScriptRoot '..\vendor\jadx-headless-mcp\0.7.1')
)

$ErrorActionPreference = 'Stop'
$manifestPath = Join-Path $PSScriptRoot '..\vendor\jadx-headless-mcp\0.7.1\manifest.json'
$manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json
$destination = [IO.Path]::GetFullPath($Destination)
New-Item -ItemType Directory -Path $destination -Force | Out-Null
$jar = Join-Path $destination $manifest.artifact
$checksum = Join-Path $destination 'jadx-headless-mcp.sha256'
if (-not (Test-Path -LiteralPath $jar)) {
    Invoke-WebRequest -Uri $manifest.source -OutFile $jar
}
if (-not (Test-Path -LiteralPath $checksum)) {
    Invoke-WebRequest -Uri $manifest.checksum_source -OutFile $checksum
}
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $jar).Hash.ToLowerInvariant()
if ($actual -ne $manifest.sha256) { throw "JADX headless MCP SHA-256 mismatch: $actual" }
$published = (Get-Content -Raw $checksum).Trim().Split()[0].ToLowerInvariant()
if ($published -ne $actual) { throw "Published JADX checksum mismatch: $published" }
Write-Output (ConvertTo-Json @{ status = 'ready'; jar = $jar; sha256 = $actual; version = $manifest.version; config_mutation = $false } -Compress)
