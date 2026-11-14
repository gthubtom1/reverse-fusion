param(
    [switch]$Apply,
    [string]$VenvPath = (Join-Path $PSScriptRoot '..\.venv')
)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$venv = [IO.Path]::GetFullPath($VenvPath)
if (-not $venv.StartsWith($repo + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'VenvPath must stay inside the repository' }
if ($Apply -and (Test-Path -LiteralPath $venv)) { Remove-Item -LiteralPath $venv -Recurse -Force }
Write-Output (ConvertTo-Json @{ status = if ($Apply) { 'uninstalled' } else { 'dry-run' }; venv=$venv; global_config_mutation=$false } -Compress)
