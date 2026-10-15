---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-14"
step_id: 2
id: NIB-M-GATE-A-MECHANICAL-VALIDATION
version: "1.2.0"
scope: gate-a-campaign-runner/mechanical-validation
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Mechanical Validation

## 1. Status, authority, and purpose

Implement the first active Module Brief for undecomposed M6
`mechanical-validation`.

Version `1.2.0` additively closes the exact mechanical-validation failure
requirement representation needed by M1, M8-B and M2. It preserves all version
`1.1.0` behavior, Stage A, Stage B, current P6 cognitive validation, every
semantic helper and P8 inactivity. M6 gains no BlockerId/OAR, mutation,
retry, semantic inference or orchestration authority.

Version `1.1.0` additively synchronizes mechanical helper surfaces required by
complete C9-E M5 construction. It changes no M6 ownership, no C9-D semantic
rule, no Stage A/Stage B behavior, and no P6 behavior.

This NIB-M is implementation-construction authority only. It creates no:

```text
TURNLOCK product semantic
Gate A protocol semantic
SemanticQuestionContract
SemanticValueType
PredicateRevision
QualificationContractRevision
QLEK identity rule
SemanticAdmission meaning
SemanticFact meaning
CandidateView meaning
formal assurance claim
review evidence
ADR
protocol activation
```

Use M6 only to execute accepted mechanical validation authority over exact
immutable inputs, return typed mechanical results, and seal runner-owned
mechanical validation evidence. Do not let M6 become semantic, orchestration,
persistence, scheduling, currentness, retry, candidate-construction, or
repository-publication authority.

## 2. Consumed construction authority

Consume exactly:

```text
NIB-S-GATE-A-CAMPAIGN-RUNNER 13.0.1
NIB-M-GATE-A-CONTRACTS 1.5.0
NIB-M-GATE-A-CAMPAIGN-STATE-PERSISTENCE-OWNERSHIP 3.0.4
NIB-M-GATE-A-CAMPAIGN-STATE-MUTATION-EXECUTION 9.1.0
NIB-M-GATE-A-CAMPAIGN-STATE-SNAPSHOT-INTEGRITY 8.1.0
NIB-M-GATE-A-COGNITIVE-EXECUTION-CAPTURE 2.1.1
NIB-M-GATE-A-COGNITIVE-EXECUTION-RECOVERY-OBSERVATION 1.1.0
NIB-M-GATE-A-REPOSITORY-CONTROL-MATERIALIZATION-CANDIDATE-CONSTRUCTION 2.1.1
NIB-M-GATE-A-REPOSITORY-CONTROL-PUBLICATION-REMOTE-RECOVERY 1.0.0
```

Consume the exact closed protocol-v8 C1-C6 construction authority:

```text
docs/formal/gate-a-protocol-v8-semantic-question-contract-catalog.md
docs/formal/gate-a-protocol-v8-semantic-identity-algebra.md
docs/formal/gate-a-protocol-v8-semantic-admission-authority-execution-fencing.md
docs/formal/gate-a-protocol-v8-semantic-fact-qualification-resolution.md
docs/formal/gate-a-protocol-v8-candidate-bound-identity-candidate-view.md
docs/formal/gate-a-protocol-v8-packet-receipt-evidence-projections.md
```

Consume the exact published protocol-v8 catalogs and bundle selected by the
bundle itself:

```text
formal/reviews/contracts/gate-a-semantic-question-contracts-v8.json
formal/reviews/contracts/gate-a-predicate-revisions-v8.json
formal/reviews/contracts/gate-a-qualification-contracts-v8.json
formal/reviews/protocols/gate-a-campaign-protocol-v8.json
```

Do not manually duplicate those authorities. In particular, do not maintain a
TypeScript table containing the 20 SemanticQuestionContract revisions.

Treat the M7-A materialization contract at version `2.1.1` and the M7-B
publication contract at version `1.0.0` as the current accepted inputs. Their
synchronization changes no M6 validation meaning selected here.

## 3. Protocol lifecycle boundary

Preserve exactly:

```text
P6 remains current.
P7 remains permanently inactive.
P8 remains inactive until C15.
M6 P8 validation code paths may be constructed and tested while inactive.
Construction or validation of P8 artifacts does not activate P8.
```

Do not infer current protocol identity from the availability of P8 code,
catalogs, schemas, bundles, validation results, or tests.

## 4. M6 responsibility and ownership boundary

Own only mechanical validation.

For P8, own exactly:

```text
LogicalQuestionDescriptor validation
QLEK recomputation
semantic-value identity recomputation
semantic-question-binding validation/projection
SemanticAdmission evidence-binding validation
completion → protocol candidate deterministic classification
FactId reconstruction
QualificationKey reconstruction
qualification reducer mechanical evaluation
SemanticFact reconstructibility/soundness validation
CandidateView integrity validation
candidate-bound identity validation
P8 packet/output schema validation
P8 citation/reference validation
P8 bundle/catalog/schema validation
external SemanticHistoryExport validation
mechanical validation evidence
```

Do not own:

```text
semantic-question requirement selection
question scheduling
provider invocation
provider/model selection
SemanticAdmission mutation
AdmissionAuthority
M2 WriteAuthority
retry authorization
semantic retry
qualification progression meaning
currentness
campaign applicability
SemanticFact persistence
receipt ownership
receipt assembly
origin-witness projection ownership
candidate construction
CandidateView construction
repository mutation
operator policy
```

Preserve this exact ownership separation:

```text
M5
→ owns semantic work derivation
→ owns which question is required
→ owns semantic predecessor consumption
→ owns qualification/progression interpretation
→ later C9-E owns P8 execution-receipt evidence packaging

M6
→ verifies mechanically that exact proposed semantic objects satisfy accepted
  catalogs/identity/projection contracts

M7
→ constructs exact CandidateView/materialization values

M2
→ owns authoritative semantic state and admission

M1
→ owns orchestration
```

Never substitute M6 for any of those owners.

## 5. Dependencies and the Python authority bridge

Select no new external dependency.

Consume exactly:

```text
repository-owned Python validation authority
Node standard subprocess/filesystem primitives
CampaignArtifactStore
```

Treat the Python checker as project-owned code, not as a third-party dependency.
Do not create `DC-PYTHON-*` or `DC-CHECKER-*`.

If future GREEN requires a new third-party sandbox or process package, stop
before GREEN and obtain the required Dependency Contract. Do not weaken the
sandboxing or validation contract to avoid that dependency decision.

Implement one future internal Python bridge at exactly:

```text
scripts/gate-a-mechanical-validation.py
```

Do not create that bridge while consuming this brief to create construction
authority. During future GREEN, make it:

```text
delegate to accepted scripts/check-formal-traceability.py authority
reuse existing P8 checker algorithms
never create an independent second P8 validator
perform no model call
perform no network call
perform no Git mutation
perform no M2 mutation
perform no repository publication
```

Invoke a fresh Python subprocess for each completed mechanical operation. Do not
create a long-lived Python daemon. A process cache is never semantic authority.

Invoke the bridge conceptually as:

```text
<configured Python executable>
scripts/gate-a-mechanical-validation.py
--operation <exact-operation>
```

Use this process contract:

```text
stdin  = exactly one UTF-8 JSON request document
stdout = exactly one UTF-8 JSON result document
stderr = diagnostics only
```

Use exit status `0` for every normally classified mechanical result, including
a legitimate `protocol-invalid` semantic completion.

Treat non-zero exit as one of:

```text
implementation failure
integrity failure
authority-loading failure
dependency failure
subprocess failure
```

Never reinterpret non-zero exit as:

```text
protocol-invalid
NotEstablished
PNE
retry authority
qualification failure
semantic negative result
```

## 6. Exact semantic bytes and identity computation

Never round-trip arbitrary semantic JSON through:

```text
JSON.parse
→ JavaScript number
→ JSON.stringify
```

when that path could alter exact semantic numeric meaning.

Perform all of the following through the accepted Python authority over exact
C2 bytes and value semantics:

```text
C2 semantic canonicalization
SemanticValueId derivation
QLEK derivation
SemanticAdmissionId derivation
FactId derivation
QualificationKey derivation
```

Transport arbitrary semantic JSON values crossing the TypeScript/Python bridge
as opaque exact bytes, using a base64url byte carrier or an exactly equivalent
lossless byte carrier. Do not embed those values as parsed JavaScript
number-bearing values for convenience.

Keep control-plane integers that M0 already defines as safe integer counters as
ordinary M0 values. They are not arbitrary C2 semantic integers.

Perform no Unicode normalization. Do not:

```text
NFC normalize
NFD normalize
case-fold
trim
rewrite escapes semantically
reorder semantic arrays
```

Preserve exact C2 identity.

## 7. Closed P8 authority and Python oracle anchors

Load and validate exactly the P8 authority selected by the P8 bundle. Use exact
`question_realizations` as the packaging realization mapping. For one SQC,
require exactly one matching realization and verify that it remains the
mechanically accepted mapping derived from the SQC catalog.

