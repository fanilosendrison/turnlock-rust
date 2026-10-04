#!/usr/bin/env python3
"""Validate the proto-ring binding registry copy against Turnlock authority."""

from __future__ import annotations

from pathlib import Path
import sys

from proto_ring import governance_bindings, repository_governance_state
from proto_ring_executable_binding import (
    PROTO_RING_REPOSITORY,
    authoritative_proto_ring_commit,
)

ROOT = Path(__file__).resolve().parents[1]
_BINDING_ID = "proto_ring_executable"


def binding_registry_proto_ring_commit(root: Path) -> str:
    """Return the canonical state's stable executable binding commit."""

    state = repository_governance_state.load(root)
    registry = state.governance_bindings
    binding = registry.bindings.get(_BINDING_ID)
    if binding is None:
        raise ValueError(f"Governance Binding Registry requires {_BINDING_ID}")
    if binding.kind is not governance_bindings.BindingKind.EXECUTABLE_PROVIDER:
        raise ValueError(f"{_BINDING_ID} must be executable_provider")
    if binding.scope.kind is not governance_bindings.ScopeKind.LOGICAL_PROVIDER:
        raise ValueError(f"{_BINDING_ID} scope must be logical_provider")
    if not isinstance(
        binding.identity, governance_bindings.ExecutableProviderIdentity
    ):
        raise ValueError(
            f"{_BINDING_ID} identity must be ExecutableProviderIdentity"
        )
    if binding.identity.repository != PROTO_RING_REPOSITORY:
        raise ValueError(
            f"{_BINDING_ID} repository must be {PROTO_RING_REPOSITORY}"
        )
    return binding.identity.commit


def check(root: Path = ROOT) -> list[str]:
    """Check the routed registry copy against requirements.txt authority."""

    try:
        expected = authoritative_proto_ring_commit(root)
        actual = binding_registry_proto_ring_commit(root)
    except (
        OSError,
        ValueError,
        repository_governance_state.RepositoryGovernanceStateError,
    ) as error:
        return [str(error)]
    if actual != expected:
        return [
            "Governance Binding Registry proto_ring_executable commit "
            f"{actual} differs from authoritative requirements.txt commit {expected}"
        ]
    return []


def main(arguments: list[str] | None = None) -> int:
    argv = sys.argv[1:] if arguments is None else arguments
    if argv:
        print("usage: check-proto-ring-binding-registry.py", file=sys.stderr)
        return 1
    errors = check()
    if errors:
        for error in errors:
            print(f"ERROR: proto-ring binding registry: {error}", file=sys.stderr)
        print("proto-ring binding registry: FAILED", file=sys.stderr)
        return 1
    print("proto-ring binding registry: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
