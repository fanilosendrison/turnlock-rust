---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-13"
step_id: 2
id: NIB-M-GATE-A-CONTRACTS
version: "1.2.0"
scope: gate-a-campaign-runner/contracts
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Contracts

## 1. Status, authority, and purpose

Implement the first active Module Brief for undecomposed M0 `contracts`.

Version `1.2.0` additively synchronizes M0 representation and runtime
validation with the protocol-v8 M2 semantic-authority boundary. It changes no
existing identity, canonicalization, dependency, protocol, semantic, or
authority rule. It retains the exact 19-domain deterministic runner-ID registry,
`zod@4.6.7`, and the future `DC-ZOD-GATE-A-CONTRACTS` requirement.

Version `1.1.0` closed the two M5-A construction obligations omitted from
version `1.0.0`: expose the exact `CampaignArtifactStore` TypeScript contract
without implementing its effectful behavior, and provide exact structural
runtime validation for execution-receipt schema v3 before M5-A sealing. This
minor revision added backward-compatible M0 contract surface and changed no
identity, canonicalization, dependency, protocol, semantic, or authority rule.

Consume exactly:

```text
NIB-S-GATE-A-CAMPAIGN-RUNNER 11.0.0
accepted ADR-041 through ADR-049
accepted ADR-053 through ADR-056
closed protocol-v8 C1-C7 construction
```

Implement construction contracts only. Create no:

```text
TURNLOCK product semantics
canonical formal semantics
hostile-review protocol semantics
formal-assurance claims
review evidence
verification evidence
product ADR
```

Keep P6 current, P7 permanently inactive, and P8 inactive. Do not activate P8.

Do not decompose M0. Create no M0-A or M0-B sub-brief or implementation
responsibility.

## 2. Module responsibility

Make M0 own exactly:

```text
cross-module TypeScript contract declarations
runtime structural validation for runner-owned serialized contract forms
runtime lexical validation for opaque runner IDs and protocol-v8 semantic
identity/reference strings
canonical runner-owned JSON serialization
pure deterministic runner orchestration ID derivation
the exact immutable root-preflight obligation-definition value and canonical
bytes
pure equality/helpers required to compare already-valid contract values
mechanically
ProtocolV8CognitiveExecutionRole representation
protocol-v8 semantic reference representations that are exact TypeScript
mirrors of the published immutable schemas
the exact CampaignArtifactStore TypeScript interface contract implemented by M2
runtime structural validation of the exact execution-receipt schema-v3
runner-side representation required by M5-A before sealing
```

M0 may validate representation. M0 must not decide meaning.

## 3. Prohibited module responsibilities

Perform no:

```text
I/O
state mutation
repository access
Git access
Python invocation
provider/model invocation
currentness decision
semantic-question derivation
semantic equality decision
qualification reduction
SemanticAdmission mutation
SemanticFact derivation
CandidateView construction
recovery classification
scheduling
orchestration
```

Keep all effectful operations and authoritative decisions in their NIB-S-owned
modules.

## 4. System-level cross-module contract ownership

Treat NIB-S 11.0.0 sections 12 through 16 as the canonical system-level
cross-module shape authority.

Implement those exact declarations. Do not add, remove, rename, widen, narrow,
default, reinterpret, or silently normalize a field defined by NIB-S.

Make the source implementation contain or re-export exact structural TypeScript
counterparts for every cross-module data type in NIB-S sections 12 through 16.
Export those types under their exact accepted names. Do not duplicate those
thousands of lines in this brief.

Where a later active NIB-M owns a more specific internal serialized type,
provide its runtime validator only from that exact accepted type definition.
Do not make M0 the semantic owner of that type.

Treat service and module interfaces as TypeScript contracts. Do not give an
interface a serialized runtime validator merely because it is an interface.

## 5. Inputs and outputs

Consume only in-memory unknown values or already-valid immutable values supplied
by callers.

Export:

```text
exact NIB-S section 12-16 TypeScript declarations
Zod-backed runtime validators for runner-owned serialized forms
normalized ContractValidationResult values
CanonicalRunnerJsonBytesV1
deriveId
deriveReviewCampaignId
exact structural equality helpers selected by owning contracts
root-preflight definition constants
the exact CampaignArtifactStore TypeScript interface contract
validateExecutionReceiptV3
```

Perform no I/O while producing any output.

## 6. Runtime validation result

Expose exactly:

```ts
interface ContractValidationIssueV1 {
  readonly path: string;
  readonly code:
    | "TYPE"
    | "REQUIRED"
    | "UNEXPECTED-PROPERTY"
    | "FORMAT"
    | "ENUM"
    | "RANGE"
    | "DUPLICATE"
    | "ORDER"
    | "CROSS-FIELD"
    | "UNSUPPORTED-VERSION";
}

type ContractValidationResult<T> =
  | {
      readonly kind: "valid";
      readonly value: T;
    }
  | {
      readonly kind: "invalid";
      readonly issues: readonly ContractValidationIssueV1[];
    };
```

Represent `path` as an RFC 6901 JSON Pointer. Represent the root path as the
empty string:

```text
""
```

Escape `~` as `~0` and `/` as `~1` in a pointer token. Render an array index as
its canonical non-negative decimal index.

Never expose a Zod-native error, issue, schema, or parser result through the M0
public module boundary.

## 7. Validation issue normalization

Map validation failures exactly:

```text
missing required property
→ REQUIRED

wrong primitive/container type
→ TYPE

unknown property in closed object
→ UNEXPECTED-PROPERTY

regex/lexical/representation failure
→ FORMAT

invalid closed enum/literal choice
→ ENUM

invalid supported-version discriminator
→ UNSUPPORTED-VERSION

numeric bound failure
→ RANGE

duplicate member where uniqueness is required
→ DUPLICATE

canonical ordering violation
→ ORDER

exact multi-field consistency violation
→ CROSS-FIELD
```

For an unknown property, report the pointer to that property, not only the
pointer to its containing object.

Sort normalized issues by:

```text
RFC 6901 path, compared by UTF-8 unsigned bytes ascending
then issue code, compared by ASCII bytes ascending
```

Suppress duplicate identical `(path, code)` pairs. Return at least one issue for
every invalid result.

## 8. Runtime validation behavior

Use safe parsing for every untrusted runtime input. Never use exception-based
malformed-input control flow.

Make every runtime validator:

```text
deterministic
non-throwing merely because untrusted input is malformed
non-mutating
closed to unexpected object properties
non-coercing
non-defaulting
non-transforming
non-normalizing
non-repairing
```

Never:

```text
insert a default
delete or strip an unknown field
pass an unknown field through
coerce string ↔ number ↔ boolean
normalize Unicode
reorder a semantic array
repair an invalid structure
supply a catch/fallback value
```

For a closed M0 contract object:

```text
unexpected key
→ validation failure
```

Never implement:

```text
unexpected key
→ silently discarded
```

## 9. Zod usage discipline

Use Zod schemas as the runtime validator engine. Forbid behavior equivalent to:

```text
z.coerce.*
.default(...)
.catch(...)
.transform(...)
object passthrough
object strip semantics for closed contract objects
```

Use strict closed object validation. Use refinements or custom checks only to
implement exact representation constraints already fixed by NIB-S or an active
NIB-M. Do not invent a semantic rule in a refinement or custom check.

Apply the pipeline in this order whenever a pure canonical or ID helper requires
validated input:

```text
Zod-backed M0 runtime validation
→ validated exact runner-owned representation
→ pure M0 canonical/ID helper
```

Do not replace canonicalization or ID algorithms with Zod behavior.

## 10. Validator export naming

For each cross-module serialized data type `T` defined by NIB-S sections 12
through 16, export:

```text
validate<T>
```

with conceptual signature:

```ts
function validateT(
  value: unknown
): ContractValidationResult<T>;
```

Include at least:

```text
validateArtifactRef
validateRepositoryAuthorityRef
validateSemanticSubjectRef
validateProtocolBundleRef
validateCandidateRevisionRef
validateReviewCampaignRef
validateObligationRef
validateWorkItemRef
validateExecutionRef
validateWriteAuthorityRef
validateAuthoritativeMutationRef
validateExecutionReceiptV3
```

Also expose runtime validators for every module-internal serialized schema whose
active NIB-M explicitly assigns runtime validation to final M0 closure. Derive
each validator from its owning active NIB-M definition. Do not transfer shape or
semantic ownership to M0.

## 11. Opaque runner-ID validation

Validate every runner opaque ID as a string satisfying:

```text
non-empty
contains no NUL
contains no CR
contains no LF
```

Apply every stronger exact lexical contract fixed by accepted construction.
Do not require every runner-internal opaque ID to be SHA-derived.

Validate `GateARunId` exactly with:

```text
^RUN-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$
```

Validate `Sha256` exactly with:

```text
^[0-9a-f]{64}$
```

## 12. Canonical runner JSON value domain

Define `CanonicalRunnerJsonBytesV1(value)` over exactly:

```text
null
boolean
string
finite safe integer
array
plain JSON object
```

