---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "construction-identity-algebra"
domain: "turnlock-rust-formal-assurance"
severity: "strict"
name: "Gate A protocol v8 semantic identity algebra"
---

# Gate A protocol v8 semantic identity algebra

## Status and authority

This document is the C2 construction closure for the protocol-v8 work authorized
by ADR-056 and the published C1 SemanticQuestionContract catalog.

It is a non-protocol-authoritative construction artifact.

Its purpose is to define the exact generic identity algebra that later
protocol-v8 construction must materialize without semantic discretion.

Authority remains:

```text
docs/specification/turnlock-spec.md
accepted ADRs
especially ADR-055 and ADR-056
published immutable protocol-v7 artifacts
docs/formal/gate-a-protocol-v8-semantic-question-contract-catalog.md
```

This document MUST NOT:

```text
change TURNLOCK product semantics
change Gate A semantic subject S
reinterpret ADR-055
reinterpret ADR-056
change any C1 SemanticQuestionContract meaning
activate protocol v8
define SemanticAdmission storage or fencing
define concrete PredicateRevision semantics
define qualification reducers
define CandidateView construction
select protocol-v8 packet/receipt schemas
construct protocol-v8 runtime artifacts
```

If later construction requires choosing between materially distinct semantic
meanings rather than mechanically realizing this algebra:

```text
STOP
→ decision-required
→ accepted ADR
→ return to the earliest affected construction stage
```

## C2 / C4 boundary

C2 closes the generic identity algebra and reference forms for:

```text
SemanticValue
LogicalQuestionDescriptor
QLEK
SemanticAdmission
PredicateRevision identity
SemanticFact identity
QualificationKey
```

C2 does NOT close:

```text
the concrete PredicateRevision catalog
predicate-specific argument signatures
qualification reducers
primitive-versus-derived persistence decisions
semantic-fact reducer algorithms
```

Those remain C4 construction responsibilities.

C2 defines how a future exact PredicateRevision or qualification input is
identified once its C4 semantics are closed.

## C2 / C5 boundary

C2 defines how an exact CandidateView semantic value is identified and referenced.

C2 does NOT define how CandidateView is constructed from an immutable
CandidateRevision.

That remains C5.

## C2 / C6 boundary

C2 defines canonical semantic identity values.

It does NOT select execution packet, receipt, supplement, protocol-bundle or
repository artifact schemas.

Those remain C6/C7.

# Canonical value domain

## CanonicalJsonValueV1

The exact value domain is:

```text
CanonicalJsonValueV1 =
    null
  | boolean
  | arbitrary-precision mathematical integer
  | Unicode scalar string
  | ordered array<CanonicalJsonValueV1>
  | object<string, CanonicalJsonValueV1>
```

The following are forbidden:

```text
floating-point value
NaN
Infinity
negative zero as a distinct value
duplicate object key
unpaired Unicode surrogate
implementation-dependent integer truncation
implementation-dependent numeric rounding
```

No implementation numeric-width limit is semantic.

In particular, C2 does NOT impose the JavaScript safe-integer limit.

Implementations MUST preserve exact arbitrary-precision integer value during
identity construction.

## Integer serialization

A canonical integer is emitted as its unique base-10 representation:

```text
0
1
-1
42
123456789012345678901234567890
```

Forbidden alternative spellings include:

```text
+1
01
-0
1.0
1e0
1E0
```

## String semantics

Strings are exact Unicode scalar sequences.

No NFC, NFD or other Unicode normalization is performed.

Two distinct Unicode scalar sequences remain distinct values even when they
render visually identically.

## Object-key order

Object keys are unique strings.

Canonical serialization orders object keys lexicographically by their exact UTF-8
byte sequences.

For valid Unicode scalar strings, this is the required cross-language canonical
ordering.

## Array order

Array order is semantic unless the exact owning semantic type defines a
canonical transformation before identity construction.

C2 MUST NOT generically sort arrays.

Therefore:

```text
[A, B] != [B, A]
```

unless an upstream exact type definition has already established those arrays as
the same canonical semantic value.

# Canonical JSON value bytes

Define:

```text
CanonicalJsonValueBytesV1(V)
```

as the UTF-8 encoding of the exact JSON value for `V` with:

```text
object keys in canonical order
no insignificant whitespace
non-ASCII Unicode scalars emitted directly as UTF-8
JSON-required escaping for quotes, backslash and control characters
canonical integer serialization
no trailing newline
```

This preserves the repository's existing canonical JSON value convention
equivalent, for values within Python's exact integer domain, to:

```python
json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
).encode("utf-8")
```

The semantic definition above, not a particular language runtime, is
authoritative for cross-language implementations.

# Identity hash framing

## IdentityHashV1

Define exactly:

```text
IdentityHashV1(domain, payload) =
lowercaseHex(
  SHA256(
    CanonicalJsonValueBytesV1(
      {
        "domain": domain,
        "frame": "turnlock.identity-frame.v1",
        "payload": payload
      }
    )
  )
)
```

The identity frame is:

```text
turnlock.identity-frame.v1
```

The frame and domain are part of the hashed canonical value.

No concatenation-based alternate framing is permitted.

