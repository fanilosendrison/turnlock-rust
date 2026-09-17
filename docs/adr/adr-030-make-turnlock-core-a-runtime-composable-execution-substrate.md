---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Make TURNLOCK Core a runtime-composable execution substrate"
id: "ADR-030"
status: "accepted"
date: "2026-09-17"
decision_body_sha256: "8002b7b57302a286233d69c827313d17cee945f7e1c6d174451fe05070c87acf"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms:
    - "ADR-007"
    - "ADR-010"
    - "ADR-019"
    - "ADR-024"
    - "ADR-025"
    - "ADR-026"
    - "ADR-029"
governs:
  - "Runtime composability of execution realizations not fixed by TURNLOCK semantics"
  - "Public runtime composition boundary for supported external realizations"
  - "No Core modification or recompilation as the sole extension path for supported external realizations"
  - "Causal timing and no-silent-substitution requirements for accepted external realizations"
---

# ADR-030: Make TURNLOCK Core a runtime-composable execution substrate

## Context

ADR-019 deliberately keeps evaluation and optimization policy above Core.
ADR-024 through ADR-026 ensure that TURNLOCK-known effective
execution-condition provenance can cross TURNLOCK's semantic boundary.
ADR-029 keeps general filesystem, repository, tool, OS, sandbox, and permission
policy outside Core. Those decisions fix responsibilities around Core, but they
do not by themselves ensure that a higher-level system can supply a semantically
equivalent external execution realization to an already-built Core without
modifying or recompiling Core.

The distinction matters because the accepted corpus constrains the first
direction but not the second:

```text
TURNLOCK execution
        ↓
effective-condition provenance
        ↓
higher-level system
```

is already protected for TURNLOCK-known conditions under ADR-024 through
ADR-026. The complementary direction:

```text
higher-level system
        ↓
supported external realization
        ↓
TURNLOCK execution
```

was not established. An implementation could satisfy every current invariant
while internally hardwiring every execution realization, so that changing an
externalizable realization requires editing and recompiling Core. ADR-019
established that evaluation and optimization policy is external to Core; it did
not establish that an already-built Core must support runtime composition
without source modification or recompilation.

The product owner explicitly requires that runtime-composable boundary where it
is technically realizable without changing TURNLOCK semantics. This ADR records
the accepted decision without editing any accepted ADR body.

## Discovery classification

### Accepted product decision: TURNLOCK Core is a runtime-composable execution substrate

- **Statement:** For a concrete execution realization that is not fixed by
  TURNLOCK semantics, and for which an alternative realization can preserve
  those semantics, TURNLOCK Core must provide a supported runtime composition
  path rather than making Core modification or recompilation the only
  substitution path. A supported external realization must become effective
  before its first governed causal use, and once TURNLOCK has accepted an
  external realization as governing an applicable use, that use must not
  silently execute through a different realization unless the applicable
  TURNLOCK semantics authorize that alternative.
- **Source and evidence:** The pre-decision corpus fixed the
  evaluation/optimization-policy boundary (ADR-019, `TL-INV-034`), outbound
  effective-condition provenance (ADR-024 through ADR-026, `TL-INV-036`),
  environment-permission responsibility (ADR-029), and main-agent continuity
  (ADR-007, ADR-010). It did not determine whether an already-built Core must
  offer runtime composition without Core source modification or recompilation,
  so multiple behaviors remained compatible with current authority. The product
  owner resolved that open question explicitly in favor of runtime
  composability.
- **Existing authority:** ADR-003 makes product intent and derived invariants
  govern implementation; ADR-007 and ADR-010 preserve main-agent continuity and
  harness independence; ADR-014 makes the workflow program the source of
  declared orchestration; ADR-019 and `TL-INV-034` keep evaluation and
  optimization policy outside Core; ADR-024 through ADR-026 and `TL-INV-036`
  own outbound effective-condition provenance; ADR-029 keeps general
  environment permissions outside Core; ADR-027, ADR-028, and `TL-INV-037`
  stabilize an accepted invocation's governing workflow definition. None of
  those sources establishes or forbids an inbound runtime composition boundary.
- **Semantic disposition:** `decision-required`, resolved by this accepted
  decision. It is not reclassified as `derived-from-existing-authority` for the
  prior corpus state: ADR-019 established the evaluation/optimization-policy
  boundary, not runtime/binary composability with an already-built Core.
- **Affected layers:** `normative-contract`, `decision-history`,
  `formal-model-or-analysis`, `architecture-or-implementation`,
  `integration-or-conformance`, and `repository-governance-or-documentation`.
