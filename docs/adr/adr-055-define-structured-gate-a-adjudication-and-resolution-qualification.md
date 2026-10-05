---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Define structured Gate A adjudication and resolution qualification"
id: "ADR-055"
status: "proposed"
date: "2026-10-05"
decision_body_sha256: "fb47a19e559f2a7c57392286c68dd77ea646698ed86ac41a21eb0d508add649e"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-045"
    - "ADR-046"
    - "ADR-047"
    - "ADR-053"
  supersedes: []
  confirms:
    - "ADR-048"
    - "ADR-049"
    - "ADR-054"
governs:
  - "Gate A structured adjudication protocol evolution"
  - "Gate A structured resolution-qualification protocol evolution"
  - "Gate A supporting-role reviewer acquisition"
  - "Gate A role-aware deterministic cognitive-output validation"
  - "Gate A resolution challenge objectives"
  - "Gate A stale-protocol re-adjudication identity"
---

# ADR-055: Define structured Gate A adjudication and resolution qualification

## Context

ADR-045 defines the Gate A resolution boundary, including materiality,
refutation, uniquely derived correction, no-normative-impact, genuine product
underdetermination, genuine unresolved product-authority conflict, and exact
repair qualification.

ADR-046 makes protocol attempt validity checker-derived for roles whose output
has a deterministic protocol validator.

ADR-047 explicitly leaves these cognitive roles without deterministic output
validators:

```text
materiality-assessor
refutation-builder
discovery-classifier
derivation-builder
decision-necessity-challenger
repair-synthesizer
decision-projection
```

For those roles, protocol v3 through v6 therefore cannot truthfully classify a
completed structured response as `protocol-invalid`. The first completed
response is terminal regardless of whether its shape would satisfy a future
role-specific schema.

That boundary was correct when no role-specific deterministic protocol had been
justified. Construction of M5-B review-evidence adjudication and M5-C resolution
qualification now requires the missing protocol structure.

Without a protocol-owned structure, the runner would otherwise have to infer:

- how materiality-assessor output is represented;
- how absence of a refutation candidate differs from proof that a finding is
  true;
- how discovery classification is represented;
- what constitutes a unique-correction candidate;
- how no-normative-impact is represented positively;
- how genuine decision necessity is distinguished from inability to derive;
- how candidate-bound repair realization is represented;
- what exact objectives a hostile challenge must attempt;
- which reviewer profile executes supporting cognitive work.

Those choices affect hostile-review assurance and cannot be invented by an
M5 Module Brief or production implementation.

This is an assurance-protocol architecture problem. It is not TURNLOCK
product-semantic underdetermination.

## Discovery classification

```text
decision-required at the hostile-review assurance/protocol architecture layer;
resolved by this ADR;
no TURNLOCK product-semantic impact
```

## Decision

### Protocol v7 is the structured-adjudication evolution

The next hostile-review protocol evolution is:

```text
gate-a-campaign-protocol-v7
```

Its exact predecessor is the published protocol v6.

Published protocol bundles v1 through v6 and every immutable schema,
meta-schema, prompt, and protocol artifact they reference remain immutable.

Protocol v7 changes protocol identity `P`.

It does not change Gate A semantic subject `S`.

Protocol v7 introduces the protocol-owned structured contracts required for
post-review adjudication and resolution qualification.

### Review-evidence schema 5.0 remains the immutable campaign-record schema

Protocol v7 continues to bind the immutable:

```text
formal/reviews/meta-schemas/review-evidence-v5.schema.json
```

No review-evidence schema 6.0 is introduced by this decision.

Schema 5.0 remains the exact schema for hostile-review campaign records.

One schema-5 record continues to mean one real `ReviewCampaign`.

In particular:

```text
review_id
==
ReviewCampaignId
```

remains unchanged.

Protocol v7 MUST NOT create a synthetic ReviewCampaign merely to obtain a
writable repository record for later post-review evidence.

A repository-imported or already-projected campaign record remains immutable.

### Post-review adjudication supplements

Protocol v7 additionally introduces a separate immutable artifact schema:

```text
formal/reviews/schemas/finding-adjudication-supplement-v1.schema.json
```

for conceptually named:

```text
FindingAdjudicationSupplementV1
```

instances.

Projected supplement instances reside under:

```text
formal/reviews/supplements/<supplement-sha256>.json
```

A supplement is not a ReviewCampaign.

It therefore:

```text
does not have a ReviewCampaignId of its own
does not count toward minimum_independent_reviewers
does not create initial-reviewer acquisition obligations
does not create a new reviewed subject
does not supersede its source ReviewCampaign
does not retarget its source ReviewCampaign
does not rewrite its source review record
```

The supplement exists only to append an exact current-protocol adjudication of
one immutable original finding.

### Supplement semantic identity

The semantic key of one supplement is exactly:

```text
source review identity
+
source finding identity
+
validated substantive source-finding SHA-256
+
exact adjudicating protocol identity P
```

The source-finding SHA MUST first be recomputed from the exact original finding
through the canonical `hostile-finding-subject-v1` construction.

A mismatching SHA does not create another semantic key.

For one exact semantic key:

```text
zero supplements
OR
exactly one supplement
```

is valid.

Two different supplements for the same exact semantic key are duplicate
adjudications and invalid evidence.

The exact adjudicating ReviewCampaign is provenance only and MUST NOT become an
additional supplement identity dimension.

A supplement under a later exact `P` is not a duplicate of a supplement under an
earlier exact `P`.

### Exact supplement shape

The protocol-v7 supplement contract conceptually has exactly this shape:

```ts
interface FindingAdjudicationSupplementV1 {
  readonly supplement_schema_version:
    "1.0";

  readonly semantic_subject: {
    readonly selector:
      "gate-a-assurance-decomposition-v1";

    readonly sha256:
      Sha256;
  };

  readonly protocol: {
    readonly protocol_bundle:
      ArtifactReference;

    readonly review_packet:
      ArtifactReference;
  };

  readonly source_finding: {
    readonly review_id:
      ReviewCampaignId;

    readonly finding_id:
      string;

    readonly substantive_finding_sha256:
      Sha256;
  };

  readonly adjudicating_review_id:
    ReviewCampaignId;

  readonly supporting_executions:
    readonly ArtifactReference[];

  readonly effective_adjudication:
    EffectiveFindingAdjudicationV1;
}
```

The eventual JSON Schema may encode the exact lexical primitives through shared
or duplicated schema definitions, but it MUST preserve this exact semantic
shape and MUST NOT add free outcome authority.

`additionalProperties` is false for every closed object defined by the
supplement schema.

### Supplement authority binding

For one supplement require mechanically:

```text
source review exists

source review contains exactly source_finding.finding_id

recomputed hostile-finding-subject-v1 SHA
==
source_finding.substantive_finding_sha256

semantic_subject
==
exact current Gate A semantic subject S

protocol.protocol_bundle
==
exact protocol P governing this supplement

protocol.review_packet
==
exact current review packet used by this adjudication lineage

review_packet subject
==
semantic_subject

adjudicating_review_id identifies an exact current ReviewCampaign

adjudicating ReviewCampaign semantic subject
==
semantic_subject

adjudicating ReviewCampaign protocol
==
protocol.protocol_bundle
```

The adjudicating ReviewCampaign may be runner-produced or repository-imported.

Its role is current execution/protocol provenance.

It is not a writable owner of the supplement and is never mutated by supplement
projection.

### Evidence roots

Protocol v7 has exactly two lawful classes of post-review supporting-evidence
root.

A supporting execution belongs to exactly one of:

```text
A. schema-5 ReviewCampaign record supporting_executions[]
   for post-review work over findings native to that same runner-produced
   campaign while its root record is being constructed;

B. FindingAdjudicationSupplementV1 supporting_executions[]
   for append-only adjudication of a finding whose source campaign evidence is
   independently immutable from that new adjudication.
```

A supporting receipt MUST NOT belong to both roots.

Cross-campaign P7 adjudication always uses a supplement.

Adjudication of an immutable repository-imported campaign finding always uses a
supplement.

Historical schema-5 `re_adjudications[]` produced under protocol versions that
authorize them remain valid historical evidence.

New protocol-v7 cross-campaign adjudication MUST NOT emit a new schema-5
`re_adjudications[]` member as an alternative representation of the same
semantic adjudication.

### Supporting output evidence links

Whenever a later protocol-v7 packet depends on an earlier supporting cognitive
output, that dependency is represented by exact content identity over:

```text
producer execution receipt ArtifactRef
producer raw-output ArtifactRef
exact parsed producer output payload
```

The checker must establish all of the following:

```text
producer receipt belongs to the exact evidence root for this lineage

producer receipt has exactly one qualified attempt

producer receipt qualifying raw_output
==
referenced raw-output artifact identity

SHA-256 of exact sealed raw-output bytes
==
raw-output ArtifactRef.sha256

parsing the exact sealed raw-output bytes
==
embedded predecessor payload
```

The embedded payload does not replace the sealed raw evidence.

The raw-output `ArtifactRef.sha256` identifies the exact sealed model-produced
bytes.

A canonical semantic-object hash inside a packet identifies the canonical JSON
payload required by that packet contract.

These identities MUST NOT be conflated.

### Runtime content identity and repository projection

Runner-owned supporting artifacts are content-addressed before repository
projection.

Their runtime identity is the exact sealed `ArtifactRef`, including:

```text
artifactId = "sha256:" + sha256
exact sha256
exact byteLength
exact mediaType
repositoryPath = null
```

Repository `{path, sha256}` references are material locators for those exact
bytes.

Repository projection MUST NOT:

```text
rewrite bytes
normalize model output
repair JSON
change encoding
change SHA
create a second semantic evidence identity
```

At final repository validation, the checker reads exact projected bytes,
validates the declared SHA, and reconstructs the corresponding runtime
content-addressed identity required by that artifact class.

Location may change from CAS-only runtime storage to repository projection.

Content identity never changes.

### Durable negative semantic results

A schema-valid role result such as:

```text
not-established
```

is a qualified semantic result.

It is not absence of evidence, a technical failure, a protocol-invalid
completion, or authorization for semantic retry.

Its durable evidence remains the exact qualified supporting receipt and exact
sealed raw output in the lineage DAG.

If retry policy ends without a qualified protocol attempt, no conforming
execution receipt is manufactured.

Operational history remains runner history and the applicable operator path is
used.

### Revision evidence is append-only

A semantic closure revision never replaces the candidate or challenge that
caused it.

Revision ordinal `0` has no prior closure.

Revision ordinal `1` binds exact evidence for:

```text
prior producer receipt/output
+
prior hostile challenge receipt/output
```

and the checker verifies that the prior challenge packet was itself bound to the
exact prior candidate.

Thus:

```text
C0
→ H0
→ C1
→ H1
```

is a cryptographically linked evidence graph.

It is not four unrelated executions.

No revision ordinal greater than `1` is valid.

### Supporting evidence graph closure

For each protocol-v7 evidence root, the checker requires:

```text
every supporting receipt belongs to exactly one valid finding lineage

every predecessor receipt/output edge resolves exactly

every referenced output equals that execution's exact qualified raw output

every packet subject belongs to the exact semantic subject and protocol
required by that lineage

all semantic predecessor edges originate from qualified attempts only

protocol-invalid and technical-failure attempts may remain receipt history
but are never semantic DAG predecessors

the supporting dependency graph is acyclic

every supporting receipt is reachable from exactly one valid lineage root
```

No orphan supporting execution is valid evidence.

No cross-finding, cross-subject, or cross-protocol predecessor edge is valid.

### No duplicate logical execution for one exact semantic packet

For protocol v7, two distinct supporting logical execution receipts with the
same exact:

```text
role
+
input.packet content identity
```

inside one finding lineage are invalid evidence.

A retry of that exact semantic input belongs inside the same logical execution
receipt.

A legitimate semantic revision has a different packet because the packet binds
the exact prior candidate, exact prior challenge, and revision ordinal.

The same rule applies to exact challenge packets.

### Effective finding adjudication

A supplement MUST NOT contain a free v5-style `status` / `disposition` override.

Its `effective_adjudication` is exactly one of:

```text
qualified-non-material
qualified-refutation
surviving-material
```

No other supplement effective state exists.

The model never emits one of those final effective states directly.

They are mechanically projected from the exact qualified supporting DAG.

### Qualified non-material

Conceptually:

```ts
interface QualifiedNonMaterialV1 {
  readonly kind:
    "qualified-non-material";

  readonly materiality_assessment_execution_receipt:
    ArtifactReference;

  readonly materiality_challenge_execution_receipt:
    ArtifactReference;
}
```

The checker requires that the cited exact assessment has:

```text
all seven materiality axes == false
```

and that the exact required hostile materiality challenge:

```text
is bound to that assessment
uses the exact protocol-owned challenge contract
has objections == []
```

Only then is the effective finding non-material and therefore non-blocking for
Gate A.

No free `material = false` field exists.

### Qualified refutation

Conceptually:

```ts
interface QualifiedRefutationV1 {
  readonly kind:
    "qualified-refutation";

  readonly materiality_assessment_execution_receipt:
    ArtifactReference;

  readonly refutation_execution_receipt:
    ArtifactReference;

  readonly refutation_challenge_execution_receipt:
    ArtifactReference;
}
```

The checker requires:

```text
positive materiality
+
exact refutation-candidate output
+
exact hostile refutation challenge bound to that candidate
+
challenge objections == []
```

Only then may the exact finding cease blocking through refutation.

The model never emits `status = refuted`.

### Surviving material

Conceptually:

```ts
interface SurvivingMaterialV1 {
  readonly kind:
    "surviving-material";

  readonly materiality_assessment_execution_receipt:
    ArtifactReference;

  readonly refutation_exhaustion_terminal_receipt:
    ArtifactReference;
}
```

This variant requires:

```text
positive materiality
+
lawfully exhausted refutation path
+
no qualified refutation
```

where lawful exhaustion is exactly the mandatory bounded-revision meaning
defined by this ADR.

Operational inability before lawful M5-B completion does not manufacture a
surviving-material supplement.

In that case no completed current adjudication supplement is projected and the
applicable operator path remains authoritative.

### Exactly two non-blocking overlay states

A supplement can make a finding non-blocking only through exactly:

```text
qualified-non-material
OR
qualified-refutation
```

Every other terminal protocol-v7 resolution lineage retains:

```text
effective_adjudication.kind
=
surviving-material
```

In particular none of the following independently makes a material finding
non-blocking:

```text
UniqueCorrection
qualified RealizationScope
qualified RepairRealization
RepairIntent
already-realized repair claim
qualified NoNormativeImpact
DecisionRequest
SemanticBlocker
OPERATOR-ACTION-REQUIRED
downstream cause marked resolved
```

`no-normative-impact` is not non-materiality.

A qualified repair is not a refutation.

A Decision Request is not finding closure.

An operator path is not finding closure.

### Effective overlay selection

For each original finding applicable to the current exact subject `S`, let `P`
be the exact current protocol.

Find the supplements whose exact semantic key names that original finding and
exact `P`.

Require:

```text
count > 1
→ evidence integrity failure
```

When exactly one current-P supplement exists:

```text
effective Gate A adjudication
=
supplement.effective_adjudication
```

When no current-P supplement exists and:

```text
source campaign protocol == current P
```

use the source campaign finding's native materiality/status/disposition.

When no current-P supplement exists and:

```text
source campaign protocol != current P
```

the finding lacks required current-protocol adjudication and remains blocking.

Thus a protocol change never erases a historical finding merely because the old
record is stale.

### Same-protocol overlay

A source finding whose source campaign already uses exact current `P` may also
receive one supplement when later append-only post-review adjudication must
change its effective current qualification without rewriting the immutable source
record.

This permits an immutable current campaign finding to become effectively:

```text
qualified-non-material
```

or:

```text
qualified-refutation
```

only through the exact positive protocol-v7 qualification path.

It does not permit arbitrary status replacement.

### Supplement projection terminality

A supplement is projected only as an immutable closed artifact.

It MUST NOT be projected while:

```text
a required materiality/refutation closure execution is pending
a mandatory closure revision is pending
a required hostile challenge is pending
a supporting logical execution represented by that supplement is unresolved
```

Its exact M5-C/M5-D projection readiness point remains construction-owned, but a
projected supplement's `supporting_executions[]` MUST form a closed evidence DAG.

For a surviving-material finding, later M5-C qualification products may remain
part of the same closed audit lineage without changing
`effective_adjudication.kind`.

### Historical compatibility

Protocol-v1 through protocol-v6 evidence retains its historical interpretation.

