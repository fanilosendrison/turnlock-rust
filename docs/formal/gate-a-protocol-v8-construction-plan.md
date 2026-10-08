---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "construction-plan"
domain: "turnlock-rust-formal-assurance"
severity: "strict"
name: "Gate A protocol v8 construction plan"
---

# Gate A protocol v8 construction plan

## Status and authority

This document is a non-authoritative construction map for the Gate A hostile-review protocol-v8 evolution required by ADR-056.

It does not define TURNLOCK product semantics, Gate A semantic subject `S`, hostile-review protocol semantics, semantic-question meaning, qualification meaning, formal semantics, implementation behavior, or live engineering work state.

The governing authority remains:

```text
docs/specification/turnlock-spec.md
accepted ADRs
formal/verification.yaml
immutable hostile-review protocol/evidence artifacts under formal/reviews/
accepted NIB-S / NIB-M / Dependency Contracts during construction
```

In particular:

```text
ADR-055
```

remains accepted authority for the structured adjudication and resolution semantics introduced by published protocol v7.

```text
ADR-056
```

is accepted authority for:

```text
protocol-v8 semantic-question identity
QLEK construction semantics
global single-admission authority
cross-run/cross-root semantic-fact reuse
semantic-fact / provenance separation
candidate-revision nominal binding
anti-model-shopping dispatch fencing
protocol-v7 permanent inactivity
protocol-v8 activation boundary
```

This plan must not reinterpret either ADR.

GitHub Issues, native GitHub relationships, and Turnlock-Rust Engineering Project fields own live work existence, dependency, lifecycle state, scheduling, and priority.

This plan records only the stable construction sequence.

## Current immutable baseline

At publication of this plan:

```text
current hostile-review protocol:
    gate-a-campaign-protocol-v6

published protocol lineage:
    v1 → v2 → v3 → v4 → v5 → v6 → v7

protocol v7:
    published
    immutable
    mechanically validated
    permanently inactive
    never current

protocol v8:
    not yet published
    not current
```

`formal/verification.yaml` MUST remain bound to exact protocol v6 until the explicit protocol-v8 activation transition defined by ADR-056.

No construction work described here may make protocol v7 current.

No intermediate protocol-v8 artifact becomes current merely because it exists or mechanically validates.

## Objective

Construct the complete protocol-v8 semantic, evidence, validation, runner-construction, and formal-assurance closure required by ADR-056 so that one exact semantic question:

```text
SemanticQuestionContractRevision
+
ExactLogicalInput
→ QLEK
```

has at most one authoritative semantic admission across one coherent Authoritative History domain, while:

```text
execution provenance
evidence-root placement
model/provider realization
run identity
```

remain orthogonal to semantic-question identity.

The completed system must support:

```text
cross-run semantic reuse
cross-root semantic reuse
candidate-independent reuse
fresh candidate-bound qualification
crash-safe anti-resampling
exact recovery of possibly-dispatched semantic executions
exact semantic-fact dependency resolution
historical provenance auditability
```

without weakening any accepted ADR-055 adjudication or challenge semantics.

## Non-goals

This construction MUST NOT:

```text
change TURNLOCK product semantics
change Gate A semantic subject S
activate protocol v7
reinterpret protocol-v1 through protocol-v7 evidence
introduce a generic problem-solving IR
introduce a SCOPE IR
invent cross-protocol semantic equivalence
invent generic legacy cognitive-result import
replace existing runner module boundaries
create a third authoritative post-review evidence root
make evidence-root ownership semantic authority
make model/provider/prompt identity part of QLEK
deduplicate distinct CandidateRevision identities by byte equality
```

No protocol-v8 implementation begins until the relevant construction authority is closed.

## Existing module architecture remains

Protocol v8 MUST fit the existing runner module architecture:

```text
M0 contracts
M1 orchestrator
M2 campaign-state
M3 campaign-authority
M4 cognitive-execution
M5 assurance-ledger
M6 mechanical-validation
M7 repository-control
M8 recovery-operator
```

ADR-056 does not authorize a new semantic module or a parallel state engine.

The protocol-v8 construction must instead refine the existing responsibilities.

