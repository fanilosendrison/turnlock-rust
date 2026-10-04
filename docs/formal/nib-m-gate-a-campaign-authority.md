---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-02"
step_id: 2
id: NIB-M-GATE-A-CAMPAIGN-AUTHORITY
version: "4.0.0"
scope: gate-a-campaign-runner/campaign-authority
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Campaign Authority

## 1. Status, authority, and purpose

Implement M3 `campaign-authority` according to this active Module Brief.

It consumes `NIB-S-GATE-A-CAMPAIGN-RUNNER` version `9.1.2`.

Version `4.0.0` is a breaking construction-contract revision because the
exported established `ReviewerPrerequisiteResolution` shape gains the exact
retained retry-policy fact required by M5-A. It adds no M3 semantic, retry
interpretation, or retry-admissibility authority.

Version `3.0.0` is a breaking construction-contract revision that removes the
WorkItem/ReviewContext construction cycle, adds exact retained initial-reviewer
execution inputs to the M3 prerequisite result, and changes no M3 ownership,
external side effect, product semantic, or hostile-review semantic.

Version `2.0.2` was a dependency-only compatibility synchronization with NIB-S
`9.1.0`. It changed no algorithm, type, or module invariant.

Version `2.0.1` is dependency-only synchronization with NIB-S `9.0.1`.

M3 still produces the same exact `ReviewerPrerequisiteResolution` established
basis. NIB-S `9.0.1` only makes the downstream admitted basis restart-observable.
M3 gains no new persistence or execution authority.

Version `2.0.0` is a breaking Module Brief revision because
`ReviewerPrerequisiteResolution` and static reviewer-feasibility semantics
change under ADR-053 and protocol v5. M3 preserves its existing authority,
currentness, operational-cause, and no-execution ownership boundaries.

Treat this brief as implementation-construction authority only. It creates no:

```text
TURNLOCK product semantic
canonical formal semantic
hostile-review protocol semantic
formal-assurance claim
review evidence
verification evidence
product ADR
```

M3 campaign-authority is NOT decomposed.

Keep these responsibilities in one coherent deterministic module:

```text
preflight authority interpretation
exact semantic-subject/protocol campaign currentness
repository review-campaign observation/import merge
reviewer-prerequisite interpretation
preservation of exact M6-projected initial-reviewer execution inputs
preservation of exact M6-projected protocol retry policy
campaign-authority operational cause construction
campaign-authority blocking-obligation construction
GateACampaignAuthorityEvaluationV1 witness construction
GateAEvaluationContext construction
ReviewContext construction
```

Create no sub-module briefs for M3.

## 2. Responsibility boundary

M3 owns exactly:

```text
repository/preflight authority interpretation
binding of exact mechanically derived Gate A semantic subject S
interpretation of exact mechanically projected hostile-review authority
exact current hostile-review protocol identity P consumption
exact (S,P) campaign currentness
construction of repository-origin ReviewCampaignRef values from exact M6 facts
merge/conflict handling by ReviewCampaignId
canonical current/stale campaign selection
INITIAL / SUBJECT-CHANGED / PROTOCOL-CHANGED classification
static reviewer-profile prerequisite interpretation
preservation without interpretation of exact M6-projected protocol retry policy
M3 campaign-authority operational cause semantics
M3 blocking ObligationRef construction
GateACampaignAuthorityEvaluationV1 construction/sealing
GateAEvaluationContext construction
ReviewContext construction
```

M3 does not own:

```text
repository inspection
Git semantics or Git invocation
Python validator invocation
subject derivation
protocol parsing
protocol schema validation
review-evidence parsing/validation
hostile-review record parsing
repository review dependency-closure derivation
LLM/provider invocation
provider/model-version evidence resolution
final independent-reviewer evidence counting
finding semantics
adjudication semantics
re-adjudication semantics
assurance repository projection semantics
M5 assurance derivation
runner-produced ReviewCampaign repositoryAuthority provenance construction
candidate construction
candidate provenance mutation
authoritative campaign-state mutation
OperationalBlocker construction
BlockerId construction
Operator Action Request construction
operator-resolution ingestion
publication
```

## 3. Candidate-provenance boundary

NIB-S `9.0.0` candidates include:

```text
producedByRepairIntentId
producedByAssuranceProjectionId
```

Do not reinterpret either provenance mechanism in M3. M2, M5, and M7 own their
respective candidate and projection integrity contracts.

Apply this exact currentness rule:

```text
candidate revision change alone != subject change

currentness is determined from exact S, exact P, and campaign history
```

Apply the same currentness algorithm to an assurance-only successor, repair-only
successor, combined successor, or any other admitted `CandidateRevisionRef`.
Do not use candidate provenance kind to filter current or stale campaigns. Do
not add a special currentness branch for `producedByAssuranceProjectionId`.

## 4. Dependencies and consumed contracts

M3 consumes exactly:

```text
M0 contracts/runtime validators/pure deterministic helpers/canonical runner JSON
CampaignArtifactStore
```

Use this construction dependency shape:

```ts
interface CampaignAuthorityDependencies {
  readonly artifactStore: CampaignArtifactStore;
}
```

Select no non-trivial external dependency in M3. M3 requires no separate
Dependency Contract.

Do not directly import or use:

```text
Git executable
Python
SQLite
network
provider SDK
pi-ai
llm-runtime
repository filesystem traversal
mutable repositoryPath authority
wall clock
randomness
environment-selected campaign authority
```

Consume the following NIB-S `9.1.2` cross-module types unchanged:

```text
ArtifactRef
GateARunId
CandidateRevisionId
ReviewCampaignId
ObligationId
StateRevision
RepositoryAuthorityRef
SemanticSubjectRef
ProtocolBundleRef
RepositoryInspectionRef
CandidateRevisionRef
ReviewCampaignRef
ObligationRef
PreflightRequest
PreflightResolution
ReviewCurrentnessRequest
ReviewCurrentnessResolution
ReviewerPrerequisiteRequest
ReviewerPrerequisiteResolution
ReviewContext
RepositoryReviewObservationV1
GateACampaignAuthorityEvaluationV1
GateAEvaluationContext
CandidateSubjectMechanicalDerivationResult
CandidateReviewAuthorityMechanicalProjectionResult
GateAReviewerProfileMechanicalFactV1
GateAReviewerAcquisitionPolicyMechanicalFactV1
GateACognitiveRetryPolicyMechanicalFactV1
EffectiveReviewerIdentityRefV1
GateAReviewerAcquisitionCandidateV1
InitialReviewerExecutionInputsRefV1
GateARepositoryReviewMechanicalFactV1
CampaignAuthorityOperationalCauseRefV1
GateACampaignAuthorityOperationalCauseV1
PreflightReviewAuthorityInvalidCauseV1
CurrentCandidateReviewAuthorityInvalidCauseV1
ReviewerPrerequisitesUnavailableCauseV1
NonRecoveryOperationalCauseRefV1
NonRecoveryOperatorResolutionContractV1
CampaignArtifactStore
```

Do not redefine a conflicting cross-module type.

## 5. Operation surface

Expose exactly these four M3 operations:

```ts
preflight(
  request: PreflightRequest,
): Promise<PreflightResolution>;

resolve_currentness(
  request: ReviewCurrentnessRequest,
): Promise<ReviewCurrentnessResolution>;

verify_reviewer_prerequisites(
  request: ReviewerPrerequisiteRequest,
): Promise<ReviewerPrerequisiteResolution>;

construct_review_context(
  request: ReviewContextConstructionRequest,
): ReviewContext;
```

Define exactly one M3-internal request type:

```ts
interface ReviewContextConstructionRequest {
  readonly runId: GateARunId;
  readonly candidate: CandidateRevisionRef;
  readonly campaign: ReviewCampaignRef;
}
```

Keep `ReviewContextConstructionRequest` internal to M3. Do not add it to NIB-S.
Do not add another M3 operation.

## 6. Canonical ordering and deduplication

Use exactly:

```text
ReviewCampaignId → unsigned ASCII ascending
profileId → unsigned ASCII ascending
```

Deduplicate an `ArtifactRef` array only through complete `ArtifactRef`
structural equality. Let the first occurrence win and preserve first-occurrence
order. Do not deduplicate merely by SHA because distinct external
`ArtifactRef` identities may legally identify identical bytes.

## 7. M3 obligation definitions

Define exactly:

```ts
interface GateACampaignAuthorityObligationDefinitionV1 {
  readonly schema:
    "gate-a-campaign-authority-obligation-definition.v1";

  readonly kind:
    | "current-review-authority"
    | "reviewer-prerequisites";
}
```

No other kind exists in M3 v1.

The first exact value is:

```json
{
  "schema": "gate-a-campaign-authority-obligation-definition.v1",
  "kind": "current-review-authority"
}
```

Its canonical runner JSON bytes are exactly:

```text
{"kind":"current-review-authority","schema":"gate-a-campaign-authority-obligation-definition.v1"}
```

The second exact value is:

```json
{
  "schema": "gate-a-campaign-authority-obligation-definition.v1",
  "kind": "reviewer-prerequisites"
}
```

Its canonical runner JSON bytes are exactly:

```text
{"kind":"reviewer-prerequisites","schema":"gate-a-campaign-authority-obligation-definition.v1"}
```

For both values require:

```text
UTF-8
compact JSON
no trailing newline
mediaType = application/json
runner-owned
repositoryPath = null
```

M0 final closure must expose the runtime validator for this schema before
GREEN.

### 7.1 Obligation-definition sealing

Seal an obligation definition with this exact algorithm:

```text
construct exact constant value
runtime-validate with M0
canonical runner JSON serialize
artifactStore.sealRunnerArtifact({
    bytes,
    mediaType: "application/json"
})
require returned ArtifactRef.mediaType == "application/json"
require returned ArtifactRef.repositoryPath == null
artifactStore.verify(returnedRef)
return exact ArtifactRef
```

A memory cache may avoid redundant sealing. The cache is never authority. A
restart may reseal the same bytes. Identical bytes must resolve to the same
CAS-backed runner artifact identity under `CampaignArtifactStore`.

## 8. M3 operational causes

M3 has exactly these three operational cause kinds inherited from NIB-S:

```text
preflight-review-authority-invalid
current-candidate-review-authority-invalid
reviewer-prerequisites-unavailable
```

For one accepted M3 cause, use this exact sealing process:

```text
construct exact GateACampaignAuthorityOperationalCauseV1 value
runtime-validate using M0
canonical runner JSON serialize
sealRunnerArtifact(application/json)
require repositoryPath == null
require mediaType == application/json
verify returned ArtifactRef
construct exact CampaignAuthorityOperationalCauseRefV1
```

Set the returned cause reference fields exactly as follows:

```text
producer = "campaign-authority"
causeDescriptor = exact newly sealed ArtifactRef
basisArtifacts = exact cause-specific ordered basis
resolutionContracts = exact cause-specific contracts
```

