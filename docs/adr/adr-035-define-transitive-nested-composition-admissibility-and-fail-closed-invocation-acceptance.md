---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Define transitive nested-composition admissibility and fail-closed invocation acceptance"
id: "ADR-035"
status: "accepted"
date: "2026-09-18"
decision_body_sha256: "3b0bb876f73c30a4968b743edaeaaa55caf3336273342fd4006aa8891079b533"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-008"
    - "ADR-013"
    - "ADR-014"
    - "ADR-022"
    - "ADR-023"
    - "ADR-027"
    - "ADR-032"
    - "ADR-033"
    - "ADR-034"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "General transitive admissibility closure for nested workflow composition"
  - "Per-invocation fail-closed admission before nested invocation acceptance"
  - "Workflow invocation inside parallel or otherwise restricted contexts when independently authorized and admissible"
  - "Pre-acceptance rejection semantics for nested invocation attempts"
---

# ADR-035: Define transitive nested-composition admissibility and fail-closed invocation acceptance

## Context

TURNLOCK supports structured nested workflow invocation from multiple semantic
decision owners.

ADR-008 permits a main-agent region to select a nested workflow.

ADR-022 permits workflow-declared nested invocation.

ADR-034 permits a workflow to explicitly delegate dynamic nested-workflow
selection/invocation authority to a workflow-declared independent-agent region.

ADR-032 permits main-agent continuation inside workflow-owned concurrency while
forbidding unordered concurrent continuation of the same main-agent cognitive
lineage.

ADR-033 permits direct recursion and cyclic workflow call graphs.

ADR-034 additionally establishes that an invocation subtree selected by an
independent-agent region MUST NOT transitively reach the coding session's
main-agent cognitive lineage.

These decisions make nested composition expressive, but they create a general
closure requirement.

A restriction imposed by an enclosing execution context must not be bypassable
merely by crossing one or more nested workflow boundaries.

For example, a same-main-lineage concurrency conflict remains a conflict when
one occurrence is hidden behind a nested workflow:

```text
parallel
├── main-agent M/A
└── workflow B
      └── main-agent M/B
````

Likewise, ADR-034's isolation restriction must survive arbitrary nested workflow
boundaries:

```text
IA1
↓
B
↓
C
↓
D
↓
main-agent continuation
```

The remaining product question is the general semantic contract under which an
otherwise authorized nested invocation may be accepted inside a context that
carries such restrictions.

GitHub Issue #6 records that decision.

## Discovery classification

### B — nested invocation is permitted inside parallel or otherwise restricted contexts when admissible

Existing nested invocation authority did not by itself establish every placement
in which such invocation may occur.

The accepted decision is:

```text
a nested workflow invocation MAY occur
inside a workflow-owned parallel branch
or another context carrying admissibility restrictions

when

