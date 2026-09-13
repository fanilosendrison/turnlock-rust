# ADR-003: Make product intent and derived invariants govern implementation

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 003
- **Governs:** interpretation of subsequent TURNLOCK architecture decisions

## Context

During specification, the explicit working method was established: start from the **product intent**, derive invariants as far as possible, and avoid prematurely fixing implementation mechanisms.

TURNLOCK is particularly vulnerable to mechanism-first design because existing harnesses expose different APIs. Starting from `session_id`, daemon, IPC, subprocess, RPC, or adapter details could produce a locally convenient design that fails the intended control semantics.

## Decision

TURNLOCK architecture is specified in this order:

```text
product intent
    ↓
user-visible truths
    ↓
system invariants
    ↓
constraints / authority boundaries
    ↓
implementation mechanisms
```

Product intent and accepted invariants are normative. Concrete mechanisms are subordinate unless a later ADR explicitly promotes a mechanism to an invariant because the product cannot otherwise be satisfied.

A future implementation choice MUST NOT silently weaken a higher-level invariant merely because a harness makes another mechanism easier.

If a proposed mechanism cannot satisfy the product contract on a particular harness, the system must describe that as a capability/conformance limitation or explicitly amend the product contract through a new ADR.

## Rationale

The product is defined by control semantics, not by today's APIs of Claude Code, Pi, Codex, or any single runtime. Mechanism-neutral invariants preserve the ability to find different implementations that satisfy the same product promise.

This also prevents accidental over-specification such as requiring the same OS process when the actual product requirement is continuity of the same agentic lineage.

## Consequences

- Terms such as daemon, IPC, session identifier, process injection, adapter protocol, and storage engine remain open until forced by lower-level analysis.
- ADRs should state user-visible or semantic commitments before choosing a mechanism.
- Harness-specific limitations cannot redefine TURNLOCK semantics silently.
- The consolidated spec is the primary expression of the current product contract; ADRs record why important clauses exist.

## Alternatives considered

- **Start by designing a portable adapter API:** rejected as premature because the required semantics had not yet been fully derived.
- **Choose Pi's extension model as the architecture:** rejected as a product definition; Pi may be an implementation path, not the invariant.
- **Require literal same-process reinjection:** rejected at this stage because continuity, not process identity, is the product property.
