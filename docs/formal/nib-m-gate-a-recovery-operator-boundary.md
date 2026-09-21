---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-09-21"
step_id: 2
id: NIB-M-GATE-A-RECOVERY-OPERATOR-BOUNDARY
version: "1.0.0"
scope: gate-a-campaign-runner/recovery-operator/operator-boundary
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Recovery Operator — Operator Boundary

It consumes `NIB-S-GATE-A-CAMPAIGN-RUNNER` version `6.0.8`.

This Module Brief is implementation-construction authority only. It does not
create TURNLOCK product semantics, hostile-review protocol semantics, canonical
formal semantics, or verification evidence.

## 1. Purpose and responsibility boundary

M8 is decomposed exactly as:

```text
M8 recovery-operator
├── M8-A recovery-reconciliation
│   establish mechanically what happened
└── M8-B operator-boundary
    materialize operational consequences
    own blocker identity/presentation
    reconcile blocker lifecycle
    ingest explicit operator resolutions
```

M8-B owns:

```text
all OperationalBlocker identity normalization
all GateAOperatorActionRequestV1 construction/sealing
non-recovery occurrence blocker materialization
M8 recovery causal blocker materialization
outstanding blocker validation/indexing
recovery blocker reuse
recovery blocker disposition
RecoveryPlan blocker aggregation
operator-resolution input ingestion
GateAOperatorResolutionArtifactV1 validation
OperatorResolutionEnvelope construction
OperatorResolutionStateEffect derivation
operator-request projection
```

M8-B does NOT own:

```text
M8-A executor-domain recovery truth
M3 producer-domain cause meaning
M5 assurance semantics
M6 validation truth
M7 repository-domain cause meaning
semantic Decision Request answers
M2 current-state mutation admissibility
successor Execution identity
human product decisions
```

## 2. Consumed contracts and dependencies

M8-B consumes these NIB-S types unchanged:

```text
ArtifactRef
BlockerId
OperationalBlocker
WorkItemRef
ExecutionRef
StateRevision
RecoveryRequest
RecoveryPlan
RecoveryBlockerDisposition
ClassifyUnresolvedExecutionRequest
ClassifyUnresolvedExecutionResult
OperatorResolutionEnvelope
OperatorResolutionStateEffect
OperationalBlockerMaterializationRequestV1
MaterializedOperationalBlockerV1
ValidateOperatorResolutionRequestV1
ValidatedOperatorResolutionV1
GateAOperatorActionRequestV1
GateAOperatorResolutionArtifactV1
NonRecoveryOperationalBlockerProducerV1
RecoveryOperationalBlockerCauseV1
OperatorResolutionContractV1
NonRecoveryOperatorResolutionContractV1
OperatorMechanicalContinuationV1
OperatorBlockerSourceV1
ExecutionRecoveryResolution
ProvenExecutionRecoveryResolution
UnresolvableExecutionRecoveryResolution
ReconciliationPendingRef
```

M8-B consumes M8-A through this exact internal boundary:

```ts
reconcile_unresolved_execution(
  request: RecoveryReconciliationRequestV1,
): Promise<RecoveryReconciliationResultV1>
```

M8-B does not duplicate M8-A observation, validation, re-observation, waiting,
evidence-projection, trace, or failure algorithms.

M8-B consumes `CampaignArtifactStore` for immutable artifact sealing and
verification.

## 3. Canonical runner JSON

M8-B uses the deterministic runner-owned JSON serializer already selected for
M8-A:

```text
UTF-8 JSON
object keys recursively lexicographically sorted
array order preserves exact semantic order
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

It uses this serializer for:

```text
GateAOperatorActionRequestV1
```

It uses it for no operator-authored input. Operator-authored resolution bytes
are never rewritten by this serializer.

## 4. Non-recovery operational-blocker materialization

The public boundary is:

```ts
materialize_operational_blocker(
  request: OperationalBlockerMaterializationRequestV1,
): Promise<MaterializedOperationalBlockerV1>
```

For `request.kind == producer-occurrence`, M8-B executes exactly:

```text
validate runId
validate producer is non-recovery closed union
validate obligationId
validate optional workItemId/executionId structural shape

verify causeDescriptor ArtifactRef
require causeDescriptor.mediaType == application/json

