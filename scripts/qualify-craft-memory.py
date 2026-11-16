"""Real original Craft Project persistence and case-isolation qualification.

Creates owned material in a new temporary outcome project outside the tool
checkout. Does not read keys, change host settings or start another model.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reverse_fusion.mcp_probe import StdioMcp, catalog

parser = argparse.ArgumentParser()
pin = json.loads((ROOT/'components/craft-mcp/manifest.json').read_text(encoding='utf-8'))
parser.add_argument('--binary', type=Path, default=ROOT/pin['platforms']['windows-x64']['local_path'])
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=False)
project = Path(tempfile.mkdtemp(prefix='rf36-craft-outcome-')).resolve()
case = project/'work/case-a'
other = project/'work/case-b'
case.mkdir(parents=True);other.mkdir(parents=True)
source = project/'original.mjs'
source.write_text('export function answer(x) { return x + 7; }\n', encoding='utf-8')
native = project/'owned.bin'
native.write_bytes(b'\x90\x90\xc3')
state = output/'owned-server-state'
argv = [str(args.binary.resolve()), '--all-tools', '--deep-mode', '--allow-run', '--state-dir', str(state)]
calls = []

def call(client, name, arguments, *, error=False):
    response = client.request('tools/call', {'name':name,'arguments':arguments})
    calls.append({'tool':name,'arguments':arguments,'result':response})
    (output/'calls.json').write_text(json.dumps(calls,ensure_ascii=True,indent=2)+'\n',encoding='ascii')
    if bool(response.get('isError')) != error:
        raise AssertionError(f'{name}: unexpected error status {response}')
    content = response.get('structuredContent',{})
    return content if 'id' in content else content.get('result',content)

with StdioMcp(argv,cwd=ROOT) as client:
    identity=client.initialize()
    tools=catalog(client)
    names={tool['name'] for tool in tools}
    assert 'fusion_case_open' in names
    call(client,'js_app_map',{'input_path':str(source)},error=True)
    modes=call(client,'engines_list',{})
    assert modes['deep_mode']['enabled'] is True
    bound=call(client,'fusion_case_open',{'project_root':str(project),'case_root':str(case)})
    call(client,'core_target_open',{'path':str(source)})
    evidence=call(client,'js_app_map',{'input_path':str(source)})
    evidence_id=evidence['id']
    call(client,'core_brief_write',{'question':'Explain the owned answer function','done_when':'Evidence and memory survive restart'})
    call(client,'core_finding_record',{'statement':'The owned module exports answer','evidence_ids':[evidence_id],'confidence':'derived'})
    call(client,'core_unknown_add',{'question':'Does a future input change behavior?','domain':'owned-fixture','evidence_for':[evidence_id]})
    unknowns=call(client,'core_unknowns_show',{})
    call(client,'core_handoff_write',{'text':'Resume original analysis; preserved original evidence ID is required.'})
    call(client,'core_target_open',{'path':str(native),'format':'raw-binary','architecture':'x86_64','entry_point':'0x1000'})
    call(client,'native_comment_write',{'address':'0x1000','comment':'Owned annotation survives restart'})
    before=call(client,'core_investigation_show',{})
    call(client,'core_journal_read',{'limit':30})

with StdioMcp(argv,cwd=ROOT) as client:
    client.initialize()
    reopened=call(client,'fusion_case_open',{'project_root':str(project),'case_root':str(case)})
    restored=call(client,'core_investigation_show',{})
    assert restored['brief']==before['brief']
    assert restored['findings']==before['findings']
    assert restored['handoff']==before['handoff']
    assert call(client,'core_unknowns_show',{})==unknowns
    assert reopened['restored_targets']==2
    retained=call(client,'core_evidence_show',{'evidence_id':evidence_id})
    assert evidence_id in json.dumps(retained)
    annotation=call(client,'native_comment_read',{'address':'0x1000'})
    assert 'Owned annotation survives restart' in json.dumps(annotation)
    journal=call(client,'core_journal_read',{'tool':'core_handoff_write','limit':30})
    assert 'core_handoff_write' in json.dumps(journal)
    call(client,'fusion_case_open',{'project_root':str(project),'case_root':str(other)})
    other_state=call(client,'core_session_show',{})
    assert other_state['evidence_records']==0 and other_state['unknowns']==0 and not other_state['targets']
    empty=call(client,'core_investigation_show',{})
    assert empty['brief'] is None and empty['findings']==[]
    assert call(client,'core_evidence_show',{'evidence_id':evidence_id})['records']==[]
    call(client,'fusion_case_open',{'project_root':str(project),'case_root':str(case)})
    assert call(client,'core_investigation_show',{})['findings']==before['findings']

# A missing/changed target blocks that target's restore, not the saved investigation.
source.write_text('export function answer(x) { return x + 8; }\n',encoding='utf-8')
with StdioMcp(argv,cwd=ROOT) as client:
    client.initialize()
    changed=call(client,'fusion_case_open',{'project_root':str(project),'case_root':str(case)})
    assert changed['restored_targets']==1 and len(changed['unavailable_targets'])==1
    assert call(client,'core_investigation_show',{})['findings']==before['findings']

report={'status':'pass','scope':'owned original Project bind/analysis/brief/finding/handoff/annotation/journal, restart, case isolation and target drift',
        'server':identity['serverInfo'],'tools':len(tools),'binary_sha256':sha256(args.binary.read_bytes()).hexdigest(),
        'outcome_project':str(project),'case_root':str(case),'evidence_id':evidence_id,
        'original_memory_restored':True,'unknowns_restored':True,'annotation_restored':True,'journal_restored':True,
        'cross_case_contamination':False,'changed_target_isolated':True,
        'effective_deep_mode':modes['deep_mode'],'cleanup':client.cleanup}
(output/'report.json').write_text(json.dumps(report,ensure_ascii=True,indent=2)+'\n',encoding='ascii')
print(json.dumps(report,ensure_ascii=True,indent=2))
