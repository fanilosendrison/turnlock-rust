#!/usr/bin/env python3
"""Validate Turnlock-Rust's routed structured governance declarations."""

from pathlib import Path
import sys

from proto_ring_executable_binding import ProtoRingExecutableError, invoke_compat_result

ROOT = Path(__file__).resolve().parents[1]
_REQUIRED_COMPONENTS = (
    "repository_governance_model",
    "governance_authority",
    "governed_objects",
    "governance_bindings",
    "repository_integrity",
    "projection_registry",
    "evidence_requirements",
)


def load_structured_governance(root: Path = ROOT) -> dict[str, object]:
    """Compose canonical governance without executing validators or generators."""

    return invoke_compat_result(
        root, "repository-governance-state.compose", {"repository": str(root)}
    )


def check(root: Path = ROOT) -> list[str]:
    try:
        value = load_structured_governance(root)
    except ProtoRingExecutableError as error:
        return [str(error)]
    components = value.get("components")
    if not isinstance(components, dict):
        return ["canonical governance state has no component projection"]
    missing = [name for name in _REQUIRED_COMPONENTS if components.get(name) is not True]
    return [f"canonical governance state is missing: {', '.join(missing)}"] if missing else []


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(f"ERROR: structured governance: {error}", file=sys.stderr)
        print("structured governance: FAILED", file=sys.stderr)
        return 1
    print("structured governance: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
