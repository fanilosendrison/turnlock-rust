---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "construction-admission-authority"
domain: "turnlock-rust-formal-assurance"
severity: "strict"
name: "Gate A protocol v8 SemanticAdmission authority and execution fencing"
---

# Gate A protocol v8 SemanticAdmission authority and execution fencing

## Status and authority

This document is the C3 construction closure for protocol-v8 work authorized by
ADR-056 and constrained by the published C1 and C2 construction closures.

It is a non-protocol-authoritative construction artifact.

It closes the authoritative and operational semantics required to ensure that
one exact logical semantic question cannot be model-shopped through concurrent,
replacement, crash-recovery, cross-run or cross-root execution paths.

Authority remains:

```text
docs/specification/turnlock-spec.md

accepted ADRs

especially ADR-055 and ADR-056

docs/formal/gate-a-protocol-v8-semantic-question-contract-catalog.md

docs/formal/gate-a-protocol-v8-semantic-identity-algebra.md

accepted M2/M4/M8 execution and recovery construction
```

This document MUST NOT:

```text
change TURNLOCK product semantics

change Gate A semantic subject S

change a C1 SemanticQuestionContract

change C2 QLEK or SemanticAdmission identity

activate protocol v8

select SQL table names

select the physical QLEK lock primitive

define packet/receipt schemas

define concrete SemanticFact predicates

define CandidateView construction

create a second recovery system

weaken M4 MAYBE-SENT semantics

reinterpret historical P1-P7 evidence
```

If implementation or later construction would require choosing between
materially different semantic meanings rather than mechanically refining this
design:

```text
STOP
→ decision-required
→ accepted ADR
→ resume from earliest affected stage
```

# C3 construction boundary

C3 closes:

```text
coherent Authoritative History semantic-admission namespace

Admission : QLEK ⇀ SemanticCandidate

single-assignment admission authority

QLEK-bound semantic Execution authority

pre-dispatch admission fencing

semantic sampling-hazard semantics

replacement-safety semantics

origin execution/evidence binding

crash/restart semantics

completion-to-admission reconciliation

cross-domain semantic-history reconciliation

admission conflict semantics

semantic consumption boundary
```

C3 does NOT close:

```text
concrete SQL relations
physical locks
runtime public APIs
packet or receipt schemas
fact predicate catalog
qualification reducers
CandidateView construction
module-level implementation signatures
executable TLA+ files
```

Those belong to later construction stages.

# Fundamental authority split

Protocol v8 distinguishes exactly:

```text
SemanticAdmission
```

from:

```text
live AdmissionAuthority
```

`SemanticAdmission` is durable semantic truth.

`AdmissionAuthority` is operational coordination authority permitting at most
one lawful semantic-execution trajectory to approach the dispatch boundary for
one unresolved QLEK.

AdmissionAuthority is NOT:

```text
a SemanticFact
part of QLEK
part of SemanticAdmissionId
a qualification result
an execution receipt
a root-local ownership fact
```

# Coherent Authoritative History namespace

For one coherent Authoritative History domain `H`, protocol v8 exposes one
logically shared admission namespace:

```text
Admission_H : QLEK ⇀ SemanticCandidate
```

All GateARuns that may observe or reuse the same Turnlock semantic admissions in
that coherent domain consult this same logical namespace.

Admission authority MUST NOT be scoped by:

```text
GateARunId
ReviewCampaignId
evidence root
supplement root
repository projection path
provider
model
WorkItemId
ExecutionId
```

No coherent-domain identity is added to QLEK.

The exact physical realization of the coherent domain remains deferred.

# Minimum durable C3 primitive set

C3 requires only these conceptual durable primitive commitments:

```text
AdmissionAuthorityGrant(K, generation)

SemanticExecutionBinding(E, K)

SemanticArmBinding(E, K, generation)

SemanticAdmission(K, V)

ExecutionEvidenceOf(E, SemanticAdmission(K,V))

SemanticAdmissionConflict(K, A1, A2)
```

C3 MUST NOT introduce mutable semantic status roots such as:

```text
QLEKStatus
AdmissionPendingStatus
CurrentSemanticExecution
SemanticExecutionStatus
ConsumedFlag
QualificationStatus
```

The relevant state is derived from append-only authoritative commitments plus
accepted M2/M4/M8 history.

# AdmissionAuthority generation

For one coherent coordination epoch and exact QLEK `K`, issued generations are
strictly monotone:

```text
g1 < g2 < g3 < ...
```

A durable authority grant is conceptually:

```text
AdmissionAuthorityGrant {
  qlek: K
  generation: g
}
```

Generation is operational fencing state.

It MUST NOT affect:

```text
QLEK
SemanticAdmissionId
SemanticFact identity
semantic candidate value
qualification identity
```

A live authority handle is conceptually:

```text
AdmissionAuthorityHandle(K, g)
```

It is not semantic history.

