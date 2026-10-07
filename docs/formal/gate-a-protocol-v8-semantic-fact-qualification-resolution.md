---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "construction-semantic-fact-resolution"
domain: "turnlock-rust-formal-assurance"
severity: "strict"
name: "Gate A protocol v8 SemanticFact and qualification resolution"
---

# Gate A protocol v8 SemanticFact and qualification resolution

## Status and authority

This document is the C4 construction closure for protocol-v8 work authorized by
ADR-056 and constrained by the published C1, C2 and C3 construction closures.

It is a non-protocol-authoritative construction artifact.

It closes the exact protocol-v8 SemanticFact substrate required by C1 semantic
questions and by ADR-055/ADR-056 qualification and resolution semantics.

Authority remains:

```text
docs/specification/turnlock-spec.md

accepted ADRs

especially ADR-055 and ADR-056

docs/formal/gate-a-protocol-v8-semantic-question-contract-catalog.md

docs/formal/gate-a-protocol-v8-semantic-identity-algebra.md

docs/formal/gate-a-protocol-v8-semantic-admission-authority-execution-fencing.md
```

This document MUST NOT:

```text
change TURNLOCK product semantics

change Gate A semantic subject S

change a C1 SemanticQuestionContract

change a C1 QualificationContract

change C2 identity framing

change C3 admission/fencing semantics

activate protocol v8

select SQL tables

select physical indexes

select Fact storage

select QualificationKey storage

define packet/receipt schemas

define CandidateView construction

perform current-candidate selection

create mutable semantic status authority

reinterpret P1-P7 evidence
```

If implementation or later construction requires choosing between materially
different semantic meanings rather than mechanically refining this design:

```text
STOP
→ decision-required
→ accepted ADR
→ resume from earliest affected stage
```

# C4 construction boundary

C4 closes:

```text
exact PredicateRevisionId inventory

exact SemanticFact argument objects

predicate semantic meanings

seven qualification reducers

five non-qualification reducers

fact reconstructibility

fact consumability

cross-run and cross-root resolution

semantic dependency well-foundedness

semantic/provenance proof separation

deterministic model-visible fact projection

primitive-versus-derived fact boundary
```

C4 does NOT close:

```text
physical Fact persistence

physical QualificationKey persistence

packet representation

receipt representation

repository fact projection schema

CandidateView construction

current-candidate authorization

module APIs

SQL layout

executable TLA+ model
```

# Fundamental SemanticFact rule

A protocol-v8 SemanticFact is an exact positive proposition.

Its immutable identity remains the exact C2 algebra:

```text
SemanticFactDescriptorV1 {
  schema:
    "turnlock.semantic-fact-descriptor.v1"

  predicateRevision:
    PredicateRevisionId

  arguments:
    exact closed predicate-specific canonical object
}
```

and:

```text
FactId =
"semantic-fact-sha256:" +
IdentityHashV1(
  "turnlock.semantic-fact.v1",
  exact SemanticFactDescriptorV1
)
```

Fact identity commits:

```text
exact PredicateRevisionId
+
exact canonical semantic arguments
```

Fact identity does NOT commit arbitrary proof/provenance identity.

# Exact PredicateRevision inventory

Protocol v8 C4 defines exactly thirteen PredicateRevisionIds:

```text
turnlock.predicate:QualifiedPositiveMateriality@1

turnlock.predicate:QualifiedNonMateriality@1

turnlock.predicate:QualifiedRefutation@1

turnlock.predicate:RefutationExhaustionWithoutQualifiedRefutation@1

turnlock.predicate:TargetedDiscoveryStatement@1

turnlock.predicate:DecisionRequiredDiscoveryStatement@1

turnlock.predicate:QualifiedNoNormativeImpact@1

turnlock.predicate:UniqueCorrectionExhaustion@1

turnlock.predicate:DecisionNecessityCandidate@1

turnlock.predicate:QualifiedDecisionNecessity@1

turnlock.predicate:AcceptedUniqueCorrection@1

turnlock.predicate:AcceptedRealizationScope@1

turnlock.predicate:AcceptedRepairRealization@1
```

No additional protocol-v8 C4 predicate is authorized.

In particular C4 does NOT introduce:

```text
MaterialityRejected

NormativeImpact

FindingTrue

NoDecisionNecessary

RejectedUniqueCorrection

UniqueCorrectionFailed

RealizationScopeFailed

RepairRealizationFailed

ChallengePassed

ChallengeFailed

FactStatus
```

A future semantic change to a predicate's:

```text
argument schema

identity semantics

proposition meaning
```

requires a new PredicateRevision.

# Primitive versus derived facts

Protocol-v8 C4 introduces:

```text
zero primitive persisted SemanticFact commitments
```

All thirteen C4 facts are derived mechanically from:

```text
primitive durable SemanticAdmissions

exact SemanticValues

ExactAuthorities

exact accepted protocol rules
```

A physical implementation MAY cache or index derived fact information.

Such cache/index data:

```text
is not semantic authority

is disposable

must be exactly rebuildable
```

Deleting every derived Fact cache and rebuilding from the same exact
Authoritative History MUST produce the same exact semantic closure.

# Qualification-result argument pattern