- **Related discoveries or consequences:** The derived universal obligation
  below is admitted as `TL-INV-038`. The concrete composition mechanism remains
  separately governed and is not selected here.
- **Required authority:** Product-owner acceptance through the repository ADR
  process.
- **Next action:** Synchronize the normative specification with the runtime
  composition boundary, admit `TL-INV-038`, record formalization
  `not-applicable`, and regenerate the affected ADR and formal projections.

### Derived obligation: supported external realizations must not be trapped behind mandatory Core modification

- **Statement:** TURNLOCK Core must not require modification or recompilation of
  Core as the only supported substitution path for an execution-relevant
  concrete realization that is not fixed by TURNLOCK semantics, when a
  supported alternative realization can preserve the applicable TURNLOCK
  semantics. A supported external realization must be able to become effective
  before the first causal use it is intended to govern, and an accepted
  external realization for a governed use must not be silently bypassed by an
  unauthorized substitute.
- **Derived from:** The accepted product decision in this ADR, which makes
  runtime composability a product requirement, combined with the existing
  responsibility boundaries. After acceptance, an implementation that satisfies
  every other invariant while structurally trapping supported externalizable
  realizations behind a mandatory Core source edit and recompile contradicts
  the accepted decision.
- **Why no new choice is introduced:** The statement is the minimal normative
  form of the accepted decision. It preserves the mandatory
  `when doing so preserves TURNLOCK semantics` clause, does not require every
  execution determinant to be externally replaceable or controllable, and
  selects no extension mechanism.
- **Failure if omitted:** An implementation could claim conformance while
  making Core source modification or recompilation the only way to supply a
  supported alternative external realization, contradicting the accepted
  runtime composition boundary.
- **Semantic disposition:** `derived-from-existing-authority` after acceptance
  of this ADR.
- **Affected layers:** `normative-contract`, `decision-history`,
  `formal-model-or-analysis`, and `integration-or-conformance`.

### Separately governed composition mechanisms

Plugin systems, hooks, callbacks, middleware, dependency injection, Rust
traits, IPC, RPC, sockets, dynamic libraries, sidecars, environment variables,
service locators, resource registries, resource handles, event buses, process
topologies, and any other concrete composition mechanism remain
`no-normative-impact` in `architecture-or-implementation` and
`integration-or-conformance` unless a later accepted decision requires an
observable TURNLOCK capability. TURNLOCK Core does not select them, and their
choice is not an open product question of this ADR.

## Decision

TURNLOCK Core is a **runtime-composable execution substrate**.

```text
higher-level system
        │
        │ supported external realization
        ▼
public runtime composition capability
        │
        ▼
existing TURNLOCK Core
        │
        ▼
execution
```

For a concrete execution realization that is not fixed by TURNLOCK semantics,
and for which an alternative realization can preserve those semantics, Core must
provide a supported runtime composition path rather than making Core
modification/recompilation the only substitution path.

The realization must become effective before the causal uses it is intended to
govern.

If TURNLOCK accepts the realization for a governed use, TURNLOCK may not
silently bypass it or substitute another realization unless the applicable
TURNLOCK semantics authorize that alternative.

The clause `when doing so preserves TURNLOCK semantics` is mandatory. This
decision never permits silently changing the meaning of a TURNLOCK primitive to
facilitate experimentation. The following path must not be the only means of
substitution when the realization is an externalizable, supported realization:

```text
need different realization
        ↓
edit TURNLOCK Core source
        ↓
recompile/rebuild Core
        ↓
execute
```

### Semantic composability, source-level extensibility, and runtime composability are distinct

The decision concerns runtime composability and nothing broader:

```text
semantic composability
!=
source-level extensibility
!=
runtime composability
```

Semantic composability concerns whether primitives compose with preserved
meaning. Source-level extensibility concerns whether developers can change Core
source or build variants. Runtime composability concerns whether an already-built
Core can accept a supported external realization at runtime without source
modification or recompilation. ADR-030 decides only the third.

This decision completes, without replacing, the accepted boundaries:

```text
ADR-019 / TL-INV-034
evaluation and optimization policy stay outside Core

ADR-024/025/026 / TL-INV-036
TURNLOCK-known effective-condition provenance can leave Core
through a realizable capture handoff

ADR-029
TURNLOCK does not own general filesystem/tool/sandbox/ACL permissions

ADR-007
main-agent continuation preserves the existing cognitive lineage

ADR-010
product semantics remain harness-independent
```

The new direction:

```text
higher-level system
        ↓
supported external realization
        ↓
TURNLOCK execution
```

is complementary to the direction already protected:

```text
TURNLOCK execution
        ↓
effective-condition provenance
        ↓
higher-level system
```

