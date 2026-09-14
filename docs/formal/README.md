# TURNLOCK formal specification

This directory documents how the normative TURNLOCK specification is connected to formal verification artifacts. The governing decision is [ADR-015](../adr/adr-015-evolve-the-normative-and-formal-specifications-together.md).

## Artifact roles

```text
docs/specification/turnlock-spec.md
= normative product meaning

formal/verification.yaml
= machine-readable desired traceability and verification coverage

formal/Turnlock.tla
= executable abstract state-machine model (planned)

formal/models/focused/*.cfg
= targeted TLC exploration of the shared model

formal/models/integrated/*.cfg
= cross-feature TLC exploration of the shared model

formal/results/*
= machine-readable evidence of actual TLC runs

formal/tlc-result.schema.json
= schema for those run-evidence records

docs/formal/invariant-mapping.md
= generated human-readable forward + reverse traceability view
```

The TLA+ model complements the normative prose; it does not replace it.

## Full traceability

The intended chain is:

```text
product invariant ID
→ governing ADR(s)
→ TLA+ module/property
→ TLA+ state variables and actions/transitions
→ TLC focused/integrated configs
→ actual TLC run evidence for a concrete commit + finite bounds
→ later implementation/conformance tests
```

The mapping is also intended to work in reverse so a change to a TLA+ property, state variable, or action can identify potentially affected product invariants.

Machine-readable referential integrity is not semantic proof: tooling can verify that `TL-INV-018` points to an existing operator, but human/formal review must still establish that the operator faithfully represents the prose invariant.

## Current status

Stable invariant IDs and the schema-v2 verification manifest exist. Planned TLA+ property names are recorded where useful, but the executable `Turnlock.tla` model and TLC configurations have **not yet been introduced**. State-variable/action mappings therefore remain intentionally empty and no invariant is `checked`.

`formal/results/` contains no passing run evidence because TLC has not yet run against an executable TURNLOCK model. This separation is intentional.

## Focused and integrated exploration

Focused configurations are intended for fast diagnosis and iteration. Integrated configurations are required to preserve cross-feature verification. Focused checks never substitute for an integrated model.

The intended integrated profiles are:

```text
integrated-smoke
→ all currently formalized core forms, small bounds

integrated-standard
→ all currently formalized core forms, ordinary CI bounds

integrated-stress
→ deliberately larger and more expensive exploration
```

A semantic state-machine change should normally run the relevant focused configurations plus `integrated-smoke`.

## Finite bounds and temporal properties

TLC cannot exhaust an unbounded real-world TURNLOCK system. An integrated
configuration means all currently formalized mechanisms are connected in one
abstract model and explored exhaustively within explicit finite bounds. A finite
state-space domain or bound is a modeling choice; it is not a TURNLOCK runtime
limit on turns, tokens, tools, cost, time, retries, or context, and it does not
establish eventual completion. Safety and liveness are separate obligations
where both matter.

## Generated mapping

`invariant-mapping.md` is generated from `formal/verification.yaml`:

```bash
python scripts/render-formal-mapping.py
```

`python scripts/check-formal-traceability.py` validates the current cross-artifact consistency rules and becomes stricter automatically once mappings move from planned to modeled/checked.
