---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-15"
step_id: 2
id: NIB-M-GATE-A-REPOSITORY-CONTROL-PUBLICATION-REMOTE-RECOVERY
version: "1.0.0"
scope: gate-a-campaign-runner/repository-control/publication-remote-recovery
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Repository Control — Publication, Remote Observation, and Recovery

## 1. Status, authority, and lifecycle

This document is the active M7-B Module Brief. Together with M7-A it closes
complete M7 `repository-control` NIB-M coverage.

It consumes exactly:

```text
NIB-S-GATE-A-CAMPAIGN-RUNNER 13.0.0
NIB-M-GATE-A-CONTRACTS 1.4.0
NIB-M-GATE-A-CAMPAIGN-STATE-MUTATION-EXECUTION 9.0.0
NIB-M-GATE-A-CAMPAIGN-STATE-SNAPSHOT-INTEGRITY 8.0.0
NIB-M-GATE-A-REPOSITORY-CONTROL-MATERIALIZATION-CANDIDATE-CONSTRUCTION 2.1.1
NIB-M-GATE-A-RECOVERY-OPERATOR-RECONCILIATION 2.1.0
NIB-M-GATE-A-RECOVERY-OPERATOR-BOUNDARY 2.1.0
CampaignArtifactStore
future DC-GIT-CLI-GATE-A-REPOSITORY-CONTROL
```

This brief is implementation-construction authority only. It creates no
TURNLOCK product semantics, hostile-review protocol semantics, canonical formal
semantics, formal-assurance claims, review evidence, or verification evidence.

P6 remains current. P7 remains permanently inactive. P8 remains inactive until
C15. C9-G closes M7-B construction only. C9 overall remains incomplete and C9-H
must still close M1 orchestration. C10/NIB-T has not begun.

The required Git Dependency Contract remains absent. This brief specifies its
exact consumer surface but does not create it. M7-B is not GREEN.

## 2. Responsibility boundary

M7-B owns exactly:

```text
publication preparation
exact current target predecessor observation P
exact P <= T proof
publication realization selection
PublicationIntent proposal construction
publication obligation construction
publication WorkItem construction
publication WorkItem operation schema
pre-Arm publication revalidation
publication RecoveryCapabilityRef construction
conditional remote ref mutation
direct publication attempt capture
fresh already-current observation
publication executed-result qualification
PublicationNonApplicationRef construction
PublicationConfirmationRef construction
PublishedRepositoryViewRef construction
publication ExecutionRecoveryPort implementation
repository-domain recovery continuability / indeterminacy
repository-control publication operational causes
pure publication binding validators consumed by M2
```

M7-B does not own:

```text
candidate construction
RepairIntent interpretation
assurance projection interpretation
candidate semantic subject derivation
Gate A qualification
Python
M6 post-publication validation
campaign currentness
M5 assurance semantics
M8 recovery classification
M8 BlockerId
M8 Operator Action Request bytes
M2 authoritative mutation
M1 orchestration
publication retry permission
operator replacement decision
```

## 3. Exact M7-A / M7-B boundary

M7-A owns:

```text
T = exact immutable publication successor projection
```

M7-B owns:

```text
P = exact current remote predecessor
positive proof P <= T
publication against exact P
remote observation and recovery
```

M7-B must never recompute or change `T`, change commit metadata, select another
parent, derive another candidate tree, or make `T` depend on current remote
state. M7-B consumes M7-A's exact:

```text
project_publication_successor
materialize_projected_successor
```

boundaries and treats contradiction with either as an implementation/process/
integrity failure.

## 4. Shared Git Dependency Contract surface

The future `DC-GIT-CLI-GATE-A-REPOSITORY-CONTROL` exposes M7-A's existing 19
primitives unchanged and exactly these four M7-B-specific primitives:

```text
20 observePublicationTarget
21 acquirePublicationTargetHistory
22 provePublicationAncestorOrEqual
23 conditionalUpdatePublicationTarget
```

The total shared surface is exactly 23 primitives. M7-B consumes only the four
listed here in addition to M7-A boundaries; M7-A does not consume them.

The future Dependency Contract owns exact Git commands, flags, controlled
environment, protocol parsing, credential injection, transport interpretation,
object-format mechanics, and conditional-ref-update mechanics. M7-B owns when
and why each primitive is invoked and validates every typed result.

Runtime qualification must establish exactly:

```text
publication target observation is read-only
repeating target observation cannot create or replay the original mutation
conditionalUpdatePublicationTarget enforces the expected predecessor atomically
conditional update returns exactly applied, not-applied or uncertain
no unconditional remote write is substituted
no force overwrite independent of exact predecessor is permitted
```

