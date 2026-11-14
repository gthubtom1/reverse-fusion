import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { compareWasmInterfaces } from "../vendor/rea/package/dist/application/wasm/WasmInterfaceComparisonService.js";
import { createEvidence } from "../vendor/rea/package/dist/domain/evidence.js";
import { createEvidenceBundle } from "../vendor/rea/package/dist/domain/evidenceBundle.js";

const root = path.resolve(fileURLToPath(new URL("..", import.meta.url)));
const state = path.join(root, "state");

const readJson = (name) => JSON.parse(fs.readFileSync(path.join(state, name), "utf8"));
const writeJson = (name, value) => {
  fs.writeFileSync(path.join(state, name), `${JSON.stringify(value, null, 2)}\n`, "utf8");
};

const original = readJson("rea-wasm-evidence.json").data;
const candidate = readJson("rea-wasm-candidate-evidence.json").data;
const acceptance = readJson("wasm-acceptance.json");
if (acceptance.status !== "pass" || acceptance.candidate_kind !== "correct") {
  throw new Error("The correct WASM acceptance must pass before an obligation proof is emitted");
}

const comparisonResult = await compareWasmInterfaces({
  left: original,
  right: candidate,
  scope: "both",
});
if (!comparisonResult.ok) throw comparisonResult.error;
const comparison = comparisonResult.value.evidence;
if (comparison.normalized_result.summary.changed !== 0 || comparison.normalized_result.summary.unknown !== 0) {
  throw new Error("WASM interface comparison is not an unchanged, complete comparison");
}

const sourceIds = [original.evidence_id, candidate.evidence_id];
const proof = createEvidence(
  undefined,
  { id: "reverse-fusion-wabt-verifier", name: "Reverse Fusion WABT verifier", version: "1" },
  {
    operation: "verify_reconstruction_obligations",
    predicateType: "rea.reconstruction-proof",
    parameters: {
      obligation_id: "wasm-answer",
      fixture_id: "wasm-answer-fixture",
      verifier_id: "wasm-interpreter",
      toolchain: "wabt@1.0.42",
    },
    rawResult: {
      operation: acceptance.operation,
      candidate: acceptance.candidate_kind,
      interface: acceptance.interface,
      runtime: acceptance.runtime,
      left_run: acceptance.left_run,
      right_run: acceptance.right_run,
    },
    result: {
      bindings: [
        {
          obligation_id: "wasm-answer",
          obligation_version: 1,
          owner_sha256: original.subject.digest.sha256,
          fixtures: [
            { fixture_id: "wasm-answer-fixture", case_kind: "positive", passed: true },
          ],
          verifiers: [
            { verifier_id: "wasm-interpreter", claim_id: "wasm-answer", passed: true },
          ],
        },
      ],
    },
    confidence: "observed",
    authority: "controlled-replay",
    limitations: [
      "This proof covers the declared finite WASM fixture and WABT interpreter run only.",
      "It does not establish global source equivalence or behavior outside the declared export.",
    ],
    evidenceLinks: [...sourceIds, comparison.evidence_id],
  },
);

const bundle = createEvidenceBundle([original, candidate, comparison, proof], []);
writeJson("rea-wasm-comparison-evidence.json", { ok: true, data: comparison });
writeJson("rea-wasm-proof-evidence.json", { ok: true, data: proof });
writeJson("rea-bundle.json", bundle);

const input = readJson("ledger-input.json");
input.evidence_bundle = bundle;
input.manifest.bindings = input.manifest.bindings.map((binding) => ({
  ...binding,
  fixtures: binding.fixtures.map((fixture) => ({
    ...fixture,
    evidence_ids: [proof.evidence_id],
  })),
  verifier: binding.verifier
    ? { ...binding.verifier, result_evidence_id: proof.evidence_id }
    : binding.verifier,
}));
writeJson("ledger-input.json", input);
console.log(JSON.stringify({
  status: "ready-for-ledger",
  comparison_evidence_id: comparison.evidence_id,
  proof_evidence_id: proof.evidence_id,
  evidence_ids: bundle.records.map(({ evidence_id }) => evidence_id),
}));
