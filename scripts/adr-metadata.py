#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = Path("docs/adr/adr-profile.yaml")
PROFILE_VERSION = "0.1.0"
BODY_BOUNDARY = re.compile(br"(?m)^## Context(?: |$)")
RELATION_TYPES = ("clarifies", "amends", "supersedes", "confirms")


class AdrMetadataError(ValueError):
    pass


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise AdrMetadataError(f"cannot read YAML {path}: {error}") from error


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AdrMetadataError(f"cannot read JSON {path}: {error}") from error


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decision_body_bytes(data: bytes) -> bytes:
    if data.startswith(b"\xef\xbb\xbf"):
        raise AdrMetadataError("UTF-8 BOM is forbidden")
    if b"\r" in data:
        raise AdrMetadataError("CRLF or bare CR is forbidden; ADRs must use LF")
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise AdrMetadataError(f"ADR is not valid UTF-8: {error}") from error

    boundaries = list(BODY_BOUNDARY.finditer(data))
    if len(boundaries) != 1:
        raise AdrMetadataError(
            "ADR must contain exactly one line beginning with '## Context'"
        )
    return data[boundaries[0].start() :]


def preserved_payload_bytes(data: bytes) -> bytes:
    decision_body_bytes(data)
    headings = list(re.finditer(br"(?m)^# .+$", data))
    if len(headings) != 1:
        raise AdrMetadataError("ADR must contain exactly one H1 heading")
    return data[headings[0].start() :]


