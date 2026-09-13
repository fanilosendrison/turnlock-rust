# ADR-004: Make mechanical steps first-class and non-agent-mediated

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 004
- **Clarifies:** ADR-001

## Context

The desired workflow explicitly alternates between **mechanical steps** and **main-agent steps**.

The reason to move orchestration outside the main agent is partly to stop asking a probabilistic model to interpret and execute steps whose semantics are already known. If a mechanical step remains a prose instruction that the agent may choose to execute, the workflow has not actually gained deterministic control.

## Decision

TURNLOCK treats a mechanical step as a first-class workflow region whose execution does **not** depend on the main agent interpreting, remembering, or deciding to perform it.

Conceptually:

```text
workflow owns control
  → mechanical step executes according to workflow semantics
  → result/state becomes available to later workflow progression
```

The exact set of mechanical primitives is intentionally unspecified. The invariant is about execution authority, not the eventual DSL or runtime API.

## Rationale

Mechanical execution is the reliability half of TURNLOCK's product value. The system should use agentic judgment only where judgment is needed, while known procedure is executed as procedure.

This allows a user's process to become progressively more deterministic as its invariants become understood.

## Consequences

- A mechanical step cannot merely be "ask the main agent to run command X" if correctness depends on X actually running.
- Workflow state/results must be representable outside the main agent's memory.
- Agentic steps may consume mechanical outputs, but they do not become the source of truth for whether the mechanical step occurred.
- The product can support mixed deterministic/agentic workflows without forcing either mode to simulate the other.

## Alternatives considered

- **Represent every step as natural-language instructions to the main agent:** rejected because it preserves prompt-driven orchestration.
- **Make everything deterministic and forbid agentic regions:** rejected because coding work often requires open-ended judgment.
