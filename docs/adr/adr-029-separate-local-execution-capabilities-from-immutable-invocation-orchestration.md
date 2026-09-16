---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Separate local execution capabilities from immutable invocation orchestration"
id: "ADR-029"
status: "accepted"
date: "2026-09-16"
decision_body_sha256: "8377e851673103542f5219cfecd8b8f0a1adaf5cd0dbd819ee29fbef09bad972"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-001"
    - "ADR-007"
    - "ADR-014"
    - "ADR-016"
    - "ADR-019"
    - "ADR-027"
    - "ADR-028"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Responsibility boundary between local execution capabilities and TURNLOCK orchestration authority"
  - "Workflow source-artifact authoring versus active invocation self-replanning"
  - "Absence of active replanning and rebinding under current TURNLOCK semantics"
  - "Conformance boundary for local actions during an active invocation"
---

# ADR-029: Separate local execution capabilities from immutable invocation orchestration

## Context

TURNLOCK workflows are developer-readable artifacts that developers and coding
agents may author and modify through the same primitives (ADR-009,
`TL-INV-020`). A main-agent region restores the ordinary interactive agency of
the surrounding coding agent (ADR-007, `TL-INV-015`), and that agency can
include repository edits. An execution resource may therefore be able to modify
a workflow source artifact while one of its invocations is active. ADR-027 and
ADR-028 already fix that an ordinary source-artifact edit cannot change the
governing definition of an already accepted invocation, and that the current
formal model must contain no active-definition-mutation transition, no
authorization guard for one, and no placeholder for one.

The follow-up authority Issue originally asked for a general TURNLOCK authority
model: what authority must exist before an agentic region acts, who may confer,
narrow, or revoke it at runtime, and whether participation in an execution
region confers workflow-authorship permission. That framing conflated two
different responsibilities:

```text
1. general local operational capability supplied by the surrounding
   execution environment (filesystem, tools, OS, sandbox)

2. TURNLOCK orchestration authority over declared workflow execution
```

The accepted corpus constrains the second responsibility and says nothing that
makes TURNLOCK the owner of the first. ADR-014 and `TL-INV-001`/`TL-INV-002`
make the workflow program the source of declared global orchestration and
TURNLOCK the engine that executes it without inventing undeclared strategy.
`TL-INV-013` forbids hidden agent-owned orchestration, and `TL-INV-030`
restricts every global control transition to workflow-authorized semantics.
ADR-016 and `TL-INV-032` separate workflow authorship from runtime execution
authority. ADR-019 and `TL-INV-034` keep evaluation and optimization policy
outside core. ADR-027 and ADR-028 with `TL-INV-037` fix the stability of an
accepted invocation's governing workflow definition.

Read as a request for a TURNLOCK-owned permission system, the former framing
would have made TURNLOCK the author of environment policy: ACL/RBAC,
path-based rules, tool allowlists, capability tokens, a generic grant/revoke
protocol, and a privilege class for "meta-workflows". That outcome would add a
second authorization layer whose meaning depends on each harness and would blur
the orchestration responsibility the product actually owns. It would also make
a workflow artifact a specially protected file class, which the stability
semantics already make unnecessary.

The product owner resolved the question explicitly. This ADR records the
accepted decision without editing any accepted ADR body.

## Discovery classification

### Accepted product decision: TURNLOCK does not own general environment permissions

- **Statement:** TURNLOCK core does not define, and MUST NOT invent, a general
  permission system over the local actions of execution resources. ACL/RBAC,
  filesystem permissions, path-based permissions, tool allowlists, capability
  tokens, sandboxing, container permissions, TURNLOCK artifact-specific
  read/write rules, a generic local grant/revoke authority system, a special
  "meta-workflow" semantic class, and a privileged class reserved to official
  TURNLOCK workflows are outside TURNLOCK core. Responsibility for restricting
  local access and local actions belongs to the surrounding execution
  environment, harness, sandbox, or user-controlled environment unless a later,
  explicit, distinct accepted product decision introduces a specific TURNLOCK
  capability. Filesystem or tool capability does not imply TURNLOCK
  orchestration authority, and TURNLOCK core adds no second permission that
  treats a workflow source artifact as specially forbidden merely because it
  contains a TURNLOCK workflow.
