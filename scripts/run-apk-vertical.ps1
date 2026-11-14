param(
    [string]$NodePath = $env:REVERSE_FUSION_NODE,
    [string]$JavaHome = $env:JAVA_HOME,
    [string]$AndroidSdk = $env:ANDROID_HOME
)

$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$state = Join-Path $repo 'state'
if (-not $NodePath) { $NodePath = 'node' }
if (-not $JavaHome) { throw 'Set JAVA_HOME to a JDK 21+ before running the APK vertical slice.' }
if (-not $AndroidSdk) { throw 'Set ANDROID_HOME to an Android SDK before running the APK vertical slice.' }
$bootstrap = & powershell -NoProfile -File (Join-Path $PSScriptRoot 'bootstrap-jadx.ps1') | ConvertFrom-Json
$env:REA_JADX_MCP_JAR = $bootstrap.jar
$env:JAVA_HOME = $JavaHome
$candidateRoot = Join-Path $state 'apk-candidate'
$build = Join-Path $candidateRoot 'build'
$androidJar = Join-Path $AndroidSdk 'platforms\android-28\android.jar'
$buildTools = Join-Path $AndroidSdk 'build-tools\34.0.0'
if (-not (Test-Path -LiteralPath (Join-Path $candidateRoot 'src\com\reversefusion\Answer.java'))) { throw 'Candidate source is missing; run the host Builder first.' }
function Build-Apk([string]$SourceRoot, [string]$OutputRoot) {
    $classes = Join-Path $OutputRoot 'classes'
    $dex = Join-Path $OutputRoot 'dex'
    New-Item -ItemType Directory -Path $classes,$dex -Force | Out-Null
    & (Join-Path $JavaHome 'bin\javac.exe') -encoding UTF-8 -cp $androidJar -d $classes (Get-ChildItem (Join-Path $SourceRoot 'src') -Recurse -Filter '*.java' | ForEach-Object FullName)
    & (Join-Path $buildTools 'd8.bat') --min-api 28 --output $dex (Get-ChildItem $classes -Recurse -Filter '*.class' | ForEach-Object FullName)
    & (Join-Path $buildTools 'aapt.exe') package -f -M (Join-Path $SourceRoot 'AndroidManifest.xml') -I $androidJar -F (Join-Path $OutputRoot 'unsigned.apk')
    Copy-Item (Join-Path $dex 'classes.dex') (Join-Path $OutputRoot 'classes.dex') -Force
    @'
from pathlib import Path
import shutil, sys, zipfile
build = Path(sys.argv[1])
with zipfile.ZipFile(build / 'unsigned.apk', 'a') as archive:
    archive.write(build / 'classes.dex', 'classes.dex', compress_type=zipfile.ZIP_STORED)
shutil.copyfile(build / 'unsigned.apk', build / 'fixture.apk')
'@ | python - (Join-Path $OutputRoot '')
}
$originalRoot = Join-Path $repo 'fixtures\apk-original'
Build-Apk $originalRoot (Join-Path $originalRoot 'build')
Build-Apk $candidateRoot $build
$node = $NodePath
$rea = Join-Path $repo 'vendor\rea\package\scripts\rea.mjs'
& $node $rea inspect-android-package (Join-Path $repo 'fixtures\apk-original\build\fixture.apk') --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-apk-original.json') -Encoding utf8
& $node $rea inspect-android-class (Join-Path $repo 'fixtures\apk-original\build\fixture.apk') com.reversefusion.Answer --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-apk-original-class.json') -Encoding utf8
& $node $rea inspect-android-package (Join-Path $build 'fixture.apk') --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-apk-candidate.json') -Encoding utf8
& $node $rea inspect-android-class (Join-Path $build 'fixture.apk') com.reversefusion.Answer --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-apk-candidate-class.json') -Encoding utf8
& $node (Join-Path $repo 'scripts\run-apk-proof.mjs') state/rea-apk-original.json state/rea-apk-original-class.json state/rea-apk-candidate.json state/rea-apk-candidate-class.json state | Out-Host
& $node $rea build-reconstruction-obligation-ledger (Join-Path $state 'apk-ledger-input.json') --format json --full-output | Out-File -LiteralPath (Join-Path $state 'rea-apk-ledger.json') -Encoding utf8
Write-Output (Get-Content -Raw (Join-Path $state 'apk-acceptance.json'))
