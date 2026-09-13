#!/usr/bin/env python3
from pathlib import Path
import json
import re
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / "formal" / "verification.yaml"
spec_path = ROOT / "docs" / "specification" / "turnlock-spec.md"
adr_dir = ROOT / "docs" / "adr"
mapping_path = ROOT / "docs" / "formal" / "invariant-mapping.md"

data = yaml.safe_load(manifest_path.read_text())
errors = []

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

allowed_formalization = set(data["status_vocabulary"]["formalization"])
allowed_verification = set(data["status_vocabulary"]["verification"])
allowed_mapping = set(data["status_vocabulary"]["mapping"])

model_policy = data["policy"]["formal_model"]
model_path = ROOT / model_policy["path"]
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
            if not (ROOT / cfg).exists():
                errors.append(f"{iid} references missing TLC config {cfg}")

# Planned profiles may point at not-yet-created files. Once a profile is no longer planned, its path must exist.
for profile in data["policy"].get("integrated_profiles", []):
    if profile.get("status") != "planned" and not (ROOT / profile["path"]).exists():
        errors.append(f"integrated profile path missing: {profile['path']}")

# The run-evidence schema itself is already a real artifact and must remain parseable JSON.
result_policy = data["policy"]["result_artifacts"]
result_schema_path = ROOT / result_policy["schema"]
if not result_schema_path.exists():
    errors.append(f"TLC result schema missing: {result_policy['schema']}")
else:
    try:
        json.loads(result_schema_path.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"invalid JSON in TLC result schema: {e}")

# A checked claim requires at least one passing run-evidence record mentioning that invariant.
results_dir = ROOT / result_policy["directory"]
run_records = []
if results_dir.exists():
    for p in results_dir.rglob("*.yaml"):
        try:
            record = yaml.safe_load(p.read_text()) or {}
            run_records.append((p, record))
        except Exception as e:
            errors.append(f"cannot parse TLC run evidence {p.relative_to(ROOT)}: {e}")
    for p in results_dir.rglob("*.json"):
        try:
            record = json.loads(p.read_text())
            run_records.append((p, record))
        except Exception as e:
            errors.append(f"cannot parse TLC run evidence {p.relative_to(ROOT)}: {e}")

required_run_fields = set(result_policy.get("required_identity", [])) | set(result_policy.get("required_verification_evidence", []))
for path, record in run_records:
    missing = sorted(required_run_fields - set(record))
    if missing:
        errors.append(f"TLC run evidence {path.relative_to(ROOT)} missing required fields: {', '.join(missing)}")
    unknown_ids = sorted(set(record.get("invariant_ids", [])) - set(ids))
    if unknown_ids:
        errors.append(f"TLC run evidence {path.relative_to(ROOT)} references unknown invariant IDs: {', '.join(unknown_ids)}")
    if record.get("tool") not in {None, "TLC"}:
        errors.append(f"TLC run evidence {path.relative_to(ROOT)} has unexpected tool {record.get('tool')}")

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

# Check the generated human-readable view by regenerating and comparing bytes.
original = mapping_path.read_text() if mapping_path.exists() else None
subprocess.run([sys.executable, str(ROOT / "scripts" / "render-formal-mapping.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
regenerated = mapping_path.read_text()
if original is not None and original != regenerated:
    errors.append("docs/formal/invariant-mapping.md was stale (it has been regenerated)")

if errors:
    print("formal traceability check: FAILED")
    for e in errors:
        print(f"- {e}")
    sys.exit(1)

print(f"formal traceability check: OK ({len(ids)} invariants)")
