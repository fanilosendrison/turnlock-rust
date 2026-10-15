---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-15"
step_id: 2
id: NIB-M-GATE-A-ORCHESTRATOR
version: "1.0.0"
scope: gate-a-campaign-runner/orchestrator
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Orchestrator

## 1. Status, authority, and purpose

Implement M1 `orchestrator` according to this active Module Brief.

Consume exactly:

```text
NIB-S-GATE-A-CAMPAIGN-RUNNER 13.0.1
NIB-M-GATE-A-CONTRACTS 1.5.0
NIB-M-GATE-A-CAMPAIGN-STATE-PERSISTENCE-OWNERSHIP 3.0.4
NIB-M-GATE-A-CAMPAIGN-STATE-MUTATION-EXECUTION 9.1.0
NIB-M-GATE-A-CAMPAIGN-STATE-SNAPSHOT-INTEGRITY 8.1.0
NIB-M-GATE-A-CAMPAIGN-AUTHORITY 4.0.1
NIB-M-GATE-A-COGNITIVE-EXECUTION-CAPTURE 2.1.1
NIB-M-GATE-A-COGNITIVE-EXECUTION-RECOVERY-OBSERVATION 1.1.0
NIB-M-GATE-A-ASSURANCE-LEDGER-CAMPAIGN-WORK-EXECUTION-RECEIPT 3.1.0
NIB-M-GATE-A-ASSURANCE-LEDGER-FINDING-ADJUDICATION 1.1.0
NIB-M-GATE-A-ASSURANCE-LEDGER-RESOLUTION-QUALIFICATION 1.1.0
NIB-M-GATE-A-ASSURANCE-LEDGER-REPOSITORY-PROJECTION-READINESS 1.1.0
NIB-M-GATE-A-MECHANICAL-VALIDATION 1.2.0
NIB-M-GATE-A-REPOSITORY-CONTROL-MATERIALIZATION-CANDIDATE-CONSTRUCTION 2.1.1
NIB-M-GATE-A-REPOSITORY-CONTROL-PUBLICATION-REMOTE-RECOVERY 1.0.0
NIB-M-GATE-A-RECOVERY-OPERATOR-RECONCILIATION 2.1.0
NIB-M-GATE-A-RECOVERY-OPERATOR-BOUNDARY 2.1.0
```

This brief is implementation-construction authority only. It creates no TURNLOCK
product semantic, hostile-review protocol semantic, formal semantic, assurance
claim, verification evidence, ADR, dependency behavior or protocol activation.

Preserve exactly:

```text
P6 = current
P7 = permanently inactive
P8 = inactive until C15
```

M1 contains the fully specified P8 lane for future activation but must make that
lane unreachable while P6 is current. Construction availability is not protocol
activation.

## 2. Responsibility and no-semantic-discretion boundary

M1 is choreography only. It owns:

```text
CLI parsing and invocation dispatch
runtime composition
start/resume sequencing
one-process RunnerSession occurrence identity
recovery barrier sequencing
fresh-snapshot orchestration loop
deterministic selection among already-enabled WorkItems
cross-module call sequencing
pre-effect currentness revalidation
execution-owned AbortController lifecycle
normal RunnerResult projection from final authoritative state
```

M1 chooses none of:

```text
M1 chooses no campaign semantic.
M1 chooses no semantic answer.
M1 chooses no protocol branch.
M1 chooses no retry permission.
M1 chooses no repair.
M1 chooses no Decision Required condition.
M1 chooses no blocker identity.
M1 chooses no publication predecessor/successor.
M1 chooses no recovery classification.
M1 chooses no QLEK.
M1 chooses no Admission.
```

M1 transports exact products from their owning modules. It never interprets a
mechanical result beyond its closed discriminant, parses arbitrary P8 semantic
JSON for meaning, reconstructs an M5 semantic request, or substitutes its own
branch selection.

## 3. Runtime composition

Define exactly:

```ts
interface GateAOrchestratorRuntimeConfigV1 {
  readonly stateRoot: string;
  readonly journalRoot: string;
  readonly pythonExecutable: string;
  readonly heartbeatIntervalMs: 5000;
}
```

Resolve `stateRoot` exactly:

```text
if TURNLOCK_GATE_A_STATE_ROOT exists:
    require non-empty absolute path
    use it exactly

otherwise:
    path.join(os.homedir(), ".turnlock", "gate-a", "state")
```

Resolve `journalRoot` exactly:

```text
if TURNLOCK_GATE_A_JOURNAL_ROOT exists:
    require non-empty absolute path
    use it exactly

otherwise:
    path.join(
      os.homedir(),
      ".turnlock",
      "gate-a",
      "cognitive-journal"
    )
```

`TURNLOCK_GATE_A_PYTHON` is required and must resolve to a non-empty executable
path. Add no CLI flag and select no fallback Python executable.

Set:

```text
heartbeatIntervalMs = 5000
```

This is a fixed telemetry-only construction constant and creates no liveness,
timeout, recovery or execution truth.

Require before composition:

```text
stateRoot != journalRoot
neither root is inside candidate repository/worktree
both roots are durable and writable
```

Reject lexical equality and resolved filesystem containment. Do not normalize a
configured root into a different authority-domain identity.

The default state root is deliberately user-global rather than repository-local
so GateARuns in the same configured domain can reuse exact protocol-v8 semantic
Admissions. Different explicitly configured state roots remain separate M2
authority domains under existing M2 rules.

## 4. RunnerSession occurrence identity

One process invocation creates exactly one `RunnerSessionId`:

```text
SESSION-<lowercase UUIDv4>
```

Generate the UUID with Node cryptographic UUID support. Validate UUID version and
variant. This is occurrence identity, not `deriveId` identity, semantic identity,
QLEK input, provider identity or persisted semantic input.

## 5. Root-preflight artifact

At composition M1 seals through the existing `CampaignArtifactStore` the exact
M0 bytes:

```text
{"kind":"root-preflight","schema":"gate-a-root-preflight-obligation-definition.v1"}
```

Require before bootstrap:

```text
UTF-8 byte length = 83
SHA-256 = 595cd152405f868a67fc9dce8b00767700c2273777873c944a7596f1d382be3b
mediaType = application/json
repositoryPath = null
```

M1 verifies the returned `ArtifactRef` byte length, digest, media type and null
repository path and supplies only that exact reference to M2 bootstrap. It does
not reconstruct alternative JSON or accept an equivalent parsed object.

## 6. CLI and process result

Preserve exactly these command forms:

```text
run-gate-a-review start --repository <path>

run-gate-a-review resume \
  --repository <path> \
  --run-id <GateARunId>

run-gate-a-review resume \
  --repository <path> \
  --run-id <GateARunId> \
  --operator-resolution <path>
```

No other form exists. Reject duplicate flags, unknown flags, positional extras,
missing values and interactive input. Never prompt.

A normal contract outcome writes exactly one serialized `RunnerResult` to
stdout and exits zero. Diagnostics go only to stderr. Implementation, process,
integrity, configuration and coordination failures exit non-zero and emit no
fabricated `RunnerResult`.

## 7. Start and resume bootstrap choreography

Use the exact NIB-S section 37 order.

### 7.1 Start

```text
M2 create run + initial ownership
→ M7 inspect repository
→ M6 derive S
→ M6 project review authority
→ M3 preflight
→ M2 EstablishPreflightV1
→ M2 AdmitCandidateV1(C0)
```

M1 transports exact products only. It does not derive repository authority,
subject, protocol, campaign authority, C0 bytes or preflight blockers.

### 7.2 Resume

```text
read exact run/revision
→ M2 acquire write ownership
→ optional M8-B operator resolution validation
→ M2 admit exact operator resolution effect
→ reconstruct root-preflight state
→ resume incomplete bootstrap if required
→ otherwise recovery barrier
```

For ownership acquisition:

```text
read-only load exact current StateRevision
then call acquireWriteOwnership with that exact revision
then discard the pre-acquisition snapshot
use only the snapshot returned by successful ownership acquisition
```

`ACTIVE_OWNER_CONFLICT` and stale acquisition are non-zero invocation failures.
Never create another run as fallback.

Incomplete bootstrap follows NIB-S exactly. Before preflight establishment,
rerun repository inspection, subject derivation, authority projection and M3
preflight only while the root-preflight obligation remains outstanding and no
operational blocker remains. After `EstablishPreflightV1` but before C0, use the
exact retained preflight authority and sealed baseline; do not reread or retarget
mutable repository state.

