param(
    [string]$Destination = (Join-Path $PSScriptRoot '..\vendor\jadx-headless-mcp\0.7.1')
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
$manifestPath = Join-Path $PSScriptRoot '..\vendor\jadx-headless-mcp\0.7.1\manifest.json'
$manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json
$destination = Assert-RepositoryWritePath $repo $Destination
New-Item -ItemType Directory -Path $destination -Force | Out-Null
$jar = Assert-RepositoryWritePath $repo (Join-Path $destination $manifest.artifact)
$checksum = Assert-RepositoryWritePath $repo (Join-Path $destination 'jadx-headless-mcp.sha256')
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
[void][Reflection.Assembly]::LoadWithPartialName('System.IO.Compression.FileSystem')
$zip = [IO.Compression.ZipFile]::OpenRead($jar)
try {
    $entries = @{}; foreach ($entry in $zip.Entries) { $entries[$entry.FullName] = $true }
    foreach ($required in $manifest.required_classes) {
        if (-not $entries.ContainsKey($required)) { throw "JADX JAR required class missing: $required" }
    }
} finally { $zip.Dispose() }
Write-Output (ConvertTo-Json @{ status = 'ready'; jar = $jar; sha256 = $actual; version = $manifest.version; config_mutation = $false } -Compress)
