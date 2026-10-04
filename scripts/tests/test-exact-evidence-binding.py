#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
import sys
import unittest
from unittest import mock

from proto_ring.evidence_requirements import (
    EvidenceClassKind,
    InstantiationKind,
)
from proto_ring.exact_evidence_binding import (
    BindingStatus,
    EvidenceBinding,
    EvidenceRequirement,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "scripts" / "check-formal-traceability.py"
EXECUTABLE_PROVIDER_COMMIT = "dedb01a3a9b7a18930c9da75afa3773b5ad67f69"


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_formal_traceability_exact_evidence_binding", CHECKER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load formal traceability checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


def gate_a_subject(sha256: str = "subject-sha") -> dict:
    return {
        "subject_type": "derived",
        "selector": checker.GATE_A_SUBJECT_SELECTOR,
        "sha256": sha256,
    }


def review_record(
    *,
    review_class: object = checker.GATE_A_REVIEW_CLASS,
    bundle_sha256: object = "current-bundle",
) -> dict:
    return {
        "review_class": review_class,
        "protocol": {"protocol_bundle": {"sha256": bundle_sha256}},
    }


class ExactEvidenceBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.subject_requirement, cls.protocol_requirement = (
            checker._load_gate_a_requirements(ROOT)
        )

    def test_requirements_pin_exact_provider(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn(
            "proto-ring @ git+https://github.com/fanilosendrison/"
            f"proto-ring.git@{EXECUTABLE_PROVIDER_COMMIT}",
            requirements.splitlines(),
        )

    def test_routed_registry_has_exact_gate_a_requirements(self) -> None:
        requirements = {
            self.subject_requirement.id: self.subject_requirement,
            self.protocol_requirement.id: self.protocol_requirement,
        }
        self.assertEqual(
            {
                "gate_a_subject_binding",
                "gate_a_current_protocol_binding",
            },
            set(requirements),
        )
        for requirement in requirements.values():
            self.assertEqual("formal_assurance_graph", requirement.responsibility_id)
            self.assertIs(InstantiationKind.SINGLE, requirement.instances.kind)
            self.assertIs(EvidenceClassKind.EXPLICIT, requirement.evidence_classes.kind)
            self.assertEqual(
                frozenset({"assurance-decomposition"}),
                requirement.evidence_classes.explicit_classes,
            )
            self.assertEqual("gate_a_current_subject", requirement.subject_source_id)
            self.assertEqual("gate_a_review_candidates", requirement.candidate_source_id)
        self.assertFalse(self.subject_requirement.context.required)
        self.assertIsNone(self.subject_requirement.context.source_id)
        self.assertTrue(self.protocol_requirement.context.required)
        self.assertEqual(
            "gate_a_current_protocol_context",
            self.protocol_requirement.context.source_id,
        )

    def test_checker_delegates_registry_derived_runtime_values(self) -> None:
        subject = gate_a_subject()
        with mock.patch.object(
            checker, "evaluate_evidence_binding", return_value=BindingStatus.MATCH
        ) as shared_evaluate:
            status = checker._gate_a_binding_status(
                requirement=self.protocol_requirement,
                current_subject=subject,
                current_bundle_sha256="current-bundle",
                record=review_record(),
                gate_a_subject=subject,
            )
        self.assertIs(status, BindingStatus.MATCH)
        requirement, evidence = shared_evaluate.call_args.args
        self.assertIs(type(requirement), EvidenceRequirement)
        self.assertIs(type(evidence), EvidenceBinding)
        self.assertEqual(
            self.protocol_requirement.evidence_classes.explicit_classes,
            requirement.admitted_classes,
        )

    def test_subject_only_context_policy_comes_from_registry(self) -> None:
        subject = gate_a_subject()
        with mock.patch.object(
            checker, "evaluate_evidence_binding", return_value=BindingStatus.MATCH
        ) as shared_evaluate:
            checker._gate_a_binding_status(
                requirement=self.subject_requirement,
                current_subject=subject,
                current_bundle_sha256="current-bundle",
                record=review_record(),
                gate_a_subject=subject,
            )
        runtime = shared_evaluate.call_args.args[0]
        self.assertFalse(runtime.context_required)
        self.assertIsNone(runtime.context_identity)

    def test_current_protocol_context_policy_comes_from_registry(self) -> None:
        subject = gate_a_subject()
        with mock.patch.object(
            checker, "evaluate_evidence_binding", return_value=BindingStatus.MATCH
        ) as shared_evaluate:
            checker._gate_a_binding_status(
                requirement=self.protocol_requirement,
                current_subject=subject,
                current_bundle_sha256="current-bundle",
                record=review_record(),
                gate_a_subject=subject,
            )
        runtime = shared_evaluate.call_args.args[0]
        self.assertTrue(runtime.context_required)
        self.assertEqual(b"current-bundle", runtime.context_identity)

    def status(self, requirement, *, current="current-bundle", record="current-bundle", review_class=None):
        subject = gate_a_subject()
        return checker._gate_a_binding_status(
            requirement=requirement,
            current_subject=subject,
            current_bundle_sha256=current,
            record=review_record(
                review_class=(checker.GATE_A_REVIEW_CLASS if review_class is None else review_class),
                bundle_sha256=record,
            ),
            gate_a_subject=subject,
        )

    def test_stale_protocol_classification_is_unchanged(self) -> None:
        self.assertIs(
            BindingStatus.MATCH,
            self.status(self.subject_requirement, current="current", record="stale"),
        )
        self.assertIs(
            BindingStatus.MISMATCH,
            self.status(self.protocol_requirement, current="current", record="stale"),
        )

    def test_wrong_review_class_remains_mismatch(self) -> None:
        self.assertIs(
            BindingStatus.MISMATCH,
            self.status(self.subject_requirement, review_class="other-review"),
        )

    def test_missing_current_context_remains_undetermined(self) -> None:
        self.assertIs(
            BindingStatus.UNDETERMINED,
            self.status(self.protocol_requirement, current=None),
        )

    def test_different_exact_subject_remains_mismatch(self) -> None:
        self.assertIs(
            BindingStatus.MISMATCH,
            checker._gate_a_binding_status(
                requirement=self.subject_requirement,
                current_subject=gate_a_subject("current"),
                current_bundle_sha256=None,
                record=review_record(),
                gate_a_subject=gate_a_subject("historical"),
            ),
        )

    def test_current_subject_unavailable_remains_undetermined(self) -> None:
        self.assertIs(
            BindingStatus.UNDETERMINED,
            checker._gate_a_binding_status(
                requirement=self.subject_requirement,
                current_subject=None,
                current_bundle_sha256=None,
                record=review_record(),
                gate_a_subject=gate_a_subject(),
            ),
        )

    def test_hardcoded_requirement_policy_cannot_return(self) -> None:
        signature = inspect.signature(checker._gate_a_binding_status)
        self.assertNotIn("context_required", signature.parameters)
        source = CHECKER_PATH.read_text(encoding="utf-8")
        compact = "".join(source.split())
        self.assertNotIn(
            "admitted_classes=frozenset({GATE_A_REVIEW_CLASS})", compact
        )
        derive_source = inspect.getsource(checker.derive_gate_a)
        self.assertNotIn("context_required=False", derive_source)
        self.assertNotIn("context_required=True", derive_source)
        self.assertIn("subject_requirement", derive_source)
        self.assertIn("current_protocol_requirement", derive_source)
        self.assertEqual(1, source.count("EvidenceRequirement("))

    def test_checker_uses_shared_exact_evidence_objects(self) -> None:
        self.assertIs(checker.BindingStatus, BindingStatus)
        self.assertIs(checker.EvidenceRequirement, EvidenceRequirement)
        self.assertIs(checker.EvidenceBinding, EvidenceBinding)
        self.assertIs(checker.evaluate_evidence_binding, evaluate)


if __name__ == "__main__":
    unittest.main()
