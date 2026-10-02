---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-02"
step_id: 2
id: NIB-M-GATE-A-COGNITIVE-EXECUTION-CAPTURE
version: "1.0.0"
scope: gate-a-campaign-runner/cognitive-execution/execution-capture
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Cognitive Execution — Execution and Capture

It consumes `NIB-S-GATE-A-CAMPAIGN-RUNNER` version `8.0.1`.

## 1. Status, authority, and responsibility boundary

This document is implementation-construction authority only. It creates no
TURNLOCK product semantics, hostile-review semantics, canonical formal
semantics, review evidence, or verification evidence.

The system-level module remains exactly:

```text
M4 cognitive-execution
```

Its construction decomposition is:

```text
M4 cognitive-execution
├── M4-A execution / capture
└── M4-B recovery observation
```

This brief closes M4-A only.

M4-A owns:

```text
cognitive WorkItem operation schema and validation
pre-Arm M4 preparation
cognitive-call identity
credential-free dependency execution planning
pre-Arm credential availability classification
M4 recovery-capability preparation
durable M4 execution journal around the cognitive-call effect boundary
fresh isolated direct cognitive execution through the selected dependency
execution-owned abort propagation
provider/runtime evidence capture
exact textual completion sealing
known terminal no-completed-response technical-failure capture
execution uncertainty construction
best-effort liveness telemetry
M4-A invocation-failure taxonomy
```

M4-A does NOT own:

```text
M4-B recovery observation/classification facts
M8 recovery classification
M8 blocker identity/materialization
M2 authoritative state
M5 retry authorization or assurance adjudication
M6 protocol validation
qualified/protocol-invalid classification
reviewer-profile invention
protocol semantics
provider-reported resolved-identity versus alias resolution
Pi API facts beyond requirements placed on Dependency Contract #31
```

## 2. Construction dependencies and runtime configuration

M4-A consumes exactly:

```text
CampaignArtifactStore
Pi M4 Dependency Contract owned by Issue #31
Node.js standard filesystem/crypto/timer primitives
```

No other non-trivial dependency may be selected by this brief.

```ts
interface CognitiveExecutionRuntimeConfig {
  readonly journalRoot: string;
  readonly heartbeatIntervalMs: number;
}
```

`journalRoot` must be:

```text
absolute
durable across process restart
writable
outside every candidate repository/worktree
shared by all sessions that may resume the same GateARun
resolved once at process composition
```

M1 process composition owns validation that
`CognitiveExecutionRuntimeConfig.journalRoot` and
`CampaignStateRuntimeConfig.stateRoot` are disjoint.

M4-A validates its supplied `journalRoot` as an absolute, durable, writable
executor root outside every candidate repository or worktree. M4-A does not
receive or reinterpret M2 `stateRoot`.

`heartbeatIntervalMs` is a positive finite integer. It affects telemetry only.
It must not affect execution truth, timeout, abort, retry, recovery, ownership,
or classification.

There is no M4 execution-timeout configuration field.

## 3. Canonical M4 JSON

All runner-owned M4 JSON artifacts defined by this brief use exactly:

```text
UTF-8 JSON
object keys recursively lexicographically sorted
array order preserves semantic order
all required fields emitted
undefined rejected
bigint rejected
NaN rejected
+Infinity rejected
-Infinity rejected
compact encoding
no insignificant whitespace
no trailing newline
mediaType = application/json
```

M4-A seals them through `CampaignArtifactStore.sealRunnerArtifact`.

## 4. Cognitive WorkItem operation

```ts
interface CognitiveExecutionOperationV1 {
  readonly schema: "gate-a-cognitive-execution-operation.v1";
  readonly reviewContext: ReviewContext;
  readonly role: CognitiveExecutionRole;
  readonly reviewerProfileId: string;
  readonly prompt: ArtifactRef;
  readonly packet: ArtifactRef;
}
```

The operation is the complete immutable cognitive meaning of the WorkItem.
There is no separate `protocolBundle` field. The exact protocol identity is
already:

```text
operation.reviewContext.campaign.protocolBundle
```

M4 owns sealing and validation of this operation. Its artifact must have:

```text
mediaType = application/json
repositoryPath = null
```

through ordinary runner artifact-store semantics.

For every cognitive WorkItem accepted by M4-A, with decoded operation `O` and
WorkItem `W`, require exactly:

```text
W.executor == "cognitive-execution"

W.runId ==
    O.reviewContext.runId

W.candidateId ==
    O.reviewContext.candidate.candidateId

W.reviewCampaignId ==
    O.reviewContext.campaign.reviewCampaignId

O.reviewContext.candidate.runId ==
    W.runId

O.reviewContext.campaign.provenance.kind ==
    "runner-produced"

O.reviewContext.campaign.provenance.originatingRunId ==
    W.runId

O.reviewContext.campaign.provenance.candidateId ==
    W.candidateId

O.reviewContext.campaign.semanticSubject ==
    O.reviewContext.candidate.semanticSubject

W.inputRefs ==
[
    O.prompt,
    O.packet
]
```

