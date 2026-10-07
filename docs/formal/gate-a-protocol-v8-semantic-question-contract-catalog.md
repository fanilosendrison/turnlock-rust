---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "construction-contract-catalog"
domain: "turnlock-rust-formal-assurance"
severity: "strict"
name: "Gate A protocol v8 SemanticQuestionContract catalog"
---

# Gate A protocol v8 SemanticQuestionContract catalog

## Status and authority

This document is the C1 construction closure for the protocol-v8 work authorized by ADR-056.

It is a non-protocol-authoritative construction artifact.

Its purpose is to define the exact semantic-question contract catalog that later protocol-v8 construction must materialize without semantic discretion.

Authority remains:

```text
docs/specification/turnlock-spec.md
accepted ADRs
especially ADR-055 and ADR-056
published immutable protocol-v7 artifacts
```

This document MUST NOT:

```text
change TURNLOCK product semantics
change Gate A semantic subject S
reinterpret ADR-055
reinterpret ADR-056
activate protocol v8
select packet/schema serialization
define QLEK byte framing
define FactId byte framing
define storage architecture
define execution fencing implementation
```

If implementation of this catalog requires choosing between materially distinct protocol meanings not uniquely determined by accepted authority:

```text
STOP
→ decision-required
→ accepted ADR
→ return to the earliest affected C-stage
```

## C1 completion objective

C1 is complete only if every semantic producer, semantic revision and hostile semantic challenge used by protocol v8 has one exact immutable semantic-question contract definition.

The complete C1 set is:

```text
6 initial producer contracts
+
7 revision contracts
+
7 challenge contracts
=
20 SemanticQuestionContract revisions
```

No additional semantic-question family is authorized by C1.

## Contract identity at C1

Each contract has one exact construction identity:

```text
<ContractName>@1
```

For example:

```text
MaterialityAssessmentInitial@1
```

This construction identity is immutable once C1 is closed.

C2/C6 will define the exact public serialized and/or content-addressed representation of `SemanticQuestionContractRevisionId`.

Those later representation decisions MUST preserve a one-to-one mapping with the exact C1 identities in this catalog.

A semantic change to one contract requires a distinct contract revision identity.

Changing only:

```text
prompt
provider
model
reviewer profile
runtime implementation
receipt
packet layout
storage locator
```

does not create another contract revision unless the change alters what counts as a semantically correct answer.

## Shared identity modes

C1 uses the following semantic identity modes.

### Exact semantic value

The exact canonical semantic value of one typed immutable value.

Examples:

```text
FA
SM
CandidateView
```

### Exact SemanticAdmission

The exact identity of one admitted semantic candidate:

```text
SemanticAdmissionId
```

which commits:

```text
exact QLEK
+
exact semantic candidate value
```

Execution provenance is excluded.

### Exact semantic fact

One exact mechanically reconstructible semantic fact.

Examples:

```text
QualifiedPositiveMaterialityFact
AcceptedUniqueCorrectionFact
AcceptedRealizationScopeFact
UniqueCorrectionExhaustionFact
TargetedDiscoveryStatementFact
```

Its exact `PredicateRevisionId` / `FactId` representation belongs to C4.

### Exact mechanically derived fact

One deterministic semantic fact whose value is mechanically derived rather than model-produced.

Example:

```text
DecisionNecessityCandidateFact
```

### Exact nominal authority

An immutable identity whose distinct occurrences remain distinct even if their materialized contents are equal.

Protocol v8 uses this mode for:

```text
CandidateRevisionId
```

### Exact extensional physical value

The exact observable physical state supplied to cognition.

Protocol v8 uses this mode for:

```text
CandidateView
```

A CandidateView never substitutes for CandidateRevision identity.

## Shared semantic-value rule

Unless this catalog explicitly states otherwise, protocol-v8 bootstrap semantic value equality is:

```text
exact structural semantic equality
```

No fuzzy semantic equivalence is introduced by C1.

Therefore differences in exact semantic payload such as:

```text
arguments
rationales
authority references
evidence references
array order
candidate statements
proposed exact bytes
```

remain value-significant when they are part of the semantic result domain.

Protocol/envelope-only fields such as:

```text
schema version
task discriminator
challenge kind
```

do not become duplicate semantic payload merely because an execution artifact carries them.

They are owned by the applicable contract.

Exact canonical byte encoding belongs to C2.

## Reused immutable output-value authority

ADR-056 changes semantic identity, semantic dependency, admission, fencing and evidence topology.

It does not automatically redefine protocol-v7 semantic result value domains.

Unless explicitly changed in this catalog, protocol-v8 reuses the exact semantic result value semantics already defined by the immutable protocol-v7 artifacts, including:

```text
formal/reviews/schemas/adjudication-output-v1.schema.json

formal/reviews/schemas/challenge-output-v1.schema.json
```

Published protocol-v7 bytes remain immutable.

C6 determines whether those exact immutable schemas can be directly referenced by protocol v8 or whether new schema artifacts are required to represent the same C1 semantics.

## Shared challenge semantic value

Every hostile challenge SQC uses the exact semantic challenge value:

```text
ChallengeSemanticValue {
    objective_assessments[]
    objections[]
}
```

Each objective assessment binds:

```text
objective
objection_ids[]
```

Each objection binds:

```text
challenge_objection_id
objective
statement
argument
evidence_references[]
```

The applicable challenge contract owns:

```text
challenge family
challenge kind
exact ordered objective set
challenger role
revision authorization
withdrawal policy
```

A challenge admission with:

```text
objections == []
```

means the challenged positive closure survived that exact hostile challenge.

It is not a generic truth proof.

A challenge with objections does not mechanically establish the opposite proposition.

No challenge contract permits `not-established`.

## Shared revision rule

A semantic closure revision:

```text
is a new semantic question
is not protocol retry
is not another sample for the original QLEK
```

Every revision contract commits:

```text
the semantic dependencies of its family
+
the exact prior positive candidate/admission or exact equivalent fact
+
the exact prior hostile challenge semantic admission
```

Revision ordinal is conceptually:

```text
1
```

The maximum closure revision count is:

```text
1
```

A positive revised candidate requires one fresh challenge.

No `C2` / second revision exists.

A revision MUST remain in the exact same closure family.

## Shared provenance exclusions

Unless explicitly stated as semantic by one contract, these MUST NOT affect QLEK identity:

```text
GateARunId
adjudicating ReviewCampaignId
execution receipt identity
execution root
supplement root
raw-output locator
ArtifactRef locator
reviewer profile
provider
model
model version
prompt identity
timestamps
latency
token count
cost
retry count
attempt ID
call ID
```

## Shared semantic bases

### FindingAdjudicationBasis `FA`

`FA` is the exact semantic authority closure for adjudicating one historical finding under current protocol-v8 semantic authority.

It commits directly or transitively:

```text
exact current semantic subject S

exact current protocol identity P

exact semantic-question authority required by the applicable contract

exact controlling review-authority closure exposed to the question

exact source ReviewCampaignId

exact source FindingId

exact substantiveFindingSha256

exact canonical substantive finding value
```

The following do not define `FA` merely because protocol v7 carried them as evidence/provenance:

```text
GateARunId
adjudicating ReviewCampaignId
evidence-root identity
execution receipt
raw-output locator
storage locator
provenance.kind
historical sourceProtocolBundle when merely production provenance
```

### SurvivingMaterialBasis `SM`

`SM` commits exactly:

```text
FA

QualifiedPositiveMaterialityFact

RefutationExhaustionWithoutQualifiedRefutationFact
```

Receipts proving those facts do not define `SM`.

Two provenance graphs establishing the same exact semantic facts under the same `FA` yield the same `SM`.

## Family 1 — Materiality

### `MaterialityAssessmentInitial@1`

Producer:

```text
role = materiality-assessor
task = materiality-assessment
```

Typed input:

```text
FA
```

Identity mode:

```text
FA → exact semantic value
```

Semantic output:

```text
MaterialityAssessmentValue {
    authority_or_upstream_decision: boolean
    claim_structure: boolean
    normative_provenance: boolean
    modality_or_assurance_domain: boolean
    coverage_or_residual_assurance: boolean
    interaction_scope: boolean
    candidate_model_authorization: boolean
    rationale: non-empty string
}
```

No independent `material` boolean exists.

Derived mechanically:

```text
material =
OR(all seven axes)
```

Semantic answer obligation:

```text
assuming the finding is true,
assess whether the Gate A subject could remain unchanged
while still legitimately authorizing the candidate model
```

Materiality does not represent:

```text
confidence
severity
probability
reviewer consensus
```

Negative structured result:

```text
not permitted
```

Applicable qualification:

```text
MaterialityAssessmentQualification@1
```

Challenge:

```text
MaterialityChallenge@1
```

Challenge trigger:

```text
all seven axes == false
```

Same-family revision:

```text
MaterialityAssessmentRevision@1
```

only after an initial all-false candidate receives hostile objections.

### `MaterialityAssessmentRevision@1`

Typed input:

```text
FA

exact prior all-false MaterialityAssessment SemanticAdmission

exact prior MaterialityChallenge SemanticAdmission
with objections != []
```

Identity modes:

```text
FA → exact semantic value

prior assessment
→ exact SemanticAdmission

prior challenge
→ exact SemanticAdmission
```

Output domain:

```text
MaterialityAssessmentValue
```

Negative result:

```text
not permitted
```

Answer obligation:

```text
revise only the exact prior materiality assessment
to answer the exact hostile objections
without branch-switching or free second semantic search
```

If revised output has one or more true axes:

```text
QualifiedPositiveMateriality
```

may be derived without another Materiality challenge.

If revised output remains all-false:

```text
fresh MaterialityChallenge
```

is required.

No further revision exists.

### `MaterialityChallenge@1`

Input:

```text
exact challenged MaterialityAssessment SemanticAdmission
```

Precondition:

```text
all seven axes == false
```

Identity mode:

```text
challenged candidate → exact SemanticAdmission
```

Contract-owned challenge kind:

```text
materiality
```

Exact objectives, in order:

```text
authority_or_upstream_decision
claim_structure
normative_provenance
modality_or_assurance_domain
coverage_or_residual_assurance
interaction_scope
candidate_model_authorization
```

Challenger role:

```text
challenge
```

Output:

```text
ChallengeSemanticValue
```

Answer obligation:

```text
hostile-test the exact all-false candidate
against every exact materiality objective
and emit every established objection
```

No negative result.

No revision of the challenge itself.

A challenge against an initial candidate with objections authorizes/requires `MaterialityAssessmentRevision@1` when current and operationally admissible.