The implementation mechanism providing live exclusion remains deferred.

# Effective live authority

At most one live authority capable of reaching Semantic Arm may exist for one
exact K in one coherent coordination epoch.

Live exclusion and generation fencing have distinct roles:

```text
live exclusion
→ prevents normal concurrent acquisition

generation fencing
→ prevents a stale former holder from Arm after authority transfer
```

A stale generation MUST NOT Arm.

# Generation scope across disconnected domains

Generation numbers are comparable only inside one coherent coordination epoch.

Two physically disconnected authority domains may both independently issue:

```text
K, generation = 1
```

without those grants denoting the same authority.

When previously disconnected semantic histories are reconciled:

```text
all pre-reconciliation live AdmissionAuthority handles
become ineffective in the merged coherent domain
```

No pre-merge handle may Arm after merge.

Any later Arm requires authority issued after semantic-history reconciliation.

QLEK identity remains unchanged.

# SemanticExecutionBinding

Every protocol-v8 semantic Execution governed by C1 has exactly one immutable
logical-question binding:

```text
SemanticExecutionBinding(E, K)
```

Require:

```text
one Execution
→ zero or one QLEK

once bound
→ never retargeted
```

A semantic Execution MUST NOT be created authoritatively in a state where its
QLEK binding is absent or deferred.

For a newly created protocol-v8 semantic Execution:

```text
Execution creation
+
SemanticExecutionBinding(E,K)
```

must be one atomic authoritative transition.

No authoritative intermediate state is legal where:

```text
Execution E exists
but no exact K is known
```

# Generation is not part of SemanticExecutionBinding

`SemanticExecutionBinding(E,K)` does not contain the current admission-authority
generation.

An unarmed exact Execution may survive authority handoff:

```text
E → K under g1

crash / relinquish

fresh authority g2

same E → K
```

The immutable semantic question does not change.

Only operational dispatch authority changes.

# Existing unarmed trajectory

For one exact K, a coherent domain may have at most one still-dispatchable
unarmed semantic Execution trajectory.

If one exists:

```text
resume/revalidate that exact E
```

rather than creating a sibling semantic trajectory.

A different GateARun requiring the same K does not gain authority to create E2
merely because E1 belongs to another run.

Cross-run occurrence identity is provenance.

# Retiring an unarmed Execution

An unarmed semantic Execution may cease to block a future semantic trajectory
only when accepted authoritative history establishes that it is definitively
non-dispatchable before Arm.

Examples may include accepted orchestration supersession or other exact
pre-Arm progression termination.

Require:

```text
Arm(E) absent
```

No M8 PROVEN-NOT-EXECUTED proof is required for a never-Armed Execution because
M4 external execution is impossible before successful Arm.

# Semantic Arm

For a protocol-v8 semantic Execution, the exact M2 Arm transition and its
semantic QLEK/fence binding are one authoritative linearization point.

Conceptually:

```text
SemanticArmBinding(E, K, g)
```

is established atomically with the normal M2 Arm for E.

A conforming realization MUST NOT permit:

```text
M2 Arm(E)
COMMIT

crash

SemanticArmBinding(E,K,g) missing
```

or the inverse partial state.

Successful Semantic Arm establishes durable semantic-sampling hazard for exact K.

# Semantic Arm preconditions

Immediately before the atomic Semantic Arm transition, revalidate at least:

```text
SemanticExecutionBinding(E,K) exists

E has no prior Arm

exact current effective generation for K == g

the caller holds effective AdmissionAuthority(K,g)

Admission(K) is absent

no SemanticAdmissionConflict(K) exists

no protocol-valid completion for K awaits admission reconciliation

no incompatible sampling hazard for K exists

E is the exact lawful unarmed trajectory selected for K

all normal M2 Arm preconditions hold
```

Candidate-bound currentness is an additional C5 authorization requirement and is
not defined by C3.

If any precondition fails:

```text
NO Arm
NO provider dispatch
```

# Arm remains the side-effect permission linearization point

C3 preserves the existing M2 meaning:

```text
AUTHORIZED-NOT-DISPATCHED
→
POSSIBLY-DISPATCHED
```

Successful Arm is still the runner's side-effect permission linearization point.

C3 does NOT create another semantic Arm phase after M2 Arm.

# M4 effect fence remains authoritative

C3 preserves exact existing M4 semantics:

```text
no successful M2 Arm
→ provider unreachable

Arm but no durable MAYBE-SENT
→ provider still unreachable

durable MAYBE-SENT
→ provider may have become reachable
```

C3 MUST NOT reinterpret MAYBE-SENT as:

```text
provider definitely received request
provider definitely executed
provider definitely completed
provider definitely did not execute
```

# Live authority after Arm

After durable Semantic Arm, safety MUST NOT depend on continued possession of a
live AdmissionAuthority handle.

A process may:

```text
crash
lose an OS lock
lose run ownership
terminate
```

without making K reusable.

