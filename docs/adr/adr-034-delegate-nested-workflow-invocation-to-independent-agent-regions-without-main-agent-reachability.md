---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Delegate nested-workflow invocation to independent-agent regions without main-agent reachability"
id: "ADR-034"
status: "accepted"
date: "2026-09-18"
decision_body_sha256: "c4a02b4cdc3c606cb066506cfdb2f5901e8b9c5b486b599d94d43060fa3a3185"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-007"
    - "ADR-008"
    - "ADR-011"
    - "ADR-014"
    - "ADR-020"
    - "ADR-021"
    - "ADR-022"
    - "ADR-023"
    - "ADR-029"
    - "ADR-033"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Explicit delegation of nested-workflow selection and invocation authority to workflow-declared independent-agent regions"
  - "Dynamic callee selection by authorized independent agents without a universal parent-enumerated callee whitelist"
  - "Transitive prohibition on session-main-agent-lineage reachability from independent-agent-selected invocation subtrees"
---

# ADR-034: Delegate nested-workflow invocation to independent-agent regions without main-agent reachability

## Context

TURNLOCK already treats workflow-declared independent agents as first-class
execution resources with fresh cognitive lineages, declared semantic missions,
autonomous multi-turn local strategy and tactics, and workflow-owned global
continuation.

ADR-020 establishes that independent-agent local autonomy does not confer global
workflow-orchestration authority and that an independent agent may exercise
available authority but cannot create additional TURNLOCK-governed authority
unilaterally.

ADR-021 separates independent-agent normal completion, optional business output,
and persistent effects.

ADR-022 and ADR-023 establish structured nested invocation with an immediate
caller context and preserved return-bearing continuation.

ADR-029 keeps generic filesystem, tool, repository, sandbox, ACL/RBAC, and
environment permission policy outside TURNLOCK Core.

ADR-033 permits recursive and cyclic workflow invocation through ordinary
invocation semantics.

Current authority does not determine whether a workflow may explicitly delegate
to one of its independent-agent regions the authority to select and invoke
nested TURNLOCK workflows dynamically during that agent's autonomous local work.

Without such delegation, an independent agent that discovers a useful reusable
workflow during investigation would have to end or escape its local cognitive
episode merely to request that some external caller perform the nested
composition.

Unrestricted delegation would create a different problem. A fresh independent
cognitive lineage could indirectly cause a nested workflow to reach the coding
session's existing main-agent cognitive lineage, crossing the accepted boundary
between independent local autonomy and workflow-owned transition into the main
interactive lineage.

GitHub Issue #24 records the product-owner decisions resolving both questions.

## Discovery classification

### B — explicit delegated independent-agent invocation capability

Existing independent-agent autonomy does not grant workflow invocation authority.

The product decision is:

```text
A workflow MAY explicitly delegate
nested TURNLOCK workflow-selection/invocation authority
to a workflow-declared independent-agent region.
```

This creates a specific TURNLOCK semantic capability.

### B — independent-agent-selected invocation cannot reach the session main-agent lineage

The delegated capability is bounded by an explicit composition restriction:

```text
an invocation subtree causally rooted in
an independent-agent-selected nested invocation

MUST NOT transitively reach

the coding session's main-agent cognitive lineage
```

The restriction applies through any number of nested workflow boundaries.

### B — no universal parent-enumerated exact-callee whitelist

TURNLOCK Core does not universally require the parent workflow to enumerate the
exact identities of every workflow an authorized independent-agent region may
later select.

The independent agent may dynamically select among workflows available to it
within its mission and delegated authority.

This decision does not make every existing workflow available or authorized.

### A — the capability is not implicit

ADR-020 already establishes that local autonomy does not permit unilateral
authority expansion.

Therefore an independent agent without explicit delegated nested-workflow
invocation authority does not acquire that authority merely by deciding that it
would be useful.

### A — technical invocation ability is not semantic authority

Generic shell, tool, filesystem, executable, API, or environment access is
outside TURNLOCK Core authority under ADR-029.

Therefore technical ability to attempt a TURNLOCK invocation does not itself
create TURNLOCK semantic invocation authority.

### A — ordinary immediate-caller return applies

When an authorized independent-agent region selects an admitted nested
invocation, the independent-agent region is the immediate caller context.

