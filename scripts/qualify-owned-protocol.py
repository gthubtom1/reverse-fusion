"""Finite state/error/dependency comparison for an owned protocol fixture."""
from pathlib import Path
import json
import shutil
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import urllib.request
import urllib.error
from datetime import datetime, timezone
import time
import re

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from reverse_fusion.differential import compare_processes
from reverse_fusion.owned_process import run_owned
from reverse_fusion.rea_runner import run_rea

run_name=sys.argv[1] if len(sys.argv)>1 else 'rf33-owned-protocol'
if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',run_name):raise SystemExit('Use a plain new run directory name')
project=root/'state'/run_name
if project.exists():raise SystemExit('Preserve old protocol qualification and choose a new run')
project.mkdir()
for side in ('original','candidate'):
    (project/side).mkdir()
    shutil.copyfile(root/f'fixtures/owned-protocol/{side}.py',project/side/'handler.py')
login={'op':'login','device':'owned-device','key':'owned-test-key','now':100}
cases=[
    ('offline-independent-local', [{'op':'login','service_available':False},{'op':'local_sum','values':[2,-3,7]},{'op':'list','token':'owned-session','now':101}]),
    ('denied-device',[{**login,'device':'wrong'},{'op':'put','token':'owned-session','now':101,'value':'must not write'}]),
    ('expiry-and-local',[login,{'op':'put','token':'owned-session','now':101,'value':' 文档 '},{'op':'list','token':'owned-session','now':129},{'op':'list','token':'owned-session','now':130},{'op':'local_sum','values':[1,2,3]}]),
    ('cancellation-and-close',[login,{'op':'cancel','token':'owned-session','now':101},{'op':'list','token':'owned-session','now':101},{'op':'logout'},{'op':'list','token':'owned-session','now':101}]),
    ('errors',[None,{},[],{'op':'local_sum','values':[True]},{'op':'unknown'}])]
plan={'version':1,'scope':'owned line protocol auth/device/expiry/offline/cancel/error states, no external service',
      'original':{'argv':[sys.executable,'handler.py'],'cwd':'original','sources':['original/handler.py']},
      'candidate':{'argv':[sys.executable,'handler.py'],'cwd':'candidate','sources':['candidate/handler.py']},
      'cases':[{'id':name,'stdin':''.join(json.dumps(item,ensure_ascii=True)+'\n' for item in messages)} for name,messages in cases],
      'timeout_seconds':3}
(project/'plan.json').write_text(json.dumps(plan),encoding='utf-8')
correct=compare_processes(project,'plan.json','correct')
candidate=project/'candidate/handler.py'
candidate.write_text(candidate.read_text().replace("return {'error': 'service-unavailable'}","return {'closed': True}"),encoding='utf-8')
wrong=compare_processes(project,'plan.json','wrong')
report={'scope':'owned protocol finite dependency/control-flow qualification, not a third-party license/server claim',
        'cases':len(cases),'positive':correct['status'],'wrong_dependency_response':wrong['status'],
        'local_work_after_service_failure':'observed in offline-independent-local and expiry-and-local cases',
        'unknown_services':'not defaulted to success; explicit error retained',
        'status':'pass' if correct['status']=='pass' and wrong['status']=='fail' else 'fail'}
# Retain actual localhost HTTP observations and ask official REA to inspect them.
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
        data=self.rfile.read(int(self.headers.get('Content-Length','0')))
        try:
            request=json.loads(data)
            if self.path!='/trace':
                status,body=404,b'{"error":"not-found"}'
            else:
                trace=request['trace']
                if not isinstance(trace,list):raise ValueError('trace')
                run=run_owned([sys.executable,'handler.py'],cwd=project/'original',stdin=(''.join(json.dumps(x)+'\n' for x in trace)).encode(),timeout=3)
                status,body=200,json.dumps([json.loads(line) for line in run['stdout'].splitlines()]).encode()
        except (ValueError,KeyError,TypeError):status,body=400,b'{"error":"malformed"}'
        self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
entries=[]
try:
    for suffix,payload in [('/trace',json.dumps({'trace':cases[0][1]}).encode()),('/trace',b'{damaged'),('/missing',b'{}')]:
        url=f'http://127.0.0.1:{server.server_port}{suffix}';started=time.perf_counter()
        req=urllib.request.Request(url,data=payload,headers={'Content-Type':'application/json'})
        try:response=urllib.request.urlopen(req,timeout=5)
        except urllib.error.HTTPError as exc:response=exc
        body=response.read();elapsed=(time.perf_counter()-started)*1000
        entries.append({'startedDateTime':datetime.now(timezone.utc).isoformat(),'time':elapsed,
            'request':{'method':'POST','url':url,'httpVersion':'HTTP/1.1','headers':[{'name':'Content-Type','value':'application/json'}],
                       'queryString':[],'cookies':[],'headersSize':-1,'bodySize':len(payload),'postData':{'mimeType':'application/json','text':payload.decode()}},
            'response':{'status':response.code,'statusText':response.reason,'httpVersion':'HTTP/1.1','headers':[],
                        'cookies':[],'content':{'size':len(body),'mimeType':'application/json','text':body.decode()},'redirectURL':'','headersSize':-1,'bodySize':len(body)},
            'cache':{},'timings':{'send':0,'wait':elapsed,'receive':0}})
finally:
    server.shutdown();server.server_close();thread.join(timeout=3)
(project/'capture.har').write_text(json.dumps({'log':{'version':'1.2','creator':{'name':'Reverse Fusion owned protocol qualifier','version':'1'},'entries':entries}}),encoding='utf-8')
(project/'rea-args.json').write_text(json.dumps(['capture.har','har','--format','json','--full-output']),encoding='utf-8')
rea=run_rea(root,project,operation='inspect-web-network-capture',arguments='rea-args.json',output='rea-capture',timeout=20,memory_mb=768)
report['actual_local_http_statuses']=[item['response']['status'] for item in entries]
report['official_rea_capture_execution']=rea['execution_status']
report['status']='pass' if report['status']=='pass' and report['actual_local_http_statuses']==[200,400,404] and rea['execution_status']=='returned' else 'fail'
(project/'qualification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report));raise SystemExit(0 if report['status']=='pass' else 1)
