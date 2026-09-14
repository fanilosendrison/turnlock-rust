---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "future-consideration"
domain: "turnlock-rust"
severity: "informational"
name: "Future workflow run-evaluation design space"
---

# Future workflow run-evaluation design space

> - **Status:** Non-normative future consideration
> - **Authority:** None
> - **Accepted product decision:** No
> - **Creates TURNLOCK semantics:** No
> - **Creates invariants:** No
>
> This note preserves an exploratory design space. It does not amend the
> [TURNLOCK specification](../specification/turnlock-spec.md), record an accepted
> [architecture decision](../adr/README.md), define formal-verification intent,
> or provide execution evidence. If it conflicts with any authoritative source,
> this note yields.

## 1. Purpose and classification

The repository currently leaves observability, tracing, replay, and debugging
open. This note prevents a related line of reasoning from being lost without
promoting it into the product contract.

Preserving this exploration is classified as `no-normative-impact` in the
`repository-governance-or-documentation` layer. Any proposal to require a run
model, event contract, stable identifier, comparison profile, replay behavior,
or execution proof would be a separate `decision-required` discovery unless it
were independently derived from accepted product intent.

No such decision is made here.

## 2. Motivation

TURNLOCK makes orchestration explicit across distinct execution forms:

```text
mechanical regions
raw LLM regions
independent-agent regions
main-agent regions
```

It also distinguishes local execution authority, global workflow-owned control,
and explicit handoff boundaries. That structure could eventually make workflow
executions easier to:

```text
observe
compare
experiment with
optimize
```

A retrieval-augmented generation pipeline is one plausible specialized workflow:

```text
query
→ retrieval
→ reranking
→ context construction
→ LLM
→ validation
→ declared retry / fallback
→ result
```

Prior systems discussed as YADA-core / Implicit-Free Execution are a conceptual
precedent for this exploration. They suggest that evaluating and optimizing runs
can require explicit treatment of:

- the identity of what was executed;
- traceability;
- comparison across runs;
- identification of evaluation-relevant determinants;
- levels of reproducibility;
- potentially, independently verifiable execution evidence.

YADA-core is a source of inspiration only. It has no authority over TURNLOCK,
and none of its properties becomes a TURNLOCK obligation by appearing in this
note.

## 3. Separate layers in the design space

The layers below are deliberately separated. They are not one implied package,
and the existence of a lower layer does not accept the higher layers.

### 3.1 Core orchestration correctness

The layer closest to current TURNLOCK concerns whether control transitions,
region boundaries, and handoffs respect the workflow semantics that authorize
them.

Conceptually, an assessment might ask whether:

```text
a region activated through a permitted transition
local authority remained inside its declared boundary
a handoff returned to its authorized continuation
termination returned to the immediate caller
```

The normative meaning of those questions belongs to the specification and
accepted ADRs, not to this note. Orchestration correctness does not imply
computational determinism, identical outputs, one path, one schedule, or one
trace.

### 3.2 Run observability

A future observability layer might make selected execution facts reconstructible,
for example:

```text
workflow invocation
region activation
region entry
outcome
handoff
completion
termination
```

Observing such events would not promise that two invocations with apparently
identical inputs produce the same results. It would also remain distinct from:

- harness conformance evidence;
- repository validation output;
- TLC result evidence under `formal/results/`;
- proof that an implementation satisfies every TURNLOCK invariant.

The event set, retention model, ordering guarantees, and observation boundary
inside agentic regions remain undecided.

### 3.3 Run comparability

A future comparison layer might answer a property-relative question:

```text
Are R1 and R2 comparable for property P?
```

Comparability should not be presumed to mean global equality between runs. Its
requirements could depend on the evaluation property and on explicitly selected
determinants such as:

```text
workflow definition / revision
inputs
model or execution-resource configuration
relevant environment
policies and other configuration
```

Different properties may require different determinants. Two runs could be
comparable for control-path conformance while not being comparable for output
quality, latency, cost, retrieval quality, or model behavior.

