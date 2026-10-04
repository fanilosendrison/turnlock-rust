---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-04"
step_id: 2
id: NIB-M-GATE-A-ASSURANCE-LEDGER-CAMPAIGN-WORK-EXECUTION-RECEIPT
version: "1.0.0"
scope: gate-a-campaign-runner/assurance-ledger/campaign-work-execution-receipt
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Assurance Ledger — Campaign Work and Execution Receipt

## 1. Status, authority, and purpose

Implement M5-A `assurance-ledger / campaign-work / execution-receipt` according
to this active Module Brief.

Consume exactly:

```text
NIB-S-GATE-A-CAMPAIGN-RUNNER 9.1.2

NIB-M-GATE-A-CAMPAIGN-AUTHORITY 4.0.0

NIB-M-GATE-A-CAMPAIGN-STATE-MUTATION-EXECUTION 6.0.0

NIB-M-GATE-A-CAMPAIGN-STATE-SNAPSHOT-INTEGRITY 5.0.0

NIB-M-GATE-A-COGNITIVE-EXECUTION-CAPTURE 1.1.3

NIB-M-GATE-A-COGNITIVE-EXECUTION-RECOVERY-OBSERVATION 1.0.2

NIB-M-GATE-A-RECOVERY-OPERATOR-BOUNDARY 2.0.11

DC-PI-M4-GATE-A-COGNITIVE-EXECUTION 1.1.3

ADR-045
ADR-046
ADR-047
ADR-048
ADR-049
ADR-053
ADR-054

gate-a-campaign-protocol-v6

execution-receipt schema 3.0
```

Treat this brief as implementation-construction authority only. It creates no:

```text
TURNLOCK product semantic
hostile-review protocol semantic
ADR
TL-INV
TL-CLAIM
new cross-module product category
```

Do not implement production code from this brief until the repository's GREEN
boundary authorizes implementation.

## 2. Responsibility boundary

M5-A owns exactly:

```text
protocol-derived reviewer-acquisition target obligation construction
selected-initial-reviewer obligation construction
selected-initial-reviewer WorkItem construction
M4 CognitiveExecutionOperationV1 construction inputs
M4 operation sealing invocation
first-round selected-candidate materialization validation
later-round deterministic reviewer acquisition
effective-identity acquisition-progress reconstruction
cognitive protocol retry admissibility
ExecutionRetryAuthorizationRef construction
retry-exhaustion assurance-domain cause construction
eligible reviewer-pool exhaustion cause construction
provider-reported-identity-unavailable cause construction
initial-reviewer schema-v3 receipt attempt selection
initial-reviewer schema-v3 receipt assembly
receipt sealing
receipt EvidenceRef construction
selected-reviewer obligation satisfaction
reviewer-acquisition-target satisfaction
restart/idempotence for all M5-A products
```

M5-A does not own:

```text
first-round candidate selection
M2 state writes
M4 execution
M6 validation/classification
M8-B OperationalBlocker identity
Operator Action Request construction
finding normalization
finding adjudication
materiality/refutation
resolution qualification
RepairIntent
DecisionRequest
semantic blockers
assurance repository projection
final review-record construction
CandidateReviewReadiness
Gate A qualification
repository mutation
```

Keep those responsibilities with their accepted owners:

```text
M1 / M2 / M4 / M6 / M8-B / M5-B / M5-C / M5-D / M7
```

Do not merge M5-A responsibility with a sibling M5 responsibility.

## 3. Mandatory identity-level distinctions

Preserve explicitly:

```text
Obligation
!=
WorkItem
!=
runner Execution
!=
logical hostile-review execution
!=
protocol attempt
!=
M4 cognitive call
!=
provider/transport attempt
```

For one selected initial reviewer, require exactly:

```text
one selected-reviewer Obligation
=
one required logical reviewer work item

one WorkItem
=
one logical hostile-review execution
=
one schema-v3 receipt.execution_id

runner Executions
=
protocol attempts of that same logical execution

one runner Execution
=
one M4 cognitive call

provider retries
=
internal transport attempts below that call
```

Never collapse or exchange identities across these levels.

## 4. M5-A construction interfaces

Define exactly:

```ts
interface ConstructInitialReviewerCampaignWorkRequestV1 {
  readonly campaign: ReviewCampaignRef;

  readonly prerequisiteBasis:
    ReviewCampaignPrerequisiteBasisRefV1;

  readonly selectedFirstRoundCandidates:
    readonly GateAReviewerAcquisitionCandidateV1[];
}

interface ConstructInitialReviewerCampaignWorkResultV1 {
  readonly obligations: readonly ObligationRef[];
  readonly workItems: readonly WorkItemRef[];
}
```

Expose:

```ts
construct_initial_reviewer_campaign_work(
  request: ConstructInitialReviewerCampaignWorkRequestV1
): Promise<ConstructInitialReviewerCampaignWorkResultV1>
```

This operation must not select the first round. Validate that M1 supplied the
exact expected deterministic first round.

Define the M5-A contribution to the future composite M5 exactly:

```ts
interface M5ACampaignWorkPreparationV1 {
  readonly expectedStateRevision: StateRevision;

  readonly evidenceToEstablish:
    readonly EvidenceRef[];

  readonly obligationDispositions:
    readonly ObligationDispositionRef[];

  readonly obligationsToAdd:
    readonly ObligationRef[];

  readonly workItemsToAdd:
    readonly WorkItemRef[];

  readonly executionRetryAuthorizationsToEstablish:
    readonly ExecutionRetryAuthorizationRef[];

  readonly operationalBlockerRequests:
    readonly AssuranceOperationalBlockerRequest[];
}
```

Expose:

```ts
prepare_campaign_work_contribution(
  request: AssuranceDerivationRequest
): Promise<M5ACampaignWorkPreparationV1>
```

Do not define how M5-A, M5-B, M5-C, and M5-D contributions are merged into the
ultimate `AssuranceLedgerPreparation`. Keep the NIB-S public authority:

```text
prepare_complete_delta
finalize_complete_delta
```

Close complete composition only after all four M5 Module Briefs exist.

## 5. Obligation-definition artifacts

Define exactly:

```ts
interface GateAAssuranceLedgerObligationDefinitionV1 {
  readonly schema:
    "gate-a-assurance-ledger-obligation-definition.v1";

  readonly kind:
    | "reviewer-acquisition-target"
    | "selected-initial-reviewer";
}
```

The two constant values are exactly:

```json
{
  "schema": "gate-a-assurance-ledger-obligation-definition.v1",
  "kind": "reviewer-acquisition-target"
}
```

and:

```json
{
  "schema": "gate-a-assurance-ledger-obligation-definition.v1",
  "kind": "selected-initial-reviewer"
}
```

Seal each definition exactly:

```text
construct exact value
runtime validate
canonical runner JSON serialize
CampaignArtifactStore.sealRunnerArtifact({
    exact bytes,
    mediaType: "application/json"
})
require returned repositoryPath == null
require mediaType == application/json
verify returned ArtifactRef
return exact ref
```

A memory cache is permitted. The cache is never authority.

After restart, require:

```text
same bytes
→ same CAS-backed ArtifactRef
```

## 6. Reviewer-acquisition target obligation

For basis `B`, set:

```text
runId = B.reviewContext.runId
```

Derive the exact identity:

```text
deriveId(
  "assurance-ledger-reviewer-acquisition-target-obligation.v1",
  B.reviewContext.runId,
  B.reviewCampaignId,
  decimal(B.minimumIndependentReviewers),
  B.acquisitionMode,
  targetDefinition.sha256
)
```

Construct exactly:

```ts
ObligationRef {
  obligationId,

  runId:
    B.reviewContext.runId,

  candidateId:
    B.candidateId,

  reviewCampaignId:
    B.reviewCampaignId,

  definition:
    exact reviewer-acquisition-target definition
}
```

The acquisition target has no WorkItem. Never construct:

```text
target WorkItem
round WorkItem
collision WorkItem
deficit WorkItem
retry WorkItem
```

## 7. Selected initial-reviewer obligation

For exact candidate `A`, require full structural equality with exactly one member
of `B.reviewerAcquisitionCandidates`. Never reconstruct `A` from `profileId`.

Derive exactly:

```text
deriveId(
  "assurance-ledger-selected-initial-reviewer-obligation.v1",
  B.reviewContext.runId,
  B.reviewCampaignId,
  A.profileId,
  selectedReviewerDefinition.sha256
)
```

Construct:

```ts
ObligationRef {
  obligationId,

  runId:
    B.reviewContext.runId,

  candidateId:
    B.candidateId,

  reviewCampaignId:
    B.reviewCampaignId,

  definition:
    exact selected-initial-reviewer definition
}
```

Do not include in the identity:

```text
round
Execution
retry
effective identity
providerModel
StateRevision
timestamp
```

## 8. Selected-reviewer WorkItem identity

For selected-reviewer obligation `O`, derive exactly:

```text
workItemId =
deriveId(
  "assurance-ledger-selected-initial-reviewer-work-item.v1",
  O.obligationId
)
```

Require the final M0 renderer for this domain to produce a value satisfying the
hostile-review lexical contract for logical execution identity:

```text
^EXEC-[A-Z0-9][A-Z0-9-]*$
```

Do not change identity inputs to satisfy the rendering. Keep collision-safe,
domain-separated byte framing and rendering in final M0 closure.

Require:

```text
same obligation
→ same WorkItemId

same WorkItemId + incompatible payload
→ ASSURANCE-HISTORY-INTEGRITY-FAILURE
```

## 9. Cognitive operation construction

For basis `B` and exact selected candidate `A`, construct exactly:

```ts
CognitiveExecutionOperationV1 {
  schema:
    "gate-a-cognitive-execution-operation.v1",

  reviewContext:
    B.reviewContext,

  role:
    "initial-reviewer",

  reviewerProfileId:
    A.profileId,

  reviewerAcquisitionCandidate:
    A,

  prompt:
    B.initialReviewerExecutionInputs.prompt,

  packet:
    B.initialReviewerExecutionInputs.packet
}
```

Require exact bindings:

```text
operation.reviewContext
==
B.reviewContext

operation.reviewerAcquisitionCandidate
==
exact A

operation.prompt
==
B.initialReviewerExecutionInputs.prompt

operation.packet
==
B.initialReviewerExecutionInputs.packet
```

Invoke:

```text
M4.sealOperation(exact operation)
```

Do not serialize the M4 operation in M5-A.

## 10. Exact reviewer WorkItem

Construct exactly:

```ts
WorkItemRef {
  workItemId,

  runId:
    B.reviewContext.runId,

  candidateId:
    B.candidateId,

  reviewCampaignId:
    B.reviewCampaignId,

  sourceObligationIds: [
    selectedReviewerObligation.obligationId
  ],

  executor:
    "cognitive-execution",

  operation:
    exact M4-sealed operation ArtifactRef,

  inputRefs: [
    B.initialReviewerExecutionInputs.prompt,
    B.initialReviewerExecutionInputs.packet
  ]
}
```

`sourceObligationIds` must not contain the reviewer-acquisition-target
obligation. The target controls global acquisition. The selected-reviewer
obligation controls execution of the exact reviewer.

## 11. One constructor for first and later rounds

Define one internal helper only:

```text
construct_selected_initial_reviewer_work(B, A)
```

Produce exactly:

```text
selected-reviewer Obligation
M4 CognitiveExecutionOperationV1
M4-sealed operation
WorkItem
```

Use the same helper for first and later rounds. Do not introduce:

```text
first-round constructor
later-round constructor
roundNumber
roundId
```

## 12. First-round M1 boundary

In `construct_initial_reviewer_campaign_work`, require:

```text
campaign == B.reviewContext.campaign

campaign.reviewCampaignId == B.reviewCampaignId

campaign provenance is runner-produced

campaign candidate/S/P bindings == exact B bindings
```

Compute purely:

```text
expectedFirstRound =
derive_acquisition_round(
  B,
  E = empty set,
  alreadySelectedProfiles = empty set
)
```

Require full structural equality and identical order:

```text
request.selectedFirstRoundCandidates
==
expectedFirstRound
```

This recomputation validates M1 selection. It does not transfer ownership of
first-round selection to M5.

Return exactly:

```text
obligations =
[
  acquisitionTargetObligation,
  ...selectedReviewerObligations
      in exact selectedFirstRoundCandidates order
]

workItems =
[
  ...selectedReviewerWorkItems
      in exact selectedFirstRoundCandidates order
]
```

## 13. Pure acquisition-round function

Define conceptually:

```text
derive_acquisition_round(
  B,
  E,
  alreadySelectedProfiles
)
```

Compute:

```text
N = B.minimumIndependentReviewers

deficit = N - |E|
```

When `deficit <= 0`, return `[]`.

Otherwise traverse `B.reviewerAcquisitionCandidates` in exact retained order.
Ignore every profile already in `alreadySelectedProfiles`.

For a pinned candidate, define:

```text
K =
(
  A.provider,
  A.requestModel
)
```

Skip it when:

```text
K ∈ E

OR

K ∈ pinnedReservedInThisRound
```

Otherwise select `A` and add `K` to the ephemeral round reservation.

For a provider-reported candidate:

```text
do not pre-collapse
do not guess identity
```

Stop when:

```text
selectedThisRound.length == deficit
```

or when the pool is exhausted. Permit no finding, content, timing, or scheduler
input.

## 14. Selected-profile reconstruction

Do not reconstruct selection from WorkItem history.

For each candidate `A` in `B`, recompute:

```text
expectedSelectedObligationId(A)
```

