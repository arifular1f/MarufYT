"""Security regression fixtures; no real keys, passwords or account sessions."""
# Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

spec = importlib.util.spec_from_file_location('secret_scan', Path(__file__).resolve().parents[1] / 'Tools/marufyt_secret_scan.py')
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class SecretScanTests(unittest.TestCase):
    def test_binary_content_is_detected_without_disclosure(self):
        fixture = b'gh' + b'p_' + b'7aB9' * 10
        findings = scanner.scan_bytes(b'\0binary\0' + fixture, ['fixture.bin'])
        self.assertTrue(any(f['type'] == 'GitHub token' for f in findings))
        self.assertNotIn(fixture.decode(), json.dumps(findings))
        self.assertTrue(all('matchSHA256' in f and 'match' not in f for f in findings))

    def test_private_key_and_embedded_token_locations(self):
        fixture = b'-----BEGIN ' + b'PRIVATE KEY-----'
        found = scanner.scan_bytes(b'prefix\0' + fixture, ['archive.bin'])
        self.assertEqual(found[0]['byteOffset'], 7)
        self.assertEqual(found[0]['type'], 'Private key block')

    def test_sensitive_extensions(self):
        for name in ['.env.production', 'client.p8', 'signing.p12', 'test.ipa']:
            self.assertIsNotNone(scanner.SENSITIVE_FILES.search(name), name)

    def test_history_alias_and_index_are_not_missed(self):
        with tempfile.TemporaryDirectory(prefix='marufyt-secret-test-') as directory:
            root = Path(directory)

            def git(*args):
                return subprocess.run(['git', *args], cwd=root, capture_output=True, check=True)

            git('init', '-q')
            git('config', 'user.name', 'Security fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            (root / 'notes.txt').write_text('Identical benign content')
            git('add', 'notes.txt'); git('commit', '-qm', 'benign fixture')
            (root / '.env').write_text('Identical benign content')
            git('add', '.env'); git('commit', '-qm', 'sensitive filename alias')
            git('rm', '-q', '.env'); git('commit', '-qm', 'remove alias')
            fixture = b'gh' + b'p_' + b'8xY2' * 10
            (root / 'staged.txt').write_bytes(fixture)
            git('add', 'staged.txt')
            (root / 'staged.txt').write_text('clean working copy')
            (root / 'new.bin').write_bytes(b'\0' + fixture)
            report = root / 'scan-result.json'
            capture = io.StringIO()
            with mock.patch.object(scanner, 'ROOT', root), mock.patch.object(sys, 'argv', ['scan', str(report)]), contextlib.redirect_stdout(capture):
                exit_code = scanner.main()
            self.assertEqual(exit_code, 1)
            results = json.loads(report.read_text())
            self.assertTrue(any(f.get('path') == '.env' for f in results['findings']))
            self.assertTrue(any('staged.txt' in f.get('paths', []) and f.get('scope') == 'history-or-index' for f in results['findings']))
            self.assertTrue(any('new.bin' in f.get('paths', []) and f.get('scope') == 'working-tree' for f in results['findings']))
            self.assertNotIn(fixture.decode(), report.read_text())
            self.assertNotIn(fixture.decode(), capture.getvalue())
            # A deliberately shallow fixture must fail coverage, not report a
            # misleading full-history pass. Only this temporary repo is changed.
            head = git('rev-parse', 'HEAD').stdout.decode().strip()
            (root / '.git/shallow').write_text(head + '\n')
            with mock.patch.object(scanner, 'ROOT', root), mock.patch.object(sys, 'argv', ['scan']), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(scanner.main(), 2)


if __name__ == '__main__':
    unittest.main()
