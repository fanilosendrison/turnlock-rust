#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import unittest

from proto_ring import governance_authority, governed_objects
from proto_ring import repository_governance_model

ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = (
    ROOT
    / "docs"
    / "repository-governance"
    / "turnlock-rust-governed-objects.md"
)
def load_profiles():
    model = repository_governance_model.load(ROOT)
    authority_route = model.capabilities["governance_authority"].routes["profile"]
    authority = governance_authority.load(ROOT, authority_route)
    catalog_route = model.capabilities["governed_objects"].routes["profile"]
    catalog = governed_objects.load(ROOT, catalog_route, authority)
    return model, authority, catalog


class GovernedObjectsProfileTests(unittest.TestCase):
    def test_profile_is_routed_without_duplicate_contract_pin(self) -> None:
        model, _authority, catalog = load_profiles()
        route = model.capabilities["governed_objects"].routes["profile"]

        self.assertEqual(
            "docs/repository-governance/turnlock-rust-governed-objects.md",
            route.declared_path,
        )
        self.assertEqual(PROFILE_PATH.resolve(), route.target)
        self.assertEqual(PROFILE_PATH.resolve(), catalog.carrier)

        self.assertNotIn(
            "governed_objects_contract:",
            PROFILE_PATH.read_text(encoding="utf-8"),
        )

    def test_governance_authority_owns_only_profile_route(self) -> None:
        _model, authority, _catalog = load_profiles()
        responsibility = authority.responsibilities[
            "governed_objects_profile_route"
        ]

        self.assertEqual(
            {"agents_governance_frontmatter": governance_authority.SourceRole.AUTHORITY},
            responsibility.roles,
        )
        self.assertEqual((), responsibility.precedence)

    def test_catalog_has_exact_initial_interfaces_and_objects(self) -> None:
        _model, _authority, catalog = load_profiles()

        self.assertEqual(
            {"architecture_decisions", "stable_invariants", "formal_claims"},
            set(catalog.interfaces),
        )
        self.assertEqual(
            {f"ADR-{number:03d}" for number in range(1, 53)},
            set(catalog.interfaces["architecture_decisions"].objects),
        )
        self.assertEqual(
            {f"TL-INV-{number:03d}" for number in range(1, 43)},
            set(catalog.interfaces["stable_invariants"].objects),
        )
        self.assertEqual(
            {f"TL-CLAIM-{number:03d}" for number in range(1, 84)},
            set(catalog.interfaces["formal_claims"].objects),
        )

    def test_catalog_has_exact_initial_responsibilities(self) -> None:
        _model, _authority, catalog = load_profiles()

        for governed_object in catalog.interfaces[
            "architecture_decisions"
        ].objects.values():
            self.assertEqual(
                frozenset(
                    {"adr_metadata", "product_semantics", "accepted_decisions"}
                ),
                governed_object.responsibilities,
            )
            self.assertEqual(frozenset(), governed_object.relations)

        for governed_object in catalog.interfaces[
            "stable_invariants"
        ].objects.values():
            self.assertEqual(
                frozenset(
                    {"product_semantics", "stable_invariant_definitions"}
                ),
                governed_object.responsibilities,
            )
            self.assertEqual(frozenset(), governed_object.relations)

        for governed_object in catalog.interfaces[
            "formal_claims"
        ].objects.values():
            self.assertEqual(
                frozenset({"formal_assurance_graph"}),
                governed_object.responsibilities,
            )

    def test_claim_relations_use_only_normative_sources(self) -> None:
        _model, _authority, catalog = load_profiles()
        relations = [
            relation
            for governed_object in catalog.interfaces[
                "formal_claims"
            ].objects.values()
            for relation in governed_object.relations
        ]

        self.assertEqual(125, len(relations))
        for relation in relations:
            self.assertEqual("normative_sources", relation.relation)
            self.assertEqual("formal_assurance_graph", relation.responsibility)
            self.assertEqual("stable_invariants", relation.target.interface_id)
            self.assertRegex(relation.target.object_id, r"^TL-INV-\d{3}$")


if __name__ == "__main__":
    unittest.main()
