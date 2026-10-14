---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-14"
step_id: 2
id: NIB-M-GATE-A-ASSURANCE-LEDGER-FINDING-ADJUDICATION
version: "1.0.0"
scope: gate-a-campaign-runner/assurance-ledger/finding-adjudication
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Assurance Ledger — Finding Adjudication

## 1. Status and authority

Implement M5-B `review evidence / finding adjudication` as construction
authority only.

Consume exactly:

```text
NIB-S-GATE-A-CAMPAIGN-RUNNER 12.0.0
NIB-M-GATE-A-CONTRACTS 1.3.0
NIB-M-GATE-A-CAMPAIGN-STATE-PERSISTENCE-OWNERSHIP 3.0.4
NIB-M-GATE-A-CAMPAIGN-STATE-MUTATION-EXECUTION 8.0.0
NIB-M-GATE-A-CAMPAIGN-STATE-SNAPSHOT-INTEGRITY 7.0.0
NIB-M-GATE-A-ASSURANCE-LEDGER-CAMPAIGN-WORK-EXECUTION-RECEIPT 3.0.0
NIB-M-GATE-A-MECHANICAL-VALIDATION 1.1.0
ADR-055
ADR-056
exact closed protocol-v8 C1-C7 authority
exact immutable P6 and inactive P8 bundles
```

P6 is current. P7 is immutable and permanently inactive. P8 is immutable,
mechanically valid and inactive until C15. Create no product or protocol
semantics, ADR, activation, provider/model rule, retry rule or new dependency.

## 2. Responsibility boundary

Own exactly:

```text
immutable current/stale ReviewCampaign finding intake
repository-imported review EvidenceRef construction
runner-produced one-to-one raw-finding normalization
repository-imported finding import into FindingRef
finding-resolution ObligationRef construction
P8 FindingAdjudicationBasis initiation
P8 materiality progression
P8 refutation progression
P8 materiality/refutation challenge requirements
P8 bounded revisions for those two families
P8 positive qualification consumption
P8 SurvivingMaterialBasis construction request
P8 finding-adjudication supplement-v2 construction
M5 P8 run-local semantic AdjudicationRef projections for M5-B semantic uses
P6 fail-closed post-review automation boundary
replay/idempotence
```

Do not own:

```text
Discovery
UniqueCorrection
DecisionNecessity
RealizationScope
RepairRealization
RepairIntent
DecisionRequest
repository mutation
Gate A readiness
Python
M2 writes
```

## 3. Inputs and contribution

Consume exact `AssuranceDerivationRequest`, its authoritative snapshot, exact
`GateAEvaluationContext`, and only repository observations retained by exact
`GateACampaignAuthorityEvaluationV1`.

Return an M5-B contribution containing only M5-B-owned:

```text
EvidenceRefs
FindingRefs
AdjudicationRefs
ReAdjudicationRefs
finding-resolution ObligationRefs
ObligationDispositionRefs
P8 semantic WorkItem requirements/products
operational blocker requests
repository-facing supplement artifacts for later M5-D selection
```

Return neither assurance-projection nor readiness scalar. Mutate no authority.
When a required M6 result is missing, expose the exact required mechanical
operation to M1; never guess identity or skip validation.

## 4. Normalized finding artifact

Define exactly:

```ts
interface GateANormalizedFindingArtifactV1 {
  readonly schema:
    "gate-a-normalized-finding.v1";
  readonly findingId: FindingId;
  readonly sourceReviewExecutionId:
    HostileReviewExecutionId;
  readonly rawFindingId: string;
  readonly statement: string;
  readonly argument: string;
  readonly counterexample: string | null;
}
```

Include no materiality, status, disposition, challenge, repair or candidate
status. Seal canonical runner JSON. Treat it as operational normalization
material, not independent semantic authority.

## 5. Runner-produced finding normalization

For each qualified initial-reviewer receipt, read the exact qualifying raw
review output and traverse raw `findings[]` order.

Require:

```text
one raw finding → exactly one FindingRef
no semantic merge
no semantic deduplication
no one-to-many split
```

For each raw finding set exactly:

```text
sourceReviewExecutionId = source WorkItemId
sourceRunnerExecutionId = qualifying receipt attempt ExecutionId
rawFindingId = exact raw finding id
findingId = deriveId(
  "assurance-ledger-runner-finding.v1",
  reviewCampaignId,
  sourceReviewExecutionId,
  rawFindingId
)
candidateId = source ReviewCampaign production candidate
evidenceIds = [corresponding initial-reviewer receipt EvidenceId]
```

Seal one exact `GateANormalizedFindingArtifactV1`; bind it as
`normalizedFinding`.

## 6. Repository-imported finding intake

Consume imported evidence only through
`GateACampaignAuthorityEvaluationV1.repositoryReviewObservations`. Read only
exact `sourceRecord` and `referencedArtifacts` through `CampaignArtifactStore`.
Never scan mutable repository state.

For each exact source-record finding set:

```text
findingId = exact source finding_id
candidateId = null
sourceReviewExecutionId = exact finding.sources[0].execution_id
sourceRunnerExecutionId = null
rawFindingId = exact finding.sources[0].raw_finding_id
```

Preserve exact source finding identity. Do not rederive it.

Create one imported `EvidenceRef` for the source record:

```text
evidenceId = deriveId(
  "assurance-ledger-imported-review-evidence.v1",
  runId,
  reviewCampaignId,
  sourceRecord.sha256
)
candidateId = null
reviewCampaignId = exact imported campaign
sourceExecutionIds = []
artifact = exact sourceRecord
```

Every imported `FindingRef` references that EvidenceId. Never fabricate runner
Execution or WorkItem provenance.

## 7. Canonical finding order

Order every applicable target under one current `(S,P)` by:

```text
1. source ReviewCampaignId unsigned UTF-8/ASCII ascending
2. source FindingId unsigned UTF-8 ascending
```

Use this as the sole M5-B/M5-C progression order. Do not order by severity,
confidence, text, model, provider, candidate, completion time, repository path
or scheduler order.

## 8. Finding-resolution obligation

For each applicable source-finding/current-P pair establish exactly one
`finding-resolution` obligation with:

```text
deriveId(
  "assurance-ledger-finding-resolution-obligation.v1",
  runId,
  sourceReviewCampaignId,
  findingId,
  currentProtocolBundle.protocolId,
  currentProtocolBundle.sha256
)
```

Use the exact shared definition:

```json
{
  "schema": "gate-a-assurance-ledger-obligation-definition.v1",
  "kind": "finding-resolution"
}
```

Keep it outstanding until qualified non-materiality, qualified refutation,
subject-change inapplicability, or supersession by a new-current-P obligation.

Disposition is exactly:

```text
QualifiedNonMateriality → satisfied
QualifiedRefutation → satisfied
subject change → superseded with replacementObligationIds = []
protocol change with same S → superseded by exact new-P obligation
```

Surviving materiality, repair, NoNormativeImpact and DecisionRequest never
satisfy it.

## 9. P8 initiation

M5 selects the exact finding/current authority and asks M6
`project_protocol_v8_finding_adjudication_basis`. Require returned exact
`FindingAdjudicationBasisV1`, validated `SemanticValueRefV1`, substantive
finding SHA and non-empty evidence.

M5 computes no SemanticValueId and no hostile-finding subject SHA.

Select the adjudicating campaign as
`evaluationContext.currentCampaigns[0]`. It may be runner-produced or imported.
Construct `ResolutionContextV1` with exact current candidate, S, P, selected
campaign and exact FA canonical value artifact as `resolutionSubject`.

## 10. Exact P8 adjudication order

Process applicable findings in canonical order. For one finding:

```text
FindingAdjudicationBasis
↓
MaterialityAssessmentInitial
↓
materiality qualification/challenge/revision
↓
QualifiedNonMateriality
  → non-blocking supplement
  → satisfy obligation
OR QualifiedPositiveMateriality
↓
RefutationInitial
↓
refutation challenge/revision/exhaustion
↓
QualifiedRefutation
  → non-blocking supplement
  → satisfy obligation
OR RefutationExhaustionWithoutQualifiedRefutation
↓
SurvivingMaterialBasis
↓
surviving-material supplement
↓
M5-C
```

Never branch on model convenience.

## 11. Materiality progression

