---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Define global semantic-question identity and single-admission resolution evidence"
id: "ADR-056"
status: "accepted"
date: "2026-10-06"
decision_body_sha256: "ede8ed439aa8ba9c457b19084b125ca49f56369fbd0754ec4550d15fa794fb09"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-049"
  amends:
    - "ADR-045"
    - "ADR-046"
    - "ADR-055"
  supersedes: []
  confirms:
    - "ADR-047"
    - "ADR-048"
    - "ADR-053"
    - "ADR-054"
governs:
  - "Gate A protocol-v8 semantic-question identity"
  - "Gate A global single-admission cognitive-result authority"
  - "Gate A cross-run and cross-root semantic-result reuse"
  - "Gate A semantic-fact versus evidence-provenance separation"
  - "Gate A candidate-bound resolution identity and freshness"
  - "Gate A semantic-execution anti-model-shopping fencing"
  - "Gate A protocol-v7 non-activation and protocol-v8 activation lineage"
---

# ADR-056: Define global semantic-question identity and single-admission resolution evidence

## Context

ADR-055 closes the structured Gate A adjudication and resolution-qualification protocol sufficiently to define:

- exact post-review finding adjudication subjects;
- surviving-material resolution subjects;
- structured materiality, refutation, discovery, UniqueCorrection, RealizationScope, and RepairRealization outputs;
- exact hostile challenge families and objective sets;
- deterministic supporting-role acquisition;
- bounded same-family closure revision;
- candidate-independent semantic correction;
- candidate-bound physical realization;
- append-only `FindingAdjudicationSupplementV1` overlays for immutable findings.

Protocol v7 is the immutable published protocol snapshot produced by that decision.

Protocol v7 has not been selected by `formal/verification.yaml` and has never become the current Gate A hostile-review protocol. Protocol v6 remains current.

Construction analysis before protocol-v7 activation exposes one remaining protocol-architecture defect.

Protocol v7 identifies one supporting logical cognitive execution by the exact pair:

```text
role
+
input.packet content identity
```

and constrains every semantic predecessor receipt to belong to the same lawful post-review supporting-evidence root and finding lineage.

This is sufficient for a closed adjudication lineage whose semantic cognition and physical realization all occur under one evidence root.

It is not sufficient for append-only resolution continuation after a candidate advance.

ADR-055 simultaneously requires:

```text
a qualified UniqueCorrection is semantic and not candidate-bound

AND

an old candidate-bound RealizationScope does not transfer to a new candidate

AND

a new current candidate requires fresh candidate-bound
RealizationScope qualification before new repair synthesis
```

Suppose one exact finding has already reached:

```text
qualified semantic UniqueCorrection
+
surviving-material adjudication
```

under exact semantic subject `S` and exact protocol `P`.

If the physical candidate later advances while `(S, P)` and the exact adjudication basis remain unchanged, the semantic UniqueCorrection remains applicable but a fresh candidate-bound RealizationScope and RepairRealization are required.

Under protocol v7, the prior UniqueCorrection receipt remains owned by its immutable evidence root.

A later resolution execution cannot consume that exact semantic result without either:

1. making the old receipt belong to another evidence root;
2. reopening or replacing an immutable root;
3. creating an additional same-key adjudication supplement;
4. re-executing semantic work that should have been reused;
5. introducing a new continuation evidence-root class solely to recover ownership of later receipts.

The first three violate accepted append-only evidence ownership.

The fourth permits semantic-result resampling and weakens reproducibility.

The fifth repairs one concrete ownership case but leaves semantic identity dependent on evidence-root topology.

The underlying defect is therefore not the absence of a third evidence root.

The defect is that protocol v7 conflates:

```text
semantic-question identity
```

with:

```text
execution/provenance packet identity
```

and conflates:

```text
semantic dependency
```

with:

```text
same-root receipt ownership
```

The protocol must separate those concepts before structured adjudication is activated.

No protocol-v7 campaign or supplement instance requires migration because protocol v7 has never been current.

## Discovery classification

```text
decision-required at the Gate A hostile-review assurance/protocol
architecture layer;

resolved by this ADR;

no TURNLOCK product-semantic change;

no Gate A semantic subject S change.
```

## Decision

### 1. Protocol v8 is the next structured-adjudication protocol

The next Gate A hostile-review protocol evolution is:

```text
gate-a-campaign-protocol-v8
```

Its exact predecessor is the already published immutable:

```text
gate-a-campaign-protocol-v7
```

Protocol v8 therefore extends the append-only publication lineage:

```text
v1
→ v2
→ v3
→ v4
→ v5
→ v6
→ v7
→ v8
```

Protocol publication lineage and protocol currentness history are distinct.

Protocol v7 MUST remain inactive.

Protocol v7 MUST NOT subsequently be selected as the current Gate A hostile-review protocol.

Protocol v8 MAY become current directly after protocol v6 once all synchronization and activation requirements in this ADR are satisfied.

Until that explicit activation occurs:

```text
gate-a-campaign-protocol-v6
```

remains current.

Published protocol-v1 through protocol-v7 artifacts, schemas, meta-schemas, prompts, predecessor bindings, and immutable referenced bytes remain unchanged.

### 2. Execution identity and semantic-question identity are distinct

Protocol v8 MUST distinguish:

```text
execution/provenance identity
```

from:

```text
logical semantic-question identity
```

An execution identity records how one cognitive execution was physically realized and audited.

It may include:

```text
GateARunId
ReviewCampaignId
ExecutionId
attempt IDs
call IDs
reviewer profile
provider
model
model version
prompt
execution packet
receipt
timestamps
retry history
evidence-root projection
artifact locators
```

A logical semantic-question identity contains only:

```text
one exact immutable SemanticQuestionContractRevision

+

one exact typed semantic-input closure
```