Existing schema-5 campaign records and historical `re_adjudications[]` are not
rewritten or reinterpreted merely because protocol v7 exists.

The immutable:

```text
formal/reviews/meta-schemas/review-evidence-v5.schema.json
```

is not modified.

P7 extends append-only post-review evidence through a separate supplement
artifact rather than changing the meaning of historical campaign records.

### Execution receipts advance to schema 4.0

Execution receipt schema `3.0` is immutable.

Its current contract structurally forbids `protocol-invalid` for the seven roles
that ADR-047 classified as lacking deterministic output validators.

Protocol v7 therefore requires a new execution receipt schema:

```text
execution-receipt-v4.schema.json
```

Receipt v4 preserves the existing attempt model:

```text
technical-failure
protocol-invalid
qualified
```

but permits `protocol-invalid` for every current protocol-v7 cognitive role
whose sealed output can now be validated deterministically.

For every deterministically validated role:

```text
technical-failure
=
no completed semantic response
AND raw_output == null
AND protocol_errors == []

protocol-invalid
=
completed response exists
AND deterministic protocol validation fails
AND raw_output != null
AND protocol_errors non-empty

qualified
=
completed response exists
AND deterministic protocol validation succeeds
AND raw_output != null
AND protocol_errors == []
```

A schema-valid or otherwise protocol-valid semantic result is terminal.

A runner MUST NOT retry a protocol-valid result because the content is
inconvenient, unfavorable, inconclusive, or operationally undesirable.

### Current protocol-v7 cognitive roles

Protocol v7 retains these current cognitive roles:

```text
initial-reviewer
materiality-assessor
refutation-builder
challenge
discovery-classifier
derivation-builder
decision-necessity-challenger
repair-synthesizer
```

`decision-projection` is not a current protocol-v7 cognitive role.

Historical protocol artifacts and receipts that name `decision-projection`
remain valid under the exact protocol version that published them.

Protocol v7 does not rewrite historical protocol schemas.

A qualified Decision Request is projected mechanically from qualified decision
necessity and exact current provenance. No LLM is required merely to rewrite
that already-qualified meaning into a Decision Request artifact.

### Structured adjudication packet

Protocol v7 introduces:

```text
formal/reviews/schemas/adjudication-packet-v1.schema.json
```

The packet is a strict discriminated union over the exact supporting cognitive
task being performed.

The packet contains all semantic bytes the selected cognitive execution is
allowed to inspect.

No hidden repository, artifact-store, mutable-workspace, scheduler, prior-model,
or ambient contextual input is permitted.

Every semantic object embedded in an adjudication packet is self-contained and
content-bound by:

```text
selector
sha256
payload
```

where:

```text
sha256
=
SHA-256 of the canonical JSON payload bytes
```

The model does not establish this binding. The runner constructs it
mechanically and the checker validates it.

The packet task variants required by this ADR are:

```text
materiality-assessment
refutation
discovery-classification
unique-correction-derivation
realization-scope-derivation
repair-realization
```

`decision-necessity-challenger` does not consume an adjudication packet.
It consumes the canonical challenge packet with:

```text
challenge_kind = decision-necessity
```

### Structured adjudication output

Protocol v7 introduces:

```text
formal/reviews/schemas/adjudication-output-v1.schema.json
```

It is a strict discriminated union over the current producer roles and task
variants.

The output carries only model-produced semantic candidate material.

It MUST NOT duplicate externally authoritative identities merely so that the
model can restate them.

In particular, packet identity, protocol identity, current candidate identity,
campaign identity, and receipt identity are established by runner provenance
and exact packet binding rather than by trusting model-copied fields.

### Materiality output

`materiality-assessor` output contains exactly the accepted seven materiality
axes plus rationale:

```text
authority_or_upstream_decision
claim_structure
normative_provenance
modality_or_assurance_domain
coverage_or_residual_assurance
interaction_scope
candidate_model_authorization
rationale
```

It MUST NOT contain a free `material` boolean.

Materiality remains mechanically derived:

```text
material
=
OR(
  authority_or_upstream_decision,
  claim_structure,
  normative_provenance,
  modality_or_assurance_domain,
  coverage_or_residual_assurance,
  interaction_scope,
  candidate_model_authorization
)
```

If at least one axis is true, the finding is material.

If all seven axes are false, non-material closure still requires the accepted
hostile materiality challenge path.

### Refutation output

`refutation-builder` output has exactly two semantic result classes:

```text
refutation-candidate
not-established
```

A `refutation-candidate` uses the existing structured refutation grounds and
contains:

```text
ground
attacked_premise_or_inference
evidence_references
argument
counterexample_disposition
```

`not-established` means only that the execution did not establish a refutation
candidate.

It MUST NOT be interpreted as:

```text
finding is true
```

Failure to establish a refutation remains distinct from proving the finding.

### Discovery classification is routing evidence, not outcome authority

`discovery-classifier` produces one earliest unresolved cause plus one or more
atomic classification statements.

The exact discovery layers are:

```text
normative-contract
decision-history
formal-model-or-analysis
verification-or-qualification-evidence
architecture-or-implementation
integration-or-conformance
repository-governance-or-documentation
```

Each atomic statement has exactly one semantic disposition:

```text
derived-from-existing-authority
decision-required
no-normative-impact
authority-conflict-or-uncertain
```

Different statements from one investigation may have different dispositions.

A discovery classification is a structured routing hypothesis.

It does not independently authorize:

```text
repair
Decision Request
finding refutation
Gate A readiness
external outcome
```

Those consequences require their own accepted positive qualification paths.

### Decision-required discovery candidate

A `decision-required` discovery candidate must positively identify either:

```text
product-underdetermination
```

or:

```text
product-authority-conflict
```

For product underdetermination it must identify at least two materially distinct
authority-compatible semantic alternatives and an argument that current
authority does not select one.

For product-authority conflict it must identify at least two incompatible
current controlling product-authority positions and an analysis showing that
accepted precedence, amendment, or supersession rules do not already resolve
the conflict.

A statement equivalent to:

```text
the model could not derive the answer
```

is not a decision-required candidate.

### Authority-conflict-or-uncertain discovery candidate

`authority-conflict-or-uncertain` distinguishes exactly these reason kinds:

```text
authority-conflict
unstated-premise
missing-authority
uncertain-provenance
```

This classification does not by itself authorize `DECISION-REQUIRED`.

Unstated premise, missing authority, provenance uncertainty, insufficient
evidence, or inability to conclude are epistemic/operational conditions unless
a separate qualified decision-necessity path establishes genuine product
underdetermination or genuine unresolved product-authority conflict.

### Unique correction is semantic, not candidate-bound

A `unique-correction-derivation` task may produce:

```text
unique-correction-candidate
not-established
```

A unique-correction candidate contains:

```text
correction_requirements
derivation_claims
alternatives_considered
uniqueness_argument
```

The correction requirements state the semantic postconditions uniquely required
by existing authority.

They are not repository patch operations.

They are not file paths.

They are not implementation choices.

A qualified UniqueCorrection is bound to the exact semantic resolution subject,
exact current `S`, exact current `P`, exact finding provenance, and exact
adjudication basis from which it was qualified.

It is not semantically bound to one physical candidate merely because a later
repository realization is.

`not-established` means only that a unique correction was not established.

It MUST NOT be converted automatically into `DECISION-REQUIRED`.

### Unique correction requires hostile derivation challenge

A unique-correction candidate is not qualified merely because
`derivation-builder` emitted it.

It must survive a fresh hostile challenge:

```text
challenge_kind = derivation
```

with the exact protocol-owned derivation objectives.

Only a derivation candidate whose required challenge closes without surviving
objections is a qualified UniqueCorrection.

### Realization scope is candidate-bound

After a UniqueCorrection is qualified, physical realization authority is
derived separately for the exact current candidate.

A `realization-scope-derivation` task produces a candidate scope containing:

```text
readable_paths
writable_paths
completeness_argument
minimal_write_authority_argument
```

Paths are exact raw candidate path identities.

No glob, wildcard, directory prefix, fuzzy selector, semantic path expression,
or mutable-workspace lookup is permitted.

Mechanically:

```text
writable_paths subset-of readable_paths
```

A writable path set is a maximum physical authority boundary.

It is not itself a patch.

The scope MUST NOT grant write authority to controlling product-authority
artifacts merely to make an automatic repair possible.

If changing controlling product authority is required, automatic repair is not
authorized by the UniqueCorrection path.

A realization-scope candidate must itself survive:

```text
challenge_kind = derivation
```

before it becomes qualified realization authority.

### Candidate advance does not rebind an old physical scope

When the current candidate changes while `(S, P)` remains unchanged, an already
qualified semantic UniqueCorrection may remain applicable.

An old candidate-bound RealizationScope does not automatically transfer to the
new candidate.

The new current candidate requires fresh candidate-bound realization-scope
qualification before new repair synthesis.

No scope rebasing or silent retargeting is permitted.

### Repair realization is requirement-complete

`repair-synthesizer` operates only after:

```text
qualified UniqueCorrection
+
qualified candidate-bound RealizationScope
+
exact current candidate view
```

Its structured result has exactly two top-level classes:

```text
repair-realization-candidate
not-established
```

A repair-realization candidate contains:

```text
requirement_realizations
operations
```

Every correction requirement appears exactly once in
`requirement_realizations`.

Each requirement realization is exactly one of:

```text
already-realized
patch-realized
```

`already-realized` is a positive candidate-bound claim that the exact current
candidate already satisfies that exact qualified correction requirement.

`patch-realized` names the proposed repair operations that would realize that
requirement.

The model does not construct authoritative `ArtifactRef` values or trusted
preimages.

The runner derives physical before-state from the exact current candidate view
and seals proposed after-state bytes mechanically.

### Empty automatic RepairIntent is forbidden

For one repair-realization candidate:

```text
operations == []
```

if and only if every correction requirement is classified
`already-realized`.

A fully already-realized candidate produces no empty patch and no empty
RepairIntent.

If at least one requirement is `patch-realized`, at least one exact repair
operation is required.

A qualified fully-already-realized realization satisfies the candidate-bound
realization obligation only.

It does not:

```text
refute the finding
make the finding non-material
change finding status
declare Gate A ready
```

### Repair challenge

A repair-realization candidate must survive:

```text
challenge_kind = repair
```

against the exact current candidate-bound realization.

The repair challenge attempts to falsify both:

- positive `already-realized` claims;
- proposed patch realization.

A qualified automatic RepairIntent may be constructed only after the exact
repair realization survives this challenge.

### No normative impact is a positive qualification

`no-normative-impact` is not synonymous with:

```text
derived-from-existing-authority
```

and is not synonymous with:

```text
finding non-material
```

A no-normative-impact candidate positively claims that resolving the identified
issue does not require:

```text
new product authority
changed product authority
selection among multiple product meanings
change to accepted observable product obligations
```

It requires its own hostile challenge:

```text
challenge_kind = normative-impact
```

A qualified no-normative-impact result does not by itself prove that one exact
automatic correction can be generated.

If no unique automatic correction is established, a qualified
no-normative-impact result may prevent fabrication of `DECISION-REQUIRED` while
the remaining inability is handled through the applicable non-semantic or
operator path.

### Decision necessity is a positive qualification

`DECISION-REQUIRED` is authorized only for:

```text
genuine product-semantic underdetermination
or
genuine unresolved product-authority conflict
```

Before decision necessity may qualify, the protocol must attempt the existing
authority derivation path.

Failure of derivation is not sufficient.

The exact decision-necessity candidate is challenged by a fresh logical
execution with role:

```text
decision-necessity-challenger
```

using:

```text
challenge_kind = decision-necessity
```

and the same canonical challenge-output contract.

This specialized role is the hostile challenger for decision necessity.

There is no second generic challenge after a qualified
`decision-necessity-challenger` execution.

A Decision Request is projected mechanically only after the decision-necessity
candidate survives its required hostile challenge.

### Closure revision is mandatory when current and operationally admissible

The existing:

```text
max_closure_revisions = 1
```

remains in protocol identity.

Protocol v7 strengthens the procedural meaning of that bound.

When an initial revision-eligible closure candidate receives one or more
qualified hostile objections, exactly one revision execution is REQUIRED when:

```text
the exact closure subject remains current
AND
the exact protocol identity remains current
AND
automatic execution of that revision remains operationally admissible
```

The runner, scheduler, coding agent, operator, model preference, cost,
latency, expected outcome, finding severity, or perceived strength of the
objections MUST NOT decide whether to skip that required revision.

Without this rule, two otherwise identical conforming runs could diverge only
because one runner elected to abandon a challenged closure while another used
the available revision. Protocol v7 forbids that hidden orchestration choice.

### Revision is not protocol retry

A closure revision is a NEW logical cognitive execution.

It is not another semantic attempt inside the prior producer receipt.

The revision packet contains the exact:

```text
closure subject
prior producer receipt/output
prior challenge receipt/output
revision ordinal = 1
```

A schema-invalid or technical retry and a semantic revision remain distinct:

```text
protocol retry
→ same logical execution
→ same semantic packet
→ another protocol attempt
→ same execution receipt

closure revision
→ new semantic packet
→ new logical execution
→ new execution receipt
```

### Revision is bounded to the same closure family

A revision exists only to answer the exact objections raised against the prior
closure candidate.

It MUST NOT be used as a free second semantic search or as a branch-switching
mechanism.

A revision may:

```text
produce one revised candidate in the same closure family
OR
withdraw that closure through the role/task's protocol-defined
not-established result
```

It MUST NOT directly convert one closure family into another.

Examples of forbidden revision branch-switching include:

```text
unique-correction
→ decision-required

no-normative-impact
→ unique-correction

refutation
→ normative-impact

repair-realization
→ product decision
```

A different semantic branch, when authorized, is entered only through its own
ordinary qualification path.

For mechanically projected closures whose source is an atomic structured
discovery product, protocol-v7 construction must bind the revision to that
exact atomic candidate and its exact hostile objections. It may not rewrite
unrelated classifications from the same discovery output.

The concrete P7 schema must make this same-family binding mechanically
checkable. No implementation may infer it from free text.

### Revised candidates require one fresh hostile challenge

If the revision emits a revised closure candidate, that candidate requires one
fresh hostile challenge bound to its exact revised bytes.

The producer cannot self-certify that the objections were repaired.

The maximal closure graph is therefore:

```text
C0
→ H0 with objections
→ C1
→ H1
```

No `C2` exists.

No `H2` exists.

If `H1` contains one or more objections, that closure path is exhausted.

### not-established revision terminates the closure path

When the revision emits the protocol-defined:

```text
not-established
```

result, the producer has withdrawn the closure candidate.

No hostile challenge is required for that withdrawal because no positive
closure is being asserted.

The closure path is then exhausted.

`not-established` does not prove the opposite semantic proposition.

### Materiality asymmetry remains special

For a materiality-assessment closure:

```text
M0 has all seven axes false
→ hostile materiality challenge H0
```

If `H0` has objections, one materiality revision `M1` is mandatory while the
subject remains current and execution remains operationally admissible.

If `M1` sets at least one materiality axis to true:

```text
material = true
```

and no second materiality challenge is required.

If `M1` still has all seven axes false, it is a revised non-material closure
candidate and requires one fresh materiality challenge `H1`.

Then:

```text
H1.objections == []
→ non-material closure qualifies

H1.objections != []
→ non-material closure is not established
→ materiality remains unresolved
→ applicable operator path
```

Surviving objections to an all-false materiality candidate MUST NOT be
mechanically converted into `material = true`.

### Refutation exhaustion

For refutation:

```text
R0 candidate
→ H0 objections
→ mandatory R1
```

`R1` may be:

```text
revised refutation candidate
OR
not-established
```

If it is a revised candidate, one fresh challenge is required.

If the revision returns `not-established`, or if its fresh challenge still has
objections, the refutation path is exhausted.

Refutation-path exhaustion does not prove the finding true.

A positively material finding with no qualified refutation may then cross the
separate surviving-material boundary defined by this ADR.

### Derivation, realization-scope and repair exhaustion

The same bounded rule applies to challenged positive candidates for:

```text
unique correction
realization scope
repair realization
```

The revision may produce a same-family revised candidate or
`not-established`.

A revised candidate requires one fresh challenge.

A withdrawal or a revised candidate that still receives objections exhausts
that exact closure path.

Failure of automatic realization after a semantic correction has already been
qualified is an operational inability to establish safe realization. It does
not fabricate product-semantic underdetermination.

### No-normative-impact and decision-necessity revisions

A challenged no-normative-impact or decision-necessity closure also consumes
the one mandatory revision when current and operationally admissible.

The revision remains bound to the same exact closure family and exact prior
objections.

