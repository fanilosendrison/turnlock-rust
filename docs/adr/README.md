# TURNLOCK annotated architectural decision history

This maintained history explains the chronological decision narrative and
repository-specific qualifications. Its narrative annotations remain manually
authored, while the canonical ADR identity, name, status, path, order, and
coverage of the marked chronological trace are mechanically validated against
canonical ADR records. It is not an authority over ADR metadata. Canonical
structured metadata lives in ADR frontmatter under
[`adr-profile.yaml`](adr-profile.yaml); incoming relations are derived from
source ADRs once the generated projection is enabled.

ADR-001 through ADR-016 were migrated under ADR-017 with exact H1-to-EOF
preservation evidence in
[`metadata-migration-evidence.yaml`](metadata-migration-evidence.yaml). All ADRs
now carry canonical structured frontmatter. Retained legacy Markdown metadata is
historical presentation only.

The [generated ADR index](index.md) is the mechanical forward/reverse projection
of canonical metadata. This README remains the manually maintained annotated
history and repository guide; `scripts/adr-metadata.py` validates the marked
trace against the canonical ADR corpus.

Architectural decisions are kept in the chronological order in which the
product discussion established them. Decision numbers are stable identities.
The consolidated product specification lives at
[`../specification/turnlock-spec.md`](../specification/turnlock-spec.md).

ADR-001 through ADR-015 were reconstructed from the TURNLOCK product
conversation of 2026-09-12/13. They record decisions that were already made in
the discussion but had not yet been separated into explicit decision records.
Later ADRs record subsequently accepted decisions.

## Chronological decision trace

<!-- adr-annotated-trace:start -->

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
    **Accepted**, amended by ADR-039. ADR-018 historically introduced
    completed-execution inspectability: completed executions expose enough
    actual TURNLOCK-visible behavior for user- or system-led evaluation and
    iterative refinement, without making TURNLOCK itself the evaluator or
    optimizer or selecting a tracing, storage, replay, comparison, or
    reproducibility mechanism. ADR-039 later generalized that obligation into
    the current execution-inspectability contract and made its semantic
    sufficiency and realizable-terminal-inspection-handoff semantics precise.

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
23. [ADR-023: Clarify caller-context and continuation semantics across nested
    workflow invocations][23] — **Accepted**. An immediate caller context is
    distinct from its preserved call continuation. A workflow-declared
    invocation makes its workflow-declared post-call continuation eligible on
    normal return, while an agent-selected invocation resumes the same
    main-agent region; neither return disables independently active concurrent
    contexts.
24. [ADR-024: Preserve effective execution-condition provenance][24] —
    **Accepted**, clarified by ADR-025. Conditions TURNLOCK selects, binds,
    explicitly supplies, or resolves remain attributable to the execution
    scopes they govern and exposable or capturable at its semantic boundary.
    Unknown external conditions may remain unknown; persistence, replay,
    reproducibility, comparison policy, and optimization policy are not implied.
25. [ADR-025: Preserve condition-specific provenance without requiring
    protected-value disclosure][25] — **Accepted**. Exact protected values need
    not be disclosed, but before or during the required boundary capture
    opportunity protection cannot substitute away condition-specific information
    TURNLOCK possessed about known effective conditions. A condition-specific
    representation remains scope-attributable and capturable; consumer views may
    be more restrictive without defining stable cross-run identity, equality,
    authorization, persistence, or a protection mechanism.
26. [ADR-026: Define a realizable semantic-boundary capture handoff][26] —
    **Accepted**, clarifies ADR-024 and ADR-025. The required boundary capture
    opportunity is satisfied only by a realizable semantic-boundary capture
    handoff: an eligible conforming capture context could acquire the required
    condition-specific provenance and governed-scope attribution as part of the
    boundary interaction, not merely because the provenance existed internally
    for some duration or because a consumer could win an accidental timing race.
    The universal floor requires a structurally realizable capture capability
    and completion of TURNLOCK's side of the semantic-boundary interaction, but
    not an actual attached or participating consumer, successful delivery,
    acknowledgment, retention duration, or post-handoff availability; stronger
    guarantees may be added above it by a profile, integration, or later
    decision.
