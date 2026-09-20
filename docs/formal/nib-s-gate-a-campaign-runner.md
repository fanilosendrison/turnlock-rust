---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-system"
workspace: "turnlock-rust"
date: "2026-09-20"
step_id: 1
id: NIB-S-GATE-A-CAMPAIGN-RUNNER
version: "2.0.0"
scope: gate-a-hostile-review-campaign-runner
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-S — Gate A hostile-review campaign runner

## 1. Status, authority, and purpose

This document is the active construction System Brief for the Gate A hostile-review campaign runner.

It is implementation-construction authority only. It does not define TURNLOCK product semantics, canonical formal semantics, hostile-review protocol semantics, formal-assurance claims, review evidence, or verification evidence.

Its controlling technical inputs are:

- `docs/specification/turnlock-spec.md`;
- accepted ADR-041 through ADR-048;
- `formal/verification.yaml`;
- the content-addressed hostile-review protocol and evidence contracts under `formal/reviews/`;
- the repository authority and validation rules in `AGENTS.md`.

The runner realizes those accepted responsibilities. It must not silently complete, weaken, strengthen, reinterpret, or replace them.

This NIB-S fixes:

- the implementation ecosystem boundary;
- physical application placement;
- system pipeline;
- system-level identity model;
- implementation module boundaries;
- cross-module types;
- ownership and persistence boundaries;
- recovery model;
- candidate and exact campaign identities;
- LLM-resource boundary;
- finding/evidence/adjudication boundary;
- mechanical-validation boundary;
- repair/re-review boundary;
- repository/publication boundary;
- configuration and secret boundary;
- human decision and operator-action boundary;
- external output contract;
- orchestration contract;
- dependency inventory;
- global invariants and cross-cutting policies.

It intentionally does not define module-internal algorithms. Those belong in NIB-M.

## 2. System objective

Build one isolated TypeScript/Node assurance-tooling application that mechanically executes the accepted Gate A hostile-review protocol over exact candidate repository states, persists and recovers execution without fabricating external outcomes, applies only exact protocol-authorized repairs, starts a full new review campaign whenever a repair changes the semantic subject `S`, and publishes only an exact mechanically qualified candidate.

## 3. Realization and product boundary

The runner is assurance tooling. It is not the TURNLOCK production runtime.

The selected implementation realization is:

```text
language       = TypeScript
runtime        = Node.js >= 20
module system  = ESM
type checking  = strict TypeScript
application    = isolated repository tool
```

Production TURNLOCK code must not depend on this TypeScript application merely because the runner is implemented in TypeScript.

The runner consumes `llm-runtime` in-process through one campaign-owned adapter.

The runner invokes existing Python validation authority out-of-process.

The runner invokes Git/repository mechanisms through an explicit repository boundary.

No artificial IPC layer is inserted between the runner and `llm-runtime`.

No Python validator logic is silently reimplemented in TypeScript.

## 4. Physical placement

The future implementation application root is exactly:

```text
tools/gate-a-campaign-runner/
```

The intended top-level structure is:

```text
tools/gate-a-campaign-runner/
├── package.json
├── tsconfig.json
├── src/
│   ├── cli.ts
│   ├── contracts/
│   ├── orchestrator/
│   ├── campaign-state/
│   ├── campaign-authority/
│   ├── cognitive-execution/
│   ├── assurance-ledger/
│   ├── mechanical-validation/
│   ├── repository-control/
│   └── recovery-operator/
└── tests/
```

This NIB-S selects the responsibility boundaries represented by those directories.

Issue #29 does not create any of them.

The complete NIB-M set must cover every implementation module listed here before GREEN work is decomposed.

## 5. System identity model

Three lifecycle identities must not be conflated.

### 5.1 RunnerSession

A `RunnerSession` is one process invocation of `run-gate-a-review`.

A session may:

* start a new `GateARun`;
* resume an existing `GateARun`;
* acquire or lose write ownership;
* reconcile work left by a previous session;
* terminate while the durable `GateARun` remains resumable.

A process lifetime is not semantic campaign identity.

### 5.2 GateARun

A `GateARun` is the durable top-level runner execution.

It owns:

* the initial repository authority from which construction began;
* the linear candidate lineage;
* exact review campaigns;
* obligations;
* WorkItems;
* Executions;
* evidence and findings;
* repairs;
* recovery history;
* blockers;
* Gate A qualification;
* publication state;
* terminal runner outcome.

A `GateARun` may orchestrate more than one exact hostile-review campaign because a protocol-authorized automatic repair may change `S`, making the previous exact campaign historical and requiring a full new campaign.

A `GateARun` does not allow a product-semantic decision to mutate its governing authority in place.

A genuine `DECISION-REQUIRED` terminates semantic progression of that run. After accepted repository authority changes, a later invocation starts a new `GateARun`.

### 5.3 ReviewCampaign

A `ReviewCampaign` is the exact protocol-defined hostile-review campaign.

Its production provenance is bound immutably to:

```text
the exact CandidateRevision, when the runner produced it
+
the exact repository authority where it was produced
+
one exact semantic subject S
+
one exact review protocol P
```

Campaign currentness is a separate relation determined only by the accepted exact pair `(S, P)`.

The candidate or repository authority recorded as campaign provenance does not participate in currentness. If the active candidate changes from `C0` to `C1` while `S` and `P` remain unchanged, every structurally valid campaign over that exact `(S, P)` remains current. The runner must not require a new campaign merely because CandidateRevision or repository commit identity changed.

More than one ReviewCampaign may be current for the same exact `(S, P)`. All current assurance-decomposition review records selected by the existing repository authority participate in surviving-finding evaluation, regardless of the candidate or repository state where each was produced.

A ReviewCampaign must never be retargeted to another candidate, repository authority, subject, or protocol. Current applicability to a later candidate with the same exact `(S, P)` does not rewrite provenance.

If an approved repair changes `S`, the previous ReviewCampaign set becomes historical for the successor subject and a full new ReviewCampaign over the successor candidate and new `S` is required.

A protocol change changes `P` without changing `S`. ReviewCampaigns bound to the previous `P` then become stale historical and cannot satisfy current Gate A. After reviewer/profile prerequisites have been established, the `GateARun` must create one full new ReviewCampaign over the active CandidateRevision and the same exact `S`, bound to the new current `P`.

That new ReviewCampaign must execute every protocol-required current-`P` campaign obligation. In addition, every finding from stale-protocol campaigns over the same `S` must be re-adjudicated under the new current `P` exactly as required by accepted hostile-review authority.

Historical evidence remains immutable. No result produced under stale `P` satisfies a current-`P` campaign requirement except through an explicit stale-protocol re-adjudication path authorized by the accepted protocol.

## 6. Candidate model

Candidate identity belongs to the `GateARun`, not to a fixed semantic subject.

Candidates form one active linear lineage:

```text
C0 → C1 → C2 → ... → Cn
```

Branching, merging, speculative parallel candidate trees, and candidate selection are outside the initial runner.

A `CandidateRevision` is:

* immutable after sealing;
* bound to one exact repository materialization;
* bound to one parent candidate except `C0`;
* bound to exact construction/repair provenance;
* assigned one exact derived semantic subject identity after sealing.

A mutable worktree under repair is not a CandidateRevision.

The construction boundary is:

```text
sealed CandidateRevision Cn
        ↓
exact qualified RepairIntent
        ↓
mutable CandidateDraft
        ↓
exact approved patch applied
        ↓
seal
        ↓
CandidateRevision Cn+1
        ↓
derive exact S(n+1)
```

No review evidence may target a mutable draft.

If:

```text
S(n+1) != S(n)
```

then the ReviewCampaign set for `S(n) / P` is historical for the successor subject and a full new campaign for `Cn+1 / S(n+1) / current P` is required.

If:

```text
S(n+1) == S(n)
AND
P(n+1) == P(n)
```

then CandidateRevision change alone does not make a campaign stale and does not require a new campaign. Campaign provenance remains bound to the exact candidate and repository authority where it was produced, while currentness remains derived from exact `(S, P)`.

The runner must never treat a repaired candidate that changes `S` as continuation of the old current campaign.

## 7. Authoritative state model

Authoritative runner state is not a single lifecycle enum.

It consists of durable:

```text
GateARun identity
CandidateRevision lineage
ReviewCampaign identities
authority-bearing facts
obligations
WorkItems
Executions
qualification records
finding/evidence references
repair records
Gate A mechanical qualification
publication records
operator-resolution records
terminal/supersession facts
```

The following are derived projections only:

```text
phase
enabled work
outstanding blockers
current candidate
current campaign set
external outcome
```

A `REVIEW`, `REPAIR`, `RECOVERY`, or `PUBLICATION` label may be used for diagnostics or UI but must not be authoritative progression state.

## 8. Facts, obligations, WorkItems, and Executions

These concepts are distinct.

### 8.1 Facts

Facts are immutable durable statements about what was established or observed.

Later facts may supersede the effective permission created by an earlier fact, but historical facts are not rewritten.

### 8.2 Obligations

An obligation states what still must be established or resolved.

Outstanding obligations are derived from durable state.

They never disappear merely because code stopped scheduling them.

### 8.3 WorkItems

A WorkItem is an immutable attributable unit of work derived from one or more obligations under accepted protocol rules.

A WorkItem is bound to exact immutable inputs.

It must never mean:

```text
review current candidate
```

It must identify the exact candidate, subject, protocol, role, and other required inputs.

The same logical derivation must be stably identifiable so restart cannot silently create duplicate work.

### 8.4 Executions

An Execution is one historically unique concrete attempt to perform one WorkItem.

Retries create new Executions.

A failed or unresolved Execution is not rewritten into a later successful attempt.

At most one non-terminal Execution exists for one WorkItem at one time in the initial runner.

Independent parallelism is expressed as independent WorkItems.

### 8.5 WorkItem satisfaction

A terminal or transport-successful Execution does not by itself satisfy its WorkItem.

A WorkItem is satisfied only when the exact result class required by that WorkItem has been durably captured and qualified under its governing contract.

WorkItem satisfaction does not itself imply that every Obligation using that result is satisfied.

## 9. Cognitive output and authority

Cognitive output is never authority merely because an LLM emitted it.

The structural pattern is:

```text
cognitive execution
      ↓
sealed output / proposal / claim
      ↓
protocol-defined validation or qualification
      ↓
authority-bearing campaign fact
```

The runner must not treat any of the following as implicit authority:

* model confidence;
* reviewer majority;
* agreement between models;
* absence of objection;
* absence of a finding;
* a free-form `PASS`;
* a repair synthesizer's assertion that its own repair is valid;
* a result merely because `llm-runtime` returned successfully.

A cognitive execution cannot be the sole authority that both proposes a semantic claim and certifies that claim as sufficient for progression.

## 10. Pipeline architecture

The complete top-level execution order is:

```text
CLI invocation
    ↓
RunnerSession creation
    ↓
start: atomically create GateARun + acquire initial fenced ownership in M2
resume: load GateARun + acquire successor fenced ownership in M2
    ↓
new-run preflight OR resume recovery barrier
    ↓
resolve exact baseline repository authority
    ↓
materialize/seal current CandidateRevision
    ↓
derive exact semantic subject S
    ↓
load/validate exact current protocol P
    ↓
enumerate the complete repository-selected campaign sets:
    current campaigns = every structurally valid campaign over exact (S, P)
    stale-protocol campaigns = every campaign over exact S and non-current P
    candidate/repository provenance does not filter either set
    ↓
determine whether accepted authority requires a new campaign:
    initial S with no current campaign
    OR subject changed
    OR protocol changed
    candidate-only change with unchanged (S, P) never requires one
    ↓
if a new campaign is required:
    verify all protocol-owned reviewer/profile prerequisites first
    if prerequisites are unavailable:
        create no ReviewCampaign
        materialize exact operational blocker
        OPERATOR-ACTION-REQUIRED
    otherwise:
        create exactly one full ReviewCampaign(candidate, S, P)
        schedule all current-P campaign work
        schedule required current-P re-adjudication of stale-protocol findings
    ↓
derive protocol-required WorkItems
    ↓
execute cognitive/mechanical work
    ↓
seal and admit exact execution results
    ↓
mechanical one-to-one finding normalization
    ↓
protocol adjudication / hostile challenge paths
    ↓
for every surviving material finding:
    ├─ valid refutation path
    ├─ uniquely derived correction path
    ├─ genuine semantic underdetermination/conflict
    └─ unresolved operational/epistemic path
    ↓
if uniquely derived repair is authorized:
    derive exact patch
    ↓
    hostile repair challenge
    ↓
    exact mechanical patch application
    ↓
    seal successor CandidateRevision
    ↓
    recompute S
    ↓
    if S changed:
        prior ReviewCampaign set becomes historical for the successor subject
        return to prerequisite verification before creating the required campaign
    else:
        retain the complete current campaign set for unchanged (S, P)
    ↓
if genuine semantic decision is required:
    DECISION-REQUIRED
    terminate semantic progression of this GateARun
    ↓
if safe automatic progression is operationally impossible:
    OPERATOR-ACTION-REQUIRED
    preserve resumable GateARun
    ↓
when current protocol evidence is complete:
    execute authoritative Python repository/Gate A validation
    ↓
admit exact GateAQualification for exact CandidateRevision and the complete
current/contributing campaign sets selected by repository authority
    ↓
construct PublicationIntent with exact publication target and authorized
fast-forward predecessor-to-successor transition
    ↓
revalidate effective publication permission
    ↓
conditionally mutate the exact target ref against the exact predecessor
    ↓
reconcile/confirm exact publication
    ↓
verify target, transition, and published materialization identity
    ↓
post-publication repository validation
    ↓
GATE-A-READY
```

The orchestrator may schedule independent enabled WorkItems concurrently where their contracts permit it.

Concurrency must not change the authoritative order of admitted facts or allow more than one authoritative writer.

## 11. Module architecture

The implementation contains exactly these system modules.

The CLI file is the external adapter for the orchestrator and is not a separate semantic module.

### M0 — `contracts`

Owns:

* all cross-module TypeScript contracts;
* runtime validation schemas for runner-owned serialized data;
* opaque identity/ref types;
* normal external result schemas.

It performs no I/O and makes no progression decisions.

### M1 — `orchestrator`

Owns:

* `run-gate-a-review` application orchestration;
* start/resume dispatch;
* selection among already-enabled WorkItems;
* sequencing calls across M2-M8;
* revalidation immediately before external dispatch;
* external outcome projection.

It may choose scheduling order among already-authorized WorkItems according to later NIB-M policy.

It may not invent WorkItems or semantic transitions.

### M2 — `campaign-state`

Owns:

* durable `GateARun` authoritative history;
* atomic new-run creation plus initial fenced write-ownership acquisition;
* immutable artifact references;
* authoritative state revision;
* fenced single-writer ownership;
* atomic authoritative transitions;
* stable logical identity registration;
* snapshot/projection reconstruction;
* integrity verification of retained provenance.

Only M2 commits authoritative runner-state mutations.

Other modules return proposals/results to M1; they do not mutate authoritative state directly.

### M3 — `campaign-authority`

Owns:

* repository/preflight authority resolution;
* exact baseline repository authority;
* exact Gate A semantic subject derivation/currentness;
* exact current protocol bundle identity/currentness;
* protocol-owned reviewer/profile admissibility prerequisites;
* detection of subject/protocol staleness;
* construction of exact per-campaign `ReviewContext` and complete `GateAEvaluationContext`.

It does not redefine any protocol rule.

It does not select unregistered reviewer profiles or models.

### M4 — `cognitive-execution`

Owns:

* the `CognitiveExecutionPort`;
* the sole direct import/use of `llm-runtime`;
* mapping from campaign Execution identity to `llm-runtime` call identity and provider-attempt evidence;
* dispatch/cancellation integration;
* raw result capture;
* exact runtime metadata needed by execution receipts;
* secret injection into the LLM dependency boundary.

It does not adjudicate semantic correctness.

It does not retry outside the exact behavior authorized by the protocol and the `llm-runtime` Dependency Contract.

### M5 — `assurance-ledger`

Owns:

* protocol-derived obligations and WorkItems;
* review-campaign artifact relationships;
* exact one-to-one finding normalization;
* finding/evidence provenance;
* materiality/refutation/challenge qualification;
* stale-protocol finding re-adjudication state;
* derivation, decision-necessity, repair, and decision-request qualification state;
* authority-preserving RepairIntent qualification;
* explicit finding, evidence, adjudication, re-adjudication, obligation-disposition, RepairIntent, and Decision Request products for M2 admission;
* determination that a candidate and its complete current/contributing campaign sets are ready to be submitted to mechanical Gate A validation.

It does not perform LLM calls.

It does not invoke Python validators.

It does not apply patches.

It does not declare Gate A READY independently of existing mechanical authority.

### M6 — `mechanical-validation`

Owns:

* subprocess invocation of existing repository Python validation authorities;
* exact capture of validator inputs, outputs, exit status, and candidate identity;
* admission-ready mechanical result artifacts;
* final mechanical Gate A qualification request for one exact sealed candidate;
* post-publication repository validation request.

It must invoke existing authorities rather than reimplementing them in TypeScript.

### M7 — `repository-control`

Owns:

* isolated mutable worktree/candidate workspace;
* candidate draft materialization;
* exact approved patch application with no semantic latitude;
* candidate sealing;
* candidate materialization identity;
* Git/repository inspection;
* PublicationIntent realization;
* conditional publication against the expected predecessor;
* publication reconciliation;
* exact published-candidate materialization proof.

It does not synthesize repairs.

It does not modify accepted patches.

It does not merge/rebase repository divergence unless a future accepted contract explicitly authorizes that exact operation.

### M8 — `recovery-operator`

Owns:

* recovery-barrier construction from complete unresolved-execution recovery descriptors;
* invocation of the exact executor-owned recovery capability through the common recovery port;
* unresolved external-effect reconciliation;
* operational blocker materialization;
* operator-resolution ingestion;
* operational supersession of unresolved executions when explicitly authorized;
* durable Decision Request and Operator Action Request presentation artifacts.

It does not answer a Decision Request.

It does not turn an operator action into semantic authority.

## 12. Canonical cross-module identity types

All IDs below are opaque validated strings.

```ts
type RunnerSessionId = string;
type GateARunId = string;
type CandidateRevisionId = string;
type ReviewCampaignId = string;
type ObligationId = string;
type WorkItemId = string;
type ExecutionId = string;
type FindingId = string;
type EvidenceId = string;
type RepairIntentId = string;
type AdjudicationId = string;
type ReAdjudicationId = string;
type DecisionRequestId = string;
type ReviewReadinessId = string;
type GateAQualificationId = string;
type PublicationIntentId = string;
type PublicationConfirmationId = string;
type BlockerId = string;
type ArtifactId = string;
type StateRevision = string;
type OwnershipGeneration = number;
type Sha256 = string;

type WorkExecutor =
  | "cognitive-execution"
  | "mechanical-validation"
  | "repository-control"
  | "recovery-operator";

type CognitiveExecutionRole =
  | "initial-reviewer"
  | "materiality-assessor"
  | "refutation-builder"
  | "challenge"
  | "discovery-classifier"
  | "derivation-builder"
  | "decision-necessity-challenger"
  | "repair-synthesizer"
  | "decision-projection";

interface ObligationRef {
  readonly obligationId: ObligationId;
  readonly runId: GateARunId;
  readonly candidateId: CandidateRevisionId | null;
  readonly reviewCampaignId: ReviewCampaignId | null;
  readonly definition: ArtifactRef;
}

interface WriteAuthorityRef {
  readonly runId: GateARunId;
  readonly sessionId: RunnerSessionId;
  readonly generation: OwnershipGeneration;
  readonly acquiredAtStateRevision: StateRevision;
}

interface AuthoritativeMutationRef {
  readonly schema: "gate-a-state-mutation.v1";
  readonly artifact: ArtifactRef;
}
```

`Sha256` is runtime-validated as the lowercase 64-hex representation required by repository hostile-review artifacts where SHA-256 identity is applicable.

Runner-internal opaque IDs are not required to be SHA-derived.

## 13. Canonical reference types

```ts
interface ArtifactRef {
  readonly artifactId: ArtifactId;
  readonly sha256: Sha256;
  readonly byteLength: number;
  readonly mediaType: string;
  readonly repositoryPath: string | null;
}

interface RepositoryAuthorityRef {
  readonly commitSha: string;
  readonly treeSha: string;
}

interface SemanticSubjectRef {
  readonly selector: "gate-a-assurance-decomposition-v1";
  readonly sha256: Sha256;
}

interface ProtocolBundleRef {
  readonly protocolId: string;
  readonly repositoryPath: string;
  readonly sha256: Sha256;
}

interface GateARunRef {
  readonly runId: GateARunId;
  readonly initialRepositoryAuthority: RepositoryAuthorityRef | null;
  readonly publicationTarget: RepositoryPublicationTargetRef | null;
}

`initialRepositoryAuthority` and `publicationTarget` are `null` only in the atomic bootstrap snapshot before preflight has established the exact baseline and credential-free publication target. Their first non-null values are committed together through M2 and are thereafter immutable.

interface CandidateRevisionRef {
  readonly candidateId: CandidateRevisionId;
  readonly runId: GateARunId;
  readonly ordinal: number;
  readonly parentCandidateId: CandidateRevisionId | null;
  readonly materialization: ArtifactRef;
  readonly semanticSubject: SemanticSubjectRef;
  readonly producedByRepairIntentId: RepairIntentId | null;
}

interface ReviewCampaignProvenanceRef {
  readonly originatingRunId: GateARunId | null;
  readonly candidateId: CandidateRevisionId | null;
  readonly repositoryAuthority: RepositoryAuthorityRef;
}

interface ReviewCampaignRef {
  readonly reviewCampaignId: ReviewCampaignId;
  readonly provenance: ReviewCampaignProvenanceRef;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
}

interface ReviewCampaignCurrentnessRef {
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly currentReviewCampaignIds: readonly ReviewCampaignId[];
  readonly staleProtocolReviewCampaignIds: readonly ReviewCampaignId[];
}

interface GateAQualificationRef {
  readonly qualificationId: GateAQualificationId;
  readonly candidateId: CandidateRevisionId;
  readonly currentReviewCampaignIds: readonly ReviewCampaignId[];
  readonly contributingReviewCampaignIds: readonly ReviewCampaignId[];
  readonly validatorEvidence: readonly ArtifactRef[];
}
```

