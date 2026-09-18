---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Require eventual advance of continuously enabled orchestration progress"
id: "ADR-037"
status: "accepted"
date: "2026-09-18"
decision_body_sha256: "3f7951b14ff89506679e6908c571aa6962ef23236218084376f324fcf76d71a1"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-036"
  supersedes: []
  confirms: []
governs:
  - "Unqualified eventual advance of continuously enabled and applicable TURNLOCK-owned progression"
  - "Removal of competing-progress or scheduling-cause as a precondition of TL-INV-042"
  - "Non-conformance of indefinite engine inaction while eligible progression remains applicable"
---

# ADR-037: Require eventual advance of continuously enabled orchestration progress

## Context

ADR-036 established `TL-INV-042` as TURNLOCK's occurrence-scoped conditional
orchestration-progress invariant.

The intended product distinction was:

```text
execution-resource completion
is not universally guaranteed

but

once a TURNLOCK-owned progression occurrence
is continuously eligible and applicable,
TURNLOCK must eventually advance that occurrence
```

ADR-036 correctly rejected universal completion guarantees and correctly made
the progress obligation occurrence-scoped.

However, one part of its accepted wording stated that TURNLOCK must not
indefinitely fail to advance an eligible occurrence:

```text
solely because TURNLOCK's own scheduling
keeps selecting other progression
```

That causal qualification is too narrow.

It leaves open a behavior in which the occurrence remains continuously eligible
and applicable forever while TURNLOCK advances no competing occurrence and
simply leaves the occurrence unadvanced forever.

That behavior does not satisfy the intended orchestration-engine progress
contract.

This ADR amends ADR-036 only at that boundary.

## Discovery classification

### Decision-required, resolved — remove the causal qualification from conditional progress

ADR-036's accepted wording does not uniquely prohibit indefinite inactivity when
no competing progression is selected.

The accepted corrected decision is:

```text
for every particular TURNLOCK-owned progression occurrence P:

if P is eligible,
and P remains continuously eligible,
and P remains applicable under the governing workflow semantics,

TURNLOCK MUST eventually advance P
```

The obligation does not depend on why progression has not yet occurred.

In particular:

```text
P continuously eligible and applicable
+
other occurrences repeatedly progress
+
P never progresses
```

is non-conforming.

And:

```text
P continuously eligible and applicable
+
TURNLOCK performs no competing progression
+
P never progresses
```

is also non-conforming.

No competing occurrence, scheduler preference, or other causal explanation is a
premise of the liveness obligation.

### Preserved scope — no universal completion guarantee

This amendment does not require the event, agent, external operation, workflow,
branch, or other execution resource that would create an eligible continuation
to eventually complete.

The obligation begins only after the applicable TURNLOCK-owned progression
occurrence is eligible.

It therefore does not convert TURNLOCK into a universal termination guarantee.

### Preserved scope — applicability may cease

The obligation applies while the particular occurrence remains continuously
eligible and applicable.

If governing workflow semantics legitimately make that occurrence no longer
eligible or applicable before it advances, this ADR introduces no independent
requirement that the occurrence still execute.

This ADR does not define the semantics that might cause eligibility or
applicability to cease.

### Preserved scope — no crash, failure, or durability semantics

This amendment does not define failure, cancellation, timeout, retry,
preemption, crash recovery, durability, persistence, process lifetime, machine
failure, or resource-exhaustion semantics.

It does not define whether or how an occurrence remains eligible across such an
event.

Those questions remain governed separately or intentionally unspecified.

### Formal-modeling choice remains downstream

This amendment does not select a TLA+ occurrence representation or a fairness
formula.

Issue #3 remains responsible for representing the accepted semantic obligation
in the formal model.

Issue #1 remains responsible for the property-level verification/evidence
metamodel.

## Decision

ADR-036 is amended as follows.

For every particular TURNLOCK-owned progression occurrence:

```text
eligible
AND continuously remains eligible
AND continuously remains applicable under the governing workflow semantics
```

TURNLOCK MUST eventually advance that same occurrence.

The obligation is occurrence-scoped.

Progress of another occurrence does not discharge it.

No competing progression is required for the obligation to exist.

No causal classification of the delay is required.

A behavior in which the occurrence remains continuously eligible and applicable
indefinitely but is never advanced is non-conforming, including a behavior in
which TURNLOCK performs no other progression.

The causal qualifier from ADR-036:

```text
solely because TURNLOCK's own scheduling
continues to select other progression
```

does not govern the corrected product contract.

The corrected obligation is:

```text
continuously eligible and applicable
→ eventual advance of that occurrence
```

## Invariant consequence

No new invariant identity is introduced.

`TL-INV-042 — Conditional orchestration-progress invariant` remains the stable
invariant identity.

Its normative meaning is amended to require eventual advance of each particular
TURNLOCK-owned progression occurrence that remains continuously eligible and
applicable.

`TL-INV-042` remains a liveness invariant.

No change is made to the identity or classification of:

```text
TL-INV-004
TL-INV-008
TL-INV-018
TL-INV-027
```

## Formal-traceability consequence

`formal/verification.yaml` must add ADR-037 as governing authority for
`TL-INV-042`.

The manifest must state explicitly that:

```text
continuously enabled and applicable occurrence
→ eventual advance of that occurrence
```

and that no competing progress or scheduler-choice premise is required.

No TLA+ property identifier, action, state variable, occurrence identity,
fairness formula, or TLC configuration is introduced by this ADR.

## Consequences

* TURNLOCK cannot conform by indefinitely leaving continuously eligible and
  applicable orchestration progression unadvanced.
* The obligation applies whether TURNLOCK is progressing other work or no other
  work.
* Conformance does not require determining why an occurrence was delayed.
* Execution-resource completion remains distinct from engine progress.
* Universal workflow, region, invocation, or branch termination remains
  unguaranteed.
* Occurrence representation and fairness encoding remain downstream formal
  modeling choices.
* No scheduler implementation becomes product semantics.

## Non-goals

This amendment does not define:

* universal work completion;
* workflow termination guarantees;
* main-agent termination;
* independent-agent termination;
* raw-LLM termination;
* mechanical/external-operation termination;
* branch termination;
* failure;
* cancellation;
* timeout;
* retry;
* preemption;
* crash recovery;
* durability;
* persistence;
* process or machine failure;
* scheduler algorithms;
* scheduler priorities;
* runtime occurrence identifiers;
* weak fairness;
* strong fairness;
* TLA+ actions;
* TLA+ state variables;
* TLA+ property identifiers;
* TLC configurations.
