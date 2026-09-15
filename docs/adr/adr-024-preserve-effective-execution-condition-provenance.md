---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Preserve effective execution-condition provenance"
id: "ADR-024"
status: "accepted"
date: "2026-09-15"
decision_body_sha256: "702e7799370bb71be037a20213f2ff82686195a3bb01d1bb2ce5fbf50e227433"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms:
    - "ADR-019"
governs:
  - "Attribution and boundary exposability of effective execution conditions selected, bound, explicitly supplied, or resolved by TURNLOCK"
---

# ADR-024: Preserve effective execution-condition provenance

## Context

ADR-018 and `TL-INV-033` require enough actual TURNLOCK-visible behavior from a
completed workflow execution to remain inspectable for understanding,
evaluation, and iterative refinement. That accepted obligation principally
answers:

```text
what actually happened?
```

ADR-018 explicitly does not derive a `Run`, `RunSpec`, workflow revision
identity, replay, cross-run comparability, reproducibility level, experiment
framework, or automatic optimization capability. Issue #13 separately owns the
detailed minimum fact set, sufficiency, availability, retention, privacy, and
non-completed-execution semantics needed to apply execution inspectability.

ADR-019 and `TL-INV-034` keep evaluation and optimization policy outside
TURNLOCK core. An explicitly responsible user, coding agent, evaluator,
higher-level system, or ordinary authored workflow supplies objectives,
selects relevant evidence, judges comparisons, and may author a refined
workflow. TURNLOCK does not define what "better" means.

A separate upstream question remains. Credible future evaluation may need to
know not only what happened, but:

```text
under which TURNLOCK-known effective conditions did it happen?
```

The relevant conditions depend on the property being evaluated. A model
configuration may matter for output quality, while different facts may matter
for control-flow conformance. Comparison therefore has a property-relative
shape:

```text
Are executions E1 and E2 comparable for property P?
```

TURNLOCK cannot know every causal determinant, complete environment fact, or
future property `P`. It does, however, possess some effective conditions when it
selects, binds, explicitly supplies, or resolves them at its semantic boundary.
If that attribution remains only hidden transient adapter state or is discarded
without an execution-boundary means of exposure or capture, a later evaluator
may be unable to reconstruct which known conditions governed which execution
scope. Evaluation, replay, and optimization features can be added later;
provenance lost while the governing information was available may not be
recoverable later.

Before Issue #15, multiple answers remained compatible with the accepted
corpus. The discovery was therefore `decision-required`, not derived from
ADR-018 or ADR-019. The product owner has now explicitly accepted the
forward-compatible semantic-provenance alternative through Issue #15's
resolution directive.

## Discovery classification

### Accepted product decision

- **Statement:** Effective execution conditions that TURNLOCK selects, binds,
  explicitly supplies, or resolves at its semantic boundary remain attributable
  to the execution scopes they govern and exposable or capturable at that
  boundary.
- **Source and evidence:** Issue #15 identified that future property-relative
  evaluation may depend on TURNLOCK-known governing conditions whose provenance
  cannot necessarily be reconstructed after it is lost. The product-owner
  resolution directive explicitly accepts Alternative B.
- **Existing authority:** ADR-018 requires completed-execution truth but
  expressly leaves comparability, reproducibility, workflow-definition
  identity, and stronger execution records open. ADR-019 assigns evaluation and
  optimization policy outside core without deciding governing-condition
  provenance. ADR-020 governs only initial cognitive-context provenance for
  workflow-declared independent agents.
- **Semantic disposition:** `decision-required`, resolved by this accepted ADR.
- **Affected layers:** `normative-contract`, `decision-history`,
  `formal-model-or-analysis`, `architecture-or-implementation`, and
  `integration-or-conformance`.
- **Related discoveries or consequences:** Issue #4 retains workflow-definition
  binding; Issue #13 retains detailed execution-inspectability semantics.
  Persistence, retention, replay, comparison contracts, reproducibility
  profiles, and stronger evidence profiles remain separate decisions.
