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
REVIEW_PACKET_PREFIX = "formal/reviews/packets/"
REVIEW_PROMPT_PREFIX = "formal/reviews/prompts/"
REVIEW_RAW_OUTPUT_PREFIX = "formal/reviews/raw/"
REVIEW_CHALLENGE_PREFIX = "formal/reviews/challenges/"
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
        if path.name == REVIEW_SCHEMA_RELATIVE.name:
            continue
        suffix = path.suffix.lower()
        if suffix not in REVIEW_SUFFIXES:
            continue
        label = path.relative_to(root).as_posix()
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


def _review_artifact_errors(
    root: Path,
    reference: object,
    label: str,
    prefix: str,
) -> list[str]:
    """Validate a repository-relative, content-addressed review artifact."""
    errors: list[str] = []
    artifact = _mapping(reference)
    raw_path = artifact.get("path")
    expected_sha = artifact.get("sha256")
    if not isinstance(raw_path, str) or not raw_path:
        errors.append(f"{label}: artifact path must be a non-empty string")
        return errors
    path = Path(raw_path)
    if path.is_absolute():
        errors.append(f"{label}: artifact path must be repository-relative: {raw_path}")
        return errors
    if ".." in path.parts:
        errors.append(f"{label}: artifact path must not contain '..': {raw_path}")
        return errors
    normalized = path.as_posix()
    if not normalized.startswith(prefix):
        errors.append(f"{label}: artifact path must be under {prefix}: {raw_path}")
        return errors
    if not normalized.endswith(".md"):
        errors.append(f"{label}: artifact path must be a Markdown file: {raw_path}")
        return errors
    target = root / normalized
    if not target.exists():
        errors.append(f"{label}: artifact does not exist: {raw_path}")
        return errors
    if not target.is_file():
        errors.append(f"{label}: artifact is not a regular file: {raw_path}")
        return errors
    try:
        data = target.read_bytes()
    except OSError as error:
        errors.append(f"{label}: cannot read artifact {raw_path}: {error}")
        return errors
    if expected_sha != sha256_hex(data):
        errors.append(f"{label}: artifact sha256 does not match {raw_path}")
    return errors


def _refutation_errors(
    root: Path,
    label: str,
    finding: dict,
    declared_raw_ids: dict[str, set[str]],
) -> list[str]:
    """Validate the structured refutation contract for a single finding."""
    if finding.get("status") != "refuted":
        return []
    errors: list[str] = []
    finding_id = finding.get("finding_id")
    disposition = _mapping(finding.get("disposition"))
    if disposition.get("kind") != "refuted":
        errors.append(
            f"{label}: finding {finding_id!r} with status 'refuted' must carry a "
            "refuted disposition"
        )
        return errors
    counterexample = finding.get("counterexample")
    if isinstance(counterexample, str) and counterexample.strip():
        if not isinstance(disposition.get("counterexample_disposition"), dict):
            errors.append(
                f"{label}: finding {finding_id!r} declares a counterexample and "
                "requires counterexample_disposition"
            )
    if not _finding_is_material(finding):
        return errors
    challenge = disposition.get("challenge")
    if not isinstance(challenge, dict):
        errors.append(
            f"{label}: material refuted finding {finding_id!r} requires a challenge "
            "artifact"
        )
        return errors
    challenger_execution_id = challenge.get("challenger_execution_id")
    if challenger_execution_id not in declared_raw_ids:
        errors.append(
            f"{label}: finding {finding_id!r} challenge references unknown execution "
            f"{challenger_execution_id!r}"
        )
    errors.extend(
        _review_artifact_errors(
            root,
            _mapping(challenge.get("output")),
            f"{label}: finding {finding_id!r} challenge output",
            REVIEW_CHALLENGE_PREFIX,
        )
    )
    return errors


