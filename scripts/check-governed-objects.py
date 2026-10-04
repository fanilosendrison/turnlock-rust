#!/usr/bin/env python3
"""Validate the routed Turnlock-Rust Governed Objects profile."""

from __future__ import annotations

from pathlib import Path
import sys

from proto_ring import repository_governance_state


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        state = repository_governance_state.load(ROOT)
        if state.governed_objects is None:
            raise ValueError(
                "Turnlock-Rust declares governed_objects but the canonical state "
                "does not contain its profile"
            )
    except (
        ValueError,
        repository_governance_state.RepositoryGovernanceStateError,
    ) as error:
        print(f"ERROR: governed objects: {error}", file=sys.stderr)
        return 1

    print("governed objects: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
