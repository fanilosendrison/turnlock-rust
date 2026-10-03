---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Define provider-reported effective model identity resolution"
id: "ADR-054"
status: "accepted"
date: "2026-10-03"
decision_body_sha256: "10ffb5051b63cc3c39fa6f622631c5368dac670da38cbe0dd12ae8e15352c4e4"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-053"
  amends:
    - "ADR-045"
  supersedes: []
  confirms:
    - "ADR-042"
    - "ADR-046"
    - "ADR-047"
    - "ADR-048"
    - "ADR-049"
governs:
  - "Gate A provider-reported model identity resolution"
  - "Canonical effective model identity channel"
  - "Provider-reported unresolved-alias handling"
  - "Reviewer identity realization conformance"
---

# ADR-054: Define provider-reported effective model identity resolution

## Context

ADR-045 requires model identity to be the tuple:

```text
(provider, model, model_version)
```

For `provider-reported`, ADR-045 requires:

```text
model_version = qualified attempt provider_model
```

It also requires that `model_version` not be an unresolved alias. Existing
hostile-review authority does not define what establishes that a
`provider_model` is the resolved effective identity rather than an unresolved
alias.

Pi qualification exposed this gap, but Pi is not semantic authority, OpenAI is
not TURNLOCK authority, checker behavior is not semantic authority, and Issue
evidence is not protocol authority. The existing Pi evidence establishes
faithful capture of provider-owned `response.model`; it does not establish
canonical post-alias effective identity semantics.

## Discovery classification

```text
decision-required at hostile-review assurance/protocol architecture layer;
resolved by this ADR;
no TURNLOCK product-semantic impact
```

## Decision

### Provider-reported identity channel

A provider-reported `model_version` is admissible only when the selected
execution realization exposes an exact provider-owned, execution-bound identity
channel whose qualified contract identifies the canonical effective model
selected after request-alias resolution.

The named contract is:

```text
provider-owned-canonical-effective-model-identity-v1
```

The channel value is provider-owned, execution-bound, post-routing and
post-alias-resolution, canonical for effective-model identity equality, and
opaque to TURNLOCK. For an exact qualified attempt:

```text
provider_model =
exact value emitted by that qualified provider-owned channel

model_version =
provider_model
```

Admissibility does not depend on spelling, date or version appearance,
snapshot-looking syntax, repeated observations, request/model inequality, local
catalog metadata, provider-specific name guessing, Pi catalog inference, runner
assertion, or provider documentation alone. TURNLOCK never establishes alias
resolution through regular expressions, date tests, version-number tests,
repeated-observation tests, or request/response string comparison.

The exact value `latest` remains forbidden as `model_version`. This exact
prohibition is not a syntax-based alias heuristic.

### Canonical equality

The qualified identity-channel contract establishes, in the provider identity
namespace:

```text
same effective provider model identity
⇔
same canonical identity token
```

The exact `provider_model` token is therefore the effective identity component
used by `(provider, model_version)` reviewer counting. Two request aliases that
route to the same effective model cannot produce distinct canonical effective
identity tokens and inflate reviewer diversity. TURNLOCK does not attempt to
prove this property from strings observed during a run.

### Separation of authority levels

The responsibilities remain distinct:

```text
ADR-054
→ defines what provider-reported means

Dependency Contract / realization conformance
→ establishes whether an exact provider/runtime path satisfies the property

execution evidence
→ provides the exact provider_model token for one occurrence
```

None of these levels replaces another.

### Unavailable capability

If the selected realization cannot establish
`provider-owned-canonical-effective-model-identity-v1`, provider-reported
resolution is unavailable for that realization. This is not a global Pi
failure, does not establish that a provider cannot support the capability in
principle, and does not authorize fabrication of `model_version`.

A profile can use `pinned-request-model` only when its accepted preconditions
are satisfied. Otherwise the profile is not usable through that realization.
There is no fallback to `request_model`.

### Profile admission and realization support

A future protocol bundle containing a reviewer profile whose
`identity_resolution.kind` is `provider-reported` may be published for a
provider/runtime binding only when its selected realization has established
`provider-owned-canonical-effective-model-identity-v1`.

Publishing a profile does not create the capability, and a realization cannot
invent it during execution. M3 remains protocol-only and never consults a
Dependency Contract to modify static profile qualification:

```text
protocol profile qualification
!=
runner realization support
```

A mismatch between P and the selected realization fails closed before provider
invocation.

### Completed response with unavailable identity

For one completed semantic response when the selected profile uses
`provider-reported` and the required `provider_model` is null, empty, or exact
`latest`:

```text
preserve completed response
preserve exact raw evidence
do not fabricate model_version
do not create a qualifying execution receipt
do not authorize semantic retry
do not substitute another reviewer profile
do not derive a later acquisition round from this WorkItem
stop automatic campaign progression
OPERATOR-ACTION-REQUIRED
```