The `inputRefs` equality means exact same length, same order, same exact
`ArtifactRef` values, and no hidden semantic input.

For a new M4 execution:

```text
non-runner-produced ReviewContext
→ INVALID-COGNITIVE-OPERATION
```

There is no alternate or imported-campaign branch.

## 5. M4-A public construction interfaces

```ts
interface CognitiveExecutionRequestTemplateV1 {
  readonly reviewContext: ReviewContext;
  readonly role: CognitiveExecutionRole;
  readonly reviewerProfileId: string;
  readonly prompt: ArtifactRef;
  readonly packet: ArtifactRef;
}

interface PrepareCognitiveExecutionRequestV1 {
  readonly execution: ExecutionRef;
  readonly workItem: WorkItemRef;
}

interface PreparedCognitiveExecutionV1 {
  readonly execution: ExecutionRef;
  readonly workItem: WorkItemRef;
  readonly requestTemplate: CognitiveExecutionRequestTemplateV1;
  readonly preparation: ArtifactRef;
  readonly dispatchEvidence: readonly [ArtifactRef, ArtifactRef];
  readonly recoveryCapability: RecoveryCapabilityRef;
}

type PrepareCognitiveExecutionResultV1 =
  | {
      readonly kind: "prepared";
      readonly value: PreparedCognitiveExecutionV1;
    }
  | {
      readonly kind: "operationally-blocked";
      readonly blockingObligationId: ObligationId;
      readonly cause: NonRecoveryOperationalCauseRefV1;
    };

interface CognitiveExecutionControlV1 {
  readonly signal: AbortSignal;
  readonly runnerSessionId: RunnerSessionId;
}

interface CognitiveExecutionCaptureModule {
  sealOperation(
    operation: CognitiveExecutionOperationV1
  ): Promise<ArtifactRef>;

  prepare(
    request: PrepareCognitiveExecutionRequestV1
  ): Promise<PrepareCognitiveExecutionResultV1>;

  execute(
    request: CognitiveExecutionRequest,
    control: CognitiveExecutionControlV1
  ): Promise<CognitiveExecutionCapture>;
}
```

`sealOperation` causes no external cognitive effect. `prepare` causes no
external cognitive effect. Only `execute` may make the cognitive dependency
invocation, and only after a valid M2 Arm.

## 6. WorkItem and request binding validation

For `prepare({execution:E, workItem:W})` require:

```text
E.workItemId == W.workItemId
W.executor == "cognitive-execution"
W.sourceObligationIds.length >= 1
W.operation exists and verifies
decoded operation passes exact Section 4 rules
every W.inputRefs ArtifactRef verifies
```

Before any possible operationally blocked return, define exactly:

```text
blockingObligationId =
W.sourceObligationIds[0]
```

This is only the deterministic presentation and admission anchor for the
credential blocker. It does not mean that this obligation uniquely caused
credential unavailability, that other source obligations are irrelevant, or
that the obligation becomes satisfied or disposed.

For successful preparation with decoded operation `O`, define:

```text
requestTemplate.reviewContext = O.reviewContext
requestTemplate.role = O.role
requestTemplate.reviewerProfileId = O.reviewerProfileId
requestTemplate.prompt = O.prompt
requestTemplate.packet = O.packet
```

For `execute(R, control)`, require exactly:

```text
R.dispatch.execution == prepared execution

R.dispatch.workItem == prepared exact WorkItem

R.dispatch.workItem.operation == exact prepared operation ArtifactRef

R.reviewContext == prepared requestTemplate.reviewContext

R.role == prepared requestTemplate.role

R.reviewerProfileId ==
    prepared requestTemplate.reviewerProfileId

R.prompt == prepared requestTemplate.prompt

R.packet == prepared requestTemplate.packet

R.dispatch.recoveryCapability ==
    exact prepared recoveryCapability

R.dispatch.dispatchEvidence ==
    exact prepared dispatchEvidence
```

M4 must not repair any mismatch. A mismatch is invocation failure.

## 7. Cognitive-call identity

```ts
type CognitiveCallId = string;
```

Derive exactly:

```text
callId =
deriveId(
    "m4-cognitive-call.v1",
    execution.executionId
)
```

Use the existing runner/M0 `deriveId` collision-safe domain-separated framing.

Identity mapping is exactly:

```text
WorkItemId
→ logical cognitive execution / receipt execution_id

ExecutionId
→ protocol attempt / receipt attempt_id

CognitiveCallId
→ one M4 cognitive call / receipt call_id

ProviderResponseId
→ provider-owned response identity
```

Require:

```text
one Execution → one callId
same Execution → same callId across restart
new Execution → new callId
callId is never replaced by provider response identity
```

Provider, model, and request identity do not enter callId derivation.

## 8. Pre-Arm preparation algorithm

`prepare()` executes exactly this order:

```text
1. Validate E/W and operation bindings.

2. Verify every referenced immutable input artifact.

3. Derive exact callId.

4. Request from the Issue #31 Dependency Contract the exact
   credential-free dependency execution plan for:
       exact operation
       exact callId

5. Seal/verify the exact dependencyExecutionPlan ArtifactRef according
   to the Dependency Contract representation.

6. Obtain from that plan exactly:
       provider
       request model
       runtime identity
       credentialRequirementId

7. Check required credential availability through the injected runtime
   credential boundary.

8. If the credential boundary legitimately establishes
   required credential unavailable:
       construct the exact Section 19 operational cause
       return exactly:
           {
             kind: "operationally-blocked",
             blockingObligationId: W.sourceObligationIds[0],
             cause: exact cognitive-execution cause,
           }
       create no PREPARED journal marker
       do not Arm
       do not call provider

9. If credential boundary invocation itself fails, rejects unexpectedly,
   returns malformed material, or violates its contract:
       fail invocation with CREDENTIAL-BOUNDARY-FAILURE

10. Construct and seal preparation artifact.

11. Construct and seal reconciliation-operation artifact.

12. Durably publish PREPARED journal marker.

13. Return PreparedCognitiveExecutionV1.
```

Credential secret values are not retained by preparation. Preparation
establishes availability only at that moment. Execution resolves and injects
the credential again immediately before the external-call fence.

## 9. Preparation and reconciliation artifacts

```ts
interface CognitiveExecutionPreparationArtifactV1 {
  readonly schema: "gate-a-cognitive-execution-preparation.v1";
  readonly execution: ExecutionRef;
  readonly workItemId: WorkItemId;
  readonly operation: ArtifactRef;
  readonly callId: CognitiveCallId;
  readonly dependencyExecutionPlan: ArtifactRef;
}
```

```ts
interface CognitiveReconciliationOperationV1 {
  readonly schema:
    "gate-a-cognitive-execution-reconciliation-operation.v1";

  readonly execution: ExecutionRef;
  readonly workItemId: WorkItemId;
  readonly callId: CognitiveCallId;
  readonly preparation: ArtifactRef;
  readonly journalKey: string;
}
```

Derive exactly:

```text
journalKey =
lowercaseHex(
    SHA256(
        UTF8(callId)
    )
)
```

Construct exactly:

```ts
RecoveryCapabilityRef {
  executor: "cognitive-execution",
  reconciliationOperation:
      exact sealed CognitiveReconciliationOperationV1 ArtifactRef
}
```

Successful preparation always has a non-null recovery capability. The selected
M4 realization has trustworthy local-journal recoverability even when it has no
provider-side read-only recovery lookup.

Set exactly:

```text
dispatchEvidence =
[
    preparationArtifactRef,
    reconciliationOperationArtifactRef
]
```

The order is exact and duplicate-free.

## 10. Durable M4 execution journal

M4 owns a durable operational journal separate from M2 authority.

```text
<journalRoot>/
└── calls/
    └── <journalKey>/
        ├── prepared.json
        ├── maybe-sent.json
        ├── terminal.json
        └── telemetry/
            ├── heartbeat.json
            └── provider-activity.json
```

The three truth-bearing marker names are exactly:

```text
prepared.json
maybe-sent.json
terminal.json
```

Telemetry files are not truth-bearing.

```ts
interface CognitiveExecutionPreparedMarkerV1 {
  readonly schema: "gate-a-cognitive-execution-journal-prepared.v1";
  readonly executionId: ExecutionId;
  readonly workItemId: WorkItemId;
  readonly callId: CognitiveCallId;
  readonly preparation: ArtifactRef;
  readonly reconciliationOperation: ArtifactRef;
}

interface CognitiveExecutionMaybeSentMarkerV1 {
  readonly schema: "gate-a-cognitive-execution-journal-maybe-sent.v1";
  readonly executionId: ExecutionId;
  readonly workItemId: WorkItemId;
  readonly callId: CognitiveCallId;
  readonly callStartEvidence: ArtifactRef;
}

interface CognitiveExecutionTerminalMarkerV1 {
  readonly schema: "gate-a-cognitive-execution-journal-terminal.v1";
  readonly executionId: ExecutionId;
  readonly workItemId: WorkItemId;
  readonly callId: CognitiveCallId;
  readonly terminalEvidence: ArtifactRef;
}
```

Truth-state interpretation is exactly:

```text
valid PREPARED
and no valid MAYBE-SENT
→ cognitive-call boundary never became reachable

valid MAYBE-SENT
and no valid TERMINAL-DURABLE
→ call may have crossed effect boundary; local truth unresolved

valid TERMINAL-DURABLE
→ exact terminal evidence is locally recoverable
```

`MAYBE-SENT` means only that the durable fence permitting the cognitive call or
provider attempt to become reachable has been crossed. It does not mean the
provider received the request, executed it, produced tokens, or completed.

Journal markers are write-once, never updated, never deleted by M4 during normal
execution, canonical JSON, and bound to the exact Execution, WorkItem, and call.

For each final marker publication use exactly:

```text
create parent directory
write canonical bytes to same-directory unique temporary file
fsync temporary file
close temporary file
require final marker target does not already exist
publish with an atomic no-replace filesystem operation
fsync marker directory
read back
canonical-parse
runtime-validate
```