Selected v1 has no exact historical query for one ambiguous remote Git-ref
mutation occurrence. Recovery therefore never infers historical non-execution
from current ref state.

## 5. Canonical JSON and credential boundary

Every runner-owned M7-B JSON artifact uses M0
`CanonicalRunnerJsonBytesV1`. M7-B owns no competing canonical JSON algorithm.
Unless an explicit rule states otherwise, seal each artifact through
`CampaignArtifactStore` with:

```text
mediaType = application/json
repositoryPath = null
```

Credentials are injected only at a future Git Dependency Contract invocation.
Never retain credentials in a target, obligation, cause, operation,
revalidation, recovery operation, attempt result, observation, proof,
confirmation, `PublishedRepositoryViewRef`, or `ArtifactRef.repositoryPath`.
The target's `remoteEndpoint` remains the exact credential-free endpoint already
established by M7-A preflight.

## 6. Publication-preparation obligation

The obligation means exactly:

```text
establish a mechanically valid publication preparation for this exact
run + candidate + qualification + publication target
```

It is operational construction authority only. It is not product semantics,
publication confirmation, permission to mutate a remote, a PublicationIntent,
a WorkItem, or an Execution.

Define exactly:

```ts
interface GateAPublicationPreparationObligationDefinitionV1 {
  readonly schema:
    "gate-a-publication-preparation-obligation-definition.v1";

  readonly kind:
    "publication-preparation";
}
```

Its exact canonical value is:

```json
{
  "schema": "gate-a-publication-preparation-obligation-definition.v1",
  "kind": "publication-preparation"
}
```

Seal it through M0 canonical runner JSON. Construct the ID exactly:

```text
deriveId(
  "publication-preparation-obligation.v1",
  runId,
  candidateId,
  qualificationId,
  target.repositoryIdentity,
  target.remoteEndpoint,
  target.refName,
  definition.sha256
)
```

Exclude `StateRevision`, ownership generation, timestamp, remote observation,
predecessor, successor, process identity, temporary repository path, and
credentials.

Construct a blocked preparation obligation exactly as:

```ts
ObligationRef {
  obligationId: exact formula above,
  runId: request.runId,
  candidateId: request.candidate.candidateId,
  reviewCampaignId: null,
  definition: exact sealed preparation definition
}
```

## 7. Publication obligation and WorkItem operation

Define the actual publication-obligation definition exactly:

```ts
interface GateAPublicationObligationDefinitionV1 {
  readonly schema:
    "gate-a-publication-obligation-definition.v1";

  readonly kind:
    "publish-qualified-candidate";
}
```

Its exact canonical value is:

```json
{
  "schema": "gate-a-publication-obligation-definition.v1",
  "kind": "publish-qualified-candidate"
}
```

The obligation ID remains:

```text
deriveId(
  "publication-obligation.v1",
  publicationIntentId
)
```

No additional publication-obligation ID domain exists.

Define the WorkItem operation exactly:

```ts
interface GateAPublicationWorkOperationV1 {
  readonly schema:
    "gate-a-publication-work-operation.v1";

  readonly intent:
    PublicationIntentRef;
}
```

Seal exact M0-canonical bytes. The pure extractor:

```text
extract_publication_intent_from_operation(operation)
```

must verify the exact `ArtifactRef`, require `application/json`, require
`repositoryPath == null`, require exact M0-canonical bytes, validate the exact
schema, and return the exact embedded `PublicationIntentRef`. It performs no
repository I/O, remote observation, or Git command.

## 8. Publication target observation

Define exactly:

```ts
interface GateAPublicationTargetObservationV1 {
  readonly schema:
    "gate-a-publication-target-observation.v1";

  readonly target:
    RepositoryPublicationTargetRef;

  readonly state:
    | {
        readonly kind: "present";
        readonly authority: RepositoryAuthorityRef;
      }
    | {
        readonly kind: "missing";
      }
    | {
        readonly kind: "unavailable";
        readonly reason:
          | "remote-unreachable"
          | "remote-observation-failed"
          | "commit-authority-unresolvable";
      };
}
```

The artifact contains no timestamp, credential, local remote name, or temporary
path. Repeating the same exact observation may produce the same content-
addressed artifact.

## 9. Fast-forward proof

Define exactly:

```ts
interface GateAPublicationFastForwardProofV1 {
  readonly schema:
    "gate-a-publication-fast-forward-proof.v1";

  readonly target:
    RepositoryPublicationTargetRef;

  readonly predecessor:
    RepositoryAuthorityRef;

  readonly successor:
    RepositoryAuthorityRef;

  readonly result:
    | "ancestor-or-equal"
    | "not-ancestor";
}
```

