# TURNLOCK annotated architectural decision history

This maintained history explains the chronological decision narrative and
repository-specific qualifications. It is not a generated relationship
authority. Canonical structured metadata lives in ADR frontmatter under
[`adr-profile.yaml`](adr-profile.yaml); incoming relations are derived from
source ADRs once the generated projection is enabled.

ADR-001 through ADR-016 were migrated under ADR-017 with exact H1-to-EOF
preservation evidence in
[`metadata-migration-evidence.yaml`](metadata-migration-evidence.yaml). All ADRs
now carry canonical structured frontmatter. Retained legacy Markdown metadata is
historical presentation only.

The [generated ADR index](index.md) is the mechanical forward/reverse projection
of canonical metadata. This README remains the manually maintained annotated
history and repository guide.

Architectural decisions are kept in the chronological order in which the
product discussion established them. Decision numbers are stable identities.
The consolidated product specification lives at
[`../specification/turnlock-spec.md`](../specification/turnlock-spec.md).

ADR-001 through ADR-015 were reconstructed from the TURNLOCK product
conversation of 2026-09-12/13. They record decisions that were already made in
the discussion but had not yet been separated into explicit decision records.
Later ADRs record subsequently accepted decisions.

## Chronological decision trace

1. [ADR-001: Make the workflow own orchestration after session entry](adr-001-make-the-workflow-own-orchestration-after-session-entry.md) — **Accepted**. The initial problem established that a skill-like slash invocation should start a script/workflow which can later use the main agent, rather than asking the main agent to orchestrate the entire procedure.
2. [ADR-002: Require natural skill-like slash-command invocation inside coding-agent sessions](adr-002-require-natural-skill-like-slash-command-invocation.md) — **Accepted**. The motivating `/go` string was only an example; the actual product invariant is native-feeling slash-command invocation from the active coding-agent session, comparable to invoking a skill.
3. [ADR-003: Make product intent and derived invariants govern implementation](adr-003-make-product-intent-and-derived-invariants-govern-implementation.md) — **Accepted**. The specification method was made explicit: product intent first, then invariants, with implementation mechanisms deferred.
4. [ADR-004: Make mechanical steps first-class and non-agent-mediated](adr-004-make-mechanical-steps-first-class-and-non-agent-mediated.md) — **Accepted**. The target control sequence introduced mechanical steps that must remain workflow-owned rather than agent-interpreted.
5. [ADR-005: Model main-agent steps as reversible, repeatable control handoffs](adr-005-model-main-agent-steps-as-reversible-repeatable-control-handoffs.md) — **Accepted**. The discussion clarified that after the main agent takes control, execution must be able to return to mechanical workflow steps repeatedly.
6. [ADR-006: Nest workflow execution inside the originating main-agent session lifecycle](adr-006-nest-workflow-execution-inside-the-originating-main-agent-session-lifecycle.md) — **Accepted**, clarified by ADR-008. The top-level reference sequence established that workflow execution is a bounded episode inside the originating main-agent session; ADR-008 generalizes termination to return to the immediate caller for nested invocations.
7. [ADR-007: Preserve main-agent cognitive lineage and ordinary interactive agency](adr-007-preserve-main-agent-cognitive-lineage-and-ordinary-interactive-agency.md) — **Accepted**. The comparison with spawned agents established why main-agent handoff exists: avoid a cognitive fork/context reconstruction boundary and preserve the coding harness's native interactive agent loop.
8. [ADR-008: Allow nested workflow invocation from main-agent regions and return to the immediate caller](adr-008-allow-nested-workflow-invocation-from-main-agent-regions.md) — **Accepted**. Skill-like session capabilities remain available during main-agent regions; nested workflows suspend their callers, own their own progression, and return to the immediate invocation context.
9. [ADR-009: Use the same TURNLOCK primitives for developer-authored and coding-agent-authored workflows](adr-009-use-the-same-turnlock-primitives-for-developer-and-agent-authored-workflows.md) — **Accepted**. Workflow authoring is developer-native: the developer may write the workflow directly or ask the coding agent to write it, but both use the same public TURNLOCK primitives and artifact semantics.
10. [ADR-010: Keep workflow semantics harness-independent and use Pi as the first reference integration](adr-010-keep-workflow-semantics-harness-independent-and-use-pi-as-the-first-reference-integration.md) — **Accepted**. TURNLOCK remains harness-agnostic at the semantic layer while Pi is used as the first implementation and conformance environment.
11. [ADR-011: Make independent agents first-class workflow resources and support workflow-owned parallel fan-out/fan-in](adr-011-make-independent-agents-first-class-and-support-parallel-fan-out-fan-in.md) — **Accepted**. Independent bounded cognitive lineages are required workflow resources; declared subagent fan-out/fan-in remains under workflow-owned control and may run same-task or different-task branches concurrently.
12. [ADR-012: Make bounded raw LLM inference first-class and allocate the minimum sufficient cognition](adr-012-make-bounded-raw-llm-inference-first-class-and-allocate-minimum-sufficient-cognition.md) — **Accepted**. One-shot semantic inference is distinct from autonomous agents and main-agent continuation; workflows choose the minimum sufficient cognition form while retaining workflow-owned control over probabilistic results.
13. [ADR-013: Allow heterogeneous parallel fan-out across execution forms](adr-013-allow-heterogeneous-parallel-fan-out-across-execution-forms.md) — **Accepted**. A single workflow-owned parallel region may mix mechanical, raw-LLM, and independent-agent branches while preserving each branch type's semantics; same-task and different-task semantic branches are both supported.
14. [ADR-014: Define TURNLOCK as the orchestration engine and the workflow as the orchestration program](adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md) — **Accepted**. The workflow artifact owns declared orchestration decisions and topology; TURNLOCK is the engine/runtime that executes, coordinates, and tracks them without silently inventing undeclared global strategy.
15. [ADR-015: Evolve the normative and formal specifications together](adr-015-evolve-the-normative-and-formal-specifications-together.md) — **Accepted**. State/control/concurrency semantics are formalized in parallel with the prose specification; stable invariant IDs map machine-readably to TLA+ properties and, once modeled, their state variables/actions and TLC configs; the mapping is reversible for impact analysis; actual TLC run evidence is stored separately from verification intent; focused exploration never replaces integrated exploration.
16. [ADR-016: Separate workflow authorship from runtime execution
    authority][16] — **Accepted**. Developer, agent, planner, or
    higher-level-system authorship does not confer runtime orchestration
    authority. The workflow artifact remains authoritative and TURNLOCK executes
    it; an authoring agent available under an existing execution form may later
    participate through an explicitly declared region.

