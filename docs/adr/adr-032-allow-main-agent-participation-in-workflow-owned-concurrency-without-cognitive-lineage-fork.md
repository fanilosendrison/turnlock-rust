---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Allow main-agent participation in workflow-owned concurrency without cognitive-lineage fork"
id: "ADR-032"
status: "accepted"
date: "2026-09-18"
decision_body_sha256: "dcbabc1dae021c88ac7b4648fe4ce8abb0560aed513db24365ccc5a6a414bae4"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-007"
    - "ADR-008"
    - "ADR-013"
    - "ADR-014"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Main-agent participation in workflow-owned concurrent topology"
  - "Non-forkability of the continuing main-agent cognitive lineage across unordered concurrent continuations"
  - "Branch-local main-agent handoff under workflow-owned parallel execution"
---

# ADR-032: Allow main-agent participation in workflow-owned concurrency without cognitive-lineage fork

## Context

ADR-013 accepted heterogeneous workflow-owned parallel fan-out/fan-in across mechanical execution, bounded raw-LLM inference, and independent-agent execution, but explicitly left main-agent continuation in a concurrent branch unresolved.

ADR-007 establishes that a main-agent continuation preserves the continuing cognitive lineage of the surrounding coding-agent session rather than creating a fresh or reconstructed agent. ADR-014 requires declared global orchestration to remain workflow-owned rather than being manufactured by runtime scheduling or agent judgment.

The unresolved question is therefore not merely whether a main-agent region may execute while unrelated work also progresses. The product must define whether main-agent continuation may participate in workflow-owned concurrent topology while preserving the fact that one continuing main-agent cognitive lineage is not an independently forkable execution resource.

The relevant semantic distinction is between:

```text
one main-agent continuation
coexisting with independent sibling work
```

and:

```text
the same continuing main-agent cognitive lineage
forked into multiple unordered concurrent continuations
```

Runtime timing cannot define that distinction because scheduler order is an execution accident rather than declared workflow causality.

GitHub Issue #22 records the product-owner decision from which this ADR is derived.

## Discovery classification

### B — main-agent continuation in workflow-owned concurrency

ADR-013 deliberately left main-agent participation in a concurrent branch unresolved.

The product decision is:

```text
A main-agent continuation MAY participate
as a branch of workflow-owned concurrent execution.
```

This is new product authority.

### A — non-forkability of one continuing main-agent cognitive lineage

Once concurrent main-agent participation is accepted, ADR-007's cognitive-lineage semantics require:

```text
one continuing main-agent cognitive lineage
MUST NOT be forked or duplicated across
independently concurrent, non-causally-ordered continuations
```

### A — scheduler order is not semantic causal order

ADR-014 requires orchestration to remain declared by workflow semantics.

Therefore:

```text
runtime scheduling order
MUST NOT manufacture semantic causal ordering
that the declared workflow does not provide
```

### A — a concurrent main-agent handoff is branch-local

A main-agent continuation reached within one declared concurrent branch suspends only that branch's calling continuation.

It does not implicitly suspend unrelated sibling branches that remain enabled by the declared workflow topology.

## Decision

TURNLOCK permits main-agent continuation as a participant in workflow-owned concurrent execution.

A declared parallel region may therefore contain, subject to the rules below:

```text
mechanical execution
raw LLM inference
independent-agent execution
main-agent continuation
```

A main-agent concurrent branch remains continuation of the existing session main-agent cognitive lineage. TURNLOCK MUST NOT silently realize it as a fresh independent agent, a reconstructed child agent, or another cognitive lineage.

### Branch-local handoff

When a concurrent branch reaches a main-agent continuation, the handoff is local to that branch's calling continuation.

Conceptually:

```text
parallel
├── mechanical ------------------------>
├── raw LLM --------------------------->
├── independent agent ----------------->
└── main-agent continuation ----------->

join
↓
declared continuation
```

The main-agent handoff does not implicitly pause or suspend independently enabled sibling branches.

Completion of the main-agent branch also does not itself complete the enclosing parallel region or release the join. The workflow's declared join semantics remain authoritative.

### One continuing main-agent lineage is non-forkable

An admitted TURNLOCK topology MUST NOT permit the same continuing main-agent cognitive lineage to continue through two independently concurrent, non-causally-ordered continuations.