Do not infer realization from role strings alone. Do not create another mapping
in TypeScript.

Factor the current checker internals behind the thin bridge without changing
their accepted behavior. Use at least these oracle families as construction
anchors:

```text
E1:
_protocol_v8_e1_semantic_value_errors
_protocol_v8_e1_canonical_json_value_bytes
_protocol_v8_e1_identity_hash
_protocol_v8_e1_semantic_value_id
_protocol_v8_e1_qlek
_protocol_v8_e1_semantic_admission_id
_protocol_v8_e1_fact_id
_protocol_v8_e1_qualification_key
_protocol_v8_e1_contract_map
_protocol_v8_e1_descriptor_errors
_protocol_v8_e1_recompute_structural_qlek
_protocol_v8_e1_candidate_variant
_protocol_v8_e1_project_semantic_candidate
_protocol_v8_e1_output_validators

E2:
_protocol_v8_e2_binding_errors
_protocol_v8_e2_load_receipt_validator
_protocol_v8_e2_question_realization_map
_protocol_v8_e2_origin_witness_errors

E3-A:
semantic identity/preimage/dependency reconstruction helpers

E3-B:
qualification reducer helpers

E4:
candidate-bound/CandidateView helpers

E5:
semantic Fact/cognitive-surface/citation helpers

E6-A:
semantic-question-binding closure helpers
```

Also preserve behavior equivalent to:

```text
_protocol_v8_e3b_reduce_qualification
_protocol_v8_e5d_validate_completion_citations
_protocol_v8_e6a_strong_semantic_question_binding_errors
```

Do not copy any of that logic into TypeScript.

## 8. Disposable semantic closure input

Define exactly:

```ts
interface ProtocolV8MechanicalSemanticValueInputV1 {
  readonly ref: SemanticValueRefV1;
  readonly canonicalValue: ArtifactRef;
}

interface ProtocolV8MechanicalFactDescriptorInputV1 {
  readonly ref: SemanticFactRefV1;
  readonly descriptor: ArtifactRef;
}

interface ProtocolV8MechanicalQualificationDescriptorInputV1 {
  readonly ref: QualificationKeyRefV1;
  readonly descriptor: ArtifactRef;
}

interface ProtocolV8MechanicalClosureInputV1 {
  readonly semanticQuestionStates:
    readonly SemanticQuestionStateV1[];

  readonly semanticQuestionBindings:
    readonly ArtifactRef[];

  readonly semanticValues:
    readonly ProtocolV8MechanicalSemanticValueInputV1[];

  readonly factDescriptors:
    readonly ProtocolV8MechanicalFactDescriptorInputV1[];

  readonly qualificationDescriptors:
    readonly ProtocolV8MechanicalQualificationDescriptorInputV1[];

  readonly candidateRevisions:
    readonly CandidateRevisionRef[];
}
```

Treat this structure only as disposable M6 invocation input. It is not:

```text
authoritative history
a new semantic namespace
a persisted semantic cache
a replacement for M2
```

Require duplicate-free canonical input ordering:

```text
semanticQuestionStates:
qlek ASCII ascending

semanticQuestionBindings:
(sha256, artifactId) ascending

semanticValues:
(valueType, valueId) ascending

factDescriptors:
(predicateRevision, factId) ascending

qualificationDescriptors:
(qualificationContract, qualificationKey) ascending

candidateRevisions:
candidateId unsigned UTF-8 ascending
```

Reject exact duplicate content as redundant invocation input. If one identity
has incompatible preimages, fail closed with `IDENTITY-HASH-COLLISION`.

## 9. Disposable closure reconstruction algorithm

For every invocation requiring P8 semantic closure, construct one disposable
Python semantic closure only for that invocation:

```text
1. load the exact P8 bundle and catalogs;
2. register every exact supplied SemanticValue preimage;
3. recompute every SemanticValueId;
4. load every exact supplied semantic-question binding;
5. recompute every binding QLEK;
6. register every exact question-descriptor preimage;
7. read every supplied M2 SemanticQuestionStateV1;
8. read every Admission candidate artifact;
9. recompute every SemanticAdmissionId;
10. retain conflicts without winner selection;
11. load every exact supplied qualification descriptor;
12. recompute every QualificationKey;
13. load every exact supplied Fact descriptor;
14. recompute every FactId;
15. register every exact CandidateRevision authority ref;
16. resolve the complete semantic dependency graph;
17. fail on every dangling reference;
18. fail on every semantic dependency cycle;
19. fail on every hash collision;
20. discard the closure after the call.
```

For direct semantic predecessors, enforce:

```text
semantic-value input
→ exact value preimage resolves

semantic-admission input
→ exact Admission resolves from supplied M2 semantic state
→ no conflict winner is selected

semantic-fact input
→ exact Fact is reconstructible

exact-authority input
→ exact accepted authority resolves
```

When validating dispatchability, require every semantic Admission or Fact
predecessor used by the question to be currently consumable. Treat that result
only as mechanical verification of M5's proposed predecessor closure. Do not
transfer question selection or progression ownership to M6.

## 10. Artifact integrity and semantic-value input

Before consuming any `ArtifactRef`, call:

```text
CampaignArtifactStore.verify(ref)
```

Then read it only through:

```text
CampaignArtifactStore.readVerified(ref)
```

Classify a missing or SHA-mismatched artifact as:

```text
ARTIFACT-INTEGRITY-FAILURE
```

Never convert artifact corruption into a protocol-invalid model response.

For every `ProtocolV8MechanicalSemanticValueInputV1`, require:

```text
canonicalValue.mediaType == application/json
canonicalValue bytes parse under the exact C2 semantic JSON domain
bytes == CanonicalJsonValueBytesV1(parsed exact value)
recomputed SemanticValueId == ref.valueId
exact value type == ref.valueType
```

Reject a noncanonical source artifact. Do not silently recanonicalize and accept
it.

## 11. Semantic-question validation boundary

Define exactly:

```ts
interface ValidateProtocolV8SemanticQuestionRequestV1 {
  readonly descriptor: ArtifactRef;
  readonly closure: ProtocolV8MechanicalClosureInputV1;
}

validate_protocol_v8_semantic_question(
  request: ValidateProtocolV8SemanticQuestionRequestV1,
): Promise<ValidatedSemanticQuestionRefV1>
```

Keep this as an M6 module boundary. Do not add it to M0.

Require `request.descriptor` to satisfy:

```text
mediaType = application/json
repositoryPath = null
```

Read exact verified bytes and require the exact closed
`LogicalQuestionDescriptorV1` shape. Treat the descriptor artifact as a
proposal/input carrier. Never include its `ArtifactRef` in QLEK identity.

Resolve descriptor `D` against exactly one C1 contract:

```text
contract.revision_id == D.semanticQuestionContract
```

Require:

```text
contract exists exactly once
D.exactLogicalInput keys equal the exact contract logical_input keys
each input-ref kind matches the exact catalog declaration
SemanticValueRef.valueType matches the declaration
SemanticFactRef.predicateRevision matches the declaration
ExactAuthorityRef.authorityType matches the declaration
SemanticAdmission producer-family constraints are mechanically resolvable where
C1 declares them
```

Reject hidden extra input, missing input, and caller-selected alternate
contract.

Recompute exact `QLEK(D)` through C2. Never accept caller QLEK as authority. Any
supplied or referenced QLEK must equal the exact recomputation.

Use the exact C1 candidate-independent inventory. Return:

```text
boundCandidateRevisionId = null
```

for every candidate-independent question. Treat a WorkItem's occurrence
candidate as provenance only; never inject it into QLEK.

Use the exact C1/C5 candidate-bound inventory. The directly candidate-bound
producers are exactly:

```text
RealizationScopeInitial
RealizationScopeRevision
RepairRealizationInitial
RepairRealizationRevision
```

Their challenges inherit exact candidate identity transitively through the
challenged Admission. Never resolve `current candidate` to establish semantic
identity.

## 12. CandidateView validation boundary

Preserve this ownership:

```text
M7 constructs CandidateView.
M6 independently reconstructs the expected CandidateView from exact sealed
CandidateRevision materialization and compares equality.
M6 does not publish a competing CandidateView construction authority.
```

Define exactly:

```ts
type ProtocolV8CandidateViewCoverageValidationV1 =
  | {
      readonly kind: "complete";
    }
  | {
      readonly kind: "accepted-realization-scope";
      readonly acceptedRealizationScope: SemanticFactRefV1;
    };

interface ValidateProtocolV8CandidateViewRequestV1 {
  readonly candidate: CandidateRevisionRef;
  readonly candidateView:
    ProtocolV8MechanicalSemanticValueInputV1;
  readonly coverage:
    ProtocolV8CandidateViewCoverageValidationV1;
  readonly closure:
    ProtocolV8MechanicalClosureInputV1;
}

interface ValidatedProtocolV8CandidateViewV1 {
  readonly candidateId: CandidateRevisionId;
  readonly candidateView: SemanticValueRefV1;
  readonly validationEvidence:
    readonly [ArtifactRef, ...ArtifactRef[]];
}
```

