---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Bind each accepted invocation to a stable governing workflow definition"
id: "ADR-027"
status: "accepted"
date: "2026-09-16"
decision_body_sha256: "bde101a5cd9ec6ddd23b71036a38bbd7ca495739c6c4dad21b1c2c5984fb830b"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms:
    - "ADR-014"
    - "ADR-024"
governs:
  - "active-invocation workflow-definition binding"
  - "ordinary source-artifact edit visibility"
  - "nested-invocation governing-definition independence"
---

# ADR-027: Bind each accepted invocation to a stable governing workflow definition

## Context

TURNLOCK workflows are developer-readable executable artifacts that developers
and coding agents may author and modify through the same primitives (ADR-009,
`TL-INV-020`). A main-agent region restores the ordinary interactive agency of
the surrounding coding agent (ADR-007, `TL-INV-015`), and that agency can
include repository edits. An ordinary edit of a workflow source artifact while
one of its invocations is active is therefore a realistic event, not a
theoretical one.

Existing accepted decisions establish **who owns declared topology**. ADR-014
and `TL-INV-001`/`TL-INV-002` make the workflow program the source of declared
global orchestration and TURNLOCK the engine that executes, coordinates, and
tracks it without silently inventing undeclared strategy. `TL-INV-013` forbids
hidden agent-owned orchestration, and `TL-INV-030` restricts every global
control transition to workflow-authorized semantics.

Those decisions do not determine **which definition of a mutable source
artifact governs an invocation that is already active when the artifact
changes**. Several mutually compatible semantics remained available: stable
per-invocation binding, live observation of ordinary artifact edits, an implicit
dynamic mutation of the active definition, or a root-wide transitive snapshot
of current and future workflow dependencies.

The ambiguity blocks the first core TLA+ model. The model must represent the
workflow program as the source of declared topology and determine the next
transition, so it cannot state whether the definition associated with an active
invocation is stable, live, or explicitly mutable without inventing behavior.

Adjacent accepted decisions intentionally preserved this question rather than
answering it:

- ADR-018 and `TL-INV-033` require actual completed-execution behavior to remain
  inspectable and forbid presenting a later or current definition alone as proof
  of earlier execution, while expressly leaving workflow-definition binding to
  Issue #4.
- ADR-024, ADR-025, and ADR-026 with `TL-INV-036` require whichever workflow
  definition TURNLOCK binds or resolves as an effective condition to remain
  semantically distinguished, attributable to the governed scope, and
  capturable through the required realizable semantic-boundary capture handoff,
  but they deliberately selected none of stable binding, live observation, or
  explicit dynamic mutation.
- ADR-016 and `TL-INV-032` separate workflow authorship from runtime execution
  authority, and ADR-019 and `TL-INV-034` treat a produced workflow refinement
  as authorship rather than implicit runtime replanning. Neither decides whether
  an ordinary edit becomes visible to, or mutates, an already accepted
  invocation.

Issue #4 identified this as a `decision-required` product-semantic choice. The
corpus did not uniquely entail any of the compatible semantics, so stable
binding must not be treated as already derivable before this decision. The
product owner has now explicitly accepted **stable governing definition per
invocation** through Issue #4's resolution directive.

## Discovery classification

### Accepted product decision

- **Statement:** For every accepted TURNLOCK workflow invocation, TURNLOCK MUST
  have determined a governing workflow definition no later than invocation
  acceptance. That governing definition is the source of declared workflow
  topology for that invocation and remains stable for the lifetime of that
  invocation. Ordinary subsequent modification of the workflow source artifact
  MUST NOT alter the invocation's governing definition or its remaining declared
  topology. Every nested workflow invocation is a distinct invocation and
  determines its own governing workflow definition no later than acceptance of
  that nested invocation; a caller's governing definition does not, merely by
  governing the caller, transitively bind the definitions of workflows that may
  later be invoked.
