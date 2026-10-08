---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "construction-candidate-bound-identity-view"
domain: "turnlock-rust-formal-assurance"
severity: "strict"
name: "Gate A protocol v8 candidate-bound identity and CandidateView construction"
---

# Gate A protocol v8 candidate-bound identity and CandidateView construction

## Status and authority

This document is the C5 construction closure for protocol-v8 work authorized by
ADR-056 and constrained by the published C1, C2, C3 and C4 construction
closures.

It is a non-protocol-authoritative construction artifact.

It closes the exact relation between:

```text
CandidateRevisionId

CoverageSpec

CandidateView
```

required for protocol-v8 candidate-bound semantic questions.

Authority remains:

```text
docs/specification/turnlock-spec.md

accepted ADRs

especially ADR-055 and ADR-056

docs/formal/gate-a-protocol-v8-semantic-question-contract-catalog.md

docs/formal/gate-a-protocol-v8-semantic-identity-algebra.md

docs/formal/gate-a-protocol-v8-semantic-admission-authority-execution-fencing.md

docs/formal/gate-a-protocol-v8-semantic-fact-qualification-resolution.md

accepted existing M2 CandidateRevision authority

accepted existing M7 sealed-candidate materialization authority
```

This document MUST NOT:

```text
change TURNLOCK product semantics

change CandidateRevisionId identity

replace candidate-revision.v2

create CandidateRevisionV3

equate distinct CandidateRevision occurrences by repository-content equality

change C1 SemanticQuestionContracts

change C2 identity framing

change C3 admission/fencing semantics

change C4 Fact semantics

activate protocol v8

select packet serialization

select SQL/storage/cache implementation

select final runtime APIs

change immutable P1-P7 artifacts
```

If later construction requires choosing between materially different semantic
meanings rather than mechanically refining this closure:

```text
STOP
→ decision-required
→ accepted ADR
→ resume from earliest affected construction stage
```

# C5 construction boundary

C5 closes:

```text
exact CandidateRevision nominal authority consumption

CoverageSpec semantics

CandidateView@1 semantic value

CandidateViewOf(C, coverage, V)

complete CandidateView construction

readable-path-scoped CandidateView construction

raw path identity reuse

canonical path ordering

exact entry/state/byte identity

candidate-view reconstruction/validation

candidate-bound producer binding

candidate-bound revision binding

candidate-bound challenge inherited binding

fresh current-candidate Semantic Arm authorization

stale-before-Arm behavior

stale-after-Arm semantic-history preservation

candidate-bound Fact applicability

RepairIntent exact-candidate projection
```

C5 does NOT close:

```text
packet schemas

receipt schemas

model packet field names

physical CandidateView cache

module API signatures

SQL layout

TLA+ implementation

P8 activation
```

# CandidateRevision authority is unchanged

C5 consumes the existing exact M2-owned CandidateRevision identity.

Current accepted identity remains exactly:

```text
deriveId(
  "candidate-revision.v2",
  runId,
  decimal ordinal,
  parentCandidateId or "-",
  producedByRepairIntentId or "-",
  producedByAssuranceProjectionId or "-"
)
```

The materialization and semantic subject remain payload bound to that exact
nominal slot under existing M2 authority.

C5 does NOT redefine CandidateRevision identity.

Therefore:

```text
C17 != C18
```

remains true even when:

```text
C17.materialization == C18.materialization
```

or their complete repository physical content is byte-identical.

Repository-content equality MUST NOT collapse CandidateRevision identity.

# CandidateRevision versus CandidateView

Protocol v8 keeps two distinct identity modes.

```text
CandidateRevisionId
```

is exact nominal authority.

It answers:

```text
which exact candidate occurrence?
```

```text
CandidateView
```

is exact extensional physical value.

It answers:

```text
what exact physical state is this semantic question authorized to observe?
```

A CandidateView NEVER substitutes for CandidateRevision identity.

A CandidateRevision identity NEVER substitutes for the exact physical state
exposed to cognition.

# CandidateView semantic value type

The exact C2 value type remains:

```text
turnlock.semantic-value:CandidateView@1
```

C5 defines the exact canonical semantic value for that type.

# CoverageSpec

CoverageSpec is NOT part of CandidateView semantic payload.

It is an input to the deterministic relation:

```text
CandidateViewOf(
  exact CandidateRevision C,
  exact CoverageSpec coverage,
  exact CandidateView V
)
```

Define conceptually exactly:

```text
CoverageSpecV1 =
    {
      kind: "complete"
    }

  |

    {
      kind: "readable-paths"

      paths:
        exact canonical ordered sequence
        of raw candidate path identities
    }
```

For `readable-paths`, require:

```text
paths duplicate-free

every path is one canonical M7 raw candidate path identity

every path is present in the exact sealed materialization of C

paths are ordered by decoded raw path bytes
in unsigned-byte lexicographic ascending order
```

No path may be:

```text
glob

wildcard

directory prefix

fuzzy selector

semantic path expression

mutable-workspace lookup
```

CoverageSpec is relation authority.

It is not duplicated into CandidateView value identity.

# Exact CandidateViewV1 semantic value

Define exactly:

```text
CandidateViewV1 {
  gitObjectFormat:
    "sha1"
    |
    "sha256"

  entries:
    ordered array<CandidateViewEntryV1>
}
```

No other field belongs to the CandidateView@1 semantic value.

# CandidateViewEntryV1

Define exactly:

```text
CandidateViewEntryV1 {
  pathBytesBase64url:
    exact canonical raw candidate path identity

  state:
    CandidateViewEntryStateV1
}
```

For protocol-v8 CandidateView@1 construction, exact state is one of:

```text
BlobStateV1

SymlinkStateV1

GitlinkStateV1
```

No `absent` state belongs to a CandidateView produced by current protocol-v8 C5
construction.

# BlobStateV1

Define:

```text
BlobStateV1 {
  kind:
    "blob"

  mode:
    "100644"
    |
    "100755"

  content:
    ExactBytesV1
}
```

`content` commits exact file bytes, not ArtifactRef identity.

# SymlinkStateV1

Define:

```text
SymlinkStateV1 {
  kind:
    "symlink"

  mode:
    "120000"

  content:
    ExactBytesV1
}
```

Symlink target bytes are exact content bytes.

C5 never materializes a filesystem symlink to construct CandidateView.

# GitlinkStateV1

Define:

```text
GitlinkStateV1 {
  kind:
    "gitlink"

  mode:
    "160000"

  objectId:
    exact canonical Git object ID
    retained by accepted M7 candidate materialization
}
```

C5 MUST NOT:

```text
resolve the submodule

contact a submodule repository

replace object ID with repository content

normalize object ID under a new C5 rule
```

Git object-ID validity remains governed by exact accepted M7/Git authority and
the exact `gitObjectFormat`.

# ExactBytesV1

Define exact canonical byte representation:

```text
ExactBytesV1 =
    {
      encoding:
        "utf-8"

      data:
        exact Unicode scalar string
    }

  |

    {
      encoding:
        "base64url"

      data:
        canonical unpadded RFC 4648 base64url
    }
```

Canonical rule is exactly:

```text
if exact bytes are valid UTF-8:
    MUST use encoding = "utf-8"
    data = exact decoded Unicode scalar string

otherwise:
    MUST use encoding = "base64url"
    data = canonical unpadded base64url(exact bytes)
```

Therefore:

```text
same exact bytes
→ exactly one ExactBytesV1 value
```

An implementation MUST NOT choose base64url for bytes that are valid UTF-8.

# Raw candidate path identity

C5 reuses exact accepted M7 raw candidate path identity.

`pathBytesBase64url` is:

```text
canonical unpadded RFC 4648 base64url
of exact full raw Git path bytes
```

Raw Git byte `0x2f` is the path separator.

Accepted M7 path admissibility remains authoritative, including rejection of:

```text
empty path

absolute path

trailing slash

NUL

empty component

.

..

unsafe Git-metadata-equivalent component
```

C5 performs no:

```text
Unicode normalization

locale normalization

filesystem separator normalization

realpath

case folding

host filesystem path normalization
```

# CandidateView path ordering

CandidateView entries MUST be:

```text
duplicate-free

ordered by decoded raw path bytes

unsigned-byte lexicographic ascending
```

This ordering applies to both complete and readable-path-scoped views.

Model-emitted `readable_paths` array order is NOT physical ordering authority.

For a scoped view, C5 canonicalizes the exact accepted path set into this order.

# Fields excluded from CandidateView semantic value

The following are NOT part of `CandidateView@1` canonical semantic payload:

```text
schema discriminator

legacy P7 selector

legacy P7 content-bound sha256 wrapper

CoverageSpec

CandidateRevisionId

GateARunId

candidate ordinal

parentCandidateId

producedByRepairIntentId

producedByAssuranceProjectionId

SemanticSubject

Candidate materialization ArtifactRef

content ArtifactRef identities

materializationEvidence

rootTreeObjectId

pathUtf8

repository path

mutable workspace path

Git HEAD

Git index state

receipt identity

root identity

supplement identity

current/stale flag

StateRevision

timestamp
```

These exclusions are semantic.

A later packet projection MUST NOT reinterpret excluded provenance as independent
CandidateView semantic identity.

# ArtifactRef exclusion

Accepted M7 candidate materialization represents blob/symlink content through
exact ArtifactRefs.

C5 resolves and verifies those exact ArtifactRefs, obtains exact content bytes,
then constructs `ExactBytesV1`.

Therefore:

```text
ArtifactRef A != ArtifactRef B
AND
bytes(A) == bytes(B)

→

same CandidateView physical content
```

Artifact storage identity is provenance/evidence.

It is not CandidateView extensional identity.

# pathUtf8 is projection-only

For one exact raw path:

```text
if raw bytes decode as valid UTF-8:
    pathUtf8 = exact decoded string

else:
    pathUtf8 = null
```

`pathUtf8` is a deterministic display/projection convenience.

It is NOT a second path authority and does NOT enter CandidateView@1 semantic
payload.

A future C6 packet MAY expose it only as an exact deterministic projection of the
raw path already committed by CandidateView.

# rootTreeObjectId exclusion

`rootTreeObjectId` MUST NOT enter CandidateView@1 semantic payload.

For a complete view it is redundant with:

```text
gitObjectFormat
+
complete exact path/state set
```

For a readable-path-scoped view it would incorrectly reveal physical state
outside the authorized coverage.

Require the non-interference property:

```text
if only physical state outside exact CoverageSpec changes,
the scoped CandidateView value does not change
```

A packet projection for a scoped CandidateView MUST NOT reintroduce a global
candidate tree digest as model-visible semantic state.

# CandidateView equality

CandidateView equality is exact structural equality over:

```text
gitObjectFormat

ordered entries
```

Each entry equality is exact over:

```text
raw path identity

state kind

mode

exact content bytes
or exact gitlink object ID
```

Nothing else participates.

Therefore distinct CandidateRevision occurrences may lawfully resolve to the same
CandidateView semantic value.

# CandidateViewOf functional relation

Define conceptually:

```text
CandidateViewOf(
  exact CandidateRevision C,
  exact CoverageSpec coverage,
  exact CandidateView V
)
```

For one exact pair:

```text
(C, coverage)
```

there MUST NOT exist two incompatible lawful CandidateViews.

Require:

```text
Cardinality({
  V |
  CandidateViewOf(C, coverage, V)
})
<= 1
```

For one valid authoritative C and one valid C5 CoverageSpec, exact construction
must yield one deterministic V.

Two incompatible values for the same exact pair are:

```text
CANDIDATE-VIEW-INTEGRITY-FAILURE
```

They are NOT authority for two competing semantic questions.

# CandidateViewOf source authority

Construct CandidateView only from:

```text
exact authoritative CandidateRevisionRef C

exact admitted sealed candidate binding

exact C.materialization ArtifactRef

exact canonical GateACandidateMaterializationV1

exact content artifacts referenced by that materialization
```

Never use:

```text
mutable repository workspace

current checkout

HEAD

Git index

ambient filesystem

repository traversal against current disk state
```

as substitute candidate authority.

# CandidateView construction algorithm

Conceptually define:

```text
ConstructCandidateView(C, coverage)
```

with exactly these semantic steps.

## Step 1 — resolve exact CandidateRevision

Resolve exact authoritative `CandidateRevisionRef C`.

Require existing M2 CandidateRevision identity and payload integrity.

Do not accept a caller-constructed incompatible candidate payload.

## Step 2 — resolve exact sealed materialization

Resolve exact `C.materialization`.

Require it equals the materialization admitted for that exact CandidateRevision
under existing M2/sealed-candidate authority.

## Step 3 — validate exact M7 materialization

Resolve exact canonical:

```text
GateACandidateMaterializationV1 M
```

Require accepted M7 integrity including:

```text
canonical path identity/order

valid entry modes/types

exact content ArtifactRefs

exact gitObjectFormat

accepted tree round-trip materialization authority
```

C5 does not redefine Git materialization validity.

## Step 4 — validate CoverageSpec

For:

```text
coverage.kind = "complete"
```

select every materialized entry.

For:

```text
coverage.kind = "readable-paths"
```

require every canonical path belongs to `M.entries`.

No missing/prospective path is permitted.

## Step 5 — project exact selected physical state

For each selected path:

```text
blob
→ exact kind/mode
→ verify/resolve exact content bytes
→ canonical ExactBytesV1

symlink
→ exact kind/mode
→ verify/resolve exact target bytes
→ canonical ExactBytesV1

gitlink
→ exact kind/mode/objectId
```

## Step 6 — canonical ordering

Order selected entries by decoded raw path bytes in unsigned-byte lexicographic
ascending order.

## Step 7 — construct CandidateViewV1

Construct exactly:

```text
{
  gitObjectFormat:
    M.gitObjectFormat,

  entries:
    exact selected canonical entries
}
```

No additional field.

## Step 8 — construct C2 SemanticValue identity

Identify exact V under:

```text
turnlock.semantic-value:CandidateView@1
```

using exact C2 `SemanticValueId` algebra.

# Complete CandidateView construction

For RealizationScope initial/revision:

```text
coverage =
{
  kind: "complete"
}
```

Require:

```text
Paths(V)
==
exact complete path set of C.materialization
```

Every exact materialized path appears once.

No extra path appears.

No materialized path is omitted.

An empty candidate materialization lawfully yields:

```text
entries = []
```

for its complete CandidateView.

# Complete view and absent state

The accepted M7 candidate materialization contains only physically present
candidate entries.

Therefore a complete protocol-v8 CandidateView contains no `absent` state.

Absence of a path is represented by its non-membership in the complete
materialization/view.

# RealizationScope path-authority restriction

The current protocol-v8 RealizationScope producer receives only exact raw
candidate path identities supplied by its complete CandidateView and MUST NOT
infer paths outside that view.

C5 therefore mechanically requires for any positive current-P8 RealizationScope:

```text
readable_paths
⊆
Paths(complete CandidateView)

writable_paths
⊆
readable_paths
```

Therefore:

```text
writable_paths
⊆
Paths(complete CandidateView)
```

Current protocol-v8 RealizationScope does not authorize prospective absent path
identity.

# Current-P8 automatic repair cannot create a new absent path

The existing generic M7 patch engine may mechanically support:

```text
before = null
after != null
```

under other accepted authority.

That generic physical capability is NOT semantic authority for current
protocol-v8 automatic RepairIntent.

Current P8 RS/RR construction has no lawful path for naming a previously absent
candidate path.

Therefore current automatic RepairIntent derived from accepted RepairRealization
MUST NOT create a path that was absent from its exact source CandidateRevision.

This restriction does NOT modify generic M7 capability.

It only closes current P8 semantic authorization.

# RepairRealization CoverageSpec

Let:

```text
F =
exact AcceptedRealizationScope Fact
```

C4 mechanically exposes:

```text
CandidateRevisionOf(F)

exact accepted RealizationScope semantic value
including readable_paths[]
```

For RepairRealization on exact candidate `C`, require first:

```text
CandidateRevisionOf(F)
==
C
```

If not equal:

```text
deterministic non-bindable disposition
```

No repository-content equality or CandidateView equality may substitute for this
nominal equality.

Then define exact coverage:

```text
coverage =
{
  kind:
    "readable-paths",

  paths:
    canonical raw-byte ordered
    duplicate-free set of
    F.readable_paths
}
```

Require every path remains present in exact C materialization.

# RepairRealization scoped CandidateView

Construct:

```text
CandidateViewOf(
  C,
  exact readable-paths CoverageSpec,
  V
)
```

Require:

```text
Paths(V)
==
exact canonical set of
AcceptedRealizationScope.readable_paths
```

Every entry state is the exact present state from C.

No path outside accepted readable scope is exposed.

No path inside accepted readable scope is omitted.

A lawfully empty readable path set yields a scoped CandidateView with:

```text
entries = []
```

C5 does not invent a non-empty-scope requirement.

# Scoped-view outside-state non-interference

For exact coverage P:

```text
CandidateViewOf(C17, P, V17)

CandidateViewOf(C18, P, V18)
```

If exact state of every path in P is identical and exact `gitObjectFormat` is
identical, then changes only to candidate paths outside P MUST NOT change the
CandidateView value.

This remains true even when:

```text
rootTree(C17) != rootTree(C18)
```

because root-tree identity is excluded from scoped CandidateView semantics.

# Same CandidateView across distinct candidates

