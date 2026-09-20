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
- Apply
  `docs/repository-governance/turnlock-rust-projection-integrity.md` whenever you
  add or modify a statement containing mechanically derivable mutable repository
  state.
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
3. `formal/verification.yaml` is the canonical machine-readable
   formal-assurance and traceability graph. It owns normative provenance,
   required assurance claims, assurance domains and modalities, formal
   coverage, residual assurance, domain bindings, review requirements, and
   evidence contracts. It is not product semantics, not canonical formal
   semantics, and not verification evidence.
4. An accepted canonical formal semantic representation under `formal/`
   (initially the integrated TLA+ semantics after Gate B) defines the checked
   abstract mathematical semantics for its declared domain and scope. It is
   not normative product authority.
5. `formal/reviews/` records durable hostile semantic-review evidence for exact
   reviewed artifacts. It is not mathematical proof of natural-language to
   formal equivalence.
6. Records under `formal/results/` are concrete mechanism-specific bounded
   verification evidence, authoritative only for the exact runs they identify.
7. Generated mappings, generated indexes, README files, and other explanatory
   projections do not create product semantics, formal-verification claims, or
   independent mutable repository state. Mutable derived repository facts in
   those artifacts must follow
   `docs/repository-governance/turnlock-rust-projection-integrity.md`.
8. `docs/specification/terminology-inventory.yaml` records reviewed lexical
   candidates and fingerprints only. It is not a glossary or semantic authority;
   Section 2 of the normative specification owns canonical terminology.
9. `docs/repository-governance/turnlock-rust-discovery-classification.md`
   binds the shared procedural classification of material discoveries to this
   repository; it creates no product semantics, accepted decision, or
   formal-verification evidence.
10. `docs/vision/turnlock-vision.md` explains non-normative motivation and
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
└── scripts/                        # repository validation tooling and tests
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
- Treat GitHub Issue state, Turnlock-Rust Engineering fields, and native GitHub
  relationships as the single live authority for work state. Reference them
  from Issue prose; do not mirror mutable work state in Issue bodies. Apply the
  detailed policy in
  `docs/repository-governance/turnlock-rust-engineering.md`.
- Treat Project `Priority` as live portfolio-relative scheduling state. After a
  material work-graph change, including creation of a durable Issue, revalidate
  `Priority` across every open Turnlock-Rust Engineering Issue under
  `docs/repository-governance/turnlock-rust-engineering.md`. For autonomous
  pickup, select the highest-priority `Ready` Issue; `Priority` does not
  replace dependencies or readiness.
- Revalidate every Issue and finding against current authoritative repository
  sources before implementation.
- Never use a Project status transition or Issue closure as a substitute for
  repository validation or formal evidence.

## Architectural invariants

### Architectural center and product boundary

- Do not model TURNLOCK as an agent-centric orchestration framework. Keep the
  workflow program at the architectural center for declared orchestration.
- Treat mechanical execution, raw LLM inference, independent agents, and the
  existing main agent as semantically distinct execution resources available to
  the workflow, not as interchangeable agent calls.
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
- Keep mechanical work outside agent interpretation without treating mechanical
  execution as a guarantee of deterministic outputs or traces.
- Keep probabilistic, nondeterministic, externally dependent, and event-driven
  results under workflow-owned control; those results may select only among
  continuations permitted by executable workflow semantics.

### Control handoff and composition

- Preserve reversible and repeatable handoffs to the originating main agent.
- Preserve the enclosing workflow and a well-defined continuation outside agent
  memory.
- Return nested workflow invocations to their immediate caller without
  rewriting outer continuation state.
- Preserve the distinct semantics of mechanical execution, bounded raw LLM
  inference, bounded independent-agent execution, and main-agent continuation.
- Keep workflow-owned fan-out, fan-in, branch lifecycle, and join semantics
  explicit.

### Authoring and harness boundaries

- Expose the same workflow artifact model and public primitives to developers
  and coding agents.
- Keep semantic contracts independent of any one coding harness.
- Treat Pi integration as a reference conformance surface, not as the definition
  of TURNLOCK concepts.
