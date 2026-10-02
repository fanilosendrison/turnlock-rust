---
okf_version: "1.0"
kind: "RuntimeArtifact"
format: "nib-module"
workspace: "turnlock-rust"
date: "2026-10-01"
step_id: 2
id: NIB-M-GATE-A-REPOSITORY-CONTROL-MATERIALIZATION-CANDIDATE-CONSTRUCTION
version: "1.0.3"
scope: gate-a-campaign-runner/repository-control/materialization-candidate-construction
status: active
consumers: [architect, coding-agent]
superseded_by: []
---

# NIB-M — Gate A Repository Control — Materialization and Candidate Construction

It consumes `NIB-S-GATE-A-CAMPAIGN-RUNNER` version `7.0.4`.

This Module Brief is implementation-construction authority only. It creates no
TURNLOCK product semantics, hostile-review protocol semantics, canonical formal
semantics, review evidence, or verification evidence.

## 1. Responsibility boundary

M7 is decomposed exactly as:

```text
M7 repository-control
├── M7-A materialization / candidate construction
└── M7-B publication / remote observation / recovery
```

M7-A owns exactly:

```text
repository inspection
baseline repository authority observation
publication-target identity resolution from local Git configuration
baseline raw-object acquisition
complete reachable closure rooted at C
closure purification
bundle-v3 baseline carrier
independent offline restore verification
baselineGitBasis
C0 candidate materialization
candidate canonical representation
Git path admissibility
candidate-to-tree projection
tree round-trip verification
exact RepairIntent approved-patch application
repaired candidate sealing/evidence
deterministic publication-successor projection T
restart-safe local materialization of exact projected T
repository-inspection producer cause descriptors
```

M7-A does not own:

```text
Python validator invocation
Gate A semantic-subject mechanical derivation
hostile-review protocol/review-authority mechanical projection
campaign currentness
protocol selection
repair semantic sufficiency
RepairIntent qualification
authoritative candidate admission
remote predecessor P observation
P <= T proof
PublicationIntent construction/admission
publication WorkItem admission
Arm
remote ref mutation
already-current fresh remote observation
publication recovery
publication confirmation/non-application
published-repository post-publication qualification
OperationalBlocker identity
Operator Action Request identity
authoritative campaign state mutation
```

M7-B consumes the exact successor projection produced by M7-A. M7-B may verify
that projection and materialize its exact Git objects, but it may not derive
another successor, modify commit metadata, select another parent, or make
successor identity depend on current remote state.

## 2. Construction dependencies

M7-A consumes exactly these construction dependencies:

```text
CampaignArtifactStore
DC-GIT-CLI-GATE-A-REPOSITORY-CONTROL
```

The Git Dependency Contract is required before GREEN. Its separate artifact is
not created by this Module Brief.

The Git Dependency Contract must expose exactly these 19 Git dependency
primitives:

```text
01 qualifyRuntime
02 inspectRepositoryHead
03 inspectRepositoryObjectSources
04 inspectPushConfiguration
05 resolveRemotePushEndpoints
06 parsePushRefspec
07 classifyEndpoint
08 readRawObject
09 writeRawObject
10 inspectCommitObject
11 traverseReachableClosure
12 acquirePromisorObjects
13 acquireConfiguredUpstreamHistory
14 createIsolatedObjectDatabase
15 listTreeEntries
16 buildTree
17 classifyGitMetadataPath
18 createBaselineBundleV3
19 restoreAndInspectBaselineBundleV3
```

The NIB owns when and why these primitives are invoked and how their typed
results are interpreted.

The Dependency Contract owns Git executable qualification, exact commands,
flags, controlled environment, config semantics, byte/NUL parsing, refspec
grammar, object-format mechanics, raw object mechanics, bundle mechanics,
credential boundary, and Git error interpretation.

No M7-B remote-observation or remote-mutation primitive is part of this M7-A
contract version.

## 3. Git runtime qualification

Require the Dependency Contract to qualify at least:

```text
sha1 object format
sha256 object format
raw object read/write
missing-object traversal
NUL-safe tree listing
NUL-safe tree construction
bundle v3
```

Require capability qualification in addition to any minimum Git version.
Classify a missing required dependency capability as:

```text
construction/runtime dependency failure
```

Do not classify it as an operational blocker.

## 4. Canonical runner JSON

Use exactly this canonical runner JSON contract:

```text
UTF-8 JSON
object keys recursively lexicographically sorted
array order preserves exact semantic order
all required fields emitted
undefined rejected
bigint rejected
NaN rejected
+Infinity rejected
-Infinity rejected
compact encoding
no insignificant whitespace
no trailing newline
mediaType = application/json
```

Use this serializer for all M7-A runner-owned JSON artifacts.

## 5. Baseline Git basis

Define exactly:

