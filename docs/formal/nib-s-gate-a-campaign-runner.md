---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-system"
workspace: "turnlock-rust"
date: "2026-09-20"
step_id: 1
id: NIB-S-GATE-A-CAMPAIGN-RUNNER
version: "6.0.8"
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
- accepted ADR-041 through ADR-049;
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

Version `5.0.0` is a breaking construction-contract revision of version `4.0.0`.
It adds the required typed M6-to-M5 cognitive-attempt validation boundary and
closes candidate-construction and execution-receipt lifecycle gaps before NIB-M.

Version `6.0.0` is a breaking construction-contract revision of version `5.0.0`.
It makes the durable dispatch-arm boundary self-contained across M2, M4, M7,
and M8: an armed externally effectful Execution carries its exact WorkItem,
dispatch intent/evidence, and recovery capability, and becomes immediately
unresolved after Arm until an authoritative terminal disposition exists.

Version `6.0.1` corrects the M1 multi-dispatch pseudocode so each external
capture and uncertainty-recovery branch remains bound to the exact
`ArmedExecutionDispatchRef` created for that loop iteration.

Version `6.0.2` corrects two implementation-contract continuation gaps without
changing TURNLOCK product semantics: blocked recovery plans retain the exact
pending reconciliation references required for M2 admission, and resume
orchestration can re-enter an incomplete bootstrap preflight after its exact
operational blockers have been resolved.

Version `6.0.3` closes recovery-blocker disposition plumbing without changing
TURNLOCK product semantics: M8 receives the complete outstanding operational
blocker set for the recovery snapshot, returns the exact blocker dispositions
selected for each unresolved Execution, and M1 transports those dispositions
and any pending-policy-exhaustion fact to M2 without choosing recovery
semantics.

Version `6.0.4` closes the non-execution-proof construction boundary without
changing TURNLOCK product semantics: executor-owned recovery observations must
carry an exact cross-module `NonExecutionProofRef` before M8 may derive
`PROVEN-NOT-EXECUTED`; M4 and M7 remain responsible for establishing
executor-domain non-execution facts, M8 validates only their common bindings
and owns recovery classification, and M2 remains the sole authority that admits
the resulting recovery fact.

Version `6.0.5` closes the pending/unknown construction boundary without
changing TURNLOCK product semantics: executor-owned pending observations must
carry an exact `ReconciliationContinuabilityRef` that positively establishes
safe re-observability, executor-owned unknown observations must carry an exact
`RecoveryIndeterminacyRef` that positively establishes executor-domain recovery
indeterminacy, and M8 automatic-policy exhaustion remains distinct from
executor-domain recovery exhaustion. The no-capability direct `UNRESOLVABLE`
path, M2 recovery-admission shapes, and all other M2 semantics remain unchanged.

Version `6.0.6` closes a construction-authority mismatch introduced by M8
reconciliation-trace materialization without changing TURNLOCK product
semantics. The later M8 NIB-M may append exactly one immutable
reconciliation-trace artifact to final M8 recovery evidence, including the
`ReconciliationPendingRef.evidence` retained after automatic-policy exhaustion.
The exact executor-owned or structurally derived base recovery evidence remains
first and unchanged; the M8 trace is algorithmic provenance only and never
establishes executor-domain execution truth. Recovery classifications, M2
recovery-admission shapes, and all other M2 semantics remain unchanged.

Version `6.0.7` closes the operator-replacement progression-supersession
construction boundary without changing TURNLOCK product semantics. An explicit
operator-authorized replacement may revoke one prior Execution's future
campaign-progression and automatic-recovery authority without asserting that
the prior external effect did or did not occur. M2 now retains that exact
progression-supersession relation durably, excludes a superseded prior Execution
from the active unresolved-recovery projection, and preserves the prior
Execution as immutable operational history. A post-supersession result may
remain auditable but may not silently re-enter authoritative progression.
Cognitive Executions whose protocol outcome was never mechanically established
remain GateARun operational history and are not fabricated into hostile-review
receipt attempts.

Version `6.0.8` closes the M8 operator-boundary construction contract without
changing TURNLOCK product semantics. M8 now owns deterministic operational-
blocker materialization, immutable Operator Action Request presentation,
recovery-blocker reuse and disposition, the closed operator-resolution
language, and operator-resolution ingestion. Non-recovery blockers use
occurrence identity bound to an immutable producer cause descriptor and base
StateRevision; M8 recovery blockers use stable causal identity independent of
reconciliation episode or StateRevision. Operator resolution never creates
domain truth: M8 validates the requested action and M2 independently validates
its current authoritative admissibility before any atomic blocker disposition
or Execution progression supersession.

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

* constructed only after one exact repository materialization is sealed and its
  exact semantic subject is derived;
* immutable after admission;
* bound to one exact repository materialization;
* bound to one parent candidate except `C0`;
* bound to exact construction/repair provenance;
* bound to that exact derived semantic subject identity.

A mutable worktree under repair is not a CandidateRevision.

The construction boundary is:

```text
complete admitted CandidateRevision Cn
        ↓
exact qualified RepairIntent
        ↓
mutable CandidateDraft
        ↓
exact approved patch applied
        ↓
seal candidate materialization Cn+1
        ↓
derive exact S(n+1)
        ↓
construct and admit complete CandidateRevision Cn+1
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

A runner-level retry or replacement of a WorkItem creates a new Execution.

Provider/transport retries internal to one external call do not create a new
runner Execution.

For a cognitive WorkItem, construction identity is bound to the accepted
hostile-review receipt hierarchy from ADR-049:

```text
cognitive WorkItem / logical hostile-review execution identity
→ zero or more runner Executions that reach the cognitive call boundary
→ one protocol attempt per such executed runner Execution
→ one llm-runtime call per protocol attempt
→ provider/transport attempts internal to that call
→ after the first qualified attempt, one complete hostile-review receipt
  aggregates every ordered protocol attempt
```

If a cognitive WorkItem reaches a qualified attempt and its complete
receipt is assembled:

```text
receipt.execution_id == WorkItemId
receipt.attempts[*].attempt_id == the corresponding runner ExecutionId
receipt.attempts[*].call_id == the exact llm-runtime call identity
```

The ordered receipt-attempt sequence follows the order of the corresponding
executed runner Executions.

A runner Execution proven `PROVEN-NOT-EXECUTED` remains historical but creates
no hostile-review receipt attempt because no cognitive call was established.

A failed or unresolved Execution is not rewritten into a later successful
attempt.

At most one non-terminal Execution exists for one WorkItem at one time in the
initial runner.

Independent parallelism is expressed as independent WorkItems.

A hostile challenge is a different cognitive WorkItem and therefore has a
different logical execution-receipt identity from the execution it challenges.

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
materialize/seal current candidate materialization
    ↓
derive exact semantic subject S
    ↓
construct/admit complete current CandidateRevision
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
for each completed cognitive response:
    M6 obtains exact checker-derived attempt classification
    M5 consumes that classification and either authorizes an admissible retry
    or, after the first qualified attempt, assembles the complete receipt
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
    seal successor candidate materialization
    ↓
    derive successor S
    ↓
    construct/admit complete successor CandidateRevision
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
* mapping from cognitive WorkItem/Execution identity to ADR-049 receipt execution/attempt identity, `llm-runtime` call identity, and provider-attempt evidence;
* dispatch/cancellation integration;
* raw result capture;
* exact attempt artifacts and runtime metadata needed to preserve pre-receipt
  history and later assemble execution receipts;
* secret injection into the LLM dependency boundary.

It does not adjudicate semantic correctness.

It does not retry outside the exact behavior authorized by the protocol and the `llm-runtime` Dependency Contract.

### M5 — `assurance-ledger`

Owns:

* protocol-derived obligations and WorkItems;
* consumption of exact M6 cognitive-attempt classifications;
* checker-derived cognitive protocol-attempt admissibility and exact retry-authorization products;
* assembly and sealing of one complete schema-v3 execution receipt only after
  the first qualified attempt;
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
* role-aware classification of exact captured cognitive attempts through the
  existing Python hostile-review validation authority;
* exact capture of validator inputs, outputs, exit status, candidate identity,
  and cognitive-attempt identity;
* admission-ready mechanical result artifacts;
* final mechanical Gate A qualification request for one exact sealed candidate;
* post-publication repository validation request.

It must invoke existing authorities rather than reimplementing them in TypeScript.

M6 validation invocations are read-only with respect to authoritative external systems.

They execute only against exact immutable validation inputs: an exact
cognitive execution request plus captured result, an exact sealed candidate, or
an exact `PublishedRepositoryViewRef`.

A validator subprocess interruption does not create an ambiguous external authoritative side effect.

The same exact validation request is therefore replay-safe.

M6 does not implement `ExecutionRecoveryPort`.

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
type ExecutionRetryAuthorizationId = string;
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

interface SealedCandidateMaterializationRef {
  readonly runId: GateARunId;
  readonly parentCandidateId: CandidateRevisionId | null;
  readonly producedByRepairIntentId: RepairIntentId | null;
  readonly materialization: ArtifactRef;
  readonly materializationEvidence: readonly ArtifactRef[];
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

interface PublishedRepositoryViewRef {
  readonly publicationConfirmationId: PublicationConfirmationId;
  readonly candidateId: CandidateRevisionId;
  readonly target: RepositoryPublicationTargetRef;
  readonly authority: RepositoryAuthorityRef;
  readonly repositoryPath: string;
  readonly materializationEvidence: readonly ArtifactRef[];
}
```

`RepositoryPublicationTargetRef` is the exact durable remote mutation target. `repositoryIdentity` identifies the repository independently of a local checkout, `remoteEndpoint` is the normalized credential-free publication endpoint, and `refName` is the fully qualified Git ref name. Credentials and credential-bearing URLs are invalid target identities.

A publication successor is an exact repository-authority identity, not merely a Git tree identity.

Before any remote publication mutation, M7 must prepare the exact immutable successor repository object locally, expose both its exact commit identity and exact tree identity through `RepositoryAuthorityRef`, and mechanically prove that the predecessor commit is an ancestor of the successor commit for the exact target. The initial runner authorizes only the `fast-forward` relationship.

A `PublicationIntentRef` that lacks the exact target, contains only a tree SHA, or lacks valid ancestry evidence is invalid. A compare-and-swap from `A` to an unrelated `C` is prohibited even when the target still equals `A`.

A repository path or local remote name is never sufficient as durable publication-target or immutable historical identity by itself.

`PublishedRepositoryViewRef` is an isolated local materialization of the exact confirmed publication successor.

Its `target` must equal the target in the referenced `PublicationConfirmationRef`.

Its `authority` must equal that confirmation's exact transition successor by both commit SHA and tree SHA.

Its `repositoryPath` is an operational location only. The path never substitutes for the bound target, authority, candidate, confirmation, or materialization evidence.

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

interface ExecutionProgressionSupersessionRef {
  readonly runId: GateARunId;
  readonly workItemId: WorkItemId;
  readonly priorExecutionId: ExecutionId;
  readonly successorExecutionId: ExecutionId;
  readonly blockerId: BlockerId;
  readonly operatorResolution: ArtifactRef;
}
```

`ExecutionProgressionSupersessionRef` records an explicit operator-authorized
progression cut between one prior Execution and the exactly one replacement
Execution created by the same authoritative transition.

It does not establish or imply that the prior Execution:

```text
did not execute
failed
completed
was cancelled before effect
was rolled back
has a known external outcome
```

It establishes only that the prior Execution no longer has authority to control
future campaign progression or automatic recovery.

The prior Execution remains immutable historical operational state.

For one supersession `S`:

```text
S.runId == exact GateARun
S.workItemId == prior.workItemId == successor.workItemId

prior.executionId == S.priorExecutionId
successor.executionId == S.successorExecutionId

successor.attemptOrdinal == prior.attemptOrdinal + 1

S.blockerId == exact disposed OperationalBlocker
S.operatorResolution == exact accepted operator-resolution ArtifactRef
```

One prior Execution may have at most one
`ExecutionProgressionSupersessionRef`.

Sequential replacement remains possible only as a linear Execution chain:

```text
E1 → E2 → E3
```

where each supersession names the then-current prior Execution and its exact
single successor.

```ts
type ExecutionRetryReason =
  | "technical-failure"
  | "protocol-invalid";

