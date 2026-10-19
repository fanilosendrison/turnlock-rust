#!/usr/bin/env python3
"""Validate immutable accepted ADR bodies through native proto-ring."""

from pathlib import Path
import sys

from proto_ring_executable_binding import ProtoRingExecutableError, invoke_compat_result

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path = ROOT) -> tuple[bool, str | None]:
    try:
        value = invoke_compat_result(
            root, "accepted-adr-body.immutability", {"repository": str(root)}
        )
    except ProtoRingExecutableError as error:
        return False, str(error)
    status, category = value.get("status"), value.get("category")
    if status == "PASS" and category is None:
        return True, None
    if status == "NON_PASS" and category in {
        "body_changed",
        "historical_state_invalid",
    }:
        return False, category
    return False, "provider returned an invalid accepted ADR body status"


def main() -> int:
    passed, diagnostic = check()
    if not passed:
        print(f"ERROR: accepted ADR body: {diagnostic}", file=sys.stderr)
        print("accepted ADR body: FAILED", file=sys.stderr)
        return 1
    print("accepted ADR body: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