Accept a plain object only when its prototype is `Object.prototype` or `null`
and every own property is an enumerable string-keyed data property. Reject
symbol keys, non-enumerable own properties, accessors, and inherited data.

Reject:

```text
undefined
bigint
NaN
Infinity
-Infinity
non-integer number
negative zero
function
symbol
Date
Map
Set
typed array
class instance
other non-plain prototype object
cyclic graph
string containing an unpaired UTF-16 surrogate
```

Never invoke an accessor while inspecting an invalid value. Read only own data
properties. Reject sparse arrays because a missing element is not an accepted
value.

## 13. Canonical runner JSON serialization

Serialize recursively and purely.

Order object keys by exact UTF-8 unsigned-byte lexicographic order. Preserve
array order exactly. Never generic-sort an array.

Do not normalize Unicode. Emit every non-ASCII Unicode scalar directly as
UTF-8. Escape strings exactly as follows:

```text
quotation mark → \"
reverse solidus → \\
U+0008 → \b
U+0009 → \t
U+000A → \n
U+000C → \f
U+000D → \r
other U+0000 through U+001F → \u00xx with lowercase hexadecimal digits
```

Do not escape solidus. Reject unpaired UTF-16 surrogates before encoding.

Require every number to satisfy:

```text
Number.isSafeInteger(value) == true
Object.is(value, -0) == false
```

Render numbers in canonical base-10 JSON integer spelling with no leading plus,
no leading zero except `0`, no decimal point, and no exponent.

Emit no insignificant whitespace and no trailing newline. Return the exact
UTF-8 bytes. The same accepted value must produce byte-identical bytes.

## 14. Runner JSON is not semantic canonical JSON

Enforce:

```text
CanonicalRunnerJsonBytesV1
!=
protocol-v8 CanonicalJsonValueBytesV1 semantic identity authority
```

Use the runner serializer only for runner-owned construction artifacts and the
runner ID frame fixed by this brief.

Do not redefine the semantic canonicalization, `IdentityHashV1`, QLEK, FactId,
SemanticAdmissionId, or QualificationKey semantics closed by C2-C4 and
mechanically validated by M6. M0 may structurally and lexically validate their
representations only.

## 15. Runner ID hash frame

Define:

```text
RunnerIdHashV1(domain, components)
```

Require:

```text
domain = a non-empty ASCII string selected only from the closed registry
components = an ordered array of already-canonical strings
components.length >= 1
```

Compute exactly:

```text
lowercaseHex(
  SHA256(
    CanonicalRunnerJsonBytesV1(
      {
        "components": components,
        "domain": domain,
        "frame": "turnlock.runner-id-frame.v1"
      }
    )
  )
)
```

Use the exact frame:

```text
turnlock.runner-id-frame.v1
```

Forbid concatenation framing. Treat component array order as significant. Do
not let a caller supply an output prefix or dynamically invent a domain.

Render every registered deterministic runner ID as:

```text
registered prefix + uppercaseHex(RunnerIdHashV1 digest)
```

Require the rendered digest portion to contain exactly 64 hexadecimal
characters.

## 16. Complete runner ID domain registry

Use exactly these 19 current domains and prefixes:

```text
candidate-revision.v2
→ CANDIDATE-

assurance-repository-projection.v1
→ ASSURANCE-PROJECTION-

campaign-authority-current-review-authority-obligation.v1
→ OBLIGATION-

campaign-authority-reviewer-prerequisites-obligation.v1
→ OBLIGATION-

gate-a-operational-blocker-occurrence.v1
→ BLOCKER-

gate-a-recovery-operational-blocker.v1
→ BLOCKER-

gate-a-root-preflight-obligation.v1
→ OBLIGATION-

execution.v1
→ ATTEMPT-

publication-intent.v1
→ PUBLICATION-INTENT-

publication-obligation.v1
→ OBLIGATION-

publication-work-item.v1
→ WORK-

m4-cognitive-call.v1
→ CALL-

m4-provider-attempt.v1
→ PROVIDER-ATTEMPT-

assurance-ledger-reviewer-acquisition-target-obligation.v1
→ OBLIGATION-

assurance-ledger-selected-initial-reviewer-obligation.v1
→ OBLIGATION-

assurance-ledger-selected-initial-reviewer-work-item.v1
→ EXEC-

assurance-ledger-execution-receipt-evidence.v1
→ EVIDENCE-

assurance-ledger-execution-retry-authorization.v1
→ RETRY-AUTH-

review-campaign.v1
→ REVIEW-
```

Do not add a twentieth domain during C9-A. Extend the registry only through a
later accepted M0 synchronization that introduces another deterministic
runner-owned ID.

## 17. Domain types and generic deriveId API

Expose exactly:

```ts
type RunnerIdHashDomainV1 =
  | "candidate-revision.v2"
  | "assurance-repository-projection.v1"
  | "campaign-authority-current-review-authority-obligation.v1"
  | "campaign-authority-reviewer-prerequisites-obligation.v1"
  | "gate-a-operational-blocker-occurrence.v1"
  | "gate-a-recovery-operational-blocker.v1"
  | "gate-a-root-preflight-obligation.v1"
  | "execution.v1"
  | "publication-intent.v1"
  | "publication-obligation.v1"
  | "publication-work-item.v1"
  | "m4-cognitive-call.v1"
  | "m4-provider-attempt.v1"
  | "assurance-ledger-reviewer-acquisition-target-obligation.v1"
  | "assurance-ledger-selected-initial-reviewer-obligation.v1"
  | "assurance-ledger-selected-initial-reviewer-work-item.v1"
  | "assurance-ledger-execution-receipt-evidence.v1"
  | "assurance-ledger-execution-retry-authorization.v1"
  | "review-campaign.v1";

type GenericRunnerDerivedIdDomainV1 =
  Exclude<
    RunnerIdHashDomainV1,
    "review-campaign.v1"
  >;

function deriveId(
  domain: GenericRunnerDerivedIdDomainV1,
  ...components: readonly string[]
): string;
```

Reject `review-campaign.v1` at the generic TypeScript/API boundary. Validate the
runtime domain even when TypeScript has already checked the caller.

Require every component to be an exact canonical string selected by its owning
contract. Perform no implicit `String(value)` conversion, trimming, or Unicode
normalization.

Guarantee:

```text
same domain + same ordered components
→ same exact ID

different domain
→ different hash preimage

different ordered component vector
→ different hash preimage
```

## 18. Dedicated runner-produced ReviewCampaign identity

Expose exactly:

```ts
function deriveReviewCampaignId(
  domain: "review-campaign.v1",
  runId: GateARunId,
  semanticSubjectSelector: string,
  semanticSubjectSha256: Sha256,
  protocolId: string,
  protocolBundleSha256: Sha256
): ReviewCampaignId;
```

Use exactly this ordered component vector:

```text
[
  runId,
  semanticSubjectSelector,
  semanticSubjectSha256,
  protocolId,
  protocolBundleSha256
]
```

Compute exactly:

```text
digest =
RunnerIdHashV1(
  "review-campaign.v1",
  [
    runId,
    semanticSubjectSelector,
    semanticSubjectSha256,
    protocolId,
    protocolBundleSha256
  ]
)

ReviewCampaignId =
"REVIEW-" + uppercaseHex(digest)
```

Exclude all of the following from runner-created ReviewCampaign identity:

```text
candidateId
repositoryAuthority
repository commit
repository tree
StateRevision
timestamp
session identity
receipt identity
```

Treat `ReviewCampaignId` as the same logical identity as hostile-review
schema-5 `review_id`. Validate every `ReviewCampaignId`, whether runner-produced
or imported, with:

```text
^REVIEW-[A-Z0-9][A-Z0-9-]*$
```

Require `deriveReviewCampaignId(...)` to satisfy that lexical contract
mechanically.

For an imported campaign, validate the exact repository review record's
accepted `review_id`; never derive or replace it. Do not derive an imported
ReviewCampaignId from record SHA, record path, candidate, run, repository
commit, or repository tree.

## 19. M4 provider-attempt identity

Support exactly:

```text
providerAttemptId =
deriveId(
  "m4-provider-attempt.v1",
  callId,
  "1"
)
```

For the currently selected Pi M4 dependency realization, use exactly:

```text
[
  callId,
  "1"
]
```

Render exactly:

```text
"PROVIDER-ATTEMPT-" + uppercaseHex(
  RunnerIdHashV1(
    "m4-provider-attempt.v1",
    [
      callId,
      "1"
    ]
  )
)
```

Do not let M0 decide the provider-attempt ordinal. Treat the active Pi M4
Dependency Contract as authority for the selected-v1 rule that the only provider
attempt ordinal is exactly `1`. Provide only the deterministic domain-separated
renderer.

Keep `providerAttemptId` as operational/provider evidence. It is not:

```text
ExecutionId
WorkItemId
receipt execution_id
receipt attempt_id
SemanticAdmission identity
QLEK
```

Its existence or lexical validity does not establish that a provider request
occurred, a provider completed, a provider returned a response, a provider or
model identity was established, or a semantic completion exists. Leave those
facts to the Pi M4 execution/evidence contract.