Apply exactly:

```text
initial any axis true
→ QualifiedPositiveMateriality
→ no materiality challenge

initial all axes false
→ MaterialityChallenge

initial challenge zero objections
→ QualifiedNonMateriality

initial challenge objections
→ mandatory MaterialityAssessmentRevision when current and operationally admissible

revised any axis true
→ QualifiedPositiveMateriality
→ no second materiality challenge

revised all axes false
→ fresh MaterialityChallenge

fresh revised challenge zero objections
→ QualifiedNonMateriality

fresh revised challenge objections
→ no positive qualification
→ materiality closure unresolved
→ operator path
```

Never convert objections into positive materiality. Allow no second materiality
revision.

## 12. Refutation progression

After exact QPM:

```text
RefutationInitial NotEstablished
→ RefutationExhaustionWithoutQualifiedRefutation

initial positive
→ RefutationChallenge

challenge zero objections
→ QualifiedRefutation

initial positive + challenge objections
→ mandatory RefutationRevision

revision NotEstablished
→ RefutationExhaustionWithoutQualifiedRefutation

positive revision
→ fresh RefutationChallenge

fresh challenge zero objections
→ QualifiedRefutation

fresh challenge objections
→ RefutationExhaustionWithoutQualifiedRefutation
```

Operational failure is not exhaustion. Allow no second revision.

Use M6 progression view, Fact-descriptor validation and qualification reduction.
M5 computes no QLEK, FactId or QualificationKey.

## 13. SurvivingMaterialBasis

Only after exact FA, exact `QualifiedPositiveMateriality` Fact and exact
`RefutationExhaustionWithoutQualifiedRefutation` Fact, construct the proposed C2
value and ask M6 semantic-value validation for its exact ref and bytes.

M5 never computes `SemanticValueId`.

## 14. P8 supplement-v2

Construct exactly one `finding-adjudication-supplement-v2` candidate per
completed P8 adjudication. Its semantic key is:

```text
source ReviewCampaignId
+ source FindingId
+ M6-validated substantiveFindingSha256
+ exact current P
```

Project exactly one effective state:

```text
qualified-non-material → QualifiedNonMateriality SemanticFactRef
qualified-refutation → QualifiedRefutation SemanticFactRef
surviving-material → SurvivingMaterialBasis SemanticValueRef
```

Include no receipts, supporting executions, witness ownership, candidate or
run/root identity. Seal exact schema-v2 bytes and validate against its exact
published schema. The later M5-D path is
`formal/reviews/supplements/<supplement.sha256>.json`.

## 15. Re-adjudication projection

For every P8 supplement, same-P or stale-P, create one `ReAdjudicationRef` with:

```text
reAdjudicationId = deriveId(
  "assurance-ledger-readjudication.v1",
  runId,
  sourceReviewCampaignId,
  sourceFindingId,
  currentProtocolBundle.protocolId,
  currentProtocolBundle.sha256,
  sourceFindingSha256
)
sourceReviewCampaignId
sourceFindingId
currentProtocolBundle
sourceFindingSha256
artifact = supplement ArtifactRef
```

Use `evidenceIds` only for local EvidenceIds genuinely owned by this run;
otherwise use `[]`. Never transfer predecessor receipt ownership.

## 16. Run-local semantic-use projection

For each consumed P8 Admission, create at most one `AdjudicationRef` using the
M0 exact formula and an exact `GateAM5SemanticUseProjectionV1` owned by the
complete M5 contract.

Map Materiality to `materiality`, Refutation to `refutation`, and their
challenges to `hostile-challenge`. For reused cross-root truth, local receipt,
witness, packet and prompt fields are null and both sourceExecutionIds and
evidenceIds are empty. This audit projection is not SemanticAdmission authority.

## 17. P6 fail-closed boundary

P6 remains current. Import and consume existing complete mechanically valid P6
repository evidence. A runner-produced P6 campaign with zero findings may
complete normally.

If a runner-produced P6 campaign has raw findings requiring new post-review
cognitive semantic interpretation:

```text
no P8 question
no P7 behavior
cause.kind = p6-post-review-automation-unavailable
resolutionContracts = []
```

Do not invent structured P8 semantics. This changes no P6 semantics.

