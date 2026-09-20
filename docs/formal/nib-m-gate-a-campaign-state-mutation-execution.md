---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-09-20"
step_id: 2
id: NIB-M-GATE-A-CAMPAIGN-STATE-MUTATION-EXECUTION
version: "1.0.2"
scope: gate-a-campaign-runner/campaign-state/mutation-execution
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Campaign State — Mutation Admission and Execution Lifecycle

## 1. Status, authority, and purpose

This document is one of three active Module Briefs that together close M2
`campaign-state` for the Gate A hostile-review campaign runner.

It consumes `NIB-S-GATE-A-CAMPAIGN-RUNNER` version `6.0.2`.

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
  readonly baselineAuthority: RepositoryAuthorityRef;
  readonly publicationTarget: RepositoryPublicationTargetRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly rootObligationDisposition: Extract<
    ObligationDispositionRef,
    { readonly kind: "satisfied" }
  >;
}
```

The disposition must name the exact bootstrap root obligation.

This mutation is accepted at most once per run.

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
}
```

At most one effective publication intent may exist for one exact
candidate/qualification transition.

Historical intents remain retained.

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

Let:

```text
Q = request
E = Q.executionResult.execution
W = exact authoritative WorkItem for E
I = Q.intent
C = Q.candidate
```

Before either result branch is admitted, M2 requires:

```text
E exists

E has a successful Arm fact

Q.executionResult equals one exact already-authoritative
CapturedExecutionResult for E

that captured result was admitted either:
    directly through AdmitExecutionOutcomeV1
    or
    as the captured recovered outcome of a PROVEN-COMPLETED
    AdmitExecutionRecoveryV1

W exists

W.executor == "repository-control"

W.candidateId == C.candidateId

I equals one exact admitted PublicationIntentRef

C equals one exact authoritative CandidateRevisionRef

C.candidateId == I.candidateId

I.qualificationId equals the exact qualification governing publication
```

M2 must additionally verify that the repository-control WorkItem owning `E` is
the exact PublicationIntent WorkItem for `I`.

The exact runtime-validated M7 publication operation/input representation and
binding extractor belong to the M7 NIB-M.

The M7 NIB-M must close that representation before GREEN.

The coding agent may not infer that binding from repository-control executor
identity alone.

For:

```text
result.kind = "confirmed"
```

M2 requires:

```text
result.confirmation.publicationIntentId
    == I.publicationIntentId

result.confirmation.candidateId
    == C.candidateId

result.confirmation.transition
    == I.transition

result.publishedView.publicationConfirmationId
    == result.confirmation.publicationConfirmationId

result.publishedView.candidateId
    == C.candidateId

result.publishedView.target
    == I.transition.target

result.publishedView.authority
    == I.transition.successor
    by exact commit SHA and tree SHA
```

M2 then atomically appends:

```text
the exact PublicationObservationQualification request/result admission basis
the exact PublicationConfirmationRef
the exact PublishedRepositoryViewRef identity descriptor
```

in one StateRevision.

A `PublicationConfirmationRef` may never become authoritative from a bare
confirmation/view pair.

For:

```text
result.kind = "blocked"
```

M2 requires:

```text
result.blocker.kind == "operational"

result.blocker.executionId
    == E.executionId

result.blocker references one exact applicable publication obligation
```

M2 then atomically appends:

```text
the exact PublicationObservationQualification request/result admission basis
the exact OperationalBlocker
```

and appends no `PublicationConfirmationRef` or `PublishedRepositoryViewRef`.

A captured publication result by itself never establishes publication
confirmation.

A blocked publication qualification is a known M7 domain result and is not an
M8 execution-uncertainty classification.

### 5.15 Operator resolution

M2 accepts only an M8-validated state effect.

```ts
type OperatorResolutionStateEffect =
  | {
      readonly kind: "resolve-blocker-only";
    }
  | {
      readonly kind: "resolve-blocker-and-replace-execution";
      readonly priorExecutionId: ExecutionId;
    };

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

For replacement, M2 atomically:

```text
admits operator resolution
disposes exact target blocker
records prior Execution supersession
creates exactly one successor Execution
records creation basis = operator-replacement
```

in one StateRevision.

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
require M8 resolution binds exact E
append terminal recovery resolution
E leaves unresolved projection
```

It establishes one possible creation basis for one successor execution.

### PROVEN-COMPLETED

```text
require E armed and unresolved
require recoveredOutcome.execution == E
append terminal recovery resolution
append recovered terminal outcome provenance
E leaves unresolved projection
```

When the recovered outcome belongs to repository publication and
`recoveredOutcome.kind = "captured"`, that exact captured result is thereafter
the authoritative `CapturedExecutionResult` that may be supplied in a
`PublicationObservationQualificationRequest`.

No second direct-outcome admission is required or permitted for the same
Execution.

Captured and technical-failure recovered outcomes remain distinct.

### UNRESOLVABLE

```text
require E armed and unresolved
require blocker.executionId == E
append terminal UNRESOLVABLE resolution
append blocker
E leaves unresolved projection
blocker remains outstanding
```

### Pending-policy exhaustion

```text
require lastPending binds E
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

Operational blocker identity represents an exact episode and includes the
derivation base revision in its identity tuple.

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
Arm exact publication Execution
↓
obtain direct or recovered CapturedExecutionResult
↓
make that CapturedExecutionResult authoritative
↓
M7 qualify_publication_observation(request)
↓
AdmitPublicationObservationQualificationV1(request, result)
↓
if confirmed:
    PublicationConfirmationRef + PublishedRepositoryViewRef
if blocked:
    exact OperationalBlocker
```

M1 may not commit a bare publication confirmation/view pair.

The snapshot/integrity M2 brief performs all resulting-state reconstruction and
invariant validation before SQLite commit.