- **Source and evidence:** The follow-up authority Issue identified that the
  accepted corpus permitted multiple responsibility readings and could be read
  as requiring a TURNLOCK-owned authority model with ex-ante grants and runtime
  revocation. The product-owner resolution explicitly rejects a TURNLOCK-owned
  general permission system and assigns local operational restrictions to the
  surrounding environment.
- **Existing authority:** ADR-001, ADR-014, and `TL-INV-001`/`TL-INV-002`
  establish workflow-owned orchestration and engine/decision-owner separation.
  `TL-INV-013` and `TL-INV-030` restrict global control transitions to
  workflow-authorized semantics. ADR-007 and `TL-INV-015` restore ordinary
  interactive agency with its environment-provided capabilities. ADR-009 and
  `TL-INV-020` make the same workflow artifact available to developers and
  coding agents. ADR-016 and `TL-INV-032` separate authorship from runtime
  execution authority. ADR-019 and `TL-INV-034` keep evaluation and
  optimization policy outside core. ADR-027 and ADR-028 with `TL-INV-037`
  stabilize an accepted invocation's governing workflow definition. None of
  these sources makes TURNLOCK the owner of general environment permissions.
- **Semantic disposition:** `decision-required`, resolved by this accepted ADR.
- **Affected layers:** `normative-contract`, `decision-history`,
  `architecture-or-implementation`, `integration-or-conformance`, and
  `repository-governance-or-documentation`.
- **Related discoveries or consequences:** The derived clarifications below
  record the already-entailed consequences. Issue #18's former acceptance
  criteria asking for an ex-ante grants system, runtime grant/revoke, an
  authority-source hierarchy, and a workflow-authorship permission model are
  superseded by this decision.
- **Required authority:** Product-owner acceptance through the repository ADR
  process, supplied explicitly for Issue #18.
- **Next action:** Synchronize the normative specification with the
  responsibility boundary, clarify the existing invariant scope without
  admitting a new `TL-INV-*` identity, synchronize formal traceability notes,
  and regenerate the affected ADR and formal projections.

### Derived clarification: source-artifact self-authoring is not active self-replanning

- **Statement:** Modifying the source artifact of the workflow that currently
  governs an active invocation is an ordinary local authoring action when the
  surrounding environment permits it. It does not rebind, replan, or mutate
  the active invocation. The current invocation continues under its governing
  definition `D1`; a later invocation independently resolves its own governing
  definition and may therefore bind to the edited definition `D2`. This holds
  when the later invocation is the same workflow invoked recursively according
  to `D1`'s already-declared semantics.
- **Derived from:** ADR-027 and ADR-028 with `TL-INV-037` already establish that
  an ordinary source edit cannot change the governing definition of an already
  accepted invocation and that no active-definition-mutation transition exists.
  This decision adds only the responsibility boundary that makes the local
  authoring action itself authorized or restricted by the surrounding
  environment rather than by TURNLOCK core.
- **Why no new choice is introduced:** Treating a local source edit as an
  active-invocation mutation would contradict `TL-INV-037`; treating it as
  forbidden by TURNLOCK core would invent the environment permission system
  this decision rejects.
- **Failure if omitted:** "Self-modifying active workflow" wording could
  conflate local source authoring with active self-rebinding and invite either
  an implicit mutation path or a TURNLOCK-owned write protection.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `formal-model-or-analysis`, and
  `integration-or-conformance`.

### Derived clarification: active replanning and rebinding are unsupported and unreserved

- **Statement:** Active replanning, active rebinding, and replacement of the
  governing workflow definition of an accepted invocation are outside and
  contrary to the current TURNLOCK product contract. They are not an open
  future feature, not a roadmap item, not an expected capability, not an
  extension to prepare, not a transition to reserve, and not a
  forward-compatibility obligation. Historical wording stating that a future
  product decision could consider such a capability is only a
  future-governance boundary. The current model contains no
  active-definition-mutation transition, no authorization guard for one, and no
  placeholder for one. A later proposal to introduce such behavior would be an
  explicit modification of governing product semantics and would have to
  reconcile with `TL-INV-037`, ADR-027, and ADR-028.
- **Derived from:** ADR-028 already requires the current model to forbid every
  represented transition that changes an active invocation's governing
  definition and forbids reserving an authorization-gated exception. This
  decision states the same boundary at the product-contract level.
- **Why no new choice is introduced:** Reserving a transition for an
  unauthorized capability would weaken present authority before any decision
  accepts it.
