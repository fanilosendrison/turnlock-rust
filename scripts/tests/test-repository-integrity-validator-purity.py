#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class RepositoryIntegrityValidatorPurityTests(unittest.TestCase):
    def test_native_whitespace_checker_is_non_mutating(self) -> None:
        command = ["git", "-C", str(ROOT), "status", "--porcelain=v2", "-z"]
        before = subprocess.run(command, check=True, capture_output=True).stdout
        result = subprocess.run(
            [sys.executable, "scripts/check-git-whitespace.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        after = subprocess.run(command, check=True, capture_output=True).stdout
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
