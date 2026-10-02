#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

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
                "repository_integrity_contract",
                "evidence_requirements_contract",
            },
            set(self.bindings.bindings),
        )
        executable = self.bindings.bindings["proto_ring_executable"]
        # proto-ring#52 migration acceptance assertion; executable currentness is
        # proved separately by proto_ring_binding_registry_currentness.
        self.assertEqual(
            "890ed560e61e205067bdf3628e419302613ef06e",
            executable.identity.commit,
        )
        self.assertEqual("executable_dependency_manifest", executable.authority.source_id)

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