whose lawful variation may change the semantic question or the set of semantically correct answers.

Protocol v8 uses the term:

```text
QLEK
```

for the canonical logical-question key.

`QLEK` is NOT an execution identity.

Conceptually:

```text
LogicalQuestionDescriptorV1 {
    semanticQuestionContract:
        SemanticQuestionContractRevisionId

    exactLogicalInput:
        canonical typed semantic input
}
```

and:

```text
QLEK =
H(
    "turnlock.logical-question.v1",
    canonical(LogicalQuestionDescriptorV1)
)
```

The exact collision-safe framing and public serialization belong to protocol-v8 construction.

They MUST preserve this meaning.

### 3. Semantic-question contracts are harness-independent

One immutable `SemanticQuestionContractRevision` defines one class of semantic questions independently of any harness realization.

It MUST establish at least:

```text
typed input domain

input identity semantics

semantic output domain

semantic answer obligation/relation

semantic value identity/canonicalization
```

It MUST NOT obtain semantic identity from:

```text
prompt identity
provider
model
model version
reviewer profile
runtime implementation
retry attempt
execution receipt
evidence-root ownership
repository locator
timestamp
latency
token count
cost
```

Changing only those execution-realization properties does not create another QLEK.

If a prompt or realization change actually changes what constitutes a correct answer, the change requires a new `SemanticQuestionContractRevision`; it MUST NOT be represented as a mere prompt substitution for the same QLEK.

### 4. Exact logical inputs are typed authoritative dependencies

A semantic-question contract MUST determine the exact semantic role and identity mode of each input.

Protocol-v8 construction MUST distinguish at least conceptually between:

```text
exact authoritative identity

canonical semantic value

qualified semantic fact
```

A binding rule supplies exact values for those declared roles.

The binding rule MUST NOT redefine their identity semantics.

For any candidate dependency `X`, protocol-v8 construction MUST apply the following completeness/minimality criterion:

```text
holding the contract and every other dependency fixed,
could changing X make a different output lawfully correct?
```

If yes, the applicable exact identity of `X` MUST be committed directly or transitively by the logical input.

If no, `X` MUST NOT affect QLEK identity.

Binding MUST be deterministic.

For one exact protocol state and one exact required question slot, binding MUST result in:

```text
exactly one LogicalQuestionDescriptor
```

or one deterministic non-bindable disposition.

More than one lawful descriptor for one exact requirement is a protocol ambiguity/integrity failure.

A runner MUST NOT choose between them.

### 5. Provenance-only values do not create new QLEKs

Protocol-v8 QLEK construction MUST exclude provenance-only dimensions.

In particular, where they do not independently alter the semantic question:

```text
GateARunId
adjudicating ReviewCampaignId
execution receipt identity
raw-output locator
evidence-root identity
prompt ArtifactRef
provider/model identity
repository projection path
timestamps
attempt identifiers
```

MUST NOT create another QLEK.

A source finding's historical semantic identity is not equivalent to execution provenance.

The exact finding being resolved remains semantic input through the exact source-finding identity and canonical substantive finding value required by the applicable contract.

### 6. Review packets remain exact execution projections, not QLEKs

Canonical Gate A review packets and protocol-v8 cognitive execution packets remain exact immutable execution inputs.

They MAY contain more provenance and self-contained evidence material than the logical semantic descriptor.

Their complete artifact SHA MUST NOT be used as QLEK merely because the packet is content-addressed.

Protocol-v8 native construction MUST proceed conceptually in this order:

```text
authoritative Turnlock state
↓
deterministic semantic binding
↓
LogicalQuestionDescriptor
↓
QLEK
↓
global admission lookup
↓
execution/provenance packet when execution is required
```

It MUST NOT derive semantic identity by taking an arbitrary execution packet and deleting a heuristic set of provenance fields.

### 7. Initial semantic-question families

Protocol-v8 construction MUST preserve the structured semantic families accepted by ADR-055.

For protocol v8, `FA` and `SM` are normative semantic projections.

They do not imply standalone persisted artifacts.

#### Finding-adjudication basis `FA`

`FA` is the exact semantic authority closure for adjudicating one historical finding under the current semantic-question/protocol authority.

It MUST commit, directly or transitively:

```text
exact current semantic subject S

exact current protocol identity P and exact semantic-question authority
required by the applicable contract

exact controlling review-authority closure exposed to that question

exact source-finding semantic identity:
    source ReviewCampaignId
    source FindingId
    substantiveFindingSha256

exact canonical substantive finding value
```

For the protocol-v8 initial families defined by this ADR, exact current protocol identity `P` is part of that semantic authority closure.

The controlling review-authority closure MUST bind the exact authority/value content required by the semantic-question contract.

The review packet `ArtifactRef`, review-packet repository path, or complete review-packet artifact SHA MUST NOT substitute for the authority/value closure merely because protocol-v7 execution packets carried that projection.

The following are provenance-only for the protocol-v8 initial families defined by this ADR and MUST NOT affect `FA` merely because protocol-v7 subjects, packets, or evidence carried them:

```text
GateARunId

adjudicating ReviewCampaignId

execution-root or evidence-root ownership

execution receipt identity

raw-output identity or locator

artifact/storage locator

provenance.kind

sourceProtocolBundle when it denotes only the historical protocol
under which the source finding was produced
```

If a later accepted `SemanticQuestionContractRevision` classifies one of those values as semantic input, that later contract MUST state the exact dependency explicitly.

Protocol-v8 construction MUST NOT infer such a dependency from protocol-v7 packet shape, receipt ownership, or provenance.

#### Surviving-material basis `SM`

`SM` is the exact semantic basis for post-adjudication resolution of one finding that remains surviving-material.

It MUST commit, directly or transitively:

```text
exact FA

exact qualified-positive-materiality semantic fact

exact refutation-exhaustion-without-qualified-refutation semantic fact
```

The materiality and refutation-exhaustion components are semantic facts.

Their origin execution receipts, raw-output locators, evidence-root owners, or supplement-local receipt membership MUST NOT define `SM`.

Two evidence/provenance graphs that establish the same exact qualified-positive-materiality fact and the same exact refutation-exhaustion-without-qualified-refutation fact under the same exact `FA` yield the same `SM`.

For an exact finding-adjudication basis `FA`, an exact surviving-material basis `SM`, and exact qualified predecessor facts, initial questions are conceptually bound as follows.

#### Materiality

```text
MaterialityAssessmentInitial:
    FA
```

#### Refutation

```text
RefutationInitial:
    FA
    exact positive-materiality semantic fact
```

#### Discovery classification

```text
DiscoveryClassificationInitial:
    SM
```

#### UniqueCorrection

```text
UniqueCorrectionInitial:
    SM
    exact Discovery semantic admission/result
    exact targeted classification fact
```

The discovery result supplied by protocol v8 MUST preserve at least the semantic information protocol v7 supplied to the UniqueCorrection role.

Protocol v8 MUST NOT silently reduce that input to a smaller semantic projection unless an accepted later authority proves the reduction sufficient.

#### RealizationScope

```text
RealizationScopeInitial:
    SM
    exact accepted UniqueCorrection fact
    exact CandidateRevisionId
    exact complete CandidateView of that CandidateRevision
```

#### RepairRealization

```text
RepairRealizationInitial:
    SM
    exact accepted UniqueCorrection fact
    exact accepted RealizationScope fact
    exact CandidateRevisionId
    exact scoped CandidateView of that CandidateRevision
```

Candidate-independent versus candidate-bound behavior MUST arise from these exact input dependencies.

The runner MUST NOT carry a separate hidden semantic rule saying which task names must be rerun after candidate change.

### 8. Semantic closure revision is a distinct question

A bounded same-family revision is NOT a retry of the original QLEK.

It is a new semantic question.

Where ADR-055 permits one closure revision, protocol v8 MUST use an immutable revision-specific semantic-question contract whose exact logical input additionally binds:

```text
exact prior positive candidate/admission

+

exact prior hostile-challenge semantic result/objections
```

The revision MUST remain in the same semantic family.

No revision may change branch merely to obtain a successful outcome.

The accepted maximum closure revision count remains:

```text
1
```

A positive revised candidate requires one fresh exact challenge.

`not-established` remains a lawful durable semantic result where ADR-055 permits it.

### 9. Challenges consume semantic admissions, not producer receipts

A protocol-v8 challenge is a distinct semantic question.

Its logical input MUST identify the exact challenged semantic candidate through the exact producer `SemanticAdmissionId` or an equivalent canonical fact identity that commits the producer QLEK and candidate value.

Conceptually:

```text
ChallengeQLEK =
H(
    exact ChallengeContractRevision,
    exact challenged SemanticAdmission
)
```

The applicable challenge contract revision owns:

```text
challenge family
challenge kind
required ordered objective set
challenger role
same-family revision authorization
permitted withdrawal result
```

Those properties are contract semantics, not per-run logical inputs.

A challenge MUST NOT depend semantically on which provider/model produced the challenged candidate.

A challenge MUST NOT use the producer receipt as the semantic identity of the challenged result.

The receipt remains origin evidence for that producer admission.

### 10. DecisionNecessity remains positive qualification

The ADR-055 decision-necessity semantics remain unchanged.

A decision-necessity challenge MUST consume exact semantic facts representing:

```text
exact surviving-material basis

exact decision-required discovery hypothesis

exact UniqueCorrection exhaustion fact

exact deterministically derived decision-necessity candidate
```

UniqueCorrection exhaustion remains one of the protocol-defined exact branches corresponding to:

```text
initial not-established

revision not-established

revised candidate whose fresh challenge retains objections
```

The exhaustion fact MUST be derivable from exact semantic admissions/challenges.

It MUST NOT be identified merely by an arbitrary list of receipt locators.

### 11. SemanticAdmission is globally single-assignment within one coherent Authoritative History domain

For every exact QLEK `K`, protocol v8 defines a partial immutable binding:

```text
Admission : QLEK ⇀ SemanticCandidate
```

For one exact QLEK:

```text
zero
OR
exactly one
```

semantic candidate may be admitted.

Conceptually:

```text
SemanticAdmission(K, V)
```

means:

```text
V is the unique protocol-admitted semantic candidate
for exact logical question K.
```

Its semantic identity MUST bind:

```text
K
+
canonical semantic candidate V
```

Conceptually:

```text
SemanticAdmissionId =
H(
    "turnlock.semantic-admission.v1",
    K,
    canonical(V)
)
```

Execution/provenance identity MUST NOT become part of `SemanticAdmissionId`.

### 12. Protocol-valid negative results consume their QLEK

Where an exact question contract permits a structured negative result such as:

```text
not-established
```

that result is a semantic candidate.

It is not absence of evidence.

If it is the first protocol-valid completed semantic candidate for QLEK `K`, then:

```text
Admission(K) = not-established
```

and `K` MUST NOT later be re-executed merely to obtain a different semantic result.

### 13. Admission and qualification are distinct

A protocol-valid structured candidate is not thereby semantically correct.

Admission answers:

```text
what one semantic candidate did this exact question produce?
```

Qualification answers:

```text
under the exact applicable qualification authority,
may that candidate be used for progression?
```

Protocol-v8 construction MUST preserve this distinction.

Qualification is identified by an exact qualification key conceptually binding:

```text
exact QualificationContractRevision

exact SemanticAdmissionId

exact additional qualification inputs, if any
```

