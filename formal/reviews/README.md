# Hostile semantic-review evidence

This directory stores durable evidence of executed hostile semantic-review
campaigns over TURNLOCK formal-assurance artifacts.

The existence of `review-evidence.schema.json` is **not** evidence that any
review occurred. The absence of a review record means that no review evidence
exists. Review requirements are satisfied only by records that exist, validate,
and are current for the exact reviewed artifact version. Review evidence is a
distinct evidence class from TLC or other mechanical checker evidence.

Hostile review is adversarial falsification, not majority voting. A single
surviving valid material objection blocks acceptance of the reviewed semantic
link until it is resolved or refuted, regardless of how many reviewers approved.
Review evidence never constitutes mathematical proof of natural-language/formal
equivalence; the strongest valid conclusion is bounded reviewed semantic
correspondence under the executed review protocol.

The evidence contract is `review-evidence.schema.json` schema version `2.0`.
Version 2.0 is a breaking contract; no compatibility branch for the previous
`1.1` shape exists. No `1.1` review record was ever authored, so no migration is
required.

Review records are declarative evidence artifacts. They MUST validate against
`review-evidence.schema.json`; the repository formal traceability checker
validates them, validates their referenced artifacts, and derives review-coverage
state from them without inventing review results. Structurally or referentially
invalid review evidence makes Gate A BLOCKED; it is never silently ignored and
it can never coexist with a Gate A READY summary.

## Campaign artifacts

A campaign separates, conceptually and durably:

```text
canonical review packet
canonical review prompt
reviewer execution metadata
sealed raw reviewer output
normalized campaign evidence
adjudication / challenge evidence
```

The review packet, the prompt, the raw reviewer output, and any challenge output
are repository-relative artifacts content-addressed by SHA-256. A raw output
becomes SEALED when its bytes are fixed and hashed. After sealing there is no
edit, no cleanup, no rewriting, and no finding deletion. Normalization and
adjudication are recorded elsewhere in the campaign evidence.

The campaign evidence connects every execution to its execution identity, model
identity, packet SHA-256, prompt SHA-256, attack objectives, isolation
declaration, sealed raw-output artifact, and declared raw finding IDs.

## Operational independence

Independence is **operational independence**, not a probabilistic independence
claim about models.

A reviewer execution counts toward the declared
`minimum_independent_reviewers` only when it:

- analyzes the same exact reviewed subject;
- uses the same canonical review packet;
- uses the same canonical review prompt;
- executes in a separate context;
- has no direct or indirect access to the outputs, findings, or adjudications of
  any other reviewer before its own raw output is sealed;
- belongs to a distinct model identity.

Model identity is exactly:

```text
(provider, model, model_version)
```

Two executions of the same model identity may be recorded, but they count as one
identity for the independent-reviewer minimum. Provider inequality
(`provider A != provider B`) is not required. Provider and model-family diversity
is recommended campaign quality because it reduces common-mode risk, but it is
not the universal mechanical definition of independence.

## Attack coverage per execution

Every reviewer execution that counts toward the Gate A campaign must
individually cover the complete attack-objective set declared by:

```text
formal/verification.yaml
policy.hostile_review.required_attack_objectives.assurance-decomposition
```

Aggregated campaign coverage is not sufficient. A qualifying execution that
omits an objective is not qualifying, even when another execution covered that
objective.

## Sealed outputs and lossless normalization

Every raw finding declared by a reviewer execution must have exactly one
destination in the normalized finding ledger.

Several raw findings may merge into one normalized finding. A single raw finding
cannot be consumed by more than one normalized finding. A normalized finding
preserves its exact source pairs:

```text
(execution_id, raw_finding_id)
```

No declared raw finding may be lost. An unmapped raw finding, a raw finding
mapped to several normalized findings, or a source that references an unknown
execution or unknown raw finding is a review-evidence integrity failure.

## Derived materiality

`material` is not a stored boolean. Materiality is derived from these boolean
impact axes:

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

Every finding must carry a materiality `rationale` explaining why, assuming the
finding is true, the Gate A subject could or could not remain unchanged while
still legitimately authorizing the candidate model. Materiality measures the
counterfactual impact of a true finding; it does not measure confidence,
severity, reviewer consensus, or probability.

## Status semantics

```text
open     = the argument is neither refuted, nor resolved, nor routed.
routed   = the argument may be valid, but its earliest upstream cause requires
           resolution outside the relation currently under review.
resolved = the finding was valid and its cause has been corrected.
refuted  = at least one necessary premise or inference of the finding was
           invalidated by an argument traceable to the subject or its exact
           authority, without a new normative assumption.
```

For a material finding:

```text
open     blocks Gate A
routed   blocks Gate A
resolved blocks Gate A while it still belongs to the current subject
refuted  may cease to block only when the refutation contract is satisfied
```

