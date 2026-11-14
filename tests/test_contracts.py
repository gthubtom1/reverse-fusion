# Minimal static contract tests
import json
import tempfile
import unittest
from pathlib import Path
from shutil import copytree

from reverse_fusion.adapters import CraftAdapter, LocalBoundedWorker, spec_pointer
from reverse_fusion.builder import HostBuilder
from reverse_fusion.case_bridge import build_case_pointer, dry_run_route
from reverse_fusion.contracts import ContractError, check_contracts, validate_candidate_result, validate_external_baseline, validate_handoff
from reverse_fusion.host import detect_hosts, read_handshake_record
from reverse_fusion.vertical import correct_candidate, evaluate_console, wrong_candidate

ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_contracts_pass(self):
        result = check_contracts(ROOT)
        self.assertEqual(result["status"], "pass", result)

    def test_manifest_is_single_repository(self):
        data = json.loads((ROOT / "components/official/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data["project"], "reverse-fusion")
        self.assertGreaterEqual(len(data["components"]), 4)

    def test_unknown_manifest_field_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            copytree(ROOT, root)
            path = root / "components/official/manifest.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["unexpected"] = True
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(check_contracts(root)["status"], "fail")

    def test_source_manifest_drift_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            copytree(ROOT, root)
            path = root / "SOURCE-MANIFEST.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["components"].pop()
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(check_contracts(root)["status"], "fail")

    def test_duplicate_and_path_boundary_rejected(self):
        for mutation in ("duplicate", "traversal", "absolute"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / "repo"
                copytree(ROOT, root)
                path = root / "components/official/manifest.json"
                data = json.loads(path.read_text(encoding="utf-8"))
                if mutation == "duplicate":
                    data["components"].append(dict(data["components"][0]))
                else:
                    data["components"][0]["path"] = "../escape" if mutation == "traversal" else str(root / "outside")
                path.write_text(json.dumps(data), encoding="utf-8")
                self.assertEqual(check_contracts(root)["status"], "fail")

    def test_hash_and_version_contracts(self):
        with self.assertRaises(ContractError):
            validate_external_baseline({"version": 1, "root": "x", "bundle_sha256": "bad", "artifacts": []})
        with self.assertRaises(ContractError):
            validate_candidate_result({"version": 2, "disposition": "candidate", "tasks": [], "checks": [], "cleanup": {}})
        with self.assertRaises(ContractError):
            validate_handoff({"version": 1})

    def test_vertical_slice_pass_fail_unknown(self):
        passed = evaluate_console(correct_candidate, ["a", "b"])
        failed = evaluate_console(wrong_candidate, ["a", "b"])
        unknown = evaluate_console(None, ["a", "b"], evidence=False)
        self.assertEqual(passed.status, "pass")
        self.assertEqual(failed.status, "fail")
        self.assertEqual(unknown.status, "unknown")

    def test_case_spec_and_craft_boundaries(self):
        pointer = build_case_pointer(Path("work/case"), "skills/reconstruction/SKILL.md", "reconstruction")
        self.assertEqual(pointer.route_owner, "reverse.native-router")
        self.assertEqual(spec_pointer("specs/demo", "console", ["T-001"], ["E-CONSOLE-001"]).feature, "console")
        adapter = CraftAdapter("abc123", ("0001.patch",))
        unsupported = adapter.run(baseline={"bundle_sha256": "a" * 64}, tasks=["T-001"], research_ref="E-CONSOLE-001")
        self.assertEqual(unsupported["disposition"], "unsupported")
        candidate = CraftAdapter(
            "abc123",
            ("0001.patch",),
            backend="test",
            capabilities=CraftAdapter.REQUIRED_CAPABILITIES,
        ).run(
            baseline={"bundle_sha256": "a" * 64},
            tasks=["T-001"],
            writer=lambda tasks: {"tasks": tasks},
            model_id="fixture-model",
            research_ref="E-CONSOLE-001",
        )
        self.assertEqual(validate_candidate_result(candidate)["disposition"], "candidate")

    def test_local_route_does_not_require_external_receipt(self):
        result = dry_run_route("APK reverse reconstruction", source="local")
        self.assertEqual(result["status"], "local-route-pass")
        self.assertEqual(result["source"], "local")
        self.assertEqual(result["primary_id"], "R1")
        self.assertTrue((ROOT / result["primary"]).is_file())

    def test_external_route_is_explicitly_unavailable_when_uninstalled(self):
        result = dry_run_route("reconstruction implementation", source="external")
        self.assertIn(result["status"], {"unavailable", "external-route-pass"})
        if result["status"] == "unavailable":
            self.assertEqual(result["source"], "external")

    def test_craft_gate_and_host_discovery(self):
        gate = CraftAdapter.six_tool_gate(["prepare", "build"])
        self.assertEqual(gate["status"], "fail")
        hosts = detect_hosts()
        self.assertIn("codex", hosts["hosts"])
        self.assertFalse(hosts["global_config_mutation"])

    def test_host_handshake_record_is_typed_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(read_handshake_record(root)["status"], "unrecorded")
            state = root / "state"
            state.mkdir()
            (state / "host-handshakes.json").write_text(
                json.dumps({
                    "config_mutation": False,
                    "probes": [{"id": "codex", "status": "pass", "version": "x", "exit_code": 0}],
                }),
                encoding="utf-8",
            )
            result = read_handshake_record(root)
            self.assertEqual(result["status"], "recorded")
            self.assertEqual(result["probes"][0]["status"], "pass")

    def test_local_bounded_worker_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            source = workspace / "source.txt"
            source.write_text("candidate", encoding="utf-8")
            result = LocalBoundedWorker(workspace).run(
                source=source,
                output_relative="state/implementation/candidate.txt",
                tasks=["T-001"],
                research_ref="E-CONSOLE-001",
            )
            self.assertEqual(result["disposition"], "candidate")
            self.assertEqual(result["cleanup"]["status"], "verified")
            self.assertTrue((workspace / "state/implementation/candidate.txt").is_file())

    def test_host_builder_does_not_select_a_model_and_fails_closed_without_host(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            builder = HostBuilder(workspace, host="missing-host")
            result = builder.run(
                baseline={"bundle_sha256": "a" * 64},
                tasks=["T-001"],
                research_ref="E-001",
                output_relative="candidate.txt",
                prompt="write the candidate",
            )
            self.assertEqual(result["disposition"], "unsupported")
            invocation = HostBuilder(workspace, host="codex")._invocation("codex", "codex", "prompt")
            self.assertNotIn("--model", invocation.argv)


if __name__ == "__main__":
    unittest.main()
