---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Define a realizable semantic-boundary capture handoff"
id: "ADR-026"
status: "accepted"
date: "2026-09-15"
decision_body_sha256: "260257ae9512ad5b08edd147f8c773da282c5648f39e9224679642e2e03efec0"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-024"
    - "ADR-025"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Minimum realizable semantic-boundary capture-handoff sufficiency for effective execution-condition provenance"
  - "Separation of the required provenance capture handoff from post-handoff availability, persistence, and retention"
---

# ADR-026: Define a realizable semantic-boundary capture handoff

## Context

ADR-024 and `TL-INV-036` require each effective execution condition that
TURNLOCK selects, binds, explicitly supplies, or resolves to remain semantically
distinguished, attributable to the execution scope it governs, and exposable or
capturable at TURNLOCK's semantic boundary. ADR-025 requires a TURNLOCK-known
protected condition to retain condition-specific provenance through the required
boundary capture opportunity while permitting restrictive consumer views.

ADR-025 therefore made that opportunity a material temporal boundary: before or
during it, TURNLOCK may not irreversibly substitute away required provenance;
after it, ADR-024 and ADR-025 themselves no longer require continued availability
and leave persistence and retention separately governed. Neither decision
defined what makes the opportunity sufficient rather than nominal.

Issue #17 exposed the remaining product-semantic question:

> What constitutes a sufficient semantic-boundary capture opportunity for
> `TL-INV-036`, and when may TURNLOCK cease to make effective
> execution-condition provenance capturable without violating that invariant?

Multiple observably different temporal and accessibility contracts remained
compatible with the accepted corpus: an instantaneous boundary availability, a
realizable capture path, scope-bounded availability, invocation- or
lifecycle-bounded availability, or profiled guarantees above a core floor. The
discovery was therefore `decision-required`, not derived from ADR-024 or
ADR-025. The product owner has now explicitly accepted the realizable
semantic-boundary capture handoff as the universal core floor, with
instantaneous availability permitted only as a conforming special case and
stronger profile- or layer-dependent guarantees remaining available above it.

## Discovery classification

### Accepted product decision

- **Statement:** For every effective condition TURNLOCK selects, binds,
  explicitly supplies, or resolves, TURNLOCK must preserve the required
  condition-specific provenance and governed-scope attribution until that
  provenance participates in a realizable semantic-boundary capture handoff.
  A handoff is realizable only when an eligible conforming capture context
  could be established in time to acquire the required provenance as part of
  the semantic-boundary interaction, without depending on inaccessible
  transient internal state, accidental timing against TURNLOCK's internal
  execution, or reconstruction from later mutable state, human recollection, or
  agent recollection.
