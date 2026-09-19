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

Exact artifact identity matters. Every record lists the reviewed subjects with
their exact SHA-256 hashes and the repository commit from which the review was
executed. Stale review evidence for an older artifact revision remains valid
historical evidence, but it does not satisfy review requirements for a changed
artifact. A changed subject requires a new review of the new bytes.

Review records are declarative evidence artifacts. They MUST validate against
`review-evidence.schema.json`; the repository formal traceability checker
validates them and derives review-coverage state from them without inventing
review results.

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

A review record's `repository_commit` records provenance of execution.
It does not by itself determine review currentness.

A future `formal_realization` may therefore be added after Gate A without
invalidating the assurance-decomposition review, provided no dependency of the
derived subject changed.

## Gate A review adequacy

Gate A assurance-decomposition review requires the exact attack-objective set
declared by `formal/verification.yaml`.

A review with incomplete attack coverage does not satisfy Gate A.

All current assurance-decomposition review records for the exact current
manifest participate in surviving-finding evaluation.

One material `open` or `routed` finding in any current review blocks Gate A even
if another review is clean.

No majority vote can override the finding.

Malformed JSON/YAML review evidence is a repository-integrity failure and is not
silently ignored.

A non-mapping review file is also an integrity failure.

Stale review evidence remains historical evidence but does not satisfy the
current manifest's Gate A.