## 20. M5-A hostile-review lexical compatibility

Require:

```text
deriveId(
  "assurance-ledger-selected-initial-reviewer-work-item.v1",
  exact obligationId
)
```

to render as:

```text
EXEC- + 64 uppercase hexadecimal characters
```

This rendering satisfies:

```text
^EXEC-[A-Z0-9][A-Z0-9-]*$
```

Therefore preserve its validity as the hostile-review logical execution and
`receipt.execution_id`. Do not modify M5-A identity inputs to obtain the lexical
shape.

## 21. GateARun occurrence identity

Enforce:

```text
GateARunId is NOT deriveId-derived.
```

Leave GateARunId generation to M2 exactly as:

```text
RUN-<lowercase UUIDv4>
```

Validate only its lexical form. Never generate a GateARunId in M0.

## 22. Runner deterministic ID collision behavior

When authoritative retained history exposes a deterministic runner-ID preimage,
require:

```text
same rendered deterministic runner ID
+
different domain/components preimage
→ RUNNER-ID-HASH-COLLISION
→ integrity failure
```

For ReviewCampaign identity, also require:

```text
same derived ReviewCampaignId
+
different exact runner-production identity preimage
→ RUNNER-ID-HASH-COLLISION
→ integrity failure
```

Preserve the stronger accepted domain rule:

```text
same ReviewCampaignId
+
incompatible immutable ReviewCampaign binding
→ integrity failure
```

Never select first or last, merge, duplicate the campaign, retry the hash, or
create a random replacement ID. Define the pure preimage comparison rule in M0.
Leave retained authoritative-history writing and collision establishment to M2.
Do not conflate `RUNNER-ID-HASH-COLLISION` with P8 semantic
`IDENTITY-HASH-COLLISION`.

## 23. Root-preflight obligation definition

Expose exactly:

```ts
interface GateARootPreflightObligationDefinitionV1 {
  readonly schema:
    "gate-a-root-preflight-obligation-definition.v1";

  readonly kind:
    "root-preflight";
}
```

Use the exact value:

```json
{
  "schema": "gate-a-root-preflight-obligation-definition.v1",
  "kind": "root-preflight"
}
```

Use these exact canonical runner JSON bytes as UTF-8 text:

```text
{"kind":"root-preflight","schema":"gate-a-root-preflight-obligation-definition.v1"}
```

Require:

```text
byte length = 83
SHA-256 = 595cd152405f868a67fc9dce8b00767700c2273777873c944a7596f1d382be3b
```

Use exactly this meaning:

```text
establish the initial exact repository/preflight authority required before
ordinary Gate A campaign progression for one GateARun
```

Include none of the following in definition identity:

```text
runId
candidateId
ReviewCampaignId
StateRevision
session identity
timestamp
repository path
S
P
mutable repository observation
```

Treat those as occurrence or binding facts.

## 24. Root-preflight exports and integration

Export pure constants:

```ts
const ROOT_PREFLIGHT_OBLIGATION_DEFINITION_V1:
  GateARootPreflightObligationDefinitionV1;

const ROOT_PREFLIGHT_OBLIGATION_DEFINITION_BYTES_V1:
  Uint8Array;

const ROOT_PREFLIGHT_OBLIGATION_DEFINITION_SHA256_V1:
  "595cd152405f868a67fc9dce8b00767700c2273777873c944a7596f1d382be3b";
```

Keep their values immutable by contract. Do not expose any internal buffer that
M0 later mutates.

Perform no artifact-store I/O. Require a later M1/composition synchronization to
seal these exact bytes mechanically through the existing
`CampaignArtifactStore` and supply the resulting exact `ArtifactRef` to M2
bootstrap.

Do not return or fabricate an `ArtifactRef` in M0.

## 25. Protocol-v8 semantic identity structural mirror

Declare exact structural TypeScript mirrors of
`formal/reviews/schemas/semantic-identity-v1.schema.json`:

```ts
type SemanticQuestionContractRevisionId = string;
type SemanticValueTypeRevisionId = string;
type SemanticValueId = string;
type QLEK = string;
type SemanticAdmissionId = string;
type PredicateRevisionId = string;
type FactId = string;
type QualificationContractRevisionId = string;
type QualificationKey = string;

type CanonicalSemanticJsonValueV1 =
  | null
  | boolean
  | number
  | string
  | readonly CanonicalSemanticJsonValueV1[]
  | {
      readonly [key: string]:
        CanonicalSemanticJsonValueV1;
    };

interface SemanticValueRefV1 {
  readonly kind: "semantic-value";
  readonly valueType: SemanticValueTypeRevisionId;
  readonly valueId: SemanticValueId;
}

interface SemanticAdmissionRefV1 {
  readonly kind: "semantic-admission";
  readonly admissionId: SemanticAdmissionId;
}

interface SemanticFactRefV1 {
  readonly kind: "semantic-fact";
  readonly predicateRevision: PredicateRevisionId;
  readonly factId: FactId;
}

interface ExactAuthorityRefV1 {
  readonly kind: "exact-authority";
  readonly authorityType: string;
  readonly authorityId: string;
}

interface QualificationKeyRefV1 {
  readonly kind: "qualification-key";
  readonly qualificationContract:
    QualificationContractRevisionId;
  readonly qualificationKey: QualificationKey;
}

interface LogicalQuestionDescriptorV1 {
  readonly schema:
    "turnlock.logical-question-descriptor.v1";
  readonly semanticQuestionContract:
    SemanticQuestionContractRevisionId;
  readonly exactLogicalInput:
    Readonly<Record<string, CanonicalSemanticJsonValueV1>>;
}
```

Add no fields. Validate every object above as a strict closed object with every
published required field present. Require non-empty `authorityType` and
`authorityId` in `ExactAuthorityRefV1`; require `exactLogicalInput` to be an
object whose values are valid `CanonicalSemanticJsonValueV1` values. Apply no
semantic interpretation while checking these constraints.

## 26. Protocol-v8 semantic lexical validation

Validate exact published patterns:

```text
SemanticQuestionContractRevisionId
^turnlock\.sqc:[A-Za-z][A-Za-z0-9]*@[1-9][0-9]*$

SemanticValueTypeRevisionId
^turnlock\.semantic-value:[A-Za-z][A-Za-z0-9]*@[1-9][0-9]*$

SemanticValueId
^semantic-value-sha256:[0-9a-f]{64}$

QLEK
^qlek-sha256:[0-9a-f]{64}$

SemanticAdmissionId
^semantic-admission-sha256:[0-9a-f]{64}$

PredicateRevisionId
^turnlock\.predicate:[A-Za-z][A-Za-z0-9]*@[1-9][0-9]*$

FactId
^semantic-fact-sha256:[0-9a-f]{64}$

QualificationContractRevisionId
^turnlock\.qualification:[A-Za-z][A-Za-z0-9]*@[1-9][0-9]*$

QualificationKey
^qualification-key-sha256:[0-9a-f]{64}$
```

Validate syntax only. Do not establish that a referenced semantic object exists,
is reconstructible, is current, is consumable, or is semantically valid. Leave
those responsibilities to M2, M5, and M6 according to NIB-S 11.0.0.

## 27. Canonical semantic JSON and binding mirrors

For values used in published P8 semantic identity representation, validate the
schema-level `canonicalJsonValue` domain exactly:

```text
null
boolean
integer
string
array recursively containing valid values
object recursively containing valid values
```

Reject fractional numbers, `NaN`, infinity, `undefined`, bigint as a JSON
runtime value, functions, symbols, and cyclic data. Do not silently normalize
arrays, object values, Unicode, or numeric meaning. Do not compute semantic
identity.

Declare exactly:

```ts
interface SemanticQuestionBindingSemanticValueV1 {
  readonly ref: SemanticValueRefV1;
  readonly value: CanonicalSemanticJsonValueV1;
}

interface SemanticQuestionBindingV1 {
  readonly semantic_question_binding_schema_version:
    "1.0";

  readonly logical_question_descriptor:
    LogicalQuestionDescriptorV1;

  readonly qlek:
    QLEK;

  readonly semantic_values:
    readonly SemanticQuestionBindingSemanticValueV1[];
}
```

Mirror `semantic-question-binding-v1.schema.json` structurally only. Leave to M6:

```text
descriptor ↔ QLEK recomputation
semantic ref ↔ exact resolved value
complete transitive semantic binding
```

## 28. Selected M0 support dependency

Consume exactly:

```text
Node.js standard runtime
+
zod@4.6.7
```

Pin the future package manifest exactly as:

```json
"zod": "4.6.7"
```

Forbid:

```text
^4.6.7
~4.6.7
>=4.6.7
4.x
latest
*
```

The selected M0 external support dependency count is exactly one. Select no
other non-trivial external runtime dependency in C9-A.

Use `zod@4.6.7` only for:

```text
runtime validation of runner-owned serialized internal structures
runtime validation of runner-owned CLI structures
runtime structural/lexical validation of M0's exact runner-side mirrors of
published P8 identity/reference forms
runtime structural validation of M0's exact runner-side mirror of published
execution-receipt schema v3
```

