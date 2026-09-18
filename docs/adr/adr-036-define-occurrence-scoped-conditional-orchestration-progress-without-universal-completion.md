---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Define occurrence-scoped conditional orchestration progress without universal completion"
id: "ADR-036"
status: "accepted"
date: "2026-09-18"
decision_body_sha256: "288e9cad445b806cdf736c21c001907940bd29ed05904747f8ec3fc1120154ea"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-005"
    - "ADR-006"
    - "ADR-008"
    - "ADR-011"
    - "ADR-013"
    - "ADR-014"
    - "ADR-015"
    - "ADR-023"
    - "ADR-033"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Separation of execution-resource completion from TURNLOCK-owned orchestration progress"
  - "Structural control consequences after recognized completion, yield, return, and join satisfaction"
  - "Occurrence-scoped conditional non-starvation of continuously enabled TURNLOCK-owned progression"
  - "Absence of a universal TURNLOCK completion guarantee"
---

# ADR-036: Define occurrence-scoped conditional orchestration progress without universal completion

## Context

TURNLOCK's accepted control semantics define reversible main-agent handoff,
structured workflow invocation/return, immediate-caller restoration, and
workflow-owned fan-out/fan-in.

The formal traceability manifest historically associated several of those
invariants with planned property names containing `Eventually` or otherwise
grouped them under `safety+liveness`.

Those names did not establish product semantics and left three materially
different obligations conflated:

1. whether an execution resource or workflow eventually produces completion;
2. what control-state consequence follows when a completion/yield/return/join
   condition is recognized;
3. whether TURNLOCK may indefinitely starve orchestration progression that is
   already continuously enabled.

Issue #2 resolves that ambiguity.

The distinction must preserve TURNLOCK's role as the orchestration engine
without turning TURNLOCK into a guarantor that arbitrary computation,
agentic work, external dependencies, recursive workflows, or branch sets always
terminate.

## Discovery classification

### Derived from existing authority — completion determines the structural return/continuation consequence

Existing handoff, invocation/return, immediate-caller, and join semantics already
require a determinate control consequence when their applicable completion
condition occurs.

Normal completion does not create an additional product choice about which
caller or continuation is restored.

At the semantic level, once TURNLOCK recognizes the relevant completion/yield
condition, the resulting control consequence is established by that control
transition.

This semantic requirement does not require implementation-level transaction
atomicity or any particular scheduler/runtime mechanism.

### Decision-required, resolved — occurrence-scoped conditional non-starvation

Existing authority did not uniquely decide whether a continuation that remains
eligible may be indefinitely ignored by TURNLOCK's own scheduling.

The accepted decision is:

```text
for each TURNLOCK-owned progression occurrence P:

if P is eligible,
and P remains continuously eligible,
and P remains applicable under the governing workflow semantics,

TURNLOCK must not indefinitely fail to advance P
solely because TURNLOCK's own scheduling keeps selecting other progression
```

Progress by another occurrence does not satisfy this obligation.

This is a product-level conditional liveness guarantee.

### Scope clarification — no universal completion guarantee

TURNLOCK does not universally guarantee that every started execution region,
workflow invocation, parallel branch, branch set, or workflow eventually
completes.

In particular, the conditional liveness obligation does not assert that the
completion/yield/result condition which enables later orchestration progression
will eventually occur.

This preserves the existing absence of universal completion guarantees for
bounded cognition and recursive/cyclic workflow execution and applies the same
boundary consistently to the affected handoff, invocation, return, and join
semantics.

### Formal-modeling choice — occurrence representation and fairness encoding

The representation of an occurrence and the TLA+ fairness mechanism used to
encode this product obligation are formal-modeling choices.

ADR-036 does not select weak fairness, strong fairness, a scheduler algorithm,
an occurrence identifier, a state-variable representation, or a parameterized
action shape.

Issue #3 owns that formal representation.

Issue #1 owns the property-level verification/evidence metamodel.

## Decision

TURNLOCK separates execution-resource completion from TURNLOCK-owned
orchestration progress.

### 1. No universal work-completion promise

TURNLOCK does not promise that every execution resource, region, invocation,
branch set, or workflow eventually reaches normal completion.

A product or workflow primitive may acquire stronger semantics through a
separate accepted decision, but no such universal guarantee is introduced here.

### 2. Recognized completion has an immediate semantic control consequence