## 18. Replay, failures and edge cases

Derive exact identity first. If absent, emit; if exact identity/payload exists,
emit nothing; if same identity conflicts, fail
`ASSURANCE-HISTORY-INTEGRITY-FAILURE`.

Use only:

```text
INVALID-ASSURANCE-DERIVATION-REQUEST
ASSURANCE-HISTORY-INTEGRITY-FAILURE
ASSURANCE-ARTIFACT-INTEGRITY-FAILURE
ASSURANCE-ARTIFACT-SEAL-FAILURE
ASSURANCE-SEMANTIC-CLOSURE-INTEGRITY-FAILURE
ASSURANCE-FINALIZATION-INTEGRITY-FAILURE
```

Implementation/integrity failures are not Decision Required, Operator Action
Required, protocol-invalid or NotEstablished. Normal no-continuation uses exact
M5 cause material for M8-B.

## 19. Invariants

```text
M5B-01 Every raw finding maps exactly once.
M5B-02 M5-B performs no semantic finding merge or deduplication.
M5B-03 Imported findings fabricate no local WorkItem or Execution.
M5B-04 Runner finding source binds exact logical WorkItem and qualifying attempt.
M5B-05 Finding-resolution obligation identity is current-P scoped.
M5B-06 Only QualifiedNonMateriality closes a finding as non-material.
M5B-07 Only QualifiedRefutation closes a finding as refuted.
M5B-08 Materiality objections never imply positive materiality.
M5B-09 Refutation failure never proves finding truth.
M5B-10 Operational failure never establishes semantic exhaustion.
M5B-11 SurvivingMaterialBasis requires exact QPM and refutation exhaustion.
M5B-12 P8 supplement owns no receipt provenance.
M5B-13 One semantic key has at most one supplement.
M5B-14 Same-P and stale-P findings use the same P8 adjudication rules.
M5B-15 P6 is never silently upgraded to P8.
M5B-16 Historical evidence is immutable.
M5B-17 Repository evidence is consumed only through retained observations.
M5B-18 Reused semantic truth transfers no receipt ownership.
M5B-19 P7 remains permanently inactive.
M5B-20 P8 remains inactive until C15.
```

## 20. Future tests

Create no NIB-T here. Require tests for imported finding without local
Execution, runner source identity split, deterministic FindingId, one-to-one raw
order, source-finding SHA mismatch, all-false materiality revision, each exact
refutation-exhaustion branch, supplement key collision, same-P/stale-P parity,
imported adjudicating campaign via ResolutionContextV1, P6 zero-finding
regression, P6 fail-closed cause, no receipt transfer, P7 inactive and P8
inactive.

## 21. Forbidden behavior

Explicitly forbid:

```text
LLM calls directly from M5
Python invocation directly from M5
QLEK computation in TypeScript
SemanticValueId computation in M5
FactId computation in M5
QualificationKey computation in M5
packet semantics duplicated in TypeScript
semantic result retry
model shopping
profile substitution after WorkItem selection
receipt/root ownership as semantic predecessor authority
copying reused predecessor receipts into consuming root
candidate equality by bytes replacing CandidateRevision identity
candidate-bound scope rebasing
RepairIntent rebasing
patch widening
empty RepairIntent
DecisionRequest from mere failure to derive
operator action as semantic truth
P8 decision-projection cognitive work
M5-created OperationalBlocker
M5 direct M2 mutation
M5 direct repository mutation
readiness from partial work
P8 activation
P7 activation
```

Also forbid mutable repository scans, semantic finding merge, imported Execution
fabrication, arbitrary semantic JSON number round-trip, Unicode normalization,
float conversion, integer rounding and semantic-payload key reordering.

## 22. Construction classification

```text
statement:
complete M5-B construction follows accepted NIB-S 12.0.0, ADR-055, ADR-056 and
closed protocol-v8 C1-C7 authority without introducing semantic choices

semantic disposition:
derived-from-existing-authority

affected layer:
architecture-or-implementation

normative impact:
none
```

The FindingRef split, canonical target order, internal normalized artifact and
supplement projection mechanics are `no-normative-impact`
`architecture-or-implementation` mechanisms. No ADR is required.
