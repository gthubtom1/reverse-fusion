param(
    [string]$PythonPath = $env:REVERSE_FUSION_PYTHON
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
if (-not $PythonPath) { $PythonPath = Join-Path $repo '.venv/Scripts/python.exe' }
$acceptancePath = Join-Path $repo 'state\wasm-acceptance.json'
[void](Reset-OutputFile $repo $acceptancePath)
Push-Location $repo
try {
    & (Join-Path $PSScriptRoot 'run-rea-wasm.ps1') -Fixture (Join-Path $repo 'fixtures\answer.wasm') -EvidenceOut (Join-Path $repo 'state\rea-wasm-evidence.json') | Out-Host
    & (Join-Path $PSScriptRoot 'run-rea-wasm.ps1') -Fixture (Join-Path $repo 'fixtures\answer-candidate.wasm') -EvidenceOut (Join-Path $repo 'state\rea-wasm-candidate-evidence.json') | Out-Host
    & (Join-Path $PSScriptRoot 'run-rea-wasm.ps1') -Fixture (Join-Path $repo 'fixtures\answer-wrong.wasm') -EvidenceOut (Join-Path $repo 'state\rea-wasm-wrong-evidence.json') | Out-Host

    $correctText = (& $PythonPath -m reverse_fusion accept --fixture wasm --candidate correct --record --format json 2>&1 | Out-String)
    $correctExit = $LASTEXITCODE
    Assert-NativeExit $correctExit 'correct WASM acceptance' @(0)
    $correct = $correctText | ConvertFrom-Json
    Assert-ResultStatus $correct @('pass') 'correct WASM acceptance'

    $wrongText = (& $PythonPath -m reverse_fusion accept --fixture wasm --candidate wrong --format json 2>&1 | Out-String)
    $wrongExit = $LASTEXITCODE
    Assert-NativeExit $wrongExit 'wrong WASM acceptance' @(1)
    $wrong = $wrongText | ConvertFrom-Json
    Assert-ResultStatus $wrong @('fail') 'wrong WASM acceptance'

    $missingText = (& $PythonPath -m reverse_fusion accept --fixture wasm --candidate missing --format json 2>&1 | Out-String)
    $missingExit = $LASTEXITCODE
    Assert-NativeExit $missingExit 'missing WASM acceptance' @(2)
    $missing = $missingText | ConvertFrom-Json
    Assert-ResultStatus $missing @('unknown') 'missing WASM acceptance'
} finally { Pop-Location }
Write-Output (ConvertTo-Json @{ status='pass'; correct_exit=$correctExit; wrong_exit=$wrongExit; missing_exit=$missingExit; correct=$correct.status; wrong=$wrong.status; missing=$missing.status } -Compress)
