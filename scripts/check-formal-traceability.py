#!/usr/bin/env python3
from pathlib import Path
import json
import re
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]


def collect_errors(root: Path, *, check_generated: bool = True) -> tuple[list[str], int]:
    root = root.resolve()
    manifest_path = root / "formal" / "verification.yaml"
    spec_path = root / "docs" / "specification" / "turnlock-spec.md"
    adr_dir = root / "docs" / "adr"
    mapping_path = root / "docs" / "formal" / "invariant-mapping.md"

    data = yaml.safe_load(manifest_path.read_text())
    errors: list[str] = []

    if data.get("schema_version") != 2:
        errors.append("formal/verification.yaml must use schema_version 2")

    invariants = data.get("invariants", [])
    ids = [i["id"] for i in invariants]
    if len(ids) != len(set(ids)):
        errors.append("duplicate invariant IDs in formal/verification.yaml")

    spec = spec_path.read_text()
    heading_ids = re.findall(r"^##\s+[^\n]*\b(TL-INV-\d{3})\b", spec, flags=re.M)
    if len(heading_ids) != len(set(heading_ids)):
        errors.append("duplicate invariant IDs in specification headings")

    missing_manifest = sorted(set(heading_ids) - set(ids))
    missing_spec = sorted(set(ids) - set(heading_ids))
    if missing_manifest:
        errors.append("spec invariant IDs missing from manifest: " + ", ".join(missing_manifest))
    if missing_spec:
        errors.append("manifest invariant IDs missing from spec headings: " + ", ".join(missing_spec))

    adr_files = {p.name.split('-', 2)[0] + '-' + p.name.split('-', 2)[1] for p in adr_dir.glob('adr-*.md')}
    adr_ids = {x.upper() for x in adr_files}
    for inv in invariants:
        for adr in inv.get("adrs", []):
            if adr not in adr_ids:
                errors.append(f"{inv['id']} references missing {adr}")

    status_vocabulary = data.get("status_vocabulary", {})
    allowed_formalization = set(status_vocabulary["formalization"])
    allowed_verification = set(status_vocabulary["verification"])
    allowed_mapping = set(status_vocabulary["mapping"])
    allowed_model_status = set(status_vocabulary.get("formal_model", {}))
    allowed_profile_status = set(status_vocabulary.get("integrated_profile", {}))

    model_policy = data["policy"]["formal_model"]
    model_status = model_policy.get("status")
    model_path = root / model_policy["path"]
    if model_status not in allowed_model_status:
        errors.append(
            f"policy.formal_model.status {model_status!r} is not in status_vocabulary.formal_model"
        )
    else:
        if model_status == "not-yet-introduced" and model_path.exists():
            errors.append(
                f"formal model exists while policy status is not-yet-introduced: {model_policy['path']}"
            )
        if model_status == "introduced" and not model_path.exists():
            errors.append(
                f"formal model status is introduced but path is missing: {model_policy['path']}"
            )

    model_text = model_path.read_text() if model_path.exists() else ""

    # Simple identifier discovery is intentionally conservative. It is a traceability
    # consistency check, not a TLA+ parser or semantic proof.
    variable_names = set()
    if model_text:
        for match in re.finditer(r"(?m)^\s*VARIABLES?\s+([^\n]+)", model_text):
            variable_names.update(x.strip() for x in match.group(1).split(',') if x.strip())
        operator_names = set(re.findall(r"(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^\n]*\))?\s*==", model_text))
    else:
        operator_names = set()

    for inv in invariants:
        iid = inv["id"]
        if inv.get("formalization") not in allowed_formalization:
            errors.append(f"{iid} has invalid formalization status {inv.get('formalization')}")
        if inv.get("verification") not in allowed_verification:
            errors.append(f"{iid} has invalid verification status {inv.get('verification')}")
        tla = inv.get("tla")
        if not isinstance(tla, dict):
            errors.append(f"{iid} is missing tla mapping object")
            continue
        if tla.get("mapping_status") not in allowed_mapping:
            errors.append(f"{iid} has invalid TLA+ mapping status {tla.get('mapping_status')}")

        if inv.get("formalization") == "not-applicable":
            if tla.get("mapping_status") != "not-applicable":
                errors.append(f"{iid} is not-applicable but TLA+ mapping status differs")
            continue

        # Once a mapping is executable, the referenced identifiers must actually exist.
        if tla.get("mapping_status") == "mapped" or inv.get("verification") in {"modeled", "checked"}:
            if not model_path.exists():
                errors.append(f"{iid} is mapped/modeled but formal model is missing: {model_policy['path']}")
                continue
            for prop in tla.get("properties", []):
                name = prop["name"] if isinstance(prop, dict) else prop
                if name not in operator_names:
                    errors.append(f"{iid} references missing TLA+ property/operator {name}")
            for action in tla.get("actions", []):
                if action not in operator_names:
                    errors.append(f"{iid} references missing TLA+ action/operator {action}")
            for var in tla.get("state_variables", []):
                if var not in variable_names:
                    errors.append(f"{iid} references missing TLA+ state variable {var}")
            for cfg in tla.get("focused_configs", []) + tla.get("integrated_configs", []):
                if not (root / cfg).exists():
                    errors.append(f"{iid} references missing TLC config {cfg}")

    # Integrated profile lifecycle is declared machine-readably and checked bidirectionally.
    for profile in data["policy"].get("integrated_profiles", []):
        profile_status = profile.get("status")
        profile_path = root / profile["path"]
        if profile_status not in allowed_profile_status:
            errors.append(
                f"integrated profile {profile['name']} has unknown status {profile_status!r}"
            )
            continue
        if profile_status == "planned" and profile_path.exists():
            errors.append(
                f"integrated profile {profile['name']} exists while status is planned"
            )
        if profile_status == "introduced" and not profile_path.exists():
            errors.append(
                f"integrated profile {profile['name']} is introduced but path is missing"
            )

    # The run-evidence schema itself is already a real artifact and must remain parseable JSON.
    result_policy = data["policy"]["result_artifacts"]
    result_schema_path = root / result_policy["schema"]
    if not result_schema_path.exists():
        errors.append(f"TLC result schema missing: {result_policy['schema']}")
    else:
        try:
            json.loads(result_schema_path.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"invalid JSON in TLC result schema: {e}")

    # A checked claim requires at least one passing run-evidence record mentioning that invariant.
    results_dir = root / result_policy["directory"]
    run_records = []
    if results_dir.exists():
        for p in results_dir.rglob("*.yaml"):
            try:
                record = yaml.safe_load(p.read_text()) or {}
                run_records.append((p, record))
            except Exception as e:
                errors.append(f"cannot parse TLC run evidence {p.relative_to(root)}: {e}")
        for p in results_dir.rglob("*.json"):
            try:
                record = json.loads(p.read_text())
                run_records.append((p, record))
            except Exception as e:
                errors.append(f"cannot parse TLC run evidence {p.relative_to(root)}: {e}")

    required_run_fields = set(result_policy.get("required_identity", [])) | set(result_policy.get("required_verification_evidence", []))
    for path, record in run_records:
        missing = sorted(required_run_fields - set(record))
        if missing:
            errors.append(f"TLC run evidence {path.relative_to(root)} missing required fields: {', '.join(missing)}")
        unknown_ids = sorted(set(record.get("invariant_ids", [])) - set(ids))
        if unknown_ids:
            errors.append(f"TLC run evidence {path.relative_to(root)} references unknown invariant IDs: {', '.join(unknown_ids)}")
        if record.get("tool") not in {None, "TLC"}:
            errors.append(f"TLC run evidence {path.relative_to(root)} has unexpected tool {record.get('tool')}")

    for inv in invariants:
        if inv.get("verification") == "checked":
            evidence = [(p, r) for p, r in run_records if r.get("outcome") == "passed" and inv["id"] in r.get("invariant_ids", [])]
            if not evidence:
                errors.append(f"{inv['id']} is marked checked but has no passing TLC run evidence")
                continue
            # Every config explicitly declared as required coverage for this invariant must have passing evidence.
            tla = inv.get("tla", {})
            required_cfgs = set(tla.get("focused_configs", [])) | set(tla.get("integrated_configs", []))
            evidenced_cfgs = {r.get("model_config") for _, r in evidence}
            missing_cfgs = sorted(required_cfgs - evidenced_cfgs)
            if missing_cfgs:
                errors.append(f"{inv['id']} is marked checked but lacks passing evidence for configs: {', '.join(missing_cfgs)}")

    if check_generated:
        # Diagnose the generated projection without mutating repository state.
        renderer = root / "scripts" / "render-formal-mapping.py"
        result = subprocess.run(
            [sys.executable, str(renderer), "--stdout"],
            cwd=root,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            errors.append(
                "generated formal invariant mapping could not be rendered"
                + (f": {detail}" if detail else f" (exit {result.returncode})")
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

    return errors, len(ids)


def main() -> int:
    errors, invariant_count = collect_errors(ROOT)
    if errors:
        print("formal traceability check: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"formal traceability check: OK ({invariant_count} invariants)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