The durable Arm/hazard history becomes the safety authority.

Physical live-lock release after Arm is an implementation concern.

# Semantic sampling hazard

Define conceptually:

```text
SemanticSamplingHazard(E,K)
```

when:

```text
SemanticExecutionBinding(E,K)

AND E has been lawfully Armed

AND semantic-hazard clearance for E has not been positively established
```

Hazard is derived.

It is not persisted as an independent mutable status.

# SemanticHazardCleared versus ReplacementAuthorized

C3 distinguishes exactly:

```text
SemanticHazardCleared(E)
```

from:

```text
ReplacementAuthorized(E)
```

`SemanticHazardCleared(E)` means:

```text
no protocol-valid SemanticCandidate can still emerge from E
```

`ReplacementAuthorized(E)` means:

```text
semantic hazard is cleared

AND

the exact protocol/orchestration/retry authority permits another Execution
```

Therefore:

```text
ReplacementAuthorized(E)
→ SemanticHazardCleared(E)
```

but NOT the reverse.

# Semantic-hazard clearance

For an Armed semantic Execution, semantic hazard may be cleared only by exact
positive authority proving no protocol-valid semantic candidate can still emerge.

C3 accepts these categories:

```text
PROVEN-NOT-EXECUTED

exact terminal technical failure positively proving that
no completed semantic response exists

exact deterministic protocol-invalid completed response
for which no protocol-valid semantic candidate exists in that response
```

A never-Armed definitively non-dispatchable Execution is also non-hazardous.

The following NEVER clear semantic hazard merely by themselves:

```text
timeout

process death

missing heartbeat

missing response

MAYBE-SENT

M8 unknown

M8 UNRESOLVABLE

operator acknowledgement

ExecutionProgressionSupersessionRef after Arm

absence of Admission(K)

candidate staleness

run termination

evidence-root change
```

# Replacement authorization

Cleared hazard does not automatically authorize another Execution.

Replacement additionally requires all exact existing outer authority, including
where applicable:

```text
retry authorization

M2 attempt limits

WorkItem legality

source obligation legality

protocol retry rules

current progression legality
```

C3 does not redefine those limits.

# PROVEN-NOT-EXECUTED

PNE clears semantic hazard because accepted M4/M8 authority proves the external
cognitive effect boundary was not crossed.

PNE permits only the exact existing lawful replacement path.

PNE MUST NOT be interpreted as:

```text
unlimited retry

retry with another model

retry after exhausted attempt limits

operator-selected resampling
```

# M4 PNE / MAYBE-SENT refinement condition

The C3 abstract model relies on the accepted M4 refinement guarantee that:

```text
M4-A MAYBE-SENT publication
```

and:

```text
M4-B positive non-execution observation
```

for one call are serialized by the accepted M4 call-lock and ownership-handoff
contract.

Cross-session recovery occurs only after prior live M4 execution authority has
been shut down or the prior process has terminated.

Therefore a conforming refinement MUST NOT permit:

```text
PNE established
then
old same-Execution invocation later creates MAYBE-SENT
```

# UNRESOLVABLE

For a QLEK-bound protocol-v8 semantic Execution:

```text
UNRESOLVABLE
```

means:

```text
ordinary accepted recovery mechanism is exhausted
```

It does NOT mean:

```text
no semantic candidate can exist
```

Therefore:

```text
UNRESOLVABLE
→ operationally terminal under existing M2 recovery projection
→ semantic sampling hazard remains
→ no fresh semantic dispatch for same K
```

With the currently accepted M4 backend:

```text
MAYBE-SENT
+
no TERMINAL
+
no qualified post-crash provider-response observation
→ UNRESOLVABLE
```

may leave the same K blocked indefinitely.

This is a lawful safety-over-liveness outcome.

# Operator uncertain replacement prohibition

Existing generic M8 operator semantics may authorize uncertain replacement for
some external effects.

That generic authority MUST NOT be accepted for an exact P8 QLEK-bound semantic
Execution while semantic hazard remains.

For such an Execution:

```text
authorize-uncertain-execution-replacement
```

MUST NOT create a replacement semantic Execution for the same K.

Operator acknowledgement cannot override protocol-v8 single-sample semantics.

An operator cannot turn:

```text
prior model may have produced a semantic candidate
```

into lawful resampling authority.

# Progression supersession

`ExecutionProgressionSupersessionRef` changes progression authority.

It does NOT establish:

```text
PROVEN-NOT-EXECUTED

no completed response

no semantic candidate

semantic hazard clearance
```

For an Armed E:

```text
progression supersession
→ E may cease to be current
→ E may leave ordinary active progression projections
→ its semantic hazard remains unless separately cleared
```

A late lawful completion does not reverse supersession and does not make E
current again.

# Completion truth

A semantic completion becomes authoritative only through accepted durable
execution evidence.

Unreferenced CAS bytes are not semantic completion authority.

In particular:

```text
raw/CAS blob exists
but exact accepted M4 terminal linkage does not exist
```

does NOT establish:

```text
SemanticCandidate
Admission
PNE
replacement safety
```

# Deterministic semantic candidate reconstruction

For an authoritative captured completion, deterministic protocol/structural
validation produces exactly one of:

```text
protocol-valid SemanticCandidate V

protocol-invalid
```

Protocol-valid means only that V belongs lawfully to the output domain of the
exact SemanticQuestionContract.

It does NOT mean:

```text
qualified
correct
accepted for progression
```

# Mandatory completion-to-admission reconciliation

If authoritative history establishes:

```text
exact QLEK-bound Execution E

+

exact protocol-valid completion V
```

then the exact semantic history MUST reconcile:

```text
Admission(K,V)
```

The runner MUST NOT:

```text
discard V

wait for a nicer answer

change model

change prompt

sample another answer for K

ignore V because current progression no longer wants it
```

# Crash after validation before Admission

A protocol-valid candidate does not require a mutable "pending semantic
candidate" record merely to survive crash.

The exact authoritative completion and deterministic protocol validation are
sufficient to reconstruct V.

Therefore:

```text
protocol-valid completion durable
+
Admission(K) absent
```

is a legal incomplete crash state.

It creates a mandatory reconciliation obligation.

It MUST NOT authorize another semantic execution.

# SemanticAdmission

The durable semantic commitment is conceptually:

```text
SemanticAdmission {
  qlek: K

  semanticCandidate: V

  semanticAdmissionId:
    exact C2 SemanticAdmissionId(K,V)
}
```

Admission identity contains no execution/provenance identity.

# Origin evidence

Every native SemanticAdmission MUST have at least one exact lawful origin witness
conceptually equivalent to:

```text
ExecutionEvidenceOf(
  exact Execution E,
  exact SemanticAdmission(K,V)
)
```

The witness must establish enough exact authority to reconstruct:

```text
SemanticExecutionBinding(E,K)

lawful Semantic Arm(E,K,g)

exact qualifying execution/protocol attempt

exact sealed completion/raw evidence

deterministic semantic candidate V

Admission(K) == V
```

Exact serialization belongs to C6.

# Admission and first origin witness atomicity

For the first native admission of exact K:

```text
SemanticAdmission(K,V)

+

first exact ExecutionEvidenceOf witness
```

must be one atomic authoritative transition.

A state is invalid if:

```text
Admission(K,V) exists
but no lawful origin witness exists
```

# Additional provenance witness

If the same exact semantic admission is later proven by another exact lawful
execution:

```text
same K
same V
```

retain:

```text
one SemanticAdmission(K,V)

+

multiple exact origin witnesses
```

Do NOT create another semantic admission.

# Single-assignment mutation

For exact K and candidate V:

```text
Admission(K) absent
→ establish Admission(K,V)

Admission(K) == V
→ semantic convergence
→ optionally add missing lawful provenance witness

Admission(K) == V1
and incoming V2 != V1
→ SemanticAdmissionConflict
→ no winner
```

# SemanticAdmissionConflict

A conflict must be exact and reconstructible.

Conceptually:

```text
SemanticAdmissionConflict {
  qlek: K

  admissionA:
    exact Admission(K,V1)

  admissionB:
    exact incompatible Admission(K,V2)
}
```

Require:

```text
V1 != V2
```

Conflict resolution by:

```text
first-wins
latest-wins
current-run-wins
majority
model preference
resampling
```

is forbidden.

No currently accepted authority defines a winner.

# Conflict effect

For exact conflicted K:

```text
no fresh semantic dispatch

no semantic consumption

no automatic qualification

no automatic winner
```

until separately accepted future authority explicitly defines otherwise.

# Cross-run admission reuse

If exact Admission(K,V) already exists in the coherent domain:

```text
another GateARun requiring K
→ reuse exact Admission(K,V)
→ no model dispatch for K
```

The original execution receipt remains origin evidence where its historical
provenance places it.

The consuming run/root does not become owner of that receipt.

# Semantic consumption boundary

A newly produced semantic candidate MUST NOT be consumed before durable
SemanticAdmission commit.

The normal native pipeline is:

```text
raw completion

↓ deterministic protocol validation

SemanticCandidate V

↓ atomic admission + first origin witness

SemanticAdmission(K,V)

↓ semantic consumers / qualification
```

# ConsumableAdmission

For ordinary native coherent-domain operation, an unconflicted Admission is
consumable after its lawful origin completion has reconciled.

Cross-domain merge requires a stronger derived predicate.

Define conceptually:

```text
ConsumableAdmission(K)
```

as:

```text
Admission(K) exists

AND no SemanticAdmissionConflict(K)

AND no unreconciled pre-existing semantic sampling hazard for K remains
```

Semantic consumers MUST require `ConsumableAdmission(K)`.

# Unreconciled sampling hazard

