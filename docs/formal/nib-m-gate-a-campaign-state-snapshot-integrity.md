---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-09-20"
step_id: 2
id: NIB-M-GATE-A-CAMPAIGN-STATE-SNAPSHOT-INTEGRITY
version: "1.0.4"
scope: gate-a-campaign-runner/campaign-state/snapshot-integrity
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Campaign State — Snapshot Reconstruction and Integrity

## 1. Status, authority, and purpose

This document is one of three active Module Briefs that together close M2
`campaign-state` for the Gate A hostile-review campaign runner.

It consumes `NIB-S-GATE-A-CAMPAIGN-RUNNER` version `6.0.5`.

It is implementation-construction authority only. It does not define TURNLOCK
product semantics, canonical formal semantics, hostile-review protocol
semantics, formal-assurance claims, review evidence, or verification evidence.

This brief defines how M2 reconstructs one exact `GateARunSnapshot` from
append-only Authoritative History and how it determines whether retained state
is trustworthy.

The snapshot is a deterministic read-side projection.

It is not separately persisted authority.

A restart must produce the same snapshot from the same authoritative revision
without scanning mutable workspaces.

Persistence and ownership mechanics are defined by
`NIB-M-GATE-A-CAMPAIGN-STATE-PERSISTENCE-OWNERSHIP`.

Mutation admission and execution lifecycle are defined by
`NIB-M-GATE-A-CAMPAIGN-STATE-MUTATION-EXECUTION`.

## 2. Public input/output

```ts
interface LoadGateARunSnapshotRequest {
  readonly runId: GateARunId;
}
```

Successful load returns the exact NIB-S:

```ts
GateARunSnapshot
```

There is no normal union branch for unknown/corrupt state.

These reject/fail the invocation:

```text
unknown GateARunId
unsupported M2 schema
SQLite corruption
authoritative history contradiction
missing committed artifact
invalid committed artifact
broken revision chain
broken referential closure
```

They must never fabricate:

```text
GATE-A-READY
DECISION-REQUIRED
OPERATOR-ACTION-REQUIRED
```

## 3. Read transaction

Every snapshot is reconstructed inside one SQLite read transaction.

```text
BEGIN

establish exact run exists

R = exact maximum StateRevision for run

load every authoritative fact for run
whose introduced revision <= R

validate structural and artifact integrity

derive snapshot projections

validate snapshot invariants

END/COMMIT read transaction
```

No query outside that transaction may contribute authoritative snapshot data.

## 4. Integrity levels

M2 validates five layers.

### 4.1 Storage/schema integrity

Require:

```text
recognized schema version
required relations/triggers/indexes exist
foreign-key enforcement active
SQLite quick_check == ok
no foreign-key violation
```

An open database that silently lacks an append-only trigger is not accepted as
valid M2 v1 storage.

### 4.2 Revision integrity

For one run:

```text
revision 0 exists exactly once
revision numbers are contiguous
no duplicate revision
revision N.previous == N-1
every N>0 has one intact mutation artifact
mutation artifact runId == run
mutation artifact baseStateRevision == N-1
journal session/generation matches the commit authority recorded for N
```

No missing revision may be skipped.

### 4.3 Referential integrity

Every authoritative reference must resolve to an admitted or valid external
identity required by its owning contract.

Examples:

```text
candidate parent exists
repair intent exists where named
WorkItem obligations exist
Execution WorkItem exists
retry authorization prior Execution exists
finding campaign/execution exists
blocker obligation exists
publication confirmation intent exists
```

### 4.4 Artifact integrity

Every `ArtifactRef` reachable from authoritative history must have:

```text
valid runtime shape
registered artifactId/SHA binding
CAS bytes present
exact byteLength
exact SHA-256
```

Repository paths and mutable workspaces are not used to repair missing CAS bytes
during snapshot reconstruction.

### 4.5 Domain/global integrity

The complete retained run must satisfy the domain invariants in §11 below.

If a contradiction is already present in committed history, this is
`INTEGRITY_FAILURE`, not an invalid new proposal.

## 5. Snapshot field projection

### 5.1 `run`

Derived from:

```text
runs
+
optional exact preflight_establishment
```

Before preflight:

```ts
{
  runId,
  initialRepositoryAuthority: null,
  publicationTarget: null,
}
```

After successful preflight both become non-null together and never change.

### 5.2 `stateRevision`

