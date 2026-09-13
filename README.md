# TURNLOCK

## A runtime for programs that call cognition

TURNLOCK is a runtime for executable workflows that compose deterministic
computation and cognition inside an existing interactive coding-agent session.
A workflow program owns its declared control flow; TURNLOCK executes,
coordinates, and tracks that control flow. Cognition is an explicit execution
resource rather than the implicit global scheduler.

A workflow may compose four distinct execution forms:

```text
deterministic computation
bounded raw LLM inference
bounded independent agents
continuation of the user's existing main coding agent
```

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
history in the [ADR index](docs/adr/README.md).

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
- [Repository governance](docs/repository-governance/turnlock-rust-engineering.md)
  defines GitHub Engineering Project routing and workflow policy.
- [Normative specification](docs/specification/turnlock-spec.md) defines product
  intent, promises, invariants, boundaries, and architectural implications.
- [ADR index](docs/adr/README.md) provides the chronological decision record and
  links to ADR-001 through ADR-016.
- [Formal-verification policy](docs/formal/README.md) explains the relationship
  between normative prose, formal intent, executable models, and evidence.
- [Formal traceability manifest](formal/verification.yaml) records
  machine-readable forward and reverse traceability and intended verification
  coverage.
- [Generated invariant mapping](docs/formal/invariant-mapping.md) projects the
  manifest into a human-readable view.
- [Formal workspace](formal/README.md) records the planned model layout and its
  current status.
- [Traceability checker](scripts/check-formal-traceability.py) validates
  invariant IDs, ADR references, manifest statuses, and generated mapping
  freshness.
- [Mapping renderer](scripts/render-formal-mapping.py) regenerates the
  human-readable mapping from the manifest.
- [Pinned tooling dependency](requirements.txt) supports formal traceability
  validation.

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
deterministic computation = non-semantic executable work
raw LLM inference = bounded non-agentic semantic computation
independent agent = bounded autonomous cognitive fork
main agent = continuation of the existing interactive cognitive lineage
```

The guiding allocation rule is to use the minimum sufficient form of
computation or cognition for each workflow region. Known orchestration remains
in executable workflow logic even when a leaf is probabilistic or locally
autonomous.

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
