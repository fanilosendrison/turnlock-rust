"""Resolve Turnlock's authoritative proto-ring executable binding."""

from __future__ import annotations

from pathlib import Path
import re

PROTO_RING_REPOSITORY = "fanilosendrison/proto-ring"
_DISTRIBUTION_NAME = re.compile(r"([A-Za-z0-9][A-Za-z0-9._-]*)")
_REQUIREMENT = re.compile(
    r"proto-ring\s*@\s*git\+https://github\.com/fanilosendrison/"
    r"proto-ring\.git@([0-9a-f]{40})"
)


def _logical_requirement_lines(text: str) -> list[str]:
    """Join pip-style backslash continuations without interpreting requirements."""

    logical_lines: list[str] = []
    continued = ""
    for physical_line in text.splitlines():
        segment = physical_line.rstrip()
        if segment.endswith("\\"):
            continued += segment[:-1]
            continue
        logical_lines.append(continued + segment)
        continued = ""
    if continued:
        logical_lines.append(continued)
    return logical_lines


def authoritative_proto_ring_commit(root: Path) -> str:
    """Return the one exact proto-ring commit pinned by requirements.txt."""

    requirements_text = (root / "requirements.txt").read_text(encoding="utf-8")
    declarations = []
    for raw_line in _logical_requirement_lines(requirements_text):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        # Requirement comments begin at a hash preceded by whitespace. Preserve
        # URL fragments such as '#egg=' because they can identify a dependency.
        declaration_text = re.split(r"\s+#", line, maxsplit=1)[0].rstrip()
        # PEP 503 name normalization collapses every run of '-', '_' and '.'.
        canonical_names = {
            re.sub(r"[-_.]+", "-", match.group(1)).lower()
            for match in _DISTRIBUTION_NAME.finditer(declaration_text)
        }
        if "proto-ring" in canonical_names:
            declarations.append(declaration_text)
    matches = [
        match.group(1)
        for line in declarations
        if (match := _REQUIREMENT.fullmatch(line)) is not None
    ]
    if len(declarations) != 1 or len(matches) != 1:
        raise ValueError(
            "requirements.txt must contain one exact fanilosendrison/proto-ring "
            "Git pin at a 40-lowercase-hex commit"
        )
    return matches[0]
