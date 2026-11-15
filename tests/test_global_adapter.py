import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from reverse_fusion.global_adapter import (
    MARKER_END,
    MARKER_START,
    install_global_adapter,
    remove_global_adapter,
    adapter_paths,
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

    def test_uninstalling_old_checkout_cannot_remove_new_shared_pointer(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / 'home'
            old, new = Path(directory) / 'old', Path(directory) / 'new'
            install_global_adapter(old, home=home)
            result = install_global_adapter(new, home=home)
            remove_global_adapter(home=home, repo_root=old)
            self.assertIn(new.as_posix(), Path(result['skill']).read_text(encoding='utf-8'))
            self.assertIn(new.as_posix(), Path(result['agents']).read_text(encoding='utf-8'))

    def test_malformed_markers_fail_without_replacing_existing_user_files(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / 'home'
            repo = Path(directory) / 'repo'
            result = install_global_adapter(repo, home=home)
            skill, agents = Path(result['skill']), Path(result['agents'])
            original = skill.read_bytes()
            broken = '# User instructions\n' + MARKER_START + '\nunfinished block\n'
            agents.write_text(broken, encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'markers'):
                install_global_adapter(repo / 'other', home=home)
            self.assertEqual(skill.read_bytes(), original)
            self.assertEqual(agents.read_text(encoding='utf-8'), broken)

    def test_custom_codex_home_is_respected(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {'CODEX_HOME': directory}):
            self.assertEqual(adapter_paths()['agents'], Path(directory) / 'AGENTS.md')


if __name__ == "__main__":
    unittest.main()