### Scope

```text
semantic responsibility fixed by TURNLOCK
→ Core may own that semantic decision

concrete realization not fixed by TURNLOCK semantics
→ supported alternatives must not be structurally trapped behind a
  mandatory Core source edit/recompile when runtime composition is
  technically realizable without semantic change

opaque external determinant outside TURNLOCK capability
→ may remain uncontrolled or unknown
```

This is a composability requirement, not a requirement that all execution state
or every implementation decision be externally replaceable. TURNLOCK may still
own decisions that are part of its semantic responsibility. External provider
internals, environment facts, and other determinants outside TURNLOCK's
observation or control may remain unavailable, unknown, or uncontrollable.

The rule does not turn TURNLOCK into a general environment-control system.
Filesystem, repository, tool, OS, and sandbox restrictions remain
responsibilities of the surrounding environment under ADR-029 and Section 0.8B
unless a separately accepted TURNLOCK semantic says otherwise.

### Coding-agent-session boundary

TURNLOCK executes inside a live, mutable, stateful coding-agent session. The
accepted model is:

```text
live mutable coding-agent session
+
selected scoped execution controls
+
remaining uncontrolled/unknown variance
```

Runtime composability does not change that model:

```text
runtime-composable TURNLOCK execution
!=
fully controlled coding-agent session
```

Main-agent continuity remains real. The existing coding-agent lineage remains
the main agent where a main-agent region is declared, and a higher-level
experimental concern cannot silently replace that lineage with a fresh agent
and claim equivalent TURNLOCK semantics.

```text
restoring a repository
!=
erasing main-agent cognitive history

external experimental control
!=
permission to replace the existing main agent with a fresh agent
```

No mechanism is created or authorized by this ADR to make the entire session
hermetic or to remove the remaining uncontrolled or unknown variance.

### Rejected interpretations

- **`runtime composability means everything is injectable`:** Rejected. The
  obligation applies only to execution-relevant concrete realizations that are
  not fixed by TURNLOCK semantics and for which a supported alternative can
  preserve those semantics. It does not require every execution determinant,
  internal algorithm, scheduler decision, provider-internal state, or
  environment fact to be externally replaceable or controllable.
- **`runtime composability requires arbitrary pause/interception before every step`:** Rejected. The requirement is that a supported external realization
  can become effective before the first causal use it is intended to govern,
  and that an accepted realization is not silently bypassed. It does not
  require arbitrary mid-execution interception, before-step or after-step
  hooks, or any particular extension mechanism.

### Mechanisms explicitly not selected

ADR-030 selects none of:

```text
plugin system
Rust trait
dependency injection
middleware
callback
hook
IPC
RPC
socket
dynamic library
sidecar
environment variable
service locator
resource registry
resource handle
event bus
```

## Rationale

TURNLOCK is positioned below higher-level policy, methodology, and domain
systems, and ADR-019 already keeps evaluation and optimization policy above
Core. A higher-level system that experiments with, evaluates, or specializes
execution realizations must therefore be able to compose a supported external
realization with an already-built Core when the alternative preserves TURNLOCK
semantics. If the only substitution path were editing and recompiling Core,
the runtime boundary would silently leak implementation ownership into every
higher-level system and would make conformance depend on build access rather
than on semantics.

The boundary is deliberately narrow. It preserves the existing principle that
TURNLOCK owns decisions that are part of its semantic responsibility, and it
does not promise control over determinants outside TURNLOCK's capability. It
also preserves the existing prohibition on silently changing primitive meaning:
the mandatory preservation clause keeps runtime composition from becoming a
mechanism for quiet semantic drift.

The decision composes with the accepted responsibilities rather than replacing
them. Outbound provenance remains governed by ADR-024 through ADR-026. The
evaluation and optimization policy boundary remains governed by ADR-019.
General environment permissions remain governed by ADR-029. Main-agent
continuity remains governed by ADR-007. Harness independence remains governed
by ADR-010. ADR-030 adds only the inbound runtime composition obligation those
decisions left open.

## Alternatives considered

### Keep Core modification or recompilation as the only substitution path

Rejected by the product owner. It preserves internal implementation convenience
but prevents a higher-level system from supplying a semantically preserving
external realization to an already-built Core, contradicting the accepted
runtime composition boundary.

### Require every execution determinant to be externally replaceable

Rejected. The obligation does not extend to internal algorithms, scheduler
decisions, provider-internal state, or environment facts that are not fixed by
TURNLOCK semantics, and it does not require a universal injection framework.

### Require arbitrary pause or interception before every step