validate resolutionContracts duplicate-free

reject authorize-uncertain-execution-replacement

for every authorize-known-terminal-execution-replacement:
    require executionId != null
    require contract.priorExecutionId == executionId

canonicalize resolutionContracts order:
    request-operational-recheck
    then authorize-known-terminal-execution-replacement

derive exact workItemComponent
derive exact executionComponent

derive BlockerId using NIB-S formula

construct exact GateAOperatorActionRequestV1:
    schema = gate-a-operator-action-request.v1
    exact runId
    exact blockerId
    exact obligationId
    exact workItemId
    exact executionId

    source = {
        kind: producer-occurrence,
        producer,
        causeDescriptor,
        baseStateRevision
    }

    mechanicalContinuations = []

    resolutionContracts =
        exact canonicalized contracts

runtime-validate OAR
canonical serialize
sealRunnerArtifact(application/json)
verify returned ArtifactRef

construct:
OperationalBlocker {
    kind: operational,
    blockerId,
    obligationId,
    executionId,
    operatorRequest
}

return exact blocker
```

M8-B does not inspect producer-domain cause-descriptor semantics beyond the
accepted producer contract and common `ArtifactRef` integrity.

## 5. Recovery causal blocker materialization

For `request.kind == recovery-causal`, M8-B requires and derives:

```text
require request.execution.workItemId ==
        request.workItem.workItemId

require request.workItem.runId == request.runId

require sourceObligationIds non-empty

obligationId = workItem.sourceObligationIds[0]

workItemId = workItem.workItemId
executionId = execution.executionId

derive stable recovery BlockerId using NIB-S formula
```

M8-B constructs the exact recovery OAR from the NIB-S cause matrix.

It does not include any of these values in the OAR bytes:

```text
traceRef
ReconciliationPendingRef
StateRevision
ownership generation
episode number
timestamp
last observation
```

M8-B runtime-validates the OAR, canonical-serializes it once, seals it once as a
runner-owned `application/json` artifact, verifies the returned `ArtifactRef`,
and returns the exact `OperationalBlocker`.

## 6. Outstanding blocker validation and indexing

M8-B validates the complete ordered outstanding `OperationalBlocker` list.

For every blocker it executes:

```text
verify blocker.operatorRequest ArtifactRef
read exact OAR bytes
runtime-validate GateAOperatorActionRequestV1

require:
    OAR.runId == current runId
    OAR.blockerId == blocker.blockerId
    OAR.obligationId == blocker.obligationId
    OAR.executionId == blocker.executionId
```

For `source.kind == producer-occurrence`:

```text
verify causeDescriptor ArtifactRef
recompute occurrence BlockerId
require exact equality
```

For `source.kind == recovery-causal`:

```text
require producer == recovery-operator
require workItemId != null
require executionId != null
recompute stable recovery BlockerId
require exact equality
validate exact recovery continuation/resolution contract for cause
```

Any malformed retained OAR, missing artifact, corrupt artifact, binding
mismatch, or recomputed-ID mismatch is:

```text
OPERATIONAL-BLOCKER-INTEGRITY-FAILURE
```

It is not a new blocker and not operator input error.

M8-B indexes recognized recovery blockers by `executionId` and requires:

```text
at most one outstanding recovery-causal blocker per Execution
```

Non-recovery blockers may coexist for the same Execution.

## 7. Recovery classification order

For one supplied unresolved `U`:

```text
existingRecoveryBlocker =
    indexed recovery blocker for U.execution.executionId
```

Before invoking M8-A:

```text
if existing cause == no-recovery-capability:
    fail integrity

if existing cause == executor-domain-indeterminacy:
    fail integrity

if existing cause == pending-policy-exhausted:
    require exact OAR/U binding:
        runId
        workItemId
        executionId
        obligation anchor
    require U.recoveryCapability != null
    continue

if no existing recovery blocker:
    continue
