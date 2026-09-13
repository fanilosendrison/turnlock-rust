# ADR-014: Define TURNLOCK as the orchestration engine and the workflow as the orchestration program

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 014
- **Governs:** Ownership of orchestration logic versus runtime execution authority
- **Clarifies:** ADR-001

## Context

Earlier TURNLOCK decisions repeatedly state that “the workflow owns orchestration.” That wording is correct at the level of decision ownership, but it can be misread as if the workflow artifact itself were the execution engine or as if TURNLOCK should be called the orchestrator that makes global decisions.

The current product model is richer: a workflow may sequence and parallelize mechanical computation, raw LLM calls, independent agents, main-agent continuations, and nested workflows. Something must execute that graph, maintain workflow progression, coordinate fan-out/fan-in, perform harness handoffs, and resume suspended continuations. That execution authority is TURNLOCK.

At the same time, TURNLOCK exists specifically to move reusable orchestration decisions out of agent improvisation and into executable workflow logic. Allowing the runtime itself to invent undeclared strategy would recreate a hidden decision-maker and blur the product boundary.

## Decision

TURNLOCK is the **orchestration engine/runtime**. The workflow artifact is the **orchestration program** and source of truth for the declared global orchestration logic.

Normatively:

```text
developer or coding agent
  → authors
workflow program
  → declares orchestration decisions / topology
TURNLOCK engine
  → executes, coordinates, and tracks that declared orchestration
execution resources
  → perform bounded regions
```

TURNLOCK MUST provide sufficient execution authority to realize declared workflow semantics, including sequencing, state tracking, branching, iteration, concurrency, fan-out/fan-in, nested invocation, structured return, raw LLM calls, independent-agent execution, and main-agent continuation where those primitives are present.

TURNLOCK MUST NOT silently invent undeclared global workflow strategy merely because it is the runtime. In particular, unless a future explicit workflow semantic grants policy authority, the engine does not independently decide:

- how many semantic workers should exist when the workflow has declared a different topology;
- whether a declared raw LLM call should become an independent agent or main-agent handoff;
- whether a declared workflow phase should be skipped or replaced;
- which undeclared phase should execute next;
- how the global workflow should be re-planned.

The compact rule is:

> **TURNLOCK executes orchestration; it does not invent it.**

## Rationale

This distinction preserves both halves of the product. TURNLOCK must be powerful enough to execute complex deterministic orchestration, but the authored workflow must remain the place where known control decisions live. Otherwise the product would drift either toward a passive library with no runtime authority or toward an agentic/policy orchestrator that reintroduces hidden decision-making.

The phrase “workflow owns orchestration” therefore means **ownership of orchestration decisions and declared control flow**, while TURNLOCK owns **execution machinery and runtime progression**.

## Consequences

- TURNLOCK may legitimately be called an orchestration engine or runtime.
- In broad industry language TURNLOCK may sometimes be called an orchestrator, but normative documents must distinguish runtime execution from orchestration decision ownership.
- Workflow artifacts remain the source of truth for declared topology and progression semantics.
- Runtime scheduling, state tracking, branch coordination, and harness translation are TURNLOCK responsibilities.
- Runtime optimizations may choose equivalent mechanisms but may not change workflow meaning.
- Future adaptive/policy-driven orchestration, if ever desired, must be introduced as an explicit primitive or separately governed capability rather than emerging implicitly inside the engine.

## Alternatives considered

- **Call TURNLOCK itself the global orchestration decision-maker:** rejected because it obscures where workflow policy lives and opens the door to undeclared runtime strategy.
- **Treat the workflow artifact as if it literally executes itself:** rejected because real runtime authority is required for state, scheduling, concurrency, harness integration, and handoffs.
- **Let the main agent remain the real orchestrator behind the runtime:** rejected by ADR-001 because it recreates the original problem.

## Verification obligation

For any implementation decision, it must be possible to answer separately:

1. What orchestration decision was declared by the workflow?
2. What execution mechanism did TURNLOCK use to realize it?
3. Did the runtime preserve the declared topology and semantics?
4. Did any runtime component invent a new global decision that was not authorized by workflow semantics?

A conforming implementation must keep those answers distinguishable.
