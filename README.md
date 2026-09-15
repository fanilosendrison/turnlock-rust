# TURNLOCK

## A runtime for programs that call cognition

TURNLOCK is a runtime for executable workflows that compose mechanical
execution and cognition inside an existing interactive coding-agent session.
A workflow program owns its declared control flow; TURNLOCK executes,
coordinates, and tracks that control flow. A completed execution remains
sufficiently inspectable at TURNLOCK's semantic boundary for user- or system-led
evaluation and iterative workflow refinement. Effective execution conditions
that TURNLOCK selects, binds, explicitly supplies, or resolves remain
attributable to the execution scopes they govern and capturable at that boundary
without creating a persistence, replay, reproducibility, or comparison
guarantee. Cognition is an explicit execution resource rather than the implicit
global scheduler.

A workflow may compose four distinct execution forms:

```text
mechanical execution
bounded raw LLM inference
bounded independent agents
continuation of the user's existing main coding agent
```

Mechanical execution means progression governed by executable workflow
semantics rather than missing agent-supplied orchestration decisions. It does
not imply deterministic outputs, paths, traces, or replay.

The fourth form is product-defining. TURNLOCK can temporarily return local
control to the same main coding agent and later resume workflow-owned
progression. That continuation preserves the living interactive lineage rather
than silently replacing it with a generic model call or fresh agent.

The motivating long-term thesis is that processes such as software production
can become executable programs that call cognition where judgment is required,
instead of procedures that a main coding agent must remember and orchestrate
from prose. TURNLOCK does not prescribe those processes. Their policy,
methodology, and topology belong in workflow programs and higher-level systems
above the runtime.

```text
policy / intent / methodology / generated strategy
                    ↓
             workflow program
                    ↓
                 TURNLOCK
                    ↓
    computation and distinct forms of cognition
```

Read the non-normative [architectural vision](docs/vision/turnlock-vision.md)
for the full product thesis. Normative product meaning remains in the
[TURNLOCK specification](docs/specification/turnlock-spec.md), with decision
history in the [annotated ADR history](docs/adr/README.md).

## Repository status

This repository is currently a specification, architecture, and
formal-verification package that intentionally precedes implementation. It
contains the normative product contract, accepted architectural decisions, and
formal traceability for the planned model.

It does **not** yet contain a Rust crate, Cargo manifest, runtime source tree,
fixed workflow-authoring syntax, executable TLA+ model, TLC configuration, or
successful TLC result. No concrete runtime, persistence, protocol, scheduler,
or adapter architecture has been selected.

Pi is the first reference harness, while TURNLOCK workflow semantics remain
harness-independent. Pi will be used to prove the coding-session lifecycle end
to end; Pi-specific mechanisms do not define TURNLOCK concepts.

## Contents

- [Repository directives](AGENTS.md) define authority boundaries and guardrails
  for coding agents.
- [Architectural vision](docs/vision/turnlock-vision.md) explains the
  non-normative long-term thesis and motivation.
- [Future workflow run-evaluation design space](docs/vision/future-workflow-run-evaluation.md)
  preserves an explicitly non-normative exploration of stronger observability,
  comparability, reproducibility, and execution-evidence profiles beyond the
  accepted minimum inspectability obligation, effective execution-condition
  provenance floor, and evaluation/optimization-policy boundary.
- [Repository governance](docs/repository-governance/turnlock-rust-engineering.md)
  defines GitHub Engineering Project routing and workflow policy.
- [Discovery classification profile](docs/repository-governance/turnlock-rust-discovery-classification.md)
  binds the shared engineering-discovery process to Turnlock-Rust authority,
  artifacts, and validation.
- [Normative specification](docs/specification/turnlock-spec.md) defines product
  intent, canonical terminology, promises, invariants, boundaries, and
  architectural implications.
- [Terminology review inventory](docs/specification/terminology-inventory.yaml)
  records non-authoritative locations and fingerprints for reviewed
  definition-like occurrences.
- [Annotated ADR history](docs/adr/README.md) provides the maintained
  chronological decision narrative and links to ADR-001 through ADR-024.
