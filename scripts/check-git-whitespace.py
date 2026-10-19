#!/usr/bin/env python3
"""Validate Git whitespace through native proto-ring."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

from proto_ring_executable_binding import ProtoRingExecutableError, invoke_compat_result

ROOT = Path(__file__).resolve().parents[1]


def _local_diagnostics(root: Path, domains: list[str]) -> list[str]:
    commands = {
        "unstaged": ["git", "-C", str(root), "diff", "--check"],
        "staged": ["git", "-C", str(root), "diff", "--cached", "--check"],
    }
    diagnostics: list[str] = []
    for domain in domains:
        command = commands.get(domain)
        if command is None:
            diagnostics.append(f"whitespace domain: {domain}")
            continue
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        lines = [line for line in result.stdout.splitlines() if line]
        diagnostics.extend(lines or [f"whitespace domain: {domain}"])
    return diagnostics


def check(root: Path = ROOT, environment: dict[str, str] | None = None) -> list[str]:
    exact_environment = dict(os.environ) if environment is None else dict(environment)
    try:
        value = invoke_compat_result(
            ROOT,
            "git-whitespace.validate",
            {"repository": str(root), "environment": exact_environment},
        )
    except ProtoRingExecutableError as error:
        return [str(error)]
    status, domains = value.get("status"), value.get("domains")
    if status == "PASS" and domains == []:
        return []
    if status == "NON_PASS" and isinstance(domains, list) and all(
        isinstance(domain, str) for domain in domains
    ):
        return _local_diagnostics(root, domains or ["unspecified"])
    return ["provider returned an invalid Git whitespace status"]


def main() -> int:
    errors = check()
    if errors:
        print("git whitespace check: FAILED")
        for error in errors:
            print(error)
        return 1
    print("git whitespace check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
