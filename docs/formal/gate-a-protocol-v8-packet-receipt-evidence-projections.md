---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "construction-packet-receipt-evidence-projection"
domain: "turnlock-rust-formal-assurance"
severity: "strict"
name: "Gate A protocol v8 packet, receipt, and evidence projection construction"
---

# Gate A protocol v8 packet, receipt, and evidence projection construction

## Status and authority

This document is the C6 construction closure for protocol-v8 work authorized by
ADR-056 and constrained by the published C1, C2, C3, C4 and C5 construction
closures.

It is a non-protocol-authoritative construction artifact.

It closes the representation boundary between:

```text
semantic identity and authority

model-visible cognitive execution input

execution/provenance evidence

repository evidence projection
```

required before protocol-v8 artifacts can be constructed.

Authority remains:

```text
docs/specification/turnlock-spec.md

accepted ADRs

especially ADR-055 and ADR-056

docs/formal/gate-a-protocol-v8-semantic-question-contract-catalog.md

docs/formal/gate-a-protocol-v8-semantic-identity-algebra.md

docs/formal/gate-a-protocol-v8-semantic-admission-authority-execution-fencing.md

docs/formal/gate-a-protocol-v8-semantic-fact-qualification-resolution.md

docs/formal/gate-a-protocol-v8-candidate-bound-identity-candidate-view.md

accepted existing M2/M4/M8 execution and recovery authority

accepted existing hostile-review execution evidence semantics
```

This document MUST NOT:

```text
change TURNLOCK product semantics

change Gate A semantic subject S

change ADR-055 semantic output meanings

change ADR-056 global semantic identity or single-admission authority

change any C1 SemanticQuestionContract meaning

change C2 identity framing

change C3 admission/fencing semantics

change C4 Fact or qualification semantics

change C5 CandidateRevision/CandidateView semantics

reinterpret published P1-P7 bytes

activate protocol v8

construct protocol-v8 runtime artifacts

construct protocol-v8 schema bytes

construct protocol-v8 prompt bytes

construct protocol-v8 bundle bytes

select SQL tables, lock implementations or cache layouts

create another semantic/evidence authority root

make repository projection identity semantic authority
```

If later construction requires choosing between materially different semantic
meanings rather than mechanically realizing this closure:

```text
STOP
→ decision-required
→ accepted ADR
→ resume from the earliest affected construction stage
```

# C6 construction boundary

C6 closes exactly:

```text
public protocol-v8 representation of C2 semantic reference forms

model-visible cognitive projection rules

FindingAdjudication cognitive basis projection

SurvivingMaterial cognitive basis projection

SemanticAdmission cognitive inheritance boundary

SemanticFact cognitive projection boundary

CandidateView packet projection

canonical cognitive citation namespace

normalized cognitive packet shapes for all 20 C1 questions

execution-receipt reuse decision

semantic-question/QLEK audit projection

SemanticAdmission origin-witness evidence projection

completion-to-admission evidence reconstruction

ReviewCampaign protocol-v8 projection boundary

finding-adjudication supplement protocol-v8 projection

protocol-v8 semantic-contract catalog packaging

protocol-v8 question-realization packaging

protocol-bundle-v8 interpretation structure

prompt reuse/versioning decisions

complete P7 artifact reuse/replacement audit
```

C6 does NOT construct any artifact selected below.

Artifact publication and checker implementation remain C7.

System/module ownership synchronization remains C8/C9.

# Four distinct representation planes

Protocol v8 MUST keep four distinct planes.

## Semantic identity and authority plane

This plane contains exact semantic identities including:

```text
SemanticQuestionContractRevisionId

LogicalQuestionDescriptorV1

QLEK

SemanticValueRefV1

SemanticAdmissionRefV1

SemanticFactRefV1

ExactAuthorityRefV1

QualificationKeyRefV1

SemanticAdmission

SemanticFact

CandidateRevisionId
```

This plane defines semantic identity and authority.

Execution provenance MUST NOT redefine it.

## Cognitive execution plane

This plane contains only the deterministic model-visible semantic projection
authorized for one exact logical question.

It contains:

```text
contract presentation

normalized cognitive basis

exact model-visible semantic inputs

exact contract-derived cognitive constraints

one canonical citation catalog
```

It MUST NOT become semantic identity merely because it is serialized or hashed.

## Execution/provenance plane

This plane contains exact physical execution history including:

```text
Execution

SemanticExecutionBinding

SemanticArmBinding

receipt

protocol attempts

provider/model identity

raw completion

origin witness

timestamps

runtime identity

recovery and reconciliation evidence
```

This plane proves lawful execution.

It does not define QLEK.

## Repository projection plane

This plane contains immutable audit projections including:

```text
ReviewCampaign

finding-adjudication supplement

semantic-question binding projection

origin-witness projection

protocol/catalog/schema artifacts
```

Repository projection paths and ownership MUST NOT define semantic predecessor
availability.

# No reverse semantic derivation from execution packets

Native protocol-v8 construction order is exactly:

```text
authoritative semantic state

→ deterministic exact semantic bindings

→ LogicalQuestionDescriptorV1

→ QLEK

→ global SemanticAdmission lookup

→ model-visible cognitive execution packet only when execution is required
```

A conforming implementation MUST NOT:

```text
construct a rich execution packet first

then delete selected fields

then hash the remainder as semantic identity
```

Packet identity, packet SHA and packet repository location MUST NOT enter QLEK.

