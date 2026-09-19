---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Assume native harness workflow convergence"
id: "ADR-038"
status: "accepted"
date: "2026-09-19"
decision_body_sha256: "33d599686ccd8db72f7b9cda0939173c7f3fcdefd6fcb5d40a67bad77f510351"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-010"
  amends: []
  supersedes: []
  confirms:
    - "ADR-030"
governs:
  - "Architectural treatment of increasing native workflow capabilities in coding-agent harnesses"
  - "TURNLOCK value independence from current harness capability gaps"
  - "Reuse of semantically compatible harness-native mechanisms as execution realizations"
  - "Perfect-harness stress test for TURNLOCK architecture and implementation proposals"
---

# ADR-038: Assume native harness workflow convergence

## Context

TURNLOCK is anchored inside an existing interactive coding-agent session.

Its original motivating mechanics include:

```text
workflow-owned orchestration
reversible and repeatable handoff to the existing main agent
workflow resumption
eventual return to the continuing interactive session
```

ADR-010 already makes TURNLOCK workflow semantics harness-independent and
positions Pi as the first reference integration rather than the semantic
definition of TURNLOCK concepts.

ADR-030 already establishes runtime composition of semantically preserving
external realizations, so a supported realization that is not fixed by
TURNLOCK semantics can be supplied or established without modifying or
recompiling Core.

Coding-agent harnesses can evolve independently and may acquire increasingly
capable native workflow facilities.

TURNLOCK must not rely for durable product value on those facilities remaining
absent or inferior.

This is a conservative architectural stress assumption, not a prediction about
a specific vendor or delivery date.

## Discovery classification

```text
decision-required, resolved
```

The accepted corpus already required harness independence. It did not uniquely
require TURNLOCK architecture to be designed as if native harness workflow
capabilities would converge toward the original TURNLOCK mechanism.

This decision affects architectural and integration/conformance reasoning. It
introduces no new normative workflow behavior.

## Decision

### Native-harness-convergence assumption

TURNLOCK SHALL be designed under a **native-harness-convergence assumption**.

### Mechanisms that may become available

For architectural stress testing, assume that a coding-agent harness may
eventually provide excellent native mechanisms for some or all of:

```text
workflow/state-machine execution
externally controlled control flow
suspension and resumption
continuation/re-entry of the existing main agent
durable execution state
rich execution tracing
workflow authoring facilities
built-in evaluation-adjacent facilities
```

This list describes mechanisms that may become available. It does not promote
them into TURNLOCK requirements.

### No durable value from current capability gaps

The absence, weakness, or inconvenience of one of those mechanisms in a
current harness MUST NOT by itself be treated as durable TURNLOCK product
value.

### Harness-native capabilities as realization assets

When a harness-native capability can faithfully realize accepted TURNLOCK
semantics, TURNLOCK architecture MUST permit that capability to be treated as a
candidate realization asset through the appropriate integration/conformance
boundary.

### No reimplementation solely for differentiation

TURNLOCK MUST NOT reimplement a harness-native mechanism solely to preserve
differentiation. A TURNLOCK-owned mechanism remains justified when required by:

```text
accepted TURNLOCK semantics
semantic preservation
portability of TURNLOCK meaning
conformance
evidence obligations
or because no adequate underlying realization exists
```

### No semantic authority from a harness-native mechanism

A harness-native workflow mechanism never becomes semantic authority merely
because TURNLOCK uses it. The dependency direction remains:

```text
TURNLOCK semantics
        ↓
required capabilities / conformance
        ↓
harness-native or other execution realization
```

### Perfect Harness Test

The architectural **Perfect Harness Test** is:

```text
Assume the underlying coding harness already provides
an excellent native implementation of the mechanism
being proposed.

What TURNLOCK-specific user value or responsibility remains?
```

The result is interpreted exactly as follows:

```text
if the answer is:
"none; the value existed only because the harness lacked the mechanism"

then:
the mechanism is not by itself a durable TURNLOCK-core reason for existence
and should remain an integration / realization / implementation concern
unless separate accepted authority requires otherwise
```

and:

```text
if TURNLOCK-specific value remains because of
semantic guarantees,
authority boundaries,
harness-independent meaning,
conformance,
portable workflow meaning across supported realizations,
execution characterization / evidence,
or other accepted TURNLOCK responsibilities,

then:
the proposal may still belong at the TURNLOCK layer
```

The examples in the second branch are illustrations of possible independent
responsibilities. They do not become new guarantees merely because they are
listed.

### Better harnesses are better substrates

Improving coding harnesses should generally make them **better TURNLOCK
substrates** when their native capabilities can preserve TURNLOCK semantics.

### Augmentation layer

TURNLOCK augments coding-agent harnesses rather than depending on replacing
them.

### No uniform-capability requirement

This decision does not require identical capabilities across harnesses and does
not require TURNLOCK to support every harness-native mechanism.

### Preserved decisions

ADR-010 remains in force: Pi remains the first reference integration unless
separately changed.

ADR-019 remains in force: this decision does not move evaluation or
optimization policy into TURNLOCK Core.

ADR-030 remains in force: native harness capabilities may participate as
runtime-composable realizations only under the semantic-preservation rules
already established there.

## Invariant consequence

No new invariant identity is introduced.

No existing `TL-INV-*` meaning is amended.

This decision is architectural guidance and integration/conformance policy
rather than a new universal workflow-semantic obligation.

## Formal-traceability consequence

`formal/verification.yaml` requires no change from this ADR.

No TLA+ property, state variable, action, fairness condition, model, or TLC
configuration is introduced.

The Perfect Harness Test is an architectural review test, not a model-checking
property.

## Consequences

- Native workflow improvements in Pi, Codex, Claude Code, or future harnesses
  can reduce adapter/runtime work without erasing TURNLOCK's semantic role.
- Implementation must not create artificial duplication simply to keep a
  mechanism TURNLOCK-owned.
- TURNLOCK architecture must be evaluated for value that survives mechanism
  commoditization.
- Harness-specific native facilities remain subordinate to TURNLOCK semantics.
- Better harnesses should normally improve TURNLOCK when they expose useful
  conformant capabilities.
- TURNLOCK's durable differentiation must come from responsibilities that
  remain meaningful above the underlying mechanism, not from temporary
  ecosystem gaps.

This ADR does not assert that any named current harness already satisfies a
particular future capability.

## Non-goals

This ADR does not:

- predict a six-month vendor roadmap;
- require native workflow support from any harness;
- guarantee cross-harness feature parity;
- guarantee that every TURNLOCK workflow can run on every harness;
- define a workflow DSL or syntax;
- define adapter APIs;
- define runtime implementation structure;
- add durability semantics;
- add tracing semantics;
- add evaluation or optimization semantics;
- add cross-run comparability guarantees;
- amend the existing main-agent, orchestration-ownership,
  stable-governing-definition, inspectability, or provenance semantics;
- make a harness's internal workflow model TURNLOCK semantics.

## References

- `AGENTS.md`
- `docs/vision/turnlock-vision.md`
- `docs/adr/adr-010-keep-workflow-semantics-harness-independent-and-use-pi-as-the-first-reference-integration.md`
- `docs/adr/adr-019-keep-evaluation-and-optimization-policy-outside-turnlock-core.md`
- `docs/adr/adr-030-make-turnlock-core-a-runtime-composable-execution-substrate.md`