interface ExecutionRetryAuthorizationRef {
  readonly retryAuthorizationId: ExecutionRetryAuthorizationId;
  readonly runId: GateARunId;
  readonly workItemId: WorkItemId;
  readonly priorExecutionId: ExecutionId;
  readonly reason: ExecutionRetryReason;
  readonly protocolBundle: ProtocolBundleRef;
  readonly basisArtifacts: readonly ArtifactRef[];
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

type RecoveredExecutionOutcome =
  | {
      readonly kind: "captured";
      readonly value: CapturedExecutionResult;
    }
  | {
      readonly kind: "technical-failure";
      readonly value: TechnicalExecutionFailure;
    };

type DurableDispatchState =
  | "AUTHORIZED-NOT-DISPATCHED"
  | "POSSIBLY-DISPATCHED"
  | "OBSERVED-RESULT";

interface RecoveryCapabilityRef {
  readonly executor: WorkExecutor;
  readonly reconciliationOperation: ArtifactRef;
}

interface NonExecutionProofRef {
  readonly schema: "gate-a-non-execution-proof.v1";
  readonly execution: ExecutionRef;
  readonly workItemId: WorkItemId;
  readonly executor: "cognitive-execution" | "repository-control";
  readonly dispatchIntent: ArtifactRef;
  readonly recoveryCapability: RecoveryCapabilityRef;
  readonly proof: ArtifactRef;
  readonly basisArtifacts: readonly ArtifactRef[];
}

interface ReconciliationContinuabilityRef {
  readonly schema: "gate-a-reconciliation-continuability.v1";
  readonly execution: ExecutionRef;
  readonly workItemId: WorkItemId;
  readonly executor: "cognitive-execution" | "repository-control";
  readonly dispatchIntent: ArtifactRef;
  readonly recoveryCapability: RecoveryCapabilityRef;
  readonly continuability: ArtifactRef;
  readonly basisArtifacts: readonly ArtifactRef[];
}

interface RecoveryIndeterminacyRef {
  readonly schema: "gate-a-recovery-indeterminacy.v1";
  readonly execution: ExecutionRef;
  readonly workItemId: WorkItemId;
  readonly executor: "cognitive-execution" | "repository-control";
  readonly dispatchIntent: ArtifactRef;
  readonly recoveryCapability: RecoveryCapabilityRef;
  readonly indeterminacy: ArtifactRef;
  readonly basisArtifacts: readonly ArtifactRef[];
}

interface ArmedExecutionDispatchRef {
  readonly execution: ExecutionRef;
  readonly workItem: WorkItemRef;
  readonly dispatchIntent: ArtifactRef;
  readonly dispatchEvidence: readonly ArtifactRef[];
  readonly recoveryCapability: RecoveryCapabilityRef | null;
}

interface UnresolvedExecutionRecoveryRef {
  readonly execution: ExecutionRef;
  readonly workItem: WorkItemRef;
  readonly dispatchState: DurableDispatchState;
  readonly dispatchIntent: ArtifactRef;
  readonly dispatchEvidence: readonly ArtifactRef[];
  readonly terminalOutcome: RecoveredExecutionOutcome | null;
  readonly recoveryCapability: RecoveryCapabilityRef | null;
}

`ArmedExecutionDispatchRef` is the complete cross-module dispatch identity handed
to an externally effectful executor after M2 has durably admitted the exact Arm
transition.

The successful Arm commit is the authoritative transition from
`AUTHORIZED-NOT-DISPATCHED` to `POSSIBLY-DISPATCHED`.

From that commit until an authoritative terminal execution disposition exists,
the Execution is unresolved even if the process crashes before M4 or M7 returns
and even if the actual external call may not have begun.

For an armed Execution with no later uncertainty enrichment or terminal
material, M2 reconstructs its recovery descriptor as:

```text
execution          = ArmedExecutionDispatchRef.execution
workItem           = ArmedExecutionDispatchRef.workItem
dispatchState      = POSSIBLY-DISPATCHED
dispatchIntent     = ArmedExecutionDispatchRef.dispatchIntent
dispatchEvidence   = ArmedExecutionDispatchRef.dispatchEvidence
terminalOutcome    = null
recoveryCapability = ArmedExecutionDispatchRef.recoveryCapability
```

A later admitted executor uncertainty observation may only add exact
dispatch/recovery evidence and an exact already-known terminal outcome. It does
not create unresolvedness and may not change the bound Execution, WorkItem, or
dispatch intent.

type ExecutionRecoveryObservation =
  | {
      readonly kind: "not-executed";
      readonly nonExecutionProof: NonExecutionProofRef;
    }
  | {
      readonly kind: "terminal";
      readonly outcome: RecoveredExecutionOutcome;
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly kind: "pending";
      readonly continuability: ReconciliationContinuabilityRef;
    }
  | {
      readonly kind: "unknown";
      readonly indeterminacy: RecoveryIndeterminacyRef;
    };

interface ExecutionRecoveryPort {
  reconcile(
    unresolved: UnresolvedExecutionRecoveryRef
  ): Promise<ExecutionRecoveryObservation>;
}

`NonExecutionProofRef` is the common cross-module envelope for one positive
executor-owned proof that the exact external effect represented by one
Execution did not cross that executor's effect boundary.

It is not itself an authoritative recovery classification.

The common envelope binds the proof to:

```text
exact Execution
+
exact WorkItem identity
+
exact effect-owning executor
+
exact dispatch intent
+
exact recovery capability used to perform reconciliation
+
one exact executor-owned proof artifact
+
its exact supporting basis artifacts
```

`basisArtifacts` must be duplicate-free.

`proof` must not also occur in `basisArtifacts`.

Every referenced artifact must exist in the immutable artifact store and pass
ordinary artifact-integrity verification.

The executor-owned `proof` artifact's internal schema, domain interpretation,
and construction algorithm belong to the owning executor NIB-M and any required
Dependency Contract.

M0 validates the common cross-module envelope shape.

The owning executor must runtime-validate its own proof according to its exact
module/domain contract before returning `kind = "not-executed"`.

M8 must not reinterpret provider, transport, Git, repository, or other
executor-domain evidence in order to decide whether the external effect
occurred.

For an unresolved descriptor `U` and a returned non-execution proof `P`, M8
accepts the observation for classification only when all of these common
bindings hold:

```text
P.execution == U.execution

P.workItemId == U.workItem.workItemId

P.executor == U.workItem.executor

U.recoveryCapability != null

P.executor == U.recoveryCapability.executor

P.recoveryCapability == U.recoveryCapability

P.dispatchIntent == U.dispatchIntent
```

`P.executor` can therefore only be:

```text
cognitive-execution
repository-control
```

because only M4 and M7 own externally effectful recovery ports in this System
Brief.

M8 additionally requires successful immutable-artifact verification for:

```text
P.proof
every P.basisArtifacts entry
P.dispatchIntent
P.recoveryCapability.reconciliationOperation
```

A failed common binding, malformed proof envelope, missing artifact, corrupt
artifact, wrong executor, wrong Execution, wrong WorkItem, wrong dispatch
intent, or wrong recovery capability is an implementation/process/integrity
failure.

M8 must not downgrade such a contract violation to `pending`, `unknown`, or
`UNRESOLVABLE`.

If the executor cannot legitimately establish a valid non-execution proof, the
executor must not return `kind = "not-executed"`.

It must instead return the valid `pending`, `unknown`, or terminal observation
selected by its exact executor-domain contract.

For one accepted `not-executed` observation, M8 constructs the recovery
resolution evidence as the ordered duplicate-free sequence:

```text
[
    P.proof,
    ...P.basisArtifacts
]
```

where the first occurrence of an exact `ArtifactRef` is retained.

The later M8 NIB-M may append exactly one immutable reconciliation-trace
artifact to final M8 recovery evidence after the exact base evidence required
by this System Brief. This permission applies both to
`ExecutionRecoveryResolution.evidence` and to the
`ReconciliationPendingRef.evidence` retained after automatic-policy exhaustion.
The trace may not remove, replace, reorder, or reinterpret executor-owned or
structurally derived base evidence. The trace is M8 algorithmic provenance only;
it does not establish executor-domain execution truth.

The presence of a valid proof artifact in the artifact store does not by itself
make non-execution authoritative.

`PROVEN-NOT-EXECUTED` becomes authoritative only after M8 has produced the
bound recovery classification and M2 has admitted that recovery through the
ordinary authoritative mutation boundary.

`ReconciliationContinuabilityRef` and `RecoveryIndeterminacyRef` are common
cross-module envelopes for positive executor-owned recovery facts. Neither is
itself an authoritative recovery classification.

For an unresolved descriptor `U` and either returned envelope `R`, M8 accepts
the observation for classification only when all of these common bindings hold:

```text
R.execution == U.execution

R.workItemId == U.workItem.workItemId

R.executor == U.workItem.executor

U.recoveryCapability != null

R.executor == U.recoveryCapability.executor

R.recoveryCapability == U.recoveryCapability

R.dispatchIntent == U.dispatchIntent
```

M8 additionally requires successful immutable-artifact verification for:

```text
R.dispatchIntent
R.recoveryCapability.reconciliationOperation
every R.basisArtifacts entry
R.continuability when R is ReconciliationContinuabilityRef
R.indeterminacy when R is RecoveryIndeterminacyRef
```

For both envelope types, `basisArtifacts` must be duplicate-free. The primary
`continuability` or `indeterminacy` artifact must not also occur in
`basisArtifacts`.

M0 validates the common envelope shapes. The owning executor must
runtime-validate the executor-domain meaning of its envelope before returning
the observation. M8 validates only common bindings and artifact integrity; it
must not reinterpret executor-domain evidence.

A `ReconciliationContinuabilityRef` positively establishes that invoking its
exact `recoveryCapability.reconciliationOperation` again:

```text
is observational with respect to the original external effect
cannot create, repeat, or replay that original external effect
remains bound to the exact Execution, WorkItem, executor, and dispatch intent
```

It establishes safe re-observability only. It does not promise that another
observation will produce progress or a terminal outcome.

A `RecoveryIndeterminacyRef` positively establishes that the executor's
available domain recovery mechanism is exhausted for the exact operation: it
cannot establish a terminal outcome, a valid non-execution proof, or a valid
safe-re-observation continuability fact.

It does not prove that the original effect executed or did not execute.

A failed lookup, elapsed time, process crash, absent result, missing convenient
evidence, or M8's decision to stop automatically re-observing is insufficient
by itself to establish either envelope.

A malformed envelope, failed binding, missing or corrupt artifact, wrong
executor, wrong Execution, wrong WorkItem, wrong dispatch intent, or wrong
recovery capability is an implementation/process/integrity failure. M8 must not
downgrade it to `pending`, `unknown`, or `UNRESOLVABLE`.

For one accepted pending envelope `C`, M8 constructs the existing
`ReconciliationPendingRef` with this exact base evidence:

```text
unresolvedExecution = U
recoveryCapability  = C.recoveryCapability
evidence            = ordered duplicate-free [
    C.continuability,
    ...C.basisArtifacts
]
```

When this pending fact is the final retained pending fact after M8
automatic-policy exhaustion, the later M8 NIB-M may append exactly one
immutable reconciliation-trace artifact after that base evidence under the
general trace-provenance rule above. The append does not change the
`ReconciliationPendingRef` shape, does not alter the executor-owned
continuability fact, and does not convert pending into executor-domain
indeterminacy.

For one accepted unknown envelope `I`, M8 constructs the `UNRESOLVABLE`
resolution evidence as the ordered duplicate-free sequence:

```text
[
    I.indeterminacy,
    ...I.basisArtifacts
]
```

In both projections, the first occurrence of an exact `ArtifactRef` is retained.

Executor-domain recovery exhaustion and M8 automatic-policy exhaustion are
distinct. An accepted `RecoveryIndeterminacyRef` establishes the former and
produces `UNRESOLVABLE`. When M8 ends its finite automatic policy while the last
accepted observation remains pending, the executor has positively established
safe re-observability; M8 retains the exact `ReconciliationPendingRef`, creates
no `RecoveryIndeterminacyRef`, and produces no terminal recovery resolution.

type ProvenExecutionRecoveryResolution =
  | {
      readonly executionId: ExecutionId;
      readonly classification: "PROVEN-NOT-EXECUTED";
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly executionId: ExecutionId;
      readonly classification: "PROVEN-COMPLETED";
      readonly recoveredOutcome: RecoveredExecutionOutcome;
      readonly evidence: readonly ArtifactRef[];
    };

interface UnresolvableExecutionRecoveryResolution {
  readonly executionId: ExecutionId;
  readonly classification: "UNRESOLVABLE";
  readonly blocker: OperationalBlocker;
  readonly evidence: readonly ArtifactRef[];
}

type ExecutionRecoveryResolution =
  | ProvenExecutionRecoveryResolution
  | UnresolvableExecutionRecoveryResolution;

interface ReconciliationPendingRef {
  readonly unresolvedExecution: UnresolvedExecutionRecoveryRef;
  readonly recoveryCapability: RecoveryCapabilityRef;
  readonly evidence: readonly ArtifactRef[];
}

type ExecutionRecoveryStep =
  | {
      readonly kind: "terminal";
      readonly resolution: ExecutionRecoveryResolution;
    }
  | {
      readonly kind: "reconcilable";
      readonly pending: ReconciliationPendingRef;
    };
```

A captured result is durable material.

It is not automatically an authority-bearing semantic result.

`TechnicalExecutionFailure` means that no completed semantic response exists. It is distinct from execution uncertainty and distinct from a captured semantic response.

`PROVEN-COMPLETED` means that the exact Execution has a proven terminal outcome. It does not mean that a completed semantic response exists. Its `recoveredOutcome` preserves the distinction between a captured response and a known terminal technical failure.

`PROVEN-NOT-EXECUTED` means positive mechanically validated evidence establishes
that the exact external effect represented by that Execution did not cross the
effect boundary owned by its executor.

It does not mean merely:

```text
no successful result was observed
no completed result was observed
no receipt exists
a timeout elapsed
a cancellation was requested or acknowledged
the runner process crashed
an external lookup returned no convenient result
the currently observed external state happens to resemble the pre-dispatch state
```

Absence of evidence is never converted into proof of non-execution.

A dependency-specific negative lookup may support `PROVEN-NOT-EXECUTED` only
when the owning executor's accepted Dependency Contract establishes that the
lookup is complete for the exact operation and that the returned negative fact
positively proves that the exact effect boundary was never crossed.

An uncertain executor result carries the complete `UnresolvedExecutionRecoveryRef`. The owning executor reports durable dispatch identity/evidence, any already known terminal outcome, and its exact recovery capability. The owning executor does not assign a recovery classification.

A `not-executed` observation requires a non-null exact recovery capability
because its `NonExecutionProofRef` is bound to the capability used to establish
that proof.

When an executor can mechanically prepare a trustworthy recovery capability
before Arm, its later NIB-M should require that capability to be carried by the
Arm rather than deliberately discarding recoverability.

This System Brief does not make recovery capability universally mandatory:
`null` remains valid when the selected executor/dependency boundary cannot
provide a trustworthy capability.

For a possibly-dispatched Execution with no terminal outcome and no usable
recovery capability, M8 must follow the existing direct `UNRESOLVABLE` rule
without invoking an `ExecutionRecoveryPort`; it must not infer non-execution
from the absence of a capability.

The non-null `recoveryCapability` required inside
`ReconciliationContinuabilityRef` and `RecoveryIndeterminacyRef` does not alter
`RecoveryCapabilityRef | null` on `ArmedExecutionDispatchRef` or
`UnresolvedExecutionRecoveryRef`.

`RECONCILABLE` is represented only by `ExecutionRecoveryStep.kind = "reconcilable"`. It is an intermediate recovery state, not a terminal recovery resolution and not permission to resume campaign external dispatch.

While an execution is reconcilable, the recovery barrier remains closed.

M8 may automatically perform further reconciliation observations under a finite bounded algorithm specified in M8 NIB-M.

If that finite automatic reconciliation policy ends while the execution is still pending, M8 must materialize an exact `OperationalBlocker` and return `OPERATOR-ACTION-REQUIRED`.

A technical failure never satisfies the WorkItem.

For a cognitive WorkItem, M5 may establish an
`ExecutionRetryAuthorizationRef` only when the accepted protocol attempt rules
and the runner retry policy both authorize another runner Execution for the
same exact WorkItem.

For `reason = "technical-failure"`, the referenced prior Execution must have an
exact admitted `TechnicalExecutionFailure`.

For `reason = "protocol-invalid"`, the referenced prior Execution must have an
exact completed captured response and an exact
`CognitiveAttemptValidationResult` from M6 that classifies that response as
`protocol-invalid`. M5 may establish the retry authorization only when the same
M2 transition also admits the result's exact validation evidence or that
evidence is already admitted. This reason is permitted only for the
deterministically validated roles `initial-reviewer` and `challenge`.

A completed response for a role without a deterministic output validator is
terminal and may never produce a `protocol-invalid` retry authorization.

A `qualified` protocol attempt may never produce a retry authorization.

One retry authorization names one exact prior Execution and authorizes at most
one replacement runner Execution. It is consumed atomically when that
replacement Execution is authoritatively created and may never be reused.

M1 never invents retry permission.

M2 validates and consumes admitted retry authorization but never invents it.

Provider/transport retries internal to one `llm-runtime` call are governed by
the `llm-runtime` Dependency Contract and do not use
`ExecutionRetryAuthorizationRef`.

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
  readonly expectedStateRevision: StateRevision;
}

type AcquireWriteOwnershipResult =
  | {
      readonly kind: "acquired";
      readonly authority: WriteAuthorityRef;
      readonly snapshot: GateARunSnapshot;
    }
  | {
      readonly kind: "rejected";
      readonly reason: "STALE_STATE";
      readonly currentStateRevision: StateRevision;
    }
  | {
      readonly kind: "rejected";
      readonly reason: "ACTIVE_OWNER_CONFLICT";
    }
  | {
      readonly kind: "rejected";
      readonly reason: "INTEGRITY_FAILURE";
    };

interface LoadGateARunSnapshotRequest {
  readonly runId: GateARunId;
}

interface GateARunSnapshot {
  readonly run: GateARunRef;
  readonly stateRevision: StateRevision;
  readonly currentCandidate: CandidateRevisionRef | null;
  readonly reviewCampaigns: readonly ReviewCampaignRef[];
  readonly obligations: readonly ObligationRef[];
  readonly obligationDispositions: readonly ObligationDispositionRef[];
  readonly workItems: readonly WorkItemRef[];
  readonly executions: readonly ExecutionRef[];
  readonly executionProgressionSupersessions:
    readonly ExecutionProgressionSupersessionRef[];
  readonly executionRetryAuthorizations: readonly ExecutionRetryAuthorizationRef[];
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

`AcquireWriteOwnershipRequest.expectedStateRevision` is mandatory for every
resume acquisition. `null` has no meaning and is not accepted.

`STALE_STATE` means the exact revision supplied by the caller is not current.
It reports the current exact `StateRevision` and grants no ownership.

`ACTIVE_OWNER_CONFLICT` means another RunnerSession currently retains the
exclusive ownership primitive for that `GateARun`. It grants no ownership and
does not report a supposedly stable campaign revision because the active owner
may continue to advance it.

`INTEGRITY_FAILURE` means M2 cannot establish a trustworthy ownership/state
result. It grants no ownership and must not fabricate a `StateRevision`.

No rejected ownership acquisition creates a CampaignBlocker or mutates the
`GateARun`.

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

interface CandidateSubjectDerivationRequest {
  readonly sealedCandidate: SealedCandidateMaterializationRef;
}

interface CandidateSubjectDerivationResult {
  readonly semanticSubject: SemanticSubjectRef;
}

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

M3 derives `SemanticSubjectRef` only from the exact sealed candidate
materialization. M7 does not derive `S`.

A complete `CandidateRevisionRef` is constructed only after M7 has returned the
sealed materialization and M3 has returned the exact derived semantic subject.
M2 then validates and registers that complete candidate identity.

M3 selects current campaigns solely by exact `(S, P)` through existing repository authority. Candidate, run, and repository provenance never filter `currentCampaigns`. Invalid evidence yields `blocked`; M3 must not omit it and continue with a convenient subset.

A `ReviewContext` used for new execution must use the exact production candidate recorded by its runner-owned campaign provenance. Reusing a current campaign to qualify a later same-`(S, P)` candidate does not create new executions under rewritten provenance.

`campaign-required` is never emitted for CandidateRevision change alone when exact `(S, P)` is unchanged and at least one current campaign exists.

For every `campaign-required` result, M1 must obtain `ReviewerPrerequisiteResolution.kind = "established"` before committing a new ReviewCampaign. A blocked prerequisite creates no campaign and projects `OPERATOR-ACTION-REQUIRED` after the blockers are committed.

`established` is valid only when the exact protocol bundle registers a non-empty set of `frontier_eligible == true` reviewer profiles that satisfies every protocol-declared reviewer-qualification prerequisite for the required review class, and `qualifyingReviewerProfileIds` is the exact duplicate-free subser of those registered profile IDs. An empty or insufficient registered set MUST be `blocked` with exact operational blockers. M1 and M3 never establish a resolution from runner configuration, environment, or a model alias absent from the protocol bundle.

`PROTOCOL-CHANGED` requires one full new current-`P` campaign plus accepted stale-protocol re-adjudication. It is not permission to mutate any old ReviewCampaign.

### M4

```ts
interface CognitiveExecutionRequest {
  readonly dispatch: ArmedExecutionDispatchRef;
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

For `kind = "uncertain"`, `value.terminalOutcome` may be non-null only when a terminal outcome has already been durably captured but the exact authoritative execution disposition still requires recovery reconciliation.

M4 must execute only an `ArmedExecutionDispatchRef` produced after successful
M2 Arm admission. It must not reconstruct a WorkItem, dispatch intent,
dispatch evidence, or recovery identity from `ExecutionRef` alone.

For every M4 capture:

```text
captured.value.execution
or
technical-failure.value.execution
or
uncertain.value.execution
==
request.dispatch.execution
```

For `kind = "uncertain"`, M4 must preserve exactly:

```text
value.workItem       == request.dispatch.workItem
value.dispatchIntent == request.dispatch.dispatchIntent
```

Its returned `dispatchEvidence` must contain the exact arm-time dispatch
evidence and may append only exact evidence observed during this same external
execution.

Its returned `recoveryCapability` must equal the arm-time capability unless the
executor has obtained a strictly more specific capability for the same exact
dispatch. It may remain `null`.

M4 never removes or weakens durable arm-time dispatch evidence.

M4 never converts `TechnicalExecutionFailure` into `CapturedExecutionResult`.

M4 recovery observations use `RecoveredExecutionOutcome.kind = "technical-failure"` when reconciliation proves that the execution terminated as a known no-completed-response technical failure.

For cognitive WorkItems, one runner `Execution` represents one protocol attempt
for the logical execution receipt identified by the WorkItem.

M4 performs exactly the external call for that runner Execution and seals the
result/evidence. It does not decide that an inconvenient completed semantic
result should be retried.

For M4 recovery, the relevant non-execution effect boundary is the exact
cognitive-call boundary for the runner Execution.

M4 may return `ExecutionRecoveryObservation.kind = "not-executed"` only when its
runtime-validated executor-owned proof positively establishes that the exact
runner Execution never crossed that cognitive-call boundary.

A known terminal call with no completed semantic response is not
`not-executed`; it is represented as a terminal recovery observation whose
`RecoveredExecutionOutcome.kind = "technical-failure"`.

No response, no receipt, timeout, cancellation, process interruption, missing
provider material, or an otherwise negative lookup is sufficient by itself to
prove cognitive non-execution.

The exact M4 proof artifact schema, its mapping to the exact `llm-runtime` call
identity, and the external facts sufficient to prove that the cognitive-call
boundary was not crossed belong to the M4 NIB-M and the scoped `llm-runtime`
Dependency Contract.

M8 must not reimplement that M4/domain proof algorithm.

M4 may return `ExecutionRecoveryObservation.kind = "pending"` only with a
runtime-validated `ReconciliationContinuabilityRef` that positively establishes
that another invocation of the exact cognitive reconciliation operation is
observational and cannot submit, resubmit, or otherwise replay the original
cognitive request.

M4 may return `ExecutionRecoveryObservation.kind = "unknown"` only with a
runtime-validated `RecoveryIndeterminacyRef` that positively establishes that
the exact provider/transport recovery capability cannot determine a terminal
outcome and cannot establish safe continued observation.

A missing response, cancellation, elapsed time, process interruption,
provider/transport failure, missing provider material, or unavailable
convenient lookup is not independently sufficient for either cognitive
recovery fact.

M4 owns validation of the cognitive executor-domain meaning. M8 validates the
common envelope bindings and artifacts and owns recovery classification.

A completed captured response must be submitted by M1 to M6. M6 invokes the
existing Python hostile-review validation authority and returns the exact typed
classification as either `qualified` or, only for the deterministically
validated roles, `protocol-invalid`.

M5 consumes that exact M6 result and owns the cross-module retry-authorization
product derived from the accepted attempt classification. M4 and M5 never
reimplement or override the Python classification.

M4 may perform only dependency-internal provider/transport retries inside the
same `llm-runtime` call when the Dependency Contract authorizes them. Those
transport retries do not create runner Executions or hostile-review protocol
attempts.
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
  readonly newlyValidatedCognitiveAttempts:
    readonly CognitiveAttemptValidationResult[];
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
  readonly executionRetryAuthorizationsToEstablish: readonly ExecutionRetryAuthorizationRef[];
  readonly blockersToAdd: readonly CampaignBlocker[];
  readonly candidateReviewReadiness: CandidateReviewReadinessRef | null;
}
```

M5 must return every cross-module ledger product it establishes. It may not hide
a finding, evidence admission, adjudication, re-adjudication, obligation
satisfaction/supersession, qualified RepairIntent, qualified Decision Request,
execution-retry authorization, or candidate-review-readiness determination
behind only a new WorkItem or blocker.

M2 returns those admitted products in `GateARunSnapshot`; M5 receives the
complete prior ledger plus exact newly captured results, technical failures,
and exact M6 cognitive-attempt validation results. No module may reconstruct
the ledger by rescanning mutable workspaces.

M5 must return complete cross-module `ObligationRef` values, not bare newly invented IDs.

`ObligationRef.definition` points to the immutable runtime-validated obligation definition that M2 registers in authoritative history.

The internal serialized schemas and algorithms for these exact product categories belong to M5 NIB-M. NIB-M may refine their internal artifact payloads but may not remove, merge, or invent another cross-module category.

The cross-module rule is fixed: M5 returns one `AssuranceLedgerDelta`. It never commits state directly.

Before a cognitive WorkItem has a qualified attempt, M5 preserves its exact
runner Executions, captured results or technical failures, M4 runtime evidence,
sealed completed outputs, and M6 validation evidence as GateARun operational
history. That pre-receipt history is not a hostile-review execution receipt and
must not be written or admitted under `formal/reviews/executions/`.

When M6 returns the first `qualified` classification for the logical cognitive
execution, M5 mechanically assembles and seals one complete schema-v3 receipt.
The receipt includes every preserved receipt-admissible protocol attempt for
that WorkItem, in runner Execution attempt-ordinal order, together with its
applicable exact M4 and M6 evidence. A receipt-admissible attempt has an exact
mechanically established receipt outcome permitted by the accepted hostile-
review receipt contract. The qualified attempt is final. M5 returns the sealed
receipt through the existing `EvidenceRef` category; it does not create another
cross-module ledger-product category.

A runner Execution that reached an external cognitive effect boundary but was
later progression-superseded while its protocol outcome remained mechanically
unknown stays in durable GateARun operational history. It is not fabricated
into a schema-v3 receipt attempt and is not relabeled as `technical-failure`,
`protocol-invalid`, or `qualified`.

If finite runner retry policy ends before any qualified attempt exists, M5
returns an exact `OperationalBlocker`, the external projection is
`OPERATOR-ACTION-REQUIRED`, and no schema-v3 hostile-review receipt is admitted.
The complete operational attempt history remains durable in the GateARun. If a
later accepted continuation lawfully reaches a qualified attempt for that same
WorkItem, the eventual receipt includes the preserved earlier attempts.

A partial or no-qualified receipt is never review evidence. Validator evidence
for an individual attempt is likewise not a substitute for the complete
schema-v3 receipt.

### M6

```ts
interface CognitiveAttemptValidationRequest {
  readonly kind: "cognitive-attempt";
  readonly runId: GateARunId;
  readonly repositoryPath: string;
  readonly executionRequest: CognitiveExecutionRequest;
  readonly capturedResult: CapturedExecutionResult;
}

type CognitiveAttemptValidationResult =
  | {
      readonly requestKind: "cognitive-attempt";
      readonly executionRequest: CognitiveExecutionRequest;
      readonly capturedResult: CapturedExecutionResult;
      readonly classification: "qualified";
      readonly protocolErrors: readonly [];
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly requestKind: "cognitive-attempt";
      readonly executionRequest: CognitiveExecutionRequest & {
        readonly role: "initial-reviewer" | "challenge";
      };
      readonly capturedResult: CapturedExecutionResult;
      readonly classification: "protocol-invalid";
      readonly protocolErrors: readonly [string, ...string[]];
      readonly evidence: readonly ArtifactRef[];
    };

type MechanicalValidationRequest =
  | CognitiveAttemptValidationRequest
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
      readonly publishedView: PublishedRepositoryViewRef;
    };

