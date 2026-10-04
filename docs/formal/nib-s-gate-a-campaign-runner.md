---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-system"
workspace: "turnlock-rust"
date: "2026-09-20"
step_id: 1
id: NIB-S-GATE-A-CAMPAIGN-RUNNER
version: "9.1.2"
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
- accepted ADR-041 through ADR-049, ADR-053, and ADR-054;
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

Version `6.0.9` closes the publication-intent work/admission and pre-Arm
staleness construction gaps without changing TURNLOCK product semantics.
Publication preparation now supplies the exact publication intent together with
its exact publication obligation and repository-control WorkItem for atomic M2
admission. Historical publication intents remain append-only, while a later
safe pre-Arm intent mechanically supersedes the prior publication obligation.
M2 Arm admission for repository publication now requires the exact currently
projected PublicationIntent WorkItem, preventing an authorized but unarmed
Execution for a historical intent from crossing the external-effect boundary.
An already-armed publication Execution remains governed exclusively by its
existing outcome/recovery lifecycle and cannot be bypassed by publication-intent
replacement.

Version `6.0.10` closes the pre-M7 repository-baseline and publication-realization
construction gaps without changing TURNLOCK product semantics.

Repository baseline observation/capture now precedes authoritative preflight:
M7 mechanically captures the exact immutable repository inspection, durable
baseline Git basis, and sealed baseline candidate; M3 interprets that exact
immutable inspection; M2 then admits the baseline/target/protocol and their
provenance atomically.

Publication preparation no longer accepts a caller-selected predecessor; M7
observes the exact current target authority itself.

Publication realization now distinguishes conditional-ref-update from
already-current.

Already-current publication uses no Execution and never crosses Arm.

Confirmed publication atomically satisfies its exact publication obligation.

A direct terminal publication attempt may establish an exact
PublicationNonApplicationRef proving that the authorized target-ref mutation was
not applied. This fact is distinct from PROVEN-NOT-EXECUTED and may permit safe
future PublicationIntent replacement without fabricating retry authority.

Version `6.0.11` closes the direct-versus-recovered publication non-application
provenance gap without changing TURNLOCK product semantics. A recovered
`PROVEN-COMPLETED` captured outcome remains eligible for ordinary executed-
publication qualification and confirmation, but it can never produce a
`PublicationNonApplicationRef`. M1 rejects an attempted recovered
`not-applied` qualification as an implementation/process/integrity failure
without submitting a publication-qualification mutation to M2; M2 accepts
`not-applied` only when the exact
captured result was introduced directly by `AdmitExecutionOutcomeV1`; snapshot
integrity enforces the same provenance condition. The required prior M2 recovery
resolution remains durable; the guard prevents only publication-qualification
mutation and PNA append.

The construction discovery classifications preserved by this revision are:

```text
baseline material must precede baseline authority admission
→ derived-from-existing-authority
  from GI-24 / GI-26 / GI-27 / fail-closed restart

old baseline-first-then-seal construction
→ authority-conflict-or-uncertain
```

```text
M7 observes publication predecessor itself
→ derived-from-existing-authority

already-current avoids Arm when no external mutation is required
→ derived-from-existing-authority

exact read-only already-current confirmation
→ accepted construction decision in NIB-S 6.0.10
```

```text
confirmed publication satisfies its publication obligation
→ derived-from-existing-authority

direct terminal ref non-application != PROVEN-NOT-EXECUTED
→ derived-from-existing-authority

PublicationNonApplicationRef representation
→ no-normative-impact construction mechanism
```

Version `6.0.12` closes the repository-inspection operational-blocker ownership
gap required before M7-A construction.

M7 repository inspection now returns producer-owned immutable operational cause
material instead of constructing `OperationalBlocker` directly.

M1 binds the exact current occurrence anchors.

M8-B remains the sole owner of `BlockerId`, Operator Action Request
construction, and `OperationalBlocker` materialization.

M2 remains the sole authoritative state-admission boundary.

This revision changes implementation-construction contracts only and creates no
TURNLOCK product semantics.

The construction discovery classifications recorded by this revision are:

```text
RepositoryInspectionResult returning OperationalBlocker directly
→ authority-conflict-or-uncertain

because M8-B already owns blocker identity/OAR materialization

RepositoryInspectionResult returning producer cause material
→ derived-from-existing-authority

exact NonRecoveryOperationalCauseRefV1 wrapper
→ no-normative-impact construction mechanism
```

No product ADR is created.

Version `6.0.13` closes the M7-A RepairIntent-to-candidate construction binding
before repository-control candidate-construction Module Brief authoring.

Candidate construction now consumes one complete authoritative RepairIntentRef
rather than separately supplied RepairIntentId and approvedPatch values.

The exact RepairIntent must name the exact source CandidateRevision, and M7 may
consume only that RepairIntent's exact approvedPatch.

A repaired sealed candidate and the CandidateRevision admitted from it must
retain exact parent-candidate, RepairIntent, and materialization bindings.

One RepairIntent may produce at most one CandidateRevision. The admitted
CandidateRevision itself is the append-only proof that the RepairIntent was
consumed; no mutable consumed flag exists.

M2 independently enforces these bindings during candidate admission and
snapshot reconstruction detects retained violations as integrity failures.

This revision changes implementation-construction contracts only and creates no
TURNLOCK product semantics.

The construction discovery classifications recorded by this revision are:

```text
separately supplied repairIntentId + approvedPatch at M7 candidate construction
→ authority-conflict-or-uncertain

because the caller could combine an authority identity with a different patch
artifact
```

```text
M7 consumes the complete admitted RepairIntentRef and uses only its
approvedPatch
→ derived-from-existing-authority
```

```text
one RepairIntent produces at most one CandidateRevision and that historical
candidate is append-only proof of consumption
→ derived-from-existing-authority
```

No product ADR is created.

Version `7.0.0` is a breaking construction-contract revision of version
`6.0.14`. It synchronizes the M4 realization boundary with the approved Pi
qualification result without changing TURNLOCK product semantics or
hostile-review protocol semantics.

M4 now consumes `@earendil-works/pi-ai@0.99.2` at Pi commit
`005af57d88ee23b33778f343a9595b32e67ff788` through one explicit,
campaign-owned adapter around public `Models.streamSimple(...)`. The adapter
is the sole Pi execution boundary; `AgentSession`, Pi coding-agent/subagent
loops, Codex CLI, Codex App Server, and other higher-level harness paths are
not M4 execution paths.

The construction runtime floor is Node.js `>= 22.19.0`.

The adapter preserves the existing one-Execution/one-protocol-attempt/
one-provider-call and recovery/evidence contracts. It exposes provider-owned
identity evidence without resolving the separate provider-reported
resolved-identity-versus-alias question routed to Issue #47.

The selected external M4 dependency and construction runtime floor change the
implementation boundary and minimum supported runtime. The downstream NIB-M
consumers therefore consume this new System Brief version.

This breaking construction revision changes implementation-construction
dependency selection only and creates no TURNLOCK product semantics.

No product ADR is created.

Version `7.0.1` closes the M7-A repository materialization and candidate-
construction contract before M7-A Module Brief publication without changing
TURNLOCK product semantics, hostile-review protocol semantics, canonical formal
semantics, or verification evidence.

M7 construction is decomposed into:

```text
M7-A repository materialization / candidate construction
and
M7-B publication / remote observation / recovery
```

M7-A owns deterministic construction of the exact publication successor `T`
from the retained baseline repository inspection and exact candidate
materialization.

M7-B owns observation of the exact current remote predecessor `P`, proof that
`P` is ancestor-or-equal to `T`, publication realization, remote mutation,
already-current observation, publication recovery, and publication
qualification. M7-B may not recompute or modify `T`.

`PublicationPreparationRequest` now carries the exact
`RepositoryInspectionRef` so the retained baseline Git basis used to derive `T`
is bound explicitly rather than reconstructed through mutable repository state.

The active M7-A Module Brief owns the exact `baselineGitBasis` representation,
candidate-materialization representation, evidence ordering, repository-
inspection operational causes, deterministic successor projection, and the
required Git Dependency Contract primitive surface.

The required Git Dependency Contract remains a separate construction artifact
that must exist before GREEN.

This revision is implementation-construction authority only.

No product ADR is created.

Version `7.0.2` closes the M6↔M3 mechanical-authority/campaign-authority seam
required before M3 Module Brief authoring.

M6 owns mechanical execution of existing TURNLOCK Python authority for:

- exact Gate A subject derivation;
- exact current hostile-review protocol/policy projection;
- complete hostile-review repository-record validation/projection.

M3 consumes mechanically established facts and owns:

- campaign interpretation;
- exact `(S, P)` currentness;
- imported campaign construction;
- reviewer-prerequisite interpretation;
- `INITIAL` / `SUBJECT-CHANGED` / `PROTOCOL-CHANGED` classification;
- `ReviewContext` / `GateAEvaluationContext`.

M3 never directly invokes Python authority and never reimplements existing
checker rules in TypeScript.

`ReviewCampaignId` is the hostile-review `review_id` identity.

Runner-produced campaign logical identity is based on `(runId, S, P)`, not
candidate identity or repository provenance.

Imported campaign provenance retains the exact schema-5 `repository_commit`;
it does not fabricate an unavailable repository tree identity.

Exact subject derivation must succeed before baseline preflight becomes
authoritative.

A trustworthy failure to derive `S` is not a normal campaign blocker/outcome.

The construction discoveries in this revision are implementation/construction
closure derived from existing authority, with no product-semantic change:

```text
M6 mechanical facts vs M3 campaign interpretation
ReviewCampaignId adoption of hostile-review review_id
imported provenance preserving repository_commit without invented tree
subject-derivation failure outside normal campaign outcomes
preflight subject witness retained before C0
exact ReviewCurrentnessRequest/currentness algorithm
```

This revision changes implementation-construction authority only.

No TURNLOCK product semantics change.
No hostile-review protocol semantics change.
No canonical formal semantics change.
No verification evidence change.
No product ADR is created.

Version `7.0.3` closes the M4 non-recovery operational-blocker
producer-ownership gap before M4-A Module Brief authoring without changing
TURNLOCK product semantics, hostile-review protocol semantics, canonical formal
semantics, or verification evidence.

`NonRecoveryOperationalBlockerProducerV1` now includes
`"cognitive-execution"`. This makes the already-required unavailable-provider-
credential operational path representable as exact M4-owned producer cause
material through the existing non-recovery operator boundary.

M4 owns the cognitive-execution cause schema and domain meaning.

M8-B remains the sole owner of `BlockerId`, Operator Action Request
construction, and `OperationalBlocker` materialization.

M2 remains the sole authoritative state-admission boundary.

This change does not grant M4 authority to construct `OperationalBlocker`,
assign recovery classifications, invent operator resolutions, or reinterpret
cognitive execution truth.

The construction discovery classifications recorded by this revision are:

```text
unavailable required provider credential requires OPERATOR-ACTION-REQUIRED,
but cognitive-execution is absent from NonRecoveryOperationalBlockerProducerV1
→ authority-conflict-or-uncertain

adding cognitive-execution to the closed producer union while preserving
M4 producer-domain cause meaning, M8-B blocker-materialization ownership,
and M2 authoritative-admission ownership
→ derived-from-existing-authority

exact union-member addition
→ no-normative-impact construction mechanism
```

No TURNLOCK product semantics change.
No hostile-review protocol semantics change.
No canonical formal semantics change.
No verification evidence change.
No product ADR is created.

Version `7.0.4` closes the remaining M3 operational-cause / M8-B blocker-
materialization / M2 obligation-admission seam before M3 Module Brief authoring.

M3 owns campaign-authority operational cause meaning and immutable cause
descriptors.

M3 never constructs `OperationalBlocker`, `BlockerId`, Operator Action Request,
operator-resolution identity, or operator-resolution state effects.

Every M3 operational blocker is materialized by M8-B from exact M3-owned
`NonRecoveryOperationalCauseRefV1` material.

Post-preflight M3 blocking conditions require an exact candidate-scoped
`ObligationRef` because every `OperationalBlocker` must reference an admitted or
co-admitted obligation.

`EstablishOperationalBlockersV1` is extended with `obligationsToAdd` so the
already-declared co-admission rule becomes mechanically realizable.

Insufficient reviewer prerequisites under the immutable current candidate/P are
`OPERATOR-ACTION-REQUIRED` but have no same-run operator resolution contract.

Invalid review authority over an already-authoritative immutable candidate is
also `OPERATOR-ACTION-REQUIRED` with no same-run operator resolution contract.

Invalid review authority before preflight remains genuinely recheckable because
no baseline authority has yet been admitted.

This revision changes implementation-construction authority only.

No TURNLOCK product semantics change.
No hostile-review protocol semantics change.
No canonical formal semantics change.
No verification evidence change.
No product ADR is created.

The construction discovery classification recorded by this revision is:

```text
derived-from-existing-authority
architecture-or-implementation
no-normative-impact
```

No ADR or Issue is created.

Version `8.0.0` is a breaking implementation-construction contract revision
that closes the remaining M5 construction gaps. It adds complete immutable
referenced-artifact closure on the existing M6→M3 review-authority seam;
`AssuranceRepositoryProjectionRef`; candidate provenance independent for
`RepairIntent` and assurance projection; assurance-only, repair-only, and
repair-plus-assurance successors; M5 assurance operational cause routing
through M8-B; and M7 publication non-recovery cause routing through M8-B.

The construction discovery classifications recorded by this revision are:

```text
repair-only assumption for every non-C0 candidate
→ authority-conflict-or-uncertain at construction level

assurance evidence needs exact candidate repository materialization
→ derived-from-existing-authority

AssuranceRepositoryProjectionRef
→ no-normative-impact construction mechanism

M6 review fact lacks immutable referenced-artifact closure required downstream
→ derived-from-existing-authority

adding exact closure to existing mechanical projection
→ no-normative-impact construction mechanism

M5 directly returning OperationalBlocker
→ authority-conflict-or-uncertain

M5 cause → M8-B materialization
→ derived-from-existing-authority

M7 non-recovery direct blocker result
→ authority-conflict-or-uncertain with accepted M8-B ownership
```

No TURNLOCK product semantics change.
No hostile-review protocol semantics change.
No M6/M3 ownership change.
No ReviewCampaign identity change.
No M3 operational-cause architecture change.
No blocker identity change.
No product ADR is created.

Version `8.0.1` corrects three stale repair-only active clauses left by the
`8.0.0` candidate-provenance generalization.

The accepted `8.0.0` architecture already allows assurance-only, repair-only,
and combined repair-plus-assurance successors.

This revision synchronizes GI-84, M7-A M7A-11 through its consuming Module
Brief, and M2 restart/replay prose with that already-accepted architecture.

The construction discovery classifications recorded by this revision are:

```text
stale repair-only clauses contradicting already-accepted generalized candidate
provenance
→ derived-from-existing-authority

exact wording/invariant synchronization
→ no-normative-impact construction correction
```

No construction architecture changes.
No TURNLOCK product semantics change.
No hostile-review protocol semantics change.
No formal-assurance semantics change.
No blocker/recovery semantics change.
No product ADR is created.

Version `9.0.0` is a breaking implementation-construction contract revision
driven by ADR-053 and hostile-review protocol v5. It adds the protocol-owned,
deterministic minimum-effective reviewer-acquisition boundary across M6 → M3 →
M5. Reviewer registry membership remains eligibility rather than execute-all
authority; acquisition is protocol-ordered, content-independent, round-based,
and expands only after qualified effective-identity collision.

The numeric `minimum_independent_reviewers` remains formal-assurance policy
outside protocol identity P. This revision changes no TURNLOCK product
semantics, Gate A semantic subject S, review-evidence schema, or execution-
receipt schema.

Version 9.0.1 closes two implementation-construction transport/restart seams
introduced by the accepted ADR-053 reviewer-acquisition architecture.

First, the exact reviewer-prerequisite acquisition basis admitted with a
runner-produced ReviewCampaign becomes an explicit deterministic
GateARunSnapshot projection. M5 therefore consumes the exact authoritative
basis after restart instead of rerunning M3, rereading P, or reconstructing
profile acquisition state.

Second, every selected cognitive reviewer WorkItem must retain the exact
GateAReviewerAcquisitionCandidateV1 selected by M1/M5 inside its executor-owned
M4 operation. M4 obtains provider and requestModel only from that exact
candidate; the Pi Dependency Contract may validate/realize those values but may
not select or substitute them.

This revision changes no reviewer-acquisition policy, formal-assurance
semantics, hostile-review protocol semantics, TURNLOCK product semantics,
effective-identity semantics, retry policy, recovery semantics, or module
ownership.

Both corrections are derived from existing ADR-053 / protocol-v5 authority and
introduce no product ADR.

Version `9.1.0` is an additive compatible implementation-construction revision
driven by ADR-054 and hostile-review protocol v6. It changes no system module,
cross-module type shape, TURNLOCK product semantics, Gate A semantic subject S,
reviewer-acquisition algorithm, review-evidence schema, or execution-receipt
schema. It closes provider-reported effective identity semantics, Pi Dependency
Contract realization conformance, the completed-response-without-required-
identity boundary, and the M5 operational-stop behavior.

Version 9.1.1 closes two M5-A implementation-construction seams.

1. ReviewContext construction no longer depends on a WorkItem whose M4
   operation itself requires that ReviewContext.

2. The exact initial-reviewer execution inputs required for first-round and
   later-round reviewer WorkItems are mechanically established upstream and
   retained in the admitted ReviewCampaignPrerequisiteBasisRefV1.

The correction preserves:

```text
M3 ownership of ReviewContext construction
M6 ownership of Python mechanical authority
M5 ownership of protocol-derived assurance ObligationRef / WorkItemRef construction
M1 ownership of first-round reviewer candidate selection only
M5 ownership of later-round reviewer candidate selection
M4 ownership of CognitiveExecutionOperationV1 validation/sealing
M2 ownership of authoritative state writes
```

The construction discoveries are classified exactly as follows:

```text
statement:
the active M3 ReviewContext construction input is cyclic with the active
M4 cognitive WorkItem operation contract

semantic disposition:
authority-conflict-or-uncertain at implementation-construction level,
resolved by synchronization of already accepted ownership/binding authority

affected layer:
architecture-or-implementation

normative impact:
none
```

```text
statement:
the exact initial-reviewer prompt/packet execution inputs required by accepted
hostile-review authority are not durably carried across the admitted
M6 → M3 → M5 campaign basis

semantic disposition:
derived-from-existing-authority

affected layer:
architecture-or-implementation

normative impact:
none
```

The exact M6 → M3 → retained basis mechanism is classified as:

```text
no-normative-impact construction mechanism
```

No TURNLOCK product semantic change.
No hostile-review protocol semantic change.
No Gate A semantic-subject change.
No reviewer-acquisition semantic change.
No retry semantic change.
No provider/model semantic change.
No review-evidence schema change.
No execution-receipt schema change.
No formal-assurance claim change.
No product ADR is created.

Version 9.1.2 closes the remaining M5-A protocol-retry-authority transport
seam.

The exact retry policy of the ReviewCampaign's bound protocol P is now
mechanically projected by M6, preserved without interpretation by M3, retained
inside ReviewCampaignPrerequisiteBasisRefV1, reconstructed unchanged by M2, and
consumed from that retained basis by M5.

M5 therefore never needs to reread current P, rerun M6/M3, infer retry policy
from an M6 attempt classification, or hardcode current protocol-v6 retry values.

Runner retry hard limits remain separately M2-owned and unchanged.

The construction discovery is classified exactly as follows:

```text
statement:
after a runner-produced ReviewCampaign has been admitted, M5 must derive
protocol retry admissibility from the exact protocol P bound to that campaign,
but the exact P retry-policy facts are not currently carried in the retained
ReviewCampaignPrerequisiteBasisRefV1

semantic disposition:
derived-from-existing-authority

affected layer:
architecture-or-implementation

normative impact:
none
```

No TURNLOCK product semantic change.
No hostile-review protocol semantic change.
No retry semantic change.
No runner hard-limit change.
No reviewer-acquisition semantic change.
No recovery semantic change.
No execution-receipt schema change.
No review-evidence schema change.
No formal-assurance claim change.
No product ADR is created.

## 2. System objective

Build one isolated TypeScript/Node assurance-tooling application that mechanically executes the accepted Gate A hostile-review protocol over exact candidate repository states, persists and recovers execution without fabricating external outcomes, applies only exact protocol-authorized repairs, starts a full new review campaign whenever a repair changes the semantic subject `S`, and publishes only an exact mechanically qualified candidate.

## 3. Realization and product boundary

The runner is assurance tooling. It is not the TURNLOCK production runtime.

