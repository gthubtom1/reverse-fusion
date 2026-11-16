"""Exercise original MCP tools on owned material, without a model or user target."""
import functools
from hashlib import sha256
import http.server
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reverse_fusion.craft_mcp import mcp_binary
from reverse_fusion.mcp_probe import StdioMcp, catalog
from reverse_fusion.mcp_adapter import REA_ENV
from reverse_fusion.provider_runtime import launch_environment
from reverse_fusion.runtime import node_runtime

output = (ROOT / (sys.argv[1] if len(sys.argv)>1 else 'state/mcp-qualification')).resolve()
output.mkdir(parents=True, exist_ok=False)
project = Path(tempfile.mkdtemp(prefix='rf36-mcp-outcome-')).resolve()
if project.is_relative_to(ROOT):
    raise ValueError('Qualification needs an outcome project outside the shared checkout')
case = project/'work/owned-case'
case.mkdir(parents=True)
original = project/'original'
shutil.copytree(ROOT/'fixtures/desk-original',original)
node, _ = node_runtime(ROOT)
commands = {'rea': [node, str(ROOT/'vendor/rea/package/scripts/rea.mjs'), 'mcp'],
            'craft': [str(mcp_binary(ROOT)), '--all-tools', '--deep-mode', '--allow-run', '--state-dir', str(output/'craft')]}
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = http.server.ThreadingHTTPServer(('127.0.0.1',0), functools.partial(Quiet, directory=str(original)))
threading.Thread(target=server.serve_forever, daemon=True).start()
report = {'scope': 'owned fixture real protocol/tools/browser, bound outcome Project and restart evidence; not every provider or target equivalence',
          'outcome_project':str(project),'case_root':str(case),'servers': {}}
environment = {**launch_environment(ROOT),**REA_ENV}
try:
    for name, argv in commands.items():
        with StdioMcp(argv,cwd=ROOT,env=environment,timeout=60) as client:
            identity = client.initialize()
            tools = catalog(client)
            prompts = catalog(client,'prompts/list','prompts')
            if name=='craft' and (len(tools)!=305 or not {'fusion_case_open','fusion_asset_generate'} <= {item['name'] for item in tools}):
                raise ValueError('Expected pinned 303 original Craft tools plus fusion_case_open')
            calls = ([('binary_session',{}),('analyze_javascript_application',{
                'input_path':str(original), 'detail':'summary',
                'analysis_timeout_ms':15000,'max_heap_mb':256})] if name=='rea' else [
                ('fusion_case_open',{'project_root':str(project),'case_root':str(case)}),
                ('core_target_open',{'path':str(original/'core.mjs')}),
                ('js_app_map',{'input_path':str(original),'max_files':20,'limit':10}),
                ('engines_list',{}),('web_site_open',{'url':f'http://127.0.0.1:{server.server_port}',
                    'headless':True,'settle_ms':100,'timeout_secs':20}),
                ('web_site_capture',{'output_directory':str(case/'capture'),'widths':[1100,390],'timeout_secs':30}),
                ('web_site_close',{})])
            observed=[]
            for tool,arguments in calls:
                result = client.request('tools/call',{'name':tool,'arguments':arguments})
                observed.append({'tool':tool,'arguments':arguments,'result':result})
                (output/f'{name}-calls.json').write_text(json.dumps(observed,ensure_ascii=True,indent=2)+'\n',encoding='ascii')
                if result.get('isError'): raise ValueError(f'{name}: {tool} failed; retained raw response')
                if name=='craft' and tool=='engines_list':
                    if result['structuredContent']['result']['deep_mode']['enabled'] is not True:
                        raise ValueError('Craft did not report its effective process Deep mode')
                if name=='craft' and tool=='js_app_map':
                    evidence_id=result['structuredContent']['id']
                    if not evidence_id.startswith('ev_'):raise ValueError('Original Craft Evidence identity missing')
            manifest = {'initialize':identity,'tools':tools,'prompts':prompts}
            (output/f'{name}-catalog.json').write_text(json.dumps(manifest,ensure_ascii=True,indent=2)+'\n',encoding='ascii')
        if client.cleanup['status']!=('verified' if os.name=='nt' else 'observed'):
            raise ValueError(f'{name}: owned process cleanup is incomplete')
        report['servers'][name]={'server':identity['serverInfo'],'tools':len(tools),'prompts':len(prompts),
            'binary_sha256':sha256(Path(argv[0]).read_bytes()).hexdigest(),
            'called':[call['tool'] for call in observed],'cleanup':client.cleanup}
        if name=='craft':
            with StdioMcp(argv,cwd=ROOT,env=environment,timeout=60) as client:
                client.initialize()
                reopened=[]
                for tool,arguments in [('fusion_case_open',{'project_root':str(project),'case_root':str(case)}),
                    ('core_evidence_show',{'evidence_id':evidence_id}),('core_session_show',{})]:
                    result=client.request('tools/call',{'name':tool,'arguments':arguments})
                    reopened.append({'tool':tool,'arguments':arguments,'result':result})
                    (output/'craft-restart-calls.json').write_text(json.dumps(reopened,ensure_ascii=True,indent=2)+'\n',encoding='ascii')
                    if result.get('isError'):raise ValueError(f'craft restart: {tool} failed')
                    if tool=='core_evidence_show' and evidence_id not in json.dumps(result):
                        raise ValueError('Original Craft Evidence did not survive restart and binding')
                    if tool=='core_session_show' and result['structuredContent']['result']['evidence_records']<1:
                        raise ValueError('Bound original Project did not restore its evidence ledger')
            if client.cleanup['status']!=('verified' if os.name=='nt' else 'observed'):
                raise ValueError('craft restart: owned process cleanup is incomplete')
            report['servers'][name].update({'evidence_id':evidence_id,'restart_evidence_restored':True,
                                            'restart_cleanup':client.cleanup,'capture_directory':str(case/'capture')})
    report['status']='pass'
except BaseException as error:
    report['status']='fail'
    report['error']=str(error)
    raise
finally:
    server.shutdown();server.server_close()
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=True,indent=2)+'\n',encoding='ascii')
print(json.dumps(report,ensure_ascii=True,indent=2))