It is lawful that:

```text
C17 != C18

CandidateViewOf(C17, coverage, V)

CandidateViewOf(C18, coverage, V)
```

for one same exact V.

In that case both candidate-bound questions may reuse the same CandidateView
SemanticValueRef.

They still MUST retain their distinct exact CandidateRevision authorities.

# Required anti-cheat identity rule

For RealizationScope:

```text
C17 != C18
```

implies:

```text
ExactAuthorityRef(C17)
!=
ExactAuthorityRef(C18)
```

and therefore:

```text
QLEK_RS(C17)
!=
QLEK_RS(C18)
```

even when:

```text
CandidateViewOf(C17, complete, V)

CandidateViewOf(C18, complete, V)
```

for the exact same V.

The same nominal-authority principle applies to RepairRealization.

# CandidateView claimed-value validation

A valid CandidateView `SemanticValueRef` is not sufficient merely because its
C2 SemanticValueId recomputes.

For candidate-bound binding, C5 requires:

```text
resolve exact CandidateRevision C

derive exact expected CoverageSpec coverage

resolve exact CandidateView SemanticValueRef → V

ConstructCandidateView(C, coverage) → V'

require:

V' == V
```

Mismatch is:

```text
CANDIDATE-VIEW-INTEGRITY-FAILURE
```

Do not repair, rebase, normalize or substitute another view.

# Expected CoverageSpec by contract

For:

```text
RealizationScopeInitial@1

RealizationScopeRevision@1
```

expected CoverageSpec is exactly:

```text
Complete
```

For:

```text
RepairRealizationInitial@1

RepairRealizationRevision@1
```

expected CoverageSpec is exactly:

```text
ReadablePaths(
  exact canonical
  AcceptedRealizationScope.readable_paths
)
```

The caller does not choose another coverage.

# BoundCandidateRevision

Define conceptually:

```text
BoundCandidateRevision(Q)
```

for candidate-bound protocol-v8 semantic questions.

For:

```text
RealizationScopeInitial

RealizationScopeRevision

RepairRealizationInitial

RepairRealizationRevision
```

the bound candidate is the exact direct:

```text
ExactAuthorityRef<CandidateRevisionId>
```

in the LogicalQuestionDescriptor input.

# Challenge inherited candidate binding

For:

```text
RealizationScopeChallenge
```

derive:

```text
challenged RealizationScope SemanticAdmission
→ producer QLEK
→ exact CandidateRevision C
```

For:

```text
RepairRealizationChallenge
```

derive:

```text
challenged RepairRealization SemanticAdmission
→ producer QLEK
→ exact CandidateRevision C
```

The challenge MUST NOT:

```text
resolve "current candidate"

choose another candidate

construct another CandidateView

rebase the challenged producer
```

Its candidate authority is inherited exactly through the challenged Admission.

# CandidateRevisionOf accepted candidate-bound Facts

C4 preserves exact candidate binding for:

```text
AcceptedRealizationScope

AcceptedRepairRealization
```

C5 defines mechanically:

```text
CandidateRevisionOf(AcceptedRealizationScope F)
=
exact CandidateRevision of F's anchor RS Admission/QLEK
```

and:

```text
CandidateRevisionOf(AcceptedRepairRealization F)
=
exact CandidateRevision of F's anchor RR Admission/QLEK
```

Candidate advance does NOT rewrite either projection.

# RealizationScope revision same-candidate closure

For exact prior positive RS admission `A0`, resolve:

```text
C0 =
BoundCandidateRevision(A0.QLEK)

V0 =
exact complete CandidateView input of A0.QLEK

U0 =
exact AcceptedUniqueCorrection input of A0.QLEK
```

A lawful RealizationScopeRevision descriptor MUST retain exactly:

```text
candidateRevision == C0

completeCandidateView == V0

acceptedUniqueCorrection == U0
```

plus its exact prior producer/challenge inputs.

It MUST NOT re-resolve current candidate as semantic input.

# RepairRealization revision same-candidate closure

For exact prior positive RR admission `A0`, resolve:

```text
C0 =
BoundCandidateRevision(A0.QLEK)

V0 =
exact scoped CandidateView input

U0 =
exact AcceptedUniqueCorrection input

S0 =
exact AcceptedRealizationScope input
```

A lawful RepairRealizationRevision descriptor MUST retain exactly:

```text
candidateRevision == C0

scopedCandidateView == V0

acceptedUniqueCorrection == U0

acceptedRealizationScope == S0
```