```ts
type GateAGitObjectFormatV1 = "sha1" | "sha256";

interface GateABaselineGitBasisV1 {
  readonly schema: "gate-a-baseline-git-basis.v1";
  readonly gitObjectFormat: GateAGitObjectFormatV1;
  readonly baselineAuthority: RepositoryAuthorityRef;
  readonly carrier: {
    readonly kind: "git-bundle-v3";
    readonly bundle: ArtifactRef;
    readonly internalRef: "refs/turnlock/baseline";
    readonly prerequisiteObjectIds: readonly [];
  };
  readonly verification: ArtifactRef;
}

interface GateABaselineGitBasisVerificationV1 {
  readonly schema: "gate-a-baseline-git-basis-verification.v1";
  readonly gitObjectFormat: GateAGitObjectFormatV1;
  readonly bundle: ArtifactRef;
  readonly internalRef: "refs/turnlock/baseline";
  readonly prerequisiteObjectIds: readonly [];
  readonly expectedAuthority: RepositoryAuthorityRef;
  readonly restoredAuthority: RepositoryAuthorityRef;
  readonly closureObjectCount: number;
  readonly closureSetSha256: Sha256;
  readonly reachableClosureComplete: true;
  readonly standaloneRestoreVerified: true;
}
```

Require:

```text
expectedAuthority == restoredAuthority == RepositoryInspectionRef.baselineAuthority
```

`baselineGitBasis` is the `ArtifactRef` of the canonical
`GateABaselineGitBasisV1` JSON. It is not the raw bundle.

Use exactly these media types and path bindings:

```text
baselineGitBasis descriptor      application/json
verification record              application/json
raw bundle                       application/octet-stream

repositoryPath = null for all three
```

## 6. Closure identity and semantics

Define the exact closure fingerprint:

```text
ClosureSet =
all unique Git objects reachable from C under the M7-A closure semantics

sort ClosureSet by lowercase full OID ASCII lexicographic order

for each OID:
    resolve exact Git object type
    emit:
        type + SP + oid + LF

closureSetSha256 =
    SHA256(UTF8(concatenated emitted lines))
```

`closureObjectCount` equals the exact `ClosureSet` cardinality.

Define reachable closure exactly as:

```text
Closure(C)
=
C
+
all parent commits recursively
+
every tree recursively reachable from those commits
+
every nested tree
+
every blob
```

For tree mode `160000`:

```text
retain exact gitlink OID as candidate material
do NOT traverse into the referenced submodule commit
do NOT contact a submodule repository
```

No tag, note, stash, reflog, unrelated ref, remote-tracking ref, or unreachable
object belongs to `Closure(C)` merely because it exists locally.

## 7. Object acquisition architecture

Use exactly four conceptual repositories:

```text
SOURCE
→ read-only mutable source repository

ACQUISITION
→ isolated object database permitted to use authorized acquisition sources

CLOSURE
→ isolated object database containing only exact Closure(C)

VERIFICATION
→ new isolated empty object database populated only from the final bundle
```

Never hydrate, fetch, unshallow, configure, or mutate `SOURCE`.

Use allowed acquisition source classes in this exact order:

```text
1. source repository object database
   including repository-declared objects/info/alternates

2. explicitly declared promisor remotes

3. configured current-branch fetch/upstream source
   only when required to complete shallow ancestry
```

Forbid these acquisition sources:

```text
ambient GIT_ALTERNATE_OBJECT_DIRECTORIES
implicit origin fallback
arbitrary remotes
publication target solely because an object is missing
submodule remotes
URLs found in .gitmodules
server-added promisor remotes
guessed URLs
```

Always read the source repository with lazy fetching disabled.

### 7.1 Acquisition loop

Execute exactly:

```text
copy raw C into ACQUISITION
verify recomputed C OID

repeat:
    traverse exact graph from C in ACQUISITION
    with:
        no shallow boundary
        no replace objects
        no lazy fetch

    compute PRESENT and MISSING

    if MISSING empty:
        stop

    attempt missing-object acquisition from authorized sources
    in exact source-class order

    every acquired object's recomputed OID must equal the requested OID

    if no requested missing object becomes newly available:
        return baseline-git-closure-unavailable

    repeat
```

Extra objects returned by Git or server fetch mechanics may exist in
`ACQUISITION`. They do not become baseline objects unless they are members of
exact `Closure(C)`.

### 7.2 Shallow completion

Allow configured shallow-history acquisition only when:

```text
source repository is shallow

current symbolic branch has one explicit effective branch.<B>.remote

current symbolic branch has exactly one branch.<B>.merge

branch.<B>.merge is fully qualified under refs/heads/*
```

There is no implicit `origin`.

Fetch only in `ACQUISITION`. Remote advancement does not change baseline
authority. After acquisition, always recompute `Closure(C)`, never closure of
the remote tip.

## 8. Closure purification, bundle, and restore

After `Closure(C)` is complete, execute exactly:

```text
create CLOSURE as a new isolated same-object-format object database

for each exact ClosureSet OID:
    read raw object from ACQUISITION
    write raw object into CLOSURE
    require written OID == expected OID

re-traverse C in CLOSURE

require:
    no missing objects
    same closureObjectCount
    same closureSetSha256
    tree(C) == baselineAuthority.treeSha
```

Require `CLOSURE` to have:

```text
zero remotes
zero alternates
zero promisor configuration
zero shallow state
zero replace refs
zero worktree
zero index
```

Create the baseline bundle from `CLOSURE` with exactly:

```text
Git bundle v3

exactly one internal ref:
refs/turnlock/baseline -> C

zero prerequisites
same exact object format
no filter capability
```