### M0 — contracts

M0 will eventually own the exact cross-module representations selected by the synchronized NIB-S for concepts including:

```text
SemanticQuestionContractRevision identity
LogicalQuestionDescriptor
QLEK
SemanticAdmission identity/reference
SemanticFact identity/reference
qualification identity/reference
QLEK-bound execution authority/fencing references
candidate-view bindings
```

M0 owns representation and runtime validation only.

It does not decide semantic-question meaning.

### M1 — orchestrator

M1 continues to own orchestration.

Protocol-v8 synchronization must make M1 mechanically enforce:

```text
derive required semantic work from accepted authority
resolve/reuse existing exact semantic facts/admissions first
never dispatch an admitted QLEK
obtain exact QLEK execution authority before dispatch
perform fresh candidate/currentness revalidation where required
resume recovery before authorizing replacement semantic work
```

M1 does not choose semantic equivalence.

### M2 — campaign-state

M2 remains the sole authoritative state writer.

Protocol v8 requires M2 construction to close a second concurrency dimension in addition to per-`GateARun` write ownership:

```text
GateARun write authority
≠
QLEK semantic-execution/admission authority
```

M2 must ultimately preserve:

```text
global single-assignment Admission(K)=V
exact origin-evidence binding
QLEK-bound durable pre-dispatch authority
fencing against stale semantic executors
crash-safe reconstruction
semantic-admission conflict detection
```

within the coherent Authoritative History domain.

### M3 — campaign-authority

M3 retains its existing authority over exact current:

```text
S
P
campaign currentness
reviewer/profile prerequisites
```

Protocol v8 MUST NOT move resolution semantics or semantic-fact qualification into M3.

M3 supplies exact authority inputs required downstream.

### M4 — cognitive-execution

M4 remains the cognitive execution boundary.

Protocol-v8 synchronization must bind an exact semantic Execution to:

```text
QLEK
Execution identity
exact admission-authority/fencing generation
exact packet/prompt realization
```

before provider dispatch.

M4 does not decide whether two questions are semantically equal.

M4 does not discard an already obtained protocol-valid result because the originating candidate later becomes stale.

### M5 — assurance-ledger

M5 remains the primary owner of protocol-derived semantic work and qualification.

Its synchronized responsibilities must include the accepted protocol-v8 semantics for:

```text
required semantic-question derivation
exact contract/input binding
semantic-fact consumption
cross-run/cross-root reuse
qualification closure
challenge requirements
bounded revision progression
candidate-bound resolution progression
semantic predecessor requirements
```

M5 must consume exact facts/admissions rather than root-owned predecessor receipts as semantic authority.

### M6 — mechanical-validation

M6 remains the runner's mechanical validation boundary over the repository's accepted validation authority.

Protocol-v8 construction must provide mechanical validation for at least:

```text
LogicalQuestionDescriptor construction
QLEK recomputation
candidate-view integrity
packet/output structural validity
semantic-admission evidence binding
FactId reconstruction
qualification reduction inputs
protocol-v8 bundle/evidence validity
```

M6 does not invent semantic equivalence.

### M7 — repository-control

M7 remains the repository-fact and materialization authority.

Where a protocol-v8 candidate-bound question requires `CandidateView`, the construction must obtain the exact view from the exact sealed `CandidateRevision` materialization under an explicit coverage specification.

M7 does not decide whether the view is semantically sufficient.

### M8 — recovery-operator

M8 retains execution uncertainty/recovery classification.

Protocol-v8 synchronization must ensure that one unresolved QLEK-bound Execution that may have been dispatched prevents an unsafe replacement semantic execution.

Absence of an admission is not proof of non-execution.

`PROVEN-NOT-EXECUTED` and other exact accepted replacement-safe dispositions remain the only authority for the corresponding replacement paths.

## Stable construction sequence

The protocol-v8 construction sequence is:

