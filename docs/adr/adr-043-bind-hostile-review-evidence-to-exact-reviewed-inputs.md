---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Bind hostile-review evidence to exact reviewed inputs"
id: "ADR-043"
status: "accepted"
date: "2026-09-19"
decision_body_sha256: "dad6d2fc83e076c61fc374958e45bea29cb15ece4cc5185b714c164bbf5509a4"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-042"
  supersedes: []
  confirms:
    - "ADR-041"
governs:
  - "Canonical Gate A hostile-review packet identity"
  - "Hostile-review packet-to-subject binding"
  - "Refutation-to-challenge binding"
  - "Hostile-review repository path containment"
---

# ADR-043: Bind hostile-review evidence to exact reviewed inputs

## Context

ADR-042 defined auditable hostile-review campaign execution and adjudication.
Review-evidence schema version 2.0 closes:

```text
reviewer identity
operational independence
per-execution attacks
sealed raw outputs
lossless finding normalization
derived materiality
structured refutation
hostile challenge existence
```

Those properties are necessary but not sufficient for exact evidence identity.
Three trust gaps remain.

First, a campaign can declare the exact current Gate A subject while supplying
an arbitrary content-addressed review packet. The contract proves that
qualifying executions shared one packet, but not that this packet actually
represented the reviewed Gate A subject. A fixture test demonstrates the gap: a
trivial packet containing only a heading can currently participate in a campaign
that derives Gate A READY if all declarative metadata is otherwise valid. This
has not occurred in production, and no real hostile-review campaign exists yet.

Second, a material refutation can be changed after its challenge was produced.
The contract proves that a challenge artifact existed, but not that it
challenged the exact refutation currently recorded, because the challenge is not
bound to the exact refutation payload.

Third, a repository-relative artifact path may still resolve through a symlink.
A repository-looking path whose filesystem resolution may escape or alias
through symlinks weakens exact artifact identity.

## Discovery classification

```text
assurance-defect
```

Exact reasons:

```text
A. the evidence contract proves that reviewers shared one packet,
   but not that this packet actually represented the reviewed Gate A subject;

B. the evidence contract proves that a challenge artifact existed,
   but not that it challenged the exact refutation currently recorded;

C. the evidence contract accepts repository-looking paths whose filesystem
   resolution may escape or alias through symlinks, weakening exact artifact identity.
```

None of the three defects is a product-semantics discovery. No TURNLOCK product
meaning, invariant identity, assurance claim, or normative coverage mapping is
introduced, amended, or reinterpreted.

## Decision

### Canonical Gate A review packet

Every review record whose `review_class` is `assurance-decomposition` and which
declares a derived subject with:

```text
selector = gate-a-assurance-decomposition-v1
```

MUST use a self-contained canonical Gate A review packet.

The packet is NOT a new semantic authority. It is a canonical self-contained
projection of the exact reviewed subject and its textual authority. It carries
the exact readable normative authority, not merely digests.

The packet is a JSON file:

```text
formal/reviews/packets/*.json
```

It is no longer Markdown.

The prompt, raw, and challenge artifacts remain Markdown:

```text
formal/reviews/prompts/*.md
formal/reviews/raw/*.md
formal/reviews/challenges/*.md
```

### Canonical packet payload

The exact logical payload is:

```json
{
  "packet_schema_version": 1,
  "subject": {
    "subject_type": "derived",
    "selector": "gate-a-assurance-decomposition-v1",
    "sha256": "<subject sha256>"
  },
  "subject_payload": {
    "...": "exact canonical Gate A subject payload"
  },
  "authority_contents": [
    {
      "role": "normative-spec",
      "id": null,
      "path": "...",
      "sha256": "...",
      "content_utf8": "..."
    },
    {
      "role": "architecture-decision",
      "id": "ADR-...",
      "path": "...",
      "sha256": "...",
      "content_utf8": "..."
    },
    {
      "role": "abstraction-constraint",
      "id": "ADR-...",
      "path": "...",
      "sha256": "...",
      "content_utf8": "..."
    }
  ]
}
```

The exact ordering of `authority_contents` is:

```text
1. normative spec
2. architecture decisions sorted lexicographically by ADR id
3. abstraction constraints sorted lexicographically by ADR id
```