Only `ancestor-or-equal` may enter
`AuthorizedGitTransitionRef.ancestryEvidence`. An accepted transition uses
exactly:

```text
ancestryEvidence = [fastForwardProofArtifact]
```

## 10. Exact publication preparation

For request `R`, execute exactly:

```text
1. validate exact run, retained RepositoryInspection, candidate,
   qualification and publication-target bindings
2. call M7-A project_publication_successor for exact T
3. call M7-A materialize_projected_successor
4. require materialized authority equals projected T by commit and tree
5. call observePublicationTarget for the exact target
```

Require:

```text
R.runId == R.repositoryInspection.runId == R.candidate.runId
R.candidate is the exact qualified candidate
R.qualification.candidateId == R.candidate.candidateId
R.target == R.repositoryInspection.publicationTarget
R.target == exact GateARun publicationTarget
R.repositoryInspection is the exact retained preflight inspection
```

If target observation is unavailable or missing, or a present authority cannot
be acquired and validated, return blocked preparation. No PublicationIntent
exists.

When exact predecessor `P` is established, call in order:

```text
acquirePublicationTargetHistory(P)
provePublicationAncestorOrEqual(P, T)
```

Unavailable predecessor authority/history and `not-ancestor` return blocked
preparation. A positive proof constructs exactly:

```ts
AuthorizedGitTransitionRef {
  target: exact request target,
  predecessor: P,
  successor: T,
  relationship: "fast-forward",
  ancestryEvidence: [exact positive fast-forward proof]
}
```

Publication preparation performs no remote mutation.

## 11. Preparation evidence, intent, obligation, and WorkItem

For successful preparation define:

```text
successorProjection =
  exact M7-A PublicationSuccessorProjectionResultV1.projection

predecessorObservation =
  exact present GateAPublicationTargetObservationV1

fastForwardProof =
  exact positive GateAPublicationFastForwardProofV1
```

Set exactly:

```text
intent.preparationEvidence = [
  successorProjection,
  predecessorObservation,
  fastForwardProof
]

PreparedPublication.materialIdentityEvidence = [
  successorProjection,
  predecessorObservation,
  fastForwardProof
]
```

Use no hash or filesystem sorting.

Construct the intent ID exactly:

```text
deriveId(
  "publication-intent.v1",
  runId,
  candidateId,
  qualificationId,
  target.repositoryIdentity,
  target.remoteEndpoint,
  target.refName,
  predecessor.commitSha,
  predecessor.treeSha,
  successor.commitSha,
  successor.treeSha
)
```

M7-B proposes but never admits `PublicationIntentRef`.

Construct publication obligation and WorkItem IDs exactly:

```text
publication obligation =
deriveId("publication-obligation.v1", publicationIntentId)

publication WorkItem =
deriveId("publication-work-item.v1", publicationIntentId)
```

Require publication obligation:

```text
runId = intent.runId
candidateId = intent.candidateId
reviewCampaignId = null
definition = exact publication obligation definition
```

Require WorkItem:

```text
runId = intent.runId
candidateId = intent.candidateId
reviewCampaignId = null
sourceObligationIds = [publicationObligation.obligationId]
executor = repository-control
operation = exact GateAPublicationWorkOperationV1 artifact
inputRefs = [successorProjection, predecessorObservation, fastForwardProof]
```

## 12. Realization selection

M7-B derives realization only as:

```text
predecessor == successor
→ already-current

predecessor != successor
→ conditional-ref-update
```

No caller boolean, M1 choice, or Git heuristic participates.

## 13. Preparation-blocked cause and result

All M7-B operational causes use:

```text
schema = gate-a-repository-publication-operational-cause.v1
```

Define preparation cause exactly:

```ts
interface PublicationPreparationUnavailableCauseV1 {
  readonly schema:
    "gate-a-repository-publication-operational-cause.v1";

  readonly kind:
    "publication-preparation-unavailable";

  readonly candidateId:
    CandidateRevisionId;

  readonly qualificationId:
    GateAQualificationId;

  readonly target:
    RepositoryPublicationTargetRef;

  readonly reason:
    | "target-unavailable"
    | "target-ref-missing"
    | "predecessor-authority-unavailable"
    | "predecessor-history-unavailable"
    | "non-fast-forward";
}
```

It has exactly:

```text
resolutionContracts = [
  { kind: "request-operational-recheck" }
]
```

Basis artifacts contain only exact immutable observations/proofs actually
available. Cause descriptors contain no StateRevision, timestamp, process ID,
or random occurrence material.

