# TURNLOCK — Requirements, Invariants, and Architectural Implications

> Working product specification derived from the current product discussion.
>
> This document intentionally starts from product intent and derives invariants before fixing implementation mechanisms. Terms such as process model, IPC, daemon, session identifiers, adapters, protocol shape, storage engine, or concrete harness APIs are deliberately left unspecified unless the product contract requires them.

# 0. Product intent — governing user experience

This section is normative for the current product direction. It states the
product outcome that lower-level design exists to serve. It is ratified by
ADR-001 through ADR-014 and ADR-016 in `../adr/`, which record the chronological
product decisions that produced the current contract. ADR-015 governs how this
normative specification co-evolves with the formal TLA+/TLC model and
verification manifest.

If a future implementation admits several mechanisms, the conforming mechanism is the one that preserves this product intent and the derived invariants. A technical convenience is not sufficient reason to weaken the product promise. If a later design weakens one of these user-visible guarantees, that weakening must be explicit in a new ADR rather than emerging accidentally from implementation constraints.

## 0.1 Product definition: user-authored workflows inside coding-agent sessions

TURNLOCK exists so that a user working inside an interactive coding-agent session can **build and execute workflows whose global orchestration is owned by executable workflow logic rather than by the main agent, while still being able to compose the appropriate form of computation or cognition at each explicit region**.

The product is not merely a prompt library, a large skill, a subagent launcher, or a generic LLM workflow engine. Its defining property is that **the workflow program owns the declared orchestration logic, while TURNLOCK is the engine/runtime that executes that logic** and makes different execution resources available as first-class leaves or bounded regions.

The current execution spectrum is:

```text
deterministic / mechanical computation
bounded raw LLM inference
bounded independent-agent execution
continuation of the main interactive coding agent
```

TURNLOCK also requires workflow-owned composition capabilities such as sequencing, branching/iteration where declared, concurrency, fan-out/fan-in, nested workflow invocation, and structured return to the immediate caller.

A representative control shape remains:

```text
main agent
  → workflow invocation
  → mechanical preparation
  → parallel bounded semantic work
      ├→ raw LLM call(s)
      └→ independent agent(s)
  → collect / continue
  → main-agent continuation
  → mechanical finalization
  → workflow ends
  → immediate caller resumes
```

The workflow is therefore not a sequence that an agent is asked to remember and execute. The workflow program declares the progression through the graph; TURNLOCK executes that declared orchestration, even when some leaves are probabilistic or locally autonomous. TURNLOCK MUST NOT silently become a decision-maker that invents the global strategy on the workflow's behalf.

## 0.2 The product promise

TURNLOCK exists so that **a user can turn part of their working method into executable workflow logic, allocate the minimum sufficient computation or cognition to each region, and still preserve first-class access to the main coding agent when continuity with the interactive session matters**.

The target experience includes all of the following without transferring global orchestration to the main agent:

```text
User is already working with the main agent.

User invokes a workflow naturally from the coding-agent session.

The workflow executes mechanical work directly.

For bounded one-shot semantic work, it can call an LLM directly.

For bounded autonomous semantic work, it can start independent agents,
including several in parallel on the same task or different tasks.

When session continuity itself is valuable, the workflow can hand control
to the existing main agent and later resume.

Any of these regions may be composed with explicit workflow control,
including fan-out/fan-in and nested workflows.

When an invocation finishes, control returns to its immediate caller.
```

The governing promise is:

> **The workflow program owns the declared orchestration logic; TURNLOCK is the orchestration engine that executes it. The workflow can compose deterministic computation, bounded LLM inference, bounded independent agency, and continuation of the main interactive agent as distinct execution forms. Probabilistic or autonomous leaves do not become the global orchestration decision-maker merely by being invoked, and completed workflows return structurally to their immediate caller.**

## 0.3 Workflow invocation is a natural slash-command surface inside the coding-agent session

TURNLOCK workflows MUST be naturally invocable **from inside the active coding-agent session through a slash-command interaction comparable to invoking a native skill**.

The product requirement is the interaction shape, not a particular command name. `/go` was only an illustrative example used during the product discussion. TURNLOCK does not define `/go` as the canonical command, and this specification does not yet decide whether invocation is exposed through one TURNLOCK command, workflow-specific slash commands, harness-native skill registration, or another equivalent slash-command mapping.

The ordinary interaction is approximately:

```text
user is working with main agent
  → user invokes a TURNLOCK workflow through a natural slash command
  → workflow-owned execution begins
```

The invocation surface MUST NOT make the main agent the hidden orchestrator of all subsequent workflow steps. A design is therefore non-conformant if the slash command merely expands into a large prompt whose effective meaning is:

```text
"Main agent, remember this whole workflow,
execute every step in order,
decide when to run commands,
decide when to reason,
and keep track of where you are."
```

That would preserve agent-owned orchestration and fail the core product intent.

The invocation mechanism may be realized differently by different supported coding-agent harnesses, but the user-facing invariant remains: **invoking a TURNLOCK workflow should feel like invoking a skill from the session the user is already in, not like leaving that session to operate a separate workflow product or shell protocol.**

### 0.3A Workflow capabilities remain invocable whenever the main agent owns control

The skill-like invocation surface is not only a top-level user entry mechanism. A TURNLOCK workflow exposed to the coding-agent session is also a capability that the main agent may use while it owns an agentic region.

Therefore, when a workflow has yielded control to the main agent, that main agent MAY invoke another available TURNLOCK workflow. The enclosing workflow is suspended while the nested workflow executes; it is not replaced or discarded.

Conceptually:

```text
main agent
  → workflow A
    → mechanical A1
    → main-agent region A
      → workflow B
        → mechanical B1
        → main-agent region B
        → mechanical B2
        → workflow B ends
      → main-agent region A resumes
    → mechanical A2
    → workflow A ends
  → main agent continues
```

This makes TURNLOCK workflows **composable capabilities inside the same coding-agent session**. A main-agent region retains the ordinary ability to select and invoke a workflow that is available to that session. The concrete discovery mechanism — for example skill frontmatter loaded by a harness — is an implementation detail; the product invariant is that entering a workflow MUST NOT make other session-available TURNLOCK workflows disappear from the main agent's usable capability surface.

Nested invocation does not transfer global orchestration of the outer workflow to the main agent. The main agent decides only to invoke workflow B while it owns region A; workflow A still owns its own continuation after region A eventually completes.

## 0.4 Main-agent steps are real control handoffs

A main-agent step is not merely equivalent to calling an arbitrary model with a prompt.

The required product semantics are:

```text
workflow owns control
  → main-agent step begins
  → main agent owns control for that phase
  → main-agent phase completes
  → workflow regains control
```

The main-agent phase exists specifically so the workflow can use the coding agent the user is already working with, including the useful continuity of that interactive working relationship.

Therefore, unless a future product decision explicitly weakens this promise:

```text
main-agent step != anonymous LLM completion
main-agent step != unrelated fresh agent by default
main-agent step != mandatory subagent replacement
```

Independent agents are a required TURNLOCK capability, but they remain semantically distinct from a **main-agent step**. A fresh agent intentionally creates a bounded new cognitive lineage; it does not by itself satisfy the continuation semantics of the main agent.

## 0.5 Control handoff is reversible and repeatable

A handoff to the main agent MUST NOT terminate the surrounding workflow.

The workflow must be able to resume after the main-agent phase and continue with the next workflow-owned step.

The minimum conforming sequence is:

```text
workflow
  → mechanical step
  → main-agent step
  → mechanical step
```

The general conforming sequence permits repeated alternation:

```text
workflow
  → mechanical
  → main agent
  → mechanical
  → main agent
  → mechanical
  → ...
```

There is no product-level assumption that a workflow contains only one agentic phase.

## 0.6 Workflow completion returns control to the immediate caller

The surrounding interactive coding-agent session is not conceptually replaced by workflow execution, and a nested workflow does not replace the context that invoked it.

The general lifecycle is:

```text
caller context
  → enter workflow
  → workflow executes
  → workflow terminates
  → caller context resumes
```