plus exact prior producer/challenge inputs.

No scope expansion, candidate substitution or CandidateView substitution is
lawful.

# Currentness is authorization, not semantic identity

`"current candidate"` is never a LogicalQuestionDescriptor semantic input.

New candidate-bound binding proceeds conceptually:

```text
authoritative current candidate
↓
resolve exact CandidateRevision C
↓
construct exact CandidateViewOf(C, coverage, V)
↓
construct exact LogicalQuestionDescriptor
↓
derive QLEK
```

After QLEK construction:

```text
C
```

is immutable question identity.

Currentness is separately revalidated at the dispatch authorization boundary.

# Candidate-bound currentness at Semantic Arm

For every candidate-bound semantic Execution E with QLEK K:

```text
C =
BoundCandidateRevision(K)
```

C5 adds this exact T3 precondition:

```text
authoritative currentCandidate.candidateId
==
C
```

This check MUST be linearized atomically with the C3/M2 Semantic Arm
transition.

A conforming realization MUST NOT permit:

```text
check C is current

candidate advances

Arm old C
```

between independent authoritative transitions.

Conceptually T3 includes in one authoritative linearization:

```text
fresh candidate-currentness recheck

C3 admission-authority generation recheck

Admission/conflict/completion/hazard rechecks

all normal M2 Arm preconditions

M2 Arm

SemanticArmBinding(E,K,g)
```

C9 owns the exact implementation transaction/API.

# Candidate advance before Arm

If:

```text
BoundCandidateRevision(K) = C17
```

and current candidate becomes C18 before lawful T3:

```text
C17 != C18
```

then:

```text
NO Arm

NO provider dispatch
```

The old candidate-bound execution is no longer a current-progression
dispatchable trajectory.

If it was never Armed, external semantic effect is impossible.

Candidate staleness before Arm does NOT require PNE merely to establish that the
never-Armed trajectory did not cross the external-effect boundary.

Exact retirement/supersession orchestration belongs to later construction.

# Candidate advance after lawful Arm

If C17 was exact current candidate at successful Semantic Arm and C18 later
becomes current:

```text
the old C17 Execution remains a lawfully Armed semantic Execution
```

Candidate staleness does NOT establish:

```text
PROVEN-NOT-EXECUTED

SemanticHazardCleared

ReplacementAuthorized
```

C3 hazard/recovery semantics continue unchanged.

If exact protocol-valid completion V later becomes authoritative:

```text
Admission(K_C17, V)
```

MUST be reconciled.

Candidate advance never erases old semantic history.

# Candidate advance after Arm but before dependency invocation

Existing M1/M4 execution-control semantics may revoke future external-work
authority and project that revocation through the execution-owned AbortSignal.

Such control MAY prevent dependency invocation under existing M4 rules.

However:

```text
candidate staleness alone
```

is never proof of non-execution.

Only exact accepted M4/M8 authority may establish PNE or other hazard-clearance
truth.

C5 creates no additional recovery mechanism.

# Historical candidate-bound admission applicability

An old candidate-bound admission remains historical truth for its exact old QLEK.

It MUST NOT satisfy a new current candidate's qualification target.

Therefore:

```text
Admission / Fact bound to C17
```

does not become:

```text
Admission / Fact bound to C18
```

even when candidate contents or CandidateViews are identical.

# Candidate-bound Fact current applicability

`AcceptedRealizationScope(C17)` and `AcceptedRepairRealization(C17)` remain
reconstructible historical facts after candidate advance.

For new candidate-bound progression on C18, require exact nominal equality:

```text
CandidateRevisionOf(F)
==
C18
```

where applicable.

Content equality, CandidateView equality or repository-tree equality MUST NOT
replace this check.

# Candidate-independent semantic work

C5 MUST NOT make these families candidate-bound:

```text
MaterialityAssessment

Refutation

DiscoveryClassification

NoNormativeImpact qualification

DecisionNecessity qualification

UniqueCorrection

their accepted candidate-independent revisions/challenges
```

Candidate occurrence under which such work happened remains provenance unless an
accepted future protocol explicitly changes the semantic input contract.

Candidate advance therefore does not create hidden rerun commands for these
families.

# Candidate advance creates fresh candidate-bound inputs

When current candidate changes:

```text
C17 → C18
```

new candidate-bound binding yields descriptors naming exact C18.

This mechanically creates fresh candidate-bound questions where required.

There is no hidden imperative:

```text
rerun task by name
```