- **Failure if omitted:** An implementation could present active replanning as
  an anticipated extension and prepare a mutation path the product contract
  does not support.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract` and `formal-model-or-analysis`.

### Derived clarification: runtime choices within the declared envelope remain conformant

- **Statement:** A runtime result may select among continuations already
  authorized by the governing definition, including branches, conditions,
  iteration, runtime inputs, results-dependent choices, event-driven behavior,
  bounded delegation, and nested workflow invocation. Selecting a declared
  possibility is not active replanning, does not change the governing
  definition, and does not create a global transition. Workflow-owned control
  is not computational, output, path, or trace determinism.
- **Derived from:** ADR-014, `TL-INV-001`/`TL-INV-002`, and `TL-INV-030`
  already restrict global progression to workflow-authorized transitions while
  preserving runtime selection among declared possibilities. This decision
  reaffirms the distinction between an immutable orchestration envelope and
  nondeterministic results inside it.
- **Why no new choice is introduced:** Reading immutability as determinism
  would exceed the accepted contract and conflate two concerns the corpus
  already separates.
- **Failure if omitted:** The new boundary could be misread as forbidding
  legitimate runtime selection or as promising a deterministic run.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract` and `formal-model-or-analysis`.

### Derived clarification: the same boundary applies to every execution resource

- **Statement:** The boundary is general: an execution resource's local effect
  never implicitly changes the current invocation's governing orchestration.
  No asymmetric rule is decided, such as permitting the main agent to edit
  workflows while forbidding independent agents from doing so, or the reverse.
  Concrete capabilities of each harness or execution form may differ, but that
  difference is an environment, capability, conformance, or integration
  concern rather than a new general TURNLOCK permission rule.
- **Derived from:** ADR-007, ADR-016, ADR-019, and ADR-027 already define
  execution forms by their declared semantics and separate authorship from
  runtime authority without making one form's local capability an orchestration
  authority. No accepted source justifies an asymmetry in the TURNLOCK
  permission boundary.
- **Why no new choice is introduced:** Formulating the boundary as a
  main-agent-specific exception would invent a semantic privilege or
  restriction that no accepted decision establishes.
- **Failure if omitted:** A harness or implementation could infer an
  unauthorized asymmetric authority rule for one execution form.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `integration-or-conformance` and `normative-contract`.

### Derived clarification: the non-conformance condition is orchestration mutation

- **Statement:** TURNLOCK non-conformance is not "an execution resource edited
  a TURNLOCK workflow file". Non-conformance is, for example, an ordinary local
  action that changed the governing definition of an already accepted active
  invocation, a local action that introduced an undeclared global transition
  into the current invocation, or a runtime that treated local
  filesystem/tool capability as authority to replace or replan the current
  global orchestration. A workflow source edit is not a TURNLOCK orchestration
  mutation.
- **Derived from:** `TL-INV-037` already forbids changing an active
  invocation's governing definition; `TL-INV-030` and `TL-INV-013` already
  forbid undeclared global transitions and hidden agent-owned orchestration.
  This decision states the responsibility boundary that prevents local
  capability from being read as orchestration authority.
- **Why no new choice is introduced:** Identifying a workflow-file edit as
  non-conformance would invent a TURNLOCK write permission the corpus does not
  establish.
