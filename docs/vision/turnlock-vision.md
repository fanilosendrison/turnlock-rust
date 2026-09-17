---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "vision"
domain: "turnlock-rust"
severity: "informational"
name: "TURNLOCK architectural vision"
---

# TURNLOCK architectural vision

> **Status: non-normative.** This document explains TURNLOCK's long-term thesis
> and architectural motivation. Normative product semantics remain in the
> [TURNLOCK specification](../specification/turnlock-spec.md), accepted
> decisions remain in the [ADR record](../adr/README.md), and formal artifacts
> remain governed by the [formal-specification policy](../formal/README.md) and
> [ADR-015](../adr/adr-015-evolve-the-normative-and-formal-specifications-together.md).
> If this vision conflicts with one of those authorities, this document yields.
>
> The separate [future workflow run-evaluation design space](future-workflow-run-evaluation.md)
> preserves another non-normative exploration. It does not extend this vision or
> the product contract.

## 1. Why TURNLOCK exists

TURNLOCK exists to make processes executable without requiring a main coding
agent to remember, interpret, and simulate their entire control flow.

Its long-term architectural thesis is:

> **TURNLOCK makes it possible to build programs that call cognition.**

For the motivating software-development use case, this means that a production
process can itself become a program. Mechanical regions progress through
executable semantics, while judgment, interpretation, synthesis, invention, and
open-ended problem solving are requested explicitly where they are needed.
Mechanical execution need not produce deterministic outputs or traces.

TURNLOCK does not define that production process. It supplies the lower-level
workflow runtime and execution semantics on which a developer, organization,
coding agent, planner, or higher-level system can express one.

The current product remains specifically anchored inside an existing
interactive coding-agent session. The broader thesis is general; that session
integration is a defining part of TURNLOCK rather than an incidental user
interface.

## 2. The inversion: from agent-centric systems to programs that call cognition

Many coding-agent systems place the main agent at the architectural center:

```text
agent-centric

main agent
  ├── tools
  ├── skills
  ├── subagents
  └── workflows
```

In that shape, the main agent commonly decides what happens next, remembers the
procedure, and launches other capabilities. TURNLOCK moves declared global
control flow into an executable workflow program:

```text
TURNLOCK

workflow program
  ├── mechanical execution
  ├── bounded raw LLM inference
  ├── bounded independent agents
  └── existing main agent
```

This inversion does not make the main agent unimportant. The existing main
agent may be the richest cognitive resource in the system. It means only that:

```text
being the most capable execution resource
!=
owning global workflow progression
```

The workflow program owns its declared orchestration. TURNLOCK executes that
orchestration. Cognitive resources perform the regions allocated to them.

## 3. Programs capable of calling cognition

The architecture separates the source of policy from the runtime that realizes
it:

```text
policy / intent / methodology / generated strategy
                    ↓
             workflow program
                    ↓
                 TURNLOCK
                    ↓
    mechanical execution
    bounded raw LLM inference
    bounded independent agents
    continuation of the existing main coding agent
```

The layer above TURNLOCK chooses the workflow topology. The workflow artifact
records the resulting orchestration decisions. TURNLOCK then coordinates the
declared sequence, branches, joins, nested invocations, and returns while
preserving the semantics of each execution form.

This makes cognition callable without treating every cognitive operation as one
universal agent step. A program can select a bounded inference, create a new
agentic lineage, or continue the existing interactive lineage according to the
needs of a particular region.

## 4. Why the existing coding-agent session matters

TURNLOCK is invoked from the user's active coding-agent session. Workflow
execution is a bounded episode inside that continuing interaction, not a
separate workflow product that replaces it.

```text
user ↔ main coding agent
          ↓
       workflow
          ↓
      main agent
          ↓
       workflow
          ↓
user ↔ same main coding agent
```

More fully, a workflow may yield local control to the existing main agent,
resume its own progression, and repeat that handoff before returning to the
immediate caller:

```text
user ↔ existing main coding agent
              ↓
       invoke TURNLOCK workflow
              ↓
          workflow runs
              ↓
   may temporarily yield control
   back to the SAME main agent
              ↓
         workflow resumes
              ↓
     workflow eventually ends
              ↓
same interactive session continues
```

The workflow episode must not make the user abandon the working relationship,
context, or ordinary harness-native interaction already established in the
session.

## 5. Why the main agent is not equivalent to a fresh agent

The existing main agent carries a living cognitive lineage that may include:

- prior conversation and user corrections;
- repository understanding and prior tool results;
- local assumptions and decisions accumulated during the session;
- the ongoing interactive relationship with the user;
- ordinary capabilities supplied by the coding-agent harness.

An independent agent intentionally begins a new, bounded cognitive lineage. It
may receive carefully selected context and may use the same model, repository,
or tools, but those similarities do not make it the same continuing cognition.

```text
workflow → fresh agent → workflow
```

is therefore not equivalent to:

```text
workflow → existing main agent → workflow
```

A fresh independent agent is a deliberate cognitive fork. A main-agent region
is a deliberate continuation of the user's existing interactive cognitive
lineage. TURNLOCK preserves both as useful and distinct execution forms. A main
agent is not a generic LLM endpoint, and a main-agent region is not a renamed
subagent call.

## 6. Workflow-owned orchestration versus cognition-owned local execution

TURNLOCK separates two kinds of authority:

```text
global orchestration authority
!=
local cognitive / agentic execution authority
```

The workflow owns declared global progression: which region runs, which branch
follows, where fan-out joins, and where results return. TURNLOCK supplies the
runtime authority that executes and tracks that progression.

Within an explicitly agentic region, an agent may exercise substantial local
autonomy. It may reason, inspect files, use tools, react to evidence, revise its
approach, or interact with the user when the region permits it. That local
agency does not transfer ownership of the enclosing graph.

```text
workflow owns the process around a region
agent owns cognitive execution inside the region
workflow resumes at the declared continuation
```

Known control-flow decisions should remain workflow logic even when a harness
would make it convenient to ask the main agent to remember or schedule them.

## 7. TURNLOCK is a runtime, not a methodology

TURNLOCK is the runtime that executes a declared workflow. It is not the policy,
intent, methodology, or generated strategy that determines what the workflow
should be.

```text
TURNLOCK
!=
the software-development workflow

TURNLOCK
=
runtime that makes such workflows executable
```

TURNLOCK is therefore not:

- a software-development methodology;
- a catalog of predefined feature, bug-fix, review, or security workflows;
- a prompt workflow system;
- merely a multi-agent framework or a better subagent launcher;
- a replacement coding agent;
- a separate workflow product that users must leave their coding sessions to
  operate.

An organization may define a security process, a team may define a migration
process, and an agent may generate a task-specific graph. Those workflows live
above TURNLOCK. Domain concepts such as `FeatureWorkflow`, `BugfixWorkflow`, or
`ReviewWorkflow` do not belong in TURNLOCK's core semantics merely because
software development motivates the project.

## 8. Minimum-sufficient cognition

TURNLOCK treats computation and cognition as deliberately allocated resources.
The current execution spectrum is:

```text
0. mechanical execution
1. bounded raw LLM inference
2. bounded independent-agent execution
3. continuation of the existing main interactive agent
```

The guiding principle is to use the minimum sufficient form for each workflow
region:

- Known mechanical work should progress through executable semantics rather
  than depend on agent interpretation. Its results may still vary.
- A bounded semantic transformation should use raw inference when one inference
  is enough.
- A cognitively isolated task may use an independent agent when autonomous,
  multi-turn work is required.
- Main-agent continuation is appropriate when the living session lineage and
  ordinary interactive agency are valuable.