Never construct an `OperationalBlocker`, `BlockerId`,
`GateAOperatorActionRequestV1`, or `OperatorResolutionEnvelope` in M3.

## 9. Input artifact verification

Before interpretation, verify through `CampaignArtifactStore.verify()` every
`ArtifactRef` whose existence M3 relies on.

For preflight verify:

```text
repositoryInspection.baselineGitBasis
repositoryInspection.sealedBaselineCandidate.materialization
every repositoryInspection.sealedBaselineCandidate.materializationEvidence
every repositoryInspection.evidence
subjectDerivation.projection
every subjectDerivation.evidence
reviewAuthority.projection
every reviewAuthority.evidence
reviewAuthority.diagnostics when reviewAuthority.kind == invalid
```

For currentness verify:

```text
reviewAuthority.projection
every reviewAuthority.evidence
reviewAuthority.diagnostics when invalid
for established repositoryReviews:
    every sourceRecord
    every referencedArtifacts member
```

For reviewer prerequisites verify:

```text
reviewAuthority.projection
every reviewAuthority.evidence
```

Do not reread repository paths. Treat artifact verification failure as a module
invocation failure, not a normal blocked result.

## 10. Mechanical-authority trust boundary

Consume exact M6 structured facts. Do not:

```text
run Python again
parse hostile-review records
recompute referencedArtifacts closure
reorder referencedArtifacts
add referencedArtifacts
remove referencedArtifacts
derive transitive hostile-review artifact dependencies
reimplement protocol validation
reimplement review-evidence validation
recompute S
recompute P
```

Reject structurally impossible dependency results, including:

```text
minimumIndependentReviewers < 1
duplicate reviewer profile IDs
reviewerProfiles not ordered by profileId unsigned ASCII
reviewerAcquisition.mode != minimum-effective-independent-v1
reviewerAcquisition.profileOrder is not an exact permutation of every
    reviewerProfiles.profileId with each ID exactly once
duplicate repository review IDs
repositoryReviews not ordered by reviewId unsigned ASCII
review.referencedArtifacts violates the declared M6 structural contract
candidate materialization binding contradiction
```

Classify these failures as
`MECHANICAL-AUTHORITY-CONTRACT-FAILURE`, not operational blockers.

## 11. Preflight algorithm

### 11.1 Request closure

Require:

```text
repositoryInspection.runId == request.runId
repositoryInspection.sealedBaselineCandidate.runId == request.runId
repositoryInspection.sealedBaselineCandidate.parentCandidateId == null
repositoryInspection.sealedBaselineCandidate.producedByRepairIntentId == null
repositoryInspection.sealedBaselineCandidate.producedByAssuranceProjectionId == null
subjectDerivation.candidateMaterialization ==
    repositoryInspection.sealedBaselineCandidate.materialization
reviewAuthority.candidateMaterialization ==
    repositoryInspection.sealedBaselineCandidate.materialization
```

Do not reread the repository.

### 11.2 Invalid review authority

When `reviewAuthority.kind == "invalid"`, construct exactly:

```ts
PreflightReviewAuthorityInvalidCauseV1 {
  schema:
    "gate-a-campaign-authority-operational-cause.v1",

  kind:
    "preflight-review-authority-invalid",

  candidateMaterialization:
    reviewAuthority.candidateMaterialization,

  reviewAuthorityProjection:
    reviewAuthority.projection
}
```

Use this basis:

```text
firstOccurrenceArtifactRefDedupe([
    reviewAuthority.projection,
    reviewAuthority.diagnostics,
    ...reviewAuthority.evidence
])
```

Use exactly these resolution contracts:

```ts
[
  {
    kind: "request-operational-recheck"
  }
]
```

Seal through the generic M3 cause helper and return exactly:

```ts
{
  kind: "blocked",
  cause
}
```

Do not construct a new M3 `ObligationRef`. The existing root-preflight
obligation is used later by M1 and M8-B.

### 11.3 Established review authority

Require `reviewAuthority.kind == "established"`.

Derive evidence exactly:

```text
firstOccurrenceArtifactRefDedupe([
    ...subjectDerivation.evidence,
    ...reviewAuthority.evidence
])
```

Require the result not to contain `subjectDerivation.projection` or
`reviewAuthority.projection`, because both have dedicated fields. Treat a
violation of projection/evidence separation as
`MECHANICAL-AUTHORITY-CONTRACT-FAILURE`.

Return exactly:

```ts
{
  kind: "established",

  baselineAuthority:
    repositoryInspection.baselineAuthority,

  publicationTarget:
    repositoryInspection.publicationTarget,

  baselineSemanticSubject:
    subjectDerivation.semanticSubject,

  protocolBundle:
    reviewAuthority.protocolBundle,

  subjectProjection:
    subjectDerivation.projection,

  reviewAuthorityProjection:
    reviewAuthority.projection,

  evidence
}
```

Seal no additional successful-preflight witness.

## 12. Review currentness

### 12.1 Request validation

Require exactly:

```text
request.candidate.runId == request.runId
candidateLineage non-empty
candidateLineage duplicate-free by candidateId
candidateLineage ordered by ordinal ascending
candidateLineage ordinals contiguous from 0
request.candidate == final candidateLineage item
every candidateLineage item.runId == request.runId
registeredCampaigns contains no duplicate ReviewCampaignId
reviewAuthority.candidateMaterialization == request.candidate.materialization
```

Do not add a currentness branch based on `producedByRepairIntentId`,
`producedByAssuranceProjectionId`, or candidate construction kind.

