param(
    [ValidateSet('codex', 'pi', 'claude')][string]$Client,
    [string]$PythonPath,
    [ValidateRange(1, 60)][int]$TimeoutSeconds = 45,
    [string]$Output
)

$ErrorActionPreference = 'Stop'
if (-not $Client) { throw 'Pass the selected host explicitly with -Client codex, -Client pi or -Client claude.' }
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
. (Join-Path $PSScriptRoot 'lib/ScriptSupport.ps1')
if (-not $Output) { $Output = Join-Path $repo 'state/host-handshakes.json' }
$Output = Assert-RepositoryWritePath $repo $Output
if (-not $PythonPath) {
    $PythonPath = Join-Path $repo '.venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
        throw 'Create the repository venv first or supply -PythonPath explicitly.'
    }
}
Push-Location $repo
try {
    $result = & $PythonPath -m reverse_fusion handshake --client $Client --timeout $TimeoutSeconds --record --format json
    Assert-NativeExit $LASTEXITCODE 'host handshake observation' @(0, 1, 2)
    $record = Join-Path $repo 'state/host-handshakes.json'
    if ($Output -ne $record) { Copy-Item -LiteralPath $record -Destination $Output -Force }
    $result | Write-Output
} finally { Pop-Location }
