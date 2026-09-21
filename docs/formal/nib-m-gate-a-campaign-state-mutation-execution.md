---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-09-20"
step_id: 2
id: NIB-M-GATE-A-CAMPAIGN-STATE-MUTATION-EXECUTION
version: "1.0.11"
scope: gate-a-campaign-runner/campaign-state/mutation-execution
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Campaign State — Mutation Admission and Execution Lifecycle

## 1. Status, authority, and purpose

This document is one of three active Module Briefs that together close M2
`campaign-state` for the Gate A hostile-review campaign runner.

It consumes `NIB-S-GATE-A-CAMPAIGN-RUNNER` version `6.0.11`.

It is implementation-construction authority only. It does not define TURNLOCK
product semantics, canonical formal semantics, hostile-review protocol
semantics, formal-assurance claims, review evidence, or verification evidence.

This brief defines the complete M2 authoritative mutation language and the
algorithms that admit campaign facts into Authoritative History.

Every successful mutation is one atomic append-only `StateRevision`.

M2 validates authority, identity, structural consistency, causal preconditions,
and global invariants.

It does not invent M3 currentness, M5 assurance meaning, M6 validator
conclusions, M7 repository facts, or M8 recovery classifications.

Persistence and ownership mechanics are defined by
`NIB-M-GATE-A-CAMPAIGN-STATE-PERSISTENCE-OWNERSHIP`.

Snapshot reconstruction and retained-state integrity are defined by
`NIB-M-GATE-A-CAMPAIGN-STATE-SNAPSHOT-INTEGRITY`.

## 2. Public input/output

The public mutation boundary remains exactly:

```ts
interface CommitAuthoritativeMutationRequest {
  readonly runId: GateARunId;
  readonly authority: WriteAuthorityRef;
  readonly expectedStateRevision: StateRevision;
  readonly mutation: AuthoritativeMutationRef;
}

type CommitAuthoritativeMutationResult =
  | {
      readonly kind: "committed";
      readonly newStateRevision: StateRevision;
      readonly snapshot: GateARunSnapshot;
    }
  | {
      readonly kind: "stale-state";
      readonly currentStateRevision: StateRevision;
    }
  | {
      readonly kind: "ownership-lost";
      readonly currentOwnershipGeneration: OwnershipGeneration;
    };
```

Malformed mutation input, contradictory proposed history, or inability to trust
authoritative state is not encoded as another branch of this union.

It rejects the invocation as an implementation/process/integrity failure.

## 3. Serialized mutation envelope

`AuthoritativeMutationRef.artifact` must contain UTF-8 JSON validating exactly
as:

```ts
interface GateAStateMutationArtifactV1 {
  readonly schema: "gate-a-state-mutation.v1";
  readonly runId: GateARunId;
  readonly baseStateRevision: StateRevision;
  readonly mutation: GateAStateMutationV1;
}
```

The artifact must already exist in the immutable artifact store before the
SQLite transaction begins.

The mutation artifact itself is immutable provenance.

M2 additionally inserts normalized authoritative facts from its validated
content.

## 4. Closed mutation union

```ts
type GateAStateMutationV1 =
  | EstablishPreflightV1
  | AdmitCandidateV1
  | EstablishReviewCampaignBundleV1
  | EstablishOperationalBlockersV1
  | AuthorizeExecutionV1
  | ArmExecutionDispatchV1
  | AdmitExecutionOutcomeV1
  | AdmitExecutionUncertaintyV1
  | AdmitExecutionRecoveryV1
  | AdmitAssuranceLedgerDeltaV1
  | AdmitMechanicalValidationObservationV1
  | AdmitGateAQualificationV1
  | EstablishPublicationIntentV1
  | AdmitPublicationObservationQualificationV1
  | AdmitOperatorResolutionV1
  | EstablishGateAReadyV1;
```

No `"generic"`, `"custom"`, `"patch"`, or `"other"` mutation kind exists.

## 5. Mutation types

### 5.1 Preflight

```ts
interface EstablishPreflightV1 {
  readonly kind: "establish-preflight";
  readonly repositoryInspection: RepositoryInspectionRef;
  readonly baselineAuthority: RepositoryAuthorityRef;
  readonly publicationTarget: RepositoryPublicationTargetRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly preflightEvidence: readonly ArtifactRef[];
  readonly rootObligationDisposition: Extract<
    ObligationDispositionRef,
    { readonly kind: "satisfied" }
  >;
}
```

This mutation is accepted at most once per run.

M2 validates:

```text
repositoryInspection.runId == exact run

baselineAuthority ==
    repositoryInspection.baselineAuthority

publicationTarget ==
    repositoryInspection.publicationTarget

repositoryInspection sealed-baseline bindings pass NIB-S

every RepositoryInspectionRef ArtifactRef exists and is intact

preflightEvidence duplicate-free
every preflightEvidence ArtifactRef intact

rootObligationDisposition names exact bootstrap root obligation

rootObligationDisposition.basisEvidenceIds == []

rootObligationDisposition.basisArtifacts equals exactly the ordered

duplicate-free first-occurrence sequence:

[
    repositoryInspection.baselineGitBasis,
    repositoryInspection.sealedBaselineCandidate.materialization,
    ...repositoryInspection.sealedBaselineCandidate.materializationEvidence,
    ...repositoryInspection.evidence,
    ...preflightEvidence
]
```

### 5.2 Candidate

```ts
interface AdmitCandidateV1 {
  readonly kind: "admit-candidate";
  readonly sealedCandidate: SealedCandidateMaterializationRef;
  readonly candidate: CandidateRevisionRef;
}
```

Candidate identity is M2-owned.

For `C0`:

```text
ordinal = 0
parentCandidateId = null
producedByRepairIntentId = null
```

For `Cn+1`:

```text
ordinal = currentCandidate.ordinal + 1
parentCandidateId = currentCandidate.candidateId
producedByRepairIntentId = exact admitted qualified RepairIntent
```

Identity:

```text
deriveId(
  "candidate-revision.v1",
  runId,
  decimal ordinal,
  parentCandidateId or "-",
  producedByRepairIntentId or "-"
)
```

`materialization` and `semanticSubject` are payload bound to the logical slot.

A second different payload for the same slot is `INVALID_MUTATION`.

For `AdmitCandidateV1` when `ordinal = 0`:

```text
exact EstablishPreflightV1 exists

sealedCandidate ==
    EstablishPreflightV1.repositoryInspection.sealedBaselineCandidate
```

