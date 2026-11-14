param(
    [string]$Fixture = (Join-Path $PSScriptRoot '..\fixtures\answer.wasm'),
    [string]$EvidenceOut = (Join-Path $PSScriptRoot '..\state\rea-wasm-evidence.json'),
    [string]$NodePath = $env:REVERSE_FUSION_NODE,
    [string]$ReaScript = $env:REVERSE_FUSION_REA_SCRIPT
)

$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$fixturePath = [IO.Path]::GetFullPath($Fixture)
$evidencePath = [IO.Path]::GetFullPath($EvidenceOut)
if (-not (Test-Path -LiteralPath $fixturePath)) { throw "Fixture not found: $fixturePath" }

$reaBootstrap = Join-Path $PSScriptRoot 'bootstrap-rea.ps1'
$rea = & powershell -NoProfile -File $reaBootstrap -NodePath $NodePath | ConvertFrom-Json
if (-not $NodePath) { $NodePath = $rea.node }
if (-not $ReaScript) { $ReaScript = $rea.script }
$bootstrap = Join-Path $PSScriptRoot 'bootstrap-wabt.ps1'
$bootstrapResult = & powershell -NoProfile -File $bootstrap | ConvertFrom-Json
$env:REA_WABT_BIN_DIRECTORY = $bootstrapResult.bin
New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($evidencePath)) -Force | Out-Null
& $NodePath $ReaScript inspect-wasm-artifact $fixturePath --format json --full-output | Out-File -LiteralPath $evidencePath -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw "REA inspect-wasm-artifact failed with exit code $LASTEXITCODE" }
$raw = Get-Content -Raw $evidencePath | ConvertFrom-Json
Write-Output (ConvertTo-Json @{ status = 'pass'; evidence_id = $raw.data.evidence_id; artifact_sha256 = $raw.data.subject.digest.sha256; wabt_bin = $bootstrapResult.bin; evidence_path = $evidencePath } -Compress)
