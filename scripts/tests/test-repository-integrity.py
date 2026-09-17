#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-repository-integrity.py"

spec = importlib.util.spec_from_file_location("repository_integrity", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def make_git_fixture(temporary: str) -> Path:
    fixture = Path(temporary)
    subprocess.run(["git", "init", "-q", str(fixture)], check=True)
    (fixture / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(fixture), "add", "tracked.txt"],
        check=True,
        capture_output=True,
    )
    return fixture


def python_command(source: str) -> list[str]:
    return [sys.executable, "-c", source]


class RepositoryIntegrityRunnerTests(unittest.TestCase):
    def test_non_mutating_command_passes_purity_guard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_git_fixture(temporary)
            errors, failed = checker.run_validation(
                fixture, [("noop", python_command("pass"))]
            )
            self.assertEqual([], errors)
            self.assertEqual([], failed)

    def test_tracked_file_mutation_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_git_fixture(temporary)
            errors, _ = checker.run_validation(
                fixture,
                [
                    (
                        "mutate",
                        python_command(
                            "open('tracked.txt', 'a').write('mutation\\n')"
                        ),
                    )
                ],
            )
            self.assertTrue(
                any(
                    "repository integrity validation modified the worktree" in error
                    for error in errors
                ),
                errors,
            )

    def test_untracked_file_creation_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_git_fixture(temporary)
            errors, _ = checker.run_validation(
                fixture,
                [
                    (
                        "create",
                        python_command("open('created.txt', 'w').write('new\\n')"),
                    )
                ],
            )
            self.assertTrue(
                any(
                    "repository integrity validation modified the worktree" in error
                    for error in errors
                ),
                errors,
            )

    def test_tracked_file_deletion_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_git_fixture(temporary)
            errors, _ = checker.run_validation(
                fixture,
                [
                    (
                        "delete",
                        python_command(
                            "import os\nos.remove('tracked.txt')"
                        ),
                    )
                ],
            )
            self.assertTrue(
                any(
                    "repository integrity validation modified the worktree" in error
                    for error in errors
                ),
                errors,
            )

    def test_failing_step_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_git_fixture(temporary)
            errors, failed = checker.run_validation(
                fixture,
                [("failing", python_command("raise SystemExit(3)"))],
            )
            self.assertTrue(
                any(
                    "validation step failed: failing" in error
                    and "3" in error
                    for error in errors
                ),
                errors,
            )
            self.assertEqual([("failing", 3)], failed)

    def test_pre_existing_dirty_state_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_git_fixture(temporary)
            (fixture / "tracked.txt").write_text("dirty\n", encoding="utf-8")
            (fixture / "untracked.txt").write_text("scratch\n", encoding="utf-8")
            errors, failed = checker.run_validation(
                fixture, [("noop", python_command("pass"))]
            )
            self.assertEqual([], errors)
            self.assertEqual([], failed)


if __name__ == "__main__":
    unittest.main()
