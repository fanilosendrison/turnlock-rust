#!/usr/bin/env python3
"""Validate Turnlock-Rust's routed structured governance declarations."""

from __future__ import annotations

from pathlib import Path
import sys

from proto_ring import (
    evidence_requirements,
    governance_authority,
    governance_bindings,
    governed_objects,
    projection_registry,
    repository_governance_model,
    repository_integrity,
)

ROOT = Path(__file__).resolve().parents[1]


def _route(model, capability_id: str, route_id: str):
    capability = model.capabilities.get(capability_id)
    if capability is None:
        raise repository_governance_model.RepositoryGovernanceModelError(
            f"{capability_id} capability is required"
        )
    route = capability.routes.get(route_id)
    if route is None:
        raise repository_governance_model.RepositoryGovernanceModelError(
            f"{capability_id}/{route_id} route is required"
        )
    return route


def load_structured_governance(root: Path = ROOT):
    """Load all proto-ring#52 declarations without running validators or generators."""

    model = repository_governance_model.load(root)
    authority = governance_authority.load(
        root, _route(model, "governance_authority", "profile")
    )
    objects = governed_objects.load(
        root, _route(model, "governed_objects", "profile"), authority
    )
    bindings = governance_bindings.load(
        root,
        _route(model, "shared_governance_provider", "registry"),
        authority,
        objects,
    )
    repository_governance_model.validate_binding_capabilities(model, bindings)
    integrity = repository_integrity.load(
        root,
        _route(model, "repository_integrity", "profile"),
        authority,
        objects,
    )
    projections = projection_registry.load(
        root,
        _route(model, "projection_integrity", "registry"),
        authority,
        integrity,
        objects,
        bindings,
    )
    evidence = evidence_requirements.load(
        root,
        _route(model, "evidence_requirements", "registry"),
        authority,
        objects,
    )
    return model, authority, objects, bindings, integrity, projections, evidence


def main() -> int:
    try:
        load_structured_governance()
    except (
        evidence_requirements.EvidenceRequirementsError,
        governance_authority.GovernanceAuthorityError,
        governance_bindings.GovernanceBindingsError,
        governed_objects.GovernedObjectsError,
        projection_registry.ProjectionRegistryError,
        repository_governance_model.RepositoryGovernanceModelError,
        repository_integrity.RepositoryIntegrityError,
    ) as error:
        print(f"ERROR: structured governance: {error}", file=sys.stderr)
        print("structured governance: FAILED", file=sys.stderr)
        return 1
    print("structured governance: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
