---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "dependency-contract"
workspace: "turnlock-rust"
date: "2026-10-13"
step_id: 2
id: DC-SQLITE-NODE-GATE-A-CAMPAIGN-STATE
version: "1.0.0"
dependency_version: "13.0.3"
scope: gate-a-campaign-runner/campaign-state/sqlite-node
status: active
consumers: [architect, coding-agent]
referenced_by: [NIB-M-GATE-A-CAMPAIGN-STATE-PERSISTENCE-OWNERSHIP]
superseded_by: []
---

# Dependency Contract — Gate A SQLite/Node Campaign State

Contract ID: `DC-SQLITE-NODE-GATE-A-CAMPAIGN-STATE`

Version: `1.0.0`

Status: `active`

## 0. Identity, authority, and purpose

This Dependency Contract is implementation-construction dependency authority
for the M2 `campaign-state` persistence/ownership implementation only.

It is consumed by:

```text
NIB-M-GATE-A-CAMPAIGN-STATE-PERSISTENCE-OWNERSHIP 3.0.2
```

Other modules consume M2 APIs. They must not import `better-sqlite3` directly.

This contract selects exactly:

```text
runtime package:
better-sqlite3

runtime package version:
13.0.3

exact future package.json dependency:
"better-sqlite3": "13.0.3"

upstream repository:
WiseLibs/better-sqlite3

upstream release tag:
v13.0.3

tag target source commit:
dbc2ea1165fef1f599b9be12faea33fa5e9d7ffb

bundled SQLite version:
3.53.4

runtime floor:
Node.js >= 22.19.0
```

Use no version range. Forbid:

```text
^13.0.3
~13.0.3
>=13
latest
*
```

The selected package's engine floor is Node.js `>=22`. The TURNLOCK-selected
runtime floor remains Node.js `>=22.19.0`; this contract does not increase the
already selected Gate A runtime floor.

This contract creates no TURNLOCK, Gate A, hostile-review protocol, QLEK,
Admission, WorkItem, Execution, recovery, currentness, hazard, mutation-
admissibility, or evidence semantics.

## 1. Dependency ownership boundary

The dependency owns only:

```text
SQLite connection realization
SQLite statement execution
SQLite transaction realization
SQLite lock realization
SQLite error reporting
SQLite PRAGMA realization
```

It owns no:

```text
TURNLOCK semantics
Gate A semantics
QLEK semantics
Admission semantics
WorkItem semantics
Execution semantics
recovery classification
candidate currentness
semantic hazard classification
M2 mutation admissibility
```

M2 remains authority for state-root layout, schema version 2, tables, indexes,
foreign keys, append-only triggers, constraints, state semantics, artifact-store
relationships, lock topology and ordering, and semantic-history
export/reconciliation.

## 2. Runtime and build-only dependencies

The runtime dependency is exactly:

```json
{
  "dependencies": {
    "better-sqlite3": "13.0.3"
  }
}
```

Select exactly this compile-time TypeScript declaration support:

```text
@types/better-sqlite3@9.6.0
```

The future package manifest must declare:

```json
{
  "devDependencies": {
    "@types/better-sqlite3": "9.6.0"
  }
}
```

`@types/better-sqlite3`:

```text
is not runtime behavior
is not M2 authority
is not SQLite authority
is not campaign state
is not part of QLEK
is not evidence
```

Do not consume `@types/node` directly because of this contract. Its presence
remains the owning TypeScript/toolchain concern.

Do not create a package manifest merely to satisfy this contract. GREEN later
introduces the exact manifest under its separately authorized construction
stage.

## 3. Selected SQLite distribution

Consume exactly the stock bundled `better-sqlite3@13.0.3` distribution and its
bundled SQLite `3.53.4`.

Do not use:

```text
custom SQLite amalgamation
--sqlite3 custom source
SQLCipher
SQLite encryption extension
loadExtension
custom nativeBinding
forked better-sqlite3 package
system sqlite shared library substitution
```

Do not silently substitute another SQLite version because it is installed on
the host.

## 4. Allowed dependency interface

The M2 SQLite adapter may use only:

```text
new Database(path, options)

Database#exec(...)

Database#prepare(...)

Statement#run(...)

Statement#get(...)

Statement#all(...)

Database#pragma(...)

Database#close()

Database#inTransaction

Database#defaultSafeIntegers(true)

Database.SqliteError / SqliteError.code
```