- **Failure if omitted:** Conformance could reject a permitted local edit or
  accept an actual rebinding because a file changed.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract` and `integration-or-conformance`.

### Separately governed mechanisms and policies

Filesystem sandboxing, OS permissions, container permissions, ACL/RBAC, path
permissions, tool allowlists, capability tokens, a generic runtime
grant/revoke protocol, meta-workflow classification, official-workflow
privilege, optimizer privilege, intent inference for whether a workflow may
author workflows, concrete environment restriction mechanisms, and concrete
harness capability surfaces remain `no-normative-impact` in
`architecture-or-implementation` and `integration-or-conformance` unless a
later accepted decision requires an observable TURNLOCK capability. TURNLOCK
core does not define them, and their absence from core is not an open product
question of this ADR.

## Decision

The product responsibility boundary is:

```text
TURNLOCK orchestration authority
!=
general operational authority over the surrounding environment
```

TURNLOCK core governs declared workflow orchestration. It does not own and MUST
NOT invent general permissions over the local actions of execution resources.
ACL/RBAC, filesystem permissions, path-based permissions, tool allowlists,
capability tokens, sandboxing, container permissions, TURNLOCK artifact-specific
read/write rules, a generic local grant/revoke authority system, a special
"meta-workflow" semantic class, and a privileged class reserved to official
TURNLOCK workflows are outside TURNLOCK core.

```text
filesystem/tool capability
does not imply
TURNLOCK orchestration authority
```

The inverse boundary is explicit:

```text
ordinary source file          -> no implicit TURNLOCK permission needed
TURNLOCK workflow source file -> no implicit TURNLOCK prohibition added
```

If the environment of an execution resource permits modifying a repository
file, TURNLOCK core does not add a second permission that treats a workflow file
as specially forbidden. Restrictions on local access and local actions are
supplied by the surrounding execution environment, harness, sandbox, or
user-controlled environment unless a separately accepted TURNLOCK semantic
explicitly defines otherwise.

### Local authoring does not mutate the governing orchestration

An execution resource may perform the local actions its environment permits,
including inspecting a workflow, proposing a modification, creating a workflow,
modifying another workflow, modifying the workflow whose definition governs the
currently active invocation, deleting or moving an artifact, producing a new
workflow version, or performing workflow authoring as part of an ordinary
evaluator, optimizer, or meta-workflow.

TURNLOCK MUST NOT infer a workflow's purpose or intent to decide whether it may
modify workflows. No rule of the following shape exists in TURNLOCK core:

```text
if workflow purpose == "modify workflows"
then allow workflow modification
```

No equivalent semantic flag exists, such as `meta_workflow = true` or
`workflow_authorship_permission`. A workflow that orchestrates a coding agent
performing workflow authoring remains an ordinary workflow.

The core distinction is:

```text
local agency / local effects
!=
TURNLOCK global orchestration authority
```

A local action, however powerful, never implicitly becomes a modification of
the orchestration governing the current invocation:

```text
artifact A = D1

accept invocation I of A
→ governing definition(I) = D1

during I:
execution resource edits artifact A
A becomes D2

required result:
I continues under D1
```

Never `I switches to D2`. The source-artifact modification is a local authoring
action, not a mutation of the governing definition. It may become visible to a
future invocation under that future invocation's normal resolution semantics.

### Self-authoring versus self-replanning

The situation MUST NOT be described as "self-modifying active workflow",
because that wording conflates two different operations:

```text
source-artifact self-authoring
    MAY occur if the surrounding environment permits it

active invocation self-rebinding
    MUST NOT occur

active invocation self-replanning
    MUST NOT occur
```

```text
A/D1 running
→ execution resource edits artifact A into D2
→ current invocation remains governed by D1
→ invocation ends
→ a later invocation of A may bind to D2
```

The recursive or nested case is equally conformant:

```text
I1 executes A/D1
→ edits source artifact A into D2
→ later, according to D1's already-declared semantics, invokes A again
→ new invocation I2 is independently accepted
→ I2 determines its own governing definition
→ I2 may therefore bind to D2
```

This is not replanning of `I1`. `I1` remains governed by `D1`. No special rule
forbids modifying the currently governing source workflow while other workflows
remain editable.

### Governing orchestration is immutable for an accepted invocation

For every accepted TURNLOCK workflow invocation:

```text
Accepted(I)
→ one governing workflow definition D

while I remains active
→ D remains the governing definition
→ the orchestration envelope authorized by D cannot be replaced,
   rebound, rewritten, or replanned
```

The immutable object is the **orchestration envelope / governing
orchestration**, not every runtime result. A definition may declare branches,
conditions, iteration, runtime inputs, results-dependent choices, event-driven
behavior, bounded delegation to an agent, nested workflow invocation, and other
executable workflow semantics:

```text
D declares:
if X -> A
else -> B
```

`X` may be determined during execution. What is immutable is that `D`
authorizes that decision structure. A runtime result may select a possibility
already declared by `D`; it cannot create a new global possibility that `D`
does not authorize.

```text
workflow-owned control
!=
computational/output/path determinism
```

This decision does not promise that a run is totally deterministic, that its
trace is reproducible, or that runtime inputs cannot influence the selected
continuation. The contract concerns immutability of the governing orchestration
and authorization of global transitions.

### Active replanning and rebinding are outside the current contract

Active replanning, active rebinding, and replacement of the governing workflow
definition of an accepted invocation are outside and contrary to the current
TURNLOCK product contract.

They are not an unresolved future feature, not a roadmap item, not an expected
capability, not an extension to prepare, not a transition to reserve, and not a
forward-compatibility obligation. The current formal model MUST NOT contain an
active-definition-mutation transition, an authorization guard for one, or a
placeholder for one.

Historical wording stating that a future product decision could consider such a
capability is only a future-governance boundary. A later proposal to introduce
such behavior would be an explicit modification of the governing product
semantics; it would require a new accepted decision that explicitly amends,
supersedes, or otherwise reconciles `TL-INV-037`, ADR-027, and ADR-028.

### The same boundary applies to every execution resource

The boundary is general:

```text
execution resource performs local action
→ local effect may occur according to its environment