A challenge against a revised candidate with objections terminates the non-material closure path.

## Family 2 — Refutation

### `RefutationInitial@1`

Producer:

```text
role = refutation-builder
task = refutation
```

Typed input:

```text
FA

QualifiedPositiveMaterialityFact
```

Identity modes:

```text
FA → exact semantic value

QualifiedPositiveMaterialityFact
→ exact semantic fact
```

Output:

```text
RefutationValue =
    RefutationCandidate
  | NotEstablished
```

Positive candidate:

```text
RefutationCandidate {
    ground:
        premise-false
      | target-misidentified
      | counterexample-outside-authority
      | consequence-does-not-follow
      | already-accounted-for

    attacked_premise_or_inference
    evidence_references[]
    argument
    counterexample_disposition
}
```

`counterexample_disposition`, when required, is one of:

```text
impossible
outside-scope
non-concluding
```

with rationale.

Semantic obligation:

```text
positively invalidate at least one necessary premise
or inference of the finding
from exact admissible authority/evidence
without introducing a new normative assumption
```

The following are never refutation grounds:

```text
reviewer majority
absence of another review finding
author intent
preferred interpretation
difficulty reproducing
future implementation
```

`NotEstablished` means only:

```text
this question did not establish a refutation candidate
```

It never means:

```text
finding is true
```

Qualification:

```text
RefutationQualification@1
```

Positive challenge:

```text
RefutationChallenge@1
```

Same-family revision:

```text
RefutationRevision@1
```

after objections to an initial positive candidate.

An initial `NotEstablished` is a lawful refutation-exhaustion terminal for surviving-material derivation when all other exact requirements hold.

### `RefutationRevision@1`

Input:

```text
FA

QualifiedPositiveMaterialityFact

exact prior positive Refutation SemanticAdmission

exact prior RefutationChallenge SemanticAdmission
with objections != []
```

Output:

```text
RefutationCandidate
|
NotEstablished
```

Answer obligation:

```text
answer the exact hostile objections against
the exact prior refutation candidate
within the same refutation family
```

`NotEstablished` withdraws the refutation candidate and terminates the refutation path without qualified refutation.

A positive revised candidate requires a fresh `RefutationChallenge@1`.

No second revision exists.

### `RefutationChallenge@1`

Input:

```text
exact positive Refutation SemanticAdmission
```

Challenge kind:

```text
refutation
```

Exact objectives:

```text
attacked-premise-still-supported
target-correctly-identified
counterexample-remains-in-scope
consequence-still-follows
not-actually-already-accounted-for
hidden-assumption-in-refutation
alternative-authority-compatible-interpretation
```

Challenger:

```text
challenge
```

Output:

```text
ChallengeSemanticValue
```

Zero objections:

```text
QualifiedRefutation
```

may be derived.

Initial candidate + objections:

```text
RefutationRevision@1
```

must be used when current and operationally admissible.

Revised candidate + objections:

```text
RefutationExhaustionWithoutQualifiedRefutation
```

may be derived.

No opposite finding-truth proposition is implied.

## Family 3 — Discovery classification

### `DiscoveryClassificationInitial@1`

Producer:

```text
role = discovery-classifier
task = discovery-classification
```

Input:

```text
SM
```

Identity:

```text
SM → exact semantic value
```

Output:

```text
DiscoveryClassificationValue {
    earliest_unresolved_cause
    classification_statements[]
}
```

At least one atomic statement is required.

`earliest_unresolved_cause` binds:

```text
classification_statement_ordinal
evidence_references[]
causal_explanation
upstream_exclusion_argument
```

Each atomic classification statement is the exact protocol-v7 semantic value containing:

```text
statement
evidence_references[]
evidence_argument
existing_authority[]
affected_layers[]
semantic_disposition
disposition_basis
```

Exact discovery layers:

```text
normative-contract
decision-history
formal-model-or-analysis
verification-or-qualification-evidence
architecture-or-implementation
integration-or-conformance
repository-governance-or-documentation
```

Exact semantic dispositions:

```text
derived-from-existing-authority
decision-required
no-normative-impact
authority-conflict-or-uncertain
```

Different statements in one Discovery admission may have different dispositions.

The statement array remains ordered semantic value.

C1 does not convert it to a set.

Duplicate exact canonical statements are invalid.

Negative result:

```text
not permitted
```

There is no global `DiscoveryClassificationQualification`.

Discovery is routing evidence.

It does not independently authorize:

```text
repair
finding refutation
Decision Request
Gate A readiness
external outcome
```

### Targeted Discovery statement fact

A targetable statement is represented conceptually as:

```text
TargetedDiscoveryStatementFact {
    exact producer Discovery SemanticAdmission
    exact atomic discovery statement
}
```

The producer admission is part of the statement fact identity.

The ordinal need not be an independent identity dimension because duplicate exact statements inside one producer admission are forbidden.

The ordinal remains reconstructible and continues to matter to the whole Discovery value, especially `earliest_unresolved_cause`.

Exact FactId representation belongs to C4.

## Family 4 — NoNormativeImpact qualification

### `NoNormativeImpactChallenge@1`

Input:

```text
exact TargetedDiscoveryStatementFact
```

Precondition:

```text
semantic_disposition == no-normative-impact
```

Challenge kind:

```text
normative-impact
```

Selector meaning:

```text
gate-a-no-normative-impact-candidate-challenge-v1
```

Challenger:

```text
challenge
```

Exact objectives:

```text
correction-requires-product-authority-change
correction-selects-among-product-meanings
missing-product-obligation-exposed
earliest-cause-is-normative-or-upstream
accepted-observable-behavior-would-change
downstream-resolution-requires-product-choice
authority-conflict-hidden-as-downstream-defect
```

Output:

```text
ChallengeSemanticValue
```

Zero objections permit:

```text
QualifiedNoNormativeImpact
```

Initial statement + objections requires:

```text
DiscoveryNoNormativeImpactRevision@1
```

when current and operationally admissible.

Objections do not prove normative impact.

### `DiscoveryNoNormativeImpactRevision@1`

Producer:

```text
role = discovery-classifier
task = discovery-classification
mode = closure-revision
```

Input:

```text
SM

exact prior NoNormativeImpact TargetedDiscoveryStatementFact

exact prior NoNormativeImpactChallenge SemanticAdmission
with objections != []
```

Output:

```text
RevisedDiscoveryStatement
|
NotEstablished
```

A positive revised statement MUST retain:

```text
semantic_disposition = no-normative-impact
```

and may revise only the exact targeted statement.

Sibling Discovery statements are immutable historical results and MUST NOT be rewritten.

`NotEstablished` means:

```text
the positive no-normative-impact claim is withdrawn
```

It does not establish normative impact.

A positive revised statement requires one fresh `NoNormativeImpactChallenge@1`.

No second revision exists.

## Family 5 — DecisionNecessity qualification

### Decision-required Discovery hypothesis

A target statement with:

```text
semantic_disposition = decision-required
```

must positively encode exactly one of:

```text
product-underdetermination
product-authority-conflict
```

Product underdetermination requires at least two materially distinct authority-compatible semantic alternatives and a positive argument that current authority selects none.

Product-authority conflict requires at least two incompatible current controlling product-authority positions and a positive argument that accepted precedence, amendment and supersession rules do not already resolve the conflict.

The statement itself still does not authorize `DECISION-REQUIRED`.

### DecisionNecessity candidate

A DecisionNecessity candidate is not model-produced.

It is an exact mechanically derived fact based on:

```text
SM

exact DecisionRequiredDiscoveryStatementFact

exact UniqueCorrectionExhaustionFact

exact mechanically projected decision-necessity candidate
```

Conceptually the candidate preserves exactly the discovery hypothesis's decision basis.

Its exact FactId representation belongs to C4.

### `DecisionNecessityChallenge@1`

Input:

```text
SM

exact DecisionRequiredDiscoveryStatementFact

exact UniqueCorrectionExhaustionFact

exact DecisionNecessityCandidateFact
```

Challenge kind:

```text
decision-necessity
```

Challenger role:

```text
decision-necessity-challenger
```

Exact objectives:

```text
alternative-not-authority-compatible
alternatives-not-materially-distinct
existing-authority-selects-an-alternative
unique-existing-authority-derivation-remains
alleged-conflict-is-downstream-only
alleged-conflict-resolved-by-precedence
uncertainty-is-missing-evidence-not-product-freedom
authority-source-is-not-controlling
```

Output:

```text
ChallengeSemanticValue
```

Zero objections permit:

```text
QualifiedDecisionNecessity
```

Only then may a Decision Request be projected mechanically.

If an initial DecisionNecessity challenge has objections, the exact target statement enters `DiscoveryDecisionRequiredRevision@1`.

There is no second generic challenge layer above DecisionNecessityChallenge.

### `DiscoveryDecisionRequiredRevision@1`

Producer:

```text
role = discovery-classifier
task = discovery-classification
mode = closure-revision
```

This contract closes the C1 audit correction.

Input is exactly:

```text
SM

exact prior DecisionRequiredDiscoveryStatementFact

exact prior DecisionNecessityCandidateFact

exact prior DecisionNecessityChallenge SemanticAdmission
with objections != []
```

The exact prior `DecisionNecessityCandidateFact` is mandatory.

It is the mechanically projected positive closure candidate that received the hostile objections.

It MUST NOT be omitted merely because the prior challenge transitively references it.

Output:

```text
RevisedDiscoveryStatement
|
NotEstablished
```

A positive revised statement MUST retain:

```text
semantic_disposition = decision-required
```

It may revise only the exact targeted statement.

It MUST NOT modify sibling Discovery classifications.

`NotEstablished` withdraws that exact decision-required closure.

It does not establish that no product decision is needed.

If a revised positive `decision-required` statement is emitted, the old `UniqueCorrectionExhaustionFact` MUST NOT be reused.

The revised statement must enter a fresh ordinary `UniqueCorrection` path.

Only if that new path is lawfully exhausted may a new exact `DecisionNecessityCandidateFact` be derived and a fresh `DecisionNecessityChallenge@1` executed.

No second Discovery revision exists.

## Family 6 — UniqueCorrection

### `UniqueCorrectionInitial@1`

Producer:

```text
role = derivation-builder
task = unique-correction-derivation
```

Input:

```text
SM

exact Discovery SemanticAdmission/result

exact TargetedDiscoveryStatementFact
```

The exact Discovery admission is the admission whose semantic result directly contains or produces the targeted statement.

For a statement in the initial Discovery result:

```text
use the initial Discovery admission
```

For a statement produced by a targeted Discovery revision:

```text
use that exact revision admission
```

The whole Discovery admission is retained in addition to the target statement.

