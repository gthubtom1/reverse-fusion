// Real bounded WASM integration replay; the official CLI owns ledger closure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { read, readEvidence, assertArtifact, sha256, createEvidence, bundle } from "./proof-support.mjs";

const root = path.resolve(fileURLToPath(new URL("..", import.meta.url)));
const state = path.join(root, "state");
const write = (name, value) => fs.writeFileSync(path.join(state, name), `${JSON.stringify(value, null, 2)}\n`, "utf8");
const original = readEvidence(path.join(state, "rea-wasm-evidence.json"));
const candidate = readEvidence(path.join(state, "rea-wasm-candidate-evidence.json"));
const originalFile = path.join(root, "fixtures/answer.wasm");
const candidateFile = path.join(root, "fixtures/answer-candidate.wasm");
assertArtifact(original, originalFile);
assertArtifact(candidate, candidateFile);
const wabt = read(path.join(root, "vendor/wabt/1.0.42/manifest.json"));
const interpreter = path.join(process.env.REVERSE_FUSION_WABT_BIN ?? path.join(root, "vendor/wabt/1.0.42/windows-x64/wabt-1.0.42/bin"), "wasm-interp.exe");
if (sha256(interpreter) !== wabt.bin_sha256["wasm-interp.exe"]) throw new Error("WABT interpreter hash differs from the pinned manifest");
const invoke = (file) => {
  const run = spawnSync(interpreter, [file, "--run-all-exports"], { encoding: "utf8", timeout: 10000, maxBuffer: 1024 * 1024, windowsHide: true });
  const output = run.stdout ?? "";
  const match = /answer\(\) => i32:(-?\d+)/u.exec(output);
  return { status: !run.error && run.status === 0 && match ? "observed" : "unknown", value: match ? Number(match[1]) : null, output, stderr: run.stderr ?? "", exit_code: run.status };
};
const left = invoke(originalFile);
const right = invoke(candidateFile);
assertArtifact(original, originalFile);
assertArtifact(candidate, candidateFile);
const observed = left.status === "observed" && right.status === "observed";
const passed = observed && left.value === right.value;

const compareInput = path.join(state, "wasm-compare-input.json");
write("wasm-compare-input.json", { left: original, right: candidate, scope: "both" });
const compared = spawnSync(process.execPath, [path.join(root, "vendor/rea/package/scripts/rea.mjs"), "compare-wasm-interfaces", compareInput, "--format", "json", "--full-output"], { encoding: "utf8", timeout: 30000, maxBuffer: 8 * 1024 * 1024, windowsHide: true });
if (compared.error || compared.status !== 0) throw new Error(`Official WASM comparison failed: ${compared.error?.message ?? compared.stderr}`);
write("rea-wasm-comparison-evidence.json", JSON.parse(compared.stdout));
const comparison = readEvidence(path.join(state, "rea-wasm-comparison-evidence.json"));
const proof = createEvidence(undefined, { id: "reverse-fusion-wabt-verifier", name: "Reverse Fusion WABT integration verifier", version: "rf25" }, {
  operation: "verify_reconstruction_obligations", predicateType: "rea.reconstruction-proof",
  parameters: { obligation_id: "wasm-answer", fixture_id: "wasm-answer-fixture", verifier_id: "wasm-interpreter", original_sha256: sha256(originalFile), candidate_sha256: sha256(candidateFile), interpreter_sha256: sha256(interpreter), verifier_sha256: sha256(fileURLToPath(import.meta.url)) },
  rawResult: { original: left, candidate: right },
  result: { bindings: [{ obligation_id: "wasm-answer", obligation_version: 1, owner_sha256: original.subject.digest.sha256,
    fixtures: [{ fixture_id: "wasm-answer-fixture", case_kind: "positive", passed }],
    verifiers: [{ verifier_id: "wasm-interpreter", claim_id: "wasm-answer", passed }] }] },
  confidence: observed ? "observed" : "derived", authority: "controlled-replay",
  limitations: ["Repository-owned integration replay covers answer() only; it is not native REA process verification or global equivalence."],
  evidenceLinks: [original.evidence_id, candidate.evidence_id, comparison.evidence_id],
});
write("rea-wasm-proof-evidence.json", { ok: true, data: proof });
const evidenceBundle = bundle([original, candidate, comparison, proof]);
write("rea-bundle.json", evidenceBundle);
write("ledger-input.json", {
  evidence_bundle: evidenceBundle,
  manifest: { contradictions: [], bindings: [{
    owner: { module_path: "fixtures/answer.wasm", symbol: "answer", owner_sha256: original.subject.digest.sha256 },
    obligation_id: "wasm-answer", parser_type: null,
    original_cases: [{ location: "export answer()", kind: "positive", evidence_id: proof.evidence_id }],
    fixtures: [{ fixture_id: "wasm-answer-fixture", case_kind: "positive", authority: "integration", evidence_ids: [proof.evidence_id] }],
    verifier: { verifier_id: "wasm-interpreter", claim_id: "wasm-answer", enumerated_obligation_ids: ["wasm-answer"], command: "wasm-interp <artifact> --run-all-exports", status: !observed ? "unknown" : passed ? "pass" : "fail", result_evidence_id: proof.evidence_id, authority: "integration", nondeterminism: { mode: "finite-traces", specification: "The original and candidate answer() observations are equal" } },
  }] },
  reviewed_obligations: [{ obligation_id: "wasm-answer", obligation_version: 1, title: "Observed WASM answer() export matches", application_layer: "runtime", family: "wasm-export", target: { semantic_node_id: null, application_node_id: null, artifact_sha256: original.subject.digest.sha256, location: "answer()" }, required: true, required_case_kinds: ["positive"], required_original_authority: "runtime", required_fixture_authority: "integration", required_verifier_authority: "integration", requires_parser_type: false, dependency_obligation_ids: [], residual_unknown_ids: [], unavailable_authority: [], required_next_evidence: [], disposition: "active", review_evidence_ids: [proof.evidence_id] }],
});
console.log(JSON.stringify({ status: !observed ? "unknown" : passed ? "pass" : "fail", proof_evidence_id: proof.evidence_id }));
process.exitCode = !observed ? 2 : passed ? 0 : 1;
