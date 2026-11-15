param(
    [switch]$DryRun,
    [switch]$PackageOnly,
    [string]$NodePath = $env:REVERSE_FUSION_NODE,
    [string]$Python = 'python',
    [string]$VenvPath = (Join-Path $PSScriptRoot '..\.venv')
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
$venv = Assert-RepositoryWritePath $repo $VenvPath
if ($DryRun) { Write-Output (ConvertTo-Json @{ mode='dry-run'; package_only=[bool]$PackageOnly; required_components=@('REA','Spec Kit','Craft native'); commands=@("$Python -m venv $venv", "$venv\Scripts\python.exe -m pip install --no-deps -e $repo", 'scripts/bootstrap-core.ps1') } -Compress); exit 0 }
& $Python -m venv $venv
Assert-NativeExit $LASTEXITCODE 'venv creation'
& (Join-Path $venv 'Scripts\python.exe') -m pip install --no-deps -e $repo
Assert-NativeExit $LASTEXITCODE 'editable install'
if (-not $PackageOnly) {
    if ($venv -ne (Join-Path $repo '.venv')) { throw 'Core deployment requires the canonical repository .venv' }
    if ($NodePath) { & powershell -NoProfile -File (Join-Path $PSScriptRoot 'bootstrap-core.ps1') -NodePath $NodePath }
    else { & powershell -NoProfile -File (Join-Path $PSScriptRoot 'bootstrap-core.ps1') }
    Assert-NativeExit $LASTEXITCODE 'Required core deployment'
}
Write-Output (ConvertTo-Json @{ status=$(if ($PackageOnly) {'package-only'} else {'core-installed'}); venv=$venv; global_adapter='deferred-to-reverse-fusion-install' } -Compress)
