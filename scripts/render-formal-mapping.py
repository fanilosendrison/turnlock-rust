#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]

MANIFEST_RELATIVE = Path("formal/verification.yaml")
MIGRATION_RELATIVE = Path("formal/migrations/verification-v2-to-v3-property-audit.yaml")
REVIEW_DIRECTORY_RELATIVE = Path("formal/reviews")
RESULTS_DIRECTORY_RELATIVE = Path("formal/results")
MODEL_RELATIVE = Path("formal/Turnlock.tla")


def _load_checker():
    path = Path(__file__).with_name("check-formal-traceability.py")
    spec = importlib.util.spec_from_file_location("formal_traceability", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MappingRenderError(RuntimeError):
    """Raised when the mapping cannot be rendered from valid repository evidence."""


def _markdown_cell(value: object) -> str:
    text = str(value)
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def _claim_list_markdown(claim_ids: list[str]) -> str:
    if not claim_ids:
        return "—"
    return ", ".join(f"`{claim_id}`" for claim_id in claim_ids)


def _count_records(directory: Path) -> int:
    if not directory.is_dir():
        return 0
    suffixes = {".json", ".yaml", ".yml"}
    return sum(
        1
        for path in sorted(directory.rglob("*"))
        if path.is_file()
        and path.suffix.lower() in suffixes
        and path.name != "review-evidence.schema.json"
    )


def render_mapping(root: Path) -> str:
    root = root.resolve()
    checker = _load_checker()
    data = yaml.safe_load((root / MANIFEST_RELATIVE).read_text(encoding="utf-8"))
    manifest_bytes = (root / MANIFEST_RELATIVE).read_bytes()
    review_records, review_load_errors = checker.load_review_records(root)
    if review_load_errors:
        raise MappingRenderError("\n".join(review_load_errors))
    gate_a = checker.derive_gate_a(data, manifest_bytes, review_records)

    claims = [claim for claim in data.get("claims", []) if isinstance(claim, dict)]
    coverage = [
        entry for entry in data.get("normative_coverage", []) if isinstance(entry, dict)
    ]
    realizations = data.get("formal_realizations", [])
    if not isinstance(realizations, list):
        realizations = []

    migration = yaml.safe_load((root / MIGRATION_RELATIVE).read_text(encoding="utf-8"))
    migration_entries = migration.get("entries", []) if isinstance(migration, dict) else []
    classification_counts: dict[str, int] = {}
    for entry in migration_entries:
        if not isinstance(entry, dict):
            continue
        classification = entry.get("classification")
        if isinstance(classification, str):
            classification_counts[classification] = (
                classification_counts.get(classification, 0) + 1
            )

    evidence_policy = data.get("policy", {}).get("hostile_review", {})
    mechanical_policy = (
        data.get("policy", {}).get("mechanical_evidence", {}).get("tlc", {})
    )
    review_evidence_schema = evidence_policy.get(
        "evidence_schema", "formal/reviews/review-evidence.schema.json"
    )
    tlc_evidence_schema = mechanical_policy.get(
        "evidence_schema", "formal/tlc-result.schema.json"
    )

    lines: list[str] = [
        "# TURNLOCK formal assurance mapping",
        "",
        "> **Generated file.** Source of truth: "
        "[`../../formal/verification.yaml`](../../formal/verification.yaml).",
        "> Regenerate with `.venv/bin/python scripts/render-formal-mapping.py`. "
        "Do not edit manually.",
        "",
        "## Authority and artifact roles",
        "",
        "Normative product authority remains `docs/specification/turnlock-spec.md` "
        "together with accepted ADRs. This document is a generated projection of the "
        "formal-assurance graph; it creates no semantics, no claim, and no "
        "verification result.",
        "",
        "- [`formal/verification.yaml`](../../formal/verification.yaml) owns the "
        "formal-assurance graph: normative provenance, required assurance claims, "
        "coverage, residual assurance, domain bindings, review requirements, and "
        "evidence contracts.",
        "- [`formal/reviews/`](../../formal/reviews/) owns durable hostile "
        "semantic-review evidence for exact reviewed artifacts.",
        "- [`formal/results/`](../../formal/results/) owns concrete mechanism-specific "
        "bounded checker evidence.",
        "- The canonical formal semantic representation (initially integrated TLA+ "
        "after Gate B) will define the checked abstract semantics for the operational "
        "domain. It is not normative product authority.",
        "",
        "## Readiness",
        "",
    ]

    if gate_a["ready"]:
        lines.append("Formal-Architecture-Ready: READY")
        lines.append(f"reason: {gate_a['reason']}")
    else:
        lines.append("Formal-Architecture-Ready: BLOCKED")
        lines.append(f"reason: {gate_a['reason']}")
    lines.extend(
        [
            "",
            "Canonical-Formal-Semantics-Ready:",
            "NOT-APPLICABLE — candidate model absent",
            "",
            "Formal-Verification-Ready:",
            "NOT-APPLICABLE — candidate model absent",
            "",
            "## Normative coverage",
            "",
            "| Invariant | Canonical operational coverage | Formal claims | Residual claims |",
            "|---|---|---|---|",
        ]
    )
    for entry in coverage:
        lines.append(
            f"| `{entry.get('invariant', '—')}` "
            f"| {entry.get('canonical_operational_coverage', '—')} "
            f"| {_claim_list_markdown(entry.get('formal_claims') or [])} "
            f"| {_claim_list_markdown(entry.get('residual_claims') or [])} |"
        )

    lines.extend(
        [
            "",
            "## Required assurance claims",
            "",
            "| Claim | Assurance domain | Modality | Normative sources | Statement |",
            "|---|---|---|---|---|",
        ]
    )
    for claim in claims:
        modality = claim.get("modality")
        modality_text = modality if isinstance(modality, str) else "—"
        sources = claim.get("normative_sources") or []
        sources_text = ", ".join(f"`{source}`" for source in sources) or "—"
        lines.append(
            f"| `{claim.get('id', '—')}` "
            f"| {claim.get('assurance_domain', '—')} "
            f"| {modality_text} "
            f"| {sources_text} "
            f"| {_markdown_cell(claim.get('statement', '—'))} |"
        )

    lines.extend(["", "## Formal realizations", ""])
    if not realizations:
        lines.append("No executable formal realizations are declared yet.")
    else:
        for realization in realizations:
            if not isinstance(realization, dict):
                continue
            claim = realization.get("claim", "—")
            lines.append(
                f"- `{realization.get('backend', '—')}:{realization.get('module', '—')}:"
                f"{claim}` → `{claim}`"
            )

    lines.extend(["", "## Reverse traceability", "", "### Claim → invariant IDs", ""])
    for claim in claims:
        sources = claim.get("normative_sources") or []
        source_text = ", ".join(f"`{source}`" for source in sources) or "—"
        lines.append(f"- `{claim.get('id', '—')}` → {source_text}")
    lines.extend(
        [
            "",
            "Once formal realizations exist, this section also renders "
            "`formal realization identifier → claim IDs → invariant IDs`.",
        ]
    )
    if realizations:
        lines.extend(["", "### Formal realization → claim → invariant IDs", ""])
        for realization in realizations:
            if not isinstance(realization, dict):
                continue
            claim = realization.get("claim", "—")
            claim_record = next(
                (item for item in claims if item.get("id") == claim), {}
            )
            sources = claim_record.get("normative_sources") or []
            source_text = ", ".join(f"`{source}`" for source in sources) or "—"
            lines.append(
                f"- `{realization.get('backend', '—')}:{realization.get('module', '—')}:"
                f"{claim}` → `{claim}` → {source_text}"
            )

    review_count = len(review_records)
    results_count = _count_records(root / RESULTS_DIRECTORY_RELATIVE)
    lines.extend(
        [
            "",
            "## Evidence classes",
            "",
            f"- **Hostile semantic-review evidence** — `formal/reviews/`, schema "
            f"`{review_evidence_schema}`; {review_count} record(s) present.",
            f"- **Mechanical TLC evidence** — `formal/results/`, schema "
            f"`{tlc_evidence_schema}`; {results_count} record(s) present.",
            "- **Future conformance evidence** — not yet represented by a repository "
            "evidence contract.",
            "",
            "## Legacy v2 property migration",
            "",
            f"{len(migration_entries)} historical planned property entries were audited:",
            "",
            f"- {classification_counts.get('required-assurance-claim-candidate', 0)} "
            "migrated to required assurance intent;",
            f"- {classification_counts.get('supporting-model-property-candidate', 0)} "
            "retained only as supporting-model-property candidates;",
            f"- {classification_counts.get('obsolete-or-misplaced-planning-artifact', 0)} "
            "discarded as meaningless.",
            "",
            "Audit: "
            "[`../../formal/migrations/verification-v2-to-v3-property-audit.yaml`]"
            "(../../formal/migrations/verification-v2-to-v3-property-audit.yaml).",
            "",
            "## Notes",
            "",
            "This projection derives its readiness state from repository artifacts and "
            "review evidence. Assurance claims record intended assurance; they are not "
            "verification results. Hostile review is bounded reviewed semantic "
            "correspondence, not mathematical proof. Mechanical checker evidence cannot "
            "by itself support an invariant directly; it is lifted through reviewed "
            "claim/property correspondence and declared coverage.",
            "",
            f"Model presence: `{MODEL_RELATIVE.as_posix()}` "
            + ("exists." if (root / MODEL_RELATIVE).exists() else "does not exist."),
            "",
        ]
    )
    return "\n".join(lines)


def write_mapping(root: Path) -> Path:
    out_path = root / "docs" / "formal" / "invariant-mapping.md"
    out_path.write_text(render_mapping(root), encoding="utf-8", newline="\n")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render the TURNLOCK formal-assurance mapping from the formal manifest"
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="write the rendered mapping to stdout without modifying repository files",
    )
    arguments = parser.parse_args(argv)
    try:
        if arguments.stdout:
            sys.stdout.buffer.write(render_mapping(ROOT).encode("utf-8"))
            return 0
        out_path = write_mapping(ROOT)
    except MappingRenderError as error:
        for line in str(error).splitlines():
            print(f"ERROR: {line}", file=sys.stderr)
        return 1
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
