---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Bind Gate A campaigns to a versioned review protocol and derived evidence"
id: "ADR-045"
status: "accepted"
date: "2026-09-19"
decision_body_sha256: "b0b9cb56937166137b15bbf92326f1520cfcaed4fc8c1c7c8516e294583df1b3"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-042"
    - "ADR-043"
    - "ADR-044"
  supersedes: []
  confirms:
    - "ADR-041"
governs:
  - "Gate A hostile-review protocol identity and currentness"
  - "Reviewer-profile qualification and effective model identity"
  - "Structured hostile-review raw output and execution receipts"
  - "One-to-one hostile finding normalization"
  - "Conservative adjudication and challenge closure"
  - "Campaign retry, restart, and external outcome rules"
---

# ADR-045: Bind Gate A campaigns to a versioned review protocol and derived evidence

## Context

ADR-041 established hostile semantic review as a first-class assurance
mechanism and required durable, inspectable review evidence. ADR-042 defined
auditable campaign execution and adjudication. ADR-043 bound review evidence to
exact self-contained reviewed inputs and prohibited symlink aliasing. ADR-044
required exactly one unambiguous Gate A derived subject per review record.

Those decisions make review evidence structurally exact but leave the review
PROTOCOL itself under-specified and not mechanically versioned:

```text
- a campaign can be current for the semantic subject while using an
  obsolete, unstated, or per-execution review protocol;
- frontier-llm is still an arbitrary per-execution free assertion with no
  protocol-owned reviewer-profile qualification;
- model_version can be an arbitrary runner-supplied alias;
- raw reviewer output can be Markdown rather than structured JSON;
- completed but protocol-invalid responses need not be sealed;
- a finding may be normalized into several findings or merged;
- non-materiality and refutation closure are not required to survive a fresh
  hostile challenge; challenge output can carry a free boolean verdict;
- a protocol change can silently erase surviving findings or accept an old
  non-material conclusion or old refutation as still sufficient;
- the campaign runner contract does not distinguish DECISION-REQUIRED from
  OPERATOR-ACTION-REQUIRED.
```

ADR-042 already required several of these properties in principle. ADR-045
makes protocol identity, reviewer qualification, structured raw output,
execution receipts, one-to-one normalization, conservative challenge closure,
and stale-protocol handling explicit and mechanically enforceable.

No real hostile-review campaign exists, so no historical campaign-evidence
migration is required.

## Discovery classification

```text
assurance-defect, resolved by this ADR
```

The defect is in the hostile-review protocol identity and evidence contract and
its mechanical enforcement. It does not concern TURNLOCK product semantics. No
normative meaning, invariant identity, assurance claim, or normative coverage
mapping is introduced, amended, or reinterpreted.

The exact discovery disposition for this change is `no-normative-impact`.

## Decision

### Semantic subject versus review protocol

Gate A has two independent identities:

```text
S = Gate A semantic subject identity
P = Gate A hostile-review protocol-bundle identity
```

A campaign is current for Gate A only if it is current for BOTH:

```text
(S, P)
```

`S` remains the existing derived subject:

```text
gate-a-assurance-decomposition-v1
```

The current semantic subject schema version remains `1`.

The current semantic subject SHA remains exactly:

```text
2b0dd42fb07d67f3a38d0414f12df49ecb9df640f12c805ee98b6af3a1db979b
```

Hostile-review protocol policy remains excluded from `S`.

Changing only hostile-review protocol policy MUST NOT change `S`.

### Protocol bundle

Gate A uses a content-addressed, versioned protocol bundle. The current bundle
is pointed to by:

```text
formal/verification.yaml
policy.hostile_review.current_protocol_bundle
```

The bundle is evidence and protocol authority only. It is not TURNLOCK product
authority.

The bundle is a canonical JSON document that declares its schema version,
protocol identity, review class, canonical prompt artifacts, canonical schema
artifacts, reviewer profiles, and protocol policies.

A protocol change requires a new content identity `P`.

A review made under a stale `P` does not satisfy current Gate A.

### Protocol changes do not erase findings

A protocol change MUST NOT erase a finding from a campaign over the same
semantic subject.

For a stale-protocol campaign whose reviewed semantic subject is still the
current `S`:

* its raw findings remain durable;
* an old non-material conclusion is not sufficient under the new protocol;
* an old refutation is not sufficient under the new protocol;
* every stale-protocol finding must be re-adjudicated under the current
  protocol before it can cease affecting Gate A.

