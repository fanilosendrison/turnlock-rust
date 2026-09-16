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

## Live work-state ownership

Live work state has exactly one canonical owner per fact. GitHub Issue state,
Turnlock-Rust Engineering fields, and native GitHub relationships own the
current work graph. Repository-governance prose, Issue bodies, and comments may
reference that state; they must not maintain a second copy of it.

| Information                                       | Canonical owner                        |
| ------------------------------------------------- | -------------------------------------- |
| Durable work item                                 | GitHub Issue                           |
| Open/closed Issue state                           | GitHub Issue state                     |
| Workflow state                                    | Project `Status`                       |
| Lifecycle classification                          | Project `Phase`                        |
| Work-item classification                          | Project `Kind`                         |
| Scheduling priority                               | Project `Priority`                     |
| Parent/sub-issue structure                        | Native GitHub Issue relationships      |
| Blocking/blocked-by structure                     | Native GitHub dependency relationships |
| Pull Request linkage                              | Native GitHub relationships            |
| Product semantics                                 | `docs/specification/turnlock-spec.md`  |
| Accepted decision history                         | Accepted ADRs                          |
| Intended formal traceability/coverage             | `formal/verification.yaml`             |
| Concrete bounded verification evidence            | `formal/results/`                      |
| Acceptance criteria for the work owned by Issue X | Issue X body                           |

Apply the governing principle for Issue bodies:

```text
Reference, do not mirror.
```

### Do not duplicate live work state

An Issue body must not present as current truth:

- another Issue's open, closed, completion, or reopening state;
- `Status`, `Phase`, `Kind`, or `Priority` values;
- parent/sub-issue membership;
- blocked-by or blocking state;
- Pull Request relationship state.

The GitHub object or native relationship that owns the fact remains the single
live authority. An Issue may reference another work item and explain why its
outcome matters as a semantic input or sequencing constraint.

### Keep acceptance checklists local

Every acceptance checkbox in Issue X must describe an outcome that can be
satisfied by executing Issue X. Do not write criteria whose predicate is
another Issue's completion, resolution, closure, or current relationship.

A local criterion may require Issue X's own result to consume, exclude, or
remain compatible with the then-current authoritative outcome of related work.

### Let native relationships own the work graph

Use native parent, sub-issue, blocked-by, blocking, and Pull Request
relationships for current work relationships. Issue prose may state the stable
semantic reason an input or sequencing constraint matters, but it must not
maintain a second copy of the current relationship state.

### Let Project fields own live Project classification

`Status`, `Phase`, `Kind`, and `Priority` belong exclusively to Turnlock-Rust
Engineering as live classification state. Do not reproduce them as a Markdown
block inside an Issue body.

A required classification rationale records the reasoning without copying the
current field values. A durable exception explanation is historical rationale,
not another live Project record.

### Let accepted authority own accepted outcomes

When work produces an accepted ADR, normative specification change, formal
contract, or other authoritative artifact, other work items must reference that
artifact for the resulting technical meaning.

Do not use `Issue #N is resolved` as technical authority for an accepted
product or formal conclusion. A closed Issue remains available as historical
provenance.

### Bound historical snapshots explicitly

A historical observation is legitimate when provenance matters, but it must be
bounded by a date, repository revision, or equivalent immutable context and
must be identified as a snapshot rather than current work state.

Revision-scoped evidence sections are not violations merely because later
repository state differs.

### Do not maintain manual work-status dashboards

Do not add tables or dashboard sections whose rows track the current state of
multiple Issues. GitHub Issues, Project fields, and native relationships are
the live work graph.

A future projection that is genuinely required must be separately justified,
mechanically generated from canonical live sources, and clearly marked
non-authoritative. Never synchronize it by hand.

### Treat closed Issues as historical records

Do not rewrite closed Issues solely to conform to this presentation rule. Apply
the rule prospectively and normalize the currently active Issue corpus. Change
a closed Issue only for an independently justified reason.

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

An open product or specification semantic decision defaults to `P0` when it is
recorded as a `Finding` classified to `Phase: Specification`. This applies the
authority-protection branch of `P0`: while the decision remains open,
downstream artifacts can acquire unratified product or specification meaning
unless every reviewer independently notices the reservation. Do not classify an
open semantic decision below `P0` merely because it does not block a specific
downstream deliverable, including the first safety-only formal model.

A `Follow-up` that operationalizes an already accepted decision without
introducing new product meaning does not inherit that default. Classify it by
its actual effect on current-phase progress.

Record an explicit rationale on the Issue when deviating from either default.
Priority remains a work-management judgment: it neither creates nor indicates a
semantic blocking relationship, and it must not be cited as evidence that the
decision itself has been accepted or rejected.

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
- the stable semantic prerequisites and sequencing constraints that affect the
  work, without restating live dependency or Project state;
- constraints and authority boundaries;
- mechanically checkable acceptance criteria that are local to the Issue;
- required generation, traceability, formal, conformance, or implementation
  validation.

An Issue that may change product semantics must distinguish the observed problem
from a proposed resolution and identify every normative, decision, traceability,
and generated artifact that requires synchronization.

When useful, add a collapsed `Coding agent execution brief` with detailed
execution guidance. Keep the Issue outcome-oriented and do not duplicate the
only authoritative technical contract in GitHub prose.

Populate `Status`, `Phase`, `Kind`, and `Priority` in the Project itself; an
Issue body does not repeat them. Use native GitHub parent, sub-issue,
dependency, and Pull Request relationships when available. Do not encode the
only dependency record in Project ordering, and do not restate current
dependency or relationship state in Issue prose.

When a classification deviates from a default and requires a durable rationale,
record the reasoning without copying the current field values or creating a
second live Project record.

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
