"""Bind finite engineering regressions to source bytes, without target claims."""
from hashlib import sha256
import json
from pathlib import Path


def engineering_inputs(root: Path) -> dict:
    paths = [root / name for name in ('VERSION', 'pyproject.toml', 'SOURCE-MANIFEST.json', 'release/manifest.json')]
    for directory in ('reverse_fusion', 'tests', 'scripts', 'components'):
        paths += [path for path in (root / directory).rglob('*') if path.is_file()
                  and '__pycache__' not in path.parts]
    return {path.relative_to(root).as_posix(): sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
            for path in sorted(paths)}


def verification_status(root: Path) -> dict:
    try:
        report = json.loads((root / 'release/verification.json').read_text(encoding='utf-8'))
        if (report.get('schema_version') != 1 or report.get('status') != 'pass'
                or report.get('source_inputs') != engineering_inputs(root)):
            raise ValueError('Source changed since engineering checks; rerun scripts/verify-engineering.py')
        suites = report['suites']
        if (set(suites) != {'product', 'reconstruction'} or report.get('native_capabilities', {}).get('adapter_version') != '0.1.1'
                or 'abort' not in report['native_capabilities'].get('capabilities', [])):
            raise ValueError('Engineering report lacks required native lifecycle or suites')
        for name, suite in suites.items():
            if suite['returncode'] != 0 or suite['tests_run'] < 1 or suite['skipped'] != 0:
                raise ValueError(f'Engineering suite not fully executed: {name}')
            log = root / 'evidence/rf31' / f'{name}-tests.txt'
            if sha256(log.read_bytes()).hexdigest() != suite['log_sha256']:
                raise ValueError(f'Engineering log differs from recorded result: {name}')
        return {'status': 'pass', 'suites': {name: suite['tests_run'] for name, suite in suites.items()},
                'scope': 'recorded repository regressions with matching source; no new user target'}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {'status': 'fail', 'reason': str(exc)}
