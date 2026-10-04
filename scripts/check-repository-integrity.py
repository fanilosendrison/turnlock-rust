#!/usr/bin/env python3
"""Evaluate the routed Turnlock-Rust Repository Integrity profile."""

from __future__ import annotations

import os
from pathlib import Path
import sys

from proto_ring import repository_governance_state, repository_integrity
from proto_ring.repository_integrity import (
    EvaluationContext,
    IntegrityVerdict,
    ObligationStatus,
    ValidationEnvironmentRealization,
    evaluate_consumer_profile,
)

ROOT = Path(__file__).resolve().parents[1]


def load_profile(root: Path = ROOT):
    state = repository_governance_state.load(root)
    profile = state.repository_integrity
    if profile is None:
        raise repository_integrity.RepositoryIntegrityError(
            "Turnlock-Rust declares repository_integrity but the canonical state "
            "does not contain its profile"
        )
    return profile


def evaluation_context() -> EvaluationContext:
    environment = ValidationEnvironmentRealization(
        environment_id="turnlock_python",
        identity="turnlock-python-validation-environment-v1",
        command_prefix=(sys.executable,),
        process_environment=dict(os.environ),
    )
    return EvaluationContext({environment.environment_id: environment})


def run_validation(root: Path = ROOT):
    profile = load_profile(root)
    return evaluate_consumer_profile(root, profile, evaluation_context())


def _diagnostics(result) -> list[str]:
    diagnostics = list(result.errors)
    for validation in result.validations:
        if validation.status is ObligationStatus.SATISFIED:
            continue
        detail = next(
            (item.detail for item in validation.obligations if item.detail), None
        )
        suffix = f": {detail}" if detail else ""
        diagnostics.append(
            f"validation {validation.validation_id}: {validation.status.value}{suffix}"
        )
    return diagnostics


def main() -> int:
    try:
        result = run_validation()
    except (
        repository_governance_state.RepositoryGovernanceStateError,
        repository_integrity.RepositoryIntegrityError,
    ) as error:
        print(f"ERROR: repository integrity: {error}", file=sys.stderr)
        print("repository integrity: FAILED", file=sys.stderr)
        return 1
    if result.verdict is not IntegrityVerdict.PASS:
        for diagnostic in _diagnostics(result):
            print(f"ERROR: {diagnostic}", file=sys.stderr)
        print("repository integrity: FAILED", file=sys.stderr)
        return 1
    print("repository integrity: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