Exactly eight C4 predicates represent qualification outcomes:

```text
QualifiedPositiveMateriality

QualifiedNonMateriality

QualifiedRefutation

QualifiedNoNormativeImpact

QualifiedDecisionNecessity

AcceptedUniqueCorrection

AcceptedRealizationScope

AcceptedRepairRealization
```

For each, the exact argument object contains one field only:

```text
{
  "qualification":
    QualificationKeyRefV1
}
```

The applicable predicate revision constrains the exact required
QualificationContractRevisionId.

No qualification-result fact duplicates:

```text
anchor SemanticAdmission

challenge SemanticAdmission

SM

CandidateRevision

CandidateView

receipt

root

run
```

when that authority is already committed by the exact QualificationKey.

# QualifiedPositiveMateriality@1

Exact predicate:

```text
turnlock.predicate:QualifiedPositiveMateriality@1
```

Arguments:

```text
{
  "qualification":
    QualificationKeyRef<
      turnlock.qualification:MaterialityAssessmentQualification@1
    >
}
```

Reducer requires:

```text
exact QualificationKey resolves

anchorAdmission is exact consumable
MaterialityAssessmentInitial@1
OR
MaterialityAssessmentRevision@1 admission

additionalInputs == {}

exact MaterialityAssessmentValue resolves

at least one of the seven materiality axes == true
```

The seven axes are exactly:

```text
authority_or_upstream_decision

claim_structure

normative_provenance

modality_or_assurance_domain

coverage_or_residual_assurance

interaction_scope

candidate_model_authorization
```

No Materiality challenge is required on this positive branch.

A positive Materiality revision with one or more true axes is qualified directly
under its own exact qualification key.

# QualifiedNonMateriality@1

Exact predicate:

```text
turnlock.predicate:QualifiedNonMateriality@1
```

Arguments:

```text
{
  "qualification":
    QualificationKeyRef<
      turnlock.qualification:MaterialityAssessmentQualification@1
    >
}
```

Reducer requires:

```text
anchorAdmission is exact consumable
MaterialityAssessmentInitial@1
OR
MaterialityAssessmentRevision@1 admission

all seven materiality axes == false

additionalInputs contains exactly:
materialityChallenge

materialityChallenge is exact consumable
MaterialityChallenge@1 admission

the MaterialityChallenge exact QLEK targets anchorAdmission

challenge semantic value is exact ChallengeSemanticValue

challenge.objections == []
```

Then and only then:

```text
QualifiedNonMateriality
```

is derivable.

A non-empty Materiality challenge objection set derives no positive C4
qualification fact.

It NEVER mechanically implies positive materiality.

The same exact assessment cannot derive both:

```text
QualifiedPositiveMateriality

and

QualifiedNonMateriality
```

# QualifiedRefutation@1

Exact predicate:

```text
turnlock.predicate:QualifiedRefutation@1
```

Arguments:

```text
{
  "qualification":
    QualificationKeyRef<
      turnlock.qualification:RefutationQualification@1
    >
}
```

Reducer requires:

```text
anchorAdmission is exact consumable
RefutationInitial@1
OR
RefutationRevision@1 admission

anchor semantic candidate is a positive RefutationCandidate

anchor semantic candidate is NOT NotEstablished

additionalInputs contains exactly:
refutationChallenge

refutationChallenge is exact consumable
RefutationChallenge@1 admission

challenge exact QLEK targets anchorAdmission

challenge.objections == []
```

A non-empty challenge objection set derives no `QualifiedRefutation`.

It does not prove finding truth.

# RefutationExhaustionWithoutQualifiedRefutation@1

Exact predicate:

```text
turnlock.predicate:RefutationExhaustionWithoutQualifiedRefutation@1
```

Arguments:

```text
{
  "qualifiedPositiveMateriality":
    SemanticFactRef<
      turnlock.predicate:QualifiedPositiveMateriality@1
    >
}
```

No exhaustion proof branch, receipt or terminal locator enters the arguments.

Resolve exact QPM `M`.

Mechanically reconstruct from `M`:

```text
exact FindingAdjudicationBasis FA

exact RefutationInitial@1 QLEK:
  FA
  +
  M
```

The predicate is derivable iff exactly one lawful bounded-refutation terminal
proof is established.

The three lawful semantic terminal branches are:

```text
initial-not-established

revision-not-established

revised-challenge-objections
```

## Refutation exhaustion branch: initial-not-established

Require exact consumable:

```text
RefutationInitial admission
```

for the reconstructed initial QLEK and:

```text
semantic candidate == NotEstablished
```

## Refutation exhaustion branch: revision-not-established

Require exact consumable chain:

```text
initial positive Refutation admission

exact RefutationChallenge(initial)
with objections != []

exact RefutationRevision@1
with exact same FA
and exact same QPM
and exact prior initial Refutation admission
and exact prior RefutationChallenge admission

revision semantic candidate == NotEstablished
```

## Refutation exhaustion branch: revised-challenge-objections

Require exact consumable chain:

```text
initial positive Refutation admission

exact initial RefutationChallenge
with objections != []

exact positive RefutationRevision@1
bound to same FA/QPM/prior closure

exact fresh RefutationChallenge(revision)
with objections != []
```