## 8. Recovery barrier

Before ordinary progression call:

```text
reconcile_prior_sessions
```

over the complete exact current unresolved-Execution list and complete
outstanding operational-blocker list.

M8 classifies every position. One legitimately blocked position does not prevent
classification of later positions.

Admit plan positions in exact unresolved-Execution order. For each position:

```text
use current M2 StateRevision for that commit
commit exactly the M8-provided resolution/pending/blocker/disposition
reload the committed snapshot before any non-recovery orchestration
```

Do not alter a blocker disposition. M8 recovery identities and dispositions are
Execution-scoped; `StateRevision` is not recovery identity. M1 transports the
exact plan product without rewriting meaning.

After all positions:

```text
reload authoritative snapshot

if recovery blocker remains outstanding
→ OPERATOR-ACTION-REQUIRED

if unresolved execution remains without lawful pending/recovery representation
→ integrity failure

otherwise
→ ordinary progression may continue
```

## 9. Fresh-authority main-loop barrier

Every iteration begins from one fresh trustworthy `GateARunSnapshot`. No cached
snapshot remains authoritative after an M2 mutation.

After every mutation that can change progression eligibility, use the exact
committed snapshot or reload, discard prior derivation products, and restart
derivation. Never perform two semantic phase transitions from one pre-mutation
snapshot.

Require these barriers:

```text
admit receipts
→ fresh snapshot
→ derive next acquisition round

admit semantic result
→ fresh snapshot
→ derive next semantic phase

admit candidate
→ fresh snapshot
→ resolve currentness

admit qualification
→ fresh snapshot
→ prepare publication

admit publication observation
→ fresh snapshot
→ post-publication validation / terminality
```

A stale-state rejection discards any pure preparation and restarts. It never
replays an external effect.

## 10. Deterministic scheduler

M1 is single-step deterministic. Select no concurrency in v1 for Gate A runner
WorkItem execution.

Never schedule by wall-clock time, completion time, provider speed, cost, model
preference, finding severity, confidence, filesystem enumeration, incidental
Map/Set order or randomness.

Use exact progression priority:

```text
1. mandatory recovery / exact already-captured execution truth

2. exact M2 protocol-v8 validation/reconciliation work that must precede any
   same-QLEK sample

3. M5 deterministic derivation and admission of already-available facts,
   receipts, findings, adjudications, blockers, retry authorizations,
   projection/readiness facts

4. exact candidate materialization already authorized by retained RepairIntent
   and/or AssuranceRepositoryProjection

5. externally effectful cognitive WorkItem execution

6. Gate A mechanical qualification for exact CandidateReviewReadiness

7. publication preparation / publication WorkItem

8. post-publication validation / Gate A ready
```

Within simultaneously enabled ordinary cognitive WorkItems, choose
`WorkItemId` by unsigned ASCII ascending. This order is scheduling only and
changes no acquisition semantic. M5-D still serializes initial-review campaign
evidence by reviewer-acquisition selection order, never completion order. M5-C
still permits at most one selected semantic finding progression.

## 11. First reviewer round

M1 owns first-round selection but no reviewer-policy semantic. Implement exactly
the M5-A `derive_acquisition_round` algorithm.

For the first round:

```text
E = empty effective identity set
alreadySelectedProfiles = empty
```

Use exact M3-retained `minimumIndependentReviewers` and
`reviewerAcquisitionCandidates`:

```text
deficit = N - |E|

pinned candidate:
  skip when effective (provider, requestModel) already reserved/effective

provider-reported candidate:
  do not pre-collapse
  do not guess effective model identity

preserve candidate order
stop at deficit or pool exhaustion
```

Pass the exact selected candidates to
`M5-A construct_initial_reviewer_campaign_work`. M5-A recomputes and validates
exact equality. M1 has no fallback profile selection. Later rounds are M5-A
owned and derive from authoritative receipts.

## 12. Ordinary cognitive execution lane

For one exact enabled cognitive WorkItem, derive the lawful
`ExecutionCreationRequestBasis` only through existing M2/M5 facts. The closed
basis set remains:

```text
initial-work
protocol-retry
proven-not-executed
```

M1 never invents retry or replacement permission.

Sequence exactly:

```text
M2 authorize Execution
M4 prepare
```

