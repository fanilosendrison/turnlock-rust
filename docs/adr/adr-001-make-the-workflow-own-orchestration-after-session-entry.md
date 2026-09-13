---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Make the workflow own orchestration after session entry"
id: "ADR-001"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "1302d2ce1b7c79b47a56938c6ee42ae93b50a88a62d8c9543434cd9e3638ed8f"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs:
  - "TURNLOCK product definition and execution ownership"
---

# ADR-001: Make the workflow own orchestration after session entry

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 001
- **Governs:** TURNLOCK product definition and execution ownership
- **Clarified by:** ADR-014

## Context

The originating problem was stated from inside an existing coding-agent session: the user wants to invoke a workflow through a natural slash command in the coding-agent session (the discussion used `/go` only as an example), have that invocation launch a script/workflow, and have the workflow later be able to use the main agent again.

The important requirement is not merely that a script can call an LLM. The user wants to **build and execute workflows directly from the coding-agent session without making the main agent responsible for remembering and orchestrating those workflows**.

Encoding the workflow as a long skill or prompt would leave the effective control flow inside the model:

```text
user
→ main agent
→ agent interprets step 1
→ agent decides to run step 2
→ agent remembers step 3
→ ...
```

That does not solve the product problem because the reusable procedure still depends on agent interpretation for ordering and progression.

## Decision

After a TURNLOCK workflow is entered, **the workflow program owns the declared global orchestration logic until it terminates; TURNLOCK is the runtime that executes and tracks that logic**.

The main agent may participate in explicitly agentic regions, but it is not the authority that decides or remembers the global workflow progression.

Conceptually:

```text
main agent
  → workflow entry
  → workflow owns execution
       ├─ mechanical region
       ├─ main-agent region
       ├─ mechanical region
       └─ ...
  → workflow terminates
  → main agent
```

The workflow must retain enough execution truth to know where it is and what comes next independently of the main agent's conversational memory.

## Rationale

TURNLOCK exists to move reusable process semantics out of model recollection and into executable control flow. This allows the user to encode a working method as a program while retaining the main agent only where judgment is actually useful.

The architectural separation is:

```text
orchestration authority != agentic execution capability
```

## Consequences

- Workflow progression cannot depend on the main agent remembering the remaining procedure.
- Agentic phases are subordinate regions inside a larger workflow execution, not owners of the workflow itself.
- Mechanical steps can remain deterministic even when surrounding agentic behavior is flexible.
- TURNLOCK requires an execution notion distinct from the main agent's chat history.
- A solution that merely expands the workflow slash command into a long instruction for the main agent is non-conformant.

## Alternatives considered

- **Keep orchestration in the main agent via a large skill/prompt:** rejected because it preserves the original failure mode.
- **Make every step a subagent call:** rejected as the product definition because it replaces orchestration by the main agent with orchestration by an agent-call graph rather than establishing first-class workflow-owned execution.
- **Use an external workflow that never returns to the main agent:** rejected because agentic work inside the user's ongoing coding session is a core requirement.