## Closed identity domains

C2 closes these generic hash domains:

```text
turnlock.semantic-value.v1
turnlock.logical-question.v1
turnlock.semantic-admission.v1
turnlock.semantic-fact.v1
turnlock.qualification-key.v1
```

A packet or runtime caller MUST NOT choose another domain dynamically for these
identity classes.

# Public identity rendering

C2 uses these exact renderings:

```text
SemanticValueId:
semantic-value-sha256:<64 lowercase hexadecimal characters>

QLEK:
qlek-sha256:<64 lowercase hexadecimal characters>

SemanticAdmissionId:
semantic-admission-sha256:<64 lowercase hexadecimal characters>

FactId:
semantic-fact-sha256:<64 lowercase hexadecimal characters>

QualificationKey:
qualification-key-sha256:<64 lowercase hexadecimal characters>
```

The rendered prefix is not part of the SHA-256 preimage.

The suffix is exactly the corresponding `IdentityHashV1` digest.

# SemanticQuestionContractRevision identity

The C1 construction identities receive this public symbolic encoding:

```text
SemanticQuestionContractRevisionId =
"turnlock.sqc:" + C1ContractName + "@" + revision
```

The exact protocol-v8 set is:

```text
turnlock.sqc:MaterialityAssessmentInitial@1
turnlock.sqc:MaterialityAssessmentRevision@1
turnlock.sqc:MaterialityChallenge@1

turnlock.sqc:RefutationInitial@1
turnlock.sqc:RefutationRevision@1
turnlock.sqc:RefutationChallenge@1

turnlock.sqc:DiscoveryClassificationInitial@1

turnlock.sqc:NoNormativeImpactChallenge@1
turnlock.sqc:DiscoveryNoNormativeImpactRevision@1

turnlock.sqc:DecisionNecessityChallenge@1
turnlock.sqc:DiscoveryDecisionRequiredRevision@1

turnlock.sqc:UniqueCorrectionInitial@1
turnlock.sqc:UniqueCorrectionRevision@1
turnlock.sqc:UniqueCorrectionChallenge@1

turnlock.sqc:RealizationScopeInitial@1
turnlock.sqc:RealizationScopeRevision@1
turnlock.sqc:RealizationScopeChallenge@1

turnlock.sqc:RepairRealizationInitial@1
turnlock.sqc:RepairRealizationRevision@1
turnlock.sqc:RepairRealizationChallenge@1
```

This symbolic identity is semantic identity.

It is NOT a hash of this construction document or of a future protocol artifact.

A semantic change requires a new revision identity.

Formatting, repository path or packaging changes that preserve exact contract
meaning do not create another semantic revision.

# Semantic value identity

## SemanticValueTypeRevisionId

The generic namespace is:

```text
turnlock.semantic-value:<Name>@<Revision>
```

The P8 construction already requires at least:

```text
turnlock.semantic-value:FindingAdjudicationBasis@1
turnlock.semantic-value:SurvivingMaterialBasis@1
turnlock.semantic-value:CandidateView@1
```

C5 remains responsible for exact CandidateView construction.

## SemanticValueId

For exact type `T` and exact canonical value `V`:

```text
SemanticValueId(T, V) =
"semantic-value-sha256:" +
IdentityHashV1(
  "turnlock.semantic-value.v1",
  {
    "valueType": T,
    "value": V
  }
)
```

## SemanticValueRefV1

The exact reference shape is:

```text
SemanticValueRefV1 {
  kind:
    "semantic-value"

  valueType:
    SemanticValueTypeRevisionId

  valueId:
    SemanticValueId
}
```

Validation requires:

```text
resolve(valueId)
→ exactly one canonical semantic value preimage

resolved valueType == ref.valueType

recomputed SemanticValueId == ref.valueId
```

# Exact authoritative identity

## ExactAuthorityRefV1

The exact generic shape is:

```text
ExactAuthorityRefV1 {
  kind:
    "exact-authority"

  authorityType:
    non-empty immutable authority-type identifier

  authorityId:
    exact authority-native identity
}
```

For P8 C1 candidate-bound SQC inputs, use exactly:

```text
authorityType =
"turnlock.authority:candidate-revision.v2"

authorityId =
exact CandidateRevisionId
```

C2 does not redefine CandidateRevisionId.

It consumes the existing exact nominal candidate identity owned by current
runner authority.

Repository-content equality MUST NOT replace CandidateRevision nominal identity.

# FindingAdjudicationBasis

## FindingAdjudicationBasisV1

The exact canonical semantic value is:

```text
FindingAdjudicationBasisV1 {
  schema:
    "turnlock.finding-adjudication-basis.v1"

  semanticSubject: {
    selector:
      "gate-a-assurance-decomposition-v1"

    sha256:
      exact current semantic subject S sha256
  }

  currentProtocol: {
    protocolId:
      exact current hostile-review protocol id

    bundleSha256:
      exact current hostile-review protocol-bundle sha256
  }

  sourceFinding: {
    reviewCampaignId:
      exact source ReviewCampaignId

    findingId:
      exact source FindingId

    substantiveFindingSha256:
      exact validated hostile-finding-subject-v1 sha256
  }
}
```