The applicable qualification procedure MAY include:

```text
deterministic predicates/checkers

existing normative authority

formal results

operator authority

semantic challenges that themselves obey the
same single-admission rule
```

An accepted/rejected qualification disposition SHOULD remain mechanically derived when all required leaves are already durably available.

Protocol v8 MUST NOT create a redundant mutable qualification-status source of truth merely for convenience.

### 14. Rejection never reopens the original QLEK

If one exact candidate `V` admitted for `K` is later rejected under its exact qualification contract:

```text
RejectedUnder(K, V, Q, witness)
```

the original QLEK remains permanently consumed.

The protocol MUST NOT:

```text
retry K with feedback

ask another model for K

change prompt/model after seeing the rejected result

generate sibling candidate answers for K
```

Any lawful automatic semantic continuation after rejection MUST be represented as a new, explicitly authorized successor semantic question whose logical input commits:

```text
the predecessor admission

the exact rejection fact/witness

the exact authority required by the successor contract
```

### 15. Semantic admission is global across a coherent Authoritative History domain

Single-admission authority MUST NOT be scoped by:

```text
GateARunId
ReviewCampaignId
finding evidence root
repository path
provider
model
```

All runs that may observe or reuse the same Turnlock semantic admissions within one coherent Authoritative History domain MUST consult one logically shared QLEK admission namespace.

The exact physical storage architecture belongs to construction.

The QLEK itself MUST NOT include storage/domain identity merely to avoid collisions.

Two physically disconnected authority domains may independently admit candidates for the same QLEK because they cannot coordinate.

When such domains are reconciled:

```text
same QLEK + same semantic candidate
→ one semantic admission with possibly multiple provenance witnesses

same QLEK + different semantic candidates
→ semantic admission integrity conflict
```

No automatic winner selection is permitted.

### 16. Single-assignment at commit time is not sufficient

A uniqueness constraint applied only when `SemanticAdmission` is written does not satisfy this ADR.

Protocol v8 MUST prevent two semantic trajectories for the same unresolved QLEK from being dispatched concurrently or serially as alternative candidate searches.

Before any semantic provider/model dispatch for exact `K`, the execution MUST hold an exclusive fenced authorization for that QLEK.

Conceptually:

```text
AdmissionAuthority(K, generation)
```

is operational coordination authority.

It is not a semantic fact.

For one exact `K`, at most one live authorization may be capable of producing an admission.

### 17. Semantic execution is bound to durable execution history before dispatch

The live exclusion primitive MAY use implementation-specific coordination.

However, semantic-dispatch history MUST be durably recoverable before a provider/model call can become semantically possible.

Protocol-v8 construction MUST bind every semantic execution to:

```text
exact QLEK
exact execution identity
exact admission-authority generation/fence
```

before dispatch.

A crash after the call may have been sent MUST NOT permit the runner to behave as if no semantic execution existed.

The existing Turnlock execution/recovery architecture remains authoritative for:

```text
Arm before dispatch

MAYBE-SENT uncertainty

same-Execution no-replay

recovery

PROVEN-NOT-EXECUTED replacement safety
```

Protocol-v8 construction MUST integrate QLEK admission fencing with that lifecycle rather than bypass it.

### 18. Replacement is legal only when no competing semantic result can still emerge

If an earlier exact QLEK-bound Execution is unresolved and may have been dispatched, another semantic execution for the same QLEK MUST NOT be armed.

A replacement may become lawful only when the prior execution state establishes an exact disposition that makes semantic duplication impossible.

`PROVEN-NOT-EXECUTED` is one such disposition.

A timeout, process death, missing heartbeat, lost response, or lack of an admission is not by itself proof that a semantic execution did not occur.

### 19. Every protocol-valid semantic completion must reconcile with admission history

Protocol-v8 conformance MUST validate both directions:

```text
SemanticAdmission
→ exact lawful origin evidence exists
```

and:

```text
exact protocol-valid semantic completion
→ corresponding SemanticAdmission exists or must be established
```

A conforming runner MUST NOT:

```text
receive a protocol-valid candidate

omit/discard it

then dispatch the same QLEK again
```

merely because the first candidate was undesirable, stale for current progression, or not yet committed when a process failed.

All completed responses remain sealed exactly as required by accepted retry/evidence authority.

### 20. Admission precedes semantic consumption

No semantic consumer may use a newly produced candidate as semantic input before the candidate is authoritatively bound to its QLEK.

Conceptually:

```text
raw completion
↓
deterministic protocol/structural validation
↓
exact semantic candidate V
↓
durable Admission(K,V)
↓
semantic consumers / qualification
```

The execution receipt and exact raw evidence MUST be durably available as origin evidence before or atomically with authoritative admission.

Unreferenced CAS blobs caused by a failed authoritative commit remain non-authoritative garbage.

A protocol-valid completion that is known to exist MUST NOT become disposable garbage merely because the final admission mutation has not yet completed.

### 21. Semantic facts are distinct from evidence provenance

A semantic downstream dependency is identified by an exact semantic fact, not by ownership of the predecessor receipt.

Conceptually, a ground semantic fact has immutable identity:

```text
FactId =
H(
    exact PredicateRevisionId,
    canonical exact arguments
)
```

For example, an accepted UniqueCorrection is represented conceptually by an exact fact such as:

```text
AcceptedUnder(
    exact UniqueCorrection SemanticAdmission,
    exact QualificationContractRevision
)
```

A downstream RealizationScope consumes that exact qualified fact.

It does not consume:

```text
"some UniqueCorrection receipt in my current evidence root"
```

### 22. Semantic facts may be derived rather than persisted

A fact need not have a dedicated file merely because it is normatively meaningful.

If a fact is mechanically reconstructible from:

```text
primitive durable authoritative commitments
+
exact protocol rules
```