- **Source and evidence:** Issue #4 identified that the accepted corpus allowed
  multiple edit-visibility semantics for an active invocation and that the first
  executable model would otherwise force a product decision silently. The
  product-owner resolution directive explicitly accepts stable governing
  definition per invocation, accepts independent nested-invocation governing
  definitions, and rejects live source-edit visibility, an implicit root-wide
  transitive dependency freeze, and implicit dynamic mutation of an active
  governing definition.
- **Existing authority:** ADR-014 and `TL-INV-001`–`TL-INV-002`, `TL-INV-013`,
  and `TL-INV-030` establish workflow-owned declared topology but permit
  multiple edit-visibility semantics. ADR-009 and `TL-INV-020` make the same
  artifact editable by developers and coding agents. ADR-007 and `TL-INV-015`
  restore ordinary main-agent agency that may include repository edits. ADR-018
  and `TL-INV-033` separate execution truth from a later or current definition
  shown during inspection. ADR-024, ADR-025, and ADR-026 with `TL-INV-036`
  preserve effective-condition provenance for whichever definition governs
  without selecting the binding rule. ADR-016 and `TL-INV-032` separate
  authorship from runtime execution authority.
- **Semantic disposition:** `decision-required`, resolved by this accepted ADR.
- **Affected layers:** `normative-contract`, `decision-history`,
  `formal-model-or-analysis`, `architecture-or-implementation`, and
  `integration-or-conformance`.
- **Related discoveries or consequences:** ADR-024, ADR-025, and ADR-026
  provenance semantics continue to apply to the effective governing definition.
  Issue #13 retains inspection-correspondence semantics under `TL-INV-033`. A
  follow-up Issue retains whether an execution resource is semantically
  authorized to edit the source artifact of the workflow whose definition
  currently governs it. Deliberate replacement or mutation of an
  active governing definition remains a separate future product decision.
- **Required authority:** Product-owner acceptance through the repository ADR
  process, supplied explicitly for Issue #4.
- **Next action:** Admit `TL-INV-037`, synchronize the normative specification
  and formal traceability projection, and record only planned formal scope
  without inventing executable TLA+ identifiers.

### Derived clarification: invocation acceptance is the binding boundary

- **Statement:** The governing definition MUST be determined no later than
  invocation acceptance. It may be resolved during acceptance or before
  acceptance, but not after it. "First executed step" is not the binding
  boundary, and the moment the user typed a slash command is not the binding
  boundary unless that moment independently is the invocation-acceptance event.
- **Derived from:** The accepted decision makes acceptance the point after which
  no accepted invocation may lack a governing definition and the point at which
  the definition becomes stable.
- **Why no new choice is introduced:** Allowing binding to occur after
  acceptance would permit an accepted invocation to have no determined source
  of declared topology, contradicting the accepted boundary.
- **Failure if omitted:** A runtime could claim an invocation is accepted while
  its governing definition is still undetermined, and the first model could
  re-invent a later binding moment.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `formal-model-or-analysis`, and
  `integration-or-conformance`.
- **Boundary:** This clarification does not define the invocation-acceptance
  event, the invocation-surface mechanism, the mapping between commands and
  workflows, or the syntax by which a reference resolves to a definition.

### Derived clarification: nested independence is not caller unbinding

- **Statement:** Accepting a nested invocation neither replaces the caller's
  governing definition nor freezes the callee's. The caller's governing
  definition continues to govern the caller's own remaining declared topology,
  and the callee establishes its own at its own acceptance. After the callee
  returns, the caller continues under its own governing definition.
- **Derived from:** The accepted decision makes the governing definition
  per-invocation and explicitly rejects a caller's transitive binding of future
  callees.
- **Why no new choice is introduced:** Treating a nested invocation as either a
  re-binding of the caller or as an implicit snapshot of every possible callee
  would contradict the accepted per-invocation scope.
