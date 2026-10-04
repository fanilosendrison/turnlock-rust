#!/usr/bin/env python3
"""Validate Turnlock-Rust's routed structured governance declarations."""

from __future__ import annotations

from pathlib import Path
import sys

from proto_ring import repository_governance_state

ROOT = Path(__file__).resolve().parents[1]


def load_structured_governance(root: Path = ROOT):
    """Load the canonical exact state without executing validators or generators."""

    state = repository_governance_state.load(root)
    return (
        state.repository_governance_model,
        state.governance_authority,
        state.governed_objects,
        state.governance_bindings,
        state.repository_integrity,
        state.projection_registry,
        state.evidence_requirements,
    )


def main() -> int:
    try:
        load_structured_governance()
    except repository_governance_state.RepositoryGovernanceStateError as error:
        print(f"ERROR: structured governance: {error}", file=sys.stderr)
        print("structured governance: FAILED", file=sys.stderr)
        return 1
    print("structured governance: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
