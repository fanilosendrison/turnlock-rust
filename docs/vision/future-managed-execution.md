---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "future-consideration"
domain: "turnlock-rust"
severity: "informational"
name: "Future managed execution design space"
---

# Future managed execution design space

> - **Status:** Non-normative future consideration
> - **Authority:** None
> - **Creates TURNLOCK semantics:** No
> - **Creates invariants:** No
> - **Selects TURNLOCK architecture:** No
> - **Selects Turnlock Cloud architecture:** No
> - **Establishes Turnlock Cloud as a product:** No
>
> Authoritative TURNLOCK meaning remains in the
> [TURNLOCK specification](../specification/turnlock-spec.md) and accepted
> [ADRs](../adr/README.md). If this document conflicts with either source, this
> document yields.
>
> [ADR-029](../adr/adr-029-separate-local-execution-capabilities-from-immutable-invocation-orchestration.md)
> assigns general operational capability and permission policy to the
> surrounding environment. [ADR-030](../adr/adr-030-make-turnlock-core-a-runtime-composable-execution-substrate.md)
> and [ADR-031](../adr/adr-031-clarify-the-runtime-realization-composability-trigger.md)
> require runtime composition of semantically compatible external realizations
> when their accepted trigger applies, without making every realization a
> TURNLOCK semantic responsibility. Those decisions do not require the future
> managed-execution capability or product explored here.

## 1. Purpose and classification

This document preserves a future managed-execution design space. It has no
product authority over TURNLOCK, establishes neither a managed product nor
Turnlock Cloud, and creates no requirement for cloud execution, remote
execution, virtual machines, or any other compute realization. It does not alter
the current TURNLOCK Core boundary.

TURNLOCK may later have an adjacent managed execution capability or commercial
managed product capable of realizing TURNLOCK execution through remotely
managed, elastic, isolated execution infrastructure. Such capabilities may
potentially form part of a product named **Turnlock Cloud**. Establishing that
product and its boundary would require separate future authority.

This exploration is classified as `no-normative-impact` in the
`repository-governance-or-documentation` layer. It preserves opportunities and
questions without deriving TURNLOCK semantics or selecting implementation
architecture.

## 2. Motivation

Increasingly capable coding agents may need broad access to development
workspaces and tools in order to:

- inspect many repositories;
- modify files;
- run arbitrary development tools;
- compile software;
- run tests;
- start services;
- use Docker or equivalent tooling when the environment allows it;
- perform experiments; and
- create temporary state.

The scaling problem has this shape:

```text
increasingly capable coding agents
        ↓
need broad access to development tools and workspace
        ↓
shared mutable execution surfaces create interference and blast-radius risk
        ↓
fine-grained restriction of every possible action may reduce useful agency
        ↓
isolated disposable execution can move part of the safety boundary
from per-action restriction to environment containment
```

A candidate strategy is to reduce the blast radius of mutable work by assigning
an execution sufficiently isolated compute, materializing the workspace it
needs, permitting broad local operational capability inside that boundary,
extracting required results or authoritative effects, and then retiring or
destroying the disposable environment.

```text
give one execution sufficiently isolated compute
        ↓
materialize the development workspace required for that execution
        ↓
allow broad local operational capability inside that boundary
        ↓
extract required results / authoritative effects
        ↓
retire or destroy the disposable environment
```

The design hypothesis is that broad local agent freedom can be made safer by
confining mutable operational effects to a disposable isolated execution
environment. It is not an accepted TURNLOCK guarantee.

Concurrency strengthens the motivation:

```text
one mutable agent
→ manageable locally

many concurrent mutable agents
→ shared-machine interference
→ mutable residue
→ resource contention
→ accidental cross-execution effects
```

Disposable isolation does not solve every security, correctness, authority, or
operational problem. It may move part of the safety boundary; it does not remove
the need for other boundaries.

## 3. Managed execution as an adjacent capability

The central conceptual separation is:

```text
TURNLOCK Core
→ executes declared workflow semantics

managed execution capability
→ may realize selected execution resources using managed infrastructure
```

The semantic execution form and its concrete compute realization remain
separate:

```text
TURNLOCK execution primitive
!=
specific compute realization

independent agent
!=
VM

mechanical execution
!=
local process

main-agent continuation
!=
remote worker
```

A virtual machine, container, local process, remote worker, or another compute
form could be a realization asset only where it preserves the applicable
TURNLOCK semantics. The realization does not redefine the execution form.

## 4. Candidate managed execution shape

One illustrative candidate has a persistent managed control plane allocating
work to ephemeral compute environments:

```text
persistent managed control plane
            │
            │ allocates execution
            ▼
     ephemeral compute environments
       ┌──────┼──────┐
       ▼      ▼      ▼
     env A  env B  env C
       │      │      │
 execution execution execution
       │      │      │
       └── results / effects ──┘
```