Freshness emerges from exact input identity.

# RepairIntent projection boundary

RepairIntent is not a C1 SemanticQuestionContract output.

It is mechanically derived only from exact:

```text
AcceptedRepairRealization Fact
```

For accepted RR Fact F:

```text
C =
CandidateRevisionOf(F)
```

If its accepted RR semantic candidate contains:

```text
operations == []
```

then existing C1 semantics remain:

```text
no RepairIntent

no empty patch

no repair successor candidate
```

If patch-realized operations exist, C5 requires RepairIntent construction to bind:

```text
candidateId == C
```

exactly.

# RepairIntent authoritative before-state

For every repair operation path:

```text
derive authoritative before-state
from the exact scoped CandidateView
of the same source CandidateRevision C
```

Never accept model-authored or mutable-workspace before-state.

The approved patch combines:

```text
exact C5-derived before-state

+

exact qualified after-state
```

mechanically.

# RepairIntent cannot retarget

A RepairIntent derived from `AcceptedRepairRealization(C17)` MUST NOT be applied
to C18 merely because:

```text
repository bytes are equal

CandidateView values are equal

tree identity is equal
```

Existing M2 authority additionally requires a RepairIntent's candidate identity
to match the exact current candidate when constructing its successor.

No scope rebase, patch rebase, three-way merge or content-equivalence retarget is
authorized.

# CandidateView semantic preimage reconstructibility

Every valid `SemanticValueRef<CandidateView@1>` consumed by a candidate-bound
question MUST have exactly one canonical semantic value preimage under C2 and
MUST additionally satisfy exact C5 `CandidateViewOf`.

A digest string or cached view without reconstructible candidate/materialization
binding is insufficient authority.

# CandidateView caches

A future implementation MAY cache:

```text
(CandidateRevisionId, CoverageSpec)
→ CandidateView SemanticValueRef
```

for performance.

Such cache:

```text
is derived

is disposable

is not semantic authority

must not change reconstruction result
```

Deleting and rebuilding it from unchanged authoritative candidate history MUST
produce the same exact relation.

C5 selects no storage mechanism.

# C5 / C6 projection boundary

C5 defines CandidateView semantic meaning.

C6 owns packet/evidence representation.

A C6 packet projection MAY expose information deterministically derivable from
exact C5 authority, such as:

```text
coverage label determined by exact question contract/binding

pathUtf8 derived from exact raw path bytes

content-bound presentation digest
```

Such projection fields MUST NOT create new semantic authority.

For a scoped CandidateView, C6 MUST NOT make model-visible:

```text
global rootTreeObjectId

unselected candidate paths

candidate provenance

materialization ArtifactRef identity

receipt provenance

mutable workspace state
```

if those values are absent from the exact semantic input closure.

# P7 immutability

Protocol-v7 CandidateView packet/schema artifacts remain immutable.

C5 does NOT modify or reinterpret P7 bytes.

P7 may retain representation fields that are not part of P8 CandidateView@1
semantic identity, including:

```text
selector

sha256 wrapper

schema discriminator

root_tree_object_id

path_utf8

generic absent state
```

C5 defines protocol-v8 semantic value construction.

C6 later selects exact P8 artifact representation.

# M7 generic capability versus P8 semantic authority

Accepted M7 physical candidate-construction capability may be broader than
current P8 semantic RepairIntent authority.

In particular M7 may support exact path creation under other accepted authority.

C5 MUST NOT infer:

```text
M7 can physically create path
→ P8 automatic repair may semantically authorize that path
```

Physical capability never substitutes for semantic authorization.

# Required C5 properties

Later C10 formal/checker assurance must establish or refine at least:

```text
CandidateRevisionNominalIdentityPreserved

CandidateViewExtensionality

CandidateViewExcludesCandidateIdentity

CandidateViewExcludesProvenanceIdentity

CandidateViewExcludesArtifactRefIdentity

CandidateViewExcludesRootTreeIdentity

CandidateViewCanonicalPathOrdering

CandidateViewCanonicalExactBytes

CandidateViewOfFunctional

CandidateViewFromSealedMaterializationOnly

CompleteViewIsComplete

ScopedViewMatchesExactReadablePaths

ScopedViewOutsideCoverageNonInterference

CurrentP8ScopeUsesPresentPathsOnly

CandidateViewSoundness

DistinctCandidatesRemainDistinctWithEqualViews

AcceptedRSCannotRebindCandidate

AcceptedRRCannotRebindCandidate

CandidateBoundRevisionPreservesCandidate

CandidateBoundRevisionPreservesView

ChallengeInheritsProducerCandidate

CandidateCurrentnessCheckedAtSemanticArm

NoCandidateCurrentnessArmTOCTOU

StaleBeforeArmCannotDispatch

StaleAfterArmDoesNotEraseAdmission

CandidateStalenessDoesNotClearHazard

HistoricalCandidateFactPreservesBinding

CandidateIndependentWorkRemainsReusable

RepairIntentPreservesSourceCandidate

RepairIntentCannotRetarget

NoCandidateRebinding
```

