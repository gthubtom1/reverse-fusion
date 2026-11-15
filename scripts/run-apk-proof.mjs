import fs from "node:fs";
import path from "node:path";
import { readEvidence, assertArtifact, sha256, createEvidence, bundle as createEvidenceBundle } from "./proof-support.mjs";

const [originalPackagePath, originalClassPath, candidatePackagePath, candidateClassPath, outputDir] = process.argv.slice(2);
if (![originalPackagePath, originalClassPath, candidatePackagePath, candidateClassPath, outputDir].every(Boolean)) {
  throw new Error("usage: run-apk-proof.mjs original-package.json original-class.json candidate-package.json candidate-class.json output-dir");
}
const originalPackage = readEvidence(originalPackagePath);
const originalClass = readEvidence(originalClassPath);
const candidatePackage = readEvidence(candidatePackagePath);
const candidateClass = readEvidence(candidateClassPath);
assertArtifact(originalPackage, originalPackage.subject.local_path);
assertArtifact(candidatePackage, candidatePackage.subject.local_path);
if (originalClass.subject.digest.sha256 !== originalPackage.subject.digest.sha256 || candidateClass.subject.digest.sha256 !== candidatePackage.subject.digest.sha256) throw new Error("Package and class Evidence must refer to the same artifact on each side");

const componentProjection = (record) => (record.normalized_result?.components?.items ?? []).map((item) => ({
  kind: item.kind,
  name: item.name,
  exported: item.exported,
  actions: item.actions,
  categories: item.categories,
}));
const methodProjection = (record) => (record.normalized_result?.methods ?? []).map((item) => ({
  name: item.name,
  reported_signature: item.reported_signature,
  dex_descriptor: item.dex_descriptor,
  is_constructor: item.is_constructor,
}));
const packageEqual = originalPackage.normalized_result?.package_name === candidatePackage.normalized_result?.package_name
  && JSON.stringify(componentProjection(originalPackage)) === JSON.stringify(componentProjection(candidatePackage));
const classEqual = originalClass.normalized_result?.class_name === candidateClass.normalized_result?.class_name
  && JSON.stringify(methodProjection(originalClass)) === JSON.stringify(methodProjection(candidateClass))
  && JSON.stringify(originalClass.normalized_result?.fields ?? []) === JSON.stringify(candidateClass.normalized_result?.fields ?? []);
const staticPass = packageEqual && classEqual;
if (!originalClass.normalized_result?.methods?.length || !candidateClass.normalized_result?.methods?.length) throw new Error("Missing class member observations cannot establish static equality");
const comparison = createEvidence(
  undefined,
  { id: "reverse-fusion-apk-comparator", name: "Reverse Fusion APK comparator", version: "1" },
  {
    operation: "compare_android_reconstruction",
    predicateType: "rea.comparison",
    parameters: { class_name: "com.reversefusion.Answer", scope: "manifest-and-class-members" },
    rawResult: {
      package_equal: packageEqual,
      class_equal: classEqual,
      original_package: componentProjection(originalPackage),
      candidate_package: componentProjection(candidatePackage),
      original_methods: methodProjection(originalClass),
      candidate_methods: methodProjection(candidateClass),
    },
    result: {
      summary: { unchanged: staticPass ? 1 : 0, changed: staticPass ? 0 : 1, added: 0, removed: 0, unknown: 0 },
      coverage: { status: "complete-within-inputs" },
      package_equal: packageEqual,
      class_equal: classEqual,
    },
    confidence: "derived",
    authority: "shipped-artifact",
    limitations: [
      "The comparison covers the declared manifest projection and Answer class member inventory only.",
      "Android runtime behavior is not established without a device or emulator capture.",
    ],
    evidenceLinks: [originalPackage.evidence_id, originalClass.evidence_id, candidatePackage.evidence_id, candidateClass.evidence_id],
  },
);

