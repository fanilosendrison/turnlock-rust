#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "docs/repository-governance/turnlock-rust-repository-integrity.md"
EXPECTED_ORDER = (
    "adr_metadata_provider_binding_tests",
    "adr_metadata_profile_validation_tests",
    "adr_metadata_migration_evidence_tests",
    "adr_metadata_generated_index_tests",
    "adr_metadata_annotated_history_tests",
    "exact_evidence_binding_tests",
    "structured_governance_tests",
    "proto_ring_binding_registry_tests",
    "proto_ring_provider_tests",
    "governed_objects_profile_tests",
    "normative_terminology_tests",
    "repository_integrity_binding_tests",
    "repository_integrity_evaluator_tests",
    "repository_integrity_cli_tests",
    "repository_integrity_validator_purity_tests",
    "governance_test_module_size_tests",
    "git_whitespace_tests",
    "adr_metadata_check",
    "accepted_adr_body_immutability",
    "proto_ring_binding_registry_currentness",
    "proto_ring_provider_currentness",
    "structured_governance_check",
    "governance_authority_profile",
    "governed_objects_profile",
    "authoritative_ref_monotonicity_effective_rules",
    "normative_terminology_check",
    "git_whitespace_check",
    "assurance_archive_tests",
    "assurance_archive_custody",
)


def profile() -> dict:
    text = PROFILE.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n", 2)[1])["repository_integrity"]


class RepositoryIntegrityBindingTests(unittest.TestCase):
    def test_persistent_profile_is_sole_membership_and_order_authority(self) -> None:
        value = profile()
        self.assertEqual(EXPECTED_ORDER, tuple(value["validations"]))
        self.assertEqual(EXPECTED_ORDER, tuple(value["order"]))
        self.assertTrue(value["continue_after_non_satisfied"])

    def test_accepted_adr_body_uses_native_wrapper(self) -> None:
        arguments = profile()["validations"]["accepted_adr_body_immutability"][
            "command"
        ]["arguments"]
        self.assertEqual(["scripts/check-accepted-adr-body.py"], arguments)

    def test_provider_currentness_validations_are_adjacent(self) -> None:
        order = profile()["order"]
        index = order.index("proto_ring_binding_registry_currentness")
        self.assertEqual("proto_ring_provider_currentness", order[index + 1])

    def test_arm_exit_two_is_the_only_undetermined_exit(self) -> None:
        for validation_id, definition in profile()["validations"].items():
            expected = (
                [2]
                if validation_id == "authoritative_ref_monotonicity_effective_rules"
                else []
            )
            self.assertEqual(expected, definition["command"]["undetermined_exit_codes"])

    def test_runtime_path_is_not_persistent_identity(self) -> None:
        carrier = PROFILE.read_text(encoding="utf-8")
        self.assertNotIn(sys.executable, carrier)
        self.assertNotIn(".venv/bin/python", carrier)

    def test_requirements_contains_no_provider_declaration(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertNotIn("proto-ring", requirements)
        self.assertNotIn("proto_ring", requirements)

    def test_ci_prepares_provider_before_repository_integrity(self) -> None:
        workflow = (ROOT / ".github/workflows/repository-integrity.yml").read_text(
            encoding="utf-8"
        )
        preparation = "python3 scripts/prepare-proto-ring-provider.py"
        integrity = "python3 scripts/check-repository-integrity.py"
        self.assertIn(preparation, workflow)
        self.assertLess(workflow.index(preparation), workflow.index(integrity))


if __name__ == "__main__":
    unittest.main()
