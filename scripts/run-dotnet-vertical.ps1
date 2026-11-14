param(
    [string]$NodePath = $env:REVERSE_FUSION_NODE,
    [string]$DotnetPath = $env:REVERSE_FUSION_DOTNET
)

$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$state = Join-Path $repo 'state'
if (-not $NodePath) { $NodePath = 'node' }
if (-not $DotnetPath) { $DotnetPath = 'dotnet' }
$rea = Join-Path $repo 'vendor\rea\package\scripts\rea.mjs'
$originalDll = Join-Path $repo 'fixtures\dotnet-original\bin\Release\net8.0\ReverseFixture.dll'
$candidateRoot = Join-Path $state 'dotnet-candidate'
$candidateDll = Join-Path $candidateRoot 'bin\Release\net8.0\ReverseFixture.dll'
if (-not (Test-Path -LiteralPath (Join-Path $candidateRoot 'ReverseFixture.csproj'))) { throw 'Candidate source is missing; run the host Builder first.' }
New-Item -ItemType Directory -Path $state -Force | Out-Null
& $DotnetPath build (Join-Path $repo 'fixtures\dotnet-original\ReverseFixture.csproj') --configuration Release --nologo | Out-Host
& $DotnetPath build (Join-Path $candidateRoot 'ReverseFixture.csproj') --configuration Release --nologo | Out-Host
& $NodePath $rea inspect-managed-artifact $originalDll --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-dotnet-original.json') -Encoding utf8
& $NodePath $rea inspect-managed-members $originalDll --type Program --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-dotnet-original-members.json') -Encoding utf8
& $NodePath $rea inspect-managed-artifact $candidateDll --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-dotnet-candidate.json') -Encoding utf8
& $NodePath $rea inspect-managed-members $candidateDll --type Program --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-dotnet-candidate-members.json') -Encoding utf8
& $NodePath $rea compare-managed-members $originalDll $candidateDll --type Program --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-dotnet-comparison.json') -Encoding utf8
& $NodePath (Join-Path $repo 'scripts\run-dotnet-proof.mjs') state/rea-dotnet-original.json state/rea-dotnet-candidate.json state/rea-dotnet-original-members.json state/rea-dotnet-candidate-members.json state/rea-dotnet-comparison.json state | Out-Host
& $NodePath $rea build-reconstruction-obligation-ledger (Join-Path $state 'dotnet-ledger-input.json') --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-dotnet-ledger.json') -Encoding utf8
Write-Output (Get-Content -Raw (Join-Path $state 'dotnet-acceptance.json'))
