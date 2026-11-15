import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { readEvidence, assertArtifact, sha256, createEvidence, bundle as createEvidenceBundle } from "./proof-support.mjs";

const [originalPath, candidatePath, originalMembersPath, candidateMembersPath, comparisonPath, outputDir] = process.argv.slice(2);
if (![originalPath, candidatePath, originalMembersPath, candidateMembersPath, comparisonPath, outputDir].every(Boolean)) {
  throw new Error("usage: run-dotnet-proof.mjs original.json candidate.json original-members.json candidate-members.json comparison.json output-dir");
}

const original = readEvidence(originalPath);
const candidate = readEvidence(candidatePath);
const originalMembers = readEvidence(originalMembersPath);
const candidateMembers = readEvidence(candidateMembersPath);
const comparison = readEvidence(comparisonPath);
assertArtifact(original, original.subject.local_path);
assertArtifact(candidate, candidate.subject.local_path);
assertArtifact(originalMembers, original.subject.local_path);
assertArtifact(candidateMembers, candidate.subject.local_path);
if (!comparison.evidence_links.includes(originalMembers.evidence_id) || !comparison.evidence_links.includes(candidateMembers.evidence_id)) throw new Error('Managed comparison does not bind the retained member Evidence');
const dotnet = process.env.REVERSE_FUSION_DOTNET || "dotnet";
const cases = [" hello ", "", "\tMixed  text\n", "reverse-fusion"];

const invoke = (dll, input) => {
  const result = spawnSync(dotnet, [dll, input], { encoding: "utf8", timeout: 15000, windowsHide: true });
  const stdout = (result.stdout || "").trimEnd();
  const stderr = (result.stderr || "").trim();
  if (result.error) return { status: "unknown", reason: result.error.message, input };
  if (result.status !== 0) return { status: "unknown", reason: stderr || `exit ${result.status}`, input, exit_code: result.status };
  return { status: "observed", input, output: stdout, exit_code: 0 };
};

const traces = cases.map((input) => {
  const left = invoke(original.subject.local_path, input);
  const right = invoke(candidate.subject.local_path, input);
  return { input, original: left, candidate: right, equal: left.status === "observed" && right.status === "observed" && left.output === right.output };
});
const runtimePass = traces.every(({ equal }) => equal);
const runtimeObserved = traces.every(({ original: left, candidate: right }) => left.status === "observed" && right.status === "observed");
assertArtifact(original, original.subject.local_path);
assertArtifact(candidate, candidate.subject.local_path);
const proof = createEvidence(
  undefined,
  { id: "reverse-fusion-dotnet-verifier", name: "Reverse Fusion .NET verifier", version: "1" },
  {
    operation: "verify_reconstruction_obligations",
    predicateType: "rea.reconstruction-proof",
    parameters: {
      obligation_id: "dotnet-answer",
      fixture_id: "dotnet-answer-fixture",
      verifier_id: "dotnet-runtime",
      toolchain: process.env.REVERSE_FUSION_DOTNET || "dotnet",
      original_sha256: sha256(original.subject.local_path),
      candidate_sha256: sha256(candidate.subject.local_path),
      verifier_sha256: sha256(new URL(import.meta.url)),
    },
    rawResult: {
      operation: "dotnet-answer",
      runtime: { status: runtimePass ? "pass" : "fail", traces },
      managed_comparison: { evidence_id: comparison.evidence_id, summary: comparison.normalized_result?.summary ?? null },
    },
    result: {
      bindings: [{
        obligation_id: "dotnet-answer",
        obligation_version: 1,
        owner_sha256: original.subject.digest.sha256,
        fixtures: [{ fixture_id: "dotnet-answer-fixture", case_kind: "positive", passed: runtimePass }],
        verifiers: [{ verifier_id: "dotnet-runtime", claim_id: "dotnet-answer", passed: runtimePass }],
      }],
    },
    confidence: runtimeObserved ? "observed" : "derived",
    authority: "controlled-replay",
    limitations: [
      "The runtime proof covers the declared finite command-line inputs only.",
      "Managed member comparison includes build-local metadata and does not establish whole-program equivalence.",
    ],
    evidenceLinks: [original.evidence_id, originalMembers.evidence_id, candidate.evidence_id, candidateMembers.evidence_id, comparison.evidence_id],
  },
);

const bundle = createEvidenceBundle([original, originalMembers, candidate, candidateMembers, comparison, proof], []);
fs.mkdirSync(outputDir, { recursive: true });
const write = (name, value) => fs.writeFileSync(path.join(outputDir, name), `${JSON.stringify(value, null, 2)}\n`, "utf8");
write("rea-dotnet-proof-evidence.json", { ok: true, data: proof });
write("rea-dotnet-bundle.json", bundle);
write("dotnet-acceptance.json", {
  version: 1,
  operation: "dotnet-reconstruction",
  status: !runtimeObserved ? "unknown" : runtimePass ? "pass" : "fail",
  original_evidence_id: original.evidence_id,
  original_members_evidence_id: originalMembers.evidence_id,
  candidate_evidence_id: candidate.evidence_id,
  candidate_members_evidence_id: candidateMembers.evidence_id,
  comparison_evidence_id: comparison.evidence_id,
  proof_evidence_id: proof.evidence_id,
  static_summary: comparison.normalized_result?.summary ?? null,
  runtime: traces,
  cleanup: { status: "observed", scope: "Bounded child invocations returned; descendant containment is not qualified." },
});
write("dotnet-ledger-input.json", {
  manifest: {
    bindings: [{
      owner: { symbol: "Answer", module_path: "Program.cs", owner_sha256: original.subject.digest.sha256 },
      obligation_id: "dotnet-answer",
      parser_type: null,
      original_cases: [{ location: "Program.Answer", kind: "positive", evidence_id: proof.evidence_id }],
      fixtures: [{ fixture_id: "dotnet-answer-fixture", case_kind: "positive", authority: "integration", evidence_ids: [proof.evidence_id] }],
      verifier: {
        verifier_id: "dotnet-runtime",
        enumerated_obligation_ids: ["dotnet-answer"],
        command: "dotnet ReverseFixture.dll <input>",
        status: runtimePass ? "pass" : "fail",
        result_evidence_id: proof.evidence_id,
        authority: "integration",
        claim_id: "dotnet-answer",
        nondeterminism: { mode: "finite-traces", specification: "Answer(value) trims, uppercases invariantly and prefixes rf:" },
      },
    }],
    contradictions: [],
  },
  evidence_bundle: bundle,
  reviewed_obligations: [{
    disposition: "active",
    required: true,
    family: "managed-method",
    residual_unknown_ids: [],
    unavailable_authority: [],
    requires_parser_type: false,
    application_layer: "application",
    obligation_version: 1,
    obligation_id: "dotnet-answer",
    required_fixture_authority: "integration",
    required_verifier_authority: "integration",
    required_case_kinds: ["positive"],
    dependency_obligation_ids: [],
    target: { semantic_node_id: null, location: "Program.Answer", artifact_sha256: original.subject.digest.sha256, application_node_id: null },
    required_next_evidence: [],
    review_evidence_ids: [proof.evidence_id],
    required_original_authority: "runtime",
    title: "Managed Answer method matches the observed finite runtime traces",
  }],
});
console.log(JSON.stringify({ status: runtimePass ? "pass" : "fail", original: original.evidence_id, candidate: candidate.evidence_id, comparison: comparison.evidence_id, proof: proof.evidence_id }));
process.exitCode = !runtimeObserved ? 2 : runtimePass ? 0 : 1;