- **Source and evidence:** Issue #17 identified that the phrase `required
  semantic-boundary capture opportunity` carried an undefined temporal and
  accessibility contract. The product-owner resolution directive explicitly
  accepts the realizable-handoff refinement of Alternative B as the universal
  floor, treats Alternative A as a conforming special case, and leaves
  Alternative E above the floor.
- **Existing authority:** ADR-024 establishes semantic distinction,
  scope-attribution, and an execution-boundary means of exposure or capture, and
  rejects provenance that exists only as inaccessible transient state.
  ADR-025 makes the boundary capture opportunity material for protected
  provenance. ADR-018 and ADR-019 own inspectability and evaluation-policy
  boundaries that this decision preserves without clarifying or amending.
- **Semantic disposition:** `decision-required`, resolved by this accepted ADR.
- **Affected layers:** `normative-contract`, `decision-history`,
  `formal-model-or-analysis`, `architecture-or-implementation`, and
  `integration-or-conformance`.
- **Related discoveries or consequences:** Issue #13 retains detailed completed
  and non-completed execution inspectability, availability, retention, access,
  and privacy. Issue #4 retains workflow-definition binding. Persistence,
  retention, authorization, delivery guarantees, concrete capture mechanisms,
  comparability, replay, and reproducibility remain separate decisions.
- **Required authority:** Product-owner acceptance through the repository ADR
  process, supplied explicitly for Issue #17.
- **Next action:** Clarify `TL-INV-036`, synchronize the normative
  specification and formal traceability projection, and record only the
  abstract temporal consequence in planned formal scope.

### Derived clarification: internal transient existence is not capturability

- **Statement:** A conforming capture opportunity cannot depend on an external
  consumer winning an accidental race against inaccessible internal timing.
  TURNLOCK does not satisfy `TL-INV-036` merely because the required provenance
  existed somewhere internally for some nonzero duration.
- **Derived from:** ADR-024 already rejects provenance that exists only as
  hidden transient adapter state and requires an execution-boundary means of
  exposure or capture. The accepted handoff floor defines what makes that means
  genuine.
- **Why no new choice is introduced:** Treating momentary internal existence as
  a capture opportunity would make the accepted boundary nominal, and no
  accepted decision permits an acquisition path that depends on an accidental
  race.
- **Failure if omitted:** A runtime could claim conformance while no conforming
  context could ever acquire the provenance.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `formal-model-or-analysis`, and
  `integration-or-conformance`.

### Derived clarification: actual consumer participation is not universally required

- **Statement:** A conforming runtime does not become non-conforming solely
  because no capture consumer was attached or configured for a particular
  invocation, provided the runtime exposes a real semantic capability through
  which an eligible conforming capture context could have been established in
  time to participate in the required handoff.
- **Derived from:** The accepted floor requires a realizable capture path, not
  actual capture. Requiring an attached consumer would import consumer-lifecycle
  and delivery semantics the decision expressly excludes.
- **Why no new choice is introduced:** Capture capability and actual capture are
  distinct; the floor is satisfiable without any consumer present.
- **Failure if omitted:** Every invocation without a consumer would either fail
  conformance or silently impose indefinite retention, neither of which follows
  from the accepted decision.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `integration-or-conformance`, and
  `architecture-or-implementation`.

### Derived clarification: delivery and acknowledgment are not implied

- **Statement:** The core contract does not require successful end-to-end
  delivery, consumer processing or persistence, acknowledgment, retry until
  success, exactly-once or at-least-once delivery, queue durability,
  backpressure, indefinite blocking for a receiver, or TURNLOCK-operated
  persistent buffering. A conforming capture participant may crash, disconnect,
  refuse, or mishandle the information without automatically creating an
  indefinite retention obligation for TURNLOCK core.
- **Derived from:** The accepted floor is an opportunity to acquire, not a
  reliable-messaging contract. ADR-024 and ADR-025 already leave persistence and
  post-opportunity availability separately governed.
- **Why no new choice is introduced:** The decision selects no transport,
  delivery guarantee, storage, or consumer-lifecycle semantics.
- **Failure if omitted:** A realizable handoff could be misread as a delivery
  guarantee, converting the capture floor into persistence, backpressure, and
  retry semantics.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract` and `integration-or-conformance`.

### Derived clarification: post-handoff survival is not implied by `TL-INV-036`

- **Statement:** Once the required provenance has participated in a conforming
  realizable semantic-boundary capture handoff, `TL-INV-036` alone does not
  require that provenance to remain capturable. Post-handoff availability,
  persistence, and retention remain independently governed and may be required
  by another accepted invariant, decision, profile, or integration contract.
- **Derived from:** ADR-024 and ADR-025 already separate capture from
  persistence and retention and define post-opportunity availability as
  separately governed.
- **Why no new choice is introduced:** The handoff discharges the universal
  capture obligation; reading it as scope-long, invocation-long, or
  workflow-long availability would add stronger semantics not entailed by the
  accepted floor.
- **Failure if omitted:** `capturable` would silently become a persistence or
  retention guarantee, overlapping Issue #13 and future retention decisions.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `formal-model-or-analysis`,
  `architecture-or-implementation`, and `integration-or-conformance`.

### Derived clarification: later failure does not erase an incurred obligation

- **Statement:** If an effective condition governed part of an accepted
  invocation, later failure, cancellation, or interruption must not
  retroactively erase the obligation that its provenance reach the required
  realizable handoff, just as ADR-024 prevents the governing relationship from
  becoming semantically nonexistent.
- **Derived from:** ADR-024 already makes the governing relationship
  independent of later successful completion, and the handoff is the
  satisfaction condition of that same provenance obligation.
