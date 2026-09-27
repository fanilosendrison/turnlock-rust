#!/usr/bin/env python3
from __future__ import annotations

import importlib
import os
import shutil
import sys
import tempfile
import unittest

fixture = importlib.import_module("repository-integrity-test-fixture")
ROOT = fixture.ROOT
checker = fixture.checker
make_committed_git_fixture = fixture.make_committed_git_fixture


class RepositoryIntegrityBindingTests(unittest.TestCase):
    def test_whitespace_checker_is_non_mutating_under_shared_binding(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(temporary)

            scripts_dir = fixture / "scripts"
            scripts_dir.mkdir()

            whitespace_checker = scripts_dir / "check-git-whitespace.py"

            shutil.copyfile(
                ROOT / "scripts" / "check-git-whitespace.py",
                whitespace_checker,
            )

            saved = {
                key: os.environ.pop(key)
                for key in ("GITHUB_EVENT_NAME", "GITHUB_EVENT_PATH")
                if key in os.environ
            }

            try:
                errors, failed = checker.run_validation(
                    fixture,
                    [
                        (
                            "whitespace",
                            [
                                sys.executable,
                                str(whitespace_checker),
                            ],
                        )
                    ],
                )
            finally:
                os.environ.update(saved)

            self.assertEqual([], errors)
            self.assertEqual([], failed)


if __name__ == "__main__":
    unittest.main()