Treat `A` as selected if and only if the exact selected-initial-reviewer
`ObligationRef` is present in Authoritative History with that identity and exact
payload.

Use the corresponding WorkItem only as an integrity control. Require:

```text
for every selected A:
    exact expected WorkItem exists

for every unselected A:
    corresponding selected-reviewer WorkItem does not exist
```

Map each impossible case to `ASSURANCE-HISTORY-INTEGRITY-FAILURE`:

```text
obligation exists / WorkItem missing
WorkItem exists / obligation missing
same logical ID / incompatible payload
```

## 15. Receipt Evidence identity lookup

For expected selected-reviewer WorkItem `W`, derive:

```text
receiptEvidenceId =
deriveId(
  "assurance-ledger-execution-receipt-evidence.v1",
  W.runId,
  W.workItemId
)
```

A complete receipt exists authoritatively only when an exact `EvidenceRef` with
that `evidenceId` exists and its artifact validates as the exact schema-v3
receipt of `W`.

Map the same EvidenceId with another artifact to
`ASSURANCE-HISTORY-INTEGRITY-FAILURE`.

## 16. Reviewer-acquisition replay

Define exactly:

```ts
type ReviewerAcquisitionProgressV1 =
  | {
      readonly kind: "await-selected-work";
    }
  | {
      readonly kind: "select-next-round";
      readonly candidates:
        readonly GateAReviewerAcquisitionCandidateV1[];
    }
  | {
      readonly kind: "target-established";
    }
  | {
      readonly kind: "pool-exhausted";
    };
```

Add no `roundNumber`, `roundId`, `storedDeficit`, or `currentRound` field.

Apply exactly:

```text
E = empty effective-identity set

selectedBefore = empty ordered candidate list

loop:

    deficit =
        B.minimumIndependentReviewers - |E|

    if deficit <= 0:
        require no selected candidate exists outside selectedBefore
        return target-established

    R =
        derive_acquisition_round(
            B,
            E,
            selectedBefore profile IDs
        )

    if R == []:
        require no selected candidate exists outside selectedBefore
        return pool-exhausted

    determine selected-obligation presence for every A in R

    if no A in R is selected:
        require no selected candidate exists outside selectedBefore
        return select-next-round(R)

    if only a strict subset of R is selected:
        ASSURANCE-HISTORY-INTEGRITY-FAILURE

    require exact WorkItem exists for every A in R

    if any selected candidate exists outside
       selectedBefore + R
       while any WorkItem in R lacks a complete receipt:
        ASSURANCE-HISTORY-INTEGRITY-FAILURE

    if any WorkItem in R lacks a complete qualified receipt:
        return await-selected-work

    for every A/W in R in exact round order:
        verify exact receipt
        extract exact effective identity:
            (
              resolved_identity.provider,
              resolved_identity.model_version
            )
        add to E as a set

    append R to selectedBefore

    continue
```

A WorkItem with an operational blocker, recovery blocker, retry exhaustion, or
provider identity unavailable but no complete receipt still produces
`await-selected-work` and no next round. The top-level runner stops automatic
campaign progression through the blocker path. This is never profile fallback.

## 17. Later-round construction

When replay returns `select-next-round(R)`, construct for each candidate in `R`:

```text
exact selected-reviewer Obligation
exact selected-reviewer WorkItem
```

Use the Section 11 helper. Emit:

```text
obligationsToAdd
=
reviewer obligations in exact R order

workItemsToAdd
=
corresponding WorkItems in exact R order
```

Do not add another target obligation. Derive a later round only from the exact
authoritative input snapshot.

Never admit final receipts of a previous round and derive a next round from
those not-yet-authoritative receipts in one phase transition. Enforce:

```text
admit receipts
reload authoritative snapshot
then derive later round
```

## 18. Acquisition-target satisfaction

Satisfy the acquisition target only when the exact input snapshot establishes:

```text
effective identity count >= N

AND

every selected reviewer WorkItem has its complete qualified receipt
```

Construct:

```ts
{
  kind: "satisfied",
  obligationId:
    exact target obligation ID,

  basisEvidenceIds:
    all selected-reviewer receipt EvidenceIds
    in reconstructed acquisition-selection order,

  basisArtifacts:
    corresponding receipt artifacts
    in the same order
}
```

Require no duplicates. Never produce `superseded` for this target.

If an identical target disposition is already authoritative, emit nothing. If
an incompatible disposition exists, fail with
`ASSURANCE-HISTORY-INTEGRITY-FAILURE`.

## 19. Selected-reviewer satisfaction

When a complete receipt for `W` is established, construct:

```ts
{
  kind: "satisfied",
  obligationId:
    exact selected-reviewer obligation,

  basisEvidenceIds: [
    receiptEvidence.evidenceId
  ],

  basisArtifacts: [
    receiptEvidence.artifact
  ]
}
```

Propose a new receipt `EvidenceRef` and selected-reviewer satisfaction atomically
in the same M5-A contribution.

Treat either state as an integrity failure:

```text
selected reviewer is satisfied
but its complete receipt EvidenceRef does not exist

OR

complete receipt EvidenceRef exists
but selected-reviewer obligation remains outstanding
```

## 20. Effective identity

Count acquisition progress only by:

```text
(
  receipt.resolved_identity.provider,
  receipt.resolved_identity.model_version
)
```

Do not use `(provider, model, model_version)` for acquisition cardinality. Keep
the full tuple under hostile-review evidence and checker authority.

For a duplicate effective identity:

```text
receipt remains evidence
selected-reviewer obligation remains satisfied
target gains no extra identity
```

## 21. Eligible-pool exhaustion

Return `pool-exhausted` only when:

```text
|E| < N
all previously selected reviewer WorkItems qualified
derive_acquisition_round(...) == []
```

Never substitute a profile after failed selected work.

Construct the Section 32 M5 cause and anchor it exactly:

```text
obligationId = acquisition-target obligation
workItemId = null
executionId = null
```

## 22. Retry-policy source

For campaign basis `B`, require:

```text
protocol-side retry policy
=
B.retryPolicy
```

Never:

```text
reread P
read protocol files
rerun M6
rerun M3
hardcode protocol-v6
infer retry policy from CognitiveAttemptValidationResult
```

Preserve the authority distinction:

```text
M6 CognitiveAttemptValidationResult
=
attempt classification

B.retryPolicy
=
protocol-side retry permission

M2 Execution history + M2 hard limits
=
runner-side replacement permission
```

## 23. Retry-eligible terminal states

Only these exact states may produce `ExecutionRetryAuthorizationRef`:

```text
technical-failure
protocol-invalid
```

Never authorize retry for:

```text
qualified
provider-reported-identity-unavailable
unresolved execution
PROVEN-NOT-EXECUTED
operator replacement
missing validator classification
```