If the platform or runtime cannot provide the required create-if-absent
publication semantics, fail the invocation. Never weaken this to overwrite or
last-writer-wins. Temporary orphan files after crash are non-authoritative
operational garbage.

## 11. Armed execution algorithm

`execute()` requires an already-valid `ArmedExecutionDispatchRef` and performs
exactly:

```text
1. Validate exact prepared bindings from Section 6.

2. Acquire one process-local exclusive execution lock keyed by callId.

3. Re-read and validate PREPARED marker and referenced artifacts.

4. Require:
       MAYBE-SENT absent
       TERMINAL absent

   If either already exists for this call:
       do not invoke provider
       fail invocation as PREPARATION-STATE-CONFLICT

5. If control.signal is already aborted:
       return uncertain using exact Arm evidence
       do not create call-start evidence
       do not create MAYBE-SENT
       do not invoke provider

6. Resolve the required credential again.

7. If credential is now legitimately unavailable:
       return uncertain using exact Arm evidence
       do not create call-start evidence
       do not create MAYBE-SENT
       do not invoke provider

8. Credential boundary contract failure:
       fail invocation

9. Re-check control.signal.

10. Capture startedAt from Node wall clock using Date.toISOString().

11. Construct and seal CognitiveCallStartEvidenceV1.

12. Re-check control.signal.
    If aborted:
       return uncertain using exact Arm evidence
       do not publish MAYBE-SENT
       do not invoke provider

13. Durably publish MAYBE-SENT marker.

14. Only after successful durable MAYBE-SENT publication may the direct
    dependency cognitive invocation become reachable.

15. Invoke the Issue #31 dependency adapter exactly once.

16. While the call is live:
       propagate control.signal
       emit best-effort heartbeat
       update best-effort provider-activity telemetry when provider activity
       is observed

17. Classify only from trustworthy dependency facts:

       completed provider-semantic textual response
       → completed-response terminal path

       positively established terminal no-completed-response failure
       → technical-failure terminal path

       anything else where external truth is not positively terminal
       → uncertain path

18. Never retry inside M4-A v1.
```

There is no automatic duration-based abort.

## 12. Dependency-consumer requirements

Issue #31 must provide a consumer contract satisfying exactly:

```text
@earendil-works/pi-ai@0.99.2
Pi source commit =
005af57d88ee23b33778f343a9595b32e67ff788

public execution surface =
Models.streamSimple(...)

fresh public pi-ai Context for every M4 call

one direct Models.streamSimple invocation per runner Execution

transport = SSE

dependency automatic retry disabled

dependency timeout disabled

tools disabled

deferred disabled

exact execution-owned AbortSignal propagated

no AgentSession

no coding-agent/subagent loop

no Codex CLI/App Server execution path

no inherited context

no cross-reviewer pre-seal visibility

provider/request evidence captured without rewriting semantic request

provider response identity captured only from provider-owned evidence

provider model captured only from provider-owned evidence

exact provider-semantic textual completion exposed before interpretation

credential requirement exposed without credential value

runtime name/version exposed

request provider/model exposed

transport-attempt count exposed

terminal-vs-ambiguous dependency outcomes mechanically distinguishable
```

For the selected v1 realization, dependency automatic retries equal zero.
Therefore every receipt-admissible terminal M4 attempt that reaches transport
has:

```text
transportAttemptCount == 1
```

Pre-call paths with no transport attempt do not become receipt technical-failure
attempts. Pi source and API details beyond these M4 consumer requirements remain
owned by Issue #31.

## 13. Raw completion and terminal evidence

```ts
interface CognitiveCallStartEvidenceV1 {
  readonly schema: "gate-a-cognitive-call-start.v1";
  readonly execution: ExecutionRef;
  readonly workItemId: WorkItemId;
  readonly callId: CognitiveCallId;
  readonly dispatchIntent: ArtifactRef;
  readonly preparation: ArtifactRef;
  readonly startedAt: string;
}
```

`startedAt` is Node `Date.toISOString()` UTC wall-clock provenance only. It
never controls timeout, retry, recovery, or classification.

