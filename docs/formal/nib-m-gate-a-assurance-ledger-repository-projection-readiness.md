---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-14"
step_id: 2
id: NIB-M-GATE-A-ASSURANCE-LEDGER-REPOSITORY-PROJECTION-READINESS
version: "1.1.0"
scope: gate-a-campaign-runner/assurance-ledger/repository-projection-readiness
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Assurance Ledger — Repository Projection and Readiness

## 1. Status and authority

Implement M5-D from NIB-S 13.0.1, M0 1.5.0, M2 3.0.4/9.1.0/8.1.0,
M5-A 3.1.0, M5-B 1.1.0, M5-C 1.1.0, M6 1.2.0, accepted ADR-055/056 and
closed P8 C1-C7 authority.

Version `1.1.0` additively exposes one deterministic, pure, replayable M1-facing
broker over M5-B/C and exact M6 semantic helper operations. It transfers no
semantic branch, provider execution, state authority, retry, receipt ownership
or protocol activation to M1.

Version `1.0.1` synchronizes the construction representation with NIB-S
`12.0.1` and M7-A `2.1.0`. It changes no semantic progression, readiness,
identity, evidence, path, or module-ownership rule.

P6 remains current. P7 remains permanently inactive. P8 remains inactive until
C15. This brief adds no semantics, activation, dependency or repository
mutation authority.

## 2. Responsibility boundary

Own exactly:

```text
repository-facing assurance artifact selection
exact repository projection path selection
P6/P8 ReviewCampaign serialization where construction is complete
P8 local semantic evidence projection
P8 supplement projection
AssuranceRepositoryProjectionRef construction
projection duplicate/collision handling
CandidateReviewReadinessRef construction
current/contributing campaign-set construction
M5-A/B/C/D mechanical contribution composition
finalize_complete_delta mechanical blocker merge
```

Do not mutate repository, interpret Git, invoke Python, apply RepairIntent,
choose semantic progression or declare Gate A ready. M7 applies projection
mechanically; M6 qualifies mechanically.

## 3. Exact P8 paths and source media

Use exactly:

```text
runner-produced ReviewCampaign
→ formal/reviews/<ReviewCampaignId>.json
→ application/json

packet
→ formal/reviews/packets/<sha256>.json
→ application/json

receipt
→ formal/reviews/executions/<WorkItemId>.json
→ application/json

raw receipt attempt
→ formal/reviews/raw/<WorkItemId>-ATTEMPT-<attemptOrdinal>.json
→ text/plain; charset=utf-8

qualified non-challenge semantic output
→ formal/reviews/adjudications/<rawOutput.sha256>.json
→ text/plain; charset=utf-8

qualified challenge semantic output
→ formal/reviews/challenges/<rawOutput.sha256>.json
→ text/plain; charset=utf-8

semantic-question binding
→ formal/reviews/semantic-question-bindings/<binding.sha256>.json
→ application/json

origin witness
→ formal/reviews/semantic-admission-origin-witnesses/<witness.sha256>.json
→ application/json

finding-adjudication supplement
→ formal/reviews/supplements/<supplement.sha256>.json
→ application/json
```

No path changes from C9-E. No path enters QLEK or any semantic ID. P8 does not
use `adjudication-packets/` or `challenge-packets/` as semantic execution packet
namespaces.

## 4. P8 ReviewCampaign projection

Serialize review-evidence-v6 as initial campaign only, from exact
runner-produced history. Include review identity/class, production repository
commit, subject, P8 protocol, initial-reviewer executions only, normalized
substantive findings only, supersedes IDs, `started_at` and `completed_at`.

Include no supporting executions, re-adjudications, finding materiality/status
or disposition.

Order initial executions by reviewer-acquisition selection order and findings by
execution order then raw `findings[]` order. Set `started_at` to earliest exact
initial receipt-attempt start and `completed_at` to latest final qualifying
initial-attempt end. Invent no timestamp.

