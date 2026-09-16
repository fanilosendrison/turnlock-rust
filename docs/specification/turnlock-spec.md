# TURNLOCK — Requirements, Invariants, and Architectural Implications

> Working product specification derived from the current product discussion.
>
> This document intentionally starts from product intent and derives invariants before fixing implementation mechanisms. Terms such as process model, IPC, daemon, session identifiers, adapters, protocol shape, storage engine, or concrete harness APIs are deliberately left unspecified unless the product contract requires them.

# 0. Product intent — governing user experience

This section is normative for the current product direction. It states the
product outcome that lower-level design exists to serve. It is ratified by
ADR-001 through ADR-014 and ADR-016 in `../adr/`, which record the chronological
product decisions that produced the current contract. ADR-018 establishes
minimum completed-execution inspectability. ADR-020 and ADR-021 clarify
independent-agent context provenance and completion/output semantics. ADR-022
defines workflow-declared invocation and its structured call/return semantics.
ADR-023 clarifies the caller-context and continuation distinction for nested
workflow invocations. ADR-024 establishes effective execution-condition
provenance for conditions TURNLOCK selects, binds, explicitly supplies, or
resolves. ADR-027 binds every accepted workflow invocation to a stable
governing workflow definition determined no later than invocation acceptance.
ADR-015 governs how this normative specification co-evolves with the formal
TLA+/TLC model and verification manifest.

If a future implementation admits several mechanisms, the conforming mechanism is the one that preserves this product intent and the derived invariants. A technical convenience is not sufficient reason to weaken the product promise. If a later design weakens one of these user-visible guarantees, that weakening must be explicit in a new ADR rather than emerging accidentally from implementation constraints.

## 0.1 Product definition: user-authored workflows inside coding-agent sessions

TURNLOCK exists so that a user working inside an interactive coding-agent session can **build and execute workflows whose global orchestration is owned by executable workflow logic rather than by the main agent, while still being able to compose the appropriate form of computation or cognition at each explicit region**.

The product is not merely a prompt library, a large skill, a subagent launcher, or a generic LLM workflow engine. Its defining property is that **the workflow program owns the declared orchestration logic, while TURNLOCK is the engine/runtime that executes that logic** and makes different execution resources available as first-class leaves or bounded regions.

The current execution spectrum is:

```text
mechanical execution
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

The completed execution remains sufficiently inspectable at TURNLOCK's
semantic boundary for user- or system-led evaluation and iterative refinement.

Effective conditions TURNLOCK selects, binds, explicitly supplies, or resolves
remain attributable to the execution scopes they govern and capturable at that
boundary without making TURNLOCK the evaluator or optimizer.
```

The governing promise is:

> **The workflow program owns the declared orchestration logic; TURNLOCK is the orchestration engine that executes it. The workflow can compose mechanical execution, bounded LLM inference, bounded independent agency, and continuation of the main interactive agent as distinct execution forms. Probabilistic or autonomous regions do not become the global orchestration decision-maker merely by being invoked, completed workflows return structurally to their immediate caller, completed execution exposes enough actual TURNLOCK-visible behavior for external understanding, evaluation, and iterative refinement, and effective conditions TURNLOCK selects, binds, explicitly supplies, or resolves remain attributable to the execution scopes they govern and capturable at its semantic boundary. Evaluation and optimization policy remain external to TURNLOCK core.**

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

For a nested invocation, the immediate caller is the calling execution context
inside the enclosing workflow. That caller context preserves a return-bearing
continuation while the callee executes. An immediate caller context and its call
continuation are distinct: the caller is the context that invoked the workflow,
while the continuation is the preserved return state of that context.

For an agent-selected invocation, the immediate caller is the main-agent region:

```text
main-agent region A
  → workflow B
  → workflow B terminates
  → main-agent region A resumes
```

For a workflow-declared invocation, the immediate caller is the workflow
execution context inside the enclosing workflow that performs the declared call.
That caller context preserves the workflow-declared post-call continuation while
the callee executes.

Workflow completion MUST therefore have a defined return path to the **immediate invocation context** rather than unconditionally jumping to the root session, leaving the user stranded in a separate automation context, or requiring manual reconstruction of the suspended caller.

For top-level workflows, this preserves the original promise that the ordinary interactive session resumes when the workflow ends.

For nested workflows, inner completion returns to the immediate caller. For a workflow-declared invocation, normal completion makes the caller's preserved workflow-declared post-call continuation eligible according to the enclosing topology. For an agent-selected invocation, normal completion resumes the same main-agent region, and the enclosing workflow resumes its own declared continuation only after that main-agent region itself completes.

## 0.7 Mechanical work must not require agent interpretation

A workflow may contain steps whose progression is sufficiently specified that it
can execute mechanically. Section 2.4 owns the canonical meanings of
**mechanical execution** and **mechanical step**. In this product-intent context,
the consequence is that execution and control authority, rather than
computational determinism, distinguishes mechanical work.

Examples may eventually include commands, checks, transformations, waiting,
event handling, branching, state transitions, validation, or other executable
operations. A mechanical region MAY be deterministic, nondeterministic,
probabilistic, dependent on external state, or driven by external events. It may
wait for information that was not known before execution.

The invariant is:

> **If a workflow step is defined as mechanical, its correct progression follows executable workflow semantics together with runtime inputs, results, state, or events. It must not require discretionary agent judgment to supply a missing orchestration decision.**

This is the core reliability gain TURNLOCK seeks over encoding the whole process
in a skill or prompt. It does not promise that equal inputs produce an identical
output, path, schedule, trace, or replay.

A mechanical region MAY consume a result produced by an LLM or agent and select
among continuations already declared by workflow semantics. The origin or
variability of that result does not make the consuming region agent-mediated or
transfer global orchestration authority to its producer.

## 0.8 The workflow, not the main agent, owns global progression

During an active workflow, the workflow is the authority for **where execution is in the workflow** and **what phase comes next**.

The main agent may own a main-agent phase while that phase is active, but that temporary ownership does not make the main agent the global workflow orchestrator.

Conceptually:

```text
workflow owns global progression

mechanical phase:
  TURNLOCK executes mechanical semantics
  workflow semantics govern permitted progression

main-agent phase:
  workflow yields local control
  main agent acts
  main agent completes/yields
  workflow resumes global progression
```

Local semantic or discretionary authority inside an explicitly declared
main-agent or independent-agent region is distinct from global orchestration
authority. Such an agent MAY explore, edit, test, react to evidence, and choose
local tactics within its region.

For an independent-agent region, the workflow-declared task boundary is semantic
rather than an exhaustive whitelist of files, actions, or hypotheses: work may
follow evidence into another module when it remains directed toward the declared
task and uses available authority. The independent agent MAY exercise available
authority but MUST NOT unilaterally create additional TURNLOCK-governed semantic
or orchestration authority; local desire alone cannot do so. A separately
accepted TURNLOCK semantic may explicitly define a specific TURNLOCK capability,
but general filesystem, tool, OS, repository, and sandbox permissions supplied
by the surrounding execution environment are not owned by TURNLOCK core.
Section 0.8B defines that responsibility boundary.

A result of local work MAY select among continuations related to the result by
executable workflow semantics; it does not thereby create a new orchestration
possibility, skip a phase, rewrite the enclosing graph, or make the agent owner
of global progression.

Every decision required for global workflow progression MUST be represented by
executable workflow semantics. Those semantics MAY explicitly delegate a
bounded decision to a declared agentic region, but they MUST define how the
permitted result relates to declared continuations. The workflow MUST NOT reach
an underspecified control point where an agent is expected to infer, remember,
or reconstruct what the global workflow should do next.

Therefore the workflow's correctness MUST NOT rely on the main agent remembering
the remaining control-flow graph after every agentic phase.

## 0.8A TURNLOCK executes orchestration; it does not invent it

Section 2.7 owns the canonical meanings of **control ownership** and
**workflow-owned control**. At the product-intent level, the workflow's ownership
of declared orchestration logic does not make TURNLOCK absent from execution.
TURNLOCK is the runtime/engine that interprets or executes the workflow program,
tracks its declared progression, and realizes its primitives against the
available harness and execution resources.

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

## 0.8B Local execution capability is not TURNLOCK orchestration authority

TURNLOCK core does not define, and MUST NOT invent, a general permission system
over the local actions of execution resources. ACL/RBAC, filesystem permissions,
path-based permissions, tool allowlists, capability tokens, sandboxing,
container permissions, workflow-artifact-specific read/write rules, a generic
local grant/revoke authority system, a special “meta-workflow” class, and a
privileged class reserved to official TURNLOCK workflows are outside TURNLOCK
core.

```text
TURNLOCK orchestration authority
!=
general operational authority over the surrounding environment

filesystem/tool capability
does not imply
TURNLOCK orchestration authority
```

Restrictions on local access and local actions are supplied by the surrounding
execution environment, harness, sandbox, or user-controlled environment unless
a separately accepted TURNLOCK semantic explicitly defines a specific
capability. If the environment of an execution resource permits modifying a
repository file, TURNLOCK core does not add a second permission that treats a
workflow source artifact as specially forbidden merely because it contains a
TURNLOCK workflow.

An execution resource may therefore inspect a workflow, propose a modification,
create a workflow, modify another workflow, modify the workflow whose definition
govers the currently active invocation, or produce a new version of a workflow
when its environment permits those local actions. Such actions are local
execution and authoring effects; they are not TURNLOCK orchestration authority.
TURNLOCK MUST NOT infer a workflow's purpose or intent to decide whether it may
modify workflows, and no meta-workflow flag or workflow-authorship permission
flag exists.

The boundary is general across execution resources:

```text
execution resource performs local action
→ local effect may occur according to its environment

BUT

local effect
↛ implicit change of the current invocation's governing orchestration
```

The governing orchestration of an accepted invocation remains immutable under
Section 0.13E and `TL-INV-037`. A source-artifact edit is not a mutation of the
governing definition; a later invocation may bind to the edited artifact under
its own resolution semantics. Active replanning, active rebinding, and
replacement of the governing workflow definition of an accepted invocation are
outside and contrary to the current product contract, not a reserved future
capability.

