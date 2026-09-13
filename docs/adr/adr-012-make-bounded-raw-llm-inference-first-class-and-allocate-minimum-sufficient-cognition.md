---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Make bounded raw LLM inference first-class and allocate the minimum sufficient cognition"
id: "ADR-012"
status: "accepted"
date: "2026-09-13"
decision_body_sha256: "772dca4b7406ad07318d34edc78e9b65ab046fa6de4594e8c2429795c6855669"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs: []
---

# ADR-012: Make bounded raw LLM inference first-class and allocate the minimum sufficient cognition

- **Status:** Accepted
- **Date:** 2026-09-13
- **Decision order:** 012

## Context

After independent agents became a required workflow primitive, the product discussion identified a further distinction: not every semantic task requires an autonomous multi-turn agent.

Many tasks already have all required information available and need only one bounded semantic transformation: classification, extraction, summarization, scoring, ranking, rewriting, adjudication, or another direct inference. Creating an agentic loop for such a task can add unnecessary turns, context, tool surface, latency, and budget.

This reveals a broader spectrum of execution forms rather than a binary mechanical/agentic choice:

```text
deterministic computation
raw LLM inference
independent agent
main-agent continuation
```

The workflow should be able to choose the form whose capabilities match the task instead of routing all semantic work through the most powerful execution mode.

The discussion also clarified that TURNLOCK's deterministic-orchestration thesis does not require deterministic outputs from every leaf. A workflow can explicitly control when and how probabilistic LLM or agent computations occur while still owning the global control graph.

## Decision

TURNLOCK MUST support **bounded raw LLM inference as a first-class workflow execution form** distinct from both independent-agent execution and main-agent continuation.

Its semantic shape is:

```text
explicit instruction + explicit context
              ↓
         model inference
              ↓
            result
```

A raw LLM inference does not request an autonomous observe/reason/act loop, persistent cognitive lineage, or continuation of the user's interactive main-agent session.

TURNLOCK MUST allow multiple raw LLM calls to be executed concurrently when the workflow declares them independent. Parallel calls MAY perform the same task for diversity/redundancy or different tasks for decomposition.

Raw LLM branches MUST also be composable in a heterogeneous parallel region with mechanical computation and bounded independent-agent branches. The workflow may therefore mix execution forms in one fan-out while preserving each branch's distinct semantics.

TURNLOCK adopts the following product principle:

> **For each workflow region, use the minimum sufficient form of computation or cognition required to perform the task correctly.**

The workflow author must therefore be able to distinguish and deliberately select:

```text
0. deterministic computation
1. bounded raw LLM inference
2. bounded independent agentic execution
3. continuation of the main interactive agent
```

TURNLOCK further adopts the rule:

> **Deterministic orchestration does not require deterministic leaf computations.**

Probabilistic model or agent outputs do not by themselves transfer global orchestration authority away from the workflow.

This ADR does not fix model/provider selection, inference parameters, output schemas, routing/fallback strategy, context packaging, caching, or token/cost controls.

## Rationale

Using an autonomous agent when one model inference is sufficient wastes capabilities the task does not need. It can increase cost and latency and may broaden context unnecessarily.

Conversely, forcing a difficult exploratory task into one LLM call can under-provision the task, and replacing main-agent continuation with either form loses session continuity.

The distinct execution forms let workflow authors design an explicit cognitive architecture:

```text
cheap bounded inference for simple semantic transforms
independent bounded agency for autonomous exploration
main-agent continuation when the living session context matters
mechanical execution where no model intelligence is required
```

This also enables deterministic escalation patterns, for example:

```text
3 cheap LLM judgments in parallel
→ agreement? continue
→ disagreement? independent agent adjudicates
→ still unresolved? main-agent continuation
```

The workflow remains the orchestrator throughout because it declares the escalation topology.

## Consequences

- TURNLOCK has four conceptually distinct execution levels: deterministic computation, raw LLM inference, independent agents, and main-agent continuation.
- A universal generic "agent step" is insufficient as the product model.
- The runtime must preserve different lifecycle/context semantics for raw inference and agentic execution.
- Workflows can optimize cost, latency, context size, and agency intentionally rather than implicitly.
- Parallel raw LLM inference is a workflow-owned capability just like parallel independent-agent work.
- Probabilistic leaves are compatible with deterministic workflow control.
- Future model/provider and budget controls become important design work, but are not selected by this ADR.

## Alternatives considered

### Express one-shot LLM work by spawning an independent agent

Rejected as the only mechanism. It adds an autonomous loop and lifecycle semantics that many bounded semantic tasks do not require.

### Express all semantic work through the main agent

Rejected. It loses context/budget isolation and pushes known semantic calls into the expensive, continuity-preserving execution mode.

### Allow LLM calls only as implementation details of mechanical code

Rejected as the product abstraction. Although code could technically call a provider API, TURNLOCK needs to preserve the semantic distinction so workflows, adapters, observability, budgeting, concurrency, and conformance can reason about bounded model inference directly.

### Require all workflow leaves to be deterministic

Rejected. TURNLOCK requires deterministic ownership of orchestration, not deterministic outputs from every semantic computation.

## Verification obligation

A conforming implementation must demonstrate a workflow in which:

```text
mechanical input preparation
→ multiple bounded LLM calls execute concurrently
→ workflow collects their outputs
→ mechanical or declared semantic logic evaluates those outputs
→ workflow continues without transferring global orchestration authority to any model
```

It must also demonstrate that a raw LLM call is observably distinct from an independent agent and from main-agent continuation in lifecycle and context semantics.