If M4 preparation is operationally blocked, pass its exact producer cause to
M8-B, admit the exact resulting blocker through M2, and stop ordinary
progression.

Otherwise:

```text
fresh currentness / authority revalidation
M2 Arm
construct exact CognitiveExecutionRequest only from:
  prepared requestTemplate
  exact ArmedExecutionDispatchRef
create execution-owned AbortController
M4 execute with exact execution-owned AbortSignal
```

If exact live authority is revoked before the external-effect boundary, abort
that controller under existing M4 rules.

Admit known terminal direct outcome through `AdmitExecutionOutcomeV1`. For an
uncertain outcome, admit exact M2 uncertainty enrichment, invoke exact M8
recovery and never replay the same external effect.

After any authoritative captured cognitive completion, route through the exact
P6 or inactive-P8 validation lane selected by current protocol authority.

## 13. Current P6 validation lane

P6 remains current. For a P6 completed cognitive response:

```text
reconstruct exact CognitiveExecutionRequest
M6 validate_cognitive_attempt
M5 consumes exact CognitiveAttemptValidationResult
M5 decides existing retry/receipt behavior
M2 admits exact M5 delta
```

Technical failure creates no M6 cognitive-attempt validation request. Preserve
all schema-v3 receipt behavior unchanged.

## 14. Protocol-v8 reuse-first lane — inactive until C15

This lane is fully specified but unreachable while P6 is current. M1 must not
select it from artifact availability or construction completion.

For one M5 `resolve-semantic-question` plan with exact validated K, call:

```text
M2 acquireAdmissionAuthority(K, session)
```

Handle every closed result exactly as follows.

### 14.1 `reuse`

Perform zero WorkItem, zero Execution and zero model call. Supply the exact
Admission to the M5-D broker. M5 requests the exact M6 progression-view
projection; M1 performs exactly that M6 call and returns the result unchanged to
M5. Restart M5 planning. M1 never inspects the semantic value and transfers no
receipt ownership.

### 14.2 `reconciliation-required`

Process the exact returned completion order. For each exact completion, call M2
T4 `ReconcileSemanticCompletion`.

```text
admitted/converged
→ restart T1/planning from fresh semantic state

busy
→ non-zero transient semantic coordination contention

conflict
→ non-zero semantic-admission integrity/conflict
```

Never choose a winner or sample again.

### 14.3 `validation-required`

Process exact returned Execution-locator order. For each locator:

```text
obtain owning-run WriteAuthority non-blocking when required
load exact GateAExecutionHistoryViewV1
require exact captured result
require exact reconstructed ArmedExecutionDispatchRef
call M4 prepare read-only/replay path for exact WorkItem/Execution
reconstruct exact CognitiveExecutionRequest without provider replay
load exact SemanticExecutionStateV1
reconstruct exact M5 protocol-v8 closure
M6 Stage A
```

If Stage A is `protocol-invalid`:

```text
M2 AdmitProtocolV8SemanticValidationV1
fresh snapshot
M5-A prepare_protocol_v8_attempt_contribution
admit exact retry/stop consequence if any
restart T1
```

If Stage A is `protocol-valid-candidate`:

```text
M5-A prepare_protocol_v8_completion_package
M6 Stage B
M2 AdmitProtocolV8SemanticValidationV1
M2 T4
fresh semantic state
restart T1
```

Never discard or replace the captured result. If the owning GateARun lock is
active elsewhere, fail non-zero as transient owner contention. Never create a
sibling same-K Execution.

### 14.4 `hazard-blocked`

Never sample K. For one exact local armed hazard, use the returned owning
run/execution, acquire that run's WriteAuthority non-blocking, route exactly that
Execution through M8 recovery, then restart T1 after authoritative recovery
progression. A busy owning run fails non-zero.

An imported/external unresolved semantic hazard without a local recovery
transition fails non-zero as unresolved external semantic hazard. M1 fabricates
no OAR, Decision Required or clearance.

### 14.5 `conflict`

Fail non-zero as semantic-admission conflict. Choose no winner, retry, sample or
local blocker.

### 14.6 `busy`

Fail non-zero as transient QLEK coordination contention. Do not spin and do not
create another QLEK acquisition path.

### 14.7 `acquired`

