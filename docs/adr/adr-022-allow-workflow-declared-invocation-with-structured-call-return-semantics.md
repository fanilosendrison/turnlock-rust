---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Allow workflow-declared invocation with structured call/return semantics"
id: "ADR-022"
status: "accepted"
date: "2026-09-15"
decision_body_sha256: "086106471128551f4d3dd8114a7cec367979cf32536bf48651b6c12a1f9b9184"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-008"
    - "ADR-014"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Declared workflow-to-workflow invocation capability, structured caller/return semantics, and the decision-owner boundary with agent-selected invocation"
---

# ADR-022: Allow workflow-declared invocation with structured call/return semantics

## Context

TURNLOCK treats a workflow as an executable orchestration program and TURNLOCK
as the engine that executes its declared topology (ADR-014). The
workflow-declared orchestration surface must already be expressive enough that
known composition decisions remain executable workflow logic rather than being
delegated back to an agent for lack of orchestration primitives. Sections 0.1,
0.2, and 2.2 and `TL-INV-031` list nested workflow invocation and structured
return among the composition capabilities a workflow must be able to express,
and ADR-014 requires TURNLOCK to provide the execution authority needed to
realize declared semantics, including nested invocation and structured return,
without inventing undeclared strategy.

Current authority defines only one invocation decision owner. ADR-008 accepted
agent-selected invocation from a main-agent region, and Section 2.8 canonically
defines `nested workflow invocation` as an invocation made from a main-agent
region while that immediate caller context is suspended. No accepted decision
defines a workflow-declared invocation, its immediate caller, its suspension
scope, its return target, or its relationship to ADR-008. The canonical
definition is therefore narrower than the composition language that references
it, and the corpus does not uniquely decide whether the references already
require a declared invocation.

That gap blocks the first TLA+ safety model. The model must distinguish who
authorized an invocation, what execution context is the immediate caller, which
continuation is suspended, what workflow invocation is active, and where normal
completion returns. Reusing ADR-008's main-agent-selected transition for a
workflow-declared invocation would misattribute decision ownership. Adding a
generic declared-invocation transition without accepted semantics would create
product meaning inside a model. Issue #5 owns this decision, and the discovery
classification records the existence question as
`authority-conflict-or-uncertain` with a candidate derived-from-authority
derivation, and the exact transition semantics as `decision-required`.

## Decision

A TURNLOCK workflow program MAY declaratively invoke another TURNLOCK workflow
as part of its authored orchestration. The decision to invoke that workflow
belongs to the invoking workflow program, and TURNLOCK MUST execute an admitted
declared invocation directly rather than requiring a main-agent handoff solely
to reproduce an invocation decision already present in the executable topology.

For every admitted invocation, whether workflow-declared or agent-selected:

- the caller context preserves a structured call continuation;
- the calling continuation is suspended with respect to that call;
- the callee executes its own declared progression;
- normal completion returns to the same immediate caller context and enables
  only the caller's declared post-call continuation;
- the callee MUST NOT replace, rewrite, skip, or capture the caller's
  continuation or the enclosing workflow's declared progression;
- the enclosing workflow's orchestration remains governed by its own program.

Suspension is local to the calling continuation. An invocation MUST NOT be
interpreted as implicitly suspending concurrently active contexts that the
declared topology permits to continue. The local rule must not be generalized
into unconditional whole-workflow suspension.

The decision owners remain distinct. The workflow program owns a declared
invocation; the main agent owns an agent-selected invocation only during a
main-agent region where it legitimately holds local authority (ADR-008). ADR-008
remains valid and its accepted scenario is unchanged. The structural guarantees
above do not decide whether an implementation, model, primitive, action, or
runtime path is shared; that factorization is a modeling and architecture
choice, not product semantics.

This decision does not decide recursion, cyclic call graphs, or the
admissibility of invocation in restricted contexts. Issue #6 owns that
admissibility boundary, and an admitted invocation is one that existing
authority and that boundary permit. Concrete nesting depth, stack size,
resource budgets, and cancellation or failure behavior remain policy or
implementation concerns.

The canonical term remains `nested workflow invocation`. Its Section 2.8
definition is generalized to cover an invocation whose immediate caller is a
context inside an enclosing workflow, regardless of whether the workflow
program declared the invocation or the main agent selected it, while the
decision owner remains explicit. This decision introduces no parallel
terminology.

## Alternatives considered

- **Reject declared invocation and keep agent-selected nesting only:** Rejected
  because a known declared call would have to be reproduced through main-agent
  judgment, delegating a decision the workflow program already owns and
  contradicting `TL-INV-031` and ADR-014.
- **Execute a declared call as an internal main-agent handoff:** Rejected
  because it misattributes decision ownership and moves declared orchestration
  back into agent judgment.
- **Define invocation as unconditional whole-workflow suspension:** Rejected
  because it contradicts declared concurrency and fan-out/fan-in semantics
  (`TL-INV-024`, `TL-INV-027`, ADR-013).
- **Decide a shared primitive, model action, or runtime representation:**
  Rejected as a modeling and architecture choice that does not change product
  semantics.
- **Introduce a new general term instead of broadening `nested workflow
  invocation`:** Rejected because the existing canonical term already identifies
  the structural relation; broadening its definition removes the ambiguity with
  less terminology and traceability churn.
- **Decide recursion, cyclic admissibility, placements, and depth limits here:**
  Rejected as outside the smallest necessary semantic delta; Issue #6 owns
  admissibility and concrete limits remain policy.
- **Edit ADR-008's accepted body to broaden it:** Rejected because accepted
  decision bodies are immutable; this later ADR records the generalization while
  ADR-008 remains valid.

## Consequences

### Benefits

- Resolves the Section 2.8 definitional conflict and gives the first TLA+ safety
  model a decision-owner-neutral invocation transition with a defined caller and
  return structure.
- Keeps known composition decisions in executable workflow logic instead of
  returning them to agent judgment.
- Preserves ADR-008 unchanged while placing both invocation paths under the same
  applicable structural guarantees.
- Introduces no representation, primitive, or factorization obligation.

### Costs and obligations

- The normative specification must generalize the immediate-caller and nested
  invocation definitions, state the declared-invocation obligation, and carry it
  in a new stable invariant identity without broadening the published meanings
  of `TL-INV-016`–`TL-INV-019`.
- The terminology review inventory must be refreshed for moved definition-like
  occurrences.
- `formal/verification.yaml` may record intended properties only; no model, no
  TLC run, and no `checked` claim exist.
- The first model must scope recursion, cyclic, and restricted-placement behavior
  consistently with Issue #6 rather than enabling it accidentally.
- Conformance tests for the declared path and for local suspension under
  declared concurrency are required later but are not created by this decision.

## References

- `docs/specification/turnlock-spec.md`
- `docs/adr/adr-008-allow-nested-workflow-invocation-from-main-agent-regions.md`
- `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
- `docs/adr/adr-013-allow-heterogeneous-parallel-fan-out-across-execution-forms.md`
- `formal/verification.yaml`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
- GitHub Issues #5, #6, and #9
