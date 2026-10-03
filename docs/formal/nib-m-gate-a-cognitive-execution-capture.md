---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-02"
step_id: 2
id: NIB-M-GATE-A-COGNITIVE-EXECUTION-CAPTURE
version: "1.1.0"
scope: gate-a-campaign-runner/cognitive-execution/execution-capture
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Cognitive Execution — Execution and Capture

It consumes `NIB-S-GATE-A-CAMPAIGN-RUNNER` version `9.1.0`.

Version `1.1.0` is built on version `1.0.5`, preserves all of its exact adapter
interface, strict UTF-8, unsealed-result, evidence-sealing, and journal-ownership
closures, closes the Issue #47 provider-reported realization boundary, and
activates `DC-PI-M4-GATE-A-COGNITIVE-EXECUTION` version `1.1.0`. It changes no
public interface.

Version `1.0.5` consumes
`DC-PI-M4-GATE-A-COGNITIVE-EXECUTION` version `1.0.1` and closes only the exact
adapter interface, strict UTF-8 failure mapping, unsealed dependency-result
mapping, and M4-owned evidence-sealing boundary. It changes no M4 execution or
capture semantics.

Version 1.0.4 activates
`DC-PI-M4-GATE-A-COGNITIVE-EXECUTION` version `1.0.0` as the exact selected
Pi dependency contract required by M4-A.

It changes no M4 execution/capture semantics established by versions 1.0.1
through 1.0.3.

Version `1.0.3` binds the exact selected
`GateAReviewerAcquisitionCandidateV1` into the immutable M4 WorkItem operation
so provider and requestModel are never inferred from reviewerProfileId.

This is a pre-GREEN construction closure. It changes no product semantics,
hostile-review protocol semantics, reviewer-acquisition policy, provider/model
selection, retry, recovery, persistence, module ownership, or Issue #47
identity-resolution authority.

Version 1.0.2 synchronizes this Module Brief with
NIB-S-GATE-A-CAMPAIGN-RUNNER 9.0.0.

The reviewer-acquisition System Brief change does not alter M4-A execution,
capture, AbortSignal, journal, credential, dependency-call, technical-failure,
uncertainty, or receipt-attempt material semantics.

All behavior introduced by version 1.0.1 remains unchanged.

Version `1.0.1` closes three implementation-construction completeness gaps in
version `1.0.0` without changing TURNLOCK product semantics, hostile-review
protocol semantics, system-level module decomposition, recovery
classifications, or dependency selection.

It closes:

1. caller execution-authority revocation projection onto the execution-owned
   `AbortSignal` and the final pre-dependency signal fence;
2. deterministic prepare replay while credential availability remains a
   freshly observed operational condition;
3. exact handling of atomic journal-marker create-if-absent collisions.

It also makes explicit that, for selected v1, a `TechnicalExecutionFailure`
that can become a schema-v3 receipt attempt must carry
`transportAttemptCount == 1`.

No product ADR is created.

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
  readonly schema:
    "gate-a-cognitive-execution-operation.v1";

  readonly reviewContext:
    ReviewContext;

  readonly role:
    CognitiveExecutionRole;

  readonly reviewerProfileId:
    string;

  readonly reviewerAcquisitionCandidate:
    GateAReviewerAcquisitionCandidateV1;

  readonly prompt:
    ArtifactRef;

  readonly packet:
    ArtifactRef;
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

O.reviewerAcquisitionCandidate.profileId ==
    O.reviewerProfileId

W.inputRefs ==
[
    O.prompt,
    O.packet
]
```

The `inputRefs` equality means exact same length, same order, same exact
`ArtifactRef` values, and no hidden semantic input. The acquisition candidate is
immutable execution configuration retained in the operation, not an additional
cognitive textual input.

Runtime-validate the complete candidate structure. Require exactly:

```text
identityResolution.kind == "provider-reported"
→ staticallyKnownEffectiveIdentity == null

identityResolution.kind == "pinned-request-model"
→ requestModelIsImmutableVersion == true
→ staticallyKnownEffectiveIdentity ==
    {
      provider:
        O.reviewerAcquisitionCandidate.provider,

      modelVersion:
        O.reviewerAcquisitionCandidate.requestModel
    }
