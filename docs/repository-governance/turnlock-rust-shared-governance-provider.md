---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust Shared Governance Provider binding"
shared_governance_provider:
  mandatory: true
  authority_adr:
    id: "ADR-051"
  contract:
    repository: "fanilosendrison/proto-ring"
    commit: "974ca31ff12630a90da6371cc27c1f5ef0cc590e"
    path: "docs/contracts/shared-governance-provider.md"
---

# Turnlock-Rust Shared Governance Provider binding

The `shared_governance_provider` frontmatter is the machine-readable local
projection of the accepted authority identified there. The prose below remains
human-readable guidance and does not replace that authority.

## Shared contract

Apply the canonical proto-ring Shared Governance Provider contract at this
immutable identity:

```text
fanilosendrison/proto-ring
974ca31ff12630a90da6371cc27c1f5ef0cc590e
docs/contracts/shared-governance-provider.md
```

Turnlock-Rust adopts the canonical proto-ring Shared Governance Provider
contract at the immutable identity above.

Mutable proto-ring state is not authority for this binding.

## Binding effect

For generic/reusable repository-governance responsibilities, Turnlock-Rust uses
proto-ring as the mandatory provider.

An applicable proto-ring mechanism must not be replaced, copied, forked, or
reimplemented locally.

## Turnlock-Rust authority remains local

Turnlock-Rust continues to own locally:

```text
product semantics
accepted ADRs
formal-assurance authority and configuration
formal semantics
hostile-review evidence
bounded verification evidence
repository-specific profiles and overlays
repository-specific mappings and bindings
generated repository artifacts
Turnlock-specific validation obligations
repository coordinates and work-management configuration
```

## Existing proto-ring bindings

Projection Integrity retains its own binding and its own immutable
contract-authority pin in
`docs/repository-governance/turnlock-rust-projection-integrity.md`.

The `proto-ring` package in `requirements.txt` retains its own
executable-provider pin.

The Shared Governance Provider contract upgrades neither of those pins.

Each identity remains governed separately.

## New repository-governance mechanisms

Classify each new or changed repository-governance responsibility using the
shared contract:

```text
Turnlock-specific → local
generic/reusable → proto-ring
```

## Immutable binding

This binding is the Turnlock-Rust contract-authority pin for the Shared
Governance Provider contract.

It identifies only the governance contract adopted by Turnlock-Rust.

Changing this immutable proto-ring binding is an explicit Turnlock-Rust
repository change.

## Authority boundary

Using proto-ring as mandatory provider for generic governance does not make
proto-ring authoritative over TURNLOCK.

This binding changes repository governance only. It does not change TURNLOCK
product meaning, formal-assurance semantics, hostile-review claims, bounded
verification evidence, accepted ADR content, or the authority order in
`AGENTS.md`.
