---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "product-rationale"
domain: "turnlock-cloud"
severity: "informational"
name: "Turnlock Cloud Product Rationale"
---

# Turnlock Cloud — Product Rationale

> **Status and authority:** This document is non-normative. It explains the user
> and strategic value of the possible adjacent product explored by the
> [future managed execution design space](../vision/future-managed-execution.md)
> and the [future workflow run-evaluation design space](../vision/future-workflow-run-evaluation.md).
> Those documents establish neither Turnlock Cloud Product Intent nor accepted
> Cloud architecture. This rationale does not promote that opportunity into an
> established product or a candidate normative specification. It creates no
> TURNLOCK or Turnlock Cloud obligation, architecture, mechanism, interface,
> data model, capture contract, persistence requirement, or implementation
> commitment. It is not an input to TURNLOCK Core derivation. The
> [TURNLOCK specification](../specification/turnlock-spec.md) and accepted
> [ADRs](../adr/README.md) retain their respective authority.

## Intended user and unresolved problem

The motivating user has an executable working method, or is building one inside
a coding-agent session, and wants to use it beyond the resources and operational
attention the user is willing to manage personally.

A workflow can declare work without supplying the infrastructure on which that
work runs. As a method uses more concurrent agents, builds, tests, repositories,
and experiments, the surrounding work can include preparing environments,
providing tools and scoped credentials, protecting shared mutable resources,
collecting results, and disposing of temporary state.

The user may also accumulate many executions without a retained, interpretable
basis for learning whether changes to the method actually help.

These are two related but independent problems:

```text
how to operate the executable method at useful scale

how to learn from the method's actual executions
```

## Current pain

A user can otherwise become both workflow author and infrastructure operator.
The agent can help write provisioning scripts, but the resulting infrastructure
still needs correct lifecycle, isolation, permissions, result extraction, and
failure handling.

Parallel work can amplify interference on shared files, tools, services, and
other mutable surfaces. Cleaning up one execution's temporary state can become
another recurring task. Local compute can also limit which declared methods
are practical to use.

Separately, disconnected results, logs, and later workflow versions can leave
the user reconstructing what happened and whether a perceived improvement was
caused by a method change or by different execution conditions.

These are motivating conditions, not claims that all users need managed
execution or that existing infrastructure and evaluation products cannot help.

## Potential user outcome

A possible Turnlock Cloud product could let the user remain focused on the
working method while a compatible managed layer supplies execution resources
and, where separately established, facilities for retaining and evaluating
execution information.

```text
user and coding agent
→ author the working method

TURNLOCK
→ executes its declared orchestration

possible managed execution
→ supplies compatible execution environments and resources

possible run-evaluation facilities
→ preserve and use authorized available execution information

user or explicitly responsible evaluator
→ assesses the method against an explicit objective
→ may author a later workflow version
```

> **Turnlock Cloud could make executable working methods practical to operate,
> scale, and improve without requiring each user to build the surrounding
> execution and evaluation infrastructure.**

This is product rationale for an opportunity, not an accepted service guarantee.
The managed-execution and evaluation sides need not be one indivisible package.

## Example: parallel investigation without a manually operated environment fleet

Consider an authored workflow that requests several independent investigations,
mechanical experiments, collection of their results, and contextual synthesis
with the existing main agent.

A compatible managed realization could make the workflow practical by preparing
sufficiently isolated environments, materializing the configured workspace,
supplying the needed tools and scoped capabilities, executing the selected
resources, extracting required results, and retiring temporary environments.

The user would not have to operate that sequence separately for each unit of
work. The number of branches and the conditions for collecting or using results
would still come from the workflow, not from an infrastructure service deciding
to invent a different method.

This example selects no environment granularity. It does not require one VM per
agent, one environment per workflow, or a particular provider. Contextual
synthesis remains a genuine main-agent continuation where declared, not a fresh
remote worker relabeled as the main agent.

## Industrialization: operating conditions become a managed capability

TURNLOCK's industrialization opportunity concerns executable method. The
managed-execution opportunity concerns the operational work needed to use that
method repeatedly.