def parse_adr(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        data = path.read_bytes()
    except OSError as error:
        raise AdrMetadataError(f"cannot read {path}: {error}") from error
    body = decision_body_bytes(data)
    if not data.startswith(b"---\n"):
        raise AdrMetadataError("ADR has no YAML frontmatter")

    closing = data.find(b"\n---\n", 4)
    if closing < 0:
        raise AdrMetadataError("ADR frontmatter has no closing delimiter")
    try:
        metadata = yaml.safe_load(data[4:closing].decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        raise AdrMetadataError(f"invalid ADR frontmatter: {error}") from error
    if not isinstance(metadata, dict):
        raise AdrMetadataError("ADR frontmatter must be a mapping")
    return metadata, body


def schema_errors(
    metadata: dict[str, Any],
    base_schema: dict[str, Any],
    overlay_schema: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    checker = FormatChecker()
    for label, schema in (("base", base_schema), ("overlay", overlay_schema)):
        try:
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema, format_checker=checker)
        except SchemaError as error:
            errors.append(f"{label} schema is invalid: {error.message}")
            continue
        for error in sorted(validator.iter_errors(metadata), key=lambda item: item.json_path):
            errors.append(f"{label} schema {error.json_path}: {error.message}")
    return errors


def repository_path(root: Path, relative: Any) -> Path:
    if not isinstance(relative, str) or not relative:
        raise AdrMetadataError("repository path must be a non-empty string")
    candidate = Path(relative)
    if candidate.is_absolute():
        raise AdrMetadataError(f"repository path must be relative: {relative}")
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    if not resolved.is_relative_to(resolved_root):
        raise AdrMetadataError(f"repository path escapes root: {relative}")
    return resolved


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AdrMetadataError(f"{label} must be a mapping")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise AdrMetadataError(f"{label} must be a non-empty string")
    return value


def _require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise AdrMetadataError(f"{label} must be a list of non-empty strings")
    if len(value) != len(set(value)):
        raise AdrMetadataError(f"{label} contains duplicates")
    return value


def load_profile(root: Path) -> dict[str, Any]:
    profile = _require_mapping(load_yaml(root / PROFILE_PATH), str(PROFILE_PATH))
    if profile.get("profile_version") != PROFILE_VERSION:
        raise AdrMetadataError(
            f"{PROFILE_PATH} must use profile_version {PROFILE_VERSION}"
        )

    canonical = _require_mapping(profile.get("canonical_schema"), "canonical_schema")
    for key in (
        "id",
        "repository",
        "source_path",
        "source_commit",
        "sha256",
        "vendored_path",
    ):
        _require_string(canonical.get(key), f"canonical_schema.{key}")
    if not re.fullmatch(r"[0-9a-f]{40}", canonical["source_commit"]):
        raise AdrMetadataError("canonical_schema.source_commit must be a full Git SHA")
    if not re.fullmatch(r"[0-9a-f]{64}", canonical["sha256"]):
        raise AdrMetadataError("canonical_schema.sha256 must be lowercase SHA-256")
    if not canonical["repository"].startswith("https://"):
        raise AdrMetadataError("canonical_schema.repository must use HTTPS")

    overlay = _require_mapping(profile.get("local_overlay"), "local_overlay")
    _require_string(overlay.get("id"), "local_overlay.id")
    overlay_hash = _require_string(overlay.get("sha256"), "local_overlay.sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", overlay_hash):
        raise AdrMetadataError("local_overlay.sha256 must be lowercase SHA-256")
    _require_string(overlay.get("path"), "local_overlay.path")

    repository = _require_mapping(profile.get("repository"), "repository")
    for key in (
        "domain",
        "adr_directory",
        "filename_pattern",
        "id_pattern",
        "h1_separator",
    ):
        _require_string(repository.get(key), f"repository.{key}")
    if not isinstance(repository.get("id_width"), int) or repository["id_width"] < 1:
        raise AdrMetadataError("repository.id_width must be a positive integer")
    if repository.get("require_contiguous_ids") is not True:
        raise AdrMetadataError("repository.require_contiguous_ids must be true")
    if repository.get("retain_allocated_ids") is not True:
        raise AdrMetadataError("repository.retain_allocated_ids must be true")
    non_adr = _require_string_list(
        repository.get("non_adr_markdown"), "repository.non_adr_markdown"
    )
    if any(Path(name).name != name or not name.endswith(".md") for name in non_adr):
        raise AdrMetadataError(
            "repository.non_adr_markdown entries must be Markdown basenames"
        )
    try:
        re.compile(repository["filename_pattern"])
        re.compile(repository["id_pattern"])
    except re.error as error:
        raise AdrMetadataError(f"repository regex is invalid: {error}") from error

    legacy = _require_mapping(profile.get("legacy"), "legacy")
    _require_string_list(legacy.get("without_frontmatter"), "legacy.without_frontmatter")
    _require_string_list(legacy.get("null_dates"), "legacy.null_dates")

    generated_index = _require_mapping(profile.get("generated_index"), "generated_index")
    _require_string(generated_index.get("path"), "generated_index.path")
    if not isinstance(generated_index.get("required"), bool):
        raise AdrMetadataError("generated_index.required must be boolean")

    migration = _require_mapping(profile.get("migration_evidence"), "migration_evidence")
    _require_string(migration.get("path"), "migration_evidence.path")
    if not isinstance(migration.get("required"), bool):
        raise AdrMetadataError("migration_evidence.required must be boolean")
    _require_string_list(migration.get("ids"), "migration_evidence.ids")
    baseline = migration.get("baseline_commit")
    if migration["required"]:
        if not isinstance(baseline, str) or not re.fullmatch(r"[0-9a-f]{40}", baseline):
            raise AdrMetadataError(
                "migration_evidence.baseline_commit must be a full Git SHA when required"
            )
    elif baseline is not None:
        raise AdrMetadataError(
            "migration_evidence.baseline_commit must be null when evidence is optional"
        )

    commands = _require_mapping(profile.get("commands"), "commands")
    _require_string(commands.get("check"), "commands.check")
    _require_string(commands.get("render"), "commands.render")
    return profile


def _h1(data: bytes) -> str:
    text = data.decode("utf-8")
    headings = re.findall(r"(?m)^# (.+)$", text)
    if len(headings) != 1:
        raise AdrMetadataError("ADR must contain exactly one H1 heading")
    return headings[0]


def _derived_identity(
    path: Path, filename_pattern: re.Pattern[str], id_width: int
) -> tuple[str, str, int]:
    match = filename_pattern.fullmatch(path.name)
    if match is None:
        raise AdrMetadataError("filename does not match repository.filename_pattern")
    number_text = match.group("number")
    slug = match.group("slug")
    if len(number_text) != id_width:
        raise AdrMetadataError(f"filename number must use exactly {id_width} digits")
    number = int(number_text)
    if number < 1:
        raise AdrMetadataError("ADR number must be positive")
    return f"ADR-{number_text}", slug, number


def _load_schemas(
    root: Path, profile: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    errors: list[str] = []
    canonical = profile["canonical_schema"]
    try:
        vendored_path = repository_path(root, canonical["vendored_path"])
        vendored_bytes = vendored_path.read_bytes()
    except (AdrMetadataError, OSError) as error:
        return {}, {}, [f"canonical schema: {error}"]

    actual_hash = sha256_hex(vendored_bytes)
    if actual_hash != canonical["sha256"]:
        errors.append(
            "vendored canonical schema SHA-256 mismatch: "
            f"expected {canonical['sha256']}, found {actual_hash}"
        )
    try:
        base = json.loads(vendored_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"vendored canonical schema is invalid JSON: {error}")
        base = {}
    if not isinstance(base, dict):
        errors.append("vendored canonical schema must be a JSON object")
        base = {}
    if base.get("$id") != canonical["id"]:
        errors.append(
            "vendored canonical schema $id mismatch: "
            f"expected {canonical['id']}, found {base.get('$id')}"
        )

    try:
        overlay_path = repository_path(root, profile["local_overlay"]["path"])
        overlay_bytes = overlay_path.read_bytes()
        overlay = json.loads(overlay_bytes.decode("utf-8"))
    except (AdrMetadataError, OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"local overlay: {error}")
        overlay_bytes = b""
        overlay = {}
    if not isinstance(overlay, dict):
        errors.append("local overlay schema must be a JSON object")
        overlay = {}
    overlay_hash = sha256_hex(overlay_bytes)
    if overlay_hash != profile["local_overlay"]["sha256"]:
        errors.append(
            "local overlay SHA-256 mismatch: expected "
            f"{profile['local_overlay']['sha256']}, found {overlay_hash}"
        )
    if not overlay:
        errors.append("local overlay must be a non-empty JSON Schema")
    if overlay.get("$id") != profile["local_overlay"]["id"]:
        errors.append(
            "local overlay $id mismatch: expected "
            f"{profile['local_overlay']['id']}, found {overlay.get('$id')}"
        )

    properties = overlay.get("properties")
    required = overlay.get("required")
    if not isinstance(properties, dict):
        properties = {}
    if not isinstance(required, list):
        required = []
    expected_constraints = {
        "adr_profile_version": ("const", profile["profile_version"]),
        "domain": ("const", profile["repository"]["domain"]),
        "id": ("pattern", profile["repository"]["id_pattern"]),
    }
    for field, (keyword, expected) in expected_constraints.items():
        constraint = properties.get(field)
        if not isinstance(constraint, dict) or constraint.get(keyword) != expected:
            errors.append(f"local overlay {field} constraint mismatch")
        if field not in required:
            errors.append(f"local overlay must require {field}")
    return base, overlay, errors


def _git_baseline_blob(root: Path, commit: str, relative_path: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{relative_path}"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise AdrMetadataError(
            f"baseline commit {commit} cannot provide {relative_path}: {detail}"
        )
    return result.stdout


def _migration_evidence_errors(
    root: Path,
    profile: dict[str, Any],
    records_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    section = profile["migration_evidence"]
    if not section["required"]:
        return []
    errors: list[str] = []
    try:
        path = repository_path(root, section["path"])
        evidence = _require_mapping(load_yaml(path), section["path"])
    except AdrMetadataError as error:
        return [f"migration evidence: {error}"]

    baseline = section["baseline_commit"]
    if evidence.get("schema_version") != 1:
        errors.append("migration evidence must use schema_version 1")
    if evidence.get("profile_version") != profile["profile_version"]:
        errors.append("migration evidence profile_version mismatch")
    if evidence.get("baseline_commit") != baseline:
        errors.append("migration evidence baseline_commit does not match profile")

    ancestor = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", baseline, "HEAD"],
        check=False,
        capture_output=True,
    )
    if ancestor.returncode != 0:
        detail = ancestor.stderr.decode("utf-8", errors="replace").strip()
        errors.append(
            f"migration baseline commit {baseline} is unavailable or not an ancestor"
            + (f": {detail}" if detail else "")
        )

    expected = set(section["ids"])
    entries = evidence.get("records")
    if not isinstance(entries, list):
        return errors + ["migration evidence records must be a list"]

    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("migration evidence record must be a mapping")
            continue
        adr_id = entry.get("id")
        if not isinstance(adr_id, str):
            errors.append("migration evidence record id must be a string")
            continue
        if adr_id in seen:
            errors.append(f"duplicate migration evidence record {adr_id}")
        seen.add(adr_id)
        record = records_by_id.get(adr_id)
        if record is None:
            errors.append(f"migration evidence references missing {adr_id}")
            continue
        if entry.get("path") != record["relative_path"]:
            errors.append(f"migration evidence {adr_id} path mismatch")
            continue

        try:
            baseline_bytes = _git_baseline_blob(
                root, baseline, record["relative_path"]
            )
            baseline_payload = preserved_payload_bytes(baseline_bytes)
            current_payload = preserved_payload_bytes(record["data"])
            baseline_body = decision_body_bytes(baseline_bytes)
        except AdrMetadataError as error:
            errors.append(f"migration evidence {adr_id}: {error}")
            continue

        if baseline_payload != baseline_bytes:
            errors.append(
                f"migration evidence {adr_id}: baseline file must begin at its H1"
            )
        if current_payload != baseline_bytes:
            errors.append(
                f"migration evidence {adr_id}: H1-to-EOF payload differs from baseline"
            )

        expected_hashes = {
            "baseline_file_sha256": sha256_hex(baseline_bytes),
            "migrated_payload_sha256": sha256_hex(current_payload),
            "before_decision_body_sha256": sha256_hex(baseline_body),
            "after_decision_body_sha256": sha256_hex(record["body"]),
        }
        for field, expected_hash in expected_hashes.items():
            if entry.get(field) != expected_hash:
                errors.append(
                    f"migration evidence {adr_id} {field} does not match actual bytes"
                )

    if seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        if missing:
            errors.append("migration evidence missing IDs: " + ", ".join(missing))
        if extra:
            errors.append("migration evidence has unexpected IDs: " + ", ".join(extra))
    return errors


def collect_errors(root: Path, *, check_generated: bool = True) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    try:
        profile = load_profile(root)
    except AdrMetadataError as error:
        return [str(error)]

    base_schema, overlay_schema, schema_load_errors = _load_schemas(root, profile)
    errors.extend(schema_load_errors)
    repository = profile["repository"]
    try:
        adr_directory = repository_path(root, repository["adr_directory"])
    except AdrMetadataError as error:
        return errors + [str(error)]
    filename_pattern = re.compile(repository["filename_pattern"])
    id_pattern = re.compile(repository["id_pattern"])
    id_width = repository["id_width"]
    separator = repository["h1_separator"]
    legacy_ids = set(profile["legacy"]["without_frontmatter"])
    null_date_ids = set(profile["legacy"]["null_dates"])

    excluded_markdown = set(repository["non_adr_markdown"])
    paths = sorted(
        path
        for path in adr_directory.glob("*.md")
        if path.name not in excluded_markdown
    )
    records_by_id: dict[str, dict[str, Any]] = {}
    legacy_found: set[str] = set()
    numbers: list[int] = []

    for path in paths:
        prefix = path.relative_to(root).as_posix()
        try:
            derived_id, _filename_slug, number = _derived_identity(
                path, filename_pattern, id_width
            )
        except AdrMetadataError as error:
            errors.append(f"{prefix}: {error}")
            continue
        numbers.append(number)
        if derived_id in records_by_id:
            errors.append(f"duplicate ADR identity {derived_id}")
            continue

        try:
            data = path.read_bytes()
            body = decision_body_bytes(data)
            heading = _h1(data)
        except (OSError, UnicodeError, AdrMetadataError) as error:
            errors.append(f"{prefix}: {error}")
            continue

        record = {
            "id": derived_id,
            "path": path,
            "relative_path": prefix,
            "data": data,
            "body": body,
            "metadata": None,
        }
        records_by_id[derived_id] = record

        if not data.startswith(b"---\n"):
            legacy_found.add(derived_id)
            if derived_id not in legacy_ids:
                errors.append(
                    f"{prefix}: {derived_id} is frontmatter-free but not allowlisted"
                )
            expected_prefix = derived_id + separator
            if not heading.startswith(expected_prefix):
                errors.append(
                    f"{prefix}: H1 must begin with {expected_prefix!r}, found {heading!r}"
                )
            continue

        if derived_id in legacy_ids:
            errors.append(
                f"{prefix}: stale legacy without_frontmatter entry {derived_id}"
            )
        try:
            metadata, parsed_body = parse_adr(path)
        except AdrMetadataError as error:
            errors.append(f"{prefix}: {error}")
            continue
        record["metadata"] = metadata
        record["body"] = parsed_body
        for error in schema_errors(metadata, base_schema, overlay_schema):
            errors.append(f"{prefix}: {error}")

        metadata_id = metadata.get("id")
        if metadata_id != derived_id:
            errors.append(
                f"{prefix}: metadata id {metadata_id!r} does not match {derived_id}"
            )
        elif not id_pattern.fullmatch(metadata_id):
            errors.append(f"{prefix}: metadata id violates repository.id_pattern")

        name = metadata.get("name")
        if isinstance(name, str):
            expected_h1 = derived_id + separator + name
            if heading != expected_h1:
                errors.append(
                    f"{prefix}: H1 {heading!r} does not equal {expected_h1!r}"
                )

        actual_body_hash = sha256_hex(parsed_body)
        if metadata.get("decision_body_sha256") != actual_body_hash:
            errors.append(
                f"{prefix}: decision_body_sha256 mismatch; expected {actual_body_hash}"
            )

        date = metadata.get("date")
        if date is None and derived_id not in null_date_ids:
            errors.append(f"{prefix}: null date is not allowlisted for {derived_id}")
        if date is not None and derived_id in null_date_ids:
            errors.append(f"{prefix}: stale legacy null_dates entry {derived_id}")

    all_ids = set(records_by_id)
    for adr_id in sorted(legacy_ids - legacy_found):
        errors.append(f"stale legacy without_frontmatter entry {adr_id}")
    for adr_id in sorted(null_date_ids - all_ids):
        errors.append(f"stale legacy null_dates entry {adr_id}")

    if len(numbers) != len(set(numbers)):
        errors.append("duplicate ADR numbers")
    if numbers:
        expected_numbers = list(range(1, max(numbers) + 1))
        if sorted(numbers) != expected_numbers:
            errors.append(
                "ADR IDs must be contiguous from 1 through " + str(max(numbers))
            )

    for adr_id, record in sorted(records_by_id.items()):
        metadata = record["metadata"]
        if not isinstance(metadata, dict):
            continue
        relations = metadata.get("relations")
        if not isinstance(relations, dict):
            continue
        for relation_type in RELATION_TYPES:
            targets = relations.get(relation_type)
            if not isinstance(targets, list):
                continue
            for target in targets:
                if target == adr_id:
                    errors.append(
                        f"{record['relative_path']}: {relation_type} cannot reference itself"
                    )
                elif target not in all_ids:
                    errors.append(
                        f"{record['relative_path']}: {relation_type} references missing {target}"
                    )

    errors.extend(_migration_evidence_errors(root, profile, records_by_id))

    generated = profile["generated_index"]
    if check_generated and generated["required"]:
        try:
            expected_index = render_index(root)
            index_path = repository_path(root, generated["path"])
            actual_index = index_path.read_text(encoding="utf-8")
            if actual_index != expected_index:
                errors.append(
                    f"generated ADR index is stale; run {profile['commands']['render']}"
                )
        except (AdrMetadataError, OSError, UnicodeError) as error:
            errors.append(f"generated ADR index: {error}")
    return errors


def _structured_records(root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    profile = load_profile(root)
    adr_directory = repository_path(root, profile["repository"]["adr_directory"])
    filename_pattern = re.compile(profile["repository"]["filename_pattern"])
    id_width = profile["repository"]["id_width"]
    records: list[dict[str, Any]] = []
    for path in sorted(adr_directory.glob("adr-*.md")):
        adr_id, _, number = _derived_identity(path, filename_pattern, id_width)
        try:
            metadata, body = parse_adr(path)
        except AdrMetadataError as error:
            raise AdrMetadataError(
                f"cannot render while {adr_id} is unstructured: {error}"
            ) from error
        records.append(
            {
                "id": adr_id,
                "number": number,
                "path": path,
                "relative_path": path.relative_to(root).as_posix(),
                "metadata": metadata,
                "body": body,
            }
        )
    records.sort(key=lambda record: record["number"])
    return profile, records


def render_index(root: Path) -> str:
    profile, records = _structured_records(root.resolve())
    domain = profile["repository"]["domain"]
    lines = [
        "---",
        'okf_version: "1.0"',
        'kind: "KnowledgeAsset"',
        'asset_type: "generated-architecture-decision-index"',
        f'domain: "{domain}"',
        'severity: "strict"',
        'name: "Generated TURNLOCK Architecture Decision Record index"',
        "---",
        "",
        "# Generated TURNLOCK Architecture Decision Record index",
        "",
        "> Generated by `scripts/adr-metadata.py`. Do not edit manually.",
        "> Source frontmatter stores outgoing relations; incoming relations below",
        "> are derived projections complete only relative to recorded assertions.",
        "",
        "## Decisions",
        "",
        "| ID | Decision | Status | Date |",
        "|---|---|---|---|",
    ]
    path_by_id = {record["id"]: record["path"].name for record in records}
    for record in records:
        metadata = record["metadata"]
        date = metadata["date"] if metadata["date"] is not None else "Unknown"
        lines.append(
            f"| [{record['id']}]({record['path'].name}) | {metadata['name']} | "
            f"{metadata['status']} | {date} |"
        )

    outgoing: list[tuple[str, str, str]] = []
    incoming: list[tuple[str, str, str]] = []
    inverse = {
        "clarifies": "clarified by",
        "amends": "amended by",
        "supersedes": "superseded by",
        "confirms": "confirmed by",
    }
    for record in records:
        relations = record["metadata"]["relations"]
        for relation_type in RELATION_TYPES:
            for target in relations[relation_type]:
                outgoing.append((record["id"], relation_type, target))
                incoming.append((target, inverse[relation_type], record["id"]))

    lines.extend(
        [
            "",
            "## Recorded outgoing relations",
            "",
            "| Source | Relation | Target |",
            "|---|---|---|",
        ]
    )
    if outgoing:
        for source, relation, target in sorted(outgoing):
            lines.append(
                f"| [{source}]({path_by_id[source]}) | {relation} | "
                f"[{target}]({path_by_id[target]}) |"
            )
    else:
        lines.append("| — | — | — |")

    lines.extend(
        [
            "",
            "## Derived incoming relations",
            "",
            "| Target | Relation | Source |",
            "|---|---|---|",
        ]
    )
    if incoming:
        for target, relation, source in sorted(incoming):
            lines.append(
                f"| [{target}]({path_by_id[target]}) | {relation} | "
                f"[{source}]({path_by_id[source]}) |"
            )
    else:
        lines.append("| — | — | — |")
    lines.append("")
    return "\n".join(lines)


def check_command(root: Path) -> int:
    errors = collect_errors(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"ADR metadata: FAILED ({len(errors)} errors)", file=sys.stderr)
        return 1
    profile, records = _structured_records_if_possible(root)
    legacy_count = len(profile["legacy"]["without_frontmatter"])
    print(f"ADR metadata: OK ({len(records)} structured, {legacy_count} legacy)")
    return 0


def _structured_records_if_possible(
    root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    profile = load_profile(root)
    adr_directory = repository_path(root, profile["repository"]["adr_directory"])
    records: list[dict[str, Any]] = []
    for path in sorted(adr_directory.glob("adr-*.md")):
        if path.read_bytes().startswith(b"---\n"):
            metadata, body = parse_adr(path)
            records.append({"path": path, "metadata": metadata, "body": body})
    return profile, records


def render_command(root: Path) -> int:
    errors = collect_errors(root, check_generated=False)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("ADR index rendering refused because source validation failed", file=sys.stderr)
        return 1
    try:
        profile = load_profile(root)
        rendered = render_index(root)
        output_path = repository_path(root, profile["generated_index"]["path"])
        output_path.write_text(rendered, encoding="utf-8", newline="\n")
    except (AdrMetadataError, OSError, UnicodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Rendered {output_path.relative_to(root)}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and render TURNLOCK ADR metadata")
    parser.add_argument("command", choices=("check", "render"))
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    arguments = parse_args(argv)
    root = arguments.root.resolve()
    if arguments.command == "check":
        return check_command(root)
    return render_command(root)


if __name__ == "__main__":
    raise SystemExit(main())
