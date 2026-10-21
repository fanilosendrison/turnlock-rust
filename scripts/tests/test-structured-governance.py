#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CHECKER = SCRIPTS / "check-structured-governance.py"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_checker():
    spec = importlib.util.spec_from_file_location("check_structured_governance", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load structured governance checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def frontmatter(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---\n", 2)[1])


checker = load_checker()


class StructuredGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = checker.load_structured_governance(ROOT)
        cls.model = frontmatter(ROOT / "AGENTS.md")["repository_governance"]
        governance = ROOT / "docs/repository-governance"
        cls.authority = frontmatter(
            governance / "turnlock-rust-governance-authority.md"
        )["governance_authority"]
        cls.projections = frontmatter(
            governance / "turnlock-rust-projection-integrity.md"
        )["projection_registry"]
        cls.integrity = frontmatter(
            governance / "turnlock-rust-repository-integrity.md"
        )["repository_integrity"]
        cls.bindings = frontmatter(
            governance / "turnlock-rust-governance-bindings.md"
        )["governance_bindings"]
        cls.evidence = frontmatter(
            governance / "turnlock-rust-evidence-requirements.md"
        )["evidence_requirements"]

    def test_native_composition_is_complete(self) -> None:
        self.assertEqual("composition", self.state["stage"])
        self.assertTrue(self.state["identity_present"])
        self.assertTrue(all(self.state["components"].values()))
        self.assertEqual([], checker.check(ROOT))

    def test_model_declares_exact_applicable_capabilities(self) -> None:
        self.assertEqual(2, self.model["model_version"])
        self.assertEqual(
            {
                "architecture_decisions",
                "governance_authority",
                "governed_objects",
                "shared_governance_provider",
                "projection_integrity",
                "repository_integrity",
                "evidence_requirements",
                "authoritative_ref_monotonicity",
            },
            set(self.model["capabilities"]),
        )
        self.assertEqual("registry", self.model["provider"]["binding"]["route"])
        for carrier in (
            "turnlock-rust-governance-authority.md",
            "turnlock-rust-governance-bindings.md",
            "turnlock-rust-governed-objects.md",
            "turnlock-rust-repository-integrity.md",
            "turnlock-rust-projection-integrity.md",
            "turnlock-rust-evidence-requirements.md",
        ):
            self.assertIn(
                f"docs/repository-governance/{carrier}", self.state["scope_paths"]
            )

    def test_native_composition_is_read_only(self) -> None:
        command = ["git", "-C", str(ROOT), "status", "--porcelain=v2", "-z"]
        before = subprocess.run(command, check=True, capture_output=True).stdout
        checker.load_structured_governance(ROOT)
        after = subprocess.run(command, check=True, capture_output=True).stdout
        self.assertEqual(before, after)

    def test_executable_provider_authority_is_registry_only(self) -> None:
        roles = self.authority["responsibilities"]["executable_provider_binding"][
            "roles"
        ]
        self.assertEqual(
            {
                "governance_binding_registry": "authority",
                "effective_proto_ring_provider": "secondary_representation",
                "proto_ring_environment": "non_authoritative",
            },
            roles,
        )
        self.assertNotIn("executable_dependency_manifest", self.authority["sources"])

    def test_binding_registry_contains_exact_active_bindings(self) -> None:
        bindings = self.bindings["bindings"]
        self.assertEqual(
            {
                "proto_ring_executable",
                "shared_governance_provider_contract",
                "projection_integrity_contract",
                "exact_evidence_binding_contract",
                "governance_authority_contract",
                "governed_objects_contract",
                "authoritative_ref_monotonicity_contract",
                "repository_governance_model_contract",
                "repository_governance_state_contract",
                "repository_integrity_contract",
                "evidence_requirements_contract",
            },
            set(bindings),
        )
        executable = bindings["proto_ring_executable"]
        self.assertEqual(
            "814a884ccb759b0fdbde48673a74428d6443b847",
            executable["identity"]["commit"],
        )
        self.assertEqual(
            "governance_binding_registry", executable["authority"]["source"]
        )
        self.assertEqual(
            "9a1ed2d71d079b0118177c2a509ca356c371a597",
            bindings["repository_governance_state_contract"]["identity"]["commit"],
        )
        self.assertEqual(
            "890ed560e61e205067bdf3628e419302613ef06e",
            bindings["repository_governance_model_contract"]["identity"]["commit"],
        )

    def test_projection_has_only_five_retained_projections(self) -> None:
        projections = self.projections["projections"]
        self.assertEqual(
            {
                "adr_index",
                "adr_annotated_history",
                "governed_adr_catalog",
                "governed_invariant_catalog",
                "effective_proto_ring_realization",
            },
            set(projections),
        )
        self.assertNotIn("executable_binding_registry_representation", projections)
        realization = projections["effective_proto_ring_realization"]
        self.assertEqual("governance_binding_registry", realization["canonical_source"])
        self.assertEqual("effective_proto_ring_provider", realization["secondary_source"])
        self.assertEqual("proto_ring_environment", realization["generator_source"])
        self.assertEqual("proto_ring_executable", realization["binding"])
        self.assertEqual("proto_ring_provider_currentness", realization["validation"])

    def test_empty_evidence_registry_and_archive_custody_remain_turnlock_owned(self) -> None:
        self.assertEqual({}, self.evidence["requirements"])
        self.assertNotIn("gate_a_current_subject", self.authority["sources"])
        self.assertNotIn("gate_a_current_protocol_context", self.authority["sources"])
        self.assertNotIn("gate_a_review_candidates", self.authority["sources"])
        self.assertEqual(
            {
                "assurance_archive_manifest": "authority",
                "assurance_archive_payload": "non_authoritative",
            },
            self.authority["responsibilities"]["historical_source_custody"][
                "roles"
            ],
        )
        self.assertEqual(
            {"repository_integrity_profile": "authority"},
            self.authority["responsibilities"]["repository_integrity_profile"][
                "roles"
            ],
        )

    def test_persistent_integrity_owns_exact_order(self) -> None:
        validations = self.integrity["validations"]
        order = self.integrity["order"]
        self.assertEqual(29, len(validations))
        self.assertEqual(list(validations), order)
        self.assertEqual(
            ["assurance_archive_tests", "assurance_archive_custody"], order[-2:]
        )
        self.assertEqual(
            [2],
            validations["authoritative_ref_monotonicity_effective_rules"]["command"] [
                "undetermined_exit_codes"
            ],
        )

    def test_obsolete_carriers_are_absent(self) -> None:
        governance = ROOT / "docs/repository-governance"
        self.assertFalse((governance / "turnlock-rust-shared-governance-provider.md").exists())
        self.assertFalse((governance / "turnlock-rust-exact-evidence-binding.md").exists())
        for path in (
            governance / "turnlock-rust-governance-authority.md",
            governance / "turnlock-rust-governed-objects.md",
            governance / "turnlock-rust-authoritative-ref-monotonicity.md",
        ):
            self.assertNotIn("_contract:", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