## 5. Local semantic evidence projection

Project only provenance produced by the current run. For a reused Admission,
project no predecessor receipt, witness, packet or root ownership.

Every `AssuranceRepositoryProjectionEntryV1.content` is the exact original
immutable CAS-backed source `ArtifactRef`, always with `repositoryPath == null`.
Never use an M5-A Stage-B repository-path alias as projection-entry content;
those aliases remain validation/provenance locators only.

For structured artifacts use the original sealed source with exactly:

```text
root ReviewCampaign record
packet
receipt
supplement
semantic-question binding
origin witness
historical P6 challenge packet when applicable

mediaType == application/json
repositoryPath == null
```

For exact raw cognitive textual artifacts use the original M4 captured source
with exactly:

```text
raw attempt output
qualified non-challenge semantic output
qualified challenge semantic output

mediaType == text/plain; charset=utf-8
repositoryPath == null
```

Project locally produced P8 Admission artifacts under the exact Section 3 paths
and preserve every receipt/witness binding exactly. Do not reseal raw output as
`application/json`, change its media type, parse and rewrite it, create a JSON
wrapper, or change its SHA-256 or byte length. The projection descriptor carries
placement separately in `entry.repositoryPath`.

Project each completed finding supplement under its exact SHA path. A supplement
contains effective adjudication only and no receipt provenance.

## 6. Projection entry algorithm

For each target, pair the exact Section 3 repository path with the exact original
Section 5 source `ArtifactRef`. Require before candidate comparison:

```text
source content exists and is intact
source content.repositoryPath == null
source content.mediaType obeys the exact NIB-S 12.0.1 path/media-type mapping
```

Then apply exactly:

```text
absent
→ include exact regular-file projection entry whose content is that unchanged
  source ArtifactRef

exact regular file with byte-identical content
→ omit as already materialized

same path with different bytes
→ ASSURANCE-PROJECTION-INTEGRITY-FAILURE

symlink/directory/gitlink/non-regular
→ ASSURANCE-PROJECTION-INTEGRITY-FAILURE
```

Never overwrite, rename, delete, merge, follow a symlink, or construct a
repository-path alias as entry content. Sort entries by exact repository-path
unsigned UTF-8 order without Unicode normalization. Require at least one absent
target; a complete no-op creates no projection.

Construct the exact NIB-S projection artifact/ref and ID. The projection
descriptor itself remains runner-owned canonical JSON with
`mediaType == application/json` and `repositoryPath == null`. M5-D reads
candidate materialization only through exact accepted immutable M7/M6
boundaries and does not mutate it.

## 7. Repair and assurance coexistence

If one current candidate has one qualified RepairIntent and one unconsumed
assurance projection, expose both. M7 later applies exact `repair + assurance`
through existing combined construction. Require path sets disjoint under M7-A.
A collision is integrity/construction failure; M5 never chooses preference.

C9-F synchronizes M7-A 2.1.0 with NIB-S 12.0.1 and this exact projection
contract. M5 chooses assurance content and intended repository placement; M7-A
applies that projection mechanically, creates candidate-only byte carriers where
required, and interprets no hostile-review or semantic meaning.

## 8. Readiness basis

Define exactly:

```ts
interface GateAReviewReadinessBasisV1 {
  readonly schema:
    "gate-a-review-readiness-basis.v1";
  readonly candidateId: CandidateRevisionId;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly currentReviewCampaignIds:
    readonly ReviewCampaignId[];
  readonly contributingReviewCampaignIds:
    readonly ReviewCampaignId[];
  readonly basisArtifacts: readonly ArtifactRef[];
}
```

Seal canonical runner JSON and derive:

```text
deriveId(
  "assurance-ledger-review-readiness.v1",
  candidateId,
  readinessBasis.sha256
)
```

Set `CandidateReviewReadinessRef.basisArtifacts` to the readiness-basis artifact
followed by exact source artifacts with first-occurrence dedupe.

