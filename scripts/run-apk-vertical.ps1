param(
    [string]$NodePath = $env:REVERSE_FUSION_NODE,
    [string]$JavaHome = $env:JAVA_HOME,
    [string]$AndroidSdk = $env:ANDROID_HOME,
    [string]$PythonPath = $env:REVERSE_FUSION_PYTHON
)

$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
. (Join-Path $PSScriptRoot 'lib/ScriptSupport.ps1')
Push-Location $repo
try {
$state = Join-Path $repo 'state'
$NodePath = Resolve-ReaNodePath $repo $NodePath
if (-not $PythonPath) { $PythonPath = 'python' }
if (-not $JavaHome) { throw 'Set JAVA_HOME to a JDK 21+ before running the APK vertical slice.' }
if (-not $AndroidSdk) { throw 'Set ANDROID_HOME to an Android SDK before running the APK vertical slice.' }
$bootstrap = & (Join-Path $PSScriptRoot 'bootstrap-jadx.ps1')
$bootstrap = $bootstrap | ConvertFrom-Json
$env:REA_JADX_MCP_JAR = $bootstrap.jar
$env:JAVA_HOME = $JavaHome
$candidateRoot = Join-Path $state 'apk-candidate'
$build = Join-Path $candidateRoot 'build'
$androidJar = Join-Path $AndroidSdk 'platforms\android-28\android.jar'
$buildTools = Join-Path $AndroidSdk 'build-tools\34.0.0'
if (-not (Test-Path -LiteralPath (Join-Path $candidateRoot 'src\com\reversefusion\Answer.java'))) { throw 'Candidate source is missing; run the host Builder first.' }
function Build-Apk([string]$SourceRoot, [string]$OutputRoot) {
    $safeOutput = Assert-RepositoryWritePath $repo $OutputRoot
    if (Test-Path -LiteralPath $safeOutput) { Remove-Item -LiteralPath $safeOutput -Recurse -Force }
    $classes = Join-Path $safeOutput 'classes'
    $dex = Join-Path $OutputRoot 'dex'
    New-Item -ItemType Directory -Path $classes,$dex -Force | Out-Null
    & (Join-Path $JavaHome 'bin\javac.exe') --release 8 -encoding UTF-8 -cp $androidJar -d $classes (Get-ChildItem (Join-Path $SourceRoot 'src') -Recurse -Filter '*.java' | ForEach-Object FullName)
Assert-NativeExit $LASTEXITCODE 'run-apk-vertical.ps1 native step'
    & (Join-Path $buildTools 'd8.bat') --min-api 28 --output $dex (Get-ChildItem $classes -Recurse -Filter '*.class' | ForEach-Object FullName)
Assert-NativeExit $LASTEXITCODE 'run-apk-vertical.ps1 native step'
    & (Join-Path $buildTools 'aapt.exe') package -f -M (Join-Path $SourceRoot 'AndroidManifest.xml') -I $androidJar -F (Join-Path $OutputRoot 'unsigned.apk')
Assert-NativeExit $LASTEXITCODE 'run-apk-vertical.ps1 native step'
    Copy-Item (Join-Path $dex 'classes.dex') (Join-Path $OutputRoot 'classes.dex') -Force
    @'
from pathlib import Path
import shutil, sys, zipfile
build = Path(sys.argv[1])
with zipfile.ZipFile(build / 'unsigned.apk', 'a') as archive:
    archive.write(build / 'classes.dex', 'classes.dex', compress_type=zipfile.ZIP_STORED)
shutil.copyfile(build / 'unsigned.apk', build / 'fixture.apk')
'@ | & $PythonPath - (Join-Path $OutputRoot '')
Assert-NativeExit $LASTEXITCODE 'run-apk-vertical.ps1 native step'
}
$originalRoot = Join-Path $repo 'fixtures\apk-original'
Build-Apk $originalRoot (Join-Path $originalRoot 'build')
Build-Apk $candidateRoot $build
$node = $NodePath
$rea = Join-Path $repo 'vendor\rea\package\scripts\rea.mjs'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-apk-original.json')
& $node $rea inspect-android-package (Join-Path $repo 'fixtures\apk-original\build\fixture.apk') --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-apk-original.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-apk-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-apk-original-class.json')
& $node $rea inspect-android-class (Join-Path $repo 'fixtures\apk-original\build\fixture.apk') com.reversefusion.Answer --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-apk-original-class.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-apk-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-apk-candidate.json')
& $node $rea inspect-android-package (Join-Path $build 'fixture.apk') --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-apk-candidate.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-apk-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-apk-candidate-class.json')
& $node $rea inspect-android-class (Join-Path $build 'fixture.apk') com.reversefusion.Answer --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-apk-candidate-class.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-apk-vertical.ps1 native step'
& $node (Join-Path $repo 'scripts\run-apk-proof.mjs') state/rea-apk-original.json state/rea-apk-original-class.json state/rea-apk-candidate.json state/rea-apk-candidate-class.json state | Out-Host
Assert-NativeExit $LASTEXITCODE 'run-apk-vertical.ps1 native step'
$null = Reset-OutputFile $repo (Join-Path $state 'rea-apk-ledger.json')
& $node $rea build-reconstruction-obligation-ledger (Join-Path $state 'apk-ledger-input.json') --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-apk-ledger.json') -Encoding utf8
Assert-NativeExit $LASTEXITCODE 'run-apk-vertical.ps1 native step'
$ledger = Get-Content -Raw (Join-Path $state 'rea-apk-ledger.json') | ConvertFrom-Json
if (-not $ledger.ok -or $ledger.data.normalized_result.status -ne 'ready' -or $ledger.data.normalized_result.summary.required_open -ne 0) { throw 'Bounded obligation ledger did not close' }
Write-Output (Get-Content -Raw (Join-Path $state 'apk-acceptance.json'))
} finally { Pop-Location }
