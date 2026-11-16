"""Cross-entry regressions using inert tools and temporary client configuration.

The mocked process boundary records the environment actually dispatched by the
CLI and MCP launcher. No real provider, client setting or credential is used.
"""
from contextlib import chdir, redirect_stderr, redirect_stdout
from hashlib import sha256
import io
import json
import os
import platform
from pathlib import Path
import runpy
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from reverse_fusion.mcp_adapter import (BEGIN, REA_ENV, SERVERS, install_mcp,
                                       inspect_mcp, mcp_paths, remove_mcp)
from reverse_fusion.mcp_probe import connection_status, runtime_fingerprint
from reverse_fusion.provider_runtime import (ALL_KEYS, launch_environment,
                                            provider_status)
from reverse_fusion.rea_runner import run_rea


SOURCE_ROOT = Path(__file__).resolve().parents[1]


class ProviderIntegrationTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        for key in ALL_KEYS | {'REVERSE_FUSION_NODE'}:
            os.environ.pop(key, None)
        temporary = tempfile.TemporaryDirectory(prefix='rf provider integration 中文 ')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / 'shared checkout'
        self.home = self.base / 'isolated home'
        self.config = mcp_paths(self.home)['config']
        self.node = self.inert('vendor/node/node-pin/node.exe')
        self.craft = self.inert('vendor/craft/mcp/windows-x64/0.1.1/reverse-fusion-craft-mcp.exe')
        self.python = self.inert('.venv/' + ('Scripts/python.exe' if os.name == 'nt' else 'bin/python'))
        self.entry = self.inert('vendor/rea/package/scripts/rea.mjs')
        self.inert('reverse_fusion/provider_runtime.py')
        system = {'Windows': 'windows', 'Linux': 'linux', 'Darwin': 'macos'}.get(platform.system(), 'unknown')
        machine = platform.machine().lower()
        architecture = 'x64' if machine in {'amd64', 'x86_64'} else 'arm64' if machine in {'arm64', 'aarch64'} else machine
        self.write_json(self.root/'components/craft-mcp/manifest.json', {'platforms': {
            f'{system}-{architecture}': {'local_path': self.craft.relative_to(self.root).as_posix()},
        }})
        self.launcher = self.root / 'scripts/mcp-launch.py'
        self.launcher.parent.mkdir(parents=True, exist_ok=True)
        self.launcher.write_bytes((SOURCE_ROOT / 'scripts/mcp-launch.py').read_bytes())
        self.write_json(self.root / 'state/rea-runtime.json', {
            'schema_version': 1, 'repository_root': str(self.root), 'node': str(self.node),
        })

    def inert(self, relative, content=b'inert owned identity; never executed'):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def write_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding='utf-8')

    def saved_paths(self, paths):
        self.write_json(self.root / 'state/provider-runtime.json', {
            'schema_version': 1, 'repository_root': str(self.root),
            'paths': {key: str(value) for key, value in paths.items()},
        })

    def observed_cli(self, output='cli-output'):
        """Dispatch real run_rea preparation while replacing only process I/O."""
        self.write_json(self.root / 'args.json', [])
        observed = {'stdout': b'{"ok":true,"result":{}}', 'stderr': b'',
                    'status': 'observed', 'output_truncated': False, 'exit_code': 0}
        with patch('reverse_fusion.rea_runner.run_owned', return_value=observed) as runner:
            result = run_rea(self.root, self.root, operation='analyze-javascript-application',
                             arguments='args.json', output=output)
        self.assertEqual(result['execution_status'], 'returned')
        return runner.call_args.kwargs['env']

    def status_fixture(self):
        """A synthetic prior observation; only staleness detection is qualified."""
        install_mcp(self.root, self.home)
        entries = tomllib.loads(self.config.read_text(encoding='utf-8'))['mcp_servers']
        saved = {
            'schema_version': 1, 'status': 'pass', 'repository': str(self.root),
            'scope': 'inert mocked observation for stale-provider regression only',
            'runtime_inputs': runtime_fingerprint(self.root),
            'servers': [{
                'server': name, 'registration': entries[name],
                'binary_sha256': sha256(Path(entries[name]['command']).read_bytes()).hexdigest(),
                'entry_sha256': sha256(self.entry.read_bytes()).hexdigest() if name.endswith('-rea') else None,
                'cleanup': {'status': 'verified' if os.name == 'nt' else 'observed'},
                'server_info': {'name': 'inert-test'}, 'tools': 1, 'prompts': 0, 'called': 'fixture',
            } for name in SERVERS],
        }
        self.write_json(self.root / 'state/mcp-runtime.json', saved)

    def test_no_receipt_does_not_borrow_terminal_only_provider_paths(self):
        # A background app can have a different snapshot. Neither snapshot may
        # silently select unrecorded providers during an operation.
        base = {'PATH': 'unrelated-path', 'APP_UNRELATED_SETTING': 'retained'}
        base.update({key: str(self.root / 'unrecorded tool') for key in ALL_KEYS})
        environment = launch_environment(self.root, base=base)
        self.assertTrue(set(ALL_KEYS).isdisjoint(environment))
        self.assertEqual(environment, {'PATH': 'unrelated-path', 'APP_UNRELATED_SETTING': 'retained'})

    def test_nonobject_receipts_give_cli_blocked_json_without_mutation_or_process(self):
        from reverse_fusion.cli import main
        receipt=self.root/'state/provider-runtime.json'
        for value in ([],None,'wrong JSON root'):
            for refresh in (False,True):
                with self.subTest(value=value,refresh=refresh):
                    self.write_json(receipt,value)
                    original=receipt.read_bytes()
                    stdout,stderr=io.StringIO(),io.StringIO()
                    with (patch('reverse_fusion.cli.ROOT',self.root),
                          patch('reverse_fusion.mcp_process.McpProcess') as process,
                          patch('reverse_fusion.provider_runtime.shutil.which') as discovery,
                          redirect_stdout(stdout),redirect_stderr(stderr)):
                        code=main(['providers',*(['--refresh'] if refresh else []),'--format','json'])
                    self.assertEqual(code,2)
                    result=json.loads(stdout.getvalue())
                    self.assertEqual(result['operation'],'providers')
                    self.assertEqual(result['status'],'blocked')
                    self.assertIn('Provider runtime receipt is not bound',result['reason'])
                    self.assertEqual(stderr.getvalue(),'')
                    self.assertEqual(receipt.read_bytes(),original)
                    discovery.assert_not_called()
                    process.assert_not_called()

    def test_nonobject_receipts_make_actual_launcher_report_stderr_without_starting_child(self):
        receipt=self.root/'state/provider-runtime.json'
        for value in ([],None,'wrong JSON root'):
            for component in ('rea','craft','rea-cli'):
                with self.subTest(value=value,component=component):
                    self.write_json(receipt,value)
                    original=receipt.read_bytes()
                    stdout=io.TextIOWrapper(io.BytesIO(),encoding='utf-8')
                    stderr=io.TextIOWrapper(io.BytesIO(),encoding='utf-8')
                    stdin=io.TextIOWrapper(io.BytesIO(),encoding='utf-8')
                    with (patch('reverse_fusion.mcp_process.McpProcess') as process,
                          patch.object(sys,'argv',[str(self.launcher),component]),
                          patch.object(sys,'path',list(sys.path)),
                          patch.object(sys,'stdin',stdin),
                          patch.object(sys,'stdout',stdout),
                          patch.object(sys,'stderr',stderr)):
                        with self.assertRaises(SystemExit) as exit_result:
                            runpy.run_path(str(self.launcher),run_name='__main__')
                    self.assertEqual(exit_result.exception.code,2)
                    stdout.flush();stderr.flush()
                    self.assertEqual(stdout.buffer.getvalue(),b'')
                    diagnosis=stderr.buffer.getvalue().decode('utf-8')
                    self.assertIn('Reverse Fusion MCP launch: Provider runtime receipt is not bound',diagnosis)
                    self.assertNotIn('Traceback',diagnosis)
                    process.assert_not_called()
                    self.assertEqual(receipt.read_bytes(),original)
                    stdin.close();stdout.close();stderr.close()

    def test_cli_and_actual_launcher_restore_same_saved_paths_and_drop_ambient_paths(self):
        selected = self.inert('tools/saved adb.exe')
        self.saved_paths({'REA_ADB_PATH': selected})
        ambient = {'REA_ADB_PATH': str(self.root / 'old adb.exe'),
                   'GHIDRA_INSTALL_DIR': str(self.root / 'old ghidra'),
                   'REVERSE_FUSION_CRAFT_TOOL_ADB': str(self.root / 'unrecorded adb.exe'),
                   'APP_UNRELATED_SETTING': 'keep-current-host-value'}
        with patch.dict(os.environ, ambient):
            cli_environment = self.observed_cli()
            project = self.base/'outcome software'
            project.mkdir()
            (project/'owned source.mjs').write_text('export const owned = true;\n', encoding='utf-8')
            cli_tail = ['analyze-javascript-application', '--input-path', 'owned source.mjs']
            commands = {
                'rea': ([str(self.launcher), 'rea'], [str(self.node), str(self.entry), 'mcp']),
                'craft': ([str(self.launcher), 'craft'], [str(self.craft), '--all-tools', '--deep-mode',
                          '--allow-run', '--state-dir', str(self.root/'state/craft-mcp')]),
                'rea-cli': ([str(self.launcher), 'rea-cli', *cli_tail], [str(self.node), str(self.entry), *cli_tail]),
            }
            for component, (arguments, expected_command) in commands.items():
                with self.subTest(component=component):
                    # Run the real copied launcher, mocking its owned process
                    # boundary rather than its environment resolver.
                    with (chdir(project),
                          patch('reverse_fusion.mcp_process.McpProcess') as process,
                          patch('reverse_fusion.craft_mcp.mcp_binary', return_value=self.craft),
                          patch.object(sys, 'argv', arguments),
                          patch.object(sys, 'path', list(sys.path)),
                          patch.object(sys, 'stdin', io.TextIOWrapper(io.BytesIO(), encoding='utf-8')),
                          patch.object(sys, 'stdout', io.TextIOWrapper(io.BytesIO(), encoding='utf-8')),
                          patch.object(sys, 'stderr', io.TextIOWrapper(io.BytesIO(), encoding='utf-8'))):
                        process.return_value.process.wait.return_value = 0
                        with self.assertRaises(SystemExit) as exit_result:
                            runpy.run_path(str(self.launcher), run_name='__main__')
                        self.assertEqual(exit_result.exception.code, 0)
                    self.assertEqual(process.call_args.kwargs['env'], cli_environment)
                    self.assertEqual(process.call_args.args[0], expected_command)
                    self.assertEqual(Path(process.call_args.kwargs['cwd']),
                                     project if component == 'rea-cli' else self.root)
                    process.return_value.close.assert_called_once_with(grace_seconds=0)
        self.assertEqual(cli_environment['REA_ADB_PATH'], str(selected))
        self.assertNotIn('GHIDRA_INSTALL_DIR', cli_environment)
        self.assertNotIn('REVERSE_FUSION_CRAFT_TOOL_ADB', cli_environment)
        self.assertEqual(cli_environment['APP_UNRELATED_SETTING'], 'keep-current-host-value')

    def test_missing_provider_does_not_block_independent_cli_dispatch(self):
        selected = self.inert('tools/adb.exe')
        self.saved_paths({'REA_ADB_PATH': selected})
        selected.unlink()
        self.assertIn('REA_ADB_PATH', provider_status(self.root)['unavailable'])
        environment = self.observed_cli()
        self.assertNotIn('REA_ADB_PATH', environment)
        self.assertTrue((self.root / 'cli-output/stdout.json').is_file())

    def test_deleted_selected_provider_invalidates_prior_connection_observation(self):
        selected = self.inert('tools/adb.exe')
        self.saved_paths({'REA_ADB_PATH': selected})
        with (patch('reverse_fusion.craft_mcp.mcp_binary', return_value=self.craft),
              patch('reverse_fusion.mcp_adapter.mcp_paths', return_value={'config': self.config})):
            self.status_fixture()
            self.assertEqual(connection_status(self.root)['status'], 'pass')
            selected.unlink()
            status = connection_status(self.root)
        self.assertEqual(status['status'], 'fail')
        self.assertIn('provider', status['reason'].lower())

    def test_same_path_replacement_invalidates_prior_connection_observation(self):
        selected = self.inert('tools/adb.exe', b'old provider bytes')
        self.saved_paths({'REA_ADB_PATH': selected})
        with (patch('reverse_fusion.craft_mcp.mcp_binary', return_value=self.craft),
              patch('reverse_fusion.mcp_adapter.mcp_paths', return_value={'config': self.config})):
            self.status_fixture()
            self.assertEqual(connection_status(self.root)['status'], 'pass')
            original = runtime_fingerprint(self.root)
            selected.write_bytes(b'new provider bytes at exactly the same selected path')
            self.assertNotEqual(runtime_fingerprint(self.root), original)
            self.assertEqual(provider_status(self.root)['unavailable'], {})
            self.assertEqual(connection_status(self.root)['status'], 'fail')

    def test_java_directory_identity_tracks_executable_changes(self):
        java = self.inert('tools/jdk/bin/' + ('java.exe' if os.name == 'nt' else 'java'), b'java release one')
        home = java.parent.parent
        self.inert('tools/jdk/release', b'JAVA_VERSION="21-test"')
        self.saved_paths({'JAVA_HOME': home})
        with (patch('reverse_fusion.craft_mcp.mcp_binary', return_value=self.craft),
              patch('reverse_fusion.mcp_adapter.mcp_paths', return_value={'config': self.config})):
            self.status_fixture()
            self.assertEqual(connection_status(self.root)['status'], 'pass')
            java.write_bytes(b'java release two')
            self.assertEqual(connection_status(self.root)['status'], 'fail')

    def test_old_rf35_direct_registrations_migrate_without_changing_adjacent_bytes(self):
        prefix = b'\xef\xbb\xbf# original user config\r\n[mcp_servers.other]\r\ncommand="retained"'
        suffix = b'\r\n[unrelated_section]\r\nvalue = "leave this exact suffix"\r\n'
        self.config.parent.mkdir(parents=True, exist_ok=True)
        self.config.write_bytes(prefix)
        old = {
            SERVERS[0]: {'command': str(self.node), 'args': [str(self.entry), 'mcp'],
                         'cwd': str(self.root), 'startup_timeout_sec': 60,
                         'tool_timeout_sec': 600, 'env': dict(REA_ENV)},
            SERVERS[1]: {'command': str(self.craft),
                         'args': ['--all-tools', '--deep-mode', '--allow-run',
                                  '--state-dir', str(self.root / 'state/craft-mcp')],
                         'cwd': str(self.root), 'startup_timeout_sec': 60, 'tool_timeout_sec': 600},
        }
        with patch('reverse_fusion.mcp_adapter._registrations', return_value=old):
            install_mcp(self.root, self.home)
        self.config.write_bytes(self.config.read_bytes() + suffix)
        self.assertEqual(inspect_mcp(self.root, self.home)['status'], 'stale')
        self.assertTrue(install_mcp(self.root, self.home)['changed'])
        migrated = self.config.read_bytes()
        self.assertTrue(migrated.startswith(prefix))
        self.assertTrue(migrated.endswith(suffix))
        self.assertEqual(migrated.count(BEGIN), 1)
        entries = tomllib.loads(migrated.decode('utf-8-sig'))['mcp_servers']
        for server, component in zip(SERVERS, ('rea', 'craft')):
            self.assertEqual(entries[server]['command'], str(self.python))
            self.assertEqual(entries[server]['args'], [str(self.launcher), component])
        self.assertTrue(inspect_mcp(self.root, self.home)['enabled'])
        self.assertFalse(install_mcp(self.root, self.home)['changed'])
        remove_mcp(self.root, self.home)
        self.assertEqual(self.config.read_bytes(), prefix + suffix)


if __name__ == '__main__':
    unittest.main()