C0 may not substitute another materialization after baseline establishment.

### 5.3 Review campaign bundle

```ts
interface ReviewerPrerequisiteAdmissionBasis {
  readonly candidateId: CandidateRevisionId;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly qualifyingReviewerProfileIds: readonly string[];
  readonly evidence: readonly ArtifactRef[];
}

interface EstablishReviewCampaignBundleV1 {
  readonly kind: "establish-review-campaign-bundle";
  readonly campaign: ReviewCampaignRef;
  readonly prerequisiteBasis: ReviewerPrerequisiteAdmissionBasis;
  readonly obligations: readonly ObligationRef[];
  readonly workItems: readonly WorkItemRef[];
}
```

The campaign and all initial obligations/work items are committed in the same
revision.

No runner-created executable campaign may become visible before its complete
initial bundle is admitted.

Imported repository campaigns are not created through this mutation; they are
registered from exact M3 evaluation context during
`AdmitAssuranceLedgerDeltaV1`.

### 5.4 Operational blockers

```ts
interface EstablishOperationalBlockersV1 {
  readonly kind: "establish-operational-blockers";
  readonly blockers: readonly OperationalBlocker[];
  readonly basisArtifacts: readonly ArtifactRef[];
}
```

`blockers` must be non-empty.

Every blocker must reference an exact admitted or co-admitted obligation.

Every admitted `OperationalBlocker` must satisfy the accepted M8-B
operational-boundary identity and Operator Action Request contract.

M2 does not invent or normalize an operational blocker identity.

For every blocker it verifies:

```text
operatorRequest ArtifactRef exists and is intact
Operator Action Request runtime shape is valid
OAR/blocker field bindings are exact
BlockerId recomputes under the exact M8-B identity policy selected by OAR.source
```

`basisArtifacts` remain evidence/provenance for the producing condition. They
are not implicitly part of `BlockerId`.

### 5.5 Execution authorization

```ts
type ExecutionCreationRequestBasis =
  | {
      readonly kind: "initial-work";
    }
  | {
      readonly kind: "protocol-retry";
      readonly retryAuthorizationId: ExecutionRetryAuthorizationId;
    }
  | {
      readonly kind: "proven-not-executed";
      readonly priorExecutionId: ExecutionId;
    };

interface AuthorizeExecutionV1 {
  readonly kind: "authorize-execution";
  readonly workItemId: WorkItemId;
  readonly basis: ExecutionCreationRequestBasis;
}
```

Caller does not provide `ExecutionId` or `attemptOrdinal`.

M2 derives them.

Attempt ordinals begin at:

```text
1
```

Identity:

```text
deriveId(
  "execution.v1",
  workItemId,
  decimal attemptOrdinal
)
```

The persisted internal creation basis is exactly one of:

```text
initial-work
protocol-retry
proven-not-executed
operator-replacement
```

For `operator-replacement`, the persisted internal basis is exactly:

```ts
interface OperatorReplacementCreationBasisV1 {
  readonly kind: "operator-replacement";
  readonly priorExecutionId: ExecutionId;
  readonly blockerId: BlockerId;
  readonly operatorResolution: ArtifactRef;
}
```

This basis is created only by the atomic
`AdmitOperatorResolutionV1` replacement path.

It is not accepted through `AuthorizeExecutionV1`.

The presence of a successor Execution carrying a one-shot basis is itself the
append-only proof that the basis was consumed.

There is no mutable `consumed` flag.

### 5.6 Arm dispatch

```ts
interface ArmExecutionDispatchV1 {
  readonly kind: "arm-execution-dispatch";
  readonly executionId: ExecutionId;
  readonly workItemId: WorkItemId;
  readonly ownershipGeneration: OwnershipGeneration;
  readonly revalidationBasis: readonly ArtifactRef[];
  readonly dispatchEvidence: readonly ArtifactRef[];
  readonly recoveryCapability: RecoveryCapabilityRef | null;
}
```

The enclosing mutation artifact itself is the durable:

```text
dispatchIntent
```

for the resulting `ArmedExecutionDispatchRef`.

Successful commit is the exact transition:

```text
AUTHORIZED-NOT-DISPATCHED
→
POSSIBLY-DISPATCHED
```

and the side-effect permission linearization point.

### 5.7 Direct execution outcome

```ts
interface AdmitExecutionOutcomeV1 {
  readonly kind: "admit-execution-outcome";
  readonly outcome:
    | {
        readonly kind: "captured";
        readonly value: CapturedExecutionResult;
      }
    | {
        readonly kind: "technical-failure";
        readonly value: TechnicalExecutionFailure;
      };
}
```

This is used only when the owning executor directly returns a known terminal
capture/failure after an armed dispatch.

For a repository-control publication Execution whose direct M7 capture will be
submitted to `PublicationObservationQualificationRequest`,
`AdmitExecutionOutcomeV1` must commit that exact
`CapturedExecutionResult` before
`AdmitPublicationObservationQualificationV1` may be admitted.

The publication-observation qualification mutation never introduces a
previously unknown execution result.

An execution already routed through uncertainty/recovery is terminalized through
`AdmitExecutionRecoveryV1`, not this mutation.

### 5.8 Uncertainty enrichment

```ts
interface AdmitExecutionUncertaintyV1 {
  readonly kind: "admit-execution-uncertainty";
  readonly unresolved: UnresolvedExecutionRecoveryRef;
}
```

This mutation does not make an execution unresolved.

Arm already did that.

It only enriches the exact armed unresolved execution.

### 5.9 Recovery

```ts
interface AdmitExecutionRecoveryV1 {
  readonly kind: "admit-execution-recovery";
  readonly resolution: ExecutionRecoveryResolution | null;
  readonly lastPending: ReconciliationPendingRef | null;
  readonly blockers: readonly OperationalBlocker[];
  readonly blockerIdsToDispose: readonly BlockerId[];
}
```

Valid shapes are exactly:

```text
PROVEN-NOT-EXECUTED:
    resolution != null
    resolution.classification = PROVEN-NOT-EXECUTED
    lastPending = null

PROVEN-COMPLETED:
    resolution != null
    resolution.classification = PROVEN-COMPLETED
    lastPending = null

UNRESOLVABLE:
    resolution != null
    resolution.classification = UNRESOLVABLE
    exactly its required blocker is present
    lastPending = null

pending-policy-exhausted:
    resolution = null
    lastPending != null
    one exact operational blocker is present
```

`blockerIdsToDispose` may contain only operational blockers whose exact causal
condition is mechanically superseded by the admitted recovery fact.