## 9. Current campaign set

Set `currentReviewCampaignIds` exactly to
`evaluationContext.currentCampaigns[*].reviewCampaignId`, preserving M3 order.
Apply no candidate provenance, runner/imported or first-wins filter.

## 10. Contributing campaign set

Construct exactly:

```text
all currentReviewCampaignIds in currentCampaign order
then each staleProtocolCampaignId in exact M3 stale order
iff that campaign contributes at least one exact current-P supplement to basis
```

Keep duplicate-free. Do not include a stale campaign merely because it exists,
or omit one whose current-P supplement contributes.

## 11. P8 readiness preconditions

Return non-null readiness only if all hold:

```text
candidate is exact current candidate
S/P equal evaluationContext
no outstanding OperationalBlocker
no outstanding SemanticBlocker
no applicable RepairIntent awaiting materialization
no unconsumed AssuranceRepositoryProjection
every current runner-produced initial campaign obligation closed
every selected initial-reviewer WorkItem has complete receipt evidence
reviewer-acquisition target satisfied
every applicable current/stale finding has complete P8 effective adjudication
every applicable finding-resolution obligation terminal satisfied/superseded
no applicable surviving-material finding with outstanding finding obligation
no M5 cognitive WorkItem can alter qualification basis
no unresolved relevant Execution can alter basis
no pending P8 semantic validation/reconciliation can alter basis
every required repository-facing artifact already exists in current candidate
no unconsumed projection exists
```

M5-D establishes only closure sufficient to submit exact candidate/basis to M6.
It never reproduces Python Gate A acceptance.

## 12. P6 readiness

P6 remains current. Existing mechanically valid complete repository evidence may
contribute under M3/M6. A runner-produced P6 campaign with zero findings may be
projected through review-evidence-v5. A P6 campaign with unresolved new findings
cannot reach readiness because M5-B emits
`p6-post-review-automation-unavailable`.

Do not reinterpret P6 with P8 supplements or activate P7.

## 13. Mechanical composition

Require every submodule contribution to bind the same exact
`snapshot.stateRevision`. Compose arrays in exactly:

```text
M5-A
M5-B
M5-C
M5-D
```

Preserve each internal deterministic order. Duplicate logical identity across
siblings is `ASSURANCE-FINALIZATION-INTEGRITY-FAILURE`, even for byte-equal
payloads.

No same-delta semantic phase advancement: any A/B/C/D product becomes later
semantic-phase input only after M2 admission and fresh snapshot reload.

Only M5-D may establish `assuranceRepositoryProjectionToEstablish` and
`candidateReviewReadiness`; A/B/C return neither. Permit at most one of each,
and enforce existing rule `unconsumed projection → readiness null`.

## 14. Operational blocker request composition

Concatenate requests in A/B/C/D order and preserve each canonical traversal.
M1 transports unchanged to M8-B. M5 assigns no Operational BlockerId.

## 15. Complete-delta finalization

Copy all non-blocker preparation fields byte-for-byte/logically unchanged. Set:

```text
blockersToAdd = [
  ...semanticBlockersToAdd,
  ...materializedOperationalBlockers[*].blocker
]
```

Preserve request order. Require one-to-one exact request/materialization
binding; mismatch is `ASSURANCE-FINALIZATION-INTEGRITY-FAILURE`.

## 16. Deterministic M5-to-M6 broker facade

M5-D exposes one pure replayable planning transcript over M5-B/C. The transcript
is ephemeral orchestration material, never authoritative state and never
persisted in M2.

The closed mechanical operation set is exactly:

```text
project_protocol_v8_finding_adjudication_basis
validate_protocol_v8_semantic_value_proposal
validate_protocol_v8_semantic_fact_descriptor
reduce_protocol_v8_qualification_descriptor
project_protocol_v8_semantic_progression_view
validate_protocol_v8_candidate_view
validate_protocol_v8_semantic_question
```

Add no semantic operation and no provider execution to this broker.

