#!/usr/bin/env python3
"""Validate the routed Turnlock-Rust Governance Authority profile."""

from pathlib import Path
import sys

from proto_ring_executable_binding import ProtoRingExecutableError, invoke_compat_result

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path = ROOT) -> list[str]:
    try:
        value = invoke_compat_result(
            root, "repository-governance-state.compose", {"repository": str(root)}
        )
    except ProtoRingExecutableError as error:
        return [str(error)]
    return [] if value["components"].get("governance_authority") is True else [
        "canonical governance state has no Governance Authority profile"
    ]


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(f"ERROR: governance authority: {error}", file=sys.stderr)
        return 1
    print("governance authority: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