No other field is part of the FA canonical value.

In particular, FA excludes:

```text
GateARunId
adjudicating ReviewCampaignId
review-packet path
review-packet sha256
execution root
evidence root
receipt identity
raw-output identity
storage locator
provenance.kind
historical sourceProtocolBundle when merely production provenance
```

## FA resolution requirements

A FA value is valid only if authoritative closure mechanically establishes:

```text
semanticSubject resolves exactly

resolved semantic-subject canonical payload hashes to semanticSubject.sha256

the exact controlling review-authority content closure referenced by S resolves
and every exact content hash verifies

currentProtocol resolves exactly

resolved current protocol has exactly the named protocolId and bundleSha256

source ReviewCampaign exists

source FindingId resolves exactly once in that source campaign

recomputed hostile-finding-subject-v1 sha256 equals
sourceFinding.substantiveFindingSha256

the exact canonical substantive finding value is reconstructible
```

The exact current `S` identity remains unchanged.

C2 MUST NOT define an `S'` that strips historical path fields from the existing
semantic-subject payload.

Repository/storage locators transitively present in the historical S
representation do not thereby become independent QLEK inputs or model-visible
semantic branches.

## FA semantic value reference

Use:

```text
SemanticValueRefV1 {
  kind:
    "semantic-value"

  valueType:
    "turnlock.semantic-value:FindingAdjudicationBasis@1"

  valueId:
    SemanticValueId(
      "turnlock.semantic-value:FindingAdjudicationBasis@1",
      exact FindingAdjudicationBasisV1
    )
}
```

# SurvivingMaterialBasis

## SurvivingMaterialBasisV1

The exact canonical semantic value is:

```text
SurvivingMaterialBasisV1 {
  schema:
    "turnlock.surviving-material-basis.v1"

  findingAdjudicationBasis:
    SemanticValueRefV1

  qualifiedPositiveMateriality:
    SemanticFactRefV1

  refutationExhaustionWithoutQualifiedRefutation:
    SemanticFactRefV1
}
```

The `findingAdjudicationBasis` ref MUST have value type:

```text
turnlock.semantic-value:FindingAdjudicationBasis@1
```

C4 will define the exact predicate revisions for the two semantic facts.

A valid SM requires mechanically:

```text
all three refs resolve exactly

qualifiedPositiveMateriality belongs to the exact referenced FA

refutationExhaustionWithoutQualifiedRefutation belongs to the exact referenced FA

refutationExhaustionWithoutQualifiedRefutation commits the same exact
qualifiedPositiveMateriality fact
```

SM excludes:

```text
run
root
receipt
raw output
challenge locator
supplement ownership
candidate revision
candidate view
```

Two provenance graphs establishing the same exact FA and same exact two semantic
facts yield the same SM.

## SM semantic value reference

Use:

```text
SemanticValueRefV1 {
  kind:
    "semantic-value"

  valueType:
    "turnlock.semantic-value:SurvivingMaterialBasis@1"

  valueId:
    SemanticValueId(
      "turnlock.semantic-value:SurvivingMaterialBasis@1",
      exact SurvivingMaterialBasisV1
    )
}
```

# SemanticAdmission identity

## SemanticAdmissionId

For exact QLEK `K` and exact canonical semantic candidate `V`:

```text
SemanticAdmissionId(K, V) =
"semantic-admission-sha256:" +
IdentityHashV1(
  "turnlock.semantic-admission.v1",
  {
    "qlek": K,
    "semanticCandidate": V
  }
)
```

Execution identity, receipt identity and provenance MUST NOT enter the admission
identity.

A structured negative result such as:

```text
{"kind":"not-established"}
```

is an ordinary semantic candidate where its exact SQC permits it.

## SemanticAdmissionRefV1

The exact reference is:

```text
SemanticAdmissionRefV1 {
  kind:
    "semantic-admission"

  admissionId:
    SemanticAdmissionId
}
```

Validation requires exact reconstruction of:

```text
SemanticAdmissionId
→ exact QLEK
→ exact LogicalQuestionDescriptor
+
exact canonical semantic candidate
```

A receipt is origin evidence for an admission.

A receipt is not the admission identity.

# Predicate and fact identity algebra

## PredicateRevisionId

The generic public namespace is:

```text
PredicateRevisionId =
"turnlock.predicate:" + Name + "@" + Revision
```

C2 does not instantiate the concrete P8 PredicateRevision catalog.

C4 owns:

```text
exact predicate names
exact predicate revisions
exact argument schemas
predicate semantic meaning
qualification reducers
derived/primitive fact boundary
```

A semantic change to a predicate's argument schema, identity semantics or
proposition meaning requires a new revision.

## SemanticFactDescriptorV1

The generic canonical descriptor is:

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

Predicate-specific arguments may use exact C2 references as authorized by the
future C4 predicate revision.

Receipt/root/locator provenance MUST NOT be included merely because it proves the
fact.

## FactId

Define:

```text
FactId =
"semantic-fact-sha256:" +
IdentityHashV1(
  "turnlock.semantic-fact.v1",
  SemanticFactDescriptorV1
)
```

