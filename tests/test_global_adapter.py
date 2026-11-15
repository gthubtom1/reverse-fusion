import tempfile
import unittest
from pathlib import Path

from reverse_fusion.global_adapter import (
    MARKER_END,
    MARKER_START,
    install_global_adapter,
    remove_global_adapter,
)


class GlobalAdapterTests(unittest.TestCase):
    def test_install_updates_only_managed_codex_surfaces(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            repo = Path(directory) / "reverse-fusion"
            agents = home / ".codex" / "AGENTS.md"
            agents.parent.mkdir(parents=True)
            agents.write_text("# Existing instructions\n\n- Keep project files local.\n", encoding="utf-8")

            result = install_global_adapter(repo, home=home)
            skill = Path(result["skill"])
            self.assertTrue(skill.is_file())
            self.assertIn(repo.as_posix(), skill.read_text(encoding="utf-8"))
            text = agents.read_text(encoding="utf-8")
            self.assertIn("# Existing instructions", text)
            self.assertIn(MARKER_START, text)
            self.assertIn(MARKER_END, text)

            # A second install replaces the managed block instead of duplicating it.
            install_global_adapter(repo / "moved", home=home)
            updated = agents.read_text(encoding="utf-8")
            self.assertEqual(updated.count(MARKER_START), 1)
            self.assertIn((repo / "moved").as_posix(), updated)

    def test_remove_preserves_unrelated_global_instructions(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            repo = Path(directory) / "reverse-fusion"
            install_global_adapter(repo, home=home)
            agents = home / ".codex" / "AGENTS.md"
            agents.write_text(agents.read_text(encoding="utf-8") + "\n- User addition.\n", encoding="utf-8")

            result = remove_global_adapter(home=home)
            self.assertFalse((home / ".agents" / "skills" / "reverse-fusion" / "SKILL.md").exists())
            self.assertIn("User addition", agents.read_text(encoding="utf-8"))
            self.assertFalse(result["enabled"])


if __name__ == "__main__":
    unittest.main()
