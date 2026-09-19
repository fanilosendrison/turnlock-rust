---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Require one unambiguous Gate A review subject"
id: "ADR-044"
status: "accepted"
date: "2026-09-19"
decision_body_sha256: "c118077969f95caaf28e882e032522e0a0e2ad2aa4f0bacec0269b7db78a13be"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-043"
  supersedes: []
  confirms:
    - "ADR-042"
governs:
  - "Gate A review-record subject cardinality"
  - "Gate A packet-to-record subject identity"
  - "Gate A current-review subject selection"
---

# ADR-044: Require one unambiguous Gate A review subject

## Context

ADR-043 guarantees that a Gate A review packet is self-contained and exact:

```text
packet subject hash ← packet subject_payload
packet authority contents ← packet subject authority
packet subject ∈ review record subjects
```

The review record `subjects` field remains a multi-valued array.

The checker therefore used two independent existential matches:

```text
Gate A currentness:
ANY record subject == current subject

packet binding:
packet.subject == ANY record subject
```

That leaves the following record insufficiently constrained:

```text
subjects = [C, F]

C = current Gate A subject
F = second Gate A derived subject

packet.subject = F
```

In this structure:

```text
C can make the record current
F can satisfy packet membership
```

without imposing:

```text
packet.subject == C
```

Record currentness and packet binding matched against the subjects array
independently, so a record could contain the real current Gate A subject C and
another Gate A derived subject F while the packet was bound only to F.

No real hostile-review campaign exists, so no historical evidence migration is
required.

## Discovery classification

```text
assurance-defect
```

The Gate A review evidence contract allowed subject confusion because record
currentness and packet binding were existentially matched against the subjects
array independently.

A record could contain the real current Gate A subject C and another Gate A
derived subject F while the packet was bound only to F.

This defect belongs to the hostile-review evidence contract. It is not a
product-semantics discovery. No TURNLOCK product meaning, invariant identity,
assurance claim, or normative coverage mapping is introduced, amended, or
reinterpreted.

## Decision

### Definition of Gate A derived subject

A Gate A derived subject is exactly a `subjects[]` entry where:

```text
subject_type == "derived"
AND
selector == "gate-a-assurance-decomposition-v1"
```

No deduplication is permitted.

Two identical entries count as two entries.

Two different entries with the same selector also count as two entries.

### Cardinality

For any record where:

```text
review_class == "assurance-decomposition"
```

and which contains at least one Gate A derived subject:

```text
the number of Gate A derived subjects MUST equal exactly 1
```

Therefore both of the following are invalid:

```text
[C, C]
```

```text
[C, F]
```

when C and F are both Gate A derived subjects.

None of the following precedence rules may ever be applied:

```text
first wins
last wins
deduplicate
packet subject wins
current subject wins
```

The record is invalid evidence.

### Other subjects remain allowed

ADR-044 does not turn `subjects` into an array of size one.

Additional artifact subjects may coexist. A valid example is:

```text
subjects =
[
  C = unique Gate A derived subject,
  A = artifact subject
]
```

provided that:

```text
packet.subject == C
```

Artifact subjects participate neither in:

```text
Gate A currentness
```

nor in:

```text
Gate A packet subject identity
```

### Records without a Gate A derived subject

A record where:

```text
review_class == "assurance-decomposition"
```

that contains only artifact subjects remains structurally allowed.

It does not constitute a Gate A campaign.

It cannot satisfy Gate A.

The current artifact-only behavior is preserved. ADR-044 imposes
`exactly one` only when at least one Gate A derived subject is declared.

### Packet binding

For a valid Gate A assurance-decomposition record:

```text
gate_a_subjects = all Gate A derived subjects

len(gate_a_subjects) == 1

gate_a_subject = gate_a_subjects[0]
```

The rule is then exactly:

```text
packet.subject == gate_a_subject
```

and not:

```text
packet.subject in record.subjects
```

### Gate A currentness

Gate A currentness uses exactly the same extraction.

An assurance-decomposition record can be CURRENT only when:

```text
len(gate_a_subjects) == 1
AND
gate_a_subjects[0] == current_gate_a_subject
```

A record containing several Gate A derived subjects is not considered current,
even when one of them matches the current subject.

This remains true even when `derive_gate_a()` is called directly on
non-prevalidated records. The rule is a defense in depth.

### Required identity chain

After ADR-044, a current qualifying campaign must transitively guarantee:

```text
packet.subject
==
unique record Gate A derived subject
==
current Gate A derived subject
```

This is the central invariant of this ADR.

### Schema version remains unchanged

The review-evidence schema remains:

```text
3.0
```

and:

```text
formal/reviews/review-evidence.schema.json remains byte-for-byte unchanged.
```

The exact reason is:

```text
No serialized field or type changes.
The correction is a cross-field semantic and referential integrity rule
that the repository checker already owns.
```

### Gate A semantic subject remains unchanged

ADR-044 MUST NOT enter:

```text
formal/verification.yaml
authority.architecture_decisions
```

The Gate A subject remains:

```text
selector =
gate-a-assurance-decomposition-v1

subject_schema_version =
1

sha256 =
2b0dd42fb07d67f3a38d0414f12df49ecb9df640f12c805ee98b6af3a1db979b
```

## Consequences

* Subject confusion between record currentness and packet binding is eliminated.
* Duplicate Gate A derived subjects are invalid evidence.
* Additional artifact subjects remain permitted.
* Packet binding, evidence validation, and Gate A currentness share one
  subject-selection rule.
* Schema 3.0 remains unchanged.
* Historical evidence semantics remain inspectable.
* No product semantics change.
* No executable formal model is introduced.

## Alternatives rejected

### `subjects.maxItems = 1`

Rejected because additional artifact subjects are legitimate metadata and
evidence context and do not need to be forbidden.

### JSON Schema `uniqueItems`

Rejected because it cannot enforce the intended semantic role and cardinality
rule for distinct Gate A derived subjects and would not establish
packet/currentness identity.

### `packet.subject in subjects`

Rejected because membership is insufficient when several Gate A derived
subjects exist.

### first/last Gate A subject wins

Rejected because array order has no declared authority semantics.

### deduplicate identical subjects

Rejected because duplicate semantic identities are malformed evidence and must
not be silently normalized.

### leave `derive_gate_a()` as ANY-match

Rejected because currentness must use the same unique subject identity as packet
validation.

## Verification obligation

ADR-044 requires mechanical tests proving:

```text
[C,F] + packet F → rejected
[C,C] + packet C → rejected
[C] + packet F → rejected
[C,artifact] + packet C → valid
direct derive_gate_a([C,F]) cannot report READY
```

## References

* `AGENTS.md`
* `docs/adr/adr-042-define-auditable-hostile-review-campaign-execution-and-adjudication.md`
* `docs/adr/adr-043-bind-hostile-review-evidence-to-exact-reviewed-inputs.md`
* `docs/formal/README.md`
* `formal/README.md`
* `formal/reviews/README.md`
* `formal/reviews/review-evidence.schema.json`
* `formal/verification.yaml`
* `scripts/check-formal-traceability.py`
* `scripts/tests/test-formal-traceability.py`
