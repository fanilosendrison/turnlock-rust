---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-03"
step_id: 2
id: NIB-M-GATE-A-COGNITIVE-EXECUTION-RECOVERY-OBSERVATION
version: "1.0.2"
scope: gate-a-campaign-runner/cognitive-execution/recovery-observation
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Cognitive Execution — Recovery Observation

This brief consumes exactly:

```text
NIB-S-GATE-A-CAMPAIGN-RUNNER 9.1.2

NIB-M-GATE-A-COGNITIVE-EXECUTION-CAPTURE 1.1.3

DC-PI-M4-GATE-A-COGNITIVE-EXECUTION 1.1.3

NIB-M-GATE-A-RECOVERY-OPERATOR-RECONCILIATION 2.0.11

NIB-M-GATE-A-RECOVERY-OPERATOR-BOUNDARY 2.0.11
```

Version `1.0.2` is a dependency-only / construction-only compatibility
synchronization. It makes no execution algorithm change, no provider change, no
retry semantic change, no hard-limit change, no recovery change, and no
repository semantic change.

Version `1.0.1` was a dependency-only / construction-only compatibility
synchronization. It changed no algorithm, type, provider, recovery, or
repository semantics.

## 1. Responsibility boundary

M4 remains one system module:

```text
M4 cognitive-execution
├── M4-A execution/capture
└── M4-B recovery observation
```

M4-B owns only:

```text
validation of cognitive recovery descriptors
validation of exact M4 recovery capability
read-only interpretation of the M4 journal
construction/sealing of cognitive non-execution proof
local terminal reconstruction
construction/sealing of cognitive recovery indeterminacy
ExecutionRecoveryPort.reconcile(...)
```

M4-B does NOT own:

```text
provider invocation
provider replay
provider lookup
protocol retry
M8 classification
M2 authoritative mutation
OperationalBlocker
Operator Action Request
reviewer qualification
provider identity reinterpretation
ADR-054 semantics
```

## 2. Construction dependencies

M4-B consumes exactly:

```ts
interface CognitiveExecutionRecoveryObservationDependencies {
  readonly artifactStore:
    CampaignArtifactStore;

  readonly runtimeConfig:
    CognitiveExecutionRuntimeConfig;

  readonly callLocks:
    CognitiveExecutionCallLockRegistry;
}

interface CognitiveExecutionCallLockRegistry {
  withExclusive<T>(
    callId: CognitiveCallId,
    operation: () => Promise<T>,
  ): Promise<T>;
}
```

M1 process composition supplies M4-A and M4-B:

```text
the same resolved CognitiveExecutionRuntimeConfig
the same CognitiveExecutionCallLockRegistry instance
```

M4-B uses:

```text
runtimeConfig.journalRoot
```

and ignores `heartbeatIntervalMs`.

M4-B does not import:

```text
@earendil-works/pi-ai
provider SDK
Git
SQLite
M2 persistence internals
```

## 3. Ownership-handoff and concurrency requirement

Within one process:

```text
M4-A execute()
and
M4-B reconcile()
for the same callId

must both use the same callLocks.withExclusive(...)
```

M4-B reads journal truth only while holding that lock.

Cross-session recovery occurs only after M1 has successfully acquired current
M2 write ownership and entered the recovery barrier.

Future M1 construction MUST preserve this ordering:

```text
before intentionally releasing/closing one live session's M2 ownership handle:

abort every live execution-owned M4 AbortController
await every live M4-A execute invocation to settle
only then release/close session ownership resources
```

A process crash inherently terminates its process-local M4 writer before another
process can resume.

This rule introduces no execution truth.

It only ensures no prior same-session M4-A invocation may later create
MAYBE-SENT after a new recovery observer has legitimately established a
PREPARED-only state.

## 4. Public boundary

M4-B implements exactly:

```ts
interface ExecutionRecoveryPort {
  reconcile(
    unresolved: UnresolvedExecutionRecoveryRef
  ): Promise<ExecutionRecoveryObservation>;
}
```

No second public M4-B API.

## 5. Canonical M4-B JSON

Every M4-B-owned JSON artifact uses exact existing M4 canonical JSON:

```text
UTF-8
recursive lexicographic object keys
semantic array order preserved
all required fields emitted
undefined rejected
bigint rejected
NaN/infinity rejected
compact
no trailing newline
mediaType = application/json
repositoryPath = null
```

Seal only through:

```text
CampaignArtifactStore.sealRunnerArtifact
```

## 6. Incoming descriptor validation

For unresolved descriptor `U`, require before journal interpretation:

```text
U.workItem.executor == "cognitive-execution"

U.execution.workItemId ==
U.workItem.workItemId

U.terminalOutcome == null

U.dispatchState ==
"POSSIBLY-DISPATCHED"

U.recoveryCapability != null

U.recoveryCapability.executor ==
"cognitive-execution"

U.recoveryCapability.executor ==
U.workItem.executor
```

Verify:

```text
U.dispatchIntent
every U.dispatchEvidence ArtifactRef
U.workItem.operation
U.recoveryCapability.reconciliationOperation
```

Any failure is invocation/integrity failure, never recovery observation.

## 7. Reconciliation-operation validation

Decode exact:

```ts
CognitiveReconciliationOperationV1
```

from:

```text
U.recoveryCapability.reconciliationOperation
```

Call it `R`.

Require:

```text
R.execution == U.execution

R.workItemId ==
U.workItem.workItemId

R.callId ==
deriveId(
  "m4-cognitive-call.v1",
  U.execution.executionId
)

R.journalKey ==
lowercaseHex(
  SHA256(
    UTF8(R.callId)
  )
)
```

Verify and decode `R.preparation`.

Call preparation `P`.

Require:

```text
P.execution == U.execution

P.workItemId ==
U.workItem.workItemId

P.operation ==
U.workItem.operation

P.callId ==
R.callId
```

Verify:

```text
P.operation
P.dependencyExecutionPlan
```

Decode dependency plan and require:

```text
contractId ==
"DC-PI-M4-GATE-A-COGNITIVE-EXECUTION"

contractVersion ==
"1.1.3"

callId ==
R.callId
```

Any unsupported/mismatched DC version is:

```text
RECOVERY-CONTRACT-VIOLATION
```

M4-B never dynamically guesses recovery behavior from another DC version.

## 8. Arm evidence prefix

Require:

```text
U.dispatchEvidence.length >= 2
```

and exact prefix:

```text
U.dispatchEvidence[0] ==
R.preparation

U.dispatchEvidence[1] ==
U.recoveryCapability.reconciliationOperation
```

Any later entries are immutable same-execution uncertainty evidence and are
preserved exactly.

## 9. Journal location

Use exactly:

```text
journalRoot =
runtimeConfig.journalRoot

journalDir =
journalRoot + "/calls/" + R.journalKey
```

Truth-bearing names are exactly:

```text
prepared.json
maybe-sent.json
terminal.json
```

Telemetry is never read for recovery truth.

Ignore:

```text
heartbeat.json
provider-activity.json
temporary orphan files
unreferenced CAS artifacts
```

## 10. Journal observation ordering

After all immutable descriptor/capability validation:

```text
acquire exact M4 call lock for R.callId
```

While holding lock:

```text
1. read/validate prepared.json

2. inspect maybe-sent.json

3. inspect terminal.json

4. validate complete state

5. construct/seal any M4-B proof artifact

6. construct exact observation

7. release lock only after the observation's immutable support material has
   been sealed successfully
```

For optional marker lookup:

```text
ENOENT
→ marker absent

other filesystem failure
→ JOURNAL-IO-FAILURE
```

`prepared.json` is mandatory.

Missing PREPARED is:

```text
JOURNAL-INTEGRITY-FAILURE
```

## 11. Prepared-marker validation

Decode exact `CognitiveExecutionPreparedMarkerV1 M`.

Require:

```text
M.executionId ==
U.execution.executionId

M.workItemId ==
U.workItem.workItemId

M.callId ==
R.callId

M.preparation ==
R.preparation

M.reconciliationOperation ==
U.recoveryCapability.reconciliationOperation
```

Malformed or contradictory marker:

```text
JOURNAL-INTEGRITY-FAILURE
```

## 12. MAYBE-SENT validation

If `maybe-sent.json` exists, decode exact
`CognitiveExecutionMaybeSentMarkerV1 S`.

Require:

```text
S.executionId ==
U.execution.executionId

S.workItemId ==
U.workItem.workItemId

S.callId ==
R.callId
```

Verify and decode:

```text
S.callStartEvidence
```

as exact `CognitiveCallStartEvidenceV1 C`.

Require:

```text
C.execution ==
U.execution

C.workItemId ==
U.workItem.workItemId

C.callId ==
R.callId

C.dispatchIntent ==
U.dispatchIntent

C.preparation ==
R.preparation
```

Any contradiction:

```text
JOURNAL-INTEGRITY-FAILURE
```

## 13. TERMINAL validation

If `terminal.json` exists:

```text
maybe-sent.json MUST exist
```

Otherwise:

```text
JOURNAL-INTEGRITY-FAILURE
```

Decode exact `CognitiveExecutionTerminalMarkerV1 T`.

Require:

```text
T.executionId ==
U.execution.executionId

T.workItemId ==
U.workItem.workItemId

T.callId ==
R.callId
```

Verify/decode `T.terminalEvidence`.

It must be exactly one of:

```text
CognitiveCompletedResponseEvidenceV1
CognitiveTechnicalFailureEvidenceV1
```

For either exact terminal evidence `E`, require:

```text
E.execution ==
U.execution

E.workItemId ==
U.workItem.workItemId

E.callId ==
R.callId

E.dispatchIntent ==
U.dispatchIntent

E.preparation ==
R.preparation

E.callStartEvidence ==
S.callStartEvidence
```

Verify every ArtifactRef referenced by E.

Any failure:

```text
JOURNAL-INTEGRITY-FAILURE
```

## 14. Exact journal-state decision table

After validation, exactly one branch is legal:

```text
PREPARED present
MAYBE-SENT absent
TERMINAL absent
→ NOT-EXECUTED branch

PREPARED present
MAYBE-SENT present
TERMINAL absent
→ UNKNOWN branch

PREPARED present
MAYBE-SENT present
TERMINAL present
→ TERMINAL branch
```

Any other state:

```text
JOURNAL-INTEGRITY-FAILURE
```

## 15. Non-execution proof artifact

Define exactly:

```ts
interface CognitiveExecutionNonExecutionProofV1 {
  readonly schema:
    "gate-a-cognitive-execution-non-execution-proof.v1";

  readonly execution:
    ExecutionRef;

  readonly workItemId:
    WorkItemId;

  readonly callId:
    CognitiveCallId;

  readonly dispatchIntent:
    ArtifactRef;

  readonly recoveryCapability:
    RecoveryCapabilityRef;

  readonly preparation:
    ArtifactRef;

  readonly reconciliationOperation:
    ArtifactRef;

  readonly journalKey:
    string;

  readonly preparedMarker:
    CognitiveExecutionPreparedMarkerV1;

  readonly observedJournalState:
    "prepared-without-maybe-sent-or-terminal";

  readonly effectBoundary:
    "durable-maybe-sent-required-before-cognitive-call-reachable.v1";
}
```

No:

```text
timestamp
session id
ownership generation
PID
heartbeat
provider fact
```

This proof means:

```text
the exact valid PREPARED state exists

AND

while M4-B holds the shared M4 call lock, no MAYBE-SENT or TERMINAL marker
exists

AND

M4-A construction guarantees the cognitive call is unreachable before durable
MAYBE-SENT

THEREFORE

the exact cognitive-call effect boundary was not crossed
```

It is NOT merely:

```text
file missing → not executed
```

## 16. NonExecutionProofRef construction

Seal exact `CognitiveExecutionNonExecutionProofV1` as `proofRef`.

Construct:

```ts
NonExecutionProofRef {
  schema:
    "gate-a-non-execution-proof.v1",

  execution:
    U.execution,

  workItemId:
    U.workItem.workItemId,

  executor:
    "cognitive-execution",

  dispatchIntent:
    U.dispatchIntent,

  recoveryCapability:
    U.recoveryCapability,

  proof:
    proofRef,

  basisArtifacts:
    orderedUnique([
      ...U.dispatchEvidence,
    ]),
}
```

Require:

```text
proofRef not present in basisArtifacts
basisArtifacts duplicate-free
```

Return exactly:

```ts
{
  kind: "not-executed",
  nonExecutionProof,
}
```

## 17. Terminal captured reconstruction

For terminal evidence:

```text
kind == completed-response
```

construct exactly:

```ts
CapturedExecutionResult {
  execution:
    U.execution,

  rawResult:
    E.rawResult,

  runtimeEvidence:
    orderedUnique([
      R.preparation,
      U.recoveryCapability.reconciliationOperation,
      E.callStartEvidence,
      T.terminalEvidence,
      E.dependencyRequestEvidence,
      ...E.dependencyRuntimeEvidence,
    ]),
}
```

This must equal the logical direct M4-A captured result for the same terminal
evidence.

Return:

```ts
{
  kind: "terminal",
  outcome: {
    kind: "captured",
    value: exactRecoveredCapturedResult,
  },
  evidence: [],
}
```

No new recovery artifact is sealed for terminal reconstruction.

## 18. Terminal technical-failure reconstruction

For terminal evidence:

```text
kind == technical-failure
```

construct exactly:

```ts
TechnicalExecutionFailure {
  execution:
    U.execution,

  completedResponse:
    false,

  failureEvidence:
    orderedUnique([
      R.preparation,
      U.recoveryCapability.reconciliationOperation,
      E.callStartEvidence,
      T.terminalEvidence,
      E.dependencyRequestEvidence,
      ...E.dependencyRuntimeEvidence,
      ...E.failureEvidence,
    ]),
}
```

Require:

```text
E.transportAttemptCount == 1
```

Return:

```ts
{
  kind: "terminal",
  outcome: {
    kind: "technical-failure",
    value: exactRecoveredTechnicalFailure,
  },
  evidence: [],
}
```

No new recovery artifact is sealed.

## 19. Recovery indeterminacy artifact

For:

```text
PREPARED
+
MAYBE-SENT
+
no TERMINAL
```

define exactly:

```ts
interface CognitiveExecutionRecoveryIndeterminacyV1 {
  readonly schema:
    "gate-a-cognitive-execution-recovery-indeterminacy.v1";

  readonly execution:
    ExecutionRef;

  readonly workItemId:
    WorkItemId;

  readonly callId:
    CognitiveCallId;

  readonly dispatchIntent:
    ArtifactRef;

  readonly recoveryCapability:
    RecoveryCapabilityRef;

  readonly preparation:
    ArtifactRef;

  readonly reconciliationOperation:
    ArtifactRef;

  readonly dependencyExecutionPlan:
    ArtifactRef;

  readonly journalKey:
    string;

  readonly preparedMarker:
    CognitiveExecutionPreparedMarkerV1;

  readonly maybeSentMarker:
    CognitiveExecutionMaybeSentMarkerV1;

  readonly reason:
    "maybe-sent-without-terminal-and-no-qualified-observational-provider-recovery";

  readonly dependencyContract: {
    readonly id:
      "DC-PI-M4-GATE-A-COGNITIVE-EXECUTION";

    readonly version:
      "1.1.3";
  };

  readonly providerRecoveryCapability: {
    readonly postCrashResponseLookup:
      "not-established";

    readonly providerResponseIdRecovery:
      "not-established";

    readonly safeReadOnlyPendingObservation:
      "not-established";

    readonly pending:
      "forbidden";

    readonly replay:
      "forbidden";
  };
}
```

This is positive executor-domain indeterminacy:

```text
MAYBE-SENT proves effect boundary may have become reachable

no valid TERMINAL means no local durable terminal truth exists

accepted DC 1.1.3 establishes no qualified read-only provider recovery mechanism

replay is forbidden

therefore M4's available recovery mechanism is exhausted for this exact
Execution
```

## 20. RecoveryIndeterminacyRef construction

Seal exact `CognitiveExecutionRecoveryIndeterminacyV1` as `indeterminacyRef`.

Construct:

```ts
RecoveryIndeterminacyRef {
  schema:
    "gate-a-recovery-indeterminacy.v1",

  execution:
    U.execution,

  workItemId:
    U.workItem.workItemId,

  executor:
    "cognitive-execution",

  dispatchIntent:
    U.dispatchIntent,

  recoveryCapability:
    U.recoveryCapability,

  indeterminacy:
    indeterminacyRef,

  basisArtifacts:
    orderedUnique([
      ...U.dispatchEvidence,
      S.callStartEvidence,
      P.dependencyExecutionPlan,
    ]),
}
```

Require:

```text
indeterminacyRef not present in basisArtifacts
basisArtifacts duplicate-free
```

Return exactly:

```ts
{
  kind: "unknown",
  indeterminacy,
}
```

## 21. Pending is unreachable

M4-B 1.0.2 MUST NEVER construct:

```text
ReconciliationContinuabilityRef
```

and MUST NEVER return:

```text
kind = "pending"
```

because DC 1.1.3 establishes:

```text
safe read-only provider pending observation = NOT-ESTABLISHED
pending = FORBIDDEN
provider-call replay = FORBIDDEN
```

A future accepted DC version that establishes a genuinely observational
recovery operation requires:

```text
new explicit M4-B Module Brief revision
```

M4-B must not dynamically infer pending capability.

## 22. Unreferenced material

These never advance recovery truth:

```text
unreferenced CAS terminal artifact
temporary journal files
telemetry files
provider activity telemetry
heartbeat
raw provider material not referenced by terminal.json
```

Only valid truth-bearing journal markers determine the local M4 recovery state.

## 23. Idempotence

Repeated `reconcile(U)` over unchanged valid durable material returns the same
logical observation.

