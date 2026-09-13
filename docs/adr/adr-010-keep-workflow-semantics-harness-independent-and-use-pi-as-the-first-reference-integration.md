---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Keep workflow semantics harness-independent and use Pi as the first reference integration"
id: "ADR-010"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "dc1ec02ee4a73fb1f2c111717962e992ccc9c9a5ec0b31976e965c068a05adb5"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-010: Keep workflow semantics harness-independent and use Pi as the first reference integration

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 010

## Context

TURNLOCK is intended to work across interactive coding-agent harnesses rather than become a feature whose semantics are defined by one vendor client. The motivating environments include Pi, Claude Code, Codex, and similar systems.

At the same time, attempting to implement several harnesses before the control model has been proven would slow the project and encourage design by least-common-denominator abstraction. The product discussion therefore chose to concentrate implementation first on **Pi**.

This creates a predictable architecture risk: because Pi is implemented first and exposes concrete APIs, events, extension mechanisms, session behavior, and skill-discovery conventions, those mechanics can accidentally leak upward and become the ontology of TURNLOCK itself.

The project needs to optimize deeply for Pi without confusing "first realization" with "semantic definition."

## Decision

TURNLOCK workflow semantics are **harness-independent**.

The normative dependency direction is:

```text
TURNLOCK product/workflow semantics
        ↓
harness integration contract
        ↓
concrete harness adapter
```

Pi is the **first reference harness** and the first concrete adapter to be implemented and optimized. Pi-specific mechanisms MAY be used fully inside that adapter to achieve the best possible TURNLOCK experience in Pi.

However, workflow authors MUST express TURNLOCK concepts through TURNLOCK primitives rather than Pi-internal control mechanics when those concepts can be stated independently of Pi.

Pi-specific APIs, events, frontmatter/skill loading behavior, session identifiers, extension hooks, or messaging primitives do not become normative TURNLOCK semantics merely because the first implementation uses them.

A later supported harness may use entirely different implementation mechanics while remaining conformant if it realizes the same abstract TURNLOCK control contract.

## Rationale

The product needs both focus and portability.

Pi-first implementation gives TURNLOCK one concrete environment in which to prove the difficult semantics end to end: natural session invocation, workflow-owned orchestration, mechanical execution, reversible main-agent handoff, nested workflows, immediate-caller return, and developer/agent authoring.

Harness independence prevents that focused first implementation from locking the workflow model to incidental Pi details.

This is intentionally not a least-common-denominator policy. If Pi supports a useful capability that another harness does not, TURNLOCK may model explicit harness capabilities or support levels later. What must remain stable is the meaning of the product primitives that a harness claims to support.

## Consequences

- Pi is the implementation and validation priority for the first working system.
- TURNLOCK may have a Pi adapter with substantial harness-specific logic.
- Public workflow artifacts should not contain Pi plumbing merely to express core TURNLOCK control semantics.
- The eventual second harness becomes an important abstraction test for detecting accidental Pi leakage.
- Harness capability differences may need to become explicit rather than being hidden behind falsely uniform behavior.
- The specification remains free to evolve if Pi exposes a genuine missing product concept, but such evolution must happen as a product/ADR decision rather than by silently promoting adapter mechanics into semantics.

## Alternatives considered

### Define TURNLOCK directly in terms of Pi APIs

Rejected. It would make Pi the product ontology and turn future harness support into emulation of Pi rather than realization of TURNLOCK semantics.

### Implement several harnesses before validating Pi

Rejected for the current phase. It would increase complexity before the core handoff/control model is proven and risk premature least-common-denominator abstractions.

### Refuse all Pi-specific implementation mechanisms in the name of portability

Rejected. Harness independence applies to product semantics, not to adapter internals. The Pi integration should use Pi well.

### Guarantee identical capability across every harness

Not adopted. Different harnesses may expose different powers. TURNLOCK requires stable semantics for supported capabilities, not fiction that every environment is equally capable.

## Verification obligation

Every Pi-specific concept introduced during implementation must be classifiable as either:

```text
(a) a realization of an existing TURNLOCK semantic concept
or
(b) an internal Pi-adapter implementation detail
```

If a concept cannot be classified this way and changes workflow-visible meaning, it requires an explicit TURNLOCK product decision before becoming part of the normative model.

Once a second harness is implemented, architecture review must use it as a portability test and identify any workflow-level concepts that accidentally require Pi internals.