It may revise that candidate or withdraw it through the protocol-defined
negative result.

It may not introduce a materially different product question merely to preserve
the closure.

Protocol-v7 construction must define the exact targeted role/task binding for
these mechanically projected closure candidates before activation. No M5
implementation may choose it.

A failed no-normative-impact closure does not prove normative impact.

A failed decision-necessity closure does not prove that no product decision is
needed.

### Staleness and operational inability

The mandatory revision requirement does not authorize stale semantic work.

If, before revision construction:

```text
S changes
OR
P changes
OR
the exact adjudication/resolution subject ceases to be current
```

the old closure lineage terminates and work is derived from new current
authority.

Likewise, if the required revision cannot be executed because the exact current
protocol has no usable supporting profile, required identity evidence cannot be
established, dispatch cannot lawfully occur, or another accepted operational
precondition fails, the applicable operational/operator path is used.

Operational inability is not semantic closure failure and is not
`DECISION-REQUIRED`.

### Closure exhaustion is therefore deterministic

For a challenged revision-eligible closure, `closure path exhausted` means
exactly one of the protocol-defined terminal conditions has occurred after the
mandatory bounded revision rule has been applied.

A runner MUST NOT call a closure path exhausted merely because it chose not to
exercise the available revision.

This makes closure exhaustion replayable and comparable across conforming runs.

### Closure challenge contracts belong to protocol identity

Protocol v7 does not select hostile challenge behavior by `challenge_kind`
alone.

Protocol identity owns exactly one closure challenge contract for every admitted:

```text
(challenge_kind, challenge_subject.selector)
```

pair.

Every contract fixes exactly:

```text
candidate family
challenge kind
challenge subject selector
challenger role
required objective sequence
revision producer role
revision task
revision task mode where applicable
same-family revision target
permitted withdrawal result
```

No runner, M5 implementation, prompt, scheduler, coding agent, or checker may
select another objective set or role dynamically.

No challenge-kind-only fallback exists.

Unknown selector, known selector with wrong challenge kind, wrong challenger
role, wrong objective sequence, or wrong revision producer/task binding is
invalid evidence.

### Exact protocol-v7 closure contracts

Protocol v7 owns exactly these seven closure contracts:

```text
1.
candidate family:
materiality-assessment

challenge_kind:
materiality

challenge_subject.selector:
gate-a-materiality-assessment-challenge-v1

challenger role:
challenge

revision producer:
materiality-assessor

revision task:
materiality-assessment

withdrawal:
not permitted


2.
candidate family:
refutation

challenge_kind:
refutation

challenge_subject.selector:
gate-a-refutation-candidate-challenge-v1

challenger role:
challenge

revision producer:
refutation-builder

revision task:
refutation

withdrawal:
not-established


3.
candidate family:
unique-correction

challenge_kind:
derivation

challenge_subject.selector:
gate-a-unique-correction-candidate-challenge-v1

challenger role:
challenge

revision producer:
derivation-builder

revision task:
unique-correction-derivation

withdrawal:
not-established


4.
candidate family:
realization-scope

challenge_kind:
derivation

challenge_subject.selector:
gate-a-realization-scope-candidate-challenge-v1

challenger role:
challenge

revision producer:
derivation-builder

revision task:
realization-scope-derivation

withdrawal:
not-established


5.
candidate family:
no-normative-impact

challenge_kind:
normative-impact

challenge_subject.selector:
gate-a-no-normative-impact-candidate-challenge-v1

challenger role:
challenge

revision producer:
discovery-classifier

revision task:
discovery-classification

revision task mode:
closure-revision

revision target:
no-normative-impact

withdrawal:
not-established


6.
candidate family:
decision-necessity

challenge_kind:
decision-necessity

challenge_subject.selector:
gate-a-decision-necessity-candidate-challenge-v1

challenger role:
decision-necessity-challenger

revision producer:
discovery-classifier

revision task:
discovery-classification

revision task mode:
closure-revision

revision target:
decision-necessity

withdrawal:
not-established


7.
candidate family:
repair-realization

challenge_kind:
repair

challenge_subject.selector:
gate-a-repair-realization-candidate-challenge-v1

challenger role:
challenge

revision producer:
repair-synthesizer

revision task:
repair-realization

withdrawal:
not-established
```

Historical protocol-v1 through protocol-v6 challenge selectors retain their
historical interpretation.

The new protocol-v7 selectors do not mutate
`hostile-materiality-challenge-v1` or `hostile-refutation-challenge-v1`.

### Materiality objectives

The protocol-v7 materiality contract uses exactly:

```text
authority_or_upstream_decision
claim_structure
normative_provenance
modality_or_assurance_domain
coverage_or_residual_assurance
interaction_scope
candidate_model_authorization
```

The initial and revised challenge trigger is exactly:

```text
all seven materiality axes == false
```

A revised materiality assessment with one or more true axes becomes material and
does not require another materiality challenge.

### Refutation objectives

The protocol-v7 refutation contract uses exactly:

```text
attacked-premise-still-supported
target-correctly-identified
counterexample-remains-in-scope
consequence-still-follows
not-actually-already-accounted-for
hidden-assumption-in-refutation
alternative-authority-compatible-interpretation
```

### UniqueCorrection derivation objectives

The UniqueCorrection derivation contract uses exactly:

```text
authority-does-not-entail-correction
materially-distinct-authority-compatible-alternative
required-consequence-omitted
unauthorized-semantic-effect
hidden-assumption-in-derivation
```

It does NOT use RealizationScope objectives.

### RealizationScope derivation objectives

The RealizationScope derivation contract uses exactly:

```text
realization-scope-omits-required-surface
realization-scope-grants-unnecessary-write-authority
```

It does NOT use UniqueCorrection semantic-derivation objectives.

Mechanical prohibition on writable controlling product-authority paths remains
a deterministic validation rule and is not added as another hostile objective by
this ADR.

### NoNormativeImpact objectives

The NoNormativeImpact contract uses exactly:

```text
correction-requires-product-authority-change
correction-selects-among-product-meanings
missing-product-obligation-exposed
earliest-cause-is-normative-or-upstream
accepted-observable-behavior-would-change
downstream-resolution-requires-product-choice
authority-conflict-hidden-as-downstream-defect
```

### DecisionNecessity objectives

The DecisionNecessity contract uses exactly:

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

`decision-necessity-challenger` is the one hostile challenger for this contract.

There is no second generic challenge after it.

### RepairRealization objectives

The RepairRealization contract uses exactly:

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

### Exact challenge-subject binding

For protocol-v7 candidates produced directly by one cognitive execution, the
challenge subject binds mechanically:

```text
exact qualification/adjudication subject
+
exact producer execution receipt
+
exact producer packet
+
exact producer raw output
+
exact parsed producer output
+
exact challenged candidate selected inside that output
```

This direct-producer pattern applies to:

```text
materiality
refutation
UniqueCorrection
RealizationScope
NoNormativeImpact
RepairRealization
```

The challenger therefore receives no hidden repository or mutable-workspace
context.

For DecisionNecessity, the challenged candidate is a mechanical projection, not
a free producer output.

Its challenge subject instead binds exactly:

```text
exact surviving-material resolution subject
+
exact decision-required discovery hypothesis
+
exact mechanically established UniqueCorrection-derivation exhaustion basis
+
exact mechanically projected DecisionNecessity candidate
```

Failure to derive is not enough.

Only a lawfully exhausted UniqueCorrection derivation path may participate in
that mechanical DecisionNecessity construction.

### Required objectives

The canonical challenge packet's:

```text
required_objectives
```

must equal the exact objective sequence owned by the exact closure challenge
contract selected through:

```text
challenge_subject.selector
```

and the packet's `challenge_kind` must equal that same contract's exact kind.

The checker validates exact contract selection, objective coverage, role binding,
candidate binding, and revision-family binding.

It does not claim that the challenger's objections are semantically correct.

### Supporting-role acquisition belongs to P

Initial-reviewer acquisition remains governed by ADR-053:

```text
minimum-effective-independent-v1
```

Supporting cognitive work has a different objective.

It does not attempt to increase the independent-reviewer cardinality.

Protocol v7 introduces:

```text
policies.supporting_role_acquisition.mode
=
first-statically-qualifying-in-reviewer-acquisition-order-v1
```

It reuses exactly:

```text
policies.reviewer_acquisition.profile_order
```

No second profile order exists.

For each new logical supporting cognitive WorkItem:

1. traverse the exact reviewer acquisition order;
2. filter by the existing static reviewer qualification rules;
3. select the first statically qualifying profile;
4. bind that exact profile to the WorkItem.

The static qualification predicate remains exactly the ADR-053 predicate.

### Supporting profiles are reusable

A profile selected for supporting work is not consumed.

The same profile may execute any number of distinct supporting WorkItems.

Previous use of a profile, previous resolved identity, finding authorship,
challenge authorship, or use in another role does not exclude it from later
supporting work.

There is no supporting-role round, pool-consumption counter, or
already-selected-profile set.

### Supporting effective-identity collision does not trigger expansion

Supporting work does not exist to establish an independent-reviewer minimum.

Therefore two supporting executions resolving to the same effective identity
remain valid evidence and do not trigger selection of another profile.

No supporting identity-collision expansion exists.

### Producer and challenger may use the same effective identity

A hostile challenge must remain a fresh isolated logical execution.

Protocol v7 does not newly require:

```text
challenger effective identity
!=
producer effective identity
```

Producer and challenger may therefore resolve to the same effective identity.

This decision asserts independence of execution occurrence and exact-input
binding, not diversity of model identity.

A future requirement for producer/challenger model diversity would require a
separate hostile-review assurance decision.

### No supporting-profile fallback

Once one profile is bound to a supporting WorkItem:

```text
technical retry
protocol-invalid retry
```

retain that exact profile.

A protocol-valid semantic completion is terminal.

If automatic retries are exhausted, the runner MUST NOT substitute the next
profile merely to obtain another semantic result.

The applicable operational-blocker path is used instead.

The runner MUST NOT choose a profile based on:

```text
finding text
finding count
finding author
finding severity
confidence
prior disagreement
prior agreement
desired outcome
semantic result
network latency
completion order
provider convenience
model preference
```

### Supporting identity remains evidence

Supporting executions still require exact resolved reviewer identity.

Not counting one execution toward the independent-reviewer minimum does not
remove its evidence requirements.

ADR-054 therefore applies equally to supporting roles.

If a selected `provider-reported` profile cannot establish the required
provider-owned canonical effective-model identity for a completed semantic
response:

```text
preserve the completed response
preserve raw evidence
do not fabricate model_version
do not semantic-retry
do not substitute another profile
stop automatic semantic progression
use the applicable operational path
```

### No supporting profile available

If no statically qualifying profile exists, that fact alone does not create a
campaign blocker before supporting cognitive work is actually required.

When a concrete supporting WorkItem becomes necessary and no supporting profile
can be selected, automatic semantic work cannot proceed.

That condition is operational inability under the current immutable protocol
and must use the applicable operator path.

It is not `DECISION-REQUIRED`.

The current run may not mutate P, append a profile, reorder profiles, or invent
a replacement model.

### Finding-adjudication supplement identity is protocol-scoped

A protocol change MUST NOT erase a surviving historical finding.

The same original finding may require a fresh adjudication under successive
current protocols.

Protocol-v7 append-only current adjudication uses
`FindingAdjudicationSupplementV1`.

The exact supplement semantic key is:

```text
source review identity
+
source finding identity
+
exact validated substantive source-finding SHA-256
+
exact adjudicating protocol identity P
```

A source-finding SHA MUST first be validated against the exact original finding.

A mismatching SHA does not create a valid distinct supplement.

Two supplements for one exact semantic key are duplicates.

A supplement under a later current `P` is not a duplicate of an earlier
supplement merely because source review and source finding are unchanged.

The adjudicating ReviewCampaign is provenance only.

It does not create another semantic identity dimension and does not make the
campaign record writable.

Historical protocol-v1 through protocol-v6 `re_adjudications[]` remain valid
under their exact historical protocol contracts.

Protocol v7 does not rewrite those artifacts.

New protocol-v7 cross-campaign adjudication uses the supplement representation
defined by this ADR instead of manufacturing a new schema-5
`re_adjudications[]` member.

A same-protocol immutable source finding may also receive one current-P
supplement when later post-review qualification must change its effective
current adjudication without rewriting the source record.

### ReviewContext remains immutable production provenance

`ReviewContext` is production provenance for an exact runner-produced review
campaign.

It MUST NOT be retargeted to a later candidate.

ADR-055 does not redefine that meaning.

Construction synchronization following this ADR reserves `ReviewContext`
for initial-review production.

All post-review cognitive work uses current resolution provenance through the
resolution-context concept.

This includes:

```text
materiality assessment
materiality challenge
refutation
refutation challenge
discovery classification
derivation
normative-impact challenge
decision-necessity challenge
realization-scope derivation
repair realization
repair challenge
```

The exact cross-module type revision belongs to the subsequent NIB-S update.

### Finding-adjudication bootstrap subject

The first post-review materiality assessment MUST NOT depend on an already
surviving-material resolution subject.

After one exact raw finding has been normalized into one exact `FindingRef`,
M5-B mechanically establishes an immutable bootstrap subject conceptually named:

```text
FindingAdjudicationSubjectV1
```

with canonical selector:

```text
gate-a-finding-adjudication-subject-v1
```

Its required semantic/provenance content is exactly:

```ts
interface FindingAdjudicationSubjectV1 {
  readonly schema:
    "gate-a-finding-adjudication-subject.v1";

  readonly runId:
    GateARunId;

  readonly semanticSubject:
    SemanticSubjectRef;

  readonly currentProtocolBundle:
    ProtocolBundleRef;

  readonly sourceFinding: {
    readonly reviewCampaignId:
      ReviewCampaignId;

    readonly findingId:
      FindingId;

    readonly substantiveFindingSha256:
      Sha256;

    readonly normalizedFinding:
      ArtifactRef;
  };

  readonly sourceProtocolBundle:
    ProtocolBundleRef;

  readonly adjudicatingReviewCampaignId:
    ReviewCampaignId;

  readonly provenance:
    | {
        readonly kind:
          "current-protocol-finding";
      }
    | {
        readonly kind:
          "stale-protocol-finding";
      };
}
```

The exact runtime validator and TypeScript declaration belong to the subsequent
NIB-S/M0 synchronization.

This ADR fixes the meaning they must preserve.

The subject is established before the first materiality WorkItem.

It does not claim:

```text
the finding is material
the finding survived refutation
the finding is true
the finding requires repair
the finding requires a product decision
```

It states only which exact finding is being adjudicated under which exact
current `S` and `P`.

### Substantive finding identity

`substantiveFindingSha256` is the exact canonical hostile-finding semantic
subject hash over the substantive finding content required by current
hostile-review authority.

Historical materiality, status, disposition, challenge result, or
re-adjudication result MUST NOT become part of that substantive finding hash.

A protocol change can therefore re-adjudicate the same substantive finding
without rewriting its semantic finding identity.

### Current-protocol bootstrap

For a finding whose source campaign already uses the exact current protocol:

```text
source campaign S == current S
source campaign P == current P
```

require exactly:

```text
provenance.kind
=
current-protocol-finding

adjudicatingReviewCampaignId
=
sourceFinding.reviewCampaignId

sourceProtocolBundle
=
currentProtocolBundle
```

No second campaign is selected merely to adjudicate that current-protocol
finding.

### Stale-protocol bootstrap

For a stale-protocol finding:

```text
source campaign S == current S
source campaign P != current P
```

a current-protocol campaign MUST already exist before post-review
re-adjudication begins.

If there is no current campaign, the existing protocol-changed campaign-required
path is completed first.

Once one or more current campaigns exist, select the adjudicating campaign
deterministically as:

```text
the first current campaign in the exact canonical M3 currentCampaigns order
```

where that order remains:

```text
ReviewCampaignId unsigned ASCII ascending
```

No selection by:

```text
runner-produced versus repository-imported
repository commit
record path
record hash
candidate provenance
finding severity
semantic result
scheduler order
completion time
model identity
```

is permitted.

The selected adjudicating campaign is execution/provenance context only.

It does not become a new semantic identity component of stale-finding
re-adjudication and does not authorize mutation of a repository-imported
historical review record.

It also does not determine a writable review-record owner.

Protocol-v7 append-only cross-campaign adjudication is projected through the
separate `FindingAdjudicationSupplementV1` artifact defined by this ADR.

Therefore an imported current adjudicating campaign remains fully immutable even
when it provides the current execution/protocol provenance for newly produced
supporting work.

