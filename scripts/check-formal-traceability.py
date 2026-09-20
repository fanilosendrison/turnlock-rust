#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]

MANIFEST_RELATIVE = Path("formal/verification.yaml")
MANIFEST_SCHEMA_RELATIVE = Path("formal/verification.schema.json")
MIGRATION_RELATIVE = Path("formal/migrations/verification-v2-to-v3-property-audit.yaml")
MAPPING_RELATIVE = Path("docs/formal/invariant-mapping.md")
MODEL_RELATIVE = Path("formal/Turnlock.tla")
REVIEW_DIRECTORY_RELATIVE = Path("formal/reviews")
REVIEW_SCHEMA_RELATIVE = Path("formal/reviews/review-evidence.schema.json")
RESULTS_DIRECTORY_RELATIVE = Path("formal/results")
TLC_SCHEMA_RELATIVE = Path("formal/tlc-result.schema.json")
SPEC_RELATIVE = Path("docs/specification/turnlock-spec.md")
ADR_DIRECTORY_RELATIVE = Path("docs/adr")

SPEC_HEADING = re.compile(r"^##\s+[^\n]*\b(TL-INV-\d{3})\b", re.M)
INVARIANT_ID = re.compile(r"^TL-INV-[0-9]{3}$")
CLAIM_ID = re.compile(r"^TL-CLAIM-[0-9]{3}$")
ADR_ID = re.compile(r"^ADR-[0-9]{3}$")

CLAIM_TOTAL = 83
CLAIM_ID_MIN = 1
CLAIM_ID_MAX = 83

LEGACY_SOURCE_COMMIT = "6d3c9851e0d66286280f8e49ebd8ed44da13d876"
LEGACY_SOURCE_SCHEMA_VERSION = 2
LEGACY_TARGET_SCHEMA_VERSION = 3
LEGACY_TOTAL = 50
LEGACY_CLASSIFICATIONS = {
    "required-assurance-claim-candidate": 48,
    "supporting-model-property-candidate": 2,
    "obsolete-or-misplaced-planning-artifact": 0,
}

REVIEW_SUFFIXES = {".json", ".yaml", ".yml"}
GATE_A_REVIEW_CLASS = "assurance-decomposition"
GATE_A_SUBJECT_SELECTOR = "gate-a-assurance-decomposition-v1"
GATE_A_BLOCKING_STATUSES = {"open", "routed", "resolved"}
GATE_A_ATTACK_OBJECTIVES = (
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
)
REVIEW_PACKET_PREFIX = "formal/reviews/packets/"
REVIEW_PACKET_SUFFIX = ".json"
REVIEW_PROMPT_PREFIX = "formal/reviews/prompts/"
REVIEW_PROMPT_SUFFIX = ".md"
REVIEW_RAW_OUTPUT_PREFIX = "formal/reviews/raw/"
REVIEW_RAW_OUTPUT_SUFFIX = ".json"
REVIEW_CHALLENGE_PREFIX = "formal/reviews/challenges/"
REVIEW_CHALLENGE_SUFFIX = ".json"
REVIEW_CHALLENGE_PACKET_PREFIX = "formal/reviews/challenge-packets/"
REVIEW_CHALLENGE_PACKET_SUFFIX = ".json"
REVIEW_PROTOCOLS_PREFIX = "formal/reviews/protocols/"
REVIEW_PROTOCOL_BUNDLE_SUFFIX = ".json"
REVIEW_SCHEMAS_PREFIX = "formal/reviews/schemas/"
REVIEW_EXECUTIONS_PREFIX = "formal/reviews/executions/"
REVIEW_EXECUTION_SUFFIX = ".json"
REVIEW_ADJUDICATIONS_PREFIX = "formal/reviews/adjudications/"
REVIEW_JSON_OUTPUT_SUFFIX = ".json"
REVIEW_ARTIFACT_PREFIXES = (
    REVIEW_PACKET_PREFIX,
    REVIEW_PROMPT_PREFIX,
    REVIEW_RAW_OUTPUT_PREFIX,
    REVIEW_CHALLENGE_PREFIX,
    REVIEW_CHALLENGE_PACKET_PREFIX,
    REVIEW_PROTOCOLS_PREFIX,
    REVIEW_SCHEMAS_PREFIX,
    REVIEW_EXECUTIONS_PREFIX,
    REVIEW_ADJUDICATIONS_PREFIX,
)
REVIEW_ARTIFACT_EXCLUDED_FILE_NAMES = (
    REVIEW_SCHEMA_RELATIVE.name,
    "review-protocol-bundle.schema.json",
)
PROTOCOL_BUNDLE_SCHEMA_RELATIVE = Path("formal/reviews/review-protocol-bundle.schema.json")
REFUTATION_CHALLENGE_SELECTOR = "hostile-refutation-challenge-v1"
REFUTATION_CHALLENGE_SUBJECT_SCHEMA_VERSION = 1
MATERIALITY_CHALLENGE_SELECTOR = "hostile-materiality-challenge-v1"
MATERIALITY_CHALLENGE_SUBJECT_SCHEMA_VERSION = 1
FINDING_SUBJECT_SELECTOR = "hostile-finding-subject-v1"
FINDING_SUBJECT_SCHEMA_VERSION = 1
REFUTATION_CHALLENGE_OBJECTIVES = (
    "attacked-premise-still-supported",
    "target-correctly-identified",
    "counterexample-remains-in-scope",
    "consequence-still-follows",
    "not-actually-already-accounted-for",
    "hidden-assumption-in-refutation",
    "alternative-authority-compatible-interpretation",
)
INITIAL_REVIEWER_ROLE = "initial-reviewer"
CHALLENGE_ROLE = "challenge"
DETERMINISTIC_PROTOCOL_VALIDATION_ROLES = {
    "initial-reviewer",
    "challenge",
}
ROLES_WITHOUT_DETERMINISTIC_OUTPUT_VALIDATOR = {
    "materiality-assessor",
    "refutation-builder",
    "discovery-classifier",
    "derivation-builder",
    "decision-necessity-challenger",
    "repair-synthesizer",
    "decision-projection",
}
MATERIALITY_AXES = (
    "authority_or_upstream_decision",
    "claim_structure",
    "normative_provenance",
    "modality_or_assurance_domain",
    "coverage_or_residual_assurance",
    "interaction_scope",
    "candidate_model_authorization",
)
FUTURE_EVIDENCE_NOTE = "NOT-APPLICABLE (candidate model absent)"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _canonical_json_document_bytes(value: object) -> bytes:
    return _canonical_json_bytes(value) + b"\n"


def concise_subprocess_failure(stderr: bytes, returncode: int) -> str:
    """Return one bounded diagnostic line instead of a full subprocess traceback."""
    text = stderr.decode("utf-8", errors="replace")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    detail = lines[-1][:500] if lines else ""
    return f"{detail} (exit {returncode})" if detail else f"exit {returncode}"


def _mapping(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def _sequence(value: object) -> list:
    return value if isinstance(value, list) else []


def _load_yaml(root: Path, relative: Path) -> tuple[object, list[str]]:
    path = root / relative
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        return None, [f"cannot read {relative.as_posix()}: {error}"]
    return data, []


def _load_json(root: Path, relative: Path) -> tuple[object, list[str]]:
    path = root / relative
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return None, [f"cannot read {relative.as_posix()}: {error}"]
    return data, []


def _validator(schema: object) -> tuple[Draft202012Validator | None, list[str]]:
    if not isinstance(schema, dict):
        return None, ["schema must be a JSON object"]
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        return None, [f"schema is invalid: {error.message}"]
    return Draft202012Validator(schema, format_checker=FormatChecker()), []


def _schema_violations(
    validator: Draft202012Validator, instance: object, label: str
) -> list[str]:
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: (str(error.json_path), error.message),
    )
    return [f"{label}: schema {error.json_path}: {error.message}" for error in errors]


def _manifest_schema_errors(root: Path, manifest: object) -> list[str]:
    schema, errors = _load_json(root, MANIFEST_SCHEMA_RELATIVE)
    if errors:
        return errors
    validator, validator_errors = _validator(schema)
    if validator is None:
        return [f"{MANIFEST_SCHEMA_RELATIVE.as_posix()}: {error}" for error in validator_errors]
    return _schema_violations(validator, manifest, MANIFEST_RELATIVE.as_posix())


def _spec_invariant_ids(root: Path) -> tuple[list[str], list[str]]:
    path = root / SPEC_RELATIVE
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return [], [f"cannot read {SPEC_RELATIVE.as_posix()}: {error}"]
    return SPEC_HEADING.findall(text), []


def _authority_errors(root: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    authority = _mapping(manifest.get("authority"))
    normative_spec = authority.get("normative_spec")
    if isinstance(normative_spec, str) and normative_spec:
        if not (root / normative_spec).exists():
            errors.append(f"authority.normative_spec does not exist: {normative_spec}")
    adr_ids = []
    for key in ("architecture_decisions", "abstraction_constraints"):
        for value in _sequence(authority.get(key)):
            if isinstance(value, str):
                adr_ids.append(value)
    for adr_id in sorted(set(adr_ids)):
        if not ADR_ID.fullmatch(adr_id):
            continue
        number = adr_id.split("-")[1]
        if not list((root / ADR_DIRECTORY_RELATIVE).glob(f"adr-{number}-*.md")):
            errors.append(f"authority references missing {adr_id}")
    return errors


def _migration_errors(root: Path, claim_ids: set[str]) -> list[str]:
    data, errors = _load_yaml(root, MIGRATION_RELATIVE)
    if errors:
        return errors
    if not isinstance(data, dict):
        return [f"{MIGRATION_RELATIVE.as_posix()} must be a mapping"]

    label = MIGRATION_RELATIVE.as_posix()
    if data.get("schema_version") != 1:
        errors.append(f"{label} must use schema_version 1")

    source = _mapping(data.get("source"))
    if source.get("manifest") != MANIFEST_RELATIVE.as_posix():
        errors.append(f"{label} source.manifest must be {MANIFEST_RELATIVE.as_posix()}")
    if source.get("schema_version") != LEGACY_SOURCE_SCHEMA_VERSION:
        errors.append(f"{label} source.schema_version must be {LEGACY_SOURCE_SCHEMA_VERSION}")
    if source.get("repository_commit") != LEGACY_SOURCE_COMMIT:
        errors.append(f"{label} source.repository_commit must be {LEGACY_SOURCE_COMMIT}")

    target = _mapping(data.get("target"))
    if target.get("schema_version") != LEGACY_TARGET_SCHEMA_VERSION:
        errors.append(f"{label} target.schema_version must be {LEGACY_TARGET_SCHEMA_VERSION}")

    entries = data.get("entries")
    if not isinstance(entries, list):
        return errors + [f"{label} entries must be a list"]
    if len(entries) != LEGACY_TOTAL:
        errors.append(
            f"{label} must contain exactly {LEGACY_TOTAL} entries; found {len(entries)}"
        )

    counts: Counter[str] = Counter()
    seen: set[tuple[str, str]] = set()
    for index, entry in enumerate(entries):
        entry_label = f"{label} entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{entry_label} must be a mapping")
            continue
        missing = {
            "source_invariant",
            "legacy_property",
            "classification",
            "migrated_to",
        } - set(entry)
        if missing:
            errors.append(f"{entry_label} missing fields: {', '.join(sorted(missing))}")
            continue
        if set(entry) != {
            "source_invariant",
            "legacy_property",
            "classification",
            "migrated_to",
        }:
            errors.append(f"{entry_label} must contain exactly the four declared fields")
        source_invariant = entry.get("source_invariant")
        legacy_property = entry.get("legacy_property")
        classification = entry.get("classification")
        migrated_to = entry.get("migrated_to")
        if not isinstance(source_invariant, str) or not INVARIANT_ID.fullmatch(source_invariant):
            errors.append(f"{entry_label} source_invariant must match TL-INV-NNN")
        if not isinstance(legacy_property, str) or not legacy_property:
            errors.append(f"{entry_label} legacy_property must be a non-empty string")
        if classification not in LEGACY_CLASSIFICATIONS:
            errors.append(f"{entry_label} has unknown classification {classification!r}")
        else:
            counts[classification] += 1
        if not isinstance(migrated_to, list) or any(
            not isinstance(item, str) or not CLAIM_ID.fullmatch(item)
            for item in migrated_to
        ):
            errors.append(f"{entry_label} migrated_to must be a list of TL-CLAIM-NNN IDs")
            continue
        for claim_id in migrated_to:
            if claim_id not in claim_ids:
                errors.append(f"{entry_label} migrated_to references unknown {claim_id}")
        if isinstance(source_invariant, str) and isinstance(legacy_property, str):
            pair = (source_invariant, legacy_property)
            if pair in seen:
                errors.append(f"{entry_label} duplicates legacy property {legacy_property}")
            seen.add(pair)

    if len(entries) == LEGACY_TOTAL:
        for classification, expected in sorted(LEGACY_CLASSIFICATIONS.items()):
            found = counts.get(classification, 0)
            if found != expected:
                errors.append(
                    f"{label} requires exactly {expected} {classification} entries; found {found}"
                )
    return errors


