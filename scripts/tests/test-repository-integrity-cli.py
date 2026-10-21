#!/usr/bin/env python3
from __future__ import annotations

import ast
import contextlib
import importlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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
                {"scripts/check-assurance-archive.py": "raise SystemExit(7)\n"},
            )
        combined = result.stdout + result.stderr
        self.assertEqual(1, result.returncode)
        self.assertIn("assurance_archive_custody", combined)
        self.assertIn("VIOLATED", combined)
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

    def test_inconsistent_pass_projection_fails_closed(self) -> None:
        satisfied = {
            "verdict": "PASS",
            "state_relation": "EQUAL",
            "state_coherence_halt": False,
            "validations": [
                {"id": "probe", "status": "SATISFIED", "obligations": []}
            ],
            "obligations": [],
        }
        cases = (
            {"verdict": "PASS"},
            {**satisfied, "state_coherence_halt": True},
            {
                **satisfied,
                "validations": [
                    {"id": "probe", "status": "VIOLATED", "obligations": []}
                ],
            },
            {
                **satisfied,
                "validations": [
                    {"id": "", "status": "SATISFIED", "obligations": []}
                ],
            },
            {
                **satisfied,
                "validations": [
                    {"id": "probe", "status": "SATISFIED", "obligations": []},
                    {"id": "probe", "status": "SATISFIED", "obligations": []},
                ],
            },
            {
                **satisfied,
                "obligations": [
                    {"id": "probe", "status": "UNDETERMINED"}
                ],
            },
            {
                **satisfied,
                "validations": [
                    {
                        "id": "probe",
                        "status": "SATISFIED",
                        "obligations": [
                            {"id": "probe", "status": "VIOLATED"}
                        ],
                    }
                ],
            },
            {
                **satisfied,
                "obligations": [
                    {
                        "id": "probe",
                        "status": "SATISFIED",
                        "executed": False,
                        "exit_code": "0",
                    }
                ],
            },
            {
                **satisfied,
                "obligations": [
                    {
                        "id": "probe",
                        "status": "SATISFIED",
                        "executed": True,
                        "exit_code": "7",
                    }
                ],
            },
        )
        for result in cases:
            with self.subTest(result=result), mock.patch.object(
                fixture.checker, "run_validation", return_value=result
            ), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                io.StringIO()
            ):
                self.assertEqual(1, fixture.checker.main())

    def test_empty_projection_and_unreadable_oracle_fail_closed(self) -> None:
        empty = {
            "verdict": "PASS",
            "state_relation": "EQUAL",
            "state_coherence_halt": False,
            "validations": [],
            "obligations": [],
        }
        with mock.patch.object(
            fixture.checker, "_expected_validation_ids", return_value=None
        ):
            self.assertFalse(fixture.checker._coherent_pass(empty))

        expected = fixture.checker._expected_validation_ids(fixture.ROOT)
        self.assertIsNotNone(expected)
        projection = {
            **empty,
            "validations": [
                {"id": validation_id, "status": "SATISFIED", "obligations": []}
                for validation_id in expected
            ],
        }
        self.assertFalse(fixture.checker._coherent_pass(projection, fixture.ROOT))

    def test_coherence_and_top_level_obligation_diagnostics_are_preserved(self) -> None:
        result = {
            "verdict": "NON_PASS",
            "state_relation": "CHANGED",
            "state_coherence_halt": True,
            "validations": [],
            "obligations": [
                {
                    "id": "probe",
                    "status": "VIOLATED",
                    "executed": True,
                    "exit_code": "9",
                }
            ],
        }
        diagnostics = fixture.checker._diagnostics(result)
        self.assertIn("repository state coherence halted: CHANGED", diagnostics)
        self.assertIn("obligation probe: VIOLATED (command exited with 9)", diagnostics)

    def test_runner_contains_no_validation_membership(self) -> None:
        source = (fixture.SCRIPT).read_text(encoding="utf-8")
        self.assertNotIn("canonical_steps", source)
        self.assertNotIn("scripts/tests/test-", source)
        self.assertIn('"repository-integrity.evaluate"', source)
        tree = ast.parse(source)
        imports = [
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module is not None
            and (node.module == "proto_ring" or node.module.startswith("proto_ring."))
        ]
        imports.extend(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
            if alias.name == "proto_ring" or alias.name.startswith("proto_ring.")
        )
        self.assertEqual([], imports)


if __name__ == "__main__":
    unittest.main()
