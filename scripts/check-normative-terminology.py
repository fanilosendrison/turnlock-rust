#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "docs" / "specification" / "turnlock-spec.md"
DEFAULT_INVENTORY = ROOT / "docs" / "specification" / "terminology-inventory.yaml"
REGISTRY_START = "<!-- normative-terminology-registry:start -->"
REGISTRY_END = "<!-- normative-terminology-registry:end -->"
REGISTRY_HEADERS = (
    "Concept key", "Canonical term", "Canonical anchor", "Accepted aliases", "Deprecated wording", "Term structure",
)
ALLOWED_ROLES = {"canonical-definition", "intent", "obligation", "implication", "reference", "synopsis"}
KEY_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
ANCHOR_PATTERN = re.compile(r'^<a id="(term-[a-z0-9-]+)"></a>$')
SECTION_PATTERN = re.compile(r"^(\d+(?:\.\d+)*[A-Z]?)\b")

@dataclass(frozen=True)
class RegistryEntry:
    key: str
    canonical_term: str
    anchor: str
    aliases: tuple[str, ...]
    deprecated: tuple[str, ...]

    @property
    def expressions(self) -> tuple[str, ...]:
        return (self.canonical_term, *self.aliases, *self.deprecated)

@dataclass(frozen=True)
class Block:
    line: int
    section: str
    heading: str
    text: str

@dataclass(frozen=True)
class Occurrence:
    concepts: tuple[str, ...]
    section: str
    heading: str
    fingerprint: str
    line: int
    canonical: bool

    @property
    def signature(self) -> tuple[tuple[str, ...], str, str, str]:
        return (self.concepts, self.section, self.heading, self.fingerprint)

def normalize_block(text: str) -> str:
    return " ".join(text.split())


def fingerprint_block(text: str) -> str:
    return hashlib.sha256(normalize_block(text).encode("utf-8")).hexdigest()

def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]

def _plain_cell(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        return value[1:-1]
    return value

def _term_list(value: str) -> tuple[str, ...]:
    if value.strip() in {"", "—"}:
        return ()
    return tuple(_plain_cell(item) for item in value.split(";") if item.strip())

def parse_registry(spec: str) -> tuple[list[RegistryEntry], list[str]]:
    errors: list[str] = []
    if spec.count(REGISTRY_START) != 1 or spec.count(REGISTRY_END) != 1:
        return [], ["specification must contain exactly one canonical terminology registry"]
    registry_text = spec.split(REGISTRY_START, 1)[1].split(REGISTRY_END, 1)[0]
    rows = [_table_cells(line) for line in registry_text.splitlines() if line.strip().startswith("|")]
    if len(rows) < 3 or tuple(rows[0]) != REGISTRY_HEADERS:
        return [], ["terminology registry has missing or unexpected table headers"]
    if len(rows[1]) != len(REGISTRY_HEADERS) or any(
        not re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]
    ):
        return [], ["terminology registry has a missing or malformed GFM separator row"]

    entries: list[RegistryEntry] = []
    for row_number, row in enumerate(rows[2:], start=1):
        if len(row) != len(REGISTRY_HEADERS):
            errors.append(f"terminology registry row {row_number} has {len(row)} cells; expected 6")
            continue
        key = _plain_cell(row[0])
        canonical_term = _plain_cell(row[1])
        anchor_match = re.fullmatch(r"\[`[^`]+`\]\(#(term-[a-z0-9-]+)\)", row[2])
        if not KEY_PATTERN.fullmatch(key):
            errors.append(f"invalid terminology concept key: {key!r}")
        if not canonical_term:
            errors.append(f"{key or f'row {row_number}'} has no canonical term")
        if not anchor_match:
            errors.append(f"{key or f'row {row_number}'} has an invalid canonical anchor link")
            continue
        aliases = _term_list(row[3])
        deprecated = _term_list(row[4])
        normalized_terms = [term.casefold() for term in (canonical_term, *aliases, *deprecated)]
        if len(normalized_terms) != len(set(normalized_terms)):
            errors.append(f"{key} repeats a canonical, alias, or deprecated term")
        if not row[5].strip():
            errors.append(f"{key} has no term-structure classification")
        entries.append(
            RegistryEntry(key, canonical_term, anchor_match.group(1), aliases, deprecated)
        )

    keys = [entry.key for entry in entries]
    anchors = [entry.anchor for entry in entries]
    if len(keys) != len(set(keys)):
        errors.append("terminology registry contains duplicate concept keys")
    if len(anchors) != len(set(anchors)):
        errors.append("terminology registry contains duplicate canonical destinations")
    return entries, errors

