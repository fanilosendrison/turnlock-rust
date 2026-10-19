#!/usr/bin/env python3
"""Bind unchanged Turnlock terminology policy to native proto-ring."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
import re
import sys

from proto_ring_executable_binding import ProtoRingExecutableError, invoke_compat_result
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "docs/specification/turnlock-spec.md"
DEFAULT_INVENTORY = ROOT / "docs/specification/terminology-inventory.yaml"

REGISTRY_FORMAT = {
    "start_marker": "<!-- normative-terminology-registry:start -->",
    "end_marker": "<!-- normative-terminology-registry:end -->",
    "headers": [
        "Concept key",
        "Canonical term",
        "Canonical anchor",
        "Accepted aliases",
        "Deprecated wording",
        "Term structure",
    ],
    "key_pattern": "^[a-z][a-z0-9-]*$",
    "anchor_link_pattern": r"\[`[^`]+`\]\(#(term-[a-z0-9-]+)\)",
    "anchor_pattern": '^<a id="(term-[a-z0-9-]+)"></a>$',
}
TERMINOLOGY_POLICY = {
    "allowed_roles": [
        "canonical-definition",
        "intent",
        "obligation",
        "implication",
        "reference",
        "synopsis",
    ],
    "section_from_heading": {
        "kind": "numbered_dotted_prefix_optional_uppercase_word_boundary"
    },
    "canonical_location": {"kind": "section_hierarchy", "root": "2"},
    "role_policy": {
        "canonical": "canonical-definition",
        "noncanonical_rules": [
            {"matcher": {"kind": "section_hierarchy", "value": "0"}, "role": "intent"},
            {"matcher": {"kind": "section_hierarchy", "value": "3"}, "role": "obligation"},
            {"matcher": {"kind": "section_hierarchy", "value": "5"}, "role": "implication"},
            {"matcher": {"kind": "section_hierarchy", "value": "8"}, "role": "synopsis"},
        ],
        "other_noncanonical": "reference",
    },
}


@dataclass(frozen=True)
class RegistryEntry:
    key: str
    canonical_term: str
    anchor: str
    aliases: list[str]
    deprecated: list[str]
    term_structure: str


@dataclass(frozen=True)
class Block:
    line: int
    section: str
    heading: str
    text: str


@dataclass(frozen=True)
class Occurrence:
    concepts: list[str]
    section: str
    heading: str
    fingerprint: str
    line: int
    canonical: bool


def _invoke(operation: str, payload: dict[str, object]) -> dict[str, object]:
    return invoke_compat_result(ROOT, operation, payload)


def _registry_structure_details(specification: str) -> list[str]:
    try:
        region = specification.split(REGISTRY_FORMAT["start_marker"], 1)[1].split(
            REGISTRY_FORMAT["end_marker"], 1
        )[0]
    except IndexError:
        return []
    keys: list[str] = []
    anchors: list[str] = []
    for line in region.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6 or not cells[0].startswith("`"):
            continue
        keys.append(cells[0].strip("`"))
        match = re.search(r"\(#(term-[a-z0-9-]+)\)", cells[2])
        if match:
            anchors.append(match.group(1))
    details: list[str] = []
    if len(keys) != len(set(keys)):
        details.append("terminology registry contains duplicate concept keys")
    if len(anchors) != len(set(anchors)):
        details.append("terminology registry contains duplicate canonical destinations")
    return details


def _turnlock_diagnostics(
    diagnostics: list[str], specification: str | None = None, entries: list[RegistryEntry] | None = None
) -> list[str]:
    messages = {
        "registry_marker_cardinality": (
            "specification must contain exactly one canonical terminology registry"
        ),
        "registry_structure": "terminology registry structure is invalid",
        "canonical_location_rejected": "canonical definition outside Section 2",
        "missing_canonical_definition": (
            "canonical anchor does not lead to a definition of its registered concept"
        ),
        "unregistered_canonical_anchor": (
            "canonical terminology anchor is not registered"
        ),
        "unreviewed_occurrence": "unreviewed definition-like occurrence",
        "stale_occurrence": "stale terminology inventory entry",
        "role_mismatch": "terminology inventory entry has invalid role",
        "malformed_fingerprint": (
            "terminology inventory entry has malformed fingerprint"
        ),
        "unknown_concept": "terminology inventory entry references unknown concepts",
        "inventory_occurrences_type": (
            "terminology inventory occurrences must be a list"
        ),
    }
    rendered: list[str] = []
    for diagnostic in diagnostics:
        if diagnostic == "registry_structure" and specification is not None:
            details = _registry_structure_details(specification)
            rendered.extend(details or [messages[diagnostic]])
            continue
        if (
            diagnostic == "unregistered_canonical_anchor"
            and specification is not None
            and entries is not None
        ):
            registered = {entry.anchor for entry in entries}
            discovered = set(re.findall(r'<a id="(term-[a-z0-9-]+)"></a>', specification))
            orphans = sorted(discovered - registered)
            rendered.extend(
                f"canonical terminology anchor is not registered: {anchor}"
                for anchor in orphans
            )
            if orphans:
                continue
        rendered.append(messages.get(diagnostic, diagnostic))
    return rendered


def normalize_block(text: str) -> str:
    return _invoke(
        "normative-terminology.fingerprint", {"mode": "normalize_text", "text": text}
    )["text"]


def fingerprint_block(text: str) -> str:
    return _invoke(
        "normative-terminology.fingerprint", {"mode": "fingerprint_text", "text": text}
    )["sha256"]


def parse_registry(spec: str) -> tuple[list[RegistryEntry], list[str]]:
    value = _invoke(
        "normative-terminology.registry",
        {"markdown": spec, "format": REGISTRY_FORMAT},
    )
    entries = [RegistryEntry(**item) for item in value["entries"]]
    return entries, _turnlock_diagnostics(
        list(value["diagnostics"]), spec, entries
    )


def parse_blocks(spec: str) -> tuple[list[Block], dict[str, list[tuple[int, str, str]]]]:
    value = _invoke(
        "normative-terminology.markdown",
        {
            "mode": "parse_blocks",
            "markdown": spec,
            "format": REGISTRY_FORMAT,
            "policy": TERMINOLOGY_POLICY,
        },
    )
    if value["diagnostics"]:
        raise ProtoRingExecutableError(
            "terminology block parsing produced typed diagnostics: "
            + ", ".join(_turnlock_diagnostics(list(value["diagnostics"])))
        )
    anchors = {
        key: [(item["line"], item["section"], item["heading"]) for item in items]
        for key, items in value["anchors"].items()
    }
    return [Block(**item) for item in value["blocks"]], anchors


def discover_occurrences(
    spec: str, _entries: list[RegistryEntry]
) -> tuple[list[Occurrence], list[str]]:
    value = _invoke(
        "normative-terminology.markdown",
        {
            "mode": "discover_occurrences",
            "markdown": spec,
            "format": REGISTRY_FORMAT,
            "policy": TERMINOLOGY_POLICY,
        },
    )
    return [Occurrence(**item) for item in value["occurrences"]], _turnlock_diagnostics(
        list(value["diagnostics"]), spec, _entries
    )


def occurrence_record(occurrence: Occurrence) -> dict[str, object]:
    value = _invoke(
        "normative-terminology.inventory",
        {
            "mode": "occurrence_records",
            "occurrences": [asdict(occurrence)],
            "policy": TERMINOLOGY_POLICY,
        },
    )
    return value["records"][0]


def _inventory_status(
    entries: list[RegistryEntry], occurrences: list[Occurrence], inventory: object
) -> tuple[str, list[str]]:
    value = _invoke(
        "normative-terminology.inventory",
        {
            "mode": "reconcile_inventory",
            "entries": [asdict(item) for item in entries],
            "occurrences": [asdict(item) for item in occurrences],
            "inventory": inventory,
            "policy": TERMINOLOGY_POLICY,
        },
    )
    return value["status"], _turnlock_diagnostics(list(value["diagnostics"]))


def check_document(spec: str, inventory: object) -> list[str]:
    try:
        entries, errors = parse_registry(spec)
        occurrences: list[Occurrence] = []
        if not errors:
            occurrences, discovery_errors = discover_occurrences(spec, entries)
            errors.extend(discovery_errors)
        if not isinstance(inventory, dict):
            return errors + ["terminology inventory must be a YAML mapping"]
        if inventory.get("schema_version") != 1:
            errors.append("terminology inventory must use schema_version 1")
        if inventory.get("authority") != "non-authoritative-review-inventory":
            errors.append("terminology inventory must declare non-authoritative review status")
        if inventory.get("source") != "docs/specification/turnlock-spec.md":
            errors.append("terminology inventory must identify the canonical specification source")
        if inventory.get("fingerprint") != {
            "algorithm": "sha256",
            "normalization": "collapse-whitespace",
        }:
            errors.append("terminology inventory has an unexpected fingerprint policy")
        inventory_occurrences = inventory.get("occurrences")
        if not isinstance(inventory_occurrences, list):
            return errors + ["terminology inventory occurrences must be a list"]
        if any(
            not isinstance(item, dict)
            or not isinstance(item.get("role"), str)
            or item["role"] not in TERMINOLOGY_POLICY["allowed_roles"]
            for item in inventory_occurrences
        ):
            return errors + ["terminology inventory entry has invalid role"]
        status, inventory_errors = _inventory_status(
            entries, occurrences, inventory_occurrences
        )
        errors.extend(inventory_errors)
        if status != "PASS" and not inventory_errors:
            errors.append("terminology inventory reconciliation returned NON_PASS")
        return errors
    except ProtoRingExecutableError as error:
        return [str(error)]


def check_paths(
    spec_path: Path = DEFAULT_SPEC,
    inventory_path: Path = DEFAULT_INVENTORY,
) -> list[str]:
    spec = spec_path.read_text(encoding="utf-8")
    if not inventory_path.exists():
        inventory: object = None
    else:
        try:
            inventory = yaml.safe_load(inventory_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            return [f"cannot parse terminology inventory: {error}"]
    return check_document(spec, inventory)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check canonical terminology structure and likely competing "
            "definitions; this is not semantic proof."
        )
    )
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--list-occurrences", action="store_true")
    args = parser.parse_args()
    spec = args.spec.read_text(encoding="utf-8")
    if args.list_occurrences:
        try:
            entries, registry_errors = parse_registry(spec)
            occurrences, occurrence_errors = (
                discover_occurrences(spec, entries)
                if not registry_errors
                else ([], [])
            )
            errors = [*registry_errors, *occurrence_errors]
            if errors:
                for error in errors:
                    print(f"- {error}", file=sys.stderr)
                return 1
            records = [occurrence_record(item) for item in occurrences]
        except ProtoRingExecutableError as error:
            print(f"- {error}", file=sys.stderr)
            return 1
        print(yaml.safe_dump({"occurrences": records}, sort_keys=False))
        return 0
    errors = check_paths(args.spec, args.inventory)
    if errors:
        print("normative terminology check: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("normative terminology check: OK (structural and heuristic consistency; not semantic proof)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