M2 never chooses this set.

It verifies the supplied disposition is structurally legal.

### 5.10 Assurance-ledger delta

```ts
interface AdmitAssuranceLedgerDeltaV1 {
  readonly kind: "admit-assurance-ledger-delta";
  readonly evaluationContext: GateAEvaluationContext;
  readonly cognitiveAttemptValidations:
    readonly CognitiveAttemptValidationResult[];
  readonly delta: AssuranceLedgerDelta;
}
```

Require:

```text
delta.expectedStateRevision == mutation.baseStateRevision
```

This mutation may atomically establish:

```text
observed repository ReviewCampaignRefs
cognitive-attempt classification facts
EvidenceRefs
FindingRefs
AdjudicationRefs
ReAdjudicationRefs
ObligationDispositionRefs
RepairIntentRefs
DecisionRequestRefs
ObligationRefs
WorkItemRefs
ExecutionRetryAuthorizationRefs
CampaignBlockers
CandidateReviewReadinessRef
CandidateReviewReadiness designation
```

M5 remains producer of its ledger semantics.

### 5.11 Non-cognitive mechanical validation

```ts
type NonCognitiveMechanicalValidationRequest = Exclude<
  MechanicalValidationRequest,
  CognitiveAttemptValidationRequest
>;

type NonCognitiveMechanicalValidationResult = Exclude<
  MechanicalValidationResult,
  CognitiveAttemptValidationResult
>;

interface AdmitMechanicalValidationObservationV1 {
  readonly kind: "admit-mechanical-validation-observation";
  readonly request: NonCognitiveMechanicalValidationRequest;
  readonly result: NonCognitiveMechanicalValidationResult;
}
```

Cognitive-attempt validation is forbidden here.

It belongs only to `AdmitAssuranceLedgerDeltaV1`.

### 5.12 Gate A qualification

```ts
interface AdmitGateAQualificationV1 {
  readonly kind: "admit-gate-a-qualification";
  readonly qualification: GateAQualificationRef;
}
```

M2 must find an already-admitted passing exact Gate A mechanical validation
observation whose candidate, campaign sets, and evidence match this
qualification.

### 5.13 Publication intent

```ts
interface EstablishPublicationIntentV1 {
  readonly kind: "establish-publication-intent";
  readonly intent: PublicationIntentRef;
  readonly publicationObligation: ObligationRef;
  readonly publicationWorkItem: WorkItemRef;
}
```

At most one effective publication intent may exist for one exact
candidate/qualification transition.

Historical intents remain retained.

### 5.13.1 Publication intent identity

M2 recomputes `PublicationIntentRef.publicationIntentId` exactly as:

```text
deriveId(
    "publication-intent.v1",
    runId,
    candidateId,
    qualificationId,
    transition.target.repositoryIdentity,
    transition.target.remoteEndpoint,
    transition.target.refName,
    transition.predecessor.commitSha,
    transition.predecessor.treeSha,
    transition.successor.commitSha,
    transition.successor.treeSha
)
```

Publication intent identity excludes:

```text
StateRevision
ownership generation
timestamp
preparationEvidence
ancestryEvidence ArtifactRef identities
WorkItemId
ExecutionId
```

M2 must recompute and require exact equality.

Replaying an identical preparation for the exact same transition therefore
produces the same logical intent identity. A different predecessor or successor
produces a different intent identity.

### 5.13.2 Publication obligation and WorkItem identities

M2 recomputes the co-admitted identities exactly as:

```text
publicationObligation.obligationId =
deriveId(
    "publication-obligation.v1",
    intent.publicationIntentId
)
```

```text
publicationWorkItem.workItemId =
deriveId(
    "publication-work-item.v1",
    intent.publicationIntentId
)
```

M2 requires:

```text
publicationObligation.runId == intent.runId
publicationObligation.candidateId == intent.candidateId
publicationObligation.reviewCampaignId == null
publicationObligation.definition ArtifactRef exists and is intact

publicationWorkItem.runId == intent.runId
publicationWorkItem.candidateId == intent.candidateId
publicationWorkItem.reviewCampaignId == null
publicationWorkItem.executor == "repository-control"

publicationWorkItem.sourceObligationIds
    == [publicationObligation.obligationId]

publicationWorkItem.operation ArtifactRef exists and is intact

every publicationWorkItem.inputRefs ArtifactRef exists and is intact
publicationWorkItem.inputRefs is duplicate-free
```

The exact runtime schema of:

```text
publicationObligation.definition
publicationWorkItem.operation
```

and the pure binding extractor proving the operation represents the exact
`PublicationIntentRef` belong to the future M7 NIB-M.

GREEN is blocked until that M7 contract exists.

M2 must not infer publication binding merely from:

```text
executor == "repository-control"
candidateId
target
repository path
```

### 5.13.3 Admission preconditions

For `EstablishPublicationIntentV1`, M2 requires all of the following before
admission:

```text
intent.runId == exact GateARun

intent.candidateId == exact currentCandidate.candidateId

intent.qualificationId ==
    exact currently projected gateQualification.qualificationId

intent.transition.target ==
    exact immutable run.publicationTarget

intent.transition.relationship == "fast-forward"

intent.transition.predecessor is ancestor-or-equal to
    intent.transition.successor by accepted M7 evidence

every intent.preparationEvidence ArtifactRef exists and is intact

every intent.transition.ancestryEvidence ArtifactRef exists and is intact

publication obligation/work bindings pass section 5.13.2
```

M2 does not reinterpret Git ancestry evidence.

It validates the construction/reference bindings fixed by NIB-S and future M7
contracts.

### 5.13.4 Initial versus replacement intent

Before inserting the new intent bundle, M2 obtains the currently projected
applicable publication intent for the current exact
candidate/qualification:

```text
priorIntent
```

**Case A — no prior intent**

M2 atomically appends in one StateRevision:

```text
intent
publicationObligation
publicationWorkItem
```

No obligation supersession is created.

**Case B — the exact same intent identity already exists and is currently projected**

M2 rejects the proposal as:

```text
INVALID_MUTATION
```

M2 does not create another StateRevision solely to duplicate the same effective
intent.

**Case C — a different prior intent exists for the same exact current candidate/qualification**

M2 finds its exact co-admitted:

```text
priorPublicationObligation
priorPublicationWorkItem
```

The new intent may replace it automatically only when ALL of these are true:

```text
no PublicationConfirmationRef exists for priorIntent

and every armed Execution in priorPublicationWorkItem is replacement-safe.

Define `replacement-safe(E)` exactly as:

```text
E has an exact terminal PROVEN-NOT-EXECUTED recovery resolution

OR

E has exactly one authoritative PublicationNonApplicationRef
```

Additionally, no prior WorkItem Execution is currently:

```text
unresolved POSSIBLY-DISPATCHED
pending recovery
UNRESOLVABLE without a non-application fact
PROVEN-COMPLETED publication application
confirmed publication producer
progression-superseded uncertain Execution lacking prior exact safe disposition
```

A direct captured result alone is neither safe nor unsafe. Its authoritative
M7 publication qualification decides.

A `TechnicalExecutionFailure` after Arm is not replacement-safe merely because
it is terminal.

A `PublicationNonApplicationRef` does not itself authorize another Execution
for the same WorkItem.
```

If these conditions do not hold, M2 rejects as:

```text
INVALID_MUTATION
```

M2 does not create a blocker inside M2.

M2 does not invent an operator action from an invalid proposal.

If replacement is safe, M2 atomically appends in the SAME StateRevision:

```text
new intent
new publicationObligation
new publicationWorkItem

one exact ObligationDispositionRef {
    kind: "superseded",
    obligationId: priorPublicationObligation.obligationId,
    replacementObligationIds: [
        new publicationObligation.obligationId
    ],
    basisEvidenceIds: [],
    basisArtifacts: intent.preparationEvidence
}
```

M2 requires:

```text
priorPublicationObligation is currently outstanding
```

The supersession disposition is M2 lifecycle plumbing fixed by this brief.

It does not assert repository truth beyond the already validated new
`PublicationIntent` proposal.

The prior intent, prior obligation, prior WorkItem, and prior Executions are
never mutated or deleted.

### 5.14 Publication observation qualification

```ts
interface AdmitPublicationObservationQualificationV1 {
  readonly kind: "admit-publication-observation-qualification";
  readonly request: PublicationObservationQualificationRequest;
  readonly result: PublicationObservationQualificationResult;
}
```

This mutation is the only M2 admission boundary for an M7 publication
observation qualification result.

For every request kind define:

```text
I = request.intent
C = request.candidate
W = exact publication WorkItem co-admitted with I
O = exact publication obligation co-admitted with I
```

M2 requires this common branch before either result branch is admitted:

```text
I exists
I == exact currently projected publicationIntent

C exists
C == exact currentCandidate

C.candidateId == I.candidateId

I.qualificationId ==
    exact currently projected gateQualification.qualificationId

W exists
W == exact publication WorkItem co-admitted with I

W.executor == "repository-control"
W.candidateId == C.candidateId

O exists
O is exact publication obligation co-admitted with I
O is currently outstanding
```

The exact runtime-validated M7 publication operation/input representation and
binding extractor belong to the future M7 NIB-M. The coding agent may not infer
that binding from repository-control executor identity alone.

#### Executed-publication branch

For:

```text
request.kind == "executed-publication"
```

let:

```text
E = request.executionResult.execution
```

M2 retains all existing executed-publication requirements:

```text
E exists
E has a successful Arm
no progression supersession
request.executionResult already authoritative
W is the exact owning WorkItem
exact runtime M7 binding is established
```

More precisely:

```text
no ExecutionProgressionSupersessionRef exists for E

request.executionResult equals one exact already-authoritative
CapturedExecutionResult for E

that captured result was admitted either:
    directly through AdmitExecutionOutcomeV1
    or
    as the captured recovered outcome of a PROVEN-COMPLETED
    AdmitExecutionRecoveryV1

M2 retains which exact authoritative admission introduced the result; it never
infers direct-versus-recovered provenance from the captured payload.

W == the exact publication WorkItem owning E
```

A recovered captured result remains eligible for ordinary executed-publication
qualification, including confirmation, but it is never eligible to establish
publication non-application.

For:

```text
result.kind = "confirmed"
```

M2 requires:

```text
result.confirmation.publicationIntentId ==
    I.publicationIntentId

result.confirmation.candidateId ==
    C.candidateId

result.confirmation.transition ==
    I.transition

result.publishedView.publicationConfirmationId ==
    result.confirmation.publicationConfirmationId

result.publishedView.candidateId == C.candidateId

result.publishedView.target == I.transition.target

result.publishedView.authority == I.transition.successor
    by exact commit SHA and tree SHA
```

For:

```text
result.kind = "not-applied"
```

M2 requires:

```text
result.nonApplication.publicationIntentId ==
    I.publicationIntentId

result.nonApplication.candidateId ==
    C.candidateId

result.nonApplication.executionId ==
    E.executionId

result.nonApplication.workItemId ==
    W.workItemId

result.nonApplication.dispatchIntent ==
    exact Arm dispatchIntent for E

result.nonApplication.attemptResult ==
    request.executionResult.rawResult

request.executionResult was introduced for E by one exact direct
AdmitExecutionOutcomeV1 whose outcome.kind == "captured"

no AdmitExecutionRecoveryV1 is the authoritative introduction of that captured
result

proof/basis ArtifactRefs intact

future M7 pure validator accepts the exact non-application binding
```

If the direct-outcome provenance conditions fail, M2 rejects the proposed
`not-applied` mutation as `INVALID_MUTATION` and appends no
`PublicationNonApplicationRef`. A captured result introduced by
`AdmitExecutionRecoveryV1` may not be used for this branch.

M2 atomically appends the exact publication-observation qualification
request/result basis and exact `PublicationNonApplicationRef` for this branch.
It appends:

```text
NO PublicationConfirmationRef
NO PublishedRepositoryViewRef
NO publication obligation disposition
```

A `PublicationNonApplicationRef` does not satisfy `O` and does not manufacture
an Execution outcome.

For:

```text
result.kind = "blocked"
```

M2 retains the current blocker ownership shape:

```text
result.blocker.kind == "operational"
result.blocker.executionId == E.executionId
result.blocker references one exact applicable publication obligation
```

M2 atomically appends the exact request/result basis and blocker, and appends
no confirmation or published view.

#### Already-current branch

For:

```text
request.kind == "already-current"
```

M2 requires exactly:

```text
I.transition.predecessor ==
    I.transition.successor

zero Execution exists for W

request.observation.publicationIntentId ==
    I.publicationIntentId

request.observation.candidateId ==
    C.candidateId

request.observation.target ==
    I.transition.target

request.observation.observedAuthority ==
    I.transition.successor
    by exact commit SHA and tree SHA

every observation evidence ArtifactRef intact

future M7 pure validator accepts exact already-current observation
```

