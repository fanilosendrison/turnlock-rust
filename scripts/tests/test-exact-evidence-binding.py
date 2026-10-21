#!/usr/bin/env python3
"""Exercise the retained generic binding contract without retired Gate A policy.

The former Gate A consumer tests are archived with their retired responsibility.
These synthetic cases retain direct coverage of the applicable native Exact
Evidence Binding comparator and of the valid empty local requirement registry.
"""
from __future__ import annotations

import ast
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from proto_ring_executable_binding import (  # noqa: E402
    ProtoRingExecutableError,
    invoke_compat_result,
)


def requirement(*, subject: bytes | None = b"known-subject", context=()) -> dict:
    context_required = context != ()
    context_value = None if context == () or context is None else context
    return {
        "admitted_classes": ["check"],
        "subject_hex": None if subject is None else subject.hex(),
        "context_required": context_required,
        "context_hex": (
            None if context_value is None else bytes(context_value).hex()
        ),
    }


def binding(
    *,
    evidence_class: str = "check",
    subject: bytes | None = b"known-subject",
    context: bytes | None = None,
) -> dict:
    return {
        "evidence_class": evidence_class,
        "subject_hex": None if subject is None else subject.hex(),
        "context_hex": None if context is None else context.hex(),
    }


def evaluate(required: dict, candidate: dict) -> str:
    value = invoke_compat_result(
        ROOT,
        "exact-evidence-binding.evaluate",
        {
            "mode": "evaluate_binding",
            "requirement": required,
            "binding": candidate,
        },
    )
    return value["status"]


class ExactEvidenceBindingTests(unittest.TestCase):
    def test_exact_known_binding_matches(self) -> None:
        self.assertEqual("MATCH", evaluate(requirement(), binding()))

    def test_different_class_mismatches(self) -> None:
        self.assertEqual(
            "MISMATCH", evaluate(requirement(), binding(evidence_class="other"))
        )

    def test_different_known_subject_mismatches(self) -> None:
        self.assertEqual(
            "MISMATCH", evaluate(requirement(), binding(subject=b"other-subject"))
        )

    def test_unknown_required_subject_is_undetermined(self) -> None:
        self.assertEqual("UNDETERMINED", evaluate(requirement(subject=None), binding()))

    def test_different_required_context_mismatches(self) -> None:
        self.assertEqual(
            "MISMATCH",
            evaluate(
                requirement(context=b"required-context"),
                binding(context=b"other-context"),
            ),
        )

    def test_unknown_required_context_is_undetermined(self) -> None:
        self.assertEqual(
            "UNDETERMINED",
            evaluate(
                requirement(context=None),
                binding(context=b"candidate-context"),
            ),
        )

    def test_malformed_context_required_is_rejected_without_coercion(self) -> None:
        malformed = {**requirement(), "context_required": "true"}
        with self.assertRaises(ProtoRingExecutableError):
            evaluate(malformed, binding())

    def test_empty_local_registry_is_valid_and_invents_no_requirement(self) -> None:
        value = invoke_compat_result(
            ROOT,
            "evidence-requirements.registry",
            {"repository": str(ROOT), "requirement_ids": []},
        )
        self.assertEqual({}, value["requirements"])

    def test_native_operation_is_used_without_retired_checker_or_provider(self) -> None:
        source = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = [
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        ]
        imports.extend(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        self.assertFalse(
            any(name == "proto_ring" or name.startswith("proto_ring.") for name in imports)
        )
        self.assertFalse(any("formal_traceability" in name for name in imports))


if __name__ == "__main__":
    unittest.main()
