param(
    [string]$NodePath = $env:REVERSE_FUSION_NODE,
    [string]$DotnetPath = $env:REVERSE_FUSION_DOTNET
)

$ErrorActionPreference = 'Stop'
$priorDotnet = $env:REVERSE_FUSION_DOTNET
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
. (Join-Path $PSScriptRoot 'lib/ScriptSupport.ps1')
Push-Location $repo
try {
$state = Join-Path $repo 'state'
if (-not $NodePath) { $NodePath = 'node' }
if (-not $DotnetPath) { $DotnetPath = 'dotnet' }
$env:REVERSE_FUSION_DOTNET = $DotnetPath
$rea = Join-Path $repo 'vendor\rea\package\scripts\rea.mjs'
$originalDll = Join-Path $repo 'fixtures\dotnet-original\bin\Release\net8.0\ReverseFixture.dll'
$candidateRoot = Join-Path $state 'dotnet-candidate'
$candidateDll = Join-Path $candidateRoot 'bin\Release\net8.0\ReverseFixture.dll'
if (-not (Test-Path -LiteralPath (Join-Path $candidateRoot 'ReverseFixture.csproj'))) { throw 'Candidate source is missing; run the host Builder first.' }
New-Item -ItemType Directory -Path $state -Force | Out-Null
& $DotnetPath build (Join-Path $repo 'fixtures\dotnet-original\ReverseFixture.csproj') --configuration Release --nologo | Out-Host
Assert-NativeExit $LASTEXITCODE 'run-dotnet-vertical.ps1 native step'
& $DotnetPath build (Join-Path $candidateRoot 'ReverseFixture.csproj') --configuration Release --nologo | Out-Host
Assert-NativeExit $LASTEXITCODE 'run-dotnet-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-dotnet-original.json')
& $NodePath $rea inspect-managed-artifact $originalDll --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-dotnet-original.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-dotnet-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-dotnet-original-members.json')
& $NodePath $rea inspect-managed-members $originalDll --type Program --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-dotnet-original-members.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-dotnet-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-dotnet-candidate.json')
& $NodePath $rea inspect-managed-artifact $candidateDll --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-dotnet-candidate.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-dotnet-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-dotnet-candidate-members.json')
& $NodePath $rea inspect-managed-members $candidateDll --type Program --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-dotnet-candidate-members.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-dotnet-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-dotnet-comparison.json')
& $NodePath (Join-Path $repo 'scripts/compare-managed-evidence.mjs') (Join-Path $state 'rea-dotnet-original-members.json') (Join-Path $state 'rea-dotnet-candidate-members.json') (Join-Path $state 'rea-dotnet-comparison.json') | Out-Host
Assert-NativeExit $LASTEXITCODE 'run-dotnet-vertical.ps1 native step'
& $NodePath (Join-Path $repo 'scripts\run-dotnet-proof.mjs') state/rea-dotnet-original.json state/rea-dotnet-candidate.json state/rea-dotnet-original-members.json state/rea-dotnet-candidate-members.json state/rea-dotnet-comparison.json state | Out-Host
Assert-NativeExit $LASTEXITCODE 'run-dotnet-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-dotnet-ledger.json')
& $NodePath $rea build-reconstruction-obligation-ledger (Join-Path $state 'dotnet-ledger-input.json') --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-dotnet-ledger.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-dotnet-vertical.ps1 native step'
$ledger = Get-Content -Raw (Join-Path $state 'rea-dotnet-ledger.json') | ConvertFrom-Json
if (-not $ledger.ok -or $ledger.data.normalized_result.status -ne 'ready' -or $ledger.data.normalized_result.summary.required_open -ne 0) { throw 'Bounded obligation ledger did not close' }
Write-Output (Get-Content -Raw (Join-Path $state 'dotnet-acceptance.json'))
} finally { $env:REVERSE_FUSION_DOTNET = $priorDotnet; Pop-Location }