The selected implementation realization is:

```text
language       = TypeScript
runtime        = Node.js >= 22.19.0
module system  = ESM
type checking  = strict TypeScript
application    = isolated repository tool
```

Production TURNLOCK code must not depend on this TypeScript application merely because the runner is implemented in TypeScript.

The runner consumes `@earendil-works/pi-ai@0.99.2` in-process through one
campaign-owned Pi M4 adapter. The selected Pi source identity is commit
`005af57d88ee23b33778f343a9595b32e67ff788`.

The adapter creates a fresh public `pi-ai` Context and invokes public
`Models.streamSimple(...)` directly. It does not invoke `AgentSession`, a Pi
coding-agent or subagent loop, Codex CLI, Codex App Server, or another
higher-level harness execution path.

The runner invokes existing Python validation authority out-of-process.

The runner invokes Git/repository mechanisms through an explicit repository boundary.

No artificial IPC layer is inserted between the runner and the Pi M4 adapter.

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

Branching, merging, speculative parallel candidate trees, and candidate
selection are outside the initial runner. A mutable worktree is never a
`CandidateRevision`.

Candidate construction supports exactly:

```text
C0:
    repair = null
    assurance = null

assurance-only successor:
    repair = null
    assurance != null

repair-only successor:
    repair != null
    assurance = null

repair + assurance successor:
    repair != null
    assurance != null
```

For every non-C0 candidate, the exact immediate parent `P` exists and at least
one of `RepairIntent R` or `AssuranceRepositoryProjection A` is non-null.

If `R != null`:

```text
R.runId == runId
R.candidateId == P.candidateId
```

If `A != null`:

```text
A.runId == runId
A.sourceCandidateId == P.candidateId
A.semanticSubject == P.semanticSubject
```

Candidate and sealed candidate agree exactly on parent, repair provenance,
assurance-projection provenance, and materialization. No fake `RepairIntent`
may place assurance evidence into repository state.

Candidate identity is exactly:

```text
candidateId =
deriveId(
    "candidate-revision.v2",
    runId,
    decimal ordinal,
    parentCandidateId or "-",
    producedByRepairIntentId or "-",
    producedByAssuranceProjectionId or "-"
)
```

No migration mechanism is required because no production runner state exists.

For an assurance-only successor:

```text
producedByRepairIntentId == null
producedByAssuranceProjectionId != null

M6-derived successor S ==
P.semanticSubject ==
A.semanticSubject
```

If M6 derives another subject, the invocation fails as an
implementation/process/integrity failure: no candidate is admitted and no
campaign-required interpretation is made. For repair plus assurance, `A` stays
bound to the parent subject; the M6-derived successor subject may differ only
because the separately authorized repair changed semantic-subject material.
Assurance projection paths are structurally excluded from Gate A subject
identity.

If the M6-derived successor subject changes, campaigns for the old subject
become historical. If exact `(S, P)` is unchanged, candidate identity or
construction provenance alone does not make a campaign stale.

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
→ one Pi M4 adapter call per protocol attempt
→ provider/transport attempts internal to that call
→ after the first qualified attempt, one complete hostile-review receipt
  aggregates every ordered protocol attempt
```

If a cognitive WorkItem reaches a qualified attempt and its complete
receipt is assembled:

```text
receipt.execution_id == WorkItemId
receipt.attempts[*].attempt_id == the corresponding runner ExecutionId
receipt.attempts[*].call_id == the exact Pi M4 adapter call identity
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
* a result merely because the Pi M4 adapter returned successfully.

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
M7 inspect repository and seal baseline candidate
    ↓
M6 derive exact S from the sealed candidate materialization
    ↓
M6 project exact current hostile-review authority from that materialization
    ↓
M3 interpret preflight and M2 retain exact S/P mechanical witnesses
    ↓
construct/admit complete current CandidateRevision
    ↓
for the current candidate, M6 project complete exact hostile-review authority
    ↓
M3 merge already registered campaigns plus newly mechanically valid repository
observations and enumerate complete canonical campaign sets:
    current campaigns = every campaign over exact (S, P)
    stale-protocol campaigns = every campaign over exact S and non-current P
    candidate/run/repository provenance does not filter either set
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
        create exactly one full runner-produced ReviewCampaign(runId, S, P)
        with candidate/repository authority retained only as provenance
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
* consumption and binding of the exact mechanically derived Gate A semantic subject;
* exact Gate A semantic-subject currentness;
* consumption and interpretation of exact mechanically projected hostile-review authority;
* exact current protocol bundle identity/currentness;
* protocol-owned reviewer/profile admissibility prerequisites;
* detection of subject/protocol staleness;
* construction of exact per-campaign `ReviewContext` and complete `GateAEvaluationContext`.

It does not redefine any protocol rule.

It does not select unregistered reviewer profiles or models.

M3 does not invoke repository Python validators directly.

M3 does not reimplement subject construction, canonical JSON hashing,
protocol-bundle validation, hostile-review evidence validation, or reviewer
profile parsing in TypeScript.

M3 does not manufacture repository tree identity for imported review evidence.

### M4 — `cognitive-execution`

Owns:

* the `CognitiveExecutionPort`;
* the sole direct import/use of `@earendil-works/pi-ai`, through the explicit Pi M4 adapter;
* mapping from cognitive WorkItem/Execution identity to ADR-049 receipt execution/attempt identity, Pi M4 adapter call identity, and provider-attempt evidence;
* dispatch/cancellation integration;
* raw result capture;
* exact attempt artifacts and runtime metadata needed to preserve pre-receipt
  history and later assemble execution receipts;
* secret injection into the LLM dependency boundary.

It does not adjudicate semantic correctness.

It does not retry outside the exact behavior authorized by the protocol and the Pi M4 Dependency Contract.

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
* exact assurance repository projection selection from immutable M5 evidence;
* explicit finding, evidence, adjudication, re-adjudication, obligation-disposition, RepairIntent, assurance-projection, and Decision Request products for M2 admission;
* determination that a candidate and its complete current/contributing campaign sets are ready to be submitted to mechanical Gate A validation.

It does not perform LLM calls.

It does not invoke Python validators.

It does not apply patches.

It does not declare Gate A READY independently of existing mechanical authority.

### M6 — `mechanical-validation`

Owns:

* subprocess invocation of existing repository Python validation authorities;
* exact mechanical Gate A subject derivation from one exact candidate
  materialization;
* exact mechanical current hostile-review authority projection from one exact
  candidate materialization;
* exact complete hostile-review review-record validation/projection;
* sealing of the corresponding mechanical projection artifacts;
* role-aware classification of exact captured cognitive attempts through the
  existing Python hostile-review validation authority;
* exact capture of validator inputs, outputs, exit status, candidate identity,
  and cognitive-attempt identity;
* admission-ready mechanical result artifacts;
* final mechanical Gate A qualification request for one exact sealed candidate;
* post-publication repository validation request.

M6 establishes mechanically validated facts.

M6 does not decide:

- campaign currentness;
- campaign-required;
- `INITIAL`;
- `SUBJECT-CHANGED`;
- `PROTOCOL-CHANGED`;
- `qualifyingReviewerProfileIds`;
- `ReviewContext`;
- `GateAEvaluationContext`;
- campaign blocker meaning.

Those are M3/M5/M8 responsibilities as already allocated.

It must invoke existing authorities rather than reimplementing them in TypeScript.

M6 validation invocations are read-only with respect to authoritative external systems.

They execute only against exact immutable validation inputs: an exact
cognitive execution request plus captured result, an exact sealed candidate, or
an exact `PublishedRepositoryViewRef`.

Exact candidate authority is the candidate materialization `ArtifactRef` plus
its referenced immutable content, not a caller-supplied mutable filesystem path.

The future M6 NIB-M will own the exact safe ephemeral realization needed to
invoke existing Path-based Python authority. That realization must not make a
mutable path authoritative, must not dereference candidate symlinks outside
candidate authority, and must not reimplement Python validation semantics.

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
* Git/repository inspection, including initial baseline inspection/capture;
* PublicationIntent realization and exact predecessor observation;
* construction of the exact publication admission bundle:
  `PublicationIntentRef` + publication `ObligationRef` + repository-control
  `PublicationIntent WorkItemRef`;
* conditional publication against the M7-observed exact predecessor;
* already-current observation and publication reconciliation;
* exact published-candidate materialization proof.

M7 construction decomposition:

```text
M7-A — repository materialization / candidate construction
- initial repository inspection and immutable baseline capture;
- publication-target identity resolution from local Git configuration;
- reconstructible baseline Git basis;
- exact C0 materialization;
- exact candidate representation;
- exact RepairIntent patch application;
- exact assurance repository projection application;
- assurance-only and combined repair-plus-assurance successor construction;
- Git tree projection and round-trip verification;
- deterministic publication-successor projection T;
- restart-safe local materialization of an already-projected T.

M7-B — publication / remote observation / recovery
- current target predecessor observation P;
- fast-forward ancestry/equality proof P <= T;
- PublicationIntent and publication WorkItem preparation;
- already-current observation;
- conditional ref mutation after Arm;
- publication capture, recovery, qualification, confirmation,
  non-application proof, and published-repository view materialization.
```

M7-B consumes the exact successor projection produced by M7-A.
M7-B may verify that projection and materialize its exact Git objects, but may
not derive another successor, modify commit metadata, select another parent, or
make successor identity depend on current remote state.

M7 proposes that bundle. M2 alone admits it authoritatively.

The WorkItem ownership distinction is exact:

```text
M5 → protocol-derived assurance WorkItems

M7 → repository-control publication WorkItem bound to one exact
     PublicationIntent
```

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

`initialRepositoryAuthority` and `publicationTarget` are `null` only before preflight and immutable after establishment. Their first non-null admission is legal only when the same `EstablishPreflightV1` retains the exact `RepositoryInspectionRef` and provenance closure from which those identities were established. There is no authoritative `StateRevision` in which the baseline exists but its already-sealed reconstructible repository basis does not.

interface CandidateRevisionRef {
  readonly candidateId: CandidateRevisionId;
  readonly runId: GateARunId;
  readonly ordinal: number;
  readonly parentCandidateId: CandidateRevisionId | null;
  readonly materialization: ArtifactRef;
  readonly semanticSubject: SemanticSubjectRef;
  readonly producedByRepairIntentId: RepairIntentId | null;
  readonly producedByAssuranceProjectionId:
    AssuranceRepositoryProjectionId | null;
}

interface SealedCandidateMaterializationRef {
  readonly runId: GateARunId;
  readonly parentCandidateId: CandidateRevisionId | null;
  readonly producedByRepairIntentId: RepairIntentId | null;
  readonly producedByAssuranceProjectionId:
    AssuranceRepositoryProjectionId | null;
  readonly materialization: ArtifactRef;
  readonly materializationEvidence: readonly ArtifactRef[];
}

interface AssuranceRepositoryProjectionEntryV1 {
  readonly repositoryPath: string;
  readonly content: ArtifactRef;
}

interface AssuranceRepositoryProjectionArtifactV1 {
  readonly schema: "gate-a-assurance-repository-projection.v1";
  readonly sourceCandidateId: CandidateRevisionId;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly entries: readonly AssuranceRepositoryProjectionEntryV1[];
}

interface AssuranceRepositoryProjectionRef {
  readonly projectionId: AssuranceRepositoryProjectionId;
  readonly runId: GateARunId;
  readonly sourceCandidateId: CandidateRevisionId;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly projection: ArtifactRef;
  readonly basisArtifacts: readonly ArtifactRef[];
}

interface RepositoryInspectionRef {
  readonly runId: GateARunId;
  readonly baselineAuthority: RepositoryAuthorityRef;
  readonly publicationTarget: RepositoryPublicationTargetRef;
  readonly baselineGitBasis: ArtifactRef;
  readonly sealedBaselineCandidate: SealedCandidateMaterializationRef;
  readonly evidence: readonly ArtifactRef[];
}

type ReviewCampaignProvenanceRef =
  | {
      readonly kind: "runner-produced";
      readonly originatingRunId: GateARunId;
      readonly candidateId: CandidateRevisionId;
      readonly repositoryAuthority: RepositoryAuthorityRef;
    }
  | {
      readonly kind: "repository-imported";
      readonly originatingRunId: null;
      readonly candidateId: null;
      readonly repositoryCommitSha: string;
    };

interface ReviewCampaignRef {
  readonly reviewCampaignId: ReviewCampaignId;
  readonly provenance: ReviewCampaignProvenanceRef;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
}

`ReviewCampaignId` is the same logical identity as hostile-review schema-5
`review_id`.

Every `ReviewCampaignId` must satisfy the schema-5 `review_id` lexical contract:

```text
^REVIEW-[A-Z0-9][A-Z0-9-]*$
```

For repository-imported campaigns:

```text
reviewCampaignId == exact validated record.review_id

provenance.repositoryCommitSha ==
    exact validated record.repository_commit
```

Do not derive an imported `ReviewCampaignId` from record SHA, record path,
candidate, repository observation, repository tree, or run. Do not infer a
`treeSha` for imported review evidence. The review-evidence contract supplies
`repository_commit`, not a complete `RepositoryAuthorityRef`.

For runner-produced campaigns, the logical slot is exactly:

```text
(runId, semanticSubject S, protocolBundle P)
```

The deterministic runner-created ID is:

```text
deriveReviewCampaignId(
    "review-campaign.v1",
    runId,
    semanticSubject.selector,
    semanticSubject.sha256,
    protocolBundle.protocolId,
    protocolBundle.sha256
)
```

`candidateId` is not an identity input.
`repositoryAuthority` is not an identity input.
`StateRevision` is not an identity input.
`timestamp` is not an identity input.

M0 final closure owns the collision-safe byte framing and exact deterministic
rendering of `deriveReviewCampaignId`, and the rendering must validate against
the schema-5 `review_id` lexical contract.

M2 must recompute runner-created `ReviewCampaignId` before admission.

The eventual hostile-review record produced for a runner-created campaign must
use:

```text
record.review_id == campaign.reviewCampaignId

record.repository_commit ==
    campaign.provenance.repositoryAuthority.commitSha
```

A campaign is never retargeted.

The same `ReviewCampaignId` with incompatible immutable campaign bindings fails
closed and may never be represented as a second campaign.

The canonical order for campaign sets is:

```text
ReviewCampaignId ascending by unsigned ASCII byte order
```

Every M3-produced `currentCampaigns` and `staleProtocolCampaigns` set must be
duplicate-free and in this order.

`currentReviewCampaignIds` and the current-campaign prefix of
`contributingReviewCampaignIds` must preserve that same canonical order.

No filesystem traversal order, introduction revision, record path, repository
commit, or record hash may define M3 currentness ordering.

interface GateAQualificationRef {
  readonly qualificationId: GateAQualificationId;
  readonly candidateId: CandidateRevisionId;
  readonly currentReviewCampaignIds: readonly ReviewCampaignId[];
  readonly contributingReviewCampaignIds: readonly ReviewCampaignId[];
  readonly validatorEvidence: readonly ArtifactRef[];
}
```

`RepositoryInspectionRef` is mechanical repository/Git observation material. It is not itself authoritative campaign state merely because M7 produced or persisted it.

The following bindings are normative:

```text
repositoryInspection.runId == exact GateARun

repositoryInspection.sealedBaselineCandidate.runId ==
    repositoryInspection.runId

repositoryInspection.sealedBaselineCandidate.parentCandidateId == null

repositoryInspection.sealedBaselineCandidate.producedByRepairIntentId == null

repositoryInspection.sealedBaselineCandidate.producedByAssuranceProjectionId == null

repositoryInspection.evidence is duplicate-free

baselineGitBasis exists and is intact

sealedBaselineCandidate.materialization exists and is intact

every sealedBaselineCandidate.materializationEvidence ArtifactRef exists and
is intact

