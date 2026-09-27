---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Require proto-ring for applicable generic repository governance"
id: "ADR-051"
status: "accepted"
date: "2026-09-27"
decision_body_sha256: "e85bf449d9daa6878fb3728d839a72bd276f1933586014f5691e2a2c266383ec"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-050"
  supersedes: []
  confirms: []
governs:
  - "Mandatory use of proto-ring for applicable generic repository governance"
  - "Classification boundary between generic and Turnlock-specific repository governance"
  - "Immutable local adoption of the proto-ring Shared Governance Provider contract"
---

# ADR-051: Require proto-ring for applicable generic repository governance

## Context

ADR-050 authorized externalizing shared governance mechanisms to proto-ring
without transferring repository authority.

That formulation still theoretically permits a competing local mechanism while
an applicable generic proto-ring mechanism exists.

That possibility recreates the drift risk that extraction to proto-ring is
precisely intended to remove.

This decision remains limited to repository governance.

No TURNLOCK product semantics, formal assurance, hostile-review semantics, or
evidence semantics are modified.

## Decision — mandatory provider

For every repository-governance responsibility classified as generic/reusable,
Turnlock-Rust MUST follow the immutably bound proto-ring Shared Governance
Provider contract.

When an applicable proto-ring mechanism exists, Turnlock-Rust MUST consume it
and MUST NOT maintain a competing local implementation.

## Decision — new mechanisms

Before a new repository-governance mechanism is introduced, its responsibility
MUST be classified as Turnlock-specific or generic/reusable.

Turnlock-specific responsibility remains local.

Generic/reusable responsibility belongs in proto-ring and must be consumed
through an immutable Turnlock-local binding.

## Decision — missing provider capability

The absence of a generic capability from proto-ring does not authorize a
permanent local alternative.

A temporary local bridge requires an explicit later accepted governance
decision satisfying the exception conditions in the Shared Governance Provider
contract.

## Decision — authority boundary

TURNLOCK continues to own locally:

* TURNLOCK product semantics;
* accepted TURNLOCK decisions;
* formal-assurance authority;
* formal semantics;
* hostile-review evidence;
* bounded verification evidence;
* repository-specific profiles and overlays;
* repository-specific bindings and configuration;
* generated TURNLOCK artifacts; and
* Turnlock-specific validation obligations.

## Decision — immutable binding

The Shared Governance Provider contract is bound through the local document
`docs/repository-governance/turnlock-rust-shared-governance-provider.md` to the
exact immutable proto-ring identity:

```text
fanilosendrison/proto-ring
974ca31ff12630a90da6371cc27c1f5ef0cc590e
docs/contracts/shared-governance-provider.md
```

This contract pin is independent of the existing package/executable pin.

This decision does not automatically modify the Projection Integrity pin.

This decision does not automatically modify `requirements.txt`.

## Amendment

ADR-051 amends ADR-050 as follows:

```text
ADR-050's permission to use shared governance implementation externally remains
valid, but for generic/reusable repository governance the provider choice is no
longer optional: the applicable immutably bound proto-ring mechanism is
mandatory.
```

## Consequences

* No competing local implementation of a generic proto-ring primitive.
* New generic repository-governance machinery belongs in proto-ring.
* Turnlock-specific authority remains local.
* proto-ring upgrades remain explicit and immutably pinned.
* No product, formal, or evidence change is introduced.

## Verification obligation

Before this decision is treated as satisfied, the repository must demonstrate
that:

1. the local binding references the proto-ring Shared Governance Provider
   contract at the exact published SHA;
2. `AGENTS.md` routes any addition, modification, replacement, or design of
   repository governance to the local binding;
3. existing pins that are not explicitly migrated remain unchanged;
4. no copy of the generic contract exists in Turnlock; and
5. the canonical Turnlock validation passes.
