#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-formal-traceability.py"

spec = importlib.util.spec_from_file_location("formal_traceability", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

MANIFEST_RELATIVE = Path("formal/verification.yaml")
MIGRATION_RELATIVE = Path("formal/migrations/verification-v2-to-v3-property-audit.yaml")
MAPPING_RELATIVE = Path("docs/formal/invariant-mapping.md")

GATE_A_ATTACK_OBJECTIVES = [
    "semantic-strengthening",
    "semantic-weakening",
    "omitted-valid-behavior",
    "invented-behavior",
    "collapsed-normative-distinction",
    "invented-formal-distinction",
    "hidden-assumption",
    "wrong-quantification",
    "wrong-occurrence-scope",
    "modality-mismatch",
    "vacuity",
    "coverage-gap",
    "alternative-compatible-interpretation",
    "cross-feature-interaction-failure",
]


def make_fixture(temporary: str) -> Path:
    fixture_root = Path(temporary)
    shutil.copytree(ROOT / "docs", fixture_root / "docs")
    shutil.copytree(ROOT / "formal", fixture_root / "formal")
    scripts_dir = fixture_root / "scripts"
    scripts_dir.mkdir()
    shutil.copyfile(
        ROOT / "scripts" / "render-formal-mapping.py",
        scripts_dir / "render-formal-mapping.py",
    )
    shutil.copyfile(
        ROOT / "scripts" / "check-formal-traceability.py",
        scripts_dir / "check-formal-traceability.py",
    )
    return fixture_root


def load_manifest(fixture_root: Path) -> dict:
    return yaml.safe_load((fixture_root / MANIFEST_RELATIVE).read_text())


def save_manifest(fixture_root: Path, manifest: dict) -> None:
    (fixture_root / MANIFEST_RELATIVE).write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )


def load_migration(fixture_root: Path) -> dict:
    return yaml.safe_load((fixture_root / MIGRATION_RELATIVE).read_text())


def save_migration(fixture_root: Path, migration: dict) -> None:
    (fixture_root / MIGRATION_RELATIVE).write_text(
        yaml.safe_dump(migration, sort_keys=False), encoding="utf-8"
    )


def manifest_sha(fixture_root: Path) -> str:
    return checker.sha256_hex((fixture_root / MANIFEST_RELATIVE).read_bytes())


def coverage_entry(manifest: dict, invariant: str) -> dict:
    for entry in manifest["normative_coverage"]:
        if entry["invariant"] == invariant:
            return entry
    raise AssertionError(f"missing coverage entry {invariant}")


def reviewer(reviewer_id: str, **overrides) -> dict:
    data = {
        "reviewer_id": reviewer_id,
        "reviewer_type": "frontier-llm",
        "provider": "provider",
        "model": "model",
        "model_version": "1",
        "prompt_sha256": "a" * 64,
    }
    data.update(overrides)
    return data


def make_review(
    fixture_root: Path,
    *,
    review_id: str = "REVIEW-0001",
    review_class: str = "assurance-decomposition",
    subjects: list[dict] | None = None,
    reviewers: list[dict] | None = None,
    findings: list[dict] | None = None,
    attack_objectives: list[str] | None = None,
) -> dict:
    if subjects is None:
        subject, errors = checker.build_gate_a_review_subject(
            fixture_root, load_manifest(fixture_root)
        )
        if errors or subject is None:
            raise AssertionError(errors or "Gate A subject derivation failed")
        subjects = [subject]
    if reviewers is None:
        reviewers = [reviewer("r1"), reviewer("r2")]
    return {
        "schema_version": "1.1",
        "review_id": review_id,
        "review_class": review_class,
        "repository_commit": "6d3c9851e0d66286280f8e49ebd8ed44da13d876",
        "subjects": subjects,
        "attack_objectives": (
            attack_objectives
            if attack_objectives is not None
            else list(GATE_A_ATTACK_OBJECTIVES)
        ),
        "reviewers": reviewers,
        "findings": findings if findings is not None else [],
        "supersedes_review_ids": [],
        "started_at": "2026-09-19T00:00:00Z",
        "completed_at": "2026-09-19T01:00:00Z",
    }


def write_review(fixture_root: Path, record: dict, name: str = "REVIEW-0001.yaml") -> Path:
    path = fixture_root / "formal" / "reviews" / name
    path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    return path