it MAY remain a derived fact.

A packet MAY carry a self-contained canonical projection of that fact for execution.

That projection does not become an independent source of truth.

A referenced fact is valid only if the checker can reconstruct it exactly from authoritative primitive commitments.

An unresolvable claimed fact is an integrity failure.

### 23. Evidence provenance remains complete and immutable

Native model-produced `SemanticAdmission`s MUST remain backed by exact immutable origin execution evidence.

For one native admission, the checker MUST be able to establish:

```text
exact QLEK K

exact lawful origin Execution E

E was bound to K before semantic dispatch

exact qualifying protocol attempt

exact sealed raw output

deterministic parsed candidate V

Admission(K) == V
```

The origin receipt remains where its historical provenance places it.

A later consuming run/root does not become owner of that receipt.

### 24. Cross-run and cross-root semantic reuse is mandatory when identity matches

If an active protocol obligation requires exact semantic fact `F` and `F` is already derivable from authoritative history:

```text
the existing fact MUST be reused.
```

The runner MUST NOT perform another semantic execution merely because:

```text
the original admission came from another GateARun

the original receipt is projected under another ReviewCampaign

the original receipt belongs to another adjudication supplement

the current evidence root does not own the predecessor receipt
```

A consuming root MAY contain a fact reference or evidence-provenance locator as required by its projection schema.

It MUST NOT duplicate semantic receipt ownership.

No `reused_executions[]` or equivalent semantic-ownership mechanism is required by this ADR.

`reused` is provenance/view information, not semantic authority.

### 25. Semantic dependency graph and evidence provenance graph are distinct

Protocol v8 MUST distinguish:

```text
semantic dependency graph
```

from:

```text
evidence provenance/projection graph
```

The semantic graph contains:

```text
QLEKs
SemanticAdmissions
qualified semantic facts
candidate revisions
other exact authoritative dependencies
```

The provenance graph connects primitive semantic commitments to:

```text
Executions
receipts
raw outputs
protocol attempts
ReviewCampaign projections
supplements
repository artifacts
```

The two graphs MUST remain mechanically cross-linked.

They MUST NOT be collapsed into one same-root receipt DAG.

### 26. CandidateRevision is an exact nominal authority

Protocol v8 adopts `CandidateRevisionId` as an exact nominal authority identity.

Two distinct `CandidateRevisionId` values remain distinct even when their materialized repository content is byte-identical.

Therefore:

```text
C17 != C18
```

implies different candidate-bound QLEKs even if:

```text
CandidateView(C17) == CandidateView(C18)
```

This is required by ADR-055's accepted rule:

```text
new current candidate
→ fresh candidate-bound realization qualification
```

Content equality does not authorize silent scope rebasing or retargeting.

### 27. CandidateRevision and CandidateView have different roles

For candidate-bound questions:

```text
CandidateRevisionId
```

provides nominal authority/freshness identity.

```text
CandidateView
```

provides the exact physical state exposed to cognition.

Protocol-v8 construction MUST establish a deterministic exact relation conceptually equivalent to:

```text
CandidateViewOf(
    exact CandidateRevisionId,
    exact CoverageSpec,
    exact CandidateView
)
```

For one candidate and one exact coverage specification there MUST NOT be two incompatible lawful views.

Candidate views MUST be reconstructed only from the immutable sealed candidate materialization and its exact accepted authority.

Mutable workspace state, current `HEAD`, or ambient filesystem state MUST NOT substitute for the exact bound candidate.

### 28. Candidate-bound families

The following producer question families are directly candidate-bound:

```text
RealizationScopeInitial
RealizationScopeRevision
RepairRealizationInitial
RepairRealizationRevision
```

Their exact logical inputs MUST include the exact `CandidateRevisionId`.

RealizationScope consumes a complete candidate view.

RepairRealization consumes the exact scoped view required by its accepted RealizationScope.

The corresponding challenges inherit candidate binding transitively through the exact challenged producer `SemanticAdmissionId`.

They MUST NOT independently infer or reselect another current candidate.

### 29. Candidate-independent families

The following semantic work remains candidate-independent unless a later accepted protocol explicitly changes its semantic input contract:

```text
materiality
refutation
discovery classification
UniqueCorrection
no-normative-impact qualification
decision-necessity qualification
their accepted same-family semantic revisions/challenges
```

The historical candidate under which their execution occurred is provenance.

It does not become an input merely because the execution belonged to a run that had a current candidate.

### 30. Candidate advance creates new candidate-bound questions, not rerun commands

When exact current candidate changes:

```text
C0 → C1
```

the runner does not apply a hidden rule:

```text
rerun RealizationScope
rerun RepairRealization
```

Instead, protocol binding on the new authoritative state produces new logical inputs containing `C1`.

Therefore:

```text
QLEK_RS(C0) != QLEK_RS(C1)
```

and, where required:

```text
QLEK_RR(C0) != QLEK_RR(C1)
```

Candidate-independent upstream QLEKs remain identical when their exact semantic dependencies have not changed and MUST be reused.

### 31. Candidate-bound revision cannot cross candidate identity

A same-family candidate-bound closure revision MUST retain the exact CandidateRevision of the producer candidate that received the hostile objections.

If that CandidateRevision ceases to be current before the revision is lawfully dispatched, the old candidate-bound revision is no longer required for current progression.

The new current candidate starts a new initial candidate-bound question.

Protocol v8 MUST NOT:

```text
rebase old hostile objections onto the new candidate

retarget an old RealizationScope revision to the new candidate

silently transfer RepairRealization authority
```

### 32. Currentness is an authorization property, not QLEK identity

A logical descriptor MUST bind an exact immutable CandidateRevision.

It MUST NOT contain a mutable symbolic input such as:

```text
"current candidate"
```

