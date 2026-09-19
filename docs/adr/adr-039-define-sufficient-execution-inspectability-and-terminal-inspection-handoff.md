---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Define sufficient execution inspectability and terminal inspection handoff"
id: "ADR-039"
status: "accepted"
date: "2026-09-19"
decision_body_sha256: "82ba343128dfdd1010d9ac2ddb09ff922b3d4fc7eceae5af359316d845f1c878"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-018"
  supersedes: []
  confirms: []
governs:
  - "Semantic sufficiency of execution inspection under TL-INV-033"
  - "Inspectable realized prefixes for TURNLOCK-observed terminal or cessation outcomes"
  - "Realizable terminal inspection handoff and disclosure separation"
---

# ADR-039: Define sufficient execution inspectability and terminal inspection handoff

## Context

ADR-018 and `TL-INV-033` established that completed TURNLOCK workflow
executions must expose enough actual TURNLOCK-visible behavior for a user or
higher-level system to understand and evaluate how the workflow progressed
without reconstructing it from human or agent recollection. ADR-018
intentionally left the exact sufficiency criterion, non-completed outcomes,
availability, retention, access, privacy, and representation mechanisms open.

Issue #13 resolves those boundaries without turning TURNLOCK core into an
evaluator, run-comparison system, replay system, persistence service, or
telemetry product.

Subsequent accepted authority fixes adjacent boundaries:

- ADR-019 and `TL-INV-034` keep evaluation and optimization policy outside
  TURNLOCK core.
- ADR-024, ADR-025, ADR-026, and `TL-INV-036` separately preserve effective
  execution-condition provenance and its realizable semantic-boundary capture
  handoff.
- ADR-027, ADR-028, and `TL-INV-037` bind each accepted invocation to a stable
  governing workflow definition.
- ADR-038 requires TURNLOCK to remain an augmentation layer under native-harness
  convergence: semantically compatible harness-native tracing or inspection
  facilities may be realization assets, but cannot redefine TURNLOCK semantics.

The unresolved question is the weakest mechanism-independent contract that makes
execution inspectability objectively reviewable while preserving only
TURNLOCK-semantic distinctions rather than every physical runtime detail.

## Discovery classification

### Derived clarification — semantic sufficiency

ADR-018 already requires enough actual TURNLOCK-visible behavior to understand
how execution progressed in practice.

Inspection therefore must preserve enough information to determine the realized
TURNLOCK-semantic execution whenever occurrence distinctions, multiplicity,
structural or causal relationships, effective control resolutions, explicitly
exposed boundary values, or defined outcomes are necessary to distinguish
actual progression.

This is `derived-from-existing-authority`. It clarifies `TL-INV-033`; it does
not create a new invariant.

### Derived clarification — lossless semantic compression

`TL-INV-033` requires sufficient execution truth, not one physical event for
every semantic fact.

A fact need not be represented separately when it is unambiguously derivable
from the invocation's governing workflow definition and remaining inspectable
execution truth.

This is `derived-from-existing-authority`. No event schema, identifier,
serialization, or storage model is selected.

### Decision-required, resolved — observed non-success outcomes

ADR-018 expressly limited its decision to completed executions.

The accepted decision is that execution inspectability does not depend on
successful completion.

For every accepted invocation for which TURNLOCK observes normal completion or
another terminal or cessation outcome, the inspection obligation applies to the
progression actually realized.

For a non-success outcome, inspectable truth consists of the realized prefix
plus terminal facts TURNLOCK actually knows.

The realized prefix may be empty when invocation acceptance occurred before any
workflow occurrence.

A rejected attempt before invocation acceptance is not thereby an execution
covered by `TL-INV-033`.

The decision does not require invented terminal facts and does not create a
crash-durable post-mortem guarantee when hard loss prevents TURNLOCK from
observing or exposing a terminal boundary.

This was `decision-required` and is accepted here.

### Decision-required, resolved — realizable terminal inspection handoff

