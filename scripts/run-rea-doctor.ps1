param(
    [string]$Output = (Join-Path $PSScriptRoot '..\state\rea-mcp-doctor.json'),
    [string]$NodePath = $env:REVERSE_FUSION_NODE,
    [string]$ReaScript = $env:REVERSE_FUSION_REA_SCRIPT
)

$ErrorActionPreference = 'Stop'
$reaBootstrap = Join-Path $PSScriptRoot 'bootstrap-rea.ps1'
$rea = & powershell -NoProfile -File $reaBootstrap -NodePath $NodePath | ConvertFrom-Json
if (-not $NodePath) { $NodePath = $rea.node }
if (-not $ReaScript) { $ReaScript = $rea.script }
$bootstrap = Join-Path $PSScriptRoot 'bootstrap-wabt.ps1'
$bootstrapResult = & powershell -NoProfile -File $bootstrap | ConvertFrom-Json
$env:REA_WABT_BIN_DIRECTORY = $bootstrapResult.bin
$outputPath = [IO.Path]::GetFullPath($Output)
New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($outputPath)) -Force | Out-Null
& $NodePath $ReaScript mcp doctor --format json | Out-File -LiteralPath $outputPath -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw "REA MCP doctor failed with exit code $LASTEXITCODE" }
$result = Get-Content -Raw $outputPath | ConvertFrom-Json
Write-Output (ConvertTo-Json @{ status = if ($result.healthy) { 'pass' } else { 'fail' }; output = $outputPath; rea = $result.server.version; tools = $result.inventory.tools.observed; prompts = $result.inventory.prompts.observed; catalog_digest = $result.identity.observed_catalog_digest } -Compress)