`ReviewCampaignProvenanceRef` records the exact candidate/run identity when the runner produced the campaign and always records the exact repository authority where it was produced. Imported repository evidence may have null runner-local identities; it never has missing repository authority.

`currentReviewCampaignIds` is the complete ordered, duplicate-free set of structurally valid assurance-decomposition campaigns whose exact subject and protocol equal current `(S, P)`. Candidate, run, and repository provenance do not filter this set.

Malformed or referentially invalid review evidence is never silently filtered to obtain that set. Existing repository authority must first classify it as an integrity blocker, which prevents qualification.

`contributingReviewCampaignIds` is an ordered, duplicate-free superset of `currentReviewCampaignIds`. It also contains every stale-protocol campaign over the same `S` whose findings or current-protocol re-adjudications enter the mechanical Gate A qualification basis.

A stale-protocol campaign over the same `S` that has no finding or re-adjudication effect on the qualification basis is not included merely because it exists. A current campaign may never be omitted merely because another current campaign independently satisfies the minimum reviewer count.

```ts
interface RepositoryPublicationTargetRef {
  readonly repositoryIdentity: string;
  readonly remoteEndpoint: string;
  readonly refName: string;
}

interface AuthorizedGitTransitionRef {
  readonly target: RepositoryPublicationTargetRef;
  readonly predecessor: RepositoryAuthorityRef;
  readonly successor: RepositoryAuthorityRef;
  readonly relationship: "fast-forward";
  readonly ancestryEvidence: readonly ArtifactRef[];
}

interface PublicationIntentRef {
  readonly publicationIntentId: PublicationIntentId;
  readonly runId: GateARunId;
  readonly candidateId: CandidateRevisionId;
  readonly qualificationId: GateAQualificationId;
  readonly transition: AuthorizedGitTransitionRef;
  readonly preparationEvidence: readonly ArtifactRef[];
}

interface PreparedPublication {
  readonly runId: GateARunId;
  readonly candidateId: CandidateRevisionId;
  readonly qualificationId: GateAQualificationId;
  readonly transition: AuthorizedGitTransitionRef;
  readonly materialIdentityEvidence: readonly ArtifactRef[];
}

interface PublicationConfirmationRef {
  readonly publicationConfirmationId: PublicationConfirmationId;
  readonly publicationIntentId: PublicationIntentId;
  readonly transition: AuthorizedGitTransitionRef;
  readonly candidateId: CandidateRevisionId;
  readonly materialIdentityEvidence: readonly ArtifactRef[];
}
```

`RepositoryPublicationTargetRef` is the exact durable remote mutation target. `repositoryIdentity` identifies the repository independently of a local checkout, `remoteEndpoint` is the normalized credential-free publication endpoint, and `refName` is the fully qualified Git ref name. Credentials and credential-bearing URLs are invalid target identities.

A publication successor is an exact repository-authority identity, not merely a Git tree identity.

Before any remote publication mutation, M7 must prepare the exact immutable successor repository object locally, expose both its exact commit identity and exact tree identity through `RepositoryAuthorityRef`, and mechanically prove that the predecessor commit is an ancestor of the successor commit for the exact target. The initial runner authorizes only the `fast-forward` relationship.

A `PublicationIntentRef` that lacks the exact target, contains only a tree SHA, or lacks valid ancestry evidence is invalid. A compare-and-swap from `A` to an unrelated `C` is prohibited even when the target still equals `A`.

A repository path or local remote name is never sufficient as durable publication-target or immutable historical identity by itself.

## 14. Blocker types

```ts
interface SemanticBlocker {
  readonly kind: "semantic";
  readonly blockerId: BlockerId;
  readonly obligationId: ObligationId;
  readonly findingId: FindingId | null;
  readonly decisionRequestId: DecisionRequestId;
  readonly decisionRequest: ArtifactRef;
}

interface OperationalBlocker {
  readonly kind: "operational";
  readonly blockerId: BlockerId;
  readonly obligationId: ObligationId;
  readonly executionId: ExecutionId | null;
  readonly operatorRequest: ArtifactRef;
}

type CampaignBlocker = SemanticBlocker | OperationalBlocker;
```

Semantic and operational blockers may coexist.

Authoritative state retains the full blocker set.

The top-level output projection must not erase a blocker merely because only one outcome discriminator is emitted.

## 15. Work and execution boundary types

```ts
interface WorkItemRef {
  readonly workItemId: WorkItemId;
  readonly runId: GateARunId;
  readonly candidateId: CandidateRevisionId;
  readonly reviewCampaignId: ReviewCampaignId | null;
  readonly sourceObligationIds: readonly ObligationId[];
  readonly executor: WorkExecutor;
  readonly operation: ArtifactRef;
  readonly inputRefs: readonly ArtifactRef[];
}
```

`executor` is the complete system-level dispatch routing decision.

`operation` is one immutable runtime-validated operation specification owned by the selected executor module. Its module-internal schema and algorithm belong to that module's NIB-M.

M1 may not reinterpret an operation or route a WorkItem to a different executor.

```ts
interface ExecutionRef {
  readonly executionId: ExecutionId;
  readonly workItemId: WorkItemId;
  readonly attemptOrdinal: number;
}

interface CapturedExecutionResult {
  readonly execution: ExecutionRef;
  readonly rawResult: ArtifactRef;
  readonly runtimeEvidence: readonly ArtifactRef[];
}

interface TechnicalExecutionFailure {
  readonly execution: ExecutionRef;
  readonly completedResponse: false;
  readonly failureEvidence: readonly ArtifactRef[];
}

type DurableDispatchState =
  | "AUTHORIZED-NOT-DISPATCHED"
  | "POSSIBLY-DISPATCHED"
  | "OBSERVED-RESULT";

interface RecoveryCapabilityRef {
  readonly executor: WorkExecutor;
  readonly reconciliationOperation: ArtifactRef;
}

interface UnresolvedExecutionRecoveryRef {
  readonly execution: ExecutionRef;
  readonly workItem: WorkItemRef;
  readonly dispatchState: DurableDispatchState;
  readonly dispatchIntent: ArtifactRef;
  readonly dispatchEvidence: readonly ArtifactRef[];
  readonly capturedResult: CapturedExecutionResult | TechnicalExecutionFailure | null;
  readonly recoveryCapability: RecoveryCapabilityRef | null;
}

type ExecutionRecoveryObservation =
  | {
      readonly kind: "not-executed";
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly kind: "completed";
      readonly result: CapturedExecutionResult;
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly kind: "pending";
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly kind: "unknown";
      readonly evidence: readonly ArtifactRef[];
    };

interface ExecutionRecoveryPort {
  reconcile(
    unresolved: UnresolvedExecutionRecoveryRef
  ): Promise<ExecutionRecoveryObservation>;
}

type ExecutionRecoveryResolution =
  | {
      readonly executionId: ExecutionId;
      readonly classification: "PROVEN-NOT-EXECUTED";
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly executionId: ExecutionId;
      readonly classification: "PROVEN-COMPLETED";
      readonly recoveredResult: CapturedExecutionResult;
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly executionId: ExecutionId;
      readonly classification: "RECONCILABLE";
      readonly recoveryCapability: RecoveryCapabilityRef;
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly executionId: ExecutionId;
      readonly classification: "UNRESOLVABLE";
      readonly blocker: OperationalBlocker;
      readonly evidence: readonly ArtifactRef[];
    };
```

A captured result is durable material.

It is not automatically an authority-bearing semantic result.

`TechnicalExecutionFailure` means that no completed semantic response exists. It is distinct from an uncertain capture: a known no-response technical failure is not an unknown external-effect outcome, and it carries no `rawResult`.

An uncertain capture carries the complete `UnresolvedExecutionRecoveryRef` produced by the owning executor, so durable recovery never depends on an executor-specific query invented later. The executor reports the WorkItem, durable dispatch state, dispatch intent and evidence, any captured result, and its exact recovery capability. It does not assign a recovery classification. M8 derives that classification from the descriptor and the executor's `ExecutionRecoveryPort` observation.

A technical failure never satisfies the WorkItem. M5 may derive a replacement Execution only where the exact role-specific protocol retry rule permits another attempt.

## 16. Module boundary request/result types

### M0

M0 is a pure contracts/schema module.

It consumes no runtime request and performs no I/O.

It exports the cross-module types in this System Brief, runtime validators for runner-owned serialized forms, and the immutable root preflight-obligation definition used only by M2 bootstrap.

Protocol-owned artifacts remain validated by their existing authoritative schemas/mechanical validators rather than by an invented M0 replacement.

### M1

```ts
interface StartRunnerCommand {
  readonly mode: "start";
  readonly repositoryPath: string;
}

interface ResumeRunnerCommand {
  readonly mode: "resume";
  readonly repositoryPath: string;
  readonly runId: GateARunId;
  readonly operatorResolutionPath: string | null;
}

type RunnerCommand = StartRunnerCommand | ResumeRunnerCommand;

interface RunOrchestrator {
  run(command: RunnerCommand): Promise<RunnerResult>;
}
```

`RunnerResult` is the exact union defined by §35.

Only normal contract termination resolves `RunOrchestrator.run` with a `RunnerResult`.

An implementation/process/integrity failure that prevents production of a valid normal result rejects/fails the invocation and is handled by the CLI as the non-zero process path defined in §36.

### M2