This ordering is not a quality ranking. It exposes differences in context,
autonomy, continuity, lifetime, and cost so that a workflow can allocate
cognition intentionally instead of representing all work as an undifferentiated
agent call.

## 9. Software production as the motivating application

The project's motivating long-term hypothesis is that production-grade software
development can benefit from executable process structure rather than asking a
coding agent to carry every process obligation in conversational memory.

A main agent is often asked to solve a software problem while also remembering
the procedure, choosing every transition, deciding when review is required,
determining whether verification is sufficient, and declaring completion.
TURNLOCK enables another division of responsibility:

```text
program / runtime:
    control flow
    explicit state
    lifecycle
    orchestration
    required transitions
    known process obligations

cognition:
    judgment
    interpretation
    synthesis
    invention
    open-ended problem solving
```

This is motivation, not a claim that every software process should use TURNLOCK
or that TURNLOCK knows the correct engineering method. Different developers,
teams, and organizations may encode different processes. TURNLOCK's role is to
make those processes programmable while leaving their policy and domain meaning
above the runtime.

## 10. Agent-authored workflows do not imply agent-owned execution

A workflow may be authored directly by a developer or generated and modified by
a coding agent. Both paths target the same developer-readable workflow artifact
and TURNLOCK primitives:

```text
developer authors workflow ─┐
                            ├──→ same workflow artifact
agent authors workflow ─────┘
                                      ↓
                         TURNLOCK executes declared orchestration
```

Authorship does not determine execution ownership:

```text
LLM may author orchestration
!=
LLM owns execution of orchestration
```

Once the workflow program exists, it is the source of truth for its declared
control flow. TURNLOCK executes it. An LLM that produced the artifact does not
become the hidden scheduler, just as a developer who wrote the artifact does
not personally perform its runtime progression.

## 11. Externalized and evolvable engineering methods

TURNLOCK's existing separation between workflow authorship, workflow-owned
orchestration, and cognitive execution has a broader architectural consequence:
a software-engineering method that initially exists only inside human or agentic
working behavior can be externalized into an independently executable workflow
artifact.

Conceptually:

```text
developer or coding agent
        ↓
working method / discovered procedure
        ↓
workflow artifact W
        ↓
TURNLOCK executes W
```

TURNLOCK does not decide what the correct engineering method is. Policy, intent,
methodology, generated strategy, and workflow selection or generation remain
above the runtime. TURNLOCK's role begins once the resulting orchestration is
expressed as a workflow program that it can execute.

Externalizing the method does not remove cognition from the process. The same
architecture supports the opposite direction as well:

```text
cognition
  → authors program

program
  → calls cognition where needed
```

A coding agent may therefore author or modify a workflow and later participate
in execution through one of TURNLOCK's declared cognitive execution forms. When
the applicable workflow semantics request continuation of the existing main
agent, the workflow may call back into that continuing cognitive lineage.
Authorship still does not confer runtime orchestration authority:

```text
authoring the method
!=
owning global workflow progression
```

The stable governing definition of an accepted invocation also separates
evolution of the workflow artifact from mutation of an execution already in
progress. For example:

```text
Agent A authors W17
        ↓
TURNLOCK accepts an invocation governed by W17
        ↓
A discovers an improvement while work is occurring
        ↓
A authors W18
        ↓
the active invocation remains governed by W17
        ↓
a later invocation may execute W18
```

The successor artifact is therefore a new generation of the engineering method,
not an implicit replan or rebind of the active invocation.

This creates a possible cumulative loop:

```text
cognition
    ↓
externalized method W
    ↓
execution
    ↓
observation / external evaluation
    ↓
authored successor W'
    ↓
later execution
```

TURNLOCK allows cognition to externalize a working method into an independently
executable artifact while allowing that artifact to call cognition back where
needed. The method and the cognition that participates in it can then improve
along separate axes: a better model or agent can become a better execution
resource without forcing the engineering method back into transient cognition,
and the engineering method can itself be refined without requiring a new model.

