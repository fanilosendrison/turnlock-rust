---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-09-20"
step_id: 2
id: NIB-M-GATE-A-CAMPAIGN-STATE-PERSISTENCE-OWNERSHIP
version: "3.0.3"
scope: gate-a-campaign-runner/campaign-state/persistence-ownership
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Campaign State — Persistence and Ownership

## 1. Status, authority, and purpose

This document is one of three active Module Briefs that together close M2
`campaign-state` for the Gate A hostile-review campaign runner.

It consumes:

```text
NIB-S-GATE-A-CAMPAIGN-RUNNER 11.0.0
NIB-M-GATE-A-CONTRACTS 1.2.0
```

Version `3.0.3` is a dependency-only construction correction. Its only
correction is the exact JavaScript `bigint` representation for integer-valued
PRAGMA verification under active
`DC-SQLITE-NODE-GATE-A-CAMPAIGN-STATE` version `1.0.1`. It makes exactly:

```text
no package change
no SQLite version change
no Node floor change
no transaction change
no persistence algorithm change
no schema-version change
no product semantic change
no protocol semantic change
no QLEK/Admission/recovery change
```

The SQLite authoritative schema remains exactly `2`.

Version `3.0.2` is a dependency-only construction synchronization. It binds M2
persistence/ownership to active
`DC-SQLITE-NODE-GATE-A-CAMPAIGN-STATE` version `1.0.0`. It makes:

```text
no TURNLOCK product semantic change
no hostile-review protocol semantic change
no M2 persistence algorithm change
no SQLite schema-version change
no QLEK / Admission / fencing semantic change
no retry or recovery semantic change
```

The SQLite authoritative schema remains exactly `2`.

Version `3.0.1` is an additive construction-completeness correction. It closes
the exact projection of positively cleared local semantic hazards into
`SemanticHistoryExportV1.hazardClearances`, including their immutable evidence
closure and out-of-order export monotonicity. It makes:

```text
no TURNLOCK product semantic change
no protocol semantic change
no QLEK identity change
no Admission semantics change
no recovery classification change
no SQLite schema-version change
```

The SQLite authoritative schema remains exactly `2`.

Version `3.0.0` is a breaking construction-contract revision. It establishes one
coherent M2 semantic-authority domain per configured `stateRoot`, authoritative
schema version 2, the domain/QLEK SQLite coordination realization, global
semantic-history storage, export and external reconciliation. No production
runner state exists, so no runtime migration mechanism is required. Schema-v1
runtime state is not migrated.

Version `2.0.12` was a dependency-only synchronization with NIB-S `10.0.0`. It
changes no persistence algorithm, ownership, type, retry, hard-limit, provider,
recovery, or repository semantic. The retained
`ReviewCampaignPrerequisiteBasisRefV1.reviewContext` remains exact immutable
review provenance and is not replaced by `ResolutionContextV1`.

Version `2.0.11` is a dependency-only / construction-only compatibility
synchronization with NIB-S `9.1.2`. It changes no persistence or ownership
algorithm and no retry, hard-limit, type, provider, recovery, or repository
semantics.

The newly retained `retryPolicy` field remains embedded in the immutable
`EstablishReviewCampaignBundleV1` mutation artifact.

No SQLite table or authoritative-history schema change is required.

Authoritative-history schema version remains exactly 1.

Version `2.0.10` is a dependency-only / construction-only compatibility
synchronization with NIB-S `9.1.1`. It changes no persistence or ownership
algorithm and no type, provider, recovery, or repository semantics.

The expanded `ReviewCampaignPrerequisiteBasisRefV1` remains carried inside the
immutable `EstablishReviewCampaignBundleV1` mutation artifact.

No SQLite schema-version change is required.

Authoritative-history schema version remains exactly 1.

Version `2.0.9` was a dependency-only compatibility synchronization with NIB-S
`9.1.0`. It changed no algorithm, type, or module invariant.

Version `2.0.8` is dependency-only synchronization with NIB-S `9.0.1`.

NIB-S `9.0.1` requires no SQLite schema-version change and no new authoritative
table.

The exact prerequisite basis is already durably reconstructible because every
committed `StateRevision` retains its immutable mutation artifact and
`EstablishReviewCampaignBundleV1` contains the complete exact basis.

Schema version remains exactly `1`.

Physical layout, SQLite configuration, and ownership semantics are unchanged.

Version `2.0.7` was dependency-only compatibility synchronization with
NIB-S-GATE-A-CAMPAIGN-RUNNER `9.0.0`.

`AssuranceRepositoryProjectionRef` is a companion-M2 domain relation/fact
owned by the mutation/execution and snapshot/integrity contracts. It does not
alter the selected persistence or ownership architecture and introduces no SQL
schema detail in this brief.

It is implementation-construction authority only. It does not define TURNLOCK
product semantics, canonical formal semantics, hostile-review protocol
semantics, formal-assurance claims, review evidence, or verification evidence.

This brief defines the physical persistence, immutable-artifact storage,
bootstrap, run write ownership, semantic-domain coordination, QLEK live
exclusion, semantic-history export/reconciliation transaction boundaries, and
fencing mechanics for M2 `campaign-state`.

Mutation semantics are defined by
`NIB-M-GATE-A-CAMPAIGN-STATE-MUTATION-EXECUTION`.

Snapshot reconstruction and retained-state integrity are defined by
`NIB-M-GATE-A-CAMPAIGN-STATE-SNAPSHOT-INTEGRITY`.

M2 uses SQLite as the transactional engine for Authoritative History.

M2 persistence consumes:

```text
DC-SQLITE-NODE-GATE-A-CAMPAIGN-STATE 1.0.1
```

The active contract closes the package and consumed dependency behavior exactly:

```text
runtime package:
better-sqlite3@13.0.3

runtime floor:
Node.js >=22.19.0

bundled SQLite:
3.53.4
```

M2 owns why and where these dependency mechanisms realize accepted persistence,
ownership, and coordination requirements. The Dependency Contract owns their
external-library behavior.

## 2. Inputs

The public cross-module requests are the exact NIB-S types:

```ts
CreateGateARunAndAcquireInitialOwnershipRequest
AcquireWriteOwnershipRequest
LoadGateARunSnapshotRequest
CommitAuthoritativeMutationRequest
AcquireAdmissionAuthorityRequestV1
ReleaseAdmissionAuthorityRequestV1
ExportSemanticHistoryRequestV1
ReconcileExternalSemanticHistoryRequestV1
```

This brief additionally fixes the construction-time M2 configuration:

```ts
interface CampaignStateRuntimeConfig {
  readonly stateRoot: string;
}
```

`stateRoot` is resolved once at process composition time.

It must be:

* absolute;
* durable across runner-process restart;
* writable by the runner;
* outside the candidate repository worktree;
* shared by all M2 instances that may resume the same `GateARun`.

The source of the operational configuration value belongs to the M1 brief. M2
accepts only the already-resolved value.

## 3. Physical layout

M2 owns this exact layout below `stateRoot`:

```text
<stateRoot>/
├── authoritative/
│   └── campaign-state.sqlite
├── ownership/
│   └── <GateARunId>.sqlite
├── semantic-authority/
│   ├── domain.sqlite
│   └── qlek/
│       └── <first-two-hex>/
│           └── <qlek-64-lowercase-hex>.sqlite
├── artifacts/
│   └── sha256/
│       └── <first-two-hex>/
│           └── <64-lowercase-hex>
└── temp/
```

Mutable candidate worktrees and executor workspaces are not stored here unless
another accepted NIB explicitly selects a subdirectory under a separate mutable
workspace root.

`authoritative/campaign-state.sqlite` is the sole M2 Authoritative History
database for all GateARun-local and all global protocol-v8 semantic history in
the domain. Do not create a second semantic database.

Artifact files under `artifacts/sha256/` are durable immutable bytes but are not
authoritative merely because they exist.

`ownership/*.sqlite` and `semantic-authority/*.sqlite` files contain no campaign
or semantic truth. They are OS/process coordination mechanisms only.

For QLEK `qlek-sha256:<digest>`, use the exact existing 64-lowercase-hex
`digest` in the QLEK lock path without rehashing it.

## 4. SQLite configuration

### 4.1 Authoritative database

Every authoritative connection must enable:

```text
foreign_keys = ON
journal_mode = WAL
synchronous = FULL
busy_timeout = 5000ms
```

Every authoritative write uses:

```text
BEGIN IMMEDIATE
```

and commits exactly one atomic authoritative transition.

Schema version is exactly:

```text
2
```

Unknown schema version is `INTEGRITY_FAILURE`.

No automatic migration exists. Schema-v1 runtime state is not migrated because
no production campaign runner state exists.

### 4.2 Per-run ownership database

Each:

```text
ownership/<runId>.sqlite
```

contains only a lock sentinel table.

Its connection uses:

```text
journal_mode = DELETE
synchronous = FULL
busy_timeout = 0
```

Exclusive writer ownership is represented by one connection holding:

```text
BEGIN IMMEDIATE
```

open for the entire lifetime of the acquired `WriteAuthorityRef`.

The database contains no PID, heartbeat, lease deadline, owner timestamp, or
semantic state.

`SQLITE_BUSY` when attempting `BEGIN IMMEDIATE` means:

```text
ACTIVE_OWNER_CONFLICT
```

No other interpretation is permitted.

Process termination releases the operating-system-backed SQLite lock.

A hung process remains owner until the lock is actually released.

## 5. Authoritative core schema

The implementation must create at least these append-only authoritative
relations:

```text
schema_metadata
runs
state_revisions
ownership_generations
preflight_establishments
artifact_registry
semantic_domain
semantic_coordination_epochs
semantic_admission_authority_grants
semantic_execution_bindings
semantic_arm_bindings
protocol_v8_semantic_validations
semantic_admission_claims
semantic_admission_witnesses
semantic_admission_conflicts
semantic_history_exports
semantic_external_history_reconciliations
semantic_external_hazards
semantic_external_hazard_clearances
semantic_external_unarmed_trajectories
```

Domain relations defined by the companion M2 briefs use the same database.

### 5.1 `runs`

Logical columns:

```text
run_id                  PRIMARY KEY
bootstrap_session_id    UNIQUE NOT NULL
root_obligation_id      UNIQUE NOT NULL
created_revision        NOT NULL CHECK = 0
```

A `runs` row is never updated.

Baseline repository authority and publication target are not mutable columns on
this row; they are established by an append-only `preflight_establishments`
fact.

### 5.2 `state_revisions`

Logical columns:

```text
run_id
revision_integer
previous_revision_integer
mutation_artifact_sha256 nullable only for revision 0
session_id
ownership_generation
mutation_kind
PRIMARY KEY(run_id, revision_integer)
```

Rules:

```text
revision 0:
    previous_revision = null
    mutation kind = bootstrap

revision N > 0:
    previous_revision = N - 1
    mutation artifact exists
```

A `StateRevision` exposed cross-module is the canonical decimal string for
`revision_integer`:

```text
0
1
2
...
```

No leading zero is accepted except the exact string `"0"`.

### 5.3 `ownership_generations`

Logical columns:

```text
run_id
generation
session_id
acquired_at_revision
PRIMARY KEY(run_id, generation)
UNIQUE(run_id, session_id, generation)
```

Generation begins at:

```text
1
```

and increases by exactly one on each successful ownership transfer.