If `state.resumableUnarmedExecution != null`, create no WorkItem or Execution.
Acquire exact owning-run WriteAuthority non-blocking. If busy, release the exact
AdmissionAuthority and fail non-zero. If acquired, resume the exact existing
unarmed semantic Execution.

If no resumable trajectory exists:

```text
M6 project_protocol_v8_semantic_execution_inputs
M5 construct exact semantic WorkItem
M5 delta admission
fresh snapshot
M2 T2 AuthorizeSemanticExecutionV1
```

Never combine WorkItem and Execution admission through a shortcut. If the M5
delta cannot be admitted, release the exact live AdmissionAuthority before
abandoning the T1 attempt.

For both fresh T2 and resumed unarmed execution:

```text
M4 prepare
fresh currentness
M2 T3 ArmSemanticExecutionDispatchV1
```

M2 releases the QLEK lock under its existing contract after successful T3.
Continue exactly:

```text
M4 execute
→ exact outcome admission/recovery
→ Stage A
→ M5 package
→ Stage B
→ M2 validation
→ T4
```

No P8 branch samples before validation, reconciliation and hazard clearance
requirements are satisfied.

## 15. Candidate materialization

M1 never constructs candidate bytes. When authoritative state contains an
applicable unconsumed `RepairIntentRef` and/or
`AssuranceRepositoryProjectionRef`, call the exact M7-A boundary with the exact
current candidate as source.

Permit only:

```text
repair-only
assurance-only
repair + assurance
```

M7-A returns the exact sealed successor. For a repair-containing successor,
obtain the exact M6 subject derivation required by existing authority. For an
assurance-only successor preserve the exact subject as M2 already requires.
Commit exact `AdmitCandidateV1`, then reload authoritative state.

Never rebase or retarget a RepairIntent/projection and never reuse a consumed
one.

## 16. Complete M5 delta loop

On each fresh current candidate/evaluation context call:

```text
M5 prepare_complete_delta
```

For each operational-blocker request, call M8-B materialization exactly in
returned order. Then call `M5 finalize_complete_delta` and commit one exact
`AdmitAssuranceLedgerDeltaV1`.

If preparation is a complete no-op, submit no mutation. On stale state, discard
preparation, reload and rederive from scratch. Never replay an external effect
because a pure M5 preparation became stale.

For P8 semantic progression use only M5-D
`plan_protocol_v8_progression`. M1 executes the returned exact mechanical
request, invokes T1 only for an exact `resolve-semantic-question`, or finalizes
an exact `complete-preparation`. It makes no semantic branch decision.

## 17. Gate A qualification

When exact `CandidateReviewReadinessRef` exists, call M6
`validate_gate_a_qualification` and commit the exact mechanical observation
first.

### 17.1 `passed == false`

Call M6 `derive_gate_a_qualification_failure_requirement`. Pass the exact cause
to M8-B for blocker/OAR materialization and call M2
`EstablishOperationalBlockersV1` with:

```text
obligationsToAdd = [exact dedicated obligation]
  iff not already authoritative
  otherwise []
blockers = [exact materialized blocker]
basisArtifacts = orderedUnique(cause descriptor followed by cause basis)
```

Return `OPERATOR-ACTION-REQUIRED` projection. Infer no M5 repair, Decision
Request, semantic fact or automatic revalidation loop.

### 17.2 `passed == true`

Construct the exact `GateAQualificationRef` mechanically:

```text
candidateId = exact validation candidate
currentReviewCampaignIds = exact validation result list
contributingReviewCampaignIds = exact validation result list
validatorEvidence = exact validation evidence

qualificationId =
deriveId(
  "gate-a-qualification.v1",
  runId,
  candidateId,
  reviewReadiness.reviewReadinessId,
  decimal validatorEvidence.length,
  validatorEvidence[0].sha256,
  validatorEvidence[1].sha256,
  ...
)
```

Keep SHA components lowercase as supplied. The universal M0 renderer returns:

```text
GATE-A-QUALIFICATION- + 64 uppercase hexadecimal characters
```

Require the exact lexical form:

```text
^GATE-A-QUALIFICATION-[0-9A-F]{64}$
```

M1 assigns no semantic meaning to `passed`. Commit exact
`AdmitGateAQualificationV1`, then reload.

## 18. Publication lane

