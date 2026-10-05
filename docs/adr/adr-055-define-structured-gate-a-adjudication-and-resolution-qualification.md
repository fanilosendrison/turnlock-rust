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
decision_body_sha256: "9079f149a5d49655e08d8aa13a469e6b43cbec86cab4c901f0b7286c39b3d0a5"
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

### Review evidence remains schema 5.0

ADR-055 does not require a new top-level review-evidence schema merely because
new cognitive packet/output schemas are introduced.

Protocol v7 continues to bind the immutable:

```text
formal/reviews/meta-schemas/review-evidence-v5.schema.json
```

unless later concrete schema construction proves that review-evidence v5 cannot
represent the required durable references without ambiguity.

Such a discovery must be routed separately before protocol v7 is accepted.

Do not mutate the frozen legacy aliases or the published v5 evidence
meta-schema.

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

### Closure revision remains bounded and is not protocol retry

The existing:

```text
max_closure_revisions = 1
```

remains in protocol identity.

When a closure candidate receives objections, any permitted revised closure
candidate is a NEW logical cognitive execution.

It is not a second semantic attempt inside the producer's prior receipt.

The revised execution receives the exact previous candidate and exact previous
challenge output as explicit packet input.

Its fresh challenge is another distinct logical execution bound to the revised
candidate.

A schema-invalid retry and a semantic closure revision are therefore distinct:

```text
schema-invalid retry
→ same logical semantic input
→ same WorkItem/profile
→ protocol attempt retry

closure revision
→ new semantic packet
→ new logical execution
→ new receipt
```

This ADR does not change the existing maximum revision count.

Whether a construction must always exercise the one available semantic revision
after an objection, rather than merely being allowed to do so, remains open
until the M5 construction contract closes that runner behavior.

The coding agent MUST NOT resolve that open construction question while
implementing this proposed ADR.

### Challenge objectives belong to protocol identity

Protocol v7 owns the exact required objective set for every challenge kind.

The canonical challenge packet's:

```text
required_objectives
```

must equal exactly the protocol-owned objective set for its
`challenge_kind`.

No runner, M5 implementation, prompt, scheduler, or coding agent may choose an
objective subset dynamically.

Materiality keeps exactly these objectives:

```text
authority_or_upstream_decision
claim_structure
normative_provenance
modality_or_assurance_domain
coverage_or_residual_assurance
interaction_scope
candidate_model_authorization
```

Refutation keeps exactly:

```text
attacked-premise-still-supported
target-correctly-identified
counterexample-remains-in-scope
consequence-still-follows
not-actually-already-accounted-for
hidden-assumption-in-refutation
alternative-authority-compatible-interpretation
```

Derivation uses exactly:

```text
authority-does-not-entail-correction
materially-distinct-authority-compatible-alternative
required-consequence-omitted
unauthorized-semantic-effect
hidden-assumption-in-derivation
realization-scope-omits-required-surface
realization-scope-grants-unnecessary-write-authority
```

Normative impact uses exactly:

```text
correction-requires-product-authority-change
correction-selects-among-product-meanings
missing-product-obligation-exposed
earliest-cause-is-normative-or-upstream
accepted-observable-behavior-would-change
downstream-resolution-requires-product-choice
authority-conflict-hidden-as-downstream-defect
```

Decision necessity uses exactly:

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

Repair uses exactly:

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

The checker validates exact objective coverage and binding.

It does not claim that the resulting objections are semantically correct.

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

### Stale-protocol re-adjudication identity is protocol-scoped

A protocol change MUST NOT erase a surviving finding.

The same historical source finding may therefore require a fresh
re-adjudication under successive current protocols.

The semantic identity of one re-adjudication is scoped by:

```text
source review identity
+
source finding identity
+
exact substantive source-finding SHA-256
+
current adjudicating protocol identity P
```

A source-finding SHA MUST first be validated against the exact source finding.

A mismatching SHA does not create a distinct valid re-adjudication identity.

Two re-adjudications of the same validated source finding under the same exact
current `P` are duplicates.

A re-adjudication under a later current `P` is not a duplicate of the earlier
one merely because source review and source finding are the same.

The current campaign that hosts or projects the re-adjudication is provenance.
It does not create an additional semantic identity dimension that permits
duplicate re-adjudication under one P.

### ReviewContext remains immutable production provenance

`ReviewContext` is production provenance for an exact runner-produced review
campaign.

It MUST NOT be retargeted to a later candidate.

ADR-055 does not redefine that meaning.

Construction synchronization following this ADR must reserve `ReviewContext`
for initial-review production and use the existing resolution-context concept
for post-review adjudication/resolution work that must operate against current
resolution provenance.

This construction synchronization may support both runner-produced and
repository-imported adjudicating campaigns without rewriting their historical
review evidence.

The exact cross-module type revision belongs to the subsequent NIB-S update, not
to protocol identity P.

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

The expected construction direction is:

```text
ReviewContext
→ initial-reviewer production provenance only

ResolutionContext
→ post-review materiality/refutation/discovery/derivation/
  decision-necessity/repair/challenge work
```

The future System Brief revision must also account for:

```text
decision-projection no longer being a current cognitive role
discovery-classification adjudication kind
normative-impact adjudication kind
current-target provenance for ReAdjudicationRef
supporting cognitive authority projection
protocol-v7 deterministic validation roles
```

These are construction consequences, not current active NIB-S behavior.

Until that revision is accepted:

```text
NIB-S 10.0.0 remains active
protocol v6 remains active
current Module Brief versions remain active
```

## Explicitly unresolved before acceptance

ADR-055 remains `proposed` until the complete protocol-v7 construction proves
that no hidden evidence-contract ambiguity remains.

In particular, acceptance requires explicit closure of:

1. the exact bootstrap provenance used for the first post-review materiality
   assessment before a surviving-material `ResolutionSubject` exists;

2. exact durable evidence linkage for the new adjudication packets, outputs,
   revisions, and negative `not-established` results while preserving or
   deliberately evolving review-evidence schema 5.0;

3. whether one available semantic closure revision after objections is merely
   permitted or mechanically required whenever automatic progression remains
   operationally possible.

No coding agent may decide these questions implicitly while implementing P7.

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
- Stale findings can be re-adjudicated under successive protocol identities.

### Costs

- Protocol v7 requires new immutable schema and meta-schema artifacts.
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