TURNLOCK non-conformance is therefore not merely that an execution resource
edited a workflow file. Non-conformance is an ordinary local action that
changed the governing definition of an already accepted active invocation, a
local action that introduced an undeclared global transition into the current
invocation, or a runtime that treated local filesystem/tool capability as
authority to replace or replan the current global orchestration.

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
0. mechanical execution
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
  → declare local task and explicit initial cognitive context
  → start a fresh independent cognitive lineage
  → agent performs autonomous multi-turn local work
  → if normal completion occurs, TURNLOCK recognizes it
  → required output, if any, becomes available
  → workflow follows its declared continuation
```

The independent agent exists precisely because a cognitive fork can be useful.
Its initial cognitive context is supplied explicitly through workflow semantics
rather than inherited implicitly from the main-agent lineage. The workflow may
supply main-agent-derived summaries, artifacts, files, prior results, or other
declared information, and the agent may acquire further information during its
own work. Its intermediate exploration does not need to become part of the
main-agent lineage.

The workflow owns the declared task and global continuation; the agent owns its
local strategy and tactics. The task is a semantic mission boundary, not an
exhaustive file or action whitelist. The agent may exercise available authority
but cannot expand that authority unilaterally. This boundary concerns
TURNLOCK-governed semantic and orchestration authority; general local
permissions are supplied by the surrounding execution environment, as defined
in Section 0.8B. None of these structural and authority boundaries requires a
maximum turn, token, tool-call, cost, or wall-clock budget, a timeout,
cancellation rule, or guaranteed completion.

A child agent spawned internally by the main agent remains part of that main
agent's ordinary local delegation unless the workflow explicitly declares the
child as a first-class TURNLOCK independent-agent region.

TURNLOCK MUST also be able to express parallel independent-agent work under workflow ownership. Parallel agents may receive:

```text
the same task
  → independent attempts / reviews / judgments

or

different tasks
  → decomposition / specialization
```

The workflow, not the main agent, owns declared fan-out, synchronization, collection, and subsequent progression when that topology is part of the workflow definition.

This matters because workflow-owned control intentionally withholds undeclared
global decision-time flexibility from an agentic orchestrator. TURNLOCK
compensates by making the workflow-declared orchestration surface expressive
enough that known orchestration decisions do not need to be pushed back into a
main-agent prompt merely because they involve semantic work, concurrency, or
delegation.

## 0.10B Raw LLM inference is a distinct first-class semantic primitive

Some semantic tasks do not require an agentic loop at all. When the workflow already has the needed inputs and only needs a bounded semantic transformation, a direct model inference can be more appropriate than either an independent agent or the main agent.

Conceptually:

```text
explicit instruction + explicit context
                  ↓
       one semantic inference operation
                  ↓
                result
```

A raw LLM call does not imply an autonomous observe/reason/act loop, persistent
independent cognitive lineage, interactive session continuity, or access to the
ordinary main-agent harness loop. It is intentionally narrower, and its result
boundary is constitutive of the primitive.

`One-shot` describes this TURNLOCK semantic operation rather than its physical
provider realization. It does not require exactly one HTTP request, provider
attempt, model call, or response-delivery mode. `Bounded` likewise introduces no
maximum tokens, cost, time, retries, or other resource budget and no guarantee
that every started operation completes.

Representative uses include classification, extraction, summarization, scoring, ranking, rewriting, adjudication, or another bounded semantic transformation for which one inference is sufficient.

TURNLOCK MUST be able to express multiple raw LLM calls concurrently when the workflow declares them independent. Those calls may perform the same task for diversity/redundancy or different tasks for decomposition.

The exact provider, model-selection surface, inference parameters, context format, structured-output mechanism, and budgeting controls remain open. What is fixed is that **bounded non-agentic LLM inference is semantically distinct from both independent-agent execution and main-agent continuation**.

## 0.10C Parallel fan-out may be homogeneous or heterogeneous

TURNLOCK parallelism is not limited to repeating one execution primitive. When branches are independent and the workflow declares their topology, a single fan-out MUST be able to contain heterogeneous branch types.

For example:

```text
fan-out
  ├→ mechanical execution
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
- each branch retains the lifecycle, context, authority, completion, effects, and declared output semantics of its own execution form;
- the workflow owns branch creation, synchronization, collection, and declared continuation.

This capability matters because the workflow author may want to combine cheap
bounded inference, richer autonomous delegation, and mechanical execution in one
explicit concurrency topology rather than split them into artificial sequential
phases.

This decision does **not yet assert that main-agent continuation can participate as an ordinary concurrent branch**. Main-agent continuation has unique session-lineage and interactive-control semantics; concurrency involving it remains a separate semantic question.

## 0.10D Workflow-owned control may compose varying results

TURNLOCK's workflow-owned-control goal concerns the authorization and explicit
representation of global progression. It does not imply bit-for-bit determinism
of any computation or one possible execution path.

A workflow may explicitly compose operations whose behavior or results are
probabilistic, nondeterministic, externally dependent, or event-driven:

```text
mechanical execution
raw LLM inference
independent agent
main-agent continuation
```

while retaining workflow-owned control:

```text
workflow semantics declare executable regions and permitted transitions
runtime inputs / results / state / events select among declared possibilities
TURNLOCK executes the selected sequencing / branching / fan-out / join
no execution resource invents an undeclared global continuation
```

Therefore:

> **Workflow-owned control does not require deterministic computations or results. A runtime result may select among declared possibilities; it does not thereby create new orchestration possibilities.**

The relevant question is not whether a step can vary, but whether each change in
global control is authorized by executable workflow semantics. TURNLOCK core
orchestration semantics do not by themselves imply computational determinism,
output determinism, identical traces, replayability, or run reproducibility.

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

The restored ordinary agency can include repository edits according to the
capabilities of the surrounding environment, including edits of workflow
artifacts. Such local edits are authoring actions, not orchestration mutations:
they do not alter the governing definition or the declared global progression of
the already accepted invocation (Section 0.13E, `TL-INV-037`). A later
invocation may bind to an edited artifact under its own resolution semantics,
and active replanning or rebinding of the current invocation remains outside
the current product contract. Section 0.8B defines the responsibility boundary
between environment-provided local capability and TURNLOCK orchestration
authority.

A one-shot LLM request/response is nevertheless a valid **separate** TURNLOCK primitive when that narrower semantic execution form is what the workflow requests. The prohibition here is only against implementing a declared main-agent continuation as though it were such a call.

This lets TURNLOCK combine two properties that are otherwise often traded
against each other:

```text
mechanical, workflow-owned progression outside agentic regions
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

## 0.13B Completed execution remains inspectable for iterative refinement

A TURNLOCK workflow is a reusable executable representation of part of a user's
working method. Its execution MUST NOT become an opaque event after completion.
A completed execution must make enough of its actual TURNLOCK-visible behavior
inspectable for a user or higher-level system to understand and evaluate how the
workflow progressed in practice without reconstructing it from human or agent
recollection.

The broader product loop is:

```text
author workflow
→ execute workflow
→ inspect and evaluate actual behavior
→ refine workflow
→ execute again
↺
```

Debugging is one use of this capability, not its complete purpose. The product
value is that real execution can inform user- or system-led iterative refinement
of the reusable workflow artifact.

TURNLOCK owns the minimum execution-truth responsibility at its semantic
boundary. That boundary includes workflow-mediated structure, execution
boundaries, explicitly exposed inputs and results, and TURNLOCK-visible facts
relevant to declared progression. A user, the main agent, an external evaluator,
or a higher-level workflow or system defines what good means, performs any
evaluation or comparison, decides what should change, and modifies or optimizes
the workflow.

This requirement does not make TURNLOCK itself an evaluator, benchmark system,
run comparator, experiment manager, or workflow optimizer. It does not require
disclosure of private agent reasoning or automatically require every tool call
inside an agentic region to be recorded. Nor does it imply replay,
computational or output determinism, identical traces, cross-run comparability,
reproducibility, permanent retention, execution proofs, or a particular tracing,
storage, telemetry, or user-interface mechanism.

## 0.13C Evaluation and optimization policy remain outside TURNLOCK core

Section 0.13B requires TURNLOCK to expose enough actual execution truth for
evaluation. Exposing that truth is distinct from owning evaluation or
optimization policy, and the product does not treat those responsibilities as
one implied package.

TURNLOCK core is the workflow execution substrate. It MUST NOT define a
universal evaluation objective, universal quality metrics, a default
superiority relation between workflows or executions, experiment policy, or an
autonomous workflow optimizer. Nothing in the product definition requires a
privileged evaluator abstraction, and neither workflow evaluation nor workflow
optimization becomes a core TURNLOCK capability merely because completed
executions are inspectable.

Evaluation objectives and criteria are supplied and owned outside TURNLOCK core
policy by an explicitly responsible user, coding agent, evaluator, higher-level
system, or ordinary TURNLOCK workflow. Those actors may interpret execution
truth, form assessments, compare executions where their own contracts make
comparison meaningful, and propose or author an improved workflow.

Evaluation or optimization logic MAY itself be expressed as an ordinary
TURNLOCK workflow. That execution is ordinary authored behavior under the same
TURNLOCK semantics and authority boundaries as any other workflow; it does not
become privileged runtime machinery merely because it evaluates another
execution or proposes a workflow change.

If evaluation or optimization produces an improved workflow artifact, that
result is workflow authorship. It does not authorize the TURNLOCK runtime to
mutate the orchestration of a currently executing invocation, and it does not
transfer execution authority to the evaluator or optimizer.

The product rule is:

```text
TURNLOCK makes workflows evaluable and optimizable
!=
TURNLOCK core is the evaluator or optimizer
```

The relationship is:

```text
workflow W
    → TURNLOCK executes W
    → inspectable actual execution truth
    → user / coding agent / evaluator / higher-level system / ordinary workflow
    → evaluation against an explicitly supplied objective
    → possible authoring of workflow W'
    → TURNLOCK later executes W'
```

This boundary does not prohibit future TURNLOCK-adjacent modules, libraries,
profiles, or tools for evaluation and optimization. It establishes that they
are not part of the current core product contract and that any future proposal
adding native evaluator interfaces, experiment concepts, comparison contracts,
optimizer machinery, privileged mutation authority, or stronger evaluation
guarantees requires its own accepted product decision.

## 0.13D Effective execution-condition provenance remains capturable

TURNLOCK MUST preserve the attribution of effective execution conditions that it
selects, binds, explicitly supplies, or resolves at its semantic boundary to the
execution scopes they govern. That relationship must remain semantically
distinguished and exposable or capturable at an execution boundary rather than
existing only as hidden transient adapter state or requiring reconstruction from
later mutable state, human recollection, or agent recollection.

The product layers remain distinct:

```text
workflow execution
        ↓