Expose:

```ts
validate_protocol_v8_candidate_view(
  request: ValidateProtocolV8CandidateViewRequestV1,
): Promise<ValidatedProtocolV8CandidateViewV1>
```

For `coverage.kind == "complete"`:

```text
read candidate.materialization as exact GateACandidateMaterializationV1
read exact blob/symlink content artifacts through CampaignArtifactStore
reconstruct exact C5 complete CandidateView through Python authority
require equality with the supplied semantic value
```

For `coverage.kind == "accepted-realization-scope"`:

```text
validate the supplied AcceptedRealizationScopeFact through normal Fact validation
require current consumability where the consuming question requires it
derive coverage paths only from AcceptedRealizationScope.readable_paths
reconstruct the exact scoped CandidateView through Python authority
require equality with the supplied semantic value
```

Never trust caller-supplied readable paths.

Classify any claimed-versus-reconstructed CandidateView mismatch as:

```text
CANDIDATE-VIEW-INTEGRITY-FAILURE
```

Do not reinterpret it as protocol-invalid completion, `NotEstablished`,
candidate change, or retry authority.

Preserve nominal candidate identity:

```text
same repository bytes
+
different CandidateRevisionId
→ distinct candidate-bound semantic authority
```

Never collapse nominal `CandidateRevision` identity based on equal
materialization bytes.

## 13. Semantic-question binding construction

After descriptor, QLEK, dependency, and CandidateView validation succeeds,
construct exact `SemanticQuestionBindingV1` with only:

```text
semantic_question_binding_schema_version = "1.0"
logical_question_descriptor = exact descriptor
qlek = exact recomputed QLEK
semantic_values = exact transitive semantic-value preimage closure reachable
                  from direct SemanticValueRef inputs
```

Order `semantic_values` by `(valueType, valueId)` ascending using exact UTF-8
bytes. Include each semantic value once.

Do not inline:

```text
SemanticAdmission preimages
SemanticFact proof closure
ExactAuthority implementation history
receipt provenance
run/root identity
```

Validate the binding against exactly:

```text
formal/reviews/schemas/semantic-question-binding-v1.schema.json
```

Also require strong closure equality equivalent to
`_protocol_v8_e6a_strong_semantic_question_binding_errors`.

Make Python serialize arbitrary semantic values and return exact UTF-8 binding
bytes. Never parse and reserialize those values in TypeScript.

Seal the exact returned bytes through:

```text
CampaignArtifactStore.sealRunnerArtifact
mediaType = application/json
repositoryPath = null
```

Seal exactly one runner-owned question-validation trace binding at least:

```text
operation = protocol-v8-semantic-question
descriptor ArtifactRef
semanticQuestionBinding ArtifactRef
qlek
boundCandidateRevisionId
P8 protocol identity
mechanical authority revision
result = established
```

Do not add timestamp, PID, temporary path, session ID, current candidate,
provider, or model unless another bound artifact already requires that value
semantically.

Return exactly:

```text
schema = gate-a-validated-semantic-question.v1
qlek = exact recomputed QLEK
semanticQuestionBinding = exact M6-sealed binding artifact
boundCandidateRevisionId = exact C5 result or null
validationEvidence = [questionValidationTrace]
```

## 14. Semantic Fact validation

Define exactly:

```ts
interface ValidateProtocolV8SemanticFactRequestV1 {
  readonly fact: SemanticFactRefV1;
  readonly closure: ProtocolV8MechanicalClosureInputV1;
  readonly requireCurrentConsumability: boolean;
}

interface ValidatedProtocolV8SemanticFactV1 {
  readonly fact: SemanticFactRefV1;
  readonly descriptor: ArtifactRef;
  readonly resolvedSemanticView: ArtifactRef;
  readonly reconstructible: true;
  readonly consumable: boolean;
  readonly validationEvidence:
    readonly [ArtifactRef, ...ArtifactRef[]];
}
```

Expose:

```ts
validate_protocol_v8_semantic_fact(
  request: ValidateProtocolV8SemanticFactRequestV1,
): Promise<ValidatedProtocolV8SemanticFactV1>
```

For exact `SemanticFactRef F`:

```text
1. resolve exactly one supplied Fact descriptor preimage;
2. validate it against the exact PredicateRevision catalog;
3. recompute FactId;
4. require exact equality with F;
5. resolve every semantic dependency recursively;
6. reject cycles;
7. apply exact C4 predicate/reducer semantics;
8. apply C5 candidate binding where applicable;
9. derive exact ResolvedFactSemanticView;
10. determine reconstructibility;
11. determine current consumability mechanically.
```

Require no primitive Fact row. Never include a proof artifact in FactId.

Make Python produce exact canonical JSON bytes for the resolved semantic view.
Seal them as:

```text
mediaType = application/json
repositoryPath = null
```

Never change Fact identity because evidence changed.

When `requireCurrentConsumability == true` and the exact Fact is reconstructible
but not currently consumable, return no successful
`ValidatedProtocolV8SemanticFactV1`. Use the exact mechanical validation failure
boundary. Do not invent an opposite semantic proposition.

## 15. Qualification reduction

Define exactly:

```ts
interface ReduceProtocolV8QualificationRequestV1 {
  readonly qualification: QualificationKeyRefV1;
  readonly closure: ProtocolV8MechanicalClosureInputV1;
  readonly requireCurrentConsumability: boolean;
}

type ReduceProtocolV8QualificationResultV1 =
  | {
      readonly kind: "established";
      readonly fact: ValidatedProtocolV8SemanticFactV1;
      readonly validationEvidence:
        readonly [ArtifactRef, ...ArtifactRef[]];
    }
  | {
      readonly kind: "not-established";
      readonly qualification: QualificationKeyRefV1;
      readonly validationEvidence:
        readonly [ArtifactRef, ...ArtifactRef[]];
    };
```

Expose:

```ts
reduce_protocol_v8_qualification(
  request: ReduceProtocolV8QualificationRequestV1,
): Promise<ReduceProtocolV8QualificationResultV1>
```

Execute exactly:

```text
1. resolve the exact QualificationKey descriptor;
2. recompute QualificationKey;
3. load exactly one of the seven qualification contracts;
4. select the exact catalog case;
5. validate the anchor Admission;
6. validate every additional input;
7. validate every Fact dependency;
8. run the exact C4 deterministic reducer;
9. produce zero or one positive Fact.
```

Preserve behavior equivalent to `_protocol_v8_e3b_reduce_qualification`.
Require the implementation dispatch set to equal the exact catalog-derived eight
positive qualification cases. Add no ninth case and no alternative hardcoded
semantic table.

Interpret `kind = "not-established"` only as:

```text
the exact deterministic reducer did not establish its positive Fact
```

Do not interpret it as an opposite proposition, Decision Request, semantic
blocker, retry, or protocol-invalid. M5 owns progression meaning.

## 16. Two-stage completion processing

Do not require an execution receipt before classifying a new raw completion.
Use exactly:

```text
Stage A:
raw captured completion
→ deterministic protocol classification

Stage B:
after M5 evidence packaging
→ receipt/origin-witness validation
→ final protocol-valid M0 result
```

M5 requires the Stage A classification to assemble the receipt. Preserve that
ordering.

### 16.1 Stage A request and result

Define exactly:

```ts
interface ClassifyProtocolV8SemanticCompletionRequestV1 {
  readonly semanticExecution: SemanticExecutionStateV1;
  readonly executionRequest: CognitiveExecutionRequest;
  readonly capturedResult: CapturedExecutionResult;
  readonly closure: ProtocolV8MechanicalClosureInputV1;
}

interface ProtocolV8ProtocolValidCandidateClassificationV1 {
  readonly kind: "protocol-valid-candidate";
  readonly execution: SemanticExecutionLocatorV1;
  readonly qlek: QLEK;
  readonly semanticAdmissionId: SemanticAdmissionId;
  readonly semanticCandidate: ArtifactRef;
  readonly semanticQuestionBinding: ArtifactRef;
  readonly classificationEvidence: ArtifactRef;
}

type ClassifyProtocolV8SemanticCompletionResultV1 =
  | {
      readonly kind: "protocol-invalid";
      readonly result:
        ProtocolV8ProtocolInvalidSemanticCompletionRefV1;
    }
  | ProtocolV8ProtocolValidCandidateClassificationV1;
```

Expose:

```ts
classify_protocol_v8_semantic_completion(
  request: ClassifyProtocolV8SemanticCompletionRequestV1,
): Promise<ClassifyProtocolV8SemanticCompletionResultV1>
```

Treat `protocol-valid-candidate` as an intermediate M6 result, not as final
`ProtocolV8SemanticValidationResultV1` and not as SemanticAdmission.

### 16.2 Stage A preconditions

Require all of:

```text
semanticExecution.binding exists
semanticExecution.arm != null
semanticExecution.validation == null
capturedResult.execution == semanticExecution.binding.execution
executionRequest.dispatch.execution == semanticExecution.binding.execution
executionRequest.dispatch.workItem.workItemId ==
    semanticExecution.binding.execution.workItemId
semanticExecution.arm.execution == semanticExecution.binding.execution
semanticExecution.arm.qlek == semanticExecution.binding.qlek
no TechnicalExecutionFailure exists for this exact execution
```

Treat every violation as implementation/integrity failure, never
protocol-invalid.

Read `semanticExecution.binding.semanticQuestionBinding`. Require that it equals
an intact exact binding artifact in the supplied closure. Run full strong
binding validation again and require:

```text
binding.qlek == semanticExecution.binding.qlek
```

### 16.3 Packet and prompt validation

For the exact QLEK:

```text
resolve the exact SQC
resolve the exact unique P8 question_realization
require packet_schema = cognitive-execution-packet
resolve the exact expected prompt realization
validate executionRequest.packet with the exact published packet schema
validate exact contract presentation
validate semantic inputs
validate cognitive constraints
validate canonical citation catalog
validate citation references
```

Do not duplicate packet semantics in TypeScript.

Mechanically reconstruct the expected P8 cognitive packet from the exact
validated semantic closure through accepted Python checker authority. Require
`executionRequest.packet` bytes to equal the exact canonical expected packet
bytes. Treat mismatch as integrity/protocol-construction failure, never as a
model-output protocol-invalid result.

Require the execution-request prompt to equal the exact prompt artifact bound by
the unique P8 question realization. M6 chooses no prompt.

### 16.4 Raw completion validation

Require:

```text
capturedResult.rawResult.mediaType == "text/plain; charset=utf-8"
```

Read verified exact bytes and decode strict UTF-8. Treat artifact-byte integrity
failure as `ARTIFACT-INTEGRITY-FAILURE`. A syntactically malformed completed
textual semantic response enters normal protocol-invalid classification.

Classify these exact completed-output cases as normal `protocol-invalid` when
the Python authority establishes them:

```text
empty response
invalid JSON
wrong output schema
wrong task
wrong SQC output variant
forbidden NotEstablished
invalid ChallengeSemanticValue structure
invalid challenge objective coverage
duplicate prohibited semantic structures
unresolved free-string citation
citation not in exact packet catalog
contract-specific structural/semantic output violation
```

Perform no provider retry.

Use the exact C1 `NotEstablished` matrix. Treat every permitted
`NotEstablished` as a protocol-valid semantic candidate that consumes its exact
QLEK. Never treat it as missing response, protocol-invalid, no evidence, or
retry permission. Treat every forbidden `NotEstablished` as protocol-invalid.

For structurally valid output, use the exact SQC and behavior equivalent to:

```text
_protocol_v8_e1_project_semantic_candidate
+
_protocol_v8_e5d_validate_completion_citations
```

Never ask an LLM what the candidate means.

### 16.5 Stage A protocol-invalid branch

Seal exactly one classification trace. Return exactly:

```text
ProtocolV8ProtocolInvalidSemanticCompletionRefV1 {
  schema:
    "gate-a-protocol-v8-semantic-validation.v1",

  classification:
    "protocol-invalid",

  execution:
    exact semantic execution locator,

  qlek:
    exact binding QLEK,

  protocolErrors:
    exact non-empty deterministic Python-authority diagnostics,

  validationEvidence:
    [classificationTrace],
}
```

Do not return `semanticCandidate`, `semanticAdmissionId`, `executionReceipt`, or
`originWitness` in this branch.

Treat this exact result as immediately ready for M2
`AdmitProtocolV8SemanticValidationV1`.

Preserve the exact deterministic `protocolErrors` order returned by Python. Do
not sort, deduplicate, rewrite, translate, or summarize those diagnostics.

### 16.6 Stage A protocol-valid-candidate branch

Make Python produce exact `CanonicalJsonValueBytesV1(V)`. Never serialize `V`
through JavaScript. Seal those exact bytes as:

```text
mediaType = application/json
repositoryPath = null
```

Use the resulting `ArtifactRef` as `semanticCandidate`.

Compute exact `SemanticAdmissionId(K,V)` through C2. Do not include execution,
receipt, witness, provider, run, root, or generation identity.

Seal one classification trace and return exactly:

```text
kind = protocol-valid-candidate
execution = exact SemanticExecutionLocatorV1
qlek = exact K
semanticAdmissionId = exact SemanticAdmissionId(K,V)
semanticCandidate = exact canonical candidate artifact
semanticQuestionBinding = exact original M6-validated binding artifact
classificationEvidence = exact classification trace
```

Make this result deterministic and replayable. Do not treat it as
SemanticAdmission.

Future C9-E must consume Stage A classifications and map receipt attempt outcome
exactly:

```text
Stage A protocol-invalid
→ receipt outcome protocol-invalid

Stage A protocol-valid-candidate
→ receipt outcome qualified
```

M6 does not construct the receipt.

## 17. Receipt and origin-witness ownership

Preserve exactly:

```text
M5 owns assembly/sealing of the protocol-v8 execution receipt.
M6 owns validation of the resulting receipt.
M6 MUST NOT move execution-receipt ownership from M5.
```

Reuse exactly:

```text
formal/reviews/schemas/execution-receipt-v4.schema.json
```

Do not create receipt v5.

Do not assign M6 repository-path or evidence-projection ownership. Future C9-E
must construct the proposed exact P8 evidence packaging required for:

```text
execution receipt v4
semantic-question-binding audit projection
semantic-admission-origin-witness-v1
```

M6 validates those proposed artifacts. M6 does not select their repository
paths.

## 18. Stage B finalization

Define exactly:

```ts
interface FinalizeProtocolV8SemanticValidationRequestV1 {
  readonly classification:
    ProtocolV8ProtocolValidCandidateClassificationV1;

  readonly semanticQuestionBindingProjection:
    ArtifactRef;

  readonly executionReceipt:
    ArtifactRef;

  readonly originWitness:
    ArtifactRef;

  readonly projectionArtifacts:
    readonly ArtifactRef[];

  readonly semanticQuestionState:
    SemanticQuestionStateV1;

  readonly runSnapshot:
    GateARunSnapshot;

  readonly attemptClassifications:
    readonly ClassifyProtocolV8SemanticCompletionResultV1[];

  readonly closure:
    ProtocolV8MechanicalClosureInputV1;
}
```

Expose:

```ts
finalize_protocol_v8_semantic_validation(
  request: FinalizeProtocolV8SemanticValidationRequestV1,
): Promise<ProtocolV8ProtocolValidSemanticCompletionRefV1>
```

### 18.1 Projection artifact integrity

Verify every `ArtifactRef` in:

```text
semanticQuestionBindingProjection
executionReceipt
originWitness
projectionArtifacts
```

Require every path-based receipt/witness reference to resolve to exactly one
supplied projection artifact with:

```text
repositoryPath == referenced path
sha256 == referenced sha256
```

Never look up such a path in a mutable candidate repository.

Require:

```text
bytes(semanticQuestionBindingProjection)
==
bytes(classification.semanticQuestionBinding)
```

Treat repository projection location only as provenance. Never let path change
QLEK.

### 18.2 Receipt-v4 validation

Validate the exact receipt against:

```text
formal/reviews/schemas/execution-receipt-v4.schema.json
```

and the exact current P8 bundle.

Require every receipt attempt to:

```text
belong to the same logical semantic work
have exact runner Execution identity
have exact M4 call identity
map to the exact supplied Stage A classification
bind the same exact QLEK
have lawful SemanticExecutionBinding
have lawful SemanticArmBinding when receipt-admissible
```

Require receipt attempts in exact runner `Execution.attemptOrdinal` order. Never
sort by timestamp, `ExecutionId`, provider, or outcome.

Require exactly one `qualified` attempt. Require it to be final. Require its
execution ID to equal both:

```text
classification.execution.executionId
receipt.qualifying_attempt_id
```

Do not fabricate any of these into receipt attempts:

```text
PNE
unknown unresolved execution
UNRESOLVABLE without protocol completion
progression-superseded execution whose protocol result remains unknown
```

Re-run deterministic raw-output-to-candidate validation over the exact
qualifying raw completion. Require the resulting `V` to equal the exact candidate
represented by `classification.semanticCandidate`. Never trust Stage A merely
because the caller supplied it.

### 18.3 Origin-witness validation

Validate exact `semantic-admission-origin-witness-v1` against:

```text
exact QLEK
exact SemanticAdmissionId
exact canonical semantic candidate
exact binding projection
exact execution receipt
every receipt attempt binding
every lawful Arm generation
exact qualifying attempt
exact raw completion
exact runner/M2 semantic state
```

Use accepted E2 origin-witness validation authority. Never treat a witness as
self-authenticating.

Require:

```text
originWitness.origin_execution_id
==
receipt.qualifying_attempt_id
==
classification.execution.executionId
```

