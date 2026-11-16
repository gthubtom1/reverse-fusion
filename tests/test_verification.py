from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from reverse_fusion.verification import engineering_inputs, verification_status


class VerificationTests(unittest.TestCase):
    def test_source_drift_skipped_suite_and_log_drift_block_qualification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('VERSION', 'pyproject.toml', 'SOURCE-MANIFEST.json', 'reverse_fusion/main.py'):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('synthetic qualification fixture', encoding='utf-8')
            (root / 'release').mkdir()
            (root / 'release/manifest.json').write_text('{}')
            (root / 'evidence/rf31').mkdir(parents=True)
            report = {'schema_version': 1, 'status': 'pass', 'source_inputs': engineering_inputs(root),
                      'native_capabilities': {'adapter_version': '0.1.1', 'capabilities': ['abort']}, 'suites': {}}
            for name in ('product', 'reconstruction'):
                log = root / f'evidence/rf31/{name}-tests.txt'
                log.write_bytes(b'synthetic result, not an actual test run')
                report['suites'][name] = {'returncode': 0, 'tests_run': 1, 'skipped': 0,
                                         'log_sha256': sha256(log.read_bytes()).hexdigest()}
            path = root / 'release/verification.json'
            path.write_text(json.dumps(report))
            self.assertEqual(verification_status(root)['status'], 'pass')
            source = root / 'reverse_fusion/main.py'
            original = source.read_bytes()
            source.write_bytes(b'changed code after qualification')
            self.assertEqual(verification_status(root)['status'], 'fail')
            source.write_bytes(original)
            report['suites']['product']['skipped'] = 1
            path.write_text(json.dumps(report))
            self.assertEqual(verification_status(root)['status'], 'fail')
            report['suites']['product']['skipped'] = 0
            path.write_text(json.dumps(report))
            (root / 'evidence/rf31/product-tests.txt').write_bytes(b'log changed')
            self.assertEqual(verification_status(root)['status'], 'fail')
