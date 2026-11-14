param(
    [string]$PythonPath = $env:REVERSE_FUSION_PYTHON
)
$ErrorActionPreference = 'Stop'
if (-not $PythonPath) { $PythonPath = 'python' }
& (Join-Path $PSScriptRoot 'run-rea-wasm.ps1') -Fixture (Join-Path $PSScriptRoot '..\fixtures\answer.wasm') -EvidenceOut (Join-Path $PSScriptRoot '..\state\rea-wasm-evidence.json') | Out-Host
& (Join-Path $PSScriptRoot 'run-rea-wasm.ps1') -Fixture (Join-Path $PSScriptRoot '..\fixtures\answer-candidate.wasm') -EvidenceOut (Join-Path $PSScriptRoot '..\state\rea-wasm-candidate-evidence.json') | Out-Host
& (Join-Path $PSScriptRoot 'run-rea-wasm.ps1') -Fixture (Join-Path $PSScriptRoot '..\fixtures\answer-wrong.wasm') -EvidenceOut (Join-Path $PSScriptRoot '..\state\rea-wasm-wrong-evidence.json') | Out-Host
& $PythonPath -m reverse_fusion accept --fixture wasm --candidate correct --record --format json
& $PythonPath -m reverse_fusion accept --fixture wasm --candidate wrong --format json
& $PythonPath -m reverse_fusion accept --fixture wasm --candidate missing --format json