- Design TURNLOCK as an augmentation layer over coding-agent harnesses, not as a
  bet on current harness limitations. Under ADR-038, treat semantically
  compatible native harness capabilities as candidate realization assets;
  never allow those mechanisms to redefine TURNLOCK semantics.
- Apply the Perfect Harness Test to architectural and implementation proposals:
  assume the supported harness already provides an excellent native version of
  the underlying mechanism. If the proposal's TURNLOCK-specific value then
  disappears and no independent semantic, conformance, harness-independent
  meaning, or accepted evidence responsibility remains, treat the mechanism as
  an integration or realization concern unless separate accepted authority
  requires otherwise.
- Do not freeze topics that the normative specification explicitly leaves open.

### Generalization and future abstraction boundaries

- Apply ADR-040 when introducing or changing semantic representations,
  metamodels, IRs, ASTs, schemas, formal abstraction boundaries, or architecture
  that encodes TURNLOCK concepts.
- Keep TURNLOCK concrete and TURNLOCK-specific where its accepted semantics
  require that precision. Never weaken, merge, erase, or rename a necessary
  TURNLOCK distinction merely to make it look reusable by a future higher-level
  model.
- Preserve the ability to distinguish, when relevant, between concepts that are
  intrinsically TURNLOCK-specific, concepts that may generalize to software
  problem solving, and concepts that may generalize beyond software to general
  problem solving.
- Treat the long-term abstraction direction as:
  `TURNLOCK -> software problem-solving representation -> SCOPE general
  problem-solving representation`.
- Discover generalization bottom-up from concrete domains, formalization,
  counterexamples, and recurring structure. Do not treat the presence of a
  concept in TURNLOCK as proof that it is a universal problem-solving primitive.
- Do not introduce speculative generic nodes, universal cognitive operations,
  generic problem graphs, a software problem-solving IR, a SCOPE IR, or another
  higher-level abstraction into this repository merely to anticipate future
  reuse. Such artifacts require separately scoped work and sufficient evidence.
- Where two representation or architecture choices preserve current TURNLOCK
  semantics equally well, prefer the one that avoids unnecessary entanglement
  between TURNLOCK-specific assumptions and potentially extractable semantic
  dimensions. This preference never overrides correctness, semantic precision,
  accepted authority, or a simpler representation of the current contract.
- Treat formal-model pressure, model-checking counterexamples, and verification
  structure as possible evidence for later abstraction work, not as authority
  to promote a TURNLOCK modeling convenience into a software-general or
  problem-solving-general concept.
- A future higher-level software problem-solving or SCOPE representation does
  not become TURNLOCK semantic authority automatically. TURNLOCK authority
  remains governed by the normative specification and accepted TURNLOCK
  decisions unless a later explicit governance decision changes that boundary.

## Formal-verification rules

- Preserve published `TL-INV-NNN` identities. Supersede or migrate an identity
  explicitly rather than silently reusing it.
- Keep `formal/verification.yaml` as the canonical machine-readable
  formal-assurance and traceability graph. It owns normative provenance,
  required assurance claims, assurance domains and modalities, formal coverage,
  residual assurance, formal-semantic domain bindings, review requirements,
  future backend realizations, verification-profile relations, evidence
  contracts, and reverse traceability. It must not define product semantics,
  canonical formal semantics, a semantic IR, verification results, or
  hostile-review results.
- Preserve the assurance distinctions explicitly: `assurance decomposition`,
  `formalization`, `formal semantic projection`, `independent formalization`,
  `verification restriction / instantiation`, `repository projection`, and
  `verification execution`.
- Keep formalization and formal semantic projection distinct. Formalization maps
  normative natural-language semantics to a formal representation. A formal
  semantic projection relates two formal semantic representations and is
  claim-relative or observation-relative.
- Do not invent executable TLA+ identifiers before the model contains them.
- Require claim/property correspondence to be established by reviewed
  correspondence rather than by manifest proximity.