const proof = createEvidence(
  undefined,
  { id: "reverse-fusion-apk-verifier", name: "Reverse Fusion APK verifier", version: "1" },
  {
    operation: "verify_reconstruction_obligations",
    predicateType: "rea.reconstruction-proof",
    parameters: {
      obligation_id: "apk-answer-static",
      fixture_id: "apk-answer-static-fixture",
      verifier_id: "apk-static-comparison",
      toolchain: "jadx-headless-mcp@0.7.1",
      original_sha256: sha256(originalPackage.subject.local_path),
      candidate_sha256: sha256(candidatePackage.subject.local_path),
      verifier_sha256: sha256(new URL(import.meta.url)),
    },
    rawResult: {
      operation: "apk-answer-static",
      static: { status: staticPass ? "pass" : "fail", comparison_evidence_id: comparison.evidence_id },
      android_runtime: { status: "unknown", reason: "No adb device or emulator was available on this host" },
    },
    result: {
      bindings: [{
        obligation_id: "apk-answer-static",
        obligation_version: 1,
        owner_sha256: originalPackage.subject.digest.sha256,
        fixtures: [{ fixture_id: "apk-answer-static-fixture", case_kind: "positive", passed: staticPass }],
        verifiers: [{ verifier_id: "apk-static-comparison", claim_id: "apk-answer-static", passed: staticPass }],
      }],
    },
    confidence: "observed",
    authority: "controlled-replay",
    limitations: [
      "The proof establishes static APK/package and DEX member equivalence within the selected inputs.",
      "Android device/emulator runtime remains unknown and is retained as a separate acceptance field.",
    ],
    evidenceLinks: [originalPackage.evidence_id, originalClass.evidence_id, candidatePackage.evidence_id, candidateClass.evidence_id, comparison.evidence_id],
  },
);

const bundle = createEvidenceBundle([originalPackage, originalClass, candidatePackage, candidateClass, comparison, proof], []);
fs.mkdirSync(outputDir, { recursive: true });
const write = (name, value) => fs.writeFileSync(path.join(outputDir, name), `${JSON.stringify(value, null, 2)}\n`, "utf8");
write("rea-apk-comparison.json", { ok: true, data: comparison });
write("rea-apk-proof-evidence.json", { ok: true, data: proof });
write("rea-apk-bundle.json", bundle);
write("apk-acceptance.json", {
  version: 1,
  operation: "apk-reconstruction",
  status: staticPass ? "pass" : "fail",
  original_package_evidence_id: originalPackage.evidence_id,
  original_class_evidence_id: originalClass.evidence_id,
  candidate_package_evidence_id: candidatePackage.evidence_id,
  candidate_class_evidence_id: candidateClass.evidence_id,
  comparison_evidence_id: comparison.evidence_id,
  proof_evidence_id: proof.evidence_id,
  build: { status: "pass", artifact: candidatePackage.subject.local_path },
  run: { status: "unknown", reason: "No adb device or emulator was available on this host" },
  cleanup: { status: "observed", scope: "REA inspection invocations returned; this adapter starts no target application." },
});
write("apk-ledger-input.json", {
  manifest: {
    bindings: [{
      owner: { symbol: "com.reversefusion.Answer", module_path: "classes.dex", owner_sha256: originalPackage.subject.digest.sha256 },
      obligation_id: "apk-answer-static",
      parser_type: null,
      original_cases: [{ location: "com.reversefusion.Answer", kind: "positive", evidence_id: originalClass.evidence_id }],
      fixtures: [{ fixture_id: "apk-answer-static-fixture", case_kind: "positive", authority: "integration", evidence_ids: [proof.evidence_id] }],
      verifier: {
        verifier_id: "apk-static-comparison",
        enumerated_obligation_ids: ["apk-answer-static"],
        command: "REA inspect-android-class + bounded APK comparison",
        status: staticPass ? "pass" : "fail",
        result_evidence_id: proof.evidence_id,
        authority: "integration",
        claim_id: "apk-answer-static",
        nondeterminism: { mode: "total-order", specification: "manifest and Answer class member projections are equal" },
      },
    }],
    contradictions: [],
  },
  evidence_bundle: bundle,
  reviewed_obligations: [{
    disposition: "active",
    required: true,
    family: "android-class",
    residual_unknown_ids: [],
    unavailable_authority: [],
    requires_parser_type: false,
    application_layer: "application",
    obligation_version: 1,
    obligation_id: "apk-answer-static",
    required_fixture_authority: "integration",
    required_verifier_authority: "integration",
    required_case_kinds: ["positive"],
    dependency_obligation_ids: [],
    target: { semantic_node_id: null, location: "com.reversefusion.Answer", artifact_sha256: originalPackage.subject.digest.sha256, application_node_id: null },
    required_next_evidence: [],
    review_evidence_ids: [originalClass.evidence_id],
    required_original_authority: "static",
    title: "APK Answer class and manifest projections match the shipped original",
  }],
});
console.log(JSON.stringify({ status: staticPass ? "pass" : "fail", original: originalPackage.evidence_id, candidate: candidatePackage.evidence_id, comparison: comparison.evidence_id, proof: proof.evidence_id }));
process.exitCode = staticPass ? 0 : 1;
