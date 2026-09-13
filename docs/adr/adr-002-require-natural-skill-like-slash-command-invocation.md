---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Require natural skill-like slash-command invocation inside coding-agent sessions"
id: "ADR-002"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "55edf8cddb7a4c6fcfb350f4d4627d7af16f26390dfa6aff7b29f9e33eee7fae"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-001"
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-002: Require natural skill-like slash-command invocation inside coding-agent sessions

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 002
- **Clarifies:** ADR-001
- **Clarified by:** ADR-008

## Context

The motivating examples used `/go` to illustrate invocation. That example was not intended to define a canonical TURNLOCK command. The product requirement is that a user already working inside Claude Code, Pi, Codex, or another supported coding-agent harness can invoke a TURNLOCK workflow **naturally from that session, through the same kind of slash-command interaction used to invoke skills or native session commands**.

If invocation instead requires leaving the coding session, operating a separate workflow UI, or manually running an external shell protocol as the normal path, TURNLOCK stops feeling like part of the coding-agent working environment. Conversely, if the slash command merely expands into a long prompt and asks the main agent to remember and execute the workflow, ADR-001 is violated because orchestration remains agent-owned.

## Decision

For supported coding-agent harnesses, TURNLOCK workflows MUST have a **session-local, natural slash-command invocation surface with skill-like ergonomics**.

The exact command name is not normative. `/go` was only an example. This ADR does not decide whether TURNLOCK uses:

```text
one generic TURNLOCK slash command
workflow-specific slash commands
harness-native skill/command registration
a namespace of TURNLOCK commands
another equivalent slash-command mapping
```

Those are implementation/interface-design choices as long as the ordinary product experience preserves the same invariant:

```text
user is already in the coding-agent session
  → invokes the desired TURNLOCK workflow as naturally as a skill
  → workflow-owned execution begins
```

The invocation surface MUST remain thin in orchestration responsibility. It may select, parameterize, or start a workflow, but it MUST NOT turn the main agent into the interpreter responsible for remembering and sequencing the workflow.

## Rationale

TURNLOCK is intended to let users turn parts of their working method into executable control flow **without leaving the coding session where that work is happening**. Skill-like slash invocation keeps workflow execution inside the user's existing interaction model and avoids adding a separate orchestration product to the normal loop.

Separating the invariant from the literal command name also prevents a temporary example (`/go`) from hardening into product architecture.

## Consequences

- `/go` has no normative status; it remains only a historical example from the product discussion.
- A supported harness integration must expose workflow invocation through a natural slash-command experience or an interaction that is product-equivalent to native skill invocation.
- The concrete command name, namespace, and workflow-selection mapping may differ across harnesses.
- The ordinary user does not need to leave the active coding-agent session merely to launch a workflow.
- A slash command that only injects the whole workflow as prose into the main-agent prompt is non-conformant.

## Alternatives considered

- **Standardize TURNLOCK on `/go`:** rejected because the string was only an example and carries no product-level meaning.
- **Use any arbitrary entry mechanism, including an external shell/UI:** rejected for the ordinary supported-harness experience because it loses the desired native, skill-like session interaction.
- **Encode the entire workflow inside a slash-command prompt expansion:** rejected because the main agent remains the workflow orchestrator.
- **Bind TURNLOCK to one vendor's specific slash-command implementation:** rejected because the user-facing interaction is normative, while the harness-specific realization is not.

## Verification obligation

For each supported coding-agent harness, product conformance must demonstrate that a user can select and start a TURNLOCK workflow from the active session through a natural slash-command interaction comparable to invoking a skill, without requiring the main agent to interpret the workflow's remaining control flow.