27. [ADR-027: Bind each accepted invocation to a stable governing workflow
    definition][27] — **Accepted**, confirms ADR-014 and ADR-024. Every accepted
    invocation is bound to one governing workflow definition determined no later
    than invocation acceptance and stable for that invocation's lifetime;
    ordinary later edits of the source artifact do not alter it. Each nested
    invocation establishes its own governing definition at its own acceptance,
    so a caller's binding does not transitively freeze future callees. Live
    source-edit visibility, implicit dynamic mutation, and root-wide transitive
    dependency snapshots are rejected. Deliberate active-definition mutation and
    whether an execution resource may edit a governing workflow's source
    artifact remain separate decisions.
28. [ADR-028: Clarify that TL-INV-037 forbids governing-definition changes
    under current semantics][28] — **Accepted**, clarifies ADR-027 without
    changing its substantive meaning. Under current accepted authority,
    `TL-INV-037` requires an accepted invocation's governing workflow
    definition to remain unchanged for its entire active lifetime, so the
    current formal model must forbid every represented transition that changes
    it and must not reserve an authorization-gated exception for a future
    active-definition-mutation capability. ADR-027's mention of a possible
    future mutation decision is only a future-governance boundary; a future
    decision must reconcile explicitly with `TL-INV-037` and ADR-027.
    The authority questions retained by Issue #18 were subsequently resolved
    by ADR-029.
29. [ADR-029: Separate local execution capabilities from immutable invocation
    orchestration][29] — **Accepted**, clarifies ADR-001, ADR-007, ADR-014,
    ADR-016, ADR-019, ADR-027, and ADR-028. TURNLOCK core does not own general
    repository, filesystem, tool, OS, sandbox, ACL/RBAC, path, token, or
    grant/revoke permissions; those restrictions belong to the surrounding
    execution environment unless a later explicit decision introduces a
    specific TURNLOCK capability. Local source-artifact self-authoring remains
    an ordinary local action where the environment permits it and never
    mutates the governing definition of an accepted active invocation. Active
    replanning and rebinding are outside and contrary to the current product
    contract rather than a reserved future feature, and the boundary applies
    equally to every execution resource. No new invariant identity is created;
    `TL-INV-037` and the existing workflow-owned-control and authorship
    invariants remain the owners.
30. [ADR-030: Make TURNLOCK Core a runtime-composable execution substrate][30] —
    **Accepted**. TURNLOCK Core must permit supported concrete execution
    realizations that are not fixed by TURNLOCK semantics to be composed at
    runtime without making Core modification/recompilation the only substitution
    path when the alternative preserves TURNLOCK semantics. A supported external
    realization must become effective before its governed causal use and, once
    accepted for that use, must not be silently bypassed by an unauthorized
    substitute. The decision selects no plugin, hook, IPC, DI, process, or other
    extension mechanism and preserves ADR-019's external
    evaluation/optimization-policy boundary, ADR-029's environment-permission
    boundary, and main-agent continuity.
31. [ADR-031: Clarify the runtime-realization composability trigger][31] —
    **Accepted**. Clarifies ADR-030 so pre-existing Core support cannot become a
    circular precondition for `TL-INV-038`. When a concrete realization is not
    fixed by TURNLOCK semantics and a semantically preserving alternative is
    technically realizable at runtime in a supported harness or execution
    environment, Core must provide the supported runtime composition path;
    lacking that path cannot itself justify classifying the alternative as
    unsupported. No new invariant or extension mechanism is introduced.