- **Failure if omitted:** A nested call could appear to rewrite the caller's
  remaining declared topology, or a caller's acceptance could appear to freeze
  workflows selected later from a main-agent region that could not have been
  known at caller acceptance.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `formal-model-or-analysis`, and
  `integration-or-conformance`.
- **Boundary:** This clarification does not decide recursion, cyclic call
  graphs, invocation placement admissibility, or concrete depth and resource
  limits; Issue #6 retains the admissibility boundary.

### Derived clarification: stable definition is not replay or reproducibility

- **Statement:** Stability of one invocation's governing definition does not
  make execution deterministic, reproducible, replayable, or comparable, and it
  does not create an execution record, proof, identity, or evidence artifact.
- **Derived from:** The accepted decision selects which definition governs an
  invocation; it defines no persistence, replay, comparison, or reproduction
  capability, and ADR-018, ADR-019, and ADR-024 already keep those concerns
  separate.
- **Why no new choice is introduced:** Reading stability as reproducibility would
  exceed the accepted decision and silently import concerns owned by separate
  decisions.
- **Failure if omitted:** A later design could present stable binding as an
  execution-evidence guarantee it does not provide.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract` and `integration-or-conformance`.

### Derived clarification: autonomy to edit is not authority to edit

- **Statement:** The decision that ordinary source-artifact changes do not
  mutate an active invocation's governing definition does not decide whether a
  user, main-agent region, or independent-agent region is semantically
  authorized to edit the source artifact of a workflow whose definition governs
  it. The ability to edit a file is not semantic authorship authority, and
  editing the source artifact is not the same operation as changing the
  governing definition of an already accepted invocation.
- **Derived from:** The accepted decision governs definition stability and
  rejections of implicit mutation; it does not confer or withhold authorship or
  runtime authority, and existing authority already separates local agency from
  global orchestration authority and authorship from runtime execution
  authority.
- **Why no new choice is introduced:** The accepted decision expressly leaves
  source-artifact edit authority to the separate authority question recorded as
  a follow-up Issue.
- **Failure if omitted:** Runtime stability could be misread either as
  authorizing governing-workflow edits or as forbidding them forever.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract` and `repository-governance-or-documentation`.
- **Boundary:** This clarification ratifies no authority model; the complete
  ex-ante authority question remains unresolved in the follow-up Issue.

### Separately governed mechanisms and policies

Git commit binding, Git SHA binding, SHA-256 or another hash, content
addressing, filesystem snapshots, AST copies, copy-on-write, database revisions,
repository locking, filesystem locking, a concrete workflow-version identifier,
a canonical `Run` object, `RunSpec`, `RunProof`, event sourcing, persistent
execution history, retention duration, crash recovery, replay, reproducibility,
cross-run comparability, experiment management, optimizer machinery, transitive
dependency snapshots, a workflow DSL syntax for versions, a hot-reload API, a
mutation API, a sandbox implementation, and filesystem permission rules remain
`no-normative-impact` in `architecture-or-implementation` unless a later
accepted decision requires an observable mechanism or capability.

## Decision

The universal rule is **stable governing definition per accepted invocation**.

For every accepted TURNLOCK workflow invocation, TURNLOCK MUST have determined a
governing workflow definition no later than invocation acceptance. That
governing definition is the source of declared topology for that invocation and
MUST remain stable for the lifetime of that invocation. Ordinary subsequent
modification of the workflow source artifact MUST NOT alter the invocation's
governing definition or its remaining declared topology.

Conceptually:

```text
artifact W = D1

accept invocation I of W
→ governing definition(I) = D1

artifact W later changes:
D1 → D2

I continues under D1

later accept invocation J of W
→ J receives whatever definition the applicable resolution semantics
  determine for J at J's acceptance
→ J is then stable under that definition
```

For nesting:

```text
accept A1
→ governing definition(A1) = A/D1

later A1 invokes B

accept B1
→ governing definition(B1) = B/E2

B1 completes
→ A1 continues under A/D1
```

The following shape is therefore semantically valid:

```text
A/D1
  → B/E2
  → return
  → A/D1 continues
```

### Acceptance boundary

An invocation MUST NOT become accepted without a governing workflow
definition:

```text
accepted invocation
→ has one governing workflow definition

governing definition
→ determined no later than acceptance
```

The governing definition may be resolved as part of acceptance or before
acceptance. Binding MUST NOT be deferred to the first executed step, and no
later moment may replace the definition once the invocation is accepted.

### Lifetime

The governing definition cannot change during the lifetime of an accepted
invocation merely because its source artifact changes. After the invocation
ceases to be active, the fact that this definition governed that invocation
remains an effective execution-condition attribution governed by ADR-024,
ADR-025, and ADR-026 and `TL-INV-036`. This decision creates no new persistence
or retention guarantee.

### Nested invocation

Every nested workflow invocation is a distinct invocation and determines its
own governing workflow definition no later than acceptance of that nested
invocation. A caller's governing definition does not, merely by virtue of
governing the caller, transitively bind the definitions of workflows that may
later be invoked.

Acceptance of a root or enclosing invocation MUST NOT be interpreted as
recursively freezing every current or future workflow dependency of the whole
execution tree. This preserves genuine runtime composition, including workflows
selected from a main-agent region that could not have been known when the
enclosing invocation began.

### No implicit mutation

An ordinary edit of a workflow source artifact is never an implicit mutation
operation on the governing definition of an already accepted invocation. If
TURNLOCK ever supports deliberate replacement, replanning, or mutation of the
governing definition of an already-active invocation, that capability requires
its own separate accepted product decision with its own authority and semantics.
This decision introduces no such primitive.

### Resolution syntax remains open

This decision does not define how a workflow reference resolves to a definition
and does not make an unqualified workflow name such as `B` mean "latest
version". The only decision here is that whenever TURNLOCK determines the
governing definition of an accepted invocation, that definition is stable for
that invocation. Resolution and version-selection syntax remain independently
governable.

### Responsibility boundaries

This decision does not decide or imply any of the following:

```text
Git commit binding
Git SHA binding
SHA-256 or another hash
content addressing
filesystem snapshots
AST copies
copy-on-write
database revisions
repository locking
filesystem locking
a concrete workflow-version identifier
a canonical Run object
RunSpec
RunProof
event sourcing
persistent execution history
retention duration
crash recovery
replay
reproducibility
cross-run comparability
experiment management
optimizer machinery
transitive dependency snapshots
a workflow DSL syntax for versions
a hot-reload API
a mutation API
a sandbox implementation
filesystem permission rules
```

The following distinctions remain explicit:

```text
ability to edit a file
!=
semantic authority to author/modify that workflow

editing the source artifact
!=
changing the governing definition of an already accepted invocation

authorship authority
!=
runtime orchestration authority

governing-definition stability
!=
replay/reproducibility

stable governing definition for one invocation
!=
transitive snapshot of an entire execution tree

ordinary artifact edit
!=
explicit future active-definition mutation
```

This decision does not claim that source artifacts themselves become immutable.
It does not decide whether a main-agent or independent-agent region is
semantically authorized to edit the source artifact of the workflow currently
governing it; that question is retained by the follow-up authority Issue.

## Rationale

The per-invocation rule preserves the meaning of "declared topology" for an
active invocation.

`TL-INV-001`, `TL-INV-002`, and `TL-INV-030` require every change in global
control to be authorized by executable workflow semantics. An active invocation
can therefore have a stable declared topology only if TURNLOCK knows which
workflow definition supplies that topology. Live observation of ordinary edits
would let authoring activity silently rewrite currently executing orchestration,
making the executing invocation's meaning depend on unrelated future edits and
blurring the distinction between current execution truth and later mutable
source state. The effective governing-definition provenance required by
ADR-024, ADR-025, and ADR-026 must correspond to the definition that actually
governed the invocation.

