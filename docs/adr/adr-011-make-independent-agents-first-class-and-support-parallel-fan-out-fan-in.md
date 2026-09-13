---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Make independent agents first-class workflow resources and support workflow-owned parallel fan-out/fan-in"
id: "ADR-011"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "4f5d5bf1103fc5361913e1d755c0430ff5580eaaaf43db9598b5e04eec5c45fa"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-011: Make independent agents first-class workflow resources and support workflow-owned parallel fan-out/fan-in

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 011

## Context

TURNLOCK originally established why a main-agent handoff cannot be treated as equivalent to spawning a fresh agent: the main-agent capability exists to preserve the current interactive cognitive lineage and ordinary coding-agent agency.

That distinction does not imply that fresh independent agents are undesirable. Some semantic tasks are better served by a deliberately new cognitive lineage whose mission and context are more tightly bounded than the main session. Bounded delegation can reduce irrelevant context, avoid polluting the main-agent lineage with intermediate exploration, constrain cost, and improve task focus.

There are also workflows where the topology itself requires multiple independent agents. They may all perform the same task to obtain independent attempts, reviews, or judgments, or they may perform different tasks as a decomposition. These branches may be able to execute in parallel.

If the workflow already knows that this fan-out/fan-in is required, forcing a handoff to the main agent merely so the main agent can create and synchronize subagents would move known orchestration back into agent judgment. That contradicts TURNLOCK's core purpose.

More generally, choosing a deterministic orchestrator reduces decision-time flexibility compared with an agentic orchestrator. To make that trade useful, the deterministic orchestration surface must remain broad enough to express rich execution topologies directly.

## Decision

TURNLOCK MUST support **independent-agent execution as a first-class workflow capability** distinct from main-agent continuation.

An independent-agent step creates a new bounded cognitive lineage for a declared task, allows autonomous multi-turn work within the capabilities granted to that task, and returns a result to workflow-owned progression.

Conceptually:

```text
bounded task/context
→ independent agentic execution
→ result
→ workflow continuation
```

TURNLOCK MUST also support **workflow-owned parallel fan-out/fan-in** of independent semantic work. Parallel branches MAY:

```text
perform the same task
→ independent attempts / diversity / redundancy

or

perform different tasks
→ decomposition / specialization
```

When fan-out, synchronization, collection, and continuation are declared by the workflow, those decisions remain owned by the workflow rather than by the main agent.

Independent-agent branches MUST also be composable in the same parallel region with other independent TURNLOCK execution forms such as mechanical computation and bounded raw LLM inference. Parallel composition is therefore not restricted to homogeneous subagent-only fan-out.

Independent agents MUST be conceptually capable of receiving task-specific bounded context rather than inheriting the entire main-agent cognitive lineage by default merely because they originated from the same session.

This ADR does not fix the concrete spawn API, agent runtime, model, context representation, tool grant mechanism, concurrency implementation, result type, retry behavior, or budget controls.

## Rationale

Independent agents and main-agent continuation solve different problems:

```text
main-agent continuation
= preserve the current cognitive lineage and ordinary session agency

independent agent
= intentionally create a bounded new cognitive lineage
```

The cognitive fork rejected as an implementation of a main-agent step becomes a useful feature when isolation is the actual intent.

First-class independent agents also allow deterministic workflows to retain ownership of known orchestration structures. A workflow such as:

```text
spawn 3 independent reviewers
→ wait for all
→ aggregate results
→ main agent fixes selected findings
```

should not need to become:

```text
main agent, please create and coordinate 3 reviewers
```

merely because the branches require model intelligence.

Parallelism further makes this distinction product-significant. The workflow can define semantic concurrency explicitly rather than relying on the main agent to discover and schedule it dynamically.

## Consequences

- TURNLOCK has at least two distinct agentic execution forms: independent bounded agency and continuation of the main agent.
- A fresh subagent is no longer merely a possible adjacent feature; it is required by the workflow model.
- The runtime must preserve a distinction between local autonomous execution inside a subagent and global workflow progression authority.
- Workflow authors can deliberately use cognitive isolation rather than treating context inheritance as automatic.
- Parallel semantic work becomes part of workflow orchestration rather than a main-agent-only capability.
- The implementation will eventually need explicit semantics for concurrency, join, failure, cancellation, context construction, capabilities, and resource budgets.
- TURNLOCK should prefer a small orthogonal orchestration surface with broad expressive power over a large catalog of narrow domain-specific commands.

## Alternatives considered

### Let only the main agent spawn subagents

Rejected. This remains useful inside a main-agent region when delegation is an agentic decision, but it is insufficient when the workflow itself declares that specific independent agents and their synchronization are part of the control graph.

### Treat spawned agents as equivalent to main-agent steps

Rejected. It erases the product distinction between continuation of an existing cognitive lineage and intentional creation of a new one.

### Keep semantic execution sequential

Rejected. Parallel independent work is a primary use case for bounded agents and is required for explicit diversity, redundancy, and decomposed semantic work.

### Require independent agents to inherit the full main-agent context

Rejected as a product invariant. It would destroy much of the value of bounded delegation and unnecessarily couple independent semantic tasks to accumulated session context.

## Verification obligation

A conforming implementation must demonstrate at least:

```text
workflow
→ start agents A, B, C on the same bounded task concurrently
→ join/collect A, B, C
→ continue without asking the main agent to schedule them
```

and:

```text
workflow
→ start agent A for task X
→ start agent B for task Y
→ execute A and B concurrently
→ join/collect both
→ continue at the workflow-declared next region
```

It must also show that these independent-agent executions are not presented as preserving the main-agent cognitive lineage.