No other state establishes refutation exhaustion.

In particular these do NOT establish it:

```text
missing challenge

pending mandatory revision

technical inability

provider failure

UNRESOLVABLE execution

missing supporting profile

operator blocker

retry exhaustion before semantic closure
```

The three proof branches establish one semantic proposition.

Proof-branch identity does NOT enter FactId.

For the same exact refutation closure:

```text
RefutationExhaustionWithoutQualifiedRefutation
```

and:

```text
QualifiedRefutation
```

MUST NOT both be consumable.

# TargetedDiscoveryStatement@1

Exact predicate:

```text
turnlock.predicate:TargetedDiscoveryStatement@1
```

Arguments:

```text
{
  "producerDiscovery":
    SemanticAdmissionRefV1,

  "statement":
    exact canonical AtomicDiscoveryClassificationStatement
}
```

`producerDiscovery` must be exact consumable admission from one of:

```text
DiscoveryClassificationInitial@1

positive DiscoveryNoNormativeImpactRevision@1

positive DiscoveryDecisionRequiredRevision@1
```

For initial Discovery:

```text
statement
```

must occur exactly once in:

```text
classification_statements[]
```

of the exact producer semantic candidate.

For a positive Discovery closure revision:

```text
result.kind == "revised-candidate"

result.statement == exact arguments.statement
```

A revision returning `NotEstablished` produces no
TargetedDiscoveryStatement fact.

The classification statement ordinal is reconstructible from the initial
Discovery value but does NOT enter Fact identity.

Duplicate exact canonical statements in one initial Discovery value remain
invalid under C1.

# DecisionRequiredDiscoveryStatement@1

Exact predicate:

```text
turnlock.predicate:DecisionRequiredDiscoveryStatement@1
```

Arguments:

```text
{
  "targetedDiscoveryStatement":
    SemanticFactRef<
      turnlock.predicate:TargetedDiscoveryStatement@1
    >
}
```

Resolve exact targeted statement `T`.

Require:

```text
T.statement.semantic_disposition
==
"decision-required"
```

and:

```text
T.statement.disposition_basis
```

is exact valid `decisionRequiredBasis` of exactly one of:

```text
product-underdetermination

product-authority-conflict
```

The exact basis semantics remain those already accepted by ADR-055/C1 and the
immutable semantic-value contract.

This fact represents an exact decision-required Discovery hypothesis.

It does NOT itself authorize:

```text
DECISION-REQUIRED

DecisionRequest
```

# QualifiedNoNormativeImpact@1

Exact predicate:

```text
turnlock.predicate:QualifiedNoNormativeImpact@1
```

Arguments:

```text
{
  "qualification":
    QualificationKeyRef<
      turnlock.qualification:NoNormativeImpactQualification@1
    >
}
```

Reducer requires exact key shape:

```text
anchorAdmission

targetedDiscoveryStatement

noNormativeImpactChallenge
```

Require:

```text
anchorAdmission
==
producerAdmission(targetedDiscoveryStatement)
```

Require targeted statement exact semantic disposition:

```text
no-normative-impact
```

Require exact consumable:

```text
NoNormativeImpactChallenge@1
```

whose exact QLEK input references the same exact targeted statement FactRef.

Require:

```text
challenge.objections == []
```

A non-empty challenge objection set derives no positive C4 qualification fact.

It NEVER mechanically derives a `NormativeImpact` fact.

# UniqueCorrectionExhaustion@1

Exact predicate:

```text
turnlock.predicate:UniqueCorrectionExhaustion@1
```

Arguments:

```text
{
  "targetedDiscoveryStatement":
    SemanticFactRef<
      turnlock.predicate:TargetedDiscoveryStatement@1
    >
}
```

No exhaustion proof branch, receipt or terminal locator enters the arguments.

Resolve exact TargetedDiscoveryStatement `T`.

`T` commits exactly:

```text
producer Discovery SemanticAdmission
+
exact atomic Discovery statement
```

Resolve from producer Discovery admission the exact `SM`.

Mechanically reconstruct exact:

```text
UniqueCorrectionInitial@1(
  exact SM,
  exact producer Discovery admission,
  exact T
)
```

The predicate is derivable iff one lawful bounded-UniqueCorrection terminal proof
is established.

The three lawful semantic terminal branches are exactly:

```text
initial-not-established

revision-not-established

revised-challenge-objections
```

## UniqueCorrection exhaustion branch: initial-not-established

Require exact consumable:

```text
UniqueCorrectionInitial admission
```

for the exact target closure and:

```text
semantic candidate == NotEstablished
```

## UniqueCorrection exhaustion branch: revision-not-established

Require exact consumable chain:

```text
initial positive UniqueCorrection admission

exact UniqueCorrectionChallenge(initial)
with objections != []

exact UniqueCorrectionRevision@1
with same exact SM
same producer Discovery admission
same targeted statement
same exact prior UC admission
same exact prior UC challenge

revision semantic candidate == NotEstablished
```

## UniqueCorrection exhaustion branch: revised-challenge-objections

Require exact consumable chain:

```text
initial positive UniqueCorrection

exact initial UC challenge
with objections != []

exact positive UC revision
bound to same exact closure

exact fresh UC challenge(revision)
with objections != []
```