Canonical decimal string for exact maximum revision `R`.

### 5.3 `currentCandidate`

If no candidate exists:

```text
null
```

Otherwise:

```text
candidate with maximum ordinal
```

Integrity validation must independently prove the candidate lineage is a single
linear chain.

`MAX(ordinal)` is not used to hide branching or duplicate candidates.

### 5.4 `reviewCampaigns`

Every registered `ReviewCampaignRef`, including:

```text
runner-created campaigns
repository-selected/imported campaigns observed through exact M3 context
```

Historical campaigns remain present.

Ordering:

```text
introducedRevision ascending
then reviewCampaignId ascending
```

Currentness is not projected by M2.

### 5.5 `obligations`

Every admitted `ObligationRef`.

Ordering:

```text
introducedRevision ascending
then obligationId ascending
```

### 5.6 `obligationDispositions`

Every admitted terminal disposition.

Ordering:

```text
introducedRevision ascending
then obligationId ascending
```

Outstanding obligations are internal projection:

```text
all obligations
minus obligations having a direct disposition
```

Supersession is not recursively treated as outstandingness.

### 5.7 `workItems`

Every admitted `WorkItemRef`.

Historical/inert WorkItems remain visible.

Ordering:

```text
introducedRevision ascending
then workItemId ascending
```

### 5.8 `executions`

Every admitted `ExecutionRef`.

Ordering:

```text
workItemId ascending
then attemptOrdinal ascending
then executionId ascending
```

Attempt ordinal uniqueness is verified before projection.

### 5.9 `executionRetryAuthorizations`

Every historical admitted authorization, whether currently usable, consumed, or
stale.

Ordering:

```text
introducedRevision ascending
then retryAuthorizationId ascending
```

Availability is not represented as mutable state.

Internally:

```text
usable(R) =
    R exists
    AND no Execution creation basis consumed R
    AND R.priorExecution is the current WorkItem tail
    AND at least one source obligation remains outstanding
    AND run progression still permits replacement
```

### 5.10 `capturedExecutionResults`

Every direct or recovered authoritative captured result.

One exact result is returned once in the array even if later facts reference it.

Ordering:

```text
Execution attempt order
```

### 5.11 `technicalExecutionFailures`

Every direct or recovered authoritative known technical failure.

Ordering:

```text
Execution attempt order
```

## 6. Unresolved-execution reconstruction

This is a critical M2 v1 algorithm.

For every Execution `E`:

```text
if no Arm fact:
    E is not unresolved

else if direct terminal outcome exists:
    E is not unresolved

else if terminal recovery resolution exists:
    E is not unresolved

else:
    E is unresolved
```

This rule is independent of whether the executor ever returned an explicit
`uncertain` capture.

### 6.1 Base descriptor from Arm

Given Arm fact `A`:

```ts
{
  execution: exact E,
  workItem: exact W,
  dispatchState: "POSSIBLY-DISPATCHED",
  dispatchIntent: A.mutationArtifact,
  dispatchEvidence: A.dispatchEvidence,
  terminalOutcome: null,
  recoveryCapability: A.recoveryCapability,
}
```

### 6.2 Uncertainty enrichment

If one executor uncertainty enrichment exists:

```text
require same Execution
require same WorkItem
require same dispatchIntent
```

Projection becomes:

```text
dispatchState =
    OBSERVED-RESULT
    when enrichment.terminalOutcome != null
    otherwise POSSIBLY-DISPATCHED

dispatchEvidence =
    Arm evidence
    followed by enrichment-only evidence
    with exact duplicate ArtifactRefs removed while preserving first occurrence

terminalOutcome =
    enrichment.terminalOutcome

recoveryCapability =
    enrichment.recoveryCapability
```

The enrichment may not remove Arm evidence.

### 6.3 Pending reconciliation

A `ReconciliationPendingRef` does not terminalize the Execution.

Its evidence is retained in history.

The unresolved descriptor remains projected.

A pending-exhaustion operational blocker does not remove the execution from
`unresolvedExecutions`.

### 6.4 UNRESOLVABLE

`UNRESOLVABLE` is a terminal recovery resolution.

Therefore the execution no longer appears in `unresolvedExecutions`.

Its exact operational blocker remains outstanding until lawfully disposed.

## 7. Assurance-ledger projections

The following snapshot arrays contain every admitted historical value:

```text
evidence
findings
adjudications
reAdjudications
repairIntents
decisionRequests
```