```

M8-B then invokes M8-A exactly once and applies the exact NIB-S recovery
transition matrix.

## 8. Conversion of M8-A indeterminate results

For:

```text
M8-A result =
indeterminate / no-recovery-capability
```

M8-B constructs the exact recovery blocker with:

```text
cause = no-recovery-capability
```

It then constructs:

```ts
UnresolvableExecutionRecoveryResolution {
  executionId: exact executionId,
  classification: "UNRESOLVABLE",
  blocker: exact materialized blocker,
  evidence: exact M8-A indeterminate evidence,
}
```

M8-B uses the existing NIB-S shape and does not fabricate a
`RecoveryIndeterminacyRef`.

For:

```text
M8-A result =
indeterminate / executor-domain-indeterminacy
```

M8-B constructs the exact recovery blocker with:

```text
cause = executor-domain-indeterminacy
```

It constructs the exact `UNRESOLVABLE` resolution using the exact M8-A
evidence.

For:

```text
M8-A result =
pending-policy-exhausted
```

M8-B materializes or reuses:

```text
cause = pending-policy-exhausted
```

and returns:

```text
resolution = null
lastPending = exact pending
```

## 9. Pending blocker reuse

When pending exhaustion occurs:

```text
expectedId =
stable pending recovery BlockerId
```

If no exact current blocker exists, M8-B materializes a new exact `B_pending`.

If exact valid `B_pending` already exists:

```text
reuse exact existing OperationalBlocker
do not reseal a replacement OAR
blockerIdsToDispose = []
```

A fresh pending episode may have a new `ReconciliationPendingRef` and
`traceRef` without changing the blocker or OAR.

## 10. Recovery blocker disposition

M8-B alone computes recovery blocker dispositions according to this exact
matrix:

```text
existing none + PNE
→ []

existing none + PC
→ []

existing none + pending
→ []

existing none + no capability
→ []

existing none + domain indeterminate
→ []

existing B_pending + PNE
→ [B_pending.blockerId]

existing B_pending + PC
→ [B_pending.blockerId]

existing B_pending + pending
→ []

existing B_pending + domain indeterminate
→ [B_pending.blockerId]

existing B_pending + no capability
→ integrity failure
```

M8-B never disposes any of the following merely because it shares an obligation
or Execution:

```text
a producer-occurrence blocker
a blocker for another Execution
a recovery blocker whose cause remains true
the new UNRESOLVABLE blocker created by the same classification
```

## 11. Aggregate prior-session reconciliation

`reconcile_prior_sessions` executes exactly:

```text
validate/index complete outstanding operational-blocker set

validate pre-existing terminal recovery blockers are absent
from unresolvedExecutions

initialize:
    resolutions = []
    pending = []
    blockers = []
    dispositions = []

for U in RecoveryRequest.unresolvedExecutions order:
    classify exact U through:
        existing blocker inspection
        M8-A
        M8-B transition matrix

    append exactly one disposition entry for U

    if proven PNE/PC:
        append resolution

    if UNRESOLVABLE:
        append resolution
        append exact new/reused blocker

    if pending-policy-exhausted:
        append pending
        append exact new/reused B_pending

do not fail-fast because one legitimate result is blocked

after all U:
    calculate which recovery-causal blockers remain outstanding
    after planned dispositions

if every supplied U is PNE/PC
AND zero recovery-causal blocker remains:
    return cleared

otherwise:
    return blocked
```

The order of `resolutions`, `pending`, `blockers`, and `blockerDispositions`
preserves the relevant `unresolvedExecutions` request order.

A pre-existing terminal recovery blocker with no unresolved position:

```text
forces blocked
remains only in authoritative snapshot
is not duplicated into RecoveryPlan.blockers
receives no replayed recovery resolution
```

## 12. Operator-resolution input ingestion

The public boundary is:

```ts
validate_operator_resolution(
  request: ValidateOperatorResolutionRequestV1,
): Promise<ValidatedOperatorResolutionV1>
```

The algorithm is exactly:

```text
require non-empty path

read exact filesystem bytes ONCE

if path unreadable:
    INVALID-OPERATOR-INPUT

require exact submitted bytes are valid UTF-8 JSON

parse those exact bytes once

runtime-validate GateAOperatorResolutionArtifactV1

require artifact.runId == request.runId

find exactly one target outstanding OperationalBlocker where:
    blocker.blockerId == artifact.blockerId

if zero:
    STALE-OR-INAPPLICABLE-OPERATOR-RESOLUTION

if more than one:
    retained-state integrity failure

validate exact target blocker/OAR using normal M8-B blocker validation