The protocol-scoped re-adjudication identity remains the identity defined
elsewhere in this ADR:

```text
source review
+
source finding
+
validated substantive finding SHA
+
current P
```

### Materiality and refutation share the bootstrap subject

Materiality and refutation use the same exact
`FindingAdjudicationSubjectV1`.

A successful materiality assessment does not create a new finding subject.

A refutation WorkItem receives the exact same finding-adjudication subject plus
the exact qualified materiality evidence required by its packet.

Intermediate adjudication products are packet inputs, not mutations of the
finding-adjudication subject.

### Surviving-material promotion boundary

Only after M5-B has positively established materiality and the exact refutation
path has lawfully terminated without a qualified refutation may M5 establish a
distinct downstream subject conceptually named:

```text
SurvivingMaterialResolutionSubjectV1
```

with canonical selector:

```text
gate-a-surviving-material-resolution-subject-v1
```

Conceptually it binds:

```text
the exact FindingAdjudicationSubject
+
the exact current S
+
the exact current P
+
the exact evidence that materiality qualified
+
the exact evidence that the refutation path lawfully terminated
  without a qualified refutation
```

The exact serialized field layout of the surviving-material basis belongs to the
subsequent P7 schema/NIB-S construction because it must consume the exact
durable evidence graph defined by this ADR.

That later construction MUST NOT alter this promotion rule.

No `SurvivingMaterialResolutionSubjectV1` exists when:

```text
non-material closure qualified
OR
qualified refutation exists
OR
materiality remains unresolved
OR
M5-B cannot lawfully finish the required adjudication path
```

`not-established` from one refutation-builder execution is not by itself proof
that the finding is true.

Crossing the surviving-material boundary requires:

```text
qualified materiality
+
lawfully exhausted refutation path
+
no qualified refutation
```

The meaning of `lawfully exhausted` uses the mandatory bounded-revision rule in
this ADR.

### Candidate independence of adjudication semantics

`FindingAdjudicationSubjectV1` and a qualified
`SurvivingMaterialResolutionSubjectV1` are not physical patch scopes.

Candidate-specific execution provenance remains in `ResolutionContext`.

A later same-`(S,P)` candidate does not retarget historical review production.

A qualified semantic resolution may remain applicable according to its exact
authority bindings while candidate-bound realization scope and repair must be
derived freshly for the new current candidate as required elsewhere in this
ADR.

This construction may support both runner-produced and repository-imported
adjudicating campaigns without rewriting their historical review evidence.

### Protocol structure does not define runner orchestration

The following remain construction responsibilities rather than hostile-review
protocol semantics:

```text
M5 obligation identities
M5 WorkItem identities
global resolution-classification barrier
global semantic-blocker admission barrier
deterministic multi-repair realization order
at-most-one enabled candidate-bound repair realization
RepairIntentId derivation
DecisionRequestId derivation
replay and restart algorithms
candidate lineage bookkeeping
operator-cause descriptor schemas
M2 admission batching
M7 patch application
publication behavior
```

A Module Brief may define those mechanisms only after consuming the accepted
protocol decisions.

### Deterministic validation boundary

The protocol checker may establish structural/provenance facts including:

```text
JSON/schema validity
exact role/task variant compatibility
exact packet binding
embedded object SHA validity
revision ordinal validity
local identity/reference closure
exact materiality-axis structure
exact challenge objective coverage
correction-requirement completeness
writable scope subset of readable scope
repair operation containment inside qualified writable scope
repair requirement coverage
null-operation iff all requirements are already-realized
minimum alternative cardinality for a decision-required candidate
execution receipt attempt consistency
reviewer-profile selection conformance
```

It does not mechanically prove semantic truth including:

```text
materiality axes are substantively correct
a refutation argument is true
the stated cause is actually earliest
a correction is genuinely unique
a no-normative-impact claim is true
decision necessity is genuine
a realization scope is semantically sufficient
a proposed repair faithfully realizes the correction
an already-realized claim is true
```

Those semantic claims require the exact hostile qualification relationships
defined by the protocol.

### Product semantics remain unchanged

Explicitly:

```text
no TURNLOCK product semantic change
no TL-INV change
no TL-CLAIM change
no normative coverage change
no executable formal model introduced
Gate A semantic subject S unchanged
ADR-055 is not added to authority.architecture_decisions
ADR-055 is not added to authority.abstraction_constraints
```

ADR-055 changes hostile-review assurance protocol architecture only.

## Construction consequences

If this proposal is later accepted and protocol v7 is published, construction
must synchronize the runner contracts before GREEN.

The required construction direction remains:

```text
ReviewContext
→ initial-reviewer production provenance only

ResolutionContext
→ all post-review cognitive adjudication/resolution/challenge work
```

The future System Brief revision must account for at least:

```text
FindingAdjudicationSubjectV1 bootstrap product
SurvivingMaterialResolutionSubjectV1 promotion boundary

FindingAdjudicationSupplementV1 append-only projection
supplement semantic-key uniqueness
supplement effective-adjudication overlay selection
supplement supporting-execution DAG closure
supplement repository projection namespace

decision-projection no longer being a current cognitive role

discovery-classification adjudication kind
normative-impact adjudication kind

protocol-v7 closure challenge contracts keyed by
(challenge_kind, challenge_subject.selector)

protocol-v7 exact challenger-role binding
protocol-v7 exact revision-producer binding
protocol-v7 same-family revision enforcement

supporting cognitive authority projection
protocol-v7 deterministic validation roles
protocol-v7 exact predecessor receipt/output bindings
runtime CAS identity versus repository locator reconstruction

mandatory bounded closure-revision WorkItem generation

historical schema-v5 re_adjudication compatibility
without emitting new P7 cross-campaign re_adjudications
```

These are construction consequences, not current active NIB-S behavior.

Until later synchronization is accepted:

```text
NIB-S 10.0.0 remains active
protocol v6 remains active
current Module Brief versions remain active
```

### Campaign currentness remains campaign-only

The supplement mechanism does not change ReviewCampaign currentness.

M3 continues to derive:

```text
currentCampaigns
staleProtocolCampaigns
```

only from real ReviewCampaign records.

A supplement never becomes a ReviewCampaign and never participates in reviewer
minimum counting.

The exact complete current campaign set remains the complete structurally valid
campaign set over exact `(S, P)`.

### No writable projection-host campaign

Construction MUST NOT create an otherwise unnecessary runner-produced
ReviewCampaign merely because new post-review evidence needs an append-only
repository representation.

Persistence need MUST NOT create new hostile-review semantic work.

Construction also MUST NOT fabricate a new runner-produced campaign by reusing or
copying initial-reviewer executions from an imported campaign.

A runner-produced ReviewCampaign record remains the projection of that
campaign's own authoritative campaign history.

### Repository projection boundary

The future M5-D contract must project supplement instances additively and
idempotently under:

```text
formal/reviews/supplements/**
```

and extend the assurance repository projection allowlist accordingly.

Supplement projection MUST obey the existing assurance projection principles:

```text
regular file only
mode 100644
no deletion
no rename
no rewrite
no merge
no symlink traversal
exact byte equality for idempotent preexistence
different bytes at the same exact target path fail closed
```

The supplement path is content-addressed by the exact canonical supplement
bytes.

The exact M5-D algorithms, projection-entry identity, readiness timing, and
candidate materialization mechanics remain construction-owned.

### Effective Gate A overlay

Protocol-v7 checker construction must evaluate one original finding under exact
current `(S, P)` as follows:

```text
if more than one exact current-P supplement exists:
    evidence integrity failure

if exactly one exact current-P supplement exists:
    use supplement.effective_adjudication

else if source campaign protocol == current P:
    use source finding native materiality/status/disposition

else:
    current-protocol adjudication is absent
    finding remains blocking
```

Only:

```text
qualified-non-material
qualified-refutation
```

may produce a non-blocking supplement overlay.

`surviving-material` remains blocking.

This rule changes hostile-review assurance interpretation for protocol v7 only.

It does not reinterpret historical protocol-v1 through protocol-v6 evidence.

## Closed proposal questions and remaining acceptance work

The previously identified bootstrap, durable-evidence, and bounded-revision
questions remain closed.

Concrete construction has additionally closed:

```text
challenge objective lookup
→ exact closure contract selected by kind + subject selector

cross-campaign immutable finding update
→ FindingAdjudicationSupplementV1

review-evidence-v5 role
→ remains immutable ReviewCampaign record schema

post-review append-only effective adjudication
→ supplement overlay

non-blocking overlay authority
→ only qualified non-material or qualified refutation

persistence-only ReviewCampaign creation
→ forbidden
```

