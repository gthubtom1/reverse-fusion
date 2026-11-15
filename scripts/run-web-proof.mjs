import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { readEvidence, assertArtifact, sha256, createEvidence, bundle as createEvidenceBundle } from "./proof-support.mjs";

const [originalPath, candidatePath, comparisonPath, originalModule, candidateModule, outputDir] = process.argv.slice(2);
if (![originalPath, candidatePath, comparisonPath, originalModule, candidateModule, outputDir].every(Boolean)) {
  throw new Error("usage: run-web-proof.mjs original.json candidate.json comparison.json original.js candidate.js output-dir");
}
const original = readEvidence(originalPath);
const candidate = readEvidence(candidatePath);
const comparison = readEvidence(comparisonPath);
if (!comparison.evidence_links.includes(original.evidence_id) || !comparison.evidence_links.includes(candidate.evidence_id)) throw new Error('Export comparison does not bind the retained application Evidence');
const assertGraphArtifact = (record, file) => {
  const digest = sha256(file);
  if (!(record.normalized_result?.graph?.nodes ?? []).some((node) =>
    node.identity?.sha256 === digest || node.observations?.some((item) => item.evidence?.artifact?.sha256 === digest))) {
    throw new Error(`Runtime module is absent from the application analysis: ${file}`);
  }
};
assertGraphArtifact(original, originalModule);
assertGraphArtifact(candidate, candidateModule);
// The complete application graph is archived separately. A bounded runtime
// ledger uses real, unmodified artifact-inventory Evidence as its authority;
// graph obligations are not removed by rewriting a comparison's links.
const inventory = (file) => {
  const result = spawnSync(process.execPath, [path.resolve("vendor/rea/package/scripts/rea.mjs"), "inspect-artifact", path.resolve(file), "--format", "json", "--full-output"], { encoding: "utf8", timeout: 30000, maxBuffer: 8 * 1024 * 1024, windowsHide: true });
  if (result.error || result.status !== 0) throw new Error(`Artifact inventory failed: ${result.error?.message ?? result.stderr}`);
  const record = JSON.parse(result.stdout).data.normalized_result.substeps.find((step) => step.operation === "inventory_artifact")?.evidence;
  if (!record) throw new Error("Official inventory Evidence missing");
  assertArtifact(record, file);
  return record;
};
const originalInventory = inventory(originalModule);
const candidateInventory = inventory(candidateModule);
const replay = (file, input) => {
  const code = 'import {pathToFileURL} from "node:url"; const m=await import(pathToFileURL(process.argv[1])); process.stdout.write(JSON.stringify({value:m.answer(JSON.parse(process.argv[2]))}));';
  const result = spawnSync(process.execPath, ["--input-type=module", "-e", code, path.resolve(file), JSON.stringify(input)], { encoding: "utf8", timeout: 10000, maxBuffer: 1024 * 1024, windowsHide: true });
  if (result.error || result.status !== 0) return { status: "unknown", reason: result.error?.message ?? result.stderr, exit_code: result.status };
  try { return { status: "observed", value: JSON.parse(result.stdout).value, exit_code: result.status }; }
  catch { return { status: "unknown", reason: "Runtime output was not the expected JSON" }; }
};