Use the dedicated M2 basis for `PROVEN-NOT-EXECUTED`. Use M8/M2 for operator
replacement. Neither uses M5 retry authorization.

## 24. Technical-failure retry

For exact current-tail Execution `E` of `W`, require an exact authoritative
`TechnicalExecutionFailure F` satisfying:

```text
F.execution == E
F.completedResponse == false
B.retryPolicy.technicalRetryAllowed == true
```

A `newlyKnownTechnicalFailures` value that is not yet authoritative is
insufficient. The fact must already belong to exact authoritative
snapshot/history.

Use `F.failureEvidence` in exact order as `basisArtifacts`.

## 25. Protocol-invalid retry

Require:

```text
exact authoritative CapturedExecutionResult C

exact CognitiveAttemptValidationResult V

V.capturedResult == C

V.classification == "protocol-invalid"

V.executionRequest.role belongs to
B.retryPolicy.deterministicallyValidatedRoles

B.retryPolicy.schemaInvalidCompletionRetryAllowed == true
```

The M6 validation may already be authoritative or may be co-admitted in the same
M5 delta. In the latter case, admit `V.evidence` and the retry authorization
atomically.

Use `V.evidence` in exact order as `basisArtifacts`.

## 26. Retry-authorization identity

Derive exactly:

```text
retryAuthorizationId =
deriveId(
  "assurance-ledger-execution-retry-authorization.v1",
  W.runId,
  W.workItemId,
  E.executionId,
  reason,
  B.protocolBundle.protocolId,
  B.protocolBundle.sha256
)
```

Construct exactly:

```ts
ExecutionRetryAuthorizationRef {
  retryAuthorizationId,

  runId:
    W.runId,

  workItemId:
    W.workItemId,

  priorExecutionId:
    E.executionId,

  reason,

  protocolBundle:
    B.protocolBundle,

  basisArtifacts
}
```

Do not include `StateRevision`, timestamp, retry counter, basis artifact SHA,
future ordinal, or future ExecutionId in this identity.

## 27. Current-tail retry requirements

Before authorization, require:

```text
E exists
E.workItemId == W.workItemId
E is current WorkItem execution tail
E is terminal
at least one W.sourceObligationId remains outstanding
run is not GATE-A-READY
no semantic terminal prohibits replacement
```

Never retry a qualified attempt.

## 28. Retry-consumption reconstruction

Use no mutable consumed flag on `ExecutionRetryAuthorizationRef R`.

Treat historical `R` as automatically consumed if and only if:

```text
the exact next-ordinal Execution exists for R.workItemId

its ordinal ==
priorExecution.attemptOrdinal + 1

no ExecutionProgressionSupersessionRef names
R.priorExecutionId
```

An operator replacement has a progression supersession and does not count as an
automatic protocol retry. A PNE replacement cannot consume an authorization
based on a prior terminal technical or protocol-invalid outcome.

Map every contradiction to `ASSURANCE-HISTORY-INTEGRITY-FAILURE`.

## 29. Runner retry counts

Derive purely from Authoritative History:

```text
historicalExecutionCount =
number of Executions for W
```

```text
technicalRetryReplacementCount =
count of consumed ExecutionRetryAuthorizationRef
where reason == "technical-failure"
```

```text
protocolInvalidReplacementCount =
count of consumed ExecutionRetryAuthorizationRef
where reason == "protocol-invalid"
```

Consume the exact M2 limits:

```text
total < 5
technical automatic replacements < 2
protocol-invalid automatic replacements < 1
```

Never persist these counters. An authorization created but not consumed does not
consume budget. An exact unconsumed authorization for the current tail prevents
creation of a second authorization.

## 30. Exact retry decision

For a technical/protocol-invalid current tail, apply exactly:

```text
1. validate exact outcome and protocol classification

2. if exact compatible unconsumed retry authorization already exists:
       emit no new authorization

3. determine exact protocolRetryAllowed from B.retryPolicy

4. if protocolRetryAllowed == false:
       produce cognitive-retry-unavailable cause
       resolutionContracts = []

5. if historicalExecutionCount >= 5:
       produce work-item-execution-limit-exhausted cause
       resolutionContracts = []

6. if reason == technical-failure
   AND technicalRetryReplacementCount < 2:
       construct retry authorization

7. if reason == protocol-invalid
   AND protocolInvalidReplacementCount < 1:
       construct retry authorization

8. otherwise:
       automatic reason-specific retry limit is exhausted
       total < 5
       protocol still permits retry

       produce cognitive-retry-unavailable cause

       resolutionContracts =
       [
         authorize-known-terminal-execution-replacement
       ]
```

## 31. Assurance operational-cause schema

Define a runtime-validated union under exactly:

```text
schema =
"gate-a-assurance-ledger-operational-cause.v1"
```

Use exactly these kinds:

```text
eligible-reviewer-pool-exhausted
provider-reported-identity-unavailable
cognitive-retry-unavailable
work-item-execution-limit-exhausted
```

Define:

```ts
type GateAAssuranceLedgerOperationalCauseV1 =
  | EligibleReviewerPoolExhaustedCauseV1
  | ProviderReportedIdentityUnavailableCauseV1
  | CognitiveRetryUnavailableCauseV1
  | WorkItemExecutionLimitExhaustedCauseV1;
```

## 32. EligibleReviewerPoolExhaustedCauseV1

Define exactly:

```ts
interface EligibleReviewerPoolExhaustedCauseV1 {
  readonly schema:
    "gate-a-assurance-ledger-operational-cause.v1";

  readonly kind:
    "eligible-reviewer-pool-exhausted";

  readonly runId: GateARunId;
  readonly reviewCampaignId: ReviewCampaignId;

  readonly minimumIndependentReviewers: number;

  readonly establishedEffectiveIdentityCount: number;

  readonly selectedReviewerProfileIds:
    readonly string[];
}
```

Order `selectedReviewerProfileIds` by exact reconstructed acquisition selection.
Use `resolutionContracts = []`.

Construct `basisArtifacts` exactly:

```text
firstOccurrenceArtifactRefDedupe([
  ...B.evidence,
  ...all selected qualified receipt artifacts
      in acquisition-selection order
])
```

## 33. ProviderReportedIdentityUnavailableCauseV1

Define exactly:

```ts
interface ProviderReportedIdentityUnavailableCauseV1 {
  readonly schema:
    "gate-a-assurance-ledger-operational-cause.v1";

  readonly kind:
    "provider-reported-identity-unavailable";

  readonly runId: GateARunId;
  readonly reviewCampaignId: ReviewCampaignId;
  readonly workItemId: WorkItemId;
  readonly executionId: ExecutionId;
  readonly reviewerProfileId: string;
  readonly protocolBundle: ProtocolBundleRef;
}
```

Enter this branch only for:

```text
qualified M6 classification

AND

identityResolution.kind == provider-reported

AND

qualifying M4 terminal providerModel is:
    null
    OR ""
    OR exact "latest"
```