`result.kind = "not-applied"` is invalid for this request kind. The
already-current request may produce `confirmed` but never `not-applied`.
`result.kind = "blocked"` is not used merely because the target changed before
qualification; orchestration declines to submit the stale request and
re-enters preparation instead.

For a confirmed result in either legal branch, M2 requires the exact
confirmation and published-view bindings above and atomically appends in the
same `StateRevision`:

```text
exact publication-observation qualification request/result basis
exact PublicationConfirmationRef
exact PublishedRepositoryViewRef identity descriptor
one exact ObligationDispositionRef {
    kind: "satisfied",
    obligationId: O.obligationId,
    basisEvidenceIds: [],
    basisArtifacts: <exact sequence below>
}
```

For `executed-publication`, `basisArtifacts` is the ordered duplicate-free
first-occurrence sequence:

```text
[
    request.executionResult.rawResult,
    ...request.executionResult.runtimeEvidence,
    ...result.confirmation.materialIdentityEvidence
]
```

For `already-current`, `basisArtifacts` is the ordered duplicate-free
first-occurrence sequence:

```text
[
    ...request.observation.evidence,
    ...result.confirmation.materialIdentityEvidence
]
```

M2 requires `O` had no prior disposition. There must never be an authoritative
revision with a new `PublicationConfirmationRef` while `O` remains outstanding.
Only `result.kind = "confirmed"` creates a `PublicationConfirmationRef`.
A captured publication result by itself never establishes publication
confirmation. A blocked publication qualification is a known M7 domain result
and is not an M8 execution-uncertainty classification.

### 5.15 Operator resolution

M2 accepts only an M8-validated state effect.

M2 consumes the NIB-S `OperatorResolutionStateEffect` union unchanged.

The public M2 mutation remains:

```ts
interface AdmitOperatorResolutionV1 {
  readonly kind: "admit-operator-resolution";
  readonly envelope: OperatorResolutionEnvelope;
  readonly effect: OperatorResolutionStateEffect;
}
```

The exact operator-resolution artifact union and the mapping from each accepted
artifact to one of these state effects belong to the M8 NIB-M.

GREEN may not begin until that M8 contract is closed.

M1 does not choose `effect`.

For:

```text
effect.kind = resolve-blocker-only
```

let:

```text
B = exact OperationalBlocker named by envelope.blockerId
R = envelope.resolution
```

M2 requires:

```text
envelope.runId == exact run

B exists
B is currently outstanding
B.kind == operational

R exists as an intact immutable ArtifactRef

the exact OperatorResolutionEnvelope is M8-validated
the exact state effect is M8-validated
```

M2 atomically appends in one StateRevision:

```text
the exact accepted OperatorResolutionEnvelope
the exact target blocker disposition
```

and nothing else merely because that blocker was disposed.

`resolve-blocker-only` does not:

```text
satisfy an obligation
supersede an obligation
create an Execution
create an ExecutionProgressionSupersessionRef
establish preflight
establish reviewer prerequisites
establish publication confirmation
establish mechanical-validation success
create semantic authority
```

The authoritative producer boundary must mechanically re-evaluate any
underlying condition after blocker disposition.

For:

```text
effect.kind = resolve-blocker-and-replace-execution
```

let:

```text
E = exact prior Execution named by effect.priorExecutionId
W = exact authoritative WorkItem for E
B = exact OperationalBlocker named by envelope.blockerId
R = envelope.resolution
```

M2 requires:

```text
envelope.runId == exact run

B exists
B is currently outstanding
B.kind == operational
B.executionId == E.executionId

E exists
E.workItemId == W.workItemId
E is the current WorkItem execution tail

no ExecutionProgressionSupersessionRef already names E as priorExecutionId
no later Execution for W already exists

at least one W.sourceObligationIds member remains outstanding

run is not GATE-A-READY
semantic progression does not prohibit replacement

historical Execution count for W < 5

R exists as an intact immutable ArtifactRef
```

M2 does not interpret `R` as execution truth.

M8 owns validation of the exact operator-resolution artifact union and supplies
the already validated `OperatorResolutionStateEffect`.

M2 derives exactly one successor:

```text
successor.attemptOrdinal = E.attemptOrdinal + 1

successor.executionId =
    deriveId(
        "execution.v1",
        W.workItemId,
        decimal successor.attemptOrdinal
    )

successor.workItemId = W.workItemId
```

M2 constructs exactly one:

```ts
ExecutionProgressionSupersessionRef {
  runId: exact runId,
  workItemId: W.workItemId,
  priorExecutionId: E.executionId,
  successorExecutionId: successor.executionId,
  blockerId: B.blockerId,
  operatorResolution: R,
}
```

The successor's persisted creation basis is exactly:

```ts
{
  kind: "operator-replacement",
  priorExecutionId: E.executionId,
  blockerId: B.blockerId,
  operatorResolution: R,
}
```

M2 atomically appends in one StateRevision:

```text
the exact accepted OperatorResolutionEnvelope
the exact target blocker disposition
the exact ExecutionProgressionSupersessionRef
the exact successor Execution
the exact successor operator-replacement creation basis
```

There is no authoritative intermediate state in which:

```text
the prior Execution is superseded but no successor exists

or

the successor exists without the exact supersession relation
```

Progression supersession does not append:

```text
CapturedExecutionResult
TechnicalExecutionFailure
ExecutionRecoveryResolution
ReconciliationPendingRef
NonExecutionProofRef
RecoveryIndeterminacyRef
```

for the prior Execution merely because replacement was authorized.

### 5.15.1 Execution progression supersession

`ExecutionProgressionSupersessionRef` is append-only.

One prior Execution may have at most one progression supersession.

A supersession:

```text
revokes future campaign-progression authority for the prior Execution
revokes future automatic-recovery eligibility for the prior Execution
preserves the prior Execution in immutable historical state
does not assert any external execution outcome
```

A later result or observation for the superseded prior Execution may remain
available as audit material outside progression authority, but M2 must reject
any new post-supersession mutation that would use it to create authoritative
campaign progression.

A progression supersession is irreversible within the GateARun.

It is never removed when:

```text
the prior executor later returns
the prior provider later reports a result
the successor succeeds
the successor fails
ownership changes
the run resumes
```

### 5.16 Gate A ready

```ts
interface EstablishGateAReadyV1 {
  readonly kind: "establish-gate-a-ready";
  readonly qualificationId: GateAQualificationId;
  readonly publicationConfirmationId: PublicationConfirmationId;
}
```