type MechanicalValidationResult =
  | CognitiveAttemptValidationResult
  | {
      readonly requestKind: "repository-integrity";
      readonly candidateId: CandidateRevisionId;
      readonly passed: boolean;
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly requestKind: "gate-a-qualification";
      readonly candidateId: CandidateRevisionId;
      readonly passed: boolean;
      readonly currentReviewCampaignIds: readonly ReviewCampaignId[];
      readonly contributingReviewCampaignIds: readonly ReviewCampaignId[];
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly requestKind: "post-publication-integrity";
      readonly candidateId: CandidateRevisionId;
      readonly publicationConfirmationId: PublicationConfirmationId;
      readonly target: RepositoryPublicationTargetRef;
      readonly validatedAuthority: RepositoryAuthorityRef;
      readonly passed: boolean;
      readonly evidence: readonly ArtifactRef[];
    };
```

For `cognitive-attempt`, M6 must invoke a supported thin Python entry point
that delegates to the existing hostile-review checker authority. It must not
run the whole-repository checker against an intentionally incomplete receipt,
infer attempt classification from a process exit code, or reproduce the
validator in TypeScript.

The request and result bindings are exact:

- `runId` must equal `executionRequest.reviewContext.runId`;
- `capturedResult.execution` must equal `executionRequest.dispatch.execution`;
- `executionRequest.dispatch.workItem.workItemId` must equal `executionRequest.dispatch.execution.workItemId`;
- the result's `executionRequest` and `capturedResult` must equal the exact
  request values;
- role, reviewer profile, prompt, packet, campaign, protocol bundle, execution,
  raw output, and runtime evidence must remain those of the exact dispatch and
  capture.

For `initial-reviewer` and `challenge`, the Python authority derives
`qualified` or `protocol-invalid` from the exact sealed output and exact bound
protocol inputs. For the seven roles without deterministic output validators,
the first completed response is classified `qualified` by the accepted
role-policy admission rule; this classification does not assert semantic
correctness. `protocol-invalid` is impossible for those seven roles.

A technical failure has no completed response and therefore creates no
`CognitiveAttemptValidationRequest`.

Failure to obtain a trustworthy Python classification is an
implementation/integrity failure. It produces neither `protocol-invalid`, a
retry authorization, nor a hostile-review receipt.

For `gate-a-qualification`, `reviewReadiness` must name the same candidate as the request. The result campaign-ID lists must equal the complete ordered lists in `reviewReadiness` and obey `GateAQualificationRef` completeness rules.

For `repository-integrity`, no review-campaign list exists in the result.

For `post-publication-integrity`:

- `candidateId` must equal `publishedView.candidateId`;
- `publicationConfirmationId` must equal `publishedView.publicationConfirmationId`;
- `target` must equal `publishedView.target`;
- `validatedAuthority` must equal `publishedView.authority` by both commit SHA and tree SHA.

M6 must validate the exact repository bytes materialized by `PublishedRepositoryViewRef`. A mutable path alone can never establish post-publication identity.

### M7

```ts
interface CandidateConstructionRequest {
  readonly runId: GateARunId;
  readonly sourceCandidate: CandidateRevisionRef;
  readonly repairIntentId: RepairIntentId;
  readonly approvedPatch: ArtifactRef;
}

