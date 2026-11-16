"""Windows wrapper transport, using a clearly synthetic provider, never REA proof."""
import json
from hashlib import sha256
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == 'nt' and shutil.which('powershell'), 'Windows PowerShell wrapper')
class ProviderWrapperTests(unittest.TestCase):
    def test_ps5_python_inherited_module_path_restores_hash_and_archive_in_nested_shell(self):
        """Exercise original cmdlets, with no profile or module-path cleanup."""
        with tempfile.TemporaryDirectory(prefix='rf inherited modules ') as directory:
            root = Path(directory).resolve()
            support = root/'ScriptSupport.ps1'
            shutil.copyfile(ROOT/'scripts/lib/ScriptSupport.ps1',support)
            payload = root/'payload.txt'
            payload.write_bytes(b'owned archive payload for original PowerShell cmdlets\n')
            archive = root/'owned.zip'
            with zipfile.ZipFile(archive,'w') as stream:
                stream.write(payload,'payload.txt')
            probe = root/'probe.ps1'
            probe.write_text('''param([string]$Support, [string]$Archive, [string]$Payload, [string]$Output, [switch]$Nested)
$ErrorActionPreference = 'Stop'
$before = $env:PSModulePath
. $Support
$after = $env:PSModulePath
. $Support
$repeated = $env:PSModulePath
$hash = (Get-FileHash -LiteralPath $Payload -Algorithm SHA256).Hash.ToLowerInvariant()
Expand-Archive -LiteralPath $Archive -DestinationPath $Output -Force
$restored = [IO.File]::ReadAllText([IO.Path]::Combine($Output, 'payload.txt'))
$child = $null
if (-not $Nested) {
    $child = & ([IO.Path]::Combine($PSHOME, 'powershell.exe')) -NoProfile -File $PSCommandPath -Support $Support -Archive $Archive -Payload $Payload -Output ($Output + '-nested') -Nested
    if ($LASTEXITCODE -ne 0) { throw 'Nested current-engine module recovery failed' }
    $child = $child | ConvertFrom-Json
}
@{major=$PSVersionTable.PSVersion.Major;engine_modules=[IO.Path]::Combine($PSHOME, 'Modules');before=$before;after=$after;repeated=$repeated;hash=$hash;restored=$restored;child=$child} | ConvertTo-Json -Depth 5 -Compress
''',encoding='utf-8')
            empty = root/'empty inherited Modules'
            empty.mkdir()
            pwsh = shutil.which('pwsh')
            ps7_modules = Path(pwsh).resolve().parent/'Modules' if pwsh else root/'PowerShell7-only/Modules'
            if not pwsh:
                ps7_modules.mkdir(parents=True)
            self.assertTrue(ps7_modules.is_dir())
            powershell = Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
            for name,inherited in [('empty-directory',str(empty)),('ps7-only',str(ps7_modules))]:
                with self.subTest(inherited=name):
                    # Windows environment keys are case-insensitive. Avoid a
                    # duplicate PSMODULEPATH/PSModulePath block selecting the
                    # original value instead of the deliberately broken one.
                    environment={key:value for key,value in os.environ.items() if key.casefold()!='psmodulepath'}
                    environment['PSModulePath']=inherited
                    result=subprocess.run([str(powershell),'-NoProfile','-File',str(probe),
                        '-Support',str(support),'-Archive',str(archive),'-Payload',str(payload),
                        '-Output',str(root/name)],env=environment,capture_output=True,timeout=30)
                    self.assertEqual(result.returncode,0,result.stderr.decode(errors='replace'))
                    report=json.loads(result.stdout)
                    self.assertEqual(report['major'],5)
                    self.assertTrue(report['before'].endswith(inherited))
                    self.assertEqual(report['after'],report['engine_modules']+os.pathsep+report['before'])
                    self.assertEqual(report['repeated'],report['after'])
                    self.assertEqual(report['hash'],sha256(payload.read_bytes()).hexdigest())
                    self.assertEqual(report['restored'],payload.read_text(encoding='utf-8'))
                    child=report['child']
                    self.assertEqual(child['major'],5)
                    # Windows PowerShell may itself add a user/system prefix
                    # during child startup. Keep that complete suffix while
                    # bringing this child's own engine modules first again.
                    self.assertTrue(child['before'].endswith(report['after']))
                    self.assertTrue(child['after'].startswith(child['engine_modules']+os.pathsep))
                    self.assertTrue(child['after'].endswith(child['before']))
                    self.assertEqual(child['repeated'],child['after'])
                    self.assertEqual(child['hash'],report['hash'])
                    self.assertEqual(child['restored'],report['restored'])

    def test_default_runtime_reaches_child_and_failed_bootstrap_stops_doctor(self):
        with tempfile.TemporaryDirectory(prefix='rf wrapper ') as directory:
            root = Path(directory).resolve()
            scripts = root / 'scripts'
            (scripts / 'lib').mkdir(parents=True)
            (root / 'state').mkdir()
            for name in ('run-rea-doctor.ps1', 'lib/ScriptSupport.ps1'):
                shutil.copyfile(ROOT / 'scripts' / name, scripts / name)
            # No bootstrap-wabt script exists: a catalog check must not need it.
            (scripts / 'bootstrap-rea.ps1').write_text('''param([Parameter(Mandatory=$true)][string]$NodePath)
if ($NodePath -eq 'fail-node') { exit 7 }
@{node=$NodePath;script=(Join-Path $PSScriptRoot 'synthetic-provider.py')} | ConvertTo-Json -Compress
''', encoding='utf-8')
            (scripts / 'synthetic-provider.py').write_text('''import json, sys
assert sys.argv[1:] == ['mcp', 'doctor', '--format', 'json']
print(json.dumps({'healthy': True, 'server': {'version': 'synthetic'},
 'inventory': {'tools': {'observed': 0}, 'prompts': {'observed': 0}},
 'identity': {'observed_catalog_digest': 'synthetic-only'}}))
''', encoding='utf-8')
            (root / 'state/rea-runtime.json').write_text(json.dumps({
                'schema_version': 1, 'repository_root': str(root), 'node': sys.executable,
            }), encoding='utf-8')
            env = dict(os.environ)
            for name in ('REVERSE_FUSION_NODE', 'REVERSE_FUSION_REA_SCRIPT'):
                env.pop(name, None)
            command = ['powershell', '-NoProfile', '-File', str(scripts / 'run-rea-doctor.ps1')]
            result = subprocess.run(command, env=env, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
            self.assertEqual(json.loads(result.stdout)['rea'], 'synthetic')
            rejected = root / 'state/rejected.json'
            result = subprocess.run(command + ['-NodePath', 'fail-node', '-Output', str(rejected)],
                                    env=env, capture_output=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(rejected.exists())


if __name__ == '__main__':
    unittest.main()