Ordering for each:

```text
introducedRevision ascending
then primary logical ID ascending
```

No currentness filtering occurs here.

M3/M5 own applicability.

## 8. Candidate review readiness

M2 stores:

```text
CandidateReviewReadinessRef objects
+
append-only readiness-designation facts
```

Whenever an admitted M5 delta supplies a non-null
`candidateReviewReadiness`, M2:

```text
registers the object if new
and
appends a designation when it differs from the current designation
```

Re-designating an already-existing readiness object is allowed and creates a new
designation fact.

This supports authority cycles such as:

```text
P1
→ P2
→ exact P1 again
```

without mutating an old readiness object.

Snapshot projection:

```text
if currentCandidate == null:
    candidateReviewReadiness = null

else:
    choose latest readiness designation whose referenced readiness.candidateId
    equals currentCandidate.candidateId

    if none:
        null
```

This field is not M3 currentness authority.

M1 must still compare it to a fresh `GateAEvaluationContext` before use.

## 9. Blockers

Authoritative history retains all blockers.

Snapshot exposes only outstanding blockers:

```text
outstanding(B) =
    blocker exists
    AND no blocker disposition exists
```

Ordering:

```text
introducedRevision ascending
then blockerId ascending
```

Semantic blockers have no same-run disposition.

Therefore:

```text
semanticProgressionTerminal =
    at least one SemanticBlocker exists
```

not merely:

```text
snapshot.blockers currently contains semantic blocker
```

The semantic terminal fact remains true forever for that run.

## 10. Qualification and publication projections

### 10.1 `gateQualification`

Let:

```text
C = currentCandidate
R = candidateReviewReadiness
```

Return `null` if either is null.

Otherwise choose the most recent admitted `GateAQualificationRef` such that:

```text
qualification.candidateId == C.candidateId

qualification.currentReviewCampaignIds
    == R.currentReviewCampaignIds

qualification.contributingReviewCampaignIds
    == R.contributingReviewCampaignIds
```

If more than one incompatible qualification claims the same exact basis:

```text
INTEGRITY_FAILURE
```

This is structural applicability only.

M2 does not assert that `(S,P)` remains externally current.

### 10.2 `publicationIntent`

Return the exact latest intent satisfying:

```text
intent.candidateId == currentCandidate.candidateId
intent.qualificationId == projected gateQualification.qualificationId
```

Otherwise `null`.

### 10.3 `publicationConfirmation`

Publication confirmations are projected only from admitted
`PublicationObservationQualificationResult.kind = "confirmed"` facts.

For every such admission, require the retained exact request/result basis.

The request's:

```text
intent
candidate
executionResult
```

must satisfy the M2-B publication-observation qualification admission rules.

In particular:

```text
executionResult is already-authoritative captured execution material

executionResult.execution is the exact armed repository-control publication
Execution for the request intent

request.intent == projected applicable PublicationIntent

request.candidate == currentCandidate
```

The confirmed result must satisfy:

```text
confirmation.publicationIntentId
    == request.intent.publicationIntentId

confirmation.candidateId
    == request.candidate.candidateId

confirmation.transition
    == request.intent.transition

publishedView.publicationConfirmationId
    == confirmation.publicationConfirmationId

publishedView.candidateId
    == request.candidate.candidateId

publishedView.target
    == request.intent.transition.target

publishedView.authority
    == request.intent.transition.successor
```

Return the exact confirmation from the structurally applicable confirmed
admission.

A `result.kind = "blocked"` admission never projects a publication
confirmation.

A bare retained `PublicationConfirmationRef` without its exact confirmed
publication-observation qualification basis is `INTEGRITY_FAILURE`.

Multiple incompatible confirmed admissions for one exact PublicationIntent are
`INTEGRITY_FAILURE`.

### 10.4 `gateAReady`

```text
true iff one terminal Gate A ready fact exists
```

At most one may exist.

If `gateAReady == true`, its qualification/publication/post-publication basis
must still pass retained structural integrity validation.

## 11. Required global integrity invariants

M2 snapshot/integrity must verify all of these before returning any snapshot and
before mutation/execution M2 commits any new revision:

```text
I01  Exactly one root preflight obligation exists for each run.

I02  Preflight establishment is absent or unique.

I03  Preflight baseline authority and publication target appear together.

I04  Candidate ordinals begin at 0 and are contiguous.

I05  Candidate lineage is exactly one linear chain.

I06  One candidate logical slot cannot contain two payloads.

I07  Obligation has zero or one terminal disposition.

I08  Obligation supersession graph is acyclic.

I09  Every WorkItem has at least one source obligation.

I10  Every WorkItem source obligation belongs to the same run.

I11  Execution attempt ordinals begin at 1 and are contiguous per WorkItem.

I12  One WorkItem has one linear Execution chain.

I13  One Execution has at most one Arm fact.

I14  One Execution has at most one direct terminal outcome.

I15  Captured result and technical failure cannot coexist for the same direct
     outcome.

I16  One Execution has at most one executor uncertainty enrichment.

I17  One Execution has at most one terminal recovery resolution.

I18  Direct terminal outcome and terminal recovery resolution cannot represent
     incompatible outcomes.

I19  Every armed non-terminal Execution appears exactly once in the unresolved
     projection.

I20  Every unarmed Execution appears zero times in the unresolved projection.

I21  One cognitive Execution has at most one M6 attempt classification.

I22  protocol-invalid and qualified cannot coexist for one Execution.

I23  A qualified cognitive Execution has no retry authorization naming it.

I24  One retry authorization is consumed by at most one successor Execution.

I25  One PNE recovery basis is consumed by at most one successor Execution.

I26  Execution count per WorkItem never exceeds five.

I27  Protocol-invalid replacements never exceed one.

I28  Technical-failure replacements never exceed two.

I29  Consecutive PNE replacements never exceed two.

I30  Semantic blocker has no disposition.

I31  Operational blocker has at most one disposition.

I32  Blocker disposition never deletes blocker history.

I33  Gate A ready implies zero outstanding obligations.

I34  Gate A ready implies zero outstanding blockers.

I35  Gate A ready implies semanticProgressionTerminal == false.

I36  Every PublicationConfirmation has exactly one retained
     PublicationObservationQualificationResult.kind = confirmed admission basis;
     its exact request carries an already-authoritative captured result from the
     exact armed repository-control publication Execution for that
     PublicationIntent, and Gate A ready has the exact qualification,
     publication confirmation, and passing bound post-publication validation.

I37  No StateRevision follows the Gate A ready revision.

I38  Every authoritative ArtifactRef resolves to exact immutable CAS bytes.

I39  Every N>0 StateRevision names exactly one valid mutation artifact.

I40  Snapshot reconstruction uses no mutable-workspace state.
```

## 12. Snapshot reconstruction algorithm

```text
reconstructSnapshot(runId):

    begin one read transaction

    validate physical/schema integrity

    load exact revision chain

    load all run facts through current revision R

    verify every reachable ArtifactRef

    validate all typed payloads with M0

    verify referential closure

    verify candidate linearity
    verify obligation/disposition graph
    verify WorkItem source closure
    verify Execution chains and creation bases
    verify Arm/outcome/recovery consistency
    verify cognitive validation consistency
    verify retry limits/one-shot consumption
    verify blocker/disposition consistency
    verify publication-observation qualification request/result consistency
    verify qualification/publication consistency

    derive:
        run
        currentCandidate
        historical arrays
        unresolvedExecutions
        latest applicable readiness designation
        outstanding blockers
        semanticProgressionTerminal
        structurally applicable qualification
        publication intent
        publication confirmation
        gateAReady

    verify complete snapshot invariants

    return immutable snapshot
```

No partial snapshot is returned.

## 13. Resulting-state validation during commit

The mutation/execution M2 brief performs all inserts for revision `R+1` inside
its still-open SQLite write transaction.

Before commit it calls the same reconstruction algorithm against the uncommitted
transaction view.

If reconstruction or any invariant fails:

```text
ROLLBACK entire StateRevision
```

There is no state in which half of an `AssuranceLedgerDelta`, operator
resolution, recovery transition, or campaign bundle becomes authoritative.

## 14. Integrity failure versus invalid proposal

This distinction is mandatory.

### Invalid proposal

Existing retained authority is coherent, but proposed mutation would violate it.

Examples:

```text
second Arm
wrong candidate parent
retry authorization reused
supersession cycle proposed
same logical ID with different new payload
Gate A ready proposed with an outstanding obligation
```

Result:

```text
reject invocation as INVALID_MUTATION
authoritative history remains trustworthy
```

### Integrity failure