Do not use another public `better-sqlite3` API without a later accepted
Dependency Contract revision.

Explicitly forbid:

```text
Database#transaction(...)
Database#backup(...)
Database#serialize(...)
Database#function(...)
Database#aggregate(...)
Database#table(...)
Database#loadExtension(...)
Database#unsafeMode(...)
worker-thread database transfer
custom native binding
```

## 5. Manual transaction interface

Use manually managed SQL for every M2 authoritative and lock transaction:

```text
BEGIN IMMEDIATE
COMMIT
ROLLBACK
```

Execute those fixed commands through:

```text
Database#exec(...)
```

Never use `Database#transaction(...)` and never mix its callback helper with
manually managed transactions.

M2 requires connection-scoped transactions whose lifetime is not scoped to one
synchronous callback, especially for long-lived GateARun and QLEK lock
ownership.

## 6. Connection profiles

Define exactly three profiles.

### 6.1 Authoritative database

For:

```text
<stateRoot>/authoritative/campaign-state.sqlite
```

open with:

```ts
new Database(path, {
  timeout: 5000,
})
```

Immediately execute:

```text
db.defaultSafeIntegers(true)

PRAGMA foreign_keys = ON
PRAGMA journal_mode = WAL
PRAGMA synchronous = FULL
PRAGMA busy_timeout = 5000
```

Verify exact effective values:

```text
foreign_keys == 1
journal_mode == "wal"
synchronous == 2
busy_timeout == 5000
```

Reject the connection and fail closed when these exact values cannot be
established.

### 6.2 GateARun ownership lock

For:

```text
<stateRoot>/ownership/<GateARunId>.sqlite
```

open with:

```ts
new Database(path, {
  timeout: 0,
})
```

Immediately execute:

```text
db.defaultSafeIntegers(true)

PRAGMA journal_mode = DELETE
PRAGMA synchronous = FULL
PRAGMA busy_timeout = 0
```

Verify exact effective values:

```text
journal_mode == "delete"
synchronous == 2
busy_timeout == 0
```

### 6.3 Semantic authority locks

For:

```text
<stateRoot>/semantic-authority/domain.sqlite
```

and:

```text
<stateRoot>/semantic-authority/qlek/<prefix>/<digest>.sqlite
```

use exactly the GateARun lock configuration:

```text
timeout = 0
journal_mode = DELETE
synchronous = FULL
busy_timeout = 0
defaultSafeIntegers(true)
```

Authoritative state alone uses WAL. Every lock database uses DELETE journal
mode.

## 7. Directory creation and database opening

`better-sqlite3` does not own state-root directory creation. Before opening a
database whose parent may not exist, M2/Node filesystem construction must create
the accepted directory layout.

A database-open failure caused by an absent parent directory is a
configuration/implementation failure, never campaign semantic state.

Use separate M2 operations for fresh creation and existing-state open.

### 7.1 Fresh authoritative-state creation

Only the exact M2 bootstrap path authorized to create a fresh state root may
open a missing file with:

```ts
new Database(path, {
  timeout: 5000,
})
```

It must construct exact schema version 2 before any normal campaign operation.

### 7.2 Existing authoritative-state open

Whenever M2 expects authoritative state already to exist, open with:

```ts
new Database(path, {
  timeout: 5000,
  fileMustExist: true,
})
```

Fail closed when the expected authoritative database is absent. Never create an
empty replacement authoritative database.

### 7.3 Lock database bootstrap

Run, QLEK, and domain lock files may be created when absent. Each contains
exactly one sentinel table and no campaign or semantic truth.

Finish sentinel-table creation before attempting the retained live
`BEGIN IMMEDIATE`. Do not create the sentinel while the transaction is already
intended to represent live ownership.

## 8. Lock acquisition and release

For a lock database configured with `timeout = 0` and `busy_timeout = 0`, execute:

```text
BEGIN IMMEDIATE
```

When it succeeds, the exact connection is the live lock handle. Keep that exact
`Database` object open. Do not clone or replace the connection and do not issue
`COMMIT`.

For explicit release:

```text
ROLLBACK
verify db.inTransaction == false
close connection
delete only the process-local handle
```

Do not delete the SQLite lock file. Do not mutate a durable state or semantic row
because a lock is released.

Holding `BEGIN IMMEDIATE` open across ordinary JavaScript orchestration time is
permitted only for:

```text
GateARun ownership lock DB
one exact QLEK AdmissionAuthority lock DB
```

