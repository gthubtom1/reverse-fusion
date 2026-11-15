import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from reverse_fusion.builder import HostBuilder
from reverse_fusion.host import assistant_texts
from reverse_fusion.session_builder import check_session, prepare_session
from reverse_fusion import cli


class SessionTests(unittest.TestCase):
    def prepare(self, root):
        (root / 'tasks.md').write_text('- [ ] T-001: implement answer\n', encoding='utf-8')
        (root / 'research.json').write_text('{"observed": "answer"}', encoding='utf-8')
        return prepare_session(root, workspace='candidate', receipt='session.json', tasks=['T-001'],
                               task_files=['tasks.md'], research_files=['research.json'],
                               allowed_outputs=['answer.py'])

    def test_current_host_can_complete_without_starting_a_cli(self):
        with tempfile.TemporaryDirectory() as directory, patch('subprocess.run') as run:
            root = Path(directory)
            self.assertEqual(self.prepare(root)['status'], 'prepared')
            (root / 'candidate/answer.py').write_text('answer = 42\n', encoding='utf-8')
            for phase in ('check', 'refine', 'finish'):
                result = check_session(root, receipt='session.json', phase=phase)
            self.assertEqual(result['status'], 'candidate')
            self.assertEqual(result['business_acceptance'], 'not-performed')
            self.assertEqual(result['cleanup']['child_processes_started'], 0)
            run.assert_not_called()
            with self.assertRaises(ValueError):
                check_session(root, receipt='session.json', phase='check')

    def test_stale_out_of_scope_and_frozen_drift_block_acceptance(self):
        for mode in ('stale', 'unexpected', 'frozen', 'deleted', 'git-metadata'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'candidate').mkdir()
                (root / 'candidate/protected.txt').write_text('original', encoding='utf-8')
                if mode == 'stale':
                    (root / 'candidate/answer.py').write_text('old', encoding='utf-8')
                self.prepare(root)
                if mode != 'stale':
                    (root / 'candidate/answer.py').write_text('new', encoding='utf-8')
                if mode == 'unexpected':
                    (root / 'candidate/protected.txt').write_text('changed', encoding='utf-8')
                if mode == 'deleted':
                    (root / 'candidate/protected.txt').unlink()
                if mode == 'git-metadata':
                    (root / 'candidate/.git').mkdir()
                    (root / 'candidate/.git/config').write_text('unexpected', encoding='utf-8')
                if mode == 'frozen':
                    (root / 'tasks.md').write_text('changed', encoding='utf-8')
                    with self.assertRaises(ValueError):
                        check_session(root, receipt='session.json', phase='check')
                else:
                    self.assertEqual(check_session(root, receipt='session.json', phase='check')['status'], 'blocked')

    def test_phase_order_and_receipt_boundary_are_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root)
            (root / 'candidate/answer.py').write_text('new', encoding='utf-8')
            for phase in ('refine', 'finish'):
                with self.assertRaises(ValueError):
                    check_session(root, receipt='session.json', phase=phase)
            with self.assertRaises(ValueError):
                prepare_session(root, workspace='candidate', receipt='candidate/receipt.json', tasks=['T-001'],
                                task_files=['tasks.md'], research_files=['research.json'], allowed_outputs=['answer.py'])


class HandshakeTests(unittest.TestCase):
    def test_state_symlink_cannot_write_or_remove_an_external_receipt(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            external = Path(outside) / 'install.json'
            external.write_text('original', encoding='utf-8')
            try:
                (root / 'state').symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(str(exc))
            with patch.object(cli, 'ROOT', root):
                with self.assertRaises(ValueError):
                    cli._write_state('install', {'installed': True})
                self.assertEqual(cli.main(['uninstall', '--apply', '--format', 'json']), 2)
            self.assertEqual(external.read_text(encoding='utf-8'), 'original')

    def test_echoed_prompt_is_not_an_assistant_handshake(self):
        sentinel = 'RF_HOST_HANDSHAKE_CODEX'
        echo = json.dumps({'type': 'item.completed', 'item': {'type': 'user_message', 'text': sentinel}})
        self.assertEqual(assistant_texts(echo, 'codex'), [])
        reply = json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': sentinel}})
        self.assertEqual(assistant_texts(reply, 'codex'), [sentinel])
        self.assertEqual(assistant_texts(json.dumps({'type': 'result', 'is_error': True, 'result': sentinel}), 'claude'), [])
        pi = {'type': 'message_end', 'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': 'PI'}]}}
        self.assertEqual(assistant_texts(json.dumps(pi), 'pi'), ['PI'])

    def test_builder_quota_and_timeout_are_serializable_blocked_results(self):
        with tempfile.TemporaryDirectory() as directory:
            builder = HostBuilder(Path(directory))
            invocation = builder._invocation('codex', 'codex', 'frozen input')
            quota = subprocess.CompletedProcess([], 1, stdout='', stderr='out of credits')
            with patch('subprocess.run', return_value=quota):
                self.assertEqual(builder._invoke(invocation, 'frozen input')['status'], 'blocked')
            with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('codex', 1, output=b'partial', stderr=b'quota')):
                result = builder._invoke(invocation, 'frozen input')
                self.assertEqual(result['cleanup'], 'unknown')
                self.assertIn('partial', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
