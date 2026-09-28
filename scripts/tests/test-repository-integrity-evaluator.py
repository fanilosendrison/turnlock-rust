#!/usr/bin/env python3
from __future__ import annotations

import importlib
from pathlib import Path
import subprocess
import tempfile
import unittest

fixture = importlib.import_module("repository-integrity-test-fixture")
checker = fixture.checker
make_committed_git_fixture = fixture.make_committed_git_fixture
python_command = fixture.python_command


class RepositoryIntegrityBindingTests(unittest.TestCase):
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

    def test_undetermined_exit_is_not_reported_as_failed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_committed_git_fixture(temporary)

            errors, failed = checker.run_validation(
                fixture,
                [
                    (
                        "Authoritative Ref Monotonicity effective rules",
                        python_command("raise SystemExit(2)"),
                    )
                ],
            )

            self.assertEqual([], failed)
            self.assertEqual(
                [
                    "validation step undetermined: "
                    "Authoritative Ref Monotonicity effective rules: "
                    "command exited with 2"
                ],
                errors,
            )
            self.assertNotIn(
                "validation step failed: "
                "Authoritative Ref Monotonicity effective rules",
                "\n".join(errors),
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


if __name__ == "__main__":
    unittest.main()