Require every receipt attempt QLEK to equal `classification.qlek`. Reject a
retry attempt bound to another QLEK. Select no winner.

Validate Arm generation only as execution/provenance fencing state. Never add it
to QLEK, SemanticAdmissionId, SemanticFact identity, qualification identity, or
semantic candidate identity.

### 18.4 Finalization evidence and result

Seal exactly one finalization trace binding at least:

```text
operation = protocol-v8-semantic-validation-finalization
classification evidence
semantic candidate ArtifactRef
semantic question binding ArtifactRef
binding projection ArtifactRef
execution receipt ArtifactRef
origin witness ArtifactRef
qlek
semanticAdmissionId
origin execution
```

Return exactly:

```text
ProtocolV8ProtocolValidSemanticCompletionRefV1 {
  schema:
    "gate-a-protocol-v8-semantic-validation.v1",

  classification:
    "protocol-valid",

  execution:
    classification.execution,

  qlek:
    classification.qlek,

  semanticAdmissionId:
    classification.semanticAdmissionId,

  semanticCandidate:
    classification.semanticCandidate,

  semanticQuestionBinding:
    classification.semanticQuestionBinding,

  executionReceipt:
    request.executionReceipt,

  originWitness:
    request.originWitness,

  protocolErrors:
    [],

  validationEvidence:
    [
      classification.classificationEvidence,
      finalizationTrace,
    ],
}
```

Add no third evidence item.

Treat Stage B success only as:

```text
mechanically valid completion package exists
```

Do not create Admission. Continue exactly:

```text
M1
→ submits exact result to M2

M2
→ AdmitProtocolV8SemanticValidationV1

then

M2 T4
→ reconcile SemanticAdmission
```

## 19. Crash and replay behavior

If the process crashes after Stage A:

```text
no semantic result is lost
no new model call is needed
rerun Stage A from the exact retained CapturedExecutionResult
```

Allow M5 to reconstruct receipt packaging from authoritative attempt history.
Authorize no fresh same-QLEK sample.

If exact final M6 result/artifacts exist but M2 has not admitted them:

```text
artifacts alone are not authoritative M2 state
rerun or reconstruct validation
submit the exact result to M2
do not resample
```

Keep every M6 validation operation read-only relative to external authority.
Subprocess interruption creates no ambiguous external semantic effect. Replay
the same exact immutable request safely.

Never include mechanical traces, subprocess diagnostics, or proof artifacts in:

```text
FactId
QualificationKey
QLEK
SemanticAdmissionId
SemanticValueId
```

## 20. External semantic-history validation

Define exactly:

```ts
interface ValidateExternalSemanticHistoryRequestV1 {
  readonly sourceHistory: ArtifactRef;
}

validate_external_semantic_history(
  request: ValidateExternalSemanticHistoryRequestV1,
): Promise<ValidatedExternalSemanticHistoryRefV1>
```

Mutate no M2 state.

Require:

```text
sourceHistory.mediaType == application/json
sourceHistory.repositoryPath == null
```

Read exact canonical M2 export bytes and validate M0
`SemanticHistoryExportV1` structure.

Establish exactly:

```text
sourceDomainId consistency
closedEpoch validity
successorEpoch == closedEpoch + 1
canonical array ordering
duplicate freedom
authority grant consistency
Execution → QLEK uniqueness
Arm → exact Execution/QLEK/generation validity
semantic validation → exact bound Execution/QLEK validity
AdmissionId recomputation
Admission candidate canonical validity
lawful non-empty origin-witness closure for every imported Admission
origin witness binding/receipt validity
pending protocol-valid completion exactness
unresolved-hazard exactness
positive hazard-clearance exactness
never-Armed trajectory exactness
no incompatible clearance pair
artifactClosure completeness
every referenced artifact exists and is intact
semantic identity collision absence
```

If imported history contains the same QLEK with different valid candidates,
retain exact conflict authority. Choose no winner.

Project every protocol-valid validation not lawfully reconciled to its matching
Admission/witness closure into exact `pendingProtocolValidCompletions`. Never
discard it.

Accept only these positive clearance categories:

```text
proven-not-executed
terminal-technical-no-completion
protocol-invalid-no-candidate
admission-reconciled
```

Never infer clearance from timeout, death, `UNRESOLVABLE`, or supersession.

On success, seal one external-history validation trace and construct exact
`ValidatedExternalSemanticHistoryRefV1` with:

```text
sourceHistory
sourceDomainId
closedEpoch
successorEpoch
admissions
pendingProtocolValidCompletions
unresolvedHazards
hazardClearances
unarmedTrajectories
validationEvidence = [externalHistoryValidationTrace]
```

Grant no import authority. Only M2 `ReconcileExternalSemanticHistory` may mutate
local authoritative history.

## 21. Existing current-P6 M6 operations

Close current M6 construction responsibilities from NIB-S without changing
them. Expose module operations equivalent to:

```text
derive_candidate_subject
project_candidate_review_authority
validate_cognitive_attempt
validate_repository_integrity
validate_gate_a_qualification
validate_post_publication_integrity
```

Use the exact NIB-S request and result types. Do not add another current-P6
validation algorithm.

Preserve current role-aware P6 cognitive-attempt behavior exactly. Use supported
Python authority, return the exact M6 classification, and let M5 consume it.
M6 owns no retry.

Keep C9-D P8 completion classification additive and inactive.

For legacy path-based Python authority, bind candidate authority to:

```text
sealed candidate materialization
+
exact referenced immutable content
```

Never accept a caller-provided mutable checkout path as candidate authority.

## 22. Ephemeral candidate realization and symlink safety

Create one unique ephemeral validation root for each future candidate-scoped
subprocess invocation. Treat it only as operational scratch. Never include it in
candidate identity, evidence identity, repository authority, or currentness.

Guarantee that candidate-controlled symlinks cannot make Python dereference host
filesystem content outside the exact candidate authority. Host content outside
the exact candidate materialization must not influence validator reads.

Select no third-party sandbox package in this brief. If Node, Python, and OS
primitives cannot guarantee this rule on a supported platform, stop before
GREEN and obtain an explicit Dependency Contract or construction decision. Do
not weaken the rule.

After subprocess completion or failure:

```text
close process handles
remove the ephemeral candidate realization
```

Treat best-effort cleanup failure as operational cleanup failure. Never seal a
temporary path as evidence.

## 23. Common mechanical validation trace

Define exactly:

```ts
interface GateAMechanicalValidationTraceV1 {
  readonly schema:
    "gate-a-mechanical-validation-trace.v1";

  readonly operation:
    | "candidate-subject"
    | "candidate-review-authority"
    | "cognitive-attempt"
    | "repository-integrity"
    | "gate-a-qualification"
    | "post-publication-integrity"
    | "protocol-v8-semantic-question"
    | "protocol-v8-candidate-view"
    | "protocol-v8-semantic-fact"
    | "protocol-v8-qualification"
    | "protocol-v8-semantic-completion"
    | "protocol-v8-semantic-validation-finalization"
    | "protocol-v8-external-semantic-history";

  readonly protocolBundle:
    ProtocolBundleRef | null;

  readonly execution:
    SemanticExecutionLocatorV1 | null;

  readonly qlek:
    QLEK | null;

  readonly candidateId:
    CandidateRevisionId | null;

  readonly inputArtifacts:
    readonly ArtifactRef[];

  readonly outputArtifacts:
    readonly ArtifactRef[];

  readonly result:
    | "established"
    | "protocol-valid"
    | "protocol-invalid"
    | "not-established";

  readonly authorityRevision:
    "gate-a-mechanical-validation.v1";
}
```

Apply exact first-occurrence duplicate removal to trace arrays. Do not include:

```text
timestamp
PID
temporary path
wall-clock duration
session ID
environment variables
secret
credential
mutable repository path
stdout/stderr free-form body
```

Treat each trace as provenance only. It changes no semantic identity.

Permit raw stderr only in operational logs. It is not semantic evidence. Only
deliberately sealed M6 trace artifacts enter `validationEvidence`.

## 24. Failure taxonomy

Define exactly:

```ts
type MechanicalValidationFailureCodeV1 =
  | "INVALID-MECHANICAL-VALIDATION-REQUEST"
  | "ARTIFACT-INTEGRITY-FAILURE"
  | "MECHANICAL-AUTHORITY-LOAD-FAILURE"
  | "MECHANICAL-AUTHORITY-INTEGRITY-FAILURE"
  | "MECHANICAL-AUTHORITY-EXECUTION-FAILURE"
  | "IDENTITY-HASH-COLLISION"
  | "SEMANTIC-CLOSURE-INTEGRITY-FAILURE"
  | "CANDIDATE-VIEW-INTEGRITY-FAILURE"
  | "SEMANTIC-HISTORY-VALIDATION-FAILURE"
  | "MECHANICAL-VALIDATION-TRACE-SEAL-FAILURE";
```

Map failures exactly:

```text
malformed caller-owned request shape
→ INVALID-MECHANICAL-VALIDATION-REQUEST

missing/corrupt ArtifactRef
→ ARTIFACT-INTEGRITY-FAILURE

required Python authority/schema/catalog cannot load
→ MECHANICAL-AUTHORITY-LOAD-FAILURE

catalog/schema/checker authority contradicts accepted exact binding
→ MECHANICAL-AUTHORITY-INTEGRITY-FAILURE

Python subprocess crashes/nonzero/unparseable protocol
→ MECHANICAL-AUTHORITY-EXECUTION-FAILURE

same semantic ID with distinct canonical preimages
→ IDENTITY-HASH-COLLISION

dangling/cyclic/incompatible semantic closure
→ SEMANTIC-CLOSURE-INTEGRITY-FAILURE

claimed CandidateView differs from reconstruction
→ CANDIDATE-VIEW-INTEGRITY-FAILURE

external history is not a lawful complete closed history
→ SEMANTIC-HISTORY-VALIDATION-FAILURE

trace sealing or returned ArtifactRef verification fails
→ MECHANICAL-VALIDATION-TRACE-SEAL-FAILURE
```

Except for exact completed raw-output validation failures defined for Stage A,
never equate M6 invocation or integrity failure with `protocol-invalid`. Never
hide an implementation failure by clearing semantic hazard.

Neither `protocol-invalid`, `NotEstablished`, qualification
`not-established`, CandidateView failure, nor external-history failure directly
authorizes another Execution. M5 and M2 retain every lawful retry or replacement
authority.

## 25. Exact schema bindings

Bind future P8 validation to exactly:

```text
execution-receipt-v4
formal/reviews/schemas/execution-receipt-v4.schema.json
content SHA-256:
9d5e0b50bf9b5464fadc9c57edfa265935bdf0ace9fcaf1c9770e5f7e7ab312c

semantic-question-binding-v1
formal/reviews/schemas/semantic-question-binding-v1.schema.json
content SHA-256:
fae52d48d08df8e9c3d7cafc74899913f4cc5655fb0a7ac8eb594df6edece15e

semantic-admission-origin-witness-v1
formal/reviews/schemas/semantic-admission-origin-witness-v1.schema.json
content SHA-256:
acdcf78b6862080f5147df525bc919e2b8eb6eb94b3c920fee8b9886e582607b

semantic-identity-v1
formal/reviews/schemas/semantic-identity-v1.schema.json
content SHA-256:
fc9e6a4dc241508c50a1d1671c9f43bd04ab257a8d0ad5b6319ba5522966a3f3
```

Do not dynamically accept another schema revision.

## 26. Integration sequence

Preserve this ownership-aware integration sequence:

```text
M5 derives exact required semantic work and predecessor closure
→ M1 requests M6 semantic-question validation
→ M6 recomputes QLEK, validates dependencies/CandidateView, seals binding/trace
→ M2 admits exact semantic Execution binding and later Arm authority
→ M1 dispatches exact armed request to M4
→ M4 captures exact completion
→ M1 requests M6 Stage A classification
→ M6 returns protocol-invalid final result OR protocol-valid candidate
→ protocol-invalid final result can be submitted immediately by M1 to M2
→ for protocol-valid candidate, M5 constructs receipt-v4 and witness packaging
→ M1 requests M6 Stage B finalization
→ M6 revalidates receipt, candidate, binding projection, and origin witness
→ M1 submits exact final protocol-valid result to M2
→ M2 admits validation and performs T4 reconciliation
```

Keep all receipt attempts on one exact QLEK. Do not make same evidence root,
GateARun, or receipt owner a semantic predecessor requirement unless the exact
semantic contract itself includes that identity. Preserve cross-run semantic
reuse.

Once Stage A establishes protocol-valid candidate `V`, do not erase `V` because
of candidate staleness, run staleness, progression supersession, or later
current-candidate change. Stage B and T4 remain mandatory for the old exact
QLEK.

## 27. Construction examples

### 27.1 Malformed completed JSON

Given an exact armed semantic execution, intact packet/prompt/binding, and a
captured strict UTF-8 completion whose exact text is:

```text
{
```

classify Stage A as `protocol-invalid`. Preserve the exact Python diagnostic
order, seal exactly one classification trace, return no semantic candidate,
receipt, or witness, and permit M1 to submit that exact result to M2. Perform no
provider retry.

### 27.2 Lawful NotEstablished

Given an exact SQC whose C1 matrix permits `NotEstablished`, an exact completion
matching that variant is a protocol-valid candidate for the same exact QLEK.
Produce exact canonical candidate bytes and exact `SemanticAdmissionId(K,V)`.
Do not interpret it as absent evidence or retry permission. Do not create
SemanticAdmission before Stage B and M2 T4.

### 27.3 Candidate nominal identity

Given two `CandidateRevisionRef` values with byte-identical materializations but
distinct `CandidateRevisionId` values, validate candidate-bound CandidateViews
against each exact nominal revision separately. Do not reuse one candidate-bound
semantic identity as the other.

### 27.4 Stage A crash replay

Given a retained exact `CapturedExecutionResult`, if M6 crashes after sealing a
Stage A candidate but before Stage B, replay Stage A from the same exact inputs.
Require the same canonical candidate bytes and SemanticAdmissionId. Make no new
model call and authorize no same-QLEK sample.

### 27.5 External same-QLEK conflict

Given a lawful external history containing the same QLEK and two different valid
candidates, validate and retain the exact conflict closure. Choose no winner and
grant no import authority; only M2 may reconcile the validated history.

## 28. Edge cases and required behavior

Handle at least these boundaries exactly:

```text
unknown SQC
→ invalid mechanical request/authority resolution; no QLEK result

same identity with distinct preimages
→ IDENTITY-HASH-COLLISION

missing semantic predecessor
→ SEMANTIC-CLOSURE-INTEGRITY-FAILURE

cyclic Fact dependency
→ SEMANTIC-CLOSURE-INTEGRITY-FAILURE

noncanonical semantic-value bytes
→ reject; do not recanonicalize and accept

artifact SHA mismatch
→ ARTIFACT-INTEGRITY-FAILURE

CandidateView mismatch
→ CANDIDATE-VIEW-INTEGRITY-FAILURE

valid completed text with malformed JSON
→ protocol-invalid

non-zero Python process exit
→ MECHANICAL-AUTHORITY-EXECUTION-FAILURE

protocol-valid Stage A plus missing receipt/witness
→ no final protocol-valid result

receipt attempt with another QLEK
→ fail finalization; choose no winner

multiple or non-final qualified receipt attempts
→ fail finalization

external UNRESOLVABLE execution
→ unresolved hazard; never clearance

cleanup failure for ephemeral realization
→ operational cleanup failure
```

## 29. Required invariants

```text
M6-01
Every returned ValidatedSemanticQuestionRefV1 has exact recomputed QLEK.

M6-02
M6 never computes P8 semantic identity through lossy JavaScript numeric
round-tripping.

M6-03
Semantic-question binding contains the exact transitive semantic-value preimage
closure and no provenance-only identity.

M6-04
Candidate-independent question validation returns no candidate binding.

M6-05
Candidate-bound question validation preserves exact nominal CandidateRevision.

M6-06
CandidateView equality is established from exact sealed candidate materialization.

M6-07
M6 constructs no CandidateView authority competing with M7.

M6-08
FactId is recomputed from exact PredicateRevision + arguments only.

M6-09
QualificationKey is recomputed from exact qualification descriptor only.

M6-10
Qualification reduction returns zero or one positive Fact and never an opposite
negative fact.

M6-11
Every lawful NotEstablished model output is a protocol-valid semantic candidate.

M6-12
Forbidden NotEstablished is protocol-invalid.

M6-13
Malformed completed model JSON is protocol-invalid, not TechnicalExecutionFailure.

M6-14
Artifact corruption is integrity failure, not protocol-invalid.

M6-15
Stage A protocol-valid candidate is deterministic from exact raw output and SQC.

M6-16
Stage A protocol-valid candidate is not yet SemanticAdmission.

M6-17
M6 does not construct P8 execution receipt.

M6-18
M6 does not own origin-witness repository projection.

M6-19
Stage B validates exactly one qualified final receipt attempt.

M6-20
Every P8 semantic receipt attempt binds the same QLEK.

M6-21
Origin execution equals receipt qualifying attempt.

M6-22
Origin witness is validated against exact M2 execution/binding/Arm authority.

M6-23
Protocol-valid final result contains exactly two validationEvidence refs.

M6-24
Protocol-invalid final result contains exactly one validationEvidence ref.

M6-25
Protocol-valid completion remains mandatory for T4 despite later candidate/run
staleness.

M6-26
M6 never creates retry authority.

M6-27
M6 never creates SemanticAdmission.

M6-28
M6 never persists primitive SemanticFact truth.

M6-29
External history validation selects no conflict winner.

M6-30
External history validation cannot treat UNRESOLVABLE as hazard clearance.

M6-31
M6 validation is replay-safe after process interruption.

M6-32
Temporary filesystem paths never enter semantic identity or validation evidence.

M6-33
Candidate-controlled symlinks cannot expose host filesystem content to Python
validation authority.

M6-34
P6 mechanical-validation behavior is unchanged.

M6-35
P8 remains inactive.
```