- [Generated ADR index](docs/adr/index.md) projects canonical status and
  outgoing/incoming relations mechanically.
- [ADR metadata profile](docs/adr/adr-profile.yaml) pins the generalized OKF ADR
  schema, TURNLOCK's local overlay, migration evidence, and validation commands.
- [Formal-verification policy](docs/formal/README.md) explains the relationship
  between normative prose, formal intent, executable models, and evidence.
- [Formal traceability manifest](formal/verification.yaml) records
  machine-readable forward and reverse traceability and intended verification
  coverage.
- [Generated invariant mapping](docs/formal/invariant-mapping.md) projects the
  manifest into a human-readable view.
- [Formal workspace](formal/README.md) records the planned model layout and its
  current status.
- [ADR metadata tool](scripts/adr-metadata.py) validates ADR identity,
  provenance, lifecycle metadata, outgoing relations, body integrity, and
  generated projections.
- [Traceability checker](scripts/check-formal-traceability.py) validates
  invariant IDs, ADR references, manifest statuses, and generated mapping
  freshness.
- [Terminology governance checker](scripts/check-normative-terminology.py)
  validates canonical anchors and review-inventory freshness while reporting
  only heuristic, not semantic, detection of competing definitions.
- [Terminology checker tests](scripts/tests/test-normative-terminology.py) cover
  structural drift, stale inventory, and likely competing definitions.
- [Mapping renderer](scripts/render-formal-mapping.py) regenerates the
  human-readable mapping from the manifest.
- [Pinned tooling dependencies](requirements.txt) support ADR metadata and
  formal traceability validation.

## Architectural snapshot

The workflow program is the architectural center for declared orchestration:

```text
workflow program = declared orchestration decisions and topology
TURNLOCK = runtime authority that executes the declared orchestration
```

TURNLOCK executes orchestration; it does not invent undeclared global strategy.
A developer or coding agent may author the workflow, but either path produces
the same class of workflow artifact and does not transfer runtime ownership to
the authoring agent.

The execution forms remain semantically distinct:

```text
mechanical execution = executable, non-agent-mediated progression
raw LLM inference = one declared non-agentic semantic operation with a result boundary
independent agent = workflow-declared local autonomy in a fresh cognitive lineage
main agent = continuation of the existing interactive cognitive lineage
```

The guiding allocation rule is to use the minimum sufficient form of
computation or cognition for each workflow region. Here, boundedness identifies
semantic, structural, context, and local-authority boundaries; it does not by
itself impose finite resources or guarantee termination. Known orchestration
remains in executable workflow logic even when runtime results are probabilistic,
nondeterministic, externally dependent, or produced by locally autonomous
cognition. Completed workflow execution must expose enough actual
TURNLOCK-visible behavior for external understanding and evaluation. Effective
conditions TURNLOCK selects, binds, explicitly supplies, or resolves remain
attributable to their governed execution scopes and capturable at its semantic
boundary. This does not impose persistence or make TURNLOCK the evaluator or
optimizer. Evaluation objectives, property-relative relevance, comparison
judgments, and optimization policy come from an explicitly responsible actor or
authored workflow, never from core TURNLOCK runtime policy.

## Formal verification organization

```text
docs/specification/turnlock-spec.md   normative meaning
docs/adr/                             decision history
formal/verification.yaml              intended forward/reverse traceability graph
docs/formal/invariant-mapping.md      generated human-readable mapping
formal/Turnlock.tla                   executable abstract model (not yet present)
formal/models/focused/                planned targeted TLC exploration
formal/models/integrated/             planned integrated exploration profiles
formal/tlc-result.schema.json         schema for actual TLC run evidence
formal/results/                       actual run evidence, once TLC runs exist
```

[ADR-015](docs/adr/adr-015-evolve-the-normative-and-formal-specifications-together.md)
requires normative and formal specifications to evolve together. The manifest
records intended traceability; it is not proof that model checking occurred.
Actual TLC evidence remains separate under `formal/results/`, and focused
exploration never substitutes for integrated exploration of the shared model.

Because the executable TLA+ model has not yet been introduced, the repository
makes no `checked` formal-verification claim.