```

M4 does not:

```text
choose candidate
check acquisition-round eligibility
compute reviewer deficit
determine reviewer independence
re-run M3
re-read P
```

Those responsibilities remain upstream.

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
```

`control.signal` is the sole M4-A live projection of caller-owned execution
control.

M4-A does not query M2, poll campaign state, infer ownership from time, or
interpret `ExecutionProgressionSupersessionRef` itself.

The caller/orchestrator owns the `AbortController`.

For each live armed cognitive Execution, M1 must pass the exact execution-owned
`AbortSignal` and must abort that controller immediately when M1 observes that
the caller's authority to begin or continue new external work for that exact
Execution has been revoked.

This includes an authoritative progression supersession naming that Execution
as the prior Execution and any other caller/orchestration event that, under the
accepted system contract, revokes that exact Execution's future external-work
authority.

Explicit shutdown or cancellation also uses the same signal.

Abort is control only. It never establishes provider, transport, execution,
recovery, or rollback truth.

Exact detection and orchestration of caller-side revocation belongs to the
future M1 construction contract. M4-A's contract is that every such revocation
is projected through the exact signal it receives.

```ts
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

R.reviewerProfileId ==
    prepared operation.reviewerAcquisitionCandidate.profileId

R.dispatch.recoveryCapability ==
    exact prepared recoveryCapability

R.dispatch.dispatchEvidence ==
    exact prepared dispatchEvidence
```

M4 must not repair any mismatch. A mismatch is invocation failure.

M4-A owns every prompt and packet `ArtifactRef` read and verification. For each
exact artifact bytes `B`, it decodes exactly:

```ts
const text =
  new TextDecoder(
    "utf-8",
    {
      fatal: true,
      ignoreBOM: true,
    },
  ).decode(B);
```

Then require:

```text
UTF8(text) == B byte-for-byte
```

Map exactly:

```text
invalid prompt/packet UTF-8
or failed exact UTF-8 round trip
→ ARTIFACT-INTEGRITY-FAILURE
```

This happens before dependency invocation. The adapter receives only the exact
decoded `promptText` and `packetText`; it never reads an `ArtifactRef`.

`CognitiveExecutionRequest` and `CognitiveExecutionRequestTemplateV1` retain
their existing cross-module shapes and continue to project only
`reviewerProfileId`. Provider and requestModel remain M4-internal execution
realization facts retained through the immutable WorkItem operation and
preparation.

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

3. Derive exact callId and exact journalKey.

4. Inspect the exact call journal before constructing new preparation.

5. If MAYBE-SENT or TERMINAL already exists:
       validate the observed marker enough to bind it to this exact call;
       do not construct another preparation;
       fail this prepare invocation as PREPARATION-STATE-CONFLICT.

6. If PREPARED already exists:
       runtime-validate prepared.json;
       require exact:
           executionId
           workItemId
           callId;

       verify its preparation and reconciliationOperation ArtifactRefs;

       read/validate the exact existing CognitiveExecutionPreparationArtifactV1;

       require:
           preparation.execution == E
           preparation.workItemId == W.workItemId
           preparation.operation == W.operation
           preparation.callId == callId;

       read/validate the exact existing
       CognitiveReconciliationOperationV1;

       require exact binding to:
           E
           W
           callId
           preparation
           journalKey;

       use the EXISTING dependencyExecutionPlan referenced by the existing
       preparation;

       do NOT derive or seal another dependencyExecutionPlan;
       do NOT construct another preparation artifact;
       do NOT construct another reconciliation operation;
       do NOT publish another PREPARED marker;

       require the existing plan binds exactly:
           callId == derived callId
           reviewerProfileId ==
               O.reviewerAcquisitionCandidate.profileId
           provider ==
               O.reviewerAcquisitionCandidate.provider
           requestModel ==
               O.reviewerAcquisitionCandidate.requestModel;

       if retained plan contradicts the immutable operation:
           JOURNAL-INTEGRITY-FAILURE;
           do not derive a replacement plan;

       obtain runtime identity and credentialRequirementId from the exact
       validated existing plan;

       check credential availability NOW through the runtime credential
       boundary;

       if currently unavailable:
           construct the exact Section 19 operational cause using the existing
           dependencyExecutionPlan;
           return operationally-blocked with:
               blockingObligationId = W.sourceObligationIds[0];
           retain the existing PREPARED material unchanged;
           do not Arm;
           do not call provider;

       if credential-boundary contract failure:
           CREDENTIAL-BOUNDARY-FAILURE;

       otherwise:
           reconstruct and return the exact same logical
           PreparedCognitiveExecutionV1 from the already-sealed preparation,
           reconciliation operation, request template, dispatchEvidence, and
           RecoveryCapabilityRef.