### Bootstrap provenance

The first post-review materiality assessment is bootstrapped by the exact
`FindingAdjudicationSubjectV1` defined by this ADR.

A surviving-material resolution subject is a later promotion product and is not
a prerequisite for materiality/refutation adjudication.

### Durable evidence linkage

Review-evidence schema 5.0 remains sufficient for ReviewCampaign records.

It is no longer claimed to be the sole possible root container for all
protocol-v7 post-review evidence.

Protocol v7 adds `FindingAdjudicationSupplementV1` as a separate immutable
evidence root where append-only post-review adjudication cannot lawfully mutate
the source campaign record.

Both root classes use the exact supporting-execution DAG rules defined by this
ADR.

No review-evidence-v6 meta-schema is required by this design.

### Closure revision

The one available semantic closure revision remains mandatory after qualified
objections whenever the exact subject remains current and automatic execution
remains operationally admissible.

The revision is bounded to the same closure family and may withdraw through the
protocol-defined negative result rather than fabricate a new closure.

### ADR status remains proposed

Closing these construction discoveries does not activate protocol v7 and does
not make this ADR accepted.

Before ADR-055 may transition from `proposed` to `accepted`, the concrete
protocol-v7 artifact set must be constructed and mechanically validated against
these decisions.

That construction includes at minimum:

```text
review-protocol-bundle meta-schema v7
gate-a-campaign-protocol-v7
execution-receipt-v4
adjudication-packet-v1
adjudication-output-v1
finding-adjudication-supplement-v1
adjudication prompt v2
repair prompt v2
exact protocol-owned closure challenge contracts
protocol-v7 checker behavior
protocol-v7 effective-supplement-overlay validation
protocol-v7 supporting-evidence graph validation
historical protocol-v1 through protocol-v6 regression validation
explicit inactive-P7 conformance validation while P6 remains current
```

Concrete construction may expose another material assurance ambiguity.

If that occurs, STOP and route that discovery explicitly.

A coding agent MUST NOT resolve a newly discovered semantic/protocol ambiguity
by inventing schema fields, challenge policy, reviewer policy, branch behavior,
overlay semantics, or evidence meaning.

Until the complete protocol-v7 artifact set validates and ADR-055 is explicitly
accepted:

```text
gate-a-campaign-protocol-v6 remains current
execution-receipt schema 3.0 remains current
review-evidence schema 5.0 remains current
NIB-S 10.0.0 remains active
M5-B remains pending
M5-C remains pending
M5-D remains pending
```

## Alternatives considered

### Keep protocol v6 and define structures only in M5 Module Briefs

Rejected.

That would let construction authority invent hostile-review protocol meaning
that ADR-047 explicitly left undefined.

### Treat every completed supporting response as qualified regardless of shape

Rejected.

Once structured protocol contracts are justified, preserving unvalidated
free-form outputs would prevent deterministic protocol validation and permit
ambiguous construction behavior.

### Use a different reviewer-profile order for every role

Rejected.

No accepted assurance requirement establishes role-specific model ranking.
One protocol-owned order is sufficient and avoids hidden model preference.

### Automatically fall back to another model after a supporting failure

Rejected.

That would make operational failure or semantic inconvenience a model-shopping
mechanism.

### Require producer and challenger to use different model identities

Rejected for this ADR.

Existing authority requires a fresh challenge execution, not model-identity
inequality. Adding that assurance requirement requires independent
justification.

### Put physical patch scope inside semantic UniqueCorrection

Rejected.

Semantic correction and candidate-specific physical realization have different
lifetimes. Candidate advance with unchanged `(S, P)` must not require rewriting
semantic derivation merely because physical realization scope changes.

### Create a new ReviewCampaign only to host append-only adjudication

Rejected.

A persistence requirement must not create new initial-reviewer executions,
potentially new findings, or a new hostile-review campaign merely because an
existing immutable campaign record cannot be rewritten.

ReviewCampaign identity remains semantic hostile-review campaign identity, not a
repository-write slot.

### Reuse imported reviewer executions inside a synthetic runner campaign

Rejected.

A runner-produced ReviewCampaign record must remain the projection of that
campaign's own authoritative campaign history.

Copying or re-owning imported initial-reviewer executions under another
`review_id` would manufacture campaign provenance.

### Introduce review-evidence schema 6.0 only to represent post-review overlays

Rejected for this design.

Schema 5.0 remains a coherent immutable representation of a real ReviewCampaign.

The missing abstraction is not another campaign-record version but a distinct
append-only adjudication supplement whose semantics and qualification differ
from review production.

### Convert failure to derive into DECISION-REQUIRED

Rejected.

ADR-045 explicitly reserves `DECISION-REQUIRED` for genuine product-semantic
underdetermination or genuine unresolved product-authority conflict.

## Consequences

### Benefits

- M5-B and M5-C can consume protocol-owned structured outputs rather than
  inventing semantic contracts.
- Schema-invalid supporting completions become mechanically distinguishable from
  semantically inconvenient valid completions.
- Semantic-result model shopping remains forbidden.
- Discovery classification remains routing evidence rather than outcome
  authority.
- Unique correction remains distinct from candidate-specific physical
  realization.
- Already-realized repair claims become challengeable without inventing empty
  patches.
- Genuine Decision Requests remain positively qualified.
- Supporting reviewer selection becomes deterministic and replayable.
- Immutable imported or already-projected campaign findings can receive later
  current-protocol adjudication without rewriting their source record.
- Persistence needs no longer require synthetic ReviewCampaign creation or new
  initial-reviewer execution.
- Effective finding overlay is fail-closed: only qualified non-materiality or
  qualified refutation can make one supplemented finding non-blocking.
- ReviewCampaign identity remains distinct from append-only post-review evidence
  identity.
- Stale findings can be re-adjudicated under successive protocol identities.

### Costs

- Protocol v7 requires new immutable schema and meta-schema artifacts.
- Protocol v7 additionally requires the immutable
  `finding-adjudication-supplement-v1` schema and supplement repository
  validation/projection support.
- Execution receipts require a new schema version.
- The checker requires role-aware deterministic validation for the new
  structured outputs.
- NIB-S and dependent Module Briefs require synchronization after protocol
  acceptance.
- Existing v1-v6 historical compatibility must remain regression-tested.

## Non-goals

ADR-055 does not:

- create TURNLOCK product semantics;
- answer any Decision Request;
- implement M5-B;
- implement M5-C;
- implement production code;
- define repair ordering;
- define blocker-admission ordering;
- define M5 replay state machines;
- apply a repository repair;
- execute a real hostile-review campaign;
- mark Gate A ready;
- change protocol v6 in place;
- modify historical hostile-review artifacts.

## References

- `AGENTS.md`
- `docs/adr/adr-041-establish-turnlock-formal-assurance-architecture.md`
- `docs/adr/adr-042-define-auditable-hostile-review-campaign-execution-and-adjudication.md`
- `docs/adr/adr-045-bind-gate-a-campaigns-to-versioned-review-protocol-and-derived-evidence.md`
- `docs/adr/adr-046-bind-challenge-executions-to-exact-inputs-and-derive-retry-admissibility.md`
- `docs/adr/adr-047-make-unvalidated-cognitive-completions-terminal-and-validate-readiness-projections.md`
- `docs/adr/adr-048-content-address-hostile-review-meta-schemas.md`
- `docs/adr/adr-049-clarify-hostile-review-execution-receipt-attempt-mapping.md`
- `docs/adr/adr-053-define-deterministic-minimum-effective-hostile-reviewer-acquisition.md`
- `docs/adr/adr-054-define-provider-reported-effective-model-identity-resolution.md`
- `docs/formal/nib-s-gate-a-campaign-runner.md`
- `formal/reviews/README.md`
- `formal/reviews/protocols/gate-a-campaign-protocol-v6.json`
- `formal/reviews/meta-schemas/review-protocol-bundle-v6.schema.json`
- `formal/reviews/meta-schemas/review-evidence-v5.schema.json`
- `formal/reviews/schemas/execution-receipt-v3.schema.json`
- `formal/reviews/schemas/challenge-packet-v1.schema.json`
- `formal/reviews/schemas/challenge-output-v1.schema.json`
- `scripts/check-formal-traceability.py`
