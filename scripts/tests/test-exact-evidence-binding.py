#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CHECKER_PATH = SCRIPTS / "check-formal-traceability.py"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


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
    *, review_class: object = checker.GATE_A_REVIEW_CLASS, bundle: object = "bundle"
) -> dict:
    return {
        "review_class": review_class,
        "protocol": {"protocol_bundle": {"sha256": bundle}},
    }


class ExactEvidenceBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.subject_requirement, cls.protocol_requirement = (
            checker._load_gate_a_requirements(ROOT)
        )

    def status(
        self,
        requirement: dict,
        *,
        current_subject: dict | None = None,
        current_bundle: object = "bundle",
        record_subject: dict | None = None,
        review_class: object = checker.GATE_A_REVIEW_CLASS,
        record_bundle: object = "bundle",
    ) -> str:
        subject = gate_a_subject() if current_subject is None else current_subject
        return checker._gate_a_binding_status(
            requirement=requirement,
            current_subject=subject,
            current_bundle_sha256=current_bundle,
            record=review_record(review_class=review_class, bundle=record_bundle),
            gate_a_subject=(subject if record_subject is None else record_subject),
        )

    def test_routed_registry_has_exact_gate_a_requirements(self) -> None:
        requirements = {
            self.subject_requirement["id"]: self.subject_requirement,
            self.protocol_requirement["id"]: self.protocol_requirement,
        }
        self.assertEqual(
            {"gate_a_subject_binding", "gate_a_current_protocol_binding"},
            set(requirements),
        )
        for requirement in requirements.values():
            self.assertEqual("single", requirement["instances"]["kind"])
            self.assertEqual("explicit", requirement["evidence_classes"]["kind"])
            self.assertEqual(
                ["assurance-decomposition"],
                requirement["evidence_classes"]["classes"],
            )
        self.assertEqual(
            {"required": False, "source": None},
            self.subject_requirement["context"],
        )
        self.assertEqual(
            {
                "required": True,
                "source": "gate_a_current_protocol_context",
            },
            self.protocol_requirement["context"],
        )

    def test_six_native_behavior_cases(self) -> None:
        cases = (
            (self.subject_requirement, {}, "MATCH"),
            (self.subject_requirement, {"review_class": "other"}, "MISMATCH"),
            (self.subject_requirement, {"current_subject": None}, "UNDETERMINED"),
            (
                self.subject_requirement,
                {"record_subject": gate_a_subject("historical")},
                "MISMATCH",
            ),
            (self.protocol_requirement, {}, "MATCH"),
            (self.protocol_requirement, {"current_bundle": None}, "UNDETERMINED"),
        )
        observed = []
        for requirement, arguments, expected in cases:
            with self.subTest(expected=expected, arguments=arguments):
                if "current_subject" in arguments:
                    status = checker._gate_a_binding_status(
                        requirement=requirement,
                        current_subject=None,
                        current_bundle_sha256="bundle",
                        record=review_record(),
                        gate_a_subject=gate_a_subject(),
                    )
                else:
                    status = self.status(requirement, **arguments)
                self.assertEqual(expected, status)
                observed.append(status)
        self.assertEqual(6, len(observed))

    def test_stale_protocol_context_remains_mismatch(self) -> None:
        self.assertEqual(
            "MATCH",
            self.status(
                self.subject_requirement,
                current_bundle="current",
                record_bundle="stale",
            ),
        )
        self.assertEqual(
            "MISMATCH",
            self.status(
                self.protocol_requirement,
                current_bundle="current",
                record_bundle="stale",
            ),
        )

    def test_malformed_context_required_fails_closed(self) -> None:
        for malformed in (None, "true", 1):
            with self.subTest(malformed=malformed):
                requirement = {
                    **self.protocol_requirement,
                    "context": {
                        **self.protocol_requirement["context"],
                        "required": malformed,
                    },
                }
                with self.assertRaises(checker.EvidenceRequirementsError):
                    checker._runtime_gate_a_requirement(
                        requirement, gate_a_subject(), "bundle"
                    )

    def test_requirements_contains_no_python_provider(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertNotIn("proto-ring", requirements)
        self.assertNotIn("proto_ring", requirements)

    def test_checker_uses_native_qualified_operations(self) -> None:
        source = CHECKER_PATH.read_text(encoding="utf-8")
        self.assertIn('"evidence-requirements.registry"', source)
        self.assertIn('"exact-evidence-binding.evaluate"', source)
        tree = ast.parse(source)
        imports = [
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module is not None
            and (node.module == "proto_ring" or node.module.startswith("proto_ring."))
        ]
        imports.extend(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
            if alias.name == "proto_ring" or alias.name.startswith("proto_ring.")
        )
        self.assertEqual([], imports)


if __name__ == "__main__":
    unittest.main()