BUT

local effect
↛ implicit change of the current invocation's governing orchestration
```

No asymmetric rule is decided, such as permitting the main agent to edit
workflows while forbidding independent agents from doing so, or the reverse.
Concrete capabilities of each harness or execution form may differ, but that
difference belongs to the capability, conformance, integration, or environment
layer, not to a new general TURNLOCK permission rule.

### Conformance condition

TURNLOCK non-conformance is **not**:

```text
an execution resource edited a TURNLOCK workflow file
```

Non-conformance is, for example:

```text
an ordinary local edit changed the governing definition
of an already accepted active invocation

a local agent action introduced an undeclared global transition
into the current invocation

the runtime treated local filesystem/tool capability
as authority to replace or replan the current global orchestration
```

```text
workflow source edit
!=
TURNLOCK orchestration mutation
```

TURNLOCK MUST guarantee the second boundary. It does not need to prevent the
first, because a stable governing definition already makes a local source edit
harmless to the active invocation's declared orchestration.

### Evaluation and optimization remain ordinary authorship

ADR-019 and `TL-INV-034` are preserved. An evaluator, optimizer, coding agent,
higher-level system, or ordinary TURNLOCK workflow may analyze an execution and
produce or refine a workflow `W'`. No privileged optimizer and no privileged
official meta-workflow exists in TURNLOCK core.

```text
W
→ execute
→ inspectable execution truth
→ external/user/workflow evaluation or optimization
→ possible authoring/refinement of W'
→ later TURNLOCK invocation may execute W'
```

A workflow refinement remains authorship. It never becomes implicit replanning
of an invocation that is already active.

### Existing invariant owners remain unchanged

This decision creates no new universal obligation and admits no new
`TL-INV-*` identity. The obligations affected by it already have owners:

- `TL-INV-037` owns the stability of an accepted invocation's governing
  workflow definition.
- `TL-INV-030` owns the restriction of global control transitions to
  workflow-authorized semantics and runtime choices among declared
  possibilities.
- `TL-INV-013` owns the prohibition of hidden agent-owned orchestration.
- `TL-INV-032` owns the separation of workflow authorship from runtime
  orchestration authority.
- `TL-INV-034` owns the evaluation/optimization policy boundary.

The product responsibility boundary over general environment permissions is a
scope clarification of those existing obligations, not an independent
state-machine obligation.

## Rationale

The product intent is workflow orchestration inside an existing coding-agent
session, not environmental policy. The surrounding harness, sandbox, OS,
repository configuration, and user already decide which local actions a resource
may perform. Re-declaring that policy inside TURNLOCK would create a second
authority layer whose meaning must be reconciled with every environment, would
make workflow semantics depend on harness-specific permission mechanisms, and
would turn TURNLOCK into the hidden policy owner the product exists to avoid.
ADR-014 and ADR-016 already keep orchestration ownership and authorship
separate from execution authority; a TURNLOCK permission system would
contradict that separation by making workflow semantics the source of local
operational permissions.

A workflow-artifact-specific write protection is unnecessary. ADR-027 and
ADR-028 already make an ordinary source edit harmless to an already accepted
invocation: the invocation continues under its stable governing definition.
Preventing or permitting the edit itself belongs to the environment that
supplies the filesystem or tool capability. Adding a TURNLOCK prohibition would
restrict ordinary repository work without adding orchestration safety, and
would make TURNLOCK enforce an authorship restriction that authorship/runtime
authority separation does not require.