For a top-level invocation, the immediate caller is the main-agent interaction of the surrounding coding session:

```text
main agent
  → workflow A
  → workflow A terminates
  → main agent
```

For a nested invocation from a main-agent region of another workflow, the immediate caller is that main-agent region:

```text
main-agent region A
  → workflow B
  → workflow B terminates
  → main-agent region A resumes
```

Workflow completion MUST therefore have a defined return path to the **immediate invocation context** rather than unconditionally jumping to the root session, leaving the user stranded in a separate automation context, or requiring manual reconstruction of the suspended caller.

For top-level workflows, this preserves the original promise that the ordinary interactive session resumes when the workflow ends. For nested workflows, it preserves structured composition: inner completion returns to the point that invoked the inner workflow, and the enclosing workflow continues only when its own main-agent region completes.

## 0.7 Mechanical work must not require agent interpretation

A workflow may contain steps whose semantics are sufficiently known that they should execute mechanically.

Examples may eventually include commands, checks, transformations, waiting, branching, state transitions, validation, or other deterministic operations. Their exact taxonomy is not fixed here.

The invariant is:

> **If a workflow step is defined as mechanical, its execution must not depend on the main agent correctly remembering, interpreting, or deciding to perform that step.**

This is the core reliability gain TURNLOCK seeks over encoding the whole process in a skill or prompt.

The main agent may still observe mechanical results when a later agentic phase needs them, but it is not the source of truth for whether the mechanical progression occurred.

## 0.8 The workflow, not the main agent, owns global progression

During an active workflow, the workflow is the authority for **where execution is in the workflow** and **what phase comes next**.

The main agent may own a main-agent phase while that phase is active, but that temporary ownership does not make the main agent the global workflow orchestrator.

Conceptually:

```text
workflow owns global progression

mechanical phase:
  workflow executes directly

main-agent phase:
  workflow yields local control
  main agent acts
  main agent completes/yields
  workflow resumes global progression
```

Therefore the workflow's correctness MUST NOT rely on the main agent remembering the remaining control-flow graph after every agentic phase.

## 0.8A TURNLOCK executes orchestration; it does not invent it

The phrase **“the workflow owns orchestration”** refers to ownership of the declared orchestration logic, not to TURNLOCK being absent from execution. TURNLOCK is the runtime/engine that interprets or executes the workflow program, tracks its declared progression, and realizes its primitives against the available harness and execution resources.

The roles are therefore:

```text
developer or coding agent
  → authors
workflow program
  → declares orchestration logic
TURNLOCK runtime / engine
  → executes that orchestration logic
mechanical / LLM / independent-agent / main-agent resources
  → perform bounded regions under the declared workflow semantics
```

TURNLOCK MAY implement scheduling, state tracking, branch coordination, fan-out/fan-in, retries once specified by workflow semantics, and harness translation as execution machinery. It MUST NOT, merely because it is the runtime, invent undeclared global workflow strategy such as deciding on its own how many semantic workers to launch, which cognition form should replace a declared one, which declared phase should be skipped, or what undeclared step should execute next.

The governing distinction is:

```text
workflow = orchestration program / declared decisions
TURNLOCK = orchestration engine / execution machinery
```

In ordinary industry terminology TURNLOCK may still be described broadly as an “orchestrator,” but normatively it is **not the orchestration decision-maker**. TURNLOCK executes orchestration; it does not author or invent it.

## 0.9 The workflow must have execution continuity independent of agent memory

Because the workflow owns orchestration, sufficient workflow execution state must exist independently of the main agent's conversational memory.

At minimum, after a main-agent phase completes, the system must be able to determine that the workflow should resume and which workflow phase follows.

This does **not** yet prescribe how such state is represented, persisted, transported, or recovered.

The invariant is only:

```text
workflow progression truth
!= main-agent recollection of the workflow
```

## 0.10 Use the minimum sufficient form of computation or cognition for each workflow region

TURNLOCK does not divide work only into "mechanical" and "main-agent" regions. The workflow must be able to choose among distinct execution forms according to what the task actually requires.

The governing spectrum is:

```text
0. deterministic computation
1. bounded raw LLM inference
2. bounded independent agentic execution
3. continuation of the main interactive agent
```

These forms are not interchangeable aliases. They have different cost, context, autonomy, continuity, and concurrency properties.

The product principle is:

> **For each workflow region, use the least powerful form of computation or cognition that is sufficient to perform the task correctly.**

This is not a quality ranking. A raw LLM call can be the best execution form when all required information is already available and one semantic transformation is enough. An independent agent can be best when the task requires autonomous multi-turn exploration or tool use but should remain cognitively isolated. The main agent is best when continuity with the surrounding interactive session is itself valuable.

TURNLOCK therefore allows a workflow author to deliberately allocate a cognitive budget rather than route every semantic task through the most expensive or context-heavy execution form.

## 0.10A Independent agents are first-class workflow resources

Some semantic tasks are better performed by a new, deliberately bounded cognitive lineage than by the main agent. TURNLOCK therefore requires independent-agent execution as a first-class workflow capability rather than treating it only as something the main agent may choose to do internally.

Conceptually:

```text
workflow
  → construct bounded task/context
  → start independent agent
  → agent performs autonomous multi-turn work
  → return result to workflow
  → workflow continues
```

The independent agent exists precisely because a cognitive fork can be useful. Its task may be bounded more tightly than the main session, its context may be selected specifically for the job, and its intermediate exploration does not need to become part of the main-agent lineage.

TURNLOCK MUST also be able to express parallel independent-agent work under workflow ownership. Parallel agents may receive:

```text
the same task
  → independent attempts / reviews / judgments

or

different tasks
  → decomposition / specialization
```

The workflow, not the main agent, owns declared fan-out, synchronization, collection, and subsequent progression when that topology is part of the workflow definition.

This matters because a deterministic orchestrator intentionally gives up some of the decision-time flexibility of an agentic orchestrator. TURNLOCK compensates by making the deterministic orchestration surface expressive enough that known orchestration decisions do not need to be pushed back into a main-agent prompt merely because they involve semantic work, concurrency, or delegation.

## 0.10B Raw LLM inference is a distinct first-class semantic primitive

Some semantic tasks do not require an agentic loop at all. When the workflow already has the needed inputs and only needs a bounded semantic transformation, a direct model inference can be more appropriate than either an independent agent or the main agent.

Conceptually:

```text
instruction + explicit context
          ↓
       LLM call
          ↓
        result
```

A raw LLM call does not imply an autonomous observe/reason/act loop, persistent cognitive lineage, interactive session continuity, or access to the ordinary main-agent harness loop. It is intentionally narrower.

Representative uses include classification, extraction, summarization, scoring, ranking, rewriting, adjudication, or another bounded semantic transformation for which one inference is sufficient.

TURNLOCK MUST be able to express multiple raw LLM calls concurrently when the workflow declares them independent. Those calls may perform the same task for diversity/redundancy or different tasks for decomposition.

The exact provider, model-selection surface, inference parameters, context format, structured-output mechanism, and budgeting controls remain open. What is fixed is that **bounded non-agentic LLM inference is semantically distinct from both independent-agent execution and main-agent continuation**.

## 0.10C Parallel fan-out may be homogeneous or heterogeneous

TURNLOCK parallelism is not limited to repeating one execution primitive. When branches are independent and the workflow declares their topology, a single fan-out MUST be able to contain heterogeneous branch types.

For example:

```text
fan-out
  ├→ mechanical computation
  ├→ raw LLM call A
  ├→ raw LLM call B
  ├→ independent agent A
  └→ independent agent B
join
→ workflow continuation
```

Within that fan-out:

- multiple raw LLM branches MAY perform the same task or different tasks;
- multiple independent-agent branches MAY perform the same task or different tasks;
- raw LLM, independent-agent, and mechanical branches MAY coexist in the same declared parallel region;
- each branch retains the lifecycle, context, authority, and result semantics of its own execution form;
- the workflow owns branch creation, synchronization, collection, and declared continuation.