# Shared protocol-v8 semantic representation schema

C7 MUST construct one new immutable shared schema:

```text
formal/reviews/schemas/semantic-identity-v1.schema.json
```

It MUST structurally represent, without changing C2 meaning:

```text
SemanticValueRefV1

SemanticAdmissionRefV1

SemanticFactRefV1

ExactAuthorityRefV1

QualificationKeyRefV1

LogicalQuestionDescriptorV1

SemanticValueId lexical form

QLEK lexical form

SemanticAdmissionId lexical form

FactId lexical form

QualificationKey lexical form
```

The schema is representation authority only.

The semantic meanings and hash preimages remain exactly C1-C4 authority.

No alternate inline direct logical-input representation is permitted.

# CognitiveProjectionOf

Define conceptually:

```text
CognitiveProjectionOf(
  exact protocol realization P,
  exact LogicalQuestionDescriptor D,
  exact model-visible CognitivePacket M
)
```

For one exact pair:

```text
(P, D)
```

there MUST be exactly one lawful model-visible packet `M`.

Therefore:

```text
same exact P
+
same exact D

→
same exact CognitivePacket bytes
```

Changing only:

```text
GateARun

receipt

root ownership

supplement ownership

ArtifactRef locator

provider/model identity

timestamps

execution attempt identity

provenance witness
```

MUST NOT change `M`.

Distinct QLEKs MAY lawfully have identical CognitivePacket bytes when the
distinguishing semantic dimension is identity/binding-only rather than
model-visible content.

# FindingAdjudicationCognitiveBasis

For exact valid `FindingAdjudicationBasisV1`, resolve the exact authoritative
closure required by C2 and project exactly one cognitive basis conceptually
equivalent to:

```text
FindingAdjudicationCognitiveBasis {
  formalAssuranceContext: {
    formalSemanticDomains: [
      {
        id
        representation
        module
        integratedSemanticsRequired
        focusedAnalysesAreRestrictions
      }
    ]

    behavioralModalities[]

    assuranceDomains[]
  }

  claims[]

  normativeCoverage[]

  controllingAuthorityContents: [
    {
      role
      id
      contentUtf8
    }
  ]

  sourceFinding: {
    statement
    argument
    counterexample
  }
}
```

The following exact semantic-subject fields remain model-visible where already
part of those projected structures:

```text
formal semantic domain identity and semantic properties

claim IDs and statements

claim normative sources

claim assurance domain

formal-behavioral modality/domain when present

normative coverage entries

authority role

ADR identity where applicable

exact authority UTF-8 contents

exact source-finding substantive statement/argument/counterexample
```

The following MUST NOT be model-visible through this basis:

```text
subject schema version

subject selector

subject SHA

formal/verification.yaml schema_version

project framing field

formal semantic domain repository path

authority repository path

authority SHA

protocol ID

protocol bundle SHA

source ReviewCampaignId

source FindingId

substantiveFindingSha256

source execution IDs

raw finding IDs

packet identity

receipt identity

run

root

storage locator
```

Those values remain available to authoritative validation where required.

# SurvivingMaterialCognitiveBasis

For exact valid `SurvivingMaterialBasisV1`, project exactly:

```text
SurvivingMaterialCognitiveBasis {
  findingAdjudication:
    exact FindingAdjudicationCognitiveBasis

  qualifiedPositiveMateriality:
    exact ResolvedFactSemanticView(
      QualifiedPositiveMateriality
    )

  refutationClosure: {
    kind:
      "exhausted-without-qualified-refutation"
  }
}
```

The exact positive MaterialityAssessment semantic value remains visible.

The exact refutation-exhaustion proof branch MUST NOT be visible.

In particular, the packet MUST NOT distinguish:

```text
initial-not-established

revision-not-established

revised-challenge-objections
```

when those branches establish the same exact
`RefutationExhaustionWithoutQualifiedRefutation` Fact.

The model-visible proposition MUST NOT be worded as proof that the finding is
true.

# SemanticAdmission cognitive projection

For exact consumable SemanticAdmission:

```text
A = SemanticAdmission(K, V)
```

define conceptually:

```text
AdmissionCognitiveSnapshot(A)
```

as:

```text
exact producer cognitive semantic surface

+

exact admitted semantic candidate V
```

The producer cognitive semantic surface is reconstructed from the producer
LogicalQuestionDescriptor and the exact protocol realization.

It MUST NOT be reconstructed by recursively opening the raw semantic/provenance
graph.

The snapshot MUST NOT include:

```text
SemanticAdmissionId

QLEK

producer Execution identity

producer receipt

origin witness

provider/model

run

root

prompt bytes

producer citation catalog
```

A consumer may inherit semantic cognition authorized to the producer.

It MUST NOT inherit producer execution provenance.

This rule MUST preserve the producer visibility boundary.

In particular:

```text
RepairRealization downstream of AcceptedRealizationScope
MUST NOT obtain complete CandidateView
through transitive producer/fact closure
```

# SemanticFact cognitive projection

For exact consumable SemanticFact `F`, use exactly:

```text
ResolvedFactSemanticView(F)
```

as defined by C4.

Generic Fact projection MUST NOT:

```text
open QualificationKey proof closure

open anchor SemanticAdmission cognitive snapshot

copy challenge history

copy receipt history

copy CandidateRevision identity

copy CandidateView transitively
```

Candidate binding remains mechanically reconstructible where C4/C5 require it,
but it is not automatically model-visible.

