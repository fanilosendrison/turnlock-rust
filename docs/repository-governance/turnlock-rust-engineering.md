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

- `P0`: applies when either branch holds.
  - current-progress branch: the work materially blocks current engineering
    progress or the current critical path;
  - protection branch: continuing normal work before the item is resolved can
    materially compromise or amplify risk to correctness, authority,
    traceability, verification integrity, or repository work-governance
    integrity. Cross-cutting governance failures qualify even when they do not
    block one specific downstream deliverable.
- `P1`: the work should be completed in the current phase, but other valid
  current-phase work remains safe to continue before it completes.
- `P2`: important retained work that does not materially block current progress
  and does not need to complete in the current phase.
- `P3`: useful retained work that can safely wait without meaningful current
  scheduling cost.

Keep the distinction between `P0` and `P1` explicit: `P1` means important now
with continued normal work still safe; `P0` means delay can block progress or
compromise protected engineering or governance integrity.

Priority is live, portfolio-relative scheduling state. Revalidate it when a
material change to the open work graph or current engineering context can
change relative scheduling urgency. Priority is not a permanent classification
assigned once at Issue creation.

Treat the current phase as the lifecycle domain that owns the immediate
critical-path deliverable, judged from the live open portfolio and current
authoritative context. It is not a stored Project field.

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

Record an explicit rationale when deviating from either default. Priority
remains a work-management judgment: it neither creates nor indicates a semantic
blocking relationship, and it must not be cited as evidence that the decision
itself has been accepted or rejected.

Keep `Priority` distinct from `Status`, `Phase`, `Kind`, and native dependency
relationships:

- do not encode a dependency by changing `Priority`;
- do not encode `Priority` by changing `Status`;
- do not read `P0` as automatically `Ready`; `P0` with `Backlog` is valid when
  critical work is not yet independently executable;
- a lower-priority item may still be `Ready`.

Readiness and scheduling importance are separate.

## Priority revalidation

Revalidate `Priority` as live, portfolio-relative state. A full pass over every
open Turnlock-Rust Engineering Issue is mandatory after any of these events:

1. durable Issue creation: after creating any new durable Issue and adding it
   to the Project, re-evaluate every open Project Issue, including the new one;
2. Issue completion, closure, or reopening;
3. native dependency-graph change: an added or removed blocked-by or blocking
   relationship;
4. authoritative decision change: an accepted ADR, normative specification
   change, formal-governance change, or other authoritative repository change
   that resolves or creates a prerequisite, changes a work item's
   critical-path role, or changes the risk of continuing downstream work;
5. phase transition: a material change in the active engineering focus among
   `Specification`, `Formal Verification`, and `Implementation`, because `P1`
   is relative to the current phase;
6. validated cross-cutting governance finding: a newly validated concern that
   affects the machinery by which multiple other Issues are selected,
   interpreted, validated, or governed, even without a direct dependency
   relationship.

Do not run a full portfolio pass solely for comment creation, label-only
changes, assignee changes, formatting-only Issue-body edits, historical
provenance edits, or a Priority correction itself, unless the operation also
reveals one of the material changes above.

### Revalidation algorithm

1. Load canonical live work state: read every open Issue that is a member of
   Turnlock-Rust Engineering, using Issue state, Project `Status`, `Phase`,
   `Kind`, `Priority`, native dependencies, and native parent/sub-issue
   relationships from their GitHub owners. Do not derive live values from
   Markdown bodies.
2. Refresh authoritative context: read `AGENTS.md`, this profile, the discovery
   classification profile, and the current accepted specification, ADR, and
   formal authority referenced by the affected Issues. Do not reinterpret
   product semantics while scheduling.
3. Evaluate every open Issue with the `P0`/`P1`/`P2`/`P3` contract, in this
   order: a repository default forcing `P0` (for example an unresolved
   specification semantic `Finding`); the current-progress branch; the
   protection branch; then `P1` if the work must complete in the current phase;
   then `P2` for important retained non-blocking work; otherwise `P3`. This is
   the complete decision tree; do not invent a scoring model.
4. Mutate only the Project `Priority` field where the computed value differs
   from the live value. Do not edit an Issue body to record the value and do not
   create a manually maintained portfolio-priority table.
5. Verify: re-read every changed Project item, confirm the intended `Priority`,
   and confirm that no unintended `Status`, `Phase`, `Kind`, relationship,
   body, or repository change occurred.

Never introduce a second ranking field, numeric weight, severity value, or
priority-scoring model.

## Autonomous pickup

Select autonomous work from the Project's `Agent Queue` in this order:

1. consider only `Status = Ready` issues; `In Progress` work stays visible but
   is not a new pickup candidate;
2. choose the highest `Priority` first: `P0` before `P1`, `P1` before `P2`,
   `P2` before `P3`;
3. do not select a lower-priority `Ready` Issue while a higher-priority `Ready`
   Issue exists, unless the user explicitly selects another item;
4. an explicit user selection overrides pickup order for that action only and
   does not rewrite `Priority`.

Priority does not create a dependency. When two `Ready` Issues share a
priority, obey native dependency ordering when one must precede the other;
otherwise retain the Project's existing manual order as the tie-break. Do not
invent another ranking field.

Do not let a newly created `P0` automatically interrupt an `In Progress` Issue.
Priority governs scheduling and new pickup. If a discovery makes continued
active work invalid or unsafe, represent the actual condition through a native
dependency, a `Status` change, an authority conflict, or explicit user
direction. Do not use `Priority` as an implicit cancellation or preemption
mechanism.

Keep `Priority` visible in the `Agent Queue` view. When the Project tooling
does not support configuring view ordering, this pickup contract remains
authoritative for agent behavior regardless of UI sort configuration.

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
independently. Add it to Turnlock-Rust Engineering, populate all required
fields, and establish the required native relationships.

Complete durable-Issue creation only after a full portfolio `Priority`
revalidation under this profile:

```text
create Issue
→ add to Project
→ populate required fields
→ establish required native relationships
→ revalidate Priority across every open Project Issue
→ verify changed priorities
```

Do not require the Issue body to mirror the resulting fields.

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
