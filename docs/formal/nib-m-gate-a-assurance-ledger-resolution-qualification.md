---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-14"
step_id: 2
id: NIB-M-GATE-A-ASSURANCE-LEDGER-RESOLUTION-QUALIFICATION
version: "1.1.0"
scope: gate-a-campaign-runner/assurance-ledger/resolution-qualification
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Assurance Ledger — Resolution Qualification

## 1. Status and authority

Implement M5-C `resolution qualification` from NIB-S 13.0.1, M0 1.5.0, M2
3.0.4/9.1.0/8.1.0, M5-A 3.1.0, M5-B 1.1.0, M6 1.2.0, ADR-055, ADR-056 and
closed P8 C1-C7 authority.

Version `1.1.0` additively makes the existing M5-C-to-M6 choreography boundary
mechanically callable. It changes no semantic progression, canonical finding
selection, DecisionRequest justification, repair qualification, retry,
provider/model rule or protocol activation.

P6 is current. P7 is permanently inactive. P8 remains inactive until C15. This
brief creates construction authority only and no product/protocol meaning,
activation, provider/model, dependency or retry decision.

## 2. Responsibility boundary

Own exactly:

```text
SurvivingMaterial intake
Discovery progression
exact earliest-unresolved Discovery target selection
NoNormativeImpact qualification progression
UniqueCorrection progression
DecisionNecessity progression
DecisionRequest construction
SemanticBlocker construction
candidate-bound RealizationScope progression
candidate-bound RepairRealization progression
RepairIntent construction
deterministic multi-finding repair selection
operational no-safe-continuation causes
ResolutionContextV1 construction for M5-C work
replay/idempotence
```

Do not answer DecisionRequest, apply patches, mutate repository, invoke Python,
write M2, declare Gate A ready, make findings non-material, or refute findings
through repair.

## 3. Exact finding serialization

Process one surviving-material finding at a time. Select the first outstanding
surviving-material finding in canonical M5 order:

```text
source ReviewCampaignId unsigned UTF-8/ASCII ascending
then source FindingId unsigned UTF-8 ascending
```

Do not derive semantic WorkItems for a later finding while the selected finding
has a legitimate automatic continuation. This guarantees at most one enabled
candidate-bound repair realization, removes scheduler timing from repair order,
and forces complete rederivation after candidate advance.

## 4. Discovery target

For `DiscoveryClassificationInitial@1`, target exactly the statement named by
`earliest_unresolved_cause.classification_statement_ordinal`. Consume only the
exact `targetedStatementFact` projected by M6. Keep sibling statements immutable
and unscheduled until the target resolves or progression stops.

M5 chooses no alternate statement. For positive Discovery revision, consume the
exact revised targeted-statement Fact. For `NotEstablished`, the M6 progression
view has null target/disposition and M5 enters the prescribed operator path.

## 5. Disposition routing

### 5.1 Derived from existing authority

Attempt ordinary UniqueCorrection. Accepted UC proceeds to candidate-bound
realization. Lawful UC exhaustion produces no DecisionRequest and enters the
operator path.

### 5.2 No normative impact

Require exact `NoNormativeImpactChallenge` and bounded revision. Only exact
`QualifiedNoNormativeImpact` permits ordinary UniqueCorrection. Failed NNI
closure establishes neither normative impact nor decision-required and enters
the operator path. UC exhaustion after QNNI also enters the operator path.

### 5.3 Decision required

Require ordinary UniqueCorrection first.

```text
AcceptedUniqueCorrection → candidate realization
UniqueCorrectionExhaustion
→ DecisionNecessityCandidate
→ DecisionNecessityChallenge
```

Zero objections yield `QualifiedDecisionNecessity`, then mechanical
DecisionRequest and SemanticBlocker.

Challenge objections require one `DiscoveryDecisionRequiredRevision`. If the
revision remains positively decision-required, forbid reuse of old UC
exhaustion and run a fresh UC path. Only fresh UC exhaustion permits a fresh
DecisionNecessityCandidate and challenge. Allow no second Discovery
decision-required revision. Failed final decision-necessity closure enters the
operator path. Revision `NotEstablished` withdraws the decision-required
closure, establishes no opposite, and enters the operator path.