- Do not hand-edit `docs/formal/invariant-mapping.md`; regenerate it from
  `formal/verification.yaml`.
- Never interpret an assurance claim or a planned mapping as a successful
  verification run. Require matching bounded evidence records for a concrete
  revision, exact executed artifact identity, configuration, tool version,
  checked properties, claim or invariant IDs, and outcome before lifting any
  evidence.
- Keep hostile semantic-review evidence separate from mechanical checker
  evidence. A surviving valid material objection blocks acceptance regardless of
  reviewer majority. Hostile review is bounded reviewed semantic correspondence,
  never mathematical proof.
- A hostile-review record does not satisfy a review gate merely by existing.
  Gate-specific required attack objectives and minimum reviewer count are
  declared in `formal/verification.yaml` and are mechanically enforced.
- Any surviving material `open`, `routed`, or `resolved` finding from any
  current review of the same reviewed subject blocks the relevant gate
  regardless of other clean reviews or reviewer majority. Malformed or
  referentially invalid review evidence is an integrity failure and forces the
  relevant gate BLOCKED rather than merely failing repository integrity while
  displaying a READY gate.
- "independent reviewers" means operationally independent executions, not merely
  distinct reviewer records;
- distinct (provider, model, model_version) identities count toward
  minimum_independent_reviewers;
- same model identity repeated does not increase the independent reviewer count;
- provider diversity is recommended but not a universal mechanical requirement;
- qualifying Gate A executions must use the same exact packet and prompt and must
  each cover all required assurance-decomposition attack objectives;
- raw outputs are immutable after sealing and content-addressed;
- every declared raw finding must map exactly once into the normalized finding
  ledger;
- materiality is derived from explicit impact axes, never stored as an
  independent boolean;
- current material open/routed/resolved findings block Gate A;
- material refutations require structured evidence and a sealed hostile
  challenge;
- invalid hostile-review evidence makes the gate BLOCKED;
- a real material correction changes the subject and requires a new current
  review campaign rather than patching old evidence.
- A Gate A review packet is not trusted merely because its artifact SHA matches.
- Gate A packets are canonical JSON self-contained representations of the exact
  reviewed derived subject and its textual authority.
- Recompute the packet subject SHA from subject_payload and recompute authority
  hashes from embedded UTF-8 content.
- The packet subject must be one of the review record's exact subjects.
- Never validate stale packet semantics by comparing them to current repository
  authority; stale packets remain self-contained historical evidence.
- Every non-null hostile challenge is bound to the exact canonical refutation
  subject by challenged_refutation_sha256.
- Changing the finding/refutation content invalidates its previous challenge.
- Review evidence artifacts must never traverse symlinks, including
  in-repository symlink aliases.
- A Gate A assurance-decomposition review record that declares a Gate A derived
  subject MUST declare exactly one such subject.
- Duplicate identical Gate A derived subjects are invalid evidence; never
  deduplicate them.
- Multiple distinct Gate A derived subjects are invalid evidence; never choose
  first, last, packet-selected, or current-selected precedence.
- Additional artifact subjects may coexist with the unique Gate A derived subject.
- Gate A packet binding and Gate A currentness MUST use the same unique Gate A
  derived subject identity.
- `formal_realizations` may be introduced after Gate A when real formal
  identifiers exist; their presence alone does not imply Gate B or Gate C.
- Hostile-review evidence MUST be invalidated according to its declared semantic
  subject dependencies, not merely because another unrelated field in the same
  physical file changed.
- The Gate A assurance-decomposition review subject is the derived
  `gate-a-assurance-decomposition-v1` subject. Do not use the raw hash of all
  `formal/verification.yaml` as Gate A review identity. `formal_realizations` are
  outside Gate A's assurance-decomposition subject.
- A change to normative authority, claims, normative provenance, coverage, or the
  relevant formal-assurance context invalidates the Gate A subject.