- **Why no new choice is introduced:** A capture obligation that appears only
  after successful completion would condition an already-real relationship on a
  later terminal outcome, contradicting ADR-024.
- **Failure if omitted:** A condition that genuinely governed a failing scope
  could lose its required provenance before any boundary handoff, defeating both
  ADR-024 and this decision.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `formal-model-or-analysis`, and
  `integration-or-conformance`.
- **Boundary:** This clarification defines no failure, cancellation,
  interruption, terminal-outcome, post-run availability, retention, or access
  semantics. Issue #13 retains those questions.

### Derived clarification: aggregation is permissible when semantic distinctions survive

- **Statement:** A conforming realization may batch, aggregate, group, or
  otherwise carry multiple effective-condition occurrences through one
  semantic-boundary interaction, provided that doing so preserves each
  condition occurrence's condition-specific provenance and governed-scope
  attribution at the semantic level `TL-INV-036` requires.
- **Derived from:** The accepted floor requires occurrence-specific provenance
  and scope attribution, not one physical event per occurrence. ADR-025 already
  binds captured provenance to the specific occurrence and governed scope
  without requiring a physical representation shape.
- **Why no new choice is introduced:** The decision selects no canonical event,
  message, callback, or serialization schema; it only prevents aggregation from
  destroying distinctions the invariant already requires.
- **Failure if omitted:** `TL-INV-036` could be misread as requiring exactly one
  physical event per condition occurrence, importing a mechanism the accepted
  authority does not select.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `formal-model-or-analysis`, and
  `architecture-or-implementation`.

### Separately governed mechanisms and policies

Push versus pull, synchronous versus asynchronous acquisition, callbacks,
events, queues, channels, streams, buffers, logs, files, RPC, IPC, databases,
telemetry, serialization, event schemas, identifier formats, process topology,
storage engines, polling mechanisms, concrete adapter APIs, and concrete
harness APIs remain `no-normative-impact` in `architecture-or-implementation`
unless a later accepted decision requires an observable mechanism.

The identity of eligible or authorized capture participants, access policy,
privacy policy, disclosure levels, persistence, retention, durable delivery,
cross-run identity, comparability, replay, reproducibility, and conditions
outside the universal floor require separate classification if a durable
product obligation is proposed.

## Decision

The universal floor for `TL-INV-036` is a **realizable semantic-boundary
capture handoff**.

For every effective execution condition covered by `TL-INV-036`, TURNLOCK MUST
preserve the required condition-specific provenance and governed-scope
attribution until that provenance participates in a realizable semantic-boundary
capture handoff.

A handoff is realizable only when an eligible conforming capture context could
be established in time to acquire the required provenance as part of the
semantic-boundary interaction, without depending on inaccessible transient
internal state, accidental timing against TURNLOCK's internal execution, or
reconstruction from later mutable state, human recollection, or agent
recollection.

Conceptually:

```text
eligible conforming capture context can be established
        ↓
TURNLOCK reaches the semantic boundary
        ↓
required provenance participates in a realizable boundary handoff
        ↓
the boundary interaction is discharged
        ↓
the universal provenance obligation no longer
requires post-handoff capturability by itself
```

This shape is not sufficient:

```text
TURNLOCK internally knows required provenance
        ↓
the provenance exists transiently for an implementation-defined instant
        ↓
an external party would have to poll at exactly the right instant
or win a race against internal destruction
        ↓
the provenance disappears
```

The second shape is a nominal opportunity, not a realizable capture
opportunity.

### Sufficiency is not duration

The sufficiency of the capture opportunity is not defined by wall-clock
duration. No minimum number of milliseconds, seconds, workflow transitions,
scheduler turns, process lifetimes, scope lifetimes, or invocation lifetimes is
part of the core contract. An opportunity MAY be logically instantaneous when
capture is realizable as part of the boundary interaction itself. Instantaneous
boundary availability is therefore a conforming special case of the accepted
floor when it denotes a genuine semantic handoff rather than a transient
internal state or a race to observe.

### Capture capability and actual capture

