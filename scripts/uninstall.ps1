param(
    [switch]$Apply,
    [string]$VenvPath = (Join-Path $PSScriptRoot '..\.venv')
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
$venv = Assert-RepositoryWritePath $repo $VenvPath
$receipt = Assert-RepositoryWritePath $repo (Join-Path $repo 'state\install.json')
if ($Apply -and (Test-Path -LiteralPath (Join-Path $venv 'Scripts\python.exe') -PathType Leaf)) {
    & (Join-Path $venv 'Scripts\python.exe') -m reverse_fusion uninstall --apply --format json | Out-Null
    Assert-NativeExit $LASTEXITCODE 'global adapter removal'
}
if ($Apply -and (Test-Path -LiteralPath $venv)) { Remove-Item -LiteralPath $venv -Recurse -Force }
if ($Apply -and (Test-Path -LiteralPath $receipt -PathType Leaf)) { Remove-Item -LiteralPath $receipt -Force }
Write-Output (ConvertTo-Json @{ status = if ($Apply) { 'uninstalled' } else { 'dry-run' }; venv=$venv; global_adapter='removed-by-reverse-fusion-cli-when-recorded' } -Compress)