Then require exactly:

```text
no receipt
no EvidenceRef
no resolved_identity
no retry
no profile substitution
no later acquisition round
selected-reviewer obligation remains outstanding
```

Use `resolutionContracts = []`.

Construct `basisArtifacts` in exact first-occurrence order:

```text
[
  W.operation,
  C.rawResult,
  ...C.runtimeEvidence,
  ...V.evidence
]
```

## 34. CognitiveRetryUnavailableCauseV1

Define exactly:

```ts
interface CognitiveRetryUnavailableCauseV1 {
  readonly schema:
    "gate-a-assurance-ledger-operational-cause.v1";

  readonly kind:
    "cognitive-retry-unavailable";

  readonly runId: GateARunId;
  readonly reviewCampaignId: ReviewCampaignId;
  readonly workItemId: WorkItemId;
  readonly priorExecutionId: ExecutionId;

  readonly retryReason:
    ExecutionRetryReason;

  readonly protocolBundle:
    ProtocolBundleRef;

  readonly protocolRetryAllowed:
    boolean;

  readonly reasonReplacementCount:
    number;

  readonly reasonReplacementLimit:
    number;

  readonly historicalExecutionCount:
    number;

  readonly historicalExecutionLimit:
    5;
}
```

Use exact reason limits:

```text
technical-failure → 2
protocol-invalid → 1
```

When protocol retry is forbidden, use `resolutionContracts = []`.

When only the automatic reason-specific cap is exhausted and total history is
less than five, use exactly:

```ts
[
  {
    kind:
      "authorize-known-terminal-execution-replacement",

    priorExecutionId:
      exact prior ExecutionId,

    requiredAcceptedConsequence:
      "prior-execution-remains-authoritative-history-and-this-authorizes-one-additional-execution-occurrence"
  }
]
```

Use cause `basisArtifacts` exactly:

```text
technical-failure
→ F.failureEvidence

protocol-invalid
→ V.evidence
```

## 35. WorkItemExecutionLimitExhaustedCauseV1

Define exactly:

```ts
interface WorkItemExecutionLimitExhaustedCauseV1 {
  readonly schema:
    "gate-a-assurance-ledger-operational-cause.v1";

  readonly kind:
    "work-item-execution-limit-exhausted";

  readonly runId: GateARunId;
  readonly reviewCampaignId: ReviewCampaignId;
  readonly workItemId: WorkItemId;
  readonly terminalExecutionId: ExecutionId;

  readonly historicalExecutionCount: 5;
  readonly historicalExecutionLimit: 5;

  readonly terminalCondition:
    | "technical-failure"
    | "protocol-invalid";
}
```

Use `resolutionContracts = []`.

Use cause `basisArtifacts` exactly:

```text
technical-failure
→ F.failureEvidence

protocol-invalid
→ V.evidence
```

## 36. No operational recheck

M5-A must never emit:

```text
request-operational-recheck
```

Every M5-A operational cause is based on immutable campaign, protocol, or
history facts rather than a mutable external condition that re-observation could
change.

M5-A must also never emit:

```text
authorize-uncertain-execution-replacement
```

## 37. Cause sealing

For every cause:

```text
construct exact cause value
runtime validate
canonical runner JSON serialize
sealRunnerArtifact(application/json)
require repositoryPath == null
verify returned ref
```

Then construct:

```ts
NonRecoveryOperationalCauseRefV1 {
  producer:
    "assurance-ledger",

  causeDescriptor:
    exact sealed cause ArtifactRef,

  basisArtifacts:
    exact cause-specific basis,

  resolutionContracts:
    exact cause-specific contracts
}
```

Never construct in M5-A:

```text
OperationalBlocker
BlockerId
Operator Action Request
OperatorResolutionEnvelope
```

## 38. Operational-blocker request anchors

Map exactly:

```text
eligible-reviewer-pool-exhausted
→ obligationId = target obligation
→ workItemId = null
→ executionId = null

provider-reported-identity-unavailable
→ obligationId = selected reviewer obligation
→ workItemId = exact W
→ executionId = exact E

cognitive-retry-unavailable
→ obligationId = selected reviewer obligation
→ workItemId = exact W
→ executionId = exact terminal E

work-item-execution-limit-exhausted
→ obligationId = selected reviewer obligation
→ workItemId = exact W
→ executionId = exact terminal E
```

Place each exact `NonRecoveryOperationalCauseRefV1` in the corresponding
`AssuranceOperationalBlockerRequest`. Leave blocker identity and presentation to
M8-B.

## 39. Receipt scope in M5-A

Fully close receipt construction for the cognitive WorkItems M5-A constructs:

```text
role == initial-reviewer
```

Fix the cross-layer identity mapping for every future cognitive receipt:

```text
WorkItemId
→ receipt.execution_id

ExecutionId
→ receipt.attempt_id

M4 CognitiveCallId
→ receipt.call_id
```

Do not invent prompt, packet, or output repository bindings for future M5-B/M5-C
cognitive roles. Require those future briefs to preserve the same identity
hierarchy.

Before complete receipt construction, retained runner Executions, M4 outcomes,
M4 terminal evidence, sealed completed output, and M6 classification remain
GateARun operational history. Pre-receipt history is not hostile-review evidence.

## 40. Receipt-admissible initial-reviewer attempts

For initial-reviewer `W`, traverse its Executions by ascending `attemptOrdinal`.
An Execution `E` becomes a receipt attempt only under one exact branch:

```text
A.
exact authoritative TechnicalExecutionFailure
+
exact receipt-admissible M4 technical terminal evidence

OR

B.
exact authoritative CapturedExecutionResult
+
exact M6 classification == protocol-invalid

OR

C.
exact authoritative CapturedExecutionResult
+
exact M6 classification == qualified
+
resolved identity is lawfully constructible
```

Never include:

```text
PROVEN-NOT-EXECUTED
unresolved
pending
unknown protocol outcome
progression-superseded unknown
pre-call zero-transport local failure
```

Progression supersession does not remove an attempt whose protocol outcome was
already mechanically established.

## 41. Exact M4 terminal-evidence extraction

From `CapturedExecutionResult.runtimeEvidence` or
`TechnicalExecutionFailure.failureEvidence`:

```text
verify every ArtifactRef relied upon
read exact immutable bytes through CampaignArtifactStore
locate exactly one runtime-valid:
    CognitiveCompletedResponseEvidenceV1
    or
    CognitiveTechnicalFailureEvidenceV1
require exact binding to:
    E
    W
    callId
```

Zero or multiple matching terminal evidence values are
`ASSURANCE-HISTORY-INTEGRITY-FAILURE`.

Do not reconstruct runtime or provider metadata.

## 42. Initial-reviewer raw-output repository path

For every completed initial-reviewer attempt `E/W`, derive exactly:

```text
rawOutputRepositoryPath =
"formal/reviews/raw/" +
W.workItemId +
"-ATTEMPT-" +
decimal(E.attemptOrdinal) +
".json"
```

This path provides one path per protocol attempt. Two attempts with byte-identical
raw output retain distinct paths. Content integrity remains bound by
`rawResult.sha256`. The path is deterministic and independent of callback
timing.

Require the raw-result CAS `ArtifactRef.repositoryPath == null`. Do not modify
its bytes. M5-D must later materialize the exact bytes at the exact receipt-bound
path. M5-A mutates no repository.

## 43. Technical-failure receipt attempt

Project exactly from M4 technical terminal `T`:

```ts
{
  attempt_id:
    E.executionId,

  call_id:
    T.callId,

  outcome:
    "technical-failure",

  started_at:
    T.startedAt,

  ended_at:
    T.endedAt,

  provider_model:
    T.providerModel,

  provider_response_id:
    T.providerResponseId,

  termination:
    T.termination,

  transport_attempt_count:
    T.transportAttemptCount,

  raw_output:
    null,

  protocol_errors:
    []
}
```

For selected v1, require `T.transportAttemptCount == 1`.

## 44. Protocol-invalid receipt attempt

Project exactly:

```ts
{
  attempt_id:
    E.executionId,

  call_id:
    T.callId,

  outcome:
    "protocol-invalid",

  started_at:
    T.startedAt,

  ended_at:
    T.endedAt,

  provider_model:
    T.providerModel,

  provider_response_id:
    T.providerResponseId,

  termination:
    T.termination,

  transport_attempt_count:
    T.transportAttemptCount,

  raw_output: {
    path:
      exact rawOutputRepositoryPath,

    sha256:
      C.rawResult.sha256
  },

  protocol_errors:
    exact V.protocolErrors
}
```

Do not sort or rewrite `protocolErrors`.

## 45. Qualified receipt attempt

Use the exact same M4 projection as Section 44 with:

```text
outcome = qualified

raw_output =
{
  path: exact rawOutputRepositoryPath,
  sha256: C.rawResult.sha256
}

protocol_errors = []
```

Require the qualified attempt to be the final receipt-admissible attempt and
require exactly one qualified attempt.

## 46. Receipt top-level fields

Construct exactly:

```text
receipt_schema_version =
"3.0"

execution_id =
W.workItemId

role =
"initial-reviewer"

reviewer_profile_id =
A.profileId

protocol_bundle_sha256 =
B.protocolBundle.sha256
```

Use exact constants:

```text
isolated_context = true
cross_reviewer_visibility_before_seal = false
tools_enabled = false
```

## 47. Receipt input references

Construct exactly:

```json
{
  "prompt": {
    "path": B.initialReviewerExecutionInputs.promptRepositoryPath,
    "sha256": B.initialReviewerExecutionInputs.prompt.sha256
  },

  "packet": {
    "path": B.initialReviewerExecutionInputs.packetRepositoryPath,
    "sha256": B.initialReviewerExecutionInputs.packet.sha256
  }
}
```

Require:

```text
operation.prompt ==
B.initialReviewerExecutionInputs.prompt

operation.packet ==
B.initialReviewerExecutionInputs.packet
```

## 48. Receipt request

Construct from exact immutable candidate binding:

```json
{
  "provider": A.provider,
  "model": A.requestModel
}
```

For every
receipt-admissible M4 terminal evidence `T`, require:

```text
T.request.provider == A.provider
T.request.model == A.requestModel
```

Otherwise fail with `ASSURANCE-HISTORY-INTEGRITY-FAILURE`. Retry or operator
replacement cannot change provider or request model.

## 49. Receipt runtime

Schema v3 has one top-level runtime. Require for every receipt-admissible
attempt:

```text
T.runtime ==
qualifyingAttemptTerminal.runtime
```

Set:

```text
receipt.runtime =
qualifyingAttemptTerminal.runtime
```

A runtime mismatch in one logical receipt is
`ASSURANCE-HISTORY-INTEGRITY-FAILURE`. Never select the final attempt runtime
while hiding an earlier mismatch.

## 50. Qualifying attempt identity

Set exactly:

```text
qualifying_attempt_id =
qualifiedExecution.executionId
```

Require:

```text
qualifying_attempt_id ==
exact qualified attempt.attempt_id
```

## 51. Pinned resolved identity

When:

```text
A.identityResolution.kind ==
"pinned-request-model"
```

require `requestModelIsImmutableVersion == true` and construct:

```json
{
  "provider": A.provider,
  "model": A.requestModel,
  "model_version": A.requestModel,
  "resolution_kind": "pinned-request-model",
  "evidence_attempt_id": qualifiedExecution.executionId
}
```

Do not use `providerModel` for
`model_version`.

## 52. Provider-reported resolved identity

When `A.identityResolution.kind == "provider-reported"`, require the selected
dependency realization to have already established:

```text
provider-owned-canonical-effective-model-identity-v1
```

M5-A does not qualify this capability.

Read only exact `qualifyingTerminal.providerModel`. When it is non-empty and not
exact `latest`, construct:

```json
{
  "provider": A.provider,
  "model": A.requestModel,
  "model_version": qualifyingTerminal.providerModel,
  "resolution_kind": "provider-reported",
  "evidence_attempt_id": qualifiedExecution.executionId
}
```

Apply no regex, date parsing,
snapshot-name parsing, request-versus-response heuristic, repeated-observation
heuristic, or fallback to `requestModel`.

## 53. Provider identity unavailable

When a qualified provider-reported attempt has:

```text
providerModel == null

OR

providerModel == ""

OR

providerModel == "latest"
```

stop receipt construction and produce the Section 33 cause. Produce no receipt.

## 54. Receipt-attempt list

Set exactly:

```text
attempts =
receipt-admissible executions
ordered by runner Execution.attemptOrdinal ascending
```

Required example:

```text
E1 protocol-invalid
E2 PROVEN-NOT-EXECUTED
E3 technical-failure
E4 progression-superseded unknown
E5 qualified

receipt.attempts =
[
  E1,
  E3,
  E5
]
```

Keep all five in GateARun operational history.

## 55. Receipt-construction algorithm

Apply exactly:

```text
assemble_initial_reviewer_receipt(B, A, W):

    validate exact basis/candidate/WorkItem/operation bindings

    executions =
        all W Executions ordered by attemptOrdinal

    attempts = []

    for E in executions:
        derive exact receipt-admissible outcome

        if no mechanically established receipt outcome:
            continue

        construct exact attempt

        append

    require exactly one qualified attempt

    require qualified attempt is final

    require no later Execution exists after qualified E

    require all included M4 terminal evidence use same runtime

    derive exact resolved_identity

    construct exact schema-v3 receipt

    runtime validate against execution-receipt v3 contract

    canonical serialize

    seal as application/json

    require receipt artifact repositoryPath == null

    verify sealed artifact

    construct EvidenceRef

    return receipt artifact + EvidenceRef
```

