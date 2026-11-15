param(
    [switch]$DryRun,
    [string]$Python = 'python',
    [string]$VenvPath = (Join-Path $PSScriptRoot '..\.venv')
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib\ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
$venv = Assert-RepositoryWritePath $repo $VenvPath
if ($DryRun) { Write-Output (ConvertTo-Json @{ mode='dry-run'; commands=@("$Python -m venv $venv", "$venv\Scripts\python.exe -m pip install --no-deps -e $repo") } -Compress); exit 0 }
& $Python -m venv $venv
Assert-NativeExit $LASTEXITCODE 'venv creation'
& (Join-Path $venv 'Scripts\python.exe') -m pip install --no-deps -e $repo
Assert-NativeExit $LASTEXITCODE 'editable install'
Write-Output (ConvertTo-Json @{ status='installed'; venv=$venv; global_config_mutation=$false } -Compress)