After cross-domain reconciliation, an Armed E for K remains an unreconciled
hazard unless one of these holds:

```text
SemanticHazardCleared(E)

OR

E has exact protocol-valid completion V
AND Admission(K) == V
AND exact origin witness reconciliation is complete
```

Thus an imported admission cannot be consumed while a pre-existing armed
Execution may still reveal a conflicting semantic candidate.

# Candidate staleness

Candidate currentness is progression authorization, not semantic history.

If candidate-bound K for CandidateRevision C17 was lawfully dispatched while
C17 was current and C18 later becomes current:

```text
protocol-valid completion for old K_C17
→ MUST still be reconciled into Admission(K_C17,V)
```

The old admission does NOT thereby satisfy a new candidate target.

The exact new-candidate applicability rule remains C5.

# Historical superseded execution completion

Semantic completion reconciliation may consume exact lawful historical execution
evidence even when that Execution has lost progression authority.

A progression-superseded E does not become current again.

C3 requires:

```text
historical lawful E
+
exact existing SemanticExecutionBinding(E,K)
+
exact lawful prior Arm
+
exact accepted durable terminal evidence
+
deterministic protocol-valid V
→ semantic Admission reconciliation remains lawful
```

This does not create another recovery system and does not recall the provider.

The exact synchronized M2/M4/M6 API path belongs to C9.

# Current-backend UNRESOLVABLE late-response rule

Under the currently accepted M4 recovery contract, UNRESOLVABLE is reached where
no qualified post-crash provider-response lookup remains.

Therefore the current construction MUST NOT invent:

```text
UNRESOLVABLE
→ magical later provider lookup
```

K remains blocked.

If a future accepted recovery authority establishes an exact lawful late
terminal observation mechanism, any protocol-valid completion thereby
authoritatively established must still obey this C3 admission-reconciliation
semantics.

Such future recovery authority is not introduced by C3.

# Crash/restart matrix

Every crash boundary has an exact semantic rule.

## Before AdmissionAuthority grant commit

```text
no grant exists
→ normal later acquisition
```

## After grant, before semantic Execution creation

```text
historical grant remains
no Execution exists
→ later acquisition may issue a newer generation after complete recheck
```

## During semantic Execution creation/binding transition

The transition is atomic.

After crash exactly one holds:

```text
neither E nor binding exists

OR

both E and SemanticExecutionBinding(E,K) exist
```

No partial state.

## After bound E, before Arm

```text
provider effect impossible
→ later authority may resume same E
```

Do not create a sibling still-dispatchable unarmed trajectory.

## During prepare

Use exact existing M4 PREPARED semantics.

Preparation causes no cognitive external effect.

## Before Semantic Arm commit

```text
no Arm
→ provider impossible
```

## During Semantic Arm

Semantic Arm is atomic with M2 Arm and K/g binding.

After crash exactly one holds:

```text
no Arm

OR

complete durable Semantic Arm(E,K,g)
```

## After Arm before MAYBE-SENT

```text
durable semantic hazard exists
→ no fresh sampling
→ existing M4-B may prove PNE
```

## After MAYBE-SENT

```text
never replay same E
→ recovery only
→ no fresh sample while hazard remains
```

## After TERMINAL-DURABLE before M2 terminal projection

```text
reconstruct same exact M4 terminal truth
→ no provider replay
```

## After captured response before deterministic protocol validation

```text
rerun deterministic protocol validation on exact retained completion
→ no provider replay
```

## After protocol-valid V before Admission commit

```text
reconstruct exact V
→ mandatory Admission reconciliation
→ no fresh sample
```

## During Admission transition

Admission + first witness commit atomically.

Crash exposes:

```text
before transition
OR
after complete transition
```

## After Admission

```text
reuse Admission
→ same K never dispatches again
```

# Acquire/check/recheck algorithm

Conceptually, `AcquireAdmissionAuthority(K)` performs:

```text
1. identify exact K

2. inspect Admission(K)

3. inspect SemanticAdmissionConflict(K)

4. inspect authoritative protocol-valid completions awaiting admission

5. inspect every semantic Execution bound to K

6. inspect unresolved sampling hazards

7. inspect existing unarmed semantic trajectory

8. acquire exclusive live K coordination

9. RECHECK items 2 through 7 under the exclusive acquisition

10. if Admission(K) exists:
        return reuse
        issue no generation

11. if conflict exists:
        fail closed
        issue no generation

12. if protocol-valid completion awaits admission:
        route to semantic reconciliation
        issue no generation

13. if any unresolved sampling hazard remains:
        route to recovery/reconciliation/blocking
        issue no generation

14. if a lawful existing unarmed trajectory exists:
        retain that exact E as the only resumable trajectory

15. issue fresh generation g

16. append AdmissionAuthorityGrant(K,g)

17. return effective live authority handle(K,g)
```

A previously observed absence of Admission is never sufficient after acquiring
the live authority.

