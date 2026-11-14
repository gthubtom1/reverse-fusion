param(
    [string]$Output = (Join-Path $PSScriptRoot '..\state\ledger-output.json'),
    [string]$NodePath = $env:REVERSE_FUSION_NODE
)

$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$bootstrap = Join-Path $PSScriptRoot 'bootstrap-rea.ps1'
$rea = & powershell -NoProfile -File $bootstrap -NodePath $NodePath | ConvertFrom-Json
if (-not $NodePath) { $NodePath = $rea.node }
$outputPath = [IO.Path]::GetFullPath($Output)
New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($outputPath)) -Force | Out-Null

Push-Location $repo
try {
    & $NodePath (Join-Path $repo 'scripts\run-rea-ledger.mjs') | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "REA ledger evidence preparation failed with exit code $LASTEXITCODE" }
    & $NodePath (Join-Path $repo 'vendor\rea\package\scripts\rea.mjs') build-reconstruction-obligation-ledger (Join-Path $repo 'state\ledger-input.json') --format json --full-output | Out-File -LiteralPath $outputPath -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw "REA obligation ledger failed with exit code $LASTEXITCODE" }
}
finally {
    Pop-Location
}

$record = Get-Content -Raw $outputPath | ConvertFrom-Json
$ledger = $record.data.normalized_result
if ($ledger.status -ne 'ready' -or $ledger.summary.required_open -ne 0) {
    throw "REA obligation ledger is not ready: status=$($ledger.status), required_open=$($ledger.summary.required_open)"
}
Write-Output (ConvertTo-Json @{
    status = 'pass'
    output = $outputPath
    ledger_id = $ledger.ledger_id
    closure_digest = $ledger.closure_digest
    required_open = $ledger.summary.required_open
    proof_evidence_id = (Get-Content -Raw (Join-Path $repo 'state\rea-wasm-proof-evidence.json') | ConvertFrom-Json).data.evidence_id
} -Compress)
