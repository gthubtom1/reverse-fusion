import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess

from reverse_fusion.component_status import component_status


class ComponentStatusTests(unittest.TestCase):
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
            self.assertEqual(status['craft']['native_backend'], 'unsupported')
            package = vendor / 'package'
            (package / 'scripts').mkdir(parents=True)
            (package / 'scripts/rea.mjs').write_text('// synthetic presence fixture', encoding='utf-8')
            identity = {'name': 'rea-agents', 'version': '6.9.0', 'engines': {'node': pin['node_engine']}}
            (package / 'package.json').write_text(json.dumps(identity), encoding='utf-8')
            self.assertEqual(component_status(root)['rea']['status'], 'present-unverified')
            identity['version'] = '0.0.0'
            (package / 'package.json').write_text(json.dumps(identity), encoding='utf-8')
            self.assertEqual(component_status(root)['rea']['status'], 'identity-mismatch')
            with patch('reverse_fusion.component_status.subprocess.run', return_value=
                       subprocess.CompletedProcess([], 0, stdout='v24.20.0\n')), \
                 patch.dict('os.environ', {'REVERSE_FUSION_NODE': 'fixture-node'}):
                self.assertEqual(component_status(root)['rea']['node_engine_status'], 'blocked')


if __name__ == '__main__':
    unittest.main()