Recheck is mandatory.

# Authorize semantic Execution transition

Conceptually:

```text
T2 AuthorizeSemanticExecution(K,g,W)
```

requires:

```text
effective AdmissionAuthority(K,g)

Admission(K) absent

no conflict

no completion awaiting admission

no unresolved sampling hazard

no incompatible still-dispatchable unarmed E

exact existing outer Execution-authorization rules
```

If a new Execution E is created:

```text
create E
+
SemanticExecutionBinding(E,K)
```

atomically.

# Semantic Arm transition

Conceptually:

```text
T3 ArmSemanticExecution(E,K,g)
```

atomically performs:

```text
fresh K recheck
+
normal M2 Arm
+
SemanticArmBinding(E,K,g)
```

No partial semantic/M2 Arm state is permitted.

# Completion reconciliation transition

Conceptually:

```text
T4 ReconcileSemanticCompletion(E)
```

performs:

```text
resolve SemanticExecutionBinding(E,K)

validate lawful prior Semantic Arm

resolve exact authoritative terminal completion

deterministically derive protocol-valid V

compute exact SemanticAdmissionId(K,V)

serialize authoritative admission mutation relative to exact K

if no Admission(K):
    establish SemanticAdmission(K,V)
    establish first ExecutionEvidenceOf witness atomically

if same Admission(K,V):
    add missing lawful origin witness if needed
    do not create another admission

if Admission(K,V1) exists and V1 != V:
    establish SemanticAdmissionConflict
    select no winner
```

# Cross-domain semantic-history reconciliation transition

C3 additionally defines:

```text
T5 ReconcileExternalSemanticHistory
```

This transition reconciles previously disconnected semantic authority.

It performs no model inference.

For each affected exact K it is serialized relative to:

```text
T1 AcquireAdmissionAuthority

T3 ArmSemanticExecution

T4 ReconcileSemanticCompletion
```

A physical realization MUST NOT allow:

```text
import Admission(K,V)
```

to race unsafely with:

```text
new Arm(E,K,g)
```

# T5 imported admission validity

A foreign admission is not authoritative merely because it supplies:

```text
K
V
SemanticAdmissionId
```

It must carry or resolve at least one exact lawful origin witness sufficient to
reconstruct:

```text
exact QLEK

exact SemanticAdmissionId

exact semantic candidate V

exact lawful origin Execution

exact QLEK binding

exact lawful execution/Arm history

exact terminal/raw evidence

exact deterministic candidate derivation
```

A bare unproven imported semantic admission is invalid.

# T5 merge rules

For exact K:

```text
same K + same V
→ one SemanticAdmission
→ union exact lawful provenance witnesses
```

```text
same K + different V
→ SemanticAdmissionConflict
→ no winner
```

Imported unresolved armed semantic Executions remain hazards.

They MUST NOT be erased merely because another domain already has Admission(K).

# Imported admission plus local hazard

If reconciliation observes:

```text
foreign Admission(K,V)

+

local or imported Armed E(K)
whose semantic hazard is unresolved
```

then:

```text
Admission exists

but

ConsumableAdmission(K) = false
```

until the hazard is reconciled.

If E later establishes the same V:

```text
same admission
+
additional exact witness
→ hazard reconciled
```

If E establishes V2 != V:

```text
SemanticAdmissionConflict
```

If E obtains exact hazard clearance without semantic completion:

```text
foreign Admission may become consumable
```

If E remains UNRESOLVABLE:

```text
Admission remains non-consumable
```

# Pre-merge live authority invalidation

T5 invalidates the effectiveness of every pre-merge live AdmissionAuthority
handle in the merged coherent domain.

A post-merge semantic Arm requires authority acquired after reconciliation.

Historical authority grants remain provenance/coordination history where the
final realization retains them.

# Multiple imported unarmed trajectories

If disconnected domains each contain an unarmed E for the same K:

```text
no semantic sample has occurred
```

After reconciliation at most one may remain future-dispatchable.

The exact deterministic non-semantic trajectory-selection mechanism is deferred
to C9, but it MUST:

```text
inspect no semantic output

perform no model call

create no second semantic question

leave at most one armable unarmed trajectory
```

# Multiple imported armed trajectories

If disconnected domains already contain multiple Armed semantic Executions for
the same K, reconciliation MUST retain all of their semantic hazards.

No new semantic Execution for K is permitted.

Each exact existing hazard must reconcile through existing execution truth.

Possible results include:

```text
all completions agree on V
→ one Admission(K,V)
→ multiple witnesses
```

```text
completions disagree
→ SemanticAdmissionConflict
```

```text
some executions become hazard-cleared
+
one completion yields V
→ Admission(K,V)
```

```text
Admission(K,V)
+
another imported E remains unresolved/UNRESOLVABLE
→ Admission non-consumable while potential conflict remains
```

# Five authoritative C3 transitions