```text
C0  construction-plan publication
 ↓
C1  semantic-question contract closure
 ↓
C2  semantic identity algebra closure
 ↓
C3  SemanticAdmission authority and execution-fencing closure
 ↓
C4  semantic-fact and qualification closure
 ↓
C5  candidate-bound identity/view closure
 ↓
C6  protocol-v8 packet/evidence projection closure
 ↓
C7  inactive protocol-v8 artifact + checker construction
 ↓
C8  NIB-S synchronization
 ↓
C9  NIB-M / Dependency Contract synchronization
 ↓
C10 NIB-T + formal-assurance closure
 ↓
C11 hostile construction-pack review
 ↓
C12 RED
 ↓
C13 GREEN / integration
 ↓
C14 inactive protocol-v8 qualification
 ↓
C15 explicit activation transition
```

A later stage may expose a material ambiguity in an earlier stage.

If that happens:

```text
STOP
→ classify the discovery
→ return to the earliest unresolved authoritative cause
```

No downstream construction step may invent the missing meaning.

---

## C0 — Publish this construction plan

Deliverables:

```text
this document
docs/formal/README.md link to this document
```

No protocol artifact changes occur in C0.

No NIB changes occur in C0.

No live protocol currentness changes occur in C0.

Completion condition:

```text
ADR-056 is accepted
AND
this stable construction sequence is published
AND
protocol v6 remains current
```

## C1–C6 authority boundary

C1-C6 are architect-owned pre-publication design closure.

They may mechanically derive only what is uniquely determined by ADR-055,
ADR-056, and existing accepted authority.

If closing C1-C6 requires choosing between materially different protocol
meanings:

```text
STOP
→ classify the discovery as decision-required
→ obtain an accepted ADR
→ resume from the earliest affected construction stage
```

Construction choices that do not create protocol meaning may be closed in
C1-C6 and materialized later.

The complete authoritative protocol-v8 artifact representation is published
only at C7. Before that publication, a C1-C6 design closure is a construction
input, not independent hostile-review protocol authority. An accepted ADR
required to resolve a material choice remains the authority for that choice.

---

## C1 — Close the SemanticQuestionContract catalog

The C1 construction closure is documented in
[`gate-a-protocol-v8-semantic-question-contract-catalog.md`](gate-a-protocol-v8-semantic-question-contract-catalog.md).

Before any protocol-v8 packet schema or QLEK serialization is designed, define the exact immutable semantic-question contracts for every protocol-v8 semantic family.

The catalog must cover at least:

```text
MaterialityAssessmentInitial
MaterialityAssessmentRevision

RefutationInitial
RefutationRevision

DiscoveryClassificationInitial
DiscoveryNoNormativeImpactRevision
DiscoveryDecisionRequiredRevision

UniqueCorrectionInitial
UniqueCorrectionRevision

RealizationScopeInitial
RealizationScopeRevision

RepairRealizationInitial
RepairRealizationRevision

MaterialityChallenge
RefutationChallenge
UniqueCorrectionChallenge
RealizationScopeChallenge
RepairRealizationChallenge
NoNormativeImpactChallenge
DecisionNecessityChallenge
```

For every contract revision, close exactly:

```text
contract identity

typed input domain

input identity mode for every dependency

semantic output domain

semantic value equality/canonicalization

semantic answer obligation/relation

applicable qualification contract

whether structured negative output is legal

whether one same-family successor revision exists

exact challenge family if applicable
```

The catalog must explicitly instantiate ADR-056's accepted `FA` and `SM` projections.

It must not derive semantic input identity from protocol-v7 packet shape.

Completion gate `G-C1`:

```text
every semantic producer/revision/challenge used by P8
has one exact immutable contract definition

AND

no contract contains an unresolved semantic identity decision
```

No schema serialization is selected merely to make this gate easier.

---

## C2 — Close semantic identity algebra

The C2 construction closure is documented in
[`gate-a-protocol-v8-semantic-identity-algebra.md`](gate-a-protocol-v8-semantic-identity-algebra.md).

Using the C1 contracts, define exact construction rules for:

```text
LogicalQuestionDescriptor
QLEK
SemanticAdmissionId
PredicateRevisionId
FactId
QualificationKey
```

Close:

```text
canonical byte/value semantics

domain separation

collision-safe framing

typed exact logical inputs

authority-reference semantics

semantic-value-reference semantics

semantic-fact-reference semantics
```

