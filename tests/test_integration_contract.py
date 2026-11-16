"""Fixed responsibility and provenance checks using small inert repositories."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from reverse_fusion.contracts import ContractError, check_contracts, check_integration_contract
from reverse_fusion.release import check_release


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "components/integration-contract.json"
PIN_FILES = (
    "SOURCE-MANIFEST.json", "components/official/manifest.json",
    "vendor/rea/manifest.json", "vendor/spec-kit/manifest.json",
    "components/craft-mcp/manifest.json", "components/craft-native/manifest.json",
    "components/craft-bounded/bundle-manifest.json",
)
# Intentionally independent of both the editable manifest and validator constant.
REQUIRED_IDS = {
    "reverse-routing", "reverse-case-continuation", "reverse-domain-methods",
    "rea-official-methods", "rea-mcp-cli-providers", "rea-evidence-persistence",
    "rea-comparison-proof-ledger", "spec-official-discovery", "spec-evidence-native-gate",
    "spec-converge-feedback", "craft-tools-modes-plugins", "craft-durable-case-project",
    "craft-provider-paths", "craft-native-writer", "craft-host-build-orchestration",
    "craft-host-questions-consent", "craft-assets-and-3d", "independent-comparison",
    "failure-cleanup-recovery", "deployment-ownership",
}


class IntegrationContractTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve() / "repo"
        self.data = json.loads((ROOT / CONTRACT).read_text(encoding="utf-8"))
        self.pins = {name: json.loads((ROOT / name).read_text(encoding="utf-8"))
                     for name in PIN_FILES}
        # These are declaration tests, so source bodies need not be copied.
        # Required/check references are inert nonempty files; concrete identity
        # records remain actual repository JSON. No runtime/download trees.
        references = {name for row in self.data["responsibilities"] for name in row["required_files"]}
        references.update(check["path"] for row in self.data["responsibilities"] for check in row["checks"])
        for name in references:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("inert static declaration fixture\n", encoding="utf-8")
        for name, data in self.pins.items():
            self.write(name, data)
        self.write(CONTRACT, self.data)

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def rejected(self, data, message):
        self.write(CONTRACT, data)
        with self.assertRaisesRegex(ContractError, message):
            check_integration_contract(self.root)

    def test_actual_repository_contract_passes_without_claiming_execution(self):
        result = check_integration_contract(ROOT)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["responsibilities"], 20)
        self.assertEqual(result["roles"], ["craft", "host", "rea", "reverse", "spec"])
        self.assertEqual(result["runtime_acceptance"], "not-evaluated")
        self.assertEqual({row["id"] for row in self.data["responsibilities"]}, REQUIRED_IDS)

    def test_fresh_static_tree_does_not_require_or_execute_downloaded_sources(self):
        for name in ("vendor/rea/package", "vendor/spec-kit/upstream", "vendor/craft/mcp-upstream"):
            self.assertFalse((self.root / name).exists())
        with patch("subprocess.run", side_effect=AssertionError("static contracts must not execute providers")):
            result = check_integration_contract(self.root)
        self.assertEqual(result["responsibilities"], 20)
        self.assertGreaterEqual(result["required_file_references"], 60)
        self.assertGreaterEqual(result["declared_checks"], 40)

    def test_deleting_or_renaming_a_fixed_responsibility_cannot_redefine_completion(self):
        for mutation in ("delete", "rename", "extra", "duplicate"):
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.data)
                rows = data["responsibilities"]
                if mutation == "delete":
                    rows.pop()
                elif mutation == "rename":
                    rows[0]["id"] = "replacement-routing"
                elif mutation == "extra":
                    row = copy.deepcopy(rows[0])
                    row["id"] = "extra-responsibility"
                    rows.append(row)
                else:
                    rows.append(copy.deepcopy(rows[0]))
                self.rejected(data, "20 fixed responsibility IDs|duplicate id")

    def test_component_and_host_lifecycle_roles_cannot_be_reassigned(self):
        for role, replacement in (("reverse", "host"), ("rea", "craft"), ("spec", "reverse"),
                                  ("craft", "rea"), ("host", "spec")):
            with self.subTest(role=role):
                data = copy.deepcopy(self.data)
                row = next(item for item in data["responsibilities"] if item["upstream_component"] == role)
                row["upstream_component"] = replacement
                self.rejected(data, "wrong component role")
        data = copy.deepcopy(self.data)
        del data["source_pins"]["host"]
        self.rejected(data, "source roles")

    def test_each_responsibility_requires_owner_entry_conditions_and_counterexamples(self):
        for field, invalid in (("original_role", ""), ("fusion_owner", " \n"),
                               ("entry_points", []), ("completion_condition", None),
                               ("negative_cases", []), ("acceptance_boundary", ""),
                               ("upstream_paths", []), ("required_files", []), ("checks", [])):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data["responsibilities"][0][field] = invalid
                self.rejected(data, "non-empty")

    def test_check_propositions_require_safe_file_kind_and_specific_assertion(self):
        for field, invalid in (("path", None), ("kind", "pass"), ("kind", []),
                               ("assertion", " "), ("assertion", True)):
            with self.subTest(field=field, value=invalid):
                data = copy.deepcopy(self.data)
                data["responsibilities"][0]["checks"][0][field] = invalid
                self.rejected(data, "unsafe path|kind is invalid|non-empty string")

    def test_runtime_pass_flags_are_not_part_of_the_static_contract_schema(self):
        data = copy.deepcopy(self.data)
        data["status"] = "pass"
        self.rejected(data, "identity/schema/fields")
        data = copy.deepcopy(self.data)
        data["responsibilities"][0]["complete"] = True
        self.rejected(data, "responsibility fields")
        data = copy.deepcopy(self.data)
        data["schema_version"] = True
        self.rejected(data, "identity/schema/fields")

    def test_missing_or_empty_required_and_check_files_block_the_contract(self):
        required = self.data["responsibilities"][0]["required_files"][0]
        path = self.root / required
        path.unlink()
        with self.assertRaisesRegex(ContractError, "required_files file missing or empty"):
            check_integration_contract(self.root)
        path.write_text("inert source declaration", encoding="utf-8")
        path = self.root / self.data["responsibilities"][0]["checks"][1]["path"]
        path.write_bytes(b"")
        with self.assertRaisesRegex(ContractError, "checks file missing or empty"):
            check_integration_contract(self.root)

    def test_all_path_declarations_reject_portable_escapes(self):
        bad_paths = ("../outside", "safe/../../outside", "C:/outside", "/outside", "a\\..\\outside",
                     "safe//alias", "safe/./alias", "stream:payload")
        for field in ("required_files", "checks", "upstream_paths", "pin_manifest", "reference_root"):
            for invalid in bad_paths:
                with self.subTest(field=field, path=invalid):
                    data = copy.deepcopy(self.data)
                    if field == "checks":
                        data["responsibilities"][0][field][0]["path"] = invalid
                    elif field in {"required_files", "upstream_paths"}:
                        data["responsibilities"][0][field][0] = invalid
                    else:
                        data["source_pins"]["rea"][field] = invalid
                    self.rejected(data, "unsafe path")

    def test_resolved_escape_is_rejected_before_outside_file_access(self):
        # Exercise the resolved-path guard without requiring Windows symlink
        # privileges: model the filesystem resolution of one escaping link.
        name = self.data["responsibilities"][0]["required_files"][0]
        link = self.root / name
        outside = self.root.parent / "outside.txt"
        actual_resolve = Path.resolve

        def resolve(path, *args, **kwargs):
            if path == link:
                return outside
            return actual_resolve(path, *args, **kwargs)

        with patch.object(Path, "resolve", resolve):
            with self.assertRaisesRegex(ContractError, "escapes its root"):
                check_integration_contract(self.root)
        self.assertFalse(outside.exists())

    def test_source_pins_must_match_concrete_current_manifests(self):
        mutations = (
            ("SOURCE-MANIFEST.json", lambda p: p["components"][0].update(commit="a" * 40)),
            ("vendor/spec-kit/manifest.json", lambda p: p.update(commit="b" * 40)),
            ("vendor/spec-kit/manifest.json", lambda p: p.update(version="0.0.0")),
            ("vendor/rea/manifest.json", lambda p: p.update(version="6.9.99")),
            ("components/craft-native/manifest.json", lambda p: p["upstream"].update(commit="c" * 40)),
            ("components/craft-mcp/manifest.json", lambda p: p["upstream"].update(version="0.0.0")),
            ("components/craft-mcp/manifest.json", lambda p: p["upstream"].update(local_source="vendor/craft/other")),
        )
        for name, mutate in mutations:
            with self.subTest(manifest=name):
                data = copy.deepcopy(self.pins[name])
                mutate(data)
                self.write(name, data)
                with self.assertRaisesRegex(ContractError, "pin.*drift|pins disagree|source root differs"):
                    check_integration_contract(self.root)
                self.write(name, self.pins[name])

    def test_safe_but_wrong_pin_manifest_cannot_replace_the_source_authority(self):
        data = copy.deepcopy(self.data)
        data["source_pins"]["rea"]["pin_manifest"] = "vendor/spec-kit/manifest.json"
        self.rejected(data, "source pin mapping drift")
        (self.root / "vendor/spec-kit/manifest.json").unlink()
        with self.assertRaisesRegex(ContractError, "file missing or empty"):
            check_integration_contract(self.root)

    def test_rea_original_skill_and_all_method_source_pins_are_required(self):
        name = "vendor/rea/manifest.json"
        original = self.pins[name]
        for mutation in ("missing", "one-removed", "wrong-path", "bad-digest"):
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(original)
                methods = data["method_files_sha256"]
                key = next(iter(methods))
                if mutation == "missing":
                    data.pop("method_files_sha256")
                elif mutation == "one-removed":
                    methods.pop(key)
                elif mutation == "wrong-path":
                    methods["package/../../outside.md"] = methods.pop(key)
                else:
                    methods[key] = "a" * 63
                self.write(name, data)
                with self.assertRaisesRegex(ContractError, "REA method source pin"):
                    check_integration_contract(self.root)

    def test_existing_contract_and_release_gate_reject_missing_responsibility(self):
        data = copy.deepcopy(self.data)
        data["responsibilities"].pop()
        self.write(CONTRACT, data)
        result = check_contracts(self.root)
        self.assertEqual(result["status"], "fail")
        self.assertIn("20 fixed responsibility IDs", result["checks"][-1]["detail"])
        release = check_release(self.root)
        self.assertEqual(release["status"], "blocked")
        gates = [gate for gate in release["checks"] if gate["id"] == "repository-contracts"]
        self.assertEqual(len(gates), 1)
        self.assertEqual(gates[0]["status"], "fail")
        self.assertIn("20 fixed responsibility IDs", gates[0]["detail"][-1]["detail"])


if __name__ == "__main__":
    unittest.main()
