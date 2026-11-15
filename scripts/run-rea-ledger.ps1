param(
    [string]$Output = (Join-Path $PSScriptRoot '..\state\ledger-output.json'),
    [string]$NodePath = $env:REVERSE_FUSION_NODE
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
$bootstrap = Join-Path $PSScriptRoot 'bootstrap-rea.ps1'
$rea = & powershell -NoProfile -File $bootstrap -NodePath $NodePath | ConvertFrom-Json
if (-not $NodePath) { $NodePath = $rea.node }
$outputPath = Assert-RepositoryWritePath $repo $Output
New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($outputPath)) -Force | Out-Null
$proofPath = Join-Path $repo 'state\rea-wasm-proof-evidence.json'
$comparisonPath = Join-Path $repo 'state\rea-wasm-comparison-evidence.json'
$bundlePath = Join-Path $repo 'state\rea-bundle.json'
$inputPath = Join-Path $repo 'state\ledger-input.json'
foreach ($path in @($proofPath,$comparisonPath,$bundlePath,$inputPath,$outputPath)) { [void](Reset-OutputFile $repo $path) }
$started = [DateTime]::UtcNow
$reaScript = [string]$rea.script

Push-Location $repo
try {
    & $NodePath (Join-Path $repo 'scripts\run-rea-ledger.mjs') | Out-Host
    Assert-NativeExit $LASTEXITCODE 'REA ledger evidence preparation'
    foreach ($path in @($proofPath,$comparisonPath,$bundlePath,$inputPath)) { [void](Read-FreshJson $repo $path $started) }
    & $NodePath $reaScript build-reconstruction-obligation-ledger $inputPath --format json --full-output | Out-File -LiteralPath $outputPath -Encoding utf8
    Assert-NativeExit $LASTEXITCODE 'REA obligation ledger'
}
finally {
    Pop-Location
}

$record = Read-FreshJson $repo $outputPath $started
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
    proof_evidence_id = (Get-Content -Raw $proofPath | ConvertFrom-Json).data.evidence_id
} -Compress)
