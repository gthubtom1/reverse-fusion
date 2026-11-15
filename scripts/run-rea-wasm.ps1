param(
    [string]$Fixture = (Join-Path $PSScriptRoot '..\fixtures\answer.wasm'),
    [string]$EvidenceOut = (Join-Path $PSScriptRoot '..\state\rea-wasm-evidence.json'),
    [string]$NodePath = $env:REVERSE_FUSION_NODE,
    [string]$ReaScript = $env:REVERSE_FUSION_REA_SCRIPT
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
$fixturePath = [IO.Path]::GetFullPath($Fixture)
$evidencePath = Assert-RepositoryWritePath $repo $EvidenceOut
if (-not (Test-Path -LiteralPath $fixturePath)) { throw "Fixture not found: $fixturePath" }

$reaBootstrap = Join-Path $PSScriptRoot 'bootstrap-rea.ps1'
$rea = & powershell -NoProfile -File $reaBootstrap -NodePath $NodePath | ConvertFrom-Json
if (-not $NodePath) { $NodePath = $rea.node }
if (-not $ReaScript) { $ReaScript = $rea.script }
$bootstrap = Join-Path $PSScriptRoot 'bootstrap-wabt.ps1'
$bootstrapResult = & powershell -NoProfile -File $bootstrap | ConvertFrom-Json
$env:REA_WABT_BIN_DIRECTORY = $bootstrapResult.bin
New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($evidencePath)) -Force | Out-Null
$started = Reset-OutputFile $repo $evidencePath
Push-Location $repo
try {
    & $NodePath $ReaScript inspect-wasm-artifact $fixturePath --format json --full-output | Out-File -LiteralPath $evidencePath -Encoding utf8
    Assert-NativeExit $LASTEXITCODE 'REA inspect-wasm-artifact'
} finally { Pop-Location }
$raw = Read-FreshJson $repo $evidencePath $started
if (-not $raw.ok -or -not $raw.data.evidence_id) { throw 'REA WASM output lacks a successful Evidence record' }
Write-Output (ConvertTo-Json @{ status = 'pass'; evidence_id = $raw.data.evidence_id; artifact_sha256 = $raw.data.subject.digest.sha256; wabt_bin = $bootstrapResult.bin; evidence_path = $evidencePath } -Compress)
