---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "product-rationale"
domain: "turnlock-rust"
severity: "informational"
name: "TURNLOCK Product Rationale"
---

# TURNLOCK — Product Rationale

> **Status and authority:** This document is non-normative. It explains user
> value, motivation, and product rationale behind the existing TURNLOCK Product
> Intent. It creates no product promise, invariant, obligation, architecture,
> mechanism, interface, representation, or implementation requirement. The
> [TURNLOCK specification](../specification/turnlock-spec.md) and accepted
> [ADRs](../adr/README.md), including their amendments, remain authoritative for
> their respective responsibilities. This rationale yields to those sources
> and is not an input that independently authorizes normative derivation. It
> describes intended value, not shipped capability or verification evidence.

## Intended user and unresolved problem

TURNLOCK is intended for a user building and running workflows inside an
existing interactive coding-agent session. The user may write workflow code
or ask the coding agent already present in that session to write or modify it.

The unresolved problem is not simply whether an agent can generate code, call
other agents, or describe a procedure. It is whether the user's working method
can execute without depending on an agent or the user to reconstruct and
coordinate its global progression at each boundary.

For a user whose method remains primarily conversational, the human can become
the fallback orchestrator:

```text
remember the next phase
→ remind the agent about an omitted check
→ coordinate independent work
→ collect results
→ restore the original plan after an investigation
→ explain where execution should resume
```

Generating a longer skill does not by itself remove that coordination
responsibility. Generating a custom runtime can remove it, but then the user
owns the runtime's control, continuation, integration, and composition problems
as well as the working method.

## Current pain

The motivating pains are repeated process supervision, unnecessary cognitive
work on already-decided orchestration, loss of continuity when automation uses
unrelated agents, and bespoke integration work whenever a method becomes more
compositional.

An apparently automated process can still require the user to remember whether
all reviews finished, whether a declared check ran, which caller should resume,
and whether the agent is following the method or improvising its global flow.

The intended reduction is in this coordination burden. It is not a claim that
all existing coding harnesses lack workflow execution, that every user has this
pain, or that every task needs TURNLOCK.

## Intended user outcome

The existing Product Intent supports a different relationship:

```text
user and coding agent
→ author an executable working method

workflow program
→ declares orchestration and its explicit regions of judgment

TURNLOCK
→ executes and coordinates the declared orchestration

execution resources
→ perform the work allocated to them

user
→ participates where the authored method calls for user judgment
```

A workflow remains naturally invocable from the coding-agent session. It can
execute mechanical work, request a bounded inference, start independent agents,
and temporarily return control to the existing main agent before resuming its
own progression. On normal completion, nested invocations return to their
immediate callers.

> **TURNLOCK lets users build tools that use their coding agent, rather than
> procedures their coding agent must remember to follow.**

This sentence explains the existing Product Intent; it does not replace it.

## Example: a reusable finalization method

An illustrative user request is:

> Build a finalization workflow that runs checks, obtains two independent
> reviews, returns to our existing agent session for the judgments and fixes
> that need our context, then resumes verification and finalization.

The resulting method could have this shape:

```text
natural workflow invocation in the current session
→ mechanical preparation and checks
→ workflow-declared independent reviews
→ collection and declared decision logic
→ existing main-agent region for contextual work and user interaction
→ recognized region completion or yield
→ mechanical verification and declared finalization
→ return to the immediate caller
```

The review count, decision conditions, corrections, and finalization policy are
choices in this example's workflow, not TURNLOCK defaults. If the main-agent
region invokes another available workflow, that nested workflow returns to the
same caller region rather than discarding the enclosing method.

TURNLOCK's role is not to decide that the method is good. It is to preserve the
method's declared control and continuation semantics while its resources work.

## Industrialization: working method becomes executable capability

The central industrialization opportunity is to move a recurring method out of
repeated conversational reconstruction and into an inspectable executable
artifact.

```text
working method
→ executable workflow
→ repeated use
→ observed execution
→ deliberate refinement of the method
```

The user can reuse and compose the method without reassigning its entire
coordination to the main agent on every invocation. Human and agent authors
work on the same kind of workflow artifact rather than separate semantic
products.

This can make process improvements cumulative. A better declared validation,
review arrangement, or contextual handoff can become part of the method used
in later executions instead of remaining advice in one conversation.

Industrialization here concerns how the method is executed. It does not imply
deterministic results, identical schedules, universal completion, automatic
software correctness, or that an inadequately designed method becomes good.

## Scalability: attention, coordination, and composition

### Human-attention scalability

The first scaling question is not how many machines can be started. It is how
much additional work can be delegated without requiring proportionally more
human reminders and coordination.

Keeping already-decided orchestration executable can reduce the need for the
user to supervise routine progression. Human attention can then concentrate on
judgment, exceptional conditions, and revision of the method itself.

This is an intended benefit, not a measured scaling law. A workflow that requires
a human decision at every region still has that human dependency. TURNLOCK does
not independently determine when human intervention is necessary.

### Method-complexity scalability

Sequencing, declared branching and iteration, heterogeneous parallel work,
nested invocation, and structured return can be composed without making the
main agent remember the whole control graph. The known coordination work stays
in the workflow rather than increasing the amount of procedure the main agent
must repeatedly reconstruct.

This does not remove legitimate resource constraints. In particular, the same
main-agent cognitive lineage is not an arbitrarily duplicable parallel worker.
Declared ordering or established mutual exclusion remains necessary where the
accepted semantics require it.

### Reuse and evolution scalability

An executable method is available for inspection and modification independently
of the conversation in which it was first authored. Its meaning is expressed
through TURNLOCK primitives rather than harness-internal control plumbing.