Do not make Zod authority for:

```text
hostile-review protocol validity
protocol bundle validity
review evidence validity
SemanticAdmission existence
SemanticAdmission consumability
SemanticFact truth
FactId semantic reconstruction
QLEK semantic reconstruction
qualification truth
CandidateView truth
current S
current P
```

Leave those responsibilities with their existing accepted
schema/Python/M2/M5/M6 authorities.

Require a later Dependency Contract named exactly:

```text
DC-ZOD-GATE-A-CONTRACTS
```

before GREEN closes the exact consumed Zod interface and error behavior. This
later contract is required because M0 consumes behavior from an external
validation library even though M0 exposes only its own stable result boundary.
Do not create that Dependency Contract in C9-A. This later contract does not
promote Zod into semantic or protocol authority and does not expose Zod-native
values through M0.

## 29. Zod authority exclusion

Enforce:

```text
Zod success proves only that a runner-owned value satisfies the exact M0
representation contract being checked.

Zod success does NOT prove protocol semantic validity, currentness,
reconstructibility, qualification or semantic authority.
```

For published protocol-owned artifacts, retain existing content-addressed JSON
Schema/Python validation as authority.

Do not translate published protocol schemas into Zod and then treat the Zod
result as equivalent protocol authority.

### 29.1 Execution-receipt schema-v3 structural runtime contract

Expose these strict runner-side structural TypeScript mirrors and exact
validator:

```ts
interface ExecutionReceiptV3ArtifactReference {
  readonly path: string;
  readonly sha256: Sha256;
}

type ExecutionReceiptV3Role =
  | "initial-reviewer"
  | "materiality-assessor"
  | "refutation-builder"
  | "challenge"
  | "discovery-classifier"
  | "derivation-builder"
  | "decision-necessity-challenger"
  | "repair-synthesizer"
  | "decision-projection";

type ExecutionReceiptV3AttemptOutcome =
  | "technical-failure"
  | "protocol-invalid"
  | "qualified";

interface ExecutionReceiptV3Attempt {
  readonly attempt_id: string;
  readonly call_id: string;
  readonly outcome: ExecutionReceiptV3AttemptOutcome;
  readonly started_at: string;
  readonly ended_at: string;
  readonly provider_model: string | null;
  readonly provider_response_id: string | null;
  readonly termination: string | null;
  readonly transport_attempt_count: number;
  readonly raw_output:
    ExecutionReceiptV3ArtifactReference | null;
  readonly protocol_errors: readonly string[];
}

interface ExecutionReceiptV3ResolvedIdentity {
  readonly provider: string;
  readonly model: string;
  readonly model_version: string;
  readonly resolution_kind:
    | "provider-reported"
    | "pinned-request-model";
  readonly evidence_attempt_id: string;
}

interface ExecutionReceiptV3 {
  readonly receipt_schema_version: "3.0";
  readonly execution_id: string;
  readonly role: ExecutionReceiptV3Role;
  readonly reviewer_profile_id: string;
  readonly protocol_bundle_sha256: Sha256;
  readonly input: {
    readonly prompt: ExecutionReceiptV3ArtifactReference;
    readonly packet: ExecutionReceiptV3ArtifactReference;
  };
  readonly isolated_context: true;
  readonly cross_reviewer_visibility_before_seal: false;
  readonly tools_enabled: false;
  readonly runtime: {
    readonly name: string;
    readonly version: string;
  };
  readonly request: {
    readonly provider: string;
    readonly model: string;
  };
  readonly attempts: readonly ExecutionReceiptV3Attempt[];
  readonly qualifying_attempt_id: string;
  readonly resolved_identity: ExecutionReceiptV3ResolvedIdentity;
}

function validateExecutionReceiptV3(
  value: unknown
): ContractValidationResult<ExecutionReceiptV3>;
```

Bind the mirror and validator to exactly this published immutable schema:

```text
path:
formal/reviews/schemas/execution-receipt-v3.schema.json

SHA-256:
7432767a0714324214bafe3f79856ac4ea34badd21c3a0a97ee70e4bc1865d72

$id:
urn:fanilosendrison:turnlock-rust:hostile-review-execution-receipt:3

receipt_schema_version:
3.0
```

Mirror every required field, closed-object boundary, primitive/container type,
constant, enum, pattern, minimum, `minItems`, and conditional relation in that
exact schema. In particular, enforce structurally:

```text
receipt, input, runtime, request, resolved_identity, attempt and artifact
reference objects reject unknown properties

attempts contains at least one attempt
transport_attempt_count is an integer >= 1
artifact-reference path is non-empty
artifact-reference sha256 is exactly 64 lowercase hexadecimal characters

outcome == technical-failure
→ protocol_errors is empty
→ raw_output is null

outcome == protocol-invalid
→ protocol_errors contains at least one non-empty string
→ raw_output is an exact artifact reference

outcome == qualified
→ protocol_errors is empty
→ raw_output is an exact artifact reference

for each exact role restricted by the schema-v3 top-level conditional:
    materiality-assessor
    refutation-builder
    discovery-classifier
    derivation-builder
    decision-necessity-challenger
    repair-synthesizer
    decision-projection
→ attempt outcome is technical-failure or qualified
```

Preserve the exact schema-v3 role set, including historical
`decision-projection`; do not substitute `ProtocolV8CognitiveExecutionRole` for
the schema-v3 role contract.

Implement this validator as a statically constructed strict Zod mirror. Perform
no runtime file read, schema loading, Python invocation, repository access, or
protocol-bundle lookup. A change to the bound schema path or SHA requires a
later explicit M0 synchronization; do not dynamically accept another receipt
schema version.

Require M5-A to call `validateExecutionReceiptV3` after constructing the exact
schema-v3 receipt and before canonical serialization or sealing. On an invalid
result, fail closed through the owning M5-A implementation/integrity failure
boundary. Produce no sealed receipt, receipt `ArtifactRef`, or receipt
`EvidenceRef` from the invalid value.

This validator establishes structural runtime validity only. It does not:

```text
establish hostile-review protocol validity
classify an attempt as protocol-invalid or qualified
prove attempt completeness, currentness, or admissibility
establish model identity
establish review evidence
replace M5-A's exact receipt-construction bindings
replace M6 classification
replace the content-addressed JSON Schema or Python validator
```

Keep the published content-addressed JSON Schema, existing Python validation,
and M6 mechanical/protocol classification authoritative. Zod success is only a
pre-sealing fail-closed construction guard for the runner-owned in-memory value.

## 30. Protocol-v8 cognitive role

Expose exactly:

```ts
type ProtocolV8CognitiveExecutionRole =
  | "initial-reviewer"
  | "materiality-assessor"
  | "refutation-builder"
  | "challenge"
  | "discovery-classifier"
  | "derivation-builder"
  | "decision-necessity-challenger"
  | "repair-synthesizer";
```

Reject `decision-projection` in the P8-role validator.

Preserve the broader historical/current `CognitiveExecutionRole` contract from
NIB-S for protocol versions that lawfully contain `decision-projection`. Do not
collapse the two types.

## 31. ArtifactRef validation

Validate the exact NIB-S `ArtifactRef` structure and at least:

```text
artifactId:
non-empty string

sha256:
64 lowercase hexadecimal characters

byteLength:
safe integer >= 0

mediaType:
non-empty string

repositoryPath:
null or non-empty string
```

Do not verify bytes or read paths. Leave artifact existence and integrity to the
owning module, `CampaignArtifactStore`, and M6.

### 31.1 CampaignArtifactStore TypeScript contract

Expose or re-export exactly this TypeScript interface under the exact accepted
name:

```ts
interface CampaignArtifactStore {
  sealRunnerArtifact(input: {
    readonly bytes: Uint8Array;
    readonly mediaType: string;
  }): Promise<ArtifactRef>;

  ingestReferencedArtifact(input: {
    readonly ref: ArtifactRef;
    readonly bytes: Uint8Array;
  }): Promise<void>;

  readVerified(ref: ArtifactRef): Promise<Uint8Array>;

  verify(ref: ArtifactRef): Promise<void>;
}
```

Treat
`NIB-M-GATE-A-CAMPAIGN-STATE-PERSISTENCE-OWNERSHIP` section 6 as the exact
shape and behavior owner. Do not add, remove, rename, widen, narrow, default, or
reinterpret a method, parameter, return value, or effect.

M0 owns only the shared TypeScript declaration surface. Do not give this service
interface a serialized runtime validator. M2 owns and provides the effectful
implementation, immutable artifact durability, byte verification, CAS behavior,
and every implementation/dependency failure. Inject the M2-provided
implementation into M5-A and other consuming modules through this exact M0
contract.

Do not instantiate, wrap, call, implement, persist through, or perform I/O
through `CampaignArtifactStore` in M0. Exporting the interface grants no
artifact authority and no authoritative-state write access.

## 32. Revision and generation validation

Validate `StateRevision` as a canonical non-negative decimal string:

```text
allowed:
"0"
"1"
"2"
...

forbidden:
"00"
"01"
"+1"
"-0"
"-1"
whitespace
decimal point
exponent
```