Ownership acquisition does not create a new `StateRevision`.

### 5.4 Append-only enforcement

No authoritative relation may be updated or deleted by normal M2 operation.

The SQLite schema must install `BEFORE UPDATE` and `BEFORE DELETE` triggers on
authoritative history relations that abort the statement.

State change is represented only by inserting later facts.

## 6. Immutable artifact store

M2 provides one non-authoritative infrastructure utility for the runner:

```ts
interface CampaignArtifactStore {
  sealRunnerArtifact(input: {
    readonly bytes: Uint8Array;
    readonly mediaType: string;
  }): Promise<ArtifactRef>;

  ingestReferencedArtifact(input: {
    readonly ref: ArtifactRef;
    readonly bytes: Uint8Array;
  }): Promise<void>;

  readVerified(ref: ArtifactRef): Promise<Uint8Array>;

  verify(ref: ArtifactRef): Promise<void>;
}
```

This utility may be used by sibling runner modules for immutable artifact
durability.

Using this store does not grant the caller authoritative-state write access.

### 6.1 CAS identity

The physical CAS path is derived only from:

```text
ArtifactRef.sha256
```

not from `artifactId`, `repositoryPath`, or media type.

Runner-owned artifacts created by `sealRunnerArtifact` use:

```text
artifactId = "sha256:" + sha256
repositoryPath = null
```

Existing externally defined `ArtifactRef` values retain their authoritative
`artifactId`.

Different external `artifactId` values may refer to identical bytes.

One `artifactId` may never be registered against two different SHA-256 values.

### 6.2 Artifact publication algorithm

For bytes `B`:

```text
sha = lowercase SHA-256(B)
target = artifacts/sha256/<sha[0:2]>/<sha>

if target already exists:
    verify target bytes hash exactly to sha
    return/use target

else:
    create parent directory
    write B to unique file under temp/
    fsync temporary file
    rename temporary file to target
    fsync target parent directory
    verify target SHA-256 and byte length
```

A crash may leave an orphan temporary file or an unreferenced valid CAS blob.

Both are non-authoritative garbage.

A committed authoritative `ArtifactRef` whose CAS bytes are missing, truncated,
or hash-invalid is an `INTEGRITY_FAILURE`.

## 7. Bootstrap identity

`GateARunId` is an occurrence identity.

M2 generates it with Node cryptographic randomness as:

```text
RUN-<lowercase UUIDv4>
```

The future M0 final-closure brief must expose a validator matching this exact
format.

The root preflight `ObligationId` is deterministic:

```text
deriveId(
  "gate-a-root-preflight-obligation.v1",
  runId,
  preflightObligationDefinition.sha256
)
```

The exact `deriveId` byte framing belongs to M0 final closure and must be
collision-safe and domain-separated.

M2 must recompute this ID before inserting the root obligation.

## 8. Bootstrap algorithm

Public function:

```ts
async function createGateARunAndAcquireInitialOwnership(
  request: CreateGateARunAndAcquireInitialOwnershipRequest,
): Promise<CreateGateARunAndAcquireInitialOwnershipResult>
```

Algorithm:

```text
1. Validate request using M0 runtime validators.

2. Verify request.preflightObligationDefinition equals the exact immutable
   M0 root preflight-obligation definition.

3. Verify the referenced definition artifact exists and is intact.

4. Generate a fresh GateARunId.

5. Open/create ownership/<runId>.sqlite.

6. Execute BEGIN IMMEDIATE with busy_timeout = 0.
   A collision/busy state for a newly generated run ID causes generation of a
   different fresh run ID before any authoritative insert.

7. Keep the ownership transaction open.

8. BEGIN IMMEDIATE on campaign-state.sqlite.

9. Re-run authoritative database integrity preconditions required by the
   snapshot/integrity M2 brief.

10. Require no row already exists for runId.

11. Derive the root preflight ObligationRef:
        runId = runId
        candidateId = null
        reviewCampaignId = null
        definition = exact supplied M0 definition

12. Insert atomically:
        runs row
        root obligation row
        state revision 0
        ownership generation 1

13. Construct:
        WriteAuthorityRef {
          runId,
          sessionId,
          generation: 1,
          acquiredAtStateRevision: "0"
        }

14. Reconstruct and validate the revision-0 snapshot using the
    snapshot/integrity M2 brief.

15. COMMIT campaign-state.sqlite.

16. Register the open ownership-lock connection in the process-local ownership
    handle registry under (runId, sessionId, generation).

17. Return:
        kind = created
        run
        authority
        preflightObligation
        snapshot
```

There is no visible state where:

```text
run exists but root obligation does not
run exists but ownership generation 1 does not
run exists at a revision other than 0 before bootstrap completes
```

If the authoritative transaction fails:

```text
ROLLBACK
close ownership connection
release lock
```

and return:

```text
kind = rejected
reason = INTEGRITY_FAILURE
```

only when trustworthy bootstrap cannot be established.

## 9. Bootstrap replay behavior

`bootstrap_session_id` is unique.

If the exact same process invokes bootstrap again with the same `sessionId`
while its original local ownership handle is still held, M2 returns the already
created run only when all of these match exactly:

```text
same sessionId
same preflight definition
same local ownership handle
same authoritative run
```

It must not create a second run.

A different later RunnerSession performing `start` is a distinct run creation.

M2 does not infer that two different sessions represent a retry of one lost
bootstrap response.

## 10. Ownership acquisition algorithm

Public function:

```ts
async function acquireWriteOwnership(
  request: AcquireWriteOwnershipRequest,
): Promise<AcquireWriteOwnershipResult>
```

Algorithm:

```text
1. Validate request.

2. If this process already holds the exact run lock:
      if held sessionId == request.sessionId:
          load trustworthy current snapshot using snapshot/integrity M2
          validation

          if trustworthy current snapshot cannot be established:
              return:
                  kind = rejected
                  reason = INTEGRITY_FAILURE

          if request.expectedStateRevision != snapshot.stateRevision:
              return:
                  kind = rejected
                  reason = STALE_STATE
                  currentStateRevision = snapshot.stateRevision
              without releasing the already-held ownership handle

          return:
              kind = acquired
              authority = existing authority
              snapshot = current snapshot
      otherwise:
          return ACTIVE_OWNER_CONFLICT

3. Open ownership/<runId>.sqlite.

4. Attempt BEGIN IMMEDIATE.

5. If SQLite reports BUSY:
      close attempted connection
      return:
          kind = rejected
          reason = ACTIVE_OWNER_CONFLICT

6. BEGIN IMMEDIATE on authoritative DB.

7. Establish trustworthy current run state using snapshot/integrity M2
   validation.

   If trustworthy current run state cannot be established:
      ROLLBACK authoritative DB
      ROLLBACK/close ownership DB
      return:
          kind = rejected
          reason = INTEGRITY_FAILURE

8. If request.expectedStateRevision != exact current StateRevision:
      ROLLBACK authoritative DB
      ROLLBACK/close ownership DB
      return:
          kind = rejected
          reason = STALE_STATE
          currentStateRevision = exact current revision

9. Read maximum ownership generation G.

10. Insert generation G + 1 bound to:
        request.sessionId
        acquiredAtStateRevision = exact current revision

11. Construct exact WriteAuthorityRef.

12. Reconstruct snapshot at the unchanged StateRevision.

13. COMMIT authoritative ownership-generation insert.

14. Keep ownership transaction/connection open and register local handle.

15. Return acquired authority + snapshot.
```

No rejected ownership acquisition mutates GateARun campaign state.

## 11. Commit fencing primitive

Before the mutation/execution M2 brief may enter an authoritative campaign-state
mutation transaction, this brief requires all of:

```text
process has a live local ownership handle for runId
handle.sessionId == request.authority.sessionId
handle.generation == request.authority.generation
handle ownership SQLite transaction is still usable
request.authority.runId == request.runId
durable maximum OwnershipGeneration == request.authority.generation
```

If the local handle is absent or the durable generation is newer:

```text
ownership-lost
```

If ownership authority cannot be trusted because storage is corrupt:

```text
implementation/integrity failure
```

Ownership generation and StateRevision are independent concurrency dimensions:

```text
OwnershipGeneration
    fences former writers

StateRevision
    performs optimistic campaign-state CAS
```

## 12. Dependency Contract requirement

`DC-SQLITE-NODE-GATE-A-CAMPAIGN-STATE` version `1.0.1` is active and required by
GREEN.

Use that contract as the sole external-dependency authority for:

```text
package identity
Node floor
SQLite version
connection API
PRAGMAs
BEGIN IMMEDIATE realization
BUSY/error mapping
integer behavior
close/rollback behavior
process-crash lock release
prepared statements
foreign-key behavior
many-open-connection behavior
```

The package and consumed dependency behavior are closed by the active contract.
Do not substitute another SQLite package or behavior because it is more
convenient.

This brief remains M2 authority for why those mechanisms are used, including the
`stateRoot` layout, authoritative schema version 2, run ownership, QLEK/domain
coordination topology, M2 state semantics, artifact-store relationship,
T1/T4/T5 lock ordering, and semantic-history export/reconciliation.

## 13. Example

Initial call:

```ts
{
  repositoryPath: "/workspace/turnlock-rust",
  sessionId: "SESSION-11111111-1111-4111-8111-111111111111",
  preflightObligationDefinition: {
    artifactId: "sha256:aaaaaaaa...",
    sha256: "aaaaaaaa...",
    byteLength: 512,
    mediaType: "application/json",
    repositoryPath: null,
  },
}
```

M2 creates:

```text
RUN-aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee
revision 0
ownership generation 1
one root preflight obligation
```

A second process attempts ownership and receives SQLite BUSY:

```ts
{
  kind: "rejected",
  reason: "ACTIVE_OWNER_CONFLICT",
}
```

The first process crashes.

The OS releases its SQLite lock.

A new session supplies exact revision `"0"` and acquires generation `2`.

`StateRevision` remains `"0"`.

Any request carrying generation `1` is thereafter fenced.

## 14. Edge cases

* Authoritative SQLite file missing after one or more runs were known to exist:
  `INTEGRITY_FAILURE`; never silently create an empty replacement database.
* Unknown requested run ID: invocation/process error, not a CampaignBlocker.
* Ownership DB BUSY: `ACTIVE_OWNER_CONFLICT`.
* Expected revision stale during acquisition: release newly obtained lock and
  return `STALE_STATE`.
* Crash after acquiring ownership lock but before ownership-generation commit:
  no generation is created; crash releases the lock.
* Crash after ownership-generation commit: new generation remains authoritative
  and fences prior owners.
* Artifact CAS write succeeds but campaign commit fails: orphan artifact is
  allowed.
* Campaign row references missing CAS bytes: `INTEGRITY_FAILURE`.
* SQLite schema version mismatch: `INTEGRITY_FAILURE`; no auto-migration.
* State root resolves inside the candidate repository: configuration failure
  before bootstrap.
* Read-only filesystem: invocation failure; never convert to
  `OPERATOR-ACTION-REQUIRED`.
* Failure to fsync a newly written artifact: artifact sealing fails and no
  authoritative mutation may reference it.

## 15. Constraints

* SQLite is the sole authoritative transaction engine in schema v2.
* No mutable snapshot file is authoritative.
* No filesystem lock file is ownership authority.
* No lease timeout can transfer authority.
* Ownership acquisition never increments `StateRevision`.
* Campaign mutation never increments `OwnershipGeneration`.
* CAS bytes may exist without authority; authority may never reference missing
  CAS bytes.