actual execution truth
+
effective execution-condition provenance
        ↓
external evaluation or optimization policy
```

This obligation exists now because evaluation, comparison, reproducibility, and
replay features can be added later, while provenance discarded when TURNLOCK
possesses the governing information may not be recoverable later. It does not
accept any of those future features.

The universal floor applies to conditions TURNLOCK itself selects, binds,
explicitly supplies, or resolves. Conditions outside TURNLOCK's observation or
control MAY remain unavailable or unknown. Unknown MUST NOT be presented as
known-equal across executions or as evidence that no relevant difference
exists.

Exact-value disclosure is not required by this provenance floor. When TURNLOCK
knows a specific effective condition but its underlying value is protected or
unsafe to disclose, a semantic representation containing information specific
to that known condition MUST remain bound to its effective-condition occurrence
and governed execution scope and capturable through TURNLOCK's required
realizable semantic-boundary capture handoff. Protection or redaction MUST NOT
substitute away that condition-specific information before or during the
handoff. An occurrence label or generic protected marker alone is not
condition-specific information. Such a marker MAY be a consumer-visible view,
but it is insufficient as the sole provenance representation when TURNLOCK
possessed more specific condition provenance.

The required semantic-boundary capture opportunity is the realizable
semantic-boundary capture handoff, not a minimum storage duration or retention
interval. Before TURNLOCK may irreversibly lose provenance required by this
obligation, that provenance must reach a semantic-boundary interaction through
which an eligible conforming capture context could acquire the required
condition-specific provenance and governed-scope attribution as part of that
boundary interaction. Acquisition must not depend on inaccessible transient
internal state, accidental timing against TURNLOCK's internal execution, or
later reconstruction from mutable state, human recollection, or agent
recollection. Sufficiency is therefore not defined by elapsed time, and a
logically instantaneous opportunity may conform when capture is realizable as
part of the boundary interaction itself.

The handoff is discharged when TURNLOCK completes its side of that
semantic-boundary interaction through a structurally realizable capture
capability: an eligible conforming capture context could have been established
in time to participate and acquire the required provenance, whether or not such
a context was actually attached. Discharge does not require actual receiver
participation, successful delivery, consumer processing, persistence, or
acknowledgment. Mere internal existence without such a boundary interaction does
not discharge the obligation.

The universal floor does not require an actual capture consumer for every
invocation, successful delivery, consumer processing or acknowledgment,
retry-until-success, buffering, or TURNLOCK-operated persistence. The absence
of an attached consumer does not by itself make a conforming runtime
non-conforming when a real semantic capability exists through which an eligible
capture context could have been established in time to participate. In that
no-consumer case, TURNLOCK must still complete its side of the semantic-boundary
interaction described above; structural capability without that boundary
interaction does not itself discharge the obligation. Conversely, a runtime
that keeps required provenance only as inaccessible transient internal state
does not satisfy this obligation.

Once TURNLOCK has completed a conforming realizable semantic-boundary capture
handoff as defined above, this obligation does not by itself require the
provenance to remain capturable. Post-handoff availability, persistence, and
retention remain separately governed, and another accepted invariant, decision,
profile, or integration contract may require them.

The contract therefore distinguishes absence of TURNLOCK knowledge from a known
condition whose value is protected. Consumer-visible disclosure and underlying
provenance capture capability are not equivalent: a particular consumer MAY
receive a more restrictive view, while access to the underlying provenance available through the realizable
semantic-boundary capture handoff remains subject to separately governed policy. This rule defines no authorization model,
additional consumer context, post-boundary availability, persistence, or
retention, and does not require disclosure through ordinary UI, logs, CLI
output, telemetry, or inspection surfaces.

The relevance of a condition remains relative to an externally supplied
property:

```text
Are executions E1 and E2 comparable for property P?
```

TURNLOCK core does not define which conditions matter to `P`, decide whether two
executions are comparable, select a superior execution, or own the objective or
optimization policy. Those judgments remain with the explicitly responsible
actor under Section 0.13C.

Semantic distinction, runtime availability, exposability, capture, persistence,
and retention are separate responsibilities. This obligation requires semantic
distinction, attribution, and an execution-boundary means of exposure or
capture. It does not require a TURNLOCK-owned database, post-execution
persistence, permanent retention, canonical event log, run model, replay
facility, or reproduction guarantee.

Once an effective condition governs part of an accepted invocation, its
attribution does not become semantically nonexistent solely because the
invocation later fails, is cancelled, or is interrupted. This rule does not
define those terminal outcomes or the detailed inspectability of non-completed
executions.

## 0.13E An accepted invocation keeps its governing workflow definition

Every accepted TURNLOCK workflow invocation has a governing workflow
definition. TURNLOCK must determine that definition no later than invocation
acceptance, and it remains the source of declared workflow topology for the
lifetime of that invocation. An ordinary subsequent edit of the workflow source
artifact does not alter the governing definition of an invocation that has
already been accepted, so the active invocation does not silently begin
following a later definition merely because its source artifact changed.

Each nested workflow invocation is a distinct invocation. It establishes its
own governing workflow definition no later than its own acceptance. A caller's
governing definition does not, merely by governing the caller, transitively
bind or freeze the definitions of workflows that may later be invoked from
inside the caller.

```text
artifact W = D1

accept invocation I of W
→ governing definition(I) = D1

artifact W later changes:
D1 → D2

I continues under D1

later accept invocation J of W
→ J receives the definition the applicable resolution semantics determine
  for J at J's acceptance
```

This requirement concerns which definition governs an active invocation, not
how that definition is identified or represented. It does not make source
artifacts immutable, and it does not define how a workflow reference resolves
to a definition or whether an unqualified workflow name selects the latest
version.

Ordinary artifact editing is not an operation that mutates the governing
definition of an active invocation. Source-artifact self-authoring may occur
when the surrounding execution environment permits it; it does not rebind,
replan, or replace the orchestration of the invocation that is already accepted.
The current invocation continues under its governing definition, and a later
invocation may bind to the edited artifact under its own resolution semantics.
A recursive invocation follows the same rule: when the active definition's
already-declared semantics invoke the workflow again, the new invocation
independently resolves and binds its own governing definition.

Active replanning, active rebinding, and replacement of the governing workflow
definition of an accepted invocation are outside and contrary to the current
product contract. They are not an open future feature, not a reserved
transition, and not a forward-compatibility obligation. A later proposal to
introduce such behavior would explicitly change the governing product semantics
and would have to reconcile with `TL-INV-037` and the decisions that state this
boundary.

The requirement is distinct from replay and reproducibility: keeping one
invocation's governing definition stable does not make execution deterministic,
repeatable, comparable, or reproducible, and it does not require a transitive
snapshot of an entire execution tree. Whether the surrounding environment
permits an execution resource to edit the source artifact of a workflow that
currently governs it is an environment and capability concern; TURNLOCK core
does not define general repository, filesystem, or tool authorization for
execution resources (Section 0.8B). TURNLOCK non-conformance is not the edit
itself but a changed governing definition of an accepted active invocation or an
undeclared global transition in the current invocation.

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

a workflow-declared independent agent implicitly inherits main-agent cognitive context instead of receiving initial cognitive context through explicit workflow semantics

an internally spawned child of the main agent is automatically reclassified as a first-class TURNLOCK independent-agent region

an independent agent can unilaterally expand its authority or rewrite global workflow progression because it owns local tactics

normal completion of an independent-agent region is rejected solely because its declared contract requires no non-empty business payload

structural or authority boundedness is treated as a concrete resource limit or a universal completion guarantee

a bounded one-shot semantic task can only be expressed by creating a multi-turn agent or yielding to the main agent

parallel independent semantic work cannot be expressed as workflow-owned fan-out/fan-in

a heterogeneous fan-out cannot combine mechanical, raw-LLM, and independent-agent branches while preserving each branch's distinct semantics

one semantic raw-LLM operation is required to equal exactly one provider request, physical model call, or attempt

probabilistic semantic leaves are treated as if they necessarily transfer global orchestration authority away from the workflow

evaluation or optimization policy must be owned by TURNLOCK core for workflow refinement to be correct

conforming evaluation must rely on a TURNLOCK-defined universal objective, quality metric, or superiority relation

an evaluator or optimizer must receive privileged runtime authority to assess an execution or propose a workflow change

an effective execution condition selected, bound, explicitly supplied, or
resolved by TURNLOCK can govern an execution scope while its attribution exists
only in inaccessible transient adapter state

an accepted invocation silently changes its remaining declared topology merely
because its source workflow artifact is edited

an execution resource's environment-provided local capability is treated as
TURNLOCK orchestration authority

a local workflow-artifact edit is treated as a mutation of an accepted
invocation's governing orchestration

using TURNLOCK requires a TURNLOCK-owned general permission system or a
privileged workflow class to protect its workflows

an unavailable or unknown execution condition is presented as known-equal across
executions or as evidence that no relevant difference exists
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

> **Today, reusable workflows are commonly encoded as instructions for the main agent to orchestrate. This leaves control flow, step ordering, and mechanical progression dependent on model behavior. Moving declared orchestration into executable workflow semantics removes that implicit control dependency, but typical agent-workflow systems then replace the user's main interactive coding agent with subagents or separate agent calls. TURNLOCK aims to combine workflow-owned orchestration with reversible access to the main agent already participating in the user's session.**

The central reason for preserving the main-agent handoff is that a spawned independent agent is not automatically equivalent to the current main session. Spawning introduces a context reconstruction boundary and potentially a cognitive fork; handoff is intended to preserve one continuing agentic lineage and its ordinary interactive agency while the workflow retains global orchestration. See ADR-007 and ADR-008.

TURNLOCK therefore separates concerns that are commonly fused:

```text
orchestration authority
        ≠
