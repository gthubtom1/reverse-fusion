"""Windows wrapper transport, using a clearly synthetic provider, never REA proof."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == 'nt' and shutil.which('powershell'), 'Windows PowerShell wrapper')
class ProviderWrapperTests(unittest.TestCase):
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
