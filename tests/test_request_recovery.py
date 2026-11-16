"""Real bridge/recovery behavior for novice requests and pointer loss."""
from contextlib import redirect_stdout
from concurrent.futures import ThreadPoolExecutor
import io
import json
from pathlib import Path, PureWindowsPath
import tempfile
import unittest
from unittest.mock import patch

from reverse_fusion import case_bridge
from reverse_fusion.cli import main
from reverse_fusion.file_updates import atomic_write


class RequestRecoveryTests(unittest.TestCase):
    def invoke(self, project, *arguments, code=0):
        output = io.StringIO()
        with redirect_stdout(output):
            actual = main([arguments[0], '--project-root', str(project), *arguments[1:]])
        result = json.loads(output.getvalue())
        self.assertEqual(actual, code, result)
        return result

    def test_target_analysis_and_restoration_requests_enter_analysis_and_preserve_intent(self):
        analysis = ['帮我分析这个文件', '帮我分析这个文件夹里的代码，告诉我工作原理',
                    '对这个项目做安全审计', '分析这个 dll 的功能', 'Inspect this binary',
                    '只分析这个程序，暂时不要还原它',
                    'analyze the obfuscated application']
        recreation = ['还原这个程序的功能和界面', '把这个软件还原成能用的版本，然后复刻']
        for prompt in [*analysis, *recreation]:
            with self.subTest(prompt=prompt), tempfile.TemporaryDirectory() as directory:
                project = Path(directory).resolve()
                result = self.invoke(project, 'bridge', '--hint', prompt, '--record')
                self.assertEqual(result['workflow']['stage'], 'analysis')
                self.assertEqual(result['workflow']['objective'], 'reconstruction' if prompt in recreation else 'analysis')
                self.assertEqual(result['workflow']['user_request'], prompt)
                self.assertTrue(result['recorded'])
                saved = json.loads((project/'work/current-case/case.json').read_text(encoding='utf-8'))
                self.assertEqual(saved['pointer']['workflow']['user_request'], prompt)

    def test_development_words_do_not_activate_or_write_reverse_cases(self):
        prompts = ['帮我给React网站增加登录后才能访问的 protected routes',
                   'Implement protected routes for my dashboard',
                   'Add protected routes to my application', 'Build a protected application',
                   'Write a function to reverse a list', 'Reverse an array in JavaScript',
                   'Add a reverse proxy for our app', 'Fix the packed layout in the settings page',
                   '开发一个待办事项网站', '修复我们应用的登录按钮']
        for prompt in prompts:
            with self.subTest(prompt=prompt), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                result = self.invoke(project, 'bridge', '--hint', prompt, '--record')
                self.assertEqual(result['status'], 'host-native')
                self.assertFalse(result['recorded'])
                self.assertEqual(list(project.iterdir()), [])

    def test_missing_continue_never_creates_a_new_goal_or_reports_host_native_success(self):
        for prompt in ['继续', 'continue', '恢复上次']:
            with self.subTest(prompt=prompt), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                result = self.invoke(project, 'bridge', '--hint', prompt, '--record', code=2)
                self.assertEqual(result['status'], 'no-open-case')
                self.assertEqual(result['cases'], [])
                self.assertFalse(result['recorded'])
                self.assertEqual(list(project.iterdir()), [])

    def test_explicit_missing_case_cannot_resume_another_existing_case(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            self.invoke(project, 'bridge', '--hint', '分析这个文件', '--case-root', 'work/real', '--record')
            before = {p: p.read_bytes() for p in project.rglob('*') if p.is_file()}
            result = self.invoke(project, 'bridge', '--hint', '继续', '--case-root', 'work/missing', '--record', code=2)
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_nondefault_and_nested_cases_are_discovered_from_index_without_tree_scan(self):
        for name in ['research/target', 'work/analysis/target']:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                project = Path(directory).resolve()
                prompt = '还原这个程序的功能和界面'
                self.invoke(project, 'bridge', '--hint', prompt, '--case-root', name, '--record')
                pointer = project/name/'case.json'
                before = pointer.read_bytes()
                with patch.object(Path, 'rglob', side_effect=AssertionError('Do not recursively search a user project')):
                    workflow = self.invoke(project, 'workflow')
                    resumed = self.invoke(project, 'bridge', '--hint', '继续')
                self.assertEqual(workflow['case_root'].replace('\\','/'), name)
                self.assertEqual(resumed['workflow']['user_request'], prompt)
                self.assertEqual(resumed['workflow']['objective'], 'reconstruction')
                self.assertEqual(pointer.read_bytes(), before)
                index = json.loads((project/'.reverse-fusion/cases.json').read_text(encoding='utf-8'))
                self.assertEqual(index['case_roots'], [name])

    def test_legacy_direct_cases_still_resume_without_an_index(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            self.invoke(project, 'bridge', '--hint', '分析这个文件', '--case-root', 'work/legacy', '--record')
            (project/'.reverse-fusion/cases.json').unlink()
            result = self.invoke(project, 'workflow')
            self.assertEqual(result['status'], 'context-resolved')
            self.assertEqual(result['case_root'].replace('\\','/'), 'work/legacy')

    def test_discovery_rejects_index_escape_and_pointer_identity_changes_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            self.invoke(project, 'bridge', '--hint', '分析这个文件', '--case-root', 'research/target', '--record')
            index = project/'.reverse-fusion/cases.json'
            original = index.read_bytes()
            index.write_text(json.dumps({'schema_version': 1, 'case_roots': ['../outside']}), encoding='utf-8')
            result = self.invoke(project, 'bridge', '--hint', '继续', '--record', code=2)
            self.assertEqual(result['status'], 'blocked')
            self.assertIn('../outside', index.read_text(encoding='utf-8'))
            index.write_bytes(original)
            record_path = project/'research/target/case.json'
            record = json.loads(record_path.read_text(encoding='utf-8'))
            record['pointer']['case_root'] = 'research/other'
            record_path.write_text(json.dumps(record), encoding='utf-8')
            result = self.invoke(project, 'workflow', code=2)
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(index.read_bytes(), original)

    def test_case_and_index_both_rollback_on_index_write_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            self.invoke(project, 'bridge', '--hint', '分析这个文件', '--case-root', 'research/target', '--record')
            paths = [project/'research/target/case.json', project/'.reverse-fusion/cases.json']
            before = {path: path.read_bytes() for path in paths}
            attempts = []
            def fail_index(path, data):
                attempts.append(path)
                if path == paths[1]:
                    self.assertNotEqual(paths[0].read_bytes(), before[paths[0]])
                    raise OSError('injected case index write failure')
                atomic_write(path, data)
            with patch.object(case_bridge, 'atomic_write', side_effect=fail_index):
                result = self.invoke(project, 'bridge', '--hint', '继续', '--record', code=2)
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(attempts, paths)
            self.assertEqual({path: path.read_bytes() for path in paths}, before)

    def test_failed_first_index_write_does_not_leave_an_unindexed_case(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            path = project/'research/target/case.json'
            index = project/'.reverse-fusion/cases.json'
            def fail_index(target, data):
                if target == index:
                    self.assertTrue(path.is_file())
                    raise OSError('injected first index write failure')
                atomic_write(target, data)
            with patch.object(case_bridge, 'atomic_write', side_effect=fail_index):
                result = self.invoke(project, 'bridge', '--hint', '分析这个文件', '--case-root', 'research/target', '--record', code=2)
            self.assertEqual(result['status'], 'blocked')
            self.assertFalse(path.exists())
            self.assertFalse(index.exists())

    def test_parallel_nested_case_recording_does_not_lose_index_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            names = [f'research/parallel/target-{number}' for number in range(8)]
            def record(name):
                pointer = case_bridge.build_case_pointer(Path(name), 'components/reverse-core/routes/R0.md', 'analysis',
                    workflow=case_bridge.workflow_contract({'primary':'R0'}, 'analysis', objective='analysis', user_request=name))
                return case_bridge.record_case_pointer(project, pointer)
            with ThreadPoolExecutor(max_workers=4) as pool:
                paths = list(pool.map(record, names))
            self.assertEqual(len(paths), len(names))
            self.assertEqual(case_bridge.discover_open_cases(project), sorted(names))

    def test_index_and_lock_accept_resolved_windows_prefix_without_changing_io_paths(self):
        # Deterministically model the real Windows create/resolve race: one
        # native probe returns an extended namespace while the root has none.
        for drive, extended in ((r'C:\owned\project',r'\\?\C:\owned\project'),
                                (r'\\server\share\project',r'\\?\UNC\server\share\project')):
            with self.subTest(drive=drive),tempfile.TemporaryDirectory() as directory:
                project=Path(directory).resolve()
                actual_resolve=Path.resolve
                def resolve(path,*args,**kwargs):
                    if path==project:return PureWindowsPath(drive)
                    if path.parent==project/'.reverse-fusion':
                        return PureWindowsPath(extended)/'.reverse-fusion'/path.name
                    return actual_resolve(path,*args,**kwargs)
                with patch.object(Path,'resolve',resolve):
                    index=case_bridge._case_index_path(project)
                    self.assertEqual(index,project/'.reverse-fusion/cases.json')
                    with case_bridge._case_index_lock(project):
                        self.assertTrue((project/'.reverse-fusion/cases.lock').is_file())
                self.assertFalse(index.exists())
                self.assertEqual((project/'.reverse-fusion/cases.lock').read_bytes(),b'\0')

    def test_index_and_lock_still_reject_resolved_outside_symlinks(self):
        for target in ('directory','index','lock'):
            with self.subTest(target=target),tempfile.TemporaryDirectory() as directory:
                base=Path(directory).resolve();project=base/'project';project.mkdir()
                outside=base/'outside';outside.mkdir()
                sentinel=outside/'preserve.txt';sentinel.write_bytes(b'untouched external data')
                if target=='directory':
                    (project/'.reverse-fusion').symlink_to(outside,target_is_directory=True)
                else:
                    (project/'.reverse-fusion').mkdir()
                    external=outside/('cases.json' if target=='index' else 'cases.lock')
                    external.write_bytes(b'preserve external pointer or lock')
                    (project/'.reverse-fusion'/external.name).symlink_to(external)
                before={p.name:p.read_bytes() for p in outside.iterdir()}
                pointer=case_bridge.build_case_pointer(Path('research/target'),'components/reverse-core/routes/R0.md','analysis')
                with self.assertRaisesRegex(ValueError,'Case discovery (index|lock) leaves'):
                    case_bridge.record_case_pointer(project,pointer)
                self.assertEqual({p.name:p.read_bytes() for p in outside.iterdir()},before)
                self.assertFalse((project/'research').exists())