M2 finds and verifies the exact passing post-publication mechanical validation
fact internally.

No caller-supplied boolean can establish readiness.

## 6. Common commit algorithm

```text
commitAuthoritativeMutation(request):

    verify exact local ownership handle
    verify mutation ArtifactRef exists and is intact

    parse exact GateAStateMutationArtifactV1
    validate with M0

    BEGIN IMMEDIATE authoritative DB

    verify trustworthy run authority

    if durable max generation != request.authority.generation:
        rollback
        return ownership-lost(current generation)

    if exact session/generation does not equal authority:
        rollback
        return ownership-lost(current generation)

    currentRevision = exact current revision

    if request.expectedStateRevision != currentRevision:
        rollback
        return stale-state(currentRevision)

    require mutation.runId == request.runId
    require mutation.baseStateRevision == currentRevision

    validate mutation-specific references
    recompute every M2-owned identity
    validate producer-owned identities through accepted M0/domain contracts
    verify all ArtifactRefs
    validate terminality matrix
    validate retry/capability rules

    determine exact set of new append-only facts

    if zero new authoritative facts:
        reject INVALID_MUTATION("NO_NEW_FACTS")

    nextRevision = currentRevision + 1

    append state_revisions(nextRevision)
    append all mutation facts with introduced_revision = nextRevision

    reconstruct exact resulting snapshot using snapshot/integrity M2
    run complete resulting-state invariant check

    COMMIT

    return committed(nextRevision, snapshot)
```

An exact already-existing object may be referenced again when another new fact
is being admitted.

Same logical ID + different payload is `INVALID_MUTATION`.

Already-authoritative contradictory retained history is `INTEGRITY_FAILURE`.

## 7. Execution authorization algorithm

For WorkItem `W`:

```text
require W exists
require at least one source obligation is outstanding
require run is not GATE-A-READY
require semantic progression does not prohibit new work
require no outstanding OperationalBlocker exists
```

Let existing executions for W be ordered by `attemptOrdinal`.

### Initial

```text
basis = initial-work

require no existing execution for W
ordinal = 1
```

### Protocol retry

```text
basis = protocol-retry(R)

require R exists
require R.workItemId == W
require R.priorExecutionId == current execution tail
require R is not already named by another execution creation basis
require prior execution has exact basis required by R.reason
require prior execution is terminal
```

For:

```text
technical-failure
```

the exact prior `TechnicalExecutionFailure` must exist.

For:

```text
protocol-invalid
```

the exact admitted M6 classification must be `protocol-invalid`, role must be
`initial-reviewer` or `challenge`, and exact validation evidence required by the
authorization must already be authoritative or co-admitted.

A `qualified` attempt cannot back a retry.

### Proven-not-executed

```text
basis = proven-not-executed(E)

require E == current execution tail
require exact terminal recovery resolution for E is PROVEN-NOT-EXECUTED
require no successor execution already consumed that PNE basis
```

### Common

```text
ordinal = current tail ordinal + 1
executionId = deriveId("execution.v1", W, ordinal)

insert execution
insert exact creation basis
```

## 8. Retry hard limits

These are v1 runner safety limits:

```text
attemptOrdinal starts at 1

maximum total historical Executions per WorkItem = 5

maximum automatic technical-failure replacement Executions = 2

maximum protocol-invalid replacement Executions = 1

maximum consecutive PROVEN-NOT-EXECUTED replacement Executions = 2
```

Provider/transport retries below one `llm-runtime` call do not count.

Operator-authorized replacement does not create a protocol retry authorization
but still counts against the absolute total of five Executions.

No generic operator `"retry anyway"` path exists.

When a limit is exhausted, another `AuthorizeExecutionV1` is invalid.

The owning M5/M8 path must instead establish the exact required operational
blocker.

M2 never manufactures that blocker merely because it rejected an invalid
proposal.

## 9. Arm algorithm

For Execution `E`:

```text
require E exists
require E is the current tail for its WorkItem
require E has no Arm fact
require E has no terminal outcome
require E has no terminal recovery resolution
require E's WorkItem has at least one outstanding source obligation
require no semantic terminal prevents new side effects
require no outstanding OperationalBlocker exists

require mutation.ownershipGeneration == current WriteAuthorityRef.generation
require mutation base revision == exact current revision

require every revalidationBasis ArtifactRef is intact
require every dispatchEvidence ArtifactRef is intact
require recoveryCapability artifact is intact when non-null
```

For an `Execution E` whose `WorkItem W` is a repository-control publication
WorkItem, M2 additionally requires:

```text
snapshot.publicationIntent != null

let I = snapshot.publicationIntent

W is the exact WorkItem co-admitted with I

E.workItemId == W.workItemId

W.candidateId == snapshot.currentCandidate.candidateId

I.candidateId == snapshot.currentCandidate.candidateId

I.qualificationId ==
    snapshot.gateQualification.qualificationId

the exact publication obligation co-admitted with I is outstanding

W.operation passes the future M7 pure binding extractor for exact I

the Arm revalidation basis contains the exact future-M7-validated publication
revalidation binding required for I

that binding names:
    exact I
    exact I.transition.target
    exact I.transition.predecessor
    exact I.transition.successor
```

M2 does not independently interpret remote Git state.

M7 establishes repository-domain revalidation evidence.

M2 validates that the exact accepted M7 binding is current, structurally bound
to I, and supplied to the exact current-intent WorkItem/Execution.

The future M7 NIB-M must close the exact revalidation artifact schema and pure
binding-validation contract before GREEN.

If `W` belongs to a historical PublicationIntent instead of the exact projected
current one:

```text
ArmExecutionDispatchV1 is INVALID_MUTATION
```

No Arm fact is written.

No uncertainty is created.

No M8 recovery is invoked because the external-effect permission boundary was
never crossed.

On commit:

```text
store Arm fact
store exact mutation artifact as dispatchIntent
```

After commit, the snapshot/integrity M2 brief must reconstruct:

```ts
ArmedExecutionDispatchRef {
  execution: E,
  workItem: W,
  dispatchIntent: exact Arm mutation ArtifactRef,
  dispatchEvidence,
  recoveryCapability,
}
```

and until terminal disposition:

```text
E ∈ snapshot.unresolvedExecutions
```

No later failure to invoke the executor reverses the Arm fact.

## 10. Outcome algorithm

Direct outcome requires:

```text
Arm exists
no ExecutionProgressionSupersessionRef exists for E
no direct terminal outcome exists
no terminal recovery resolution exists
no explicit uncertainty enrichment has transferred disposition to M8
outcome.execution == exact E
```

`captured` and `technical-failure` are mutually exclusive.

Admission terminalizes the execution.

For cognitive captured outcomes, terminal execution does not imply protocol
qualification.

M6/M5 classification follows separately.

## 11. Uncertainty enrichment algorithm

Require:

```text
Arm exists
execution remains unresolved
no ExecutionProgressionSupersessionRef exists for E
no terminal recovery resolution exists

unresolved.execution == armed execution
unresolved.workItem == exact authoritative WorkItem
unresolved.dispatchIntent == exact Arm mutation ArtifactRef

unresolved.dispatchEvidence contains every exact Arm dispatchEvidence item
without modification

any appended evidence is intact

if terminalOutcome != null:
    terminalOutcome.execution == same E
```

At most one executor-origin uncertainty enrichment may be admitted for one
Execution.

Later M8 reconciliation facts use `AdmitExecutionRecoveryV1`.

## 12. Recovery algorithm

### PROVEN-NOT-EXECUTED

```text
require E armed and unresolved
no ExecutionProgressionSupersessionRef exists for E
require M8 resolution binds exact E
append terminal recovery resolution
E leaves unresolved projection
```

It establishes one possible creation basis for one successor execution.

### PROVEN-COMPLETED

```text
require E armed and unresolved
no ExecutionProgressionSupersessionRef exists for E
require recoveredOutcome.execution == E
append terminal recovery resolution
append recovered terminal outcome provenance
E leaves unresolved projection
```

When the recovered outcome belongs to repository publication and
`recoveredOutcome.kind = "captured"`, that exact captured result is thereafter
the authoritative `CapturedExecutionResult` that may be supplied in a
`PublicationObservationQualificationRequest`.

For publication qualification, a recovered captured result may produce
`confirmed` or `blocked`, but it may never produce `not-applied`. M2 rejects a
`not-applied` mutation whose result was introduced by `AdmitExecutionRecoveryV1`;
M1 must fail the recovered `not-applied` path before submitting that mutation.

No second direct-outcome admission is required or permitted for the same
Execution.

Captured and technical-failure recovered outcomes remain distinct.

### UNRESOLVABLE

```text
require E armed and unresolved
no ExecutionProgressionSupersessionRef exists for E
require blocker.executionId == E
append terminal UNRESOLVABLE resolution
append blocker
E leaves unresolved projection
blocker remains outstanding
```

### Pending-policy exhaustion

```text
require lastPending binds E
no ExecutionProgressionSupersessionRef exists for E
require lastPending recovery capability is exact
append pending observation
append exact operational blocker
E remains unresolved
```

A later mechanical recovery may both establish a terminal recovery resolution
and dispose the exact pending blocker in one StateRevision.

## 13. Cognitive-attempt admission

For every supplied `CognitiveAttemptValidationResult`:

```text
execution exists
no ExecutionProgressionSupersessionRef exists for E
execution is cognitive WorkItem execution
captured result is already authoritative
validation capturedResult equals exact authoritative capture
executionRequest.dispatch.execution == E
executionRequest.dispatch.workItem == exact W
prompt/packet/campaign/protocol/role/profile bindings are exact
validation evidence artifacts exist
at most one authoritative classification exists for E
```

For `protocol-invalid`:

```text
role ∈ { initial-reviewer, challenge }
protocolErrors non-empty
qualified classification does not exist
```

If delta establishes a retry authorization from this result, the exact
validation evidence and retry authorization are admitted in the same revision.

For `qualified`:

```text
protocolErrors = []
no retry authorization may cite E
E must be current WorkItem tail
no later Execution may exist
```

The delta must contain the complete schema-v3 receipt EvidenceRef required by
the M5 brief.

M2 validates its structural binding through the accepted M5 receipt-artifact
schema.

There is no durable state:

```text
qualified classification
without its required complete receipt admission
```

## 14. Obligations

One obligation has zero or one terminal disposition.

```text
no disposition → outstanding
satisfied      → terminal satisfied
superseded     → terminal superseded
```

`satisfied` and `superseded` are mutually exclusive.

For supersession:

```text
replacementObligationIds may be empty
replacement IDs must be duplicate-free
every replacement exists or is co-admitted
all belong to same run
source cannot replace itself
resulting complete supersession graph must remain acyclic
```

Outstandingness is direct, not transitive:

```text
outstanding(O) = O has no direct disposition
```

Disposition never automatically:

```text
disposes a blocker
cancels an armed execution
satisfies another obligation
```

## 15. WorkItems

Require:

```text
sourceObligationIds length >= 1
duplicate-free
all source obligations exist/co-admitted
all belong to same run
candidate exists
reviewCampaign exists when non-null
operation and inputRefs exist
executor is exact closed WorkExecutor
```

A WorkItem may source multiple obligations.

One obligation may source multiple WorkItems.

A new Execution is forbidden when every source obligation has a disposition.

An already-armed Execution remains subject to outcome/recovery closure even if
all source obligations are later disposed.

### Publication Intent WorkItems

A PublicationIntent WorkItem is created only through
`EstablishPublicationIntentV1`.

It is never created through:

```text
EstablishReviewCampaignBundleV1
AdmitAssuranceLedgerDeltaV1
generic orchestration invention
```

Exactly one publication WorkItem exists per PublicationIntent.

Exactly one publication obligation exists per PublicationIntent.

Its `sourceObligationIds` contains only that exact publication obligation.

When a later safe publication intent supersedes the prior publication
obligation, any authorized-but-unarmed Execution of the old WorkItem remains
historical and becomes non-dispatchable under the Arm current-intent check.

Obligation supersession does not cancel or manufacture an outcome for an
already-armed Execution.

## 16. Blockers

M2 persists blockers append-only.

A blocker is outstanding iff no internal blocker disposition exists.

Semantic blockers cannot receive same-run disposition.

Operational blockers may be disposed only by:

```text
exact accepted OperatorResolution
or
exact mechanically superseding recovery allowed by its causal blocker kind
```

There is no generic `ResolveBlockerV1`.

Blocker disposition never satisfies its obligation automatically.

Operational-blocker identity is governed by the accepted M8-B
operational-boundary contract.

M2 recognizes exactly two policies:

```text
non-recovery producer blocker
→ occurrence identity
→ includes immutable producer causeDescriptor.sha256
→ includes baseStateRevision

M8 recovery blocker
→ stable causal identity
→ excludes StateRevision and reconciliation episode
```

