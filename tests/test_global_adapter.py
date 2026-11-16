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
    agents_block,
    ADAPTER_STATE,
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

    def test_exact_roundtrip_of_existing_instructions_and_checkout_migration(self):
        originals = [b'', b'# User instructions\r\n\r\n- Preserve this.  \r\n\r\n',
                     b'# No newline and trailing spaces  ', b'\xef\xbb\xbf# UTF-8 BOM\r\n']
        for original in originals:
            with self.subTest(original=original), tempfile.TemporaryDirectory() as directory:
                home, old, new = (Path(directory)/name for name in ('home', 'old', 'new'))
                agents = home/'.codex/AGENTS.md'
                agents.parent.mkdir(parents=True)
                agents.write_bytes(original)
                install_global_adapter(old, home)
                self.assertTrue(agents.read_bytes().startswith(original))
                once = agents.read_bytes()
                install_global_adapter(old, home)
                self.assertEqual(agents.read_bytes(), once)
                install_global_adapter(new, home)
                migrated = agents.read_bytes()
                remove_global_adapter(home, repo_root=old)
                self.assertEqual(agents.read_bytes(), migrated)
                remove_global_adapter(home, repo_root=new)
                self.assertEqual(agents.read_bytes(), original)

    def test_new_instructions_file_is_removed_and_later_user_suffix_is_kept(self):
        with tempfile.TemporaryDirectory() as directory:
            home, repo = Path(directory)/'home', Path(directory)/'repo'
            paths = adapter_paths(home)
            install_global_adapter(repo, home)
            remove_global_adapter(home, repo_root=repo)
            self.assertFalse(paths['agents'].exists())
            install_global_adapter(repo, home)
            suffix = b'\r\n# User suffix\r\n- Preserve exact bytes.  '
            with paths['agents'].open('ab') as stream:
                stream.write(suffix)
            remove_global_adapter(home, repo_root=repo)
            self.assertEqual(paths['agents'].read_bytes(), suffix)

    def test_legacy_markers_preserve_exact_prefix_and_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            home, repo = Path(directory)/'home', Path(directory)/'repo'
            paths = adapter_paths(home)
            paths['agents'].parent.mkdir(parents=True)
            prefix, suffix = b'\xef\xbb\xbf# Existing user text  \r\n', b'\r\n\r\n- User suffix.  \r\n'
            legacy = agents_block(repo).replace('\n', '\r\n').encode('utf-8')
            paths['agents'].write_bytes(prefix + legacy + suffix)
            install_global_adapter(repo, home)
            updated = paths['agents'].read_bytes()
            self.assertTrue(updated.startswith(prefix))
            self.assertTrue(updated.endswith(suffix))
            remove_global_adapter(home, repo_root=repo)
            self.assertEqual(paths['agents'].read_bytes(), prefix + suffix)

    def test_changed_managed_instructions_or_metadata_refuse_removal_before_writes(self):
        for change in ('instructions', 'metadata'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                home, repo = Path(directory)/'home', Path(directory)/'repo'
                paths = adapter_paths(home)
                install_global_adapter(repo, home)
                payload = paths['agents'].read_bytes()
                modified = (payload.replace(b'Keep the current project', b'Changed: keep the current project')
                            if change == 'instructions' else payload.replace(ADAPTER_STATE, ADAPTER_STATE+b'{broken}'))
                paths['agents'].write_bytes(modified)
                before = {path: path.read_bytes() for path in paths.values()}
                with self.assertRaisesRegex(ValueError, 'changed|malformed'):
                    remove_global_adapter(home, repo_root=repo)
                self.assertEqual({path: path.read_bytes() for path in before}, before)


if __name__ == "__main__":
    unittest.main()
