---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Preserve condition-specific provenance without requiring protected-value disclosure"
id: "ADR-025"
status: "accepted"
date: "2026-09-15"
decision_body_sha256: "7590d6020febc29e739628c2e3f34fc1391855f2d04511dacac3c2f906946f0d"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-024"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Minimum protected-representation semantics for TURNLOCK-known effective execution conditions"
  - "Separation of effective-condition provenance capture from consumer-visible disclosure"
---

# ADR-025: Preserve condition-specific provenance without requiring protected-value disclosure

## Context

ADR-024 and `TL-INV-036` require each effective execution condition that
TURNLOCK selects, binds, explicitly supplies, or resolves to remain semantically
distinguished, attributable to the execution scope it governs, and exposable or
capturable at TURNLOCK's semantic boundary. ADR-024 deliberately did not choose
a representation, disclosure level, identifier, persistence model, retention
policy, comparison contract, or security mechanism.

Issue #16 exposed a product-semantic question left open by that decision:

```text
what must remain capturable when TURNLOCK knows an effective condition
but its underlying value is protected or unsafe to disclose?
```

The answer cannot be delegated entirely to serialization or security tooling.
If every known protected condition is irreversibly replaced by the same generic
marker, TURNLOCK loses distinctions it possessed when those conditions governed
execution. If conformance instead universally requires the raw value, provenance
becomes incompatible with legitimate protection of credentials, secrets,
private workflow-supplied context, authorization material, sensitive
environment values, and protected provider configuration.

Before this ADR, multiple behaviors remained compatible with ADR-024: universal
exact-value exposure, a semantically sufficient protected representation, an
existence-only protected marker, layered disclosure profiles, or another
bounded contract. The product owner has now explicitly accepted a
condition-specific protected-representation floor, with optional stronger
layers or profiles.

## Discovery classification

### Accepted product decision

- **Statement:** When TURNLOCK knows a specific effective execution condition,
  protection or redaction may hide its underlying value but must not
  irreversibly collapse distinctions TURNLOCK possessed about that condition.
  A condition-specific semantic representation must remain attributable to the
  governed execution scope and capturable at TURNLOCK's semantic boundary.
- **Source and evidence:** Issue #16 identified that ADR-024's accepted
  exposure-or-capture boundary did not determine the minimum protected
  representation. The product-owner resolution directive explicitly accepts
  Alternative B as the universal floor and permits stronger layers or profiles
  under Alternative D.
- **Existing authority:** ADR-024 establishes semantic distinction,
  scope-attribution, and a capturable boundary, but intentionally leaves
  disclosure and representation details open. ADR-019 keeps relevance,
  comparison, superiority, and optimization judgments outside TURNLOCK core.
- **Semantic disposition:** `decision-required`, resolved by this accepted ADR.
- **Affected layers:** `normative-contract`, `decision-history`,
  `formal-model-or-analysis`, `architecture-or-implementation`, and
  `integration-or-conformance`.
- **Related discoveries or consequences:** Issue #13 retains detailed execution
  inspectability, availability, retention, access, and privacy questions under
  `TL-INV-033`. Issue #4 retains workflow-definition binding. Cross-run
  identity, equality or difference evidence, comparison, reproducibility,
  persistence, retention, authorization, and representation mechanisms remain
  separate questions.
- **Required authority:** Product-owner acceptance through the repository ADR
  process, supplied explicitly for Issue #16.
- **Next action:** Clarify `TL-INV-036`, synchronize its normative and formal
  traceability projections, and retain only the formally meaningful abstract
  distinction in planned formal scope.

### Derived clarification: known protected is not unknown

- **Statement:** A TURNLOCK-known condition whose value is protected cannot be
  represented as unknown merely because a particular consumer may not receive
  the value.
- **Derived from:** The accepted decision requires preservation of distinctions
  TURNLOCK actually possessed while permitting value non-disclosure.
- **Why no new choice is introduced:** Treating known protected provenance as
  unknown would erase the very distinction the accepted floor preserves.
- **Failure if omitted:** Protection could falsely convert known governing
  provenance into absence of knowledge.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `formal-model-or-analysis`, and
  `integration-or-conformance`.

### Separately governed mechanisms and policies

A hash, cryptographic commitment, HMAC, fingerprint, token, opaque identifier,
UUID, secret-store reference, encryption scheme, attestation, redaction format,
event schema, database, access-control system, or user-interface design remains
`no-normative-impact` in `architecture-or-implementation` unless a later
accepted decision requires that observable mechanism.

The identity of authorized consumers, access rules, privacy policy, persistence,
retention, cross-run linkability, and adapter coverage beyond conditions
TURNLOCK selects, binds, explicitly supplies, or resolves are not determined by
this ADR. They require separate classification if a durable product obligation
is proposed.

## Decision

Exact-value disclosure is not required to satisfy effective
execution-condition provenance.

