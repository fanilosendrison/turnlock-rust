#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
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


CHILD_SCRIPT_PATHS = [
    "scripts/tests/test-adr-metadata.py",
    "scripts/tests/test-formal-traceability.py",
    "scripts/tests/test-normative-terminology.py",
    "scripts/tests/test-repository-integrity.py",
    "scripts/tests/test-git-whitespace.py",
    "scripts/adr-metadata.py",
    "scripts/check-normative-terminology.py",
    "scripts/check-formal-traceability.py",
    "scripts/check-git-whitespace.py",
]


def make_runner_fixture(temporary: str, failing: set[str] | None = None) -> Path:
    fixture = Path(temporary) / "repo"
    fixture.mkdir()
    subprocess.run(["git", "init", "-q", str(fixture)], check=True)
    runner_dir = fixture / "scripts"
    runner_dir.mkdir()
    shutil.copyfile(
        ROOT / "scripts" / "check-repository-integrity.py",
        runner_dir / "check-repository-integrity.py",
    )
    failing = failing or set()
    for relative in CHILD_SCRIPT_PATHS:
        path = fixture / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        code = (
            "import sys\nsys.exit(7)\n"
            if relative in failing
            else "import sys\nsys.exit(0)\n"
        )
        path.write_text(code, encoding="utf-8")
    return fixture


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

    def test_failure_and_mutation_are_both_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_git_fixture(temporary)
            errors, failed = checker.run_validation(
                fixture,
                [
                    (
                        "mutate-and-fail",
                        python_command(
                            "open('tracked.txt', 'a').write('mutation\\n')\n"
                            "raise SystemExit(5)"
                        ),
                    )
                ],
            )
            self.assertEqual([("mutate-and-fail", 5)], failed)
            self.assertTrue(
                any(
                    "validation step failed: mutate-and-fail" in error
                    for error in errors
                ),
                errors,
            )
            self.assertTrue(
                any(
                    "repository integrity validation modified the worktree" in error
                    for error in errors
                ),
                errors,
            )

    def test_canonical_validation_membership_and_order(self) -> None:
        expected = [
            (
                "ADR metadata tests",
                [sys.executable, "scripts/tests/test-adr-metadata.py"],
            ),
            (
                "Formal traceability tests",
                [sys.executable, "scripts/tests/test-formal-traceability.py"],
            ),
            (
                "Normative terminology tests",
                [sys.executable, "scripts/tests/test-normative-terminology.py"],
            ),
            (
                "Repository integrity tests",
                [sys.executable, "scripts/tests/test-repository-integrity.py"],
            ),
            (
                "Git whitespace tests",
                [sys.executable, "scripts/tests/test-git-whitespace.py"],
            ),
            (
                "ADR metadata check",
                [sys.executable, "scripts/adr-metadata.py", "check"],
            ),
            (
                "Normative terminology check",
                [sys.executable, "scripts/check-normative-terminology.py"],
            ),
            (
                "Formal traceability check",
                [sys.executable, "scripts/check-formal-traceability.py"],
            ),
            (
                "Git whitespace check",
                [sys.executable, "scripts/check-git-whitespace.py"],
            ),
        ]
        self.assertEqual(expected, checker.canonical_steps())

    def test_cli_returns_nonzero_when_canonical_child_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_runner_fixture(
                temporary, failing={"scripts/check-formal-traceability.py"}
            )
            result = subprocess.run(
                [sys.executable, "scripts/check-repository-integrity.py"],
                cwd=fixture,
                capture_output=True,
                text=True,
                check=False,
            )
            combined = result.stdout + result.stderr
            self.assertEqual(1, result.returncode)
            self.assertIn("Formal traceability check", combined)
            self.assertIn("exit 7", combined)
            self.assertIn("repository integrity: FAILED", combined)

    def test_cli_returns_zero_when_all_canonical_children_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_runner_fixture(temporary)
            result = subprocess.run(
                [sys.executable, "scripts/check-repository-integrity.py"],
                cwd=fixture,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode)
            self.assertIn("repository integrity: OK", result.stdout)

    def test_whitespace_checker_is_non_mutating_under_purity_guard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_git_fixture(temporary)
            scripts_dir = fixture / "scripts"
            scripts_dir.mkdir()
            whitespace_checker = scripts_dir / "check-git-whitespace.py"
            shutil.copyfile(
                ROOT / "scripts" / "check-git-whitespace.py", whitespace_checker
            )
            saved = {
                key: os.environ.pop(key)
                for key in ("GITHUB_EVENT_NAME", "GITHUB_EVENT_PATH")
                if key in os.environ
            }
            try:
                errors, failed = checker.run_validation(
                    fixture,
                    [("whitespace", [sys.executable, str(whitespace_checker)])],
                )
            finally:
                os.environ.update(saved)
            self.assertEqual([], errors)
            self.assertEqual([], failed)


if __name__ == "__main__":
    unittest.main()