7. Otherwise PREPARED does not exist:
       define authoritative preparation inputs exactly:
           reviewerProfileId =
               O.reviewerAcquisitionCandidate.profileId
           provider =
               O.reviewerAcquisitionCandidate.provider
           requestModel =
               O.reviewerAcquisitionCandidate.requestModel
           identityResolution =
               O.reviewerAcquisitionCandidate.identityResolution;

       if identityResolution.kind == "provider-reported":
           require selected DC ==
               DC-PI-M4-GATE-A-COGNITIVE-EXECUTION 1.1.0;

           observe selected DC capability:
               provider-owned-canonical-effective-model-identity-v1
               == NOT-ESTABLISHED;

           fail prepare invocation as:
               DEPENDENCY-CONTRACT-VIOLATION;

           do NOT call adapter.buildExecutionPlan;
           do NOT seal dependencyExecutionPlan;
           do NOT check credential availability;
           do NOT construct preparation artifact;
           do NOT construct reconciliation operation;
           do NOT publish PREPARED;
           do NOT Arm;
           do NOT invoke provider;

       if identityResolution.kind == "pinned-request-model":
           require the already-existing acquisition-candidate invariant:
               requestModelIsImmutableVersion == true;

       construct exactly:
           PiM4BuildExecutionPlanRequestV1 {
               schema:
                   "gate-a-pi-m4-build-execution-plan-request.v1",
               callId:
                   exact callId,
               reviewerProfileId:
                   exact reviewerProfileId,
               provider:
                   exact provider,
               requestModel:
                   exact requestModel,
           };

       synchronously call:
           adapter.buildExecutionPlan(
               exact PiM4BuildExecutionPlanRequestV1
           );

       do not await, yield, read credentials, or perform network I/O;

       seal/verify the returned plan through M4-owned
       CampaignArtifactStore;

       require the returned plan binds exactly:
           plan.callId == derived callId
           plan.reviewerProfileId == reviewerProfileId
           plan.provider == provider
           plan.requestModel == requestModel;

       any contradiction:
           DEPENDENCY-CONTRACT-VIOLATION;
           do not accept substitution;

       obtain runtime identity and credentialRequirementId from the exact
       validated plan;

       check current credential availability;

       if unavailable:
           construct Section 19 cause;
           return operationally-blocked;
           create no PREPARED marker;
           do not Arm;
           do not call provider;

       credential-boundary contract failure
           → CREDENTIAL-BOUNDARY-FAILURE;

       construct/seal preparation artifact;

       construct/seal reconciliation-operation artifact;

       publish PREPARED using the Section 10 exact create-if-absent rules;

       if PREPARED publication succeeds:
           return PreparedCognitiveExecutionV1;

       if PREPARED publication reports already-exists:
           re-read the winner's PREPARED marker and exact referenced artifacts;

           if they are valid and describe the exact same logical preparation
           for E/W/callId/operation:
               treat the race as idempotent prepare convergence;
               return that exact existing PreparedCognitiveExecutionV1;

           if the existing valid marker represents divergent preparation
           material for the same Execution/call:
               PREPARATION-STATE-CONFLICT;

           if the existing marker/artifacts are malformed, corrupt, or
           identity-mismatched:
               JOURNAL-INTEGRITY-FAILURE;

       genuine filesystem/storage publication failure
           → JOURNAL-IO-FAILURE.