* No authoritative relation is updated or deleted.
* No module other than M2 writes `campaign-state.sqlite`.
* The shared artifact-store utility is not an alternate campaign-state writer.
* Mutable workspaces never substitute for authoritative history.

## 16. Integration

M1 process composition creates M2 with one resolved
`CampaignStateRuntimeConfig`.

Start:

```ts
const bootstrap =
  await campaignState.createGateARunAndAcquireInitialOwnership(request);
```

Resume:

```ts
const ownership =
  await campaignState.acquireWriteOwnership({
    runId,
    sessionId,
    expectedStateRevision,
  });
```

The mutation/execution M2 brief uses the retained ownership handle before every
authoritative mutation.

The snapshot/integrity M2 brief owns the snapshot reconstruction and integrity
calls used by bootstrap, ownership acquisition, load, and commit.

## 17. Coherent semantic-authority domain

Fix exactly:

```text
one CampaignStateRuntimeConfig.stateRoot
=
one coherent M2 Authoritative History domain
```

All GateARuns intended to observe or reuse each other's exact protocol-v8
semantic admissions must use the same `stateRoot`. Different roots are
physically disconnected authority domains until explicit T5 reconciliation.
QLEK contains no `stateRoot`, `SemanticAuthorityDomainId`, filesystem path, or
database identity.

On fresh authoritative-database creation, generate exactly one immutable local
`SemanticAuthorityDomainId` with Node cryptographic randomness as:

```text
SEM-DOMAIN-<lowercase UUIDv4>
```

Persist it in the singleton `semantic_domain` row. It is operational provenance,
not semantic identity, and never enters QLEK. Initialize the domain-global
`SemanticCoordinationEpoch` to `1`.

## 18. Semantic coordination databases

Configure `semantic-authority/domain.sqlite` and every per-QLEK lock database
with:

```text
journal_mode = DELETE
synchronous = FULL
busy_timeout = 0
```

Each contains one sentinel table only. Exclusive ownership is one connection
holding `BEGIN IMMEDIATE`. Persist no PID, heartbeat, lease deadline, timestamp,
semantic candidate, Admission, QLEK payload, lock-held flag, owner PID, lease
expiry, or live-authority boolean in a coordination database.

Use `domain.sqlite` as a short-lived process-coordination gate serializing:

```text
new AdmissionAuthority generation issuance
semantic-history export epoch closure
T5 cross-domain reconciliation
```

Never hold the domain gate for an entire LLM execution.

Use one per-QLEK lock for T1 acquisition, T2/T3 through one live
`AdmissionAuthorityRefV1`, T4 reconciliation, semantic-history export closure,
and T5 reconciliation. For T1, retain the lock from successful acquisition
until successful T3, explicit release, or process death. For T4, T5, and export,
use it only for short-lived transaction coordination.

## 19. Authority dimensions and counters

Keep exactly two independent authority dimensions:

```text
WriteAuthorityRef
→ exclusive authority for one GateARun mutation stream

AdmissionAuthorityRefV1
→ exclusive live semantic-dispatch authority for one exact QLEK
```

One never substitutes for the other. T2 and T3 require both. T1, T4, and T5 do
not require GateARun write authority because they do not mutate a GateARun.

`SemanticCoordinationEpoch` is domain-global, starts at `1`, advances only by the
exact export/T5 contracts below, and never wraps. `AdmissionAuthorityGeneration`
is monotone per `(QLEK, epoch)`, begins at `1`, and increments by exactly one for
each successful T1 acquisition in that epoch. A later epoch begins generation
at `1`; never compare generations across epochs. Overflow beyond
`Number.MAX_SAFE_INTEGER` fails closed as implementation/integrity capacity
exhaustion.

## 20. T1 AdmissionAuthority acquisition and release

Implement `acquireAdmissionAuthority(K, session)` exactly:

```text
validate request

acquire domain coordination gate non-blocking
if BUSY:
    return busy(K)

acquire exact per-QLEK lock non-blocking
if BUSY:
    release domain gate
    return busy(K)

BEGIN IMMEDIATE authoritative database

reconstruct exact SemanticQuestionState(K)
apply exact T1 branch priority from the snapshot/integrity brief

if branch is not acquired:
    ROLLBACK authoritative database
    release QLEK lock
    release domain gate
    return exact branch

epoch = exact current SemanticCoordinationEpoch

generation =
    max grant generation for (K, epoch) + 1
    or 1 when no grant exists

require safe-integer generation

append exact AdmissionAuthorityGrant(K, epoch, generation, session)
COMMIT authoritative database

register exact open QLEK lock handle process-locally under:
    (K, session, epoch, generation)

release domain gate

return acquired(
    AdmissionAuthorityRefV1,
    freshly reconstructed state
)
```

Evaluate the exact reconstructed branch priority before and after taking live
coordination locks. A crash after durable grant commit but before local handle
registration leaves the grant as history; OS lock release permits a later T1 to
issue a newer generation. Never reuse the stale grant as a live handle.

`releaseAdmissionAuthority` writes no authoritative fact, deletes no grant,
ROLLBACKs/closes only the exact lock-database transaction, removes the
process-local handle, and returns `released`; return `not-held` when that exact
handle is absent. A later acquisition receives a new generation.

Never wait while attempting another run ownership lock under an already-held
QLEK authority. If the run owning a cross-run resumable trajectory is busy, the
caller explicitly releases AdmissionAuthority and retries later; it never waits
holding K or creates another same-K Execution.

## 21. Authoritative schema-v2 semantic relations

