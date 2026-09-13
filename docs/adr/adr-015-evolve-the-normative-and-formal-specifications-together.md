---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Evolve the normative and formal specifications together"
id: "ADR-015"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "c321aeb4bb3a796897f37eaf3a5e729a3556395eb926cd234325f4fbde031b0e"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-003"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "formal-specification workflow, invariant traceability, TLC model-checking organization"
---

# ADR-015: Evolve the normative and formal specifications together

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 15
- **Governs:** formal-specification workflow, invariant traceability, TLC model-checking organization
- **Clarifies:** ADR-003

## Context

TURNLOCK is being specified from product intent toward invariants before implementation mechanisms are fixed. Its core semantics already contain control ownership, reversible handoff, nested invocation, immediate-caller return, concurrency, fan-out/fan-in, multiple cognitive execution forms, and workflow lifecycle rules.

These are exactly the kinds of state-transition and concurrency properties for which prose alone can hide ambiguity. Waiting until the prose specification is considered "finished" before building a formal model would postpone useful counterexamples and allow product decisions to accumulate without simultaneous state-machine scrutiny.

At the same time, the formal model must not become a line-by-line translation of the prose or encode implementation choices such as Rust, TypeScript, Pi APIs, process boundaries, persistence engines, or transport details that the product intent has not forced.

TLC exploration also creates a practical tension. Focused configurations are useful for fast feedback on a mechanism such as nested return or parallel join, but TURNLOCK's most important failures may arise only from interactions among individually-correct mechanisms. Focused models therefore cannot replace integrated exploration.

Finally, as the specification grows, prose invariants, ADRs, TLA+ properties, TLC configurations, and later implementation tests need stable, machine-checkable traceability.

## Decision

TURNLOCK SHALL evolve its normative prose specification and its formal state-machine model in parallel for decisions that materially affect state, control ownership, lifecycle, invocation/return, nesting, concurrency, synchronization, failure, cancellation, or related temporal behavior.

The prose specification remains the normative statement of product meaning. The TLA+ model is an abstract executable model used to test whether relevant state and temporal implications can coexist and to discover counterexamples. The formal model MUST remain implementation-independent and harness-agnostic unless a deliberately separate adapter-level model is introduced later.

Every derived invariant in the normative specification SHALL have a stable identifier. Section numbers and human-readable titles MAY change; invariant identifiers MUST remain stable once published except through an explicit supersession/migration decision.

TURNLOCK SHALL maintain a machine-readable verification manifest as the source of truth for formal traceability. The manifest SHALL be able to record, per invariant:

- its stable invariant ID and title;
- the ADRs that govern or motivate it;
- whether formalization is applicable;
- the corresponding TLA+ module and property names when defined;
- the TLA+ state variables and actions/transitions on which the formalization depends, once those executable identifiers exist;
- focused and integrated TLC model configurations that exercise it;
- verification status;
- later, implementation tests or conformance checks where useful.

The traceability graph SHALL be mechanically invertible. Given a TLA+ property, state variable, or action/transition recorded in the manifest, project tooling SHOULD be able to identify the product invariants that depend on it. This reverse mapping is intended to support impact analysis when the formal machine changes.

A generated human-readable invariant mapping SHALL be derived from that manifest rather than maintained as an independent manually-edited truth.

The manifest describes **verification intent and traceability**, not proof that TLC has actually run. Successful TLC executions SHALL be recorded separately as machine-readable run-evidence artifacts. Such evidence MUST identify the repository revision, TLC/model configuration, TLA+ module, TLC version, checked properties, mapped invariant IDs, explicit finite bounds, and outcome. A `checked` claim MUST be backed by matching successful run evidence; it MUST NOT be inferred from the existence of a manifest mapping alone.

Once an invariant is marked as mapped/modeled rather than merely planned, automated consistency checks SHOULD verify that referenced TLA+ modules, properties, state variables, actions/transitions, and TLC configurations actually exist. These checks establish referential integrity only. They do not prove that the formal formula faithfully captures the prose invariant; semantic correspondence remains a formal-review obligation.

TURNLOCK SHALL maintain one integrated formal model of the current core semantics. Focused TLC configurations MAY restrict constants, bounds, behaviors, or checked properties for faster diagnosis and iteration, but they MUST be restrictions or views of the same semantic model rather than divergent reimplementations of TURNLOCK semantics.

There MUST remain at least one integrated TLC configuration capable of exercising all currently-formalized core execution forms together within finite model-checking bounds. The project SHOULD maintain multiple integrated exploration budgets, for example:

```text
integrated smoke
→ all formalized core primitives, small bounds, fast feedback

integrated standard
→ all formalized core primitives, larger ordinary CI bounds

integrated stress
→ larger/expensive bounds for deliberate deep exploration
```

Focused exploration does not satisfy the integrated-verification obligation by itself.

For a semantic change that affects the formal state machine, the normal verification path SHOULD run:

```text
relevant focused checks
+ integrated smoke
```

with broader integrated configurations run according to the project's CI/release policy. The exact automation cadence is not fixed by this ADR.

The formal model MUST distinguish safety from liveness where the product meaning requires both. For example, "never return to the wrong caller" and "eventually resume the correct caller under the required fairness assumptions" are different properties and MUST NOT be conflated.

The project MUST NOT claim an invariant as formally verified merely because it appears in the manifest. Statuses such as `planned`, `modeled`, `checked`, `not-applicable`, and `blocked` (or equivalent explicit states) SHALL distinguish traceability from actual TLC execution.

## Rationale

Parallel formalization turns TLA+/TLC into a specification-discovery tool rather than a final audit step. Counterexamples can reveal missing product rules before implementation architecture hardens around them.

Stable IDs allow prose, ADRs, formal properties, model configurations, and implementation tests to refer to the same semantic obligation even when documents are reorganized.

A machine-readable manifest makes traceability checkable. It can detect missing files, stale TLA+ property names, orphaned invariants, absent integrated coverage, and later missing implementation tests. It cannot prove that the TLA+ property faithfully captures the prose meaning; that semantic correspondence remains a review responsibility.

Focused configurations keep the development loop practical. Integrated configurations preserve the ability to detect emergent failures caused by composition across nesting, concurrency, joins, handoffs, raw LLM calls, independent agents, and workflow returns.

## Consequences

The repository gains dedicated formal-specification and formal-documentation areas. A target organization is:

```text
turnlock/
├── docs/
│   ├── specification/
│   ├── adr/
│   └── formal/
├── formal/
│   ├── verification.yaml
│   ├── tlc-result.schema.json
│   ├── results/                     # actual TLC run evidence, when runs exist
│   ├── Turnlock.tla                 # when the executable model is introduced
│   └── models/
│       ├── focused/
│       └── integrated/
└── scripts/
    ├── render-formal-mapping.py
    └── check-formal-traceability.py
```

The exact implementation-language directories remain intentionally undecided.

Not every product invariant must become a TLA+ property. Developer-experience or semantic-quality requirements may legitimately be marked `not-applicable` to TLA+ with a reason. State, ordering, ownership, lifecycle, nesting, concurrency, synchronization, and temporal progress rules are strong formalization candidates.

Finite TLC exploration MUST be described honestly. "Integrated" means all relevant formalized mechanisms are connected in the same abstract model; it does not imply exploration of an unbounded real-world state space. The `.cfg` files define finite bounds under which TLC can exhaustively explore reachable states.

## Alternatives considered

### Wait until the prose specification is complete, then translate it to TLA+

Rejected. This loses the main value of formalization as an early ambiguity and counterexample discovery mechanism.

### Maintain only focused formal models

Rejected. Individually-correct mechanisms can fail in composition, and independent mini-models can drift semantically.

### Run only one maximal integrated configuration

Rejected. State-space growth would make ordinary iteration unnecessarily slow. Focused and budgeted integrated configurations serve different purposes.

### Keep the invariant mapping only as Markdown

Rejected. Human-readable documentation remains valuable, but machine-readable traceability enables automated consistency and coverage checks.

### Make TLA+ the sole normative specification

Rejected. TURNLOCK has product, DX, harness, and semantic-quality requirements that are not naturally or completely expressed as a state-transition model. TLA+ complements rather than replaces the normative prose specification.

## Verification obligation

The repository structure and CI policy must make it possible to answer, for every stable invariant ID:

1. Where is the invariant stated normatively?
2. Which ADRs govern it?
3. Is TLA+ formalization applicable?
4. If applicable, which TLA+ module and properties represent it?
5. Which TLA+ state variables and actions/transitions does that formalization depend on?
6. Which focused configurations exercise it?
7. Which integrated configurations exercise it?
8. Has it actually been checked, or is it merely planned/modeled?
9. If checked, which machine-readable TLC run evidence supports that claim for the relevant revision and finite bounds?
10. Later, which implementation tests or conformance checks cover it?

The inverse questions must also be answerable mechanically once executable mappings exist: for a changed TLA+ property, state variable, or action/transition, which `TL-INV-*` obligations may be affected?

For every semantic change affecting the formal state machine, review must also ask whether the integrated model still composes the changed behavior with all other currently-formalized core behaviors.
