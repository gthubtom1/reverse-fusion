import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess
from hashlib import sha256

from reverse_fusion.component_status import component_status
from reverse_fusion.runtime import node_runtime


class ComponentStatusTests(unittest.TestCase):
    def test_repository_runtime_survives_new_process_environment_and_rejects_copied_receipt(self):
        with tempfile.TemporaryDirectory(prefix='rf runtime ') as directory:
            root = Path(directory).resolve()
            (root / 'state').mkdir()
            executable = root / 'bundled node.exe'
            executable.write_bytes(b'synthetic executable path; never run')
            receipt_path = root / 'state/rea-runtime.json'
            receipt = {'schema_version': 1, 'repository_root': str(root), 'node': str(executable)}
            receipt_path.write_text(json.dumps(receipt), encoding='utf-8-sig')
            with patch.dict('os.environ', {}, clear=True), \
                 patch('reverse_fusion.runtime.shutil.which', return_value='path-node'):
                self.assertEqual(node_runtime(root), (str(executable), 'repository-receipt'))
                with patch.dict('os.environ', {'REVERSE_FUSION_NODE': 'explicit-node'}):
                    self.assertEqual(node_runtime(root), ('explicit-node', 'environment'))
                receipt['repository_root'] = str(root / 'other-checkout')
                receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
                self.assertEqual(node_runtime(root), ('path-node', 'path'))
                receipt['repository_root'] = str(root)
                receipt['node'] = str(root / 'removed-node.exe')
                receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
                self.assertEqual(node_runtime(root), ('path-node', 'path'))
                receipt_path.write_text('invalid json', encoding='utf-8')
                self.assertEqual(node_runtime(root), ('path-node', 'path'))

    def test_pin_does_not_masquerade_as_installed_or_healthy_rea(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vendor = root / 'vendor/rea'
            vendor.mkdir(parents=True)
            pin = {'package': 'rea-agents', 'version': '6.9.0',
                   'entry': 'package/scripts/rea.mjs', 'node_engine': '^22.23.4 || ^24.22.1 || >=26.12.1'}
            (vendor / 'manifest.json').write_text(json.dumps(pin), encoding='utf-8')
            status = component_status(root)
            self.assertEqual(status['rea']['status'], 'not-installed')
            self.assertEqual(status['rea']['handshake'], 'unverified')
            self.assertEqual(status['craft']['native_backend'], 'not-installed')
            self.assertEqual(status['builder']['status'], 'not-installed')
            with patch('reverse_fusion.component_status._craft_status', return_value={'native_backend': 'installed-identity-verified'}):
                self.assertEqual(component_status(root)['builder']['status'], 'installed-identity-verified')
            package = vendor / 'package'
            (package / 'scripts').mkdir(parents=True)
            (package / 'scripts/rea.mjs').write_text('// synthetic presence fixture', encoding='utf-8')
            identity = {'name': 'rea-agents', 'version': '6.9.0', 'engines': {'node': pin['node_engine']}}
            (package / 'package.json').write_text(json.dumps(identity), encoding='utf-8')
            self.assertEqual(component_status(root)['rea']['status'], 'methods-incomplete')
            method = package / 'skills/reverse-engineer-anything/SKILL.md'
            method.parent.mkdir(parents=True)
            method.write_bytes(b'synthetic original method identity')
            pin['method_files_sha256']={method.relative_to(vendor).as_posix():sha256(method.read_bytes()).hexdigest()}
            (vendor / 'manifest.json').write_text(json.dumps(pin), encoding='utf-8')
            self.assertEqual(component_status(root)['rea']['status'], 'present-unverified')
            method.write_bytes(b'changed method from a different package version')
            self.assertEqual(component_status(root)['rea']['status'], 'methods-incomplete')
            method.write_bytes(b'synthetic original method identity')
            identity['version'] = '0.0.0'
            (package / 'package.json').write_text(json.dumps(identity), encoding='utf-8')
            self.assertEqual(component_status(root)['rea']['status'], 'identity-mismatch')
            with patch('reverse_fusion.component_status.subprocess.run', return_value=
                       subprocess.CompletedProcess([], 0, stdout='v24.20.0\n')), \
                 patch.dict('os.environ', {'REVERSE_FUSION_NODE': 'fixture-node'}):
                self.assertEqual(component_status(root)['rea']['node_engine_status'], 'blocked')


if __name__ == '__main__':
    unittest.main()
