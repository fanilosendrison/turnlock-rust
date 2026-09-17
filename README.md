# TURNLOCK

## A runtime for programs that call cognition

TURNLOCK is a runtime for executable workflows that compose mechanical
execution and cognition inside an existing interactive coding-agent session.
A workflow program owns its declared control flow; TURNLOCK executes,
coordinates, and tracks that control flow. A completed execution remains
sufficiently inspectable at TURNLOCK's semantic boundary for user- or system-led
evaluation and iterative workflow refinement. Effective execution conditions
that TURNLOCK selects, binds, explicitly supplies, or resolves remain
attributable to the execution scopes they govern and capturable at that
boundary. Protected values need not be disclosed, but protection cannot substitute away
condition-specific provenance TURNLOCK possessed before or during its required
realizable semantic-boundary capture handoff. The handoff is not a retention interval: the universal floor requires a
structurally realizable capture capability and completion of TURNLOCK's side of
the semantic-boundary interaction, but it does not require an actual attached
or participating consumer, successful delivery, acknowledgment, or
post-handoff availability. This
creates no persistence, replay, reproducibility, stable cross-run identity, or
comparison guarantee. Cognition is an explicit execution resource rather than
the implicit global scheduler.

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

As software engineering becomes increasingly agentic, TURNLOCK is intended to
make stable parts of engineering methods executable outside transient agent
cognition. TURNLOCK is one substrate inside a larger engineering system:
higher-level actors remain responsible for intent, methodology, generated
strategy, workflow selection or generation, evaluation objectives, and
optimization policy, while TURNLOCK executes the resulting workflow under
explicit control semantics. This allows improvements in underlying cognition
and improvements in the executable engineering method itself to accumulate
independently, rather than requiring every process improvement to remain encoded
in an agent's prompt, conversational memory, or runtime judgment.

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

TURNLOCK is developed specification-first: normative product meaning and
accepted decisions govern later formalization and implementation.

Actual artifact presence is read from the repository tree. `AGENTS.md` owns
repository execution and authorization guardrails. `formal/verification.yaml`
owns formal lifecycle and intended verification state, and `formal/results/`
owns bounded TLC evidence.

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
- [Projection-integrity policy](docs/repository-governance/turnlock-rust-projection-integrity.md)
  defines repository policy for mutable derived state and documentation
  projections.
- [Normative specification](docs/specification/turnlock-spec.md) defines product
  intent, canonical terminology, promises, invariants, boundaries, and
  architectural implications.
- [Terminology review inventory](docs/specification/terminology-inventory.yaml)
  records non-authoritative locations and fingerprints for reviewed
  definition-like occurrences.
- [Annotated ADR history](docs/adr/README.md) provides the maintained
  chronological decision narrative. Its canonical ADR coverage is mechanically
  validated against the ADR corpus.
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
- [Formal workspace](formal/README.md) explains formal artifact roles and
  layout conventions; current formal lifecycle state is owned by
  `formal/verification.yaml`.
- [ADR metadata tool](scripts/adr-metadata.py) validates ADR identity,
  provenance, lifecycle metadata, outgoing relations, body integrity, and
  generated projections.
- [Traceability checker](scripts/check-formal-traceability.py) validates
  invariant IDs, ADR references, manifest statuses, and generated mapping
  freshness.
- [Repository integrity suite](scripts/check-repository-integrity.py) is the
  canonical executable repository-integrity suite used by both agents and CI.
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
boundary. Protected values need not be disclosed, but before or during the required
realizable semantic-boundary capture handoff a generic protected view cannot
replace more specific provenance TURNLOCK knew. A runtime cannot satisfy that obligation through momentary internal existence
or a race-dependent observation path. When no consumer is attached, TURNLOCK
still completes its side of the realizable semantic-boundary interaction
through the structurally realizable capture capability; actual receiver
participation is not required. Consumer absence, delivery failure, persistence,
and retention remain separate concerns. This does
not impose stable cross-run identity, equality evidence, persistence, or make
TURNLOCK the evaluator or optimizer. Evaluation objectives, property-relative
relevance, comparison judgments, and optimization policy come from an explicitly responsible actor or
authored workflow, never from core TURNLOCK runtime policy.

## Formal verification organization

```text
docs/specification/turnlock-spec.md   normative meaning
docs/adr/                             decision history
formal/verification.yaml              intended forward/reverse traceability graph
docs/formal/invariant-mapping.md      generated human-readable mapping
formal/Turnlock.tla                   executable abstract state-machine model at its governed path
formal/models/focused/                targeted TLC exploration of the shared model
formal/models/integrated/             integrated TLC exploration profiles
formal/tlc-result.schema.json         schema for TLC run evidence
formal/results/                       bounded TLC run evidence
```

[ADR-015](docs/adr/adr-015-evolve-the-normative-and-formal-specifications-together.md)
requires normative and formal specifications to evolve together. The manifest
records intended traceability; it is not proof that model checking occurred.
Actual TLC evidence remains separate under `formal/results/`, and focused
exploration never substitutes for integrated exploration of the shared model.

A `checked` claim exists only when the manifest state and matching bounded run
evidence satisfy the formal traceability checker.
