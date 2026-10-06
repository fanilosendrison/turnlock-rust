#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import base64
import copy
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from proto_ring import evidence_requirements, repository_governance_state
from proto_ring.evidence_requirements import (
    EvidenceClassKind,
    InstantiationKind,
    PersistentEvidenceRequirement,
)
from proto_ring.exact_evidence_binding import (
    BindingStatus,
    EvidenceBinding,
    EvidenceRequirement,
    evaluate as evaluate_evidence_binding,
)

def _yaml_parser_state_value(
    value: object,
    seen: set[int] | None = None,
) -> object:
    if seen is None:
        seen = set()

    if value is None:
        return ("null",)

    if type(value) is bool:
        return ("bool", value)

    if type(value) is int:
        return ("int", value)

    if type(value) is float:
        return ("float", value.hex())

    if type(value) is str:
        return ("str", value)

    if type(value) is bytes:
        return ("bytes", value)

    if isinstance(value, re.Pattern):
        return (
            "regex",
            value.pattern,
            value.flags,
        )

    if type(value) in (list, tuple, dict, set, frozenset):
        identity = id(value)

        if identity in seen:
            return (
                "recursive-identity",
                type(value),
                value,
            )

        seen.add(identity)

        try:
            if type(value) is list:
                return (
                    "list",
                    tuple(
                        _yaml_parser_state_value(
                            item,
                            seen,
                        )
                        for item in value
                    ),
                )

            if type(value) is tuple:
                return (
                    "tuple",
                    tuple(
                        _yaml_parser_state_value(
                            item,
                            seen,
                        )
                        for item in value
                    ),
                )

            if type(value) is dict:
                return (
                    "dict",
                    tuple(
                        (
                            _yaml_parser_state_value(
                                key,
                                seen,
                            ),
                            _yaml_parser_state_value(
                                item,
                                seen,
                            ),
                        )
                        for key, item in value.items()
                    ),
                )

            return (
                "set",
                type(value),
                tuple(
                    _yaml_parser_state_value(
                        item,
                        seen,
                    )
                    for item in value
                ),
            )

        finally:
            seen.remove(identity)

    # Retain the actual object, rather than only id(value).
    # For PyYAML's functions/classes/descriptors this preserves
    # identity-sensitive comparison and also keeps the original
    # object alive.
    return (
        "identity",
        type(value),
        value,
    )


def _yaml_parser_state() -> object:
    safe_loader = yaml.SafeLoader
    raw_state = (
        yaml.safe_load,
        yaml.load,
        safe_loader,
        tuple(
            (
                cls,
                dict(vars(cls)),
            )
            for cls in safe_loader.__mro__
        ),
    )
    return _yaml_parser_state_value(raw_state)


def _yaml_parser_state_equal(
    left: object,
    right: object,
) -> bool:
    if type(left) is not tuple or type(right) is not tuple:
        return False
    if not left or not right:
        return False
    if type(left[0]) is not str or type(right[0]) is not str:
        return False

    left_tag = left[0]
    right_tag = right[0]
    if left_tag != right_tag:
        return False

    if left_tag == "null":
        return len(left) == 1 and len(right) == 1

    primitive_types = {
        "bool": bool,
        "int": int,
        "float": str,
        "str": str,
        "bytes": bytes,
    }
    if left_tag in primitive_types:
        if len(left) != 2 or len(right) != 2:
            return False
        expected_type = primitive_types[left_tag]
        if type(left[1]) is not expected_type:
            return False
        if type(right[1]) is not expected_type:
            return False
        return left[1] == right[1]

    if left_tag == "regex":
        if len(left) != 3 or len(right) != 3:
            return False
        if type(left[1]) is not str or type(right[1]) is not str:
            return False
        if type(left[2]) is not int or type(right[2]) is not int:
            return False
        return left[1] == right[1] and left[2] == right[2]

    if left_tag in ("identity", "recursive-identity"):
        if len(left) != 3 or len(right) != 3:
            return False
        return left[1] is right[1] and left[2] is right[2]

    if left_tag in ("list", "tuple"):
        if len(left) != 2 or len(right) != 2:
            return False
        left_items = left[1]
        right_items = right[1]
        if type(left_items) is not tuple or type(right_items) is not tuple:
            return False
        if len(left_items) != len(right_items):
            return False
        return all(
            _yaml_parser_state_equal(left_item, right_item)
            for left_item, right_item in zip(left_items, right_items)
        )

    if left_tag == "dict":
        if len(left) != 2 or len(right) != 2:
            return False
        left_entries = left[1]
        right_entries = right[1]
        if type(left_entries) is not tuple or type(right_entries) is not tuple:
            return False
        if len(left_entries) != len(right_entries):
            return False
        for left_entry, right_entry in zip(left_entries, right_entries):
            if type(left_entry) is not tuple or len(left_entry) != 2:
                return False
            if type(right_entry) is not tuple or len(right_entry) != 2:
                return False
            if not _yaml_parser_state_equal(left_entry[0], right_entry[0]):
                return False
            if not _yaml_parser_state_equal(left_entry[1], right_entry[1]):
                return False
        return True

    if left_tag == "set":
        if len(left) != 3 or len(right) != 3:
            return False
        if left[1] is not set and left[1] is not frozenset:
            return False
        if right[1] is not set and right[1] is not frozenset:
            return False
        if left[1] is not right[1]:
            return False
        left_items = left[2]
        right_items = right[2]
        if type(left_items) is not tuple or type(right_items) is not tuple:
            return False
        if len(left_items) != len(right_items):
            return False
        matched = [False] * len(right_items)
        for left_item in left_items:
            for index, right_item in enumerate(right_items):
                if not matched[index] and _yaml_parser_state_equal(
                    left_item,
                    right_item,
                ):
                    matched[index] = True
                    break
            else:
                return False
        return True

    return False


_ORIGINAL_YAML_PARSER_STATE = _yaml_parser_state()


def _yaml_parse_cache_is_eligible() -> bool:
    return _yaml_parser_state_equal(
        _yaml_parser_state(),
        _ORIGINAL_YAML_PARSER_STATE,
    )


_YAML_PARSE_CACHE: dict[str, object] = {}

ROOT = Path(__file__).resolve().parents[1]

MANIFEST_RELATIVE = Path("formal/verification.yaml")
MANIFEST_SCHEMA_RELATIVE = Path("formal/verification.schema.json")
MIGRATION_RELATIVE = Path("formal/migrations/verification-v2-to-v3-property-audit.yaml")
MAPPING_RELATIVE = Path("docs/formal/invariant-mapping.md")
MODEL_RELATIVE = Path("formal/Turnlock.tla")
REVIEW_DIRECTORY_RELATIVE = Path("formal/reviews")
LEGACY_REVIEW_EVIDENCE_ALIAS_RELATIVE = Path("formal/reviews/review-evidence.schema.json")
LEGACY_PROTOCOL_BUNDLE_ALIAS_RELATIVE = Path(
    "formal/reviews/review-protocol-bundle.schema.json"
)
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
REVIEW_ADJUDICATION_PACKETS_PREFIX = "formal/reviews/adjudication-packets/"
REVIEW_ADJUDICATION_PACKET_SUFFIX = ".json"
REVIEW_PROTOCOLS_PREFIX = "formal/reviews/protocols/"
REVIEW_PROTOCOL_BUNDLE_SUFFIX = ".json"
REVIEW_SCHEMAS_PREFIX = "formal/reviews/schemas/"
REVIEW_META_SCHEMAS_PREFIX = "formal/reviews/meta-schemas/"
REVIEW_META_SCHEMA_SUFFIX = ".json"
REVIEW_EXECUTIONS_PREFIX = "formal/reviews/executions/"
REVIEW_EXECUTION_SUFFIX = ".json"
REVIEW_ADJUDICATIONS_PREFIX = "formal/reviews/adjudications/"
REVIEW_SUPPLEMENTS_PREFIX = "formal/reviews/supplements/"
REVIEW_JSON_OUTPUT_SUFFIX = ".json"
REVIEW_ARTIFACT_PREFIXES = (
    REVIEW_PACKET_PREFIX,
    REVIEW_PROMPT_PREFIX,
    REVIEW_RAW_OUTPUT_PREFIX,
    REVIEW_CHALLENGE_PREFIX,
    REVIEW_CHALLENGE_PACKET_PREFIX,
    REVIEW_ADJUDICATION_PACKETS_PREFIX,
    REVIEW_PROTOCOLS_PREFIX,
    REVIEW_SCHEMAS_PREFIX,
    REVIEW_META_SCHEMAS_PREFIX,
    REVIEW_EXECUTIONS_PREFIX,
    REVIEW_ADJUDICATIONS_PREFIX,
    REVIEW_SUPPLEMENTS_PREFIX,
)
REVIEW_ARTIFACT_EXCLUDED_FILE_NAMES = (
    LEGACY_REVIEW_EVIDENCE_ALIAS_RELATIVE.name,
    LEGACY_PROTOCOL_BUNDLE_ALIAS_RELATIVE.name,
)
LEGACY_REVIEW_EVIDENCE_META_SCHEMA_REFERENCE = {
    "path": "formal/reviews/meta-schemas/review-evidence-v5.schema.json",
    "sha256": "0f66a468c5afc0909389bf3bece221cc083e05a52f9e19be8b41c7e24d3e01bc",
}
LEGACY_PROTOCOL_BUNDLE_META_SCHEMA_REFERENCE = {
    "path": "formal/reviews/meta-schemas/review-protocol-bundle-v1-v3.schema.json",
    "sha256": "a599aab44b160773f35aec693bd63d604f7ddd51b8243e1f4fb12fcf2af2d1f0",
}
PROTOCOL_V4_META_SCHEMA_REFERENCE = {
    "path": "formal/reviews/meta-schemas/review-protocol-bundle-v4.schema.json",
    "sha256": "4604ad8aa1868c0f13bad5a173af5c7df1cb4343a9cd7b3b48d3000e2fb6cb43",
}
PROTOCOL_V5_META_SCHEMA_REFERENCE = {
    "path": "formal/reviews/meta-schemas/review-protocol-bundle-v5.schema.json",
    "sha256": "96ff941defb59687f77593fb60b7dda460da06250b718e9ce082f78e94407327",
}
PROTOCOL_V6_META_SCHEMA_REFERENCE = {
    "path": "formal/reviews/meta-schemas/review-protocol-bundle-v6.schema.json",
    "sha256": "b4cfc0ca7b577e2d37f048d9cb7bb5d546c77a6dffed2100340e05d52b525e78",
}
PROTOCOL_V7_META_SCHEMA_REFERENCE = {
    "path": "formal/reviews/meta-schemas/review-protocol-bundle-v7.schema.json",
    "sha256": "f1c2c91cedd8e248962d5890834472fcbbaab32daaf2bc76eccd3e910841f4f3",
}
PROTOCOL_V7_BUNDLE_REFERENCE = {
    "path": "formal/reviews/protocols/gate-a-campaign-protocol-v7.json",
    "sha256": "b9c6cde1624590d43686703b5dba991ca7a8a46f65a65d047a52197c02686f94",
}
PROTOCOL_V7_PREDECESSOR_REFERENCE = {
    "path": "formal/reviews/protocols/gate-a-campaign-protocol-v6.json",
    "sha256": "841908ae137b1caaa8d0ae1035d7f888f736fda04ef70c10d33bda8383feae98",
}
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

_UNCACHEABLE_SCHEMA_CHECK_KEY = object()
_SCHEMA_CHECK_CACHE: dict[object, str | None] = {}


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
        text = path.read_text(encoding="utf-8")
        if not _yaml_parse_cache_is_eligible():
            data = yaml.safe_load(text)
        elif text in _YAML_PARSE_CACHE:
            data = copy.deepcopy(_YAML_PARSE_CACHE[text])
        else:
            parsed = yaml.safe_load(text)
            _YAML_PARSE_CACHE[text] = parsed
            data = copy.deepcopy(parsed)
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


def _schema_check_cache_key(value: object) -> object:
    if value is None:
        return ("null",)
    if type(value) is bool:
        return ("bool", value)
    if type(value) is int:
        return ("int", value)
    if type(value) is float:
        if not math.isfinite(value):
            return _UNCACHEABLE_SCHEMA_CHECK_KEY
        return ("float", value)
    if type(value) is str:
        return ("str", value)
    if type(value) is list:
        children = []
        for child in value:
            child_key = _schema_check_cache_key(child)
            if child_key is _UNCACHEABLE_SCHEMA_CHECK_KEY:
                return _UNCACHEABLE_SCHEMA_CHECK_KEY
            children.append(child_key)
        return ("list", tuple(children))
    if type(value) is dict:
        entries = []
        for key, child in value.items():
            if type(key) is not str:
                return _UNCACHEABLE_SCHEMA_CHECK_KEY
            child_key = _schema_check_cache_key(child)
            if child_key is _UNCACHEABLE_SCHEMA_CHECK_KEY:
                return _UNCACHEABLE_SCHEMA_CHECK_KEY
            entries.append((key, child_key))
        return ("dict", tuple(entries))
    return _UNCACHEABLE_SCHEMA_CHECK_KEY


def _schema_check_error(schema: dict) -> str | None:
    key = _schema_check_cache_key(schema)
    if key is _UNCACHEABLE_SCHEMA_CHECK_KEY:
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as error:
            return f"schema is invalid: {error.message}"
        return None
    if key in _SCHEMA_CHECK_CACHE:
        return _SCHEMA_CHECK_CACHE[key]
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        diagnostic = f"schema is invalid: {error.message}"
        _SCHEMA_CHECK_CACHE[key] = diagnostic
        return diagnostic
    _SCHEMA_CHECK_CACHE[key] = None
    return None


def _validator(schema: object) -> tuple[Draft202012Validator | None, list[str]]:
    if not isinstance(schema, dict):
        return None, ["schema must be a JSON object"]
    schema_error = _schema_check_error(schema)
    if schema_error is not None:
        return None, [schema_error]
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