Rejected. Causal timing is fixed only before the first governed use, and an
accepted realization must not be silently bypassed. Arbitrary interception is
not required and would strengthen the obligation beyond the accepted decision.

### Select a concrete composition mechanism

Rejected for this decision. A plugin system, hook system, dependency-injection
framework, IPC protocol, process topology, dynamic library, resource registry,
or any other mechanism is an architecture or implementation choice. ADR-030
selects none and keeps them replaceable.

## Consequences

### Benefits

- A higher-level system can compose supported external execution realizations
  with an already-built Core without a mandatory Core source edit and
  recompile, when the alternative preserves TURNLOCK semantics.
- Causal timing and no-silent-substitution requirements keep an accepted
  realization meaningful for the use it governs.
- The decision adds no plugin, hook, IPC, DI, process, or registry mechanism to
  Core and does not weaken any accepted responsibility boundary.
- Main-agent continuity, environment-permission responsibility, and the
  evaluation/optimization-policy boundary remain intact.

### Costs and obligations

- Conformance review must reject a Core that makes modification or
  recompilation the only substitution path for a supported externalizable
  realization whose alternative preserves the applicable semantics.
- Runtime and adapter designs must make a supported external realization
  effective before its first governed causal use and must not silently bypass
  an accepted realization for a governed use.
- Documentation must not present runtime composability as a universal
  injection, interception, or environment-control guarantee.
- A later proposal that makes a currently fixed semantic realization externally
  replaceable in a way that changes TURNLOCK semantics requires its own accepted
  decision and synchronized normative and formal artifacts.

## Invariant admission

The invariant-admission test admits exactly one new invariant, `TL-INV-038`
(named the runtime-realization composability invariant). The result was decided
by the product owner and is recorded here rather than re-opened.

### Existing-owner result

No existing invariant completely owns the obligation:

- `TL-INV-034` owns the evaluation/optimization-policy boundary but not runtime
  substitution of external realizations.
- `TL-INV-036` owns outbound effective-condition provenance and capture but not
  inbound runtime composition.
- `TL-INV-037` owns active governing-definition stability but not runtime
  composition.
- `TL-INV-021`, `TL-INV-022`, and `TL-INV-023` own authoring and harness
  abstraction boundaries but not the already-built-Core runtime extension
  guarantee.

### Independent-obligation result

An implementation could respect all current invariants while doing this:

```text
all TURNLOCK semantics correct
+
all execution realizations internally hardwired
+
changing an externalizable realization requires editing/recompiling Core
```

Such an implementation must now be non-conforming. The obligation is therefore
independent and unconditional for supported externalizable realizations.

### Admission result

`TL-INV-038` is admitted with the exact normative wording recorded in
Section 3.36 of `docs/specification/turnlock-spec.md`. No other invariant is
created by this decision. Causal-control validity, session-state awareness,
control status, scope fidelity, experiment validity, and every future
evaluation concept remain outside Core and are not admitted as invariants here.

## Formal applicability

`TL-INV-038` is `formalization: not-applicable` for the current core TLA+
state-machine scope.

The distinctive obligation concerns whether an already-built runtime offers a
public composition capability without requiring Core source modification or
recompilation. That is primarily an architecture and conformance property
rather than a property of the core workflow state machine. No executable TLA+
model exists, and this decision introduces no reserved transition, state
variable, action, property, or configuration.

The model MUST NOT introduce `pluginInstalled`, `coreRecompiled`,
`externalHook`, `providerInjected`, `runtimePlugin`, or any equivalent state
variable, action, or property, and no fake formal property is created merely to
map the new invariant. Its manifest entry records
`mapping_status: not-applicable`, no properties, no state variables, no
actions, no configurations, and `verification: not-yet-modeled`.

## References

- `docs/specification/turnlock-spec.md` — Sections 0, 0.8B, 0.13E, 0.13F,
  0.14, 3.36, 4, 5.19, 6, 7, and 8
- `docs/adr/adr-007-preserve-main-agent-cognitive-lineage-and-ordinary-interactive-agency.md`
- `docs/adr/adr-010-keep-workflow-semantics-harness-independent-and-use-pi-as-the-first-reference-integration.md`
- `docs/adr/adr-019-keep-evaluation-and-optimization-policy-outside-turnlock-core.md`
- `docs/adr/adr-024-preserve-effective-execution-condition-provenance.md`
- `docs/adr/adr-025-preserve-condition-specific-provenance-without-requiring-protected-value-disclosure.md`
- `docs/adr/adr-026-define-a-realizable-semantic-boundary-capture-handoff.md`
- `docs/adr/adr-029-separate-local-execution-capabilities-from-immutable-invocation-orchestration.md`
- `formal/verification.yaml`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