When TURNLOCK recognizes a completion/yield/return-ready/join-satisfied
condition whose governing workflow semantics determines a control consequence,
the semantic state resulting from that control transition MUST already reflect
that consequence.

Examples include:

```text
main-agent region completes/yields
→ declared workflow continuation becomes eligible

workflow-declared callee normally completes
→ correct caller relationship is restored
→ preserved post-call continuation becomes eligible

agent-selected callee normally completes
→ same immediate caller agent region resumes

declared join requirements become satisfied
→ declared post-join continuation becomes eligible
```

This is semantic transition structure, not a requirement that one implementation
operation perform all internal work atomically.

### 3. Continuously enabled TURNLOCK-owned progression is not starved

For every particular TURNLOCK-owned progression occurrence, if that occurrence
is eligible, remains continuously eligible, and remains applicable under the
governing workflow semantics, TURNLOCK MUST NOT indefinitely fail to advance
that occurrence solely because its own scheduling selects other progression.

### 4. The obligation is occurrence-scoped

Progress of another invocation, caller continuation, branch, join, or workflow
does not discharge the progress obligation of the continuously enabled
occurrence.

### 5. The obligation ends if applicability legitimately ends

If governing workflow semantics make an occurrence no longer eligible or no
longer applicable, the conditional progress obligation no longer applies to
that occurrence from that point.

This decision does not define cancellation, timeout, failure, race, preemption,
or invalidation semantics.

### 6. External or agentic completion is not converted into engine liveness

TURNLOCK's conditional progress obligation begins only after the relevant
TURNLOCK-owned progression is enabled.

It does not require a main agent, independent agent, raw LLM operation,
mechanical/external operation, nested workflow, parallel branch, or recursive
workflow to eventually produce the trigger that would enable that progression.

### 7. Formal fairness and runtime scheduling mechanisms remain unspecified

This decision does not select weak fairness, strong fairness, FIFO, round-robin,
priority scheduling, work stealing, timing bounds, retries, watchdogs, runtime
IDs, UUIDs, counters, tokens, handles, threads, processes, or any equivalent
formal or implementation mechanism.

## Invariant admission

The occurrence-scoped conditional non-starvation guarantee is a distinct
universal temporal obligation and is not independently owned by the existing
local handoff, invocation/return, immediate-caller, or fan-out/fan-in
invariants.

Therefore a new stable invariant is admitted:

```text
TL-INV-042 — Conditional orchestration-progress invariant
```

`TL-INV-004`, `TL-INV-008`, `TL-INV-018`, and `TL-INV-027` retain their existing
identities and are reclassified to remove the previously conflated liveness
meaning.

No other new invariant is introduced.

## Formal-traceability consequence

The existing planned names:

```text
InvocationEventuallyReturnsUnderFairness
CorrectCallerEventuallyResumesUnderFairness
JoinEventuallyReleasesUnderFairness
```

are removed because they can be read as promising universal completion of their
triggering work.

`HandoffCanResume` is retained only as a capability/reachability obligation.

No replacement TLA+ property identifier is invented before an executable model
contains it.

`TL-INV-042` is recorded as planned/not-yet-modeled with no TLA+ property,
state-variable, action, configuration, occurrence representation, or fairness
formula selected yet.

## Consequences

* TURNLOCK remains responsible for executing workflow-owned orchestration.
* TURNLOCK cannot satisfy the contract while indefinitely starving one
  continuously enabled, still-applicable progression occurrence through its own
  scheduling.
* TURNLOCK does not become responsible for guaranteeing termination of arbitrary
  computation, agentic work, external dependencies, recursive workflows, or
  parallel branch sets.
* Normal completion determines the appropriate return/eligibility consequence
  structurally rather than creating an additional scheduling decision about
  what the continuation should be.
* Formal occurrence scope and fairness encoding remain downstream modeling
  responsibilities.
* No runtime scheduling algorithm or identity mechanism becomes product
  semantics.

## Non-goals

This decision does not define:

* universal workflow termination;
* universal region or branch completion;
* cancellation;
* failure propagation;
* timeout behavior;
* retry behavior;
* preemption;
* recovery;
* a scheduler algorithm;
* scheduler priority;
* weak or strong fairness formulas;
* runtime occurrence identifiers;
* UUIDs, counters, tokens, or handles;
* Rust types;
* process or thread topology;
* persistence;
* TLA+ state variables or actions;
* a concrete completion/yield protocol for the main agent.