This distinction becomes increasingly important as software engineering becomes
more agentic. Improving an individual agent is only one way to improve an
agentic software-engineering system. The engineering method, the explicit
control around cognition, and the evidence available for evaluating execution
can improve independently as well.

Conceptually:

```text
better cognition
        +
better executable engineering method
        +
better control
        +
better evaluation
        ↓
better agentic software-engineering system
```

This diagram expresses complementarity, not a mathematical relationship.

TURNLOCK does not primarily aim to make an individual agent more capable. Its
role is to make engineering methods used by agentic systems executable under
explicit workflow control, inspectable at TURNLOCK's semantic boundary, and
amenable to external empirical evaluation and refinement.

That role can support increasingly autonomous software-engineering systems.
Without explicit process structure, one agent may otherwise be responsible for
solving the engineering problem while also remembering the full procedure,
scheduling every step, coordinating every transition, and policing its own
adherence to the method. TURNLOCK permits a different allocation:

```text
workflow artifact
  → owns declared process structure

TURNLOCK
  → executes that structure

mechanical execution and cognition
  → perform the regions allocated to them
```

This can reduce the amount of stable procedural responsibility that must remain
inside transient agent cognition while preserving rich local cognition wherever
the workflow explicitly requires it.

TURNLOCK is not the complete system that turns human intent into software. It
does not choose product intent, invent the correct methodology, determine the
appropriate generated strategy, or decide which workflow should be used.
Higher-level systems and actors retain those responsibilities.

The relationship remains:

```text
policy / intent / methodology / generated strategy
                    ↓
             workflow program
                    ↓
                 TURNLOCK
                    ↓
    computation and distinct forms of cognition
```

Likewise, TURNLOCK core does not decide whether a successor workflow `W'` is
better than `W`, automatically promote it, or own the optimization objective.
Those decisions remain outside TURNLOCK core under the existing evaluation and
optimization boundary.

This section describes an architectural consequence and long-term direction
enabled by existing TURNLOCK semantics. It introduces no new workflow primitive,
automatic self-improvement facility, optimizer, promotion mechanism, active
replanning behavior, active rebinding behavior, or conformance obligation.

## 12. Long-term direction: structured cognition

One useful, non-normative description of the direction is **structured
cognition**. The phrase is an architectural analogy, not a new product primitive
or conformance term.

A TURNLOCK workflow makes cognitive work explicit enough to reason about:

- which workflow region owns the request;
- what context the region receives;
- whether the region creates a new cognitive lineage or continues an existing
  one;
- what local authority and capabilities it has;
- what lifetime and completion boundary apply;
- where its result or control returns;
- who owns global progression around it.

This structure permits rich local autonomy without surrendering the surrounding
process to implicit agent scheduling. Independent agents remain deliberate
forks; main-agent regions remain deliberate continuations; bounded inference
remains non-agentic semantic computation.

## 13. What TURNLOCK intentionally does not define

This vision does not select:

- a software-development methodology or domain workflow ontology;
- a concrete workflow language, syntax, file format, library, or packaging
  model;
- a Rust crate architecture or public API;
- a process, daemon, IPC, persistence, scheduling, or session-identity
  mechanism;
- a provider abstraction, model-selection interface, or context-transfer
  protocol;
- completion, failure, cancellation, retry, or durability semantics that the
  normative specification leaves open;
- main-agent participation as an ordinary concurrent branch;
- one harness's internal APIs as TURNLOCK semantics.

Current artifact status is not mirrored here: the repository tree exposes
actual artifact presence, and `formal/verification.yaml` owns current
formal-model and intended-verification state. Pi is the first reference harness,
but supported harnesses realize TURNLOCK semantics rather than define them.

These boundaries allow the architectural thesis to remain explicit without
turning implementation guesses, long-term hypotheses, or motivating examples
into product invariants.
