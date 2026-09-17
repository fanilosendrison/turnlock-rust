---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust engineering discovery classification profile"
---

# Turnlock-Rust engineering discovery classification profile

Apply the shared `engineering-discovery-classification` skill before using this
profile. This file binds the shared classification mechanics to Turnlock-Rust
authority and artifacts. It creates no TURNLOCK product semantics, accepted
decision, or formal-verification evidence.

## Authority binding

Use the authority order and responsibility boundaries in
[`AGENTS.md`](../../AGENTS.md#authority-by-responsibility). Read the current
sources governing the affected concept; do not copy their meaning into a
discovery record.

Bind the shared layers as follows:

- `normative-contract` maps to
  [`docs/specification/turnlock-spec.md`](../specification/turnlock-spec.md),
  including stable `TL-INV-NNN` identities.
- `decision-history` maps to accepted ADRs under [`docs/adr/`](../adr/) and
  explicit later amendments.
- `formal-model-or-analysis` maps to the intended traceability in
  [`formal/verification.yaml`](../../formal/verification.yaml) and to executable
  models and configurations under `formal/` once they exist.
- `verification-or-qualification-evidence` maps only to scope-bound result
  records under `formal/results/` once valid runs exist. Planned mappings and
  generated projections are not successful verification evidence.
- `architecture-or-implementation` maps to accepted implementation-specific
  decisions and future implementation artifacts. [`AGENTS.md`](../../AGENTS.md)
  owns repository implementation authorization and guardrails; the repository
  tree exposes actual artifact presence; accepted ADRs and the normative
  repository authority own accepted commitments. This profile does not mirror
  any of them.
- `integration-or-conformance` maps to harness capability requirements, adapter
  constraints, support boundaries, and conformance evidence. Pi is a reference
  integration, not semantic authority.
- `repository-governance-or-documentation` maps to procedures under
  `docs/repository-governance/` and explanatory or generated documentation
  without promoting those artifacts into product authority.

## Normative promotion

Classify a discovery as `derived-from-existing-authority` only with a complete
derivation from current normative prose and accepted decisions. Prefer mapping,
formalizing, or clarifying an existing `TL-INV-NNN` when it already entails the
obligation. Create a new invariant identity only when the invariant admission,
ADR amendment, synchronization, and traceability rules establish a distinct
normative obligation.

Classify behavior not uniquely determined by current authority as
`decision-required`. Keep it locked until the repository's accepted ADR process
resolves the semantic choice. A user task, coding-agent recommendation, Issue,
TLA+ assumption, TLC result, implementation preference, or harness capability
does not accept that decision.

Use `authority-conflict-or-uncertain` when the specification and accepted ADRs
disagree or a derivation depends on an unstated product assumption. Resolve a
semantic conflict only through a later ADR plus synchronized normative and
formal artifacts.

## Formal and conformance interpretation

Treat TLA+ and TLC as discovery and verification instruments within their
declared scope:

- do not invent executable identifiers before the model contains them;
- do not treat planned traceability as a checked result;
- do not strengthen product semantics merely to make a property pass;
- do not turn a modeling structure, finite bound, or fairness device into an
  implementation obligation;
- do not weaken TURNLOCK semantics to accommodate a harness limitation.

When a harness cannot preserve accepted semantics, record the exact capability
or conformance limitation and use only the support outcome permitted by current
TURNLOCK authority. Raise any proposed semantic weakening as a separate locked
`decision-required` discovery.

## Durable routing and synchronization

Keep transient discoveries with no durable impact in working notes. Preserve a
discovery in the resulting ADR, Issue, review record, commit, formal artifact,
or implementation artifact when its reasoning must survive the session.

For independently tracked work, apply the shared GitHub Engineering Projects
skill and the
[Turnlock-Rust Engineering profile](turnlock-rust-engineering.md). An Issue
records work and provenance; it does not accept product semantics or establish
verification evidence.

Follow the synchronization, generation, and validation contract in
[`AGENTS.md`](../../AGENTS.md#mandatory-validation) after every repository
change. When a synchronization step adds or updates a mutable derived
projection, apply the
[repository projection-integrity policy](turnlock-rust-projection-integrity.md):
reference, generate, validate, or explicitly snapshot canonical state instead of
manually mirroring it. Classification never substitutes for ADR lifecycle,
stable invariant identity, formal traceability, review, permission, or
validation.