Binding at acceptance rather than at the first executed step keeps the rule
falsifiable and prevents an accepted invocation from existing without a
determined source of declared topology. It also avoids choosing the user's
typed-command moment as a semantic boundary unless that moment independently is
acceptance under later semantics.

Per-invocation stability is intentionally narrower than a run-wide transitive
dependency snapshot. A nested invocation is a distinct invocation with its own
acceptance, its own declared topology, and its own governing definition. Making
a caller's acceptance freeze every workflow it might later call would prevent
legitimate composition, particularly when a caller invokes a workflow selected
from a main-agent region based on evidence that did not exist at caller
acceptance. The narrower rule preserves both workflow-owned orchestration and
runtime composition.

Rejecting implicit dynamic mutation keeps ordinary editing and deliberate
orchestration mutation distinct. An ordinary source edit is not an operation on
an active invocation, and a future capability that deliberately replaces an
active governing definition must be introduced explicitly rather than emerging
as a side effect of editing a file.

The rule does not require source artifacts, repositories, or files to become
immutable. It requires only that later ordinary source state cannot silently
replace the definition that governs an already accepted invocation's remaining
declared topology. Whether an execution resource is authorized to edit the
source artifact of a workflow that governs it remains a separate authority
question and is not silently answered by definition stability.

## Alternatives considered

### Stable governing definition per accepted invocation

Accepted. Each accepted invocation receives one governing definition no later
than acceptance, keeps it for its lifetime, and each nested invocation
establishes its own. This is the weakest rule that gives "declared topology" a
stable per-invocation meaning without selecting a representation.

### Live observation of ordinary artifact edits

Rejected. An active invocation silently following a later source-artifact
definition makes declared topology unstable, lets ordinary authoring activity
rewrite currently executing orchestration, and makes effective
governing-definition attribution unable to correspond reliably to what actually
governed the invocation. Rejection does not claim that source artifacts are
immutable or that editing them is unauthorized.

### Root/run-wide transitive dependency snapshot as the universal default

Rejected as the universal default. Recursively freezing every workflow that the
root or enclosing invocation might later call because that invocation was
accepted would prevent genuine runtime composition, contradict the
per-invocation acceptance semantics of nested invocations, and overreach the
accepted decision. A future explicit version-pinned reference or stronger
reproducibility profile remains possible, but requires its own semantics.

### Implicit dynamic mutation of an active governing definition

Rejected. An ordinary source edit is never an implicit active-invocation
mutation operation. Deliberate replacement, replanning, or mutation of an
already-active invocation's governing definition remains a separate future
product decision that this ADR does not introduce.

### Another bounded semantic contract

Not required. No additional bounded contract was identified that keeps declared
topology stable per invocation while preserving nested-invocation independence,
rejecting implicit mutation, and leaving representation, resolution syntax,
edit authority, persistence, and reproducibility to separate decisions.

## Consequences

### Benefits

- Every accepted invocation has a well-defined, stable source of declared
  topology, so the first TLA+ model can determine the next transition without
  inventing edit-visibility semantics.
- Ordinary authoring activity cannot silently rewrite currently executing
  orchestration.
- Current execution truth remains distinguishable from later mutable source
  state, strengthening the effective governing-definition attribution required
  by ADR-024, ADR-025, and ADR-026.
- Genuine runtime composition is preserved because nested invocations establish
  their own governing definitions and a caller does not freeze future callees.
- The rule remains mechanism-independent and selects no representation,
  persistence, locking, hashing, snapshot, or version syntax.

### Costs and obligations

- Runtime and adapter designs must determine a governing definition no later
  than acceptance and keep it stable for the invocation's lifetime without
  changing the meaning of declared topology on later source edits.
- Conformance review must distinguish an ordinary source-artifact edit from an
  explicit, separately authorized active-definition mutation, and must not
  present an ordinary edit as a permitted way to mutate an active invocation.
- The effective governing definition, whatever it is, remains subject to
  ADR-024, ADR-025, and ADR-026 provenance obligations for the scope it governs.
