#!/usr/bin/env python3
"""Validate the routed Turnlock-Rust Governance Authority profile."""

from __future__ import annotations

from pathlib import Path
import sys

from proto_ring import repository_governance_state


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        repository_governance_state.load(ROOT)
    except repository_governance_state.RepositoryGovernanceStateError as error:
        print(f"ERROR: governance authority: {error}", file=sys.stderr)
        return 1

    print("governance authority: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