```ts
interface CreateGateARunAndAcquireInitialOwnershipRequest {
  readonly repositoryPath: string;
  readonly sessionId: RunnerSessionId;
  readonly preflightObligationDefinition: ArtifactRef;
}

type CreateGateARunAndAcquireInitialOwnershipResult =
  | {
      readonly kind: "created";
      readonly run: GateARunRef;
      readonly authority: WriteAuthorityRef;
      readonly preflightObligation: ObligationRef;
      readonly snapshot: GateARunSnapshot;
    }
  | {
      readonly kind: "rejected";
      readonly reason: "INTEGRITY_FAILURE";
    };

interface AcquireWriteOwnershipRequest {
  readonly runId: GateARunId;
  readonly sessionId: RunnerSessionId;
  readonly expectedStateRevision: StateRevision | null;
}

type AcquireWriteOwnershipResult =
  | {
      readonly kind: "acquired";
      readonly authority: WriteAuthorityRef;
      readonly snapshot: GateARunSnapshot;
    }
  | {
      readonly kind: "rejected";
      readonly reason:
        | "STALE_STATE"
        | "ACTIVE_OWNER_CONFLICT"
        | "INTEGRITY_FAILURE";
      readonly currentStateRevision: StateRevision;
    };

interface LoadGateARunSnapshotRequest {
  readonly runId: GateARunId;
}

interface GateARunSnapshot {
  readonly run: GateARunRef;
  readonly stateRevision: StateRevision;
  readonly currentCandidate: CandidateRevisionRef | null;
  readonly reviewCampaigns: readonly ReviewCampaignRef[];
  readonly campaignCurrentness: ReviewCampaignCurrentnessRef | null;
  readonly obligations: readonly ObligationRef[];
  readonly obligationDispositions: readonly ObligationDispositionRef[];
  readonly workItems: readonly WorkItemRef[];
  readonly executions: readonly ExecutionRef[];
  readonly capturedExecutionResults: readonly CapturedExecutionResult[];
  readonly technicalExecutionFailures: readonly TechnicalExecutionFailure[];
  readonly unresolvedExecutions: readonly UnresolvedExecutionRecoveryRef[];
  readonly evidence: readonly EvidenceRef[];
  readonly findings: readonly FindingRef[];
  readonly adjudications: readonly AdjudicationRef[];
  readonly reAdjudications: readonly ReAdjudicationRef[];
  readonly repairIntents: readonly RepairIntentRef[];
  readonly decisionRequests: readonly DecisionRequestRef[];
  readonly candidateReviewReadiness: CandidateReviewReadinessRef | null;
  readonly blockers: readonly CampaignBlocker[];
  readonly gateQualification: GateAQualificationRef | null;
  readonly publicationIntent: PublicationIntentRef | null;
  readonly publicationConfirmation: PublicationConfirmationRef | null;
  readonly semanticProgressionTerminal: boolean;
  readonly gateAReady: boolean;
}

interface CommitAuthoritativeMutationRequest {
  readonly runId: GateARunId;
  readonly authority: WriteAuthorityRef;
  readonly expectedStateRevision: StateRevision;
  readonly mutation: AuthoritativeMutationRef;
}

type CommitAuthoritativeMutationResult =
  | {
      readonly kind: "committed";
      readonly newStateRevision: StateRevision;
      readonly snapshot: GateARunSnapshot;
    }
  | {
      readonly kind: "stale-state";
      readonly currentStateRevision: StateRevision;
    }
  | {
      readonly kind: "ownership-lost";
      readonly currentOwnershipGeneration: OwnershipGeneration;
    };
```

`CreateGateARunAndAcquireInitialOwnershipResult.kind = "created"` atomically persists the first `GateARun` revision, its initial fenced owner, and the root obligation to establish exact baseline authority, publication target, and current protocol or record exact preflight blockers. No separately visible run-without-owner or run-without-root-obligation state exists.

The request must use M0's exact immutable preflight-obligation definition. M2 assigns its run-local identity and registers it; M2 does not invent another obligation meaning.

`AcquireWriteOwnershipResult.kind = "acquired"` is the only result that grants successor-session mutation authority.

`LoadGateARunSnapshotRequest` is read-only.

`CreateGateARunAndAcquireInitialOwnershipRequest` is the only M2 bootstrap write boundary. After bootstrap, `CommitAuthoritativeMutationRequest` is the only M2 cross-module state-mutation boundary; ownership acquisition issues a `WriteAuthorityRef` under M2's fence but is not a campaign-state mutation path.

The exact mutation payload union carried by `AuthoritativeMutationRef.artifact` belongs to the M2 NIB-M, but it must implement only the authoritative facts and transitions already selected by this NIB-S. NIB-M may not introduce another writer or another write path.

Every successful commit returns the new exact `StateRevision` and the resulting authoritative snapshot.

No other module writes authoritative campaign state directly.

### M3

```ts
interface PreflightRequest {
  readonly runId: GateARunId;
  readonly repositoryPath: string;
}

type PreflightResolution =
  | {
      readonly kind: "established";
      readonly baselineAuthority: RepositoryAuthorityRef;
      readonly publicationTarget: RepositoryPublicationTargetRef;
      readonly protocolBundle: ProtocolBundleRef;
    }
  | {
      readonly kind: "blocked";
      readonly blockers: readonly OperationalBlocker[];
    };

interface ReviewContext {
  readonly runId: GateARunId;
  readonly candidate: CandidateRevisionRef;
  readonly campaign: ReviewCampaignRef;
}

interface GateAEvaluationContext {
  readonly runId: GateARunId;
  readonly qualificationCandidate: CandidateRevisionRef;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly currentCampaigns: readonly ReviewCampaignRef[];
  readonly staleProtocolCampaigns: readonly ReviewCampaignRef[];
}

interface ReviewerPrerequisiteRequest {
  readonly candidate: CandidateRevisionRef;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
}

type ReviewerPrerequisiteResolution =
  | {
      readonly kind: "established";
      readonly qualifyingReviewerProfileIds: readonly string[];
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly kind: "blocked";
      readonly blockers: readonly OperationalBlocker[];
    };

type ReviewCurrentnessResolution =
  | {
      readonly kind: "current";
      readonly context: GateAEvaluationContext;
    }
  | {
      readonly kind: "campaign-required";
      readonly reason: "INITIAL" | "SUBJECT-CHANGED" | "PROTOCOL-CHANGED";
      readonly candidate: CandidateRevisionRef;
      readonly semanticSubject: SemanticSubjectRef;
      readonly currentProtocolBundle: ProtocolBundleRef;
      readonly staleProtocolCampaigns: readonly ReviewCampaignRef[];
    }
  | {
      readonly kind: "blocked";
      readonly blockers: readonly OperationalBlocker[];
    };
```

M3 selects current campaigns solely by exact `(S, P)` through existing repository authority. Candidate, run, and repository provenance never filter `currentCampaigns`. Invalid evidence yields `blocked`; M3 must not omit it and continue with a convenient subset.

A `ReviewContext` used for new execution must use the exact production candidate recorded by its runner-owned campaign provenance. Reusing a current campaign to qualify a later same-`(S, P)` candidate does not create new executions under rewritten provenance.

`campaign-required` is never emitted for CandidateRevision change alone when exact `(S, P)` is unchanged and at least one current campaign exists.

For every `campaign-required` result, M1 must obtain `ReviewerPrerequisiteResolution.kind = "established"` before committing a new ReviewCampaign. A blocked prerequisite creates no campaign and projects `OPERATOR-ACTION-REQUIRED` after the blockers are committed.

`established` is valid only when the exact protocol bundle registers a non-empty set of `frontier_eligible == true` reviewer profiles that satisfies every protocol-declared reviewer-qualification prerequisite for the required review class, and `qualifyingReviewerProfileIds` is the exact duplicate-free subser of those registered profile IDs. An empty or insufficient registered set MUST be `blocked` with exact operational blockers. M1 and M3 never establish a resolution from runner configuration, environment, or a model alias absent from the protocol bundle.

`PROTOCOL-CHANGED` requires one full new current-`P` campaign plus accepted stale-protocol re-adjudication. It is not permission to mutate any old ReviewCampaign.

### M4

```ts
interface CognitiveExecutionRequest {
  readonly execution: ExecutionRef;
  readonly reviewContext: ReviewContext;
  readonly role: CognitiveExecutionRole;
  readonly reviewerProfileId: string;
  readonly prompt: ArtifactRef;
  readonly packet: ArtifactRef;
}

type CognitiveExecutionCapture =
  | {
      readonly kind: "captured";
      readonly value: CapturedExecutionResult;
    }
  | {
      readonly kind: "technical-failure";
      readonly value: TechnicalExecutionFailure;
    }
  | {
      readonly kind: "uncertain";
      readonly value: UnresolvedExecutionRecoveryRef;
    };
```

### M5

```ts
interface EvidenceRef {
  readonly evidenceId: EvidenceId;
  readonly runId: GateARunId;
  readonly candidateId: CandidateRevisionId | null;
  readonly reviewCampaignId: ReviewCampaignId | null;
  readonly sourceExecutionIds: readonly ExecutionId[];
  readonly artifact: ArtifactRef;
}

interface FindingRef {
  readonly findingId: FindingId;
  readonly runId: GateARunId;
  readonly candidateId: CandidateRevisionId | null;
  readonly reviewCampaignId: ReviewCampaignId;
  readonly sourceExecutionId: ExecutionId;
  readonly rawFindingId: string;
  readonly normalizedFinding: ArtifactRef;
  readonly evidenceIds: readonly EvidenceId[];
}

type AdjudicationKind =
  | "materiality"
  | "refutation"
  | "hostile-challenge"
  | "derivation"
  | "decision-necessity"
  | "repair-challenge"
  | "decision-projection";

interface AdjudicationRef {
  readonly adjudicationId: AdjudicationId;
  readonly kind: AdjudicationKind;
  readonly findingId: FindingId;
  readonly reviewCampaignId: ReviewCampaignId;
  readonly sourceExecutionIds: readonly ExecutionId[];
  readonly artifact: ArtifactRef;
  readonly evidenceIds: readonly EvidenceId[];
}

interface ReAdjudicationRef {
  readonly reAdjudicationId: ReAdjudicationId;
  readonly sourceReviewCampaignId: ReviewCampaignId;
  readonly sourceFindingId: FindingId;
  readonly currentProtocolBundle: ProtocolBundleRef;
  readonly sourceFindingSha256: Sha256;
  readonly artifact: ArtifactRef;
  readonly evidenceIds: readonly EvidenceId[];
}

type ObligationDispositionRef =
  | {
      readonly kind: "satisfied";
      readonly obligationId: ObligationId;
      readonly basisEvidenceIds: readonly EvidenceId[];
      readonly basisArtifacts: readonly ArtifactRef[];
    }
  | {
      readonly kind: "superseded";
      readonly obligationId: ObligationId;
      readonly replacementObligationIds: readonly ObligationId[];
      readonly basisEvidenceIds: readonly EvidenceId[];
      readonly basisArtifacts: readonly ArtifactRef[];
    };

interface RepairIntentRef {
  readonly repairIntentId: RepairIntentId;
  readonly runId: GateARunId;
  readonly candidateId: CandidateRevisionId;
  readonly findingId: FindingId;
  readonly approvedPatch: ArtifactRef;
  readonly qualificationEvidenceIds: readonly EvidenceId[];
  readonly qualificationArtifacts: readonly ArtifactRef[];
}

interface DecisionRequestRef {
  readonly decisionRequestId: DecisionRequestId;
  readonly runId: GateARunId;
  readonly findingId: FindingId;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly request: ArtifactRef;
  readonly qualificationEvidenceIds: readonly EvidenceId[];
}

interface CandidateReviewReadinessRef {
  readonly reviewReadinessId: ReviewReadinessId;
  readonly candidateId: CandidateRevisionId;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly currentReviewCampaignIds: readonly ReviewCampaignId[];
  readonly contributingReviewCampaignIds: readonly ReviewCampaignId[];
  readonly basisArtifacts: readonly ArtifactRef[];
}

interface AssuranceDerivationRequest {
  readonly evaluationContext: GateAEvaluationContext;
  readonly snapshot: GateARunSnapshot;
  readonly newlyCapturedResults: readonly CapturedExecutionResult[];
  readonly newlyKnownTechnicalFailures: readonly TechnicalExecutionFailure[];
  readonly admittedArtifacts: readonly ArtifactRef[];
}

interface AssuranceLedgerDelta {
  readonly expectedStateRevision: StateRevision;
  readonly evidenceToEstablish: readonly EvidenceRef[];
  readonly findingsToEstablish: readonly FindingRef[];
  readonly adjudicationsToEstablish: readonly AdjudicationRef[];
  readonly reAdjudicationsToEstablish: readonly ReAdjudicationRef[];
  readonly obligationDispositions: readonly ObligationDispositionRef[];
  readonly repairIntentsToQualify: readonly RepairIntentRef[];
  readonly decisionRequestsToEstablish: readonly DecisionRequestRef[];
  readonly obligationsToAdd: readonly ObligationRef[];
  readonly workItemsToAdd: readonly WorkItemRef[];
  readonly blockersToAdd: readonly CampaignBlocker[];
  readonly candidateReviewReadiness: CandidateReviewReadinessRef | null;
}
```