def write_raw_review(fixture_root: Path, name: str, text: str) -> Path:
    path = fixture_root / "formal" / "reviews" / name
    path.write_text(text, encoding="utf-8")
    return path


def write_candidate_model(fixture_root: Path) -> Path:
    path = fixture_root / "formal" / "Turnlock.tla"
    path.write_text(
        "---- MODULE Turnlock ----\n"
        "VARIABLES controlState\n"
        "DeclaredControlFlow == TRUE\n"
        "Advance == TRUE\n"
        "====\n",
        encoding="utf-8",
    )
    return path


def realization_payload(**overrides) -> dict:
    data = {
        "claim": "TL-CLAIM-001",
        "formal_semantic_domain": "operational",
        "backend": "tla+",
        "module": "Turnlock",
        "properties": ["DeclaredControlFlow"],
        "state_variables": ["controlState"],
        "actions": ["Advance"],
        "verification_profiles": [],
    }
    data.update(overrides)
    return data


def review_schema_errors(fixture_root: Path, record: dict) -> list:
    schema = json.loads(
        (
            fixture_root / "formal" / "reviews" / "review-evidence.schema.json"
        ).read_text(encoding="utf-8")
    )
    return list(Draft202012Validator(schema).iter_errors(record))


def finding(
    *,
    finding_id: str = "F-1",
    reviewer_ids: list[str] | None = None,
    material: bool = True,
    status: str = "open",
    disposition_rationale=None,
) -> dict:
    return {
        "finding_id": finding_id,
        "reviewer_ids": reviewer_ids if reviewer_ids is not None else ["r1"],
        "material": material,
        "statement": "A material semantic objection.",
        "argument": "The objection survives review.",
        "counterexample": None,
        "status": status,
        "disposition_rationale": disposition_rationale,
    }