the invocation is independently authorized
and
the resulting composition preserves every applicable restriction
```

Nested workflow invocation is composition inside a branch's declared
progression; it is not a new execution form.

### B — admissibility is decided per attempted invocation before acceptance

Each attempted nested invocation has its own admission boundary.

Before TURNLOCK accepts that invocation, the invocation must independently
satisfy its invocation-authority rules and its composition-admissibility rules.

The general shape is:

```text
attempt invocation
↓
determine the workflow definition
that would govern the callee if accepted
↓
check invocation authority
↓
check composition admissibility
↓
accept or reject
```

### B — inability to establish required compatibility fails closed

When preserving an applicable admissibility restriction is required for
acceptance and that preservation cannot be established at the invocation's
acceptance boundary, TURNLOCK MUST NOT accept the invocation.

The runtime MUST NOT manufacture compatibility through silent serialization,
first-arrival ordering, execution-form substitution, hidden topology rewriting,
or another undeclared repair.

### B — pre-acceptance rejection creates no callee invocation

When an invocation attempt is rejected before acceptance, no accepted callee
invocation exists.

The caller is not allowed to treat that rejection as successful completion of
the nonexistent callee.

### A — nesting cannot erase an existing restriction

ADR-014 requires workflow-owned declared topology rather than runtime-invented
global orchestration.

ADR-032 and TL-INV-039 define a same-main-lineage concurrency restriction whose
meaning depends on declared causality rather than runtime timing.

ADR-034 and TL-INV-040 define a transitive no-main-lineage reachability
restriction for IA-selected invocation subtrees.

Therefore crossing a workflow boundary cannot silently erase either restriction
without contradicting the accepted semantics that created it.

The general derived rule is:

```text
nested composition does not reset
an applicable admissibility restriction
```

### A — recursion and cycles do not reset restrictions

ADR-033 already requires recursive/cyclic invocation to remain ordinary nested
invocation and states that recursion does not create an admissibility escape.

Therefore revisiting a workflow identity cannot create a fresh unrestricted
context.

### A — invocation authority and composition admissibility are distinct

ADR-034 explicitly distinguishes delegated IA invocation authority from
composition admissibility.

The same distinction applies generally:

```text
authorized
!=
admissible
```

Both are required for acceptance.

### A — the admitted workflow definition must be the accepted governing definition

ADR-027 requires every accepted invocation to bind one governing workflow
definition no later than acceptance and keep it stable for that invocation's
lifetime.

An admissibility decision would not protect the accepted composition if
TURNLOCK could validate one definition and bind another.

Therefore the workflow definition whose composition is admitted MUST be the
definition that becomes governing for that invocation if acceptance succeeds.

## Decision

Every attempted nested TURNLOCK workflow invocation is subject to an
implementation-independent composition-admissibility boundary before acceptance.

The admission decision concerns the attempted invocation in its actual caller
and surrounding semantic context.

### Authorization and admissibility are independent requirements

An attempted nested invocation may be accepted only if both conditions hold:

```text
invocation is independently authorized
+
composition is admissible under every applicable restriction
```

Invocation authorization answers whether the relevant decision owner is allowed
to attempt/create the nested invocation.

Composition admissibility answers whether accepting the callee in that context
would preserve the restrictions that govern that composition.

Neither question substitutes for the other.

### Applicable restrictions remain closed under nested composition

When an accepted restriction's normative scope extends into nested descendants,
every accepted nested invocation within that scope remains subject to that
restriction.

Crossing a workflow boundary MUST NOT by itself:

```text
erase
reset
weaken
widen
bypass
satisfy
or terminate
```

such a restriction.

The same rule applies across recursive and cyclic workflow invocation.

`TL-INV-041` does not extend a restriction beyond the scope assigned by the
decision or invariant that owns that restriction.

It preserves each restriction according to its own accepted scope.

### Admissibility may depend on surrounding topology

Composition admissibility is not necessarily a property of the callee in
isolation.

Applicable restrictions may require considering semantic facts such as:

```text
caller context
surrounding declared topology
sibling branches
declared causal ordering
co-reachability
established mutual exclusion
cognitive-lineage identity
caller provenance
declared conditions
restriction scope
```

For example:

```text
parallel
├── main-agent M/A
└── workflow B
      └── main-agent M/B
```

is inadmissible for one continuing main-agent lineage when the declared topology
allows `M/A` and `M/B` to be unordered co-reachable continuations.

The nested workflow boundary around B does not hide that conflict.

### Workflow invocation may occur inside a parallel branch

A workflow-owned parallel branch MAY contain nested workflow invocation as part
of that branch's declared progression.

For example:

```text
parallel
├── mechanical
└── workflow B
      └── raw LLM
```

may be admitted.

Nested invocation inside a branch remains subject to ordinary invocation
authority and this ADR's composition-admissibility contract.

Nested workflow invocation is composition; it is not a fifth parallel execution
form alongside mechanical execution, raw LLM inference, independent-agent
execution, and main-agent continuation.

### Declared causality or mutual exclusion may establish compatibility

An admissibility restriction that concerns co-reachability does not prohibit
multiple syntactic occurrences merely because they both exist in the workflow
artifact.

For example:

```text
parallel
├── if X:
│     main-agent M/A
└── workflow B
      └── if !X:
            main-agent M/B