The construction must mechanically preserve:

```text
same exact semantic question
→ same QLEK

different exact semantic question
→ different QLEK

different execution provenance only
→ same QLEK

different nominal CandidateRevision for candidate-bound contract
→ different QLEK
```

This stage also closes exact requirement-slot-to-QLEK binding semantics where needed by M5 orchestration.

Requirement-slot identity MUST remain distinct from QLEK identity.

Completion gate `G-C2`:

```text
a conforming implementation can compute every P8 QLEK
without reading model/provider/run/root identity unless its exact contract
declares that value semantic
```

---

## C3 — Close SemanticAdmission authority and execution fencing

The C3 construction closure is documented in
[`gate-a-protocol-v8-semantic-admission-authority-execution-fencing.md`](gate-a-protocol-v8-semantic-admission-authority-execution-fencing.md).

Define the exact authoritative state semantics required for:

```text
Admission : QLEK ⇀ SemanticCandidate
```

and the operational authority required before semantic dispatch.

This stage must close:

```text
coherent Authoritative History admission namespace

single-assignment admission mutation

origin execution/evidence binding

admission conflict semantics

QLEK execution-authorization identity

fencing generation/token semantics

acquire/check/recheck algorithm

durable Arm binding before possible provider dispatch

replacement-safety conditions

crash/restart reconstruction

late-response handling

protocol-valid completion → mandatory admission reconciliation

no dispatch after admission
```

The design MUST preserve the distinction:

```text
durable SemanticAdmission
≠
live execution coordination
```

while ensuring live coordination failure cannot erase durable evidence that one semantic execution may already have occurred.

This stage must reuse the accepted M2/M4/M8 execution lifecycle wherever possible.

It must not create a second independent recovery system.

Completion gate `G-C3`:

```text
two runners cannot lawfully produce competing semantic samples for one K

AND

crash at every pre-dispatch/post-dispatch boundary has an exact recovery rule

AND

absence of Admission(K) alone never authorizes unsafe redispatch
```

---

## C4 — Close SemanticFact and qualification resolution

The C4 construction closure is documented in
[`gate-a-protocol-v8-semantic-fact-qualification-resolution.md`](gate-a-protocol-v8-semantic-fact-qualification-resolution.md).

Define the exact protocol-v8 semantic fact substrate needed by downstream questions.

At minimum close:

```text
ground fact identity
predicate revision identity
fact canonical arguments
qualified semantic fact construction
qualification-key construction
qualification reducer semantics
cross-root/cross-run fact resolution
primitive versus derived fact boundary
```

Required derived facts include those needed to express ADR-055/056 concepts such as:

```text
qualified positive materiality
refutation exhaustion without qualified refutation
accepted UniqueCorrection
accepted RealizationScope
accepted RepairRealization
UniqueCorrection exhaustion branches
DecisionNecessity candidate basis
```

Receipts MUST remain provenance for primitive semantic admissions.

They MUST NOT become semantic fact identity.

Do not introduce persisted status records where deterministic closure already derives the state.

Completion gate `G-C4`:

```text
every semantic predecessor required by a C1 contract
is representable as one exact typed fact

AND

that fact can be mechanically reconstructed without same-root receipt ownership
```

---

## C5 — Close candidate-bound identity and CandidateView construction

The C5 construction closure is documented in
[`gate-a-protocol-v8-candidate-bound-identity-candidate-view.md`](gate-a-protocol-v8-candidate-bound-identity-candidate-view.md).

Define the exact protocol-v8 construction contract relating:

```text
CandidateRevisionId
CoverageSpec
CandidateView
```

The design must mechanically establish:

```text
CandidateViewOf(C, coverage, V)
```

from the exact immutable sealed materialization of `C`.

Close at least:

```text
complete-view construction for RealizationScope

readable-path-scoped view construction for RepairRealization

canonical path ordering

exact entry/state/byte identity

candidate-view validation

current-candidate pre-dispatch revalidation

same-candidate requirement for candidate-bound closure revision

stale-after-dispatch admission preservation

no cross-candidate RepairIntent retargeting
```