M1 supplies the exact complete snapshot projections. Validate their internal
closure, but do not query M2 to reconstruct omitted candidates or campaigns.

### 12.2 Invalid review authority

When `reviewAuthority.kind == "invalid"`, seal or obtain the exact
`current-review-authority` obligation definition.

Construct exactly:

```ts
ObligationRef {
  obligationId:
    deriveId(
      "campaign-authority-current-review-authority-obligation.v1",
      request.runId,
      request.candidate.candidateId,
      definition.sha256
    ),

  runId:
    request.runId,

  candidateId:
    request.candidate.candidateId,

  reviewCampaignId:
    null,

  definition
}
```

Construct exactly:

```ts
CurrentCandidateReviewAuthorityInvalidCauseV1 {
  schema:
    "gate-a-campaign-authority-operational-cause.v1",

  kind:
    "current-candidate-review-authority-invalid",

  candidateId:
    request.candidate.candidateId,

  candidateMaterialization:
    request.candidate.materialization,

  reviewAuthorityProjection:
    reviewAuthority.projection
}
```

Use this basis:

```text
firstOccurrenceArtifactRefDedupe([
  reviewAuthority.projection,
  reviewAuthority.diagnostics,
  ...reviewAuthority.evidence
])
```

Use `[]` as the exact resolution contracts and return exactly:

```ts
{
  kind: "blocked",
  blockingObligation,
  cause
}
```

Do not interpret partial repository review facts.

### 12.3 Established review-authority validation

When `reviewAuthority.kind == "established"`, require:

```text
minimumIndependentReviewers is integer >= 1
reviewerProfiles ordered by profileId unsigned ASCII ascending
reviewerProfiles profileId values unique
reviewerAcquisition.mode == minimum-effective-independent-v1
reviewerAcquisition.profileOrder contains every reviewerProfiles.profileId
    exactly once and no other ID
repositoryReviews ordered by reviewId unsigned ASCII ascending
repositoryReviews reviewId values unique
```

For every repository review require structural validity of:

```text
reviewId
sourceRecord
repositoryCommitSha
semanticSubject
protocolBundle
referencedArtifacts
```

Preserve the exact M6-produced order of every `referencedArtifacts` sequence.
Do not reconstruct whether the closure is complete; that is M6 authority.

### 12.4 Repository review observations

For every `GateARepositoryReviewMechanicalFactV1 review`, construct exactly:

```ts
RepositoryReviewObservationV1 {
  reviewCampaignId:
    review.reviewId,

  sourceRecord:
    review.sourceRecord,

  repositoryCommitSha:
    review.repositoryCommitSha,

  semanticSubject:
    review.semanticSubject,

  protocolBundle:
    review.protocolBundle,

  referencedArtifacts:
    review.referencedArtifacts
}
```

Require exact array equality:

```text
observation.referencedArtifacts == review.referencedArtifacts
```

Do not deduplicate, sort, expand, shrink, reread, or rederive this sequence.
Order observations by `ReviewCampaignId` unsigned ASCII ascending. Preserve the
inner `referencedArtifacts` ordering established by M6: `repositoryPath` exact
UTF-8 unsigned-byte ascending.

### 12.5 Imported campaigns

For every mechanically projected repository review construct exactly:

```ts
{
  reviewCampaignId:
    review.reviewId,

  provenance: {
    kind:
      "repository-imported",

    originatingRunId:
      null,

    candidateId:
      null,

    repositoryCommitSha:
      review.repositoryCommitSha
  },

  semanticSubject:
    review.semanticSubject,

  protocolBundle:
    review.protocolBundle
}
```

Do not fabricate a `RepositoryAuthorityRef`, `treeSha`, `candidateId`, or
`originatingRunId`.

### 12.6 Registered campaign integrity

Validate the supplied complete registered-campaign sequence. Require every
`ReviewCampaignId` to be unique. A duplicate in authoritative registered
history is `CAMPAIGN-HISTORY-INTEGRITY-FAILURE`, even when payloads compare
equal. Do not silently deduplicate authoritative state.

For `runner-produced`, require:

```text
provenance.originatingRunId == request.runId
provenance.candidateId != null
repositoryAuthority structurally valid
```

For `repository-imported`, require:

```text
originatingRunId == null
candidateId == null
repositoryCommitSha valid
```

### 12.7 Campaign-universe merge

Start with all exact registered campaigns. Process repository reviews in
canonical `reviewId` order.

For review `R`, let `id = R.reviewId`.

If no campaign exists for `id`, insert the exact repository-imported campaign.

If an existing campaign is `runner-produced`, require:

```text
existing.semanticSubject == R.semanticSubject
existing.protocolBundle == R.protocolBundle
existing.provenance.repositoryAuthority.commitSha == R.repositoryCommitSha
```

If an existing campaign is `repository-imported`, require:

```text
existing.semanticSubject == R.semanticSubject
existing.protocolBundle == R.protocolBundle
existing.provenance.repositoryCommitSha == R.repositoryCommitSha
```

When compatible, reuse the existing logical campaign and preserve its existing
provenance. When incompatible, fail with
`CAMPAIGN-HISTORY-INTEGRITY-FAILURE`.

Never retarget, tie-break, choose first or last, choose by record SHA or
repository path, or create a duplicate logical campaign.

### 12.8 Current and stale selection

Let:

```text
S = request.candidate.semanticSubject
P = request.reviewAuthority.protocolBundle
```

Derive:

```text
currentCampaigns =
    every campaign in campaign universe where:
        campaign.semanticSubject == S
        AND
        campaign.protocolBundle == P

staleProtocolCampaigns =
    every campaign in campaign universe where:
        campaign.semanticSubject == S
        AND
        campaign.protocolBundle != P
```