```

may be admissible when the applicable declared semantics establish that the
same-lineage uses are mutually exclusive.

The product requires the semantic property.

It does not select the mechanism used to establish it.

### Runtime scheduling does not establish admissibility

A composition MUST NOT become admissible merely because one concrete runtime
schedule happens to avoid the conflict.

Runtime order is not a substitute for workflow-declared causal order.

TURNLOCK MUST NOT repair an inadmissible topology by silently:

```text
serializing branches
using first-arrival order
dropping a branch
changing a callee
substituting an execution form
cloning a cognitive lineage
lifting invocation authority
inventing a causal edge
rewriting the declared topology
```

### Fail closed when required preservation cannot be established

If acceptance requires TURNLOCK to establish that an applicable restriction is
preserved and that compatibility cannot be established at the attempted
invocation's acceptance boundary, the invocation MUST NOT be accepted.

The accepted rule is:

```text
required compatibility cannot be established
→
invocation not accepted
```

It is not:

```text
required compatibility cannot be established
→
accept and rely on runtime luck
```

This decision chooses a semantic outcome, not a proof or analysis algorithm.

### Admission occurs per invocation occurrence

TURNLOCK does not need to pre-expand or pre-resolve the complete future nested
call tree when accepting a root or parent invocation.

Each later nested invocation occurrence retains its own admission boundary.

Conceptually:

```text
accept A
↓
A later attempts B
↓
admit or reject B

if B is accepted and later attempts C
↓
admit or reject C
```

A parent's acceptance does not pre-authorize descendants.

A parent's acceptance does not guarantee that every later nested invocation will
be admissible.

A later nested rejection therefore does not imply that the parent should
necessarily have been rejected at its earlier admission boundary.

This ADR introduces no progress or termination guarantee.

### Direct behavior of the candidate composition remains constrained

The absence of root-wide future expansion does not permit the workflow
definition currently being admitted to directly violate a restriction that
already applies to the composition.

For example, under the TL-INV-040 restriction:

```text
IA1
↓
attempt B

B directly permits:
main-agent continuation
```

B cannot be accepted when the admitted semantics make that main-agent
continuation reachable and no accepted semantic ordering or exclusion removes
that reachability.

By contrast, if B later attempts another nested workflow C, C receives its own
admission boundary with the still-applicable restrictions.

### Recursive/cyclic calls preserve admission context

ADR-033 permits recursion and cycles.

For example:

```text
A1
↓
B1
↓
A2
```

Every occurrence remains distinct.

Every later nested attempt is checked at its own boundary.

A recursive/cyclic edge MUST NOT create a fresh unrestricted admissibility
context merely because a workflow identity repeats.

### The admitted definition becomes the governing definition

Before accepting an attempted invocation, TURNLOCK may resolve or otherwise
identify the workflow definition that would govern the invocation if accepted
to the extent required to establish admission.

That evaluation does not itself create an accepted invocation.

The required semantic relationship is:

```text
attempt B
↓
definition DB is the definition evaluated for admission
↓
B accepted
↓
governingDefinition(B) = DB
```

TURNLOCK MUST NOT:

```text
evaluate D1 for admission
then accept the same invocation under D2
```

without performing a new admission decision for D2.

If the attempt is rejected:

```text
no accepted B invocation exists
no governing definition is bound for B
```

This rule selects no definition identifier, hash, snapshot, storage mechanism,
workflow-reference syntax, resolution algorithm, or locking mechanism.

### Pre-acceptance rejection creates no callee lifecycle

When a nested invocation is rejected before acceptance:

```text
no accepted callee invocation exists
no callee lifetime exists
no callee governing definition is bound
no callee call/return episode exists
no normal callee completion occurs
```

The caller remains the immediate calling context.

Its preserved/local continuation is not consumed by the nonexistent callee.

Suspension for the nested call becomes effective only for an accepted
invocation.

For a main-agent-selected invocation, rejection leaves the same main-agent
region as caller.

For an independent-agent-selected invocation, rejection leaves the same
independent-agent region as caller.

For a workflow-declared invocation, rejection MUST NOT silently enable the
normal successful post-call continuation as though the rejected callee had
completed.

The rejection must remain attributable or observable at the relevant execution
boundary.

This ADR does not select retry, fallback, abort, catch, alternate-callee,
failure-propagation, cancellation, timeout, or user-interaction semantics.

### TL-INV-039 is preserved through nested composition

The same continuing main-agent cognitive lineage MUST NOT obtain unordered
concurrent continuations merely because one occurrence appears inside a nested
workflow.

Declared causal ordering or established mutual exclusion may make repeated uses
compatible.

Scheduler order cannot do so.

### TL-INV-040 is preserved through nested composition

An invocation subtree causally rooted in an independent-agent-selected nested
invocation remains prohibited from reaching the coding session's main-agent
cognitive lineage.

Nested calls, recursion, cycles, conditions, and parallel branches do not reset
that restriction.

The restriction ends only according to TL-INV-040's already-accepted scope.

### No normative effect/capability representation

This ADR defines a semantic admissibility relation.

It does not require the implementation or formal model to encode that relation
as:

```text
effect sets
capability sets
bitmasks
type effects
graph summaries
transitive closure tables
static annotations
runtime tokens
proof objects
```

Any such representation is a later modeling, architecture, implementation, or
conformance choice.

## Invariant consequence

The invariant-admission procedure admits exactly one new stable invariant:

```text
TL-INV-041
Nested-composition admissibility-closure invariant
```

`TL-INV-041` owns the universal requirement that an attempted nested invocation
must not be accepted unless it is independently authorized and preserves every
applicable composition-admissibility restriction.

It also owns:

```text
transitive preservation of restrictions whose scope extends into descendants