require artifact.operatorRequest ==
        target blocker.operatorRequest

require artifact.kind appears exactly in
        target OAR.resolutionContracts

validate exact kind-specific fields and required literal

seal EXACT original submitted bytes
without canonicalization or rewriting
using mediaType application/json

verify returned ArtifactRef

construct exact OperatorResolutionEnvelope

derive exact OperatorResolutionStateEffect

return envelope + effect
```

M8-B never reads the mutable path a second time.

## 13. Operator-resolution mapping

The exact mapping is:

```text
request-operational-recheck
→ {
     kind: resolve-blocker-only
   }
```

Validation requires the exact OAR contract:

```text
kind == request-operational-recheck
```

No domain-success assertion is created.

The exact mapping is:

```text
authorize-known-terminal-execution-replacement
→ {
     kind: resolve-blocker-and-replace-execution,
     priorExecutionId
   }
```

M8-B requires the exact accepted-consequence literal.

The exact mapping is:

```text
authorize-uncertain-execution-replacement
→ {
     kind: resolve-blocker-and-replace-execution,
     priorExecutionId
   }
```

M8-B requires the exact accepted-risk literal:

```text
prior-execution-may-have-produced-the-external-effect-and-the-replacement-may-produce-that-effect-again
```

M8-B never derives or returns:

```text
successorExecutionId
successor attemptOrdinal
```

M2 owns those values.

## 14. M2 admissibility boundary

```text
OAR contract membership
!=
current mutation admissibility
```

M8-B validates:

```text
what the operator artifact means
what exact blocker it answers
whether that resolution kind is authorized by the OAR
```

M2 validates current state, including:

```text
blocker still outstanding
current Execution tail
no prior progression supersession
no later Execution
outstanding source obligation
semantic progression legality
Gate A not ready
historical Execution count < 5
```

If M2 rejects an otherwise valid operator proposal as `INVALID_MUTATION`:

```text
no state changes
existing authoritative history remains trustworthy
M8-B must not reinterpret the rejection
```

## 15. Failure taxonomy

```ts
type OperatorBoundaryFailureCodeV1 =
  | "INVALID-BLOCKER-MATERIALIZATION-REQUEST"
  | "CAUSE-DESCRIPTOR-INTEGRITY-FAILURE"
  | "OPERATOR-REQUEST-SEAL-FAILURE"
  | "OPERATIONAL-BLOCKER-INTEGRITY-FAILURE"
  | "INVALID-OPERATOR-INPUT"
  | "STALE-OR-INAPPLICABLE-OPERATOR-RESOLUTION"
  | "OPERATOR-RESOLUTION-SEAL-FAILURE";
```

The mapping is exact:

```text
malformed producer materialization request
forbidden resolution contract
duplicate contract
known-terminal replacement without exact execution binding
→ INVALID-BLOCKER-MATERIALIZATION-REQUEST

missing/corrupt causeDescriptor
→ CAUSE-DESCRIPTOR-INTEGRITY-FAILURE

OAR serialization/sealing/returned-ref verification failure
→ OPERATOR-REQUEST-SEAL-FAILURE

malformed/corrupt retained OAR
blocker/OAR binding contradiction
recomputed BlockerId mismatch
>1 outstanding recovery blocker for one Execution
terminal recovery blocker + same active unresolved Execution
impossible pending→no-capability transition
→ OPERATIONAL-BLOCKER-INTEGRITY-FAILURE

unreadable operator input path
invalid UTF-8
invalid JSON
wrong operator artifact schema
unknown kind
wrong runId
wrong operatorRequest binding
wrong priorExecutionId
wrong required acknowledgement literal
kind not permitted by exact OAR
→ INVALID-OPERATOR-INPUT

target blocker no longer outstanding
→ STALE-OR-INAPPLICABLE-OPERATOR-RESOLUTION