def load_review_records(root: Path) -> tuple[list[tuple[Path, dict]], list[str]]:
    """Load review evidence records, failing closed on malformed evidence."""
    directory = root / REVIEW_DIRECTORY_RELATIVE
    records: list[tuple[Path, dict]] = []
    errors: list[str] = []
    if not directory.is_dir():
        return records, errors
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        if path.name in REVIEW_ARTIFACT_EXCLUDED_FILE_NAMES:
            continue
        label = path.relative_to(root).as_posix()
        if any(label.startswith(prefix) for prefix in REVIEW_ARTIFACT_PREFIXES):
            continue
        suffix = path.suffix.lower()
        if suffix not in REVIEW_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(
                f"{label}: cannot parse review evidence: {_concise_parser_error(error)}"
            )
            continue
        try:
            if suffix == ".json":
                data = json.loads(text)
            else:
                data = yaml.safe_load(text)
        except (json.JSONDecodeError, yaml.YAMLError) as error:
            errors.append(
                f"{label}: cannot parse review evidence: {_concise_parser_error(error)}"
            )
            continue
        if not isinstance(data, dict):
            errors.append(f"{label}: review evidence must be a mapping")
            continue
        records.append((path, data))
    return records, errors


def _finding_is_material(finding: dict) -> bool:
    """Derive materiality from the declared impact axes only."""
    materiality = _mapping(finding.get("materiality"))
    return any(materiality.get(axis) is True for axis in MATERIALITY_AXES)


def _read_review_artifact(
    root: Path,
    reference: object,
    label: str,
    prefix: str,
    suffix: str,
) -> tuple[bytes | None, list[str]]:
    """Read a review artifact reached through a direct non-symlink path."""
    artifact = _mapping(reference)
    raw_path = artifact.get("path")
    expected_sha = artifact.get("sha256")
    if not isinstance(raw_path, str) or not raw_path:
        return None, [f"{label}: artifact path must be a non-empty string"]
    path = Path(raw_path)
    if path.is_absolute():
        return None, [f"{label}: artifact path must be repository-relative: {raw_path}"]
    if ".." in path.parts:
        return None, [f"{label}: artifact path must not contain '..': {raw_path}"]
    normalized = path.as_posix()
    if not normalized.startswith(prefix):
        return None, [f"{label}: artifact path must be under {prefix}: {raw_path}"]
    if not normalized.endswith(suffix):
        return None, [f"{label}: artifact path must use the {suffix} suffix: {raw_path}"]

    root_resolved = root.resolve()
    target = root_resolved
    for part in path.parts:
        target = target / part
        if target.is_symlink():
            return None, [
                f"{label}: artifact path must not traverse symlinks: {raw_path}"
            ]

    if not target.exists():
        return None, [f"{label}: artifact does not exist: {raw_path}"]
    if not target.is_file():
        return None, [f"{label}: artifact is not a regular file: {raw_path}"]

    allowed_directory = (root_resolved / prefix.rstrip("/")).resolve()
    try:
        resolved_target = target.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        return None, [f"{label}: artifact cannot be resolved: {raw_path} ({error})"]
    for container in (root_resolved, allowed_directory):
        try:
            resolved_target.relative_to(container)
        except ValueError:
            return None, [
                f"{label}: artifact resolved path escapes allowed directory: {raw_path}"
            ]

    try:
        data = target.read_bytes()
    except OSError as error:
        return None, [f"{label}: cannot read artifact {raw_path}: {error}"]
    if expected_sha != sha256_hex(data):
        return None, [f"{label}: artifact sha256 does not match {raw_path}"]
    return data, []


def _gate_a_review_packet_authority_errors(
    packet: dict,
    subject_payload: dict,
    label: str,
) -> list[str]:
    """Validate embedded authority contents against the reviewed subject payload."""
    errors: list[str] = []
    authority = _mapping(subject_payload.get("authority"))

    expected_metadata: list[dict] = []
    normative_spec = authority.get("normative_spec")
    if isinstance(normative_spec, dict):
        expected_metadata.append(
            {
                "role": "normative-spec",
                "id": None,
                "path": normative_spec.get("path"),
                "sha256": normative_spec.get("sha256"),
            }
        )
    for relation, role in (
        ("architecture_decisions", "architecture-decision"),
        ("abstraction_constraints", "abstraction-constraint"),
    ):
        descriptors = [
            descriptor
            for descriptor in _sequence(authority.get(relation))
            if isinstance(descriptor, dict)
        ]
        descriptors.sort(key=lambda descriptor: str(descriptor.get("id", "")))
        for descriptor in descriptors:
            expected_metadata.append(
                {
                    "role": role,
                    "id": descriptor.get("id"),
                    "path": descriptor.get("path"),
                    "sha256": descriptor.get("sha256"),
                }
            )

    authority_contents = packet.get("authority_contents")
    if not isinstance(authority_contents, list):
        return [
            f"{label}: Gate A review packet authority contents do not match "
            "subject authority"
        ]
    if len(authority_contents) != len(expected_metadata):
        return [
            f"{label}: Gate A review packet authority contents do not match "
            "subject authority"
        ]

    expected_entry_keys = {"role", "id", "path", "sha256", "content_utf8"}
    for entry, expected in zip(authority_contents, expected_metadata):
        if not isinstance(entry, dict) or set(entry) != expected_entry_keys:
            errors.append(
                f"{label}: Gate A review packet authority contents do not match "
                "subject authority"
            )
            continue
        actual = {key: entry.get(key) for key in ("role", "id", "path", "sha256")}
        if actual != expected:
            errors.append(
                f"{label}: Gate A review packet authority contents do not match "
                "subject authority"
            )
            continue
        content = entry.get("content_utf8")
        if not isinstance(content, str):
            errors.append(
                f"{label}: Gate A review packet authority contents do not match "
                "subject authority"
            )
            continue
        if sha256_hex(content.encode("utf-8")) != entry.get("sha256"):
            errors.append(
                f"{label}: Gate A review packet authority content sha256 mismatch"
            )
    return errors


def _gate_a_review_packet_errors(
    packet_bytes: bytes,
    record_gate_a_subject: dict,
    label: str,
) -> list[str]:
    """Validate a self-contained canonical Gate A review packet."""
    try:
        text = packet_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return [f"{label}: Gate A review packet must be valid UTF-8"]
    try:
        packet = json.loads(text)
    except json.JSONDecodeError:
        return [f"{label}: Gate A review packet must be valid JSON"]
    if not isinstance(packet, dict):
        return [f"{label}: Gate A review packet must be a JSON object"]

    errors: list[str] = []
    if packet_bytes != _canonical_json_document_bytes(packet):
        errors.append(
            f"{label}: Gate A review packet must use canonical JSON serialization"
        )

    expected_top_level_keys = {
        "packet_schema_version",
        "subject",
        "subject_payload",
        "authority_contents",
    }
    if set(packet) != expected_top_level_keys:
        errors.append(
            f"{label}: Gate A review packet must contain exactly "
            "packet_schema_version, subject, subject_payload, authority_contents"
        )
        return errors

    if packet.get("packet_schema_version") != 1:
        errors.append(
            f"{label}: Gate A review packet packet_schema_version must be 1"
        )

    subject = packet.get("subject")
    if not isinstance(subject, dict) or set(subject) != {
        "subject_type",
        "selector",
        "sha256",
    }:
        errors.append(
            f"{label}: Gate A review packet subject must contain exactly "
            "subject_type, selector, sha256"
        )
        return errors
    if subject.get("subject_type") != "derived":
        errors.append(
            f"{label}: Gate A review packet subject subject_type must be derived"
        )
    if subject.get("selector") != GATE_A_SUBJECT_SELECTOR:
        errors.append(
            f"{label}: Gate A review packet subject selector must be "
            f"{GATE_A_SUBJECT_SELECTOR}"
        )

    subject_payload = packet.get("subject_payload")
    if not isinstance(subject_payload, dict):
        errors.append(
            f"{label}: Gate A review packet subject_payload must be a JSON object"
        )
        return errors
    if subject_payload.get("subject_schema_version") != 1:
        errors.append(
            f"{label}: Gate A review packet subject_payload subject_schema_version "
            "must be 1"
        )
    if subject_payload.get("selector") != GATE_A_SUBJECT_SELECTOR:
        errors.append(
            f"{label}: Gate A review packet subject_payload selector must be "
            f"{GATE_A_SUBJECT_SELECTOR}"
        )

    expected_subject_sha = sha256_hex(_canonical_json_bytes(subject_payload))
    if subject.get("sha256") != expected_subject_sha:
        errors.append(
            f"{label}: Gate A review packet subject sha256 does not match "
            "subject_payload"
        )

    if subject != record_gate_a_subject:
        errors.append(
            f"{label}: Gate A review packet subject does not equal the review "
            "record's unique Gate A derived subject"
        )

    errors.extend(
        _gate_a_review_packet_authority_errors(packet, subject_payload, label)
    )
    return errors


def _materiality_payload(materiality: object) -> dict:
    """Return the canonical seven-axis materiality payload without metadata."""
    source = _mapping(materiality)
    payload = {axis: source.get(axis) is True for axis in MATERIALITY_AXES}
    rationale = source.get("rationale")
    if isinstance(rationale, str):
        payload["rationale"] = rationale
    return payload


def _sorted_finding_sources(finding: object) -> list[dict]:
    sources = [
        {
            "execution_id": source.get("execution_id"),
            "raw_finding_id": source.get("raw_finding_id"),
        }
        for source in _sequence(_mapping(finding).get("sources"))
        if isinstance(source, dict)
    ]
    sources.sort(
        key=lambda source: (
            str(source.get("execution_id", "")),
            str(source.get("raw_finding_id", "")),
        )
    )
    return sources


def _refutation_payload(disposition: object) -> dict:
    disposition = _mapping(disposition)
    return {
        "kind": disposition.get("kind"),
        "ground": disposition.get("ground"),
        "attacked_premise_or_inference": disposition.get("attacked_premise_or_inference"),
        "evidence_references": sorted(
            reference
            for reference in _sequence(disposition.get("evidence_references"))
            if isinstance(reference, str)
        ),
        "argument": disposition.get("argument"),
        "counterexample_disposition": disposition.get("counterexample_disposition"),
    }


def _refutation_challenge_subject_payload(finding: dict) -> dict:
    """Build the canonical refutation-challenge subject payload for a finding."""
    return {
        "subject_schema_version": REFUTATION_CHALLENGE_SUBJECT_SCHEMA_VERSION,
        "selector": REFUTATION_CHALLENGE_SELECTOR,
        "finding": {
            "finding_id": finding.get("finding_id"),
            "sources": _sorted_finding_sources(finding),
            "statement": finding.get("statement"),
            "argument": finding.get("argument"),
            "counterexample": finding.get("counterexample"),
            "materiality": _materiality_payload(finding.get("materiality")),
            "status": finding.get("status"),
            "refutation": _refutation_payload(finding.get("disposition")),
        },
    }


def _refutation_challenge_subject_sha256(finding: dict) -> str:
    """Hash the canonical refutation-challenge subject for a finding."""
    return sha256_hex(
        _canonical_json_bytes(_refutation_challenge_subject_payload(finding))
    )


def _re_adjudication_refutation_subject_payload(
    source_finding: dict, re_adjudication: dict
) -> dict:
    return {
        "subject_schema_version": REFUTATION_CHALLENGE_SUBJECT_SCHEMA_VERSION,
        "selector": REFUTATION_CHALLENGE_SELECTOR,
        "finding": {
            "finding_id": source_finding.get("finding_id"),
            "sources": _sorted_finding_sources(source_finding),
            "statement": source_finding.get("statement"),
            "argument": source_finding.get("argument"),
            "counterexample": source_finding.get("counterexample"),
            "materiality": _materiality_payload(re_adjudication.get("materiality")),
            "status": "refuted",
            "refutation": _refutation_payload(re_adjudication.get("disposition")),
        },
    }


def _re_adjudication_refutation_subject_sha256(
    source_finding: dict, re_adjudication: dict
) -> str:
    return sha256_hex(
        _canonical_json_bytes(
            _re_adjudication_refutation_subject_payload(source_finding, re_adjudication)
        )
    )


def _finding_subject_payload(finding: dict) -> dict:
    return {
        "subject_schema_version": FINDING_SUBJECT_SCHEMA_VERSION,
        "selector": FINDING_SUBJECT_SELECTOR,
        "finding": {
            "finding_id": finding.get("finding_id"),
            "sources": _sorted_finding_sources(finding),
            "statement": finding.get("statement"),
            "argument": finding.get("argument"),
            "counterexample": finding.get("counterexample"),
        },
    }


def _finding_subject_sha256(finding: dict) -> str:
    return sha256_hex(_canonical_json_bytes(_finding_subject_payload(finding)))


def _materiality_challenge_subject_payload(source: dict, materiality: object) -> dict:
    payload = _materiality_payload(materiality)
    return {
        "subject_schema_version": MATERIALITY_CHALLENGE_SUBJECT_SCHEMA_VERSION,
        "selector": MATERIALITY_CHALLENGE_SELECTOR,
        "finding": {
            "finding_id": source.get("finding_id"),
            "sources": _sorted_finding_sources(source),
            "statement": source.get("statement"),
            "argument": source.get("argument"),
            "counterexample": source.get("counterexample"),
            "candidate_materiality_axes": {
                axis: payload[axis] for axis in MATERIALITY_AXES
            },
            "candidate_materiality_rationale": payload.get("rationale"),
        },
    }


def _materiality_challenge_subject_sha256(source: dict, materiality: object) -> str:
    return sha256_hex(
        _canonical_json_bytes(
            _materiality_challenge_subject_payload(source, materiality)
        )
    )