The final conceptual C3 state machine has exactly five authoritative transition
classes:

```text
T1 AcquireAdmissionAuthority

T2 AuthorizeSemanticExecution

T3 ArmSemanticExecution

T4 ReconcileSemanticCompletion

T5 ReconcileExternalSemanticHistory
```

M4/M8 existing execution/recovery transitions refine the exact Execution truth
between T3 and T4.

C3 introduces no sixth semantic retry/recovery machine.

# Abstract formal-state target

The future focused formal model may represent at least:

```text
authority grants per K

effective live authority per K

stale cached generation tokens

Execution → QLEK bindings

prepared executions

Semantic Arms and their generations

MAYBE-SENT truth

durable completed response truth

terminal technical-failure truth

PNE / UNRESOLVABLE recovery truth

progression supersession

SemanticAdmission

origin witnesses

SemanticAdmissionConflict

semantic-consumption observations
```

This section selects the abstract semantic state only.

It does not publish an executable TLA+ model.

# Required C3 formal properties

Later C10 formal assurance must refine or establish at least:

```text
AtMostOneAdmission

AtMostOneEffectiveAdmissionAuthority

ExecutionBoundToAtMostOneQLEK

StaleGenerationCannotArm

NoArmWithoutCurrentQLEKAuthority

NoArmAfterAdmission

NoUnsafeConcurrentDispatch

NoFreshDispatchWhileSemanticHazardExists

PNEConsistency

UNRESOLVABLEIsNotHazardClearance

SupersessionDoesNotImplyHazardClearance

CompletionBlocksFreshSampling

CompletionAdmissionCompleteness

AdmissionEvidenceCompleteness

NoSemanticObservationBeforeConsumableAdmission

SameKSameVConverges

SameKDifferentVConflicts

ConflictHasNoAutomaticWinner

ConflictBlocksDispatch

ConflictBlocksSemanticConsumption

ImportedAdmissionQuarantinedWhilePotentialConflictRemains

PreMergeLiveAuthorityCannotArmAfterMerge
```

`CompletionAdmissionCompleteness` is not required to hold as an instantaneous
state invariant across crash.

The lawful incomplete crash state:

```text
protocol-valid completion exists
Admission absent
```

may exist temporarily.

Required safety is:

```text
no fresh semantic sampling while reconciliation is pending
```

Required liveness under continued fair reconciliation is:

```text
ProtocolValidCompletion(E,K,V)

eventually

Admission(K,V)
OR
SemanticAdmissionConflict(K)
```

# Formal coherent-domain versus reconciliation models

Later formal work should distinguish:

```text
coherent-domain normal execution model
```

from:

```text
previously disconnected-domain reconciliation model
```

In the coherent-domain model, properties such as:

```text
at most one unresolved semantic-sampling hazard per K
```

may be invariant.

The reconciliation model must allow multiple pre-existing imported hazards, then
prove:

```text
no new semantic dispatch while they remain

same values converge

different values conflict

consumption waits until potential conflict is eliminated
```

Disconnected-domain behavior MUST NOT weaken the coherent-domain anti-resampling
invariant.

# Construction-level anti-cheat cases

C3 explicitly closes these required cases:

```text
same exact QLEK across different GateARuns reuses one Admission

two concurrent requests for one unresolved K cannot both dispatch

crash after durable Arm before result blocks unsafe replacement

PNE permits only the exact lawful replacement path

MAYBE-SENT uncertainty never authorizes another semantic sample

UNRESOLVABLE never authorizes another semantic sample

operator uncertain replacement cannot override QLEK single-sample semantics

progression supersession does not prove semantic non-execution

recovered protocol-valid result must become the admission for K

protocol-valid result cannot be omitted and replaced by another sample

Admission(K) prevents any later Arm for K

same K + same V duplicate provenance deduplicates semantically

same K + different V produces exact integrity conflict

old candidate-bound completion remains historical admission truth

candidate staleness does not cancel a lawful semantic sample

imported Admission without lawful origin witness fails closed

imported Admission remains non-consumable while an unresolved pre-existing
sampling hazard could still reveal a conflict

pre-merge authority token cannot Arm after history reconciliation
```

# No dispatch after Admission

Semantic Arm must check exact Admission absence at its authoritative
linearization point.

Admission mutation, semantic Arm authorization and external-history
reconciliation for exact K must be linearizable relative to each other.

Therefore:

```text
T4/T5 establishes Admission first
→ later T3 rejects

T3 establishes Arm first
→ durable hazard blocks sibling semantic Arm
```

Database uniqueness at Admission commit alone is insufficient.

# Absence of Admission is never retry authority

The condition:

```text
Admission(K) absent
```

alone never authorizes another semantic execution.

Fresh execution additionally requires at least:

```text
no conflict

no protocol-valid completion awaiting admission

no unresolved sampling hazard

no incompatible active unarmed trajectory

lawful replacement authorization when replacing prior work

fresh effective QLEK authority

normal outer execution authorization
```