These locks are intentionally isolated from the authoritative database. The
short-lived domain gate must never be held for an LLM/provider execution.

Never hold an authoritative `campaign-state.sqlite` transaction across:

```text
provider execution
awaiting operator input
network activity
LLM call
Git call
arbitrary orchestration delay
```

## 9. Lock contention semantics

For lock-database `BEGIN IMMEDIATE` only, exact:

```text
SqliteError.code == "SQLITE_BUSY"
```

maps to the owning M2 contention result:

```text
GateARun ownership DB
→ ACTIVE_OWNER_CONFLICT

domain/QLEK semantic coordination DB
→ exact T1/T4/T5/export busy branch selected by the owning M2 algorithm
```

Do not inspect error-message text. Do not sleep. Do not retry inside the SQLite
adapter. Do not convert another SQLite code into expected lock contention.

Any lock-acquisition error whose exact code is not `SQLITE_BUSY`, including a
different extended BUSY-family result, is not ordinary ownership contention.
Fail closed through the implementation/dependency failure boundary. A later DC
may widen this only with explicit evidence.

## 10. Authoritative database contention

The authoritative database uses:

```text
timeout = 5000
busy_timeout = 5000
```

Allow only SQLite/`better-sqlite3` configured lock waiting. Do not add an
application retry loop around:

```text
BEGIN IMMEDIATE
COMMIT
statement execution
```

If authoritative access ultimately throws exact `SQLITE_BUSY` after the
configured wait, fail the current operation as transient SQLite infrastructure
contention.

It must not become:

```text
STALE_STATE
ownership-lost
ACTIVE_OWNER_CONFLICT
SemanticAdmissionConflict
QLEK busy
OperationalBlocker
SemanticBlocker
```

No database contention creates an M2 semantic mutation.

## 11. Manual commit and rollback lifecycle

For every manually managed authoritative transaction:

```text
BEGIN IMMEDIATE succeeds
→ db.inTransaction MUST be true
```

On normal success:

```text
COMMIT
→ db.inTransaction MUST be false
```

On any exception after successful `BEGIN IMMEDIATE` and before confirmed commit:

```text
if db.inTransaction == true:
    attempt ROLLBACK
```

Then fail the operation. Never continue using a transaction after SQLite may
have automatically rolled it back. Never assume that catching a SQLite error
means the transaction remains active.

If `COMMIT` throws, do not report the M2 transition as committed. Inspect only
`db.inTransaction` to decide whether rollback remains possible. Do not infer
commit success from earlier statements, CAS bytes, files, or a local in-memory
projection. Fail closed.

For normal short-lived connection close:

```text
if db.inTransaction:
    explicit ROLLBACK first

db.close()
```

If rollback itself fails, close/discard the connection when possible, fail the
operation, never reuse the connection as trusted state, and never report
success.

A close failure is implementation/infrastructure failure. For a GateARun/QLEK
lock, do not report successful explicit release until the process has actually
dropped/discarded the live connection handle. Process termination remains the
final OS lock-release boundary.

## 12. Process death and crash behavior

Rely on SQLite/OS lock ownership attached to the live database
connection/process. On process termination:

```text
the process-held connection disappears
SQLite/OS releases the lock
no heartbeat or lease expiry is required
```

Committed durable rows remain authoritative. An uncommitted transaction is not
committed authority.

Do not create:

```text
PID authority
heartbeat ownership
lease timestamps
lock expiry
stale-lock-file cleanup semantics
```

## 13. Connection multiplicity and ownership

M2 may retain multiple independent open `better-sqlite3.Database` instances for
distinct GateARun ownership locks and QLEK locks. There is no application-global
singleton SQLite connection.

Resource exhaustion while opening a required connection is
implementation/infrastructure failure. It must not:

```text
drop an existing lock
reuse another QLEK's connection
merge two lock identities
fall back to an in-memory lock
```

One `Database` instance is owned by exactly one M2 local connection handle. Do
not share a live connection object across unrelated M2 ownership handles,
QLEKs, worker threads, or processes. Cross-process coordination occurs through
SQLite file locking, not shared JavaScript objects.

## 14. WAL and durability behavior

Only `authoritative/campaign-state.sqlite` uses WAL. Lock databases use DELETE
journal mode.

WAL supports accepted authoritative read/write concurrency. WAL files are not
independently authoritative. Do not parse, copy as evidence, derive state from,
or manually delete `-wal` files.

