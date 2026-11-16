"""Actual pinned protocol and tool checks on owned local material."""
from hashlib import sha256
from contextlib import redirect_stdout
import ctypes
import io
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from reverse_fusion.craft_mcp import mcp_binary
from reverse_fusion.mcp_probe import StdioMcp, catalog, connection_status
from reverse_fusion import cli

ROOT=Path(__file__).resolve().parents[1]


class McpProtocolTests(unittest.TestCase):
    def test_actual_craft_assets_original_producer_and_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'qualification'
            run=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/qualify-craft-assets.py'),
                                '--output',str(output)],cwd=ROOT,capture_output=True,timeout=60)
            self.assertEqual(run.returncode,0,run.stderr.decode('utf-8',errors='replace'))
            report=json.loads((output/'report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'],'pass')
            self.assertTrue(report['glb_generated'] and report['credential_redacted']
                            and report['budget_refused_before_network'] and report['formal_candidate_unchanged'])

    def test_mcp_check_nonpassing_final_status_returns_nonzero(self):
        with patch('reverse_fusion.mcp_probe.probe_registered') as probe, \
                patch('reverse_fusion.mcp_probe.connection_status', return_value={'status': 'fail', 'reason': 'changed after probe'}), \
                redirect_stdout(io.StringIO()) as output:
            self.assertEqual(cli.main(['mcp-check']), 2)
        probe.assert_called_once()
        self.assertEqual(json.loads(output.getvalue())['status'], 'fail')

    def test_owned_stdio_close_terminates_long_descendant_even_after_root_exit(self):
        server_source = '''import json, pathlib, subprocess, sys, time
child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])
pathlib.Path(sys.argv[1]).write_text(str(child.pid))
if sys.argv[2] == 'early':
    raise SystemExit(0)
for line in sys.stdin:
    request = json.loads(line)
    if 'id' in request:
        print(json.dumps({'jsonrpc':'2.0','id':request['id'],'result':{'ready':True}}), flush=True)
if sys.argv[2] == 'stuck':
    time.sleep(120)
'''
        for mode in ('normal', 'early', 'stuck'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                server = root/'server.py'
                server.write_text(server_source, encoding='utf-8')
                pidfile = root/'child.pid'
                client = StdioMcp([sys.executable, str(server), str(pidfile), mode], cwd=root, timeout=5)
                handle = None
                try:
                    deadline = time.monotonic()+5
                    while not pidfile.is_file() and time.monotonic()<deadline:
                        time.sleep(.01)
                    self.assertTrue(pidfile.is_file())
                    pid = int(pidfile.read_text())
                    if os.name == 'nt':
                        from ctypes import wintypes as w
                        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
                        kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
                        kernel.OpenProcess.restype = w.HANDLE
                        kernel.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
                        kernel.CloseHandle.argtypes = [w.HANDLE]
                        handle = kernel.OpenProcess(0x100000, False, pid)
                        self.assertTrue(handle)
                        self.assertEqual(kernel.WaitForSingleObject(handle, 0), 258)
                    if mode != 'early':
                        self.assertEqual(client.request('owned/ping'), {'ready': True})
                    else:
                        client.process.wait(timeout=5)
                    client.close()
                    if os.name == 'nt':
                        self.assertEqual(client.cleanup['status'], 'verified')
                        self.assertEqual(kernel.WaitForSingleObject(handle, 3000), 0)
                    else:
                        self.assertEqual(client.cleanup['status'], 'observed')
                    self.assertTrue(all(not thread.is_alive() for thread in client.threads))
                    self.assertIsNotNone(client.process.poll())
                finally:
                    client.close()
                    if handle:
                        kernel.CloseHandle(handle)

    def test_actual_craft_deep_catalog_and_original_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory).resolve()
            project = temporary/'outcome-project'
            case = project/'work/owned-case'
            case.mkdir(parents=True)
            self.assertFalse(project.is_relative_to(ROOT))
            argv = [str(mcp_binary(ROOT)), '--all-tools', '--deep-mode',
                    '--state-dir', str(temporary/'server-state')]
            with StdioMcp(argv,cwd=ROOT) as client:
                identity=client.initialize()
                self.assertEqual(identity['serverInfo']['name'],'craft-anything')
                names={tool['name'] for tool in catalog(client)}
                self.assertEqual(len(names), 305)
                self.assertTrue({'fusion_case_open','fusion_asset_generate','core_target_open','js_app_map','adb_devices_find',
                                 'native_functions_list','web_site_open'} <= names,names)
                unbound=client.request('tools/call',{'name':'js_app_map','arguments':{'input_path':str(ROOT/'fixtures/desk-original')}})
                self.assertTrue(unbound.get('isError'),unbound)
                self.assertIn('fusion_case_open',unbound['content'][0]['text'])
                modes=client.request('tools/call',{'name':'engines_list','arguments':{}})
                self.assertFalse(modes.get('isError'),modes)
                effective=modes['structuredContent']['result']['deep_mode']
                self.assertIs(effective['enabled'],True)
                bound=client.request('tools/call',{'name':'fusion_case_open','arguments':{
                    'project_root':str(project),'case_root':str(case)}})
                self.assertFalse(bound.get('isError'),bound)
                target=client.request('tools/call',{'name':'core_target_open','arguments':{
                    'path':str(ROOT/'fixtures/desk-original/core.mjs')}})
                self.assertFalse(target.get('isError'),target)
                result=client.request('tools/call',{'name':'js_app_map','arguments':{'input_path':str(ROOT/'fixtures/desk-original')}})
                self.assertFalse(result.get('isError'),result)
                evidence=result['structuredContent']
                self.assertEqual(evidence['operation'],'js_app_map')
                self.assertTrue(evidence['id'].startswith('ev_'))
                # Without the explicit host-consent flag execution still refuses.
                denied=client.request('tools/call',{'name':'web_site_open','arguments':{'url':'http://127.0.0.1:1'}})
                self.assertTrue(denied['isError'])
                self.assertIn('consent_required',denied['content'][0]['text'])
            self.assertEqual(client.cleanup['status'],'verified' if os.name=='nt' else 'observed')
            self.assertTrue((case/'craft-analysis.cany/fusion-binding.json').is_file())
            with StdioMcp(argv,cwd=ROOT) as client:
                client.initialize()
                rebound=client.request('tools/call',{'name':'fusion_case_open','arguments':{
                    'project_root':str(project),'case_root':str(case)}})
                self.assertFalse(rebound.get('isError'),rebound)
                restored=client.request('tools/call',{'name':'core_evidence_show','arguments':{
                    'evidence_id':evidence['id']}})
                self.assertFalse(restored.get('isError'),restored)
                self.assertIn(evidence['id'],json.dumps(restored))
                session=client.request('tools/call',{'name':'core_session_show','arguments':{}})
                self.assertGreaterEqual(session['structuredContent']['result']['evidence_records'],1)
            self.assertEqual(client.cleanup['status'],'verified' if os.name=='nt' else 'observed')

    def test_mcp_status_rejects_stale_binary_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'state').mkdir()
            binary=root/'fake.exe';binary.write_bytes(b'inert, never executed')
            entries={name:{'command':str(binary)} for name in ['reverse-fusion-rea','reverse-fusion-craft']}
            config=root/'config.toml'
            config.write_text('\n'.join(f'[mcp_servers.{name}]\ncommand = {json.dumps(str(binary))}' for name in entries))
            saved={'status':'pass','repository':str(root.resolve()),'servers':[{'server':name,'registration':entry,'binary_sha256':'0'*64,
                'cleanup':{'status':'verified' if os.name=='nt' else 'observed'}} for name,entry in entries.items()]}
            (root/'state/mcp-runtime.json').write_text(json.dumps(saved))
            with patch('reverse_fusion.mcp_adapter.inspect_mcp',return_value={'enabled':True,'config':str(config)}):
                self.assertEqual(connection_status(root)['status'],'fail')

    def test_old_root_only_protocol_observation_does_not_claim_owned_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'state').mkdir()
            binary=root/'fake.exe';binary.write_bytes(b'inert, never executed')
            entries={name:{'command':str(binary)} for name in ['reverse-fusion-rea','reverse-fusion-craft']}
            config=root/'config.toml'
            config.write_text('\n'.join(f'[mcp_servers.{name}]\ncommand = {json.dumps(str(binary))}' for name in entries))
            saved={'status':'pass','repository':str(root.resolve()),'servers':[
                {'server':name,'registration':entry,'binary_sha256':sha256(binary.read_bytes()).hexdigest()}
                for name,entry in entries.items()]}
            (root/'state/mcp-runtime.json').write_text(json.dumps(saved))
            with patch('reverse_fusion.mcp_adapter.inspect_mcp',return_value={'enabled':True,'config':str(config)}):
                result=connection_status(root)
                self.assertEqual(result['status'],'fail')
                self.assertIn('cleanup',result['reason'])

    def test_missing_full_mcp_is_not_complete_core_deployment(self):
        from reverse_fusion.component_status import core_deployment
        components={'rea':{'status':'present-unverified','node_engine_status':'satisfied'},
                    'spec':{'cli_status':'installed'},'craft':{'native_backend':'installed-identity-verified'}}
        self.assertEqual(core_deployment(components)['missing'],['craft-mcp'])

    def test_provider_settings_survive_mcp_restart_in_owned_state_only(self):
        with tempfile.TemporaryDirectory() as directory:
            state=Path(directory)
            argv=[str(mcp_binary(ROOT)), '--all-tools', '--deep-mode', '--state-dir', str(state)]
            with StdioMcp(argv,cwd=ROOT) as client:
                client.initialize()
                result=client.request('tools/call',{'name':'settings_set','arguments':{
                    'key':'engines.tools.jadx','value':'C:/owned-test-provider/jadx.exe'}})
                self.assertFalse(result.get('isError'),result)
            self.assertTrue((state/'config.toml').is_file())
            with StdioMcp(argv,cwd=ROOT) as client:
                client.initialize()
                restored=client.request('tools/call',{'name':'settings_show','arguments':{}})
                self.assertIn('C:/owned-test-provider/jadx.exe',json.dumps(restored))
                self.assertIn(str(state/'engines').replace('\\','/'),json.dumps(restored).replace('\\\\','/'))