This capability matters because the workflow author may want to combine cheap bounded inference, richer autonomous delegation, and deterministic computation in one explicit concurrency topology rather than split them into artificial sequential phases.

This decision does **not yet assert that main-agent continuation can participate as an ordinary concurrent branch**. Main-agent continuation has unique session-lineage and interactive-control semantics; concurrency involving it remains a separate semantic question.

## 0.10D Deterministic orchestration may compose probabilistic leaves

TURNLOCK's deterministic-orchestration goal concerns ownership of control flow, not bit-for-bit determinism of every computation executed by the workflow.

A workflow may explicitly orchestrate operations whose outputs are probabilistic:

```text
mechanical computation
raw LLM inference
independent agent
main-agent continuation
```

while retaining explicit progression authority:

```text
workflow decides what runs
workflow decides declared sequencing / branching / fan-out / join
workflow receives results
workflow decides the declared continuation
```

Therefore:

> **Deterministic orchestration does not require deterministic leaf computations.**

The relevant question is not "can this step produce a probabilistic result?" but "who owns the decision about what execution region comes next?"

## 0.11 Session continuity is part of the product value

The motivation for a main-agent step is not merely access to model intelligence. It is access to the user's ongoing coding-agent working context.

The main agent may already have useful continuity from the session: prior discussion, repository understanding, decisions, user corrections, current working assumptions, available tools, and the natural interaction channel with the user.

The product therefore seeks to preserve the following conceptual continuity:

```text
user ↔ main agent
        ↑      ↓
        workflow
```

rather than forcing every agentic phase into:

```text
user ↔ main agent

workflow → unrelated agent
```

The exact amount and mechanism of session/context continuity that can be guaranteed across different coding harnesses remains an implementation and capability question, but replacing the main-agent concept with arbitrary stateless completions would not satisfy the product intent.

## 0.11A Why a main-agent handoff is not equivalent to spawning a fresh agent

The requirement to return control to the main agent exists for a product reason, not because TURNLOCK prefers one process topology.

A fresh agent can often be given the same repository, prompt, model family, tools, or selected conversation excerpts. That is useful, but it creates a new agentic lineage whose working state must be reconstructed from whatever the caller chooses to transfer. The surrounding main session and the spawned agent can then learn different things and make different local assumptions. Conceptually:

```text
main session before spawn:  A B C D E
                              |
                              +--> spawned agent receives A B C
                                      and learns F G H

main session afterwards:     A B C D E
spawned lineage:              A B C F G H
```

The system must now reconcile two cognitive lineages through summaries, artifacts, patches, messages, or another synchronization mechanism. Even a very good reconstruction is still a reconstruction boundary.

A TURNLOCK main-agent handoff seeks a different semantic shape:

```text
main session:  A B C D E
                  ↓
              workflow
                  ↓
              same ongoing agentic lineage
                  ↓
              A B C D E F G H
```

The product value is therefore not merely "same model" or "same repository". It is **continuation of the user's current agentic working relationship without requiring a context export/import and later cognitive reconciliation merely because execution temporarily entered a workflow**.

This yields a stronger invariant:

> **Crossing a workflow boundary MUST NOT create a new cognitive lineage merely because a workflow requests main-agent continuation. Independent cognitive lineages are a required TURNLOCK capability, but they are a different execution form and MUST NOT be silently treated as equivalent to a main-agent step.**

This invariant is semantic rather than process-specific. A future harness mechanism that can prove equivalent continuation semantics without literally reusing the same OS process may satisfy it. TURNLOCK therefore does not require "same process" as a product invariant; it requires preservation of the continuing main-agent lineage.

## 0.11B A main-agent phase restores ordinary interactive agency, not an AI request/response call

The main agent is valuable not only because it carries context but because it is already embedded in an interactive coding harness with its ordinary operating loop. During a main-agent phase, TURNLOCK should be able to rely on the agent behaving as the user's normal coding agent rather than being reduced to a single function call.

A main-agent phase may therefore need to permit the ordinary class of behavior available in that session, such as:

```text
reason over the repository
inspect files and prior tool results
edit code
run tools and tests
change direction after new evidence
use harness-native capabilities
interact with the user when judgment requires it
continue until the phase's completion condition is satisfied
```

The governing distinction is:

```text
not:  workflow calls AI(prompt) and receives one result

but:  workflow suspends its local execution authority
      → ordinary main-agent agency is active for this region
      → that region completes/yields
      → workflow resumes
```

A one-shot LLM request/response is nevertheless a valid **separate** TURNLOCK primitive when that narrower semantic execution form is what the workflow requests. The prohibition here is only against implementing a declared main-agent continuation as though it were such a call.

This lets TURNLOCK combine two properties that are otherwise often traded against each other:

```text
determinism outside agentic regions
+
full coding-agent agency inside explicitly agentic regions
```

The workflow controls **when** agentic work occurs and what boundary it occupies. It does not need to reimplement or artificially narrow **how** the coding agent performs that work.

## 0.12 Supported coding harnesses are execution environments, not the product definition

The motivating environment includes coding agents such as Claude Code, Pi, Codex, and similar interactive coding harnesses.

TURNLOCK is not conceptually defined as a feature of only one of them.

The product-level abstraction is:

```text
supported interactive coding harness
  → workflow entry
  → workflow-owned execution
  ↔ main-agent handoffs
  → return to interactive harness
```

Different harnesses may expose different integration capabilities. Those differences may constrain implementation or conformance tiers, but the workflow semantics should not be redefined merely because one harness exposes a different API.

Portability does not mean every harness must use the same mechanism. It means the product should preserve the same user-facing control semantics wherever support is claimed.

## 0.12A Pi is the first reference harness, not the semantic definition of TURNLOCK

TURNLOCK is intended to become **harness-agnostic**, but product development will first concentrate on making the model work deeply and naturally inside **Pi**.

This is a sequencing decision, not a semantic narrowing of the product. The dependency direction is normative:

```text
TURNLOCK workflow semantics
        ↓
harness integration contract
        ↓
Pi realization first
        ↓
later realizations for other supported harnesses
```

Pi-specific APIs, lifecycle events, extension hooks, skill/frontmatter conventions, or session mechanics MAY be used aggressively to realize the best possible first implementation. They MUST NOT silently become the definition of a TURNLOCK workflow primitive when the product-level concept can be stated independently of Pi.

A workflow author should reason in TURNLOCK terms such as:

```text
mechanical execution
main-agent region
nested workflow invocation
return to immediate caller
```

not in Pi-internal operations required only to implement those semantics.

The first implementation may expose capability gaps that force refinement of the abstract contract. Such refinement is allowed, but any rule that makes a Pi-specific mechanism part of the normative semantics requires an explicit product decision rather than accidental leakage from the reference integration.

## 0.13 The user can encode working method rather than prompt an agent to simulate it

A central product outcome is that a recurring process can become an executable artifact.

The distinction is:

```text
prompt/skill model:
  "Agent, follow this procedure."

TURNLOCK model:
  procedure executes itself
  and calls the main agent only at explicit agentic boundaries
```

This matters because the procedure should remain the procedure even if the main agent would otherwise choose a different order, omit a mechanical step, or reinterpret an instruction.

The workflow therefore acts as a durable expression of the user's process, while agentic steps remain deliberate escape points into flexible reasoning and coding.

## 0.13A Workflow authoring is developer-native and agent-native

TURNLOCK does not require a separate graphical workflow builder or a second AI product in order for users to create workflows. The intended authoring surface is developer experience: a developer can write a workflow directly, or ask the coding agent already present in the session to write or modify that workflow.

Both paths target the **same workflow artifact** and the same TURNLOCK primitives:

```text
developer intent
  → developer writes TURNLOCK workflow

or
developer intent
  → coding agent writes TURNLOCK workflow

                    ↓
          same kind of workflow artifact
                    ↓
          same TURNLOCK execution semantics
```