The only current protocol-v8 direct-Fact context lift required by C6 is:

```text
NoNormativeImpactChallenge@1
+
exact TargetedDiscoveryStatementFact

→
exact producer SM cognitive basis
+
exact targeted no-normative-impact statement
```

That lift MUST NOT expose sibling Discovery statements.

No other current direct Fact input receives a generic context lift.

No context lift exists by default.

# CandidateView cognitive projection

The semantic CandidateView value remains exactly C5:

```text
CandidateViewV1 {
  gitObjectFormat

  entries[]
}
```

with exact entries:

```text
CandidateViewEntryV1 {
  pathBytesBase64url

  state
}
```

and exact C5 states/byte encodings.

For model-visible packet projection C6 additionally permits only deterministic
presentation fields:

```text
coverage

pathUtf8
```

`coverage` is exactly one of:

```text
{ kind: "complete" }

or

{
  kind: "readable-paths"
}
```

with the exact readable-path set already fixed by the consuming contract.

For each entry:

```text
pathUtf8 =
exact decoded raw path string when valid UTF-8
or null otherwise
```

The model-visible CandidateView projection MUST NOT contain:

```text
CandidateRevisionId

rootTreeObjectId

ArtifactRef

materialization ArtifactRef

workspace path

checkout path

HEAD

index identity

receipt

root
```

For RepairRealization, packet coverage is exactly the AcceptedRealizationScope
`readable_paths`.

No physical state outside that scoped CandidateView may become visible.

# Contract-derived cognitive constraints

A contract may expose deterministic conveniences derived only from exact logical
inputs when they create no new authority.

Current P8 RealizationScope requires exactly one such physical constraint class:

```text
nonWritableControllingAuthorityPaths
```

It is derived mechanically as:

```text
Paths(complete CandidateView)

INTERSECT

exact controlling product-authority repository paths
resolved from FA integrity closure
```

Every resulting path is already present in the CandidateView.

This field does not reveal a new path.

It only marks an already-visible candidate path as mechanically non-writable.

No corresponding global root-tree identity may be exposed.

# Canonical cognitive citation catalog

Every P8 CognitivePacket MUST contain one deterministic citation catalog derived
after cognitive normalization.

The catalog is:

```text
canonical handles

→

already-present exact cognitive semantic material
```

It is not another source of content or authority.

The catalog MUST NOT contain:

```text
receipt identities

run identities

root identities

execution identities

ArtifactRef identities

repository storage locators

packet SHA

raw-output locators
```

For every citable semantic item:

```text
one exact citable semantic item
→ exactly one canonical handle
```

Packet layout position, JSON Pointer and content hash MUST NOT be used as the
primary cognitive citation identity.

Existing structured citation identities remain authoritative where already
defined, including:

```text
source-finding

authority-content roles and ADR IDs

TL-CLAIM-NNN

TL-INV-NNN

formal semantic domain identity

behavioral modality

assurance domain

prior challenge objection ID

UniqueCorrection requirement ordinal
```

CandidateView path citation uses the exact already-authoritative:

```text
pathBytesBase64url
```

For output fields that remain `evidence_references: string[]`, every string MUST
resolve to exactly one canonical handle in the packet citation catalog.

An unresolved citation makes the completion protocol-invalid.

Changing only provenance MUST NOT change the citation catalog.

# Cognitive closure normalization

Before packet emission:

```text
resolve every direct logical input

project it using its exact C6 projection rule

union semantic cognitive material

deduplicate exact shared bases/values

require independently reachable copies of the same semantic basis to agree

rebuild one citation catalog over the normalized final material
```

There is no direct-input precedence rule.

Conflicting independently reconstructed semantic bases fail closed.

Historical packet citation catalogs are never concatenated.

# Normalized 20 CognitivePacket semantic surfaces

The exact current 20 C1 contracts normalize as follows.

## MaterialityAssessmentInitial@1

```text
root basis:
FA

additional semantic inputs:
none
```

## MaterialityAssessmentRevision@1

```text
root basis:
FA

additional semantic inputs:
prior exact MaterialityAssessment candidate
prior exact MaterialityChallenge semantic value
```

## MaterialityChallenge@1

```text
root basis:
challenged producer FA

additional semantic inputs:
exact challenged MaterialityAssessment candidate

contract presentation:
materiality challenge
exact seven ordered materiality objectives
```

## RefutationInitial@1

```text
root basis:
FA

additional semantic inputs:
exact positive MaterialityAssessment semantic view
```

## RefutationRevision@1

```text
root basis:
FA

additional semantic inputs:
exact positive MaterialityAssessment semantic view
prior exact Refutation candidate
prior exact RefutationChallenge semantic value
```

## RefutationChallenge@1

```text
root basis:
challenged producer FA

additional semantic inputs:
exact positive MaterialityAssessment semantic view
exact challenged Refutation candidate

contract presentation:
refutation challenge
exact seven ordered refutation objectives
```

## DiscoveryClassificationInitial@1

```text
root basis:
SM

additional semantic inputs:
none
```

## NoNormativeImpactChallenge@1

```text
root basis:
producer SM via the only current Fact context lift

additional semantic inputs:
exact targeted no-normative-impact statement

contract presentation:
normative-impact challenge
exact seven ordered no-normative-impact objectives
```

Sibling Discovery statements MUST NOT be included.

## DiscoveryNoNormativeImpactRevision@1

```text
root basis:
SM

additional semantic inputs:
exact prior no-normative-impact statement
exact prior NoNormativeImpactChallenge semantic value
```

