"""Exercise the installed CLI from a real project outside the tool checkout."""
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest


TOOL_ROOT = Path(__file__).resolve().parents[1]


class CrossProjectTests(unittest.TestCase):
    def test_novice_request_preserves_delivery_goal_through_refinement_and_continue(self):
        with tempfile.TemporaryDirectory(prefix='rf novice 项目 ') as directory:
            project = Path(directory).resolve()
            prompt = '帮我分析这个软件，然后复刻出一个界面和功能都一样、能实际使用的版本。'
            initial = self.invoke(project, 'bridge', '--hint', prompt,
                                  '--case-root', 'work/target', '--record')
            self.assertEqual(initial['workflow']['stage'], 'analysis')
            self.assertEqual(initial['workflow']['objective'], 'reconstruction')
            self.assertEqual(initial['route']['primary_id'], 'R0')
            self.assertEqual(initial['route']['next_stage']['id'], 'R46')
            self.assertTrue(Path(initial['agent_guide']).is_file())
            case_file = project / 'work/target/case.json'
            record = json.loads(case_file.read_text(encoding='utf-8'))
            record['pointer']['carry_forward_refs'].append('notes/original-behavior.md')
            case_file.write_text(json.dumps(record), encoding='utf-8')
            refined = self.invoke(project, 'bridge', '--hint', 'JavaScript WASM analysis',
                                  '--mode', 'analysis', '--case-root', 'work/target', '--record')
            self.assertEqual(refined['workflow']['user_request'], prompt)
            self.assertEqual(refined['workflow']['objective'], 'reconstruction')
            self.assertIn('notes/original-behavior.md', refined['pointer']['carry_forward_refs'])
            resumed = self.invoke(project, 'bridge', '--hint', '继续')
            self.assertEqual(resumed['mode'], 'follow-up')
            self.assertEqual(resumed['workflow']['user_request'], prompt)
            self.assertEqual(resumed['route']['primary_id'], refined['route']['primary_id'])
            self.assertEqual(Path(resumed['pointer']['case_root']), Path('work/target'))
            self.assertEqual(resumed['workflow']['stage'], 'analysis')
            self.assertEqual(json.loads(case_file.read_text(encoding='utf-8'))['revision'], 2)

    def test_continue_ambiguity_never_overwrites_a_case(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            for name in ('first', 'second'):
                self.invoke(project, 'bridge', '--hint', '分析这个软件',
                            '--case-root', f'work/{name}', '--record')
            before = {p: p.read_bytes() for p in project.rglob('case.json')}
            result = self.invoke(project, 'bridge', '--hint', '继续', '--record', code=2)
            self.assertEqual(result['status'], 'needs-case-selection')
            self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_plain_analysis_recreation_and_normal_development_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            for prompt in ('先分析这个软件，暂时不要写复刻版', '帮我看懂这个 APK', '分析这份抓包里客户端和服务器怎么交互'):
                result = self.invoke(project, 'bridge', '--hint', prompt)
                self.assertEqual(result['workflow']['objective'], 'analysis')
                self.assertEqual(result['workflow']['stage'], 'analysis')
            recreated = self.invoke(project, 'bridge', '--hint', '照着这个网站做一样的使用效果')
            self.assertEqual(recreated['workflow']['objective'], 'reconstruction')
            self.assertEqual(recreated['route']['next_stage']['id'], 'R46')
            for prompt in ('开发一个待办事项网站', '修复我们应用的登录按钮', 'continue'):
                result = self.invoke(project, 'bridge', '--hint', prompt)
                self.assertEqual(result['status'], 'host-native')
            self.assertFalse((project / 'work').exists())

    def test_json_transport_preserves_unicode_without_utf8_caller_override(self):
        with tempfile.TemporaryDirectory(prefix='rf 项目 🧪 ') as directory:
            project = Path(directory).resolve()
            env = dict(os.environ, PYTHONIOENCODING='gbk')
            result = subprocess.run(
                [sys.executable, '-m', 'reverse_fusion', 'bridge', '--mode', 'analysis',
                 '--hint', 'JavaScript 逆向 🧪', '--format', 'json'],
                cwd=project, env=env, capture_output=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr.decode('ascii', errors='replace'))
            payload = json.loads(result.stdout.decode('ascii'))
            self.assertEqual(payload['project_root'], str(project))
            self.assertEqual(payload['route']['hint'], 'JavaScript 逆向 🧪')

    def invoke(self, project, *args, code=0, cwd=None):
        result = subprocess.run(
            [sys.executable, '-X', 'utf8', '-m', 'reverse_fusion', *args],
            cwd=cwd or project, capture_output=True, text=True, encoding='utf-8', timeout=30,
        )
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_external_project_route_record_resume_and_current_session(self):
        with tempfile.TemporaryDirectory(prefix='rf external 项目 ') as directory:
            project = Path(directory).resolve()
            bridge = self.invoke(project, 'bridge', '--hint', 'reverse JavaScript app',
                                 '--mode', 'reconstruction', '--case-root', 'work/case', '--record')
            self.assertEqual(bridge['project_root'], str(project))
            self.assertEqual(bridge['repository_root'], str(TOOL_ROOT))
            self.assertTrue((project / 'work/case/case.json').is_file())
            self.assertEqual(bridge['route']['primary_id'], 'R3')
            self.assertEqual(bridge['implementation_gate']['status'], 'not-assessed')
            self.assertTrue(all(Path(p).is_file() for p in bridge['required_read_paths']))
            resumed = self.invoke(project, 'bridge', '--hint', 'continue', '--mode', 'follow-up',
                                  '--case-root', 'work/case')
            self.assertIn('frozen-spec-tasks', resumed['workflow']['required_artifacts'])

            (project / 'tasks.md').write_text('T-001: independently return the observed value\n', encoding='utf-8')
            (project / 'research.json').write_text('{"observed": {"input": 6, "output": 42}}', encoding='utf-8')
            # This separate arithmetic fixture checks file boundaries only; it
            # cannot substitute for the reconstruction handoff gate tests.
            common = ['--project-root', str(project), '--receipt', 'work/boundary/session.json']
            prepared = self.invoke(project, 'session', 'prepare', *common, '--workspace', 'candidate',
                                   '--tasks', 'T-001', '--task-file', 'tasks.md',
                                   '--research-file', 'research.json', '--allowed-output', 'answer.py',
                                   cwd=TOOL_ROOT)
            self.assertEqual(prepared['status'], 'prepared')
            (project / 'candidate/answer.py').write_text('print(7 * 6)\n', encoding='utf-8')
            for phase in ('check', 'refine', 'finish'):
                checked = self.invoke(project, 'session', phase, *common, cwd=TOOL_ROOT)
            self.assertEqual(checked['status'], 'candidate')
            self.assertEqual(checked['business_acceptance'], 'not-performed')
            # Independent runtime check; the boundary receipt itself proves no behavior.
            output = subprocess.check_output([sys.executable, str(project / 'candidate/answer.py')], text=True)
            self.assertEqual(output.strip(), '42')

    def test_explicit_root_and_traversal_cannot_write_into_shared_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            result = self.invoke(project, 'bridge', '--project-root', str(project), '--hint', 'APK reverse',
                                 '--mode', 'analysis', '--record', '--case-root', '../outside', code=2,
                                 cwd=TOOL_ROOT)
            self.assertEqual(result['status'], 'blocked')
            result = self.invoke(project, 'bridge', '--hint', 'build a todo app')
            self.assertEqual(result['status'], 'host-native')
            self.assertFalse((project / 'work').exists())

    def test_resuming_a_copied_case_pointer_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            self.invoke(project, 'bridge', '--hint', 'reverse JavaScript', '--mode', 'analysis',
                        '--case-root', 'work/first', '--record')
            (project / 'work/other').mkdir()
            shutil.copyfile(project / 'work/first/case.json', project / 'work/other/case.json')
            result = self.invoke(project, 'bridge', '--hint', 'continue', '--mode', 'follow-up',
                                 '--case-root', 'work/other', code=2)
            self.assertEqual(result['status'], 'blocked')

    def test_frozen_input_change_is_detected_through_external_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            (project / 'tasks.md').write_text('T-001: answer\n', encoding='utf-8')
            (project / 'research.txt').write_text('observed 42', encoding='utf-8')
            self.invoke(project, 'session', 'prepare', '--workspace', 'candidate', '--tasks', 'T-001',
                        '--task-file', 'tasks.md', '--research-file', 'research.txt', '--allowed-output', 'answer.py')
            (project / 'candidate/answer.py').write_text('print(42)', encoding='utf-8')
            (project / 'research.txt').write_text('changed input', encoding='utf-8')
            result = self.invoke(project, 'session', 'check', code=2)
            self.assertEqual(result['status'], 'blocked')

    def test_offline_copy_stays_in_project_and_is_not_native_craft(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            project = Path(directory).resolve()
            (project / 'input.txt').write_text('synthetic fixture', encoding='utf-8')
            copied = self.invoke(project, 'craft', '--source', 'input.txt', '--output', 'candidate/output.txt',
                                 '--record', '--project-root', str(project), cwd=TOOL_ROOT)
            self.assertEqual(copied['backend'], 'local-bounded-worker')
            self.assertTrue((project / 'state/craft-candidate.json').is_file())
            self.assertEqual((project / 'candidate/output.txt').read_text(encoding='utf-8'), 'synthetic fixture')
            try:
                (project / 'linked').symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(str(exc))
            denied = self.invoke(project, 'craft', '--source', 'input.txt', '--output', 'linked/escape.txt', code=2)
            self.assertEqual(denied['disposition'], 'needs-scope')
            self.assertFalse((Path(outside) / 'escape.txt').exists())

    def test_external_session_runs_original_candidate_and_rejects_a_mutant(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node is required only for this real JS replay fixture')
        with tempfile.TemporaryDirectory(prefix='rf differential 项目 ') as directory:
            project = Path(directory).resolve()
            # Real executable source fixture; this test produces no REA IDs or proof.
            shutil.copyfile(TOOL_ROOT / 'fixtures/web-original/app.js', project / 'original.mjs')
            (project / 'tasks.md').write_text('T-001: match the observed answer export\n', encoding='utf-8')
            self.invoke(project, 'session', 'prepare', '--workspace', 'candidate', '--tasks', 'T-001',
                        '--task-file', 'tasks.md', '--research-file', 'original.mjs', '--allowed-output', 'answer.mjs')
            candidate = project / 'candidate/answer.mjs'
            candidate.write_text("export const answer = x => ['rf', `${x}`.trim().toUpperCase()].join(':');\n", encoding='utf-8')
            for phase in ('check', 'refine', 'finish'):
                self.invoke(project, 'session', phase)
            (project / 'compare.mjs').write_text(
                "import {answer as original} from './original.mjs';\n"
                "import {answer as candidate} from './candidate/answer.mjs';\n"
                "const inputs = [' hello ', '', 'MiXeD', 7];\n"
                "const left = inputs.map(original), right = inputs.map(candidate);\n"
                "const equal = JSON.stringify(left) === JSON.stringify(right);\n"
                "console.log(JSON.stringify({left, right, equal})); process.exitCode = equal ? 0 : 1;\n",
                encoding='utf-8')
            verified = subprocess.run([node, str(project / 'compare.mjs')], capture_output=True,
                                      text=True, encoding='utf-8', timeout=15)
            self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
            self.assertTrue(json.loads(verified.stdout)['equal'])
            candidate.write_text("export const answer = x => 'rf:' + String(x).trim().toLowerCase();\n", encoding='utf-8')
            rejected = subprocess.run([node, str(project / 'compare.mjs')], capture_output=True,
                                      text=True, encoding='utf-8', timeout=15)
            self.assertEqual(rejected.returncode, 1)
            self.assertFalse(json.loads(rejected.stdout)['equal'])


if __name__ == '__main__':
    unittest.main()