Every authoritative and lock database explicitly selects:

```text
PRAGMA synchronous = FULL
```

Do not rely on package compile/default WAL synchronous settings. Verify the
effective value is exactly `2`; otherwise fail closed.

## 15. Foreign keys and integrity probes

Every authoritative connection explicitly executes and verifies:

```text
PRAGMA foreign_keys = ON

effective value:
1
```

Do not rely solely on bundled SQLite compile defaults. Lock databases contain no
cross-table campaign semantics and need no foreign-key domain model.

For authoritative integrity checks use:

```text
PRAGMA quick_check
```

and require exact successful first value:

```text
ok
```

Use:

```text
PRAGMA foreign_key_check
```

and require zero returned violation rows.

Any other result is `INTEGRITY_FAILURE`. Do not attempt automatic SQLite repair.

## 16. Prepared statements and deterministic rows

Bind every data-bearing SQL value through:

```text
Database#prepare(...)
Statement#run(...)
Statement#get(...)
Statement#all(...)
```

Do not interpolate:

```text
GateARunId
QLEK
ArtifactRef values
SHA
session ID
candidate ID
execution ID
semantic IDs
state revision values
```

DDL, fixed PRAGMAs, and fixed transaction commands may use constant SQL text.
Dynamic table names are forbidden in the current M2 schema.

Do not retain an active iterator/cursor across `COMMIT`, `ROLLBACK`, connection
release, or lock release. Use `get`, `all`, and `run` for current M2 access
patterns. Do not use streaming iteration unless a later DC explicitly requires
it.

SQL result order is authoritative only when the query includes the exact
accepted deterministic `ORDER BY`. Never depend on insertion order without
`ORDER BY`, accidental rowid order, B-tree traversal, or query-plan order.

## 17. Integer representation

Immediately after opening every selected SQLite connection call:

```text
db.defaultSafeIntegers(true)
```

SQLite INTEGER reads are therefore JavaScript `bigint` values at the dependency
boundary. Never globally disable this behavior.

### 17.1 StateRevision

SQLite stores internal `revision_integer` as INTEGER. Read it as `bigint` and
expose `StateRevision` as the exact non-negative canonical base-10 decimal
string.

```text
0n → "0"
1n → "1"
42n → "42"
```

Never convert revision INTEGER to JavaScript `number` first. Do not introduce a
hidden `Number.MAX_SAFE_INTEGER` cap on `StateRevision`.

### 17.2 Safe-number counters

For:

```text
OwnershipGeneration
SemanticCoordinationEpoch
AdmissionAuthorityGeneration
attemptOrdinal
other contract fields explicitly represented as safe-integer number
```

read INTEGER as `bigint`. Before conversion to JavaScript `number`, require:

```text
value >= contract minimum
AND
value <= BigInt(Number.MAX_SAFE_INTEGER)
```

Then convert exactly. Overflow fails closed. Never permit rounded conversion.

### 17.3 Integer writes

For INTEGER fields already represented as `bigint`, bind the bigint directly.

For safe-integer cross-module numbers:

```text
validate Number.isSafeInteger
convert to BigInt
bind BigInt
```

For `StateRevision`:

```text
validate canonical decimal string
parse exactly to BigInt
bind BigInt
```

Never bind an unsafe JavaScript number to an authoritative INTEGER column.

### 17.4 Boolean and null values

Encode persisted booleans only as `0` or `1` and decode only:

```text
0 → false
1 → true
```

Any other retained integer is integrity failure. Preserve SQL `NULL` only for
exact nullable fields. Do not use truthiness conversion.

## 18. Text and artifact bytes

SQLite TEXT consumed by M2 is logical UTF-8 text. Do not normalize Unicode,
trim identifiers, or case-fold. Opaque IDs retain their exact accepted string
bytes after M0 validation.

Do not invent BLOB persistence for objects already stored as ArtifactRef
SHA/reference, normalized columns, or canonical text. Immutable content bytes
remain in `CampaignArtifactStore`. SQLite is authoritative relational history,
not a second artifact CAS.

## 19. Error detection and taxonomy

Detect dependency-originated SQLite errors structurally through:

```text
error instanceof Database.SqliteError
```

Inspect only:

```text
error.code
```

Do not parse `error.message`, stack traces, or localized OS text to determine
semantics. Non-`SqliteError` package/adapter exceptions are
implementation/dependency failures.