Sort both by `ReviewCampaignId` unsigned ASCII ascending.

Do not filter by:

```text
candidate provenance
repair provenance
assurance projection provenance
originating run provenance
repository provenance
repository commit
record path
record hash
admission revision
filesystem order
```

### 12.9 Currentness precedence

Apply exactly:

```text
if currentCampaigns is non-empty:
    CURRENT

else if staleProtocolCampaigns is non-empty:
    PROTOCOL-CHANGED

else if request.candidate.ordinal > 0
     AND
     candidateLineage[
       request.candidate.ordinal - 1
     ].semanticSubject != S:
    SUBJECT-CHANGED

else:
    INITIAL
```

No other reason exists. A candidate revision caused solely by materializing an
`AssuranceRepositoryProjectionRef` does not require a new campaign when `(S,P)`
is unchanged and a current campaign exists.

### 12.10 Campaign-required result

For every campaign-required branch return exactly:

```ts
{
  kind: "campaign-required",

  reason,

  candidate:
    request.candidate,

  semanticSubject:
    request.candidate.semanticSubject,

  currentProtocolBundle:
    request.reviewAuthority.protocolBundle,

  staleProtocolCampaigns
}
```

Require:

```text
PROTOCOL-CHANGED → staleProtocolCampaigns non-empty
SUBJECT-CHANGED → staleProtocolCampaigns empty
INITIAL → staleProtocolCampaigns empty
```

Do not seal `GateACampaignAuthorityEvaluationV1` for a campaign-required result.

### 12.11 Current authority witness

For a current result construct exactly:

```ts
GateACampaignAuthorityEvaluationV1 {
  schema:
    "gate-a-campaign-authority-evaluation.v1",

  runId:
    request.runId,

  stateRevision:
    request.stateRevision,

  qualificationCandidateId:
    request.candidate.candidateId,

  semanticSubject:
    S,

  protocolBundle:
    P,

  reviewAuthorityProjection:
    request.reviewAuthority.projection,

  repositoryReviewObservations:
    exact complete canonical observations,

  currentReviewCampaignIds:
    currentCampaigns.map(
      campaign => campaign.reviewCampaignId
    ),

  staleProtocolReviewCampaignIds:
    staleProtocolCampaigns.map(
      campaign => campaign.reviewCampaignId
    )
}
```

Runtime-validate, canonical runner JSON serialize, seal as `application/json`
with `repositoryPath = null`, and verify the returned `ArtifactRef`.

Return exactly:

```ts
{
  kind: "current",

  context: {
    runId:
      request.runId,

    qualificationCandidate:
      request.candidate,

    semanticSubject:
      S,

    protocolBundle:
      P,

    currentCampaigns,

    staleProtocolCampaigns,

    authorityEvaluation:
      exact sealed ArtifactRef
  }
}
```

For the same exact `ReviewCurrentnessRequest`, produce the same campaign
universe, observation sequence, byte-identical witness, and CAS `ArtifactRef`.
A different `stateRevision` legitimately changes witness bytes. Add no timestamp
or random value.

## 13. Reviewer prerequisites

### 13.1 Request validation

Require:

```text
candidate.semanticSubject == semanticSubject
reviewAuthority.candidateMaterialization == candidate.materialization
reviewAuthority.protocolBundle == protocolBundle
minimumIndependentReviewers is integer >= 1
reviewerProfiles ordered by profileId unsigned ASCII ascending
reviewerProfiles profile IDs unique
reviewerAcquisition.mode == minimum-effective-independent-v1
reviewerAcquisition.profileOrder contains every reviewerProfiles.profileId
    exactly once and no other ID
reviewAuthority.retryPolicy runtime-validates as
    GateACognitiveRetryPolicyMechanicalFactV1
reviewAuthority.retryPolicy.deterministicallyValidatedRoles is duplicate-free
reviewAuthority.retryPolicy.rolesWithoutDeterministicOutputValidator is
    duplicate-free
every retryPolicy role value belongs to CognitiveExecutionRole
```

Any acquisition-policy or retry-policy structural contradiction is
`MECHANICAL-AUTHORITY-CONTRACT-FAILURE`, not a normal blocker.

Verify the exact projection and evidence `ArtifactRef` values.

Validate and preserve the exact:

```text
reviewAuthority.initialReviewerExecutionInputs
reviewAuthority.retryPolicy
```

Require its prompt and packet to exist and be intact and require every NIB-S
path, SHA, media-type, null-`repositoryPath`, and exact-byte binding. M3 must
not construct the prompt, construct the packet, reread P, reread the repository,
or invoke Python. M3 must return the exact M6-projected value without
transformation.

M3 must not read P, reopen the protocol bundle path, apply retry rules, decide
retry admissibility, compare against hardcoded protocol-v6 values, or
add/remove/reorder either retry-policy role array. M3 does not interpret any
retry-policy value.

### 13.2 Static qualification

Perform only static registry qualification. A profile is statically qualifying
if and only if:

```text
frontierEligible == true

AND

(
  identityResolution.kind == "provider-reported"

  OR

  (
    identityResolution.kind == "pinned-request-model"
    AND
    requestModelIsImmutableVersion == true
  )
)
```

Construct `qualifyingReviewerProfileIds` as the complete qualifying set, sorted
by `profileId` unsigned ASCII ascending. Never select an arbitrary subset.