This case is not `protocol-invalid`, not `TechnicalExecutionFailure`, and not
`DECISION-REQUIRED`.

The future M5-A cause semantics are exactly:

```text
producer = assurance-ledger
kind = provider-reported-identity-unavailable
resolutionContracts = []
```

The future M5-A Module Brief owns the exact cause-descriptor schema. This ADR
does not create that schema.

### Provider documentation and qualification evidence

Provider documentation, provider catalogs, provider source, provider-owned
metadata, and controlled conformance experiments may support realization
qualification. They are not Gate A semantic authority, protocol authority,
per-execution model identity evidence, or universal mandatory prerequisites.
This ADR defines the property. A Dependency Contract and realization
conformance establish whether an exact realization satisfies it.

The current Pi Dependency Contract evidence from Issues #44 and #46 establishes
faithful provider-owned `response.model` capture and no substitution from
`requestModel` or Pi high-level message normalization. It does not establish
canonical post-alias effective identity semantics. Its exact current capability
status is therefore `NOT-ESTABLISHED`, not `NOT-SUPPORTED-IN-PRINCIPLE` and not
Pi disqualification.

### Checker boundary

The checker is never an alias classifier. For `provider-reported`, it verifies
only these mechanical relations:

```text
profile kind == provider-reported
qualified attempt exists
provider_model is non-empty
provider_model != "latest"
resolved_identity.resolution_kind == provider-reported
resolved_identity.evidence_attempt_id == qualifying attempt
resolved_identity.model_version == qualifying attempt.provider_model
provider/model bindings remain exact
```

The checker performs no provider API call, provider documentation lookup,
catalog lookup, regular-expression version test, date test,
repeated-observation test, or request/response inequality test.

### Historical compatibility

Published protocol bundles v1 through v5 and their published meta-schemas remain
immutable. All published v1-v5 `reviewer_profiles` are currently empty, so no
qualifying historical evidence is reinterpreted. ADR-054 introduces a new
protocol identity P rather than rewriting history. Review evidence remains
schema `5.0`, and execution receipts remain schema `3.0`.

### Product and formal boundary

Explicitly:

```text
no TURNLOCK product semantic change
no TL-INV change
no TL-CLAIM change
no normative coverage change
no executable formal-semantics change
Gate A semantic subject S unchanged
review-evidence schema unchanged
execution-receipt schema unchanged
```

ADR-054 is not added to `formal/verification.yaml`
`authority.architecture_decisions` or `authority.abstraction_constraints`.
It changes hostile-review protocol identity P, provider-reported model identity
semantics, and reviewer-profile realization-conformance obligations only.

## Consequences

- Provider-reported identity now has one explicit realization-qualified
  canonical effective-model contract.
- Opaque provider tokens remain admissible without syntax classification.
- Request aliases cannot inflate effective reviewer diversity.
- Missing required identity after a completed semantic response preserves the
  response while stopping automatic campaign progression without retry or
  profile substitution.
- The current Pi path remains qualified for faithful provider-owned evidence
  capture but not for provider-reported canonical effective identity.
- Protocol v6 publishes the decision without changing S or historical protocol
  artifacts.

## Alternatives rejected

- Treating every non-empty provider string as resolved: field presence does not
  establish canonical post-alias effective identity.
- Syntax, date, version, or snapshot heuristics: identifier spelling is opaque
  and cannot establish provider semantics.
- Stability across repeated observations: repetition does not establish
  immutability or canonicality.
- Request/model inequality: equal strings may already be canonical and unequal
  strings may still be aliases.
- Checker network or catalog lookup: the checker validates evidence relations;
  it does not qualify provider semantics.
- Falling back to `request_model`: this would fabricate an identity not emitted
  by the required provider-owned channel.
- Retrying or substituting after a completed response lacks identity evidence:
  this would permit semantic result shopping and violate selected-WorkItem
  acquisition semantics.

## Verification obligation

Mechanical coverage is required for:

```text
protocol v6 meta-schema selection and exact binding
protocol v6 exact predecessor lineage
provider_reported_resolution policy identity
v5 reviewer-acquisition inheritance
opaque provider_model acceptance
provider_model == request_model acceptance
provider_model == "latest" rejection
resolved_identity.model_version == "latest" rejection
pinned request_model == "latest" rejection
historical v1-v5 byte identity
Gate A semantic subject S preservation
```

## References

- ADR-042
- ADR-045
- ADR-046
- ADR-047
- ADR-048
- ADR-049
- ADR-053
- `formal/verification.yaml`
- `formal/reviews/README.md`
- `docs/formal/dependency-contract-pi-m4-cognitive-execution.md`
- `scripts/check-formal-traceability.py`
- `scripts/tests/test-formal-traceability.py`