Required anti-cheat case:

```text
C17 != C18
CandidateView(C17) == CandidateView(C18)

⇒
QLEK_RS(C17) != QLEK_RS(C18)
```

Completion gate `G-C5`:

```text
no candidate-bound question can obtain or inherit physical authority
without naming one exact CandidateRevision
```

---

## C6 — Close protocol-v8 packet, receipt, and evidence projections

The C6 construction closure is documented in
[`gate-a-protocol-v8-packet-receipt-evidence-projections.md`](gate-a-protocol-v8-packet-receipt-evidence-projections.md).

Only after C1-C5 are closed may protocol-v8 serialization be selected.

Determine exactly which published P7 artifacts can remain unchanged and which require new immutable versions.

The audit must separately classify:

```text
SemanticQuestionContract catalog/registry representation
PredicateRevision / qualification-contract representation
semantic output schemas
adjudication packet schema
challenge packet schema
execution receipt schema
supplement/evidence projection schema
protocol prompts
protocol-bundle meta-schema
review-evidence meta-schema
```

Reuse is permitted only when the exact existing artifact already expresses the required P8 contract without reinterpretation.

Published P7 bytes MUST NOT be edited.

The protocol-v8 execution packet must distinguish:

```text
semantic input
```

from:

```text
execution/evidence provenance
```

A semantic predecessor must be represented by exact semantic admission/fact identity.

A consuming root must not acquire ownership of the predecessor receipt.

If self-contained evidence bindings are included for auditability, they remain provenance and MUST NOT alter QLEK.

The receipt/evidence design must support C3's completion-to-admission completeness proof.

Completion gate `G-C6`:

```text
every P8 semantic dependency has exactly one representation

AND

every provenance edge remains auditable

AND

changing only provenance locator/root ownership cannot change QLEK
```

---

## C7 — Construct the inactive protocol-v8 artifact set and checker support

Publish the concrete immutable protocol-v8 artifact set required by the closed C1-C6 architecture.

At minimum this includes:

```text
formal/reviews/protocols/gate-a-campaign-protocol-v8.json
```

with exact predecessor:

```text
formal/reviews/protocols/gate-a-campaign-protocol-v7.json
```

and every new immutable meta-schema, schema, prompt, semantic-contract,
predicate/qualification-contract, or other protocol artifact actually required
by the closed C1-C6 design.

If C6 determines that the protocol-bundle interpretation structure changes,
publish a new:

```text
formal/reviews/meta-schemas/review-protocol-bundle-v8.schema.json
```

Otherwise, the P8 bundle may bind the exact unchanged historical protocol-bundle
meta-schema whose interpretation structure remains sufficient.

Do not create new versions of unchanged artifacts without cause.

Extend the mechanical review checker with explicit inactive-P8 validation.

The checker must implement the ADR-056 validation layers:

```text
contract/protocol integrity
artifact integrity
QLEK integrity
execution/recovery integrity
SemanticAdmission integrity
completion/admission completeness
SemanticFact soundness
candidate binding
semantic dependency well-foundedness
projection soundness
```

Regression requirements:

```text
P1-P6 historical interpretation unchanged
P7 exact immutable validation unchanged
P7 remains inactive
P8 validates as inactive
P6 remains current
```

Completion gate `G-C7`:

```text
complete immutable P8 artifact set mechanically validates

AND

formal/verification.yaml still selects P6
```

---

## C8 — Synchronize the System Brief

Revise `NIB-S-GATE-A-CAMPAIGN-RUNNER` to consume accepted ADR-056 and the exact inactive-P8 construction contracts.

Do not change the existing M0-M8 module architecture unless a new material architecture discovery is explicitly classified and separately authorized.

NIB-S synchronization must close the system-level ownership of at least:

```text
QLEK identity
SemanticAdmission
SemanticFact consumption
QLEK execution fencing
cross-run reuse
cross-root reuse
candidate-bound QLEK derivation
currentness versus historical admission applicability
completion/admission reconciliation
protocol-v8 inactive/current activation boundary
```

The updated System Brief must remove or amend any P7-era construction statement that treats:

```text
same-root receipt ownership
```

