#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest import mock

from proto_ring import (
    github_authoritative_ref_monotonicity,
    repository_governance_state,
    repository_integrity,
)
from proto_ring.governance_authority import SourceRole, role_of

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "check-structured-governance.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_structured_governance", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load structured governance checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


class StructuredGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.model,
            cls.authority,
            cls.objects,
            cls.bindings,
            cls.integrity,
            cls.projections,
            cls.evidence,
        ) = checker.load_structured_governance(ROOT)

    def test_rgm_v2_declares_exact_applicable_capabilities(self) -> None:
        self.assertEqual(2, self.model.model_version)
        self.assertEqual(
            {
                "architecture_decisions",
                "governance_authority",
                "governed_objects",
                "shared_governance_provider",
                "projection_integrity",
                "repository_integrity",
                "evidence_requirements",
                "authoritative_ref_monotonicity",
            },
            set(self.model.capabilities),
        )
        self.assertEqual("registry", self.model.provider.binding.route)

    def test_binding_registry_contains_exact_active_bindings(self) -> None:
        self.assertEqual(
            {
                "proto_ring_executable",
                "shared_governance_provider_contract",
                "projection_integrity_contract",
                "exact_evidence_binding_contract",
                "governance_authority_contract",
                "governed_objects_contract",
                "authoritative_ref_monotonicity_contract",
                "repository_governance_model_contract",
                "repository_governance_state_contract",
                "repository_integrity_contract",
                "evidence_requirements_contract",
            },
            set(self.bindings.bindings),
        )
        executable = self.bindings.bindings["proto_ring_executable"]
        self.assertEqual(
            "dedb01a3a9b7a18930c9da75afa3773b5ad67f69",
            executable.identity.commit,
        )
        self.assertEqual("executable_dependency_manifest", executable.authority.source_id)

        state_contract = self.bindings.bindings[
            "repository_governance_state_contract"
        ]
        self.assertEqual("governance_contract", state_contract.kind.value)
        self.assertEqual("logical_provider", state_contract.scope.kind.value)
        self.assertEqual(
            "fanilosendrison/proto-ring", state_contract.identity.repository
        )
        self.assertEqual(
            "9a1ed2d71d079b0118177c2a509ca356c371a597",
            state_contract.identity.commit,
        )
        self.assertEqual(
            "docs/contracts/repository-governance-state.md",
            state_contract.identity.path,
        )
        self.assertEqual(
            "890ed560e61e205067bdf3628e419302613ef06e",
            self.bindings.bindings[
                "repository_governance_model_contract"
            ].identity.commit,
        )

    def test_tuple_helper_is_one_thin_canonical_state_projection(self) -> None:
        field_names = (
            "repository_governance_model",
            "governance_authority",
            "governed_objects",
            "governance_bindings",
            "repository_integrity",
            "projection_registry",
            "evidence_requirements",
        )
        expected = tuple(object() for _field_name in field_names)
        state = SimpleNamespace(**dict(zip(field_names, expected)))
        with mock.patch.object(
            checker.repository_governance_state, "load", return_value=state
        ) as load:
            actual = checker.load_structured_governance(ROOT)
        load.assert_called_once_with(ROOT)
        for projected, canonical in zip(actual, expected):
            self.assertIs(projected, canonical)

    def test_canonical_state_is_exact_and_complete_for_turnlock(self) -> None:
        state = repository_governance_state.load(ROOT)
        self.assertEqual(ROOT.resolve(), state.repository)
        self.assertEqual(ROOT.resolve(), state.observed_state.repository)
        self.assertEqual(2, state.repository_governance_model.model_version)
        self.assertIsNotNone(state.governed_objects)
        self.assertIsNotNone(state.repository_integrity)
        self.assertIsNotNone(state.projection_registry)
        self.assertIsNotNone(state.evidence_requirements)
        capabilities = set(state.repository_governance_model.capabilities)
        self.assertEqual(
            {
                "architecture_decisions",
                "governance_authority",
                "governed_objects",
                "shared_governance_provider",
                "projection_integrity",
                "repository_integrity",
                "evidence_requirements",
                "authoritative_ref_monotonicity",
            },
            capabilities,
        )
        self.assertNotIn("repository_governance_state", capabilities)

    def test_canonical_state_observes_routed_governance_carriers(self) -> None:
        state = repository_governance_state.load(ROOT)
        observed = state.observed_state
        self.assertRegex(observed.identity, re.compile(r"^[0-9a-f]{64}$"))
        self.assertEqual(tuple(sorted(set(observed.scope_paths))), observed.scope_paths)
        self.assertIn("AGENTS.md", observed.scope_paths)
        for path in (
            "turnlock-rust-governance-authority.md",
            "turnlock-rust-governance-bindings.md",
            "turnlock-rust-governed-objects.md",
            "turnlock-rust-repository-integrity.md",
            "turnlock-rust-projection-integrity.md",
            "turnlock-rust-evidence-requirements.md",
        ):
            self.assertIn(
                f"docs/repository-governance/{path}", observed.scope_paths
            )

    def test_canonical_state_load_preserves_exact_git_status(self) -> None:
        command = ["git", "-C", str(ROOT), "status", "--porcelain=v1", "-z"]
        before = subprocess.run(command, check=True, capture_output=True).stdout
        repository_governance_state.load(ROOT)
        after = subprocess.run(command, check=True, capture_output=True).stdout
        self.assertEqual(before, after)

    def test_canonical_state_construction_does_not_evaluate_operations(self) -> None:
        with (
            mock.patch.object(
                repository_integrity,
                "evaluate_consumer_profile",
                side_effect=AssertionError("Repository Integrity evaluation executed"),
            ) as evaluate,
            mock.patch.object(
                github_authoritative_ref_monotonicity,
                "run",
                side_effect=AssertionError("ARM provider evaluation executed"),
            ) as arm_run,
        ):
            state = repository_governance_state.load(ROOT)
        self.assertIsNotNone(state.repository_integrity)
        evaluate.assert_not_called()
        arm_run.assert_not_called()

    def test_canonical_state_subprocesses_are_local_git_observation_only(self) -> None:
        original_run = subprocess.run

        def git_only(arguments, *args, **kwargs):
            if not isinstance(arguments, (list, tuple)) or not arguments:
                raise AssertionError("state construction invoked an opaque subprocess")
            if arguments[0] != "git":
                raise AssertionError(
                    f"state construction invoked non-Git subprocess: {arguments[0]}"
                )
            return original_run(arguments, *args, **kwargs)

        with mock.patch("subprocess.run", side_effect=git_only) as run:
            repository_governance_state.load(ROOT)
        self.assertGreater(run.call_count, 0)

    def test_authority_preserves_executable_and_gate_a_ownership(self) -> None:
        self.assertIs(
            SourceRole.AUTHORITY,
            role_of(
                self.authority,
                "executable_provider_binding",
                "executable_dependency_manifest",
            ),
        )
        self.assertIs(
            SourceRole.SECONDARY_REPRESENTATION,
            role_of(
                self.authority,
                "executable_provider_binding",
                "governance_binding_registry",
            ),
        )
        for source_id in (
            "gate_a_current_subject",
            "gate_a_current_protocol_context",
            "gate_a_review_candidates",
        ):
            self.assertIsNone(self.authority.sources[source_id].repository_target)

    def test_persistent_integrity_owns_complete_order(self) -> None:
        self.assertEqual("repository_integrity_profile", self.integrity.authority.source)
        self.assertEqual(29, len(self.integrity.order))
        self.assertEqual(set(self.integrity.validations), set(self.integrity.order))
        self.assertEqual(
            frozenset({2}),
            self.integrity.validations[
                "authoritative_ref_monotonicity_effective_rules"
            ].command.undetermined_exit_codes,
        )
        self.assertIn("formal_traceability_check", self.integrity.order)
        self.assertIn("structured_governance_check", self.integrity.order)

    def test_projection_registry_has_required_direct_relations(self) -> None:
        self.assertEqual(
            {
                "adr_index",
                "adr_annotated_history",
                "formal_invariant_mapping",
                "governed_adr_catalog",
                "governed_invariant_catalog",
                "governed_formal_claim_catalog",
                "executable_binding_registry_representation",
                "effective_proto_ring_realization",
            },
            set(self.projections.projections),
        )
        registry = self.projections.projections[
            "executable_binding_registry_representation"
        ]
        realization = self.projections.projections["effective_proto_ring_realization"]
        self.assertEqual("executable_dependency_manifest", registry.canonical_source_id)
        self.assertEqual("governance_binding_registry", registry.secondary_source_id)
        self.assertEqual(
            "proto_ring_binding_registry_currentness", registry.validation_id
        )
        self.assertEqual("executable_dependency_manifest", realization.canonical_source_id)
        self.assertEqual("effective_proto_ring_provider", realization.secondary_source_id)
        self.assertEqual("proto_ring_provider_currentness", realization.validation_id)
        self.assertNotEqual(registry.validation_id, realization.validation_id)
        self.assertEqual("proto_ring_executable", registry.binding_id)
        self.assertEqual("proto_ring_executable", realization.binding_id)

    def test_evidence_registry_is_responsibility_scoped(self) -> None:
        self.assertEqual(
            {"gate_a_subject_binding", "gate_a_current_protocol_binding"},
            set(self.evidence.requirements),
        )
        for requirement in self.evidence.requirements.values():
            self.assertEqual("formal_assurance_graph", requirement.responsibility_id)
            self.assertIsNone(requirement.target)

    def test_obsolete_carriers_and_duplicate_pins_are_absent(self) -> None:
        governance = ROOT / "docs" / "repository-governance"
        self.assertFalse((governance / "turnlock-rust-shared-governance-provider.md").exists())
        self.assertFalse((governance / "turnlock-rust-exact-evidence-binding.md").exists())
        for path in (
            governance / "turnlock-rust-governance-authority.md",
            governance / "turnlock-rust-governed-objects.md",
            governance / "turnlock-rust-authoritative-ref-monotonicity.md",
        ):
            self.assertNotIn("_contract:", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
