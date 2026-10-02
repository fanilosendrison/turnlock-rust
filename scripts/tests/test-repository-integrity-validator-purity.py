#!/usr/bin/env python3
from __future__ import annotations

import importlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

fixture = importlib.import_module("repository-integrity-test-fixture")
ROOT = fixture.ROOT
make_repository = fixture.make_committed_git_fixture


class RepositoryIntegrityValidatorPurityTests(unittest.TestCase):
    def test_whitespace_checker_is_non_mutating(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = make_repository(temporary)
            scripts = root / "scripts"
            scripts.mkdir()
            checker = scripts / "check-git-whitespace.py"
            shutil.copyfile(ROOT / "scripts/check-git-whitespace.py", checker)
            before = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            result = subprocess.run(
                [sys.executable, str(checker)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            after = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
