#!/usr/bin/env python3
"""Validate the routed Turnlock-Rust Governed Objects profile."""

from __future__ import annotations

from pathlib import Path
import sys

from proto_ring import governance_authority, governed_objects
from proto_ring import repository_governance_model


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        model = repository_governance_model.load(ROOT)

        authority_capability = model.capabilities.get("governance_authority")
        if authority_capability is None:
            raise governance_authority.GovernanceAuthorityError(
                "governance_authority capability is required"
            )
        authority_route = authority_capability.routes.get("profile")
        if authority_route is None:
            raise governance_authority.GovernanceAuthorityError(
                "governance_authority profile route is required"
            )
        authority_profile = governance_authority.load(ROOT, authority_route)

        objects_capability = model.capabilities.get("governed_objects")
        if objects_capability is None:
            raise governed_objects.GovernedObjectsError(
                "governed_objects capability is required"
            )
        objects_route = objects_capability.routes.get("profile")
        if objects_route is None:
            raise governed_objects.GovernedObjectsError(
                "governed_objects profile route is required"
            )
        governed_objects.load(ROOT, objects_route, authority_profile)
    except (
        governance_authority.GovernanceAuthorityError,
        governed_objects.GovernedObjectsError,
        repository_governance_model.RepositoryGovernanceModelError,
    ) as error:
        print(f"ERROR: governed objects: {error}", file=sys.stderr)
        return 1

    print("governed objects: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
