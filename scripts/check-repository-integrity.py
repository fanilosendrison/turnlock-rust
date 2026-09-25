#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Sequence

from proto_ring.repository_integrity import (
    CommandObligation,
    IntegrityProfile,
    ObligationStatus,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]


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
        (
            "Git whitespace tests",
            [python, "scripts/tests/test-git-whitespace.py"],
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
        (
            "Git whitespace check",
            [python, "scripts/check-git-whitespace.py"],
        ),
    ]


def _integrity_profile(
    steps: Sequence[tuple[str, Sequence[str]]],
) -> IntegrityProfile:
    return IntegrityProfile(
        obligations=tuple(
            CommandObligation(
                name=name,
                argv=tuple(argv),
            )
            for name, argv in steps
        ),
        continue_after_non_satisfied=True,
    )


def run_validation(
    root: Path,
    steps: Sequence[tuple[str, Sequence[str]]],
) -> tuple[list[str], list[tuple[str, int]]]:
    """Bind Turnlock validation membership to shared Repository Integrity."""

    result = evaluate(
        Path(root),
        _integrity_profile(steps),
        env=os.environ,
    )

    errors: list[str] = []
    failed_steps: list[tuple[str, int]] = []

    if result.baseline_state_identity is None:
        errors.extend(
            f"repository integrity substrate: {error}"
            for error in result.errors
        )
        if not errors:
            errors.append(
                "repository integrity substrate: "
                "baseline repository state is undetermined"
            )
        return errors, failed_steps

    for obligation in result.obligations:
        if obligation.returncode is not None and obligation.returncode != 0:
            failed_steps.append(
                (
                    obligation.name,
                    obligation.returncode,
                )
            )
            errors.append(
                "validation step failed: "
                f"{obligation.name} "
                f"(exit {obligation.returncode})"
            )
            continue

        if obligation.status is ObligationStatus.UNDETERMINED:
            detail = (
                f": {obligation.detail}"
                if obligation.detail
                else ""
            )
            errors.append(
                "validation step undetermined: "
                f"{obligation.name}{detail}"
            )

    if any(
        "repository state changed" in error
        for error in result.errors
    ):
        errors.append(
            "repository integrity validation modified the worktree"
        )

    errors.extend(
        f"repository integrity substrate: {error}"
        for error in result.errors
    )

    return errors, failed_steps


def main() -> int:
    errors, _failed_steps = run_validation(
        ROOT,
        canonical_steps(),
    )

    if errors:
        for error in errors:
            print(
                f"ERROR: {error}",
                file=sys.stderr,
            )

        print(
            "repository integrity: FAILED",
            file=sys.stderr,
        )
        return 1

    print("repository integrity: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