Treat these exact code families as integrity/storage failures while reading or
committing trusted authoritative state:

```text
SQLITE_CORRUPT*
SQLITE_NOTADB*
SQLITE_FORMAT*
SQLITE_SCHEMA*
SQLITE_CONSTRAINT*
SQLITE_MISMATCH*
```

Treat these as infrastructure/resource/I/O failures:

```text
SQLITE_IOERR*
SQLITE_FULL*
SQLITE_NOMEM*
SQLITE_CANTOPEN*
SQLITE_READONLY*
```

Treat `SQLITE_LOCKED*` outside an explicitly accepted lock-contention case as
implementation/dependency misuse or infrastructure failure. Never convert these
errors into campaign semantic blockers.

M2 validates mutation admissibility before SQL append. A
`SQLITE_CONSTRAINT*` failure during an accepted authoritative insert therefore
means implementation error or retained-state integrity contradiction. It is not
a normal `INVALID_MUTATION` escape hatch and never substitutes for M2 admission
validation.

## 20. Read and write transaction constraints

When M2 requires one exact SQLite read snapshot, use one connection and one
explicit read transaction on that connection. Do not assemble one logical
snapshot from independently timed connections. End the read transaction when
the read operation completes.

Every accepted M2 authoritative transition uses `BEGIN IMMEDIATE` on the
authoritative database. Do not substitute:

```text
BEGIN DEFERRED
BEGIN EXCLUSIVE
implicit auto-commit transaction
```

Every live run/QLEK/domain lock acquisition uses `BEGIN IMMEDIATE` on its exact
lock database. Do not substitute filesystem lockfile existence, `mkdir`
locking, `flock`, PID files, leases, heartbeats, or an in-memory mutex as
cross-process authority. An in-process map may retain handles but is not lock
authority.

The dependency contract does not choose multi-lock order. M2 owns:

```text
domain gate
→ authoritative DB where specified
→ QLEKs in canonical ASCII order where specified
```

The dependency exposes non-blocking `BEGIN IMMEDIATE` acquisition only. Add no
package-level retry or reordering.

## 21. Files, schema, and migration ownership

Never automatically delete an authoritative database. Never delete an
ownership/domain/QLEK lock database because no connection currently holds it.
Old lock files are harmless coordination containers. Cleanup policy is outside
this contract.

M2 owns schema SQL, schema version 2, tables, indexes, foreign keys, append-only
triggers, and constraints. `better-sqlite3` owns none of their meaning. This
contract must not redefine M2 schema semantics.

The dependency performs no migration. For authoritative state:

```text
schema mismatch
→ M2 INTEGRITY_FAILURE
```

Introduce no package migration library.

## 22. Extension and security boundary

Require:

```text
no loadExtension
no custom SQL extension
no user-defined SQLite function
no aggregate registration
no virtual-table registration
no unsafeMode
```

Consume ordinary stock SQLite only.

Do not enable `better-sqlite3` `verbose` SQL logging in normal runtime. SQL logs
are not campaign evidence, and bound operational material must not become
accidental durable logs. Any future diagnostics require an accepted
observability boundary.

## 23. Retry and lifecycle failures

`better-sqlite3` performs no campaign retry. The only accepted waiting is:

```text
authoritative busy_timeout = 5000 ms
```

Every lock database uses:

```text
busy_timeout = 0
```

Do not add `setTimeout` retry, exponential backoff, or loop-until-lock behavior.

Failure to open a DB, establish/verify a PRAGMA, prepare a fixed statement,
execute a statement, commit, rollback, or close is surfaced to the owning M2
operation.

Do not silently reopen another database, switch to memory, switch journal mode,
lower durability, disable foreign keys, or retry through another package.

## 24. No authority from dependency timing

Never infer semantic truth from:

```text
how long BEGIN IMMEDIATE waited
how quickly SQLITE_BUSY occurred
WAL checkpoint timing
file modification times
SQLite rowid order
filesystem inode
database file size
```

Only accepted M2 history establishes authority.

## 25. External dependency qualification provenance

Record exactly:

```text
better-sqlite3 release:
v13.0.3

source commit:
dbc2ea1165fef1f599b9be12faea33fa5e9d7ffb

package engine:
Node.js >=22

TURNLOCK selected runtime floor:
Node.js >=22.19.0

bundled SQLite:
3.53.4

better-sqlite3 source package.json blob at tag:
3be238a5696295ac0e225209b118d0ad994b01b9

better-sqlite3 API documentation blob at tag:
073c4751801064ab2c6c04ebe419e512a612af07

better-sqlite3 compilation documentation blob at tag:
638d068248bcc55a10c32010e9ffbb0bbc63c99d
```