C1 MUST NOT reduce the input to the target statement alone.

Output:

```text
UniqueCorrectionCandidate
|
NotEstablished
```

Positive candidate contains exactly the protocol-v7 semantic value:

```text
correction_requirements[]
derivation_claims[]
alternatives_considered[]
uniqueness_argument
```

Each correction requirement is a semantic postcondition.

It is not:

```text
a file path
a patch
an implementation choice
a CandidateRevision-specific instruction
```

A positive answer must establish:

```text
existing authority entails the correction

every correction requirement is derivationally supported

no required consequence is omitted

no unauthorized semantic effect is introduced

no hidden assumption is required

no materially distinct authority-compatible correction remains
```

If a materially distinct authority-compatible correction remains:

```text
NotEstablished
```

must be returned rather than selecting one arbitrarily.

`NotEstablished` does not imply `DECISION-REQUIRED`.

Qualification:

```text
UniqueCorrectionQualification@1
```

Positive challenge:

```text
UniqueCorrectionChallenge@1
```

Revision:

```text
UniqueCorrectionRevision@1
```

### `UniqueCorrectionRevision@1`

Input:

```text
SM

exact Discovery SemanticAdmission/result

exact TargetedDiscoveryStatementFact

exact prior positive UniqueCorrection SemanticAdmission

exact prior UniqueCorrectionChallenge SemanticAdmission
with objections != []
```

Output:

```text
UniqueCorrectionCandidate
|
NotEstablished
```

Answer obligation:

```text
revise only the exact prior UniqueCorrection
in response to exact objections
without changing target statement or semantic family
```

A revised candidate may cite exact prior challenge objections through their IDs.

`NotEstablished` terminates the UniqueCorrection path.

A positive revised candidate requires one fresh `UniqueCorrectionChallenge@1`.

No second revision exists.

### `UniqueCorrectionChallenge@1`

Input:

```text
exact positive UniqueCorrection SemanticAdmission
```

Challenge kind:

```text
derivation
```

Challenger:

```text
challenge
```

Exact objectives:

```text
authority-does-not-entail-correction
materially-distinct-authority-compatible-alternative
required-consequence-omitted
unauthorized-semantic-effect
hidden-assumption-in-derivation
```

Output:

```text
ChallengeSemanticValue
```

Zero objections permit:

```text
AcceptedUniqueCorrectionFact
```

Initial candidate + objections requires the one revision.

Revised candidate + objections establishes the exact terminal UniqueCorrection-exhaustion branch:

```text
revised-challenge-objections
```

### UniqueCorrection exhaustion

Exactly three terminal branches exist:

```text
initial-not-established

revision-not-established

revised-challenge-objections
```

An initial challenged positive candidate is not exhausted merely because objections exist if the mandatory revision remains lawful and available.

`UniqueCorrectionExhaustionFact` never means `DECISION-REQUIRED`.

For a decision-required target it is only one prerequisite of DecisionNecessity construction.

## Family 7 — RealizationScope

### `RealizationScopeInitial@1`

Producer:

```text
role = derivation-builder
task = realization-scope-derivation
```

Input:

```text
SM

AcceptedUniqueCorrectionFact

exact CandidateRevisionId C

exact complete CandidateView V
such that CandidateViewOf(C, complete, V)
```

Identity modes:

```text
SM → exact semantic value

AcceptedUniqueCorrectionFact
→ exact semantic fact

CandidateRevisionId
→ exact nominal authority

CandidateView
→ exact extensional physical value
```

Both `C` and `V` are required.

If:

```text
C17 != C18
```

then:

```text
QLEK_RS(C17) != QLEK_RS(C18)
```

even if:

```text
CandidateView(C17) == CandidateView(C18)
```

Output:

```text
RealizationScopeCandidate
|
NotEstablished
```

Positive value contains:

```text
readable_paths[]
writable_paths[]
completeness_argument
minimal_write_authority_argument
```

Paths are exact raw candidate-path identities.

No:

```text
glob
wildcard
directory prefix
fuzzy selector
mutable workspace lookup
```

is permitted.

Required structural/semantic properties include:

```text
writable_paths ⊆ readable_paths

every UniqueCorrection requirement has exactly one requirement-surface entry

union(requirement surface paths) == readable_paths

every writable path has exact necessity justification

controlling product-authority paths are not writable
```

The scope is a maximum authorized physical boundary.

It is not a patch.

`NotEstablished` means only that no safe sufficient candidate-bound realization scope was established.

Qualification:

```text
RealizationScopeQualification@1
```

Challenge:

```text
RealizationScopeChallenge@1
```

Revision:

```text
RealizationScopeRevision@1
```

### `RealizationScopeRevision@1`

Input:

```text
SM

AcceptedUniqueCorrectionFact

exact CandidateRevisionId C

exact complete CandidateViewOf(C)

exact prior positive RealizationScope SemanticAdmission

exact prior RealizationScopeChallenge SemanticAdmission
with objections != []
```

The revision MUST retain the exact same:

```text
CandidateRevisionId
CandidateView
AcceptedUniqueCorrection
```

as the producer candidate.

It MUST NOT resolve `"current candidate"` again.

If `C` ceases to be current before lawful revision dispatch, that old revision is no longer required for current progression.

A new current candidate creates a new initial RealizationScope question.

If the old revision was already lawfully dispatched, any later protocol-valid completion still belongs to the old QLEK's admission history.