```

Preparation material is immutable and idempotent.

Credential availability is not preparation identity and is re-observed on every
prepare occurrence before Arm.

An existing `PREPARED` marker does not authorize skipping current credential
availability checking.

Credential secret values are not retained by preparation. Execution resolves
and injects the credential again immediately before the external-call fence.

The authoritative provider, requestModel, and reviewerProfileId are always the
exact immutable operation-candidate values. The Dependency Contract validates
and realizes those values; it never selects or replaces them.

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

Every atomic no-replace marker publication has exactly one conceptual outcome:

```text
CREATED
ALREADY-EXISTS
IO-FAILURE
```

`ALREADY-EXISTS` is not itself an I/O failure.

For a `PREPARED` target that already exists:

```text
re-read winner marker and referenced artifacts

same exact logical E/W/callId/operation preparation
→ idempotent prepare convergence
→ use existing prepared result

valid but divergent preparation for same Execution/call
→ PREPARATION-STATE-CONFLICT

malformed/corrupt/identity-mismatched marker or referenced artifact
→ JOURNAL-INTEGRITY-FAILURE
```

For a `MAYBE-SENT` target that already exists during `execute()`:

```text
re-read winner marker

valid marker bound to the same E/W/callId
→ another invocation already won the external-effect fence
→ current invocation MUST NOT invoke dependency
→ PREPARATION-STATE-CONFLICT

malformed/corrupt/wrong E/W/call binding
→ JOURNAL-INTEGRITY-FAILURE
```

Even when the existing `MAYBE-SENT` bytes equal the local candidate bytes, the
losing invocation must not treat this as permission to call the dependency.
Only the invocation that successfully performs the create-if-absent transition
may proceed toward the provider call.

If `TERMINAL` publication encounters an existing target:

```text
re-read marker + referenced terminal evidence

exact same valid terminalEvidence as the terminal fact currently being
published
→ treat terminal-marker publication as already durably complete
→ do not invoke provider again
→ continue constructing the corresponding return value

valid same-call terminal marker naming a DIFFERENT terminalEvidence
→ JOURNAL-INTEGRITY-FAILURE

malformed/corrupt/wrong-binding marker
→ JOURNAL-INTEGRITY-FAILURE
```

Genuine storage failures other than the classified target-exists condition are
`JOURNAL-IO-FAILURE`.

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

13. Attempt durable create-if-absent MAYBE-SENT publication.

14. If MAYBE-SENT publication reports ALREADY-EXISTS:
        apply exact Section 10 collision classification;
        current invocation never calls dependency.

15. Require this invocation successfully created MAYBE-SENT.

16. Re-check control.signal immediately after durable MAYBE-SENT publication.

17. If aborted:
        do NOT invoke dependency;
        return uncertain using exact Arm evidence plus callStartEvidence as
        same-execution dispatch evidence;
        preserve MAYBE-SENT;
        do not claim nonexecution;
        later recovery remains conservative because MAYBE-SENT exists.

18. If not aborted:
        construct the exact PiM4DependencyInvocationRequestV1 from:
            exact validated dependencyExecutionPlan
            exact M4-decoded promptText
            exact M4-decoded packetText
            exact transient OAuthCredential
            signal = exact control.signal
            onProviderActivity = exact M4 telemetry callback;

        call exactly once:

        adapter.invoke(
          exact PiM4DependencyInvocationRequestV1
        )

        There MUST be no await, timer, I/O operation, event-loop yield, or other
        asynchronous boundary between the final signal check and initiating the
        dependency adapter call.

19. Pass the same exact control.signal into the dependency adapter.

20. While live:
        propagate signal
        heartbeat best-effort
        provider activity best-effort

21. Map the exact adapter result only as follows:

        completed-response
        → M4 completed terminal sealing path
        → captured

        technical-failure
        → M4 technical-failure terminal sealing path
        → technical-failure

        ambiguous
        → no terminal marker
        → uncertain

        no fourth execution-domain result exists.

22. M4-A owns every evidence-artifact seal, rawResult seal, terminal-evidence
    seal, terminal journal publication, and CognitiveExecutionCapture
    construction. The adapter returns unsealed facts only and receives no
    CampaignArtifactStore.

23. Never retry inside M4-A v1.
```