interface CandidateSealResult {
  readonly sealedCandidate: SealedCandidateMaterializationRef;
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

interface PublicationExecutionRequest {
  readonly dispatch: ArmedExecutionDispatchRef;
  readonly intent: PublicationIntentRef;
  readonly candidate: CandidateRevisionRef;
}

type PublicationExecutionCapture =
  | {
      readonly kind: "captured";
      readonly value: CapturedExecutionResult;
    }
  | {
      readonly kind: "uncertain";
      readonly value: UnresolvedExecutionRecoveryRef;
    };

interface PublicationObservationQualificationRequest {
  readonly intent: PublicationIntentRef;
  readonly candidate: CandidateRevisionRef;
  readonly executionResult: CapturedExecutionResult;
}

type PublicationObservationQualificationResult =
  | {
      readonly kind: "confirmed";
      readonly confirmation: PublicationConfirmationRef;
      readonly publishedView: PublishedRepositoryViewRef;
    }
  | {
      readonly kind: "blocked";
      readonly blocker: OperationalBlocker;
    };
```

Publication preparation is a local repository operation.

It constructs the exact immutable successor repository object without mutating the remote publication target.

The resulting exact target, successor commit SHA, successor tree SHA, and fast-forward ancestry proof are known before `PublicationIntentRef` is committed.

Only after that exact intent is durable may M7 attempt the conditional mutation of the exact target ref.

Publication itself executes as a normal campaign WorkItem/Execution owned by M7.

M7 may perform the remote publication mutation only from an
`ArmedExecutionDispatchRef` produced after successful M2 Arm admission.

The armed dispatch must identify the exact repository-control WorkItem and
Execution authorized for the exact `PublicationIntent`.

M7 must not reconstruct dispatch identity or recovery provenance from
`ExecutionRef`, `PublicationIntentRef`, a repository path, or remote state
alone.

`PublicationExecutionCapture.kind = "captured"` means M7 obtained one exact durable publication-attempt observation artifact. It does not by itself mean publication is confirmed.

`PublicationExecutionCapture.kind = "uncertain"` carries the complete
`UnresolvedExecutionRecoveryRef` for `request.dispatch`. Its `execution`,
`workItem`, and `dispatchIntent` must equal the exact armed-dispatch values.
Its dispatch evidence may only preserve the arm-time evidence and append exact
evidence observed during this same publication attempt.

M7 never returns `RECONCILABLE` or `UNRESOLVABLE`.

All publication execution uncertainty is committed and classified through M8.

M7 implements `ExecutionRecoveryPort` for publication executions. A terminal publication recovery observation must return `RecoveredExecutionOutcome.kind = "captured"` containing the exact recovered publication observation.

After either immediate or recovered capture, M1 calls the same `PublicationObservationQualificationRequest`.

Only `PublicationObservationQualificationResult.kind = "confirmed"` may create `PublicationConfirmationRef`.

That confirmation result also returns the exact `PublishedRepositoryViewRef` consumed by post-publication M6 validation.

M7 may return `blocked` when the captured publication observation proves a publication conflict/divergence or otherwise cannot satisfy the committed `PublicationIntent`. That is a domain result from known evidence, not an uncertainty classification.

### M8

```ts
interface RecoveryRequest {
  readonly runId: GateARunId;
  readonly stateRevision: StateRevision;
  readonly newOwnershipGeneration: OwnershipGeneration;
  readonly unresolvedExecutions: readonly UnresolvedExecutionRecoveryRef[];
  readonly outstandingOperationalBlockers: readonly OperationalBlocker[];
}

interface RecoveryBlockerDisposition {
  readonly executionId: ExecutionId;
  readonly blockerIdsToDispose: readonly BlockerId[];
}

type RecoveryPlan =
  | {
      readonly kind: "cleared";
      readonly expectedStateRevision: StateRevision;
      readonly resolutions: readonly ExecutionRecoveryResolution[];
      readonly blockerDispositions: readonly RecoveryBlockerDisposition[];
    }
  | {
      readonly kind: "blocked";
      readonly expectedStateRevision: StateRevision;
      readonly resolutions: readonly ExecutionRecoveryResolution[];
      readonly pending: readonly ReconciliationPendingRef[];
      readonly blockers: readonly OperationalBlocker[];
      readonly blockerDispositions: readonly RecoveryBlockerDisposition[];
    };

interface ClassifyUnresolvedExecutionRequest {
  readonly runId: GateARunId;
  readonly unresolvedExecution: UnresolvedExecutionRecoveryRef;
  readonly outstandingOperationalBlockers: readonly OperationalBlocker[];
}

type ClassifyUnresolvedExecutionResult =
  | {
      readonly kind: "resolved";
      readonly resolution: ProvenExecutionRecoveryResolution;
      readonly blockerIdsToDispose: readonly BlockerId[];
    }
  | {
      readonly kind: "blocked";
      readonly blocker: OperationalBlocker;
      readonly resolution: UnresolvableExecutionRecoveryResolution | null;
      readonly lastPending: ReconciliationPendingRef | null;
      readonly blockerIdsToDispose: readonly BlockerId[];
    };

type NonRecoveryOperationalBlockerProducerV1 =
  | "campaign-authority"
  | "assurance-ledger"
  | "mechanical-validation"
  | "repository-control";

type RecoveryOperationalBlockerCauseV1 =
  | "pending-policy-exhausted"
  | "no-recovery-capability"
  | "executor-domain-indeterminacy";

type OperatorMechanicalContinuationV1 =
  | {
      readonly kind: "resume-reconciliation";
      readonly executionId: ExecutionId;
    };

type NonRecoveryOperatorResolutionContractV1 =
  | {
      readonly kind: "request-operational-recheck";
    }
  | {
      readonly kind: "authorize-known-terminal-execution-replacement";
      readonly priorExecutionId: ExecutionId;
      readonly requiredAcceptedConsequence:
        "prior-execution-remains-authoritative-history-and-this-authorizes-one-additional-execution-occurrence";
    };

type OperatorResolutionContractV1 =
  | NonRecoveryOperatorResolutionContractV1
  | {
      readonly kind: "authorize-uncertain-execution-replacement";
      readonly priorExecutionId: ExecutionId;
      readonly requiredAcceptedRisk:
        "prior-execution-may-have-produced-the-external-effect-and-the-replacement-may-produce-that-effect-again";
    };

type OperatorBlockerSourceV1 =
  | {
      readonly kind: "producer-occurrence";
      readonly producer: NonRecoveryOperationalBlockerProducerV1;
      readonly causeDescriptor: ArtifactRef;
      readonly baseStateRevision: StateRevision;
    }
  | {
      readonly kind: "recovery-causal";
      readonly producer: "recovery-operator";
      readonly cause: RecoveryOperationalBlockerCauseV1;
    };

interface GateAOperatorActionRequestV1 {
  readonly schema: "gate-a-operator-action-request.v1";
  readonly runId: GateARunId;
  readonly blockerId: BlockerId;
  readonly obligationId: ObligationId;
  readonly workItemId: WorkItemId | null;
  readonly executionId: ExecutionId | null;
  readonly source: OperatorBlockerSourceV1;
  readonly mechanicalContinuations:
    readonly OperatorMechanicalContinuationV1[];
  readonly resolutionContracts: readonly OperatorResolutionContractV1[];
}

type GateAOperatorResolutionArtifactV1 =
  | {
      readonly schema: "gate-a-operator-resolution-artifact.v1";
      readonly kind: "request-operational-recheck";
      readonly runId: GateARunId;
      readonly blockerId: BlockerId;
      readonly operatorRequest: ArtifactRef;
    }
  | {
      readonly schema: "gate-a-operator-resolution-artifact.v1";
      readonly kind: "authorize-known-terminal-execution-replacement";
      readonly runId: GateARunId;
      readonly blockerId: BlockerId;
      readonly operatorRequest: ArtifactRef;
      readonly priorExecutionId: ExecutionId;
      readonly acceptedConsequence:
        "prior-execution-remains-authoritative-history-and-this-authorizes-one-additional-execution-occurrence";
    }
  | {
      readonly schema: "gate-a-operator-resolution-artifact.v1";
      readonly kind: "authorize-uncertain-execution-replacement";
      readonly runId: GateARunId;
      readonly blockerId: BlockerId;
      readonly operatorRequest: ArtifactRef;
      readonly priorExecutionId: ExecutionId;
      readonly acceptedRisk:
        "prior-execution-may-have-produced-the-external-effect-and-the-replacement-may-produce-that-effect-again";
    };

type OperationalBlockerMaterializationRequestV1 =
  | {
      readonly kind: "producer-occurrence";
      readonly runId: GateARunId;
      readonly baseStateRevision: StateRevision;
      readonly producer: NonRecoveryOperationalBlockerProducerV1;
      readonly obligationId: ObligationId;
      readonly workItemId: WorkItemId | null;
      readonly executionId: ExecutionId | null;
      readonly causeDescriptor: ArtifactRef;
      readonly resolutionContracts:
        readonly NonRecoveryOperatorResolutionContractV1[];
    }
  | {
      readonly kind: "recovery-causal";
      readonly runId: GateARunId;
      readonly workItem: WorkItemRef;
      readonly execution: ExecutionRef;
      readonly cause: RecoveryOperationalBlockerCauseV1;
    };

interface MaterializedOperationalBlockerV1 {
  readonly blocker: OperationalBlocker;
}

type OperatorResolutionStateEffect =
  | {
      readonly kind: "resolve-blocker-only";
    }
  | {
      readonly kind: "resolve-blocker-and-replace-execution";
      readonly priorExecutionId: ExecutionId;
    };

interface ValidateOperatorResolutionRequestV1 {
  readonly runId: GateARunId;
  readonly operatorResolutionPath: string;
  readonly outstandingOperationalBlockers:
    readonly OperationalBlocker[];
}

interface ValidatedOperatorResolutionV1 {
  readonly envelope: OperatorResolutionEnvelope;
  readonly effect: OperatorResolutionStateEffect;
}

interface OperatorResolutionEnvelope {
  readonly schema: "gate-a-operator-resolution.v1";
  readonly runId: GateARunId;
  readonly blockerId: BlockerId;
  readonly resolution: ArtifactRef;
}
```

For a non-recovery operational blocker, `causeDescriptor` is the exact immutable
canonical description of the producer-owned operational condition.

The producing module owns:

```text
cause-descriptor schema
domain meaning
exact causal fields
runtime validation
```

It does not own `BlockerId` or Operator Action Request identity.

Every non-recovery cause descriptor uses the runner canonical JSON
serialization:

```text
UTF-8 JSON
object keys recursively lexicographically sorted
array order preserves semantic order
all required fields present
no undefined
no bigint
no NaN
no positive or negative Infinity
no insignificant whitespace
no trailing newline
mediaType = application/json
```

Occurrence-only material must not enter the cause descriptor unless that value
is genuinely part of the producer-domain causal condition.

In particular, a producer cause descriptor must not include merely for
identity:

```text
StateRevision
RunnerSessionId
ownership generation
wall-clock timestamp
process ID
temporary path
log path
random UUID
retry counter
```

`basisArtifacts`, logs, diagnostics, and other changing evidence are not blocker
identity. They remain separate provenance.

For non-recovery blocker identity, the exact producer cause identity is:

```text
causeDescriptor.sha256
```

Every M3, M5, M6, or M7 `OperationalBlocker` must be materialized through the
M8-B operational-boundary contract.

Those modules may establish producer-domain cause semantics and immutable cause
descriptors, but they do not independently invent:

```text
BlockerId
Operator Action Request schema
Operator Action Request bytes
operator-resolution kinds
operator-resolution state effects
```

The producing module's accepted NIB-M determines which
`NonRecoveryOperatorResolutionContractV1` values are lawful for each exact
producer cause.

M8-B validates the common materialization contract and normalizes identity and
presentation. It does not infer or broaden producer-domain continuation rights.

M8-B owns exactly two operational-blocker identity policies.

For one non-recovery producer occurrence:

```text
workItemComponent =
    "work-item:null"
    when workItemId == null

