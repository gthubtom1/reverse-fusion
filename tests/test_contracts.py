# Minimal static contract tests
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from shutil import copytree as _copytree, ignore_patterns
from unittest.mock import patch

from reverse_fusion.adapters import CraftAdapter, LocalBoundedWorker, spec_pointer
from reverse_fusion.builder import HostBuilder
from reverse_fusion.case_bridge import build_case_pointer, dry_run_route, record_case_pointer, resolve_case_root, workflow_contract
from reverse_fusion.contracts import ContractError, check_contracts, validate_candidate_result, validate_external_baseline, validate_handoff
from reverse_fusion.host import adapter_plan, compare_host_config, detect_hosts, read_handshake_record, snapshot_host_config
from reverse_fusion.vertical import correct_candidate, evaluate_console, wrong_candidate
from reverse_fusion import cli

ROOT = Path(__file__).resolve().parents[1]


def copytree(source, target):
    # Mutate source contracts in isolation without copying downloaded runtimes,
    # venvs or prior case outputs into every test's temporary directory.
    return _copytree(source, target, ignore=ignore_patterns(
        '.git', '.venv', '__pycache__', 'work', 'state', 'node_modules',
        'package', 'windows-x64', 'bin', 'obj', 'build', '*.tgz',
    ))


class ContractTests(unittest.TestCase):
    def test_contracts_pass(self):
        result = check_contracts(ROOT)
        self.assertEqual(result["status"], "pass", result)

    def test_console_fixture_does_not_claim_native_rea_execution(self):
        result = evaluate_console(correct_candidate, ['a'])
        self.assertEqual(result.evidence['provider'], 'reverse-fusion-local')
        self.assertEqual(result.evidence['native_rea_authentication'], 'not-performed')
        self.assertNotEqual(result.evidence['status'], 'ready')

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

    def test_reverse_route_skill_drift_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            copytree(ROOT, root)
            (root / "components" / "reverse-core" / "routes" / "R1.md").unlink()
            self.assertEqual(check_contracts(root)["status"], "fail")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            copytree(ROOT, root)
            descriptor = root / "components" / "reverse-core" / "routes" / "R1.md"
            descriptor.write_text(descriptor.read_text(encoding="utf-8").replace(
                "`skills/apk-reverse/SKILL.md`", "`skills/js-reverse/SKILL.md`"), encoding="utf-8")
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
        blocked = {"version": 1, "disposition": "blocked", "tasks": [], "checks": [], "cleanup": {"status": "blocked"}}
        self.assertEqual(validate_candidate_result(blocked)["disposition"], "blocked")
        with self.assertRaises(ContractError):
            validate_candidate_result({**blocked, "unexpected": True})
        with self.assertRaises(ContractError):
            validate_candidate_result({**blocked, "version": True})
        with self.assertRaises(ContractError):
            validate_candidate_result({**blocked, "candidate_sha256": "bad"})
        baseline = {"version": 1, "root": "original", "bundle_sha256": "a" * 64, "artifacts": [{"path": "a"}]}
        self.assertEqual(validate_external_baseline(baseline)["artifacts"][0]["path"], "a")
        with self.assertRaises(ContractError):
            validate_external_baseline({**baseline, "artifacts": ["a"]})

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
        self.assertEqual(validate_candidate_result(unsupported)["disposition"], "unsupported")
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
        self.assertTrue(result["skill_available"])

    def test_route_exposes_related_domains_and_reconstruction_stage(self):
        result = dry_run_route("reverse a JavaScript app and reconstruct its behavior", source="local")
        self.assertEqual(result["primary_id"], "R3")
        self.assertTrue(result["next_stage"])
        self.assertEqual(result["next_stage"]["id"], "R46")
        self.assertIn("skills/reconstruction/SKILL.md", result["next_stage"]["skill"])
        self.assertTrue(any(item["id"] == "R46" for item in result["related_routes"]))

        mixed = dry_run_route("reverse JavaScript and APK", source="local")
        self.assertEqual(mixed["primary_id"], "R1")
        self.assertTrue(any(item["id"] == "R3" for item in mixed["related_routes"]))
        self.assertTrue(any(item["id"] == "R3" and item["required_reads"] for item in mixed["related_routes"]))

    def test_workflow_contract_keeps_normal_dev_light_and_reconstruction_explicit(self):
        normal = workflow_contract({}, "normal-dev")
        self.assertEqual(normal["stage"], "host-native")
        self.assertEqual(normal["required_artifacts"], [])
        recon = workflow_contract({"primary": "components/reverse-core/routes/R3.md", "next_stage": {"id": "R46"}}, "reconstruction")
        self.assertEqual(recon["stage"], "reconstruction")
        self.assertIn("frozen-spec-tasks", recon["required_artifacts"])
        self.assertEqual(recon["next_stage"], {"id": "R46"})

    def test_bridge_default_is_host_native_and_follow_up_requires_existing_case(self):
        with patch.object(cli, "ROOT", ROOT):
            self.assertEqual(cli.main(["bridge", "--hint", "build a normal web app", "--format", "json"]), 0)
            self.assertEqual(cli.main(["bridge", "--hint", "reimplement behavior", "--format", "json"]), 0)
            with tempfile.TemporaryDirectory() as directory:
                case_root = Path(directory).name
                self.assertEqual(cli.main(["bridge", "--hint", "continue", "--mode", "follow-up", "--case-root", f"work/{case_root}", "--format", "json"]), 2)

    def test_case_pointer_can_be_recorded_inside_repository_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pointer = build_case_pointer(Path("work/case"), "components/reverse-core/routes/R1.md", "analysis")
            path = record_case_pointer(root, pointer)
            self.assertTrue(path.is_file())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["status"], "open")
            pointer2 = build_case_pointer(Path("work/case"), "components/reverse-core/routes/R3.md", "analysis", refs=["E-NEW"])
            record_case_pointer(root, pointer2)
            recorded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(recorded["revision"], 2)
            self.assertEqual(recorded["history"][0]["pointer"]["primary"], "components/reverse-core/routes/R1.md")
            with self.assertRaises(ValueError):
                resolve_case_root(root, "..\\outside")

    def test_case_pointer_rejects_malformed_existing_history_without_overwrite(self):
        malformed_records = (
            "{",
            json.dumps({"schema_version": 1, "status": "open", "pointer": []}),
            json.dumps({"schema_version": 1, "status": "open", "revision": "2", "history": [], "pointer": {}}),
            json.dumps({"schema_version": 1, "status": "open", "revision": 2, "history": "bad", "pointer": {}}),
            json.dumps({"schema_version": 1, "status": "open", "revision": 3, "history": [
                {"revision": 1, "pointer": {"case_root": "work/case", "route_owner": "owner", "primary": "R1", "mode": "analysis", "decision_delta": [], "carry_forward_refs": [], "route_source": "local"}},
            ], "pointer": {"case_root": "work/case", "route_owner": "owner", "primary": "R1", "mode": "analysis", "decision_delta": [], "carry_forward_refs": [], "route_source": "local"}}),
        )
        for payload in malformed_records:
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                case = root / "work" / "case"
                case.mkdir(parents=True)
                path = case / "case.json"
                path.write_text(payload, encoding="utf-8")
                pointer = build_case_pointer(Path("work/case"), "components/reverse-core/routes/R1.md", "analysis")
                with self.assertRaises(ValueError):
                    record_case_pointer(root, pointer)
                self.assertEqual(path.read_text(encoding="utf-8"), payload)

    def test_case_pointer_rejects_external_record_symlink(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            case = root / 'work/case'
            case.mkdir(parents=True)
            external = Path(outside) / 'case.json'
            external.write_text('original', encoding='utf-8')
            try:
                (case / 'case.json').symlink_to(external)
            except OSError as exc:
                self.skipTest(str(exc))
            pointer = build_case_pointer(Path('work/case'), 'components/reverse-core/routes/R1.md', 'analysis')
            with self.assertRaises(ValueError):
                record_case_pointer(root, pointer)
            self.assertEqual(external.read_text(encoding='utf-8'), 'original')

    def test_external_route_is_explicitly_unavailable_when_uninstalled(self):
        result = dry_run_route("reconstruction implementation", source="external")
        self.assertIn(result["status"], {"unavailable", "external-route-pass"})
        if result["status"] == "unavailable":
            self.assertEqual(result["source"], "external")

    def test_external_route_preserves_primary_and_returns_skill_reads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "skills" / "scripts").mkdir(parents=True)
            (root / "skills" / "config").mkdir(parents=True)
            (root / "skills" / "reconstruction").mkdir(parents=True)
            (root / "RULES.md").write_text("rules", encoding="utf-8")
            (root / "skills" / "scripts" / "master-route.ps1").write_text("# fixture", encoding="utf-8")
            (root / "skills" / "reconstruction" / "SKILL.md").write_text("skill", encoding="utf-8")
            (root / "skills" / "config" / "routing.json").write_text(json.dumps({
                "routes": {"R46": {"skill": "reconstruction/SKILL.md"}},
            }), encoding="utf-8")
            completed = subprocess.CompletedProcess([], 0, stdout="PRIMARY -> skills/reconstruction/SKILL.md\n", stderr="")
            with patch("reverse_fusion.case_bridge.platform.system", return_value="Windows"), \
                    patch("reverse_fusion.case_bridge.subprocess.run", return_value=completed) as run:
                result = dry_run_route("reconstruct", root, source="external", primary="R46")
            self.assertEqual(result["status"], "external-route-pass")
            self.assertEqual(result["primary_id"], "R46")
            self.assertEqual(result["skill"], "skills/reconstruction/SKILL.md")
            self.assertEqual(result["required_reads"], ["RULES.md", "skills/reconstruction/SKILL.md"])
            self.assertEqual(result["missing_support"], [])
            self.assertIn("-Primary", run.call_args.args[0])
            self.assertIn("R46", run.call_args.args[0])

    def test_external_route_fails_when_skill_is_missing_or_primary_mismatches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "skills" / "scripts").mkdir(parents=True)
            (root / "skills" / "config").mkdir(parents=True)
            (root / "RULES.md").write_text("rules", encoding="utf-8")
            (root / "skills" / "scripts" / "master-route.sh").write_text("# fixture", encoding="utf-8")
            (root / "skills" / "config" / "routing.json").write_text(json.dumps({
                "routes": {"R1": {"skill": "apk-reverse/SKILL.md"}, "R46": {"skill": "reconstruction/SKILL.md"}},
            }), encoding="utf-8")
            completed = subprocess.CompletedProcess([], 0, stdout="PRIMARY -> skills/apk-reverse/SKILL.md\n", stderr="")
            with patch("reverse_fusion.case_bridge.platform.system", return_value="Linux"), \
                    patch("reverse_fusion.case_bridge.subprocess.run", return_value=completed) as run:
                result = dry_run_route("reconstruct", root, source="external", primary="R46")
            self.assertEqual(result["status"], "unavailable")
            self.assertEqual(result["primary_id"], "R1")
            self.assertIn("skills/apk-reverse/SKILL.md", result["missing_support"])
            self.assertEqual(run.call_args.args[0][:2], ["bash", str(root / "skills" / "scripts" / "master-route.sh")])
            self.assertIn("--primary", run.call_args.args[0])

    def test_craft_gate_and_host_discovery(self):
        gate = CraftAdapter.six_tool_gate(["prepare", "build"])
        self.assertEqual(gate["status"], "fail")
        hosts = detect_hosts()
        self.assertIn("codex", hosts["hosts"])
        self.assertFalse(hosts["global_config_mutation"])
        self.assertEqual(adapter_plan("missing-host")["selected"], [])

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

            # Windows PowerShell 5 may leave a UTF-8 BOM in Out-File output.
            (state / "host-handshakes.json").write_text(
                json.dumps({
                    "config_mutation": False,
                    "probes": [{"id": "codex", "status": "pass", "version": "x", "exit_code": 0}],
                }),
                encoding="utf-8-sig",
            )
            bom_result = read_handshake_record(root)
            self.assertEqual(bom_result["status"], "recorded")
            self.assertEqual(bom_result["probes"][0]["id"], "codex")

    def test_host_config_snapshot_detects_changes_without_reading_contents(self):
        before = {"status": "observed", "files": {"config.toml": "a"}}
        after = {"status": "observed", "files": {"config.toml": "b"}}
        result = compare_host_config(before, after)
        self.assertTrue(result["mutation"])
        self.assertEqual(snapshot_host_config("unknown")["status"], "observed")

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
            self.assertEqual(validate_candidate_result(result)["disposition"], "candidate")
            self.assertEqual(result["cleanup"]["status"], "verified")
            self.assertTrue((workspace / "state/implementation/candidate.txt").is_file())

    def test_windows_absolute_and_traversal_outputs_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            source = workspace / "source.txt"
            source.write_text("candidate", encoding="utf-8")
            for output in ("C:/escape.txt", "..\\escape.txt", "C:\\escape.txt", "C:escape.txt", "\\escape.txt", "."):
                result = LocalBoundedWorker(workspace).run(
                    source=source,
                    output_relative=output,
                    tasks=["T-001"],
                    research_ref="E-CONSOLE-001",
                )
                self.assertEqual(result["disposition"], "needs-scope")

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
            self.assertFalse(HostBuilder._safe_relative("C:/escape.txt"))
            self.assertFalse(HostBuilder._safe_relative("..\\escape.txt"))

    def test_host_builder_rejects_existing_file_mutation_deletion_and_stale_candidate(self):
        class FakeBuilder(HostBuilder):
            mode = "noop"

            def _choose_host(self):
                return "unknown", "fake"

            def _invoke(self, invocation, prompt):
                if self.mode == "mutate":
                    (self.workspace / "protected.txt").write_text("changed", encoding="utf-8")
                    (self.workspace / "candidate.txt").write_text("new", encoding="utf-8")
                elif self.mode == "delete":
                    (self.workspace / "protected.txt").unlink(missing_ok=True)
                    (self.workspace / "candidate.txt").write_text("new", encoding="utf-8")
                return {"status": "pass", "exit_code": 0}

        for mode in ("mutate", "delete", "noop"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                (workspace / "protected.txt").write_text("original", encoding="utf-8")
                (workspace / "candidate.txt").write_text("stale", encoding="utf-8")
                builder = FakeBuilder(workspace)
                builder.mode = mode
                result = builder.run(baseline={"bundle_sha256": "a" * 64}, tasks=["T-001"],
                                     research_ref="E-001", output_relative="candidate.txt", prompt="write")
                self.assertEqual(result["disposition"], "failed")

    def test_host_builder_uses_existing_candidate_as_baseline_and_carries_refine_context(self):
        class FakeBuilder(HostBuilder):
            def __init__(self, workspace):
                super().__init__(workspace)
                self.prompts = []

            def _choose_host(self):
                return "unknown", "fake"

            def _invoke(self, invocation, prompt):
                self.prompts.append(prompt)
                if len(self.prompts) == 1:
                    self.assert_old_candidate()
                    (self.workspace / "candidate.txt").write_text("new", encoding="utf-8")
                return {"status": "pass", "exit_code": 0}

            def assert_old_candidate(self):
                if (self.workspace / "candidate.txt").read_text(encoding="utf-8") != "old":
                    raise AssertionError("pre-existing candidate was removed before invocation")

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "candidate.txt").write_text("old", encoding="utf-8")
            builder = FakeBuilder(workspace)
            result = builder.run(
                baseline={"bundle_sha256": "a" * 64}, tasks=["T-001", "T-002"],
                research_ref="E-001", output_relative="candidate.txt", prompt="bounded original prompt",
            )
            self.assertEqual(result["disposition"], "candidate")
            self.assertEqual((workspace / "candidate.txt").read_text(encoding="utf-8"), "new")
            self.assertEqual(len(builder.prompts), 2)
            for prompt in builder.prompts:
                self.assertIn("T-001", prompt)
                self.assertIn("T-002", prompt)
                self.assertIn("E-001", prompt)
                self.assertIn("bounded original prompt", prompt)
            boundary = next(check for check in result["checks"] if check["id"] == "check")
            self.assertEqual(boundary["status"], "observed")
            self.assertEqual(boundary["business_acceptance"], "not-performed")

    def test_host_builder_rejects_workspace_symlink(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            workspace = Path(directory)
            target = Path(outside) / "target.txt"
            target.write_text("outside", encoding="utf-8")
            try:
                (workspace / "linked.txt").symlink_to(target)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            builder = HostBuilder(workspace, host="missing-host")
            builder._choose_host = lambda: ("unknown", "fake")
            result = builder.run(
                baseline={"bundle_sha256": "a" * 64}, tasks=["T-001"], research_ref="E-001",
                output_relative="candidate.txt", prompt="write",
            )
            self.assertEqual(result["disposition"], "needs-scope")
            self.assertIn("linked.txt", result["result"]["unsafe_entries"])

    def test_candidate_schema_covers_existing_producer_fields(self):
        schema = json.loads((ROOT / "schemas" / "candidate-result-v1.schema.json").read_text(encoding="utf-8"))
        producer_fields = {
            "source_sha256", "candidate_sha256", "task_digest", "model_id", "research_ref", "backend",
            "host", "host_result", "output", "refine_result", "operation", "source", "workspace", "model_selection",
        }
        self.assertTrue(producer_fields <= set(schema["properties"]))
        value = {
            "version": 1, "disposition": "candidate", "tasks": ["T-001"],
            "checks": [{"id": "check", "status": "observed"}], "cleanup": {"status": "verified"},
            "candidate_sha256": "a" * 64, "source_sha256": "b" * 64,
            "operation": "craft", "source": "source.txt", "workspace": "state/build", "model_selection": "host-owned",
        }
        self.assertEqual(validate_candidate_result(value)["disposition"], "candidate")

    def test_handoff_unknown_top_level_field_is_rejected(self):
        valid = {"version": 1, **{key: {} for key in ("case", "original", "implementation", "baseline", "checks", "builder", "owner")}}
        self.assertEqual(validate_handoff(valid)["version"], 1)
        with self.assertRaises(ContractError):
            validate_handoff({**valid, "unexpected": True})


if __name__ == "__main__":
    unittest.main()