Return exactly:

```ts
{
  kind: "blocked",
  blockingObligation,
  cause
}
```

Require obligation run/candidate/qualification/target identity to match the
exact request and cause. M7-B creates no `BlockerId`. Future M1 asks M8-B to
materialize the blocker and M2 to co-admit obligation plus blocker atomically.

## 14. Pre-Arm revalidation and recovery operation

Define exact Arm revalidation artifact:

```ts
interface GateAPublicationArmRevalidationV1 {
  readonly schema:
    "gate-a-publication-arm-revalidation.v1";
  readonly publicationIntentId: PublicationIntentId;
  readonly workItemId: WorkItemId;
  readonly candidateId: CandidateRevisionId;
  readonly qualificationId: GateAQualificationId;
  readonly target: RepositoryPublicationTargetRef;
  readonly expectedPredecessor: RepositoryAuthorityRef;
  readonly observedPredecessor: RepositoryAuthorityRef;
  readonly intendedSuccessor: RepositoryAuthorityRef;
  readonly successorProjection: ArtifactRef;
  readonly targetObservation: ArtifactRef;
  readonly ancestryProof: ArtifactRef;
}
```

Require `observedPredecessor == expectedPredecessor` and seal exact canonical
JSON.

Define recovery operation exactly:

```ts
interface GateAPublicationRecoveryOperationV1 {
  readonly schema:
    "gate-a-publication-recovery-operation.v1";
  readonly publicationIntentId: PublicationIntentId;
  readonly candidateId: CandidateRevisionId;
  readonly qualificationId: GateAQualificationId;
  readonly target: RepositoryPublicationTargetRef;
  readonly expectedPredecessor: RepositoryAuthorityRef;
  readonly intendedSuccessor: RepositoryAuthorityRef;
  readonly successorProjection: ArtifactRef;
}
```

Seal it before Arm and construct exactly:

```ts
RecoveryCapabilityRef {
  executor: "repository-control",
  reconciliationOperation: exact recovery-operation ArtifactRef
}
```

Selected v1 conditional publication always carries this non-null capability.
Read-only target reconciliation is preparable before Arm; `null` is forbidden
for an M7-B conditional publication Arm.

## 15. Pre-Arm API

Expose conceptually:

```text
prepare_publication_dispatch(...)
```

It returns exactly one of `ready`, `stale-predecessor`, or `blocked`.

For `ready`, require a fresh exact target observation equal to the intent's
predecessor and return:

```text
revalidationBasis = [exact GateAPublicationArmRevalidationV1 ArtifactRef]

dispatchEvidence = orderedUnique([
  exact fresh target observation,
  exact arm-revalidation artifact,
  exact successor projection,
  exact ancestry proof
])

recoveryCapability = exact non-null repository-control RecoveryCapabilityRef
```

For `stale-predecessor`, the target was successfully observed but differs from
the intent predecessor. Return no blocker cause and permit no Arm. C9-H M1
reloads and re-enters ordinary preparation.

For `blocked`, exact required fresh observation could not be established. Return
cause `publication-pre-arm-observation-unavailable`, with only
`request-operational-recheck`, anchored to the existing publication obligation,
WorkItem, and authorized-not-dispatched Execution. No mutation occurred.

## 16. Conditional publication dependency boundary

After successful M2 Arm only, M7-B invokes:

```text
conditionalUpdatePublicationTarget(
  exact target,
  exact expected predecessor commit,
  exact intended successor commit
)
```

The result union is exactly:

```text
applied
not-applied
uncertain
```

No fourth result, unconditional-write fallback, merge, rebase, or retry inside
M7-B exists.

## 17. Attempt-result artifact and direct execution

Define exactly:

```ts
interface GateAPublicationAttemptResultV1 {
  readonly schema:
    "gate-a-publication-attempt-result.v1";
  readonly publicationIntentId: PublicationIntentId;
  readonly target: RepositoryPublicationTargetRef;
  readonly expectedPredecessor: RepositoryAuthorityRef;
  readonly intendedSuccessor: RepositoryAuthorityRef;
  readonly outcome:
    | "conditional-update-applied"
    | "conditional-update-not-applied"
    | "recovery-successor-observed";
}
```

Map direct terminal dependency results exactly:

```text
applied → conditional-update-applied
not-applied → conditional-update-not-applied
```

Seal exact canonical JSON as `CapturedExecutionResult.rawResult`. Place exact
Dependency Contract/runtime proof artifacts in `runtimeEvidence`.

Expose conceptually:

```text
publish_conditionally(PublicationExecutionRequest)
```

