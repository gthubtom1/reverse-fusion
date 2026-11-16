"""Exercise original MCP tools on owned material, without a model or user target."""
import functools
from hashlib import sha256
import http.server
import json
import os
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reverse_fusion.craft_mcp import mcp_binary
from reverse_fusion.mcp_probe import StdioMcp, catalog
from reverse_fusion.runtime import node_runtime

output = (ROOT / (sys.argv[1] if len(sys.argv)>1 else 'state/mcp-qualification')).resolve()
output.mkdir(parents=True, exist_ok=False)
node, _ = node_runtime(ROOT)
commands = {'rea': [node, str(ROOT/'vendor/rea/package/scripts/rea.mjs'), 'mcp'],
            'craft': [str(mcp_binary(ROOT)), '--all-tools', '--deep-mode', '--allow-run', '--state-dir', str(output/'craft')]}
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = http.server.ThreadingHTTPServer(('127.0.0.1',0), functools.partial(Quiet, directory=str(ROOT/'fixtures/desk-original')))
threading.Thread(target=server.serve_forever, daemon=True).start()
report = {'scope': 'owned fixture real protocol/tools/browser use; not every provider or target equivalence', 'servers': {}}
try:
    for name, argv in commands.items():
        with StdioMcp(argv,cwd=ROOT,env={**os.environ,'REA_MCP_OUTPUT_SCHEMA_PROFILE':'compact'},timeout=60) as client:
            identity = client.initialize()
            tools = catalog(client)
            prompts = catalog(client,'prompts/list','prompts')
            calls = ([('binary_session',{}),('analyze_javascript_application',{
                'input_path':str(ROOT/'fixtures/desk-original'), 'detail':'summary',
                'analysis_timeout_ms':15000,'max_heap_mb':256})] if name=='rea' else [
                ('core_target_open',{'path':str(ROOT/'fixtures/desk-original/core.mjs')}),
                ('js_app_map',{'input_path':str(ROOT/'fixtures/desk-original'),'max_files':20,'limit':10}),
                ('engines_list',{}),('web_site_open',{'url':f'http://127.0.0.1:{server.server_port}',
                    'headless':True,'settle_ms':100,'timeout_secs':20}),
                ('web_site_capture',{'output_directory':str(output/'capture'),'widths':[1100,390],'timeout_secs':30}),
                ('web_site_close',{})])
            observed=[]
            for tool,arguments in calls:
                result = client.request('tools/call',{'name':tool,'arguments':arguments})
                observed.append({'tool':tool,'arguments':arguments,'result':result})
                (output/f'{name}-calls.json').write_text(json.dumps(observed,ensure_ascii=True,indent=2)+'\n',encoding='ascii')
                if result.get('isError'): raise ValueError(f'{name}: {tool} failed; retained raw response')
            manifest = {'initialize':identity,'tools':tools,'prompts':prompts}
            (output/f'{name}-catalog.json').write_text(json.dumps(manifest,ensure_ascii=True,indent=2)+'\n',encoding='ascii')
            report['servers'][name]={'server':identity['serverInfo'],'tools':len(tools),'prompts':len(prompts),
                'binary_sha256':sha256(Path(argv[0]).read_bytes()).hexdigest(),
                'called':[call['tool'] for call in observed]}
    report['status']='pass'
finally:
    server.shutdown();server.server_close()
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=True,indent=2)+'\n',encoding='ascii')
print(json.dumps(report,ensure_ascii=True,indent=2))