Normal completion returns to that same independent-agent context and resumes the
same independent cognitive lineage.

### A — escalation remains workflow-owned

An independent agent may determine locally that main-agent intervention would be
useful or required.

That local judgment does not authorize the independent agent to transition into
the session main-agent lineage.

When workflow progression depends on that judgment, the independent-agent region
may expose information through its declared region contract and the parent
workflow may use that information to select a declared main-agent continuation.

The agent owns the local judgment.

The workflow owns the global transition.

## Decision

A workflow MAY explicitly delegate nested TURNLOCK workflow-selection and
invocation authority to a workflow-declared independent-agent region.

The capability is a TURNLOCK semantic authority available to that region when
the workflow delegates it.

It is not implicit in independent-agent execution.

### Explicit delegation is required

The following facts do not themselves grant nested-workflow invocation
authority:

```text
the region is an independent agent
the agent has autonomous local strategy
the agent has shell access
the TURNLOCK executable is technically callable
the agent can read workflow artifacts
the agent knows a workflow exists
the agent has generic environment permissions
```

Without explicit delegation through workflow semantics:

```text
IA1
↓
attempt nested TURNLOCK invocation
```

is not semantically authorized merely because IA1 is technically capable of
attempting it.

This ADR does not select how delegation is represented.

### Delegation remains local authority

Delegated nested-workflow invocation becomes part of the independent agent's
available local strategy/tactics surface within its declared semantic mission.

It does not transfer ownership of the enclosing workflow's global orchestration.

The authority split remains:

```text
workflow
= owns declared global orchestration

independent agent
= owns local strategy and tactics within its declared mission
  and may exercise explicitly delegated local invocation authority

TURNLOCK
= executes admitted orchestration
```

The independent agent does not thereby own the enclosing workflow's:

```text
sequence
branching
fan-out
join
continuation
main-agent transitions
```

### Dynamic callee selection is permitted

An authorized independent agent MAY choose the callee dynamically during its
local work.

For example:

```text
workflow A
↓
declare IA1
mission: diagnose regression
↓
explicitly delegate nested-workflow invocation authority
↓
IA1 investigates
↓
IA1 discovers an available reusable workflow X
↓
IA1 selects X
```

The parent workflow need not universally pre-enumerate `X` by exact identity for
TURNLOCK Core semantics to permit the selection.

### No universal exact-callee whitelist

TURNLOCK Core MUST NOT require every workflow using delegated independent-agent
invocation to enumerate every exact permitted callee identity in advance.

The decision is:

```text
no universal TURNLOCK-Core parent-enumerated exact-callee whitelist
```

It is not:

```text
all workflows are available
```

and it is not:

```text
the independent agent may invoke every workflow that exists
```

Workflow availability, visibility, installation, discovery, namespace,
environment permissions, or harness exposure may be constrained outside this
decision.

This ADR selects no representation for available workflows.

### Mission boundary remains applicable

Delegated invocation authority does not erase the independent-agent region's
workflow-declared semantic mission.

Nested workflow selection is one possible local tactic in pursuit of that
mission.

The delegation does not authorize the independent agent to invent an unrelated
global mission.

This ADR does not define an algorithm for deciding semantic relevance of a
selected workflow to the mission.

### Invocation authority and composition admissibility are distinct

Every independent-agent-selected nested invocation is subject to at least two
independent semantic questions:

```text
1. does this independent-agent region possess delegated nested-workflow
   selection/invocation authority?

2. is this particular attempted callee admissible in the inherited
   execution context?
```

Conceptually:

```text
IA selects B
↓
delegated invocation authority present?
├── no
│   ↓
│   invocation not authorized
│
└── yes
    ↓
    B admissible under inherited context?
    ├── no
    │   ↓
    │   invocation not accepted
    │
    └── yes
        ↓
        B may be accepted
```

Delegated invocation authority MUST NOT imply automatic composition
admissibility.

Composition admissibility MUST NOT itself create invocation authority.

Issue #6 owns the general inherited/transitive composition-admissibility
contract.

### Structured return preserves the independent-agent caller

For an admitted independent-agent-selected invocation:

```text
IA1
↓
invoke B
↓
B executes
↓
B normally completes
↓
IA1 resumes
```

The same independent-agent region is the immediate caller.

The same independent cognitive lineage resumes.