Validate the complete `ArmedExecutionDispatchRef`, exact repository-control
WorkItem and operation, intent, candidate, recovery capability, and dispatch
intent. Invoke conditional update exactly once.

For terminal `applied` or `not-applied`, return captured
`PublicationExecutionCapture` whose `CapturedExecutionResult` names the exact
armed Execution and ordered runtime evidence.

For `uncertain`, return exact `UnresolvedExecutionRecoveryRef`:

```text
execution = exact armed execution
workItem = exact armed WorkItem
dispatchState = POSSIBLY-DISPATCHED
dispatchIntent = exact armed dispatchIntent
dispatchEvidence = orderedUnique([
  ...armed dispatchEvidence,
  ...exact uncertainty evidence
])
terminalOutcome = null
recoveryCapability = exact armed non-null recovery capability
```

Publication execution has no `TechnicalExecutionFailure` branch.

## 18. Already-current observation

Expose:

```text
observe_already_current_publication(...)
```

Return exactly `observed`, `stale`, or `blocked`.

`observed` requires a fresh target authority equal to exact successor and
constructs:

```ts
PublicationAlreadyCurrentObservationRef {
  publicationIntentId: exact intent ID,
  candidateId: exact candidate ID,
  target: exact target,
  observedAuthority: exact successor,
  evidence: orderedUnique([
    exact fresh target-observation artifact,
    exact successor projection
  ])
}
```

`stale` means fresh observation succeeded but target is no longer successor. It
returns no confirmation, Arm, or blocker; M1 re-enters preparation.

`blocked` means observation could not be established. Return
`publication-already-current-observation-unavailable` with only
`request-operational-recheck`, anchored to the existing publication obligation
and WorkItem and to no Execution.

## 19. Publication confirmation and published view

Define exact verification artifact:

```ts
interface GateAPublishedRepositoryViewVerificationV1 {
  readonly schema:
    "gate-a-published-repository-view-verification.v1";
  readonly publicationIntentId: PublicationIntentId;
  readonly publicationConfirmationId: PublicationConfirmationId;
  readonly candidateId: CandidateRevisionId;
  readonly target: RepositoryPublicationTargetRef;
  readonly authority: RepositoryAuthorityRef;
  readonly successorProjection: ArtifactRef;
  readonly targetObservation: ArtifactRef;
}
```

It contains no operational local path.

Before confirmation obtain one fresh exact present observation whose authority
is exact transition successor. Call M7-A
`materialize_projected_successor` with the exact retained successor projection
and require exact commit/tree equality with the transition successor.

Compute confirmation identity exactly:

```text
deriveId(
  "publication-confirmation.v1",
  intent.publicationIntentId
)
```

One exact PublicationIntent has at most one logical confirmation; multiple
observation occurrences do not create another confirmation identity.

Seal exact view verification and use:

```text
materialIdentityEvidence = orderedUnique([
  successorProjection,
  freshTargetObservation,
  publishedViewVerification
])
```

Construct `PublicationConfirmationRef` with exact confirmation ID, intent ID,
transition, candidate and material identity evidence. Construct
`PublishedRepositoryViewRef` with that confirmation ID, candidate, exact target,
exact successor authority, the operational path returned by M7-A, and the same
materialization evidence. The operational path is never durable authority.

## 20. Publication non-application

Define exact proof:

```ts
interface GateAPublicationNonApplicationProofV1 {
  readonly schema:
    "gate-a-publication-non-application-proof.v1";
  readonly publicationIntentId: PublicationIntentId;
  readonly candidateId: CandidateRevisionId;
  readonly executionId: ExecutionId;
  readonly workItemId: WorkItemId;
  readonly target: RepositoryPublicationTargetRef;
  readonly expectedPredecessor: RepositoryAuthorityRef;
  readonly intendedSuccessor: RepositoryAuthorityRef;
  readonly attemptResult: ArtifactRef;
}
```

Construct it only from the direct positive dependency result `not-applied`,
never from absence of success, timeout, current-target equality, or recovered
material.

For a direct source require attempt outcome
`conditional-update-not-applied`, construct proof, and set:

```text
basisArtifacts = orderedUnique(executionResult.runtimeEvidence)
```

Construct exact `PublicationNonApplicationRef` with schema v1, exact intent,
candidate, Execution, WorkItem, Arm dispatch intent, attempt result, proof, and
basis artifacts. M7-B does not authorize another Execution.

## 21. Observation qualification

Keep public NIB-S request/result types unchanged. Define internal:

```text
qualify_publication_observation({ request, sourceOrigin })
```

