param(
    [switch]$DryRun,
    [string]$Python = 'python',
    [string]$VenvPath = (Join-Path $PSScriptRoot '..\.venv')
)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$venv = [IO.Path]::GetFullPath($VenvPath)
if (-not $venv.StartsWith($repo + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'VenvPath must stay inside the repository' }
if ($DryRun) { Write-Output (ConvertTo-Json @{ mode='dry-run'; commands=@("$Python -m venv $venv", "$venv\Scripts\python.exe -m pip install --no-deps -e $repo") } -Compress); exit 0 }
& $Python -m venv $venv
if ($LASTEXITCODE -ne 0) { throw "venv creation failed: $LASTEXITCODE" }
& (Join-Path $venv 'Scripts\python.exe') -m pip install --no-deps -e $repo
if ($LASTEXITCODE -ne 0) { throw "editable install failed: $LASTEXITCODE" }
Write-Output (ConvertTo-Json @{ status='installed'; venv=$venv; global_config_mutation=$false } -Compress)