Explicit re-adjudication evidence is recorded for this purpose. Re-adjudication
re-adjudicates the exact substantive finding of an older protocol without
changing its raw evidence.

Historical raw output is never edited. Stale review records are never deleted
or ignored.

### Reviewer profiles and `frontier-llm`

`frontier-llm` MUST NOT remain an arbitrary per-execution free assertion.

The current protocol bundle owns a versioned list of reviewer profiles. Each
profile has exactly:

```text
profile_id
provider
request_model
frontier_eligible
identity_resolution
```

`frontier_eligible` MUST be exactly `true` for a profile to qualify.

The runner and the checker MUST NOT invent or auto-promote a profile. A
model/profile not listed in the campaign protocol bundle does not qualify.

The initial v1 bundle created by this decision contains:

```json
"reviewer_profiles": []
```

The empty initial profile registry is intentional. No real Gate A campaign can
qualify until a later protocol snapshot explicitly adds eligible profiles. That
later profile change necessarily changes `P`.

### Model identity resolution

Model identity remains the ADR-042 tuple:

```text
(provider, model, model_version)
```

`model_version` MUST be derived according to the selected reviewer profile. The
allowed `identity_resolution.kind` values are exactly:

```text
provider-reported
pinned-request-model
```

For `provider-reported`:

```text
qualified attempt provider_model must be non-empty
model_version = qualified attempt provider_model
```

For `pinned-request-model`:

```text
request_model_is_immutable_version must be true
model_version = profile.request_model
```

No other fallback is permitted. The protocol never allows:

```text
model_version = arbitrary runner-supplied string
model_version = "latest"
model_version = an unresolved alias
```

For independent-reviewer counting, distinct full tuples are preserved, but the
protocol also enforces:

```text
same (provider, model_version)
=
same effective reviewer identity
```

Therefore aliases resolving to the same effective provider/model version MUST
NOT inflate `minimum_independent_reviewers`.

### Structured raw reviewer output

Initial hostile reviewer outputs are JSON artifacts:

```text
formal/reviews/raw/*.json
```

The exact model-produced `rawContent` bytes are sealed before interpretation.
The raw format contains exactly:

```text
raw_review_schema_version
objective_assessments
findings
```

Each of the 14 Gate A attack objectives MUST appear exactly once in
`objective_assessments`. Each assessment contains exactly:

```text
objective
finding_ids
```

Each raw finding contains exactly:

```text
raw_finding_id
attack_objectives
affected_claims
affected_invariants
affected_coverage_entries
evidence_references
statement
argument
counterexample
```

The reviewer MUST NOT emit:

```text
materiality
status
disposition
confidence
severity
recommendation
preferred_fix
Gate A READY/BLOCKED
decision-required
```

Zero findings is valid if and only if all required objectives are explicitly
present.

### Retry and attempt preservation

The protocol distinguishes:

```text
technical/provider transport attempts internal to one LLM call
```

from:

```text
completed LLM calls used as protocol attempts
```

If a completed model response exists, its exact bytes MUST be sealed and
retained even when its JSON is protocol-invalid.

A schema-invalid completed response may cause a fresh retry using the exact same
semantic input.

A valid semantic response MUST NEVER be retried merely because its content is
inconvenient.

No model-shopping is permitted after a semantically valid result.

Every completed protocol attempt is recorded in the execution receipt.

At most one attempt in a qualifying execution may have outcome:

```text
qualified
```

If more than one completed valid/qualified attempt exists for one execution
receipt, the evidence is invalid.

### Execution receipts

Every cognitive LLM call participating in the campaign has its own
content-addressed execution receipt under:

```text
formal/reviews/executions/*.json
```

This includes, when those calls exist:

```text
initial-reviewer
materiality-assessor
refutation-builder
challenge
discovery-classifier
derivation-builder
decision-necessity-challenger
repair-synthesizer
decision-projection
```

Only `initial-reviewer` receipts count toward
`minimum_independent_reviewers`.

A challenge is a NEW LLM execution. It MUST NOT pretend that an earlier
reviewer execution was the challenge execution.

The receipt records exactly:

```text
receipt_schema_version
execution_id
role
reviewer_profile_id
protocol_bundle_sha256
input
isolated_context
cross_reviewer_visibility_before_seal
tools_enabled
runtime
request
attempts
qualifying_attempt_id
resolved_identity
```