Therefore:

```text
same PredicateRevisionId
+
same exact canonical arguments
→ same FactId
```

independent of provenance graph.

## SemanticFactRefV1

The exact reference is:

```text
SemanticFactRefV1 {
  kind:
    "semantic-fact"

  predicateRevision:
    PredicateRevisionId

  factId:
    FactId
}
```

Validation requires:

```text
factId resolves to exactly one canonical fact descriptor

resolved predicateRevision == ref.predicateRevision

recomputed FactId == ref.factId

the fact is mechanically reconstructible from authoritative primitive
commitments and accepted rules
```

An unresolvable fact is an integrity failure.

It MUST NOT authorize regeneration of predecessor semantic work.

# Qualification identity algebra

## QualificationContractRevisionId

The exact C1 qualification-contract encodings are:

```text
turnlock.qualification:MaterialityAssessmentQualification@1
turnlock.qualification:RefutationQualification@1
turnlock.qualification:NoNormativeImpactQualification@1
turnlock.qualification:DecisionNecessityQualification@1
turnlock.qualification:UniqueCorrectionQualification@1
turnlock.qualification:RealizationScopeQualification@1
turnlock.qualification:RepairRealizationQualification@1
```

They are symbolic semantic identities, not hashes of future artifact bytes.

## QualificationKeyDescriptorV1

ADR-056 requires an exact qualification key to bind an exact
SemanticAdmissionId plus exact additional qualification inputs.

Use exactly:

```text
QualificationKeyDescriptorV1 {
  schema:
    "turnlock.qualification-key-descriptor.v1"

  qualificationContract:
    QualificationContractRevisionId

  anchorAdmission:
    SemanticAdmissionRefV1

  additionalInputs:
    exact closed qualification-contract-specific canonical object
}
```

`anchorAdmission` is fixed by each qualification contract.

It is never selected freely by the runner.

For model-produced candidate qualifications, it is the exact candidate
SemanticAdmission.

For the two C1 qualifications whose positive candidate is mechanically derived,
the anchor is mechanically derived from the exact Discovery statement fact as
specified below.

## QualificationKey

Define:

```text
QualificationKey =
"qualification-key-sha256:" +
IdentityHashV1(
  "turnlock.qualification-key.v1",
  QualificationKeyDescriptorV1
)
```

QualificationKey identifies the exact qualification inputs.

It does NOT encode the qualification outcome.

Qualification outcome remains mechanically derived in C4.

## QualificationKeyRefV1

Use exactly:

```text
QualificationKeyRefV1 {
  kind:
    "qualification-key"

  qualificationContract:
    QualificationContractRevisionId

  qualificationKey:
    QualificationKey
}
```

Validation requires:

```text
qualificationKey resolves exactly

resolved qualificationContract == ref.qualificationContract

recomputed QualificationKey == ref.qualificationKey
```

# Exact qualification-key input rules

## MaterialityAssessmentQualification@1

For an exact MaterialityAssessment admission with one or more positive axes:

```text
anchorAdmission =
exact MaterialityAssessment SemanticAdmission

additionalInputs = {}
```

For an exact all-false MaterialityAssessment candidate whose non-material closure
is challengeable:

```text
anchorAdmission =
exact MaterialityAssessment SemanticAdmission

additionalInputs = {
  "materialityChallenge":
    exact MaterialityChallenge SemanticAdmissionRef
}
```

C4 determines the derived qualification fact.

Hostile objections never mechanically imply positive materiality.

## RefutationQualification@1

For an exact positive Refutation candidate:

```text
anchorAdmission =
exact Refutation SemanticAdmission

additionalInputs = {
  "refutationChallenge":
    exact RefutationChallenge SemanticAdmissionRef
}
```

`NotEstablished` does not use this positive qualification key.

It contributes to the C4 refutation-exhaustion reducer.

## NoNormativeImpactQualification@1

A TargetedDiscoveryStatementFact commits:

```text
exact producer Discovery SemanticAdmission
+
exact atomic discovery statement
```

For qualification of an exact no-normative-impact statement:

```text
anchorAdmission =
the exact producer Discovery SemanticAdmission mechanically committed by
the exact targetedDiscoveryStatement fact

additionalInputs = {
  "targetedDiscoveryStatement":
    exact TargetedDiscoveryStatement SemanticFactRef,

  "noNormativeImpactChallenge":
    exact NoNormativeImpactChallenge SemanticAdmissionRef
}
```

Require:

```text
anchorAdmission
==
producerAdmission(targetedDiscoveryStatement)
```

There is no alternate legal anchor.

## DecisionNecessityQualification@1

A DecisionRequiredDiscoveryStatementFact commits its exact producer Discovery
SemanticAdmission.

The exact C1 qualification dependencies are all preserved directly:

```text
SM
DecisionRequiredDiscoveryStatementFact
UniqueCorrectionExhaustionFact
DecisionNecessityCandidateFact
DecisionNecessityChallenge SemanticAdmission
```

Construct:

```text
anchorAdmission =
the exact producer Discovery SemanticAdmission mechanically committed by
the exact decisionRequiredStatement fact

additionalInputs = {
  "survivingMaterialBasis":
    exact SM SemanticValueRef,

  "decisionRequiredStatement":
    exact DecisionRequiredDiscoveryStatement SemanticFactRef,

  "uniqueCorrectionExhaustion":
    exact UniqueCorrectionExhaustion SemanticFactRef,

  "decisionNecessityCandidate":
    exact DecisionNecessityCandidate SemanticFactRef,

  "decisionNecessityChallenge":
    exact DecisionNecessityChallenge SemanticAdmissionRef
}
```

Require:

```text
anchorAdmission
==
producerAdmission(decisionRequiredStatement)
```

C2 MUST NOT remove any of the five exact C1 qualification dependencies merely
because some are transitively reconstructible from others.

## UniqueCorrectionQualification@1

```text
anchorAdmission =
exact positive UniqueCorrection SemanticAdmission

additionalInputs = {
  "uniqueCorrectionChallenge":
    exact UniqueCorrectionChallenge SemanticAdmissionRef
}
```

## RealizationScopeQualification@1

```text
anchorAdmission =
exact positive RealizationScope SemanticAdmission

additionalInputs = {
  "realizationScopeChallenge":
    exact RealizationScopeChallenge SemanticAdmissionRef
}
```

Candidate binding is inherited through the exact RealizationScope admission.

## RepairRealizationQualification@1

```text
anchorAdmission =
exact positive RepairRealization SemanticAdmission

additionalInputs = {
  "repairRealizationChallenge":
    exact RepairRealizationChallenge SemanticAdmissionRef
}
```

Candidate binding is inherited through the exact RepairRealization admission.

# LogicalQuestionDescriptor

## Exact reference discipline

Every direct C1 logical input uses exactly one reference form:

```text
exact semantic value
→ SemanticValueRefV1

exact SemanticAdmission
→ SemanticAdmissionRefV1

exact semantic fact
or exact mechanically derived semantic fact
→ SemanticFactRefV1

exact nominal authority
→ ExactAuthorityRefV1
```

No inline alternate representation is legal inside a P8
LogicalQuestionDescriptor.

QualificationKeyRefV1 is not a direct C1 logical-question input form; it is
available to C4 semantic-fact construction.

## LogicalQuestionDescriptorV1

The exact canonical shape is:

```text
LogicalQuestionDescriptorV1 {
  schema:
    "turnlock.logical-question-descriptor.v1"

  semanticQuestionContract:
    SemanticQuestionContractRevisionId

  exactLogicalInput:
    exact closed contract-specific canonical object
}
```

The top-level key set is exact.

The descriptor MUST NOT contain:

```text
GateARunId
RequirementSlotId
ObligationId
WorkItemId
ExecutionId
receipt identity
root identity
packet identity
prompt identity
provider
model
model version
reviewer profile
timestamp
currentCandidate symbolic reference
```

unless a future accepted SemanticQuestionContractRevision explicitly makes a
currently excluded dimension semantic.

## Descriptor canonical bytes

The unique canonical public serialization is:

```text
CanonicalJsonValueBytesV1(
  exact LogicalQuestionDescriptorV1
)
```

# QLEK

For exact descriptor `D`:

```text
QLEK(D) =
"qlek-sha256:" +
IdentityHashV1(
  "turnlock.logical-question.v1",
  D
)
```

A QLEK is valid only after the exact descriptor and every direct reference have
been validated.

The runner MUST NOT hash an invalid or unresolved descriptor and then treat the
digest as semantic authority.

# Exact 20 logical-input shapes

The exact direct C1 dependency shapes are:

## MaterialityAssessmentInitial@1

```text
{
  "findingAdjudicationBasis":
    SemanticValueRef<FindingAdjudicationBasis@1>
}
```

## MaterialityAssessmentRevision@1

```text
{
  "findingAdjudicationBasis":
    SemanticValueRef<FindingAdjudicationBasis@1>,

  "priorMaterialityAssessment":
    SemanticAdmissionRef,

  "priorMaterialityChallenge":
    SemanticAdmissionRef
}
```

## MaterialityChallenge@1

```text
{
  "challengedMaterialityAssessment":
    SemanticAdmissionRef
}
```

## RefutationInitial@1

```text
{
  "findingAdjudicationBasis":
    SemanticValueRef<FindingAdjudicationBasis@1>,

  "qualifiedPositiveMateriality":
    SemanticFactRef
}
```

## RefutationRevision@1

```text
{
  "findingAdjudicationBasis":
    SemanticValueRef<FindingAdjudicationBasis@1>,

  "qualifiedPositiveMateriality":
    SemanticFactRef,

  "priorRefutation":
    SemanticAdmissionRef,

  "priorRefutationChallenge":
    SemanticAdmissionRef
}
```

## RefutationChallenge@1

```text
{
  "challengedRefutation":
    SemanticAdmissionRef
}
```

## DiscoveryClassificationInitial@1

```text
{
  "survivingMaterialBasis":
    SemanticValueRef<SurvivingMaterialBasis@1>
}
```

## NoNormativeImpactChallenge@1

```text
{
  "targetedDiscoveryStatement":
    SemanticFactRef
}
```

