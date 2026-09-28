#!/usr/bin/env python3
from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

RETIRED_TEST_MODULES = (
    "scripts/tests/test-adr-metadata.py",
    "scripts/tests/test-repository-integrity.py",
)

PRESERVED_TEST_MODULES = (
    "scripts/tests/test-adr-metadata-provider-binding.py",
    "scripts/tests/test-adr-metadata-profile-validation.py",
    "scripts/tests/test-adr-metadata-migration-evidence.py",
    "scripts/tests/test-adr-metadata-generated-index.py",
    "scripts/tests/test-adr-metadata-annotated-history.py",
    "scripts/tests/test-repository-integrity-bindings.py",
    "scripts/tests/test-repository-integrity-evaluator.py",
    "scripts/tests/test-repository-integrity-cli.py",
    "scripts/tests/test-repository-integrity-validator-purity.py",
)

REPLACEMENT_SOURCE_MODULES = (
    "scripts/check-authoritative-ref-monotonicity.py",
    "scripts/tests/adr-metadata-test-fixture.py",
    *PRESERVED_TEST_MODULES[:5],
    "scripts/tests/repository-integrity-test-fixture.py",
    *PRESERVED_TEST_MODULES[5:],
    "scripts/tests/test-governance-test-module-size.py",
)

EXPECTED_LEGACY_TEST_IDENTITIES = (
    "AdrMetadataTests.test_repository_passes_full_profile",
    "AdrMetadataTests.test_shared_primitives_are_bound_to_pinned_provider",
    "AdrMetadataTests.test_profile_path_resolution_delegates_to_shared_provider",
    "AdrMetadataTests.test_adr_051_resolves_and_outside_same_id_is_ignored",
    "AdrMetadataTests.test_calendar_aware_schema_validation_rejects_invalid_dates",
    "AdrMetadataTests.test_body_digest_uses_exact_context_suffix",
    "AdrMetadataTests.test_unknown_and_stale_legacy_entries_fail_closed",
    "AdrMetadataTests.test_empty_overlay_cannot_disable_base_schema_validation",
    "AdrMetadataTests.test_matching_overlay_id_without_local_constraints_fails_closed",
    "AdrMetadataTests.test_misnamed_adr_candidate_is_not_ignored",
    "AdrMetadataTests.test_fabricated_migration_baseline_is_rejected",
    "AdrMetadataTests.test_migration_evidence_preserves_exact_h1_to_eof_payload",
    "AdrMetadataTests.test_renderer_projects_outgoing_and_derived_incoming_relations",
    "AdrMetadataTests.test_stale_generated_index_is_rejected",
    "AdrMetadataTests.test_body_hash_mismatch_is_rejected",
    "AdrMetadataTests.test_annotated_history_missing_latest_adr_fails",
    "AdrMetadataTests.test_annotated_history_duplicate_and_reordered_entries_fail",
    "AdrMetadataTests.test_annotated_history_title_mismatch_fails",
    "AdrMetadataTests.test_annotated_history_link_target_mismatch_fails",
    "AdrMetadataTests.test_annotated_history_status_mismatch_fails",
    "AdrMetadataTests.test_annotated_history_missing_annotation_fails",
    "AdrMetadataTests.test_annotated_history_marker_corruption_fails",
    "AdrMetadataTests.test_historical_adr_ranges_outside_markers_remain_legal",
    "RepositoryIntegrityBindingTests.test_canonical_validation_membership_and_order",
    "RepositoryIntegrityBindingTests.test_shared_profile_preserves_membership_order_and_continuation",
    "RepositoryIntegrityBindingTests.test_non_mutating_pass_maps_to_no_local_error",
    "RepositoryIntegrityBindingTests.test_multiple_non_mutating_failures_are_both_reported",
    "RepositoryIntegrityBindingTests.test_undetermined_exit_is_not_reported_as_failed",
    "RepositoryIntegrityBindingTests.test_pre_existing_dirty_state_remains_admissible",
    "RepositoryIntegrityBindingTests.test_already_dirty_tracked_mutation_is_rejected_by_local_binding",
    "RepositoryIntegrityBindingTests.test_already_present_untracked_mutation_is_rejected_by_local_binding",
    "RepositoryIntegrityBindingTests.test_mutation_stops_later_local_step",
    "RepositoryIntegrityBindingTests.test_failure_and_mutation_are_both_reported",
    "RepositoryIntegrityBindingTests.test_cli_returns_zero_when_all_canonical_children_pass",
    "RepositoryIntegrityBindingTests.test_cli_returns_nonzero_when_canonical_child_fails",
    "RepositoryIntegrityBindingTests.test_cli_preserves_undetermined_diagnostic_and_fails_closed",
    "RepositoryIntegrityBindingTests.test_cli_preserves_child_stdout_and_stderr",
    "RepositoryIntegrityBindingTests.test_whitespace_checker_is_non_mutating_under_shared_binding",
    "RepositoryIntegrityBindingTests.test_requirements_pin_exact_current_provider",
    "RepositoryIntegrityBindingTests.test_authoritative_ref_monotonicity_binding",
)


def test_identities(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        f"{node.name}.{child.name}"
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        for child in node.body
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        and child.name.startswith("test_")
    ]


class GovernanceTestModuleSizeTests(unittest.TestCase):
    def test_split_governance_test_modules_preserve_identity_and_size(self) -> None:
        for relative in RETIRED_TEST_MODULES:
            with self.subTest(retired=relative):
                self.assertFalse((ROOT / relative).exists())

        observed = [
            identity
            for relative in PRESERVED_TEST_MODULES
            for identity in test_identities(ROOT / relative)
        ]
        self.assertEqual(
            Counter(EXPECTED_LEGACY_TEST_IDENTITIES),
            Counter(observed),
        )
        self.assertEqual(40, len(observed))

        for relative in REPLACEMENT_SOURCE_MODULES:
            with self.subTest(source=relative):
                path = ROOT / relative
                self.assertTrue(path.is_file())
                line_count = path.read_bytes().count(b"\n")
                self.assertLessEqual(line_count, 400, f"{relative}: {line_count} lines")


if __name__ == "__main__":
    unittest.main()
