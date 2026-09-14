---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Keep evaluation and optimization policy outside TURNLOCK core"
id: "ADR-019"
status: "accepted"
date: "2026-09-14"
decision_body_sha256: "74f8c280a5bd4f5539dfb4cfdfd648179410b9de37e414e7a7fc5f6f37d93722"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-018"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Ownership boundary between TURNLOCK execution and workflow evaluation or optimization policy"
---

# ADR-019: Keep evaluation and optimization policy outside TURNLOCK core

## Context

ADR-018 requires every completed TURNLOCK execution to expose enough actual
TURNLOCK-visible behavior for a user or higher-level system to understand and
evaluate how the workflow progressed. It also separates execution truth from
evaluation and explicitly reserves the question of whether TURNLOCK should
later provide native evaluation or optimization facilities.

That reserved question is what this decision resolves. ADR-018 already fixed
completed-execution inspectability, exposure of execution truth at TURNLOCK's
semantic boundary, retention of evaluation criteria by the user or a
higher-level system, and the fact that comparison and optimization are not
implied by inspectability. Those statements are accepted and are not reopened
here. ADR-019 fixes the remaining ownership boundary between execution and
evaluation or optimization policy.

Three responsibilities are easily conflated:

```text
1. making an execution evaluable
2. TURNLOCK performing evaluation
3. TURNLOCK optimizing workflows
```

They do not form an implied package. A system can expose execution truth
without owning an objective function, and it can enable evaluation without
optimizing authored artifacts. TURNLOCK already treats declared orchestration
as owned by the workflow program (ADR-001, ADR-014) and authorship as separate
from runtime execution authority (ADR-016). The open question is where
evaluation and optimization policy belong relative to that boundary.

The question is not only about feature selection. TURNLOCK workflows are
authored artifacts whose practical value includes iterative refinement.
Refinement requires an objective, and objectives are policy: they depend on
what the responsible user or system values. If core TURNLOCK defined universal
criteria or autonomously selected better workflows, it would become a hidden
policy owner for authored artifacts, which would conflict with the product's
execution-substrate identity. Conversely, refusing to expose execution truth
would make refinement depend on recollection, which ADR-018 already rejected.

## Discovery classification

Against the current corpus, the remaining ownership question is still a
`decision-required` product decision. Current authority constrains the boundary
but leaves multiple product boundaries compatible with it, so the answer is not
uniquely derived. The statements ADR-018 already settled are recorded as
already accepted rather than re-decided here, and the consequences of this
decision are classified separately rather than promoted wholesale. No product
meaning is treated as derived merely because this boundary is architecturally
consistent.

## Decision

TURNLOCK core is the workflow execution substrate and orchestration engine. It
does not own workflow evaluation or optimization policy.

Normatively:

```text
workflow W
  → TURNLOCK executes W
  → inspectable actual TURNLOCK-visible execution truth
  → user / coding agent / evaluator / higher-level system / ordinary TURNLOCK workflow
  → evaluation against an explicitly supplied objective
  → possible authoring of refined workflow W'
  → TURNLOCK later executes W'
```

TURNLOCK core MUST NOT define a universal evaluation objective, universal
quality metrics, a default superiority relation between workflows or
executions, experiment policy, or an autonomous workflow optimizer. What
counts as better remains a judgment supplied outside core TURNLOCK semantics by
an explicitly responsible user, coding agent, evaluator, higher-level system,
or ordinary authored workflow.

Evaluation and optimization MAY be implemented by any of those actors.
Evaluation or optimization logic MAY itself be expressed as an ordinary
TURNLOCK workflow. Such behavior remains ordinary authored execution under the
same TURNLOCK semantics and authority boundaries as any other workflow; it
does not become privileged runtime machinery merely because it inspects an
execution or proposes a workflow change.

