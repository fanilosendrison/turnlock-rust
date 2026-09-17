#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]


class RepositoryIntegrityError(RuntimeError):
    pass


def repository_status(root: Path) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RepositoryIntegrityError(
            f"cannot read git status in {root}" + (f": {detail}" if detail else "")
        )
    return result.stdout


def canonical_steps() -> list[tuple[str, list[str]]]:
    python = sys.executable
    return [
        ("ADR metadata tests", [python, "scripts/tests/test-adr-metadata.py"]),
        (
            "Formal traceability tests",
            [python, "scripts/tests/test-formal-traceability.py"],
        ),
        (
            "Normative terminology tests",
            [python, "scripts/tests/test-normative-terminology.py"],
        ),
        (
            "Repository integrity tests",
            [python, "scripts/tests/test-repository-integrity.py"],
        ),
        ("ADR metadata check", [python, "scripts/adr-metadata.py", "check"]),
        (
            "Normative terminology check",
            [python, "scripts/check-normative-terminology.py"],
        ),
        (
            "Formal traceability check",
            [python, "scripts/check-formal-traceability.py"],
        ),
        ("Git whitespace check", ["git", "diff", "--check"]),
    ]


def run_validation(
    root: Path,
    steps: Sequence[tuple[str, Sequence[str]]],
) -> tuple[list[str], list[tuple[str, int]]]:
    """Run validation steps under a worktree-purity guard.

    Returns (errors, failed_steps). Step stdout/stderr are preserved by
    inheriting this process's streams.
    """
    root = Path(root)
    errors: list[str] = []
    failed_steps: list[tuple[str, int]] = []

    try:
        baseline = repository_status(root)
    except RepositoryIntegrityError as error:
        return [str(error)], []

    for name, argv in steps:
        print(f"==> {name}", flush=True)
        result = subprocess.run(list(argv), cwd=root, check=False)
        if result.returncode != 0:
            failed_steps.append((name, result.returncode))
            errors.append(f"validation step failed: {name} (exit {result.returncode})")

    try:
        final = repository_status(root)
    except RepositoryIntegrityError as error:
        errors.append(str(error))
        return errors, failed_steps

    if baseline != final:
        errors.append("repository integrity validation modified the worktree")
        print(
            "repository integrity validation modified the worktree",
            file=sys.stderr,
        )
        print("--- worktree status before validation ---", file=sys.stderr)
        sys.stderr.write(baseline.decode("utf-8", errors="replace"))
        print("--- worktree status after validation ---", file=sys.stderr)
        sys.stderr.write(final.decode("utf-8", errors="replace"))

    return errors, failed_steps


def main() -> int:
    errors, _failed_steps = run_validation(ROOT, canonical_steps())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("repository integrity: FAILED", file=sys.stderr)
        return 1
    print("repository integrity: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
