param([string]$NodePath = $env:REVERSE_FUSION_NODE)

$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
. (Join-Path $PSScriptRoot 'lib/ScriptSupport.ps1')
Push-Location $repo
try {
$state = Join-Path $repo 'state'
$NodePath = Resolve-ReaNodePath $repo $NodePath
$rea = Join-Path $repo 'vendor\rea\package\scripts\rea.mjs'
New-Item -ItemType Directory -Path $state -Force | Out-Null
$null = Reset-OutputFile $repo (Join-Path $state 'rea-web-original.json')
& $NodePath $rea analyze-javascript-application (Join-Path $repo 'fixtures\web-original') --format json --full-output | Out-File (Join-Path $state 'rea-web-original.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-web-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-web-candidate.json')
& $NodePath $rea analyze-javascript-application (Join-Path $state 'web-candidate') --format json --full-output | Out-File (Join-Path $state 'rea-web-candidate.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-web-vertical.ps1 native step'
$original = Get-Content -Raw (Join-Path $state 'rea-web-original.json') | ConvertFrom-Json
$candidate = Get-Content -Raw (Join-Path $state 'rea-web-candidate.json') | ConvertFrom-Json
 $compareJson = @{ left = $original.data; right = $candidate.data; left_module_path = 'app.js'; left_export_name = 'answer'; right_module_path = 'app.js'; right_export_name = 'answer' } | ConvertTo-Json -Depth 100
[IO.File]::WriteAllText((Join-Path $state 'web-compare-input.json'), $compareJson, [Text.UTF8Encoding]::new($false))
$null = Reset-OutputFile $repo (Join-Path $state 'rea-web-comparison.json')
& $NodePath $rea compare-javascript-export-shapes (Join-Path $state 'web-compare-input.json') --format json --full-output | Out-File (Join-Path $state 'rea-web-comparison.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-web-vertical.ps1 native step'
& $NodePath (Join-Path $repo 'scripts\run-web-proof.mjs') state/rea-web-original.json state/rea-web-candidate.json state/rea-web-comparison.json fixtures/web-original/app.js state/web-candidate/app.js state | Out-Host
Assert-NativeExit $LASTEXITCODE 'run-web-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-web-ledger.json')
& $NodePath $rea build-reconstruction-obligation-ledger (Join-Path $state 'web-ledger-input.json') --format json --full-output | Out-File (Join-Path $state 'rea-web-ledger.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-web-vertical.ps1 native step'
$ledger = Get-Content -Raw (Join-Path $state 'rea-web-ledger.json') | ConvertFrom-Json
if (-not $ledger.ok -or $ledger.data.normalized_result.status -ne 'ready' -or $ledger.data.normalized_result.summary.required_open -ne 0) { throw 'Bounded obligation ledger did not close' }
$null = Reset-OutputFile $repo (Join-Path $state 'rea-web-full-ledger.json')
& $NodePath $rea build-reconstruction-obligation-ledger (Join-Path $state 'web-full-ledger-input.json') --format json --full-output | Out-File (Join-Path $state 'rea-web-full-ledger.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'Web full graph obligation ledger'
$fullLedger = Get-Content -Raw (Join-Path $state 'rea-web-full-ledger.json') | ConvertFrom-Json
if (-not $fullLedger.ok) { throw 'Full graph obligation ledger was not produced' }
Write-Output (Get-Content -Raw (Join-Path $state 'web-acceptance.json'))
} finally { Pop-Location }
