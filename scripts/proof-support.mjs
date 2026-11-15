// Repository-owned integration verifier support for the pinned REA 6.9.0
// wire format. This adapter does not impersonate REA's native verifier.
import fs from "node:fs";
import { createHash } from "node:crypto";
import { createEvidence, parseEvidence } from "../vendor/rea/package/dist/domain/evidence.js";
import { createEvidenceBundle } from "../vendor/rea/package/dist/domain/evidenceBundle.js";

const packageInfo = JSON.parse(fs.readFileSync(new URL("../vendor/rea/package/package.json", import.meta.url), "utf8"));
if (packageInfo.name !== "rea-agents" || packageInfo.version !== "6.9.0") {
  throw new Error("Integration serializer requires the reviewed rea-agents@6.9.0 package");
}

export const read = (file) => JSON.parse(fs.readFileSync(file, "utf8").replace(/^\uFEFF/u, ""));
export const readEvidence = (file) => {
  const envelope = read(file);
  if (envelope.ok !== true) throw new Error(`Failed Evidence envelope: ${file}`);
  return parseEvidence(envelope.data);
};
export const sha256 = (file) => createHash("sha256").update(fs.readFileSync(file)).digest("hex");
export const assertArtifact = (record, file) => {
  parseEvidence(record);
  if (record.subject?.digest?.sha256 !== sha256(file)) {
    throw new Error(`Artifact differs from its original analysis Evidence: ${file}`);
  }
};
export const bundle = (records) => createEvidenceBundle(records.map(parseEvidence), []);
export { createEvidence };
