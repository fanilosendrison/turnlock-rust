# ADR-013: Allow heterogeneous parallel fan-out across execution forms

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 013

## Context

ADR-011 established workflow-owned parallel independent-agent execution, including multiple agents performing either the same task or different tasks. ADR-012 established the same property for bounded raw LLM inference.

Those decisions could still be interpreted too narrowly as two separate homogeneous forms of parallelism: one subagent fan-out or one raw-LLM fan-out. That would unnecessarily constrain the deterministic orchestrator.

A workflow may know in advance that an independent region contains different kinds of work at the same time: deterministic computation, cheap bounded inference, and richer autonomous delegation. Requiring those branches to be serialized or split into artificial homogeneous phases would reduce expressiveness without improving orchestration semantics.

## Decision

TURNLOCK MUST support **heterogeneous workflow-owned parallel fan-out/fan-in**.

A single declared parallel region MAY contain independent branches using different execution forms, including:

```text
mechanical computation
raw LLM inference
independent-agent execution
```

Within the same fan-out:

- multiple raw LLM branches MAY perform the same task or different tasks;
- multiple independent-agent branches MAY perform the same task or different tasks;
- mechanical, raw-LLM, and independent-agent branches MAY coexist;
- each branch MUST retain the lifecycle, context, authority, and result semantics of its own execution form;
- the workflow MUST own branch creation, synchronization, result collection, and the declared continuation after join.

For example:

```text
fan-out
  ├→ mechanical static analysis
  ├→ LLM classification A
  ├→ LLM classification B
  ├→ independent security reviewer
  └→ independent compatibility reviewer
join
→ aggregate
→ continue
```

This ADR does not decide that main-agent continuation is an ordinary concurrent branch. Main-agent continuation preserves a unique interactive cognitive lineage and has distinct control semantics; concurrency involving it requires a separate decision.

## Rationale

TURNLOCK deliberately trades away some decision-time flexibility of an agentic orchestrator in exchange for explicit workflow-owned control. That trade only works if the deterministic orchestration surface is sufficiently expressive.

Homogeneous-only parallelism would force authors to reshape naturally concurrent work around implementation categories rather than around true dependency boundaries. Heterogeneous fan-out lets the workflow express the actual graph directly.

It also enables deliberate cognitive economics inside one region: deterministic code for exact work, bounded LLM calls for cheap semantic transforms, and independent agents for tasks requiring autonomous multi-turn execution.

## Consequences

- Parallelism is a general workflow-control capability, not a feature tied to one semantic leaf type.
- The runtime must track branches with different lifecycle and result contracts in the same fan-out.
- Join semantics must not erase the distinction between branch types.
- Observability, budgeting, cancellation, and failure handling will eventually need to work across heterogeneous branches.
- Main-agent concurrency remains intentionally unresolved by this ADR.

## Alternatives considered

### Support only homogeneous fan-out

Rejected. It would make authors split otherwise independent work into artificial phases and reduce the expressive power of deterministic orchestration.

### Delegate mixed parallelism to the main agent

Rejected. When the graph is known in advance, asking the main agent to construct and synchronize it moves declared orchestration back into agent judgment.

### Treat every branch as one generic AI task

Rejected. Mechanical computation, raw LLM inference, and independent-agent execution have intentionally different lifecycle, context, cost, authority, and result semantics.

## Verification obligation

A conforming implementation must demonstrate one parallel region containing at least:

```text
1 mechanical branch
2 raw LLM branches
2 independent-agent branches
```

with at least one repeated same-task pair and at least one different-task pair across the semantic branches. The workflow must join the branches and continue without transferring fan-out/fan-in ownership to the main agent.

The implementation must also show that branch-specific semantics remain observable after the join rather than collapsing all branches into one generic execution type.
