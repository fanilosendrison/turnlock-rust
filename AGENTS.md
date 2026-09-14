---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "turnlock-rust"
severity: "strict"
name: "Turnlock-Rust repository agent directives"
---

# Turnlock-Rust repository directives

Use this file as the operational map for the Turnlock-Rust repository. Apply it
with all parent workspace instructions. Never duplicate, weaken, or override a
parent permission, security, formatting, naming, or implementation rule.

## General guidelines

- Treat this repository as a normative specification and formal-verification
  corpus that precedes implementation.
- Do not infer a Rust crate layout, runtime mechanism, persistence model, public
  API, or release process from the repository name.
- Derive implementation choices from product intent and accepted invariants,
  not from an existing TURNLOCK implementation or another project.
- Keep workflow semantics harness-independent. Pi is the first reference
  integration, not the semantic authority.
- Keep the repository root limited to system entry points and
  responsibility-based directories.
- Use lowercase kebab-case for new files and directories, except recognized
  system entry points such as `AGENTS.md` and `README.md`.
- Apply the shared `engineering-discovery-classification` skill, then read
  `docs/repository-governance/turnlock-rust-discovery-classification.md`, before
  incorporating any material discovery into normative, formal, architectural,
  implementation, or harness-conformance artifacts.
- When the user mentions an Issue, Project work, backlog work, or a review
  finding, apply the shared GitHub Engineering Projects operational protocol,
  then read
  `docs/repository-governance/turnlock-rust-engineering.md` before acting.

## Authority by responsibility

Use each source only for the responsibility it owns:

1. `docs/specification/turnlock-spec.md` defines normative product meaning and
   the stable `TL-INV-NNN` invariants.
2. Accepted ADRs under `docs/adr/` record decision history and later
   amendments.
3. `formal/verification.yaml` defines intended formal traceability and coverage;
   it is not verification evidence.
4. The future executable model under `formal/` will define the checked abstract
   formulas for its declared scope without replacing normative prose.
5. Records under `formal/results/` are authoritative only for the bounded TLC
   runs they identify.
6. Generated mappings, generated ADR indexes, and README files explain or
   project authoritative sources; they do not create product semantics or
   verification claims.
7. `docs/repository-governance/turnlock-rust-discovery-classification.md`
   binds the shared procedural classification of material discoveries to this
   repository; it creates no product semantics, accepted decision, or
   formal-verification evidence.
8. `docs/vision/turnlock-vision.md` explains non-normative motivation and
   long-term direction; it never overrides the specification, ADRs, or formal
   governance.

Report every inconsistency between authoritative sources. Do not silently select
a convenient interpretation. Resolve a semantic conflict through an explicit
new ADR and synchronized normative and formal artifacts.

ADR frontmatter is canonical for ADR identity, lifecycle, explicitly recorded
outgoing relations, governed scope, and body integrity. `docs/adr/adr-profile.yaml`
and its schemas govern that representation; they do not create product semantics
or outrank accepted decision bodies.

Repository-governance documents govern repository procedures and work
management. GitHub Issues, Project fields, comments, discussions, and Pull
Requests manage work. None of these sources overrides product semantics or
constitutes formal-verification evidence.

## Required reading

Before changing product semantics, architecture, formalization, or preparing
implementation work, read:

1. `README.md`
2. `docs/specification/turnlock-spec.md`
3. `docs/adr/README.md`
4. The ADRs governing the affected concepts
5. `docs/formal/README.md`
6. `formal/README.md`
7. `formal/verification.yaml`

Read the executable model, configurations, and result evidence once those
artifacts exist and the requested work affects them.

## Folder structure

```text
turnlock-rust/
├── AGENTS.md
├── README.md
├── docs/
│   ├── adr/
│   │   └── schemas/
│   ├── formal/
│   ├── repository-governance/
│   ├── specification/
│   └── vision/
├── formal/
│   ├── models/
│   │   ├── focused/
│   │   └── integrated/
│   ├── results/
│   ├── tlc-result.schema.json
│   └── verification.yaml
└── scripts/
    └── tests/
```

