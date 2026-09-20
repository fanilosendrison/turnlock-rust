---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Clarify hostile-review execution receipt attempt mapping"
id: "ADR-049"
status: "accepted"
date: "2026-09-20"
decision_body_sha256: "9229b650aa594466164d83dc34df920a328fb5378ddb6441f0edd32e5f786ffc"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-045"
    - "ADR-046"
    - "ADR-047"
  supersedes: []
  confirms:
    - "ADR-048"
governs:
  - "Hostile-review execution receipt identity"
  - "Protocol-attempt aggregation in execution receipts"
  - "Protocol retry to receipt-attempt mapping"
  - "LLM call and transport-attempt separation"
---

# ADR-049: Clarify hostile-review execution receipt attempt mapping

## Context

ADR-045 established content-addressed hostile-review execution receipts and
distinguished:

```text
technical/provider transport attempts internal to one LLM call
```

from:

```text
completed LLM calls used as protocol attempts
```

The accepted execution-receipt schema records one top-level `execution_id` and
an ordered `attempts[]` array. Every attempt records its own `attempt_id`,
`call_id`, outcome, timestamps, provider evidence, raw-output reference where
applicable, and `transport_attempt_count`.

ADR-045 also used the shorthand statement that every cognitive LLM call
participating in the campaign has its own execution receipt.

Taken literally, that sentence conflicts with the same accepted receipt
structure and retry rules: a fresh protocol retry is another LLM call, while the
receipt is explicitly capable of retaining several protocol attempts and one
final `qualifying_attempt_id`.

ADR-046 and ADR-047 rely on that multi-attempt structure to preserve
checker-derived `technical-failure`, `protocol-invalid`, and `qualified`
attempts and to make the first qualifying completion terminal.

The ambiguity must be removed before the Gate A campaign runner binds its
WorkItem and Execution identities to the accepted evidence contract.

No accepted product semantic rule, Gate A subject, retry admissibility rule,
protocol schema, prompt, or evidence schema needs to change.

## Discovery classification

```text
no-normative-impact
```

## Decision

### 4.1 One receipt identifies one logical cognitive protocol execution

One hostile-review execution receipt represents one logical cognitive protocol
execution bound to one exact:

```text
role
reviewer profile
protocol bundle
prompt
packet
isolated execution context
```

The top-level receipt `execution_id` identifies that logical cognitive protocol
execution.

It does not identify an individual retry call within that logical execution.

### 4.2 Receipt attempts are protocol attempts

Each element of receipt `attempts[]` represents one protocol attempt of that
same logical cognitive execution.

For every receipt attempt:

```text
attempt_id
```

identifies that exact protocol attempt, and:

```text
call_id
```

identifies the exact LLM call used for that protocol attempt.

A fresh protocol retry after an admissible `technical-failure` or
`protocol-invalid` outcome adds a new protocol attempt to the same logical
execution receipt.

It does not create a second receipt for the same logical cognitive execution.

Every completed response remains sealed exactly as already required by
ADR-045 through ADR-047.

### 4.3 Transport attempts remain below the protocol-attempt boundary

Provider or transport retries performed inside one LLM call are not separate
protocol attempts.

They remain represented by the accepted per-attempt transport evidence,
including:

```text
transport_attempt_count
```

The hierarchy is therefore exactly:

```text
logical cognitive protocol execution
    ↓
one execution receipt
    ↓
one or more ordered protocol attempts
    ↓
one LLM call per protocol attempt
    ↓
zero or more internal provider/transport retries for that call
```

### 4.4 Retry terminality is unchanged

The accepted retry semantics remain unchanged.

For deterministically validated roles:

```text
initial-reviewer
challenge
```

a checker-derived `protocol-invalid` completion may permit a fresh protocol
attempt with the exact same semantic input.

For roles without deterministic output validators:

```text
materiality-assessor
refutation-builder
discovery-classifier
derivation-builder
decision-necessity-challenger
repair-synthesizer
decision-projection
```

`protocol-invalid` remains forbidden and the first completed response remains
terminal.

For every role, the first `qualified` protocol attempt is final and no later
attempt may appear in that receipt.

A challenge remains a new logical cognitive protocol execution and therefore
has its own distinct execution receipt. It never becomes an additional attempt
inside the receipt of the reviewer execution it challenges.

### 4.5 Runtime-neutral evidence remains unchanged

This decision does not make `llm-runtime` part of the hostile-review evidence
contract.

The receipt remains runtime-transport-neutral.

A concrete runner may bind its own WorkItem, Execution, call, and transport
identities to these receipt fields in construction authority, but the evidence
contract itself does not require a particular runtime implementation.

### 4.6 Published artifact versions do not change

This clarification requires no byte change to:

```text
formal/reviews/schemas/execution-receipt-v3.schema.json
formal/reviews/protocols/gate-a-campaign-protocol-v4.json
formal/reviews/meta-schemas/*
formal/reviews/prompts/*
```

Execution receipts remain schema version `3.0`.

Review evidence remains schema version `5.0`.

The Gate A semantic subject remains unchanged.

The current protocol bundle bytes and protocol identity remain unchanged.

## Consequences

The receipt structure now has one unambiguous interpretation across accepted
retry, evidence, and future runner construction rules.

A concrete campaign runner can bind:

```text
logical cognitive work
protocol attempts
LLM calls
provider/transport retries
```

to distinct identities without collapsing those layers.

Protocol-invalid completed responses remain durable evidence and cannot be
discarded or relabeled as transport failures.

A retry cannot obtain a fresh logical execution identity merely to hide prior
protocol attempts.

Historical protocol artifacts and schemas remain immutable.

## Rejected alternatives

### One execution receipt per retry LLM call

Rejected.

It contradicts the accepted multi-attempt receipt structure and would prevent
one receipt from preserving the complete ordered attempt history culminating in
its `qualifying_attempt_id`.

### Treat protocol retries as provider transport retries

Rejected.

A completed `protocol-invalid` response has semantic protocol-attempt evidence
that must remain sealed and visible. It is not a transport retry.

### Publish execution-receipt schema v4 only to clarify identity

Rejected.

The existing schema already contains all required identity layers. The defect
is ambiguity in their interpretation, not missing representation.

### Change Gate A subject or protocol qualification semantics

Rejected.

This clarification changes neither.