- Issue #13 retains how inspection represents correspondence between actual
  execution and the governing definition.
- The follow-up authority Issue retains whether any execution resource may edit
  a governing workflow's source artifact.
- Stronger reproducibility, version-pinning, or explicit mutation capabilities
  require separate accepted decisions and cannot be inferred from this ADR.

## Invariant admission

This decision uniquely entails one distinct universal obligation, `TL-INV-037`:

1. **Independent universal obligation:** Existing workflow-owned-control
   invariants establish who owns declared topology but previously allowed
   multiple edit-visibility semantics. `TL-INV-036` preserves provenance of
   whichever definition actually governed a scope but intentionally did not
   select which definition governs. Stable governing-definition semantics are
   therefore an independent obligation created by this decision, applicable to
   every accepted invocation in every conforming realization.
2. **Existing-owner test:** No existing invariant completely covers the
   obligation. `TL-INV-001`, `TL-INV-002`, and `TL-INV-030` constrain who owns
   declared transitions; `TL-INV-013` forbids hidden agent orchestration;
   `TL-INV-036` preserves attribution of an effective definition; none requires
   that an active invocation's governing definition remain stable under later
   ordinary source edits or that nested invocations determine their own.
3. **Violation test:** An implementation that lets an active invocation's
   remaining declared topology change merely because its source artifact was
   edited directly contradicts this decision and is falsifiable.
4. **Traceability-value test:** A second invariant identity would duplicate the
   same stability obligation and split traceability without adding an
   independently satisfiable requirement.

The nested-invocation consequence, the acceptance-boundary consequence, and the
rejection of implicit mutation explain the scope of the same obligation and
receive no separate invariant identities. Representation, resolution syntax,
persistence, replay, reproducibility, and edit authority likewise receive no
identities.

## Formal applicability

`TL-INV-037` is `planned` for core TLA+ formalization and `not-yet-modeled` for
verification.

A future abstract model can represent both abstract properties without selecting
a mechanism:

```text
once invocation I is accepted with governing definition D,
ordinary source-artifact changes cannot cause I's governing definition
to become another definition D'
```

and

```text
callee invocation J has its own governing definition determined for J
rather than inheriting an implicit transitive root/run snapshot
```

The abstraction must not imply a revision, hash, snapshot, copy, lock,
persistence, or authorization mechanism, and it must not forbid an explicit,
separately authorized future active-definition mutation operation. TLA+ cannot
establish real filesystem edit semantics, what counts as invocation acceptance
in a concrete harness, or whether an execution resource is authorized to edit a
source artifact; those remain conformance and product-authority concerns.

No executable TLA+ model currently exists. `formal/verification.yaml` therefore
records no planned property name, state variable, action, configuration, or TLC
evidence for this invariant. Those identifiers must be added only when the
shared executable model contains them. The mapping remains `pending-model`, and
no `modeled` or `checked` claim is made.

## References

- `docs/specification/turnlock-spec.md`
- `docs/adr/adr-007-preserve-main-agent-cognitive-lineage-and-ordinary-interactive-agency.md`
- `docs/adr/adr-009-use-the-same-turnlock-primitives-for-developer-and-agent-authored-workflows.md`
- `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
- `docs/adr/adr-016-separate-workflow-authorship-from-runtime-execution-authority.md`
- `docs/adr/adr-018-require-completed-workflow-execution-inspectability.md`
- `docs/adr/adr-019-keep-evaluation-and-optimization-policy-outside-turnlock-core.md`
- `docs/adr/adr-024-preserve-effective-execution-condition-provenance.md`
- `docs/adr/adr-025-preserve-condition-specific-provenance-without-requiring-protected-value-disclosure.md`
- `docs/adr/adr-026-define-a-realizable-semantic-boundary-capture-handoff.md`
- `formal/verification.yaml`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
- GitHub Issue #4 and the follow-up ex-ante authority Issue
