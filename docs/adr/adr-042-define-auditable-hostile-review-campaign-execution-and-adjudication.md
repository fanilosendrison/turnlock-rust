---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Define auditable hostile-review campaign execution and adjudication"
id: "ADR-042"
status: "accepted"
date: "2026-09-19"
decision_body_sha256: "b0d31779c5a59df4583f37a36ed72f52f1426bb48b0ef56272fd163fa3e33b3a"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-041"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Operational independence of hostile-review executions"
  - "Sealed hostile-review execution evidence"
  - "Lossless hostile-review finding normalization"
  - "Hostile-review materiality and adjudication"
  - "Gate A hostile-review readiness mechanics"
---

# ADR-042: Define auditable hostile-review campaign execution and adjudication

## Context

ADR-041 already requires multiple independent frontier LLM reviewers, adversarial
falsification rather than majority voting, durable and inspectable review
evidence, exact reviewed artifacts, reviewers and models, a review protocol,
findings, dispositions, a re-review relationship, and the rule that one valid
material minority objection blocks acceptance.

The existing hostile-review evidence contract at schema version 1.1 does not
make those properties sufficiently verifiable:

```text
- reviewer count can count several entries of the same model identity;
- attack coverage is declared at campaign level, not per reviewer execution;
- no sealed raw reviewer output is connected to the evidence;
- normalization can silently lose a raw objection;
- material is a free boolean;
- refuted/resolved require only a free disposition_rationale;
- material + resolved on the current subject can currently leave Gate A READY.
```

## Discovery classification

```text
assurance-defect, resolved by this ADR
```

The defect is in the hostile-review evidence contract and its mechanical
enforcement. It does not concern any TURNLOCK product semantics. No normative
meaning, invariant identity, assurance claim, or normative coverage mapping is
introduced, amended, or reinterpreted.

## Decision

### Operational independence

Independence of hostile review is defined as **operational independence**. This
decision makes no claim of probabilistic independence between models.

A reviewer execution may count toward `minimum_independent_reviewers` only when
it:

* analyzes the same exact reviewed subject;
* uses the same canonical review packet;
* uses the same canonical review prompt;
* executes in a separate context;
* has no direct or indirect access to the outputs, findings, or adjudications of
  any other reviewer before its own raw output is sealed;
* belongs to a distinct model identity.

Model identity is defined exactly as:

```text
model identity = (provider, model, model_version)
```

Two executions of the same model identity may be recorded, but they count as one
identity for the independent-reviewer minimum. Provider inequality
(`provider A != provider B`) is not an architectural requirement. Provider and
model-family diversity is recommended campaign quality because it reduces
common-mode risk, but it is not the universal mechanical definition of
independence.

### Complete attack coverage per reviewer execution

Every reviewer execution that counts toward the Gate A campaign must
individually cover the complete set of attack objectives required by:

```text
formal/verification.yaml
policy.hostile_review.required_attack_objectives.assurance-decomposition
```

Aggregated campaign coverage is not sufficient. For the current Gate A campaign,
each qualifying reviewer execution must cover the 14 currently declared
objectives.

### Campaign artifacts

The following are conceptually and durably separate:

```text
canonical review packet
canonical review prompt
reviewer execution metadata
sealed raw reviewer output
normalized campaign evidence
adjudication / challenge evidence
```

The review packet, the prompt, the raw output, and any challenge output are
repository-relative artifacts content-addressed by SHA-256. A raw output becomes
SEALED when its bytes are fixed and hashed.

After sealing:

```text
no edit
no cleanup
no rewriting
no finding deletion
```

Normalization and adjudication are recorded elsewhere.

The campaign evidence must connect every execution to its execution identity,
model identity, packet hash, prompt hash, attack objectives, isolation
declaration, sealed raw-output artifact, and declared raw finding IDs.

### Lossless finding normalization

Every raw finding declared by a reviewer execution must have exactly one
destination in the normalized finding ledger.

Several raw findings may be merged into one normalized finding. A single raw
finding cannot be consumed by more than one normalized finding.

A normalized finding must preserve its exact source pairs:

```text
(execution_id, raw_finding_id)
```

No raw finding may disappear silently.

### Materiality

`material` is not a free boolean. Materiality must be DERIVED from an explicit
impact structure with exactly these boolean axes:

```text
authority_or_upstream_decision
claim_structure
normative_provenance
modality_or_assurance_domain
coverage_or_residual_assurance
interaction_scope
candidate_model_authorization
```

A finding is material if and only if at least one axis is `true`.

Every finding must carry a materiality `rationale`. The rationale explains why,
assuming the finding is true, the Gate A subject could or could not remain
unchanged while still legitimately authorizing the candidate model.

Materiality measures the counterfactual impact of the finding if it is true. It
does not measure:

```text
confidence
severity
reviewer consensus
probability
```

### Status semantics

```text
open
= the argument is neither refuted, nor resolved, nor routed.

routed
= the argument may be valid, but its earliest upstream cause requires
  resolution outside the relation currently under review.

resolved
= the finding was valid and its cause has been corrected.

refuted
= at least one necessary premise or inference of the finding was invalidated by
  an argument traceable to the subject or to its exact authority, without a new
  normative assumption.
```

For a MATERIAL finding:

```text
open     → blocks Gate A
routed   → blocks Gate A
resolved → blocks Gate A while it still belongs to the current subject
refuted  → may cease to block only when the refutation contract is satisfied
```

The exact reason for `material + resolved` is that if the finding was material
and valid, its resolution must normally change a dependency of the subject or
resolve an upstream authority; the review then becomes historical and stale. A
current review therefore cannot use `material + resolved` as a shortcut to
READY.

