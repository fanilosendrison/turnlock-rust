---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Clarify that TL-INV-037 forbids governing-definition changes under current semantics"
id: "ADR-028"
status: "accepted"
date: "2026-09-16"
decision_body_sha256: "3f570f65caaa443f58e0129740d8858b6e84903530eb7ac3600e952620dceac1"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-027"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Current-semantics interpretation of TL-INV-037 governing-definition stability"
  - "Formal-model treatment of active governing-definition replacement"
---

# ADR-028: Clarify that TL-INV-037 forbids governing-definition changes under current semantics

## Context

ADR-027 accepted stable governing definition per invocation and admitted
`TL-INV-037`. Section 3.35 of the normative specification now requires:

```text
For every accepted workflow invocation,
its governing workflow definition remains
the source of declared topology
for the lifetime of that invocation.
```

ADR-027 also records that deliberate active-definition mutation remains a
possible subject of a future product decision. Two passages expressed that
future-governance boundary in language that can be read as constraining the
current formal model:

- ADR-027's formal-applicability section states that the abstraction "must not
  forbid an explicit, separately authorized future active-definition mutation
  operation".
- The `TL-INV-037` `formalization_note` in `formal/verification.yaml` repeated
  the same constraint.

Read literally, that wording would require the current model to reserve an
exception for a semantic capability that has not been accepted. There is
currently no accepted active-definition-mutation semantic in TURNLOCK. The
accepted contract is unconditional for the invocation's active lifetime:
while invocation `I` remains active, `governingDefinition[I]` is stable, and no
currently accepted transition changes it.

ADR-015 requires the formal model to remain faithful to the normative prose
rather than anticipating product decisions. A post-resolution repository review
therefore identified an ambiguity — not in the accepted product decision or in
the normative invariant, but in how the future-governance boundary must be
represented in the current model.

ADR-027 is accepted and its decision body is immutable under ADR-017. This ADR
records the clarifying interpretation without editing ADR-027's substantive
decision.

## Discovery classification

### Derived clarification: current semantics forbid active governing-definition replacement

- **Statement:** Under the currently accepted TURNLOCK semantics, `TL-INV-037`
  requires the governing workflow definition of an accepted invocation to
  remain unchanged for that invocation's entire active lifetime. The current
  formal model must therefore forbid every transition that changes an active
  invocation's governing workflow definition. ADR-027's statement that
  deliberate active-definition mutation remains a possible subject of a future
  product decision is only a future-governance boundary; it is not a present
  semantic exception to `TL-INV-037`, and the current model must not represent
  or permit such an exception.
- **Source and evidence:** Repository review after Issue #4's resolution
  identified that ADR-027's formal-applicability wording and the `TL-INV-037`
  `formalization_note` could be read as requiring a reserved, authorization-gated
  transition in the current model. The normative invariant and ADR-027's
  substantive decision already require stability for the invocation's active
  lifetime and introduce no mutation primitive.
- **Existing authority:** `TL-INV-037` states the lifetime-stability
  requirement. ADR-027 accepted that requirement, introduced no
  active-definition-mutation primitive, and states that any such capability
  requires its own separate accepted product decision. ADR-015 requires the
  formal model and traceability manifest to represent the accepted normative
  semantics rather than a hypothetical future one.
- **Semantic disposition:** `derived-from-existing-authority`.
- **Affected layers:** `formal-model-or-analysis`,
  `normative-contract` (clarification only, with no substantive change), and
  `repository-governance-or-documentation` for the formal traceability wording.
- **Related discoveries or consequences:** A future active-definition-mutation
  semantic remains a possible future product decision and must reconcile with
  `TL-INV-037` and ADR-027 at that time. Issue #18 separately retains whether an
  execution resource is authorized to edit the source artifact of a workflow
  that currently governs it.
- **Required authority:** None beyond the already accepted `TL-INV-037` and
  ADR-027. This is an A-class derived clarification, not a new product-semantic
  choice.
- **Next action:** Correct the `TL-INV-037` formalization note, keep the
  normative invariant unchanged, and record this clarification as ADR-028.

### Derived clarification: leaving a future decision open reserves no present transition