### 5.4 Authority conflict or uncertain

Attempt ordinary UniqueCorrection. Accepted UC proceeds to realization. UC
exhaustion never manufactures DecisionRequest and enters the operator path.

## 6. UniqueCorrection progression

```text
UniqueCorrectionInitial NotEstablished
→ UC exhaustion

initial positive
→ UniqueCorrectionChallenge

challenge zero objections
→ AcceptedUniqueCorrection

initial positive + challenge objections
→ mandatory UniqueCorrectionRevision

revision NotEstablished
→ UC exhaustion

positive revision
→ fresh UniqueCorrectionChallenge

fresh challenge zero objections
→ AcceptedUniqueCorrection

fresh challenge objections
→ UC exhaustion
```

Allow no second revision or branch switching.

## 7. Candidate-bound RealizationScope

Proceed only after exact `AcceptedUniqueCorrection`. Obtain exact current
CandidateRevision C and exact complete CandidateView(C) through accepted M7/M6
boundaries. M5-C never constructs CandidateView bytes.

Run `RealizationScopeInitial`. A positive candidate requires exact challenge.
Zero objections yield `AcceptedRealizationScope`. Initial objections permit one
mandatory `RealizationScopeRevision` retaining the same C, complete
CandidateView and AcceptedUC. Do not reselect current candidate inside revision.

`NotEstablished` or revised surviving objections enter the operator path.
Candidate advance leaves old RS historical and requires fresh RS Initial.

## 8. Candidate-bound RepairRealization

After exact AcceptedRS, construct exact scoped CandidateView(C) through M7/M6;
coverage equals exactly `AcceptedRealizationScope.readable_paths`.

Run `RepairRealizationInitial`. Positive output requires repair challenge. Zero
objections yield `AcceptedRepairRealization`. Initial objections permit one
mandatory `RepairRealizationRevision` retaining same C, AcceptedUC, AcceptedRS
and scoped CandidateView. Allow no second revision. `NotEstablished` or revised
surviving objections enter the operator path.

## 9. RepairIntent construction

Only exact AcceptedRepairRealization Fact may authorize RepairIntent. Consume
its exact M6 resolved semantic view.

If `operations == []`, require every requirement is exact `already-realized`.
Create no RepairIntent, empty patch or repair-only successor. The surviving
finding remains blocking; emit operator cause reason
`surviving-material-already-realized`.

For non-empty operations, construct exact `GateAExactCandidatePatchV1` with:

```text
sourceMaterialization = exact current CandidateRevision.materialization
one operation per unique path
canonical raw path order
no path outside AcceptedRS.writable_paths
no physical no-op
all before states match exact scoped CandidateView
no scope expansion
```

For each operation:

```text
pathBytesBase64url = exact qualified path bytes
before = exact CandidateView state
after absent = null
after blob utf-8/base64url = exact decoded/sealed bytes and blob state
after symlink = exact decoded/sealed target bytes and symlink state
after gitlink = exact object_id
```

Seal the patch, then derive:

```text
deriveId(
  "assurance-ledger-repair-intent.v1",
  runId,
  candidateId,
  findingId,
  acceptedRepairRealizationFact.factId,
  approvedPatch.sha256
)
```

Use only locally owned EvidenceIds in `qualificationEvidenceIds`. Build
`qualificationArtifacts` by canonical first-occurrence dedupe over AcceptedRR
Fact/ref/evidence, AcceptedRS evidence, AcceptedUC evidence, exact scoped
CandidateView and approved patch. Never transfer predecessor receipt ownership.

## 10. Candidate advance

Old RS/RR, RepairIntent and patch remain exact-candidate-bound and historical;
never retarget or rebase them.

If S changes, supersede the old finding-resolution obligation with no
replacement and require a new campaign under existing authority. If S remains,
retain applicable campaign/finding and reusable candidate-independent truth,
but require fresh candidate-bound RS/RR before further automatic progression.

## 11. DecisionRequest and SemanticBlocker

Only `QualifiedDecisionNecessity` may create one DecisionRequest.

Define:

```ts
interface GateADecisionRequestArtifactV1 {
  readonly schema: "gate-a-decision-request.v1";
  readonly findingId: FindingId;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly sourceFinding: ArtifactRef;
  readonly qualifiedDecisionNecessity: SemanticFactRefV1;
  readonly decisionBasis: ArtifactRef;
}
```

Use the exact M6 resolved semantic view as `decisionBasis`; do not paraphrase or
answer it.

Derive:

```text
decisionRequestId = deriveId(
  "assurance-ledger-decision-request.v1",
  runId,
  findingId,
  semanticSubject.sha256,
  protocolBundle.sha256,
  qualifiedDecisionNecessityFact.factId
)

blockerId = deriveId(
  "assurance-ledger-semantic-blocker.v1",
  runId,
  decisionRequestId
)
```

Bind the SemanticBlocker to exact finding-resolution obligation, finding,
DecisionRequest and request artifact. This is the only M5-C route to
Decision Required. M8 never constructs this semantic blocker.

## 12. Supporting profile selection

Consume the exact current `reviewAuthorityProjection` named by
`GateACampaignAuthorityEvaluationV1`; never reread mutable P.

Traverse exact `reviewerAcquisition.profileOrder` and select the first profile
satisfying:

```text
frontierEligible == true
AND
(
  identityResolution.kind == provider-reported
  OR
  (identityResolution.kind == pinned-request-model
   AND requestModelIsImmutableVersion == true)
)
```

There is no profile consumption, supporting-role round, collision expansion or
producer/challenger identity inequality. Reuse the same profile across semantic
WorkItems when selected by this rule.

For provider-reported selection set known effective identity null. For pinned
immutable selection set `{provider, modelVersion: requestModel}`. If no profile
qualifies when work is required, emit `supporting-role-unavailable` with
`resolutionContracts = []`; never Decision Required.

## 13. Adjudicating campaign and ResolutionContext

Require at least one current campaign and select exactly
`evaluationContext.currentCampaigns[0]`, whose order M3 owns. Permit
runner-produced or repository-imported provenance. Treat it only as execution
provenance and not a QLEK input.

Construct exact `ResolutionContextV1` from runId, exact current candidate,
selected campaign, exact S, exact P and immutable resolution subject. Use FA
canonical value for M5-B materiality/refutation and SM canonical value for M5-C.

## 14. P8 semantic WorkItem

Only after M6 returns `ValidatedSemanticQuestionRefV1`, and M2 establishes no
consumable Admission and lawful execution authority, construct a WorkItem:

```text
workItemId = deriveId(
  "assurance-ledger-semantic-work-item.v1",
  runId,
  qlek
)
runId = current run
candidateId = exact current candidate
reviewCampaignId = selected adjudicating current campaign
sourceObligationIds = [exact finding-resolution obligation]
executor = cognitive-execution
```

Obtain exact role/prompt/packet from M6
`project_protocol_v8_semantic_execution_inputs`, construct exact M4 operation
with ResolutionContext, selected candidate, prompt and packet, ask M4 to seal,
and set `inputRefs = [prompt, packet]`. M5 invokes no provider.

Outstanding WorkItem blocks candidate/repository advancement by the accepted
progression choreography; do not add candidate identity to QLEK.

## 15. Reuse-first rule

Before any dispatch, M1/M2 resolves exact K.

```text
consumable Admission → no WorkItem/provider; reuse and derive Facts
unresolved hazard → no new dispatch
pending protocol-valid completion → reconcile first
conflict → no winner; integrity/conflict path
```

Never convert run/root mismatch into resampling.

## 16. Run-local semantic-use projection

For each P8 Admission consumed by M5-B/C, create at most one `AdjudicationRef`
per M0 formula and seal:

```ts
interface GateAM5SemanticUseProjectionV1 {
  readonly schema: "gate-a-m5-semantic-use-projection.v1";
  readonly findingId: FindingId;
  readonly semanticQuestionContract:
    SemanticQuestionContractRevisionId;
  readonly qlek: QLEK;
  readonly admissionId: SemanticAdmissionId;
  readonly semanticQuestionBinding: ArtifactRef;
  readonly localOriginWitness: ArtifactRef | null;
  readonly localExecutionReceipt: ArtifactRef | null;
  readonly localPacket: ArtifactRef | null;
  readonly localPrompt: ArtifactRef | null;
}
```

