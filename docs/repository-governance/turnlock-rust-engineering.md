---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust Engineering GitHub Project profile"
---

# Turnlock-Rust Engineering GitHub Project profile

Apply the shared GitHub Engineering Projects operational protocol before using
this profile. This file contains only Turnlock-Rust-specific routing, authority,
classification, and workflow policy.

## Fixed routing

- GitHub owner: `fanilosendrison`
- Default repository: `fanilosendrison/turnlock-rust`
- Repository visibility: public
- Project title: `Turnlock-Rust Engineering`
- Project number: `5`
- Project URL: <https://github.com/users/fanilosendrison/projects/5>
- Project type: private user-owned GitHub Project V2

Resolve an unqualified `Issue #N` as
`fanilosendrison/turnlock-rust#N`. Follow an explicit
repository-qualified reference or Issue URL instead when the user provides one.

## Turnlock-Rust authority boundary

Treat Turnlock-Rust Engineering as the authority for durable work existence,
classification, priority, and workflow state. Never treat it as authority for
TURNLOCK product semantics or formal-verification claims.

Apply these repository authority boundaries:

1. `docs/specification/turnlock-spec.md` defines normative product meaning and
   stable invariant identities.
2. Accepted ADRs under `docs/adr/` record decision history and explicit later
   amendments.
3. `formal/verification.yaml` defines intended formal traceability and coverage;
   it is not evidence of successful verification.
4. The executable model and configurations under `formal/`, once introduced,
   define the checked abstract formulas for their declared scope without
   replacing normative prose.
5. Records under `formal/results/` are authoritative only for the concrete,
   bounded verification runs they identify.
6. Generated mappings and README files are explanatory projections, not
   independent semantic or verification authority.

Report every inconsistency between these sources. Resolve a semantic conflict
through an explicit new ADR and synchronized normative and formal artifacts
instead of treating an Issue or Project field as the decision.

The repository currently precedes both an executable TLA+ model and a Rust
implementation. The repository name does not authorize a crate structure,
runtime mechanism, persistence model, public API, or release process.

## Workflow-status mapping

Map the shared protocol's workflow roles to these exact `Status` values:

- unready backlog: `Backlog`
- ready for independent pickup: `Ready`
- active execution: `In Progress`
- reviewable result: `Review`
- completed work: `Done`

`Ready` means that the work can be picked up without reopening unresolved
product semantics or dependencies. Use the Project's `Agent Queue` as the normal
autonomous pickup surface. A direct user request may select another item, but it
does not ratify proposed semantics or remove unresolved prerequisites.

## Classification fields

### Phase

Use `Phase` for the lifecycle domain that owns the immediate deliverable:

- `Specification`
- `Formal Verification`
- `Implementation`

Classify executable TLA+ models, TLC configuration, traceability, and bounded run
evidence as `Formal Verification`. Classify Rust implementation and conformance
work as `Implementation` only after the required architecture and ecosystem
boundaries have been accepted.

Create linked follow-up Issues when downstream phases require independent
acceptance, prerequisites, or scheduling.

### Kind

Use `Kind` for the item's relationship to the engineering plan:

- `Agent Task`: independently scoped work intended for direct execution.
- `Follow-up`: downstream work created by another task, finding, or accepted
  decision.
- `Finding`: a validated concern that still requires adjudication, design, or
  correction.

Do not retain an unvalidated observation as a `Finding` item.

### Priority

Use `Priority` according to this Project contract:

- `P0`: blocks current progress or protects a critical correctness, authority,
  traceability, or verification invariant.
- `P1`: should be completed in the current phase.
- `P2`: important but non-blocking work.
- `P3`: useful retained work that can wait.

Priority controls scheduling only. It never overrides the normative
specification, accepted decisions, prerequisites, or evidence requirements.

## Project views

The intended views are:

- `Now`: board filtered to `Phase: Specification`.
- `Agent Queue`: table filtered to Issues in `Ready` or `In Progress`.
- `Specification`: table filtered to `Phase: Specification`.
- `Formal Verification`: table filtered to `Phase: Formal Verification`.
- `Implementation`: table filtered to `Phase: Implementation`.

Treat any difference between these declarations and live GitHub configuration as
an inconsistency to report before relying on the affected routing.

## Issue requirements

A normal Turnlock-Rust Issue must state:

- the observed problem or required outcome;
- the controlling specification sections, invariants, and ADRs;
- the relevant phase and unresolved prerequisites;
- constraints and authority boundaries;
- mechanically checkable acceptance criteria;
- required generation, traceability, formal, conformance, or implementation
  validation.

An Issue that may change product semantics must distinguish the observed problem
from a proposed resolution and identify every normative, decision, traceability,
and generated artifact that requires synchronization.

When useful, add a collapsed `Coding agent execution brief` with detailed
execution guidance. Keep the Issue outcome-oriented and do not duplicate the
only authoritative technical contract in GitHub prose.

Populate `Status`, `Phase`, `Kind`, and `Priority` for every Project Issue. Use
native GitHub parent, sub-issue, dependency, and Pull Request relationships when
available. Do not encode the only dependency record in Project ordering.

## Findings and durable work

Create a `fanilosendrison/turnlock-rust` Issue for every validated finding or
other work unit that must be deferred, handed off, scheduled, or tracked
independently. Add it to Turnlock-Rust Engineering and populate all required
fields.

Default retained findings to `Backlog`. Use `Ready` only when authority,
dependencies, scope, acceptance criteria, and validation make the work
independently executable.

Do not create Issues for transient exploratory reasoning that does not need to
persist beyond the current work.

## Repository validation

Use the current validation sequence in `AGENTS.md`. Project completion, an Issue
closure, or a passing review cannot replace generated traceability freshness,
the repository's formal checks, or any future model and implementation
validation required by accepted repository changes.