semantic / agentic execution capability
```

The workflow owns orchestration authority. It may allocate work to mechanical
execution, bounded raw LLM inference, bounded independent agents, or continuation
of the main agent according to the requirements of each region. None of those
execution resources becomes the global orchestrator merely by being used.

# 2. Core mental model

Section 2 is the canonical terminology registry for this specification. It owns
lexical definitions, but it is not the sole owner of product meaning:

```text
Section 0 = normative product intent and promise
Section 2 = canonical lexical definitions
Section 3 = normative obligations and stable invariant identities
Section 5 = architectural implications derived from the intent and invariants
Section 8 = non-authoritative derived synopsis
accepted ADRs = immutable decision history
```

Every normative concept that receives a lexical definition is registered here,
and one normative concept has exactly one canonical lexical definition,
identified below by a unique local concept key and stable `term-*` anchor. Other
sections may use a registered concept, state product intent, impose obligations, or
explain consequences, but they do not assign it an independent lexical meaning.
References to a concept therefore use its Section 2 meaning unless an explicit
later authority change updates this registry.

A canonical term is the preferred wording for its registered concept. An
accepted alias points to that same concept and definition. Deprecated wording
is retained only to identify wording that must not be treated as canonical.
Compound terms remain distinct registered concepts when the compound carries a
more specific identity than its component terms. A word used in several
compounds is not forced into one shared meaning: each distinct normative concept
receives its own key and destination. In particular, repeated use of a modifier
such as `bounded` does not make all containing compounds equivalent; the
relevant compound entries are the canonical destinations for any later
clarification of that modifier.

The registry identifies definitions; it does not summarize or replace their
prose:

<!-- normative-terminology-registry:start -->
| Concept key | Canonical term | Canonical anchor | Accepted aliases | Deprecated wording | Term structure |
| ----------- | -------------- | ---------------- | ---------------- | ------------------ | -------------- |
| `main-agent` | `main agent` | [`term-main-agent`](#term-main-agent) | `main coding agent`; `existing main agent` | — | base |
| `workflow` | `workflow` | [`term-workflow`](#term-workflow) | — | — | base |
| `execution-region` | `execution region` | [`term-execution-region`](#term-execution-region) | `workflow execution region` | — | compound |
| `workflow-invocation-surface` | `workflow invocation surface` | [`term-workflow-invocation-surface`](#term-workflow-invocation-surface) | `slash-command invocation surface` | — | compound |
| `workflow-artifact` | `workflow artifact` | [`term-workflow-artifact`](#term-workflow-artifact) | `workflow code` | — | compound |
| `turnlock-primitives` | `TURNLOCK primitives` | [`term-turnlock-primitives`](#term-turnlock-primitives) | `workflow primitives` | — | compound |
| `mechanical-execution` | `mechanical execution` | [`term-mechanical-execution`](#term-mechanical-execution) | `mechanical work` | `deterministic execution` | compound |
| `mechanical-step` | `mechanical step` | [`term-mechanical-step`](#term-mechanical-step) | `mechanical phase`; `mechanical region` | — | compound |
| `raw-llm-inference` | `raw LLM inference` | [`term-raw-llm-inference`](#term-raw-llm-inference) | `raw LLM call` | — | compound; overloaded modifier: `bounded` |
| `raw-llm-inference-step` | `raw LLM inference step` | [`term-raw-llm-inference-step`](#term-raw-llm-inference-step) | — | — | compound of `raw-llm-inference` |
| `independent-agent` | `independent agent` | [`term-independent-agent`](#term-independent-agent) | — | — | compound; overloaded modifier: `bounded` |
| `independent-agent-step` | `independent-agent step` | [`term-independent-agent-step`](#term-independent-agent-step) | `independent-agent phase`; `independent-agent region` | — | compound of `independent-agent` |
| `main-agent-handoff` | `main-agent handoff` | [`term-main-agent-handoff`](#term-main-agent-handoff) | `control handoff`; `handoff to the main agent` | — | compound |
| `main-agent-step` | `main-agent step` | [`term-main-agent-step`](#term-main-agent-step) | `main-agent phase`; `main-agent region`; `main-agent continuation` | — | compound |
| `immediate-caller-context` | `immediate caller context` | [`term-immediate-caller-context`](#term-immediate-caller-context) | `immediate caller`; `invocation context`; `caller context` | — | compound |
| `caller-stack` | `caller stack` | [`term-caller-stack`](#term-caller-stack) | `structured caller stack` | — | compound |
| `control-ownership` | `control ownership` | [`term-control-ownership`](#term-control-ownership) | `local control`; `phase-local control` | — | compound |
| `workflow-owned-control` | `workflow-owned control` | [`term-workflow-owned-control`](#term-workflow-owned-control) | `the workflow owns orchestration`; `workflow owns global progression` | `deterministic orchestration` | compound |
| `parallel-fan-out-fan-in` | `parallel fan-out/fan-in` | [`term-parallel-fan-out-fan-in`](#term-parallel-fan-out-fan-in) | `fan-out/fan-in`; `parallel region` | — | compound |
| `nested-workflow-invocation` | `nested workflow invocation` | [`term-nested-workflow-invocation`](#term-nested-workflow-invocation) | `nested invocation` | — | compound |
| `execution-inspectability` | `execution inspectability` | [`term-execution-inspectability`](#term-execution-inspectability) | `completed-execution inspectability` | — | compound |
| `effective-execution-condition-provenance` | `effective execution-condition provenance` | [`term-effective-execution-condition-provenance`](#term-effective-execution-condition-provenance) | — | — | compound |
| `realizable-semantic-boundary-capture-handoff` | `realizable semantic-boundary capture handoff` | [`term-realizable-semantic-boundary-capture-handoff`](#term-realizable-semantic-boundary-capture-handoff) | — | — | compound |
| `governing-workflow-definition` | `governing workflow definition` | [`term-governing-workflow-definition`](#term-governing-workflow-definition) | — | — | compound |
<!-- normative-terminology-registry:end -->

Definition-like occurrences outside their canonical destinations are reviewed in
`terminology-inventory.yaml`. That inventory records locations,
responsibility-based roles, and text fingerprints only. It is a review aid, not
a glossary or semantic authority. The associated checker detects likely
competing definitions conservatively; passing it establishes structural and
inventory consistency, not semantic equivalence.

The system must not treat these concepts as equivalent:

```text
main agent == workflow
workflow entry == workflow
main-agent step == independent-agent step
main-agent step == raw LLM inference
independent-agent step == raw LLM inference
main-agent step == context-reconstructed child-agent call
mechanical step == tool call chosen by the main agent
mechanical execution == computational determinism
workflow-owned control == one possible output, path, or trace
workflow state == chat context
workflow completion == agent-session completion
local agent discretion == global orchestration authority
probabilistic result == a new orchestration possibility
execution inspectability == evaluation or optimization
execution inspectability == replay, reproducibility, or execution proof
effective execution-condition provenance == persistence or retention
effective execution-condition provenance == comparability or reproducibility
unknown execution condition == known-equal execution condition
```

They are distinct product concepts.

## 2.1 Main agent

<a id="term-main-agent"></a>

The **main agent** is the coding agent participating in the user's surrounding interactive session.

It is the agent that has the user-facing conversational continuity before workflow entry and to which the workflow returns when execution finishes.

A main-agent step temporarily makes that agent active inside workflow execution.

The main agent does not thereby become the owner of the workflow's global control flow.

## 2.2 Workflow

<a id="term-workflow"></a>

A **workflow** is an executable user-defined process that owns progression across its steps after entry and until termination.

A workflow may contain mechanical phases, bounded raw-LLM inference phases, independent-agent phases, main-agent continuation phases, control-flow/composition operations, and nested workflow invocations.

It is not merely a prompt describing desired sequencing.

The workflow must retain enough execution truth to resume after temporary main-agent control.

## 2.2A Execution region

<a id="term-execution-region"></a>

An **execution region** is a workflow-declared semantic scope in which one
execution form performs declared work with local execution authority, without
thereby acquiring authority over the enclosing workflow's global orchestration.
The declaration identifies the region's place and continuation in workflow
semantics; a runtime occurrence is one execution of that declared region.

This distinction requires no `Region` data type, stable activation identifier,
process, thread, coroutine, or other runtime representation. It provides only
the structural boundary needed to distinguish entry, local activity, and an
applicable completion transition without implying that completion must occur.

## 2.3 Workflow invocation surface

<a id="term-workflow-invocation-surface"></a>

A **workflow invocation surface** is the session-local user interaction through which a TURNLOCK workflow is selected and started.

For supported coding-agent harnesses, the ordinary invocation surface is a **natural slash command comparable to invoking a native skill**. The concrete command name, namespace, registration mechanism, and mapping between commands and workflows are intentionally not fixed yet.

The invocation surface should be small in semantic responsibility: it selects/starts workflow-owned execution rather than embedding the workflow's orchestration into the main-agent prompt.

## 2.3A Workflow artifact and TURNLOCK primitives

<a id="term-workflow-artifact"></a>

A **workflow artifact** is the developer-readable executable representation of a TURNLOCK workflow. A developer may author it directly or a coding agent may author it on the developer's behalf. Those are two authorship paths to the same semantic object, not two workflow classes.

<a id="term-turnlock-primitives"></a>

**TURNLOCK primitives** are the author-facing operations that express TURNLOCK's control semantics. Their exact syntax and full set are not fixed yet, but they must represent product concepts at TURNLOCK level rather than require workflow authors to reproduce harness-specific control plumbing.

Pi-specific APIs may implement these primitives in the first integration; they are not themselves automatically TURNLOCK primitives.

## 2.4 Mechanical execution and mechanical step

<a id="term-mechanical-execution"></a>

**Mechanical execution** is non-agent-mediated progression governed by
executable workflow semantics together with runtime inputs, results, state, or
events. The term identifies execution and control authority, not computational
or output determinism. Mechanical execution may be deterministic,
nondeterministic, probabilistic, dependent on external state, or event-driven.

<a id="term-mechanical-step"></a>

A **mechanical step** is a workflow phase that uses mechanical execution. Its
progression does not require discretionary agent judgment to supply a missing
orchestration decision. It may consume an LLM or agent result without inheriting
the producer's local authority; a declared rule that branches on that result
remains mechanical.

This specification intentionally does not yet fix which mechanical primitives
exist or how they are expressed.

A mechanical step may produce state or evidence consumed by later steps,
including a main-agent step.

## 2.4A Raw LLM inference and raw LLM inference step

<a id="term-raw-llm-inference"></a>

**Raw LLM inference** is a bounded, non-agentic semantic operation in which an
explicit instruction and explicit context are supplied to a model and produce a
result. `Bounded` identifies one declared TURNLOCK operation with an input and
result boundary. It does not establish an autonomous observe/reason/act loop, a
persistent independent cognitive lineage, or global workflow-orchestration
authority.

The operation is one-shot at the TURNLOCK semantic level only. It does not
require exactly one provider request, one physical model call, one attempt, no
internal retry, or no streaming. Nor does its boundary select a token, cost,
time, request, or other resource limit or guarantee that an occurrence
completes. If and when a result is produced, workflow semantics may consume it
only through declared progression.

<a id="term-raw-llm-inference-step"></a>

A **raw LLM inference step** is the workflow phase that supplies the explicit
instruction and context to, and receives the constitutive result of, raw LLM
inference.

Its semantic shape is:

```text
explicit instruction + explicit context → model inference → result
```

It may be executed singly or as part of declared parallel fan-out.

## 2.4B Independent agent and independent-agent step

<a id="term-independent-agent"></a>

An **independent agent** is an agentic execution resource that operates within a
fresh cognitive lineage distinct from the main agent for a workflow-declared
local task. Its initial cognitive context consists only of information supplied
explicitly through workflow semantics; it receives no implicit inheritance of
the main agent's cognitive history. It may then acquire information through the
capabilities available during its autonomous multi-turn reasoning, tool use,
observation, and adaptation.

For independent-agent execution, `bounded` means that the workflow declares the
local task, initial cognitive-context provenance, place in the workflow, and
continuation, while the agent exercises only local available authority. It does
not mean that all physical effects remain inside the region, impose a maximum
number of turns, tokens, tool calls, cost, or time, require a timeout or
cancellation rule, or guarantee completion.

The workflow owns the declared task boundary. The agent owns its local plan,
tactics, exploration, ordering of local actions, and hypothesis changes while
exercising available authority. It cannot create additional authority merely by
wanting it and cannot acquire global workflow-orchestration authority through
local autonomy. These rules do not prescribe a capability manifest, tool list,
permission system, context format, or resource budget.

<a id="term-independent-agent-step"></a>

An **independent-agent step** is the execution region in which workflow semantics
declare the local task, initial cognitive context, and continuation for an
independent agent. Its semantic shape is:

```text
workflow-declared local task
+ fresh distinct cognitive lineage
+ explicitly supplied initial cognitive context
→ autonomous multi-turn local work
→ normal completion if reached
→ optional declared output
→ workflow-owned continuation
```

Effects, output, and completion are distinct. Effects are changes caused during
execution and may persist beyond the region. Output is a business value exposed
to workflow semantics when the declared contract requires one; a non-empty
business payload is otherwise not mandatory. Completion is the fact that a
runtime occurrence reached its normal boundary. If normal completion occurs,
TURNLOCK can recognize it, workflow-owned progression follows the declared
continuation, and any contract-required output becomes available. This
conditional rule does not guarantee that every started occurrence completes.

Fresh lineage does not mean absence of runtime or system instructions, tool
descriptions, harness environment, or technical execution state. Explicitly
supplying main-agent-derived summaries, artifacts, files, or prior results also
does not constitute implicit lineage inheritance.

An agent spawned internally by the main agent during a main-agent region remains
local delegation under ordinary main-agent agency unless workflow semantics
explicitly declare it as a first-class TURNLOCK independent-agent region. The
fresh-lineage context-provenance rule does not automatically apply to such an
internal child. Multiple workflow-declared independent-agent steps may execute
concurrently, whether they perform the same task or different tasks.

## 2.5 Main-agent handoff and main-agent step

<a id="term-main-agent-handoff"></a>

A **main-agent handoff** is the temporary transfer of local execution authority
from an active workflow to the main agent defined in Section 2.1, followed by a
return of execution authority to the workflow at the declared continuation. It
uses the existing main-agent cognitive lineage and ordinary interactive agency;
a raw LLM call or fresh independent agent is not an equivalent handoff.

<a id="term-main-agent-step"></a>

A **main-agent step** is the workflow phase bounded by that handoff and return.
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

<a id="term-immediate-caller-context"></a>

An **immediate caller context** is the execution context that invoked a workflow and to which normal completion of that workflow returns.

For a top-level workflow, the caller is the surrounding main-agent interaction. For a nested workflow, the caller is the calling execution context inside the enclosing workflow. For an agent-selected invocation, that context is the main-agent region. For a workflow-declared invocation, that context is the workflow execution context that performs the declared call.

A caller context preserves a call continuation while the callee executes. The continuation is not itself the caller context; it is the preserved return state of that context.

<a id="term-caller-stack"></a>

A **caller stack** is the conceptual structured nesting of suspended immediate
caller contexts and active workflow invocations. Nested invocations therefore
form a caller stack conceptually:

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

## 2.7 Control ownership and workflow-owned control

<a id="term-control-ownership"></a>

**Control ownership** is the authority to direct execution within the currently
active phase or context. It is phase-local and does not by itself grant authority
over the enclosing workflow's global progression.

<a id="term-workflow-owned-control"></a>

**Workflow-owned control** is the arrangement in which the workflow program is
the source of truth for declared global orchestration decisions, topology, and
permitted continuations, while TURNLOCK is the engine that executes and tracks
that progression. Runtime inputs, results, state, or events may select among
those declared possibilities; they do not create undeclared continuations.

```text
outside workflow:
  main agent owns ordinary interaction