```text
executable method
+
compatible prepared execution resources
+
required result and effect handling
+
retirement of disposable compute
→ possible repeatable operational practice
```

The benefit is not that the user can access a machine somewhere. It is that the
user need not repeatedly assemble and operate the environment lifecycle around
each method.

Repeatable operational practice does not imply deterministic computation or
identical results. Destroying compute also does not authorize loss of state or
effects that another governing system requires to survive. Exact lifecycle,
extraction, persistence, and recovery contracts remain separate design work.

## Scalability: resources without proportional operational burden

### Execution-capacity scalability

Where the workflow declares admissible parallel work, a managed realization
could supply resources beyond the user's local machine. This can make methods
with more investigations, experiments, builds, or tests practical to execute.

More compute does not authorize more workflow branches than the authored
semantics permit. Elasticity also does not guarantee linear speedup, unlimited
capacity, lower cost, or the completion of every execution resource.

### Operational-attention scalability

A managed environment lifecycle could reduce the amount of preparation,
supervision, and cleanup the user performs as execution volume grows.

This is distinct from TURNLOCK's reduction of process-coordination work. A
workflow can have explicit orchestration while its environments remain manually
operated; a cloud can supply many machines while the user still coordinates
all work conversationally.

The combined value would address both burdens without confusing them.

### Isolation and interference boundaries

Disposable isolated execution could allow broad local agent activity while
reducing accidental interference with other executions and the user's persistent
workspace. This is local freedom within an appropriately bounded environment,
not universal privilege.

Isolation does not establish that credentials are safe, network access is
appropriate, or external effects are correctly authorized and serialized. Two
isolated agents can still propose incompatible changes to the same persistent
repository. Publication, integration, and resource-conflict handling remain
responsibilities of the applicable surrounding systems and contracts.

### Remaining bottlenecks

External services, available compute, budgets, shared resources, required human
judgment, and the existing main-agent lineage can remain bottlenecks. A remote
backend cannot make the same main-agent lineage arbitrarily parallel or remove
an explicit human approval by changing placement.

Neither the current Core contract nor this rationale establishes that an
interactive session can be abandoned and later recovered after arbitrary
machine loss. Running some resources remotely is not a session-durability
contract.

## Run history is different from a workflow definition

An authored workflow describes permitted orchestration. A useful execution
history describes realized work and the information actually available about
it.

TURNLOCK already has independently justified execution-inspectability and
effective-condition provenance responsibilities. Those responsibilities are a
possible foundation for richer facilities, not a complete Cloud data product.
They do not imply a universal event set, observation of every internal agent
action, or indefinite storage.

A product offering durable history would need its own actual capture and
retention responsibilities. Core may discharge a conforming boundary handoff
without a participating consumer or successful delivery. Cloud cannot infer a
retained observation from the mere existence of Core's capture capability.

## Observation-time capture and later reconstruction

```text
what was actually known and captured at execution time
≠
what can be inferred later from mutable artifacts
```

A later workflow file, log, or model label may support useful reconstruction,
but it cannot in general recover information that was never captured and no
longer exists. Relevant examples can include the actual governing definition,
realized branch relationships, explicitly exposed results, and effective
conditions attributable to the work they governed.

An authorized capture facility could preserve such information where it is
actually available. The point is not that later reconstruction is always
impossible or that only Turnlock Cloud can capture data. It is that retrospective
analysis cannot be assumed to recreate every observation-time distinction.

Unknown conditions remain unknown. Protected values are not automatically
available to every consumer. Observation, authorization, disclosure, retention,
and comparison sufficiency are different concerns whose concrete contracts this
rationale does not select.

## Industrializing improvement of the method

Retained executions could support a second cumulative process: improving the
working method itself.

```text
workflow generation W1
→ executions with available observations and conditions
→ evaluation for an explicitly chosen property
→ possible authorship of W2
→ separate W2 executions
→ comparison where the evaluator's contract permits it
```

Possible questions include whether an additional review helps, whether another
context-construction strategy improves a selected outcome, or whether a change
in execution form is worthwhile for an explicitly supplied objective.

Those are examples of user questions, not universal metrics or accepted Cloud
features. An evaluator determines what counts as improvement and when available
evidence supports the comparison. TURNLOCK Core does not acquire that policy.