class FormalTraceabilityTests(unittest.TestCase):
    def test_repository_conforms(self) -> None:
        errors, summary = checker.collect_errors(ROOT)
        self.assertEqual([], errors)
        self.assertEqual(42, summary["invariants"])
        self.assertEqual(83, summary["claims"])
        self.assertFalse(summary["gate_a"]["ready"])
        self.assertEqual(
            "hostile assurance-decomposition review evidence required",
            summary["gate_a"]["reason"],
        )

    def test_schema_v3_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["schema_version"] = 2
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any("must use schema_version 3" in error for error in errors), errors
            )

    def test_missing_invariant_coverage_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["normative_coverage"] = [
                entry
                for entry in manifest["normative_coverage"]
                if entry["invariant"] != "TL-INV-042"
            ]
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "missing from normative_coverage: TL-INV-042" in error
                    for error in errors
                ),
                errors,
            )

    def test_unknown_invariant_coverage_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["normative_coverage"].append(
                {
                    "invariant": "TL-INV-099",
                    "canonical_operational_coverage": "none",
                    "formal_claims": [],
                    "residual_claims": ["TL-CLAIM-001"],
                }
            )
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "unknown invariant IDs: TL-INV-099" in error for error in errors
                ),
                errors,
            )

    def test_duplicate_claim_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["claims"][82]["id"] = "TL-CLAIM-082"
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any("duplicate claim ID TL-CLAIM-082" in error for error in errors),
                errors,
            )

    def test_non_contiguous_claim_ids_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["claims"][82]["id"] = "TL-CLAIM-099"
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any("claim IDs must be contiguous" in error for error in errors),
                errors,
            )

    def test_unknown_normative_source_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["claims"][0]["normative_sources"].append("TL-INV-099")
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "references unknown normative source TL-INV-099" in error
                    for error in errors
                ),
                errors,
            )

    def test_unknown_claim_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            coverage_entry(manifest, "TL-INV-001")["formal_claims"].append(
                "TL-CLAIM-099"
            )
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "formal_claims references unknown TL-CLAIM-099" in error
                    for error in errors
                ),
                errors,
            )

    def test_claim_source_coverage_reverse_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            entry = coverage_entry(manifest, "TL-INV-001")
            entry["formal_claims"] = [
                claim_id
                for claim_id in entry["formal_claims"]
                if claim_id != "TL-CLAIM-002"
            ]
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "TL-CLAIM-002 declares normative source TL-INV-001" in error
                    for error in errors
                ),
                errors,
            )

    def test_full_coverage_with_residual_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            coverage_entry(manifest, "TL-INV-001")["residual_claims"] = ["TL-CLAIM-013"]
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any("TL-INV-001 coverage is full" in error for error in errors), errors
            )

    def test_none_coverage_with_formal_claim_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            coverage_entry(manifest, "TL-INV-011")["formal_claims"] = ["TL-CLAIM-014"]
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any("TL-INV-011 coverage is none" in error for error in errors), errors
            )

    def test_partial_coverage_missing_formal_side_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            coverage_entry(manifest, "TL-INV-009")["formal_claims"] = []
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any("TL-INV-009 coverage is partial" in error for error in errors),
                errors,
            )

    def test_partial_coverage_missing_residual_side_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            coverage_entry(manifest, "TL-INV-009")["residual_claims"] = []
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any("TL-INV-009 coverage is partial" in error for error in errors),
                errors,
            )

    def test_formal_coverage_referencing_non_formal_claim_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            coverage_entry(manifest, "TL-INV-001")["formal_claims"].append(
                "TL-CLAIM-013"
            )
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "formal_claims lists non-formal-behavioral TL-CLAIM-013" in error
                    for error in errors
                ),
                errors,
            )

    def test_behavioral_claim_without_modality_fails_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            del manifest["claims"][0]["modality"]
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            joined = "\n".join(errors)
            self.assertIn("schema", joined)
            self.assertIn("modality", joined)

    def test_non_behavioral_claim_with_modality_fails_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["claims"][12]["modality"] = "safety"
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            joined = "\n".join(errors)
            self.assertIn("schema", joined)
            self.assertIn("TL-CLAIM-013", joined)

    def test_legacy_migration_count_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            migration = load_migration(fixture_root)
            migration["entries"] = migration["entries"][:-1]
            save_migration(fixture_root, migration)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any("must contain exactly 50 entries" in error for error in errors),
                errors,
            )

    def test_legacy_migration_unknown_claim_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            migration = load_migration(fixture_root)
            migration["entries"][0]["migrated_to"] = ["TL-CLAIM-099"]
            save_migration(fixture_root, migration)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any("references unknown TL-CLAIM-099" in error for error in errors),
                errors,
            )

    def test_missing_generated_mapping_is_rejected_without_recreation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            mapping_path = fixture_root / MAPPING_RELATIVE
            mapping_path.unlink()
            self.assertFalse(mapping_path.exists())

            errors, _ = checker.collect_errors(fixture_root, check_generated=True)
            self.assertTrue(
                any(
                    "generated formal invariant mapping is missing" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(mapping_path.exists())

    def test_stale_generated_mapping_is_rejected_without_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            mapping_path = fixture_root / MAPPING_RELATIVE
            mapping_path.write_text("stale", encoding="utf-8")
            before = mapping_path.read_bytes()

            errors, _ = checker.collect_errors(fixture_root, check_generated=True)
            self.assertTrue(
                any(
                    "generated formal invariant mapping is stale" in error
                    for error in errors
                ),
                errors,
            )
            self.assertEqual(before, mapping_path.read_bytes())

    def test_renderer_stdout_matches_committed_mapping_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            mapping_path = fixture_root / MAPPING_RELATIVE
            committed = mapping_path.read_bytes()
            formal_listing_before = sorted(
                path.relative_to(fixture_root).as_posix()
                for path in (fixture_root / "formal").rglob("*")
            )

            result = subprocess.run(
                [sys.executable, "scripts/render-formal-mapping.py", "--stdout"],
                cwd=fixture_root,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr.decode("utf-8"))
            self.assertEqual(committed.decode("utf-8"), result.stdout.decode("utf-8"))
            self.assertEqual(committed, mapping_path.read_bytes())
            formal_listing_after = sorted(
                path.relative_to(fixture_root).as_posix()
                for path in (fixture_root / "formal").rglob("*")
            )
            self.assertEqual(formal_listing_before, formal_listing_after)

    def test_model_appearing_while_gate_a_blocked_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            model_path = fixture_root / "formal" / "Turnlock.tla"
            model_path.write_text("---- MODULE Turnlock ----\n====\n", encoding="utf-8")
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "formal/Turnlock.tla exists while Formal-Architecture-Ready is BLOCKED"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_absence_of_candidate_model_while_gate_a_blocked_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            self.assertFalse((fixture_root / "formal" / "Turnlock.tla").exists())
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])

    def test_review_evidence_with_fewer_than_two_reviewers_fails_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(fixture_root, reviewers=[reviewer("r1")]),
            )
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            joined = "\n".join(errors)
            self.assertIn("formal/reviews/REVIEW-0001.yaml", joined)
            self.assertIn("schema", joined)

    def test_duplicate_reviewer_ids_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    reviewers=[reviewer("r1"), reviewer("r1")],
                ),
            )
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any("reviewer_id values must be unique" in error for error in errors),
                errors,
            )

    def test_raw_manifest_artifact_subject_does_not_qualify(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    subjects=[
                        {
                            "subject_type": "artifact",
                            "path": MANIFEST_RELATIVE.as_posix(),
                            "sha256": manifest_sha(fixture_root),
                        }
                    ],
                ),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile assurance-decomposition review evidence required",
                summary["gate_a"]["reason"],
            )

    def test_material_open_finding_prevents_review_from_satisfying_gate_a(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(fixture_root, findings=[finding(status="open")]),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])

    def test_material_routed_finding_prevents_review_from_satisfying_gate_a(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(fixture_root, findings=[finding(status="routed")]),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])

    def test_resolved_material_finding_requires_disposition_rationale(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    findings=[finding(status="resolved", disposition_rationale=None)],
                ),
            )
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            joined = "\n".join(errors)
            self.assertIn("disposition_rationale", joined)

    def test_majority_reviewer_count_cannot_override_surviving_open_finding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    reviewers=[
                        reviewer("r1"),
                        reviewer("r2"),
                        reviewer("r3"),
                    ],
                    findings=[finding(reviewer_ids=["r1"], status="open")],
                ),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])

    def test_current_review_with_resolved_finding_derives_gate_a_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    findings=[
                        finding(
                            status="resolved",
                            disposition_rationale="The counterexample was refuted.",
                        )
                    ],
                ),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_incomplete_attack_coverage_does_not_satisfy_gate_a(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root, attack_objectives=["semantic-strengthening"]
                ),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertIn("required attack coverage", summary["gate_a"]["reason"])

    def test_missing_one_required_objective_blocks_gate_a(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            objectives = [
                objective
                for objective in GATE_A_ATTACK_OBJECTIVES
                if objective != "vacuity"
            ]
            write_review(
                fixture_root,
                make_review(fixture_root, attack_objectives=objectives),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])

    def test_complete_attack_coverage_can_satisfy_gate_a(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(fixture_root, make_review(fixture_root))
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])
            self.assertIn(
                "satisfies required attack coverage", summary["gate_a"]["reason"]
            )

    def test_manifest_reviewer_minimum_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["policy"]["hostile_review"]["minimum_independent_reviewers"] = 3
            save_manifest(fixture_root, manifest)
            write_review(
                fixture_root,
                make_review(
                    fixture_root, reviewers=[reviewer("r1"), reviewer("r2")]
                ),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])

            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    reviewers=[reviewer("r1"), reviewer("r2"), reviewer("r3")],
                ),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_clean_review_cannot_override_another_current_open_finding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(fixture_root, review_id="REVIEW-A"),
                name="REVIEW-A.yaml",
            )
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    review_id="REVIEW-B",
                    findings=[finding(status="open")],
                ),
                name="REVIEW-B.yaml",
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "unresolved material hostile-review finding exists",
                summary["gate_a"]["reason"],
            )

    def test_clean_review_cannot_override_a_routed_material_finding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(fixture_root, review_id="REVIEW-A"),
                name="REVIEW-A.yaml",
            )
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    review_id="REVIEW-B",
                    findings=[finding(status="routed")],
                ),
                name="REVIEW-B.yaml",
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])

    def test_refuted_material_finding_can_cease_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    findings=[
                        finding(
                            status="refuted",
                            disposition_rationale="The argument was refuted.",
                        )
                    ],
                ),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_malformed_yaml_review_evidence_is_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_raw_review(
                fixture_root, "REVIEW-BROKEN.yaml", "key: [unterminated\n"
            )
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "formal/reviews/REVIEW-BROKEN.yaml: cannot parse review evidence"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_malformed_json_review_evidence_is_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_raw_review(
                fixture_root,
                "REVIEW-BROKEN.json",
                'schema_version: "1.0"\nreview_id: REVIEW-1\n',
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "formal/reviews/REVIEW-BROKEN.json: cannot parse review evidence"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_non_mapping_yaml_review_evidence_is_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_raw_review(
                fixture_root, "REVIEW-NOT-MAPPING.yaml", "- one\n- two\n"
            )
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "review evidence must be a mapping" in error for error in errors
                ),
                errors,
            )

    def test_future_formal_realization_is_not_rejected_merely_for_existing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["formal_realizations"] = [realization_payload()]
            save_manifest(fixture_root, manifest)
            write_candidate_model(fixture_root)
            write_review(fixture_root, make_review(fixture_root))
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])
            self.assertFalse(
                any("must remain empty" in error for error in errors), errors
            )

    def test_missing_tla_realization_identifier_still_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["formal_realizations"] = [
                realization_payload(properties=["DoesNotExist"])
            ]
            save_manifest(fixture_root, manifest)
            write_candidate_model(fixture_root)
            write_review(fixture_root, make_review(fixture_root))
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "references missing TLA+ property DoesNotExist" in error
                    for error in errors
                ),
                errors,
            )

    def test_realization_without_candidate_model_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["formal_realizations"] = [realization_payload()]
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "formal_realizations are present but formal/Turnlock.tla is missing"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_renderer_fails_on_malformed_review_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_raw_review(
                fixture_root, "REVIEW-BROKEN.yaml", "key: [unterminated\n"
            )
            mapping_path = fixture_root / MAPPING_RELATIVE
            before = mapping_path.read_bytes()
            result = subprocess.run(
                [sys.executable, "scripts/render-formal-mapping.py", "--stdout"],
                cwd=fixture_root,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn(b"cannot parse review evidence", result.stderr)
            self.assertEqual(before, mapping_path.read_bytes())

    def test_adding_formal_realizations_does_not_change_gate_a_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, first_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], first_errors)
            manifest["formal_realizations"] = [realization_payload()]
            second, second_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], second_errors)
            self.assertEqual(first, second)
            self.assertEqual(first["sha256"], second["sha256"])

    def test_full_lifecycle_review_remains_current_after_realization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(fixture_root, make_review(fixture_root))
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

            manifest = load_manifest(fixture_root)
            manifest["formal_realizations"] = [realization_payload()]
            save_manifest(fixture_root, manifest)
            write_candidate_model(fixture_root)

            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_changing_claim_statement_invalidates_gate_a_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(fixture_root, make_review(fixture_root))
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

            manifest = load_manifest(fixture_root)
            manifest["claims"][0]["statement"] = (
                manifest["claims"][0]["statement"] + " (fixture change)"
            )
            save_manifest(fixture_root, manifest)

            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile assurance-decomposition review evidence required",
                summary["gate_a"]["reason"],
            )

    def test_changing_claim_normative_sources_changes_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            claim = next(
                claim
                for claim in manifest["claims"]
                if claim["id"] == "TL-CLAIM-002"
            )
            claim["normative_sources"] = sorted(
                claim["normative_sources"] + ["TL-INV-005"]
            )
            second, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            self.assertNotEqual(first["sha256"], second["sha256"])

    def test_changing_normative_coverage_changes_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            entry = coverage_entry(manifest, "TL-INV-004")
            entry["formal_claims"] = sorted(
                entry["formal_claims"] + ["TL-CLAIM-001"]
            )
            second, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            self.assertNotEqual(first["sha256"], second["sha256"])

    def test_changing_normative_specification_bytes_invalidates_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            first, _ = checker.build_gate_a_review_subject(
                fixture_root, load_manifest(fixture_root)
            )
            spec_path = fixture_root / "docs" / "specification" / "turnlock-spec.md"
            with open(spec_path, "a", encoding="utf-8") as handle:
                handle.write("\n<!-- fixture change -->\n")
            second, _ = checker.build_gate_a_review_subject(
                fixture_root, load_manifest(fixture_root)
            )
            self.assertNotEqual(first["sha256"], second["sha256"])

    def test_changing_referenced_adr_bytes_invalidates_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            first, _ = checker.build_gate_a_review_subject(
                fixture_root, load_manifest(fixture_root)
            )
            adr_path = next((fixture_root / "docs" / "adr").glob("adr-041-*.md"))
            with open(adr_path, "a", encoding="utf-8") as handle:
                handle.write("\n<!-- fixture change -->\n")
            second, _ = checker.build_gate_a_review_subject(
                fixture_root, load_manifest(fixture_root)
            )
            self.assertNotEqual(first["sha256"], second["sha256"])

    def test_mechanical_evidence_policy_does_not_change_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            manifest["policy"]["mechanical_evidence"]["tlc"][
                "evidence_directory"
            ] = "formal/other-results"
            second, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            self.assertEqual(first, second)

    def test_hostile_review_policy_is_not_part_of_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            manifest["policy"]["hostile_review"][
                "minimum_independent_reviewers"
            ] = 3
            second, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            self.assertEqual(first, second)

    def test_claim_ordering_does_not_change_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            manifest["claims"] = list(reversed(manifest["claims"]))
            second, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            self.assertEqual(first, second)

    def test_normative_coverage_ordering_does_not_change_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            manifest["normative_coverage"] = list(
                reversed(manifest["normative_coverage"])
            )
            for entry in manifest["normative_coverage"]:
                entry["formal_claims"] = list(reversed(entry["formal_claims"]))
                entry["residual_claims"] = list(reversed(entry["residual_claims"]))
            second, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            self.assertEqual(first, second)

    def test_normative_source_ordering_does_not_change_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            claim = next(
                claim
                for claim in manifest["claims"]
                if len(claim["normative_sources"]) > 1
            )
            claim["normative_sources"] = list(reversed(claim["normative_sources"]))
            second, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            self.assertEqual(first, second)

    def test_formal_semantic_domain_change_changes_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            manifest["policy"]["formal_semantic_domains"][0][
                "module"
            ] = "TurnlockFixture"
            second, _ = checker.build_gate_a_review_subject(fixture_root, manifest)
            self.assertNotEqual(first["sha256"], second["sha256"])

    def test_missing_authority_artifact_fails_subject_derivation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            adr_path = next((fixture_root / "docs" / "adr").glob("adr-040-*.md"))
            adr_path.unlink()
            subject, subject_errors = checker.build_gate_a_review_subject(
                fixture_root, load_manifest(fixture_root)
            )
            self.assertIsNone(subject)
            self.assertTrue(subject_errors)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(errors)
            self.assertFalse(summary["gate_a"]["ready"])

    def test_ambiguous_adr_resolution_fails_subject_derivation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            duplicate = (
                fixture_root / "docs" / "adr" / "adr-041-duplicate-fixture.md"
            )
            duplicate.write_text("# fixture duplicate\n", encoding="utf-8")
            subject, subject_errors = checker.build_gate_a_review_subject(
                fixture_root, load_manifest(fixture_root)
            )
            self.assertIsNone(subject)
            self.assertTrue(
                any(
                    "cannot derive Gate A subject: expected exactly one file for "
                    "ADR-041; found 2" in error
                    for error in subject_errors
                ),
                subject_errors,
            )

    def test_review_schema_accepts_derived_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            self.assertEqual(
                [], review_schema_errors(fixture_root, make_review(fixture_root))
            )

    def test_review_schema_accepts_artifact_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                subjects=[
                    {
                        "subject_type": "artifact",
                        "path": "some/file",
                        "sha256": "a" * 64,
                    }
                ],
            )
            self.assertEqual([], review_schema_errors(fixture_root, record))

    def test_review_schema_rejects_ambiguous_subject_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            mixed = make_review(
                fixture_root,
                subjects=[
                    {
                        "subject_type": "derived",
                        "selector": "gate-a-assurance-decomposition-v1",
                        "path": "formal/verification.yaml",
                        "sha256": "a" * 64,
                    }
                ],
            )
            self.assertTrue(review_schema_errors(fixture_root, mixed))
            untyped = make_review(
                fixture_root,
                subjects=[
                    {
                        "path": "formal/verification.yaml",
                        "selector": "gate-a-assurance-decomposition-v1",
                        "sha256": "a" * 64,
                    }
                ],
            )
            self.assertTrue(review_schema_errors(fixture_root, untyped))

    def test_behavioral_modality_ordering_does_not_change_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, first_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], first_errors)
            manifest["policy"]["behavioral_modalities"] = list(
                reversed(manifest["policy"]["behavioral_modalities"])
            )
            second, second_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], second_errors)
            self.assertEqual(first, second)

    def test_assurance_domain_ordering_does_not_change_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, first_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], first_errors)
            manifest["policy"]["assurance_domains"] = list(
                reversed(manifest["policy"]["assurance_domains"])
            )
            second, second_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], second_errors)
            self.assertEqual(first, second)

    def test_formal_semantic_domain_ordering_does_not_change_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["policy"]["formal_semantic_domains"].append(
                {
                    "id": "secondary",
                    "representation": "tla+",
                    "module": "Secondary",
                    "path": "formal/Secondary.tla",
                    "integrated_semantics_required": True,
                    "focused_analyses_are_restrictions": True,
                }
            )
            first, first_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], first_errors)
            manifest["policy"]["formal_semantic_domains"] = list(
                reversed(manifest["policy"]["formal_semantic_domains"])
            )
            second, second_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], second_errors)
            self.assertEqual(first, second)

    def test_formal_semantic_domain_content_still_changes_subject_after_order_canonicalization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            secondary = {
                "id": "secondary",
                "representation": "tla+",
                "module": "Secondary",
                "path": "formal/Secondary.tla",
                "integrated_semantics_required": True,
                "focused_analyses_are_restrictions": True,
            }
            manifest["policy"]["formal_semantic_domains"].append(secondary)
            first, first_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], first_errors)
            secondary["module"] = "SecondaryChanged"
            second, second_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], second_errors)
            self.assertNotEqual(first["sha256"], second["sha256"])

    def test_all_gate_a_context_collection_reorderings_are_subject_invariant(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["policy"]["formal_semantic_domains"].append(
                {
                    "id": "secondary",
                    "representation": "tla+",
                    "module": "Secondary",
                    "path": "formal/Secondary.tla",
                    "integrated_semantics_required": True,
                    "focused_analyses_are_restrictions": True,
                }
            )
            first, first_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], first_errors)
            manifest["policy"]["formal_semantic_domains"] = list(
                reversed(manifest["policy"]["formal_semantic_domains"])
            )
            manifest["policy"]["behavioral_modalities"] = list(
                reversed(manifest["policy"]["behavioral_modalities"])
            )
            manifest["policy"]["assurance_domains"] = list(
                reversed(manifest["policy"]["assurance_domains"])
            )
            second, second_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], second_errors)
            self.assertEqual(first, second)

    def test_duplicate_formal_semantic_domain_id_prevents_subject_derivation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            original_domain = manifest["policy"]["formal_semantic_domains"][0]
            duplicate_domain = {
                "id": "operational",
                "representation": "tla+",
                "module": "DuplicateTurnlock",
                "path": "formal/DuplicateTurnlock.tla",
                "integrated_semantics_required": True,
                "focused_analyses_are_restrictions": True,
            }
            self.assertNotEqual(original_domain, duplicate_domain)
            manifest["policy"]["formal_semantic_domains"].append(duplicate_domain)
            subject, errors = checker.build_gate_a_review_subject(
                fixture_root,
                manifest,
            )
            self.assertIsNone(subject)
            self.assertIn(
                "cannot derive Gate A subject: duplicate formal semantic domain id 'operational'",
                errors,
            )

    def test_duplicate_formal_semantic_domain_id_fails_repository_integrity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            duplicate_domain = {
                "id": "operational",
                "representation": "tla+",
                "module": "DuplicateTurnlock",
                "path": "formal/DuplicateTurnlock.tla",
                "integrated_semantics_required": True,
                "focused_analyses_are_restrictions": True,
            }
            manifest["policy"]["formal_semantic_domains"].append(duplicate_domain)
            save_manifest(fixture_root, manifest)
            errors, summary = checker.collect_errors(
                fixture_root,
                check_generated=False,
            )
            self.assertIn(
                "cannot derive Gate A subject: duplicate formal semantic domain id 'operational'",
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])


if __name__ == "__main__":
    unittest.main()
