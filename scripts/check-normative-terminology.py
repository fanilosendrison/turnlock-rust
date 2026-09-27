#!/usr/bin/env python3
"""Bind Turnlock terminology policy to the shared proto-ring engine."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

from proto_ring import normative_terminology as shared_terminology
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "docs" / "specification" / "turnlock-spec.md"
DEFAULT_INVENTORY = ROOT / "docs" / "specification" / "terminology-inventory.yaml"
REGISTRY_START = "<!-- normative-terminology-registry:start -->"
REGISTRY_END = "<!-- normative-terminology-registry:end -->"
REGISTRY_HEADERS = (
    "Concept key",
    "Canonical term",
    "Canonical anchor",
    "Accepted aliases",
    "Deprecated wording",
    "Term structure",
)
ALLOWED_ROLES = frozenset(
    {
        "canonical-definition",
        "intent",
        "obligation",
        "implication",
        "reference",
        "synopsis",
    }
)
KEY_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
ANCHOR_PATTERN = re.compile(r'^<a id="(term-[a-z0-9-]+)"></a>$')
ANCHOR_LINK_PATTERN = r"\[`[^`]+`\]\(#(term-[a-z0-9-]+)\)"
SECTION_PATTERN = re.compile(r"^(\d+(?:\.\d+)*[A-Z]?)\b")

RegistryEntry = shared_terminology.RegistryEntry
Block = shared_terminology.MarkdownBlock
Occurrence = shared_terminology.Occurrence

REGISTRY_FORMAT = shared_terminology.RegistryFormat(
    start_marker=REGISTRY_START,
    end_marker=REGISTRY_END,
    headers=REGISTRY_HEADERS,
    key_pattern=KEY_PATTERN.pattern,
    anchor_link_pattern=ANCHOR_LINK_PATTERN,
    anchor_pattern=ANCHOR_PATTERN.pattern,
)


def _section_from_heading(heading: str) -> str:
    match = SECTION_PATTERN.match(heading)
    return match.group(1) if match else ""


def _in_section_hierarchy(section: str, root: str) -> bool:
    return section == root or section.startswith(f"{root}.")


def _canonical_location(_entry: RegistryEntry, block: Block) -> bool:
    return _in_section_hierarchy(block.section, "2")


def _suggested_role(occurrence: Occurrence) -> str:
    if occurrence.canonical:
        return "canonical-definition"
    roles = (
        ("0", "intent"),
        ("3", "obligation"),
        ("5", "implication"),
        ("8", "synopsis"),
    )
    return next(
        (
            role
            for root, role in roles
            if _in_section_hierarchy(occurrence.section, root)
        ),
        "reference",
    )


TERMINOLOGY_POLICY = shared_terminology.TerminologyPolicy(
    registry=REGISTRY_FORMAT,
    section_from_heading=_section_from_heading,
    canonical_location=_canonical_location,
    role_for=_suggested_role,
    allowed_roles=ALLOWED_ROLES,
)


def _turnlock_diagnostic(error: str) -> str:
    replacements = (
        (
            "document must contain exactly one terminology registry",
            "specification must contain exactly one canonical terminology registry",
        ),
        (
            "outside the consumer-defined canonical location",
            "outside Section 2",
        ),
        ("in section ", "in Section "),
    )
    for generic, local in replacements:
        error = error.replace(generic, local)
    return error


def _turnlock_diagnostics(errors: list[str]) -> list[str]:
    return [_turnlock_diagnostic(error) for error in errors]


def normalize_block(text: str) -> str:
    return shared_terminology.normalize_text(text)


def fingerprint_block(text: str) -> str:
    return shared_terminology.fingerprint_text(text)


def parse_registry(spec: str) -> tuple[list[RegistryEntry], list[str]]:
    entries, errors = shared_terminology.parse_registry(spec, REGISTRY_FORMAT)
    return entries, _turnlock_diagnostics(errors)


def parse_blocks(
    spec: str,
) -> tuple[list[Block], dict[str, list[tuple[int, str, str]]]]:
    return shared_terminology.parse_blocks(spec, TERMINOLOGY_POLICY)


def discover_occurrences(
    spec: str, entries: list[RegistryEntry]
) -> tuple[list[Occurrence], list[str]]:
    occurrences, errors = shared_terminology.discover_occurrences(
        spec,
        entries,
        TERMINOLOGY_POLICY,
    )
    return occurrences, _turnlock_diagnostics(errors)


def occurrence_record(occurrence: Occurrence) -> dict[str, object]:
    return shared_terminology.occurrence_record(occurrence, TERMINOLOGY_POLICY)


def check_document(spec: str, inventory: object) -> list[str]:
    entries, errors = parse_registry(spec)
    occurrences: list[Occurrence] = []
    if not errors:
        occurrences, occurrence_errors = discover_occurrences(spec, entries)
        errors.extend(occurrence_errors)

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

    reconciliation_errors = shared_terminology.reconcile_inventory(
        entries,
        occurrences,
        inventory.get("occurrences"),
        TERMINOLOGY_POLICY,
    )
    errors.extend(_turnlock_diagnostics(reconciliation_errors))
    return errors


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
    entries, registry_errors = parse_registry(spec)
    if args.list_occurrences:
        occurrences: list[Occurrence] = []
        occurrence_errors: list[str] = []
        if not registry_errors:
            occurrences, occurrence_errors = discover_occurrences(spec, entries)
        errors = [*registry_errors, *occurrence_errors]
        if errors:
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print(
            yaml.safe_dump(
                {"occurrences": [occurrence_record(item) for item in occurrences]},
                sort_keys=False,
            )
        )
        return 0

    errors = check_paths(args.spec, args.inventory)
    if errors:
        print("normative terminology check: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "normative terminology check: OK "
        "(structural and heuristic consistency; not semantic proof)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