def reconstruct_runtime_json_artifact_ref(
    root: Path,
    repository_ref: object,
    *,
    expected_prefix: str,
    expected_suffix: str = ".json",
    label: str = "repository JSON artifact",
) -> tuple[dict | None, bytes | None, list[str]]:
    """Reconstruct runtime content identity from exact projected bytes."""
    exact_bytes, errors = _read_review_artifact(
        root,
        repository_ref,
        label,
        expected_prefix,
        expected_suffix,
    )
    if exact_bytes is None:
        return None, None, errors
    digest = _mapping(repository_ref).get("sha256")
    runtime_ref = {
        "artifactId": "sha256:" + digest,
        "sha256": digest,
        "byteLength": len(exact_bytes),
        "mediaType": "application/json",
        "repositoryPath": None,
    }
    return runtime_ref, exact_bytes, errors


def _runtime_json_artifact_ref_errors(value: object, label: str) -> list[str]:
    expected_keys = {
        "artifactId",
        "sha256",
        "byteLength",
        "mediaType",
        "repositoryPath",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        return [f"{label}: must be an exact RuntimeJsonArtifactRefV1 object"]
    errors: list[str] = []
    digest = value.get("sha256")
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        errors.append(f"{label}: sha256 must be lowercase 64-hex")
    if value.get("artifactId") != f"sha256:{digest}":
        errors.append(f"{label}: artifactId must equal 'sha256:' + sha256")
    byte_length = value.get("byteLength")
    if not isinstance(byte_length, int) or isinstance(byte_length, bool) or byte_length < 0:
        errors.append(f"{label}: byteLength must be a non-negative integer")
    if value.get("mediaType") != "application/json":
        errors.append(f"{label}: mediaType must be application/json")
    if value.get("repositoryPath") is not None:
        errors.append(f"{label}: repositoryPath must be null")
    return errors


def _content_bound_semantic_object_errors(
    value: object,
    label: str,
    *,
    expected_selector: str | None = None,
) -> list[str]:
    if not isinstance(value, dict) or set(value) != {"selector", "sha256", "payload"}:
        return [f"{label}: must be an exact ContentBoundSemanticObjectV1 object"]
    errors: list[str] = []
    selector = value.get("selector")
    if not isinstance(selector, str) or not selector:
        errors.append(f"{label}: selector must be a non-empty string")
    if expected_selector is not None and selector != expected_selector:
        errors.append(f"{label}: selector must be {expected_selector}")
    payload = value.get("payload")
    if not isinstance(payload, dict):
        errors.append(f"{label}: payload must be an object")
    elif value.get("sha256") != sha256_hex(_canonical_json_bytes(payload)):
        errors.append(f"{label}: sha256 must bind canonical JSON value payload bytes")
    return errors


def _parse_json_object_bytes(data: bytes, label: str) -> tuple[dict | None, list[str]]:
    try:
        parsed = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return None, [f"{label}: must be valid UTF-8 JSON ({_concise_parser_error(error)})"]
    if not isinstance(parsed, dict):
        return None, [f"{label}: must be a JSON object"]
    return parsed, []


def _p7_packet_namespace(role: object) -> str | None:
    return {
        "initial-reviewer": REVIEW_PACKET_PREFIX,
        "challenge": REVIEW_CHALLENGE_PACKET_PREFIX,
        "decision-necessity-challenger": REVIEW_CHALLENGE_PACKET_PREFIX,
        "materiality-assessor": REVIEW_ADJUDICATION_PACKETS_PREFIX,
        "refutation-builder": REVIEW_ADJUDICATION_PACKETS_PREFIX,
        "discovery-classifier": REVIEW_ADJUDICATION_PACKETS_PREFIX,
        "derivation-builder": REVIEW_ADJUDICATION_PACKETS_PREFIX,
        "repair-synthesizer": REVIEW_ADJUDICATION_PACKETS_PREFIX,
    }.get(role)


def _p7_output_namespace(role: object) -> str | None:
    return {
        "initial-reviewer": REVIEW_RAW_OUTPUT_PREFIX,
        "challenge": REVIEW_CHALLENGE_PREFIX,
        "decision-necessity-challenger": REVIEW_CHALLENGE_PREFIX,
        "materiality-assessor": REVIEW_ADJUDICATIONS_PREFIX,
        "refutation-builder": REVIEW_ADJUDICATIONS_PREFIX,
        "discovery-classifier": REVIEW_ADJUDICATIONS_PREFIX,
        "derivation-builder": REVIEW_ADJUDICATIONS_PREFIX,
        "repair-synthesizer": REVIEW_ADJUDICATIONS_PREFIX,
    }.get(role)


def _load_p7_adjudication_packet(
    root: Path,
    repository_ref: object,
    label: str,
    validator: Draft202012Validator | None,
) -> tuple[dict | None, list[str]]:
    packet, errors = _load_json_object_artifact(
        root,
        repository_ref,
        label,
        REVIEW_ADJUDICATION_PACKETS_PREFIX,
        REVIEW_ADJUDICATION_PACKET_SUFFIX,
        require_canonical=True,
    )
    if packet is not None and validator is not None:
        errors.extend(_schema_violations(validator, packet, label))
    return packet, errors


def _gate_a_review_packet_value(root: Path, reference: object) -> dict | None:
    data, errors = _read_review_artifact(
        root,
        reference,
        "Gate A review packet",
        REVIEW_PACKET_PREFIX,
        REVIEW_PACKET_SUFFIX,
    )
    if data is None or errors:
        return None
    value, parse_errors = _parse_json_object_bytes(data, "Gate A review packet")
    return value if not parse_errors else None


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


def _load_canonical_json_value_object_artifact(
    root: Path,
    reference: object,
    label: str,
    prefix: str,
    suffix: str,
) -> tuple[dict | None, list[str]]:
    data, errors = _read_review_artifact(
        root,
        reference,
        label,
        prefix,
        suffix,
    )
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
            f"{label}: artifact must be valid JSON "
            f"({_concise_parser_error(error)})"
        ]

    if not isinstance(parsed, dict):
        return None, errors + [f"{label}: artifact must be a JSON object"]

    if data != _canonical_json_bytes(parsed):
        errors.append(
            f"{label}: artifact must use canonical JSON value serialization "
            "without a trailing newline"
        )

    return parsed, errors


def _load_meta_schema_validator(
    root: Path, reference: object, label: str
) -> tuple[Draft202012Validator | None, list[str]]:
    """Load an immutable content-addressed meta-schema artifact."""
    data, errors = _read_review_artifact(
        root, reference, label, REVIEW_META_SCHEMAS_PREFIX, REVIEW_META_SCHEMA_SUFFIX
    )
    if data is None:
        return None, errors
    try:
        schema = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return None, errors + [
            f"{label}: meta-schema must be valid JSON "
            f"({_concise_parser_error(error)})"
        ]
    validator, validator_errors = _validator(schema)
    if validator is None:
        return None, errors + [f"{label}: {error}" for error in validator_errors]
    return validator, errors


def _protocol_profile_map(bundle: object) -> dict[str, dict]:
    profiles: dict[str, dict] = {}
    for profile in _sequence(_mapping(bundle).get("reviewer_profiles")):
        if not isinstance(profile, dict):
            continue
        profile_id = profile.get("profile_id")
        if isinstance(profile_id, str) and profile_id not in profiles:
            profiles[profile_id] = profile
    return profiles


def _statically_qualifying_reviewer_profile(profile: dict) -> bool:
    if profile.get("frontier_eligible") is not True:
        return False
    resolution = _mapping(profile.get("identity_resolution"))
    kind = resolution.get("kind")
    return kind == "provider-reported" or (
        kind == "pinned-request-model"
        and resolution.get("request_model_is_immutable_version") is True
    )


def _reviewer_acquisition_policy_errors(bundle: dict, label: str) -> list[str]:
    schema_version = bundle.get("protocol_bundle_schema_version")
    if schema_version not in (5, 6, 7):
        return []
    policy = _mapping(_mapping(bundle.get("policies")).get("reviewer_acquisition"))
    errors: list[str] = []
    if policy.get("mode") != "minimum-effective-independent-v1":
        errors.append(
            f"{label}: protocol v{schema_version} reviewer acquisition mode must be "
            "minimum-effective-independent-v1"
        )
    profile_order = _sequence(policy.get("profile_order"))
    ordered_ids = [item for item in profile_order if isinstance(item, str)]
    profile_ids = [
        profile.get("profile_id")
        for profile in _sequence(bundle.get("reviewer_profiles"))
        if isinstance(profile, dict) and isinstance(profile.get("profile_id"), str)
    ]
    if len(ordered_ids) != len(set(ordered_ids)):
        errors.append(f"{label}: reviewer acquisition profile_order contains duplicates")
    if len(ordered_ids) != len(profile_ids) or set(ordered_ids) != set(profile_ids):
        errors.append(
            f"{label}: reviewer acquisition profile_order must be an exact "
            "permutation of reviewer profile IDs"
        )
    return errors


def _protocol_bundle_errors(root: Path, bundle: dict, label: str) -> list[str]:
    """Validate every immutable artifact referenced by one bundle."""
    errors: list[str] = []
    prompts = _mapping(bundle.get("prompts"))
    for key in ("initial-reviewer", "adjudication", "challenge", "repair"):
        _, artifact_errors = _read_review_artifact(root, _mapping(prompts.get(key)), f"{label}: prompts.{key}", REVIEW_PROMPT_PREFIX, REVIEW_PROMPT_SUFFIX)
        errors.extend(artifact_errors)
    schemas = _mapping(bundle.get("schemas"))
    keys = ["raw-review-output", "execution-receipt", "challenge-output"]
    version = bundle.get("protocol_bundle_schema_version")
    if version in (2, 3, 4, 5, 6, 7):
        keys.append("challenge-packet")
    if version == 7:
        keys.extend(
            (
                "adjudication-packet",
                "adjudication-output",
                "finding-adjudication-supplement",
            )
        )
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
    errors.extend(_reviewer_acquisition_policy_errors(bundle, label))
    return errors


def _bundle_selected_validators(root: Path, bundle: dict | None, label: str) -> tuple[dict[str, Draft202012Validator | None], list[str]]:
    validators: dict[str, Draft202012Validator | None] = {}
    errors: list[str] = []
    if bundle is None:
        return validators, errors
    schemas = _mapping(bundle.get("schemas"))
    for key in (
        "raw-review-output",
        "execution-receipt",
        "challenge-output",
        "challenge-packet",
        "adjudication-packet",
        "adjudication-output",
        "finding-adjudication-supplement",
    ):
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


def _protocol_bundle_meta_schema_reference(version: object) -> dict | None:
    """Select the immutable meta-schema for one protocol-bundle schema version."""
    if version in (1, 2, 3):
        return dict(LEGACY_PROTOCOL_BUNDLE_META_SCHEMA_REFERENCE)
    if version == 4:
        return dict(PROTOCOL_V4_META_SCHEMA_REFERENCE)
    if version == 5:
        return dict(PROTOCOL_V5_META_SCHEMA_REFERENCE)
    if version == 6:
        return dict(PROTOCOL_V6_META_SCHEMA_REFERENCE)
    if version == 7:
        return dict(PROTOCOL_V7_META_SCHEMA_REFERENCE)
    return None


def _load_protocol_bundle_document(root: Path, reference: object, label: str, cache: dict[str, tuple[dict | None, list[str]]], chain_paths: set[str] | None = None, chain_ids: set[str] | None = None) -> tuple[dict | None, list[str]]:
    bundle_reference = _mapping(reference)
    cache_key = bundle_reference.get("sha256")
    # Cache only fully checked acyclic chains.
    if chain_paths is None and isinstance(cache_key, str) and cache_key in cache:
        return cache[cache_key]
    bundle, errors = _load_json_object_artifact(root, bundle_reference, label, REVIEW_PROTOCOLS_PREFIX, REVIEW_PROTOCOL_BUNDLE_SUFFIX, require_canonical=True)
    if bundle is None:
        return None, errors
    version = bundle.get("protocol_bundle_schema_version")
    meta_reference = _protocol_bundle_meta_schema_reference(version)
    if meta_reference is None:
        errors.append(f"{label}: unsupported hostile-review protocol bundle schema version {version!r}")
        return bundle, errors
    validator, meta_errors = _load_meta_schema_validator(root, meta_reference, f"{label}: protocol-bundle meta-schema")
    errors.extend(meta_errors)
    if validator is not None:
        errors.extend(_schema_violations(validator, bundle, label))
    if version in (4, 5, 6, 7):
        meta_schemas = _mapping(bundle.get("meta_schemas"))
        declared_protocol_bundle = _mapping(meta_schemas.get("protocol-bundle"))
        expected_protocol_bundle = {
            4: PROTOCOL_V4_META_SCHEMA_REFERENCE,
            5: PROTOCOL_V5_META_SCHEMA_REFERENCE,
            6: PROTOCOL_V6_META_SCHEMA_REFERENCE,
            7: PROTOCOL_V7_META_SCHEMA_REFERENCE,
        }[version]
        if declared_protocol_bundle != expected_protocol_bundle:
            errors.append(
                f"{label}: protocol v{version} must bind the exact published "
                "protocol-bundle meta-schema"
            )
        declared_review_evidence = _mapping(meta_schemas.get("review-evidence"))
        if declared_review_evidence != LEGACY_REVIEW_EVIDENCE_META_SCHEMA_REFERENCE:
            errors.append(
                f"{label}: protocol v{version} must bind the exact published "
                "review-evidence meta-schema"
            )
        for key in ("protocol-bundle", "review-evidence"):
            _, binding_errors = _load_meta_schema_validator(root, _mapping(meta_schemas.get(key)), f"{label}: meta_schemas.{key}")
            errors.extend(binding_errors)
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
    predecessor = bundle.get("predecessor")
    if version in (2, 3, 4, 5, 6, 7):
        if not isinstance(predecessor, dict):
            errors.append(f"{label}: schema-version-{version} bundle requires predecessor")
        else:
            if version == 7 and predecessor != PROTOCOL_V7_PREDECESSOR_REFERENCE:
                errors.append(
                    f"{label}: protocol v7 predecessor must be the exact published "
                    "v6 bundle"
                )
            _, predecessor_errors = _load_protocol_bundle_document(root, predecessor, f"{label}: predecessor", cache, paths, ids)
            errors.extend(predecessor_errors)
    elif predecessor is not None:
        errors.append(f"{label}: schema-version-1 bundle must not declare predecessor")
    if chain_paths is None and isinstance(cache_key, str):
        cache[cache_key] = (bundle, list(errors))
    return bundle, errors