17. [ADR-017: Adopt validated OKF Architecture Decision Record metadata][17] —
    **Accepted**. TURNLOCK pins the generalized OKF ADR profile, keeps a
    byte-identical vendored base schema plus a local overlay, authorizes a
    body-preserving metadata migration, stores outgoing relations only, and
    separates the generated mechanical projection from this annotated history.
18. [ADR-018: Require completed workflow execution inspectability][18] —
    **Accepted**. Completed executions expose enough actual TURNLOCK-visible
    behavior for user- or system-led evaluation and iterative refinement,
    without making TURNLOCK itself the evaluator or optimizer or selecting a
    tracing, storage, replay, comparison, or reproducibility mechanism.

19. [ADR-019: Keep evaluation and optimization policy outside TURNLOCK core][19] —
    **Accepted**. TURNLOCK remains the execution substrate: it exposes
    sufficient actual execution truth under ADR-018 but does not define
    universal evaluation criteria, own comparison or experiment policy, or
    optimize workflow artifacts. Evaluation and optimization may be performed
    by a user, coding agent, evaluator, higher-level system, or ordinary
    TURNLOCK workflow, and any resulting refinement is ordinary authorship.
20. [ADR-020: Define independent-agent context provenance][20] — **Accepted**.
    A workflow-declared independent agent begins a fresh cognitive lineage with
    initial cognitive context supplied explicitly through workflow semantics,
    while main-agent-internal child delegation remains ordinary local agency
    unless the workflow declares it as a first-class TURNLOCK region.
21. [ADR-021: Separate independent-agent completion, output, and effects][21] —
    **Accepted**. Normal completion is workflow-recognizable and follows the
    declared continuation; business output is optional unless required by the
    region contract, effects may persist, and no universal completion or
    resource-bound guarantee is introduced.
22. [ADR-022: Allow workflow-declared invocation with structured call/return
    semantics][22] — **Accepted**. A workflow program may declaratively invoke
    another workflow, and TURNLOCK executes the declared call directly rather
    than reproducing a known decision through a main-agent handoff. The
    calling continuation is suspended locally, normal completion returns to the
    same immediate caller, and decision ownership remains distinct from
    ADR-008 agent-selected invocation.

[16]: adr-016-separate-workflow-authorship-from-runtime-execution-authority.md
[17]: adr-017-adopt-validated-okf-architecture-decision-record-metadata.md
[18]: adr-018-require-completed-workflow-execution-inspectability.md
[19]: adr-019-keep-evaluation-and-optimization-policy-outside-turnlock-core.md
[20]: adr-020-define-independent-agent-context-provenance.md
[21]: adr-021-separate-independent-agent-completion-output-and-effects.md
[22]: adr-022-allow-workflow-declared-invocation-with-structured-call-return-semantics.md

ADR-014 makes the ownership terminology precise:

```text
workflow program = orchestration decisions / declared topology
TURNLOCK = orchestration engine / runtime execution authority
```

TURNLOCK executes orchestration; it does not invent it.

ADR-016 makes author provenance independent of runtime authority:

```text
developer / agent / planner / higher-level system
  → authors workflow artifact
  → TURNLOCK executes declared orchestration

authorship != runtime orchestration authority
```

An authoring agent may later be invoked through an explicit workflow region,
including continuation of the same main-agent lineage, without becoming the
workflow's global scheduler.

ADR-018 extends the product loop beyond correct execution:

```text
author workflow
→ execute workflow
→ inspect and evaluate actual behavior
→ refine workflow
→ execute again
```

TURNLOCK exposes sufficient truth about behavior at its own semantic boundary.
The user or a higher-level system owns evaluation criteria, comparison where
appropriate, and workflow changes. ADR-019 fixes the boundary that ADR-018
reserved: TURNLOCK core does not own evaluation or optimization policy, and
behavior that evaluates or refines a workflow remains ordinary authored
execution.

## Governing reference scenario

```text
main agent
  > natural slash-command workflow invocation
  > workflow/script
  > mechanical step
  > main-agent step
  > mechanical step
  > main-agent step
  > mechanical step
  > workflow/script terminated
  > same continuing main-agent interaction
```

The individual ADRs explain why each transition in this scenario is product-significant. ADR-008 additionally establishes structured composition:

```text
main agent
  > workflow A
    > main-agent region A
      > workflow B
      < workflow B
    < main-agent region A
  < workflow A
main agent
```

Each nested workflow returns to its immediate caller. Implementation mechanisms remain intentionally open where the discussion has not yet forced them.
The authoring and harness decisions add two further conformance dimensions:

```text
developer writes workflow ─┐
                          ├─> same TURNLOCK primitives/artifact
coding agent writes it ───┘

TURNLOCK semantics
  > Pi adapter first
  > later harness adapters
```

Pi is the first reference environment, not the semantic definition of the workflow model.

## Cognitive execution spectrum

ADR-011 and ADR-012 extend the reference model beyond the original mechanical/main-agent contrast:

```text
TURNLOCK workflow owns global orchestration
  ├─ mechanical execution
  ├─ bounded raw LLM inference
  ├─ bounded independent agentic execution
  └─ continuation of the main interactive agent
```

Independent agents and raw LLM calls may be fanned out concurrently under
workflow control, either homogeneously or together with mechanical branches in
the same heterogeneous fan-out. Same-type semantic branches may perform the
same task or different tasks. The forms are intentionally non-equivalent: the
author selects the minimum sufficient form for each region.

ADR-020 and ADR-021 make the independent-agent boundary precise. A
workflow-declared independent agent receives no implicit main-agent cognitive
context, but may receive explicitly declared main-agent-derived information and
acquire information during its own work. If normal completion occurs, TURNLOCK
recognizes it and follows the declared continuation; a business payload is
required only when the region contract requires one, while effects remain a
separate concern. These structural semantics introduce neither a concrete
resource bound nor a universal completion guarantee.

ADR-022 generalizes nested invocation without relocating decision ownership. A
workflow-declared invocation belongs to the workflow program, while an
agent-selected invocation still belongs to the main agent during a main-agent
region. Both preserve the calling context's continuation and return to the same
immediate caller on normal completion, and suspension stays local to the
calling continuation rather than blocking independently declared concurrent
contexts.

Accepted ADR bodies retain their historical wording, including uses of
“deterministic computation” and “deterministic orchestration.” The current
normative specification clarifies those passages through the authority and
control distinction already present in ADR-004, ADR-012, and ADR-014:
mechanical execution is non-agent-mediated but need not have deterministic
results, and workflow-owned control restricts global progression to declared
possibilities without requiring one output, path, or trace.

## Formal-specification governance

ADR-015 establishes a second, synchronized specification surface:

```text
normative prose + ADRs
        ↕ stable invariant IDs
formal/verification.yaml
        ↕
TLA+ properties
        ↕
state variables + actions/transitions
        ↕
focused + integrated TLC configs
        ↓
formal/results/* (actual run evidence by commit/bounds)
```

`formal/verification.yaml` is the machine-readable desired traceability/coverage graph and is mechanically invertible for formal impact analysis. `docs/formal/invariant-mapping.md` is generated from it. Actual TLC execution evidence is a distinct artifact class under `formal/results/` governed by `formal/tlc-result.schema.json`; a mapped property is not the same thing as a verified property. Focused model-checking configurations are allowed for speed and diagnosis, but TURNLOCK must retain integrated smoke/standard/stress profiles against the shared semantic model so cross-feature interactions remain explorable after semantic changes. No invariant is currently claimed as `checked`; the executable TLA+ model is the next formalization step.
