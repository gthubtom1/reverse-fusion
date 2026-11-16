// Uses the repository's explicitly reviewed serializer adapter for finite replay proof.
// The official REA CLI alone calculates native ledger status.
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {read,readEvidence,sha256,assertArtifact,createEvidence,bundle} from 'file:///D:/Project/reverse/scripts/proof-support.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'work/current-case/evidence/finite-proof');fs.mkdirSync(out,{recursive:true});
const node=process.execPath,cli='D:/Project/reverse/vendor/rea/package/scripts/rea.mjs';
const write=(name,obj)=>fs.writeFileSync(path.join(out,name),JSON.stringify(obj,null,2),'utf8');
const run=(args)=>{const p=spawnSync(node,args,{cwd:root,encoding:'utf8',timeout:60000,maxBuffer:16*1024*1024,windowsHide:true});if(p.error||p.status!==0)throw Error(p.error?.message||p.stderr||p.stdout);return p.stdout;};
const oldModule=path.join(root,'desk-original/core.mjs'),newModule=path.join(root,'outputs/标签收纳盒/core.mjs');
function inventory(file,name){const output=run([cli,'inspect-artifact',file,'--format','json','--full-output']);fs.writeFileSync(path.join(out,name+'.json'),output);const record=JSON.parse(output).data.normalized_result.substeps.find(x=>x.operation==='inventory_artifact')?.evidence;if(!record)throw Error('No native inventory');assertArtifact(record,file);return record;}
const left=inventory(oldModule,'original-inventory'),right=inventory(newModule,'candidate-inventory');
const execution=run([path.join(root,'work/compare.mjs'),path.join(root,'outputs/标签收纳盒'),path.join(out,'replay')]);
fs.writeFileSync(path.join(out,'replay-output.txt'),execution);
const result=read(path.join(out,'replay/result.json')),launch=read(path.join(root,'work/current-case/evidence/launcher-smoke.json'));
const files=Object.keys(result.files);
for(const name of files){if(sha256(path.join(root,'outputs/标签收纳盒',name))!==result.files[name])throw Error('Stale candidate identity');}
const originalHashes=read(path.join(root,'work/current-case/notes/original-identity.json'));
for(const [name,hash]of Object.entries(originalHashes))if(sha256(path.join(root,'desk-original',name))!==hash)throw Error('Original changed');
const passed=result.status==='pass'&&result.wrongCandidateRejected===true&&launch.status==='pass'&&launch.port_closed;
const proof=createEvidence(undefined,{id:'reverse-fusion-desk-verifier',name:'Reverse Fusion finite desk application replay verifier',version:'1'}, {
 operation:'verify_reconstruction_obligations',predicateType:'rea.reconstruction-proof',
 parameters:{obligation_id:'desk-declared-replay',fixture_id:'desk-finite-cases',verifier_id:'desk-node-chrome',original_sha256:sha256(oldModule),candidate_sha256:sha256(newModule),verifier_sha256:sha256(fileURLToPath(import.meta.url)),comparator_sha256:sha256(path.join(root,'work/compare.mjs')),browser_scenario_sha256:sha256(path.join(root,'work/observe.cjs')),all_original_file_hashes:originalHashes,all_candidate_file_hashes:result.files},
 rawResult:{replay:result,launcher:launch},
 result:{bindings:[{obligation_id:'desk-declared-replay',obligation_version:1,owner_sha256:left.subject.digest.sha256,
 fixtures:['positive','negative','malformed'].map(kind=>({fixture_id:'desk-finite-'+kind,case_kind:kind,passed})),verifiers:[{verifier_id:'desk-node-chrome',claim_id:'desk-declared-replay',passed}]}]},
 confidence:'observed',authority:'controlled-replay',
 limitations:['Repository-owned integration proof of declared finite cases only; not native REA browser/process verification and not universal equivalence.','Full original static application ledger and conservative unknowns remain archived unchanged.','Screenshots cover this installed Chrome at declared desktop/mobile viewports.','Launcher Python path tested with --no-browser; CMD wrapper inspected separately.'],
 evidenceLinks:[left.evidence_id,right.evidence_id]
});
const evidence=bundle([left,right,proof]);
write('proof.json',{ok:true,data:proof});write('bundle.json',evidence);
write('ledger-input.json',{
 evidence_bundle:evidence,
 manifest:{contradictions:[],bindings:[{owner:{module_path:'desk-original/core.mjs',symbol:'initial,restore,change,view; observed browser UI',owner_sha256:left.subject.digest.sha256},obligation_id:'desk-declared-replay',parser_type:null,
 original_cases:['positive','negative','malformed'].map(kind=>({location:'declared core/UI replay',kind,evidence_id:proof.evidence_id})),
 fixtures:['positive','negative','malformed'].map(kind=>({fixture_id:'desk-finite-'+kind,case_kind:kind,authority:'integration',evidence_ids:[proof.evidence_id]})),
 verifier:{verifier_id:'desk-node-chrome',claim_id:'desk-declared-replay',enumerated_obligation_ids:['desk-declared-replay'],command:'node work/finite-proof.mjs',status:passed?'pass':'fail',result_evidence_id:proof.evidence_id,authority:'integration',nondeterminism:{mode:'finite-traces',specification:'Frozen deterministic core cases, 1200 seeded operations, 21 browser checkpoints, three exact screenshots, mutant rejection and local launcher smoke'}}}]},
 reviewed_obligations:[{obligation_id:'desk-declared-replay',obligation_version:1,title:'Declared finite collection behavior and same-browser screenshots match original; delivered local launcher smoke passes',application_layer:'runtime',family:'desk-declared-cases',target:{semantic_node_id:null,application_node_id:null,artifact_sha256:left.subject.digest.sha256,location:'Exact retained core, UI and local launch observations'},required:true,required_case_kinds:['positive','negative','malformed'],required_original_authority:'runtime',required_fixture_authority:'integration',required_verifier_authority:'integration',requires_parser_type:false,dependency_obligation_ids:[],residual_unknown_ids:[],unavailable_authority:[],required_next_evidence:[],disposition:'active',review_evidence_ids:[proof.evidence_id]}]
});
console.log(JSON.stringify({passed,proof_evidence:proof.evidence_id,checks:result.checks}));
if(!passed)process.exitCode=1;