## 30. Required future NIB-T cases

Create no NIB-T while consuming this brief. Require a later NIB-T to cover at
least:

```text
descriptor exact input-key mismatch rejected
unknown SQC rejected
QLEK mismatch rejected
semantic value wrong valueId rejected
semantic value Unicode normalization not performed
semantic value large integer identity not JS-rounded
identity collision fail closed
binding semantic-value order mismatch rejected
missing transitive semantic value rejected
candidate-independent question excludes candidate ID
candidate-bound same bytes / different CandidateRevision remains distinct
complete CandidateView mismatch rejected
readable-path CandidateView derived from AcceptedRealizationScope
FactId mismatch rejected
Fact dependency cycle rejected
QualificationKey mismatch rejected
all eight qualification cases reachable mechanically
qualification failure produces no opposite Fact
lawful NotEstablished protocol-valid
forbidden NotEstablished protocol-invalid
invalid UTF-8/raw JSON protocol-invalid where appropriate
wrong output task protocol-invalid
wrong output variant protocol-invalid
unresolved citation protocol-invalid
valid completion produces deterministic candidate bytes
same raw completion replay produces exact same candidate/id
protocol-invalid output contains no candidate/receipt/witness
receipt attempt on another QLEK rejected
non-final qualified receipt attempt rejected
multiple qualified receipt attempts rejected
unknown execution fabricated into receipt rejected
binding projection bytes differing from M6 binding rejected
origin execution != qualifying attempt rejected
origin witness wrong Arm generation rejected
origin witness wrong candidate rejected
origin witness wrong admission ID rejected
Stage B candidate differs from Stage A candidate rejected
external history wrong source domain binding rejected
external history incomplete witness closure rejected
external history conflicting same-K candidates preserved as conflict
external UNRESOLVABLE hazard remains unresolved
external clearance without evidence closure rejected
symlink escape cannot affect validation
```

## 31. Construction classifications

Record these construction classifications exactly. Create no ADR.

### 31.1 Thin Python authority bridge

```text
statement:
M6 uses one thin repository-owned Python bridge over the existing canonical
checker authority rather than duplicating protocol-v8 validation logic in
TypeScript

semantic disposition:
no-normative-impact

affected layer:
architecture-or-implementation

normative impact:
none
```

### 31.2 Two-stage completion processing

```text
statement:
protocol-v8 semantic completion processing is split into deterministic Stage A
classification and Stage B evidence finalization so M5 can retain execution
receipt ownership without circularly requiring a receipt before M6 can classify
the raw completion

semantic disposition:
derived-from-existing-authority

affected layer:
architecture-or-implementation

normative impact:
none
```

### 31.3 Exact-byte semantic identity

```text
statement:
all C2 semantic canonicalization and identity hashing occurs in the exact Python
authority over exact semantic bytes, while TypeScript transports opaque
canonical bytes and identifiers rather than lossy parsed semantic numbers

semantic disposition:
derived-from-existing-authority

affected layer:
architecture-or-implementation

normative impact:
none
```

### 31.4 CandidateView validation ownership

```text
statement:
M6 reconstructs CandidateView independently from M7 sealed materialization only
for validation; M7 remains the CandidateView construction owner

semantic disposition:
derived-from-existing-authority

affected layer:
architecture-or-implementation

normative impact:
none
```

## 32. Explicit prohibitions

Forbid exactly:

```text
TypeScript reimplementation of C1-C6 semantic algorithms
JavaScript semantic identity hashing
JavaScript lossy semantic integer conversion
LLM-based validation
model voting
semantic candidate selection
provider/model switching
M6 retry authorization
M6 SemanticAdmission mutation
M6 M2 database mutation
M6 primitive SemanticFact persistence
M6 current-candidate inference
M6 receipt assembly
M6 receipt ownership
M6 repository-path selection for origin witness
M6 CandidateView construction authority
mutable workspace as candidate authority
mutable repository path as semantic authority
receipt ownership as semantic predecessor availability
UNRESOLVABLE as clearance
protocol-invalid as implementation-error fallback
full-repository checker invocation as a substitute for exact completion
classification when a focused accepted oracle exists
P8 activation
```

M6 may deterministically project only:

```text
V = protocol-defined candidate of exact raw output
```

Never let M6:

```text
choose between two model outputs
pick a preferred candidate
repair a candidate
merge candidates
vote
rank semantic candidates
switch provider/model
ask another LLM
use confidence
```

M6 never establishes current `S`, current `P`, or current
`CandidateRevision`. Candidate identity validation is not currentness. Keep
currentness in M3, M1, and M2.

## 33. Construction completeness gate

Before GREEN, make the implementation plan and later NIB-T mechanically answer:

```text
how QLEK is recomputed
how semantic value IDs are verified
how semantic-question binding is built
how candidate binding is determined
how CandidateView is independently validated
how FactId is reconstructed
how QualificationKey is reconstructed
how qualification reduction works
how NotEstablished is classified
how a raw response becomes protocol-invalid
how a raw response becomes protocol-valid candidate V
why valid Stage A cannot immediately create Admission
why M5 must package receipt/witness before final valid result
who owns receipt
who validates receipt
how all receipt attempts stay on one QLEK
how origin witness is validated
how final SemanticAdmissionId is recomputed
what M2 receives
how external history is validated
why M6 can replay after crash
why arbitrary semantic integers/Unicode cannot be altered through JS
why CandidateView construction remains M7-owned
why P8 remains inactive
```

Stop future GREEN rather than making an unrecorded semantic, architectural,
protocol, identity, qualification, CandidateView, receipt-ownership,
subprocess-protocol, dependency, or module-ownership decision.

## 34. C9-E helper boundary

M5 owns semantic progression but must not invoke Python, duplicate C1/C2/C4
algorithms, compute semantic IDs, project P8 packet semantics, recompute the
hostile-finding subject, or parse arbitrary semantic JSON through JavaScript
number semantics. M6 already owns those mechanical operations.

Add only the six helper surfaces below. M6 selects no finding, currentness,
reviewer profile, WorkItem, semantic progression branch, Admission, receipt or
repository mutation.

Define the shared helper value result:

```ts
interface ValidatedProtocolV8SemanticValueV1 {
  readonly ref: SemanticValueRefV1;
  readonly canonicalValue: ArtifactRef;
  readonly validationEvidence:
    readonly [ArtifactRef, ...ArtifactRef[]];
}
```

## 35. FindingAdjudicationBasis projection helper

Expose conceptually:

```ts
project_protocol_v8_finding_adjudication_basis(
  request
): Promise<ProjectProtocolV8FindingAdjudicationBasisResultV1>
```

Bind input exactly to the authoritative `FindingRef` already selected by M5,
its exact source `ReviewCampaignRef`, exact normalized-finding artifact, exact
current `SemanticSubjectRef`, exact current `ProtocolBundleRef`, exact
`GateACampaignAuthorityEvaluationV1`, and the exact authoritative
`GateARunSnapshot` required only for binding verification.

Mechanically:

```text
verify source campaign/finding exactness
recompute exact historical hostile-finding-subject-v1 substantive SHA
construct exact C2 FindingAdjudicationBasisV1
canonicalize through accepted Python authority
compute exact SemanticValueId
seal exact canonical value
return exact SemanticValueRefV1
return substantiveFindingSha256
return non-empty validation evidence
```

Return:

```ts
interface ProjectProtocolV8FindingAdjudicationBasisResultV1 {
  readonly findingAdjudicationBasis:
    ValidatedProtocolV8SemanticValueV1;
  readonly substantiveFindingSha256: Sha256;
  readonly validationEvidence:
    readonly [ArtifactRef, ...ArtifactRef[]];
}
```

Make no currentness or progression decision.

## 36. Semantic-value proposal helper

Expose:

```ts
validate_protocol_v8_semantic_value_proposal(...)
```

Consume exact `valueType`, exact canonical-value `ArtifactRef`, and exact
mechanical closure where required. Read exact bytes, validate exact C2/C5 form,
recompute `SemanticValueId`, preserve exact canonical bytes, and return
`ValidatedProtocolV8SemanticValueV1`.

Use this boundary for at least `SurvivingMaterialBasisV1`, `CandidateViewV1`, and
future exact P8 values requiring the same validation. A caller never supplies an
authoritative claimed `valueId`.

## 37. Fact-descriptor proposal helper

Expose:

```ts
validate_protocol_v8_semantic_fact_descriptor(...)
```

Consume exact `SemanticFactDescriptorV1` artifact, exact
`ProtocolV8MechanicalClosureInputV1`, and
`requireCurrentConsumability: boolean`. Recompute `FactId`, construct exact
`SemanticFactRefV1`, apply the existing C9-D soundness/reconstructibility
validation, and return `ValidatedProtocolV8SemanticFactV1`. Persist no Fact
state.

