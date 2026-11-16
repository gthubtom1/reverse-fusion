// Authenticate archived owned-material native records without rewriting IDs/paths.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {parseEvidence} from '../vendor/rea/package/dist/domain/evidence.js';
const root=path.resolve(fileURLToPath(new URL('..',import.meta.url)));
const base=path.join(root,'evidence/rf33');
const read=name=>JSON.parse(fs.readFileSync(path.join(base,name),'utf8').replace(/^\uFEFF/,''));
const summary=read('owned-desk-completion.json');
for(const file of summary.archived_raw_files){
  const bytes=fs.readFileSync(path.join(base,'owned-desk',file.path));
  if(createHash('sha256').update(bytes).digest('hex')!==file.sha256)throw Error(`Archived file changed:${file.path}`);
}
const bundle=read('owned-desk/work/current-case/evidence/original-bundle.json');
for(const record of bundle.records)parseEvidence(record);
const ledger=read('owned-desk/work/current-case/evidence/finite-proof/ledger.json');
parseEvidence(ledger.data);
const normalized=ledger.data.normalized_result;
if(normalized.status!=='ready'||normalized.summary.required_open!==0||normalized.summary.verified!==1)throw Error('Finite ledger not closed at its declared scope');
const result={status:'pass',archivedFiles:summary.archived_raw_files.length,originalNativeRecords:bundle.records.length,
  finiteLedger:{status:normalized.status,verified:normalized.summary.verified,requiredOpen:normalized.summary.required_open},
  scope:'archived native identity/fixity and declared finite ledger only; not global semantic proof'};
console.log(JSON.stringify(result));
