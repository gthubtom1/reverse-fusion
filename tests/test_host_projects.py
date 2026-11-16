import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from reverse_fusion.project_adapter import connect_project
from reverse_fusion.spec_support import generated_workflow, PHASES
from reverse_fusion.case_bridge import build_case_pointer, record_case_pointer, workflow_contract


ROOT = Path(__file__).resolve().parents[1]


class HostProjectTests(unittest.TestCase):
    def test_inherited_case_initializer_can_complete_existing_bridge_pointer_without_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='rf case pointer ') as directory:
            project = Path(directory).resolve()
            pointer = build_case_pointer(Path('work/owned'), 'components/reverse-core/routes/R3.md', 'analysis',
                workflow=workflow_contract({}, 'analysis', objective='reconstruction', user_request='分析然后复刻'))
            record_case_pointer(project, pointer)
            record = project / 'work/owned/case.json'
            original = record.read_bytes()
            argv = ['powershell', '-NoProfile', '-File', str(ROOT/'skills/scripts/case-init.ps1'),
                    '-ProjectRoot', str(project), '-CaseName', 'owned', '-Hint', 'JavaScript analysis', '-ResumePointer']
            run = subprocess.run(argv, cwd=project, capture_output=True, timeout=30)
            self.assertEqual(run.returncode, 0, run.stderr.decode('utf-8',errors='replace'))
            self.assertEqual(record.read_bytes(), original)
            scope = project / 'work/owned/scope.md'
            content = scope.read_bytes()
            again = subprocess.run(argv, cwd=project, capture_output=True, timeout=30)
            self.assertNotEqual(again.returncode, 0)
            self.assertEqual(scope.read_bytes(), content)
            self.assertEqual(record.read_bytes(), original)

    def test_selected_host_pointer_is_project_local_and_removal_preserves_user_content(self):
        for client in ('codex', 'pi', 'claude'):
            with self.subTest(client=client), tempfile.TemporaryDirectory() as directory:
                project = Path(directory).resolve()
                original = project / ('CLAUDE.md' if client == 'claude' else 'AGENTS.md')
                original.write_text('User instructions: preserve my project.\n', encoding='utf-8')
                before = {p: p.read_bytes() for p in project.rglob('*') if p.is_file()}
                connect_project(ROOT, project, client=client)
                self.assertEqual(before, {p: p.read_bytes() for p in project.rglob('*') if p.is_file()})
                result = connect_project(ROOT, project, client=client, apply=True)
                self.assertTrue(Path(result['skill']).is_relative_to(project))
                self.assertFalse(result['global_writes'])
                self.assertIn(ROOT.as_posix(), Path(result['skill']).read_text(encoding='utf-8'))
                connect_project(ROOT, project, client=client, apply=True)
                self.assertEqual(original.read_text(encoding='utf-8').count('reverse-fusion:begin'), 1)
                connect_project(ROOT, project, client=client, apply=True, remove=True)
                self.assertIn('preserve my project', original.read_text(encoding='utf-8'))
                self.assertFalse(Path(result['skill']).exists())

    def test_unmanaged_project_file_and_other_checkout_removal_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            result = connect_project(ROOT, project, client='pi', apply=True)
            with self.assertRaisesRegex(ValueError, 'Another checkout'):
                connect_project(ROOT / 'another', project, client='pi', apply=True, remove=True)
            Path(result['skill']).write_text('User-owned skill', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'not owned'):
                connect_project(ROOT, project, client='pi', apply=True)

    def test_actual_official_spec_layouts_are_found_and_missing_phases_rejected(self):
        specify = ROOT / '.venv/Scripts/specify.exe'
        for client in ('codex', 'pi', 'claude'):
            with self.subTest(client=client), tempfile.TemporaryDirectory() as directory:
                project = Path(directory).resolve()
                run = subprocess.run([str(specify), 'init', '--here', '--non-interactive', '--integration', client,
                                      '--script', 'ps', '--ignore-agent-tools'], cwd=project,
                                     capture_output=True, timeout=30)
                self.assertEqual(run.returncode, 0, run.stderr)
                result = generated_workflow(project)
                self.assertEqual(result['client'], client)
                self.assertEqual(result['status'], 'available')
                self.assertEqual(set(result['phases']), set(PHASES))
                (project / result['phases']['converge']).unlink()
                self.assertEqual(generated_workflow(project)['missing_phases'], ['converge'])