A workflow refinement produced by evaluation or optimization is workflow
authorship. It does not authorize the TURNLOCK runtime to mutate the
orchestration of a currently executing invocation, does not make the evaluator
or optimizer the scheduler of any workflow, and does not weaken the binding of
an active invocation to its authorized orchestration. The visibility of
source-artifact edits to an already-active invocation remains a separate
question owned by Issue #4.

This decision introduces no core evaluator abstraction, metric set, comparison
contract, experiment concept, or optimizer interface. TURNLOCK-adjacent
modules, libraries, profiles, workflows, or tools for evaluation and
optimization remain possible in the future, but they are not part of the
current core product contract. Any proposal that adds native evaluator
interfaces, experiment concepts, comparison contracts, optimizer machinery,
privileged mutation authority, or stronger evaluation guarantees requires its
own accepted product decision.

This decision does not change what Issue #13 must treat as the minimum
sufficient inspectability contract. The ADR-018 obligation and `TL-INV-033`
remain exactly as accepted, and the concrete fact set, sufficiency rules,
non-completed-execution semantics, and availability or retention questions
remain Issue #13's independent decision. The workflow-definition binding
question likewise remains with Issue #4, as recorded above. Neither Issue
depends on this ownership boundary.

## Rationale

Making workflows evaluable and being the evaluator are different product
responsibilities. ADR-018 gives TURNLOCK the first because a reusable artifact
whose behavior cannot be understood cannot be responsibly maintained. Owning
the second would require core TURNLOCK to choose what is valuable, which is not
a property of orchestration semantics but of the responsible actor's context.
The product goal is workflow improvement by an explicitly responsible actor,
not optimization ownership by the runtime.

A coding agent can inspect execution truth, apply judgment against the user's
stated objectives, and author a refined workflow using the same public
primitives. An external evaluator or higher-level system can do the same. Both
paths preserve the authority model: the workflow artifact remains the source of
declared orchestration, and authorship remains separate from execution
authority. Neither path needs privileged runtime access.

The same reasoning applies when the evaluator is itself a TURNLOCK workflow.
TURNLOCK already supports mechanical execution, bounded raw LLM inference,
independent agents, and main-agent continuation. Evaluating an execution,
scoring a result, or proposing a workflow edit can be expressed with those
primitives and ordinary authoring. A special semantic class for a workflow that
evaluates workflows would add core semantics without adding a capability that
ordinary authored behavior cannot provide.

The minimum-sufficient-cognition principle (ADR-012, `TL-INV-029`) motivates
evaluating execution-form choices: a review may conclude that a region used
more autonomy or context than necessary. That conclusion is a judgment against
an objective supplied by the responsible actor. It does not grant TURNLOCK core
authority to rewrite execution forms, and it does not create a default
objective function. The same boundary applies to cost, latency, quality,
reliability, variance, or any other evaluation input: such measurements may
inform evaluation where available and relevant, but core TURNLOCK does not
define their universal meaning, weighting, or superiority relation, and
ADR-018 does not require all of them to exist.

This decision preserves and applies ADR-014 and ADR-016. ADR-014 keeps
declared orchestration in the workflow and forbids the engine from inventing
global strategy; an autonomous optimizer inside core would be exactly such
invention. ADR-016 keeps authorship separate from execution authority; a
refinement produced outside the runtime, or by an ordinary authored workflow,
remains authorship and does not become runtime scheduling authority.

## Alternatives considered

- **Native evaluation primitives with external optimization policy
  (Alternative B):** Rejected. Generic evaluator interfaces, metric
  attachment, or comparison primitives would add core semantics without a
  product need that ordinary workflows cannot already express. Because
  objectives remain external, a core abstraction would risk becoming a hidden
  default policy and would freeze vocabulary that should stay replaceable.
- **Native evaluation and assisted optimization (Alternative C):** Rejected.
  Recommending replacement of an agent with raw LLM inference, flagging
  expensive regions, or proposing workflow variants requires an objective and
  makes TURNLOCK core a policy advisor for authored artifacts. The coding agent
  and user can perform that analysis from execution truth without a privileged
  channel.