Authorship does not confer runtime orchestration authority. A developer, coding
agent, LLM planner, or higher-level system may produce the artifact; once
execution begins, the artifact remains authoritative for its declared
orchestration and TURNLOCK executes it. Authorship does not prevent an author
that is also available under an existing execution form from later
participating. Any local authority then comes from an explicit workflow region,
including a main-agent continuation when the author is the existing main agent.

TURNLOCK therefore provides **workflow primitives**, not a separate semantic language for human-authored versus agent-authored workflows. A coding agent generating a workflow is acting as a code author over TURNLOCK's public primitives, not invoking a privileged hidden generator protocol.

The product requirement is not yet a concrete syntax. The exact language, library shape, file format, typing model, or packaging convention remains open. The invariant is that the authoring model must be simple and explicit enough that:

```text
a developer can inspect and edit it directly
a coding agent can generate and modify it from natural-language intent
the resulting artifact remains understandable as workflow code
control flow is expressed through TURNLOCK semantics rather than harness plumbing
```

TURNLOCK MAY later provide higher-level authoring tools, templates, or visualizations, but they are optional layers over the same underlying workflow artifact and primitives. They MUST NOT become necessary to express the core execution model.

## 0.14 Product-intent conformance rule

A proposed design or implementation is not product-conformant if ordinary use requires any of the following to preserve workflow correctness:

```text
the main agent must remember and orchestrate the whole workflow

mechanical steps are merely prose instructions that the main agent may or may not execute

a main-agent step permanently exits the workflow

the workflow cannot continue after a main-agent phase

every main-agent phase is silently replaced by an unrelated subagent or fresh stateless completion

a main-agent phase requires exporting enough context to a new independent cognitive lineage and later reconciling that lineage as the normal semantics

a main-agent phase is reduced to a one-shot AI request/response interface when the ordinary interactive agent needs broader agency

workflow completion does not return to its immediate invocation context

a nested workflow completion jumps past its caller to the root session

entering a main-agent region hides or disables TURNLOCK workflows that are otherwise available to the session

the main agent is forbidden from invoking an available TURNLOCK workflow merely because it currently owns a main-agent region of another workflow

the user must manually reconstruct which workflow step comes next after each agentic phase

the same workflow semantics fundamentally change depending on whether the supported harness is Claude Code, Pi, Codex, or another integration

workflow authors must write Pi-specific control plumbing instead of TURNLOCK-level workflow semantics

human-authored workflows and coding-agent-authored workflows use different semantic artifact types

an agent-authored or dynamically generated workflow exists only as advisory
instructions that its author must interpret or schedule

runtime orchestration authority is delegated back to an author merely because
that author is an LLM or agent

a generated graph is not independently represented or executed, and correctness
depends on its author remembering the graph

a proprietary builder is required to express core TURNLOCK workflow behavior

a workflow whose declared topology requires independent agents must hand orchestration to the main agent merely to spawn, synchronize, or collect those agents

independent-agent execution silently inherits the entire main-agent cognitive lineage when the workflow requested a bounded independent task

a bounded one-shot semantic task can only be expressed by creating a multi-turn agent or yielding to the main agent

parallel independent semantic work cannot be expressed as workflow-owned fan-out/fan-in

a heterogeneous fan-out cannot combine mechanical, raw-LLM, and independent-agent branches while preserving each branch's distinct semantics

probabilistic semantic leaves are treated as if they necessarily transfer global orchestration authority away from the workflow
```

A conforming implementation may use different internal mechanisms per harness, but those mechanisms exist to realize the same control contract.

## 0.15 Reference product-conformance scenario

The reference scenario is:

```text
1. The user is in an ordinary interactive session with the main coding agent.

2. The user invokes a workflow through a natural slash command in the active coding-agent session, with skill-like invocation ergonomics.

3. Workflow execution begins without making the main agent responsible
   for interpreting the remaining workflow.

4. A mechanical step executes.

5. The workflow reaches a main-agent step.
   Control is handed to the main agent.

6. The main agent performs the required agentic work using the interactive
   coding-agent capabilities expected from that main session.

7. That phase completes.
   The workflow resumes automatically at the correct next step.

8. Another mechanical step executes.

9. The workflow hands control to the main agent again.

10. The second main-agent phase completes.
    The workflow resumes again.

11. Final mechanical work executes.

12. The workflow terminates.

13. Control returns to the main agent and the ordinary interactive session continues.
```

The compact form is:

```text
main agent
> natural slash-command workflow invocation
> script/workflow
> mechanical step
> main-agent step
> mechanical step
> main-agent step
> mechanical step
> script/workflow finished
> main agent
```

A second reference scenario establishes composition:

```text
main agent
> invoke workflow A
> mechanical A1
> main-agent region A
    > invoke workflow B
    > mechanical B1
    > main-agent region B
    > mechanical B2
    > workflow B finished
> main-agent region A resumes
> mechanical A2
> workflow A finished
> main agent
```

Workflow B returns to the main-agent region that invoked it. It does not skip that caller, terminate workflow A, or jump directly to the root session.

A third reference scenario establishes authoring DX:

```text
Developer describes or directly writes a desired workflow.

Path A:
  developer writes the workflow using TURNLOCK primitives

Path B:
  developer asks the coding agent to write the workflow
  coding agent writes the workflow using the same TURNLOCK primitives

Both produce the same class of inspectable/editable workflow artifact.
The workflow becomes invocable through the coding-agent session's natural workflow surface.
```

A fourth reference scenario establishes cognitive-resource composition:

```text
workflow
> mechanical preparation
> 3 bounded raw LLM calls in parallel on the same task
> mechanically compare/aggregate their outputs
> independent agent A: bounded autonomous investigation
> independent agent B: different bounded autonomous investigation
  (A and B execute in parallel)
> join A/B
> main-agent continuation for work that requires session continuity
> mechanical finalization
> workflow returns to its caller
```

The proof is not that every leaf is deterministic. The proof is that the workflow explicitly owns the topology, boundaries, fan-out/fan-in, and continuation while selecting the appropriate cognition form for each region.

A fifth reference scenario establishes authorship/execution separation:

```text
main agent
> generates workflow G
> TURNLOCK begins executing G
> mechanical step
> G invokes main-agent continuation
> same main agent performs bounded local work
> G resumes declared progression
```

The main agent's authorship of G does not make it G's runtime scheduler. Its
later local authority comes from the explicit main-agent region, after which
TURNLOCK resumes executing G's declared orchestration.

Pi is the first reference harness used to prove these scenarios end to end. Passing the Pi proof does not authorize TURNLOCK to redefine the normative workflow model in terms of Pi-only APIs.

Any architecture proposed for TURNLOCK should first demonstrate these scenarios before broader features are treated as product-defining.

# 1. Purpose

The governing user-visible contract is §0. The mechanisms below and future technical specifications MUST be interpreted in service of that contract.

TURNLOCK addresses a specific failure mode in interactive agentic software development:

> **Today, reusable workflows are commonly encoded as instructions for the main agent to orchestrate. This leaves control flow, step ordering, and mechanical progression dependent on model behavior. Moving orchestration fully into code improves determinism, but typical agent-workflow systems then replace the user's main interactive coding agent with subagents or separate agent calls. TURNLOCK aims to combine workflow-owned orchestration with reversible access to the main agent already participating in the user's session.**

The central reason for preserving the main-agent handoff is that a spawned independent agent is not automatically equivalent to the current main session. Spawning introduces a context reconstruction boundary and potentially a cognitive fork; handoff is intended to preserve one continuing agentic lineage and its ordinary interactive agency while the workflow retains global orchestration. See ADR-007 and ADR-008.

TURNLOCK therefore separates concerns that are commonly fused:

```text
orchestration authority
        ≠
semantic / agentic execution capability
```

The workflow owns orchestration authority. It may allocate work to deterministic computation, bounded raw LLM inference, bounded independent agents, or continuation of the main agent according to the requirements of each region. None of those execution resources becomes the global orchestrator merely by being used.

# 2. Core mental model

The system must not treat these concepts as equivalent:

```text
main agent == workflow
workflow entry == workflow
main-agent step == independent-agent step
main-agent step == raw LLM inference
independent-agent step == raw LLM inference
main-agent step == context-reconstructed child-agent call
mechanical step == tool call chosen by the main agent
workflow state == chat context
workflow completion == agent-session completion
probabilistic leaf == agent-owned global orchestration
```

They are distinct product concepts.

## 2.1 Main agent

The **main agent** is the coding agent participating in the user's surrounding interactive session.

It is the agent that has the user-facing conversational continuity before workflow entry and to which the workflow returns when execution finishes.

A main-agent step temporarily makes that agent active inside workflow execution.

The main agent does not thereby become the owner of the workflow's global control flow.

## 2.2 Workflow

A **workflow** is an executable user-defined process that owns progression across its steps after entry and until termination.

A workflow may contain mechanical phases, bounded raw-LLM inference phases, independent-agent phases, main-agent continuation phases, control-flow/composition operations, and nested workflow invocations.

It is not merely a prompt describing desired sequencing.

The workflow must retain enough execution truth to resume after temporary main-agent control.

## 2.3 Workflow invocation surface

A **workflow invocation surface** is the session-local user interaction through which a TURNLOCK workflow is selected and started.

For supported coding-agent harnesses, the ordinary invocation surface is a **natural slash command comparable to invoking a native skill**. The concrete command name, namespace, registration mechanism, and mapping between commands and workflows are intentionally not fixed yet.

The invocation surface should be small in semantic responsibility: it selects/starts workflow-owned execution rather than embedding the workflow's orchestration into the main-agent prompt.

## 2.3A Workflow artifact and TURNLOCK primitives

A **workflow artifact** is the developer-readable executable representation of a TURNLOCK workflow. A developer may author it directly or a coding agent may author it on the developer's behalf. Those are two authorship paths to the same semantic object, not two workflow classes.

**TURNLOCK primitives** are the author-facing operations that express TURNLOCK's control semantics. Their exact syntax and full set are not fixed yet, but they must represent product concepts at TURNLOCK level rather than require workflow authors to reproduce harness-specific control plumbing.

Pi-specific APIs may implement these primitives in the first integration; they are not themselves automatically TURNLOCK primitives.

## 2.4 Mechanical step

A **mechanical step** is a workflow phase whose progression is governed by executable semantics rather than by main-agent interpretation.

This specification intentionally does not yet fix which mechanical primitives exist or how they are expressed.

A mechanical step may produce state or evidence consumed by later steps, including a main-agent step.

## 2.4A Raw LLM inference step

A **raw LLM inference step** is a bounded semantic computation in which the workflow supplies an instruction and explicit context to a model and receives a result without requesting an autonomous multi-turn agent loop or continuation of the main interactive agent.

Its semantic shape is:

```text
explicit input/context → model inference → result
```

It may be executed singly or as part of declared parallel fan-out.

## 2.4B Independent-agent step

An **independent-agent step** creates a new bounded cognitive lineage for a declared task. The agent may perform autonomous multi-turn reasoning, tool use, observation, and adaptation within the capabilities granted to that step, then returns its result to the workflow.

Its semantic shape is:

```text
bounded task/context
→ independent agentic loop
→ result
→ workflow continuation
```

An independent-agent step intentionally does **not** preserve main-agent cognitive lineage. That isolation is part of the capability, not a defect. Multiple independent-agent steps may execute concurrently, whether they perform the same task or different tasks.

## 2.5 Main-agent step

A **main-agent step** is a workflow phase in which control is temporarily transferred to the main agent.

Its defining lifecycle is:

```text
workflow active
→ handoff to main agent
→ main agent active
→ main-agent phase reaches its completion boundary
→ workflow resumes
```

The completion boundary mechanism is not specified yet.

## 2.6 Invocation context and caller stack

Every workflow invocation has an **immediate caller context**: the execution context that invoked that workflow and to which normal completion returns.

For a top-level workflow, the caller is the surrounding main-agent interaction. For a nested workflow invoked from a main-agent region, the caller is that main-agent region. Nested invocations therefore form a structured caller stack conceptually:

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

This is a semantic model, not a requirement to implement a literal process stack. The invariant is structured suspension and return to the immediate caller.

## 2.7 Control ownership

Control ownership is phase-local, workflow progression is globally declared by the workflow program, and TURNLOCK is the engine that executes and tracks that progression.

```text
outside workflow:
  main agent owns ordinary interaction

inside mechanical phase:
  workflow owns execution

inside raw-LLM phase:
  workflow owns progression and the model produces a bounded semantic result

inside independent-agent phase:
  independent agent owns local autonomous execution for its bounded task
  workflow remains the enclosing progression authority

inside main-agent phase:
  main agent temporarily owns local interactive execution
  workflow remains the enclosing progression authority

after workflow termination:
  control returns to the immediate caller
```

This distinction is central to TURNLOCK.

# 3. Derived invariants

The following invariants are derived from the product intent already established. They constrain future architecture without fixing its mechanism.

## 3.1 TL-INV-001 — Workflow-orchestration invariant

For an active workflow:

```text
declared global orchestration logic = workflow program
execution of that logic = TURNLOCK engine
```

The main agent MUST NOT be required to act as the global step scheduler for the workflow, and TURNLOCK MUST NOT silently invent undeclared global strategy merely because it executes the workflow.

## 3.1A TL-INV-002 — Engine / decision-owner separation invariant

TURNLOCK MUST provide the runtime authority needed to execute, schedule, coordinate, and resume declared workflow control, but the workflow artifact remains the source of truth for the orchestration decisions that have been authored.

```text
TURNLOCK executes orchestration != TURNLOCK invents orchestration
```

A runtime optimization or harness adapter MAY choose equivalent execution mechanisms, but it MUST NOT change the declared topology or substitute new global decisions without an explicit workflow semantic that grants such authority.

## 3.2 TL-INV-003 — Mechanical-execution invariant

For a mechanical step:

```text
step execution truth != main-agent interpretation
```

The step either executes according to its mechanical semantics or produces a defined non-success outcome. Its execution must not depend on the main agent deciding whether to follow a prose instruction.

## 3.3 TL-INV-004 — Reversible-handoff invariant

For every nonterminal main-agent step:

```text
workflow → main agent → workflow
```

must be a valid control path.

A main-agent handoff MUST NOT inherently destroy the workflow's ability to resume.

## 3.4 TL-INV-005 — Repeatable-handoff invariant

A workflow MUST be able to contain more than one main-agent step.

The architecture MUST NOT assume:

```text
main-agent handoff count <= 1
```

## 3.5 TL-INV-006 — Enclosing-workflow invariant

While a main-agent step is active, the workflow remains the enclosing execution whose continuation follows that phase.

The agentic phase may have local autonomy, but it does not redefine the rest of the workflow.

## 3.6 TL-INV-007 — Resume-position invariant

After a main-agent phase completes, the system MUST be able to determine the correct workflow continuation without asking the main agent to reconstruct the workflow from memory.

## 3.7 TL-INV-008 — Invocation/return continuity invariant

Every workflow invocation MUST preserve a structured return path:

```text
immediate caller → workflow → immediate caller
```

For top-level invocation this reduces to:

```text
main agent → workflow → main agent
```

Entry into workflow execution and return from workflow completion are both first-class transitions. A nested workflow MUST NOT return directly to the root session when its immediate caller is a suspended main-agent region of another workflow.

## 3.8 TL-INV-009 — Main-agent identity/continuity invariant

Where TURNLOCK claims a **main-agent step**, that claim MUST preserve the product meaning of the surrounding interactive coding agent rather than silently substituting an unrelated generic completion.

The exact technical strength of identity/context continuity may be capability-dependent across harnesses, but any weaker mode must be named as weaker rather than presented as equivalent semantics.

## 3.9 TL-INV-010 — Workflow-state independence invariant

Sufficient workflow execution state MUST exist outside the main agent's conversational recollection so that workflow control remains well-defined across agentic phases.

This invariant does not require a particular persistence technology or durability level yet.

