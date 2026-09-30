#!/usr/bin/env python3
"""Validate the routed Turnlock-Rust Governance Authority profile."""

from __future__ import annotations

from pathlib import Path
import sys

from proto_ring import governance_authority, repository_governance_model


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        model = repository_governance_model.load(ROOT)
        capability = model.capabilities.get("governance_authority")
        if capability is None:
            raise governance_authority.GovernanceAuthorityError(
                "governance_authority capability is required"
            )
        profile_route = capability.routes.get("profile")
        if profile_route is None:
            raise governance_authority.GovernanceAuthorityError(
                "governance_authority profile route is required"
            )
        governance_authority.load(ROOT, profile_route)
    except (
        governance_authority.GovernanceAuthorityError,
        repository_governance_model.RepositoryGovernanceModelError,
    ) as error:
        print(f"ERROR: governance authority: {error}", file=sys.stderr)
        return 1

    print("governance authority: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