Retain every schema-v1 relation and add the append-only relations listed in
section 5. Install the same aborting `BEFORE UPDATE` and `BEFORE DELETE` triggers
on every new authoritative relation. Define at least these logical columns and
constraints:

```text
semantic_domain
---------------
singleton_key = 1 PRIMARY KEY
domain_id UNIQUE NOT NULL
created_schema_version = 2

semantic_coordination_epochs
----------------------------
epoch PRIMARY KEY
reason ∈ {initial, export, external-reconciliation}
source_domain_id nullable
source_history_sha256 nullable
export_sha256 nullable

epochs contiguous from 1

semantic_admission_authority_grants
-----------------------------------
qlek
epoch
generation
session_id
PRIMARY KEY(qlek, epoch, generation)

generation contiguous from 1 within (qlek, epoch)

semantic_execution_bindings
---------------------------
execution_id PRIMARY KEY
run_id
work_item_id
qlek
bound_candidate_revision_id nullable
semantic_question_binding_sha256
introduced_run_revision

semantic_arm_bindings
---------------------
execution_id PRIMARY KEY
qlek
domain_id
epoch
generation
introduced_run_revision

protocol_v8_semantic_validations
--------------------------------
execution_id PRIMARY KEY
qlek
classification
semantic_admission_id nullable
semantic_candidate_sha256 nullable
semantic_question_binding_sha256 nullable
execution_receipt_sha256 nullable
origin_witness_sha256 nullable
introduced_run_revision

all semantic candidate/witness/receipt fields non-null
iff classification == protocol-valid

semantic_admission_claims
-------------------------
qlek
admission_id
semantic_candidate_sha256
semantic_question_binding_sha256
PRIMARY KEY(qlek, admission_id)

semantic_admission_witnesses
----------------------------
witness_sha256 PRIMARY KEY
qlek
admission_id
source_domain_id
origin_execution_id

semantic_admission_conflicts
----------------------------
qlek
admission_a_id
admission_b_id
PRIMARY KEY(qlek, admission_a_id, admission_b_id)
CHECK admission_a_id < admission_b_id

semantic_history_exports
------------------------
export_sha256 PRIMARY KEY
closed_epoch UNIQUE
successor_epoch UNIQUE

semantic_external_history_reconciliations
-----------------------------------------
source_domain_id
source_closed_epoch
source_history_sha256
target_epoch
PRIMARY KEY(source_domain_id, source_history_sha256)
UNIQUE(source_domain_id, source_closed_epoch)

semantic_external_hazards
-------------------------
source_domain_id
source_execution_id
qlek
source_epoch
source_generation
source_history_sha256
PRIMARY KEY(source_domain_id, source_execution_id, qlek)

semantic_external_hazard_clearances
-----------------------------------
source_domain_id
source_execution_id
qlek
clearance_kind
source_history_sha256
PRIMARY KEY(source_domain_id, source_execution_id, qlek)

semantic_external_unarmed_trajectories
--------------------------------------
source_domain_id
source_execution_id
qlek
source_history_sha256
PRIMARY KEY(source_domain_id, source_execution_id, qlek)
```

Treat the same source domain plus same closed epoch with a different source
history SHA as `SEMANTIC-HISTORY-INTEGRITY-FAILURE`.

Create no `semantic_facts`, `fact_status`, `qualification_status`,
`semantic_status`, `qlek_status`, `admission_pending`,
`current_semantic_execution`, `consumed_flag`, or equivalent mutable semantic
status table. SemanticFact remains derived/reconstructible under C4/M5/M6
authority.

## 22. Lock ordering

Use exactly:

```text
T1:
domain gate
→ exact QLEK lock
→ authoritative DB

T4:
exact QLEK lock
→ authoritative DB

export/T5:
domain gate
→ authoritative DB BEGIN IMMEDIATE
→ determine exact QLEK set
→ QLEK locks in QLEK ASCII ascending order, non-blocking
```

If an export/T5 QLEK lock is busy, release every already acquired QLEK lock,
ROLLBACK the authoritative DB, release the domain gate, and return `busy` with
that QLEK. This avoids deadlock with T2/T3/T4, which already hold one exact QLEK
lock before entering the authoritative DB.

## 23. Semantic-history export

Implement `exportSemanticHistory` exactly:

```text
acquire domain gate non-blocking
if BUSY:
    return busy(domain)

BEGIN IMMEDIATE authoritative DB

determine every local QLEK present in:
    grants
    semantic execution bindings
    arm bindings
    validations
    claims
    external hazards
    external unarmed history

sort QLEKs exact ascending
acquire every exact QLEK lock in that order, non-blocking

if any lock BUSY:
    release all acquired QLEK locks
    ROLLBACK authoritative DB
    release domain gate
    return busy(qlek)

currentEpoch = exact max epoch
successorEpoch = currentEpoch + 1
require safe integer

reconstruct exact complete SemanticHistoryExportV1
from this same authoritative transaction snapshot

closedEpoch = currentEpoch
successorEpoch = currentEpoch + 1

canonical serialize with M0 CanonicalRunnerJsonBytesV1
seal through CampaignArtifactStore as application/json
require repositoryPath == null
verify sealed artifact

append semantic_coordination_epochs(
    successorEpoch,
    reason = export,
    export_sha256
)
append semantic_history_exports(
    export_sha256,
    closedEpoch,
    successorEpoch
)

COMMIT authoritative DB
release every QLEK lock
release domain gate
return exported
```

Seal bytes before DB commit; orphan CAS bytes are allowed if the DB commit
fails. Change no GateARun `StateRevision`. Epoch advance invalidates every
previously issued AdmissionAuthorityRef.

Export local hazards and unarmed trajectories in external form with
`sourceDomainId = local domain ID`. Require `successorEpoch == closedEpoch + 1`.
Sort duplicate-free arrays exactly:

```text
authorityGrants:
(qlek, epoch, generation)

executionBindings:
(qlek, execution.runId, execution.executionId)

armBindings:
(qlek, execution.runId, execution.executionId)

semanticValidations:
(qlek, execution.runId, execution.executionId)

admissionClaims:
(qlek, admissionId)

originWitnesses:
(qlek, admissionId, sourceDomainId, originExecutionId, witness.sha256)

unresolvedHazards:
(qlek, sourceDomainId, sourceExecution.executionId)

hazardClearances:
(qlek, sourceDomainId, sourceExecution.executionId)

unarmedTrajectories:
(qlek, sourceDomainId, sourceExecution.executionId)

artifactClosure:
(sha256, artifactId)
```

Use unsigned UTF-8/ASCII byte order as applicable.

### 23.1 Local positive-clearance projection

For every local Armed P8 semantic Execution `E`, let:

```text
K =
exact retained SemanticExecutionBinding(E).qlek

D =
exact local SemanticAuthorityDomainId

L =
exact SemanticExecutionLocatorV1 for E
```

When and only when exact retained local authority positively clears the semantic
hazard for `E`, export exactly one:

```ts
ExternalSemanticHazardClearanceRefV1 {
  sourceDomainId: D,
  sourceExecution: L,
  qlek: K,
  kind: exact mapping in section 23.3,
  evidence: exact mapping in section 23.3,
}
```

Never manufacture a clearance for an unresolved hazard.

### 23.2 Introducing mutation artifact

Define mechanically:

```text
introducingMutationArtifact(F)
```

as the exact immutable `ArtifactRef` named by the unique authoritative
`state_revisions` row whose mutation first introduced run-local fact `F`. Use
the retained artifact itself. Do not construct or reseal another copy.

### 23.3 Exhaustive clearance-kind and evidence mapping

These four mappings are exhaustive. No other local fact creates an exported
semantic hazard clearance.

For exact authoritative:

```text
ExecutionRecoveryResolution {
  executionId = E.executionId
  classification = "PROVEN-NOT-EXECUTED"
}
```

produce:

```text
kind =
"proven-not-executed"

evidence =
orderedUnique([
  introducingMutationArtifact(the exact admitted recovery resolution),
  ...resolution.evidence
])
```

The introducing mutation is the exact retained
`AdmitExecutionRecoveryV1` artifact. Its inclusion guarantees non-empty
evidence independently of the inner evidence array.

For exact authoritative:

```text
TechnicalExecutionFailure F
where
F.execution == E
and
F.completedResponse == false
```

produce:

```text
kind =
"terminal-technical-no-completion"

evidence =
orderedUnique([
  introducingMutationArtifact(F),
  ...F.failureEvidence
])
```

This applies whether `F` was introduced through direct
`AdmitExecutionOutcomeV1` or through `AdmitExecutionRecoveryV1` with
`PROVEN-COMPLETED` and `recoveredOutcome.kind = technical-failure`. The
Execution may have only one authoritative terminal outcome. Contradictory
terminal sources remain `INTEGRITY_FAILURE`.

For exact authoritative:

```text
ProtocolV8SemanticValidationResultV1 R

R.execution == E
R.qlek == K
R.classification == "protocol-invalid"
```

produce:

```text
kind =
"protocol-invalid-no-candidate"

evidence =
orderedUnique([
  introducingMutationArtifact(R),
  ...R.validationEvidence
])
```

The introducing mutation is the exact retained
`AdmitProtocolV8SemanticValidationV1` artifact.

For exact authoritative protocol-valid result `R` for `E`, require:

```text
matching exact SemanticAdmissionRecordV1 A

A.qlek == K
A.admissionId == R.semanticAdmissionId

and

one exact lawful SemanticAdmissionWitnessRefV1 W where:

W.qlek == K
W.admissionId == A.admissionId
W.sourceDomainId == D
W.originExecutionId == E.executionId
W.witness == R.originWitness
```

Then produce:

```text
kind =
"admission-reconciled"

evidence =
orderedUnique([
  introducingMutationArtifact(R),
  R.originWitness,
  R.executionReceipt,
  R.semanticQuestionBinding,
  R.semanticCandidate,
  ...R.validationEvidence
])
```

Do not use candidate currentness. Do not use receipt ownership.

Never derive local clearance from:

```text
timeout
process death
MAYBE-SENT
missing response
unknown
UNRESOLVABLE
operator acknowledgement
progression supersession
candidate staleness
run termination
absence of Admission
```

### 23.4 Local uniqueness and exact export union

For one exact:

```text
(D, E.executionId, K)
```

derive zero or exactly one local clearance kind. Two incompatible local
clearance kinds for the same exact semantic Execution are
`INTEGRITY_FAILURE`; never merge them or select a winner.

For every `SemanticHistoryExportV1`, set:

```text
hazardClearances =
canonical duplicate-free union of:

A.
every exact locally derived clearance from sections 23.1 through 23.3

plus

B.
every already-retained imported ExternalSemanticHazardClearanceRefV1
from semantic_external_hazard_clearances
```

For each imported clearance preserve exactly:

```text
sourceDomainId
sourceExecution
qlek
kind
evidence
```

Never rewrite an imported `sourceDomainId` to the local domain ID.

### 23.5 Export monotonicity and artifact closure

Require:

```text
if a local Armed semantic Execution E was ever exported as an unresolved hazard

and exact later local authority clears E

then every later complete export MUST include the exact local clearance for E
```

Therefore both arrival orders are safe:

```text
older hazard export
→ newer clearance export

and

newer clearance export
→ older hazard export
```

In either order, destination reconstruction must eventually satisfy:

```text
matching clearance exists
→ imported hazard is not unresolved
```

