#!/usr/bin/env python3
"""Compare raw executable authority with native governance composition."""

from pathlib import Path
import sys

from proto_ring_executable_binding import (
    PROTO_RING_BINDING_ID,
    ProtoRingExecutableError,
    invoke_compat_result,
    load_executable_provider_binding,
)

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path = ROOT) -> list[str]:
    try:
        binding = load_executable_provider_binding(root)
        state = invoke_compat_result(
            root,
            "repository-governance-state.compose",
            {"repository": str(root), "binding_ids": [PROTO_RING_BINDING_ID]},
        )
    except ProtoRingExecutableError as error:
        return [str(error)]
    projected = state.get("bindings", {}).get(PROTO_RING_BINDING_ID)
    expected = {
        "present": True,
        "kind": "executable_provider",
        "scope": {
            "kind": "logical_provider",
            "capability": None,
            "interface": None,
            "object": None,
        },
        "identity": {
            "kind": "executable_provider",
            "repository": binding.repository,
            "commit": binding.commit,
        },
        "authority": {
            "responsibility": "executable_provider_binding",
            "source": "governance_binding_registry",
        },
    }
    return [] if projected == expected else [
        "native composed binding differs from raw Governance Binding Registry"
    ]


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
