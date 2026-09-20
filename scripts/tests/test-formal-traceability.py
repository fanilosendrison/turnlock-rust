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


PROTOCOL_BUNDLE_RELATIVE = "formal/reviews/protocols/gate-a-campaign-protocol-v2.json"

SUPPORTING_PROFILE_DEFAULTS = {
    "profile-challenge": ("provider-challenge", "model-challenge"),
    "profile-materiality-assessor": ("provider-materiality", "model-materiality"),
    "profile-adjudicator": ("provider-adjudicator", "model-adjudicator"),
}


def write_review_support_artifact(
    fixture_root: Path, relative_path: str, text: str
) -> dict:
    path = fixture_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return {"path": relative_path, "sha256": checker.sha256_hex(path.read_bytes())}


def write_bytes_artifact(fixture_root: Path, relative_path: str, data: bytes) -> dict:
    path = fixture_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": relative_path, "sha256": checker.sha256_hex(data)}


def write_json_artifact(
    fixture_root: Path, relative_path: str, payload: dict, *, canonical: bool = True
) -> dict:
    if canonical:
        data = checker._canonical_json_document_bytes(payload)
    else:
        data = json.dumps(payload).encode("utf-8")
    return write_bytes_artifact(fixture_root, relative_path, data)


def write_raw_review_bytes(
    fixture_root: Path, relative_path: str, data: bytes
) -> dict:
    return write_bytes_artifact(fixture_root, relative_path, data)


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


def current_protocol_bundle_reference(fixture_root: Path) -> dict:
    manifest = load_manifest(fixture_root)
    return manifest["policy"]["hostile_review"]["current_protocol_bundle"]


def bundle_document(fixture_root: Path) -> dict:
    reference = current_protocol_bundle_reference(fixture_root)
    return json.loads(
        (fixture_root / reference["path"]).read_text(encoding="utf-8")
    )


def install_protocol_bundle(
    fixture_root: Path, profiles: list[dict]
) -> tuple[dict, dict]:
    payload = bundle_document(fixture_root)
    existing: dict[str, dict] = {}
    for profile in payload.get("reviewer_profiles", []):
        if isinstance(profile, dict) and isinstance(profile.get("profile_id"), str):
            existing[profile["profile_id"]] = profile
    for profile in profiles:
        existing[profile["profile_id"]] = profile
    payload["reviewer_profiles"] = [existing[key] for key in sorted(existing)]
    data = checker._canonical_json_document_bytes(payload)
    sha256 = checker.sha256_hex(data)
    path = fixture_root / PROTOCOL_BUNDLE_RELATIVE
    current = current_protocol_bundle_reference(fixture_root)
    if isinstance(current.get("sha256"), str) and current.get("sha256") == sha256:
        reference = {"path": current["path"], "sha256": sha256}
    else:
        derived = (
            "formal/reviews/protocols/"
            f"gate-a-campaign-protocol-v2-{sha256[:16]}.json"
        )
        path = fixture_root / derived
        path.write_bytes(data)
        reference = {"path": derived, "sha256": sha256}
    manifest = load_manifest(fixture_root)
    manifest["policy"]["hostile_review"]["current_protocol_bundle"] = reference
    save_manifest(fixture_root, manifest)
    return payload, reference


def supporting_profile(profile_id: str) -> dict:
    provider, model = SUPPORTING_PROFILE_DEFAULTS[profile_id]
    return {
        "profile_id": profile_id,
        "provider": provider,
        "request_model": model,
        "frontier_eligible": True,
        "identity_resolution": {"kind": "provider-reported"},
    }


def default_profile(
    execution_id: str,
    provider: str | None = None,
    model: str | None = None,
    *,
    kind: str = "provider-reported",
    frontier_eligible: bool = True,
    immutable: bool | None = None,
) -> dict:
    provider_default, model_default, _ = default_model_identity(execution_id)
    resolution: dict = {"kind": kind}
    if immutable is not None:
        resolution["request_model_is_immutable_version"] = immutable
    return {
        "profile_id": f"profile-{execution_id.removeprefix('EXEC-').lower()}",
        "provider": provider if provider is not None else provider_default,
        "request_model": model if model is not None else model_default,
        "frontier_eligible": frontier_eligible,
        "identity_resolution": resolution,
    }


def raw_finding(
    raw_finding_id: str,
    *,
    attack_objectives: list[str] | None = None,
    affected_claims: list[str] | None = None,
    affected_invariants: list[str] | None = None,
    affected_coverage_entries: list[str] | None = None,
    evidence_references: list[str] | None = None,
    statement: str = "A material semantic objection.",
    argument: str = "The objection survives review.",
    counterexample=None,
) -> dict:
    return {
        "raw_finding_id": raw_finding_id,
        "attack_objectives": (
            list(attack_objectives)
            if attack_objectives is not None
            else [GATE_A_ATTACK_OBJECTIVES[0]]
        ),
        "affected_claims": list(affected_claims or []),
        "affected_invariants": list(affected_invariants or []),
        "affected_coverage_entries": list(affected_coverage_entries or []),
        "evidence_references": list(evidence_references or ["canonical-packet"]),
        "statement": statement,
        "argument": argument,
        "counterexample": counterexample,
    }


def raw_review_payload(raw_findings: list[dict] | None = None) -> dict:
    findings = list(raw_findings or [])
    assessments = []
    for objective in GATE_A_ATTACK_OBJECTIVES:
        finding_ids = [
            raw["raw_finding_id"]
            for raw in findings
            if objective in raw.get("attack_objectives", [])
        ]
        assessments.append({"objective": objective, "finding_ids": finding_ids})
    return {
        "raw_review_schema_version": "1.0",
        "objective_assessments": assessments,
        "findings": findings,
    }


def challenge_output_payload(
    kind: str, objectives, objections: list[dict] | None = None
) -> dict:
    objections = list(objections or [])
    assessments = []
    for objective in objectives:
        objection_ids = [
            objection["challenge_objection_id"]
            for objection in objections
            if objection.get("objective") == objective
        ]
        assessments.append(
            {"objective": objective, "objection_ids": objection_ids}
        )
    return {
        "challenge_output_schema_version": "1.0",
        "challenge_kind": kind,
        "objective_assessments": assessments,
        "objections": objections,
    }


def attempt_payload(
    attempt_id: str = "ATTEMPT-1",
    *,
    outcome: str = "qualified",
    provider_model: str | None = "1",
    raw_output: dict | None = None,
    protocol_errors: list[str] | None = None,
    **overrides,
) -> dict:
    data = {
        "attempt_id": attempt_id,
        "call_id": f"CALL-{attempt_id}",
        "outcome": outcome,
        "started_at": "2026-09-19T00:00:00Z",
        "ended_at": "2026-09-19T00:01:00Z",
        "provider_model": provider_model,
        "provider_response_id": "RESP-1",
        "termination": "stop",
        "transport_attempt_count": 1,
        "raw_output": raw_output,
        "protocol_errors": list(protocol_errors or []),
    }
    data.update(overrides)
    return data


def build_receipt_payload(
    *,
    execution_id: str,
    role: str,
    reviewer_profile_id: str,
    protocol_bundle_sha256: str,
    prompt: dict,
    packet: dict,
    provider: str,
    model: str,
    model_version: str = "1",
    raw_output: dict | None = None,
    outcome: str = "qualified",
    attempts: list[dict] | None = None,
    resolved_identity: dict | None = None,
    overrides: dict | None = None,
) -> dict:
    if attempts is None:
        attempts = [
            attempt_payload(
                outcome=outcome,
                provider_model=model_version if outcome == "qualified" else None,
                raw_output=raw_output,
            )
        ]
    attempt_id = next(
        attempt["attempt_id"] for attempt in attempts if attempt["outcome"] == "qualified"
    )
    if resolved_identity is None and outcome == "qualified":
        resolved_identity = {
            "provider": provider,
            "model": model,
            "model_version": model_version,
            "resolution_kind": "provider-reported",
            "evidence_attempt_id": attempt_id,
        }
    payload = {
        "receipt_schema_version": "2.0",
        "execution_id": execution_id,
        "role": role,
        "reviewer_profile_id": reviewer_profile_id,
        "protocol_bundle_sha256": protocol_bundle_sha256,
        "input": {"prompt": prompt, "packet": packet},
        "isolated_context": True,
        "cross_reviewer_visibility_before_seal": False,
        "tools_enabled": False,
        "runtime": {"name": "fixture-runtime", "version": "1.0"},
        "request": {"provider": provider, "model": model},
        "attempts": attempts,
        "qualifying_attempt_id": next(
            attempt["attempt_id"]
            for attempt in attempts
            if attempt["outcome"] == "qualified"
        ),
        "resolved_identity": resolved_identity,
    }
    if overrides:
        payload.update(overrides)
    return payload


def write_receipt_payload(fixture_root: Path, payload: dict, name: str) -> dict:
    return write_json_artifact(
        fixture_root, f"formal/reviews/executions/{name}.json", payload
    )


def make_support_receipt(
    fixture_root: Path,
    *,
    name: str,
    role: str,
    profile_id: str,
    bundle_reference: dict,
    bundle_payload: dict,
    prompt_key: str,
    packet_reference: dict,
    output_reference: dict,
) -> dict:
    profile = supporting_profile(profile_id)
    payload = build_receipt_payload(
        execution_id=f"EXEC-{name.upper().replace('-', '')}",
        role=role,
        reviewer_profile_id=profile_id,
        protocol_bundle_sha256=bundle_reference["sha256"],
        prompt=bundle_payload["prompts"][prompt_key],
        packet=packet_reference,
        provider=profile["provider"],
        model=profile["request_model"],
        model_version="1",
        raw_output=output_reference,
    )
    return write_receipt_payload(fixture_root, payload, name)


def execution(
    fixture_root: Path,
    execution_id: str,
    *,
    packet: dict,
    prompt: dict,
    provider: str | None = None,
    model: str | None = None,
    model_version: str | None = None,
    reviewer_profile_id: str | None = None,
    attack_objectives: list[str] | None = None,
    raw_payload: dict | None = None,
    raw_finding_ids: list[str] | None = None,
    review_packet_sha256: str | None = None,
    prompt_sha256: str | None = None,
    isolated_context: bool = True,
    cross_reviewer_visibility_before_seal: bool = False,
) -> dict:
    identity_provider, identity_model, identity_version = default_model_identity(
        execution_id
    )
    slug = execution_id.removeprefix("EXEC-").lower() or "exec"
    if raw_payload is None:
        raw_payload = raw_review_payload()
    raw_output = write_json_artifact(
        fixture_root,
        f"formal/reviews/raw/{slug}.json",
        raw_payload,
        canonical=False,
    )
    return {
        "execution_id": execution_id,
        "reviewer_type": "frontier-llm",
        "reviewer_profile_id": (
            reviewer_profile_id
            if reviewer_profile_id is not None
            else f"profile-{slug}"
        ),
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
            list(raw_finding_ids)
            if raw_finding_ids is not None
            else [
                raw["raw_finding_id"]
                for raw in raw_payload.get("findings", [])
                if isinstance(raw, dict)
            ]
        ),
    }