Normal completion of B MUST NOT silently:

```text
complete IA1
replace IA1
spawn a fresh IA2 as the return target
skip directly to the parent workflow's post-IA continuation
return directly to the session main agent
```

unless a separate later workflow transition independently authorizes such
behavior.

### Rejection before acceptance creates no callee

If IA1 attempts B and B is rejected before invocation acceptance:

```text
IA1 active
↓
attempt B
↓
rejection before acceptance
```

then:

```text
no accepted B invocation exists
no B invocation lifetime exists
no B governing workflow definition is bound
no B call/return episode exists
IA1 remains the active caller context
IA1's local continuation is not consumed
normal post-B return semantics do not occur
```

The rejection must remain attributable/observable to the attempting caller as
required by the eventual general admission contract.

This ADR does not decide whether IA1 then retries, selects another workflow,
continues without B, reports failure, terminates, or signals its parent.

### IA-selected invocation subtrees cannot reach the session main-agent lineage

For every invocation accepted because an independent-agent region selected it
under delegated nested-workflow invocation authority, the complete causally
nested invocation subtree rooted at that call MUST NOT transitively reach the
coding session's existing main-agent cognitive lineage.

Direct reachability is forbidden:

```text
IA1
↓
select B
↓
B
↓
main-agent continuation
```

Indirect reachability is also forbidden:

```text
IA1
↓
select B
↓
B invokes C
↓
C invokes D
↓
D reaches main-agent continuation
```

The restriction is transitive.

Crossing another workflow invocation boundary does not reset it.

### Recursive/cyclic composition does not reset the restriction

ADR-033 permits recursive and cyclic workflow invocation.

That permission applies normally inside an IA-selected subtree when the
individual calls are otherwise authorized and admissible.

For example:

```text
IA1
↓
B
↓
C
↓
B
```

may be valid.

However, the inherited restriction remains:

```text
IA-selected invocation subtree
→ no session-main-agent-lineage reachability
```

Therefore this remains forbidden:

```text
IA1
↓
B
↓
C
↓
B
↓
D
↓
main-agent continuation
```

A recursive or cyclic edge MUST NOT erase, reset, or widen the restriction.

### Parallel or conditional composition does not reset the restriction

The same restriction applies when the nested subtree contains workflow-declared
parallel branches or conditions.

An IA-selected subtree MUST NOT make the session main-agent lineage reachable in
one branch merely because another branch does not reach it.

The restriction concerns reachability permitted by the admitted nested
composition, not whether a particular runtime schedule happens to exercise the
main-agent path.

This ADR does not select a reachability-analysis algorithm.

### Main-agent escalation remains workflow-owned

An independent agent MAY determine during local work that intervention by the
session main agent would be useful or required.

The independent agent MUST NOT convert that local judgment into a main-agent
transition through its delegated nested-workflow invocation capability.

The intended pattern is:

```text
workflow A
↓
IA1
↓
local judgment:
escalation_needed = true
↓
IA1 exposes that information through its declared region contract
when the workflow requires it
↓
parent workflow receives the information
↓
workflow-declared condition selects main-agent continuation
```

The invalid shortcut is:

```text
IA1
↓
"need main agent"
↓
select B
↓
B reaches main-agent continuation
```

The local judgment belongs to IA1.

The global transition into the session main-agent lineage belongs to executable
workflow semantics.

### Independent-agent business output remains optional

This decision does not require every independent-agent region to return a
business payload.

Existing ADR-021 semantics remain:

```text
IA performs effects
↓
IA reaches normal completion
↓
workflow continues
```

with no fabricated business value when the region contract requires none.

If workflow progression depends on information produced by the independent
agent, that information MUST be made available through the declared region
contract.

For example:

```text
IA determines escalation_needed
↓
parent workflow branches on escalation_needed
```

requires the applicable region contract to expose that information.

This ADR does not select whether the representation is a boolean, enum, tagged
value, structured object, JSON value, status code, typed result, or another
representation.

### TURNLOCK Core does not become a generic authorization system

This delegation capability does not introduce:

```text
generic ACL
RBAC
principal/resource/action matrices
per-workflow access-control lists
mandatory callee whitelists
mandatory callee blacklists
capability tokens
permission tokens
grant objects
namespace policy
workflow registries
workflow visibility policy
filesystem permissions
repository permissions
path permissions
sandbox permissions
tool allowlists
shell permission policy
OS permission policy
authentication
```