def _current_protocol_bundle_errors(root: Path, manifest: dict, cache: dict[str, tuple[dict | None, list[str]]]) -> tuple[object, dict | None, list[str]]:
    hostile_review = _mapping(_mapping(manifest.get("policy")).get("hostile_review"))
    reference = _mapping(hostile_review.get("current_protocol_bundle"))
    label = "policy.hostile_review.current_protocol_bundle"
    bundle, errors = _load_protocol_bundle_document(root, reference, label, cache)
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
    # v4 establishes the fixed v3 lineage and binds its interpretation contract.
    if bundle is not None and bundle.get("protocol_bundle_schema_version") == 4:
        predecessor = _mapping(bundle.get("predecessor"))
        if predecessor.get("path") != "formal/reviews/protocols/gate-a-campaign-protocol-v3.json" or predecessor.get("sha256") != "cb46d3e2ba7e4832a8877de679412fb0ec9d520327ef7c4dc0f1c6304cd222c6":
            errors.append(f"{label}: current protocol v4 predecessor must be the exact published v3 bundle")
    # v5 establishes the fixed v4 lineage and deterministic reviewer acquisition.
    if bundle is not None and bundle.get("protocol_bundle_schema_version") == 5:
        predecessor = _mapping(bundle.get("predecessor"))
        if predecessor.get("path") != "formal/reviews/protocols/gate-a-campaign-protocol-v4.json" or predecessor.get("sha256") != "f059401f092a9133fb5729db5d0f7b94346c52389bcd4deb81583152ad3b09ac":
            errors.append(f"{label}: current protocol v5 predecessor must be the exact published v4 bundle")
    # v6 establishes the fixed v5 lineage and canonical provider-reported identity.
    if bundle is not None and bundle.get("protocol_bundle_schema_version") == 6:
        predecessor = _mapping(bundle.get("predecessor"))
        if predecessor.get("path") != "formal/reviews/protocols/gate-a-campaign-protocol-v5.json" or predecessor.get("sha256") != "b9dc015188b89f605bf8252bf47ff5497be54668cc274e953146577f1a76e091":
            errors.append(f"{label}: current protocol v6 predecessor must be the exact published v5 bundle")
    if bundle is not None and bundle.get("protocol_bundle_schema_version") in (4, 5, 6):
        evidence_binding = _mapping(_mapping(bundle.get("meta_schemas")).get("review-evidence"))
        if hostile_review.get("evidence_schema") != evidence_binding.get("path"):
            errors.append(f"{label}: current hostile-review evidence_schema path must equal the current protocol-bound review-evidence meta-schema path")
    return reference, bundle, errors


def _inactive_protocol_v7_candidate_errors(
    root: Path,
    cache: dict[str, tuple[dict | None, list[str]]],
) -> list[str]:
    """Validate the exact protocol-v7 candidate without selecting it as current."""
    label = "inactive protocol v7 candidate"
    bundle, errors = _load_protocol_bundle_document(
        root,
        PROTOCOL_V7_BUNDLE_REFERENCE,
        label,
        cache,
    )
    if bundle is not None:
        if bundle.get("protocol_bundle_schema_version") != 7:
            errors.append(f"{label}: protocol bundle schema version must be 7")
        if bundle.get("protocol_id") != "gate-a-campaign-protocol-v7":
            errors.append(f"{label}: protocol_id must be gate-a-campaign-protocol-v7")
        if bundle.get("predecessor") != PROTOCOL_V7_PREDECESSOR_REFERENCE:
            errors.append(f"{label}: predecessor must be the exact published v6 bundle")
    return errors


