#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
import sys
import unittest
from unittest import mock

import yaml
from proto_ring.exact_evidence_binding import (
    BindingStatus,
    EvidenceBinding,
    EvidenceRequirement,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "scripts" / "check-formal-traceability.py"
EXECUTABLE_PROVIDER_COMMIT = "305d968c50db17cce43199ae3fa78d64da2aabdb"
EXACT_EVIDENCE_CONTRACT_COMMIT = "3bddcd4b49147f022466fdeb4acbf590e68890ce"
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "repository-governance"
    / "turnlock-rust-exact-evidence-binding.md"
)


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_formal_traceability_exact_evidence_binding",
        CHECKER_PATH,
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
    def test_requirements_pin_exact_provider(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn(
            "proto-ring @ git+https://github.com/fanilosendrison/"
            f"proto-ring.git@{EXECUTABLE_PROVIDER_COMMIT}",
            requirements.splitlines(),
        )

    def test_local_binding_pins_exact_contract(self) -> None:
        text = CONTRACT_PATH.read_text(encoding="utf-8")
        _prefix, frontmatter, _body = text.split("---", 2)
        metadata = yaml.safe_load(frontmatter)
        self.assertEqual(
            {
                "repository": "fanilosendrison/proto-ring",
                "commit": EXACT_EVIDENCE_CONTRACT_COMMIT,
                "path": "docs/contracts/exact-evidence-binding.md",
            },
            metadata["exact_evidence_binding"]["contract"],
        )

    def test_checker_delegates_to_shared_objects(self) -> None:
        self.assertIs(checker.BindingStatus, BindingStatus)
        self.assertIs(checker.EvidenceRequirement, EvidenceRequirement)
        self.assertIs(checker.EvidenceBinding, EvidenceBinding)
        self.assertIs(checker.evaluate_evidence_binding, evaluate)

        subject = gate_a_subject()
        with mock.patch.object(
            checker,
            "evaluate_evidence_binding",
            return_value=BindingStatus.MATCH,
        ) as shared_evaluate:
            status = checker._gate_a_binding_status(
                current_subject=subject,
                current_bundle_sha256="current-bundle",
                record=review_record(),
                gate_a_subject=subject,
                context_required=True,
            )

        self.assertIs(status, BindingStatus.MATCH)
        requirement, evidence = shared_evaluate.call_args.args
        self.assertIs(type(requirement), EvidenceRequirement)
        self.assertIs(type(evidence), EvidenceBinding)

    def test_exact_subject_matches_without_context(self) -> None:
        subject = gate_a_subject()
        self.assertIs(
            checker._gate_a_binding_status(
                current_subject=subject,
                current_bundle_sha256=None,
                record=review_record(),
                gate_a_subject=subject,
                context_required=False,
            ),
            BindingStatus.MATCH,
        )

    def test_wrong_review_class_mismatches(self) -> None:
        subject = gate_a_subject()
        self.assertIs(
            checker._gate_a_binding_status(
                current_subject=subject,
                current_bundle_sha256=None,
                record=review_record(review_class="other-review"),
                gate_a_subject=subject,
                context_required=False,
            ),
            BindingStatus.MISMATCH,
        )

    def test_different_exact_subject_mismatches(self) -> None:
        self.assertIs(
            checker._gate_a_binding_status(
                current_subject=gate_a_subject("current"),
                current_bundle_sha256=None,
                record=review_record(),
                gate_a_subject=gate_a_subject("historical"),
                context_required=False,
            ),
            BindingStatus.MISMATCH,
        )

    def test_exact_current_protocol_context_matches(self) -> None:
        subject = gate_a_subject()
        self.assertIs(
            checker._gate_a_binding_status(
                current_subject=subject,
                current_bundle_sha256="current-bundle",
                record=review_record(bundle_sha256="current-bundle"),
                gate_a_subject=subject,
                context_required=True,
            ),
            BindingStatus.MATCH,
        )

    def test_stale_protocol_context_mismatches(self) -> None:
        subject = gate_a_subject()
        self.assertIs(
            checker._gate_a_binding_status(
                current_subject=subject,
                current_bundle_sha256="current-bundle",
                record=review_record(bundle_sha256="stale-bundle"),
                gate_a_subject=subject,
                context_required=True,
            ),
            BindingStatus.MISMATCH,
        )

    def test_required_current_protocol_context_unavailable_is_undetermined(self) -> None:
        subject = gate_a_subject()
        self.assertIs(
            checker._gate_a_binding_status(
                current_subject=subject,
                current_bundle_sha256=None,
                record=review_record(),
                gate_a_subject=subject,
                context_required=True,
            ),
            BindingStatus.UNDETERMINED,
        )

    def test_current_subject_unavailable_is_undetermined(self) -> None:
        self.assertIs(
            checker._gate_a_binding_status(
                current_subject=None,
                current_bundle_sha256=None,
                record=review_record(),
                gate_a_subject=gate_a_subject(),
                context_required=False,
            ),
            BindingStatus.UNDETERMINED,
        )

    def test_derive_gate_a_has_no_direct_generic_binding_comparisons(self) -> None:
        source = inspect.getsource(checker.derive_gate_a)
        self.assertNotIn(
            'record.get("review_class") != GATE_A_REVIEW_CLASS',
            source,
        )
        self.assertNotIn("gate_a_subjects[0] != current_subject", source)
        self.assertNotIn("bundle_sha256 == current_bundle_sha256", source)
        self.assertIn("_gate_a_binding_status", source)


if __name__ == "__main__":
    unittest.main()