Bundle bytes need not be deterministic. Once sealed, the exact produced bundle
bytes are immutable evidence for that inspection occurrence.

Restore the bundle into a new `VERIFICATION` repository that has:

```text
same object format
zero remotes
zero alternates
zero promisor configuration
zero shallow state
zero replace refs
zero lazy fetch path
```

Require:

```text
refs/turnlock/baseline == C
raw C readable
tree(C) == expected tree
Closure(C) complete
closureObjectCount identical
closureSetSha256 identical
```

Only after this succeeds may the baseline Git basis be considered valid.

## 9. Publication-target identity resolution

Define the success artifact exactly:

```ts
interface GateARepositoryPublicationTargetResolutionV1 {
  readonly schema:
    "gate-a-repository-publication-target-resolution.v1";

  readonly symbolicHeadRef: string;

  readonly remoteSelection:
    | "branch-push-remote"
    | "remote-push-default"
    | "branch-remote";

  readonly refSelection:
    | "remote-push-refspec"
    | "push-default-current"
    | "push-default-simple"
    | "push-default-upstream";

  readonly target: RepositoryPublicationTargetRef;
}
```

This artifact must not contain the local remote alias.

### 9.1 Push configuration dependency result

Require `inspectPushConfiguration` to expose Git-effective single-valued
configuration for:

```text
branch.<B>.pushRemote
remote.pushDefault
branch.<B>.remote
push.default
```

Require it to expose all effective values for the legitimately multi-valued:

```text
branch.<B>.merge
remote.<R>.push
```

The Dependency Contract owns Git config precedence and effective-value semantics
for single-valued configuration. M7-A does not reinterpret Git config-file
precedence.

### 9.2 Publication remote selection

Select remote alias `R` exactly:

```text
if branch.<B>.pushRemote exists:
    R = that value
else if remote.pushDefault exists:
    R = that value
else if branch.<B>.remote exists:
    R = that value
else:
    publication-target-unavailable
    reason = missing
    component = push-remote
```

There is no implicit `origin` fallback.

Treat the selected remote alias as ephemeral. Never retain it in durable target
identity or success evidence.

### 9.3 Effective push endpoint

Call exactly:

```text
resolveRemotePushEndpoints(repositoryPath, R)
```

Require exactly one effective endpoint:

```text
0 endpoints
→ missing / push-endpoint

>1 endpoints
→ ambiguous / push-endpoint
```

Classify the exact Git-resolved endpoint. Support only:

```text
https
ssh-uri
ssh-scp-like
```

Reject:

```text
http
git
file
local-path
remote-helper
unknown
```

Reject any endpoint classified as credential-bearing. Reject a URI query or
fragment.

Do not:

```text
strip .git
normalize provider paths
lowercase repository paths
translate scp syntax to ssh URI
merge HTTPS/SSH identities
resolve path components
```

`remoteEndpoint` is the exact credential-free Git-resolved effective endpoint.

Define exactly:

```text
repositoryIdentity =
"git-push-endpoint-sha256:" +
lowercaseHex(
    SHA256(
        UTF8(remoteEndpoint)
    )
)
```

Permit no network, API, or provider-specific repository identity lookup.

### 9.4 Push ref selection

If `remote.<R>.push` has one or more effective refspecs:

```text
require exactly one refspec
parse through DC parsePushRefspec
```

Require:

```text
force == false
deletion == false
wildcard == false

source ==
    "HEAD"
    OR exact symbolic current branch refs/heads/<B>

destination is fully qualified refs/heads/*
```

Map any force, deletion, wildcard, matching, multi-ref, unqualified, or
foreign-source refspec to:

```text
publication-target-unavailable
reason = unsupported-refspec
component = push-ref
```

Map a fully qualified destination outside `refs/heads/*` to:

```text
reason = non-branch-target
component = push-ref
```

When accepted, require:

```text
refSelection = remote-push-refspec
target.refName = exact destination
```

### 9.5 `push.default` selection

If no `remote.<R>.push` refspec exists, use effective `push.default`. If absent,
treat it as `simple`.

Apply exactly:

```text
current:
    target = refs/heads/<B>

simple:
    if selected push remote differs from branch.<B>.remote:
        target = refs/heads/<B>
    else:
        require exactly one branch.<B>.merge
        require it equals refs/heads/<B>
        target = refs/heads/<B>

upstream or tracking:
    require selected push remote == branch.<B>.remote
    require exactly one branch.<B>.merge
    require branch.<B>.merge under refs/heads/*
    target = exact branch.<B>.merge
```

Apply the exact failure mapping:

```text
push.default = nothing
→ missing / push-ref

push.default = matching
→ unsupported-push-mode / push-ref

unknown push.default
→ unsupported-push-mode / push-ref

simple with absent upstream where central simple requires one
→ missing / push-ref

simple with mismatching upstream branch name
→ incompatible-upstream / push-ref

upstream/tracking with different push remote
→ incompatible-upstream / push-ref

upstream/tracking with absent merge ref
→ missing / push-ref

upstream/tracking with merge ref outside refs/heads/*
→ non-branch-target / push-ref
```

`push.autoSetupRemote` has no semantic effect on M7-A target identity. M7-A
never mutates Git config to establish an upstream.

