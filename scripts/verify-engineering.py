"""Run current-host repository checks and bind the result to unchanged sources.

Use the repository venv after core bootstrap. No user sample or target chat is
opened. Existing synthetic native lifecycle tests execute actual Craft tools.
"""
from pathlib import Path
import json
import platform
import re
import subprocess
import sys
from hashlib import sha256

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from reverse_fusion.craft_native import invoke_native
from reverse_fusion.verification import engineering_inputs

before = engineering_inputs(root)
capabilities = invoke_native(root, operation='capabilities')['data']
if 'abort' not in capabilities['capabilities']:
    raise SystemExit('Install the current native component before qualification')
report = {'schema_version': 1, 'scope': 'finite Windows x64/Codex repository checks; no user target',
          'environment': {'platform': platform.system(), 'python': platform.python_version()},
          'native_capabilities': capabilities, 'suites': {}}
release = json.loads((root / 'release/manifest.json').read_text(encoding='utf-8'))
relative_output = release.get('engineering_evidence_directory', 'evidence/rf31')
output = (root / relative_output).resolve()
if not output.is_relative_to(root / 'evidence'):
    raise SystemExit('Engineering logs must stay in the repository evidence directory')
output.mkdir(parents=True, exist_ok=True)
success = True
for name, directory in (('product', 'tests'), ('reconstruction', 'skills/reconstruction/tests')):
    command = [sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover', '-s', directory, '-v']
    run = subprocess.run(command, cwd=root, capture_output=True, timeout=180)
    log = (run.stdout + b'\n' + run.stderr).replace(b'\r\n', b'\n')
    (output / f'{name}-tests.txt').write_bytes(log)
    text = log.decode('utf-8', errors='replace')
    match = re.search(r'Ran (\d+) tests?', text)
    skipped = len(re.findall(r'\.\.\. skipped ', text))
    result = {'returncode': run.returncode, 'tests_run': int(match[1]) if match else 0,
              'skipped': skipped, 'log_sha256': sha256(log).hexdigest(),
              'log_path': f'{relative_output}/{name}-tests.txt'}
    report['suites'][name] = result
    print(json.dumps({name: result}), flush=True)
    success &= run.returncode == 0 and result['tests_run'] > 0 and skipped == 0
report['source_inputs'] = engineering_inputs(root)
success &= report['source_inputs'] == before
report['status'] = 'pass' if success else 'fail'
(root / 'release/verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
raise SystemExit(0 if success else 1)