where `sourceOrigin` is exactly one of:

```text
already-current
direct-execution
recovered-execution
```

C9-H M1 supplies this provenance from authoritative M2 history. M7-B never
infers it from byte-equal payloads.

### 21.1 Already-current

Require request kind and origin both `already-current`. Validate the exact
observation. `not-applied` is forbidden. If target observation and material
identity validate, construct exact confirmed result and published view.
Structural contradiction is implementation/process/integrity failure.

### 21.2 Direct execution

Require request kind `executed-publication` and origin `direct-execution`.
`conditional-update-not-applied` returns exact `not-applied` result with
`PublicationNonApplicationRef`.

For any other lawful direct captured attempt, obtain a fresh target observation.
Exact successor returns confirmed. Unavailable observation returns blocked cause
`publication-observation-unavailable`. Present/missing state that does not
establish exact successor returns blocked cause
`publication-observation-conflict`. Never manufacture non-application.

### 21.3 Recovered execution

Require request kind `executed-publication` and origin `recovered-execution`.
`not-applied` is forbidden under all conditions. A raw outcome
`conditional-update-not-applied` is implementation/process/integrity failure.
The only M7-B recovery terminal attempt outcome is
`recovery-successor-observed`. Freshly verify successor and construct exact
confirmation and view.

## 22. Operational cause union and resolution contracts

The exact post-intent cause kinds are:

```text
publication-pre-arm-observation-unavailable
publication-already-current-observation-unavailable
publication-observation-unavailable
publication-observation-conflict
publication-known-terminal-replacement-required
```

Together with `publication-preparation-unavailable`, all use
`gate-a-repository-publication-operational-cause.v1`. Cause descriptors contain
no occurrence-only StateRevision, timestamp, process, or random material.

Use exactly:

```text
publication-preparation-unavailable
publication-pre-arm-observation-unavailable
publication-already-current-observation-unavailable
publication-observation-unavailable
publication-observation-conflict
→ [{ kind: "request-operational-recheck" }]
```

For `publication-known-terminal-replacement-required`, use canonical order:

```text
[
  {
    kind: "request-operational-recheck"
  },
  {
    kind: "authorize-known-terminal-execution-replacement",
    priorExecutionId: exact prior direct-not-applied Execution,
    requiredAcceptedConsequence:
      "prior-execution-remains-authoritative-history-and-this-authorizes-one-additional-execution-occurrence"
  }
]
```

Never expose `authorize-uncertain-execution-replacement` for a known
`PublicationNonApplicationRef`.

Expose pure:

```text
derive_known_terminal_publication_replacement_cause(...)
```

C9-H M1 may call it only when fresh preparation yields the same current intent
ID, the prior publication WorkItem remains required, the exact prior Execution
has one authoritative `PublicationNonApplicationRef`, and no later Execution
exists. M7-B validates all bindings, returns only the cause, and creates no
successor Execution. M8-B/M2 retain replacement ownership.

## 23. Publication ExecutionRecoveryPort

M7-B implements:

```ts
ExecutionRecoveryPort.reconcile(
  unresolved
)
```

only for `unresolved.workItem.executor == "repository-control"`. First validate
the exact WorkItem operation and recovery capability. Reconciliation is
read-only and never invokes `conditionalUpdatePublicationTarget` or replays
publication.

Let exact recovery operation `O` bind:

```text
P = O.expectedPredecessor
T = O.intendedSuccessor
```

Perform one fresh `observePublicationTarget`.

### 23.1 Target is T

Construct exact attempt artifact with outcome `recovery-successor-observed` and
return `kind = terminal`, `outcome.kind = captured`, with exact recovered
`CapturedExecutionResult` and immutable observation evidence.

### 23.2 Target is P

Current predecessor equality does not prove historical non-execution. Return
`kind = pending` with exact `ReconciliationContinuabilityRef`.

### 23.3 Target is missing or other authority X

Because selected v1 lacks an exact historical operation query, return
`kind = unknown` with exact `RecoveryIndeterminacyRef`.

### 23.4 Observation unavailable

Failure to contact or observe the remote does not establish indeterminacy.
Return `kind = pending` with exact `ReconciliationContinuabilityRef`.

Selected v1 never returns `ExecutionRecoveryObservation.kind = not-executed`.
The Git boundary cannot positively prove that an ambiguous mutation never
crossed its effect boundary. Direct terminal known non-application remains
`PublicationNonApplicationRef`, not `PROVEN-NOT-EXECUTED`.

## 24. Recovery fact artifacts

Define continuability payload exactly:

```ts
interface GateAPublicationReconciliationContinuabilityV1 {
  readonly schema:
    "gate-a-publication-reconciliation-continuability.v1";
  readonly publicationIntentId: PublicationIntentId;
  readonly target: RepositoryPublicationTargetRef;
  readonly expectedPredecessor: RepositoryAuthorityRef;
  readonly intendedSuccessor: RepositoryAuthorityRef;
  readonly recoveryOperation: ArtifactRef;
}
```

Its meaning is only that another exact target observation is read-only and
cannot create, repeat, or replay publication. Construct the NIB-S common
`ReconciliationContinuabilityRef` envelope with exact Execution, WorkItem,
executor, dispatch intent, recovery capability, payload artifact, and
observation basis.

Define indeterminacy payload exactly:

```ts
interface GateAPublicationRecoveryIndeterminacyV1 {
  readonly schema:
    "gate-a-publication-recovery-indeterminacy.v1";
  readonly publicationIntentId: PublicationIntentId;
  readonly target: RepositoryPublicationTargetRef;
  readonly expectedPredecessor: RepositoryAuthorityRef;
  readonly intendedSuccessor: RepositoryAuthorityRef;
  readonly observedState:
    | { readonly kind: "missing" }
    | {
        readonly kind: "other-authority";
        readonly authority: RepositoryAuthorityRef;
      };
  readonly historicalOperationQuery: "unsupported";
}
```

It positively establishes executor-domain recovery exhaustion under selected
v1 without stating whether publication executed. Construct the NIB-S common
`RecoveryIndeterminacyRef` envelope exactly.

M8-A and M8-B remain unchanged. M8 validates common envelope bindings, owns
`PROVEN-COMPLETED` / `PROVEN-NOT-EXECUTED` / `UNRESOLVABLE`, owns the finite
pending policy, and owns recovery blockers. M7-B supplies only executor-domain
observation truth.

## 25. Direct-versus-recovered provenance

`PublicationNonApplicationRef` may become authoritative only when the exact
captured result was introduced by `AdmitExecutionOutcomeV1`, never by
`AdmitExecutionRecoveryV1`. Internal `sourceOrigin` fails invalid recovered
`not-applied` proposals early; M2 remains final enforcement.

## 26. Pure validators consumed by M2

Expose these exact pure/read-only responsibilities:

```text
validate_publication_preparation_obligation
validate_publication_operational_cause
extract_publication_intent_from_operation
validate_publication_arm_revalidation
validate_publication_recovery_operation
validate_already_current_observation
validate_publication_non_application
validate_publication_confirmation_bundle
```

They may read immutable `ArtifactRef` bytes through `CampaignArtifactStore` only
when those bytes are part of the requested validation. They perform no Git or
remote mutation. M2 uses them only as construction/binding validators and does
not reinterpret Git meaning.

## 27. Failure taxonomy

Implementation/process/integrity failures include at least:

```text
malformed request
wrong retained RepositoryInspectionRef
candidate/qualification mismatch
target mismatch
M7-A successor projection contradiction
successor materialization mismatch
invalid canonical artifact
Git dependency impossible result
conditional update result outside closed union
attempt result binding mismatch
recovery operation mismatch
recovery operation attempts mutation
recovered source proposes not-applied
confirmation ID mismatch
published-view authority mismatch
non-application proof contradiction
```

These are not `OperationalBlocker`, `DECISION-REQUIRED`, `protocol-invalid`, or
`UNRESOLVABLE`. Known operational conditions use exact M7-B producer cause,
M8-B blocker materialization, and M2 admission.

## 28. Crash and replay

Require exactly:

```text
crash before PublicationIntent admission
→ repeat read-only preparation

crash after preparation artifacts sealed but before intent admission
→ same deterministic intent/obligation/WorkItem

crash after intent admission before Execution
→ use authoritative intent/WorkItem

crash after Execution authorization but before Arm
→ no publication side effect occurred

crash after Arm before M7 return
→ unresolved from M2 Arm
→ recovery only
→ never replay mutation

crash after direct captured result before M2 outcome admission
→ no automatic publication replay
→ recover from armed unresolved state

crash after direct outcome admission before publication qualification
→ replay pure/fresh qualification, not mutation

crash after confirmation before post-publication validation
→ use authoritative confirmation/published view

crash during recovery observation
→ observation is read-only; M8 may invoke again under its policy
```

## 29. Required invariants

