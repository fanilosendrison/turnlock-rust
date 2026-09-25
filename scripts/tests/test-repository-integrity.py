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

from proto_ring.repository_integrity import (
    CommandObligation,
    IntegrityProfile,
    IntegrityVerdict,
    ObligationStatus,
    evaluate,
)

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


def shared_evaluate(
    root: Path,
    steps: list[tuple[str, list[str]]],
):
    profile = IntegrityProfile(
        obligations=tuple(
            CommandObligation(
                name=name,
                argv=tuple(argv),
            )
            for name, argv in steps
        ),
        continue_after_non_satisfied=True,
    )
    return evaluate(
        root,
        profile,
        env=os.environ,
    )


def make_committed_git_fixture(temporary: str) -> Path:
    fixture = Path(temporary)

    subprocess.run(
        ["git", "init", "-q", str(fixture)],
        check=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(fixture),
            "config",
            "user.name",
            "Turnlock Repository Integrity Test",
        ],
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
            "turnlock-ri@example.invalid",
        ],
        check=True,
        capture_output=True,
    )

    (fixture / "tracked.txt").write_text(
        "baseline\n",
        encoding="utf-8",
    )

    subprocess.run(
        ["git", "-C", str(fixture), "add", "tracked.txt"],
        check=True,
        capture_output=True,
    )

    subprocess.run(
        [
            "git",
            "-C",
            str(fixture),
            "commit",
            "-q",
            "-m",
            "baseline",
        ],
        check=True,
        capture_output=True,
    )

    return fixture


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


