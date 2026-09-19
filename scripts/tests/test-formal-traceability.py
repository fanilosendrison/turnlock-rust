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


def write_review_support_artifact(
    fixture_root: Path, relative_path: str, text: str
) -> dict:
    path = fixture_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return {"path": relative_path, "sha256": checker.sha256_hex(path.read_bytes())}


def write_raw_review_bytes(
    fixture_root: Path, relative_path: str, data: bytes
) -> dict:
    path = fixture_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": relative_path, "sha256": checker.sha256_hex(data)}


def write_gate_a_review_packet(fixture_root: Path) -> dict:
    manifest = load_manifest(fixture_root)
    packet_bytes, errors = checker.build_gate_a_review_packet_bytes(
        fixture_root, manifest
    )
    if errors or packet_bytes is None:
        raise AssertionError(errors or "Gate A review packet build failed")
    return write_raw_review_bytes(
        fixture_root,
        "formal/reviews/packets/packet.json",
        packet_bytes,
    )


def load_review_packet(fixture_root: Path) -> dict:
    return json.loads(
        (fixture_root / "formal/reviews/packets/packet.json").read_text(
            encoding="utf-8"
        )
    )


def replace_review_packet_bytes(
    fixture_root: Path, record: dict, packet_bytes: bytes
) -> dict:
    packet_reference = write_raw_review_bytes(
        fixture_root,
        "formal/reviews/packets/packet.json",
        packet_bytes,
    )
    record["protocol"]["review_packet"] = packet_reference
    for item in record["executions"]:
        item["review_packet_sha256"] = packet_reference["sha256"]
    return packet_reference


def replace_review_packet(
    fixture_root: Path, record: dict, packet_payload: dict
) -> dict:
    return replace_review_packet_bytes(
        fixture_root,
        record,
        checker._canonical_json_document_bytes(packet_payload),
    )


def default_model_identity(execution_id: str) -> tuple[str, str, str]:
    suffix = execution_id.removeprefix("EXEC-").lower() or "exec"
    return f"provider-{suffix}", f"model-{suffix}", "1"


def execution(
    fixture_root: Path,
    execution_id: str,
    *,
    packet: dict,
    prompt: dict,
    provider: str | None = None,
    model: str | None = None,
    model_version: str | None = None,
    attack_objectives: list[str] | None = None,
    raw_output: dict | None = None,
    raw_finding_ids: list[str] | None = None,
    review_packet_sha256: str | None = None,
    prompt_sha256: str | None = None,
    isolated_context: bool = True,
    cross_reviewer_visibility_before_seal: bool = False,
) -> dict:
    identity_provider, identity_model, identity_version = default_model_identity(
        execution_id
    )
    if raw_output is None:
        slug = execution_id.removeprefix("EXEC-").lower() or "exec"
        raw_output = write_review_support_artifact(
            fixture_root,
            f"formal/reviews/raw/{slug}.md",
            f"# Sealed raw output for {execution_id}\n",
        )
    return {
        "execution_id": execution_id,
        "reviewer_type": "frontier-llm",
        "provider": provider if provider is not None else identity_provider,
        "model": model if model is not None else identity_model,
        "model_version": (
            model_version if model_version is not None else identity_version
        ),
        "review_packet_sha256": (
            review_packet_sha256
            if review_packet_sha256 is not None
            else packet["sha256"]
        ),
        "prompt_sha256": (
            prompt_sha256 if prompt_sha256 is not None else prompt["sha256"]
        ),
        "isolated_context": isolated_context,
        "cross_reviewer_visibility_before_seal": cross_reviewer_visibility_before_seal,
        "attack_objectives": (
            list(attack_objectives)
            if attack_objectives is not None
            else list(GATE_A_ATTACK_OBJECTIVES)
        ),
        "raw_output": raw_output,
        "raw_finding_ids": (
            list(raw_finding_ids) if raw_finding_ids is not None else []
        ),
    }