No operational inability establishes UniqueCorrection exhaustion.

The three proof branches establish one semantic proposition.

Proof-branch identity does NOT enter FactId.

`UniqueCorrectionExhaustion(T)` NEVER by itself means:

```text
DECISION-REQUIRED

no correction exists
```

For the same exact UC closure:

```text
UniqueCorrectionExhaustion
```

and:

```text
AcceptedUniqueCorrection
```

MUST NOT both be consumable.

# DecisionNecessityCandidate@1

Exact predicate:

```text
turnlock.predicate:DecisionNecessityCandidate@1
```

Arguments:

```text
{
  "survivingMaterialBasis":
    SemanticValueRef<
      turnlock.semantic-value:SurvivingMaterialBasis@1
    >,

  "decisionRequiredStatement":
    SemanticFactRef<
      turnlock.predicate:DecisionRequiredDiscoveryStatement@1
    >,

  "uniqueCorrectionExhaustion":
    SemanticFactRef<
      turnlock.predicate:UniqueCorrectionExhaustion@1
    >
}
```

Let:

```text
S = survivingMaterialBasis
D = decisionRequiredStatement
U = uniqueCorrectionExhaustion
```

Resolve:

```text
D
→ exact TargetedDiscoveryStatement T
→ exact producer Discovery admission P
```

Require:

```text
exact SM committed by P's QLEK
==
S
```

Require:

```text
U.arguments.targetedDiscoveryStatement
==
T
```

Require T is exact valid `decision-required` statement.

The deterministic DecisionNecessity candidate value is exactly:

```text
{
  "kind":
    "decision-necessity-candidate",

  "basis":
    exact T.statement.disposition_basis
}
```

The basis is copied exactly.

C4 performs:

```text
no paraphrase

no semantic normalization

no model inference

no alternative selection
```

The candidate value is mechanically projected.

It does NOT independently enter the Fact arguments because it is uniquely
reconstructible from `D`.

The fact represents that:

```text
the exact decision-required hypothesis D

under exact SM S

has reached a lawful exact UniqueCorrection exhaustion U

and therefore has one exact mechanically projected
DecisionNecessity candidate
```

# QualifiedDecisionNecessity@1

Exact predicate:

```text
turnlock.predicate:QualifiedDecisionNecessity@1
```

Arguments:

```text
{
  "qualification":
    QualificationKeyRef<
      turnlock.qualification:DecisionNecessityQualification@1
    >
}
```

Resolve exact QualificationKey with:

```text
anchorAdmission

survivingMaterialBasis S

decisionRequiredStatement D

uniqueCorrectionExhaustion U

decisionNecessityCandidate N

decisionNecessityChallenge C
```

Require:

```text
anchorAdmission
==
producerAdmission(D)
```

Require exact Discovery producer closure commits:

```text
SM == S
```

Require:

```text
target(U)
==
target(D)
```

Require:

```text
N.arguments.survivingMaterialBasis == S

N.arguments.decisionRequiredStatement == D

N.arguments.uniqueCorrectionExhaustion == U
```

Require exact consumable:

```text
DecisionNecessityChallenge@1 admission C
```

whose exact logical input is:

```text
S
D
U
N
```

Require:

```text
C.objections == []
```

Then and only then:

```text
QualifiedDecisionNecessity
```

is derivable.

A non-empty DecisionNecessity challenge objection set derives no opposite fact.

Only `QualifiedDecisionNecessity` may later authorize mechanical DecisionRequest
projection.

# AcceptedUniqueCorrection@1

Exact predicate:

```text
turnlock.predicate:AcceptedUniqueCorrection@1
```

Arguments:

```text
{
  "qualification":
    QualificationKeyRef<
      turnlock.qualification:UniqueCorrectionQualification@1
    >
}
```

Reducer requires:

```text
anchorAdmission is exact consumable positive
UniqueCorrectionInitial@1
OR
UniqueCorrectionRevision@1

anchor candidate is NOT NotEstablished

exact consumable UniqueCorrectionChallenge@1
targets anchorAdmission

challenge.objections == []
```

Then:

```text
AcceptedUniqueCorrection
```

is derivable.

A non-empty challenge objection set derives no opposite Fact.

# AcceptedRealizationScope@1

Exact predicate:

```text
turnlock.predicate:AcceptedRealizationScope@1
```

Arguments:

```text
{
  "qualification":
    QualificationKeyRef<
      turnlock.qualification:RealizationScopeQualification@1
    >
}
```

Reducer requires:

```text
anchorAdmission is exact consumable positive
RealizationScopeInitial@1
OR
RealizationScopeRevision@1

anchor candidate is NOT NotEstablished

exact consumable RealizationScopeChallenge@1
targets anchorAdmission

challenge.objections == []
```

Then:

```text
AcceptedRealizationScope
```

is derivable.

Candidate binding is inherited exactly through:

```text
AcceptedRealizationScope Fact
→ QualificationKey
→ anchor RS SemanticAdmission
→ RS QLEK
→ exact CandidateRevision
```

C4 does NOT perform current-candidate revalidation.

# AcceptedRepairRealization@1

Exact predicate:

```text
turnlock.predicate:AcceptedRepairRealization@1
```