inside mechanical phase:
  workflow semantics govern permitted progression
  TURNLOCK performs mechanical execution

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

## 2.8 Parallel and nested composition

<a id="term-parallel-fan-out-fan-in"></a>

**Parallel fan-out/fan-in** is workflow-declared composition in which independent
branches may execute concurrently and are synchronized or collected before the
workflow takes its declared continuation. Each branch retains the semantics of
its execution form, and the workflow owns the branch topology and join.

<a id="term-nested-workflow-invocation"></a>

A **nested workflow invocation** is a workflow invocation made from an immediate
caller context inside an enclosing workflow while the continuation of that
calling context is suspended. The invocation MAY be declared by the enclosing
workflow program, or selected by the main agent while it legitimately owns a
main-agent region (ADR-008). The nested workflow owns its own declared
progression, and normal completion returns to that same immediate caller
context.

## 2.9 Execution inspectability

<a id="term-execution-inspectability"></a>

**Execution inspectability** is the property of a completed workflow execution
that makes enough of its actual TURNLOCK-visible behavior available for a user
or higher-level system to understand and evaluate how the workflow progressed in
practice without reconstructing the execution from human or agent recollection.

Its semantic boundary comprises workflow-mediated structure, execution
boundaries, explicitly exposed inputs and results, and TURNLOCK-visible facts
relevant to declared progression. It excludes private or internal reasoning of
raw LLM inference, independent agents, and the main agent unless information
from such a region becomes an explicitly exposed result or another
TURNLOCK-visible progression fact.

Execution inspectability enables evaluation and refinement; it does not mean
that TURNLOCK defines evaluation criteria, compares executions, or optimizes the
workflow. The term does not prescribe a run model, event schema, identifier,
storage, telemetry, retention, replay, reproducibility, proof, or user-interface
mechanism.

## 2.10 Effective execution-condition provenance

<a id="term-effective-execution-condition-provenance"></a>

**Effective execution-condition provenance** is the semantic relationship that
attributes a condition TURNLOCK selects, binds, explicitly supplies, or resolves
at its semantic boundary to the execution scope that condition governs. The
relationship remains exposable or capturable at an execution boundary rather
than existing only in hidden transient adapter state or requiring reconstruction
from later mutable state, human recollection, or agent recollection.

The concept requires semantic distinction, attribution, and a realizable
semantic-boundary capture handoff. For a specific condition TURNLOCK knows, a
semantic representation containing information specific to that known condition
must remain bound to its occurrence and governed scope and capturable through
that handoff even when the underlying value is protected from disclosure.
Protection may restrict a consumer-visible view, but it cannot substitute an
occurrence label or generic protected marker for the more specific condition
information before or during that handoff. A known protected condition is
therefore distinct from an unknown condition.

This occurrence-specific binding does not itself establish underlying-value
equality or difference across occurrences. A condition-specific representation
does not establish a public or cross-run stable identity, equality or difference
evidence, or comparability for any property. The concept does not require exact-value disclosure, persistence,
retention, a canonical event or run model, replay, reproducibility, or a
comparison contract. A condition outside TURNLOCK's observation or control may
remain unavailable or unknown; unknown is not evidence of equality or absence
of difference.

<a id="term-realizable-semantic-boundary-capture-handoff"></a>

A **realizable semantic-boundary capture handoff** is the semantic-boundary
interaction through which an eligible conforming capture context can acquire
required provenance as part of that interaction before TURNLOCK irreversibly
loses it. Such a handoff is realizable only when that context could be
established in time to participate without depending on inaccessible transient
internal state, accidental timing against TURNLOCK's internal execution, or
reconstruction from later mutable state, human recollection, or agent
recollection. The handoff is discharged when TURNLOCK completes its side of
that semantic-boundary interaction through a structurally realizable capture
capability: an eligible conforming capture context could have been established
in time to participate and acquire the required provenance, whether or not such
a context was actually attached. Discharge does not require actual receiver
participation, successful delivery, consumer processing, persistence, or
acknowledgment. Mere internal existence without such a boundary interaction
does not discharge the obligation. Sufficiency is not a wall-clock or retention
duration: capture may be logically instantaneous when acquisition is realizable
as part of the boundary interaction itself.

## 2.11 Governing workflow definition

<a id="term-governing-workflow-definition"></a>

A **governing workflow definition** is the workflow definition that TURNLOCK
has determined as the source of declared topology for one accepted workflow
invocation. That relationship is stable for that invocation: ordinary later
modification of the workflow source artifact does not change which definition
governs the invocation's remaining declared topology.

The concept identifies no concrete version, revision, hash, snapshot, copy, or
storage representation. Each accepted invocation, including each nested
invocation, has its own governing workflow definition; a caller's governing
definition does not by itself determine or freeze the governing definition of a
workflow that may later be invoked.

# 3. Derived invariants

The following invariants are derived from the product intent already established. They constrain future architecture without fixing its mechanism.

## 3.1 TL-INV-001 — Workflow-orchestration invariant

For an active workflow:

```text
declared global orchestration logic = workflow program
execution of that logic = TURNLOCK engine
```