def make_review(
    fixture_root: Path,
    *,
    review_id: str = "REVIEW-0001",
    review_class: str = "assurance-decomposition",
    subjects: list[dict] | None = None,
    protocol: dict | None = None,
    executions: list[dict] | None = None,
    findings: list[dict] | None = None,
) -> dict:
    if subjects is None:
        subject, errors = checker.build_gate_a_review_subject(
            fixture_root, load_manifest(fixture_root)
        )
        if errors or subject is None:
            raise AssertionError(errors or "Gate A subject derivation failed")
        subjects = [subject]
    if protocol is None:
        protocol = {
            "review_packet": write_gate_a_review_packet(fixture_root),
            "prompt": write_review_support_artifact(
                fixture_root,
                "formal/reviews/prompts/prompt.md",
                "# Canonical review prompt\n",
            ),
        }
    if executions is None:
        executions = [
            execution(
                fixture_root,
                "EXEC-A",
                packet=protocol["review_packet"],
                prompt=protocol["prompt"],
            ),
            execution(
                fixture_root,
                "EXEC-B",
                packet=protocol["review_packet"],
                prompt=protocol["prompt"],
            ),
        ]
    records = list(findings) if findings is not None else []
    for finding_record in records:
        for source in finding_record.get("sources", []):
            for execution_record in executions:
                if execution_record["execution_id"] != source["execution_id"]:
                    continue
                if source["raw_finding_id"] not in execution_record["raw_finding_ids"]:
                    execution_record["raw_finding_ids"].append(
                        source["raw_finding_id"]
                    )
    return {
        "schema_version": "3.0",
        "review_id": review_id,
        "review_class": review_class,
        "repository_commit": "6d3c9851e0d66286280f8e49ebd8ed44da13d876",
        "subjects": subjects,
        "protocol": protocol,
        "executions": executions,
        "findings": records,
        "supersedes_review_ids": [],
        "started_at": "2026-09-19T00:00:00Z",
        "completed_at": "2026-09-19T01:00:00Z",
    }


def materiality(**overrides) -> dict:
    data = {axis: False for axis in checker.MATERIALITY_AXES}
    data["rationale"] = (
        "Assuming the finding is true, it could change the Gate A subject while "
        "still authorizing the candidate model."
    )
    data.update(overrides)
    return data


def finding(
    *,
    finding_id: str = "F-1",
    sources: list[dict] | None = None,
    statement: str = "A material semantic objection.",
    argument: str = "The objection survives review.",
    counterexample=None,
    material: bool = True,
    status: str = "open",
    disposition=None,
) -> dict:
    return {
        "finding_id": finding_id,
        "sources": (
            sources
            if sources is not None
            else [{"execution_id": "EXEC-A", "raw_finding_id": "EXEC-A-F001"}]
        ),
        "statement": statement,
        "argument": argument,
        "counterexample": counterexample,
        "materiality": (
            materiality(authority_or_upstream_decision=True)
            if material
            else materiality()
        ),
        "status": status,
        "disposition": disposition,
    }


def routed_disposition(**overrides) -> dict:
    data = {
        "kind": "routed",
        "classification": "product-semantics-decision-required",
        "reference": "Issue #27",
        "rationale": "The earliest upstream cause requires a separate decision.",
    }
    data.update(overrides)
    return data


def resolved_disposition(**overrides) -> dict:
    data = {
        "kind": "resolved",
        "resolution_commit": "0" * 40,
        "rationale": "The cause was corrected.",
    }
    data.update(overrides)
    return data


def counterexample_disposition(**overrides) -> dict:
    data = {
        "outcome": "non-concluding",
        "rationale": "The counterexample does not establish the claimed defect.",
    }
    data.update(overrides)
    return data


def challenge_artifact(fixture_root: Path, finding: dict, **overrides) -> dict:
    data = {
        "challenger_execution_id": "EXEC-B",
        "challenged_refutation_sha256": (
            checker._refutation_challenge_subject_sha256(finding)
        ),
        "output": write_review_support_artifact(
            fixture_root,
            "formal/reviews/challenges/challenge-1.md",
            "# Hostile challenge of a material refutation\n",
        ),
        "surviving_material_argument": False,
        "rationale": "No valid material argument or counterexample survives.",
    }
    data.update(overrides)
    return data


def attach_challenge(fixture_root: Path, finding: dict, **overrides) -> dict:
    if not isinstance(finding.get("disposition"), dict):
        raise AssertionError("attaching a challenge requires a refuted disposition")
    finding["disposition"]["challenge"] = challenge_artifact(
        fixture_root, finding, **overrides
    )
    return finding


def refuted_disposition(**overrides) -> dict:
    data = {
        "kind": "refuted",
        "ground": "premise-false",
        "attacked_premise_or_inference": "The finding assumes an invalid premise.",
        "evidence_references": ["docs/specification/turnlock-spec.md"],
        "argument": "The premise is false under the exact reviewed authority.",
        "counterexample_disposition": None,
        "challenge": None,
    }
    data.update(overrides)
    return data