The protocol binding rule resolves:

```text
current candidate
→ exact CandidateRevision C
```

before constructing QLEK.

A candidate-bound semantic execution may be newly dispatched only if the bound candidate remains the exact current candidate at the required fresh pre-dispatch authorization/revalidation boundary.

### 33. Candidate advance after lawful dispatch does not erase semantic history

If one candidate-bound QLEK was lawfully dispatched while its bound CandidateRevision was current and a protocol-valid semantic completion is later obtained after another candidate becomes current:

```text
the completed semantic candidate MUST still be reconciled
into the admission history of the old QLEK.
```

It MUST NOT be discarded merely because its candidate is no longer current.

However, that historical admission or any qualification fact derived from it MUST NOT satisfy the new candidate's qualification target.

Thus:

```text
semantic execution truth is preserved

while

current progression applicability may be superseded
```

### 34. RepairIntent remains exact-candidate-bound

A RepairIntent derived from an accepted candidate-bound RepairRealization MUST bind the exact source CandidateRevision authorized by that qualification.

It MUST NOT be applied to another CandidateRevision merely because the repository bytes happen to match.

Candidate successor construction continues to preserve the exact parent/repair provenance required by accepted M2 authority.

### 35. Evidence-root ownership no longer determines semantic usability

Protocol v7's rule that every supporting semantic predecessor receipt must belong to the exact current evidence root is amended for protocol v8.

Protocol-v8 semantic validity MUST NOT require that a consuming ReviewCampaign, supplement, or run own the predecessor's origin receipt.

The following no longer determine semantic predecessor admissibility:

```text
same ReviewCampaign
same FindingAdjudicationSupplement
same GateARun
same root-local supporting_executions[] collection
```

Instead, downstream semantic dependency is valid when:

```text
the exact required FactId is mechanically derivable

AND

the downstream SemanticQuestionContractRevision accepts
that exact typed fact as its input.
```

### 36. Protocol-v8 roots remain projections

`ReviewCampaign` remains one real hostile-review campaign.

`FindingAdjudicationSupplementV1` or its protocol-v8-compatible successor remains an append-only adjudication overlay for one immutable original finding under one exact current protocol where applicable.

Those repository/evidence projections MUST remain auditable and immutable.

They MUST NOT become the namespace defining which global semantic facts a protocol-v8 question may consume.

`SemanticAdmission` is not a third post-review supporting-evidence root.

### 37. Existing effective-adjudication semantics remain

ADR-055's exact effective adjudication variants remain:

```text
qualified-non-material
qualified-refutation
surviving-material
```

Models do not emit these final adjudication states directly.

Protocol-v8 checkers mechanically derive them from exact global semantic admissions, qualification facts, and required authority.

The fact that supporting semantic evidence originated under another run/root does not invalidate the derivation when the exact semantic facts match.

### 38. Protocol-v8 checker model

Protocol-v8 conformance validation MUST separately validate at least the following layers.

#### Contract and protocol integrity

```text
exact protocol bundle
exact predecessor chain
exact schemas/meta-schemas
exact SemanticQuestionContract revisions
exact QualificationContract revisions
exact immutable prompt/realization artifacts where required
```

#### Artifact integrity

```text
exact bytes
hashes
canonical serializations
safe locators
CAS integrity
```

#### QLEK integrity

```text
exact typed semantic inputs
exact authority/fact references
deterministic descriptor construction
recomputed QLEK equality
```

#### Execution/recovery integrity

```text
QLEK-bound execution authorization
pre-dispatch Arm/fence
no unsafe parallel or replacement execution
exact outcome/uncertainty/recovery history
```

#### SemanticAdmission integrity

```text
at most one candidate per QLEK
exact lawful origin execution
exact protocol-valid terminal completion
exact deterministic raw-output-to-candidate binding
```

#### Completion completeness

```text
every protocol-valid semantic completion
reconciles with the exact QLEK admission history
```

#### SemanticFact soundness

```text
every consumed FactId is exactly reconstructible
from authoritative primitive commitments
and exact protocol rules
```

#### Candidate binding

```text
candidate-bound QLEK contains exact CandidateRevisionId
CandidateView is exact deterministic projection of that revision
candidate-bound revision remains on the same candidate
```

#### Semantic dependency well-foundedness

The exact ground semantic dependency graph MUST have no unlawful causal cycle.

Recursive rule families are not themselves forbidden.

Candidate progression such as:

```text
RealizationScope(C0)
→ Repair(C0)
→ C1
→ RealizationScope(C1)
```

is lawful when the exact instance graph progresses through new immutable authority.

#### Projection soundness

Repository review/supplement projections MUST reflect semantic truth exactly without becoming its source.

### 39. Protocol-v8 anti-model-shopping invariants

Protocol-v8 construction and formal verification MUST preserve at least the following properties.

```text
QLEKIntegrity
```

Every declared QLEK recomputes exactly from its immutable contract and typed input.

```text
AtMostOneAdmission
```

For every QLEK, at most one semantic candidate is admitted.

```text
NoDispatchAfterAdmission
```

A QLEK with an admission cannot be semantically dispatched again.

```text
NoUnsafeConcurrentDispatch
```

An unresolved prior execution that may have been semantically dispatched blocks another execution for the same QLEK until exact replacement safety is established.

```text
CompletionAdmissionCompleteness
```

A protocol-valid semantic completion cannot be omitted from admission history and replaced by another sample.

```text
AdmissionEvidenceCompleteness
```

Every native semantic admission has exact lawful immutable origin evidence.

```text
NoSemanticObservationBeforeAdmission
```

A newly produced semantic candidate cannot become a semantic predecessor before authoritative admission.

```text
SemanticFactSoundness
```

Every consumed semantic fact is exactly derivable from authoritative primitive commitments.