There is no automatic duration-based abort.

The final post-`MAYBE-SENT` check closes the local race where execution
authority is revoked while `MAYBE-SENT` is being durably published. If
revocation is observed before dependency invocation, no new provider attempt
may begin.

Because `MAYBE-SENT` is already durable, M4 does not upgrade this fact to
positive nonexecution; it returns uncertainty and leaves recovery conservative.

## 12. Dependency-consumer requirements

`DC-PI-M4-GATE-A-COGNITIVE-EXECUTION` version `1.0.1` provides the consumer
contract satisfying exactly:

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
attempts.

The active Dependency Contract additionally requires:

```text
the adapter receives the exact same execution-owned AbortSignal

if that signal is already aborted when the direct dependency invocation begins,
the adapter starts zero new provider attempts

after signal abort is observed, the adapter starts no later provider attempt

an already-started provider attempt may only be cancelled according to the
dependency's actual cancellation guarantees and remains reconciliation-relevant

with maxRetries = 0, selected v1 never starts a second transport/provider
attempt for the same M4 call
```

For selected v1, every terminal `TechnicalExecutionFailure` eligible to be
projected later as a schema-v3 receipt attempt must satisfy:

```text
transportAttemptCount == 1
```

A zero-transport local or pre-transport condition must not be silently mapped
to a receipt-admissible `TechnicalExecutionFailure`.

The Dependency Contract must establish that the selected realization either:

```text
A. guarantees every accepted terminal no-completed-response technical failure
   has transportAttemptCount == 1;

or

B. exposes any zero-transport outcome distinctly so it cannot be mislabeled as
   a receipt technical-failure attempt.
```

If the pinned Pi/provider realization cannot satisfy A or B under the existing
M4/NIB-S result language, Dependency Contract authoring must stop and route the
construction gap rather than invent a mapping.

Pi source and API details beyond these M4 consumer requirements remain owned by
the active Dependency Contract.

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

```text
caller authority revocation observed before MAYBE-SENT
→ caller AbortController aborts
→ M4 sees signal
→ no cognitive call
→ uncertain direct return after Arm

caller authority revocation observed after MAYBE-SENT but before dependency
invocation
→ final signal check prevents dependency invocation
→ uncertain
→ MAYBE-SENT remains conservative recovery truth

caller authority revocation observed after dependency invocation has begun
→ same signal is propagated to dependency
→ no additional provider attempt may start
→ already-started attempt remains reconciliation concern
→ outcome classification still depends only on durable evidence
```

Abort or revocation never proves nonexecution, provider cancellation, technical
failure, or rollback.

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

`prepare(E,W)` has one immutable logical preparation per exact Execution. Once
`PREPARED` exists, every later prepare occurrence must reuse the exact existing
preparation, dependency plan, and reconciliation operation. It must never derive
divergent preparation material.

Credential availability is an operational observation, not immutable
preparation identity. Every prepare occurrence rechecks the required credential
before returning `kind = "prepared"`.

```text
existing PREPARED + credential available now
→ return exact existing prepared result

existing PREPARED + credential unavailable now
→ operationally-blocked
→ preserve PREPARED unchanged
→ no Arm

existing PREPARED + credential-boundary failure
→ CREDENTIAL-BOUNDARY-FAILURE
```

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

valid lifecycle state proving another invocation/preparation already owns or
crossed an incompatible one-call transition
→ PREPARATION-STATE-CONFLICT

marker or referenced journal material exists but is malformed, corrupt,
identity-mismatched, or represents contradictory terminal truth
→ JOURNAL-INTEGRITY-FAILURE

filesystem/storage operation failed for a reason other than the separately
classified atomic target-already-exists result
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
Provider-owned model evidence is preserved exactly; identifier spelling never
establishes provider-reported resolution.

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

M4A-26
Caller execution-authority revocation is projected to M4-A only through the
exact execution-owned AbortSignal; M4-A never independently infers revocation
from time, heartbeat, or campaign-state polling.

M4A-27
After this invocation durably creates MAYBE-SENT, M4-A rechecks the exact
AbortSignal immediately before dependency invocation and performs no
asynchronous operation between that check and initiating the dependency call.