- **Required authority:** Product-owner acceptance through the repository ADR
  process, supplied explicitly for Issue #15.
- **Next action:** Admit the weakest universal invariant entailed by the decision,
  synchronize the normative specification, and record only abstract planned
  formal traceability.

### Derived clarification: unknown conditions remain unknown

- **Statement:** A condition outside TURNLOCK's observation or control may
  remain unavailable or unknown, and absence of knowledge cannot be represented
  as known equality or evidence of no difference.
- **Derived from:** The accepted obligation is expressly limited to conditions
  TURNLOCK selects, binds, explicitly supplies, or resolves. It does not claim
  complete causal or environmental knowledge.
- **Why no new choice is introduced:** Treating unavailable information as
  known would falsely claim attribution that the accepted boundary does not
  provide.
- **Failure if omitted:** A future evaluator could mistake missing provenance
  for evidence that two executions shared the same condition.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `formal-model-or-analysis`, and
  `integration-or-conformance`.

### Derived clarification: attribution is independent of successful completion

- **Statement:** Once an effective condition governs an execution scope in an
  accepted invocation, its attribution does not become semantically nonexistent
  solely because the invocation later fails, is cancelled, or is interrupted.
- **Derived from:** The decision governs the relationship at the time the
  condition governs execution and exists to prevent its irreversible loss.
- **Why no new choice is introduced:** Conditioning the relationship on later
  successful completion would erase an already-real governing relationship and
  defeat the accepted provenance floor.
- **Failure if omitted:** The same governing condition would alternately exist
  or disappear based only on a later terminal outcome.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `formal-model-or-analysis`, and
  `integration-or-conformance`.
- **Boundary:** This clarification defines no failure, cancellation,
  interruption, post-run inspection, availability, retention, or privacy
  semantics; Issue #13 retains those questions.

### Mechanisms and stronger guarantees

Storage, identifiers, event schemas, snapshots, provider telemetry, comparison
algorithms, replay, and stronger profiles remain `no-normative-impact` in
`architecture-or-implementation` unless a later accepted product decision
requires an observable capability or mechanism. Formal structures remain
analysis choices and cannot strengthen this decision.

## Decision

TURNLOCK MUST preserve **effective execution-condition provenance** at its
semantic boundary.

For every accepted workflow invocation:

1. an effective execution condition that TURNLOCK selects, binds, explicitly
   supplies, or resolves MUST remain semantically distinguished;
2. that condition MUST remain attributable to the execution scope it governs;
   and
3. TURNLOCK MUST provide an execution-boundary means by which the attribution
   can be exposed or captured rather than existing only as hidden transient
   adapter state or requiring reconstruction from later mutable state, human
   recollection, or agent recollection.

Conceptually:

```text
effective execution condition
        ↓
governs execution scope
        ↓
TURNLOCK preserves attribution
between condition and governed execution
        ↓
attribution is exposable or capturable
at TURNLOCK's semantic boundary
```

The universal floor applies to conditions TURNLOCK itself selects, binds,
explicitly supplies, or resolves. Candidate examples
include a governing workflow definition, explicit workflow inputs,
execution-resource selection, effective model or resource configuration,
workflow-supplied context, TURNLOCK-owned policy or configuration, nested
invocation relationships, and other TURNLOCK-resolved conditions. These are
illustrative categories, not a universal required catalog or separate
obligation for every example.

For any candidate fact, conformance and later design must distinguish:

```text
A. TURNLOCK selects or resolves it
B. TURNLOCK observes it but does not control it
C. an adapter or execution resource could expose it
D. TURNLOCK cannot reasonably observe it
```

This decision establishes the universal floor for category A, understood here
to include TURNLOCK selection, binding, explicit supply, and resolution. It does
not extend that floor automatically to B or C, and it permits D to remain
unavailable or unknown. Any extension requires its own derivation or accepted
decision. An unavailable or unknown condition MUST NOT be presented as
known-equal across executions or as evidence that no relevant difference
exists.

