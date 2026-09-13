---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Nest workflow execution inside the originating main-agent session lifecycle"
id: "ADR-006"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "3892cab7177cdd35f6527cfa385aaa37c6db1f1e1b3f9d2593a83c3c8bf71e5b"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-002"
    - "ADR-005"
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-006: Nest workflow execution inside the originating main-agent session lifecycle

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 006
- **Clarifies:** ADR-002 and ADR-005
- **Clarified by:** ADR-008

## Context

The desired sequence has both a beginning and an end in the same surrounding interaction:

```text
main agent
→ workflow
→ ...
→ workflow terminates
→ main agent
```

It is not sufficient for the session-local workflow invocation to launch an external automation that leaves the user stranded in a separate execution context when it completes. The workflow is meant to automate a bounded region **inside the user's ongoing coding session**.

## Decision

Ordinary TURNLOCK workflow execution is semantically nested inside the lifecycle of the originating main-agent session.

The main agent is:

1. the interactive context from which workflow entry occurs;
2. an execution participant during zero or more main-agent regions; and
3. the interactive context to which control returns after successful workflow termination.

Workflow termination is therefore a first-class control transition, not merely process exit.

The implementation mechanism used to realize return is intentionally unspecified.

## Rationale

TURNLOCK is intended to let users compile portions of their working method into executable process **without leaving the working relationship they already have with their coding agent**.

The workflow temporarily owns execution; it does not replace the session as the user's primary workspace.

## Consequences

- Entry and exit are both part of product conformance.
- A workflow runner that cannot return the user to the originating main-agent interaction is a weaker mode, not full TURNLOCK semantics.
- Completion/failure/cancellation semantics will eventually need to define where control returns and what state is visible there.
- The user's mental model remains one session containing a workflow episode, rather than several unrelated agent sessions.

## Alternatives considered

- **Treat workflow completion as the end of the coding-agent session:** rejected because the workflow is a bounded episode inside that session.
- **Return only a textual report to a newly launched agent:** rejected as the normal semantics because it reconstructs rather than continues the original interaction.
- **Require the user to manually resume the old session:** rejected as ordinary product behavior because return is part of the workflow lifecycle.

## Clarification by ADR-008

ADR-006 described the top-level lifecycle. ADR-008 generalizes the return rule for nested composition:

```text
workflow completion → immediate invocation context
```

For a top-level workflow, the immediate caller is the surrounding main-agent interaction described here. For a workflow invoked from a main-agent region of another workflow, completion returns to that region rather than jumping directly to the root session.
