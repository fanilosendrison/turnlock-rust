"""Validate native Proto-Ring operation results before Turnlock consumes them."""

from __future__ import annotations

from typing import Any


class ProtoRingResultShapeError(ValueError):
    """A successful transport envelope contains a malformed operation value."""


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProtoRingResultShapeError(f"{label} must be an object")
    return value


def _list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ProtoRingResultShapeError(f"{label} must be a list")
    return value


def _strings(value: object, label: str) -> list[str]:
    items = _list(value, label)
    if not all(isinstance(item, str) for item in items):
        raise ProtoRingResultShapeError(f"{label} must contain only strings")
    return items


def _string(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ProtoRingResultShapeError(f"{label} must be a string")
    return value


def _boolean(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise ProtoRingResultShapeError(f"{label} must be boolean")
    return value


def _optional_string(value: object, label: str) -> None:
    if value is not None and not isinstance(value, str):
        raise ProtoRingResultShapeError(f"{label} must be null or string")


def _hex(value: object, label: str, exact_bytes: int | None = None) -> str:
    text = _string(value, label)
    if (
        len(text) % 2 != 0
        or any(character not in "0123456789abcdef" for character in text)
        or (exact_bytes is not None and len(text) != exact_bytes * 2)
    ):
        raise ProtoRingResultShapeError(f"{label} must be lowercase hexadecimal")
    return text


def _structured(value: object, label: str) -> None:
    item = _mapping(value, label)
    if set(item) != {"type", "value"} or not isinstance(item["type"], str):
        raise ProtoRingResultShapeError(f"{label} is not a tagged structured value")


def _obligation(value: object, label: str) -> None:
    item = _mapping(value, label)
    _string(item.get("id"), f"{label}.id")
    _string(item.get("status"), f"{label}.status")
    _boolean(item.get("executed"), f"{label}.executed")
    _optional_string(item.get("exit_code"), f"{label}.exit_code")


def _integrity(value: dict[str, Any]) -> None:
    _string(value.get("verdict"), "integrity.verdict")
    _string(value.get("state_relation"), "integrity.state_relation")
    _boolean(value.get("state_coherence_halt"), "integrity.state_coherence_halt")
    obligations = _list(value.get("obligations"), "integrity.obligations")
    for index, obligation in enumerate(obligations):
        _obligation(obligation, f"integrity.obligations[{index}]")
    validations = _list(value.get("validations"), "integrity.validations")
    for index, validation_value in enumerate(validations):
        validation = _mapping(validation_value, f"integrity.validations[{index}]")
        _string(validation.get("id"), f"integrity.validations[{index}].id")
        _string(validation.get("status"), f"integrity.validations[{index}].status")
        nested = _list(
            validation.get("obligations"),
            f"integrity.validations[{index}].obligations",
        )
        for obligation_index, obligation in enumerate(nested):
            _obligation(
                obligation,
                f"integrity.validations[{index}].obligations[{obligation_index}]",
            )


def _compose(value: dict[str, Any]) -> None:
    _string(value.get("stage"), "composition.stage")
    _boolean(value.get("identity_present"), "composition.identity_present")
    _strings(value.get("scope_paths"), "composition.scope_paths")
    components = _mapping(value.get("components"), "composition.components")
    if not all(isinstance(key, str) and type(item) is bool for key, item in components.items()):
        raise ProtoRingResultShapeError("composition.components is malformed")
    _mapping(value.get("bindings"), "composition.bindings")


def _record_fields(value: object, label: str, fields: dict[str, type]) -> None:
    item = _mapping(value, label)
    if set(item) != set(fields):
        raise ProtoRingResultShapeError(f"{label} has missing or unknown fields")
    for name, expected in fields.items():
        field = item.get(name)
        if expected is int:
            valid = type(field) is int
        else:
            valid = isinstance(field, expected)
        if not valid:
            raise ProtoRingResultShapeError(f"{label}.{name} has invalid type")


def _terminology(operation: str, request: dict[str, Any], value: dict[str, Any]) -> None:
    mode = request.get("mode")
    if operation.endswith("fingerprint"):
        key = "text" if mode == "normalize_text" else "sha256"
        if key == "sha256":
            _hex(value.get(key), "terminology sha256", exact_bytes=32)
        else:
            _string(value.get(key), "terminology result")
    elif operation.endswith("registry"):
        entries = _list(value.get("entries"), "terminology.entries")
        fields = {
            "key": str,
            "canonical_term": str,
            "anchor": str,
            "aliases": list,
            "deprecated": list,
            "term_structure": str,
        }
        for index, entry in enumerate(entries):
            _record_fields(entry, f"terminology.entries[{index}]", fields)
            _strings(entry["aliases"], f"terminology.entries[{index}].aliases")
            _strings(entry["deprecated"], f"terminology.entries[{index}].deprecated")
        _strings(value.get("diagnostics"), "terminology.diagnostics")
    elif operation.endswith("markdown"):
        key = "blocks" if mode == "parse_blocks" else "occurrences"
        items = _list(value.get(key), f"terminology.{key}")
        fields = (
            {"line": int, "section": str, "heading": str, "text": str}
            if mode == "parse_blocks"
            else {
                "concepts": list,
                "section": str,
                "heading": str,
                "fingerprint": str,
                "line": int,
                "canonical": bool,
            }
        )
        for index, item in enumerate(items):
            _record_fields(item, f"terminology.{key}[{index}]", fields)
            if key == "occurrences":
                _strings(item["concepts"], f"terminology.{key}[{index}].concepts")
        _strings(value.get("diagnostics"), "terminology.diagnostics")
        if mode == "parse_blocks":
            anchors = _mapping(value.get("anchors"), "terminology.anchors")
            for anchor, records_value in anchors.items():
                _string(anchor, "terminology anchor key")
                records = _list(records_value, f"terminology.anchors.{anchor}")
                for index, record in enumerate(records):
                    _record_fields(
                        record,
                        f"terminology.anchors.{anchor}[{index}]",
                        {"line": int, "section": str, "heading": str},
                    )
    elif mode == "occurrence_records":
        records = _list(value.get("records"), "terminology.records")
        for index, record in enumerate(records):
            _record_fields(
                record,
                f"terminology.records[{index}]",
                {
                    "concepts": list,
                    "section": str,
                    "heading": str,
                    "role": str,
                    "fingerprint": str,
                },
            )
            _strings(record["concepts"], f"terminology.records[{index}].concepts")
        if len(records) != len(request.get("occurrences", [])):
            raise ProtoRingResultShapeError("terminology record count differs from request")
    else:
        _string(value.get("status"), "terminology.status")
        _strings(value.get("diagnostics"), "terminology.diagnostics")


def _adr_parse(request: dict[str, Any], value: dict[str, Any]) -> None:
    mode = request.get("mode")
    key = {
        "load_yaml": "structured",
        "load_json": "structured",
        "parse_adr": "metadata",
        "decision_body": "body_hex",
        "h1": "text",
        "preserved_payload": "payload_hex",
        "sha256": "sha256",
    }.get(mode)
    if key is None:
        raise ProtoRingResultShapeError("ADR parse mode is unknown")
    if key in {"structured", "metadata"}:
        _structured(value.get(key), f"ADR parse {key}")
        if mode == "parse_adr":
            _hex(value.get("body_hex"), "ADR parse body_hex")
    elif mode == "sha256":
        _hex(value.get(key), "ADR parse sha256", exact_bytes=32)
    elif key in {"body_hex", "payload_hex"}:
        _hex(value.get(key), f"ADR parse {key}")
    else:
        _string(value.get(key), f"ADR parse {key}")


def _adr_validation(mode: object, value: dict[str, Any]) -> None:
    if mode == "require_mapping":
        _structured(value.get("value"), "ADR validation value")
    elif mode == "require_string":
        _string(value.get("text"), "ADR validation text")
    elif mode == "require_string_list":
        _strings(value.get("items"), "ADR validation items")
    elif mode in {"relation_target_categories", "relation_target_errors"}:
        errors = _list(value.get("errors"), "ADR relation errors")
        for index, error_value in enumerate(errors):
            error = _mapping(error_value, f"ADR relation errors[{index}]")
            category = _string(error.get("category"), "ADR relation category")
            if category not in {"self_reference", "missing_target"}:
                raise ProtoRingResultShapeError("ADR relation category is unknown")
            if category == "missing_target":
                _string(error.get("target"), "ADR relation target")
    elif mode == "schema_error_labels":
        _boolean(value.get("base_has_error"), "ADR base_has_error")
        _boolean(value.get("overlay_has_error"), "ADR overlay_has_error")
    elif mode in {"schema_error_locations", "schema_errors"}:
        errors = _list(value.get("errors"), "ADR schema errors")
        for index, error_value in enumerate(errors):
            _record_fields(
                error_value,
                f"ADR schema errors[{index}]",
                {"path": str, "schema": str},
            )
        if mode == "schema_error_locations":
            _boolean(value.get("rejected"), "ADR schema rejected")
    else:
        raise ProtoRingResultShapeError("ADR validation mode is unknown")


def _evidence_requirement(value: object, label: str) -> None:
    requirement = _mapping(value, label)
    for name in ("id", "responsibility", "subject_source", "candidate_source"):
        _string(requirement.get(name), f"{label}.{name}")
    instances = _mapping(requirement.get("instances"), f"{label}.instances")
    _string(instances.get("kind"), f"{label}.instances.kind")
    _optional_string(instances.get("source"), f"{label}.instances.source")
    classes = _mapping(
        requirement.get("evidence_classes"), f"{label}.evidence_classes"
    )
    _string(classes.get("kind"), f"{label}.evidence_classes.kind")
    if classes.get("classes") is not None:
        _strings(classes["classes"], f"{label}.evidence_classes.classes")
    _optional_string(classes.get("source"), f"{label}.evidence_classes.source")
    context = _mapping(requirement.get("context"), f"{label}.context")
    _boolean(context.get("required"), f"{label}.context.required")
    _optional_string(context.get("source"), f"{label}.context.source")
    target = requirement.get("target")
    if target is not None:
        target_mapping = _mapping(target, f"{label}.target")
        _string(target_mapping.get("interface"), f"{label}.target.interface")
        _string(target_mapping.get("object"), f"{label}.target.object")


def validate_result(
    operation: str, request: dict[str, Any], raw_value: object
) -> dict[str, Any]:
    """Return a minimally shape-validated operation result."""

    value = _mapping(raw_value, f"{operation} result")
    if operation == "engine.identity":
        _string(value.get("source_repository"), "engine.identity source_repository")
        _string(value.get("source_commit"), "engine.identity source_commit")
        if type(value.get("transport_version")) is not int:
            raise ProtoRingResultShapeError("engine.identity transport_version must be integer")
    elif operation == "repository-governance-state.compose":
        _compose(value)
    elif operation == "repository-integrity.evaluate":
        _integrity(value)
    elif operation == "accepted-adr-body.immutability":
        _string(value.get("status"), "accepted ADR status")
        _optional_string(value.get("category"), "accepted ADR category")
    elif operation == "git-whitespace.validate":
        _string(value.get("status"), "Git whitespace status")
        _strings(value.get("domains"), "Git whitespace domains")
    elif operation == "github-authoritative-ref-monotonicity.observe":
        _string(value.get("status"), "ARM status")
    elif operation == "evidence-requirements.registry":
        requirements = _mapping(value.get("requirements"), "evidence requirements")
        for requirement_id in request.get("requirement_ids", []):
            _evidence_requirement(
                requirements.get(requirement_id),
                f"evidence requirement {requirement_id}",
            )
    elif operation == "exact-evidence-binding.evaluate":
        if request.get("mode") == "evaluate_binding":
            _string(value.get("status"), "exact evidence status")
        elif request.get("mode") == "evaluate_requirement_history":
            _list(value.get("comparisons"), "exact evidence comparisons")
        else:
            raise ProtoRingResultShapeError("exact evidence mode is unknown")
    elif operation == "adr-metadata.parse":
        _adr_parse(request, value)
    elif operation == "adr-metadata.repository-path":
        _string(value.get("relative"), "ADR repository relative path")
    elif operation == "adr-metadata.validation":
        _adr_validation(request.get("mode"), value)
    elif operation == "canonical-adr.resolve":
        _string(value.get("relative_path"), "canonical ADR relative path")
    elif operation.startswith("normative-terminology."):
        _terminology(operation, request, value)
    else:
        raise ProtoRingResultShapeError(f"unsupported operation result: {operation}")
    return value
