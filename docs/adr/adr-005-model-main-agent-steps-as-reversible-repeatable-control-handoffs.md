---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Model main-agent steps as reversible, repeatable control handoffs"
id: "ADR-005"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "f4fc8fad47bd6237940d4f4212424471c1337a23ac55ccefde99ee0793b70536"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-001"
    - "ADR-004"
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-005: Model main-agent steps as reversible, repeatable control handoffs

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 005
- **Clarifies:** ADR-001 and ADR-004

## Context

The product sequence was refined to make clear that a main-agent phase is not the end of workflow execution. After the main agent has "taken back control", the workflow must be able to resume mechanical execution, and this alternation may occur repeatedly.

The reference shape is:

```text
main agent
→ natural slash-command workflow invocation
→ workflow
→ mechanical
→ main agent
→ mechanical
→ main agent
→ mechanical
→ workflow ends
→ main agent
```

A conventional `workflow -> agent(prompt) -> result` abstraction can model some of this, but TURNLOCK's intended semantics are specifically a **temporary transfer of local execution authority** followed by return to the surrounding workflow.

## Decision

A main-agent step is a **reversible control handoff** inside an active workflow.

When the workflow reaches such a step:

```text
workflow owns global progression
  → workflow suspends local execution
  → main agent owns the agentic region
  → agentic region completes/yields
  → workflow resumes at the defined continuation
```

This handoff MAY occur any number of times in one workflow.

A handoff MUST NOT implicitly terminate the workflow, and the workflow MUST NOT require the main agent to reconstruct which step comes next from conversational memory.

## Rationale

This is the core composition primitive that lets TURNLOCK place deterministic code around unconstrained coding-agent work.

The workflow controls **when** the agent is active; the main agent controls the open-ended work inside that region; then workflow control resumes.

## Consequences

- Workflow execution requires an explicit notion of suspension and continuation around agentic regions.
- The completion/yield condition of a main-agent phase becomes a critical future design question.
- Multiple mechanical↔agentic transitions are normal, not nesting edge cases.
- A design that can invoke an agent only once and then exits does not satisfy this ADR.

## Alternatives considered

- **Call the main agent only at the end of the workflow:** rejected because workflows need multiple agentic islands.
- **Let the main agent continue orchestrating after first handoff:** rejected because global control would leak back from workflow to agent.
- **Restart the workflow manually after each agent phase:** rejected because it destroys reversible handoff semantics.

## Verification obligation

A conforming prototype must demonstrate at least:

```text
mechanical A
→ main-agent region 1
→ mechanical B
→ main-agent region 2
→ mechanical C
```

without requiring the user or main agent to manually select the next workflow step.