The main agent MUST NOT be required to act as the global step scheduler for the
workflow, and TURNLOCK MUST NOT silently invent undeclared global strategy
merely because it executes the workflow. Workflow-owned control MAY admit
multiple runtime results and continuations; every resulting change in global
control MUST be authorized by executable workflow semantics.

## 3.1A TL-INV-002 — Engine / decision-owner separation invariant

TURNLOCK MUST provide the runtime authority needed to execute, schedule, coordinate, and resume declared workflow control, but the workflow artifact remains the source of truth for the orchestration decisions that have been authored.

```text
TURNLOCK executes orchestration != TURNLOCK invents orchestration
```

A runtime optimization or harness adapter MAY choose equivalent execution
mechanisms, but it MUST NOT change the declared topology or substitute new
global decisions without an explicit workflow semantic that grants such
authority. Evaluating a declared rule against a runtime result and selecting one
of its permitted continuations is execution of workflow semantics, not invention
of topology.

## 3.2 TL-INV-003 — Mechanical-execution invariant

For a mechanical step:

```text
step execution truth != agent interpretation
mechanical execution != computational determinism
```

The step either progresses according to its executable semantics and available
runtime inputs, results, state, or events, or produces a defined non-success
outcome. Its execution MUST NOT depend on an agent deciding whether to follow a
prose instruction or supplying an orchestration decision absent from those
semantics.

A mechanical step MAY wait for an external event or branch on a probabilistic,
nondeterministic, external, LLM-produced, or agent-produced result when the
workflow already declares how that result relates to permitted continuations.

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

An implementation MUST NOT claim workflow-owned orchestration while covertly
translating the workflow into instructions that the main agent must interpret
step-by-step or by leaving an underspecified control point where an agent is
expected to infer what the global workflow should do next.

This prohibition does not remove local semantic or discretionary authority from
an explicitly declared main-agent or independent-agent region. Local judgment
within that region MUST NOT, by itself, authorize the agent to add, skip,
replace, or reconstruct global continuations that executable workflow semantics
do not permit.

The location of the source code is irrelevant; what matters is where control-flow
authority actually resides.

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

TURNLOCK MUST allow a workflow-owned parallel region to mix independent branch types, including mechanical execution, bounded raw LLM inference, and bounded independent-agent execution. Branches of the same semantic type MAY perform the same task or different tasks. Mixed fan-out MUST preserve the lifecycle, context, authority, completion, effects, and declared output semantics of each branch type while keeping fan-out, synchronization, collection, and continuation under workflow ownership.

This invariant does not require main-agent continuation to be an ordinary parallel branch; that question remains separately open.

## 3.23 TL-INV-025 — Independent-agent first-class invariant

TURNLOCK MUST allow a workflow to declare bounded independent-agent execution directly. The workflow MUST NOT be required to yield to the main agent merely so that the main agent can decide to create an agent that the workflow topology already requires.

Each workflow-declared independent-agent region has a declared local task,
creates a fresh cognitive lineage distinct from the main agent, and permits
autonomous multi-turn local work within available authority. If a runtime
occurrence reaches normal completion, TURNLOCK MUST recognize that completion
and follow the workflow-declared continuation. A business output is optional
unless the region contract requires one; any required output MUST become
available on normal completion. Effects MAY persist independently of whether a
business output is required.

This invariant neither grants the agent global orchestration authority nor
requires a concrete resource bound or universal completion.

## 3.24 TL-INV-026 — Independent-agent context-provenance invariant

A workflow-declared independent agent MUST receive no implicit inheritance of
the main agent's cognitive context. Its initial cognitive context MUST consist
only of information supplied explicitly through workflow semantics. It MAY then
acquire additional information during its own execution through available
capabilities.

Explicit workflow input MAY contain main-agent-derived summaries, artifacts,
files, or prior results without becoming implicit lineage inheritance. Fresh
cognitive lineage does not require an empty runtime environment or exclude
system instructions, tool descriptions, or technical execution state. The exact
context-construction API, representation, serialization, and size or resource
limits remain open.

This rule applies to first-class workflow-declared independent-agent regions. It
does not automatically govern a child agent spawned internally through ordinary
main-agent agency.

## 3.25 TL-INV-027 — Parallel semantic fan-out/fan-in invariant

TURNLOCK MUST be able to express workflow-owned parallel execution of independent semantic work and subsequent synchronization/collection. Parallel branches MAY perform the same task or different tasks.

The declared topology:

```text
fan-out → concurrent semantic work → fan-in/join → continuation
```

MUST NOT require the main agent to become the scheduler merely because the concurrent branches are agentic or LLM-based.

## 3.26 TL-INV-028 — Raw-LLM inference invariant

TURNLOCK MUST expose raw LLM inference as one declared bounded non-agentic
semantic operation with explicit instruction and context, no autonomous
observe/reason/act loop, no persistent independent cognitive lineage, a result
boundary, and no global workflow-orchestration authority.

A workflow that needs a one-shot semantic transformation MUST NOT be forced to
create a multi-turn agentic loop or hand control to the main agent solely to
obtain model intelligence. `One-shot` and `bounded` describe the TURNLOCK
semantic operation; they MUST NOT be interpreted as requiring one physical
provider call, forbidding internal retries or streaming, selecting a concrete
resource limit, or guaranteeing completion.

## 3.27 TL-INV-029 — Minimum-sufficient cognition invariant

The workflow model MUST preserve the author's ability to choose the least powerful execution form sufficient for a region:

```text
mechanical execution
→ raw LLM inference
→ independent agent
→ main-agent continuation
```

TURNLOCK MUST NOT collapse these choices into one universal "agent step" when their cost, context, autonomy, continuity, and lifecycle semantics differ.

## 3.28 TL-INV-030 — Workflow-owned-control / probabilistic-result invariant

Workflow-owned control MUST be compatible with probabilistic,
nondeterministic, externally dependent, and event-driven results. Such a result
MAY select among continuations already permitted by executable workflow
semantics; it does not authorize an LLM, agent, mechanical operation, or other
execution resource to create or alter the permitted global continuations.

An explicitly declared agentic region MAY exercise its local semantic or
discretionary authority. The workflow remains responsible for declared
sequencing, branching, fan-out, synchronization, and continuation, and every
change in global control MUST be authorized by workflow semantics.

## 3.29 TL-INV-031 — Workflow expressive-power invariant

TURNLOCK's workflow-declared orchestration surface MUST be expressive enough
that known control decisions can remain executable workflow logic rather than
being delegated back to an agent for lack of orchestration primitives.

At the semantic level this includes the ability to compose, as required by a workflow:

```text
mechanical execution
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

## 3.31 TL-INV-033 — Completed-execution inspectability invariant

Every completed TURNLOCK workflow execution MUST expose enough of its actual
TURNLOCK-visible behavior for a user or higher-level system to understand and
evaluate how the workflow progressed in practice without reconstructing the
execution from human or agent recollection.

The obligation covers enough workflow-mediated structure, execution boundaries,
explicitly exposed inputs and results, and TURNLOCK-visible facts relevant to
declared progression to satisfy execution inspectability. It does not require a
universal event catalog, visibility into private agent reasoning, recording of
every agent tool call, or any particular tracing, storage, retention, telemetry,
or user-interface mechanism.

An inspection surface MUST NOT present a later or current workflow definition as
proof of what a previous execution actually did. This prohibition preserves the
distinction between actual execution behavior and a definition shown during
inspection; it does not decide how workflow definitions bind to active
invocations or how correspondence is represented.

This invariant enables user- or system-led evaluation and iterative refinement.
It does not make TURNLOCK the evaluator or optimizer and does not imply replay,
computational or output determinism, identical traces, cross-run comparability,
reproducibility, permanent retention, or execution proofs.

## 3.32 TL-INV-034 — Evaluation/optimization-policy boundary invariant

TURNLOCK core MUST NOT define a universal evaluation objective, universal
quality metrics, a default superiority relation between workflows or
executions, experiment policy, or an autonomous workflow optimizer. Evaluation
objectives MUST be supplied by an explicitly responsible actor or artifact
outside core TURNLOCK policy.

Evaluation or optimization behavior expressed as an ordinary TURNLOCK workflow
remains ordinary authored execution under existing workflow semantics. It
receives no privileged runtime authority, and any resulting improvement to a
workflow artifact is authorship subject to `TL-INV-032`, not implicit runtime
replanning.

This invariant preserves `TL-INV-001` and `TL-INV-002`: TURNLOCK executes
declared orchestration and does not invent it. It does not prohibit
TURNLOCK-adjacent evaluation or optimization tooling; it establishes that such
capability is outside the current core product contract until a future accepted
decision changes that boundary. It does not require, forbid, or prescribe any
storage, telemetry, metric, comparison, experiment, or optimizer mechanism.

## 3.33 TL-INV-035 — Declared-invocation invariant

A TURNLOCK workflow program MAY declaratively invoke another TURNLOCK workflow
as part of its authored orchestration. The decision to invoke that workflow
belongs to the invoking workflow program, and TURNLOCK MUST execute an admitted
declared invocation directly rather than requiring a main-agent handoff solely
to reproduce an invocation decision already present in the executable topology.

For an admitted declared invocation:

```text
caller context → declared invocation of callee → same caller context
```

The caller context preserves its call continuation, and the calling continuation
is suspended with respect to that invocation; the continuation is not itself the
caller context. The callee executes its own declared progression, and normal
completion returns to the same immediate caller context and makes the preserved
workflow-declared post-call continuation eligible for that caller. That return
authorizes no other continuation of that caller context, and it does not
disable, suspend, or require stopping independently active concurrent contexts
that the declared topology permits to continue. The callee MUST NOT replace,
rewrite, skip, or capture the caller's continuation or the enclosing workflow's
declared progression.

Suspension is local to the calling continuation. A declared invocation MUST NOT
be interpreted as implicitly suspending concurrently active contexts that the
declared topology permits to continue.

This invariant does not decide recursion, cyclic call graphs, restricted
placement admissibility, or concrete depth and resource limits.

## 3.34 TL-INV-036 — Effective execution-condition provenance invariant

For every accepted workflow invocation, each effective execution condition that
TURNLOCK selects, binds, explicitly supplies, or resolves at its semantic
boundary MUST remain semantically distinguished and attributable to the
execution scope it governs. TURNLOCK MUST preserve the required
condition-specific provenance and governed-scope attribution until that
provenance participates in a realizable semantic-boundary capture handoff.

A handoff is realizable only when an eligible conforming capture context could
be established in time to acquire the required provenance as part of the
semantic-boundary interaction, without depending on inaccessible transient
internal state, accidental timing against TURNLOCK's internal execution, or
reconstruction from later mutable state, human recollection, or agent
recollection. A capture opportunity defined by elapsed time is not required:
no minimum wall-clock duration, workflow transition count, scheduler turn
count, process lifetime, scope lifetime, or invocation lifetime is part of this
invariant, and an opportunity MAY be logically instantaneous when acquisition
is realizable as part of the boundary interaction itself. TURNLOCK MUST NOT
satisfy this invariant merely because the required provenance existed
internally for some nonzero duration.

The universal floor does not require an actual capture consumer for every
invocation, successful delivery, consumer processing or acknowledgment,
retry-until-success, buffering, or durable TURNLOCK-operated storage. A runtime
that exposes a real semantic capability through which an eligible capture
context could have been established and could have participated in the required
handoff does not become non-conforming solely because no consumer was attached
for a particular invocation. In that case, the handoff is discharged when
TURNLOCK completes its side of the semantic-boundary interaction through that
structurally realizable capability; actual receiver participation is not
required. Mere internal existence without that boundary interaction does not
discharge the obligation. Consumer absence does not by itself create an
indefinite retention obligation. A runtime that keeps required provenance only
as inaccessible transient internal state remains non-conforming.

Once TURNLOCK has completed a conforming realizable semantic-boundary capture
handoff as defined above, this invariant alone does not require the provenance
to remain capturable. Post-handoff availability, persistence, and retention are
independently governed and may be required by another accepted invariant,
decision, profile, or integration contract; this invariant does not by itself
require provenance to survive until a governed scope, invocation, or workflow
ends or until a consumer inspects or acknowledges it.

A conforming realization MAY batch, aggregate, or group multiple
effective-condition occurrences into one semantic-boundary interaction provided
that doing so preserves each occurrence's condition-specific provenance and
governed-scope attribution at the semantic level this invariant requires. One
semantic occurrence is not required to correspond to one physical event,
message, or callback.

A condition outside TURNLOCK's observation or control MAY remain unavailable or
unknown. Unknown MUST NOT be represented as known-equal across executions or as
evidence that no relevant difference exists.

When TURNLOCK knows a specific effective condition, exact-value disclosure is
not required. If the value is protected or unsafe to disclose, a
semantic representation containing information specific to that known condition
MUST remain bound to its effective-condition occurrence and the scope it governed
and capturable through TURNLOCK's required realizable semantic-boundary capture
handoff. Protection or redaction MUST NOT substitute away that
condition-specific information before or during the handoff. An occurrence label alone does not
satisfy this requirement. A generic known-but-protected or redacted marker MAY
be presented to a particular consumer, but it is insufficient as the sole
provenance representation when it would replace more specific TURNLOCK-known
condition information. Known protected provenance MUST
NOT be represented as unknown merely because its value is not disclosed.

Consumer-visible disclosure is not the same responsibility as underlying
provenance capture capability. A consumer MAY receive less information than the
underlying provenance made capturable through the realizable semantic-boundary
capture handoff, under separately governed policy. This permission
neither defines who is authorized or requires an additional consumer context,
nor requires that the underlying value or the complete capturable representation
appear in UI, logs, CLI output, telemetry, or ordinary inspection surfaces. It
also requires no post-handoff availability, persistence, or retention.

If a condition governs part of an accepted invocation, later failure,
cancellation, or interruption MUST NOT make that attribution semantically
nonexistent and MUST NOT retroactively erase the obligation that its provenance
reach the required realizable handoff. This requirement defines no
terminal-outcome or detailed non-completed-execution inspectability semantics;
Issue #13 retains that scope.

This invariant does not require persistence, retention, a database, event
schema, identifier, hash, snapshot, telemetry system, canonical run model,
replay, cross-run comparability, reproducibility, deterministic execution,
identical outputs, or identical traces. Occurrence-specific provenance does not
state whether underlying values across occurrences are equal or different. Its
representation is not required to be globally or cross-run stable and
establishes no underlying-value equality or difference operation or proof. TURNLOCK does not determine which conditions are
relevant to an externally supplied property `P` or whether two executions are
comparable for that property.

## 3.35 TL-INV-037 — Active-invocation governing-definition stability invariant

For every accepted workflow invocation, TURNLOCK MUST have determined one
governing workflow definition no later than invocation acceptance. That
definition MUST remain the source of declared topology for the lifetime of that
invocation and MUST NOT be replaced, rebound, rewritten, replanned, or altered
merely because the workflow source artifact is subsequently edited.

Every accepted nested invocation establishes its own governing workflow
definition. The governing definition of its caller MUST NOT, by itself,
transitively determine or freeze the callee's governing definition before the
callee invocation is accepted.

Ordinary artifact editing and source-artifact self-authoring do not constitute
an operation that mutates the governing definition of an active invocation.
Such local authoring may occur when the surrounding execution environment
permits it and remains a local execution effect; it does not change the
orchestration envelope authorized by the governing definition. A later
invocation independently resolves and may bind to the edited artifact. Active
replanning, active rebinding, and replacement of an accepted invocation's
governing definition are outside and contrary to the current TURNLOCK product
contract, not a reserved future capability. The current formal model MUST NOT
contain an active-definition-mutation transition, an authorization guard for
one, or a placeholder for one.

This invariant does not decide how a governing definition is identified or
represented, whether source artifacts or their repositories are immutable,
whether the surrounding execution environment supplies or restricts local
access to a workflow that currently governs an invocation, or whether replay,
reproducibility, or transitive snapshot guarantees should ever exist. TURNLOCK
core does not define general repository, filesystem, or tool authorization for
execution resources; Section 0.8B states that responsibility boundary.

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
- How the surrounding execution environment supplies or restricts local
  filesystem, tool, OS, repository, and sandbox capabilities during agentic
  regions; TURNLOCK core defines no general repository, filesystem, or tool
  authorization for execution resources (Section 0.8B).
- What exact continuity guarantee is achievable or required per supported harness.
- Whether a temporarily unavailable main-agent handoff can be retried, degraded, or must fail closed.
- Which concrete inspection facts and sufficiency rules different workflow shapes require beyond the accepted minimum execution-inspectability obligation.
- What detailed tracing, event schemas, ordering guarantees, storage, retention, telemetry, debugger UI, or evaluation tooling should exist above the execution substrate; native evaluation or optimization policy remains outside TURNLOCK core under `TL-INV-034`.
- Whether completed-execution inspectability extends to failed, cancelled, interrupted, or otherwise non-completed executions, and with what outcome-specific semantics.
- How inspection represents or establishes correspondence between actual execution and the governing workflow definition remains separately open to the extent not already fixed by `TL-INV-033`, `TL-INV-036`, and `TL-INV-037`.
- Whether future TURNLOCK-adjacent capabilities should introduce native evaluator interfaces, universal metrics, cross-run comparison, experiment support, or optimizer machinery; the current product definition assigns evaluation and optimization policy outside TURNLOCK core, and any such addition requires a new accepted product decision.
- Whether replay, cross-run comparability contracts or APIs, reproducibility profiles, canonical run models, experiment frameworks, or execution proofs should ever be supported.
- Whether conditions TURNLOCK observes but does not control, or conditions an adapter or execution resource could expose, receive provenance obligations beyond the universal floor for conditions TURNLOCK selects, binds, explicitly supplies, or resolves.
- What persistence, retention, concrete authorization, access, and privacy guarantees apply above the required execution-boundary means of capture, including which consumers may receive richer or more restrictive views.
- Whether visibility inside an agentic region should extend beyond explicitly exposed results and TURNLOCK-visible facts relevant to declared progression.
- Whether multiple sibling/top-level workflows may execute concurrently in one interactive coding-agent session; structured nested invocation is already allowed.
- Whether implementations impose explicit resource/safety limits on nesting depth, and how such limits are surfaced without changing immediate-caller return semantics.
- The admissibility of workflow invocation in restricted contexts such as parallel branches, and the treatment of recursive or cyclic workflow call graphs.
- What security/trust model applies to user-authored workflow code.
- How a workflow selects models/providers and expresses inference budgets, model parameters, structured outputs, or provider fallbacks for raw LLM calls.
- How one semantic raw-LLM operation maps to provider requests, retries, streaming, or other physical inference mechanics.
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

For a top-level invocation, that caller is the surrounding main-agent interaction. For a nested invocation, that caller is the calling execution context inside the enclosing workflow: the suspended main-agent region that selected the invocation, or the workflow execution context that performs a workflow-declared invocation. The implementation may use any mechanism, but it must preserve this structured return relationship.

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

That authority must support heterogeneous parallel graphs rather than assuming all branches use one execution primitive. A single fan-out may combine mechanical execution, bounded raw LLM calls, and
bounded independent agents, while preserving the distinct lifecycle and context
contract of every branch.

This implication does not select a concurrency mechanism, scheduler, worker model, or process topology.

## 5.12 Context construction becomes an explicit boundary

Independent agents and raw LLM calls derive value from deliberately supplied
context. TURNLOCK therefore needs an architectural place where instructions,
task inputs, and context are assembled without conflating explicit workflow data
flow with implicit inheritance of the main-agent cognitive lineage.

For a workflow-declared independent agent, initial cognitive context must be
attributable to explicit workflow semantics. This requirement does not apply
automatically to child agents created through ordinary local main-agent
delegation. The exact representation, serialization, context API, and dataflow
mechanism remain open.

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

## 5.15 Completed execution requires an inspection boundary

Because completed execution must remain inspectable, the architecture must make
sufficient actual TURNLOCK-visible behavior available at an inspection boundary.
That behavior includes enough workflow-mediated structure, execution boundaries,
explicitly exposed inputs and results, and progression-relevant facts to support
the obligation in `TL-INV-033`.

The inspection boundary must preserve the distinction between actual execution
facts and a workflow definition displayed later. It may show a current or later
definition, but it cannot use that definition alone as proof of previous
execution behavior. This pressure makes the workflow-definition binding decision
consequential; `TL-INV-037` fixes that binding rule without selecting snapshot
semantics, live-edit semantics, revision identity, copy-on-start, or another
binding mechanism.

This implication requires neither a persistent event log nor a specific event,
storage, identifier, telemetry, retention, query, or user-interface design. Such
mechanisms remain replaceable and require their own derivation or decision.

## 5.16 Evaluation and optimization are layered above the execution substrate

Because evaluation objectives and optimization policy are not core TURNLOCK
semantics, the architecture must let evaluation and optimization be composed
above the execution substrate. TURNLOCK's responsibility includes executing
declared workflow semantics, exposing sufficient actual execution truth
(`TL-INV-033`), and preserving effective execution-condition provenance
(`TL-INV-036`) at its semantic boundary. It does not extend to owning evaluation
or optimization policy.

Evaluation or optimization logic requires no privileged runtime interface. It
can be implemented by a user, the main agent, an external evaluator, or another
higher-level system, and, where expressible using accepted primitives, by an
ordinary TURNLOCK workflow. Such behavior remains ordinary authored execution
and gains no runtime authority over the executions it inspects or the
workflows it proposes to change. Any resulting workflow refinement is authored
through the same artifact class as any other workflow change.

This implication does not select an evaluation API, metric set, experiment
model, comparison contract, optimizer algorithm, storage, or user interface.

## 5.17 Effective governing conditions require an attribution boundary

Because TURNLOCK must preserve effective execution-condition provenance, runtime
and adapter architecture must keep each condition TURNLOCK selects, binds,
explicitly supplies, or resolves attributable to the execution scope it governs
and provide a realizable semantic-boundary capture handoff through which that
relationship can be acquired before the required provenance is irreversibly
lost.

The architecture may distinguish unavailable or unknown conditions and need not
observe conditions outside TURNLOCK's boundary. It must not manufacture known
equality from missing information or convert a known protected condition into
unknown merely because its value is not disclosed. For a TURNLOCK-known
protected condition, the boundary must preserve a representation containing
condition-specific information rather than substitute an occurrence label or one
generic protected marker for all known condition provenance before or during
the realizable semantic-boundary capture handoff.

A particular consumer MAY receive a more restrictive view than the underlying
provenance made capturable through the realizable semantic-boundary capture
handoff, under separately governed policy. This implication
does not select an authorization or privacy model, require another consumer
context, exact-value disclosure, post-boundary availability or retention, or
that all capturable information appear through ordinary inspection surfaces. Whichever workflow
definition governs an invocation under `TL-INV-037` must remain attributable
when TURNLOCK binds or resolves it, without this implication selecting a
concrete representation.

This boundary does not select who captures the attribution, how long it remains
available, whether another layer persists it, or any database, event, identifier,
hash, snapshot, telemetry, run-model, replay, comparison, or reproduction
mechanism. It also establishes no public or cross-run stable identity and no
equality or difference evidence.

Architecture must make it structurally possible for an eligible conforming
capture context to be established in time to participate in this handoff.
When no consumer is attached, conformance still requires TURNLOCK to complete
its side of the semantic-boundary interaction through that structurally
realizable capability; mere internal existence is not a discharge event.
Actual receiver participation, successful delivery, consumer processing, and
acknowledgment are not required. Consumer absence, participant failure, or
delivery failure does not by itself create a universal retention obligation.
Once TURNLOCK has completed that conforming handoff, `TL-INV-036` alone does
not require continued capturability, and any stronger post-handoff
availability, persistence, or retention guarantee remains separately governed.
The capture boundary remains distinct from delivery acknowledgment, ordinary
inspection surfaces, and any storage mechanism.

## 5.18 Governing-definition stability requires execution-level attribution

Because every accepted invocation must retain one governing workflow definition,
the execution architecture must preserve a stable governing-definition
relationship for each active invocation independently of later mutation of the
source artifact. This implication prescribes no snapshot, hash, copy, lock,
database, revision, or file-system mechanism; it requires only that an ordinary
later source edit cannot silently replace the definition that governs an active
invocation's remaining declared topology, while each nested invocation
establishes its own governing definition at its own acceptance.

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
- a separate agent-only workflow language distinct from the artifact developers edit;
- an evaluator, benchmark system, run comparator, experiment manager, or workflow optimizer, including as a consequence of making completed executions inspectable;
- an owner of a universal evaluation objective, universal quality metrics, or a default superiority relation between workflows or executions;
- a replay, cross-run comparability, reproducibility, or execution-proof system;
- a universal execution record or a guarantee that TURNLOCK observes every causal, environmental, external, context, tool, or scheduling determinant;
- a persistence or retention system for effective execution-condition provenance;
- universal exact-value disclosure of protected effective conditions;
- a public or cross-run stable identity, equality operation, or difference proof for effective conditions;
- a universal authorization, access-control, or privacy-policy system for provenance capture;
- an owner of general filesystem, repository, OS, tool, or sandbox permissions for execution resources;
- an authority that infers workflow purpose to grant or deny workflow authoring, or that reserves privileges to official workflows or introduces a general runtime grant/revoke protocol;
- a requirement to expose private agent reasoning or record every tool call inside an agentic region.

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
what actual TURNLOCK-visible behavior remains inspectable after completion?
can the inspection distinguish execution facts from a later/current definition?
which effective conditions did TURNLOCK select, bind, explicitly supply, or
resolve for this execution scope?
can their attribution be exposed or captured without later reconstruction?
which candidate conditions remain unavailable or unknown?
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
what marks normal completion if reached, and what output does the contract require?
```

