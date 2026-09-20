---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Make unvalidated cognitive completions terminal and validate readiness projections"
id: "ADR-047"
status: "accepted"
date: "2026-09-20"
decision_body_sha256: "42971d1a7de2b2aa343bb946a37605135fa680cc159875143d4dde05fa224a3e"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-046"
  supersedes: []
  confirms:
    - "ADR-041"
    - "ADR-045"
governs:
  - "Retry admissibility for cognitive roles without deterministic output validators"
  - "Protocol v3 role-aware completion policy"
  - "Published protocol-v2 artifact immutability"
  - "Formal readiness projection validation"
---

# ADR-047: Make unvalidated cognitive completions terminal and validate readiness projections

## Context

ADR-046 correctly made attempt validity checker-derived for `initial-reviewer`
and `challenge`, because those roles have deterministic structured-output
validators.

The evidence contract also defines seven cognitive execution roles for which no
deterministic output protocol currently exists:

```text
materiality-assessor
refutation-builder
discovery-classifier
derivation-builder
decision-necessity-challenger
repair-synthesizer
decision-projection
```

A completed response from one of those roles cannot truthfully be proven
`protocol-invalid` by the current checker.

Permitting a runner to declare such a completion invalid would allow
semantic-result retry/model shopping.

No new role-specific schemas are justified merely to permit retries.

`render-formal-mapping.py` currently derives readiness directly from
`derive_gate_a()`, which assumes already-valid evidence, so projection
generation must first run full traceability validation.

## Discovery classification

```text
no-normative-impact
```

## Decision

### 4.1 Two execution-validation classes

Protocol v3 recognizes exactly two categories.

#### Deterministically validated roles

```text
initial-reviewer
challenge
```

For these roles:

```text
technical-failure
→ no completed response

protocol-invalid
→ completed response exists AND checker deterministic validation fails

qualified
→ completed response exists AND checker deterministic validation passes
```

Existing ADR-046 retry semantics remain unchanged.

#### Roles without deterministic output validators

Exactly:

```text
materiality-assessor
refutation-builder
discovery-classifier
derivation-builder
decision-necessity-challenger
repair-synthesizer
decision-projection
```

For these roles:

```text
technical-failure
→ allowed before a completed response
→ raw_output == null

protocol-invalid
→ forbidden

first completed response
→ MUST be qualified
→ MUST be terminal
→ no later attempt permitted
```

No checker claim is made that this completion is semantically correct.

`qualified` for these roles means only that this is the unique admitted
completed response of that execution.

### 4.2 No output schemas invented

This decision introduces NO role-specific structured output schema for:

```text
materiality-assessor
refutation-builder
discovery-classifier
derivation-builder
decision-necessity-challenger
repair-synthesizer
decision-projection
```

Future deterministic validators require separately justified protocol
evolution.

### 4.3 Technical failure remains retryable

A technical failure remains:

```text
no completed semantic response
raw_output == null
protocol_errors == []
```

Any number of technical failures may precede the one terminal completed
response, subject to runner retry policy.

### 4.4 Published protocol artifacts are append-only

The already-published protocol v2 and its v2-specific referenced schemas are now
immutable regression anchors, exactly as v1 artifacts already are.

Current protocol evolution therefore creates v3 rather than editing v2.

### 4.5 Readiness projection

Generated formal documentation is a projection only.

`render-formal-mapping.py` MUST NOT call `derive_gate_a()` over unvalidated
review evidence.

Before rendering, it MUST call:

```python
checker.collect_errors(root, check_generated=False)
```

If that returns ANY errors, rendering fails.

Only the returned:

```text
summary["gate_a"]
```

from that full validation pass may determine the rendered Gate A readiness
state.

The renderer may separately recompute the current Gate A subject for display
only after validation succeeds.

### 4.6 Product semantics unchanged

Explicitly:

```text
no TURNLOCK product semantic change
no TL-INV change
no TL-CLAIM change
no normative coverage change
no executable formal model
no reviewer profile
no real campaign
review evidence schema remains 5.0
Gate A semantic subject remains unchanged
ADR-047 is not added to authority.architecture_decisions
ADR-047 is not added to authority.abstraction_constraints
```

## Consequences

- A completed response from a role without a deterministic output validator can
  no longer be retried after the runner declares it invalid.
- Technical failures remain retryable before the one terminal completed
  response.
- Published protocol v2 artifacts remain available as immutable historical
  regression anchors alongside v1.
- The generated formal readiness projection cannot display `READY` from
  evidence that the canonical traceability checker rejects.
- No product semantics change and no executable formal model is introduced.

## References

- `AGENTS.md`
- `docs/adr/adr-041-establish-turnlock-formal-assurance-architecture.md`
- `docs/adr/adr-045-bind-gate-a-campaigns-to-versioned-review-protocol-and-derived-evidence.md`
- `docs/adr/adr-046-bind-challenge-executions-to-exact-inputs-and-derive-retry-admissibility.md`
- `formal/README.md`
- `formal/reviews/README.md`
- `formal/reviews/review-protocol-bundle.schema.json`
- `formal/reviews/protocols/gate-a-campaign-protocol-v3.json`
- `formal/reviews/schemas/execution-receipt-v3.schema.json`
- `scripts/check-formal-traceability.py`
- `scripts/render-formal-mapping.py`
- `scripts/tests/test-formal-traceability.py`