    otherwise
    "work-item:" + workItemId

executionComponent =
    "execution:null"
    when executionId == null

    otherwise
    "execution:" + executionId

BlockerId =
    deriveId(
        "gate-a-operational-blocker-occurrence.v1",
        runId,
        producer,
        obligationId,
        workItemComponent,
        executionComponent,
        causeDescriptor.sha256,
        decimal baseStateRevision
    )
```

The same exact cause rediscovered after a disposed occurrence and a later
authoritative re-evaluation therefore receives a new blocker identity.

For one M8 recovery causal condition:

```text
BlockerId =
    deriveId(
        "gate-a-recovery-operational-blocker.v1",
        runId,
        workItemId,
        executionId,
        recoveryCause
    )
```

Recovery blocker identity does not contain:

```text
StateRevision
ownership generation
reconciliation episode
observation ordinal
trace ArtifactRef
ReconciliationPendingRef
timestamp
```

The same Execution and same still-active recovery cause therefore reuse the
same exact blocker across fresh reconciliation episodes.

For an M8 recovery blocker, the representative `obligationId` is exactly:

```text
workItem.sourceObligationIds[0]
```

The WorkItem source-obligation list must already be non-empty under the accepted
WorkItem invariants.

That value is a deterministic presentation anchor only. It does not assert that
the selected obligation uniquely caused the recovery blocker.

For:

```text
cause = pending-policy-exhausted
```

the exact OAR continuation contract is:

```ts
mechanicalContinuations = [
  {
    kind: "resume-reconciliation",
    executionId: exact ExecutionId,
  },
]

resolutionContracts = [
  {
    kind: "authorize-uncertain-execution-replacement",
    priorExecutionId: exact ExecutionId,
    requiredAcceptedRisk:
      "prior-execution-may-have-produced-the-external-effect-and-the-replacement-may-produce-that-effect-again",
  },
]
```

For:

```text
cause = no-recovery-capability
```

or:

```text
cause = executor-domain-indeterminacy
```

the exact OAR continuation contract is:

```ts
mechanicalContinuations = []

resolutionContracts = [
  {
    kind: "authorize-uncertain-execution-replacement",
    priorExecutionId: exact ExecutionId,
    requiredAcceptedRisk:
      "prior-execution-may-have-produced-the-external-effect-and-the-replacement-may-produce-that-effect-again",
  },
]
```

A fresh runner resume may re-enter M8 reconciliation for an exact unresolved
Execution with an outstanding `pending-policy-exhausted` recovery blocker
without first disposing that blocker.

That resume is not an operator resolution.

It may perform only the already-safe observational reconciliation permitted by
the exact pending witness. Ordinary campaign progression remains blocked unless
the recovery cause is mechanically superseded or an accepted operator
resolution is committed.

For a `producer-occurrence` materialization:

```text
mechanicalContinuations = []
```

M8-B accepts only duplicate-free `resolutionContracts`.

The only permitted contracts are:

```text
request-operational-recheck
authorize-known-terminal-execution-replacement
```

A non-recovery producer may not request:

```text
authorize-uncertain-execution-replacement
```

If `authorize-known-terminal-execution-replacement` is present:

```text
request.executionId != null
contract.priorExecutionId == request.executionId
```

M8-B canonicalizes the OAR resolution-contract array in this fixed order:

```text
1. request-operational-recheck
2. authorize-known-terminal-execution-replacement
```

The existence of a contract in an OAR means only that this exact blocker cause
permits that operator request form.

It does not mean the requested state transition is still admissible when a
future operator artifact is submitted.

M2 remains the current-state admissibility authority.

For every unresolved execution, M8 consumes the complete `UnresolvedExecutionRecoveryRef` and invokes the exact `ExecutionRecoveryPort` implemented by the owning executor when reconciliation is required.

The same M8 classification machinery serves:

- restart recovery barriers;
- in-session execution uncertainty.

The owning executor provides observations only.

M8 alone derives authoritative recovery disposition.

The exact observation mapping is:

```text
not-executed observation carrying one valid exact NonExecutionProofRef
whose common bindings and artifacts pass M8 validation
→ PROVEN-NOT-EXECUTED
→ resolution evidence preserves the exact executor-owned proof basis

terminal observation with captured response
→ PROVEN-COMPLETED
→ recoveredOutcome.kind = captured

terminal observation with known technical failure
→ PROVEN-COMPLETED
→ recoveredOutcome.kind = technical-failure

pending observation carrying one valid exact ReconciliationContinuabilityRef
whose common bindings and artifacts pass M8 validation
→ RECONCILABLE intermediate step
→ construct the exact ReconciliationPendingRef evidence projection
→ keep recovery barrier closed
→ M8 may automatically re-observe under its finite NIB-M policy

unknown observation carrying one valid exact RecoveryIndeterminacyRef
whose common bindings and artifacts pass M8 validation
→ executor-domain recovery exhaustion
→ UNRESOLVABLE
→ resolution evidence preserves the exact executor-owned indeterminacy basis
→ exact OperationalBlocker

no usable recovery capability for a possibly-dispatched execution
→ do not invoke the owning executor recovery port
→ direct UNRESOLVABLE under the existing rule
→ exact OperationalBlocker

automatic reconciliation policy exhausted while the last accepted observation
remains pending
→ M8 automatic-policy exhaustion, not executor-domain recovery exhaustion
→ retain the exact ReconciliationPendingRef
→ create no RecoveryIndeterminacyRef and no terminal recovery resolution
→ exact pending-policy-exhaustion OperationalBlocker
→ OPERATOR-ACTION-REQUIRED
```

Inability to establish non-execution proof is not an independent M8
classification input. The owning executor must return a terminal observation,
a pending observation carrying a valid exact
`ReconciliationContinuabilityRef`, or an unknown observation carrying a valid
exact `RecoveryIndeterminacyRef` according to its exact domain contract.

A returned not-executed observation whose required `NonExecutionProofRef` is
missing or invalid is an implementation/process/integrity failure, not
`UNRESOLVABLE`.

Before classifying any unresolved Execution, M8-B validates and indexes the
complete outstanding operational-blocker set.

Every outstanding operational blocker must carry one intact
`GateAOperatorActionRequestV1` whose bindings and identity policy validate
against the blocker.

For recovery planning, only OARs with:

```text
source.kind == recovery-causal
source.producer == recovery-operator
```

are M8 recovery blockers.

A valid non-recovery OAR remains authoritative and untouched but does not
become a recovery blocker merely because it references the same WorkItem or
Execution.

Malformed retained OAR bytes, a missing/corrupt OAR artifact, an invalid
blocker/OAR binding, or an identity mismatch in retained authority is an
integrity failure.

At most one M8 recovery blocker may be outstanding for one Execution.

A pre-existing recovery blocker with cause:

```text
no-recovery-capability
executor-domain-indeterminacy
```

is valid only when its Execution is absent from the supplied unresolved set.

If such a terminal recovery blocker and the same Execution both appear in the
active unresolved set, the snapshot/request is inconsistent and recovery fails
as an integrity failure before invoking M8-A.

An outstanding:

```text
pending-policy-exhausted
```

recovery blocker is compatible with the same Execution remaining unresolved
and does not prevent a fresh M8-A episode.

M8 processes every legitimate supplied unresolved Execution sequentially in
request order even if another Execution or pre-existing terminal recovery
blocker already guarantees that the aggregate plan will be blocked.

A legitimate blocked result for one Execution never causes fail-fast of later
unresolved Executions.

Integrity, contract, or dependency failure still aborts the whole invocation.

After all classifications, M8 computes the set of M8 recovery blockers that
would remain outstanding after the planned dispositions.

`RecoveryPlan.kind = "cleared"` is valid only when:

```text
every supplied unresolved Execution terminated as
    PROVEN-NOT-EXECUTED
    or
    PROVEN-COMPLETED

AND

zero M8 recovery blocker remains outstanding after planned dispositions
```

Otherwise the aggregate plan is `blocked`.

A pre-existing terminal recovery blocker whose Execution is no longer in
`RecoveryRequest.unresolvedExecutions` is not duplicated into
`RecoveryPlan.blockers`; it remains authoritative in the snapshot and still
forces `RecoveryPlan.kind = "blocked"`.

`RecoveryPlan.blockers` contains only exact recovery blockers
materialized/reused for positions in the supplied unresolved-execution request.

`RecoveryPlan.kind = "blocked"` is required when any execution is `UNRESOLVABLE` or when the finite automatic reconciliation policy ends while a reconcilable execution is still pending.

For `RecoveryPlan.kind = "blocked"`, `resolutions`, `pending`, and `blockers`
preserve the order of the corresponding entries in
`RecoveryRequest.unresolvedExecutions`.

Each supplied unresolved Execution contributes to exactly one recovery position:

```text
terminal classification
→ exactly one ExecutionRecoveryResolution in resolutions
→ no ReconciliationPendingRef for that Execution

pending after finite automatic reconciliation exhaustion
→ no ExecutionRecoveryResolution for that Execution
→ exactly one ReconciliationPendingRef in pending
```

An Execution may never appear in both `resolutions` and `pending`.

For every `UNRESOLVABLE` resolution, `blockers` contains exactly the
OperationalBlocker carried by that resolution.

For every entry in `pending`, `blockers` contains exactly one
`OperationalBlocker` for that same Execution and its stable
`pending-policy-exhausted` causal condition.

A later reconciliation episode that ends pending again reuses that exact
blocker; episode occurrence is not blocker identity.

For one unresolved Execution `E`, M8-B applies this exact matrix:

```text
existing M8 recovery blocker = none
M8-A result = PROVEN-NOT-EXECUTED
→ no blocker
→ no disposition

existing = none
M8-A result = PROVEN-COMPLETED
→ no blocker
→ no disposition

existing = none
M8-A result = pending-policy-exhausted
→ materialize B_pending(E)

existing = none
M8-A result = no-recovery-capability
→ materialize B_no_capability(E)
→ construct UNRESOLVABLE

existing = none
M8-A result = executor-domain-indeterminacy
→ materialize B_domain(E)
→ construct UNRESOLVABLE

existing = B_pending(E)
M8-A result = PROVEN-NOT-EXECUTED
→ dispose B_pending(E)
→ create no new blocker

existing = B_pending(E)
M8-A result = PROVEN-COMPLETED
→ dispose B_pending(E)
→ create no new blocker

existing = B_pending(E)
M8-A result = pending-policy-exhausted
→ reuse exact B_pending(E)
→ disposition empty

existing = B_pending(E)
M8-A result = executor-domain-indeterminacy
→ dispose B_pending(E)
→ materialize B_domain(E)
→ construct UNRESOLVABLE

existing = B_pending(E)
M8-A result = no-recovery-capability
→ integrity failure

existing = B_no_capability(E)
AND E supplied as unresolved
→ integrity failure before M8-A

existing = B_domain(E)
AND E supplied as unresolved
→ integrity failure before M8-A
```

`B_pending(E)`, `B_no_capability(E)`, and `B_domain(E)` are distinct logical
IDs because their exact recovery causes differ.

The operator-resolution artifact is operator-authored input.

The mutable filesystem path is never authority.

M8-B reads the exact file bytes once, validates those exact bytes, seals those
same exact bytes into immutable artifact storage, and then constructs
`OperatorResolutionEnvelope`.

M8-B must not parse one filesystem read and seal a later filesystem read.

M8-B does not canonicalize or rewrite operator-authored bytes before sealing.
The exact submitted UTF-8 JSON bytes are retained.

The three and only three v1 resolution kinds are:

```text
request-operational-recheck
authorize-known-terminal-execution-replacement
authorize-uncertain-execution-replacement
```

No generic:

```text
resolve
acknowledge
ignore
force-success
force-failure
mark-not-executed
mark-completed
retry-anyway
```

operator action exists.

`request-operational-recheck` maps to:

```ts
{ kind: "resolve-blocker-only" }
```

It means only:

```text
dispose this exact blocker occurrence
allow its authoritative producer boundary to be evaluated again
```

It does not assert that the producer-domain condition now passes.

Both replacement resolution kinds map to:

```ts
{
  kind: "resolve-blocker-and-replace-execution",
  priorExecutionId: exact prior Execution,
}
```

The operator never provides the successor ExecutionId or next attempt ordinal.

M2 derives the exact successor when the transition is currently admissible.

For every submitted operator-resolution artifact `R`, M8-B requires:

```text
R.runId == current run
R.blockerId == exact currently outstanding target blocker
R.operatorRequest == exact target blocker.operatorRequest
R.kind is present in the exact OAR resolutionContracts
```

For `request-operational-recheck`, no Execution replacement is requested.

For `authorize-known-terminal-execution-replacement`:

```text
R.priorExecutionId == exact OAR contract priorExecutionId
R.acceptedConsequence ==
"prior-execution-remains-authoritative-history-and-this-authorizes-one-additional-execution-occurrence"
```

For `authorize-uncertain-execution-replacement`:

```text
R.priorExecutionId == exact OAR contract priorExecutionId
R.acceptedRisk ==
"prior-execution-may-have-produced-the-external-effect-and-the-replacement-may-produce-that-effect-again"
```

M8 validates resolution meaning.

M2 independently validates whether the resulting state effect remains legal in
the current authoritative state.

A valid operator artifact is not a permanent capability token.

A `PROVEN-NOT-EXECUTED` or `PROVEN-COMPLETED` resolution creates no recovery
blocker merely by being proven.

The `pending` array is empty when the blocked plan contains no
pending-policy-exhausted Execution.

The `resolutions` array may contain proven terminal resolutions alongside
`UNRESOLVABLE` terminal resolutions when different unresolved Executions in the
same RecoveryRequest produce different classifications.

This transport is required so M1 can construct the exact
`AdmitExecutionRecoveryV1` shape already defined by M2 without reconstructing,
dropping, or inventing M8 recovery facts.

`ClassifyUnresolvedExecutionResult.kind = "resolved"` returns only a proven non-execution or proven completed terminal outcome.

`ClassifyUnresolvedExecutionResult.kind = "blocked"` is the only in-session result for unresolved uncertainty that cannot be closed automatically in the current invocation.

For `blocked`:

* `resolution` is non-null only for an `UNRESOLVABLE` terminal classification;
* `lastPending` is non-null only when the automatic reconciliation policy ended while the execution remained reconcilable;
* exactly one of `resolution` and `lastPending` is non-null.

M8 must not convert pending into `PROVEN-NOT-EXECUTED`, `PROVEN-COMPLETED`, or `UNRESOLVABLE` merely because time passed.

M8 automatic-policy exhaustion preserves the last accepted pending fact. It
must not manufacture executor-domain recovery exhaustion, a
`RecoveryIndeterminacyRef`, or an `UNRESOLVABLE` classification.

`RecoveryRequest.outstandingOperationalBlockers` is the complete ordered set of
currently outstanding `OperationalBlocker` values from the exact
`stateRevision` supplied in the request.

M1 performs only the structural `CampaignBlocker.kind == "operational"`
projection needed to construct this field. M1 does not decide blocker
applicability, causal supersession, or disposition.

M8 alone determines `blockerIdsToDispose`.

For one `ClassifyUnresolvedExecutionRequest`,
`blockerIdsToDispose` contains exactly the duplicate-free set of currently
outstanding operational blocker IDs whose exact causal condition is
mechanically superseded by the recovery fact returned for that same Execution.

M8 must not include:

* a SemanticBlocker;
* an OperationalBlocker belonging to another causal condition;
* an OperationalBlocker whose condition remains true after the returned
  recovery fact;
* a blocker merely because it references the same obligation or Execution.

A later `PROVEN-NOT-EXECUTED` or `PROVEN-COMPLETED` recovery may dispose an
earlier recovery blocker for the same Execution only when that terminal fact
mechanically supersedes the blocker cause.

A later `UNRESOLVABLE` classification may dispose an earlier pending-recovery
blocker for the same Execution when the new terminal classification
mechanically supersedes the earlier pending condition. The newly materialized
`UNRESOLVABLE` blocker is not disposed by that same classification.

Pending-policy exhaustion does not by itself authorize disposal of a blocker
whose exact causal condition remains pending.

For every supplied `RecoveryRequest.unresolvedExecutions` entry,
`RecoveryPlan.blockerDispositions` contains exactly one
`RecoveryBlockerDisposition` with the same `executionId`.

The disposition entries preserve
`RecoveryRequest.unresolvedExecutions` order.

Every `blockerIdsToDispose` value in the aggregate plan is copied exactly from
the corresponding M8 classification result.

The same `BlockerId` may not occur in more than one
`RecoveryBlockerDisposition` in the same RecoveryPlan.

An empty `blockerIdsToDispose` array is valid and means that the returned
recovery fact mechanically supersedes no currently outstanding operational
blocker.

M1 may not add, remove, substitute, or infer a blocker disposition.

M2 remains responsible for validating that every supplied disposition is
structurally legal under `AdmitExecutionRecoveryV1`.

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

The durable M2 Arm transition is the side-effect permission linearization point.

Before successful Arm commit, the corresponding external effect is not treated
as having become possible.

After successful Arm commit, the effect is conservatively treated as possibly
executed and the Execution is unresolved until an authoritative terminal
execution disposition is admitted.

This remains true if the runner process crashes after Arm and before the owning
executor returns, including the case where the actual external call did not in
fact begin.

The exact Arm authority must therefore contain enough immutable information to
reconstruct `ArmedExecutionDispatchRef` and the initial
`UnresolvedExecutionRecoveryRef` after restart without consulting mutable
workspace state.

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

Terminal recovery resolutions are exactly:

```text
PROVEN-NOT-EXECUTED
PROVEN-COMPLETED
UNRESOLVABLE

RECONCILABLE is an intermediate recovery step only.
```

A possibly executed unresolved cognitive execution may not be blindly retried.

M4 and M7 implement `ExecutionRecoveryPort` for externally effectful executions that can become epistemically ambiguous.

M4 and M7 receive the exact `ArmedExecutionDispatchRef` for the execution they
perform. Neither module may manufacture or infer missing arm-time dispatch
identity from an `ExecutionRef`.

An executor return of `kind = "uncertain"` enriches the durable unresolved
record. It is not the transition that makes the Execution unresolved.

M6 does not implement `ExecutionRecoveryPort`: its Python validation subprocesses are required to be read-only with respect to authoritative external systems and replay-safe against the same exact immutable validation input.

M8 is the sole execution-uncertainty classifier and recovery-barrier consumer of those ports. An executor may report evidence through its port; it may not commit a recovery classification or authoritative state directly.

If an outcome cannot be established, automatic progression stops with `OPERATOR-ACTION-REQUIRED`.

## 20. Recovery barrier

A session taking ownership of an existing `GateARun` must cross a recovery barrier before it normally dispatches new campaign effects.

The complete active unresolved set includes every Execution for which a durable
Arm fact exists, no authoritative terminal execution disposition exists, and no
explicit `ExecutionProgressionSupersessionRef` revokes that Execution's future
progression/recovery authority, regardless of whether M4 or M7 ever returned an
explicit uncertain capture.

Progression supersession is not a terminal execution-outcome classification. A
superseded prior Execution may remain epistemically unknown while being excluded
from the active unresolved-recovery set.

The barrier consumes each complete `UnresolvedExecutionRecoveryRef`, including
its WorkItem, durable dispatch state, dispatch intent/evidence, any captured
result, and executor-owned recovery capability when one exists.

For a crash immediately after Arm with no later executor material, that
descriptor is reconstructed directly from the exact durable
`ArmedExecutionDispatchRef`.

The barrier must:

```text
load verifiable durable authority
→ enumerate complete unresolved-execution recovery descriptors
→ for each descriptor invoke M8 classification
→ if no usable recovery capability exists:
     use the direct UNRESOLVABLE path without invoking the recovery port
→ if observation is pending with valid ReconciliationContinuabilityRef:
     remain inside recovery barrier
     automatically re-observe under finite M8 NIB-M reconciliation policy
→ if observation is unknown with valid RecoveryIndeterminacyRef:
     materialize the exact UNRESOLVABLE resolution and blocker
→ preserve every proven completed recovered outcome
→ preserve every proven non-execution
→ materialize exact blockers for UNRESOLVABLE executions
→ materialize exact blockers when the finite reconciliation policy ends
  with an execution still pending
→ if any blocker exists:
     OPERATOR-ACTION-REQUIRED
→ otherwise reconstruct obligations
→ derive enabled WorkItems
→ only then permit normal campaign dispatch
```

A `RECONCILABLE` intermediate step is never sufficient to exit the barrier.

Recovery of `TechnicalExecutionFailure` is an ordinary `PROVEN-COMPLETED` execution recovery with `recoveredOutcome.kind = "technical-failure"`.

Recovery of a captured semantic result is an ordinary `PROVEN-COMPLETED` execution recovery with `recoveredOutcome.kind = "captured"`.

M8 may not invent an additional M2 lookup API, reconstruct dispatch identity from an `ExecutionRef`, or classify an execution from absence of a result alone.

Ownership transfer never resets a possibly executed operation to not executed.

If an operator explicitly supersedes an unresolved Execution and authorizes a
replacement Execution, M2 records one exact
`ExecutionProgressionSupersessionRef` in the same atomic authoritative
transition that disposes the target operational blocker and creates exactly one
successor Execution.

That supersession revokes only the prior Execution's future
campaign-progression and automatic-recovery authority. It does not manufacture
`PROVEN-NOT-EXECUTED`, `PROVEN-COMPLETED`, `UNRESOLVABLE`, a direct execution
outcome, or any other assertion about whether the prior external effect
occurred.

A later result from the superseded Execution may remain auditable, but no new
post-supersession outcome, uncertainty, recovery, cognitive-attempt
qualification, publication qualification, or other progression-bearing
admission for that prior Execution may silently re-enter authoritative campaign
progression.

## 21. `llm-runtime` boundary

Only M4 imports `llm-runtime`.

All other modules depend on M0 contracts and the M4 port.

The future `llm-runtime` Dependency Contract must close at least:

```text
cognitive WorkItem / hostile-review receipt execution identity
→ runner Execution / hostile-review receipt attempt identity
→ llm-runtime call
→ provider transport attempt(s)
```

For cognitive WorkItems, the construction binding is exact:

```text
receipt.execution_id = WorkItemId
receipt.attempts[*].attempt_id = corresponding ExecutionId
receipt.attempts[*].call_id = exact llm-runtime call identity
```

A runner-level protocol retry therefore creates a new `Execution` and, if a
qualified attempt is eventually reached, a new receipt attempt for the same
WorkItem/receipt identity.

A dependency-internal transport retry does not. Before qualification, the exact
attempt remains GateARun operational history rather than an incomplete
hostile-review receipt.

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

For cognitive-attempt classification, M6 invokes the existing Python
hostile-review authority against the exact immutable execution request and
captured result. For repository integrity and Gate A qualification, M6 invokes
the existing repository authorities against one exact sealed candidate
workspace.

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

The remote publication mutation itself is a `repository-control` WorkItem/Execution.

M7 captures the immediate publication effect but does not classify uncertainty.

If publication effect identity is uncertain, M7 returns an `UnresolvedExecutionRecoveryRef`, M1 commits it, and M8 performs the same execution-recovery classification used elsewhere in the runner.

A recovered completed publication produces a recovered `CapturedExecutionResult`, which is passed to the same M7 publication-observation qualification boundary as an immediately captured publication result.

There is no second publication-specific uncertainty-classification system.

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

This section defines the evidence interpreted by M7's publication `ExecutionRecoveryPort`; it does not grant M7 authority to classify the execution as `RECONCILABLE` or `UNRESOLVABLE`.

For an uncertain publication execution:

```text
exact target proves predecessor still present
AND exact executor-owned non-execution proof establishes that the exact
conditional publication operation did not apply its publication effect
→ M7 recovery observation = not-executed

exact target proves intended successor present
AND exact transition/material identity is established
→ M7 recovery observation = terminal captured publication observation

target state is nonterminal, the exact committed conditional publication
operation remains mechanically queryable, and another exact observation is
positively established to be non-mutating
→ M7 recovery observation = pending
→ carries exact ReconciliationContinuabilityRef

repository-domain evidence positively establishes that the exact committed
conditional publication operation cannot be classified as applied, not applied,
or safely re-observable through the available recovery capability
→ M7 recovery observation = unknown
→ carries exact RecoveryIndeterminacyRef
```

For M7 recovery, the relevant non-execution effect boundary is the exact
conditional mutation of the exact PublicationIntent target ref from its exact
expected predecessor toward its exact intended successor.

Observing only that the current target ref still equals the expected predecessor
is insufficient to prove that the exact publication operation never took
effect.

Current-state equality alone cannot establish historical non-execution because
the target may have changed after the attempted operation.

Likewise, absence of the intended successor from the currently observed target
is insufficient by itself.

M7 may return `kind = "not-executed"` only when its runtime-validated
executor-owned proof positively establishes non-application of the exact
conditional publication operation.

The exact M7 proof artifact schema, conditional-operation identity, repository
evidence interpretation, and dependency mechanism sufficient to prove
non-application belong to the M7 NIB-M and the Repository Dependency Contract.

A publication pending observation must not perform, reissue, or replay the
publication mutation. Its `ReconciliationContinuabilityRef` authorizes only the
exact non-mutating reconciliation observation.

Inability to contact the remote, absence of convenient repository evidence,
elapsed time, or a failed lookup is not by itself publication recovery
indeterminacy. M7 may return `unknown` only after runtime-validating positive
repository-domain evidence for the exact `RecoveryIndeterminacyRef`.

M7 owns validation of repository-domain continuability and indeterminacy. M8
must not reconstruct or reinterpret Git or repository semantics; it validates
the common envelope bindings and artifacts and owns recovery classification.

M8 alone converts those observations into the authoritative recovery disposition.

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

M7 first materializes `PublishedRepositoryViewRef` bound to that exact `PublicationConfirmationRef`.

M6 post-publication validation consumes that ref, not an unbound repository path.

The post-publication validation result must repeat the exact publication confirmation ID, target, candidate ID, and successor repository authority it validated.

A passing post-publication validation bound to that exact
`PublishedRepositoryViewRef` must be durably admitted before M2 may commit the
terminal Gate A ready fact.

`GATE-A-READY` is not emitted until all three hold:

```text
exact candidate mechanically qualified
AND
exact qualified representation published and confirmed
AND
exact post-publication validation passed for the bound PublishedRepositoryViewRef
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

For an `OPERATOR-ACTION-REQUIRED` projection:

```text
operatorRequests
=
the exact operatorRequest ArtifactRef of every currently outstanding
OperationalBlocker, preserving authoritative blocker order
```

Each operational blocker contributes exactly one Operator Action Request.

M8-B does not invent semantic Decision Request content.

Existing `DecisionRequestRef.request` artifacts remain M5-owned semantic
products and are projected exactly through the existing Decision Request path.

Projection precedence is exact:

```text
if the terminal Gate A ready fact exists
and its basis is the exact Gate A qualification,
publication confirmation, and passed post-publication validation
for the same bound PublishedRepositoryViewRef
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

An `OPERATOR-ACTION-REQUIRED` run may be resumed with an explicit operator
resolution.

A resume without an operator-resolution artifact may perform a mechanical
continuation only when an outstanding exact Operator Action Request explicitly
contains that continuation.

In v1 the only such continuation is:

```text
resume-reconciliation
```

for the exact unresolved Execution whose recovery blocker cause is
`pending-policy-exhausted`.

Such a resume does not dispose the blocker before reconciliation and does not
authorize ordinary campaign progression while its cause remains outstanding.

All other outstanding operational blockers require their exact producer-defined
resolution contract or remain blocking.

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

        sealed_candidate = repository_control.seal_initial_candidate(
            run,
            preflight.baselineAuthority
        )

        candidate_subject = campaign_authority.derive_subject({
            sealedCandidate: sealed_candidate.sealedCandidate
        })

        candidate = construct complete CandidateRevision(
            runId = run.runId,
            ordinal = 0,
            parentCandidateId = null,
            materialization = sealed_candidate.sealedCandidate.materialization,
            semanticSubject = candidate_subject.semanticSubject,
            producedByRepairIntentId = null
        )

        commit exact candidate through M2

    else:
        run = load_exact_run(command.runId)

        ownership_result = campaign_state.acquire_write_ownership(
            run,
            session.sessionId,
            exact loaded StateRevision
        )

        if ownership_result is rejected:
            require no GateARun mutation occurred

            if ownership_result.reason == INTEGRITY_FAILURE:
                fail invocation as implementation/integrity failure

            if ownership_result.reason == STALE_STATE:
                fail invocation non-zero as stale resume acquisition

            require ownership_result.reason == ACTIVE_OWNER_CONFLICT
            fail invocation non-zero as concurrent active-owner conflict

        ownership = ownership_result.authority
        snapshot = ownership_result.snapshot

        if command.operatorResolutionPath exists:
            validated_resolution =
                recovery_operator.validate_operator_resolution({
                    runId: run.runId,
                    operatorResolutionPath:
                        command.operatorResolutionPath,
                    outstandingOperationalBlockers:
                        snapshot.blockers filtered only by kind == operational
                        preserving snapshot order
                })

            commit through M2:
                validated_resolution.envelope
                validated_resolution.effect

            snapshot = committed snapshot

        root_preflight_obligation = exact obligation from snapshot where:
            obligationId ==
                deriveId(
                    "gate-a-root-preflight-obligation.v1",
                    run.runId,
                    contracts.preflightObligationDefinition.sha256
                )
            runId == run.runId
            candidateId == null
            reviewCampaignId == null
            definition == contracts.preflightObligationDefinition

        require exactly one such root_preflight_obligation exists

        if root_preflight_obligation is outstanding:
            if any outstanding OperationalBlocker exists:
                return project_runner_result(snapshot)

            preflight = campaign_authority.preflight(
                run,
                command.repositoryPath
            )

            if preflight is blocked:
                require every blocker references root_preflight_obligation
                commit exact blockers through M2 using
                    ownership + snapshot.stateRevision
                return project_runner_result()

            require preflight.kind == established

            commit exact baseline authority + publication target + satisfied
                root_preflight_obligation through M2
            snapshot = committed snapshot

            sealed_candidate = repository_control.seal_initial_candidate(
                run,
                preflight.baselineAuthority
            )

            candidate_subject = campaign_authority.derive_subject({
                sealedCandidate: sealed_candidate.sealedCandidate
            })

            candidate = construct complete CandidateRevision(
                runId = run.runId,
                ordinal = 0,
                parentCandidateId = null,
                materialization = sealed_candidate.sealedCandidate.materialization,
                semanticSubject = candidate_subject.semanticSubject,
                producedByRepairIntentId = null
            )

            commit exact candidate through M2
            snapshot = committed snapshot

        recovery_plan = recovery_operator.reconcile_prior_sessions({
            runId: run.runId,
            stateRevision: snapshot.stateRevision,
            newOwnershipGeneration: ownership.authority.generation,
            unresolvedExecutions: snapshot.unresolvedExecutions,
            outstandingOperationalBlockers:
                snapshot.blockers filtered only by kind == operational
                preserving snapshot order
        })

        if recovery_plan.kind == "blocked":
            for each unresolved Execution position in recovery_plan:
                select the exact M8 blockerDisposition for that Execution

                if that position has a terminal recovery resolution:
                    commit through M2:
                        that exact recovery resolution
                        its exact required recovery blocker when applicable
                        blockerIdsToDispose =
                            exact blockerDisposition.blockerIdsToDispose

                else:
                    require that position has an exact pending
                        ReconciliationPendingRef

                    commit through M2:
                        resolution = null
                        lastPending = that exact ReconciliationPendingRef
                        its exact pending-policy-exhaustion blocker
                        blockerIdsToDispose =
                            exact blockerDisposition.blockerIdsToDispose

            return OPERATOR-ACTION-REQUIRED projection

        require recovery_plan.kind == "cleared"

        for each resolution in recovery_plan.resolutions:
            if resolution.classification == PROVEN-COMPLETED:
                if resolution.recoveredOutcome.kind == "captured":
                    preserve recoveredOutcome.value as a newly captured result
                else:
                    preserve recoveredOutcome.value as a newly known technical failure

            else:
                require resolution.classification == PROVEN-NOT-EXECUTED

        for each resolution in recovery_plan.resolutions:
            select the exact M8 blockerDisposition where:
                blockerDisposition.executionId == resolution.executionId

            commit through M2:
                that exact recovery resolution
                its recovered terminal outcome when applicable
                blockerIdsToDispose =
                    exact blockerDisposition.blockerIdsToDispose

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
            sealed_successor = repository_control.apply_exact_patch_and_seal(
                exact source candidate,
                exact approved patch,
                exact RepairIntent
            )

            successor_subject = campaign_authority.derive_subject({
                sealedCandidate: sealed_successor.sealedCandidate
            })

            successor = construct complete CandidateRevision(
                runId = run.runId,
                ordinal = source candidate ordinal + 1,
                parentCandidateId = source candidate ID,
                materialization = sealed_successor.sealedCandidate.materialization,
                semanticSubject = successor_subject.semanticSubject,
                producedByRepairIntentId = exact RepairIntent ID
            )

            commit successor through M2

            if successor.semanticSubject != source candidate subject:
                prior campaigns become non-current for the successor subject by derivation
            else:
                retain the complete current campaign set for unchanged exact (S, P)
                do not create a campaign because CandidateRevision changed

            continue

        if one or more ordinary WorkItems are enabled:
            select only already-authorized WorkItems

            before creating a replacement runner Execution for cognitive work:
                require one exact admitted, unconsumed ExecutionRetryAuthorizationRef
                naming:
                    this WorkItem
                    the exact prior Execution
                    the exact accepted retry reason
                    the exact protocol bundle

                atomically consume that authorization when M2 creates
                the replacement Execution

            M1 never invents retry permission

            for each M4 or M7 externally effectful Execution selected for dispatch:

                immediately before Arm:
                    revalidate:
                        WorkItem still enabled
                        authorization still effective
                        expected StateRevision still current
                        ownership generation still current

                seal the exact Arm mutation artifact containing:
                    exact Execution
                    exact WorkItem
                    exact operation/input binding
                    exact current StateRevision
                    exact current OwnershipGeneration
                    exact fresh dispatch-revalidation basis
                    exact dispatch evidence
                    exact executor-owned RecoveryCapabilityRef if one is
                    available, otherwise null

                commit ArmExecutionDispatch through M2

                require the Arm commit succeeds before any external invocation

                armed_dispatch = construct ArmedExecutionDispatchRef from the
                    exact committed Arm authority

                from this point the Execution is unresolved until an
                authoritative terminal execution disposition exists

                mechanically dispatch through the owning executor using
                    armed_dispatch

                durably capture exactly one outcome for armed_dispatch:
                    captured result
                    known technical failure with no completed response
                    execution uncertainty enriching the already-durable unresolved
                    descriptor

                if the capture is execution uncertainty:
                    require capture.value.execution == armed_dispatch.execution
                    require capture.value.workItem == armed_dispatch.workItem
                    require capture.value.dispatchIntent == armed_dispatch.dispatchIntent

                    commit the exact uncertainty enrichment through M2

                    note:
                        if the process crashes after Arm but before this capture,
                        no uncertainty-enrichment mutation exists;
                        on resume M2 still reconstructs this Execution in
                        snapshot.unresolvedExecutions from the durable Arm authority
                        alone

                    recovery = recovery_operator.classify_unresolved_execution({
                        runId: run.runId,
                        unresolvedExecution: exact descriptor,
                        outstandingOperationalBlockers:
                            exact committed snapshot.blockers
                            filtered only by kind == operational
                            preserving snapshot order
                    })

                    if recovery.kind == "blocked":
                        commit through M2:
                            recovery.blocker
                            recovery.resolution if non-null
                            recovery.lastPending if non-null
                            blockerIdsToDispose =
                                exact recovery.blockerIdsToDispose

                        return OPERATOR-ACTION-REQUIRED projection

                    require recovery.kind == "resolved"

                    commit through M2:
                        recovery.resolution
                        its recovered terminal outcome when applicable
                        blockerIdsToDispose =
                            exact recovery.blockerIdsToDispose

                    if recovery.resolution.classification == PROVEN-COMPLETED:
                        if recovery.resolution.recoveredOutcome.kind == "captured":
                            treat recovery.resolution.recoveredOutcome.value
                                as a newly captured result
                        else:
                            treat recovery.resolution.recoveredOutcome.value
                                as a newly known technical failure

                    else:
                        require recovery.resolution.classification == PROVEN-NOT-EXECUTED

                        authorize a fresh replacement Execution from the exact
                        PROVEN-NOT-EXECUTED recovery resolution

                        do not consume a protocol retry authorization because
                        the prior external execution was proven not to have occurred

                        continue

            for each newly captured cognitive result:
                attempt_validation = mechanical_validation.validate_cognitive_attempt({
                    kind: cognitive-attempt,
                    runId: run.runId,
                    repositoryPath: exact candidate repository path,
                    executionRequest: exact CognitiveExecutionRequest,
                    capturedResult: exact CapturedExecutionResult
                })

                require attempt_validation binds the exact execution request,
                    execution, WorkItem, campaign, protocol bundle, role,
                    reviewer profile, prompt, packet, captured output, and
                    runtime evidence

                preserve attempt_validation as a newly validated cognitive attempt

            require no CognitiveAttemptValidationRequest exists for a technical failure

            delta = assurance_ledger.derive_complete_delta(
                evaluation_context,
                current authoritative snapshot,
                newly captured results,
                newly known technical failures,
                newly validated cognitive attempts,
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

            publication_execution = authorize exact repository-control Execution
            for the exact PublicationIntent WorkItem

            immediately before publication Arm:
                revalidate:
                    qualification still effective
                    no new blocker exists
                    exact target ref still equals transition.predecessor
                    transition.successor still equals prepared immutable repository object
                    fast-forward ancestry proof still valid
                    expected StateRevision still current
                    ownership generation still current

            seal the exact publication Arm mutation artifact containing:
                publication_execution
                exact PublicationIntent WorkItem
                exact transition/input binding
                exact current StateRevision
                exact current OwnershipGeneration
                exact fresh publication revalidation basis
                exact dispatch evidence
                exact M7 RecoveryCapabilityRef if one is available,
                otherwise null

            commit ArmExecutionDispatch through M2

            require the Arm commit succeeds before remote mutation

            publication_dispatch = construct ArmedExecutionDispatchRef from the
                exact committed Arm authority

            capture = repository_control.publish_conditionally({
                dispatch: publication_dispatch,
                intent: intent,
                candidate: exact candidate
            })

            if capture.kind == "uncertain":
                require capture.value.execution == publication_dispatch.execution
                require capture.value.workItem == publication_dispatch.workItem
                require capture.value.dispatchIntent == publication_dispatch.dispatchIntent

                commit the exact publication uncertainty enrichment through M2

                recovery = recovery_operator.classify_unresolved_execution({
                    runId: run.runId,
                    unresolvedExecution: capture.value,
                    outstandingOperationalBlockers:
                        exact committed snapshot.blockers
                        filtered only by kind == operational
                        preserving snapshot order
                })

                if recovery.kind == "blocked":
                    commit through M2:
                        recovery.blocker
                        recovery.resolution if non-null
                        recovery.lastPending if non-null
                        blockerIdsToDispose =
                            exact recovery.blockerIdsToDispose

                    return OPERATOR-ACTION-REQUIRED projection

                require recovery.kind == "resolved"

                commit through M2:
                    recovery.resolution
                    its recovered terminal outcome when applicable
                    blockerIdsToDispose =
                        exact recovery.blockerIdsToDispose

                if recovery.resolution.classification == PROVEN-NOT-EXECUTED:
                    retain the same PublicationIntent

                    continue

                require recovery.resolution.classification == PROVEN-COMPLETED
                require recovery.resolution.recoveredOutcome.kind == "captured"

                publication_observation =
                    recovery.resolution.recoveredOutcome.value

            else:
                publication_observation = capture.value

            qualification =
                repository_control.qualify_publication_observation({
                    intent: exact PublicationIntent,
                    candidate: exact candidate,
                    executionResult: publication_observation
                })

            if qualification.kind == "blocked":
                commit qualification.blocker through M2
                return OPERATOR-ACTION-REQUIRED projection

            require qualification.kind == "confirmed"
            require qualification.confirmation.transition == intent.transition
            require qualification.publishedView.publicationConfirmationId
                == qualification.confirmation.publicationConfirmationId
            require qualification.publishedView.target
                == intent.transition.target
            require qualification.publishedView.authority
                == intent.transition.successor
                by both commit SHA and tree SHA

            commit:
                qualification.confirmation
                qualification.publishedView
            through M2

            post_validation = mechanical_validation.post_publication({
                runId: run.runId,
                publishedView: qualification.publishedView
            })

            require post_validation.requestKind == "post-publication-integrity"
            require post_validation.publicationConfirmationId
                == qualification.confirmation.publicationConfirmationId
            require post_validation.target
                == qualification.publishedView.target
            require post_validation.validatedAuthority
                == qualification.publishedView.authority
                by both commit SHA and tree SHA

            if post_validation.passed is false:
                commit exact operational/integrity blocker through M2
                return OPERATOR-ACTION-REQUIRED projection

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

An incomplete bootstrap preflight is resumed only after the exact root preflight
obligation is still outstanding and no OperationalBlocker remains outstanding.
Resolving an operational blocker does not itself satisfy the preflight
obligation, establish repository authority, create the initial candidate, or
authorize normal campaign progression. M1 must re-run the existing M3 preflight
boundary and, on success, complete the same baseline-authority,
publication-target, root-obligation, sealed-candidate, semantic-subject, and
CandidateRevision ordinal-0 construction used by `start`. If preflight blocks
again, the newly established exact blockers are committed and the run remains
`OPERATOR-ACTION-REQUIRED`.

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
GI-03  CandidateRevision is constructed only from a sealed candidate
       materialization plus its exact derived semantic subject and is immutable
       after admission.
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
GI-14  A runner-level retry or replacement of a WorkItem creates a new
       Execution. Provider/transport retries internal to one external call do
       not.
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
GI-40  GATE-A-READY requires exact mechanical qualification, exact confirmed
       publication, and passed post-publication validation bound to the same
       exact PublishedRepositoryViewRef.
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
       qualified Decision Request, execution-retry authorization, and
       candidate-review-readiness result to M2.

GI-52  PublicationIntent proves the predecessor is an ancestor of the intended
       successor; CAS alone never authorizes an unrelated successor.

GI-53  A ReviewCampaign is created only after current protocol reviewer/profile
       prerequisites are established; a blocked prerequisite creates no
       executable campaign.

GI-54  In-session execution uncertainty is classified through M8 and the
       owning executor's recovery port before any continuation; an
       unestablished outcome returns OPERATOR-ACTION-REQUIRED rather than
       resuming or blind-retrying the WorkItem.

GI-55  Recovery may establish either a captured semantic result or a known
       terminal technical failure. Both are PROVEN-COMPLETED execution
       outcomes and remain explicitly distinct.

GI-56  RECONCILABLE is an intermediate recovery state only. No campaign
       external work may resume while any required recovery remains
       reconcilable.

GI-57  M8 is the sole authoritative classifier of execution uncertainty.
       M4 and M7 provide recovery observations; neither assigns
       RECONCILABLE or UNRESOLVABLE.

GI-58  Publication execution uncertainty uses the same
       UnresolvedExecutionRecoveryRef → M8 recovery path as other ambiguous
       external executions. No publication-specific recovery classifier
       exists.

GI-59  Post-publication validation is bound to one exact
       PublishedRepositoryViewRef and therefore to one exact publication
       confirmation, target, candidate, and successor repository authority.

GI-60  M6 validation subprocesses are read-only with respect to authoritative
       external systems and replay-safe against the same exact immutable
       validation input; M6 does not implement ExecutionRecoveryPort.

GI-61  For cognitive WorkItems, hostile-review receipt execution_id is the
       WorkItemId. If a qualified attempt is reached, every preserved
       receipt-admissible protocol attempt contributes one receipt attempt whose
       attempt_id is the corresponding runner ExecutionId, and the attempt
       call_id binds the exact llm-runtime call. A progression-superseded
       Execution whose protocol outcome was never mechanically established
       remains GateARun operational history and contributes no fabricated
       receipt attempt. Provider/transport retries remain below this identity
       boundary.

GI-62  M1 never invents cognitive protocol retry permission. M5 alone exposes
       an exact retry authorization from accepted attempt admissibility, and
       M2 consumes that authorization at most once when creating the
       replacement Execution.

GI-63  M4 captures exact cognitive attempt material, M6 alone obtains the
       checker-derived role-aware attempt classification through existing
       Python authority, and M5 consumes that exact typed result without
       reclassifying it.

GI-64  No schema-v3 hostile-review execution receipt is admitted before one
       qualified attempt exists. Exhaustion without qualification preserves
       exact GateARun attempt history and produces OPERATOR-ACTION-REQUIRED,
       not an incomplete receipt.

GI-65  A successful durable Arm transition is the external-effect permission
       linearization point. From that commit until either an authoritative
       terminal execution disposition or an explicit operator progression
       supersession exists, the armed Execution is conservatively
       POSSIBLY-DISPATCHED and belongs to the active unresolved recovery set,
       even if the owning executor never returned. Progression supersession does
       not assert an external outcome.

GI-66  M4 and M7 execute only from an exact ArmedExecutionDispatchRef produced
       after successful M2 Arm admission. Neither executor reconstructs its
       WorkItem, dispatch intent/evidence, or recovery identity from
       ExecutionRef alone.

GI-67  An explicit executor uncertainty capture enriches an already-unresolved
       armed Execution; it does not create unresolvedness. Restart recovery can
       reconstruct the initial unresolved descriptor from durable Arm authority
       alone.

GI-68  Every accepted pending recovery observation carries one exact validated
       ReconciliationContinuabilityRef proving that another invocation of the
       exact reconciliation operation is observational and cannot create,
       repeat, or replay the original external effect.

GI-69  Every accepted unknown recovery observation carries one exact validated
       RecoveryIndeterminacyRef proving executor-domain recovery exhaustion.
       No-capability direct UNRESOLVABLE and M8 automatic-policy exhaustion
       remain distinct paths and create neither envelope for the other.

GI-70  Operator-authorized Execution replacement atomically disposes the exact
       target operational blocker, records one exact
       ExecutionProgressionSupersessionRef, and creates exactly one successor
       Execution for the same WorkItem. The supersession revokes future
       progression/recovery authority only; it never manufactures execution
       truth for the prior Execution.

GI-71  Once an Execution has an authoritative progression supersession, later
       observations of that prior Execution may remain auditable but cannot
       create new authoritative progression-bearing outcome, recovery,
       cognitive-attempt qualification, publication qualification, or receipt
       truth for that superseded occurrence.
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

`GateARunSnapshot` therefore does not persist or expose a second
`campaignCurrentness` value. M3 derives currentness from exact current authority
and the authoritative campaign history.

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

### CP-11 — One uncertainty-classification path

An executor may report exact external observations.

Only M8 classifies unresolved execution uncertainty.

An executor may return pending only with an exact validated
`ReconciliationContinuabilityRef` and unknown only with an exact validated
`RecoveryIndeterminacyRef`.

`RECONCILABLE` keeps the recovery barrier closed.

If the finite automatic reconciliation policy cannot close a pending execution
during the current invocation, the runner retains the exact pending fact, emits
an exact operational blocker and `OPERATOR-ACTION-REQUIRED`, and creates no
executor-domain indeterminacy or terminal outcome.

### CP-12 — Published-state validation is identity-bound

Post-publication validation never consumes a bare mutable repository path as
proof of publication identity.

It consumes one `PublishedRepositoryViewRef` mechanically bound to the exact
`PublicationConfirmationRef`, target, candidate, and successor repository
authority.

A `PublicationConfirmationRef` alone is insufficient for `GATE-A-READY`.
The exact bound post-publication validation must pass before the terminal ready
fact may be committed.

### CP-13 — Receipt admission requires qualification

A logical cognitive execution has durable runner attempt history before it has
hostile-review receipt evidence.

Only the first qualified attempt permits M5 to assemble and seal the complete
schema-v3 receipt. No-qualified exhaustion retains the history, creates an
operational blocker, and admits no partial receipt.

### CP-14 — Arm is the unresolved-effect boundary

A successful durable Arm commit is the last authoritative boundary before an
externally effectful M4 or M7 invocation.

Before Arm, the exact Execution is not conservatively treated as externally
executed.

After Arm, it is conservatively unresolved until exact terminal disposition,
and restart may not depend on whether the executor managed to return an
uncertainty object before process interruption.

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
how one successful Arm produces the exact M4/M7 dispatch context and makes the Execution immediately reconstructible as unresolved across crash/restart
how WorkItems and Executions differ
how cognitive WorkItem, runner Execution, hostile-review receipt, receipt attempt, llm-runtime call, and provider transport attempt identities map without collapse
how M4 capture reaches existing Python validation through M6 and then M5 without reimplementation
how pre-receipt attempt history becomes one complete schema-v3 receipt only after qualification
where llm-runtime is allowed
where Python authority remains authoritative
how repair may proceed
when a Decision Request is legitimate
when Operator Action is required
what mechanically qualifies a candidate
which explicit M5 ledger products cross the module boundary
how exact cognitive retry authorization crosses from M5 to M2 and is consumed once
how M4 distinguishes no-response technical failure from uncertainty
how M4 and M7 positively establish safe re-observability for pending and executor-domain recovery indeterminacy for unknown
how executor-domain recovery exhaustion differs from M8 automatic-policy exhaustion and no-capability direct UNRESOLVABLE
what exact publication target and fast-forward Git transition may be mutated
what the CLI returns
why GATE-A-READY is justified
```

Further design therefore proceeds by module decomposition, external dependency contract closure, and test-contract construction.

It must not reopen the system semantics fixed here.