def _review_evidence_errors(
    root: Path, records: list[tuple[Path, dict]]
) -> list[str]:
    schema, errors = _load_json(root, REVIEW_SCHEMA_RELATIVE)
    if errors:
        return errors
    validator, validator_errors = _validator(schema)
    if validator is None:
        return [f"{REVIEW_SCHEMA_RELATIVE.as_posix()}: {error}" for error in validator_errors]

    for path, record in records:
        label = path.relative_to(root).as_posix()
        errors.extend(_schema_violations(validator, record, label))

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

        protocol = _mapping(record.get("protocol"))
        review_packet = _mapping(protocol.get("review_packet"))
        prompt = _mapping(protocol.get("prompt"))
        errors.extend(
            _review_artifact_errors(
                root,
                review_packet,
                f"{label}: protocol.review_packet",
                REVIEW_PACKET_PREFIX,
            )
        )
        errors.extend(
            _review_artifact_errors(
                root,
                prompt,
                f"{label}: protocol.prompt",
                REVIEW_PROMPT_PREFIX,
            )
        )

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
            if execution.get("prompt_sha256") != prompt.get("sha256"):
                errors.append(
                    f"{exec_label} prompt_sha256 must equal protocol.prompt.sha256"
                )
            raw_output = _mapping(execution.get("raw_output"))
            errors.extend(
                _review_artifact_errors(
                    root,
                    raw_output,
                    f"{exec_label} raw_output",
                    REVIEW_RAW_OUTPUT_PREFIX,
                )
            )
            raw_path = raw_output.get("path")
            if isinstance(raw_path, str):
                raw_paths.append(raw_path)
            if isinstance(execution_id, str):
                declared_raw_ids.setdefault(execution_id, set()).update(
                    raw_finding_id
                    for raw_finding_id in _sequence(execution.get("raw_finding_ids"))
                    if isinstance(raw_finding_id, str)
                )

        duplicates = sorted(
            raw_path for raw_path, count in Counter(raw_paths).items() if count > 1
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
            for source in _sequence(finding.get("sources")):
                if not isinstance(source, dict):
                    continue
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

        for finding in _sequence(record.get("findings")):
            if not isinstance(finding, dict):
                continue
            errors.extend(
                _refutation_errors(root, label, finding, declared_raw_ids)
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
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return (
        {
            "subject_type": "derived",
            "selector": GATE_A_SUBJECT_SELECTOR,
            "sha256": sha256_hex(canonical),
        },
        [],
    )


def derive_gate_a(
    manifest: dict,
    current_subject: dict | None,
    records: list[tuple[Path, dict]],
) -> dict:
    """Derive Formal-Architecture-Ready from current review evidence."""
    current: list[dict] = []
    for _path, record in records:
        if record.get("review_class") != GATE_A_REVIEW_CLASS:
            continue
        if current_subject is not None and any(
            isinstance(subject, dict) and subject == current_subject
            for subject in _sequence(record.get("subjects"))
        ):
            current.append(record)

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

    hostile_review = _mapping(_mapping(manifest.get("policy")).get("hostile_review"))
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
        if not qualifying:
            continue
        if len(identities) >= minimum_reviewers:
            return {
                "ready": True,
                "reason": (
                    "current hostile assurance-decomposition campaign satisfies "
                    "operational independence, per-execution attack coverage, sealed "
                    "evidence, and material-finding disposition requirements"
                ),
            }
    return {
        "ready": False,
        "reason": (
            "current assurance-decomposition review evidence does not satisfy "
            "operational independence and per-execution attack coverage"
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
        "gate_a": derive_gate_a({}, None, []),
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
    review_validation_errors = _review_evidence_errors(root, review_records)

    errors.extend(review_load_errors)
    errors.extend(review_validation_errors)

    if review_load_errors or review_validation_errors:
        gate_a = {
            "ready": False,
            "reason": "hostile review evidence integrity failure",
        }
    else:
        gate_a = derive_gate_a(manifest, current_subject, review_records)
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