as the semantic dependency universe.

Completion gate `G-C8`:

```text
all P8 semantics have one unambiguous system/module owner

AND

no implementation agent must decide where P8 authority belongs
```

---

## C9 — Synchronize Module Briefs and Dependency Contracts

After NIB-S closure, revise only the NIB-M briefs affected by the actual accepted module responsibility delta.

Expected affected areas include at least:

```text
M0 contracts
M1 orchestrator
M2 campaign-state
M4 cognitive-execution
M5 assurance-ledger
M6 mechanical-validation
M7 candidate/view materialization where required
M8 recovery/reconciliation
```

M3 must be modified only where exact `S/P` authority projection must expose already-owned information to the synchronized protocol.

Do not expand M3 into resolution semantics.

Close exact algorithms, signatures, edge cases, recovery branches, conflict behavior, and mutation admissibility.

Update Dependency Contracts only when the synchronized module design actually requires an external-interface change.

In particular, do not change the Pi dependency contract merely because QLEK exists if QLEK remains runner-owned metadata outside the Pi adapter surface.

Completion gate `G-C9`:

```text
every changed module behavior is fully specified

AND

every non-trivial external dependency behavior is closed

AND

coding agents have no semantic discretion
```

---

## C10 — NIB-T and formal-assurance closure

Write the P8 construction tests only after NIB-S/NIB-M/DC closure.

NIB-T must include observable and anti-cheat tests for at least:

```text
same exact QLEK across different GateARuns reuses one admission

different run/root/provider/model/prompt provenance alone does not create K'

two concurrent requests for one unresolved K cannot both dispatch

crash after durable Arm and before result blocks unsafe replacement

PROVEN-NOT-EXECUTED permits only the exact lawful replacement path

recovered protocol-valid result must become the admission for K

protocol-valid result cannot be omitted and replaced by another sample

admitted K can never dispatch again

same K + same V duplicate provenance deduplicates semantically

same K + different V produces integrity conflict

cross-root accepted UniqueCorrection can feed a later RealizationScope

predecessor receipt ownership is not transferred to the consuming root

candidate-independent work is reused after candidate advance

distinct CandidateRevision values with identical bytes produce fresh RS QLEKs

RS/RR challenge freshness follows producer admission identity

old candidate-bound completion after candidate advance is admitted historically
but cannot satisfy the new candidate target

candidate-bound revision cannot cross CandidateRevision identity

FactRef not reconstructible from authoritative closure fails closed

same exact fact proven by different provenance graphs has one FactId

P7 validation remains unchanged

P8 cannot become current implicitly
```

Formal-assurance work must model at least:

```text
AtMostOneAdmission

NoDispatchAfterAdmission

NoUnsafeConcurrentDispatch

CompletionAdmissionCompleteness

AdmissionEvidenceCompleteness

NoSemanticObservationBeforeAdmission

SemanticFactSoundness

CandidateViewSoundness

NoCandidateRebinding
```

and all additional safety/liveness properties required to make the crash/recovery semantics truthful.

Formal changes MUST preserve integrated Turnlock semantics and traceability discipline.

Completion gate `G-C10`:

```text
RED-ready test contract exists

AND

formal invariants/claims are traceable

AND

no ADR-056 invariant is merely prose without a construction or verification path
```

---

## C11 — Hostile review of the complete P8 construction pack

Before production implementation, hostile-review the complete construction pack:

```text
C1 semantic contracts
C2 identity algebra
C3 admission/fencing design
C4 semantic-fact/qualification design
C5 candidate binding
C6 evidence schemas/projections
C7 inactive P8 artifact/checker contracts
C8 NIB-S
C9 NIB-M/DC
C10 NIB-T/formal plan
```

This is a construction-quality review.

It is NOT a Gate A hostile-review campaign and MUST NOT be recorded as protocol review evidence.

Material discoveries must be classified and routed to the earliest unresolved authority.

No implementation begins while a semantic/protocol ambiguity remains open.

---

## C12 — RED

RED consumes only the accepted NIB-T.

Establish executable failing tests for the missing P8 behavior.