A software-engineering-oriented realization could follow this shape:

```text
request for isolated execution
        ↓
provision disposable environment
        ↓
start from a known base
        ↓
materialize the configured development workspace
        ↓
supply required tools / harness capabilities / scoped credentials
        ↓
execute the requested TURNLOCK execution resource
        ↓
capture required outputs and authoritative effects
        ↓
retire the environment
```

This is one candidate realization, not accepted architecture. It does not imply
that every TURNLOCK region receives a separate environment. The granularity of
an environment remains undecided.

## 5. Ephemeral isolated environments

Candidate isolation technologies include:

- virtual machines;
- microVMs;
- containers; and
- other isolation technologies.

No technology is selected. A disposable virtual machine is particularly
interesting for mutable software-development work because it could provide a
strong operational isolation boundary while allowing broad local capability.
That observation creates no VM requirement.

Ephemerality concerns the lifetime of compute, not the semantic lifetime of
state:

```text
ephemeral
!=
stateless product semantics

environment destruction
!=
permission to lose authoritative state that another governing system requires
```

A managed execution capability cannot assume that destroying compute makes all
logically relevant state disposable. The mechanism by which required state or
effects survive remains open.

## 6. Development workspace materialization

A future managed capability could materialize a complete configured development
workspace inside an execution environment. For the currently motivating
personal Development System architecture, that possibility may resemble:

```text
fresh environment
+
all repositories in the configured development workspace
+
each repository materialized from authoritative state
+
toolchain / harness availability
```

This is a possible software-engineering profile, not a universal TURNLOCK
requirement. Initial task prediction does not necessarily need to constrain
which repositories are inspectable in such a profile: broad inspection may be
valuable when the relevant repository cannot be known in advance.

Repository visibility and repository mutation authority are separate concerns.
An environment may expose a repository for inspection without granting authority
to publish or otherwise make authoritative changes to it.

This document does not define Git mechanics, a clone protocol, a workspace
manifest, caches, images, or synchronization.

## 7. Broad local capability and bounded blast radius

A mutable coding agent may benefit from broad operational freedom inside its
assigned environment while the environment boundary limits accidental impact on
other executions and persistent infrastructure. Candidate local activities
include:

- repository edits;
- arbitrary build commands;
- tests;
- local service startup;
- temporary configuration; and
- destructive changes inside the disposable environment.

This hypothesis does not imply:

- unrestricted access to cloud control-plane credentials;
- unrestricted access to other customers;
- unrestricted access to persistent infrastructure;
- bypass of external authorization;
- elimination of secret management;
- elimination of network policy; or
- elimination of security boundaries.

The hypothesis is local freedom within a bounded disposable environment, not
universal privilege.

## 8. Elastic concurrency

Managed execution may eventually map workflow-declared concurrency to elastic
compute:

```text
TURNLOCK-declared parallel execution
        ↓
managed execution service
        ↓
multiple isolated execution environments
        ↓
results return to TURNLOCK-owned workflow progression
```

The authority split remains:

```text
workflow topology
→ remains declared by workflow semantics

compute allocation
→ managed realization concern

more VMs
→ does not authorize TURNLOCK to invent more workflow branches
```

This possibility selects no autoscaling algorithm, scheduler, allocation policy,
or environment granularity.

## 9. Relationship to TURNLOCK Core

TURNLOCK Core remains independently usable without any future managed execution
capability.

```text
TURNLOCK without managed execution
→ valid product

TURNLOCK + future managed execution
→ possible additional realization capability
```

The following are not requirements of TURNLOCK Core as a consequence of this
document:

- mandatory network access;
- mandatory cloud account;
- mandatory hosted control plane;
- mandatory remote persistence;
- mandatory telemetry;
- mandatory VM provisioning;
- mandatory workspace cloning; and
- mandatory remote agent execution.

ADR-030 and ADR-031 provide an accepted reason to preserve runtime composition
of semantically compatible external realizations when their trigger applies.
They do not establish this managed product or any specific environment
mechanism. ADR-029 keeps general environment permissions and operational
capability outside TURNLOCK Core.

## 10. Relationship to proto-go and other consumers

proto-go already owns its own Managed Authoring Environment product guarantees.
A future managed execution capability may be one candidate realization capable
of satisfying some or all of those requirements. That possibility does not make
proto-go's Managed Authoring Environment semantics TURNLOCK semantics, does not
make every TURNLOCK execution a `ManagedContribution`, and does not make the
future managed execution layer owned by proto-go.

Other TURNLOCK workflows may also benefit from isolated managed execution
without being proto-go workflows.

```text
consumer
→ owns consumer-specific requirements

managed execution capability
→ may provide a compatible realization

TURNLOCK
→ executes declared orchestration semantics
```

## 11. Relationship to future workflow run evaluation

The [future workflow run-evaluation design space](future-workflow-run-evaluation.md)
preserves a complementary but independent future consideration.

