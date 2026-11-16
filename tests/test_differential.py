import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import time

from reverse_fusion.differential import compare_processes
from reverse_fusion.owned_process import run_owned


class DifferentialTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix='rf process 比较 ')
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        for side, source in [('original', 'import sys\nprint(sys.stdin.read().strip().upper())\n'),
                             ('candidate', 'import sys\nvalue=sys.stdin.read()\nprint(value.strip().upper())\n')]:
            (self.root / side).mkdir()
            (self.root / side / 'main.py').write_text(source, encoding='utf-8')
        self.plan = {'version': 1, 'scope': 'synthetic text normalization only',
            'original': {'argv': [sys.executable, 'main.py'], 'cwd': 'original', 'sources': ['original/main.py']},
            'candidate': {'argv': [sys.executable, 'main.py'], 'cwd': 'candidate', 'sources': ['candidate/main.py']},
            'cases': [{'id': 'plain', 'stdin': 'abc\n'}, {'id': 'unicode', 'stdin': '你好\n'}], 'timeout_seconds': 3}
        self.write_plan()

    def write_plan(self):
        (self.root / 'plan.json').write_text(json.dumps(self.plan), encoding='utf-8')

    def test_independent_runs_pass_wrong_output_fails_and_same_source_is_rejected(self):
        result = compare_processes(self.root, 'plan.json', 'run/pass')
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['rea_native_proof'], 'not-performed')
        self.assertTrue(all(c['original']['elapsed_ms'] > 0 for c in result['cases']))
        (self.root / 'candidate/main.py').write_text('print("wrong")\n', encoding='utf-8')
        self.assertEqual(compare_processes(self.root, 'plan.json', 'run/fail')['status'], 'fail')
        self.plan['candidate'] = self.plan['original']
        self.write_plan()
        with self.assertRaisesRegex(ValueError, 'distinct source'):
            compare_processes(self.root, 'plan.json', 'run/same')
        self.assertFalse((self.root / 'run/same').exists())

    def test_missing_executable_and_timeout_cannot_be_pass(self):
        self.plan['candidate']['argv'] = [str(self.root / 'missing.exe')]
        self.write_plan()
        self.assertEqual(compare_processes(self.root, 'plan.json', 'run/missing')['status'], 'unknown')
        self.plan['candidate']['argv'] = [sys.executable, '-c', 'import time;time.sleep(30)']
        self.plan['timeout_seconds'] = .2
        self.write_plan()
        self.assertEqual(compare_processes(self.root, 'plan.json', 'run/timeout')['status'], 'unknown')

    def test_unbounded_output_is_not_loaded_or_accepted_as_complete(self):
        result = run_owned([sys.executable, '-c', 'print("x"*10000)'],cwd=self.root,stdin=b'',timeout=3,max_output_bytes=128)
        self.assertEqual(result['status'], 'unknown')
        self.assertTrue(result['output_truncated'])
        self.assertEqual(len(result['stdout']), 129)

    def test_large_unread_stdin_does_not_block_outer_deadline(self):
        started=time.monotonic()
        result=run_owned([sys.executable,'-c','import time;time.sleep(30)'],cwd=self.root,
                         stdin=b'x'*(2*1024*1024),timeout=.2)
        self.assertEqual(result['status'],'unknown')
        self.assertEqual(result['reason'],'timeout')
        self.assertLess(time.monotonic()-started,3)

    def test_mutated_input_and_overwrite_are_rejected(self):
        (self.root / 'candidate/main.py').write_text('from pathlib import Path\nPath("main.py").write_text("changed")\nprint("ABC")\n', encoding='utf-8')
        result = compare_processes(self.root, 'plan.json', 'run/drift')
        self.assertEqual(result['status'], 'unknown')
        self.assertIn('candidate/main.py', result['changed_inputs'])
        with self.assertRaisesRegex(ValueError, 'already exists'):
            compare_processes(self.root, 'plan.json', 'run/drift')

    @unittest.skipUnless(os.name == 'nt', 'actual Windows Job lifecycle')
    def test_timeout_and_success_close_owned_descendants(self):
        for wait in (True, False):
            code = ('import subprocess,sys,time\nfrom pathlib import Path\n'
                    'child=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"],'
                    'stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n'
                    'Path("child.pid").write_text(str(child.pid))\n' + ('time.sleep(60)\n' if wait else 'print("parent done")\n'))
            result = run_owned([sys.executable, '-c', code], cwd=self.root, stdin=b'', timeout=.4)
            self.assertEqual(result['status'], 'unknown' if wait else 'observed')
            self.assertIsNotNone(result['peak_job_bytes'])
            pid = int((self.root / 'child.pid').read_text())
            probe = subprocess.run(['powershell', '-NoProfile', '-Command',
                f'if (Get-Process -Id {pid} -ErrorAction SilentlyContinue) {{ "alive" }}'],capture_output=True,timeout=5)
            self.assertFalse(probe.stdout.strip(), 'Owned descendant survived its job close')