Define `ProtocolV8ProgressionMechanicalExchangeV1` as a strict closed
discriminated union with exactly one branch per operation above. Every branch
contains:

```text
operation = exact literal operation kind
request = exact operation-specific M6 request
result = exact operation-specific M6 result
```

No branch permits an unknown operation, alternate request type, alternate result
type or extra field. An ordered ephemeral transcript is a readonly array of
those exact exchanges.

Expose exactly:

```text
plan_protocol_v8_progression(...)
```

Inputs are exactly:

```text
exact AssuranceDerivationRequest
exact ordered ephemeral transcript of prior request/result exchanges for this
same fresh authoritative snapshot
```

On every call, replay progression from the exact request snapshot. Validate that
the supplied transcript is exactly a prefix of the deterministic M5-selected
mechanical exchange sequence, including operation, request, predecessor closure,
result type and exact result binding. Any mismatch is
`ASSURANCE-SEMANTIC-CLOSURE-INTEGRITY-FAILURE`.

Return exactly one closed branch:

```text
mechanical-request
resolve-semantic-question
complete-preparation
```

For `mechanical-request`, return only:

```text
exact closed M6 operation kind
exact M6 request
```

M1 performs that exact call and appends the exact request/result exchange to its
ephemeral transcript.

Return `resolve-semantic-question` only after exact M6 semantic-question
validation is already present in the validated transcript. Return exactly:

```text
exact ValidatedSemanticQuestionRefV1
exact ProtocolV8MechanicalClosureInputV1
exact ResolutionContextV1
exact source finding-resolution ObligationRef
exact adjudicating campaign
exact supporting reviewer candidate
```

M1 invokes M2 T1 for that exact QLEK and neither inspects nor reconstructs the
semantic value.

For `complete-preparation`, return the exact complete
`AssuranceLedgerPreparation`. M1 performs only:

```text
M8-B operational blocker materialization
→ M5 finalize_complete_delta
→ M2 AdmitAssuranceLedgerDeltaV1
```

No M5 semantic state is stored between calls. Crash/restart restarts planning
from a fresh authoritative snapshot and an empty ephemeral transcript and must
reproduce the same requests.

### 16.1 Reused Admission path

When M2 T1 returns `reuse`:

```text
M1 supplies exact Admission back to M5 broker
M5 requests exact M6 progression-view projection
M1 calls M6
M5 consumes only the exact M6 projection
M5 continues semantic planning
```

M1 never inspects semantic value content.

### 16.2 Semantic execution path

When M2 T1 returns `acquired` and no existing resumable unarmed trajectory
exists, M1 calls `project_protocol_v8_semantic_execution_inputs` with the exact
validated question, exact P8 P and exact M5 closure.

Expose exactly:

```text
construct_protocol_v8_semantic_work(...)
```

It constructs only the M5-owned P8 WorkItem already specified by M5-C:

```text
workItemId =
deriveId(
  "assurance-ledger-semantic-work-item.v1",
  runId,
  qlek
)

source obligation = exact finding-resolution obligation
executor = cognitive-execution
context = exact M5 ResolutionContextV1
profile = exact M5-selected supporting profile
role/prompt/packet = exact M6-projected semantic execution inputs
```

It returns an M5 preparation that adds that exact WorkItem. M1 must admit the
WorkItem through the normal M5 delta, reload a fresh authoritative snapshot, and
only then perform M2 T2. Creating WorkItem and Execution through one shortcut is
forbidden.

If M5 delta admission fails, M1 releases the exact live
`AdmissionAuthority` before abandoning that T1 attempt.

### 16.3 Construction classification

```text
statement:
M5-B/C own the next semantic question but existing briefs only narratively said
to expose required M6 work, leaving future M1 without an exact mechanical
broker surface

semantic disposition:
authority-conflict-or-uncertain at construction representation level

resolution:
replayable M5-D planning transcript with exact closed M6 operation transport

affected layer:
architecture-or-implementation

normative impact:
none
```

