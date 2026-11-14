$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'run-rea-wasm.ps1') -Fixture (Join-Path $PSScriptRoot '..\fixtures\answer.wasm') -EvidenceOut (Join-Path $PSScriptRoot '..\state\rea-wasm-evidence.json') | Out-Host
& (Join-Path $PSScriptRoot 'run-rea-wasm.ps1') -Fixture (Join-Path $PSScriptRoot '..\fixtures\answer-candidate.wasm') -EvidenceOut (Join-Path $PSScriptRoot '..\state\rea-wasm-candidate-evidence.json') | Out-Host
& (Join-Path $PSScriptRoot 'run-rea-wasm.ps1') -Fixture (Join-Path $PSScriptRoot '..\fixtures\answer-wrong.wasm') -EvidenceOut (Join-Path $PSScriptRoot '..\state\rea-wasm-wrong-evidence.json') | Out-Host
python -m reverse_fusion accept --fixture wasm --candidate correct --record --format json
python -m reverse_fusion accept --fixture wasm --candidate wrong --format json
python -m reverse_fusion accept --fixture wasm --candidate missing --format json