When TURNLOCK knows a specific effective execution condition that it selects,
binds, explicitly supplies, or resolves, protection or redaction applied at its
semantic boundary MUST NOT substitute away condition-specific information
TURNLOCK possessed about that condition when it governed execution. A semantic
representation containing information specific to that known condition MUST
remain:

1. semantically bound to the effective-condition occurrence and the execution
   scope it governed; and
2. capturable during TURNLOCK's required semantic-boundary capture opportunity
   without reconstruction from later mutable state, human recollection, or
   agent recollection.

An occurrence label alone is not condition-specific information. The protected
representation must preserve the more specific condition provenance TURNLOCK
possessed, although that information need not be disclosed by a consumer view.
This condition-specific information and occurrence-to-scope binding do not state
or prove whether underlying values in different occurrences are equal or
different.

Conceptually:

```text
TURNLOCK knows effective condition C
        ↓
C governs execution scope S
        ↓
condition-specific semantic representation R(C)
        ↓
R(C) remains attributable to S
        ↓
R(C) is capturable at TURNLOCK's semantic boundary
```

`R(C)` need not reveal the underlying value of `C`.

The semantic contract distinguishes at least these states without prescribing
API types or canonical labels:

```text
unknown
  TURNLOCK does not know the effective condition

known and disclosable
  TURNLOCK knows the effective condition and its value may be disclosed

known and protected
  TURNLOCK knows the effective condition but its value need not be disclosed
```

Known and protected is not unknown. Non-disclosure MAY hide the underlying
value. Before or during the required boundary capture opportunity,
non-disclosure MUST NOT erase condition-specific information TURNLOCK possessed
about the effective condition. This prohibition governs lossy protection or
redaction, not expiration after the capture opportunity.

A generic marker such as `[PROTECTED]`, `[SECRET]`, or `[REDACTED]` MAY be a
valid consumer-visible view. It is insufficient as the sole provenance
representation when TURNLOCK knew condition-specific information and replacing
that information with the marker before or during the boundary opportunity
would destroy that provenance. Discard after the opportunity remains governed
by separate availability, persistence, and retention decisions.

Consumer-visible disclosure and underlying provenance capture capability are
not equivalent:

```text
consumer-visible disclosure
!=
underlying provenance capture capability
```

A consumer may receive a more restrictive or redacted view than another
consumer or capture context. This permission does not define who is authorized,
require an additional consumer context, require that every consumer receive the
capturable representation, or select an access-control or privacy policy. It
requires an execution-boundary opportunity, subject to separately governed
policy, to capture the TURNLOCK-known condition occurrence and its governed-scope
attribution without lossy substitution. Whether the representation remains
available after that opportunity, is persisted, or is retained is separately
governed.

This condition-specific requirement binds the captured provenance to the
specific effective-condition occurrence and governed scope at the required
boundary opportunity. Across separate occurrences, runs, or capture contexts,
it does not establish a public, globally stable, or cross-run identity. It does
not require:

```text
same underlying value → same representation or public identifier
different underlying value → different representation or public identifier
```

Nor does it establish an operation or proof for underlying-value equality or
difference, a comparison proof, or a judgment that two executions are
comparable for property `P`. A future
comparison layer may determine that an available representation supports
equality, supports distinction only, supports neither, or is insufficient for a
particular property. ADR-019 and `TL-INV-034` remain fully applicable: TURNLOCK
core does not choose determinant relevance, causal significance, comparability,
superiority, or optimization policy.

Stronger profiles, integrations, or separately governed contexts MAY later
provide exact-value access, cross-run correlation, equality evidence, an
auditable secret reference, reproducibility guarantees, or comparison
capabilities. Such layers do not replace the universal requirement against lossy substitution
of TURNLOCK-known condition-specific provenance before or during the boundary
capture opportunity.

This ADR clarifies ADR-024. ADR-024 accepted the provenance floor; this ADR
defines how that floor remains meaningful when disclosure of the underlying
value is constrained. It neither amends ADR-024 nor claims that ADR-024 had
already selected this answer.

Issue #13 continues to own execution inspectability, minimum actual-behavior
fact sufficiency, completed and non-completed inspection, and related
availability, retention, access, or privacy questions under `TL-INV-033`. This
ADR owns protected-representation semantics for effective-condition provenance
under `TL-INV-036`; overlap in access or privacy concerns does not merge the
scopes.

Issue #4 continues to own workflow-definition binding. If TURNLOCK binds or
resolves a workflow definition that is protected, this decision applies to that
effective condition without choosing stable binding, live observation, dynamic
mutation, or any definition representation.

This decision establishes no persistence, retention, replay, canonical run
model, event model, telemetry, secret-management system, authorization model,
cryptographic representation, equality algorithm, comparison contract,
reproducibility profile, or disclosure through ordinary UI, logs, CLI output,
or inspection surfaces.

## Rationale

The accepted floor preserves provenance correctness and privacy as compatible
responsibilities. Provenance concerns which known condition governed which
scope. Disclosure concerns which parts of that provenance a particular view may
reveal. Conflating them would either disclose protected values universally or
allow protection to erase known execution provenance.

