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
> - **Normative baseline:** Minimum completed-execution inspectability is accepted
>   by ADR-018; ADR-024 requires effective execution-condition provenance for
>   conditions TURNLOCK selects, binds, explicitly supplies, or resolves;
>   ADR-025 clarifies that protected values need not be disclosed but
>   TURNLOCK-known condition-specific provenance cannot be substituted away
>   before or during the required boundary capture opportunity; and ADR-019 keeps evaluation and optimization policy outside
>   TURNLOCK core
> - **Creates TURNLOCK semantics:** No
> - **Creates invariants:** No
>
> This note preserves an exploratory design space beyond that accepted minimum.
> It does not amend the
> [TURNLOCK specification](../specification/turnlock-spec.md), record an accepted
> [architecture decision](../adr/README.md), define formal-verification intent,
> or provide execution evidence. If it conflicts with any authoritative source,
> this note yields.

## 1. Purpose and classification

ADR-018 and `TL-INV-033` require minimum inspectability of completed execution
at TURNLOCK's semantic boundary. ADR-024 and `TL-INV-036` additionally require
effective execution conditions that TURNLOCK selects, binds, explicitly
supplies, or resolves to remain attributable to the execution scopes they govern
and exposable or capturable at that boundary. ADR-025 clarifies that exact-value
disclosure is not universal, while protection cannot substitute away
condition-specific provenance TURNLOCK knew before or during the required
boundary capture opportunity. Detailed tracing, event schemas,
retention, storage, telemetry, replay, cross-run identity or equality,
comparison, reproducibility, execution proofs, debugger UI, evaluation APIs,
metrics, and automatic optimization remain open. This note prevents that stronger design space from
being lost without promoting it into the product contract.

Preserving this exploration is classified as `no-normative-impact` in the
`repository-governance-or-documentation` layer. Any proposal to require a run
model, event contract, stable identifier, comparison profile, replay behavior,
or execution proof would be a separate `decision-required` discovery unless it
were independently derived from accepted product intent.

No such stronger decision is made here. ADR-019 fixes the boundary ADR-018
reserved: TURNLOCK core remains the execution substrate and does not own
evaluation or optimization policy. Evaluation objectives and refinement
decisions belong to an explicitly responsible user, coding agent, evaluator,
higher-level system, or ordinary authored workflow. A future native evaluation
or optimization facility would require its own accepted decision; it is not
part of the current core product contract.

```text
current TURNLOCK core
  = execution semantics
  + accepted inspectability semantics
  + effective execution-condition provenance floor

evaluation / optimization policy
  = ordinary workflow / user / higher-level-system concern

future native evaluation facilities
  = require new accepted authority
```

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

### 3.2 Execution inspectability and stronger run observability

The accepted minimum requires enough actual TURNLOCK-visible behavior to remain
inspectable after completion for external understanding and evaluation. It does
not enumerate a universal event set. A stronger future observability layer might
standardize facts such as:

```text
workflow invocation
region activation
region entry
outcome
handoff
completion
termination
```

Standardizing or retaining such events would not promise that two invocations
with apparently identical inputs produce the same results. It would also remain
distinct from:

- harness conformance evidence;
- repository validation output;
- TLC result evidence under `formal/results/`;
- proof that an implementation satisfies every TURNLOCK invariant.

The concrete event set, retention model, ordering guarantees, and any
observation boundary inside agentic regions beyond explicitly exposed results
and progression-relevant TURNLOCK-visible facts remain undecided.

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

ADR-024 makes TURNLOCK-known effective conditions available at the semantic
boundary when TURNLOCK selects, binds, explicitly supplies, or resolves them.
ADR-025 prevents protection from substituting away condition-specific
provenance TURNLOCK possessed before or during the boundary capture opportunity, but it provides no public or cross-run stable
identity and no equality or difference evidence. Neither decision defines which
conditions matter to property `P`, extends the universal floor to every observed
or externally exposable condition, or decides whether available evidence
establishes comparability.

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
    = stronger observability / comparability / reproducibility constraints

specialized workflow classes
    = potentially YADA-core-like highly evaluable workflows
```

This is not an accepted architecture. TURNLOCK is not currently declared to
replace, subsume, or provide all properties of YADA-core. ADR-019 assigns
evaluation and optimization policy outside the current TURNLOCK core product
contract, while leaving possible future TURNLOCK-adjacent tooling to a new
accepted decision. The note does not decide that comparison, reproducibility,
or evidence must always remain outside TURNLOCK's scope, and any later boundary
change requires its own authority and derivation.

A RAG pipeline could eventually be one specialized workflow class that opts
into stronger evaluation guarantees. That possibility creates no generic
requirement beyond the accepted minimum completed-execution inspectability and
effective execution-condition provenance obligations.

## 5. Forward-compatibility observations

The accepted minimums require sufficient boundary-level execution truth and
attribution of effective conditions TURNLOCK selects, binds, explicitly
supplies, or resolves. They do not uniquely require any abstraction in the
following list. These abstractions might be selected for independent reasons
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

This overlap remains a forward-compatibility observation. ADR-024 requires the
semantic attribution itself, and ADR-025 requires a condition-specific
representation when a known value is protected without choosing any listed
abstraction. The representation need not reveal the value and establishes no
public or cross-run stable identity, equality or difference evidence, or
comparison sufficiency. The list does not establish that any abstraction is
required, externally visible, stable, persistent, globally unique, or suitable
for cross-run comparison.

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

Conversely, required minimum inspectability does not prevent TURNLOCK from
later offering stronger evaluation guarantees. Computational determinism,
output determinism, run reproducibility, stronger observability profiles, and
comparison profiles remain orthogonal questions unless future authority
connects them.

## 7. Open questions

The following questions are intentionally unanswered:

1. Should TURNLOCK ever expose a standard `run` model?
2. Which concrete control events, if any, should standardize or extend the
   accepted minimum inspectability surface?
3. Is a stable workflow definition or revision identity necessary?
4. What should be observed inside an agentic region, if anything beyond
   explicitly exposed results and progression-relevant boundary facts?
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
12. Which conditions TURNLOCK observes but does not control, or an adapter or
    execution resource could expose, should receive stronger provenance duties?
13. What privacy, security, retention, and cost constraints would apply to any
    future event or evidence capture?

Listing these questions does not accept any answer, scope boundary, data model,
or implementation mechanism.
