param([string]$PythonPath = (Join-Path $PSScriptRoot '..\.venv\Scripts\python.exe'))
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lib/ScriptSupport.ps1')
$repo = Get-CanonicalPath (Join-Path $PSScriptRoot '..')
$manifest = Get-Content -Raw -LiteralPath (Join-Path $repo 'vendor/spec-kit/manifest.json') | ConvertFrom-Json
$source = Assert-RepositoryWritePath $repo (Join-Path $repo 'vendor/spec-kit/upstream')
if (-not (Test-Path -LiteralPath (Join-Path $source '.git'))) {
    if ((Test-Path -LiteralPath $source) -and (Get-ChildItem -LiteralPath $source -Force | Select-Object -First 1)) { throw 'Spec source destination is not an empty checkout' }
    & git clone --filter=blob:none --no-checkout $manifest.repository $source
    Assert-NativeExit $LASTEXITCODE 'Spec source clone'
    & git -C $source checkout --detach $manifest.commit
    Assert-NativeExit $LASTEXITCODE 'Spec pinned checkout'
}
$head = (& git -C $source rev-parse HEAD | Out-String).Trim()
Assert-NativeExit $LASTEXITCODE 'Spec source identity'
$changes = & git -C $source status --porcelain
Assert-NativeExit $LASTEXITCODE 'Spec source status'
if ($head -ne $manifest.commit -or $changes) { throw 'Spec source does not match the clean pinned revision' }
$lock = Join-Path $repo $manifest.dependency_lock
& $PythonPath -m pip install --quiet -r $lock
Assert-NativeExit $LASTEXITCODE 'Spec locked dependencies'
& $PythonPath -m pip install --quiet --no-deps $source
Assert-NativeExit $LASTEXITCODE 'Spec package install'
$version = (& $PythonPath -c "from importlib.metadata import version; print(version('specify-cli'))" | Out-String).Trim()
Assert-NativeExit $LASTEXITCODE 'Spec installed version'
if ($version -ne $manifest.version) { throw 'Spec installed version differs from source pin' }
$receipt = Assert-RepositoryWritePath $repo (Join-Path $repo 'state/spec-runtime.json')
New-Item -ItemType Directory -Path (Split-Path -Parent $receipt) -Force | Out-Null
$result = @{schema_version=1;repository_root=$repo;version=$version;source_commit=$head;python=$PythonPath;dependency_lock_sha256=(Get-FileHash -LiteralPath $lock -Algorithm SHA256).Hash.ToLowerInvariant();status='installed';workflow_acceptance='not-performed'}
$result | ConvertTo-Json | Set-Content -LiteralPath $receipt -Encoding utf8
$result | ConvertTo-Json -Compress