## DecisionNecessityChallenge@1

```text
root basis:
SM

additional semantic inputs:
exact decision-required statement
exact UniqueCorrection-exhaustion proposition bound to that statement
exact DecisionNecessity candidate

contract presentation:
decision-necessity challenge
exact eight ordered decision-necessity objectives
```

No UniqueCorrection exhaustion proof branch is visible.

## DiscoveryDecisionRequiredRevision@1

```text
root basis:
SM

additional semantic inputs:
exact prior decision-required statement
exact prior UniqueCorrection-exhaustion proposition
exact prior DecisionNecessity candidate
exact prior DecisionNecessityChallenge semantic value
```

The exhaustion proposition is inherited from the exact prior challenge Admission
semantic surface.

It is not added as another direct QLEK input.

## UniqueCorrectionInitial@1

```text
root basis:
SM

additional semantic inputs:
exact whole Discovery semantic result
exact targeted Discovery statement
```

The whole Discovery admission/result MUST NOT be reduced to only the target
statement.

## UniqueCorrectionRevision@1

```text
root basis:
SM

additional semantic inputs:
exact whole Discovery semantic result
exact targeted Discovery statement
prior exact UniqueCorrection candidate
prior exact UniqueCorrectionChallenge semantic value
```

## UniqueCorrectionChallenge@1

```text
root basis:
challenged producer SM

additional semantic inputs:
exact producer Discovery semantic result
exact target statement
exact challenged UniqueCorrection candidate

contract presentation:
derivation challenge
exact five ordered UniqueCorrection objectives
```

If the challenged candidate is a revision, its producer semantic surface may
include the exact prior candidate/challenge semantic history committed by that
revision.

Execution provenance remains excluded.

## RealizationScopeInitial@1

```text
root basis:
SM

additional semantic inputs:
exact AcceptedUniqueCorrection semantic view
exact complete CandidateView projection

contract-derived cognitive constraints:
nonWritableControllingAuthorityPaths
```

CandidateRevisionId is not model-visible.

## RealizationScopeRevision@1

```text
root basis:
SM

additional semantic inputs:
exact AcceptedUniqueCorrection semantic view
exact same complete CandidateView projection
prior exact RealizationScope candidate
prior exact RealizationScopeChallenge semantic value

contract-derived cognitive constraints:
nonWritableControllingAuthorityPaths
```

CandidateRevisionId is not model-visible.

## RealizationScopeChallenge@1

```text
root basis:
challenged producer SM

additional semantic inputs:
exact AcceptedUniqueCorrection semantic view
exact producer complete CandidateView projection
exact challenged RealizationScope candidate

contract-derived cognitive constraints:
nonWritableControllingAuthorityPaths

contract presentation:
derivation challenge
exact two ordered RealizationScope objectives
```

## RepairRealizationInitial@1

```text
root basis:
SM

additional semantic inputs:
exact AcceptedUniqueCorrection semantic view
exact AcceptedRealizationScope semantic view
exact scoped CandidateView projection
```

CandidateRevisionId is not model-visible.

Opening AcceptedRealizationScope proof/anchor closure to recover complete
CandidateView is forbidden.

## RepairRealizationRevision@1

```text
root basis:
SM

additional semantic inputs:
exact AcceptedUniqueCorrection semantic view
exact AcceptedRealizationScope semantic view
exact same scoped CandidateView projection
prior exact RepairRealization candidate
prior exact RepairRealizationChallenge semantic value
```

CandidateRevisionId is not model-visible.

## RepairRealizationChallenge@1

```text
root basis:
challenged producer SM

additional semantic inputs:
exact AcceptedUniqueCorrection semantic view
exact AcceptedRealizationScope semantic view
exact producer scoped CandidateView projection
exact challenged RepairRealization candidate

contract presentation:
repair challenge
exact nine ordered RepairRealization objectives
```

Complete CandidateView MUST NOT become visible.

# Protocol-v8 cognitive packet artifact selection

C7 MUST construct exactly one shared model-visible packet schema:

```text
formal/reviews/schemas/cognitive-execution-packet-v1.schema.json
```

It replaces, for protocol-v8 semantic executions only:

```text
formal/reviews/schemas/adjudication-packet-v1.schema.json

formal/reviews/schemas/challenge-packet-v1.schema.json
```

Those published P7 schemas remain immutable historical artifacts.

The new shared packet structurally represents:

```text
contract presentation

one normalized root basis

normalized semantic inputs

contract-derived cognitive constraints

one citation catalog
```

The packet schema MUST NOT independently redefine all 20 SQC semantics through a
second competing contract inventory.

Contract-specific semantic validity is checked using the exact SQC catalog and
checker logic.

# Execution receipt audit decision

Protocol v8 reuses unchanged:

```text
formal/reviews/schemas/execution-receipt-v4.schema.json
```

No execution-receipt-v5 is required by C6.

The v4 receipt already preserves exact execution/protocol truth:

```text
one logical cognitive execution

ordered protocol attempts

one runner Execution identity per attempt

one M4 call identity per attempt

provider/model/runtime provenance

exact prompt ArtifactRef

exact packet ArtifactRef

sealed raw output for completed attempts

protocol errors

exact qualifying attempt

resolved effective model identity
```

For protocol-v8 semantic executions:

```text
all receipt attempts for one logical semantic execution
MUST bind the same exact QLEK
```

The qualifying attempt is the exact origin Execution for the native admitted
candidate.