Validate `OwnershipGeneration` with:

```text
Number.isSafeInteger(value)
value >= 1
```

Do not decide whether a supplied revision or generation is current.

## 33. Pure exact equality

Expose exact structural equality helpers only where an owning contract requires
comparison of already-valid runner-owned values.

Define equality as:

```text
same accepted fields
same primitive values
same array length/order/content
same nested object values
```

Perform no:

```text
Unicode normalization
set conversion unless the owning contract first defines set canonicalization
path normalization
case folding
semantic alias resolution
repository-byte equivalence
```

Do not use these helpers to establish protocol semantic equality.

## 34. Error taxonomy

Use exactly these M0-local failure classes:

```text
CONTRACT-VALIDATION-FAILURE
CANONICAL-RUNNER-JSON-FAILURE
UNKNOWN-RUNNER-ID-DOMAIN
INVALID-RUNNER-ID-COMPONENT
```

Treat hash primitive failure as an implementation/process failure.

Use `RUNNER-ID-HASH-COLLISION` only for the retained-preimage collision
condition in section 22.

Do not convert an M0 failure into an `OperationalBlocker`, Decision Request,
`SemanticBlocker`, retry authorization, or alternate protocol meaning. Require
owning callers to map M0 failures under their accepted NIB-M contracts.

## 35. Algorithms

Implement validator entry points as:

```text
validateT(value):
    result = exact strict Zod schema for T.safeParse(value)

    if result succeeds:
        return {
            kind: "valid",
            value: exact validated representation
        }

    normalized = map every applicable failure to exact public issue form
    expand unknown-key failures to one issue per exact unknown-property pointer
    suppress duplicate (path, code)
    sort by pointer UTF-8 unsigned bytes, then code ASCII bytes

    require normalized is non-empty

    return {
        kind: "invalid",
        issues: normalized
    }
```

Implement canonical runner JSON as:

```text
CanonicalRunnerJsonBytesV1(value):
    validate accepted graph, prototypes, data properties, scalar domain,
        paired surrogates, safe integers, no negative zero and no cycles

    recursively emit one canonical JSON token stream:
        null/boolean → exact JSON literal
        safe integer → canonical decimal spelling
        string → exact escaping from section 13
        array → supplied order with comma separators
        object → UTF-8 unsigned-byte sorted own keys with comma separators

    UTF-8 encode exact emitted scalar stream
    return bytes without trailing newline
```

Implement ID rendering as:

```text
RunnerIdHashV1(domain, components):
    require exact registered domain
    require non-empty ordered component vector
    require every component is a string already canonical under its owner

    bytes = CanonicalRunnerJsonBytesV1({
        components,
        domain,
        frame: "turnlock.runner-id-frame.v1"
    })

    return lowercaseHex(SHA256(bytes))

renderRegisteredId(domain, components):
    return exactPrefix(domain) + uppercaseHex(
        RunnerIdHashV1(domain, components)
    )
```

Keep `renderRegisteredId` private if no caller needs it. Expose only `deriveId`
and `deriveReviewCampaignId` as public ID helpers.

## 36. Concrete examples and test vectors

### 36.1 Root-preflight canonicalization

Given:

```json
{
  "schema": "gate-a-root-preflight-obligation-definition.v1",
  "kind": "root-preflight"
}
```

Sort keys as `kind`, then `schema`, and emit:

```text
{"kind":"root-preflight","schema":"gate-a-root-preflight-obligation-definition.v1"}
```

Require exactly 83 UTF-8 bytes and SHA-256:

```text
595cd152405f868a67fc9dce8b00767700c2273777873c944a7596f1d382be3b
```

### 36.2 Closed-object validation

Given an otherwise valid `ArtifactRef` with an additional `size` property,
return `kind = "invalid"` and include exactly:

```text
path = "/size"
code = "UNEXPECTED-PROPERTY"
```

Do not return a valid value with `size` stripped.

### 36.3 Provider-attempt framing

Given a valid `callId`, frame the preimage exactly as:

```json
{
  "components": ["<exact-call-id>", "1"],
  "domain": "m4-provider-attempt.v1",
  "frame": "turnlock.runner-id-frame.v1"
}
```

Canonicalize object keys as `components`, `domain`, `frame`, hash the exact
canonical bytes, uppercase the 64-character digest, and prepend exactly:

```text
PROVIDER-ATTEMPT-
```

Do not infer from the rendered ID that a provider request occurred.

### 36.4 ReviewCampaign framing

Given exact validated `(runId, S, P)`, pass only:

```text
runId
S.selector
S.sha256
P.protocolId
P.sha256
```

in that order to `RunnerIdHashV1("review-campaign.v1", ...)`, then prepend
`REVIEW-`. Do not add candidate, repository, revision, time, session, or receipt
inputs.

## 37. Construction classifications

Record the deterministic runner-ID construction choice as:

```text
statement:
the accepted NIB-S, active NIB-M set and active Pi M4 Dependency Contract
require one exact collision-safe domain-separated runner identity framing for
all currently selected deterministic runner-owned IDs, including the dedicated
runner-produced ReviewCampaign identity and M4 provider-attempt identity; C9-A
closes one canonical-runner-JSON framed SHA-256 construction with an exact
19-domain registry and dedicated deriveReviewCampaignId rendering compatible
with the hostile-review review_id lexical contract

semantic disposition:
no-normative-impact

affected layer:
architecture-or-implementation

normative impact:
none
```

Record the root-preflight construction choice as:

```text
statement:
M2 bootstrap requires one exact immutable root-preflight obligation definition
and prior construction explicitly assigns that constant to M0 final closure;
C9-A fixes its two-field runner-owned representation and canonical bytes

semantic disposition:
no-normative-impact

affected layer:
architecture-or-implementation

normative impact:
none
```

Record the selected validation dependency as:

```text
statement:
NIB-S 11.0.0 fixes zod as the M0 runtime-validation support dependency and
delegates its exact package pin to M0 NIB-M/package construction; C9-A pins the
selected dependency to zod@4.6.7 and keeps all consumed validation behavior
behind the exact M0 ContractValidationResult boundary

semantic disposition:
no-normative-impact

affected layer:
architecture-or-implementation

normative impact:
none
```

Treat none of these choices as a modification to TURNLOCK or hostile-review
semantics.

## 38. M0 invariants

```text
M0-01
M0 performs no I/O.

M0-02
M0 performs no authoritative state mutation.

M0-03
M0 never decides protocol or semantic meaning.

M0-04
Runtime validation is deterministic, non-mutating and non-coercing.

M0-05
CanonicalRunnerJsonBytesV1 is deterministic and has one byte representation for
one accepted runner-owned JSON value.

M0-06
Canonical runner JSON never Unicode-normalizes strings.

M0-07
Canonical runner JSON never reorders arrays.

M0-08
deriveId uses exactly turnlock.runner-id-frame.v1 and the closed domain registry.

M0-09
Caller-controlled prefix/domain invention is forbidden.

M0-10
GateARunId is UUIDv4 occurrence identity and is not deriveId-derived.

M0-11
The selected M5-A initial-reviewer WorkItem domain renders ^EXEC-[A-Z0-9-]+$
and preserves hostile-review receipt execution-id compatibility.

M0-12
M0 P8 semantic identity representations are structural mirrors of published
immutable schemas and do not create semantic authority.

M0-13
decision-projection is rejected as ProtocolV8CognitiveExecutionRole.

M0-14
Historical broad CognitiveExecutionRole compatibility is preserved.

M0-15
Root preflight definition canonical bytes and SHA are immutable constants.

M0-16
M0 never fabricates ArtifactRef authority for its root-preflight bytes.

M0-17
Unknown fields in closed serialized contract shapes fail validation rather than
being ignored.

M0-18
Runtime validators never repair malformed input.

M0-19
Runner deterministic ID collisions fail closed.

M0-20
M0 consumes exactly zod@4.6.7 as its construction-selected TypeScript runtime
validation support dependency, selects no other non-trivial external runtime
dependency, and requires the later DC-ZOD-GATE-A-CONTRACTS before GREEN.

M0-21
No Zod-native error, schema object, parser result, transform, default or
coercion crosses the M0 public contract boundary.

M0-22
Zod validation establishes representation validity only and never promotes a
runner-side value into protocol, semantic, qualification or currentness
authority.

M0-23
M0 exposes the exact CampaignArtifactStore TypeScript interface contract but
performs none of its I/O; M2 remains the sole owner and provider of its effectful
implementation.

M0-24
validateExecutionReceiptV3 fail-closes malformed in-memory receipt structures
before M5-A sealing, but Zod validation never replaces the published
content-addressed schema, Python validation or M6 protocol authority.

M0-25
Runner-produced ReviewCampaignId uses only the exact NIB-S
(runId, S, P) logical slot and renders through REVIEW- plus the exact
review-campaign.v1 RunnerIdHashV1 digest.

M0-26
Every ReviewCampaignId accepted by M0 satisfies the hostile-review
^REVIEW-[A-Z0-9][A-Z0-9-]*$ lexical contract; imported review IDs are validated
but never rederived.

M0-27
m4-provider-attempt.v1 is a registered generic deriveId domain and renders as
PROVIDER-ATTEMPT- plus its exact RunnerIdHashV1 digest.

M0-28
M0 provider-attempt identity rendering creates no execution, transport,
provider, model or semantic truth.
```

