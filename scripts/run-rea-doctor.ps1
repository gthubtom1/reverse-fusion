param(
    [string]$Output = (Join-Path $PSScriptRoot '..\state\rea-mcp-doctor.json'),
    [string]$NodePath = $env:REVERSE_FUSION_NODE,
    [string]$ReaScript = $env:REVERSE_FUSION_REA_SCRIPT
)

$ErrorActionPreference = 'Stop'
if (-not $NodePath -or -not $ReaScript) {
    $receiptPath = Join-Path $env:LOCALAPPDATA 'reverse-workflow\.installer\receipt.json'
    if (-not (Test-Path -LiteralPath $receiptPath)) { throw 'Set REVERSE_FUSION_NODE and REVERSE_FUSION_REA_SCRIPT for this host' }
    $receipt = Get-Content -Raw $receiptPath | ConvertFrom-Json
    if (-not $NodePath) { $NodePath = $receipt.runtime.node }
    if (-not $ReaScript) { $ReaScript = Join-Path $receipt.paths.rea_package 'scripts\rea.mjs' }
}
$bootstrap = Join-Path $PSScriptRoot 'bootstrap-wabt.ps1'
$bootstrapResult = & powershell -NoProfile -File $bootstrap | ConvertFrom-Json
$env:REA_WABT_BIN_DIRECTORY = $bootstrapResult.bin
$outputPath = [IO.Path]::GetFullPath($Output)
New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($outputPath)) -Force | Out-Null
& $NodePath $ReaScript mcp doctor --format json | Out-File -LiteralPath $outputPath -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw "REA MCP doctor failed with exit code $LASTEXITCODE" }
$result = Get-Content -Raw $outputPath | ConvertFrom-Json
Write-Output (ConvertTo-Json @{ status = if ($result.healthy) { 'pass' } else { 'fail' }; output = $outputPath; rea = $result.server.version; tools = $result.inventory.tools.observed; prompts = $result.inventory.prompts.observed; catalog_digest = $result.identity.observed_catalog_digest } -Compress)