class SharedRepositoryIntegrityShadowTests(unittest.TestCase):
    def test_shadow_clean_non_mutating_success_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(temporary)
            steps = [("noop", python_command("pass"))]

            legacy_errors, legacy_failed = checker.run_validation(
                fixture,
                steps,
            )
            shared = shared_evaluate(
                fixture,
                steps,
            )

            self.assertEqual([], legacy_errors)
            self.assertEqual([], legacy_failed)

            self.assertEqual(
                IntegrityVerdict.PASS,
                shared.verdict,
            )
            self.assertEqual(
                ObligationStatus.SATISFIED,
                shared.obligations[0].status,
            )

    def test_shadow_non_mutating_failure_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(temporary)
            steps = [
                (
                    "failing",
                    python_command("raise SystemExit(7)"),
                )
            ]

            legacy_errors, legacy_failed = checker.run_validation(
                fixture,
                steps,
            )
            shared = shared_evaluate(
                fixture,
                steps,
            )

            self.assertEqual([("failing", 7)], legacy_failed)
            self.assertTrue(
                any(
                    "validation step failed: failing" in error
                    for error in legacy_errors
                ),
                legacy_errors,
            )

            self.assertEqual(
                IntegrityVerdict.NON_PASS,
                shared.verdict,
            )
            self.assertEqual(
                ObligationStatus.VIOLATED,
                shared.obligations[0].status,
            )
            self.assertEqual(
                7,
                shared.obligations[0].returncode,
            )

    def test_shadow_multiple_non_mutating_failures_continue_and_aggregate(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(temporary)
            steps = [
                (
                    "first-failure",
                    python_command("raise SystemExit(3)"),
                ),
                (
                    "second-failure",
                    python_command("raise SystemExit(7)"),
                ),
            ]

            legacy_errors, legacy_failed = checker.run_validation(
                fixture,
                steps,
            )
            shared = shared_evaluate(
                fixture,
                steps,
            )

            self.assertEqual(
                [
                    ("first-failure", 3),
                    ("second-failure", 7),
                ],
                legacy_failed,
            )

            self.assertEqual(
                IntegrityVerdict.NON_PASS,
                shared.verdict,
            )
            self.assertEqual(
                [
                    ObligationStatus.VIOLATED,
                    ObligationStatus.VIOLATED,
                ],
                [
                    result.status
                    for result in shared.obligations
                ],
            )
            self.assertEqual(
                [3, 7],
                [
                    result.returncode
                    for result in shared.obligations
                ],
            )

    def test_shadow_pre_existing_dirty_unchanged_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(temporary)

            (fixture / "tracked.txt").write_text(
                "dirty\n",
                encoding="utf-8",
            )

            (fixture / "untracked.txt").write_text(
                "scratch\n",
                encoding="utf-8",
            )

            steps = [("noop", python_command("pass"))]

            legacy_errors, legacy_failed = checker.run_validation(
                fixture,
                steps,
            )
            shared = shared_evaluate(
                fixture,
                steps,
            )

            self.assertEqual([], legacy_errors)
            self.assertEqual([], legacy_failed)

            self.assertEqual(
                IntegrityVerdict.PASS,
                shared.verdict,
            )
            self.assertEqual(
                ObligationStatus.SATISFIED,
                shared.obligations[0].status,
            )

    def test_shadow_clean_tracked_mutation_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            legacy_fixture = make_committed_git_fixture(
                str(Path(temporary) / "legacy")
            )
            shared_fixture = make_committed_git_fixture(
                str(Path(temporary) / "shared")
            )

            command = python_command(
                "from pathlib import Path\n"
                "Path('tracked.txt').write_text('mutated\\n', encoding='utf-8')"
            )

            legacy_errors, _legacy_failed = checker.run_validation(
                legacy_fixture,
                [("mutate", command)],
            )
            self.assertTrue(
                any(
                    "repository integrity validation modified the worktree"
                    in error
                    for error in legacy_errors
                ),
                legacy_errors,
            )

            shared = shared_evaluate(
                shared_fixture,
                [("mutate", command)],
            )
            self.assertEqual(
                IntegrityVerdict.NON_PASS,
                shared.verdict,
            )
            self.assertEqual(
                ObligationStatus.VIOLATED,
                shared.obligations[0].status,
            )
            self.assertEqual(
                0,
                shared.obligations[0].returncode,
            )
            self.assertNotEqual(
                shared.baseline_state_identity,
                shared.final_state_identity,
            )

    def test_shadow_already_dirty_tracked_content_mutation_is_strengthened(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            legacy_fixture = make_committed_git_fixture(
                str(Path(temporary) / "legacy")
            )
            shared_fixture = make_committed_git_fixture(
                str(Path(temporary) / "shared")
            )

            for fixture in (legacy_fixture, shared_fixture):
                (fixture / "tracked.txt").write_text(
                    "dirty-one\n",
                    encoding="utf-8",
                )

            legacy_status_before = subprocess.run(
                ["git", "-C", str(legacy_fixture), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual(" M tracked.txt\n", legacy_status_before)

            command = python_command(
                "from pathlib import Path\n"
                "Path('tracked.txt').write_text('dirty-two\\n', encoding='utf-8')"
            )

            legacy_errors, legacy_failed = checker.run_validation(
                legacy_fixture,
                [("mutate-dirty", command)],
            )

            legacy_status_after = subprocess.run(
                ["git", "-C", str(legacy_fixture), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual(" M tracked.txt\n", legacy_status_after)
            self.assertEqual([], legacy_errors)
            self.assertEqual([], legacy_failed)

            shared = shared_evaluate(
                shared_fixture,
                [("mutate-dirty", command)],
            )
            self.assertEqual(
                IntegrityVerdict.NON_PASS,
                shared.verdict,
            )
            self.assertEqual(
                ObligationStatus.VIOLATED,
                shared.obligations[0].status,
            )
            self.assertEqual(
                0,
                shared.obligations[0].returncode,
            )
            self.assertNotEqual(
                shared.baseline_state_identity,
                shared.final_state_identity,
            )

    def test_shadow_already_present_untracked_content_mutation_is_strengthened(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            legacy_fixture = make_committed_git_fixture(
                str(Path(temporary) / "legacy")
            )
            shared_fixture = make_committed_git_fixture(
                str(Path(temporary) / "shared")
            )

            for fixture in (legacy_fixture, shared_fixture):
                (fixture / "loose.txt").write_text(
                    "one\n",
                    encoding="utf-8",
                )

            legacy_status_before = subprocess.run(
                ["git", "-C", str(legacy_fixture), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual("?? loose.txt\n", legacy_status_before)

            command = python_command(
                "from pathlib import Path\n"
                "Path('loose.txt').write_text('two\\n', encoding='utf-8')"
            )

            legacy_errors, legacy_failed = checker.run_validation(
                legacy_fixture,
                [("mutate-untracked", command)],
            )

            legacy_status_after = subprocess.run(
                ["git", "-C", str(legacy_fixture), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual("?? loose.txt\n", legacy_status_after)
            self.assertEqual([], legacy_errors)
            self.assertEqual([], legacy_failed)

            shared = shared_evaluate(
                shared_fixture,
                [("mutate-untracked", command)],
            )
            self.assertEqual(
                IntegrityVerdict.NON_PASS,
                shared.verdict,
            )
            self.assertEqual(
                ObligationStatus.VIOLATED,
                shared.obligations[0].status,
            )
            self.assertEqual(
                0,
                shared.obligations[0].returncode,
            )
            self.assertNotEqual(
                shared.baseline_state_identity,
                shared.final_state_identity,
            )


if __name__ == "__main__":
    unittest.main()