## DiscoveryNoNormativeImpactRevision@1

```text
{
  "survivingMaterialBasis":
    SemanticValueRef<SurvivingMaterialBasis@1>,

  "priorNoNormativeImpactStatement":
    SemanticFactRef,

  "priorNoNormativeImpactChallenge":
    SemanticAdmissionRef
}
```

## DecisionNecessityChallenge@1

```text
{
  "survivingMaterialBasis":
    SemanticValueRef<SurvivingMaterialBasis@1>,

  "decisionRequiredStatement":
    SemanticFactRef,

  "uniqueCorrectionExhaustion":
    SemanticFactRef,

  "decisionNecessityCandidate":
    SemanticFactRef
}
```

## DiscoveryDecisionRequiredRevision@1

```text
{
  "survivingMaterialBasis":
    SemanticValueRef<SurvivingMaterialBasis@1>,

  "priorDecisionRequiredStatement":
    SemanticFactRef,

  "priorDecisionNecessityCandidate":
    SemanticFactRef,

  "priorDecisionNecessityChallenge":
    SemanticAdmissionRef
}
```

The exact prior DecisionNecessityCandidate fact is mandatory.

## UniqueCorrectionInitial@1

```text
{
  "survivingMaterialBasis":
    SemanticValueRef<SurvivingMaterialBasis@1>,

  "discovery":
    SemanticAdmissionRef,

  "targetedDiscoveryStatement":
    SemanticFactRef
}
```

## UniqueCorrectionRevision@1

```text
{
  "survivingMaterialBasis":
    SemanticValueRef<SurvivingMaterialBasis@1>,

  "discovery":
    SemanticAdmissionRef,

  "targetedDiscoveryStatement":
    SemanticFactRef,

  "priorUniqueCorrection":
    SemanticAdmissionRef,

  "priorUniqueCorrectionChallenge":
    SemanticAdmissionRef
}
```

## UniqueCorrectionChallenge@1

```text
{
  "challengedUniqueCorrection":
    SemanticAdmissionRef
}
```

## RealizationScopeInitial@1

```text
{
  "survivingMaterialBasis":
    SemanticValueRef<SurvivingMaterialBasis@1>,

  "acceptedUniqueCorrection":
    SemanticFactRef,

  "candidateRevision":
    ExactAuthorityRef<CandidateRevisionId>,

  "completeCandidateView":
    SemanticValueRef<CandidateView@1>
}
```

## RealizationScopeRevision@1

```text
{
  "survivingMaterialBasis":
    SemanticValueRef<SurvivingMaterialBasis@1>,

  "acceptedUniqueCorrection":
    SemanticFactRef,

  "candidateRevision":
    ExactAuthorityRef<CandidateRevisionId>,

  "completeCandidateView":
    SemanticValueRef<CandidateView@1>,

  "priorRealizationScope":
    SemanticAdmissionRef,

  "priorRealizationScopeChallenge":
    SemanticAdmissionRef
}
```

## RealizationScopeChallenge@1

```text
{
  "challengedRealizationScope":
    SemanticAdmissionRef
}
```

## RepairRealizationInitial@1

```text
{
  "survivingMaterialBasis":
    SemanticValueRef<SurvivingMaterialBasis@1>,

  "acceptedUniqueCorrection":
    SemanticFactRef,

  "acceptedRealizationScope":
    SemanticFactRef,

  "candidateRevision":
    ExactAuthorityRef<CandidateRevisionId>,

  "scopedCandidateView":
    SemanticValueRef<CandidateView@1>
}
```

## RepairRealizationRevision@1

```text
{
  "survivingMaterialBasis":
    SemanticValueRef<SurvivingMaterialBasis@1>,

  "acceptedUniqueCorrection":
    SemanticFactRef,

  "acceptedRealizationScope":
    SemanticFactRef,

  "candidateRevision":
    ExactAuthorityRef<CandidateRevisionId>,

  "scopedCandidateView":
    SemanticValueRef<CandidateView@1>,

  "priorRepairRealization":
    SemanticAdmissionRef,

  "priorRepairRealizationChallenge":
    SemanticAdmissionRef
}
```

## RepairRealizationChallenge@1

```text
{
  "challengedRepairRealization":
    SemanticAdmissionRef
}
```

No additional direct logical input is authorized for these 20 C1 contracts.

# Derived QLEK formulas

Define:

```text
Q(C, I) =
QLEK(
  LogicalQuestionDescriptorV1 {
    schema =
      "turnlock.logical-question-descriptor.v1"

    semanticQuestionContract = C

    exactLogicalInput = I
  }
)
```

Then the exact families are:

```text
MaterialityAssessmentInitial:
Q(
  MaterialityAssessmentInitial@1,
  FA
)

MaterialityAssessmentRevision:
Q(
  MaterialityAssessmentRevision@1,
  FA,
  prior Materiality admission,
  prior MaterialityChallenge admission
)

MaterialityChallenge:
Q(
  MaterialityChallenge@1,
  challenged Materiality admission
)

RefutationInitial:
Q(
  RefutationInitial@1,
  FA,
  QualifiedPositiveMateriality fact
)

RefutationRevision:
Q(
  RefutationRevision@1,
  FA,
  QualifiedPositiveMateriality fact,
  prior Refutation admission,
  prior RefutationChallenge admission
)

RefutationChallenge:
Q(
  RefutationChallenge@1,
  challenged Refutation admission
)

DiscoveryClassificationInitial:
Q(
  DiscoveryClassificationInitial@1,
  SM
)

NoNormativeImpactChallenge:
Q(
  NoNormativeImpactChallenge@1,
  targeted NNI statement fact
)

DiscoveryNoNormativeImpactRevision:
Q(
  DiscoveryNoNormativeImpactRevision@1,
  SM,
  prior NNI statement fact,
  prior NNI challenge admission
)

DecisionNecessityChallenge:
Q(
  DecisionNecessityChallenge@1,
  SM,
  decision-required statement fact,
  UniqueCorrection exhaustion fact,
  DecisionNecessity candidate fact
)

DiscoveryDecisionRequiredRevision:
Q(
  DiscoveryDecisionRequiredRevision@1,
  SM,
  prior decision-required statement fact,
  prior DecisionNecessity candidate fact,
  prior DecisionNecessity challenge admission
)

UniqueCorrectionInitial:
Q(
  UniqueCorrectionInitial@1,
  SM,
  Discovery admission,
  targeted statement fact
)

UniqueCorrectionRevision:
Q(
  UniqueCorrectionRevision@1,
  SM,
  Discovery admission,
  targeted statement fact,
  prior UniqueCorrection admission,
  prior UniqueCorrection challenge admission
)

UniqueCorrectionChallenge:
Q(
  UniqueCorrectionChallenge@1,
  challenged UniqueCorrection admission
)

RealizationScopeInitial:
Q(
  RealizationScopeInitial@1,
  SM,
  AcceptedUniqueCorrection fact,
  exact CandidateRevision,
  complete CandidateView
)

RealizationScopeRevision:
Q(
  RealizationScopeRevision@1,
  SM,
  AcceptedUniqueCorrection fact,
  same exact CandidateRevision,
  same complete CandidateView,
  prior RealizationScope admission,
  prior RealizationScope challenge admission
)

RealizationScopeChallenge:
Q(
  RealizationScopeChallenge@1,
  challenged RealizationScope admission
)

RepairRealizationInitial:
Q(
  RepairRealizationInitial@1,
  SM,
  AcceptedUniqueCorrection fact,
  AcceptedRealizationScope fact,
  exact CandidateRevision,
  exact scoped CandidateView
)

RepairRealizationRevision:
Q(
  RepairRealizationRevision@1,
  SM,
  AcceptedUniqueCorrection fact,
  AcceptedRealizationScope fact,
  same exact CandidateRevision,
  same scoped CandidateView,
  prior RepairRealization admission,
  prior RepairRealization challenge admission
)

RepairRealizationChallenge:
Q(
  RepairRealizationChallenge@1,
  challenged RepairRealization admission
)
```

The abbreviations above do not replace the exact named canonical
`exactLogicalInput` object shapes.

# RequirementSlot binding

RequirementSlot identity is orchestration identity.

It is not QLEK identity.

Define conceptually:

```text
BindRequirementSlot(
  exact RequirementSlot R,
  exact AuthoritativeState A
)
```

as a deterministic protocol binding relation.

For one exact `R` and exact `A`, binding MUST produce exactly one of:

```text
one exact LogicalQuestionDescriptor
```

or:

```text
one deterministic non-bindable disposition
```

It MUST NOT produce multiple lawful descriptors between which a runner chooses.

More than one lawful descriptor is:

```text
SEMANTIC-BINDING-AMBIGUITY
```

and fails closed.

`RequirementSlotId`, `ObligationId`, `WorkItemId` or equivalent orchestration
identity MUST NOT be inserted into `LogicalQuestionDescriptorV1`.

Therefore distinct requirement slots may bind to the same QLEK.

A later authoritative-state change may cause the same requirement slot to bind a
new descriptor because an exact semantic dependency changed.

This is not a hidden rerun command.

# Candidate currentness and freshness

`current candidate` is never a symbolic logical input.

For a candidate-bound question:

```text
authoritative current candidate
↓
resolve exact CandidateRevision C
↓
construct exact CandidateViewOf(C, coverage, V) under C5 authority
↓
construct exact refs
↓
construct LogicalQuestionDescriptor
↓
derive QLEK
```

Fresh pre-dispatch currentness validation remains an authorization property, not
part of QLEK identity.

If:

```text
C17 != C18
```

then:

```text
ExactAuthorityRef(C17)
!=
ExactAuthorityRef(C18)
```

and therefore candidate-bound QLEKs differ even when:

```text
CandidateView(C17) == CandidateView(C18)
```

If one exact CandidateRevision and one exact coverage specification resolve to
two incompatible CandidateViews, that is a CandidateView integrity failure.

It is NOT authority for two competing QLEKs.

# Provenance exclusion

Changing only any of the following MUST NOT change QLEK:

```text
GateARunId
adjudicating ReviewCampaignId
evidence root
supplement root
execution receipt
raw output locator
artifact locator
repository projection locator
reviewer profile
provider
model
model version
prompt realization
attempt id
call id
timestamp
latency
token count
cost
```