The receipt itself is not SemanticAdmission authority.

It need not contain SemanticAdmissionId.

Initial-reviewer receipt usage remains outside C1 single-admission semantics and
continues under its existing hostile-review contract.

# Semantic-question binding projection

C7 MUST construct:

```text
formal/reviews/schemas/semantic-question-binding-v1.schema.json
```

and a corresponding immutable protocol-v8 audit projection.

Conceptually:

```text
SemanticQuestionBindingV1 {
  exact LogicalQuestionDescriptorV1

  exact recomputed QLEK

  exact transitive semantic-value preimage closure
  reachable from direct SemanticValueRef inputs
}
```

The semantic-value closure is ordered canonically by:

```text
(valueType, valueId)
```

and contains each exact semantic value once.

It includes semantic-value preimages such as:

```text
FindingAdjudicationBasisV1

SurvivingMaterialBasisV1

CandidateViewV1
```

when reachable from the exact descriptor.

It does NOT inline:

```text
SemanticAdmission preimages

SemanticFact proof closures

ExactAuthority implementation history
```

Those resolve through their own authoritative semantic/history mechanisms.

The projection makes exact:

```text
QLEK
→ descriptor
→ direct semantic references
```

auditable without making repository path or projection identity part of QLEK.

A different projection path for the same exact semantic binding MUST NOT create
another QLEK.

# SemanticAdmission origin witness

C7 MUST construct:

```text
formal/reviews/schemas/semantic-admission-origin-witness-v1.schema.json
```

The witness represents the C3
`ExecutionEvidenceOf(E, SemanticAdmission(K,V))` relation.

For one exact native admission it must be sufficient to reconstruct:

```text
exact QLEK K

exact SemanticAdmissionId

exact canonical semantic candidate V

exact SemanticQuestionBinding for K

exact immutable execution receipt

every receipt attempt's exact SemanticExecutionBinding to K

every receipt-admissible attempt's lawful SemanticArmBinding

exact qualifying attempt

exact sealed raw completion

deterministic raw-output-to-candidate derivation

Admission(K) == V
```

The exact qualifying attempt satisfies:

```text
origin ExecutionId
==
receipt.qualifying_attempt_id
```

For a multi-attempt receipt:

```text
every attempt
→ same exact K
```

A protocol retry MUST NOT switch QLEK.

Arm generation remains execution/provenance fencing state only.

It MUST NOT alter:

```text
QLEK

SemanticAdmissionId

SemanticFact identity

qualification identity

semantic candidate
```

Generation values are interpreted only under their exact coherent coordination
history.

A witness is not a self-asserting semantic authority.

The checker must validate every required binding against authoritative history
and exact immutable referenced evidence.

The first native:

```text
SemanticAdmission(K,V)

+

exact first origin witness
```

is one atomic authoritative semantic-history transition under C3.

Additional lawful executions establishing the same exact `(K,V)` add additional
origin witnesses and MUST NOT create another SemanticAdmission.

C6 does not require a standalone repository file for SemanticAdmission itself.

# Completion-to-admission completeness

Protocol-v8 evidence MUST support both directions.

## Admission to evidence

For every native SemanticAdmission:

```text
Admission(K,V)
→ at least one exact lawful origin witness
→ exact receipt
→ exact qualifying attempt
→ exact raw completion
→ deterministic exact V
```

## Completion to admission

For every protocol-valid semantic completion:

```text
exact Execution E

→ exact SemanticExecutionBinding(E,K)

→ exact protocol-valid candidate V
```

authoritative semantic history MUST contain or reconcile to:

```text
Admission(K,V)
```

or an exact C3 semantic conflict/hazard state.

A protocol-valid completion MUST NOT be discarded and replaced by another
semantic sample.

Crash between completion and admission creates mandatory reconciliation.

It does not authorize another semantic execution.

# ReviewCampaign protocol-v8 projection

C7 MUST construct:

```text
formal/reviews/meta-schemas/review-evidence-v6.schema.json
```

Protocol-v8 `ReviewCampaign` becomes the immutable projection of one real
initial hostile-review campaign.

Conceptually it contains:

```text
review identity

review class

repository commit

reviewed subjects

protocol

initial-reviewer executions

substantive normalized findings

supersession metadata

start/completion provenance
```

Protocol-v8 ReviewCampaign does NOT own post-review semantic execution closure.

Therefore protocol-v8 review-evidence-v6 MUST NOT contain the P7 semantic-root
fields:

```text
supporting_executions[]

re_adjudications[]
```

Protocol-v8 normalized findings MUST NOT embed current post-review adjudication
authority through:

```text
materiality

status

disposition
```

The substantive finding remains exactly reconstructible from:

```text
finding_id

sources

statement

argument

counterexample
```

Initial-reviewer executions remain campaign-owned hostile-review evidence.

No initial-reviewer SemanticQuestionContract or SemanticAdmission is invented by
C6.

# FindingAdjudicationSupplementV2

C7 MUST construct:

```text
formal/reviews/schemas/finding-adjudication-supplement-v2.schema.json
```

The supplement remains an immutable append-only repository projection for one
exact original finding under one exact current protocol.

Its semantic key remains exactly:

```text
source ReviewCampaignId

+

source FindingId

+

validated substantiveFindingSha256

+

exact protocol P
```

For one exact key:

```text
zero
OR
exactly one
```

supplement is valid.

Conceptually the v2 supplement contains exactly:

```text
semantic subject identity

exact protocol identity

source finding identity

effective adjudication projection
```

The effective adjudication is exactly one of:

```text
qualified-non-material
→ exact SemanticFactRef<QualifiedNonMateriality@1>

qualified-refutation
→ exact SemanticFactRef<QualifiedRefutation@1>

surviving-material
→ exact SemanticValueRef<SurvivingMaterialBasis@1>
```

The `kind` is a projection discriminator only.

It MUST agree with the exact referenced semantic Fact/value.

The checker MUST cross-bind the referenced Fact/value back to the exact
supplement source finding, semantic subject and protocol.

The supplement MUST NOT contain:

```text
supporting_executions[]

reused_executions[]

materiality receipt

materiality challenge receipt

refutation receipt

refutation challenge receipt

refutation terminal receipt

origin-witness ownership list

adjudicating_review_id
```

A later consuming run/root does not acquire predecessor receipt ownership.

Additional origin witnesses for an already-existing exact Admission MUST NOT
invalidate or change an already-correct supplement projection.

Candidate advance MUST NOT change a supplement when:

```text
source finding

S

P

effective semantic adjudication
```

remain unchanged.

Downstream:

```text
AcceptedUniqueCorrection

AcceptedRealizationScope

AcceptedRepairRealization

RepairIntent

DecisionRequest
```

do not change `effective_adjudication.kind`.

# Protocol-v8 effective adjudication derivation

For one exact source finding under exact current P:

```text
QualifiedNonMateriality Fact
→ qualified-non-material

QualifiedRefutation Fact
→ qualified-refutation

valid exact SurvivingMaterialBasis
→ surviving-material
```

Models do not emit these final states directly.

No exact current-P supplement means no complete repository projection of current
effective adjudication.

That absence does not create a new semantic result.

# Semantic-contract artifact packaging

C7 MUST create a new directory:

```text
formal/reviews/contracts/
```

and exactly these three protocol-v8 semantic-contract artifacts:

```text
formal/reviews/contracts/gate-a-semantic-question-contracts-v8.json

formal/reviews/contracts/gate-a-predicate-revisions-v8.json

formal/reviews/contracts/gate-a-qualification-contracts-v8.json
```

C7 MUST also construct exactly these schemas:

```text
formal/reviews/schemas/semantic-question-contract-catalog-v1.schema.json

formal/reviews/schemas/predicate-revision-catalog-v1.schema.json

formal/reviews/schemas/qualification-contract-catalog-v1.schema.json
```

The three exact catalogs contain respectively:

```text
20 SemanticQuestionContractRevision definitions

13 PredicateRevision definitions

7 QualificationContractRevision definitions
```

Their symbolic IDs are semantic authority.

Artifact path and artifact SHA are NOT the semantic revision identity.

For one symbolic revision ID across protocol lineage:

```text
same revision ID
→ same exact canonical semantic definition
```

Changing semantic meaning requires a new revision ID.

Changing only:

```text
prompt realization

packet packaging

schema packaging

repository path
```

without semantic change does not create another semantic revision.

Catalog arrays are canonical and ordered lexicographically by exact symbolic
revision ID.

Duplicate symbolic IDs are invalid.

# Protocol-v8 question realizations

Protocol v8 separates:

```text
semantic contract meaning
```

from:

```text
exact protocol realization
```

The protocol bundle contains exactly one `question_realizations` entry for every
one of the 20 C1 SQC revisions.

Each realization binds exactly:

```text
SemanticQuestionContractRevisionId

packet schema key

prompt key

output schema key
```

The relation is protocol-specific and remains directly in the bundle.

No fourth external realization registry is introduced.

All 20 current semantic questions use:

```text
cognitive-execution-packet-v1
```

Producer/revision questions other than RepairRealization use:

```text
adjudication prompt

adjudication-output-v1
```

RepairRealization initial/revision use:

```text
repair prompt

adjudication-output-v1
```

All seven challenge SQC revisions use:

```text
challenge prompt

challenge-output-v1
```

Exactly 20 unique SQC revisions must be covered.

No SQC revision may have zero or multiple realizations in one bundle.

# Protocol prompt audit

C6 selects the following exact reuse/versioning decisions.

## Reuse unchanged

```text
formal/reviews/prompts/gate-a-initial-review-v1.md
```

Initial-review cognition remains outside the C1 semantic-admission architecture.

## New adjudication prompt

C7 MUST construct:

```text
formal/reviews/prompts/gate-a-adjudication-v3.md
```

because v2 contains P7 representation-specific revision wording including:

```text
revision.ordinal

prior closure subject

prior producer evidence
```

The v3 prompt must consume the normalized P8 cognitive packet representation
without changing C1 output semantics.

It must require every emitted evidence reference to resolve through the exact
packet citation catalog.

## New challenge prompt

C7 MUST construct:

```text
formal/reviews/prompts/gate-a-challenge-v2.md
```

It preserves challenge-output-v1 semantics and exact challenge objectives.

It must additionally require every emitted evidence reference to resolve through
the exact packet citation catalog.

## New repair prompt

C7 MUST construct:

```text
formal/reviews/prompts/gate-a-repair-v3.md
```

It preserves RepairRealization semantic output meaning.

It MUST remove the P7 statement permitting a currently absent path to be
proposed as present.

Current P8 automatic RepairRealization can operate only on exact paths already
present in AcceptedRealizationScope writable authority and scoped CandidateView.

# Published P7 artifact audit