Provenance being genuinely capturable and provenance being actually captured by
a consumer are distinct. The universal floor requires the first, not the second.
A TURNLOCK execution does not become non-conforming solely because no conforming
capture context was established for a particular invocation, provided the
runtime exposes a real semantic capability through which an eligible capture
context could have been established in time to participate in the required
handoff. In that situation TURNLOCK does not acquire an indefinite storage or
retention obligation merely because nobody chose to capture the provenance.

Conversely, a runtime is non-conforming when there is structurally no way for a
conforming capture context to be established in time to participate before
TURNLOCK destroys the required provenance, and the runtime nevertheless claims
the provenance was capturable. Architecture and integration must make it
possible for an eligible capture context to be established before it is too
late to participate in the required handoff. This decision does not fix exactly
when configuration occurs, does not require dynamic attachment during execution
when pre-configuration can suffice, and does not select a plugin, adapter,
process, subscriber, callback, or API model.

Conceptually:

```text
capture path structurally realizable
!=
consumer actually attached
```

### Delivery, acknowledgment, and consumer absence

The core contract is an opportunity to acquire, not a universal
reliable-messaging contract. It MUST NOT require successful end-to-end delivery,
consumer processing success, consumer persistence, consumer acknowledgment,
retry-until-success, exactly-once or at-least-once delivery, queue durability,
backpressure, indefinite blocking waiting for a receiver, or TURNLOCK-operated
persistent buffering. If a conforming eligible capture participant is attached
and then crashes, refuses data, mishandles data, disconnects, or fails to persist
it, that fact alone does not automatically create an indefinite
provenance-retention obligation for TURNLOCK core.

The absence of an active capture consumer does not by itself make a conforming
runtime non-conforming, provided the realizable capture capability described
above exists. Consumer absence also does not automatically require TURNLOCK to
retain provenance until some consumer later appears.

These limits state the universal floor only. A concrete integration, profile, or
later accepted decision MAY impose stronger delivery, durability, or retention
guarantees above it.

### When the universal obligation no longer requires capturability

Once required provenance has participated in a conforming realizable
semantic-boundary capture handoff, `TL-INV-036` alone does not require that
provenance to remain capturable. "May become unavailable" therefore means that
this invariant no longer independently forbids it. Another accepted invariant,
ADR, integration contract, profile, Issue #13 resolution, or future decision may
independently require later availability or retention; this decision does not
override any such obligation and does not imply scope-long, invocation-long,
workflow-long, or pre-inspection availability.

### Occurrence, scope, and aggregation

This decision preserves ADR-024 and ADR-025 occurrence and scope semantics. The
capture obligation applies to the provenance relationship between an effective
execution-condition occurrence and the governed execution scope, and the handoff
must preserve enough information to satisfy the accepted semantic distinction
and scope-attribution requirements. This decision introduces no global identity,
stable run identifier, hash, public identifier, UUID, cross-run key, workflow
revision identity, comparison identity, or equality proof.

A conforming realization MAY carry multiple provenance occurrences through one
semantic-boundary interaction. It MUST NOT destroy the condition-specific
provenance required by ADR-025, occurrence distinction at the semantic level
required to preserve the provenance relationship, or governed-scope attribution.
One semantic occurrence does not necessarily correspond to one physical event,
message, or callback. This decision selects no canonical event schema, event
type, or serialization.

### Failure, cancellation, and interruption

ADR-024 already establishes that a condition-to-scope governing relationship
does not become semantically nonexistent merely because execution later fails,
is cancelled, or is interrupted. This decision applies the same boundary to the
capture obligation: later failure, cancellation, or interruption cannot
retroactively erase an already-incurred obligation that the condition's
provenance reach the required realizable handoff. Defining capture solely as an
action after successful workflow completion is therefore non-conforming for a
condition that genuinely governed execution.

This decision does not define the complete failure lifecycle, failure
reporting, terminal-outcome records, retries, persistence, retention, recovery,
or post-failure availability. Issue #13 retains the detailed completed and
non-completed execution-inspectability problem.

### Authorization and privacy remain separate

This decision defines no authorization model. It defines no user, role, tenant,
ACL, RBAC, capability, credential, authentication method, disclosure policy,
secret management, encryption, or privacy policy. An eligible capture context
may be subject to separately governed authorization or privacy policy.

ADR-025's separation remains in force:

```text
underlying provenance capture capability
!=
what a particular consumer is allowed to see
```