ADR-018 required execution truth to be exposed and inspectable but did not fix
the weakest temporal availability contract.

The accepted universal floor is a realizable terminal inspection handoff.

Required execution truth MUST remain semantically available until it
participates in a terminal-boundary interaction through which an eligible
conforming inspection context could have been established in time to acquire a
semantically sufficient representation without depending on inaccessible
transient internal state, accidental internal timing, later mutable-state
reconstruction, human recollection, or agent recollection.

Actual receiver participation, successful delivery, processing,
acknowledgment, persistence, and retention duration are not required.

After TURNLOCK completes its side of a conforming handoff, `TL-INV-033` alone
does not require continued post-handoff availability, persistence, or retention.

This was `decision-required` and is accepted here.

### Decision-required, resolved — disclosure separation

Underlying execution truth and consumer-visible disclosure are distinct.

Separately governed access or privacy policy MAY expose a more restrictive or
redacted consumer view.

Protection/redaction MUST NOT irreversibly substitute away execution truth
required by `TL-INV-033` before an eligible conforming inspection context can
acquire a semantically sufficient representation through the required handoff.

Known-and-protected truth is not unknown truth. Required truth irreversibly
discarded before satisfying the handoff is lost truth.

No authorization, authentication, ACL, RBAC, encryption, identity,
secret-management, or disclosure mechanism is selected.

This was `decision-required` and is accepted here.

## Decision

`TL-INV-033` remains the single invariant owner.

### Semantic sufficiency

For every invocation in the scope of `TL-INV-033`, inspection MUST preserve
enough actual TURNLOCK-visible execution truth that an eligible inspection
context can faithfully determine the workflow-mediated progression actually
realized.

Conceptually:

```text
inspection truth
+
actual governing workflow definition where relied upon
        ↓
faithful determination of realized TURNLOCK-semantic execution
```

This is semantic sufficiency, not event-catalog completeness.

A representation is insufficient when it loses a TURNLOCK-semantic distinction
or relationship needed to distinguish actually different realized progressions.

A representation MAY omit facts unambiguously derivable from the governing
workflow definition and other inspectable execution truth.

### Workflow-shape-relative distinctions

Where necessary to determine realized progression, inspection MUST preserve
enough information to distinguish:

* occurrences when repeated realizations matter;
* actual multiplicity;
* structural and causal relationships among occurrences;
* effective branch or continuation selection;
* loop continuation and exit;
* runtime-resolved fan-out membership and cardinality;
* nested invocation occurrence, caller/callee relationship, and structured
  return;
* a workflow selected by dynamic nested invocation;
* explicitly exposed boundary inputs and results attributable to their relevant
  occurrences;
* defined outcomes attributable to their relevant occurrences; and
* actually known terminal or cessation facts.

These are semantic categories, not required event types.

Concurrent occurrences not causally ordered by TURNLOCK semantics MUST NOT be
artificially totally ordered merely from scheduler timing.

### Boundary facts

Explicitly exposed boundary inputs, results, and defined outcomes are execution
truth at TURNLOCK's semantic boundary.

They MUST remain attributable to their consuming or producing occurrences when
that attribution is necessary to understand realized progression.

A representation preserving only existence or an irreversible
identity/difference token is not universally sufficient when the explicitly
exposed value itself is needed for inspection or evaluation.

No representation mechanism is selected.

Private chain-of-thought, private reasoning, arbitrary agent-interior activity,
and internal tool calls remain outside the universal minimum unless they become
an explicitly exposed result or another TURNLOCK-visible progression fact.

### Governing-definition correspondence

Inspection MAY rely on an invocation's governing workflow definition to avoid
materializing facts unambiguously derivable from that definition and remaining
inspection truth.

When it does, the inspection context MUST establish correspondence to the
workflow definition that actually governed the invocation.

A later/current mutable workflow artifact MUST NOT substitute as evidence of
historical governing definition or historical execution.

No revision identifier, hash, snapshot, copy, content-addressing scheme,
persistence mechanism, or reference syntax is selected.