The final C6 classification is exactly:

```text
REUSE EXACT:

formal/reviews/schemas/raw-review-output-v1.schema.json

formal/reviews/schemas/adjudication-output-v1.schema.json

formal/reviews/schemas/challenge-output-v1.schema.json

formal/reviews/schemas/execution-receipt-v4.schema.json

formal/reviews/prompts/gate-a-initial-review-v1.md
```

```text
P7 HISTORICAL ONLY / NOT REFERENCED AS P8 INPUT REPRESENTATION:

formal/reviews/schemas/adjudication-packet-v1.schema.json

formal/reviews/schemas/challenge-packet-v1.schema.json

formal/reviews/schemas/finding-adjudication-supplement-v1.schema.json

formal/reviews/meta-schemas/review-evidence-v5.schema.json

formal/reviews/meta-schemas/review-protocol-bundle-v7.schema.json

formal/reviews/prompts/gate-a-adjudication-v2.md

formal/reviews/prompts/gate-a-challenge-v1.md

formal/reviews/prompts/gate-a-repair-v2.md
```

All published P7 bytes remain immutable.

# Protocol-bundle-v8 meta-schema

C7 MUST construct:

```text
formal/reviews/meta-schemas/review-protocol-bundle-v8.schema.json
```

and:

```text
formal/reviews/protocols/gate-a-campaign-protocol-v8.json
```

with exact predecessor:

```text
formal/reviews/protocols/gate-a-campaign-protocol-v7.json
```

The P8 bundle retains:

```text
protocol_bundle_schema_version

protocol_id

predecessor

review_class

meta_schemas

prompts

schemas

reviewer_profiles

policies
```

and adds exactly:

```text
semantic_contracts

question_realizations
```

`semantic_contracts` contains exactly three ArtifactRefs:

```text
questions

predicates

qualifications
```

to the three selected contract catalogs.

The P8 `schemas` registry must reference the selected reused/new schemas,
including:

```text
raw-review-output

execution-receipt

adjudication-output

challenge-output

semantic-identity

cognitive-execution-packet

semantic-question-binding

semantic-admission-origin-witness

semantic-question-contract-catalog

predicate-revision-catalog

qualification-contract-catalog

finding-adjudication-supplement
```

P8 does NOT register:

```text
adjudication-packet

challenge-packet
```

as protocol-v8 execution input schemas.

P8 `meta_schemas` binds exactly:

```text
protocol-bundle
→ review-protocol-bundle-v8.schema.json

review-evidence
→ review-evidence-v6.schema.json
```

# Protocol-v8 policy boundary

P8 must not duplicate SQC semantics inside an independent
`policies.challenge.closure_contracts` inventory.

Therefore the P7 bundle field:

```text
policies.challenge
```

does not survive as a protocol-v8 semantic-contract registry.

Its SQC-specific semantics, including:

```text
challenge kind

ordered objective set

revision family

revision authorization

withdrawal behavior

bounded revision structure
```

are owned by the exact SQC catalog.

The following P7 global policy semantics remain applicable and may retain their
existing exact meanings in protocol v8:

```text
normalization

retry

model_identity

decision_request

external_outcomes

artifact_lifecycle

reviewer_acquisition

supporting_role_acquisition
```

ADR-056/C3 anti-model-shopping and single-admission semantics are validated
directly as protocol-v8 conformance rules.

They MUST NOT be represented by a second conflicting semantic policy source.

# Finite protocol root

The protocol-v8 bundle remains the finite mechanical interpretation root.

Validation is conceptually:

```text
load exact P8 bundle

→ validate against exact v8 meta-schema

→ validate exact predecessor

→ validate exact finite referenced meta-schemas

→ validate exact finite referenced schemas

→ validate exact finite semantic-contract catalogs

→ validate exact prompts

→ validate exactly 20 question realizations
```

No:

```text
registry of registries

dynamic semantic-contract discovery

recursive schema-of-schema chain

ambient filesystem search for semantic contracts
```

is introduced.

# Artifact set selected by C6 for C7

C7 is authorized to construct exactly the required new artifact classes selected
below.

## New meta-schemas

```text
formal/reviews/meta-schemas/review-protocol-bundle-v8.schema.json

formal/reviews/meta-schemas/review-evidence-v6.schema.json
```

## New schemas

```text
formal/reviews/schemas/semantic-identity-v1.schema.json

formal/reviews/schemas/cognitive-execution-packet-v1.schema.json

formal/reviews/schemas/semantic-question-binding-v1.schema.json

formal/reviews/schemas/semantic-admission-origin-witness-v1.schema.json

formal/reviews/schemas/semantic-question-contract-catalog-v1.schema.json

formal/reviews/schemas/predicate-revision-catalog-v1.schema.json

formal/reviews/schemas/qualification-contract-catalog-v1.schema.json

formal/reviews/schemas/finding-adjudication-supplement-v2.schema.json
```

## New semantic-contract artifacts

```text
formal/reviews/contracts/gate-a-semantic-question-contracts-v8.json

formal/reviews/contracts/gate-a-predicate-revisions-v8.json

formal/reviews/contracts/gate-a-qualification-contracts-v8.json
```

## New prompts

```text
formal/reviews/prompts/gate-a-adjudication-v3.md

formal/reviews/prompts/gate-a-challenge-v2.md

formal/reviews/prompts/gate-a-repair-v3.md
```

## New protocol bundle

```text
formal/reviews/protocols/gate-a-campaign-protocol-v8.json
```

