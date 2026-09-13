---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Allow nested workflow invocation from main-agent regions and return to the immediate caller"
id: "ADR-008"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "e8fdad50f7ed0ad5f1fed0b9aa70b14e51407225125a4429281516ab3a9030d8"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-002"
    - "ADR-005"
    - "ADR-006"
    - "ADR-007"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "workflow composability, nested invocation, suspension, and return semantics"
---

# ADR-008: Allow nested workflow invocation from main-agent regions and return to the immediate caller

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 008
- **Clarifies:** ADR-002, ADR-005, ADR-006, and ADR-007
- **Governs:** workflow composability, nested invocation, suspension, and return semantics

## Context

ADR-002 established that TURNLOCK workflows are exposed naturally inside the coding-agent session through a skill-like slash-command surface. ADR-007 established that a main-agent region restores the ordinary interactive agency of the current main coding agent rather than reducing it to a one-shot model call.

Those two decisions combine into a further product consequence: **while a workflow has handed control to the main agent, the main agent still has the session capabilities it ordinarily has, including the ability to invoke another TURNLOCK workflow that is available to that session.**

The motivating coding-agent environments commonly make session skills/commands discoverable to the main agent for the lifetime of the session. TURNLOCK must not accidentally erase that capability merely because the agent currently owns control inside a workflow handoff.

Therefore the following sequence must be meaningful:

```text
main agent
  → workflow A
    → mechanical A1
    → main-agent region A
      → workflow B
        → mechanical B1
        → main-agent region B
        → mechanical B2
        → workflow B terminates
      → main-agent region A resumes
    → mechanical A2
    → workflow A terminates
  → main agent resumes
```

Without an explicit decision, several incompatible semantics are possible:

```text
nested invocation forbidden
nested invocation replaces workflow A
workflow B returns directly to the root main session
workflow B completion implicitly completes main-agent region A
workflow B completion implicitly completes workflow A
```

Those semantics would break composability and weaken the meaning of restored ordinary main-agent agency.

## Decision

TURNLOCK permits **structured nested workflow invocation from a main-agent region**.

Whenever the main agent owns control, a TURNLOCK workflow that is available to that coding-agent session MAY be invoked, including when the current main-agent control was reached through a handoff from an enclosing workflow.

A nested invocation has these semantics:

```text
1. the immediate caller is suspended;
2. the nested workflow becomes the active workflow execution;
3. the nested workflow owns its own declared progression;
4. normal nested completion returns to the immediate caller;
5. the caller resumes from the point after the nested invocation;
6. the enclosing workflow remains suspended until its own main-agent region completes;
7. the enclosing workflow then resumes at its own declared continuation.
```

The general return rule is therefore:

```text
workflow completion → immediate invocation context
```

not:

```text
workflow completion → root main-agent session unconditionally
```

For a top-level workflow, the immediate invocation context is the surrounding main-agent interaction, so the existing top-level lifecycle remains:

```text
main agent → workflow A → main agent
```

For a nested workflow:

```text
main-agent region A → workflow B → main-agent region A
```

Nested workflows therefore form a structured caller stack conceptually:

```text
main session
  workflow A
    main-agent region A
      workflow B
        main-agent region B
          workflow C
        ←
      ←
    ←
  ←
main session
```

This ADR does not require a literal process stack, recursive process spawning, or any specific runtime representation. It requires equivalent **structured suspension and immediate-caller return semantics**.

The semantic model MUST NOT assume that only one nesting level can exist. An implementation may later define explicit resource or safety limits on accepted nesting depth, but such limits must not change the return semantics of invocations it accepts.

## Rationale

A workflow exposed as a skill-like session capability should remain usable wherever the main agent has ordinary agency. Otherwise TURNLOCK would restore the main agent only partially: the agent could reason, edit, and use tools, but could not compose the user's existing workflow abstractions.

Nested invocation also lets workflows become reusable units of work rather than only top-level automations. The main agent can recognize that a subproblem matches an existing workflow and invoke that workflow without becoming the orchestrator of the enclosing workflow.

This preserves the key authority split:

```text
workflow A owns workflow A progression
main-agent region A owns temporary local agency
workflow B owns workflow B progression
```

Invoking workflow B does not give the main agent authority to rewrite workflow A's control flow. It only lets the main agent use another available capability during the region in which it legitimately owns control.

## Consequences

- TURNLOCK workflows are composable from main-agent regions, not only invocable by the user at the top level.
- The session's TURNLOCK workflow discovery/invocation surface must remain available to the main agent during handoff regions.
- A nested workflow suspends rather than replaces its immediate caller.
- Completion returns to the immediate caller, not automatically to the root session.
- The runtime needs semantics equivalent to a caller stack even if implemented with another representation.
- A single flat `current_workflow` state that is overwritten by nested invocation is insufficient unless additional state preserves the suspended caller and exact return target.
- Outer workflow orchestration remains independent of nested workflow orchestration.
- Nested invocation is distinct from sibling or top-level workflow concurrency; this ADR does not decide whether multiple independent workflows may run concurrently in one session.

## Alternatives considered

### Forbid workflow invocation while inside a main-agent region

Rejected. It contradicts the ordinary-agency goal of ADR-007 and prevents the main agent from using session-available workflow capabilities exactly when agentic judgment may identify them as useful.

### Allow nesting but always return to the root main agent

Rejected. It skips the immediate caller, destroys structured composition, and can strand the enclosing workflow in an undefined suspended state.

### Let a nested workflow replace the enclosing workflow

Rejected. Invocation of a reusable capability must not implicitly cancel or overwrite the caller.

### Treat nested workflows as subagents rather than workflows

Rejected. A nested workflow retains TURNLOCK workflow semantics: it may itself contain mechanical regions, main-agent handoffs, and further nested workflow invocations.

### Require a specific frontmatter or skill-loading mechanism

Rejected as an architectural invariant. Skill frontmatter loaded by a harness is one motivating realization of discoverability, but TURNLOCK specifies the capability semantics rather than one vendor-specific discovery mechanism.

## Verification obligation

A conforming implementation must demonstrate at least this sequence:

```text
main agent
→ workflow A
→ mechanical A1
→ main-agent region A
→ workflow B
→ mechanical B1
→ main-agent region B
→ mechanical B2
→ workflow B completes
→ main-agent region A resumes
→ main-agent region A completes
→ mechanical A2
→ workflow A completes
→ root main-agent interaction resumes
```

The verification must show that:

1. workflow A remains intact while workflow B executes;
2. workflow B completion returns to main-agent region A, not directly to the root session;
3. main-agent region A can continue after workflow B returns;
4. workflow A resumes only when region A itself completes;
5. the same semantics remain valid for another level of nesting, subject only to any explicit accepted resource limit.