The semantic capture obligation does not mean that every consumer must be
authorized, must receive the raw value, must receive the same view, or that
protected values must become publicly visible. A consumer receiving a generic
protected view does not change ADR-025's condition-specific requirements
underneath that view, and authorization policy must not be confused with
whether a real boundary capture capability exists at all.

### Evaluation and optimization remain outside core

The capture handoff exists so that another layer MAY acquire effective
execution-condition provenance. TURNLOCK core still does not decide which
provenance matters for a property `P`, whether two executions are comparable,
whether a condition difference is causally important, what "better" means,
whether a workflow should be replaced, how to optimize a workflow, or whether
captured provenance is sufficient for reproduction or replay. ADR-019 and
`TL-INV-034` remain fully applicable.

### Capture is not persistence or retention

The following separation remains:

```text
realizable capture handoff
!=
post-handoff persistence
!=
retention duration
```

A handoff may be implemented using machinery that buffers or persists data, but
such implementation behavior does not become a normative persistence guarantee.
A future profile or layer MAY require stronger semantics such as buffered
capture, availability until scope end, availability until invocation end, durable
delivery, persistent execution records, retention periods, acknowledgments, or
replayable streams. Those are valid future extensions above the core floor and
are not part of this decision.

This ADR clarifies ADR-024 and ADR-025. ADR-024 accepted the provenance floor;
ADR-025 defined how that floor remains meaningful when a known value is
protected; this ADR defines when the required capture opportunity is genuinely
realizable. It neither amends nor reinterprets ADR-024 or ADR-025.

ADR-018 and `TL-INV-033` own minimum completed-execution inspectability. This
decision does not clarify or amend them. Issue #17 concerns only the minimum
boundary semantics needed for the `TL-INV-036` capture obligation to be genuine.
Issue #13 retains authority over detailed execution inspectability, including
completed and non-completed fact sufficiency, later availability, retention,
access, and privacy.

## Rationale

ADR-024 already rejects provenance that exists only as inaccessible transient
internal state. ADR-025 makes the capture opportunity a material temporal
boundary because condition-specific provenance may not be irreversibly lost
before or during it. Requiring only that the data existed momentarily makes
`capturable` nominal and unfalsifiable: no conforming consumer could ever
acquire the provenance, yet a runtime could claim conformance.

Requiring survival until scope or invocation completion would introduce stronger
availability semantics that the current product intent does not entail and would
overlap with the availability, retention, and non-completed-outcome work owned
by Issue #13. Requiring consumer acknowledgment would silently import
reliable-delivery, persistence, backpressure, and consumer-lifecycle semantics
that no accepted decision establishes.

A realizable semantic handoff is therefore the weakest contract that makes
capture externally meaningful, remains falsifiable, prevents race-to-observe
implementations, preserves mechanism freedom, does not require actual capture on
every invocation, and does not silently become persistence or retention.

The floor remains falsifiable because a conformance review or test can ask
whether an eligible conforming capture context could have been established in
time and could have acquired the required provenance as part of the boundary
interaction, and can answer that question without selecting any transport,
storage, or consumer architecture.

## Alternatives considered

### Alternative A — instantaneous boundary availability

Accepted only as a conforming special case of the accepted floor. A logically
instantaneous opportunity suffices when acquisition is realizable as part of the
boundary interaction itself. Instantaneous availability that denotes an
unobservable internal instant separable from the interaction does not.

### Alternative B — realizable capture boundary

Accepted as the universal core floor. The representation must reach a
semantic-boundary interaction through which an eligible conforming capture
context could actually acquire the required provenance without an accidental
timing race, inaccessible internal state, or later reconstruction.

### Alternative C — scope-bounded availability

Rejected as the universal core contract. Requiring provenance to remain
available for the entire governed scope merely because it governed that scope
adds stronger availability semantics not entailed by ADR-024, ADR-025, or the
accepted floor, and it overlaps Issue #13's availability and retention work.

### Alternative D — invocation/lifecycle-bounded availability

Rejected as the universal core contract for the same reason. Requiring
availability until invocation completion would silently define a post-handoff
retention obligation and a terminal-outcome dependency that no accepted
authority establishes.