def parse_blocks(spec: str) -> tuple[list[Block], dict[str, tuple[int, str, str]]]:
    blocks: list[Block] = []
    anchors: dict[str, tuple[int, str, str]] = {}
    paragraph: list[str] = []
    paragraph_line = 0
    section = ""
    heading = ""
    in_registry = False
    fence: list[str] | None = None
    fence_line = 0
    fence_token = ""

    def flush_paragraph() -> None:
        nonlocal paragraph, paragraph_line
        if paragraph:
            blocks.append(Block(paragraph_line, section, heading, "\n".join(paragraph)))
            paragraph = []
            paragraph_line = 0

    for line_number, line in enumerate(spec.splitlines(), start=1):
        if line.strip() == REGISTRY_START:
            flush_paragraph()
            in_registry = True
            continue
        if line.strip() == REGISTRY_END:
            in_registry = False
            continue
        if in_registry:
            continue
        if fence is not None:
            fence.append(line)
            if line.strip().startswith(fence_token):
                blocks.append(Block(fence_line, section, heading, "\n".join(fence)))
                fence = None
            continue
        fence_match = re.match(r"^\s*(```|~~~)", line)
        if fence_match:
            flush_paragraph()
            fence = [line]
            fence_line = line_number
            fence_token = fence_match.group(1)
            continue
        heading_match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if heading_match:
            flush_paragraph()
            heading = heading_match.group(1)
            section_match = SECTION_PATTERN.match(heading)
            section = section_match.group(1) if section_match else ""
            continue
        anchor_match = ANCHOR_PATTERN.fullmatch(line.strip())
        if anchor_match:
            flush_paragraph()
            anchor = anchor_match.group(1)
            if anchor in anchors:
                anchors[anchor] = (-1, section, heading)
            else:
                anchors[anchor] = (line_number, section, heading)
            continue
        if not line.strip():
            flush_paragraph()
            continue
        if line.lstrip().startswith("<!--"):
            flush_paragraph()
            continue
        if not paragraph:
            paragraph_line = line_number
        paragraph.append(line)
    flush_paragraph()
    return blocks, anchors

def _definition_concepts(block: Block, entries: list[RegistryEntry]) -> set[str]:
    plain = re.sub(r"[`*_~]", "", block.text)
    concepts: set[str] = set()
    for entry in entries:
        for expression in entry.expressions:
            escaped = re.escape(expression)
            boundary_expression = rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"
            prose = rf"(?:\b(?:a|an|the)\s+)?[\"'“”]?{boundary_expression}[\"'“”]?\s+(?:is\b|are\b|means?\b|refers?\s+to\b|(?:is|are)\s+defined\s+(?:as|by)\b)"
            equation = rf"(?m)^\s*[\"'“”]?{boundary_expression}[\"'“”]?\s*(?::=|=(?!=))"
            if re.search(prose, plain, flags=re.IGNORECASE) or re.search(equation, plain, flags=re.IGNORECASE):
                concepts.add(entry.key)
                break
    return concepts

def discover_occurrences(spec: str, entries: list[RegistryEntry]) -> tuple[list[Occurrence], list[str]]:
    blocks, anchors = parse_blocks(spec)
    errors: list[str] = []
    registered_anchors = {entry.anchor for entry in entries}
    for anchor in sorted(set(anchors) - registered_anchors):
        errors.append(f"canonical terminology anchor is not registered: {anchor}")
    canonical_by_block: dict[int, set[str]] = {}
    occurrences: list[Occurrence] = []

    for entry in entries:
        anchor_info = anchors.get(entry.anchor)
        if anchor_info is None:
            errors.append(f"canonical anchor is missing: {entry.anchor}")
            continue
        anchor_line, section, heading = anchor_info
        if anchor_line < 0:
            errors.append(f"canonical anchor occurs more than once: {entry.anchor}")
            continue
        if not section.startswith("2"):
            errors.append(f"canonical anchor {entry.anchor} is outside Section 2")
            continue
        block_index = next((index for index, block in enumerate(blocks) if block.line > anchor_line), None)
        if block_index is None or blocks[block_index].section != section:
            errors.append(f"canonical anchor {entry.anchor} is not followed by a definition block")
            continue
        block = blocks[block_index]
        intervening_anchor = any(
            anchor_line < other_line < block.line
            for other_line, _, _ in anchors.values()
            if other_line >= 0
        )
        if intervening_anchor:
            errors.append(f"canonical anchor {entry.anchor} is not immediately followed by its definition block")
            continue
        if entry.key not in _definition_concepts(block, [entry]):
            errors.append(f"canonical anchor {entry.anchor} does not lead to a definition of {entry.canonical_term}")
            continue
        canonical_by_block.setdefault(block_index, set()).add(entry.key)
        occurrences.append(Occurrence((entry.key,), section, heading, fingerprint_block(block.text), block.line, True))

    for index, block in enumerate(blocks):
        concepts = _definition_concepts(block, entries) - canonical_by_block.get(index, set())
        if concepts:
            occurrences.append(
                Occurrence(tuple(sorted(concepts)), block.section, block.heading, fingerprint_block(block.text), block.line, False)
            )
    return occurrences, errors

