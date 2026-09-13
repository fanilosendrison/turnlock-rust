---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Adopt validated OKF Architecture Decision Record metadata"
id: "ADR-017"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "633565f0e825c7bda0cd5c33ad19e15323e55055cccb98aacf5924cd48f1b503"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Architecture Decision Record metadata, lifecycle, integrity, and generated projections"
  - "Semantics-preserving migration of accepted TURNLOCK ADR metadata"
  - "Repository-local validation of the adopted OKF ADR profile"
---

# ADR-017: Adopt validated OKF Architecture Decision Record metadata

## Context

TURNLOCK's accepted Architecture Decision Records predate a machine-readable
repository contract for their identity, lifecycle, relationships, governed
scope, and decision-body integrity. Their Markdown headers are readable but do
not provide schema validation, deterministic reverse relationships, or proof
that a repository-wide representation migration preserved accepted decisions.

The repository already treats accepted ADRs as immutable decision history.
Adding structured metadata to ADR-001 through ADR-016 therefore requires an
explicitly authorized migration boundary rather than silent edits to accepted
records. The migration must preserve product meaning, keep the existing
decision bodies byte-for-byte intact, and avoid turning generated projections
into a new source of architecture authority.

A generalized OKF Architecture Decision Record profile now exists outside this
repository. TURNLOCK needs a pinned adoption that remains independently
validatable and that can add repository-specific constraints without silently
forking the shared schema.

## Decision

TURNLOCK adopts version `0.1.0` of the generalized OKF Architecture Decision
Record profile through:

1. a byte-identical vendored copy of the canonical versioned JSON Schema;
2. provenance metadata containing the canonical repository, source path, commit,
   schema `$id`, and SHA-256 digest;
3. a separate TURNLOCK overlay for repository-specific domain and ID rules; and
4. repository-owned validation, rendering, tests, and CI enforcement.

Canonical ADR metadata lives in YAML frontmatter. The H1 and any retained legacy
Markdown metadata remain human-readable presentation and MUST agree where the
repository validator can compare them. During the authorized migration, legacy
status, date, relationship, and scope lines remain unchanged as historical
presentation; they do not remain an independent metadata authority.

`id` is the stable identity from which numeric order, filename agreement, and H1
agreement are derived. Every allocated ID MUST remain retained and MUST NOT be
reused. TURNLOCK continues to require three-digit contiguous IDs and filenames
of the form `adr-NNN-lowercase-kebab-title.md`.

Only outgoing `clarifies`, `amends`, `supersedes`, and `confirms` relationships
are stored in source frontmatter. Incoming relationships are generated
projections. `relation_completeness: complete` means every explicitly asserted
outgoing relationship of that ADR is structurally represented; it does not
claim discovery of every conceptual relationship that a reader might infer
from prose.

For accepted ADRs, the following remain immutable:

- `id`, `name`, and decision date;
- outgoing relationships and governed scope; and
- exact decision-body bytes from the first `## Context` heading through EOF.

The body digest is SHA-256 over those exact UTF-8/LF bytes, including final
newline state. Validators MUST reject BOM and CRLF instead of normalizing them
silently. Lifecycle status may change only through a transition declared in the
repository profile. A later profile/schema migration requires a later governance
decision and equivalent preservation evidence.

This decision authorizes one semantics-neutral migration of ADR-001 through
ADR-016. That migration MAY prepend conforming frontmatter but MUST preserve all
pre-existing bytes, record before/after body digests against the committed
pre-migration baseline, clear the temporary frontmatter compatibility allowlist,
and enable the generated mechanical index. It MUST NOT normalize, remove, or
reinterpret historical prose.

The generated `docs/adr/index.md` is a deterministic projection of canonical
frontmatter. The maintained `docs/adr/README.md` remains the annotated decision
history and repository guide. Neither generated reverse relations nor the README
supersede source ADRs or the normative specification.

This decision changes ADR representation and governance only. It does not alter
TURNLOCK product semantics, formal-verification claims, implementation
architecture, or the authority order between the normative specification,
accepted ADRs, formal traceability, executable models, and run evidence.

## Rationale

A shared profile avoids inventing incompatible ADR metadata for every
repository, while pinning and vendoring avoid runtime dependence on mutable
external state. A local overlay preserves repository autonomy without making a
modified schema look byte-identical to its source.

Outgoing-only relationships remove dual-write inconsistency. Exact body digests
make the accepted-record migration auditable. Keeping the narrative history
separate from the generated index preserves nuance that cannot be reconstructed
safely from heterogeneous historical prose.

## Consequences

- New TURNLOCK ADRs must be valid OKF `KnowledgeAsset` records under both the
  pinned base schema and the TURNLOCK overlay.
- The repository validator becomes the mechanical authority for metadata shape,
  provenance, identity, filenames, H1 titles, body digests, relation targets,
  legacy allowlists, and generated-index freshness.
- ADR-001 through ADR-016 may receive frontmatter only under the preservation
  conditions in this decision.
- Existing Markdown metadata remains visible but non-canonical until a separate
  future decision authorizes its removal or normalization.
- Reverse relationships are reproducible and cannot drift from source records.
- A profile upgrade requires an explicit later ADR and migration evidence.
- Ruu and other repositories require their own adoption decisions, overlays,
  migrations, and validation evidence.

## Alternatives considered

### Keep informal Markdown headers only

Rejected. They do not provide a machine-valid contract, deterministic reverse
relationships, or body-preservation evidence for metadata migrations.

### Adopt MADR or Log4brains as TURNLOCK's canonical authority

Rejected. Their conventions are useful inputs, but TURNLOCK requires an
OKF-governed, repository-enforced profile and independent authority boundaries.
The generalized profile is MADR-inspired rather than a MADR compliance claim.

### Edit the vendored base schema for TURNLOCK-specific rules

Rejected. A modified vendored copy would make provenance ambiguous. A
byte-identical base plus a separate overlay makes shared and local constraints
independently inspectable.

### Replace the annotated README with a generated index

Rejected. The maintained history contains context and qualifications that a
mechanical projection cannot reproduce safely. Generation supplements rather
than destroys it.

### Normalize all historical metadata during the frontmatter migration

Rejected. Conflating representation migration with semantic interpretation
would weaken the proof that accepted decisions remained unchanged.

## Verification obligation

The repository must demonstrate that:

1. the vendored base schema matches the pinned digest and schema `$id`;
2. both base and local schemas validate every structured ADR with calendar-aware
   date checking;
3. invalid months, days, and leap days are rejected by tests;
4. IDs are unique and contiguous, filenames and H1 titles agree with canonical
   metadata, and all relation targets exist without self-reference;
5. null dates and frontmatter-free records are accepted only on exact fixed
   legacy allowlists, with stale entries rejected;
6. every body digest matches the exact bytes from `## Context` through EOF;
7. migration evidence covers ADR-001 through ADR-016 against the committed
   governance baseline; and
8. the generated index is reproducible from canonical frontmatter.