def _load_json_object_artifact(
    root: Path,
    reference: object,
    label: str,
    prefix: str,
    suffix: str,
    *,
    require_canonical: bool,
) -> tuple[dict | None, list[str]]:
    data, errors = _read_review_artifact(root, reference, label, prefix, suffix)
    if data is None:
        return None, errors
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None, errors + [f"{label}: artifact must be valid UTF-8"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as error:
        return None, errors + [
            f"{label}: artifact must be valid JSON ({_concise_parser_error(error)})"
        ]
    if not isinstance(parsed, dict):
        return None, errors + [f"{label}: artifact must be a JSON object"]
    if require_canonical and data != _canonical_json_document_bytes(parsed):
        return None, errors + [
            f"{label}: artifact must use canonical JSON document serialization"
        ]
    return parsed, errors


def _load_schema_validator(
    root: Path, relative: Path
) -> tuple[Draft202012Validator | None, list[str]]:
    schema, errors = _load_json(root, relative)
    if errors:
        return None, errors
    validator, validator_errors = _validator(schema)
    if validator is None:
        return None, [f"{relative.as_posix()}: {error}" for error in validator_errors]
    return validator, []


def _protocol_profile_map(bundle: object) -> dict[str, dict]:
    profiles: dict[str, dict] = {}
    for profile in _sequence(_mapping(bundle).get("reviewer_profiles")):
        if not isinstance(profile, dict):
            continue
        profile_id = profile.get("profile_id")
        if isinstance(profile_id, str) and profile_id not in profiles:
            profiles[profile_id] = profile
    return profiles


def _protocol_bundle_errors(root: Path, bundle: dict, label: str) -> list[str]:
    """Validate every immutable artifact referenced by one bundle."""
    errors: list[str] = []
    prompts = _mapping(bundle.get("prompts"))
    for key in ("initial-reviewer", "adjudication", "challenge", "repair"):
        _, artifact_errors = _read_review_artifact(root, _mapping(prompts.get(key)), f"{label}: prompts.{key}", REVIEW_PROMPT_PREFIX, REVIEW_PROMPT_SUFFIX)
        errors.extend(artifact_errors)
    schemas = _mapping(bundle.get("schemas"))
    keys = ["raw-review-output", "execution-receipt", "challenge-output"]
    if bundle.get("protocol_bundle_schema_version") in (2, 3):
        keys.append("challenge-packet")
    for key in keys:
        data, artifact_errors = _read_review_artifact(root, _mapping(schemas.get(key)), f"{label}: schemas.{key}", REVIEW_SCHEMAS_PREFIX, REVIEW_JSON_OUTPUT_SUFFIX)
        errors.extend(artifact_errors)
        if data is not None:
            try:
                schema = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                errors.append(f"{label}: schemas.{key} must be valid JSON ({_concise_parser_error(error)})")
            else:
                _validator_value, schema_errors = _validator(schema)
                errors.extend(f"{label}: schemas.{key}: {error}" for error in schema_errors)
    profile_ids = [profile.get("profile_id") for profile in _sequence(bundle.get("reviewer_profiles")) if isinstance(profile, dict) and isinstance(profile.get("profile_id"), str)]
    for profile_id, count in Counter(profile_ids).items():
        if count > 1:
            errors.append(f"{label}: duplicate reviewer profile_id {profile_id!r}")
    return errors


def _bundle_selected_validators(root: Path, bundle: dict | None, label: str) -> tuple[dict[str, Draft202012Validator | None], list[str]]:
    validators: dict[str, Draft202012Validator | None] = {}
    errors: list[str] = []
    if bundle is None:
        return validators, errors
    schemas = _mapping(bundle.get("schemas"))
    for key in ("raw-review-output", "execution-receipt", "challenge-output", "challenge-packet"):
        ref = schemas.get(key)
        if ref is None:
            continue
        data, artifact_errors = _read_review_artifact(root, ref, f"{label}: schemas.{key}", REVIEW_SCHEMAS_PREFIX, REVIEW_JSON_OUTPUT_SUFFIX)
        errors.extend(artifact_errors)
        if data is None:
            continue
        try:
            schema = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            errors.append(f"{label}: schemas.{key} must be valid JSON ({_concise_parser_error(error)})")
            continue
        validator, validator_errors = _validator(schema)
        errors.extend(f"{label}: schemas.{key}: {error}" for error in validator_errors)
        validators[key] = validator
    return validators, errors


def _load_protocol_bundle_document(root: Path, reference: object, label: str, validator: Draft202012Validator | None, cache: dict[str, tuple[dict | None, list[str]]], chain_paths: set[str] | None = None, chain_ids: set[str] | None = None) -> tuple[dict | None, list[str]]:
    bundle_reference = _mapping(reference)
    cache_key = bundle_reference.get("sha256")
    # Cache only fully checked acyclic chains.
    if chain_paths is None and isinstance(cache_key, str) and cache_key in cache:
        return cache[cache_key]
    bundle, errors = _load_json_object_artifact(root, bundle_reference, label, REVIEW_PROTOCOLS_PREFIX, REVIEW_PROTOCOL_BUNDLE_SUFFIX, require_canonical=True)
    if bundle is None:
        return None, errors
    if validator is not None:
        errors.extend(_schema_violations(validator, bundle, label))
    errors.extend(_protocol_bundle_errors(root, bundle, label))
    path = _mapping(reference).get("path")
    protocol_id = bundle.get("protocol_id")
    paths = set(chain_paths or ())
    ids = set(chain_ids or ())
    if isinstance(path, str) and path in paths:
        errors.append(f"{label}: protocol predecessor cycle or duplicate bundle path")
        return bundle, errors
    if isinstance(protocol_id, str) and protocol_id in ids:
        errors.append(f"{label}: duplicate protocol_id in predecessor chain {protocol_id!r}")
        return bundle, errors
    if isinstance(path, str): paths.add(path)
    if isinstance(protocol_id, str): ids.add(protocol_id)
    version = bundle.get("protocol_bundle_schema_version")
    predecessor = bundle.get("predecessor")
    if version in (2, 3):
        if not isinstance(predecessor, dict):
            errors.append(f"{label}: schema-version-{version} bundle requires predecessor")
        else:
            _, predecessor_errors = _load_protocol_bundle_document(root, predecessor, f"{label}: predecessor", validator, cache, paths, ids)
            errors.extend(predecessor_errors)
    elif predecessor is not None:
        errors.append(f"{label}: schema-version-1 bundle must not declare predecessor")
    if chain_paths is None and isinstance(cache_key, str):
        cache[cache_key] = (bundle, list(errors))
    return bundle, errors


def _current_protocol_bundle_errors(root: Path, manifest: dict, validator: Draft202012Validator | None, cache: dict[str, tuple[dict | None, list[str]]]) -> tuple[object, dict | None, list[str]]:
    hostile_review = _mapping(_mapping(manifest.get("policy")).get("hostile_review"))
    reference = _mapping(hostile_review.get("current_protocol_bundle"))
    label = "policy.hostile_review.current_protocol_bundle"
    bundle, errors = _load_protocol_bundle_document(root, reference, label, validator, cache)
    # v2 establishes the fixed v1 lineage root.
    if bundle is not None and bundle.get("protocol_bundle_schema_version") == 2:
        predecessor = _mapping(bundle.get("predecessor"))
        if predecessor.get("path") != "formal/reviews/protocols/gate-a-campaign-protocol-v1.json" or predecessor.get("sha256") != "156d6247907f17b49802b7953ef866bdd6e07c2b3f40b01c45f6077bd8498cc1":
            errors.append(f"{label}: current protocol v2 predecessor must be the exact published v1 bundle")
    # v3 establishes the fixed v2 lineage.
    if bundle is not None and bundle.get("protocol_bundle_schema_version") == 3:
        predecessor = _mapping(bundle.get("predecessor"))
        if predecessor.get("path") != "formal/reviews/protocols/gate-a-campaign-protocol-v2.json" or predecessor.get("sha256") != "ba64ac934bee21ae3e4f31b8381c5289c56fde0a45e25d660c3ef7c6f715d6d9":
            errors.append(f"{label}: current protocol v3 predecessor must be the exact published v2 bundle")
    return reference, bundle, errors

def _load_execution_receipt(
    root: Path,
    reference: object,
    label: str,
    validator: Draft202012Validator | None,
) -> tuple[dict | None, list[str]]:
    receipt, errors = _load_json_object_artifact(
        root,
        reference,
        label,
        REVIEW_EXECUTIONS_PREFIX,
        REVIEW_EXECUTION_SUFFIX,
        require_canonical=True,
    )
    if receipt is not None and validator is not None:
        errors.extend(_schema_violations(validator, receipt, label))
    return receipt, errors


RECEIPT_ROLE_OUTPUT_PREFIXES = {
    INITIAL_REVIEWER_ROLE: (REVIEW_RAW_OUTPUT_PREFIX,),
    CHALLENGE_ROLE: (REVIEW_CHALLENGE_PREFIX,),
}
RECEIPT_DEFAULT_OUTPUT_PREFIXES = (
    REVIEW_RAW_OUTPUT_PREFIX,
    REVIEW_CHALLENGE_PREFIX,
    REVIEW_ADJUDICATIONS_PREFIX,
)


def _receipt_output_prefixes(role: object) -> tuple[str, ...]:
    return RECEIPT_ROLE_OUTPUT_PREFIXES.get(role, RECEIPT_DEFAULT_OUTPUT_PREFIXES)


def _read_receipt_output(
    root: Path, reference: object, label: str, prefixes: tuple[str, ...]
) -> tuple[bytes | None, list[str]]:
    path = _mapping(reference).get("path")
    if not isinstance(path, str) or not path:
        return None, [f"{label}: attempt raw_output path must be a non-empty string"]
    for prefix in prefixes:
        if path.startswith(prefix):
            return _read_review_artifact(
                root, reference, label, prefix, REVIEW_JSON_OUTPUT_SUFFIX
            )
    return None, [
        f"{label}: attempt raw_output path is not an allowed sealed location: {path}"
    ]


def _validate_initial_reviewer_protocol_output(root: Path, reference: object, validator: Draft202012Validator | None, required_objectives: tuple[str, ...] = GATE_A_ATTACK_OBJECTIVES) -> tuple[dict | None, list[str]]:
    raw, errors = _load_json_object_artifact(root, reference, "initial-reviewer raw output", REVIEW_RAW_OUTPUT_PREFIX, REVIEW_RAW_OUTPUT_SUFFIX, require_canonical=False)
    if raw is None:
        return None, errors
    if validator is not None:
        errors.extend(_schema_violations(validator, raw, "initial-reviewer raw output"))
    findings: dict[str, dict] = {}
    for finding in _sequence(raw.get("findings")):
        if not isinstance(finding, dict) or not isinstance(finding.get("raw_finding_id"), str):
            continue
        raw_id=finding["raw_finding_id"]
        if raw_id in findings: errors.append(f"initial-reviewer raw output: duplicate raw_finding_id {raw_id!r}")
        findings[raw_id]=finding
    assessments=[x for x in _sequence(raw.get("objective_assessments")) if isinstance(x,dict)]
    objectives=[x.get("objective") for x in assessments if isinstance(x.get("objective"),str)]
    if len(assessments)!=len(required_objectives) or len(set(objectives))!=len(required_objectives) or set(objectives)!=set(required_objectives):
        errors.append("initial-reviewer raw output: raw output must assess exactly the 14 Gate A attack objectives once each")
    listed: dict[str,set[str]]={}
    for assessment in assessments:
        objective=assessment.get("objective")
        if not isinstance(objective,str): continue
        ids={x for x in _sequence(assessment.get("finding_ids")) if isinstance(x,str)}
        listed[objective]=ids
        for raw_id in ids:
            if raw_id not in findings: errors.append(f"initial-reviewer raw output: objective assessment {objective!r} references unknown raw finding {raw_id!r}")
    for raw_id,finding in findings.items():
        declared={x for x in _sequence(finding.get("attack_objectives")) if isinstance(x,str)}
        for objective in declared:
            if raw_id not in listed.get(objective,set()): errors.append(f"initial-reviewer raw output: raw finding {raw_id!r} declares objective {objective!r} that does not reference it reciprocally")
        for objective,ids in listed.items():
            if raw_id in ids and objective not in declared: errors.append(f"initial-reviewer raw output: objective assessment {objective!r} references raw finding {raw_id!r} that does not declare it")
    return raw,errors


def _validate_challenge_protocol_output(root: Path, reference: object, validator: Draft202012Validator | None, packet: dict | None) -> tuple[dict | None,list[str]]:
    output, errors = _load_json_object_artifact(root, reference, "challenge output", REVIEW_CHALLENGE_PREFIX, REVIEW_CHALLENGE_SUFFIX, require_canonical=False)
    if output is None: return None,errors
    if validator is not None: errors.extend(_schema_violations(validator,output,"challenge output"))
    if packet is None: return output, errors+["challenge output: canonical challenge packet is unavailable"]
    if output.get("challenge_kind") != packet.get("challenge_kind"): errors.append("challenge output: challenge_kind must equal the bound challenge packet")
    errors.extend(_challenge_objective_errors(output,"challenge output",tuple(_sequence(packet.get("required_objectives")))))
    errors.extend(_challenge_objection_errors(output,"challenge output"))
    return output,errors


def _load_challenge_packet(root: Path, reference: object, record_packet: dict | None, record_packet_ref: dict, validator: Draft202012Validator | None, label: str) -> tuple[dict | None,list[str]]:
    packet, errors = _load_json_object_artifact(root, reference, label, REVIEW_CHALLENGE_PACKET_PREFIX, REVIEW_CHALLENGE_PACKET_SUFFIX, require_canonical=True)
    if packet is None: return None,errors
    if validator is not None: errors.extend(_schema_violations(validator,packet,label))
    review=_mapping(packet.get("review_packet"))
    if review.get("sha256") != record_packet_ref.get("sha256"): errors.append(f"{label}: embedded review packet sha256 must equal record protocol review packet")
    if record_packet is not None and review.get("payload") != record_packet: errors.append(f"{label}: embedded review packet payload must equal the exact campaign review packet")
    if isinstance(review.get("payload"),dict):
        errors.extend(_gate_a_review_packet_authority_errors(review["payload"], _mapping(review["payload"].get("subject_payload")), label))
        expected=sha256_hex(_canonical_json_bytes(_mapping(packet.get("challenge_subject")).get("payload")))
        if _mapping(packet.get("challenge_subject")).get("sha256") != expected: errors.append(f"{label}: challenge_subject sha256 does not match payload")
    return packet,errors

def _unique_qualifying_attempt(receipt: dict) -> dict | None:
    qualified = [
        attempt
        for attempt in _sequence(receipt.get("attempts"))
        if isinstance(attempt, dict) and attempt.get("outcome") == "qualified"
    ]
    return qualified[0] if len(qualified) == 1 else None


def _validate_execution_receipt(root: Path, receipt: dict, label: str, profile_map: dict[str,dict], expected_bundle_sha256: object, validators: dict[str,Draft202012Validator | None] | None = None, challenge_packet: dict | None = None) -> tuple[list[str],dict|None]:
    errors: list[str]=[]; validators=validators or {}; role=receipt.get("role"); profile_id=receipt.get("reviewer_profile_id"); profile=profile_map.get(profile_id) if isinstance(profile_id,str) else None
    if profile is None: errors.append(f"{label}: receipt references unknown reviewer profile {profile_id!r}")
    else:
        if profile.get("frontier_eligible") is not True: errors.append(f"{label}: reviewer profile {profile_id!r} is not frontier eligible")
        request=_mapping(receipt.get("request"))
        if request.get("provider")!=profile.get("provider"): errors.append(f"{label}: receipt request provider does not match its reviewer profile")
        if request.get("model")!=profile.get("request_model"): errors.append(f"{label}: receipt request model does not match its reviewer profile request_model")
    if receipt.get("isolated_context") is not True: errors.append(f"{label}: receipt isolated_context must be true")
    if receipt.get("cross_reviewer_visibility_before_seal") is not False: errors.append(f"{label}: receipt cross_reviewer_visibility_before_seal must be false")
    if receipt.get("tools_enabled") is not False: errors.append(f"{label}: receipt tools_enabled must be false")
    if isinstance(expected_bundle_sha256,str) and receipt.get("protocol_bundle_sha256")!=expected_bundle_sha256: errors.append(f"{label}: receipt protocol_bundle_sha256 does not match the review protocol bundle")
    attempts=[a for a in _sequence(receipt.get("attempts")) if isinstance(a,dict)]
    for field in ("attempt_id","call_id"):
        values=[a.get(field) for a in attempts if isinstance(a.get(field),str)]
        if len(values)!=len(set(values)): errors.append(f"{label}: {field} values must be unique")
    qualified=[a for a in attempts if a.get("outcome")=="qualified"]
    if len(qualified)!=1: errors.append(f"{label}: exactly one attempt must have outcome qualified; found {len(qualified)}")
    qualifying=qualified[0] if len(qualified)==1 else None
    if qualifying is not None:
        if receipt.get("qualifying_attempt_id") != qualifying.get("attempt_id"): errors.append(f"{label}: qualifying_attempt_id must name the qualified attempt")
        if attempts and attempts[-1] is not qualifying: errors.append(f"{label}: the qualified attempt must be final")
    output_paths=[]
    for attempt in attempts:
        outcome=attempt.get("outcome"); raw=attempt.get("raw_output"); alabel=f"{label}: attempt {attempt.get('attempt_id')!r}"
        if outcome=="technical-failure":
            if raw is not None: errors.append(f"{alabel}: technical-failure must not have raw_output")
            if _sequence(attempt.get("protocol_errors")): errors.append(f"{alabel}: technical-failure must not have protocol_errors")
            continue
        if (
            receipt.get("receipt_schema_version") == "3.0"
            and role in ROLES_WITHOUT_DETERMINISTIC_OUTPUT_VALIDATOR
            and outcome == "protocol-invalid"
        ):
            errors.append(f"{alabel}: protocol-invalid is forbidden for roles without a deterministic output validator")
        if raw is None:
            errors.append(f"{alabel}: a completed {outcome} attempt must seal its raw output"); continue
        if outcome=="protocol-invalid" and not _sequence(attempt.get("protocol_errors")): errors.append(f"{alabel}: protocol-invalid attempt requires nonempty protocol_errors")
        if outcome=="qualified" and _sequence(attempt.get("protocol_errors")): errors.append(f"{alabel}: qualified attempt requires empty protocol_errors")
        _,read_errors=_read_receipt_output(root,raw,alabel,_receipt_output_prefixes(role));errors.extend(read_errors)
        path=_mapping(raw).get("path");
        if isinstance(path,str): output_paths.append(path)
        derived: list[str] | None = None
        if role==INITIAL_REVIEWER_ROLE: _parsed,derived=_validate_initial_reviewer_protocol_output(root,raw,validators.get("raw-review-output"))
        elif role==CHALLENGE_ROLE and challenge_packet is not None: _parsed,derived=_validate_challenge_protocol_output(root,raw,validators.get("challenge-output"),challenge_packet)
        if derived is not None:
            if outcome=="protocol-invalid" and not derived: errors.append(f"{alabel}: declared protocol-invalid but output is protocol-valid")
            if outcome=="qualified" and derived: errors.append(f"{alabel}: declared qualified but output is protocol-invalid")
    for path,count in Counter(output_paths).items():
        if count>1: errors.append(f"{label}: duplicate attempt raw_output path {path}")
    resolved=receipt.get("resolved_identity")
    if qualifying is not None:
        if not isinstance(resolved,dict): errors.append(f"{label}: a qualified attempt requires a resolved identity")
        else:
            if resolved.get("evidence_attempt_id")!=qualifying.get("attempt_id"): errors.append(f"{label}: resolved identity must reference the qualifying attempt")
            request=_mapping(receipt.get("request"))
            if resolved.get("provider")!=request.get("provider") or resolved.get("model")!=request.get("model"): errors.append(f"{label}: resolved identity provider/model must match the receipt request")
            if profile is not None:
                resolution=_mapping(profile.get("identity_resolution"));kind=resolution.get("kind")
                if resolved.get("resolution_kind")!=kind: errors.append(f"{label}: resolved identity resolution_kind must match the reviewer profile")
                if kind=="provider-reported":
                    if not isinstance(qualifying.get("provider_model"),str) or not qualifying.get("provider_model"): errors.append(f"{label}: provider-reported identity requires a non-empty provider_model")
                    elif resolved.get("model_version")!=qualifying.get("provider_model"): errors.append(f"{label}: provider-reported model_version must equal the qualified attempt provider_model")
                elif kind=="pinned-request-model":
                    if resolution.get("request_model_is_immutable_version") is not True: errors.append(f"{label}: pinned-request-model requires request_model_is_immutable_version = true")
                    if resolved.get("model_version")!=profile.get("request_model"): errors.append(f"{label}: pinned-request-model model_version must equal the profile request_model")
    return errors,qualifying

def _initial_reviewer_receipt_errors(
    record: dict,
    execution: dict,
    receipt: dict,
    qualifying_attempt: dict | None,
) -> list[str]:
    label = f"execution {execution.get('execution_id')!r} receipt"
    errors: list[str] = []
    if receipt.get("execution_id") != execution.get("execution_id"):
        errors.append(f"{label}: receipt execution_id must equal the execution record")
    if receipt.get("role") != INITIAL_REVIEWER_ROLE:
        errors.append(
            f"{label}: initial reviewer execution receipt role must be initial-reviewer"
        )
    if receipt.get("reviewer_profile_id") != execution.get("reviewer_profile_id"):
        errors.append(
            f"{label}: receipt reviewer profile must equal the execution reviewer profile"
        )
    request = _mapping(receipt.get("request"))
    if request.get("provider") != execution.get("provider") or request.get(
        "model"
    ) != execution.get("model"):
        errors.append(
            f"{label}: receipt request must match the execution provider and model"
        )
    resolved = _mapping(receipt.get("resolved_identity"))
    for field in ("provider", "model", "model_version"):
        if resolved.get(field) != execution.get(field):
            errors.append(
                f"{label}: resolved identity {field} must equal the execution "
                f"record {field}"
            )
    if receipt.get("isolated_context") is not execution.get("isolated_context"):
        errors.append(f"{label}: receipt isolation must agree with the execution record")
    if receipt.get("cross_reviewer_visibility_before_seal") is not execution.get(
        "cross_reviewer_visibility_before_seal"
    ):
        errors.append(
            f"{label}: receipt cross-reviewer visibility must agree with the execution "
            "record"
        )
    protocol = _mapping(record.get("protocol"))
    inputs = _mapping(receipt.get("input"))
    if inputs.get("prompt") != protocol.get("prompt"):
        errors.append(
            f"{label}: receipt prompt input must equal the record protocol prompt"
        )
    if inputs.get("packet") != protocol.get("review_packet"):
        errors.append(
            f"{label}: receipt packet input must equal the record protocol packet"
        )
    if qualifying_attempt is not None and qualifying_attempt.get(
        "raw_output"
    ) != execution.get("raw_output"):
        errors.append(
            f"{label}: qualifying attempt raw output must equal the execution raw_output"
        )
    return errors


def _raw_review_errors(
    root: Path,
    label: str,
    execution: dict,
    validator: Draft202012Validator | None,
) -> tuple[dict[str, dict] | None, list[str]]:
    raw, errors = _load_json_object_artifact(
        root,
        _mapping(execution.get("raw_output")),
        label,
        REVIEW_RAW_OUTPUT_PREFIX,
        REVIEW_RAW_OUTPUT_SUFFIX,
        require_canonical=False,
    )
    if raw is None:
        return None, errors
    if validator is not None:
        errors.extend(_schema_violations(validator, raw, label))

    raw_findings: dict[str, dict] = {}
    for raw_finding in _sequence(raw.get("findings")):
        if not isinstance(raw_finding, dict):
            continue
        raw_id = raw_finding.get("raw_finding_id")
        if not isinstance(raw_id, str):
            continue
        if raw_id in raw_findings:
            errors.append(f"{label}: duplicate raw_finding_id {raw_id!r}")
            continue
        raw_findings[raw_id] = raw_finding

    assessments = [
        assessment
        for assessment in _sequence(raw.get("objective_assessments"))
        if isinstance(assessment, dict)
    ]
    objectives = [
        assessment.get("objective")
        for assessment in assessments
        if isinstance(assessment.get("objective"), str)
    ]
    if (
        len(assessments) != len(GATE_A_ATTACK_OBJECTIVES)
        or len(set(objectives)) != len(GATE_A_ATTACK_OBJECTIVES)
        or set(objectives) != set(GATE_A_ATTACK_OBJECTIVES)
    ):
        errors.append(
            f"{label}: raw output must assess exactly the 14 Gate A attack "
            "objectives once each"
        )
    assessment_finding_ids: dict[str, list[str]] = {}
    for assessment in assessments:
        objective = assessment.get("objective")
        if not isinstance(objective, str):
            continue
        finding_ids = [
            raw_id
            for raw_id in _sequence(assessment.get("finding_ids"))
            if isinstance(raw_id, str)
        ]
        assessment_finding_ids[objective] = finding_ids
        for raw_id in finding_ids:
            if raw_id not in raw_findings:
                errors.append(
                    f"{label}: objective assessment {objective!r} references unknown "
                    f"raw finding {raw_id!r}"
                )

    for raw_id, raw_finding in sorted(raw_findings.items()):
        declared_objectives = {
            objective
            for objective in _sequence(raw_finding.get("attack_objectives"))
            if isinstance(objective, str)
        }
        for objective in sorted(declared_objectives):
            if raw_id not in assessment_finding_ids.get(objective, []):
                errors.append(
                    f"{label}: raw finding {raw_id!r} declares objective "
                    f"{objective!r} that does not reference it reciprocally"
                )
        for objective, finding_ids in sorted(assessment_finding_ids.items()):
            if raw_id in finding_ids and objective not in declared_objectives:
                errors.append(
                    f"{label}: objective assessment {objective!r} references raw "
                    f"finding {raw_id!r} that does not declare it"
                )

    execution_objectives = {
        objective
        for objective in _sequence(execution.get("attack_objectives"))
        if isinstance(objective, str)
    }
    if execution_objectives != set(objectives):
        errors.append(
            f"{label}: execution attack_objectives must equal the raw objective set"
        )
    execution_raw_ids = {
        raw_id
        for raw_id in _sequence(execution.get("raw_finding_ids"))
        if isinstance(raw_id, str)
    }
    if execution_raw_ids != set(raw_findings):
        errors.append(
            f"{label}: execution raw_finding_ids must equal the raw finding ID set"
        )
    return raw_findings, errors


def _load_challenge_output(
    root: Path,
    reference: object,
    label: str,
    validator: Draft202012Validator | None,
) -> tuple[dict | None, list[str]]:
    output, errors = _load_json_object_artifact(
        root,
        reference,
        label,
        REVIEW_CHALLENGE_PREFIX,
        REVIEW_CHALLENGE_SUFFIX,
        require_canonical=False,
    )
    if output is None:
        return None, errors
    if validator is not None:
        errors.extend(_schema_violations(validator, output, label))
    return output, errors


def _challenge_objection_errors(output: dict, label: str) -> list[str]:
    errors: list[str] = []
    objections = [
        objection
        for objection in _sequence(output.get("objections"))
        if isinstance(objection, dict)
    ]
    objection_by_id: dict[str, dict] = {}
    for objection in objections:
        objection_id = objection.get("challenge_objection_id")
        if not isinstance(objection_id, str):
            continue
        if objection_id in objection_by_id:
            errors.append(f"{label}: duplicate challenge_objection_id {objection_id!r}")
            continue
        objection_by_id[objection_id] = objection
    listed_ids: set[str] = set()
    for assessment in _sequence(output.get("objective_assessments")):
        if not isinstance(assessment, dict):
            continue
        objective = assessment.get("objective")
        for objection_id in _sequence(assessment.get("objection_ids")):
            if not isinstance(objection_id, str):
                continue
            if objection_id in listed_ids:
                errors.append(
                    f"{label}: objection {objection_id!r} is listed more than once"
                )
            listed_ids.add(objection_id)
            objection = objection_by_id.get(objection_id)
            if objection is None:
                errors.append(
                    f"{label}: objective assessment references unknown objection "
                    f"{objection_id!r}"
                )
            elif objection.get("objective") != objective:
                errors.append(
                    f"{label}: objection {objection_id!r} is listed under objective "
                    f"{objective!r} but declares {objection.get('objective')!r}"
                )
    for objection_id in sorted(set(objection_by_id) - listed_ids):
        errors.append(
            f"{label}: objection {objection_id!r} is not listed by any objective "
            "assessment"
        )
    return errors


def _challenge_objective_errors(
    output: dict, label: str, expected_objectives: tuple[str, ...]
) -> list[str]:
    objectives = [
        assessment.get("objective")
        for assessment in _sequence(output.get("objective_assessments"))
        if isinstance(assessment, dict)
    ]
    counts = Counter(objective for objective in objectives if isinstance(objective, str))
    if (
        len(objectives) != len(expected_objectives)
        or set(counts) != set(expected_objectives)
        or any(count != 1 for count in counts.values())
    ):
        return [
            f"{label}: objective assessments must cover exactly "
            f"{len(expected_objectives)} required objectives once each"
        ]
    return []


def _supporting_receipt(
    supporting: dict[tuple, dict], reference: object
) -> dict | None:
    ref = _mapping(reference)
    key = (ref.get("path"), ref.get("sha256"))
    return supporting.get(key)


def _bound_challenge_packet_errors(root: Path, challenge: dict, bundle: dict | None, review_packet_ref: dict, parsed_review_packet: dict | None, packet_validator: Draft202012Validator | None, expected_kind: str, expected_selector: str, expected_payload: dict, expected_sha: str, expected_objectives: tuple[str, ...], label: str) -> tuple[dict | None, list[str]]:
    packet, errors = _load_challenge_packet(root, challenge.get("packet"), parsed_review_packet, review_packet_ref, packet_validator, f"{label}: challenge packet")
    if packet is None:
        return None, errors
    subject = _mapping(packet.get("challenge_subject"))
    if packet.get("challenge_kind") != expected_kind:
        errors.append(f"{label}: challenge packet challenge_kind must be {expected_kind}")
    if subject.get("selector") != expected_selector:
        errors.append(f"{label}: challenge packet selector must be {expected_selector}")
    if subject.get("payload") != expected_payload:
        errors.append(f"{label}: challenge packet subject payload does not equal exact challenged candidate")
    if subject.get("sha256") != expected_sha:
        errors.append(f"{label}: challenge packet subject sha256 does not equal exact challenged candidate")
    if tuple(_sequence(packet.get("required_objectives"))) != expected_objectives:
        errors.append(f"{label}: challenge packet required_objectives must equal the exact required objectives")
    return packet, errors

def _materiality_errors(
    root: Path,
    label: str,
    source_finding: dict,
    materiality: object,
    bundle: dict | None,
    supporting: dict[tuple, dict],
    challenge_validator: Draft202012Validator | None,
    review_packet_ref: dict | None = None,
    parsed_review_packet: dict | None = None,
    packet_validator: Draft202012Validator | None = None,
    bundle_sha256: object = None,
) -> list[str]:
    errors: list[str] = []
    materiality_mapping = _mapping(materiality)
    material = _finding_is_material({"materiality": materiality_mapping})

    assessment_receipt = _supporting_receipt(
        supporting, materiality_mapping.get("assessment_execution_receipt")
    )
    if assessment_receipt is None:
        errors.append(
            f"{label}: materiality assessment receipt must appear in "
            "supporting_executions"
        )
    elif assessment_receipt.get("role") != "materiality-assessor":
        errors.append(
            f"{label}: materiality assessment receipt role must be materiality-assessor"
        )

    challenge = materiality_mapping.get("challenge")
    if material:
        if challenge is not None:
            errors.append(
                f"{label}: a material finding must not carry a materiality challenge"
            )
        return errors
    if not isinstance(challenge, dict):
        errors.append(
            f"{label}: a non-material finding requires a hostile materiality challenge"
        )
        return errors

    expected_sha = _materiality_challenge_subject_sha256(
        source_finding, materiality_mapping
    )
    if challenge.get("challenged_materiality_sha256") != expected_sha:
        errors.append(
            f"{label}: materiality challenge does not bind the exact candidate "
            "materiality assessment"
        )
    packet, packet_errors = _bound_challenge_packet_errors(root, challenge, bundle, review_packet_ref or {}, parsed_review_packet, packet_validator, "materiality", MATERIALITY_CHALLENGE_SELECTOR, _materiality_challenge_subject_payload(source_finding, materiality_mapping), expected_sha, MATERIALITY_AXES, label)
    errors.extend(packet_errors)
    receipt = _supporting_receipt(supporting, challenge.get("execution_receipt"))
    if receipt is None:
        errors.append(
            f"{label}: materiality challenge execution receipt must appear in "
            "supporting_executions"
        )
    else:
        if receipt.get("role") != CHALLENGE_ROLE:
            errors.append(f"{label}: materiality challenge receipt role must be challenge")
        prompts = _mapping(_mapping(bundle).get("prompts"))
        inputs = _mapping(receipt.get("input"))
        if inputs.get("prompt") != prompts.get("challenge"):
            errors.append(
                f"{label}: materiality challenge receipt prompt must equal the "
                "protocol bundle challenge prompt"
            )
        if inputs.get("packet") != challenge.get("packet"):
            errors.append(f"{label}: materiality challenge receipt packet must equal the challenge packet")
        validators, validator_errors = _bundle_selected_validators(root, bundle, f"{label}: protocol bundle")
        errors.extend(validator_errors)
        receipt_errors, _ = _validate_execution_receipt(root, receipt, f"{label}: materiality challenge receipt", _protocol_profile_map(bundle), bundle_sha256, validators, packet)
        errors.extend(receipt_errors)
        qualifying = _unique_qualifying_attempt(receipt)
        if qualifying is not None and qualifying.get(
            "raw_output"
        ) != challenge.get("output"):
            errors.append(
                f"{label}: materiality challenge receipt qualifying output must equal "
                "the challenge output"
            )
    output, output_errors = _load_challenge_output(
        root,
        challenge.get("output"),
        f"{label}: materiality challenge output",
        challenge_validator,
    )
    errors.extend(output_errors)
    if output is None:
        return errors
    if output.get("challenge_kind") != "materiality":
        errors.append(
            f"{label}: materiality challenge output challenge_kind must be materiality"
        )
    errors.extend(_challenge_objective_errors(output, label, MATERIALITY_AXES))
    errors.extend(_challenge_objection_errors(output, label))
    if _sequence(output.get("objections")):
        errors.append(
            f"{label}: a materiality challenge with any surviving objection cannot "
            "support a non-material conclusion"
        )
    return errors


def _refutation_challenge_errors(
    root: Path,
    label: str,
    challenge: dict,
    expected_sha: str,
    bundle: dict | None,
    supporting: dict[tuple, dict],
    challenge_validator: Draft202012Validator | None,
    review_packet_ref: dict | None = None,
    parsed_review_packet: dict | None = None,
    packet_validator: Draft202012Validator | None = None,
    expected_payload: dict | None = None,
    bundle_sha256: object = None,
) -> list[str]:
    errors: list[str] = []
    if challenge.get("challenged_refutation_sha256") != expected_sha:
        errors.append(f"{label}: challenge does not bind the exact refutation")
    packet, packet_errors = _bound_challenge_packet_errors(root, challenge, bundle, review_packet_ref or {}, parsed_review_packet, packet_validator, "refutation", REFUTATION_CHALLENGE_SELECTOR, expected_payload or {}, expected_sha, REFUTATION_CHALLENGE_OBJECTIVES, label)
    errors.extend(packet_errors)
    receipt = _supporting_receipt(supporting, challenge.get("execution_receipt"))
    if receipt is None:
        errors.append(
            f"{label}: refutation challenge execution receipt must appear in "
            "supporting_executions"
        )
    else:
        if receipt.get("role") != CHALLENGE_ROLE:
            errors.append(f"{label}: refutation challenge receipt role must be challenge")
        prompts = _mapping(_mapping(bundle).get("prompts"))
        inputs = _mapping(receipt.get("input"))
        if inputs.get("prompt") != prompts.get("challenge"):
            errors.append(
                f"{label}: refutation challenge receipt prompt must equal the "
                "protocol bundle challenge prompt"
            )
        if inputs.get("packet") != challenge.get("packet"):
            errors.append(f"{label}: refutation challenge receipt packet must equal the challenge packet")
        validators, validator_errors = _bundle_selected_validators(root, bundle, f"{label}: protocol bundle")
        errors.extend(validator_errors)
        receipt_errors, _ = _validate_execution_receipt(root, receipt, f"{label}: refutation challenge receipt", _protocol_profile_map(bundle), bundle_sha256, validators, packet)
        errors.extend(receipt_errors)
        qualifying = _unique_qualifying_attempt(receipt)
        if qualifying is not None and qualifying.get(
            "raw_output"
        ) != challenge.get("output"):
            errors.append(
                f"{label}: refutation challenge receipt qualifying output must equal "
                "the challenge output"
            )
    output, output_errors = _load_challenge_output(
        root, challenge.get("output"), f"{label}: challenge output", challenge_validator
    )
    errors.extend(output_errors)
    if output is None:
        return errors
    if output.get("challenge_kind") != "refutation":
        errors.append(f"{label}: challenge output challenge_kind must be refutation")
    errors.extend(
        _challenge_objective_errors(output, label, REFUTATION_CHALLENGE_OBJECTIVES)
    )
    errors.extend(_challenge_objection_errors(output, label))
    if _sequence(output.get("objections")):
        errors.append(
            f"{label}: a refutation challenge with any surviving objection cannot "
            "close the finding"
        )
    return errors


def _disposition_errors(
    root: Path,
    label: str,
    counterexample_source: dict,
    status: object,
    materiality: object,
    disposition: object,
    bundle: dict | None,
    supporting: dict[tuple, dict],
    challenge_validator: Draft202012Validator | None,
    refutation_subject_sha256: str,
    review_packet_ref: dict | None = None,
    parsed_review_packet: dict | None = None,
    packet_validator: Draft202012Validator | None = None,
    refutation_payload: dict | None = None,
    bundle_sha256: object = None,
) -> list[str]:
    errors: list[str] = []
    material = _finding_is_material({"materiality": materiality})
    if status == "refuted":
        disposition = _mapping(disposition)
        adjudication = _supporting_receipt(
            supporting, disposition.get("adjudication_execution_receipt")
        )
        if adjudication is None:
            errors.append(
                f"{label}: refuted disposition adjudication receipt must appear in "
                "supporting_executions"
            )
        counterexample = counterexample_source.get("counterexample")
        if (
            isinstance(counterexample, str)
            and counterexample.strip()
            and not isinstance(disposition.get("counterexample_disposition"), dict)
        ):
            errors.append(
                f"{label}: a finding with a counterexample requires "
                "counterexample_disposition"
            )
        challenge = disposition.get("challenge")
        if material and not isinstance(challenge, dict):
            errors.append(
                f"{label}: material refuted finding requires a challenge artifact"
            )
        if isinstance(challenge, dict):
            errors.extend(
                _refutation_challenge_errors(
                    root,
                    label,
                    challenge,
                    refutation_subject_sha256,
                    bundle,
                    supporting,
                    challenge_validator,
                    review_packet_ref,
                    parsed_review_packet,
                    packet_validator,
                    refutation_payload,
                    bundle_sha256,
                )
            )
    elif status in ("routed", "resolved"):
        disposition = _mapping(disposition)
        adjudication = _supporting_receipt(
            supporting, disposition.get("adjudication_execution_receipt")
        )
        if adjudication is None:
            errors.append(
                f"{label}: {status} disposition adjudication receipt must appear in "
                "supporting_executions"
            )
    return errors


def _gate_a_derived_subjects(value: object) -> list[dict]:
    """Return Gate A derived subjects preserving exact record multiplicity."""
    return [
        subject
        for subject in _sequence(value)
        if isinstance(subject, dict)
        and subject.get("subject_type") == "derived"
        and subject.get("selector") == GATE_A_SUBJECT_SELECTOR
    ]


def _review_evidence_errors(
    root: Path, manifest: dict, records: list[tuple[Path, dict]]
) -> list[str]:
    errors: list[str] = []
    schema, errors_load = _load_json(root, REVIEW_SCHEMA_RELATIVE)
    if errors_load:
        return errors_load
    validator, validator_errors = _validator(schema)
    if validator is None:
        return [
            f"{REVIEW_SCHEMA_RELATIVE.as_posix()}: {error}"
            for error in validator_errors
        ]

    bundle_validator, bundle_schema_errors = _load_schema_validator(
        root, PROTOCOL_BUNDLE_SCHEMA_RELATIVE
    )
    errors.extend(bundle_schema_errors)

    bundle_cache: dict[str, tuple[dict | None, list[str]]] = {}
    _current_reference, _current_bundle, current_errors = (
        _current_protocol_bundle_errors(root, manifest, bundle_validator, bundle_cache)
    )
    errors.extend(current_errors)

    record_index: dict[str, dict] = {}
    for path, record in records:
        label = path.relative_to(root).as_posix()
        errors.extend(_schema_violations(validator, record, label))
        review_id = record.get("review_id")
        if isinstance(review_id, str):
            if review_id in record_index:
                errors.append(f"{label}: duplicate review_id {review_id!r}")
            else:
                record_index[review_id] = record

    for path, record in records:
        label = path.relative_to(root).as_posix()
        protocol = _mapping(record.get("protocol"))
        review_packet = _mapping(protocol.get("review_packet"))
        packet_bytes, packet_errors = _read_review_artifact(
            root,
            review_packet,
            f"{label}: protocol.review_packet",
            REVIEW_PACKET_PREFIX,
            REVIEW_PACKET_SUFFIX,
        )
        errors.extend(packet_errors)
        parsed_review_packet: dict | None = None
        if packet_bytes is not None:
            try:
                candidate_packet = json.loads(packet_bytes.decode("utf-8"))
                if isinstance(candidate_packet, dict):
                    parsed_review_packet = candidate_packet
            except (UnicodeDecodeError, json.JSONDecodeError):
                pass
        prompt_reference = _mapping(protocol.get("prompt"))
        _, prompt_errors = _read_review_artifact(
            root,
            prompt_reference,
            f"{label}: protocol.prompt",
            REVIEW_PROMPT_PREFIX,
            REVIEW_PROMPT_SUFFIX,
        )
        errors.extend(prompt_errors)
        bundle_reference = _mapping(protocol.get("protocol_bundle"))
        bundle, bundle_errors = _load_protocol_bundle_document(
            root,
            bundle_reference,
            f"{label}: protocol.protocol_bundle",
            bundle_validator,
            bundle_cache,
        )
        errors.extend(bundle_errors)
        selected_validators, selected_validator_errors = _bundle_selected_validators(
            root, bundle, f"{label}: protocol.protocol_bundle"
        )
        errors.extend(selected_validator_errors)
        bundle_sha = bundle_reference.get("sha256")
        profile_map = _protocol_profile_map(bundle)
        prompts = _mapping(_mapping(bundle).get("prompts"))
        if bundle is not None and protocol.get("prompt") != prompts.get(
            "initial-reviewer"
        ):
            errors.append(
                f"{label}: protocol.prompt must equal the protocol bundle "
                "initial-reviewer prompt"
            )

        supporting: dict[tuple, dict] = {}
        supporting_paths: list[str] = []
        for index, reference in enumerate(
            _sequence(record.get("supporting_executions"))
        ):
            reference = _mapping(reference)
            ref_label = f"{label}: supporting_executions[{index}]"
            receipt, receipt_errors = _load_execution_receipt(
                root, reference, ref_label, selected_validators.get("execution-receipt")
            )
            errors.extend(receipt_errors)
            path_value = reference.get("path")
            if isinstance(path_value, str):
                supporting_paths.append(path_value)
            if receipt is None:
                continue
            if receipt.get("role") == INITIAL_REVIEWER_ROLE:
                errors.append(
                    f"{ref_label}: initial-reviewer executions belong in executions, "
                    "not supporting_executions"
                )
            receipt_errors, _attempt = _validate_execution_receipt(
                root, receipt, ref_label, profile_map, bundle_sha, selected_validators
            )
            errors.extend(receipt_errors)
            supporting[(reference.get("path"), reference.get("sha256"))] = receipt
        duplicates = sorted(
            path for path, count in Counter(supporting_paths).items() if count > 1
        )
        for duplicate in duplicates:
            errors.append(f"{label}: duplicate supporting execution path {duplicate}")

        gate_a_subjects = _gate_a_derived_subjects(record.get("subjects"))
        is_gate_a_subject_review = (
            record.get("review_class") == GATE_A_REVIEW_CLASS
            and bool(gate_a_subjects)
        )
        if is_gate_a_subject_review:
            if len(gate_a_subjects) != 1:
                errors.append(
                    f"{label}: Gate A assurance-decomposition review must declare "
                    "exactly one Gate A derived subject"
                )
            elif packet_bytes is not None:
                errors.extend(
                    _gate_a_review_packet_errors(
                        packet_bytes,
                        gate_a_subjects[0],
                        f"{label}: protocol.review_packet",
                    )
                )

        executions = [
            execution
            for execution in _sequence(record.get("executions"))
            if isinstance(execution, dict)
        ]
        execution_ids = [
            execution.get("execution_id")
            for execution in executions
            if isinstance(execution.get("execution_id"), str)
        ]
        if len(execution_ids) != len(set(execution_ids)):
            errors.append(f"{label}: execution_id values must be unique")

        raw_findings_by_execution: dict[str, dict[str, dict]] = {}
        declared_raw_ids: dict[str, set[str]] = {}
        raw_paths: list[str] = []
        for execution in executions:
            execution_id = execution.get("execution_id")
            exec_label = f"{label}: execution {execution_id!r}"
            if execution.get("review_packet_sha256") != review_packet.get("sha256"):
                errors.append(
                    f"{exec_label} review_packet_sha256 must equal "
                    "protocol.review_packet.sha256"
                )
            if execution.get("prompt_sha256") != prompt_reference.get("sha256"):
                errors.append(
                    f"{exec_label} prompt_sha256 must equal protocol.prompt.sha256"
                )
            receipt_reference = _mapping(execution.get("execution_receipt"))
            receipt, receipt_errors = _load_execution_receipt(
                root,
                receipt_reference,
                f"{exec_label} execution_receipt",
                selected_validators.get("execution-receipt"),
            )
            errors.extend(receipt_errors)
            if receipt is not None:
                receipt_errors, qualifying_attempt = _validate_execution_receipt(
                    root,
                    receipt,
                    f"{exec_label} execution_receipt",
                    profile_map,
                    bundle_sha,
                    selected_validators,
                )
                errors.extend(receipt_errors)
                errors.extend(
                    _initial_reviewer_receipt_errors(
                        record, execution, receipt, qualifying_attempt
                    )
                )
            raw_path = _mapping(execution.get("raw_output")).get("path")
            if isinstance(raw_path, str):
                raw_paths.append(raw_path)
            if is_gate_a_subject_review:
                raw_findings, raw_errors = _raw_review_errors(
                    root, f"{exec_label} raw_output", execution, selected_validators.get("raw-review-output")
                )
                errors.extend(raw_errors)
                if raw_findings is not None and isinstance(execution_id, str):
                    raw_findings_by_execution[execution_id] = raw_findings
            else:
                _, raw_errors = _read_review_artifact(
                    root,
                    _mapping(execution.get("raw_output")),
                    f"{exec_label} raw_output",
                    REVIEW_RAW_OUTPUT_PREFIX,
                    REVIEW_RAW_OUTPUT_SUFFIX,
                )
                errors.extend(raw_errors)
            if not isinstance(execution_id, str):
                continue
            if is_gate_a_subject_review:
                declared_raw_ids[execution_id] = set(
                    raw_findings_by_execution.get(execution_id, {})
                )
            else:
                declared_raw_ids[execution_id] = {
                    raw_id
                    for raw_id in _sequence(execution.get("raw_finding_ids"))
                    if isinstance(raw_id, str)
                }

        duplicates = sorted(
            path for path, count in Counter(raw_paths).items() if count > 1
        )
        for duplicate in duplicates:
            errors.append(f"{label}: duplicate raw_output path {duplicate}")

        destinations: dict[tuple[str, str], list[str]] = {}
        finding_ids: list[str] = []
        for finding in _sequence(record.get("findings")):
            if not isinstance(finding, dict):
                continue
            finding_id = finding.get("finding_id")
            if isinstance(finding_id, str):
                finding_ids.append(finding_id)
            sources = [
                source
                for source in _sequence(finding.get("sources"))
                if isinstance(source, dict)
            ]
            if len(sources) != 1:
                errors.append(
                    f"{label}: finding {finding_id!r} must declare exactly one source"
                )
            for source in sources:
                execution_id = source.get("execution_id")
                raw_finding_id = source.get("raw_finding_id")
                if execution_id not in declared_raw_ids:
                    errors.append(
                        f"{label}: finding {finding_id!r} references unknown "
                        f"execution {execution_id!r}"
                    )
                    continue
                if raw_finding_id not in declared_raw_ids[execution_id]:
                    errors.append(
                        f"{label}: finding {finding_id!r} references unknown raw "
                        f"finding {raw_finding_id!r} of execution {execution_id!r}"
                    )
                    continue
                destinations.setdefault((execution_id, raw_finding_id), []).append(
                    finding_id
                )
                if is_gate_a_subject_review:
                    raw_finding = raw_findings_by_execution.get(
                        execution_id, {}
                    ).get(raw_finding_id)
                    if raw_finding is not None:
                        for field in ("statement", "argument", "counterexample"):
                            if finding.get(field) != raw_finding.get(field):
                                errors.append(
                                    f"{label}: finding {finding_id!r} {field} must "
                                    f"equal the exact raw finding {field}"
                                )
            errors.extend(
                _materiality_errors(
                    root,
                    f"{label}: finding {finding_id!r}",
                    finding,
                    finding.get("materiality"),
                    bundle,
                    supporting,
                    selected_validators.get("challenge-output"),
                    review_packet,
                    parsed_review_packet,
                    selected_validators.get("challenge-packet"),
                    bundle_sha,
                )
            )
            errors.extend(
                _disposition_errors(
                    root,
                    f"{label}: finding {finding_id!r}",
                    finding,
                    finding.get("status"),
                    finding.get("materiality"),
                    finding.get("disposition"),
                    bundle,
                    supporting,
                    selected_validators.get("challenge-output"),
                    _refutation_challenge_subject_sha256(finding),
                    review_packet,
                    parsed_review_packet,
                    selected_validators.get("challenge-packet"),
                    _refutation_challenge_subject_payload(finding),
                    bundle_sha,
                )
            )

        if len(finding_ids) != len(set(finding_ids)):
            errors.append(f"{label}: normalized finding_id values must be unique")

        for (execution_id, raw_finding_id), targets in sorted(destinations.items()):
            if len(targets) > 1:
                errors.append(
                    f"{label}: raw finding ({execution_id!r}, {raw_finding_id!r}) "
                    "maps to multiple normalized findings"
                )
        for execution_id, raw_ids in sorted(declared_raw_ids.items()):
            for raw_finding_id in sorted(raw_ids):
                if (execution_id, raw_finding_id) not in destinations:
                    errors.append(
                        f"{label}: declared raw finding ({execution_id!r}, "
                        f"{raw_finding_id!r}) has no normalized destination"
                    )

        for index, item in enumerate(_sequence(record.get("re_adjudications"))):
            if not isinstance(item, dict):
                continue
            item_label = f"{label}: re_adjudications[{index}]"
            source_review_id = item.get("source_review_id")
            source_finding_id = item.get("source_finding_id")
            source_record = (
                record_index.get(source_review_id)
                if isinstance(source_review_id, str)
                else None
            )
            if source_record is None:
                errors.append(
                    f"{item_label}: re-adjudication references unknown source review "
                    f"{source_review_id!r}"
                )
                continue
            source_finding = None
            for candidate in _sequence(source_record.get("findings")):
                if (
                    isinstance(candidate, dict)
                    and candidate.get("finding_id") == source_finding_id
                ):
                    source_finding = candidate
                    break
            if source_finding is None:
                errors.append(
                    f"{item_label}: re-adjudication references unknown source finding "
                    f"{source_finding_id!r}"
                )
                continue
            if item.get("source_finding_sha256") != _finding_subject_sha256(
                source_finding
            ):
                errors.append(
                    f"{item_label}: source_finding_sha256 does not match the exact "
                    "source finding"
                )
            errors.extend(
                _materiality_errors(
                    root,
                    item_label,
                    source_finding,
                    item.get("materiality"),
                    bundle,
                    supporting,
                    selected_validators.get("challenge-output"),
                    review_packet,
                    parsed_review_packet,
                    selected_validators.get("challenge-packet"),
                    bundle_sha,
                )
            )
            errors.extend(
                _disposition_errors(
                    root,
                    item_label,
                    source_finding,
                    item.get("status"),
                    item.get("materiality"),
                    item.get("disposition"),
                    bundle,
                    supporting,
                    selected_validators.get("challenge-output"),
                    _re_adjudication_refutation_subject_sha256(source_finding, item),
                    review_packet,
                    parsed_review_packet,
                    selected_validators.get("challenge-packet"),
                    _re_adjudication_refutation_subject_payload(source_finding, item),
                    bundle_sha,
                )
            )

    re_adjudication_keys: Counter[tuple] = Counter()
    for _path, record in records:
        for item in _sequence(record.get("re_adjudications")):
            if not isinstance(item, dict):
                continue
            re_adjudication_keys[
                (item.get("source_review_id"), item.get("source_finding_id"))
            ] += 1
    for key, count in sorted(
        re_adjudication_keys.items(), key=lambda pair: (str(pair[0][0]), str(pair[0][1]))
    ):
        if count > 1:
            errors.append(
                f"duplicate re-adjudication of finding {key[1]!r} from review "
                f"{key[0]!r}"
            )
    return errors


def _concise_parser_error(error: Exception) -> str:
    if isinstance(error, json.JSONDecodeError):
        return f"{error.msg} at line {error.lineno} column {error.colno}"
    text = " ".join(str(error).split())
    return text[:200] if text else error.__class__.__name__


def _sorted_strings(value: object) -> list[str]:
    return sorted(item for item in _sequence(value) if isinstance(item, str))


def _canonical_formal_semantic_domains(value: object) -> list[dict]:
    domains = [
        dict(item)
        for item in _sequence(value)
        if isinstance(item, dict)
    ]
    domains.sort(key=lambda item: str(item.get("id", "")))
    return domains


def _duplicate_formal_semantic_domain_ids(value: object) -> list[str]:
    domain_ids = [
        item.get("id")
        for item in _sequence(value)
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    counts = Counter(domain_ids)
    return sorted(
        domain_id
        for domain_id, count in counts.items()
        if count > 1
    )


def _authority_artifact_entries(
    root: Path, adr_ids: list[str], relation: str
) -> tuple[list[dict], list[str]]:
    entries: list[dict] = []
    errors: list[str] = []
    for adr_id in sorted(set(adr_ids)):
        if not isinstance(adr_id, str) or not ADR_ID.fullmatch(adr_id):
            errors.append(
                f"cannot derive Gate A subject: invalid {relation} entry {adr_id!r}"
            )
            continue
        number = adr_id.split("-")[1]
        matches = sorted((root / ADR_DIRECTORY_RELATIVE).glob(f"adr-{number}-*.md"))
        if len(matches) != 1:
            errors.append(
                f"cannot derive Gate A subject: expected exactly one file for "
                f"{adr_id}; found {len(matches)}"
            )
            continue
        path = matches[0]
        relative = path.relative_to(root).as_posix()
        try:
            data = path.read_bytes()
        except OSError as error:
            errors.append(
                f"cannot derive Gate A subject: cannot read {relative}: {error}"
            )
            continue
        entries.append({"id": adr_id, "path": relative, "sha256": sha256_hex(data)})
    entries.sort(key=lambda entry: entry["id"])
    return entries, errors


def build_gate_a_subject_payload(
    root: Path,
    manifest: dict,
) -> tuple[dict | None, list[str]]:
    """Build the canonical Gate A assurance-decomposition subject payload."""
    errors: list[str] = []
    authority = _mapping(manifest.get("authority"))

    normative_spec: dict | None = None
    normative_spec_path = authority.get("normative_spec")
    if not isinstance(normative_spec_path, str) or not normative_spec_path:
        errors.append(
            "cannot derive Gate A subject: authority.normative_spec is not a path"
        )
    else:
        try:
            data = (root / normative_spec_path).read_bytes()
        except OSError as error:
            errors.append(
                "cannot derive Gate A subject: cannot read normative specification "
                f"{normative_spec_path}: {error}"
            )
        else:
            normative_spec = {
                "path": normative_spec_path,
                "sha256": sha256_hex(data),
            }

    architecture_decisions, architecture_errors = _authority_artifact_entries(
        root,
        [item for item in _sequence(authority.get("architecture_decisions")) if isinstance(item, str)],
        "architecture_decisions",
    )
    abstraction_constraints, constraint_errors = _authority_artifact_entries(
        root,
        [item for item in _sequence(authority.get("abstraction_constraints")) if isinstance(item, str)],
        "abstraction_constraints",
    )
    errors.extend(architecture_errors)
    errors.extend(constraint_errors)

    policy = _mapping(manifest.get("policy"))

    duplicate_domain_ids = _duplicate_formal_semantic_domain_ids(
        policy.get("formal_semantic_domains")
    )
    for domain_id in duplicate_domain_ids:
        errors.append(
            f"cannot derive Gate A subject: duplicate formal semantic domain id {domain_id!r}"
        )

    claims = [
        {
            **claim,
            "normative_sources": _sorted_strings(claim.get("normative_sources")),
        }
        for claim in _sequence(manifest.get("claims"))
        if isinstance(claim, dict)
    ]
    claims.sort(key=lambda claim: str(claim.get("id", "")))

    coverage = [
        {
            "invariant": entry.get("invariant"),
            "canonical_operational_coverage": entry.get(
                "canonical_operational_coverage"
            ),
            "formal_claims": _sorted_strings(entry.get("formal_claims")),
            "residual_claims": _sorted_strings(entry.get("residual_claims")),
        }
        for entry in _sequence(manifest.get("normative_coverage"))
        if isinstance(entry, dict)
    ]
    coverage.sort(key=lambda entry: str(entry.get("invariant", "")))

    payload = {
        "subject_schema_version": 1,
        "selector": GATE_A_SUBJECT_SELECTOR,
        "authority": {
            "normative_spec": normative_spec,
            "architecture_decisions": architecture_decisions,
            "abstraction_constraints": abstraction_constraints,
        },
        "formal_assurance_context": {
            "schema_version": manifest.get("schema_version"),
            "project": manifest.get("project"),
            "formal_semantic_domains": _canonical_formal_semantic_domains(
                policy.get("formal_semantic_domains")
            ),
            "behavioral_modalities": _sorted_strings(
                policy.get("behavioral_modalities")
            ),
            "assurance_domains": _sorted_strings(policy.get("assurance_domains")),
        },
        "claims": claims,
        "normative_coverage": coverage,
    }
    if errors:
        return None, errors
    return payload, []


def build_gate_a_review_subject(
    root: Path,
    manifest: dict,
) -> tuple[dict | None, list[str]]:
    """Derive the canonical Gate A review subject descriptor."""
    payload, errors = build_gate_a_subject_payload(root, manifest)
    if payload is None:
        return None, errors
    return (
        {
            "subject_type": "derived",
            "selector": GATE_A_SUBJECT_SELECTOR,
            "sha256": sha256_hex(_canonical_json_bytes(payload)),
        },
        [],
    )


def build_gate_a_review_packet_payload(
    root: Path,
    manifest: dict,
) -> tuple[dict | None, list[str]]:
    """Build the self-contained canonical Gate A review packet payload."""
    subject_payload, errors = build_gate_a_subject_payload(root, manifest)
    if subject_payload is None:
        return None, errors

    subject = {
        "subject_type": "derived",
        "selector": GATE_A_SUBJECT_SELECTOR,
        "sha256": sha256_hex(_canonical_json_bytes(subject_payload)),
    }

    authority = _mapping(subject_payload.get("authority"))
    descriptors: list[tuple[str, dict, object]] = []
    normative_spec = authority.get("normative_spec")
    if isinstance(normative_spec, dict):
        descriptors.append(("normative-spec", normative_spec, None))
    else:
        errors.append("cannot embed authority content: normative_spec is missing")
    for relation, role in (
        ("architecture_decisions", "architecture-decision"),
        ("abstraction_constraints", "abstraction-constraint"),
    ):
        entries = [
            descriptor
            for descriptor in _sequence(authority.get(relation))
            if isinstance(descriptor, dict)
        ]
        entries.sort(key=lambda descriptor: str(descriptor.get("id", "")))
        for descriptor in entries:
            descriptors.append((role, descriptor, descriptor.get("id")))

    authority_contents: list[dict] = []
    for role, descriptor, identifier in descriptors:
        raw_path = descriptor.get("path")
        expected_sha = descriptor.get("sha256")
        if not isinstance(raw_path, str) or not raw_path:
            errors.append(f"cannot embed authority content: invalid path {raw_path!r}")
            continue
        try:
            data = (root / raw_path).read_bytes()
        except OSError as error:
            errors.append(f"cannot embed authority content {raw_path}: {error}")
            continue
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError as error:
            errors.append(f"cannot embed authority content {raw_path}: {error}")
            continue
        if not isinstance(expected_sha, str) or sha256_hex(data) != expected_sha:
            errors.append(
                f"cannot embed authority content {raw_path}: sha256 mismatch"
            )
            continue
        authority_contents.append(
            {
                "role": role,
                "id": identifier,
                "path": raw_path,
                "sha256": expected_sha,
                "content_utf8": content,
            }
        )

    if errors:
        return None, errors

    return (
        {
            "packet_schema_version": 1,
            "subject": subject,
            "subject_payload": subject_payload,
            "authority_contents": authority_contents,
        },
        [],
    )


def build_gate_a_review_packet_bytes(
    root: Path,
    manifest: dict,
) -> tuple[bytes | None, list[str]]:
    """Build the canonical JSON document bytes for the Gate A review packet."""
    payload, errors = build_gate_a_review_packet_payload(root, manifest)
    if payload is None:
        return None, errors
    return _canonical_json_document_bytes(payload), []


def _challenge_output_objections(root: Path, reference: object) -> list | None:
    output, errors = _load_json_object_artifact(
        root,
        reference,
        "challenge output",
        REVIEW_CHALLENGE_PREFIX,
        REVIEW_CHALLENGE_SUFFIX,
        require_canonical=False,
    )
    if output is None or errors:
        return None
    return _sequence(output.get("objections"))


def derive_gate_a(
    root: Path,
    manifest: dict,
    current_subject: dict | None,
    records: list[tuple[Path, dict]],
) -> dict:
    """Derive Formal-Architecture-Ready from current review evidence."""
    hostile_review = _mapping(_mapping(manifest.get("policy")).get("hostile_review"))
    current_bundle_reference = _mapping(
        hostile_review.get("current_protocol_bundle")
    )
    current_bundle_sha256 = current_bundle_reference.get("sha256")

    current: list[dict] = []
    stale: list[dict] = []
    for _path, record in records:
        if record.get("review_class") != GATE_A_REVIEW_CLASS:
            continue
        gate_a_subjects = _gate_a_derived_subjects(record.get("subjects"))
        if len(gate_a_subjects) != 1:
            continue
        if current_subject is None or gate_a_subjects[0] != current_subject:
            continue
        bundle_sha256 = _mapping(
            _mapping(record.get("protocol")).get("protocol_bundle")
        ).get("sha256")
        if isinstance(current_bundle_sha256, str) and bundle_sha256 == current_bundle_sha256:
            current.append(record)
        else:
            stale.append(record)

    if not current and not stale:
        return {
            "ready": False,
            "reason": "hostile assurance-decomposition review evidence required",
        }

    current_re_adjudications: dict[tuple, list[dict]] = {}
    for record in current:
        for item in _sequence(record.get("re_adjudications")):
            if not isinstance(item, dict):
                continue
            key = (item.get("source_review_id"), item.get("source_finding_id"))
            current_re_adjudications.setdefault(key, []).append(item)

    for record in stale:
        for finding in _sequence(record.get("findings")):
            if not isinstance(finding, dict):
                continue
            key = (record.get("review_id"), finding.get("finding_id"))
            if key not in current_re_adjudications:
                return {
                    "ready": False,
                    "reason": "stale-protocol finding requires current re-adjudication",
                }

    if not current:
        return {
            "ready": False,
            "reason": "hostile assurance-decomposition review evidence required",
        }

    for record in current:
        for finding in _sequence(record.get("findings")):
            if not isinstance(finding, dict):
                continue
            if (
                _finding_is_material(finding)
                and finding.get("status") in GATE_A_BLOCKING_STATUSES
            ):
                return {
                    "ready": False,
                    "reason": "surviving material hostile-review finding exists",
                }

    for record in stale:
        for finding in _sequence(record.get("findings")):
            if not isinstance(finding, dict):
                continue
            key = (record.get("review_id"), finding.get("finding_id"))
            items = current_re_adjudications.get(key, [])
            if not items:
                return {
                    "ready": False,
                    "reason": "stale-protocol finding requires current re-adjudication",
                }
            item = items[0]
            material = _finding_is_material({"materiality": item.get("materiality")})
            if material and item.get("status") in GATE_A_BLOCKING_STATUSES:
                return {
                    "ready": False,
                    "reason": "surviving material hostile-review finding exists",
                }
            if material and item.get("status") == "refuted":
                disposition = _mapping(item.get("disposition"))
                challenge = disposition.get("challenge")
                refutation_reason = (
                    "re-adjudicated material refutation requires current-protocol "
                    "challenge evidence"
                )
                if not isinstance(challenge, dict):
                    return {"ready": False, "reason": refutation_reason}
                if challenge.get(
                    "challenged_refutation_sha256"
                ) != _re_adjudication_refutation_subject_sha256(finding, item):
                    return {"ready": False, "reason": refutation_reason}
                objections = _challenge_output_objections(
                    root, challenge.get("output")
                )
                if objections is None or objections:
                    return {"ready": False, "reason": refutation_reason}
            if not material:
                challenge = _mapping(item.get("materiality")).get("challenge")
                materiality_reason = (
                    "current-protocol non-material re-adjudication requires a "
                    "hostile materiality challenge"
                )
                if not isinstance(challenge, dict):
                    return {"ready": False, "reason": materiality_reason}
                objections = _challenge_output_objections(
                    root, challenge.get("output")
                )
                if objections is None or objections:
                    return {"ready": False, "reason": materiality_reason}

    minimum_reviewers = hostile_review.get("minimum_independent_reviewers")
    if not isinstance(minimum_reviewers, int) or minimum_reviewers < 1:
        minimum_reviewers = 0
    required_objectives = {
        objective
        for objective in _sequence(
            _mapping(hostile_review.get("required_attack_objectives")).get(
                GATE_A_REVIEW_CLASS
            )
        )
        if isinstance(objective, str)
    }

    for record in current:
        executions = [
            execution
            for execution in _sequence(record.get("executions"))
            if isinstance(execution, dict)
        ]
        if not executions:
            continue
        qualifying = True
        identities: set[tuple] = set()
        effective_identities: set[tuple] = set()
        for execution in executions:
            if (
                execution.get("isolated_context") is not True
                or execution.get("cross_reviewer_visibility_before_seal") is not False
            ):
                qualifying = False
                break
            objectives = {
                objective
                for objective in _sequence(execution.get("attack_objectives"))
                if isinstance(objective, str)
            }
            if not required_objectives.issubset(objectives):
                qualifying = False
                break
            identities.add(
                (
                    execution.get("provider"),
                    execution.get("model"),
                    execution.get("model_version"),
                )
            )
            effective_identities.add(
                (execution.get("provider"), execution.get("model_version"))
            )
        if not qualifying:
            continue
        if (
            len(identities) >= minimum_reviewers
            and len(effective_identities) >= minimum_reviewers
        ):
            return {
                "ready": True,
                "reason": (
                    "current hostile assurance-decomposition campaign satisfies "
                    "operational independence, effective model identity, "
                    "per-execution attack coverage, sealed evidence, and "
                    "material-finding disposition requirements"
                ),
            }
    return {
        "ready": False,
        "reason": (
            "current assurance-decomposition review evidence does not satisfy "
            "operational independence, effective model identity, and per-execution "
            "attack coverage"
        ),
    }


def _tla_identifiers(model_text: str) -> tuple[set[str], set[str]]:
    variables: set[str] = set()
    for match in re.finditer(r"(?m)^\s*VARIABLES?\s+([^\n]+)", model_text):
        variables.update(
            name.strip() for name in match.group(1).split(",") if name.strip()
        )
    operators = set(
        re.findall(
            r"(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^\n]*\))?\s*==",
            model_text,
        )
    )
    return variables, operators


def _realization_errors(
    root: Path,
    manifest: dict,
    claim_by_id: dict[str, dict],
    domain_modules: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    realizations = manifest.get("formal_realizations")
    if not isinstance(realizations, list):
        return ["formal/verification.yaml formal_realizations must be a list"]
    if not realizations:
        return errors

    model_path = root / MODEL_RELATIVE
    model_variables: set[str] = set()
    model_operators: set[str] = set()
    if not model_path.exists():
        errors.append(
            f"formal_realizations are present but {MODEL_RELATIVE.as_posix()} is missing"
        )
    else:
        model_variables, model_operators = _tla_identifiers(
            model_path.read_text(encoding="utf-8")
        )

    for index, realization in enumerate(realizations):
        label = f"formal_realizations[{index}]"
        if not isinstance(realization, dict):
            errors.append(f"{label} must be a mapping")
            continue
        claim_id = realization.get("claim")
        claim = claim_by_id.get(claim_id) if isinstance(claim_id, str) else None
        if claim is None:
            errors.append(f"{label} references unknown claim {claim_id!r}")
        elif claim.get("assurance_domain") != "formal-behavioral":
            errors.append(f"{label} references non-formal-behavioral claim {claim_id}")
        domain = realization.get("formal_semantic_domain")
        if domain not in domain_modules:
            errors.append(f"{label} references unknown formal semantic domain")
        elif realization.get("module") != domain_modules[domain]:
            errors.append(
                f"{label} module {realization.get('module')!r} does not match the "
                f"declared module {domain_modules[domain]!r} for domain {domain}"
            )
        for field, singular, available in (
            ("properties", "property", model_operators),
            ("actions", "action", model_operators),
            ("state_variables", "state variable", model_variables),
        ):
            for identifier in _sequence(realization.get(field)):
                if isinstance(identifier, str) and identifier not in available:
                    errors.append(
                        f"{label} references missing TLA+ {singular} {identifier}"
                    )
        for profile in _sequence(realization.get("verification_profiles")):
            if not isinstance(profile, str):
                continue
            if "/" in profile or profile.endswith(".cfg"):
                if not (root / profile).exists():
                    errors.append(f"{label} references missing verification profile {profile}")
    return errors


def collect_errors(
    root: Path, *, check_generated: bool = True
) -> tuple[list[str], dict]:
    root = root.resolve()
    errors: list[str] = []
    summary: dict = {
        "invariants": 0,
        "claims": 0,
        "gate_a": {
            "ready": False,
            "reason": "hostile assurance-decomposition review evidence required",
        },
    }

    manifest, load_errors = _load_yaml(root, MANIFEST_RELATIVE)
    errors.extend(load_errors)
    if not isinstance(manifest, dict):
        if not load_errors:
            errors.append(f"{MANIFEST_RELATIVE.as_posix()} must be a mapping")
        return errors, summary

    errors.extend(_manifest_schema_errors(root, manifest))

    if manifest.get("schema_version") != 3:
        errors.append("formal/verification.yaml must use schema_version 3")

    heading_ids, spec_errors = _spec_invariant_ids(root)
    errors.extend(spec_errors)
    heading_set = set(heading_ids)
    if len(heading_ids) != len(heading_set):
        errors.append("duplicate invariant IDs in specification headings")

    errors.extend(_authority_errors(root, manifest))

    policy = _mapping(manifest.get("policy"))
    behavioral_modalities = {
        item for item in _sequence(policy.get("behavioral_modalities")) if isinstance(item, str)
    }
    formal_semantic_domains = _sequence(policy.get("formal_semantic_domains"))
    domain_ids = {
        item.get("id")
        for item in formal_semantic_domains
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    domain_modules: dict[str, str] = {}
    for item in formal_semantic_domains:
        if not isinstance(item, dict):
            continue
        domain_id = item.get("id")
        module = item.get("module")
        if not isinstance(domain_id, str) or not isinstance(module, str):
            continue
        if domain_id not in domain_modules:
            domain_modules[domain_id] = module

    claims = [claim for claim in _sequence(manifest.get("claims")) if isinstance(claim, dict)]
    claim_by_id: dict[str, dict] = {}
    for claim in claims:
        claim_id = claim.get("id")
        if not isinstance(claim_id, str):
            continue
        if claim_id in claim_by_id:
            errors.append(f"duplicate claim ID {claim_id}")
            continue
        claim_by_id[claim_id] = claim

    expected_claim_ids = {
        f"TL-CLAIM-{number:03d}"
        for number in range(CLAIM_ID_MIN, CLAIM_ID_MAX + 1)
    }
    if set(claim_by_id) != expected_claim_ids or len(claims) != CLAIM_TOTAL:
        errors.append(
            "claim IDs must be contiguous from TL-CLAIM-001 through TL-CLAIM-083 "
            f"({CLAIM_TOTAL} claims)"
        )
    summary["claims"] = len(claim_by_id)

    coverage = [
        entry
        for entry in _sequence(manifest.get("normative_coverage"))
        if isinstance(entry, dict)
    ]
    coverage_by_invariant: dict[str, dict] = {}
    for entry in coverage:
        invariant = entry.get("invariant")
        if not isinstance(invariant, str):
            continue
        if invariant in coverage_by_invariant:
            errors.append(f"normative_coverage lists {invariant} more than once")
            continue
        coverage_by_invariant[invariant] = entry

    missing_coverage = sorted(heading_set - set(coverage_by_invariant))
    if missing_coverage:
        errors.append(
            "spec invariant IDs missing from normative_coverage: "
            + ", ".join(missing_coverage)
        )
    unknown_coverage = sorted(set(coverage_by_invariant) - heading_set)
    if unknown_coverage:
        errors.append(
            "normative_coverage contains unknown invariant IDs: "
            + ", ".join(unknown_coverage)
        )
    summary["invariants"] = len(heading_set)

    for claim_id, claim in sorted(claim_by_id.items()):
        for source in _sequence(claim.get("normative_sources")):
            if not isinstance(source, str):
                continue
            if source not in heading_set:
                errors.append(f"{claim_id} references unknown normative source {source}")

    coverage_claim_refs: dict[str, set[str]] = {}
    for invariant, entry in sorted(coverage_by_invariant.items()):
        formal = entry.get("formal_claims")
        residual = entry.get("residual_claims")
        formal = formal if isinstance(formal, list) else []
        residual = residual if isinstance(residual, list) else []
        coverage_value = entry.get("canonical_operational_coverage")

        if coverage_value == "full":
            if not formal or residual:
                errors.append(
                    f"{invariant} coverage is full but requires non-empty formal_claims "
                    "and empty residual_claims"
                )
        elif coverage_value == "partial":
            if not formal or not residual:
                errors.append(
                    f"{invariant} coverage is partial but requires both formal_claims "
                    "and residual_claims to be non-empty"
                )
        elif coverage_value == "none":
            if formal or not residual:
                errors.append(
                    f"{invariant} coverage is none but requires empty formal_claims "
                    "and non-empty residual_claims"
                )

        referenced: set[str] = set()
        for kind, claim_ids in (("formal_claims", formal), ("residual_claims", residual)):
            for claim_id in claim_ids:
                if not isinstance(claim_id, str):
                    continue
                referenced.add(claim_id)
                claim = claim_by_id.get(claim_id)
                if claim is None:
                    errors.append(f"{invariant} {kind} references unknown {claim_id}")
                    continue
                sources = _sequence(claim.get("normative_sources"))
                if invariant not in sources:
                    errors.append(
                        f"{invariant} {kind} lists {claim_id} but its normative_sources "
                        f"do not include {invariant}"
                    )
                if kind == "formal_claims":
                    if claim.get("assurance_domain") != "formal-behavioral":
                        errors.append(
                            f"{invariant} formal_claims lists non-formal-behavioral {claim_id}"
                        )
                    else:
                        if claim.get("formal_semantic_domain") not in domain_ids:
                            errors.append(
                                f"{claim_id} has unknown formal_semantic_domain "
                                f"{claim.get('formal_semantic_domain')!r}"
                            )
                        if claim.get("modality") not in behavioral_modalities:
                            errors.append(
                                f"{claim_id} has invalid behavioral modality "
                                f"{claim.get('modality')!r}"
                            )
                else:
                    if claim.get("assurance_domain") == "formal-behavioral":
                        errors.append(
                            f"{invariant} residual_claims lists formal-behavioral {claim_id}"
                        )
        coverage_claim_refs[invariant] = referenced

    for claim_id, claim in sorted(claim_by_id.items()):
        for source in _sequence(claim.get("normative_sources")):
            if not isinstance(source, str):
                continue
            entry = coverage_by_invariant.get(source)
            if entry is None:
                continue
            if claim_id not in coverage_claim_refs.get(source, set()):
                errors.append(
                    f"{claim_id} declares normative source {source} but {source} "
                    "does not list it in formal_claims or residual_claims"
                )

    errors.extend(_migration_errors(root, set(claim_by_id)))
    errors.extend(_realization_errors(root, manifest, claim_by_id, domain_modules))

    current_subject, subject_errors = build_gate_a_review_subject(root, manifest)
    errors.extend(subject_errors)

    review_records, review_load_errors = load_review_records(root)
    review_validation_errors = _review_evidence_errors(root, manifest, review_records)

    errors.extend(review_load_errors)
    errors.extend(review_validation_errors)

    if review_load_errors or review_validation_errors:
        gate_a = {
            "ready": False,
            "reason": "hostile review evidence integrity failure",
        }
    else:
        gate_a = derive_gate_a(root, manifest, current_subject, review_records)
    summary["gate_a"] = gate_a

    if (root / MODEL_RELATIVE).exists() and not gate_a["ready"]:
        errors.append(
            "formal/Turnlock.tla exists while Formal-Architecture-Ready is BLOCKED"
        )

    if check_generated:
        renderer = root / "scripts" / "render-formal-mapping.py"
        mapping_path = root / MAPPING_RELATIVE
        result = subprocess.run(
            [sys.executable, str(renderer), "--stdout"],
            cwd=root,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            errors.append(
                "generated formal invariant mapping could not be rendered: "
                + concise_subprocess_failure(result.stderr, result.returncode)
            )
        elif not mapping_path.exists():
            errors.append(
                "generated formal invariant mapping is missing; "
                "run python scripts/render-formal-mapping.py"
            )
        elif mapping_path.read_bytes() != result.stdout:
            errors.append(
                "generated formal invariant mapping is stale; "
                "run python scripts/render-formal-mapping.py"
            )

    return errors, summary


def main() -> int:
    errors, summary = collect_errors(ROOT)
    if errors:
        print("formal traceability check: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    gate_a = summary["gate_a"]
    print(
        f"formal traceability check: OK ({summary['invariants']} invariants, "
        f"{summary['claims']} assurance claims)"
    )
    if gate_a["ready"]:
        print(f"formal-architecture-ready: READY ({gate_a['reason']})")
    else:
        print(f"formal-architecture-ready: BLOCKED ({gate_a['reason']})")
    print(f"canonical-formal-semantics-ready: {FUTURE_EVIDENCE_NOTE}")
    print(f"formal-verification-ready: {FUTURE_EVIDENCE_NOTE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