32. [ADR-032: Allow main-agent participation in workflow-owned concurrency without cognitive-lineage fork](adr-032-allow-main-agent-participation-in-workflow-owned-concurrency-without-cognitive-lineage-fork.md) — **Accepted**. Resolves the main-agent concurrency question deliberately left open by ADR-013: a workflow-owned concurrent region may contain a main-agent continuation, but the same continuing main-agent cognitive lineage may not fork across independently concurrent, non-causally-ordered continuations. Main-agent handoff is branch-local, sibling work remains governed by the declared topology, and runtime scheduling must not manufacture causal order absent from the workflow.
33. [ADR-033: Permit recursive and cyclic workflow invocation under ordinary invocation semantics](adr-033-permit-recursive-and-cyclic-workflow-invocation-under-ordinary-invocation-semantics.md) — **Accepted**. Resolves the recursion/cycle question left open by earlier invocation decisions: direct recursion and cyclic workflow call graphs are permitted, every occurrence remains an ordinary distinct invocation with structured immediate-caller return and per-occurrence governing-definition binding, and recursion creates neither new invocation authority nor an admissibility escape, termination guarantee, or product-level depth/resource limit.
34. [ADR-034: Delegate nested-workflow invocation to independent-agent regions without main-agent reachability](adr-034-delegate-nested-workflow-invocation-to-independent-agent-regions-without-main-agent-reachability.md) — **Accepted**. Allows a workflow to explicitly delegate dynamic nested-workflow selection/invocation authority to a workflow-declared independent-agent region without making that authority implicit or globally orchestrating. Authorized independent agents may select available callees without a universal parent-enumerated exact-callee whitelist, but every invocation remains independently subject to admission and an IA-selected invocation subtree may not transitively reach the coding session's main-agent cognitive lineage.
35. [ADR-035: Define transitive nested-composition admissibility and fail-closed invocation acceptance](adr-035-define-transitive-nested-composition-admissibility-and-fail-closed-invocation-acceptance.md) — **Accepted**. Defines the general pre-acceptance composition-admissibility contract for nested workflow invocation: invocation authority and admissibility are independent, applicable restrictions remain closed under nested/recursive composition according to their accepted scopes, workflow invocation may occur inside parallel or otherwise restricted contexts when admissible, unknown required compatibility fails closed without silent serialization or scheduler-derived ordering, and rejected pre-acceptance attempts create no callee invocation.
36. [ADR-036: Define occurrence-scoped conditional orchestration progress without universal completion](adr-036-define-occurrence-scoped-conditional-orchestration-progress-without-universal-completion.md) — **Accepted**. Separates execution-resource completion from TURNLOCK-owned orchestration progress: TURNLOCK does not universally guarantee completion of regions, invocations, branches, or workflows; recognized completion/yield/return/join satisfaction establishes its required structural control consequence; and each TURNLOCK-owned progression occurrence that remains continuously enabled and applicable must not be indefinitely starved by TURNLOCK's own scheduling. Occurrence representation and formal fairness encoding remain downstream modeling choices.
37. [ADR-037: Require eventual advance of continuously enabled orchestration progress](adr-037-require-eventual-advance-of-continuously-enabled-orchestration-progress.md) — **Accepted**. Amends ADR-036 by removing the competing-progress/scheduling-cause qualifier from `TL-INV-042`: every particular TURNLOCK-owned progression occurrence that remains continuously enabled and applicable must eventually be advanced by TURNLOCK, including when no competing progression is selected. The amendment preserves the absence of universal work-completion, crash-recovery, durability, runtime-identity, scheduler-mechanism, and formal-fairness guarantees.
38. [ADR-038: Assume native harness workflow convergence](adr-038-assume-native-harness-workflow-convergence.md) — **Accepted**. TURNLOCK is designed as an augmentation layer whose durable value does not depend on capability gaps in current coding-agent harnesses; compatible native harness workflow mechanisms are realization assets under TURNLOCK semantics, and architecture proposals are stress-tested against a hypothetical capability-complete harness.
39. [ADR-039: Define sufficient execution inspectability and terminal inspection handoff](adr-039-define-sufficient-execution-inspectability-and-terminal-inspection-handoff.md) — **Accepted**, amends ADR-018. `TL-INV-033` remains the single execution-inspectability invariant: semantic sufficiency preserves realized TURNLOCK progression without requiring an event catalog, observed non-success outcomes expose realized-prefix and actually known terminal truth, and required execution truth must reach a realizable terminal inspection handoff before irreversible loss. Disclosure may be more restrictive than underlying inspection truth, while persistence, retention duration, replay, cross-run comparison, evaluation policy, and crash-durable post-mortem evidence remain outside the universal core floor. Under ADR-038, conforming harness-native inspection facilities may serve as realization assets without becoming semantic authority.
40. [ADR-040: Preserve future abstraction extractability without prematurely generalizing TURNLOCK](adr-040-preserve-future-abstraction-extractability-without-prematurely-generalizing-turnlock.md) — **Accepted**, confirms ADR-003. TURNLOCK remains a concrete, TURNLOCK-specific semantic domain while architecture and representation work preserve the ability to later distinguish and extract abstractions that may generalize first to software problem solving and ultimately to SCOPE's general problem-solving representation. The decision forbids weakening or prematurely genericizing TURNLOCK for that future goal and creates no IR, new invariant, product semantic, or formal-verification claim.

