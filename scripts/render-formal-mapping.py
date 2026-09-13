#!/usr/bin/env python3
from collections import defaultdict
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / "formal" / "verification.yaml"
out_path = ROOT / "docs" / "formal" / "invariant-mapping.md"

data = yaml.safe_load(manifest_path.read_text())
rows = []
reverse_props = defaultdict(list)
reverse_actions = defaultdict(list)
reverse_vars = defaultdict(list)

for inv in data["invariants"]:
    tla = inv.get("tla", {})
    props = tla.get("properties", []) or []
    prop_names = [p["name"] if isinstance(p, dict) else p for p in props]
    vars_ = tla.get("state_variables", []) or []
    actions = tla.get("actions", []) or []
    for name in prop_names:
        reverse_props[name].append(inv["id"])
    for name in vars_:
        reverse_vars[name].append(inv["id"])
    for name in actions:
        reverse_actions[name].append(inv["id"])

    props_text = ", ".join(f"`{p}`" for p in prop_names) if prop_names else "—"
    vars_text = ", ".join(f"`{v}`" for v in vars_) if vars_ else "—"
    actions_text = ", ".join(f"`{a}`" for a in actions) if actions else "—"
    adrs = ", ".join(inv.get("adrs", [])) or "—"
    rows.append(
        f"| `{inv['id']}` | {inv['title']} | {inv.get('kind','—')} | "
        f"{inv.get('formalization','—')} | {tla.get('mapping_status','—')} | {props_text} | "
        f"{vars_text} | {actions_text} | {inv.get('verification','—')} | {adrs} |"
    )

formal_model = data["policy"]["formal_model"]
content = f'''# TURNLOCK invariant ↔ formal verification mapping

> **Generated file.** Source of truth: [`../../formal/verification.yaml`](../../formal/verification.yaml).  
> Regenerate with `python scripts/render-formal-mapping.py`.

The normative meaning of every invariant lives in [`../specification/turnlock-spec.md`](../specification/turnlock-spec.md). This file is a generated traceability view, not a substitute for the prose or the TLA+ formulas themselves.

Current executable formal-model status: **{formal_model['status']}**. No `checked` claim should be inferred from the existence of a row.

## Forward traceability

| Invariant | Title | Kind | Formalization | TLA+ mapping | Properties | State variables | Actions / transitions | Verification | ADRs |
|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

## Reverse traceability

The same manifest is mechanically invertible. Once state/action mappings are populated, this section answers questions such as “which product invariants may be affected if `CompleteWorkflow` changes?”.

### TLA+ properties → invariant IDs
'''
if reverse_props:
    for name in sorted(reverse_props):
        content += f"- `{name}` → {', '.join(f'`{i}`' for i in reverse_props[name])}\n"
else:
    content += "- No TLA+ properties mapped yet.\n"

content += "\n### TLA+ state variables → invariant IDs\n"
if reverse_vars:
    for name in sorted(reverse_vars):
        content += f"- `{name}` → {', '.join(f'`{i}`' for i in reverse_vars[name])}\n"
else:
    content += "- No executable state-variable mappings yet.\n"

content += "\n### TLA+ actions / transitions → invariant IDs\n"
if reverse_actions:
    for name in sorted(reverse_actions):
        content += f"- `{name}` → {', '.join(f'`{i}`' for i in reverse_actions[name])}\n"
else:
    content += "- No executable action/transition mappings yet.\n"

content += '''

## Integrated verification policy

Focused configurations are not substitutes for integrated exploration. The planned integrated profiles are:

'''
for profile in data["policy"]["integrated_profiles"]:
    content += f"- **{profile['name']}** — `{profile['path']}` — {profile['status']}: {profile['intent']}\n"

results = data["policy"]["result_artifacts"]
content += f'''

## Verification evidence

`verification.yaml` describes **intended traceability and coverage**. Successful TLC execution evidence is a separate artifact class under `{results['directory']}` and is governed by `{results['schema']}`.

An invariant must not be considered `checked` merely because it maps to a TLA+ property or TLC config. A `checked` claim requires matching run evidence for the relevant repository revision and finite bounds.

## Notes on applicability

`not-applicable` does not mean unimportant. It means the invariant is not expected to be proven by the core TLA+ state-machine model. Examples include developer-experience requirements, reference-harness policy, or semantic-quality judgments such as whether a chosen cognition form is truly the minimum sufficient one.

`partial` means TLA+ can check a meaningful structural subset while some real-world semantic obligation remains an implementation/harness/review concern.

Machine-readable linkage validates traceability consistency. It does **not** prove that a TLA+ formula faithfully captures the prose meaning; that semantic correspondence remains a formal-review obligation.
'''
out_path.write_text(content)
print(out_path)