```text
CandidateViewSoundness
```

Every candidate view is an exact projection of its bound immutable CandidateRevision.

```text
NoCandidateRebinding
```

Candidate-bound authority cannot be transferred to another CandidateRevision by content equality.

### 40. Existing retry rules remain

ADR-046, ADR-047, ADR-049, ADR-054, and ADR-055 retry/output-validity rules remain authoritative except where this ADR strengthens their scope from one root-local logical execution to one global QLEK.

Technical failure remains distinct from semantic completion.

Protocol-invalid completion remains retryable only where the exact protocol-owned deterministic validator authorizes that classification.

The first protocol-valid semantic completion remains terminal for the semantic execution.

Provider/model identity evidence remains auditable provenance and reviewer-acquisition authority where applicable.

It does not become QLEK identity.

### 41. Protocol v7 remains immutable but permanently inactive

Protocol v7 is a valid immutable published design snapshot and predecessor artifact.

It remains mechanically validated as a regression anchor.

It is not reinterpreted under protocol-v8 semantics.

No protocol-v7 artifact is modified.

No protocol-v7 supporting receipt ownership rule is retroactively changed.

Protocol v7 MUST NOT become current after this ADR is accepted.

### 42. Historical protocol evidence is not reinterpreted

Protocol-v1 through protocol-v6 evidence retains its exact historical interpretation.

Protocol-v8 global semantic-admission semantics do not retroactively convert historical cognitive outputs into `SemanticAdmission`s.

Historical findings, subjects, campaign records, and exact authority may continue to participate in current-protocol stale-finding adjudication where existing authority permits.

A historical cognitive result becomes a protocol-v8 semantic admission only if a later accepted explicit import rule can reconstruct without semantic interpretation:

```text
exact SemanticQuestionContractRevision
exact typed logical input
exact QLEK
exact semantic candidate
```

No generic legacy-import rule is introduced by this ADR.

### 43. No protocol-v7 runtime migration exists

Because protocol v7 has never been current:

```text
there is no protocol-v7 GateARun execution history to migrate;

there is no protocol-v7 semantic admission history to migrate;

there is no protocol-v7 supplement instance migration required.
```

Protocol-v8 construction starts with its native semantic identity/admission architecture.

### 44. Activation remains explicit and separate from ADR acceptance

Acceptance of ADR-056 does NOT make protocol v8 current.

Protocol v6 remains current until all required protocol-v8 construction is complete and accepted.

Before protocol v8 may be selected by `formal/verification.yaml`, construction MUST synchronize at least:

```text
protocol-v8 bundle and immutable predecessor binding

protocol-v8 meta-schema

exact SemanticQuestionContract revisions

exact logical-input/QLEK construction rules

SemanticAdmission authority global across the coherent Authoritative History domain

QLEK-bound execution authorization/fencing/recovery integration

semantic-fact identity and resolution

candidate-revision/view binding

protocol-v8 packet and receipt contracts as required

review/supplement projection changes as required

checker support for every ADR-056 invariant

NIB-S and affected NIB-M construction authority

required Dependency Contracts

formal model and invariant traceability

regression validation for protocols v1-v7
```

Only after that synchronization is accepted may:

```text
formal/verification.yaml
```

select the exact immutable protocol-v8 bundle as current.

## Consequences

### A. Protocol v8 is a new protocol identity

Protocol v8 is not a patched protocol v7.

It requires new immutable protocol artifacts.

At minimum the bundle and any changed interpretation/meta-schema artifacts require new content identity and paths.

Published protocol-v7 bytes remain unchanged.

### B. Output value contracts may be reused when unchanged

This ADR changes semantic identity, dependency, admission, execution fencing, and evidence architecture.

It does not automatically change every structured semantic output value defined by ADR-055.

An existing immutable output schema MAY remain referenced by protocol v8 if its exact value semantics and structural contract remain sufficient and unchanged.

No published schema may be edited in place.

### C. Input/evidence contracts will require protocol-v8 construction

Protocol-v7 `qualifiedDirectProducerClosure`-style semantic dependencies carry root-owned receipts directly.

Protocol-v8 semantic inputs instead require exact semantic fact/admission identity with independently resolvable provenance.

Therefore protocol-v8 packet/evidence construction MUST not merely reuse the protocol-v7 predecessor representation while claiming ADR-056 semantics.

### D. Execution receipts remain evidence, not semantic identity

Execution receipts continue to preserve exact execution truth.

Protocol-v8 construction must additionally bind relevant semantic executions to their exact QLEK and authoritative execution/admission fencing state.

The exact receipt version/field layout is deferred to construction.

### E. Supporting-evidence roots lose semantic-namespace authority

ReviewCampaign and supplement projections remain useful immutable audit artifacts.

They no longer define the universe of semantic predecessor results available to a protocol-v8 cognitive question.

### F. Minimum rerun becomes structural

Protocol v8 no longer requires a manually maintained taxonomy of reusable versus candidate-bound semantic work.

A change creates fresh work exactly where the typed QLEK dependency closure changes.

Unchanged QLEKs reuse their existing admissions.

New QLEKs require at most one semantic admission.

### G. Run reproducibility is strengthened

For one exact protocol revision and one exact primitive Authoritative History state:

```text
deterministic semantic closure reconstruction
```

must reproduce the same:

```text
QLEKs
admissions
qualification facts
active semantic dependencies
candidate-bound frontier
```

without invoking a model for any already-admitted QLEK.

Models are invoked only at exact unresolved semantic effect boundaries.

### H. Protocol-v8 semantic history is monotone

Semantic cognition is never rewritten.

A later protocol state may stop requiring a historical admission or may reject its qualification.

It does not erase that the exact logical question produced that exact candidate.

### I. The architecture remains harness-independent