<!-- adr-annotated-trace:end -->

[16]: adr-016-separate-workflow-authorship-from-runtime-execution-authority.md
[17]: adr-017-adopt-validated-okf-architecture-decision-record-metadata.md
[18]: adr-018-require-completed-workflow-execution-inspectability.md
[19]: adr-019-keep-evaluation-and-optimization-policy-outside-turnlock-core.md
[20]: adr-020-define-independent-agent-context-provenance.md
[21]: adr-021-separate-independent-agent-completion-output-and-effects.md
[22]: adr-022-allow-workflow-declared-invocation-with-structured-call-return-semantics.md
[23]: adr-023-clarify-caller-context-and-continuation-semantics-across-nested-workflow-invocations.md
[24]: adr-024-preserve-effective-execution-condition-provenance.md
[25]: adr-025-preserve-condition-specific-provenance-without-requiring-protected-value-disclosure.md
[26]: adr-026-define-a-realizable-semantic-boundary-capture-handoff.md
[27]: adr-027-bind-each-accepted-invocation-to-a-stable-governing-workflow-definition.md
[28]: adr-028-clarify-that-tl-inv-037-forbids-governing-definition-changes-under-current-semantics.md
[29]: adr-029-separate-local-execution-capabilities-from-immutable-invocation-orchestration.md
[30]: adr-030-make-turnlock-core-a-runtime-composable-execution-substrate.md
[31]: adr-031-clarify-the-runtime-realization-composability-trigger.md

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

ADR-024 adds a separate forward-compatibility floor:

```text
condition TURNLOCK selects / binds / explicitly supplies / resolves
→ governs execution scope
→ attribution remains exposable or capturable at TURNLOCK's boundary
```

ADR-025 clarifies that floor for protected values:

```text
exact-value disclosure is not universally required
+
protection cannot substitute away TURNLOCK-known condition-specific provenance
before or during the required realizable semantic-boundary capture handoff
```

A consumer may receive a restricted view, but a generic protected marker cannot
be the sole provenance representation when it substitutes away more specific
condition information TURNLOCK possessed before or during the boundary capture
handoff. This clarification creates no stable cross-run
identity, equality evidence, authorization model, persistence, replay,
reproducibility, or comparison contract. Together the decisions complement
ADR-018 without absorbing Issue #13 and preserve ADR-019's policy boundary.

ADR-026 defines when that boundary capture opportunity is genuinely satisfied:

```text
required provenance
→ realizable semantic-boundary capture handoff
→ eligible conforming capture context could acquire it as part of the interaction
→ TURNLOCK completes its side of the semantic-boundary interaction
→ universal obligation discharged

actual consumer participation, successful delivery, acknowledgment,
retention duration, or post-handoff availability are not required
by the universal floor
```