failure to seal/verify exact submitted operator bytes
→ OPERATOR-RESOLUTION-SEAL-FAILURE
```

These failures are not normal `GateARunnerResult` outcomes and do not fabricate:

```text
GATE-A-READY
DECISION-REQUIRED
OPERATOR-ACTION-REQUIRED
```

An M2 `INVALID_MUTATION` is separate and remains an M2 invalid proposal.

## 16. Presentation behavior

For every currently outstanding `OperationalBlocker`, M8-B includes the exact
`blocker.operatorRequest` in `OperatorActionRequiredResult.operatorRequests`,
preserving authoritative blocker order.

M8-B does not create a new request during read-side projection. The durable OAR
was sealed when its blocker was materialized.

For semantic Decision Requests, M8-B projects exact existing
`DecisionRequestRef.request` artifacts. M8-B does not author, answer, mutate, or
reinterpret semantic Decision Requests.

## 17. Required invariants

```text
M8B-01
Every OperationalBlocker is backed by exactly one intact
GateAOperatorActionRequestV1.

M8B-02
OAR.blockerId equals OperationalBlocker.blockerId.

M8B-03
OAR.obligationId equals OperationalBlocker.obligationId.

M8B-04
OAR.executionId equals OperationalBlocker.executionId.

M8B-05
Non-recovery identity includes causeDescriptor.sha256 and baseStateRevision.

M8B-06
Recovery identity excludes StateRevision and episode occurrence.

M8B-07
Recovery pending blocker is reusable across fresh reconciliation episodes.

M8B-08
A new pending trace never changes stable pending blocker identity.

M8B-09
At most one recovery-causal blocker is outstanding per Execution.

M8B-10
Non-recovery blockers may coexist for the same Execution.

M8B-11
M8 recovery disposition never disposes a non-recovery blocker merely because
it shares an obligation or Execution.

M8B-12
pending + pending reuses exact B_pending.

M8B-13
pending + PNE disposes B_pending.

M8B-14
pending + PC disposes B_pending.

M8B-15
pending + domain indeterminacy disposes B_pending and creates B_domain.

M8B-16
pending + no capability is an integrity failure.

M8B-17
A no-capability recovery blocker implies its Execution is absent from active
unresolved projection.

M8B-18
A domain-indeterminate recovery blocker implies its Execution is absent from
active unresolved projection.

M8B-19
Legitimate blocked recovery of one Execution never fail-fast skips another
unresolved Execution.

M8B-20
Pre-existing terminal recovery blocker can keep aggregate RecoveryPlan blocked
without replaying its recovery resolution.

M8B-21
OAR bytes never contain changing recovery trace or episode identity.

M8B-22
Non-recovery basisArtifacts are not blocker identity.

M8B-23
Producer cause meaning remains producer-owned.

M8B-24
M8-B never invents a producer cause.

M8B-25
Only the three accepted operator resolution kinds exist in v1.

M8B-26
request-operational-recheck creates no domain-success fact.

M8B-27
Known-terminal replacement authorization does not alter prior terminal truth.

M8B-28
Uncertain replacement authorization does not establish whether prior effect
occurred.

M8B-29
Uncertain replacement requires exact duplicate-effect-risk literal.

M8B-30
Operator input bytes are read once.

M8B-31
Operator-authored bytes are sealed exactly as submitted.

M8B-32
Mutable operatorResolutionPath never becomes authority.

M8B-33
Operator artifact must target one exact currently outstanding blocker.

M8B-34
A stale resolution cannot recreate a disposed blocker.

M8B-35
M8 derives state effect; M1 does not choose it.

M8B-36
M2 independently validates current mutation admissibility.

M8B-37
Operator never chooses successor ExecutionId.

M8B-38
A pending recovery blocker may permit safe resume-reconciliation without
operator resolution.

M8B-39
No other blocker permits a mechanical continuation unless its exact OAR says so.

M8B-40
M8-B never turns an operator action into semantic authority.
```

## 18. Explicitly forbidden behaviors

M8-B explicitly forbids:

```text
generic retry-anyway
generic resolve-anyway
operator-created PNE
operator-created PC
operator-created UNRESOLVABLE
operator-created publication confirmation
operator-created validation success
operator-created semantic Decision Request answer
operator-chosen successor ExecutionId
recovery blocker ID containing StateRevision
pending blocker ID containing traceRef
recovery blocker recreation per episode
OAR mutation after blocker creation
reading operator input path twice
canonical rewriting of operator-authored resolution bytes
disposing all blockers with same executionId
disposing all blockers with same obligationId
```

M8-B has no authority to weaken, broaden, or reinterpret these prohibitions.