```ts
interface CognitiveCompletedResponseEvidenceV1 {
  readonly schema: "gate-a-cognitive-completed-response.v1";
  readonly kind: "completed-response";

  readonly execution: ExecutionRef;
  readonly workItemId: WorkItemId;
  readonly callId: CognitiveCallId;

  readonly dispatchIntent: ArtifactRef;
  readonly preparation: ArtifactRef;
  readonly callStartEvidence: ArtifactRef;

  readonly startedAt: string;
  readonly endedAt: string;

  readonly runtime: {
    readonly name: string;
    readonly version: string;
  };

  readonly request: {
    readonly provider: string;
    readonly model: string;
  };

  readonly transportAttemptCount: number;

  readonly providerResponseId: string | null;
  readonly providerModel: string | null;
  readonly termination: string | null;

  readonly rawResult: ArtifactRef;

  readonly dependencyRequestEvidence: ArtifactRef;
  readonly dependencyRuntimeEvidence: readonly ArtifactRef[];
}

interface CognitiveTechnicalFailureEvidenceV1 {
  readonly schema: "gate-a-cognitive-technical-failure.v1";
  readonly kind: "technical-failure";

  readonly execution: ExecutionRef;
  readonly workItemId: WorkItemId;
  readonly callId: CognitiveCallId;

  readonly dispatchIntent: ArtifactRef;
  readonly preparation: ArtifactRef;
  readonly callStartEvidence: ArtifactRef;

  readonly startedAt: string;
  readonly endedAt: string;

  readonly runtime: {
    readonly name: string;
    readonly version: string;
  };

  readonly request: {
    readonly provider: string;
    readonly model: string;
  };

  readonly transportAttemptCount: number;

  readonly providerResponseId: string | null;
  readonly providerModel: string | null;
  readonly termination: string | null;

  readonly completedResponse: false;

  readonly dependencyRequestEvidence: ArtifactRef;
  readonly dependencyRuntimeEvidence: readonly ArtifactRef[];
  readonly failureEvidence: readonly ArtifactRef[];
}

type CognitiveAttemptTerminalEvidenceV1 =
  | CognitiveCompletedResponseEvidenceV1
  | CognitiveTechnicalFailureEvidenceV1;
```

All evidence arrays are duplicate-free. `endedAt` is captured at trustworthy
terminal observation and serialized with `Date.toISOString()`. Time values are
provenance only.

For a completed provider-semantic textual response:

```text
take exact text exposed by accepted dependency contract
encode exactly as UTF-8
NO trim
NO newline insertion/removal
NO Unicode normalization
NO JSON parsing
NO JSON repair
NO refusal interpretation
NO schema validation
NO semantic classification
```

Seal the exact UTF-8 bytes through `CampaignArtifactStore` with:

```text
mediaType = text/plain; charset=utf-8
```

The resulting `ArtifactRef` is `rawResult`. Empty textual completion, malformed
JSON, refusal text, wrong schema, or semantically invalid content remains a
completed captured response. M6 owns later protocol validation.

Completed terminal ordering is exactly:

```text
provider-semantic completion observed
↓
seal exact rawResult bytes
↓
construct/seal completed terminal evidence
↓
durably publish terminal.json
↓
construct CapturedExecutionResult
↓
return captured
```

Technical-failure terminal ordering applies only to a positive accepted
Dependency Contract fact that the exact call terminated with no completed
semantic response:

```text
positive terminal no-completed-response fact
↓
seal all required failure/runtime evidence
↓
construct/seal technical-failure terminal evidence
↓
durably publish terminal.json
↓
construct TechnicalExecutionFailure
↓
return technical-failure
```

None of these alone establishes technical failure:

```text
AbortError
network exception
stream interruption
missing response
process interruption
elapsed time
cancellation request
missing provider material
ambiguous transport failure
```

## 14. M4 result construction

For a captured result return exactly:

```ts
{
  kind: "captured",
  value: {
    execution: request.dispatch.execution,
    rawResult: exactTerminal.rawResult,
    runtimeEvidence: orderedUnique([
      preparation,
      reconciliationOperation,
      callStartEvidence,
      terminalEvidence,
      dependencyRequestEvidence,
      ...dependencyRuntimeEvidence,
    ]),
  },
}
```

Use exact first-occurrence order above.

For technical failure return exactly:

```ts
{
  kind: "technical-failure",
  value: {
    execution: request.dispatch.execution,
    completedResponse: false,
    failureEvidence: orderedUnique([
      preparation,
      reconciliationOperation,
      callStartEvidence,
      terminalEvidence,
      dependencyRequestEvidence,
      ...dependencyRuntimeEvidence,
      ...terminalFailureEvidence,
    ]),
  },
}
```

For legitimate pre-call abort or credential disappearance after Arm return:

```ts
{
  kind: "uncertain",
  value: {
    execution: request.dispatch.execution,
    workItem: request.dispatch.workItem,
    dispatchState: "POSSIBLY-DISPATCHED",
    dispatchIntent: request.dispatch.dispatchIntent,
    dispatchEvidence: request.dispatch.dispatchEvidence,
    terminalOutcome: null,
    recoveryCapability: request.dispatch.recoveryCapability,
  },
}
```

Do not append fake evidence.

After `MAYBE-SENT`, when no trustworthy terminal fact exists, use the exact
armed execution and WorkItem, `POSSIBLY-DISPATCHED`, exact Arm dispatch intent,
null terminal outcome, and exact Arm recovery capability. Set
`dispatchEvidence` to the ordered duplicate-free sequence:

```text
[
    ...exact arm-time dispatchEvidence,
    callStartEvidence,
    dependencyRequestEvidence if durably available,
    ...durably sealed same-call dependencyRuntimeEvidence
]
```

Do not remove or reorder Arm-time evidence and do not manufacture a terminal
outcome.

## 15. Abort and cancellation behavior

There is no automatic M4 timeout and no elapsed-time decision. M4 receives only
the execution-owned caller `AbortSignal`.

Abort means a control request, never execution truth.

