---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Allow shared governance implementation without transferring repository authority"
id: "ADR-050"
status: "accepted"
date: "2026-09-22"
decision_body_sha256: "c88c0381923cd8f20fef836974a465d14879070bd96cb7949aff69cc7f2b642b"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-017"
  supersedes: []
  confirms: []
governs:
  - "Ownership boundary between repository authority and shared governance implementation"
  - "Use of proto-ring as a reusable governance implementation provider"
  - "Immutable pinning and local bindings for shared governance tooling"
---

# ADR-050: Allow shared governance implementation without transferring repository authority

## Context

ADR-017 required TURNLOCK's adopted OKF Architecture Decision Record profile to
use repository-owned validation, rendering, tests, and CI enforcement. That
boundary was appropriate when the reusable asset was only a shared metadata
schema and the validation implementation still existed solely inside this
repository.

Ruu later adopted the same OKF profile and independently implemented the same
class of ADR validation and rendering machinery. A cross-repository extraction
audit preserved in `fanilosendrison/proto-ring` at
`a5c42454530aa90e82caa4d6904e699450cb3359` identifies this duplicated
governance implementation while preserving the distinction between shared
governance rules and repository-specific authority. The audit is non-normative;
it is evidence for this repository-governance decision, not authority over
TURNLOCK.

Keeping equivalent reusable governance mechanisms repository-owned now creates a
different integrity risk: fixes and strengthened checks can diverge between
repositories even when the intended governance contract is the same. TURNLOCK
therefore needs to permit a shared implementation owner without transferring
ownership of its product semantics, decision history, local governance bindings,
or evidence.

This is a repository-governance change only. It does not change TURNLOCK product
semantics, formal-assurance claims, hostile-review semantics, implementation
architecture, or the authority order established by existing accepted sources.

## Discovery classification

```text
decision-required, resolved; repository-governance-only
```

## Decision

### Shared governance implementation may be external

ADR-017's requirement for repository-owned validation, rendering, tests, and CI
enforcement is amended.

TURNLOCK MUST continue to own and govern whether a shared governance mechanism
is adopted and how it is bound locally, but the reusable implementation of that
mechanism MAY be owned outside this repository.

`fanilosendrison/proto-ring` is the initial intended shared implementation
provider for governance mechanisms demonstrated to be common to TURNLOCK and
Ruu. This decision does not define the complete scope or Product Intent of a
future Ring product.

### Repository authority remains local

Externalizing reusable implementation MUST NOT externalize TURNLOCK authority.

TURNLOCK continues to own:

* its normative product specification and accepted product meaning;
* its accepted ADR corpus and decision history;
* its repository-local ADR profile and local schema overlay;
* its repository-specific authority bindings and governance configuration;
* its migration and preservation evidence;
* its formal-assurance instance, claims, models, reviews, and verification
  evidence;
* its generated repository projections; and
* every TURNLOCK-specific validation obligation.

A shared implementation consumes those local authorities and bindings. It does
not replace them.

### Shared implementation owns mechanism, not repository facts

A shared governance provider MAY own reusable:

* validation and rendering engines;
* generic governance contracts;
* generic schemas whose canonical ownership has been explicitly assigned to
  that provider;
* generic regression tests for those mechanisms; and
* validation orchestration that is independent of TURNLOCK product semantics.

It MUST NOT silently create, infer, amend, or become canonical owner of
TURNLOCK-specific product facts, accepted decisions, local bindings, evidence,
or generated outputs.

Repository-specific overlays and checks remain admissible and MUST compose
without weakening the shared contract.

### Consumption must be immutable and reproducible

When TURNLOCK consumes governance implementation from another repository, the
consumed implementation MUST be pinned to an immutable identity sufficient to
reproduce the exact validation semantics used by the repository.

Validation MUST NOT depend on fetching mutable provider state such as an
unpinned `main` branch at validation time.