For the current subject this means the embedded authority includes exactly the
current subject dependencies:

```text
normative specification
ADR-015
ADR-041
ADR-040
```

The generic builder derives that set from `subject_payload.authority`. Those
four identifiers are not hard-coded.

### Canonical packet serialization

Canonical JSON value serialization is defined exactly as:

```python
json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
).encode("utf-8")
```

This serialization has no trailing newline.

A canonical JSON document for the packet is:

```python
canonical_json_bytes(packet_payload) + b"\n"
```

Therefore:

```text
subject SHA
=
SHA256(canonical_json_bytes(subject_payload))

packet artifact SHA
=
SHA256(canonical_json_bytes(packet_payload) + "\n")
```

These two hashes are intentionally different identities. The current Gate A
subject serialization and hash are not changed.

### Self-contained packet validation

A packet referencing a Gate A derived subject is valid only if ALL of the
following are true:

```text
- packet bytes are valid UTF-8;
- packet bytes parse as a JSON object;
- packet bytes are exactly the canonical JSON document serialization of the
  parsed packet object;
- the exact top-level key set is:
    packet_schema_version
    subject
    subject_payload
    authority_contents;

- packet_schema_version == 1;

- packet.subject has exactly:
    subject_type
    selector
    sha256;

- packet.subject.subject_type == derived;
- packet.subject.selector == gate-a-assurance-decomposition-v1;

- packet.subject_payload.subject_schema_version == 1;
- packet.subject_payload.selector == gate-a-assurance-decomposition-v1;

- SHA256(canonical_json_bytes(subject_payload)) == packet.subject.sha256;

- packet.subject exactly appears in the review record's subjects;

- authority_contents has no omissions;
- authority_contents has no extra entries;
- authority_contents has the exact required ordering;

- each authority entry metadata matches the corresponding descriptor in
  subject_payload.authority exactly;

- each content_utf8 is a string;

- SHA256(content_utf8.encode("utf-8")) == the authority entry sha256;

- therefore the embedded authority content is cryptographically tied to the
  authority hash included in the reviewed subject payload.
```

Packet validation MUST remain possible after the repository has evolved.
Packet validation MUST be self-contained from the packet plus its review record.
A stale historical packet MUST NOT be validated by comparing it to the CURRENT
manifest.

### Current Gate A implication

For a CURRENT Gate A campaign, the existing rule:

```text
record subjects contains exact current derived subject
```

combined with packet self-validation implies:

```text
packet.subject == current derived subject
```

An arbitrary or trivial packet therefore cannot satisfy Gate A.

### Refutation challenge binding

A canonical `hostile-refutation-challenge-v1` subject is defined for each
refuted finding. It binds the challenge to the exact finding and the exact
refutation it challenges.

The challenge subject payload exact top-level structure is:

```json
{
  "subject_schema_version": 1,
  "selector": "hostile-refutation-challenge-v1",
  "finding": {
    "...": "canonical finding and refutation data excluding challenge itself"
  }
}
```

The embedded `finding` MUST contain:

```text
finding_id
sources
statement
argument
counterexample
materiality
status
refutation
```

`status` must be exactly:

```text
refuted
```

`refutation` must contain exactly:

```text
kind
ground
attacked_premise_or_inference
evidence_references
argument
counterexample_disposition
```

It MUST NOT contain `challenge`.

Unordered fields are canonicalized before hashing without mutating the review
record:

```text
sources:
sort ascending by (execution_id, raw_finding_id)

evidence_references:
sort lexicographically
```

The binding hash is exact:

```text
challenged_refutation_sha256
=
SHA256(
  canonical_json_bytes(
    hostile-refutation-challenge-v1 payload
  )
)
```

Every non-null challenge object must contain `challenged_refutation_sha256` and
it must equal the checker-derived value for the exact current finding and
refutation.

Therefore changing any of:

```text
finding_id
sources
statement
argument
counterexample
materiality
refutation ground
attacked premise or inference
evidence references
refutation argument
counterexample disposition
```

invalidates the previous challenge binding. Changing only source or
evidence-reference ordering does not change the challenge subject hash.

### Challenge validation scope

The existing rule remains:

```text
material + refuted requires a non-null challenge
```

