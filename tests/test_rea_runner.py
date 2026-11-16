from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from reverse_fusion.rea_runner import run_rea


ROOT = Path(__file__).resolve().parents[1]


class ReaRunnerTests(unittest.TestCase):
    def test_partial_error_with_zero_exit_is_retained_and_never_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            (project/'args.json').write_text('[]')
            raw = b'{"ok":true,"limitations":["Resource constraint: worker exhausted its heap"]}'
            fake = {'status':'observed','exit_code':0,'output_truncated':False,'stdout':raw,'stderr':b''}
            with patch('reverse_fusion.rea_runner.run_owned',return_value=fake):
                report = run_rea(ROOT,project,operation='inspect-artifact',arguments='args.json',output='run')
            self.assertEqual(report['execution_status'],'partial')
            self.assertEqual((project/'run/stdout.json').read_bytes(),raw)
            self.assertIn('not-assessed',report['semantic_acceptance'])

    def test_real_official_schema_is_read_with_owned_process_and_recorded_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            project=Path(directory).resolve()
            (project/'args.json').write_text('["--schema","--format","json"]')
            report=run_rea(ROOT,project,operation='build-reconstruction-obligation-ledger',arguments='args.json',output='schema',timeout=15,memory_mb=768)
            self.assertEqual(report['execution_status'],'returned')
            self.assertEqual(report['process']['memory_limit_mb'],768)
            self.assertGreater(report['process']['elapsed_ms'],0)
            with self.assertRaisesRegex(ValueError,'Preserve existing'):
                run_rea(ROOT,project,operation='inspect-artifact',arguments='args.json',output='schema')
