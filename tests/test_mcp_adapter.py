import json
import os
import platform
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from reverse_fusion.mcp_adapter import BEGIN, END, install_mcp, inspect_mcp, mcp_paths, remove_mcp


class McpAdapterTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop('REVERSE_FUSION_NODE', None)
        temporary = tempfile.TemporaryDirectory(prefix='rf MCP 中文 ')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.home = self.base / 'home'
        self.root = self.make_repo('shared repo')
        self.config = mcp_paths(self.home)['config']

    def make_repo(self, name):
        root = self.base / name
        for relative in ('vendor/node/node-pin/node.exe', 'vendor/rea/package/scripts/rea.mjs',
                         'vendor/craft/mcp/windows-x64/0.1.1/reverse-fusion-craft-mcp.exe',
                         '.venv/' + ('Scripts/python.exe' if os.name == 'nt' else 'bin/python'), 'scripts/mcp-launch.py'):
            file = root / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(b'owned test identity, never executed')
        (root / 'vendor/node/manifest.json').write_text(json.dumps({'entry': 'node-pin/node.exe'}), encoding='utf-8')
        self.write_craft_manifest(root, 'vendor/craft/mcp/windows-x64/0.1.1/reverse-fusion-craft-mcp.exe')
        (root / 'state').mkdir()
        (root / 'state/rea-runtime.json').write_text(json.dumps({
            'schema_version': 1, 'repository_root': str(root),
            'node': str(root / 'vendor/node/node-pin/node.exe'),
        }), encoding='utf-8')
        return root

    def write_craft_manifest(self, root, relative):
        system = {'Windows': 'windows', 'Linux': 'linux', 'Darwin': 'macos'}.get(platform.system(), 'unknown')
        machine = platform.machine().lower()
        architecture = 'x64' if machine in {'amd64', 'x86_64'} else 'arm64' if machine in {'arm64', 'aarch64'} else machine
        manifest = root/'components/craft-mcp/manifest.json'
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({'platforms': {f'{system}-{architecture}': {'local_path': relative}}}), encoding='utf-8')

    def write(self, data):
        self.config.parent.mkdir(parents=True, exist_ok=True)
        self.config.write_bytes(data)

    def test_roundtrip_preserves_unrelated_bytes_and_servers_at_all_eof_styles(self):
        samples = [b'', b'# exact user bytes\r\nmodel = "owned-model"\r\n',
                   b'# no newline\n[mcp_servers.other]\ncommand = "other"',
                   b'\xef\xbb\xbf# BOM and no newline']
        for original in samples:
            with self.subTest(original=original):
                self.write(original)
                result = install_mcp(self.root, self.home)
                self.assertTrue(result['enabled'])
                self.assertTrue(self.config.read_bytes().startswith(original))
                parsed = tomllib.loads(self.config.read_bytes().decode('utf-8-sig'))
                rea = parsed['mcp_servers']['reverse-fusion-rea']
                self.assertEqual(rea['args'], [str(self.root/'scripts/mcp-launch.py'), 'rea'])
                self.assertEqual(rea['env']['REA_MCP_OUTPUT_SCHEMA_PROFILE'], 'compact')
                self.assertEqual(parsed['mcp_servers']['reverse-fusion-craft']['args'],
                                 [str(self.root/'scripts/mcp-launch.py'),'craft'])
                once = self.config.read_bytes()
                self.assertFalse(install_mcp(self.root, self.home)['changed'])
                self.assertEqual(self.config.read_bytes(), once)
                self.assertEqual(inspect_mcp(self.root, self.home)['status'], 'registered')
                remove_mcp(self.root, self.home)
                self.assertEqual(self.config.read_bytes(), original)
                self.assertEqual(remove_mcp(self.root, self.home)['status'], 'not-registered')

    def test_missing_config_is_removed_but_original_empty_config_is_retained(self):
        self.assertFalse(self.config.exists())
        install_mcp(self.root, self.home)
        remove_mcp(self.root, self.home)
        self.assertFalse(self.config.exists())
        self.write(b'')
        install_mcp(self.root, self.home)
        remove_mcp(self.root, self.home)
        self.assertEqual(self.config.read_bytes(), b'')

    def test_update_changes_owned_pointer_and_old_checkout_cannot_remove_it(self):
        original = b'# retained\r\n[mcp_servers.other]\r\ncommand="untouched"'
        self.write(original)
        install_mcp(self.root, self.home)
        moved = self.make_repo('moved checkout')
        install_mcp(moved, self.home)
        updated = self.config.read_bytes()
        self.assertEqual(updated.count(BEGIN), 1)
        self.assertEqual(inspect_mcp(self.root, self.home)['status'], 'other-checkout')
        self.assertEqual(remove_mcp(self.root, self.home)['status'], 'retained')
        self.assertEqual(self.config.read_bytes(), updated)
        remove_mcp(moved, self.home)
        self.assertEqual(self.config.read_bytes(), original)

    def test_unmanaged_conflicts_invalid_toml_and_bad_markers_never_write(self):
        originals = [b'[mcp_servers.reverse-fusion-rea]\ncommand="user-owned"\n',
                     b'not valid TOML', BEGIN+b'\n', END+b'\n'+BEGIN+b'\n',
                     BEGIN+b'\n'+BEGIN+b'\n'+END+b'\n']
        for original in originals:
            with self.subTest(original=original):
                self.write(original)
                with self.assertRaises(ValueError):
                    install_mcp(self.root, self.home)
                self.assertEqual(self.config.read_bytes(), original)

    def test_managed_block_cannot_remove_unrelated_settings_added_inside_it(self):
        install_mcp(self.root, self.home)
        altered = self.config.read_bytes().replace(END, b'[other_private_section]\nkeep="yes"\n'+END)
        self.write(altered)
        with self.assertRaisesRegex(ValueError, 'unrelated'):
            remove_mcp(self.root, self.home)
        with self.assertRaises(ValueError):
            install_mcp(self.root, self.home)
        self.assertEqual(self.config.read_bytes(), altered)

    def test_missing_launcher_does_not_create_config_and_atomic_failure_keeps_user_bytes(self):
        (self.root/'vendor/craft/mcp/windows-x64/0.1.1/reverse-fusion-craft-mcp.exe').unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            install_mcp(self.root, self.home)
        self.assertFalse(self.config.exists())
        self.root = self.make_repo('ready repo')
        original = b'# exact bytes\n'
        self.write(original)
        with patch('reverse_fusion.mcp_adapter.atomic_write', side_effect=OSError('write failure')):
            with self.assertRaises(OSError):
                install_mcp(self.root, self.home)
        self.assertEqual(self.config.read_bytes(), original)

    def test_manifest_versioned_asset_is_required_even_when_legacy_binary_exists(self):
        legacy = self.root/'vendor/craft/mcp/windows-x64/reverse-fusion-craft-mcp.exe'
        legacy.write_bytes(b'obsolete path must not satisfy selected distribution')
        selected = self.root/'vendor/craft/mcp/windows-x64/0.1.1/reverse-fusion-craft-mcp.exe'
        selected.unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            install_mcp(self.root, self.home)
        self.assertFalse(self.config.exists())
        selected.write_bytes(b'inert selected versioned identity')
        self.assertTrue(install_mcp(self.root, self.home)['enabled'])

    def test_manifest_cannot_select_outside_checkout_or_traversal_path(self):
        external = self.base/'outside.exe'
        external.write_bytes(b'owned outside test identity, never executed')
        original = b'# unchanged client config\r\n'
        self.write(original)
        for relative in (str(external), '../outside.exe', 'vendor/../outside.exe'):
            with self.subTest(relative=relative):
                self.write_craft_manifest(self.root, relative)
                with self.assertRaisesRegex(ValueError, 'relative|leaves'):
                    install_mcp(self.root, self.home)
                self.assertEqual(self.config.read_bytes(), original)

    def test_custom_codex_home_controls_only_config_path(self):
        selected = self.base/'custom codex'
        with patch.dict(os.environ, {'CODEX_HOME': str(selected)}):
            self.assertEqual(mcp_paths()['config'], selected/'config.toml')
            self.assertEqual(mcp_paths(self.home)['config'], self.home/'.codex/config.toml')

    def test_selected_compatible_runtime_outside_checkout_is_used_and_missing_runtime_blocks(self):
        external = self.base / 'selected desktop runtime/node.exe'
        external.parent.mkdir()
        external.write_bytes(b'owned external runtime fixture, never executed')
        receipt = self.root/'state/rea-runtime.json'
        value = json.loads(receipt.read_text(encoding='utf-8'))
        value['node'] = str(external)
        receipt.write_text(json.dumps(value), encoding='utf-8')
        install_mcp(self.root, self.home)
        parsed = tomllib.loads(self.config.read_text(encoding='utf-8'))
        self.assertEqual(parsed['mcp_servers']['reverse-fusion-rea']['command'],
                         str(self.root/'.venv'/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')))
        from reverse_fusion.runtime import node_runtime
        self.assertEqual(node_runtime(self.root)[0],str(external))
        self.assertTrue(inspect_mcp(self.root, self.home)['enabled'])
        before = self.config.read_bytes()
        with patch('reverse_fusion.mcp_adapter.node_runtime', return_value=(None, 'path')):
            with self.assertRaisesRegex(ValueError, 'unavailable'):
                install_mcp(self.root, self.home)
        self.assertEqual(self.config.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