ADR-027, ADR-028, and `TL-INV-037` remain authoritative.

### Non-success terminal or cessation outcomes

Successful completion covers realized execution through completion.

A TURNLOCK-observed failure, cancellation, interruption, or other non-success
terminal/cessation outcome covers the realized prefix and terminal facts
TURNLOCK actually knows.

Unrealized workflow regions MUST NOT be represented as executed.

Unknown cause/state MUST NOT become a known failure cause, completion, or other
invented terminal fact.

The realized prefix MAY be empty after invocation acceptance.

A pre-acceptance rejected invocation attempt is outside this obligation unless
another accepted contract independently requires its inspection.

A hard process, machine, or environment loss preventing TURNLOCK from observing
or exposing a terminal boundary does not create crash-recovery or durable
post-mortem evidence semantics.

### Realizable terminal inspection handoff

Required execution truth MUST remain available until a realizable terminal
inspection handoff.

An eligible conforming inspection context must be able to be established in
time to acquire a semantically sufficient representation as part of the
terminal-boundary interaction without inaccessible transient internal state,
accidental timing, later mutable-state reconstruction, human recollection, or
agent recollection.

Mere momentary internal existence is insufficient.

Actual receiver participation, successful delivery, consumer processing,
acknowledgment, persistence, durable buffering, and retention duration are not
required by the universal floor.

When no consumer is attached, conformance requires that the inspection
capability nevertheless be structurally realizable so that an eligible context
could have participated in time.

After TURNLOCK completes its side of the conforming handoff, `TL-INV-033` alone
does not require continued availability, persistence, or retention.

### Access/privacy separation

Underlying semantically sufficient execution truth is distinct from a
consumer-visible disclosure view.

Separately governed policy MAY redact or protect values for a particular
consumer.

A restrictive consumer view does not allow required execution truth to be
irreversibly destroyed before an eligible conforming inspection context can
acquire a semantically sufficient representation through the terminal handoff.

Conceptually:

```text
known and disclosable
!=
known and protected
!=
unknown
!=
lost before satisfying the required handoff
```

No consumer identity, authorization, ACL, RBAC, encryption, redaction,
secret-management, or privacy mechanism is established.

### Harness convergence

ADR-038 remains in force.

Execution inspectability is a TURNLOCK semantic/evidence responsibility, not a
requirement that TURNLOCK own a particular tracing mechanism.

If a harness-native capability faithfully realizes this contract, it MAY be a
candidate realization asset through the appropriate integration/conformance
boundary.

A harness-native mechanism does not become semantic authority and TURNLOCK MUST
NOT reimplement it solely for differentiation.

### Evaluation and provenance remain separate

TURNLOCK exposes execution truth. It does not decide what quality means, which
differences matter to property `P`, whether executions are comparable, which is
superior, or how a workflow should be optimized.

ADR-019 and `TL-INV-034` remain unchanged.

Execution inspectability and effective execution-condition provenance remain
distinct:

```text
TL-INV-033
→ what TURNLOCK-visible execution actually happened?

TL-INV-036
→ under which TURNLOCK-known effective conditions did a scope operate?
```

ADR-024, ADR-025, and ADR-026 remain independently applicable.

## Rationale

The weakest useful inspectability contract is neither "record everything" nor
"emit one event per semantic fact".

It preserves TURNLOCK-semantic distinctions while permitting lossless semantic
compression and excluding irrelevant physical/runtime detail.

This prevents TURNLOCK-known realized variation from becoming opaque solely
because execution truth was discarded.

External evaluation can later interpret captured truth according to its own
property-relative policy without TURNLOCK becoming an evaluator.

Non-success executions remain evidence about the prefix that actually executed.

The terminal inspection handoff is the weakest availability contract making
"inspectable" externally meaningful without making TURNLOCK a persistence or
retention service.

The contract also satisfies ADR-038's Perfect Harness Test: the durable
TURNLOCK responsibility is the harness-independent semantic/evidence contract,
while a conforming native harness mechanism may realize it.