A handoff is not a retention interval. Momentary internal existence, or an
acquisition path that depends on an accidental race against inaccessible
internal timing, does not satisfy or discharge the floor. When no consumer is
attached, TURNLOCK discharges the handoff by completing its side of the
semantic-boundary interaction through the structurally realizable capture
capability; actual receiver participation is not required. Consumer absence,
participant failure, and delivery failure do not by themselves impose
retention, while stronger availability and persistence guarantees remain
available above the floor through separate accepted decisions or integration
contracts. Issue #13 owns detailed non-completed-execution inspectability,
availability, retention, access, and privacy.

ADR-027 fixes which definition governs an active invocation without selecting a
representation:

```text
artifact W = D1
accept invocation I of W
→ governing definition(I) = D1
artifact W later changes D1 → D2
→ I continues under D1
→ a later invocation J receives whatever definition applies at J's acceptance
```

Each nested invocation establishes its own governing definition, so stability
is per invocation rather than a transitive snapshot of the entire execution
tree. Live source-edit visibility, implicit root-wide dependency freezing, and
implicit mutation of an active governing definition are rejected; deliberate
active-definition mutation and whether an execution resource may edit a
governing workflow's source artifact remain separate decisions. ADR-024,
ADR-025, and ADR-026 continue to govern the provenance of whichever definition
is effective.

ADR-028 removes an ambiguity in how ADR-027's accepted semantics must be
represented in the current formal model:

```text
future product possibility
!=
current semantic permission

leaving a future decision open
!=
reserving a present transition in the state machine
```

`TL-INV-037` is unconditional for an accepted invocation's active lifetime, so
the current model must reject every represented transition changing its
governing definition from `D` to another definition `D'`, with no
authorization-gated exception path. The invariant and ADR-027's substantive
decision are unchanged; a future active-definition-mutation decision would have
to reconcile with both.

ADR-029 resolves the authority question retained by Issue #18 without creating
a TURNLOCK-owned permission layer:

```text
TURNLOCK orchestration authority
!=
general operational authority over the surrounding environment

local agency / local effects
!=
TURNLOCK global orchestration authority

source-artifact self-authoring
!=
active invocation self-replanning
```

TURNLOCK core defines no ACL/RBAC, filesystem, path, tool-allowlist,
capability-token, sandbox, grant/revoke, meta-workflow, or official-workflow
privilege semantics. Ordinary workflow authoring, including editing a currently governing
source artifact, remains a local action permitted or restricted by the
surrounding environment and never changes an accepted invocation's governing
definition. Active replanning and rebinding are recorded as outside and
contrary to the current product contract rather than as a reserved extension,
and the same boundary applies to the main agent, independent agents, and every
other execution resource. `TL-INV-037` and the existing workflow-owned-control
and authorship invariants remain the sole owners; ADR-029 admits no new
`TL-INV-*` identity.

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

ADR-023 clarifies the caller model shared by both invocation paths. The caller
is an execution context, not the continuation itself: the caller context
preserves a return-bearing continuation while the callee executes. A
workflow-declared invocation makes its workflow-declared post-call continuation
eligible on normal return, while an agent-selected invocation resumes the same
main-agent region and leaves that region's subsequent local work under the main
agent's local authority. Neither case implies whole-workflow suspension of
independently active concurrent contexts.

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

`formal/verification.yaml` is the machine-readable desired traceability/coverage graph and is mechanically invertible for formal impact analysis. `docs/formal/invariant-mapping.md` is generated from it. Actual TLC execution evidence is a distinct artifact class under `formal/results/` governed by `formal/tlc-result.schema.json`; a mapped property is not the same thing as a verified property. Focused model-checking configurations are allowed for speed and diagnosis, but TURNLOCK must retain the manifest-declared integrated profiles against the shared semantic model so cross-feature interactions remain explorable after semantic changes. A `checked` claim exists only when the manifest state and matching bounded run evidence satisfy the formal traceability checker.