For reused truth all local fields are null and sourceExecutionIds/evidenceIds
are empty. For locally produced truth, bind exact local package and receipt
attempts/EvidenceId.

Map exact P8 roles:

```text
MaterialityAssessment* → materiality
Refutation* → refutation
Materiality/Refutation/NNI/UC/RS Challenge → hostile-challenge
DecisionNecessityChallenge → decision-necessity
RepairRealizationChallenge → repair-challenge
Discovery*/UniqueCorrection*/RealizationScope*/RepairRealization* → derivation
```

Never emit P8 `decision-projection`. AdjudicationRef is run-local audit and
progression projection, not Admission authority.

## 17. Exact semantic question dependencies

Copy exact revision IDs and logical-input keys from the published 20-SQC
catalog. Preserve at least these exact edges:

```text
MaterialityInitial: FA
MaterialityRevision: FA + prior assessment Admission + prior challenge Admission
MaterialityChallenge: challenged assessment Admission
RefutationInitial: FA + QPM Fact
RefutationRevision: FA + QPM + prior refutation Admission + prior challenge Admission
RefutationChallenge: challenged refutation Admission
DiscoveryInitial: SM
NoNormativeImpactChallenge: TargetedDiscoveryStatement Fact
DiscoveryNoNormativeImpactRevision: SM + prior NNI statement Fact + prior challenge Admission
UniqueCorrectionInitial: SM + producer Discovery Admission + targeted statement Fact
UniqueCorrectionRevision: same + prior UC Admission + prior challenge Admission
UniqueCorrectionChallenge: challenged UC Admission
DecisionNecessityChallenge: SM + DecisionRequiredDiscoveryStatement Fact + UC Exhaustion Fact + DecisionNecessityCandidate Fact
DiscoveryDecisionRequiredRevision: SM + prior DecisionRequired Fact + prior DN Candidate Fact + prior DN Challenge Admission
RealizationScopeInitial: SM + AcceptedUC + CandidateRevision + complete CandidateView
RealizationScopeRevision: same + prior RS Admission + prior challenge Admission
RealizationScopeChallenge: challenged RS Admission
RepairRealizationInitial: SM + AcceptedUC + AcceptedRS + CandidateRevision + scoped CandidateView
RepairRealizationRevision: same + prior RR Admission + prior challenge Admission
RepairRealizationChallenge: challenged RR Admission
```

M6 recomputes QLEK. M5 never hashes packet bytes as K.

## 18. Fact and qualification discipline

M5 proposes exact descriptors only. M6 owns identities and reducer truth. Use
exactly seven published qualification contracts and thirteen predicates; add no
qualification or predicate and persist no Fact-status table.

Use M6 progression-view Fact for TargetedDiscoveryStatement. Propose exact C4
Fact descriptors for DecisionRequiredDiscoveryStatement,
RefutationExhaustionWithoutQualifiedRefutation, UniqueCorrectionExhaustion and
DecisionNecessityCandidate. For positive qualifications, propose exact
QualificationKeyDescriptor and ask M6 reducer.

## 19. Operator no-continuation mapping

Use exact common cause
`semantic-progression-no-automatic-continuation` with one closed reason:

```text
materiality-closure-unresolved
no-normative-impact-closure-unresolved
decision-necessity-closure-unresolved
unique-correction-exhausted-without-decision-path
realization-scope-closure-unresolved
repair-realization-closure-unresolved
surviving-material-already-realized
authority-conflict-or-uncertain-unresolved
```

All have `resolutionContracts = []`. They establish no semantic truth,
Decision Required or resampling permission. M8-B creates OperationalBlocker/OAR.

## 20. Exact M6 choreography exposure

For every M5-C semantic step, mechanically expose all of:

```text
exact M6 operation to execute
exact M6 request
exact predecessor closure
exact expected M6 result type
```

M5-C remains the sole owner of which semantic question is next, which
Fact/value/qualification is required, which finding and Discovery statement are
targeted, which challenge/revision is required, whether progression is
exhausted and whether a DecisionRequest is justified. M1 owns none of those
decisions.

