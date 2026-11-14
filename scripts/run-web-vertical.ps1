param([string]$NodePath = $env:REVERSE_FUSION_NODE)

$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$state = Join-Path $repo 'state'
if (-not $NodePath) { $NodePath = 'node' }
$rea = Join-Path $repo 'vendor\rea\package\scripts\rea.mjs'
New-Item -ItemType Directory -Path $state -Force | Out-Null
& $NodePath $rea analyze-javascript-application (Join-Path $repo 'fixtures\web-original') --format json --full-output | Out-File (Join-Path $state 'rea-web-original.json') -Encoding utf8
& $NodePath $rea analyze-javascript-application (Join-Path $state 'web-candidate') --format json --full-output | Out-File (Join-Path $state 'rea-web-candidate.json') -Encoding utf8
$original = Get-Content -Raw (Join-Path $state 'rea-web-original.json') | ConvertFrom-Json
$candidate = Get-Content -Raw (Join-Path $state 'rea-web-candidate.json') | ConvertFrom-Json
 $compareJson = @{ left = $original.data; right = $candidate.data; left_module_path = 'app.js'; left_export_name = 'answer'; right_module_path = 'app.js'; right_export_name = 'answer' } | ConvertTo-Json -Depth 100
[IO.File]::WriteAllText((Join-Path $state 'web-compare-input.json'), $compareJson, [Text.UTF8Encoding]::new($false))
& $NodePath $rea compare-javascript-export-shapes (Join-Path $state 'web-compare-input.json') --format json --full-output | Out-File (Join-Path $state 'rea-web-comparison.json') -Encoding utf8
& $NodePath (Join-Path $repo 'scripts\run-web-proof.mjs') state/rea-web-original.json state/rea-web-candidate.json state/rea-web-comparison.json fixtures/web-original/app.js state/web-candidate/app.js state | Out-Host
& $NodePath $rea build-reconstruction-obligation-ledger (Join-Path $state 'web-ledger-input.json') --format json --full-output | Out-File (Join-Path $state 'rea-web-ledger.json') -Encoding utf8
Write-Output (Get-Content -Raw (Join-Path $state 'web-acceptance.json'))
