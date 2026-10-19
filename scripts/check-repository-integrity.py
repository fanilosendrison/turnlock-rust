#!/usr/bin/env python3
"""Evaluate Turnlock-Rust Repository Integrity through native proto-ring."""

from __future__ import annotations

import os
from pathlib import Path
import sys

from proto_ring_executable_binding import ProtoRingExecutableError, invoke_compat_result
import yaml

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT_ID = "turnlock_python"
ENVIRONMENT_IDENTITY = "turnlock-python-validation-environment-v1"
PROFILE = Path("docs/repository-governance/turnlock-rust-repository-integrity.md")


def _expected_validation_ids(root: Path) -> list[str] | None:
    try:
        text = (root / PROFILE).read_text(encoding="utf-8")
        metadata = yaml.safe_load(text.split("---\n", 2)[1])
        integrity = metadata["repository_integrity"]
        validations = integrity["validations"]
        order = integrity["order"]
    except (OSError, ValueError, IndexError, KeyError, TypeError, yaml.YAMLError):
        return None
    if (
        not isinstance(validations, dict)
        or not isinstance(order, list)
        or not all(isinstance(item, str) and item for item in order)
        or list(validations) != order
        or not order
    ):
        return None
    return order


def evaluation_input(root: Path = ROOT) -> dict[str, object]:
    return {
        "repository": str(root),
        "evaluation_context": {
            "realizations": [
                {
                    "environment_id": ENVIRONMENT_ID,
                    "identity_utf8": ENVIRONMENT_IDENTITY,
                    "command_prefix": [sys.executable],
                    "process_environment": dict(os.environ),
                }
            ]
        },
    }


def run_validation(root: Path = ROOT) -> dict[str, object]:
    return invoke_compat_result(
        root, "repository-integrity.evaluate", evaluation_input(root)
    )


def _obligation_diagnostic(prefix: str, obligation: dict[str, object]) -> str:
    message = f"{prefix} {obligation.get('id')}: {obligation.get('status')}"
    if obligation.get("exit_code") is not None:
        message += f" (command exited with {obligation['exit_code']})"
    return message


def _diagnostics(result: dict[str, object]) -> list[str]:
    diagnostics: list[str] = []
    if result.get("state_coherence_halt") is True:
        diagnostics.append(
            f"repository state coherence halted: {result.get('state_relation')}"
        )
    obligations = result.get("obligations")
    if isinstance(obligations, list):
        diagnostics.extend(
            _obligation_diagnostic("obligation", obligation)
            for obligation in obligations
            if isinstance(obligation, dict)
            and obligation.get("status") != "SATISFIED"
        )
    validations = result.get("validations")
    if not isinstance(validations, list):
        return ["provider returned no validation projection"]
    for validation in validations:
        if not isinstance(validation, dict) or validation.get("status") == "SATISFIED":
            continue
        message = f"validation {validation.get('id')}: {validation.get('status')}"
        nested = validation.get("obligations")
        failed = (
            [
                item
                for item in nested
                if isinstance(item, dict) and item.get("status") != "SATISFIED"
            ]
            if isinstance(nested, list)
            else []
        )
        if failed and failed[0].get("exit_code") is not None:
            message += f" (command exited with {failed[0]['exit_code']})"
        diagnostics.append(message)
    if not diagnostics:
        diagnostics.append("provider returned an inconsistent non-passing projection")
    return diagnostics


def _obligations_satisfied(items: object) -> bool:
    return isinstance(items, list) and all(
        isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and bool(item["id"])
        and item.get("status") == "SATISFIED"
        and item.get("executed") is True
        and item.get("exit_code") == "0"
        for item in items
    )


def _validations_satisfied(items: object) -> bool:
    return isinstance(items, list) and all(
        isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and bool(item["id"])
        and item.get("status") == "SATISFIED"
        and _obligations_satisfied(item.get("obligations"))
        for item in items
    )


def _coherent_pass(result: dict[str, object], root: Path = ROOT) -> bool:
    expected = _expected_validation_ids(root)
    validations = result.get("validations")
    obligations = result.get("obligations")
    if (
        expected is None
        or not isinstance(validations, list)
        or not isinstance(obligations, list)
        or not all(isinstance(item, dict) for item in validations)
    ):
        return False
    validation_ids = [item.get("id") for item in validations]
    obligation_ids = [
        item.get("id") for item in obligations if isinstance(item, dict)
    ]
    nested_ids = [
        [item.get("id") for item in validation.get("obligations", [])]
        if isinstance(validation.get("obligations"), list)
        else []
        for validation in validations
    ]
    return (
        result.get("verdict") == "PASS"
        and result.get("state_relation") == "EQUAL"
        and result.get("state_coherence_halt") is False
        and validation_ids == expected
        and obligation_ids == expected
        and nested_ids == [[validation_id] for validation_id in expected]
        and len(validation_ids) == len(set(validation_ids))
        and _validations_satisfied(validations)
        and _obligations_satisfied(obligations)
    )


def main() -> int:
    try:
        result = run_validation()
    except ProtoRingExecutableError as error:
        print(f"ERROR: repository integrity: {error}", file=sys.stderr)
        print("repository integrity: FAILED", file=sys.stderr)
        return 1
    if not _coherent_pass(result, ROOT):
        for diagnostic in _diagnostics(result):
            print(f"ERROR: {diagnostic}", file=sys.stderr)
        print("repository integrity: FAILED", file=sys.stderr)
        return 1
    print("repository integrity: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
