// Preserve canonical REA records as UTF-8/JSON across Windows locale settings.
// Static shape observations are separate from runtime behavior acceptance.
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';

const [leftFile, rightFile, leftModule, rightModule, outputDirectory, ...exports] = process.argv.slice(2);
if (!outputDirectory || exports.length === 0 || exports.some(name => !/^[A-Za-z_$][\w$]*$/.test(name))) {
  throw Error('Expected left-bundle right-bundle left-module right-module output-dir export-names...');
}
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const rea = path.join(root, 'vendor/rea/package/scripts/rea.mjs');
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const load = name => {
  const bytes = fs.readFileSync(name);
  const bundle = JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/, ''));
  const records = bundle.records ?? [bundle.data ?? bundle];
  const applications = records.filter(record => record.operation === 'analyze_javascript_application');
  if (applications.length !== 1) throw Error('Select a bundle containing exactly one application Evidence');
  return {record: applications[0], digest: digest(bytes)};
};
const left = load(leftFile), right = load(rightFile);
const output = path.resolve(outputDirectory);
fs.mkdirSync(output, {recursive: true});
const results = [];
for (const name of exports) {
  const input = path.join(output, `${name}-request.json`);
  if (fs.existsSync(input) || fs.existsSync(path.join(output, `${name}-result.json`))) throw Error('Comparison output already exists; use a new run directory');
  fs.writeFileSync(input, JSON.stringify({left: left.record, right: right.record,
    left_module_path: leftModule, left_export_name: name,
    right_module_path: rightModule, right_export_name: name}), {flag: 'wx'});
  const run = spawnSync(process.execPath, [rea, 'compare-javascript-export-shapes', input,
    '--format', 'json', '--full-output'], {encoding: 'utf8', timeout: 30000,
    maxBuffer: 16 * 1024 * 1024, windowsHide: true});
  fs.writeFileSync(path.join(output, `${name}-result.json`), run.stdout ?? '');
  fs.writeFileSync(path.join(output, `${name}-stderr.txt`), run.stderr ?? '');
  if (run.error || run.status !== 0) throw Error(`REA comparison failed for ${name}; inspect retained result`);
  const result = JSON.parse(run.stdout);
  if (result.ok !== true) throw Error('REA did not return a successful Evidence record');
  results.push({export: name, evidence_id: result.data.evidence_id,
    coverage: result.data.normalized_result.coverage, business_acceptance: 'not-performed'});
}
if (digest(fs.readFileSync(leftFile)) !== left.digest || digest(fs.readFileSync(rightFile)) !== right.digest) throw Error('Source Evidence changed during comparison');
const summary = {authority: 'official REA static shape comparison, no runtime equivalence claim',
  left_bundle_sha256: left.digest, right_bundle_sha256: right.digest, results};
fs.writeFileSync(path.join(output, 'summary.json'), JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary));