Separately construct `reviewerAcquisitionCandidates` by traversing exact
`reviewAuthority.reviewerAcquisition.profileOrder` and retaining only
statically qualifying profiles. Never sort that sequence lexically.

For every retained candidate construct exact static identity:

```text
provider-reported
→ staticallyKnownEffectiveIdentity = null

pinned-request-model with immutable version
→ {
    provider: profile.provider,
    modelVersion: profile.requestModel
  }
```

M3 does not establish final execution independence and does not know future
provider-reported `model_version`. Do not:

```text
invent model_version
resolve latest/alias
guess provider_model
deduplicate unknown future provider-reported identities
claim final distinct (provider, model, model_version) count
claim final distinct (provider, model_version) count
```

Those identities are evidence-derived downstream.

Compute exactly:

```text
knownPinned =
set of staticallyKnownEffectiveIdentity
for qualifying pinned candidates

unknownProviderReportedCount =
count qualifying provider-reported candidates

maximumStaticallyPossibleIndependentReviewers =
len(knownPinned) + unknownProviderReportedCount
```

Never deduplicate two provider-reported profiles before execution.

Static prerequisites are established if and only if:

```text
maximumStaticallyPossibleIndependentReviewers >=
    reviewAuthority.minimumIndependentReviewers
```

This is an optimistic maximum only, not final Gate A reviewer-independence
qualification.

### 13.3 Established result

Construct evidence exactly:

```text
firstOccurrenceArtifactRefDedupe([
  reviewAuthority.projection,
  ...reviewAuthority.evidence
])
```

Return exactly:

```ts
{
  kind: "established",
  minimumIndependentReviewers:
    reviewAuthority.minimumIndependentReviewers,
  acquisitionMode:
    "minimum-effective-independent-v1",
  retryPolicy:
    reviewAuthority.retryPolicy,
  qualifyingReviewerProfileIds,
  reviewerAcquisitionCandidates,
  initialReviewerExecutionInputs:
    reviewAuthority.initialReviewerExecutionInputs,
  evidence
}
```

### 13.4 Blocked result

When the complete qualifying set is insufficient, seal or obtain the exact
`reviewer-prerequisites` definition.

Construct exactly:

```ts
ObligationRef {
  obligationId:
    deriveId(
      "campaign-authority-reviewer-prerequisites-obligation.v1",
      candidate.runId,
      candidate.candidateId,
      semanticSubject.selector,
      semanticSubject.sha256,
      protocolBundle.protocolId,
      protocolBundle.sha256,
      definition.sha256
    ),

  runId:
    candidate.runId,

  candidateId:
    candidate.candidateId,

  reviewCampaignId:
    null,

  definition
}
```

Construct exactly:

```ts
ReviewerPrerequisitesUnavailableCauseV1 {
  schema:
    "gate-a-campaign-authority-operational-cause.v1",

  kind:
    "reviewer-prerequisites-unavailable",

  candidateId:
    candidate.candidateId,

  semanticSubject,

  protocolBundle,

  minimumIndependentReviewers:
    reviewAuthority.minimumIndependentReviewers,

  qualifyingReviewerProfileIds,

  maximumStaticallyPossibleIndependentReviewers,

  reviewerAcquisitionProfileIds:
    reviewerAcquisitionCandidates.map(candidate => candidate.profileId),

  reviewAuthorityProjection:
    reviewAuthority.projection
}
```

Use this basis:

```text
firstOccurrenceArtifactRefDedupe([
  reviewAuthority.projection,
  ...reviewAuthority.evidence
])
```

Use `[]` as the exact resolution contracts and return exactly:

```ts
{
  kind: "blocked",
  blockingObligation,
  cause
}
```

## 14. ReviewContext construction

Keep `construct_review_context` pure. Use no artifact store, perform no state
write, and do not recompute currentness.

Apply exactly:

```text
require candidate.runId == request.runId

require campaign.provenance.kind == "runner-produced"

require campaign.provenance.originatingRunId ==
    request.runId

require campaign.provenance.candidateId ==
    candidate.candidateId

require candidate.semanticSubject ==
    campaign.semanticSubject

return exactly:
{
    runId: request.runId,
    candidate: exact request.candidate,
    campaign: exact request.campaign
}
```

Do not perform:

```text
repository-imported campaign acceptance
candidate retargeting
current-candidate substitution
registered-campaign lookup
WorkItem lookup
mutable repository lookup
M2 query
currentness recomputation
```

M2 retains responsibility for subsequently admitting a campaign. For the first
round, `construct_review_context` may therefore receive the exact newly
constructed runner-produced `ReviewCampaignRef` before admission together with
its exact production `CandidateRevisionRef`.

For later rounds, M5 must not call M3 again. It consumes the exact
`reviewContext` retained in the authoritative prerequisite basis.

Preserve production provenance. For example:

```text
REVIEW-X was produced against C1
C2 later becomes current
S(C2) == S(C1)
P unchanged
REVIEW-X remains current
```

The retained `ReviewContext` for `REVIEW-X` continues to name C1, not C2. The
existence of `producedByRepairIntentId` or
`producedByAssuranceProjectionId` on C2 does not retarget `REVIEW-X`.

## 15. Runner-produced campaign construction boundary

Do not construct in M3 the final complete runner-produced `ReviewCampaignRef`
committed after a campaign-required result. M3 establishes only:

```text
reason
candidate
S
P
staleProtocolCampaigns
reviewer prerequisites
```

M1 orchestrates the campaign bundle under NIB-S. M2 independently validates and
adopts it. M3 does not derive `provenance.repositoryAuthority` and does not call
M7 to obtain it. No M3→M7 dependency exists.