Required constants:

```text
isolated_context = true
cross_reviewer_visibility_before_seal = false
tools_enabled = false
```

The receipt format MUST remain runtime-transport-neutral. It MUST NOT require
`llm-runtime`. A future campaign runner may use `llm-runtime`, but the evidence
contract does not give it authority.

### One-to-one normalization

For schema 4.0:

```text
one raw finding -> exactly one normalized finding
```

No semantic merge. No semantic deduplication. No one-to-many mapping.

A normalized finding MUST have exactly one source.

The normalized:

```text
statement
argument
counterexample
```

MUST equal the exact corresponding raw finding values.

Normalization may add global identity and adjudication metadata only.

### Materiality asymmetry

Materiality remains derived from the existing seven axes. If ANY axis is true,
the finding is material.

If ALL seven axes are false, the non-material conclusion is not accepted merely
because one assessor says so. It requires a fresh hostile materiality challenge
bound to the exact candidate materiality assessment.

The challenge attempts all seven materiality axes. Its output contains
objections, not a pass/fail verdict.

Non-material is admissible only when the validated challenge output contains:

```text
objections = []
```

### Refutation challenge

The structured ADR-042 refutation grounds are preserved. A material refutation
requires a fresh challenge execution bound to the exact refutation subject.

Schema 4.0 removes the free field:

```text
surviving_material_argument
```

The result is derived mechanically from the challenge output:

```text
challenge objections == []
=> closure survived challenge
```

Any challenge objection means the refutation does not currently close the
finding. A challenge output MUST NOT carry an approval or rejection boolean.

### Challenge protocol

A challenge is falsification, not voting. The challenger receives only:

```text
canonical challenge prompt
canonical challenge packet
```

The challenger receives no other reviewer outputs unless those bytes are
explicitly part of the challenged candidate. No incidental findings are allowed
in challenge output v1; no `incidental_findings` field exists.

For a closure candidate:

* the initial candidate may be challenged;
* if objections exist, exactly ONE revised closure candidate may be produced;
* the revision requires a fresh challenge;
* if the revised candidate still receives objections, that closure path fails.

The maximum closure revisions is exactly `1`. Recursive LLM debate is not
introduced.

### Failure to refute is not proof

```text
failure to establish a valid refutation
!=
proof that the finding is true
```

A material finding stays `open` unless another branch is positively established
and challenged.

If the system cannot establish a valid refutation, a uniquely derived
correction, no normative impact, genuine product underdetermination, or a
genuine authority conflict, then the correct external outcome is:

```text
OPERATOR-ACTION-REQUIRED
```

It MUST NOT fabricate `DECISION-REQUIRED`.

### DECISION-REQUIRED boundary

`DECISION-REQUIRED` is reserved for:

```text
genuine product-semantic underdetermination
or
genuine unresolved product-authority conflict
```

Before emitting it, the protocol must attempt to show that existing authority
uniquely determines the answer. A successful unique derivation then enters the
ordinary derivation-challenge path.

In v1, a Decision Request is bound to:

```text
full current semantic subject S
+
full current review protocol P
+
exact finding
```

A narrower dependency slice is not implemented in v1.

### Auto-repair boundary

An automated repair is allowed only after:

1. the correction is established as uniquely derived from existing authority;
2. that derivation survives hostile challenge;
3. an exact candidate patch is produced;
4. the exact patch survives a repair challenge.

The patch executor then applies the exact approved patch and has no semantic
latitude. If the semantic subject changes, the old campaign becomes historical
and a full new campaign is required.

The repair runner is not implemented by this decision. This decision records
the protocol only.

### External outcomes

The campaign runner contract has exactly these normal external outcomes:

```text
GATE-A-READY
DECISION-REQUIRED
OPERATOR-ACTION-REQUIRED
```

No technical failure may be disguised as `DECISION-REQUIRED`. No product
decision may be invented to avoid `OPERATOR-ACTION-REQUIRED`.

### Product semantics unchanged

ADR-045 introduces no TURNLOCK product semantic change:

* no TURNLOCK product semantic changes;
* no new invariant;
* no claim change;
* no coverage change;
* no executable model;
* the Gate A semantic subject remains unchanged;
* ADR-045 MUST NOT be added to
  `formal/verification.yaml authority.architecture_decisions`;