# Reuse of existing M2/M4/M8 lifecycle

C3 preserves module-semantic ownership:

```text
M2
→ Execution identity
→ normal execution authorization
→ Arm
→ authoritative outcome/uncertainty/recovery progression

M4
→ PREPARED
→ MAYBE-SENT
→ terminal/raw execution evidence
→ same-Execution no-replay

M8
→ mechanical recovery observation
→ PNE
→ PROVEN-COMPLETED
→ UNRESOLVABLE / operational recovery boundary
```

C3 adds only:

```text
global logical K admission namespace

QLEK execution fencing

Execution → QLEK binding

semantic admission/conflict reconciliation
```

No separate recovery subsystem is authorized.

# Physical realization constraints

C3 does not choose a database or lock implementation.

Any conforming realization must nevertheless provide one logical serialization
domain sufficient that, for exact K:

```text
authority acquisition

fresh-generation issue

semantic Arm authorization

SemanticAdmission mutation

external semantic-history reconciliation
```

are linearizable relative to one another.

A realization placing these mutations in unrelated physical systems without a
correct linearizable coupling is non-conforming.

# M2 run-scoped ownership distinction

Existing M2 `WriteAuthorityRef` / ownership generation is run-scoped.

AdmissionAuthority generation is QLEK-scoped across the coherent semantic
authority domain.

These authorities MUST NOT be conflated.

Conceptually:

```text
M2 WriteAuthority
→ permission to mutate one run's authoritative progression

AdmissionAuthority
→ permission for exact K to approach one semantic-dispatch boundary
```

C8/C9 must map their interaction mechanically.

# Checker consequences

Protocol-v8 checker support must eventually validate enough authoritative
history to establish at least:

```text
exact QLEK binding for every native semantic Execution

lawful semantic Arm before possible provider dispatch

no stale generation Arm

no unsafe competing semantic trajectory

every native Admission has exact lawful origin evidence

every protocol-valid completion reconciles to Admission or exact conflict

Admission candidate equals deterministic candidate reconstructed from raw
completion

same K + same V converges semantically

same K + different V conflicts

no semantic consumer reads an uncommitted or non-consumable Admission

cross-run/root provenance does not change admission identity

UNRESOLVABLE and supersession do not silently authorize resampling
```

# C3 completeness assertions

C3 is complete only if all statements below hold:

```text
one coherent semantic-admission namespace exists independently of GateARun

Admission is single-assignment per QLEK

live AdmissionAuthority is distinct from durable SemanticAdmission

authority generation is monotone inside a coherent coordination epoch

stale authority cannot Arm

generation is not semantic identity

every semantic Execution has at most one immutable QLEK binding

Execution creation and new semantic binding are atomic

normal M2 Arm and SemanticArmBinding are atomic

provider remains unreachable before accepted M2/M4 effect fences

durable Arm survives live-owner crash

semantic hazard is distinct from Execution progression terminality

hazard clearance is distinct from replacement authorization

PNE clears hazard but does not itself authorize arbitrary retry

UNRESOLVABLE does not clear hazard

post-Arm supersession does not clear hazard

operator uncertain replacement cannot resample an unresolved QLEK

protocol-valid completion blocks fresh semantic sampling until reconciliation

Admission and first lawful origin witness are atomic

same K + same V converges to one admission with additional provenance

same K + different V creates exact fail-closed conflict

Admission conflict has no automatic winner

semantic consumption requires exact consumable Admission

candidate staleness never erases lawful old-QLEK semantic truth

cross-domain merge invalidates pre-merge live QLEK authority

imported Admission requires exact lawful origin evidence

imported unresolved hazards remain hazards

imported Admission is quarantined while a pre-existing hazard could still
produce a conflicting candidate

absence of Admission never independently authorizes redispatch

C3 reuses M2/M4/M8 rather than creating a second recovery machine

no SQL/lock/schema/API implementation choice is made

no C4 fact semantics are invented

no C5 CandidateView semantics are invented

no C6 packet/receipt representation is selected
```

# G-C3 closure

Completion gate `G-C3` is semantically satisfied by this construction when the
artifact is published and verified against ADR-056, C1 and C2.

The gate establishes:

```text
two runners inside one coherent semantic authority domain
cannot lawfully produce competing semantic samples for one K
```

and:

```text
every pre-dispatch and post-dispatch crash boundary
has an exact safety/recovery disposition
```

and:

```text
absence of Admission(K)
alone
never authorizes unsafe redispatch
```

Disconnected domains may contain independently created semantic histories only
because they could not coordinate.

Their later reconciliation is fail-closed and does not permit new model
shopping.

After publication and audit of this artifact:

```text
C3 = CLOSED
```

Construction may then proceed to:

```text
C4 — SemanticFact and qualification resolution
```

without constructing or activating protocol-v8 runtime artifacts.