every repositoryInspection.evidence ArtifactRef exists and is intact
```

The active
`NIB-M-GATE-A-REPOSITORY-CONTROL-MATERIALIZATION-CANDIDATE-CONSTRUCTION`
owns the exact M7-A representation and algorithms, while
`DC-GIT-CLI-GATE-A-REPOSITORY-CONTROL` owns the exact Git dependency
realization required before GREEN. The separate Dependency Contract does not
yet exist.

The exact `sealedBaselineCandidate` must be derived from the exact retained
baseline tree, not mutable working-tree bytes.

No mutable `repositoryPath`, worktree, index, remote-tracking ref, Git config,
or temporary repository is part of retained baseline authority.

`ReviewCampaignProvenanceRef` records the exact candidate/run/full repository
authority when the runner produced the campaign. Imported repository evidence
retains null runner-local identities and exactly the schema-5
`repository_commit`; it never fabricates an unavailable repository tree
identity or complete `RepositoryAuthorityRef`.

`currentReviewCampaignIds` is the complete ordered, duplicate-free set of structurally valid assurance-decomposition campaigns whose exact subject and protocol equal current `(S, P)`. Candidate, run, and repository provenance do not filter this set.

Malformed or referentially invalid review evidence is never silently filtered to obtain that set. Existing repository authority must first classify it as an integrity blocker, which prevents qualification.

`contributingReviewCampaignIds` is an ordered, duplicate-free superset of `currentReviewCampaignIds`. It also contains every stale-protocol campaign over the same `S` whose findings or current-protocol re-adjudications enter the mechanical Gate A qualification basis.

A stale-protocol campaign over the same `S` that has no finding or re-adjudication effect on the qualification basis is not included merely because it exists. A current campaign may never be omitted merely because another current campaign independently satisfies the minimum reviewer count.

`AssuranceRepositoryProjectionArtifactV1` is runner-owned canonical JSON under
the existing canonical runner JSON convention. Its `entries` array is non-empty,
strictly ordered by exact `repositoryPath` UTF-8 unsigned bytes, and
duplicate-free by path. Every content `ArtifactRef` is intact, has media type
`application/json`, and materializes one regular Git blob with mode `100644`.
No directory, symlink, or gitlink is created by assurance projection.

The exact allowed target set is:

```text
formal/reviews/<ReviewCampaignId>.json
formal/reviews/packets/*.json
formal/reviews/challenge-packets/*.json
formal/reviews/executions/*.json
formal/reviews/raw/*.json
formal/reviews/adjudications/*.json
formal/reviews/challenges/*.json
```

For a root runner-produced review record:

```text
repositoryPath ==
    "formal/reviews/" + campaign.reviewCampaignId + ".json"

parsed record.review_id == campaign.reviewCampaignId
parsed record.repository_commit ==
    campaign.provenance.repositoryAuthority.commitSha
```

These bindings reuse the accepted `ReviewCampaignId == review_id` and
`(runId, S, P)` identity rules. No competing campaign/record mapping exists.

Projection targets are explicitly forbidden under:

```text
formal/reviews/prompts/**
formal/reviews/protocols/**
formal/reviews/schemas/**
formal/reviews/meta-schemas/**
formal/reviews/review-evidence.schema.json
formal/reviews/review-protocol-bundle.schema.json
formal/verification.yaml
docs/**
```

Assurance projection cannot mutate judging authority.

Application is additive/idempotent against the exact source candidate:

```text
path absent
→ add exact content as mode 100644

path exists as mode 100644 with exact same bytes
→ idempotent equality permitted

path exists with different bytes
→ implementation/process/integrity failure

path exists with another mode/type
→ implementation/process/integrity failure
```

Projection never deletes, renames, changes mode, replaces different bytes,
fuzzy-matches, performs a 3-way merge, resolves conflicts, or rewrites JSON. At
least one entry must be absent from the source candidate; a complete no-op does
not justify another candidate.

A runner-produced root review record is projected only after M5 completes the
campaign/adjudication state represented by those exact bytes. Once
`formal/reviews/<ReviewCampaignId>.json` exists, later projection may encounter
only exact byte equality and may not replace it. Raw outputs, receipts,
challenge outputs, adjudication artifacts, and final review records remain
append-only at their repository paths. The exact M5-D final-record readiness
algorithm remains M5-D work.

M2 owns and recomputes projection identity exactly:

```text
projectionId =
deriveId(
    "assurance-repository-projection.v1",
    runId,
    sourceCandidateId,
    semanticSubject.sha256,
    protocolBundle.sha256,
    projection.sha256
)
```

`StateRevision`, ownership generation, timestamp, and successor candidate ID do
not participate.

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
  readonly realization:
    | "conditional-ref-update"
    | "already-current";
  readonly materialIdentityEvidence: readonly ArtifactRef[];
  readonly intent: PublicationIntentRef;
  readonly publicationObligation: ObligationRef;
  readonly publicationWorkItem: WorkItemRef;
}

`PreparedPublication.intent` is the exact `PublicationIntentRef` proposed for
the prepared transition. All of these bindings are required:

```text
PreparedPublication.intent.runId == PreparedPublication.runId.

PreparedPublication.intent.candidateId == PreparedPublication.candidateId.

PreparedPublication.intent.qualificationId ==
PreparedPublication.qualificationId.

PreparedPublication.intent.transition == PreparedPublication.transition.

`realization == "conditional-ref-update"` iff
`transition.predecessor != transition.successor`.

`realization == "already-current"` iff
`transition.predecessor == transition.successor`.

M1 does not choose `realization`; M7 derives it mechanically.

PreparedPublication.publicationObligation belongs to the same GateARun and
candidate as the intent.

PreparedPublication.publicationObligation.reviewCampaignId == null.

PreparedPublication.publicationWorkItem belongs to the same GateARun and
candidate as the intent.

PreparedPublication.publicationWorkItem.reviewCampaignId == null.

PreparedPublication.publicationWorkItem.executor == "repository-control".

PreparedPublication.publicationWorkItem.sourceObligationIds contains exactly
one item and that item equals
PreparedPublication.publicationObligation.obligationId.
```

The publication WorkItem operation must bind the exact `PublicationIntent`.

Its exact runner-owned operation schema and pure binding extractor belong to
the future M7 NIB-M and must be closed before GREEN.

M1 may coordinate this bundle but may not invent or reinterpret its WorkItem,
obligation, transition, or repository-domain meaning.

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

interface PublicationAlreadyCurrentObservationRef {
  readonly publicationIntentId: PublicationIntentId;
  readonly candidateId: CandidateRevisionId;
  readonly target: RepositoryPublicationTargetRef;
  readonly observedAuthority: RepositoryAuthorityRef;
  readonly evidence: readonly ArtifactRef[];
}

interface PublicationNonApplicationRef {
  readonly schema: "gate-a-publication-non-application.v1";
  readonly publicationIntentId: PublicationIntentId;
  readonly candidateId: CandidateRevisionId;
  readonly executionId: ExecutionId;
  readonly workItemId: WorkItemId;
  readonly dispatchIntent: ArtifactRef;
  readonly attemptResult: ArtifactRef;
  readonly proof: ArtifactRef;
  readonly basisArtifacts: readonly ArtifactRef[];
}
```

`RepositoryPublicationTargetRef` is the exact durable remote mutation target. `repositoryIdentity` identifies the repository independently of a local checkout, `remoteEndpoint` is the normalized credential-free publication endpoint, and `refName` is the fully qualified Git ref name. Credentials and credential-bearing URLs are invalid target identities.

A publication successor is an exact repository-authority identity, not merely a Git tree identity.

Before any remote publication mutation, M7 must prepare the exact immutable successor repository object locally, expose both its exact commit identity and exact tree identity through `RepositoryAuthorityRef`, and mechanically prove that the predecessor commit is an ancestor-or-equal to the successor commit for the exact target. The initial runner authorizes only the `fast-forward` relationship. For Gate A publication construction, `"fast-forward"` requires predecessor to be ancestor-or-equal to successor: when `predecessor != successor`, the realization is `conditional-ref-update`; when `predecessor == successor`, the realization is `already-current`. CAS alone remains insufficient; ancestry/equality evidence remains required.

A `PublicationIntentRef` that lacks the exact target, contains only a tree SHA, or lacks valid ancestry evidence is invalid. A compare-and-swap from `A` to an unrelated `C` is prohibited even when the target still equals `A`.

A repository path or local remote name is never sufficient as durable publication-target or immutable historical identity by itself.

`PublishedRepositoryViewRef` is an isolated local materialization of the exact confirmed publication successor.

Its `target` must equal the target in the referenced `PublicationConfirmationRef`.

Its `authority` must equal that confirmation's exact transition successor by both commit SHA and tree SHA.

Its `repositoryPath` is an operational location only. The path never substitutes for the bound target, authority, candidate, confirmation, or materialization evidence.

`PublicationAlreadyCurrentObservationRef.evidence` is duplicate-free and every
referenced artifact is intact. The future M7 NIB-M defines the exact read-only
observation artifact schema and Git dependency interpretation.

`PublicationNonApplicationRef.basisArtifacts` is duplicate-free, its `proof` is
not duplicated inside `basisArtifacts`, and all referenced artifacts are intact.
Its normative meaning is exactly:

```text
The exact armed publication Execution terminated with direct captured material.

M7, under its accepted repository/Git contract, positively established that the
exact target-ref mutation represented by that Execution's dispatch intent was
not applied.
```

This fact does not mean:

```text
the Execution never occurred
the executor boundary was never crossed
PROVEN-NOT-EXECUTED
a retry is authorized
the publication obligation is satisfied
the target still equals the old predecessor
a new PublicationIntent already exists
```

`PublicationNonApplicationRef` v1 is produced only from a direct terminal M7
capture. For authoritative provenance, "direct terminal" means that the exact
`CapturedExecutionResult` was introduced for the exact Execution by
`AdmitExecutionOutcomeV1` with `outcome.kind = "captured"`. A captured payload
introduced by `AdmitExecutionRecoveryV1` is recovery-derived even when its
payload is otherwise identical. Recovery-derived captured material may support
executed-publication qualification and confirmation, but it may never produce a
`not-applied` result or a `PublicationNonApplicationRef`.

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

For every runner-produced ReviewCampaign, after campaign admission M5 obtains
protocol retry policy only from the exact authoritative
`ReviewCampaignPrerequisiteBasisRefV1.retryPolicy` retained for that campaign.

M5 must not:

```text
reread current P
read protocol files from mutable repository state
rerun M6 review-authority projection
rerun M3 reviewer prerequisites
hardcode protocol-v6 retry booleans
infer protocol retry authorization solely from M6 classification
```

The admissibility authorities remain separate:

```text
protocol-side retry admissibility
→ B.retryPolicy

runner hard-limit admissibility
→ exact authoritative Execution history
  + accepted M2 runner limits
```

`CognitiveAttemptValidationResult` establishes the exact attempt classification.
It is not protocol retry policy. Both the exact attempt classification and the
applicable protocol-side policy fact are required when applicable.

Provider/transport retries internal to one Pi M4 adapter call are governed by
the Pi M4 Dependency Contract and do not use
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
  readonly repositoryInspection: RepositoryInspectionRef | null;
  readonly preflightSemanticSubject: SemanticSubjectRef | null;
  readonly preflightProtocolBundle: ProtocolBundleRef | null;
  readonly preflightSubjectProjection: ArtifactRef | null;
  readonly preflightReviewAuthorityProjection: ArtifactRef | null;
  readonly stateRevision: StateRevision;
  readonly candidates: readonly CandidateRevisionRef[];
  readonly currentCandidate: CandidateRevisionRef | null;
  readonly reviewCampaigns: readonly ReviewCampaignRef[];
  readonly reviewCampaignPrerequisiteBases:
    readonly ReviewCampaignPrerequisiteBasisRefV1[];
  readonly obligations: readonly ObligationRef[];
  readonly obligationDispositions: readonly ObligationDispositionRef[];
  readonly workItems: readonly WorkItemRef[];
  readonly executions: readonly ExecutionRef[];
  readonly executionProgressionSupersessions:
    readonly ExecutionProgressionSupersessionRef[];
  readonly executionRetryAuthorizations: readonly ExecutionRetryAuthorizationRef[];
  readonly capturedExecutionResults: readonly CapturedExecutionResult[];
  readonly technicalExecutionFailures: readonly TechnicalExecutionFailure[];
  readonly publicationNonApplications: readonly PublicationNonApplicationRef[];
  readonly unresolvedExecutions: readonly UnresolvedExecutionRecoveryRef[];
  readonly evidence: readonly EvidenceRef[];
  readonly findings: readonly FindingRef[];
  readonly adjudications: readonly AdjudicationRef[];
  readonly reAdjudications: readonly ReAdjudicationRef[];
  readonly repairIntents: readonly RepairIntentRef[];
  readonly assuranceRepositoryProjections:
    readonly AssuranceRepositoryProjectionRef[];
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

`repositoryInspection`, `preflightSemanticSubject`,
`preflightProtocolBundle`, `preflightSubjectProjection`, and
`preflightReviewAuthorityProjection` are derived snapshot projections of
authoritative preflight history.

Before one `EstablishPreflightV1` is admitted:

```text
repositoryInspection == null
preflightSemanticSubject == null
preflightProtocolBundle == null
preflightSubjectProjection == null
preflightReviewAuthorityProjection == null
run.initialRepositoryAuthority == null
run.publicationTarget == null
```

After the unique `EstablishPreflightV1` is admitted:

```text
repositoryInspection ==
    exact retained mutation.repositoryInspection

preflightSemanticSubject ==
    exact retained mutation.baselineSemanticSubject

preflightProtocolBundle ==
    exact retained mutation.protocolBundle

preflightSubjectProjection ==
    exact retained mutation.subjectProjection

preflightReviewAuthorityProjection ==
    exact retained mutation.reviewAuthorityProjection
```

All four preflight projected values become non-null together and never change.
They are reconstructed only from the exact retained unique
`EstablishPreflightV1`.

Never reconstruct them from:

```text
current repository
candidate files
CAS guesses
current Git state
another M6 invocation
normalized database columns without exact mutation provenance
```

The projected `RepositoryInspectionRef` is likewise never reconstructed from
`repositoryPath`, baseline-Git-basis bytes, evidence arrays, current Git
configuration, current repository state, or commit/tree identity alone.

M2 projects the exact retained values from authoritative history.

The projections are immutable for the lifetime of the `GateARun` because
`EstablishPreflightV1` is admitted at most once.

For `reviewCampaignPrerequisiteBases`, require exactly:

```text
one and only one basis exists for every runner-produced ReviewCampaign

no basis exists for repository-imported ReviewCampaigns
```

Ordering is the exact relative order of `snapshot.reviewCampaigns` after
filtering to `provenance.kind == "runner-produced"`. Do not invent another
independent ordering.

`reviewCampaignPrerequisiteBases` is reconstructed only from exact retained
`EstablishReviewCampaignBundleV1` mutation history.

It is never reconstructed from:

```text
current P
protocol files
current reviewer registry
current candidate
a new M3 invocation
a new M6 invocation
GateAReviewAuthorityMechanicalProjectionV1 re-execution
WorkItem operation
CognitiveAttemptValidationResult
preflight re-execution
Pi configuration
environment
repository files
current repository
current Git state
```

The exact retained mutation is authoritative for what acquisition basis was
admitted for that campaign. Its exact `retryPolicy` is projected unchanged,
without sorting, rewriting, defaulting, or reinterpretation.

Require exact equivalence:

```text
snapshot.repositoryInspection == null
iff
snapshot.preflightSemanticSubject == null
AND
snapshot.preflightProtocolBundle == null
AND
snapshot.preflightSubjectProjection == null
AND
snapshot.preflightReviewAuthorityProjection == null
AND
snapshot.run.initialRepositoryAuthority == null
AND
snapshot.run.publicationTarget == null
```

Candidate lineage is projected exactly as:

```text
candidates =
    all admitted CandidateRevisionRef values
    ordered by ordinal ascending

candidate ordinals are contiguous from 0

currentCandidate == null
iff
candidates is empty

otherwise:
currentCandidate == candidates[candidates.length - 1]
```

Any retained state violating these requirements is `INTEGRITY_FAILURE`.

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
type CampaignAuthorityOperationalCauseRefV1 =
  NonRecoveryOperationalCauseRefV1 & {
    readonly producer: "campaign-authority";
  };

type GateACampaignAuthorityOperationalCauseV1 =
  | PreflightReviewAuthorityInvalidCauseV1
  | CurrentCandidateReviewAuthorityInvalidCauseV1
  | ReviewerPrerequisitesUnavailableCauseV1;

interface PreflightReviewAuthorityInvalidCauseV1 {
  readonly schema:
    "gate-a-campaign-authority-operational-cause.v1";
  readonly kind:
    "preflight-review-authority-invalid";
  readonly candidateMaterialization: ArtifactRef;
  readonly reviewAuthorityProjection: ArtifactRef;
}

interface CurrentCandidateReviewAuthorityInvalidCauseV1 {
  readonly schema:
    "gate-a-campaign-authority-operational-cause.v1";
  readonly kind:
    "current-candidate-review-authority-invalid";
  readonly candidateId: CandidateRevisionId;
  readonly candidateMaterialization: ArtifactRef;
  readonly reviewAuthorityProjection: ArtifactRef;
}

interface ReviewerPrerequisitesUnavailableCauseV1 {
  readonly schema:
    "gate-a-campaign-authority-operational-cause.v1";
  readonly kind:
    "reviewer-prerequisites-unavailable";
  readonly candidateId: CandidateRevisionId;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly minimumIndependentReviewers: number;
  readonly qualifyingReviewerProfileIds: readonly string[];
  readonly maximumStaticallyPossibleIndependentReviewers: number;
  readonly reviewerAcquisitionProfileIds: readonly string[];
  readonly reviewAuthorityProjection: ArtifactRef;
}

interface PreflightRequest {
  readonly runId: GateARunId;
  readonly repositoryInspection: RepositoryInspectionRef;
  readonly subjectDerivation: CandidateSubjectMechanicalDerivationResult;
  readonly reviewAuthority:
    CandidateReviewAuthorityMechanicalProjectionResult;
}

type PreflightResolution =
  | {
      readonly kind: "established";
      readonly baselineAuthority: RepositoryAuthorityRef;
      readonly publicationTarget: RepositoryPublicationTargetRef;
      readonly baselineSemanticSubject: SemanticSubjectRef;
      readonly protocolBundle: ProtocolBundleRef;
      readonly subjectProjection: ArtifactRef;
      readonly reviewAuthorityProjection: ArtifactRef;
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly kind: "blocked";
      readonly cause: CampaignAuthorityOperationalCauseRefV1;
    };

interface ReviewContext {
  readonly runId: GateARunId;
  readonly candidate: CandidateRevisionRef;
  readonly campaign: ReviewCampaignRef;
}

interface RepositoryReviewObservationV1 {
  readonly reviewCampaignId: ReviewCampaignId;
  readonly sourceRecord: ArtifactRef;
  readonly repositoryCommitSha: string;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly referencedArtifacts: readonly ArtifactRef[];
}

interface GateACampaignAuthorityEvaluationV1 {
  readonly schema: "gate-a-campaign-authority-evaluation.v1";
  readonly runId: GateARunId;
  readonly stateRevision: StateRevision;
  readonly qualificationCandidateId: CandidateRevisionId;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly reviewAuthorityProjection: ArtifactRef;
  readonly repositoryReviewObservations:
    readonly RepositoryReviewObservationV1[];
  readonly currentReviewCampaignIds: readonly ReviewCampaignId[];
  readonly staleProtocolReviewCampaignIds: readonly ReviewCampaignId[];
}

interface GateAEvaluationContext {
  readonly runId: GateARunId;
  readonly qualificationCandidate: CandidateRevisionRef;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly currentCampaigns: readonly ReviewCampaignRef[];
  readonly staleProtocolCampaigns: readonly ReviewCampaignRef[];
  readonly authorityEvaluation: ArtifactRef;
}

interface ReviewerPrerequisiteRequest {
  readonly candidate: CandidateRevisionRef;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly reviewAuthority:
    Extract<
      CandidateReviewAuthorityMechanicalProjectionResult,
      { readonly kind: "established" }
    >;
}

type ReviewerPrerequisiteResolution =
  | {
      readonly kind: "established";
      readonly minimumIndependentReviewers: number;
      readonly acquisitionMode: "minimum-effective-independent-v1";
      readonly retryPolicy:
        GateACognitiveRetryPolicyMechanicalFactV1;
      readonly qualifyingReviewerProfileIds: readonly string[];
      readonly reviewerAcquisitionCandidates:
        readonly GateAReviewerAcquisitionCandidateV1[];

      readonly initialReviewerExecutionInputs:
        InitialReviewerExecutionInputsRefV1;

      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly kind: "blocked";
      readonly blockingObligation: ObligationRef;
      readonly cause: CampaignAuthorityOperationalCauseRefV1;
    };

interface ReviewCurrentnessRequest {
  readonly runId: GateARunId;
  readonly stateRevision: StateRevision;
  readonly candidate: CandidateRevisionRef;
  readonly candidateLineage: readonly CandidateRevisionRef[];
  readonly registeredCampaigns: readonly ReviewCampaignRef[];
  readonly reviewAuthority:
    CandidateReviewAuthorityMechanicalProjectionResult;
}

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
      readonly blockingObligation: ObligationRef;
      readonly cause: CampaignAuthorityOperationalCauseRefV1;
    };
```

M3 may return only cause references whose:

```text
producer == "campaign-authority"
```

M3 does not return an already-materialized `OperationalBlocker`. Under current
M3 semantics each blocked result has exactly one producer cause; do not add a
cause or blocker array.

M3 owns the campaign-authority cause schema, cause-domain meaning, exact causal
fields, runtime validation, basis evidence, and lawful resolution contracts.
M3 never constructs `OperationalBlocker`, `BlockerId`, Operator Action Request,
operator-resolution identity, or operator-resolution state effects. Every M3
operational blocker is materialized by M8-B from exact M3-owned
`NonRecoveryOperationalCauseRefV1` material.

Every M3 `causeDescriptor` is the exact immutable canonical serialization of
one `GateACampaignAuthorityOperationalCauseV1` value.

Every M3 operational cause descriptor is:

```text
runner-owned
canonical runner JSON
UTF-8
application/json
causeDescriptor.repositoryPath = null
sealed through CampaignArtifactStore
verified after sealing
```

Use the existing runner canonical JSON contract. M3 does not own `BlockerId` or
Operator Action Request serialization. The future M3 NIB-M will close the exact
implementation algorithm.

Do not add any of these fields to an M3 cause descriptor:

```text
StateRevision
RunnerSessionId
ownershipGeneration
timestamp
process ID
temporary path
repositoryPath
retry counter
random identity
mutable environment state
credential value
diagnostic text
```

M3 has exactly three campaign-authority operational cause kinds in this
revision:

```text
preflight-review-authority-invalid
current-candidate-review-authority-invalid
reviewer-prerequisites-unavailable
```

For `preflight-review-authority-invalid`, require exactly:

```text
cause.candidateMaterialization ==
    reviewAuthority.candidateMaterialization

cause.reviewAuthorityProjection ==
    reviewAuthority.projection

basisArtifacts =
ordered duplicate-free first-occurrence sequence:
[
    reviewAuthority.projection,
    reviewAuthority.diagnostics,
    ...reviewAuthority.evidence
]

resolutionContracts =
[
    {
        kind: "request-operational-recheck"
    }
]
```

Diagnostics remain provenance/evidence only and are not part of cause identity.

`preflight-review-authority-invalid` is recheckable because:

```text
no EstablishPreflightV1 has been admitted
baseline authority is still null
C0 does not exist
the root preflight obligation remains outstanding
a later invocation may inspect a newly corrected mutable repository state
```

After accepted `request-operational-recheck` disposition:

```text
M1 performs a fresh M7 repository inspection
→ fresh sealed baseline candidate
→ fresh M6 subject/review-authority projections
→ fresh M3 preflight
```

M1 does not reuse the prior mutable repository observation.

For `current-candidate-review-authority-invalid`, require exactly:

```text
cause.candidateId ==
    exact current candidate.candidateId

cause.candidateMaterialization ==
    exact current candidate.materialization

cause.reviewAuthorityProjection ==
    reviewAuthority.projection

basisArtifacts =
ordered duplicate-free first-occurrence sequence:
[
    reviewAuthority.projection,
    reviewAuthority.diagnostics,
    ...reviewAuthority.evidence
]

resolutionContracts = []
```

Diagnostics remain provenance/evidence only and are not part of cause identity.

`current-candidate-review-authority-invalid` has no same-run resolution because:

```text
CandidateRevision is already authoritative and immutable
M6 is bound to exact candidate.materialization
rereading or modifying an external repository cannot alter candidate authority
rechecking the same immutable candidate cannot lawfully substitute new bytes
```

The current `GateARun` therefore remains operationally blocked. Any correction
that changes repository authority must be materialized through the repository
authority mechanism and observed by a later `GateARun`. Do not invent candidate
mutation or rebaseline-in-place.

For `reviewer-prerequisites-unavailable`, require exactly:

```text
cause.candidateId ==
    request.candidate.candidateId

cause.semanticSubject ==
    request.semanticSubject

cause.protocolBundle ==
    request.protocolBundle

cause.minimumIndependentReviewers ==
    request.reviewAuthority.minimumIndependentReviewers

cause.reviewAuthorityProjection ==
    request.reviewAuthority.projection

cause.qualifyingReviewerProfileIds ==
    exact complete canonical set of profile IDs that satisfy the accepted
    statically checkable reviewer-profile qualification rules, even when that
    complete set is insufficient to satisfy the applicable prerequisite/minimum

cause.qualifyingReviewerProfileIds ordered by unsigned ASCII ascending

basisArtifacts =
ordered duplicate-free first-occurrence sequence:
[
    request.reviewAuthority.projection,
    ...request.reviewAuthority.evidence
]

resolutionContracts = []
```

`reviewer-prerequisites-unavailable` has no same-run resolution contract. The
current protocol `P` and its reviewer-profile registry are candidate-bound
authority. A profile-registry change requires a new protocol snapshot and
therefore a new `P`. The current `GateARun` may not mutate `P` or its candidate
authority in place. The blocker therefore remains outstanding in that run. Do
not emit `request-operational-recheck` for this cause.

For an M3 cause reference:

```text
resolutionContracts = []
```

means:

```text
the operational condition legitimately requires external operator action,
but the current GateARun exposes no accepted same-run operator-resolution
transition that can establish the missing domain fact.
```

Such a blocker remains `OPERATOR-ACTION-REQUIRED` while outstanding. It is not:

```text
DECISION-REQUIRED
implementation failure
automatic retry permission
request-operational-recheck permission
permission to mutate candidate/P in place
```

No `GateAOperatorResolutionArtifactV1` can validly target an Operator Action
Request whose `resolutionContracts` array is empty.

M3 owns exactly two candidate-scoped blocking-obligation meanings:

```text
current-review-authority
reviewer-prerequisites
```

These are campaign-authority obligations. They are not protocol-derived M5
obligations, the root M0 preflight obligation, or M7 publication obligations.
The future M3 NIB-M owns the exact immutable runner-owned obligation-definition
artifact payloads for these two meanings. Each definition `ArtifactRef` must be
immutable, intact, runtime-valid, and content-addressed.

For a post-preflight currentness invalidity, M3 constructs exactly one
`ObligationRef` with:

```text
runId == exact GateARun
candidateId == exact current candidate.candidateId
reviewCampaignId == null
definition == exact M3 current-review-authority obligation definition
```

Identity:

```text
obligationId =
deriveId(
    "campaign-authority-current-review-authority-obligation.v1",
    runId,
    candidateId,
    definition.sha256
)
```

This obligation means exactly:

```text
establish a mechanically valid complete hostile-review authority projection
for this exact authoritative candidate before safe Gate A campaign progression
can continue
```

Do not put M6 diagnostics or `StateRevision` into the identity.

For reviewer-prerequisite failure, M3 constructs exactly one `ObligationRef`
with:

```text
runId == exact GateARun
candidateId == exact candidate.candidateId
reviewCampaignId == null
definition == exact M3 reviewer-prerequisites obligation definition
```

Identity:

```text
obligationId =
deriveId(
    "campaign-authority-reviewer-prerequisites-obligation.v1",
    runId,
    candidateId,
    semanticSubject.selector,
    semanticSubject.sha256,
    protocolBundle.protocolId,
    protocolBundle.sha256,
    definition.sha256
)
```

This obligation means exactly:

```text
establish sufficient protocol-authorized reviewer prerequisites for creation
of a ReviewCampaign over this exact candidate, S, and P
```

Do not create a `ReviewCampaignId` merely to identify this obligation.
`reviewCampaignId` remains `null`.

The `current-review-authority` blocking obligation and the
`reviewer-prerequisites` blocking obligation have no same-run automatic
satisfaction path in this construction revision. They remain outstanding in the
blocked `GateARun`. This does not create a persisted `campaignCurrentness` field
and does not alter the rule that ordinary M3 currentness is freshly derived from
exact current authority and campaign history. These obligations exist only when
the corresponding blocking condition has actually been established.

Require these exact blocked-result mappings:

```text
PreflightRequest.reviewAuthority.kind == invalid
→ PreflightResolution.kind == blocked
→ cause.kind == preflight-review-authority-invalid

ReviewCurrentnessRequest.reviewAuthority.kind == invalid
→ ReviewCurrentnessResolution.kind == blocked
→ blockingObligation == exact current-review-authority obligation
→ cause.kind == current-candidate-review-authority-invalid

ReviewerPrerequisiteRequest cannot satisfy exact applicable prerequisites
→ ReviewerPrerequisiteResolution.kind == blocked
→ blockingObligation == exact reviewer-prerequisites obligation
→ cause.kind == reviewer-prerequisites-unavailable
```

No other M3 cause kind exists in this revision.

Do not convert any of these into operational causes:

```text
malformed M3 request
candidate/run binding contradiction
candidate-lineage contradiction
registered campaign duplicate with incompatible immutable payload
same ReviewCampaignId conflict
corrupt/missing ArtifactRef required to trust the input
CampaignArtifactStore integrity failure
canonical serializer contradiction
impossible M6 result under its declared contract
untrustworthy Python authority
subject-derivation failure
```

These remain outside normal M3 result unions as applicable implementation,
process, integrity, dependency, or invocation failures.

For preflight `kind = established`, require exactly:

```text
subjectDerivation.candidateMaterialization ==
    repositoryInspection.sealedBaselineCandidate.materialization

reviewAuthority.kind == established

reviewAuthority.candidateMaterialization ==
    repositoryInspection.sealedBaselineCandidate.materialization

baselineAuthority ==
    repositoryInspection.baselineAuthority

publicationTarget ==
    repositoryInspection.publicationTarget

baselineSemanticSubject ==
    subjectDerivation.semanticSubject

protocolBundle ==
    reviewAuthority.protocolBundle

subjectProjection ==
    subjectDerivation.projection

reviewAuthorityProjection ==
    reviewAuthority.projection
```

`evidence` remains duplicate-free and intact. Do not duplicate
`subjectProjection` or `reviewAuthorityProjection` inside `evidence`.

If `reviewAuthority.kind == "invalid"`, `PreflightResolution.kind == blocked`
using the exact M3-owned operational cause construction rules above. M8-B alone
materializes the blocker. No campaign is created, baseline authority is not
admitted, and the root preflight obligation remains outstanding.

M7 observes and mechanically captures repository/Git facts.

M3 interprets the exact immutable `RepositoryInspectionRef` and exact M6
mechanical projections under accepted campaign/repository authority.

M3 does not establish baseline authority or publication target by rereading a
mutable repository path. M3 does not invoke Python authority or derive `S`.

M2 alone makes the resulting preflight facts authoritative.

A complete `CandidateRevisionRef` is constructed only after M7 has returned the
sealed materialization and M6 has returned the exact mechanically derived
semantic subject. M2 then validates and registers that complete candidate
identity.

For `ReviewCurrentnessRequest`, require exactly:

```text
candidate.runId == runId

candidateLineage is duplicate-free
candidateLineage ordered by ordinal ascending
candidateLineage ordinals contiguous from 0
candidate == final candidateLineage item

every candidateLineage item belongs to runId

registeredCampaigns contains the complete GateARunSnapshot.reviewCampaigns
sequence

reviewAuthority.candidateMaterialization ==
    candidate.materialization
```

`reviewAuthority.kind == invalid` produces
`ReviewCurrentnessResolution.kind == blocked`. M3 does not use partial review
records.

For every established mechanically projected repository review, M3 first
constructs one exact canonical observation satisfying:

```text
observation.reviewCampaignId == review.reviewId
observation.sourceRecord == review.sourceRecord
observation.repositoryCommitSha == review.repositoryCommitSha
observation.semanticSubject == review.semanticSubject
observation.protocolBundle == review.protocolBundle
observation.referencedArtifacts == review.referencedArtifacts
```

M3 does not add, remove, reorder, or reread closure artifacts. It does not
reinterpret M6 mechanical validity. The exact observations remain solely in
`GateACampaignAuthorityEvaluationV1.repositoryReviewObservations`.

If no registered campaign has its `reviewId`, M3 constructs exactly:

```ts
{
  reviewCampaignId: review.reviewId,
  provenance: {
    kind: "repository-imported",
    originatingRunId: null,
    candidateId: null,
    repositoryCommitSha: review.repositoryCommitSha
  },
  semanticSubject: review.semanticSubject,
  protocolBundle: review.protocolBundle
}
```

If a registered campaign has the same `ReviewCampaignId`, require compatible
immutable bindings. For an existing runner-produced campaign require:

```text
existing.semanticSubject == review.semanticSubject
existing.protocolBundle == review.protocolBundle
existing.provenance.repositoryAuthority.commitSha ==
    review.repositoryCommitSha
```

For an existing repository-imported campaign require:

```text
existing.semanticSubject == review.semanticSubject
existing.protocolBundle == review.protocolBundle
existing.provenance.repositoryCommitSha ==
    review.repositoryCommitSha
```

Then reuse the existing campaign identity. Do not create an imported duplicate.
Any same-ID incompatibility fails closed. Never retarget the existing campaign,
create a second campaign for the same `review_id`, tie-break by record
path/hash/order, or fabricate repository tree identity.

For an established review-authority projection, define the campaign universe as
all registered `ReviewCampaignRef` values plus every newly observed mechanically
valid repository `ReviewCampaignRef`. Merge only by exact `ReviewCampaignId`.
Exact duplicate identity plus exact compatible payload is one logical campaign.
The same identity plus incompatible immutable payload fails closed.

Define:

```text
S = request.candidate.semanticSubject
P = request.reviewAuthority.protocolBundle

currentCampaigns =
    every campaign in campaign universe where:
        campaign.semanticSubject == S
        AND
        campaign.protocolBundle == P

staleProtocolCampaigns =
    every campaign in campaign universe where:
        campaign.semanticSubject == S
        AND
        campaign.protocolBundle != P
```

Candidate, run, and repository provenance do not filter either set. Sort both by
`ReviewCampaignId` unsigned ASCII ascending.

Apply exact precedence:

```text
if currentCampaigns is non-empty:
    return current

else if staleProtocolCampaigns is non-empty:
    return campaign-required(PROTOCOL-CHANGED)

else if candidate.ordinal > 0
     AND immediate parent candidate semanticSubject != S:
    return campaign-required(SUBJECT-CHANGED)

else:
    return campaign-required(INITIAL)
```

The immediate parent is exactly:

```text
candidateLineage[candidate.ordinal - 1]
```

No historical repository campaign over another subject may substitute for this
parent comparison.

`INITIAL` means the required first campaign for the currently applicable exact
subject/protocol when neither a current campaign nor a same-subject stale-P
campaign explains the requirement.

`PROTOCOL-CHANGED` takes precedence over `SUBJECT-CHANGED` when same-subject
stale-P campaigns exist, because current-P campaign creation and stale-P
re-adjudication are required.

CandidateRevision change alone never produces campaign-required when a current
exact `(S, P)` campaign exists.

M3 canonical-serializes and seals exactly one
`GateACampaignAuthorityEvaluationV1` artifact for every successful `current`
resolution. Repository observations are ordered by `ReviewCampaignId` unsigned
ASCII ascending. The witness is runner-owned immutable provenance.

Require exact authority-evaluation bindings:

```text
authorityEvaluation.runId == context.runId

authorityEvaluation.stateRevision == request.stateRevision

authorityEvaluation.reviewAuthorityProjection ==
    request.reviewAuthority.projection

authorityEvaluation.qualificationCandidateId ==
    context.qualificationCandidate.candidateId

authorityEvaluation.semanticSubject ==
    context.semanticSubject

authorityEvaluation.protocolBundle ==
    context.protocolBundle

authorityEvaluation.currentReviewCampaignIds ==
    context.currentCampaigns.map(reviewCampaignId)

authorityEvaluation.staleProtocolReviewCampaignIds ==
    context.staleProtocolCampaigns.map(reviewCampaignId)
```

A `ReviewContext` used for new execution must use the exact production candidate
recorded by its runner-produced campaign provenance. Reusing a current campaign
to qualify a later same-`(S, P)` candidate does not create new executions under
rewritten provenance.

For every `campaign-required` result, M1 must obtain
`ReviewerPrerequisiteResolution.kind = "established"` before committing a new
ReviewCampaign. A blocked prerequisite creates no campaign and projects
`OPERATOR-ACTION-REQUIRED` after the blockers are committed.

Reviewer-prerequisite requests require exactly:

```text
reviewAuthority.candidateMaterialization ==
    candidate.materialization

reviewAuthority.protocolBundle ==
    protocolBundle

candidate.semanticSubject ==
    semanticSubject
```

M3 validates and preserves the exact
`reviewAuthority.initialReviewerExecutionInputs` and
`reviewAuthority.retryPolicy`. It requires the retry policy to runtime-validate
as `GateACognitiveRetryPolicyMechanicalFactV1`, both role arrays to be
duplicate-free, and every role value to belong to `CognitiveExecutionRole`.
Any structural contradiction is `MECHANICAL-AUTHORITY-CONTRACT-FAILURE`.
It returns exactly:

```text
retryPolicy:
    reviewAuthority.retryPolicy

initialReviewerExecutionInputs:
    reviewAuthority.initialReviewerExecutionInputs
```

M3 must not construct the prompt, construct the packet, reread P, reopen the
protocol bundle path, reread the repository, invoke Python, apply retry rules,
decide retry admissibility, compare against hardcoded protocol-v6 values, or
add/remove/reorder either retry-policy role array. It performs no transformation
of either exact immutable byte carrier, repository-path binding, or retry-policy
fact.

M6 mechanically projects `reviewerAcquisition` exactly from validated current P.
M6 does not choose acquisition order, select profiles, or use finding content.

M3 static provider-reported qualification remains protocol-only. M3 does not
inspect Pi, Dependency Contract capability, provider runtime support, or
provider documentation. Therefore:

```text
protocol profile qualification
!=
execution-realization capability
```

M3 gains no realization-conformance ownership.

For `kind = established`, `qualifyingReviewerProfileIds` must be the complete
set of protocol-registered profiles that satisfy every accepted
reviewer/profile prerequisite for the required Gate A review class. M3 may not
choose an arbitrary subset. The order is `profileId` unsigned ASCII ascending.

`reviewerAcquisitionCandidates` traverses exact P `profileOrder`, filtered to
the complete statically qualifying set. It is never lexically resorted. A
provider-reported candidate has `staticallyKnownEffectiveIdentity = null`. A
pinned immutable candidate has the exact known `{ provider, modelVersion:
requestModel }` identity.

M3 computes the optimistic static capacity as the count of distinct known
pinned effective identities plus the number of qualifying provider-reported
profiles. It never pre-collapses provider-reported profiles. If that capacity is
less than `minimumIndependentReviewers`, the result is `blocked` with the exact
candidate-scoped blocking obligation, the extended exact cause fields, and
`resolutionContracts = []`. No ReviewCampaign is created.

M1 selects the first deterministic acquisition-round candidates from this exact
M3 basis. M5 owns protocol-derived assurance `ObligationRef` / `WorkItemRef`
construction for both first-round selected reviewers and later-round selected
reviewers. M5 alone selects later acquisition rounds from qualified receipt
identities. Registry membership never means execute-all authority. Selection
and expansion depend only on P, the policy minimum, static profile facts,
profiles already selected, qualified receipt existence, resolved identities,
and statically known pinned identities. Finding content, favorability, latency,
scheduling, and completion order are never inputs.

For any runner-produced ReviewCampaign whose acquisition state M5 must derive,
M5 obtains the exact `ReviewCampaignPrerequisiteBasisRefV1` from
`snapshot.reviewCampaignPrerequisiteBases`.

M5 must not rerun M3 or reconstruct the acquisition candidate universe from
current P.

Later acquisition rounds consume exactly the immutable candidate sequence in
that retained basis together with already-admitted qualified receipt identities
and other exact ADR-053 inputs.

`AssuranceDerivationRequest` itself remains unchanged because it already carries
the exact `GateARunSnapshot`.

Every cognitive WorkItem representing one selected reviewer acquisition
candidate must bind exactly one `GateAReviewerAcquisitionCandidateV1` selected
from the exact `ReviewCampaignPrerequisiteBasisRefV1` governing its
ReviewCampaign.

The executor-owned M4 operation must retain that exact candidate.

WorkItem reviewer-profile binding is exactly:

```text
operation.reviewerProfileId ==
operation.reviewerAcquisitionCandidate.profileId
```

Selection and WorkItem-construction ownership remain exactly:

```text
M1
→ selects first acquisition round candidates only

M5
→ owns protocol-derived assurance ObligationRef / WorkItemRef construction
  for BOTH:
    first-round selected reviewers
    later-round selected reviewers

M5
→ selects later acquisition rounds only
```

M4 does not select candidates. M2 does not select candidates.

A selected reviewer WorkItem remains required campaign work. Retry exhaustion
never triggers automatic profile substitution and routes through the existing
M5 → M8-B → M2 `OPERATOR-ACTION-REQUIRED` path. A qualified duplicate effective
identity remains evidence and may cause M5 to derive the next ordered round.
Eligible-pool exhaustion below the effective minimum produces exact M5
assurance-domain non-recovery cause material for M8-B with
`resolutionContracts = []`; it is never `DECISION-REQUIRED` and cannot mutate P
inside the current run.

M1 and M3 never establish a resolution from runner configuration, environment,
an unregistered model alias, or a model alias absent from the protocol bundle.

`PROTOCOL-CHANGED` requires one full new current-`P` campaign plus accepted
stale-protocol re-adjudication. It is not permission to mutate any old
ReviewCampaign.

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

The selected M4 realization is the explicit Pi M4 adapter around
`Models.streamSimple(...)`. Its construction responsibilities are exactly:

1. Construct a fresh public `pi-ai` Context and call
   `Models.streamSimple(...)` directly; do not use `AgentSession` or a
   coding-agent loop.
2. Set transport, `maxRetries`, tool behavior, deferred behavior, and the
   execution-owned `AbortSignal` explicitly rather than relying on defaults.
3. Capture provider-owned request/response evidence through `fetch`,
   `onPayload`, `onResponse`, and `onProviderStreamEvent` without rewriting the
   semantic request.
4. Bind provider response identity and effective model identity from
   provider-owned events; do not substitute the requested `AssistantMessage.model`
   or an unpopulated high-level `responseModel` field.
5. Preserve the exact provider-semantic textual completion and the operational
   M4 journal/recovery evidence before interpretation; never manufacture
   provider truth from Pi normalization or absence of response.

For `identityResolution.kind == "provider-reported"`, M4 may execute only
through a selected Dependency Contract realization that has established:

```text
provider-owned-canonical-effective-model-identity-v1
```

M4 does not infer this capability from `providerModel` spelling, repeated
observations, request/model inequality, Pi requested-model normalization, or
provider-specific naming. It never substitutes `requestModel`. An exact
Dependency Contract realization mismatch fails closed before provider
invocation through `DEPENDENCY-CONTRACT-VIOLATION`.

M4 captures the exact provider-owned identity token only after an accepted
realization contract has established the capability. It does not classify the
token's spelling.

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

The exact M4 proof artifact schema, its mapping to the exact Pi M4 adapter
call identity, and the external facts sufficient to prove that the
cognitive-call boundary was not crossed belong to the M4 NIB-M and the scoped
Pi M4 Dependency Contract.

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
same Pi M4 adapter call when the Pi M4 Dependency Contract authorizes them.
Those transport retries do not create runner Executions or hostile-review
protocol attempts.
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

interface AssuranceOperationalBlockerRequest {
  readonly obligationId: ObligationId;
  readonly workItemId: WorkItemId | null;
  readonly executionId: ExecutionId | null;
  readonly cause: NonRecoveryOperationalCauseRefV1 & {
    readonly producer: "assurance-ledger";
  };
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
  readonly assuranceRepositoryProjectionToEstablish:
    AssuranceRepositoryProjectionRef | null;
  readonly obligationsToAdd: readonly ObligationRef[];
  readonly workItemsToAdd: readonly WorkItemRef[];
  readonly executionRetryAuthorizationsToEstablish: readonly ExecutionRetryAuthorizationRef[];
  readonly blockersToAdd: readonly CampaignBlocker[];
  readonly candidateReviewReadiness: CandidateReviewReadinessRef | null;
}

type AssuranceLedgerDeltaWithoutBlockers =
  Omit<AssuranceLedgerDelta, "blockersToAdd">;

interface AssuranceLedgerPreparation
  extends AssuranceLedgerDeltaWithoutBlockers {
  readonly semanticBlockersToAdd: readonly SemanticBlocker[];
  readonly operationalBlockerRequests:
    readonly AssuranceOperationalBlockerRequest[];
}

interface AssuranceLedgerFinalizationRequest {
  readonly preparation: AssuranceLedgerPreparation;
  readonly materializedOperationalBlockers:
    readonly MaterializedOperationalBlockerV1[];
}
```

M5 must return every cross-module ledger product it establishes. It may not hide
a finding, evidence admission, adjudication, re-adjudication, obligation
satisfaction/supersession, qualified RepairIntent, qualified Decision Request,
execution-retry authorization, or candidate-review-readiness determination
behind only a new WorkItem or blocker.

M2 returns those admitted products in `GateARunSnapshot`; M5 receives the
complete prior ledger plus exact newly captured results, technical failures,
and exact M6 cognitive-attempt validation results.

M5 consumes repository campaign evidence only through the exact
`GateACampaignAuthorityEvaluationV1` named by
`GateAEvaluationContext.authorityEvaluation`. For every current or stale
repository-origin campaign, M5 obtains the exact
`RepositoryReviewObservationV1`, `sourceRecord`, and `referencedArtifacts` from
that immutable artifact and may read their bytes only through
`CampaignArtifactStore`. M5 never reconstructs repository review evidence by
scanning `repositoryPath`, a worktree or working tree, Git index, current
checkout/files, or current remote.

M5 must return complete cross-module `ObligationRef` values, not bare newly invented IDs.

`ObligationRef.definition` points to the immutable runtime-validated obligation definition that M2 registers in authoritative history.

The internal serialized schemas and algorithms for these exact product categories belong to M5 NIB-M. NIB-M may refine their internal artifact payloads but may not remove, merge, or invent another cross-module category.

The M5 public conceptual flow is:

```text
M5 prepare_complete_delta
→ AssuranceLedgerPreparation

M1 transports operational requests unchanged

M8-B materializes exact OperationalBlockers

M5 finalize_complete_delta
→ final AssuranceLedgerDelta

M2 admits final delta atomically
```

Finalization preserves every non-blocker preparation field exactly. Final
`blockersToAdd` is `semanticBlockersToAdd` followed by each
`materializedOperationalBlockers[*].blocker` in exact request order. M5 never
invents `BlockerId`, OAR bytes,
operator resolution kinds, or operator state effects. M5 never commits state or
mutates candidate repository material.

M5 may establish at most one assurance projection per delta. M2 retains all
projections append-only. A projection is consumed exactly when a retained
candidate names its `projectionId`; no consumed boolean, revision, or mutable
consumption state exists. One projection produces at most one candidate. For one
exact current source candidate, authoritative state contains at most one
unconsumed projection; M2 rejects a competing second projection.

If the exact current candidate has an unconsumed projection, M5 must not
establish a non-null `CandidateReviewReadinessRef` for that source candidate.
The projection must first be mechanically materialized into a successor, so a
readiness basis always names a candidate whose exact repository materialization
already contains every required evidence artifact.

Before a cognitive WorkItem has a qualified attempt, M5 preserves its exact
runner Executions, captured results or technical failures, M4 runtime evidence,
sealed completed outputs, and M6 validation evidence as GateARun operational
history. That pre-receipt history is not a hostile-review execution receipt and
must not be written or admitted under `formal/reviews/executions/`.

For one cognitive WorkItem whose retained acquisition candidate has
`identityResolution.kind == "provider-reported"`, after M6 returns the first
`qualified` semantic-attempt classification, M5 reads the exact M4 terminal
evidence bound to the captured result. If exact `providerModel` is `null`, the
empty string, or exact `latest`, M5 must preserve the raw response, all M4
runtime evidence, and all M6 validation evidence. It creates no schema-v3
receipt, no receipt `EvidenceRef`, no `resolved_identity`, and no retry
authorization. It performs no semantic retry, no reviewer-profile substitution,
and derives no later reviewer-acquisition round from that WorkItem.

M5 prepares exactly one assurance-ledger non-recovery operational blocker
request bound to the exact source obligation, WorkItem, and Execution with:

```text
producer = assurance-ledger
kind = provider-reported-identity-unavailable
resolutionContracts = []
```

The future M5-A Module Brief owns the exact cause-descriptor schema. M8-B remains
the sole blocker and Operator Action Request materializer, M2 remains the sole
authoritative writer, and normal external progression becomes
`OPERATOR-ACTION-REQUIRED`. This case is neither `protocol-invalid`,
`TechnicalExecutionFailure`, nor `DECISION-REQUIRED`.

When M6 returns the first `qualified` classification for any other admissible
logical cognitive execution, or when provider-reported `providerModel` is
non-empty and not exact `latest`, M5 mechanically assembles and seals one
complete schema-v3 receipt. For provider-reported identity M5 never inspects
identifier spelling and sets the exact request/provider binding, exact request
model, exact `providerModel`, `resolution_kind = "provider-reported"`, and exact
qualifying attempt as `evidence_attempt_id`. Effective counting remains
distinct `(provider, model_version)`.
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

If runner retry policy permits no replacement, no qualified attempt and no
complete schema-v3 receipt exist, while operational attempt history remains
durable. M5 returns one exact assurance-ledger
`NonRecoveryOperationalCauseRefV1` plus exact occurrence anchors for M8-B.
`resolutionContracts` may be empty when the accepted producer contract declares
no lawful same-run resolution. Issue #50 does not decide which exact M5-A causes
use `[]`, `request-operational-recheck`, or
`authorize-known-terminal-execution-replacement`; M5-A must close that mapping.
The external projection is `OPERATOR-ACTION-REQUIRED` only after M8-B
materializes the blocker and M2 admits it. A later lawful qualified attempt may
include preserved prior attempts.

A partial or no-qualified receipt is never review evidence. Validator evidence
for an individual attempt is likewise not a substitute for the complete
schema-v3 receipt.

### M6

```ts
interface CandidateSubjectMechanicalDerivationRequest {
  readonly runId: GateARunId;
  readonly candidateMaterialization: ArtifactRef;
}

interface GateASubjectMechanicalProjectionV1 {
  readonly schema: "gate-a-subject-mechanical-projection.v1";
  readonly runId: GateARunId;
  readonly candidateMaterialization: ArtifactRef;
  readonly semanticSubject: SemanticSubjectRef;
  readonly evidence: readonly ArtifactRef[];
}

interface CandidateSubjectMechanicalDerivationResult {
  readonly candidateMaterialization: ArtifactRef;
  readonly semanticSubject: SemanticSubjectRef;
  readonly projection: ArtifactRef;
  readonly evidence: readonly ArtifactRef[];
}

interface GateAReviewerProfileMechanicalFactV1 {
  readonly profileId: string;
  readonly provider: string;
  readonly requestModel: string;
  readonly frontierEligible: boolean;
  readonly identityResolution:
    | {
        readonly kind: "provider-reported";
      }
    | {
        readonly kind: "pinned-request-model";
        readonly requestModelIsImmutableVersion: boolean;
      };
}

interface GateAReviewerAcquisitionPolicyMechanicalFactV1 {
  readonly mode: "minimum-effective-independent-v1";
  readonly profileOrder: readonly string[];
}

interface GateACognitiveRetryPolicyMechanicalFactV1 {
  readonly technicalRetryAllowed: boolean;

  readonly schemaInvalidCompletionRetryAllowed: boolean;

  readonly semanticResultRetryAllowed: boolean;

  readonly allCompletedAttemptsMustBeSealed: boolean;

  readonly outcomeClassification:
    "role-aware-conservative";

  readonly firstProtocolValidCompletionIsTerminal: boolean;

  readonly deterministicallyValidatedRoles:
    readonly CognitiveExecutionRole[];

  readonly rolesWithoutDeterministicOutputValidator:
    readonly CognitiveExecutionRole[];

  readonly rolesWithoutDeterministicOutputValidatorProtocolInvalidAllowed:
    boolean;

  readonly rolesWithoutDeterministicOutputValidatorFirstCompletedResponseTerminal:
    boolean;
}

interface EffectiveReviewerIdentityRefV1 {
  readonly provider: string;
  readonly modelVersion: string;
}

interface GateAReviewerAcquisitionCandidateV1 {
  readonly profileId: string;
  readonly provider: string;
  readonly requestModel: string;
  readonly identityResolution:
    | {
        readonly kind: "provider-reported";
      }
    | {
        readonly kind: "pinned-request-model";
        readonly requestModelIsImmutableVersion: true;
      };
  readonly staticallyKnownEffectiveIdentity:
    EffectiveReviewerIdentityRefV1 | null;
}

interface InitialReviewerExecutionInputsRefV1 {
  readonly prompt: ArtifactRef;
  readonly promptRepositoryPath: string;

  readonly packet: ArtifactRef;
  readonly packetRepositoryPath: string;
}

interface ReviewCampaignPrerequisiteBasisRefV1 {
  readonly reviewCampaignId: ReviewCampaignId;

  readonly candidateId: CandidateRevisionId;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;

  readonly retryPolicy:
    GateACognitiveRetryPolicyMechanicalFactV1;

  readonly reviewContext: ReviewContext;

  readonly initialReviewerExecutionInputs:
    InitialReviewerExecutionInputsRefV1;

  readonly minimumIndependentReviewers: number;
  readonly acquisitionMode: "minimum-effective-independent-v1";

  readonly qualifyingReviewerProfileIds: readonly string[];

  readonly reviewerAcquisitionCandidates:
    readonly GateAReviewerAcquisitionCandidateV1[];

  readonly evidence: readonly ArtifactRef[];
}
```

`ReviewCampaignPrerequisiteBasisRefV1` is runner authoritative-history
projection material. It is not hostile-review evidence and is not a new product
or protocol artifact.

For every `ReviewCampaignPrerequisiteBasisRefV1 B`, require exactly:

```text
B.reviewCampaignId names one exact runner-produced ReviewCampaign C

C.provenance.kind == "runner-produced"

B.candidateId ==
    C.provenance.candidateId

B.semanticSubject ==
    C.semanticSubject

B.protocolBundle ==
    C.protocolBundle

B.retryPolicy is runtime-valid as
GateACognitiveRetryPolicyMechanicalFactV1

B.retryPolicy belongs to the exact protocol P named by B.protocolBundle

B.retryPolicy role arrays contain only valid CognitiveExecutionRole values

B.retryPolicy.deterministicallyValidatedRoles is duplicate-free

B.retryPolicy.rolesWithoutDeterministicOutputValidator is duplicate-free

B.reviewContext.runId ==
    C.provenance.originatingRunId

B.reviewContext.campaign ==
    C

B.reviewContext.candidate.candidateId ==
    B.candidateId

B.reviewContext.candidate.runId ==
    C.provenance.originatingRunId

B.reviewContext.candidate.semanticSubject ==
    C.semanticSubject

B.initialReviewerExecutionInputs.prompt exists and is intact

B.initialReviewerExecutionInputs.packet exists and is intact

B.initialReviewerExecutionInputs.prompt.repositoryPath == null

B.initialReviewerExecutionInputs.packet.repositoryPath == null

B.initialReviewerExecutionInputs.packetRepositoryPath ==
    "formal/reviews/packets/" +
    B.initialReviewerExecutionInputs.packet.sha256 +
    ".json"

B.minimumIndependentReviewers is integer >= 1

B.acquisitionMode ==
    "minimum-effective-independent-v1"

B.qualifyingReviewerProfileIds:
    duplicate-free
    unsigned-ASCII ascending

B.reviewerAcquisitionCandidates:
    duplicate-free by profileId

set(
  B.reviewerAcquisitionCandidates.map(profileId)
)
==
set(
  B.qualifyingReviewerProfileIds
)
```

Candidate ordering is preserved exactly from the accepted M3 result. Do not
sort `reviewerAcquisitionCandidates`.

`ReviewCampaignPrerequisiteBasisRefV1.retryPolicy` is immutable retained
construction authority for M5's protocol-side retry admissibility.

It is not new hostile-review policy authority.

It is a mechanically preserved projection of exact P.

For each candidate require:

```text
identityResolution.kind == "provider-reported"
→ staticallyKnownEffectiveIdentity == null

identityResolution.kind == "pinned-request-model"
→ identityResolution.requestModelIsImmutableVersion == true
→ staticallyKnownEffectiveIdentity ==
    {
      provider: candidate.provider,
      modelVersion: candidate.requestModel
    }
```

`evidence` is duplicate-free and every `ArtifactRef` is intact.

```ts
interface GateARepositoryReviewMechanicalFactV1 {
  readonly reviewId: ReviewCampaignId;
  readonly sourceRecord: ArtifactRef;
  readonly repositoryCommitSha: string;
  readonly semanticSubject: SemanticSubjectRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly referencedArtifacts: readonly ArtifactRef[];
}

interface GateAReviewAuthorityMechanicalProjectionV1 {
  readonly schema: "gate-a-review-authority-mechanical-projection.v1";
  readonly runId: GateARunId;
  readonly candidateMaterialization: ArtifactRef;
  readonly protocolBundle: ProtocolBundleRef;
  readonly retryPolicy:
    GateACognitiveRetryPolicyMechanicalFactV1;
  readonly initialReviewerExecutionInputs:
    InitialReviewerExecutionInputsRefV1;
  readonly minimumIndependentReviewers: number;
  readonly reviewerProfiles:
    readonly GateAReviewerProfileMechanicalFactV1[];
  readonly reviewerAcquisition:
    GateAReviewerAcquisitionPolicyMechanicalFactV1;
  readonly repositoryReviews:
    readonly GateARepositoryReviewMechanicalFactV1[];
  readonly evidence: readonly ArtifactRef[];
}

interface CandidateReviewAuthorityMechanicalProjectionRequest {
  readonly runId: GateARunId;
  readonly candidateMaterialization: ArtifactRef;
}

type CandidateReviewAuthorityMechanicalProjectionResult =
  | {
      readonly kind: "established";
      readonly candidateMaterialization: ArtifactRef;
      readonly protocolBundle: ProtocolBundleRef;
      readonly retryPolicy:
        GateACognitiveRetryPolicyMechanicalFactV1;
      readonly initialReviewerExecutionInputs:
        InitialReviewerExecutionInputsRefV1;
      readonly minimumIndependentReviewers: number;
      readonly reviewerProfiles:
        readonly GateAReviewerProfileMechanicalFactV1[];
      readonly reviewerAcquisition:
        GateAReviewerAcquisitionPolicyMechanicalFactV1;
      readonly repositoryReviews:
        readonly GateARepositoryReviewMechanicalFactV1[];
      readonly projection: ArtifactRef;
      readonly evidence: readonly ArtifactRef[];
    }
  | {
      readonly kind: "invalid";
      readonly candidateMaterialization: ArtifactRef;
      readonly projection: ArtifactRef;
      readonly diagnostics: ArtifactRef;
      readonly evidence: readonly ArtifactRef[];
    };

interface CognitiveAttemptValidationRequest {
  readonly kind: "cognitive-attempt";
  readonly runId: GateARunId;
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
    }
  | {
      readonly kind: "gate-a-qualification";
      readonly runId: GateARunId;
      readonly candidate: CandidateRevisionRef;
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

For subject derivation, require exactly:

```text
result.candidateMaterialization == request.candidateMaterialization

projection is the sealed canonical runner-owned representation of the exact
GateASubjectMechanicalProjectionV1

projection.candidateMaterialization == request.candidateMaterialization

projection.semanticSubject == result.semanticSubject

projection.evidence == result.evidence
```

The exact subject must come from the existing Turnlock Python subject authority.
The supported thin Python entry point must delegate to the existing checker
implementation that owns Gate A subject construction.

M6 must not reproduce in TypeScript:

```text
subject payload construction
authority artifact hashing
claim normalization
normative-coverage normalization
formal semantic-domain canonicalization
canonical JSON hashing
Gate A subject selector semantics
```

There is no `kind = invalid`, `kind = blocked`, or `semanticSubject = null`
branch for subject derivation.

If the existing mechanical authority executes trustworthily and establishes
that the exact candidate cannot produce a Gate A subject, including duplicate
`formal_semantic_domain` ID, missing required subject authority artifact,
ambiguous required subject authority, or another trustworthy
subject-construction integrity failure, the result is:

```text
repository/candidate integrity failure
no CandidateSubjectMechanicalDerivationResult
no CampaignBlocker
no OperationalBlocker
no Operator Action Request
no OPERATOR-ACTION-REQUIRED
no DECISION-REQUIRED
```

If trustworthy Python authority cannot be obtained because the mechanism itself
is unreliable, the result is an implementation/process/integrity/dependency
failure and no `CandidateSubjectMechanicalDerivationResult`.

Transient local/process/resource failure is invocation failure, creates no
`CampaignBlocker`, and permits retry from durable state.

For review-authority `kind = established`, require exactly:

```text
candidateMaterialization == request.candidateMaterialization

projection is a sealed canonical
GateAReviewAuthorityMechanicalProjectionV1

projection.protocolBundle ==
    result.protocolBundle

projection.retryPolicy ==
    result.retryPolicy

projection.initialReviewerExecutionInputs ==
    result.initialReviewerExecutionInputs

projection.minimumIndependentReviewers ==
    result.minimumIndependentReviewers

projection.reviewerProfiles ==
    result.reviewerProfiles

projection.repositoryReviews ==
    result.repositoryReviews

projection.evidence ==
    result.evidence
```

`retryPolicy` is the exact mechanically projected `P.policies.retry` of the
validated protocol bundle P. M6 obtains every value from that exact P and maps
exactly:

```text
P.policies.retry.technical_retry_allowed
→ technicalRetryAllowed

P.policies.retry.schema_invalid_completion_retry_allowed
→ schemaInvalidCompletionRetryAllowed

P.policies.retry.semantic_result_retry_allowed
→ semanticResultRetryAllowed

P.policies.retry.all_completed_attempts_must_be_sealed
→ allCompletedAttemptsMustBeSealed

P.policies.retry.outcome_classification
→ outcomeClassification

P.policies.retry.first_protocol_valid_completion_is_terminal
→ firstProtocolValidCompletionIsTerminal

P.policies.retry.deterministically_validated_roles
→ deterministicallyValidatedRoles

P.policies.retry.roles_without_deterministic_output_validator
→ rolesWithoutDeterministicOutputValidator

P.policies.retry.roles_without_deterministic_output_validator_protocol_invalid_allowed
→ rolesWithoutDeterministicOutputValidatorProtocolInvalidAllowed

P.policies.retry.roles_without_deterministic_output_validator_first_completed_response_terminal
→ rolesWithoutDeterministicOutputValidatorFirstCompletedResponseTerminal
```

Both role arrays preserve exact values and exact order from P, with no sorting,
deduplication, or reinterpretation.

M6 decides no retry semantic. It projects only exact mechanically validated P.
M6 must not use hardcoded protocol-v6 retry constants, default retry values, a
current-protocol fixed-path reread after projection authority is established,
inference from `CognitiveAttemptValidationResult`, inference from role alone,
or any M2 runner hard limit when constructing this fact.

`GateACognitiveRetryPolicyMechanicalFactV1` contains no runner retry count,
runner absolute limit, `retryAuthorizationId`, Execution history,
`StateRevision`, timestamp, current deficit, or provider transport retry
configuration.

`initialReviewerExecutionInputs` is an immutable exact execution-input basis.
Its `prompt` and `packet` `ArtifactRef` values are immutable byte carriers in
`CampaignArtifactStore`. Require exactly:

```text
prompt.repositoryPath == null
packet.repositoryPath == null
packet.mediaType == "application/json"
promptRepositoryPath is non-empty
packetRepositoryPath matches exactly:
formal/reviews/packets/<lowercase-64-hex-sha256>.json
packetRepositoryPath ==
    "formal/reviews/packets/" + packet.sha256 + ".json"
```

Do not overload `ArtifactRef.repositoryPath` with a future repository path for
bytes not materially present in the candidate repository. Do not assign a new
media type to `prompt`; preserve the media type of its exact immutable byte
carrier.

For the prompt, M6 mechanically establishes exactly:

```text
result.initialReviewerExecutionInputs.promptRepositoryPath
==
exact current-P prompts["initial-reviewer"].path

result.initialReviewerExecutionInputs.prompt.sha256
==
exact current-P prompts["initial-reviewer"].sha256
```

The prompt bytes are exactly the bytes bound by that path and SHA in the exact
candidate materialization. M6 must not rewrite, normalize, or choose another
prompt.

For the packet, M6 must delegate byte construction to the existing Python
mechanism that already owns mechanical Gate A review-packet construction,
including the existing equivalent of:

```text
build_gate_a_review_packet_bytes(...)
```

M6 must not reimplement in TypeScript:

```text
subject payload construction
authority content enumeration
authority content ordering
authority content hashing
canonical Gate A packet serialization
packet subject binding
```

Construct the packet from the exact immutable candidate materialization for
which `CandidateReviewAuthorityMechanicalProjectionResult` is produced and
which the runner-produced campaign binds as its exact production candidate
authority. Seal or intern the resulting exact canonical Python-authority bytes in
`CampaignArtifactStore` as an immutable runner artifact. Require exactly:

```text
packet.repositoryPath == null
packet.mediaType == "application/json"
packet bytes are the exact canonical Python-authority bytes
packetRepositoryPath ==
    "formal/reviews/packets/" + packet.sha256 + ".json"
```

The future exact M6 Module Brief may close the precise Python invocation and
`ArtifactRef` realization. It must not change any of these bindings.

`minimumIndependentReviewers` is mechanically projected from the applicable
hostile-review policy. It is not added to protocol identity `P`.

`reviewerProfiles` is the complete validated current-`P` registry, ordered by
`profileId` unsigned ASCII ascending. M6 does not select
`qualifyingReviewerProfileIds`.

`repositoryReviews` is the complete mechanically valid Gate A
assurance-decomposition review-record corpus selected by the exact candidate
authority, ordered by `reviewId` unsigned ASCII ascending.

For each item:

```text
reviewId == exact record.review_id
repositoryCommitSha == exact record.repository_commit
semanticSubject == exact unique Gate A record subject
protocolBundle == exact record protocol bundle
sourceRecord == exact sealed/ingested record bytes
```

For every repository review fact, M6 mechanically establishes from the exact
immutable candidate materialization and existing Python hostile-review authority
the complete repository artifact closure needed to interpret and validate that
exact record. The closure is the exact graph required by current checker
authority, including as applicable: review packet, protocol bundle and required
predecessors, protocol-bound meta-schemas, prompts, execution receipts, raw
outputs, challenge packets and outputs, adjudication artifacts, and every other
exact hostile-review artifact required by accepted authority. M6 invents no
alternate validation graph and interprets no finding semantics.

For `referencedArtifacts`:

```text
sourceRecord is excluded
every ArtifactRef.repositoryPath is non-null
every path is inside the exact candidate materialization
every ArtifactRef resolves to exact bytes at that path
every SHA matches the review record or accepted transitive contract
paths are duplicate-free
order is repositoryPath exact UTF-8 unsigned-byte ascending
```

If a mechanically trustworthy complete closure cannot be established, M6 does
not return an established review-authority fact for that record and follows the
existing invalid/integrity behavior.

Duplicate `review_id` is invalid authority; never tie-break.
Malformed/referentially invalid review evidence is never silently omitted.

The `invalid` branch is legal only when the existing Python authority executed
trustworthily and established an invalid protocol/review-authority condition.
Failure to execute or trust the Python authority is not `kind = invalid`; it is
an implementation/process/integrity/dependency failure outside this union.

M6 must use supported thin Python authority entry points delegating to existing
checker logic.

M6 must not reimplement in TypeScript:

```text
current protocol validation
protocol predecessor-chain validation
meta-schema selection
review-evidence schema validation
packet binding
prompt/schema/reference validation
execution-receipt validation
review-record integrity
```

Candidate-scoped M6 validation is bound to the exact candidate materialization
already reachable from the request's candidate/review context.

A caller-supplied mutable repository path is never candidate authority.

The future M6 NIB-M owns the exact ephemeral checker-input realization needed
to run the existing Python authority.

`PublishedRepositoryViewRef` remains the post-publication exact view contract.

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
interface RepositoryInspectionRequest {
  readonly runId: GateARunId;
  readonly repositoryPath: string;
}

type RepositoryInspectionResult =
  | {
      readonly kind: "observed";
      readonly inspection: RepositoryInspectionRef;
    }
  | {
      readonly kind: "blocked";
      readonly cause: NonRecoveryOperationalCauseRefV1;
    };
```

For `RepositoryInspectionResult.kind == "blocked"`, M1 requires:

```text
cause.producer == "repository-control"

cause.resolutionContracts equals exactly:
[
  {
    kind: "request-operational-recheck"
  }
]
```

A repository-inspection cause may not expose:

```text
authorize-known-terminal-execution-replacement
authorize-uncertain-execution-replacement
```

Repository inspection has no WorkItem Execution. M7 owns the future exact
repository-control cause schemas; this System Brief defines no individual cause
schema.

```ts
interface CandidateConstructionRequest {
  readonly runId: GateARunId;
  readonly sourceCandidate: CandidateRevisionRef;
  readonly repairIntent: RepairIntentRef | null;
  readonly assuranceProjection:
    AssuranceRepositoryProjectionRef | null;
}

interface CandidateSealResult {
  readonly sealedCandidate: SealedCandidateMaterializationRef;
}

interface PublicationPreparationRequest {
  readonly runId: GateARunId;
  readonly repositoryInspection: RepositoryInspectionRef;
  readonly candidate: CandidateRevisionRef;
  readonly qualification: GateAQualificationRef;
  readonly target: RepositoryPublicationTargetRef;
}

type PublicationPreparationResult =
  | {
      readonly kind: "prepared";
      readonly publication: PreparedPublication;
    }
  | {
      readonly kind: "blocked";
      readonly cause: NonRecoveryOperationalCauseRefV1 & {
        readonly producer: "repository-control";
      };
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

type PublicationObservationQualificationRequest =
  | {
      readonly kind: "executed-publication";
      readonly intent: PublicationIntentRef;
      readonly candidate: CandidateRevisionRef;
      readonly executionResult: CapturedExecutionResult;
    }
  | {
      readonly kind: "already-current";
      readonly intent: PublicationIntentRef;
      readonly candidate: CandidateRevisionRef;
      readonly observation: PublicationAlreadyCurrentObservationRef;
    };

type PublicationObservationQualificationResult =
  | {
      readonly kind: "confirmed";
      readonly confirmation: PublicationConfirmationRef;
      readonly publishedView: PublishedRepositoryViewRef;
    }
  | {
      readonly kind: "not-applied";
      readonly nonApplication: PublicationNonApplicationRef;
    }
  | {
      readonly kind: "blocked";
      readonly cause: NonRecoveryOperationalCauseRefV1 & {
        readonly producer: "repository-control";
      };
    };
```

Publication-preparation bindings:

```text
request.runId ==
    request.repositoryInspection.runId ==
    request.candidate.runId

request.repositoryInspection.baselineAuthority ==
    exact GateARun.initialRepositoryAuthority

request.repositoryInspection.publicationTarget ==
    request.target

request.target ==
    exact GateARun.publicationTarget
```

For ordinary M1 publication preparation:

```text
request.repositoryInspection ==
    exact current GateARunSnapshot.repositoryInspection
```

The caller may not substitute another structurally valid
`RepositoryInspectionRef` having the same `baselineAuthority` or
`publicationTarget`.

The exact retained preflight inspection is required.

No caller may provide a separate baseline Git basis or baseline authority.

Candidate-construction bindings:

```text
request.runId == request.sourceCandidate.runId
request.repairIntent != null OR request.assuranceProjection != null
```

When repair is non-null, it is the exact current authoritative `RepairIntentRef`,
its run/candidate bind the source, and M7 uses only its `approvedPatch`. When
assurance projection is non-null, it is the exact authoritative projection and
its run/source/S bindings equal the source candidate.

Before applying either change, M7 derives exact repair and assurance path sets
and requires an empty intersection. It then applies exactly:

```text
1. exact immutable source candidate
2. exact RepairIntent patch if non-null
3. exact AssuranceRepositoryProjection if non-null
4. validate resulting candidate
5. canonical materialization
6. Git tree projection
7. round-trip verification
8. seal
```

No precedence rule, merge, or conflict resolution exists. M7 validates the
projection `ArtifactRef`, canonical runner JSON, exact schema, source candidate,
parent subject and protocol binding, ordered unique non-empty entries, allowed
namespace, intact content refs, and exact source path state. It applies only the
additive/idempotent rules above and never interprets hostile-review content.

Successful candidate and sealed-candidate provenance contains the exact nullable
repair/projection IDs from the request. Candidate construction has no normal
blocked result. Invalid construction provenance, overlap, namespace, bytes,
mode/type, or source binding is an implementation/process/integrity failure.

Repository inspection is the only M7 operation in the initial-run path that may
read mutable `repositoryPath` to establish the initial mechanical repository
observation.

Before returning `kind = "observed"`, M7 must have already sealed all durable
material required by `RepositoryInspectionRef`.

No authoritative baseline may be committed and then preserved afterwards.

If M7 cannot establish a reconstructible baseline Git basis or exact sealed
baseline candidate, it must not return `kind = "observed"`.

M7 observes the exact current predecessor from the exact publication target
during publication preparation. The caller never selects, predicts, caches, or
supplies the publication predecessor.

Publication preparation performs no remote mutation but may perform exact
read-only target observation and acquire immutable Git objects/evidence needed
to establish the predecessor and fast-forward relation. Remote observation is
not the publication side effect. The future M7 NIB-M and Git Dependency
Contract define the exact observation and Git-dependency representations.

It constructs the exact immutable successor repository object without mutating
the remote publication target. The resulting exact target, successor commit
SHA, successor tree SHA, and fast-forward ancestry/equality proof are known
before `PublicationIntentRef` is committed.

For Gate A publication construction, `"fast-forward"` is reflexive for
realization selection: predecessor must be ancestor-or-equal to successor;
predecessor unequal to successor selects `"conditional-ref-update"`, while
predecessor equal to successor selects `"already-current"`. M1 does not choose
that realization; M7 derives it mechanically. CAS alone remains insufficient;
ancestry/equality evidence remains required.

Only after the exact intent is durable may M7 attempt the conditional mutation
of the exact target ref. Publication itself executes as a normal campaign
WorkItem/Execution owned by M7 only for the `"conditional-ref-update"`
realization.

For `"already-current"`, M1 creates no Execution, performs no
`AuthorizeExecutionV1`, no `ArmExecutionDispatchV1`, and no publication
push/mutation. M1 asks M7 for one fresh exact read-only observation of the exact
target bound to the current `PublicationIntent`, candidate, target, and intended
successor. If the fresh observation still proves target authority equals the
successor, M1 submits a `PublicationObservationQualificationRequest` with
`kind = "already-current"`. If the target no longer equals the successor, M1
does not qualify or Arm; it reloads the authoritative snapshot and returns to
ordinary publication preparation. Because no Arm occurred, this is not
execution uncertainty and M8 recovery is not involved.

For `"conditional-ref-update"`, M7 may perform the remote publication mutation
only from an `ArmedExecutionDispatchRef` produced after successful M2 Arm
admission. The armed dispatch must identify the exact repository-control
WorkItem and Execution authorized for the exact `PublicationIntent`. M7 must
not reconstruct dispatch identity or recovery provenance from `ExecutionRef`,
`PublicationIntentRef`, a repository path, or remote state alone.

`PublicationExecutionCapture.kind = "captured"` means M7 obtained one exact
durable publication-attempt observation artifact. It does not by itself mean
publication is confirmed. A direct terminal captured publication attempt may
produce `PublicationNonApplicationRef` only when M7 positively establishes
that the exact authorized target-ref mutation was not applied. This fact is
distinct from `PROVEN-NOT-EXECUTED`, `TechnicalExecutionFailure`, and execution
uncertainty; it does not authorize retry or satisfy the publication obligation.

`PublicationExecutionCapture.kind = "uncertain"` carries the complete
`UnresolvedExecutionRecoveryRef` for `request.dispatch`. Its `execution`,
`workItem`, and `dispatchIntent` must equal the exact armed-dispatch values.
Its dispatch evidence may only preserve the arm-time evidence and append exact
evidence observed during this same publication attempt.

M7 never returns `RECONCILABLE` or `UNRESOLVABLE`.

All publication execution uncertainty is committed and classified through M8.
A terminal observation that establishes the intended successor after Arm
remains in the executed-publication outcome/recovery lifecycle; it never enters
the already-current shortcut and must not bypass GI-65/GI-75.

M7 implements `ExecutionRecoveryPort` for publication executions. A terminal
publication recovery observation must return `RecoveredExecutionOutcome.kind =
"captured"` containing the exact recovered publication observation.

After one direct captured M7 result is admitted through
`AdmitExecutionOutcomeV1`, or after a recovered captured result is admitted
through `AdmitExecutionRecoveryV1`, M1 uses the executed-publication form of
`PublicationObservationQualificationRequest`.

A recovered captured result may qualify as `confirmed` or `blocked`, but it
may not qualify as `not-applied`. If M7 returns `not-applied` for a recovered
source, M1 fails the invocation as an implementation/process/integrity
failure and submits no publication-qualification mutation to M2.

`PublicationObservationQualificationResult.kind = "not-applied"` is valid only
for `request.kind = "executed-publication"`. The already-current request kind
may produce `confirmed` but never `not-applied`. Only `confirmed` may create
`PublicationConfirmationRef`; `not-applied` creates no confirmation and does
not satisfy the publication obligation. `PublicationNonApplicationRef` v1 is
produced only from direct terminal M7 capture, not from recovery-derived
material.

That confirmation result also returns the exact `PublishedRepositoryViewRef`
consumed by post-publication M6 validation.

M7 may return `blocked` when the captured publication observation proves a
publication conflict/divergence or otherwise cannot satisfy the committed
`PublicationIntent`. That is a domain result from known evidence, not an
uncertainty classification.

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
  | "cognitive-execution"
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

interface NonRecoveryOperationalCauseRefV1 {
  readonly producer: NonRecoveryOperationalBlockerProducerV1;
  readonly causeDescriptor: ArtifactRef;
  readonly basisArtifacts: readonly ArtifactRef[];
  readonly resolutionContracts:
    readonly NonRecoveryOperatorResolutionContractV1[];
}

`NonRecoveryOperationalCauseRefV1` is immutable producer material used to
request M8-B blocker materialization. It is not authoritative campaign state
and is not an `OperationalBlocker`.

The normative bindings are:

```text
causeDescriptor is the exact producer-owned canonical operational cause

causeDescriptor.mediaType == "application/json"

causeDescriptor exists and is intact

basisArtifacts is duplicate-free

every basisArtifacts ArtifactRef exists and is intact

resolutionContracts is duplicate-free

producer modules own:
    cause schema
    cause-domain meaning
    cause field validation
    basis evidence
    lawful non-recovery resolution contracts

producer modules do NOT own:
    BlockerId
    Operator Action Request bytes
    blocker occurrence identity
    operator-resolution state effects
```

The cause reference is immutable producer material used only to request M8-B
materialization. It does not itself create blocker identity, an Operator Action
Request, a blocker occurrence identity, or an operator-resolution state effect.

M7 repository inspection constructs and runtime-validates its exact canonical
cause descriptor, seals that descriptor through `CampaignArtifactStore`, and
returns the resulting cause reference with its basis artifacts. M8-B alone
materializes the `OperationalBlocker`; M2 independently validates the
materialized blocker before authoritative admission.

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

## 21. Pi M4 runtime boundary

Only M4 imports `@earendil-works/pi-ai`, and only through the explicit
campaign-owned Pi M4 adapter around public `Models.streamSimple(...)`.

All other modules depend on M0 contracts and the M4 port.

The selected dependency identity is:

```text
package = @earendil-works/pi-ai@0.99.2
Pi source commit = 005af57d88ee23b33778f343a9595b32e67ff788
public execution surface = Models.streamSimple(...)
execution wrapper = explicit Pi M4 adapter
```

The scoped Pi M4 Dependency Contract must close at least:

```text
cognitive WorkItem / hostile-review receipt execution identity
→ runner Execution / hostile-review receipt attempt identity
→ explicit Pi M4 adapter invocation of Models.streamSimple(...)
→ provider transport attempt(s)
```

For cognitive WorkItems, the construction binding is exact:

```text
receipt.execution_id = WorkItemId
receipt.attempts[*].attempt_id = corresponding ExecutionId
receipt.attempts[*].call_id = exact Pi M4 adapter call identity
```

A runner-level protocol retry therefore creates a new `Execution` and, if a
qualified attempt is eventually reached, a new receipt attempt for the same
WorkItem/receipt identity.

A dependency-internal transport retry does not. Before qualification, the exact
attempt remains GateARun operational history rather than an incomplete
hostile-review receipt.

The Pi M4 Dependency Contract must define:

* adapter call identity;
* provider-attempt identity;
* dispatch boundary;
* internal retry behavior;
* cancellation guarantees;
* result identity;
* provider response identity where available;
* observable attempt history;
* recovery/reconciliation capability;
* behavior when runner execution authority is revoked.

The Pi M4 adapter may not begin a new provider attempt after the owning
caller's campaign execution authority has been revoked.

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

`OPERATOR-ACTION-REQUIRED` does not imply that the current `GateARun`
necessarily exposes a same-run `OperatorResolution` capable of making progress.

When an exact blocker has `resolutionContracts == []`, the Operator Action
Request is a durable explanation of the required external intervention. The
current run remains blocked and may require repository/protocol authority to
change before a later `GateARun` can proceed.

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
```

M7 observes the exact current predecessor from the exact publication target
itself during publication preparation. The caller never selects, predicts,
caches, or supplies that predecessor. Publication preparation performs no remote
mutation but may perform exact read-only target observation and acquire
immutable Git objects/evidence needed to establish the predecessor and the
fast-forward relation. Remote observation is not the publication side effect.

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
mechanical proof that predecessor is an ancestor-or-equal to successor
+
relationship = fast-forward
+
predecessor != successor → realization = conditional-ref-update
predecessor == successor → realization = already-current
```

The preparation itself does not mutate the remote publication target. CAS alone
is insufficient; ancestry/equality evidence remains required.

The committed PublicationIntent therefore binds:

exact publication target
+
exact authorized predecessor-to-successor transition
+
exact qualified CandidateRevision
+
exact GateAQualificationRef
```

For `conditional-ref-update`, the publication effect must be conditional on
the exact target ref still having the exact M7-observed predecessor. For
`already-current`, no external publication mutation is required; M1 must obtain
one fresh exact read-only observation before confirmation. CAS success alone is
insufficient unless the committed fast-forward transition proof remains valid.

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
M7-observed predecessor
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
→ an uncertain execution may follow its existing recovery contract;
  a known terminal PublicationNonApplicationRef does not by itself authorize
  an automatic replacement Execution

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

A direct terminal captured publication attempt may positively establish an exact
`PublicationNonApplicationRef`. That fact is distinct from
`PROVEN-NOT-EXECUTED`, `TechnicalExecutionFailure`, and execution uncertainty;
it does not satisfy the publication obligation or automatically retry the same
WorkItem. For prior `I1 = P → T`, `W1`, `E1` with this exact fact:

```text
fresh target == T
→ a fresh ordinary preparation may produce I2 = T → T;
  normal replacement rules apply and I2 follows the already-current path

fresh target == X, X ancestor T, X != P
→ a fresh ordinary preparation may produce I2 = X → T;
  I2 is a new PublicationIntent and new WorkItem, not a retry of W1

fresh target == P
→ fresh preparation reproduces exact I1;
  do not duplicate EstablishPublicationIntentV1 or auto-authorize E2;
  M7/repository-control produces the normal non-recovery operational cause
  for the still-required exact publication WorkItem
```

Under the existing M8-B boundary, that last operational cause may expose
`request-operational-recheck` or
`authorize-known-terminal-execution-replacement` where the producer-domain
contract permits. It must not expose
`authorize-uncertain-execution-replacement` merely for an exact known-terminal
`PublicationNonApplicationRef`.

Already-current confirmation is legal only before any Execution exists for the
exact publication WorkItem. After publication Arm, observing the intended
successor never enters the already-current shortcut; it belongs to the existing
outcome/recovery lifecycle of the armed Execution and may not bypass GI-65/GI-75.

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

The exact credential names/source integration belong to the M4 NIB-M and Pi M4 Dependency Contract.

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

        inspection_result = repository_control.inspect_repository({
            runId: run.runId,
            repositoryPath: command.repositoryPath
        })

        if inspection_result is blocked:
            expected_state_revision = snapshot.stateRevision
            snapshot = campaign_state.load_snapshot({
                runId: run.runId
            })
            require snapshot.stateRevision == expected_state_revision

            root_preflight_obligation =
                exact current outstanding bootstrap preflight obligation
            require root_preflight_obligation == bootstrap.preflightObligation
            require inspection_result.cause.producer == "repository-control"
            require inspection_result.cause.resolutionContracts equals exactly:
                [
                    {
                        kind: "request-operational-recheck"
                    }
                ]

            materialized =
                recovery_operator.materialize_operational_blocker({
                    kind: "producer-occurrence",
                    runId: run.runId,
                    baseStateRevision: snapshot.stateRevision,
                    producer: "repository-control",
                    obligationId: root_preflight_obligation.obligationId,
                    workItemId: null,
                    executionId: null,
                    causeDescriptor: inspection_result.cause.causeDescriptor,
                    resolutionContracts:
                        inspection_result.cause.resolutionContracts,
                })

            require materialized.blocker.kind == "operational"
            require materialized.blocker.obligationId ==
                root_preflight_obligation.obligationId
            require materialized.blocker.executionId == null

            M1 does not construct `BlockerId`, `GateAOperatorActionRequestV1`,
            or `operatorRequest`; it consumes the exact M8-B materialization.

            committed = commit through M2 one exact EstablishOperationalBlockersV1
                using ownership + expected_state_revision:
                {
                    kind: "establish-operational-blockers",
                    obligationsToAdd: [],
                    blockers: [
                        materialized.blocker
                    ],
                    basisArtifacts:
                        ordered duplicate-free first-occurrence sequence:
                        [
                            inspection_result.cause.causeDescriptor,
                            ...inspection_result.cause.basisArtifacts
                        ]
                }
            snapshot = committed snapshot
            require snapshot.run.initialRepositoryAuthority == null
            require snapshot.run.publicationTarget == null
            require root preflight obligation remains outstanding
            return project_runner_result(snapshot)

        require inspection_result.kind == observed
        inspection = inspection_result.inspection

        subject_derivation = mechanical_validation.derive_candidate_subject({
            runId: run.runId,
            candidateMaterialization:
                inspection.sealedBaselineCandidate.materialization
        })

        review_authority = mechanical_validation.project_candidate_review_authority({
            runId: run.runId,
            candidateMaterialization:
                inspection.sealedBaselineCandidate.materialization
        })

        preflight = campaign_authority.preflight({
            runId: run.runId,
            repositoryInspection: inspection,
            subjectDerivation: subject_derivation,
            reviewAuthority: review_authority
        })

        if preflight.kind == "blocked":
            root_preflight_obligation =
                exact current outstanding bootstrap preflight obligation
            require root_preflight_obligation == bootstrap.preflightObligation
            require preflight.cause.producer == "campaign-authority"
            require preflight.cause.resolutionContracts equals exactly:
                [
                    {
                        kind: "request-operational-recheck"
                    }
                ]

            materialized =
                recovery_operator.materialize_operational_blocker({
                    kind: "producer-occurrence",
                    runId: run.runId,
                    baseStateRevision: snapshot.stateRevision,
                    producer: "campaign-authority",
                    obligationId: root_preflight_obligation.obligationId,
                    workItemId: null,
                    executionId: null,
                    causeDescriptor: preflight.cause.causeDescriptor,
                    resolutionContracts: preflight.cause.resolutionContracts
                })

            committed = commit through M2 one exact EstablishOperationalBlockersV1:
                {
                    kind: "establish-operational-blockers",
                    obligationsToAdd: [],
                    blockers: [
                        materialized.blocker
                    ],
                    basisArtifacts:
                        ordered duplicate-free first-occurrence sequence:
                        [
                            preflight.cause.causeDescriptor,
                            ...preflight.cause.basisArtifacts
                        ]
                }
            snapshot = committed snapshot

            require snapshot.run.initialRepositoryAuthority == null
            require snapshot.run.publicationTarget == null
            require root preflight obligation remains outstanding
            return project_runner_result(snapshot)

        require preflight.kind == established
        require preflight.baselineAuthority == inspection.baselineAuthority
        require preflight.publicationTarget == inspection.publicationTarget

        preflight_basisArtifacts = ordered duplicate-free first-occurrence sequence:
            [
                inspection.baselineGitBasis,
                inspection.sealedBaselineCandidate.materialization,
                ...inspection.sealedBaselineCandidate.materializationEvidence,
                ...inspection.evidence,
                preflight.subjectProjection,
                preflight.reviewAuthorityProjection,
                ...preflight.evidence
            ]

        root_preflight_disposition = exact satisfied disposition:
            {
                kind: "satisfied",
                obligationId: bootstrap.preflightObligation.obligationId,
                basisEvidenceIds: [],
                basisArtifacts: preflight_basisArtifacts
            }

        commit through M2 one exact EstablishPreflightV1:
            {
                kind: "establish-preflight",
                repositoryInspection: inspection,
                baselineAuthority: preflight.baselineAuthority,
                publicationTarget: preflight.publicationTarget,
                protocolBundle: preflight.protocolBundle,
                baselineSemanticSubject: preflight.baselineSemanticSubject,
                subjectProjection: preflight.subjectProjection,
                reviewAuthorityProjection: preflight.reviewAuthorityProjection,
                preflightEvidence: preflight.evidence,
                rootObligationDisposition: root_preflight_disposition
            }

        snapshot = committed snapshot

        candidate = construct complete CandidateRevision:
            runId = run.runId,
            ordinal = 0,
            parentCandidateId = null,
            materialization = inspection.sealedBaselineCandidate.materialization,
            semanticSubject = snapshot.preflightSemanticSubject,
            producedByRepairIntentId = null
            producedByAssuranceProjectionId = null

        commit through M2 one exact AdmitCandidateV1:
            {
                kind: "admit-candidate",
                sealedCandidate: inspection.sealedBaselineCandidate,
                candidate
            }

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

            inspection_result = repository_control.inspect_repository({
                runId: run.runId,
                repositoryPath: command.repositoryPath
            })

            if inspection_result is blocked:
                expected_state_revision = snapshot.stateRevision
                snapshot = campaign_state.load_snapshot({
                    runId: run.runId
                })
                require snapshot.stateRevision == expected_state_revision
                require root_preflight_obligation is the exact current outstanding
                    bootstrap preflight obligation
                require inspection_result.cause.producer == "repository-control"
                require inspection_result.cause.resolutionContracts equals exactly:
                    [
                        {
                            kind: "request-operational-recheck"
                        }
                    ]

                materialized =
                    recovery_operator.materialize_operational_blocker({
                        kind: "producer-occurrence",
                        runId: run.runId,
                        baseStateRevision: snapshot.stateRevision,
                        producer: "repository-control",
                        obligationId: root_preflight_obligation.obligationId,
                        workItemId: null,
                        executionId: null,
                        causeDescriptor: inspection_result.cause.causeDescriptor,
                        resolutionContracts:
                            inspection_result.cause.resolutionContracts,
                    })

                require materialized.blocker.kind == "operational"
                require materialized.blocker.obligationId ==
                    root_preflight_obligation.obligationId
                require materialized.blocker.executionId == null

                M1 does not construct `BlockerId`, `GateAOperatorActionRequestV1`,
                or `operatorRequest`; it consumes the exact M8-B materialization.

                committed = commit through M2 one exact EstablishOperationalBlockersV1
                    using ownership + expected_state_revision:
                    {
                        kind: "establish-operational-blockers",
                        obligationsToAdd: [],
                        blockers: [
                            materialized.blocker
                        ],
                        basisArtifacts:
                            ordered duplicate-free first-occurrence sequence:
                            [
                                inspection_result.cause.causeDescriptor,
                                ...inspection_result.cause.basisArtifacts
                            ]
                    }
                snapshot = committed snapshot
                require snapshot.run.initialRepositoryAuthority == null
                require snapshot.run.publicationTarget == null
                require root_preflight_obligation remains outstanding
                return project_runner_result(snapshot)

            require inspection_result.kind == observed
            inspection = inspection_result.inspection

            subject_derivation = mechanical_validation.derive_candidate_subject({
                runId: run.runId,
                candidateMaterialization:
                    inspection.sealedBaselineCandidate.materialization
            })

            review_authority = mechanical_validation.project_candidate_review_authority({
                runId: run.runId,
                candidateMaterialization:
                    inspection.sealedBaselineCandidate.materialization
            })

            preflight = campaign_authority.preflight({
                runId: run.runId,
                repositoryInspection: inspection,
                subjectDerivation: subject_derivation,
                reviewAuthority: review_authority
            })

            if preflight.kind == "blocked":
                require preflight.cause.producer == "campaign-authority"
                require preflight.cause.resolutionContracts equals exactly:
                    [
                        {
                            kind: "request-operational-recheck"
                        }
                    ]

                materialized =
                    recovery_operator.materialize_operational_blocker({
                        kind: "producer-occurrence",
                        runId: run.runId,
                        baseStateRevision: snapshot.stateRevision,
                        producer: "campaign-authority",
                        obligationId: root_preflight_obligation.obligationId,
                        workItemId: null,
                        executionId: null,
                        causeDescriptor: preflight.cause.causeDescriptor,
                        resolutionContracts: preflight.cause.resolutionContracts
                    })

                committed = commit through M2 one exact EstablishOperationalBlockersV1:
                    {
                        kind: "establish-operational-blockers",
                        obligationsToAdd: [],
                        blockers: [
                            materialized.blocker
                        ],
                        basisArtifacts:
                            ordered duplicate-free first-occurrence sequence:
                            [
                                preflight.cause.causeDescriptor,
                                ...preflight.cause.basisArtifacts
                            ]
                    }
                snapshot = committed snapshot

                require snapshot.run.initialRepositoryAuthority == null
                require snapshot.run.publicationTarget == null
                require root_preflight_obligation remains outstanding
                return project_runner_result(snapshot)

            require preflight.kind == established
            require preflight.baselineAuthority == inspection.baselineAuthority
            require preflight.publicationTarget == inspection.publicationTarget

            preflight_basisArtifacts = ordered duplicate-free first-occurrence sequence:
                [
                    inspection.baselineGitBasis,
                    inspection.sealedBaselineCandidate.materialization,
                    ...inspection.sealedBaselineCandidate.materializationEvidence,
                    ...inspection.evidence,
                    preflight.subjectProjection,
                    preflight.reviewAuthorityProjection,
                    ...preflight.evidence
                ]

            root_preflight_disposition = exact satisfied disposition:
                {
                    kind: "satisfied",
                    obligationId: root_preflight_obligation.obligationId,
                    basisEvidenceIds: [],
                    basisArtifacts: preflight_basisArtifacts
                }

            commit through M2 one exact EstablishPreflightV1:
                {
                    kind: "establish-preflight",
                    repositoryInspection: inspection,
                    baselineAuthority: preflight.baselineAuthority,
                    publicationTarget: preflight.publicationTarget,
                    protocolBundle: preflight.protocolBundle,
                    baselineSemanticSubject: preflight.baselineSemanticSubject,
                    subjectProjection: preflight.subjectProjection,
                    reviewAuthorityProjection: preflight.reviewAuthorityProjection,
                    preflightEvidence: preflight.evidence,
                    rootObligationDisposition: root_preflight_disposition
                }
            snapshot = committed snapshot

            candidate = construct complete CandidateRevision:
                runId = run.runId,
                ordinal = 0,
                parentCandidateId = null,
                materialization = inspection.sealedBaselineCandidate.materialization,
                semanticSubject = snapshot.preflightSemanticSubject,
                producedByRepairIntentId = null
                producedByAssuranceProjectionId = null

            commit through M2 one exact AdmitCandidateV1:
                {
                    kind: "admit-candidate",
                    sealedCandidate: inspection.sealedBaselineCandidate,
                    candidate
                }
            snapshot = committed snapshot

        if snapshot.repositoryInspection != null
           and snapshot.candidates is empty:
            require snapshot.preflightSemanticSubject != null
            require snapshot.preflightProtocolBundle != null
            require snapshot.preflightSubjectProjection != null and intact
            require snapshot.preflightReviewAuthorityProjection != null and intact
            require snapshot.currentCandidate == null
            require root_preflight_obligation is satisfied by the exact retained
                EstablishPreflightV1

            inspection = snapshot.repositoryInspection

            candidate = construct complete CandidateRevision:
                runId = run.runId,
                ordinal = 0,
                parentCandidateId = null,
                materialization =
                    inspection.sealedBaselineCandidate.materialization,
                semanticSubject = snapshot.preflightSemanticSubject,
                producedByRepairIntentId = null
                producedByAssuranceProjectionId = null

            commit through M2 one exact AdmitCandidateV1:
                {
                    kind: "admit-candidate",
                    sealedCandidate: inspection.sealedBaselineCandidate,
                    candidate
                }
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

        require snapshot.currentCandidate != null

        review_authority =
            mechanical_validation.project_candidate_review_authority({
                runId: run.runId,
                candidateMaterialization:
                    snapshot.currentCandidate.materialization
            })

        currentness =
            campaign_authority.resolve_currentness({
                runId: run.runId,
                stateRevision: snapshot.stateRevision,
                candidate: snapshot.currentCandidate,
                candidateLineage: snapshot.candidates,
                registeredCampaigns: snapshot.reviewCampaigns,
                reviewAuthority: review_authority
            })

        if currentness.kind == "campaign-required":
            prerequisites = campaign_authority.verify_reviewer_prerequisites({
                candidate: currentness.candidate,
                semanticSubject: currentness.semanticSubject,
                protocolBundle: currentness.currentProtocolBundle,
                reviewAuthority:
                    require established review_authority
            })

            if prerequisites.kind == "blocked":
                require prerequisites.blockingObligation.runId == run.runId
                require prerequisites.blockingObligation.candidateId ==
                    currentness.candidate.candidateId
                require prerequisites.blockingObligation.reviewCampaignId == null
                require prerequisites.cause.producer == "campaign-authority"
                require prerequisites.cause.resolutionContracts == []

                materialized =
                    recovery_operator.materialize_operational_blocker({
                        kind: "producer-occurrence",
                        runId: run.runId,
                        baseStateRevision: snapshot.stateRevision,
                        producer: "campaign-authority",
                        obligationId:
                            prerequisites.blockingObligation.obligationId,
                        workItemId: null,
                        executionId: null,
                        causeDescriptor:
                            prerequisites.cause.causeDescriptor,
                        resolutionContracts: []
                    })

                committed = commit through M2 atomically:
                    {
                        kind: "establish-operational-blockers",
                        obligationsToAdd: [
                            prerequisites.blockingObligation
                        ],
                        blockers: [
                            materialized.blocker
                        ],
                        basisArtifacts:
                            ordered duplicate-free first-occurrence sequence:
                            [
                                prerequisites.cause.causeDescriptor,
                                ...prerequisites.cause.basisArtifacts
                            ]
                    }
                snapshot = committed snapshot
                require no ReviewCampaign was created

                return OPERATOR-ACTION-REQUIRED projection from snapshot

            campaign = construct exactly one full runner-produced ReviewCampaign(
                logical slot =
                    run.runId,
                    currentness.semanticSubject,
                    currentness.currentProtocolBundle,
                reviewCampaignId = deriveReviewCampaignId(
                    "review-campaign.v1",
                    run.runId,
                    currentness.semanticSubject.selector,
                    currentness.semanticSubject.sha256,
                    currentness.currentProtocolBundle.protocolId,
                    currentness.currentProtocolBundle.sha256
                ),
                provenance = exact current candidate plus exact current full
                    repository authority,
                prerequisites.minimumIndependentReviewers,
                prerequisites.acquisitionMode,
                prerequisites.qualifyingReviewerProfileIds,
                prerequisites.reviewerAcquisitionCandidates,
                prerequisites.evidence
            )

            review_context =
                campaign_authority.construct_review_context({
                    runId: run.runId,
                    candidate: exact campaign production candidate,
                    campaign
                })

            prerequisite_basis =
                construct exact ReviewCampaignPrerequisiteBasisRefV1 from:
                    campaign C
                    exact established ReviewerPrerequisiteResolution P
                    exact review_context R

                set exactly:
                    retryPolicy:
                        P.retryPolicy

                copy with no field transformation, sorting, or normalization:
                    minimumIndependentReviewers
                    acquisitionMode
                    qualifyingReviewerProfileIds
                    reviewerAcquisitionCandidates
                    initialReviewerExecutionInputs
                    evidence

                bind exact:
                    reviewCampaignId
                    candidateId
                    semanticSubject
                    protocolBundle
                    reviewContext

            selected_first_round_candidates =
                M1 derives exact first-round selected acquisition candidates
                from the exact M3 prerequisite basis

            initial_ledger_products =
                M1 supplies:
                    campaign
                    prerequisite_basis
                    exact selected_first_round_candidates
                to the M5 assurance-ledger construction boundary

                M5 returns the exact M5-owned initial obligations/workItems

                for every M5-produced reviewer WorkItem:
                    the cognitive WorkItem's M4 operation retains its exact
                        selected GateAReviewerAcquisitionCandidateV1
                    no WorkItem may be constructed from only profileId while
                        dropping provider, requestModel, identityResolution, or
                        staticallyKnownEffectiveIdentity

                M5 also returns all other protocol-required current-P campaign
                    obligations and non-reviewer WorkItems and all required
                    current-P re-adjudication obligations and WorkItems for
                    stale-protocol findings over the same S

            M1 submits:
                campaign
                prerequisite_basis
                complete initial M5-produced obligations/workItems
            to M2 atomically

            The future M5-A Module Brief closes the exact internal interface and
            ID formulas. Do not invent those formulas before M5-A.

            require later initial-reviewer acquisition WorkItems are added only
                through M5 assurance-ledger deltas after every selected WorkItem
                in the prior round has qualified or entered an existing
                operational/recovery blocker path

            require every M5-added cognitive reviewer WorkItem for a later
                acquisition round binds the exact
                GateAReviewerAcquisitionCandidateV1 from the campaign's exact
                snapshot ReviewCampaignPrerequisiteBasisRefV1

            require no environment/config lookup replaces this binding

            commit campaign + exact prerequisite_basis + complete initial
                M5-produced ledger products through M2 atomically

            continue

        if currentness.kind == "blocked":
            require currentness.blockingObligation.runId == run.runId
            require currentness.blockingObligation.candidateId ==
                snapshot.currentCandidate.candidateId
            require currentness.blockingObligation.reviewCampaignId == null
            require currentness.cause.producer == "campaign-authority"
            require currentness.cause.resolutionContracts == []

            materialized =
                recovery_operator.materialize_operational_blocker({
                    kind: "producer-occurrence",
                    runId: run.runId,
                    baseStateRevision: snapshot.stateRevision,
                    producer: "campaign-authority",
                    obligationId:
                        currentness.blockingObligation.obligationId,
                    workItemId: null,
                    executionId: null,
                    causeDescriptor: currentness.cause.causeDescriptor,
                    resolutionContracts: []
                })

            committed = commit through M2 atomically:
                {
                    kind: "establish-operational-blockers",
                    obligationsToAdd: [
                        currentness.blockingObligation
                    ],
                    blockers: [
                        materialized.blocker
                    ],
                    basisArtifacts:
                        ordered duplicate-free first-occurrence sequence:
                        [
                            currentness.cause.causeDescriptor,
                            ...currentness.cause.basisArtifacts
                        ]
                }
            snapshot = committed snapshot

            return OPERATOR-ACTION-REQUIRED projection from snapshot

        evaluation_context = currentness.context

        require evaluation_context.currentCampaigns
            == complete canonical campaign set after exact M3 merge of:
                already registered campaigns
                plus newly mechanically valid repository observations
            for exact (S, P)
            without candidate/run/repository provenance filtering

        require no registered campaign is forgotten because it was produced
            under another candidate or repository provenance

        require invalid evidence was not silently omitted

        if operational blocker exists:
            return OPERATOR-ACTION-REQUIRED projection

        if semantic blocker exists and no operational blocker exists:
            return DECISION-REQUIRED projection

        work = derive_enabled_work(snapshot)

        before ordinary WorkItem dispatch:
            repair_intent =
                exact enabled current-candidate RepairIntentRef
                or null

            assurance_projection =
                exact unconsumed current-candidate
                    AssuranceRepositoryProjectionRef
                or null

        if repair_intent != null or assurance_projection != null:
            source_candidate = exact snapshot.currentCandidate

            sealed_successor =
                repository_control.apply_exact_candidate_changes_and_seal({
                    runId: run.runId,
                    sourceCandidate: source_candidate,
                    repairIntent: repair_intent,
                    assuranceProjection: assurance_projection
                })

            successor_subject = mechanical_validation.derive_candidate_subject({
                runId: run.runId,
                candidateMaterialization:
                    sealed_successor.sealedCandidate.materialization
            })

            if M6 does not produce a trustworthy subject result:
                admit no successor CandidateRevision
                leave repair/projection unconsumed
                fabricate no CampaignBlocker
                fail invocation outside normal RunnerResult

            successor = construct complete CandidateRevision:
                ordinal = source_candidate.ordinal + 1
                parentCandidateId = source_candidate.candidateId
                producedByRepairIntentId =
                    repair_intent?.repairIntentId or null
                producedByAssuranceProjectionId =
                    assurance_projection?.projectionId or null
                materialization =
                    sealed_successor.sealedCandidate.materialization
                semanticSubject = successor_subject.semanticSubject

            require successor and sealed candidate agree exactly on:
                parentCandidateId
                producedByRepairIntentId
                producedByAssuranceProjectionId
                materialization

            if repair_intent == null and assurance_projection != null:
                require successor.semanticSubject ==
                    source_candidate.semanticSubject ==
                    assurance_projection.semanticSubject
                otherwise fail invocation as implementation/process/integrity
                    failure, admit no candidate, and do not reinterpret as
                    campaign-required

            commit exact successor through M2 AdmitCandidateV1

            after successful admission:
                candidate existence is immutable consumption proof for every
                    non-null repair/projection authority

            continue

        A crash after projection admission but before M7 leaves the exact
        projection authoritative and unconsumed. A crash after M7 sealing but
        before candidate admission replays the same immutable inputs and
        deterministically reproduces the same successor. M2 remains the sole
        consumption enforcer.

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
                    executionRequest: exact CognitiveExecutionRequest,
                    capturedResult: exact CapturedExecutionResult
                })

                require attempt_validation binds the exact execution request,
                    execution, WorkItem, campaign, protocol bundle, role,
                    reviewer profile, prompt, packet, captured output, and
                    runtime evidence

                preserve attempt_validation as a newly validated cognitive attempt

            require no CognitiveAttemptValidationRequest exists for a technical failure

            preparation = assurance_ledger.prepare_complete_delta(
                evaluation_context,
                current authoritative snapshot,
                newly captured results,
                newly known technical failures,
                newly validated cognitive attempts,
                newly admitted artifacts
            )

            require preparation.expectedStateRevision ==
                snapshot.stateRevision

            materializedOperationalBlockers = []

            for each request in preparation.operationalBlockerRequests
            in exact order:
                require request.cause.producer == "assurance-ledger"

                materialized =
                    recovery_operator.materialize_operational_blocker({
                        kind: "producer-occurrence",
                        runId: run.runId,
                        baseStateRevision:
                            preparation.expectedStateRevision,
                        producer: "assurance-ledger",
                        obligationId: request.obligationId,
                        workItemId: request.workItemId,
                        executionId: request.executionId,
                        causeDescriptor: request.cause.causeDescriptor,
                        resolutionContracts:
                            request.cause.resolutionContracts
                    })

                append materialized to materializedOperationalBlockers

            delta = assurance_ledger.finalize_complete_delta({
                preparation,
                materializedOperationalBlockers
            })

            commit one exact AdmitAssuranceLedgerDeltaV1
            using the same expected StateRevision

            if StateRevision becomes stale before commit:
                no materialized blocker becomes authoritative
                sealed M8-B artifacts remain non-authoritative durable material
                reload authoritative snapshot
                rederive preparation
                replay no external effect


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
            require snapshot.repositoryInspection != null

            require snapshot.repositoryInspection.runId ==
                run.runId

            require snapshot.repositoryInspection.baselineAuthority ==
                snapshot.run.initialRepositoryAuthority

            require snapshot.repositoryInspection.publicationTarget ==
                snapshot.run.publicationTarget

            preparation = repository_control.prepare_publication({
                runId: run.runId,
                repositoryInspection: exact snapshot.repositoryInspection,
                candidate: exact candidate,
                qualification: exact qualification,
                target: exact snapshot.run.publicationTarget
            })

            if preparation is blocked:
                require preparation.cause.producer == "repository-control"
                bind only exact already-determined authoritative occurrence
                    anchors for preparation.cause
                materialized = recovery_operator.materialize_operational_blocker(
                    exact preparation.cause + exact anchors + current StateRevision
                )
                commit only materialized.blocker through M2
                continue

            require preparation.transition.relationship == "fast-forward"
            require valid mechanical evidence that:
                transition.predecessor is ancestor-or-equal to transition.successor
                transition.target is exact repository + endpoint + ref
            require preparation.publication.realization ==
                "conditional-ref-update"
                iff transition.predecessor != transition.successor
            require preparation.publication.realization ==
                "already-current"
                iff transition.predecessor == transition.successor

            intent = preparation.publication.intent
            publication_obligation =
                preparation.publication.publicationObligation
            publication_work_item =
                preparation.publication.publicationWorkItem

            require intent.runId == run.runId
            require intent.candidateId == exact candidate.candidateId
            require intent.qualificationId
                == exact qualification.qualificationId
            require intent.transition == preparation.publication.transition

            require publication_obligation.runId == intent.runId
            require publication_obligation.candidateId == intent.candidateId
            require publication_obligation.reviewCampaignId == null

            require publication_work_item.runId == intent.runId
            require publication_work_item.candidateId == intent.candidateId
            require publication_work_item.reviewCampaignId == null
            require publication_work_item.executor == "repository-control"
            require publication_work_item.sourceObligationIds
                == [publication_obligation.obligationId]

            commit through M2 in one atomic EstablishPublicationIntentV1:
                exact intent
                exact publication_obligation
                exact publication_work_item

            snapshot = committed snapshot

            if preparation.publication.realization == "already-current":
                require intent.transition.predecessor == intent.transition.successor
                require zero Execution exists for the exact publication WorkItem

                observation = repository_control.observe_publication_target({
                    runId: run.runId,
                    intent: exact intent,
                    candidate: exact candidate,
                    target: intent.transition.target
                })

                require observation is bound to:
                    exact current PublicationIntent
                    exact candidate
                    exact target
                    exact intended successor

                if observation.observedAuthority != intent.transition.successor:
                    do not confirm
                    do not Arm
                    snapshot = load_authoritative_snapshot(run)
                    continue

                publication_qualification =
                    repository_control.qualify_publication_observation({
                        kind: "already-current",
                        intent: exact intent,
                        candidate: exact candidate,
                        observation
                    })

                if publication_qualification.kind == "blocked":
                    require publication_qualification.cause.producer ==
                        "repository-control"
                    bind only exact already-determined authoritative occurrence
                        anchors for publication_qualification.cause
                    materialized =
                        recovery_operator.materialize_operational_blocker(
                            exact publication_qualification.cause
                            + exact anchors
                            + current StateRevision
                        )
                    commit only materialized.blocker through M2
                    return OPERATOR-ACTION-REQUIRED projection

                require publication_qualification.kind == "confirmed"
                publication_qualification_request = {
                    kind: "already-current",
                    intent: exact intent,
                    candidate: exact candidate,
                    observation
                }

            else:
                require preparation.publication.realization ==
                    "conditional-ref-update"

                publication_execution = authorize exact repository-control Execution
                for preparation.publication.publicationWorkItem

                immediately before publication Arm:
                    revalidate:
                        qualification still effective
                        no new blocker exists
                        exact projected snapshot.publicationIntent still equals intent
                        publication WorkItem still equals the exact publication
                            WorkItem co-admitted with that intent
                        publication obligation is still outstanding
                        exact target ref still equals transition.predecessor
                        transition.successor still equals prepared immutable repository object
                        fast-forward ancestry/equality proof still valid
                        expected StateRevision still current
                        ownership generation still current

                if fresh target-ref revalidation establishes that the target no
                longer equals intent.transition.predecessor:
                    M1 must not Arm the Execution

                    because no Arm occurred, this is not execution uncertainty
                    and does not enter M8 recovery

                    M1 returns to ordinary authoritative orchestration after
                    loading the latest M2 snapshot

                    a later mechanically prepared PublicationIntent may replace
                    the old intent only through the ordinary
                    EstablishPublicationIntentV1 admission rules

                    the historical intent, WorkItem, obligation, and any
                    authorized-but-unarmed Execution remain retained

                    continue

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
                        authorize only the existing PNE-governed continuation
                        continue

                    require recovery.resolution.classification == PROVEN-COMPLETED
                    require recovery.resolution.recoveredOutcome.kind == "captured"

                    publication_observation =
                        recovery.resolution.recoveredOutcome.value
                    publication_observation_source = "recovered"

                else:
                    publication_observation = capture.value
                    publication_observation_source = "direct"
                    commit through M2 the exact AdmitExecutionOutcomeV1:
                        captured publication_observation

                publication_qualification =
                    repository_control.qualify_publication_observation({
                        kind: "executed-publication",
                        intent: exact intent,
                        candidate: exact candidate,
                        executionResult: publication_observation
                    })

                if publication_qualification.kind == "blocked":
                    require publication_qualification.cause.producer ==
                        "repository-control"
                    bind only exact already-determined authoritative occurrence
                        anchors for publication_qualification.cause
                    materialized =
                        recovery_operator.materialize_operational_blocker(
                            exact publication_qualification.cause
                            + exact anchors
                            + current StateRevision
                        )
                    commit only materialized.blocker through M2
                    return OPERATOR-ACTION-REQUIRED projection

                if publication_observation_source == "recovered" and
                   publication_qualification.kind == "not-applied":
                    fail invocation as implementation/process/integrity failure
                    do not construct or submit the publication-qualification
                        AdmitPublicationObservationQualificationV1 mutation
                    do not append PublicationNonApplicationRef

                publication_qualification_request = {
                    kind: "executed-publication",
                    intent: exact intent,
                    candidate: exact candidate,
                    executionResult: publication_observation
                }

            require publication_qualification.kind is one of:
                "confirmed"
                "not-applied"

            if publication_qualification.kind == "not-applied":
                require publication_qualification_request.kind ==
                    "executed-publication"
                commit through M2 the exact
                    AdmitPublicationObservationQualificationV1 request/result
                    basis and PublicationNonApplicationRef
                snapshot = committed snapshot
                reload authoritative snapshot
                perform a fresh ordinary publication preparation
                continue

            require publication_qualification.kind == "confirmed"
            require publication_qualification.confirmation.transition == intent.transition
            require publication_qualification.publishedView.publicationConfirmationId
                == publication_qualification.confirmation.publicationConfirmationId
            require publication_qualification.publishedView.target
                == intent.transition.target
            require publication_qualification.publishedView.authority
                == intent.transition.successor
                by both commit SHA and tree SHA

            commit through M2 one atomic
                AdmitPublicationObservationQualificationV1:
                    exact publication_qualification_request
                    exact publication_qualification
                    exact confirmation
                    exact publishedView
                    exact satisfied disposition for publication_obligation

            post_validation = mechanical_validation.post_publication({
                runId: run.runId,
                publishedView: publication_qualification.publishedView
            })

            require post_validation.requestKind == "post-publication-integrity"
            require post_validation.publicationConfirmationId
                == publication_qualification.confirmation.publicationConfirmationId
            require post_validation.target
                == publication_qualification.publishedView.target
            require post_validation.validatedAuthority
                == publication_qualification.publishedView.authority
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

An incomplete bootstrap before preflight establishment is resumed only after
the exact root preflight obligation is still outstanding and no
`OperationalBlocker` remains outstanding. Resolving an operational blocker does
not itself satisfy the preflight obligation, establish repository authority,
create the initial candidate, or authorize normal campaign progression. M1 must
re-run repository inspection, M6 subject derivation, M6 review-authority
projection, and M3 preflight interpretation. If preflight blocks again, the
newly established exact blockers are committed and the run remains
`OPERATOR-ACTION-REQUIRED`.

Subject derivation failure before `EstablishPreflightV1` creates no
authoritative baseline fact, creates no `CampaignBlocker`, leaves the root
preflight obligation outstanding, and fails the invocation outside normal
`RunnerResult`. A later invocation may re-run repository inspection because
baseline authority was never established.

After the unique `EstablishPreflightV1` but before C0 admission, the legal
incomplete-bootstrap state is resumed from exact retained preflight authority.
M1 loads the exact retained `RepositoryInspectionRef`, verifies all retained
preflight projection fields and `ArtifactRef` values, constructs C0 from the
exact retained sealed baseline candidate and `preflightSemanticSubject`, and
commits exact `AdmitCandidateV1`. M1 does not rerun repository inspection,
reread mutable `repositoryPath`, select another baseline, rederive `S` from
mutable state, select another protocol, or replace the sealed baseline
candidate. Missing, corrupt, or contradictory retained subject/review
projections are retained-authority integrity failure and produce no normal
`RunnerResult`.

After an accepted operator `request-operational-recheck` resolution, ordinary
orchestration may invoke repository inspection again against the current
operational repository state under the existing M8-B and M2 blocker-disposition
rules. M1 does not create a retry counter, reuse prior mutable repository
observations, or convert a prior cause descriptor into repository truth. Each
new inspection returns either `observed` or one fresh producer cause under the
current exact state.

The initial-run and preflight-establishment order is therefore always:

```text
M7 inspect repository and seal baseline candidate
→ M6 derive exact S from the sealed baseline candidate materialization
→ M6 project exact hostile-review authority from the same materialization
→ M3 preflight interpretation
→ M2 EstablishPreflightV1 retaining S/P mechanical witnesses
→ M2 AdmitCandidateV1(C0)
```

M1 owns this sequencing. M6 does not call M3. M3 does not call M6. Neither
writes M2 directly.

There is no separate initial-candidate sealing operation after baseline
authority becomes authoritative, and no authoritative StateRevision may expose
baseline authority without its already-sealed reconstructible repository basis
and exact C0 source material.

The orchestrator never creates semantic authority.

It only coordinates work already permitted by the current exact authority and admitted durable facts.

## 38. Dependency inventory

### Runtime dependencies/boundaries

```text
Node.js >= 22.19.0
  required process/runtime platform

@earendil-works/pi-ai@0.99.2
  TypeScript ESM in-process package
  consumed only by M4 through the explicit Pi M4 adapter
  public execution surface = Models.streamSimple(...)
  Pi source commit = 005af57d88ee23b33778f343a9595b32e67ff788
  exact contract deferred to Issue #31 Pi M4 Dependency Contract

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
       candidate/run/full repository authority when runner-produced, or to null
       runner/candidate plus exact repository_commit when repository-imported,
       and always to exact S and exact P; currentness is independently derived
       from (S, P).
GI-03  CandidateRevision is constructed only from a sealed candidate
       materialization plus its exact M6 mechanically derived semantic subject
       and is immutable after admission.
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
       call_id binds the exact Pi M4 adapter call. A progression-superseded
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

GI-72  Every authoritative PublicationIntent is admitted atomically with exactly
       one publication obligation and exactly one repository-control
       PublicationIntent WorkItem bound to that exact intent.

GI-73  When a later safe PublicationIntent becomes effective for the same exact
       candidate/qualification transition, the prior publication obligation is
       superseded append-only by the replacement publication obligation; the
       prior intent, WorkItem, and Executions remain immutable historical
       state.

GI-74  M2 may Arm a repository-control publication Execution only when its
       WorkItem is the exact WorkItem co-admitted with the currently projected
       PublicationIntent and its exact publication obligation remains
       outstanding.

GI-75  Publication-intent replacement never bypasses an already potentially-
       effectful publication Execution. Once a publication Execution has
       crossed Arm, its external-effect disposition must first be established
       through the existing outcome/recovery/progression rules before another
       publication intent may obtain side-effect authority.

GI-76  Initial repository authority is never admitted before M7 has already
       sealed the exact RepositoryInspectionRef, reconstructible baseline Git
       basis, and exact sealed baseline candidate that support it.

GI-77  M7 observes repository/Git facts, M3 interprets the immutable inspection
       under accepted authority, and M2 alone admits the resulting
       baseline/target/protocol. A mutable repository path is never retained
       authority.

GI-78  Publication predecessor is observed by M7 from the exact publication
       target; no caller supplies or selects the predecessor used by
       PublicationIntent.

GI-79  If predecessor equals successor before Arm, publication realization is
       already-current: no publication Execution exists, no Arm occurs, and
       exact read-only observation is required for confirmation.

GI-80  Every PublicationConfirmation atomically satisfies the exact
       publication obligation co-admitted with its PublicationIntent.

GI-81  PublicationNonApplicationRef positively establishes only that one exact
       armed publication target-ref mutation was not applied. It is distinct
       from PROVEN-NOT-EXECUTED and does not itself authorize retry. It may be
       produced only from a direct terminal M7 capture introduced by
       AdmitExecutionOutcomeV1; a recovery-derived captured outcome can never
       produce this fact.

GI-82  A later PublicationIntent may supersede an armed prior publication
       intent only after every relevant prior armed Execution has an exact safe
       effect disposition: PROVEN-NOT-EXECUTED or PublicationNonApplicationRef.

GI-83  After publication Arm, observing the intended successor never enters the
       already-current shortcut; it belongs to the existing outcome/recovery
       lifecycle of the armed Execution.

GI-84  For every non-C0 candidate construction, M7 consumes the exact
       authoritative nullable RepairIntentRef and
       AssuranceRepositoryProjectionRef selected for the exact source
       CandidateRevision, requires at least one of them to be non-null, applies
       only the exact RepairIntent.approvedPatch when repair is present and only
       the exact AssuranceRepositoryProjection.projection when assurance
       projection is present, and returns a sealed candidate bound to the same
       source candidate and the exact nullable repair/projection provenance.

GI-85  One RepairIntent may produce at most one CandidateRevision. The admitted
       CandidateRevision carrying that RepairIntentId is the append-only proof
       of consumption; no mutable consumed flag may authorize or suppress
       repair reuse.
GI-86  Every non-C0 candidate is produced by RepairIntent,
       AssuranceRepositoryProjection, or both.
GI-87  Assurance-only candidate construction preserves the exact M6-derived
       semantic subject of parent and projection.
GI-88  Assurance projection cannot modify judging authority.
GI-89  M6 supplies complete immutable repository-review artifact closure; M3
       preserves it exactly and M5 consumes it only through authorityEvaluation.
GI-90  M5 does not scan mutable repository state or mutate candidate material.
GI-91  M7 applies assurance projection mechanically and interprets no assurance
       meaning.
GI-92  One assurance projection produces at most one candidate and at most one
       unconsumed projection exists per source candidate.
GI-93  Candidate review readiness is null while the current candidate has an
       unconsumed assurance projection.
GI-94  M5 and M7 non-recovery causes become OperationalBlockers only through
       M8-B; M2 alone admits them.
GI-95  Combined repair/projection path sets are disjoint.
GI-96  Reviewer-profile registry membership is eligibility, not execute-all
       authority. Initial-reviewer WorkItems are derived only through the
       current P acquisition policy.
GI-97  Reviewer acquisition is independent of finding content, semantic
       favorability, execution latency, and scheduler completion order.
GI-98  A qualified reviewer whose effective identity duplicates an already-
       counted identity remains complete evidence but adds no independent-
       reviewer count.
GI-99  Automatic profile expansion is permitted after qualified identity
       collision but never as a substitute for operational retry exhaustion of
       an already-selected WorkItem.
GI-100 If the current P eligible pool is exhausted after qualified reviews and
       the effective independent-reviewer minimum remains unmet, M5 emits exact
       assurance-domain non-recovery cause material for M8-B; no
       DECISION-REQUIRED meaning is invented.
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

Immediately before every external side effect, current effective permission and current write authority are revalidated. Before publication, the exact target ref, M7-observed predecessor, intended successor, and authorized fast-forward ancestry/equality relation are all revalidated.

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

### CP-15 — Deterministic minimum-effective reviewer acquisition

Current P owns the sole total profile acquisition order. M3 proves optimistic
static feasibility and returns the exact ordered qualifying candidate basis.
M1 selects candidates for the first round from that basis. M5 constructs the
protocol-derived assurance obligations and WorkItems for those selected
first-round candidates and owns both candidate selection and WorkItem
construction for every later round. M5 derives a later round only after a
successful prior round establishes exact qualified receipt identities.

Each round selects at most the current effective-identity deficit. Statically
known duplicate pinned identities are skipped within the round or against
already counted identities. Provider-reported identities are never guessed or
pre-collapsed. Every selected WorkItem becomes required campaign work, and its
retry exhaustion never authorizes automatic profile substitution.

Qualified duplicate effective identities remain complete evidence. They may
cause expansion to the next protocol-ordered eligible profile. Acquisition is
independent of findings, semantic favorability, execution timing, and scheduler
completion order. Once the effective minimum is established, no extra initial
reviewer is acquired. Pool exhaustion below the minimum routes exact M5
non-recovery cause material to M8-B and `OPERATOR-ACTION-REQUIRED`, with no
same-run resolution contract.

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
Pi M4 Dependency Contract
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
how cognitive WorkItem, runner Execution, hostile-review receipt, receipt attempt, Pi M4 adapter call, and provider transport attempt identities map without collapse
how M4 capture reaches existing Python validation through M6 and then M5 without reimplementation
how pre-receipt attempt history becomes one complete schema-v3 receipt only after qualification
where `@earendil-works/pi-ai` and the explicit Pi M4 adapter are allowed
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