def _suggested_role(occurrence: Occurrence) -> str:
    if occurrence.canonical:
        return "canonical-definition"
    roles = (("0", "intent"), ("3", "obligation"), ("5", "implication"), ("8", "synopsis"))
    return next((role for prefix, role in roles if occurrence.section.startswith(prefix)), "reference")

def occurrence_record(occurrence: Occurrence) -> dict[str, Any]:
    return {
        "concepts": list(occurrence.concepts),
        "section": occurrence.section,
        "heading": occurrence.heading,
        "role": _suggested_role(occurrence),
        "fingerprint": occurrence.fingerprint,
    }

def check_document(spec: str, inventory: Any) -> list[str]:
    entries, errors = parse_registry(spec)
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
    fingerprint_policy = inventory.get("fingerprint")
    if fingerprint_policy != {"algorithm": "sha256", "normalization": "collapse-whitespace"}:
        errors.append("terminology inventory has an unexpected fingerprint policy")

    known_keys = {entry.key for entry in entries}
    actual = Counter(occurrence.signature for occurrence in occurrences)
    recorded: Counter[tuple[tuple[str, ...], str, str, str]] = Counter()
    inventory_occurrences = inventory.get("occurrences")
    if not isinstance(inventory_occurrences, list):
        errors.append("terminology inventory occurrences must be a list")
        inventory_occurrences = []
    for index, item in enumerate(inventory_occurrences, start=1):
        label = f"terminology inventory occurrence {index}"
        if not isinstance(item, dict):
            errors.append(f"{label} must be a mapping")
            continue
        concepts = item.get("concepts")
        if not isinstance(concepts, list) or not concepts or any(not isinstance(value, str) for value in concepts):
            errors.append(f"{label} must contain a non-empty concepts list")
            continue
        concepts_tuple = tuple(sorted(concepts))
        unknown = sorted(set(concepts_tuple) - known_keys)
        if unknown:
            errors.append(f"{label} references unknown concepts: {', '.join(unknown)}")
        role = item.get("role")
        if not isinstance(role, str) or role not in ALLOWED_ROLES:
            errors.append(f"{label} has invalid role: {role!r}")
        fingerprint = item.get("fingerprint")
        if not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
            errors.append(f"{label} has an invalid SHA-256 fingerprint")
            continue
        signature = (concepts_tuple, str(item.get("section", "")), str(item.get("heading", "")), fingerprint)
        recorded[signature] += 1
        matching = [occurrence for occurrence in occurrences if occurrence.signature == signature]
        if matching:
            expected_role = _suggested_role(matching[0])
            if role != expected_role:
                errors.append(f"{label} must use role {expected_role!r}, not {role!r}")

    for signature, count in (actual - recorded).items():
        concepts, section, heading, _ = signature
        lines = [str(item.line) for item in occurrences if item.signature == signature]
        errors.append(
            f"unreviewed definition-like occurrence for {', '.join(concepts)} in Section {section} "
            f"({heading}) near line {', '.join(lines[:count])}"
        )
    for signature, count in (recorded - actual).items():
        concepts, section, heading, _ = signature
        errors.append(
            f"stale terminology inventory entry for {', '.join(concepts)} in Section {section} "
            f"({heading}); unmatched copies: {count}"
        )
    return errors

def check_paths(spec_path: Path = DEFAULT_SPEC, inventory_path: Path = DEFAULT_INVENTORY) -> list[str]:
    spec = spec_path.read_text(encoding="utf-8")
    if not inventory_path.exists():
        inventory: Any = None
    else:
        try:
            inventory = yaml.safe_load(inventory_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            return [f"cannot parse terminology inventory: {error}"]
    return check_document(spec, inventory)

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check canonical terminology structure and likely competing definitions; this is not semantic proof."
    )
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--list-occurrences", action="store_true")
    args = parser.parse_args()
    spec = args.spec.read_text(encoding="utf-8")
    entries, registry_errors = parse_registry(spec)
    if args.list_occurrences:
        occurrences, occurrence_errors = discover_occurrences(spec, entries)
        errors = [*registry_errors, *occurrence_errors]
        if errors:
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print(yaml.safe_dump({"occurrences": [occurrence_record(item) for item in occurrences]}, sort_keys=False))
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
    sys.exit(main())