def sync_execution_raw(
    fixture_root: Path, execution: dict, raw_findings: list[dict]
) -> None:
    payload = raw_review_payload(raw_findings)
    reference = write_json_artifact(
        fixture_root,
        execution["raw_output"]["path"],
        payload,
        canonical=False,
    )
    execution["raw_output"] = reference
    execution["raw_finding_ids"] = [
        raw["raw_finding_id"] for raw in raw_findings
    ]


def executions_for(
    fixture_root: Path, execution_ids: list[str]
) -> list[dict]:
    packet = write_gate_a_review_packet(fixture_root)
    prompt = bundle_document(fixture_root)["prompts"]["initial-reviewer"]
    return [
        execution(fixture_root, execution_id, packet=packet, prompt=prompt)
        for execution_id in execution_ids
    ]


def mutate_execution_receipt(
    fixture_root: Path, record: dict, index: int, mutator
) -> dict:
    execution = record["executions"][index]
    reference = execution["execution_receipt"]
    payload = json.loads(
        (fixture_root / reference["path"]).read_text(encoding="utf-8")
    )
    mutator(payload)
    new_reference = write_json_artifact(fixture_root, reference["path"], payload)
    execution["execution_receipt"] = new_reference
    return payload


def challenge_output_schema_errors(fixture_root: Path, payload: dict) -> list:
    schema = json.loads(
        (
            fixture_root
            / "formal/reviews/schemas/challenge-output-v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    return list(Draft202012Validator(schema).iter_errors(payload))


def replace_execution_raw_output(
    fixture_root: Path, record: dict, index: int, payload: dict
) -> dict:
    execution = record["executions"][index]
    old_reference = execution["raw_output"]
    reference = write_json_artifact(
        fixture_root,
        old_reference["path"],
        payload,
        canonical=False,
    )
    execution["raw_output"] = reference
    execution["raw_finding_ids"] = [
        raw["raw_finding_id"]
        for raw in payload.get("findings", [])
        if isinstance(raw, dict) and isinstance(raw.get("raw_finding_id"), str)
    ]
    receipt_reference = execution.get("execution_receipt")
    if isinstance(receipt_reference, dict):
        receipt_payload = json.loads(
            (fixture_root / receipt_reference["path"]).read_text(
                encoding="utf-8"
            )
        )
        for attempt in receipt_payload.get("attempts", []):
            attempt_reference = attempt.get("raw_output")
            if (
                isinstance(attempt_reference, dict)
                and attempt_reference.get("path") == old_reference["path"]
            ):
                attempt["raw_output"] = reference
        execution["execution_receipt"] = write_json_artifact(
            fixture_root, receipt_reference["path"], receipt_payload
        )
    return reference


def make_challenge_packet(fixture_root: Path, protocol: dict, *, name: str, kind: str, selector: str, payload: dict, objectives: tuple[str, ...]) -> dict:
    review_reference = protocol["review_packet"]
    review_payload = json.loads((fixture_root / review_reference["path"]).read_text(encoding="utf-8"))
    packet = {
        "challenge_packet_schema_version": "1.0",
        "challenge_kind": kind,
        "challenge_subject": {"selector": selector, "sha256": checker.sha256_hex(checker._canonical_json_bytes(payload)), "payload": payload},
        "required_objectives": list(objectives),
        "review_packet": {"sha256": review_reference["sha256"], "payload": review_payload},
    }
    return write_json_artifact(fixture_root, f"formal/reviews/challenge-packets/{name}.json", packet)

def attach_materiality_evidence(
    fixture_root: Path,
    protocol: dict,
    bundle_payload: dict,
    bundle_reference: dict,
    supporting: list[dict],
    *,
    name: str,
    substantive_finding: dict,
    materiality_mapping: dict,
    objections: list[dict] | None = None,
) -> None:
    output_reference = write_json_artifact(
        fixture_root,
        f"formal/reviews/adjudications/materiality-{name}.json",
        {"materiality_assessment": name},
    )
    assessment_receipt = make_support_receipt(
        fixture_root,
        name=f"materiality-{name}",
        role="materiality-assessor",
        profile_id="profile-materiality-assessor",
        bundle_reference=bundle_reference,
        bundle_payload=bundle_payload,
        prompt_key="adjudication",
        packet_reference=protocol["review_packet"],
        output_reference=output_reference,
    )
    supporting.append(assessment_receipt)
    materiality_mapping["assessment_execution_receipt"] = assessment_receipt

    material = any(
        materiality_mapping.get(axis) is True for axis in checker.MATERIALITY_AXES
    )
    if material:
        materiality_mapping["challenge"] = None
        return
    challenged_sha = checker._materiality_challenge_subject_sha256(
        substantive_finding, materiality_mapping
    )
    challenge_packet = make_challenge_packet(fixture_root, protocol, name=f"materiality-{name}", kind="materiality", selector=checker.MATERIALITY_CHALLENGE_SELECTOR, payload=checker._materiality_challenge_subject_payload(substantive_finding, materiality_mapping), objectives=checker.MATERIALITY_AXES)
    challenge_output = challenge_output_payload(
        "materiality",
        checker.MATERIALITY_AXES,
        objections,
    )
    challenge_output_reference = write_json_artifact(
        fixture_root,
        f"formal/reviews/challenges/materiality-{name}.json",
        challenge_output,
    )
    challenge_receipt = make_support_receipt(
        fixture_root,
        name=f"materiality-challenge-{name}",
        role="challenge",
        profile_id="profile-challenge",
        bundle_reference=bundle_reference,
        bundle_payload=bundle_payload,
        prompt_key="challenge",
        packet_reference=challenge_packet,
        output_reference=challenge_output_reference,
    )
    supporting.append(challenge_receipt)
    materiality_mapping["challenge"] = {
        "challenged_materiality_sha256": challenged_sha,
        "packet": challenge_packet,
        "execution_receipt": challenge_receipt,
        "output": challenge_output_reference,
        "rationale": "Fixture hostile materiality challenge.",
    }


def replace_materiality_challenge(
    fixture_root: Path,
    protocol: dict,
    bundle_payload: dict,
    bundle_reference: dict,
    supporting: list[dict],
    *,
    name: str,
    substantive_finding: dict,
    materiality_mapping: dict,
    objections: list[dict],
) -> None:
    previous = materiality_mapping.get("challenge")
    if isinstance(previous, dict):
        old_receipt = previous.get("execution_receipt") or {}
        old_key = (old_receipt.get("path"), old_receipt.get("sha256"))
        supporting[:] = [
            reference
            for reference in supporting
            if (reference.get("path"), reference.get("sha256")) != old_key
        ]
    challenged_sha = checker._materiality_challenge_subject_sha256(
        substantive_finding, materiality_mapping
    )
    challenge_packet = make_challenge_packet(fixture_root, protocol, name=f"materiality-{name}-revision", kind="materiality", selector=checker.MATERIALITY_CHALLENGE_SELECTOR, payload=checker._materiality_challenge_subject_payload(substantive_finding, materiality_mapping), objectives=checker.MATERIALITY_AXES)
    challenge_output = challenge_output_payload(
        "materiality", checker.MATERIALITY_AXES, objections
    )
    challenge_output_reference = write_json_artifact(
        fixture_root,
        f"formal/reviews/challenges/materiality-{name}-revision.json",
        challenge_output,
    )
    challenge_receipt = make_support_receipt(
        fixture_root,
        name=f"materiality-challenge-{name}-revision",
        role="challenge",
        profile_id="profile-challenge",
        bundle_reference=bundle_reference,
        bundle_payload=bundle_payload,
        prompt_key="challenge",
        packet_reference=challenge_packet,
        output_reference=challenge_output_reference,
    )
    supporting.append(challenge_receipt)
    materiality_mapping["challenge"] = {
        "challenged_materiality_sha256": challenged_sha,
        "packet": challenge_packet,
        "execution_receipt": challenge_receipt,
        "output": challenge_output_reference,
        "rationale": "Fixture revised hostile materiality challenge.",
    }


def attach_adjudication_receipt(
    fixture_root: Path,
    protocol: dict,
    bundle_payload: dict,
    bundle_reference: dict,
    supporting: list[dict],
    *,
    name: str,
    role: str,
    output_name: str | None = None,
) -> dict:
    output_reference = write_json_artifact(
        fixture_root,
        f"formal/reviews/adjudications/{output_name or name}.json",
        {"disposition": name},
    )
    receipt = make_support_receipt(
        fixture_root,
        name=name,
        role=role,
        profile_id="profile-adjudicator",
        bundle_reference=bundle_reference,
        bundle_payload=bundle_payload,
        prompt_key="adjudication",
        packet_reference=protocol["review_packet"],
        output_reference=output_reference,
    )
    supporting.append(receipt)
    return receipt


def attach_challenge(
    fixture_root: Path,
    record: dict,
    finding: dict,
    *,
    objections: list[dict] | None = None,
    execution_receipt: dict | None = None,
    output: dict | None = None,
    binding: str | None = None,
    role: str = "challenge",
) -> dict:
    bundle_payload = bundle_document(fixture_root)
    bundle_reference = record["protocol"]["protocol_bundle"]
    supporting = record.setdefault("supporting_executions", [])
    if not isinstance(finding.get("disposition"), dict):
        raise AssertionError("attaching a challenge requires a refuted disposition")
    expected_sha = checker._refutation_challenge_subject_sha256(finding)
    if output is None:
        challenge_output = challenge_output_payload(
            "refutation", checker.REFUTATION_CHALLENGE_OBJECTIVES, objections
        )
        output = write_json_artifact(
            fixture_root,
            f"formal/reviews/challenges/refutation-{finding['finding_id']}.json",
            challenge_output,
        )
    challenge_packet = make_challenge_packet(fixture_root, record["protocol"], name=f"refutation-{finding['finding_id']}", kind="refutation", selector=checker.REFUTATION_CHALLENGE_SELECTOR, payload=checker._refutation_challenge_subject_payload(finding), objectives=checker.REFUTATION_CHALLENGE_OBJECTIVES)
    if execution_receipt is None:
        receipt_payload = build_receipt_payload(
            execution_id=f"EXEC-CHALLENGE-{finding['finding_id'].upper().replace('-', '')}",
            role=role,
            reviewer_profile_id="profile-challenge",
            protocol_bundle_sha256=bundle_reference["sha256"],
            prompt=bundle_payload["prompts"]["challenge"],
            packet=challenge_packet,
            provider="provider-challenge" if role == "challenge" else "provider-adjudicator",
            model="model-challenge" if role == "challenge" else "model-adjudicator",
            model_version="1",
            raw_output=output,
        )
        if execution_receipt is None:
            execution_receipt = write_receipt_payload(
                fixture_root,
                receipt_payload,
                f"challenge-{finding['finding_id']}",
            )
            supporting.append(execution_receipt)
    finding["disposition"]["challenge"] = {
        "challenged_refutation_sha256": (
            binding if binding is not None else expected_sha
        ),
        "packet": challenge_packet,
        "execution_receipt": execution_receipt,
        "output": output,
        "rationale": "Fixture hostile refutation challenge.",
    }
    return finding


def make_re_adjudication(
    fixture_root: Path,
    protocol: dict,
    bundle_payload: dict,
    bundle_reference: dict,
    supporting: list[dict],
    *,
    source_review_id: str,
    source_finding: dict,
    material: bool = False,
    status: str = "open",
    disposition=None,
    name_suffix: str = "readj",
) -> dict:
    axes = {axis: axis == "authority_or_upstream_decision" and material for axis in checker.MATERIALITY_AXES}
    materiality_mapping = {
        **axes,
        "rationale": (
            "Assuming the finding is true, it could change the Gate A subject while "
            "still authorizing the candidate model."
        ),
    }
    item = {
        "source_review_id": source_review_id,
        "source_finding_id": source_finding["finding_id"],
        "source_finding_sha256": checker._finding_subject_sha256(source_finding),
        "materiality": materiality_mapping,
        "status": status,
        "disposition": disposition,
    }
    attach_materiality_evidence(
        fixture_root,
        protocol,
        bundle_payload,
        bundle_reference,
        supporting,
        name=f"{name_suffix}-{source_review_id}-{source_finding['finding_id']}",
        substantive_finding=source_finding,
        materiality_mapping=materiality_mapping,
    )
    if status == "refuted":
        receipt = attach_adjudication_receipt(
            fixture_root,
            protocol,
            bundle_payload,
            bundle_reference,
            supporting,
            name=f"{name_suffix}-refutation-{source_review_id}-{source_finding['finding_id']}",
            role="refutation-builder",
        )
        item["disposition"] = disposition if isinstance(disposition, dict) else refuted_disposition()
        item["disposition"]["adjudication_execution_receipt"] = receipt
        if material:
            expected_sha = checker._re_adjudication_refutation_subject_sha256(
                source_finding, item
            )
            challenge_output = challenge_output_payload(
                "refutation", checker.REFUTATION_CHALLENGE_OBJECTIVES
            )
            challenge_output_reference = write_json_artifact(
                fixture_root,
                f"formal/reviews/challenges/readj-{source_review_id}-{source_finding['finding_id']}.json",
                challenge_output,
            )
            challenge_packet = make_challenge_packet(fixture_root, protocol, name=f"readj-{source_review_id}-{source_finding['finding_id']}", kind="refutation", selector=checker.REFUTATION_CHALLENGE_SELECTOR, payload=checker._re_adjudication_refutation_subject_payload(source_finding, item), objectives=checker.REFUTATION_CHALLENGE_OBJECTIVES)
            challenge_receipt = make_support_receipt(
                fixture_root,
                name=f"readj-challenge-{source_review_id}-{source_finding['finding_id']}",
                role="challenge",
                profile_id="profile-challenge",
                bundle_reference=bundle_reference,
                bundle_payload=bundle_payload,
                prompt_key="challenge",
                packet_reference=challenge_packet,
                output_reference=challenge_output_reference,
            )
            supporting.append(challenge_receipt)
            item["disposition"]["challenge"] = {
                "challenged_refutation_sha256": expected_sha,
                "packet": challenge_packet,
                "execution_receipt": challenge_receipt,
                "output": challenge_output_reference,
                "rationale": "Fixture hostile re-adjudication refutation challenge.",
            }
    elif status in ("routed", "resolved"):
        role = "discovery-classifier" if status == "routed" else "derivation-builder"
        receipt = attach_adjudication_receipt(
            fixture_root,
            protocol,
            bundle_payload,
            bundle_reference,
            supporting,
            name=f"{name_suffix}-{status}-{source_review_id}-{source_finding['finding_id']}",
            role=role,
        )
        item["disposition"] = (
            disposition
            if isinstance(disposition, dict)
            else (routed_disposition() if status == "routed" else resolved_disposition())
        )
        item["disposition"]["adjudication_execution_receipt"] = receipt
    return item


def make_review(
    fixture_root: Path,
    *,
    review_id: str = "REVIEW-0001",
    review_class: str = "assurance-decomposition",
    subjects: list[dict] | None = None,
    protocol: dict | None = None,
    executions: list[dict] | None = None,
    findings: list[dict] | None = None,
    supporting_executions: list[dict] | None = None,
    re_adjudications: list[dict] | None = None,
    profiles: list[dict] | None = None,
    receipt_overrides: dict | None = None,
) -> dict:
    manifest = load_manifest(fixture_root)
    if subjects is None:
        subject, errors = checker.build_gate_a_review_subject(fixture_root, manifest)
        if errors or subject is None:
            raise AssertionError(errors or "Gate A subject derivation failed")
        subjects = [subject]

    bundle_payload = bundle_document(fixture_root)
    packet_reference: dict
    if protocol is None:
        packet_reference = write_gate_a_review_packet(fixture_root)
        protocol = {
            "review_packet": packet_reference,
            "prompt": bundle_payload["prompts"]["initial-reviewer"],
            "protocol_bundle": {},
        }
    packet_reference = protocol["review_packet"]
    prompt_reference = protocol["prompt"]

    if executions is None:
        executions = [
            execution(
                fixture_root,
                "EXEC-A",
                packet=packet_reference,
                prompt=prompt_reference,
            ),
            execution(
                fixture_root,
                "EXEC-B",
                packet=packet_reference,
                prompt=prompt_reference,
            ),
        ]

    if profiles is None:
        profiles = [
            default_profile(
                item["execution_id"], item.get("provider"), item.get("model")
            )
            for item in executions
        ]
    else:
        profiles = list(profiles)
    profiles.extend(supporting_profile(pid) for pid in SUPPORTING_PROFILE_DEFAULTS)
    bundle_payload, bundle_reference = install_protocol_bundle(
        fixture_root, profiles
    )
    protocol["protocol_bundle"] = bundle_reference

    records = list(findings) if findings is not None else []
    supporting = list(supporting_executions) if supporting_executions is not None else []

    for finding in records:
        sources = [
            source for source in finding.get("sources", []) if isinstance(source, dict)
        ]
        for source in sources:
            execution_id = source.get("execution_id")
            target = next(
                (
                    item
                    for item in executions
                    if item["execution_id"] == execution_id
                ),
                None,
            )
            if target is None:
                continue
            payload = json.loads(
                (fixture_root / target["raw_output"]["path"]).read_text(
                    encoding="utf-8"
                )
            )
            raw_id = source.get("raw_finding_id")
            existing = next(
                (
                    raw
                    for raw in payload.get("findings", [])
                    if isinstance(raw, dict)
                    and raw.get("raw_finding_id") == raw_id
                ),
                None,
            )
            if existing is None:
                payload.setdefault("findings", []).append(
                    raw_finding(
                        raw_id,
                        statement=finding["statement"],
                        argument=finding["argument"],
                        counterexample=finding["counterexample"],
                    )
                )
            assessments = []
            for objective in GATE_A_ATTACK_OBJECTIVES:
                finding_ids = [
                    raw["raw_finding_id"]
                    for raw in payload["findings"]
                    if objective in raw.get("attack_objectives", [])
                ]
                assessments.append(
                    {"objective": objective, "finding_ids": finding_ids}
                )
            payload["objective_assessments"] = assessments
            sync_execution_raw(fixture_root, target, payload["findings"])

    for finding in records:
        attach_materiality_evidence(
            fixture_root,
            protocol,
            bundle_payload,
            bundle_reference,
            supporting,
            name=f"finding-{finding['finding_id']}",
            substantive_finding=finding,
            materiality_mapping=finding["materiality"],
        )
        status = finding.get("status")
        disposition = finding.get("disposition")
        if isinstance(disposition, dict):
            role_by_status = {
                "refuted": "refutation-builder",
                "routed": "discovery-classifier",
                "resolved": "derivation-builder",
            }
            role = role_by_status.get(status)
            if role is not None and disposition.get(
                "adjudication_execution_receipt"
            ) is None:
                receipt = attach_adjudication_receipt(
                    fixture_root,
                    protocol,
                    bundle_payload,
                    bundle_reference,
                    supporting,
                    name=f"adjudication-{finding['finding_id']}",
                    role=role,
                )
                disposition["adjudication_execution_receipt"] = receipt

    if re_adjudications:
        for item in re_adjudications:
            if item["materiality"].get("assessment_execution_receipt") is None:
                attach_materiality_evidence(
                    fixture_root,
                    protocol,
                    bundle_payload,
                    bundle_reference,
                    supporting,
                    name=f"readj-{item['source_review_id']}-{item['source_finding_id']}",
                    substantive_finding=item["_source_finding"],
                    materiality_mapping=item["materiality"],
                )
            status = item.get("status")
            disposition = item.get("disposition")
            if isinstance(disposition, dict):
                role_by_status = {
                    "refuted": "refutation-builder",
                    "routed": "discovery-classifier",
                    "resolved": "derivation-builder",
                }
                role = role_by_status.get(status)
                if role is not None and disposition.get(
                    "adjudication_execution_receipt"
                ) is None:
                    receipt = attach_adjudication_receipt(
                        fixture_root,
                        protocol,
                        bundle_payload,
                        bundle_reference,
                        supporting,
                        name=f"readj-{item['source_review_id']}-{item['source_finding_id']}",
                        role=role,
                    )
                    disposition["adjudication_execution_receipt"] = receipt
            item.pop("_source_finding", None)

    for item in executions:
        profile_id = item["reviewer_profile_id"]
        profile = next(
            (
                candidate
                for candidate in bundle_payload["reviewer_profiles"]
                if candidate["profile_id"] == profile_id
            ),
            default_profile(item["execution_id"], item["provider"], item["model"]),
        )
        kind = profile.get("identity_resolution", {}).get("kind", "provider-reported")
        model_version = item["model_version"]
        resolved_identity = {
            "provider": item["provider"],
            "model": item["model"],
            "model_version": (
                profile["request_model"]
                if kind == "pinned-request-model"
                and profile.get("identity_resolution", {}).get(
                    "request_model_is_immutable_version"
                )
                is True
                else model_version
            ),
            "resolution_kind": kind,
            "evidence_attempt_id": "ATTEMPT-1",
        }
        receipt_payload = build_receipt_payload(
            execution_id=item["execution_id"],
            role="initial-reviewer",
            reviewer_profile_id=profile_id,
            protocol_bundle_sha256=bundle_reference["sha256"],
            prompt=prompt_reference,
            packet=packet_reference,
            provider=item["provider"],
            model=item["model"],
            model_version=model_version,
            raw_output=item["raw_output"],
            resolved_identity=resolved_identity,
        )
        overrides = (receipt_overrides or {}).get(item["execution_id"])
        if overrides:
            receipt_payload.update(overrides)
        receipt_reference = write_receipt_payload(
            fixture_root,
            receipt_payload,
            f"receipt-{item['execution_id'].lower()}",
        )
        item["execution_receipt"] = receipt_reference

    deduplicated_supporting: dict[tuple, dict] = {}
    for reference in supporting:
        deduplicated_supporting[
            (reference.get("path"), reference.get("sha256"))
        ] = reference

    return {
        "schema_version": "5.0",
        "review_id": review_id,
        "review_class": review_class,
        "repository_commit": "6d3c9851e0d66286280f8e49ebd8ed44da13d876",
        "subjects": subjects,
        "protocol": protocol,
        "executions": executions,
        "supporting_executions": list(deduplicated_supporting.values()),
        "findings": records,
        "re_adjudications": list(re_adjudications) if re_adjudications else [],
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
    wrapper = {"$defs": schema.get("$defs", {}), "$ref": "#/$defs/refutationChallenge"}
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
                "formal/reviews/raw/exec-a-duplicate.json",
                "{}\n",
            )
            record["executions"][1] = execution(
                fixture_root,
                "EXEC-A",
                packet=protocol["review_packet"],
                prompt=protocol["prompt"],
                raw_payload=raw_review_payload(),
            )
            record["executions"][1]["raw_output"] = duplicate_raw
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
            packet = write_gate_a_review_packet(fixture_root)
            prompt = bundle_document(fixture_root)["prompts"]["initial-reviewer"]
            executions = [
                execution(
                    fixture_root,
                    "EXEC-A",
                    packet=packet,
                    prompt=prompt,
                    provider="provider",
                    model="model",
                    model_version="1",
                ),
                execution(
                    fixture_root,
                    "EXEC-B",
                    packet=packet,
                    prompt=prompt,
                    provider="provider",
                    model="model",
                    model_version="1",
                ),
            ]
            record = make_review(fixture_root, executions=executions)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertIn("operational independence", summary["gate_a"]["reason"])

    def test_alias_models_with_same_effective_identity_do_not_satisfy_minimum(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            packet = write_gate_a_review_packet(fixture_root)
            prompt = bundle_document(fixture_root)["prompts"]["initial-reviewer"]
            executions = [
                execution(
                    fixture_root,
                    "EXEC-A",
                    packet=packet,
                    prompt=prompt,
                    provider="provider",
                    model="model-a",
                    model_version="1",
                ),
                execution(
                    fixture_root,
                    "EXEC-B",
                    packet=packet,
                    prompt=prompt,
                    provider="provider",
                    model="model-b",
                    model_version="1",
                ),
            ]
            record = make_review(fixture_root, executions=executions)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertIn("effective model identity", summary["gate_a"]["reason"])

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
            packet = write_gate_a_review_packet(fixture_root)
            prompt = bundle_document(fixture_root)["prompts"]["initial-reviewer"]
            executions = [
                execution(fixture_root, "EXEC-A", packet=packet, prompt=prompt),
                execution(fixture_root, "EXEC-B", packet=packet, prompt=prompt),
                execution(fixture_root, "EXEC-C", packet=packet, prompt=prompt),
            ]
            record = make_review(
                fixture_root,
                executions=executions,
                findings=[finding(status="open")],
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
            self.assertTrue(
                any(
                    "execution attack_objectives must equal the raw objective set"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

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
            self.assertTrue(
                any(
                    "execution attack_objectives must equal the raw objective set"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

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
                fixture_root,
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
                "formal/reviews/raw/missing.json"
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
            packet = write_gate_a_review_packet(fixture_root)
            prompt = bundle_document(fixture_root)["prompts"]["initial-reviewer"]
            executions = [
                execution(
                    fixture_root,
                    "EXEC-A",
                    packet=packet,
                    prompt=prompt,
                    raw_payload=raw_review_payload(
                        [raw_finding("EXEC-A-UNMAPPED")]
                    ),
                ),
                execution(fixture_root, "EXEC-B", packet=packet, prompt=prompt),
            ]
            record = make_review(fixture_root, executions=executions)
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

    def test_multiple_raw_findings_cannot_merge_into_one_normalized_finding(
        self,
    ) -> None:
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
            self.assertTrue(
                any(
                    "must declare exactly one source" in error for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

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
            record = make_review(
                fixture_root, executions=executions_for(fixture_root, ["EXEC-A", "EXEC-B"])
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])

            record = make_review(
                fixture_root,
                executions=executions_for(
                    fixture_root, ["EXEC-A", "EXEC-B", "EXEC-C"]
                ),
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
                make_review(
                    fixture_root,
                    review_id="REVIEW-A",
                    executions=executions_for(fixture_root, ["EXEC-A", "EXEC-B"]),
                ),
                name="REVIEW-A.yaml",
            )
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    review_id="REVIEW-B",
                    executions=executions_for(fixture_root, ["EXEC-C", "EXEC-D"]),
                    findings=[
                        finding(
                            status="open",
                            sources=[
                                {
                                    "execution_id": "EXEC-C",
                                    "raw_finding_id": "EXEC-C-F001",
                                }
                            ],
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

    def test_clean_review_cannot_override_a_routed_material_finding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    review_id="REVIEW-A",
                    executions=executions_for(fixture_root, ["EXEC-A", "EXEC-B"]),
                ),
                name="REVIEW-A.yaml",
            )
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    review_id="REVIEW-B",
                    executions=executions_for(fixture_root, ["EXEC-C", "EXEC-D"]),
                    findings=[
                        finding(
                            status="routed",
                            sources=[
                                {
                                    "execution_id": "EXEC-C",
                                    "raw_finding_id": "EXEC-C-F001",
                                }
                            ],
                            disposition=routed_disposition(),
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

    def test_clean_review_cannot_override_another_current_resolved_finding(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    review_id="REVIEW-A",
                    executions=executions_for(fixture_root, ["EXEC-A", "EXEC-B"]),
                ),
                name="REVIEW-A.yaml",
            )
            write_review(
                fixture_root,
                make_review(
                    fixture_root,
                    review_id="REVIEW-B",
                    executions=executions_for(fixture_root, ["EXEC-C", "EXEC-D"]),
                    findings=[
                        finding(
                            status="resolved",
                            sources=[
                                {
                                    "execution_id": "EXEC-C",
                                    "raw_finding_id": "EXEC-C-F001",
                                }
                            ],
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
            record = make_review(fixture_root, findings=[finding_record])
            attach_challenge(fixture_root, record, record["findings"][0])
            write_review(fixture_root, record)
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

    def test_refutation_challenge_receipt_must_be_supporting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[
                    finding(
                        status="refuted",
                        disposition=refuted_disposition(),
                    )
                ],
            )
            bundle_payload = bundle_document(fixture_root)
            orphan_payload = build_receipt_payload(
                execution_id="EXEC-ORPHANCHALLENGE",
                role="challenge",
                reviewer_profile_id="profile-challenge",
                protocol_bundle_sha256=record["protocol"]["protocol_bundle"][
                    "sha256"
                ],
                prompt=bundle_payload["prompts"]["challenge"],
                packet=record["protocol"]["review_packet"],
                provider="provider-challenge",
                model="model-challenge",
            )
            orphan_receipt = write_receipt_payload(
                fixture_root, orphan_payload, "orphan-challenge"
            )
            attach_challenge(
                fixture_root,
                record,
                record["findings"][0],
                execution_receipt=orphan_receipt,
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "execution receipt must appear in supporting_executions"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_refutation_challenge_receipt_role_must_be_challenge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[
                    finding(
                        status="refuted",
                        disposition=refuted_disposition(),
                    )
                ],
            )
            attach_challenge(
                fixture_root,
                record,
                record["findings"][0],
                role="materiality-assessor",
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "receipt role must be challenge" in error for error in errors
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
            record = make_review(fixture_root, findings=[finding_record])
            attach_challenge(
                fixture_root,
                record,
                record["findings"][0],
                output={
                    "path": "formal/reviews/challenges/missing.json",
                    "sha256": "a" * 64,
                },
            )
            write_review(fixture_root, record)
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
            record = make_review(fixture_root, findings=[finding_record])
            attach_challenge(fixture_root, record, record["findings"][0])
            record["findings"][0]["disposition"]["challenge"]["output"][
                "sha256"
            ] = "0" * 64
            write_review(fixture_root, record)
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
            record = make_review(fixture_root, findings=[finding_record])
            attach_challenge(fixture_root, record, record["findings"][0])
            write_review(fixture_root, record)
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
            record = make_review(fixture_root, findings=[finding_record])
            attach_challenge(fixture_root, record, record["findings"][0])
            challenge = record["findings"][0]["disposition"]["challenge"]
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
            record = make_review(fixture_root, findings=[finding_record])
            attach_challenge(fixture_root, record, record["findings"][0])
            record["findings"][0]["disposition"]["challenge"][
                "challenged_refutation_sha256"
            ] = "0" * 64
            write_review(fixture_root, record)
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
            record = make_review(fixture_root, findings=[finding_record])
            attach_challenge(fixture_root, record, record["findings"][0])
            record["findings"][0]["disposition"]["argument"] = (
                "The refutation argument was rewritten after the challenge was sealed."
            )
            write_review(fixture_root, record)
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
            record = make_review(fixture_root, findings=[finding_record])
            attach_challenge(
                fixture_root,
                record,
                record["findings"][0],
                output={
                    "path": "formal/reviews/challenges/missing.json",
                    "sha256": "a" * 64,
                },
            )
            write_review(fixture_root, record)
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


def challenge_objection(
    objective: str, objection_id: str = "OBJ-1"
) -> dict:
    return {
        "challenge_objection_id": objection_id,
        "objective": objective,
        "statement": "The closure candidate does not survive hostile challenge.",
        "argument": "A counterexample or alternative interpretation remains in scope.",
        "evidence_references": ["canonical-packet"],
    }


class GateAProtocolV4Tests(unittest.TestCase):
    def test_review_schema_v4_accepts_valid_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            self.assertEqual(
                [], review_schema_errors(fixture_root, make_review(fixture_root))
            )

    def test_review_schema_rejects_v3_0_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            legacy = make_review(fixture_root)
            legacy["schema_version"] = "3.0"
            self.assertTrue(review_schema_errors(fixture_root, legacy))
            write_review(fixture_root, legacy, name="REVIEW-LEGACY-V3.yaml")
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_canonical_current_protocol_bundle_validates(self) -> None:
        manifest = yaml.safe_load((ROOT / MANIFEST_RELATIVE).read_text())
        bundle_validator, schema_errors = checker._load_schema_validator(
            ROOT, checker.PROTOCOL_BUNDLE_SCHEMA_RELATIVE
        )
        self.assertEqual([], schema_errors)
        _reference, bundle, errors = checker._current_protocol_bundle_errors(
            ROOT, manifest, bundle_validator, {}
        )
        self.assertEqual([], errors)
        self.assertIsNotNone(bundle)
        self.assertEqual(
            [], checker._protocol_bundle_errors(ROOT, bundle, "current protocol bundle")
        )
        self.assertEqual([], bundle.get("reviewer_profiles"))

    def test_protocol_bundle_bad_sha_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["policy"]["hostile_review"]["current_protocol_bundle"][
                "sha256"
            ] = "0" * 64
            save_manifest(fixture_root, manifest)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("artifact sha256 does not match" in error for error in errors),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_protocol_bundle_noncanonical_json_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            reference = current_protocol_bundle_reference(fixture_root)
            payload = bundle_document(fixture_root)
            data = json.dumps(payload, indent=2).encode("utf-8")
            (fixture_root / reference["path"]).write_bytes(data)
            manifest = load_manifest(fixture_root)
            manifest["policy"]["hostile_review"]["current_protocol_bundle"] = {
                "path": reference["path"],
                "sha256": checker.sha256_hex(data),
            }
            save_manifest(fixture_root, manifest)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "canonical JSON document serialization" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_protocol_bundle_prompt_hash_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            reference = current_protocol_bundle_reference(fixture_root)
            payload = bundle_document(fixture_root)
            payload["prompts"]["initial-reviewer"]["sha256"] = "0" * 64
            data = checker._canonical_json_document_bytes(payload)
            (fixture_root / reference["path"]).write_bytes(data)
            manifest = load_manifest(fixture_root)
            manifest["policy"]["hostile_review"]["current_protocol_bundle"] = {
                "path": reference["path"],
                "sha256": checker.sha256_hex(data),
            }
            save_manifest(fixture_root, manifest)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "prompts.initial-reviewer" in error
                    and "artifact sha256 does not match" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_unknown_reviewer_profile_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root, profiles=[default_profile("EXEC-B")]
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("unknown reviewer profile" in error for error in errors),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "hostile review evidence integrity failure",
                summary["gate_a"]["reason"],
            )

    def test_frontier_eligible_false_profile_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                profiles=[
                    default_profile("EXEC-A", frontier_eligible=False),
                    default_profile("EXEC-B"),
                ],
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("not frontier eligible" in error for error in errors), errors
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_profile_provider_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                profiles=[
                    default_profile("EXEC-A", provider="provider-other"),
                    default_profile("EXEC-B"),
                ],
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "receipt request provider does not match its reviewer profile"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_profile_request_model_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                profiles=[
                    default_profile("EXEC-A", model="model-other"),
                    default_profile("EXEC-B"),
                ],
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "receipt request model does not match its reviewer profile"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_provider_reported_identity_requires_provider_model(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)

            def mutator(payload: dict) -> None:
                payload["attempts"][0]["provider_model"] = None

            mutate_execution_receipt(fixture_root, record, 0, mutator)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "provider-reported identity requires a non-empty provider_model"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_provider_reported_model_version_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)

            def mutator(payload: dict) -> None:
                payload["resolved_identity"]["model_version"] = "999"

            mutate_execution_receipt(fixture_root, record, 0, mutator)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "provider-reported model_version must equal the qualified "
                    "attempt provider_model" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_pinned_request_model_requires_immutable_version_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                profiles=[
                    default_profile("EXEC-A", kind="pinned-request-model"),
                    default_profile("EXEC-B"),
                ],
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "pinned-request-model requires "
                    "request_model_is_immutable_version = true" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_pinned_request_model_version_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                profiles=[
                    default_profile(
                        "EXEC-A",
                        kind="pinned-request-model",
                        immutable=True,
                    ),
                    default_profile("EXEC-B"),
                ],
            )

            def mutator(payload: dict) -> None:
                payload["resolved_identity"]["model_version"] = "999"

            mutate_execution_receipt(fixture_root, record, 0, mutator)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "pinned-request-model model_version must equal the profile "
                    "request_model" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_raw_output_must_be_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["executions"][0]["raw_output"]["path"] = (
                "formal/reviews/raw/exec-a.md"
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "artifact path must use the .json suffix" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_raw_output_missing_required_objective_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            payload = raw_review_payload()
            payload["objective_assessments"] = payload["objective_assessments"][:-1]
            replace_execution_raw_output(fixture_root, record, 0, payload)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "must assess exactly the 14 Gate A attack objectives once each"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_raw_output_duplicate_objective_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            payload = raw_review_payload()
            payload["objective_assessments"][0] = dict(
                payload["objective_assessments"][1]
            )
            replace_execution_raw_output(fixture_root, record, 0, payload)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "must assess exactly the 14 Gate A attack objectives once each"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_execution_raw_finding_ids_must_equal_raw(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["executions"][0]["raw_finding_ids"] = ["EXEC-A-EXTRA"]
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "execution raw_finding_ids must equal the raw finding ID set"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_raw_objective_broken_finding_reference_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            payload = raw_review_payload()
            payload["objective_assessments"][0]["finding_ids"] = [
                "EXEC-A-MISSING"
            ]
            replace_execution_raw_output(fixture_root, record, 0, payload)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "references unknown raw finding 'EXEC-A-MISSING'" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_raw_finding_objective_reciprocal_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            payload = raw_review_payload(
                [raw_finding("EXEC-A-F001", attack_objectives=["vacuity"])]
            )
            for assessment in payload["objective_assessments"]:
                if assessment["objective"] == "vacuity":
                    assessment["finding_ids"] = []
                if assessment["objective"] == "semantic-strengthening":
                    assessment["finding_ids"] = ["EXEC-A-F001"]
            replace_execution_raw_output(fixture_root, record, 0, payload)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "declares objective 'vacuity' that does not reference it "
                    "reciprocally" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_normalized_statement_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root, findings=[finding()])
            record["findings"][0]["statement"] = "A rewritten statement."
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "statement must equal the exact raw finding statement" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_normalized_argument_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root, findings=[finding()])
            record["findings"][0]["argument"] = "A rewritten argument."
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "argument must equal the exact raw finding argument" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_normalized_counterexample_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root, findings=[finding()])
            record["findings"][0]["counterexample"] = "An invented counterexample."
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "counterexample must equal the exact raw finding counterexample"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_protocol_invalid_completed_attempt_without_sealed_output_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            raw_reference = dict(record["executions"][0]["raw_output"])

            def mutator(payload: dict) -> None:
                payload["attempts"] = [
                    attempt_payload(
                        "ATTEMPT-1",
                        outcome="protocol-invalid",
                        provider_model=None,
                        raw_output=None,
                    ),
                    attempt_payload("ATTEMPT-2", raw_output=raw_reference),
                ]
                payload["qualifying_attempt_id"] = "ATTEMPT-2"
                payload["resolved_identity"]["evidence_attempt_id"] = "ATTEMPT-2"

            mutate_execution_receipt(fixture_root, record, 0, mutator)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("must seal its raw output" in error for error in errors),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_protocol_invalid_sealed_attempt_then_qualified_attempt_accepted(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            raw_reference = dict(record["executions"][0]["raw_output"])
            invalid_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/raw/exec-a-invalid-attempt.json",
                {"protocol_invalid": True},
                canonical=False,
            )

            def mutator(payload: dict) -> None:
                payload["attempts"] = [
                    attempt_payload(
                        "ATTEMPT-1",
                        outcome="protocol-invalid",
                        provider_model="1",
                        raw_output=invalid_reference,
                        protocol_errors=["schema-invalid"],
                    ),
                    attempt_payload("ATTEMPT-2", raw_output=raw_reference),
                ]
                payload["qualifying_attempt_id"] = "ATTEMPT-2"
                payload["resolved_identity"]["evidence_attempt_id"] = "ATTEMPT-2"

            mutate_execution_receipt(fixture_root, record, 0, mutator)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_two_qualified_attempts_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            raw_reference = dict(record["executions"][0]["raw_output"])
            second_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/raw/exec-a-second-qualified.json",
                {"second": True},
                canonical=False,
            )

            def mutator(payload: dict) -> None:
                payload["attempts"] = [
                    attempt_payload("ATTEMPT-1", raw_output=raw_reference),
                    attempt_payload("ATTEMPT-2", raw_output=second_reference),
                ]
                payload["qualifying_attempt_id"] = "ATTEMPT-1"

            mutate_execution_receipt(fixture_root, record, 0, mutator)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "exactly one attempt must have outcome qualified; found 2"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_refutation_challenge_objection_cannot_close_finding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[
                    finding(status="refuted", disposition=refuted_disposition())
                ],
            )
            attach_challenge(
                fixture_root,
                record,
                record["findings"][0],
                objections=[
                    challenge_objection("attacked-premise-still-supported")
                ],
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "with any surviving objection cannot close the finding" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_schema4_rejects_surviving_material_argument(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[
                    finding(status="refuted", disposition=refuted_disposition())
                ],
            )
            attach_challenge(fixture_root, record, record["findings"][0])
            record["findings"][0]["disposition"]["challenge"][
                "surviving_material_argument"
            ] = False
            self.assertTrue(review_schema_errors(fixture_root, record))

    def test_schema4_rejects_challenger_execution_id(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[
                    finding(status="refuted", disposition=refuted_disposition())
                ],
            )
            attach_challenge(fixture_root, record, record["findings"][0])
            record["findings"][0]["disposition"]["challenge"][
                "challenger_execution_id"
            ] = "EXEC-B"
            self.assertTrue(review_schema_errors(fixture_root, record))

    def test_challenge_output_schema_rejects_incidental_findings(self) -> None:
        payload = challenge_output_payload(
            "refutation", checker.REFUTATION_CHALLENGE_OBJECTIVES
        )
        payload["incidental_findings"] = []
        self.assertTrue(challenge_output_schema_errors(ROOT, payload))

    def test_non_material_finding_without_materiality_challenge_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root, findings=[finding(material=False)]
            )
            record["findings"][0]["materiality"]["challenge"] = None
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "requires a hostile materiality challenge" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_non_material_materiality_challenge_with_objection_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root, findings=[finding(material=False)]
            )
            bundle_payload = bundle_document(fixture_root)
            bundle_reference = current_protocol_bundle_reference(fixture_root)
            replace_materiality_challenge(
                fixture_root,
                record["protocol"],
                bundle_payload,
                bundle_reference,
                record["supporting_executions"],
                name="finding-F-1",
                substantive_finding=record["findings"][0],
                materiality_mapping=record["findings"][0]["materiality"],
                objections=[challenge_objection(checker.MATERIALITY_AXES[0])],
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "with any surviving objection cannot support a non-material "
                    "conclusion" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_valid_zero_objection_materiality_challenge_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root, findings=[finding(material=False)]
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_material_finding_must_have_null_materiality_challenge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root, findings=[finding(material=True)]
            )
            bundle_payload = bundle_document(fixture_root)
            bundle_reference = current_protocol_bundle_reference(fixture_root)
            replace_materiality_challenge(
                fixture_root,
                record["protocol"],
                bundle_payload,
                bundle_reference,
                record["supporting_executions"],
                name="finding-F-1",
                substantive_finding=record["findings"][0],
                materiality_mapping=record["findings"][0]["materiality"],
                objections=[],
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "a material finding must not carry a materiality challenge"
                    in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_stale_protocol_finding_without_re_adjudication_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[finding(finding_id="F-1", status="open")],
            )
            write_review(fixture_root, record, name="REVIEW-STALE.yaml")
            install_protocol_bundle(
                fixture_root, [default_profile("EXEC-C")]
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "stale-protocol finding requires current re-adjudication",
                summary["gate_a"]["reason"],
            )

    def test_stale_protocol_old_refutation_without_re_adjudication_blocks(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[
                    finding(
                        finding_id="F-1",
                        counterexample="A concrete counterexample trace.",
                        status="refuted",
                        disposition=refuted_disposition(
                            counterexample_disposition=counterexample_disposition()
                        ),
                    )
                ],
            )
            attach_challenge(fixture_root, record, record["findings"][0])
            write_review(fixture_root, record, name="REVIEW-STALE.yaml")
            install_protocol_bundle(
                fixture_root, [default_profile("EXEC-C")]
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "stale-protocol finding requires current re-adjudication",
                summary["gate_a"]["reason"],
            )

    def test_stale_protocol_old_non_material_without_re_adjudication_blocks(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[
                    finding(finding_id="F-1", material=False, status="open")
                ],
            )
            write_review(fixture_root, record, name="REVIEW-STALE.yaml")
            install_protocol_bundle(
                fixture_root, [default_profile("EXEC-C")]
            )
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "stale-protocol finding requires current re-adjudication",
                summary["gate_a"]["reason"],
            )

    def _re_adjudicated_fixture(
        self, fixture_root: Path, *, material: bool
    ) -> tuple[dict, dict]:
        record_a = make_review(
            fixture_root,
            review_id="REVIEW-A",
            findings=[
                finding(finding_id="F-1", material=False, status="open")
            ],
        )
        source_finding = record_a["findings"][0]
        write_review(fixture_root, record_a, name="REVIEW-A.yaml")

        install_protocol_bundle(fixture_root, [default_profile("EXEC-C")])

        record_b = make_review(
            fixture_root,
            review_id="REVIEW-B",
            executions=executions_for(fixture_root, ["EXEC-C", "EXEC-D"]),
        )
        bundle_payload = bundle_document(fixture_root)
        bundle_reference = current_protocol_bundle_reference(fixture_root)
        protocol_shell = {
            "review_packet": record_b["protocol"]["review_packet"],
            "prompt": record_b["protocol"]["prompt"],
            "protocol_bundle": bundle_reference,
        }
        supporting: list[dict] = []
        item = make_re_adjudication(
            fixture_root,
            protocol_shell,
            bundle_payload,
            bundle_reference,
            supporting,
            source_review_id="REVIEW-A",
            source_finding=source_finding,
            material=material,
            status="open",
        )
        record_b = make_review(
            fixture_root,
            review_id="REVIEW-B",
            executions=executions_for(fixture_root, ["EXEC-C", "EXEC-D"]),
            supporting_executions=supporting,
            re_adjudications=[item],
        )
        write_review(fixture_root, record_b, name="REVIEW-B.yaml")
        return record_a, record_b

    def test_valid_current_protocol_re_adjudication_recognized(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            self._re_adjudicated_fixture(fixture_root, material=False)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_re_adjudicated_material_open_finding_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            self._re_adjudicated_fixture(fixture_root, material=True)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertFalse(summary["gate_a"]["ready"])
            self.assertEqual(
                "surviving material hostile-review finding exists",
                summary["gate_a"]["reason"],
            )

    def test_stale_protocol_review_does_not_satisfy_minimum(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            write_review(fixture_root, record, name="REVIEW-STALE.yaml")
            install_protocol_bundle(
                fixture_root, [default_profile("EXEC-C")]
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

    def test_current_protocol_bundle_change_does_not_change_subject(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, first_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], first_errors)
            manifest["policy"]["hostile_review"]["current_protocol_bundle"] = {
                "path": "formal/reviews/protocols/other.json",
                "sha256": "a" * 64,
            }
            second, second_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], second_errors)
            self.assertEqual(first, second)

    def test_hostile_review_protocol_only_fields_do_not_change_subject(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            first, first_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], first_errors)
            hostile_review = manifest["policy"]["hostile_review"]
            hostile_review["minimum_independent_reviewers"] = 5
            hostile_review["current_protocol_bundle"] = {
                "path": "formal/reviews/protocols/other.json",
                "sha256": "b" * 64,
            }
            hostile_review["majority_vote_sufficient"] = False
            second, second_errors = checker.build_gate_a_review_subject(
                fixture_root, manifest
            )
            self.assertEqual([], second_errors)
            self.assertEqual(first, second)

    def test_gate_a_subject_sha_is_exact(self) -> None:
        manifest = yaml.safe_load((ROOT / MANIFEST_RELATIVE).read_text())
        subject, errors = checker.build_gate_a_review_subject(ROOT, manifest)
        self.assertEqual([], errors)
        self.assertEqual(
            "2b0dd42fb07d67f3a38d0414f12df49ecb9df640f12c805ee98b6af3a1db979b",
            subject["sha256"],
        )


class GateAProtocolV5RegressionTests(unittest.TestCase):
    def test_published_protocol_v1_artifacts_remain_byte_identical(self):
        expected = {
            "formal/reviews/protocols/gate-a-campaign-protocol-v1.json": "156d6247907f17b49802b7953ef866bdd6e07c2b3f40b01c45f6077bd8498cc1",
            "formal/reviews/prompts/gate-a-initial-review-v1.md": "516c63b4df16c72fb7ac1718fa4af5a9ab402e0ecf9c460d44a65858b7862748",
            "formal/reviews/prompts/gate-a-adjudication-v1.md": "76a342dd88f2566a9fa40ee3b9f5ccbd6d5b399de822227b3ccd451774dc2f50",
            "formal/reviews/prompts/gate-a-challenge-v1.md": "b5fef8fd42eef80175556322c8067dc5ea9c1eb66869061e22ef194a434aeb65",
            "formal/reviews/prompts/gate-a-repair-v1.md": "3c7e1e97667c5f0e3d2e578d6c256a22cf5227b66865f858421cc7d23dad5a6c",
            "formal/reviews/schemas/raw-review-output-v1.schema.json": "ab9c8f7c8d0e0314a925a7feb589975c98314c0e47e70c7794c1e1443aca8b6c",
            "formal/reviews/schemas/challenge-output-v1.schema.json": "418245a1619b51090fc52e431996f05303ce6f38736423212879b6cb768419f2",
            "formal/reviews/schemas/execution-receipt-v1.schema.json": "f23511730695a61d4a79102874228196c26af9c6c8ce3b4af6251c1429dd8d2b",
        }
        for relative, expected_hash in expected.items():
            self.assertEqual(expected_hash, checker.sha256_hex((ROOT / relative).read_bytes()))

    def test_current_protocol_is_v2_and_predecessor_is_exact_v1(self):
        manifest = yaml.safe_load((ROOT / MANIFEST_RELATIVE).read_text())
        reference = manifest["policy"]["hostile_review"]["current_protocol_bundle"]
        self.assertEqual("formal/reviews/protocols/gate-a-campaign-protocol-v2.json", reference["path"])
        bundle = json.loads((ROOT / reference["path"]).read_text())
        self.assertEqual("gate-a-campaign-protocol-v2", bundle["protocol_id"])
        self.assertEqual({"path": "formal/reviews/protocols/gate-a-campaign-protocol-v1.json", "sha256": "156d6247907f17b49802b7953ef866bdd6e07c2b3f40b01c45f6077bd8498cc1"}, bundle["predecessor"])

    def test_current_protocol_v2_change_does_not_change_gate_a_subject(self):
        manifest = yaml.safe_load((ROOT / MANIFEST_RELATIVE).read_text())
        reference = manifest["policy"]["hostile_review"]["current_protocol_bundle"]
        bundle = json.loads((ROOT / reference["path"]).read_text())
        self.assertEqual(2, bundle["protocol_bundle_schema_version"])
        subject, errors = checker.build_gate_a_review_subject(ROOT, manifest)
        self.assertEqual([], errors)
        self.assertEqual("2b0dd42fb07d67f3a38d0414f12df49ecb9df640f12c805ee98b6af3a1db979b", subject["sha256"])

    def test_review_schema5_is_current(self):
        schema = json.loads((ROOT / "formal/reviews/review-evidence.schema.json").read_text())
        self.assertEqual("5.0", schema["properties"]["schema_version"]["const"])

    def test_schema4_review_record_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            record["schema_version"] = "4.0"
            self.assertTrue(review_schema_errors(fixture_root, record))

    def test_initial_valid_output_cannot_be_declared_protocol_invalid(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            raw = write_json_artifact(root, "formal/reviews/raw/valid.json", raw_review_payload(), canonical=False)
            bundle_ref = current_protocol_bundle_reference(root)
            validators, errors = checker._bundle_selected_validators(root, bundle_document(root), "test")
            self.assertEqual([], errors)
            profile = default_profile("EXEC-ONE")
            attempts = [attempt_payload("ATTEMPT-1", outcome="protocol-invalid", raw_output=raw, protocol_errors=["claimed"]), attempt_payload("ATTEMPT-2", outcome="qualified", raw_output=write_json_artifact(root, "formal/reviews/raw/valid2.json", raw_review_payload(), canonical=False), provider_model="1")]
            receipt = build_receipt_payload(execution_id="EXEC-ONE", role="initial-reviewer", reviewer_profile_id=profile["profile_id"], protocol_bundle_sha256=bundle_ref["sha256"], prompt=bundle_document(root)["prompts"]["initial-reviewer"], packet=write_gate_a_review_packet(root), provider=profile["provider"], model=profile["request_model"], attempts=attempts)
            errors, _ = checker._validate_execution_receipt(root, receipt, "test", {profile["profile_id"]: profile}, bundle_ref["sha256"], validators)
            self.assertTrue(any("declared protocol-invalid but output is protocol-valid" in error for error in errors))

    def test_initial_qualified_attempt_must_be_final(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            raw = write_json_artifact(root, "formal/reviews/raw/valid.json", raw_review_payload(), canonical=False)
            bundle_ref = current_protocol_bundle_reference(root); bundle = bundle_document(root)
            validators, _ = checker._bundle_selected_validators(root, bundle, "test"); profile = default_profile("EXEC-ONE")
            attempts=[attempt_payload("ATTEMPT-1", outcome="qualified", raw_output=raw, provider_model="1"), attempt_payload("ATTEMPT-2", outcome="technical-failure", raw_output=None)]
            receipt=build_receipt_payload(execution_id="EXEC-ONE", role="initial-reviewer", reviewer_profile_id=profile["profile_id"], protocol_bundle_sha256=bundle_ref["sha256"], prompt=bundle["prompts"]["initial-reviewer"], packet=write_gate_a_review_packet(root), provider=profile["provider"], model=profile["request_model"], attempts=attempts)
            errors,_=checker._validate_execution_receipt(root,receipt,"test",{profile["profile_id"]:profile},bundle_ref["sha256"],validators)
            self.assertTrue(any("qualified attempt must be final" in error for error in errors))

    def test_initial_protocol_invalid_output_can_precede_qualified_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            raw_reference = dict(record["executions"][0]["raw_output"])
            invalid_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/raw/exec-a-invalid-predecessor.json",
                {"protocol_invalid": True},
                canonical=False,
            )

            def mutator(payload: dict) -> None:
                payload["attempts"] = [
                    attempt_payload(
                        "ATTEMPT-1",
                        outcome="protocol-invalid",
                        provider_model="1",
                        raw_output=invalid_reference,
                        protocol_errors=["schema-invalid"],
                    ),
                    attempt_payload("ATTEMPT-2", raw_output=raw_reference),
                ]
                payload["qualifying_attempt_id"] = "ATTEMPT-2"
                payload["resolved_identity"]["evidence_attempt_id"] = "ATTEMPT-2"

            mutate_execution_receipt(fixture_root, record, 0, mutator)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def _receipt_schema_violations(
        self, fixture_root: Path, attempts: list[dict]
    ) -> list[str]:
        bundle = bundle_document(fixture_root)
        validators, errors = checker._bundle_selected_validators(
            fixture_root, bundle, "test"
        )
        self.assertEqual([], errors)
        payload = build_receipt_payload(
            execution_id="EXEC-SCHEMA",
            role="initial-reviewer",
            reviewer_profile_id="profile-schema",
            protocol_bundle_sha256="0" * 64,
            prompt=bundle["prompts"]["initial-reviewer"],
            packet={
                "path": "formal/reviews/packets/packet.json",
                "sha256": "0" * 64,
            },
            provider="provider-schema",
            model="model-schema",
            attempts=attempts,
        )
        return checker._schema_violations(
            validators["execution-receipt"], payload, "receipt"
        )

    def test_initial_protocol_invalid_attempt_requires_nonempty_protocol_errors(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            raw_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/raw/schema-attempt-one.json",
                raw_review_payload(),
                canonical=False,
            )
            second_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/raw/schema-attempt-two.json",
                raw_review_payload(),
                canonical=False,
            )
            violations = self._receipt_schema_violations(
                fixture_root,
                [
                    attempt_payload(
                        "ATTEMPT-1",
                        outcome="protocol-invalid",
                        provider_model="1",
                        raw_output=raw_reference,
                        protocol_errors=[],
                    ),
                    attempt_payload("ATTEMPT-2", raw_output=second_reference),
                ],
            )
            self.assertTrue(
                any("protocol_errors" in violation for violation in violations),
                violations,
            )

    def test_initial_qualified_attempt_requires_empty_protocol_errors(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            raw_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/raw/schema-qualified.json",
                raw_review_payload(),
                canonical=False,
            )
            violations = self._receipt_schema_violations(
                fixture_root,
                [
                    attempt_payload(
                        "ATTEMPT-1",
                        raw_output=raw_reference,
                        protocol_errors=["claimed-invalid"],
                    )
                ],
            )
            self.assertTrue(
                any("protocol_errors" in violation for violation in violations),
                violations,
            )

    def test_initial_qualified_output_that_is_protocol_invalid_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root)
            invalid_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/raw/exec-a-qualified-invalid.json",
                {"not": "a raw review output"},
                canonical=False,
            )

            def mutator(payload: dict) -> None:
                payload["attempts"] = [
                    attempt_payload("ATTEMPT-1", raw_output=invalid_reference)
                ]
                payload["qualifying_attempt_id"] = "ATTEMPT-1"
                payload["resolved_identity"]["evidence_attempt_id"] = "ATTEMPT-1"

            mutate_execution_receipt(fixture_root, record, 0, mutator)
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "declared qualified but output is protocol-invalid" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_technical_failure_attempt_must_not_have_raw_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            raw_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/raw/schema-technical-raw.json",
                raw_review_payload(),
                canonical=False,
            )
            violations = self._receipt_schema_violations(
                fixture_root,
                [
                    attempt_payload(
                        "ATTEMPT-1",
                        outcome="technical-failure",
                        provider_model=None,
                        raw_output=raw_reference,
                    ),
                    attempt_payload("ATTEMPT-2", raw_output=raw_reference),
                ],
            )
            self.assertTrue(
                any("raw_output" in violation for violation in violations),
                violations,
            )

    def test_technical_failure_attempt_must_not_have_protocol_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            raw_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/raw/schema-technical-errors.json",
                raw_review_payload(),
                canonical=False,
            )
            violations = self._receipt_schema_violations(
                fixture_root,
                [
                    attempt_payload(
                        "ATTEMPT-1",
                        outcome="technical-failure",
                        provider_model=None,
                        raw_output=None,
                        protocol_errors=["unexpected"],
                    ),
                    attempt_payload("ATTEMPT-2", raw_output=raw_reference),
                ],
            )
            self.assertTrue(
                any("protocol_errors" in violation for violation in violations),
                violations,
            )

    def test_execution_call_ids_must_be_unique(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            raw_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/raw/schema-call-one.json",
                raw_review_payload(),
                canonical=False,
            )
            second_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/raw/schema-call-two.json",
                raw_review_payload(),
                canonical=False,
            )
            bundle_reference = current_protocol_bundle_reference(fixture_root)
            bundle = bundle_document(fixture_root)
            validators, errors = checker._bundle_selected_validators(
                fixture_root, bundle, "test"
            )
            self.assertEqual([], errors)
            profile = default_profile("EXEC-CALL")
            attempts = [
                attempt_payload("ATTEMPT-1", raw_output=raw_reference),
                attempt_payload(
                    "ATTEMPT-2",
                    raw_output=second_reference,
                    call_id="CALL-ATTEMPT-1",
                ),
            ]
            receipt = build_receipt_payload(
                execution_id="EXEC-CALL",
                role="initial-reviewer",
                reviewer_profile_id=profile["profile_id"],
                protocol_bundle_sha256=bundle_reference["sha256"],
                prompt=bundle["prompts"]["initial-reviewer"],
                packet=write_gate_a_review_packet(fixture_root),
                provider=profile["provider"],
                model=profile["request_model"],
                attempts=attempts,
            )
            receipt_errors, _ = checker._validate_execution_receipt(
                fixture_root,
                receipt,
                "test",
                {profile["profile_id"]: profile},
                bundle_reference["sha256"],
                validators,
            )
            self.assertTrue(
                any("call_id values must be unique" in error for error in receipt_errors),
                receipt_errors,
            )

    def _materiality_record(self, fixture_root: Path) -> tuple[dict, dict, dict]:
        record = make_review(fixture_root, findings=[finding(material=False)])
        challenge = record["findings"][0]["materiality"]["challenge"]
        return record, record["findings"][0], challenge

    def _refutation_record(self, fixture_root: Path) -> tuple[dict, dict, dict]:
        record = make_review(
            fixture_root,
            findings=[finding(status="refuted", disposition=refuted_disposition())],
        )
        attach_challenge(fixture_root, record, record["findings"][0])
        challenge = record["findings"][0]["disposition"]["challenge"]
        return record, record["findings"][0], challenge

    def test_materiality_challenge_requires_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(fixture_root, findings=[finding(material=False)])
            del record["findings"][0]["materiality"]["challenge"]["packet"]
            self.assertTrue(review_schema_errors(fixture_root, record))

    def test_refutation_challenge_requires_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[finding(status="refuted", disposition=refuted_disposition())],
            )
            attach_challenge(fixture_root, record, record["findings"][0])
            del record["findings"][0]["disposition"]["challenge"]["packet"]
            self.assertTrue(review_schema_errors(fixture_root, record))

    def test_challenge_packet_must_be_canonical_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._materiality_record(fixture_root)
            packet_payload = json.loads(
                (fixture_root / challenge["packet"]["path"]).read_text(
                    encoding="utf-8"
                )
            )
            reference = write_bytes_artifact(
                fixture_root,
                "formal/reviews/challenge-packets/not-canonical.json",
                json.dumps(packet_payload, indent=2).encode("utf-8"),
            )
            challenge["packet"] = reference
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "canonical JSON document serialization" in error
                    for error in errors
                ),
                errors,
            )

    def test_challenge_packet_hash_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._materiality_record(fixture_root)
            reference = dict(challenge["packet"])
            reference["sha256"] = "0" * 64
            challenge["packet"] = reference
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("artifact sha256 does not match" in error for error in errors),
                errors,
            )

    def test_challenge_packet_embedded_review_packet_sha_mismatch_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._materiality_record(fixture_root)

            def mutate(payload: dict) -> None:
                payload["review_packet"]["sha256"] = "0" * 64

            reference = _mutated_challenge_packet(
                fixture_root,
                challenge["packet"],
                mutate,
                "materiality-embedded-sha",
            )
            challenge["packet"] = reference
            _rewrite_challenge_receipt_packet(
                fixture_root, record, challenge, reference, "materiality-embedded-sha"
            )
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "embedded review packet sha256 must equal" in error
                    for error in errors
                ),
                errors,
            )

    def test_challenge_packet_embedded_review_packet_payload_mismatch_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._materiality_record(fixture_root)

            def mutate(payload: dict) -> None:
                payload["review_packet"]["payload"] = dict(
                    payload["review_packet"]["payload"],
                    unexpected_authority="injected",
                )

            reference = _mutated_challenge_packet(
                fixture_root,
                challenge["packet"],
                mutate,
                "materiality-embedded-payload",
            )
            challenge["packet"] = reference
            _rewrite_challenge_receipt_packet(
                fixture_root,
                record,
                challenge,
                reference,
                "materiality-embedded-payload",
            )
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "embedded review packet payload must equal the exact campaign "
                    "review packet" in error
                    for error in errors
                ),
                errors,
            )

    def test_materiality_challenge_packet_subject_payload_mismatch_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._materiality_record(fixture_root)
            reference = _mutated_challenge_packet(
                fixture_root,
                challenge["packet"],
                lambda payload: self._inject_subject(payload),
                "materiality-subject-payload",
            )
            challenge["packet"] = reference
            _rewrite_challenge_receipt_packet(
                fixture_root,
                record,
                challenge,
                reference,
                "materiality-subject-payload",
            )
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "subject payload does not equal exact challenged candidate"
                    in error
                    for error in errors
                ),
                errors,
            )

    @staticmethod
    def _inject_subject(payload: dict) -> None:
        mutated = dict(payload["challenge_subject"]["payload"], injected="x")
        payload["challenge_subject"]["payload"] = mutated
        payload["challenge_subject"]["sha256"] = checker.sha256_hex(
            checker._canonical_json_bytes(mutated)
        )

    def test_materiality_challenge_packet_subject_sha_mismatch_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._materiality_record(fixture_root)
            reference = _mutated_challenge_packet(
                fixture_root,
                challenge["packet"],
                lambda payload: payload["challenge_subject"].__setitem__(
                    "sha256", "0" * 64
                ),
                "materiality-subject-sha",
            )
            challenge["packet"] = reference
            _rewrite_challenge_receipt_packet(
                fixture_root,
                record,
                challenge,
                reference,
                "materiality-subject-sha",
            )
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "subject sha256 does not equal exact challenged candidate"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_materiality_challenge_packet_required_objectives_mismatch_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._materiality_record(fixture_root)
            reference = _mutated_challenge_packet(
                fixture_root,
                challenge["packet"],
                lambda payload: payload.__setitem__(
                    "required_objectives", payload["required_objectives"][:-1]
                ),
                "materiality-objectives",
            )
            challenge["packet"] = reference
            _rewrite_challenge_receipt_packet(
                fixture_root, record, challenge, reference, "materiality-objectives"
            )
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "required_objectives must equal the exact required objectives"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_refutation_challenge_packet_subject_payload_mismatch_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._refutation_record(fixture_root)
            reference = _mutated_challenge_packet(
                fixture_root,
                challenge["packet"],
                lambda payload: self._inject_subject(payload),
                "refutation-subject-payload",
            )
            challenge["packet"] = reference
            _rewrite_challenge_receipt_packet(
                fixture_root,
                record,
                challenge,
                reference,
                "refutation-subject-payload",
            )
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "subject payload does not equal exact challenged candidate"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_refutation_challenge_packet_subject_sha_mismatch_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._refutation_record(fixture_root)
            reference = _mutated_challenge_packet(
                fixture_root,
                challenge["packet"],
                lambda payload: payload["challenge_subject"].__setitem__(
                    "sha256", "0" * 64
                ),
                "refutation-subject-sha",
            )
            challenge["packet"] = reference
            _rewrite_challenge_receipt_packet(
                fixture_root, record, challenge, reference, "refutation-subject-sha"
            )
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "subject sha256 does not equal exact challenged candidate"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_refutation_challenge_packet_required_objectives_mismatch_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._refutation_record(fixture_root)
            reference = _mutated_challenge_packet(
                fixture_root,
                challenge["packet"],
                lambda payload: payload.__setitem__(
                    "required_objectives", payload["required_objectives"][:-1]
                ),
                "refutation-objectives",
            )
            challenge["packet"] = reference
            _rewrite_challenge_receipt_packet(
                fixture_root, record, challenge, reference, "refutation-objectives"
            )
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "required_objectives must equal the exact required objectives"
                    in error
                    for error in errors
                ),
                errors,
            )

    def _other_canonical_challenge_packet(
        self, fixture_root: Path, challenge: dict, name: str
    ) -> dict:
        return _mutated_challenge_packet(
            fixture_root,
            challenge["packet"],
            lambda payload: self._inject_subject(payload),
            name,
        )

    def test_materiality_challenge_receipt_packet_must_equal_challenge_packet(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._materiality_record(fixture_root)
            other_reference = self._other_canonical_challenge_packet(
                fixture_root, challenge, "materiality-other-packet"
            )
            _rewrite_challenge_receipt_packet(
                fixture_root,
                record,
                challenge,
                other_reference,
                "materiality-other-receipt",
            )
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "materiality challenge receipt packet must equal the challenge "
                    "packet" in error
                    for error in errors
                ),
                errors,
            )

    def test_refutation_challenge_receipt_packet_must_equal_challenge_packet(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._refutation_record(fixture_root)
            other_reference = self._other_canonical_challenge_packet(
                fixture_root, challenge, "refutation-other-packet"
            )
            _rewrite_challenge_receipt_packet(
                fixture_root,
                record,
                challenge,
                other_reference,
                "refutation-other-receipt",
            )
            write_review(fixture_root, record)
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "refutation challenge receipt packet must equal the challenge "
                    "packet" in error
                    for error in errors
                ),
                errors,
            )

    def test_valid_challenge_output_cannot_be_declared_protocol_invalid(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._refutation_record(fixture_root)
            output_reference = dict(challenge["output"])
            second_output_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/challenges/refutation-second-qualified.json",
                json.loads(
                    (fixture_root / output_reference["path"]).read_text(
                        encoding="utf-8"
                    )
                ),
            )
            _rewrite_challenge_receipt_attempts(
                fixture_root,
                record,
                challenge,
                [
                    attempt_payload(
                        "ATTEMPT-1",
                        outcome="protocol-invalid",
                        provider_model="1",
                        raw_output=output_reference,
                        protocol_errors=["claimed"],
                    ),
                    attempt_payload("ATTEMPT-2", raw_output=second_output_reference),
                ],
                "challenge-refutation-cherry",
            )
            challenge["output"] = second_output_reference
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "declared protocol-invalid but output is protocol-valid" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_protocol_invalid_challenge_output_can_precede_qualified_output(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._refutation_record(fixture_root)
            invalid_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/challenges/refutation-invalid-attempt.json",
                {
                    "challenge_output_schema_version": "1.0",
                    "challenge_kind": "refutation",
                    "objective_assessments": [],
                    "objections": [],
                },
            )
            _rewrite_challenge_receipt_attempts(
                fixture_root,
                record,
                challenge,
                [
                    attempt_payload(
                        "ATTEMPT-1",
                        outcome="protocol-invalid",
                        provider_model="1",
                        raw_output=invalid_reference,
                        protocol_errors=["objective-coverage"],
                    ),
                    attempt_payload(
                        "ATTEMPT-2", raw_output=dict(challenge["output"])
                    ),
                ],
                "challenge-refutation-retry",
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertEqual([], errors)
            self.assertTrue(summary["gate_a"]["ready"])

    def test_challenge_qualified_output_must_match_packet_kind(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[finding(status="refuted", disposition=refuted_disposition())],
            )
            custom_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/challenges/refutation-wrong-kind.json",
                challenge_output_payload(
                    "materiality", checker.REFUTATION_CHALLENGE_OBJECTIVES
                ),
            )
            attach_challenge(
                fixture_root,
                record,
                record["findings"][0],
                output=custom_reference,
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "challenge output challenge_kind must be refutation" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_challenge_qualified_output_must_cover_packet_required_objectives(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record = make_review(
                fixture_root,
                findings=[finding(status="refuted", disposition=refuted_disposition())],
            )
            custom_reference = write_json_artifact(
                fixture_root,
                "formal/reviews/challenges/refutation-missing-objective.json",
                challenge_output_payload(
                    "refutation", checker.REFUTATION_CHALLENGE_OBJECTIVES[:-1]
                ),
            )
            attach_challenge(
                fixture_root,
                record,
                record["findings"][0],
                output=custom_reference,
            )
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "objective assessments must cover exactly 7 required objectives "
                    "once each" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_challenge_must_be_separate_receipt_with_role_challenge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            record, _finding, challenge = self._refutation_record(fixture_root)
            receipt_reference = challenge["execution_receipt"]
            payload = json.loads(
                (fixture_root / receipt_reference["path"]).read_text(
                    encoding="utf-8"
                )
            )
            payload["role"] = "materiality-assessor"
            new_reference = write_receipt_payload(
                fixture_root, payload, "refutation-wrong-role"
            )
            _replace_supporting_receipt(record, receipt_reference, new_reference)
            challenge["execution_receipt"] = new_reference
            write_review(fixture_root, record)
            errors, summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "refutation challenge receipt role must be challenge" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(summary["gate_a"]["ready"])

    def test_protocol_v2_missing_predecessor_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            payload = bundle_document(fixture_root)
            payload.pop("predecessor", None)
            _install_manifest_bundle(
                fixture_root,
                payload,
                "formal/reviews/protocols/v2-missing-predecessor.json",
            )
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("predecessor" in error for error in errors), errors
            )

    def test_protocol_predecessor_hash_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            payload = bundle_document(fixture_root)
            payload["predecessor"] = {
                "path": "formal/reviews/protocols/gate-a-campaign-protocol-v1.json",
                "sha256": "0" * 64,
            }
            _install_manifest_bundle(
                fixture_root,
                payload,
                "formal/reviews/protocols/v2-bad-predecessor.json",
            )
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any("artifact sha256 does not match" in error for error in errors),
                errors,
            )

    def test_protocol_predecessor_cycle_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            reference = current_protocol_bundle_reference(fixture_root)
            validator, errors = checker._load_schema_validator(
                ROOT, checker.PROTOCOL_BUNDLE_SCHEMA_RELATIVE
            )
            self.assertEqual([], errors)
            # A hash-valid self-referential cycle is unsatisfiable by content
            # addressing, so the guard is exercised with seeded chain state.
            _, cycle_errors = checker._load_protocol_bundle_document(
                fixture_root,
                reference,
                "cycle",
                validator,
                {},
                {reference["path"]},
                set(),
            )
            self.assertTrue(
                any(
                    "protocol predecessor cycle" in error
                    for error in cycle_errors
                ),
                cycle_errors,
            )

    def test_protocol_predecessor_duplicate_protocol_id_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            payload = bundle_document(fixture_root)
            bundle_b = dict(payload)
            bundle_b["protocol_id"] = "duplicate-protocol-id"
            bundle_b["predecessor"] = {
                "path": "formal/reviews/protocols/gate-a-campaign-protocol-v1.json",
                "sha256": (
                    "156d6247907f17b49802b7953ef866bdd6e07c2b3f40b01c45f6077bd8498cc1"
                ),
            }
            reference_b = write_json_artifact(
                fixture_root,
                "formal/reviews/protocols/duplicate-b.json",
                bundle_b,
            )
            bundle_a = dict(payload)
            bundle_a["protocol_id"] = "duplicate-protocol-id"
            bundle_a["predecessor"] = reference_b
            _install_manifest_bundle(
                fixture_root,
                bundle_a,
                "formal/reviews/protocols/duplicate-a.json",
            )
            errors, _summary = checker.collect_errors(
                fixture_root, check_generated=False
            )
            self.assertTrue(
                any(
                    "duplicate protocol_id in predecessor chain" in error
                    for error in errors
                ),
                errors,
            )

    def test_protocol_v1_still_validates_unchanged_under_bundle_schema(
        self,
    ) -> None:
        validator, errors = checker._load_schema_validator(
            ROOT, checker.PROTOCOL_BUNDLE_SCHEMA_RELATIVE
        )
        self.assertEqual([], errors)
        bundle = json.loads(
            (
                ROOT / "formal/reviews/protocols/gate-a-campaign-protocol-v1.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            [], checker._schema_violations(validator, bundle, "protocol-v1")
        )


def _install_manifest_bundle(
    fixture_root: Path, payload: dict, relative_path: str
) -> dict:
    reference = write_json_artifact(fixture_root, relative_path, payload)
    manifest = load_manifest(fixture_root)
    manifest["policy"]["hostile_review"]["current_protocol_bundle"] = reference
    save_manifest(fixture_root, manifest)
    return reference


def _replace_supporting_receipt(
    record: dict, old_reference: dict, new_reference: dict
) -> None:
    supporting = record.setdefault("supporting_executions", [])
    key = (old_reference.get("path"), old_reference.get("sha256"))
    for index, item in enumerate(supporting):
        if (item.get("path"), item.get("sha256")) == key:
            supporting[index] = new_reference
            return
    raise AssertionError("supporting receipt not found")


def _rewrite_challenge_receipt_packet(
    fixture_root: Path,
    record: dict,
    challenge: dict,
    packet_reference: dict,
    name: str,
) -> dict:
    receipt_reference = challenge["execution_receipt"]
    payload = json.loads(
        (fixture_root / receipt_reference["path"]).read_text(encoding="utf-8")
    )
    payload["input"]["packet"] = packet_reference
    new_reference = write_receipt_payload(fixture_root, payload, name)
    _replace_supporting_receipt(record, receipt_reference, new_reference)
    challenge["execution_receipt"] = new_reference
    return new_reference


def _rewrite_challenge_receipt_attempts(
    fixture_root: Path,
    record: dict,
    challenge: dict,
    attempts: list[dict],
    name: str,
) -> dict:
    receipt_reference = challenge["execution_receipt"]
    payload = json.loads(
        (fixture_root / receipt_reference["path"]).read_text(encoding="utf-8")
    )
    payload["attempts"] = attempts
    qualifying = next(
        attempt for attempt in attempts if attempt["outcome"] == "qualified"
    )
    payload["qualifying_attempt_id"] = qualifying["attempt_id"]
    if isinstance(payload.get("resolved_identity"), dict):
        payload["resolved_identity"]["evidence_attempt_id"] = qualifying[
            "attempt_id"
        ]
    new_reference = write_receipt_payload(fixture_root, payload, name)
    _replace_supporting_receipt(record, receipt_reference, new_reference)
    challenge["execution_receipt"] = new_reference
    return new_reference


def _mutated_challenge_packet(
    fixture_root: Path, reference: dict, mutate, name: str
) -> dict:
    payload = json.loads(
        (fixture_root / reference["path"]).read_text(encoding="utf-8")
    )
    mutate(payload)
    return write_json_artifact(
        fixture_root, f"formal/reviews/challenge-packets/{name}.json", payload
    )

if __name__ == "__main__":
    unittest.main()