M5 must return every cross-module ledger product it establishes. It may not hide a finding, evidence admission, adjudication, re-adjudication, obligation satisfaction/supersession, qualified RepairIntent, qualified Decision Request, or candidate-review-readiness determination behind only a new WorkItem or blocker.

M2 returns those admitted products in `GateARunSnapshot`; M5 receives the complete prior ledger plus exact newly captured results and technical failures. No module may reconstruct the ledger by rescanning mutable workspaces.

M5 must return complete cross-module `ObligationRef` values, not bare newly invented IDs.

`ObligationRef.definition` points to the immutable runtime-validated obligation definition that M2 registers in authoritative history.

The internal serialized schemas and algorithms for these exact product categories belong to M5 NIB-M. NIB-M may refine their internal artifact payloads but may not remove, merge, or invent another cross-module category.

The cross-module rule is fixed: M5 returns one `AssuranceLedgerDelta`. It never commits state directly.

### M6

```ts
type MechanicalValidationRequest =
  | {
      readonly kind: "repository-integrity";
      readonly runId: GateARunId;
      readonly candidate: CandidateRevisionRef;
      readonly repositoryPath: string;
    }
  | {
      readonly kind: "gate-a-qualification";
      readonly runId: GateARunId;
      readonly candidate: CandidateRevisionRef;
      readonly repositoryPath: string;
      readonly reviewReadiness: CandidateReviewReadinessRef;
    }
  | {
      readonly kind: "post-publication-integrity";
      readonly runId: GateARunId;
      readonly candidate: CandidateRevisionRef;
      readonly repositoryPath: string;
    };

interface MechanicalValidationResult {
  readonly requestKind: MechanicalValidationRequest["kind"];
  readonly candidateId: CandidateRevisionId;
  readonly passed: boolean;
  readonly currentReviewCampaignIds: readonly ReviewCampaignId[];
  readonly contributingReviewCampaignIds: readonly ReviewCampaignId[];
  readonly evidence: readonly ArtifactRef[];
}
```

For `gate-a-qualification`, `reviewReadiness` must name the same candidate as the request, and both campaign-ID lists in the result must equal the complete ordered lists in `reviewReadiness` and obey `GateAQualificationRef` completeness rules.

For the other two validation kinds, both campaign-ID lists are empty.

### M7

```ts
interface CandidateConstructionRequest {
  readonly runId: GateARunId;
  readonly sourceCandidate: CandidateRevisionRef;
  readonly repairIntentId: RepairIntentId;
  readonly approvedPatch: ArtifactRef;
}

interface CandidateSealResult {
  readonly candidate: CandidateRevisionRef;
  readonly materializationEvidence: readonly ArtifactRef[];
}

interface PublicationPreparationRequest {
  readonly runId: GateARunId;
  readonly candidate: CandidateRevisionRef;
  readonly qualification: GateAQualificationRef;
  readonly target: RepositoryPublicationTargetRef;
  readonly expectedPredecessor: RepositoryAuthorityRef;
}

type PublicationPreparationResult =
  | {
      readonly kind: "prepared";
      readonly publication: PreparedPublication;
    }
  | {
      readonly kind: "blocked";
      readonly blocker: OperationalBlocker;
    };

interface PublicationRequest {
  readonly intent: PublicationIntentRef;
  readonly candidate: CandidateRevisionRef;
}

type PublicationEffectResult =
  | {
      readonly kind: "confirmed";
      readonly confirmation: PublicationConfirmationRef;
    }
  | {
      readonly kind: "reconcilable";
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly kind: "unresolvable";
      readonly blocker: OperationalBlocker;
    };
```

Publication preparation is a local repository operation.

It constructs the exact immutable successor repository object without mutating the remote publication target.

The resulting exact target, successor commit SHA, successor tree SHA, and fast-forward ancestry proof are known before `PublicationIntentRef` is committed.

Only after that exact intent is durable may M7 attempt the conditional mutation of the exact target ref.

### M8

```ts
interface RecoveryRequest {
  readonly runId: GateARunId;
  readonly stateRevision: StateRevision;
  readonly newOwnershipGeneration: OwnershipGeneration;
  readonly unresolvedExecutions: readonly UnresolvedExecutionRecoveryRef[];
}

interface RecoveryPlan {
  readonly expectedStateRevision: StateRevision;
  readonly resolutions: readonly ExecutionRecoveryResolution[];
  readonly remainingBlockers: readonly OperationalBlocker[];
}

interface ClassifyUnresolvedExecutionRequest {
  readonly runId: GateARunId;
  readonly unresolvedExecution: UnresolvedExecutionRecoveryRef;
}

type ClassifyUnresolvedExecutionResult = ExecutionRecoveryResolution;

interface OperatorResolutionEnvelope {
  readonly schema: "gate-a-operator-resolution.v1";
  readonly runId: GateARunId;
  readonly blockerId: BlockerId;
  readonly resolution: ArtifactRef;
}
```

For every unresolved execution, M8 must use the descriptor's exact dispatch evidence, captured result, and recovery capability. It calls the common `ExecutionRecoveryPort` implemented by the owning executor and returns exactly one `ExecutionRecoveryResolution`. It must not invent an executor-specific M2 query or infer non-execution from missing result material.

The same classification path serves the restart barrier (`RecoveryRequest`) and in-session uncertainty (`ClassifyUnresolvedExecutionRequest`). M8 never returns more than one resolution per descriptor and never converts a missing observation into `PROVEN-NOT-EXECUTED`.

The mapping is exact:

```text
not-executed observation with proof
→ PROVEN-NOT-EXECUTED

completed observation with captured result
→ PROVEN-COMPLETED

pending observation with retained recovery capability
→ RECONCILABLE

unknown observation, missing required proof, or no usable capability for a
possibly-dispatched execution
→ UNRESOLVABLE + exact OperationalBlocker
```

`resolution` is one immutable runtime-validated operator-resolution artifact.

The exact operator-resolution artifact union belongs to the M8 NIB-M because it depends on the exact recovery cases selected there.

That NIB-M must define the complete closed union before GREEN. The coding agent may not invent a resolution kind.

No operator-resolution artifact may create semantic authority.

## 17. Persistence boundary

The physical persistence engine is intentionally not selected by NIB-S.

M2 NIB-M must select an implementation that satisfies all of these system properties.

The logical persistence model has three distinct roles:

```text
Authoritative History
Immutable Durable Artifacts
Mutable Execution Workspace
```

### Authoritative History

Contains the facts and references required to reconstruct authoritative `GateARun` state.

### Immutable Durable Artifacts

Contains immutable material such as:

* sealed candidate manifests/materializations;
* exact LLM outputs;
* execution receipts;
* validator outputs;
* evidence;
* decision/operator request artifacts;
* provenance material.

Durability does not itself grant authority.

### Mutable Execution Workspace

Contains worktrees, candidate drafts, temporary subprocess material, and other mutable operational state.

A worktree is not the campaign database.

A cached snapshot is not the final authority unless the selected persistence design mechanically establishes that role under M2's contract.

## 18. Ownership and authoritative mutation

Each `GateARun` has at most one authoritative writer at one time.

Write ownership may move between RunnerSessions.

Former owners must be fenced from later authoritative writes.

The first authoritative mutation is the M2 atomic bootstrap:

```text
create GateARun
+
commit initial StateRevision
+
acquire initial fenced WriteAuthorityRef
```

No `WriteAuthorityRef` can pre-exist that atomic operation, and no separately visible unowned `GateARun` may be created.

Every later authoritative mutation is conditional on:

```text
current WriteAuthorityRef
+
exact expected StateRevision
```

A stale transition must fail rather than overwrite newer authority.

Concurrent external work may run in parallel.

Its results cannot directly mutate authoritative state.

Only M2 commits authoritative state changes, under orchestration by M1.

## 19. External-effect dispatch and recovery

Externally effectful work must have durable intent before dispatch.

The runner distinguishes:

```text
planned
authorized-to-dispatch
possibly-dispatched
observed-result
durable-result
reconciled
```

The exact persisted representation belongs to NIB-M.

The semantic requirements do not.

The following invariants are mandatory:

```text
absence of success != failure
failure != unknown
unknown != safe to retry
cancellation != rollback
new owner != proof old effect stopped
```

The recovery classifications are exactly:

```text
PROVEN-NOT-EXECUTED
PROVEN-COMPLETED
RECONCILABLE
UNRESOLVABLE
```

A possibly executed unresolved cognitive execution may not be blindly retried.

M4, M6, and M7 each implement `ExecutionRecoveryPort` for the external effects they dispatch. M8 is the sole recovery-barrier consumer of those ports. An executor may report evidence through its port; it may not commit a recovery classification or authoritative state directly.

If an outcome cannot be established, automatic progression stops with `OPERATOR-ACTION-REQUIRED`.

## 20. Recovery barrier

A session taking ownership of an existing `GateARun` must cross a recovery barrier before it normally dispatches new campaign effects.

The barrier consumes each complete `UnresolvedExecutionRecoveryRef`, including its WorkItem, durable dispatch state, dispatch intent/evidence, any captured result, and exact executor-owned recovery capability.

The barrier must:

```text
load verifiable durable authority
→ enumerate complete unresolved-execution recovery descriptors
→ invoke each available exact executor recovery capability
→ classify every unresolved execution exactly once
→ preserve recovered completed results for ordinary admission
→ materialize blockers for unresolvable executions
→ reconstruct obligations
→ derive enabled WorkItems
→ only then permit normal dispatch
```

M8 may not invent an additional M2 lookup API, reconstruct dispatch identity from an `ExecutionRef`, or classify an execution from absence of a result alone.