Therefore this topology is inadmissible for one main-agent lineage:

```text
parallel
├── main-agent M/A
└── main-agent M/B
```

when the declared orchestration establishes neither:

```text
M/A before M/B
```

nor:

```text
M/B before M/A
```

and does not otherwise establish mutual exclusion.

The prohibition concerns declared causal structure, not wall-clock overlap.

### Runtime scheduling does not create semantic ordering

A topology does not become admissible merely because one execution happens to schedule or complete one main-agent use before another main-agent use reaches the resource.

For example:

```text
parallel
├── main-agent M/A
└── mechanical
      ↓
      main-agent M/B
```

is not rendered valid by an execution in which `M/A` happens to finish before `M/B` is reached.

TURNLOCK MUST NOT interpret accidental runtime order as declared workflow order.

### No hidden serialization

TURNLOCK MUST NOT repair unordered concurrent uses of the same main-agent lineage by silently serializing them.

Such serialization would manufacture an observable cognitive causal order that the workflow did not declare and would therefore change workflow meaning.

TURNLOCK likewise MUST NOT repair the conflict by:

```text
choosing first arrival
cloning or duplicating the main-agent lineage
substituting an independent agent
changing one execution form into another
inventing an undeclared order
```

### Declared causal order permits repeated main-agent use

The number of main-agent continuation occurrences is not itself restricted.

Repeated use is valid when the workflow declares the relevant causal order.

For example:

```text
main-agent M/A
↓
main-agent M/B
```

is valid.

Likewise:

```text
parallel
├── main-agent M/A
└── mechanical
join
↓
main-agent M/B
```

is valid because the declared join establishes an ordering boundary before the later main-agent continuation.

### Established mutual exclusion permits multiple syntactic uses

Multiple syntactic occurrences of the same main-agent lineage may exist in concurrent topology when declared workflow semantics establish that the uses cannot become unordered concurrent continuations.

For example:

```text
parallel
├── if X:
│     main-agent M/A
└── if !X:
      main-agent M/B
```

may be admissible when the applicable declared semantics establish mutual exclusion.

The normative rule is not:

```text
one main-agent occurrence per parallel region
```

The normative rule concerns unordered co-reachability of the same continuing cognitive lineage.

This ADR selects no representation, proof system, static analysis, solver, graph algorithm, effect system, or other mechanism for establishing mutual exclusion or causal ordering.

### Fail closed when compatibility cannot be established

If a topology potentially exposes the same continuing main-agent lineage to unordered concurrent continuations and the required declared ordering or mutual exclusion cannot be established, that topology or invocation MUST NOT be admitted under full TURNLOCK semantics.

TURNLOCK MUST NOT change workflow meaning in order to make the topology executable.

### Structured nested continuation is not a concurrent fork

Structured nested main-agent use remains valid.

For example:

```text
main-agent region A
↓
invoke workflow B
  ↓
  main-agent region B
  ↓
return to main-agent region A
```

uses structured suspension and immediate-caller return.

The outer main-agent continuation is suspended while the nested invocation executes and later resumes according to the accepted nested-call semantics.

That is sequential continuation of one cognitive lineage through structured call/return, not two independently concurrent continuations of that lineage.

## Invariant consequence

The invariant-admission test admits a new stable invariant identity.

`TL-INV-014` already owns preservation of main-agent cognitive lineage across a handoff.

`TL-INV-024` owns heterogeneous parallel composition.

`TL-INV-027` owns workflow-owned parallel fan-out/fan-in.

`TL-INV-030` owns the requirement that global control transitions remain workflow-authorized.

None of those existing invariant identities independently states the universal prohibition against exposing the same continuing main-agent cognitive lineage to unordered concurrent continuations.

The new obligation therefore receives:

```text
TL-INV-039
Main-agent concurrent-lineage non-forkability invariant
```

`TL-INV-039` does not replace or broaden `TL-INV-014`. It owns the concurrency-specific non-forkability obligation.

## Formal applicability

The concurrency-specific non-forkability obligation is a core safety property suitable for future formalization.

The current repository contains no executable TLA+ model for this obligation, so:

```text
formalization: planned
verification: not-yet-modeled
```

The intended future model must distinguish declared causal structure from runtime scheduler order well enough to prevent unordered concurrent continuations of one main-agent lineage.

