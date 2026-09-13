---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Preserve main-agent cognitive lineage and ordinary interactive agency"
id: "ADR-007"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "005a611031097a6dd7e6c65e47e34e2a97a4cef6b150a5312a27c0159e407740"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-005"
    - "ADR-006"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "semantic difference between a main-agent step and a spawned independent agent"
---

# ADR-007: Preserve main-agent cognitive lineage and ordinary interactive agency

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 007
- **Clarifies:** ADR-005 and ADR-006
- **Governs:** semantic difference between a main-agent step and a spawned independent agent
- **Clarified by:** ADR-008

## Context

After establishing reversible main-agent handoffs, the key challenge became: **what does returning to the main agent actually provide that spawning a fresh agent does not?**

A fresh agent can often use the same model, repository, tools, and a prompt containing selected session context. If that were semantically equivalent, requiring a main-agent handoff would be unnecessary complexity.

The important difference is that the current main agent is an ongoing agentic lineage embedded in the user's interactive session. It may have accumulated prior discussion, corrections, repository understanding, tool results, assumptions, permissions, and the direct interaction channel with the user.

Spawning a new independent agent introduces a reconstruction and synchronization boundary:

```text
main before spawn:       A B C D E
                             |
                             +--> child gets A B C
                                     + learns F G H

main afterwards:         A B C D E
child lineage:           A B C F G H
```

The system must then reconcile what the child learned back into the main session through a summary, patch, artifact, result object, or another lossy/explicit handoff.

TURNLOCK instead seeks:

```text
main lineage A B C D E
        ↓
workflow episode
        ↓
main lineage continues and learns F G H
        ↓
workflow resumes
```

There is a second distinction. The main coding agent is not merely a model endpoint. During its ordinary session it can reason, inspect, edit, call tools, react to tool output, change direction, and interact with the user. Reducing a main-agent region to `AI(prompt) -> result` can discard exactly the interactive agency TURNLOCK is trying to preserve.

## Decision

A TURNLOCK **main-agent step** means continuation of the current main-agent cognitive lineage and restoration of the ordinary class of interactive coding-agent agency required by that region.

Therefore:

```text
main-agent step != arbitrary fresh completion
main-agent step != independent spawned agent by default
main-agent step != context-reconstructed child presented as equivalent
main-agent step != necessarily one-shot request/response AI call
```

Crossing a workflow boundary MUST NOT create a new cognitive lineage merely because execution temporarily becomes agentic.

A spawned/subagent capability may exist separately and may be useful, but it MUST be named as a different semantic capability unless the harness can establish continuation semantics equivalent to the current main-agent lineage.

This decision does **not** require literal same-process identity. A future mechanism may satisfy the ADR through session continuation, suspension/resumption, state-preserving migration, or another technique if it preserves the semantic continuity defined here.

During a main-agent region, TURNLOCK MUST NOT unnecessarily reimplement or narrow the coding agent's normal operating loop. The workflow owns the boundary and continuation; the agent may use its native capabilities and user interaction inside that boundary, subject to future explicit authority/completion rules.

## Rationale

TURNLOCK combines:

```text
determinism outside agentic regions
+
ordinary coding-agent agency inside agentic regions
```

The user gets executable workflow control without paying a context-export/import tax every time the workflow needs judgment.

This is the strongest reason for reversible **main-agent** handoff rather than merely adding an `agent()` function to a workflow engine.

## Consequences

- Harness conformance must be evaluated on continuity semantics, not only on whether an API can launch an agent.
- Same model/repository/tools are insufficient proof of same-main-agent semantics.
- Subagent spawning remains a potentially useful additional feature but is not a substitute for main-agent handoff.
- A harness that cannot preserve this lineage may support a weaker execution tier, but that limitation must be explicit.
- TURNLOCK should avoid implementing its own mini coding-agent loop merely to simulate what the harness already provides during the main-agent region.
- User interaction during a main-agent region becomes a legitimate capability to specify rather than an anomaly.

## Alternatives considered

### Treat a spawned agent with copied context as equivalent

Rejected. It creates a new cognitive lineage and requires explicit context reconstruction and later reconciliation. The copied context can be excellent and still be a different state trajectory.

### Require the exact same OS process

Rejected as an invariant. Process identity is a possible mechanism, not the semantic requirement. A harness may provide equivalent continuation through another mechanism.

### Reduce main-agent regions to one-shot LLM calls

Rejected. It unnecessarily discards the interactive coding-agent loop, tools, iterative reasoning, and user interaction that motivate using the main agent.

### Always prefer the main agent and forbid subagents

Rejected. TURNLOCK may later expose separate spawned-agent primitives. The decision only prevents those primitives from being mislabeled as equivalent to a main-agent handoff.

## Verification obligation

Any claimed harness implementation of a main-agent step must answer, with testable behavior rather than naming alone:

1. What state/lineage is continuous across workflow entry and each main-agent region?
2. Does agentic work in the region become part of the same continuing session seen after the workflow ends?
3. Can the agent use the ordinary harness capabilities required by the region rather than only return one completion?
4. Does the workflow resume without needing to summarize/reconstruct the entire agentic episode as a separate child-agent result?

If these are not true, the integration may still be valuable, but it is not full main-agent-handoff semantics.

## Clarification by ADR-008

The ordinary interactive agency restored by a main-agent region includes the ability to invoke TURNLOCK workflows that are available to the coding-agent session. Using that capability creates a structured nested workflow invocation; it does not transfer orchestration ownership of the enclosing workflow to the main agent.