These facts are qualification provenance, not TURNLOCK runtime identities.

## 26. Known installation limitation

Record as construction/tooling limitation only:

```text
better-sqlite3 v13 uses a native Node-API addon.

Package installation/prebuilt availability belongs to build/tooling realization,
not campaign semantics.
```

Do not create a runtime fallback to another SQLite library if native loading
fails. Handle a future build/install issue as build/tooling work.

## 27. Future package-manifest exclusions

When GREEN later introduces package metadata, require exactly:

```json
{
  "dependencies": {
    "better-sqlite3": "13.0.3"
  },
  "devDependencies": {
    "@types/better-sqlite3": "9.6.0"
  }
}
```

Without an explicit accepted DC revision, forbid:

```text
sqlite3
sqlite
@vscode/sqlite3
node:sqlite substitution
sql.js
wa-sqlite
another better-sqlite3 fork
```

## 28. Required future contract tests

NIB-T/RED-GREEN construction must implement the following observable contract
tests. Do not implement them as part of this contract-authoring task.

### DC-SQLITE-01 — authoritative profile

Open the authoritative DB and verify:

```text
foreign_keys == 1
journal_mode == wal
synchronous == 2
busy_timeout == 5000
```

### DC-SQLITE-02 — lock profile

Open a lock DB and verify:

```text
journal_mode == delete
synchronous == 2
busy_timeout == 0
```

### DC-SQLITE-03 — non-blocking exclusion

With two connections to one lock DB:

```text
A BEGIN IMMEDIATE
→ success

B BEGIN IMMEDIATE
→ exact SqliteError.code == SQLITE_BUSY
```

Require no adapter retry.

### DC-SQLITE-04 — explicit release

```text
A BEGIN IMMEDIATE
B → SQLITE_BUSY

A ROLLBACK + close

new B BEGIN IMMEDIATE
→ success
```

### DC-SQLITE-05 — connection-death release

Use a separate child process:

```text
child opens lock
child BEGIN IMMEDIATE
parent observes SQLITE_BUSY
child is forcibly terminated
parent later obtains BEGIN IMMEDIATE
```

Assert no exact release latency.

### DC-SQLITE-06 — manual transaction persistence

For one lock connection:

```text
exec(BEGIN IMMEDIATE)
return from helper
perform ordinary JS control flow
db.inTransaction == true
second connection remains SQLITE_BUSY
```

This proves the transaction is not callback-scoped.

### DC-SQLITE-07 — authoritative atomic commit

```text
BEGIN IMMEDIATE
insert multiple rows
COMMIT
reopen
all rows present
```

### DC-SQLITE-08 — authoritative rollback

```text
BEGIN IMMEDIATE
insert
ROLLBACK
reopen
insert absent
```

### DC-SQLITE-09 — crash rollback

In a child process:

```text
BEGIN IMMEDIATE
insert uncommitted row
signal parent
forced process termination
```

On reopen require:

```text
uncommitted row absent
database passes quick_check
```

### DC-SQLITE-10 — integer exactness

Store and read:

```text
0
1
Number.MAX_SAFE_INTEGER
Number.MAX_SAFE_INTEGER + 1 represented as bigint
SQLite signed 64-bit-safe fixture
```

Require dependency values to be `bigint`, safe-number conversion to reject
values above `MAX_SAFE_INTEGER`, and exact StateRevision decimal-string
conversion.

### DC-SQLITE-11 — foreign-key enforcement

Attempt an invalid foreign-key insert inside an authoritative transaction.
Require SQLite constraint failure and no successful M2 commit.

### DC-SQLITE-12 — append-only trigger

Attempt UPDATE and DELETE against one authoritative append-only table. Require
exact SQLite constraint/trigger failure.

### DC-SQLITE-13 — read snapshot

Connection A begins an exact read transaction. Connection B commits a later
authoritative change. Require A to retain its original snapshot until its
transaction ends and a later A/new connection to see the committed change.

### DC-SQLITE-14 — WAL readers

With authoritative WAL configured, keep a writer transaction active and require
existing committed state to remain readable from an independent reader. Never
assert that the reader observes uncommitted state.

### DC-SQLITE-15 — missing expected DB

