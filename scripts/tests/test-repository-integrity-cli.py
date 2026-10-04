#!/usr/bin/env python3
from __future__ import annotations

import importlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

fixture = importlib.import_module("repository-integrity-test-fixture")


def run_fixture(
    temporary: str,
    child_sources: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    root = fixture.make_runner_fixture(temporary, child_sources=child_sources)
    return subprocess.run(
        [sys.executable, "scripts/check-repository-integrity.py"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


class RepositoryIntegrityCliTests(unittest.TestCase):
    def test_cli_returns_zero_when_all_profile_commands_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_fixture(temporary)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("repository integrity: OK", result.stdout)

    def test_cli_returns_nonzero_when_profile_command_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_fixture(
                temporary,
                {"scripts/check-formal-traceability.py": "raise SystemExit(7)\n"},
            )
        combined = result.stdout + result.stderr
        self.assertEqual(1, result.returncode)
        self.assertIn("formal_traceability_check", combined)
        self.assertIn("command exited with 7", combined)
        self.assertIn("repository integrity: FAILED", combined)

    def test_cli_preserves_undetermined_and_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_fixture(
                temporary,
                {"scripts/check-authoritative-ref-monotonicity.py": "raise SystemExit(2)\n"},
            )
        combined = result.stdout + result.stderr
        self.assertEqual(1, result.returncode)
        self.assertIn("authoritative_ref_monotonicity_effective_rules", combined)
        self.assertIn("UNDETERMINED", combined)
        self.assertIn("repository integrity: FAILED", combined)

    def test_runner_contains_no_validation_membership(self) -> None:
        source = (fixture.SCRIPT).read_text(encoding="utf-8")
        self.assertNotIn("canonical_steps", source)
        self.assertNotIn("scripts/tests/test-", source)
        self.assertIn("repository_governance_state.load", source)
        self.assertNotIn("repository_integrity.load", source)
        self.assertIn("evaluate_consumer_profile", source)


if __name__ == "__main__":
    unittest.main()