def _load_execution_receipt(
    root: Path,
    reference: object,
    label: str,
    validator: Draft202012Validator | None,
) -> tuple[dict | None, list[str]]:
    receipt, errors = _load_canonical_json_value_object_artifact(
        root,
        reference,
        label,
        REVIEW_EXECUTIONS_PREFIX,
        REVIEW_EXECUTION_SUFFIX,
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


P7_ADJUDICATION_ROLE_TASKS = {
    "materiality-assessor": {"materiality-assessment"},
    "refutation-builder": {"refutation"},
    "discovery-classifier": {"discovery-classification"},
    "derivation-builder": {
        "unique-correction-derivation",
        "realization-scope-derivation",
    },
    "repair-synthesizer": {"repair-realization"},
}


def _validate_adjudication_protocol_output(
    root: Path,
    reference: object,
    validator: Draft202012Validator | None,
    packet: dict | None,
) -> tuple[dict | None, list[str]]:
    output, errors = _load_json_object_artifact(
        root,
        reference,
        "adjudication output",
        REVIEW_ADJUDICATIONS_PREFIX,
        REVIEW_JSON_OUTPUT_SUFFIX,
        require_canonical=False,
    )
    if output is None:
        return None, errors
    if validator is not None:
        errors.extend(_schema_violations(validator, output, "adjudication output"))
    if packet is None:
        errors.append("adjudication output: canonical adjudication packet is unavailable")
    elif output.get("task") != packet.get("task"):
        errors.append("adjudication output: task must equal the bound adjudication packet")
    return output, errors


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
        elif role in {CHALLENGE_ROLE, "decision-necessity-challenger"} and challenge_packet is not None: _parsed,derived=_validate_challenge_protocol_output(root,raw,validators.get("challenge-output"),challenge_packet)
        elif (
            receipt.get("receipt_schema_version") == "4.0"
            and role in P7_ADJUDICATION_ROLE_TASKS
        ):
            packet_ref = _mapping(receipt.get("input")).get("packet")
            packet, packet_errors = _load_p7_adjudication_packet(
                root,
                packet_ref,
                f"{alabel}: adjudication packet",
                validators.get("adjudication-packet"),
            )
            derived = list(packet_errors)
            _parsed, output_errors = _validate_adjudication_protocol_output(
                root,
                raw,
                validators.get("adjudication-output"),
                packet,
            )
            derived.extend(output_errors)
            if packet is not None and packet.get("task") not in P7_ADJUDICATION_ROLE_TASKS[role]:
                derived.append(
                    f"adjudication output: role {role!r} cannot perform task "
                    f"{packet.get('task')!r}"
                )
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
                if resolved.get("model_version") == "latest":
                    errors.append(f"{label}: resolved identity model_version must not be latest")
                if kind=="provider-reported":
                    if not isinstance(qualifying.get("provider_model"),str) or not qualifying.get("provider_model"): errors.append(f"{label}: provider-reported identity requires a non-empty provider_model")
                    elif qualifying.get("provider_model") == "latest": errors.append(f"{label}: provider-reported provider_model must not be latest")
                    elif resolved.get("model_version")!=qualifying.get("provider_model"): errors.append(f"{label}: provider-reported model_version must equal the qualified attempt provider_model")
                elif kind=="pinned-request-model":
                    if resolution.get("request_model_is_immutable_version") is not True: errors.append(f"{label}: pinned-request-model requires request_model_is_immutable_version = true")
                    if profile.get("request_model") == "latest" and resolution.get("request_model_is_immutable_version") is True: errors.append(f"{label}: pinned-request-model request_model must not be latest")
                    if resolved.get("model_version")!=profile.get("request_model"): errors.append(f"{label}: pinned-request-model model_version must equal the profile request_model")
    return errors,qualifying

def _decode_canonical_base64url(value: object, label: str) -> tuple[bytes | None, list[str]]:
    if not isinstance(value, str) or not value:
        return None, [f"{label}: must be a non-empty canonical base64url string"]
    if re.fullmatch(r"[A-Za-z0-9_-]+", value) is None:
        return None, [f"{label}: must use unpadded base64url"]
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except ValueError:
        return None, [f"{label}: invalid base64url"]
    encoded = base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii")
    if encoded != value:
        return None, [f"{label}: base64url representation is not canonical"]
    return decoded, []


def _inline_exact_bytes(value: object, label: str) -> tuple[bytes | None, list[str]]:
    if not isinstance(value, dict) or set(value) != {"encoding", "data"}:
        return None, [f"{label}: invalid InlineExactBytesV1 shape"]
    encoding = value.get("encoding")
    data = value.get("data")
    if encoding == "utf-8":
        if not isinstance(data, str):
            return None, [f"{label}: utf-8 data must be a string"]
        return data.encode("utf-8"), []
    if encoding == "base64url":
        decoded, errors = _decode_canonical_base64url(data, f"{label}.data")
        if decoded is not None:
            try:
                decoded.decode("utf-8")
            except UnicodeDecodeError:
                pass
            else:
                errors.append(f"{label}: valid UTF-8 exact bytes must use utf-8 encoding")
        return decoded, errors
    return None, [f"{label}: encoding must be utf-8 or base64url"]


def _p7_discovery_output_errors(packet: dict, result: object, label: str) -> list[str]:
    errors: list[str] = []
    revision = _mapping(packet.get("revision"))
    ordinal = revision.get("ordinal")
    if isinstance(result, dict) and "classification_statements" in result:
        statements = _sequence(result.get("classification_statements"))
        identities = [sha256_hex(_canonical_json_bytes(statement)) for statement in statements]
        if len(identities) != len(set(identities)):
            errors.append(f"{label}: duplicate canonical discovery statement identity")
        cause_ordinal = _mapping(result.get("earliest_unresolved_cause")).get(
            "classification_statement_ordinal"
        )
        if not isinstance(cause_ordinal, int) or not 0 <= cause_ordinal < len(statements):
            errors.append(f"{label}: earliest unresolved cause ordinal is out of range")
        if ordinal != 0:
            errors.append(f"{label}: initial discovery result requires revision ordinal 0")
    elif _mapping(result).get("kind") == "revised-candidate":
        if ordinal != 1:
            errors.append(f"{label}: revised discovery candidate requires ordinal 1")
        selector = _mapping(revision.get("closure_subject")).get("selector")
        disposition = _mapping(_mapping(result).get("statement")).get(
            "semantic_disposition"
        )
        expected = {
            "gate-a-no-normative-impact-candidate-challenge-v1": "no-normative-impact",
            "gate-a-decision-necessity-candidate-challenge-v1": "decision-required",
        }.get(selector)
        if expected is None or disposition != expected:
            errors.append(f"{label}: targeted discovery revision changed closure family")
    elif _mapping(result).get("kind") == "not-established":
        if ordinal != 1:
            errors.append(f"{label}: discovery withdrawal is allowed only for ordinal 1")
    for node in _walk_json(result):
        if isinstance(node, dict) and node.get("kind") == "prior-challenge-objection":
            if ordinal != 1:
                errors.append(f"{label}: prior-challenge citation requires ordinal 1")
            objections = _sequence(
                _mapping(_mapping(revision.get("prior_challenge")).get("output")).get(
                    "objections"
                )
            )
            objection_id = node.get("challenge_objection_id")
            if sum(_mapping(item).get("challenge_objection_id") == objection_id for item in objections) != 1:
                errors.append(f"{label}: prior challenge objection citation is not exact")
    return errors


def _walk_json(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_json(child)


def _p7_unique_correction_errors(result: object, label: str) -> list[str]:
    if _mapping(result).get("kind") == "not-established":
        return []
    candidate = _mapping(result)
    requirements = _sequence(candidate.get("correction_requirements"))
    identities = [
        sha256_hex(_canonical_json_bytes({"postcondition": _mapping(item).get("postcondition")}))
        for item in requirements
    ]
    errors: list[str] = []
    if len(identities) != len(set(identities)):
        errors.append(f"{label}: duplicate canonical correction requirement")
    covered: set[int] = set()
    for claim in _sequence(candidate.get("derivation_claims")):
        for ordinal in _sequence(_mapping(claim).get("requirement_ordinals")):
            if not isinstance(ordinal, int) or isinstance(ordinal, bool) or not 0 <= ordinal < len(requirements):
                errors.append(f"{label}: derivation claim requirement ordinal is invalid")
            else:
                covered.add(ordinal)
    if covered != set(range(len(requirements))):
        errors.append(f"{label}: every correction requirement must be covered")
    return errors


def _qualified_closure_result(closure: object) -> object:
    closure = _mapping(closure)
    producer = _mapping(closure.get("producer"))
    challenge = _mapping(closure.get("challenge"))
    challenge_output = _mapping(challenge.get("output"))
    if challenge_output.get("objections") != []:
        return None
    return _mapping(producer.get("output")).get("result")


def _p7_realization_scope_errors(packet: dict, result: object, label: str) -> list[str]:
    if _mapping(result).get("kind") == "not-established":
        return []
    scope = _mapping(result)
    readable = _sequence(scope.get("readable_paths"))
    writable = _sequence(scope.get("writable_paths"))
    errors: list[str] = []
    if not set(writable).issubset(set(readable)):
        errors.append(f"{label}: writable_paths must be a subset of readable_paths")
    correction = _mapping(
        _qualified_closure_result(
            _mapping(packet.get("task_input")).get("qualified_unique_correction")
        )
    )
    requirement_count = len(_sequence(correction.get("correction_requirements")))
    surfaces = _sequence(
        _mapping(scope.get("completeness_argument")).get("requirement_surfaces")
    )
    ordinals = [_mapping(item).get("requirement_ordinal") for item in surfaces]
    if sorted(ordinal for ordinal in ordinals if isinstance(ordinal, int)) != list(range(requirement_count)) or len(ordinals) != requirement_count:
        errors.append(f"{label}: requirement_surfaces must cover each requirement exactly once")
    surface_paths: set[str] = set()
    for item in surfaces:
        for path in _sequence(_mapping(item).get("surface_paths")):
            if path not in readable:
                errors.append(f"{label}: surface path is outside readable_paths")
            if isinstance(path, str):
                surface_paths.add(path)
    if surface_paths != set(readable):
        errors.append(f"{label}: readable_paths must equal union of requirement surfaces")
    justifications = _sequence(
        _mapping(scope.get("minimal_write_authority_argument")).get(
            "writable_path_justifications"
        )
    )
    justified = [_mapping(item).get("path_bytes_base64url") for item in justifications]
    if sorted(justified) != sorted(writable) or len(justified) != len(writable):
        errors.append(f"{label}: every writable path requires exactly one justification")
    for item in justifications:
        for ordinal in _sequence(_mapping(item).get("requirement_ordinals")):
            if not isinstance(ordinal, int) or not 0 <= ordinal < requirement_count:
                errors.append(f"{label}: writable justification requirement ordinal is invalid")
    review_packet = _mapping(packet.get("review_packet"))
    controlling_paths = set()
    for authority in _sequence(_mapping(review_packet.get("payload")).get("authority_contents")):
        if _mapping(authority).get("role") in {
            "normative-spec",
            "architecture-decision",
            "abstraction-constraint",
        }:
            path = _mapping(authority).get("path")
            if isinstance(path, str):
                controlling_paths.add(
                    base64.urlsafe_b64encode(path.encode("utf-8")).rstrip(b"=").decode("ascii")
                )
    for path in writable:
        if path in controlling_paths:
            errors.append(f"{label}: controlling product-authority path is not writable")
    return errors


def _candidate_view_entry_bytes(state: object, label: str) -> tuple[bytes | None, list[str]]:
    state = _mapping(state)
    if state.get("kind") in {"blob", "symlink"}:
        return _inline_exact_bytes(state.get("content"), f"{label}.content")
    return None, []


def _p7_candidate_view_errors(
    root: Path,
    candidate_view: object,
    *,
    expected_coverage: str,
    expected_paths: set[str] | None,
    label: str,
) -> list[str]:
    errors = _content_bound_semantic_object_errors(
        candidate_view,
        label,
        expected_selector="gate-a-candidate-view-v1",
    )
    payload = _mapping(_mapping(candidate_view).get("payload"))
    coverage = _mapping(payload.get("coverage")).get("kind")
    if coverage != expected_coverage:
        errors.append(f"{label}: coverage must be {expected_coverage}")
    object_format = payload.get("git_object_format")
    object_length = 40 if object_format == "sha1" else 64
    root_tree = payload.get("root_tree_object_id")
    if not isinstance(root_tree, str) or len(root_tree) != object_length:
        errors.append(f"{label}: root tree object ID length is invalid")
    entries = _sequence(payload.get("entries"))
    decoded_paths: list[bytes] = []
    encoded_paths: list[str] = []
    for index, entry in enumerate(entries):
        entry = _mapping(entry)
        encoded = entry.get("path_bytes_base64url")
        decoded, path_errors = _decode_canonical_base64url(encoded, f"{label}.entries[{index}].path")
        errors.extend(path_errors)
        if decoded is None:
            continue
        decoded_paths.append(decoded)
        encoded_paths.append(encoded)
        try:
            utf8 = decoded.decode("utf-8")
        except UnicodeDecodeError:
            utf8 = None
        if entry.get("path_utf8") != utf8:
            errors.append(f"{label}.entries[{index}]: path_utf8 mismatch")
        state = _mapping(entry.get("state"))
        if state.get("kind") == "gitlink":
            object_id = state.get("object_id")
            if not isinstance(object_id, str) or len(object_id) != object_length:
                errors.append(f"{label}.entries[{index}]: gitlink object ID length mismatch")
        _bytes, byte_errors = _candidate_view_entry_bytes(state, f"{label}.entries[{index}]")
        errors.extend(byte_errors)
    if decoded_paths != sorted(decoded_paths) or len(decoded_paths) != len(set(decoded_paths)):
        errors.append(f"{label}: candidate paths must be unique in canonical raw-byte order")
    if expected_paths is not None and set(encoded_paths) != expected_paths:
        errors.append(f"{label}: candidate view path set does not equal readable_paths")
    if coverage == "complete":
        if any(_mapping(entry).get("state", {}).get("kind") == "absent" for entry in entries):
            errors.append(f"{label}: complete candidate view cannot contain absent entries")
        if isinstance(root_tree, str):
            process = subprocess.run(
                ["git", "-C", str(root), "ls-tree", "-rz", "-r", root_tree],
                capture_output=True,
                check=False,
            )
            if process.returncode != 0:
                errors.append(f"{label}: root tree object is unavailable")
            else:
                actual_paths = [
                    record.split(b"\t", 1)[1]
                    for record in process.stdout.split(b"\0")
                    if b"\t" in record
                ]
                if decoded_paths != actual_paths:
                    errors.append(f"{label}: complete candidate view is not the full tree materialization")
    return errors


def _p7_repair_errors(packet: dict, result: object, label: str) -> list[str]:
    if _mapping(result).get("kind") == "not-established":
        return []
    repair = _mapping(result)
    task_input = _mapping(packet.get("task_input"))
    correction = _mapping(
        _qualified_closure_result(task_input.get("qualified_unique_correction"))
    )
    requirements = _sequence(correction.get("correction_requirements"))
    realizations = _sequence(repair.get("requirement_realizations"))
    operations = _sequence(repair.get("operations"))
    errors: list[str] = []
    if len(realizations) != len(requirements) or [
        _mapping(item).get("requirement_ordinal") for item in realizations
    ] != list(range(len(requirements))):
        errors.append(f"{label}: requirement realizations must be ordinal-complete")
    operation_paths = [_mapping(item).get("path_bytes_base64url") for item in operations]
    if operation_paths != sorted(operation_paths) or len(operation_paths) != len(set(operation_paths)):
        errors.append(f"{label}: operation paths must be unique in canonical order")
    scope = _mapping(
        _qualified_closure_result(task_input.get("qualified_realization_scope"))
    )
    writable = set(_sequence(scope.get("writable_paths")))
    for path in operation_paths:
        if path not in writable:
            errors.append(f"{label}: operation path is outside qualified writable scope")
    referenced: set[str] = set()
    all_already = True
    for realization in realizations:
        realization = _mapping(realization)
        if realization.get("kind") == "patch-realized":
            all_already = False
            referenced.update(_sequence(realization.get("operation_paths")))
    if referenced != set(operation_paths):
        errors.append(f"{label}: patch-realized operation union must equal operations")
    if (not operations) != all_already:
        errors.append(f"{label}: operations must be empty iff all requirements are already-realized")
    candidate_view = _mapping(task_input.get("candidate_view"))
    entries = {
        _mapping(entry).get("path_bytes_base64url"): _mapping(entry).get("state")
        for entry in _sequence(_mapping(candidate_view.get("payload")).get("entries"))
    }
    for index, operation in enumerate(operations):
        operation = _mapping(operation)
        path = operation.get("path_bytes_base64url")
        after = _mapping(operation.get("after_state"))
        if after.get("kind") in {"blob", "symlink"}:
            _bytes, inline_errors = _candidate_view_entry_bytes(after, f"{label}.operations[{index}].after_state")
            errors.extend(inline_errors)
        if after == entries.get(path):
            errors.append(f"{label}: repair operation must not be a no-op")
    return errors


def _p7_adjudication_semantic_errors(
    root: Path,
    packet: dict,
    output: dict,
    label: str,
) -> list[str]:
    errors: list[str] = []
    for field in ("subject", "finding"):
        errors.extend(_content_bound_semantic_object_errors(packet.get(field), f"{label}.{field}"))
    revision = _mapping(packet.get("revision"))
    if revision.get("ordinal") == 1:
        errors.extend(_content_bound_semantic_object_errors(revision.get("closure_subject"), f"{label}.revision.closure_subject"))
        objections = _sequence(
            _mapping(_mapping(revision.get("prior_challenge")).get("output")).get("objections")
        )
        if not objections:
            errors.append(f"{label}: revision requires non-empty prior hostile objections")
    task = packet.get("task")
    result = output.get("result")
    if task == "discovery-classification":
        errors.extend(_p7_discovery_output_errors(packet, result, label))
    elif task == "unique-correction-derivation":
        errors.extend(_p7_unique_correction_errors(result, label))
        target = _mapping(packet.get("task_input")).get("target_classification")
        errors.extend(_content_bound_semantic_object_errors(target, f"{label}.target_classification", expected_selector="gate-a-discovery-classification-statement-v1"))
    elif task == "realization-scope-derivation":
        errors.extend(_p7_realization_scope_errors(packet, result, label))
        readable = set(_sequence(_mapping(result).get("readable_paths"))) if _mapping(result).get("kind") != "not-established" else None
        errors.extend(_p7_candidate_view_errors(root, _mapping(packet.get("task_input")).get("candidate_view"), expected_coverage="complete", expected_paths=None, label=f"{label}.candidate_view"))
    elif task == "repair-realization":
        errors.extend(_p7_repair_errors(packet, result, label))
        scope = _mapping(_qualified_closure_result(_mapping(packet.get("task_input")).get("qualified_realization_scope")))
        errors.extend(_p7_candidate_view_errors(root, _mapping(packet.get("task_input")).get("candidate_view"), expected_coverage="readable-paths", expected_paths=set(_sequence(scope.get("readable_paths"))), label=f"{label}.candidate_view"))
    return errors


def _bound_execution_evidence(
    root: Path,
    value: object,
    label: str,
    *,
    owner_receipt_refs: list[dict],
    bundle: dict,
    bundle_sha256: str,
    validators: dict[str, Draft202012Validator | None],
) -> tuple[dict | None, list[str]]:
    """Resolve and validate one closed BoundExecutionEvidenceV1 graph node."""
    required = {"execution_receipt", "packet", "raw_output", "parsed_output"}
    if not isinstance(value, dict) or set(value) != required:
        return None, [f"{label}: must be an exact BoundExecutionEvidenceV1 object"]
    errors: list[str] = []
    receipt_runtime = value.get("execution_receipt")
    errors.extend(_runtime_json_artifact_ref_errors(receipt_runtime, f"{label}.execution_receipt"))
    digest = _mapping(receipt_runtime).get("sha256")
    matching = [
        ref
        for ref in owner_receipt_refs
        if isinstance(ref, dict) and ref.get("sha256") == digest
    ]
    if len(matching) != 1:
        errors.append(
            f"{label}: owning evidence root must contain exactly one receipt locator "
            f"for bound sha256; found {len(matching)}"
        )
        return None, errors
    receipt_ref = matching[0]
    reconstructed_receipt, receipt_bytes, reconstruction_errors = (
        reconstruct_runtime_json_artifact_ref(
            root,
            receipt_ref,
            expected_prefix=REVIEW_EXECUTIONS_PREFIX,
            expected_suffix=REVIEW_EXECUTION_SUFFIX,
            label=f"{label}.execution_receipt",
        )
    )
    errors.extend(reconstruction_errors)
    if reconstructed_receipt != receipt_runtime:
        errors.append(f"{label}: reconstructed receipt runtime identity does not match")
    if receipt_bytes is None:
        return None, errors
    receipt, parse_errors = _parse_json_object_bytes(
        receipt_bytes, f"{label}.execution_receipt"
    )
    errors.extend(parse_errors)
    if receipt is None:
        return None, errors
    if receipt_bytes != _canonical_json_bytes(receipt):
        errors.append(f"{label}: execution receipt must use canonical JSON value bytes")

    packet_binding = value.get("packet")
    if not isinstance(packet_binding, dict) or set(packet_binding) != {"artifact", "payload"}:
        errors.append(f"{label}.packet: must contain exactly artifact and payload")
        return None, errors
    packet_runtime = packet_binding.get("artifact")
    errors.extend(_runtime_json_artifact_ref_errors(packet_runtime, f"{label}.packet.artifact"))
    role = receipt.get("role")
    packet_prefix = _p7_packet_namespace(role)
    if packet_prefix is None:
        errors.append(f"{label}: role {role!r} has no P7 packet namespace")
        return None, errors
    packet_ref = _mapping(receipt.get("input")).get("packet")
    reconstructed_packet, packet_bytes, packet_errors = reconstruct_runtime_json_artifact_ref(
        root,
        packet_ref,
        expected_prefix=packet_prefix,
        expected_suffix=".json",
        label=f"{label}.packet",
    )
    errors.extend(packet_errors)
    if reconstructed_packet != packet_runtime:
        errors.append(f"{label}: reconstructed packet runtime identity does not match")
    if packet_bytes is None:
        return None, errors
    packet_payload, packet_parse_errors = _parse_json_object_bytes(
        packet_bytes, f"{label}.packet"
    )
    errors.extend(packet_parse_errors)
    if packet_payload is None:
        return None, errors
    if packet_bytes != _canonical_json_document_bytes(packet_payload):
        errors.append(f"{label}: packet must use canonical JSON document bytes")
    if packet_payload != packet_binding.get("payload"):
        errors.append(f"{label}: embedded packet payload does not equal exact packet bytes")

    if role in P7_ADJUDICATION_ROLE_TASKS:
        validator = validators.get("adjudication-packet")
    elif role in {"challenge", "decision-necessity-challenger"}:
        validator = validators.get("challenge-packet")
    else:
        validator = None
    if validator is not None:
        errors.extend(_schema_violations(validator, packet_payload, f"{label}.packet"))

    raw_runtime = value.get("raw_output")
    errors.extend(_runtime_json_artifact_ref_errors(raw_runtime, f"{label}.raw_output"))
    qualifying = _unique_qualifying_attempt(receipt)
    if qualifying is None:
        errors.append(f"{label}: receipt must have exactly one qualified attempt")
        return None, errors
    raw_ref = qualifying.get("raw_output")
    output_prefix = _p7_output_namespace(role)
    if output_prefix is None:
        errors.append(f"{label}: role {role!r} has no P7 output namespace")
        return None, errors
    reconstructed_raw, raw_bytes, raw_errors = reconstruct_runtime_json_artifact_ref(
        root,
        raw_ref,
        expected_prefix=output_prefix,
        expected_suffix=".json",
        label=f"{label}.raw_output",
    )
    errors.extend(raw_errors)
    if reconstructed_raw != raw_runtime:
        errors.append(f"{label}: reconstructed raw-output runtime identity does not match")
    if raw_bytes is None:
        return None, errors
    parsed_output, output_parse_errors = _parse_json_object_bytes(
        raw_bytes, f"{label}.raw_output"
    )
    errors.extend(output_parse_errors)
    if parsed_output is None:
        return None, errors
    if parsed_output != value.get("parsed_output"):
        errors.append(f"{label}: parsed_output does not equal exact sealed raw bytes")
    if role in P7_ADJUDICATION_ROLE_TASKS:
        errors.extend(
            _p7_adjudication_semantic_errors(
                root,
                packet_payload,
                parsed_output,
                f"{label}.adjudication",
            )
        )

    receipt_errors, checked_attempt = _validate_execution_receipt(
        root,
        receipt,
        f"{label}.execution_receipt",
        _protocol_profile_map(bundle),
        bundle_sha256,
        validators,
        packet_payload if role in {"challenge", "decision-necessity-challenger"} else None,
    )
    errors.extend(receipt_errors)
    if checked_attempt is not qualifying:
        errors.append(f"{label}: qualifying attempt resolution is inconsistent")
    return {
        "receipt": receipt,
        "packet": packet_payload,
        "output": parsed_output,
        "receipt_ref": receipt_ref,
        "execution_receipt": receipt_runtime,
        "raw_output": raw_runtime,
    }, errors


P7_DIRECT_CHALLENGE_FAMILIES = {
    "gate-a-materiality-assessment-challenge-v1": {
        "family": "materiality-assessment",
        "kind": "materiality",
        "role": "materiality-assessor",
        "task": "materiality-assessment",
        "subject_selector": "gate-a-finding-adjudication-subject-v1",
        "candidate_kind": None,
    },
    "gate-a-refutation-candidate-challenge-v1": {
        "family": "refutation",
        "kind": "refutation",
        "role": "refutation-builder",
        "task": "refutation",
        "subject_selector": "gate-a-finding-adjudication-subject-v1",
        "candidate_kind": "refutation-candidate",
    },
    "gate-a-unique-correction-candidate-challenge-v1": {
        "family": "unique-correction",
        "kind": "derivation",
        "role": "derivation-builder",
        "task": "unique-correction-derivation",
        "subject_selector": "gate-a-surviving-material-resolution-subject-v1",
        "candidate_kind": "unique-correction-candidate",
    },
    "gate-a-realization-scope-candidate-challenge-v1": {
        "family": "realization-scope",
        "kind": "derivation",
        "role": "derivation-builder",
        "task": "realization-scope-derivation",
        "subject_selector": "gate-a-surviving-material-resolution-subject-v1",
        "candidate_kind": None,
    },
    "gate-a-no-normative-impact-candidate-challenge-v1": {
        "family": "no-normative-impact",
        "kind": "normative-impact",
        "role": "discovery-classifier",
        "task": "discovery-classification",
        "subject_selector": "gate-a-surviving-material-resolution-subject-v1",
        "candidate_kind": "content-bound-discovery-statement",
    },
    "gate-a-repair-realization-candidate-challenge-v1": {
        "family": "repair-realization",
        "kind": "repair",
        "role": "repair-synthesizer",
        "task": "repair-realization",
        "subject_selector": "gate-a-surviving-material-resolution-subject-v1",
        "candidate_kind": "repair-realization-candidate",
    },
}
P7_DECISION_NECESSITY_SELECTOR = "gate-a-decision-necessity-candidate-challenge-v1"


def _p7_closure_contract(bundle: dict, kind: object, selector: object) -> dict | None:
    contracts = _sequence(
        _mapping(_mapping(bundle.get("policies")).get("challenge")).get(
            "closure_contracts"
        )
    )
    matches = [
        contract
        for contract in contracts
        if isinstance(contract, dict)
        and contract.get("challenge_kind") == kind
        and contract.get("challenge_subject_selector") == selector
    ]
    return matches[0] if len(matches) == 1 else None


def _p7_direct_challenge_subject_errors(
    root: Path,
    challenge_packet: dict,
    owner_receipt_refs: list[dict],
    bundle: dict,
    bundle_sha256: str,
    validators: dict[str, Draft202012Validator | None],
    label: str,
) -> list[str]:
    challenge_subject = _mapping(challenge_packet.get("challenge_subject"))
    selector = challenge_subject.get("selector")
    family = P7_DIRECT_CHALLENGE_FAMILIES.get(selector)
    if family is None:
        return [f"{label}: unknown P7 direct-producer challenge selector {selector!r}"]
    payload = challenge_subject.get("payload")
    errors: list[str] = []
    if not isinstance(payload, dict) or set(payload) != {
        "subject_schema_version",
        "selector",
        "subject",
        "producer",
        "candidate",
    }:
        return [f"{label}: challenge subject payload has the wrong closed shape"]
    if payload.get("subject_schema_version") != 1:
        errors.append(f"{label}: subject_schema_version must be 1")
    if payload.get("selector") != selector:
        errors.append(f"{label}: payload selector must equal challenge subject selector")
    expected_sha = sha256_hex(_canonical_json_bytes(payload))
    if challenge_subject.get("sha256") != expected_sha:
        errors.append(f"{label}: challenge subject sha256 does not bind canonical payload")
    subject = payload.get("subject")
    errors.extend(
        _content_bound_semantic_object_errors(
            subject,
            f"{label}.subject",
            expected_selector=family["subject_selector"],
        )
    )
    bound, bound_errors = _bound_execution_evidence(
        root,
        payload.get("producer"),
        f"{label}.producer",
        owner_receipt_refs=owner_receipt_refs,
        bundle=bundle,
        bundle_sha256=bundle_sha256,
        validators=validators,
    )
    errors.extend(bound_errors)
    if bound is None:
        return errors
    receipt = bound["receipt"]
    packet = bound["packet"]
    output = bound["output"]
    if receipt.get("role") != family["role"]:
        errors.append(f"{label}: producer role must be {family['role']}")
    if packet.get("task") != family["task"]:
        errors.append(f"{label}: producer packet task must be {family['task']}")
    if output.get("task") != family["task"]:
        errors.append(f"{label}: producer output task must be {family['task']}")
    if packet.get("subject") != subject:
        errors.append(f"{label}: producer packet subject must equal challenged subject")
    if packet.get("review_packet") != challenge_packet.get("review_packet"):
        errors.append(f"{label}: producer and challenge review packets must be equal")
    result = output.get("result")
    candidate = payload.get("candidate")
    if family["candidate_kind"] == "content-bound-discovery-statement":
        errors.extend(
            _content_bound_semantic_object_errors(
                candidate,
                f"{label}.candidate",
                expected_selector="gate-a-discovery-classification-statement-v1",
            )
        )
        candidate_payload = _mapping(candidate).get("payload")
        if _mapping(candidate_payload).get("semantic_disposition") != "no-normative-impact":
            errors.append(f"{label}: discovery candidate must be no-normative-impact")
        revision = _mapping(packet.get("revision"))
        if revision.get("ordinal") == 0:
            statements = _sequence(_mapping(result).get("classification_statements"))
            if sum(statement == candidate_payload for statement in statements) != 1:
                errors.append(f"{label}: candidate must select exactly one producer statement")
        elif revision.get("ordinal") == 1:
            if _mapping(result).get("kind") != "revised-candidate" or _mapping(result).get("statement") != candidate_payload:
                errors.append(f"{label}: revised discovery candidate must equal revision output")
            closure = _mapping(revision.get("closure_subject"))
            if closure.get("selector") != selector:
                errors.append(f"{label}: discovery revision must remain in the same family")
        else:
            errors.append(f"{label}: discovery producer revision ordinal must be 0 or 1")
    else:
        if candidate != result:
            errors.append(f"{label}: candidate must equal exact producer output result")
        candidate_kind = family["candidate_kind"]
        if candidate_kind is not None and _mapping(result).get("kind") != candidate_kind:
            errors.append(f"{label}: producer result must be {candidate_kind}")
        if family["task"] == "materiality-assessment" and any(
            _mapping(candidate).get(axis) is True for axis in MATERIALITY_AXES
        ):
            errors.append(f"{label}: materiality challenge requires all seven axes false")
    return errors


def _bound_supporting_projection(value: object) -> dict:
    bound = _mapping(value)
    return {
        "execution_receipt": bound.get("execution_receipt"),
        "raw_output": bound.get("raw_output"),
        "output": bound.get("parsed_output"),
    }


def _p7_unique_correction_exhaustion_errors(
    root: Path,
    value: object,
    *,
    subject: dict,
    discovery_hypothesis: dict,
    review_packet: object,
    owner_receipt_refs: list[dict],
    bundle: dict,
    bundle_sha256: str,
    validators: dict[str, Draft202012Validator | None],
    label: str,
) -> list[str]:
    branches = {
        "initial-not-established": ["producer"],
        "revision-not-established": [
            "initial_producer",
            "initial_challenge",
            "revision_producer",
        ],
        "revised-challenge-objections": [
            "initial_producer",
            "initial_challenge",
            "revision_producer",
            "revision_challenge",
        ],
    }
    if not isinstance(value, dict) or value.get("kind") not in branches:
        return [f"{label}: unknown UniqueCorrectionExhaustionBasisV1 branch"]
    kind = value["kind"]
    expected_keys = {"kind", *branches[kind]}
    if set(value) != expected_keys:
        return [f"{label}: exhaustion branch has the wrong closed shape"]
    errors: list[str] = []
    resolved: dict[str, dict] = {}
    for field in branches[kind]:
        bound, bound_errors = _bound_execution_evidence(
            root,
            value.get(field),
            f"{label}.{field}",
            owner_receipt_refs=owner_receipt_refs,
            bundle=bundle,
            bundle_sha256=bundle_sha256,
            validators=validators,
        )
        errors.extend(bound_errors)
        if bound is not None:
            resolved[field] = bound
    if len(resolved) != len(branches[kind]):
        return errors

    def producer_errors(field: str, ordinal: int, positive: bool) -> None:
        bound = resolved[field]
        receipt, packet, output = bound["receipt"], bound["packet"], bound["output"]
        if receipt.get("role") != "derivation-builder":
            errors.append(f"{label}.{field}: role must be derivation-builder")
        if packet.get("task") != "unique-correction-derivation" or output.get("task") != "unique-correction-derivation":
            errors.append(f"{label}.{field}: task must be unique-correction-derivation")
        if _mapping(packet.get("revision")).get("ordinal") != ordinal:
            errors.append(f"{label}.{field}: revision ordinal must be {ordinal}")
        if packet.get("subject") != subject:
            errors.append(f"{label}.{field}: subject must equal decision-necessity subject")
        if _mapping(packet.get("task_input")).get("target_classification") != discovery_hypothesis:
            errors.append(f"{label}.{field}: target classification must equal discovery hypothesis")
        if packet.get("review_packet") != review_packet:
            errors.append(f"{label}.{field}: review packet must equal lineage review packet")
        result = output.get("result")
        if positive and _mapping(result).get("kind") != "unique-correction-candidate":
            errors.append(f"{label}.{field}: result must be a unique-correction-candidate")
        if not positive and result != {"kind": "not-established"}:
            errors.append(f"{label}.{field}: result must be not-established")

    if kind == "initial-not-established":
        producer_errors("producer", 0, False)
        return errors

    producer_errors("initial_producer", 0, True)
    initial_challenge = resolved["initial_challenge"]
    initial_packet = initial_challenge["packet"]
    if initial_challenge["receipt"].get("role") != "challenge":
        errors.append(f"{label}.initial_challenge: role must be challenge")
    if initial_packet.get("challenge_kind") != "derivation" or _mapping(initial_packet.get("challenge_subject")).get("selector") != "gate-a-unique-correction-candidate-challenge-v1":
        errors.append(f"{label}.initial_challenge: must be the exact unique-correction challenge family")
    if initial_packet.get("review_packet") != review_packet:
        errors.append(f"{label}.initial_challenge: review packet must equal lineage review packet")
    if not _sequence(initial_challenge["output"].get("objections")):
        errors.append(f"{label}.initial_challenge: objections must be non-empty")
    revision = _mapping(resolved["revision_producer"]["packet"].get("revision"))
    producer_errors(
        "revision_producer",
        1,
        kind == "revised-challenge-objections",
    )
    if revision.get("closure_subject") != initial_packet.get("challenge_subject"):
        errors.append(f"{label}.revision_producer: closure subject must equal initial challenge subject")
    if revision.get("prior_producer") != _bound_supporting_projection(value.get("initial_producer")):
        errors.append(f"{label}.revision_producer: prior producer evidence mismatch")
    if revision.get("prior_challenge") != _bound_supporting_projection(value.get("initial_challenge")):
        errors.append(f"{label}.revision_producer: prior challenge evidence mismatch")
    if kind == "revised-challenge-objections":
        revised_challenge = resolved["revision_challenge"]
        revised_packet = revised_challenge["packet"]
        if revised_challenge["receipt"].get("role") != "challenge":
            errors.append(f"{label}.revision_challenge: role must be challenge")
        if revised_packet.get("challenge_kind") != "derivation" or _mapping(revised_packet.get("challenge_subject")).get("selector") != "gate-a-unique-correction-candidate-challenge-v1":
            errors.append(f"{label}.revision_challenge: must be the exact unique-correction challenge family")
        if revised_packet.get("review_packet") != review_packet:
            errors.append(f"{label}.revision_challenge: review packet mismatch")
        if not _sequence(revised_challenge["output"].get("objections")):
            errors.append(f"{label}.revision_challenge: objections must be non-empty")
        challenged = _mapping(revised_packet.get("challenge_subject")).get("payload")
        revised_result = resolved["revision_producer"]["output"].get("result")
        if _mapping(challenged).get("candidate") != revised_result:
            errors.append(f"{label}.revision_challenge: candidate must equal revision output")
    return errors


def _p7_decision_necessity_subject_errors(
    root: Path,
    challenge_packet: dict,
    owner_receipt_refs: list[dict],
    bundle: dict,
    bundle_sha256: str,
    validators: dict[str, Draft202012Validator | None],
    label: str,
) -> list[str]:
    challenge_subject = _mapping(challenge_packet.get("challenge_subject"))
    payload = challenge_subject.get("payload")
    required = {
        "subject_schema_version",
        "selector",
        "subject",
        "discovery_hypothesis",
        "unique_correction_exhaustion",
        "candidate",
    }
    if not isinstance(payload, dict) or set(payload) != required:
        return [f"{label}: decision-necessity subject has the wrong closed shape"]
    errors: list[str] = []
    if payload.get("subject_schema_version") != 1:
        errors.append(f"{label}: subject_schema_version must be 1")
    if payload.get("selector") != P7_DECISION_NECESSITY_SELECTOR:
        errors.append(f"{label}: payload selector mismatch")
    if challenge_subject.get("sha256") != sha256_hex(_canonical_json_bytes(payload)):
        errors.append(f"{label}: challenge subject sha256 mismatch")
    subject = payload.get("subject")
    errors.extend(_content_bound_semantic_object_errors(
        subject,
        f"{label}.subject",
        expected_selector="gate-a-surviving-material-resolution-subject-v1",
    ))
    hypothesis = payload.get("discovery_hypothesis")
    errors.extend(_content_bound_semantic_object_errors(
        hypothesis,
        f"{label}.discovery_hypothesis",
        expected_selector="gate-a-discovery-classification-statement-v1",
    ))
    hypothesis_payload = _mapping(hypothesis).get("payload")
    if _mapping(hypothesis_payload).get("semantic_disposition") != "decision-required":
        errors.append(f"{label}: discovery hypothesis must be decision-required")
    candidate = payload.get("candidate")
    if not isinstance(candidate, dict) or set(candidate) != {"kind", "basis"}:
        errors.append(f"{label}: candidate must have exact decision-necessity shape")
    else:
        if candidate.get("kind") != "decision-necessity-candidate":
            errors.append(f"{label}: candidate kind mismatch")
        if candidate.get("basis") != _mapping(hypothesis_payload).get("disposition_basis"):
            errors.append(f"{label}: candidate basis must equal discovery disposition basis")
    errors.extend(_p7_unique_correction_exhaustion_errors(
        root,
        payload.get("unique_correction_exhaustion"),
        subject=_mapping(subject),
        discovery_hypothesis=_mapping(hypothesis),
        review_packet=challenge_packet.get("review_packet"),
        owner_receipt_refs=owner_receipt_refs,
        bundle=bundle,
        bundle_sha256=bundle_sha256,
        validators=validators,
        label=f"{label}.unique_correction_exhaustion",
    ))
    return errors


def _p7_challenge_packet_errors(
    root: Path,
    challenge_packet: dict,
    *,
    owner_receipt_refs: list[dict],
    bundle: dict,
    bundle_sha256: str,
    validators: dict[str, Draft202012Validator | None],
    label: str,
    challenger_role: str | None = None,
) -> list[str]:
    errors: list[str] = []
    validator = validators.get("challenge-packet")
    if validator is not None:
        errors.extend(_schema_violations(validator, challenge_packet, label))
    subject = _mapping(challenge_packet.get("challenge_subject"))
    selector = subject.get("selector")
    kind = challenge_packet.get("challenge_kind")
    contract = _p7_closure_contract(bundle, kind, selector)
    if contract is None:
        errors.append(f"{label}: no exact P7 closure contract for kind/selector pair")
        return errors
    if challenge_packet.get("required_objectives") != contract.get("required_objectives"):
        errors.append(f"{label}: required_objectives must equal exact contract sequence")
    if challenger_role is not None and challenger_role != contract.get("challenger_role"):
        errors.append(f"{label}: challenger role does not match exact closure contract")
    if selector in P7_DIRECT_CHALLENGE_FAMILIES:
        errors.extend(
            _p7_direct_challenge_subject_errors(
                root,
                challenge_packet,
                owner_receipt_refs,
                bundle,
                bundle_sha256,
                validators,
                label,
            )
        )
    elif selector == P7_DECISION_NECESSITY_SELECTOR:
        errors.extend(
            _p7_decision_necessity_subject_errors(
                root,
                challenge_packet,
                owner_receipt_refs,
                bundle,
                bundle_sha256,
                validators,
                label,
            )
        )
    else:
        errors.append(f"{label}: unknown P7 challenge selector {selector!r}")
    return errors


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


def _reviewer_acquisition_conformance_errors(
    bundle: dict,
    executions: list[dict],
    minimum_reviewers: int,
    label: str,
) -> list[str]:
    """Reconstruct deterministic initial-reviewer acquisition."""
    schema_version = bundle.get("protocol_bundle_schema_version")
    if schema_version not in (5, 6, 7):
        return []

    errors: list[str] = []
    actual_by_profile: dict[str, list[dict]] = {}
    for execution in executions:
        profile_id = execution.get("reviewer_profile_id")
        if isinstance(profile_id, str):
            actual_by_profile.setdefault(profile_id, []).append(execution)
    for profile_id, matching in actual_by_profile.items():
        if len(matching) > 1:
            errors.append(
                f"{label}: protocol v{schema_version} permits at most one logical "
                f"initial-reviewer execution for profile {profile_id!r}"
            )

    profiles = _protocol_profile_map(bundle)
    policy = _mapping(_mapping(bundle.get("policies")).get("reviewer_acquisition"))
    acquisition_order = [
        profile_id
        for profile_id in _sequence(policy.get("profile_order"))
        if isinstance(profile_id, str)
        and profile_id in profiles
        and _statically_qualifying_reviewer_profile(profiles[profile_id])
    ]

    effective_identities: set[tuple[object, object]] = set()
    selected_history: list[str] = []
    selected_ids: set[str] = set()
    while len(effective_identities) < minimum_reviewers:
        deficit = minimum_reviewers - len(effective_identities)
        selected_round: list[str] = []
        reserved_pinned: set[tuple[object, object]] = set()
        for profile_id in acquisition_order:
            if profile_id in selected_ids:
                continue
            profile = profiles[profile_id]
            resolution = _mapping(profile.get("identity_resolution"))
            if resolution.get("kind") == "pinned-request-model":
                known_identity = (profile.get("provider"), profile.get("request_model"))
                if (
                    known_identity in effective_identities
                    or known_identity in reserved_pinned
                ):
                    continue
                reserved_pinned.add(known_identity)
            selected_round.append(profile_id)
            if len(selected_round) == deficit:
                break

        if not selected_round:
            errors.append(
                f"{label}: completed protocol-v{schema_version} review cannot satisfy "
                "minimum-effective-independent-v1 with the remaining eligible pool"
            )
            break

        selected_history.extend(selected_round)
        selected_ids.update(selected_round)
        missing = [
            profile_id
            for profile_id in selected_round
            if len(actual_by_profile.get(profile_id, [])) != 1
        ]
        for profile_id in missing:
            errors.append(
                f"{label}: deterministic reviewer acquisition requires exactly one "
                f"execution for selected profile {profile_id!r}"
            )
        if missing:
            break

        for profile_id in selected_round:
            execution = actual_by_profile[profile_id][0]
            effective_identities.add(
                (execution.get("provider"), execution.get("model_version"))
            )

    actual_profile_ids = set(actual_by_profile)
    expected_profile_ids = set(selected_history)
    if actual_profile_ids != expected_profile_ids:
        errors.append(
            f"{label}: actual initial-reviewer profiles must equal deterministic "
            f"acquisition history; expected {sorted(expected_profile_ids)!r}, "
            f"found {sorted(actual_profile_ids)!r}"
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
    bundle_cache: dict[str, tuple[dict | None, list[str]]] = {}
    _current_reference, _current_bundle, current_errors = (
        _current_protocol_bundle_errors(root, manifest, bundle_cache)
    )
    errors.extend(current_errors)

    record_index: dict[str, dict] = {}
    for path, record in records:
        label = path.relative_to(root).as_posix()
        protocol = _mapping(record.get("protocol"))
        bundle_reference = _mapping(protocol.get("protocol_bundle"))
        bundle, bundle_errors = _load_protocol_bundle_document(
            root,
            bundle_reference,
            f"{label}: protocol.protocol_bundle",
            bundle_cache,
        )
        errors.extend(bundle_errors)
        evidence_reference: dict = {}
        if bundle is not None:
            version = bundle.get("protocol_bundle_schema_version")
            if version in (4, 5, 6, 7):
                evidence_reference = _mapping(
                    _mapping(bundle.get("meta_schemas")).get("review-evidence")
                )
            elif version in (1, 2, 3):
                evidence_reference = dict(LEGACY_REVIEW_EVIDENCE_META_SCHEMA_REFERENCE)
        evidence_validator: Draft202012Validator | None = None
        if not evidence_reference:
            errors.append(
                f"{label}: review record protocol bundle does not select a "
                "review-evidence meta-schema"
            )
        else:
            evidence_validator, evidence_errors = _load_meta_schema_validator(
                root, evidence_reference, f"{label}: review-evidence meta-schema"
            )
            errors.extend(evidence_errors)
        if evidence_validator is not None:
            errors.extend(_schema_violations(evidence_validator, record, label))
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

        if is_gate_a_subject_review and bundle is not None:
            hostile_review = _mapping(
                _mapping(manifest.get("policy")).get("hostile_review")
            )
            minimum_reviewers = hostile_review.get("minimum_independent_reviewers")
            if isinstance(minimum_reviewers, int) and minimum_reviewers >= 1:
                errors.extend(
                    _reviewer_acquisition_conformance_errors(
                        bundle, executions, minimum_reviewers, label
                    )
                )

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


def load_finding_adjudication_supplements(
    root: Path,
) -> tuple[list[tuple[Path, dict]], list[str]]:
    directory = root / REVIEW_SUPPLEMENTS_PREFIX.rstrip("/")
    supplements: list[tuple[Path, dict]] = []
    errors: list[str] = []
    if not directory.exists():
        return supplements, errors
    if directory.is_symlink() or not directory.is_dir():
        return supplements, [f"{REVIEW_SUPPLEMENTS_PREFIX.rstrip('/')}: must be a direct directory"]
    for path in sorted(directory.iterdir()):
        label = path.relative_to(root).as_posix()
        if path.is_symlink() or not path.is_file():
            errors.append(f"{label}: supplement must be a direct regular file")
            continue
        if path.suffix != ".json":
            errors.append(f"{label}: supplement must use the .json suffix")
            continue
        try:
            data = path.read_bytes()
            value = json.loads(data.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            errors.append(f"{label}: invalid supplement JSON ({_concise_parser_error(error)})")
            continue
        if not isinstance(value, dict):
            errors.append(f"{label}: supplement must be a JSON object")
            continue
        if data != _canonical_json_document_bytes(value):
            errors.append(f"{label}: supplement must use canonical JSON document bytes")
        expected_name = f"{sha256_hex(data)}.json"
        if path.name != expected_name:
            errors.append(
                f"{label}: supplement filename must equal exact document SHA-256; "
                f"expected {expected_name}"
            )
        supplements.append((path, value))
    return supplements, errors


def _supporting_execution_dag_errors(
    nodes: dict[str, dict],
    roots: set[str],
    label: str,
) -> list[str]:
    errors: list[str] = []
    for identity, node in nodes.items():
        for predecessor in node.get("predecessors", set()):
            if predecessor not in nodes:
                errors.append(f"{label}: supporting DAG has missing predecessor {predecessor}")
            elif node.get("lineage") != nodes[predecessor].get("lineage"):
                errors.append(f"{label}: supporting DAG has a cross-lineage edge")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identity: str) -> None:
        if identity in visiting:
            errors.append(f"{label}: supporting execution DAG contains a cycle")
            return
        if identity in visited or identity not in nodes:
            return
        visiting.add(identity)
        for predecessor in nodes[identity].get("predecessors", set()):
            visit(predecessor)
        visiting.remove(identity)
        visited.add(identity)

    reachable: set[str] = set()

    def mark(identity: str) -> None:
        if identity in reachable or identity not in nodes:
            return
        reachable.add(identity)
        for predecessor in nodes[identity].get("predecessors", set()):
            mark(predecessor)

    for root_identity in roots:
        visit(root_identity)
        mark(root_identity)
    if reachable != set(nodes):
        errors.append(f"{label}: supporting execution DAG contains an orphan receipt")
    logical_keys = [node.get("logical_key") for node in nodes.values()]
    if len(logical_keys) != len(set(logical_keys)):
        errors.append(f"{label}: duplicate logical execution for exact role and packet")
    return errors


def _supplement_effective_receipt_refs(supplement: dict) -> list[dict]:
    effective = _mapping(supplement.get("effective_adjudication"))
    return [
        value
        for key, value in effective.items()
        if key != "kind" and isinstance(value, dict)
    ]


def _supplement_terminal_receipt_refs(supplement: dict) -> list[dict]:
    effective = _mapping(supplement.get("effective_adjudication"))
    terminal_field = {
        "qualified-non-material": "materiality_challenge_execution_receipt",
        "qualified-refutation": "refutation_challenge_execution_receipt",
        "surviving-material": "refutation_exhaustion_terminal_receipt",
    }.get(effective.get("kind"))
    terminal = effective.get(terminal_field) if terminal_field is not None else None
    return [terminal] if isinstance(terminal, dict) else []


def _p7_lineage_packet_errors(
    packet: dict,
    *,
    supplement: dict,
    source_finding: dict,
    bundle: dict,
    review_packet: dict,
    label: str,
) -> list[str]:
    errors: list[str] = []
    protocol = _mapping(supplement.get("protocol"))
    bundle_ref = _mapping(protocol.get("protocol_bundle"))
    packet_ref = _mapping(protocol.get("review_packet"))
    expected_review_packet = {"sha256": packet_ref.get("sha256"), "payload": review_packet}
    if packet.get("review_packet") != expected_review_packet:
        errors.append(f"{label}: packet is not bound to the supplement review packet")
    if "task" not in packet:
        return errors
    expected_finding = {
        "selector": FINDING_SUBJECT_SELECTOR,
        "sha256": _finding_subject_sha256(source_finding),
        "payload": _finding_subject_payload(source_finding),
    }
    if packet.get("finding") != expected_finding:
        errors.append(f"{label}: packet finding does not equal the exact source finding")
    subject_payload = _mapping(_mapping(packet.get("subject")).get("payload"))
    semantic_subject = _mapping(supplement.get("semantic_subject"))
    if subject_payload.get("semanticSubject") != semantic_subject:
        errors.append(f"{label}: packet subject semantic identity mismatch")
    expected_protocol = {
        "protocolId": bundle.get("protocol_id"),
        "repositoryPath": bundle_ref.get("path"),
        "sha256": bundle_ref.get("sha256"),
    }
    protocol_field = (
        "currentProtocolBundle"
        if _mapping(packet.get("subject")).get("selector")
        == "gate-a-finding-adjudication-subject-v1"
        else "protocolBundle"
    )
    if subject_payload.get(protocol_field) != expected_protocol:
        errors.append(f"{label}: packet subject protocol identity mismatch")
    if protocol_field == "currentProtocolBundle":
        source = _mapping(supplement.get("source_finding"))
        source_subject = _mapping(subject_payload.get("sourceFinding"))
        if (
            source_subject.get("reviewCampaignId") != source.get("review_id")
            or source_subject.get("findingId") != source.get("finding_id")
            or source_subject.get("substantiveFindingSha256")
            != source.get("substantive_finding_sha256")
        ):
            errors.append(f"{label}: packet subject source-finding identity mismatch")
        if subject_payload.get("adjudicatingReviewCampaignId") != supplement.get(
            "adjudicating_review_id"
        ):
            errors.append(f"{label}: packet subject adjudicating campaign mismatch")
    return errors


def _supplement_supporting_execution_graph(
    root: Path,
    supplement: dict,
    *,
    source_finding: dict,
    bundle: dict,
    bundle_sha256: str,
    validators: dict[str, Draft202012Validator | None],
    label: str,
) -> tuple[dict[tuple[str, str], dict], list[str]]:
    owner_refs = [
        ref
        for ref in _sequence(supplement.get("supporting_executions"))
        if isinstance(ref, dict)
    ]
    contexts: dict[tuple[str, str], dict] = {}
    nodes: dict[str, dict] = {}
    errors: list[str] = []
    review_packet_ref = _mapping(_mapping(supplement.get("protocol")).get("review_packet"))
    review_packet_bytes, review_packet_errors = _read_review_artifact(
        root,
        review_packet_ref,
        f"{label}.protocol.review_packet",
        REVIEW_PACKET_PREFIX,
        REVIEW_PACKET_SUFFIX,
    )
    errors.extend(review_packet_errors)
    review_packet: dict = {}
    if review_packet_bytes is not None:
        parsed_review_packet, parse_errors = _parse_json_object_bytes(
            review_packet_bytes, f"{label}.protocol.review_packet"
        )
        errors.extend(parse_errors)
        if parsed_review_packet is not None:
            review_packet = parsed_review_packet
    lineage = (
        _mapping(supplement.get("source_finding")).get("substantive_finding_sha256"),
        _mapping(supplement.get("semantic_subject")).get("sha256"),
        bundle_sha256,
    )
    for index, receipt_ref in enumerate(owner_refs):
        receipt_runtime, receipt_bytes, receipt_errors = reconstruct_runtime_json_artifact_ref(
            root,
            receipt_ref,
            expected_prefix=REVIEW_EXECUTIONS_PREFIX,
            expected_suffix=REVIEW_EXECUTION_SUFFIX,
            label=f"{label}.supporting_executions[{index}]",
        )
        errors.extend(receipt_errors)
        if receipt_runtime is None or receipt_bytes is None:
            continue
        receipt, parse_errors = _parse_json_object_bytes(
            receipt_bytes, f"{label}.supporting_executions[{index}]"
        )
        errors.extend(parse_errors)
        if receipt is None:
            continue
        if receipt_bytes != _canonical_json_bytes(receipt):
            errors.append(
                f"{label}.supporting_executions[{index}]: receipt must use canonical JSON value bytes"
            )
        receipt_validator = validators.get("execution-receipt")
        if receipt_validator is not None:
            errors.extend(
                _schema_violations(
                    receipt_validator,
                    receipt,
                    f"{label}.supporting_executions[{index}]",
                )
            )
        role = receipt.get("role")
        packet_prefix = _p7_packet_namespace(role)
        output_prefix = _p7_output_namespace(role)
        if receipt.get("receipt_schema_version") != "4.0" or packet_prefix is None or output_prefix is None:
            errors.append(
                f"{label}.supporting_executions[{index}]: supplement requires a protocol-v7 receipt role"
            )
            continue
        packet_ref = _mapping(receipt.get("input")).get("packet")
        packet_runtime, packet_bytes, packet_errors = reconstruct_runtime_json_artifact_ref(
            root,
            packet_ref,
            expected_prefix=packet_prefix,
            expected_suffix=".json",
            label=f"{label}.supporting_executions[{index}].packet",
        )
        errors.extend(packet_errors)
        qualifying = _unique_qualifying_attempt(receipt)
        if qualifying is None:
            errors.append(
                f"{label}.supporting_executions[{index}]: receipt has no unique qualified attempt"
            )
            continue
        raw_ref = qualifying.get("raw_output")
        raw_runtime, raw_bytes, raw_errors = reconstruct_runtime_json_artifact_ref(
            root,
            raw_ref,
            expected_prefix=output_prefix,
            expected_suffix=".json",
            label=f"{label}.supporting_executions[{index}].raw_output",
        )
        errors.extend(raw_errors)
        if packet_runtime is None or packet_bytes is None or raw_runtime is None or raw_bytes is None:
            continue
        packet, packet_parse_errors = _parse_json_object_bytes(
            packet_bytes, f"{label}.supporting_executions[{index}].packet"
        )
        output, output_parse_errors = _parse_json_object_bytes(
            raw_bytes, f"{label}.supporting_executions[{index}].raw_output"
        )
        errors.extend(packet_parse_errors)
        errors.extend(output_parse_errors)
        if packet is None or output is None:
            continue
        bound = {
            "execution_receipt": receipt_runtime,
            "packet": {"artifact": packet_runtime, "payload": packet},
            "raw_output": raw_runtime,
            "parsed_output": output,
        }
        context, bound_errors = _bound_execution_evidence(
            root,
            bound,
            f"{label}.supporting_executions[{index}]",
            owner_receipt_refs=owner_refs,
            bundle=bundle,
            bundle_sha256=bundle_sha256,
            validators=validators,
        )
        errors.extend(bound_errors)
        if context is None:
            continue
        errors.extend(
            _p7_lineage_packet_errors(
                packet,
                supplement=supplement,
                source_finding=source_finding,
                bundle=bundle,
                review_packet=review_packet,
                label=f"{label}.supporting_executions[{index}]",
            )
        )
        if role in {"challenge", "decision-necessity-challenger"}:
            errors.extend(
                _p7_challenge_packet_errors(
                    root,
                    packet,
                    owner_receipt_refs=owner_refs,
                    bundle=bundle,
                    bundle_sha256=bundle_sha256,
                    validators=validators,
                    label=f"{label}.supporting_executions[{index}].challenge_packet",
                    challenger_role=role,
                )
            )
        key = (receipt_ref.get("path"), receipt_ref.get("sha256"))
        contexts[key] = context
        predecessors: set[str] = set()
        for node in _walk_json(packet):
            if not isinstance(node, dict):
                continue
            if set(node) == {
                "execution_receipt",
                "packet",
                "raw_output",
                "parsed_output",
            } or set(node) == {"execution_receipt", "raw_output", "output"}:
                predecessor_sha = _mapping(node.get("execution_receipt")).get("sha256")
                if isinstance(predecessor_sha, str):
                    predecessors.add(predecessor_sha)
        nodes[receipt_ref.get("sha256")] = {
            "predecessors": predecessors,
            "lineage": lineage,
            "logical_key": (role, _mapping(packet_runtime).get("sha256")),
        }

    contexts_by_sha = {
        _mapping(context.get("execution_receipt")).get("sha256"): context
        for context in contexts.values()
    }
    for context in contexts.values():
        packet = _mapping(context.get("packet"))
        for node in _walk_json(packet):
            if not isinstance(node, dict) or set(node) != {
                "execution_receipt",
                "raw_output",
                "output",
            }:
                continue
            predecessor = contexts_by_sha.get(
                _mapping(node.get("execution_receipt")).get("sha256")
            )
            if predecessor is None:
                continue
            if node.get("raw_output") != predecessor.get("raw_output"):
                errors.append(f"{label}: supporting predecessor raw-output identity mismatch")
            if node.get("output") != predecessor.get("output"):
                errors.append(f"{label}: supporting predecessor parsed output mismatch")
        revision = _mapping(packet.get("revision"))
        if revision.get("ordinal") != 1:
            continue
        prior_producer = contexts_by_sha.get(
            _mapping(_mapping(revision.get("prior_producer")).get("execution_receipt")).get("sha256")
        )
        prior_challenge = contexts_by_sha.get(
            _mapping(_mapping(revision.get("prior_challenge")).get("execution_receipt")).get("sha256")
        )
        if prior_producer is None or prior_challenge is None:
            continue
        if _mapping(prior_producer.get("receipt")).get("role") != _mapping(context.get("receipt")).get("role"):
            errors.append(f"{label}: revision producer role changed")
        if _mapping(prior_producer.get("packet")).get("task") != packet.get("task"):
            errors.append(f"{label}: revision producer task changed")
        if _mapping(prior_producer.get("packet")).get("subject") != packet.get("subject"):
            errors.append(f"{label}: revision producer subject changed")
        if _mapping(prior_producer.get("packet")).get("review_packet") != packet.get("review_packet"):
            errors.append(f"{label}: revision producer review packet changed")
        challenge_packet = _mapping(prior_challenge.get("packet"))
        if challenge_packet.get("challenge_subject") != revision.get("closure_subject"):
            errors.append(f"{label}: revision closure subject does not equal prior challenge subject")
        if not _sequence(_mapping(prior_challenge.get("output")).get("objections")):
            errors.append(f"{label}: revision requires prior hostile objections")
        challenged_producer = _mapping(
            _mapping(challenge_packet.get("challenge_subject")).get("payload")
        ).get("producer")
        if _bound_supporting_projection(challenged_producer) != revision.get("prior_producer"):
            errors.append(f"{label}: prior challenge was not bound to the revision producer")
    root_shas = {
        _mapping(ref).get("sha256")
        for ref in _supplement_terminal_receipt_refs(supplement)
        if isinstance(_mapping(ref).get("sha256"), str)
    }
    errors.extend(_supporting_execution_dag_errors(nodes, root_shas, label))
    return contexts, errors


def _materiality_axes_from_context(context: dict | None) -> list[object]:
    result = _mapping(_mapping(context).get("output")).get("result")
    result = _mapping(result)
    return [result.get(axis) for axis in MATERIALITY_AXES]


def _effective_supplement_adjudication_errors(
    supplement: dict,
    contexts: dict[tuple[str, str], dict],
    label: str,
) -> list[str]:
    effective = _mapping(supplement.get("effective_adjudication"))
    kind = effective.get("kind")
    errors: list[str] = []

    def context(field: str) -> dict | None:
        ref = _mapping(effective.get(field))
        return contexts.get((ref.get("path"), ref.get("sha256")))

    materiality = context("materiality_assessment_execution_receipt")
    materiality_axes = _materiality_axes_from_context(materiality)
    if _mapping(materiality).get("receipt", {}).get("role") != "materiality-assessor":
        errors.append(f"{label}: effective materiality receipt has the wrong role")
    if kind == "qualified-non-material":
        if materiality_axes != [False] * len(MATERIALITY_AXES):
            errors.append(f"{label}: qualified non-material requires all materiality axes false")
        challenge = context("materiality_challenge_execution_receipt")
        if _mapping(challenge).get("receipt", {}).get("role") != "challenge":
            errors.append(f"{label}: materiality challenge receipt has the wrong role")
        if _mapping(_mapping(challenge).get("packet")).get("challenge_subject", {}).get("selector") != "gate-a-materiality-assessment-challenge-v1":
            errors.append(f"{label}: materiality challenge selector mismatch")
        if _mapping(_mapping(challenge).get("output")).get("objections") != []:
            errors.append(f"{label}: qualified non-material requires zero challenge objections")
    elif kind == "qualified-refutation":
        if not any(axis is True for axis in materiality_axes):
            errors.append(f"{label}: qualified refutation requires positive materiality")
        refutation = context("refutation_execution_receipt")
        if _mapping(refutation).get("receipt", {}).get("role") != "refutation-builder" or _mapping(_mapping(refutation).get("output")).get("result", {}).get("kind") != "refutation-candidate":
            errors.append(f"{label}: qualified refutation requires an exact refutation candidate")
        challenge = context("refutation_challenge_execution_receipt")
        if _mapping(challenge).get("receipt", {}).get("role") != "challenge":
            errors.append(f"{label}: refutation challenge receipt has the wrong role")
        if _mapping(_mapping(challenge).get("packet")).get("challenge_subject", {}).get("selector") != "gate-a-refutation-candidate-challenge-v1":
            errors.append(f"{label}: refutation challenge selector mismatch")
        if _mapping(_mapping(challenge).get("output")).get("objections") != []:
            errors.append(f"{label}: qualified refutation requires zero challenge objections")
    elif kind == "surviving-material":
        if not any(axis is True for axis in materiality_axes):
            errors.append(f"{label}: surviving material requires positive materiality")
        terminal = context("refutation_exhaustion_terminal_receipt")
        terminal_role = _mapping(terminal).get("receipt", {}).get("role")
        terminal_output = _mapping(_mapping(terminal).get("output"))
        terminal_packet = _mapping(_mapping(terminal).get("packet"))
        exhausted = (
            terminal_role == "refutation-builder"
            and _mapping(terminal_output.get("result")).get("kind") == "not-established"
        ) or (
            terminal_role == "challenge"
            and terminal_output.get("objections") not in (None, [])
            and _mapping(terminal_packet.get("challenge_subject")).get("selector")
            == "gate-a-refutation-candidate-challenge-v1"
            and _mapping(
                _mapping(
                    _mapping(terminal_packet.get("challenge_subject")).get("payload")
                ).get("producer")
            ).get("packet", {}).get("payload", {}).get("revision", {}).get("ordinal")
            == 1
        )
        if not exhausted:
            errors.append(f"{label}: terminal receipt does not establish lawful refutation exhaustion")
    return errors


def _finding_adjudication_supplement_errors(
    root: Path,
    manifest: dict,
    records: list[tuple[Path, dict]],
    supplements: list[tuple[Path, dict]],
    current_subject: dict | None,
) -> list[str]:
    errors: list[str] = []
    record_index = {
        record.get("review_id"): record
        for _path, record in records
        if isinstance(record.get("review_id"), str)
    }
    bundle_cache: dict[str, tuple[dict | None, list[str]]] = {}
    semantic_keys: Counter[tuple] = Counter()
    receipt_owners: Counter[tuple] = Counter()
    campaign_receipts = {
        (_mapping(ref).get("path"), _mapping(ref).get("sha256"))
        for _path, record in records
        for ref in _sequence(record.get("supporting_executions"))
    }
    for path, supplement in supplements:
        label = path.relative_to(root).as_posix()
        protocol = _mapping(supplement.get("protocol"))
        bundle_ref = _mapping(protocol.get("protocol_bundle"))
        bundle, bundle_errors = _load_protocol_bundle_document(
            root, bundle_ref, f"{label}: protocol bundle", bundle_cache
        )
        errors.extend(bundle_errors)
        validators, validator_errors = _bundle_selected_validators(
            root, bundle, f"{label}: protocol bundle"
        )
        errors.extend(validator_errors)
        validator = validators.get("finding-adjudication-supplement")
        if validator is not None:
            errors.extend(_schema_violations(validator, supplement, label))
        if bundle is None or bundle.get("protocol_bundle_schema_version") != 7:
            errors.append(f"{label}: supplement must bind a protocol-v7 bundle")
            continue
        semantic_subject = _mapping(supplement.get("semantic_subject"))
        if current_subject is not None and semantic_subject != {
            "selector": current_subject.get("selector"),
            "sha256": current_subject.get("sha256"),
        }:
            errors.append(f"{label}: supplement semantic subject is not current S")
        source = _mapping(supplement.get("source_finding"))
        source_record = record_index.get(source.get("review_id"))
        source_finding = None
        if source_record is not None:
            matches = [
                finding
                for finding in _sequence(source_record.get("findings"))
                if isinstance(finding, dict)
                and finding.get("finding_id") == source.get("finding_id")
            ]
            if len(matches) == 1:
                source_finding = matches[0]
        if source_finding is None:
            errors.append(f"{label}: source finding does not resolve exactly")
            continue
        finding_sha = _finding_subject_sha256(source_finding)
        if source.get("substantive_finding_sha256") != finding_sha:
            errors.append(f"{label}: substantive finding sha256 mismatch")
        semantic_key = (
            source.get("review_id"),
            source.get("finding_id"),
            finding_sha,
            bundle_ref.get("path"),
            bundle_ref.get("sha256"),
        )
        semantic_keys[semantic_key] += 1
        review_packet_ref = _mapping(protocol.get("review_packet"))
        review_packet_bytes, packet_errors = _read_review_artifact(
            root,
            review_packet_ref,
            f"{label}: review packet",
            REVIEW_PACKET_PREFIX,
            REVIEW_PACKET_SUFFIX,
        )
        errors.extend(packet_errors)
        if review_packet_bytes is not None:
            packet, parse_errors = _parse_json_object_bytes(review_packet_bytes, f"{label}: review packet")
            errors.extend(parse_errors)
            if packet is not None:
                subject = _mapping(packet.get("subject"))
                if subject.get("selector") != semantic_subject.get("selector") or subject.get("sha256") != semantic_subject.get("sha256"):
                    errors.append(f"{label}: review packet subject mismatch")
        adjudicating_id = supplement.get("adjudicating_review_id")
        adjudicating = record_index.get(adjudicating_id)
        if adjudicating is None:
            errors.append(f"{label}: adjudicating ReviewCampaign does not exist")
        else:
            subjects = _gate_a_derived_subjects(adjudicating.get("subjects"))
            if len(subjects) != 1 or subjects[0].get("selector") != semantic_subject.get("selector") or subjects[0].get("sha256") != semantic_subject.get("sha256"):
                errors.append(f"{label}: adjudicating review has wrong S")
            if _mapping(_mapping(adjudicating.get("protocol")).get("protocol_bundle")) != bundle_ref:
                errors.append(f"{label}: adjudicating review has wrong P")
            if _mapping(_mapping(adjudicating.get("protocol")).get("review_packet")) != review_packet_ref:
                errors.append(f"{label}: adjudicating review packet mismatch")
        source_bundle = _mapping(_mapping(source_record.get("protocol")).get("protocol_bundle"))
        if source_bundle == bundle_ref:
            if adjudicating_id != source.get("review_id"):
                errors.append(f"{label}: same-protocol bootstrap must use source review")
        else:
            current_ids = sorted(
                review_id
                for review_id, record in record_index.items()
                if _mapping(_mapping(record.get("protocol")).get("protocol_bundle")) == bundle_ref
                and len(_gate_a_derived_subjects(record.get("subjects"))) == 1
                and _gate_a_derived_subjects(record.get("subjects"))[0].get("sha256") == semantic_subject.get("sha256")
            )
            if not current_ids or adjudicating_id != current_ids[0]:
                errors.append(f"{label}: stale-source adjudicating campaign selection is not canonical")
        refs = [_mapping(ref) for ref in _sequence(supplement.get("supporting_executions"))]
        if refs != sorted(refs, key=lambda ref: (str(ref.get("path")), str(ref.get("sha256")))):
            errors.append(f"{label}: supporting executions are not in canonical order")
        ref_keys = {(ref.get("path"), ref.get("sha256")) for ref in refs}
        if len(ref_keys) != len(refs):
            errors.append(f"{label}: supporting execution references must be unique")
        for key in ref_keys:
            receipt_owners[key] += 1
            if key in campaign_receipts:
                errors.append(f"{label}: receipt belongs to campaign and supplement roots")
        for effective_ref in _supplement_effective_receipt_refs(supplement):
            key = (effective_ref.get("path"), effective_ref.get("sha256"))
            if key not in ref_keys:
                errors.append(f"{label}: effective adjudication receipt is outside supporting_executions")
        effective_kind = _mapping(supplement.get("effective_adjudication")).get("kind")
        if effective_kind not in {
            "qualified-non-material",
            "qualified-refutation",
            "surviving-material",
        }:
            errors.append(f"{label}: invalid effective adjudication kind")
        contexts, graph_errors = _supplement_supporting_execution_graph(
            root,
            supplement,
            source_finding=source_finding,
            bundle=bundle,
            bundle_sha256=str(bundle_ref.get("sha256")),
            validators=validators,
            label=label,
        )
        errors.extend(graph_errors)
        errors.extend(
            _effective_supplement_adjudication_errors(supplement, contexts, label)
        )
    for key, count in semantic_keys.items():
        if count > 1:
            errors.append(f"duplicate supplement semantic key {key!r}")
    for key, count in receipt_owners.items():
        if count > 1:
            errors.append(f"supporting receipt belongs to multiple supplement roots: {key!r}")
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


GATE_A_SUBJECT_REQUIREMENT_ID = "gate_a_subject_binding"
GATE_A_CURRENT_PROTOCOL_REQUIREMENT_ID = "gate_a_current_protocol_binding"


def _load_gate_a_requirements(
    root: Path,
) -> tuple[PersistentEvidenceRequirement, PersistentEvidenceRequirement]:
    state = repository_governance_state.load(root)
    registry = state.evidence_requirements
    if registry is None:
        raise evidence_requirements.EvidenceRequirementsError(
            "Turnlock-Rust declares evidence_requirements but the canonical state "
            "does not contain its registry"
        )
    try:
        subject = registry.requirements[GATE_A_SUBJECT_REQUIREMENT_ID]
        current_protocol = registry.requirements[
            GATE_A_CURRENT_PROTOCOL_REQUIREMENT_ID
        ]
    except KeyError as error:
        raise evidence_requirements.EvidenceRequirementsError(
            f"required Gate A EvidenceRequirementId is missing: {error.args[0]}"
        ) from error
    _validate_gate_a_requirement(subject)
    _validate_gate_a_requirement(current_protocol)
    return subject, current_protocol


def _validate_gate_a_requirement(
    requirement: PersistentEvidenceRequirement,
) -> None:
    classes = requirement.evidence_classes
    if (
        requirement.instances.kind is not InstantiationKind.SINGLE
        or classes.kind is not EvidenceClassKind.EXPLICIT
        or not classes.explicit_classes
        or requirement.subject_source_id != "gate_a_current_subject"
        or requirement.candidate_source_id != "gate_a_review_candidates"
        or (
            requirement.context.required
            and requirement.context.source_id != "gate_a_current_protocol_context"
        )
        or (
            not requirement.context.required
            and requirement.context.source_id is not None
        )
    ):
        raise evidence_requirements.EvidenceRequirementsError(
            f"unsupported Gate A evidence requirement declaration: {requirement.id}"
        )


def _runtime_gate_a_requirement(
    requirement: PersistentEvidenceRequirement,
    current_subject: dict | None,
    current_bundle_sha256: object,
) -> EvidenceRequirement:
    explicit_classes = requirement.evidence_classes.explicit_classes
    if explicit_classes is None:
        raise evidence_requirements.EvidenceRequirementsError(
            f"Gate A evidence classes are not explicit: {requirement.id}"
        )
    requires_context = requirement.context.required
    return EvidenceRequirement(
        admitted_classes=explicit_classes,
        subject_identity=(
            _canonical_json_bytes(current_subject)
            if isinstance(current_subject, dict)
            else None
        ),
        context_required=requires_context,
        context_identity=(
            current_bundle_sha256.encode("utf-8")
            if requires_context
            and isinstance(current_bundle_sha256, str)
            and current_bundle_sha256
            else None
        ),
    )


def _gate_a_binding_status(
    *,
    requirement: PersistentEvidenceRequirement,
    current_subject: dict | None,
    current_bundle_sha256: object,
    record: dict,
    gate_a_subject: dict,
) -> BindingStatus:
    runtime_requirement = _runtime_gate_a_requirement(
        requirement, current_subject, current_bundle_sha256
    )
    record_review_class = record.get("review_class")
    record_bundle_sha256 = _mapping(
        _mapping(record.get("protocol")).get("protocol_bundle")
    ).get("sha256")
    evidence = EvidenceBinding(
        evidence_class=(
            record_review_class if isinstance(record_review_class, str) else None
        ),
        subject_identity=_canonical_json_bytes(gate_a_subject),
        context_identity=(
            record_bundle_sha256.encode("utf-8")
            if requirement.context.required
            and isinstance(record_bundle_sha256, str)
            and record_bundle_sha256
            else None
        ),
    )
    return evaluate_evidence_binding(runtime_requirement, evidence)


def derive_gate_a(
    root: Path,
    manifest: dict,
    current_subject: dict | None,
    records: list[tuple[Path, dict]],
    subject_requirement: PersistentEvidenceRequirement,
    current_protocol_requirement: PersistentEvidenceRequirement,
    supplements: list[tuple[Path, dict]] | None = None,
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
        gate_a_subjects = _gate_a_derived_subjects(record.get("subjects"))
        if len(gate_a_subjects) != 1:
            continue
        subject_binding = _gate_a_binding_status(
            requirement=subject_requirement,
            current_subject=current_subject,
            current_bundle_sha256=current_bundle_sha256,
            record=record,
            gate_a_subject=gate_a_subjects[0],
        )
        if subject_binding is not BindingStatus.MATCH:
            continue
        current_binding = _gate_a_binding_status(
            requirement=current_protocol_requirement,
            current_subject=current_subject,
            current_bundle_sha256=current_bundle_sha256,
            record=record,
            gate_a_subject=gate_a_subjects[0],
        )
        if current_binding is BindingStatus.MATCH:
            current.append(record)
        else:
            stale.append(record)

    if not current and not stale:
        return {
            "ready": False,
            "reason": "hostile assurance-decomposition review evidence required",
        }

    current_supplements: dict[tuple, dict] = {}
    for _path, supplement in supplements or []:
        protocol_bundle = _mapping(_mapping(supplement.get("protocol")).get("protocol_bundle"))
        source = _mapping(supplement.get("source_finding"))
        if protocol_bundle.get("sha256") == current_bundle_sha256:
            current_supplements[(source.get("review_id"), source.get("finding_id"))] = supplement

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
            if key not in current_supplements and key not in current_re_adjudications:
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
            key = (record.get("review_id"), finding.get("finding_id"))
            overlay = current_supplements.get(key)
            if overlay is not None:
                kind = _mapping(overlay.get("effective_adjudication")).get("kind")
                if kind in {"qualified-non-material", "qualified-refutation"}:
                    continue
                return {
                    "ready": False,
                    "reason": "surviving material hostile-review finding exists",
                }
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
            overlay = current_supplements.get(key)
            if overlay is not None:
                kind = _mapping(overlay.get("effective_adjudication")).get("kind")
                if kind in {"qualified-non-material", "qualified-refutation"}:
                    continue
                return {
                    "ready": False,
                    "reason": "surviving material hostile-review finding exists",
                }
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
    root: Path,
    *,
    check_generated: bool = True,
    load_governance: bool = True,
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

    candidate_bundle_cache: dict[str, tuple[dict | None, list[str]]] = {}
    errors.extend(_inactive_protocol_v7_candidate_errors(root, candidate_bundle_cache))

    review_records, review_load_errors = load_review_records(root)
    review_validation_errors = _review_evidence_errors(root, manifest, review_records)
    supplements, supplement_load_errors = load_finding_adjudication_supplements(root)
    supplement_validation_errors = _finding_adjudication_supplement_errors(
        root,
        manifest,
        review_records,
        supplements,
        current_subject,
    )

    errors.extend(review_load_errors)
    errors.extend(review_validation_errors)
    errors.extend(supplement_load_errors)
    errors.extend(supplement_validation_errors)

    gate_a_requirements = None
    if load_governance:
        try:
            gate_a_requirements = _load_gate_a_requirements(root)
        except (
            evidence_requirements.EvidenceRequirementsError,
            repository_governance_state.RepositoryGovernanceStateError,
            KeyError,
        ) as error:
            errors.append(f"Gate A evidence requirements: {error}")

    if (
        review_load_errors
        or review_validation_errors
        or supplement_load_errors
        or supplement_validation_errors
    ):
        gate_a = {
            "ready": False,
            "reason": "hostile review evidence integrity failure",
        }
    elif not load_governance:
        gate_a = summary["gate_a"]
    elif gate_a_requirements is None:
        gate_a = {
            "ready": False,
            "reason": "Gate A evidence requirements integrity failure",
        }
    else:
        gate_a = derive_gate_a(
            root,
            manifest,
            current_subject,
            review_records,
            gate_a_requirements[0],
            gate_a_requirements[1],
            supplements=supplements,
        )
    summary["gate_a"] = gate_a

    if (root / MODEL_RELATIVE).exists() and not gate_a["ready"]:
        errors.append(
            "formal/Turnlock.tla exists while Formal-Architecture-Ready is BLOCKED"
        )

    if check_generated:
        renderer = root / "scripts" / "render-formal-mapping.py"
        mapping_path = root / MAPPING_RELATIVE
        if not mapping_path.exists():
            errors.append(
                "generated formal invariant mapping is missing; "
                "run python scripts/render-formal-mapping.py"
            )
        else:
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