Ownership transfer never resets a possibly executed operation to not executed.

If an operator explicitly supersedes an unresolved Execution and authorizes a replacement Execution, a later result from the superseded execution may remain auditable but may not silently re-enter authoritative progression.

## 21. `llm-runtime` boundary

Only M4 imports `llm-runtime`.

All other modules depend on M0 contracts and the M4 port.

The future `llm-runtime` Dependency Contract must close at least:

```text
Campaign WorkItem
→ Campaign Execution
→ llm-runtime call
→ provider attempt(s)
```

and must define:

* call identity;
* provider-attempt identity;
* dispatch boundary;
* internal retry behavior;
* cancellation guarantees;
* result identity;
* provider response identity where available;
* observable attempt history;
* recovery/reconciliation capability;
* behavior when runner execution authority is revoked.

A dependency capable of autonomous retry may not begin a new provider attempt after the owning caller's campaign execution authority has been revoked.

An already-dispatched provider attempt remains a reconciliation concern.

## 22. Protocol-owned cognitive execution constraints

The runner does not create its own review semantics.

For protocol executions it must preserve the current accepted properties including:

```text
exact S
exact P
exact canonical packet
exact canonical prompt
protocol-owned reviewer profile
evidence-derived model identity
isolated execution context
no cross-reviewer visibility before seal
tools disabled where the protocol requires them disabled
complete required attack coverage per qualifying initial reviewer
sealed completed responses
role-specific attempt admissibility
```

The runner never upgrades an unregistered model/profile into a qualifying reviewer.

If the current protocol cannot supply a qualifying reviewer set satisfying Gate A requirements, the runner returns `OPERATOR-ACTION-REQUIRED`.

It does not invent reviewer profiles.

## 23. Finding and evidence boundary

Findings and evidence remain bound to the exact ReviewCampaign provenance against which they were produced, including its production candidate when runner-owned and its exact repository authority.

Current applicability is separately derived from exact `(S, P)`. A finding is never retargeted to a repaired candidate, but a campaign over unchanged exact `(S, P)` remains current even when the active CandidateRevision or repository commit differs from its provenance.

A repair that changes `S` creates a new candidate and requires a new full campaign over the changed subject.

Historical campaign evidence remains historical evidence.

Protocol changes never erase findings.

Stale-protocol findings over the same `S` retain the current re-adjudication requirements from accepted authority.

The runner must preserve exact one-to-one raw finding normalization.

It may not semantically merge or deduplicate raw findings when the current evidence contract forbids that transformation.

## 24. Repair boundary

An automatic repair is allowed only after the accepted protocol has established all required authorization predicates.

At system level, the required chain is:

```text
material finding
↓
attempt accepted closure/refutation path
↓
if correction path is required:
  existing authority uniquely determines correction
↓
derivation survives hostile challenge
↓
exact candidate patch is synthesized
↓
exact patch survives repair challenge
↓
RepairIntent becomes effective
↓
M7 applies the exact approved patch with no semantic latitude
```

The repair executor may not modify the approved patch.

A RepairIntent may not silently expand its own semantic scope.

A repair must not change the judging rules under which that same campaign is evaluated.

If a proposed change requires new product-semantic authority, the repair path stops and produces a Decision Request.

## 25. Decision boundary

`DECISION-REQUIRED` is reserved for the accepted semantic boundary:

```text
genuine product-semantic underdetermination
or
genuine unresolved product-authority conflict
```

Before that outcome is emitted, the existing protocol-required attempt to derive a unique answer from existing authority must have been exhausted.

A Decision Request is bound to:

```text
full current S
full current P
exact finding
```

The runner does not accept an interactive yes/no answer as new semantic authority.

The current `GateARun` does not mutate its semantic authority in place after a decision.

An accepted semantic decision must first be materialized through the repository authority mechanism that owns that decision.

A later invocation then starts a new `GateARun` from the new authority.

## 26. Operator boundary

`OPERATOR-ACTION-REQUIRED` means safe automatic progression is impossible without an operational or epistemic assumption that current evidence does not justify.

Examples of the class include:

* unresolved possibly-dispatched non-reconcilable execution;
* unavailable required provider credential;
* insufficient qualifying reviewer configuration under current P;
* repository publication divergence;
* corrupted/missing required durable provenance;
* an operational state for which no accepted automatic continuation exists.

Operator authority is operational only.

It may not resolve a product-semantic gap.

Operator-authorized repetition after an unresolved Execution is a new Execution with explicit provenance.

The unresolved historical Execution is not rewritten as failed or absent.

## 27. Mechanical validation and Gate A qualification

The runner does not define an independent Gate A acceptance algorithm.

Existing repository mechanical authorities remain authoritative for the exact checks they own.

M6 invokes them against one exact sealed candidate workspace.

A candidate becomes publication-eligible only after:

```text
runner-required campaign work for that exact candidate is closed
AND
all required evidence artifacts are materialized
AND
no unresolved runner execution can still alter the qualification basis
AND
canonical repository validation passes
AND
the existing formal traceability/review-evidence authority reports Gate A ready
for that exact candidate state
```

The resulting runner fact is a `GateAQualificationRef`.

That qualification binds the complete ordered set of all current ReviewCampaigns over exact `(S, P)` and the complete ordered set of ReviewCampaigns whose current evidence or stale-protocol re-adjudication actually contributes to the mechanical Gate A result.

The runner must not collapse currentness or provenance to one campaign merely because one current campaign independently satisfies the minimum reviewer count.

It is a provenance-bearing admission of mechanical authority for that exact candidate.

It is not an independently invented TypeScript gate algorithm.

A validation result for `Cn` never qualifies `Cn+1`.

## 28. Candidate purity of qualification

Every input used to establish a Gate A qualification for candidate `Cn` must be:

```text
directly scoped to Cn
```

or admitted through an existing accepted protocol mechanism that explicitly preserves applicability.

Evidence from an earlier semantic subject may not be silently inherited across a repair that changed `S`.

A full new ReviewCampaign is required after such a change.

Candidate or repository revision change with unchanged exact `(S, P)` is not subject change. In that case the accepted repository currentness rule, rather than candidate provenance, determines campaign applicability.

## 29. Repository and publication boundary

Publication is separate from qualification.

A qualified candidate is not yet repository authority.

Publication consumes exactly:

```text
one GateAQualificationRef
+
the exact qualified CandidateRevision
+
one exact credential-free RepositoryPublicationTargetRef
+
one exact expected repository predecessor
```

```text
Before `PublicationIntentRef` is committed, M7 prepares the exact immutable Git successor object locally from the authorized publication projection.

That preparation yields one exact `AuthorizedGitTransitionRef` containing:

exact repository identity
+
exact credential-free remote publication endpoint
+
exact fully qualified ref name
+
exact predecessor commit and tree
+
exact successor commit and tree
+
mechanical proof that predecessor is an ancestor of successor
+
relationship = fast-forward
```

The preparation itself does not mutate the remote publication target.

The committed PublicationIntent therefore binds:

exact publication target
+
exact authorized predecessor-to-successor transition
+
exact qualified CandidateRevision
+
exact GateAQualificationRef
```

The publication effect must be conditional on the exact target ref still having that expected predecessor. CAS success alone is insufficient unless the committed fast-forward transition proof remains valid.

A conflict does not grant permission to:

* rebase;
* merge;
* force-push;
* rewrite the qualified candidate;
* adjust files for convenience;
* include unrelated mutable worktree content.

Any material change creates a different candidate and requires the appropriate review/qualification again.

## 30. Publication reconciliation

Before dispatch, PublicationIntent is durable.

The runner must be able to distinguish:

```text
exact publication target
expected predecessor
intended successor
observed authority of that exact target ref
```

After uncertainty:

```text
observed exact target ref commit == transition.successor.commitSha
AND
observed exact target ref tree == transition.successor.treeSha
→ publication may be mechanically confirmed after target, ancestry,
  and material-identity verification

observed exact target ref commit == transition.predecessor.commitSha
AND
observed exact target ref tree == transition.predecessor.treeSha
→ the exact same conditional publication may be issued/reissued

observed exact target ref authority differs from both exact identities
→ do not improvise
→ OPERATOR-ACTION-REQUIRED unless an accepted repository contract proves another exact result
```

Every publication attempt must be a compare-and-swap-style mutation of the exact target ref against the exact predecessor commit identity and must preserve the committed fast-forward ancestry relation.

Therefore a stale concurrent attempt using that same predecessor cannot overwrite a successor after another attempt has already won the transition: its predecessor condition must fail.

Publication recovery must never infer exact completion from tree equality alone.

A read followed by an unconditional write is insufficient when it leaves an inspection-to-mutation race.

The Repository Dependency Contract/NIB-M must use a conditional mutation boundary capable of enforcing the expected predecessor.

## 31. Publication confirmation and post-publication validation

`PublicationConfirmed` binds:

```text
exact PublicationIntent
exact publication target
exact authorized fast-forward predecessor-to-successor transition
exact predecessor and successor authority, including commit SHA and tree SHA
exact qualified CandidateRevision
mechanical target, ancestry, and material-identity evidence
```

After publication confirmation, the runner executes the required post-publication repository validation on the published representation.

`GATE-A-READY` is not emitted until both hold:

```text
exact candidate mechanically qualified
AND
exact qualified representation published and confirmed
```

A successor repository authority may be used as authority by a future run.

It may not flow backward to justify the candidate or qualification that created it.

## 32. Non-circular judging authority

The runner must not allow a candidate to change the rules by which that same candidate is accepted.

Within one exact ReviewCampaign:

```text
S is exact
P is exact
judging authority is fixed
```

A candidate repair may change the reviewed subject and therefore create a new `S` and a new ReviewCampaign.

It may not alter `P`, the acceptance rules, or another judging authority and then use the modified rule to accept itself.

A change to judging authority requires an external authority transition and evaluation under the resulting new exact authority.

## 33. Configuration boundary

Runner configuration is divided into:

```text
protocol-owned configuration
runner operational configuration
secrets
```

Protocol-owned values include anything whose variation changes hostile-review semantics or qualification, including reviewer profiles, prompts, protocol schemas, retry/admissibility policy, and current protocol identity.

Those values come only from exact P.

They are not CLI overrides.

Runner operational configuration may select only implementation concerns that do not redefine hostile-review semantics.

NIB-M must enumerate the exact operational configuration surface.

No operational option may override:

* `S`;
* `P`;
* reviewer qualification;
* model identity rules;
* canonical prompt;
* canonical packet;
* required attack objectives;
* minimum independent reviewer policy;
* protocol retry admissibility;
* finding normalization;
* challenge semantics;
* Gate A qualification rules.

## 34. Secret boundary

Secret values never enter:

* the repository;
* NIBs;
* protocol artifacts;
* campaign packets;
* execution receipts;
* raw hostile-review outputs;
* durable adjudication evidence;
* GitHub Issues/comments;
* runner logs intended as durable evidence;
* RunnerResult.

M4 receives provider credentials through an injected runtime credential boundary.

The exact credential names/source integration belong to the M4 NIB-M and `llm-runtime` Dependency Contract.

The campaign runner has no direct runtime dependency on Doppler.

Development tooling may arrange the environment using the workspace credential mechanism, but Doppler is not campaign semantics.

Missing required credentials are an operational blocker, never `DECISION-REQUIRED`.

## 35. Normal external result contract

Normal runner termination returns exactly one of:

```text
GATE-A-READY
DECISION-REQUIRED
OPERATOR-ACTION-REQUIRED
```

All three are normal contract outcomes.

They are not generic exception classes.

The serialized result schema is:

```ts
interface RunnerResultCommon {
  readonly schema: "gate-a-runner-result.v1";
  readonly runId: GateARunId;
  readonly candidate: CandidateRevisionRef | null;
  readonly semanticSubject: SemanticSubjectRef | null;
  readonly protocolBundle: ProtocolBundleRef | null;
  readonly blockers: readonly CampaignBlocker[];
  readonly provenanceRoot: ArtifactRef;
}