The authoring surface must additionally prove that the same workflow can be produced through either direct developer authoring or coding-agent authoring using public TURNLOCK primitives, without requiring a privileged generator path. The Pi implementation must prove the complete reference scenarios while keeping Pi-specific mechanisms below the TURNLOCK workflow semantics boundary.

After a reference execution completes, the architecture must also demonstrate
that enough actual boundary-level behavior remains inspectable to understand how
the workflow progressed. That demonstration must not rely on human or agent
recollection, must not substitute a current workflow definition for execution
truth, and need not disclose private agent reasoning or establish replay,
comparability, reproducibility, or proof.

When evaluation or optimization is part of a use case, the architecture must
identify who supplied the objective and must keep evaluation and optimization
policy outside TURNLOCK core runtime authority. Behavior that evaluates another
execution or proposes a refined workflow remains ordinary authored execution;
it must not obtain privileged control over the workflow it assesses, and any
resulting refinement is authored through the same artifact class as any other
workflow change.

The architecture must separately demonstrate effective execution-condition
provenance. For a condition TURNLOCK selects, binds, explicitly supplies, or
resolves, it must identify the governed execution scope and the realizable
semantic-boundary capture handoff by which that attribution can be acquired
before the required provenance is irreversibly lost. A nominal opportunity that
depends on an inaccessible internal instant or an accidental timing race does
not satisfy the demonstration. If no capture consumer is attached, the
demonstration must still identify the TURNLOCK-side semantic-boundary
interaction that discharges the handoff through the structurally realizable
capture capability; mere internal existence is insufficient, while actual
receiver participation, successful delivery, and acknowledgment are not
required. For a TURNLOCK-known protected condition, the demonstration must show
that, through the required realizable semantic-boundary capture handoff,
protection preserves condition-specific information bound to the condition
occurrence and its governed-scope attribution rather than substituting an
occurrence label or generic marker or misrepresenting it as unknown. It need
not disclose the protected value to every consumer, preserve the representation
after that handoff, or establish a public or cross-run stable identity,
underlying-value equality or difference evidence, persistence, replay,
reproducibility, or comparability.

# 8. Derived synopsis

This section is a non-authoritative synopsis derived from the specification's
owning sections. It introduces no lexical definition, product promise, or
invariant. If compressed wording here diverges, Section 0 governs product intent,
Section 2 governs terminology, and Section 3 governs obligations and stable
invariant identities.

TURNLOCK can currently be summarized as:

> **A harness-independent orchestration engine for coding-agent sessions that executes workflow-declared control, using the same TURNLOCK primitives whether authored by a developer or coding agent, and composes mechanical execution, bounded raw LLM inference, bounded independent agents, continuation of the user's main coding agent, concurrency, and nested workflows. The workflow program owns the declared orchestration logic; TURNLOCK executes it, keeps completed execution sufficiently inspectable, and preserves effective execution-condition provenance for conditions it selects, binds, explicitly supplies, or resolves. External actors retain evaluation and optimization policy. Pi is the first reference harness used to prove the model.**

The synopsis uses these canonical destinations:

- workflow, workflow artifact, and TURNLOCK primitives: Sections 2.2 and 2.3A;
- mechanical execution and mechanical step: Section 2.4;
- raw LLM inference and raw LLM inference step: Section 2.4A;
- independent agent and independent-agent step: Section 2.4B;
- main agent, main-agent handoff, and main-agent step: Sections 2.1 and 2.5;
- immediate caller context and caller stack: Section 2.6;
- control ownership and workflow-owned control: Section 2.7;
- workflow invocation surface: Section 2.3; and
- parallel fan-out/fan-in and nested workflow invocation: Section 2.8;
- execution inspectability: Section 2.9; and
- effective execution-condition provenance: Section 2.10.

The guiding allocation rule remains the product principle in Section 0.10 and
the obligation in `TL-INV-029`: use the minimum sufficient form of computation
or cognition for each region.

Evaluation and optimization policy remain outside TURNLOCK core: evaluation
objectives come from an explicitly responsible actor or authored workflow, and
the runtime never silently optimizes authored orchestration. TURNLOCK preserves
its own effective governing-condition attribution without deciding which
conditions matter to a property or whether executions are comparable.

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

TLC exploration is necessarily finite. "Integrated" means the formalized
mechanisms are connected in the same abstract model; it does not claim exhaustive
exploration of an unbounded real-world system. A finite TLC domain or exploration
bound is a formal-modeling choice, not a TURNLOCK product resource limit,
timeout, termination guarantee, or fairness premise.

Safety and liveness are distinct obligations. For example:

```text
safety:  a nested workflow never resumes the wrong caller
liveness: under the required fairness assumptions, a normally completable nested workflow eventually resumes the correct caller
```

Not every product invariant is necessarily expressible or useful as TLA+. DX and semantic-quality requirements may be explicitly marked `not-applicable`; state, ordering, ownership, lifecycle, nesting, concurrency, synchronization, and progress rules are strong formalization candidates.
