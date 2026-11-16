"""I/O fault injection in owned installer surfaces; no real user files touched."""
from contextlib import ExitStack, redirect_stdout
import io
from pathlib import Path
import tempfile
import os
import subprocess
import shutil
import sys
import unittest
from unittest.mock import patch

from reverse_fusion import cli, global_adapter, mcp_adapter
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
        self.mcp = {'config': self.paths['agents'].parent / 'config.toml'}

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
        stack.enter_context(patch.object(mcp_adapter, 'adapter_paths', return_value=self.paths))
        stack.enter_context(patch.object(cli, 'mcp_paths', return_value=self.mcp))
        stack.enter_context(patch.object(mcp_adapter, '_registrations', return_value={
            'reverse-fusion-rea': {'command': 'synthetic-node', 'args': ['rea.mjs', 'mcp'], 'cwd':str(self.repo), 'startup_timeout_sec':60, 'tool_timeout_sec':600, 'env':dict(mcp_adapter.REA_ENV)},
            'reverse-fusion-craft': {'command': 'synthetic-craft', 'args': [], 'cwd':str(self.repo), 'startup_timeout_sec':60, 'tool_timeout_sec':600}}))
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
        self.mcp['config'].write_bytes(b'model = "unchanged-model"\n')
        before[self.mcp['config']] = self.mcp['config'].read_bytes()
        with self.cli_patches(), patch.object(cli, '_write_state', side_effect=OSError('injected receipt failure')):
            self.assertEqual(cli.main(['install', '--apply', '--client', 'codex']), 2)
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_uninstall_receipt_failure_restores_removed_entries(self):
        global_adapter.install_global_adapter(self.repo, self.home)
        self.receipt.parent.mkdir()
        self.receipt.write_bytes(b'{"global_adapter":{"enabled":true}}')
        before = {p: p.read_bytes() for p in [*self.paths.values(), self.receipt]}
        with self.cli_patches():
            mcp_adapter.install_mcp(self.repo)
        before[self.mcp['config']] = self.mcp['config'].read_bytes()
        original_unlink = Path.unlink
        receipt_failure_reached = []

        def fail_receipt(path, *args, **kwargs):
            if path == self.receipt:
                # The MCP/skill entries must already be removed, so this is an
                # actual mid-uninstall failure rather than an earlier refusal.
                self.assertFalse(self.paths['skill'].exists())
                self.assertFalse(self.mcp['config'].exists())
                receipt_failure_reached.append(True)
                raise OSError('injected receipt unlink failure')
            return original_unlink(path, *args, **kwargs)

        with self.cli_patches(), patch.object(Path, 'unlink', new=fail_receipt):
            self.assertEqual(cli.main(['uninstall', '--apply']), 2)
        self.assertEqual(receipt_failure_reached, [True])
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_missing_receipt_still_removes_owned_global_entries(self):
        with self.cli_patches():
            self.assertEqual(cli.main(['install', '--apply', '--client', 'codex']), 0)
            self.receipt.unlink()
            self.assertEqual(cli.main(['uninstall', '--apply']), 0)
            self.assertEqual(cli.main(['uninstall', '--apply']), 0)
        self.assertFalse(self.paths['skill'].exists())
        self.assertFalse(self.paths['agents'].exists())
        self.assertFalse(self.mcp['config'].exists())

    def test_missing_receipt_cannot_remove_newer_checkout_pointers(self):
        newer = self.root/'newer'
        global_adapter.install_global_adapter(newer, self.home)
        registrations = {
            'reverse-fusion-rea': {'command':'synthetic-node', 'args':['rea.mjs','mcp'], 'cwd':str(newer),
                                 'startup_timeout_sec':60, 'tool_timeout_sec':600, 'env':dict(mcp_adapter.REA_ENV)},
            'reverse-fusion-craft': {'command':'synthetic-craft', 'args':[], 'cwd':str(newer),
                                   'startup_timeout_sec':60, 'tool_timeout_sec':600}}
        with self.cli_patches(), patch.object(mcp_adapter, '_registrations', return_value=registrations):
            mcp_adapter.install_mcp(newer)
        before = {path:path.read_bytes() for path in [*self.paths.values(),self.mcp['config']]}
        with self.cli_patches():
            self.assertEqual(cli.main(['uninstall', '--apply']), 0)
        self.assertEqual({path:path.read_bytes() for path in before}, before)

    def test_missing_receipt_uncertain_ownership_blocks_without_partial_removal(self):
        for uncertain in ('instructions', 'mcp', 'skill', 'unmarked-instructions'):
            with self.subTest(uncertain=uncertain):
                # Each branch starts with a complete temporary owned install.
                with self.cli_patches():
                    self.assertEqual(cli.main(['install', '--apply', '--client', 'codex']), 0)
                self.receipt.unlink()
                target = (self.paths['agents'] if uncertain in {'instructions','unmarked-instructions'} else
                          self.paths['skill'] if uncertain=='skill' else self.mcp['config'])
                original = target.read_bytes()
                if uncertain == 'instructions':
                    target.write_bytes(original.replace(b'Keep the current project',b'Edited: keep the current project'))
                elif uncertain == 'skill':
                    target.write_bytes(b'# User-owned skill with uncertain runtime dependencies\n')
                elif uncertain == 'unmarked-instructions':
                    target.write_text(f'User-maintained instructions still call `{self.repo.as_posix()}/.venv/Scripts/python.exe`.\n',encoding='utf-8')
                else:
                    target.write_bytes(b'[mcp_servers.reverse-fusion-rea]\ncommand="unmanaged"\n')
                before = {path:path.read_bytes() for path in [*self.paths.values(),self.mcp['config']]}
                with self.cli_patches():
                    self.assertEqual(cli.main(['uninstall', '--apply']), 2)
                self.assertEqual({path:path.read_bytes() for path in before}, before)
                target.write_bytes(original)
                with self.cli_patches():
                    self.assertEqual(cli.main(['uninstall', '--apply']), 0)

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

    @unittest.skipUnless(os.name == 'nt', 'Windows uninstall lifecycle')
    def test_uninstall_script_without_receipt_or_python_retains_runtime_and_global_entries(self):
        source = Path(__file__).resolve().parents[1]
        scripts = self.repo/'scripts'
        (scripts/'lib').mkdir(parents=True)
        for name in ('uninstall.ps1', 'lib/ScriptSupport.ps1'):
            shutil.copyfile(source/'scripts'/name, scripts/name)
        global_adapter.install_global_adapter(self.repo,self.home)
        self.mcp['config'].write_bytes(b'[mcp_servers.reverse-fusion-rea]\ncommand="unmanaged"\n')
        venv = self.repo/'.venv'
        sentinel = venv/'Scripts/keep.txt'
        sentinel.parent.mkdir(parents=True)
        sentinel.write_bytes(b'owned runtime remainder requiring ownership review')
        before = {path:path.read_bytes() for path in [*self.paths.values(),self.mcp['config'],sentinel]}
        self.assertFalse(self.receipt.exists())
        environment = {**os.environ, 'USERPROFILE':str(self.home), 'CODEX_HOME':str(self.home/'.codex')}
        run = subprocess.run(['powershell','-NoProfile','-File',str(scripts/'uninstall.ps1'),'-Apply'],
                             cwd=self.repo,env=environment,capture_output=True,timeout=15)
        self.assertNotEqual(run.returncode,0)
        self.assertIn(b'Python is unavailable',run.stderr)
        self.assertNotIn(b'"status":"uninstalled"',run.stdout)
        self.assertEqual({path:path.read_bytes() for path in before},before)

    def test_shell_uninstall_without_receipt_or_python_retains_runtime_and_global_entries(self):
        shell = shutil.which('sh')
        if shell is None and os.name == 'nt':
            git = shutil.which('git')
            if git:
                candidate = Path(git).resolve().parents[1]/'bin/sh.exe'
                if candidate.is_file():
                    shell = str(candidate)
        self.assertIsNotNone(shell, 'Repository shell lifecycle check requires sh or Git for Windows')
        source = Path(__file__).resolve().parents[1]
        script = self.repo/'scripts/uninstall.sh'
        script.parent.mkdir()
        shutil.copyfile(source/'scripts/uninstall.sh',script)
        global_adapter.install_global_adapter(self.repo,self.home)
        venv = self.repo/'.venv'
        sentinel = venv/'keep.txt'
        sentinel.parent.mkdir()
        sentinel.write_bytes(b'owned runtime remainder requiring ownership review')
        before = {path:path.read_bytes() for path in [*self.paths.values(),sentinel]}
        self.assertFalse(self.receipt.exists())
        environment = {**os.environ, 'USERPROFILE':str(self.home), 'HOME':str(self.home),
                       'CODEX_HOME':str(self.home/'.codex'),'RF_PYTHON':Path(sys.executable).as_posix()}
        run = subprocess.run([shell,script.as_posix()],cwd=self.repo,env=environment,
                             capture_output=True,timeout=15)
        self.assertNotEqual(run.returncode,0)
        self.assertIn(b'Python is unavailable',run.stderr)
        self.assertNotIn(b'"status":"uninstalled"',run.stdout)
        self.assertEqual({path:path.read_bytes() for path in before},before)

    @unittest.skipUnless(os.name == 'nt', 'Windows uninstall lifecycle')
    def test_uninstall_script_retains_runtime_when_receipt_missing_and_pointer_unmanaged(self):
        source = Path(__file__).resolve().parents[1]
        shutil.copytree(source/'reverse_fusion', self.repo/'reverse_fusion',
                        ignore=shutil.ignore_patterns('__pycache__'))
        scripts = self.repo/'scripts'
        (scripts/'lib').mkdir(parents=True)
        for name in ('uninstall.ps1','lib/ScriptSupport.ps1'):
            shutil.copyfile(source/'scripts'/name, scripts/name)
        venv = self.repo/'.venv'
        create = subprocess.run([sys.executable, '-m', 'venv', '--without-pip', str(venv)],capture_output=True,timeout=20)
        self.assertEqual(create.returncode, 0, create.stderr)
        (venv/'keep.txt').write_bytes(b'retain runtime while a live unmanaged pointer may depend on it')
        global_adapter.install_global_adapter(self.repo,self.home)
        self.mcp['config'].write_bytes(b'[mcp_servers.reverse-fusion-rea]\ncommand="unmanaged"\n')
        before = {path:path.read_bytes() for path in [*self.paths.values(),self.mcp['config']]}
        environment = {**os.environ, 'USERPROFILE':str(self.home), 'CODEX_HOME':str(self.home/'.codex'),
                       'PYTHONPATH':str(self.repo)}
        run = subprocess.run(['powershell','-NoProfile','-File',str(scripts/'uninstall.ps1'),'-Apply'],
                             cwd=self.repo, env=environment, capture_output=True,timeout=20)
        self.assertNotEqual(run.returncode,0)
        self.assertTrue((venv/'Scripts/python.exe').is_file())
        self.assertTrue((venv/'keep.txt').is_file())
        self.assertEqual({path:path.read_bytes() for path in before}, before)


if __name__ == '__main__':
    unittest.main()