def legacy_v1_1_review(fixture_root: Path) -> dict:
    subject, errors = checker.build_gate_a_review_subject(
        fixture_root, load_manifest(fixture_root)
    )
    if errors or subject is None:
        raise AssertionError(errors or "Gate A subject derivation failed")
    reviewer = {
        "reviewer_id": "r1",
        "reviewer_type": "frontier-llm",
        "provider": "provider",
        "model": "model",
        "model_version": "1",
        "prompt_sha256": "a" * 64,
    }
    return {
        "schema_version": "1.1",
        "review_id": "REVIEW-LEGACY",
        "review_class": "assurance-decomposition",
        "repository_commit": "6d3c9851e0d66286280f8e49ebd8ed44da13d876",
        "subjects": [subject],
        "attack_objectives": list(GATE_A_ATTACK_OBJECTIVES),
        "reviewers": [reviewer, dict(reviewer, reviewer_id="r2")],
        "findings": [],
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


def review_challenge_schema_errors(fixture_root: Path, challenge: dict) -> list:
    schema = json.loads(
        (
            fixture_root / "formal" / "reviews" / "review-evidence.schema.json"
        ).read_text(encoding="utf-8")
    )
    wrapper = {"$defs": schema.get("$defs", {}), "$ref": "#/$defs/challenge"}
    return list(Draft202012Validator(wrapper).iter_errors(challenge))


def fake_gate_a_subject() -> tuple[dict, dict]:
    fake_subject_payload = {
        "subject_schema_version": 1,
        "selector": checker.GATE_A_SUBJECT_SELECTOR,
        "authority": {},
    }
    fake_subject = {
        "subject_type": "derived",
        "selector": checker.GATE_A_SUBJECT_SELECTOR,
        "sha256": checker.sha256_hex(
            checker._canonical_json_bytes(fake_subject_payload)
        ),
    }
    return fake_subject_payload, fake_subject


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

    def test_review_schema_v3_accepts_valid_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            self.assertEqual(
                [], review_schema_errors(fixture_root, make_review(fixture_root))
            )

    def test_review_schema_rejects_v2_0_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            legacy = make_review(fixture_root)
            legacy["schema_version"] = "2.0"
            self.assertTrue(review_schema_errors(fixture_root, legacy))
            write_review(fixture_root, legacy, name="REVIEW-LEGACY-V2.yaml")
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_review_schema_rejects_v1_1_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            legacy = legacy_v1_1_review(fixture_root)
            self.assertTrue(review_schema_errors(fixture_root, legacy))
            write_review(fixture_root, legacy, name="REVIEW-LEGACY.yaml")
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_review_evidence_with_fewer_than_two_executions_fails_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["executions"] = record["executions"][:1]
            write_review(fixture_root, record)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            joined = "\n".join(errors)
            self.assertIn("formal/reviews/REVIEW-0001.yaml", joined)
            self.assertIn("schema", joined)

    def test_duplicate_execution_ids_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            protocol = record["protocol"]
            duplicate_raw = write_review_support_artifact(
                fixture_root,
                "formal/reviews/raw/exec-a-duplicate.md",
                "# Duplicate execution identifier raw output\n",
            )
            record["executions"][1] = execution(
                fixture_root,
                "EXEC-A",
                packet=protocol["review_packet"],
                prompt=protocol["prompt"],
                raw_output=duplicate_raw,
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("execution_id values must be unique" in error for error in errors),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_same_model_identity_twice_counts_as_one_independent_reviewer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            for item in record["executions"]:
                item["provider"] = "provider"
                item["model"] = "model"
                item["model_version"] = "1"
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertIn("operational independence", summary["gate_a"]["reason"])

    def test_same_provider_distinct_model_identities_can_satisfy_independence(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["executions"][0].update(
                {"provider": "provider", "model": "model-a", "model_version": "1"}
            )
            record["executions"][1].update(
                {"provider": "provider", "model": "model-b", "model_version": "1"}
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_distinct_provider_and_model_identities_can_satisfy_independence(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            self.assertNotEqual(
                (
                    record["executions"][0]["provider"],
                    record["executions"][0]["model"],
                    record["executions"][0]["model_version"],
                ),
                (
                    record["executions"][1]["provider"],
                    record["executions"][1]["model"],
                    record["executions"][1]["model_version"],
                ),
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_gate_a_review_packet_builder_contains_exact_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            packet_bytes, errors = checker.build_gate_a_review_packet_bytes(
                fixture_root, manifest
            )
            self.assertEqual([], errors)
            self.assertIsNotNone(packet_bytes)
            packet = json.loads(packet_bytes.decode("utf-8"))
            subject, subject_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], subject_errors)
            self.assertEqual(subject, packet["subject"])
            self.assertEqual("derived", packet["subject"]["subject_type"])
            self.assertEqual(
                checker.GATE_A_SUBJECT_SELECTOR, packet["subject"]["selector"]
            )
            self.assertEqual(
                subject["sha256"],
                checker.sha256_hex(
                    checker._canonical_json_bytes(packet["subject_payload"])
                ),
            )

    def test_gate_a_review_packet_builder_embeds_exact_authority_contents(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            packet_bytes, errors = checker.build_gate_a_review_packet_bytes(
                fixture_root, load_manifest(fixture_root)
            )
            self.assertEqual([], errors)
            packet = json.loads(packet_bytes.decode("utf-8"))
            authority = packet["subject_payload"]["authority"]
            expected_metadata = [
                {
                    "role": "normative-spec",
                    "id": None,
                    "path": authority["normative_spec"]["path"],
                    "sha256": authority["normative_spec"]["sha256"],
                }
            ]
            for relation, role in (
                ("architecture_decisions", "architecture-decision"),
                ("abstraction_constraints", "abstraction-constraint"),
            ):
                descriptors = sorted(
                    authority[relation], key=lambda descriptor: descriptor["id"]
                )
                for descriptor in descriptors:
                    expected_metadata.append(
                        {
                            "role": role,
                            "id": descriptor["id"],
                            "path": descriptor["path"],
                            "sha256": descriptor["sha256"],
                        }
                    )
            self.assertEqual(
                expected_metadata,
                [
                    {
                        "role": entry["role"],
                        "id": entry["id"],
                        "path": entry["path"],
                        "sha256": entry["sha256"],
                    }
                    for entry in packet["authority_contents"]
                ],
            )
            self.assertEqual(
                [None, "ADR-015", "ADR-041", "ADR-040"],
                [entry["id"] for entry in packet["authority_contents"]],
            )
            for entry in packet["authority_contents"]:
                data = (fixture_root / entry["path"]).read_bytes()
                self.assertEqual(entry["sha256"], checker.sha256_hex(data))
                self.assertEqual(entry["content_utf8"].encode("utf-8"), data)

    def test_gate_a_review_packet_bytes_are_canonical_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            packet_bytes, errors = checker.build_gate_a_review_packet_bytes(
                fixture_root, load_manifest(fixture_root)
            )
            self.assertEqual([], errors)
            self.assertTrue(packet_bytes.endswith(b"\n"))
            parsed = json.loads(packet_bytes.decode("utf-8"))
            self.assertEqual(
                packet_bytes, checker._canonical_json_document_bytes(parsed)
            )
            self.assertNotEqual(packet_bytes, checker._canonical_json_bytes(parsed))

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
            self.assertEqual(
                "surviving material hostile-review finding exists",
                summary["gate_a"]["reason"],
            )

    def test_material_routed_finding_prevents_review_from_satisfying_gate_a(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    findings=[
                        finding(status="routed", disposition=routed_disposition())
                    ],
                ),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "surviving material hostile-review finding exists",
                summary["gate_a"]["reason"],
            )

    def test_current_review_with_material_resolved_finding_blocks_gate_a(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    findings=[
                        finding(
                            material=True,
                            status="resolved",
                            disposition=resolved_disposition(),
                        )
                    ],
                ),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "surviving material hostile-review finding exists",
                summary["gate_a"]["reason"],
            )

    def test_current_review_with_non_material_resolved_finding_can_satisfy_gate_a(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    findings=[
                        finding(
                            material=False,
                            status="resolved",
                            disposition=resolved_disposition(),
                        )
                    ],
                ),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_majority_reviewer_count_cannot_override_surviving_open_finding(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root, findings=[finding(status="open")])
            protocol = record["protocol"]
            record["executions"].append(
                execution(
                    fixture_root,
                    "EXEC-C",
                    packet=protocol["review_packet"],
                    prompt=protocol["prompt"],
                )
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "surviving material hostile-review finding exists",
                summary["gate_a"]["reason"],
            )

    def test_incomplete_campaign_objective_set_does_not_satisfy_gate_a(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            objectives = [
                objective
                for objective in GATE_A_ATTACK_OBJECTIVES
                if objective != "vacuity"
            ]
            for item in record["executions"]:
                item["attack_objectives"] = list(objectives)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertIn("per-execution attack coverage", summary["gate_a"]["reason"])

    def test_missing_required_objective_from_one_execution_blocks_gate_a(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["executions"][0]["attack_objectives"] = [
                objective
                for objective in GATE_A_ATTACK_OBJECTIVES
                if objective != "vacuity"
            ]
            self.assertEqual(
                list(GATE_A_ATTACK_OBJECTIVES),
                record["executions"][1]["attack_objectives"],
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertIn("per-execution attack coverage", summary["gate_a"]["reason"])

    def test_complete_required_objectives_on_each_execution_can_satisfy_gate_a(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            self.assertEqual(
                "formal/reviews/packets/packet.json",
                record["protocol"]["review_packet"]["path"],
            )
            for item in record["executions"]:
                self.assertEqual(
                    list(GATE_A_ATTACK_OBJECTIVES), item["attack_objectives"]
                )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])
            self.assertIn("per-execution attack coverage", summary["gate_a"]["reason"])

    def test_execution_packet_hash_must_match_campaign_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["executions"][0]["review_packet_sha256"] = "0" * 64
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("review_packet_sha256" in error for error in errors), errors
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_execution_prompt_hash_must_match_campaign_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["executions"][0]["prompt_sha256"] = "0" * 64
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(any("prompt_sha256" in error for error in errors), errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_trivial_gate_a_review_packet_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            replace_review_packet_bytes(
                fixture_root,
                record,
                checker._canonical_json_document_bytes({"packet_schema_version": 1}),
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("Gate A review packet" in error for error in errors), errors
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_gate_a_review_packet_subject_hash_mismatch_is_integrity_failure(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            packet = load_review_packet(fixture_root)
            packet["subject"]["sha256"] = "0" * 64
            replace_review_packet(fixture_root, record, packet)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "subject sha256 does not match subject_payload" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_gate_a_review_packet_missing_authority_content_is_integrity_failure(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            packet = load_review_packet(fixture_root)
            packet["authority_contents"] = packet["authority_contents"][:-1]
            replace_review_packet(fixture_root, record, packet)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "authority contents do not match subject authority" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_gate_a_review_packet_extra_authority_content_is_integrity_failure(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            packet = load_review_packet(fixture_root)
            extra = dict(packet["authority_contents"][-1])
            extra["id"] = "ADR-999"
            extra["path"] = "docs/adr/adr-999-fixture.md"
            packet["authority_contents"].append(extra)
            replace_review_packet(fixture_root, record, packet)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "authority contents do not match subject authority" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_gate_a_review_packet_authority_content_hash_mismatch_is_integrity_failure(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            packet = load_review_packet(fixture_root)
            packet["authority_contents"][0]["content_utf8"] += (
                "\n<!-- tampered embedded authority -->\n"
            )
            replace_review_packet(fixture_root, record, packet)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "authority content sha256 mismatch" in error for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_noncanonical_gate_a_review_packet_serialization_is_integrity_failure(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            packet = load_review_packet(fixture_root)
            noncanonical = json.dumps(packet, indent=2).encode("utf-8")
            replace_review_packet_bytes(fixture_root, record, noncanonical)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertFalse(
                any("artifact sha256 does not match" in error for error in errors),
                errors,
            )
            self.assertTrue(
                any(
                    "canonical JSON serialization" in error for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_stale_gate_a_review_packet_remains_self_validating_after_subject_change(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(fixture_root, make_review(fixture_root))
            manifest = load_manifest(fixture_root)
            manifest["claims"][0]["statement"] += " (fixture subject change)"
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

    def test_multi_gate_a_subject_confusion_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            current_subject, subject_errors = checker.build_gate_a_review_subject(
                fixture_root,
                load_manifest(fixture_root),
            )
            self.assertEqual([], subject_errors)
            self.assertIsNotNone(current_subject)
            fake_subject_payload, fake_subject = fake_gate_a_subject()
            self.assertNotEqual(fake_subject, current_subject)
            fake_packet = {
                "packet_schema_version": 1,
                "subject": fake_subject,
                "subject_payload": fake_subject_payload,
                "authority_contents": [],
            }
            fake_packet_bytes = checker._canonical_json_document_bytes(fake_packet)
            record["protocol"]["review_packet"] = write_raw_review_bytes(
                fixture_root,
                "formal/reviews/packets/packet.json",
                fake_packet_bytes,
            )
            for item in record["executions"]:
                item["review_packet_sha256"] = record["protocol"]["review_packet"][
                    "sha256"
                ]
            record["subjects"] = [current_subject, fake_subject]
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root,
                check_generated=False,
            )
            self.assertTrue(errors)
            self.assertTrue(
                any(
                    "must declare exactly one Gate A derived subject" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_duplicate_gate_a_derived_subject_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            current_subject, subject_errors = checker.build_gate_a_review_subject(
                fixture_root,
                load_manifest(fixture_root),
            )
            self.assertEqual([], subject_errors)
            self.assertIsNotNone(current_subject)
            record["subjects"] = [current_subject, dict(current_subject)]
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root,
                check_generated=False,
            )
            self.assertTrue(errors)
            self.assertTrue(
                any(
                    "must declare exactly one Gate A derived subject" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_gate_a_packet_must_equal_unique_declared_gate_a_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            _fake_payload, fake_subject = fake_gate_a_subject()
            record["subjects"] = [fake_subject]
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root,
                check_generated=False,
            )
            self.assertTrue(
                any(
                    "does not equal the review record's unique Gate A derived "
                    "subject" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_single_gate_a_subject_with_additional_artifact_subject_can_satisfy_gate_a(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            current_subject, subject_errors = checker.build_gate_a_review_subject(
                fixture_root,
                load_manifest(fixture_root),
            )
            self.assertEqual([], subject_errors)
            self.assertIsNotNone(current_subject)
            artifact_subject = {
                "subject_type": "artifact",
                "path": "formal/verification.yaml",
                "sha256": checker.sha256_hex(
                    (fixture_root / "formal/verification.yaml").read_bytes()
                ),
            }
            record["subjects"] = [current_subject, artifact_subject]
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root,
                check_generated=False,
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_derive_gate_a_does_not_count_multi_gate_a_subject_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            record = make_review(fixture_root)
            current_subject, subject_errors = checker.build_gate_a_review_subject(
                fixture_root,
                manifest,
            )
            self.assertEqual([], subject_errors)
            self.assertIsNotNone(current_subject)
            _fake_payload, fake_subject = fake_gate_a_subject()
            record["subjects"] = [current_subject, fake_subject]
            summary = checker.derive_gate_a(
                manifest,
                current_subject,
                [(Path("formal/reviews/REVIEW-CONFUSED.yaml"), record)],
            )
            self.assertFalse(summary["ready"])
            self.assertEqual(
                "hostile assurance-decomposition review evidence required",
                summary["reason"],
            )

    def test_missing_review_packet_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["protocol"]["review_packet"]["path"] = (
                "formal/reviews/packets/missing.json"
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("protocol.review_packet: artifact does not exist" in error for error in errors),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_review_packet_hash_mismatch_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["protocol"]["review_packet"]["sha256"] = "0" * 64
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "protocol.review_packet: artifact sha256 does not match" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_missing_prompt_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["protocol"]["prompt"]["path"] = "formal/reviews/prompts/missing.md"
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("protocol.prompt: artifact does not exist" in error for error in errors),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_prompt_hash_mismatch_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["protocol"]["prompt"]["sha256"] = "0" * 64
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "protocol.prompt: artifact sha256 does not match" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_missing_raw_output_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["executions"][0]["raw_output"]["path"] = (
                "formal/reviews/raw/missing.md"
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("raw_output: artifact does not exist" in error for error in errors),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_raw_output_hash_mismatch_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["executions"][0]["raw_output"]["sha256"] = "0" * 64
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "raw_output: artifact sha256 does not match" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_duplicate_raw_output_path_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["executions"][1]["raw_output"] = dict(
                record["executions"][0]["raw_output"]
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("duplicate raw_output path" in error for error in errors), errors
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_unknown_finding_source_execution_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["findings"] = [
                finding(
                    sources=[
                        {"execution_id": "EXEC-Z", "raw_finding_id": "EXEC-Z-F001"}
                    ]
                )
            ]
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "references unknown execution 'EXEC-Z'" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_unknown_raw_finding_source_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root, findings=[finding()])
            record["findings"][0]["sources"] = [
                {"execution_id": "EXEC-A", "raw_finding_id": "EXEC-A-F999"}
            ]
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "references unknown raw finding 'EXEC-A-F999'" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_declared_raw_finding_without_normalized_destination_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["executions"][0]["raw_finding_ids"] = ["EXEC-A-F001"]
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("has no normalized destination" in error for error in errors),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_raw_finding_cannot_map_to_two_normalized_findings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            source = {"execution_id": "EXEC-A", "raw_finding_id": "EXEC-A-F001"}
            record = make_review(
                fixture_root,
                findings=[
                    finding(finding_id="F-1", sources=[dict(source)]),
                    finding(finding_id="F-2", sources=[dict(source)]),
                ],
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "maps to multiple normalized findings" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_multiple_raw_findings_can_merge_into_one_normalized_finding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[
                    finding(
                        sources=[
                            {"execution_id": "EXEC-A", "raw_finding_id": "EXEC-A-F001"},
                            {"execution_id": "EXEC-A", "raw_finding_id": "EXEC-A-F002"},
                        ],
                        material=False,
                        status="open",
                    )
                ],
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_duplicate_normalized_finding_ids_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[
                    finding(
                        finding_id="F-1",
                        sources=[
                            {"execution_id": "EXEC-A", "raw_finding_id": "EXEC-A-F001"}
                        ],
                        material=False,
                    ),
                    finding(
                        finding_id="F-1",
                        sources=[
                            {"execution_id": "EXEC-B", "raw_finding_id": "EXEC-B-F001"}
                        ],
                        material=False,
                    ),
                ],
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "normalized finding_id values must be unique" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_all_false_materiality_axes_derives_non_material(self) -> None:
        self.assertFalse(
            checker._finding_is_material({"materiality": materiality()})
        )

    def test_any_true_materiality_axis_derives_material(self) -> None:
        for axis in checker.MATERIALITY_AXES:
            with self.subTest(axis=axis):
                payload = {"materiality": materiality(**{axis: True})}
                self.assertTrue(checker._finding_is_material(payload))

    def test_manifest_reviewer_minimum_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["policy"]["hostile_review"]["minimum_independent_reviewers"] = 3
            save_manifest(fixture_root, manifest)
            record = make_review(fixture_root)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])

            protocol = record["protocol"]
            record["executions"].append(
                execution(
                    fixture_root,
                    "EXEC-C",
                    packet=protocol["review_packet"],
                    prompt=protocol["prompt"],
                )
            )
            write_review(fixture_root, record)
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
                "surviving material hostile-review finding exists",
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
                    findings=[
                        finding(status="routed", disposition=routed_disposition())
                    ],
                ),
                name="REVIEW-B.yaml",
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "surviving material hostile-review finding exists",
                summary["gate_a"]["reason"],
            )

    def test_clean_review_cannot_override_another_current_resolved_finding(
        self,
    ) -> None:
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
                    findings=[
                        finding(
                            status="resolved",
                            disposition=resolved_disposition(),
                        )
                    ],
                ),
                name="REVIEW-B.yaml",
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "surviving material hostile-review finding exists",
                summary["gate_a"]["reason"],
            )

    def test_refuted_finding_requires_structured_refutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    findings=[finding(status="refuted", disposition=None)],
                ),
            )
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            joined = "\n".join(errors)
            self.assertIn("schema", joined)
            self.assertIn("disposition", joined)

    def test_refuted_counterexample_requires_counterexample_disposition(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            finding_record = finding(
                counterexample="A concrete counterexample trace.",
                status="refuted",
                disposition=refuted_disposition(counterexample_disposition=None),
            )
            attach_challenge(fixture_root, finding_record)
            write_review(
                fixture_root,
                make_review(fixture_root, findings=[finding_record]),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "requires counterexample_disposition" in error for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_material_refuted_finding_requires_challenge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    findings=[
                        finding(
                            material=True,
                            status="refuted",
                            disposition=refuted_disposition(
                                counterexample_disposition=counterexample_disposition(),
                                challenge=None,
                            ),
                        )
                    ],
                ),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("requires a challenge artifact" in error for error in errors),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_refutation_challenge_execution_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            finding_record = finding(
                status="refuted",
                disposition=refuted_disposition(),
            )
            attach_challenge(
                fixture_root,
                finding_record,
                challenger_execution_id="EXEC-Z",
            )
            write_review(
                fixture_root,
                make_review(fixture_root, findings=[finding_record]),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "challenge references unknown execution 'EXEC-Z'" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_missing_challenge_output_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            finding_record = finding(
                status="refuted",
                disposition=refuted_disposition(),
            )
            attach_challenge(
                fixture_root,
                finding_record,
                output={
                    "path": "formal/reviews/challenges/missing.md",
                    "sha256": "a" * 64,
                },
            )
            write_review(
                fixture_root,
                make_review(fixture_root, findings=[finding_record]),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "challenge output: artifact does not exist" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_challenge_output_hash_mismatch_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            finding_record = finding(
                status="refuted",
                disposition=refuted_disposition(),
            )
            attach_challenge(fixture_root, finding_record)
            finding_record["disposition"]["challenge"]["output"]["sha256"] = "0" * 64
            write_review(
                fixture_root,
                make_review(fixture_root, findings=[finding_record]),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "challenge output: artifact sha256 does not match" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_valid_material_refutation_with_valid_challenge_can_cease_blocking(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            finding_record = finding(
                counterexample="A concrete counterexample trace.",
                status="refuted",
                disposition=refuted_disposition(
                    counterexample_disposition=counterexample_disposition(),
                ),
            )
            attach_challenge(fixture_root, finding_record)
            write_review(
                fixture_root,
                make_review(fixture_root, findings=[finding_record]),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_material_refutation_challenge_requires_challenged_refutation_sha256(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            finding_record = finding(
                status="refuted",
                disposition=refuted_disposition(),
            )
            attach_challenge(fixture_root, finding_record)
            challenge = finding_record["disposition"]["challenge"]
            del challenge["challenged_refutation_sha256"]
            schema_errors = review_challenge_schema_errors(fixture_root, challenge)
            self.assertTrue(schema_errors)
            self.assertTrue(
                any(
                    "challenged_refutation_sha256" in error.message
                    for error in schema_errors
                ),
                schema_errors,
            )
            record = make_review(fixture_root, findings=[finding_record])
            self.assertTrue(review_schema_errors(fixture_root, record))
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_challenge_refutation_hash_mismatch_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            finding_record = finding(
                status="refuted",
                disposition=refuted_disposition(),
            )
            attach_challenge(fixture_root, finding_record)
            finding_record["disposition"]["challenge"][
                "challenged_refutation_sha256"
            ] = "0" * 64
            write_review(
                fixture_root,
                make_review(fixture_root, findings=[finding_record]),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "challenge does not bind the exact refutation" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_changing_refutation_after_challenge_invalidates_challenge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            finding_record = finding(
                status="refuted",
                disposition=refuted_disposition(),
            )
            attach_challenge(fixture_root, finding_record)
            finding_record["disposition"]["argument"] = (
                "The refutation argument was rewritten after the challenge was sealed."
            )
            write_review(
                fixture_root,
                make_review(fixture_root, findings=[finding_record]),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "challenge does not bind the exact refutation" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_refutation_challenge_hash_is_invariant_to_source_and_evidence_reference_order(
        self,
    ) -> None:
        sources = [
            {"execution_id": "EXEC-A", "raw_finding_id": "EXEC-A-F001"},
            {"execution_id": "EXEC-B", "raw_finding_id": "EXEC-B-F001"},
        ]
        finding_a = finding(
            sources=list(sources),
            status="refuted",
            disposition=refuted_disposition(evidence_references=["b.md", "a.md"]),
        )
        finding_b = finding(
            sources=list(reversed(sources)),
            status="refuted",
            disposition=refuted_disposition(evidence_references=["a.md", "b.md"]),
        )
        self.assertEqual(
            checker._refutation_challenge_subject_sha256(finding_a),
            checker._refutation_challenge_subject_sha256(finding_b),
        )
        payload = checker._refutation_challenge_subject_payload(finding_b)
        self.assertEqual(
            ["a.md", "b.md"], payload["finding"]["refutation"]["evidence_references"]
        )
        self.assertEqual(
            ["EXEC-A", "EXEC-B"],
            [source["execution_id"] for source in payload["finding"]["sources"]],
        )

    def test_non_material_refutation_with_supplied_invalid_challenge_is_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            finding_record = finding(
                material=False,
                status="refuted",
                disposition=refuted_disposition(),
            )
            attach_challenge(
                fixture_root,
                finding_record,
                output={
                    "path": "formal/reviews/challenges/missing.md",
                    "sha256": "a" * 64,
                },
            )
            write_review(
                fixture_root,
                make_review(fixture_root, findings=[finding_record]),
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "challenge output: artifact does not exist" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_review_artifact_final_symlink_is_integrity_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            raw_path = fixture_root / record["executions"][0]["raw_output"]["path"]
            target = raw_path.with_name("a-real.md")
            target.write_bytes(raw_path.read_bytes())
            raw_path.unlink()
            try:
                raw_path.symlink_to(target.name)
            except OSError as error:
                self.skipTest(f"cannot create symlink: {error}")
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "artifact path must not traverse symlinks" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_review_artifact_parent_directory_symlink_is_integrity_failure(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            raw_directory = fixture_root / "formal/reviews/raw"
            alternate = fixture_root / "formal/reviews/alternate-raw"
            alternate.mkdir()
            for path in sorted(raw_directory.iterdir()):
                (alternate / path.name).write_bytes(path.read_bytes())
                path.unlink()
            raw_directory.rmdir()
            try:
                raw_directory.symlink_to(alternate.name)
            except OSError as error:
                self.skipTest(f"cannot create symlink: {error}")
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "artifact path must not traverse symlinks" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_invalid_review_evidence_cannot_report_gate_a_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["protocol"]["review_packet"]["sha256"] = "0" * 64
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

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
