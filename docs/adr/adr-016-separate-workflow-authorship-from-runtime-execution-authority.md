# ADR-016: Separate workflow authorship from runtime execution authority

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 016
- **Clarifies:** ADR-009 and ADR-014
- **Governs:** Relationship between workflow authorship and runtime
  orchestration authority

## Context

ADR-009 establishes that developers and coding agents author the same semantic
workflow artifact through the same TURNLOCK primitives. ADR-014 establishes the
workflow artifact as the source of declared orchestration decisions and
TURNLOCK as the engine that executes, coordinates, and tracks them.

Those decisions compose cleanly, but they leave a provenance-specific ambiguity
without its own stable invariant. When a coding agent, LLM planner, or
higher-level system generates a workflow dynamically, an implementation could
retain that author as a hidden scheduler, treat the generated graph as advisory
prose, and still claim to support agent-authored workflows.

That interpretation would recreate the problem TURNLOCK exists to prevent:
workflow progression would depend on an agent remembering, interpreting, and
scheduling the process rather than on execution of the workflow artifact.

## Decision

The identity or nature of a workflow's author MUST NOT, by itself, confer
runtime orchestration authority over that workflow.

A developer, coding agent, LLM planner, or higher-level system MAY author or
generate a workflow with any topology expressible through supported TURNLOCK
primitives. Once execution begins:

```text
workflow artifact
  = source of truth for declared orchestration

TURNLOCK
  = engine that executes, coordinates, and tracks that orchestration

workflow author
  != implicit runtime scheduler
```

An agent-authored or dynamically generated workflow MUST remain an independently
represented executable artifact. It MUST NOT silently degrade into prose or
instructions that its author must remember, interpret, or schedule during
execution.

Authorship does not prevent an author that is also available under an existing
execution form from later participating through a declared workflow region. In
particular, when the author is the existing main coding agent, the workflow MAY
invoke that same cognitive lineage through a declared main-agent region:

```text
main agent authors workflow G
  → TURNLOCK executes G
  → G enters a declared main-agent region
  → same main agent owns bounded local execution
  → region completes
  → G resumes declared global progression
```

The main agent's local authority in that region follows from the workflow's
explicit execution semantics, not from having authored G. The workflow may
likewise invoke raw LLM inference or independent agents wherever its declared
topology uses those execution forms.

This decision constrains authority semantics only. It does not select an
authoring syntax, dynamic-planning API, scheduler, process model, persistence
mechanism, or harness integration mechanism.

## Rationale

TURNLOCK allows cognition to author programs and allows programs to call
cognition. Those capabilities remain compatible only if authorship and runtime
execution authority stay independent.

The compact rule is:

```text
authorship of workflow
!=
ownership of workflow execution
```

A stable invariant for this boundary prevents dynamic generation from becoming
a privileged path back to prompt-driven orchestration. It also preserves the
useful case in which the main agent authors a workflow and later participates
inside that workflow without becoming its global scheduler.

## Consequences

- Developer-authored, coding-agent-authored, planner-generated, and
  higher-level-system-generated workflows retain the same runtime authority
  model.
- Author provenance alone cannot authorize an agent to advance, replace, or
  reinterpret declared global workflow progression.
- Generated workflows require an independently represented executable artifact;
  advisory prose whose correctness depends on author recollection is
  non-conformant.
- An author that is also available under an existing execution form may receive
  local authority through an explicitly declared region, including continuation
  of the same main-agent lineage.
- `TL-INV-020` remains limited to same-artifact authoring. The new
  authorship/execution-authority invariant has a separate identity and
  responsibility.
- Future conformance suites must test that workflows execute independently of
  whether a developer, coding agent, planner, or higher-level system authored
  them.

## Alternatives considered

### Rely only on ADR-009 and ADR-014 by implication

Rejected. Their composition suggests the desired boundary, but it does not give
the provenance-specific obligation a stable identity for implementation,
conformance, and traceability.

### Extend the meaning of the same-artifact authoring invariant

Rejected. Artifact-class equivalence and runtime-authority separation are
independent obligations. Overloading `TL-INV-020` would weaken both concepts and
violate the stability of its published meaning.

### Retain an authoring agent as the normal workflow interpreter

Rejected. Treating the workflow as advice to its author leaves actual ordering,
progression, and completion dependent on agent interpretation and violates
workflow-owned orchestration.

### Add author provenance to the core TLA+ model solely for this invariant

Rejected. The distinct concern is whether real authoring and runtime paths
preserve the architecture boundary. That is an implementation/API conformance
question. Existing formally applicable control invariants already cover the
state-machine consequences of hidden agent orchestration. This decision does
not prevent a future formal model from representing provenance if another
accepted semantic need requires it.

## Verification obligation

A conforming implementation must demonstrate all of the following authoring
paths with the same execution-authority semantics:

```text
developer writes G → TURNLOCK executes G
coding agent writes G → TURNLOCK executes G
planner dynamically generates G → TURNLOCK executes G
higher-level system synthesizes G → TURNLOCK executes G
```

For an agent-authored workflow, conformance must show that:

1. G is represented independently of the author's conversational recollection;
2. TURNLOCK can determine and execute G's declared progression without asking
   the author what step comes next;
3. the author cannot advance or replace global progression solely because it
   authored G; and
4. G may later invoke that same main agent through an explicit main-agent
   region, after which G resumes its declared continuation.

The following shape is conformant:

```text
main agent
  → generates workflow G
  → TURNLOCK begins executing G
  → mechanical step
  → G invokes main-agent continuation
  → same main agent performs bounded local work
  → G resumes
```

The same agent appears as both author and later execution resource, but neither
role grants implicit ownership of G's runtime progression.