- Derived semantic review subjects MUST canonicalize collections whose ordering
  has no declared semantics before hashing. Do not invalidate hostile-review
  evidence because of a pure representation-order change. `formal_semantic_domains`
  is canonicalized by domain `id`; `behavioral_modalities` and `assurance_domains`
  are canonicalized lexicographically. Content changes remain
  fingerprint-significant.
- `policy.formal_semantic_domains[*].id` MUST be unique. Do not resolve duplicate
  formal semantic domain IDs by declaration order, last-write-wins behavior,
  secondary sorting, module name, or path. Duplicate domain IDs are an integrity
  error and prevent derived review-subject construction.
- Gate A currentness requires BOTH the exact derived semantic subject `S` and the
  exact current content-addressed hostile-review protocol bundle `P` declared by
  `policy.hostile_review.current_protocol_bundle`.
- A hostile-review protocol change MUST NOT change the Gate A semantic subject.
  `current_protocol_bundle` and hostile-review policy are outside `S`.
- Reviewer executions MUST resolve a protocol-owned reviewer profile with
  `frontier_eligible == true`; never invent or auto-promote a profile.
- Model version identity MUST be evidence-derived: `provider-reported` requires
  a non-empty qualified attempt `provider_model`; `pinned-request-model`
  requires `request_model_is_immutable_version == true` and the profile
  `request_model`. Never accept a runner-supplied alias, `latest`, or an
  unresolved alias.
- Independent reviewer counting MUST satisfy both the full
  `(provider, model, model_version)` tuple minimum and the effective
  `(provider, model_version)` tuple minimum. Aliases MUST NOT inflate the count.
- Initial hostile reviewer raw outputs MUST be structured JSON under
  `formal/reviews/raw/*.json` and MUST assess all 14 Gate A objectives exactly
  once with reciprocal objective/finding references.
- Every completed cognitive LLM call MUST have a content-addressed execution
  receipt under `formal/reviews/executions/*.json`; every completed response MUST
  be sealed even when protocol-invalid; at most one attempt per receipt may be
  `qualified`; a valid semantic result MUST NOT be retried and no model-shopping
  is permitted.
- Published versioned hostile-review protocol bundles and every prompt/schema
  they reference are append-only and must not be edited or deleted; protocol
  evolution creates a new bundle/path and links the previous bundle through
  `predecessor`.
- A completed response's protocol validity is derived by the checker, not trusted
  from the runner's outcome label. The first protocol-valid completed response is
  terminal and must be the final attempt; technical-failure means no completed
  response/raw output.
- Materiality/refutation challenges require a canonical challenge packet whose
  exact bytes are the receipt `input.packet`; each embeds the exact reviewed Gate
  A packet and exact challenged candidate.
- Normalization MUST be exactly one raw finding to exactly one normalized
  finding; normalized `statement`, `argument`, and `counterexample` MUST equal
  the raw finding values exactly.
- A non-material conclusion MUST carry a valid zero-objection hostile materiality
  challenge bound to the exact candidate assessment. A material finding MUST NOT
  carry a materiality challenge.
- Challenge outputs MUST be derived from objections; `objections == []` is the
  only no-surviving-challenge representation. Never add a free pass/fail,
  `surviving_material_argument`, or `challenger_execution_id` verdict, and never
  add incidental findings to challenge output v1.
- Every stale-protocol finding whose semantic subject is the current `S` MUST
  have a current-protocol re-adjudication before it can cease affecting Gate A.
  A protocol change MUST NOT erase a finding; an old non-material conclusion or
  old refutation is not sufficient under the new protocol.
- Failure to establish a valid refutation MUST NOT be treated as proof that the
  finding is true. Use `OPERATOR-ACTION-REQUIRED` when no valid refutation,
  uniquely derived correction, no-normative-impact, genuine underdetermination,
  or genuine authority conflict can be established; reserve `DECISION-REQUIRED`
  for genuine product-semantic underdetermination or genuine unresolved
  product-authority conflict.
- Keep safety, reachability, liveness, conformance, semantic-quality, and
  architectural claims structurally distinct.
- Route a finding by its earliest unresolved cause rather than by the tool that
  detected it. Never repair a downstream layer while a surviving upstream
  semantic finding remains unresolved.