## 16. Failure taxonomy and propagation

Define exactly:

```ts
type CampaignAuthorityFailureCodeV1 =
  | "INVALID-REQUEST"
  | "MECHANICAL-AUTHORITY-CONTRACT-FAILURE"
  | "CAMPAIGN-HISTORY-INTEGRITY-FAILURE"
  | "ARTIFACT-INTEGRITY-FAILURE"
  | "CANONICAL-SERIALIZATION-FAILURE"
  | "ARTIFACT-SEAL-FAILURE";
```

No other M3 failure code exists in v1.

For M3 operations other than `construct_review_context`, retain the applicable
`INVALID-REQUEST` mappings, including runtime-invalid requests, run-binding
mismatches, and malformed candidate lineage supplied to currentness.

For `construct_review_context`, map `INVALID-REQUEST` exactly to:

```text
malformed request
candidate.runId mismatch
```

Map `MECHANICAL-AUTHORITY-CONTRACT-FAILURE` to:

```text
M6 result contradicts its accepted structured contract
invalid minimumIndependentReviewers
runtime-invalid M6 retryPolicy
retryPolicy role array contains an invalid CognitiveExecutionRole
retryPolicy role array contains a duplicate role
duplicate/misordered M6 reviewer profiles
duplicate/misordered M6 repository reviews
M6 referencedArtifacts violates its declared structural result contract
impossible candidate-materialization binding
```

For M3 operations other than `construct_review_context`, retain the applicable
`CAMPAIGN-HISTORY-INTEGRITY-FAILURE` mappings, including duplicate registered
`ReviewCampaignId`, incompatible same-ID repository observations, and campaign
history/provenance contradictions.

For `construct_review_context`, map
`CAMPAIGN-HISTORY-INTEGRITY-FAILURE` exactly to:

```text
repository-imported campaign supplied
campaign originatingRunId mismatch
campaign production candidateId mismatch
candidate/campaign semantic-subject contradiction
```

Map `ARTIFACT-INTEGRITY-FAILURE` to:

```text
required ArtifactRef missing/corrupt
sourceRecord integrity failure
referencedArtifacts member integrity failure
hash/length/reference verification failure
```

Map `CANONICAL-SERIALIZATION-FAILURE` to:

```text
M3-owned cause/witness/definition fails M0 runtime validation
canonical serializer rejects an impossible M3-owned value
```

Map `ARTIFACT-SEAL-FAILURE` to:

```text
sealRunnerArtifact fails
returned runner ArtifactRef violates artifact-store contract
newly sealed artifact fails verify()
```

For any `CampaignAuthorityFailureCodeV1`, fail the M3 invocation, return no
normal M3 domain result, create no `OperationalBlocker`, create no
`OPERATOR-ACTION-REQUIRED`, create no `DECISION-REQUIRED`, and propose no M2
authoritative mutation.

Only the three explicit NIB-S M3 operational causes produce normal blocked
results. Do not catch an integrity failure and reinterpret it as an operational
blocker.

## 17. Retry, interruption, replay, and determinism

Implement zero internal retry loops. Add no retry counter, backoff, fallback
authority, or second source. Replay is orchestrator-owned.

Apply this interruption behavior:

```text
crash before M3 seal
→ no authoritative effect

seal succeeds, crash before return
→ unreferenced valid CAS artifact may remain

M3 returns, crash before M2 admission
→ M3 result remains non-authoritative
→ replay from authoritative snapshot is legal

M2 commit succeeds
→ returned M2 snapshot is authority on restart
→ no cached M3 result overrides it
```

Permit orphan CAS artifacts.

For identical immutable inputs require:

```text
preflight
→ same normal result / same cause bytes

resolve_currentness
→ same observations
→ same merge
→ same classification
→ same witness bytes when current

verify_reviewer_prerequisites
→ same exact preserved retry policy
→ same qualifying set
→ same result / same blocking obligation and cause

construct_review_context
→ same pure ReviewContext
```

Use no clock, randomness, repository traversal ordering, database row ordering,
unordered `Map`/`Set` iteration as serialized authority, environment-selected
model/provider, or network state.

## 18. Required edge cases

Implement these exact outcomes:

```text
preflight reviewAuthority.invalid
→ blocked preflight cause
→ no new M3 blocking obligation

current candidate reviewAuthority.invalid
→ current-review-authority obligation + blocked cause

zero reviewer profiles
→ reviewer-prerequisites blocked

frontierEligible=false
→ profile excluded

pinned-request-model with requestModelIsImmutableVersion=false
→ profile excluded

provider-reported + frontierEligible=true
→ statically eligible
→ M3 does not invent model_version

exactly minimum statically possible effective identities
→ established

more than minimum qualifying profiles
→ ALL qualifying profile IDs returned
→ acquisition candidates remain exact P order, not lexical order

duplicate immutable pinned effective identities
→ counted once in maximum static capacity
→ later duplicate pinned candidate remains absent from an acquisition round

provider-reported profiles with similar request metadata
→ each contributes one optimistic unknown capacity
→ never pre-collapsed

same registered/repository ReviewCampaignId compatible
→ one logical campaign, existing provenance preserved

same ID incompatible
→ CAMPAIGN-HISTORY-INTEGRITY-FAILURE

repository-imported campaign may satisfy currentness

candidate changed only by assurance projection, same S/P, current campaign exists
→ current

candidate changed by repair but S unchanged, same P, current campaign exists
→ current

candidate S changed, no same-S current/stale campaign
→ SUBJECT-CHANGED

same S + stale P exists + no current P campaign
→ PROTOCOL-CHANGED

C0/no campaign
→ INITIAL

repository review over different S
→ remains in repositoryReviewObservations
→ absent from current/stale sets

repository review referencedArtifacts
→ copied exactly
→ not reordered/deduplicated/rederived

current campaign + stale campaigns
→ current
→ stale list remains complete

ReviewContext construction with imported campaign
→ failure

ReviewContext construction with candidate.runId mismatch
→ INVALID-REQUEST

ReviewContext construction with campaign run/candidate/subject contradiction
→ CAMPAIGN-HISTORY-INTEGRITY-FAILURE

Later-round WorkItem construction
→ M5 consumes exact retained ReviewContext
→ no new M3 invocation
```