M4A-28
PREPARED material is immutable and replay-stable, but credential availability
is freshly re-observed on every prepare occurrence before Arm.

M4A-29
An atomic truth-marker target-already-exists result is classified by exact
marker identity/lifecycle rules and is never automatically treated as generic
journal I/O failure.

M4A-30
For selected v1, a TechnicalExecutionFailure eligible to become a schema-v3
receipt attempt has transportAttemptCount == 1; zero-transport outcomes may not
be mislabeled as such an attempt.

M4A-31
Every cognitive reviewer WorkItem operation retains exactly one selected
GateAReviewerAcquisitionCandidateV1.

M4A-32
operation.reviewerProfileId always equals
operation.reviewerAcquisitionCandidate.profileId.

M4A-33
M4-A obtains requested provider and requestModel only from the exact retained
reviewerAcquisitionCandidate and never from reviewerProfileId alone.

M4A-34
A dependencyExecutionPlan may validate but never replace callId,
reviewerProfileId, provider, or requestModel selected by the immutable M4
operation.

M4A-35
For DC-PI-M4-GATE-A-COGNITIVE-EXECUTION 1.1.0, a provider-reported acquisition
candidate is rejected as DEPENDENCY-CONTRACT-VIOLATION before
buildExecutionPlan because
provider-owned-canonical-effective-model-identity-v1 is NOT-ESTABLISHED.

M4A-36
PiM4BuildExecutionPlanRequestV1 remains identity-resolution blind; M4-A never
adds provider-reported admission semantics to the dependency adapter interface.

M4A-37
A completed provider-semantic response remains captured when providerModel is
null, empty, or "latest"; missing usable identity evidence never creates
technical-failure or retry permission.
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

M1 first-round WorkItem construction:
→ exact selected GateAReviewerAcquisitionCandidateV1 from the newly established
  ReviewCampaignPrerequisiteBasisRefV1
→ copied unchanged into CognitiveExecutionOperationV1

M5 later-round WorkItem construction:
→ exact selected GateAReviewerAcquisitionCandidateV1 from
  snapshot.reviewCampaignPrerequisiteBases
→ copied unchanged into CognitiveExecutionOperationV1

Neither may construct only `reviewerProfileId` and later ask M4 to recover the
remaining profile data.

M8
→ owns recovery classification/operator boundary
→ never reimplements M4 journal/domain proof meaning
```

For every live armed cognitive Execution, M1 owns exactly one `AbortController`
used for the execution-owned M4 control signal.

M1 passes `controller.signal` as `CognitiveExecutionControlV1.signal`.

M1 aborts that exact controller whenever it observes caller execution authority
for that exact Execution has been revoked.

At minimum, an authoritative `ExecutionProgressionSupersessionRef` naming the
Execution as `priorExecutionId` is such a revocation of future progression and
recovery authority and must not permit a new provider attempt.

M1 also uses that signal for explicit caller shutdown or cancellation.

M4-A does not inspect campaign state to discover revocation itself. The future
M1 Module Brief owns the exact orchestration mechanisms by which these authority
events are observed and translated into `AbortController.abort()`.

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

Active dependency contract:

```text
DC-PI-M4-GATE-A-COGNITIVE-EXECUTION
version 1.1.0
docs/formal/dependency-contract-pi-m4-cognitive-execution.md
```

The active DC 1.1.0 closes these requirements for the selected v1 Pi backend.

It satisfies every requirement in Section 12 and additionally closes:

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
exact provider-reported identity capability status for the selected realization
exact provider-owned providerModel extraction and preservation
exact qualification evidence required before
provider-owned-canonical-effective-model-identity-v1 may be reported as
ESTABLISHED
fail-closed consumer behavior when
provider-owned-canonical-effective-model-identity-v1 is NOT-ESTABLISHED
proof that providerModel is not substituted from requestModel or Pi
high-level normalization
exact textual completion extraction
exact transportAttemptCount definition
exact terminal-no-completed-response facts
exact ambiguous failure mapping
known provider-normalization limitations
selected backend recovery limitation
```