### Refutation

A refutation must choose exactly one `ground` from:

```text
premise-false
target-misidentified
counterexample-outside-authority
consequence-does-not-follow
already-accounted-for
```

It must contain:

```text
attacked_premise_or_inference
evidence_references
argument
counterexample_disposition when a counterexample exists
```

None of the following is ever a refutation:

```text
reviewer majority
another reviewer did not find the defect
author intent
preferred interpretation
difficulty reproducing
future TLA+ implementation
```

If the finding contains a counterexample, the refutation must classify that
counterexample as exactly one of:

```text
impossible
outside-scope
non-concluding
```

with a rationale.

### Hostile challenge of material refutations

Every refutation of a MATERIAL finding must itself have a durable challenge
artifact. The challenge must:

* identify an existing reviewer execution;
* identify the exact challenge output by path and SHA-256;
* declare `surviving_material_argument = false` for a `refuted` status to be
  admissible;
* contain a rationale.

The original reviewer's consent is not authority. The only question is: does a
valid material argument or counterexample survive?

### Gate A readiness

A current assurance-decomposition campaign satisfies Gate A only when:

* it reviews the current exact Gate A subject;
* its evidence is structurally and referentially valid;
* every referenced packet, prompt, raw, and challenge artifact exists and
  matches its SHA-256;
* it has at least `minimum_independent_reviewers` distinct model identities;
* every qualifying execution individually covers all required attack
  objectives;
* the qualifying executions use the same canonical packet and the same
  canonical prompt;
* their contexts are declared isolated;
* cross-reviewer visibility before sealing is false;
* every raw finding is represented exactly once in the normalized ledger;
* no current material finding is `open`;
* no current material finding is `routed`;
* no current material finding is `resolved`;
* every current material `refuted` finding satisfies the structured refutation
  contract and has a valid hostile challenge.

An invalid review-evidence contract must make Gate A BLOCKED. It must not merely
fail repository integrity while Gate A still appears READY.

### Gate A subject remains unchanged

ADR-042 governs the review PROTOCOL, not the semantics of the assurance
decomposition under review.

ADR-042 MUST NOT be added to
`formal/verification.yaml authority.architecture_decisions`.

The selector remains:

```text
gate-a-assurance-decomposition-v1
```

The subject schema version remains:

```text
1
```

At the acceptance of this ADR (2026-09-19), the fingerprint of the current valid
subject is exactly:

```text
2b0dd42fb07d67f3a38d0414f12df49ecb9df640f12c805ee98b6af3a1db979b
```

The hostile-review adequacy protocol remains outside the reviewed subject. The
live derived subject value remains owned by `formal/verification.yaml` and its
generated projection, not by this ADR.

## Consequences

* Hostile-review evidence integrity is stronger.
* Operational independence is explicit and mechanically checkable.
* Campaign results remain review-based bounded assurance, never proof.
* Each campaign produces more repository artifacts.
* Material findings are intentionally easier to open than to close.
* A real subject correction forces a new campaign rather than patching an old
  campaign.
* No product semantics are added.
* No executable formal model is introduced.

## Alternatives rejected

* Campaign-level attack coverage only: a single execution could omit an attack
  objective because another execution covered it, so no individual reviewer
  would have attempted the complete adversarial obligation. Rejected in favor of
  per-execution coverage.
* Counting raw reviewer records as independent: repeated records of one model
  identity would inflate independence without adding a distinct interpretation
  source. Rejected in favor of distinct
  `(provider, model, model_version)` identities.
* Majority voting: a valid material minority objection must block acceptance.
  Already rejected by ADR-041 and preserved here.
* Free-form material boolean: it cannot be reviewed or mechanically verified.
  Rejected in favor of materiality derived from explicit impact axes.
* Free-form refutation rationale: it cannot be checked for a traceable ground or
  for counterexample disposition. Rejected in favor of the structured refutation
  contract.
* Editing raw outputs after execution: it destroys the sealed evidence relation.
  Rejected; raw outputs are immutable after sealing.
* Allowing resolved material findings to satisfy current Gate A: resolution of a
  material finding normally changes the subject, so the previous review is stale
  for the new bytes. Rejected.
* Requiring provider diversity as the universal independence definition:
  provider diversity is recommended campaign quality, but it is not a sound
  universal mechanical rule. Rejected.

## Verification obligation

This ADR requires the following properties to be mechanically enforced:

* review evidence schema version 2.0 and its structural constraints;
* artifact identity validation for packet, prompt, raw-output, and challenge
  references;
* execution-level packet and prompt agreement with the campaign protocol;
* uniqueness of execution identities and raw-output paths;
* lossless raw-finding to normalized-finding ledger coverage;
* materiality derived only from the seven declared impact axes;
* structured refutation validation, including counterexample disposition and
  material-refutation challenges;
* Gate A BLOCKED whenever review evidence is structurally or referentially
  invalid;
* global blocking of current material `open`, `routed`, and `resolved` findings;
* per-execution required attack coverage and distinct model-identity counting.

These properties are implemented by
`formal/reviews/review-evidence.schema.json` and
`scripts/check-formal-traceability.py`, and covered by
`scripts/tests/test-formal-traceability.py`.

## References

* `AGENTS.md`
* `formal/README.md`
* `formal/reviews/README.md`
* `formal/reviews/review-evidence.schema.json`
* `formal/verification.yaml`
* `docs/formal/README.md`
* `docs/adr/adr-041-establish-turnlock-formal-assurance-architecture.md`
* `scripts/check-formal-traceability.py`
* `scripts/tests/test-formal-traceability.py`
