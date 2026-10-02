#!/usr/bin/env python3
"""Validate the effective proto-ring provider against Turnlock authority."""

from __future__ import annotations

from importlib import metadata
import json
from pathlib import Path
import re
import sys

from proto_ring_executable_binding import (
    PROTO_RING_REPOSITORY,
    authoritative_proto_ring_commit,
)

ROOT = Path(__file__).resolve().parents[1]


def installed_proto_ring_commit() -> str:
    """Return the exact installed provider commit from PEP 610 provenance."""

    distribution = metadata.distribution("proto-ring")
    direct_url_text = distribution.read_text("direct_url.json")
    if direct_url_text is None:
        raise ValueError("installed proto-ring has no PEP 610 provenance")
    value = json.loads(direct_url_text)
    vcs_info = value.get("vcs_info") if isinstance(value, dict) else None
    vcs = vcs_info.get("vcs") if isinstance(vcs_info, dict) else None
    commit = vcs_info.get("commit_id") if isinstance(vcs_info, dict) else None
    url = value.get("url") if isinstance(value, dict) else None
    expected_url = f"https://github.com/{PROTO_RING_REPOSITORY}.git"
    if vcs != "git":
        raise ValueError("installed proto-ring PEP 610 provenance is not Git VCS")
    if url != expected_url:
        raise ValueError(
            "installed proto-ring PEP 610 repository does not identify "
            f"{PROTO_RING_REPOSITORY}"
        )
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("installed proto-ring has no exact Git commit provenance")
    return commit


def check(root: Path = ROOT) -> list[str]:
    """Check installed provenance against requirements.txt authority."""

    try:
        expected = authoritative_proto_ring_commit(root)
        actual = installed_proto_ring_commit()
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        metadata.PackageNotFoundError,
    ) as error:
        return [str(error)]
    if actual != expected:
        return [
            f"installed proto-ring {actual} differs from authoritative "
            f"requirements.txt commit {expected}"
        ]
    return []


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
