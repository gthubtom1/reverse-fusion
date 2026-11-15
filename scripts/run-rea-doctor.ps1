param(
    [string]$Output = (Join-Path $PSScriptRoot '..\state\rea-mcp-doctor.json'),
    [string]$NodePath = $env:REVERSE_FUSION_NODE,
    [string]$ReaScript = $env:REVERSE_FUSION_REA_SCRIPT
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
$NodePath = Resolve-ReaNodePath $repo $NodePath
$reaBootstrap = Join-Path $PSScriptRoot 'bootstrap-rea.ps1'
$rea = & powershell -NoProfile -File $reaBootstrap -NodePath $NodePath | ConvertFrom-Json
Assert-NativeExit $LASTEXITCODE 'REA bootstrap'
$NodePath = $rea.node
if (-not $ReaScript) { $ReaScript = $rea.script }
$outputPath = Assert-RepositoryWritePath $repo $Output
New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($outputPath)) -Force | Out-Null
$started = Reset-OutputFile $repo $outputPath
& $NodePath $ReaScript mcp doctor --format json | Out-File -LiteralPath $outputPath -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'REA MCP doctor'
$result = Read-FreshJson $repo $outputPath $started
if (-not $result.healthy) { throw 'REA MCP doctor returned healthy=false' }
Write-Output (ConvertTo-Json @{ status = 'pass'; output = $outputPath; rea = $result.server.version; tools = $result.inventory.tools.observed; prompts = $result.inventory.prompts.observed; catalog_digest = $result.identity.observed_catalog_digest } -Compress)
