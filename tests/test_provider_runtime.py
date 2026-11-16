import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from hashlib import sha256

from reverse_fusion.provider_runtime import discover_providers,provider_environment,provider_status,ALL_KEYS


class ProviderRuntimeTests(unittest.TestCase):
    def environment(self):
        return patch.dict(os.environ,{k:v for k,v in os.environ.items() if k not in ALL_KEYS},clear=True)

    def test_saved_tool_paths_survive_app_environment_without_importing_secrets(self):
        with tempfile.TemporaryDirectory() as directory,self.environment(),patch('shutil.which',return_value=None):
            root=Path(directory);ghidra=root/'tools/ghidra';(ghidra/'Ghidra').mkdir(parents=True)
            (ghidra/'Ghidra/application.properties').write_text('application.version=12.1.3')
            java=root/'tools/jdk';(java/'bin').mkdir(parents=True)
            (java/'bin'/('java.exe' if os.name=='nt' else 'java')).write_bytes(b'inert tool, not run')
            with patch.dict(os.environ,{'GHIDRA_INSTALL_DIR':str(ghidra),'JAVA_HOME':str(java),'API_KEY':'never-persist-this'}):
                report=discover_providers(root,persist=True)
            restored=provider_environment(root)
            self.assertEqual(restored['GHIDRA_INSTALL_DIR'],str(ghidra.resolve()))
            self.assertEqual(restored['JAVA_HOME'],str(java.resolve()))
            self.assertNotIn('API_KEY',report['paths'])
            self.assertNotIn('never-persist-this',(root/'state/provider-runtime.json').read_text())

    def test_deleted_provider_only_becomes_unavailable_and_refresh_retains_reason(self):
        with tempfile.TemporaryDirectory() as directory,self.environment(),patch('shutil.which',return_value=None):
            root=Path(directory);tool=root/'adb.exe';tool.write_bytes(b'inert')
            discover_providers(root,persist=True,overrides={'REA_ADB_PATH':str(tool)})
            tool.unlink()
            self.assertNotIn('REA_ADB_PATH',provider_environment(root))
            self.assertIn('REA_ADB_PATH',provider_status(root)['unavailable'])
            refreshed=discover_providers(root,persist=True)
            self.assertIn('REA_ADB_PATH',refreshed['removed_unavailable_paths'])

    def test_shared_craft_paths_follow_source_refresh_but_independent_selection_survives(self):
        with tempfile.TemporaryDirectory() as directory,self.environment(),patch('shutil.which',return_value=None):
            root=Path(directory)
            tools=[root/name for name in ('old-adb.exe','new-adb.exe','own-adb.exe')]
            for tool in tools:tool.write_bytes(b'inert tool, never executed')
            craft_key='REVERSE_FUSION_CRAFT_TOOL_ADB'
            first=discover_providers(root,persist=True,overrides={'REA_ADB_PATH':str(tools[0])})
            self.assertEqual(first['sources'][craft_key],'shared-provider-path')
            shared=discover_providers(root,persist=True,overrides={'REA_ADB_PATH':str(tools[1])})
            self.assertEqual(shared['paths'][craft_key],str(tools[1].resolve()))
            discover_providers(root,persist=True,overrides={craft_key:str(tools[2])})
            independent=discover_providers(root,persist=True,overrides={'REA_ADB_PATH':str(tools[0])})
            self.assertEqual(independent['paths'][craft_key],str(tools[2].resolve()))
            self.assertEqual(independent['sources'][craft_key],'explicit-tool-path')

    def test_only_verified_repository_jadx_is_selected_and_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as directory,self.environment(),patch('shutil.which',return_value=None):
            root=Path(directory);folder=root/'vendor/jadx-headless-mcp/0.7.1';folder.mkdir(parents=True)
            jar=folder/'owned.jar';jar.write_bytes(b'inert jar')
            (folder/'manifest.json').write_text(json.dumps({'artifact':'owned.jar','sha256':sha256(jar.read_bytes()).hexdigest()}))
            discovered=discover_providers(root,persist=True)
            self.assertEqual(discovered['paths']['REA_JADX_MCP_JAR'],str(jar.resolve()))
            jar.write_bytes(b'tampered')
            self.assertNotIn('REA_JADX_MCP_JAR',provider_environment(root))
            self.assertIn('integrity',provider_status(root)['unavailable']['REA_JADX_MCP_JAR'])

    def test_receipt_from_another_checkout_and_unknown_or_relative_paths_fail(self):
        with tempfile.TemporaryDirectory() as directory,self.environment(),patch('shutil.which',return_value=None):
            root=Path(directory)
            with self.assertRaises(ValueError):discover_providers(root,persist=True,overrides={'API_TOKEN':'secret'})
            with self.assertRaises(ValueError):discover_providers(root,persist=True,overrides={'REA_ADB_PATH':'relative.exe'})
            (root/'state').mkdir();(root/'state/provider-runtime.json').write_text(json.dumps({
                'schema_version':1,'repository_root':str(root/'other'),'paths':{}}))
            with self.assertRaises(ValueError):provider_environment(root)

    def test_nonobject_saved_receipt_roots_are_controlled_value_errors(self):
        with tempfile.TemporaryDirectory() as directory,self.environment(),patch('shutil.which',return_value=None):
            root=Path(directory);(root/'state').mkdir()
            receipt=root/'state/provider-runtime.json'
            for value in ([],None,'wrong JSON root'):
                with self.subTest(value=value):
                    receipt.write_text(json.dumps(value),encoding='utf-8')
                    original=receipt.read_bytes()
                    for operation in (provider_status,provider_environment,discover_providers):
                        with self.subTest(operation=operation.__name__):
                            with self.assertRaisesRegex(ValueError,'Provider runtime receipt is not bound'):
                                operation(root)
                    self.assertEqual(receipt.read_bytes(),original)