A current review cannot use `material + resolved` as a shortcut to READY. If the
finding was material and valid, its resolution normally changes a dependency of
the subject or resolves an upstream authority, and the review becomes historical
and stale for the new bytes. A real material correction therefore requires a new
current campaign rather than patching an old campaign's evidence.

## Structured refutation and hostile challenge

A refutation must choose exactly one `ground`:

```text
premise-false
target-misidentified
counterexample-outside-authority
consequence-does-not-follow
already-accounted-for
```

It must contain the attacked premise or inference, evidence references, an
argument, and a counterexample disposition when the finding contains a
counterexample. A counterexample disposition classifies the counterexample as
exactly one of `impossible`, `outside-scope`, or `non-concluding`, with a
rationale.

Reviewer majority, another reviewer not finding the defect, author intent,
preferred interpretation, difficulty reproducing, and a future TLA+
implementation are never refutations.

Every refutation of a material finding must itself have a durable hostile
challenge artifact. The challenge identifies an existing reviewer execution,
identifies the exact challenge output by path and SHA-256, declares
`surviving_material_argument = false`, and contains a rationale. The original
reviewer's consent is not authority; the only question is whether a valid
material argument or counterexample survives.

## Subject kinds

Review evidence identifies its reviewed subject with one of two exact shapes:

```text
artifact subject
= exact bytes of a repository artifact

derived subject
= mechanically canonicalized semantic review scope whose identity is independent
  of unrelated physical-file changes
```

`gate-a-assurance-decomposition-v1` is the only current derived subject selector.

Its dependency set is:

```text
normative specification bytes
ADR-015 bytes
ADR-041 bytes
ADR-040 bytes
manifest schema_version/project
formal semantic domain declarations
behavioral modalities
assurance domains
83 claim contents and provenance
42 normative coverage mappings
```

Its explicit exclusions are:

```text
formal_realizations
hostile-review adequacy policy
mechanical-evidence policy
readiness-gate declarations
generated docs
review records
result records
Git commit identity
```

ADR-042 governs the review protocol. It is not a dependency of the derived
subject and is not listed in
`formal/verification.yaml authority.architecture_decisions`.

### Canonicalization

The Gate A derived subject is canonical over semantically unordered collections.

The following collections are order-insensitive when deriving the subject:

- architecture decision references
- abstraction constraint references
- formal semantic domains, ordered canonically by `id`
- behavioral modalities
- assurance domains
- claims, ordered canonically by claim ID
- claim normative sources
- normative coverage, ordered canonically by invariant ID
- formal claim references
- residual claim references

Reordering any of those collections without changing their contents does not
invalidate an existing Gate A review.

Changing the content of any included object still changes the derived subject.
Canonicalization removes representation-order sensitivity; it does not remove
semantic dependencies.

`formal_semantic_domains` is canonicalized by `id` only because domain IDs are
required to be unique. Duplicate IDs are invalid; they are never tie-broken by
module, path, declaration order, or serialized object content.

A manifest with duplicate domain IDs has no valid Gate A derived subject.

A review record's `repository_commit` records provenance of execution.
It does not by itself determine review currentness.

A future `formal_realization` may therefore be added after Gate A without
invalidating the assurance-decomposition review, provided no dependency of the
derived subject changed.

## Gate A review adequacy

Gate A requires a current assurance-decomposition campaign that:

- reviews the current exact Gate A subject;
- is structurally and referentially valid;
- references only existing packet, prompt, raw, and challenge artifacts whose
  bytes match their declared SHA-256;
- has at least `minimum_independent_reviewers` distinct
  `(provider, model, model_version)` model identities;
- covers the complete required attack-objective set in each qualifying
  execution;
- uses the same canonical packet and the same canonical prompt across
  qualifying executions;
- declares isolated contexts and no cross-reviewer visibility before sealing;
- represents every declared raw finding exactly once in the normalized ledger;
- has no current material `open`, `routed`, or `resolved` finding;
- carries a valid structured refutation and a valid hostile challenge for every
  current material `refuted` finding.

All current assurance-decomposition review records for the exact current subject
participate in surviving-finding evaluation. One material `open`, `routed`, or
`resolved` finding in any current review blocks Gate A even if another review is
clean. No majority vote can override the finding.

A changed subject requires a full new review campaign over the new bytes. Stale
review evidence remains historical evidence but does not satisfy the current
manifest's Gate A.

## Path conventions

Campaign artifacts use these repository-relative conventions:

```text
formal/reviews/packets/*.md
formal/reviews/prompts/*.md
formal/reviews/raw/*.md
formal/reviews/challenges/*.md
```

Their absence is normal while no real hostile-review campaign has been executed;
an empty directory is a valid state and is not evidence of a review.

## Repository integrity

Malformed JSON/YAML review evidence is a repository-integrity failure and is not
silently ignored.

A non-mapping review file is also an integrity failure.

Any review-evidence integrity failure forces Gate A BLOCKED with the reason
`hostile review evidence integrity failure`. It can never coexist with a Gate A
READY summary.