Do not create speculative implementation directories or manifests before an
accepted decision establishes their responsibilities and ecosystem boundaries.

## Engineering work tracking

- Apply the shared GitHub Engineering Projects operational protocol for generic
  Issue and Project operations.
- Use
  `docs/repository-governance/turnlock-rust-engineering.md` only for this
  repository's Project coordinates, fields, views, and workflow policy.
- Resolve an unqualified `Issue #N` as
  `fanilosendrison/turnlock-rust#N`.
- Track durable future work in Turnlock-Rust Engineering and its associated
  GitHub Issues.
- Revalidate every Issue and finding against current authoritative repository
  sources before implementation.
- Never use a Project status transition or Issue closure as a substitute for
  repository validation or formal evidence.

## Architectural invariants

### Architectural center and product boundary

- Do not model TURNLOCK as an agent-centric orchestration framework. Keep the
  workflow program at the architectural center for declared orchestration.
- Treat deterministic computation, raw LLM inference, independent agents, and
  the existing main agent as semantically distinct execution resources
  available to the workflow, not as interchangeable agent calls.
- Keep known control-flow decisions in executable workflow logic. Do not move
  them back into main-agent judgment merely because a harness makes that
  convenient.
- Keep TURNLOCK below policy, methodology, and domain-specific workflows. Do
  not add core concepts such as feature, bug-fix, review, security, or migration
  workflows; higher-level systems define those topologies above TURNLOCK.
- Preserve the existing interactive coding-agent session as a product-defining,
  first-class resumable cognitive resource rather than treating session
  continuity as incidental UX.
- Never present a generic LLM call, newly spawned agent, or reconstructed fresh
  agent as main-agent continuation. Equivalent continuation must preserve the
  existing cognitive lineage under the normative contract.
- Enforce `TL-INV-032`: keep workflow authorship separate from execution
  ownership. A coding agent or other LLM may author a workflow without becoming
  the owner or scheduler of that workflow's execution.

### Orchestration ownership

- Keep declared orchestration decisions and topology in the workflow program.
- Keep TURNLOCK responsible for executing, coordinating, and tracking declared
  orchestration without inventing global strategy.
- Keep deterministic mechanical work outside agent interpretation.
- Keep probabilistic execution forms as bounded leaves under deterministic
  workflow control.

### Control handoff and composition

- Preserve reversible and repeatable handoffs to the originating main agent.
- Preserve the enclosing workflow and a well-defined continuation outside agent
  memory.
- Return nested workflow invocations to their immediate caller without
  rewriting outer continuation state.
- Preserve the distinct semantics of deterministic computation, bounded raw LLM
  inference, bounded independent-agent execution, and main-agent continuation.
- Keep workflow-owned fan-out, fan-in, branch lifecycle, and join semantics
  explicit.

### Authoring and harness boundaries

- Expose the same workflow artifact model and public primitives to developers
  and coding agents.
- Keep semantic contracts independent of any one coding harness.
- Treat Pi integration as a reference conformance surface, not as the definition
  of TURNLOCK concepts.
- Do not freeze topics that the normative specification explicitly leaves open.

## Formal-verification rules

- Preserve published `TL-INV-NNN` identities. Supersede or migrate an identity
  explicitly rather than silently reusing it.
- Keep `formal/verification.yaml` mechanically invertible from prose invariants
  to TLA+ properties, state variables, actions, configurations, and evidence.
- Do not invent executable TLA+ identifiers before the model contains them.
- Do not hand-edit `docs/formal/invariant-mapping.md`; regenerate it from
  `formal/verification.yaml`.
- Never interpret a planned mapping as a successful verification run.
- Require matching result records for a concrete revision, configuration, tool
  version, finite bounds, checked properties, invariant IDs, and outcome before
  marking an invariant `checked`.