Dependency Contract closure means that the exact realization's capability
status and evidence boundary are determinate.

It does not mean every optional capability is established.

The Dependency Contract must always determine and declare the capability status
of the exact selected realization. Declaring the status does not imply that the
capability is established.

For the active DC 1.1.0:

```text
provider-owned providerModel capture
= ESTABLISHED

canonical-effective identity capability
= NOT-ESTABLISHED
```

The active DC therefore satisfies the M4-A obligation to report the capability
status, but it does not satisfy a provider-reported execution's requirement for
that capability to be `ESTABLISHED`:

```text
DC obligation closed
AND
current provider-reported execution realization inadmissible
```

For a provider-reported execution, M4-A requires the status of
`provider-owned-canonical-effective-model-identity-v1` to be `ESTABLISHED`. A
determinate `NOT-ESTABLISHED` status therefore closes the Dependency Contract
question while making that exact provider-reported realization inadmissible.

A future accepted Dependency Contract realization may report
`provider-owned-canonical-effective-model-identity-v1` as `ESTABLISHED` only
when its qualification evidence establishes that property. M4-A does not define
which future concrete evidence suffices beyond the semantic contract fixed by
ADR-054 and introduces no provider-specific qualification rule.

The contract must also close exactly:

```text
the adapter receives the exact same execution-owned AbortSignal

if that signal is already aborted when the direct dependency invocation begins,
the adapter starts zero new provider attempts

after signal abort is observed, the adapter starts no later provider attempt

an already-started provider attempt may only be cancelled according to the
dependency's actual cancellation guarantees and remains reconciliation-relevant

with maxRetries = 0, selected v1 never starts a second transport/provider
attempt for the same M4 call
```

For selected v1, every terminal `TechnicalExecutionFailure` eligible for later
schema-v3 receipt projection must have `transportAttemptCount == 1`. A
zero-transport local or pre-transport condition must not be silently mapped to
a receipt-admissible `TechnicalExecutionFailure`.

The contract must establish either that every accepted terminal
no-completed-response technical failure has `transportAttemptCount == 1`, or
that every zero-transport outcome is exposed distinctly so it cannot be
mislabeled as a receipt technical-failure attempt. If the pinned realization
can establish neither under the existing M4/NIB-S result language, Dependency
Contract authoring must stop and route the construction gap rather than invent a
mapping.

The Pi Dependency Contract receives exact:

```text
callId
reviewerProfileId
provider
requestModel
```

from the M4 operation.

The Dependency Contract may validate support but must not:

```text
resolve reviewerProfileId through configuration
choose another provider
choose another requestModel
fall back to a Pi default model
replace unsupported model with another catalog model
infer provider/model from environment
use Pi's model catalog as reviewer-profile authority
```

An unsupported exact binding must fail closed under the Dependency Contract.

The M4 NIB does not implement those Pi facts itself.

The Pi-specific Dependency Contract prerequisite for M4-A is satisfied by
`DC-PI-M4-GATE-A-COGNITIVE-EXECUTION` 1.1.0.

This does not itself authorize GREEN before the remaining construction sequence
is complete.

## 26. Provider-reported identity realization boundary

ADR-054 resolves the semantic meaning of provider-reported.

M4-A owns no identifier-string classification. The selected Dependency Contract
owns realization capability status.

Current DC 1.1.0 status:

```text
provider-owned-canonical-effective-model-identity-v1
= NOT-ESTABLISHED
```

Therefore current provider-reported candidates fail closed as
`DEPENDENCY-CONTRACT-VIOLATION` before `buildExecutionPlan`. M4-A calls no
adapter operation, seals no dependency execution plan, publishes no PREPARED,
creates no Arm, and invokes no provider.

M4-A never invents `providerModel`, substitutes `requestModel`, normalizes an
unresolved alias into a fabricated version, or uses Pi high-level requested-
model echoes as provider-owned evidence.

If a later accepted realization establishes the capability and an executed
completed semantic response nevertheless has `providerModel` null, empty, or
`"latest"`, M4 preserves the captured completed response. M4 does not relabel
it technical-failure and does not retry. M5 owns assurance progression
handling.
