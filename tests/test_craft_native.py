"""Real pinned Craft engine operations; fixtures are not target-equivalence proof."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from reverse_fusion.craft_native import invoke_native, native_binary, prepare_native
from reverse_fusion.session_builder import check_session


ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / 'vendor/craft/native/windows-x64/reverse-fusion-craft-native.exe'


@unittest.skipUnless(os.name == 'nt' and BINARY.is_file(), 'Install the source-bound native Craft component')
class NativeCraftTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='rf Craft 项目 ')
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name)
        (self.project / 'tasks.md').write_text('T001 native engine fixture, no target proof', encoding='utf-8')
        (self.project / 'research.json').write_text('{"scope":"synthetic fixture"}', encoding='utf-8')
        self.command = f'"{sys.executable}" main.py'

    def prepare(self, commands=None, timeout=10, extra_outputs=None):
        return prepare_native(self.project, lease='native/lease.json', workspace='native/workspace',
                              receipt='native/session.json', tasks=['T001'], task_files=['tasks.md'],
                              research_files=['research.json'], allowed_outputs=['app/main.py', *(extra_outputs or [])],
                              check_commands=commands or [self.command], command_timeout_seconds=timeout)

    def call(self, operation, **params):
        return invoke_native(self.project, lease='native/lease.json', operation=operation, params=params)

    def test_real_native_lifecycle_invalidates_old_checks_and_keeps_business_acceptance_separate(self):
        self.assertEqual(native_binary(), BINARY)
        result = self.prepare()
        self.assertEqual(result['native']['data']['native_operation'], 'Workspace::create_at')
        with self.assertRaisesRegex(ValueError, 'needs all frozen'):
            self.call('cleanup')
        self.call('build', path='app/main.py', content='print(6 * 7)\n')
        run = self.call('check', command=self.command, timeout_secs=10)['data']['output']['result']
        self.assertTrue(run['succeeded'], run)
        self.assertEqual(run['stdout'].strip(), '42')
        self.call('refine', path='app/main.py', old_text='6 * 7', new_text='7 * 6')
        with self.assertRaisesRegex(ValueError, 'needs all frozen'):
            self.call('cleanup')
        self.call('check', command=self.command, timeout_secs=10)
        self.assertEqual(self.call('return_summary')['data']['native_tool'], 'build_files_list')
        self.assertEqual(self.call('cleanup')['data']['status'], 'candidate')
        for phase in ('check', 'refine', 'finish'):
            observed = check_session(self.project, receipt='native/session.json', phase=phase)
        self.assertEqual(observed['business_acceptance'], 'not-performed')
        events = [json.loads(line) for line in (self.project / 'native/lease.events.jsonl').read_text().splitlines()]
        self.assertTrue(all(event['native_binary_sha256'] for event in events))

    def test_native_boundary_rejects_output_escape_wrong_commands_and_changed_research(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError, 'outside frozen'):
            self.call('build', path='app/../../outside.py', content='bad')
        with self.assertRaisesRegex(ValueError, 'differs from frozen'):
            self.call('check', command='echo unauthorized-command', timeout_secs=1)
        (self.project / 'research.json').write_text('{"scope":"changed"}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Frozen input changed'):
            self.call('build', path='app/main.py', content='bad')
        self.assertFalse((self.project / 'native/workspace/app/main.py').exists())
        self.assertFalse((self.project / 'outside.py').exists())

    def test_nonzero_native_command_is_not_a_passing_check(self):
        self.prepare()
        self.call('build', path='app/main.py', content='raise SystemExit(7)\n')
        run = self.call('check', command=self.command, timeout_secs=10)['data']['output']['result']
        self.assertEqual(run['exit_code'], 7)
        self.assertFalse(run['succeeded'])
        with self.assertRaisesRegex(ValueError, 'needs all frozen'):
            self.call('cleanup')

    def test_failed_batch_can_abort_after_frozen_drift_and_retains_original_records(self):
        self.prepare()
        self.call('build', path='app/main.py', content='raise SystemExit(7)\n')
        original = json.loads((self.project / 'native/session.json').read_text())['frozen_refs']
        (self.project / 'research.json').unlink()
        result = self.call('abort', reason='Research needs a new reviewed batch')['data']
        self.assertEqual(result['status'], 'aborted')
        self.assertIn('research.json', result['changed_frozen_refs'])
        record = json.loads((self.project / 'native/session.json').read_text())
        self.assertEqual(record['frozen_refs'], original)
        self.assertEqual(record['phase'], 'aborted')
        self.assertTrue((self.project / 'native/workspace/app/main.py').is_file())
        with self.assertRaisesRegex(ValueError, 'closed'):
            self.call('build', path='app/main.py', content='must not resume an aborted batch')
        with self.assertRaisesRegex(ValueError, 'aborted'):
            check_session(self.project, receipt='native/session.json', phase='finish')

    def test_external_edit_cannot_reuse_native_checks_or_finish_after_cleanup(self):
        self.prepare()
        self.call('build', path='app/main.py', content='print(42)\n')
        self.call('check', command=self.command, timeout_secs=10)
        candidate = self.project / 'native/workspace/app/main.py'
        candidate.write_text('print(43)\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'needs all frozen'):
            self.call('cleanup')
        self.call('check', command=self.command, timeout_secs=10)
        for phase in ('check', 'refine'):
            check_session(self.project, receipt='native/session.json', phase=phase)
        with self.assertRaisesRegex(ValueError, 'Native completion requires'):
            check_session(self.project, receipt='native/session.json', phase='finish')
        self.call('cleanup')
        candidate.write_text('print(44)\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Native completion requires'):
            check_session(self.project, receipt='native/session.json', phase='finish')

    def test_existing_workspace_is_rejected_before_creating_another_batch(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError, 'empty new workspace'):
            prepare_native(self.project, lease='new/lease.json', workspace='native/workspace',
                receipt='new/session.json', tasks=['T001'], task_files=['tasks.md'],
                research_files=['research.json'], allowed_outputs=['app/main.py'], check_commands=[self.command])
        self.assertFalse((self.project / 'new').exists())

    def test_binary_patch_and_hybrid_delivery_use_native_commands_and_preserve_original(self):
        # Owned inert binary fixture, not third-party licensing/patch evidence.
        original = b'RF-OWNED\x00MODE=OLD\x00\xff\x80'
        (self.project / 'original.bin').write_bytes(original)
        (self.project / 'research.json').write_text(json.dumps({
            'scope': 'owned delivery transport; change MODE=OLD to MODE=NEW only',
            'original_hex': original.hex(), 'approved_bytes': [original.index(b'OLD'), 3]}), encoding='utf-8')
        (self.project / 'tasks.md').write_text('T001 prepare verified patch and hybrid wrapper from owned fixture', encoding='utf-8')
        self.command = f'"{sys.executable}" build_delivery.py'
        self.prepare(extra_outputs=['app/build_delivery.py', 'app/patched.bin', 'app/hybrid.py'])
        script = ('from pathlib import Path\n'
            f'original=bytes.fromhex("{original.hex()}")\n'
            'assert original.count(b"MODE=OLD")==1\n'
            'patched=original.replace(b"MODE=OLD",b"MODE=NEW")\n'
            'Path("patched.bin").write_bytes(patched)\n'
            'Path("hybrid.py").write_text("from pathlib import Path\\nprint(Path(__file__).with_name(\'patched.bin\').read_bytes().hex())\\n",encoding="utf-8")\n'
            'assert len(original)==len(patched)\n'
            'assert sum(a!=b for a,b in zip(original,patched))==3\n'
            'print("owned binary patch and wrapper verified")\n')
        self.call('build', path='app/main.py', content='# owned transport test; no arbitrary reconstruction claim\n')
        self.call('build', path='app/build_delivery.py', content=script)
        self.call('check', command=self.command, timeout_secs=10)
        result = self.call('cleanup')
        self.assertEqual(result['data']['status'], 'candidate')
        self.assertEqual((self.project / 'original.bin').read_bytes(), original)
        patched = self.project / 'native/workspace/app/patched.bin'
        self.assertEqual(patched.read_bytes(), original.replace(b'OLD', b'NEW'))
        wrapper = subprocess.run([sys.executable, str(patched.with_name('hybrid.py'))], capture_output=True, timeout=5)
        self.assertEqual(wrapper.stdout.strip().decode(), patched.read_bytes().hex())
        for phase in ('check', 'refine', 'finish'):
            checked = check_session(self.project, receipt='native/session.json', phase=phase)
        self.assertEqual(checked['phase'], 'finish')

    def test_timeout_stops_owned_descendant_and_serializes_writers(self):
        self.prepare(timeout=2, extra_outputs=['app/owned-child.pid'])
        code = ('import subprocess,sys,time\nfrom pathlib import Path\n'
                'child=subprocess.Popen([sys.executable,"-c","import time;time.sleep(90)"],'
                'creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))\n'
                'Path("owned-child.pid").write_text(str(child.pid))\ntime.sleep(90)\n')
        self.call('build', path='app/main.py', content=code)
        pid_file = self.project / 'native/workspace/app/owned-child.pid'
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.call, 'check', command=self.command, timeout_secs=2)
            deadline = time.monotonic() + 5
            while not pid_file.exists() and time.monotonic() < deadline and not future.done():
                time.sleep(.025)
            self.assertTrue(pid_file.exists(), 'Native timeout fixture did not start')
            with self.assertRaisesRegex(ValueError, 'Another native Craft operation'):
                self.call('build', path='app/main.py', content='should not write while check owns lease')
            with self.assertRaisesRegex(ValueError, 'Another native Craft operation'):
                self.call('abort', reason='Must not abort an active writer')
            with self.assertRaisesRegex(ValueError, 'timed out|timeout|time limit|deadline|took longer'):
                future.result(timeout=12)
        child_pid = int(pid_file.read_text())
        probe = subprocess.run(['powershell', '-NoProfile', '-Command',
                                f'if (Get-Process -Id {child_pid} -ErrorAction SilentlyContinue) {{ "alive" }}'],
                               capture_output=True, timeout=5)
        if probe.stdout.strip():
            # This exact PID came from this owned fixture; stop it before failing.
            subprocess.run(['taskkill', '/PID', str(child_pid), '/T', '/F'], capture_output=True, timeout=5)
        self.assertFalse(probe.stdout.strip(), 'Native process cleanup left its owned child alive')
        with self.assertRaisesRegex(ValueError, 'needs all frozen'):
            self.call('cleanup')


if __name__ == '__main__':
    unittest.main()