- **TURNLOCK as an optimization system (Alternative D):** Rejected. Owning a
  search or evolution loop over workflow variants would materially expand the
  product definition and conflict with workflow-owned orchestration and
  authorship/execution-authority separation.
- **Undefined optional or profiled core boundary (Alternative E):** Rejected
  for the current product definition. Declaring evaluation or optimization an
  optional core capability would leave ownership, conformance, and the meaning
  of a default objective undefined. Future TURNLOCK-adjacent tooling is
  legitimate but must enter through an explicit accepted decision rather than
  a profile flag.
- **Core ownership of a default objective function:** Rejected. A hidden
  default would make TURNLOCK the arbiter of what "better" means and would
  recreate the hidden-policy problem the product exists to avoid.
- **Requiring a universal comparison or experiment model now:** Rejected.
  ADR-018 enables evaluation of completed behavior without establishing
  universal cross-run comparability. Comparisons are meaningful only relative
  to explicitly supplied determinants and criteria.

## Consequences

### Benefits

- TURNLOCK stays the execution substrate; the product does not silently become
  an evaluation or optimization platform.
- Evaluation and optimization can be implemented by users, coding agents,
  external evaluators, higher-level systems, or ordinary TURNLOCK workflows
  without privileged runtime machinery.
- Workflow refinement remains normal authoring over the same artifact class,
  preserving ADR-009, ADR-014, and ADR-016.
- The minimum-sufficient-cognition principle remains an author-side tool for
  reasoning about execution forms rather than a core optimizer mandate.

### Costs and obligations

- Conformance review must reject a TURNLOCK core that presents a universal
  evaluation objective, quality score, superiority relation, or autonomous
  optimizer as core product behavior.
- Any future native evaluation or optimization facility requires a new
  accepted decision and synchronized normative and formal artifacts.
- Documentation and tooling must not imply that core TURNLOCK supplies
  evaluation criteria merely because it supplies execution truth.

### Derived invariant admission

The decision uniquely entails one distinct universal obligation, `TL-INV-034`:

1. a conforming TURNLOCK core must not own evaluation or optimization policy;
2. a core that defines a universal objective, defaults a superiority relation,
   or autonomously optimizes workflows contradicts this decision;
3. every conforming realization owes the obligation independently of
   mechanism;
4. the obligation states no stronger requirement than the accepted boundary
   and introduces no evaluator, metric, comparison, experiment, or optimizer
   mechanism;
5. the closest existing identities are insufficient: `TL-INV-002` forbids
   inventing global strategy for an execution but does not forbid a core from
   owning a universal objective outside progression, and `TL-INV-032` covers
   authorship versus execution authority but not evaluation or optimization
   ownership. `TL-INV-033` requires execution truth without constraining who
   owns evaluation policy.

`TL-INV-034` is formalization-`not-applicable`: it constrains product
responsibility and implementation conformance rather than an executable state
predicate. No TLA+ property is added, and the state-machine consequences of
silent orchestration changes remain covered by the existing formally
applicable invariants.

## References

- `docs/specification/turnlock-spec.md`
- `docs/adr/adr-001-make-the-workflow-own-orchestration-after-session-entry.md`
- `docs/adr/adr-003-make-product-intent-and-derived-invariants-govern-implementation.md`
- `docs/adr/adr-009-use-the-same-turnlock-primitives-for-developer-and-agent-authored-workflows.md`
- `docs/adr/adr-012-make-bounded-raw-llm-inference-first-class-and-allocate-minimum-sufficient-cognition.md`
- `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
- `docs/adr/adr-016-separate-workflow-authorship-from-runtime-execution-authority.md`
- `docs/adr/adr-018-require-completed-workflow-execution-inspectability.md`
- `docs/vision/future-workflow-run-evaluation.md`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
- GitHub Issues #4, #11, #12, and #13