An upgrade of the shared implementation is an explicit repository change. Any
upgrade that changes accepted ADR metadata semantics, lifecycle rules,
preservation boundaries, authority boundaries, or another accepted governance
contract requires an appropriate later governance decision rather than being
treated as a tooling-only update.

### Generated artifacts remain TURNLOCK artifacts

A shared renderer MAY produce repository projections such as
`docs/adr/index.md`, but the generated file remains a TURNLOCK repository
artifact derived from TURNLOCK-owned canonical sources.

The shared provider does not acquire authority merely because its implementation
produces or validates the projection.

### Existing external OKF schema authority is unchanged

This decision does not transfer canonical ownership of the generalized OKF ADR
schema currently pinned by `docs/adr/adr-profile.yaml`.

That schema remains governed by its existing pinned canonical source until a
separate explicit decision changes that ownership.

### Extraction requires parity before local implementation removal

This decision authorizes later extraction of demonstrated reusable governance
implementation into proto-ring and pinned consumption from TURNLOCK.

Local implementation MUST NOT be removed merely because an external replacement
exists. Before replacement, the repository MUST establish that the shared
implementation preserves the accepted local governance contract and all
repository-specific constraints that remain applicable.

The extraction itself MUST remain semantics-neutral with respect to TURNLOCK
product meaning and accepted decision history.

## Rationale

The repository should own its authority, not necessarily every byte of generic
machinery used to enforce that authority.

Separating local authority from reusable enforcement removes duplicated
maintenance while preserving the ability of TURNLOCK to bind, extend, reject,
or upgrade shared governance explicitly.

Immutable consumption prevents a shared repository from becoming mutable
ambient authority. Local profiles and overlays preserve repository autonomy,
while shared engines make generic governance fixes available to multiple
consumers without manual reimplementation.

This also preserves ADR-040's bottom-up generalization discipline: only
governance already demonstrated as reusable is eligible for extraction. This
decision does not authorize speculative generalization of TURNLOCK product
semantics.

## Consequences

* ADR-017's `repository-owned validation, rendering, tests, and CI enforcement`
  requirement now means repository-governed adoption and enforcement, not
  mandatory repository-local ownership of reusable implementation bytes.
* TURNLOCK may consume pinned proto-ring governance tooling once parity is
  established.
* TURNLOCK-specific profiles, overlays, decisions, evidence, generated outputs,
  and semantic authority remain in this repository.
* Shared tooling upgrades cannot silently change accepted governance semantics.
* The current ADR tooling remains valid until a separately validated extraction
  replaces it.
* No current formal-assurance artifact or TURNLOCK product invariant changes as
  a consequence of this decision.

## Alternatives considered

### Keep all governance implementation duplicated per repository

Rejected. It preserves local code ownership at the cost of systematic drift and
duplicated strengthening work for rules that are intentionally shared.

### Move repository authority into proto-ring

Rejected. Shared implementation is not a reason to centralize product meaning,
decision history, local evidence, or repository-specific governance facts.

### Consume mutable proto-ring `main`

Rejected. Mutable external state would become ambient validation authority and
would make historical repository validation semantics non-reproducible.

### Specify the complete Ring product before factorization

Rejected. The current need is narrower: factor governance already demonstrated
to be shared. Future Ring scope must continue to be derived from concrete
problems rather than assumed here.

## Verification obligation

Before TURNLOCK removes any local implementation in favor of proto-ring, the
repository must demonstrate that:

1. the consumed shared implementation is pinned to an immutable identity;
2. TURNLOCK-owned profiles, overlays, authority bindings, evidence, and
   generated outputs remain local;
3. the shared implementation validates the same accepted ADR corpus and local
   constraints without semantic weakening;
4. repository-specific validation can extend the shared mechanism without
   redefining its generic contract;
5. generated projections remain reproducible from TURNLOCK-owned canonical
   sources;
6. validation does not consult mutable provider state; and
7. the canonical repository-integrity suite passes after the replacement.