## 3.10 TL-INV-011 — Harness-semantics invariant

For every coding harness that TURNLOCK declares supported, the same abstract workflow semantics MUST hold:

```text
enter
→ mechanical execution
↔ main-agent handoff/resume as defined by workflow
→ terminate
→ return
```

Harness-specific integration mechanisms MAY differ.
The product-level control contract MUST NOT silently differ.

## 3.11 TL-INV-012 — Non-equivalence of cognitive execution forms invariant

Support for independent agents or raw LLM inference does not by itself prove support for a TURNLOCK main-agent step. Conversely, support for main-agent continuation does not eliminate the requirement for first-class bounded independent-agent and raw-LLM execution.

Each form MUST preserve its own semantics rather than being silently implemented as another:

```text
raw LLM inference != independent agent != main-agent continuation
```

Conformance requires satisfying the specific contracts of the execution form declared by the workflow.

## 3.12 TL-INV-013 — No-hidden-agent-orchestration invariant

An implementation MUST NOT claim workflow-owned orchestration while covertly translating the workflow into instructions that the main agent must interpret step-by-step.

The location of the source code is irrelevant; what matters is where control-flow authority actually resides.

## 3.13 TL-INV-014 — Cognitive-lineage continuity invariant

A main-agent step MUST preserve the continuing agentic lineage of the surrounding main session strongly enough that TURNLOCK does not require a normal-case export/import/reconciliation cycle merely to cross the workflow boundary.

A spawned independent agent, even with the same model, repository, tools, and a reconstructed context, is a distinct capability unless the harness can establish semantics equivalent to continuation of the current main-agent lineage.

This invariant deliberately does not prescribe same-process identity, a particular session identifier, or any concrete resume protocol.

## 3.14 TL-INV-015 — Ordinary-agency restoration invariant

A main-agent step MUST be able to restore the ordinary class of interactive coding-agent behavior required by that phase. TURNLOCK MUST NOT define main-agent participation solely as a stateless or one-shot request/response primitive.

The workflow remains the global orchestrator, but during the agentic region the main agent may use the native capabilities and user interaction normally available to it, subject to future explicit rules for completion, interruption, and authority transfer.

## 3.15 TL-INV-016 — Workflow-availability invariant

When the main agent owns control, TURNLOCK workflows that are available to that coding-agent session MUST remain invocable, including while the main agent is executing a main-agent region of another workflow.

Entering workflow-owned execution MUST NOT make the session's TURNLOCK workflow capability surface disappear merely because the current main-agent control was reached through a handoff.

## 3.16 TL-INV-017 — Nested-invocation invariant

A main-agent region MAY invoke another TURNLOCK workflow. Nested invocation suspends the immediate caller and begins a distinct workflow execution; it MUST NOT discard, replace, or implicitly complete the caller.

The semantic model MUST NOT assume nesting depth is limited to one level. Any future resource or safety limit on nesting must be explicit and must preserve structured caller semantics for every accepted invocation.

## 3.17 TL-INV-018 — Immediate-caller return invariant

For every normally completed nested workflow:

```text
caller context → nested workflow → same caller context
```

The workflow MUST return to the context that invoked it, not unconditionally to the root main-agent session.

## 3.18 TL-INV-019 — Outer-orchestration preservation invariant

Invoking a nested workflow from a main-agent region does not transfer orchestration authority over the enclosing workflow to the main agent or to the nested workflow.

Each workflow owns its own declared progression. When the nested workflow returns, the main-agent region that invoked it resumes; when that region later completes, the enclosing workflow resumes at its own declared continuation.

## 3.19 TL-INV-020 — Same-artifact authoring invariant

A workflow written directly by a developer and a workflow generated or modified by a coding agent MUST target the same semantic workflow artifact and execution model. TURNLOCK MUST NOT require a privileged agent-only workflow representation for ordinary authoring.

## 3.20 TL-INV-021 — Author-facing primitive invariant

TURNLOCK MUST expose workflow-authoring primitives that directly express the product's control concepts strongly enough that workflow authors do not have to recreate harness integration mechanics themselves.

The exact syntax is open, but the semantic dependency direction is fixed:

```text
workflow code
  → TURNLOCK primitives
  → harness integration
  → harness-specific mechanisms
```

not:

```text
workflow code
  → Pi/Claude/Codex internal control API details
```

## 3.21 TL-INV-022 — Harness-independence invariant

TURNLOCK workflow semantics MUST be defined independently of any one coding harness. A supported harness adapter realizes those semantics; it does not redefine them.

Harness-specific capability differences MAY produce explicit support limitations or capability declarations, but an implementation MUST NOT silently change the meaning of a TURNLOCK primitive per harness.

## 3.22 TL-INV-023 — Pi-reference invariant

Pi is the first reference harness and MAY shape implementation sequencing, test fixtures, and the first concrete adapter. Pi-specific mechanics MUST NOT become normative product semantics solely because Pi is implemented first.

A future second-harness implementation is expected to act as an abstraction test: concepts that cannot be stated without Pi internals must be re-examined to determine whether they are genuinely TURNLOCK semantics or reference-adapter leakage.

## 3.22A TL-INV-024 — Heterogeneous parallel composition invariant

TURNLOCK MUST allow a workflow-owned parallel region to mix independent branch types, including mechanical computation, bounded raw LLM inference, and bounded independent-agent execution. Branches of the same semantic type MAY perform the same task or different tasks. Mixed fan-out MUST preserve the lifecycle, context, authority, and result contract of each branch type while keeping fan-out, synchronization, collection, and continuation under workflow ownership.

This invariant does not require main-agent continuation to be an ordinary parallel branch; that question remains separately open.

## 3.23 TL-INV-025 — Independent-agent first-class invariant

TURNLOCK MUST allow a workflow to declare bounded independent-agent execution directly. The workflow MUST NOT be required to yield to the main agent merely so that the main agent can decide to create an agent that the workflow topology already requires.

Independent-agent execution creates a distinct cognitive lineage by design and returns a result to workflow-owned progression.

## 3.24 TL-INV-026 — Bounded-context delegation invariant

An independent-agent task MUST be conceptually capable of receiving task-specific context rather than implicitly inheriting the complete main-agent cognitive lineage. The exact context-construction API remains open, but bounded context is part of the product value of independent delegation.

The workflow author must be able to treat cognitive isolation as intentional.

## 3.25 TL-INV-027 — Parallel semantic fan-out/fan-in invariant

TURNLOCK MUST be able to express workflow-owned parallel execution of independent semantic work and subsequent synchronization/collection. Parallel branches MAY perform the same task or different tasks.

The declared topology:

```text
fan-out → concurrent semantic work → fan-in/join → continuation
```

MUST NOT require the main agent to become the scheduler merely because the concurrent branches are agentic or LLM-based.

## 3.26 TL-INV-028 — Raw-LLM inference invariant

TURNLOCK MUST expose bounded non-agentic model inference as a semantic execution form distinct from independent-agent execution and main-agent continuation.

A workflow that needs a one-shot semantic transformation MUST NOT be forced to create a multi-turn agentic loop or hand control to the main agent solely to obtain model intelligence.

## 3.27 TL-INV-029 — Minimum-sufficient cognition invariant

The workflow model MUST preserve the author's ability to choose the least powerful execution form sufficient for a region:

```text
deterministic computation
→ raw LLM inference
→ independent agent
→ main-agent continuation
```

TURNLOCK MUST NOT collapse these choices into one universal "agent step" when their cost, context, autonomy, continuity, and lifecycle semantics differ.

## 3.28 TL-INV-030 — Deterministic-orchestration / probabilistic-leaf invariant

Workflow-owned deterministic control MUST be compatible with probabilistic leaf computations. Invoking an LLM or agent does not by itself transfer authority over the workflow's global control graph.

The workflow remains responsible for declared sequencing, branching, fan-out, synchronization, and continuation unless it explicitly enters a main-agent region or another execution region with different local authority semantics.

## 3.29 TL-INV-031 — Workflow expressive-power invariant

