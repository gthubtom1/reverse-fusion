"""I/O fault injection in owned installer surfaces; no real user files touched."""
from contextlib import ExitStack, redirect_stdout
import io
from pathlib import Path
import tempfile
import os
import subprocess
import shutil
import unittest
from unittest.mock import patch

from reverse_fusion import cli, global_adapter
from reverse_fusion.file_updates import atomic_write
from reverse_fusion.contracts import is_safe_relative_path


class InstallFailureTests(unittest.TestCase):
    def test_portable_paths_reject_windows_streams_and_control_characters(self):
        for name in ('work/file:stream', 'work/a\x00.json', 'work/a\n.json'):
            self.assertFalse(is_safe_relative_path(name))

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / 'home'
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.paths = global_adapter.adapter_paths(self.home)
        self.receipt = self.repo / 'state/install.json'

    def test_second_entry_write_failure_restores_the_first_file(self):
        global_adapter.install_global_adapter(self.repo, self.home)
        before = {p: p.read_bytes() for p in self.paths.values()}

        def fail_agents(path, data):
            if path == self.paths['agents']:
                raise OSError('injected global instructions write failure')
            atomic_write(path, data)

        with patch.object(global_adapter, 'atomic_write', side_effect=fail_agents):
            with self.assertRaisesRegex(OSError, 'injected'):
                global_adapter.install_global_adapter(self.root / 'new', self.home)
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_atomic_replace_failure_keeps_old_file_and_removes_temporary(self):
        target = self.root / 'record.json'
        target.write_bytes(b'original record')
        with patch('reverse_fusion.file_updates.os.replace', side_effect=OSError('injected replace failure')):
            with self.assertRaises(OSError):
                atomic_write(target, b'new bytes')
        self.assertEqual(target.read_bytes(), b'original record')
        self.assertEqual(list(self.root.glob('.rf-update-*')), [])

    def cli_patches(self):
        stack = ExitStack()
        stack.enter_context(patch.object(cli, 'ROOT', self.repo))
        stack.enter_context(patch.object(cli, 'adapter_paths', return_value=self.paths))
        stack.enter_context(patch.object(global_adapter, 'adapter_paths', return_value=self.paths))
        stack.enter_context(patch.object(cli, 'check_contracts', return_value={'status': 'pass'}))
        stack.enter_context(patch.object(cli, 'component_status', return_value={}))
        stack.enter_context(patch.object(cli, 'core_deployment', return_value={'status': 'installed'}))
        stack.enter_context(patch.object(cli, 'detect_hosts', return_value={}))
        stack.enter_context(redirect_stdout(io.StringIO()))
        return stack

    def test_install_receipt_failure_rolls_back_both_global_entries(self):
        global_adapter.install_global_adapter(self.root / 'old', self.home)
        self.receipt.parent.mkdir()
        self.receipt.write_bytes(b'{"original":true}')
        before = {p: p.read_bytes() for p in [*self.paths.values(), self.receipt]}
        with self.cli_patches(), patch.object(cli, '_write_state', side_effect=OSError('injected receipt failure')):
            self.assertEqual(cli.main(['install', '--apply', '--client', 'codex']), 2)
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_uninstall_receipt_failure_restores_removed_entries(self):
        global_adapter.install_global_adapter(self.repo, self.home)
        self.receipt.parent.mkdir()
        self.receipt.write_bytes(b'{"global_adapter":{"enabled":true}}')
        before = {p: p.read_bytes() for p in [*self.paths.values(), self.receipt]}
        original_unlink = Path.unlink

        def fail_receipt(path, *args, **kwargs):
            if path == self.receipt:
                raise OSError('injected receipt unlink failure')
            return original_unlink(path, *args, **kwargs)

        with self.cli_patches(), patch.object(Path, 'unlink', new=fail_receipt):
            self.assertEqual(cli.main(['uninstall', '--apply']), 2)
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    @unittest.skipUnless(os.name == 'nt', 'Windows uninstall lifecycle')
    def test_uninstall_script_keeps_receipt_when_python_is_missing(self):
        source = Path(__file__).resolve().parents[1]
        scripts = self.repo / 'scripts'
        (scripts / 'lib').mkdir(parents=True)
        for name in ('uninstall.ps1', 'lib/ScriptSupport.ps1'):
            shutil.copyfile(source / 'scripts' / name, scripts / name)
        self.receipt.parent.mkdir()
        self.receipt.write_bytes(b'{"global_adapter":{"enabled":true}}')
        venv = self.repo / '.venv'
        venv.mkdir()
        (venv / 'keep.txt').write_bytes(b'preserve existing installation files')
        run = subprocess.run(['powershell', '-NoProfile', '-File', str(scripts / 'uninstall.ps1'), '-Apply'],
                             capture_output=True, timeout=15)
        self.assertNotEqual(run.returncode, 0)
        self.assertTrue(self.receipt.is_file())
        self.assertTrue((venv / 'keep.txt').is_file())


if __name__ == '__main__':
    unittest.main()
