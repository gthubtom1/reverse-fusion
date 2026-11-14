# Minimal static contract tests
import json
import unittest
from pathlib import Path

from reverse_fusion.contracts import check_contracts

ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_contracts_pass(self):
        result = check_contracts(ROOT)
        self.assertEqual(result["status"], "pass", result)

    def test_manifest_is_single_repository(self):
        data = json.loads((ROOT / "components/official/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data["project"], "reverse-fusion")
        self.assertGreaterEqual(len(data["components"]), 4)


if __name__ == "__main__":
    unittest.main()
