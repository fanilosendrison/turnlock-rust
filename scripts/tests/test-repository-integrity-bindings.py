#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
import unittest

fixture = importlib.import_module("repository-integrity-test-fixture")
ROOT = fixture.ROOT
checker = fixture.checker

LEGACY_ARGUMENTS = (
    ("scripts/tests/test-adr-metadata-provider-binding.py",),
    ("scripts/tests/test-adr-metadata-profile-validation.py",),
    ("scripts/tests/test-adr-metadata-migration-evidence.py",),
    ("scripts/tests/test-adr-metadata-generated-index.py",),
    ("scripts/tests/test-adr-metadata-annotated-history.py",),
    ("scripts/tests/test-formal-traceability.py",),
    ("scripts/tests/test-exact-evidence-binding.py",),
    ("scripts/tests/test-governed-objects.py",),
    ("scripts/tests/test-normative-terminology.py",),
    ("scripts/tests/test-repository-integrity-bindings.py",),
    ("scripts/tests/test-repository-integrity-evaluator.py",),
    ("scripts/tests/test-repository-integrity-cli.py",),
    ("scripts/tests/test-repository-integrity-validator-purity.py",),
    ("scripts/tests/test-governance-test-module-size.py",),
    ("scripts/tests/test-git-whitespace.py",),
    ("scripts/adr-metadata.py", "check"),
    ("-m", "proto_ring.accepted_adr_body"),
    ("scripts/check-governance-authority.py",),
    ("scripts/check-governed-objects.py",),
    ("scripts/check-authoritative-ref-monotonicity.py",),
    ("scripts/check-normative-terminology.py",),
    ("scripts/check-formal-traceability.py",),
    ("scripts/check-git-whitespace.py",),
)


class RepositoryIntegrityBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = checker.load_profile(ROOT)

    def test_persistent_profile_is_sole_membership_and_order_authority(self) -> None:
        self.assertEqual(set(self.profile.validations), set(self.profile.order))
        self.assertEqual(29, len(self.profile.order))
        self.assertTrue(self.profile.continue_after_non_satisfied)
        self.assertNotIn("canonical_steps", checker.__dict__)
        self.assertNotIn("UNDETERMINED_EXIT_CODES_BY_STEP", checker.__dict__)

    def test_every_legacy_command_remains_in_original_relative_order(self) -> None:
        ordered_arguments = [
            self.profile.validations[validation_id].command.arguments
            for validation_id in self.profile.order
        ]
        cursor = 0
        for arguments in LEGACY_ARGUMENTS:
            cursor = ordered_arguments.index(arguments, cursor) + 1

    def test_additive_migration_validations_are_mandatory(self) -> None:
        for validation_id in (
            "structured_governance_tests",
            "proto_ring_binding_registry_tests",
            "proto_ring_provider_tests",
            "proto_ring_binding_registry_currentness",
            "proto_ring_provider_currentness",
            "structured_governance_check",
        ):
            self.assertIn(validation_id, self.profile.validations)

    def test_provider_currentness_validations_are_adjacent_and_distinct(self) -> None:
        binding_index = self.profile.order.index(
            "proto_ring_binding_registry_currentness"
        )
        self.assertEqual(
            "proto_ring_provider_currentness",
            self.profile.order[binding_index + 1],
        )
        self.assertEqual(
            ("scripts/check-proto-ring-binding-registry.py",),
            self.profile.validations[
                "proto_ring_binding_registry_currentness"
            ].command.arguments,
        )
        self.assertEqual(
            ("scripts/check-proto-ring-provider.py",),
            self.profile.validations[
                "proto_ring_provider_currentness"
            ].command.arguments,
        )

    def test_arm_exit_two_is_the_only_undetermined_exit(self) -> None:
        for validation_id, definition in self.profile.validations.items():
            expected = (
                frozenset({2})
                if validation_id == "authoritative_ref_monotonicity_effective_rules"
                else frozenset()
            )
            self.assertEqual(expected, definition.command.undetermined_exit_codes)

    def test_runtime_environment_path_is_not_persistent_identity(self) -> None:
        self.assertEqual(frozenset({"turnlock_python"}), self.profile.environments)
        carrier = self.profile.carrier.read_text(encoding="utf-8")
        self.assertNotIn(sys.executable, carrier)
        self.assertNotIn(".venv/bin/python", carrier)

    def test_requirements_pins_final_exact_provider(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn(
            "proto-ring @ git+https://github.com/fanilosendrison/"
            "proto-ring.git@dedb01a3a9b7a18930c9da75afa3773b5ad67f69",
            requirements.splitlines(),
        )

    def test_arm_local_binding_no_longer_duplicates_contract_pin(self) -> None:
        binding = (
            ROOT
            / "docs/repository-governance/turnlock-rust-authoritative-ref-monotonicity.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("contract:", binding)
        self.assertIn("ruleset_id: 24106121", binding)


if __name__ == "__main__":
    unittest.main()