```text
future managed execution
→ controls / provides more of the concrete execution realization

future workflow run evaluation
→ may consume stronger execution information for observation,
  comparison, evaluation, reproducibility profiles, or refinement
```

A possible relationship is:

```text
managed execution
        ↓
more known execution conditions
        ↓
potentially stronger provenance / observability
        ↓
potentially stronger optional run-evaluation profiles
```

Managed execution does not automatically make runs reproducible, comparable,
deterministic, or valid experiments. This relationship does not strengthen
current TURNLOCK inspectability or execution-condition provenance semantics.

## 12. Possible future Turnlock Cloud relationship

Some combination of:

```text
managed execution
+
run history / stronger observability
+
comparison / evaluation facilities
+
workflow-generation or refinement support
```

may later form part of a commercial or managed product such as **Turnlock
Cloud**. This is only a future product hypothesis.

This document does not establish:

```text
Turnlock Cloud Product Intent
Turnlock Cloud architecture
Turnlock Cloud packaging
Turnlock Cloud pricing
Turnlock Cloud deployment model
Turnlock Cloud API
Turnlock Cloud data model
Turnlock Cloud provider model
```

Turnlock Cloud is not an accepted product as a consequence of this document.

## 13. Provider neutrality

No provider is selected. Possible infrastructure could include OVHcloud, AWS,
Google Cloud, Azure, bare-metal infrastructure, customer-owned infrastructure,
or another provider-neutral realization.

An early prototype may use OVHcloud Public Cloud without giving OVHcloud
semantic or architectural authority. This document defines no OVHcloud-specific
architecture.

## 14. Candidate deployment shapes

Possible deployment shapes include:

- managed SaaS;
- self-hosted control plane;
- BYOC / customer cloud;
- hybrid; and
- local-only realization.

A currently interesting candidate combines:

```text
persistent control plane
+
ephemeral compute per sufficiently isolated unit of execution
```

No unit granularity is selected. It remains open whether the unit maps to:

```text
workflow invocation
execution region
independent agent
task
contribution
another runtime unit
```

## 15. Explicit non-goals

This document does not define:

- TURNLOCK Core semantics;
- new `TL-INV` identities;
- a new ADR;
- a VM requirement;
- a VM-per-agent requirement;
- a VM-per-workflow requirement;
- a cloud requirement;
- a provider requirement;
- a scheduler;
- an autoscaler;
- a provisioning API;
- a workspace manifest;
- a clone protocol;
- an image format;
- a cache design;
- a secrets system;
- an authorization model;
- a network policy;
- a billing model;
- a multi-tenancy model;
- a durable state store;
- an execution-result schema;
- a remote-execution protocol;
- a control-plane/data-plane protocol;
- Turnlock Cloud Product Intent; or
- Turnlock Cloud architecture.

It also does not define environment lifecycle protocols, persistence mechanics,
provider adapters, pricing, packaging, deployment contracts, or any new
TURNLOCK execution primitive.

## 16. Open questions

The following questions are intentionally unanswered:

1. What execution granularity should receive an isolated environment?
2. Which execution forms benefit from remote managed realization?
3. When is environment reuse safe versus disposal preferable?
4. What must be authoritative before workspace materialization?
5. How is authoritative output extracted before environment retirement?
6. Which state belongs to the disposable environment and which must survive it?
7. How should a complete development workspace be materialized efficiently?
8. Can caching or prebuilt images preserve freshness and authority requirements?
9. What is the correct relationship between main-agent continuation and remote
   execution?
10. Which execution resources require broad local mutation capability?
11. Which capabilities must remain outside the isolated environment?
12. What provider-neutral contract, if any, is actually needed?
13. How should failures during provisioning, execution, extraction, or
    retirement be represented?
14. What scheduling and cost-control semantics belong to a managed product
    rather than TURNLOCK Core?
15. What security model is needed for secrets, network access, and external
    services?
16. What deployment models should exist: SaaS, BYOC, self-hosted, or hybrid?
17. Which facts known by managed execution should be capturable for future run
    evaluation?
18. Which managed-execution capabilities, if any, ultimately belong to a future
    Turnlock Cloud product?
19. At what point should Turnlock Cloud receive its own repository and normative
    Product Intent?

No answer, product boundary, architecture, or implementation mechanism is
accepted by listing these questions.

## 17. Future promotion boundary

```text
future managed execution consideration
→ preserves opportunity and questions

TURNLOCK Product Intent
→ independently determines TURNLOCK Core requirements

future Turnlock Cloud Product Intent
→ must be separately established before becoming normative

explicit interface derivation
→ later determines the boundary
```

A capability useful only to a future cloud product cannot be smuggled into
TURNLOCK Core as though it were derived from current Product Intent. Any future
promotion requires the authority, derivation, and repository synchronization
appropriate to the product boundary being established.