Consume only M7-B `1.0.0` algorithms. M1 never selects P, T, realization,
fast-forward truth or replacement authority.

### 18.1 Preparation

Call exact M7-B publication preparation.

Blocked:

```text
M7-B supplies blocking obligation + repository-control cause
M8-B materializes blocker
M2 co-admits obligation + blocker
return OAR
```

Prepared:

```text
M2 EstablishPublicationIntentV1
fresh snapshot
```

### 18.2 Already current

Use M7-B fresh already-current observation with no Execution.

```text
confirmed
→ M2 exact confirmation admission

blocked
→ exact M8-B/M2 blocker path

stale
→ reload
→ fresh preparation
```

### 18.3 Conditional remote update

Use the exact repository-control WorkItem:

```text
M2 authorize
M7-B pre-Arm revalidation
M2 Arm
M7-B publish_conditionally exactly once
```

Admit a direct exact captured result through `AdmitExecutionOutcomeV1`. On
uncertainty, admit M2 uncertainty, invoke M8 recovery and never replay
publication.

Before `qualify_publication_observation`, call M2
`loadExecutionHistoryView` and pass exactly its authoritative origin:

```text
direct-execution
or
recovered-execution
```

Never infer origin from payload equality. `not-applied` is legal only for
`direct-execution` under existing M7-B/M2 rules.

## 19. Post-publication validation

After exact authoritative confirmation/published view, call M6
`validate_post_publication_integrity` and commit the exact mechanical validation
observation.

If `passed == false`, call
`derive_post_publication_integrity_failure_requirement`, materialize through
M8-B, atomically co-admit the dedicated obligation/blocker through M2, and
return OAR. Do not retry validation, republish, rewrite candidate or create a
Decision Request.

If `passed == true`, commit exact `EstablishGateAReadyV1` with:

```text
exact GateAQualificationId
exact PublicationConfirmationId
exact passing post-publication validation basis
```

Reload the final snapshot.

## 20. RunnerResult projection

Derive a normal result only from one fresh exact authoritative snapshot. Before
serialization call M2 `materializeProvenanceRoot` for the exact final run
revision.

Use exact precedence:

```text
if exact Gate A ready fact exists
AND exact qualification exists
AND exact publication confirmation exists
AND exact bound post-publication validation passed
AND no blocker remains

→ GATE-A-READY

else if any outstanding OperationalBlocker exists

→ OPERATOR-ACTION-REQUIRED

else if one or more SemanticBlockers exist

→ DECISION-REQUIRED

else

→ implementation/integrity failure
```

For OAR, set `operatorRequests` to every exact M8-B `operatorRequest` in
authoritative blocker order and preserve coexisting semantic blockers. For
Decision Required, use only exact M5-owned `DecisionRequestRef.request`
artifacts. M1 writes no semantic request text.

## 21. Abort/controller lifecycle

M1 owns one `AbortController` per live armed cognitive Execution and passes its
exact signal to M4-A.

Immediately abort when authoritative state says the caller no longer has
authority to begin or continue new external work for that Execution, including
all existing M4 revocation conditions.

Before closing process-owned run resources:

```text
abort every live execution-owned controller
await every live M4-A execute invocation to settle
only then close process/session ownership resources
```

Abort is not execution truth. M4/M8 remain execution/recovery truth owners.

## 22. Failure taxonomy

Normal outcomes are only:

```text
GATE-A-READY
DECISION-REQUIRED
OPERATOR-ACTION-REQUIRED
```

These are non-zero invocation failures and never normal `RunnerResult` values:

```text
invalid CLI shape
invalid runtime configuration
missing TURNLOCK_GATE_A_PYTHON
state/journal root overlap
state/journal root inside candidate repository
M2 integrity failure
stale resume ownership acquisition
active run-owner contention
QLEK coordination busy
cross-run semantic owner contention
semantic Admission conflict
unresolved external semantic hazard
M5/M6 transcript mismatch
M6 implementation/integrity/dependency failure
M7 impossible dependency result
artifact integrity failure
invalid authoritative history
unexpected closed-union result
```

Do not create a CampaignBlocker to convert implementation failure into a normal
outcome.

## 23. Restart, interruption, and idempotence

Restart always begins with resume ownership acquisition, fresh authoritative
state and the recovery barrier. Reconstruct pure plans from authority; never
persist M1 scheduler cursor, M5 broker transcript or cached semantic phase.