A special meta-workflow class or an intent-inference rule would require
TURNLOCK to decide why a workflow authors workflows. That classification is
unnecessary for the runtime contract: a workflow that orchestrates workflow
authoring is an ordinary workflow whose declared topology is executed. A
privileged class could also become an artificial lock or an artificial grant,
neither of which follows from the accepted product intent.

Active replanning and rebinding must be rejected rather than reserved. Reserving
a transition in the model or presenting the capability as a planned extension
would weaken the present universal obligation and invite an implementation to
prepare a mutation path that current authority does not permit. The accepted
contract is unconditional while an invocation is active: its governing
definition does not change. Understanding this boundary requires keeping two
distinctions separate:

```text
runtime choice authorized by the governing definition
!=
changing the governing definition

future invocation binding
!=
rebinding the current invocation
```

The first permits legitimate runtime composition and results-dependent
progression; the second preserves recursive and nested invocation semantics
without weakening the active invocation's stability.

## Alternatives considered

### TURNLOCK-owned generic authorization model

Rejected. A TURNLOCK-owned ACL/RBAC, capability-token, or generic
grant/revoke layer is unnecessary for the current product intent and conflates
orchestration authority with environmental permissions. It would make local
operational policy part of workflow semantics and duplicate responsibilities
already owned by the surrounding environment.

### Workflow-artifact-specific write protection

Rejected. Treating a workflow source artifact as a specially protected file
introduces a TURNLOCK-owned restriction that the stable governing-definition
semantics make unnecessary. An ordinary source edit already cannot mutate the
active invocation's orchestration, so TURNLOCK does not need to forbid the
edit; the environment that permits or forbids local writes owns that decision.

### Special meta-workflow or official-workflow privilege

Rejected. Inferring or declaring a privileged class of workflows would make
TURNLOCK interpret workflow purpose and could become either an artificial lock
or an artificial privilege. A workflow that authors or refines workflows
remains an ordinary workflow under the same semantics.

### Ordinary source edits may mutate the current orchestration

Rejected. This contradicts ADR-027, ADR-028, and `TL-INV-037` and the original
product intent that declared orchestration remain stable for an accepted
invocation. A local edit is an authoring action, not an orchestration mutation.

### Active replanning or rebinding as a current or anticipated semantic

Rejected for the current contract. TURNLOCK fixes the governing orchestration
of an accepted invocation for its active lifetime; runtime choices remain
inside the declared envelope. Reserving a transition, guard, or placeholder for
active replanning would anticipate a capability that current authority does not
accept.

### Another bounded responsibility contract

Not required. No alternative was identified that preserves workflow-owned
orchestration, stable governing definitions, ordinary local authoring, the
environment's ownership of local restrictions, and the absence of privileged
workflow classes or intent inference without introducing an unnecessary
TURNLOCK permission layer.

## Consequences

### Benefits

- TURNLOCK remains the orchestration engine rather than an environment policy
  owner; local operational restrictions stay with the harness, sandbox, OS, and
  user that supply them.
- Ordinary developer and coding-agent repository work, including workflow
  authoring, remains possible wherever the environment permits it.
- An accepted invocation's orchestration stays stable without requiring
  workflow files to become immutable or specially protected.
- Conformance has a precise failure condition: a changed governing definition,
  an undeclared global transition, or local capability treated as orchestration
  authority.
- The model gains no permission state, meta-workflow flag, authorization guard,
  replanning transition, or placeholder.
- Evaluation and optimization remain ordinary authorship under ADR-019 and
  `TL-INV-034`.

### Costs and obligations

- Runtime and adapter designs MUST NOT treat a surrounding-environment
  filesystem or tool capability as TURNLOCK orchestration authority, and MUST
  NOT introduce a TURNLOCK-owned permission layer to protect workflows.
- Conformance review must verify that a local source edit does not change an
  active invocation's governing definition, that runtime results select only
  among declared possibilities, and that no rebinding or replanning transition
  exists.
- Documentation must not present TURNLOCK as the owner of local access
  restrictions or invite users to express environment policy through TURNLOCK
  semantics.
- A later proposal that adds a TURNLOCK-owned permission capability or an
  active-replanning capability requires a new accepted decision and synchronized
  normative and formal artifacts.
- The environment, not TURNLOCK, must be changed when a user wants to restrict
  which local files an execution resource may edit.

## Invariant admission

No new invariant is admitted. This decision resolves a product responsibility
boundary and clarifies the scope of existing obligations rather than creating
an independent universal state-machine obligation.

