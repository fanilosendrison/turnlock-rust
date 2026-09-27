#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from proto_ring import shared_governance_provider

ROOT = Path(__file__).resolve().parents[1]

PROFILE = shared_governance_provider.SharedGovernanceProviderProfile(
    agent_directives_path="AGENTS.md",
    binding_path=(
        "docs/repository-governance/"
        "turnlock-rust-shared-governance-provider.md"
    ),
    contract_commit=(
        "974ca31ff12630a90da6371cc27c1f5ef0cc590e"
    ),
    required_agent_directive=(
        "Before adding, modifying, replacing, or designing any repository-governance\n"
        "  mechanism, read and apply\n"
        "  `docs/repository-governance/"
        "turnlock-rust-shared-governance-provider.md`."
    ),
    required_binding_directive=(
        "For generic/reusable repository-governance responsibilities, Turnlock-Rust uses\n"
        "proto-ring as the mandatory provider."
    ),
)


def check(repository: Path = ROOT) -> list[str]:
    return shared_governance_provider.check(repository, PROFILE)


def main() -> int:
    errors = check(ROOT)

    if errors:
        print("shared governance provider binding: FAILED")
        for error in errors:
            print(error)
        return 1

    print("shared governance provider binding: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