- **Statement:** Leaving open whether a future product decision will introduce
  active-definition mutation does not reserve, enable, or require any present
  model transition. The current model contains no active-definition-mutation
  transition, no authorization guard for one, and no placeholder for one.
- **Derived from:** There is no accepted active-definition-mutation semantic.
  ADR-027 explicitly introduces no such primitive, and `TL-INV-037` is
  unconditional for the invocation's active lifetime.
- **Why no new choice is introduced:** Reserving a transition for a
  not-yet-accepted capability would let the formal model weaken present
  authority before any product decision authorizes it.
- **Failure if omitted:** A model could claim to implement `TL-INV-037` while
  representing an exception path that current authority does not permit.
- **Semantic disposition:** `derived-from-existing-authority`.
- **Affected layers:** `formal-model-or-analysis` and
  `repository-governance-or-documentation`.

### Separately governed questions

Whether active-definition mutation should ever exist, who could authorize it,
whether a user may grant such authority, whether a main-agent or
independent-agent region may edit a governing workflow's source artifact, what
ex-ante authority means, and whether runtime grants are permitted remain outside
this clarification. Issue #18 retains the authority questions. This ADR records
only that no current accepted semantic allows an active invocation's governing
definition to change.

## Decision

Under the currently accepted TURNLOCK semantics, `TL-INV-037` requires the
governing workflow definition of an accepted invocation to remain unchanged for
that invocation's entire active lifetime. The current formal model must
therefore forbid every transition that changes an active invocation's governing
workflow definition.

Conceptually, the current authority is:

```text
Accepted(I)
∧ Active(I)
∧ governingDefinition(I) = D

→ governingDefinition(I) remains D
  for the active lifetime of I
```

The current model must therefore reject, without any authorization guard:

```text
Accepted(I)
∧ Active(I)
∧ governingDefinition(I) = D1

→

Active(I)
∧ governingDefinition(I) = D2
```

The model MUST NOT introduce a shape such as:

```text
if AuthorizedMutation(...)
then D1 → D2 is allowed
```

No such semantic exists today.

ADR-027's statement that deliberate active-definition mutation remains a
possible subject of a future product decision is only a future-governance
boundary. It is not a present semantic exception to `TL-INV-037`, and the
current formal model must not represent or permit such an exception.

No currently accepted active-definition-mutation transition exists. A future
accepted decision may change the normative contract, but if it introduces such
a capability it must explicitly reconcile the new semantic with `TL-INV-037`
and ADR-027, and must explicitly amend, supersede, qualify, or otherwise change
the current contract as appropriate at that time. The current model must not
anticipate the result of that future adjudication.

The following distinctions are normative:

```text
future product possibility
!=
current semantic permission

leaving a future decision open
!=
reserving a present transition in the state machine
```

This clarification changes no substantive product decision. ADR-027's accepted
semantics remain unchanged; this ADR removes ambiguity about how those semantics
must be represented in the current formal model.

`TL-INV-037` remains the sole invariant owner. This clarification creates no new
`TL-INV-*` identity, no mutation primitive, no authorization model, no replay or
reproducibility semantics, and no implementation mechanism.

## Rationale

The accepted normative invariant is unconditional for the invocation's active
lifetime. A formal model that reserves an exception for a hypothetical future
mutation capability would not faithfully represent that invariant: it would
permit transitions that current authority does not permit, and it would let a
modeling convenience anticipate a product decision before acceptance.

Separating a future-governance boundary from a present semantic permission keeps
the formal model falsifiable. The current model can be checked against a clear
safety obligation — an active invocation's governing definition never changes —
without encoding an authorization condition whose semantics, authority source,
and reconciliation with `TL-INV-037` have not been decided.

This clarification also preserves the correct authority direction. If a future
decision introduces active-definition mutation, the future decision owns the
reconciliation; the present model must not pre-empt it by defining a reserved
path.

## Alternatives considered

### Preserve the current wording as a forward-compatibility allowance

Rejected. The wording constrains the current formal model to accept a transition
that no accepted semantic permits. Forward compatibility for a future product
option does not justify weakening a present universal safety obligation in the
model.