fail-closed rejection when required preservation cannot be established

scheduler order not manufacturing admissibility

rejected pre-acceptance attempts creating no callee invocation

the admitted workflow definition matching the definition bound at acceptance
```

Existing invariants retain their specific responsibilities:

```text
TL-INV-024
→ heterogeneous workflow-owned parallel composition

TL-INV-035
→ workflow-declared nested invocation

TL-INV-037
→ stable governing definition per accepted invocation

TL-INV-039
→ same-main-lineage concurrent non-forkability

TL-INV-040
→ IA-selected subtree main-lineage isolation
```

No second new invariant is admitted.

## Formal applicability

`TL-INV-041` is a core safety obligation for the first executable TURNLOCK
state-machine model.

A future model must be able to distinguish:

```text
attempted invocation
accepted invocation
rejected pre-acceptance attempt
```

and must represent enough abstract context to decide whether each modeled nested
invocation transition is admissible.

The model must preserve the distinction:

```text
invocation authority
!=
composition admissibility
```

The model must also preserve enough declared topology to represent, where
relevant:

```text
causal ordering
co-reachability
mutual exclusion
restriction scope
caller context
main-agent lineage identity
IA-selected-subtree provenance
```

The model may abstract these facts.

The model may use:

```text
sets
predicates
relations
finite workflow universes
finite invocation depth
abstract summaries
flags
```

when appropriate.

Those choices are modeling decisions, not TURNLOCK product semantics.

The first model does not need to pre-expand an unbounded recursive call graph.

Later nested invocations may be checked at their own abstract admission
boundaries.

No TLA+ state variable, action, effect representation, capability lattice,
static-analysis algorithm, graph algorithm, theorem prover, scheduler, Rust
representation, DSL representation, or runtime validation strategy is selected
by this ADR.

No successful TLA+/TLC verification is claimed.

## Rationale

TURNLOCK permits reusable nested composition while preserving explicit
workflow-owned orchestration.

That composition is only safe if restrictions established by one semantic layer
cannot be bypassed merely by adding another workflow boundary.

At the same time, requiring root-wide pre-expansion of all possible future
nested calls would conflict with per-invocation definition binding, dynamic
workflow selection, and recursive/cyclic composition.

The accepted design therefore uses a compositional rule:

```text
each invocation has an admission boundary
+
applicable restrictions remain in force across descendants
+
later nested invocations are checked at their own boundaries
+
unknown required compatibility fails closed
```

This gives the formal model a definite invocation-admission contract without
forcing TURNLOCK to adopt a particular effect system or graph-analysis
architecture.

## Alternatives considered

### Check only the direct syntactic step at the caller

Rejected. Nested workflow boundaries could bypass restrictions transitively.

### Reject every nested workflow invocation from a parallel branch

Rejected. Workflow invocation is valid branch-local composition when the
resulting topology preserves applicable restrictions.

### Accept every authorized invocation and rely on descendant checks

Rejected as a universal rule. The candidate composition itself may already
directly violate an applicable restriction.

### Require full root-wide transitive workflow expansion before acceptance

Rejected. Future nested occurrences have their own admission boundaries, and
recursive/dynamic invocation does not require a transitive root snapshot.

### Silently serialize incompatible topology

Rejected. Serialization would manufacture semantic causal ordering absent from
the workflow definition.

### Use runtime first-arrival order as admissibility

Rejected. Scheduler timing is not declared workflow semantics.

### Validate one workflow definition and bind another

Rejected. The admitted composition must correspond to the governing definition
of the accepted invocation.

### Require a particular effect or capability type system

Rejected. The product requires admissibility closure, not a representation.

### Decide retry/fallback/failure policy now

Rejected. Pre-acceptance rejection semantics are sufficient for this Issue;
subsequent failure handling remains separately open.

## Consequences

* Workflow invocation is permitted inside workflow-owned parallel branches when
  independently authorized and composition-admissible.
* Nested workflow invocation is composition rather than a new parallel execution
  form.
* Invocation authority and composition admissibility are independent.
* Every attempted nested invocation receives its own pre-acceptance
  admissibility boundary.
* Applicable restrictions remain closed under nested composition according to
  their own normative scopes.
* Workflow boundaries do not erase restrictions.
* Recursive and cyclic invocation do not reset restrictions.
* Declared causality and established mutual exclusion may establish
  compatibility.
* Runtime scheduling cannot manufacture compatibility.
* When required compatibility cannot be established, the invocation is not
  accepted.
* Parent acceptance does not pre-authorize every future descendant invocation.
* Root acceptance does not require transitive expansion of the future call tree.
* The workflow definition admitted for an invocation is the definition bound as
  governing if acceptance succeeds.
* Rejected pre-acceptance attempts bind no callee governing definition.
* Rejection does not silently become successful post-call continuation.
* `TL-INV-039` and `TL-INV-040` remain specific restrictions consumed by the
  general `TL-INV-041` closure rule.
* No effect system, capability lattice, static analysis, runtime algorithm, or
  implementation representation becomes normative.

## Verification obligation

A conforming realization must be capable of demonstrating:

1. a workflow invocation accepted inside a parallel branch when the resulting
   composition preserves all applicable restrictions;
2. rejection of a nested composition that would create unordered concurrent use
   of one main-agent lineage;
3. acceptance when declared causal ordering makes repeated same-lineage use
   compatible;
4. acceptance when established mutual exclusion makes syntactically repeated
   same-lineage uses non-co-reachable;
5. rejection when required compatibility cannot be established;
6. scheduler order not converting an inadmissible topology into an admissible
   one;
7. preservation of TL-INV-040 across multiple nested workflow boundaries;
8. preservation of TL-INV-040 across recursive/cyclic invocation;
9. a parent invocation accepted without pre-resolving every future nested
   workflow;
10. a later nested invocation rejected at its own boundary while its already
    accepted caller remains the caller;
11. the workflow definition evaluated for successful admission becoming the
    accepted invocation's governing definition;
12. a rejected pre-acceptance attempt binding no callee governing definition;
13. a rejected workflow-declared invocation not silently enabling the normal
    successful post-call continuation; and
14. ordinary structured return remaining unchanged for admitted invocations.

The demonstration MUST NOT require a particular effect system, capability
representation, graph algorithm, static-analysis implementation, theorem prover,
scheduler, runtime token, Rust type, DSL construct, workflow hash, snapshot
mechanism, or failure-handling policy selected by this ADR.

## References

* `docs/specification/turnlock-spec.md`
* `docs/adr/adr-008-allow-nested-workflow-invocation-from-main-agent-regions.md`
* `docs/adr/adr-013-allow-heterogeneous-parallel-fan-out-across-execution-forms.md`
* `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
* `docs/adr/adr-022-allow-workflow-declared-invocation-with-structured-call-return-semantics.md`
* `docs/adr/adr-023-clarify-caller-context-and-continuation-semantics-across-nested-workflow-invocations.md`
* `docs/adr/adr-027-bind-each-accepted-invocation-to-a-stable-governing-workflow-definition.md`
* `docs/adr/adr-032-allow-main-agent-participation-in-workflow-owned-concurrency-without-cognitive-lineage-fork.md`
* `docs/adr/adr-033-permit-recursive-and-cyclic-workflow-invocation-under-ordinary-invocation-semantics.md`
* `docs/adr/adr-034-delegate-nested-workflow-invocation-to-independent-agent-regions-without-main-agent-reachability.md`
* `formal/verification.yaml`
* GitHub Issue #6
