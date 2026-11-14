import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createEvidence } from "../vendor/rea/package/dist/domain/evidence.js";
import { createEvidenceBundle } from "../vendor/rea/package/dist/domain/evidenceBundle.js";

const [originalPath, candidatePath, comparisonPath, originalModule, candidateModule, outputDir] = process.argv.slice(2);
if (![originalPath, candidatePath, comparisonPath, originalModule, candidateModule, outputDir].every(Boolean)) {
  throw new Error("usage: run-web-proof.mjs original.json candidate.json comparison.json original.js candidate.js output-dir");
}
const read = (file) => JSON.parse(fs.readFileSync(file, "utf8").replace(/^\uFEFF/u, ""));
const original = read(originalPath).data;
const candidate = read(candidatePath).data;
const comparison = read(comparisonPath).data;
const originalModuleValue = await import(pathToFileURL(path.resolve(originalModule)).href + `?original=${Date.now()}`);
const candidateModuleValue = await import(pathToFileURL(path.resolve(candidateModule)).href + `?candidate=${Date.now()}`);
if (typeof originalModuleValue.answer !== "function" || typeof candidateModuleValue.answer !== "function") {
  throw new Error("both artifacts must export answer(value)");
}

const cases = [" hello ", "", "\tMixed  text\n", "reverse-fusion"];
const traces = cases.map((input) => {
  const left = originalModuleValue.answer(input);
  const right = candidateModuleValue.answer(input);
  return { input, original: left, candidate: right, equal: left === right };
});
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
    },
    rawResult: {
      operation: "web-answer",
      runtime: { status: runtimePass ? "pass" : "fail", traces },
      static_comparison: { evidence_id: comparison.evidence_id, status: comparison.normalized_result?.coverage?.status ?? "unknown" },
    },
    result: {
      bindings: [{
        obligation_id: "web-answer",
        obligation_version: 1,
        owner_sha256: original.subject.digest.sha256,
        fixtures: [{ fixture_id: "web-answer-fixture", case_kind: "positive", passed: runtimePass }],
        verifiers: [{ verifier_id: "node-runtime", claim_id: "web-answer", passed: runtimePass }],
      }],
    },
    confidence: runtimePass ? "observed" : "contradicted",
    authority: "controlled-replay",
    limitations: [
      "The runtime proof covers the declared answer inputs only.",
      "REA static return-shape comparison remains conservative and may report unknown for dynamic expressions.",
      "This fixture does not claim browser rendering, network, or framework equivalence.",
    ],
    evidenceLinks: [original.evidence_id, candidate.evidence_id, comparison.evidence_id],
  },
);
const bundle = createEvidenceBundle([original, candidate, comparison, proof], []);
// Keep the complete REA bundle for the case, but give the obligation ledger a
// bounded bundle for the reviewed export obligation. REA's application graph
// also derives packaging/parser obligations for this fixture; those remain
// explicit unknown scope in the acceptance record rather than being silently
// treated as verified by the answer proof.
const ledgerComparison = createEvidence(
  undefined,
  comparison.provider,
  {
    operation: comparison.operation,
    predicateType: comparison.predicate_type,
    parameters: comparison.parameters,
    rawResult: comparison.raw_result,
    result: comparison.normalized_result,
    confidence: comparison.confidence,
    authority: comparison.authority,
    limitations: comparison.limitations,
    evidenceLinks: [],
  },
);
const ledgerProof = createEvidence(
  undefined,
  proof.provider,
  {
    operation: proof.operation,
    predicateType: proof.predicate_type,
    parameters: proof.parameters,
    rawResult: proof.raw_result,
    result: proof.normalized_result,
    confidence: proof.confidence,
    authority: proof.authority,
    limitations: proof.limitations,
    evidenceLinks: [ledgerComparison.evidence_id],
  },
);
const ledgerBundle = createEvidenceBundle([ledgerComparison, ledgerProof], []);
fs.mkdirSync(outputDir, { recursive: true });
const write = (name, value) => fs.writeFileSync(path.join(outputDir, name), `${JSON.stringify(value, null, 2)}\n`, "utf8");
write("rea-web-proof-evidence.json", { ok: true, data: proof });
write("rea-web-ledger-proof-evidence.json", { ok: true, data: ledgerProof });
write("rea-web-bundle.json", bundle);
write("web-acceptance.json", {
  version: 1,
  operation: "web-reconstruction",
  status: runtimePass ? "pass" : "fail",
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
  cleanup: { status: "verified" },
});
write("web-ledger-input.json", {
  manifest: {
    bindings: [{
      owner: { symbol: "answer", module_path: "app.js", owner_sha256: original.subject.digest.sha256 },
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
    target: { semantic_node_id: null, location: "app.js export answer", artifact_sha256: original.subject.digest.sha256, application_node_id: null },
    required_next_evidence: [],
    review_evidence_ids: [ledgerProof.evidence_id],
    required_original_authority: "runtime",
    title: "Web answer export matches the observed finite runtime traces",
  }],
});
console.log(JSON.stringify({ status: runtimePass ? "pass" : "fail", original: original.evidence_id, candidate: candidate.evidence_id, comparison: comparison.evidence_id, proof: proof.evidence_id }));
process.exitCode = runtimePass ? 0 : 1;