ADR-029 remains authoritative:

```text
TURNLOCK orchestration authority
!=
generic surrounding-environment permission policy
```

## Invariant consequence

The invariant-admission procedure admits exactly one new stable invariant:

```text
TL-INV-040
Independent-agent-selected invocation main-lineage isolation invariant
```

`TL-INV-040` owns the new universal transitive safety restriction:

```text
an invocation subtree causally rooted in
an independent-agent-selected nested invocation

MUST NOT transitively reach

the coding session's main-agent cognitive lineage
```

No second new invariant is admitted.

The positive delegated capability and its ordinary structured consequences are
projected onto existing invariant responsibilities:

```text
TL-INV-018
→ normal completion returns to the same immediate caller,
  including an independent-agent caller

TL-INV-019
→ nested execution cannot bypass or replace the independent-agent caller
  or rewrite enclosing orchestration

TL-INV-025
→ a workflow-declared independent-agent region may receive explicit
  delegated nested-workflow selection/invocation authority;
  the capability is not implicit;
  exact callee identities need not be universally parent-enumerated

TL-INV-030
→ delegated IA invocation remains local authority and does not transfer
  ownership of global workflow progression or main-agent escalation

TL-INV-031
→ TURNLOCK expressive power includes delegated independent-agent-selected
  nested workflow invocation
```

`TL-INV-026` remains the owner of independent-agent cognitive-context
provenance and is unchanged by this decision.

`TL-INV-035` remains the owner of workflow-declared invocation and is not
repurposed to own independent-agent-selected invocation.

`TL-INV-039` remains the owner of non-forkability of the session main-agent
lineage across unordered concurrent continuations and is not broadened by this
decision.

Issue #6 remains the owner of the general transitive composition-admissibility
contract.

## Formal applicability

The positive delegated capability and the transitive no-main-lineage restriction
are relevant to the future core state-machine model.

A future model may abstract explicit delegation as a semantic authorization fact.

It MUST distinguish:

```text
technical ability to attempt invocation
```

from:

```text
TURNLOCK semantic authority to create an invocation
```

The model must also distinguish:

```text
invocation authority
```

from:

```text
composition admissibility
```

A future model of `TL-INV-040` must preserve the transitive no-main-lineage
restriction across represented nested, conditional, parallel, recursive, and
cyclic composition.

The model may use finite workflow sets or finite invocation depth as modeling
bounds.

Those bounds MUST NOT become a mandatory parent-enumerated callee whitelist,
product-level recursion limit, or universal TURNLOCK Core authorization model.

No static-analysis algorithm, graph traversal, effect system, capability
lattice, theorem prover, scheduler, token, ACL mechanism, or runtime
representation is selected.

No successful TLA+/TLC verification is claimed.

## Rationale

Independent agents exist so a workflow can deliberately delegate autonomous
local cognition to a fresh lineage.

Local autonomy is materially more useful when the agent can reuse TURNLOCK
workflows as local subroutines without terminating its cognitive episode merely
because the exact reusable workflow was not known to the parent in advance.

That capability must remain local.

Allowing an independent agent to transitively reach the coding session's
existing main-agent lineage would let a fresh independent cognitive lineage
commandeer a global session transition that belongs to workflow-owned
orchestration.

The accepted design therefore combines:

```text
explicit delegation
+
dynamic local workflow selection
+
ordinary structured return
+
ordinary admission
+
no transitive main-agent reachability
+
workflow-owned escalation
```

## Alternatives considered

### Give every independent agent workflow-invocation authority automatically

Rejected. Local autonomy does not create TURNLOCK orchestration authority.

### Treat shell access as invocation authority

Rejected. Technical environment capability and TURNLOCK semantic authority are
distinct.

### Require the parent to enumerate every exact callee identity

Rejected as a universal TURNLOCK Core requirement. It would remove much of the
value of autonomous local discovery and reuse.

### Permit unrestricted IA-selected nested invocation

Rejected. It could allow a fresh independent cognitive lineage to transitively
enter the session's existing main-agent lineage.

### Permit main-agent reachability when the IA considers escalation necessary

Rejected. The IA may own the local judgment, but executable workflow semantics
must own the global transition.