- Enforce the staged readiness gates:
  Gate A authorizes candidate formal-model authoring.
  Gate B authorizes canonical formal-semantic promotion.
  Gate C authorizes verification-evidence lifting.
- No executable formal model may appear while Gate A prerequisites remain
  unsatisfied. Derive readiness from repository artifacts and review evidence
  rather than storing it as mutable manifest status.
- Use focused configurations for diagnosis and fast feedback only. They never
  replace integrated exploration of the shared canonical semantics.
- Preserve integrated semantic interaction closure once the model exists;
  focused analyses are restrictions of the shared canonical semantics with
  explicit finite bounds.

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
- Prefer reference over duplication for mutable derived repository facts.
- Keep generated projections clearly identified and derived from their
  canonical source.
- When a maintained narrative must duplicate mechanically derivable fields,
  validate those fields mechanically.
- Never rely on agent diligence alone to synchronize a mutable projection.
- Historical snapshots must identify immutable historical scope.
- Keep repository process under `docs/repository-governance/`, separate from
  product semantics and formal evidence.
- Write agent directives and public documentation in English.

## Implementation authorization boundary

Do not infer implementation structure or mechanism from the repository name.

Rust, Cargo, runtime, API, packaging, release, persistence, protocol, scheduler,
adapter, or similar implementation artifacts/rules may be introduced only when
current repository authority establishes the corresponding responsibility and
boundary.

Use the repository tree to determine actual artifact presence. Use accepted ADRs
and the normative repository authority to determine accepted architectural or
implementation commitments. Use `formal/verification.yaml` for the
formal-assurance graph, `formal/reviews/` for hostile-review evidence, and
`formal/results/` for bounded mechanical verification evidence; derive readiness
from the formal traceability checker rather than from stored status.

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

After every intentional repository change, run the canonical validation suite:

```bash
.venv/bin/python scripts/check-repository-integrity.py
```

`scripts/check-repository-integrity.py` owns the mandatory repository-validation
suite and execution order. Do not duplicate its member commands here or in CI.

Inspect generated differences and confirm they follow directly from canonical
sources. Diagnostic checks are side-effect free; only the explicit render
commands above mutate generated projections.

Do not fabricate Cargo, TLC, implementation-test, packaging, or CI commands
before the corresponding artifacts and supported toolchain are introduced.
When they are introduced, update this validation contract in the same accepted
change.

## Quick navigation

- Repository overview: `README.md`
- Non-normative architectural vision: `docs/vision/turnlock-vision.md`
- Normative product specification: `docs/specification/turnlock-spec.md`
- Non-authoritative terminology review inventory:
  `docs/specification/terminology-inventory.yaml`
- Annotated decision history and guide: `docs/adr/README.md`
- ADR metadata profile: `docs/adr/adr-profile.yaml`
- Generated ADR index: `docs/adr/index.md`
- ADR migration evidence: `docs/adr/metadata-migration-evidence.yaml`
- ADR metadata validator and renderer: `scripts/adr-metadata.py`
- Canonical repository-integrity suite:
  `scripts/check-repository-integrity.py`
- Formal-verification policy: `docs/formal/README.md`
- Formal workspace guidance: `formal/README.md`
- Formal-assurance graph: `formal/verification.yaml`
- Formal-assurance schema: `formal/verification.schema.json`
- Generated invariant mapping: `docs/formal/invariant-mapping.md`
- Hostile-review evidence contract: `formal/reviews/README.md`
- Legacy property migration audit:
  `formal/migrations/verification-v2-to-v3-property-audit.yaml`
- TLC result schema: `formal/tlc-result.schema.json`
- Python tooling dependency: `requirements.txt`
- Discovery classification profile:
  `docs/repository-governance/turnlock-rust-discovery-classification.md`
- Projection-integrity policy:
  `docs/repository-governance/turnlock-rust-projection-integrity.md`
- Engineering Project profile:
  `docs/repository-governance/turnlock-rust-engineering.md`