## 38. Qualification-descriptor reducer helper

Expose:

```ts
reduce_protocol_v8_qualification_descriptor(...)
```

Consume exact `QualificationKeyDescriptorV1` artifact and exact
`ProtocolV8MechanicalClosureInputV1`. Recompute `QualificationKey`, construct
exact `QualificationKeyRefV1`, run the existing C4 reducer, and return the
qualification ref, descriptor, and either the exact established positive Fact
or normal `not-established`. Reducer absence never establishes an opposite
proposition.

## 39. Safe semantic progression view

Expose:

```ts
project_protocol_v8_semantic_progression_view(...)
```

Consume one exact consumable `SemanticAdmissionRecordV1` and its exact
semantic-question binding/closure. Return exactly one strict closed value:

```ts
interface ProtocolV8SemanticProgressionViewV1 {
  readonly schema:
    "gate-a-protocol-v8-semantic-progression-view.v1";
  readonly qlek: QLEK;
  readonly admissionId: SemanticAdmissionId;
  readonly semanticQuestionContract:
    SemanticQuestionContractRevisionId;
  readonly result:
    | {
        readonly kind: "materiality";
        readonly anyAxisTrue: boolean;
        readonly allAxesFalse: boolean;
      }
    | {
        readonly kind: "refutation";
        readonly state: "positive" | "not-established";
      }
    | {
        readonly kind: "discovery";
        readonly state:
          | "initial"
          | "revised-positive"
          | "not-established";
        readonly targetedStatementFact:
          ValidatedProtocolV8SemanticFactV1 | null;
        readonly semanticDisposition:
          | "derived-from-existing-authority"
          | "decision-required"
          | "no-normative-impact"
          | "authority-conflict-or-uncertain"
          | null;
      }
    | {
        readonly kind: "unique-correction";
        readonly state: "positive" | "not-established";
      }
    | {
        readonly kind: "realization-scope";
        readonly state: "positive" | "not-established";
      }
    | {
        readonly kind: "repair-realization";
        readonly state: "positive" | "not-established";
        readonly operationsEmpty: boolean;
      }
    | {
        readonly kind: "challenge";
        readonly objections: "zero" | "nonzero";
      };
  readonly validationEvidence:
    readonly [ArtifactRef, ...ArtifactRef[]];
}
```

For `DiscoveryClassificationInitial@1`, mechanically derive
`targetedStatementFact` from exactly the
`classification_statement_ordinal` named by `earliest_unresolved_cause`. Make no
routing decision. For a positive targeted Discovery revision, return the exact
revised targeted-statement Fact. For `NotEstablished`, return both
`targetedStatementFact = null` and `semanticDisposition = null`.

This view prevents M5 from parsing arbitrary semantic numbers or Unicode.

## 40. Pre-dispatch P8 execution-input projection

Expose:

```ts
project_protocol_v8_semantic_execution_inputs(...)
```

Consume exact `ValidatedSemanticQuestionRefV1`, exact current P8
`ProtocolBundleRef`, and exact `ProtocolV8MechanicalClosureInputV1`. Reuse the
same accepted Python authority that Stage A later uses to reconstruct expected
packet bytes.

Return:

```ts
interface ProtocolV8SemanticExecutionInputsV1 {
  readonly schema:
    "gate-a-protocol-v8-semantic-execution-inputs.v1";
  readonly qlek: QLEK;
  readonly role: ProtocolV8CognitiveExecutionRole;
  readonly prompt: ArtifactRef;
  readonly packet: ArtifactRef;
  readonly validationEvidence:
    readonly [ArtifactRef, ...ArtifactRef[]];
}
```

Require the prompt to be the exact immutable prompt selected by the unique P8
`question_realization`. Seal exact canonical `cognitive-execution-packet-v1`
bytes with `repositoryPath == null`; those bytes must equal what Stage A later
reconstructs. Choose no reviewer profile and create no WorkItem, Admission or
receipt.

## 41. Regression and future tests

Keep these operations unchanged:

```text
derive_candidate_subject
project_candidate_review_authority
validate_cognitive_attempt
validate_repository_integrity
validate_gate_a_qualification
validate_post_publication_integrity
```

Keep every C9-D Stage A/Stage B rule unchanged. P6 remains current and
unchanged; P8 remains inactive until C15.

Require future tests for exact FA source-finding hash binding, semantic-value
exact-byte validation, FactId and QualificationKey recomputation, all progression
view variants, earliest Discovery target selection, `NotEstablished` null
projection, packet equality between pre-dispatch and Stage A, no reviewer
selection, no JS large-integer or Unicode rewrite, complete C9-D Stage A/Stage B
regression, both exact mechanical-validation failure requirements, each exact
cause/result mismatch rejection, exact basis ordering, empty resolution
contracts, generic M0 obligation-ID recomputation, and proof that M6 constructs
neither BlockerId nor OAR.

## 42. Mechanical-validation failure requirement boundary

Define exactly:

```ts
interface GateAMechanicalValidationObligationDefinitionV1 {
  readonly schema:
    "gate-a-mechanical-validation-obligation-definition.v1";

  readonly kind:
    | "gate-a-qualification"
    | "post-publication-integrity";
}
```

Seal the exact definition through M0 canonical runner JSON. Construct its
`ObligationRef` only through M0 `mechanical-validation-obligation.v1` using:

```text
runId
obligationKind = definition.kind
candidateId
basisId
exact sealed definition.sha256
```

Every such obligation has:

```text
reviewCampaignId == null
candidateId == exact affected candidate
```

Use `basisId` exactly as fixed by M0:

```text
gate-a-qualification
→ CandidateReviewReadinessRef.reviewReadinessId

post-publication-integrity
→ PublicationConfirmationRef.publicationConfirmationId
```

Define the cause descriptor schema exactly as:

```text
gate-a-mechanical-validation-operational-cause.v1
```

Its closed cause-kind set is exactly:

```text
gate-a-qualification-not-established
post-publication-integrity-not-established
```

No third cause kind exists.

### 42.1 Gate A qualification failure

Seal this exact semantic payload through M0 canonical runner JSON:

```ts
{
  schema:
    "gate-a-mechanical-validation-operational-cause.v1",

  kind:
    "gate-a-qualification-not-established",

  candidateId:
    exact candidate ID,

  reviewReadinessId:
    exact CandidateReviewReadinessRef.reviewReadinessId
}
```

Require the exact M6 result:

```text
requestKind == gate-a-qualification
passed == false
candidateId == exact candidate
campaign sets == exact readiness campaign sets
```

The cause uses:

```text
producer = mechanical-validation
basisArtifacts = exact validation.evidence in exact result order
resolutionContracts = []
```

### 42.2 Post-publication integrity failure

Seal this exact semantic payload through M0 canonical runner JSON:

```ts
{
  schema:
    "gate-a-mechanical-validation-operational-cause.v1",

  kind:
    "post-publication-integrity-not-established",

  candidateId:
    exact candidate ID,

  publicationConfirmationId:
    exact confirmation ID,

  target:
    exact PublishedRepositoryViewRef.target,

  validatedAuthority:
    exact PublishedRepositoryViewRef.authority
}
```

Require the exact M6 result:

```text
requestKind == post-publication-integrity
passed == false
candidateId == publishedView.candidateId
publicationConfirmationId == publishedView.publicationConfirmationId
target == publishedView.target
validatedAuthority == publishedView.authority
```

The cause uses:

```text
producer = mechanical-validation
basisArtifacts = orderedUnique(
  validation.evidence
  followed by
  publishedView.materializationEvidence
)
resolutionContracts = []
```

`orderedUnique` uses exact `ArtifactRef` equality and preserves first
occurrence.

Empty resolution contracts mean exactly:

```text
the same immutable validation basis cannot be transformed into a passing
mechanical fact by acknowledging, retrying, resampling, or answering a semantic
question inside the same GateARun
```

### 42.3 Helper operations

Expose exactly:

```text
derive_gate_a_qualification_failure_requirement
derive_post_publication_integrity_failure_requirement
validate_mechanical_validation_obligation
validate_mechanical_validation_operational_cause
```

Each derivation operation returns exactly:

```text
blockingObligation
cause
```

The validators require the exact definition/cause shape, intact artifacts,
identity formula, kind/basis/candidate binding, cause/result binding and empty
resolution-contract set fixed above. They establish representation and exact
mechanical binding only.

The derivation and validation operations create no `BlockerId`, create no
Operator Action Request and mutate no M2 state. M8-B remains the sole
blocker/OAR owner.

### 42.4 Construction classification

```text
statement:
M6 can legitimately return passed=false for Gate A or post-publication
mechanical validation, but M1 cannot invent blocker cause/obligation identity

semantic disposition:
derived-from-existing-authority

resolution:
M6-owned dedicated mechanical-validation obligation/cause + M8-B
materialization + M2 admission

affected layer:
architecture-or-implementation

normative impact:
none
```

No ADR is required.