An accepted invocation keeps its governing workflow definition when a source
artifact is later edited. New invocations establish their own bindings. This
allows method evolution without silently changing the rules of an already
accepted invocation; it does not freeze every future nested callee into one
transitive snapshot or establish replayability.

Harness-independent meaning is an intended product property wherever support
is claimed. It is not evidence that every harness is supported or that every
integration can preserve the same capabilities today.

## Appropriate cognition without sacrificing session continuity

A method can keep a mechanical check in executable logic, allocate an extraction
to raw inference, give an investigation to an independent agent, and return
context-sensitive work to the user's existing main agent.

The author can therefore avoid routing every operation through the richest
cognitive resource. Possible cost, latency, and context benefits depend on the
method and realization; no numeric improvement is promised.

The main-agent case matters because using the same model with selected context
is not necessarily continuation of the user's ongoing working relationship.
The existing Product Intent preserves that continuation and ordinary interactive
agency rather than silently substituting a fresh agent or a one-shot call.

The intended outcome combines executable coordination around an agentic region
with flexible work inside it. It does not promise unlimited context or perfect
memory.

## Capabilities requiring TURNLOCK or an equivalent system

### Executable control rather than procedural advice

A prompt saying that a check should happen does not itself make a successful
workflow continuation depend on that check. Something must execute and enforce
the declared control relationship.

TURNLOCK supplies that responsibility for its workflow semantics. A native
harness feature, extension, or other runtime providing the same responsibility
is an equivalent on that dimension. The necessity concerns a system capability,
not the TURNLOCK brand.

### Bidirectional use of the existing agent

A program that returns control to the existing interactive main agent and then
resumes the correct continuation needs more than a generic model endpoint. It
needs a compatible control boundary and continuation state.

Structured nesting additionally requires preservation of the immediate caller.
Messages, summaries, or manual relaunches may be useful, but they are not by
themselves a guarantee of the same continuation contract.

### Composition that preserves authority and lineage

Parallel and nested work need coordination that preserves each region's
semantics. Runtime scheduling alone cannot invent missing causal order or make
an inadmissible composition valid. Dynamic invocation by an independent agent
also does not silently acquire global orchestration authority or access to the
main-agent lineage.

A conforming equivalent must preserve these distinctions rather than merely
launch the same number of workers.

### Execution truth that remains available at the required boundary

A workflow definition describes permitted behavior, not necessarily what
actually happened. Faithful inspection requires sufficient actual execution
truth, and relevant effective conditions known through TURNLOCK's specified
responsibilities require attributable provenance.

Once necessary information has been irreversibly lost, a later evaluator cannot
in general recover it from the current workflow file or a conversational
summary. An equivalent capture capability can preserve such information; this
is not a claim of proprietary exclusivity.

## Inspection supports refinement, not a correctness oracle

TURNLOCK's inspectability contract covers realized execution or realized-prefix
truth for accepted invocations with a TURNLOCK-observed terminal or cessation
outcome. It does not turn unrealized work into execution or unknown terminal
facts into known causes.

The user can use available execution information to investigate the difference
between a method problem, an outcome produced inside a region, and an execution
that stopped before later work. Interpretation and evaluation objectives remain
with an explicitly responsible actor or authored workflow.

Core's realizable inspection and provenance handoffs do not universally require
an actual participating consumer, successful delivery, or post-handoff
persistence. A durable history, stronger comparison facilities, and experimental
profiles require separately established responsibilities.

An agent may still reason incorrectly, and a workflow may contain an inadequate
check. Preserving declared orchestration does not eliminate hallucinations,
prove the usefulness of the method, or enforce a general sandbox over local
agent actions.

## Relationship to existing harnesses and tools

Scripts, skills, hooks, native workflows, and agent frameworks can already
provide useful parts of this space. TURNLOCK is not justified by asserting that
none of them can execute code or coordinate agents.

The [architectural vision](../vision/turnlock-vision.md) treats compatible
harness-native mechanisms as realization assets. Its Perfect Harness Test asks
which TURNLOCK value remains when the harness already implements the underlying
mechanisms well.

If a user's existing environment already supplies every capability and guarantee
the user needs, this rationale does not establish a need for an additional
runtime. TURNLOCK's value must come from the required control, composition,
continuity, inspectability, or cross-harness semantic boundary, not unnecessary
duplication.

## TURNLOCK and possible Turnlock Cloud value

TURNLOCK addresses executable working methods inside coding-agent sessions.
The [Turnlock Cloud Product Rationale](turnlock-cloud-product-rationale.md)
explains a separate possible managed-execution and run-evaluation opportunity.

Core remains independently useful without that product. Cloud infrastructure,
durable run history, and evaluation facilities are not implied Core requirements
merely because they would make industrialized use more convenient.

## Explicit boundaries and non-goals

This rationale does not establish crash durability, exactly-once external
effects, transactional phases, replay, reproducibility, a security sandbox,
elastic compute, a universal optimizer, or a guarantee of bug-free software.
It selects no language, scheduler, protocol, storage mechanism, provider, or
harness API. It adds no SLA, throughput target, cost claim, adoption claim, or
proof of formal verification.

The Gate A campaign runner and its construction briefs govern the assurance
controller, not TURNLOCK product runtime behavior. Their mechanisms and
operational guarantees are not imported into this rationale.

## Reading basis

The explanatory basis is the existing specification's Product Intent, its
current boundaries, and its architectural implications, particularly Sections
0.1–0.13I, 4, and 5. The architectural vision provides non-normative motivation.
The two future design-space documents linked by the Cloud rationale preserve
possibilities only; they supply no additional Core authority.

> **TURNLOCK aims to make a user's working method executable and reusable,
> reducing dependence on repeated human or agent reconstruction of its
> coordination while preserving access to the user's existing coding agent.**