It is strengthened as follows:

```text
ANY non-null challenge,
including a challenge attached to a non-material refuted finding,
must be fully validated.
```

Every supplied challenge must have:

```text
existing challenger_execution_id
valid exact challenged_refutation_sha256
existing challenge output
correct challenge output SHA-256
repository-contained non-symlink path
surviving_material_argument = false
non-empty rationale
```

A non-material refuted finding may have `challenge = null`. A material refuted
finding may not.

### Symlink and path containment

Every hostile-review artifact reference must denote actual bytes reached without
traversing ANY symlink. This applies to:

```text
review packet
prompt
raw reviewer output
challenge output
```

The checker MUST reject:

```text
- a final artifact that is a symlink;
- any intermediate path component that is a symlink;
- any resolved target escaping the repository root;
- any resolved target escaping its allowed review-artifact directory.
```

This property is stronger than rejecting `..` in the textual path. Every path
component from the resolved repository root to the referenced artifact must be a
non-symlink filesystem object, and the artifact itself must be a regular file.
No symlink-based alias is admissible, even when its resolved target remains
inside the repository.

### Gate semantics

ADR-043 changes review-evidence validity only. It MUST NOT change:

```text
product semantics
claims
coverage
Gate A subject dependencies
Gate A selector
Gate A subject schema version
Gate A current SHA
```

The current SHA remains:

```text
2b0dd42fb07d67f3a38d0414f12df49ecb9df640f12c805ee98b6af3a1db979b
```

ADR-043 MUST NOT be added to:

```text
formal/verification.yaml
authority.architecture_decisions
```

## Consequences

* Gate A packet identity becomes independently inspectable.
* Historical packets remain self-validating against their declared historical
  subjects.
* A challenge becomes stale when the exact refutation it challenged changes.
* Repository-looking paths can no longer alias different bytes through
  symlinks.
* The review-evidence schema changes incompatibly from 2.0 to 3.0.
* No real v2 campaign evidence exists, so no campaign evidence migration is
  required.
* No product semantics change.
* No executable formal model is introduced.

## Alternatives rejected

* Trust `protocol.review_packet.sha256` without packet-to-subject binding.
  Rejected: it proves byte identity, not semantic input identity.
* Compare every packet only against current repository state. Rejected: it would
  make legitimate stale historical evidence unverifiable.
* Put only subject hashes in the packet. Rejected: reviewers need the exact
  readable normative authority, not merely digests.
* Allow noncanonical JSON packet formatting. Rejected: it would create multiple
  byte identities for the same packet content.
* Bind challenge only by `finding_id`. Rejected: refutation content could change
  without invalidating the challenge.
* Bind challenge only by review-record SHA. Rejected: it creates unnecessary
  coupling to unrelated record fields.
* Allow symlinks whose targets remain inside the repository. Rejected: the
  declared path would no longer be the direct filesystem identity of the
  reviewed artifact.
* Modify ADR-042. Rejected: accepted ADR bodies are immutable; later decisions
  amend them.

## Verification obligation

ADR-043 requires mechanical tests for:

* canonical packet construction, exact subject identity, and exact embedded
  authority contents;
* canonical JSON document serialization of the packet;
* rejection of trivial, subject-mismatched, incomplete, extra, hash-mismatched,
  and noncanonical Gate A packets;
* self-validation of a stale historical packet after the current subject
  changes, without comparison to current repository authority;
* required `challenged_refutation_sha256` schema validation;
* challenge invalidation after refutation-content changes;
* challenge-subject hash invariance to source and evidence-reference reordering;
* validation of every supplied challenge regardless of finding materiality;
* rejection of final and intermediate symlink traversal in review-evidence
  artifact paths.

## References

* `AGENTS.md`
* `docs/adr/adr-041-establish-turnlock-formal-assurance-architecture.md`
* `docs/adr/adr-042-define-auditable-hostile-review-campaign-execution-and-adjudication.md`
* `docs/formal/README.md`
* `formal/README.md`
* `formal/reviews/README.md`
* `formal/reviews/review-evidence.schema.json`
* `formal/verification.yaml`
* `scripts/check-formal-traceability.py`
* `scripts/tests/test-formal-traceability.py`
