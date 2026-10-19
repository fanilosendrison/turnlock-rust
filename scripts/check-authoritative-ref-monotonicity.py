#!/usr/bin/env python3
"""Observe Turnlock-Rust's exact GitHub ARM binding through native proto-ring."""

from pathlib import Path
import sys

from proto_ring_executable_binding import ProtoRingExecutableError, invoke_compat_result

ROOT = Path(__file__).resolve().parents[1]
BINDING = ROOT / "docs/repository-governance/turnlock-rust-authoritative-ref-monotonicity.md"
_EXIT_CODES = {"SATISFIED": 0, "VIOLATED": 1, "UNDETERMINED": 2}


def observe(root: Path = ROOT, binding: Path = BINDING) -> str:
    value = invoke_compat_result(
        root,
        "github-authoritative-ref-monotonicity.observe",
        {"binding_path": str(binding)},
    )
    status = value.get("status")
    if status not in _EXIT_CODES:
        raise ProtoRingExecutableError("provider returned an invalid ARM status")
    return status


def main() -> int:
    try:
        status = observe()
    except ProtoRingExecutableError as error:
        print(f"ERROR: authoritative-ref monotonicity: {error}", file=sys.stderr)
        return 2
    print(f"authoritative-ref monotonicity: {status}")
    return _EXIT_CODES[status]


if __name__ == "__main__":
    raise SystemExit(main())