## Alternatives considered

### Universal event catalog

Rejected.

### Final outcome only

Rejected because it cannot preserve non-derivable realized branch, iteration,
fan-out, nested-invocation, boundary-result, or causal distinctions.

### Record every physical runtime detail

Rejected because it would create false semantic distinctions from scheduler or
implementation behavior.

### Successful completions only

Rejected because non-success executions may contain meaningful realized-prefix
evidence.

### Mandatory persistent execution record

Rejected. The terminal handoff is the universal floor.

### Universal raw-value disclosure

Rejected. Consumer disclosure may be restricted independently.

### Crash-durable post-mortem evidence

Rejected as an implication of this decision.

### TURNLOCK-owned tracing solely because current harnesses lack it

Rejected under ADR-038. A conforming harness-native mechanism may realize the
accepted inspection semantics.

## Consequences

* Execution inspectability becomes reviewable through semantic sufficiency.
* Compact representations are permitted when semantics remain recoverable.
* Inaccessible transient state or race-to-observe behavior cannot satisfy
  `TL-INV-033`.
* TURNLOCK-observed non-success outcomes provide inspectable realized-prefix
  evidence.
* Consumer disclosure may be restricted without redefining protected truth as
  unknown or lost.
* TURNLOCK core gains no universal post-handoff persistence/retention duty.
* External evaluation layers may capture execution truth without moving
  evaluation/optimization policy into core.
* Harness-native tracing/inspection capabilities may satisfy the mechanism side
  when semantically conforming.

## Invariant admission

No new invariant identity is admitted.

`TL-INV-033` remains the stable owner and is renamed from:

```text
Completed-execution inspectability invariant
```

to:

```text
Execution-inspectability invariant
```

Semantic-sufficiency details clarify the existing obligation.

Extension to observed non-success outcomes broadens the domain of the same
execution-truth obligation rather than creating another form of inspectability.

The terminal handoff defines when "expose/inspectable" is genuinely satisfied.

Disclosure separation governs preservation of the same required truth.

A second invariant would split one coherent inspectability contract without
independent traceability value.

ADR-039 therefore amends ADR-018's completed-execution-only scope.

## Formal applicability

`TL-INV-033` remains `partial` for core TLA+ formalization and
`not-yet-modeled` for verification.

A future abstraction may distinguish realized progression, occurrence
multiplicity where relevant, structural/causal relationships, control
resolutions, observed non-success prefixes, terminal facts, and impermissible
loss before an abstract terminal inspection handoff.

It may omit semantically redundant facts when derivable from governing
definition plus remaining inspection truth.

It MUST NOT invent concrete events, IDs, serialization, timestamps, storage,
retention, disclosure mechanisms, authorization systems, comparison algorithms,
evaluators, replay engines, or crash-durability mechanisms.

No executable TLA+ model currently exists for this invariant. No checked claim
is made.

## References

* `AGENTS.md`
* `docs/specification/turnlock-spec.md`
* `docs/adr/adr-018-require-completed-workflow-execution-inspectability.md`
* `docs/adr/adr-019-keep-evaluation-and-optimization-policy-outside-turnlock-core.md`
* `docs/adr/adr-024-preserve-effective-execution-condition-provenance.md`
* `docs/adr/adr-025-preserve-condition-specific-provenance-without-requiring-protected-value-disclosure.md`
* `docs/adr/adr-026-define-a-realizable-semantic-boundary-capture-handoff.md`
* `docs/adr/adr-027-bind-each-accepted-invocation-to-a-stable-governing-workflow-definition.md`
* `docs/adr/adr-028-clarify-that-tl-inv-037-forbids-governing-definition-changes-under-current-semantics.md`
* `docs/adr/adr-038-assume-native-harness-workflow-convergence.md`
* `formal/verification.yaml`
* `docs/repository-governance/turnlock-rust-discovery-classification.md`
* GitHub Issue #13
