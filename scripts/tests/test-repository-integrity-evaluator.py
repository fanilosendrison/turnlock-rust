#!/usr/bin/env python3
from __future__ import annotations

import importlib
from pathlib import Path
import sys
import tempfile
import unittest

from proto_ring.repository_integrity import (
    CommandBinding,
    ConsumerIntegrityProfile,
    EvaluationContext,
    ObligationStatus,
    ProfileAuthority,
    ValidationDefinition,
    ValidationEnvironmentRealization,
    ValidationInstances,
    evaluate_consumer_profile,
)

fixture = importlib.import_module("repository-integrity-test-fixture")
make_repository = fixture.make_committed_git_fixture


def evaluate_steps(root: Path, steps: list[tuple[str, str, frozenset[int]]]):
    validations = {}
    order = []
    for validation_id, source, undetermined in steps:
        order.append(validation_id)
        validations[validation_id] = ValidationDefinition(
            validation_id,
            "repository_validation",
            (),
            None,
            ValidationInstances("single"),
            CommandBinding("python", ("-c", source), undetermined),
        )
    profile = ConsumerIntegrityProfile(
        root,
        root / "profile.md",
        1,
        ProfileAuthority("repository_integrity_profile", "profile"),
        frozenset({"python"}),
        True,
        validations,
        tuple(order),
        "test-profile",
    )
    realization = ValidationEnvironmentRealization(
        "python", "test-python", (sys.executable,), {}
    )
    return evaluate_consumer_profile(
        root, profile, EvaluationContext({"python": realization})
    )


class RepositoryIntegrityEvaluatorTests(unittest.TestCase):
    def test_non_mutating_pass_is_satisfied(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = make_repository(temporary)
            result = evaluate_steps(root, [("noop", "pass", frozenset())])
            self.assertIs(ObligationStatus.SATISFIED, result.validations[0].status)
            self.assertEqual((), result.errors)

    def test_multiple_failures_are_both_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = make_repository(temporary)
            result = evaluate_steps(
                root,
                [
                    ("first", "raise SystemExit(3)", frozenset()),
                    ("second", "raise SystemExit(7)", frozenset()),
                ],
            )
            self.assertEqual(
                [ObligationStatus.VIOLATED, ObligationStatus.VIOLATED],
                [item.status for item in result.validations],
            )
            self.assertEqual([3, 7], [item.obligations[0].returncode for item in result.validations])

    def test_exit_two_maps_to_undetermined(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = make_repository(temporary)
            result = evaluate_steps(
                root, [("arm", "raise SystemExit(2)", frozenset({2}))]
            )
            self.assertIs(ObligationStatus.UNDETERMINED, result.validations[0].status)

    def test_preexisting_dirty_state_is_admissible(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = make_repository(temporary)
            (root / "tracked.txt").write_text("dirty\n", encoding="utf-8")
            (root / "loose.txt").write_text("scratch\n", encoding="utf-8")
            result = evaluate_steps(root, [("noop", "pass", frozenset())])
            self.assertIs(ObligationStatus.SATISFIED, result.validations[0].status)

    def test_mutation_is_detected_and_stops_later_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = make_repository(temporary)
            marker = Path(temporary) / "later"
            result = evaluate_steps(
                root,
                [
                    (
                        "mutate",
                        "from pathlib import Path; Path('tracked.txt').write_text('changed')",
                        frozenset(),
                    ),
                    (
                        "later",
                        f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')",
                        frozenset(),
                    ),
                ],
            )
            self.assertFalse(marker.exists())
            self.assertTrue(any("repository state changed" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
