---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Adopt native proto-ring compatibility execution boundary"
id: "ADR-058"
status: "accepted"
date: "2026-10-17"
decision_body_sha256: "004f4f23f57a22bdc303b69da75a7aa16c8403807af26ffe5521a9e9a1d4c800"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-052"
  supersedes: []
  confirms:
    - "ADR-050"
    - "ADR-051"
governs:
  - "Native proto-ring executable compatibility boundary"
  - "Executable provider authority and external exact-source realization"
  - "Removal of Python proto-ring production execution"
---

# ADR-058: Adopt native proto-ring compatibility execution boundary

## Context

ADR-050 permits shared governance implementation without transferring TURNLOCK authority. ADR-051 requires applicable generic repository governance to use an immutable proto-ring provider. ADR-052 adopted structured repository governance but retained `requirements.txt` as authority for a Python package realization.

Proto-ring now exposes the generic mechanisms used by Turnlock-Rust through the standalone `proto-ring-compat` executable and compatibility transport version 1. Exact Phase 1 confrontation established parity between the former Python provider and the Rust executable at commit `814a884ccb759b0fdbde48673a74428d6443b847` for the governed Turnlock observations.

This decision changes repository-governance integration only. It does not change TURNLOCK product semantics, formal semantics, assurance claims, evidence meaning, consumer policy, validation membership, or validation order.

## Discovery classification

```text
no-normative-impact; repository-governance integration realization
```

## Decision

### Executable provider authority

The Governance Binding Registry is authoritative for executable provider identity. Its `proto_ring_executable` binding identifies exactly:

```text
repository = fanilosendrison/proto-ring
commit = 814a884ccb759b0fdbde48673a74428d6443b847
transport_version = 1
```

`requirements.txt` is no longer provider identity authority. Installed Python package provenance, including PEP-610 metadata, is not provider currentness authority.

A provider upgrade is an explicit Turnlock-Rust repository change to the authoritative binding. Mutable provider state such as a branch head is never executable authority.

### External exact-source realization

The provider is realized outside the Turnlock repository by checking out the exact bound source commit and building `proto-ring-compat` with the locked release build. The realization cache is commit-keyed. No Proto-Ring binary or source is committed into Turnlock.

The realized executable is accepted only when its manifest and binary digest validate and `engine.identity` exactly matches the authoritative repository, commit, and transport version. A binary digest is realization evidence, not provider authority.

Provider preparation is an explicit operation preceding Repository Integrity evaluation. Repository Integrity does not provision, fetch, or build the provider implicitly.

### Production integration boundary

All production generic Proto-Ring execution crosses the standalone executable through compatibility transport version 1. Turnlock invokes one request per process and validates the transport envelope, operation, typed outcome, and native identity before governed use.

Python `proto_ring` production execution is removed. Turnlock does not consume Proto-Ring Rust crate internals or add a Proto-Ring Rust crate dependency.

The compatibility transport is migration-local and non-normative. It creates no new Proto-Ring semantic contract and does not become TURNLOCK product authority.

### Consumer authority preservation

Turnlock continues to own all Turnlock policy, formal-assurance semantics, evidence construction, qualification truth, diagnostics, rendering, local command behavior, and repository-specific configuration. Generic Proto-Ring algorithms are delegated through the qualified executable operations rather than reproduced locally.

The exact Phase 1-qualified declarative normative-terminology policy remains unchanged and Turnlock-owned.

### Repository Integrity preservation

The persistent Repository Integrity profile remains the sole authority for mandatory validation membership and order. The migration changes only the realization of existing validation IDs. No validation ID is added, removed, renamed, or reordered.

## Amendment

ADR-058 amends ADR-052 as follows:

```text
The Governance Binding Registry, not requirements.txt, owns executable provider
identity. The effective realization is an external exact-source native build
accepted by engine.identity. Python package provenance is no longer an active
provider or currentness authority.
```

ADR-050 and ADR-051 remain confirmed: reusable mechanism ownership does not transfer Turnlock authority, and applicable generic governance continues to use an immutable Proto-Ring provider.

## Consequences

- The active executable provider is pinned to `814a884ccb759b0fdbde48673a74428d6443b847` in the Governance Binding Registry.
- `requirements.txt` contains only Turnlock's Python validation-tool dependencies.
- The effective provider realization is a generated secondary representation of the binding authority.
- Provider currentness compares the authoritative binding with `engine.identity`.
- CI explicitly prepares the exact native provider before Repository Integrity.
- Python Proto-Ring execution and package provenance are absent from production and tests.
- Repository Integrity validation IDs and order remain unchanged.
- Future provider upgrades require an explicit repository change and complete qualification.

## Alternatives considered

### Retain Python Proto-Ring as production provider

Rejected. It would retain duplicate executable-provider authority in `requirements.txt` and PEP-610 provenance after the qualified native boundary exists.

### Link Proto-Ring Rust crates into Turnlock

Rejected. It would couple Turnlock to provider internals instead of the migration compatibility boundary and would create a Rust dependency not required by repository-governance semantics.

### Download a mutable or prebuilt executable

Rejected. Mutable source and unauthoritative artifacts cannot establish the exact immutable provider identity required by ADR-050 and ADR-051.

### Build the provider implicitly during Repository Integrity

Rejected. Provisioning is an explicit prerequisite; validation must fail closed when its bound realization is absent or invalid.

## Verification obligation

Completion requires:

1. the raw Governance Binding Registry and composed state agree on the exact provider binding;
2. the exact-source build reports matching `engine.identity`;
3. every applicable generic governance wrapper executes through compatibility transport version 1;
4. no Python `proto_ring` import, module execution, requirement declaration, copied source, committed binary, or Proto-Ring Rust crate dependency remains;
5. the exact Repository Integrity validation ID list and order remain unchanged;
6. root-`.venv` governance composition and Repository Integrity complete without the historical pipe deadlock;
7. fresh-cache provider realization and full Repository Integrity pass without Python Proto-Ring installed; and
8. the canonical Turnlock Repository Integrity suite passes.