TURNLOCK's deterministic orchestration engine MUST be expressive enough that known control decisions can remain executable workflow logic rather than being delegated back to an agent for lack of orchestration primitives.

At the semantic level this includes the ability to compose, as required by a workflow:

```text
mechanical computation
sequencing and conditional progression
iteration where the workflow declares it
parallel fan-out and join
raw LLM inference
independent-agent execution
main-agent continuation
nested workflow invocation
structured return to caller
```

This invariant does not require a large primitive catalog. TURNLOCK SHOULD prefer a small set of orthogonal primitives capable of expressing this space over a collection of domain-specific commands.

## 3.30 TL-INV-032 — Authorship / execution-authority separation invariant

The identity or nature of a workflow's author MUST NOT, by itself, confer
runtime orchestration authority over that workflow.

A developer, coding agent, LLM planner, or higher-level system MAY author or
generate a workflow with any topology expressible through supported TURNLOCK
primitives. Once execution begins, the workflow artifact remains the source of
truth for its declared orchestration, and TURNLOCK remains the engine
responsible for executing, coordinating, and tracking that orchestration.

```text
authorship of workflow
!=
ownership of workflow execution
```

An agent-authored or dynamically generated workflow MUST be independently
represented and executed. It MUST NOT silently degrade into prose or
instructions that its author must interpret, remember, or schedule during
execution.

Authorship does not prevent an author that is also available under an existing
execution form from later participating through a region explicitly declared by
the workflow. In particular, when the author is the existing main agent, a
main-agent region MAY continue that same cognitive lineage for bounded local
work. Authorship does not grant global progression authority, and the workflow
resumes at its declared continuation after the region completes.

# 4. Current boundaries — intentionally not yet specified

The following questions are important but are **not yet answered by the product discussion** and therefore must not be accidentally frozen as architecture:

- How a main-agent phase signals that it is complete and yields control back.
- Whether the user may interact with the main agent during a main-agent phase, and how such interaction affects completion.
- What cancellation, interruption, timeout, and failure mean in each phase.
- Whether workflow execution state must survive harness/process/machine crashes, and at what durability level.
- The exact workflow authoring language, library surface, file format, and packaging convention; only the same-artifact/primitives contract is fixed.
- The exact set of mechanical step primitives.
- Whether workflows are always external scripts or may have other executable representations.
- How values/results/context cross the workflow ↔ main-agent boundary.
- How permissions and tool authority transfer during a main-agent phase.
- What exact continuity guarantee is achievable or required per supported harness.
- Whether a temporarily unavailable main-agent handoff can be retried, degraded, or must fail closed.
- How observability, tracing, replay, and debugging should work.
- Whether multiple sibling/top-level workflows may execute concurrently in one interactive coding-agent session; structured nested invocation is already allowed.
- Whether implementations impose explicit resource/safety limits on nesting depth, and how such limits are surfaced without changing immediate-caller return semantics.
- What security/trust model applies to user-authored workflow code.
- How a workflow selects models/providers and expresses inference budgets, model parameters, structured outputs, or provider fallbacks for raw LLM calls.
- How independent-agent context is constructed, materialized, isolated, and size/budget constrained.
- Which tools/capabilities an independent agent may receive and how those capabilities are declared.
- What lifecycle limits apply to independent agents, including turn, token, time, and tool-use budgets.
- Exact fan-out/fan-in failure semantics, partial-result behavior, cancellation propagation, and concurrency/resource limits.
- Whether parallel branches share any mutable workflow state and, if so, under what synchronization rules.

These are future derivation points. Their solutions must preserve the invariants above.

# 5. Architectural implications already forced by the intent

This section records only implications that follow directly from the current invariants. It deliberately avoids selecting concrete mechanisms.

## 5.1 There must be an execution authority outside ordinary main-agent reasoning

Because the workflow owns progression and mechanical steps must execute independently of agent interpretation, some execution authority must exist that is not merely the main agent following prose.

This does not determine whether that authority is implemented as a script process, extension runtime, embedded interpreter, supervisor, harness plugin, protocol peer, or another mechanism.

## 5.2 There must be a bidirectional control boundary

The architecture must support both transitions:

```text
workflow → main agent
main agent → workflow
```

Supporting only workflow → agent invocation is insufficient.

## 5.3 There must be an explicit structured return path

The architecture must support workflow completion as a return to the immediate caller:

```text
workflow → immediate caller context
```

For a top-level invocation, that caller is the surrounding main-agent interaction. For a nested invocation, that caller is the suspended main-agent region that invoked the workflow. The implementation may use any mechanism, but it must preserve this structured return relationship.

## 5.4 Workflow progression cannot live only in prompt context

Because the workflow resumes after main-agent execution and may do so repeatedly, continuation position and sufficient execution state require a representation independent of the main agent's memory.

## 5.5 Harness integration is a capability boundary

Claude Code, Pi, Codex, and other harnesses may expose different control primitives.

TURNLOCK will therefore eventually need to distinguish:

```text
product semantics
from
harness-specific realization capability
```

The implementation may need different integration strategies, but those strategies must be evaluated against the same reference scenario rather than defining separate products.

## 5.6 The main-agent capability surface must survive handoff

Because a main-agent region restores ordinary interactive agency and may invoke another TURNLOCK workflow, the integration must preserve enough of the session's workflow-discovery/invocation surface for the main agent to use available workflows while inside a handoff region.

This does not require a particular frontmatter format, command registry, or harness API. It requires only that workflow entry through TURNLOCK not erase the main agent's ability to discover, select, or invoke workflows that the session exposes.

## 5.7 Nested invocation requires structured suspension, not replacement

The execution model must be able to suspend a caller context while a nested workflow runs and later resume that same caller context. A flat "current workflow" slot that is overwritten by nested invocation would violate the immediate-caller return invariant unless it provides equivalent structured semantics by another mechanism.

## 5.8 Authoring primitives must sit above harness plumbing

Because both developers and coding agents author workflows against TURNLOCK semantics, the public workflow-authoring surface must not require knowledge of Pi-specific control hooks merely to express a main-agent region, mechanical step, nested invocation, or structured return.

The first Pi implementation may internally translate those primitives to Pi-specific mechanisms. That translation belongs below the workflow artifact.

## 5.9 Pi should be optimized as the first integration without owning the ontology

The first implementation should use Pi's capabilities fully rather than artificially pretending every harness is identical. However, every Pi-specific mechanism introduced should be classifiable as either:

```text
TURNLOCK semantic concept realized through Pi
```

or:

```text
Pi adapter implementation detail
```

If it fits neither category, the architecture has likely allowed the reference harness to leak into the product model and requires an explicit decision.

## 5.10 The runtime needs more than one semantic execution adapter

Because raw LLM inference, independent-agent execution, and main-agent continuation have different semantics, the runtime cannot treat them as one generic "AI call" without losing product meaning. The architecture must preserve their distinct lifecycle and context contracts even if one harness/provider happens to implement multiple forms through related APIs.

## 5.11 Parallel orchestration must exist outside agent judgment

Workflow-owned fan-out/fan-in requires an execution authority capable of starting independent branches, tracking their completion/results, and resuming declared continuation without asking the main agent to remember or schedule the parallel graph.

That authority must support heterogeneous parallel graphs rather than assuming all branches use one execution primitive. A single fan-out may combine deterministic computation, bounded raw LLM calls, and bounded independent agents, while preserving the distinct lifecycle and context contract of every branch.

This implication does not select a concurrency mechanism, scheduler, worker model, or process topology.

## 5.12 Context construction becomes an explicit boundary

Independent agents and raw LLM calls derive value from receiving deliberately bounded context. TURNLOCK therefore needs an architectural place where task inputs/context are assembled without conflating that assembly with inheritance of the main-agent conversation.

The exact representation and dataflow API remain open.

## 5.13 The orchestration core must remain richer than a prompt sequencer

Because workflows may combine general computation, concurrency, semantic calls, independent agency, main-agent continuation, and nested composition, TURNLOCK cannot satisfy the product intent by merely expanding prompts sent to an agent. Its executable control layer must represent the declared topology directly.

