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
REVIEW_CONTRACTS_PREFIX = "formal/reviews/contracts/"
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
    REVIEW_CONTRACTS_PREFIX,
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
PROTOCOL_V8_SEMANTIC_IDENTITY_SCHEMA_REFERENCE = {
    "path": "formal/reviews/schemas/semantic-identity-v1.schema.json",
    "sha256": "fc9e6a4dc241508c50a1d1671c9f43bd04ab257a8d0ad5b6319ba5522966a3f3",
}
PROTOCOL_V8_SQC_CATALOG_SCHEMA_REFERENCE = {
    "path": "formal/reviews/schemas/semantic-question-contract-catalog-v1.schema.json",
    "sha256": "dca83227b9a4c6c8bde3dbce381027a94079648fd1fec1ead861c57219bdd8ca",
}
PROTOCOL_V8_PREDICATE_CATALOG_SCHEMA_REFERENCE = {
    "path": "formal/reviews/schemas/predicate-revision-catalog-v1.schema.json",
    "sha256": "da100b5f6ca9d40bdf7e07a1560d9ef0ede321c7bb4f9fb3977aa9d815fae20e",
}
PROTOCOL_V8_QUALIFICATION_CATALOG_SCHEMA_REFERENCE = {
    "path": "formal/reviews/schemas/qualification-contract-catalog-v1.schema.json",
    "sha256": "cb490d4a530f2438d051134f5ca588ecfa42fd5b24bf1bbb2e75cdaa1e40d5a3",
}
PROTOCOL_V8_SQC_CATALOG_REFERENCE = {
    "path": "formal/reviews/contracts/gate-a-semantic-question-contracts-v8.json",
    "sha256": "ad347de040e6b48730af346532d97a6553a8604bbdf1fb4dd45abe3d41336daf",
}
PROTOCOL_V8_PREDICATE_CATALOG_REFERENCE = {
    "path": "formal/reviews/contracts/gate-a-predicate-revisions-v8.json",
    "sha256": "895007928cf71e56c2e1908e2b8540a99ef92b8725eb9a4feb9167053b74d788",
}
PROTOCOL_V8_QUALIFICATION_CATALOG_REFERENCE = {
    "path": "formal/reviews/contracts/gate-a-qualification-contracts-v8.json",
    "sha256": "3be09c8de68f70e2c5cfe1409f417dfffc38bc62502df0036c4bc073bfafd2f1",
}
PROTOCOL_V8_COGNITIVE_EXECUTION_PACKET_SCHEMA_REFERENCE = {
    "path": "formal/reviews/schemas/cognitive-execution-packet-v1.schema.json",
    "sha256": "93deddfd3b69c1e69f208b15df594e74d57e47d2f074143f364cb7c300a841fc",
}
PROTOCOL_V8_SEMANTIC_QUESTION_BINDING_SCHEMA_REFERENCE = {
    "path": "formal/reviews/schemas/semantic-question-binding-v1.schema.json",
    "sha256": "fae52d48d08df8e9c3d7cafc74899913f4cc5655fb0a7ac8eb594df6edece15e",
}
PROTOCOL_V8_SEMANTIC_ADMISSION_ORIGIN_WITNESS_SCHEMA_REFERENCE = {
    "path": "formal/reviews/schemas/semantic-admission-origin-witness-v1.schema.json",
    "sha256": "acdcf78b6862080f5147df525bc919e2b8eb6eb94b3c920fee8b9886e582607b",
}
PROTOCOL_V8_FINDING_ADJUDICATION_SUPPLEMENT_V2_SCHEMA_REFERENCE = {
    "path": "formal/reviews/schemas/finding-adjudication-supplement-v2.schema.json",
    "sha256": "001050946c7275ba768676ea4dc8c24dfc2af5b1b285475864d050cbfe95991a",
}
PROTOCOL_V8_REVIEW_EVIDENCE_V6_SCHEMA_REFERENCE = {
    "path": "formal/reviews/meta-schemas/review-evidence-v6.schema.json",
    "sha256": "d91fa2e6fe3f3e00065cf5631ea8737de9e4f314ea52d945517f27c968770c63",
}
PROTOCOL_V8_ADJUDICATION_PROMPT_V3_REFERENCE = {
    "path": "formal/reviews/prompts/gate-a-adjudication-v3.md",
    "sha256": "19f40526aea2ffaae324859b3f1fd21e516d7230b237d3a31234f3678dd8770f",
}
PROTOCOL_V8_CHALLENGE_PROMPT_V2_REFERENCE = {
    "path": "formal/reviews/prompts/gate-a-challenge-v2.md",
    "sha256": "386f44d5f790f80821ab90170828469da844b3fd6d26852963b0c72b487d7edd",
}
PROTOCOL_V8_REPAIR_PROMPT_V3_REFERENCE = {
    "path": "formal/reviews/prompts/gate-a-repair-v3.md",
    "sha256": "3b42a6e99d85aebc29574d6130709ef641a4cc80595249e4623710db4a547e1c",
}
PROTOCOL_V8_META_SCHEMA_REFERENCE = {
    "path": "formal/reviews/meta-schemas/review-protocol-bundle-v8.schema.json",
    "sha256": "179687faf37035245ddf117c9604621ebef1d104e07ae31f66eb042589097801",
}
PROTOCOL_V8_BUNDLE_REFERENCE = {
    "path": "formal/reviews/protocols/gate-a-campaign-protocol-v8.json",
    "sha256": "e83bb163519e6f278d6111b1d53f0218e0a3c0fece11ead91c1548d5d13219f5",
}
PROTOCOL_V8_PREDECESSOR_REFERENCE = {
    "path": "formal/reviews/protocols/gate-a-campaign-protocol-v7.json",
    "sha256": "b9c6cde1624590d43686703b5dba991ca7a8a46f65a65d047a52197c02686f94",
}

PROTOCOL_V8_SQC_REVISION_IDS = (
    "turnlock.sqc:DecisionNecessityChallenge@1",
    "turnlock.sqc:DiscoveryClassificationInitial@1",
    "turnlock.sqc:DiscoveryDecisionRequiredRevision@1",
    "turnlock.sqc:DiscoveryNoNormativeImpactRevision@1",
    "turnlock.sqc:MaterialityAssessmentInitial@1",
    "turnlock.sqc:MaterialityAssessmentRevision@1",
    "turnlock.sqc:MaterialityChallenge@1",
    "turnlock.sqc:NoNormativeImpactChallenge@1",
    "turnlock.sqc:RealizationScopeChallenge@1",
    "turnlock.sqc:RealizationScopeInitial@1",
    "turnlock.sqc:RealizationScopeRevision@1",
    "turnlock.sqc:RefutationChallenge@1",
    "turnlock.sqc:RefutationInitial@1",
    "turnlock.sqc:RefutationRevision@1",
    "turnlock.sqc:RepairRealizationChallenge@1",
    "turnlock.sqc:RepairRealizationInitial@1",
    "turnlock.sqc:RepairRealizationRevision@1",
    "turnlock.sqc:UniqueCorrectionChallenge@1",
    "turnlock.sqc:UniqueCorrectionInitial@1",
    "turnlock.sqc:UniqueCorrectionRevision@1",
)

PROTOCOL_V8_PREDICATE_REVISION_IDS = (
    "turnlock.predicate:AcceptedRealizationScope@1",
    "turnlock.predicate:AcceptedRepairRealization@1",
    "turnlock.predicate:AcceptedUniqueCorrection@1",
    "turnlock.predicate:DecisionNecessityCandidate@1",
    "turnlock.predicate:DecisionRequiredDiscoveryStatement@1",
    "turnlock.predicate:QualifiedDecisionNecessity@1",
    "turnlock.predicate:QualifiedNoNormativeImpact@1",
    "turnlock.predicate:QualifiedNonMateriality@1",
    "turnlock.predicate:QualifiedPositiveMateriality@1",
    "turnlock.predicate:QualifiedRefutation@1",
    "turnlock.predicate:RefutationExhaustionWithoutQualifiedRefutation@1",
    "turnlock.predicate:TargetedDiscoveryStatement@1",
    "turnlock.predicate:UniqueCorrectionExhaustion@1",
)

PROTOCOL_V8_QUALIFICATION_REVISION_IDS = (
    "turnlock.qualification:DecisionNecessityQualification@1",
    "turnlock.qualification:MaterialityAssessmentQualification@1",
    "turnlock.qualification:NoNormativeImpactQualification@1",
    "turnlock.qualification:RealizationScopeQualification@1",
    "turnlock.qualification:RefutationQualification@1",
    "turnlock.qualification:RepairRealizationQualification@1",
    "turnlock.qualification:UniqueCorrectionQualification@1",
)
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


_PROTOCOL_V8_E1_IDENTITY_DOMAINS = frozenset(
    {
        "turnlock.semantic-value.v1",
        "turnlock.logical-question.v1",
        "turnlock.semantic-admission.v1",
        "turnlock.semantic-fact.v1",
        "turnlock.qualification-key.v1",
    }
)
_PROTOCOL_V8_E1_IDENTITY_FRAME = "turnlock.identity-frame.v1"
_PROTOCOL_V8_E1_SEMANTIC_VALUE_TYPE = re.compile(
    r"^turnlock\.semantic-value:[A-Za-z][A-Za-z0-9]*@[1-9][0-9]*$"
)
_PROTOCOL_V8_E1_SQC_ID = re.compile(
    r"^turnlock\.sqc:[A-Za-z][A-Za-z0-9]*@[1-9][0-9]*$"
)
_PROTOCOL_V8_E1_PREDICATE_ID = re.compile(
    r"^turnlock\.predicate:[A-Za-z][A-Za-z0-9]*@[1-9][0-9]*$"
)
_PROTOCOL_V8_E1_QUALIFICATION_ID = re.compile(
    r"^turnlock\.qualification:[A-Za-z][A-Za-z0-9]*@[1-9][0-9]*$"
)
_PROTOCOL_V8_E1_SEMANTIC_VALUE_ID = re.compile(
    r"^semantic-value-sha256:[0-9a-f]{64}$"
)
_PROTOCOL_V8_E1_QLEK = re.compile(r"^qlek-sha256:[0-9a-f]{64}$")
_PROTOCOL_V8_E1_ADMISSION_ID = re.compile(
    r"^semantic-admission-sha256:[0-9a-f]{64}$"
)
_PROTOCOL_V8_E1_FACT_ID = re.compile(
    r"^semantic-fact-sha256:[0-9a-f]{64}$"
)
_PROTOCOL_V8_E1_QUALIFICATION_KEY = re.compile(
    r"^qualification-key-sha256:[0-9a-f]{64}$"
)


def _protocol_v8_e1_decimal_integer_bytes(value: int) -> bytes:
    """Serialize one mathematical integer without Python decimal digit limits."""
    if type(value) is not int:
        raise TypeError("semantic integer must have exact Python int type")
    if value == 0:
        return b"0"

    negative = value < 0
    remaining = -value if negative else value
    base = 1_000_000_000
    chunks: list[int] = []

    while remaining:
        remaining, chunk = divmod(remaining, base)
        chunks.append(chunk)

    rendered = str(chunks[-1])
    if len(chunks) > 1:
        rendered += "".join(
            f"{chunk:09d}"
            for chunk in reversed(chunks[:-1])
        )
    if negative:
        rendered = "-" + rendered
    return rendered.encode("ascii")


def _protocol_v8_e1_semantic_value_errors(
    value: object,
    label: str,
    seen: set[int] | None = None,
) -> list[str]:
    """Validate the exact C2 CanonicalJsonValueV1 domain."""
    errors: list[str] = []
    if seen is None:
        seen = set()

    if value is None or type(value) is bool or type(value) is int:
        return errors

    if type(value) is float:
        return [f"{label}: floating-point semantic values are forbidden"]

    if type(value) is str:
        if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            errors.append(
                f"{label}: Unicode surrogate code points are forbidden"
            )
        return errors

    if type(value) is list:
        identity = id(value)
        if identity in seen:
            return [f"{label}: recursive semantic arrays are forbidden"]
        seen.add(identity)
        try:
            for index, item in enumerate(value):
                errors.extend(
                    _protocol_v8_e1_semantic_value_errors(
                        item,
                        f"{label}[{index}]",
                        seen,
                    )
                )
        finally:
            seen.remove(identity)
        return errors

    if type(value) is dict:
        identity = id(value)
        if identity in seen:
            return [f"{label}: recursive semantic objects are forbidden"]
        seen.add(identity)
        try:
            for key, item in value.items():
                if type(key) is not str:
                    errors.append(
                        f"{label}: semantic object keys must be strings"
                    )
                    continue
                errors.extend(
                    _protocol_v8_e1_semantic_value_errors(
                        key,
                        f"{label} object key",
                        seen,
                    )
                )
                errors.extend(
                    _protocol_v8_e1_semantic_value_errors(
                        item,
                        f"{label}.{key}",
                        seen,
                    )
                )
        finally:
            seen.remove(identity)
        return errors

    return [
        f"{label}: unsupported semantic JSON value type "
        f"{type(value).__name__}"
    ]


def _protocol_v8_e1_json_string_bytes(value: str) -> bytes:
    errors = _protocol_v8_e1_semantic_value_errors(
        value,
        "semantic JSON string",
    )
    if errors:
        raise ValueError(errors[0])
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _protocol_v8_e1_canonical_json_value_bytes(value: object) -> bytes:
    """Implement CanonicalJsonValueBytesV1 without integer-width limits."""
    errors = _protocol_v8_e1_semantic_value_errors(
        value,
        "semantic JSON value",
    )
    if errors:
        raise ValueError(errors[0])

    def encode(item: object) -> bytes:
        if item is None:
            return b"null"
        if type(item) is bool:
            return b"true" if item else b"false"
        if type(item) is int:
            return _protocol_v8_e1_decimal_integer_bytes(item)
        if type(item) is str:
            return _protocol_v8_e1_json_string_bytes(item)
        if type(item) is list:
            return b"[" + b",".join(encode(child) for child in item) + b"]"
        if type(item) is dict:
            ordered = sorted(
                item.items(),
                key=lambda pair: pair[0].encode("utf-8"),
            )
            return b"{" + b",".join(
                _protocol_v8_e1_json_string_bytes(key)
                + b":"
                + encode(child)
                for key, child in ordered
            ) + b"}"
        raise AssertionError("validated semantic JSON type became unreachable")

    return encode(value)


def _protocol_v8_e1_parse_decimal_integer(text: str) -> int:
    negative = text.startswith("-")
    digits = text[1:] if negative else text
    value = 0
    for offset in range(0, len(digits), 9):
        chunk = digits[offset : offset + 9]
        value = value * (10 ** len(chunk)) + int(chunk)
    return -value if negative else value


def _protocol_v8_e1_reject_float(_text: str) -> object:
    raise ValueError("floating-point semantic JSON numbers are forbidden")


def _protocol_v8_e1_reject_constant(_text: str) -> object:
    raise ValueError("non-finite semantic JSON numbers are forbidden")


def _protocol_v8_e1_object_from_pairs(
    pairs: list[tuple[str, object]],
) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(
                f"duplicate semantic JSON object key {key!r}"
            )
        result[key] = value
    return result


def _protocol_v8_e1_parse_canonical_json_value(data: bytes) -> object:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("semantic JSON must be valid UTF-8") from error

    try:
        value = json.loads(
            text,
            parse_int=_protocol_v8_e1_parse_decimal_integer,
            parse_float=_protocol_v8_e1_reject_float,
            parse_constant=_protocol_v8_e1_reject_constant,
            object_pairs_hook=_protocol_v8_e1_object_from_pairs,
        )
    except (json.JSONDecodeError, ValueError) as error:
        raise ValueError(f"invalid semantic JSON: {error}") from error

    errors = _protocol_v8_e1_semantic_value_errors(
        value,
        "semantic JSON value",
    )
    if errors:
        raise ValueError(errors[0])

    canonical = _protocol_v8_e1_canonical_json_value_bytes(value)
    if canonical != data:
        raise ValueError("semantic JSON is not canonical C2 serialization")
    return value


def _protocol_v8_e1_identity_hash(domain: str, payload: object) -> str:
    if domain not in _PROTOCOL_V8_E1_IDENTITY_DOMAINS:
        raise ValueError(f"unsupported protocol-v8 identity domain {domain!r}")
    framed = {
        "domain": domain,
        "frame": _PROTOCOL_V8_E1_IDENTITY_FRAME,
        "payload": payload,
    }
    return hashlib.sha256(
        _protocol_v8_e1_canonical_json_value_bytes(framed)
    ).hexdigest()


def _protocol_v8_e1_semantic_value_id(
    value_type: str,
    value: object,
) -> str:
    if type(value_type) is not str or _PROTOCOL_V8_E1_SEMANTIC_VALUE_TYPE.fullmatch(value_type) is None:
        raise ValueError("invalid SemanticValueTypeRevisionId")
    _protocol_v8_e1_canonical_json_value_bytes(value)
    return "semantic-value-sha256:" + _protocol_v8_e1_identity_hash(
        "turnlock.semantic-value.v1",
        {
            "valueType": value_type,
            "value": value,
        },
    )


def _protocol_v8_e1_qlek(descriptor: dict) -> str:
    return "qlek-sha256:" + _protocol_v8_e1_identity_hash(
        "turnlock.logical-question.v1",
        descriptor,
    )


def _protocol_v8_e1_semantic_admission_id(
    qlek: str,
    semantic_candidate: object,
) -> str:
    if type(qlek) is not str or _PROTOCOL_V8_E1_QLEK.fullmatch(qlek) is None:
        raise ValueError("invalid QLEK")
    _protocol_v8_e1_canonical_json_value_bytes(semantic_candidate)
    return "semantic-admission-sha256:" + _protocol_v8_e1_identity_hash(
        "turnlock.semantic-admission.v1",
        {
            "qlek": qlek,
            "semanticCandidate": semantic_candidate,
        },
    )


def _protocol_v8_e1_fact_id(descriptor: dict) -> str:
    if type(descriptor) is not dict or set(descriptor) != {"schema", "predicateRevision", "arguments"}:
        raise ValueError("invalid SemanticFactDescriptorV1 shape")
    if descriptor.get("schema") != "turnlock.semantic-fact-descriptor.v1":
        raise ValueError("invalid SemanticFactDescriptorV1 schema")
    predicate = descriptor.get("predicateRevision")
    if type(predicate) is not str or _PROTOCOL_V8_E1_PREDICATE_ID.fullmatch(predicate) is None:
        raise ValueError("invalid PredicateRevisionId")
    if type(descriptor.get("arguments")) is not dict:
        raise ValueError("SemanticFactDescriptorV1 arguments must be an object")
    _protocol_v8_e1_canonical_json_value_bytes(descriptor)
    return "semantic-fact-sha256:" + _protocol_v8_e1_identity_hash(
        "turnlock.semantic-fact.v1",
        descriptor,
    )


def _protocol_v8_e1_qualification_key(descriptor: dict) -> str:
    if type(descriptor) is not dict or set(descriptor) != {"schema", "qualificationContract", "anchorAdmission", "additionalInputs"}:
        raise ValueError("invalid QualificationKeyDescriptorV1 shape")
    if descriptor.get("schema") != "turnlock.qualification-key-descriptor.v1":
        raise ValueError("invalid QualificationKeyDescriptorV1 schema")
    qualification = descriptor.get("qualificationContract")
    if type(qualification) is not str or _PROTOCOL_V8_E1_QUALIFICATION_ID.fullmatch(qualification) is None:
        raise ValueError("invalid QualificationContractRevisionId")
    anchor = descriptor.get("anchorAdmission")
    if type(anchor) is not dict or set(anchor) != {"kind", "admissionId"} or anchor.get("kind") != "semantic-admission":
        raise ValueError("invalid qualification anchorAdmission")
    admission_id = anchor.get("admissionId")
    if type(admission_id) is not str or _PROTOCOL_V8_E1_ADMISSION_ID.fullmatch(admission_id) is None:
        raise ValueError("invalid qualification anchor SemanticAdmissionId")
    if type(descriptor.get("additionalInputs")) is not dict:
        raise ValueError("QualificationKeyDescriptorV1 additionalInputs must be an object")
    _protocol_v8_e1_canonical_json_value_bytes(descriptor)
    return "qualification-key-sha256:" + _protocol_v8_e1_identity_hash(
        "turnlock.qualification-key.v1",
        descriptor,
    )


def _protocol_v8_e1_contract_map(
    root: Path,
) -> tuple[dict[str, dict], list[str]]:
    catalog, errors = _load_json_object_artifact(
        root,
        PROTOCOL_V8_SQC_CATALOG_REFERENCE,
        "inactive protocol v8 E1 SemanticQuestionContract catalog",
        REVIEW_CONTRACTS_PREFIX,
        REVIEW_JSON_OUTPUT_SUFFIX,
        require_canonical=True,
    )
    if catalog is None:
        return {}, errors

    contracts: dict[str, dict] = {}
    for index, entry in enumerate(_sequence(catalog.get("contracts"))):
        label = f"inactive protocol v8 E1 contracts[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: entry must be a mapping")
            continue
        revision_id = entry.get("revision_id")
        if not isinstance(revision_id, str):
            errors.append(f"{label}: revision_id must be a string")
            continue
        if revision_id in contracts:
            errors.append(f"{label}: duplicate revision_id {revision_id!r}")
            continue
        contracts[revision_id] = entry
    return contracts, errors


def _protocol_v8_e1_exact_keys(
    value: object,
    expected: set[str],
    label: str,
) -> list[str]:
    if type(value) is not dict:
        return [f"{label}: value must be an object"]
    actual = set(value)
    if actual != expected:
        return [
            f"{label}: key set must be exactly {sorted(expected)!r}; "
            f"found {sorted(actual)!r}"
        ]
    return []


def _protocol_v8_e1_ref_errors(
    value: object,
    descriptor: dict,
    label: str,
) -> list[str]:
    kind = descriptor.get("kind")

    if kind == "semantic-value":
        errors = _protocol_v8_e1_exact_keys(
            value,
            {"kind", "valueType", "valueId"},
            label,
        )
        if errors:
            return errors
        assert isinstance(value, dict)
        if value.get("kind") != "semantic-value":
            errors.append(f"{label}: kind must be semantic-value")
        if value.get("valueType") != descriptor.get("value_type"):
            errors.append(f"{label}: valueType does not match the SQC contract")
        value_id = value.get("valueId")
        if type(value_id) is not str or _PROTOCOL_V8_E1_SEMANTIC_VALUE_ID.fullmatch(value_id) is None:
            errors.append(f"{label}: valueId must be an exact SemanticValueId")
        return errors

    if kind == "semantic-admission":
        errors = _protocol_v8_e1_exact_keys(
            value,
            {"kind", "admissionId"},
            label,
        )
        if errors:
            return errors
        assert isinstance(value, dict)
        if value.get("kind") != "semantic-admission":
            errors.append(f"{label}: kind must be semantic-admission")
        admission_id = value.get("admissionId")
        if type(admission_id) is not str or _PROTOCOL_V8_E1_ADMISSION_ID.fullmatch(admission_id) is None:
            errors.append(f"{label}: admissionId must be an exact SemanticAdmissionId")
        return errors

    if kind == "semantic-fact":
        errors = _protocol_v8_e1_exact_keys(
            value,
            {"kind", "predicateRevision", "factId"},
            label,
        )
        if errors:
            return errors
        assert isinstance(value, dict)
        if value.get("kind") != "semantic-fact":
            errors.append(f"{label}: kind must be semantic-fact")
        if value.get("predicateRevision") != descriptor.get("predicate_revision"):
            errors.append(
                f"{label}: predicateRevision does not match the SQC contract"
            )
        fact_id = value.get("factId")
        if type(fact_id) is not str or _PROTOCOL_V8_E1_FACT_ID.fullmatch(fact_id) is None:
            errors.append(f"{label}: factId must be an exact FactId")
        return errors

    if kind == "exact-authority":
        errors = _protocol_v8_e1_exact_keys(
            value,
            {"kind", "authorityType", "authorityId"},
            label,
        )
        if errors:
            return errors
        assert isinstance(value, dict)
        if value.get("kind") != "exact-authority":
            errors.append(f"{label}: kind must be exact-authority")
        if value.get("authorityType") != descriptor.get("authority_type"):
            errors.append(
                f"{label}: authorityType does not match the SQC contract"
            )
        authority_id = value.get("authorityId")
        if type(authority_id) is not str or not authority_id:
            errors.append(f"{label}: authorityId must be a non-empty string")
        return errors

    return [f"{label}: unsupported SQC logical input kind {kind!r}"]


def _protocol_v8_e1_descriptor_errors(
    contracts: dict[str, dict],
    descriptor: object,
    label: str,
) -> list[str]:
    errors = _protocol_v8_e1_semantic_value_errors(descriptor, label)
    if errors:
        return errors
    errors.extend(
        _protocol_v8_e1_exact_keys(
            descriptor,
            {"schema", "semanticQuestionContract", "exactLogicalInput"},
            label,
        )
    )
    if errors:
        return errors
    assert isinstance(descriptor, dict)

    if descriptor.get("schema") != "turnlock.logical-question-descriptor.v1":
        errors.append(
            f"{label}: schema must be turnlock.logical-question-descriptor.v1"
        )

    contract_id = descriptor.get("semanticQuestionContract")
    contract = contracts.get(contract_id) if isinstance(contract_id, str) else None
    if contract is None:
        errors.append(f"{label}: semanticQuestionContract is not an exact P8 SQC")
        return errors

    exact_input = descriptor.get("exactLogicalInput")
    if type(exact_input) is not dict:
        errors.append(f"{label}: exactLogicalInput must be an object")
        return errors

    logical_input = _mapping(_mapping(contract.get("definition")).get("logical_input"))
    expected_names = set(logical_input)
    if set(exact_input) != expected_names:
        errors.append(
            f"{label}: exactLogicalInput keys must equal the selected SQC input keys"
        )
        return errors

    for name in sorted(expected_names):
        input_descriptor = logical_input.get(name)
        if not isinstance(input_descriptor, dict):
            errors.append(
                f"{label}.{name}: SQC catalog logical input descriptor is invalid"
            )
            continue
        errors.extend(
            _protocol_v8_e1_ref_errors(
                exact_input.get(name),
                input_descriptor,
                f"{label}.exactLogicalInput.{name}",
            )
        )
    return errors


def _protocol_v8_e1_recompute_structural_qlek(
    contracts: dict[str, dict],
    descriptor: object,
) -> tuple[str | None, list[str]]:
    """Recompute structural QLEK; later E2/E3 must resolve every direct ref."""
    errors = _protocol_v8_e1_descriptor_errors(
        contracts,
        descriptor,
        "protocol-v8 LogicalQuestionDescriptor",
    )
    if errors:
        return None, errors
    assert isinstance(descriptor, dict)
    return _protocol_v8_e1_qlek(descriptor), []


def _protocol_v8_e1_candidate_variant(
    definition: dict,
    candidate: object,
) -> str | None:
    if definition.get("question_kind") == "challenge":
        return "ChallengeSemanticValue"

    if isinstance(candidate, dict) and candidate.get("kind") == "not-established":
        return "NotEstablished"

    execution = _mapping(definition.get("execution"))
    task = execution.get("task")
    if task == "materiality-assessment":
        return "MaterialityAssessmentValue"
    if task == "refutation":
        return "RefutationCandidate"
    if task == "discovery-classification":
        if isinstance(candidate, dict) and candidate.get("kind") == "revised-candidate":
            return "RevisedDiscoveryStatement"
        return "DiscoveryClassificationValue"
    if task == "unique-correction-derivation":
        return "UniqueCorrectionCandidate"
    if task == "realization-scope-derivation":
        return "RealizationScopeCandidate"
    if task == "repair-realization":
        return "RepairRealizationCandidate"
    return None


def _protocol_v8_e1_challenge_semantic_errors(
    definition: dict,
    output: dict,
    label: str,
) -> list[str]:
    errors: list[str] = []
    challenge = _mapping(definition.get("challenge"))
    expected_kind = challenge.get("challenge_kind")
    if output.get("challenge_kind") != expected_kind:
        errors.append(f"{label}: challenge_kind does not match the selected SQC")

    expected_objectives = list(_sequence(challenge.get("objectives")))
    assessments = [
        item
        for item in _sequence(output.get("objective_assessments"))
        if isinstance(item, dict)
    ]
    actual_objectives = [item.get("objective") for item in assessments]
    if actual_objectives != expected_objectives:
        errors.append(
            f"{label}: objective_assessments must use the exact ordered SQC objectives"
        )

    objections = [
        item
        for item in _sequence(output.get("objections"))
        if isinstance(item, dict)
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

    listed: set[str] = set()
    for assessment in assessments:
        objective = assessment.get("objective")
        for objection_id in _sequence(assessment.get("objection_ids")):
            if not isinstance(objection_id, str):
                continue
            if objection_id in listed:
                errors.append(f"{label}: objection {objection_id!r} listed more than once")
            listed.add(objection_id)
            objection = objection_by_id.get(objection_id)
            if objection is None:
                errors.append(f"{label}: unknown objection {objection_id!r}")
            elif objection.get("objective") != objective:
                errors.append(
                    f"{label}: objection {objection_id!r} objective does not match its assessment"
                )

    for objection_id in sorted(set(objection_by_id) - listed):
        errors.append(f"{label}: objection {objection_id!r} is not assessed")
    return errors


def _protocol_v8_e1_project_semantic_candidate(
    contract: dict,
    output: object,
    validator: Draft202012Validator,
    label: str,
) -> tuple[object | None, list[str]]:
    errors = [
        f"{label}: output schema violation: {error.message}"
        for error in validator.iter_errors(output)
    ]
    if errors:
        return None, errors
    if not isinstance(output, dict):
        return None, [f"{label}: protocol output must be an object"]

    definition = _mapping(contract.get("definition"))
    question_kind = definition.get("question_kind")

    if question_kind == "challenge":
        errors.extend(
            _protocol_v8_e1_challenge_semantic_errors(
                definition,
                output,
                label,
            )
        )
        if errors:
            return None, errors
        candidate: object = {
            "objective_assessments": copy.deepcopy(output.get("objective_assessments")),
            "objections": copy.deepcopy(output.get("objections")),
        }
    else:
        expected_task = _mapping(definition.get("execution")).get("task")
        if output.get("task") != expected_task:
            errors.append(f"{label}: task does not match the selected SQC")
            return None, errors
        candidate = copy.deepcopy(output.get("result"))

    candidate_errors = _protocol_v8_e1_semantic_value_errors(
        candidate,
        f"{label} semantic candidate",
    )
    if candidate_errors:
        return None, errors + candidate_errors

    variant = _protocol_v8_e1_candidate_variant(definition, candidate)
    allowed = _sequence(definition.get("semantic_result_variants"))
    if variant is None or variant not in allowed:
        errors.append(
            f"{label}: projected semantic candidate variant {variant!r} "
            "is not permitted by the selected SQC"
        )
        return None, errors
    return candidate, errors


def _protocol_v8_e1_sample_input(input_descriptor: dict) -> dict:
    kind = input_descriptor.get("kind")
    if kind == "semantic-value":
        return {
            "kind": "semantic-value",
            "valueType": input_descriptor.get("value_type"),
            "valueId": "semantic-value-sha256:" + "0" * 64,
        }
    if kind == "semantic-admission":
        return {
            "kind": "semantic-admission",
            "admissionId": "semantic-admission-sha256:" + "1" * 64,
        }
    if kind == "semantic-fact":
        return {
            "kind": "semantic-fact",
            "predicateRevision": input_descriptor.get("predicate_revision"),
            "factId": "semantic-fact-sha256:" + "2" * 64,
        }
    if kind == "exact-authority":
        return {
            "kind": "exact-authority",
            "authorityType": input_descriptor.get("authority_type"),
            "authorityId": "candidate-revision-test",
        }
    raise ValueError(f"unsupported sample input kind {kind!r}")


def _protocol_v8_e1_output_validators(
    root: Path,
) -> tuple[dict[str, Draft202012Validator], list[str]]:
    bundle, errors = _load_json_object_artifact(
        root,
        PROTOCOL_V8_BUNDLE_REFERENCE,
        "inactive protocol v8 E1 bundle",
        REVIEW_PROTOCOLS_PREFIX,
        REVIEW_PROTOCOL_BUNDLE_SUFFIX,
        require_canonical=True,
    )
    if bundle is None:
        return {}, errors
    validators, validator_errors = _bundle_selected_validators(
        root,
        bundle,
        "inactive protocol v8 E1 bundle",
    )
    errors.extend(validator_errors)
    result: dict[str, Draft202012Validator] = {}
    for key in ("adjudication-output", "challenge-output"):
        validator = validators.get(key)
        if validator is None:
            errors.append(f"inactive protocol v8 E1: missing {key} validator")
        else:
            result[key] = validator
    return result, errors


def _inactive_protocol_v8_e1_semantic_identity_errors(root: Path) -> list[str]:
    """Exercise the exact C2/C1 identity and structural-QLEK reference oracle."""
    errors: list[str] = []

    huge = 10 ** 5000 + 7
    huge_bytes = _protocol_v8_e1_canonical_json_value_bytes(huge)
    if len(huge_bytes) != 5001 or not huge_bytes.endswith(b"7"):
        errors.append("inactive protocol v8 E1: arbitrary-precision integer serialization failed")
    else:
        try:
            round_trip = _protocol_v8_e1_parse_canonical_json_value(huge_bytes)
        except ValueError as error:
            errors.append(f"inactive protocol v8 E1: huge integer parse failed: {error}")
        else:
            if round_trip != huge:
                errors.append("inactive protocol v8 E1: huge integer round-trip changed value")

    invalid_values: list[tuple[str, object]] = [
        ("float", 1.0),
        ("surrogate", "\ud800"),
        ("non-string-key", {1: "x"}),
    ]
    recursive: list[object] = []
    recursive.append(recursive)
    invalid_values.append(("recursive", recursive))
    for name, value in invalid_values:
        if not _protocol_v8_e1_semantic_value_errors(value, name):
            errors.append(f"inactive protocol v8 E1: {name} semantic value was not rejected")

    for name, data in (
        ("duplicate-key", b'{"a":1,"a":2}'),
        ("NaN", b'NaN'),
        ("negative-zero", b'-0'),
    ):
        try:
            _protocol_v8_e1_parse_canonical_json_value(data)
        except ValueError:
            pass
        else:
            errors.append(f"inactive protocol v8 E1: {name} JSON was not rejected")

    try:
        _protocol_v8_e1_identity_hash("turnlock.unknown.v1", {})
    except ValueError:
        pass
    else:
        errors.append("inactive protocol v8 E1: unknown identity domain was accepted")

    composed = _protocol_v8_e1_semantic_value_id(
        "turnlock.semantic-value:Test@1",
        "é",
    )
    decomposed = _protocol_v8_e1_semantic_value_id(
        "turnlock.semantic-value:Test@1",
        "e\u0301",
    )
    if composed == decomposed:
        errors.append("inactive protocol v8 E1: Unicode normalization changed identity")

    if _protocol_v8_e1_semantic_value_id(
        "turnlock.semantic-value:Test@1",
        [1, 2],
    ) == _protocol_v8_e1_semantic_value_id(
        "turnlock.semantic-value:Test@1",
        [2, 1],
    ):
        errors.append("inactive protocol v8 E1: array ordering did not affect identity")

    if _protocol_v8_e1_semantic_value_id(
        "turnlock.semantic-value:Test@1",
        {"x": 1, "s": "é"},
    ) != (
        "semantic-value-sha256:"
        "ac25a4a9320254a912b73fb570fb2ce0df1ae1fe23bef947ef2ef6885d3ee0e0"
    ):
        errors.append("inactive protocol v8 E1: SemanticValueId test vector mismatch")

    finding_basis = {
        "schema": "turnlock.finding-adjudication-basis.v1",
        "semanticSubject": {
            "selector": "gate-a-assurance-decomposition-v1",
            "sha256": "0" * 64,
        },
        "currentProtocol": {
            "protocolId": "gate-a-campaign-protocol-v8",
            "bundleSha256": "1" * 64,
        },
        "sourceFinding": {
            "reviewCampaignId": "REVIEW-TEST",
            "findingId": "F-1",
            "substantiveFindingSha256": "2" * 64,
        },
    }
    finding_basis_id = _protocol_v8_e1_semantic_value_id(
        "turnlock.semantic-value:FindingAdjudicationBasis@1",
        finding_basis,
    )
    if finding_basis_id != (
        "semantic-value-sha256:"
        "7553e7df2a659ef9897fd2c699660a98abf99d3c2997c5a4c1390299a2ac4753"
    ):
        errors.append("inactive protocol v8 E1: FindingAdjudicationBasis identity mismatch")

    contracts, contract_errors = _protocol_v8_e1_contract_map(root)
    errors.extend(contract_errors)
    if len(contracts) != 20:
        errors.append("inactive protocol v8 E1: expected exactly 20 SQC contracts")

    descriptor = {
        "schema": "turnlock.logical-question-descriptor.v1",
        "semanticQuestionContract": "turnlock.sqc:MaterialityAssessmentInitial@1",
        "exactLogicalInput": {
            "findingAdjudicationBasis": {
                "kind": "semantic-value",
                "valueType": "turnlock.semantic-value:FindingAdjudicationBasis@1",
                "valueId": finding_basis_id,
            }
        },
    }
    qlek, qlek_errors = _protocol_v8_e1_recompute_structural_qlek(contracts, descriptor)
    errors.extend(qlek_errors)
    if qlek != (
        "qlek-sha256:"
        "865adc7398f25c140ce32008eb321570452ce54f5bb544a886fd67c3aa52012f"
    ):
        errors.append("inactive protocol v8 E1: MaterialityAssessmentInitial QLEK mismatch")

    candidate = {
        "authority_or_upstream_decision": True,
        "claim_structure": False,
        "normative_provenance": False,
        "modality_or_assurance_domain": False,
        "coverage_or_residual_assurance": False,
        "interaction_scope": False,
        "candidate_model_authorization": False,
        "rationale": "test",
    }
    admission_id = _protocol_v8_e1_semantic_admission_id(qlek or "", candidate)
    if admission_id != (
        "semantic-admission-sha256:"
        "50d5e8d5100a59311a140bd883f721769fabab9262ee2eeb598e9d7a10e02c1c"
    ):
        errors.append("inactive protocol v8 E1: SemanticAdmissionId vector mismatch")

    qualification_descriptor = {
        "schema": "turnlock.qualification-key-descriptor.v1",
        "qualificationContract": "turnlock.qualification:MaterialityAssessmentQualification@1",
        "anchorAdmission": {
            "kind": "semantic-admission",
            "admissionId": admission_id,
        },
        "additionalInputs": {},
    }
    qualification_key = _protocol_v8_e1_qualification_key(qualification_descriptor)
    if qualification_key != (
        "qualification-key-sha256:"
        "e1cc7da47bacb3042f8db303d01b0a7ae2b4a7b8a156496e90a8331ea36acdb2"
    ):
        errors.append("inactive protocol v8 E1: QualificationKey vector mismatch")

    fact_descriptor = {
        "schema": "turnlock.semantic-fact-descriptor.v1",
        "predicateRevision": "turnlock.predicate:QualifiedPositiveMateriality@1",
        "arguments": {
            "qualification": {
                "kind": "qualification-key",
                "qualificationContract": "turnlock.qualification:MaterialityAssessmentQualification@1",
                "qualificationKey": qualification_key,
            }
        },
    }
    if _protocol_v8_e1_fact_id(fact_descriptor) != (
        "semantic-fact-sha256:"
        "c9941247235f54717e3a042e2b23c0055f7c3d44b3371317fe199e620eef475c"
    ):
        errors.append("inactive protocol v8 E1: FactId vector mismatch")

    for contract_id, contract in sorted(contracts.items()):
        logical_input = _mapping(_mapping(contract.get("definition")).get("logical_input"))
        sample_input = {
            name: _protocol_v8_e1_sample_input(input_descriptor)
            for name, input_descriptor in logical_input.items()
            if isinstance(input_descriptor, dict)
        }
        sample_descriptor = {
            "schema": "turnlock.logical-question-descriptor.v1",
            "semanticQuestionContract": contract_id,
            "exactLogicalInput": sample_input,
        }
        sample_errors = _protocol_v8_e1_descriptor_errors(
            contracts,
            sample_descriptor,
            f"inactive protocol v8 E1 {contract_id}",
        )
        errors.extend(sample_errors)

        extra = copy.deepcopy(sample_descriptor)
        extra["exactLogicalInput"]["runId"] = "RUN-ANTI-CHEAT"
        if not _protocol_v8_e1_descriptor_errors(contracts, extra, "extra provenance"):
            errors.append(f"inactive protocol v8 E1: {contract_id} accepted extra runId input")

        if logical_input:
            missing = copy.deepcopy(sample_descriptor)
            first_name = next(iter(logical_input))
            del missing["exactLogicalInput"][first_name]
            if not _protocol_v8_e1_descriptor_errors(contracts, missing, "missing input"):
                errors.append(f"inactive protocol v8 E1: {contract_id} accepted missing input")

    validators, validator_errors = _protocol_v8_e1_output_validators(root)
    errors.extend(validator_errors)
    adjudication_validator = validators.get("adjudication-output")
    challenge_validator = validators.get("challenge-output")

    refutation_contract = contracts.get("turnlock.sqc:RefutationInitial@1")
    discovery_contract = contracts.get("turnlock.sqc:DiscoveryClassificationInitial@1")
    materiality_challenge = contracts.get("turnlock.sqc:MaterialityChallenge@1")

    if adjudication_validator is not None and refutation_contract is not None:
        refutation_output = {
            "adjudication_output_schema_version": "1.0",
            "task": "refutation",
            "result": {"kind": "not-established"},
        }
        projected, projection_errors = _protocol_v8_e1_project_semantic_candidate(
            refutation_contract,
            refutation_output,
            adjudication_validator,
            "inactive protocol v8 E1 refutation output",
        )
        errors.extend(projection_errors)
        if projected != {"kind": "not-established"}:
            errors.append("inactive protocol v8 E1: Refutation NotEstablished projection mismatch")

    if adjudication_validator is not None and discovery_contract is not None:
        discovery_negative = {
            "adjudication_output_schema_version": "1.0",
            "task": "discovery-classification",
            "result": {"kind": "not-established"},
        }
        _projected, projection_errors = _protocol_v8_e1_project_semantic_candidate(
            discovery_contract,
            discovery_negative,
            adjudication_validator,
            "inactive protocol v8 E1 discovery output",
        )
        if not projection_errors:
            errors.append("inactive protocol v8 E1: initial Discovery accepted NotEstablished")

    if challenge_validator is not None and materiality_challenge is not None:
        objectives = list(
            _sequence(
                _mapping(_mapping(materiality_challenge.get("definition")).get("challenge")).get("objectives")
            )
        )
        challenge_output = {
            "challenge_output_schema_version": "1.0",
            "challenge_kind": "materiality",
            "objective_assessments": [
                {"objective": objective, "objection_ids": []}
                for objective in objectives
            ],
            "objections": [],
        }
        projected, projection_errors = _protocol_v8_e1_project_semantic_candidate(
            materiality_challenge,
            challenge_output,
            challenge_validator,
            "inactive protocol v8 E1 challenge output",
        )
        errors.extend(projection_errors)
        expected_candidate = {
            "objective_assessments": challenge_output["objective_assessments"],
            "objections": [],
        }
        if projected != expected_candidate:
            errors.append("inactive protocol v8 E1: ChallengeSemanticValue projection mismatch")
        if isinstance(projected, dict) and "challenge_kind" in projected:
            errors.append("inactive protocol v8 E1: challenge_kind leaked into semantic candidate")

        reversed_output = copy.deepcopy(challenge_output)
        reversed_output["objective_assessments"] = list(
            reversed(reversed_output["objective_assessments"])
        )
        _projected, reversed_errors = _protocol_v8_e1_project_semantic_candidate(
            materiality_challenge,
            reversed_output,
            challenge_validator,
            "inactive protocol v8 E1 reversed challenge objectives",
        )
        if not reversed_errors:
            errors.append("inactive protocol v8 E1: challenge objective order was not enforced")

    return errors



_PROTOCOL_V8_E2_CLEARANCE_REASONS = frozenset(
    {
        "proven-not-executed",
        "terminal-technical-failure-no-completion",
        "protocol-invalid-completion",
    }
)
_PROTOCOL_V8_E2_VALIDATED_WITNESS_MARKER = object()


def _protocol_v8_e2_new_state() -> dict:
    """Create one disposable C3 reference state; it is not a runtime storage schema."""
    return {
        "coordination_epoch": 0,
        "generation_high_water": {},
        "effective_authority": {},
        "authority_grants": [],
        "executions": {},
        "admissions": {},
        "conflicts": {},
        "imported_unarmed_selection_required": set(),
    }


def _protocol_v8_e2_require_qlek(qlek: object) -> str:
    if type(qlek) is not str or _PROTOCOL_V8_E1_QLEK.fullmatch(qlek) is None:
        raise ValueError("E2 requires an exact QLEK")
    return qlek


def _protocol_v8_e2_execution_ids(
    state: dict,
    qlek: str,
) -> list[str]:
    return sorted(
        execution_id
        for execution_id, execution in state["executions"].items()
        if execution.get("qlek") == qlek
    )


def _protocol_v8_e2_active_unarmed_ids(
    state: dict,
    qlek: str,
) -> list[str]:
    return sorted(
        execution_id
        for execution_id in _protocol_v8_e2_execution_ids(state, qlek)
        if (
            state["executions"][execution_id].get("armed") is not True
            and state["executions"][execution_id].get("retired_unarmed") is not True
        )
    )


def _protocol_v8_e2_pending_completion_ids(
    state: dict,
    qlek: str,
) -> list[str]:
    return sorted(
        execution_id
        for execution_id in _protocol_v8_e2_execution_ids(state, qlek)
        if (
            state["executions"][execution_id].get("terminal_kind")
            == "protocol-valid"
            and state["executions"][execution_id].get("completion_reconciled")
            is not True
        )
    )


def _protocol_v8_e2_unreconciled_hazard(
    state: dict,
    execution_id: str,
) -> bool:
    execution = state["executions"].get(execution_id)
    if not isinstance(execution, dict) or execution.get("armed") is not True:
        return False

    if execution.get("hazard_clearance") in _PROTOCOL_V8_E2_CLEARANCE_REASONS:
        return False

    if (
        execution.get("terminal_kind") == "protocol-valid"
        and execution.get("completion_reconciled") is True
    ):
        return False

    return True


def _protocol_v8_e2_unreconciled_hazard_ids(
    state: dict,
    qlek: str,
) -> list[str]:
    return sorted(
        execution_id
        for execution_id in _protocol_v8_e2_execution_ids(state, qlek)
        if _protocol_v8_e2_unreconciled_hazard(state, execution_id)
    )


def _protocol_v8_e2_replacement_candidates(
    state: dict,
    qlek: str,
) -> list[str]:
    return sorted(
        execution_id
        for execution_id in _protocol_v8_e2_execution_ids(state, qlek)
        if (
            state["executions"][execution_id].get("armed") is True
            and state["executions"][execution_id].get("hazard_clearance")
            in _PROTOCOL_V8_E2_CLEARANCE_REASONS
            and state["executions"][execution_id].get("terminal_kind")
            != "protocol-valid"
            and state["executions"][execution_id].get("replaced_by") is None
        )
    )


def _protocol_v8_e2_consumable_admission(
    state: dict,
    qlek: str,
) -> bool:
    qlek = _protocol_v8_e2_require_qlek(qlek)
    admission = state["admissions"].get(qlek)

    if not isinstance(admission, dict):
        return False

    if qlek in state["conflicts"]:
        return False

    if not admission.get("witnesses"):
        return False

    return not _protocol_v8_e2_unreconciled_hazard_ids(state, qlek)


def _protocol_v8_e2_t1_acquire_authority(
    state: dict,
    qlek: str,
    generation: int,
) -> dict:
    """Reference T1. Generation has no minimum; it is only monotone per epoch."""
    qlek = _protocol_v8_e2_require_qlek(qlek)

    if type(generation) is not int:
        raise ValueError("AdmissionAuthority generation must be an exact integer")

    if qlek in state["conflicts"]:
        return {"status": "conflict"}

    admission = state["admissions"].get(qlek)
    if isinstance(admission, dict):
        return {
            "status": "reuse",
            "admission": copy.deepcopy(admission),
            "consumable": _protocol_v8_e2_consumable_admission(state, qlek),
        }

    pending = _protocol_v8_e2_pending_completion_ids(state, qlek)
    if pending:
        return {
            "status": "reconcile",
            "execution_ids": pending,
        }

    hazards = _protocol_v8_e2_unreconciled_hazard_ids(state, qlek)
    if hazards:
        return {
            "status": "blocked-hazard",
            "execution_ids": hazards,
        }

    if qlek in state["imported_unarmed_selection_required"]:
        return {"status": "blocked-unarmed-selection"}

    unarmed = _protocol_v8_e2_active_unarmed_ids(state, qlek)
    if len(unarmed) > 1:
        return {
            "status": "blocked-unarmed-selection",
            "execution_ids": unarmed,
        }

    previous = state["generation_high_water"].get(qlek)
    if previous is not None and generation <= previous:
        raise ValueError(
            "AdmissionAuthority generation must increase strictly within one epoch"
        )

    state["generation_high_water"][qlek] = generation
    handle = {
        "qlek": qlek,
        "epoch": state["coordination_epoch"],
        "generation": generation,
    }
    state["effective_authority"][qlek] = copy.deepcopy(handle)
    state["authority_grants"].append(copy.deepcopy(handle))

    return {
        "status": "authority",
        "handle": handle,
        "execution_id": unarmed[0] if unarmed else None,
    }


def _protocol_v8_e2_current_handle(
    state: dict,
    qlek: str,
    generation: int,
) -> dict:
    handle = state["effective_authority"].get(qlek)
    expected = {
        "qlek": qlek,
        "epoch": state["coordination_epoch"],
        "generation": generation,
    }
    if handle != expected:
        raise ValueError("AdmissionAuthority handle is stale or ineffective")
    return handle


def _protocol_v8_e2_t2_authorize_execution(
    state: dict,
    qlek: str,
    generation: int,
    execution_id: str,
    *,
    outer_authorized: bool,
    replacement_of: str | None = None,
    replacement_authorized: bool = False,
) -> dict:
    """Reference T2; create+SemanticExecutionBinding is atomic."""
    qlek = _protocol_v8_e2_require_qlek(qlek)

    if type(execution_id) is not str or not execution_id:
        raise ValueError("semantic Execution identity must be a non-empty string")

    _protocol_v8_e2_current_handle(state, qlek, generation)

    if qlek in state["conflicts"]:
        raise ValueError("semantic conflict blocks execution authorization")

    if qlek in state["admissions"]:
        raise ValueError("Admission(K) blocks execution authorization")

    if _protocol_v8_e2_pending_completion_ids(state, qlek):
        raise ValueError("completion awaiting admission blocks execution authorization")

    if _protocol_v8_e2_unreconciled_hazard_ids(state, qlek):
        raise ValueError("unreconciled semantic hazard blocks execution authorization")

    if qlek in state["imported_unarmed_selection_required"]:
        raise ValueError("post-merge unarmed trajectory selection is unresolved")

    unarmed = _protocol_v8_e2_active_unarmed_ids(state, qlek)
    if unarmed:
        if unarmed != [execution_id]:
            raise ValueError("existing unarmed trajectory must be resumed exactly")
        execution = state["executions"][execution_id]
        if execution.get("qlek") != qlek:
            raise ValueError("SemanticExecutionBinding cannot be retargeted")
        return execution

    existing = state["executions"].get(execution_id)
    if existing is not None:
        if existing.get("qlek") != qlek:
            raise ValueError("one Execution cannot bind to two QLEKs")
        raise ValueError("retired or armed Execution cannot be re-authorized as new")

    if outer_authorized is not True:
        raise ValueError("outer Execution authorization is required")

    replacements = _protocol_v8_e2_replacement_candidates(state, qlek)
    if len(replacements) > 1:
        raise ValueError("ambiguous cleared predecessor executions fail closed")

    if replacements:
        if (
            replacement_authorized is not True
            or replacement_of != replacements[0]
        ):
            raise ValueError(
                "hazard clearance does not itself authorize semantic replacement"
            )
    elif replacement_of is not None or replacement_authorized:
        raise ValueError("unexpected replacement authority without predecessor")

    execution = {
        "qlek": qlek,
        "armed": False,
        "arm_epoch": None,
        "arm_generation": None,
        "maybe_sent": False,
        "terminal_kind": None,
        "semantic_candidate": None,
        "completion_reconciled": False,
        "witness_reconciled": False,
        "hazard_clearance": None,
        "unresolvable": False,
        "superseded": False,
        "retired_unarmed": False,
        "replaced_by": None,
        "imported": False,
    }
    state["executions"][execution_id] = execution

    if replacements:
        state["executions"][replacements[0]]["replaced_by"] = execution_id

    return execution


def _protocol_v8_e2_t3_arm_execution(
    state: dict,
    qlek: str,
    generation: int,
    execution_id: str,
) -> dict:
    """Reference T3; normal Arm + SemanticArmBinding is one mutation."""
    qlek = _protocol_v8_e2_require_qlek(qlek)
    _protocol_v8_e2_current_handle(state, qlek, generation)

    execution = state["executions"].get(execution_id)
    if not isinstance(execution, dict) or execution.get("qlek") != qlek:
        raise ValueError("Arm requires the exact SemanticExecutionBinding")

    if execution.get("armed") is True:
        raise ValueError("semantic Execution may Arm at most once")

    if execution.get("retired_unarmed") is True:
        raise ValueError("retired unarmed Execution cannot Arm")

    if qlek in state["conflicts"]:
        raise ValueError("semantic conflict blocks Arm")

    if qlek in state["admissions"]:
        raise ValueError("Admission(K) blocks Arm")

    if _protocol_v8_e2_pending_completion_ids(state, qlek):
        raise ValueError("completion awaiting admission blocks Arm")

    if _protocol_v8_e2_unreconciled_hazard_ids(state, qlek):
        raise ValueError("unreconciled semantic hazard blocks Arm")

    if qlek in state["imported_unarmed_selection_required"]:
        raise ValueError("post-merge unarmed trajectory selection is unresolved")

    if _protocol_v8_e2_active_unarmed_ids(state, qlek) != [execution_id]:
        raise ValueError("Arm must target the one exact lawful unarmed trajectory")

    execution["armed"] = True
    execution["arm_epoch"] = state["coordination_epoch"]
    execution["arm_generation"] = generation

    # Safety after Arm is durable history, not continued live-handle possession.
    state["effective_authority"].pop(qlek, None)
    return execution


def _protocol_v8_e2_retire_unarmed(
    state: dict,
    execution_id: str,
) -> None:
    execution = state["executions"].get(execution_id)
    if not isinstance(execution, dict):
        raise ValueError("unknown semantic Execution")
    if execution.get("armed") is True:
        raise ValueError("Armed Execution cannot be retired as never-dispatched")
    execution["retired_unarmed"] = True


def _protocol_v8_e2_mark_maybe_sent(
    state: dict,
    execution_id: str,
) -> None:
    execution = state["executions"].get(execution_id)
    if not isinstance(execution, dict) or execution.get("armed") is not True:
        raise ValueError("MAYBE-SENT requires prior Semantic Arm")
    if execution.get("terminal_kind") is not None:
        raise ValueError("terminal semantic Execution cannot become MAYBE-SENT")
    execution["maybe_sent"] = True


def _protocol_v8_e2_record_protocol_valid_completion(
    state: dict,
    execution_id: str,
    semantic_candidate: object,
) -> None:
    execution = state["executions"].get(execution_id)
    if not isinstance(execution, dict) or execution.get("armed") is not True:
        raise ValueError("protocol-valid completion requires prior Semantic Arm")
    if execution.get("unresolvable") is True:
        raise ValueError("current-backend UNRESOLVABLE cannot later acquire completion")
    if execution.get("terminal_kind") is not None:
        raise ValueError("first protocol-valid completion is terminal")
    candidate_errors = _protocol_v8_e1_semantic_value_errors(
        semantic_candidate,
        "E2 semantic candidate",
    )
    if candidate_errors:
        raise ValueError(candidate_errors[0])
    execution["terminal_kind"] = "protocol-valid"
    execution["semantic_candidate"] = copy.deepcopy(semantic_candidate)


def _protocol_v8_e2_record_protocol_invalid_completion(
    state: dict,
    execution_id: str,
) -> None:
    execution = state["executions"].get(execution_id)
    if not isinstance(execution, dict) or execution.get("armed") is not True:
        raise ValueError("protocol-invalid completion requires prior Semantic Arm")
    if execution.get("unresolvable") is True:
        raise ValueError("current-backend UNRESOLVABLE cannot later acquire completion")
    if execution.get("terminal_kind") is not None:
        raise ValueError("semantic Execution already has terminal completion truth")
    execution["terminal_kind"] = "protocol-invalid"
    execution["hazard_clearance"] = "protocol-invalid-completion"


def _protocol_v8_e2_record_terminal_technical_failure(
    state: dict,
    execution_id: str,
) -> None:
    execution = state["executions"].get(execution_id)
    if not isinstance(execution, dict) or execution.get("armed") is not True:
        raise ValueError("terminal technical failure requires prior Semantic Arm")
    if execution.get("unresolvable") is True:
        raise ValueError("current-backend UNRESOLVABLE cannot later acquire completion")
    if execution.get("terminal_kind") is not None:
        raise ValueError("semantic Execution already has terminal completion truth")
    execution["terminal_kind"] = "technical-failure-no-completion"
    execution["hazard_clearance"] = "terminal-technical-failure-no-completion"


def _protocol_v8_e2_record_pne(
    state: dict,
    execution_id: str,
) -> None:
    execution = state["executions"].get(execution_id)
    if not isinstance(execution, dict) or execution.get("armed") is not True:
        raise ValueError("PROVEN-NOT-EXECUTED requires prior Semantic Arm")
    if execution.get("terminal_kind") == "protocol-valid":
        raise ValueError("PNE cannot erase a protocol-valid completion")
    if execution.get("unresolvable") is True:
        raise ValueError("current-backend UNRESOLVABLE cannot later become PNE")
    execution["hazard_clearance"] = "proven-not-executed"


def _protocol_v8_e2_record_unresolvable(
    state: dict,
    execution_id: str,
) -> None:
    execution = state["executions"].get(execution_id)
    if not isinstance(execution, dict) or execution.get("armed") is not True:
        raise ValueError("UNRESOLVABLE requires prior Semantic Arm")
    if execution.get("terminal_kind") is not None:
        raise ValueError("completed semantic Execution is not UNRESOLVABLE")
    execution["unresolvable"] = True


def _protocol_v8_e2_record_supersession(
    state: dict,
    execution_id: str,
) -> None:
    execution = state["executions"].get(execution_id)
    if not isinstance(execution, dict):
        raise ValueError("unknown semantic Execution")
    execution["superseded"] = True


def _protocol_v8_e2_internal_witness(
    execution_id: str,
    execution: dict,
    admission_id: str,
    candidate: object,
) -> dict:
    return {
        "execution_id": execution_id,
        "qlek": execution["qlek"],
        "semantic_candidate": copy.deepcopy(candidate),
        "admission_id": admission_id,
        "arm_generation": execution["arm_generation"],
        # Epoch is reference-machine coordination state only and is never serialized
        # into the public C6 origin-witness representation.
        "arm_epoch": execution["arm_epoch"],
    }


def _protocol_v8_e2_conflict_add(
    state: dict,
    qlek: str,
    admission_record: dict,
) -> None:
    conflict = state["conflicts"].setdefault(qlek, {})
    conflict[admission_record["admission_id"]] = copy.deepcopy(admission_record)
    state["admissions"].pop(qlek, None)


def _protocol_v8_e2_t4_reconcile_completion(
    state: dict,
    execution_id: str,
) -> dict:
    """Reference T4. First Admission + first witness is one atomic mutation."""
    execution = state["executions"].get(execution_id)
    if not isinstance(execution, dict):
        raise ValueError("unknown semantic Execution")
    if execution.get("armed") is not True:
        raise ValueError("completion reconciliation requires prior Semantic Arm")
    if execution.get("terminal_kind") != "protocol-valid":
        raise ValueError("no protocol-valid semantic completion to reconcile")

    qlek = execution["qlek"]
    candidate = copy.deepcopy(execution["semantic_candidate"])
    admission_id = _protocol_v8_e1_semantic_admission_id(qlek, candidate)
    witness = _protocol_v8_e2_internal_witness(
        execution_id,
        execution,
        admission_id,
        candidate,
    )
    incoming = {
        "qlek": qlek,
        "candidate": candidate,
        "admission_id": admission_id,
        "witnesses": [witness],
    }

    if qlek in state["conflicts"]:
        _protocol_v8_e2_conflict_add(state, qlek, incoming)
        status = "conflict"
    else:
        existing = state["admissions"].get(qlek)
        if existing is None:
            state["admissions"][qlek] = copy.deepcopy(incoming)
            status = "admitted"
        elif existing.get("candidate") == candidate:
            known = {
                item.get("execution_id")
                for item in existing.get("witnesses", [])
                if isinstance(item, dict)
            }
            if execution_id not in known:
                existing["witnesses"].append(copy.deepcopy(witness))
            status = "converged"
        else:
            _protocol_v8_e2_conflict_add(state, qlek, existing)
            _protocol_v8_e2_conflict_add(state, qlek, incoming)
            status = "conflict"

    execution["completion_reconciled"] = True
    execution["witness_reconciled"] = True
    return {
        "status": status,
        "qlek": qlek,
        "admission_id": admission_id,
    }


def _protocol_v8_e2_validated_witness_token(
    qlek: str,
    admission_id: str,
    candidate: object,
    origin_execution_id: str,
) -> dict:
    return {
        "_marker": _PROTOCOL_V8_E2_VALIDATED_WITNESS_MARKER,
        "qlek": qlek,
        "admission_id": admission_id,
        "semantic_candidate": copy.deepcopy(candidate),
        "origin_execution_id": origin_execution_id,
    }


def _protocol_v8_e2_require_validated_witness_token(
    token: object,
    qlek: str,
    candidate: object,
) -> dict:
    if not isinstance(token, dict):
        raise ValueError("imported Admission requires a validated origin witness")
    if token.get("_marker") is not _PROTOCOL_V8_E2_VALIDATED_WITNESS_MARKER:
        raise ValueError("imported Admission witness token is not checker-validated")
    if token.get("qlek") != qlek:
        raise ValueError("imported witness QLEK mismatch")
    expected_id = _protocol_v8_e1_semantic_admission_id(qlek, candidate)
    if token.get("admission_id") != expected_id:
        raise ValueError("imported witness SemanticAdmissionId mismatch")
    if token.get("semantic_candidate") != candidate:
        raise ValueError("imported witness candidate mismatch")
    return token


def _protocol_v8_e2_t5_reconcile_external_history(
    state: dict,
    qlek: str,
    *,
    semantic_candidate: object | None = None,
    validated_origin_witness: object | None = None,
    imported_armed: list[dict] | None = None,
    imported_unarmed: list[str] | None = None,
) -> dict:
    """Reference T5; no model inference and no post-merge trajectory selection."""
    qlek = _protocol_v8_e2_require_qlek(qlek)

    has_admission = semantic_candidate is not None
    if has_admission:
        candidate_errors = _protocol_v8_e1_semantic_value_errors(
            semantic_candidate,
            "imported semantic candidate",
        )
        if candidate_errors:
            raise ValueError(candidate_errors[0])
        token = _protocol_v8_e2_require_validated_witness_token(
            validated_origin_witness,
            qlek,
            semantic_candidate,
        )
    else:
        if validated_origin_witness is not None:
            raise ValueError("origin witness without imported Admission is invalid")
        token = None

    # Every pre-merge live authority becomes ineffective. Generation comparability
    # does not cross the reconciliation epoch.
    state["coordination_epoch"] += 1
    state["effective_authority"].clear()
    state["generation_high_water"] = {}

    for execution_id in imported_unarmed or []:
        if type(execution_id) is not str or not execution_id:
            raise ValueError("imported unarmed Execution identity must be non-empty")
        if execution_id in state["executions"]:
            raise ValueError("duplicate imported Execution identity")
        state["executions"][execution_id] = {
            "qlek": qlek,
            "armed": False,
            "arm_epoch": None,
            "arm_generation": None,
            "maybe_sent": False,
            "terminal_kind": None,
            "semantic_candidate": None,
            "completion_reconciled": False,
            "witness_reconciled": False,
            "hazard_clearance": None,
            "unresolvable": False,
            "superseded": False,
            "retired_unarmed": False,
            "replaced_by": None,
            "imported": True,
        }

    for item in imported_armed or []:
        if not isinstance(item, dict):
            raise ValueError("imported Armed execution must be an object")
        if set(item) != {"execution_id", "arm_generation"}:
            raise ValueError("imported Armed execution shape is invalid")
        execution_id = item.get("execution_id")
        generation = item.get("arm_generation")
        if type(execution_id) is not str or not execution_id:
            raise ValueError("imported Armed Execution identity must be non-empty")
        if type(generation) is not int:
            raise ValueError("imported arm_generation must be an exact integer")
        if execution_id in state["executions"]:
            raise ValueError("duplicate imported Execution identity")
        state["executions"][execution_id] = {
            "qlek": qlek,
            "armed": True,
            "arm_epoch": None,
            "arm_generation": generation,
            "maybe_sent": True,
            "terminal_kind": None,
            "semantic_candidate": None,
            "completion_reconciled": False,
            "witness_reconciled": False,
            "hazard_clearance": None,
            "unresolvable": False,
            "superseded": False,
            "retired_unarmed": False,
            "replaced_by": None,
            "imported": True,
        }

    if len(_protocol_v8_e2_active_unarmed_ids(state, qlek)) > 1:
        state["imported_unarmed_selection_required"].add(qlek)

    if not has_admission:
        return {
            "status": "history-merged",
            "qlek": qlek,
            "admission_id": None,
        }

    assert token is not None
    admission_id = _protocol_v8_e1_semantic_admission_id(
        qlek,
        semantic_candidate,
    )
    external_witness = {
        "execution_id": token["origin_execution_id"],
        "qlek": qlek,
        "semantic_candidate": copy.deepcopy(semantic_candidate),
        "admission_id": admission_id,
        "external_validated": True,
    }
    incoming = {
        "qlek": qlek,
        "candidate": copy.deepcopy(semantic_candidate),
        "admission_id": admission_id,
        "witnesses": [external_witness],
    }

    if qlek in state["conflicts"]:
        _protocol_v8_e2_conflict_add(state, qlek, incoming)
        status = "conflict"
    else:
        existing = state["admissions"].get(qlek)
        if existing is None:
            state["admissions"][qlek] = copy.deepcopy(incoming)
            status = "imported"
        elif existing.get("candidate") == semantic_candidate:
            known = {
                (
                    item.get("execution_id"),
                    item.get("admission_id"),
                )
                for item in existing.get("witnesses", [])
                if isinstance(item, dict)
            }
            witness_key = (
                external_witness["execution_id"],
                external_witness["admission_id"],
            )
            if witness_key not in known:
                existing["witnesses"].append(external_witness)
            status = "converged"
        else:
            _protocol_v8_e2_conflict_add(state, qlek, existing)
            _protocol_v8_e2_conflict_add(state, qlek, incoming)
            status = "conflict"

    return {
        "status": status,
        "qlek": qlek,
        "admission_id": admission_id,
    }


def _protocol_v8_e2_artifact_ref_errors(
    value: object,
    label: str,
) -> list[str]:
    if type(value) is not dict or set(value) != {"path", "sha256"}:
        return [f"{label}: ArtifactRef shape must be exactly path + sha256"]
    errors: list[str] = []
    path = value.get("path")
    digest = value.get("sha256")
    if type(path) is not str or not path:
        errors.append(f"{label}: ArtifactRef path must be non-empty")
    if (
        type(digest) is not str
        or re.fullmatch(r"[0-9a-f]{64}", digest) is None
    ):
        errors.append(f"{label}: ArtifactRef sha256 must be lowercase hex")
    return errors


def _protocol_v8_e2_binding_errors(
    contracts: dict[str, dict],
    binding: object,
    label: str,
) -> tuple[str | None, list[str]]:
    errors = _protocol_v8_e1_exact_keys(
        binding,
        {
            "semantic_question_binding_schema_version",
            "logical_question_descriptor",
            "qlek",
            "semantic_values",
        },
        label,
    )
    if errors:
        return None, errors
    assert isinstance(binding, dict)

    if binding.get("semantic_question_binding_schema_version") != "1.0":
        errors.append(f"{label}: schema version must be 1.0")

    descriptor = binding.get("logical_question_descriptor")
    recomputed, descriptor_errors = _protocol_v8_e1_recompute_structural_qlek(
        contracts,
        descriptor,
    )
    errors.extend(descriptor_errors)
    if recomputed is not None and binding.get("qlek") != recomputed:
        errors.append(f"{label}: qlek does not match exact descriptor")

    semantic_values = binding.get("semantic_values")
    if type(semantic_values) is not list:
        errors.append(f"{label}: semantic_values must be an array")
        return recomputed, errors

    resolved: list[tuple[str, str]] = []
    refs_by_id: dict[str, dict] = {}
    for index, item in enumerate(semantic_values):
        item_label = f"{label}.semantic_values[{index}]"
        item_errors = _protocol_v8_e1_exact_keys(
            item,
            {"ref", "value"},
            item_label,
        )
        errors.extend(item_errors)
        if item_errors or not isinstance(item, dict):
            continue

        ref = item.get("ref")
        value = item.get("value")
        if type(ref) is not dict or set(ref) != {"kind", "valueType", "valueId"}:
            errors.append(f"{item_label}: ref must be exact SemanticValueRefV1")
            continue
        if ref.get("kind") != "semantic-value":
            errors.append(f"{item_label}: ref.kind must be semantic-value")
            continue
        value_type = ref.get("valueType")
        value_id = ref.get("valueId")
        try:
            recomputed_id = _protocol_v8_e1_semantic_value_id(
                value_type,
                value,
            )
        except (TypeError, ValueError) as error:
            errors.append(f"{item_label}: {error}")
            continue
        if value_id != recomputed_id:
            errors.append(f"{item_label}: valueId does not match exact value")
        if value_id in refs_by_id:
            errors.append(f"{item_label}: duplicate semantic value preimage")
        refs_by_id[value_id] = ref
        resolved.append((value_type, value_id))

    if resolved != sorted(resolved):
        errors.append(
            f"{label}: semantic_values must be ordered by (valueType, valueId)"
        )

    direct_value_ids: set[str] = set()
    if isinstance(descriptor, dict):
        exact_input = _mapping(descriptor.get("exactLogicalInput"))
        for value in exact_input.values():
            if isinstance(value, dict) and value.get("kind") == "semantic-value":
                value_id = value.get("valueId")
                if isinstance(value_id, str):
                    direct_value_ids.add(value_id)

    missing_direct = sorted(direct_value_ids - set(refs_by_id))
    if missing_direct:
        errors.append(
            f"{label}: direct SemanticValueRef preimages are missing: {missing_direct!r}"
        )

    # E4 will close transitive semantic-value closure beyond these direct refs.
    return recomputed, errors


def _protocol_v8_e2_load_receipt_validator(
    root: Path,
    bundle: dict,
) -> tuple[Draft202012Validator | None, list[str]]:
    ref = _mapping(_mapping(bundle.get("schemas")).get("execution-receipt"))
    schema, errors = _load_json_object_artifact(
        root,
        ref,
        "inactive protocol v8 E2 execution receipt schema",
        REVIEW_SCHEMAS_PREFIX,
        REVIEW_JSON_OUTPUT_SUFFIX,
        require_canonical=False,
    )
    if schema is None:
        return None, errors
    validator, validator_errors = _validator(schema)
    errors.extend(
        f"inactive protocol v8 E2 execution receipt schema: {error}"
        for error in validator_errors
    )
    return validator, errors


def _protocol_v8_e2_question_realization_map(
    bundle: dict,
) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in _sequence(bundle.get("question_realizations")):
        if not isinstance(item, dict):
            continue
        contract_id = item.get("semantic_question_contract")
        if isinstance(contract_id, str):
            result[contract_id] = item
    return result


def _protocol_v8_e2_origin_witness_errors(
    root: Path,
    contracts: dict[str, dict],
    bundle: dict,
    witness: object,
    binding: object,
    receipt: object,
    *,
    binding_ref: dict,
    receipt_ref: dict,
    execution_bindings: dict[str, str],
    arm_bindings: dict[str, dict],
    parsed_outputs: dict[str, object],
) -> tuple[dict | None, list[str]]:
    """Cross-bind C6 witness to C3 history. E4 closes packet/value transitive projection."""
    label = "inactive protocol v8 E2 origin witness"
    errors = _protocol_v8_e1_exact_keys(
        witness,
        {
            "origin_witness_schema_version",
            "semantic_admission",
            "semantic_question_binding",
            "execution_receipt",
            "attempt_bindings",
            "origin_execution_id",
        },
        label,
    )
    if errors:
        return None, errors
    assert isinstance(witness, dict)

    if witness.get("origin_witness_schema_version") != "1.0":
        errors.append(f"{label}: schema version must be 1.0")

    errors.extend(
        _protocol_v8_e2_artifact_ref_errors(
            witness.get("semantic_question_binding"),
            f"{label}.semantic_question_binding",
        )
    )
    errors.extend(
        _protocol_v8_e2_artifact_ref_errors(
            witness.get("execution_receipt"),
            f"{label}.execution_receipt",
        )
    )
    if witness.get("semantic_question_binding") != binding_ref:
        errors.append(f"{label}: semantic_question_binding ArtifactRef mismatch")
    if witness.get("execution_receipt") != receipt_ref:
        errors.append(f"{label}: execution_receipt ArtifactRef mismatch")

    qlek, binding_errors = _protocol_v8_e2_binding_errors(
        contracts,
        binding,
        f"{label} binding",
    )
    errors.extend(binding_errors)

    admission = witness.get("semantic_admission")
    admission_errors = _protocol_v8_e1_exact_keys(
        admission,
        {"admission_id", "qlek", "semantic_candidate"},
        f"{label}.semantic_admission",
    )
    errors.extend(admission_errors)
    if admission_errors or not isinstance(admission, dict):
        return None, errors

    if qlek is not None and admission.get("qlek") != qlek:
        errors.append(f"{label}: Admission QLEK does not match binding QLEK")

    candidate = admission.get("semantic_candidate")
    candidate_errors = _protocol_v8_e1_semantic_value_errors(
        candidate,
        f"{label}.semantic_candidate",
    )
    errors.extend(candidate_errors)

    if qlek is not None and not candidate_errors:
        expected_admission_id = _protocol_v8_e1_semantic_admission_id(
            qlek,
            candidate,
        )
        if admission.get("admission_id") != expected_admission_id:
            errors.append(f"{label}: SemanticAdmissionId mismatch")
    else:
        expected_admission_id = None

    if not isinstance(receipt, dict):
        errors.append(f"{label}: receipt must be an object")
        return None, errors

    receipt_validator, receipt_validator_errors = (
        _protocol_v8_e2_load_receipt_validator(root, bundle)
    )
    errors.extend(receipt_validator_errors)
    if receipt_validator is not None:
        errors.extend(_schema_violations(receipt_validator, receipt, f"{label} receipt"))

    if receipt.get("protocol_bundle_sha256") != PROTOCOL_V8_BUNDLE_REFERENCE["sha256"]:
        errors.append(f"{label}: receipt protocol_bundle_sha256 must equal P8")

    descriptor = _mapping(_mapping(binding).get("logical_question_descriptor"))
    contract_id = descriptor.get("semanticQuestionContract")
    contract = contracts.get(contract_id) if isinstance(contract_id, str) else None
    if contract is None:
        errors.append(f"{label}: binding does not select an exact P8 SQC")
        return None, errors

    definition = _mapping(contract.get("definition"))
    expected_role = _mapping(definition.get("execution")).get("role")
    if receipt.get("role") != expected_role:
        errors.append(f"{label}: receipt role does not match selected SQC")

    realizations = _protocol_v8_e2_question_realization_map(bundle)
    realization = realizations.get(contract_id)
    if realization is None:
        errors.append(f"{label}: no P8 question realization for selected SQC")
    else:
        prompt_key = realization.get("prompt")
        expected_prompt = _mapping(_mapping(bundle.get("prompts")).get(prompt_key))
        if _mapping(receipt.get("input")).get("prompt") != expected_prompt:
            errors.append(f"{label}: receipt prompt does not match P8 realization")

    attempts = [
        item
        for item in _sequence(receipt.get("attempts"))
        if isinstance(item, dict)
    ]
    attempt_ids = [
        item.get("attempt_id")
        for item in attempts
        if isinstance(item.get("attempt_id"), str)
    ]
    if len(attempt_ids) != len(attempts) or len(attempt_ids) != len(set(attempt_ids)):
        errors.append(f"{label}: receipt attempt_id values must be unique strings")

    qualified = [
        item
        for item in attempts
        if item.get("outcome") == "qualified"
    ]
    qualifying = qualified[0] if len(qualified) == 1 else None
    if len(qualified) != 1:
        errors.append(f"{label}: receipt must contain exactly one qualified attempt")
    if qualifying is not None:
        if receipt.get("qualifying_attempt_id") != qualifying.get("attempt_id"):
            errors.append(f"{label}: qualifying_attempt_id mismatch")
        if attempts and attempts[-1] is not qualifying:
            errors.append(f"{label}: qualified attempt must be final")

    origin_execution_id = witness.get("origin_execution_id")
    if qualifying is not None and origin_execution_id != qualifying.get("attempt_id"):
        errors.append(
            f"{label}: origin_execution_id must equal receipt.qualifying_attempt_id"
        )

    attempt_bindings = witness.get("attempt_bindings")
    if type(attempt_bindings) is not list or not attempt_bindings:
        errors.append(f"{label}: attempt_bindings must be a non-empty array")
        bindings_by_execution: dict[str, dict] = {}
    else:
        bindings_by_execution = {}
        for index, item in enumerate(attempt_bindings):
            item_label = f"{label}.attempt_bindings[{index}]"
            item_errors = _protocol_v8_e1_exact_keys(
                item,
                {"execution_id", "qlek", "arm_generation"},
                item_label,
            )
            errors.extend(item_errors)
            if item_errors or not isinstance(item, dict):
                continue
            execution_id = item.get("execution_id")
            if type(execution_id) is not str or not execution_id:
                errors.append(f"{item_label}: execution_id must be non-empty")
                continue
            if execution_id in bindings_by_execution:
                errors.append(f"{item_label}: duplicate execution_id")
                continue
            if item.get("qlek") != qlek:
                errors.append(f"{item_label}: every receipt attempt must bind same QLEK")
            if type(item.get("arm_generation")) is not int:
                errors.append(f"{item_label}: arm_generation must be exact integer")
            bindings_by_execution[execution_id] = item

    if set(bindings_by_execution) != set(attempt_ids):
        errors.append(
            f"{label}: attempt_bindings must cover every receipt attempt exactly once"
        )

    for execution_id in attempt_ids:
        if execution_bindings.get(execution_id) != qlek:
            errors.append(
                f"{label}: authoritative SemanticExecutionBinding mismatch for "
                f"{execution_id!r}"
            )
        authoritative_arm = arm_bindings.get(execution_id)
        witness_arm = bindings_by_execution.get(execution_id)
        if not isinstance(authoritative_arm, dict):
            errors.append(
                f"{label}: missing authoritative SemanticArmBinding for "
                f"{execution_id!r}"
            )
            continue
        if (
            authoritative_arm.get("qlek") != qlek
            or not isinstance(witness_arm, dict)
            or witness_arm.get("qlek") != qlek
            or authoritative_arm.get("generation")
            != witness_arm.get("arm_generation")
        ):
            errors.append(
                f"{label}: witness Arm binding does not match authoritative history "
                f"for {execution_id!r}"
            )

    validators, validator_errors = _protocol_v8_e1_output_validators(root)
    errors.extend(validator_errors)
    if realization is not None:
        output_schema = realization.get("output_schema")
        output_validator = validators.get(output_schema)
    else:
        output_validator = None

    projected_qualifying = None
    for attempt in attempts:
        execution_id = attempt.get("attempt_id")
        outcome = attempt.get("outcome")

        if outcome == "technical-failure":
            if execution_id in parsed_outputs:
                errors.append(
                    f"{label}: technical-failure attempt must not have parsed output"
                )
            continue

        if execution_id not in parsed_outputs:
            errors.append(
                f"{label}: completed attempt {execution_id!r} lacks sealed parsed output"
            )
            continue

        if output_validator is None:
            errors.append(f"{label}: missing output validator for P8 realization")
            continue

        projected, projection_errors = _protocol_v8_e1_project_semantic_candidate(
            contract,
            parsed_outputs[execution_id],
            output_validator,
            f"{label} attempt {execution_id!r}",
        )

        if outcome == "protocol-invalid":
            if not projection_errors:
                errors.append(
                    f"{label}: protocol-invalid attempt is actually protocol-valid"
                )
        elif outcome == "qualified":
            if projection_errors:
                errors.extend(projection_errors)
            else:
                projected_qualifying = projected
        else:
            errors.append(f"{label}: unknown receipt attempt outcome {outcome!r}")

    if qualifying is not None and projected_qualifying != candidate:
        errors.append(
            f"{label}: qualifying raw output does not deterministically derive "
            "the admitted candidate"
        )

    if errors or qlek is None or expected_admission_id is None:
        return None, errors

    return (
        _protocol_v8_e2_validated_witness_token(
            qlek,
            expected_admission_id,
            candidate,
            origin_execution_id,
        ),
        [],
    )


def _protocol_v8_e2_expect_rejected(
    action,
    errors: list[str],
    label: str,
) -> None:
    try:
        action()
    except ValueError:
        return
    errors.append(f"inactive protocol v8 E2: expected rejection: {label}")


def _inactive_protocol_v8_e2_execution_admission_errors(root: Path) -> list[str]:
    """Exercise the exact C3 execution/admission reference machine."""
    errors: list[str] = []

    contracts, contract_errors = _protocol_v8_e1_contract_map(root)
    errors.extend(contract_errors)

    bundle, bundle_errors = _load_json_object_artifact(
        root,
        PROTOCOL_V8_BUNDLE_REFERENCE,
        "inactive protocol v8 E2 bundle",
        REVIEW_PROTOCOLS_PREFIX,
        REVIEW_PROTOCOL_BUNDLE_SUFFIX,
        require_canonical=True,
    )
    errors.extend(bundle_errors)
    if bundle is None:
        return errors

    finding_basis = {
        "schema": "turnlock.finding-adjudication-basis.v1",
        "semanticSubject": {
            "selector": "gate-a-assurance-decomposition-v1",
            "sha256": "0" * 64,
        },
        "currentProtocol": {
            "protocolId": "gate-a-campaign-protocol-v8",
            "bundleSha256": PROTOCOL_V8_BUNDLE_REFERENCE["sha256"],
        },
        "sourceFinding": {
            "reviewCampaignId": "REVIEW-E2",
            "findingId": "F-E2",
            "substantiveFindingSha256": "2" * 64,
        },
    }
    finding_basis_id = _protocol_v8_e1_semantic_value_id(
        "turnlock.semantic-value:FindingAdjudicationBasis@1",
        finding_basis,
    )
    descriptor = {
        "schema": "turnlock.logical-question-descriptor.v1",
        "semanticQuestionContract": "turnlock.sqc:MaterialityAssessmentInitial@1",
        "exactLogicalInput": {
            "findingAdjudicationBasis": {
                "kind": "semantic-value",
                "valueType": "turnlock.semantic-value:FindingAdjudicationBasis@1",
                "valueId": finding_basis_id,
            }
        },
    }
    qlek, qlek_errors = _protocol_v8_e1_recompute_structural_qlek(
        contracts,
        descriptor,
    )
    errors.extend(qlek_errors)
    if qlek is None:
        return errors

    candidate = {
        "authority_or_upstream_decision": True,
        "claim_structure": False,
        "normative_provenance": False,
        "modality_or_assurance_domain": False,
        "coverage_or_residual_assurance": False,
        "interaction_scope": False,
        "candidate_model_authorization": False,
        "rationale": "e2",
    }

    # No generation minimum; only strict monotonicity in one epoch.
    state = _protocol_v8_e2_new_state()
    first = _protocol_v8_e2_t1_acquire_authority(state, qlek, -7)
    if first.get("status") != "authority":
        errors.append("inactive protocol v8 E2: negative initial generation rejected")
    _protocol_v8_e2_t2_authorize_execution(
        state,
        qlek,
        -7,
        "E-STABLE",
        outer_authorized=True,
    )
    second = _protocol_v8_e2_t1_acquire_authority(state, qlek, 2)
    if second.get("execution_id") != "E-STABLE":
        errors.append("inactive protocol v8 E2: unarmed trajectory was not retained")
    _protocol_v8_e2_expect_rejected(
        lambda: _protocol_v8_e2_t3_arm_execution(
            state,
            qlek,
            -7,
            "E-STABLE",
        ),
        errors,
        "stale generation Arm",
    )
    _protocol_v8_e2_t3_arm_execution(
        state,
        qlek,
        2,
        "E-STABLE",
    )
    blocked = _protocol_v8_e2_t1_acquire_authority(state, qlek, 3)
    if blocked.get("status") != "blocked-hazard":
        errors.append("inactive protocol v8 E2: Armed execution did not block sibling sampling")

    _protocol_v8_e2_record_pne(state, "E-STABLE")
    third = _protocol_v8_e2_t1_acquire_authority(state, qlek, 3)
    if third.get("status") != "authority":
        errors.append("inactive protocol v8 E2: PNE did not permit fresh authority")
    _protocol_v8_e2_expect_rejected(
        lambda: _protocol_v8_e2_t2_authorize_execution(
            state,
            qlek,
            3,
            "E-REPLACEMENT",
            outer_authorized=True,
        ),
        errors,
        "PNE used as automatic replacement authority",
    )
    _protocol_v8_e2_t2_authorize_execution(
        state,
        qlek,
        3,
        "E-REPLACEMENT",
        outer_authorized=True,
        replacement_of="E-STABLE",
        replacement_authorized=True,
    )

    # UNRESOLVABLE and supersession do not clear hazard.
    unresolved = _protocol_v8_e2_new_state()
    _protocol_v8_e2_t1_acquire_authority(unresolved, qlek, 0)
    _protocol_v8_e2_t2_authorize_execution(
        unresolved,
        qlek,
        0,
        "E-UNRESOLVABLE",
        outer_authorized=True,
    )
    _protocol_v8_e2_t3_arm_execution(
        unresolved,
        qlek,
        0,
        "E-UNRESOLVABLE",
    )
    _protocol_v8_e2_mark_maybe_sent(unresolved, "E-UNRESOLVABLE")
    _protocol_v8_e2_record_unresolvable(unresolved, "E-UNRESOLVABLE")
    _protocol_v8_e2_record_supersession(unresolved, "E-UNRESOLVABLE")
    unresolved_result = _protocol_v8_e2_t1_acquire_authority(
        unresolved,
        qlek,
        1,
    )
    if unresolved_result.get("status") != "blocked-hazard":
        errors.append("inactive protocol v8 E2: UNRESOLVABLE/supersession cleared hazard")
    _protocol_v8_e2_expect_rejected(
        lambda: _protocol_v8_e2_record_protocol_valid_completion(
            unresolved,
            "E-UNRESOLVABLE",
            candidate,
        ),
        errors,
        "UNRESOLVABLE acquired magical later completion",
    )

    # Protocol-valid completion blocks new sampling and reconciles atomically.
    completed = _protocol_v8_e2_new_state()
    _protocol_v8_e2_t1_acquire_authority(completed, qlek, 11)
    _protocol_v8_e2_t2_authorize_execution(
        completed,
        qlek,
        11,
        "E-COMPLETE",
        outer_authorized=True,
    )
    _protocol_v8_e2_t3_arm_execution(
        completed,
        qlek,
        11,
        "E-COMPLETE",
    )
    _protocol_v8_e2_record_supersession(completed, "E-COMPLETE")
    _protocol_v8_e2_record_protocol_valid_completion(
        completed,
        "E-COMPLETE",
        candidate,
    )
    pending = _protocol_v8_e2_t1_acquire_authority(completed, qlek, 12)
    if pending.get("status") != "reconcile":
        errors.append("inactive protocol v8 E2: pending completion did not block sampling")
    result = _protocol_v8_e2_t4_reconcile_completion(
        completed,
        "E-COMPLETE",
    )
    if result.get("status") != "admitted":
        errors.append("inactive protocol v8 E2: first completion did not create Admission")
    admission = completed["admissions"].get(qlek)
    if not isinstance(admission, dict) or len(admission.get("witnesses", [])) != 1:
        errors.append("inactive protocol v8 E2: first Admission lacks atomic first witness")
    if not _protocol_v8_e2_consumable_admission(completed, qlek):
        errors.append("inactive protocol v8 E2: reconciled native Admission not consumable")
    reuse = _protocol_v8_e2_t1_acquire_authority(completed, qlek, 12)
    if reuse.get("status") != "reuse":
        errors.append("inactive protocol v8 E2: admitted QLEK did not reuse Admission")

    # Build exact C6 audit projections for a two-attempt receipt.
    materiality_contract = contracts.get(
        "turnlock.sqc:MaterialityAssessmentInitial@1"
    )
    validators, validator_errors = _protocol_v8_e1_output_validators(root)
    errors.extend(validator_errors)
    adjudication_validator = validators.get("adjudication-output")

    binding = {
        "semantic_question_binding_schema_version": "1.0",
        "logical_question_descriptor": descriptor,
        "qlek": qlek,
        "semantic_values": [
            {
                "ref": {
                    "kind": "semantic-value",
                    "valueType": "turnlock.semantic-value:FindingAdjudicationBasis@1",
                    "valueId": finding_basis_id,
                },
                "value": finding_basis,
            }
        ],
    }
    binding_ref = {
        "path": "__C7_E2_IN_MEMORY__/binding",
        "sha256": "3" * 64,
    }
    receipt_ref = {
        "path": "__C7_E2_IN_MEMORY__/receipt",
        "sha256": "4" * 64,
    }
    packet_ref = {
        "path": "__C7_E2_IN_MEMORY__/packet",
        "sha256": "5" * 64,
    }
    raw_ref = {
        "path": "__C7_E2_IN_MEMORY__/qualified-output",
        "sha256": "6" * 64,
    }
    qualified_output = {
        "adjudication_output_schema_version": "1.0",
        "task": "materiality-assessment",
        "result": candidate,
    }
    if adjudication_validator is not None and materiality_contract is not None:
        projected, projected_errors = _protocol_v8_e1_project_semantic_candidate(
            materiality_contract,
            qualified_output,
            adjudication_validator,
            "inactive protocol v8 E2 qualified output",
        )
        errors.extend(projected_errors)
        if projected != candidate:
            errors.append("inactive protocol v8 E2: sample candidate projection mismatch")

    receipt = {
        "receipt_schema_version": "4.0",
        "execution_id": "LOGICAL-E2",
        "role": "materiality-assessor",
        "reviewer_profile_id": "PROFILE-E2",
        "protocol_bundle_sha256": PROTOCOL_V8_BUNDLE_REFERENCE["sha256"],
        "input": {
            "prompt": _mapping(bundle.get("prompts")).get("adjudication"),
            "packet": packet_ref,
        },
        "isolated_context": True,
        "cross_reviewer_visibility_before_seal": False,
        "tools_enabled": False,
        "runtime": {
            "name": "e2-test-runtime",
            "version": "1",
        },
        "request": {
            "provider": "provider-a",
            "model": "model-a",
        },
        "attempts": [
            {
                "attempt_id": "ATTEMPT-E2-A",
                "call_id": "CALL-E2-A",
                "outcome": "technical-failure",
                "started_at": "t0",
                "ended_at": "t1",
                "provider_model": None,
                "provider_response_id": None,
                "termination": "technical",
                "transport_attempt_count": 1,
                "raw_output": None,
                "protocol_errors": [],
            },
            {
                "attempt_id": "ATTEMPT-E2-B",
                "call_id": "CALL-E2-B",
                "outcome": "qualified",
                "started_at": "t2",
                "ended_at": "t3",
                "provider_model": "model-a-v1",
                "provider_response_id": "response-e2",
                "termination": "complete",
                "transport_attempt_count": 1,
                "raw_output": raw_ref,
                "protocol_errors": [],
            },
        ],
        "qualifying_attempt_id": "ATTEMPT-E2-B",
        "resolved_identity": {
            "provider": "provider-a",
            "model": "model-a",
            "model_version": "model-a-v1",
            "resolution_kind": "provider-reported",
            "evidence_attempt_id": "ATTEMPT-E2-B",
        },
    }
    admission_id = _protocol_v8_e1_semantic_admission_id(qlek, candidate)
    witness = {
        "origin_witness_schema_version": "1.0",
        "semantic_admission": {
            "admission_id": admission_id,
            "qlek": qlek,
            "semantic_candidate": candidate,
        },
        "semantic_question_binding": binding_ref,
        "execution_receipt": receipt_ref,
        "attempt_bindings": [
            {
                "execution_id": "ATTEMPT-E2-A",
                "qlek": qlek,
                "arm_generation": -9,
            },
            {
                "execution_id": "ATTEMPT-E2-B",
                "qlek": qlek,
                "arm_generation": 4,
            },
        ],
        "origin_execution_id": "ATTEMPT-E2-B",
    }
    token, witness_errors = _protocol_v8_e2_origin_witness_errors(
        root,
        contracts,
        bundle,
        witness,
        binding,
        receipt,
        binding_ref=binding_ref,
        receipt_ref=receipt_ref,
        execution_bindings={
            "ATTEMPT-E2-A": qlek,
            "ATTEMPT-E2-B": qlek,
        },
        arm_bindings={
            "ATTEMPT-E2-A": {
                "qlek": qlek,
                "generation": -9,
            },
            "ATTEMPT-E2-B": {
                "qlek": qlek,
                "generation": 4,
            },
        },
        parsed_outputs={
            "ATTEMPT-E2-B": qualified_output,
        },
    )
    errors.extend(witness_errors)
    if token is None:
        errors.append("inactive protocol v8 E2: lawful origin witness was not validated")
        return errors

    wrong_qlek_witness = copy.deepcopy(witness)
    wrong_qlek_witness["attempt_bindings"][0]["qlek"] = (
        "qlek-sha256:" + "f" * 64
    )
    _token, wrong_qlek_errors = _protocol_v8_e2_origin_witness_errors(
        root,
        contracts,
        bundle,
        wrong_qlek_witness,
        binding,
        receipt,
        binding_ref=binding_ref,
        receipt_ref=receipt_ref,
        execution_bindings={
            "ATTEMPT-E2-A": qlek,
            "ATTEMPT-E2-B": qlek,
        },
        arm_bindings={
            "ATTEMPT-E2-A": {"qlek": qlek, "generation": -9},
            "ATTEMPT-E2-B": {"qlek": qlek, "generation": 4},
        },
        parsed_outputs={"ATTEMPT-E2-B": qualified_output},
    )
    if not wrong_qlek_errors:
        errors.append("inactive protocol v8 E2: retry attempt was allowed to switch QLEK")

    wrong_origin = copy.deepcopy(witness)
    wrong_origin["origin_execution_id"] = "ATTEMPT-E2-A"
    _token, wrong_origin_errors = _protocol_v8_e2_origin_witness_errors(
        root,
        contracts,
        bundle,
        wrong_origin,
        binding,
        receipt,
        binding_ref=binding_ref,
        receipt_ref=receipt_ref,
        execution_bindings={
            "ATTEMPT-E2-A": qlek,
            "ATTEMPT-E2-B": qlek,
        },
        arm_bindings={
            "ATTEMPT-E2-A": {"qlek": qlek, "generation": -9},
            "ATTEMPT-E2-B": {"qlek": qlek, "generation": 4},
        },
        parsed_outputs={"ATTEMPT-E2-B": qualified_output},
    )
    if not wrong_origin_errors:
        errors.append("inactive protocol v8 E2: non-qualifying origin_execution_id accepted")

    wrong_candidate = copy.deepcopy(witness)
    wrong_candidate["semantic_admission"]["semantic_candidate"]["rationale"] = "other"
    wrong_candidate["semantic_admission"]["admission_id"] = (
        _protocol_v8_e1_semantic_admission_id(
            qlek,
            wrong_candidate["semantic_admission"]["semantic_candidate"],
        )
    )
    _token, wrong_candidate_errors = _protocol_v8_e2_origin_witness_errors(
        root,
        contracts,
        bundle,
        wrong_candidate,
        binding,
        receipt,
        binding_ref=binding_ref,
        receipt_ref=receipt_ref,
        execution_bindings={
            "ATTEMPT-E2-A": qlek,
            "ATTEMPT-E2-B": qlek,
        },
        arm_bindings={
            "ATTEMPT-E2-A": {"qlek": qlek, "generation": -9},
            "ATTEMPT-E2-B": {"qlek": qlek, "generation": 4},
        },
        parsed_outputs={"ATTEMPT-E2-B": qualified_output},
    )
    if not wrong_candidate_errors:
        errors.append("inactive protocol v8 E2: witness candidate was trusted over raw output")

    # Bare imports are invalid; validated imports converge or conflict exactly.
    imported = _protocol_v8_e2_new_state()
    _protocol_v8_e2_expect_rejected(
        lambda: _protocol_v8_e2_t5_reconcile_external_history(
            imported,
            qlek,
            semantic_candidate=candidate,
            validated_origin_witness={},
        ),
        errors,
        "bare imported Admission without lawful witness",
    )
    first_import = _protocol_v8_e2_t5_reconcile_external_history(
        imported,
        qlek,
        semantic_candidate=candidate,
        validated_origin_witness=token,
    )
    if first_import.get("status") != "imported":
        errors.append("inactive protocol v8 E2: lawful imported Admission not established")

    # Same exact value converges with additional provenance.
    token_same = _protocol_v8_e2_validated_witness_token(
        qlek,
        admission_id,
        candidate,
        "ATTEMPT-E2-C",
    )
    same_import = _protocol_v8_e2_t5_reconcile_external_history(
        imported,
        qlek,
        semantic_candidate=candidate,
        validated_origin_witness=token_same,
    )
    if same_import.get("status") != "converged":
        errors.append("inactive protocol v8 E2: same K + same V did not converge")
    if len(imported["admissions"][qlek]["witnesses"]) != 2:
        errors.append("inactive protocol v8 E2: same-value provenance was not retained")

    # Different exact value conflicts and removes any automatic winner.
    candidate_two = copy.deepcopy(candidate)
    candidate_two["rationale"] = "different"
    token_two = _protocol_v8_e2_validated_witness_token(
        qlek,
        _protocol_v8_e1_semantic_admission_id(qlek, candidate_two),
        candidate_two,
        "ATTEMPT-E2-D",
    )
    conflict_result = _protocol_v8_e2_t5_reconcile_external_history(
        imported,
        qlek,
        semantic_candidate=candidate_two,
        validated_origin_witness=token_two,
    )
    if conflict_result.get("status") != "conflict":
        errors.append("inactive protocol v8 E2: same K + different V did not conflict")
    if qlek in imported["admissions"] or qlek not in imported["conflicts"]:
        errors.append("inactive protocol v8 E2: conflict retained an automatic winner")
    if _protocol_v8_e2_consumable_admission(imported, qlek):
        errors.append("inactive protocol v8 E2: conflicted Admission became consumable")
    if _protocol_v8_e2_t1_acquire_authority(imported, qlek, 0).get("status") != "conflict":
        errors.append("inactive protocol v8 E2: conflict did not block new authority")

    # Imported Admission is quarantined by unresolved pre-existing hazard.
    quarantined = _protocol_v8_e2_new_state()
    _protocol_v8_e2_t1_acquire_authority(quarantined, qlek, 8)
    _protocol_v8_e2_t2_authorize_execution(
        quarantined,
        qlek,
        8,
        "LOCAL-HAZARD",
        outer_authorized=True,
    )
    _protocol_v8_e2_t3_arm_execution(
        quarantined,
        qlek,
        8,
        "LOCAL-HAZARD",
    )
    _protocol_v8_e2_t5_reconcile_external_history(
        quarantined,
        qlek,
        semantic_candidate=candidate,
        validated_origin_witness=token,
    )
    if _protocol_v8_e2_consumable_admission(quarantined, qlek):
        errors.append("inactive protocol v8 E2: imported Admission ignored local hazard")
    _protocol_v8_e2_record_pne(quarantined, "LOCAL-HAZARD")
    if not _protocol_v8_e2_consumable_admission(quarantined, qlek):
        errors.append("inactive protocol v8 E2: cleared imported hazard kept Admission quarantined")

    # T5 invalidates every pre-merge live handle, even for another K.
    other_descriptor = copy.deepcopy(descriptor)
    other_descriptor["exactLogicalInput"]["findingAdjudicationBasis"]["valueId"] = (
        "semantic-value-sha256:" + "9" * 64
    )
    other_qlek, other_errors = _protocol_v8_e1_recompute_structural_qlek(
        contracts,
        other_descriptor,
    )
    errors.extend(other_errors)
    if other_qlek is not None:
        epoch_state = _protocol_v8_e2_new_state()
        _protocol_v8_e2_t1_acquire_authority(epoch_state, other_qlek, -3)
        _protocol_v8_e2_t2_authorize_execution(
            epoch_state,
            other_qlek,
            -3,
            "PREMERGE-E",
            outer_authorized=True,
        )
        _protocol_v8_e2_t5_reconcile_external_history(
            epoch_state,
            qlek,
            semantic_candidate=candidate,
            validated_origin_witness=token,
        )
        _protocol_v8_e2_expect_rejected(
            lambda: _protocol_v8_e2_t3_arm_execution(
                epoch_state,
                other_qlek,
                -3,
                "PREMERGE-E",
            ),
            errors,
            "pre-merge live authority remained effective",
        )

    # Multiple imported unarmed trajectories are not semantically selected in E2.
    unarmed_merge = _protocol_v8_e2_new_state()
    _protocol_v8_e2_t5_reconcile_external_history(
        unarmed_merge,
        qlek,
        imported_unarmed=["IMPORTED-U1", "IMPORTED-U2"],
    )
    if (
        _protocol_v8_e2_t1_acquire_authority(
            unarmed_merge,
            qlek,
            1,
        ).get("status")
        != "blocked-unarmed-selection"
    ):
        errors.append("inactive protocol v8 E2: imported unarmed ambiguity was not blocked")
    if qlek not in unarmed_merge["imported_unarmed_selection_required"]:
        errors.append("inactive protocol v8 E2: imported unarmed ambiguity was auto-selected")

    # Imported unresolved Armed trajectory keeps an otherwise valid Admission non-consumable.
    imported_hazard = _protocol_v8_e2_new_state()
    _protocol_v8_e2_t5_reconcile_external_history(
        imported_hazard,
        qlek,
        semantic_candidate=candidate,
        validated_origin_witness=token,
        imported_armed=[
            {
                "execution_id": "IMPORTED-ARMED",
                "arm_generation": -101,
            }
        ],
    )
    if _protocol_v8_e2_consumable_admission(imported_hazard, qlek):
        errors.append("inactive protocol v8 E2: unresolved imported Arm did not quarantine Admission")
    _protocol_v8_e2_record_unresolvable(imported_hazard, "IMPORTED-ARMED")
    if _protocol_v8_e2_consumable_admission(imported_hazard, qlek):
        errors.append("inactive protocol v8 E2: UNRESOLVABLE cleared imported hazard")

    imported_same = _protocol_v8_e2_new_state()
    _protocol_v8_e2_t5_reconcile_external_history(
        imported_same,
        qlek,
        semantic_candidate=candidate,
        validated_origin_witness=token,
        imported_armed=[
            {
                "execution_id": "IMPORTED-SAME",
                "arm_generation": -17,
            }
        ],
    )
    _protocol_v8_e2_record_protocol_valid_completion(
        imported_same,
        "IMPORTED-SAME",
        candidate,
    )
    same_reconcile = _protocol_v8_e2_t4_reconcile_completion(
        imported_same,
        "IMPORTED-SAME",
    )
    if same_reconcile.get("status") != "converged":
        errors.append("inactive protocol v8 E2: imported same-value hazard did not converge")
    if not _protocol_v8_e2_consumable_admission(imported_same, qlek):
        errors.append("inactive protocol v8 E2: reconciled same-value imported hazard remained quarantined")

    imported_different = _protocol_v8_e2_new_state()
    _protocol_v8_e2_t5_reconcile_external_history(
        imported_different,
        qlek,
        semantic_candidate=candidate,
        validated_origin_witness=token,
        imported_armed=[
            {
                "execution_id": "IMPORTED-DIFFERENT",
                "arm_generation": -19,
            }
        ],
    )
    _protocol_v8_e2_record_protocol_valid_completion(
        imported_different,
        "IMPORTED-DIFFERENT",
        candidate_two,
    )
    different_reconcile = _protocol_v8_e2_t4_reconcile_completion(
        imported_different,
        "IMPORTED-DIFFERENT",
    )
    if different_reconcile.get("status") != "conflict":
        errors.append("inactive protocol v8 E2: imported conflicting hazard did not conflict")
    if qlek in imported_different["admissions"]:
        errors.append("inactive protocol v8 E2: imported conflict retained automatic winner")

    return errors


def _protocol_v8_e3a_new_closure(
    e2_state: dict,
) -> dict:
    """Create disposable semantic identity/dependency closure state."""
    return {
        "e2_state": e2_state,
        "questions": {},
        "semantic_values": {},
        "exact_authorities": {},
        "qualification_descriptors": {},
        "fact_descriptors": {},
    }


def _protocol_v8_e3a_catalog_maps(
    root: Path,
) -> tuple[dict[str, dict], dict[str, dict], list[str]]:
    """Load exact catalog-owned Predicate and Qualification inventories."""
    errors: list[str] = []
    specifications = (
        (
            "PredicateRevision",
            PROTOCOL_V8_PREDICATE_CATALOG_REFERENCE,
            "predicates",
            13,
        ),
        (
            "QualificationContractRevision",
            PROTOCOL_V8_QUALIFICATION_CATALOG_REFERENCE,
            "qualifications",
            7,
        ),
    )
    maps: list[dict[str, dict]] = []
    for name, reference, field, expected_count in specifications:
        catalog, load_errors = _load_json_object_artifact(
            root,
            reference,
            f"inactive protocol v8 E3-A {name} catalog",
            REVIEW_CONTRACTS_PREFIX,
            REVIEW_JSON_OUTPUT_SUFFIX,
            require_canonical=True,
        )
        errors.extend(load_errors)
        entries = _sequence(_mapping(catalog).get(field))
        if len(entries) != expected_count:
            errors.append(
                f"inactive protocol v8 E3-A: expected exactly {expected_count} "
                f"{name} entries"
            )
        entry_map: dict[str, dict] = {}
        for index, entry in enumerate(entries):
            label = f"inactive protocol v8 E3-A {name} catalog {field}[{index}]"
            if not isinstance(entry, dict):
                errors.append(f"{label}: entry must be a mapping")
                continue
            revision_id = entry.get("revision_id")
            if not isinstance(revision_id, str):
                errors.append(f"{label}: revision_id must be a string")
                continue
            if revision_id in entry_map:
                errors.append(f"{label}: duplicate revision_id {revision_id!r}")
                continue
            entry_map[revision_id] = entry
        maps.append(entry_map)
    return maps[0], maps[1], errors


def _protocol_v8_e3a_register_preimage(
    index: dict,
    identity: object,
    preimage: object,
) -> None:
    """Retain every distinct canonical preimage; never choose a collision winner."""
    encoded = _protocol_v8_e1_canonical_json_value_bytes(preimage)
    preimages = index.setdefault(identity, [])
    for existing in preimages:
        if _protocol_v8_e1_canonical_json_value_bytes(existing) == encoded:
            return
    preimages.append(copy.deepcopy(preimage))


def _protocol_v8_e3a_unique_preimage(
    index: dict,
    identity: object,
    label: str,
) -> object:
    preimages = index.get(identity)
    if not isinstance(preimages, list) or not preimages:
        raise ValueError(f"{label}: dangling reference")
    canonical: dict[bytes, object] = {}
    for preimage in preimages:
        canonical.setdefault(
            _protocol_v8_e1_canonical_json_value_bytes(preimage),
            preimage,
        )
    if len(canonical) != 1:
        raise ValueError(f"{label}: IDENTITY-HASH-COLLISION")
    return copy.deepcopy(next(iter(canonical.values())))


def _protocol_v8_e3a_register_question(
    closure: dict,
    contracts: dict[str, dict],
    descriptor: object,
    *,
    claimed_qlek: str | None = None,
) -> str:
    qlek, errors = _protocol_v8_e1_recompute_structural_qlek(
        contracts,
        descriptor,
    )
    if errors or qlek is None:
        raise ValueError(errors[0] if errors else "invalid LogicalQuestionDescriptor")
    if claimed_qlek is not None and claimed_qlek != qlek:
        raise ValueError("claimed QLEK does not equal recomputed structural QLEK")
    _protocol_v8_e3a_register_preimage(
        closure["questions"],
        qlek,
        descriptor,
    )
    return qlek


def _protocol_v8_e3a_register_semantic_value(
    closure: dict,
    value_type: str,
    value: object,
    *,
    claimed_ref: object | None = None,
) -> dict:
    errors = _protocol_v8_e1_semantic_value_errors(
        value,
        "protocol-v8 E3-A SemanticValue",
    )
    if errors:
        raise ValueError(errors[0])
    value_id = _protocol_v8_e1_semantic_value_id(value_type, value)
    reference = {
        "kind": "semantic-value",
        "valueType": value_type,
        "valueId": value_id,
    }
    if claimed_ref is not None and claimed_ref != reference:
        raise ValueError("claimed SemanticValueRef does not match recomputed identity")
    _protocol_v8_e3a_register_preimage(
        closure["semantic_values"],
        value_id,
        {"valueType": value_type, "value": value},
    )
    return reference


def _protocol_v8_e3a_register_exact_authority(
    closure: dict,
    authority_ref: object,
) -> tuple[str, str]:
    errors = _protocol_v8_e1_exact_keys(
        authority_ref,
        {"kind", "authorityType", "authorityId"},
        "protocol-v8 E3-A ExactAuthorityRef",
    )
    if errors:
        raise ValueError(errors[0])
    assert isinstance(authority_ref, dict)
    authority_type = authority_ref.get("authorityType")
    authority_id = authority_ref.get("authorityId")
    if authority_ref.get("kind") != "exact-authority":
        raise ValueError("ExactAuthorityRef kind must be exact-authority")
    if not isinstance(authority_type, str) or not authority_type:
        raise ValueError("ExactAuthorityRef authorityType must be non-empty")
    if not isinstance(authority_id, str) or not authority_id:
        raise ValueError("ExactAuthorityRef authorityId must be non-empty")
    key = (authority_type, authority_id)
    closure["exact_authorities"][key] = copy.deepcopy(authority_ref)
    return key


def _protocol_v8_e3a_admission_index(
    closure: dict,
) -> dict[str, list[dict]]:
    """Build an identity index over effective and conflicted E2 Admissions."""
    index: dict[str, list[dict]] = {}
    state = closure["e2_state"]
    records: list[tuple[object, object]] = list(state["admissions"].items())
    for qlek, branches in state["conflicts"].items():
        if not isinstance(branches, dict):
            raise ValueError("E2 conflict branches must be a mapping")
        records.extend((qlek, record) for record in branches.values())
    for qlek, record in records:
        qlek = _protocol_v8_e2_require_qlek(qlek)
        if not isinstance(record, dict):
            raise ValueError("E2 Admission record must be a mapping")
        candidate = record.get("candidate")
        candidate_errors = _protocol_v8_e1_semantic_value_errors(
            candidate,
            "protocol-v8 E3-A Admission candidate",
        )
        if candidate_errors:
            raise ValueError(candidate_errors[0])
        admission_id = _protocol_v8_e1_semantic_admission_id(qlek, candidate)
        if record.get("admission_id") != admission_id:
            raise ValueError("SemanticAdmissionId mismatch in E2 reference state")
        _protocol_v8_e3a_register_preimage(
            index,
            admission_id,
            {
                "qlek": qlek,
                "candidate": candidate,
                "admission_id": admission_id,
            },
        )
    return index


def _protocol_v8_e3a_qualification_descriptor_errors(
    qualification_catalog: dict[str, dict],
    descriptor: object,
    label: str,
) -> list[str]:
    errors = _protocol_v8_e1_semantic_value_errors(descriptor, label)
    if errors:
        return errors
    errors.extend(
        _protocol_v8_e1_exact_keys(
            descriptor,
            {
                "schema",
                "qualificationContract",
                "anchorAdmission",
                "additionalInputs",
            },
            label,
        )
    )
    if errors:
        return errors
    assert isinstance(descriptor, dict)
    if descriptor.get("schema") != "turnlock.qualification-key-descriptor.v1":
        errors.append(f"{label}: invalid QualificationKeyDescriptorV1 schema")
    contract_id = descriptor.get("qualificationContract")
    contract = qualification_catalog.get(contract_id)
    if contract is None:
        errors.append(f"{label}: unknown QualificationContractRevisionId")
        return errors
    errors.extend(
        _protocol_v8_e1_ref_errors(
            descriptor.get("anchorAdmission"),
            {"kind": "semantic-admission"},
            f"{label}.anchorAdmission",
        )
    )
    additional = descriptor.get("additionalInputs")
    if not isinstance(additional, dict):
        errors.append(f"{label}: additionalInputs must be an object")
        return errors
    cases = _sequence(_mapping(contract.get("definition")).get("cases"))
    key_sets: dict[frozenset[str], list[dict]] = {}
    for case in cases:
        if not isinstance(case, dict):
            errors.append(f"{label}: qualification catalog case must be a mapping")
            continue
        declared = case.get("additional_inputs")
        if not isinstance(declared, dict):
            errors.append(f"{label}: qualification case additional_inputs must be an object")
            continue
        key_sets.setdefault(frozenset(declared), []).append(case)
    if any(len(declarations) != 1 for declarations in key_sets.values()):
        errors.append(f"{label}: catalog integrity failure: duplicate additional-input key set")
        return errors
    matches = key_sets.get(frozenset(additional), [])
    if not matches:
        errors.append(f"{label}: additionalInputs key set matches no catalog case")
        return errors
    declared = _mapping(matches[0].get("additional_inputs"))
    for name in sorted(declared, key=lambda item: item.encode("utf-8")):
        input_descriptor = declared[name]
        if not isinstance(input_descriptor, dict):
            errors.append(f"{label}.{name}: invalid catalog input descriptor")
            continue
        errors.extend(
            _protocol_v8_e1_ref_errors(
                additional.get(name),
                input_descriptor,
                f"{label}.additionalInputs.{name}",
            )
        )
    return errors


def _protocol_v8_e3a_register_qualification_descriptor(
    closure: dict,
    qualification_catalog: dict[str, dict],
    descriptor: object,
    *,
    claimed_ref: object | None = None,
) -> dict:
    errors = _protocol_v8_e3a_qualification_descriptor_errors(
        qualification_catalog,
        descriptor,
        "protocol-v8 E3-A QualificationKeyDescriptor",
    )
    if errors:
        raise ValueError(errors[0])
    assert isinstance(descriptor, dict)
    qualification_key = _protocol_v8_e1_qualification_key(descriptor)
    reference = {
        "kind": "qualification-key",
        "qualificationContract": descriptor["qualificationContract"],
        "qualificationKey": qualification_key,
    }
    if claimed_ref is not None and claimed_ref != reference:
        raise ValueError("claimed QualificationKeyRef does not match recomputed identity")
    _protocol_v8_e3a_register_preimage(
        closure["qualification_descriptors"],
        qualification_key,
        descriptor,
    )
    return reference


def _protocol_v8_e3a_fact_descriptor_errors(
    predicate_catalog: dict[str, dict],
    descriptor: object,
    label: str,
) -> list[str]:
    errors = _protocol_v8_e1_semantic_value_errors(descriptor, label)
    if errors:
        return errors
    errors.extend(
        _protocol_v8_e1_exact_keys(
            descriptor,
            {"schema", "predicateRevision", "arguments"},
            label,
        )
    )
    if errors:
        return errors
    assert isinstance(descriptor, dict)
    if descriptor.get("schema") != "turnlock.semantic-fact-descriptor.v1":
        errors.append(f"{label}: invalid SemanticFactDescriptorV1 schema")
    predicate_id = descriptor.get("predicateRevision")
    predicate = predicate_catalog.get(predicate_id)
    if predicate is None:
        errors.append(f"{label}: unknown PredicateRevisionId")
        return errors
    arguments = descriptor.get("arguments")
    if not isinstance(arguments, dict):
        errors.append(f"{label}: arguments must be an object")
        return errors
    declarations = _mapping(_mapping(predicate.get("definition")).get("arguments"))
    if set(arguments) != set(declarations):
        errors.append(f"{label}: argument keys must equal the exact Predicate catalog keys")
        return errors
    for name in sorted(declarations, key=lambda item: item.encode("utf-8")):
        declaration = declarations[name]
        value = arguments.get(name)
        argument_label = f"{label}.arguments.{name}"
        if not isinstance(declaration, dict):
            errors.append(f"{argument_label}: invalid catalog argument descriptor")
            continue
        kind = declaration.get("kind")
        if kind == "qualification-key":
            argument_errors = _protocol_v8_e1_exact_keys(
                value,
                {"kind", "qualificationContract", "qualificationKey"},
                argument_label,
            )
            if argument_errors:
                errors.extend(argument_errors)
                continue
            assert isinstance(value, dict)
            if value.get("kind") != "qualification-key":
                errors.append(f"{argument_label}: kind must be qualification-key")
            if value.get("qualificationContract") != declaration.get("qualification_contract"):
                errors.append(f"{argument_label}: QualificationContract mismatch")
            key = value.get("qualificationKey")
            if type(key) is not str or _PROTOCOL_V8_E1_QUALIFICATION_KEY.fullmatch(key) is None:
                errors.append(f"{argument_label}: invalid QualificationKey")
        elif kind in {
            "semantic-value",
            "semantic-admission",
            "semantic-fact",
            "exact-authority",
        }:
            errors.extend(
                _protocol_v8_e1_ref_errors(
                    value,
                    declaration,
                    argument_label,
                )
            )
        elif kind == "canonical-value":
            errors.extend(
                _protocol_v8_e1_semantic_value_errors(value, argument_label)
            )
        else:
            errors.append(f"{argument_label}: unsupported catalog argument kind {kind!r}")
    return errors


def _protocol_v8_e3a_register_fact_descriptor(
    closure: dict,
    predicate_catalog: dict[str, dict],
    descriptor: object,
    *,
    claimed_ref: object | None = None,
) -> dict:
    errors = _protocol_v8_e3a_fact_descriptor_errors(
        predicate_catalog,
        descriptor,
        "protocol-v8 E3-A SemanticFactDescriptor",
    )
    if errors:
        raise ValueError(errors[0])
    assert isinstance(descriptor, dict)
    fact_id = _protocol_v8_e1_fact_id(descriptor)
    reference = {
        "kind": "semantic-fact",
        "predicateRevision": descriptor["predicateRevision"],
        "factId": fact_id,
    }
    if claimed_ref is not None and claimed_ref != reference:
        raise ValueError("claimed SemanticFactRef does not match recomputed identity")
    _protocol_v8_e3a_register_preimage(
        closure["fact_descriptors"],
        fact_id,
        descriptor,
    )
    return reference


def _protocol_v8_e3a_resolve_semantic_value(
    closure: dict,
    reference: object,
) -> dict:
    errors = _protocol_v8_e1_exact_keys(
        reference,
        {"kind", "valueType", "valueId"},
        "protocol-v8 E3-A SemanticValueRef",
    )
    if errors:
        raise ValueError(errors[0])
    assert isinstance(reference, dict)
    if reference.get("kind") != "semantic-value":
        raise ValueError("SemanticValueRef kind mismatch")
    value_id = reference.get("valueId")
    if type(value_id) is not str or _PROTOCOL_V8_E1_SEMANTIC_VALUE_ID.fullmatch(value_id) is None:
        raise ValueError("invalid SemanticValueId")
    preimage = _protocol_v8_e3a_unique_preimage(
        closure["semantic_values"], value_id, "dangling semantic-value ref"
    )
    assert isinstance(preimage, dict)
    if preimage.get("valueType") != reference.get("valueType"):
        raise ValueError("SemanticValueRef valueType mismatch")
    if _protocol_v8_e1_semantic_value_id(preimage["valueType"], preimage.get("value")) != value_id:
        raise ValueError("SemanticValueId/preimage mismatch")
    return preimage


def _protocol_v8_e3a_resolve_admission_identity(
    closure: dict,
    reference: object,
) -> dict:
    errors = _protocol_v8_e1_exact_keys(
        reference,
        {"kind", "admissionId"},
        "protocol-v8 E3-A SemanticAdmissionRef",
    )
    if errors:
        raise ValueError(errors[0])
    assert isinstance(reference, dict)
    admission_id = reference.get("admissionId")
    if reference.get("kind") != "semantic-admission":
        raise ValueError("SemanticAdmissionRef kind mismatch")
    if type(admission_id) is not str or _PROTOCOL_V8_E1_ADMISSION_ID.fullmatch(admission_id) is None:
        raise ValueError("invalid SemanticAdmissionId")
    preimage = _protocol_v8_e3a_unique_preimage(
        _protocol_v8_e3a_admission_index(closure),
        admission_id,
        "dangling semantic-admission ref",
    )
    assert isinstance(preimage, dict)
    if _protocol_v8_e1_semantic_admission_id(preimage["qlek"], preimage.get("candidate")) != admission_id:
        raise ValueError("SemanticAdmissionId/preimage mismatch")
    return preimage


def _protocol_v8_e3a_resolve_qualification_identity(
    closure: dict,
    reference: object,
) -> dict:
    errors = _protocol_v8_e1_exact_keys(
        reference,
        {"kind", "qualificationContract", "qualificationKey"},
        "protocol-v8 E3-A QualificationKeyRef",
    )
    if errors:
        raise ValueError(errors[0])
    assert isinstance(reference, dict)
    key = reference.get("qualificationKey")
    if reference.get("kind") != "qualification-key":
        raise ValueError("QualificationKeyRef kind mismatch")
    if type(key) is not str or _PROTOCOL_V8_E1_QUALIFICATION_KEY.fullmatch(key) is None:
        raise ValueError("invalid QualificationKey")
    descriptor = _protocol_v8_e3a_unique_preimage(
        closure["qualification_descriptors"], key, "dangling qualification-key ref"
    )
    assert isinstance(descriptor, dict)
    if descriptor.get("qualificationContract") != reference.get("qualificationContract"):
        raise ValueError("QualificationKeyRef QualificationContract mismatch")
    if _protocol_v8_e1_qualification_key(descriptor) != key:
        raise ValueError("QualificationKey/descriptor mismatch")
    return descriptor


def _protocol_v8_e3a_resolve_fact_identity(
    closure: dict,
    reference: object,
) -> dict:
    errors = _protocol_v8_e1_exact_keys(
        reference,
        {"kind", "predicateRevision", "factId"},
        "protocol-v8 E3-A SemanticFactRef",
    )
    if errors:
        raise ValueError(errors[0])
    assert isinstance(reference, dict)
    fact_id = reference.get("factId")
    if reference.get("kind") != "semantic-fact":
        raise ValueError("SemanticFactRef kind mismatch")
    if type(fact_id) is not str or _PROTOCOL_V8_E1_FACT_ID.fullmatch(fact_id) is None:
        raise ValueError("invalid FactId")
    descriptor = _protocol_v8_e3a_unique_preimage(
        closure["fact_descriptors"], fact_id, "dangling FactRef"
    )
    assert isinstance(descriptor, dict)
    if descriptor.get("predicateRevision") != reference.get("predicateRevision"):
        raise ValueError("FactRef predicate mismatch")
    if _protocol_v8_e1_fact_id(descriptor) != fact_id:
        raise ValueError("FactId/descriptor mismatch")
    return descriptor


def _protocol_v8_e3a_resolve_exact_authority(
    closure: dict,
    reference: object,
) -> dict:
    errors = _protocol_v8_e1_exact_keys(
        reference,
        {"kind", "authorityType", "authorityId"},
        "protocol-v8 E3-A ExactAuthorityRef",
    )
    if errors:
        raise ValueError(errors[0])
    assert isinstance(reference, dict)
    if reference.get("kind") != "exact-authority":
        raise ValueError("ExactAuthorityRef kind mismatch")
    key = (reference.get("authorityType"), reference.get("authorityId"))
    registered = closure["exact_authorities"].get(key)
    if registered != reference:
        raise ValueError("ExactAuthorityRef not explicitly registered")
    return copy.deepcopy(registered)


def _protocol_v8_e3a_resolve_qlek(
    closure: dict,
    contracts: dict[str, dict],
    qlek: object,
) -> dict:
    qlek = _protocol_v8_e2_require_qlek(qlek)
    descriptor = _protocol_v8_e3a_unique_preimage(
        closure["questions"], qlek, "QLEK with no exact descriptor preimage"
    )
    recomputed, errors = _protocol_v8_e1_recompute_structural_qlek(
        contracts,
        descriptor,
    )
    if errors or recomputed != qlek:
        raise ValueError(errors[0] if errors else "QLEK/descriptor mismatch")
    assert isinstance(descriptor, dict)
    return descriptor


def _protocol_v8_e3a_admission_consumable(
    closure: dict,
    admission_ref: object,
) -> bool:
    admission = _protocol_v8_e3a_resolve_admission_identity(
        closure,
        admission_ref,
    )
    qlek = admission["qlek"]
    effective = closure["e2_state"]["admissions"].get(qlek)
    if not isinstance(effective, dict):
        return False
    if effective.get("admission_id") != admission.get("admission_id"):
        return False
    return _protocol_v8_e2_consumable_admission(
        closure["e2_state"],
        qlek,
    )


def _protocol_v8_e3a_extract_references(
    value: object,
) -> list[dict]:
    if isinstance(value, dict):
        shapes = {
            "semantic-value": {"kind", "valueType", "valueId"},
            "semantic-admission": {"kind", "admissionId"},
            "semantic-fact": {"kind", "predicateRevision", "factId"},
            "qualification-key": {"kind", "qualificationContract", "qualificationKey"},
            "exact-authority": {"kind", "authorityType", "authorityId"},
        }
        kind = value.get("kind")
        if kind in shapes and set(value) == shapes[kind]:
            return [copy.deepcopy(value)]
        result: list[dict] = []
        for key in sorted(value, key=lambda item: item.encode("utf-8")):
            result.extend(_protocol_v8_e3a_extract_references(value[key]))
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(_protocol_v8_e3a_extract_references(item))
        return result
    return []


def _protocol_v8_e3a_reference_node(
    closure: dict,
    reference: dict,
) -> tuple:
    kind = reference["kind"]
    if kind == "semantic-value":
        _protocol_v8_e3a_resolve_semantic_value(closure, reference)
        return ("semantic-value", reference["valueId"])
    if kind == "semantic-admission":
        _protocol_v8_e3a_resolve_admission_identity(closure, reference)
        return ("semantic-admission", reference["admissionId"])
    if kind == "qualification-key":
        _protocol_v8_e3a_resolve_qualification_identity(closure, reference)
        return ("qualification-key", reference["qualificationKey"])
    if kind == "semantic-fact":
        _protocol_v8_e3a_resolve_fact_identity(closure, reference)
        return ("semantic-fact", reference["factId"])
    if kind == "exact-authority":
        _protocol_v8_e3a_resolve_exact_authority(closure, reference)
        return (
            "exact-authority",
            reference["authorityType"],
            reference["authorityId"],
        )
    raise ValueError(f"unsupported semantic reference kind {kind!r}")


def _protocol_v8_e3a_node_dependencies(
    closure: dict,
    contracts: dict[str, dict],
    node: tuple,
) -> list[tuple]:
    kind = node[0]
    if kind == "semantic-value":
        preimage = _protocol_v8_e3a_resolve_semantic_value(
            closure,
            {
                "kind": "semantic-value",
                "valueType": _protocol_v8_e3a_unique_preimage(
                    closure["semantic_values"], node[1], "semantic-value"
                )["valueType"],
                "valueId": node[1],
            },
        )
        references = _protocol_v8_e3a_extract_references(preimage["value"])
    elif kind == "qlek":
        descriptor = _protocol_v8_e3a_resolve_qlek(closure, contracts, node[1])
        references = _protocol_v8_e3a_extract_references(
            descriptor["exactLogicalInput"]
        )
    elif kind == "semantic-admission":
        admission = _protocol_v8_e3a_resolve_admission_identity(
            closure,
            {"kind": "semantic-admission", "admissionId": node[1]},
        )
        return [("qlek", admission["qlek"])]
    elif kind == "qualification-key":
        descriptor = _protocol_v8_e3a_resolve_qualification_identity(
            closure,
            {
                "kind": "qualification-key",
                "qualificationContract": _protocol_v8_e3a_unique_preimage(
                    closure["qualification_descriptors"], node[1], "qualification-key"
                )["qualificationContract"],
                "qualificationKey": node[1],
            },
        )
        references = _protocol_v8_e3a_extract_references(
            descriptor["anchorAdmission"]
        ) + _protocol_v8_e3a_extract_references(descriptor["additionalInputs"])
    elif kind == "semantic-fact":
        descriptor = _protocol_v8_e3a_resolve_fact_identity(
            closure,
            {
                "kind": "semantic-fact",
                "predicateRevision": _protocol_v8_e3a_unique_preimage(
                    closure["fact_descriptors"], node[1], "semantic-fact"
                )["predicateRevision"],
                "factId": node[1],
            },
        )
        references = _protocol_v8_e3a_extract_references(descriptor["arguments"])
    elif kind == "exact-authority":
        _protocol_v8_e3a_resolve_exact_authority(
            closure,
            {
                "kind": "exact-authority",
                "authorityType": node[1],
                "authorityId": node[2],
            },
        )
        return []
    else:
        raise ValueError(f"unsupported semantic dependency node {node!r}")
    return [
        _protocol_v8_e3a_reference_node(closure, reference)
        for reference in references
    ]


def _protocol_v8_e3a_resolve_dependency_graph(
    closure: dict,
    contracts: dict[str, dict],
    roots: list[tuple],
    dependency_function=None,
) -> set[tuple]:
    active: set[tuple] = set()
    resolved: set[tuple] = set()
    dependencies = dependency_function or (
        lambda node: _protocol_v8_e3a_node_dependencies(closure, contracts, node)
    )

    def visit(node: tuple) -> None:
        if node in active:
            raise ValueError(f"unlawful semantic dependency cycle at {node!r}")
        if node in resolved:
            return
        active.add(node)
        try:
            for dependency in dependencies(node):
                visit(dependency)
        finally:
            active.remove(node)
        resolved.add(node)

    for root in roots:
        visit(root)
    return resolved


def _protocol_v8_e3a_expect_rejected(
    action,
    errors: list[str],
    label: str,
    required_text: str | None = None,
) -> None:
    try:
        action()
    except ValueError as error:
        if required_text is not None and required_text not in str(error):
            errors.append(
                f"inactive protocol v8 E3-A: {label} rejected without {required_text!r}"
            )
        return
    errors.append(f"inactive protocol v8 E3-A: expected rejection: {label}")


def _inactive_protocol_v8_e3a_semantic_closure_errors(
    root: Path,
) -> list[str]:
    """Exercise identity/preimage resolution without establishing Fact truth."""
    errors: list[str] = []
    predicates, qualifications, catalog_errors = _protocol_v8_e3a_catalog_maps(root)
    errors.extend(catalog_errors)
    contracts, contract_errors = _protocol_v8_e1_contract_map(root)
    errors.extend(contract_errors)
    if errors:
        return errors

    state = _protocol_v8_e2_new_state()
    closure = _protocol_v8_e3a_new_closure(state)
    finding_basis = {
        "schema": "turnlock.finding-adjudication-basis.v1",
        "semanticSubject": {
            "selector": "gate-a-assurance-decomposition-v1",
            "sha256": "0" * 64,
        },
        "currentProtocol": {
            "protocolId": "gate-a-campaign-protocol-v8",
            "bundleSha256": PROTOCOL_V8_BUNDLE_REFERENCE["sha256"],
        },
        "sourceFinding": {
            "reviewCampaignId": "REVIEW-E3-A",
            "findingId": "F-E3-A",
            "substantiveFindingSha256": "3" * 64,
        },
    }
    finding_ref = _protocol_v8_e3a_register_semantic_value(
        closure,
        "turnlock.semantic-value:FindingAdjudicationBasis@1",
        finding_basis,
    )
    question = {
        "schema": "turnlock.logical-question-descriptor.v1",
        "semanticQuestionContract": "turnlock.sqc:MaterialityAssessmentInitial@1",
        "exactLogicalInput": {"findingAdjudicationBasis": finding_ref},
    }
    qlek = _protocol_v8_e3a_register_question(closure, contracts, question)
    candidate = {
        "authority_or_upstream_decision": True,
        "claim_structure": False,
        "normative_provenance": False,
        "modality_or_assurance_domain": False,
        "coverage_or_residual_assurance": False,
        "interaction_scope": False,
        "candidate_model_authorization": False,
        "rationale": "e3-a identity chain only",
    }
    _protocol_v8_e2_t1_acquire_authority(state, qlek, -3)
    _protocol_v8_e2_t2_authorize_execution(
        state, qlek, -3, "E-E3-A", outer_authorized=True
    )
    _protocol_v8_e2_t3_arm_execution(state, qlek, -3, "E-E3-A")
    _protocol_v8_e2_record_protocol_valid_completion(state, "E-E3-A", candidate)
    admission_result = _protocol_v8_e2_t4_reconcile_completion(state, "E-E3-A")
    admission_ref = {
        "kind": "semantic-admission",
        "admissionId": admission_result["admission_id"],
    }
    if not _protocol_v8_e3a_admission_consumable(closure, admission_ref):
        errors.append("inactive protocol v8 E3-A: sample Admission is not consumable")

    qualification_descriptor = {
        "schema": "turnlock.qualification-key-descriptor.v1",
        "qualificationContract": "turnlock.qualification:MaterialityAssessmentQualification@1",
        "anchorAdmission": admission_ref,
        "additionalInputs": {},
    }
    qualification_ref = _protocol_v8_e3a_register_qualification_descriptor(
        closure,
        qualifications,
        qualification_descriptor,
    )
    fact_descriptor = {
        "schema": "turnlock.semantic-fact-descriptor.v1",
        "predicateRevision": "turnlock.predicate:QualifiedPositiveMateriality@1",
        "arguments": {"qualification": qualification_ref},
    }
    fact_ref = _protocol_v8_e3a_register_fact_descriptor(
        closure,
        predicates,
        fact_descriptor,
    )
    resolved = _protocol_v8_e3a_resolve_dependency_graph(
        closure,
        contracts,
        [("semantic-fact", fact_ref["factId"])],
    )
    expected = {
        ("semantic-fact", fact_ref["factId"]),
        ("qualification-key", qualification_ref["qualificationKey"]),
        ("semantic-admission", admission_ref["admissionId"]),
        ("qlek", qlek),
        ("semantic-value", finding_ref["valueId"]),
    }
    if resolved != expected:
        errors.append("inactive protocol v8 E3-A: acyclic identity closure mismatch")

    dangling_fact = {
        "kind": "semantic-fact",
        "predicateRevision": fact_ref["predicateRevision"],
        "factId": "semantic-fact-sha256:" + "a" * 64,
    }
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_resolve_fact_identity(closure, dangling_fact),
        errors,
        "dangling FactRef",
    )
    wrong_predicate = dict(fact_ref)
    wrong_predicate["predicateRevision"] = "turnlock.predicate:QualifiedNonMateriality@1"
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_resolve_fact_identity(closure, wrong_predicate),
        errors,
        "FactRef predicate mismatch",
    )
    forged_fact = dict(fact_ref)
    forged_fact["factId"] = "semantic-fact-sha256:" + "b" * 64
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_register_fact_descriptor(
            closure, predicates, fact_descriptor, claimed_ref=forged_fact
        ),
        errors,
        "forged FactId",
    )
    wrong_qualification = copy.deepcopy(fact_descriptor)
    wrong_qualification["arguments"]["qualification"]["qualificationContract"] = (
        "turnlock.qualification:RefutationQualification@1"
    )
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_register_fact_descriptor(
            closure, predicates, wrong_qualification
        ),
        errors,
        "wrong QualificationContract",
    )
    dangling_qualification = dict(qualification_ref)
    dangling_qualification["qualificationKey"] = "qualification-key-sha256:" + "c" * 64
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_resolve_qualification_identity(
            closure, dangling_qualification
        ),
        errors,
        "dangling QualificationKeyRef",
    )

    _protocol_v8_e3a_register_fact_descriptor(closure, predicates, fact_descriptor)
    _protocol_v8_e3a_register_qualification_descriptor(
        closure, qualifications, qualification_descriptor
    )
    if len(closure["fact_descriptors"][fact_ref["factId"]]) != 1:
        errors.append("inactive protocol v8 E3-A: duplicate Fact preimage was not idempotent")
    if len(closure["qualification_descriptors"][qualification_ref["qualificationKey"]]) != 1:
        errors.append("inactive protocol v8 E3-A: duplicate Qualification preimage was not idempotent")

    collision_id = "semantic-fact-sha256:" + "d" * 64
    collision_ref = {
        "kind": "semantic-fact",
        "predicateRevision": fact_ref["predicateRevision"],
        "factId": collision_id,
    }
    closure["fact_descriptors"][collision_id] = [
        fact_descriptor,
        {
            **fact_descriptor,
            "arguments": {"qualification": dangling_qualification},
        },
    ]
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_resolve_fact_identity(closure, collision_ref),
        errors,
        "synthetic Fact identity collision",
        "IDENTITY-HASH-COLLISION",
    )

    qualification_collision = "qualification-key-sha256:" + "e" * 64
    qualification_collision_ref = {
        "kind": "qualification-key",
        "qualificationContract": qualification_ref["qualificationContract"],
        "qualificationKey": qualification_collision,
    }
    closure["qualification_descriptors"][qualification_collision] = [
        qualification_descriptor,
        {**qualification_descriptor, "additionalInputs": {"x": admission_ref}},
    ]
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_resolve_qualification_identity(
            closure, qualification_collision_ref
        ),
        errors,
        "synthetic Qualification identity collision",
        "IDENTITY-HASH-COLLISION",
    )

    node_a = ("exact-authority", "synthetic", "A")
    node_b = ("exact-authority", "synthetic", "B")
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_resolve_dependency_graph(
            closure,
            contracts,
            [node_a],
            lambda node: [node_b] if node == node_a else [node_a],
        ),
        errors,
        "exact-node dependency cycle",
        "unlawful semantic dependency cycle",
    )

    conflict_state = _protocol_v8_e2_new_state()
    conflict_closure = _protocol_v8_e3a_new_closure(conflict_state)
    candidate_two = {**candidate, "claim_structure": True}
    first_id = _protocol_v8_e1_semantic_admission_id(qlek, candidate)
    second_id = _protocol_v8_e1_semantic_admission_id(qlek, candidate_two)
    first_token = _protocol_v8_e2_validated_witness_token(
        qlek, first_id, candidate, "IMPORTED-E3-A-1"
    )
    second_token = _protocol_v8_e2_validated_witness_token(
        qlek, second_id, candidate_two, "IMPORTED-E3-A-2"
    )
    _protocol_v8_e2_t5_reconcile_external_history(
        conflict_state,
        qlek,
        semantic_candidate=candidate,
        validated_origin_witness=first_token,
    )
    _protocol_v8_e2_t5_reconcile_external_history(
        conflict_state,
        qlek,
        semantic_candidate=candidate_two,
        validated_origin_witness=second_token,
    )
    for admission_id in (first_id, second_id):
        branch_ref = {"kind": "semantic-admission", "admissionId": admission_id}
        try:
            _protocol_v8_e3a_resolve_admission_identity(conflict_closure, branch_ref)
        except ValueError as error:
            errors.append(f"inactive protocol v8 E3-A: conflict branch did not resolve: {error}")
        if _protocol_v8_e3a_admission_consumable(conflict_closure, branch_ref):
            errors.append("inactive protocol v8 E3-A: conflict branch became consumable")

    provenance_one = _protocol_v8_e3a_register_fact_descriptor(
        closure, predicates, fact_descriptor
    )
    provenance_two = _protocol_v8_e3a_register_fact_descriptor(
        closure, predicates, copy.deepcopy(fact_descriptor)
    )
    if provenance_one["factId"] != provenance_two["factId"]:
        errors.append("inactive protocol v8 E3-A: provenance changed Fact identity")

    value_type_mismatch = dict(finding_ref)
    value_type_mismatch["valueType"] = "turnlock.semantic-value:SurvivingMaterialBasis@1"
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_resolve_semantic_value(closure, value_type_mismatch),
        errors,
        "SemanticValueRef valueType mismatch",
    )
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_resolve_qlek(
            closure, contracts, "qlek-sha256:" + "f" * 64
        ),
        errors,
        "dangling QLEK",
    )
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_resolve_exact_authority(
            closure,
            {
                "kind": "exact-authority",
                "authorityType": "candidate-revision",
                "authorityId": "UNREGISTERED",
            },
        ),
        errors,
        "unregistered ExactAuthorityRef",
    )

    malformed_state = _protocol_v8_e2_new_state()
    malformed_state["admissions"][qlek] = {
        "qlek": qlek,
        "candidate": candidate,
        "admission_id": "semantic-admission-sha256:" + "0" * 64,
        "witnesses": [{}],
    }
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_admission_index(
            _protocol_v8_e3a_new_closure(malformed_state)
        ),
        errors,
        "SemanticAdmissionId mismatch",
    )
    return errors


def _protocol_v8_e3b_case_map(
    qualification_catalog: dict[str, dict],
) -> tuple[dict[str, dict], list[str]]:
    """Derive the complete qualification-case dispatch inventory from C4."""
    errors: list[str] = []
    cases: dict[str, dict] = {}
    total = 0
    for qualification_id, qualification in qualification_catalog.items():
        definition = _mapping(qualification.get("definition"))
        for index, case in enumerate(_sequence(definition.get("cases"))):
            total += 1
            label = f"inactive protocol v8 E3-B {qualification_id} cases[{index}]"
            if not isinstance(case, dict):
                errors.append(f"{label}: case must be a mapping")
                continue
            case_id = case.get("case_id")
            predicate_id = case.get("derives_predicate")
            additional = case.get("additional_inputs")
            if not isinstance(case_id, str) or not case_id:
                errors.append(f"{label}: case_id must be a non-empty string")
                continue
            if not isinstance(predicate_id, str) or not predicate_id:
                errors.append(f"{label}: derives_predicate must be non-empty")
            if not isinstance(additional, dict):
                errors.append(f"{label}: additional_inputs must be an object")
            if case_id in cases:
                errors.append(f"{label}: duplicate case_id {case_id!r}")
                continue
            cases[case_id] = {
                "qualification_contract": qualification_id,
                "case": case,
                "qualification": qualification,
            }
    if total != 8:
        errors.append("inactive protocol v8 E3-B: expected exactly 8 qualification cases")
    if any(not isinstance(item, str) or not item for item in qualification_catalog):
        errors.append("inactive protocol v8 E3-B: invalid Qualification revision_id")
    return cases, errors


def _protocol_v8_e3b_case_for_descriptor(
    qualification_catalog: dict[str, dict],
    descriptor: dict,
) -> dict:
    """Select one catalog case solely by its exact additional-input key set."""
    contract_id = descriptor.get("qualificationContract")
    qualification = qualification_catalog.get(contract_id)
    if not isinstance(qualification, dict):
        raise ValueError("unknown QualificationContractRevisionId")
    additional = descriptor.get("additionalInputs")
    if not isinstance(additional, dict):
        raise ValueError("QualificationKey additionalInputs must be an object")
    matches = [
        case
        for case in _sequence(_mapping(qualification.get("definition")).get("cases"))
        if isinstance(case, dict)
        and isinstance(case.get("additional_inputs"), dict)
        and set(case["additional_inputs"]) == set(additional)
    ]
    if not matches:
        raise ValueError("qualification case integrity failure: no exact case match")
    if len(matches) != 1:
        raise ValueError("qualification catalog integrity failure: ambiguous case match")
    return {
        "qualification_contract": contract_id,
        "case": matches[0],
        "qualification": qualification,
    }


def _protocol_v8_e3b_admission_context(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    admission_ref: object,
    validators: dict[str, Draft202012Validator],
) -> dict:
    """Resolve and independently revalidate one exact producer Admission."""
    reference_errors = _protocol_v8_e1_ref_errors(
        admission_ref,
        {"kind": "semantic-admission"},
        "protocol-v8 E3-B SemanticAdmissionRef",
    )
    if reference_errors:
        raise ValueError(reference_errors[0])
    assert isinstance(admission_ref, dict)
    admission_id = admission_ref["admissionId"]
    cache = closure.setdefault("_e3b_admission_contexts", {})
    cached = cache.get(admission_id)
    if isinstance(cached, dict):
        context = copy.deepcopy(cached)
    else:
        record = _protocol_v8_e3a_resolve_admission_identity(closure, admission_ref)
        qlek = record.get("qlek")
        descriptor = _protocol_v8_e3a_resolve_qlek(closure, contracts, qlek)
        contract_id = descriptor.get("semanticQuestionContract")
        contract = contracts.get(contract_id)
        if not isinstance(contract, dict):
            raise ValueError("Admission QLEK references unknown SemanticQuestionContract")
        definition = _mapping(contract.get("definition"))
        candidate = record.get("candidate")
        if definition.get("question_kind") == "challenge":
            if not isinstance(candidate, dict) or set(candidate) != {
                "objective_assessments",
                "objections",
            }:
                raise ValueError("challenge Admission candidate has invalid exact key set")
            challenge_kind = _mapping(definition.get("challenge")).get("challenge_kind")
            output = {
                "challenge_output_schema_version": "1.0",
                "challenge_kind": challenge_kind,
                "objective_assessments": copy.deepcopy(candidate["objective_assessments"]),
                "objections": copy.deepcopy(candidate["objections"]),
            }
            validator = validators.get("challenge-output")
        else:
            task = _mapping(definition.get("execution")).get("task")
            output = {
                "adjudication_output_schema_version": "1.0",
                "task": task,
                "result": copy.deepcopy(candidate),
            }
            validator = validators.get("adjudication-output")
        if validator is None:
            raise ValueError("exact P8 output validator is unavailable")
        projected, projection_errors = _protocol_v8_e1_project_semantic_candidate(
            contract,
            output,
            validator,
            "inactive protocol v8 E3-B Admission candidate",
        )
        if projection_errors:
            raise ValueError(projection_errors[0])
        if projected != candidate:
            raise ValueError("Admission candidate differs from exact E1 projection")
        context = {
            "reference": copy.deepcopy(admission_ref),
            "record": record,
            "qlek": qlek,
            "descriptor": descriptor,
            "contract_id": contract_id,
            "contract": contract,
            "candidate": copy.deepcopy(candidate),
        }
        # The cache is a disposable validated-preimage optimization. Current
        # consumability is deliberately recomputed from mutable C3 history below.
        cache[admission_id] = copy.deepcopy(context)
    effective = closure["e2_state"]["admissions"].get(context["qlek"])
    context["currently_consumable"] = (
        isinstance(effective, dict)
        and effective.get("admission_id") == admission_id
        and _protocol_v8_e2_consumable_admission(
            closure["e2_state"], context["qlek"]
        )
    )
    return context


def _protocol_v8_e3b_fact_dependency(
    closure: dict,
    fact_ref: object,
    fact_dependency_resolver,
) -> dict:
    """Resolve a claimed predecessor Fact through the staged E3-C boundary."""
    if fact_dependency_resolver is None:
        raise ValueError("E3-C fact dependency resolver required")
    result = fact_dependency_resolver(copy.deepcopy(fact_ref))
    if not isinstance(result, dict) or set(result) != {
        "reference",
        "descriptor",
        "reconstructible",
        "consumable",
    }:
        raise ValueError("Fact dependency resolver returned invalid exact result shape")
    if result.get("reference") != fact_ref:
        raise ValueError("Fact dependency resolver returned mismatched reference")
    resolved = _protocol_v8_e3a_resolve_fact_identity(closure, fact_ref)
    if result.get("descriptor") != resolved:
        raise ValueError("Fact dependency resolver returned mismatched descriptor")
    if result.get("reconstructible") is not True:
        raise ValueError("claimed Fact dependency is not reconstructible")
    if type(result.get("consumable")) is not bool:
        raise ValueError("Fact dependency consumable must be an exact bool")
    return copy.deepcopy(result)


def _protocol_v8_e3b_producer_admission_of_fact(
    fact_ref: object,
    fact_dependency_resolver,
) -> dict:
    """Implement the two published C4 producerAdmission(F) projections."""
    if fact_dependency_resolver is None:
        raise ValueError("E3-C fact dependency resolver required")
    resolved = fact_dependency_resolver(copy.deepcopy(fact_ref))
    if not isinstance(resolved, dict) or set(resolved) != {
        "reference",
        "descriptor",
        "reconstructible",
        "consumable",
    }:
        raise ValueError("Fact dependency resolver returned invalid exact result shape")
    if resolved.get("reference") != fact_ref:
        raise ValueError("Fact dependency resolver returned mismatched reference")
    if resolved.get("reconstructible") is not True:
        raise ValueError("claimed Fact dependency is not reconstructible")
    if type(resolved.get("consumable")) is not bool:
        raise ValueError("Fact dependency consumable must be an exact bool")
    descriptor = resolved.get("descriptor")
    if not isinstance(descriptor, dict):
        raise ValueError("Fact dependency descriptor is invalid")
    predicate = descriptor.get("predicateRevision")
    arguments = _mapping(descriptor.get("arguments"))
    if predicate == "turnlock.predicate:TargetedDiscoveryStatement@1":
        producer = arguments.get("producerDiscovery")
    elif predicate == "turnlock.predicate:DecisionRequiredDiscoveryStatement@1":
        targeted_ref = arguments.get("targetedDiscoveryStatement")
        targeted = fact_dependency_resolver(copy.deepcopy(targeted_ref))
        if not isinstance(targeted, dict) or set(targeted) != {
            "reference",
            "descriptor",
            "reconstructible",
            "consumable",
        }:
            raise ValueError("Fact dependency resolver returned invalid exact result shape")
        if targeted.get("reference") != targeted_ref:
            raise ValueError("Fact dependency resolver returned mismatched reference")
        if targeted.get("reconstructible") is not True:
            raise ValueError("claimed Fact dependency is not reconstructible")
        if type(targeted.get("consumable")) is not bool:
            raise ValueError("Fact dependency consumable must be an exact bool")
        targeted_descriptor = targeted.get("descriptor")
        if (
            not isinstance(targeted_descriptor, dict)
            or targeted_descriptor.get("predicateRevision")
            != "turnlock.predicate:TargetedDiscoveryStatement@1"
        ):
            raise ValueError("DecisionRequiredDiscoveryStatement has invalid target")
        producer = _mapping(targeted_descriptor.get("arguments")).get(
            "producerDiscovery"
        )
    else:
        raise ValueError("unsupported published C4 producer-admission-of-fact contract")
    reference_errors = _protocol_v8_e1_ref_errors(
        producer,
        {"kind": "semantic-admission"},
        "protocol-v8 E3-B producerAdmission(F)",
    )
    if reference_errors:
        raise ValueError(reference_errors[0])
    return copy.deepcopy(producer)


def _protocol_v8_e3b_materiality_axes(
    contracts: dict[str, dict],
    anchor_context: dict,
) -> list[str]:
    """Derive materiality axes from the unique C1 challenge contract."""
    anchor_family = _mapping(anchor_context["contract"].get("definition")).get(
        "family"
    )
    matches: list[dict] = []
    for contract in contracts.values():
        definition = _mapping(contract.get("definition"))
        if definition.get("question_kind") != "challenge":
            continue
        if definition.get("family") != anchor_family:
            continue
        challenge = _mapping(definition.get("challenge"))
        target_name = challenge.get("target_input")
        target = _mapping(_mapping(definition.get("logical_input")).get(target_name))
        if anchor_context["contract_id"] in _sequence(target.get("producer_contracts")):
            matches.append(contract)
    if len(matches) != 1:
        raise ValueError("materiality challenge contract must resolve exactly once")
    objectives = _sequence(
        _mapping(_mapping(matches[0].get("definition")).get("challenge")).get(
            "objectives"
        )
    )
    if (
        len(objectives) != 7
        or any(not isinstance(item, str) or not item for item in objectives)
        or len(set(objectives)) != len(objectives)
    ):
        raise ValueError("materiality challenge objectives are invalid")
    return list(objectives)


def _protocol_v8_e3b_challenge_result(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    qualification_descriptor: dict,
    qualification_case: dict,
    anchor_context: dict,
    target_ref: object,
    validators: dict[str, Draft202012Validator],
    require_current_consumability: bool,
) -> bool:
    """Return whether the exact required challenge closes with zero objections."""
    declarations = _mapping(qualification_case.get("additional_inputs"))
    challenge_inputs = [
        (name, declaration)
        for name, declaration in declarations.items()
        if isinstance(declaration, dict)
        and declaration.get("kind") == "semantic-admission"
    ]
    if len(challenge_inputs) != 1:
        raise ValueError("challenge qualification case must declare exactly one challenge")
    name, declaration = challenge_inputs[0]
    challenge_ref = _mapping(qualification_descriptor.get("additionalInputs")).get(name)
    challenge_context = _protocol_v8_e3b_admission_context(
        root, closure, contracts, challenge_ref, validators
    )
    if challenge_context["contract_id"] not in _sequence(
        declaration.get("producer_contracts")
    ):
        return False
    definition = _mapping(challenge_context["contract"].get("definition"))
    if definition.get("question_kind") != "challenge":
        raise ValueError("challenge producer is not a challenge contract")
    challenge = _mapping(definition.get("challenge"))
    target_name = challenge.get("target_input")
    logical_input = _mapping(definition.get("logical_input"))
    expected: dict[str, object] = {}
    qualification_inputs = _mapping(qualification_descriptor.get("additionalInputs"))
    for input_name in logical_input:
        if input_name == target_name:
            expected[input_name] = copy.deepcopy(target_ref)
        elif input_name in qualification_inputs:
            expected[input_name] = copy.deepcopy(qualification_inputs[input_name])
        else:
            return False
    if _mapping(challenge_context["descriptor"]).get("exactLogicalInput") != expected:
        return False
    if require_current_consumability and not challenge_context["currently_consumable"]:
        return False
    return _mapping(challenge_context["candidate"]).get("objections") == []


def _protocol_v8_e3b_case_positive_materiality(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    descriptor: dict,
    case: dict,
    anchor: dict,
    validators: dict[str, Draft202012Validator],
    dependency,
    require_current_consumability: bool,
) -> bool:
    axes = _protocol_v8_e3b_materiality_axes(contracts, anchor)
    return any(anchor["candidate"].get(axis) is True for axis in axes)


def _protocol_v8_e3b_case_qualified_non_materiality(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    descriptor: dict,
    case: dict,
    anchor: dict,
    validators: dict[str, Draft202012Validator],
    dependency,
    require_current_consumability: bool,
) -> bool:
    axes = _protocol_v8_e3b_materiality_axes(contracts, anchor)
    if any(anchor["candidate"].get(axis) is not False for axis in axes):
        return False
    return _protocol_v8_e3b_challenge_result(
        root,
        closure,
        contracts,
        descriptor,
        case,
        anchor,
        descriptor["anchorAdmission"],
        validators,
        require_current_consumability,
    )


def _protocol_v8_e3b_case_qualified_refutation(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    descriptor: dict,
    case: dict,
    anchor: dict,
    validators: dict[str, Draft202012Validator],
    dependency,
    require_current_consumability: bool,
) -> bool:
    if anchor["candidate"] == {"kind": "not-established"}:
        return False
    return _protocol_v8_e3b_challenge_result(
        root, closure, contracts, descriptor, case, anchor,
        descriptor["anchorAdmission"], validators, require_current_consumability
    )


def _protocol_v8_e3b_case_qualified_no_normative_impact(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    descriptor: dict,
    case: dict,
    anchor: dict,
    validators: dict[str, Draft202012Validator],
    dependency,
    require_current_consumability: bool,
) -> bool:
    targeted_ref = descriptor["additionalInputs"]["targetedDiscoveryStatement"]
    targeted = dependency(targeted_ref)
    if require_current_consumability and not targeted["consumable"]:
        return False
    targeted_descriptor = targeted["descriptor"]
    if targeted_descriptor.get("predicateRevision") != (
        "turnlock.predicate:TargetedDiscoveryStatement@1"
    ):
        return False
    arguments = _mapping(targeted_descriptor.get("arguments"))
    statement = _mapping(arguments.get("statement"))
    if statement.get("semantic_disposition") != "no-normative-impact":
        return False
    if descriptor["anchorAdmission"] != arguments.get("producerDiscovery"):
        return False
    return _protocol_v8_e3b_challenge_result(
        root, closure, contracts, descriptor, case, anchor,
        targeted_ref, validators, require_current_consumability
    )


def _protocol_v8_e3b_case_qualified_decision_necessity(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    descriptor: dict,
    case: dict,
    anchor: dict,
    validators: dict[str, Draft202012Validator],
    dependency,
    require_current_consumability: bool,
) -> bool:
    inputs = descriptor["additionalInputs"]
    s_ref = inputs["survivingMaterialBasis"]
    d_ref = inputs["decisionRequiredStatement"]
    u_ref = inputs["uniqueCorrectionExhaustion"]
    n_ref = inputs["decisionNecessityCandidate"]
    d_result = dependency(d_ref)
    u_result = dependency(u_ref)
    n_result = dependency(n_ref)
    if require_current_consumability and not all(
        result["consumable"] for result in (d_result, u_result, n_result)
    ):
        return False
    if d_result["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:DecisionRequiredDiscoveryStatement@1"
    ):
        return False
    if u_result["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:UniqueCorrectionExhaustion@1"
    ):
        return False
    if n_result["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:DecisionNecessityCandidate@1"
    ):
        return False
    t_ref = _mapping(d_result["descriptor"].get("arguments")).get(
        "targetedDiscoveryStatement"
    )
    t_result = dependency(t_ref)
    if require_current_consumability and not t_result["consumable"]:
        return False
    if t_result["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:TargetedDiscoveryStatement@1"
    ):
        return False
    t_arguments = _mapping(t_result["descriptor"].get("arguments"))
    if descriptor["anchorAdmission"] != t_arguments.get("producerDiscovery"):
        return False
    if _mapping(anchor["descriptor"].get("exactLogicalInput")).get(
        "survivingMaterialBasis"
    ) != s_ref:
        return False
    if _mapping(u_result["descriptor"].get("arguments")).get(
        "targetedDiscoveryStatement"
    ) != t_ref:
        return False
    if _mapping(n_result["descriptor"].get("arguments")) != {
        "survivingMaterialBasis": s_ref,
        "decisionRequiredStatement": d_ref,
        "uniqueCorrectionExhaustion": u_ref,
    }:
        return False
    return _protocol_v8_e3b_challenge_result(
        root, closure, contracts, descriptor, case, anchor,
        n_ref, validators, require_current_consumability
    )


def _protocol_v8_e3b_case_accepted_unique_correction(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    descriptor: dict,
    case: dict,
    anchor: dict,
    validators: dict[str, Draft202012Validator],
    dependency,
    require_current_consumability: bool,
) -> bool:
    if anchor["candidate"] == {"kind": "not-established"}:
        return False
    return _protocol_v8_e3b_challenge_result(
        root, closure, contracts, descriptor, case, anchor,
        descriptor["anchorAdmission"], validators, require_current_consumability
    )


def _protocol_v8_e3b_case_accepted_realization_scope(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    descriptor: dict,
    case: dict,
    anchor: dict,
    validators: dict[str, Draft202012Validator],
    dependency,
    require_current_consumability: bool,
) -> bool:
    if anchor["candidate"] == {"kind": "not-established"}:
        return False
    return _protocol_v8_e3b_challenge_result(
        root, closure, contracts, descriptor, case, anchor,
        descriptor["anchorAdmission"], validators, require_current_consumability
    )


def _protocol_v8_e3b_case_accepted_repair_realization(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    descriptor: dict,
    case: dict,
    anchor: dict,
    validators: dict[str, Draft202012Validator],
    dependency,
    require_current_consumability: bool,
) -> bool:
    if anchor["candidate"] == {"kind": "not-established"}:
        return False
    return _protocol_v8_e3b_challenge_result(
        root, closure, contracts, descriptor, case, anchor,
        descriptor["anchorAdmission"], validators, require_current_consumability
    )


def _protocol_v8_e3b_derive_qualification_fact(
    closure: dict,
    predicates: dict[str, dict],
    qualification_ref: dict,
    descriptor: dict,
    case_record: dict,
) -> dict:
    """Derive the one catalog-selected qualification-result Predicate."""
    predicate_id = _mapping(case_record.get("case")).get("derives_predicate")
    predicate = predicates.get(predicate_id)
    if not isinstance(predicate, dict):
        raise ValueError("qualification case derives unknown PredicateRevision")
    definition = _mapping(predicate.get("definition"))
    derivation = _mapping(definition.get("derivation"))
    contract_id = descriptor.get("qualificationContract")
    if (
        derivation.get("kind") != "qualification-result"
        or derivation.get("qualification_contract") != contract_id
    ):
        raise ValueError("Predicate/Qualification catalog derivation mismatch")
    arguments = _mapping(definition.get("arguments"))
    if set(arguments) != {"qualification"}:
        raise ValueError("qualification-result Predicate arguments mismatch")
    declaration = _mapping(arguments.get("qualification"))
    if (
        declaration.get("kind") != "qualification-key"
        or declaration.get("qualification_contract") != contract_id
    ):
        raise ValueError("Predicate qualification argument cross-binding mismatch")
    fact_descriptor = {
        "schema": "turnlock.semantic-fact-descriptor.v1",
        "predicateRevision": predicate_id,
        "arguments": {"qualification": copy.deepcopy(qualification_ref)},
    }
    return _protocol_v8_e3a_register_fact_descriptor(
        closure, predicates, fact_descriptor
    )


def _protocol_v8_e3b_reduce_qualification(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    qualification_ref: object,
    *,
    fact_dependency_resolver=None,
    require_current_consumability: bool,
) -> dict | None:
    """Reduce one exact C4 QualificationKey to zero or one positive Fact."""
    if type(require_current_consumability) is not bool:
        raise ValueError("require_current_consumability must be an exact bool")
    case_map, case_errors = _protocol_v8_e3b_case_map(qualifications)
    if case_errors:
        raise ValueError(case_errors[0])
    handlers = {
        "positive-materiality": _protocol_v8_e3b_case_positive_materiality,
        "qualified-non-materiality": _protocol_v8_e3b_case_qualified_non_materiality,
        "qualified-refutation": _protocol_v8_e3b_case_qualified_refutation,
        "qualified-no-normative-impact": _protocol_v8_e3b_case_qualified_no_normative_impact,
        "qualified-decision-necessity": _protocol_v8_e3b_case_qualified_decision_necessity,
        "accepted-unique-correction": _protocol_v8_e3b_case_accepted_unique_correction,
        "accepted-realization-scope": _protocol_v8_e3b_case_accepted_realization_scope,
        "accepted-repair-realization": _protocol_v8_e3b_case_accepted_repair_realization,
    }
    if set(case_map) != set(handlers):
        raise ValueError("catalog/implementation integrity failure")
    descriptor = _protocol_v8_e3a_resolve_qualification_identity(
        closure, qualification_ref
    )
    case_record = _protocol_v8_e3b_case_for_descriptor(
        qualifications, descriptor
    )
    case = case_record["case"]
    case_id = case.get("case_id")
    validators = closure.get("_e3b_output_validators")
    if not isinstance(validators, dict):
        validators, validator_errors = _protocol_v8_e1_output_validators(root)
        if validator_errors:
            raise ValueError(validator_errors[0])
        # Validator compilation is a disposable technical cache, never semantic
        # authority or runtime persistence.
        closure["_e3b_output_validators"] = validators
    anchor = _protocol_v8_e3b_admission_context(
        root,
        closure,
        contracts,
        descriptor.get("anchorAdmission"),
        validators,
    )

    def dependency(reference: object) -> dict:
        return _protocol_v8_e3b_fact_dependency(
            closure, reference, fact_dependency_resolver
        )

    anchor_definition = _mapping(
        _mapping(case_record["qualification"].get("definition")).get("anchor")
    )
    anchor_kind = anchor_definition.get("kind")
    if anchor_kind == "direct-semantic-admission":
        if anchor["contract_id"] not in _sequence(
            anchor_definition.get("producer_contracts")
        ):
            return None
    elif anchor_kind == "producer-admission-of-fact":
        source_name = anchor_definition.get("source_input")
        source_ref = _mapping(descriptor.get("additionalInputs")).get(source_name)
        source = dependency(source_ref)
        if source["descriptor"].get("predicateRevision") != anchor_definition.get(
            "predicate_revision"
        ):
            return None
        if require_current_consumability and not source["consumable"]:
            return None
        producer = _protocol_v8_e3b_producer_admission_of_fact(
            source_ref, dependency
        )
        if descriptor.get("anchorAdmission") != producer:
            return None
        if anchor["contract_id"] not in _sequence(
            anchor_definition.get("producer_contracts")
        ):
            return None
    else:
        raise ValueError("unsupported published C4 qualification anchor kind")
    if require_current_consumability and not anchor["currently_consumable"]:
        return None
    established = handlers[case_id](
        root,
        closure,
        contracts,
        descriptor,
        case,
        anchor,
        validators,
        dependency,
        require_current_consumability,
    )
    if not established:
        return None
    fact_ref = _protocol_v8_e3b_derive_qualification_fact(
        closure,
        predicates,
        qualification_ref,
        descriptor,
        case_record,
    )
    return {
        "case_id": case_id,
        "qualification": copy.deepcopy(qualification_ref),
        "fact": fact_ref,
    }


def _protocol_v8_e3b_test_admit(
    closure: dict,
    contracts: dict[str, dict],
    contract_id: str,
    exact_logical_input: dict,
    candidate: object,
) -> dict:
    """Create one exact in-memory Admission through T1/T2/T3/completion/T4."""
    descriptor = {
        "schema": "turnlock.logical-question-descriptor.v1",
        "semanticQuestionContract": contract_id,
        "exactLogicalInput": copy.deepcopy(exact_logical_input),
    }
    qlek = _protocol_v8_e3a_register_question(closure, contracts, descriptor)
    counter = closure.setdefault("_e3b_test_execution_counter", 0) + 1
    closure["_e3b_test_execution_counter"] = counter
    execution_id = f"E-E3-B-{counter}"
    state = closure["e2_state"]
    _protocol_v8_e2_t1_acquire_authority(state, qlek, counter)
    _protocol_v8_e2_t2_authorize_execution(
        state, qlek, counter, execution_id, outer_authorized=True
    )
    _protocol_v8_e2_t3_arm_execution(state, qlek, counter, execution_id)
    _protocol_v8_e2_record_protocol_valid_completion(
        state, execution_id, candidate
    )
    result = _protocol_v8_e2_t4_reconcile_completion(state, execution_id)
    return {
        "kind": "semantic-admission",
        "admissionId": result["admission_id"],
    }


def _protocol_v8_e3b_test_challenge_candidate(
    challenge_contract: dict,
    zero_objections: bool,
) -> dict:
    """Build an exact self-check-only ChallengeSemanticValue."""
    objectives = list(
        _sequence(
            _mapping(
                _mapping(challenge_contract.get("definition")).get("challenge")
            ).get("objectives")
        )
    )
    assessments = [
        {"objective": objective, "objection_ids": []}
        for objective in objectives
    ]
    objections: list[dict] = []
    if not zero_objections:
        objection_id = "O-E3-B-1"
        assessments[0]["objection_ids"] = [objection_id]
        objections = [
            {
                "challenge_objection_id": objection_id,
                "objective": objectives[0],
                "statement": "test objection",
                "argument": "test objection argument",
                "evidence_references": ["E-E3-B-1"],
            }
        ]
    return {
        "objective_assessments": assessments,
        "objections": objections,
    }


def _protocol_v8_e3b_test_qualification(
    closure: dict,
    qualifications: dict[str, dict],
    contract_id: str,
    anchor: dict,
    additional: dict,
) -> dict:
    return _protocol_v8_e3a_register_qualification_descriptor(
        closure,
        qualifications,
        {
            "schema": "turnlock.qualification-key-descriptor.v1",
            "qualificationContract": contract_id,
            "anchorAdmission": copy.deepcopy(anchor),
            "additionalInputs": copy.deepcopy(additional),
        },
    )


def _protocol_v8_e3b_test_fact(
    closure: dict,
    predicates: dict[str, dict],
    predicate_id: str,
    arguments: dict,
) -> dict:
    return _protocol_v8_e3a_register_fact_descriptor(
        closure,
        predicates,
        {
            "schema": "turnlock.semantic-fact-descriptor.v1",
            "predicateRevision": predicate_id,
            "arguments": copy.deepcopy(arguments),
        },
    )


def _inactive_protocol_v8_e3b_qualification_reducer_errors(
    root: Path,
) -> list[str]:
    """Exercise all eight exact qualification cases in disposable C3 state."""
    errors: list[str] = []
    predicates, qualifications, catalog_errors = _protocol_v8_e3a_catalog_maps(root)
    contracts, contract_errors = _protocol_v8_e1_contract_map(root)
    validators, validator_errors = _protocol_v8_e1_output_validators(root)
    errors.extend(catalog_errors)
    errors.extend(contract_errors)
    errors.extend(validator_errors)
    case_map, case_errors = _protocol_v8_e3b_case_map(qualifications)
    errors.extend(case_errors)
    handlers = {
        "positive-materiality",
        "qualified-non-materiality",
        "qualified-refutation",
        "qualified-no-normative-impact",
        "qualified-decision-necessity",
        "accepted-unique-correction",
        "accepted-realization-scope",
        "accepted-repair-realization",
    }
    if len(qualifications) != 7:
        errors.append("inactive protocol v8 E3-B: expected 7 QualificationContracts")
    if len(case_map) != 8 or set(case_map) != handlers:
        errors.append("inactive protocol v8 E3-B: reducer handler coverage mismatch")
    derived = [
        _mapping(record.get("case")).get("derives_predicate")
        for record in case_map.values()
    ]
    if len(set(derived)) != 8:
        errors.append("inactive protocol v8 E3-B: case output Predicates are not unique")
    for case_id, record in case_map.items():
        predicate_id = _mapping(record.get("case")).get("derives_predicate")
        predicate = predicates.get(predicate_id)
        derivation = _mapping(_mapping(predicate).get("definition")).get("derivation")
        if not isinstance(derivation, dict) or (
            derivation.get("kind") != "qualification-result"
            or derivation.get("qualification_contract")
            != record.get("qualification_contract")
        ):
            errors.append(
                f"inactive protocol v8 E3-B: {case_id} Predicate cross-binding mismatch"
            )
    if errors:
        return errors

    state = _protocol_v8_e2_new_state()
    closure = _protocol_v8_e3a_new_closure(state)

    def semantic_value(value_type: str, label: str) -> dict:
        return _protocol_v8_e3a_register_semantic_value(
            closure, value_type, {"test": label}
        )

    finding_ref = semantic_value(
        "turnlock.semantic-value:FindingAdjudicationBasis@1", "finding-1"
    )
    finding_ref_two = semantic_value(
        "turnlock.semantic-value:FindingAdjudicationBasis@1", "finding-2"
    )
    finding_ref_three = semantic_value(
        "turnlock.semantic-value:FindingAdjudicationBasis@1", "finding-3"
    )
    surviving_ref = semantic_value(
        "turnlock.semantic-value:SurvivingMaterialBasis@1", "surviving-1"
    )
    surviving_ref_two = semantic_value(
        "turnlock.semantic-value:SurvivingMaterialBasis@1", "surviving-2"
    )
    candidate_view = semantic_value(
        "turnlock.semantic-value:CandidateView@1", "candidate-view"
    )
    candidate_revision = {
        "kind": "exact-authority",
        "authorityType": "turnlock.authority:candidate-revision.v2",
        "authorityId": "C-E3-B-1",
    }
    _protocol_v8_e3a_register_exact_authority(closure, candidate_revision)

    positive_materiality = {
        "authority_or_upstream_decision": True,
        "claim_structure": False,
        "normative_provenance": False,
        "modality_or_assurance_domain": False,
        "coverage_or_residual_assurance": False,
        "interaction_scope": False,
        "candidate_model_authorization": False,
        "rationale": "e3-b positive materiality",
    }
    all_false_materiality = {
        "authority_or_upstream_decision": False,
        "claim_structure": False,
        "normative_provenance": False,
        "modality_or_assurance_domain": False,
        "coverage_or_residual_assurance": False,
        "interaction_scope": False,
        "candidate_model_authorization": False,
        "rationale": "e3-b qualified non-materiality",
    }
    refutation_candidate = {
        "kind": "refutation-candidate",
        "ground": "premise-false",
        "attacked_premise_or_inference": "required premise",
        "evidence_references": ["E-E3-B"],
        "argument": "exact authority refutes the required premise",
        "counterexample_disposition": None,
    }
    unique_correction_candidate = {
        "kind": "unique-correction-candidate",
        "correction_requirements": [
            {"postcondition": "required semantic state"}
        ],
        "derivation_claims": [
            {
                "claim": "existing authority entails the required semantic state",
                "requirement_ordinals": [0],
                "authority_references": [
                    {"kind": "authority-content", "role": "normative-spec"}
                ],
                "evidence_references": [{"kind": "source-finding"}],
                "derivation_argument": (
                    "the controlling authority entails this requirement"
                ),
            }
        ],
        "alternatives_considered": [],
        "uniqueness_argument": {
            "authority_references": [
                {"kind": "authority-content", "role": "normative-spec"}
            ],
            "argument": (
                "no materially distinct authority-compatible correction remains"
            ),
        },
    }
    realization_scope_candidate = {
        "readable_paths": [],
        "writable_paths": [],
        "completeness_argument": {
            "requirement_surfaces": [],
            "whole_scope_argument": "complete test scope",
        },
        "minimal_write_authority_argument": {
            "writable_path_justifications": [],
            "no_additional_write_authority_argument": (
                "no additional write authority"
            ),
        },
    }
    repair_realization_candidate = {
        "kind": "repair-realization-candidate",
        "requirement_realizations": [],
        "operations": [],
    }
    nni_statement = {
        "statement": "downstream correction requires no product authority change",
        "evidence_references": [{"kind": "source-finding"}],
        "evidence_argument": (
            "the cited finding and authority establish the classification"
        ),
        "existing_authority": [],
        "affected_layers": ["architecture-or-implementation"],
        "semantic_disposition": "no-normative-impact",
        "disposition_basis": {
            "new_product_authority_not_required_argument": (
                "no new product authority is required"
            ),
            "changed_product_authority_not_required_argument": (
                "no existing product authority must change"
            ),
            "product_meaning_selection_not_required_argument": (
                "no product meaning selection is required"
            ),
            "accepted_observable_obligation_change_not_required_argument": (
                "accepted observable obligations remain unchanged"
            ),
        },
    }
    decision_statement = {
        "statement": "current product authority leaves two materially distinct outcomes",
        "evidence_references": [{"kind": "source-finding"}],
        "evidence_argument": (
            "the cited evidence exposes the unresolved product choice"
        ),
        "existing_authority": [],
        "affected_layers": ["normative-contract"],
        "semantic_disposition": "decision-required",
        "disposition_basis": {
            "kind": "product-underdetermination",
            "alternatives": [
                {
                    "alternative": "A",
                    "authority_compatibility_argument": (
                        "A is compatible with current authority"
                    ),
                },
                {
                    "alternative": "B",
                    "authority_compatibility_argument": (
                        "B is compatible with current authority"
                    ),
                },
            ],
            "material_distinction_argument": "A and B differ materially",
            "current_authority_non_selection_argument": (
                "current authority selects neither A nor B"
            ),
        },
    }

    def discovery_candidate(statement: dict) -> dict:
        return {
            "earliest_unresolved_cause": {
                "classification_statement_ordinal": 0,
                "evidence_references": [{"kind": "source-finding"}],
                "causal_explanation": (
                    "the test statement is the earliest unresolved cause"
                ),
                "upstream_exclusion_argument": "no earlier unresolved cause exists",
            },
            "classification_statements": [copy.deepcopy(statement)],
        }

    def challenge(
        target_closure: dict,
        contract_id: str,
        logical_input: dict,
        zero_objections: bool,
    ) -> dict:
        return _protocol_v8_e3b_test_admit(
            target_closure,
            contracts,
            contract_id,
            logical_input,
            _protocol_v8_e3b_test_challenge_candidate(
                contracts[contract_id], zero_objections
            ),
        )

    def qualification(
        target_closure: dict,
        contract_id: str,
        anchor: dict,
        additional: dict,
    ) -> dict:
        return _protocol_v8_e3b_test_qualification(
            target_closure, qualifications, contract_id, anchor, additional
        )

    def reduce(
        target_closure: dict,
        reference: dict,
        *,
        resolver=None,
        current: bool = False,
    ) -> dict | None:
        return _protocol_v8_e3b_reduce_qualification(
            root,
            target_closure,
            contracts,
            predicates,
            qualifications,
            reference,
            fact_dependency_resolver=resolver,
            require_current_consumability=current,
        )

    def expect_none(label: str, action) -> None:
        try:
            result = action()
        except ValueError as error:
            errors.append(f"inactive protocol v8 E3-B: {label} raised: {error}")
            return
        if result is not None:
            errors.append(f"inactive protocol v8 E3-B: {label} derived a Fact")

    successes: list[dict] = []
    materiality_anchor = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:MaterialityAssessmentInitial@1",
        {"findingAdjudicationBasis": finding_ref},
        positive_materiality,
    )
    positive_q = qualification(
        closure,
        "turnlock.qualification:MaterialityAssessmentQualification@1",
        materiality_anchor,
        {},
    )
    positive_result = reduce(closure, positive_q)
    if positive_result is None:
        errors.append("inactive protocol v8 E3-B: positive Materiality did not reduce")
        return errors
    successes.append(positive_result)
    if positive_result["case_id"] != "positive-materiality":
        errors.append("inactive protocol v8 E3-B: positive Materiality case mismatch")
    qpm_ref = positive_result["fact"]
    qpm_descriptor = _protocol_v8_e3a_resolve_fact_identity(closure, qpm_ref)
    if (
        qpm_descriptor.get("predicateRevision")
        != "turnlock.predicate:QualifiedPositiveMateriality@1"
        or qpm_descriptor.get("arguments") != {"qualification": positive_q}
    ):
        errors.append("inactive protocol v8 E3-B: QPM descriptor mismatch")
    if reduce(closure, positive_q)["fact"] != qpm_ref:
        errors.append("inactive protocol v8 E3-B: provenance changed Fact identity")

    positive_challenge = challenge(
        closure,
        "turnlock.sqc:MaterialityChallenge@1",
        {"challengedMaterialityAssessment": materiality_anchor},
        True,
    )
    positive_nonmaterial_q = qualification(
        closure,
        "turnlock.qualification:MaterialityAssessmentQualification@1",
        materiality_anchor,
        {"materialityChallenge": positive_challenge},
    )
    expect_none(
        "positive assessment used for QualifiedNonMateriality",
        lambda: reduce(closure, positive_nonmaterial_q),
    )

    all_false_anchor = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:MaterialityAssessmentInitial@1",
        {"findingAdjudicationBasis": finding_ref_two},
        all_false_materiality,
    )
    all_false_positive_q = qualification(
        closure,
        "turnlock.qualification:MaterialityAssessmentQualification@1",
        all_false_anchor,
        {},
    )
    expect_none(
        "all-false assessment used for QualifiedPositiveMateriality",
        lambda: reduce(closure, all_false_positive_q),
    )
    materiality_objection_closure = copy.deepcopy(closure)
    zero_materiality_challenge = challenge(
        closure,
        "turnlock.sqc:MaterialityChallenge@1",
        {"challengedMaterialityAssessment": all_false_anchor},
        True,
    )
    nonmaterial_q = qualification(
        closure,
        "turnlock.qualification:MaterialityAssessmentQualification@1",
        all_false_anchor,
        {"materialityChallenge": zero_materiality_challenge},
    )
    nonmaterial_result = reduce(closure, nonmaterial_q)
    if nonmaterial_result is None:
        errors.append("inactive protocol v8 E3-B: non-materiality did not reduce")
        return errors
    successes.append(nonmaterial_result)
    objection = challenge(
        materiality_objection_closure,
        "turnlock.sqc:MaterialityChallenge@1",
        {"challengedMaterialityAssessment": all_false_anchor},
        False,
    )
    objection_q = qualification(
        materiality_objection_closure,
        "turnlock.qualification:MaterialityAssessmentQualification@1",
        all_false_anchor,
        {"materialityChallenge": objection},
    )
    expect_none(
        "non-empty Materiality objections",
        lambda: reduce(materiality_objection_closure, objection_q),
    )

    refutation_anchor = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:RefutationInitial@1",
        {
            "findingAdjudicationBasis": finding_ref,
            "qualifiedPositiveMateriality": qpm_ref,
        },
        refutation_candidate,
    )
    refutation_objection_closure = copy.deepcopy(closure)
    refutation_challenge = challenge(
        closure,
        "turnlock.sqc:RefutationChallenge@1",
        {"challengedRefutation": refutation_anchor},
        True,
    )
    refutation_q = qualification(
        closure,
        "turnlock.qualification:RefutationQualification@1",
        refutation_anchor,
        {"refutationChallenge": refutation_challenge},
    )
    refutation_result = reduce(closure, refutation_q)
    if refutation_result is None:
        errors.append("inactive protocol v8 E3-B: Refutation did not reduce")
        return errors
    successes.append(refutation_result)
    refutation_objection = challenge(
        refutation_objection_closure,
        "turnlock.sqc:RefutationChallenge@1",
        {"challengedRefutation": refutation_anchor},
        False,
    )
    refutation_objection_q = qualification(
        refutation_objection_closure,
        "turnlock.qualification:RefutationQualification@1",
        refutation_anchor,
        {"refutationChallenge": refutation_objection},
    )
    expect_none(
        "non-empty Refutation objections",
        lambda: reduce(refutation_objection_closure, refutation_objection_q),
    )
    refutation_negative = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:RefutationInitial@1",
        {
            "findingAdjudicationBasis": finding_ref_two,
            "qualifiedPositiveMateriality": qpm_ref,
        },
        {"kind": "not-established"},
    )
    negative_refutation_challenge = challenge(
        closure,
        "turnlock.sqc:RefutationChallenge@1",
        {"challengedRefutation": refutation_negative},
        True,
    )
    negative_refutation_q = qualification(
        closure,
        "turnlock.qualification:RefutationQualification@1",
        refutation_negative,
        {"refutationChallenge": negative_refutation_challenge},
    )
    expect_none(
        "NotEstablished Refutation",
        lambda: reduce(closure, negative_refutation_q),
    )
    other_refutation = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:RefutationInitial@1",
        {
            "findingAdjudicationBasis": finding_ref_three,
            "qualifiedPositiveMateriality": qpm_ref,
        },
        refutation_candidate,
    )
    other_refutation_challenge = challenge(
        closure,
        "turnlock.sqc:RefutationChallenge@1",
        {"challengedRefutation": other_refutation},
        True,
    )
    wrong_refutation_target_q = qualification(
        closure,
        "turnlock.qualification:RefutationQualification@1",
        refutation_anchor,
        {"refutationChallenge": other_refutation_challenge},
    )
    expect_none(
        "Refutation challenge targets another Admission",
        lambda: reduce(closure, wrong_refutation_target_q),
    )

    nni_discovery = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:DiscoveryClassificationInitial@1",
        {"survivingMaterialBasis": surviving_ref},
        discovery_candidate(nni_statement),
    )
    decision_discovery = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:DiscoveryClassificationInitial@1",
        {"survivingMaterialBasis": surviving_ref_two},
        discovery_candidate(decision_statement),
    )
    nni_t = _protocol_v8_e3b_test_fact(
        closure,
        predicates,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": nni_discovery, "statement": nni_statement},
    )
    decision_t = _protocol_v8_e3b_test_fact(
        closure,
        predicates,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": decision_discovery, "statement": decision_statement},
    )
    support: dict[str, bool] = {
        nni_t["factId"]: True,
        decision_t["factId"]: True,
    }

    def fact_resolver(reference: dict) -> dict:
        descriptor = _protocol_v8_e3a_resolve_fact_identity(closure, reference)
        return {
            "reference": copy.deepcopy(reference),
            "descriptor": descriptor,
            "reconstructible": True,
            "consumable": support.get(reference["factId"], True),
        }

    uc_anchor = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:UniqueCorrectionInitial@1",
        {
            "survivingMaterialBasis": surviving_ref,
            "discovery": nni_discovery,
            "targetedDiscoveryStatement": nni_t,
        },
        unique_correction_candidate,
    )
    uc_objection_closure = copy.deepcopy(closure)
    uc_challenge = challenge(
        closure,
        "turnlock.sqc:UniqueCorrectionChallenge@1",
        {"challengedUniqueCorrection": uc_anchor},
        True,
    )
    uc_q = qualification(
        closure,
        "turnlock.qualification:UniqueCorrectionQualification@1",
        uc_anchor,
        {"uniqueCorrectionChallenge": uc_challenge},
    )
    uc_result = reduce(closure, uc_q)
    if uc_result is None:
        errors.append("inactive protocol v8 E3-B: UniqueCorrection did not reduce")
        return errors
    successes.append(uc_result)
    auc_ref = uc_result["fact"]
    uc_objection = challenge(
        uc_objection_closure,
        "turnlock.sqc:UniqueCorrectionChallenge@1",
        {"challengedUniqueCorrection": uc_anchor},
        False,
    )
    uc_objection_q = qualification(
        uc_objection_closure,
        "turnlock.qualification:UniqueCorrectionQualification@1",
        uc_anchor,
        {"uniqueCorrectionChallenge": uc_objection},
    )
    expect_none(
        "non-empty UniqueCorrection objections",
        lambda: reduce(uc_objection_closure, uc_objection_q),
    )
    uc_negative = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:UniqueCorrectionInitial@1",
        {
            "survivingMaterialBasis": surviving_ref_two,
            "discovery": decision_discovery,
            "targetedDiscoveryStatement": decision_t,
        },
        {"kind": "not-established"},
    )
    uc_negative_challenge = challenge(
        closure,
        "turnlock.sqc:UniqueCorrectionChallenge@1",
        {"challengedUniqueCorrection": uc_negative},
        True,
    )
    uc_negative_q = qualification(
        closure,
        "turnlock.qualification:UniqueCorrectionQualification@1",
        uc_negative,
        {"uniqueCorrectionChallenge": uc_negative_challenge},
    )
    expect_none("NotEstablished UniqueCorrection", lambda: reduce(closure, uc_negative_q))

    rs_anchor = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:RealizationScopeInitial@1",
        {
            "survivingMaterialBasis": surviving_ref,
            "acceptedUniqueCorrection": auc_ref,
            "candidateRevision": candidate_revision,
            "completeCandidateView": candidate_view,
        },
        realization_scope_candidate,
    )
    rs_objection_closure = copy.deepcopy(closure)
    rs_challenge = challenge(
        closure,
        "turnlock.sqc:RealizationScopeChallenge@1",
        {"challengedRealizationScope": rs_anchor},
        True,
    )
    rs_q = qualification(
        closure,
        "turnlock.qualification:RealizationScopeQualification@1",
        rs_anchor,
        {"realizationScopeChallenge": rs_challenge},
    )
    rs_result = reduce(closure, rs_q)
    if rs_result is None:
        errors.append("inactive protocol v8 E3-B: RealizationScope did not reduce")
        return errors
    successes.append(rs_result)
    ars_ref = rs_result["fact"]
    rs_objection = challenge(
        rs_objection_closure,
        "turnlock.sqc:RealizationScopeChallenge@1",
        {"challengedRealizationScope": rs_anchor},
        False,
    )
    rs_objection_q = qualification(
        rs_objection_closure,
        "turnlock.qualification:RealizationScopeQualification@1",
        rs_anchor,
        {"realizationScopeChallenge": rs_objection},
    )
    expect_none(
        "non-empty RealizationScope objections",
        lambda: reduce(rs_objection_closure, rs_objection_q),
    )
    candidate_revision_two = {
        "kind": "exact-authority",
        "authorityType": "turnlock.authority:candidate-revision.v2",
        "authorityId": "C-E3-B-2",
    }
    _protocol_v8_e3a_register_exact_authority(closure, candidate_revision_two)
    rs_negative = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:RealizationScopeInitial@1",
        {
            "survivingMaterialBasis": surviving_ref,
            "acceptedUniqueCorrection": auc_ref,
            "candidateRevision": candidate_revision_two,
            "completeCandidateView": candidate_view,
        },
        {"kind": "not-established"},
    )
    rs_negative_challenge = challenge(
        closure,
        "turnlock.sqc:RealizationScopeChallenge@1",
        {"challengedRealizationScope": rs_negative},
        True,
    )
    rs_negative_q = qualification(
        closure,
        "turnlock.qualification:RealizationScopeQualification@1",
        rs_negative,
        {"realizationScopeChallenge": rs_negative_challenge},
    )
    expect_none(
        "NotEstablished RealizationScope",
        lambda: reduce(closure, rs_negative_q),
    )

    rr_anchor = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:RepairRealizationInitial@1",
        {
            "survivingMaterialBasis": surviving_ref,
            "acceptedUniqueCorrection": auc_ref,
            "acceptedRealizationScope": ars_ref,
            "candidateRevision": candidate_revision,
            "scopedCandidateView": candidate_view,
        },
        repair_realization_candidate,
    )
    rr_objection_closure = copy.deepcopy(closure)
    rr_challenge = challenge(
        closure,
        "turnlock.sqc:RepairRealizationChallenge@1",
        {"challengedRepairRealization": rr_anchor},
        True,
    )
    rr_q = qualification(
        closure,
        "turnlock.qualification:RepairRealizationQualification@1",
        rr_anchor,
        {"repairRealizationChallenge": rr_challenge},
    )
    rr_result = reduce(closure, rr_q)
    if rr_result is None:
        errors.append("inactive protocol v8 E3-B: RepairRealization did not reduce")
        return errors
    successes.append(rr_result)
    rr_objection = challenge(
        rr_objection_closure,
        "turnlock.sqc:RepairRealizationChallenge@1",
        {"challengedRepairRealization": rr_anchor},
        False,
    )
    rr_objection_q = qualification(
        rr_objection_closure,
        "turnlock.qualification:RepairRealizationQualification@1",
        rr_anchor,
        {"repairRealizationChallenge": rr_objection},
    )
    expect_none(
        "non-empty RepairRealization objections",
        lambda: reduce(rr_objection_closure, rr_objection_q),
    )
    rr_negative = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:RepairRealizationInitial@1",
        {
            "survivingMaterialBasis": surviving_ref,
            "acceptedUniqueCorrection": auc_ref,
            "acceptedRealizationScope": ars_ref,
            "candidateRevision": candidate_revision_two,
            "scopedCandidateView": candidate_view,
        },
        {"kind": "not-established"},
    )
    rr_negative_challenge = challenge(
        closure,
        "turnlock.sqc:RepairRealizationChallenge@1",
        {"challengedRepairRealization": rr_negative},
        True,
    )
    rr_negative_q = qualification(
        closure,
        "turnlock.qualification:RepairRealizationQualification@1",
        rr_negative,
        {"repairRealizationChallenge": rr_negative_challenge},
    )
    expect_none(
        "NotEstablished RepairRealization",
        lambda: reduce(closure, rr_negative_q),
    )

    nni_objection_closure = copy.deepcopy(closure)
    nni_challenge = challenge(
        closure,
        "turnlock.sqc:NoNormativeImpactChallenge@1",
        {"targetedDiscoveryStatement": nni_t},
        True,
    )
    nni_q = qualification(
        closure,
        "turnlock.qualification:NoNormativeImpactQualification@1",
        nni_discovery,
        {
            "targetedDiscoveryStatement": nni_t,
            "noNormativeImpactChallenge": nni_challenge,
        },
    )
    nni_result = reduce(closure, nni_q, resolver=fact_resolver)
    if nni_result is None:
        errors.append("inactive protocol v8 E3-B: NoNormativeImpact did not reduce")
        return errors
    successes.append(nni_result)
    wrong_nni_anchor_q = qualification(
        closure,
        "turnlock.qualification:NoNormativeImpactQualification@1",
        decision_discovery,
        {
            "targetedDiscoveryStatement": nni_t,
            "noNormativeImpactChallenge": nni_challenge,
        },
    )
    expect_none(
        "NNI different producer anchor",
        lambda: reduce(closure, wrong_nni_anchor_q, resolver=fact_resolver),
    )
    wrong_nni_disposition_challenge = challenge(
        closure,
        "turnlock.sqc:NoNormativeImpactChallenge@1",
        {"targetedDiscoveryStatement": decision_t},
        True,
    )
    wrong_nni_disposition_q = qualification(
        closure,
        "turnlock.qualification:NoNormativeImpactQualification@1",
        decision_discovery,
        {
            "targetedDiscoveryStatement": decision_t,
            "noNormativeImpactChallenge": wrong_nni_disposition_challenge,
        },
    )
    expect_none(
        "decision-required target used as NNI",
        lambda: reduce(closure, wrong_nni_disposition_q, resolver=fact_resolver),
    )
    wrong_nni_target_q = qualification(
        closure,
        "turnlock.qualification:NoNormativeImpactQualification@1",
        nni_discovery,
        {
            "targetedDiscoveryStatement": nni_t,
            "noNormativeImpactChallenge": wrong_nni_disposition_challenge,
        },
    )
    expect_none(
        "NNI challenge targets another Fact",
        lambda: reduce(closure, wrong_nni_target_q, resolver=fact_resolver),
    )

    def cloned_resolver(target_closure: dict, consumable: bool = True):
        def resolve(reference: dict) -> dict:
            return {
                "reference": copy.deepcopy(reference),
                "descriptor": _protocol_v8_e3a_resolve_fact_identity(
                    target_closure, reference
                ),
                "reconstructible": True,
                "consumable": consumable,
            }
        return resolve

    nni_objection = challenge(
        nni_objection_closure,
        "turnlock.sqc:NoNormativeImpactChallenge@1",
        {"targetedDiscoveryStatement": nni_t},
        False,
    )
    nni_objection_q = qualification(
        nni_objection_closure,
        "turnlock.qualification:NoNormativeImpactQualification@1",
        nni_discovery,
        {
            "targetedDiscoveryStatement": nni_t,
            "noNormativeImpactChallenge": nni_objection,
        },
    )
    expect_none(
        "non-empty NNI objections",
        lambda: reduce(
            nni_objection_closure,
            nni_objection_q,
            resolver=cloned_resolver(nni_objection_closure),
        ),
    )

    d_ref = _protocol_v8_e3b_test_fact(
        closure,
        predicates,
        "turnlock.predicate:DecisionRequiredDiscoveryStatement@1",
        {"targetedDiscoveryStatement": decision_t},
    )
    u_ref = _protocol_v8_e3b_test_fact(
        closure,
        predicates,
        "turnlock.predicate:UniqueCorrectionExhaustion@1",
        {"targetedDiscoveryStatement": decision_t},
    )
    n_ref = _protocol_v8_e3b_test_fact(
        closure,
        predicates,
        "turnlock.predicate:DecisionNecessityCandidate@1",
        {
            "survivingMaterialBasis": surviving_ref_two,
            "decisionRequiredStatement": d_ref,
            "uniqueCorrectionExhaustion": u_ref,
        },
    )
    support.update(
        {
            d_ref["factId"]: True,
            u_ref["factId"]: True,
            n_ref["factId"]: True,
        }
    )
    dn_objection_closure = copy.deepcopy(closure)
    dn_challenge = challenge(
        closure,
        "turnlock.sqc:DecisionNecessityChallenge@1",
        {
            "survivingMaterialBasis": surviving_ref_two,
            "decisionRequiredStatement": d_ref,
            "uniqueCorrectionExhaustion": u_ref,
            "decisionNecessityCandidate": n_ref,
        },
        True,
    )
    dn_q = qualification(
        closure,
        "turnlock.qualification:DecisionNecessityQualification@1",
        decision_discovery,
        {
            "survivingMaterialBasis": surviving_ref_two,
            "decisionRequiredStatement": d_ref,
            "uniqueCorrectionExhaustion": u_ref,
            "decisionNecessityCandidate": n_ref,
            "decisionNecessityChallenge": dn_challenge,
        },
    )
    dn_result = reduce(closure, dn_q, resolver=fact_resolver)
    if dn_result is None:
        errors.append("inactive protocol v8 E3-B: DecisionNecessity did not reduce")
        return errors
    successes.append(dn_result)

    t_two = _protocol_v8_e3b_test_fact(
        closure,
        predicates,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": nni_discovery, "statement": decision_statement},
    )
    u_two = _protocol_v8_e3b_test_fact(
        closure,
        predicates,
        "turnlock.predicate:UniqueCorrectionExhaustion@1",
        {"targetedDiscoveryStatement": t_two},
    )
    n_two = _protocol_v8_e3b_test_fact(
        closure,
        predicates,
        "turnlock.predicate:DecisionNecessityCandidate@1",
        {
            "survivingMaterialBasis": surviving_ref,
            "decisionRequiredStatement": d_ref,
            "uniqueCorrectionExhaustion": u_ref,
        },
    )
    support.update({t_two["factId"]: True, u_two["factId"]: True, n_two["factId"]: True})
    wrong_u_q = qualification(
        closure,
        "turnlock.qualification:DecisionNecessityQualification@1",
        decision_discovery,
        {
            "survivingMaterialBasis": surviving_ref_two,
            "decisionRequiredStatement": d_ref,
            "uniqueCorrectionExhaustion": u_two,
            "decisionNecessityCandidate": n_ref,
            "decisionNecessityChallenge": dn_challenge,
        },
    )
    expect_none(
        "DN U targets another T",
        lambda: reduce(closure, wrong_u_q, resolver=fact_resolver),
    )
    wrong_n_q = qualification(
        closure,
        "turnlock.qualification:DecisionNecessityQualification@1",
        decision_discovery,
        {
            "survivingMaterialBasis": surviving_ref_two,
            "decisionRequiredStatement": d_ref,
            "uniqueCorrectionExhaustion": u_ref,
            "decisionNecessityCandidate": n_two,
            "decisionNecessityChallenge": dn_challenge,
        },
    )
    expect_none(
        "DN N arguments mismatch",
        lambda: reduce(closure, wrong_n_q, resolver=fact_resolver),
    )
    wrong_sm_q = qualification(
        closure,
        "turnlock.qualification:DecisionNecessityQualification@1",
        decision_discovery,
        {
            "survivingMaterialBasis": surviving_ref,
            "decisionRequiredStatement": d_ref,
            "uniqueCorrectionExhaustion": u_ref,
            "decisionNecessityCandidate": n_ref,
            "decisionNecessityChallenge": dn_challenge,
        },
    )
    expect_none(
        "DN wrong SM",
        lambda: reduce(closure, wrong_sm_q, resolver=fact_resolver),
    )
    dn_mismatch_challenge = challenge(
        closure,
        "turnlock.sqc:DecisionNecessityChallenge@1",
        {
            "survivingMaterialBasis": surviving_ref,
            "decisionRequiredStatement": d_ref,
            "uniqueCorrectionExhaustion": u_ref,
            "decisionNecessityCandidate": n_ref,
        },
        True,
    )
    dn_mismatch_q = qualification(
        closure,
        "turnlock.qualification:DecisionNecessityQualification@1",
        decision_discovery,
        {
            "survivingMaterialBasis": surviving_ref_two,
            "decisionRequiredStatement": d_ref,
            "uniqueCorrectionExhaustion": u_ref,
            "decisionNecessityCandidate": n_ref,
            "decisionNecessityChallenge": dn_mismatch_challenge,
        },
    )
    expect_none(
        "DN challenge logical-input mismatch",
        lambda: reduce(closure, dn_mismatch_q, resolver=fact_resolver),
    )
    dn_objection = challenge(
        dn_objection_closure,
        "turnlock.sqc:DecisionNecessityChallenge@1",
        {
            "survivingMaterialBasis": surviving_ref_two,
            "decisionRequiredStatement": d_ref,
            "uniqueCorrectionExhaustion": u_ref,
            "decisionNecessityCandidate": n_ref,
        },
        False,
    )
    dn_objection_q = qualification(
        dn_objection_closure,
        "turnlock.qualification:DecisionNecessityQualification@1",
        decision_discovery,
        {
            "survivingMaterialBasis": surviving_ref_two,
            "decisionRequiredStatement": d_ref,
            "uniqueCorrectionExhaustion": u_ref,
            "decisionNecessityCandidate": n_ref,
            "decisionNecessityChallenge": dn_objection,
        },
    )
    expect_none(
        "non-empty DecisionNecessity objections",
        lambda: reduce(
            dn_objection_closure,
            dn_objection_q,
            resolver=cloned_resolver(dn_objection_closure),
        ),
    )

    _protocol_v8_e3a_expect_rejected(
        lambda: reduce(closure, nni_q),
        errors,
        "NNI without E3-C dependency resolver",
        "E3-C fact dependency resolver required",
    )
    _protocol_v8_e3a_expect_rejected(
        lambda: reduce(closure, dn_q),
        errors,
        "DecisionNecessity without E3-C dependency resolver",
        "E3-C fact dependency resolver required",
    )

    def unreconstructible(reference: dict) -> dict:
        return {
            "reference": copy.deepcopy(reference),
            "descriptor": _protocol_v8_e3a_resolve_fact_identity(
                closure, reference
            ),
            "reconstructible": False,
            "consumable": True,
        }

    _protocol_v8_e3a_expect_rejected(
        lambda: reduce(closure, nni_q, resolver=unreconstructible),
        errors,
        "unreconstructible claimed Fact dependency",
        "not reconstructible",
    )

    def quarantined(reference: dict) -> dict:
        result = fact_resolver(reference)
        result["consumable"] = False
        return result

    expect_none(
        "currently quarantined Fact dependency",
        lambda: reduce(closure, nni_q, resolver=quarantined, current=True),
    )
    if reduce(closure, nni_q, resolver=quarantined, current=False) is None:
        errors.append(
            "inactive protocol v8 E3-B: quarantined Fact erased historical truth"
        )

    wrong_producer_q = qualification(
        closure,
        "turnlock.qualification:MaterialityAssessmentQualification@1",
        refutation_anchor,
        {},
    )
    expect_none("wrong anchor producer contract", lambda: reduce(closure, wrong_producer_q))
    malformed_anchor = _protocol_v8_e3b_test_admit(
        closure,
        contracts,
        "turnlock.sqc:MaterialityAssessmentInitial@1",
        {"findingAdjudicationBasis": finding_ref_three},
        {"invalid": True},
    )
    malformed_q = qualification(
        closure,
        "turnlock.qualification:MaterialityAssessmentQualification@1",
        malformed_anchor,
        {},
    )
    _protocol_v8_e3a_expect_rejected(
        lambda: reduce(closure, malformed_q),
        errors,
        "invalid Admission candidate schema",
        "output schema violation",
    )

    inconsistent_predicates = copy.deepcopy(predicates)
    inconsistent_predicates[
        "turnlock.predicate:QualifiedPositiveMateriality@1"
    ]["definition"]["derivation"]["qualification_contract"] = (
        "turnlock.qualification:RefutationQualification@1"
    )
    try:
        _protocol_v8_e3b_reduce_qualification(
            root,
            closure,
            contracts,
            inconsistent_predicates,
            qualifications,
            positive_q,
            require_current_consumability=False,
        )
    except ValueError:
        pass
    else:
        errors.append(
            "inactive protocol v8 E3-B: Predicate catalog mismatch did not fail"
        )

    materiality_record = _protocol_v8_e3a_resolve_admission_identity(
        closure, materiality_anchor
    )
    qlek = materiality_record["qlek"]
    conflict_candidate = {**positive_materiality, "claim_structure": True}
    conflict_id = _protocol_v8_e1_semantic_admission_id(qlek, conflict_candidate)
    token = _protocol_v8_e2_validated_witness_token(
        qlek, conflict_id, conflict_candidate, "IMPORTED-E3-B-CONFLICT"
    )
    _protocol_v8_e2_t5_reconcile_external_history(
        state,
        qlek,
        semantic_candidate=conflict_candidate,
        validated_origin_witness=token,
    )
    historical = reduce(closure, positive_q, current=False)
    if historical is None or historical["fact"] != qpm_ref:
        errors.append(
            "inactive protocol v8 E3-B: historical Admission conflict changed Fact truth"
        )
    expect_none(
        "currently quarantined Admission",
        lambda: reduce(closure, positive_q, current=True),
    )

    expected_predicates = set(derived)
    actual_predicates = {
        result["fact"]["predicateRevision"]
        for result in successes
    }
    if len(successes) != 8 or actual_predicates != expected_predicates:
        errors.append(
            "inactive protocol v8 E3-B: eight-case successful output cardinality mismatch"
        )
    for result in successes:
        if set(result) != {"case_id", "qualification", "fact"}:
            errors.append("inactive protocol v8 E3-B: reducer result shape mismatch")
    return errors


def _protocol_v8_e3c1_rule_map(
    predicates: dict[str, dict],
) -> tuple[dict[str, dict], list[str]]:
    """Select the two E3-C1 deterministic rules from the Predicate catalog."""
    supported = {
        "targeted-discovery-statement",
        "decision-required-discovery-statement",
    }
    rules: dict[str, dict] = {}
    errors: list[str] = []
    for predicate_id, predicate in predicates.items():
        definition = _mapping(predicate.get("definition"))
        derivation = _mapping(definition.get("derivation"))
        if derivation.get("kind") != "deterministic":
            continue
        rule = derivation.get("rule")
        if rule not in supported:
            continue
        if predicate.get("revision_id") != predicate_id:
            errors.append(
                f"inactive protocol v8 E3-C1: {rule} revision_id/catalog mismatch"
            )
            continue
        if rule in rules:
            errors.append(
                f"inactive protocol v8 E3-C1: duplicate deterministic rule {rule!r}"
            )
            continue
        rules[rule] = predicate
    if set(rules) != supported:
        errors.append(
            "inactive protocol v8 E3-C1: expected exactly the two Discovery rules"
        )
    return rules, errors


def _protocol_v8_e3c1_initial_discovery_statement_truth(
    producer_context: dict,
    statement: object,
) -> bool:
    """Reduce one exact initial Discovery statement occurrence."""
    definition = _mapping(producer_context["contract"].get("definition"))
    if (
        definition.get("question_kind") != "initial"
        or definition.get("family") != "discovery-classification"
    ):
        return False
    candidate = producer_context.get("candidate")
    if not isinstance(candidate, dict):
        raise ValueError("initial Discovery candidate must be an object")
    statements = candidate.get("classification_statements")
    if not isinstance(statements, list):
        raise ValueError("initial Discovery classification_statements must be an array")
    canonical = [
        _protocol_v8_e1_canonical_json_value_bytes(item)
        for item in statements
    ]
    if len(set(canonical)) != len(canonical):
        raise ValueError("duplicate exact canonical Discovery statement")
    target = _protocol_v8_e1_canonical_json_value_bytes(statement)
    return sum(item == target for item in canonical) == 1


def _protocol_v8_e3c1_nni_revision_statement_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    producer_context: dict,
    statement: object,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Reduce the one catalog-authorized positive NNI Discovery revision."""
    definition = _mapping(producer_context["contract"].get("definition"))
    if (
        definition.get("question_kind") != "revision"
        or definition.get("family") != "no-normative-impact"
    ):
        return False
    revision = _mapping(definition.get("revision"))
    prior_target_name = revision.get("prior_candidate_input")
    prior_challenge_name = revision.get("prior_challenge_input")
    required_disposition = revision.get("required_positive_disposition")
    if any(
        not isinstance(value, str) or not value
        for value in (
            prior_target_name,
            prior_challenge_name,
            required_disposition,
        )
    ):
        raise ValueError("NNI Discovery revision metadata is incomplete")
    candidate = producer_context.get("candidate")
    if candidate == {"kind": "not-established"}:
        return False
    if not isinstance(candidate, dict) or candidate.get("kind") != "revised-candidate":
        raise ValueError("NNI Discovery revision candidate has invalid positive shape")
    candidate_statement = candidate.get("statement")
    candidate_bytes = _protocol_v8_e1_canonical_json_value_bytes(
        candidate_statement
    )
    statement_bytes = _protocol_v8_e1_canonical_json_value_bytes(statement)
    if _mapping(candidate_statement).get("semantic_disposition") != required_disposition:
        raise ValueError("Discovery revision positive disposition violates SQC")
    if candidate_bytes != statement_bytes:
        return False

    producer_input = _mapping(producer_context["descriptor"]).get(
        "exactLogicalInput"
    )
    if not isinstance(producer_input, dict):
        raise ValueError("Discovery revision exactLogicalInput must be an object")
    prior_target_ref = producer_input.get(prior_target_name)
    prior_status = _protocol_v8_e3c1_fact_status(
        root,
        closure,
        contracts,
        predicates,
        prior_target_ref,
        active=active,
    )
    rules, rule_errors = _protocol_v8_e3c1_rule_map(predicates)
    if rule_errors:
        raise ValueError(rule_errors[0])
    targeted_id = rules["targeted-discovery-statement"]["revision_id"]
    if prior_status["descriptor"].get("predicateRevision") != targeted_id:
        return False
    if prior_status["reconstructible"] is not True:
        return False
    if require_current_consumability and prior_status["consumable"] is not True:
        return False
    prior_arguments = _mapping(prior_status["descriptor"].get("arguments"))
    prior_statement = _mapping(prior_arguments.get("statement"))
    if prior_statement.get("semantic_disposition") != required_disposition:
        return False

    followup = _mapping(revision.get("followup"))
    challenge_contract_id = followup.get("challenge_contract")
    challenge_contract = contracts.get(challenge_contract_id)
    if not isinstance(challenge_contract, dict):
        raise ValueError("NNI revision challenge contract is unknown")
    challenge_definition = _mapping(challenge_contract.get("definition"))
    challenge = _mapping(challenge_definition.get("challenge"))
    trigger_contracts = challenge.get("revision_trigger_producer_contracts")
    if (
        challenge_definition.get("question_kind") != "challenge"
        or not isinstance(trigger_contracts, list)
        or not trigger_contracts
        or any(not isinstance(item, str) or not item for item in trigger_contracts)
    ):
        raise ValueError("NNI revision challenge metadata is invalid")

    validators = closure.get("_e3b_output_validators")
    if not isinstance(validators, dict):
        validators, validator_errors = _protocol_v8_e1_output_validators(root)
        if validator_errors:
            raise ValueError(validator_errors[0])
        closure["_e3b_output_validators"] = validators
    prior_producer_context = _protocol_v8_e3b_admission_context(
        root,
        closure,
        contracts,
        prior_arguments.get("producerDiscovery"),
        validators,
    )
    if prior_producer_context["contract_id"] not in trigger_contracts:
        return False

    prior_challenge_ref = producer_input.get(prior_challenge_name)
    prior_challenge = _protocol_v8_e3b_admission_context(
        root,
        closure,
        contracts,
        prior_challenge_ref,
        validators,
    )
    if prior_challenge["contract_id"] != challenge_contract_id:
        return False
    target_name = challenge.get("target_input")
    logical_input = _mapping(challenge_definition.get("logical_input"))
    if not isinstance(target_name, str) or target_name not in logical_input:
        raise ValueError("NNI challenge target metadata is invalid")
    expected: dict[str, object] = {}
    for name in logical_input:
        if name == target_name:
            expected[name] = copy.deepcopy(prior_target_ref)
        elif name in producer_input:
            expected[name] = copy.deepcopy(producer_input[name])
        else:
            return False
    actual = _mapping(prior_challenge["descriptor"]).get("exactLogicalInput")
    if actual != expected:
        return False
    objections = _mapping(prior_challenge.get("candidate")).get("objections")
    if not isinstance(objections, list) or not objections:
        return False
    if (
        require_current_consumability
        and prior_challenge["currently_consumable"] is not True
    ):
        return False
    return True


def _protocol_v8_e3c1_targeted_discovery_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    descriptor: dict,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Reduce one catalog-selected TargetedDiscoveryStatement descriptor."""
    rules, rule_errors = _protocol_v8_e3c1_rule_map(predicates)
    if rule_errors:
        raise ValueError(rule_errors[0])
    predicate = rules["targeted-discovery-statement"]
    if descriptor.get("predicateRevision") != predicate.get("revision_id"):
        return False
    definition = _mapping(predicate.get("definition"))
    declarations = _mapping(definition.get("arguments"))
    if set(declarations) != {"producerDiscovery", "statement"}:
        raise ValueError("TargetedDiscoveryStatement catalog arguments mismatch")
    producer_declaration = _mapping(declarations.get("producerDiscovery"))
    producer_contracts = producer_declaration.get("producer_contracts")
    if (
        producer_declaration.get("kind") != "semantic-admission"
        or not isinstance(producer_contracts, list)
        or not producer_contracts
        or any(not isinstance(item, str) or not item for item in producer_contracts)
        or len(set(producer_contracts)) != len(producer_contracts)
    ):
        raise ValueError("TargetedDiscoveryStatement producer catalog is invalid")
    if _mapping(declarations.get("statement")).get("kind") != "canonical-value":
        raise ValueError("TargetedDiscoveryStatement statement catalog is invalid")
    arguments = descriptor.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) != {
        "producerDiscovery",
        "statement",
    }:
        raise ValueError("TargetedDiscoveryStatement descriptor arguments mismatch")

    validators = closure.get("_e3b_output_validators")
    if not isinstance(validators, dict):
        validators, validator_errors = _protocol_v8_e1_output_validators(root)
        if validator_errors:
            raise ValueError(validator_errors[0])
        closure["_e3b_output_validators"] = validators
    producer = _protocol_v8_e3b_admission_context(
        root,
        closure,
        contracts,
        arguments.get("producerDiscovery"),
        validators,
    )
    if producer["contract_id"] not in producer_contracts:
        return False
    if require_current_consumability and not producer["currently_consumable"]:
        return False
    producer_definition = _mapping(producer["contract"].get("definition"))
    question_kind = producer_definition.get("question_kind")
    family = producer_definition.get("family")
    if question_kind == "initial" and family == "discovery-classification":
        return _protocol_v8_e3c1_initial_discovery_statement_truth(
            producer, arguments.get("statement")
        )
    if question_kind == "revision" and family == "no-normative-impact":
        return _protocol_v8_e3c1_nni_revision_statement_truth(
            root,
            closure,
            contracts,
            predicates,
            producer,
            arguments.get("statement"),
            require_current_consumability=require_current_consumability,
            active=active,
        )
    if question_kind == "revision" and family == "decision-necessity":
        raise ValueError(
            "E3-C3 decision-required Discovery revision resolver required"
        )
    return False


def _protocol_v8_e3c1_decision_required_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    descriptor: dict,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Reduce one DecisionRequiredDiscoveryStatement through its exact target."""
    rules, rule_errors = _protocol_v8_e3c1_rule_map(predicates)
    if rule_errors:
        raise ValueError(rule_errors[0])
    targeted = rules["targeted-discovery-statement"]
    predicate = rules["decision-required-discovery-statement"]
    if descriptor.get("predicateRevision") != predicate.get("revision_id"):
        return False
    definition = _mapping(predicate.get("definition"))
    declarations = _mapping(definition.get("arguments"))
    if set(declarations) != {"targetedDiscoveryStatement"}:
        raise ValueError("DecisionRequiredDiscoveryStatement arguments mismatch")
    declaration = _mapping(declarations.get("targetedDiscoveryStatement"))
    if (
        declaration.get("kind") != "semantic-fact"
        or declaration.get("predicate_revision") != targeted.get("revision_id")
    ):
        raise ValueError("DecisionRequired target Predicate catalog mismatch")
    derivation = _mapping(definition.get("derivation"))
    required_disposition = derivation.get("required_disposition")
    allowed_basis_kinds = derivation.get("allowed_basis_kinds")
    if not isinstance(required_disposition, str) or not required_disposition:
        raise ValueError("DecisionRequired required disposition is invalid")
    if (
        not isinstance(allowed_basis_kinds, list)
        or not allowed_basis_kinds
        or any(
            not isinstance(item, str) or not item
            for item in allowed_basis_kinds
        )
        or len(set(allowed_basis_kinds)) != len(allowed_basis_kinds)
    ):
        raise ValueError("DecisionRequired allowed basis kinds are invalid")
    arguments = descriptor.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) != {
        "targetedDiscoveryStatement"
    }:
        raise ValueError("DecisionRequired descriptor arguments mismatch")
    target_ref = arguments.get("targetedDiscoveryStatement")
    target = _protocol_v8_e3c1_fact_status(
        root,
        closure,
        contracts,
        predicates,
        target_ref,
        active=active,
    )
    if target["descriptor"].get("predicateRevision") != targeted.get("revision_id"):
        return False
    if target["reconstructible"] is not True:
        return False
    if require_current_consumability and target["consumable"] is not True:
        return False
    statement = _mapping(
        _mapping(target["descriptor"].get("arguments")).get("statement")
    )
    if statement.get("semantic_disposition") != required_disposition:
        return False
    basis = statement.get("disposition_basis")
    return isinstance(basis, dict) and basis.get("kind") in allowed_basis_kinds


def _protocol_v8_e3c1_fact_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    descriptor: dict,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Dispatch exactly the two E3-C1 deterministic reducer rules."""
    rules, rule_errors = _protocol_v8_e3c1_rule_map(predicates)
    if rule_errors:
        raise ValueError(rule_errors[0])
    predicate_id = descriptor.get("predicateRevision")
    by_predicate = {
        predicate["revision_id"]: rule
        for rule, predicate in rules.items()
    }
    rule = by_predicate.get(predicate_id)
    if rule == "targeted-discovery-statement":
        return _protocol_v8_e3c1_targeted_discovery_truth(
            root,
            closure,
            contracts,
            predicates,
            descriptor,
            require_current_consumability=require_current_consumability,
            active=active,
        )
    if rule == "decision-required-discovery-statement":
        return _protocol_v8_e3c1_decision_required_truth(
            root,
            closure,
            contracts,
            predicates,
            descriptor,
            require_current_consumability=require_current_consumability,
            active=active,
        )
    raise ValueError("E3-C1 unsupported predicate; later E3-C stage required")


def _protocol_v8_e3c1_fact_status(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    fact_ref: object,
    *,
    active: set[str] | None = None,
) -> dict:
    """Resolve historical/current truth for only the two E3-C1 predicates."""
    descriptor = _protocol_v8_e3a_resolve_fact_identity(closure, fact_ref)
    assert isinstance(fact_ref, dict)
    fact_id = fact_ref["factId"]
    _protocol_v8_e3a_resolve_dependency_graph(
        closure,
        contracts,
        [("semantic-fact", fact_id)],
    )
    stack = active if active is not None else set()
    if fact_id in stack:
        raise ValueError("unlawful semantic Fact reducer cycle")
    stack.add(fact_id)
    try:
        reconstructible = _protocol_v8_e3c1_fact_truth(
            root,
            closure,
            contracts,
            predicates,
            descriptor,
            require_current_consumability=False,
            active=stack,
        )
        consumable = False
        if reconstructible:
            consumable = _protocol_v8_e3c1_fact_truth(
                root,
                closure,
                contracts,
                predicates,
                descriptor,
                require_current_consumability=True,
                active=stack,
            )
    finally:
        stack.remove(fact_id)
    return {
        "reference": copy.deepcopy(fact_ref),
        "descriptor": descriptor,
        "reconstructible": bool(reconstructible),
        "consumable": bool(consumable),
    }


def _protocol_v8_e3c1_claimed_fact_dependency(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    fact_ref: object,
) -> dict:
    """Adapt E3-C1 status to E3-B's claimed-Fact dependency contract."""
    status = _protocol_v8_e3c1_fact_status(
        root,
        closure,
        contracts,
        predicates,
        fact_ref,
    )
    if status["reconstructible"] is not True:
        raise ValueError("claimed Fact dependency is not reconstructible")
    return status


def _inactive_protocol_v8_e3c1_discovery_fact_errors(
    root: Path,
) -> list[str]:
    """Exercise the two Discovery Fact reducers in disposable semantic state."""
    errors: list[str] = []
    predicates, qualifications, catalog_errors = _protocol_v8_e3a_catalog_maps(root)
    contracts, contract_errors = _protocol_v8_e1_contract_map(root)
    validators, validator_errors = _protocol_v8_e1_output_validators(root)
    errors.extend(catalog_errors)
    errors.extend(contract_errors)
    errors.extend(validator_errors)
    rules, rule_errors = _protocol_v8_e3c1_rule_map(predicates)
    errors.extend(rule_errors)
    if set(rules) != {
        "targeted-discovery-statement",
        "decision-required-discovery-statement",
    }:
        errors.append("inactive protocol v8 E3-C1: rule-map coverage mismatch")
    targeted_predicate = rules.get("targeted-discovery-statement", {})
    decision_predicate = rules.get("decision-required-discovery-statement", {})
    targeted_definition = _mapping(targeted_predicate.get("definition"))
    targeted_producers = _mapping(
        _mapping(targeted_definition.get("arguments")).get("producerDiscovery")
    ).get("producer_contracts")
    decision_derivation = _mapping(
        _mapping(decision_predicate.get("definition")).get("derivation")
    )
    if not isinstance(targeted_producers, list) or not targeted_producers:
        errors.append("inactive protocol v8 E3-C1: no catalog Targeted producers")
    if (
        not isinstance(decision_derivation.get("required_disposition"), str)
        or not isinstance(decision_derivation.get("allowed_basis_kinds"), list)
    ):
        errors.append("inactive protocol v8 E3-C1: DecisionRequired metadata missing")
    if errors:
        return errors

    state = _protocol_v8_e2_new_state()
    closure = _protocol_v8_e3a_new_closure(state)
    closure["_e3b_output_validators"] = validators
    surviving_ref = _protocol_v8_e3a_register_semantic_value(
        closure,
        "turnlock.semantic-value:SurvivingMaterialBasis@1",
        {"test": "e3-c1-surviving-material"},
    )

    nni_statement = {
        "statement": "downstream correction requires no product authority change",
        "evidence_references": [{"kind": "source-finding"}],
        "evidence_argument": (
            "the cited finding and authority establish the classification"
        ),
        "existing_authority": [],
        "affected_layers": ["architecture-or-implementation"],
        "semantic_disposition": "no-normative-impact",
        "disposition_basis": {
            "new_product_authority_not_required_argument": (
                "no new product authority is required"
            ),
            "changed_product_authority_not_required_argument": (
                "no existing product authority must change"
            ),
            "product_meaning_selection_not_required_argument": (
                "no product meaning selection is required"
            ),
            "accepted_observable_obligation_change_not_required_argument": (
                "accepted observable obligations remain unchanged"
            ),
        },
    }
    decision_statement = {
        "statement": "current product authority leaves two materially distinct outcomes",
        "evidence_references": [{"kind": "source-finding"}],
        "evidence_argument": (
            "the cited evidence exposes the unresolved product choice"
        ),
        "existing_authority": [],
        "affected_layers": ["normative-contract"],
        "semantic_disposition": "decision-required",
        "disposition_basis": {
            "kind": "product-underdetermination",
            "alternatives": [
                {
                    "alternative": "A",
                    "authority_compatibility_argument": (
                        "A is compatible with current authority"
                    ),
                },
                {
                    "alternative": "B",
                    "authority_compatibility_argument": (
                        "B is compatible with current authority"
                    ),
                },
            ],
            "material_distinction_argument": "A and B differ materially",
            "current_authority_non_selection_argument": (
                "current authority selects neither A nor B"
            ),
        },
    }
    revised_nni_statement = {
        "statement": (
            "revised downstream correction still requires no product authority change"
        ),
        "evidence_references": [{"kind": "source-finding"}],
        "evidence_argument": (
            "the challenged evidence still establishes the downstream classification"
        ),
        "existing_authority": [],
        "affected_layers": ["architecture-or-implementation"],
        "semantic_disposition": "no-normative-impact",
        "disposition_basis": {
            "new_product_authority_not_required_argument": (
                "the revision still requires no new product authority"
            ),
            "changed_product_authority_not_required_argument": (
                "the revision changes no existing product authority"
            ),
            "product_meaning_selection_not_required_argument": (
                "the revision requires no product meaning selection"
            ),
            "accepted_observable_obligation_change_not_required_argument": (
                "the revision changes no accepted observable obligation"
            ),
        },
    }

    def discovery_candidate(statement: dict, *, duplicate: bool = False) -> dict:
        statements = [copy.deepcopy(statement)]
        if duplicate:
            statements.append(copy.deepcopy(statement))
        return {
            "earliest_unresolved_cause": {
                "classification_statement_ordinal": 0,
                "evidence_references": [{"kind": "source-finding"}],
                "causal_explanation": (
                    "the test statement is the earliest unresolved cause"
                ),
                "upstream_exclusion_argument": "no earlier unresolved cause exists",
            },
            "classification_statements": statements,
        }

    def semantic_value(label: str) -> dict:
        return _protocol_v8_e3a_register_semantic_value(
            closure,
            "turnlock.semantic-value:SurvivingMaterialBasis@1",
            {"test": label},
        )

    def admit(contract_id: str, logical_input: dict, candidate: object) -> dict:
        return _protocol_v8_e3b_test_admit(
            closure, contracts, contract_id, logical_input, candidate
        )

    def fact(predicate: dict, arguments: dict) -> dict:
        return _protocol_v8_e3b_test_fact(
            closure, predicates, predicate["revision_id"], arguments
        )

    def targeted(producer: dict, statement: dict) -> dict:
        return fact(
            targeted_predicate,
            {
                "producerDiscovery": producer,
                "statement": copy.deepcopy(statement),
            },
        )

    def initial(s_ref: dict, statement: dict, *, duplicate: bool = False) -> tuple[dict, dict]:
        producer = admit(
            "turnlock.sqc:DiscoveryClassificationInitial@1",
            {"survivingMaterialBasis": s_ref},
            discovery_candidate(statement, duplicate=duplicate),
        )
        return producer, targeted(producer, statement)

    def challenge(target: dict, zero_objections: bool) -> dict:
        contract_id = "turnlock.sqc:NoNormativeImpactChallenge@1"
        return admit(
            contract_id,
            {"targetedDiscoveryStatement": target},
            _protocol_v8_e3b_test_challenge_candidate(
                contracts[contract_id], zero_objections
            ),
        )

    def nni_revision(
        s_ref: dict,
        prior_target: dict,
        prior_challenge: dict,
        candidate: object,
    ) -> dict:
        return admit(
            "turnlock.sqc:DiscoveryNoNormativeImpactRevision@1",
            {
                "survivingMaterialBasis": s_ref,
                "priorNoNormativeImpactStatement": prior_target,
                "priorNoNormativeImpactChallenge": prior_challenge,
            },
            candidate,
        )

    def status(reference: dict, *, predicate_catalog=None) -> dict:
        return _protocol_v8_e3c1_fact_status(
            root,
            closure,
            contracts,
            predicate_catalog or predicates,
            reference,
        )

    def expect_false(label: str, reference: dict, *, predicate_catalog=None) -> None:
        try:
            result = status(reference, predicate_catalog=predicate_catalog)
        except ValueError as error:
            errors.append(f"inactive protocol v8 E3-C1: {label} raised: {error}")
            return
        if result["reconstructible"] or result["consumable"]:
            errors.append(f"inactive protocol v8 E3-C1: {label} became true")

    nni_producer, nni_t = initial(surviving_ref, nni_statement)
    nni_status = status(nni_t)
    if not nni_status["reconstructible"] or not nni_status["consumable"]:
        errors.append("inactive protocol v8 E3-C1: initial NNI Targeted Fact failed")

    decision_s = semantic_value("e3-c1-decision-material")
    decision_producer, decision_t = initial(decision_s, decision_statement)
    decision_t_status = status(decision_t)
    if not decision_t_status["reconstructible"] or not decision_t_status["consumable"]:
        errors.append("inactive protocol v8 E3-C1: initial decision Targeted Fact failed")

    absent_t = targeted(nni_producer, revised_nni_statement)
    expect_false("statement absent from initial Discovery", absent_t)

    duplicate_s = semantic_value("e3-c1-duplicate-material")
    duplicate_producer, duplicate_t = initial(
        duplicate_s, nni_statement, duplicate=True
    )
    _protocol_v8_e3a_expect_rejected(
        lambda: status(duplicate_t),
        errors,
        "duplicate exact Discovery statements",
        "duplicate exact canonical Discovery statement",
    )

    decision_d = fact(
        decision_predicate,
        {"targetedDiscoveryStatement": decision_t},
    )
    decision_d_status = status(decision_d)
    if not decision_d_status["reconstructible"] or not decision_d_status["consumable"]:
        errors.append("inactive protocol v8 E3-C1: DecisionRequired Fact failed")
    nni_d = fact(
        decision_predicate,
        {"targetedDiscoveryStatement": nni_t},
    )
    expect_false("DecisionRequired over NNI statement", nni_d)

    prior_objection = challenge(nni_t, False)
    revision_producer = nni_revision(
        surviving_ref,
        nni_t,
        prior_objection,
        {"kind": "revised-candidate", "statement": revised_nni_statement},
    )
    revised_t = targeted(revision_producer, revised_nni_statement)
    revised_status = status(revised_t)
    if not revised_status["reconstructible"] or not revised_status["consumable"]:
        errors.append("inactive protocol v8 E3-C1: positive NNI revision failed")

    zero_s = semantic_value("e3-c1-zero-challenge-material")
    zero_producer, zero_t = initial(zero_s, nni_statement)
    zero_challenge = challenge(zero_t, True)
    zero_revision = nni_revision(
        zero_s,
        zero_t,
        zero_challenge,
        {"kind": "revised-candidate", "statement": revised_nni_statement},
    )
    expect_false(
        "NNI revision after zero-objection challenge",
        targeted(zero_revision, revised_nni_statement),
    )

    second_challenge = challenge(revised_t, False)
    second_revision_statement = copy.deepcopy(revised_nni_statement)
    second_revision_statement["statement"] = (
        "second revised downstream correction remains non-normative"
    )
    second_revision = nni_revision(
        surviving_ref,
        revised_t,
        second_challenge,
        {
            "kind": "revised-candidate",
            "statement": second_revision_statement,
        },
    )
    expect_false(
        "second NNI revision",
        targeted(second_revision, second_revision_statement),
    )

    wrong_disposition_s = semantic_value("e3-c1-wrong-disposition-material")
    _wrong_producer, wrong_prior_t = initial(
        wrong_disposition_s, nni_statement
    )
    wrong_prior_challenge = challenge(wrong_prior_t, False)
    wrong_disposition_revision = nni_revision(
        wrong_disposition_s,
        wrong_prior_t,
        wrong_prior_challenge,
        {"kind": "revised-candidate", "statement": decision_statement},
    )
    wrong_disposition_t = targeted(
        wrong_disposition_revision, decision_statement
    )
    _protocol_v8_e3a_expect_rejected(
        lambda: status(wrong_disposition_t),
        errors,
        "wrong positive NNI revision disposition",
        "Discovery revision positive disposition violates SQC",
    )

    wrong_target_s = semantic_value("e3-c1-wrong-target-material")
    _wrong_target_producer, wrong_target_t = initial(
        wrong_target_s, nni_statement
    )
    another_s = semantic_value("e3-c1-another-target-material")
    _another_producer, another_t = initial(another_s, nni_statement)
    another_challenge = challenge(another_t, False)
    wrong_target_revision = nni_revision(
        wrong_target_s,
        wrong_target_t,
        another_challenge,
        {"kind": "revised-candidate", "statement": revised_nni_statement},
    )
    expect_false(
        "NNI prior challenge targets another Fact",
        targeted(wrong_target_revision, revised_nni_statement),
    )

    negative_s = semantic_value("e3-c1-negative-revision-material")
    _negative_producer, negative_t = initial(negative_s, nni_statement)
    negative_challenge = challenge(negative_t, False)
    negative_revision = nni_revision(
        negative_s,
        negative_t,
        negative_challenge,
        {"kind": "not-established"},
    )
    expect_false(
        "NotEstablished NNI revision",
        targeted(negative_revision, revised_nni_statement),
    )

    materiality_basis = _protocol_v8_e3a_register_semantic_value(
        closure,
        "turnlock.semantic-value:FindingAdjudicationBasis@1",
        {"test": "e3-c1-unauthorized-producer"},
    )
    materiality_producer = admit(
        "turnlock.sqc:MaterialityAssessmentInitial@1",
        {"findingAdjudicationBasis": materiality_basis},
        {
            "authority_or_upstream_decision": True,
            "claim_structure": False,
            "normative_provenance": False,
            "modality_or_assurance_domain": False,
            "coverage_or_residual_assurance": False,
            "interaction_scope": False,
            "candidate_model_authorization": False,
            "rationale": "e3-c1 unauthorized producer",
        },
    )
    expect_false(
        "unauthorized Targeted producer",
        targeted(materiality_producer, nni_statement),
    )

    restricted_predicates = copy.deepcopy(predicates)
    restricted_predicates[decision_predicate["revision_id"]]["definition"][
        "derivation"
    ]["allowed_basis_kinds"] = ["product-authority-conflict"]
    expect_false(
        "DecisionRequired basis kind excluded by catalog",
        decision_d,
        predicate_catalog=restricted_predicates,
    )

    unique_exhaustion_id = next(
        predicate_id
        for predicate_id, predicate in predicates.items()
        if _mapping(_mapping(predicate.get("definition")).get("derivation")).get(
            "rule"
        ) == "unique-correction-exhaustion"
    )
    unique_exhaustion = _protocol_v8_e3b_test_fact(
        closure,
        predicates,
        unique_exhaustion_id,
        {"targetedDiscoveryStatement": decision_t},
    )
    decision_candidate_id = next(
        predicate_id
        for predicate_id, predicate in predicates.items()
        if _mapping(_mapping(predicate.get("definition")).get("derivation")).get(
            "rule"
        ) == "decision-necessity-candidate"
    )
    decision_candidate = _protocol_v8_e3b_test_fact(
        closure,
        predicates,
        decision_candidate_id,
        {
            "survivingMaterialBasis": decision_s,
            "decisionRequiredStatement": decision_d,
            "uniqueCorrectionExhaustion": unique_exhaustion,
        },
    )
    decision_challenge_id = "turnlock.sqc:DecisionNecessityChallenge@1"
    decision_challenge = admit(
        decision_challenge_id,
        {
            "survivingMaterialBasis": decision_s,
            "decisionRequiredStatement": decision_d,
            "uniqueCorrectionExhaustion": unique_exhaustion,
            "decisionNecessityCandidate": decision_candidate,
        },
        _protocol_v8_e3b_test_challenge_candidate(
            contracts[decision_challenge_id], False
        ),
    )
    revised_decision_statement = copy.deepcopy(decision_statement)
    revised_decision_statement["statement"] = (
        "revised product authority still leaves two materially distinct outcomes"
    )
    decision_revision = admit(
        "turnlock.sqc:DiscoveryDecisionRequiredRevision@1",
        {
            "survivingMaterialBasis": decision_s,
            "priorDecisionRequiredStatement": decision_d,
            "priorDecisionNecessityChallenge": decision_challenge,
            "priorDecisionNecessityCandidate": decision_candidate,
        },
        {
            "kind": "revised-candidate",
            "statement": revised_decision_statement,
        },
    )
    staged_t = targeted(decision_revision, revised_decision_statement)
    _protocol_v8_e3a_expect_rejected(
        lambda: status(staged_t),
        errors,
        "staged decision-required Discovery revision",
        "E3-C3 decision-required Discovery revision resolver required",
    )

    nni_qualification = _protocol_v8_e3b_test_qualification(
        closure,
        qualifications,
        "turnlock.qualification:NoNormativeImpactQualification@1",
        zero_producer,
        {
            "targetedDiscoveryStatement": zero_t,
            "noNormativeImpactChallenge": zero_challenge,
        },
    )
    nni_result = _protocol_v8_e3b_reduce_qualification(
        root,
        closure,
        contracts,
        predicates,
        qualifications,
        nni_qualification,
        fact_dependency_resolver=lambda reference: (
            _protocol_v8_e3c1_claimed_fact_dependency(
                root,
                closure,
                contracts,
                predicates,
                reference,
            )
        ),
        require_current_consumability=True,
    )
    if nni_result is None or nni_result["fact"]["predicateRevision"] != (
        "turnlock.predicate:QualifiedNoNormativeImpact@1"
    ):
        errors.append("inactive protocol v8 E3-C1: real E3-B NNI integration failed")

    original_record = _protocol_v8_e3a_resolve_admission_identity(
        closure, decision_producer
    )
    qlek = original_record["qlek"]
    conflict_statement = copy.deepcopy(decision_statement)
    conflict_statement["statement"] = "conflicting decision Discovery candidate"
    conflict_candidate = discovery_candidate(conflict_statement)
    conflict_id = _protocol_v8_e1_semantic_admission_id(qlek, conflict_candidate)
    conflict_token = _protocol_v8_e2_validated_witness_token(
        qlek,
        conflict_id,
        conflict_candidate,
        "IMPORTED-E3-C1-CONFLICT",
    )
    _protocol_v8_e2_t5_reconcile_external_history(
        state,
        qlek,
        semantic_candidate=conflict_candidate,
        validated_origin_witness=conflict_token,
    )
    quarantined_t = status(decision_t)
    quarantined_d = status(decision_d)
    if (
        quarantined_t["reconstructible"] is not True
        or quarantined_t["consumable"] is not False
        or quarantined_d["reconstructible"] is not True
        or quarantined_d["consumable"] is not False
    ):
        errors.append(
            "inactive protocol v8 E3-C1: quarantine rewrote historical Discovery truth"
        )

    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3c1_fact_status(
            root,
            closure,
            contracts,
            predicates,
            nni_t,
            active={nni_t["factId"]},
        ),
        errors,
        "exact Fact reducer cycle",
        "unlawful semantic Fact reducer cycle",
    )
    cycle_a = ("exact-authority", "e3-c1-cycle", "A")
    cycle_b = ("exact-authority", "e3-c1-cycle", "B")
    _protocol_v8_e3a_expect_rejected(
        lambda: _protocol_v8_e3a_resolve_dependency_graph(
            closure,
            contracts,
            [cycle_a],
            lambda node: [cycle_b] if node == cycle_a else [cycle_a],
        ),
        errors,
        "E3-A dependency cycle",
        "unlawful semantic dependency cycle",
    )

    if targeted(nni_producer, nni_statement)["factId"] != nni_t["factId"]:
        errors.append("inactive protocol v8 E3-C1: provenance changed Targeted FactId")
    if fact(
        decision_predicate,
        {"targetedDiscoveryStatement": decision_t},
    )["factId"] != decision_d["factId"]:
        errors.append(
            "inactive protocol v8 E3-C1: provenance changed DecisionRequired FactId"
        )
    _protocol_v8_e3a_expect_rejected(
        lambda: status(unique_exhaustion),
        errors,
        "unsupported later-stage predicate",
        "E3-C1 unsupported predicate; later E3-C stage required",
    )
    dangling_target = dict(nni_t)
    dangling_target["factId"] = "semantic-fact-sha256:" + "9" * 64
    dangling_decision = fact(
        decision_predicate,
        {"targetedDiscoveryStatement": dangling_target},
    )
    _protocol_v8_e3a_expect_rejected(
        lambda: status(dangling_decision),
        errors,
        "dangling Targeted predecessor",
    )
    return errors


def _protocol_v8_e3c2_rule_map(
    predicates: dict[str, dict],
) -> tuple[dict[str, dict], list[str]]:
    """Select and validate exactly the two E3-C2 deterministic rules."""
    supported = {
        "refutation-exhaustion-without-qualified-refutation",
        "unique-correction-exhaustion",
    }
    proof_branches = [
        "initial-not-established",
        "revision-not-established",
        "revised-challenge-objections",
    ]
    rules: dict[str, dict] = {}
    errors: list[str] = []
    for predicate_id, predicate in predicates.items():
        definition = _mapping(predicate.get("definition"))
        derivation = _mapping(definition.get("derivation"))
        rule = derivation.get("rule")
        if rule not in supported:
            continue
        if derivation.get("kind") != "deterministic":
            errors.append(
                f"inactive protocol v8 E3-C2: {rule} derivation is not deterministic"
            )
            continue
        if predicate.get("revision_id") != predicate_id:
            errors.append(
                f"inactive protocol v8 E3-C2: {rule} revision_id/catalog mismatch"
            )
            continue
        if derivation.get("proof_branch_enters_fact_id") is not False:
            errors.append(
                f"inactive protocol v8 E3-C2: {rule} proof branch enters FactId"
            )
        if derivation.get("proof_branches") != proof_branches:
            errors.append(
                f"inactive protocol v8 E3-C2: {rule} proof branches mismatch"
            )
        if rule in rules:
            errors.append(
                f"inactive protocol v8 E3-C2: duplicate deterministic rule {rule!r}"
            )
            continue
        rules[rule] = predicate
    if set(rules) != supported:
        errors.append(
            "inactive protocol v8 E3-C2: expected exactly the two exhaustion rules"
        )
    return rules, errors


def _protocol_v8_e3c2_family_contracts(
    contracts: dict[str, dict],
    family: str,
    *,
    initial_inputs: list[str],
    challenge_target: str,
    revision_inputs: list[str],
    retained_inputs: list[str],
    prior_candidate_input: str,
    prior_challenge_input: str,
) -> dict:
    """Validate one exact bounded exhaustion-family SQC topology."""
    selected: dict[str, list[tuple[str, dict]]] = {
        "initial": [],
        "challenge": [],
        "revision": [],
    }
    for contract_id, contract in contracts.items():
        definition = _mapping(contract.get("definition"))
        question_kind = definition.get("question_kind")
        if definition.get("family") == family and question_kind in selected:
            selected[question_kind].append((contract_id, contract))
    if any(len(selected[kind]) != 1 for kind in selected):
        raise ValueError(
            f"inactive protocol v8 E3-C2: {family} contract topology is not unique"
        )
    initial_id, initial = selected["initial"][0]
    challenge_id, challenge_contract = selected["challenge"][0]
    revision_id, revision = selected["revision"][0]
    initial_definition = _mapping(initial.get("definition"))
    challenge_definition = _mapping(challenge_contract.get("definition"))
    revision_definition = _mapping(revision.get("definition"))
    if set(_mapping(initial_definition.get("logical_input"))) != set(initial_inputs):
        raise ValueError(
            f"inactive protocol v8 E3-C2: {family} initial logical input mismatch"
        )
    if set(_mapping(challenge_definition.get("logical_input"))) != {challenge_target}:
        raise ValueError(
            f"inactive protocol v8 E3-C2: {family} challenge logical input mismatch"
        )
    if set(_mapping(revision_definition.get("logical_input"))) != set(revision_inputs):
        raise ValueError(
            f"inactive protocol v8 E3-C2: {family} revision logical input mismatch"
        )
    challenge = _mapping(challenge_definition.get("challenge"))
    target_declaration = _mapping(
        _mapping(challenge_definition.get("logical_input")).get(challenge_target)
    )
    if (
        challenge.get("target_input") != challenge_target
        or challenge.get("revision_contract") != revision_id
        or challenge.get("revision_trigger_producer_contracts") != [initial_id]
        or target_declaration.get("kind") != "semantic-admission"
        or target_declaration.get("producer_contracts") != [initial_id, revision_id]
    ):
        raise ValueError(
            f"inactive protocol v8 E3-C2: {family} challenge binding mismatch"
        )
    revision_metadata = _mapping(revision_definition.get("revision"))
    if (
        revision_metadata.get("ordinal") != 1
        or revision_metadata.get("prior_candidate_input") != prior_candidate_input
        or revision_metadata.get("challenged_candidate_input")
        != prior_candidate_input
        or revision_metadata.get("revised_target_input") != prior_candidate_input
        or revision_metadata.get("prior_challenge_input") != prior_challenge_input
        or revision_metadata.get("retained_family_inputs") != retained_inputs
        or revision_metadata.get("withdrawal") != "not-established"
        or _mapping(revision_metadata.get("followup")).get("kind")
        != "fresh-challenge"
        or _mapping(revision_metadata.get("followup")).get("challenge_contract")
        != challenge_id
    ):
        raise ValueError(
            f"inactive protocol v8 E3-C2: {family} revision metadata mismatch"
        )
    return {
        "initial_id": initial_id,
        "challenge_id": challenge_id,
        "revision_id": revision_id,
        "initial": initial,
        "challenge": challenge_contract,
        "revision": revision,
        "challenge_target": challenge_target,
        "prior_candidate_input": prior_candidate_input,
        "prior_challenge_input": prior_challenge_input,
        "retained_inputs": list(retained_inputs),
    }


def _protocol_v8_e3c2_admissions_for_question(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    contract_id: str,
    exact_logical_input: dict,
) -> list[dict]:
    """Return every exact historical Admission for one reconstructed QLEK."""
    descriptor = {
        "schema": "turnlock.logical-question-descriptor.v1",
        "semanticQuestionContract": contract_id,
        "exactLogicalInput": copy.deepcopy(exact_logical_input),
    }
    qlek, qlek_errors = _protocol_v8_e1_recompute_structural_qlek(
        contracts, descriptor
    )
    if qlek_errors or qlek is None:
        raise ValueError(
            "inactive protocol v8 E3-C2: "
            + (qlek_errors[0] if qlek_errors else "invalid reconstructed QLEK")
        )
    state = closure["e2_state"]
    records: list[dict] = []
    effective = state["admissions"].get(qlek)
    if isinstance(effective, dict):
        records.append(effective)
    conflicts = state["conflicts"].get(qlek)
    if isinstance(conflicts, dict):
        records.extend(record for record in conflicts.values() if isinstance(record, dict))
    validators = closure.get("_e3b_output_validators")
    if not isinstance(validators, dict):
        validators, validator_errors = _protocol_v8_e1_output_validators(root)
        if validator_errors:
            raise ValueError(
                f"inactive protocol v8 E3-C2: {validator_errors[0]}"
            )
        closure["_e3b_output_validators"] = validators
    contexts: list[dict] = []
    seen: set[str] = set()
    for record in records:
        admission_id = record.get("admission_id")
        if not isinstance(admission_id, str) or admission_id in seen:
            continue
        seen.add(admission_id)
        context = _protocol_v8_e3b_admission_context(
            root,
            closure,
            contracts,
            {"kind": "semantic-admission", "admissionId": admission_id},
            validators,
        )
        if context["qlek"] != qlek or context["contract_id"] != contract_id:
            raise ValueError(
                "inactive protocol v8 E3-C2: reconstructed Admission closure mismatch"
            )
        contexts.append(context)
    return contexts


def _protocol_v8_e3c2_qualification_fact_status(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    fact_ref: object,
    *,
    active: set[str],
) -> dict:
    """Reconstruct only the three E3-B Fact dependencies admitted by C2."""
    descriptor = _protocol_v8_e3a_resolve_fact_identity(closure, fact_ref)
    assert isinstance(fact_ref, dict)
    allowed = {
        "turnlock.predicate:QualifiedPositiveMateriality@1",
        "turnlock.predicate:QualifiedRefutation@1",
        "turnlock.predicate:AcceptedUniqueCorrection@1",
    }
    if descriptor.get("predicateRevision") not in allowed:
        raise ValueError(
            "inactive protocol v8 E3-C2: unsupported qualification-result dependency"
        )
    arguments = descriptor.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) != {"qualification"}:
        raise ValueError(
            "inactive protocol v8 E3-C2: qualification-result arguments mismatch"
        )
    qualification_ref = arguments["qualification"]

    def dependency(reference: object) -> dict:
        return _protocol_v8_e3c2_dependency_status(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            reference,
            active=active,
        )

    historical = _protocol_v8_e3b_reduce_qualification(
        root,
        closure,
        contracts,
        predicates,
        qualifications,
        qualification_ref,
        fact_dependency_resolver=dependency,
        require_current_consumability=False,
    )
    current = _protocol_v8_e3b_reduce_qualification(
        root,
        closure,
        contracts,
        predicates,
        qualifications,
        qualification_ref,
        fact_dependency_resolver=dependency,
        require_current_consumability=True,
    )
    if historical is not None and historical.get("fact") != fact_ref:
        raise ValueError(
            "inactive protocol v8 E3-C2: qualification derived a different Fact"
        )
    if current is not None and current.get("fact") != fact_ref:
        raise ValueError(
            "inactive protocol v8 E3-C2: current qualification derived a different Fact"
        )
    return {
        "reference": copy.deepcopy(fact_ref),
        "descriptor": descriptor,
        "reconstructible": historical is not None,
        "consumable": current is not None,
    }


def _protocol_v8_e3c2_dependency_status(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    fact_ref: object,
    *,
    active: set[str],
) -> dict:
    """Dispatch only the E3-B and E3-C1 predecessors required by C2."""
    descriptor = _protocol_v8_e3a_resolve_fact_identity(closure, fact_ref)
    assert isinstance(fact_ref, dict)
    if fact_ref["factId"] in active:
        raise ValueError(
            "inactive protocol v8 E3-C2: unlawful semantic Fact reducer cycle"
        )
    predicate_id = descriptor.get("predicateRevision")
    if predicate_id == "turnlock.predicate:TargetedDiscoveryStatement@1":
        return _protocol_v8_e3c1_fact_status(
            root,
            closure,
            contracts,
            predicates,
            fact_ref,
            active=active,
        )
    if predicate_id in {
        "turnlock.predicate:QualifiedPositiveMateriality@1",
        "turnlock.predicate:QualifiedRefutation@1",
        "turnlock.predicate:AcceptedUniqueCorrection@1",
    }:
        return _protocol_v8_e3c2_qualification_fact_status(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            fact_ref,
            active=active,
        )
    raise ValueError(
        "inactive protocol v8 E3-C2: unsupported staged Fact dependency"
    )


def _protocol_v8_e3c2_terminal_branches(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    family_contracts: dict,
    initial_input: dict,
    *,
    require_current_consumability: bool,
) -> dict:
    """Evaluate the three exact bounded terminal branches for one family."""
    def usable(context: dict) -> bool:
        return (
            not require_current_consumability
            or context.get("currently_consumable") is True
        )

    initial_contexts = _protocol_v8_e3c2_admissions_for_question(
        root,
        closure,
        contracts,
        family_contracts["initial_id"],
        initial_input,
    )
    branches: set[str] = set()
    positive_admissions: set[str] = set()
    if any(
        context.get("candidate") == {"kind": "not-established"} and usable(context)
        for context in initial_contexts
    ):
        branches.add("initial-not-established")
    for initial in initial_contexts:
        if initial.get("candidate") == {"kind": "not-established"} or not usable(initial):
            continue
        initial_ref = initial["reference"]
        positive_admissions.add(initial_ref["admissionId"])
        challenge_input = {
            family_contracts["challenge_target"]: copy.deepcopy(initial_ref)
        }
        challenges = _protocol_v8_e3c2_admissions_for_question(
            root,
            closure,
            contracts,
            family_contracts["challenge_id"],
            challenge_input,
        )
        for challenge in challenges:
            objections = _mapping(challenge.get("candidate")).get("objections")
            if not usable(challenge) or not isinstance(objections, list) or not objections:
                continue
            revision_input = {
                name: copy.deepcopy(initial_input[name])
                for name in family_contracts["retained_inputs"]
            }
            revision_input[family_contracts["prior_candidate_input"]] = copy.deepcopy(
                initial_ref
            )
            revision_input[family_contracts["prior_challenge_input"]] = copy.deepcopy(
                challenge["reference"]
            )
            revisions = _protocol_v8_e3c2_admissions_for_question(
                root,
                closure,
                contracts,
                family_contracts["revision_id"],
                revision_input,
            )
            for revision in revisions:
                if not usable(revision):
                    continue
                if revision.get("candidate") == {"kind": "not-established"}:
                    branches.add("revision-not-established")
                    continue
                revision_ref = revision["reference"]
                positive_admissions.add(revision_ref["admissionId"])
                fresh_challenges = _protocol_v8_e3c2_admissions_for_question(
                    root,
                    closure,
                    contracts,
                    family_contracts["challenge_id"],
                    {
                        family_contracts["challenge_target"]: copy.deepcopy(
                            revision_ref
                        )
                    },
                )
                if any(
                    usable(fresh)
                    and isinstance(
                        _mapping(fresh.get("candidate")).get("objections"), list
                    )
                    and bool(_mapping(fresh.get("candidate")).get("objections"))
                    for fresh in fresh_challenges
                ):
                    branches.add("revised-challenge-objections")
    if len(branches) > 1:
        raise ValueError(
            "inactive protocol v8 E3-C2: multiple terminal proof branches are valid"
        )
    return {
        "established": len(branches) == 1,
        "branches": branches,
        "positive_admission_ids": positive_admissions,
    }


def _protocol_v8_e3c2_current_qualification_contradiction(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    counterpart_predicate: str,
    closure_admission_ids: set[str],
    *,
    active: set[str],
) -> bool:
    """Find a currently consumable opposite qualification for the exact closure."""
    for fact_id, preimages in closure["fact_descriptors"].items():
        if not isinstance(preimages, list):
            continue
        for descriptor in preimages:
            if (
                not isinstance(descriptor, dict)
                or descriptor.get("predicateRevision") != counterpart_predicate
            ):
                continue
            reference = {
                "kind": "semantic-fact",
                "predicateRevision": counterpart_predicate,
                "factId": fact_id,
            }
            result = _protocol_v8_e3c2_qualification_fact_status(
                root,
                closure,
                contracts,
                predicates,
                qualifications,
                reference,
                active=active,
            )
            if not result["consumable"]:
                continue
            qualification_ref = _mapping(descriptor.get("arguments")).get(
                "qualification"
            )
            qualification = _protocol_v8_e3a_resolve_qualification_identity(
                closure, qualification_ref
            )
            anchor = _mapping(qualification.get("anchorAdmission")).get(
                "admissionId"
            )
            if anchor in closure_admission_ids:
                return True
    return False


def _protocol_v8_e3c2_reject_current_contradiction(
    exhaustion_consumable: bool,
    counterpart_consumable: bool,
    family: str,
) -> None:
    """Fail closed rather than select a winner for a current contradiction."""
    if exhaustion_consumable and counterpart_consumable:
        raise ValueError(
            f"inactive protocol v8 E3-C2: {family} exhaustion/current qualification contradiction"
        )


def _protocol_v8_e3c2_refutation_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    descriptor: dict,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Reduce exact bounded Refutation exhaustion for one exact QPM Fact."""
    rules, rule_errors = _protocol_v8_e3c2_rule_map(predicates)
    if rule_errors:
        raise ValueError(rule_errors[0])
    predicate = rules["refutation-exhaustion-without-qualified-refutation"]
    if descriptor.get("predicateRevision") != predicate.get("revision_id"):
        return False
    declarations = _mapping(_mapping(predicate.get("definition")).get("arguments"))
    arguments = descriptor.get("arguments")
    if set(declarations) != {"qualifiedPositiveMateriality"} or (
        not isinstance(arguments, dict)
        or set(arguments) != {"qualifiedPositiveMateriality"}
    ):
        raise ValueError(
            "inactive protocol v8 E3-C2: Refutation exhaustion arguments mismatch"
        )
    qpm_ref = arguments["qualifiedPositiveMateriality"]
    qpm = _protocol_v8_e3c2_dependency_status(
        root,
        closure,
        contracts,
        predicates,
        qualifications,
        qpm_ref,
        active=active,
    )
    if qpm["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:QualifiedPositiveMateriality@1"
    ):
        return False
    if not qpm["reconstructible"]:
        return False
    if require_current_consumability and not qpm["consumable"]:
        return False
    qualification_ref = _mapping(qpm["descriptor"].get("arguments")).get(
        "qualification"
    )
    qualification = _protocol_v8_e3a_resolve_qualification_identity(
        closure, qualification_ref
    )
    materiality_ref = qualification.get("anchorAdmission")
    validators = closure.get("_e3b_output_validators")
    if not isinstance(validators, dict):
        raise ValueError(
            "inactive protocol v8 E3-C2: exact output validators are unavailable"
        )
    materiality = _protocol_v8_e3b_admission_context(
        root, closure, contracts, materiality_ref, validators
    )
    materiality_input = _mapping(materiality["descriptor"]).get("exactLogicalInput")
    if (
        not isinstance(materiality_input, dict)
        or "findingAdjudicationBasis" not in materiality_input
    ):
        raise ValueError(
            "inactive protocol v8 E3-C2: Materiality anchor input mismatch"
        )
    family = _protocol_v8_e3c2_family_contracts(
        contracts,
        "refutation",
        initial_inputs=["findingAdjudicationBasis", "qualifiedPositiveMateriality"],
        challenge_target="challengedRefutation",
        revision_inputs=[
            "findingAdjudicationBasis",
            "priorRefutation",
            "priorRefutationChallenge",
            "qualifiedPositiveMateriality",
        ],
        retained_inputs=["findingAdjudicationBasis", "qualifiedPositiveMateriality"],
        prior_candidate_input="priorRefutation",
        prior_challenge_input="priorRefutationChallenge",
    )
    initial_input = {
        "findingAdjudicationBasis": copy.deepcopy(
            materiality_input["findingAdjudicationBasis"]
        ),
        "qualifiedPositiveMateriality": copy.deepcopy(qpm_ref),
    }
    terminal = _protocol_v8_e3c2_terminal_branches(
        root,
        closure,
        contracts,
        family,
        initial_input,
        require_current_consumability=require_current_consumability,
    )
    if not terminal["established"]:
        return False
    if require_current_consumability:
        contradictory = _protocol_v8_e3c2_current_qualification_contradiction(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            "turnlock.predicate:QualifiedRefutation@1",
            terminal["positive_admission_ids"],
            active=active,
        )
        _protocol_v8_e3c2_reject_current_contradiction(
            True, contradictory, "Refutation"
        )
    return True


def _protocol_v8_e3c2_unique_correction_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    descriptor: dict,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Reduce exact bounded UniqueCorrection exhaustion for one exact target."""
    rules, rule_errors = _protocol_v8_e3c2_rule_map(predicates)
    if rule_errors:
        raise ValueError(rule_errors[0])
    predicate = rules["unique-correction-exhaustion"]
    if descriptor.get("predicateRevision") != predicate.get("revision_id"):
        return False
    declarations = _mapping(_mapping(predicate.get("definition")).get("arguments"))
    arguments = descriptor.get("arguments")
    if set(declarations) != {"targetedDiscoveryStatement"} or (
        not isinstance(arguments, dict)
        or set(arguments) != {"targetedDiscoveryStatement"}
    ):
        raise ValueError(
            "inactive protocol v8 E3-C2: UniqueCorrection exhaustion arguments mismatch"
        )
    target_ref = arguments["targetedDiscoveryStatement"]
    target = _protocol_v8_e3c2_dependency_status(
        root,
        closure,
        contracts,
        predicates,
        qualifications,
        target_ref,
        active=active,
    )
    if target["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:TargetedDiscoveryStatement@1"
    ):
        return False
    if not target["reconstructible"]:
        return False
    if require_current_consumability and not target["consumable"]:
        return False
    target_arguments = _mapping(target["descriptor"].get("arguments"))
    producer_ref = target_arguments.get("producerDiscovery")
    validators = closure.get("_e3b_output_validators")
    if not isinstance(validators, dict):
        validators, validator_errors = _protocol_v8_e1_output_validators(root)
        if validator_errors:
            raise ValueError(
                f"inactive protocol v8 E3-C2: {validator_errors[0]}"
            )
        closure["_e3b_output_validators"] = validators
    producer = _protocol_v8_e3b_admission_context(
        root, closure, contracts, producer_ref, validators
    )
    producer_input = _mapping(producer["descriptor"]).get("exactLogicalInput")
    if not isinstance(producer_input, dict) or "survivingMaterialBasis" not in producer_input:
        raise ValueError(
            "inactive protocol v8 E3-C2: Discovery producer has no exact SurvivingMaterialBasis"
        )
    family = _protocol_v8_e3c2_family_contracts(
        contracts,
        "unique-correction",
        initial_inputs=[
            "discovery",
            "survivingMaterialBasis",
            "targetedDiscoveryStatement",
        ],
        challenge_target="challengedUniqueCorrection",
        revision_inputs=[
            "discovery",
            "priorUniqueCorrection",
            "priorUniqueCorrectionChallenge",
            "survivingMaterialBasis",
            "targetedDiscoveryStatement",
        ],
        retained_inputs=[
            "discovery",
            "survivingMaterialBasis",
            "targetedDiscoveryStatement",
        ],
        prior_candidate_input="priorUniqueCorrection",
        prior_challenge_input="priorUniqueCorrectionChallenge",
    )
    initial_input = {
        "discovery": copy.deepcopy(producer_ref),
        "survivingMaterialBasis": copy.deepcopy(
            producer_input["survivingMaterialBasis"]
        ),
        "targetedDiscoveryStatement": copy.deepcopy(target_ref),
    }
    terminal = _protocol_v8_e3c2_terminal_branches(
        root,
        closure,
        contracts,
        family,
        initial_input,
        require_current_consumability=require_current_consumability,
    )
    if not terminal["established"]:
        return False
    if require_current_consumability:
        contradictory = _protocol_v8_e3c2_current_qualification_contradiction(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            "turnlock.predicate:AcceptedUniqueCorrection@1",
            terminal["positive_admission_ids"],
            active=active,
        )
        _protocol_v8_e3c2_reject_current_contradiction(
            True, contradictory, "UniqueCorrection"
        )
    return True


def _protocol_v8_e3c2_fact_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    descriptor: dict,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Dispatch exactly the two E3-C2 exhaustion rules."""
    rules, rule_errors = _protocol_v8_e3c2_rule_map(predicates)
    if rule_errors:
        raise ValueError(rule_errors[0])
    by_predicate = {
        predicate["revision_id"]: rule for rule, predicate in rules.items()
    }
    rule = by_predicate.get(descriptor.get("predicateRevision"))
    if rule == "refutation-exhaustion-without-qualified-refutation":
        return _protocol_v8_e3c2_refutation_truth(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            descriptor,
            require_current_consumability=require_current_consumability,
            active=active,
        )
    if rule == "unique-correction-exhaustion":
        return _protocol_v8_e3c2_unique_correction_truth(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            descriptor,
            require_current_consumability=require_current_consumability,
            active=active,
        )
    raise ValueError(
        "inactive protocol v8 E3-C2: unsupported root Predicate; later E3-C stage required"
    )


def _protocol_v8_e3c2_fact_status(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    fact_ref: object,
    *,
    active: set[str] | None = None,
) -> dict:
    """Resolve historical/current truth for only the two E3-C2 Predicates."""
    descriptor = _protocol_v8_e3a_resolve_fact_identity(closure, fact_ref)
    assert isinstance(fact_ref, dict)
    fact_id = fact_ref["factId"]
    _protocol_v8_e3a_resolve_dependency_graph(
        closure,
        contracts,
        [("semantic-fact", fact_id)],
    )
    stack = active if active is not None else set()
    if fact_id in stack:
        raise ValueError(
            "inactive protocol v8 E3-C2: unlawful semantic Fact reducer cycle"
        )
    stack.add(fact_id)
    try:
        reconstructible = _protocol_v8_e3c2_fact_truth(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            descriptor,
            require_current_consumability=False,
            active=stack,
        )
        consumable = False
        if reconstructible:
            consumable = _protocol_v8_e3c2_fact_truth(
                root,
                closure,
                contracts,
                predicates,
                qualifications,
                descriptor,
                require_current_consumability=True,
                active=stack,
            )
    finally:
        stack.remove(fact_id)
    return {
        "reference": copy.deepcopy(fact_ref),
        "descriptor": descriptor,
        "reconstructible": bool(reconstructible),
        "consumable": bool(consumable),
    }


def _inactive_protocol_v8_e3c2_exhaustion_fact_errors(
    root: Path,
) -> list[str]:
    """Exercise both bounded exhaustion reducers in disposable semantic state."""
    errors: list[str] = []
    predicates, qualifications, catalog_errors = _protocol_v8_e3a_catalog_maps(root)
    contracts, contract_errors = _protocol_v8_e1_contract_map(root)
    validators, validator_errors = _protocol_v8_e1_output_validators(root)
    errors.extend(catalog_errors)
    errors.extend(contract_errors)
    errors.extend(validator_errors)
    rules, rule_errors = _protocol_v8_e3c2_rule_map(predicates)
    errors.extend(rule_errors)
    if errors:
        return errors

    refutation_candidate = {
        "kind": "refutation-candidate",
        "ground": "premise-false",
        "attacked_premise_or_inference": "required premise",
        "evidence_references": ["E-E3-C2"],
        "argument": "exact authority refutes the required premise",
        "counterexample_disposition": None,
    }
    unique_candidate = {
        "kind": "unique-correction-candidate",
        "correction_requirements": [{"postcondition": "required semantic state"}],
        "derivation_claims": [
            {
                "claim": "existing authority entails the required semantic state",
                "requirement_ordinals": [0],
                "authority_references": [
                    {"kind": "authority-content", "role": "normative-spec"}
                ],
                "evidence_references": [{"kind": "source-finding"}],
                "derivation_argument": "the authority entails this requirement",
            }
        ],
        "alternatives_considered": [],
        "uniqueness_argument": {
            "authority_references": [
                {"kind": "authority-content", "role": "normative-spec"}
            ],
            "argument": "no distinct authority-compatible correction remains",
        },
    }
    positive_materiality = {
        "authority_or_upstream_decision": True,
        "claim_structure": False,
        "normative_provenance": False,
        "modality_or_assurance_domain": False,
        "coverage_or_residual_assurance": False,
        "interaction_scope": False,
        "candidate_model_authorization": False,
        "rationale": "e3-c2 positive materiality",
    }
    statement = {
        "statement": "the exact downstream correction has no normative impact",
        "evidence_references": [{"kind": "source-finding"}],
        "evidence_argument": "the exact evidence establishes this classification",
        "existing_authority": [],
        "affected_layers": ["architecture-or-implementation"],
        "semantic_disposition": "no-normative-impact",
        "disposition_basis": {
            "new_product_authority_not_required_argument": "no new authority",
            "changed_product_authority_not_required_argument": "no changed authority",
            "product_meaning_selection_not_required_argument": "no meaning selection",
            "accepted_observable_obligation_change_not_required_argument": (
                "no accepted obligation changes"
            ),
        },
    }

    def discovery_candidate(value: dict) -> dict:
        return {
            "earliest_unresolved_cause": {
                "classification_statement_ordinal": 0,
                "evidence_references": [{"kind": "source-finding"}],
                "causal_explanation": "the statement is the earliest unresolved cause",
                "upstream_exclusion_argument": "no earlier cause exists",
            },
            "classification_statements": [copy.deepcopy(value)],
        }

    def new_closure() -> dict:
        closure = _protocol_v8_e3a_new_closure(_protocol_v8_e2_new_state())
        closure["_e3b_output_validators"] = validators
        return closure

    def admit(closure: dict, contract_id: str, logical_input: dict, candidate: object) -> dict:
        return _protocol_v8_e3b_test_admit(
            closure, contracts, contract_id, logical_input, candidate
        )

    def challenge(closure: dict, contract_id: str, target_name: str, target: dict, zero: bool) -> dict:
        return admit(
            closure,
            contract_id,
            {target_name: target},
            _protocol_v8_e3b_test_challenge_candidate(
                contracts[contract_id], zero
            ),
        )

    def add_qpm(closure: dict, label: str = "exact") -> tuple[dict, dict, dict]:
        finding = _protocol_v8_e3a_register_semantic_value(
            closure,
            "turnlock.semantic-value:FindingAdjudicationBasis@1",
            {"test": f"e3-c2-finding-{label}"},
        )
        anchor = admit(
            closure,
            "turnlock.sqc:MaterialityAssessmentInitial@1",
            {"findingAdjudicationBasis": finding},
            positive_materiality,
        )
        qualification = _protocol_v8_e3b_test_qualification(
            closure,
            qualifications,
            "turnlock.qualification:MaterialityAssessmentQualification@1",
            anchor,
            {},
        )
        result = _protocol_v8_e3b_reduce_qualification(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            qualification,
            require_current_consumability=False,
        )
        if result is None:
            raise ValueError("inactive protocol v8 E3-C2: test QPM did not reduce")
        return finding, anchor, result["fact"]

    def add_target(closure: dict, label: str = "exact") -> tuple[dict, dict, dict]:
        surviving = _protocol_v8_e3a_register_semantic_value(
            closure,
            "turnlock.semantic-value:SurvivingMaterialBasis@1",
            {"test": f"e3-c2-surviving-{label}"},
        )
        producer = admit(
            closure,
            "turnlock.sqc:DiscoveryClassificationInitial@1",
            {"survivingMaterialBasis": surviving},
            discovery_candidate(statement),
        )
        target = _protocol_v8_e3b_test_fact(
            closure,
            predicates,
            "turnlock.predicate:TargetedDiscoveryStatement@1",
            {"producerDiscovery": producer, "statement": statement},
        )
        return surviving, producer, target

    def build(family: str, path: str) -> dict:
        closure = new_closure()
        if family == "refutation":
            finding, _materiality, subject = add_qpm(closure)
            initial_id = "turnlock.sqc:RefutationInitial@1"
            challenge_id = "turnlock.sqc:RefutationChallenge@1"
            revision_id = "turnlock.sqc:RefutationRevision@1"
            target_name = "challengedRefutation"
            initial_input = {
                "findingAdjudicationBasis": finding,
                "qualifiedPositiveMateriality": subject,
            }
            root_fact = _protocol_v8_e3b_test_fact(
                closure,
                predicates,
                rules[
                    "refutation-exhaustion-without-qualified-refutation"
                ]["revision_id"],
                {"qualifiedPositiveMateriality": subject},
            )
            positive = refutation_candidate
            retained = dict(initial_input)
            prior_name = "priorRefutation"
            prior_challenge_name = "priorRefutationChallenge"
        else:
            surviving, producer, subject = add_target(closure)
            initial_id = "turnlock.sqc:UniqueCorrectionInitial@1"
            challenge_id = "turnlock.sqc:UniqueCorrectionChallenge@1"
            revision_id = "turnlock.sqc:UniqueCorrectionRevision@1"
            target_name = "challengedUniqueCorrection"
            initial_input = {
                "discovery": producer,
                "survivingMaterialBasis": surviving,
                "targetedDiscoveryStatement": subject,
            }
            root_fact = _protocol_v8_e3b_test_fact(
                closure,
                predicates,
                rules["unique-correction-exhaustion"]["revision_id"],
                {"targetedDiscoveryStatement": subject},
            )
            positive = unique_candidate
            retained = dict(initial_input)
            prior_name = "priorUniqueCorrection"
            prior_challenge_name = "priorUniqueCorrectionChallenge"
        fixture = {
            "closure": closure,
            "subject": subject,
            "root": root_fact,
            "initial_input": initial_input,
            "initial_id": initial_id,
            "challenge_id": challenge_id,
            "revision_id": revision_id,
            "target_name": target_name,
            "retained": retained,
            "prior_name": prior_name,
            "prior_challenge_name": prior_challenge_name,
            "positive": positive,
        }
        if path == "absent":
            return fixture
        initial_candidate = (
            {"kind": "not-established"}
            if path == "initial-not-established"
            else positive
        )
        initial_ref = admit(closure, initial_id, initial_input, initial_candidate)
        fixture["initial"] = initial_ref
        if path in {"initial-not-established", "positive"}:
            return fixture
        zero_initial = path == "initial-zero-objections"
        initial_challenge = challenge(
            closure,
            challenge_id,
            target_name,
            initial_ref,
            zero_initial,
        )
        fixture["initial_challenge"] = initial_challenge
        if path in {"initial-zero-objections", "initial-objections"}:
            return fixture
        revision_input = copy.deepcopy(retained)
        revision_input[prior_name] = initial_ref
        revision_input[prior_challenge_name] = initial_challenge
        revision_candidate = (
            {"kind": "not-established"}
            if path == "revision-not-established"
            else positive
        )
        revision_ref = admit(
            closure, revision_id, revision_input, revision_candidate
        )
        fixture["revision"] = revision_ref
        fixture["revision_input"] = revision_input
        if path in {"revision-not-established", "revision-positive"}:
            return fixture
        fresh_challenge = challenge(
            closure,
            challenge_id,
            target_name,
            revision_ref,
            path == "revised-zero-objections",
        )
        fixture["fresh_challenge"] = fresh_challenge
        return fixture

    def status(fixture: dict) -> dict:
        return _protocol_v8_e3c2_fact_status(
            root,
            fixture["closure"],
            contracts,
            predicates,
            qualifications,
            fixture["root"],
        )

    def expect_rejected(
        label: str,
        action,
        required_text: str | None = None,
    ) -> None:
        try:
            action()
        except ValueError as error:
            if required_text is not None and required_text not in str(error):
                errors.append(
                    f"inactive protocol v8 E3-C2: {label} rejected without "
                    f"{required_text!r}"
                )
            return
        errors.append(f"inactive protocol v8 E3-C2: expected rejection: {label}")

    def expect_true(label: str, fixture: dict) -> None:
        try:
            result = status(fixture)
        except ValueError as error:
            errors.append(f"inactive protocol v8 E3-C2: {label} raised: {error}")
            return
        if not result["reconstructible"] or not result["consumable"]:
            errors.append(f"inactive protocol v8 E3-C2: {label} did not reduce")

    def expect_false(label: str, fixture: dict) -> None:
        try:
            result = status(fixture)
        except ValueError as error:
            errors.append(f"inactive protocol v8 E3-C2: {label} raised: {error}")
            return
        if result["reconstructible"] or result["consumable"]:
            errors.append(f"inactive protocol v8 E3-C2: {label} became true")

    positive_paths = [
        "initial-not-established",
        "revision-not-established",
        "revised-challenge-objections",
    ]
    negative_paths = [
        "absent",
        "positive",
        "initial-zero-objections",
        "initial-objections",
        "revision-positive",
        "revised-zero-objections",
    ]
    for family in ("refutation", "unique-correction"):
        positive_fixtures = [build(family, path) for path in positive_paths]
        for path, fixture in zip(positive_paths, positive_fixtures):
            expect_true(f"{family} {path}", fixture)
        fact_ids = {fixture["root"]["factId"] for fixture in positive_fixtures}
        descriptors = {
            _protocol_v8_e1_canonical_json_value_bytes(
                _protocol_v8_e3a_resolve_fact_identity(
                    fixture["closure"], fixture["root"]
                )
            )
            for fixture in positive_fixtures
        }
        if len(fact_ids) != 1 or len(descriptors) != 1:
            errors.append(
                f"inactive protocol v8 E3-C2: {family} proof branch changed Fact identity"
            )
        for path in negative_paths:
            expect_false(f"{family} {path}", build(family, path))

    for family in ("refutation", "unique-correction"):
        fixture = build(family, "revision-positive")
        second_input = copy.deepcopy(fixture["retained"])
        second_input[fixture["prior_name"]] = fixture["revision"]
        second_input[fixture["prior_challenge_name"]] = fixture["initial_challenge"]
        admit(
            fixture["closure"],
            fixture["revision_id"],
            second_input,
            {"kind": "not-established"},
        )
        expect_false(f"{family} second revision", fixture)

    wrong_ref = build("refutation", "initial-objections")
    other_finding, _other_materiality, other_qpm = add_qpm(
        wrong_ref["closure"], "other"
    )
    wrong_revision_inputs = [
        {
            **wrong_ref["retained"],
            "findingAdjudicationBasis": other_finding,
            "priorRefutation": wrong_ref["initial"],
            "priorRefutationChallenge": wrong_ref["initial_challenge"],
        },
        {
            **wrong_ref["retained"],
            "qualifiedPositiveMateriality": other_qpm,
            "priorRefutation": wrong_ref["initial"],
            "priorRefutationChallenge": wrong_ref["initial_challenge"],
        },
    ]
    alternate_initial = admit(
        wrong_ref["closure"],
        wrong_ref["initial_id"],
        {
            "findingAdjudicationBasis": other_finding,
            "qualifiedPositiveMateriality": wrong_ref["subject"],
        },
        refutation_candidate,
    )
    alternate_challenge = challenge(
        wrong_ref["closure"],
        wrong_ref["challenge_id"],
        wrong_ref["target_name"],
        alternate_initial,
        False,
    )
    wrong_revision_inputs.extend(
        [
            {
                **wrong_ref["retained"],
                "priorRefutation": alternate_initial,
                "priorRefutationChallenge": wrong_ref["initial_challenge"],
            },
            {
                **wrong_ref["retained"],
                "priorRefutation": wrong_ref["initial"],
                "priorRefutationChallenge": alternate_challenge,
            },
        ]
    )
    for index, revision_input in enumerate(wrong_revision_inputs):
        admit(
            wrong_ref["closure"],
            wrong_ref["revision_id"],
            revision_input,
            {"kind": "not-established"},
        )
        expect_false(f"refutation retained mismatch {index}", wrong_ref)
    wrong_challenge_target = build("refutation", "positive")
    other_finding, _anchor, other_qpm = add_qpm(
        wrong_challenge_target["closure"], "challenge-target"
    )
    other_initial = admit(
        wrong_challenge_target["closure"],
        wrong_challenge_target["initial_id"],
        {
            "findingAdjudicationBasis": other_finding,
            "qualifiedPositiveMateriality": other_qpm,
        },
        refutation_candidate,
    )
    challenge(
        wrong_challenge_target["closure"],
        wrong_challenge_target["challenge_id"],
        wrong_challenge_target["target_name"],
        other_initial,
        False,
    )
    expect_false("refutation wrong challenge target", wrong_challenge_target)

    wrong_uc_target = build("unique-correction", "positive")
    alt_surviving, alt_producer, alt_target = add_target(
        wrong_uc_target["closure"], "challenge-target"
    )
    alt_uc = admit(
        wrong_uc_target["closure"],
        wrong_uc_target["initial_id"],
        {
            "discovery": alt_producer,
            "survivingMaterialBasis": alt_surviving,
            "targetedDiscoveryStatement": alt_target,
        },
        unique_candidate,
    )
    challenge(
        wrong_uc_target["closure"],
        wrong_uc_target["challenge_id"],
        wrong_uc_target["target_name"],
        alt_uc,
        False,
    )
    expect_false("unique-correction wrong challenge target", wrong_uc_target)

    wrong_uc = build("unique-correction", "initial-objections")
    other_surviving, other_producer, other_target = add_target(
        wrong_uc["closure"], "other"
    )
    uc_wrong_revision_inputs = [
        {
            **wrong_uc["retained"],
            "survivingMaterialBasis": other_surviving,
            "priorUniqueCorrection": wrong_uc["initial"],
            "priorUniqueCorrectionChallenge": wrong_uc["initial_challenge"],
        },
        {
            **wrong_uc["retained"],
            "discovery": other_producer,
            "priorUniqueCorrection": wrong_uc["initial"],
            "priorUniqueCorrectionChallenge": wrong_uc["initial_challenge"],
        },
        {
            **wrong_uc["retained"],
            "targetedDiscoveryStatement": other_target,
            "priorUniqueCorrection": wrong_uc["initial"],
            "priorUniqueCorrectionChallenge": wrong_uc["initial_challenge"],
        },
    ]
    other_uc_initial = admit(
        wrong_uc["closure"],
        wrong_uc["initial_id"],
        {
            "discovery": other_producer,
            "survivingMaterialBasis": other_surviving,
            "targetedDiscoveryStatement": other_target,
        },
        unique_candidate,
    )
    other_uc_challenge = challenge(
        wrong_uc["closure"],
        wrong_uc["challenge_id"],
        wrong_uc["target_name"],
        other_uc_initial,
        False,
    )
    uc_wrong_revision_inputs.extend(
        [
            {
                **wrong_uc["retained"],
                "priorUniqueCorrection": other_uc_initial,
                "priorUniqueCorrectionChallenge": wrong_uc["initial_challenge"],
            },
            {
                **wrong_uc["retained"],
                "priorUniqueCorrection": wrong_uc["initial"],
                "priorUniqueCorrectionChallenge": other_uc_challenge,
            },
        ]
    )
    for index, revision_input in enumerate(uc_wrong_revision_inputs):
        admit(
            wrong_uc["closure"],
            wrong_uc["revision_id"],
            revision_input,
            {"kind": "not-established"},
        )
        expect_false(f"unique-correction retained mismatch {index}", wrong_uc)

    old_target = build("unique-correction", "initial-not-established")
    later_surviving, later_producer, later_target = add_target(
        old_target["closure"], "later"
    )
    later_fact = _protocol_v8_e3b_test_fact(
        old_target["closure"],
        predicates,
        rules["unique-correction-exhaustion"]["revision_id"],
        {"targetedDiscoveryStatement": later_target},
    )
    expect_true("old-target original exhaustion", old_target)
    later_fixture = dict(old_target)
    later_fixture["root"] = later_fact
    expect_false("old-target cannot bind later Targeted Fact", later_fixture)
    old_descriptor = _protocol_v8_e3a_resolve_fact_identity(
        old_target["closure"], old_target["root"]
    )
    if _mapping(old_descriptor.get("arguments")).get(
        "targetedDiscoveryStatement"
    ) == later_target or later_producer == old_target["retained"]["discovery"] or (
        later_surviving == old_target["retained"]["survivingMaterialBasis"]
    ):
        errors.append("inactive protocol v8 E3-C2: old-target fixture was not distinct")

    ambiguous = build("refutation", "initial-not-established")
    ambiguous_record = _protocol_v8_e3a_resolve_admission_identity(
        ambiguous["closure"], ambiguous["initial"]
    )
    positive_id = _protocol_v8_e1_semantic_admission_id(
        ambiguous_record["qlek"], refutation_candidate
    )
    positive_token = _protocol_v8_e2_validated_witness_token(
        ambiguous_record["qlek"],
        positive_id,
        refutation_candidate,
        "IMPORTED-E3-C2-AMBIGUOUS",
    )
    _protocol_v8_e2_t5_reconcile_external_history(
        ambiguous["closure"]["e2_state"],
        ambiguous_record["qlek"],
        semantic_candidate=refutation_candidate,
        validated_origin_witness=positive_token,
    )
    positive_ref = {"kind": "semantic-admission", "admissionId": positive_id}
    ambiguous_challenge = challenge(
        ambiguous["closure"],
        ambiguous["challenge_id"],
        ambiguous["target_name"],
        positive_ref,
        False,
    )
    ambiguous_revision_input = copy.deepcopy(ambiguous["retained"])
    ambiguous_revision_input[ambiguous["prior_name"]] = positive_ref
    ambiguous_revision_input[ambiguous["prior_challenge_name"]] = ambiguous_challenge
    admit(
        ambiguous["closure"],
        ambiguous["revision_id"],
        ambiguous_revision_input,
        {"kind": "not-established"},
    )
    expect_rejected(
        "simultaneous terminal branches",
        lambda: status(ambiguous),
        "multiple terminal proof branches",
    )

    quarantined = build("refutation", "initial-not-established")
    original = _protocol_v8_e3a_resolve_admission_identity(
        quarantined["closure"], quarantined["initial"]
    )
    conflict_id = _protocol_v8_e1_semantic_admission_id(
        original["qlek"], refutation_candidate
    )
    token = _protocol_v8_e2_validated_witness_token(
        original["qlek"],
        conflict_id,
        refutation_candidate,
        "IMPORTED-E3-C2-CONFLICT",
    )
    _protocol_v8_e2_t5_reconcile_external_history(
        quarantined["closure"]["e2_state"],
        original["qlek"],
        semantic_candidate=refutation_candidate,
        validated_origin_witness=token,
    )
    quarantine_status = status(quarantined)
    if (
        quarantine_status["reconstructible"] is not True
        or quarantine_status["consumable"] is not False
    ):
        errors.append(
            "inactive protocol v8 E3-C2: quarantine rewrote historical exhaustion"
        )

    try:
        _protocol_v8_e3c2_reject_current_contradiction(
            True, True, "Refutation"
        )
    except ValueError as error:
        if "inactive protocol v8 E3-C2:" not in str(error):
            errors.append("inactive protocol v8 E3-C2: contradiction prefix missing")
    else:
        errors.append("inactive protocol v8 E3-C2: Refutation contradiction accepted")
    try:
        _protocol_v8_e3c2_reject_current_contradiction(
            True, True, "UniqueCorrection"
        )
    except ValueError:
        pass
    else:
        errors.append(
            "inactive protocol v8 E3-C2: UniqueCorrection contradiction accepted"
        )

    dangling_ref = build("refutation", "absent")
    dangling_qpm = {
        "kind": "semantic-fact",
        "predicateRevision": "turnlock.predicate:QualifiedPositiveMateriality@1",
        "factId": "semantic-fact-sha256:" + "9" * 64,
    }
    dangling_ref["root"] = _protocol_v8_e3b_test_fact(
        dangling_ref["closure"],
        predicates,
        rules[
            "refutation-exhaustion-without-qualified-refutation"
        ]["revision_id"],
        {"qualifiedPositiveMateriality": dangling_qpm},
    )
    expect_rejected(
        "dangling QPM FactRef", lambda: status(dangling_ref)
    )
    dangling_uc = build("unique-correction", "absent")
    dangling_target = {
        "kind": "semantic-fact",
        "predicateRevision": "turnlock.predicate:TargetedDiscoveryStatement@1",
        "factId": "semantic-fact-sha256:" + "8" * 64,
    }
    dangling_uc["root"] = _protocol_v8_e3b_test_fact(
        dangling_uc["closure"],
        predicates,
        rules["unique-correction-exhaustion"]["revision_id"],
        {"targetedDiscoveryStatement": dangling_target},
    )
    expect_rejected(
        "dangling Targeted FactRef", lambda: status(dangling_uc)
    )

    mismatch = build("refutation", "initial-not-established")
    descriptor = _protocol_v8_e3a_resolve_fact_identity(
        mismatch["closure"], mismatch["root"]
    )
    mismatch["closure"]["fact_descriptors"][mismatch["root"]["factId"]] = [
        {
            **descriptor,
            "arguments": {
                "qualifiedPositiveMateriality": {
                    **mismatch["subject"],
                    "factId": "semantic-fact-sha256:" + "7" * 64,
                }
            },
        }
    ]
    expect_rejected(
        "FactId/descriptor mismatch",
        lambda: status(mismatch),
        "FactId/descriptor mismatch",
    )

    wrong_dependency = build("refutation", "absent")
    _surviving, _producer, target = add_target(
        wrong_dependency["closure"], "wrong-predicate"
    )
    forged_qpm = {
        "kind": "semantic-fact",
        "predicateRevision": "turnlock.predicate:QualifiedPositiveMateriality@1",
        "factId": target["factId"],
    }
    wrong_dependency["root"] = _protocol_v8_e3b_test_fact(
        wrong_dependency["closure"],
        predicates,
        rules[
            "refutation-exhaustion-without-qualified-refutation"
        ]["revision_id"],
        {"qualifiedPositiveMateriality": forged_qpm},
    )
    expect_rejected(
        "wrong PredicateRevision dependency",
        lambda: status(wrong_dependency),
        "FactRef predicate mismatch",
    )

    cycle = build("unique-correction", "initial-not-established")
    expect_rejected(
        "exact Fact reducer cycle",
        lambda: _protocol_v8_e3c2_fact_status(
            root,
            cycle["closure"],
            contracts,
            predicates,
            qualifications,
            cycle["root"],
            active={cycle["root"]["factId"]},
        ),
        "unlawful semantic Fact reducer cycle",
    )

    decision_candidate_id = "turnlock.predicate:DecisionNecessityCandidate@1"
    unsupported = build("unique-correction", "initial-not-established")
    unsupported["root"] = _protocol_v8_e3b_test_fact(
        unsupported["closure"],
        predicates,
        decision_candidate_id,
        {
            "survivingMaterialBasis": unsupported["retained"][
                "survivingMaterialBasis"
            ],
            "decisionRequiredStatement": _protocol_v8_e3b_test_fact(
                unsupported["closure"],
                predicates,
                "turnlock.predicate:DecisionRequiredDiscoveryStatement@1",
                {"targetedDiscoveryStatement": unsupported["subject"]},
            ),
            "uniqueCorrectionExhaustion": build(
                "unique-correction", "initial-not-established"
            )["root"],
        },
    )
    expect_rejected(
        "DecisionNecessityCandidate remains unsupported",
        lambda: status(unsupported),
        "later E3-C stage required",
    )

    inconsistent = copy.deepcopy(predicates)
    refutation_id = rules[
        "refutation-exhaustion-without-qualified-refutation"
    ]["revision_id"]
    inconsistent[refutation_id]["definition"]["derivation"]["proof_branches"] = [
        "revision-not-established",
        "initial-not-established",
        "revised-challenge-objections",
    ]
    _, inconsistent_errors = _protocol_v8_e3c2_rule_map(inconsistent)
    if not inconsistent_errors or any(
        not error.startswith("inactive protocol v8 E3-C2:")
        for error in inconsistent_errors
    ):
        errors.append(
            "inactive protocol v8 E3-C2: catalog branch-order corruption accepted"
        )
    inconsistent = copy.deepcopy(predicates)
    inconsistent[refutation_id]["definition"]["derivation"][
        "proof_branch_enters_fact_id"
    ] = True
    _, inconsistent_errors = _protocol_v8_e3c2_rule_map(inconsistent)
    if not inconsistent_errors:
        errors.append(
            "inactive protocol v8 E3-C2: proof-branch identity leakage accepted"
        )
    return errors


def _protocol_v8_e3c3_rule_map(
    predicates: dict[str, dict],
) -> tuple[dict[str, dict], list[str]]:
    """Select and validate the sole E3-C3 deterministic Predicate rule."""
    rule_name = "decision-necessity-candidate"
    matches: list[tuple[str, dict]] = []
    errors: list[str] = []
    for predicate_id, predicate in predicates.items():
        definition = _mapping(predicate.get("definition"))
        derivation = _mapping(definition.get("derivation"))
        if derivation.get("rule") == rule_name:
            matches.append((predicate_id, predicate))
    if len(matches) != 1:
        errors.append(
            "inactive protocol v8 E3-C3: expected exactly one DecisionNecessity rule"
        )
        return {}, errors
    predicate_id, predicate = matches[0]
    definition = _mapping(predicate.get("definition"))
    derivation = _mapping(definition.get("derivation"))
    if predicate.get("revision_id") != predicate_id or predicate_id != (
        "turnlock.predicate:DecisionNecessityCandidate@1"
    ):
        errors.append(
            "inactive protocol v8 E3-C3: DecisionNecessity revision/catalog mismatch"
        )
    if (
        derivation.get("kind") != "deterministic"
        or derivation.get("rule") != rule_name
        or derivation.get("projection") != "exact-target-disposition-basis"
    ):
        errors.append(
            "inactive protocol v8 E3-C3: DecisionNecessity derivation mismatch"
        )
    arguments = _mapping(definition.get("arguments"))
    expected_arguments = {
        "survivingMaterialBasis": {
            "kind": "semantic-value",
            "value_type": "turnlock.semantic-value:SurvivingMaterialBasis@1",
        },
        "decisionRequiredStatement": {
            "kind": "semantic-fact",
            "predicate_revision": (
                "turnlock.predicate:DecisionRequiredDiscoveryStatement@1"
            ),
        },
        "uniqueCorrectionExhaustion": {
            "kind": "semantic-fact",
            "predicate_revision": "turnlock.predicate:UniqueCorrectionExhaustion@1",
        },
    }
    if arguments != expected_arguments:
        errors.append(
            "inactive protocol v8 E3-C3: DecisionNecessity arguments mismatch"
        )
    if _mapping(definition.get("semantic_view")) != {
        "kind": "decision-necessity-candidate",
        "source_argument": "decisionRequiredStatement",
    }:
        errors.append(
            "inactive protocol v8 E3-C3: DecisionNecessity semantic-view metadata mismatch"
        )
    return {rule_name: predicate}, errors


def _protocol_v8_e3c3_topology(
    contracts: dict[str, dict],
) -> dict:
    """Validate the exact DecisionNecessity challenge/revision topology."""
    challenge_id = "turnlock.sqc:DecisionNecessityChallenge@1"
    revision_id = "turnlock.sqc:DiscoveryDecisionRequiredRevision@1"
    challenge_contract = contracts.get(challenge_id)
    revision_contract = contracts.get(revision_id)
    if not isinstance(challenge_contract, dict) or not isinstance(revision_contract, dict):
        raise ValueError(
            "inactive protocol v8 E3-C3: DecisionNecessity topology contract missing"
        )
    challenge_definition = _mapping(challenge_contract.get("definition"))
    revision_definition = _mapping(revision_contract.get("definition"))
    challenge_inputs = _mapping(challenge_definition.get("logical_input"))
    expected_challenge_inputs = {
        "survivingMaterialBasis": {
            "kind": "semantic-value",
            "value_type": "turnlock.semantic-value:SurvivingMaterialBasis@1",
        },
        "decisionRequiredStatement": {
            "kind": "semantic-fact",
            "predicate_revision": (
                "turnlock.predicate:DecisionRequiredDiscoveryStatement@1"
            ),
        },
        "uniqueCorrectionExhaustion": {
            "kind": "semantic-fact",
            "predicate_revision": "turnlock.predicate:UniqueCorrectionExhaustion@1",
        },
        "decisionNecessityCandidate": {
            "kind": "semantic-fact",
            "predicate_revision": "turnlock.predicate:DecisionNecessityCandidate@1",
        },
    }
    challenge = _mapping(challenge_definition.get("challenge"))
    if (
        challenge_contract.get("revision_id") != challenge_id
        or challenge_definition.get("family") != "decision-necessity"
        or challenge_definition.get("question_kind") != "challenge"
        or challenge_inputs != expected_challenge_inputs
        or challenge.get("challenge_kind") != "decision-necessity"
        or challenge.get("target_input") != "decisionNecessityCandidate"
        or challenge.get("revision_contract") != revision_id
        or challenge.get("revision_trigger_producer_contracts")
        != ["turnlock.sqc:DiscoveryClassificationInitial@1"]
        or challenge.get("zero_objections_derives_predicate")
        != "turnlock.predicate:QualifiedDecisionNecessity@1"
    ):
        raise ValueError(
            "inactive protocol v8 E3-C3: DecisionNecessity challenge topology mismatch"
        )
    revision_inputs = _mapping(revision_definition.get("logical_input"))
    expected_revision_inputs = {
        "survivingMaterialBasis": {
            "kind": "semantic-value",
            "value_type": "turnlock.semantic-value:SurvivingMaterialBasis@1",
        },
        "priorDecisionRequiredStatement": {
            "kind": "semantic-fact",
            "predicate_revision": (
                "turnlock.predicate:DecisionRequiredDiscoveryStatement@1"
            ),
        },
        "priorDecisionNecessityCandidate": {
            "kind": "semantic-fact",
            "predicate_revision": "turnlock.predicate:DecisionNecessityCandidate@1",
        },
        "priorDecisionNecessityChallenge": {
            "kind": "semantic-admission",
            "producer_contracts": [
                "turnlock.sqc:DecisionNecessityChallenge@1"
            ],
        },
    }
    revision = _mapping(revision_definition.get("revision"))
    followup = _mapping(revision.get("followup"))
    if (
        revision_contract.get("revision_id") != revision_id
        or revision_definition.get("family") != "decision-necessity"
        or revision_definition.get("question_kind") != "revision"
        or revision_inputs != expected_revision_inputs
        or revision.get("ordinal") != 1
        or revision.get("prior_candidate_input")
        != "priorDecisionRequiredStatement"
        or revision.get("challenged_candidate_input")
        != "priorDecisionNecessityCandidate"
        or revision.get("prior_challenge_input")
        != "priorDecisionNecessityChallenge"
        or revision.get("revised_target_input")
        != "priorDecisionRequiredStatement"
        or revision.get("retained_family_inputs") != ["survivingMaterialBasis"]
        or revision.get("required_positive_disposition") != "decision-required"
        or revision.get("sibling_discovery_statements_immutable") is not True
        or revision.get("withdrawal") != "not-established"
        or followup
        != {
            "challenge_contract": challenge_id,
            "decision_necessity_candidate_predicate": (
                "turnlock.predicate:DecisionNecessityCandidate@1"
            ),
            "kind": "fresh-unique-correction-path",
            "unique_correction_exhaustion_predicate": (
                "turnlock.predicate:UniqueCorrectionExhaustion@1"
            ),
            "unique_correction_initial_contract": (
                "turnlock.sqc:UniqueCorrectionInitial@1"
            ),
        }
    ):
        raise ValueError(
            "inactive protocol v8 E3-C3: Discovery decision revision topology mismatch"
        )
    return {
        "challenge_id": challenge_id,
        "challenge": challenge_contract,
        "revision_id": revision_id,
        "revision": revision_contract,
        "challenge_metadata": challenge,
        "revision_metadata": revision,
    }


def _protocol_v8_e3c3_admission_context(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    admission_ref: object,
) -> dict:
    validators = closure.get("_e3b_output_validators")
    if not isinstance(validators, dict):
        validators, validator_errors = _protocol_v8_e1_output_validators(root)
        if validator_errors:
            raise ValueError(
                f"inactive protocol v8 E3-C3: {validator_errors[0]}"
            )
        closure["_e3b_output_validators"] = validators
    return _protocol_v8_e3b_admission_context(
        root, closure, contracts, admission_ref, validators
    )


def _protocol_v8_e3c3_targeted_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    descriptor: dict,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Resolve C1 targets plus the exact decision-required revision target."""
    c1_rules, c1_errors = _protocol_v8_e3c1_rule_map(predicates)
    if c1_errors:
        raise ValueError(c1_errors[0])
    predicate = c1_rules["targeted-discovery-statement"]
    if descriptor.get("predicateRevision") != predicate.get("revision_id"):
        return False
    arguments = descriptor.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) != {
        "producerDiscovery",
        "statement",
    }:
        raise ValueError(
            "inactive protocol v8 E3-C3: Targeted descriptor arguments mismatch"
        )
    producer = _protocol_v8_e3c3_admission_context(
        root, closure, contracts, arguments["producerDiscovery"]
    )
    if producer["contract_id"] != "turnlock.sqc:DiscoveryDecisionRequiredRevision@1":
        return _protocol_v8_e3c1_targeted_discovery_truth(
            root,
            closure,
            contracts,
            predicates,
            descriptor,
            require_current_consumability=require_current_consumability,
            active=active,
        )
    topology = _protocol_v8_e3c3_topology(contracts)
    if require_current_consumability and not producer["currently_consumable"]:
        return False
    candidate = producer.get("candidate")
    if candidate == {"kind": "not-established"}:
        return False
    if not isinstance(candidate, dict) or set(candidate) != {"kind", "statement"}:
        raise ValueError(
            "inactive protocol v8 E3-C3: decision revision candidate shape mismatch"
        )
    if candidate.get("kind") != "revised-candidate":
        raise ValueError(
            "inactive protocol v8 E3-C3: decision revision candidate kind mismatch"
        )
    statement = candidate.get("statement")
    if _protocol_v8_e1_canonical_json_value_bytes(statement) != (
        _protocol_v8_e1_canonical_json_value_bytes(arguments["statement"])
    ):
        return False
    required_disposition = topology["revision_metadata"].get(
        "required_positive_disposition"
    )
    if _mapping(statement).get("semantic_disposition") != required_disposition:
        raise ValueError(
            "inactive protocol v8 E3-C3: revised statement disposition mismatch"
        )
    exact_input = _mapping(producer["descriptor"]).get("exactLogicalInput")
    if not isinstance(exact_input, dict) or set(exact_input) != {
        "survivingMaterialBasis",
        "priorDecisionRequiredStatement",
        "priorDecisionNecessityCandidate",
        "priorDecisionNecessityChallenge",
    }:
        raise ValueError(
            "inactive protocol v8 E3-C3: decision revision exact input mismatch"
        )
    surviving_ref = exact_input["survivingMaterialBasis"]
    surviving = _protocol_v8_e3a_resolve_semantic_value(closure, surviving_ref)
    if surviving.get("valueType") != (
        "turnlock.semantic-value:SurvivingMaterialBasis@1"
    ):
        return False
    decision_ref = exact_input["priorDecisionRequiredStatement"]
    candidate_ref = exact_input["priorDecisionNecessityCandidate"]
    decision = _protocol_v8_e3c3_dependency_status(
        root, closure, contracts, predicates, qualifications, decision_ref,
        active=active,
    )
    necessity = _protocol_v8_e3c3_dependency_status(
        root, closure, contracts, predicates, qualifications, candidate_ref,
        active=active,
    )
    if not decision["reconstructible"] or not necessity["reconstructible"]:
        return False
    if decision["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:DecisionRequiredDiscoveryStatement@1"
    ) or necessity["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:DecisionNecessityCandidate@1"
    ):
        return False
    if require_current_consumability and (
        not decision["consumable"] or not necessity["consumable"]
    ):
        return False
    necessity_arguments = _mapping(necessity["descriptor"].get("arguments"))
    if necessity_arguments.get("survivingMaterialBasis") != surviving_ref or (
        necessity_arguments.get("decisionRequiredStatement") != decision_ref
    ):
        return False
    exhaustion_ref = necessity_arguments.get("uniqueCorrectionExhaustion")
    exhaustion = _protocol_v8_e3c3_dependency_status(
        root, closure, contracts, predicates, qualifications, exhaustion_ref,
        active=active,
    )
    if not exhaustion["reconstructible"]:
        return False
    if exhaustion["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:UniqueCorrectionExhaustion@1"
    ):
        return False
    if require_current_consumability and not exhaustion["consumable"]:
        return False
    challenge = _protocol_v8_e3c3_admission_context(
        root,
        closure,
        contracts,
        exact_input["priorDecisionNecessityChallenge"],
    )
    expected_challenge_input = {
        "survivingMaterialBasis": copy.deepcopy(surviving_ref),
        "decisionRequiredStatement": copy.deepcopy(decision_ref),
        "uniqueCorrectionExhaustion": copy.deepcopy(exhaustion_ref),
        "decisionNecessityCandidate": copy.deepcopy(candidate_ref),
    }
    if challenge["contract_id"] != topology["challenge_id"] or (
        _mapping(challenge["descriptor"]).get("exactLogicalInput")
        != expected_challenge_input
    ):
        return False
    objections = _mapping(challenge.get("candidate")).get("objections")
    if not isinstance(objections, list) or not objections:
        return False
    if require_current_consumability and not challenge["currently_consumable"]:
        return False
    decision_arguments = _mapping(decision["descriptor"].get("arguments"))
    prior_target_ref = decision_arguments.get("targetedDiscoveryStatement")
    prior_target = _protocol_v8_e3c3_dependency_status(
        root, closure, contracts, predicates, qualifications, prior_target_ref,
        active=active,
    )
    if not prior_target["reconstructible"]:
        return False
    if require_current_consumability and not prior_target["consumable"]:
        return False
    prior_producer_ref = _mapping(prior_target["descriptor"].get("arguments")).get(
        "producerDiscovery"
    )
    prior_producer = _protocol_v8_e3c3_admission_context(
        root, closure, contracts, prior_producer_ref
    )
    trigger_contracts = topology["challenge_metadata"].get(
        "revision_trigger_producer_contracts"
    )
    return prior_producer["contract_id"] in trigger_contracts


def _protocol_v8_e3c3_decision_required_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    descriptor: dict,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Resolve DecisionRequired over either C1 or C3 Targeted Facts."""
    c1_rules, c1_errors = _protocol_v8_e3c1_rule_map(predicates)
    if c1_errors:
        raise ValueError(c1_errors[0])
    predicate = c1_rules["decision-required-discovery-statement"]
    if descriptor.get("predicateRevision") != predicate.get("revision_id"):
        return False
    arguments = descriptor.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) != {
        "targetedDiscoveryStatement"
    }:
        raise ValueError(
            "inactive protocol v8 E3-C3: DecisionRequired arguments mismatch"
        )
    target_ref = arguments["targetedDiscoveryStatement"]
    target_descriptor = _protocol_v8_e3a_resolve_fact_identity(
        closure, target_ref
    )
    producer_ref = _mapping(target_descriptor.get("arguments")).get(
        "producerDiscovery"
    )
    producer = _protocol_v8_e3c3_admission_context(
        root, closure, contracts, producer_ref
    )
    if producer["contract_id"] != "turnlock.sqc:DiscoveryDecisionRequiredRevision@1":
        return _protocol_v8_e3c1_decision_required_truth(
            root,
            closure,
            contracts,
            predicates,
            descriptor,
            require_current_consumability=require_current_consumability,
            active=active,
        )
    target = _protocol_v8_e3c3_dependency_status(
        root,
        closure,
        contracts,
        predicates,
        qualifications,
        target_ref,
        active=active,
    )
    if target["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:TargetedDiscoveryStatement@1"
    ) or not target["reconstructible"]:
        return False
    if require_current_consumability and not target["consumable"]:
        return False
    statement = _mapping(
        _mapping(target["descriptor"].get("arguments")).get("statement")
    )
    derivation = _mapping(_mapping(predicate.get("definition")).get("derivation"))
    allowed = derivation.get("allowed_basis_kinds")
    if statement.get("semantic_disposition") != derivation.get(
        "required_disposition"
    ):
        return False
    basis = statement.get("disposition_basis")
    return isinstance(basis, dict) and basis.get("kind") in allowed


def _protocol_v8_e3c3_unique_correction_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    descriptor: dict,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Bridge C2 exhaustion only when the exact Target is C3-produced."""
    c2_rules, c2_errors = _protocol_v8_e3c2_rule_map(predicates)
    if c2_errors:
        raise ValueError(c2_errors[0])
    predicate = c2_rules["unique-correction-exhaustion"]
    if descriptor.get("predicateRevision") != predicate.get("revision_id"):
        return False
    arguments = descriptor.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) != {
        "targetedDiscoveryStatement"
    }:
        raise ValueError(
            "inactive protocol v8 E3-C3: UniqueCorrection arguments mismatch"
        )
    target_ref = arguments["targetedDiscoveryStatement"]
    target_descriptor = _protocol_v8_e3a_resolve_fact_identity(closure, target_ref)
    producer_ref = _mapping(target_descriptor.get("arguments")).get(
        "producerDiscovery"
    )
    producer = _protocol_v8_e3c3_admission_context(
        root, closure, contracts, producer_ref
    )
    if producer["contract_id"] != "turnlock.sqc:DiscoveryDecisionRequiredRevision@1":
        return _protocol_v8_e3c2_unique_correction_truth(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            descriptor,
            require_current_consumability=require_current_consumability,
            active=active,
        )
    target = _protocol_v8_e3c3_dependency_status(
        root, closure, contracts, predicates, qualifications, target_ref,
        active=active,
    )
    if not target["reconstructible"]:
        return False
    if require_current_consumability and not target["consumable"]:
        return False
    producer_input = _mapping(producer["descriptor"]).get("exactLogicalInput")
    if not isinstance(producer_input, dict) or "survivingMaterialBasis" not in producer_input:
        raise ValueError(
            "inactive protocol v8 E3-C3: revised Discovery lacks SurvivingMaterialBasis"
        )
    family = _protocol_v8_e3c2_family_contracts(
        contracts,
        "unique-correction",
        initial_inputs=[
            "discovery",
            "survivingMaterialBasis",
            "targetedDiscoveryStatement",
        ],
        challenge_target="challengedUniqueCorrection",
        revision_inputs=[
            "discovery",
            "priorUniqueCorrection",
            "priorUniqueCorrectionChallenge",
            "survivingMaterialBasis",
            "targetedDiscoveryStatement",
        ],
        retained_inputs=[
            "discovery",
            "survivingMaterialBasis",
            "targetedDiscoveryStatement",
        ],
        prior_candidate_input="priorUniqueCorrection",
        prior_challenge_input="priorUniqueCorrectionChallenge",
    )
    terminal = _protocol_v8_e3c2_terminal_branches(
        root,
        closure,
        contracts,
        family,
        {
            "discovery": copy.deepcopy(producer_ref),
            "survivingMaterialBasis": copy.deepcopy(
                producer_input["survivingMaterialBasis"]
            ),
            "targetedDiscoveryStatement": copy.deepcopy(target_ref),
        },
        require_current_consumability=require_current_consumability,
    )
    if not terminal["established"]:
        return False
    if require_current_consumability:
        contradictory = _protocol_v8_e3c2_current_qualification_contradiction(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            "turnlock.predicate:AcceptedUniqueCorrection@1",
            terminal["positive_admission_ids"],
            active=active,
        )
        _protocol_v8_e3c2_reject_current_contradiction(
            True, contradictory, "UniqueCorrection"
        )
    return True


def _protocol_v8_e3c3_decision_necessity_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    descriptor: dict,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Reduce exact S/D/U cross-binding to DecisionNecessityCandidate."""
    rules, rule_errors = _protocol_v8_e3c3_rule_map(predicates)
    if rule_errors:
        raise ValueError(rule_errors[0])
    predicate = rules["decision-necessity-candidate"]
    if descriptor.get("predicateRevision") != predicate.get("revision_id"):
        return False
    arguments = descriptor.get("arguments")
    if not isinstance(arguments, dict) or set(arguments) != {
        "survivingMaterialBasis",
        "decisionRequiredStatement",
        "uniqueCorrectionExhaustion",
    }:
        raise ValueError(
            "inactive protocol v8 E3-C3: DecisionNecessity descriptor mismatch"
        )
    surviving_ref = arguments["survivingMaterialBasis"]
    surviving = _protocol_v8_e3a_resolve_semantic_value(closure, surviving_ref)
    if surviving.get("valueType") != (
        "turnlock.semantic-value:SurvivingMaterialBasis@1"
    ):
        return False
    decision_ref = arguments["decisionRequiredStatement"]
    exhaustion_ref = arguments["uniqueCorrectionExhaustion"]
    decision = _protocol_v8_e3c3_dependency_status(
        root, closure, contracts, predicates, qualifications, decision_ref,
        active=active,
    )
    exhaustion = _protocol_v8_e3c3_dependency_status(
        root, closure, contracts, predicates, qualifications, exhaustion_ref,
        active=active,
    )
    if not decision["reconstructible"] or not exhaustion["reconstructible"]:
        return False
    if require_current_consumability and (
        not decision["consumable"] or not exhaustion["consumable"]
    ):
        return False
    if decision["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:DecisionRequiredDiscoveryStatement@1"
    ) or exhaustion["descriptor"].get("predicateRevision") != (
        "turnlock.predicate:UniqueCorrectionExhaustion@1"
    ):
        return False
    target_ref = _mapping(decision["descriptor"].get("arguments")).get(
        "targetedDiscoveryStatement"
    )
    target = _protocol_v8_e3c3_dependency_status(
        root, closure, contracts, predicates, qualifications, target_ref,
        active=active,
    )
    if not target["reconstructible"]:
        return False
    if require_current_consumability and not target["consumable"]:
        return False
    target_arguments = _mapping(target["descriptor"].get("arguments"))
    if _mapping(exhaustion["descriptor"].get("arguments")).get(
        "targetedDiscoveryStatement"
    ) != target_ref:
        return False
    producer = _protocol_v8_e3c3_admission_context(
        root, closure, contracts, target_arguments.get("producerDiscovery")
    )
    producer_input = _mapping(producer["descriptor"]).get("exactLogicalInput")
    if not isinstance(producer_input, dict) or (
        producer_input.get("survivingMaterialBasis") != surviving_ref
    ):
        return False
    if require_current_consumability and not producer["currently_consumable"]:
        return False
    return True


def _protocol_v8_e3c3_fact_truth(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    descriptor: dict,
    *,
    require_current_consumability: bool,
    active: set[str],
) -> bool:
    """Dispatch only the four C3 loop Predicate kinds."""
    predicate_id = descriptor.get("predicateRevision")
    if predicate_id == "turnlock.predicate:TargetedDiscoveryStatement@1":
        return _protocol_v8_e3c3_targeted_truth(
            root, closure, contracts, predicates, qualifications, descriptor,
            require_current_consumability=require_current_consumability,
            active=active,
        )
    if predicate_id == "turnlock.predicate:DecisionRequiredDiscoveryStatement@1":
        return _protocol_v8_e3c3_decision_required_truth(
            root, closure, contracts, predicates, qualifications, descriptor,
            require_current_consumability=require_current_consumability,
            active=active,
        )
    if predicate_id == "turnlock.predicate:UniqueCorrectionExhaustion@1":
        return _protocol_v8_e3c3_unique_correction_truth(
            root, closure, contracts, predicates, qualifications, descriptor,
            require_current_consumability=require_current_consumability,
            active=active,
        )
    if predicate_id == "turnlock.predicate:DecisionNecessityCandidate@1":
        return _protocol_v8_e3c3_decision_necessity_truth(
            root, closure, contracts, predicates, qualifications, descriptor,
            require_current_consumability=require_current_consumability,
            active=active,
        )
    raise ValueError(
        "inactive protocol v8 E3-C3: unsupported root Predicate"
    )


def _protocol_v8_e3c3_fact_status(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    fact_ref: object,
    *,
    active: set[str] | None = None,
    _memo: dict[str, dict] | None = None,
    _graph_checked: set[str] | None = None,
) -> dict:
    """Resolve historical/current truth for exactly the C3 loop Predicates."""
    descriptor = _protocol_v8_e3a_resolve_fact_identity(closure, fact_ref)
    assert isinstance(fact_ref, dict)
    fact_id = fact_ref["factId"]
    stack = active if active is not None else set()
    if fact_id in stack:
        raise ValueError(
            "inactive protocol v8 E3-C3: unlawful semantic Fact reducer cycle"
        )
    # These maps live only for one synchronous resolution. They avoid repeating
    # exact identity/graph work and never become semantic or persistent authority.
    memo = _memo if _memo is not None else {}
    graph_checked = _graph_checked if _graph_checked is not None else set()
    cached = memo.get(fact_id)
    if isinstance(cached, dict):
        return copy.deepcopy(cached)
    if fact_id not in graph_checked:
        _protocol_v8_e3a_resolve_dependency_graph(
            closure, contracts, [("semantic-fact", fact_id)]
        )
        graph_checked.add(fact_id)
    stack.add(fact_id)
    closure["_e3c3_ephemeral_resolution"] = {
        "memo": memo,
        "graph_checked": graph_checked,
    }
    try:
        reconstructible = _protocol_v8_e3c3_fact_truth(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            descriptor,
            require_current_consumability=False,
            active=stack,
        )
        consumable = False
        if reconstructible:
            consumable = _protocol_v8_e3c3_fact_truth(
                root,
                closure,
                contracts,
                predicates,
                qualifications,
                descriptor,
                require_current_consumability=True,
                active=stack,
            )
    finally:
        stack.remove(fact_id)
        if active is None:
            closure.pop("_e3c3_ephemeral_resolution", None)
    result = {
        "reference": copy.deepcopy(fact_ref),
        "descriptor": descriptor,
        "reconstructible": bool(reconstructible),
        "consumable": bool(consumable),
    }
    memo[fact_id] = copy.deepcopy(result)
    return result


def _protocol_v8_e3c3_dependency_status(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    fact_ref: object,
    *,
    active: set[str],
) -> dict:
    """Resolve only the exact recursive Fact kinds required by the C3 loop."""
    descriptor = _protocol_v8_e3a_resolve_fact_identity(closure, fact_ref)
    if descriptor.get("predicateRevision") not in {
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        "turnlock.predicate:DecisionRequiredDiscoveryStatement@1",
        "turnlock.predicate:UniqueCorrectionExhaustion@1",
        "turnlock.predicate:DecisionNecessityCandidate@1",
    }:
        raise ValueError(
            "inactive protocol v8 E3-C3: unsupported C3 Fact dependency"
        )
    ephemeral = closure.get("_e3c3_ephemeral_resolution")
    memo = _mapping(ephemeral).get("memo")
    graph_checked = _mapping(ephemeral).get("graph_checked")
    return _protocol_v8_e3c3_fact_status(
        root,
        closure,
        contracts,
        predicates,
        qualifications,
        fact_ref,
        active=active,
        _memo=memo if isinstance(memo, dict) else None,
        _graph_checked=(
            graph_checked if isinstance(graph_checked, set) else None
        ),
    )


def _protocol_v8_e3c3_claimed_fact_dependency(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    fact_ref: object,
    *,
    _memo: dict[str, dict] | None = None,
    _graph_checked: set[str] | None = None,
) -> dict:
    """Adapt C3 status to E3-B's exact claimed-Fact dependency contract."""
    status = _protocol_v8_e3c3_fact_status(
        root,
        closure,
        contracts,
        predicates,
        qualifications,
        fact_ref,
        _memo=_memo,
        _graph_checked=_graph_checked,
    )
    if status["reconstructible"] is not True:
        raise ValueError(
            "inactive protocol v8 E3-C3: claimed Fact dependency is not reconstructible"
        )
    return status


def _protocol_v8_e3c3_decision_necessity_view(
    root: Path,
    closure: dict,
    contracts: dict[str, dict],
    predicates: dict[str, dict],
    qualifications: dict[str, dict],
    fact_ref: object,
) -> dict:
    """Project the exact disposition basis without changing Fact identity."""
    status = _protocol_v8_e3c3_fact_status(
        root, closure, contracts, predicates, qualifications, fact_ref
    )
    if not status["reconstructible"] or status["descriptor"].get(
        "predicateRevision"
    ) != "turnlock.predicate:DecisionNecessityCandidate@1":
        raise ValueError(
            "inactive protocol v8 E3-C3: semantic view requires valid DecisionNecessity"
        )
    decision_ref = _mapping(status["descriptor"].get("arguments")).get(
        "decisionRequiredStatement"
    )
    decision = _protocol_v8_e3c3_fact_status(
        root, closure, contracts, predicates, qualifications, decision_ref
    )
    target_ref = _mapping(decision["descriptor"].get("arguments")).get(
        "targetedDiscoveryStatement"
    )
    target = _protocol_v8_e3c3_fact_status(
        root, closure, contracts, predicates, qualifications, target_ref
    )
    statement = _mapping(_mapping(target["descriptor"].get("arguments")).get("statement"))
    return {
        "kind": "decision-necessity-candidate",
        "basis": copy.deepcopy(statement.get("disposition_basis")),
    }


def _inactive_protocol_v8_e3c3_decision_necessity_errors(
    root: Path,
) -> list[str]:
    """Exercise the exact C3 DecisionNecessity closure in disposable state."""
    errors: list[str] = []
    predicates, qualifications, catalog_errors = _protocol_v8_e3a_catalog_maps(root)
    contracts, contract_errors = _protocol_v8_e1_contract_map(root)
    validators, validator_errors = _protocol_v8_e1_output_validators(root)
    errors.extend(catalog_errors)
    errors.extend(contract_errors)
    errors.extend(validator_errors)
    rules, rule_errors = _protocol_v8_e3c3_rule_map(predicates)
    errors.extend(rule_errors)
    try:
        topology = _protocol_v8_e3c3_topology(contracts)
    except ValueError as error:
        errors.append(str(error))
        return errors
    if errors:
        return errors

    decision_statement = {
        "statement": "current authority leaves two materially distinct outcomes",
        "evidence_references": [{"kind": "source-finding"}],
        "evidence_argument": "the exact evidence exposes the unresolved choice",
        "existing_authority": [],
        "affected_layers": ["normative-contract"],
        "semantic_disposition": "decision-required",
        "disposition_basis": {
            "kind": "product-underdetermination",
            "alternatives": [
                {
                    "alternative": "A",
                    "authority_compatibility_argument": "A is authority-compatible",
                },
                {
                    "alternative": "B",
                    "authority_compatibility_argument": "B is authority-compatible",
                },
            ],
            "material_distinction_argument": "A and B differ materially",
            "current_authority_non_selection_argument": "authority selects neither",
        },
    }
    revised_statement = copy.deepcopy(decision_statement)
    revised_statement["statement"] = "revised authority still leaves two outcomes"
    sibling_statement = {
        "statement": "a downstream correction has no normative impact",
        "evidence_references": [{"kind": "source-finding"}],
        "evidence_argument": "the exact evidence establishes downstream scope",
        "existing_authority": [],
        "affected_layers": ["architecture-or-implementation"],
        "semantic_disposition": "no-normative-impact",
        "disposition_basis": {
            "new_product_authority_not_required_argument": "no new authority",
            "changed_product_authority_not_required_argument": "no changed authority",
            "product_meaning_selection_not_required_argument": "no meaning choice",
            "accepted_observable_obligation_change_not_required_argument": (
                "no accepted obligation changes"
            ),
        },
    }

    def new_closure() -> dict:
        closure = _protocol_v8_e3a_new_closure(_protocol_v8_e2_new_state())
        closure["_e3b_output_validators"] = validators
        return closure

    def admit(closure: dict, contract_id: str, logical_input: dict, candidate: object) -> dict:
        return _protocol_v8_e3b_test_admit(
            closure, contracts, contract_id, logical_input, candidate
        )

    def fact(closure: dict, predicate_id: str, arguments: dict) -> dict:
        return _protocol_v8_e3b_test_fact(
            closure, predicates, predicate_id, arguments
        )

    def discovery_candidate(statements: list[dict]) -> dict:
        return {
            "earliest_unresolved_cause": {
                "classification_statement_ordinal": 0,
                "evidence_references": [{"kind": "source-finding"}],
                "causal_explanation": "the decision statement is earliest",
                "upstream_exclusion_argument": "no earlier cause exists",
            },
            "classification_statements": copy.deepcopy(statements),
        }

    def challenge_candidate(contract_id: str, zero: bool) -> dict:
        return _protocol_v8_e3b_test_challenge_candidate(
            contracts[contract_id], zero
        )

    def status(closure: dict, reference: dict) -> dict:
        return _protocol_v8_e3c3_fact_status(
            root, closure, contracts, predicates, qualifications, reference
        )

    def expect_true(label: str, closure: dict, reference: dict) -> dict | None:
        try:
            result = status(closure, reference)
        except ValueError as error:
            errors.append(f"inactive protocol v8 E3-C3: {label} raised: {error}")
            return None
        if not result["reconstructible"] or not result["consumable"]:
            errors.append(f"inactive protocol v8 E3-C3: {label} did not reduce")
        return result

    def expect_false(label: str, closure: dict, reference: dict) -> None:
        try:
            result = status(closure, reference)
        except ValueError as error:
            errors.append(f"inactive protocol v8 E3-C3: {label} raised: {error}")
            return
        if result["reconstructible"] or result["consumable"]:
            errors.append(f"inactive protocol v8 E3-C3: {label} became true")

    def expect_rejected(label: str, action, required: str | None = None) -> None:
        try:
            action()
        except ValueError as error:
            if required is not None and required not in str(error):
                errors.append(
                    f"inactive protocol v8 E3-C3: {label} rejected without {required!r}"
                )
            return
        errors.append(f"inactive protocol v8 E3-C3: expected rejection: {label}")

    def make_target(
        closure: dict,
        surviving_ref: dict,
        statement_value: dict,
        label: str,
        *,
        siblings: list[dict] | None = None,
    ) -> tuple[dict, dict, dict]:
        producer = admit(
            closure,
            "turnlock.sqc:DiscoveryClassificationInitial@1",
            {"survivingMaterialBasis": surviving_ref},
            discovery_candidate([statement_value] + list(siblings or [])),
        )
        targeted = fact(
            closure,
            "turnlock.predicate:TargetedDiscoveryStatement@1",
            {"producerDiscovery": producer, "statement": statement_value},
        )
        decision = fact(
            closure,
            "turnlock.predicate:DecisionRequiredDiscoveryStatement@1",
            {"targetedDiscoveryStatement": targeted},
        )
        return producer, targeted, decision

    def make_exhaustion(
        closure: dict,
        surviving_ref: dict,
        producer_ref: dict,
        targeted_ref: dict,
    ) -> dict:
        admit(
            closure,
            "turnlock.sqc:UniqueCorrectionInitial@1",
            {
                "discovery": producer_ref,
                "survivingMaterialBasis": surviving_ref,
                "targetedDiscoveryStatement": targeted_ref,
            },
            {"kind": "not-established"},
        )
        return fact(
            closure,
            "turnlock.predicate:UniqueCorrectionExhaustion@1",
            {"targetedDiscoveryStatement": targeted_ref},
        )

    def make_necessity(
        closure: dict,
        surviving_ref: dict,
        decision_ref: dict,
        exhaustion_ref: dict,
    ) -> dict:
        return fact(
            closure,
            rules["decision-necessity-candidate"]["revision_id"],
            {
                "survivingMaterialBasis": surviving_ref,
                "decisionRequiredStatement": decision_ref,
                "uniqueCorrectionExhaustion": exhaustion_ref,
            },
        )

    def make_dn_challenge(
        closure: dict,
        surviving_ref: dict,
        decision_ref: dict,
        exhaustion_ref: dict,
        necessity_ref: dict,
        *,
        zero: bool,
    ) -> dict:
        return admit(
            closure,
            topology["challenge_id"],
            {
                "survivingMaterialBasis": surviving_ref,
                "decisionRequiredStatement": decision_ref,
                "uniqueCorrectionExhaustion": exhaustion_ref,
                "decisionNecessityCandidate": necessity_ref,
            },
            challenge_candidate(topology["challenge_id"], zero),
        )

    def reduce_qualification(
        closure: dict,
        qualification_ref: dict,
    ) -> dict | None:
        memo: dict[str, dict] = {}
        graph_checked: set[str] = set()
        return _protocol_v8_e3b_reduce_qualification(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            qualification_ref,
            fact_dependency_resolver=lambda reference: (
                _protocol_v8_e3c3_claimed_fact_dependency(
                    root,
                    closure,
                    contracts,
                    predicates,
                    qualifications,
                    reference,
                    _memo=memo,
                    _graph_checked=graph_checked,
                )
            ),
            require_current_consumability=True,
        )

    def make_qualification(
        closure: dict,
        producer_ref: dict,
        surviving_ref: dict,
        decision_ref: dict,
        exhaustion_ref: dict,
        necessity_ref: dict,
        challenge_ref: dict,
    ) -> dict:
        return _protocol_v8_e3b_test_qualification(
            closure,
            qualifications,
            "turnlock.qualification:DecisionNecessityQualification@1",
            producer_ref,
            {
                "survivingMaterialBasis": surviving_ref,
                "decisionRequiredStatement": decision_ref,
                "uniqueCorrectionExhaustion": exhaustion_ref,
                "decisionNecessityCandidate": necessity_ref,
                "decisionNecessityChallenge": challenge_ref,
            },
        )

    closure = new_closure()
    surviving = _protocol_v8_e3a_register_semantic_value(
        closure,
        "turnlock.semantic-value:SurvivingMaterialBasis@1",
        {"test": "e3-c3-surviving-0"},
    )
    producer0, target0, decision0 = make_target(
        closure,
        surviving,
        decision_statement,
        "initial",
        siblings=[sibling_statement],
    )
    sibling_target = fact(
        closure,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": producer0, "statement": sibling_statement},
    )
    exhaustion0 = make_exhaustion(closure, surviving, producer0, target0)
    necessity0 = make_necessity(closure, surviving, decision0, exhaustion0)
    for label, reference in (
        ("initial Targeted", target0),
        ("initial DecisionRequired", decision0),
        ("initial UniqueCorrection exhaustion", exhaustion0),
        ("initial DecisionNecessity", necessity0),
    ):
        expect_true(label, closure, reference)

    view = _protocol_v8_e3c3_decision_necessity_view(
        root, closure, contracts, predicates, qualifications, necessity0
    )
    expected_view = {
        "kind": "decision-necessity-candidate",
        "basis": copy.deepcopy(decision_statement["disposition_basis"]),
    }
    if _protocol_v8_e1_canonical_json_value_bytes(view) != (
        _protocol_v8_e1_canonical_json_value_bytes(expected_view)
    ):
        errors.append("inactive protocol v8 E3-C3: semantic view mismatch")
    necessity0_descriptor = _protocol_v8_e3a_resolve_fact_identity(
        closure, necessity0
    )
    if "basis" in necessity0_descriptor or set(
        _mapping(necessity0_descriptor.get("arguments"))
    ) != {
        "survivingMaterialBasis",
        "decisionRequiredStatement",
        "uniqueCorrectionExhaustion",
    }:
        errors.append("inactive protocol v8 E3-C3: semantic view entered Fact identity")

    other_surviving = _protocol_v8_e3a_register_semantic_value(
        closure,
        "turnlock.semantic-value:SurvivingMaterialBasis@1",
        {"test": "e3-c3-surviving-other"},
    )
    wrong_s = make_necessity(closure, other_surviving, decision0, exhaustion0)
    expect_false("wrong SurvivingMaterialBasis", closure, wrong_s)
    other_statement = copy.deepcopy(decision_statement)
    other_statement["statement"] = "another exact decision statement"
    other_producer, other_target, other_decision = make_target(
        closure, other_surviving, other_statement, "other"
    )
    other_exhaustion = make_exhaustion(
        closure, other_surviving, other_producer, other_target
    )
    wrong_d = make_necessity(closure, surviving, other_decision, exhaustion0)
    wrong_u = make_necessity(closure, surviving, decision0, other_exhaustion)
    expect_false("wrong DecisionRequired Fact", closure, wrong_d)
    expect_false("wrong UniqueCorrection target", closure, wrong_u)
    expect_true("non-decision sibling remains Targeted", closure, sibling_target)
    sibling_fact_ids = {
        item.get("predicateRevision")
        for descriptors in closure["fact_descriptors"].values()
        for item in descriptors
        if isinstance(item, dict)
        and _mapping(item.get("arguments")).get("targetedDiscoveryStatement")
        == sibling_target
    }
    if "turnlock.predicate:DecisionRequiredDiscoveryStatement@1" in sibling_fact_ids:
        errors.append(
            "inactive protocol v8 E3-C3: oracle invented DecisionRequired for NNI target"
        )

    zero_closure = copy.deepcopy(closure)
    zero_challenge = make_dn_challenge(
        zero_closure,
        surviving,
        decision0,
        exhaustion0,
        necessity0,
        zero=True,
    )
    zero_qualification = make_qualification(
        zero_closure,
        producer0,
        surviving,
        decision0,
        exhaustion0,
        necessity0,
        zero_challenge,
    )
    zero_result = reduce_qualification(zero_closure, zero_qualification)
    if zero_result is None or zero_result["fact"]["predicateRevision"] != (
        "turnlock.predicate:QualifiedDecisionNecessity@1"
    ):
        errors.append(
            "inactive protocol v8 E3-C3: zero-objection qualification did not reduce"
        )
    zero_revision = admit(
        zero_closure,
        topology["revision_id"],
        {
            "survivingMaterialBasis": surviving,
            "priorDecisionRequiredStatement": decision0,
            "priorDecisionNecessityCandidate": necessity0,
            "priorDecisionNecessityChallenge": zero_challenge,
        },
        {"kind": "revised-candidate", "statement": revised_statement},
    )
    zero_target = fact(
        zero_closure,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": zero_revision, "statement": revised_statement},
    )
    expect_false("zero-objection revision", zero_closure, zero_target)

    objection_closure = copy.deepcopy(closure)
    objection_challenge = make_dn_challenge(
        objection_closure,
        surviving,
        decision0,
        exhaustion0,
        necessity0,
        zero=False,
    )
    objection_qualification = make_qualification(
        objection_closure,
        producer0,
        surviving,
        decision0,
        exhaustion0,
        necessity0,
        objection_challenge,
    )
    if reduce_qualification(objection_closure, objection_qualification) is not None:
        errors.append(
            "inactive protocol v8 E3-C3: objections derived QualifiedDecisionNecessity"
        )
    pre_revision_closure = copy.deepcopy(objection_closure)
    revision1 = admit(
        objection_closure,
        topology["revision_id"],
        {
            "survivingMaterialBasis": surviving,
            "priorDecisionRequiredStatement": decision0,
            "priorDecisionNecessityCandidate": necessity0,
            "priorDecisionNecessityChallenge": objection_challenge,
        },
        {"kind": "revised-candidate", "statement": revised_statement},
    )
    target1 = fact(
        objection_closure,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": revision1, "statement": revised_statement},
    )
    decision1 = fact(
        objection_closure,
        "turnlock.predicate:DecisionRequiredDiscoveryStatement@1",
        {"targetedDiscoveryStatement": target1},
    )
    target1_status = expect_true("revised Targeted", objection_closure, target1)
    decision1_status = expect_true(
        "revised DecisionRequired", objection_closure, decision1
    )
    if target1_status is not None and _mapping(
        target1_status["descriptor"].get("arguments")
    ).get("producerDiscovery") != revision1:
        errors.append("inactive protocol v8 E3-C3: revised Target producer mismatch")
    if decision1_status is not None and _mapping(
        decision1_status["descriptor"].get("arguments")
    ).get("targetedDiscoveryStatement") != target1:
        errors.append("inactive protocol v8 E3-C3: revised Decision target mismatch")

    wrong_disposition_closure = copy.deepcopy(pre_revision_closure)
    wrong_statement = copy.deepcopy(sibling_statement)
    wrong_statement["statement"] = "wrong positive revision disposition"
    wrong_revision = admit(
        wrong_disposition_closure,
        topology["revision_id"],
        {
            "survivingMaterialBasis": surviving,
            "priorDecisionRequiredStatement": decision0,
            "priorDecisionNecessityCandidate": necessity0,
            "priorDecisionNecessityChallenge": objection_challenge,
        },
        {"kind": "revised-candidate", "statement": wrong_statement},
    )
    wrong_target = fact(
        wrong_disposition_closure,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": wrong_revision, "statement": wrong_statement},
    )
    expect_rejected(
        "wrong revised disposition",
        lambda: status(wrong_disposition_closure, wrong_target),
        "disposition mismatch",
    )

    withdrawn_closure = copy.deepcopy(pre_revision_closure)
    withdrawn_revision = admit(
        withdrawn_closure,
        topology["revision_id"],
        {
            "survivingMaterialBasis": surviving,
            "priorDecisionRequiredStatement": decision0,
            "priorDecisionNecessityCandidate": necessity0,
            "priorDecisionNecessityChallenge": objection_challenge,
        },
        {"kind": "not-established"},
    )
    withdrawn_target = fact(
        withdrawn_closure,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": withdrawn_revision, "statement": revised_statement},
    )
    expect_false("NotEstablished decision revision", withdrawn_closure, withdrawn_target)

    wrong_prior_n_closure = copy.deepcopy(pre_revision_closure)
    wrong_prior_revision = admit(
        wrong_prior_n_closure,
        topology["revision_id"],
        {
            "survivingMaterialBasis": surviving,
            "priorDecisionRequiredStatement": decision0,
            "priorDecisionNecessityCandidate": wrong_s,
            "priorDecisionNecessityChallenge": objection_challenge,
        },
        {"kind": "revised-candidate", "statement": revised_statement},
    )
    wrong_prior_target = fact(
        wrong_prior_n_closure,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": wrong_prior_revision, "statement": revised_statement},
    )
    expect_false("wrong prior DecisionNecessity", wrong_prior_n_closure, wrong_prior_target)

    challenge_mismatch_base = copy.deepcopy(closure)
    other_necessity = make_necessity(
        challenge_mismatch_base,
        other_surviving,
        other_decision,
        other_exhaustion,
    )
    challenge_variants = {
        "S": (other_surviving, decision0, exhaustion0, necessity0),
        "D": (surviving, other_decision, exhaustion0, necessity0),
        "U": (surviving, decision0, other_exhaustion, necessity0),
        "N": (surviving, decision0, exhaustion0, other_necessity),
    }
    for label, challenge_inputs in challenge_variants.items():
        wrong_challenge_closure = copy.deepcopy(challenge_mismatch_base)
        other_challenge = make_dn_challenge(
            wrong_challenge_closure,
            *challenge_inputs,
            zero=False,
        )
        mismatched_revision = admit(
            wrong_challenge_closure,
            topology["revision_id"],
            {
                "survivingMaterialBasis": surviving,
                "priorDecisionRequiredStatement": decision0,
                "priorDecisionNecessityCandidate": necessity0,
                "priorDecisionNecessityChallenge": other_challenge,
            },
            {"kind": "revised-candidate", "statement": revised_statement},
        )
        mismatched_target = fact(
            wrong_challenge_closure,
            "turnlock.predicate:TargetedDiscoveryStatement@1",
            {
                "producerDiscovery": mismatched_revision,
                "statement": revised_statement,
            },
        )
        expect_false(
            f"prior challenge {label} mismatch",
            wrong_challenge_closure,
            mismatched_target,
        )

    expect_true("original sibling after revision", objection_closure, sibling_target)
    revised_sibling = fact(
        objection_closure,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": revision1, "statement": sibling_statement},
    )
    expect_false("revision cannot produce sibling", objection_closure, revised_sibling)

    old_exhaustion_reuse = make_necessity(
        objection_closure, surviving, decision1, exhaustion0
    )
    expect_false("old exhaustion cannot bind revised target", objection_closure, old_exhaustion_reuse)
    exhaustion1 = make_exhaustion(
        objection_closure, surviving, revision1, target1
    )
    necessity1 = make_necessity(
        objection_closure, surviving, decision1, exhaustion1
    )
    expect_true("fresh revised exhaustion", objection_closure, exhaustion1)
    expect_true("fresh revised DecisionNecessity", objection_closure, necessity1)
    if (
        target1["factId"] == target0["factId"]
        or exhaustion1["factId"] == exhaustion0["factId"]
        or necessity1["factId"] == necessity0["factId"]
    ):
        errors.append("inactive protocol v8 E3-C3: revised closure reused old FactId")

    fresh_zero_closure = copy.deepcopy(objection_closure)
    fresh_zero = make_dn_challenge(
        fresh_zero_closure,
        surviving,
        decision1,
        exhaustion1,
        necessity1,
        zero=True,
    )
    fresh_qualification = make_qualification(
        fresh_zero_closure,
        revision1,
        surviving,
        decision1,
        exhaustion1,
        necessity1,
        fresh_zero,
    )
    fresh_result = reduce_qualification(fresh_zero_closure, fresh_qualification)
    if fresh_result is None or fresh_result["fact"]["predicateRevision"] != (
        "turnlock.predicate:QualifiedDecisionNecessity@1"
    ):
        errors.append("inactive protocol v8 E3-C3: fresh qualification failed")

    second_closure = copy.deepcopy(objection_closure)
    fresh_objection = make_dn_challenge(
        second_closure,
        surviving,
        decision1,
        exhaustion1,
        necessity1,
        zero=False,
    )
    revision2 = admit(
        second_closure,
        topology["revision_id"],
        {
            "survivingMaterialBasis": surviving,
            "priorDecisionRequiredStatement": decision1,
            "priorDecisionNecessityCandidate": necessity1,
            "priorDecisionNecessityChallenge": fresh_objection,
        },
        {"kind": "revised-candidate", "statement": revised_statement},
    )
    target2 = fact(
        second_closure,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": revision2, "statement": revised_statement},
    )
    expect_false("second decision-required revision", second_closure, target2)

    quarantined = copy.deepcopy(objection_closure)
    revision_record = _protocol_v8_e3a_resolve_admission_identity(
        quarantined, revision1
    )
    conflict_statement = copy.deepcopy(revised_statement)
    conflict_statement["statement"] = "conflicting revised decision statement"
    conflict_candidate = {
        "kind": "revised-candidate",
        "statement": conflict_statement,
    }
    conflict_id = _protocol_v8_e1_semantic_admission_id(
        revision_record["qlek"], conflict_candidate
    )
    conflict_token = _protocol_v8_e2_validated_witness_token(
        revision_record["qlek"],
        conflict_id,
        conflict_candidate,
        "IMPORTED-E3-C3-CONFLICT",
    )
    _protocol_v8_e2_t5_reconcile_external_history(
        quarantined["e2_state"],
        revision_record["qlek"],
        semantic_candidate=conflict_candidate,
        validated_origin_witness=conflict_token,
    )
    historical = status(quarantined, target1)
    if historical["reconstructible"] is not True or historical["consumable"] is not False:
        errors.append("inactive protocol v8 E3-C3: quarantine rewrote historical truth")

    dangling_d = {
        "kind": "semantic-fact",
        "predicateRevision": "turnlock.predicate:DecisionRequiredDiscoveryStatement@1",
        "factId": "semantic-fact-sha256:" + "9" * 64,
    }
    dangling_u = {
        "kind": "semantic-fact",
        "predicateRevision": "turnlock.predicate:UniqueCorrectionExhaustion@1",
        "factId": "semantic-fact-sha256:" + "8" * 64,
    }
    dangling_n = {
        "kind": "semantic-fact",
        "predicateRevision": "turnlock.predicate:DecisionNecessityCandidate@1",
        "factId": "semantic-fact-sha256:" + "7" * 64,
    }
    for label, bad_d, bad_u in (
        ("dangling D", dangling_d, exhaustion0),
        ("dangling U", decision0, dangling_u),
    ):
        dangling_fact = make_necessity(closure, surviving, bad_d, bad_u)
        expect_rejected(label, lambda ref=dangling_fact: status(closure, ref))
    dangling_revision_closure = copy.deepcopy(pre_revision_closure)
    dangling_revision = admit(
        dangling_revision_closure,
        topology["revision_id"],
        {
            "survivingMaterialBasis": surviving,
            "priorDecisionRequiredStatement": decision0,
            "priorDecisionNecessityCandidate": dangling_n,
            "priorDecisionNecessityChallenge": objection_challenge,
        },
        {"kind": "revised-candidate", "statement": revised_statement},
    )
    dangling_revision_target = fact(
        dangling_revision_closure,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": dangling_revision, "statement": revised_statement},
    )
    expect_rejected(
        "dangling N predecessor",
        lambda: status(dangling_revision_closure, dangling_revision_target),
    )
    dangling_challenge_closure = copy.deepcopy(closure)
    dangling_admission = {
        "kind": "semantic-admission",
        "admissionId": "semantic-admission-sha256:" + "6" * 64,
    }
    dangling_challenge_revision = admit(
        dangling_challenge_closure,
        topology["revision_id"],
        {
            "survivingMaterialBasis": surviving,
            "priorDecisionRequiredStatement": decision0,
            "priorDecisionNecessityCandidate": necessity0,
            "priorDecisionNecessityChallenge": dangling_admission,
        },
        {"kind": "revised-candidate", "statement": revised_statement},
    )
    dangling_challenge_target = fact(
        dangling_challenge_closure,
        "turnlock.predicate:TargetedDiscoveryStatement@1",
        {"producerDiscovery": dangling_challenge_revision, "statement": revised_statement},
    )
    expect_rejected(
        "dangling DecisionNecessityChallenge",
        lambda: status(dangling_challenge_closure, dangling_challenge_target),
    )

    mismatch_closure = copy.deepcopy(closure)
    mismatch_descriptor = _protocol_v8_e3a_resolve_fact_identity(
        mismatch_closure, necessity0
    )
    mismatch_closure["fact_descriptors"][necessity0["factId"]] = [
        {
            **mismatch_descriptor,
            "arguments": {
                **mismatch_descriptor["arguments"],
                "survivingMaterialBasis": other_surviving,
            },
        }
    ]
    expect_rejected(
        "FactId/descriptor mismatch",
        lambda: status(mismatch_closure, necessity0),
        "FactId/descriptor mismatch",
    )
    expect_rejected(
        "exact Fact reducer cycle",
        lambda: _protocol_v8_e3c3_fact_status(
            root,
            closure,
            contracts,
            predicates,
            qualifications,
            necessity0,
            active={necessity0["factId"]},
        ),
        "unlawful semantic Fact reducer cycle",
    )

    if zero_result is not None:
        unrelated = zero_result["fact"]
        expect_rejected(
            "unrelated C4 Predicate",
            lambda: status(zero_closure, unrelated),
            "unsupported root Predicate",
        )
    return errors


def _protocol_v8_e4a_decode_path_identity(value: object) -> bytes:
    """Decode one exact canonical unpadded raw-path identity."""
    if not isinstance(value, str) or not value:
        raise ValueError(
            "inactive protocol v8 E4-A: raw path identity must be non-empty"
        )
    if "=" in value:
        raise ValueError(
            "inactive protocol v8 E4-A: raw path identity must be unpadded"
        )
    try:
        encoded = value.encode("ascii")
        decoded = base64.b64decode(
            encoded + b"=" * (-len(encoded) % 4),
            altchars=b"-_",
            validate=True,
        )
    except (UnicodeEncodeError, ValueError) as error:
        raise ValueError(
            "inactive protocol v8 E4-A: invalid raw path base64url identity"
        ) from error
    canonical = base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii")
    if canonical != value:
        raise ValueError(
            "inactive protocol v8 E4-A: non-canonical raw path base64url identity"
        )
    return decoded


def _protocol_v8_e4a_canonical_readable_coverage(
    path_identities: object,
) -> dict:
    """Canonicalize an accepted exact set/list of M7 raw-path identities."""
    if not isinstance(path_identities, (list, tuple, set, frozenset)):
        raise ValueError(
            "inactive protocol v8 E4-A: readable paths must be an exact collection"
        )
    decoded: list[tuple[bytes, str]] = []
    seen: set[str] = set()
    for identity in path_identities:
        raw = _protocol_v8_e4a_decode_path_identity(identity)
        assert isinstance(identity, str)
        if identity in seen:
            raise ValueError(
                "inactive protocol v8 E4-A: duplicate readable raw path"
            )
        seen.add(identity)
        decoded.append((raw, identity))
    decoded.sort(key=lambda item: item[0])
    return {
        "kind": "readable-paths",
        "paths": [identity for _, identity in decoded],
    }


def _protocol_v8_e4a_validate_coverage(
    coverage: object,
    materialized_paths: dict[str, bytes],
) -> dict:
    """Validate exact CoverageSpecV1 against one admitted materialization."""
    if not isinstance(coverage, dict):
        raise ValueError(
            "inactive protocol v8 E4-A: CoverageSpec must be an object"
        )
    kind = coverage.get("kind")
    if kind == "complete":
        if set(coverage) != {"kind"}:
            raise ValueError(
                "inactive protocol v8 E4-A: complete CoverageSpec key mismatch"
            )
        return {"kind": "complete"}
    if kind != "readable-paths":
        raise ValueError(
            "inactive protocol v8 E4-A: unknown CoverageSpec kind"
        )
    if set(coverage) != {"kind", "paths"}:
        raise ValueError(
            "inactive protocol v8 E4-A: readable CoverageSpec key mismatch"
        )
    paths = coverage.get("paths")
    if not isinstance(paths, list):
        raise ValueError(
            "inactive protocol v8 E4-A: readable CoverageSpec paths must be an array"
        )
    canonical = _protocol_v8_e4a_canonical_readable_coverage(paths)
    if canonical != coverage:
        raise ValueError(
            "inactive protocol v8 E4-A: readable CoverageSpec path order is non-canonical"
        )
    for identity in paths:
        if identity not in materialized_paths:
            raise ValueError(
                "inactive protocol v8 E4-A: readable path is absent from materialization"
            )
    return copy.deepcopy(canonical)


def _protocol_v8_e4a_exact_bytes(exact_bytes: object) -> dict:
    """Construct the sole canonical ExactBytesV1 representation."""
    if type(exact_bytes) is not bytes:
        raise ValueError(
            "inactive protocol v8 E4-A: ExactBytes input must be exact bytes"
        )
    try:
        decoded = exact_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return {
            "encoding": "base64url",
            "data": base64.urlsafe_b64encode(exact_bytes)
            .rstrip(b"=")
            .decode("ascii"),
        }
    return {"encoding": "utf-8", "data": decoded}


def _protocol_v8_e4a_construct_candidate_view(
    closure: dict,
    candidate_revision_ref: object,
    coverage: object,
    candidate_materialization_resolver,
    sealed_content_resolver,
) -> dict:
    """Construct exact CandidateViewV1 only from injected sealed authority."""
    try:
        candidate = _protocol_v8_e3a_resolve_exact_authority(
            closure, candidate_revision_ref
        )
    except ValueError as error:
        raise ValueError(
            "inactive protocol v8 E4-A: CandidateRevision authority does not resolve"
        ) from error
    if candidate.get("authorityType") != (
        "turnlock.authority:candidate-revision.v2"
    ):
        raise ValueError(
            "inactive protocol v8 E4-A: authority is not CandidateRevision v2"
        )
    try:
        materialization = candidate_materialization_resolver(copy.deepcopy(candidate))
    except ValueError as error:
        raise ValueError(
            "inactive protocol v8 E4-A: admitted M7 materialization does not resolve"
        ) from error
    if not isinstance(materialization, dict):
        raise ValueError(
            "inactive protocol v8 E4-A: M7 materialization resolver returned no object"
        )
    git_object_format = materialization.get("gitObjectFormat")
    entries = materialization.get("entries")
    if git_object_format not in {"sha1", "sha256"} or not isinstance(entries, list):
        raise ValueError(
            "inactive protocol v8 E4-A: injected M7 materialization contract mismatch"
        )
    by_path: dict[str, tuple[bytes, dict]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(
                "inactive protocol v8 E4-A: injected M7 entry must be an object"
            )
        identity = entry.get("pathBytesBase64url")
        raw_path = _protocol_v8_e4a_decode_path_identity(identity)
        assert isinstance(identity, str)
        if identity in by_path:
            raise ValueError(
                "inactive protocol v8 E4-A: injected M7 paths are not unique"
            )
        by_path[identity] = (raw_path, entry)
    exact_coverage = _protocol_v8_e4a_validate_coverage(
        coverage,
        {identity: raw for identity, (raw, _) in by_path.items()},
    )
    if exact_coverage["kind"] == "complete":
        selected = list(by_path)
    else:
        selected = list(exact_coverage["paths"])
    selected.sort(key=lambda identity: by_path[identity][0])
    projected: list[dict] = []
    for identity in selected:
        entry = by_path[identity][1]
        kind = entry.get("kind")
        mode = entry.get("mode")
        if kind == "blob":
            if set(entry) != {"pathBytesBase64url", "kind", "mode", "content"} or (
                mode not in {"100644", "100755"}
            ):
                raise ValueError(
                    "inactive protocol v8 E4-A: injected M7 blob entry mismatch"
                )
            try:
                content = sealed_content_resolver(copy.deepcopy(entry["content"]))
            except ValueError as error:
                raise ValueError(
                    "inactive protocol v8 E4-A: sealed blob content does not resolve"
                ) from error
            state = {
                "kind": "blob",
                "mode": mode,
                "content": _protocol_v8_e4a_exact_bytes(content),
            }
        elif kind == "symlink":
            if set(entry) != {"pathBytesBase64url", "kind", "mode", "content"} or (
                mode != "120000"
            ):
                raise ValueError(
                    "inactive protocol v8 E4-A: injected M7 symlink entry mismatch"
                )
            try:
                content = sealed_content_resolver(copy.deepcopy(entry["content"]))
            except ValueError as error:
                raise ValueError(
                    "inactive protocol v8 E4-A: sealed symlink content does not resolve"
                ) from error
            state = {
                "kind": "symlink",
                "mode": "120000",
                "content": _protocol_v8_e4a_exact_bytes(content),
            }
        elif kind == "gitlink":
            if set(entry) != {"pathBytesBase64url", "kind", "mode", "objectId"} or (
                mode != "160000"
            ):
                raise ValueError(
                    "inactive protocol v8 E4-A: injected M7 gitlink entry mismatch"
                )
            object_id = entry.get("objectId")
            if not isinstance(object_id, str) or not object_id:
                raise ValueError(
                    "inactive protocol v8 E4-A: injected M7 gitlink objectId missing"
                )
            state = {
                "kind": "gitlink",
                "mode": "160000",
                "objectId": object_id,
            }
        else:
            raise ValueError(
                "inactive protocol v8 E4-A: injected M7 entry kind mismatch"
            )
        projected.append(
            {
                "pathBytesBase64url": identity,
                "state": state,
            }
        )
    return {
        "gitObjectFormat": git_object_format,
        "entries": projected,
    }


def _protocol_v8_e4a_register_candidate_view(
    closure: dict,
    candidate_view: object,
) -> dict:
    """Identify one exact CandidateView through the existing C2 algebra."""
    return _protocol_v8_e3a_register_semantic_value(
        closure,
        "turnlock.semantic-value:CandidateView@1",
        candidate_view,
    )


def _protocol_v8_e4a_candidate_view_of(
    closure: dict,
    candidate_revision_ref: object,
    coverage: object,
    candidate_view_ref: object,
    candidate_materialization_resolver,
    sealed_content_resolver,
) -> bool:
    """Validate one exact claimed CandidateViewOf relation."""
    expected = _protocol_v8_e4a_construct_candidate_view(
        closure,
        candidate_revision_ref,
        coverage,
        candidate_materialization_resolver,
        sealed_content_resolver,
    )
    try:
        claimed = _protocol_v8_e3a_resolve_semantic_value(
            closure, candidate_view_ref
        )
    except ValueError as error:
        raise ValueError(
            "inactive protocol v8 E4-A: CANDIDATE-VIEW-INTEGRITY-FAILURE: "
            "claimed CandidateView does not resolve"
        ) from error
    if claimed.get("valueType") != "turnlock.semantic-value:CandidateView@1" or (
        _protocol_v8_e1_canonical_json_value_bytes(claimed.get("value"))
        != _protocol_v8_e1_canonical_json_value_bytes(expected)
    ):
        raise ValueError(
            "inactive protocol v8 E4-A: CANDIDATE-VIEW-INTEGRITY-FAILURE: "
            "claimed CandidateView differs from exact construction"
        )
    return True


def _inactive_protocol_v8_e4a_candidate_view_errors(root: Path) -> list[str]:
    """Exercise exact CandidateView construction with disposable fixtures."""
    del root
    errors: list[str] = []
    closure = _protocol_v8_e3a_new_closure(_protocol_v8_e2_new_state())

    def path(raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    def artifact(artifact_id: str, content: bytes) -> dict:
        return {
            "artifactId": artifact_id,
            "sha256": hashlib.sha256(content).hexdigest(),
            "byteLength": len(content),
            "mediaType": "application/octet-stream",
            "repositoryPath": None,
        }

    artifact_bytes: dict[str, bytes] = {}

    def add_artifact(artifact_id: str, content: bytes) -> dict:
        if artifact_id in artifact_bytes and artifact_bytes[artifact_id] != content:
            raise ValueError(
                "inactive protocol v8 E4-A: fixture ArtifactRef bytes conflict"
            )
        artifact_bytes[artifact_id] = content
        return artifact(artifact_id, content)

    def resolve_content(reference: object) -> bytes:
        if not isinstance(reference, dict) or set(reference) != {
            "artifactId",
            "sha256",
            "byteLength",
            "mediaType",
            "repositoryPath",
        }:
            raise ValueError(
                "inactive protocol v8 E4-A: fixture ArtifactRef shape mismatch"
            )
        artifact_id = reference.get("artifactId")
        content = artifact_bytes.get(artifact_id)
        if content is None or reference != artifact(str(artifact_id), content):
            raise ValueError(
                "inactive protocol v8 E4-A: fixture ArtifactRef integrity mismatch"
            )
        return content

    def candidate(candidate_id: str) -> dict:
        reference = {
            "kind": "exact-authority",
            "authorityType": "turnlock.authority:candidate-revision.v2",
            "authorityId": candidate_id,
        }
        _protocol_v8_e3a_register_exact_authority(closure, reference)
        return reference

    candidates: dict[str, dict] = {}

    def resolve_candidate(reference: object) -> dict:
        if not isinstance(reference, dict):
            raise ValueError(
                "inactive protocol v8 E4-A: fixture candidate ref missing"
            )
        value = candidates.get(reference.get("authorityId"))
        if value is None:
            raise ValueError(
                "inactive protocol v8 E4-A: fixture candidate materialization missing"
            )
        return copy.deepcopy(value)

    def materialization(entries: list[dict], *, object_format: str = "sha1") -> dict:
        return {
            "gitObjectFormat": object_format,
            "entries": copy.deepcopy(entries),
        }

    def entry(path_identity: str, kind: str, mode: str, value: object) -> dict:
        result = {
            "pathBytesBase64url": path_identity,
            "kind": kind,
            "mode": mode,
        }
        if kind in {"blob", "symlink"}:
            result["content"] = copy.deepcopy(value)
        else:
            result["objectId"] = value
        return result

    p_a = path(b"a.txt")
    p_z = path(b"z.txt")
    p_utf8 = path("é.txt".encode("utf-8"))
    p_link = path(b"link")
    p_git = path(b"submodule")
    all_paths = _protocol_v8_e4a_canonical_readable_coverage(
        [p_z, p_utf8, p_a, p_git, p_link]
    )
    bytes_ascii = b"same bytes\n"
    bytes_utf8 = "café\n".encode("utf-8")
    bytes_invalid = b"\xfftarget"
    a_ref = add_artifact("A", bytes_ascii)
    b_ref = add_artifact("B", bytes_ascii)
    utf8_ref = add_artifact("UTF8", bytes_utf8)
    invalid_ref = add_artifact("INVALID", bytes_invalid)
    changed_ref = add_artifact("CHANGED", b"different bytes\n")
    entries_a = [
        entry(p_z, "blob", "100755", a_ref),
        entry(p_utf8, "blob", "100644", utf8_ref),
        entry(p_link, "symlink", "120000", invalid_ref),
        entry(p_git, "gitlink", "160000", "1" * 40),
        entry(p_a, "blob", "100644", a_ref),
    ]
    entries_b = copy.deepcopy(entries_a)
    entries_b[-1]["content"] = b_ref
    c17 = candidate("C17")
    c18 = candidate("C18")
    c_empty = candidate("C-EMPTY")
    candidates.update(
        {
            "C17": materialization(entries_a),
            "C18": materialization(entries_b),
            "C-EMPTY": materialization([]),
        }
    )

    def construct(candidate_ref: dict, coverage: dict) -> dict:
        return _protocol_v8_e4a_construct_candidate_view(
            closure,
            candidate_ref,
            coverage,
            resolve_candidate,
            resolve_content,
        )

    def register(value: dict) -> dict:
        return _protocol_v8_e4a_register_candidate_view(closure, value)

    def expect_rejected(label: str, action, required: str | None = None) -> None:
        try:
            action()
        except ValueError as error:
            if required is not None and required not in str(error):
                errors.append(
                    f"inactive protocol v8 E4-A: {label} rejected without {required!r}"
                )
            return
        errors.append(f"inactive protocol v8 E4-A: expected rejection: {label}")

    complete = {"kind": "complete"}
    view17 = construct(c17, complete)
    view17_repeat = construct(c17, complete)
    view18 = construct(c18, complete)
    empty_complete = construct(c_empty, complete)
    empty_scoped = construct(
        c17, {"kind": "readable-paths", "paths": []}
    )
    if view17 != view17_repeat or view17 != view18:
        errors.append(
            "inactive protocol v8 E4-A: deterministic/equal physical views diverged"
        )
    if a_ref == b_ref:
        errors.append("inactive protocol v8 E4-A: distinct ArtifactRefs collapsed")
    if set(view17) != {"gitObjectFormat", "entries"} or any(
        not isinstance(item, dict)
        or set(item) != {"pathBytesBase64url", "state"}
        or _mapping(item.get("state")).get("kind") == "absent"
        for item in view17["entries"]
    ):
        errors.append("inactive protocol v8 E4-A: CandidateView exact shape mismatch")
    if c17 == c18:
        errors.append("inactive protocol v8 E4-A: nominal candidates collapsed")
    if empty_complete != {"gitObjectFormat": "sha1", "entries": []} or (
        empty_scoped != {"gitObjectFormat": "sha1", "entries": []}
    ):
        errors.append("inactive protocol v8 E4-A: empty CandidateView mismatch")
    expected_order = [
        identity
        for _, identity in sorted(
            [(_protocol_v8_e4a_decode_path_identity(item), item) for item in all_paths["paths"]]
        )
    ]
    actual_order = [item["pathBytesBase64url"] for item in view17["entries"]]
    if actual_order != expected_order or actual_order == [
        item["pathBytesBase64url"] for item in entries_a
    ]:
        errors.append("inactive protocol v8 E4-A: raw-byte path ordering mismatch")
    readable_all = construct(c17, all_paths)
    if readable_all != view17 or "coverage" in readable_all:
        errors.append("inactive protocol v8 E4-A: coverage leaked into CandidateView")

    view17_ref = register(view17)
    view17_repeat_ref = register(view17_repeat)
    view18_ref = register(view18)
    if view17_ref != view17_repeat_ref or view17_ref != view18_ref:
        errors.append("inactive protocol v8 E4-A: CandidateView identity is not extensional")
    for candidate_ref, view_ref in ((c17, view17_ref), (c18, view18_ref)):
        if not _protocol_v8_e4a_candidate_view_of(
            closure,
            candidate_ref,
            complete,
            view_ref,
            resolve_candidate,
            resolve_content,
        ):
            errors.append("inactive protocol v8 E4-A: CandidateViewOf positive failed")

    exact_cases = {
        b"": {"encoding": "utf-8", "data": ""},
        b"ascii": {"encoding": "utf-8", "data": "ascii"},
        "é".encode("utf-8"): {"encoding": "utf-8", "data": "é"},
        b"\xff": {"encoding": "base64url", "data": "_w"},
    }
    for raw, expected in exact_cases.items():
        actual = _protocol_v8_e4a_exact_bytes(raw)
        if actual != expected or "=" in actual["data"]:
            errors.append("inactive protocol v8 E4-A: ExactBytes canonicalization mismatch")

    scoped = {"kind": "readable-paths", "paths": [p_a]}
    view17_scoped = construct(c17, scoped)
    if [item["pathBytesBase64url"] for item in view17_scoped["entries"]] != [p_a]:
        errors.append("inactive protocol v8 E4-A: scoped view path set mismatch")
    c19 = candidate("C19")
    entries_outside_changed = copy.deepcopy(entries_a)
    entries_outside_changed[0]["content"] = changed_ref
    candidates["C19"] = materialization(entries_outside_changed)
    view19_scoped = construct(c19, scoped)
    view19_complete = construct(c19, complete)
    if view17_scoped != view19_scoped or view17 == view19_complete:
        errors.append(
            "inactive protocol v8 E4-A: scoped outside-coverage non-interference failed"
        )
    if register(view17_scoped) != register(view19_scoped):
        errors.append("inactive protocol v8 E4-A: scoped SemanticValueId diverged")

    c20 = candidate("C20")
    entries_changed = copy.deepcopy(entries_a)
    entries_changed[-1]["content"] = changed_ref
    candidates["C20"] = materialization(entries_changed)
    view20 = construct(c20, complete)
    view20_ref = register(view20)
    if view20 == view17:
        errors.append("inactive protocol v8 E4-A: changed exact bytes were ignored")
    expect_rejected(
        "wrong-candidate claimed view",
        lambda: _protocol_v8_e4a_candidate_view_of(
            closure, c20, complete, view17_ref, resolve_candidate, resolve_content
        ),
        "CANDIDATE-VIEW-INTEGRITY-FAILURE",
    )
    if not _protocol_v8_e4a_candidate_view_of(
        closure, c20, complete, view20_ref, resolve_candidate, resolve_content
    ):
        errors.append("inactive protocol v8 E4-A: changed candidate view failed")

    p2_scope = {"kind": "readable-paths", "paths": [p_z]}
    scoped_ref = register(view17_scoped)
    expect_rejected(
        "wrong scoped coverage",
        lambda: _protocol_v8_e4a_candidate_view_of(
            closure, c17, p2_scope, scoped_ref, resolve_candidate, resolve_content
        ),
        "CANDIDATE-VIEW-INTEGRITY-FAILURE",
    )

    coverage_failures = [
        ("unknown coverage", {"kind": "other"}),
        ("extra complete field", {"kind": "complete", "extra": True}),
        ("duplicate path", {"kind": "readable-paths", "paths": [p_a, p_a]}),
        ("non-array paths", {"kind": "readable-paths", "paths": p_a}),
        ("padded path", {"kind": "readable-paths", "paths": [p_a + "="]}),
        ("invalid base64url", {"kind": "readable-paths", "paths": ["***"]}),
        (
            "missing path",
            {"kind": "readable-paths", "paths": [path(b"missing")]},
        ),
        (
            "non-canonical order",
            {"kind": "readable-paths", "paths": [p_z, p_a]},
        ),
    ]
    for label, bad_coverage in coverage_failures:
        expect_rejected(label, lambda value=bad_coverage: construct(c17, value))

    forged_values: list[tuple[str, dict]] = []
    forged = copy.deepcopy(view17)
    forged["extra"] = True
    forged_values.append(("extra top-level field", forged))
    forged = copy.deepcopy(view17)
    del forged["gitObjectFormat"]
    forged_values.append(("missing gitObjectFormat", forged))
    forged = copy.deepcopy(view17)
    forged["gitObjectFormat"] = "sha512"
    forged_values.append(("wrong gitObjectFormat", forged))
    forged = copy.deepcopy(view17)
    forged["entries"][0]["extra"] = True
    forged_values.append(("extra entry field", forged))
    forged = copy.deepcopy(view17)
    forged["entries"][0], forged["entries"][1] = (
        forged["entries"][1], forged["entries"][0]
    )
    forged_values.append(("wrong entry ordering", forged))
    forged = copy.deepcopy(view17)
    forged["entries"][1] = copy.deepcopy(forged["entries"][0])
    forged_values.append(("duplicate entry path", forged))
    forged = copy.deepcopy(view17)
    forged["entries"][0]["state"]["mode"] = "100755"
    forged_values.append(("wrong mode", forged))
    forged = copy.deepcopy(view17)
    forged["entries"][0]["state"]["kind"] = "symlink"
    forged_values.append(("wrong state kind", forged))
    forged = copy.deepcopy(view17)
    forged["entries"][0]["state"]["content"] = {
        "encoding": "utf-8",
        "data": "wrong bytes",
    }
    forged_values.append(("wrong content bytes", forged))
    forged = copy.deepcopy(view17)
    blob_state = next(
        item["state"] for item in forged["entries"]
        if item["state"]["kind"] == "blob"
    )
    blob_state["content"] = {
        "encoding": "base64url",
        "data": base64.urlsafe_b64encode(bytes_ascii).rstrip(b"=").decode("ascii"),
    }
    forged_values.append(("wrong ExactBytes encoding", forged))
    forged = copy.deepcopy(view17)
    gitlink_state = next(
        item["state"] for item in forged["entries"]
        if item["state"]["kind"] == "gitlink"
    )
    gitlink_state["objectId"] = "2" * 40
    forged_values.append(("wrong gitlink objectId", forged))
    forged = copy.deepcopy(view17)
    forged["entries"][0]["state"]["artifactRef"] = a_ref
    forged_values.append(("ArtifactRef leaked", forged))
    for label, field in (
        ("CandidateRevision leaked", "candidateRevision"),
        ("rootTreeObjectId leaked", "rootTreeObjectId"),
        ("coverage leaked", "coverage"),
    ):
        forged = copy.deepcopy(view17)
        forged[field] = "forbidden"
        forged_values.append((label, forged))
    for label, forged_value in forged_values:
        forged_ref = register(forged_value)
        expect_rejected(
            label,
            lambda ref=forged_ref: _protocol_v8_e4a_candidate_view_of(
                closure, c17, complete, ref, resolve_candidate, resolve_content
            ),
            "CANDIDATE-VIEW-INTEGRITY-FAILURE",
        )

    same_path = path(b"physical")
    physical_candidates: list[tuple[dict, dict]] = []
    for candidate_id, state_entry in (
        ("C-BLOB-644", entry(same_path, "blob", "100644", a_ref)),
        ("C-BLOB-755", entry(same_path, "blob", "100755", a_ref)),
        ("C-SYMLINK", entry(same_path, "symlink", "120000", a_ref)),
        ("C-GITLINK", entry(same_path, "gitlink", "160000", "3" * 40)),
    ):
        candidate_ref = candidate(candidate_id)
        candidates[candidate_id] = materialization([state_entry])
        physical_candidates.append((candidate_ref, construct(candidate_ref, complete)))
    physical_views = {
        _protocol_v8_e1_canonical_json_value_bytes(value)
        for _, value in physical_candidates
    }
    if len(physical_views) != 4:
        errors.append("inactive protocol v8 E4-A: physical state distinctions collapsed")

    forbidden_e4a_fragments = {
        "bound_candidate_revision",
        "candidate_revision_of",
        "candidate_current",
        "semantic_arm",
        "repair_intent",
    }
    introduced = {
        name
        for name in globals()
        if name.startswith("_protocol_v8_e4a_")
        and any(fragment in name for fragment in forbidden_e4a_fragments)
    }
    if introduced:
        errors.append(
            "inactive protocol v8 E4-A: later candidate-bound layer was introduced"
        )
    return errors


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
    if schema_version not in (5, 6, 7, 8):
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
        _, artifact_errors = _read_review_artifact(
            root,
            _mapping(prompts.get(key)),
            f"{label}: prompts.{key}",
            REVIEW_PROMPT_PREFIX,
            REVIEW_PROMPT_SUFFIX,
        )
        errors.extend(artifact_errors)

    schemas = _mapping(bundle.get("schemas"))
    version = bundle.get("protocol_bundle_schema_version")

    if version == 8:
        keys = sorted(schemas)
    else:
        keys = [
            "raw-review-output",
            "execution-receipt",
            "challenge-output",
        ]

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
        data, artifact_errors = _read_review_artifact(
            root,
            _mapping(schemas.get(key)),
            f"{label}: schemas.{key}",
            REVIEW_SCHEMAS_PREFIX,
            REVIEW_JSON_OUTPUT_SUFFIX,
        )
        errors.extend(artifact_errors)

        if data is not None:
            try:
                schema = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                errors.append(
                    f"{label}: schemas.{key} must be valid JSON "
                    f"({_concise_parser_error(error)})"
                )
            else:
                _validator_value, schema_errors = _validator(schema)
                errors.extend(
                    f"{label}: schemas.{key}: {error}"
                    for error in schema_errors
                )

    if version == 8:
        semantic_contracts = _mapping(
            bundle.get("semantic_contracts")
        )

        for key in (
            "questions",
            "predicates",
            "qualifications",
        ):
            _catalog, artifact_errors = (
                _load_json_object_artifact(
                    root,
                    _mapping(semantic_contracts.get(key)),
                    f"{label}: semantic_contracts.{key}",
                    REVIEW_CONTRACTS_PREFIX,
                    REVIEW_JSON_OUTPUT_SUFFIX,
                    require_canonical=True,
                )
            )
            errors.extend(artifact_errors)

    profile_ids = [
        profile.get("profile_id")
        for profile in _sequence(
            bundle.get("reviewer_profiles")
        )
        if (
            isinstance(profile, dict)
            and isinstance(profile.get("profile_id"), str)
        )
    ]

    for profile_id, count in Counter(profile_ids).items():
        if count > 1:
            errors.append(
                f"{label}: duplicate reviewer profile_id "
                f"{profile_id!r}"
            )

    errors.extend(
        _reviewer_acquisition_policy_errors(
            bundle,
            label,
        )
    )

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


def _protocol_bundle_meta_schema_reference(
    version: object,
) -> dict | None:
    """Select the immutable meta-schema for one protocol-bundle schema version."""
    if version in (1, 2, 3):
        return dict(
            LEGACY_PROTOCOL_BUNDLE_META_SCHEMA_REFERENCE
        )

    if version == 4:
        return dict(PROTOCOL_V4_META_SCHEMA_REFERENCE)

    if version == 5:
        return dict(PROTOCOL_V5_META_SCHEMA_REFERENCE)

    if version == 6:
        return dict(PROTOCOL_V6_META_SCHEMA_REFERENCE)

    if version == 7:
        return dict(PROTOCOL_V7_META_SCHEMA_REFERENCE)

    if version == 8:
        return dict(PROTOCOL_V8_META_SCHEMA_REFERENCE)

    return None


def _load_protocol_bundle_document(
    root: Path,
    reference: object,
    label: str,
    cache: dict[
        str,
        tuple[dict | None, list[str]],
    ],
    chain_paths: set[str] | None = None,
    chain_ids: set[str] | None = None,
) -> tuple[dict | None, list[str]]:
    bundle_reference = _mapping(reference)
    cache_key = bundle_reference.get("sha256")

    # Cache only fully checked acyclic chains.
    if (
        chain_paths is None
        and isinstance(cache_key, str)
        and cache_key in cache
    ):
        return cache[cache_key]

    bundle, errors = _load_json_object_artifact(
        root,
        bundle_reference,
        label,
        REVIEW_PROTOCOLS_PREFIX,
        REVIEW_PROTOCOL_BUNDLE_SUFFIX,
        require_canonical=True,
    )

    if bundle is None:
        return None, errors

    version = bundle.get(
        "protocol_bundle_schema_version"
    )

    meta_reference = (
        _protocol_bundle_meta_schema_reference(
            version
        )
    )

    if meta_reference is None:
        errors.append(
            f"{label}: unsupported hostile-review "
            f"protocol bundle schema version {version!r}"
        )
        return bundle, errors

    validator, meta_errors = (
        _load_meta_schema_validator(
            root,
            meta_reference,
            f"{label}: protocol-bundle meta-schema",
        )
    )

    errors.extend(meta_errors)

    if validator is not None:
        errors.extend(
            _schema_violations(
                validator,
                bundle,
                label,
            )
        )

    if version in (4, 5, 6, 7, 8):
        meta_schemas = _mapping(
            bundle.get("meta_schemas")
        )

        declared_protocol_bundle = _mapping(
            meta_schemas.get("protocol-bundle")
        )

        expected_protocol_bundle = {
            4: PROTOCOL_V4_META_SCHEMA_REFERENCE,
            5: PROTOCOL_V5_META_SCHEMA_REFERENCE,
            6: PROTOCOL_V6_META_SCHEMA_REFERENCE,
            7: PROTOCOL_V7_META_SCHEMA_REFERENCE,
            8: PROTOCOL_V8_META_SCHEMA_REFERENCE,
        }[version]

        if (
            declared_protocol_bundle
            != expected_protocol_bundle
        ):
            errors.append(
                f"{label}: protocol v{version} must "
                "bind the exact published "
                "protocol-bundle meta-schema"
            )

        declared_review_evidence = _mapping(
            meta_schemas.get("review-evidence")
        )

        expected_review_evidence = (
            PROTOCOL_V8_REVIEW_EVIDENCE_V6_SCHEMA_REFERENCE
            if version == 8
            else LEGACY_REVIEW_EVIDENCE_META_SCHEMA_REFERENCE
        )

        if (
            declared_review_evidence
            != expected_review_evidence
        ):
            errors.append(
                f"{label}: protocol v{version} must "
                "bind the exact published "
                "review-evidence meta-schema"
            )

        for key in (
            "protocol-bundle",
            "review-evidence",
        ):
            _, binding_errors = (
                _load_meta_schema_validator(
                    root,
                    _mapping(
                        meta_schemas.get(key)
                    ),
                    f"{label}: meta_schemas.{key}",
                )
            )
            errors.extend(binding_errors)

    errors.extend(
        _protocol_bundle_errors(
            root,
            bundle,
            label,
        )
    )

    path = _mapping(reference).get("path")
    protocol_id = bundle.get("protocol_id")

    paths = set(chain_paths or ())
    ids = set(chain_ids or ())

    if (
        isinstance(path, str)
        and path in paths
    ):
        errors.append(
            f"{label}: protocol predecessor cycle "
            "or duplicate bundle path"
        )
        return bundle, errors

    if (
        isinstance(protocol_id, str)
        and protocol_id in ids
    ):
        errors.append(
            f"{label}: duplicate protocol_id in "
            f"predecessor chain {protocol_id!r}"
        )
        return bundle, errors

    if isinstance(path, str):
        paths.add(path)

    if isinstance(protocol_id, str):
        ids.add(protocol_id)

    predecessor = bundle.get("predecessor")

    if version in (2, 3, 4, 5, 6, 7, 8):
        if not isinstance(predecessor, dict):
            errors.append(
                f"{label}: schema-version-{version} "
                "bundle requires predecessor"
            )
        else:
            if (
                version == 7
                and predecessor
                != PROTOCOL_V7_PREDECESSOR_REFERENCE
            ):
                errors.append(
                    f"{label}: protocol v7 predecessor "
                    "must be the exact published v6 bundle"
                )

            if (
                version == 8
                and predecessor
                != PROTOCOL_V8_PREDECESSOR_REFERENCE
            ):
                errors.append(
                    f"{label}: protocol v8 predecessor "
                    "must be the exact published v7 bundle"
                )

            _, predecessor_errors = (
                _load_protocol_bundle_document(
                    root,
                    predecessor,
                    f"{label}: predecessor",
                    cache,
                    paths,
                    ids,
                )
            )

            errors.extend(predecessor_errors)

    elif predecessor is not None:
        errors.append(
            f"{label}: schema-version-1 bundle "
            "must not declare predecessor"
        )

    if (
        chain_paths is None
        and isinstance(cache_key, str)
    ):
        cache[cache_key] = (
            bundle,
            list(errors),
        )

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


def _inactive_protocol_v8_contract_foundation_errors(
    root: Path,
) -> list[str]:
    """Validate the exact inactive protocol-v8 C7-A semantic foundation."""
    errors: list[str] = []

    schema_specs = (
        (
            "semantic identity schema",
            PROTOCOL_V8_SEMANTIC_IDENTITY_SCHEMA_REFERENCE,
            "urn:fanilosendrison:turnlock-rust:hostile-review-semantic-identity:1",
        ),
        (
            "SemanticQuestionContract catalog schema",
            PROTOCOL_V8_SQC_CATALOG_SCHEMA_REFERENCE,
            "urn:fanilosendrison:turnlock-rust:hostile-review-semantic-question-contract-catalog:1",
        ),
        (
            "PredicateRevision catalog schema",
            PROTOCOL_V8_PREDICATE_CATALOG_SCHEMA_REFERENCE,
            "urn:fanilosendrison:turnlock-rust:hostile-review-predicate-revision-catalog:1",
        ),
        (
            "QualificationContractRevision catalog schema",
            PROTOCOL_V8_QUALIFICATION_CATALOG_SCHEMA_REFERENCE,
            "urn:fanilosendrison:turnlock-rust:hostile-review-qualification-contract-catalog:1",
        ),
    )

    for name, reference, expected_id in schema_specs:
        label = f"inactive protocol v8 C7-A {name}"
        schema, artifact_errors = _load_json_object_artifact(
            root,
            reference,
            label,
            REVIEW_SCHEMAS_PREFIX,
            REVIEW_JSON_OUTPUT_SUFFIX,
            require_canonical=True,
        )
        errors.extend(artifact_errors)
        if schema is None:
            continue

        if schema.get("$id") != expected_id:
            errors.append(
                f"{label}: $id must equal the exact C7-A schema identity"
            )

        _validator_value, schema_errors = _validator(schema)
        errors.extend(f"{label}: {error}" for error in schema_errors)

    catalog_specs = (
        (
            "SemanticQuestionContract catalog",
            PROTOCOL_V8_SQC_CATALOG_REFERENCE,
            "contracts",
            PROTOCOL_V8_SQC_REVISION_IDS,
        ),
        (
            "PredicateRevision catalog",
            PROTOCOL_V8_PREDICATE_CATALOG_REFERENCE,
            "predicates",
            PROTOCOL_V8_PREDICATE_REVISION_IDS,
        ),
        (
            "QualificationContractRevision catalog",
            PROTOCOL_V8_QUALIFICATION_CATALOG_REFERENCE,
            "qualifications",
            PROTOCOL_V8_QUALIFICATION_REVISION_IDS,
        ),
    )

    for name, reference, field, expected_ids in catalog_specs:
        label = f"inactive protocol v8 C7-A {name}"
        catalog, artifact_errors = _load_json_object_artifact(
            root,
            reference,
            label,
            REVIEW_CONTRACTS_PREFIX,
            REVIEW_JSON_OUTPUT_SUFFIX,
            require_canonical=True,
        )
        errors.extend(artifact_errors)
        if catalog is None:
            continue

        if catalog.get("catalog_schema_version") != "1.0":
            errors.append(
                f"{label}: catalog_schema_version must be exactly '1.0'"
            )

        entries = _sequence(catalog.get(field))
        revision_ids = [
            entry.get("revision_id")
            for entry in entries
            if isinstance(entry, dict)
        ]

        if len(entries) != len(expected_ids):
            errors.append(
                f"{label}: {field} must contain exactly "
                f"{len(expected_ids)} entries"
            )

        if revision_ids != list(expected_ids):
            errors.append(
                f"{label}: revision IDs and lexical ordering must equal "
                "the exact C7-A catalog"
            )

        if len(revision_ids) != len(set(revision_ids)):
            errors.append(
                f"{label}: duplicate revision_id is forbidden"
            )

    return errors


def _inactive_protocol_v8_projection_schema_errors(
    root: Path,
) -> list[str]:
    """Validate the exact inactive protocol-v8 C7-B projection schemas."""
    errors: list[str] = []

    specs = (
        (
            "cognitive execution packet schema",
            PROTOCOL_V8_COGNITIVE_EXECUTION_PACKET_SCHEMA_REFERENCE,
            REVIEW_SCHEMAS_PREFIX,
            "urn:fanilosendrison:turnlock-rust:hostile-review-cognitive-execution-packet:1",
        ),
        (
            "semantic question binding schema",
            PROTOCOL_V8_SEMANTIC_QUESTION_BINDING_SCHEMA_REFERENCE,
            REVIEW_SCHEMAS_PREFIX,
            "urn:fanilosendrison:turnlock-rust:hostile-review-semantic-question-binding:1",
        ),
        (
            "SemanticAdmission origin witness schema",
            PROTOCOL_V8_SEMANTIC_ADMISSION_ORIGIN_WITNESS_SCHEMA_REFERENCE,
            REVIEW_SCHEMAS_PREFIX,
            "urn:fanilosendrison:turnlock-rust:hostile-review-semantic-admission-origin-witness:1",
        ),
        (
            "finding adjudication supplement v2 schema",
            PROTOCOL_V8_FINDING_ADJUDICATION_SUPPLEMENT_V2_SCHEMA_REFERENCE,
            REVIEW_SCHEMAS_PREFIX,
            "urn:fanilosendrison:turnlock-rust:finding-adjudication-supplement:2",
        ),
        (
            "review evidence v6 meta-schema",
            PROTOCOL_V8_REVIEW_EVIDENCE_V6_SCHEMA_REFERENCE,
            REVIEW_META_SCHEMAS_PREFIX,
            "urn:fanilosendrison:turnlock-rust:hostile-review-evidence:6",
        ),
    )

    for name, reference, prefix, expected_id in specs:
        label = f"inactive protocol v8 C7-B {name}"

        schema, artifact_errors = _load_json_object_artifact(
            root,
            reference,
            label,
            prefix,
            REVIEW_JSON_OUTPUT_SUFFIX,
            require_canonical=True,
        )

        errors.extend(artifact_errors)

        if schema is None:
            continue

        if schema.get("$id") != expected_id:
            errors.append(
                f"{label}: $id must equal the exact C7-B schema identity"
            )

        _validator_value, schema_errors = _validator(schema)

        errors.extend(
            f"{label}: {error}"
            for error in schema_errors
        )

    return errors


def _inactive_protocol_v8_prompt_errors(
    root: Path,
) -> list[str]:
    """Validate the exact inactive protocol-v8 C7-C prompts."""
    errors: list[str] = []

    specs = (
        (
            "adjudication prompt v3",
            PROTOCOL_V8_ADJUDICATION_PROMPT_V3_REFERENCE,
            "# Gate A adjudication prompt — v3\n",
        ),
        (
            "challenge prompt v2",
            PROTOCOL_V8_CHALLENGE_PROMPT_V2_REFERENCE,
            "# Gate A challenge prompt — v2\n",
        ),
        (
            "repair prompt v3",
            PROTOCOL_V8_REPAIR_PROMPT_V3_REFERENCE,
            "# Gate A repair prompt — v3\n",
        ),
    )

    for name, reference, expected_heading in specs:
        label = f"inactive protocol v8 C7-C {name}"

        data, artifact_errors = _read_review_artifact(
            root,
            reference,
            label,
            REVIEW_PROMPT_PREFIX,
            REVIEW_PROMPT_SUFFIX,
        )

        errors.extend(artifact_errors)

        if data is None:
            continue

        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(
                f"{label}: prompt must be valid UTF-8"
            )
            continue

        if not text.startswith(expected_heading):
            errors.append(
                f"{label}: prompt heading does not match exact C7-C prompt"
            )

        if not text.endswith("\n"):
            errors.append(
                f"{label}: prompt must end with exactly one LF"
            )

        if "\r" in text:
            errors.append(
                f"{label}: CR characters are forbidden"
            )

    return errors


def _protocol_v8_question_realization_errors(
    root: Path,
    bundle: dict,
    label: str,
) -> list[str]:
    """Derive P8 question realizations from the selected exact SQC catalog."""
    errors: list[str] = []

    semantic_contracts = _mapping(
        bundle.get("semantic_contracts")
    )

    catalog, catalog_errors = (
        _load_json_object_artifact(
            root,
            _mapping(
                semantic_contracts.get(
                    "questions"
                )
            ),
            f"{label}: semantic question catalog",
            REVIEW_CONTRACTS_PREFIX,
            REVIEW_JSON_OUTPUT_SUFFIX,
            require_canonical=True,
        )
    )

    errors.extend(catalog_errors)

    if catalog is None:
        return errors

    expected: list[dict] = []

    for index, entry in enumerate(
        _sequence(catalog.get("contracts"))
    ):
        entry_label = (
            f"{label}: semantic question "
            f"catalog contracts[{index}]"
        )

        if not isinstance(entry, dict):
            errors.append(
                f"{entry_label} must be a mapping"
            )
            continue

        revision_id = entry.get(
            "revision_id"
        )

        if not isinstance(revision_id, str):
            errors.append(
                f"{entry_label}.revision_id "
                "must be a string"
            )
            continue

        definition = _mapping(
            entry.get("definition")
        )

        question_kind = definition.get(
            "question_kind"
        )

        family = definition.get("family")

        if question_kind == "challenge":
            prompt = "challenge"
            output_schema = "challenge-output"

        elif family == "repair-realization":
            prompt = "repair"
            output_schema = "adjudication-output"

        else:
            prompt = "adjudication"
            output_schema = "adjudication-output"

        expected.append(
            {
                "semantic_question_contract":
                    revision_id,
                "packet_schema":
                    "cognitive-execution-packet",
                "prompt":
                    prompt,
                "output_schema":
                    output_schema,
            }
        )

    actual = _sequence(
        bundle.get("question_realizations")
    )

    if actual != expected:
        errors.append(
            f"{label}: question_realizations "
            "must equal the exact realization "
            "mapping mechanically derived from "
            "the selected SQC catalog"
        )

    return errors


def _inactive_protocol_v8_candidate_errors(
    root: Path,
    cache: dict[
        str,
        tuple[dict | None, list[str]],
    ],
) -> list[str]:
    """Validate the exact protocol-v8 candidate without selecting it as current."""
    label = "inactive protocol v8 candidate"

    bundle, errors = (
        _load_protocol_bundle_document(
            root,
            PROTOCOL_V8_BUNDLE_REFERENCE,
            label,
            cache,
        )
    )

    if bundle is None:
        return errors

    if (
        bundle.get(
            "protocol_bundle_schema_version"
        )
        != 8
    ):
        errors.append(
            f"{label}: protocol bundle schema "
            "version must be 8"
        )

    if (
        bundle.get("protocol_id")
        != "gate-a-campaign-protocol-v8"
    ):
        errors.append(
            f"{label}: protocol_id must be "
            "gate-a-campaign-protocol-v8"
        )

    if (
        bundle.get("predecessor")
        != PROTOCOL_V8_PREDECESSOR_REFERENCE
    ):
        errors.append(
            f"{label}: predecessor must be "
            "the exact published v7 bundle"
        )

    semantic_contracts = _mapping(
        bundle.get("semantic_contracts")
    )

    expected_semantic_contracts = {
        "questions":
            PROTOCOL_V8_SQC_CATALOG_REFERENCE,
        "predicates":
            PROTOCOL_V8_PREDICATE_CATALOG_REFERENCE,
        "qualifications":
            PROTOCOL_V8_QUALIFICATION_CATALOG_REFERENCE,
    }

    if (
        semantic_contracts
        != expected_semantic_contracts
    ):
        errors.append(
            f"{label}: semantic_contracts must "
            "bind the exact C7-A catalogs"
        )

    policies = _mapping(
        bundle.get("policies")
    )

    if "challenge" in policies:
        errors.append(
            f"{label}: policies.challenge is "
            "forbidden in protocol v8"
        )

    schemas = _mapping(
        bundle.get("schemas")
    )

    for forbidden_key in (
        "adjudication-packet",
        "challenge-packet",
    ):
        if forbidden_key in schemas:
            errors.append(
                f"{label}: schemas."
                f"{forbidden_key} is forbidden "
                "in protocol v8"
            )

    errors.extend(
        _protocol_v8_question_realization_errors(
            root,
            bundle,
            label,
        )
    )

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
    errors.extend(_inactive_protocol_v8_contract_foundation_errors(root))
    errors.extend(_inactive_protocol_v8_projection_schema_errors(root))
    errors.extend(_inactive_protocol_v8_prompt_errors(root))
    errors.extend(_inactive_protocol_v8_candidate_errors(root, candidate_bundle_cache))
    errors.extend(_inactive_protocol_v8_e1_semantic_identity_errors(root))
    errors.extend(_inactive_protocol_v8_e2_execution_admission_errors(root))
    errors.extend(
        _inactive_protocol_v8_e3a_semantic_closure_errors(root)
    )
    errors.extend(
        _inactive_protocol_v8_e3b_qualification_reducer_errors(root)
    )
    errors.extend(
        _inactive_protocol_v8_e3c1_discovery_fact_errors(root)
    )
    errors.extend(
        _inactive_protocol_v8_e3c2_exhaustion_fact_errors(root)
    )
    errors.extend(
        _inactive_protocol_v8_e3c3_decision_necessity_errors(root)
    )
    errors.extend(
        _inactive_protocol_v8_e4a_candidate_view_errors(root)
    )

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