## 39. Forbidden behavior

Do not let M0:

```text
read current P
read current S
load protocol files
read repository state
invoke the Python checker
resolve SemanticAdmissionRef
resolve SemanticFactRef
recompute QLEK as semantic authority
derive FactId semantic truth
run qualification reducers
construct CandidateView
construct WorkItems
construct Executions
acquire AdmissionAuthority
perform Semantic Arm
write M2 state
perform M4 execution
perform M5 qualification
instantiate, implement or invoke CampaignArtifactStore
classify execution-receipt protocol validity or evidence authority
perform M6 repository validation
perform M7 materialization
perform M8 recovery
normalize repository paths for semantic identity
use receipt ownership as semantic identity
add decision-projection to P8
activate P8
```

Also forbid Zod from validating protocol authority, coercing runtime contract
values, inserting defaults, transforming values, passing through unknown
fields, or stripping unknown fields.

## 40. Explicit C9-A exclusions

Do not synchronize existing NIB-M dependency versions to NIB-S 11.0.0 during
C9-A. Leave that work to later C9 sub-stages.

Create no:

```text
package.json
package-lock.json
pnpm-lock.yaml
yarn.lock
Dependency Contract
M1 brief
M2 changes
M3 changes
M4 changes
M5-B/C/D
M6 brief
M7-B brief
M8 changes
NIB-T
formal model
production implementation
```

Do not modify the Pi M4 Dependency Contract, NIB-S, another active NIB-M, formal
artifacts, scripts, tests, or repository governance.

## 41. Construction completion contract

Treat M0 construction as decision-complete only when a later implementation
agent can determine without discretion:

```text
what M0 owns
what M0 cannot own
which cross-module shapes it implements
how runtime validation behaves
how validation errors are represented
that Zod is mandatory
that the exact Zod version is 4.6.7
which M0 values Zod validates
which values remain under protocol/Python authority
that malformed runtime input uses safe validation
that coercion/default/transform/passthrough behavior is forbidden
how Zod errors become ContractValidationIssueV1
why Zod creates no semantic authority
why DC-ZOD-GATE-A-CONTRACTS is required later but is not created by C9-A
how runner canonical JSON is serialized
how deterministic ID bytes are framed
which 19 current deterministic ID domains exist
how every current domain renders
how runner-produced ReviewCampaignId is framed
why ReviewCampaign identity uses a dedicated API
which exact five ReviewCampaign components participate
how REVIEW- rendering works
how every ReviewCampaignId is lexically validated
why imported ReviewCampaignIds are never rederived
how m4-provider-attempt.v1 is framed
how PROVIDER-ATTEMPT- rendering works
why provider-attempt identity creates no provider/execution truth
how M5-A WorkItem IDs remain hostile-review compatible
how GateARunId is validated
what the root-preflight definition bytes are
how P8 semantic reference forms are represented
which P8 identity lexical forms are valid
why structural validation does not establish semantic authority
that M0 exposes the exact CampaignArtifactStore TypeScript contract
that M2 alone owns and provides CampaignArtifactStore's effectful implementation
that M0 performs no CampaignArtifactStore I/O
which exact immutable execution-receipt v3 schema the runtime validator mirrors
how validateExecutionReceiptV3 fail-closes before M5-A serialization and sealing
which exact schema-v3 structural and conditional constraints it enforces
why receipt-v3 Zod success creates no hostile-review or evidence authority
why schema/Python/M6 authority remains unchanged
```

Sections 1 through 41 retain the complete prior C9-A.1 contract. C9-B adds only
the protocol-v8 M2 representation and validation surface in sections 42 through
49.

## 42. C9-B protocol-v8 M2 contract synchronization

Expose the exact cross-module representations in sections 43 through 49. M0
owns their TypeScript declaration and strict runtime representation validation
only. M2 owns authoritative persistence and transition behavior; M6 owns every
mechanical protocol/semantic validation identified below.

The exact 19-domain `deriveId` registry remains unchanged. C9-B introduces no
new deterministic runner-ID domain.

## 43. Semantic authority, execution, and validation types

Expose:

```ts
type SemanticAuthorityDomainId = string;
type SemanticCoordinationEpoch = number;
type AdmissionAuthorityGeneration = number;

interface AdmissionAuthorityRefV1 {
  readonly schema:
    "gate-a-admission-authority.v1";
  readonly domainId:
    SemanticAuthorityDomainId;
  readonly qlek:
    QLEK;
  readonly epoch:
    SemanticCoordinationEpoch;
  readonly generation:
    AdmissionAuthorityGeneration;
  readonly sessionId:
    RunnerSessionId;
}

interface SemanticExecutionLocatorV1 {
  readonly runId: GateARunId;
  readonly workItemId: WorkItemId;
  readonly executionId: ExecutionId;
}

interface ValidatedSemanticQuestionRefV1 {
  readonly schema:
    "gate-a-validated-semantic-question.v1";
  readonly qlek:
    QLEK;
  readonly semanticQuestionBinding:
    ArtifactRef;
  readonly boundCandidateRevisionId:
    CandidateRevisionId | null;
  readonly validationEvidence:
    readonly ArtifactRef[];
}

interface SemanticExecutionBindingRefV1 {
  readonly schema:
    "gate-a-semantic-execution-binding.v1";
  readonly execution:
    SemanticExecutionLocatorV1;
  readonly qlek:
    QLEK;
  readonly boundCandidateRevisionId:
    CandidateRevisionId | null;
  readonly semanticQuestionBinding:
    ArtifactRef;
  readonly validationEvidence:
    readonly ArtifactRef[];
}

interface SemanticArmBindingRefV1 {
  readonly schema:
    "gate-a-semantic-arm-binding.v1";
  readonly execution:
    SemanticExecutionLocatorV1;
  readonly qlek:
    QLEK;
  readonly domainId:
    SemanticAuthorityDomainId;
  readonly epoch:
    SemanticCoordinationEpoch;
  readonly generation:
    AdmissionAuthorityGeneration;
}
```

Validate `SemanticAuthorityDomainId` exactly as:

```text
^SEM-DOMAIN-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$
```

Treat it as operational provenance, never semantic identity and never a QLEK
input. Validate both counter types with:

```text
Number.isSafeInteger(value)
value >= 1
```

Never wrap either counter. Treat a value beyond `Number.MAX_SAFE_INTEGER` as
implementation/integrity capacity exhaustion.

Require `ValidatedSemanticQuestionRefV1.validationEvidence` and
`SemanticExecutionBindingRefV1.validationEvidence` to be non-empty and
duplicate-free by exact `ArtifactRef` equality. Interpret a null
`boundCandidateRevisionId` as candidate-independent authorization metadata and a
non-null value as the exact C5 mechanically validated bound candidate. Never
add this metadata as another QLEK input. Do not add authority generation to
`SemanticExecutionBindingRefV1`.

Expose:

```ts
type ProtocolV8SemanticValidationResultV1 =
  | {
      readonly schema:
        "gate-a-protocol-v8-semantic-validation.v1";
      readonly classification:
        "protocol-valid";
      readonly execution:
        SemanticExecutionLocatorV1;
      readonly qlek:
        QLEK;
      readonly semanticAdmissionId:
        SemanticAdmissionId;
      readonly semanticCandidate:
        ArtifactRef;
      readonly semanticQuestionBinding:
        ArtifactRef;
      readonly executionReceipt:
        ArtifactRef;
      readonly originWitness:
        ArtifactRef;
      readonly protocolErrors:
        readonly [];
      readonly validationEvidence:
        readonly ArtifactRef[];
    }
  | {
      readonly schema:
        "gate-a-protocol-v8-semantic-validation.v1";
      readonly classification:
        "protocol-invalid";
      readonly execution:
        SemanticExecutionLocatorV1;
      readonly qlek:
        QLEK;
      readonly protocolErrors:
        readonly [string, ...string[]];
      readonly validationEvidence:
        readonly ArtifactRef[];
    };

type ProtocolV8ProtocolValidSemanticCompletionRefV1 =
  Extract<
    ProtocolV8SemanticValidationResultV1,
    { readonly classification: "protocol-valid" }
  >;

type ProtocolV8ProtocolInvalidSemanticCompletionRefV1 =
  Extract<
    ProtocolV8SemanticValidationResultV1,
    { readonly classification: "protocol-invalid" }
  >;
```

Require validation evidence to be non-empty and duplicate-free. M0 validates
only these closed representations.

## 44. Admission, hazard, and derived-state types

Expose:

```ts
interface SemanticAdmissionRecordV1 {
  readonly schema:
    "gate-a-semantic-admission.v1";
  readonly qlek:
    QLEK;
  readonly admissionId:
    SemanticAdmissionId;
  readonly semanticCandidate:
    ArtifactRef;
  readonly semanticQuestionBinding:
    ArtifactRef;
}

interface SemanticAdmissionWitnessRefV1 {
  readonly qlek:
    QLEK;
  readonly admissionId:
    SemanticAdmissionId;
  readonly sourceDomainId:
    SemanticAuthorityDomainId;
  readonly originExecutionId:
    ExecutionId;
  readonly witness:
    ArtifactRef;
}

interface SemanticAdmissionConflictRefV1 {
  readonly qlek:
    QLEK;
  readonly admissionA:
    SemanticAdmissionRecordV1;
  readonly admissionB:
    SemanticAdmissionRecordV1;
}

type SemanticSamplingHazardRefV1 =
  | {
      readonly kind:
        "local-armed-execution";
      readonly qlek:
        QLEK;
      readonly execution:
        SemanticExecutionLocatorV1;
      readonly arm:
        SemanticArmBindingRefV1;
    }
  | {
      readonly kind:
        "external-armed-execution";
      readonly qlek:
        QLEK;
      readonly sourceDomainId:
        SemanticAuthorityDomainId;
      readonly sourceExecution:
        SemanticExecutionLocatorV1;
      readonly sourceEpoch:
        SemanticCoordinationEpoch;
      readonly sourceGeneration:
        AdmissionAuthorityGeneration;
      readonly evidence:
        readonly ArtifactRef[];
    };

interface ExternalSemanticHazardClearanceRefV1 {
  readonly sourceDomainId:
    SemanticAuthorityDomainId;
  readonly sourceExecution:
    SemanticExecutionLocatorV1;
  readonly qlek:
    QLEK;
  readonly kind:
    | "proven-not-executed"
    | "terminal-technical-no-completion"
    | "protocol-invalid-no-candidate"
    | "admission-reconciled";
  readonly evidence:
    readonly ArtifactRef[];
}

interface ExternalSemanticUnarmedTrajectoryRefV1 {
  readonly sourceDomainId:
    SemanticAuthorityDomainId;
  readonly sourceExecution:
    SemanticExecutionLocatorV1;
  readonly qlek:
    QLEK;
  readonly evidence:
    readonly ArtifactRef[];
}

interface SemanticExecutionStateV1 {
  readonly binding:
    SemanticExecutionBindingRefV1;
  readonly arm:
    SemanticArmBindingRefV1 | null;
  readonly validation:
    ProtocolV8SemanticValidationResultV1 | null;
}

interface SemanticQuestionStateV1 {
  readonly schema:
    "gate-a-semantic-question-state.v1";
  readonly domainId:
    SemanticAuthorityDomainId;
  readonly qlek:
    QLEK;
  readonly currentEpoch:
    SemanticCoordinationEpoch;
  readonly latestGrantGeneration:
    AdmissionAuthorityGeneration | null;
  readonly localExecutions:
    readonly SemanticExecutionStateV1[];
  readonly admissionClaims:
    readonly SemanticAdmissionRecordV1[];
  readonly originWitnesses:
    readonly SemanticAdmissionWitnessRefV1[];
  readonly conflicts:
    readonly SemanticAdmissionConflictRefV1[];
  readonly unvalidatedCapturedExecutions:
    readonly SemanticExecutionLocatorV1[];
  readonly pendingProtocolValidValidations:
    readonly ProtocolV8ProtocolValidSemanticCompletionRefV1[];
  readonly unresolvedHazards:
    readonly SemanticSamplingHazardRefV1[];
  readonly resumableUnarmedExecution:
    SemanticExecutionLocatorV1 | null;
  readonly consumableAdmission:
    SemanticAdmissionRecordV1 | null;
}
```

Require every external hazard, clearance, and unarmed-trajectory evidence array
to be non-empty and duplicate-free. A clearance is provenance and never creates
another semantic candidate. An external unarmed trajectory is audit/reconciliation
provenance only and never becomes a local armable Execution. Require every
conflict to bind both claims to its exact QLEK, contain distinct admission IDs,
and order them by admission ID ASCII ascending. Expose no winner field. Treat
`SemanticQuestionStateV1` and hazard state as derived read projections, never
persisted status objects or mutable `hazard = true/false` fields.

Treat `SemanticAdmissionRecordV1.semanticQuestionBinding` as reconstructibility
and provenance. It does not enter `SemanticAdmissionId`.

## 45. Authority and semantic-history APIs

Expose:

```ts
interface AcquireAdmissionAuthorityRequestV1 {
  readonly qlek: QLEK;
  readonly sessionId: RunnerSessionId;
}

type AcquireAdmissionAuthorityResultV1 =
  | {
      readonly kind: "acquired";
      readonly authority: AdmissionAuthorityRefV1;
      readonly state: SemanticQuestionStateV1;
    }
  | {
      readonly kind: "reuse";
      readonly admission: SemanticAdmissionRecordV1;
      readonly state: SemanticQuestionStateV1;
    }
  | {
      readonly kind: "validation-required";
      readonly executions:
        readonly [SemanticExecutionLocatorV1, ...SemanticExecutionLocatorV1[]];
      readonly state: SemanticQuestionStateV1;
    }
  | {
      readonly kind: "reconciliation-required";
      readonly completions:
        readonly [
          ProtocolV8ProtocolValidSemanticCompletionRefV1,
          ...ProtocolV8ProtocolValidSemanticCompletionRefV1[]
        ];
      readonly state: SemanticQuestionStateV1;
    }
  | {
      readonly kind: "hazard-blocked";
      readonly hazards:
        readonly [SemanticSamplingHazardRefV1, ...SemanticSamplingHazardRefV1[]];
      readonly state: SemanticQuestionStateV1;
    }
  | {
      readonly kind: "conflict";
      readonly conflicts:
        readonly [SemanticAdmissionConflictRefV1, ...SemanticAdmissionConflictRefV1[]];
      readonly state: SemanticQuestionStateV1;
    }
  | {
      readonly kind: "busy";
      readonly qlek: QLEK;
    };

interface ReleaseAdmissionAuthorityRequestV1 {
  readonly authority: AdmissionAuthorityRefV1;
}

type ReleaseAdmissionAuthorityResultV1 =
  | { readonly kind: "released" }
  | { readonly kind: "not-held" };

interface ReconcileSemanticCompletionRequestV1 {
  readonly execution: SemanticExecutionLocatorV1;
}

type ReconcileSemanticCompletionResultV1 =
  | {
      readonly kind: "admitted";
      readonly admission: SemanticAdmissionRecordV1;
      readonly state: SemanticQuestionStateV1;
    }
  | {
      readonly kind: "converged";
      readonly admission: SemanticAdmissionRecordV1;
      readonly witnessAdded: boolean;
      readonly state: SemanticQuestionStateV1;
    }
  | {
      readonly kind: "conflict";
      readonly state: SemanticQuestionStateV1;
    }
  | {
      readonly kind: "busy";
      readonly qlek: QLEK;
    };

interface LoadSemanticQuestionStateRequestV1 {
  readonly qlek: QLEK;
}

interface LoadSemanticExecutionStateRequestV1 {
  readonly runId: GateARunId;
  readonly executionId: ExecutionId;
}

type LoadSemanticExecutionStateResultV1 =
  | {
      readonly kind: "semantic";
      readonly state: SemanticExecutionStateV1;
    }
  | { readonly kind: "non-semantic" };
```

The M2 public service also exposes these pure/read-only conceptual signatures:

```ts
loadSemanticQuestionState(
  request: LoadSemanticQuestionStateRequestV1
): Promise<SemanticQuestionStateV1>;

loadSemanticExecutionState(
  request: LoadSemanticExecutionStateRequestV1
): Promise<LoadSemanticExecutionStateResultV1>;
```

## 46. Protocol-v8 M2 mutation representations

Expose:

```ts
interface AuthorizeSemanticExecutionV1 {
  readonly kind:
    "authorize-semantic-execution";
  readonly workItemId:
    WorkItemId;
  readonly basis:
    ExecutionCreationRequestBasis;
  readonly semanticQuestion:
    ValidatedSemanticQuestionRefV1;
  readonly admissionAuthority:
    AdmissionAuthorityRefV1;
}

interface ArmSemanticExecutionDispatchV1 {
  readonly kind:
    "arm-semantic-execution-dispatch";
  readonly executionId:
    ExecutionId;
  readonly workItemId:
    WorkItemId;
  readonly ownershipGeneration:
    OwnershipGeneration;
  readonly admissionAuthority:
    AdmissionAuthorityRefV1;
  readonly revalidationBasis:
    readonly ArtifactRef[];
  readonly dispatchEvidence:
    readonly ArtifactRef[];
  readonly recoveryCapability:
    RecoveryCapabilityRef | null;
}

interface AdmitProtocolV8SemanticValidationV1 {
  readonly kind:
    "admit-protocol-v8-semantic-validation";
  readonly result:
    ProtocolV8SemanticValidationResultV1;
}
```

## 47. Semantic-history export and reconciliation types

Expose:

```ts
interface SemanticHistoryAuthorityGrantV1 {
  readonly qlek: QLEK;
  readonly epoch: SemanticCoordinationEpoch;
  readonly generation: AdmissionAuthorityGeneration;
  readonly sessionId: RunnerSessionId;
}

interface SemanticHistoryExportV1 {
  readonly schema:
    "gate-a-semantic-history-export.v1";
  readonly sourceDomainId:
    SemanticAuthorityDomainId;
  readonly closedEpoch:
    SemanticCoordinationEpoch;
  readonly successorEpoch:
    SemanticCoordinationEpoch;
  readonly authorityGrants:
    readonly SemanticHistoryAuthorityGrantV1[];
  readonly executionBindings:
    readonly SemanticExecutionBindingRefV1[];
  readonly armBindings:
    readonly SemanticArmBindingRefV1[];
  readonly semanticValidations:
    readonly ProtocolV8SemanticValidationResultV1[];
  readonly admissionClaims:
    readonly SemanticAdmissionRecordV1[];
  readonly originWitnesses:
    readonly SemanticAdmissionWitnessRefV1[];
  readonly unresolvedHazards:
    readonly Extract<
      SemanticSamplingHazardRefV1,
      { readonly kind: "external-armed-execution" }
    >[];
  readonly hazardClearances:
    readonly ExternalSemanticHazardClearanceRefV1[];
  readonly unarmedTrajectories:
    readonly ExternalSemanticUnarmedTrajectoryRefV1[];
  readonly artifactClosure:
    readonly ArtifactRef[];
}

interface ExportSemanticHistoryRequestV1 {
  readonly sessionId: RunnerSessionId;
}

type ExportSemanticHistoryResultV1 =
  | {
      readonly kind: "exported";
      readonly history: ArtifactRef;
      readonly sourceDomainId: SemanticAuthorityDomainId;
      readonly closedEpoch: SemanticCoordinationEpoch;
      readonly successorEpoch: SemanticCoordinationEpoch;
    }
  | {
      readonly kind: "busy";
      readonly scope: "domain" | "qlek";
      readonly qlek: QLEK | null;
    };

interface SemanticAdmissionWithWitnessesV1 {
  readonly admission:
    SemanticAdmissionRecordV1;
  readonly witnesses:
    readonly [
      SemanticAdmissionWitnessRefV1,
      ...SemanticAdmissionWitnessRefV1[]
    ];
}

interface ValidatedExternalSemanticHistoryRefV1 {
  readonly schema:
    "gate-a-validated-external-semantic-history.v1";
  readonly sourceHistory:
    ArtifactRef;
  readonly sourceDomainId:
    SemanticAuthorityDomainId;
  readonly closedEpoch:
    SemanticCoordinationEpoch;
  readonly successorEpoch:
    SemanticCoordinationEpoch;
  readonly admissions:
    readonly SemanticAdmissionWithWitnessesV1[];
  readonly pendingProtocolValidCompletions:
    readonly ProtocolV8ProtocolValidSemanticCompletionRefV1[];
  readonly unresolvedHazards:
    readonly Extract<
      SemanticSamplingHazardRefV1,
      { readonly kind: "external-armed-execution" }
    >[];
  readonly hazardClearances:
    readonly ExternalSemanticHazardClearanceRefV1[];
  readonly unarmedTrajectories:
    readonly ExternalSemanticUnarmedTrajectoryRefV1[];
  readonly validationEvidence:
    readonly ArtifactRef[];
}

interface ReconcileExternalSemanticHistoryRequestV1 {
  readonly history:
    ValidatedExternalSemanticHistoryRefV1;
}

type ReconcileExternalSemanticHistoryResultV1 =
  | {
      readonly kind: "reconciled";
      readonly sourceHistory: ArtifactRef;
      readonly sourceDomainId: SemanticAuthorityDomainId;
      readonly newEpoch: SemanticCoordinationEpoch;
      readonly affectedQleks: readonly QLEK[];
    }
  | {
      readonly kind: "already-reconciled";
      readonly sourceHistory: ArtifactRef;
      readonly sourceDomainId: SemanticAuthorityDomainId;
    }
  | {
      readonly kind: "busy";
      readonly scope: "domain" | "qlek";
      readonly qlek: QLEK | null;
    };
```

Require `successorEpoch == closedEpoch + 1`, non-empty duplicate-free witness
tuples, non-empty duplicate-free external validation evidence, canonical array
ordering, and duplicate freedom under the owning contracts.

## 48. Exact protocol-v8 schema bindings

Bind future M6 protocol-valid validation to exactly:

```text
execution receipt
path = formal/reviews/schemas/execution-receipt-v4.schema.json
SHA-256 = 9d5e0b50bf9b5464fadc9c57edfa265935bdf0ace9fcaf1c9770e5f7e7ab312c

semantic question binding
path = formal/reviews/schemas/semantic-question-binding-v1.schema.json
SHA-256 = fae52d48d08df8e9c3d7cafc74899913f4cc5655fb0a7ac8eb594df6edece15e

semantic admission origin witness
path = formal/reviews/schemas/semantic-admission-origin-witness-v1.schema.json
SHA-256 = acdcf78b6862080f5147df525bc919e2b8eb6eb94b3c920fee8b9886e582607b

semantic identity
path = formal/reviews/schemas/semantic-identity-v1.schema.json
SHA-256 = fc9e6a4dc241508c50a1d1671c9f43bd04ab257a8d0ad5b6319ba5522966a3f3
```

These content-addressed schemas, their existing Python validation, and future M6
mechanical/protocol validation remain authority. M0/Zod never replaces them.
For a protocol-valid result, M6 must mechanically establish exactly:

```text
semanticCandidate
→ exact C2 CanonicalJsonValueBytesV1(V)
→ mediaType == application/json
→ runner-owned immutable ArtifactRef
→ repositoryPath == null

semanticQuestionBinding
→ exact P8 semantic-question-binding-v1 representation

executionReceipt
→ exact P8 execution-receipt-v4

originWitness
→ exact P8 semantic-admission-origin-witness-v1

semanticAdmissionId
→ exact C2 SemanticAdmissionId(K,V)

execution
→ exact SemanticExecutionBinding(E,K)

origin witness
→ exact E/K/V/receipt/Arm binding
```

M2 verifies only authoritative M6 provenance, agreement with retained M2
history, and artifact integrity; M2 does not redo these semantic/mechanical
derivations.

## 49. C9-B runtime validator closure

Use the existing `zod@4.6.7` strict `safeParse` discipline and stable
`ContractValidationResult` boundary for every new serialized type in sections
43 through 47 and for every new request, result, and mutation representation.
At minimum export:

```text
validateSemanticAuthorityDomainId
validateSemanticCoordinationEpoch
validateAdmissionAuthorityGeneration
validateAdmissionAuthorityRefV1
validateSemanticExecutionLocatorV1
validateValidatedSemanticQuestionRefV1
validateSemanticExecutionBindingRefV1
validateSemanticArmBindingRefV1
validateProtocolV8SemanticValidationResultV1
validateProtocolV8ProtocolValidSemanticCompletionRefV1
validateProtocolV8ProtocolInvalidSemanticCompletionRefV1
validateSemanticAdmissionRecordV1
validateSemanticAdmissionWitnessRefV1
validateSemanticAdmissionConflictRefV1
validateSemanticSamplingHazardRefV1
validateExternalSemanticHazardClearanceRefV1
validateExternalSemanticUnarmedTrajectoryRefV1
validateSemanticExecutionStateV1
validateSemanticQuestionStateV1
validateAcquireAdmissionAuthorityRequestV1
validateAcquireAdmissionAuthorityResultV1
validateReleaseAdmissionAuthorityRequestV1
validateReleaseAdmissionAuthorityResultV1
validateAuthorizeSemanticExecutionV1
validateArmSemanticExecutionDispatchV1
validateAdmitProtocolV8SemanticValidationV1
validateReconcileSemanticCompletionRequestV1
validateReconcileSemanticCompletionResultV1
validateLoadSemanticQuestionStateRequestV1
validateLoadSemanticExecutionStateRequestV1
validateLoadSemanticExecutionStateResultV1
validateSemanticHistoryAuthorityGrantV1
validateSemanticHistoryExportV1
validateExportSemanticHistoryRequestV1
validateExportSemanticHistoryResultV1
validateSemanticAdmissionWithWitnessesV1
validateValidatedExternalSemanticHistoryRefV1
validateReconcileExternalSemanticHistoryRequestV1
validateReconcileExternalSemanticHistoryResultV1
```

Apply strict closed objects, no coercion, no defaults, no transforms, no
passthrough, no unknown-field stripping, deterministic issue mapping, and every
exact non-empty/duplicate-free/ordering/cross-field constraint above.
Representation validation creates no semantic, protocol, currentness,
qualification, persistence, or conflict-resolution authority.

Retain exactly:

```text
zod@4.6.7
future DC-ZOD-GATE-A-CONTRACTS required
19 current deriveId domains
```

`SemanticAuthorityDomainId` is UUIDv4 occurrence identity generated by M2, not
`deriveId`. Epoch and generation are safe-integer counters, not hashes.