- Keep safety, liveness, reachability, conformance, and semantic-quality claims
  distinct.
- Use focused configurations for diagnosis and fast feedback only. They never
  replace integrated exploration of the shared model.
- Once the model exists, preserve integrated smoke, standard, and stress
  profiles with explicit finite bounds.

## Architectural decisions and documentation

- Keep ADRs chronological under `docs/adr/` using
  `adr-NNN-lowercase-kebab-title.md` and the pinned contract in
  `docs/adr/adr-profile.yaml`.
- Treat accepted ADR identity, name, date, outgoing relations, governed scope,
  and decision body as immutable. Use a later ADR to amend or supersede an
  accepted decision; derive incoming relations instead of editing old records.
- Permit a representation/schema migration only through a later governance ADR
  and machine-readable body-preservation evidence.
- Keep `docs/adr/README.md` as the maintained annotated history. Never hand-edit
  the required generated projection at `docs/adr/index.md`.
- Synchronize the normative specification, ADR projections, formal traceability,
  and generated mapping whenever an accepted semantic change affects them.
- Classify every material discovery with the shared
  `engineering-discovery-classification` skill and
  `docs/repository-governance/turnlock-rust-discovery-classification.md` before
  incorporating it into a semantically significant artifact. Never treat
  classification as a substitute for required ADRs, synchronization,
  traceability, review, or validation.
- Keep generated artifacts clearly identified and derived from one canonical
  source.
- Keep repository process under `docs/repository-governance/`, separate from
  product semantics and formal evidence.
- Write agent directives and public documentation in English.

## Current implementation boundary

The repository currently contains no Rust crate, Cargo manifest, production
source tree, executable TLA+ model, TLC configuration, or successful TLC result.
Do not claim that any of those artifacts exist. Do not add Rust, Cargo, runtime,
API, packaging, or release rules until accepted repository decisions introduce
them.

## Mandatory validation

Create an isolated Python 3 environment and install the pinned tooling
dependency before validation:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --requirement requirements.txt
```

After changing `formal/verification.yaml`, regenerate the human-readable mapping
first:

```bash
.venv/bin/python scripts/render-formal-mapping.py
```

When ADR metadata changes and the repository profile requires its generated
index, regenerate it first:

```bash
.venv/bin/python scripts/adr-metadata.py render
```

After every intentional repository change, run:

```bash
.venv/bin/python scripts/tests/test-adr-metadata.py
.venv/bin/python scripts/adr-metadata.py check
.venv/bin/python scripts/check-formal-traceability.py
git diff --check
```

Inspect generated differences and confirm they follow directly from canonical
sources. The formal traceability checker invokes its renderer and can therefore
update `docs/formal/invariant-mapping.md`.

Do not fabricate Cargo, TLC, implementation-test, packaging, or CI commands
before the corresponding artifacts and supported toolchain are introduced.
When they are introduced, update this validation contract in the same accepted
change.

## Quick navigation

- Repository overview: `README.md`
- Non-normative architectural vision: `docs/vision/turnlock-vision.md`
- Normative product specification: `docs/specification/turnlock-spec.md`
- Annotated decision history and guide: `docs/adr/README.md`
- ADR metadata profile: `docs/adr/adr-profile.yaml`
- Generated ADR index: `docs/adr/index.md`
- ADR migration evidence: `docs/adr/metadata-migration-evidence.yaml`
- ADR metadata validator and renderer: `scripts/adr-metadata.py`
- Formal-verification policy: `docs/formal/README.md`
- Formal workspace status: `formal/README.md`
- Machine-readable traceability: `formal/verification.yaml`
- Generated invariant mapping: `docs/formal/invariant-mapping.md`
- TLC result schema: `formal/tlc-result.schema.json`
- Python tooling dependency: `requirements.txt`
- Discovery classification profile:
  `docs/repository-governance/turnlock-rust-discovery-classification.md`
- Engineering Project profile:
  `docs/repository-governance/turnlock-rust-engineering.md`