Contradiction already exists in retained authority or committed provenance
cannot be verified.

Examples:

```text
missing committed artifact
broken revision chain
two committed candidate payloads in one slot
two committed classifications for one cognitive attempt
database structural corruption
```

Result:

```text
CampaignStateIntegrityError
no normal RunnerResult
no attempt to choose one historical branch
```

M2 must never repair retained authority by choosing the newest convenient row.

## 15. Provenance root

Runner-result provenance is a read-side artifact, not a new StateRevision.

Internal read API:

```ts
interface MaterializeProvenanceRootRequest {
  readonly runId: GateARunId;
  readonly stateRevision: StateRevision;
}

async function materializeProvenanceRoot(
  request: MaterializeProvenanceRootRequest,
): Promise<ArtifactRef>;
```

Algorithm:

```text
require requested revision exists

enumerate every authoritative revision/fact/artifact reachable from the exact
normal-result projection at that revision

construct deterministic manifest ordered by:
    revision
    fact category
    logical identity
    artifact SHA

seal manifest through CampaignArtifactStore

return ArtifactRef
```

The manifest is a projection.

Its existence does not change the GateARun.

Two calls against the same trustworthy revision must produce byte-identical
manifest content and the same SHA-256.

## 16. Example: crash immediately after Arm

History:

```text
revision 12
    AuthorizeExecution(E4)

revision 13
    ArmExecutionDispatch(E4)
```

No executor result was ever committed.

Process crashes.

A later process acquires ownership generation `5` and reconstructs revision 13.

M2 sees:

```text
E4 exists
Arm(E4) exists
no direct terminal outcome
no terminal recovery resolution
```

It therefore returns:

```ts
snapshot.unresolvedExecutions = [
  {
    execution: E4,
    workItem: exactW,
    dispatchState: "POSSIBLY-DISPATCHED",
    dispatchIntent: exactRevision13ArmMutationArtifact,
    dispatchEvidence: exactArmEvidence,
    terminalOutcome: null,
    recoveryCapability: exactArmCapabilityOrNull,
  },
];
```

This result is required even when:

```text
M4/M7 never returned
no AdmitExecutionUncertaintyV1 exists
actual external call may never have begun
```

The new session must enter the M8 recovery barrier before normal external
dispatch.

## 17. Edge cases

* Database can parse but revision 7 is missing between 6 and 8:
  integrity failure.
* Highest ordinal candidate has wrong parent: integrity failure.
* Historical retry authorization is consumed: still present in snapshot
  authorization history.
* Old WorkItem whose obligations are all disposed: still present, but not
  enabled by that fact alone.
* Authorized-not-dispatched Execution whose obligations became superseded:
  remains historical, is not unresolved, and is never armed unless it becomes
  lawfully dispatchable again.
* Armed Execution whose source obligation is later superseded: remains
  unresolved until outcome/recovery closure.
* Pending recovery blocker exists and execution remains armed: execution remains
  in `unresolvedExecutions`.
* UNRESOLVABLE recovery exists: execution leaves `unresolvedExecutions`;
  blocker remains.
* Old qualification exists for previous readiness basis: historical DB retains
  it, projected `gateQualification` is null or another matching qualification.
* Protocol changes and later returns exactly to an older protocol: an
  append-only readiness re-designation can make an existing readiness object
  the latest designation again.
* CAS contains extra unreferenced blob: ignored by snapshot.
* Artifact has correct path name but wrong bytes: integrity failure.

## 18. Constraints

* Snapshot is always reconstructed, never authoritative by cache.
* Snapshot order is deterministic.
* No mutable workspace may fill a missing authoritative field.
* Currentness is not inferred by M2.
* Historical facts are never filtered out merely because they are stale.
* `snapshot.blockers` is intentionally an outstanding-only projection.
* `snapshot.executionRetryAuthorizations` is intentionally historical.
* `semanticProgressionTerminal` is monotonic within one run.
* Integrity ambiguity fails closed.
* There is no best-effort snapshot.

## 19. Integration

Read-only load:

```ts
const snapshot = await campaignState.loadGateARunSnapshot({ runId });
```

Ownership acquisition uses this same reconstruction after generation insertion.

The mutation/execution M2 brief calls reconstruction inside every uncommitted
write transaction before commit.

M1 must treat the snapshot returned by the latest successful M2 call as its only
campaign-state view.

It may not merge it with a stale local snapshot.