Do not invoke the Python validator in M5-A. M6 classification remains authority
for attempt validity.

## 56. Receipt canonical JSON

Use exact bytes:

```text
UTF-8
recursive object-key sorting
arrays preserve semantic order
separators exactly "," and ":"
ensure_ascii = false
no insignificant whitespace
no trailing newline
```

Use the accepted canonical hostile-review JSON convention.

## 57. Receipt EvidenceRef

Derive identity exactly:

```text
deriveId(
  "assurance-ledger-execution-receipt-evidence.v1",
  W.runId,
  W.workItemId
)
```

Construct exactly:

```ts
EvidenceRef {
  evidenceId,

  runId:
    W.runId,

  candidateId:
    W.candidateId,

  reviewCampaignId:
    W.reviewCampaignId,

  sourceExecutionIds:
    receipt attempts
      in receipt order
      mapped to attempt ExecutionIds,

  artifact:
    exact sealed receipt ArtifactRef
}
```

Require:

```text
sourceExecutionIds ==
receipt.attempts[*].attempt_id
```

## 58. Receipt repository-path ownership

Do not select the eventual repository path of the receipt artifact in M5-A.
M5-D owns exact assurance-repository projection and must project this exact
immutable receipt under:

```text
formal/reviews/executions/*.json
```

The receipt-embedded `raw_output.path` is already closed by Section 42. Require
M5-D to preserve it exactly during materialization.

## 59. Input/request closure

Start `prepare_campaign_work_contribution` by requiring:

```text
request.snapshot.run.runId ==
request.evaluationContext.runId

request.evaluationContext.authorityEvaluation exists and is intact
```

Decode the exact `GateACampaignAuthorityEvaluationV1` and require:

```text
runId ==
evaluationContext.runId

stateRevision ==
snapshot.stateRevision

qualificationCandidateId ==
evaluationContext.qualificationCandidate.candidateId

semanticSubject ==
evaluationContext.semanticSubject

protocolBundle ==
evaluationContext.protocolBundle

current/stale campaign IDs ==
exact evaluationContext campaign sets
```

Map caller-supplied contradiction to
`INVALID-ASSURANCE-DERIVATION-REQUEST`. Map contradiction already present in
Authoritative History to `ASSURANCE-HISTORY-INTEGRITY-FAILURE`.

## 60. M5-A campaign traversal

Process only M5-A-owned current runner-produced campaign work. Traverse exact
`evaluationContext.currentCampaigns` order.

For each current runner-produced campaign, locate exactly one corresponding
member of `snapshot.reviewCampaignPrerequisiteBases`.

Leave repository-imported campaigns to M5-B evidence import. Add no new M5-A
reviewer work for historical non-current runner campaigns.

## 61. Input arrays and submodule ownership

The arrays:

```text
newlyCapturedResults
newlyKnownTechnicalFailures
newlyValidatedCognitiveAttempts
```

may eventually contain values for M5-B/M5-C cognitive WorkItems. Consume only
exact values whose WorkItem is one of the selected initial-reviewer WorkItems
reconstructed by M5-A.

Do not reject another-role value merely because it belongs to a future sibling
submodule. Do not interpret it. Require future composite M5 to distribute the
exact request to each owner.

## 62. Artifact verification

Before interpreting any `ArtifactRef`, invoke:

```text
CampaignArtifactStore.verify()
```

for every artifact on which the result depends.

Never infer:

```text
ArtifactRef present in admittedArtifacts
→ trustworthy
```

Map a missing or corrupt artifact to
`ASSURANCE-ARTIFACT-INTEGRITY-FAILURE`, not to a blocker.

## 63. Idempotence pattern

For every M5-A product:

```text
derive exact logical identity

if absent:
    emit exact product

if exact same identity + exact same payload already authoritative:
    emit nothing

if same identity + incompatible payload:
    ASSURANCE-HISTORY-INTEGRITY-FAILURE
```

Apply this pattern to:

```text
target obligation
selected-reviewer obligation
selected reviewer WorkItem
retry authorization
receipt EvidenceRef
obligation disposition
sealed operational cause descriptor
operational-blocker request
```

For the same immutable cause inputs, produce byte-identical cause-descriptor
bytes and the same CAS-backed `ArtifactRef`; let M8-B own blocker identity and
blocker reuse.

## 64. Stale-state behavior

Derive M5-A products against `request.snapshot.stateRevision` and set:

```text
preparation.expectedStateRevision =
request.snapshot.stateRevision
```

If M2 later rejects with stale-state:

```text
no stale preparation is rebound
no causeDescriptor is rewritten with a new revision
no materialized blocker is reused as authority
reload snapshot
rederive from scratch
```

Already sealed CAS artifacts remain non-authoritative durable material.

## 65. No empty mutation

When the M5-A contribution has no new EvidenceRef, disposition, obligation,
WorkItem, retry authorization, or operational-blocker request, it represents no
new M5-A fact.

Require future composite M5 not to submit a mutation solely for this no-op. Do
not use M2 `NO_NEW_FACTS` as normal control flow.

## 66. Authoritative barriers

Require:

```text
products of one M5 phase do not become inputs to another M5 progression phase
until M2 has admitted them and a fresh snapshot has been loaded
```

Apply at least:

```text
receipt admission
→ reload
→ next reviewer round

final receipt establishing N effective identities
→ reload
→ target satisfaction
```

Permit no speculative same-delta phase advancement.

## 67. Output ordering

Make every M5-A output independent of callback timing.

Use:

```text
campaign traversal
→ evaluationContext.currentCampaigns exact order

within one campaign
→ reconstructed reviewer-acquisition selection order

within one WorkItem
→ Execution attemptOrdinal ascending

later-round obligations/workItems
→ exact acquisition-round order

operational-blocker requests
→ same campaign/reviewer traversal order
```

Do not sort acquisition candidates by profile ID.

## 68. Failure taxonomy

Define exactly:

```ts
type M5ACampaignWorkFailureCodeV1 =
  | "INVALID-ASSURANCE-DERIVATION-REQUEST"
  | "ASSURANCE-HISTORY-INTEGRITY-FAILURE"
  | "ASSURANCE-ARTIFACT-INTEGRITY-FAILURE"
  | "ASSURANCE-ARTIFACT-SEAL-FAILURE"
  | "ASSURANCE-FINALIZATION-INTEGRITY-FAILURE";
```

Map exactly:

```text
malformed request
caller snapshot/context mismatch
duplicate incompatible newly-* caller inputs
wrong-run caller result
→ INVALID-ASSURANCE-DERIVATION-REQUEST
```