No ADR is required.

## 17. Failures and replay

Use exact common failures, including:

```text
ASSURANCE-PROJECTION-INTEGRITY-FAILURE
ASSURANCE-READINESS-INTEGRITY-FAILURE
ASSURANCE-FINALIZATION-INTEGRITY-FAILURE
```

These are implementation/integrity failures, not Decision Required, Operator
Action Required, protocol-invalid or NotEstablished. Same inputs reproduce exact
bytes/identity; admitted exact products replay to no-op; conflicts fail closed.

## 18. Invariants

```text
M5D-01 M5 never mutates repository directly.
M5D-02 Projection entries are additive regular files only.
M5D-03 Same path/different bytes fails closed.
M5D-04 Projection paths are not semantic identity.
M5D-05 Reused Admission provenance is not copied into consuming root.
M5D-06 P8 ReviewCampaign contains initial review only.
M5D-07 P8 supplement contains effective adjudication only.
M5D-08 Binding/witness projection is audit provenance.
M5D-09 All required projection bytes exist in current candidate before readiness.
M5D-10 Unconsumed projection forbids readiness.
M5D-11 RepairIntent awaiting materialization forbids readiness.
M5D-12 Outstanding semantic/operational blocker forbids readiness.
M5D-13 Outstanding applicable finding obligation forbids readiness.
M5D-14 Current campaign set is complete.
M5D-15 Stale contributing campaign set is exact.
M5D-16 Readiness does not duplicate Python Gate A logic.
M5D-17 M6 alone establishes mechanical Gate A qualification.
M5D-18 Composition order is exactly A/B/C/D.
M5D-19 Sibling duplicate identity fails even when bytes match.
M5D-20 P8 remains inactive until C15.
M5D-21 Projection entry content is always the original immutable CAS-backed
       source ArtifactRef.
M5D-22 Projection entry content has repositoryPath null; entry.repositoryPath
       alone owns placement.
M5D-23 Structured projection sources retain application/json.
M5D-24 Raw cognitive projection sources retain text/plain; charset=utf-8.
M5D-25 Repository projection never changes source bytes, SHA or byteLength.
M5D-26 Stage-B repository-path aliases remain validation/provenance locators and
       never become projection-entry content authority.
M5D-27 M7 candidate-byte carriers never replace M5 projection content identity.
```

## 19. Future tests

Create no NIB-T. Require tests for exact paths, every path-qualified media type,
raw malformed bytes preserved exactly, `content.repositoryPath != null`
rejection, Stage-B alias rejection as projection authority, path collision,
byte-identical idempotence, symlink rejection, reused Admission projecting no
predecessor receipt/witness, unconsumed projection blocking readiness,
surviving-material finding blocking readiness, complete current campaign set,
exact stale contributors, repair/projection disjointness, one-to-one blocker
finalization, A/B/C/D order, P6 regression, P7 inactive and P8 inactive.

## 20. Forbidden behavior

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

Also forbid direct Git, overwrite/rename/delete/merge, symlink following,
path-as-semantic-identity, Python Gate A reimplementation, RepairIntent
application, arbitrary semantic JSON number round-trip, Unicode normalization,
float conversion, integer rounding and semantic-payload key reordering.

## 21. Construction classification

P8 binding/witness/supplement paths were intentionally construction-owned by C6;
selecting them here is a `no-normative-impact`
`architecture-or-implementation` mechanism. Composition/readiness follows
accepted authority and adds no product meaning.

The C9-F representation discovery is recorded as:

```text
statement:
exact raw cognitive completion artifacts are immutable text/plain CAS sources,
while repository placement uses .json locators

semantic disposition:
derived-from-existing-authority

affected layer:
architecture-or-implementation

mechanism:
retain the exact source ArtifactRef and carry placement only in
AssuranceRepositoryProjectionEntryV1.repositoryPath

normative impact:
none
```

No ADR is required.