const cases = [" hello ", "", "\tMixed  text\n", "reverse-fusion"];
const traces = cases.map((input) => {
  const left = replay(originalModule, input);
  const right = replay(candidateModule, input);
  return { input, original: left, candidate: right, equal: left.status === "observed" && right.status === "observed" && left.value === right.value };
});
assertArtifact(originalInventory, originalModule);
assertArtifact(candidateInventory, candidateModule);
const runtimeObserved = traces.every(({ original: left, candidate: right }) => left.status === "observed" && right.status === "observed");
const runtimePass = traces.every(({ equal }) => equal);
const proof = createEvidence(
  undefined,
  { id: "reverse-fusion-web-verifier", name: "Reverse Fusion Web verifier", version: "1" },
  {
    // REA's ledger only qualifies the canonical reconstruction-proof
    // operation.  Keep the Web-specific trace in rawResult, while exposing
    // the typed bindings the official authority checker understands.
    operation: "verify_reconstruction_obligations",
    predicateType: "rea.reconstruction-proof",
    parameters: {
      obligation_id: "web-answer",
      fixture_id: "web-answer-fixture",
      verifier_id: "node-runtime",
      toolchain: process.version,
      original_sha256: sha256(originalModule),
      candidate_sha256: sha256(candidateModule),
      verifier_sha256: sha256(new URL(import.meta.url)),
    },
    rawResult: {
      operation: "web-answer",
      runtime: { status: runtimePass ? "pass" : "fail", traces },
    },
    result: {
      bindings: [{
        obligation_id: "web-answer",
        obligation_version: 1,
        owner_sha256: originalInventory.subject.digest.sha256,
        fixtures: [{ fixture_id: "web-answer-fixture", case_kind: "positive", passed: runtimePass }],
        verifiers: [{ verifier_id: "node-runtime", claim_id: "web-answer", passed: runtimePass }],
      }],
    },
    confidence: runtimeObserved ? "observed" : "derived",
    authority: "controlled-replay",
    limitations: [
      "The runtime proof covers the declared answer inputs only.",
      "REA static return-shape comparison remains conservative and may report unknown for dynamic expressions.",
      "This fixture does not claim browser rendering, network, or framework equivalence.",
    ],
    evidenceLinks: [originalInventory.evidence_id, candidateInventory.evidence_id],
  },
);
const bundle = createEvidenceBundle([original, candidate, comparison, originalInventory, candidateInventory, proof]);
// Keep the complete REA bundle for the case, but give the obligation ledger a
// bounded bundle for the reviewed export obligation. REA's application graph
// also derives packaging/parser obligations for this fixture; those remain
// explicit unknown scope in the acceptance record rather than being silently
// treated as verified by the answer proof.
const ledgerProof = proof;
const ledgerBundle = createEvidenceBundle([originalInventory, candidateInventory, proof]);
fs.mkdirSync(outputDir, { recursive: true });
const write = (name, value) => fs.writeFileSync(path.join(outputDir, name), `${JSON.stringify(value, null, 2)}\n`, "utf8");
write("rea-web-proof-evidence.json", { ok: true, data: proof });
write("rea-web-ledger-proof-evidence.json", { ok: true, data: ledgerProof });
write("rea-web-bundle.json", bundle);
write("rea-web-original-inventory.json", { ok: true, data: originalInventory });
write("rea-web-candidate-inventory.json", { ok: true, data: candidateInventory });
write("web-acceptance.json", {
  version: 1,
  operation: "web-reconstruction",
  status: !runtimeObserved ? "unknown" : runtimePass ? "pass" : "fail",
  original_evidence_id: original.evidence_id,
  candidate_evidence_id: candidate.evidence_id,
  comparison_evidence_id: comparison.evidence_id,
  proof_evidence_id: proof.evidence_id,
  ledger_proof_evidence_id: ledgerProof.evidence_id,
  static_status: comparison.normalized_result?.coverage?.status ?? "unknown",
  runtime: traces,
  unknown_scope: [
    "package-lifecycle behavior was not exercised",
    "parser-boundary obligations generated by the full application graph remain outside this export case",
  ],
  cleanup: { status: "observed", scope: "Bounded child invocations returned; descendant containment is not qualified." },
});
const ledgerInput = {
  manifest: {
    bindings: [{
      owner: { symbol: "answer", module_path: "app.js", owner_sha256: originalInventory.subject.digest.sha256 },
      obligation_id: "web-answer",
      fixtures: [{ fixture_id: "web-answer-fixture", evidence_ids: [ledgerProof.evidence_id], authority: "integration", case_kind: "positive" }],
      verifier: {
        verifier_id: "node-runtime",
        enumerated_obligation_ids: ["web-answer"],
        command: "node web-answer-fixture",
        status: runtimePass ? "pass" : "fail",
        result_evidence_id: ledgerProof.evidence_id,
        authority: "integration",
        claim_id: "web-answer",
        nondeterminism: { mode: "finite-traces", specification: "answer(value) trims, uppercases and prefixes rf:" },
      },
      parser_type: null,
      original_cases: [{ location: "app.js export answer runtime trace", kind: "positive", evidence_id: ledgerProof.evidence_id }],
    }],
    contradictions: [],
  },
  evidence_bundle: ledgerBundle,
  reviewed_obligations: [{
    disposition: "active",
    required: true,
    family: "javascript-export",
    residual_unknown_ids: [],
    unavailable_authority: [],
    requires_parser_type: false,
    application_layer: "runtime",
    obligation_version: 1,
    obligation_id: "web-answer",
    required_fixture_authority: "integration",
    required_verifier_authority: "integration",
    required_case_kinds: ["positive"],
    dependency_obligation_ids: [],
    target: { semantic_node_id: null, location: "app.js export answer", artifact_sha256: originalInventory.subject.digest.sha256, application_node_id: null },
    required_next_evidence: [],
    review_evidence_ids: [ledgerProof.evidence_id],
    required_original_authority: "runtime",
    title: "Web answer export matches the observed finite runtime traces",
  }],
};
write("web-ledger-input.json", ledgerInput);
write("web-full-ledger-input.json", { ...ledgerInput, evidence_bundle: bundle });
console.log(JSON.stringify({ status: runtimePass ? "pass" : "fail", original: original.evidence_id, candidate: candidate.evidence_id, comparison: comparison.evidence_id, proof: proof.evidence_id }));
process.exitCode = !runtimeObserved ? 2 : runtimePass ? 0 : 1;