If a condition actually governs any execution scope within an accepted
invocation, its semantic attribution is not conditional on the invocation later
completing successfully. Later failure, cancellation, or interruption does not
make that already-governing relationship nonexistent. This rule does not define
terminal outcomes or broaden the detailed non-completed-execution
inspectability work owned by Issue #13.

Semantic distinction, runtime availability, exposability, capture, persistence,
and retention are non-equivalent responsibilities:

```text
semantic distinction
!= runtime availability
!= exposability
!= capture
!= persistence
!= retention
```

This decision requires semantic distinction, attribution, and an
execution-boundary means of exposure or capture. It does not require TURNLOCK to
operate a database, perform the capture itself in every deployment, persist the
attribution after execution, or retain it for any duration. Another layer may
capture or persist the boundary information. A conforming core cannot make
capture impossible by keeping the attribution only in inaccessible transient
adapter state.

Comparability remains property-relative and externally judged. TURNLOCK does
not decide which conditions matter to property `P`, whether available evidence
makes two executions comparable, which execution is superior, or which workflow
should replace another. The accepted pipeline remains:

```text
workflow
    ↓
TURNLOCK execution
    ↓
execution truth
+
effective execution-condition provenance
    ↓
external responsible evaluator
    ↓
property P + explicitly supplied objective
    ↓
possible comparison or evaluation
    ↓
possible workflow refinement
```

ADR-019 and `TL-INV-034` remain fully applicable. This ADR confirms that policy
boundary; it does not clarify or amend it.

ADR-018 and this decision are complementary but distinct. ADR-018 owns minimum
completed-execution truth. This decision adds governing-condition attribution
that ADR-018 explicitly did not entail. It therefore neither amends nor claims
to clarify ADR-018. Issue #13 retains its detailed scope.

Issue #4 continues to decide which workflow definition governs an active
invocation when its source artifact changes. This decision chooses none of
stable binding, live observation, or explicit dynamic mutation. Whichever
definition Issue #4's eventual semantics make effective, that definition-to-
execution-scope relationship must satisfy this provenance obligation when
TURNLOCK binds or resolves it. No hash, Git revision, snapshot, copy-on-write
representation, AST identity, or database revision is implied.

This decision establishes no exact or partial replay, reproducibility profile,
cross-run comparison API, canonical run model, experiment framework, execution
proof, universal execution record, or optimization facility. It does not imply
computational determinism, deterministic scheduling, deterministic agents or
external systems, identical outputs, or identical traces.

## Rationale

Forward-compatible semantic provenance is the weakest universal obligation that
protects future empirical evaluation without prematurely defining its policy or
infrastructure.

The boundary follows TURNLOCK's own semantic responsibility. When TURNLOCK
selects or resolves a condition, it already possesses that information and uses
it to govern an execution scope. Preserving the attribution does not require
complete knowledge of the world. It prevents the core from discarding its own
known governing relationship in a way no later layer can repair.

Explicit unknown values preserve epistemic honesty. A future evaluator can
conclude that comparability for a model-sensitive property cannot be established
when one execution's effective model configuration is unavailable. That is
preferable to silently treating missing evidence as equality.

The decision does not make provenance itself sufficient for comparison.
Relevance depends on property `P`, and objectives and comparison judgments
remain with the responsible external actor under ADR-019. The core provides
available TURNLOCK-known attribution; it does not supply universal determinant
sets or evaluation policy.

## Alternatives considered

### No present obligation

Rejected. Evaluation, comparison, replay, and optimization features can be
added later, but a conforming first runtime under this alternative could satisfy
ADR-018 while irreversibly discarding conditions TURNLOCK itself selected or
resolved. A later evaluator could then be unable to reconstruct the information
needed for a credible property-relative judgment. The lost provenance may be
impossible or disproportionately costly to recover after the fact.

### Forward-compatible semantic provenance

Accepted. It establishes semantic distinction, execution-scope attribution, and
boundary exposability or capturability for TURNLOCK-determined effective
conditions without choosing persistence, retention, identifiers, event schemas,
comparison policy, replay, or optimization machinery.

### Stronger universal execution record