Pi, Codex, Claude Code, or any future harness may use different realization mechanics for the same `SemanticQuestionContractRevision`.

Those realization differences do not create another QLEK.

A harness that cannot preserve the exact semantic contract/input/output and anti-resampling rules is a conformance limitation, not authority to weaken protocol semantics.

## Rejected alternatives

### 1. Add `FindingResolutionContinuationV1` as a third authoritative evidence root

Rejected.

This repairs the immediate post-supplement ownership case but preserves the incorrect assumption that semantic predecessor validity is defined by receipt-root ownership.

Resolution continuation is better represented as a derived causal projection over global semantic facts and current candidate targets.

### 2. Allow multiple adjudication supplements for the same semantic key

Rejected.

This weakens append-only adjudication identity and creates competing effective overlays.

### 3. Reopen or mutate one existing supplement

Rejected.

Published/current adjudication evidence remains immutable.

### 4. Copy/re-own historical receipts into a later root

Rejected.

One historical execution does not gain another semantic owner merely because another run consumes the fact it established.

### 5. Re-execute candidate-independent work under each new candidate

Rejected.

This creates unnecessary run variance, weakens comparability, and permits semantic-result shopping.

### 6. Use protocol-v7 packet SHA as global QLEK

Rejected.

The packet includes execution/provenance dimensions such as run identity and receipt/root-bound material that are not uniformly semantic inputs.

### 7. Define QLEK by stripping selected provenance fields from protocol-v7 packet bytes

Rejected.

QLEK construction is positive and typed from an exact semantic contract.

It is not a heuristic subtraction from an execution artifact.

### 8. Include prompt/model/provider in QLEK

Rejected.

This would authorize semantic resampling merely by changing realization.

### 9. Scope QLEK by GateARun, ReviewCampaign, evidence root, repository, or protocol store

Rejected.

Where one of those dimensions is semantically relevant it must appear through the exact logical input/contract.

Adding artificial namespace dimensions would make identical logical questions distinct and permit resampling.

### 10. Enforce uniqueness only at SemanticAdmission commit

Rejected.

Two competing model calls could already have sampled alternative semantic candidates before one database uniqueness constraint rejects the loser.

Pre-dispatch exclusive fenced authority and recovery-safe execution history are required.

### 11. Treat process crash or missing response as proof that no semantic execution occurred

Rejected.

Turnlock already distinguishes uncertainty from `PROVEN-NOT-EXECUTED`.

An unresolved possibly-sent execution cannot authorize a competing semantic dispatch.

### 12. Discard a protocol-valid result because its candidate became stale

Rejected.

The semantic sample already occurred.

It must remain part of exact historical admission truth even when it no longer has current progression authority.

### 13. Deduplicate candidate-bound questions by repository content

Rejected.

Distinct `CandidateRevisionId` values remain distinct exact authorities even when materialized bytes match.

ADR-055 requires fresh candidate-bound qualification for a new current candidate.

### 14. Branch protocol v8 directly from protocol v6

Rejected.

Protocol v7 is already a published immutable protocol snapshot in the append-only protocol lineage.

Protocol v8 therefore uses exact published protocol v7 as predecessor while protocol currentness may move directly from v6 to v8.

### 15. Activate protocol v7 temporarily before protocol v8

Rejected.

Once this ADR recognizes protocol-v7's semantic-identity/evidence-ownership gap, protocol v7 is not eligible for current activation.

### 16. Retroactively reinterpret protocol-v1 through protocol-v7 evidence using protocol-v8 semantics

Rejected.

Historical evidence retains the interpretation of its exact governing protocol.

### 17. Introduce a generic problem-solving IR or DSL as part of this decision

Rejected as premature.

This ADR defines Turnlock-specific protocol semantics.

The architecture intentionally preserves later abstraction extractability but does not make a generalized IR part of Gate A protocol-v8 authority.

## Non-decisions

This ADR intentionally does not select:

```text
physical SQL table names

whether SemanticAdmission has a standalone repository artifact

the exact SQLite/lock primitive used for QLEK live exclusion

the exact public serialization of LogicalQuestionDescriptor

the exact public serialization of SemanticFact references

the exact hash framing implementation

the final packet/receipt schema version numbers

the final supplement schema version

a cross-protocol semantic-equivalence mechanism

a generic legacy cognitive-result import mechanism

a generalized Turnlock/SCOPE IR
```

Subsequent construction may choose among conforming realizations only where this ADR and higher authority leave implementation freedom.

Construction MUST STOP rather than invent product/protocol semantics when these decisions are insufficient.

## Required follow-up

After acceptance of this ADR, the next architecture/construction work is:

```text
1. publish the protocol-v8 construction plan;

2. define exact protocol-v8 SemanticQuestionContract revisions
   for every producer, revision, and challenge family;

3. define exact typed LogicalQuestionDescriptor/QLEK construction;

4. define the globally single-assignment SemanticAdmission authoritative
   mutation within the coherent Authoritative History domain and its
   origin-evidence binding;

5. bind existing M2/M4 execution authorization, Arm, uncertainty,
   recovery, and replacement-safety semantics to QLEK admission authority;

6. define exact SemanticFact identity/resolution and protocol-v8
   semantic predecessor packet representation;

7. add exact CandidateRevisionId + CandidateView binding for
   candidate-bound families;

8. define protocol-v8 checker passes and formal invariants;

9. update affected NIB-S/NIB-M/DC construction authority mechanically;

10. mechanically validate protocol-v8 while keeping protocol v6 current;

11. explicitly activate protocol v8 only after every required
    construction and verification precondition is accepted.
```

Until those steps are complete:

```text
gate-a-campaign-protocol-v6 remains current

gate-a-campaign-protocol-v7 remains immutable and inactive

gate-a-campaign-protocol-v8 is not yet current
```
