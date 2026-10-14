---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-14"
step_id: 2
id: NIB-M-GATE-A-ASSURANCE-LEDGER-REPOSITORY-PROJECTION-READINESS
version: "1.0.0"
scope: gate-a-campaign-runner/assurance-ledger/repository-projection-readiness
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Assurance Ledger — Repository Projection and Readiness

## 1. Status and authority

Implement M5-D from NIB-S 12.0.0, M0 1.3.0, M2 3.0.4/8.0.0/7.0.0,
M5-A 3.0.0, M5-B 1.0.0, M5-C 1.0.0, M6 1.1.0, accepted ADR-055/056 and
closed P8 C1-C7 authority.

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

## 3. Exact P8 paths

Use exactly:

```text
runner-produced ReviewCampaign:
formal/reviews/<ReviewCampaignId>.json

packet:
formal/reviews/packets/<sha256>.json

receipt:
formal/reviews/executions/<WorkItemId>.json

raw receipt attempt:
formal/reviews/raw/<WorkItemId>-ATTEMPT-<attemptOrdinal>.json

qualified non-challenge semantic output:
formal/reviews/adjudications/<rawOutput.sha256>.json

qualified challenge semantic output:
formal/reviews/challenges/<rawOutput.sha256>.json

semantic-question binding:
formal/reviews/semantic-question-bindings/<binding.sha256>.json

origin witness:
formal/reviews/semantic-admission-origin-witnesses/<witness.sha256>.json

finding-adjudication supplement:
formal/reviews/supplements/<supplement.sha256>.json
```

No path enters QLEK or any semantic ID. P8 does not use
`adjudication-packets/` or `challenge-packets/` as semantic execution packet
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

For locally produced P8 Admission project exact packet, receipt, raw attempts,
binding, origin witness and qualifying output under `adjudications/` or
`challenges/`. Preserve every receipt/witness binding exactly.

Project each completed finding supplement under its exact SHA path. A supplement
contains effective adjudication only and no receipt provenance.

## 6. Projection entry algorithm

For each target:

```text
absent
→ include exact regular-file projection entry

exact regular file with byte-identical content
→ omit as already materialized

same path with different bytes
→ ASSURANCE-PROJECTION-INTEGRITY-FAILURE

symlink/directory/gitlink/non-regular
→ ASSURANCE-PROJECTION-INTEGRITY-FAILURE
```

Never overwrite, rename, delete, merge or follow a symlink. Sort entries by
repository-path unsigned UTF-8 order. Require at least one absent target; a
complete no-op creates no projection.

Construct the exact NIB-S projection artifact/ref and ID. M5-D reads candidate
materialization only through exact accepted immutable M7/M6 boundaries and does
not mutate it.

## 7. Repair and assurance coexistence

If one current candidate has one qualified RepairIntent and one unconsumed
assurance projection, expose both. M7 later applies exact `repair + assurance`
through existing combined construction. Require path sets disjoint under M7-A.
A collision is integrity/construction failure; M5 never chooses preference.

C9-F must synchronize M7-A with NIB-S 12.0.0 and this exact allowlist before
GREEN. Do not modify M7 during C9-E.

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

## 16. M1 integration dependency

Future M1 must route reuse-first semantics, M6 mechanical requests, M2
AdmissionAuthority, Stage A/M5-A/Stage B, fresh currentness before Arm,
CandidateView requests, and complete-delta composition. M1 chooses no semantic
branch. Do not modify M1 in C9-E.

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
```

## 19. Future tests

Create no NIB-T. Require tests for exact paths, path collision, byte-identical
idempotence, symlink rejection, reused Admission projecting no predecessor
receipt/witness, unconsumed projection blocking readiness, surviving-material
finding blocking readiness, complete current campaign set, exact stale
contributors, repair/projection disjointness, one-to-one blocker finalization,
A/B/C/D order, P6 regression, P7 inactive and P8 inactive.

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
accepted authority and adds no product meaning. No ADR is required.
