#!/usr/bin/env python3
"""Validate native engine identity against Turnlock's authoritative binding."""

from pathlib import Path
import sys

from proto_ring_executable_binding import (
    PROTO_RING_TRANSPORT_VERSION,
    ProtoRingExecutableError,
    invoke_compat_result,
    load_executable_provider_binding,
)

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path = ROOT) -> list[str]:
    try:
        binding = load_executable_provider_binding(root)
        identity = invoke_compat_result(root, "engine.identity", {})
    except ProtoRingExecutableError as error:
        return [str(error)]
    expected = {
        "source_repository": binding.repository,
        "source_commit": binding.commit,
        "transport_version": PROTO_RING_TRANSPORT_VERSION,
    }
    return [] if identity == expected else ["engine.identity differs from binding authority"]


def main(arguments: list[str] | None = None) -> int:
    argv = sys.argv[1:] if arguments is None else arguments
    if argv:
        print("usage: check-proto-ring-provider.py", file=sys.stderr)
        return 1
    errors = check()
    if errors:
        for error in errors:
            print(f"ERROR: proto-ring provider: {error}", file=sys.stderr)
        print("proto-ring provider: FAILED", file=sys.stderr)
        return 1
    print("proto-ring provider: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
