"""Trust-boundary tests for the pinned bootstrap; no network or target execution."""
import copy
import hashlib
import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('bootstrap', Path(__file__).resolve().parents[1] / 'Tools/bootstrap_pinned.py')
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


class BootstrapTests(unittest.TestCase):
    def test_lock_has_no_moving_archive_refs(self):
        lock = json.loads((bootstrap.ROOT / 'Tools/toolchain.lock.json').read_text())
        bootstrap.validate_lock(lock)
        changed = copy.deepcopy(lock)
        changed['archives'][0]['url'] = 'https://github.com/owner/repo/releases/latest/download/tool.tar.xz'
        with self.assertRaises(ValueError):
            bootstrap.validate_lock(changed)

    def test_tampered_cache_rejected_before_extraction(self):
        with tempfile.TemporaryDirectory(prefix='marufyt-pin-test-') as directory:
            cache = Path(directory)
            expected = hashlib.sha256(b'original').hexdigest()
            (cache / (expected + '.tar.xz')).write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'integrity'):
                bootstrap.verified_download({'sha256': expected, 'bytes': 8}, cache)

    def test_tar_traversal_rejected(self):
        with tempfile.TemporaryDirectory(prefix='marufyt-pin-test-') as directory:
            root = Path(directory); archive = root / 'test.tar'
            with tarfile.open(archive, 'w') as t:
                member = tarfile.TarInfo('../outside'); member.size = 1
                t.addfile(member, io.BytesIO(b'x'))
            with self.assertRaises(ValueError):
                bootstrap.safe_extract(archive, root / 'dest', 'sdk')
            self.assertFalse((root / 'outside').exists())

    def test_escaping_symlink_rejected(self):
        with tempfile.TemporaryDirectory(prefix='marufyt-pin-test-') as directory:
            root = Path(directory); archive = root / 'test.tar'
            with tarfile.open(archive, 'w') as t:
                member = tarfile.TarInfo('sdk/link'); member.type = tarfile.SYMTYPE; member.linkname = '../../outside'
                t.addfile(member)
            with self.assertRaises((tarfile.FilterError, OSError)):
                bootstrap.safe_extract(archive, root / 'dest', 'sdk')


if __name__ == '__main__':
    unittest.main()
