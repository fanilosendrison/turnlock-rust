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