Producing W2 is authorship. It does not rewrite the governing definition of an
already accepted W1 invocation or give an evaluator privileged runtime control.

The potential benefit is that method improvements can accumulate in executable
artifacts, while observations can inform the next revision. This can complement
improvements in the underlying models without depending on a particular model
improvement forecast.

## Experimental efficiency rather than promised determinism

Managed execution could make more concrete execution conditions known or
controllable. Combined with available provenance, an evaluator might treat
relevant variation explicitly rather than automatically average over all of it.

Where justified for the chosen property, controlled, paired, or blocked
comparisons may reduce residual unexplained variation. This could increase the
information obtained per execution and sometimes reduce the repetitions needed
for a particular comparison objective.

No guaranteed reduction follows from collecting more data or running in the
cloud. The outcome depends on the property, effect size, residual variation,
experimental design, and actual observability. Stochastic results remain
stochastic; valid comparison and reproducibility are not automatic consequences
of managed execution.

## Capabilities requiring an equivalent surrounding system

TURNLOCK Core cannot supply physical capacity, isolation, environment lifecycle,
durable history, or an experimental discipline merely by defining orchestration.
Those capabilities require corresponding systems and responsibilities.

A user can build them, assemble existing services, self-host compatible
facilities, or obtain them through a managed product. None is exclusive to the
Turnlock Cloud name. A future product's value would be a coherent, compatible
way to obtain the needed capabilities without rebuilding the surrounding stack
for each working method.

The strongest irrecoverability concern is historical: an alternative deployed
later cannot necessarily recreate execution-time information that was never
retained. It can provide equivalent capture for future work.

## Core, managed execution, and evaluation boundaries

The possible relationship remains:

```text
workflow author
→ decides the method

TURNLOCK Core
→ preserves and executes the declared control semantics
→ supplies its independently justified inspection and provenance boundary

managed realization
→ supplies compatible operational resources

responsible evaluator or ordinary authored workflow
→ owns objectives, interpretation, comparison, and refinement policy
```

The existing runtime-composition obligation provides a boundary for compatible
external realizations without making their infrastructure choices Core
semantics. An accepted realization cannot silently substitute a different
execution form or bypass the semantics of the governed use.

Cloud does not become a requirement for TURNLOCK use. A datum useful to Cloud
does not become a Core capture obligation merely because an evaluator wants it.
Likewise, a convenient managed mechanism does not decide TURNLOCK's ontology.

Ring and Ring Cloud supply a precedent for separating product rationale from
normative product meaning. They do not supply TURNLOCK governance semantics,
Cloud requirements, training-data rights, or a mandatory cross-product
integration.

## Explicit boundaries and non-goals

This rationale selects no SaaS-only model, provider, VM or container technology,
environment-per-agent rule, workspace protocol, scheduler, autoscaler,
persistence store, event schema, public API, billing model, retention policy,
security model, training pipeline, or proprietary workflow-authoring surface.

It establishes no SLA, numeric speedup, cost reduction, statistical guarantee,
exactly-once external effect, regulatory assurance, automatic method optimizer,
or claim that the described Cloud capabilities already exist.

Establishing Turnlock Cloud Product Intent and deriving its interfaces,
architecture, guarantees, and operating model remain separate authority steps.
Neither Core's normative scope nor the two future-consideration documents are
changed by this rationale.

## Reading basis

The [managed-execution consideration](../vision/future-managed-execution.md)
provides the isolation, workspace, elasticity, and lifecycle opportunity. The
[run-evaluation consideration](../vision/future-workflow-run-evaluation.md)
provides the comparison, variance, workflow-generation, and refinement
opportunity. Both remain non-normative and independent.

The [TURNLOCK Product Rationale](turnlock-product-rationale.md) explains the
existing Core product's intended user value. The normative specification,
particularly Sections 0.8B and 0.13B–F, governs the Core boundaries used here.

> **TURNLOCK aims to industrialize executable working methods. A possible
> Turnlock Cloud could make their operation scalable and their improvement more
> systematic, without transferring method ownership to the infrastructure.**
