# TURNLOCK — specification package

This package contains the current TURNLOCK product specification and the
architectural decisions reconstructed chronologically from the product
discussion.

## Contents

- `AGENTS.md` — repository directives and authority boundaries for coding agents.
- `docs/repository-governance/turnlock-rust-engineering.md` — GitHub Engineering
  Project routing and workflow policy.
- `docs/specification/turnlock-spec.md` — consolidated product intent, product
  promise, mental model, invariants, boundaries, and architectural implications.
- `docs/adr/README.md` — chronological ADR index and conversation-to-decision
  trace.
- `docs/adr/adr-001...adr-015` — accepted decisions derived from the discussion.
- `formal/verification.yaml` — machine-readable forward/reverse traceability and
  intended verification manifest.
- `docs/formal/invariant-mapping.md` — generated human-readable traceability
  view.
- `formal/` — formal-model workspace, including planned focused and integrated
  TLC profiles plus the schema and location for actual TLC run evidence.
- `scripts/render-formal-mapping.py` — regenerates the human-readable mapping
  from the manifest.
- `scripts/check-formal-traceability.py` — validates invariant IDs, ADR
  references, manifest statuses, and generated mapping freshness.

The package intentionally stops before fixing implementation mechanisms that
have not yet been forced by the product invariants. Pi is the first reference
harness, while TURNLOCK workflow semantics remain harness-independent. Workflow
authoring is developer-native: developers and coding agents target the same
TURNLOCK primitives and artifact model.

The workflow model treats deterministic computation, bounded raw LLM inference,
bounded independent agents, and main-agent continuation as distinct composable
execution forms, with workflow-owned parallel fan-out/fan-in and a
minimum-sufficient-cognition principle.

ADR-014 makes the orchestration ownership boundary explicit: the workflow
program owns declared orchestration decisions and topology, while TURNLOCK is
the orchestration engine/runtime that executes, coordinates, and tracks them
without silently inventing global strategy.

ADR-015 makes formal verification a parallel specification activity rather than
a final audit. Every derived invariant has a stable `TL-INV-xxx` identity.
`formal/verification.yaml` records machine-readable forward/reverse traceability
from product invariant to TLA+ properties and, once modeled, state variables,
actions, and TLC configurations.

Actual TLC run evidence is deliberately separate under `formal/results/`, so
planned mappings cannot be mistaken for successful verification. Focused
exploration remains subordinate to integrated smoke, standard, and stress
exploration of the shared model.

## Formal verification organization

```text
docs/specification/turnlock-spec.md   normative meaning
docs/adr/                             decision history
formal/verification.yaml              desired forward/reverse traceability graph
docs/formal/invariant-mapping.md      generated human-readable mapping
formal/Turnlock.tla                    executable abstract model (next step)
formal/models/focused/                fast targeted exploration
formal/models/integrated/             smoke / standard / stress integrated exploration
formal/tlc-result.schema.json         schema for actual TLC run evidence
formal/results/                       actual run evidence, once TLC runs exist
```

The executable TLA+ model has not yet been introduced, so the package
makes no `checked` verification claim.