* ADR-045 MUST NOT be added to
  `authority.abstraction_constraints`.

## Consequences

* Review protocol identity becomes explicit and versioned.
* Gate A currentness requires both the semantic subject and the review protocol.
* Reviewer qualification becomes protocol-owned rather than a free assertion.
* Model-version identity becomes evidence-derived.
* Completed but protocol-invalid responses remain sealed evidence.
* Finding normalization is strictly one-to-one and content-preserving.
* Non-material and refuted conclusions must survive fresh hostile challenges.
* A protocol change cannot erase a surviving finding.
* Stale-protocol findings remain durable and require current re-adjudication.
* Challenge output cannot carry a free verdict.
* External outcomes distinguish product decisions from operator action.
* No product semantics change and no executable formal model is introduced.

## Alternatives rejected

* Treating the review protocol as an unversioned convention: a stale or
  per-execution protocol could satisfy Gate A without detection. Rejected in
  favor of a content-addressed protocol bundle.
* Free per-execution `frontier-llm` assertions: unqualified models could count
  toward assurance. Rejected in favor of protocol-owned reviewer profiles.
* Runner-supplied `model_version`: aliases could inflate independent reviewer
  counts. Rejected in favor of evidence-derived resolution.
* Markdown raw reviewer output: interpretation could alter the sealed
  evidentiary content. Rejected in favor of structured JSON.
* Discarding protocol-invalid completed responses: evidence would be destroyed.
  Rejected in favor of sealing every completed response.
* Semantic merge or deduplication during normalization: a raw objection could
  disappear. Rejected in favor of strict one-to-one mapping.
* Accepting a non-material conclusion from a single assessor: symmetric
  falsification would not be attempted. Rejected in favor of a hostile
  materiality challenge.
* A free `surviving_material_argument` boolean: closure would not be derived
  from challenge objections. Rejected.
* Treating a protocol change as erasing old findings: a surviving finding could
  be silently dropped. Rejected in favor of re-adjudication.
* Fabricating `DECISION-REQUIRED` when no valid refutation was established:
  failure to refute is not proof. Rejected in favor of
  `OPERATOR-ACTION-REQUIRED`.

## Verification obligation

This decision requires mechanical enforcement of:

* exact canonical protocol-bundle validation, canonical JSON serialization, and
  referenced prompt/schema artifact hashes;
* unique reviewer profile IDs and protocol-qualified reviewer profiles with
  `frontier_eligible == true`;
* evidence-derived model-version resolution for both allowed identity kinds;
* `(provider, model_version)` effective-identity anti-alias counting;
* structured JSON raw reviewer outputs with objective/finding reciprocity;
* sealed execution receipts with at most one qualified attempt;
* exact one-to-one normalized finding mapping and content equality;
* zero-objection materiality and refutation challenges;
* stale-protocol finding re-adjudication under the current protocol;
* exclusion of the review protocol and `current_protocol_bundle` from the Gate A
  semantic subject;
* preservation of the Gate A semantic subject SHA.

These properties are implemented by `formal/reviews/review-evidence.schema.json`,
the protocol bundle and schema artifacts under `formal/reviews/`,
`scripts/check-formal-traceability.py`, and covered by
`scripts/tests/test-formal-traceability.py`.

## References

* `AGENTS.md`
* `formal/README.md`
* `formal/reviews/README.md`
* `formal/reviews/review-evidence.schema.json`
* `formal/reviews/review-protocol-bundle.schema.json`
* `formal/reviews/protocols/gate-a-campaign-protocol-v1.json`
* `formal/reviews/prompts/gate-a-initial-review-v1.md`
* `formal/reviews/prompts/gate-a-adjudication-v1.md`
* `formal/reviews/prompts/gate-a-challenge-v1.md`
* `formal/reviews/prompts/gate-a-repair-v1.md`
* `formal/verification.yaml`
* `docs/formal/README.md`
* `docs/adr/adr-041-establish-turnlock-formal-assurance-architecture.md`
* `docs/adr/adr-042-define-auditable-hostile-review-campaign-execution-and-adjudication.md`
* `docs/adr/adr-043-bind-hostile-review-evidence-to-exact-reviewed-inputs.md`
* `docs/adr/adr-044-require-one-unambiguous-gate-a-review-subject.md`
* `scripts/check-formal-traceability.py`
* `scripts/tests/test-formal-traceability.py`