Where a historically named identifier is explicitly semantic under accepted
authority, such as source ReviewCampaignId inside FA, it enters only through the
exact semantic value or contract that declares it semantic.

# Preimage reconstructibility

Every valid hash-derived semantic identity MUST have exactly one reconstructible
canonical preimage in authoritative closure.

Require:

```text
SemanticValueId
→ exact value type + exact canonical semantic value

QLEK
→ exact LogicalQuestionDescriptor

SemanticAdmissionId
→ exact QLEK + exact canonical semantic candidate

FactId
→ exact PredicateRevisionId + exact canonical arguments

QualificationKey
→ exact QualificationContractRevisionId
  + exact anchor SemanticAdmission
  + exact additional qualification inputs
```

A digest string without reconstructible canonical meaning is not sufficient
semantic authority.

No persistence layout is selected by this rule.

# Collision behavior

If one rendered hash-derived identity resolves to more than one distinct
canonical preimage:

```text
IDENTITY-HASH-COLLISION
```

The repository/history fails closed.

No first-wins, last-wins, merge, retry or resampling is permitted.

This rule applies to:

```text
SemanticValueId
QLEK
SemanticAdmissionId
FactId
QualificationKey
```

This is distinct from a semantic-admission conflict in which physically
disconnected authority domains have the same valid QLEK but different admitted
semantic candidates.

# SemanticAdmission uniqueness remains C3

C2 identity permits computing:

```text
SemanticAdmissionId(K, V1)
```

and:

```text
SemanticAdmissionId(K, V2)
```

as distinct exact identities.

That does NOT authorize both admissions.

The accepted semantic authority remains:

```text
Admission : QLEK ⇀ SemanticCandidate
```

with at most one candidate per QLEK.

C3 closes authoritative mutation, fencing, recovery and conflict handling.

# C2 invariants

C2 establishes exactly:

```text
same exact semantic-question contract
+
same exact logical input
→ same LogicalQuestionDescriptor
→ same QLEK

different exact semantic-question contract
or different exact logical input
→ different canonical descriptor
→ different QLEK
except impossible-to-ignore cryptographic collision,
which fails closed

different execution provenance only
→ same descriptor
→ same QLEK

different nominal CandidateRevision for a candidate-bound contract
→ different ExactAuthorityRef
→ different descriptor
→ different QLEK

same challenged admission
+
same challenge contract
→ same challenge QLEK

initial candidate admission
!=
revised candidate admission
→ fresh challenge QLEK without an explicit challenge ordinal

distinct RequirementSlots may bind the same descriptor
→ one shared QLEK

same semantic fact established by different provenance graphs
→ same FactId

same exact qualification inputs
→ same QualificationKey
```

# C2 completeness assertions

The C2 construction is complete only if all of the following hold:

```text
all 20 C1 SQC families have one exact closed logical-input shape

every direct logical input has one and only one identity/reference mode

FA has one exact canonical semantic value

SM has one exact canonical semantic value

CanonicalJsonValueV1 is cross-language exact

integer semantics are exact and unbounded by implementation word size

array order cannot change accidentally during generic canonicalization

Unicode normalization cannot silently merge distinct semantic values

IdentityHashV1 has one exact collision-safe domain-separated framing

all public hash-derived identity renderings are exact

SemanticQuestionContractRevisionId encoding is exact

SemanticValueTypeRevisionId namespace is exact

SemanticValueRef representation is exact

SemanticAdmissionRef representation is exact

SemanticFactRef representation is exact

ExactAuthorityRef representation is exact

QualificationKeyRef representation is exact

QLEK construction is exact

SemanticAdmissionId construction is exact

generic PredicateRevisionId and FactId algebra are exact

QualificationContractRevisionId encoding is exact

QualificationKey algebra is exact

all seven qualification-contract input closures are representable

RequirementSlot identity is excluded from QLEK

model/provider/run/root identity is excluded unless an accepted contract
explicitly classifies a value as semantic

every hash-derived semantic identity has a reconstructible canonical preimage

identity collisions fail closed

no C3 mutation/fencing rule is selected

no concrete C4 predicate/reducer is invented

no C5 CandidateView construction is selected

no C6 serialization/protocol artifact is selected
```

# G-C2 closure

Completion gate `G-C2` is semantically satisfied when this construction artifact
is published and verified against ADR-056 and the exact published C1 catalog.

The gate establishes:

```text
a conforming implementation can compute every P8 QLEK
from the exact contract-bound semantic dependencies

without reading model/provider/run/root identity
unless an exact accepted contract declares the value semantic
```

and:

```text
same exact semantic question
→ same QLEK

different exact semantic question
→ different QLEK or fail-closed identity collision

different execution provenance only
→ same QLEK

different nominal CandidateRevision for candidate-bound contract
→ different QLEK
```

After publication and audit of this artifact:

```text
C2 = CLOSED
```

Construction may then proceed to:

```text
C3 — SemanticAdmission authority and execution-fencing closure
```

without constructing or activating protocol-v8 runtime artifacts.
