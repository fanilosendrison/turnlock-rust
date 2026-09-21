---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-09-21"
step_id: 2
id: NIB-M-GATE-A-RECOVERY-OPERATOR-RECONCILIATION
version: "1.0.4"
scope: gate-a-campaign-runner/recovery-operator/recovery-reconciliation
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Recovery Operator — Recovery Reconciliation

## 1. Status, authority, and purpose

This document is the active Module Brief for M8-A
`recovery-operator/recovery-reconciliation` in the Gate A hostile-review
campaign runner.

It consumes `NIB-S-GATE-A-CAMPAIGN-RUNNER` version `6.0.9`.

It is implementation-construction authority only.

It does not define TURNLOCK product semantics, canonical formal semantics,
hostile-review protocol semantics, formal-assurance claims, review evidence, or
verification evidence.

M8 `recovery-operator` is decomposed as:

```text
M8 recovery-operator
├── M8-A recovery-reconciliation
│   mechanically establish the recovery fact for one exact unresolved Execution
└── M8-B operator-boundary
    materialize operational consequences, blockers, operator requests,
    blocker disposition, and operator resolution
```

This brief closes M8-A only.

M8-A owns:

```text
exact unresolved-descriptor validation
exact recovery-port selection
bounded automatic re-observation
validation of executor-owned recovery observations
recovery classification before operator materialization
recovery evidence projection
immutable reconciliation trace construction
restart-safe episode behavior
```

M8-A does not own:

```text
OperationalBlocker construction
Operator Action Request construction
Decision Request construction
blocker identity
blocker reuse
blocker disposition
operator-resolution ingestion
operator supersession
RecoveryPlan blocker aggregation
human semantic decisions
```

Those belong to M8-B or the M8 facade that composes M8-A and M8-B.

## 2. Cross-module dependencies

M8-A consumes these accepted NIB-S types unchanged:

```ts
UnresolvedExecutionRecoveryRef
ExecutionRecoveryPort
ExecutionRecoveryObservation
NonExecutionProofRef
ReconciliationContinuabilityRef
RecoveryIndeterminacyRef
RecoveredExecutionOutcome
ProvenExecutionRecoveryResolution
ReconciliationPendingRef
RecoveryCapabilityRef
ArtifactRef
ExecutionRef
WorkItemRef
GateARunId
ExecutionId
WorkItemId
```

M8-A consumes the non-authoritative immutable artifact utility defined by
`NIB-M-GATE-A-CAMPAIGN-STATE-PERSISTENCE-OWNERSHIP`:

```ts
CampaignArtifactStore
```

Using `CampaignArtifactStore` gives M8-A no M2 authoritative-state mutation
authority.

M8-A invokes only the internal runner `ExecutionRecoveryPort` boundaries owned
by M4 and M7.

M8-A does not directly import:

```text
llm-runtime
Git libraries
provider SDKs
repository APIs
SQLite
```

No new external Dependency Contract is selected by this brief.

The exact M4 and M7 executor-domain recovery behavior remains owned by their
future Module Briefs and required Dependency Contracts.

## 3. Construction dependencies

M8-A is constructed with exactly:

```ts
interface RecoveryReconciliationDependencies {
  readonly artifactStore: CampaignArtifactStore;
  readonly cognitiveExecutionRecoveryPort: ExecutionRecoveryPort;
  readonly repositoryControlRecoveryPort: ExecutionRecoveryPort;
  readonly sleeper: ReconciliationSleeper;
}

interface ReconciliationSleeper {
  sleep(delayMs: number): Promise<void>;
}
```

The production `ReconciliationSleeper` uses relative process-local delay through
the Node standard library timer boundary.

It must not derive delays from wall-clock timestamps.

It must not read or compare calendar time.

It must not introduce jitter.

Missing M4 or M7 recovery-port dependencies are composition failures.

They are not runtime `UNRESOLVABLE` classifications.

## 4. Internal M8-A request and result

The exact internal request is:

```ts
interface RecoveryReconciliationRequestV1 {
  readonly runId: GateARunId;
  readonly unresolvedExecution: UnresolvedExecutionRecoveryRef;
}
```

The exact internal result is:

```ts
type RecoveryIndeterminateCauseV1 =
  | "no-recovery-capability"
  | "executor-domain-indeterminacy";

type RecoveryReconciliationResultV1 =
  | {
      readonly kind: "resolved";
      readonly resolution: ProvenExecutionRecoveryResolution;
    }
  | {
      readonly kind: "indeterminate";
      readonly executionId: ExecutionId;
      readonly cause: RecoveryIndeterminateCauseV1;
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly kind: "pending-policy-exhausted";
      readonly pending: ReconciliationPendingRef;
    };
```

M8-A does not construct `UnresolvableExecutionRecoveryResolution`.

That type contains an `OperationalBlocker`, which belongs to M8-B.

M8-B consumes an M8-A `indeterminate` result and constructs the exact
`UNRESOLVABLE` resolution and operational boundary.

M8-B consumes an M8-A `pending-policy-exhausted` result and constructs the exact
pending operational boundary.

The `evidence` supplied by M8-A must be preserved unchanged by M8-B except for
ordinary enclosing authoritative serialization.

## 5. Exact automatic-reconciliation policies

M8-A owns exactly two fixed policy values:

```ts
type RecoveryReconciliationPolicyV1 =
  | {
      readonly id: "gate-a-reconciliation-cognitive.v1";
      readonly maxObservations: 6;
      readonly waitsAfterPendingMs:
        readonly [5000, 10000, 20000, 40000, 80000];
    }
  | {
      readonly id: "gate-a-reconciliation-repository.v1";
      readonly maxObservations: 6;
      readonly waitsAfterPendingMs:
        readonly [1000, 2000, 4000, 8000, 16000];
    };
```

Policy selection is exactly:

```text
workItem.executor == cognitive-execution
→ gate-a-reconciliation-cognitive.v1

workItem.executor == repository-control
→ gate-a-reconciliation-repository.v1

any other executor
→ invalid unresolved descriptor / implementation-integrity failure
```

The cognitive deliberate wait budget is:

```text
5 + 10 + 20 + 40 + 80 = 155 seconds
```

The repository deliberate wait budget is:

```text
1 + 2 + 4 + 8 + 16 = 31 seconds
```

These values exclude the execution duration of each `reconcile()` call.

The first recovery observation is immediate.

A wait occurs only after a valid `pending` observation and only when another
observation remains in the same episode.

These policies are implementation construction behavior.

They are not configurable through:

```text
CLI
environment variables
GateARun
campaign protocol
operator resolution
provider response
Retry-After
repository response
```

Changing either policy requires a later explicit construction change with a new
policy version.

## 6. Reconciliation episode

One invocation of:

```text
reconcileExecution(request)
```

creates at most one reconciliation episode for the supplied exact unresolved
Execution.

The supplied `UnresolvedExecutionRecoveryRef` is frozen for the complete
episode.

Every port invocation receives the exact same descriptor object logically:

```text
U0
→ reconcile(U0)
→ reconcile(U0)
→ reconcile(U0)
```

M8-A must not synthesize:

```text
U1
U2
U3
```

from intermediate pending observations.

Intermediate pending observations do not mutate M2.

The episode budget is process-local and ephemeral.

M8-A persists no:

```text
observation counter
remaining budget
next wakeup time
poll deadline
episode UUID
```

into M2.

Exactly one automatic episode may be created for one unresolved Execution by
one top-level M8 classification attempt.

When that episode reaches `pending-policy-exhausted`, the same top-level
classification attempt must not start another automatic episode.

A later top-level runner resume may start a fresh full-budget episode from the
then-current authoritative unresolved descriptor.

## 7. Descriptor validation

For request `R` and unresolved descriptor `U`, require before any recovery-port
call:

```text
R.runId == U.workItem.runId

U.execution.workItemId == U.workItem.workItemId

U.workItem.executor is exactly one of:
    cognitive-execution
    repository-control
```

Require:

```text
if U.terminalOutcome == null:
    U.dispatchState == POSSIBLY-DISPATCHED

if U.terminalOutcome != null:
    U.dispatchState == OBSERVED-RESULT
    recovered outcome execution == U.execution
```

`AUTHORIZED-NOT-DISPATCHED` is invalid in an
`UnresolvedExecutionRecoveryRef` supplied to M8-A.

Verify immutable-artifact integrity for:

```text
U.dispatchIntent
every U.dispatchEvidence entry
```

If:

```text
U.recoveryCapability != null
```

also require:

```text
U.recoveryCapability.executor == U.workItem.executor
```

and verify:

```text
U.recoveryCapability.reconciliationOperation
```

If a terminal outcome already exists, verify its direct outcome artifacts:

```text
captured:
    rawResult
    every runtimeEvidence entry

technical-failure:
    every failureEvidence entry
```

Do not reinterpret any artifact contents as provider or repository semantics.

Descriptor structural failure or artifact-integrity failure is an invocation
failure.

It is not `pending`, `unknown`, or `UNRESOLVABLE`.

## 8. Exact fast-path ordering

Classification ordering is mandatory:

```text
1. validate exact descriptor

2. if terminalOutcome != null:
       PROVEN-COMPLETED
       no recovery-port call

3. else if recoveryCapability == null:
       indeterminate / no-recovery-capability
       no recovery-port call

4. otherwise:
       invoke exact executor-owned recovery port
```

A known terminal outcome always wins over recovery-capability availability.

M8-A must never degrade already-known terminal truth because a recovery
capability is absent or unavailable later.

The phrase `no recovery capability` in M8-A means exactly:

```ts
U.recoveryCapability === null
```

A non-null malformed, corrupt, mismatched, or unusable capability is not this
branch.

It is an implementation/integrity failure.

## 9. Exact recovery-port routing

For non-null capability:

```text
cognitive-execution
→ dependencies.cognitiveExecutionRecoveryPort

repository-control
→ dependencies.repositoryControlRecoveryPort
```

Selection uses only:

```text
U.workItem.executor
```

after requiring:

```text
U.recoveryCapability.executor == U.workItem.executor
```

M8-A must not select a port by:

```text
ExecutionId parsing
ArtifactRef contents
operation contents
provider identity
repository identity
heuristics
```

## 10. Observation validation

A returned `not-executed` observation is accepted only when its exact
`NonExecutionProofRef P` satisfies the NIB-S common binding:

```text
P.execution == U.execution
P.workItemId == U.workItem.workItemId
P.executor == U.workItem.executor

U.recoveryCapability != null

P.executor == U.recoveryCapability.executor
P.recoveryCapability == U.recoveryCapability
P.dispatchIntent == U.dispatchIntent
```

Verify:

```text
P.proof
every P.basisArtifacts entry
P.dispatchIntent
P.recoveryCapability.reconciliationOperation
```

Require:

```text
P.basisArtifacts duplicate-free
P.proof not present in P.basisArtifacts
```

A returned `pending` observation is accepted only when its exact
`ReconciliationContinuabilityRef C` satisfies:

```text
C.execution == U.execution
C.workItemId == U.workItem.workItemId
C.executor == U.workItem.executor

U.recoveryCapability != null

C.executor == U.recoveryCapability.executor
C.recoveryCapability == U.recoveryCapability
C.dispatchIntent == U.dispatchIntent
```

Verify:

```text
C.continuability
every C.basisArtifacts entry
C.dispatchIntent
C.recoveryCapability.reconciliationOperation
```

Require:

```text
C.basisArtifacts duplicate-free
C.continuability not present in C.basisArtifacts
```

A returned `unknown` observation is accepted only when its exact
`RecoveryIndeterminacyRef I` satisfies:

```text
I.execution == U.execution
I.workItemId == U.workItem.workItemId
I.executor == U.workItem.executor

U.recoveryCapability != null

I.executor == U.recoveryCapability.executor
I.recoveryCapability == U.recoveryCapability
I.dispatchIntent == U.dispatchIntent
```

Verify:

```text
I.indeterminacy
every I.basisArtifacts entry
I.dispatchIntent
I.recoveryCapability.reconciliationOperation
```

Require:

```text
I.basisArtifacts duplicate-free
I.indeterminacy not present in I.basisArtifacts
```

For a returned terminal observation:

```text
observation.outcome execution == U.execution
```

Verify every exact:

```text
observation.evidence entry
```

and verify the direct outcome artifacts.

M8-A must not reinterpret executor-domain artifacts.

Invalid observation shape, binding, or artifact integrity is a port-contract or
integrity failure.

It is never downgraded to another recovery observation kind.

## 11. Exact ArtifactRef equality and ordered uniqueness

Whenever this brief says:

```text
orderedUnique(...)
```

two `ArtifactRef` values are equal only when all exact fields are equal:

```text
artifactId
sha256
byteLength
mediaType
repositoryPath
```

Same SHA-256 with different external `artifactId` is not sufficient for
ArtifactRef equality.

`orderedUnique` preserves the first occurrence and removes only later exact
ArtifactRef duplicates.

## 12. Direct terminal evidence

For:

```ts
RecoveredExecutionOutcome O
```

define exact direct terminal evidence:

```text
if O.kind == captured:

    orderedUnique([
        O.value.rawResult,
        ...O.value.runtimeEvidence
    ])

if O.kind == technical-failure:

    orderedUnique([
        ...O.value.failureEvidence
    ])
```

M8-A does not require `runtimeEvidence` or `failureEvidence` to be non-empty
unless a future owning-executor contract requires that.

M8-A must not automatically prepend:

```text
dispatchIntent
dispatchEvidence
```

to `PROVEN-COMPLETED.evidence`.

Those remain part of durable execution provenance in the unresolved descriptor.

`ExecutionRecoveryResolution.evidence` preserves recovery-specific immutable
artifact provenance, not a duplicate serialization of all Execution provenance.

## 13. Terminal observation evidence

For a terminal port observation `T` with outcome `O`, final recovery evidence
before the M8 trace is:

```text
orderedUnique([
    ...T.evidence,
    ...directTerminalEvidence(O)
])
```

M8-A preserves terminal observation evidence exactly.

It does not interpret its provider/repository meaning.

## 14. Recovery trace schema

Every legitimately completed M8-A episode is represented by one immutable
runner-owned trace:

```ts
interface ExecutionRecoveryTraceV1 {
  readonly schema: "gate-a-execution-recovery-trace.v1";

  readonly runId: GateARunId;
  readonly execution: ExecutionRef;
  readonly workItemId: WorkItemId;
  readonly executor: "cognitive-execution" | "repository-control";

  readonly dispatchIntent: ArtifactRef;
  readonly recoveryCapability: RecoveryCapabilityRef | null;

  readonly policy: RecoveryReconciliationPolicyV1 | null;

  readonly observations: readonly RecoveryTraceObservationV1[];

  readonly termination: RecoveryTraceTerminationV1;
}

type RecoveryTraceObservationV1 =
  | {
      readonly ordinal: number;
      readonly kind: "not-executed";
      readonly nonExecutionProof: NonExecutionProofRef;
    }
  | {
      readonly ordinal: number;
      readonly kind: "terminal";
      readonly outcome: RecoveredExecutionOutcome;
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly ordinal: number;
      readonly kind: "pending";
      readonly continuability: ReconciliationContinuabilityRef;
    }
  | {
      readonly ordinal: number;
      readonly kind: "unknown";
      readonly indeterminacy: RecoveryIndeterminacyRef;
    };

type RecoveryTraceTerminationV1 =
  | {
      readonly kind: "preexisting-terminal-outcome";
      readonly outcome: RecoveredExecutionOutcome;
    }
  | {
      readonly kind: "no-recovery-capability";
    }
  | {
      readonly kind: "proven-not-executed";
      readonly observationOrdinal: number;
    }
  | {
      readonly kind: "proven-completed";
      readonly observationOrdinal: number;
    }
  | {
      readonly kind: "executor-domain-indeterminate";
      readonly observationOrdinal: number;
    }
  | {
      readonly kind: "pending-policy-exhausted";
      readonly observationOrdinal: 6;
    };
```

The trace contains references and structured runner facts only.

It does not copy raw provider bytes or repository material.

## 15. Trace invariants

Require:

```text
trace.runId == request.runId
trace.execution == U.execution
trace.workItemId == U.workItem.workItemId
trace.executor == U.workItem.executor
trace.dispatchIntent == U.dispatchIntent
trace.recoveryCapability == U.recoveryCapability
```

For fast path:

```text
preexisting-terminal-outcome
or
no-recovery-capability
```

require:

```text
trace.policy == null
trace.observations == []
```

For any recovery-port episode require:

```text
trace.policy != null
trace.policy == exact policy selected from U.workItem.executor
trace.recoveryCapability != null
1 <= observations.length <= 6
```

Observation ordinals are exact:

```text
observations[0].ordinal == 1

for every array index i:
    observations[i].ordinal == i + 1
```

No gaps and no duplicate ordinal are valid.

Every observation before the final observation must be:

```text
pending
```

because:

```text
not-executed
terminal
unknown
```

terminate the episode immediately.

Termination correspondence is exact:

```text
proven-not-executed
→ final observation.kind == not-executed

proven-completed
→ final observation.kind == terminal

executor-domain-indeterminate
→ final observation.kind == unknown

pending-policy-exhausted
→ observations.length == 6
→ every observation.kind == pending
→ final observation.ordinal == 6
```