## 10. Candidate materialization

Define exactly:

```ts
interface GateACandidateMaterializationV1 {
  readonly schema: "gate-a-candidate-materialization.v1";
  readonly gitObjectFormat: GateAGitObjectFormatV1;
  readonly rootTreeObjectId: string;
  readonly entries: readonly CandidateMaterializedEntryV1[];
}

type CandidateMaterializedEntryV1 =
  | {
      readonly pathBytesBase64url: string;
      readonly kind: "blob";
      readonly mode: "100644" | "100755";
      readonly content: ArtifactRef;
    }
  | {
      readonly pathBytesBase64url: string;
      readonly kind: "symlink";
      readonly mode: "120000";
      readonly content: ArtifactRef;
    }
  | {
      readonly pathBytesBase64url: string;
      readonly kind: "gitlink";
      readonly mode: "160000";
      readonly objectId: string;
    };
```

No directory entries occur. An empty repository is representable. Empty
directories are not.

### 10.1 Candidate path rules

`pathBytesBase64url` is:

```text
canonical unpadded RFC 4648 base64url
of the exact full raw Git path bytes
```

Use raw Git byte `0x2f` as the path separator. Reject:

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

Use `classifyGitMetadataPath` for metadata-equivalent detection.

Do not use:

```text
Unicode normalization
locale
filesystem separator semantics
realpath
case folding for general candidate collisions
host filesystem path normalization
```

Require exact paths to be unique. Reject leaf/prefix collisions. Order candidate
entries by decoded raw path bytes in unsigned bytewise lexicographic ascending
order.

### 10.2 Candidate content

For blob and symlink entries, require:

```text
content ArtifactRef
mediaType = application/octet-stream
repositoryPath = null
exact bytes
```

Symlink target bytes are content bytes. Never create filesystem symlinks.

For a gitlink, require:

```text
mode = 160000
exact objectId
no ArtifactRef content
no submodule resolution
```

### 10.3 Candidate tree projection

Define exactly:

```ts
interface GateACandidateTreeProjectionVerificationV1 {
  readonly schema:
    "gate-a-candidate-tree-projection-verification.v1";

  readonly gitObjectFormat: GateAGitObjectFormatV1;
  readonly materialization: ArtifactRef;
  readonly computedRootTreeObjectId: string;
  readonly roundTripVerified: true;
}
```

Project through an isolated object database with:

```text
no worktree
no index
no filters
```

After `buildTree`, call `listTreeEntries` and reconstruct the manifest. Require
byte-for-byte canonical materialization equality and exact root-tree identity.

### 10.4 C0 construction

Derive `C0` only from the exact independently verified baseline tree:

```text
read exact verified tree(C)
list exact raw tree entries
validate paths and modes
seal every blob/symlink exact content
retain gitlink OIDs
construct canonical GateACandidateMaterializationV1
seal materialization
project materialization back to Git tree
require projected root == baselineAuthority.treeSha
seal tree-projection verification
construct SealedCandidateMaterializationRef:
    runId = inspection runId
    parentCandidateId = null
    producedByRepairIntentId = null
```

Never derive `C0` from mutable worktree bytes.

## 11. Exact candidate patching

Define exactly:

```ts
interface GateAExactCandidatePatchV1 {
  readonly schema: "gate-a-exact-candidate-patch.v1";
  readonly sourceMaterialization: ArtifactRef;
  readonly operations: readonly CandidateEntryReplacementV1[];
}

interface CandidateEntryReplacementV1 {
  readonly pathBytesBase64url: string;
  readonly before: CandidateEntryStateV1 | null;
  readonly after: CandidateEntryStateV1 | null;
}

type CandidateEntryStateV1 =
  | {
      readonly kind: "blob";
      readonly mode: "100644" | "100755";
      readonly content: ArtifactRef;
    }
  | {
      readonly kind: "symlink";
      readonly mode: "120000";
      readonly content: ArtifactRef;
    }
  | {
      readonly kind: "gitlink";
      readonly mode: "160000";
      readonly objectId: string;
    };
```

### 11.1 Patch canonicality and admissibility

Require:

```text
canonical runner JSON
>= 1 operation
operations ordered by canonical decoded path order
one operation per exact path
no before == after no-op
sourceMaterialization exact source candidate
every before checked against the same immutable source materialization
all preimages checked before any mutation
```

If any preimage mismatches, reject the entire patch as an
implementation/process/integrity failure.

Never:

```text
fuzzy match
offset
context repair
3-way merge
manual conflict resolution
partial patch application
```

Represent operations exactly as:

```text
rename = delete + create
copy = create
chmod/type change = single replacement
```

Patch `after` content is already sealed by exact `ArtifactRef`. Permit no inline
arbitrary file bytes.

### 11.2 CandidateConstructionRequest algorithm

Consume exactly:

```text
request.runId
request.sourceCandidate
request.repairIntent
```

Require:

```text
request.runId ==
request.sourceCandidate.runId ==
request.repairIntent.runId

request.repairIntent.candidateId ==
request.sourceCandidate.candidateId
```

Use exactly:

```text
request.repairIntent.approvedPatch
```

Accept no separately supplied patch, override, or fallback.

Execute exactly:

```text
read exact source candidate materialization
read exact RepairIntent approved patch
validate source binding
validate all operations/preimages
apply all replacements simultaneously to immutable source copy
validate resulting candidate path/type invariants
construct canonical result materialization
seal resulting content refs as already required
project result to Git tree
round-trip verify
seal result materialization and verification
construct CandidateSealResult
```

Require successful result bindings:

```text
sealedCandidate.runId == request.runId

sealedCandidate.parentCandidateId ==
    request.sourceCandidate.candidateId

sealedCandidate.producedByRepairIntentId ==
    request.repairIntent.repairIntentId
```

One `RepairIntent` may produce at most one admitted `CandidateRevision`. M2
remains the authoritative enforcement boundary.

## 12. Evidence ordering

Define exact `ArtifactRef` equality as structural equality over:

```text
artifactId
sha256
byteLength
mediaType
repositoryPath
```

For every M7-A ordered duplicate-free array:

```text
construct exact source sequence
scan left-to-right
retain first occurrence
drop later exact-ArtifactRef duplicates
```

Never deduplicate only by SHA.

Define `candidateContentArtifacts(M)` exactly as:

```text
iterate candidate entries in canonical candidate-path order

blob    → append content
symlink → append content
gitlink → append nothing

then exact-ArtifactRef first-occurrence dedup
```

Require exact baseline candidate evidence:

```text
sealedBaselineCandidate.materializationEvidence =
[
  ...candidateContentArtifacts(C0),
  baselineCandidateTreeProjectionVerification
]
```

Require exact repository-inspection evidence:

```text
RepositoryInspectionRef.evidence =
[
  publicationTargetResolution,
  baselineBundle,
  baselineGitBasisVerification
]
```

Require descriptor bindings:

```text
baselineGitBasis.carrier.bundle ==
RepositoryInspectionRef.evidence[1]

baselineGitBasis.verification ==
RepositoryInspectionRef.evidence[2]
```

For source candidate `P`, `RepairIntent R`, resulting materialization `M`, and
projection verification `V`, require:

```text
sealedCandidate.materializationEvidence =
[
  P.materialization,
  R.approvedPatch,
  ...candidateContentArtifacts(M),
  V
]
```

Then apply exact-`ArtifactRef` first-occurrence deduplication. Do not recursively
include `P.materializationEvidence`. Do not separately add patch `after` content
references; resulting candidate content ordering is authoritative for result
content evidence.

## 13. Publication-successor projection

Define exactly:

```ts
interface PublicationSuccessorProjectionRequestV1 {
  readonly repositoryInspection: RepositoryInspectionRef;
  readonly candidate: CandidateRevisionRef;
}

interface PublicationSuccessorProjectionResultV1 {
  readonly projection: ArtifactRef;
  readonly successorAuthority: RepositoryAuthorityRef;
}

interface GateAGitPublicationSuccessorProjectionV1 {
  readonly schema:
    "gate-a-git-publication-successor-projection.v1";

  readonly algorithm:
    "baseline-single-parent.v1";

  readonly gitObjectFormat:
    GateAGitObjectFormatV1;

  readonly baselineAuthority:
    RepositoryAuthorityRef;

  readonly candidateMaterialization:
    ArtifactRef;

  readonly candidateTreeObjectId:
    string;

  readonly candidateTreeProjectionVerification:
    ArtifactRef;

  readonly mode:
    | "reuse-baseline-commit"
    | "synthetic-single-parent";

  readonly successorAuthority:
    RepositoryAuthorityRef;

  readonly syntheticCommitBody:
    ArtifactRef | null;
}

interface MaterializeProjectedSuccessorRequestV1 {
  readonly repositoryInspection: RepositoryInspectionRef;
  readonly candidate: CandidateRevisionRef;
  readonly projection: ArtifactRef;
}

interface MaterializedProjectedSuccessorV1 {
  readonly authority: RepositoryAuthorityRef;
  readonly repositoryPath: string;
}
```

`repositoryPath` is operational only and never durable identity.

### 13.1 Deterministic successor algorithm

Let:

```text
C  = baselineAuthority.commitSha
TC = baselineAuthority.treeSha
TM = exact projected candidate tree
```

If:

```text
TM == TC
```

then require:

```text
mode = reuse-baseline-commit
successorAuthority = baselineAuthority
syntheticCommitBody = null
```

Otherwise construct these exact raw commit bytes:

```text
tree <TM>
parent <C>
author TURNLOCK Gate A Runner <turnlock-gate-a-runner@turnlock.invalid> <baseline_committer_unix_seconds> +0000
committer TURNLOCK Gate A Runner <turnlock-gate-a-runner@turnlock.invalid> <baseline_committer_unix_seconds> +0000

TURNLOCK Gate A publication
```

The final message includes exactly one trailing LF. Headers occur exactly in
this order:

```text
tree
parent
author
committer
```

Add no header. Do not sign. Use no current clock, run ID, or candidate ID.

Seal the exact raw commit bytes as:

```text
application/octet-stream
repositoryPath = null
```

Store exact type `commit` through the Git Dependency Contract. Require exact OID
readback. Set `successorAuthority.treeSha = TM`.

For identical:

```text
baseline authority
candidate materialization
Git object format
baseline committer timestamp
```