Condition-specific preservation is weaker than stable identity or comparison
evidence. It prevents irreversible collapse of distinctions TURNLOCK already
possessed without promising that external consumers can correlate two
representations, infer equality or difference, or evaluate relevance to a
property. This preserves room for future security, comparison, and
reproducibility decisions.

The boundary remains mechanism-independent. Different realizations may have
materially different linkability, collision, confidentiality, authorization,
and retention properties. Selecting one now would decide concerns beyond the
accepted semantic floor.

## Alternatives considered

### Exact effective-value exposure as the universal floor

Rejected. Real provenance does not universally require disclosure of a raw
value. Requiring raw credentials, secrets, private context, authorization
material, sensitive environment values, or protected provider configuration
would create an unnecessary conflict between provenance correctness and
security or privacy.

### Semantically sufficient protected representation

Accepted as the universal floor. A representation retaining condition-specific information preserves
TURNLOCK-known provenance and governed-scope attribution without requiring raw
value disclosure, stable identity, equality evidence, or a mechanism.

### Existence-only known-but-protected marker

Rejected as a sufficient universal floor when used as the sole provenance
representation. Such a marker may be a valid view for a particular consumer,
but replacing more specific TURNLOCK-known information with one generic protected
state before or during the boundary opportunity destroys the accepted
provenance.

### Layered or profiled disclosure

Accepted as an optional extension above the universal floor. Stronger layers
may expose more information or evidence under separately accepted contracts;
they cannot compensate for provenance irreversibly lost by the base runtime.

### A prescribed security or representation mechanism

Rejected. No single hash, commitment, identifier, encryption, secret-store,
redaction, access-control, storage, event, telemetry, or UI mechanism follows
from the accepted product semantics.

## Consequences

### Benefits

- Protected values can remain undisclosed without converting known provenance
  into unknown provenance.
- Consumers may receive appropriately restricted views while the required
  boundary opportunity preserves capture of the condition occurrence and its
  governed-scope attribution under separately governed policy.
- Future comparison or reproducibility layers can assess available provenance
  without this decision predefining identity, equality, relevance, or
  comparability.
- Runtime and adapter designs retain freedom to select protection and capture
  mechanisms that satisfy later security and conformance requirements.

### Costs and obligations

- Runtime and adapter designs cannot treat one generic protected marker as the
  only retained provenance for all effective conditions TURNLOCK knew
  specifically.
- Conformance review must distinguish unknown, known and disclosable, and known
  and protected states at the semantic level.
- Protection mechanisms must be evaluated for whether they substitute away the
  TURNLOCK-known condition occurrence or its governed-scope attribution before
  or during the required boundary capture opportunity, independently of what a
  particular consumer view discloses.
- Concrete authorization, privacy, retention, and representation choices remain
  unresolved and may require later decisions before implementation.

## Invariant admission

No new invariant is admitted. This decision clarifies the conditions for
satisfying `TL-INV-036`.

The repository invariant-admission test yields:

1. **Independent universal obligation:** The decision adds no obligation
   independent of effective execution-condition semantic distinction,
   scope-attribution, and boundary capturability already owned by `TL-INV-036`.
2. **Existing-owner test:** It defines what preservation and capturability mean
   when a known condition's value is protected; the existing invariant is the
   correct owner.
3. **Violation test:** Once `TL-INV-036` is correctly interpreted, a realization
   that irreversibly collapses all known protected conditions into one generic
   provenance marker does not preserve semantic distinction and therefore
   violates `TL-INV-036` itself.
4. **Traceability-value test:** A second identity would duplicate the same
   condition-to-scope provenance contract and split traceability without adding
   an independently satisfiable obligation.

`TL-INV-036` keeps its stable identity. Its normative wording and ADR mapping
are updated to include this clarification.

## Formal applicability

`TL-INV-036` remains `partial` for core TLA+ formalization and
`not-yet-modeled` for verification.

A future abstract model may distinguish unknown condition provenance, known
condition-occurrence provenance, and an impermissibly collapsed generic
protected state. It may model preservation of an abstract occurrence-to-scope
relationship through a boundary capture opportunity without assigning a
concrete representation, post-boundary lifetime, underlying-value equality, or
cross-run identity.

TLA+ cannot establish whether a real protected representation leaks secrets,
whether an adapter exposes it safely, whether a consumer is authorized, or
whether concrete privacy, serialization, persistence, and retention behavior is
correct. Those concerns require later conformance, security, and implementation
work under their own accepted contracts.

No executable TLA+ model currently exists. No property, state variable, action,
configuration, or evidence identifier is introduced, and no `modeled` or
`checked` claim is made.

## References

- `docs/specification/turnlock-spec.md`
- `docs/adr/adr-019-keep-evaluation-and-optimization-policy-outside-turnlock-core.md`
- `docs/adr/adr-024-preserve-effective-execution-condition-provenance.md`
- `docs/vision/future-workflow-run-evaluation.md`
- `formal/verification.yaml`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
- GitHub Issues #4, #13, #15, and #16