# C5 anti-cheat cases

C5 explicitly closes at least:

```text
valid CandidateView hash but wrong bound CandidateRevision
→ CandidateView integrity failure

same C + same coverage producing two incompatible views
→ CandidateView integrity failure

different entry ordering for same physical view
→ rejected by canonical raw-byte ordering

alternate byte encoding for same exact bytes
→ rejected by ExactBytes canonicalization

different ArtifactRefs with identical bytes
→ same extensional CandidateView content

blob and symlink with identical bytes
→ different physical state because kind/mode differ

extra path in scoped CandidateView
→ invalid

missing path in scoped CandidateView
→ invalid

change only outside scoped coverage
→ scoped CandidateView unchanged

root-tree identity used to distinguish scoped view
→ forbidden

RealizationScope invents path absent from complete view
→ invalid current-P8 scope

RepairRealization attempts operation on path outside AcceptedRS writable_paths
→ invalid

C17 != C18 with identical physical content
→ candidate-bound QLEKs remain distinct

AcceptedRS(C17) used to bind RR(C18)
→ deterministic non-bindable

RS revision rebased from C17 to C18
→ invalid descriptor

RR revision rebased from C17 to C18
→ invalid descriptor

RS/RR challenge independently reselects current candidate
→ forbidden

candidate advance before candidate-bound Arm
→ no Arm / no provider dispatch

candidate currentness checked outside T3 then races with candidate advance
→ non-conforming

candidate advance after lawful Arm
→ old semantic hazard/history preserved

late protocol-valid old-candidate completion dropped because stale
→ forbidden

candidate staleness treated as PNE
→ forbidden

AcceptedRR(C17) projected into RepairIntent(C18)
→ forbidden

RepairIntent(C17) applied to C18 because bytes are identical
→ forbidden

mutable workspace used to reconstruct CandidateView
→ integrity failure/non-conforming

candidate-independent QLEK rerun solely because candidate advanced
→ forbidden
```

# Exact G-C5 coverage

Completion gate `G-C5` requires:

```text
no candidate-bound question can obtain or inherit physical authority
without naming one exact CandidateRevision
```

C5 satisfies this for direct producers:

```text
RealizationScopeInitial

RealizationScopeRevision

RepairRealizationInitial

RepairRealizationRevision
```

through exact direct `CandidateRevisionId` logical input.

C5 satisfies this for challenges:

```text
RealizationScopeChallenge

RepairRealizationChallenge
```

through exact challenged producer Admission → QLEK → CandidateRevision binding.

C5 satisfies this for candidate-bound accepted Facts:

```text
AcceptedRealizationScope

AcceptedRepairRealization
```

through exact anchor Admission/QLEK CandidateRevision projection.

C5 satisfies this for RepairIntent through:

```text
AcceptedRepairRealization
→ CandidateRevisionOf(F)
→ exact RepairIntent candidateId
```

No content-equivalence or mutable-current-candidate rebinding path exists.

# G-C5 closure

Completion gate `G-C5` is semantically satisfied by this construction when the
artifact is published and verified against ADR-056 and exact C1/C2/C3/C4
authority.

The gate establishes:

```text
one exact CandidateRevision is always named
for candidate-bound physical authority
```

and:

```text
CandidateView is exact extensional physical state
rather than nominal candidate identity
```

and:

```text
same physical state does not collapse distinct CandidateRevision authority
```

and:

```text
candidate advance before Arm prevents stale dispatch
while candidate advance after lawful Arm preserves old semantic history
```

and:

```text
candidate-bound scope, realization and RepairIntent authority never rebase
across CandidateRevision identity
```

After publication and audit of this artifact:

```text
C5 = CLOSED
```

Construction may then proceed to:

```text
C6 — protocol-v8 packet, receipt, and evidence projections
```

without constructing or activating protocol-v8 runtime artifacts.
