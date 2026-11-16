"""Bind the existing handoff checker to an external Builder session.

All native-looking bundle data below comes from the explicitly synthetic
pointer fixture. These tests prove mechanical gating, not authentic REA proof.
"""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import subprocess
import sys

from reverse_fusion.case_bridge import build_case_pointer, record_case_pointer, workflow_contract
from reverse_fusion.session_builder import prepare_session, check_session
from hashlib import sha256
from copy import deepcopy


ROOT = Path(__file__).resolve().parents[1]
CASE = 'case-fixture/demo'
MANIFEST = f'{CASE}/notes/handoff-manifest.json'
TASKS = 'specs/001-literal-v1/tasks.md'
BUNDLE = f'{CASE}/evidence/synthetic-bundle.json'


class ReconstructionGateTests(unittest.TestCase):
    def test_independent_reviewed_batch_retains_deferred_critical_requirement(self):
        spec = self.project / 'specs/001-literal-v1/spec.md'
        spec.write_text(spec.read_text(encoding='utf-8') + '\n- FR-002: Remote-dependent behavior remains unknown.\n', encoding='utf-8')
        tasks = self.project / TASKS
        tasks.write_text('- [ ] T001 Implement local behavior FR-001\n- [ ] T002 Implement remote behavior FR-002\n', encoding='utf-8')
        manifest_path = self.project / MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        for name, path in [('spec', spec), ('tasks', tasks)]:
            manifest['feature_refs'][name]['sha256'] = sha256(path.read_bytes()).hexdigest()
        deferred = deepcopy(manifest['requirements'][0])
        deferred['fr_id'] = 'FR-002'
        deferred['unknown_refs'][0]['critical'] = True
        manifest['requirements'].append(deferred)
        manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'critical_open'):
            prepare_session(self.project, **self.kwargs)
        result = prepare_session(self.project, **self.kwargs, requirements=['FR-001'])
        self.assertEqual(result['status'], 'prepared')
        record = json.loads((self.project / self.kwargs['receipt']).read_text(encoding='utf-8'))
        self.assertEqual(record['batch_requirements'], ['FR-001'])
        self.assertEqual(record['handoff']['deferred_requirements'], ['FR-002'])
        self.assertIn('FR-002', spec.read_text(encoding='utf-8'))

    def test_selected_batch_cannot_omit_its_tasks_requirement(self):
        tasks = self.project / TASKS
        tasks.write_text('- [ ] T001 Implement FR-001\n', encoding='utf-8')
        path = self.project / MANIFEST
        manifest = json.loads(path.read_text(encoding='utf-8'))
        manifest['feature_refs']['tasks']['sha256'] = sha256(tasks.read_bytes()).hexdigest()
        path.write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'fr.batch'):
            prepare_session(self.project, **self.kwargs, requirements=['FR-999'])
        tasks.write_text('- [ ] T001 No explicit requirement\n', encoding='utf-8')
        manifest['feature_refs']['tasks']['sha256'] = sha256(tasks.read_bytes()).hexdigest()
        path.write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'lacks an explicit FR mapping'):
            prepare_session(self.project, **self.kwargs, requirements=['FR-001'])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='rf handoff ')
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name).resolve() / 'project'
        shutil.copytree(ROOT / 'skills/reconstruction/examples/synthetic-project', self.project)
        pointer = build_case_pointer(Path(CASE), 'components/reverse-core/routes/R46.md', 'reconstruction',
                                     workflow=workflow_contract({}, 'reconstruction'))
        record_case_pointer(self.project, pointer)
        (self.project / 'review.md').write_text(
            'Synthetic fixture review: only literal empty-input exit 2 is supported. '
            'Nonempty input remains unknown; no real target or REA execution occurred.', encoding='utf-8')
        self.kwargs = dict(workspace='candidate', receipt=f'{CASE}/session.json', tasks=['T001'],
                           task_files=[TASKS], research_files=[BUNDLE], allowed_outputs=['answer.py'],
                           handoff_manifest=MANIFEST, review_file='review.md')

    def test_installed_cli_binds_external_case_and_reports_only_mechanical_review(self):
        arguments = [sys.executable, '-X', 'utf8', '-m', 'reverse_fusion', 'session', 'prepare',
                     '--project-root', str(self.project), '--case-root', CASE,
                     '--receipt', self.kwargs['receipt'], '--workspace', 'candidate', '--tasks', 'T001',
                     '--task-file', TASKS, '--research-file', BUNDLE, '--allowed-output', 'answer.py',
                     '--handoff-manifest', MANIFEST, '--review-file', 'review.md']
        result = subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['handoff_assessment'], 'machine_check_only')
        self.assertIn('not-performed', data['semantic_verification'])
        self.assertTrue((self.project / self.kwargs['receipt']).is_file())

    def test_checked_handoff_and_all_source_dependencies_are_frozen(self):
        result = prepare_session(self.project, **self.kwargs)
        self.assertEqual(result['handoff_assessment'], 'machine_check_only')
        self.assertIn('not-performed', result['semantic_verification'])
        (self.project / 'candidate/answer.py').write_text('raise SystemExit(2)\n', encoding='utf-8')
        for phase in ('check', 'refine', 'finish'):
            checked = check_session(self.project, receipt=self.kwargs['receipt'], phase=phase)
        self.assertEqual(checked['business_acceptance'], 'not-performed')

    def test_critical_unknown_blocks_before_candidate_or_receipt_creation(self):
        manifest = json.loads((self.project / MANIFEST).read_text(encoding='utf-8'))
        manifest['requirements'][0]['unknown_refs'][0]['critical'] = True
        (self.project / MANIFEST).write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'critical_open'):
            prepare_session(self.project, **self.kwargs)
        self.assertFalse((self.project / 'candidate').exists())
        self.assertFalse((self.project / self.kwargs['receipt']).exists())

    def test_omitting_case_flag_does_not_skip_gate_for_a_case_receipt(self):
        self.kwargs.pop('handoff_manifest')
        self.kwargs.pop('review_file')
        with self.assertRaisesRegex(ValueError, 'requires --handoff-manifest'):
            prepare_session(self.project, **self.kwargs)

    def test_evidence_and_review_changes_invalidate_prepared_candidate(self):
        prepare_session(self.project, **self.kwargs)
        (self.project / 'candidate/answer.py').write_text('raise SystemExit(2)\n', encoding='utf-8')
        (self.project / 'review.md').write_text('new unsupported delivery scope', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Frozen task or research changed'):
            check_session(self.project, receipt=self.kwargs['receipt'], phase='check')

    def test_analysis_case_cannot_silently_enter_implementation(self):
        pointer = build_case_pointer(Path(CASE), 'components/reverse-core/routes/R0.md', 'analysis',
                                     workflow=workflow_contract({}, 'analysis'))
        record_case_pointer(self.project, pointer)
        with self.assertRaisesRegex(ValueError, 'evidence-to-reconstruction transition'):
            prepare_session(self.project, **self.kwargs)

    def test_omitted_review_and_different_task_file_cannot_pass(self):
        self.kwargs['review_file'] = None
        with self.assertRaisesRegex(ValueError, 'requires --handoff-manifest'):
            prepare_session(self.project, **self.kwargs)
        self.kwargs['review_file'] = 'review.md'
        (self.project / 'other-tasks.md').write_text('T001 unrelated', encoding='utf-8')
        self.kwargs['task_files'] = ['other-tasks.md']
        with self.assertRaisesRegex(ValueError, 'handoff feature'):
            prepare_session(self.project, **self.kwargs)


if __name__ == '__main__':
    unittest.main()