## 19. Forbidden behavior

Do not implement any of the following in M3:

```text
direct Git invocation
direct Python invocation
mutable repositoryPath reread
protocol-bundle parsing from repository
review-record parsing from repository
referencedArtifacts closure derivation
referencedArtifacts sorting/deduplication
subject recomputation
protocol identity recomputation from mutable bytes
reviewer-profile invention
arbitrary reviewer subset selection
model alias promotion
model_version invention
final effective-reviewer-independence assertion
campaign retargeting
imported treeSha fabrication
candidate provenance filtering of currentness
special currentness semantics for assurance projection candidates
repository provenance filtering of currentness
filesystem-order campaign ordering
direct authoritative state writes
OperationalBlocker construction
BlockerId construction
OAR construction
operator-resolution interpretation
time/randomness in M3 identities
silent deduplication of duplicate authoritative registered campaigns
integrity failure → operational blocker conversion
runner-produced repositoryAuthority provenance derivation
M3→M7 dependency
```

## 20. Invariants

### M3-01

M3 never mutates authoritative campaign state.

### M3-02

M3 directly invokes neither Git, Python, repository traversal, provider APIs nor
network authority.

### M3-03

Every normal M3 operational cause has `producer == campaign-authority`.

### M3-04

No M3 blocked result contains an `OperationalBlocker`.

### M3-05

Preflight established binds exactly one sealed baseline materialization to exact
M6-established S and P.

### M3-06

M6 `reviewAuthority.invalid` is never partially interpreted.

### M3-07

Registered authoritative campaign IDs are unique.

### M3-08

Campaign universe equals registered campaigns merged with the complete
mechanically projected repository-review corpus by `ReviewCampaignId`.

### M3-09

A compatible same-ID repository observation never retargets an existing
campaign.

### M3-10

An incompatible same-ID observation fails closed.

### M3-11

Current/stale applicability depends only on exact S and P.

### M3-12

Candidate repair/assurance-projection provenance never independently changes
campaign applicability.

### M3-13

`currentCampaigns` and `staleProtocolCampaigns` are duplicate-free and ordered
by `ReviewCampaignId` unsigned ASCII ascending.

### M3-14

Currentness precedence is current, PROTOCOL-CHANGED, SUBJECT-CHANGED, INITIAL.

### M3-15

Candidate-only change cannot require a campaign while an exact current `(S,P)`
campaign exists.

### M3-16

Every current resolution has exactly one sealed
`GateACampaignAuthorityEvaluationV1` witness.

### M3-17

The authority-evaluation witness is bound to exact `StateRevision`.

### M3-18

The `RepositoryReviewObservationV1` sequence is complete for exact M6
`repositoryReviews` and ordered by `ReviewCampaignId`.

### M3-19

Every `RepositoryReviewObservationV1.referencedArtifacts` sequence equals the
exact M6-projected sequence without modification.

### M3-20

`qualifyingReviewerProfileIds` is the complete statically qualifying profile-ID
set and never an arbitrary subset. `reviewerAcquisitionCandidates` contains
that same qualifying set in exact P acquisition order.

### M3-20A

M3 static capacity equals distinct known pinned effective identities plus the
count of qualifying provider-reported profiles.

### M3-21

M3 does not claim final effective reviewer independence before execution
evidence exists.

### M3-22

M3 current-review-authority blocking `ObligationId` is deterministic.

### M3-23

M3 reviewer-prerequisites blocking `ObligationId` is deterministic over exact
run/candidate/S/P/definition identity.

### M3-24

M3 cause descriptors contain no occurrence-only
`StateRevision`/session/time/path/retry/random material.

### M3-25

Only `preflight-review-authority-invalid` permits
`request-operational-recheck`.

### M3-26

Both post-preflight M3 causes have `resolutionContracts == []`.

### M3-27

`construct_review_context` accepts only the exact supplied runner-produced
campaign and performs no campaign or WorkItem lookup.

### M3-28

`ReviewContext` always preserves the exact supplied production candidate and
campaign.

### M3-29

Reusing a current campaign for a later same-`(S,P)` candidate never rewrites
campaign production provenance.

### M3-30

M3 performs zero internal retry loops.

### M3-31

Same immutable inputs yield byte-identical M3-owned serialized artifacts.

### M3-32

No M3 cache is authority.

## 21. Construction boundary

M0 final closure must expose all runtime validators and pure deterministic
canonical/ID helpers consumed by M3 before GREEN.

`CampaignArtifactStore` is already selected by M2.

M3 requires no external Dependency Contract.

The future coding agent must not choose:

```text
campaign merge semantics
currentness semantics
reviewer prerequisite filtering
initial-reviewer execution-input preservation
cause types
blocking obligation identities
authority witness shape
repository observation closure handling
ReviewContext provenance
failure classes
retry semantics
```