Content-addressed proof/indeterminacy sealing therefore converges to the same
ArtifactRefs.

M4-B writes:

```text
no journal marker
no telemetry
no M2 state
```

It only seals immutable proof/indeterminacy artifacts when required.

## 24. Crash during M4-B

If process crashes before M4-B returns:

```text
no recovery observation became authoritative
```

Any proof/indeterminacy CAS artifact sealed but not consumed later is
non-authoritative garbage.

A later recovery occurrence re-reads journal truth from scratch.

M4-B stores no polling counter, cache, or mutable recovery state.

## 25. Failure taxonomy

Define exactly:

```ts
type CognitiveExecutionRecoveryObservationFailureCodeV1 =
  | "INVALID-UNRESOLVED-DESCRIPTOR"
  | "INVALID-RECOVERY-CAPABILITY"
  | "ARTIFACT-INTEGRITY-FAILURE"
  | "JOURNAL-INTEGRITY-FAILURE"
  | "JOURNAL-IO-FAILURE"
  | "ARTIFACT-SEAL-FAILURE"
  | "RECOVERY-CONTRACT-VIOLATION";
```

Map exactly:

```text
wrong executor / dispatch state / terminalOutcome presence / execution-workitem
binding
→ INVALID-UNRESOLVED-DESCRIPTOR

null/wrong recovery capability or malformed reconciliation operation binding
→ INVALID-RECOVERY-CAPABILITY

missing/corrupt immutable ArtifactRef bytes
→ ARTIFACT-INTEGRITY-FAILURE

missing mandatory PREPARED
invalid marker schema
contradictory marker identities
TERMINAL without MAYBE-SENT
terminal evidence contradicts marker/call/preparation
→ JOURNAL-INTEGRITY-FAILURE

unexpected filesystem read failure
→ JOURNAL-IO-FAILURE

proof/indeterminacy sealing failure
→ ARTIFACT-SEAL-FAILURE

dependency plan contract id/version not exactly supported by this M4-B
→ RECOVERY-CONTRACT-VIOLATION
```

Every such failure rejects `reconcile()`.

Never convert one into:

```text
not-executed
terminal
pending
unknown
```

## 26. M8 boundary

M4-B returns executor-domain observations only.

It never emits:

```text
PROVEN-NOT-EXECUTED
PROVEN-COMPLETED
UNRESOLVABLE
RECONCILABLE
OperationalBlocker
```

M8-A validates common envelopes and owns those classifications.

M2 alone admits them.

## 27. ADR-054 boundary

M4-B does not resolve or reinterpret provider identity.

Recovered terminal evidence preserves exactly the provider/model facts already
sealed by M4-A.

M4-B performs no:

```text
alias detection
canonical-model inference
provider_model synthesis
request-model fallback
identity-resolution qualification
```

## 28. Forbidden behavior

Explicitly forbid:

```text
provider call
Models.streamSimple
Pi import
credential resolution
provider lookup
provider response GET
provider pending query
request replay
resubmit
retry
new Execution
M2 mutation
M8 classification
wall-clock timeout classification
heartbeat truth
telemetry truth
negative lookup as nonexecution proof
missing terminal artifact as terminal failure
CAS artifact without journal reference as terminal truth
journal marker creation/update/deletion
```

## 29. Required invariants

```text
M4B-01
M4-B never creates or repeats the cognitive external effect.

M4B-02
M4-B validates one exact non-null cognitive RecoveryCapabilityRef before journal
interpretation.

M4B-03
M4-B uses the same process-local callId lock registry as M4-A.

M4B-04
PREPARED without MAYBE-SENT or TERMINAL is the only selected-v1 M4 local state
that may produce not-executed.

M4B-05
Not-executed is established by a sealed positive M4-owned proof, never by
absence alone.

M4B-06
TERMINAL-DURABLE reconstructs the exact logical direct M4-A terminal outcome.

M4B-07
Terminal recovery adds no new recovery-domain evidence artifact.

M4B-08
MAYBE-SENT without TERMINAL-DURABLE never proves execution, nonexecution, or
technical failure.

M4B-09
Under DC 1.1.3, MAYBE-SENT without terminal produces exact executor-domain
indeterminacy.

M4B-10
M4-B 1.0.2 never returns pending.

M4B-11
Unreferenced CAS material and telemetry never advance recovery truth.

M4B-12
M4-B never assigns M8 recovery classifications.

M4B-13
M4-B never writes M2 authoritative state.

M4B-14
M4-B never reinterprets ADR-054 provider identity semantics.

M4B-15
Repeated reconciliation over unchanged durable state is logically idempotent.
```