Arguments:

```text
{
  "qualification":
    QualificationKeyRef<
      turnlock.qualification:RepairRealizationQualification@1
    >
}
```

Reducer requires:

```text
anchorAdmission is exact consumable positive
RepairRealizationInitial@1
OR
RepairRealizationRevision@1

anchor candidate is NOT NotEstablished

exact consumable RepairRealizationChallenge@1
targets anchorAdmission

challenge.objections == []
```

Then:

```text
AcceptedRepairRealization
```

is derivable.

A positive RepairRealization with:

```text
operations == []
```

because every correction requirement is `already-realized` remains a positive
candidate and may derive `AcceptedRepairRealization`.

Later RepairIntent projection remains separately mechanical.

# Qualification reducer common rules

For every exact QualificationKeyRef:

```text
1. resolve exact QualificationKeyDescriptor

2. recompute QualificationKey

3. require exact expected QualificationContractRevisionId

4. resolve anchorAdmission

5. require anchorAdmission is C3 ConsumableAdmission

6. resolve every additional SemanticAdmissionRef

7. require every such Admission is C3 ConsumableAdmission

8. resolve every SemanticFactRef

9. mechanically re-establish every referenced Fact

10. resolve every SemanticValueRef

11. validate all exact qualification-specific cross-bindings

12. execute deterministic qualification reducer
```

A structurally valid QualificationKey whose reducer establishes no positive fact
is normal qualification absence.

It is NOT integrity failure.

A claimed FactRef asserting a qualification result that its reducer does not
establish IS integrity failure.

# Qualification reducer outcome cardinality

For one exact QualificationKey under one exact authoritative semantic closure:

```text
Cardinality(
  derived C4 qualification-result facts
)
<= 1
```

QualificationKey existence does NOT itself encode outcome.

`ReduceQualification(Q) = {}` means only:

```text
this exact qualification closure establishes
none of the positive C4 facts
```

It does NOT establish the opposite proposition.

# Materiality qualification mutual exclusion

For one exact MaterialityAssessment admission:

```text
any axis true
→ positive-materiality QualificationKey shape
→ QualifiedPositiveMateriality
```

or:

```text
all axes false
→ challenged non-material QualificationKey shape
```

The same exact assessment cannot derive both:

```text
QualifiedPositiveMateriality
QualifiedNonMateriality
```

# Challenge semantics

For every challenge-closed qualification:

```text
challenge.objections == []
```

is necessary for its positive C4 fact.

A non-empty objection list:

```text
does not establish the opposite proposition

does not create a negative Fact

does not permit semantic resampling
```

Revision behavior remains exactly C1 authority.

# SurvivingMaterialBasis interaction

C2 defines:

```text
SurvivingMaterialBasisV1 {
  findingAdjudicationBasis
  qualifiedPositiveMateriality
  refutationExhaustionWithoutQualifiedRefutation
}
```

C4 validates exact SM mechanically.

Require:

```text
findingAdjudicationBasis resolves exact FA

qualifiedPositiveMateriality resolves exact
QualifiedPositiveMateriality@1 Fact

refutationExhaustionWithoutQualifiedRefutation resolves exact
RefutationExhaustionWithoutQualifiedRefutation@1 Fact

QPM belongs to exact FA

RefutationExhaustion belongs to exact FA

RefutationExhaustion commits exact same QPM Fact
```

For semantic consumption, both Fact dependencies must also be consumable.

# Fact descriptor preimages

A `SemanticFactRefV1` carries:

```text
predicateRevision
factId
```

and therefore does not inline its descriptor.

C4 requires every valid FactId to have exactly one reconstructible canonical
`SemanticFactDescriptorV1` preimage in semantic closure.

A FactId digest without a reconstructible descriptor is insufficient authority.

C4 does NOT require a primitive persisted Fact object.

# SemanticClosureIndex

Define conceptually:

```text
SemanticClosureIndex(H)
```

for exact coherent Authoritative History `H`.

It is a deterministic disposable derived index constructed forward from:

```text
primitive authoritative commitments

exact SemanticAdmissions

exact SemanticValues

ExactAuthorities

C1/C2/C3 rules

C4 reducers
```

It may index deterministic preimages for:

```text
QualificationKey

FactId
```

It MUST NOT become semantic authority.

No semantic hash inversion is permitted.

Conceptually:

```text
Authoritative History
↓
forward deterministic derivation
↓
canonical descriptors
↓
identity computation
↓
derived lookup index
```

Deleting and rebuilding the complete derived index from unchanged authoritative
history MUST produce identical semantic closure.

# Fact identity resolution

For exact `SemanticFactRef F`, identity resolution requires:

```text
F has exact SemanticFactRefV1 shape

F.predicateRevision belongs exact thirteen-predicate C4 catalog

F.factId resolves to exactly one canonical descriptor

descriptor.predicateRevision == F.predicateRevision

descriptor arguments match exact closed predicate schema

recomputed FactId(descriptor) == F.factId
```

No descriptor preimage:

```text
dangling FactRef
→ integrity failure
```

More than one distinct canonical descriptor for one FactId:

```text
IDENTITY-HASH-COLLISION
→ fail closed
```

# Fact reconstructibility