## 5.14 The runtime is an orchestration engine, not an orchestration author

TURNLOCK requires real execution authority: it must schedule declared regions, track workflow state, coordinate parallel branches, realize harness handoffs, and resume continuations. That makes TURNLOCK an orchestration engine.

However, the source of declared global orchestration decisions remains the workflow program. The runtime architecture must therefore separate:

```text
workflow semantics / authored topology
from
runtime execution / scheduling machinery
```

A scheduler, adapter, optimizer, or execution backend may select equivalent mechanisms for fulfilling a declared primitive, but it must not silently become a policy engine that invents a different workflow.

# 6. Non-goals implied by the current product intent

At the current stage, TURNLOCK is not defined as:

- a replacement coding agent;
- a subagent-only framework in which every semantic task is forced through independent agents;
- a prompt format for asking the main agent to follow longer procedures;
- a requirement that all work become deterministic;
- a requirement that agentic reasoning disappear from development workflows;
- a requirement that every semantic task use the main agent or any other single cognition form;
- an agent framework where every intelligent step is semantically interchangeable with every other agent call;
- a harness-specific feature whose semantics are valid only inside one vendor's coding client;
- a mandatory graphical/no-code workflow builder;
- a separate agent-only workflow language distinct from the artifact developers edit.

Future features may include some adjacent capabilities, but they must not blur the control model that defines the product.

# 7. Product test

Before debating implementation sophistication, a candidate TURNLOCK architecture should answer one question:

> Can it execute the reference sequence below with the stated control ownership, using the actual main agent semantics it claims to support?

```text
main agent
  > natural slash-command workflow invocation
  > workflow
  > mechanical step A
  > main-agent step A
  > mechanical step B
  > main-agent step B
  > mechanical step C
  > workflow finished
  > main agent
```

For each transition, the architecture should be able to identify:

```text
who currently owns control?
what makes the current phase complete?
who decides what phase comes next?
where is continuation state held?
what exactly makes an "agent step" the main agent rather than another agent?
how does control return after the phase?
```

If the answer to "who decides what comes next?" is repeatedly "the main agent reads the remaining instructions and decides", the architecture has drifted away from TURNLOCK's product intent.

The architecture must also demonstrate nested composition:

```text
main agent
  > workflow A
  > main-agent region A
      > workflow B
      > main-agent region B
      < workflow B
  < main-agent region A
  < workflow A
main agent
```

The critical proof is that workflow B returns to its immediate caller (main-agent region A), not directly to the root session, and that workflow A resumes only after region A later completes.

The architecture must additionally demonstrate that the workflow can own an explicitly declared semantic fan-out/fan-in without turning the main agent into the scheduler, for example:

```text
prepare mechanically
→ run N raw LLM calls concurrently
→ in another declared fan-out, run mechanical + raw-LLM + independent-agent branches concurrently
→ aggregate
→ run independent agents concurrently
→ join
→ continue mechanically or hand off to the main agent
```

For each semantic region it must be possible to answer:

```text
why is this raw inference vs independent agency vs main-agent continuation?
what context is intentionally provided?
who owns local execution?
who owns global progression?
how are concurrent branches joined?
what value returns to the workflow?
```

The authoring surface must additionally prove that the same workflow can be produced through either direct developer authoring or coding-agent authoring using public TURNLOCK primitives, without requiring a privileged generator path. The Pi implementation must prove the complete reference scenarios while keeping Pi-specific mechanisms below the TURNLOCK workflow semantics boundary.

# 8. Short form

TURNLOCK can currently be summarized as:

> **A harness-independent orchestration engine for coding-agent sessions that executes workflow-authored deterministic control, using the same TURNLOCK primitives whether authored by a developer or coding agent, and composes mechanical computation, bounded raw LLM inference, bounded independent agents, continuation of the user's main coding agent, concurrency, and nested workflows. The workflow program owns the declared orchestration logic; TURNLOCK executes it. Pi is the first reference harness used to prove the model.**

Or as a control equation:

```text
workflow program = declared orchestration logic / orchestration program
TURNLOCK = orchestration engine / runtime that executes it

mechanical computation = non-semantic executable work
raw LLM inference = bounded stateless semantic function
independent agent = bounded autonomous cognitive fork
main agent = continuation of the existing interactive cognitive lineage

parallelism = workflow-owned fan-out / join
nested workflow = suspended caller + independent workflow progression + caller resumption
slash-command invocation = natural session-local workflow invocation surface
workflow end = structured return to immediate caller
workflow authoring = developer or coding agent → same TURNLOCK artifact/primitives
workflow authorship != workflow execution ownership
Pi = first reference integration, not the semantic definition
```

The guiding allocation rule is:

```text
use the minimum sufficient form of computation or cognition for each region
```

The product is successful only if these roles remain distinct in the real execution model and if known orchestration decisions can remain in the workflow rather than being pushed back into an agent merely because the workflow lacks expressive power.

# 9. Formal specification governance

TURNLOCK maintains a formal state-machine specification alongside this normative prose specification for semantics that materially involve state, control ownership, lifecycle, invocation/return, nesting, concurrency, synchronization, failure, cancellation, or temporal progress. ADR-015 governs this relationship.

The prose specification remains the normative statement of product meaning. The TLA+ model is an abstract executable model used to test relevant state/temporal consequences and to discover counterexamples before implementation choices harden. It MUST remain implementation-independent and harness-agnostic at the core semantic layer.

Every invariant in Section 3 has a stable `TL-INV-xxx` identifier. Section numbering and titles may evolve; published invariant IDs are stable traceability identities.

Formal traceability is maintained in the machine-readable manifest:

```text
formal/verification.yaml
```

A human-readable mapping in `docs/formal/invariant-mapping.md` is generated from that manifest. For every formally modeled invariant, the manifest is intended to trace the stable product ID to its TLA+ module/property, the state variables and actions/transitions used by that formalization, the focused/integrated TLC configurations that exercise it, and later implementation/conformance tests. The mapping MUST also be mechanically invertible so that a changed TLA+ property, state variable, or action can identify potentially affected product invariants.

The manifest describes verification intent and traceability. Actual TLC execution evidence is a separate machine-readable artifact class under `formal/results/`, governed by `formal/tlc-result.schema.json`. A `checked` claim MUST identify successful run evidence for a concrete repository revision, TLC/model configuration, checked properties, and explicit finite bounds. Presence in the manifest MUST NOT be interpreted as successful TLC verification.

Automated traceability checks SHOULD enforce referential integrity once mappings become executable: referenced TLA+ modules, properties, variables, actions/transitions, and TLC configurations must exist. Such checks do not prove semantic correspondence between prose and formula; that correspondence remains a formal-review obligation.

TURNLOCK's formal verification organization has two complementary modes:

```text
focused exploration
→ restrict the same semantic model to a mechanism/property for fast diagnosis

integrated exploration
→ exercise all currently-formalized core mechanisms together within finite bounds
```

Focused configurations are development accelerators, not substitutes for integrated verification. At least one integrated configuration MUST remain capable of composing all currently-formalized core execution forms in one state space. The project should maintain multiple integrated exploration budgets such as smoke, standard, and stress.

A semantic change affecting the formal state machine should normally run the relevant focused checks plus an integrated smoke exploration. Larger integrated runs are governed by CI/release policy.

TLC exploration is necessarily finite. "Integrated" means the formalized mechanisms are connected in the same abstract model; it does not claim exhaustive exploration of an unbounded real-world system.

Safety and liveness are distinct obligations. For example:

```text
safety:  a nested workflow never resumes the wrong caller
liveness: under the required fairness assumptions, a normally completable nested workflow eventually resumes the correct caller
```

Not every product invariant is necessarily expressible or useful as TLA+. DX and semantic-quality requirements may be explicitly marked `not-applicable`; state, ordering, ownership, lifecycle, nesting, concurrency, synchronization, and progress rules are strong formalization candidates.
