---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Adopt structured proto-ring repository governance"
id: "ADR-052"
status: "accepted"
date: "2026-10-02"
decision_body_sha256: "9a8b529dec8d67e50fe9588740634a57197357bbd44822636810c29d4b42bae3"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-051"
  supersedes: []
  confirms:
    - "ADR-050"
governs:
  - "Repository Governance Model version 2 adoption"
  - "Structured proto-ring governance registries and profiles"
  - "Authority migration for active governance bindings and validation membership"
---

# ADR-052: Adopt structured proto-ring repository governance

## Context

ADR-050 permits shared governance implementation without transferring TURNLOCK
authority. ADR-051 requires proto-ring for applicable generic repository
governance. Proto-ring now provides persistent Governance Binding, Repository
Integrity, Projection, and Evidence Requirement structures discovered through
Repository Governance Model version 2.

Turnlock-Rust currently distributes the corresponding active facts across
contract-specific documents, Python-owned validation membership, and prose
projection and evidence mappings. Those duplicate carriers can drift despite
the mandatory-provider decision.

This decision changes repository governance only. It does not change TURNLOCK
product semantics, formal semantics, assurance claims, hostile-review policy,
evidence truth, readiness, or bounded verification evidence.

## Discovery classification

```text
no-normative-impact; repository-governance and integration realization
```

## Decision

Turnlock-Rust adopts Repository Governance Model version 2 and all eight
applicable capabilities. Its active proto-ring executable and governance
contract identities are owned by one consumer Governance Binding Registry.

`requirements.txt` remains authority for the exact executable proto-ring
provider identity. The registry and effective installed realization remain
secondary representations of that authority.

Turnlock-Rust adopts one persistent Repository Integrity profile as the sole
owner of mandatory validation membership and order. The Python entry point
loads and evaluates that profile and renders diagnostics; it no longer defines
membership or ordering.

Turnlock-Rust adopts one Projection Registry for actual direct authority-to-
secondary relationships and one Evidence Requirements Registry for the two
Gate A Exact Evidence Binding requirements. Gate A subject and protocol identity
construction, candidate parsing, current/stale sequencing, finding lifecycle,
materiality, challenge, re-adjudication, and readiness remain Turnlock-owned.
Exact Evidence Binding remains only the generic comparator.

Active contract pins and machine-governing mappings move out of the former
Shared Governance Provider and Exact Evidence Binding carriers. Those carriers
are removed after their unique facts have explicit new owners. Historical
ADR-050 and ADR-051 remain immutable historical decisions.

No governed-object identity is introduced solely for this migration. Existing
ADR, invariant, and formal-claim identities remain unchanged except for adding
this ADR's ordinary catalog identity.

## Authority preservation

The migration does not transfer authority over:

- TURNLOCK product or formal semantics;
- accepted decision bodies;
- the formal-assurance graph;
- hostile-review records or protocol semantics;
- bounded verification evidence;
- Gate A or qualification truth; or
- consumer-local repository paths, commands, provider installation, and
  environment realization.

## Consequences

Repository governance becomes mechanically discoverable through RGM v2.
Contract and executable bindings have one active owner. Validation membership
and order have one persistent owner. Projection and evidence requirements have
one active declaration surface. Consumer adapters continue to realize local
identity, package, environment, and review-record semantics without redefining
the generic proto-ring contracts.

Any future change to these active bindings or profiles remains an explicit
Turnlock-Rust repository change subject to the same authority and validation
boundaries.

## Verification obligation

Completion requires all routed structures to load through the exact published
proto-ring provider, the effective provider realization to match the
`requirements.txt` pin, the former duplicate carriers and pins to be absent,
Gate A to consume the routed Evidence Requirements Registry without hardcoded
requirement fallback, generated ADR projections to be current, and the complete
canonical Repository Integrity evaluation to pass without repository mutation.