Rejected for the current core contract. TURNLOCK does not know all future
properties `P`, all determinant sets relevant to them, all required
reproduction levels, or all persistence and retention needs. Claiming a
universal record sufficient for every future comparison would exceed current
product knowledge and could create false assurance.

### Profiles or layers instead of a universal floor

Rejected as a substitute for the accepted floor. Optional future profiles may
require stronger determinant capture, persistence, retention, reproducibility
levels, comparison guarantees, replay guarantees, or execution evidence. They
cannot repair attribution that the base runtime irreversibly discarded while it
possessed the effective condition.

Profiles and layers remain a valid future extension above the universal floor.

## Consequences

### Benefits

- Future evaluators can consume captured TURNLOCK-known governing-condition
  attribution without relying on later mutable state or recollection.
- Unknown external determinants remain explicit, allowing an evaluator to
  decline an unsupported comparison rather than infer equality.
- Future comparison, reproducibility, replay, experiment, and optimization
  facilities remain possible without becoming current core features.
- The obligation remains harness-independent and mechanism-independent.

### Costs and obligations

- Runtime and adapter designs must provide a semantic boundary through which a
  consumer can capture the attribution TURNLOCK itself establishes.
- Conformance must distinguish effective governing conditions from later or
  merely configured values and must preserve unknown rather than manufacture
  certainty.
- Architecture must keep the attribution associated with the execution scope it
  governed, including when the invocation later fails, is cancelled, or is
  interrupted.
- Issue #4's eventual workflow-definition binding decision must preserve
  attribution of whichever definition is effective without inheriting a
  representation choice from this ADR.
- Issue #13 remains responsible for detailed inspectability, terminal-outcome,
  availability, persistence or retention, access, and privacy semantics where
  applicable.
- Extensions beyond conditions TURNLOCK selects, binds, explicitly supplies,
  or resolves require separate derivation or decision.

## Derived invariant admission

This decision uniquely entails one distinct universal obligation,
`TL-INV-036`:

1. no existing invariant completely covers the obligation: `TL-INV-033`
   requires actual completed-execution behavior to remain inspectable but does
   not require attribution of effective governing conditions, and
   `TL-INV-034` constrains policy ownership without defining provenance;
2. every conforming realization owes attribution and boundary exposability or
   capturability for effective conditions TURNLOCK selects, binds, explicitly
   supplies, or resolves;
3. an implementation that leaves those relationships only in inaccessible
   transient state or requires reconstruction from later mutable state or
   recollection directly contradicts this decision;
4. the obligation is independent of storage, identifier, event, hashing,
   snapshot, API, telemetry, and UI mechanisms; and
5. the invariant remains distinct from completed-execution inspectability and
   evaluation/optimization-policy ownership.

The unknown-condition and non-successful-termination consequences explain the
scope of the same obligation and do not receive separate invariant identities.
Illustrative condition categories likewise receive no separate identities.

## Formal applicability

`TL-INV-036` is `partial` for core TLA+ formalization and
`not-yet-modeled` for verification.

A future abstract model can represent that an effective condition governs an
execution scope, preserve the attribution rather than substitute unrelated
later state, and distinguish known attribution from unavailable or unknown
information. TLA+ cannot establish that a real provider, harness, adapter, or
inspection boundary exposes semantically sufficient metadata, nor can it decide
privacy, serialization, storage, retention, or UI obligations.

No executable TLA+ model currently exists. The verification manifest therefore
records no planned property name, state variable, action, configuration, or
TLC evidence for this invariant. Those identifiers must be added only when the
shared executable model contains them. The mapping remains `pending-model`, and
no `modeled` or `checked` claim is made.

## References

- `docs/specification/turnlock-spec.md`
- `docs/adr/adr-018-require-completed-workflow-execution-inspectability.md`
- `docs/adr/adr-019-keep-evaluation-and-optimization-policy-outside-turnlock-core.md`
- `docs/adr/adr-020-define-independent-agent-context-provenance.md`
- `docs/vision/future-workflow-run-evaluation.md`
- `formal/verification.yaml`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
- GitHub Issues #4, #13, and #15