interface GateAReadyResult extends RunnerResultCommon {
  readonly outcome: "GATE-A-READY";
  readonly candidate: CandidateRevisionRef;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly blockers: readonly [];
  readonly gateQualification: GateAQualificationRef;
  readonly publication: PublicationConfirmationRef;
}

interface DecisionRequiredResult extends RunnerResultCommon {
  readonly outcome: "DECISION-REQUIRED";
  readonly blockers: readonly SemanticBlocker[];
  readonly decisionRequests: readonly ArtifactRef[];
}

interface OperatorActionRequiredResult extends RunnerResultCommon {
  readonly outcome: "OPERATOR-ACTION-REQUIRED";
  readonly blockers: readonly CampaignBlocker[];
  readonly decisionRequests: readonly ArtifactRef[];
  readonly operatorRequests: readonly ArtifactRef[];
}

type RunnerResult =
  | GateAReadyResult
  | DecisionRequiredResult
  | OperatorActionRequiredResult;
```

Projection precedence is exact:

```text
if Gate A qualification + publication confirmation exist
and no blocker remains
→ GATE-A-READY

else if any operational blocker exists
→ OPERATOR-ACTION-REQUIRED
  and preserve every coexisting semantic blocker in `blockers`

else if one or more semantic blockers exist
→ DECISION-REQUIRED

else
→ this is not a normal campaign outcome;
  treat it as runner implementation/integrity failure
```

## 36. CLI boundary

The executable command is:

```text
run-gate-a-review
```

The normal command forms are exactly:

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

`start` creates a new `GateARun`.

`resume` never creates a replacement run silently.

A `DECISION-REQUIRED` run is not semantically resumed after product authority changes. A later `start` begins a new run from the new repository authority.

An `OPERATOR-ACTION-REQUIRED` run may be resumed after an explicit operator resolution.

The CLI is non-interactive.

It must not prompt the user for product decisions, reviewer profiles, model substitutions, repair choices, merge choices, or hidden retry choices.

For normal contract termination:

```text
stdout = exactly one serialized RunnerResult
exit status = 0
```

Diagnostics go to stderr.

An uncaught implementation/process failure that prevents production of a valid normal RunnerResult exits non-zero and must not fabricate one of the three contract outcomes.

## 37. Orchestration pseudocode

The top-level orchestration contract is:

```text
run(command):
    session = begin_runner_session(command)

    if command.mode == "start":
        bootstrap = campaign_state.create_run_and_acquire_initial_ownership(
            command.repositoryPath,
            session.sessionId,
            contracts.preflightObligationDefinition
        )

        if bootstrap is rejected:
            fail invocation as implementation/integrity failure

        run = bootstrap.run
        ownership = bootstrap.authority
        snapshot = bootstrap.snapshot

        preflight = campaign_authority.preflight(run, command.repositoryPath)

        if preflight is blocked:
            require every blocker references bootstrap.preflightObligation
            commit exact blockers through M2 using ownership + snapshot.stateRevision
            return project_runner_result()

        commit exact baseline authority + publication target + satisfied root
            preflight obligation through M2

        candidate = repository_control.seal_initial_candidate(
            run,
            preflight.baselineAuthority
        )

        commit exact candidate through M2

    else:
        run = load_exact_run(command.runId)

        ownership = campaign_state.acquire_write_ownership(
            run,
            session.sessionId,
            exact loaded StateRevision
        )

        snapshot = ownership.snapshot

        if command.operatorResolutionPath exists:
            resolution = recovery_operator.validate_and_admit_resolution(
                exact blocker from snapshot,
                command.operatorResolutionPath
            )
            commit resolution through M2
            snapshot = committed snapshot

        recovery_plan = recovery_operator.reconcile_prior_sessions({
            runId: run.runId,
            stateRevision: snapshot.stateRevision,
            newOwnershipGeneration: ownership.authority.generation,
            unresolvedExecutions: snapshot.unresolvedExecutions
        })

        require exactly one recovery resolution per unresolved execution
        commit recovery_plan through M2

        if recovery_plan leaves blocking operational uncertainty:
            return project_runner_result()

    loop:
        snapshot = load_authoritative_snapshot(run)

        if snapshot is effectively terminal:
            return project_runner_result(snapshot)

        currentness = revalidate_current_authority_and_currentness(snapshot)

        if currentness.kind == "campaign-required":
            prerequisites = campaign_authority.verify_reviewer_prerequisites({
                candidate: currentness.candidate,
                semanticSubject: currentness.semanticSubject,
                protocolBundle: currentness.currentProtocolBundle
            })

            if prerequisites.kind == "blocked":
                commit exact operational blockers through M2
                return OPERATOR-ACTION-REQUIRED projection

            campaign = construct exactly one full ReviewCampaign(
                exact current candidate provenance,
                exact current repository authority,
                currentness.semanticSubject,
                currentness.currentProtocolBundle,
                prerequisites.qualifyingReviewerProfileIds,
                prerequisites.evidence
            )

            derive:
                all protocol-required current-P campaign obligations and WorkItems
                all required current-P re-adjudication obligations and WorkItems
                for stale-protocol findings over the same S

            commit campaign + complete derived ledger products through M2

            continue

        if currentness.kind == "blocked":
            commit exact operational blockers through M2
            return project_runner_result()

        evaluation_context = currentness.context

        require evaluation_context.currentCampaigns
            == complete repository-selected campaign set for exact (S, P)
            without candidate/repository provenance filtering

        if operational blocker exists:
            return OPERATOR-ACTION-REQUIRED projection

        if semantic blocker exists and no operational blocker exists:
            return DECISION-REQUIRED projection

        work = derive_enabled_work(snapshot)

        if qualified exact repair is enabled:
            successor = repository_control.apply_exact_patch_and_seal(
                exact source candidate,
                exact approved patch,
                exact RepairIntent
            )

            successor_subject = campaign_authority.derive_subject(successor)

            commit successor through M2

            if successor_subject != source subject:
                prior campaigns become non-current for the successor subject by derivation
            else:
                retain the complete current campaign set for unchanged exact (S, P)
                do not create a campaign because CandidateRevision changed

            continue

        if one or more ordinary WorkItems are enabled:
            select only already-authorized WorkItems

            immediately before each external dispatch:
                revalidate:
                    WorkItem still enabled
                    authorization still effective
                    expected StateRevision still current
                    ownership generation still current

            dispatch through the owning module

            durably capture one of:
                captured result
                known technical failure with no completed response
                execution uncertainty with its complete
                UnresolvedExecutionRecoveryRef

            if the capture is execution uncertainty:
                commit the exact descriptor through M2
                classification = recovery_operator.classify_unresolved_execution(
                    exact descriptor
                )
                commit classification through M2
                if classification.classification == PROVEN-COMPLETED:
                    treat classification.recoveredResult as a newly captured result
                else if classification.classification == PROVEN-NOT-EXECUTED:
                    require the exact protocol retry rule before any replacement
                        Execution is derived
                else:
                    commit exact operational blocker through M2
                    return OPERATOR-ACTION-REQUIRED projection

            delta = assurance_ledger.derive_complete_delta(
                evaluation_context,
                current authoritative snapshot,
                newly captured results,
                newly known technical failures,
                newly admitted artifacts
            )

            commit every explicit delta product through M2

            continue

        if exact CandidateReviewReadiness exists:
            require readiness.currentReviewCampaignIds
                == every repository-selected current campaign over exact (S, P)
            require readiness.contributingReviewCampaignIds
                == complete current + stale-protocol contribution basis

            validation = mechanical_validation.qualify_exact_candidate(
                exact candidate,
                exact CandidateReviewReadiness
            )

            commit validation evidence through M2

            if validation does not establish Gate A readiness:
                derive complete resulting AssuranceLedgerDelta
                continue

            qualification = admit GateAQualification(
                validation,
                exact complete current campaign IDs,
                exact complete contributing campaign IDs
            )

            commit qualification through M2

            continue

        if exact qualified candidate exists and publication is enabled:
            preparation = repository_control.prepare_publication(
                exact qualification,
                exact candidate,
                exact snapshot.run.publicationTarget,
                exact expected repository predecessor
            )

            if preparation is blocked:
                commit exact operational blocker through M2
                continue

            require preparation.transition.relationship == "fast-forward"
            require valid mechanical evidence that:
                transition.predecessor is ancestor of transition.successor
                transition.target is exact repository + endpoint + ref

            intent = construct PublicationIntent(
                exact qualification,
                exact candidate,
                preparation.transition,
                preparation.materialIdentityEvidence
            )

            commit intent through M2

            immediately before publication dispatch:
                revalidate:
                    qualification still effective
                    no new blocker exists
                    exact target ref still equals transition.predecessor
                    transition.successor still equals prepared immutable repository object
                    fast-forward ancestry proof still valid
                    ownership generation still current

            result = repository_control.publish_conditionally(intent)

            reconcile result against the exact target ref if needed

            if publication cannot be established safely:
                commit exact operational blocker through M2
                continue

            require confirmation.transition == intent.transition
            require observed target successor authority
                == intent.transition.successor
                by both commit SHA and tree SHA

            commit PublicationConfirmed through M2

            post_validation = mechanical_validation.post_publication(
                exact published target representation
            )

            if post_validation fails:
                commit operational/integrity blocker through M2
                continue

            commit terminal Gate A ready fact through M2

            return GATE-A-READY projection

        if no legitimate automatic continuation exists:
            derive exact blocking obligation

            if blocker is semantic:
                materialize Decision Request
            else:
                materialize Operator Action Request

            commit blocker through M2

            continue
```

The orchestrator never creates semantic authority.

It only coordinates work already permitted by the current exact authority and admitted durable facts.

## 38. Dependency inventory

### Runtime dependencies/boundaries

```text
Node.js >= 20
  required process/runtime platform

llm-runtime
  TypeScript ESM in-process library
  consumed only by M4
  exact contract deferred to Issue #31 Dependency Contract