```text
authoritative logical-ID conflict
partial acquisition round
illegal selected profile
extra selected profile after target
missing selected WorkItem
multiple receipt classifications
invalid Execution chain
multiple qualified attempts
qualified not final
runtime mismatch across receipt attempts
WorkItem/operation/candidate contradiction
receipt/disposition contradiction
→ ASSURANCE-HISTORY-INTEGRITY-FAILURE
```

```text
missing/corrupt immutable artifact
SHA mismatch
malformed retained M4/M6 artifact
→ ASSURANCE-ARTIFACT-INTEGRITY-FAILURE
```

```text
canonical serialization failure
CAS sealing failure
sealed-ref verification mismatch
→ ASSURANCE-ARTIFACT-SEAL-FAILURE
```

```text
future M5 composite receives M8 materialization inconsistent with exact
M5-A operational request
→ ASSURANCE-FINALIZATION-INTEGRITY-FAILURE
```

These failures do not produce an OperationalBlocker, `DECISION-REQUIRED`, retry,
or reviewer substitution.

## 69. Restart matrix

Apply exactly:

```text
crash before M4 terminal outcome admission
→ M4/M8 recovery path

crash after terminal outcome admission but before M6 classification
→ exact authoritative outcome retained
→ exact validation can be recomputed

crash after M6 computation but before M5 delta admission
→ classification may be recomputed
→ same M5 derivation

crash after M5 seals receipt/cause but before M2 admission
→ CAS artifact non-authoritative
→ same snapshot reproduces same bytes

crash after M2 admits M5 products
→ snapshot exposes products
→ replay emits no duplicates

crash after blocker admission
→ authoritative blocker stops ordinary progression

crash after operator replacement
→ M2 atomic successor + supersession defines new tail
```

## 70. Required invariants

```text
M5A-01
One runner-produced campaign has exactly one reviewer-acquisition target obligation.

M5A-02
One selected initial-reviewer profile has exactly one selected-reviewer obligation per campaign.

M5A-03
One selected-reviewer obligation has exactly one logical WorkItem.

M5A-04
Reviewer acquisition target has no WorkItem.

M5A-05
Reviewer WorkItem sourceObligationIds contains only its selected-reviewer obligation.

M5A-06
First-round candidate selection remains M1-owned.

M5A-07
M5 validates but does not independently choose first-round candidates.

M5A-08
First and later rounds use the same selected-reviewer WorkItem constructor.

M5A-09
No acquisition round identity is persisted.

M5A-10
Selected reviewer reconstruction is obligation-based, not WorkItem-history-based.

M5A-11
Reviewer acquisition is independent of findings and timing.

M5A-12
Pinned candidates are skipped only under exact accepted effective-identity rules.

M5A-13
Provider-reported candidates are never pre-collapsed.

M5A-14
A selected WorkItem failure never becomes automatic profile substitution.

M5A-15
No extra reviewer is selected after the effective minimum is established.

M5A-16
Pool exhaustion below minimum yields exactly the M5 non-recovery cause.

M5A-17
Protocol retry policy comes only from retained basis.retryPolicy.

M5A-18
M5 never rereads P for retry permission.

M5A-19
Qualified attempt never produces retry authorization.

M5A-20
Protocol-invalid retry exists only for protocol-authorized deterministically validated roles.

M5A-21
Technical retry requires exact admitted TechnicalExecutionFailure.

M5A-22
One retry authorization names one exact prior Execution.

M5A-23
One retry authorization may produce at most one automatic successor.

M5A-24
Retry counts are derived, never persisted.

M5A-25
Operator replacement does not consume automatic retry count.

M5A-26
Absolute historical Execution count never exceeds the M2 cap through M5 authorization.

M5A-27
M5-A never emits request-operational-recheck.

M5A-28
Provider-reported identity unavailable produces no receipt and no retry.

M5A-29
One WorkItem identifies one logical schema-v3 execution receipt.

M5A-30
One receipt attempt corresponds to one receipt-admissible runner Execution.

M5A-31
receipt.execution_id equals WorkItemId.

M5A-32
receipt attempt_id equals runner ExecutionId.

M5A-33
receipt call_id equals exact M4 CognitiveCallId.

M5A-34
Receipt attempts preserve Execution attemptOrdinal order.

M5A-35
PNE and unknown/superseded-unknown Executions are never fabricated into receipt attempts.

M5A-36
Exactly one qualified receipt attempt exists.

M5A-37
The qualified attempt is final.

M5A-38
Provider/model request bindings never change across retries.

M5A-39
All receipt-admissible attempts represented by one schema-v3 receipt use one identical runtime identity.

M5A-40
Provider-reported resolved identity uses only the exact qualifying providerModel.

M5A-41
Pinned resolved identity uses only immutable requestModel.

M5A-42
Complete receipt EvidenceRef and selected-reviewer satisfaction are atomic M5 products.

M5A-43
Partial/no-qualified receipt is never EvidenceRef.

M5A-44
Acquisition target satisfaction derives only from already-authoritative receipts.

M5A-45
Same immutable M5-A inputs produce byte-identical M5-A artifacts.

M5A-46
M5-A cache is never authority.

M5A-47
M5-A mutates no repository state.

M5A-48
M5-A writes no authoritative campaign state.

M5A-49
M5-A constructs no OperationalBlocker identity.

M5A-50
M5-A implementation/integrity failures are never disguised as normal campaign outcomes.
```

## 71. Forbidden behavior

Explicitly forbid:

```text
M5 choosing first-round profile independently
execute-all reviewer registry semantics
profile substitution after failed selected work
finding-driven reviewer acquisition
timing-driven reviewer acquisition
providerModel guessing
requestModel fallback for provider-reported identity
retrying qualified semantic result
retrying protocol-invalid role without deterministic validator
creating new WorkItem for protocol retry
creating new WorkItem for operator retry
partial receipt
receipt from unknown protocol outcome
fabricating PNE as technical failure
inventing round state
persisting retry counters
rereading current P
rerunning M3 for admitted campaign
rerunning M6 review-authority projection for admitted campaign
mutable repository rescan
M5 direct repository mutation
M5 direct state mutation
M5-created BlockerId/OAR/operator effect
semantic merge with M5-B/C/D responsibilities
```

## 72. Construction boundary

Final M0 closure must provide:

```text
runtime validators for every M5-A internal schema
collision-safe/domain-separated deterministic ID helpers
the exact lexical renderer needed by selected reviewer WorkItem logical
execution identity
canonical runner JSON
CampaignArtifactStore
execution-receipt schema-v3 runtime validation
```

M5-A requires no new external Dependency Contract. It consumes M4's active Pi
Dependency Contract indirectly through accepted M4 evidence bindings only.

No coding agent may choose:

```text
obligation identity
WorkItem identity
reviewer acquisition progression
retry admissibility
retry authorization identity
retry exhaustion consequence
cause schema
resolution contract
receipt attempt inclusion
attempt ordering
receipt field mapping
resolved identity
receipt EvidenceRef identity
restart behavior
failure classes
```