```text
abort before MAYBE-SENT
→ no cognitive call
→ uncertain direct return
→ later M4-B may prove nonexecution from PREPARED state

abort after MAYBE-SENT
→ propagate to dependency
→ if durable completed terminal fact exists: captured
→ if durable positive terminal no-response failure exists: technical-failure
→ otherwise: uncertain
```

M4 must not claim:

```text
abort == provider stopped
abort == provider did not execute
abort == technical failure
abort == rollback
```

No new provider attempt may begin after the caller signal is observed aborted.

## 16. Crash, interruption, and restart table

```text
PREPARED only
→ cognitive-call boundary never became reachable
→ future M4-B may produce positive non-execution proof

MAYBE-SENT without TERMINAL-DURABLE
→ local truth cannot establish terminal outcome
→ future M4-B must not infer nonexecution
→ selected backend local recovery resolves conservatively to indeterminacy

TERMINAL-DURABLE
→ exact terminal evidence is locally reconstructible
→ future M4-B may return exact recovered terminal outcome
```

Also require:

```text
process crash before PREPARED publication
→ no valid preparation result exists

process crash after PREPARED before Arm
→ no external call possible
→ orphan preparation is non-authoritative

process crash after Arm before MAYBE-SENT
→ M2 still projects unresolved POSSIBLY-DISPATCHED
→ M4-B local PREPARED proof may later establish not-executed

process crash after MAYBE-SENT
→ never replay same Execution
→ recovery only

process crash after terminal evidence but before terminal marker
→ no direct result may be fabricated
→ later recovery is conservative according to durable journal state
```

A CAS artifact existing without a valid journal reference does not by itself
advance journal state.

## 17. Liveness telemetry

Telemetry is required for operational visibility but is never execution truth.

`heartbeat.json` is mutable best-effort telemetry containing at least:

```text
executionId
callId
runnerSessionId
sequence
observedAt
```

It is refreshed periodically while the M4 call is live after `MAYBE-SENT`.

`provider-activity.json` is mutable best-effort telemetry containing at least:

```text
executionId
callId
sequence
observedAt
```

It is refreshed only when provider or runtime activity is actually observed.
Both files may be overwritten, need not be fsync truth barriers, and are not
`ArtifactRef`s, evidence, authority, recovery inputs, or ownership.

A telemetry write failure does not abort the call, create technical failure,
create uncertainty, or alter journal state.

A stale or missing heartbeat or provider-activity file implies only that no
recent telemetry was observed. It never proves process death, provider death,
nonexecution, completion, failure, or unknown.

## 18. Idempotence and non-replay

`sealOperation` is content-addressed and replay-safe.

`prepare(E,W)` is idempotent only for the exact same preparation. If the exact
valid preparation and journal already exist and all bindings match, return the
same logical preparation. If the same Execution maps to divergent preparation
material, fail with `PREPARATION-STATE-CONFLICT`.

`execute()` is not replayable. For one `callId`:

```text
at most one legitimate MAYBE-SENT transition
at most one external cognitive call
at most one TERMINAL-DURABLE marker
```

Concurrent same-call execution is serialized by the exact process-local call
lock plus write-once journal markers. A second execute after `MAYBE-SENT` must
never call the provider. After process restart, never resume by replaying the
same armed Execution.

Even when recovery later proves `PROVEN-NOT-EXECUTED`, the normal M5/M8/M2
lifecycle creates a new runner Execution with a new `callId`. Never reuse the
prior Execution.

## 19. Operational credential blocker

```ts
interface CognitiveExecutionOperationalCauseV1 {
  readonly schema:
    "gate-a-cognitive-execution-operational-cause.v1";

  readonly kind:
    "required-provider-credential-unavailable";

  readonly runId: GateARunId;
  readonly executionId: ExecutionId;
  readonly workItemId: WorkItemId;

  readonly reviewerProfileId: string;
  readonly provider: string;
  readonly credentialRequirementId: string;

  readonly dependencyExecutionPlan: ArtifactRef;
}
```

This cause exists only during pre-Arm `prepare()` when the credential boundary
legitimately establishes that the required credential is unavailable. Canonical
serialize and seal the cause descriptor. The obligation anchor remains separate
from producer-domain credential meaning; do not add `obligationId` to this cause
descriptor.

Construct exactly:

```ts
NonRecoveryOperationalCauseRefV1 {
  producer: "cognitive-execution",

  causeDescriptor:
      exact CognitiveExecutionOperationalCauseV1 ArtifactRef,

  basisArtifacts: [
      exact workItem.operation,
      exact dependencyExecutionPlan,
  ],

  resolutionContracts: [
      { kind: "request-operational-recheck" },
  ],
}
```

No replacement-execution resolution contract is lawful for this pre-Arm cause.
M4 does not construct `OperationalBlocker`; M8-B does. M2 admits the resulting
blocker authoritatively.

## 20. Invocation failure taxonomy