Use M2 historical Execution view for captured-completion reconstruction. Use M4
read-only/replay preparation only to reconstruct exact request material; never
invoke the provider during reconstruction. Use M8 for every unresolved armed
Execution.

Idempotent exact authoritative products become no-ops only through owning-module
contracts. Incompatible same identity, stale authority, unknown union branch or
contradictory history fails closed.

## 24. Required invariants

```text
M1-01
M1 never invents a WorkItem.

M1-02
M1 executes only WorkItems/continuations mechanically authorized by current
authority.

M1-03
Scheduler order never changes semantic meaning.

M1-04
Every authoritative mutation is based on one fresh exact StateRevision.

M1-05
After any progression-changing mutation, M1 re-enters derivation from fresh
authoritative state.

M1-06
M1 never retries external work without exact existing retry/replacement
authority.

M1-07
An Armed external effect is never replayed as the same Execution.

M1-08
Recovery precedes ordinary progression.

M1-09
M1 never treats technical failure as semantic result.

M1-10
M1 never treats semantic failure/exhaustion as technical failure.

M1-11
P8 exact Admission reuse precedes any same-QLEK provider dispatch.

M1-12
A validation-required exact completion is processed before any same-QLEK fresh
sample.

M1-13
A reconciliation-required protocol-valid completion is reconciled before any
same-QLEK fresh sample.

M1-14
A semantic hazard never authorizes another same-QLEK Execution.

M1-15
A SemanticAdmissionConflict never gets a scheduler-selected winner.

M1-16
Cross-run/root semantic reuse transfers no receipt ownership.

M1-17
M1 never computes QLEK, SemanticValueId, FactId or QualificationKey.

M1-18
M1 never parses arbitrary P8 semantic JSON for meaning.

M1-19
M1 never selects the semantic next question; M5 does.

M1-20
M1 never selects P/T publication authority; M7 does.

M1-21
M1 never classifies recovery; M8 does.

M1-22
M1 never constructs BlockerId/OAR; M8-B does.

M1-23
M1 never constructs DecisionRequest semantics; M5 does.

M1-24
M1 never declares Gate A ready without exact M2 terminal authority.

M1-25
RunnerResult is always projected from exact final authoritative state.

M1-26
P6 remains current.

M1-27
P7 is never executable.

M1-28
P8 execution lane remains inactive until C15.
```

## 25. Edge cases and forbidden behavior

Fail closed rather than:

```text
using a cached snapshot after mutation
running two WorkItems concurrently
selecting a different reviewer profile
sampling during same-QLEK validation/reconciliation/hazard
copying a reused receipt across roots
inferring direct/recovered origin from equal bytes
inventing an M6 request or M5 predecessor
parsing semantic payload to choose progression
retrying publication
turning busy/conflict/integrity failure into OAR or Decision Required
using filesystem order as scheduler order
choosing fallback Python
placing durable roots under candidate repository
activating P7 or P8
```

A complete M5 no-op causes no mutation. Pool exhaustion, retry exhaustion and
semantic no-continuation use only exact M5-owned consequences. M1 never converts
absence of a continuation into its own blocker.

## 26. Construction-discovery record

C9-H closes four representation seams in their owning briefs:

```text
GateAQualificationId construction
→ M0 1.5.0

historical Arm/direct-vs-recovered read
→ M2 snapshot 8.1.0

P8 M5-to-M6 choreography
→ M5-B/C/D 1.1.0

mechanical qualification-failure blocker
→ M6 1.2.0 + M2 mutation 9.1.0
```

Their recorded dispositions and resolutions create no product semantic and
require no ADR. M1 consumes those exact closures without becoming their owner.

## 27. Construction completeness and GREEN boundary

M1 `1.0.0` closes active Module Brief coverage for the NIB-S module topology.
Complete M0-M8 NIB-M coverage does not make the runner GREEN.

C9 remains open because exactly these required Dependency Contracts are absent:

```text
DC-ZOD-GATE-A-CONTRACTS
DC-GIT-CLI-GATE-A-REPOSITORY-CONTROL
```

C9-I owns their later closure. C10/NIB-T has not begun. Create no production
implementation or tests from this C9-H documentation task.
