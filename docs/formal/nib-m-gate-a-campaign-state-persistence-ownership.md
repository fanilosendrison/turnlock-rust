---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-09-20"
step_id: 2
id: NIB-M-GATE-A-CAMPAIGN-STATE-PERSISTENCE-OWNERSHIP
version: "1.0.3"
scope: gate-a-campaign-runner/campaign-state/persistence-ownership
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Campaign State — Persistence and Ownership

## 1. Status, authority, and purpose

This document is one of three active Module Briefs that together close M2
`campaign-state` for the Gate A hostile-review campaign runner.

It consumes `NIB-S-GATE-A-CAMPAIGN-RUNNER` version `6.0.3`.

It is implementation-construction authority only. It does not define TURNLOCK
product semantics, canonical formal semantics, hostile-review protocol
semantics, formal-assurance claims, review evidence, or verification evidence.

This brief defines the physical persistence, immutable-artifact storage,
bootstrap, write-ownership, and fencing mechanics for M2 `campaign-state`.

Mutation semantics are defined by
`NIB-M-GATE-A-CAMPAIGN-STATE-MUTATION-EXECUTION`.

Snapshot reconstruction and retained-state integrity are defined by
`NIB-M-GATE-A-CAMPAIGN-STATE-SNAPSHOT-INTEGRITY`.

M2 uses SQLite as the transactional engine for Authoritative History.

The exact Node SQLite package/version/API is not selected by the coding agent.
GREEN is blocked until an accepted Dependency Contract named:

```text
DC-SQLITE-NODE-GATE-A-CAMPAIGN-STATE
```

defines the exact binding used by M2.

## 2. Inputs

The public cross-module requests are the exact NIB-S types:

```ts
CreateGateARunAndAcquireInitialOwnershipRequest
AcquireWriteOwnershipRequest
LoadGateARunSnapshotRequest
CommitAuthoritativeMutationRequest
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
database.

Artifact files under `artifacts/sha256/` are durable immutable bytes but are not
authoritative merely because they exist.

`ownership/*.sqlite` files contain no campaign semantics.

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
1
```

Unknown schema version is `INTEGRITY_FAILURE`.

No automatic migration exists in v1.

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

Before GREEN, `DC-SQLITE-NODE-GATE-A-CAMPAIGN-STATE` must define at minimum:

```text
exact package and version
supported Node versions
open/close semantics
BEGIN IMMEDIATE semantics
BUSY error identity
busy_timeout support
WAL support
synchronous=FULL behavior
transaction rollback behavior
process-crash recovery guarantees
prepared statements
foreign-key enforcement
error taxonomy
connection lifetime
ability to keep an ownership transaction open indefinitely
behavior on filesystem/I/O corruption
```

The implementation agent may not substitute a different SQLite package because
its API is more convenient.

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

* SQLite is the sole authoritative transaction engine in v1.
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