require the successor OID to be identical.

### 13.2 M7-A to M7-B boundary

Expose exactly these internal functions:

```ts
project_publication_successor(
  request: PublicationSuccessorProjectionRequestV1,
): Promise<PublicationSuccessorProjectionResultV1>

materialize_projected_successor(
  request: MaterializeProjectedSuccessorRequestV1,
): Promise<MaterializedProjectedSuccessorV1>
```

The `RepositoryInspectionRef` supplied for publication-successor projection is
the exact retained preflight inspection projected as:

```text
GateARunSnapshot.repositoryInspection
```

M1 passes that exact retained value through `PublicationPreparationRequest`.

M7 must reject an invocation whose `repositoryInspection` is not the exact
retained inspection for the `GateARun`, even if its `baselineAuthority`,
`publicationTarget`, or referenced artifact bytes appear equivalent.

M7 does not rediscover or reconstruct the preflight inspection from mutable
repository state.

`project_publication_successor` performs:

```text
NO network
NO remote observation
NO mutable repository reread
NO current clock
NO randomness
```

`materialize_projected_successor` realizes an already-derived projection. It
must verify:

```text
projection.baselineAuthority ==
repositoryInspection.baselineAuthority

projection.candidateMaterialization ==
candidate.materialization

materialized authority ==
projection.successorAuthority
```

It may not derive a different successor.

M7-B owns `P` and `P <= T`. M7-A owns `T`.

## 14. Repository-inspection operational causes

Define the exact root union:

```ts
type GateARepositoryInspectionOperationalCauseV1 =
  | RepositoryHeadUnavailableCauseV1
  | RepositoryFormatUnsupportedCauseV1
  | PublicationTargetUnavailableCauseV1
  | BaselineGitClosureUnavailableCauseV1
  | BaselineGitCommitUnsupportedCauseV1
  | BaselineCandidateUnsupportedCauseV1;
```

Every member has exactly:

```text
schema =
"gate-a-repository-inspection-operational-cause.v1"
```

Serialize every cause descriptor as canonical runner JSON with:

```text
mediaType = application/json
repositoryPath = null
```

Construct every resulting `NonRecoveryOperationalCauseRefV1` with exactly:

```text
producer = "repository-control"

resolutionContracts = [
  { kind: "request-operational-recheck" }
]
```

No execution-replacement resolution contract is lawful.

### 14.1 Head and format causes

Define exactly:

```ts
interface RepositoryHeadUnavailableCauseV1 {
  readonly schema:
    "gate-a-repository-inspection-operational-cause.v1";
  readonly kind: "repository-head-unavailable";
  readonly reason:
    | "not-git-repository"
    | "unborn-head"
    | "detached-head";
}

interface RepositoryFormatUnsupportedCauseV1 {
  readonly schema:
    "gate-a-repository-inspection-operational-cause.v1";
  readonly kind: "repository-format-unsupported";
  readonly observedObjectFormat: string;
}
```

For both, require:

```text
basisArtifacts = []
```

Support only:

```text
sha1
sha256
```

### 14.2 Publication-target cause and evidence

Define exactly:

```ts
interface PublicationTargetUnavailableCauseV1 {
  readonly schema:
    "gate-a-repository-inspection-operational-cause.v1";

  readonly kind:
    "publication-target-unavailable";

  readonly reason:
    | "missing"
    | "ambiguous"
    | "unsupported-endpoint"
    | "credential-bearing-endpoint"
    | "unsupported-refspec"
    | "unsupported-push-mode"
    | "incompatible-upstream"
    | "non-branch-target";

  readonly component:
    | "push-remote"
    | "push-endpoint"
    | "push-ref";
}
```

Allow only these reason/component combinations:

```text
missing / push-remote
missing / push-endpoint
missing / push-ref
ambiguous / push-endpoint
unsupported-endpoint / push-endpoint
credential-bearing-endpoint / push-endpoint
unsupported-refspec / push-ref
unsupported-push-mode / push-ref
incompatible-upstream / push-ref
non-branch-target / push-ref
```

Define the failure evidence exactly:

```ts
interface GateARepositoryPublicationTargetResolutionFailureV1 {
  readonly schema:
    "gate-a-repository-publication-target-resolution-failure.v1";

  readonly symbolicHeadRef: string;

  readonly remoteSelection:
    | "branch-push-remote"
    | "remote-push-default"
    | "branch-remote"
    | null;

  readonly failure: {
    readonly reason:
      PublicationTargetUnavailableCauseV1["reason"];
    readonly component:
      PublicationTargetUnavailableCauseV1["component"];
  };

  readonly effectivePushEndpointCount:
    number | null;

  readonly configuredPushRefspecCount:
    number | null;

  readonly pushDefaultMode:
    string | null;

  readonly endpointClass:
    | "https"
    | "ssh-uri"
    | "ssh-scp-like"
    | "http"
    | "git"
    | "file"
    | "local-path"
    | "remote-helper"
    | "unknown"
    | null;

  readonly candidateRefName:
    string | null;
}
```

It must not contain:

```text
remote alias
remote endpoint bytes
credentials
credential helper output
repositoryPath
raw config
```

For `publication-target-unavailable`, require:

```text
basisArtifacts =
[
  targetResolutionFailure
]
```

### 14.3 Closure-unavailable cause and evidence

Define exactly:

```ts
interface BaselineGitClosureUnavailableCauseV1 {
  readonly schema:
    "gate-a-repository-inspection-operational-cause.v1";
  readonly kind:
    "baseline-git-closure-unavailable";
  readonly gitObjectFormat:
    GateAGitObjectFormatV1;
  readonly baselineCommitObjectId:
    string;
}

interface GateABaselineGitClosureUnavailableEvidenceV1 {
  readonly schema:
    "gate-a-baseline-git-closure-unavailable-evidence.v1";
  readonly gitObjectFormat:
    GateAGitObjectFormatV1;
  readonly baselineCommitObjectId:
    string;
  readonly missingObjectCount:
    number;
  readonly missingObjectSetSha256:
    Sha256;
  readonly sourceClassesAttempted:
    readonly (
      | "source-object-database"
      | "declared-alternates"
      | "declared-promisor-remotes"
      | "configured-upstream-history"
    )[];
}
```

Compute the missing-set fingerprint exactly:

```text
sort missing lowercase full OIDs ASCII lexicographic
bytes = oid1 + LF + oid2 + LF + ...
SHA256(bytes)
```

Require:

```text
missingObjectCount > 0
basisArtifacts = [closureUnavailableEvidence]
```

Do not retain remote aliases, remote URLs, or transient network diagnostics.

### 14.4 Commit-unsupported cause

Define exactly:

```ts
interface BaselineGitCommitUnsupportedCauseV1 {
  readonly schema:
    "gate-a-repository-inspection-operational-cause.v1";
  readonly kind:
    "baseline-git-commit-unsupported";
  readonly reason:
    | "malformed-commit"
    | "invalid-committer-date";
  readonly gitObjectFormat:
    GateAGitObjectFormatV1;
  readonly commitObjectId:
    string;
}
```

Require:

```text
basisArtifacts =
[
  exact raw baseline commit body
]
```

The raw body has `mediaType = application/octet-stream` and
`repositoryPath = null`. Its exact Git object hash must equal `commitObjectId`.

### 14.5 Candidate-unsupported causes

Define exactly:

```ts
type BaselineCandidateUnsupportedCauseV1 =
  | UnsafeGitMetadataPathCauseV1
  | UnsupportedTreeEntryModeCauseV1
  | InvalidTreeStructureCauseV1;

interface UnsafeGitMetadataPathCauseV1 {
  readonly schema:
    "gate-a-repository-inspection-operational-cause.v1";
  readonly kind:
    "baseline-candidate-unsupported";
  readonly reason:
    "unsafe-git-metadata-path";
  readonly gitObjectFormat:
    GateAGitObjectFormatV1;
  readonly treeObjectId:
    string;
  readonly pathBytesBase64url:
    string;
}

interface UnsupportedTreeEntryModeCauseV1 {
  readonly schema:
    "gate-a-repository-inspection-operational-cause.v1";
  readonly kind:
    "baseline-candidate-unsupported";
  readonly reason:
    "unsupported-tree-entry-mode";
  readonly gitObjectFormat:
    GateAGitObjectFormatV1;
  readonly treeObjectId:
    string;
  readonly pathBytesBase64url:
    string;
  readonly observedMode:
    string;
}

interface InvalidTreeStructureCauseV1 {
  readonly schema:
    "gate-a-repository-inspection-operational-cause.v1";
  readonly kind:
    "baseline-candidate-unsupported";
  readonly reason:
    "invalid-tree-structure";
  readonly gitObjectFormat:
    GateAGitObjectFormatV1;
  readonly treeObjectId:
    string;
  readonly treePathBytesBase64url:
    string | null;
}
```

For all three require:

```text
basisArtifacts =
[
  exact raw failing tree body
]
```

The hash of the raw tree body must equal `treeObjectId`.

### 14.6 Inspection failure ordering

Return at most one cause from one repository inspection. Detect in this exact
order:

```text
1. repository/head validity
2. object format
3. publication target
4. baseline commit parse / committer date
5. baseline closure acquisition
6. baseline candidate/tree admissibility
7. bundle construction / independent restoration
8. C0 projection
```

At steps 7 and 8, treat contradiction after previously valid inputs as an
implementation/process/integrity failure, not an operational cause.

For candidate/tree admissibility, select the first failure under deterministic:

```text
root-first recursive traversal
children by canonical raw Git path-byte order
```

## 15. Repository inspection

Keep the NIB-S public boundary unchanged:

```ts
interface RepositoryInspectionRequest {
  readonly runId: GateARunId;
  readonly repositoryPath: string;
}
```

Execute the successful algorithm exactly:

```text
qualify Git dependency
inspect repository/head
resolve exact publication target
parse exact baseline commit
complete exact Closure(C)
purify closure
construct baseline bundle
independently restore/verify basis
derive C0 only from exact verified tree(C)
round-trip C0 back to exact tree(C)
seal all exact artifacts
construct RepositoryInspectionRef
```

Admit no authoritative baseline before every successful output artifact is
already sealed.

Require exact repository-inspection evidence:

```text
RepositoryInspectionRef.evidence =
[
  publicationTargetResolution,
  baselineBundle,
  baselineGitBasisVerification
]
```

Apply exact-`ArtifactRef` first-occurrence deduplication.

## 16. Replay, interruption, and failure taxonomy

Apply exactly:

```text
repository inspection
→ may observe different mutable repository/config state on a later retry before
  preflight admission
→ creates no campaign fact until M2 admits its exact result

candidate construction
→ exact immutable inputs
→ deterministic/replay-safe
→ no authoritative fact until candidate admission

successor projection
→ exact immutable inputs
→ deterministic/replay-safe

local resource/process failure before authoritative admission
→ invocation failure
→ no OperationalBlocker
→ retry from durable state allowed
```

An operationally blocked inspection consists only of the exact D3 cause union
in Section 14.

Implementation/process/integrity failure includes at least:

```text
DC returns impossible result under its contract
raw object hash mismatch
ArtifactStore returns invalid ArtifactRef
canonical serializer contract violation
purified closure loses object
closure fingerprint contradiction
bundle has prerequisite after complete closure
bundle has filter capability
offline restore changes C/tree/closure
C0 round-trip fails after input was accepted
successor object hash mismatch
```

Transient local failures include:

```text
disk full
temp directory failure
local process interruption
local resource exhaustion
CAS local write interruption
```

These do not become `GateARun` blockers.

Remote acquisition unavailability from an already-authorized acquisition source
may produce `baseline-git-closure-unavailable` when exact closure cannot be
completed.

## 17. Explicitly forbidden behaviors

M7-A must never:

```text
read candidate bytes from mutable worktree after baseline capture
hydrate or mutate SOURCE repository
use ambient alternates
use implicit origin fallback
probe arbitrary remotes
use publication target as arbitrary object source
fetch or update submodules
use Unicode/case/filesystem path normalization
materialize filesystem symlinks
fuzzy patch
3-way patch
partially apply a patch
make M7 repair semantic judgment
allow remote state to influence T
allow M7-B to recompute T
use current clock or randomness in T
use git commit/commit-tree as successor construction authority
use Git replace objects
permit implicit lazy fetch during ordinary object reads
create bundle prerequisites
create a filtered baseline bundle
retain temporary paths as durable identity
retain credentials in any artifact
order evidence by hash, artifactId, or filesystem discovery
```

## 18. Required invariants

M7-A must satisfy all of these:

```text
M7A-01 baseline authority is exact C + tree(C).

M7A-02 baselineGitBasis exists before preflight admission.

M7A-03 independently restored basis reconstructs exact C/tree(C).

M7A-04 baseline closure is standalone and has zero prerequisites.

M7A-05 C0 is derived only from verified baseline tree.

M7A-06 candidate manifest round-trips to exact Git tree.

M7A-07 candidate paths preserve exact Git path bytes.

M7A-08 gitlink target objects are never required for candidate closure.

M7A-09 RepairIntent approvedPatch is the only accepted repair patch.

M7A-10 all patch preimages are validated against one immutable source before
        any replacement is applied.

M7A-11 one successful candidate construction preserves exact source parent and
        RepairIntent provenance.

M7A-12 identical baseline/candidate/object-format inputs produce identical T.

M7A-13 remote predecessor/current state never influences T.

M7A-14 M7-B may materialize but never recompute or alter T.

M7A-15 inspection evidence arrays use exact NIB-defined order.

M7A-16 blocked inspection returns exactly one producer cause and exactly
        request-operational-recheck.

M7A-17 M7-A never creates OperationalBlocker identity.

M7A-18 no mutable repository path/config/ref forms retained baseline authority.

M7A-19 no credential-bearing endpoint becomes durable target identity.

M7A-20 Git dependency contradiction is integrity failure, never operator
        blocker.
```

## 19. Required edge cases

Cover all of these explicitly in NIB-T:

```text
non-Git directory
unborn symbolic branch
detached HEAD
sha1 repository
sha256 repository
unsupported object format
repository using declared alternates
partial clone with missing blob/tree
multiple promisor remotes
shallow repository with configured upstream
shallow repository without configured upstream
remote history advanced beyond C
C no longer obtainable from authorized sources
gitlink/submodule tree entry
symlink with non-UTF8 target bytes
non-UTF8 Git pathname
case-colliding paths
.git metadata-equivalent component
unsupported tree mode
empty repository tree representation where valid
duplicate file-content ArtifactRefs
patch delete/create/rename/copy/chmod/type change
patch preimage mismatch
candidate tree identical to baseline tree
candidate tree different from baseline tree
invalid baseline committer date
multiple effective push endpoints
credential-bearing endpoint
unsupported transport
remote push refspec with force/wildcard/delete
push.default current/simple/upstream/tracking/matching/nothing
simple upstream-name mismatch
upstream push-remote mismatch
restart before candidate admission
restart after successor projection artifact exists
```

## 20. Construction boundary

M7-A construction authority is closed by this Module Brief.

GREEN for M7-A remains forbidden until
`DC-GIT-CLI-GATE-A-REPOSITORY-CONTROL`
exists and realizes every required primitive with the exact contract consumed
here.

This Module Brief does not close M7-B publication, remote observation,
publication recovery, or executor-domain recovery behavior.
