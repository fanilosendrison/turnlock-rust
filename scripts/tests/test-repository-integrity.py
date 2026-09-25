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
    IntegrityVerdict,
    ObligationStatus,
)

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-repository-integrity.py"

spec = importlib.util.spec_from_file_location(
    "repository_integrity",
    SCRIPT,
)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")

checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


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


def python_command(source: str) -> list[str]:
    return [
        sys.executable,
        "-c",
        source,
    ]


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


def make_runner_fixture(
    temporary: str,
    *,
    child_sources: dict[str, str] | None = None,
) -> Path:
    fixture = Path(temporary) / "repo"
    fixture.mkdir()

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
            "Turnlock Runner Test",
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
            "turnlock-runner@example.invalid",
        ],
        check=True,
        capture_output=True,
    )

    runner_dir = fixture / "scripts"
    runner_dir.mkdir()

    shutil.copyfile(
        ROOT / "scripts" / "check-repository-integrity.py",
        runner_dir / "check-repository-integrity.py",
    )

    child_sources = child_sources or {}

    for relative in CHILD_SCRIPT_PATHS:
        path = fixture / relative
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            child_sources.get(
                relative,
                "import sys\nsys.exit(0)\n",
            ),
            encoding="utf-8",
        )

    return fixture


class RepositoryIntegrityBindingTests(unittest.TestCase):
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

        self.assertEqual(
            expected,
            checker.canonical_steps(),
        )

    def test_shared_profile_preserves_membership_order_and_continuation(
        self,
    ) -> None:
        steps = checker.canonical_steps()
        profile = checker._integrity_profile(steps)

        self.assertTrue(
            profile.continue_after_non_satisfied
        )

        self.assertEqual(
            [name for name, _argv in steps],
            [
                obligation.name
                for obligation in profile.obligations
            ],
        )

        self.assertEqual(
            [tuple(argv) for _name, argv in steps],
            [
                obligation.argv
                for obligation in profile.obligations
            ],
        )

        for obligation in profile.obligations:
            self.assertEqual(
                frozenset(),
                obligation.undetermined_exit_codes,
            )

    def test_non_mutating_pass_maps_to_no_local_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(temporary)

            errors, failed = checker.run_validation(
                fixture,
                [("noop", python_command("pass"))],
            )

            self.assertEqual([], errors)
            self.assertEqual([], failed)

    def test_multiple_non_mutating_failures_are_both_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(temporary)

            errors, failed = checker.run_validation(
                fixture,
                [
                    (
                        "first-failure",
                        python_command("raise SystemExit(3)"),
                    ),
                    (
                        "second-failure",
                        python_command("raise SystemExit(7)"),
                    ),
                ],
            )

            self.assertEqual(
                [
                    ("first-failure", 3),
                    ("second-failure", 7),
                ],
                failed,
            )
            self.assertIn(
                "validation step failed: first-failure (exit 3)",
                errors,
            )
            self.assertIn(
                "validation step failed: second-failure (exit 7)",
                errors,
            )

    def test_pre_existing_dirty_state_remains_admissible(self) -> None:
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

            errors, failed = checker.run_validation(
                fixture,
                [("noop", python_command("pass"))],
            )

            self.assertEqual([], errors)
            self.assertEqual([], failed)

    def test_already_dirty_tracked_mutation_is_rejected_by_local_binding(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(temporary)

            (fixture / "tracked.txt").write_text(
                "dirty-one\n",
                encoding="utf-8",
            )

            status_before = subprocess.run(
                ["git", "-C", str(fixture), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual(" M tracked.txt\n", status_before)

            errors, failed = checker.run_validation(
                fixture,
                [
                    (
                        "mutate-dirty",
                        python_command(
                            "from pathlib import Path\n"
                            "Path('tracked.txt').write_text('dirty-two\\n', encoding='utf-8')"
                        ),
                    )
                ],
            )

            status_after = subprocess.run(
                ["git", "-C", str(fixture), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual(" M tracked.txt\n", status_after)

            self.assertEqual([], failed)
            self.assertIn(
                "repository integrity validation modified the worktree",
                errors,
            )
            self.assertTrue(
                any(
                    "repository state changed during obligation" in error
                    for error in errors
                ),
                errors,
            )

    def test_already_present_untracked_mutation_is_rejected_by_local_binding(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(temporary)

            (fixture / "loose.txt").write_text(
                "one\n",
                encoding="utf-8",
            )

            status_before = subprocess.run(
                ["git", "-C", str(fixture), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual("?? loose.txt\n", status_before)

            errors, failed = checker.run_validation(
                fixture,
                [
                    (
                        "mutate-untracked",
                        python_command(
                            "from pathlib import Path\n"
                            "Path('loose.txt').write_text('two\\n', encoding='utf-8')"
                        ),
                    )
                ],
            )

            status_after = subprocess.run(
                ["git", "-C", str(fixture), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual("?? loose.txt\n", status_after)

            self.assertEqual([], failed)
            self.assertIn(
                "repository integrity validation modified the worktree",
                errors,
            )
            self.assertTrue(
                any(
                    "repository state changed during obligation" in error
                    for error in errors
                ),
                errors,
            )

    def test_mutation_stops_later_local_step(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(str(Path(temporary) / "repo"))
            marker = Path(temporary) / "later.marker"

            errors, _failed = checker.run_validation(
                fixture,
                [
                    (
                        "mutate",
                        python_command(
                            "from pathlib import Path\n"
                            "Path('tracked.txt').write_text('mutated\\n', encoding='utf-8')"
                        ),
                    ),
                    (
                        "later",
                        python_command(
                            "from pathlib import Path\n"
                            f"Path({str(marker)!r}).write_text('ran')"
                        ),
                    ),
                ],
            )

            self.assertFalse(marker.exists())
            self.assertIn(
                "repository integrity validation modified the worktree",
                errors,
            )

    def test_failure_and_mutation_are_both_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(temporary)

            errors, failed = checker.run_validation(
                fixture,
                [
                    (
                        "mutate-and-fail",
                        python_command(
                            "from pathlib import Path\n"
                            "Path('tracked.txt').write_text('mutated\\n', encoding='utf-8')\n"
                            "raise SystemExit(5)"
                        ),
                    )
                ],
            )

            self.assertEqual([("mutate-and-fail", 5)], failed)
            self.assertIn(
                "validation step failed: mutate-and-fail (exit 5)",
                errors,
            )
            self.assertIn(
                "repository integrity validation modified the worktree",
                errors,
            )

    def test_cli_returns_zero_when_all_canonical_children_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_runner_fixture(temporary)

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/check-repository-integrity.py",
                ],
                cwd=fixture,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode)
            self.assertIn("repository integrity: OK", result.stdout)

    def test_cli_returns_nonzero_when_canonical_child_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_runner_fixture(
                temporary,
                child_sources={
                    "scripts/check-formal-traceability.py":
                        "import sys\nsys.exit(7)\n",
                },
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/check-repository-integrity.py",
                ],
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

    def test_cli_preserves_child_stdout_and_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_runner_fixture(
                temporary,
                child_sources={
                    "scripts/tests/test-adr-metadata.py":
                        (
                            "import sys\n"
                            "print('TURNLOCK-CHILD-STDOUT', flush=True)\n"
                            "print('TURNLOCK-CHILD-STDERR', file=sys.stderr, flush=True)\n"
                            "sys.exit(0)\n"
                        ),
                },
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/check-repository-integrity.py",
                ],
                cwd=fixture,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode)
            self.assertIn("TURNLOCK-CHILD-STDOUT", result.stdout)
            self.assertIn("TURNLOCK-CHILD-STDERR", result.stderr)

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

    def test_requirements_pin_exact_repository_integrity_provider(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "proto-ring @ git+https://github.com/fanilosendrison/proto-ring.git@5b0d3a3493e01a4b9569ded7665d7a44a444bf35",
            requirements.splitlines(),
        )

        self.assertNotIn(
            "8784935272db7fbde20d8cef603c203fb2457d3d",
            requirements,
        )


if __name__ == "__main__":
    unittest.main()
