# TURNLOCK formal specification

This directory documents how the normative TURNLOCK specification is connected to formal verification artifacts. The governing decision is [ADR-015](../adr/adr-015-evolve-the-normative-and-formal-specifications-together.md).

## Artifact roles

```text
docs/specification/turnlock-spec.md
= normative product meaning

formal/verification.yaml
= machine-readable desired traceability and verification coverage

formal/Turnlock.tla
= executable abstract state-machine model at the manifest-governed path

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

## Reading current status

Current formal-model and intended verification state is owned by `formal/verification.yaml`. Actual bounded verification evidence is owned by the records under `formal/results/`. Cross-artifact consistency, including lifecycle state against the filesystem, is enforced by `scripts/check-formal-traceability.py`.

This README does not mirror those mutable values.

## Focused and integrated exploration

Focused configurations are intended for fast diagnosis and iteration. Integrated configurations are required to preserve cross-feature verification. Focused checks never substitute for an integrated model.

Integrated profile names, paths, lifecycle state, intents, and the default
semantic-change check set are owned by `formal/verification.yaml` and projected
mechanically in `docs/formal/invariant-mapping.md`.

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