Output:

```text
RealizationScopeCandidate
|
NotEstablished
```

A positive revised candidate requires one fresh `RealizationScopeChallenge@1`.

No second revision exists.

### `RealizationScopeChallenge@1`

Input:

```text
exact positive RealizationScope SemanticAdmission
```

Candidate binding is inherited transitively through the challenged admission.

The challenge MUST NOT independently infer or select another candidate.

Challenge kind:

```text
derivation
```

Exact objectives:

```text
realization-scope-omits-required-surface
realization-scope-grants-unnecessary-write-authority
```

Challenger:

```text
challenge
```

Output:

```text
ChallengeSemanticValue
```

Zero objections permit:

```text
AcceptedRealizationScopeFact
```

The resulting fact remains exact-candidate-bound.

It never transfers to another `CandidateRevisionId`, even when candidate contents are identical.

## Family 8 — RepairRealization

### `RepairRealizationInitial@1`

Producer:

```text
role = repair-synthesizer
task = repair-realization
```

Input:

```text
SM

AcceptedUniqueCorrectionFact

AcceptedRealizationScopeFact

exact CandidateRevisionId C

exact scoped CandidateView V
```

The exact coverage of `V` is:

```text
readable-paths
```

and its path set MUST equal exactly:

```text
AcceptedRealizationScope.readable_paths
```

The candidate view is reconstructed from the immutable sealed materialization of `C`.

Output:

```text
RepairRealizationCandidate
|
NotEstablished
```

Positive candidate contains:

```text
requirement_realizations[]
operations[]
```

Every exact UniqueCorrection requirement appears exactly once in `requirement_realizations`.

Each requirement realization is exactly one of:

```text
already-realized

patch-realized
```

#### already-realized

Meaning:

```text
the exact current CandidateRevision already satisfies
this exact qualified correction requirement
```

It is a positive candidate-bound semantic claim.

#### patch-realized

Meaning:

```text
the exact proposed operation paths would realize
this exact qualified correction requirement
```

One operation may contribute to more than one requirement.

No operation may contribute to no requirement.

The union of all patch-realized operation paths MUST equal the exact set of proposed operation paths.

Each repair operation supplies:

```text
exact raw candidate path

exact desired after-state
```

The after-state is one of:

```text
absent
blob with exact bytes/mode
symlink with exact target bytes
gitlink with exact object id
```

The model does not emit:

```text
authoritative before-state
trusted preimage
ArtifactRef
diff
patch hunk
search/replace command
shell operation
merge instruction
```

The runner derives authoritative before-state from the exact scoped CandidateView.

Every operation path MUST belong to:

```text
AcceptedRealizationScope.writable_paths
```

No operation may be a physical no-op relative to the exact candidate view.

Empty realization rule:

```text
operations == []
iff
every requirement is already-realized
```

A fully already-realized result is a positive RepairRealization candidate.

It is not `NotEstablished`.

Semantic obligation:

```text
realize exactly the qualified UniqueCorrection
against exactly C
within exactly the accepted RealizationScope
without semantic expansion, unrelated work or new product choice
```

Qualification:

```text
RepairRealizationQualification@1
```

Challenge:

```text
RepairRealizationChallenge@1
```

Revision:

```text
RepairRealizationRevision@1
```

### `RepairRealizationRevision@1`

Input:

```text
SM

AcceptedUniqueCorrectionFact

AcceptedRealizationScopeFact

exact CandidateRevisionId C

exact scoped CandidateViewOf(C)

exact prior positive RepairRealization SemanticAdmission

exact prior RepairRealizationChallenge SemanticAdmission
with objections != []
```

The revision MUST preserve exactly:

```text
C

AcceptedUniqueCorrection

AcceptedRealizationScope

scoped CandidateView
```

It cannot:

```text
change correction
expand scope
select another candidate
introduce a product decision
perform free second semantic search
```

Output:

```text
RepairRealizationCandidate
|
NotEstablished
```

`NotEstablished` means only:

```text
this revision did not establish a valid repair realization
```

It does not imply product underdetermination.

A positive revised candidate requires one fresh `RepairRealizationChallenge@1`.

No second revision exists.

### `RepairRealizationChallenge@1`

Input:

```text
exact positive RepairRealization SemanticAdmission
```

Challenge kind:

```text
repair
```

Challenger:

```text
challenge
```

Exact objectives:

```text
authorized-correction-not-fully-realized
realization-exceeds-authorized-correction
product-semantic-choice-introduced
unrelated-cleanup-or-refactor
hidden-assumption-in-realization
previous-qualified-correction-broken
already-realized-claim-not-supported
required-candidate-change-omitted
partial-realization-misclassified-complete
```

The challenge hostile-tests both:

```text
already-realized claims

and

proposed patch realization
```

Output:

```text
ChallengeSemanticValue
```

Zero objections permit:

```text
AcceptedRepairRealizationFact
```

The fact remains bound to exact CandidateRevision `C`.

## RepairIntent projection boundary

`RepairIntent` is NOT a SemanticQuestionContract output.

It is a downstream authoritative effect/mutation projection.

Only an exact:

```text
AcceptedRepairRealizationFact
```

may authorize its mechanical construction.

If the accepted RepairRealization has:

```text
operations == []
```

because all requirements are `already-realized`:

```text
no RepairIntent is constructed
no empty patch is constructed
no repair successor CandidateRevision is created
```