Define conceptually:

```text
FactReconstructible(F)
```

when:

```text
exact Fact identity resolves

all typed dependencies resolve

all exact cross-bindings validate

at least one lawful deterministic derivation/proof
establishes the predicate
```

Fact descriptor existence alone does NOT establish Fact truth.

# Fact consumability

Define conceptually:

```text
FactConsumable(F)
```

when:

```text
FactReconstructible(F)

AND

the entire exact semantic dependency closure
is currently consumable under C3

AND

no SemanticAdmissionConflict or unresolved C3 semantic hazard
quarantines a required dependency
```

Therefore:

```text
FactConsumable(F)
→ FactReconstructible(F)
```

but not necessarily the reverse.

A historically reconstructible Fact may become temporarily or permanently
non-consumable after semantic-history reconciliation.

That does NOT rewrite:

```text
FactId
Fact descriptor
historical semantic truth
```

# Admission consumability propagation

Any SemanticAdmission used to establish or consume a C4 fact must satisfy the
applicable C3 `ConsumableAdmission` authority.

This applies to:

```text
qualification anchors

challenge admissions

producer Discovery admissions

Refutation/UniqueCorrection closure admissions

admissions transitively required by semantic values or predecessor facts
```

A non-consumable Admission MUST NOT be used to derive a new downstream semantic
QLEK or qualification result.

# Prospective derivation versus claimed Fact resolution

C4 distinguishes conceptually:

```text
TryDeriveFact(
  PredicateRevision,
  exact arguments,
  AuthoritativeHistory
)
```

from:

```text
ResolveClaimedFact(
  SemanticFactRef,
  AuthoritativeHistory
)
```

`TryDeriveFact` may normally produce:

```text
exact derivable Fact
```

or:

```text
not derivable
```

without integrity failure.

`ResolveClaimedFact` asserts that the referenced Fact exists.

It must therefore resolve as reconstructible or fail closed.

A claimed non-reconstructible FactRef is integrity failure.

# No negative Fact semantics

C4 uses positive ground predicates.

A reducer returning no Fact does NOT mean:

```text
opposite proposition is true
```

C4 does not introduce generic:

```text
false Fact

rejected Fact

challenge failed Fact

qualification failed Fact
```

# No regeneration from invalid FactRef

An unresolvable, dangling or invalid claimed FactRef MUST NOT authorize:

```text
rerun predecessor cognition

recreate a challenge

resample a SemanticAdmission

guess alternate arguments

fabricate a replacement Fact
```

It is integrity failure.

# Semantic dependency graph

The exact semantic dependency graph contains exact instances of at least:

```text
ExactAuthority

SemanticValue

QLEK

SemanticAdmission

QualificationKey

SemanticFact
```

Execution receipts, raw outputs and root projections belong to the evidence
provenance graph.

They may be required to validate SemanticAdmission origin evidence but do not
become semantic predecessor identities merely as proof.

# Semantic dependency well-foundedness

The exact ground semantic dependency instance graph MUST have no unlawful causal
cycle.

During recursive resolution, if exact node `N` is encountered while that same
exact node remains active on the resolution stack:

```text
unlawful causal cycle
→ fail closed
```

Node identity is its exact semantic identity, such as:

```text
SemanticValueId

QLEK

SemanticAdmissionId

QualificationKey

FactId

ExactAuthority identity
```

No fixed-point semantic interpretation is introduced.

Recursive families are lawful when exact instances differ through new immutable
authority.

For example:

```text
RealizationScope(C0)
→ RepairRealization(C0)
→ C1
→ RealizationScope(C1)
```

does not create an instance cycle because:

```text
QLEK_RS(C0)
!=
QLEK_RS(C1)
```

# Cross-run fact resolution

Fact resolution is scoped to the coherent Authoritative History semantic
namespace.

It is NOT restricted by current GateARun.

If Run A established exact Fact `F` and Run B later requires exact same `F`:

```text
reuse F
```

when it remains consumable.

Do NOT rerun semantic work merely because Fact provenance belongs to another run.

# Cross-root fact resolution

Fact semantic usability is NOT determined by:

```text
ReviewCampaign ownership

supplement ownership

supporting_executions[] ownership

receipt location
```

A consuming root resolves exact Fact identity and reconstructs semantic truth.

The predecessor origin receipt remains in its original historical provenance
location.

No semantic receipt ownership transfer is required.

# Multiple provenance graphs

Different lawful evidence/provenance graphs may establish the same exact
SemanticFact.

If they produce:

```text
same PredicateRevisionId
+
same exact canonical arguments
```

then they produce:

```text
one same FactId
```

Conceptually multiple proof witnesses may exist.

Proof-witness identity does NOT enter FactId merely as provenance.

The resolver does not select an evidence owner as semantic identity.

# Exhaustion proof branches are provenance

For both:

```text
RefutationExhaustionWithoutQualifiedRefutation

UniqueCorrectionExhaustion
```

the exact bounded-closure proof branch remains reconstructible audit evidence.

It does NOT enter FactId.

It MUST NOT become a model-visible semantic discriminator for the same FactId.

# Deterministic resolved fact semantic view

Some C1/C5/C6 consumers require semantic content represented by a Fact rather
than a boolean proposition alone.