For:

```text
preexisting-terminal-outcome
```

require:

```text
U.terminalOutcome != null
termination.outcome == U.terminalOutcome
```

For:

```text
no-recovery-capability
```

require:

```text
U.terminalOutcome == null
U.recoveryCapability == null
```

## 16. Trace serialization

Before sealing, runtime-validate the complete trace invariants.

Serialize the trace deterministically as UTF-8 JSON using this exact local
canonicalization rule:

```text
JSON primitives:
    ordinary JSON representation

arrays:
    preserve array order exactly

objects:
    include every required field
    omit no required field
    sort object keys lexicographically before serialization
    recursively apply this same rule to nested objects

forbidden:
    undefined
    bigint
    NaN
    Infinity
    -Infinity
```

Use compact JSON:

```text
no indentation
no insignificant whitespace
no trailing newline
```

Seal with:

```ts
artifactStore.sealRunnerArtifact({
  bytes: exactCanonicalUtf8Bytes,
  mediaType: "application/json",
})
```

Then verify the returned `ArtifactRef` through `CampaignArtifactStore`.

The trace does not contain its own `ArtifactRef`.

The trace is sealed first.

Its resulting `traceRef` is then appended to final recovery evidence.

A content-identical trace may produce the same CAS identity.

No random episode identifier is added merely to force uniqueness.

## 17. Trace authority boundary

The trace is M8-A algorithmic provenance.

It is not executor-domain proof that an external effect:

```text
occurred
did not occur
remains pending
became indeterminate
```

Those facts remain established by:

```text
NonExecutionProofRef
RecoveredExecutionOutcome
ReconciliationContinuabilityRef
RecoveryIndeterminacyRef
or validated authoritative structural state
```

The trace records:

```text
which exact descriptor M8-A processed
which exact policy M8-A used
which valid observations M8-A accepted
in which logical order
why M8-A terminated
```

## 18. Exact final evidence projections

### 18.1 PROVEN-NOT-EXECUTED

For accepted proof `P`:

```text
orderedUnique([
    P.proof,
    ...P.basisArtifacts,
    traceRef
])
```

### 18.2 PROVEN-COMPLETED from preexisting terminal outcome

Captured:

```text
orderedUnique([
    U.terminalOutcome.value.rawResult,
    ...U.terminalOutcome.value.runtimeEvidence,
    traceRef
])
```

Technical failure:

```text
orderedUnique([
    ...U.terminalOutcome.value.failureEvidence,
    traceRef
])
```

### 18.3 PROVEN-COMPLETED from terminal recovery observation

Captured:

```text
orderedUnique([
    ...terminalObservation.evidence,
    terminalObservation.outcome.value.rawResult,
    ...terminalObservation.outcome.value.runtimeEvidence,
    traceRef
])
```

Technical failure:

```text
orderedUnique([
    ...terminalObservation.evidence,
    ...terminalObservation.outcome.value.failureEvidence,
    traceRef
])
```

### 18.4 Pending policy exhausted

For final continuability witness `C`:

```text
orderedUnique([
    C.continuability,
    ...C.basisArtifacts,
    traceRef
])
```

### 18.5 Executor-domain indeterminacy

For final indeterminacy witness `I`:

```text
orderedUnique([
    I.indeterminacy,
    ...I.basisArtifacts,
    traceRef
])
```

### 18.6 No recovery capability

```text
orderedUnique([
    U.dispatchIntent,
    ...U.dispatchEvidence,
    traceRef
])
```

In this last branch:

```text
U.recoveryCapability == null
```

is authoritative structural state.

The artifact evidence does not pretend independently to prove the null field.

M8-A must not synthesize a fake:

```text
NoRecoveryCapabilityProof
```

artifact.

## 19. Main reconciliation algorithm

For exact request `R`:

```text
U = R.unresolvedExecution

validate U completely

if U.terminalOutcome != null:

    O = U.terminalOutcome

    build trace:
        policy = null
        observations = []
        termination =
            preexisting-terminal-outcome(O)

    seal and verify trace

    evidence =
        directTerminalEvidence(O)
        + traceRef
        through orderedUnique

    return:
        kind = resolved

        resolution =
            classification = PROVEN-COMPLETED
            executionId = U.execution.executionId
            recoveredOutcome = O
            evidence = exact projected evidence


if U.recoveryCapability == null:

    build trace:
        policy = null
        observations = []
        termination =
            no-recovery-capability

    seal and verify trace

    evidence =
        orderedUnique([
            U.dispatchIntent,
            ...U.dispatchEvidence,
            traceRef
        ])

    return:
        kind = indeterminate
        executionId = U.execution.executionId
        cause = no-recovery-capability
        evidence = exact projected evidence


policy = exact policy selected from U.workItem.executor

port = exact port selected from U.workItem.executor

observations = []

lastPending = null

for ordinal from 1 through 6 inclusive:

    rawObservation =
        await port.reconcile(U)

    validate rawObservation completely

    append exact validated typed observation with this ordinal
        to process-local observations

    if rawObservation.kind == not-executed:

        construct complete trace:
            policy = selected policy
            observations = exact accumulated observations
            termination =
                proven-not-executed at current ordinal

        seal and verify trace

        evidence =
            orderedUnique([
                rawObservation.nonExecutionProof.proof,
                ...rawObservation.nonExecutionProof.basisArtifacts,
                traceRef
            ])

        return resolved PROVEN-NOT-EXECUTED


    if rawObservation.kind == terminal:

        construct complete trace:
            policy = selected policy
            observations = exact accumulated observations
            termination =
                proven-completed at current ordinal

        seal and verify trace

        evidence =
            orderedUnique([
                ...rawObservation.evidence,
                ...directTerminalEvidence(rawObservation.outcome),
                traceRef
            ])

        return resolved PROVEN-COMPLETED
            with exact recovered outcome


    if rawObservation.kind == unknown:

        construct complete trace:
            policy = selected policy
            observations = exact accumulated observations
            termination =
                executor-domain-indeterminate at current ordinal

        seal and verify trace

        evidence =
            orderedUnique([
                rawObservation.indeterminacy.indeterminacy,
                ...rawObservation.indeterminacy.basisArtifacts,
                traceRef
            ])

        return:
            kind = indeterminate
            executionId = U.execution.executionId
            cause = executor-domain-indeterminacy
            evidence = exact projected evidence


    require rawObservation.kind == pending

    lastPending =
        exact ReconciliationPendingRef:
            unresolvedExecution = U
            recoveryCapability =
                rawObservation.continuability.recoveryCapability

            evidence temporarily equals:
                orderedUnique([
                    rawObservation.continuability.continuability,
                    ...rawObservation.continuability.basisArtifacts
                ])

    if ordinal == 6:

        construct complete trace:
            policy = selected policy
            observations = exact accumulated observations
            termination =
                pending-policy-exhausted
                observationOrdinal = 6

        seal and verify trace

        finalPending =
            exact ReconciliationPendingRef:
                unresolvedExecution = U
                recoveryCapability =
                    rawObservation.continuability.recoveryCapability

                evidence =
                    orderedUnique([
                        rawObservation.continuability.continuability,
                        ...rawObservation.continuability.basisArtifacts,
                        traceRef
                    ])

        return:
            kind = pending-policy-exhausted
            pending = finalPending


    delayMs =
        policy.waitsAfterPendingMs[ordinal - 1]

    await sleeper.sleep(delayMs)
```

No branch after a legitimate result may fall through.

No seventh observation is permitted.

## 20. Wait semantics

A completed wait is not recovery evidence.

Elapsed time is not recovery evidence.

A wait cannot produce:

```text
not-executed
terminal
unknown
UNRESOLVABLE
```

The wait only permits the next safe re-observation.

No jitter is added.

No adaptive provider or repository delay is applied.

No `Retry-After` value changes M8-A policy.

If provider-specific wait handling is needed, it belongs inside the owning
executor/dependency contract and must still result in one finite port invocation.

## 21. Port completion requirement

Every M4/M7 `ExecutionRecoveryPort.reconcile(U)` invocation must itself complete
finitely under its owning Module Brief and Dependency Contract.

It must either:

```text
return one valid ExecutionRecoveryObservation
```

or fail as an implementation/dependency failure.

M8-A does not impose a second semantic timeout around the port.

M8-A must not implement:

```ts
Promise.race([
  port.reconcile(U),
  locallyInventedTimeout
])
```

because local timeout expiry does not determine the external execution truth.

## 22. Restart and interruption semantics

Intermediate observations and the process-local episode budget are not M2
authority.

If the process terminates:

```text
during reconcile()
during a wait
after one or more pending observations
```

before a legitimate final M8-A result is admitted by M2:

```text
the episode is abandoned
the Execution remains governed only by existing authoritative M2 state
```

A later runner resume reconstructs the unresolved Execution from M2 and starts a
fresh M8-A episode with a fresh full policy budget.

This does not redispatch the original external effect.

A valid pending `ReconciliationContinuabilityRef` specifically guarantees that
future recovery observation remains observational with respect to that original
effect.

If M8-A seals a trace and the process crashes before that trace is referenced by
an authoritative mutation, the unreferenced CAS artifact is non-authoritative
garbage and is harmless.

## 23. Existing pending blockers do not suppress recovery

An already-outstanding operational blocker caused by prior pending-policy
exhaustion blocks normal campaign progression.

It does not prevent M8-A from mechanically re-observing the exact unresolved
Execution during a later recovery barrier.

A later resume may therefore produce:

```text
prior pending blocker exists
+
same unresolved Execution
+
new M8-A episode
→ terminal outcome
```

M8-B may then mechanically dispose the earlier pending blocker when the new
terminal recovery fact supersedes its exact cause.

M8-A does not itself perform that disposition.

## 24. Relationship to M8 facade and M8-B

The public NIB-S:

```text
classify_unresolved_execution(...)
```

is implemented by composing:

```text
M8-A reconcile exact Execution
↓
M8-B materialize blocker/operator consequences when required
↓
public ClassifyUnresolvedExecutionResult
```

The public:

```text
reconcile_prior_sessions(...)
```

must eventually iterate supplied unresolved Executions in exact request order.

The composition is sequential in the initial construction:

```text
E1 episode completes
then E2 episode begins
then E3 episode begins
...
```

No recovery-episode parallelism is selected by this brief.

A legitimate:

```text
UNRESOLVABLE-equivalent indeterminate result
or
pending-policy-exhausted result
```

does not abort classification of later unresolved Executions in a
`RecoveryRequest`.

The aggregate recovery barrier is exhaustive over legitimate recovery results.

By contrast, an implementation/integrity/dependency failure aborts the complete
invocation.

No partial M8 classifications are authoritative merely because they were
computed before that failure.

## 25. Error taxonomy

M8-A uses exact invocation-failure categories:

```ts
type RecoveryReconciliationFailureCodeV1 =
  | "INVALID-UNRESOLVED-DESCRIPTOR"
  | "ARTIFACT-INTEGRITY-FAILURE"
  | "RECOVERY-PORT-CONTRACT-VIOLATION"
  | "RECOVERY-PORT-FAILURE"
  | "RECONCILIATION-WAIT-FAILURE"
  | "TRACE-VALIDATION-FAILURE"
  | "TRACE-SEAL-FAILURE";
```

These failures are implementation/process/integrity/dependency failures.

They are not ordinary `RecoveryReconciliationResultV1` branches.

They must never create:

```text
pending
unknown
UNRESOLVABLE
OperationalBlocker
Operator Action Request
```

merely to hide the failure.

Exact mapping:

```text
malformed or contradictory U
→ INVALID-UNRESOLVED-DESCRIPTOR

missing/corrupt referenced immutable artifact
→ ARTIFACT-INTEGRITY-FAILURE

valid port call returns malformed/mismatched observation
→ RECOVERY-PORT-CONTRACT-VIOLATION

port invocation rejects/throws unexpectedly
→ RECOVERY-PORT-FAILURE

sleeper rejects unexpectedly
→ RECONCILIATION-WAIT-FAILURE

constructed trace violates M8-A trace invariants
→ TRACE-VALIDATION-FAILURE

trace serialization/sealing/verification fails
→ TRACE-SEAL-FAILURE
```

Process termination is not converted into one of these persistent recovery
classifications.

The process simply fails to produce a legitimate completed episode.

## 26. Required invariants

M8-A must satisfy all of these:

```text
M8A-01
One episode processes exactly one immutable unresolved descriptor.

M8A-02
Known terminal outcome is classified without a recovery-port invocation.

M8A-03
recoveryCapability == null is the only direct no-capability branch.

M8A-04
A non-null broken capability is an integrity/composition failure, not
UNRESOLVABLE.

M8A-05
Only cognitive-execution and repository-control have M8-A recovery routes.

M8A-06
Every accepted not-executed observation carries a valid exact
NonExecutionProofRef.

M8A-07
Every accepted pending observation carries a valid exact
ReconciliationContinuabilityRef.

M8A-08
Every accepted unknown observation carries a valid exact
RecoveryIndeterminacyRef.

M8A-09
Every accepted terminal observation binds the exact Execution.

M8A-10
Only pending permits another observation in the same episode.

M8A-11
At most six valid observations occur in one episode.

M8A-12
Observation 1 is immediate.

M8A-13
The five waits are fixed by exact executor-selected policy v1.

M8A-14
Elapsed time never changes recovery truth.

M8A-15
Policy exhaustion while pending never creates executor-domain indeterminacy.

M8A-16
One top-level classification attempt cannot start a second episode after policy
exhaustion.

M8A-17
A later top-level runner resume may start a fresh episode.

M8A-18
Intermediate episode state is not authoritative M2 state.

M8A-19
Every legitimately completed episode seals exactly one immutable M8-A trace.

M8A-20
An interrupted or invalid episode does not produce a legitimate final recovery
trace result.

M8A-21
The trace never replaces executor-domain proof/witness artifacts.

M8A-22
M8-A never creates OperationalBlocker.

M8A-23
M8-A never ingests operator resolution.

M8A-24
M8-A never answers a semantic Decision Request.

M8A-25
M8-A never redispatches the original external effect.

M8A-26
Recovery-plan concurrency is not selected; initial composition is sequential.
```

## 27. Required edge-case behavior

### Existing terminal plus null capability

```text
terminalOutcome != null
recoveryCapability == null

→ PROVEN-COMPLETED
→ zero port calls
```

### Existing terminal plus non-null capability

```text
terminalOutcome != null
recoveryCapability != null

→ PROVEN-COMPLETED
→ zero port calls
```

### No terminal, null capability

```text
terminalOutcome == null
recoveryCapability == null

→ indeterminate
→ cause = no-recovery-capability
→ zero port calls
```

### Non-null capability with wrong executor

```text
→ INVALID-UNRESOLVED-DESCRIPTOR
or equivalent integrity failure before any port call
```

### First observation terminal

```text
observations.length = 1
→ PROVEN-COMPLETED
→ no wait
```

### First observation not-executed

```text
observations.length = 1
→ PROVEN-NOT-EXECUTED
→ no wait
```

### First observation unknown

```text
observations.length = 1
→ executor-domain-indeterminacy
→ no wait
```

### Six pending observations

```text
observations ordinals = 1,2,3,4,5,6
→ exactly five waits
→ pending-policy-exhausted
```

### Pending then terminal

```text
pending
wait
terminal
→ PROVEN-COMPLETED
→ no later observation
```

### Pending then malformed response

```text
→ recovery-port contract failure
→ no fabricated blocker or recovery result
```

### Port throws

```text
→ recovery-port failure
→ no conversion to pending
```

### Process crash after two pending observations

```text
→ no authoritative policy exhaustion
→ later resume starts fresh episode from authoritative descriptor
```

### Prior pending-policy blocker exists on later resume

```text
→ M8-A may re-observe exact unresolved Execution
→ blocker does not suppress mechanical recovery
```

## 28. Forbidden behavior

M8-A must never:

```text
interpret HTTP status codes
interpret provider JSON
interpret Git command output
interpret repository remote state directly
construct NonExecutionProofRef
construct ReconciliationContinuabilityRef
construct RecoveryIndeterminacyRef
guess executor-domain truth
infer unknown from elapsed time
infer unknown from one failed lookup
infer non-execution from missing result
redispatch cognitive work
retry a Git publication mutation
mutate WorkItem identity
mutate Execution identity
mutate dispatch intent
replace recovery capability
start more than six observations
start a second episode after policy exhaustion in the same top-level attempt
persist intermediate poll counters to M2
use wall-clock deadlines
add jitter
honor Retry-After as M8 policy
read user-configured retry settings
create OperationalBlocker
create Decision Request
create Operator Action Request
dispose blocker IDs
ingest operator resolution
create a new external Dependency Contract
```

## 29. Construction boundary

This brief closes M8-A `recovery-reconciliation`.

It intentionally does not close M8-B `operator-boundary`.

After this brief is accepted, the remaining M8 semantic construction work is
the separate M8-B Module Brief defining:

```text
operational blocker causal identity
stable blocker reuse
operator-request presentation artifacts
UNRESOLVABLE blocker materialization
pending-policy-exhaustion blocker materialization
blocker disposition
operator-resolution ingestion
explicit operational supersession
```

The coding agent must not infer those behaviors from this brief.
