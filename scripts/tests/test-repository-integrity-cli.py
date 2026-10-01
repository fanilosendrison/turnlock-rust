#!/usr/bin/env python3
from __future__ import annotations

import importlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

fixture = importlib.import_module("repository-integrity-test-fixture")


def make_runner_fixture(
    temporary: str,
    *,
    child_sources: dict[str, str] | None = None,
) -> Path:
    return fixture.make_runner_fixture(
        temporary,
        support_paths=(
            "AGENTS.md",
            "docs/repository-governance/turnlock-rust-shared-governance-provider.md",
            "docs/repository-governance/turnlock-rust-governance-authority.md",
            "docs/repository-governance/turnlock-rust-governed-objects.md",
            "docs/adr/adr-profile.yaml",
            "docs/adr/adr-051-require-proto-ring-for-applicable-generic-repository-governance.md",
        ),
        child_sources=child_sources,
    )


class RepositoryIntegrityBindingTests(unittest.TestCase):
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

    def test_cli_preserves_undetermined_diagnostic_and_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_runner_fixture(
                temporary,
                child_sources={
                    "scripts/check-authoritative-ref-monotonicity.py":
                        "raise SystemExit(2)\n",
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
            name = "Authoritative Ref Monotonicity effective rules"
            self.assertEqual(1, result.returncode)
            self.assertIn(
                f"validation step undetermined: {name}: command exited with 2",
                combined,
            )
            self.assertNotIn(f"validation step failed: {name}", combined)
            self.assertIn("repository integrity: FAILED", combined)

    def test_cli_preserves_child_stdout_and_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_runner_fixture(
                temporary,
                child_sources={
                    "scripts/tests/test-adr-metadata-provider-binding.py":
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


if __name__ == "__main__":
    unittest.main()