```ts
type CognitiveExecutionInvocationFailureCodeV1 =
  | "INVALID-COGNITIVE-OPERATION"
  | "INVALID-PREPARATION-REQUEST"
  | "INVALID-EXECUTION-REQUEST"
  | "ARTIFACT-INTEGRITY-FAILURE"
  | "PREPARATION-STATE-CONFLICT"
  | "JOURNAL-INTEGRITY-FAILURE"
  | "JOURNAL-IO-FAILURE"
  | "ARTIFACT-SEAL-FAILURE"
  | "DEPENDENCY-CONTRACT-VIOLATION"
  | "CREDENTIAL-BOUNDARY-FAILURE";
```

These are invocation failures. They are not `CognitiveExecutionCapture`,
`TechnicalExecutionFailure`, `UnresolvedExecutionRecoveryRef`,
`OperationalBlocker`, M8 unknown, M8 pending, or `DECISION-REQUIRED`.

Map exactly:

```text
malformed/mismatched operation
→ INVALID-COGNITIVE-OPERATION

E/W/preparation mismatch before Arm
→ INVALID-PREPARATION-REQUEST

armed request contradicts exact prepared bindings
→ INVALID-EXECUTION-REQUEST

missing/corrupt immutable artifact
→ ARTIFACT-INTEGRITY-FAILURE

same call has divergent or already-crossed lifecycle
→ PREPARATION-STATE-CONFLICT

malformed/impossible journal state
→ JOURNAL-INTEGRITY-FAILURE

filesystem persistence/publication failure
→ JOURNAL-IO-FAILURE

CampaignArtifactStore sealing failure
→ ARTIFACT-SEAL-FAILURE

Dependency Contract returns impossible/malformed material
→ DEPENDENCY-CONTRACT-VIOLATION

credential boundary rejects/throws/malforms unexpectedly
→ CREDENTIAL-BOUNDARY-FAILURE
```

Implementation, process, and integrity failures reject the M4 invocation. They
must never be hidden as execution uncertainty. If Arm already exists, the
authoritative unresolved Execution remains in M2 history despite the invocation
failure. A later run passes through the ordinary recovery barrier.

## 21. Credential and secret boundary

Secrets may exist only in transient runtime memory at the dependency invocation
boundary.

Never put secret values into:

```text
WorkItem.operation
dependencyExecutionPlan
preparation
reconciliationOperation
journal markers
telemetry
rawResult metadata
runtime evidence
failure evidence
causeDescriptor
dispatchEvidence
execution receipt
logs intended as durable evidence
repository
GitHub
```

Never persist `Authorization`, `Cookie`, an OAuth token, API key, secret-bearing
URL, or credential-source payload. The Dependency Contract owns exact runtime
credential injection mechanics. M4 owns only the rule that secrets never become
evidence or semantic authority.

## 22. Required invariants

```text
M4A-01
One cognitive WorkItem has one immutable M4-owned operation artifact.

M4A-02
WorkItem.inputRefs is exactly [operation.prompt, operation.packet].

M4A-03
One runner Execution maps deterministically to exactly one M4 callId.

M4A-04
One M4 callId may cross MAYBE-SENT at most once.

M4A-05
The external cognitive dependency is unreachable before successful M2 Arm.

M4A-06
The external cognitive dependency is unreachable before durable MAYBE-SENT.

M4A-07
Successful preparation carries a non-null cognitive-execution recovery capability.

M4A-08
PREPARED without MAYBE-SENT is the only local-journal state sufficient for
M4-B to establish positive cognitive nonexecution.

M4A-09
MAYBE-SENT without terminal evidence never proves execution, nonexecution,
failure, or completion.

M4A-10
TERMINAL-DURABLE references exactly one valid terminal evidence artifact.

M4A-11
A completed provider-semantic textual response is always sealed exactly before
any protocol interpretation.

M4A-12
Malformed or semantically invalid completion content remains a captured response.

M4A-13
TechnicalExecutionFailure requires positive terminal proof that no completed
semantic response exists.

M4A-14
Abort and elapsed time never create execution truth.

M4A-15
There is no automatic execution timeout in M4-A v1.

M4A-16
There is no dependency/provider automatic retry in the selected M4-A v1 realization.

M4A-17
A runner-level retry always means a new Execution and therefore a new callId.

M4A-18
Provider response identity is never substituted for callId.

M4A-19
Provider-reported model evidence is preserved without resolving Issue #47.

M4A-20
Heartbeat and provider-activity telemetry are non-authoritative and non-evidentiary.

M4A-21
M4-A never writes M2 authoritative campaign state.

M4A-22
M4-A never assigns qualified/protocol-invalid or M8 recovery classifications.

M4A-23
Credential unavailability before Arm is a cognitive-execution producer cause,
not a technical failure.

M4A-24
Credential disappearance after Arm but before MAYBE-SENT produces no provider
effect and is routed through the armed unresolved recovery lifecycle.

M4A-25
An invocation/process/integrity failure is never disguised as an execution-domain result.
```

## 23. Forbidden behavior

M4-A explicitly forbids:

```text
AgentSession
coding-agent loop
subagent loop
Codex CLI
Codex App Server
inherited prior conversation/context
cross-reviewer context sharing before seal
tools
automatic timeout
elapsed-time cancellation
Pi/provider automatic retry
M4 protocol retry
response JSON repair
response trim/normalization
response semantic interpretation
qualified/protocol-invalid classification
provider alias resolution
fabricated provider model
fabricated provider response ID
provider response ID used as callId
M4 authoritative M2 writes
M4 OperationalBlocker construction
heartbeat-driven ownership
heartbeat-driven recovery
missing heartbeat as failure
same-Execution replay
secret persistence
```

## 24. Integration boundaries

```text
M1
→ obtains/coordinates exact cognitive WorkItem inputs
→ asks M4-A to seal exact operation
→ obtains Execution from M2
→ calls M4-A prepare before Arm
→ transports preparation dispatchEvidence + recoveryCapability
→ performs fresh revalidation
→ commits M2 Arm
→ constructs CognitiveExecutionRequest only by exact projection of prepared
   requestTemplate + exact ArmedExecutionDispatchRef
→ calls M4-A execute

M2
→ owns Execution identity
→ owns Arm authoritative transition
→ owns authoritative outcome/uncertainty admission
→ never interprets Pi
→ never interprets M4 operation internals

M4-A
→ owns execution/capture facts only

M4-B
→ later owns cognitive recovery observation meaning
→ consumes the exact preparation/journal/reconciliation artifacts created here
→ is not authored in this task

M6
→ receives exact CognitiveExecutionRequest + CapturedExecutionResult
→ alone mechanically determines qualified/protocol-invalid where permitted

M5
→ owns protocol/campaign retry authorization and receipt assembly

M8
→ owns recovery classification/operator boundary
→ never reimplements M4 journal/domain proof meaning
```

For the pre-Arm credential-blocker occurrence, let:

```text
S =
exact authoritative snapshot from which
the selected still-unarmed Execution E and WorkItem W
were obtained for this preparation occurrence
```

If `prepare(E, W)` returns `operationally-blocked` value `B`, require:

```text
B.blockingObligationId ==
W.sourceObligationIds[0]

B.cause.producer ==
"cognitive-execution"

B.cause.resolutionContracts ==
[
  { kind: "request-operational-recheck" }
]
```

M1 invokes exactly:

```ts
recovery_operator.materialize_operational_blocker({
  kind: "producer-occurrence",

  runId:
      W.runId,

  baseStateRevision:
      S.stateRevision,

  producer:
      "cognitive-execution",

  obligationId:
      B.blockingObligationId,

  workItemId:
      W.workItemId,

  executionId:
      E.executionId,

  causeDescriptor:
      B.cause.causeDescriptor,

  resolutionContracts:
      B.cause.resolutionContracts,
})
```

M1 never constructs `BlockerId`, an Operator Action Request, or
`operatorRequest`. M8-B owns blocker identity, Operator Action Request
construction, and `OperationalBlocker` materialization.

The underlying source obligation is already authoritative before the WorkItem
and Execution exist. M1 therefore proposes exactly one
`EstablishOperationalBlockersV1` through M2 with:

```text
obligationsToAdd = []

blockers =
[
  exact M8-B materialized blocker
]

basisArtifacts =
ordered duplicate-free first-occurrence sequence:
[
  B.cause.causeDescriptor,
  ...B.cause.basisArtifacts
]

expectedStateRevision =
S.stateRevision
```

M2 alone owns authoritative blocker admission. If `S.stateRevision` is stale,
M1 admits no blocker from the stale occurrence, does not rebind the old
occurrence identity to a new `StateRevision`, reloads authoritative state, and
returns to ordinary orchestration and revalidation. M1 does not reinterpret or
mutate the M4 cause.

This preserves the accepted occurrence discipline:

```text
producer cause
→ M8-B materialization
→ M2 authoritative admission
```

## 25. Dependency Contract obligations

The future scoped Pi contract owned by Issue #31 must satisfy every requirement
in Section 12 and additionally close:

```text
exact dependencyExecutionPlan schema
exact provider/request-model projection
exact runtime identity projection
exact credentialRequirementId
exact runtime credential injection
exact Models.streamSimple request construction
exact fresh Context construction
exact SSE option construction
exact maxRetries=0 binding
exact disabled dependency timeout binding
exact tools/deferred disabling
exact AbortSignal propagation
exact request evidence schema
exact runtime/provider evidence schema
exact providerResponseId extraction
exact providerModel extraction
exact textual completion extraction
exact transportAttemptCount definition
exact terminal-no-completed-response facts
exact ambiguous failure mapping
known provider-normalization limitations
selected backend recovery limitation
```

The M4 NIB does not implement those Pi facts itself. GREEN for M4-A remains
blocked until the accepted Dependency Contract exists.

## 26. Unresolved model-identity boundary

Issue #47 remains unresolved.

M4-A may capture:

```text
requested provider
requested model
provider-owned response model
provider-owned response identity
```

It may not decide whether a provider-reported identifier is a resolved immutable
`model_version` or an unresolved alias. No syntax heuristic, date suffix,
repeated observation, Pi behavior, or provider documentation is allowed to
resolve that Product Semantics question here.
