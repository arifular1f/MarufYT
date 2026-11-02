"""Compile and run Tests/native/test_layout_math.c with the host C compiler.

Copyright (c) 2026 arifular1f. MIT License; see LICENSE.

Set MARUFYT_REQUIRE_NATIVE=1 (CI does) to fail instead of skipping when no
C compiler is available. These tests cover pure geometry and preference
decisions only; they do not run UIKit.
"""
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Tests" / "native" / "test_layout_math.c"
INCLUDE = ROOT / "Tweak" / "MarufYT" / "Design"


def compiler():
    for name in ("cc", "gcc", "clang"):
        found = shutil.which(name)
        if found:
            return found
    return None


class NativeLayoutMathTests(unittest.TestCase):
    def test_layout_math(self):
        cc = compiler()
        if cc is None:
            if os.environ.get("MARUFYT_REQUIRE_NATIVE") == "1":
                self.fail("no C compiler found but MARUFYT_REQUIRE_NATIVE=1")
            self.skipTest("no C compiler available")
        with tempfile.TemporaryDirectory() as directory:
            binary = pathlib.Path(directory) / "test_layout_math"
            build = subprocess.run(
                [cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O1",
                 "-I", str(INCLUDE), str(SOURCE), "-lm", "-o", str(binary)],
                capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr + build.stdout)
            run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=120)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn(" 0 failures", run.stdout)


if __name__ == "__main__":
    unittest.main()
