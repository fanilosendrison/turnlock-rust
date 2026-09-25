#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-git-whitespace.py"


def make_fixture(temporary: str) -> Path:
    fixture = Path(temporary) / "repo"
    fixture.mkdir()

    subprocess.run(
        ["git", "init", "-q", str(fixture)],
        check=True,
    )

    subprocess.run(
        ["git", "-C", str(fixture), "config", "user.name", "TURNLOCK Test"],
        check=True,
        capture_output=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(fixture),
            "config",
            "user.email",
            "turnlock@example.invalid",
        ],
        check=True,
        capture_output=True,
    )

    return fixture


def commit_all(fixture: Path, message: str) -> None:
    subprocess.run(
        ["git", "-C", str(fixture), "add", "-A"],
        check=True,
        capture_output=True,
    )

    subprocess.run(
        ["git", "-C", str(fixture), "commit", "-q", "-m", message],
        check=True,
        capture_output=True,
    )


class GitWhitespaceBindingTests(unittest.TestCase):
    def test_cli_propagates_provider_whitespace_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)

            scripts_dir = fixture / "scripts"
            scripts_dir.mkdir()

            shutil.copyfile(
                SCRIPT,
                scripts_dir / "check-git-whitespace.py",
            )

            (fixture / "clean.txt").write_text(
                "clean\n",
                encoding="utf-8",
            )

            commit_all(fixture, "clean")

            (fixture / "clean.txt").write_text(
                "clean   \n",
                encoding="utf-8",
            )

            env = dict(os.environ)
            env.pop("GITHUB_EVENT_NAME", None)
            env.pop("GITHUB_EVENT_PATH", None)

            result = subprocess.run(
                [sys.executable, "scripts/check-git-whitespace.py"],
                cwd=fixture,
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn(
                "git whitespace check: FAILED",
                result.stdout,
            )
            self.assertIn(
                "clean.txt:1",
                result.stdout,
            )


if __name__ == "__main__":
    unittest.main()