### Alternative E — profile/layer-dependent capture guarantees

Accepted as an optional extension above the universal floor. Profiles,
integrations, or later decisions may require buffered capture, scope-long or
invocation-long availability, durable delivery, persistence, retention periods,
or replayable streams. Such layers cannot make the core obligation nominal.

### Alternative F — another bounded semantic contract

Not required. No additional bounded contract was identified that makes
`capturable` falsifiable without implying persistence, acknowledgment, or a
concrete mechanism.

## Consequences

### Benefits

- `capturable` becomes a falsifiable boundary contract rather than a claim about
  momentary internal existence.
- Runtime and adapter designs cannot satisfy the invariant through
  race-to-observe behavior or inaccessible transient state.
- The floor stays mechanism-independent and harness-independent.
- Consumer absence, delivery failure, and participant failure do not silently
  create retention or persistence obligations.
- Stronger availability, persistence, retention, authorization, and delivery
  semantics remain available above the floor through explicit decisions.
- ADR-024, ADR-025, ADR-018, ADR-019, and Issue #13 retain their scopes.

### Costs and obligations

- Runtime and adapter designs must provide a real capture boundary through which
  an eligible conforming capture context can participate before required
  provenance is irreversibly lost.
- Conformance review must be able to distinguish a realizable handoff from a
  nominal, race-dependent, or post-hoc-reconstruction capture claim.
- Architecture must keep the capture boundary distinct from delivery,
  acknowledgment, persistence, retention, authorization, and ordinary
  inspection surfaces.
- Failure, cancellation, and interruption paths must not discard required
  provenance before the handoff when the condition already governed execution.
- Concrete authorization, privacy, persistence, retention, and delivery choices
  remain unresolved and may require later decisions before implementation.

## Invariant admission

No new invariant is admitted. This decision clarifies the satisfaction condition
of `TL-INV-036`.

The repository invariant-admission test yields:

1. **Independent universal obligation:** The decision adds no obligation
   independent of effective execution-condition semantic distinction,
   governed-scope attribution, and boundary capturability already owned by
   `TL-INV-036`.
2. **Existing-owner test:** It defines when the existing word `capturable` is
   genuinely satisfied; the existing invariant is the correct owner.
3. **Violation test:** Once `TL-INV-036` is correctly interpreted, a runtime that
   exposes required provenance only through an inaccessible timing race fails
   `TL-INV-036` itself.
4. **Traceability-value test:** A second identity would duplicate and split the
   same condition-to-scope provenance obligation without adding an independently
   satisfiable product requirement.

`TL-INV-036` keeps its stable identity. Its normative wording, ADR mapping, and
formal traceability note are updated to include this clarification. No invariant
number is reserved or left unused by this decision.

## Formal applicability

`TL-INV-036` remains `partial` for core TLA+ formalization and `not-yet-modeled`
for verification.

A future abstract model can represent an abstract temporal relation of the
following shape:

```text
required provenance exists / is owed
        ↓
capture handoff not yet discharged
        ↓
required provenance cannot be irreversibly lost

capture handoff discharged
        ↓
TL-INV-036 itself no longer requires post-handoff availability
```

The model may abstract whether a provenance obligation is pending, whether the
semantic capture boundary has been realized or discharged, and whether required
provenance has been impermissibly lost beforehand. It MUST NOT prematurely
select wall-clock duration, queue semantics, retry semantics, consumer
acknowledgments, storage, process topology, or adapter protocols.

No executable TLA+ model currently exists. No property, state variable, action,
configuration, or evidence identifier is introduced, and no `modeled` or
`checked` claim is made.

## References

- `docs/specification/turnlock-spec.md`
- `docs/adr/adr-018-require-completed-workflow-execution-inspectability.md`
- `docs/adr/adr-019-keep-evaluation-and-optimization-policy-outside-turnlock-core.md`
- `docs/adr/adr-024-preserve-effective-execution-condition-provenance.md`
- `docs/adr/adr-025-preserve-condition-specific-provenance-without-requiring-protected-value-disclosure.md`
- `docs/formal/invariant-mapping.md`
- `formal/verification.yaml`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
- GitHub Issues #4, #13, #15, #16, and #17