Open an absent expected authoritative DB with:

```text
fileMustExist = true
```

Require failure and no empty database creation.

### DC-SQLITE-16 — error taxonomy

Prove expected lock conflict is identified from `SqliteError.code`, never
message text.

## 29. Dependency invariants

```text
DC-SQLITE-01
Only better-sqlite3@13.0.3 realizes M2 SQLite.

DC-SQLITE-02
TURNLOCK runtime floor remains Node.js >=22.19.0.

DC-SQLITE-03
The selected bundled SQLite is 3.53.4.

DC-SQLITE-04
Authoritative state uses WAL + FULL + FK ON + busy_timeout 5000.

DC-SQLITE-05
Run/QLEK/domain locks use DELETE + FULL + busy_timeout 0.

DC-SQLITE-06
All M2 write/lock transactions use manual BEGIN IMMEDIATE.

DC-SQLITE-07
Database#transaction() is not used.

DC-SQLITE-08
Expected lock contention is classified by exact SqliteError.code, never message.

DC-SQLITE-09
A lock is the retained live connection/transaction, not lock-file existence.

DC-SQLITE-10
Process termination releases process-held SQLite locks without lease semantics.

DC-SQLITE-11
Authoritative DB transactions are never kept open across external effects.

DC-SQLITE-12
SQLite INTEGER reads use bigint at the dependency boundary.

DC-SQLITE-13
StateRevision never round-trips through JavaScript number.

DC-SQLITE-14
Safe-number fields reject bigint overflow before number conversion.

DC-SQLITE-15
M2 validates semantics before relying on SQL constraints.

DC-SQLITE-16
No SQLite error manufactures campaign semantic authority.

DC-SQLITE-17
No mutable SQLite/WAL filesystem artifact is independently semantic authority.

DC-SQLITE-18
Row order is deterministic only through explicit ORDER BY.

DC-SQLITE-19
No custom SQLite build/extension is consumed.

DC-SQLITE-20
No sibling module imports better-sqlite3 directly.

DC-SQLITE-21
@types/better-sqlite3 is compile-time only.

DC-SQLITE-22
Failure to satisfy required PRAGMA values is fail closed.

DC-SQLITE-23
Missing expected authoritative DB never creates an empty replacement.

DC-SQLITE-24
No application retry loop hides SQLite lock/contention outcomes.

DC-SQLITE-25
SQLite schema version remains owned by M2, currently version 2.
```

## 30. Construction classifications

### 30.1 Selected synchronous SQLite realization

```text
statement:
M2 schema-v2 requires a synchronous Node SQLite realization that supports
explicit BEGIN IMMEDIATE transactions whose connection can remain open as a
long-lived OS-backed ownership/fencing handle; better-sqlite3@13.0.3 is selected
as the exact dependency realization, with bundled SQLite 3.53.4 and
Node.js >=22.19.0 runtime floor

semantic disposition:
no-normative-impact

affected layer:
architecture-or-implementation

normative impact:
none
```

### 30.2 Manual transaction realization

```text
statement:
M2 uses manually managed better-sqlite3 transactions rather than the
Database#transaction callback helper because accepted run/QLEK ownership
requires connection-scoped transactions that outlive one callback invocation

semantic disposition:
derived-from-existing-authority

affected layer:
architecture-or-implementation

normative impact:
none
```

### 30.3 Exact integer boundary

```text
statement:
all SQLite INTEGER values are read as bigint at the dependency boundary, with
explicit checked projection into safe-number cross-module counters or exact
decimal-string StateRevision, preventing hidden JavaScript integer rounding

semantic disposition:
derived-from-existing-authority

affected layer:
architecture-or-implementation

normative impact:
none
```

### 30.4 Build-only TypeScript declarations

```text
statement:
@types/better-sqlite3@9.6.0 is selected only as compile-time declaration support
because the selected runtime package does not expose the required TypeScript
declaration surface as runtime authority

semantic disposition:
no-normative-impact

affected layer:
architecture-or-implementation

normative impact:
none
```

No classification in this section creates product/protocol semantics or requires
an ADR.

## 31. GREEN boundary

This contract closes the external SQLite/Node dependency behavior required by
M2 persistence/ownership. GREEN remains subject to the accepted construction
sequence, future NIB-T tests, implementation, and repository validation.

Do not interpret contract publication as implementation, package-manifest
creation, protocol activation, formal evidence, or campaign authority.
