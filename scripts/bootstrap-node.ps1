param()
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib/ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
if ($env:OS -ne 'Windows_NT' -or [Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'X64') { throw 'Pinned local Node package currently targets Windows x64' }
$manifest = Get-Content -Raw -LiteralPath (Join-Path $repo 'vendor/node/manifest.json') | ConvertFrom-Json
$destination = Assert-RepositoryWritePath $repo (Join-Path $repo 'vendor/node')
$archive = Assert-RepositoryWritePath $repo (Join-Path $destination 'node-windows-x64.zip')
$entry = Assert-RepositoryWritePath $repo (Join-Path $destination $manifest.entry)
if (-not (Test-Path -LiteralPath $entry)) {
    if (-not (Test-Path -LiteralPath $archive) -or (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.sha256) {
        Invoke-WebRequest -Uri $manifest.url -OutFile $archive -UseBasicParsing
    }
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.sha256) { throw 'Node archive digest mismatch' }
    Expand-Archive -LiteralPath $archive -DestinationPath $destination -Force
}
$version = (& $entry --version | Out-String).Trim()
Assert-NativeExit $LASTEXITCODE 'Local Node version'
if ($version -ne ('v' + $manifest.version)) { throw 'Local Node version mismatch' }
@{status='installed';node=$entry;version=$version;scope='repository-local'} | ConvertTo-Json -Compress