Python 3 + repository-pinned Python tooling
  external mechanical validation authority
  invoked only through M6

Git command-line/repository implementation
  repository inspection/worktree/publication mechanism
  consumed only through M7

Node standard library
  filesystem/process/crypto/runtime primitives
```

### Construction-selected TypeScript support dependency

The implementation selects:

```text
zod
```

M0 MUST use `zod` for runtime validation of runner-owned serialized internal and CLI structures.

Zod does not validate or replace hostile-review protocol authority where existing content-addressed JSON schemas and Python mechanical validators own that responsibility.

The exact pinned package version belongs to the M0 NIB-M/package construction step. The dependency choice itself is fixed here and is not left to GREEN implementation discretion.

### Dependencies explicitly NOT selected

```text
TURNLOCK production runtime
Temporal
Inngest
Trigger.dev
external database service
message broker
Doppler runtime SDK
custom Python reimplementation
custom Git library as semantic authority
```

The M2 NIB-M must select the persistence mechanism.

That choice is intentionally not made by NIB-S and must satisfy the persistence/ownership invariants in this document before implementation.

## 39. Global invariants

The implementation must preserve all of the following.

### Identity and authority

```text
GI-01  RunnerSession != GateARun != ReviewCampaign.
GI-02  ReviewCampaign provenance is permanently bound to its exact production
       candidate/run identity when runner-owned, exact repository authority,
       exact S, and exact P; currentness is independently derived from (S, P).
GI-03  CandidateRevision identity is immutable after seal.
GI-04  A repair that changes S requires a full new ReviewCampaign; a
       CandidateRevision-only change with unchanged (S, P) does not.
GI-05  A protocol change never rewrites historical campaign evidence.
GI-06  Product-semantic authority is never invented by the runner.
GI-07  Judging authority cannot self-amend to accept the candidate it judges.
GI-08  Successor repository authority cannot retroactively justify its own creation.
```

### Cognitive authority

```text
GI-09  Cognitive output is not authority merely because execution succeeded.
GI-10  Reviewer/model majority never overrides a surviving material blocker.
GI-11  No unregistered reviewer profile/model is auto-promoted.
GI-12  Existing protocol validation and challenge semantics are not reimplemented
       as free TypeScript judgment.
```

### Work and recovery

```text
GI-13  Obligation != WorkItem != Execution.
GI-14  Retry creates a new Execution.
GI-15  UNKNOWN != FAILURE.
GI-16  POSSIBLY-EXECUTED != NOT-EXECUTED.
GI-17  Cancellation != rollback.
GI-18  Work queue is not authoritative state.
GI-19  Scheduler selects enabled work; it never invents work.
GI-20  One GateARun has at most one authoritative writer at a time.
GI-21  Stale writers cannot commit authoritative transitions.
GI-22  Ownership transfer does not erase external uncertainty.
GI-23  Recovery re-derives safe work from durable authority and complete
       unresolved-execution recovery descriptors.
```

### Persistence and provenance

```text
GI-24  Mutable workspace != authoritative history.
GI-25  Durable material != authority merely because it was persisted.
GI-26  Authority-bearing references resolve to immutable/verifiable identities.
GI-27  Retained authoritative facts retain reconstructible provenance closure.
GI-28  Result capture != result admission.
```

### Repair and candidate handling

```text
GI-29  CandidateDraft != CandidateRevision.
GI-30  Review evidence never targets a mutable draft.
GI-31  Repair executor applies only the exact approved patch.
GI-32  Repair cannot silently expand its authority.
GI-33  A material subject-changing repair never patches old campaign evidence
       into currentness; it creates a new current campaign.
```

### Mechanical qualification and publication

```text
GI-34  TypeScript runner logic does not replace Python Gate A authority.
GI-35  Validation for Cn never qualifies Cn+1.
GI-36  Qualification != publication.
GI-37  Publication conditionally mutates one exact repository/endpoint/ref
       target against the exact expected repository predecessor.
GI-38  Publication cannot silently merge, rebase, force-push, or rewrite a
       qualified candidate.
GI-39  Published representation must be mechanically identical to the authorized
       publication projection of the qualified candidate.
GI-40  GATE-A-READY requires both exact mechanical qualification and exact
       confirmed publication.
```

### Outcomes

```text
GI-41  Technical/operational uncertainty is never disguised as DECISION-REQUIRED.
GI-42  Product-semantic underdetermination is never invented away to avoid
       DECISION-REQUIRED.
GI-43  Semantic and operational blockers may coexist.
GI-44  If any operational blocker exists, top-level projection is
       OPERATOR-ACTION-REQUIRED and all blockers remain visible.
GI-45  A normal result is derived from authoritative state, not from an exception.

GI-46  If current P changes while S remains unchanged, stale-P campaigns become
       historical for currentness and one full new ReviewCampaign under current
       P is required after reviewer prerequisites are established.

GI-47  GateAQualification records every current ReviewCampaign over exact (S, P)
       and every ReviewCampaign whose evidence or stale-protocol re-adjudication
       contributes to its mechanical qualification basis, without candidate-
       provenance filtering.

GI-48  PublicationIntent binds the exact credential-free publication target and
       exact authorized fast-forward transition, including predecessor and
       successor commit/tree identities, before remote mutation is dispatched.

GI-49  The first authoritative write atomically creates GateARun and initial
       WriteAuthorityRef in M2. Every later authoritative cross-module write
       flows through M2 with exact WriteAuthorityRef and expected StateRevision;
       no other module has an implicit state-write path.

GI-50  A known technical failure with no completed response is neither a
       captured raw result nor execution uncertainty.

GI-51  M5 exposes every established finding, evidence item, adjudication,
       re-adjudication, obligation disposition, qualified RepairIntent,
       qualified Decision Request, and candidate-review-readiness result to M2.

GI-52  PublicationIntent proves the predecessor is an ancestor of the intended
       successor; CAS alone never authorizes an unrelated successor.

GI-53  A ReviewCampaign is created only after current protocol reviewer/profile
       prerequisites are established; a blocked prerequisite creates no
       executable campaign.

GI-54  In-session execution uncertainty is classified through M8 and the
       owning executor's recovery port before any continuation; an
       unestablished outcome returns OPERATOR-ACTION-REQUIRED rather than
       resuming or blind-retrying the WorkItem.
```

## 40. Cross-cutting policies

### CP-1 — Fail closed on missing authority

If exact `S`, exact `P`, exact candidate identity, required protocol inputs, or required provenance cannot be established, automatic campaign progression stops.

### CP-2 — No semantic fallback

Provider limitations, unavailable models, missing credentials, Git conflicts, storage problems, or runtime limitations never create alternative product semantics.

### CP-3 — Exact-input binding

Every external cognitive/mechanical execution is bound to exact immutable campaign inputs before dispatch.

### CP-4 — Revalidate at side-effect boundary

Historical authorization is insufficient.

Immediately before every external side effect, current effective permission and current write authority are revalidated. Before publication, the exact target ref, expected predecessor, intended successor, and authorized fast-forward ancestry relation are all revalidated.

### CP-5 — No silent inheritance across subject changes

Evidence, findings, qualification, or review closure from `S(n)` never silently qualify `S(n+1)`.

The accepted protocol determines any explicitly permitted stale-protocol re-adjudication only when `S` remains the same.

### CP-6 — Existing authority owns currentness

Currentness for Gate A is determined from the accepted repository/protocol machinery.

The runner does not maintain a second independent currentness truth.

### CP-7 — Secrets are capability input, not evidence

A secret may enable execution but never becomes campaign evidence or semantic authority.

### CP-8 — No hidden interaction

The CLI does not ask conversational questions.

Every human/operator boundary is represented by an explicit durable request/outcome artifact.

### CP-9 — Protocol-currentness creates a new exact campaign

If current `P` differs from the protocol identity of campaigns over the same exact `S`, every stale-`P` campaign is historical for currentness.

After current-`P` reviewer/profile prerequisites are established, one full new ReviewCampaign under current `P` is required, together with every stale-protocol finding re-adjudication required by accepted authority.

No stale protocol campaign is mutated into currentness. Candidate or repository provenance does not determine currentness.

### CP-10 — Prerequisites precede campaign creation

Before any required ReviewCampaign is committed, M3 must establish the exact protocol-owned reviewer/profile prerequisites.

If it cannot, M1 commits the resulting operational blockers and returns `OPERATOR-ACTION-REQUIRED`. It must not create an empty, duplicate, or nominally executable ReviewCampaign.

## 41. NIB-M decomposition required by this System Brief

Issue #30 must produce active NIB-M coverage for exactly these implementation modules:

```text
M0 contracts
M1 orchestrator
M2 campaign-state
M3 campaign-authority
M4 cognitive-execution
M5 assurance-ledger
M6 mechanical-validation
M7 repository-control
M8 recovery-operator
```

A module may require more than one NIB-M only if the architect explicitly decomposes that module under the workspace NIB convention.

The coding agent does not choose such decomposition.

The NIB-M set must not change the system module boundaries above.

## 42. Dependency Contracts required downstream

The accepted module design requires, at minimum:

```text
llm-runtime Dependency Contract
```

before M4 implementation.

Repository/Git and persistence behavior must receive separate Dependency Contracts only if the NIB-M design selects a non-trivial external dependency whose behavior is not completely owned by Node/Git contracts already fixed by the implementation environment.

The architect decides that during NIB-M.

The coding agent does not.

## 43. NIB-S exclusions

This System Brief does not define:

* module-internal algorithms;
* persistence-engine choice;
* persistence file/database layout;
* exact ID generation algorithm;
* exact scheduler ordering;
* exact retry counts/backoff;
* exact provider timeout values;
* exact prompt text;
* exact reviewer profiles;
* exact operator-resolution kinds;
* exact Git command sequences;
* exact Python subprocess command sequences;
* exact NIB-T fixtures;
* production code.

Those details must be closed by NIB-M, Dependency Contracts, and NIB-T before construction.

## 44. Validation and completion contract

This NIB-S is complete only if downstream work can determine without redesigning the system:

```text
where the runner lives
which ecosystem it uses
which modules exist
what each module owns
which identities cross module boundaries
what is durable versus authoritative versus mutable
how campaign provenance remains exact while campaign currentness depends only on (S, P)
how complete plural current/contributing campaign sets qualify one candidate
what happens after subject-changing and candidate-only repairs
how M2 atomically bootstraps the run and initial writer
who may write state
what exact recovery descriptors and ports exist after crash/ownership transfer
how WorkItems and Executions differ
where llm-runtime is allowed
where Python authority remains authoritative
how repair may proceed
when a Decision Request is legitimate
when Operator Action is required
what mechanically qualifies a candidate
which explicit M5 ledger products cross the module boundary
how M4 distinguishes no-response technical failure from uncertainty
what exact publication target and fast-forward Git transition may be mutated
what the CLI returns
why GATE-A-READY is justified
```

Further design therefore proceeds by module decomposition, external dependency contract closure, and test-contract construction.

It must not reopen the system semantics fixed here.