## Reused exact artifacts

```text
formal/reviews/schemas/raw-review-output-v1.schema.json

formal/reviews/schemas/adjudication-output-v1.schema.json

formal/reviews/schemas/challenge-output-v1.schema.json

formal/reviews/schemas/execution-receipt-v4.schema.json

formal/reviews/prompts/gate-a-initial-review-v1.md
```

C6 does not authorize creation of any additional protocol-v8 artifact class
without returning to construction analysis.

# C6 required invariants

C6 closes at least:

```text
CognitiveProjectionFunctional

CognitivePacketNotQLEKAuthority

ProvenanceChangeDoesNotChangeCognitivePacket

FindingAdjudicationCognitiveProjectionSoundness

SurvivingMaterialCognitiveProjectionSoundness

QPMExactSemanticViewVisible

RefutationExhaustionProofBranchNotVisible

AdmissionSnapshotRequiresConsumableAdmission

AdmissionSnapshotPreservesProducerVisibilityBoundary

FactProjectionUsesResolvedFactSemanticView

FactProjectionDoesNotOpenQualificationClosure

NoFactContextLiftByDefault

NNIChallengeLiftUsesProducerSMOnly

CandidateRevisionNotModelVisible

ScopedCandidateViewDoesNotWiden

CitationCatalogFunctional

CitationCatalogExcludesProvenance

FreeStringCitationMustResolve

CognitiveClosureSharedBasisDeduplicated

CognitiveClosureConflictFailsClosed

ReceiptSemanticQuestionSingleBinding

ProtocolRetryCannotSwitchQLEK

OriginExecutionIsQualifyingAttempt

OriginWitnessAdmissionExact

FirstAdmissionHasAtomicFirstWitness

AdditionalWitnessDoesNotCreateAdmission

EveryProtocolValidSemanticCompletionIsAdmissionReconciled

ReviewCampaignContainsInitialReviewProductionOnly

ReviewCampaignDoesNotOwnPostReviewSemanticExecutions

SupplementDoesNotOwnReceipts

SupplementEffectiveStateDerivedNotAsserted

SupplementSemanticKeyUnchanged

AdditionalOriginWitnessDoesNotInvalidateSupplement

CandidateAdvanceDoesNotChangeFindingSupplement

SemanticRevisionIdCannotBeRedefined

QuestionRealizationCoverageExact
```

# C6 anti-cheat cases

C6 explicitly rejects at least:

```text
packet SHA used as QLEK
→ invalid

receipt path added to logical input
→ invalid

provider/model added to logical input
→ invalid unless future accepted SQC explicitly says otherwise

different root ownership changes QLEK
→ invalid

same exact logical question serialized with two lawful cognitive packets
→ invalid

Fact projection opens anchor Admission automatically
→ invalid

AcceptedRealizationScope leaks complete CandidateView into RepairRealization
→ invalid

NNI TargetedDiscoveryStatement Fact exposes sibling Discovery statements
→ invalid

refutation exhaustion proof branch becomes model-visible
→ invalid

CandidateRevisionId emitted as cognitive CandidateView identity
→ invalid

rootTreeObjectId emitted in scoped CandidateView packet
→ invalid

free-string evidence reference does not resolve to citation catalog
→ protocol-invalid completion

protocol retry attempt bound to another QLEK
→ invalid

native Admission without lawful origin witness
→ invalid

protocol-valid completion omitted from Admission history and resampled
→ invalid

later consuming root copies predecessor receipt ownership
→ invalid

supplement-v2 owns supporting_executions[]
→ invalid

supplement effective state asserted without matching exact Fact/value
→ invalid

additional origin witness changes supplement bytes
→ invalid design

same symbolic SQC revision ID with changed semantic definition
→ invalid

same symbolic PredicateRevisionId with changed semantic definition
→ invalid

same symbolic QualificationContractRevisionId with changed semantic definition
→ invalid

packet schema independently redefines a second conflicting 20-contract inventory
→ invalid

P8 policies.challenge independently duplicates the C1 SQC catalog
→ invalid

construct any P8 artifact before C7
→ stage violation
```

# Exact G-C6 coverage

Completion gate `G-C6` requires:

```text
every P8 semantic dependency has exactly one representation

AND

every provenance edge remains auditable

AND

changing only provenance locator/root ownership cannot change QLEK
```

This construction satisfies the gate because:

```text
C2 semantic identities have one selected shared public representation

all 20 C1 questions have one deterministic cognitive projection architecture

FA and SM have exact normalized cognitive bases

Admissions inherit producer cognition without execution provenance

Facts expose only exact C4 semantic views unless one contract-specific lift is
explicitly authorized

CandidateView projection preserves C5 physical visibility boundaries

one canonical citation catalog is derived after normalization

execution receipt v4 remains exact execution truth

SemanticAdmission origin witness separately binds execution truth to exact QLEK
and Admission

ReviewCampaign and supplement are repository projections rather than semantic
namespaces

effective adjudication is derived from exact semantic Facts/values

the protocol bundle binds exact semantic catalogs separately from exact
question realizations

all P7 artifacts are classified as exact reuse or historical-only

no C7 artifact is constructed by C6
```

Therefore:

```text
G-C6 = CLOSED
```

C7 may now construct the exact inactive protocol-v8 artifact set selected by this
document.

Protocol v8 remains inactive.

Protocol v6 remains current until explicit later activation authority changes
`formal/verification.yaml`.