Define conceptually:

```text
ResolvedFactSemanticView(F)
```

as the unique deterministic semantic projection of exact Fact `F`.

It is:

```text
not a new semantic identity

not a new primitive commitment

not a second source of truth

not a persisted mutable status
```

It is derived only from information directly or transitively committed by the
Fact identity closure.

Require globally:

```text
same FactId
→ same exact ResolvedFactSemanticView
```

Changing only:

```text
receipt selected as proof

root ownership

GateARun

proof branch

evidence locator

provenance witness
```

MUST NOT alter the semantic view when those dimensions are absent from Fact
identity.

# Qualification-fact semantic views

For a qualification-result Fact:

```text
Fact
→ QualificationKey
→ exact anchorAdmission
```

The anchor admission semantic candidate is the canonical basis for its
candidate-bearing semantic view where applicable.

Examples:

```text
AcceptedUniqueCorrection
→ exact accepted UniqueCorrection candidate

AcceptedRealizationScope
→ exact accepted RealizationScope candidate

AcceptedRepairRealization
→ exact accepted RepairRealization candidate

QualifiedRefutation
→ exact qualified Refutation candidate

QualifiedPositiveMateriality
→ exact positive MaterialityAssessment value
```

No independently copied candidate value becomes another authority.

# AcceptedUniqueCorrection semantic view

From exact `AcceptedUniqueCorrection` Fact:

```text
resolve QualificationKey

resolve anchor UniqueCorrection admission

return exact anchor semantic candidate
```

This exposes exact accepted semantic content including:

```text
correction_requirements[]

derivation_claims[]

alternatives_considered[]

uniqueness_argument
```

as already committed by the anchor admission.

# AcceptedRealizationScope semantic view

From exact `AcceptedRealizationScope` Fact:

```text
resolve QualificationKey

resolve anchor RealizationScope admission

return exact anchor semantic candidate
```

This exposes:

```text
readable_paths[]

writable_paths[]

completeness_argument

minimal_write_authority_argument
```

The exact bound CandidateRevision is reconstructible from the anchor RS QLEK.

C4 therefore exposes conceptually:

```text
CandidateRevisionOf(
  AcceptedRealizationScope Fact
)
```

as a deterministic projection.

C4 does NOT test whether that CandidateRevision remains current.

# AcceptedRepairRealization semantic view

From exact `AcceptedRepairRealization` Fact:

```text
resolve QualificationKey

resolve anchor RepairRealization admission

return exact anchor semantic candidate
```

This exposes:

```text
requirement_realizations[]

operations[]
```

The exact bound CandidateRevision is reconstructible from the anchor RR QLEK.

# TargetedDiscoveryStatement semantic view

The semantic view is exactly:

```text
arguments.statement
```

No receipt or statement ordinal is added as semantic content.

# DecisionRequiredDiscoveryStatement semantic view

The semantic view is the exact targeted statement committed by its predecessor,
including the exact:

```text
decision-required disposition

decisionRequiredBasis
```

No new wording is generated.

# DecisionNecessityCandidate semantic view

The semantic view is exactly:

```text
{
  "kind":
    "decision-necessity-candidate",

  "basis":
    exact underlying decision-required statement disposition_basis
}
```

No semantic transformation is permitted.

# Exhaustion semantic views

For:

```text
RefutationExhaustionWithoutQualifiedRefutation
```

the semantic view exposes the exact proposition and the exact QPM Fact identity
required by its semantic meaning.

It MUST NOT expose proof-branch choice as semantic input.

For:

```text
UniqueCorrectionExhaustion
```

the semantic view exposes the exact proposition and exact target
TargetedDiscoveryStatement identity.

It MUST NOT expose proof-branch choice as semantic input.

# Model-visible provenance exclusion

A protocol-v8 execution packet that carries a SemanticFact projection MUST NOT
make provenance-only proof variation model-visible if that variation is absent
from the exact Fact identity.

In particular changing only:

```text
run

root

receipt

proof branch

provenance locator

proof witness
```

for the same exact Fact MUST NOT create different model-visible semantics.

Concrete packet representation remains C6.

# Candidate-bound Fact preservation

`AcceptedRealizationScope` and `AcceptedRepairRealization` remain exact
candidate-bound historical Facts.

Candidate advance does NOT make those historical Facts false.

C4 preserves mechanically their exact bound CandidateRevision through the anchor
SemanticAdmission/QLEK.

C5 owns later equality/currentness checks and MUST prevent another candidate from
inheriting that authority.

# Contradictory same-closure facts

For one exact bounded closure, C4 requires fail-closed consistency.

At minimum:

```text
RefutationExhaustionWithoutQualifiedRefutation
```

and:

```text
QualifiedRefutation
```

for the same exact Refutation closure MUST NOT both be consumable.

Likewise:

```text
UniqueCorrectionExhaustion
```

and:

```text
AcceptedUniqueCorrection
```

for the same exact UC closure MUST NOT both be consumable.

In a coherent normal domain the exact SemanticAdmission algebra should already
prevent such contradictory terminal closures.

After disconnected-domain reconciliation, C3 conflict/quarantine semantics MUST
prevent contradictory closure evidence from simultaneously becoming consumable.

