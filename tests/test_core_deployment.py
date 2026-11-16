from argparse import Namespace
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from reverse_fusion.component_status import core_deployment
from reverse_fusion.craft_native import native_binary
from reverse_fusion import cli


class CoreDeploymentTests(unittest.TestCase):
    def test_published_binary_also_requires_matching_adapter_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            sources = ['components/craft-native/src/main.rs', 'components/craft-native/Cargo.toml',
                       'components/craft-native/Cargo.lock']
            for name in sources:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'synthetic source, never executed')
            binary = root / 'driver.exe'
            binary.write_bytes(b'synthetic binary, never executed')
            manifest = {'platforms': {'windows-x64': {'local_path': 'driver.exe',
                         'binary_sha256': sha256(binary.read_bytes()).hexdigest()}}, 'patches': [],
                        'adapter_source_sha256': {n: sha256((root / n).read_bytes()).hexdigest() for n in sources}}
            (root / 'components/craft-native/manifest.json').write_text(json.dumps(manifest))
            with patch('reverse_fusion.craft_native.platform.system', return_value='Windows'), \
                    patch('reverse_fusion.craft_native.platform.machine', return_value='AMD64'):
                self.assertEqual(native_binary(root), binary)
                (root / sources[0]).write_bytes(b'adapter was edited without a rebuild')
                with self.assertRaisesRegex(ValueError, 'source-bound'):
                    native_binary(root)

    def test_missing_real_component_blocks_install_before_global_writes(self):
        components = {'rea': {'status': 'present-unverified', 'node_engine_status': 'satisfied'},
                      'spec': {'cli_status': 'installed'}, 'craft': {'native_backend': 'not-installed', 'mcp_backend': 'installed-identity-verified'}}
        self.assertEqual(core_deployment(components)['missing'], ['craft-native'])
        args = Namespace(apply=True, format='json')
        with patch.object(cli, 'check_contracts', return_value={'status': 'pass'}), \
                patch.object(cli, 'component_status', return_value=components), \
                patch.object(cli, 'install_global_adapter') as adapter, patch.object(cli, '_print'):
            self.assertEqual(cli.cmd_install(args), 2)
            adapter.assert_not_called()

    def test_source_build_is_bound_to_checkout_binary_and_all_adapter_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            manifest = root / 'components/craft-native/manifest.json'
            manifest.parent.mkdir(parents=True)
            names = ['components/craft-native/src/main.rs', 'components/craft-native/Cargo.toml',
                     'components/craft-native/Cargo.lock', 'components/craft-native/patches/windows.patch']
            for name in names:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b'synthetic source identity; never compiled or run')
            binary = root / 'vendor/craft/driver.exe'
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b'synthetic binary identity; never executed')
            manifest.write_text(json.dumps({'platforms': {'windows-x64': {'local_path': 'vendor/craft/driver.exe',
                                'binary_sha256': '0' * 64}}, 'patches': [{'path': names[-1]}]}))
            names.append('components/craft-native/manifest.json')
            receipt = {'schema_version': 1, 'distribution': 'source-build', 'repository_root': str(root),
                       'binary_sha256': sha256(binary.read_bytes()).hexdigest(),
                       'source_inputs': {name: sha256((root / name).read_bytes()).hexdigest() for name in names}}
            state = root / 'state/craft-runtime.json'
            state.parent.mkdir()
            state.write_text(json.dumps(receipt))
            with patch('reverse_fusion.craft_native.platform.system', return_value='Windows'), \
                    patch('reverse_fusion.craft_native.platform.machine', return_value='AMD64'):
                self.assertEqual(native_binary(root), binary)
                receipt['repository_root'] = str(root / 'other')
                state.write_text(json.dumps(receipt))
                with self.assertRaisesRegex(ValueError, 'source-bound'):
                    native_binary(root)
                receipt['repository_root'] = str(root)
                state.write_text(json.dumps(receipt))
                (root / names[0]).write_bytes(b'changed source')
                with self.assertRaisesRegex(ValueError, 'source-bound'):
                    native_binary(root)