The repository invariant-admission test yields:

1. **Independent universal obligation:** The decision fixes who owns general
   local permissions and clarifies that local effects cannot change the
   governing orchestration. The stability consequence is already an
   unconditional universal obligation owned by `TL-INV-037`; the prohibition of
   undeclared global transitions is owned by `TL-INV-013` and `TL-INV-030`; the
   authorship/runtime separation is owned by `TL-INV-032`; the
   evaluation/optimization boundary is owned by `TL-INV-034`. No distinct
   universal obligation remains without an owner.
2. **Existing-owner test:** `TL-INV-037` completely covers the active-invocation
   stability requirement; `TL-INV-030` covers runtime choices among declared
   possibilities versus undeclared global transitions; `TL-INV-032` covers
   authorship versus runtime orchestration authority. The permission
   responsibility boundary limits the scope of those obligations rather than
   adding one.
3. **Violation test:** A runtime that rebinds an active invocation's governing
   definition violates `TL-INV-037`. A runtime that introduces an undeclared
   global transition violates `TL-INV-030`. A core that defines a permission
   system in place of the environment violates this ADR's responsibility
   boundary; because that boundary assigns responsibility rather than
   constraining an executable product state, it is enforced through
   conformance review and normative prose, not through a new invariant
   identity.
4. **Traceability-value test:** A second invariant identity covering the same
   stability or authorship obligations would duplicate existing traceability.
   The environment-permission boundary has no independent state predicate to
   trace and would add an identity without an independently satisfiable
   requirement.

This mirrors the treatment of responsibility boundaries elsewhere in the
corpus: not every accepted responsibility assignment requires a new
`TL-INV-*` identity. `TL-INV-037` remains the sole owner of
governing-definition stability, and the existing workflow-owned-control and
authorship-authority invariants remain the sole owners of their respective
obligations.

## Formal applicability

`TL-INV-037` remains `planned` for core TLA+ formalization and
`not-yet-modeled` for verification. This decision changes no executable
identifier and introduces no reserved transition, state variable, action, or
configuration.

The future abstract model must represent:

```text
while invocation I is active:
governingDefinition[I] does not change
```

and it must not contain an active-definition-mutation transition, an
authorization guard for one, or a placeholder for one. Runtime choices that
select among declared continuations remain represented as authorized
transitions inside the declared envelope, not as changes to the envelope.

The responsibility boundary over general environment permissions is
formalization-not-applicable: it is not a TURNLOCK product state to model. The
model MUST NOT introduce identifiers such as `workflowWritePermission`,
`metaWorkflow`, `AuthorizedMutation`, or `ReplanPermission`, or any equivalent
permission or meta-workflow state. Local filesystem or tool edits are
environment actions; their only modeled consequence is that an active
invocation's governing definition remains unchanged.

TLA+ cannot establish real filesystem edit semantics, the actual local
capabilities of an execution resource, or which restrictions a harness,
sandbox, or user supplies. Those remain environment and conformance concerns.
No executable TLA+ model exists, so `formal/verification.yaml` records no
property, state variable, action, config, or run evidence for this decision.
The manifest is updated only to record this ADR as governing authority for the
already planned `TL-INV-037` formalization and to state that no permission or
replanning model state is intended.

## References

- `docs/specification/turnlock-spec.md` — Sections 0.8, 0.8B, 0.11B, 0.13E,
  2.7, 2.11, and 3.35
- `docs/adr/adr-001-make-the-workflow-own-orchestration-after-session-entry.md`
- `docs/adr/adr-007-preserve-main-agent-cognitive-lineage-and-ordinary-interactive-agency.md`
- `docs/adr/adr-009-use-the-same-turnlock-primitives-for-developer-and-agent-authored-workflows.md`
- `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
- `docs/adr/adr-016-separate-workflow-authorship-from-runtime-execution-authority.md`
- `docs/adr/adr-019-keep-evaluation-and-optimization-policy-outside-turnlock-core.md`
- `docs/adr/adr-027-bind-each-accepted-invocation-to-a-stable-governing-workflow-definition.md`
- `docs/adr/adr-028-clarify-that-tl-inv-037-forbids-governing-definition-changes-under-current-semantics.md`
- `formal/verification.yaml`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
- GitHub Issue #18 and Issue #4
