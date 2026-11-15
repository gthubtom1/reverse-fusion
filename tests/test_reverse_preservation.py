"""Regression checks for the actual enhanced Reverse handoff and dependencies."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree, ignore_patterns

from reverse_fusion.case_bridge import dry_run_route
from reverse_fusion.contracts import check_contracts

ROOT = Path(__file__).resolve().parents[1]


class ReversePreservationTests(unittest.TestCase):
    def test_all_inherited_routing_expectations_are_preserved(self):
        cases = json.loads((ROOT / "skills/tests/routing-benchmark.json").read_text(encoding="utf-8-sig"))["cases"]
        self.assertEqual(len(cases), 192)
        for case in cases:
            with self.subTest(hint=case["hint"]):
                result = dry_run_route(case["hint"], source="local")
                self.assertEqual(result["primary_id"], case["expect"])
                self.assertEqual(result["status"], "local-route-pass")

    def test_hard_targets_carry_their_real_specialist_resources(self):
        cases = (
            ("R0", "VMProtect packed PE anti-debug", "skills/reverse-engineering/anti-analysis.md"),
            ("R1", "APK dynamic DEX anti-Frida", "skills/apk-reverse/references/high-difficulty-android-playbook.md"),
            ("R3", "JavaScript obfuscation", "skills/js-reverse/references/high-difficulty-js-wasm-playbook.md"),
            ("R5", ".NET obfuscated assembly", "skills/dotnet-reverse/references/obfuscators.md"),
            ("R6", "IDA OLLVM", "skills/reverse-engineering/references/ollvm-deobfuscation.md"),
        )
        for primary, hint, resource in cases:
            with self.subTest(primary=primary):
                result = dry_run_route(hint, source="local", primary=primary)
                self.assertTrue(result["hard_target"])
                self.assertIn("RULES.md", result["required_reads"])
                self.assertIn(resource, result["required_reads"])
                self.assertEqual(result["missing_support"], [])

    def test_plain_route_stays_light_and_ctf_sidecar_is_reachable(self):
        plain = dry_run_route("APK manifest", source="local")
        self.assertFalse(plain["hard_target"])
        self.assertEqual(plain["required_reads"], ["RULES.md", "skills/apk-reverse/SKILL.md"])
        ctf = dry_run_route("CTF AWD", source="local", primary="R41")
        self.assertIn("CTF-Sandbox-Orchestrator/ctf-sandbox-orchestrator/SKILL.md", ctf["required_reads"])
        self.assertEqual(ctf["missing_support"], [])

    def test_missing_or_modified_support_is_not_reported_available(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            copytree(ROOT, root, ignore=ignore_patterns(".git", ".venv", "state", "work", "__pycache__", "*.egg-info"))
            spec = importlib.util.spec_from_file_location("isolated_reverse_router", root / "components/reverse-core/router.py")
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            try:
                spec.loader.exec_module(module)
                resource = root / "skills/reverse-engineering/anti-analysis.md"
                original = resource.read_bytes()
                resource.unlink()
                result = module.route("VMProtect anti-debug").to_dict()
                self.assertEqual(result["status"], "unavailable")
                self.assertIn("skills/reverse-engineering/anti-analysis.md", result["missing_support"])
                self.assertEqual(check_contracts(root)["status"], "fail")
                resource.write_bytes(original + b"\nunrecorded drift\n")
                result = check_contracts(root)
                self.assertEqual(result["status"], "fail")
                self.assertIn("hash mismatch", result["checks"][-1]["detail"])
                resource.write_bytes(original)
                manifest_path = root / "components/reverse-core/preservation.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest["commit"] = "0" * 40
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                result = check_contracts(root)
                self.assertEqual(result["status"], "fail")
                self.assertIn("source identity", result["checks"][-1]["detail"])
            finally:
                sys.modules.pop(spec.name, None)


if __name__ == "__main__":
    unittest.main()