### Weaken or qualify `TL-INV-037` with a present mutation exception

Rejected. That would be a new product decision, and no accepted authority
establishes an active-definition-mutation semantic. This clarification must not
change the substantive invariant.

### Represent a reserved authorization-gated transition in the model

Rejected. It would invent a transition and an authorization condition in advance
of any accepted decision, and it would make `TL-INV-037` model-checkably false
for the reserved path.

### Model only the ordinary-edit case and leave mutation unmentioned

Rejected as insufficient. The current model must forbid every represented
transition that changes an active invocation's governing definition, not merely
transitions caused by ordinary source-artifact edits.

### Treat ADR-027's future-governance sentence as already normative

Rejected. ADR-027 expressly introduces no mutation primitive and requires a
separate future accepted decision. Its sentence describes what a future decision
may consider, not what the current semantics permit.

## Consequences

### Benefits

- The current model has one unambiguous safety obligation: an active
  invocation's governing definition never changes.
- The formal model cannot silently weaken present authority by reserving a
  hypothetical exception.
- `TL-INV-037` remains the sole owner of the stability obligation and keeps its
  published identity and substantive wording.
- A future active-definition-mutation decision remains possible and is required
  to reconcile explicitly with `TL-INV-037` and ADR-027.

### Costs and obligations

- The `TL-INV-037` `formalization_note` must state that every represented
  transition changing an active invocation's governing definition violates the
  modeled safety property and that no mutation transition may be invented or
  reserved.
- Future formal work must not add an authorization-gated mutation transition
  without a new accepted decision.
- If a future accepted decision introduces active-definition mutation, it must
  reconcile that semantic with `TL-INV-037` and ADR-027 explicitly.

## Invariant admission

No new invariant is admitted. This decision clarifies how the existing
`TL-INV-037` obligation must be represented in the current formal model.

The repository invariant-admission test yields:

1. **Independent universal obligation:** The decision adds no obligation
   independent of the accepted lifetime-stability requirement already owned by
   `TL-INV-037`.
2. **Existing-owner test:** The stability requirement already has a stable
   owner; this ADR removes ambiguity about its current-semantics interpretation.
3. **Violation test:** A model that permits an active invocation's governing
   definition to change violates `TL-INV-037` itself once the invariant is
   interpreted under current authority.
4. **Traceability-value test:** A second invariant identity would duplicate the
   same obligation and split traceability without adding an independently
   satisfiable requirement.

## Formal applicability

`TL-INV-037` remains `planned` for core TLA+ formalization and
`not-yet-modeled` for verification.

The future abstract model must represent that once an invocation is accepted
with governing definition `D`, that governing definition remains unchanged
while the invocation is active, and that every represented transition changing
it from `D` to another definition `D'` violates the modeled `TL-INV-037` safety
property. The model must not provide an authorization-gated or otherwise
reserved exception path. The nested-invocation requirement remains: a nested
invocation `J` has its own governing definition determined for `J`, and caller
acceptance does not imply a transitive root/run-wide snapshot.

The abstraction must not select or imply a revision mechanism, hash, snapshot
representation, copy mechanism, storage choice, lock mechanism, authorization
implementation, replay implication, or reproducibility implication. TLA+
cannot establish real filesystem edit semantics, what counts as invocation
acceptance in a concrete harness, or whether an execution resource is
authorized to edit a source artifact; those remain conformance and
product-authority concerns.

No executable TLA+ model currently exists. `formal/verification.yaml` therefore
records no property, state variable, action, or configuration identifier for
this invariant, and no `modeled` or `checked` claim is made.

## References

- `docs/specification/turnlock-spec.md` — Section 3.35, `TL-INV-037`
- `docs/adr/adr-015-evolve-the-normative-and-formal-specifications-together.md`
- `docs/adr/adr-017-adopt-validated-okf-architecture-decision-record-metadata.md`
- `docs/adr/adr-027-bind-each-accepted-invocation-to-a-stable-governing-workflow-definition.md`
- `formal/verification.yaml`
- `docs/formal/invariant-mapping.md`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
- GitHub Issue #4 and the follow-up authority Issue #18
