---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust Projection Integrity binding"
---

# Turnlock-Rust Projection Integrity binding

## Shared contract

Apply the canonical proto-ring Projection Integrity contract at this immutable
identity:

```text
fanilosendrison/proto-ring
ae8d05935553086b68d5d832dc9d3317328f0c89
docs/contracts/projection-integrity.md
```

The Projection Integrity contract is bound to the exact immutable proto-ring
commit above. This contract identity identifies only the governance contract
adopted by Turnlock-Rust.

Turnlock-Rust's executable proto-ring package dependency is pinned independently
to the immutable provider revision required by the shared implementations it
consumes. That package identity identifies the executable shared implementation
being imported. The package dependency pin and this governance-contract
authority pin need not be identical when they govern different responsibilities;
neither pin automatically authorizes or determines the other.

Neither mutable proto-ring state nor an unpinned provider reference is authority
for either binding.

The shared contract owns generic canonical-owner, projection-mode,
direct-source, currentness, validation-ownership, synchronization, and
completion rules. This profile owns only the Turnlock-Rust mappings and local
extensions below.

## Local scope

Apply the shared contract whenever a Turnlock-Rust artifact states mechanically
derivable mutable repository state, including current ADR metadata, governed
artifact presence, formal lifecycle and traceability state, generated mappings,
validation membership, and live engineering work state.

Ordinary explanatory prose and vision documents are not required to receive a
mechanical semantic-equivalence proof. Existing authority and discovery
classification continue to govern semantic paraphrases.

## Turnlock-Rust owner mappings

Use these local bindings:

```text
ADR frontmatter and canonical ADR files
    → own current ADR identity, name, lifecycle status, path, and relations

docs/adr/index.md
    → generated projection from canonical ADR frontmatter

docs/adr/README.md chronological trace
    → mechanically validated maintained projection for derivable ADR fields
    → independently authored narrative remains maintained content

formal/verification.yaml
    → owns formal-model lifecycle, intended formal traceability, and profile state

docs/formal/invariant-mapping.md
    → generated projection from formal/verification.yaml

formal/results/
    → owns concrete bounded execution evidence for each recorded run

repository filesystem and Git tree
    → own current governed artifact presence or absence

accepted ADRs and other declared repository authority
    → own accepted implementation and architecture commitments

AGENTS.md
    → owns repository authorization and execution guardrails

scripts/check-repository-integrity.py
    → owns mandatory repository-validation membership and order

.github/workflows/repository-integrity.yml
    → references the canonical validation entry point and owns CI bootstrap

GitHub Issues, Project fields, and native relationships
    → own current engineering work state
```

README files remain explanatory consumers unless a more specific mapping above
assigns maintained or generated projection responsibility.

## Local extensions

The maintained ADR history must validate every duplicated derivable identity,
name, lifecycle status, path, order, and coverage field directly against
canonical ADR records. Narrative annotations remain independently authored and
are not generated.

Formal readiness projections may be generated only after the complete local
traceability and evidence validation succeeds. A focused checker or partial
traceability result is not a canonical source for those projections.

Generated ADR and formal mappings are produced only through their declared local
render commands. Repository Integrity remains diagnostic and must reject stale
output rather than silently repairing it into a passing state.

Historical migration ranges and sealed formal evidence must retain their exact
revision-, protocol-, subject-, or run-bounded scope. They must not be presented
as current mutable state.

Live engineering work state must be referenced through GitHub's native owners.
Repository prose must not maintain a manual status, classification, dependency,
parentage, or linked-change dashboard.

## Change procedure

For a new or changed Turnlock-Rust projection, apply the shared contract first,
then add or update the concrete owner mapping and local generator or validator in
the same change. Keep product semantics, formal semantics, accepted decisions,
evidence, paths, commands, and Project coordinates local.

Do not duplicate the generic contract in this profile. Do not treat a local
mapping as proto-ring authority. Run the canonical Repository Integrity suite
and refresh every affected generated projection before completing the change.

## Authority boundary

This binding changes repository governance only. It does not change TURNLOCK
product meaning, formal-assurance semantics, hostile-review claims, bounded
verification evidence, accepted ADR content, or the authority order in
`AGENTS.md`.

The separate governed-identity finding remains outside this binding. Projection
Integrity does not resolve identity or canonicalization semantics that current
Turnlock-Rust authority has not accepted.