This note does not define the determinant set, a canonical run description, or
a comparison algorithm.

### 3.4 Reproducibility and evidence profiles

An optional future profile could explore stronger, separately stated guarantees,
such as:

```text
same control structure
same selected workflow definition
same selected mechanical operations
same configuration
selected output reproducibility
independently verifiable execution evidence
```

These are different guarantees and need not form a single Boolean property.
Reproducing a control structure is not the same as reproducing an LLM output;
recording execution evidence is not the same as proving semantic correctness.

No reproducibility, replay, comparison, or run-proof guarantee is part of the
TURNLOCK core as a consequence of this note.

## 4. Architectural hypothesis, not accepted architecture

The design hypothesis worth retaining is:

```text
TURNLOCK core
    = generic explicit workflow / control semantics

optional future evaluation profiles
    = observability / comparability / reproducibility constraints

specialized workflow classes
    = potentially YADA-core-like highly evaluable workflows
```

This is not an accepted architecture. TURNLOCK is not currently declared to
replace, subsume, or provide all properties of YADA-core. The note also does not
decide that evaluation, comparison, reproducibility, or evidence must always
remain outside TURNLOCK's scope. Any later boundary requires its own authority
and derivation.

A RAG pipeline could eventually be one specialized workflow class that opts
into stronger evaluation guarantees. That possibility creates no requirement
for generic TURNLOCK workflows today.

## 5. Forward-compatibility observations

Several abstractions might be required by TURNLOCK core for independent reasons
and could also become useful to future run evaluation:

```text
workflow invocation identity
region identity
activation identity
region boundaries
handoff identity or events
completion events
workflow definition or revision identity
```

This overlap is only a forward-compatibility observation. It does not establish
that any listed abstraction is already required, externally visible, stable,
persistent, globally unique, or suitable for cross-run comparison.

In particular, the core must not gain any of the following solely to prepare for
this design space:

```text
hash-based identities
canonical RunSpec
persistent event logs
RunProof
mandatory metrics
replay guarantees
cross-run comparability guarantees
```

Such an obligation would require either an independent derivation from current
product intent or an explicit future product decision. A TLA+ modeling device,
implementation convenience, provider capability, or idea imported from
YADA-core / Implicit-Free Execution would not supply that authority.

## 6. Separation from deterministic-control clarification

The clarification tracked by Issue #7 is independent of this exploration.
Mechanical execution is non-agent-mediated execution; it may still be
probabilistic, nondeterministic, externally dependent, or event-driven.
Workflow-owned control constrains global progression to workflow-authorized
possibilities; it does not promise one output, path, schedule, or trace.

Nothing in that clarification implies:

```text
mechanical execution must be reproducible
workflow runs must be comparable
workflow definitions must be content-addressed
every activation must be persisted
every run must produce a proof
external operations must be replayable
```

Conversely, current core orchestration semantics do not imply that TURNLOCK can
never offer stronger evaluation guarantees. Computational determinism, output
determinism, run reproducibility, observability profiles, and comparison
profiles remain orthogonal questions unless future authority connects them.

## 7. Open questions

The following questions are intentionally unanswered:

1. Should TURNLOCK ever expose a standard `run` model?
2. Which control events, if any, should be observable?
3. Is a stable workflow definition or revision identity necessary?
4. What should be observed inside an agentic region, if anything beyond its
   boundaries?
5. Should comparability be an optional profile?
6. Should reproducibility be expressed in levels rather than as a Boolean?
7. Can agentic workflows be evaluated usefully without attempting to reproduce
   their outputs?
8. Which YADA-core properties are generic to any evaluated workflow?
9. Which properties are needed only for YADA-core's RAG, auditability,
   experimentation, or proof objectives?
10. How would evaluation evidence remain distinct from formal model-checking
    evidence and implementation conformance evidence?
11. Which determinants matter for a particular comparison property, and who
    declares them?
12. What privacy, security, retention, and cost constraints would apply to any
    future event or evidence capture?

Listing these questions does not accept any answer, scope boundary, data model,
or implementation mechanism.