Production code at the end of RED may contain only the minimum scaffolding required for compilation/execution of the failing test suite.

RED is complete only when the P8 tests fail for the intended missing behavior.

---

## C13 — GREEN and integration

GREEN consumes only the closed construction pack.

Implementation proceeds mechanically through the synchronized existing modules.

The implementation agent MUST NOT:

```text
invent QLEK fields
choose fact equivalence
choose candidate identity semantics
choose admission conflict resolution
choose replacement behavior after uncertainty
choose cross-root reuse policy
choose protocol artifact reuse/versioning
```

All such choices must already be closed upstream.

GREEN must preserve protocol v6 as current throughout construction.

---

## C14 — Inactive protocol-v8 qualification

After implementation integration is GREEN:

```text
run complete repository integrity
run complete protocol-v1 through protocol-v8 regression validation
run P8 conformance/checker tests
run required formal verification
run recovery/crash/concurrency tests
run implementation-quality closure
```

Require:

```text
P1-P6 historical interpretation intact

P7 immutable and inactive

P8 complete and mechanically valid

P8 runner construction synchronized

P8 formal obligations satisfied to the required readiness level

formal/verification.yaml still selects P6
```

Any failure returns to the earliest responsible construction layer.

---

## C15 — Explicit protocol-v8 activation

Activation is a separate authorized transition.

Only after C14 closure may a dedicated activation change select the exact immutable protocol-v8 bundle in:

```text
formal/verification.yaml
```

That activation change MUST be small and mechanically auditable.

It MUST NOT simultaneously redesign P8 semantics or construction.

Immediately before activation, require exact verification of:

```text
P8 bundle identity
P8 predecessor == exact immutable P7
all referenced artifact hashes
complete checker support
complete runner synchronization
accepted NIB construction
required formal assurance
P7 permanent inactivity
P6 previous-current identity
```

After activation:

```text
P8 becomes current
P7 remains never-current immutable history
P6 becomes historical protocol authority
```

Activation does not itself create reviewer profiles or fabricate a real Gate A campaign.

## Work-graph policy

This document owns only the stable dependency sequence.

GitHub owns live execution state.

The architecture/construction work graph may mirror C1-C11 when useful, but issue state MUST NOT be duplicated here.

Implementation GREEN issue decomposition is derived only after NIB-M closure.

A coding agent MUST NOT choose implementation issue boundaries before the accepted construction architecture does.

## Construction invariants

The entire protocol-v8 effort is governed by these construction-level invariants:

```text
P8-CI-01
P6 remains current until explicit C15 activation.

P8-CI-02
P7 remains immutable and permanently inactive.

P8-CI-03
No published P1-P7 artifact is edited to implement P8.

P8-CI-04
Semantic identity is closed before execution/evidence serialization.

P8-CI-05
QLEK identity never derives from arbitrary packet bytes.

P8-CI-06
Admission uniqueness is enforced before semantic dispatch, not only at commit.

P8-CI-07
Possibly-dispatched semantic execution cannot disappear across crash.

P8-CI-08
Semantic predecessor authority is FactId/Admission-based, not root ownership.

P8-CI-09
Provenance remains fully auditable without becoming semantic identity.

P8-CI-10
CandidateRevision nominal identity and CandidateView extensional identity remain distinct.

P8-CI-11
Candidate-independent reuse and candidate-bound freshness emerge from QLEK dependencies.

P8-CI-12
Protocol artifacts are versioned only when their exact contract changes.

P8-CI-13
No implementation agent resolves semantic/protocol ambiguity.

P8-CI-14
P8 activation is a separate transition after complete inactive qualification.
```

## Completion boundary

Protocol-v8 construction is complete only when:

```text
all C1-C14 gates are closed

all ADR-056 required-follow-up items except activation are satisfied

all synchronized NIB/DC/NIB-T construction is complete

the runner implements the accepted P8 semantics

P8 validation and formal assurance pass

P1-P7 regression validation passes

P7 remains permanently inactive

P6 is still current
```

Only then may C15 begin.

The protocol-v8 construction plan itself is complete when this document is published and linked from the formal construction documentation.

It creates no protocol identity and activates no runtime behavior.