When a question becomes fully derivable, expose all of:

```text
exact LogicalQuestionDescriptor artifact
exact ProtocolV8MechanicalClosureInputV1
exact ResolutionContextV1
exact source finding-resolution ObligationRef
exact adjudicating campaign
exact supporting reviewer candidate selected by M5 rules
```

M1 must never reconstruct, normalize, substitute or infer those values. M5-C
validates every supplied M6 result against the exact operation/request it
emitted and the exact predecessor closure. An unexpected operation, request,
result type, result binding or transcript position is
`ASSURANCE-SEMANTIC-CLOSURE-INTEGRITY-FAILURE`.

M1 must sequence only the resulting exact choreography:

```text
M5 derives exact next proposal
→ M6 validates/projects
→ M5 consumes validated result
→ M6 validates exact question
→ M2 resolves K before dispatch
→ reuse OR AdmissionAuthority
→ if execution: M6 prompt/packet, M5 WorkItem, M2 admission,
  M4 prepare, fresh currentness, M2 Arm, M4 execute
→ M6 Stage A
→ protocol-invalid admission then M5-A retry/stop
→ protocol-valid: M5-A package, M6 Stage B, M2 validation, M2 T4
→ fresh snapshot/read
→ continue M5 progression
```

M1 makes no semantic branch choice.

## 21. Replay and failures

Use deterministic identities and exact artifact bytes. Same authoritative input
replays to no duplicate; same identity/incompatible payload fails closed.

Use exact common failure family, including
`ASSURANCE-SEMANTIC-CLOSURE-INTEGRITY-FAILURE` and
`ASSURANCE-PATCH-CONSTRUCTION-INTEGRITY-FAILURE`. Failures are implementation
or integrity outcomes, never semantic/operator/Decision outcomes. Normal
no-continuation uses exact cause material.

## 22. Invariants

```text
M5C-01 Exactly one canonical finding target progresses at a time.
M5C-02 Earliest Discovery statement controls progression.
M5C-03 Failed UniqueCorrection is not Decision Required.
M5C-04 DecisionRequest requires QualifiedDecisionNecessity.
M5C-05 NoNormativeImpact requires positive challenge qualification.
M5C-06 Failed NNI does not prove normative impact.
M5C-07 UniqueCorrection revision is bounded to one.
M5C-08 DecisionRequired revision is bounded to one.
M5C-09 RealizationScope and RepairRealization are exact-candidate-bound.
M5C-10 Candidate advance never retargets old scope or patch.
M5C-11 At most one candidate-bound repair realization is enabled.
M5C-12 AcceptedRR with empty operations creates no RepairIntent.
M5C-13 RepairIntent requires AcceptedRR with non-empty operations.
M5C-14 Patch before-state comes only from exact CandidateView.
M5C-15 Patch after-state comes only from qualified RepairRealization.
M5C-16 Repair never makes a finding non-material or refuted.
M5C-17 Operator inability never becomes SemanticBlocker.
M5C-18 Reused semantic truth transfers no receipt ownership.
M5C-19 M5-C computes no semantic ID and invokes no Python.
M5C-20 P8 remains inactive until C15.
```

## 23. Future tests

Require future tests for failed NNI operator routing, accepted UC avoiding
DecisionRequest, qualified DecisionNecessity-only DecisionRequest, objection
revision requiring fresh UC exhaustion, identical candidate bytes/distinct IDs
requiring fresh RS/RR, fully already-realized RR yielding no RepairIntent,
canonical multi-finding order, exact patch bytes/scope, imported adjudicating
campaign, reused Admission without receipt copy, supporting-role absence,
bounded revisions and lifecycle regressions.

## 24. Forbidden behavior

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

Also forbid arbitrary semantic JSON number round-trip, Unicode normalization,
float conversion, integer rounding and semantic-payload key reordering.

## 25. Construction classifications

The exact progression is derived from accepted authority with no normative
impact. The one-finding-at-a-time order (`ReviewCampaignId`, then `FindingId`
unsigned ordering), helper boundaries and internal projection schemas are
`no-normative-impact` architecture/implementation mechanisms. No ADR is
required.
