"""Use saved providers through the real launcher, export and reopen Evidence.

Caller supplies repository-owned compiled fixtures. No target is executed by
these analysis tools. This is not a reconstruction/equivalence claim.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from reverse_fusion.mcp_probe import StdioMcp,_check_configured_providers
from reverse_fusion.provider_runtime import ALL_KEYS,provider_status

parser=argparse.ArgumentParser()
parser.add_argument('--native',required=True)
parser.add_argument('--apk',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
native,apk=Path(args.native).resolve(),Path(args.apk).resolve()
output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=False)
environment={k:v for k,v in os.environ.items() if k not in ALL_KEYS}
argv=[sys.executable,str(ROOT/'scripts/mcp-launch.py'),'rea']
calls=[]
def call(client,name,arguments):
    response=client.request('tools/call',{'name':name,'arguments':arguments})
    calls.append({'tool':name,'arguments':arguments,'result':response})
    (output/'calls.json').write_text(json.dumps(calls,ensure_ascii=True,indent=2)+'\n',encoding='ascii')
    if response.get('isError'):raise ValueError(f'{name} returned an error; raw record retained')
    print(json.dumps({'tool':name,'status':'returned'}),flush=True)
    return response

with StdioMcp(argv,cwd=ROOT,env=environment,timeout=180) as client:
    identity=client.initialize()
    status=call(client,'binary_session',{})
    _check_configured_providers(ROOT,status)
    call(client,'inspect_wasm_artifact',{'path':str(ROOT/'fixtures/answer.wasm'),'detail':'summary'})
    call(client,'inspect_android_package',{'path':str(apk),'detail':'summary'})
    android=call(client,'inspect_android_class',{'path':str(apk),'class_name':'com.reversefusion.Answer'})
    call(client,'open_binary',{'path':str(native),'provider_id':'ghidra'})
    pseudocode=call(client,'procedure_pseudo_code',{'procedure':'main'})
    call(client,'close_binary',{})
    call(client,'export_evidence_bundle',{'path':str(output/'bundle.json')})
    before=call(client,'get_evidence_bundle',{'detail':'summary'})

with StdioMcp(argv,cwd=ROOT,env=environment,timeout=60) as resumed:
    resumed.initialize()
    imported=call(resumed,'import_evidence_bundle',{'path':str(output/'bundle.json')})
    after=call(resumed,'get_evidence_bundle',{'detail':'summary'})
previous=before['structuredContent']['result']
restored=after['structuredContent']['result']
if previous!=restored or previous['missing_direct_links'] or previous['matching_records']!=previous['total_retained_records']:
    raise ValueError('Evidence recovery changed records, links or retained coverage')
providers={record['provider']['id'] for record in restored['records']}
if not {'ghidra','jadx','wabt-artifact'}.issubset(providers):
    raise ValueError('The actual required native providers did not produce retained Evidence')
record_ids={record['evidence_id'] for record in restored['records']}
if not {pseudocode['structuredContent']['evidence_id'],android['structuredContent']['evidence_id']}.issubset(record_ids):
    raise ValueError('Original provider Evidence IDs did not survive process restart')
if imported['structuredContent']['result']['imported']!=len(record_ids):
    raise ValueError('The new server did not actually import the retained Evidence')
if not isinstance(pseudocode['structuredContent']['normalized_result'],str) or 'main' not in pseudocode['structuredContent']['normalized_result']:
    raise ValueError('Ghidra did not return the owned main function pseudocode')
if not any(method['name']=='answer' for method in android['structuredContent']['normalized_result']['methods']):
    raise ValueError('JADX did not inspect the owned class method')
if any(cleanup.get('status')!='verified' for cleanup in (client.cleanup,resumed.cleanup)):
    raise ValueError('Owned provider process cleanup is incomplete')
report={'status':'pass','scope':'finite Ghidra PE pseudocode, WABT module and JADX class; exported native Evidence accepted after process restart; no device/runtime/equivalence claim',
        'server':identity['serverInfo'],'provider_paths':provider_status(ROOT),
        'terminal_provider_keys_removed':sorted(ALL_KEYS),'native_sha256':sha256(native.read_bytes()).hexdigest(),
        'apk_sha256':sha256(apk.read_bytes()).hexdigest(),'bundle_sha256':sha256((output/'bundle.json').read_bytes()).hexdigest(),
        'ghidra_evidence_id':pseudocode['structuredContent']['evidence_id'],
        'jadx_evidence_id':android['structuredContent']['evidence_id'],
        'restored_records':len(record_ids),'provider_records':sorted(providers),'original_ids_and_links_restored':True,
        'first_process_cleanup':client.cleanup,'resumed_process_cleanup':resumed.cleanup,
        'before':before,'after':after}
(output/'report.json').write_text(json.dumps(report,ensure_ascii=True,indent=2)+'\n',encoding='ascii')
print(json.dumps({'status':'pass','bundle':str(output/'bundle.json')}))
