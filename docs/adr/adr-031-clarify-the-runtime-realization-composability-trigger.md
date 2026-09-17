---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Clarify the runtime-realization composability trigger"
id: "ADR-031"
status: "accepted"
date: "2026-09-17"
decision_body_sha256: "1b47062e0a7d36a55e16db344d1105e7f3b05899e7cdf8b3fe3d56ed9c37e24d"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-030"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Trigger condition for TL-INV-038 runtime-realization composability"
  - "Anti-circular interpretation of supported external realizations"
  - "Conformance when semantically preserving runtime substitution is technically realizable"
---

# ADR-031: Clarify the runtime-realization composability trigger

## Context

ADR-030 accepted TURNLOCK Core as a runtime-composable execution substrate.

Its substantive Decision states that, for a concrete execution realization that
is not fixed by TURNLOCK semantics and for which an alternative realization can
preserve those semantics, Core must provide a supported runtime composition path
rather than making Core modification or recompilation the only substitution
path.

The synchronized normative specification introduced a narrower-looking phrase
in several places:

`a supported alternative realization`

or equivalent wording in which `supported` can be read as a precondition on the
obligation.

That wording permits a circular interpretation:

```text
Core exposes no runtime composition path
→ Core declares no alternative supported
→ no "supported alternative" exists
→ runtime composability supposedly has no application
```

That interpretation is inconsistent with ADR-030's substantive Decision and
with the product-owner decision ADR-030 records.

The distinction is:

```text
trigger
=
the realization is not fixed by TURNLOCK semantics
+
a semantically preserving alternative is technically realizable at runtime
in the supported harness or execution environment

resulting Core obligation
=
provide a supported runtime composition path
```

Pre-existing support by the current Core implementation is therefore not itself
part of the trigger.

## Discovery classification

The mismatch is `authority-conflict-or-uncertain` in the pre-clarification
synchronized corpus because the accepted ADR-030 Decision and the wording of its
normative projection admit different readings.

No new product decision is introduced here.

The product owner confirms the ADR-030 reading in which technical runtime
realizability plus semantic preservation triggers the Core composition
obligation.

After this clarification, the synchronized normative correction is
`derived-from-existing-authority`.

## Decision

ADR-030 is clarified as follows.

For an execution-relevant concrete realization required to carry out TURNLOCK
execution but not itself fixed by TURNLOCK semantics:

```text
if

a semantically preserving alternative realization
is technically realizable at runtime
in a TURNLOCK-supported harness or execution environment

then

TURNLOCK Core must provide a supported runtime composition path
through which that alternative can be supplied or established
without modifying or recompiling Core
```

Core modification or recompilation must not be the only substitution path in
that case.

The absence of an existing Core runtime composition path is not evidence that
the alternative is outside the obligation.

A Core therefore MUST NOT discharge the runtime-composability requirement merely
by declaring an otherwise runtime-realizable, semantically preserving
alternative unsupported because Core lacks the runtime composition path required
by TL-INV-038.

This clarification does not require runtime substitution where the alternative
would change TURNLOCK semantics or where the relevant supported harness or
execution environment makes the substitution technically unrealizable.

Once a realization is supplied or established through the runtime composition
path, ADR-030's existing causal-timing and no-silent-substitution requirements
remain unchanged:

```text
realization becomes effective
before its first intended causal use

and

once accepted as governing that use
it is not silently bypassed by another realization
unless TURNLOCK semantics authorize that alternative
```

## Responsibility boundary

This clarification does not broaden TURNLOCK into a universal injection or
environment-control platform.

The following remain distinct:

```text
semantic decision fixed by TURNLOCK
→ TURNLOCK may own that semantic decision

semantically preserving alternative realization
technically realizable at runtime
→ Core must expose the TL-INV-038 composition path

opaque or technically unavailable determinant
outside the supported harness/environment capability
→ may remain unavailable, unknown, or uncontrollable
```

A harness or execution environment may have genuine capability limitations.

A limitation caused only by Core having failed to provide the required runtime
composition path is not such a capability limitation.

## Mechanisms not selected

This clarification selects none of:

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
before-step interception
after-step interception
```

The mechanism remains an architecture or implementation choice.

## Invariant consequence

No new invariant identity is admitted.

`TL-INV-038` remains the sole stable invariant for runtime-realization
composability.

Its wording is clarified so that:

```text
pre-existing "support"
```

cannot be used as a circular precondition that nullifies the invariant.

`TL-INV-038` continues to require:

```text
runtime composition when the clarified trigger applies
causal effectiveness before the governed use
no silent unauthorized substitution
```

No invariant is added for experiment validity, control status, causal-control
classification, scope fidelity, sampling, evaluation, or optimization.

## Formal applicability

The clarification does not change formal applicability.

`TL-INV-038` remains:

```text
formalization: not-applicable
tla.mapping_status: not-applicable
verification: not-yet-modeled
```

for the current core TLA+ state-machine scope.

No TLA+ state variable, action, property, configuration, or placeholder is
introduced.

## Consequences

The normative specification must remove every wording that makes pre-existing
Core support a precondition for the runtime-composability obligation.

Conformance review must distinguish:

```text
genuine technical impossibility in the supported harness/environment
```

from:

```text
absence of the required Core runtime composition boundary
```

The second is a possible TL-INV-038 violation, not an exemption from it.

ADR-030 remains accepted and immutable. This ADR clarifies its interpretation;
it does not edit, supersede, or replace ADR-030.
