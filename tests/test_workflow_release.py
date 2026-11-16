"""Engineering handoff checks using inert records, never a user target."""
import hashlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from reverse_fusion.cli import main
from reverse_fusion.release import check_release
from reverse_fusion.workflow import inspect_workflow

ROOT = Path(__file__).resolve().parents[1]


class WorkflowReleaseTests(unittest.TestCase):
    def bridge(self, project, *args):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(['bridge', '--project-root', str(project), '--hint', '分析这个软件然后复刻', '--record', *args])
        self.assertEqual(code, 0, output.getvalue())
        return json.loads(output.getvalue())

    def test_workflow_recovers_referenced_material_without_writes_or_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            scope = project / 'scope.md'
            scope.write_text('inert research record; do not execute', encoding='utf-8')
            self.bridge(project, '--ref', 'scope.md')
            case = project / 'work/current-case/case.json'
            before = case.read_bytes()
            with patch('subprocess.run', side_effect=AssertionError('workflow must not execute a provider')):
                result = inspect_workflow(ROOT, project)
            self.assertEqual(result['workflow']['objective'], 'reconstruction')
            self.assertEqual(result['project_refs'], [{'path': str(scope), 'present': True}])
            self.assertEqual(result['entries']['cwd'], str(project))
            self.assertEqual(case.read_bytes(), before)
            scope.unlink()
            self.assertEqual(inspect_workflow(ROOT, project)['status'], 'missing-context')

    def test_receipt_drift_and_other_case_receipt_do_not_qualify_work(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            self.bridge(project)
            name = 'work/current-case/case.json'
            frozen = hashlib.sha256((project / name).read_bytes()).hexdigest()
            receipt = {'version': 1, 'backend': 'current-session', 'project_root': str(project),
                       'workspace': 'candidate', 'phase': 'check', 'frozen_refs': {name: frozen}}
            path = project / 'session.json'
            path.write_text(json.dumps(receipt), encoding='utf-8')
            original = path.read_bytes()
            self.assertEqual(inspect_workflow(ROOT, project, receipt='session.json')['status'], 'context-resolved')
            (project / name).write_bytes((project / name).read_bytes() + b'\n')
            drifted = inspect_workflow(ROOT, project, receipt='session.json')
            self.assertEqual(drifted['status'], 'frozen-input-changed')
            self.assertEqual(path.read_bytes(), original)
            receipt['frozen_refs'] = {'session.json': '0' * 64}
            path.write_text(json.dumps(receipt), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'selected case'):
                inspect_workflow(ROOT, project, receipt='session.json')
            path.write_text('[]', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'supported record'):
                inspect_workflow(ROOT, project, receipt='session.json')

    def test_multiple_cases_and_escape_never_select_or_read_an_outside_record(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            self.assertEqual(inspect_workflow(ROOT, project)['status'], 'no-open-case')
            self.bridge(project, '--case-root', 'work/one')
            self.bridge(project, '--case-root', 'work/two')
            self.assertEqual(inspect_workflow(ROOT, project)['status'], 'needs-case-selection')
            with self.assertRaises(ValueError):
                inspect_workflow(ROOT, project, case_root='../outside')
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(['bridge', '--project-root', str(project), '--hint', '分析程序',
                             '--case-root', 'work/one', '--ref', '../outside', '--record'])
            self.assertEqual(code, 2)

    def test_release_is_finite_and_missing_release_contract_blocks_it(self):
        result = check_release(ROOT)
        self.assertEqual(result['status'], 'ready', result)
        self.assertEqual(result['target_acceptance'], 'not-performed')
        with tempfile.TemporaryDirectory() as directory, patch('reverse_fusion.release.check_contracts',
                         return_value={'status': 'pass', 'checks': []}):
            result = check_release(Path(directory))
            self.assertEqual(result['status'], 'blocked')
            self.assertTrue(any(gate['id'] == 'release-contract' and gate['status'] == 'fail' for gate in result['checks']))

    def test_deployed_release_rejects_stale_managed_entry(self):
        from reverse_fusion.global_adapter import agents_block, skill_text
        from reverse_fusion import __version__
        with tempfile.TemporaryDirectory() as directory:
            local = Path(directory)
            skill, agents = local / 'skill.md', local / 'agents.md'
            skill.write_text(skill_text(ROOT), encoding='utf-8')
            agents.write_text(agents_block(ROOT), encoding='utf-8')
            install = {'installed': True, 'version': __version__, 'host': {'client': 'codex'},
                       'global_adapter': {'enabled': True, 'repository': str(ROOT)}}
            actual_read = Path.read_text
            def read(path, *args, **kwargs):
                if path == ROOT / 'state/install.json':
                    return json.dumps(install)
                return actual_read(path, *args, **kwargs)
            with patch('reverse_fusion.release.platform.system', return_value='Windows'), \
                    patch('reverse_fusion.release.platform.machine', return_value='AMD64'), \
                    patch('reverse_fusion.release.component_status', return_value={}), \
                    patch('reverse_fusion.release.core_deployment', return_value={'status': 'installed', 'missing': []}), \
                    patch('reverse_fusion.release.adapter_paths', return_value={'skill': skill, 'agents': agents}), \
                    patch.object(Path, 'read_text', read):
                self.assertEqual(check_release(ROOT, deployed=True)['status'], 'ready')
                skill.write_text('outdated managed entry', encoding='utf-8')
                result = check_release(ROOT, deployed=True)
                self.assertEqual(result['status'], 'blocked')
                self.assertTrue(any(gate['id'] == 'deployed-entry' and gate['status'] == 'fail' for gate in result['checks']))


if __name__ == '__main__':
    unittest.main()