```text
M7B-01 M7-B never derives or modifies T.
M7B-02 M7-B observes P from the exact immutable publication target; caller never
        supplies P.
M7B-03 Publication requires positive P <= T proof.
M7B-04 Publication preparation performs no remote mutation.
M7B-05 Publication realization is derived only by P == T versus P != T.
M7B-06 Already-current creates no Execution and crosses no Arm.
M7B-07 Conditional publication mutation occurs only after successful M2 Arm.
M7B-08 Every conditional mutation enforces exact predecessor atomically.
M7B-09 No unconditional write fallback exists.
M7B-10 Publication recovery never reissues the mutation.
M7B-11 Selected v1 publication recovery never claims PROVEN-NOT-EXECUTED.
M7B-12 Current target == predecessor alone never proves non-execution.
M7B-13 Direct known non-application is distinct from recovery non-execution.
M7B-14 Recovered payload can never create PublicationNonApplicationRef.
M7B-15 PublicationConfirmationId is deterministic from PublicationIntentId.
M7B-16 Confirmed publication binds exact target, P, T, candidate and
        qualification.
M7B-17 PublishedRepositoryViewRef authority equals exact T by commit and tree.
M7B-18 Operational path cannot become semantic Decision Required.
M7B-19 M7-B constructs no BlockerId or OAR.
M7B-20 M2 remains sole authoritative state writer.
M7B-21 Publication preparation blocker always has exact blocking obligation.
M7B-22 A preparation obligation is operational construction state, not
        publication permission.
M7B-23 Recovery reobservation is read-only.
M7B-24 P7 remains permanently inactive.
M7B-25 P8 remains inactive until C15.
```

## 30. Future NIB-T requirements

Create no NIB-T. Future tests must cover at least:

```text
target observation unavailable before intent produces preparation obligation + cause
target ref missing before intent produces preparation obligation + cause
P not ancestor of T blocks preparation
preparation replay preserves obligation/cause identity
successful preparation supersedes prior preparation obligation by publication obligation
candidate advance supersedes old preparation obligation with empty replacement
qualification replacement supersedes old preparation obligation with empty replacement
P == T selects already-current
already-current target changes before fresh observation: stale and no Arm
already-current observation unavailable produces operational cause
P != T selects conditional-ref-update
pre-Arm target changed produces no Arm or uncertainty
pre-Arm target unavailable produces operational cause and no mutation
conditional update applied produces direct captured result
conditional update positive not-applied produces direct captured result and PublicationNonApplicationRef
conditional update uncertain produces unresolved Execution
crash after Arm uses recovery only
recovery target T produces recovered captured result
recovery target P is pending and never PROVEN-NOT-EXECUTED
recovery target missing is indeterminate
recovery target X other than P/T is indeterminate
recovery observation unavailable is pending
recovered not-applied attempt is rejected
direct not-applied plus same-intent preparation produces known-terminal replacement cause
confirmation ID is deterministic
published view binds exact T
preparation performs no remote mutation
recovery performs no mutation
no credential becomes durable
P6 remains unchanged
P7 remains inactive
P8 remains inactive
```

## 31. Forbidden behavior

M7-B must never:

```text
accept caller-selected predecessor
accept caller-selected realization
recompute successor T
modify successor commit or metadata
merge
rebase
force overwrite without exact predecessor
perform unconditional push
retry remote mutation inside M7-B
replay publication during recovery
infer non-execution from target == predecessor
infer non-execution from timeout
infer non-execution from missing successor
use tree equality without exact commit identity
produce not-applied from recovered source
construct BlockerId
construct Operator Action Request
classify UNRESOLVABLE
classify PROVEN-NOT-EXECUTED
classify PROVEN-COMPLETED
mutate M2 directly
invoke M6
interpret Gate A semantics
persist credentials
use mutable local path as durable authority
use P7
activate P8
```

## 32. Construction discovery classification

Record the exposed seam exactly:

```text
statement:
PublicationPreparationResult may be operationally blocked before a
PublicationIntent exists, but every OperationalBlocker must reference one exact
admitted or co-admitted ObligationRef; therefore the existing blocked result
contains insufficient construction authority for M1/M8-B/M2 to materialize the
blocker mechanically

semantic disposition:
authority-conflict-or-uncertain at construction representation level

affected layer:
architecture-or-implementation

normative impact:
none
```

Resolve it through the accepted M3 producer pattern:

```text
blocked producer resolution = blockingObligation + producer-owned cause

publication preparation blocked
→ exact publication-preparation ObligationRef
→ exact repository-control cause
→ M8-B materializes OperationalBlocker
→ M2 co-admits obligation + blocker atomically

publication later becomes preparable
→ exact outstanding preparation obligation
→ atomically superseded by exact publication obligation
```

The resolution is derived from existing construction authority, changes no
product or protocol semantic meaning, and requires no ADR.