An older export must not resurrect a positively cleared hazard.

For every exported clearance, require:

```text
every exact ArtifactRef in clearance.evidence
MUST appear in SemanticHistoryExportV1.artifactClosure
```

Apply the existing canonical `(sha256, artifactId)` ordering and duplicate
suppression. Do not otherwise redesign `artifactClosure`.

## 24. T5 external-history transaction realization

Consume only exact `ValidatedExternalSemanticHistoryRefV1` produced by future
M6 from an exact M2 export. M6 owns validation that the source export is
self-consistent, complete for its closed epoch, correctly bound to its source
domain, has lawful admission/witness closure, exact pending completions,
positively established clearances, never-Armed trajectories, intact artifacts,
and exact QLEK/admission/witness/Arm bindings. M2 does not reproduce those M6
semantic/protocol validations.

Implement the T5 coordination and transaction exactly:

```text
validate M0 representation
verify sourceHistory and validationEvidence intact
require sourceDomainId != local SemanticAuthorityDomainId

if exact (sourceDomainId, sourceHistory.sha256) already reconciled:
    return already-reconciled

if same sourceDomainId + same closedEpoch already recorded
with different sourceHistory.sha256:
    fail SEMANTIC-HISTORY-INTEGRITY-FAILURE

acquire domain gate non-blocking
if BUSY:
    return busy(domain)

BEGIN IMMEDIATE authoritative DB

compute union of every local semantic-history QLEK and every QLEK in H
order exact ascending
acquire each QLEK lock non-blocking in exact order

if any BUSY:
    release acquired QLEK locks
    ROLLBACK
    release domain gate
    return busy(qlek)

recheck source not already reconciled
recheck local current epoch unchanged
newEpoch = currentEpoch + 1
require safe integer

append clearances, unresolved hazards and audit-only unarmed trajectories
merge admissions and pending protocol-valid completions under T4 rules
derive and append every canonical conflict pair
append external-history reconciliation record
append semantic_coordination_epochs(
    newEpoch,
    reason = external-reconciliation,
    source_domain_id,
    source_history_sha256
)

COMMIT
release all QLEK locks
release domain gate
return reconciled(affectedQleks canonical sorted)
```

Change no GateARun `StateRevision`. Never copy an imported unarmed trajectory
into local executions or `semantic_execution_bindings`; it is audit provenance
only and never locally armable. After T5, future local work may create one fresh
local trajectory only when no admission, conflict, hazard, or pending completion
blocks K.

Store an exact clearance even if it arrives before an older hazard export. An
external hazard blocks iff its row exists and no matching clearance row exists;
out-of-order source exports cannot resurrect a positively cleared hazard.

## 25. Crash and capacity behavior

```text
T1 crash before grant commit
→ no durable grant; OS releases lock

T1 crash after grant commit
→ grant remains; later T1 issues newer generation

export/T5 crash before authoritative commit
→ no epoch change; orphan CAS export bytes allowed

export/T5 crash after authoritative commit
→ epoch and all export/merge facts remain atomic
→ every authority ref from the prior epoch is ineffective
```

No lock or counter wraps. Persist no live-lock state.

## 26. C9-B construction classifications

Record exactly these implementation-construction choices. None changes TURNLOCK
or hostile-review semantics.

### 26.1 Coherent domain

```text
statement:
one configured stateRoot and its single authoritative campaign-state.sqlite form
one coherent M2 Authoritative History domain for all GateARuns using that root;
a random immutable SemanticAuthorityDomainId identifies the physical domain for
cross-domain provenance but never enters QLEK

semantic disposition:
no-normative-impact

affected layer:
architecture-or-implementation

normative impact:
none
```

### 26.2 QLEK coordination

```text
statement:
M2 realizes live QLEK exclusion through one short-lived domain coordination
SQLite lock and one separately addressed per-QLEK SQLite lock while retaining all
semantic truth exclusively in the existing authoritative campaign-state.sqlite

semantic disposition:
no-normative-impact

affected layer:
architecture-or-implementation

normative impact:
none
```

### 26.3 Separate global semantic projection

```text
statement:
GateARunSnapshot remains run-local while M2 exposes SemanticQuestionStateV1 as a
separate derived global QLEK projection; T1/T4/T5 global semantic transitions do
not manufacture a GateARun StateRevision

semantic disposition:
no-normative-impact

affected layer:
architecture-or-implementation

normative impact:
none
```

### 26.4 Imported unarmed trajectory

```text
statement:
during T5, foreign unarmed semantic trajectories are retained as audit history
but none is imported as a locally armable Execution; later local work may create
one fresh local trajectory only after the reconciled semantic state permits it

semantic disposition:
no-normative-impact

affected layer:
architecture-or-implementation

normative impact:
none
```

### 26.5 Epoch closure on export/reconciliation

```text
statement:
semantic-history export and T5 each advance one domain-global coordination epoch
while holding the domain/authoritative/QLEK coordination barrier so every
pre-transition AdmissionAuthorityRef becomes ineffective without changing QLEK
identity

semantic disposition:
no-normative-impact

affected layer:
architecture-or-implementation

normative impact:
none
```

## 27. Protocol activation and dependency boundary

All protocol-v8 semantic operations remain inactive while
`formal/verification.yaml` selects P6. P6 remains current, P7 remains
permanently inactive, and P8 remains inactive. Administrative export/T5
interfaces do not make P8 current.

GREEN must consume active
`DC-SQLITE-NODE-GATE-A-CAMPAIGN-STATE` version `1.0.1` for the exact selected
package and external dependency behavior. The DC realizes, but does not redefine,
all schema-v2, coordination-database, dynamic per-QLEK connection,
crash-release, WAL-coexistence, deterministic multi-lock, non-blocking BUSY, and
no-lease requirements specified here.