### End the IA region before every nested workflow call

Rejected. It destroys the useful local cognitive continuity that delegated
nested composition is intended to preserve.

### Make every IA return a structured business payload

Rejected. ADR-021 already allows effect-oriented regions whose contract requires
no business output.

### Create a generic TURNLOCK ACL/RBAC/capability-token system

Rejected. ADR-029 keeps generic environment authorization policy outside
TURNLOCK Core.

### Select a graph-reachability implementation now

Rejected. The product specifies the admissibility property, not the algorithm
used to establish it.

## Consequences

* A workflow can explicitly delegate nested-workflow selection/invocation
  authority to a workflow-declared independent-agent region.
* The capability is not implicit in independent-agent autonomy.
* Technical shell/tool/API access does not create semantic invocation authority.
* An authorized independent agent may select an available callee dynamically.
* TURNLOCK Core does not universally require exact parent-enumerated callee
  identities.
* Delegated invocation remains bounded by the independent agent's declared
  semantic mission.
* Delegated invocation authority does not imply composition admissibility.
* Composition admissibility does not grant invocation authority.
* Normal completion returns to the same independent-agent caller and cognitive
  lineage.
* Rejection before acceptance creates no callee invocation.
* An IA-selected invocation subtree cannot transitively reach the session
  main-agent cognitive lineage.
* Nested, parallel, conditional, recursive, and cyclic composition do not reset
  that restriction.
* Main-agent escalation remains a workflow-owned transition.
* Independent-agent business output remains optional unless required by the
  declared region contract.
* No generic TURNLOCK ACL/RBAC/capability-token system is introduced.
* `TL-INV-040` is the sole new stable invariant admitted by this decision.
* Issue #6 remains responsible for general inherited/transitive composition
  admissibility.

## Verification obligation

A conforming realization must be capable of demonstrating:

1. an independent-agent region with no delegated nested-workflow authority whose
   invocation attempt is not semantically authorized;
2. an independent-agent region with explicit delegated authority dynamically
   selecting a workflow not pre-enumerated by exact identity in the parent;
3. ordinary admission still being required after authority is established;
4. normal completion returning to the same independent-agent caller;
5. rejection before acceptance creating no callee and leaving the
   independent-agent caller active;
6. an admitted IA-selected subtree containing mechanical, raw-LLM, or
   independent-agent work without requiring main-agent reachability;
7. rejection of direct session-main-agent reachability from an IA-selected
   subtree;
8. rejection of indirect session-main-agent reachability through multiple nested
   workflows;
9. preservation of the restriction through recursive/cyclic composition;
10. preservation of the restriction through represented parallel/conditional
    composition; and
11. a valid workflow-owned escalation pattern in which IA-produced information
    is consumed by the parent workflow and the parent workflow selects a
    main-agent continuation.

The demonstration MUST NOT depend on a product-level ACL system, callee
whitelist representation, capability token, static graph algorithm, effect
system, theorem prover, scheduler, Rust structure, DSL syntax, namespace,
registry, process model, or harness-specific permission mechanism selected by
this ADR.

## References

* `docs/specification/turnlock-spec.md`
* `docs/adr/adr-007-preserve-main-agent-cognitive-lineage-and-ordinary-interactive-agency.md`
* `docs/adr/adr-008-allow-nested-workflow-invocation-from-main-agent-regions.md`
* `docs/adr/adr-011-make-independent-agents-first-class-and-support-parallel-fan-out-fan-in.md`
* `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
* `docs/adr/adr-020-define-independent-agent-context-provenance.md`
* `docs/adr/adr-021-separate-independent-agent-completion-output-and-effects.md`
* `docs/adr/adr-022-allow-workflow-declared-invocation-with-structured-call-return-semantics.md`
* `docs/adr/adr-023-clarify-caller-context-and-continuation-semantics-across-nested-workflow-invocations.md`
* `docs/adr/adr-029-separate-local-execution-capabilities-from-immutable-invocation-orchestration.md`
* `docs/adr/adr-032-allow-main-agent-participation-in-workflow-owned-concurrency-without-cognitive-lineage-fork.md`
* `docs/adr/adr-033-permit-recursive-and-cyclic-workflow-invocation-under-ordinary-invocation-semantics.md`
* `formal/verification.yaml`
* GitHub Issue #24