If at least one requirement is patch-realized:

```text
AcceptedRepairRealization
↓
derive exact authoritative before-state from CandidateView(C)
↓
combine with exact qualified after-states
↓
mechanically construct approvedPatch
↓
construct exact-candidate-bound RepairIntent
```

The RepairIntent MUST bind exact source CandidateRevision `C`.

It MUST NOT be applied to a different candidate merely because physical bytes are equal.

## Qualification-contract catalog

C1 closes exactly seven qualification contract identities.

### `MaterialityAssessmentQualification@1`

For an exact MaterialityAssessment admission:

```text
any axis true
→ QualifiedPositiveMaterialityFact
```

No Materiality challenge is used on that branch.

For all axes false:

```text
exact MaterialityChallenge
with objections == []
→ QualifiedNonMaterialityFact
```

Initial all-false + objections:

```text
mandatory Materiality revision
```

Revised all-false + objections:

```text
no qualified non-materiality
materiality closure unresolved/exhausted
```

Surviving objections never mechanically imply positive materiality.

### `RefutationQualification@1`

Positive Refutation admission:

```text
exact RefutationChallenge
with objections == []
→ QualifiedRefutationFact
```

Terminal no-qualified-refutation states feed the exact refutation-exhaustion reducer.

`NotEstablished` and hostile objections never prove finding truth.

### `NoNormativeImpactQualification@1`

Exact no-normative-impact statement:

```text
exact NNI challenge
with objections == []
→ QualifiedNoNormativeImpactFact
```

A failed NNI closure does not prove normative impact.

### `DecisionNecessityQualification@1`

Exact inputs:

```text
SM
DecisionRequiredDiscoveryStatementFact
UniqueCorrectionExhaustionFact
DecisionNecessityCandidateFact
DecisionNecessityChallenge admission
```

Zero objections:

```text
→ QualifiedDecisionNecessityFact
```

Only that positive fact may authorize mechanical Decision Request projection.

Failure does not prove that no product decision is needed.

### `UniqueCorrectionQualification@1`

Exact positive UniqueCorrection admission:

```text
exact UC challenge
with objections == []
→ AcceptedUniqueCorrectionFact
```

### `RealizationScopeQualification@1`

Exact positive RealizationScope admission:

```text
exact RS challenge
with objections == []
→ AcceptedRealizationScopeFact
```

The accepted fact remains exact-candidate-bound.

### `RepairRealizationQualification@1`

Exact positive RepairRealization admission:

```text
exact repair challenge
with objections == []
→ AcceptedRepairRealizationFact
```

The accepted fact remains exact-candidate-bound.

## Structured-negative-result matrix

Protocol-v8 C1 permits `NotEstablished` exactly as follows:

```text
MaterialityAssessmentInitial
    forbidden

MaterialityAssessmentRevision
    forbidden

RefutationInitial
    permitted

RefutationRevision
    permitted

DiscoveryClassificationInitial
    forbidden

DiscoveryNoNormativeImpactRevision
    permitted

DiscoveryDecisionRequiredRevision
    permitted

UniqueCorrectionInitial
    permitted

UniqueCorrectionRevision
    permitted

RealizationScopeInitial
    permitted

RealizationScopeRevision
    permitted

RepairRealizationInitial
    permitted

RepairRealizationRevision
    permitted

all seven Challenge contracts
    forbidden
```

Every lawful `NotEstablished` is a semantic candidate.

It consumes its exact QLEK.

It MUST NOT be treated as absence of semantic evidence and MUST NOT authorize resampling of that same QLEK.

## Initial versus revised challenge contracts

C1 defines only one challenge contract revision per closure family.

It does NOT define separate:

```text
InitialChallenge
RevisionChallenge
```

contract identities.

For example both:

```text
UniqueCorrectionChallenge(UC0 admission)

and

UniqueCorrectionChallenge(UC1 admission)
```

use:

```text
UniqueCorrectionChallenge@1
```

The exact challenged SemanticAdmission differentiates the questions.

The same rule applies to all seven challenge families.

## Initial-reviewer exclusion

Protocol-v8 C1 does NOT introduce a single-admission SQC for the campaign `initial-reviewer` role.

Initial review intentionally requires multiple operationally independent reviewer executions and effective identity diversity under existing hostile-review authority.

Collapsing those executions into:

```text
one QLEK
→ one SemanticAdmission
```

would destroy the required independent-review campaign semantics.

The C1 catalog therefore governs ADR-055/056 post-review semantic adjudication, resolution and hostile qualification cognition.

Initial-review campaign execution remains governed by the existing review-campaign acquisition/evidence authority.

## Non-SQC derived products

The following are not missing SQC families.

They are mechanically derived facts or projections:

```text
QualifiedPositiveMaterialityFact

QualifiedNonMaterialityFact

RefutationExhaustionWithoutQualifiedRefutationFact

TargetedDiscoveryStatementFact

DecisionNecessityCandidateFact

AcceptedUniqueCorrectionFact

UniqueCorrectionExhaustionFact

AcceptedRealizationScopeFact

AcceptedRepairRealizationFact

DecisionRequest

RepairIntent
```

Their exact fact identities, predicate revisions and qualification keys belong to C4.

Their serialization/projection belongs to later construction stages.

## Candidate-independent contracts

The following remain candidate-independent:

```text
MaterialityAssessmentInitial
MaterialityAssessmentRevision
MaterialityChallenge

RefutationInitial
RefutationRevision
RefutationChallenge

DiscoveryClassificationInitial

NoNormativeImpactChallenge
DiscoveryNoNormativeImpactRevision

DecisionNecessityChallenge
DiscoveryDecisionRequiredRevision

UniqueCorrectionInitial
UniqueCorrectionRevision
UniqueCorrectionChallenge
```

A CandidateRevision under which these happen to execute is provenance only.

## Candidate-bound contracts

The following are directly candidate-bound:

```text
RealizationScopeInitial
RealizationScopeRevision

RepairRealizationInitial
RepairRealizationRevision
```

Their challenges inherit candidate binding transitively through the exact challenged SemanticAdmission:

```text
RealizationScopeChallenge
RepairRealizationChallenge
```

Challenges MUST NOT independently reselect a candidate.

## Candidate currentness

`"current candidate"` is never a semantic logical input.

Binding proceeds conceptually:

```text
current authoritative state
↓
resolve exact CandidateRevision C
↓
construct exact CandidateViewOf(C,...)
↓
construct LogicalQuestionDescriptor
↓
QLEK
```

Fresh pre-dispatch authorization separately verifies that `C` remains current.

Currentness is an execution/progression authorization property.

It is not QLEK identity.

## Candidate advance

Candidate advance:

```text
C0 → C1
```

does not create hidden task-name rerun rules.

Instead candidate-bound input closure changes:

```text
QLEK_RS(C0) != QLEK_RS(C1)

QLEK_RR(C0) != QLEK_RR(C1)
```

Candidate-independent upstream QLEKs remain identical when their exact semantic dependencies remain identical and MUST be reused.

Candidate-bound revisions never cross candidate identity.

## C1 contract inventory

The exact 20-contract inventory is:

```text
INITIAL PRODUCERS — 6

MaterialityAssessmentInitial@1
RefutationInitial@1
DiscoveryClassificationInitial@1
UniqueCorrectionInitial@1
RealizationScopeInitial@1
RepairRealizationInitial@1
```

```text
REVISIONS — 7

MaterialityAssessmentRevision@1
RefutationRevision@1
DiscoveryNoNormativeImpactRevision@1
DiscoveryDecisionRequiredRevision@1
UniqueCorrectionRevision@1
RealizationScopeRevision@1
RepairRealizationRevision@1
```

```text
CHALLENGES — 7

MaterialityChallenge@1
RefutationChallenge@1
NoNormativeImpactChallenge@1
DecisionNecessityChallenge@1
UniqueCorrectionChallenge@1
RealizationScopeChallenge@1
RepairRealizationChallenge@1
```

No other semantic-question family is authorized by C1.

## C1 completeness assertions

The catalog satisfies these exact assertions:

```text
every protocol-v8 initial semantic producer has one contract

every protocol-v8 closure revision has one distinct revision contract

every one of ADR-055's seven exact closure challenge families
has one challenge contract

every structured negative result is explicitly permitted or forbidden

every positive candidate's qualification path is explicit

every candidate-bound family names exact CandidateRevision identity

every candidate-independent family excludes candidate identity

every challenge consumes semantic candidate/fact identity,
not producer receipt identity

every revision binds its exact prior positive candidate/fact
and exact hostile challenge

DecisionNecessity revision binds the exact mechanical
DecisionNecessityCandidateFact

no root-local receipt ownership defines semantic input

no contract derives QLEK from packet SHA

no contract admits provider/model/prompt as semantic identity

no initial-reviewer single-admission contract is invented

no DecisionNecessity producer SQC is invented

no DecisionRequest SQC is invented

no RepairIntent SQC is invented
```

## Explicit C1 deferrals

C1 intentionally does not close the following.

### C2

```text
LogicalQuestionDescriptor serialization

QLEK canonical framing

SemanticAdmissionId framing

public SemanticQuestionContractRevisionId encoding

canonical semantic-value bytes

identity-reference byte representation
```

### C3

```text
global admission mutation
pre-dispatch authority
execution fencing
recovery integration
completion/admission reconciliation
```

### C4

```text
PredicateRevisionId
FactId
QualificationKey
exact fact reducer definitions
fact persistence versus derivation
```

### C5

```text
exact CandidateView construction algorithm
coverage serialization
raw-path canonical ordering
CandidateView validation algorithm
```

### C6

```text
packet schemas
challenge packet representation
receipt version
evidence projection representation
semantic-contract registry artifact representation
protocol-bundle/meta-schema representation
```

These deferrals MUST NOT reopen the semantic meanings closed by C1.

## G-C1 closure

`G-C1` is semantically satisfied when this catalog is published and verified against exact accepted ADR-055/ADR-056 authority.

The gate asserts:

```text
every semantic producer/revision/challenge used by protocol v8
has one exact immutable contract definition
```

and:

```text
no contract contains an unresolved semantic identity decision
```

The closed count is exactly:

```text
20 SemanticQuestionContract revisions
7 QualificationContract revisions
```

with:

```text
0 missing semantic-question families
0 extra invented semantic-question families
0 unresolved semantic identity decisions
```

After publication and audit of this catalog:

```text
C1 = CLOSED
```

and construction may proceed to:

```text
C2 — semantic identity algebra
```

without selecting protocol-v8 serialization or constructing protocol-v8 runtime artifacts.