M2 must not inject `StateRevision`, ownership generation, episode identity,
timestamp, or another occurrence discriminator into a recovery blocker ID.

M2 validates the exact supplied blocker identity; it does not create another
identity policy.

## 17. Semantic terminality matrix

Once any SemanticBlocker has been admitted:

```text
semanticProgressionTerminal = true
```

Forbidden afterward:

```text
new ReviewCampaign
new ordinary WorkItem
new candidate repair
new qualification
new publication intent
Gate A ready
new not-yet-armed semantic side effect
```

Still admissible when causally required to close prior effects:

```text
outcome of already-armed Execution
uncertainty enrichment for already-armed Execution
recovery facts
operational blocker arising from that recovery
operator resolution needed for those operational facts
required evidence/history closure
```

## 18. Gate A ready preconditions

`EstablishGateAReadyV1` is accepted only when all hold:

```text
semanticProgressionTerminal == false
outstanding blockers == []
outstanding obligations == []

exact projected GateAQualification exists
exact projected PublicationConfirmation exists

one admitted post-publication MechanicalValidationResult exists where:
    passed == true
    candidateId == qualification.candidateId
    publicationConfirmationId == exact confirmation
    target == exact confirmed target
    validatedAuthority == exact confirmed successor authority
```

After Gate A ready fact exists, no later campaign-state mutation is accepted.

Read-only load and ownership acquisition remain permitted.

## 19. Example

Cognitive WorkItem `W1` receives:

```text
E1 attemptOrdinal 1
```

E1 is armed, returns a completed response, and is admitted as captured.

M6 classifies it:

```text
protocol-invalid
```

M5 returns one retry authorization `R1`.

One `AdmitAssuranceLedgerDeltaV1` revision atomically admits:

```text
M6 classification(E1)
validation evidence
R1
```

M1 later requests:

```ts
{
  kind: "authorize-execution",
  workItemId: "W1",
  basis: {
    kind: "protocol-retry",
    retryAuthorizationId: "R1",
  },
}
```

M2 creates:

```text
E2
attemptOrdinal = 2
creation basis = R1
```

R1 is now consumed because E2 exists.

E2 is armed.

The process crashes before M4 returns.

On restart E2 is already unresolved from the Arm fact.

M8 proves the provider never executed E2:

```text
PROVEN-NOT-EXECUTED(E2)
```

M2 admits the recovery.

A new authorization creates E3 from the exact PNE basis.

E3 is armed, captured, and M6 classifies it `qualified`.

The M5 delta admits in one revision:

```text
qualified(E3)
complete receipt for W1:
    attempts = [E1, E3]
required EvidenceRef
resulting ledger products
```

E2 is absent from the receipt attempt list because it never reached the
cognitive call boundary.

Its runner history remains authoritative.

## 20. Edge cases

* Wrong `expectedStateRevision`: return `stale-state`; no facts inserted.
* Wrong generation: return `ownership-lost`; no facts inserted.
* Same logical ID with different payload: invalid mutation.
* Exact duplicate mutation against current revision with no new fact:
  `NO_NEW_FACTS`.
* Retry authorization already consumed: invalid mutation.
* PNE basis already consumed: invalid mutation.
* WorkItem has an authorized-not-dispatched tail: no successor may be created.
* Arm attempted twice: invalid mutation.
* Outcome without Arm: invalid mutation.
* Executor uncertain enrichment changes WorkItem or dispatch intent: invalid.
* Qualified cognitive result accompanied by retry authorization: invalid.
* Protocol-invalid result for an unvalidated cognitive role: invalid.
* Supersession introduces cycle: invalid.
* Semantic blocker disposition proposed: invalid.
* Gate A ready with one outstanding obligation: invalid.
* Gate A ready with old/unbound post-publication validation: invalid.
* Operator resolution attempts replacement after absolute Execution cap:
  invalid.
* Already-armed execution may still close after semantic terminality.
* Artifact reference exists in JSON but CAS bytes fail verification:
  integrity/invocation failure before commit.

## 21. Constraints

* One successful mutation equals one StateRevision.
* One StateRevision may establish multiple related facts atomically.
* No mutation updates or deletes history.
* M2 does not schedule WorkItems.
* M2 does not infer M3 currentness.
* M2 does not reclassify M6 cognitive results.
* M2 does not derive M5 semantic conclusions.
* M2 does not derive M8 recovery classifications.
* No authorization is represented by a mutable consumed flag.
* Arm is irreversible.
* External-effect uncertainty is conservative after Arm.
* No execution branch may fork from a non-tail Execution.
* No campaign mutation may bypass ownership generation and StateRevision CAS.

## 22. Integration

M1 always constructs and seals one exact mutation artifact before calling:

```ts
const committed = await campaignState.commitAuthoritativeMutation({
  runId,
  authority,
  expectedStateRevision: snapshot.stateRevision,
  mutation: mutationRef,
});
```

On:

```text
committed
```

M1 discards its prior snapshot and uses only the returned snapshot.

On:

```text
stale-state
ownership-lost
```

M1 does not replay the external effect that motivated the mutation.

It reloads or re-enters the appropriate orchestration/recovery path.

For repository publication, the required admission order is:

```text
conditional-ref-update:
    Arm exact publication Execution
    ↓
    obtain direct or recovered CapturedExecutionResult
    ↓
    make that CapturedExecutionResult authoritative
    ↓
    M7 qualify_publication_observation({ kind: executed-publication, ... })
    ↓
    if result == not-applied:
        require the exact result was introduced directly through
            AdmitExecutionOutcomeV1
        reject recovered-origin results as INVALID_MUTATION
    ↓
already-current:
    EstablishPublicationIntentV1
    ↓
    obtain one fresh exact read-only target observation
    ↓
    M7 qualify_publication_observation({ kind: already-current, ... })
    ↓
AdmitPublicationObservationQualificationV1(request, result)
↓
if confirmed:
    PublicationConfirmationRef + PublishedRepositoryViewRef
    + exact publication-obligation satisfied disposition in the same revision
if not-applied:
    PublicationNonApplicationRef only
    + no confirmation/view/disposition
if blocked:
    exact OperationalBlocker
```

A `not-applied` result is valid only for the executed-publication request kind.
M1 may not commit a bare publication confirmation/view pair or a confirmation
whose exact publication obligation remains outstanding.

The snapshot/integrity M2 brief performs all resulting-state reconstruction and
invariant validation before SQLite commit.
