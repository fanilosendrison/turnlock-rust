---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Bind challenge executions to exact inputs and derive retry admissibility"
id: "ADR-046"
status: "accepted"
date: "2026-09-20"
decision_body_sha256: "d421b76751ff3a22cc62fa2ff08e05ea046e05332b52445f899dea433044f2d6"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-043"
    - "ADR-045"
  supersedes: []
  confirms:
    - "ADR-042"
governs:
  - "Challenge execution binding to exact canonical challenge packets"
  - "Checker-derived protocol-attempt outcome admissibility"
  - "Termination after the first protocol-valid completed response"
  - "Append-only hostile-review protocol artifact evolution"
  - "Protocol-bundle predecessor-chain validation"
---

# ADR-046: Bind challenge executions to exact inputs and derive retry admissibility

## Context

### A. False `protocol-invalid`

ADR-045 prohibits retrying a semantically/protocol-valid result, but the schema
and checker trusted the runner-declared attempt `outcome`. A valid sealed output
could consequently be declared `protocol-invalid` and followed by a more
convenient result. Sealing alone cannot prevent cherry-picking when declared
invalidity is not independently checked.

### B. Unbound challenge packet

ADR-045 requires a challenge to receive a canonical challenge packet containing
the exact closure candidate. Existing evidence checked the challenged-subject
SHA, prompt, receipt, and output, but did not prove `receipt.input.packet` was
that canonical packet. Output over arbitrary input could be attributed to a
different candidate.

### C. Historical protocol availability

Content-addressed protocol bundles and stale-protocol re-adjudication require
historical bundles and every referenced artifact to remain available at their
published bytes. Protocol evolution must therefore be append-only.

## Discovery classification

```text
no-normative-impact
```

This is an assurance defect in the hostile-review evidence contract only.

## Decision

### Attempt outcome is checker-derived

Attempt outcome labels are not proof. For each completed campaign LLM call the
checker independently derives role-specific deterministic protocol validity and
requires the declaration to agree:

```text
technical-failure = no completed response, raw_output == null, protocol_errors == []
protocol-invalid = completed response, raw_output != null, deterministic validation fails, protocol_errors non-empty
qualified = completed response, raw_output != null, deterministic validation passes, protocol_errors == []
```

The checker requires only the empty/non-empty rule for `protocol_errors`, not
textual equality to its own diagnostics. Every admitted receipt has exactly one
qualified attempt. The first protocol-valid completed response is terminal: the
qualified attempt is final and no attempt follows it.

For `initial-reviewer`, validity is derived from the sealed output and bundle
raw-output schema only: JSON parsing; schema validation; exactly the complete
14 Gate A objectives once; unique raw finding IDs; valid assessment references;
and both directions of finding/objective reciprocity. Execution metadata is
checked after qualification, not used to determine validity.

For `challenge`, validity is derived from its sealed output, bundle challenge
schema, and exact bound canonical challenge packet: matching kind, exact required
objective coverage, unique objections, valid assessment references, matching
objection objectives, and exactly-one assessment membership. Semantic correctness
of objections is not decided by this deterministic validation.

### Canonical self-contained challenge packets

Canonical challenge packets reside at `formal/reviews/challenge-packets/*.json`.
They contain exactly `challenge_packet_schema_version`, `challenge_kind`,
`challenge_subject`, `required_objectives`, and `review_packet`, with no extra
properties. They use repository canonical JSON document bytes. A subject SHA is
the canonical JSON payload SHA without its trailing document newline.

The embedded `review_packet.payload` equals the exact parsed canonical Gate A
packet and its SHA equals `record.protocol.review_packet.sha256`; it is validated
by the same ADR-043 packet self-validation rules. Thus the challenge receives
the reviewed authority universe rather than an opaque reference.

Materiality packets use kind `materiality`, selector
`hostile-materiality-challenge-v1`, the checker-derived exact materiality payload
and SHA, and exactly the seven materiality axes. Refutation packets use kind
`refutation`, selector `hostile-refutation-challenge-v1`, the checker-derived
exact refutation payload and SHA, and exactly the seven specified refutation
objectives.

Every materiality or refutation challenge receipt has role `challenge`, uses the
bundle challenge prompt, and has `input.packet == challenge.packet`. The packet
must exist under the challenge-packet directory with `.json` suffix, direct
non-symlink path, exact hash, canonical bytes, and bundle-selected schema. Its
qualified output equals `challenge.output`.

### Append-only protocol evolution

Published versioned protocol bundles and every versioned prompt/schema they
reference are immutable by path and bytes. A protocol change creates new paths,
a new bundle, and a new protocol identity. Bundle schema version 2 introduces a
`predecessor`; the current v2 bundle points exactly to the published v1 bundle
at `formal/reviews/protocols/gate-a-campaign-protocol-v1.json` with SHA
`156d6247907f17b49802b7953ef866bdd6e07c2b3f40b01c45f6077bd8498cc1`.

The checker recursively validates each referenced chain bundle, canonical bytes,
schema, prompts, schemas, hash, and direct safe path. Cycles, repeated bundle
paths, and duplicate `protocol_id` values in one chain are invalid. Only chains
referenced by the current protocol or evidence are required.

### Current protocol v2 and semantic boundary

The current protocol moves from v1 to v2 without modifying v1. `P` changes while
Gate A semantic identity `S` remains unchanged because hostile-review policy is
excluded from `S`.

## Consequences

There is no TURNLOCK product semantic change, no `TL-INV` change, no `TL-CLAIM`
change, no normative coverage change, and no executable formal model. The Gate A
semantic subject is unchanged. ADR-046 is not added to
`formal/verification.yaml` `authority.architecture_decisions` or
`authority.abstraction_constraints`.

## References

* ADR-042
* ADR-043
* ADR-045
* `formal/reviews/review-evidence.schema.json`
* `formal/reviews/review-protocol-bundle.schema.json`
