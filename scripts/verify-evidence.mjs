// Optional provider-level verification after REA bootstrap. Pure Python
// contracts stay usable without downloading a provider during installation.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
import { parseEvidence } from "../vendor/rea/package/dist/domain/evidence.js";
import { readEvidenceBundle } from "../vendor/rea/package/dist/domain/evidenceBundle.js";

const root = path.resolve(fileURLToPath(new URL("..", import.meta.url)));
if (process.argv[2] === '--records') {
  if (process.argv.length < 4) throw new Error('At least one Evidence envelope is required');
  for (const name of process.argv.slice(3)) {
    const envelope = JSON.parse(fs.readFileSync(name, 'utf8').replace(/^\uFEFF/u, ''));
    if (envelope.ok !== true) throw new Error(`Failed Evidence envelope: ${name}`);
    parseEvidence(envelope.data);
  }
  console.log(JSON.stringify({ status: 'pass', authenticated_records: process.argv.length - 3 }));
} else {
const manifest = JSON.parse(fs.readFileSync(path.join(root, "evidence/rf22/manifest.json"), "utf8"));
const checks = [];
const digest = (file) => createHash('sha256').update(fs.readFileSync(file)).digest('hex');
for (const [target, group] of Object.entries(manifest.targets)) {
  const records = new Map();
  for (const name of Object.keys(group.files)) {
    const file = path.join(root, "evidence/rf22", target, name);
    if (digest(file) !== group.files[name].sha256) throw new Error(`Archive file digest mismatch: ${target}/${name}`);
    const value = JSON.parse(fs.readFileSync(file, "utf8").replace(/^\uFEFF/u, ""));
    if (Array.isArray(value.records)) {
      const admitted = readEvidenceBundle(value, { operation: "reverse-fusion-archive-check", path: [target, name] });
      if (!admitted.ok) throw admitted.error;
      for (const record of value.records) records.set(record.evidence_id, record);
    } else if (value.data?.evidence_id) {
      parseEvidence(value.data);
      records.set(value.data.evidence_id, value.data);
    }
  }
  const missing = new Set();
  for (const record of records.values()) {
    for (const id of record.evidence_links) if (!records.has(id)) missing.add(id);
  }
  if (missing.size) throw new Error(`${target}: missing linked Evidence: ${[...missing].join(", ")}`);
  // Exercise the negative gate using the actual archived record, not a mock
  // declaration that merely says an invalid digest was rejected.
  const altered = structuredClone(records.values().next().value);
  altered.parameters = { ...altered.parameters, tampered: true };
  let rejected = false;
  try { parseEvidence(altered); } catch { rejected = true; }
  if (!rejected) throw new Error(`${target}: Evidence tamper control was accepted`);
  checks.push({ target, authenticated_records: records.size, linked_closure: "pass", tamper_control: "rejected" });
}
const archiveRoot = path.join(root, 'evidence/rf22');
const builder = JSON.parse(fs.readFileSync(path.join(archiveRoot, 'builder/manifest.json'), 'utf8'));
const session = JSON.parse(fs.readFileSync(path.join(archiveRoot, builder.record), 'utf8'));
for (const [source, expected] of Object.entries(session.frozen_refs)) {
  if (digest(path.join(archiveRoot, builder.frozen_input_archive[source])) !== expected) throw new Error(`Frozen Builder input drift: ${source}`);
}
for (const [name, record] of Object.entries(builder.outputs)) {
  if (digest(path.join(archiveRoot, record.path)) !== record.sha256 || session.events.at(-1).outputs[name] !== record.sha256) throw new Error(`Archived candidate drift: ${name}`);
}
checks.push({ target: 'current-session-builder', frozen_inputs: Object.keys(session.frozen_refs).length, candidate_files: Object.keys(builder.outputs).length, status: 'pass', business_acceptance: 'separate target proofs' });
console.log(JSON.stringify({ status: "pass", checks }, null, 2));
}