It may abstract established mutual exclusion.

It MUST NOT turn a particular static-analysis algorithm, solver, scheduler, lock, token, or proof representation into normative product semantics.

No successful TLA+/TLC verification is claimed by this ADR.

## Rationale

TURNLOCK benefits from allowing the user's continuing main agent to participate in a parallel region while independent work continues elsewhere. For example, mechanical work or independent-agent investigation need not stop merely because one branch currently requires the main agent.

At the same time, the main agent is not a stateless interchangeable worker. Its value is continuation of one session-specific cognitive lineage.

Allowing the same lineage to fork into unordered concurrent continuations would either require multiple divergent cognitive histories or force the runtime to invent an ordering that the workflow did not declare.

The accepted semantics therefore combine:

```text
main-agent participation in workflow-owned concurrency
+
branch-local handoff
+
one non-forkable continuing main-agent lineage
+
workflow-declared causal order
```

## Alternatives considered

### Forbid main-agent continuation in all parallel regions

Rejected. A single main-agent continuation can coexist coherently with independent sibling work without transferring global orchestration authority to the main agent.

### Allow arbitrary concurrent forks of the same main-agent lineage

Rejected. It contradicts the cognitive-lineage continuity that distinguishes main-agent continuation from independent agents.

### Silently serialize conflicting main-agent branches

Rejected. Serialization would introduce cognitive causal ordering absent from the declared workflow topology.

### Use runtime first-arrival order

Rejected. Scheduler timing is not workflow semantics.

### Clone or reconstruct the main agent for each branch

Rejected. A clone or reconstructed agent is a distinct cognitive lineage unless a separate capability establishes equivalent continuation semantics; it cannot silently stand in for the same continuing main agent.

### Permit only one syntactic main-agent occurrence per parallel region

Rejected. Declared causal ordering or established mutual exclusion may make multiple syntactic occurrences semantically compatible.

### Require a particular mutual-exclusion proof mechanism

Rejected. The product requires the semantic property, not a specific implementation or analysis technique.

## Consequences

* Main-agent continuation becomes an accepted branch type in heterogeneous workflow-owned parallel composition.
* Main-agent handoff inside one concurrent branch is branch-local.
* Independently enabled sibling branches are not implicitly suspended by that handoff.
* Main-agent branch completion does not itself satisfy the enclosing join.
* One continuing main-agent cognitive lineage cannot occupy unordered concurrent continuations.
* Multiple main-agent uses remain valid when declared causal ordering or established mutual exclusion makes them compatible.
* Runtime scheduler order cannot manufacture the required ordering.
* Potentially conflicting topology fails closed when compatibility cannot be established.
* Structured nested suspension/return remains valid and is not classified as a concurrent lineage fork.
* The mechanism used to establish causal ordering, co-reachability, or mutual exclusion remains an architecture, modeling, implementation, or conformance choice rather than normative product semantics.

## Verification obligation

A conforming realization must demonstrate at least:

1. a declared parallel region containing one main-agent continuation alongside independently progressing sibling work;
2. that reaching the main-agent continuation does not implicitly suspend unrelated siblings;
3. that completion of the main-agent branch does not release the join while required sibling work remains incomplete;
4. rejection of a topology exposing the same main-agent lineage to two unordered concurrent continuations;
5. rejection does not become acceptance merely because one concrete runtime schedule would serialize those uses;
6. repeated main-agent use after an explicit causal boundary remains permitted;
7. multiple syntactic uses may remain permitted when declared mutual exclusion is established; and
8. structured nested suspension/return remains distinguishable from a concurrent fork.

The demonstration must not depend on a particular scheduler, lock, ownership token, effect system, graph-analysis algorithm, static theorem prover, Rust representation, DSL syntax, process model, or harness-specific implementation.

## References

* `docs/specification/turnlock-spec.md`
* `docs/adr/adr-007-preserve-main-agent-cognitive-lineage-and-ordinary-interactive-agency.md`
* `docs/adr/adr-008-allow-nested-workflow-invocation-from-main-agent-regions.md`
* `docs/adr/adr-013-allow-heterogeneous-parallel-fan-out-across-execution-forms.md`
* `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
* `formal/verification.yaml`
* GitHub Issue #22