C4 does not choose a winner.

# Resolver cache

Resolution MAY memoize locally:

```text
reconstructibility

consumability

resolved semantic views
```

for performance.

Such memoization:

```text
is disposable

is not authoritative

must not affect semantic output
```

Re-running resolution over unchanged authoritative history MUST produce the same
result.

# Required C4 invariants

Later C10 formal/checker assurance must establish or refine at least:

```text
ExactlyThirteenPredicateRevisions

NoPrimitiveSemanticFactAuthority

FactIdRecomputes

FactDescriptorUniquePreimage

QualificationKeyRecomputes

QualificationOutcomeNotEncodedInQualificationKey

QualificationReducerDeterministic

QualificationReducerAtMostOnePositiveFact

NonEmptyChallengeObjectionsDoNotImplyOppositeFact

MaterialityPositiveNeedsNoChallenge

QualifiedNonMaterialityRequiresAllFalseAndZeroObjections

QualifiedRefutationRequiresPositiveRefutationAndZeroObjections

QualifiedNoNormativeImpactRequiresExactTargetAndZeroObjections

QualifiedDecisionNecessityRequiresExactSM_D_U_N_ChallengeClosure

AcceptedUCRequiresExactPositiveUCAndZeroObjections

AcceptedRSRequiresExactPositiveRSAndZeroObjections

AcceptedRRRequiresExactPositiveRRAndZeroObjections

RefutationExhaustionHasExactlyThreeLawfulTerminalProofBranches

UniqueCorrectionExhaustionHasExactlyThreeLawfulTerminalProofBranches

OperationalFailureDoesNotEstablishSemanticExhaustion

OldUniqueCorrectionExhaustionCannotBindRevisedDiscoveryStatement

DecisionNecessityCandidateEqualsExactDiscoveryBasisProjection

ClaimedUnreconstructibleFactFailsClosed

DanglingFactDoesNotAuthorizeSemanticRegeneration

ExactNodeSemanticDependencyCycleFailsClosed

SameFactDifferentProvenanceHasOneFactId

SameFactIdHasSameSemanticView

ProofBranchDoesNotChangeSemanticView

CrossRunFactReuse

CrossRootFactReuse

ConsumedFactIsReconstructible

ConsumedFactHasConsumableSemanticClosure

CandidateBoundFactPreservesCandidateRevision

ProjectionDoesNotCreateSemanticAuthority
```

# C4 anti-cheat cases

C4 explicitly closes at least:

```text
forged FactId with mismatched descriptor
→ integrity failure

valid hash but reducer-false claimed Fact
→ integrity failure

dangling FactRef
→ integrity failure

same FactId with two canonical descriptors
→ IDENTITY-HASH-COLLISION

wrong QualificationContract for predicate
→ invalid Fact closure

zero-objection challenge targeting another admission
→ invalid Fact closure

old UniqueCorrectionExhaustion reused after positive Discovery revision
→ rejected by exact target mismatch

mandatory revision skipped
→ exhaustion not derivable

provider/operator/recovery failure
→ does not establish semantic exhaustion

different provenance graphs
→ same FactId when semantic descriptor is same

same FactId
→ same model-visible semantic view

proof branch differs
→ no semantic-input variation

non-consumable C3 Admission dependency
→ downstream Fact not consumable

candidate advance
→ historical candidate-bound Fact preserved

candidate content equality
→ no candidate authority rebinding

cross-root AcceptedUniqueCorrection
→ may feed later RealizationScope without receipt ownership transfer

unreconstructible predecessor Fact
→ fail closed, never rerun predecessor model
```

# Exact C1 coverage

The thirteen C4 predicates cover exactly the semantic Fact concepts named by the
published C1 catalog:

```text
QualifiedPositiveMaterialityFact

QualifiedNonMaterialityFact

QualifiedRefutationFact

RefutationExhaustionWithoutQualifiedRefutationFact

TargetedDiscoveryStatementFact

DecisionRequiredDiscoveryStatementFact

QualifiedNoNormativeImpactFact

UniqueCorrectionExhaustionFact

DecisionNecessityCandidateFact

QualifiedDecisionNecessityFact

AcceptedUniqueCorrectionFact

AcceptedRealizationScopeFact

AcceptedRepairRealizationFact
```

No C1 Fact concept is missing.

No additional C4 PredicateRevision is introduced.

# G-C4 closure

Completion gate `G-C4` is semantically satisfied by this construction when the
artifact is published and verified against ADR-056 and exact C1/C2/C3 authority.

The gate establishes:

```text
every semantic predecessor required by a C1 contract
is representable as one exact typed Fact
```

and:

```text
every such Fact can be mechanically reconstructed
from authoritative semantic history
without same-root receipt ownership
```

It additionally closes:

```text
exact PredicateRevision inventory

qualification reduction

semantic exhaustion reduction

Fact dependency resolution

cross-run/cross-root reuse

well-foundedness

semantic/provenance separation

deterministic semantic projection
```

After publication and audit of this artifact:

```text
C4 = CLOSED
```

Construction may then proceed to:

```text
C5 — candidate-bound identity and CandidateView construction
```

without constructing or activating protocol-v8 runtime artifacts.
