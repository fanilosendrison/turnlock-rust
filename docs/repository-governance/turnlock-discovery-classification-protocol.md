---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "TURNLOCK Discovery Classification Protocol"
---

# TURNLOCK Discovery Classification Protocol

## Purpose

Apply this protocol when handling discoveries during specification, formal
modeling, implementation, review, model checking, testing, and LLM-assisted
analysis.

Use it to prevent accidental specification drift.

A discovery MUST NOT become a normative invariant, semantic rule, ADR decision,
or product requirement merely because it:

- appears necessary in a TLA+ model;
- is suggested by TLC;
- is convenient for implementation;
- is proposed by an LLM;
- makes the architecture cleaner;
- prevents a particular implementation bug;
- or appears intuitively desirable.

Classify every discovery according to this protocol before incorporating it.

### Protocol authority

Treat this protocol as procedural authority for classifying material
engineering, review, and formalization discoveries. It creates no product
semantics, accepted decision, or formal-verification evidence.

Apply it together with the [repository directives](../../AGENTS.md). Normative
product meaning, including accepted product intent and `TL-INV-*` invariants,
remains in the [TURNLOCK specification](../specification/turnlock-spec.md).
Accepted ADRs remain the decision history and amendment mechanism. Formal
artifacts retain only the authority assigned to them by the repository
directives.

Classification does not itself authorize a repository change or bypass existing
permission, ADR lifecycle, stable invariant identity, synchronization,
traceability, or validation requirements.

## 1. Scope

This protocol applies to discoveries originating from any source, including:

- TLC counterexamples;
- TLA+ modeling difficulties;
- TLA+ state-space exploration;
- LLM analysis;
- coding-agent reasoning;
- implementation work;
- code review;
- tests;
- harness integration;
- architectural analysis;
- manual specification review;
- contradictions discovered between existing documents.

It applies before modifying any of the following normative or semantically
significant surfaces:

- product intent;
- normative specification;
- `TL-INV-*` invariants;
- accepted ADRs;
- formal verification mappings;
- TURNLOCK abstract semantics;
- harness conformance requirements.

## 2. Mandatory classification

Classify every material discovery as exactly one primary category before
incorporating it into the project.

### A — Derived semantic requirement

The discovery follows necessarily from already accepted product intent,
normative semantics, or invariants.

It introduces no genuinely new product decision.

Examples:

> An active workflow invocation must not silently change topology because its
> source artifact was edited during execution.

This is category A if stable workflow-owned control flow is already required.

Or:

> A nested workflow must return to its immediate caller rather than an arbitrary
> outer continuation.

This is category A if structured nested invocation is already normative.

#### Required action

A discovery classified as **A** MAY become a new invariant or normative
clarification.

Before doing so, provide a derivation chain.

Required form:

```text
Discovery:
<statement>

Classification:
A — Derived semantic requirement

Derived from:
- <product intent / invariant / ADR>
- <product intent / invariant / ADR>

Derivation:
1. ...
2. ...
3. ...

Why this adds no new product choice:
...

Failure if omitted:
<counterexample or semantic inconsistency>
```

If the derivation depends on an unstated assumption, classification A is
invalid.

### B — New product or semantic decision

The discovery identifies a question that the existing product intent does not
uniquely answer.

Multiple behaviors remain consistent with the accepted specification.

Examples:

- whether workflow edits become visible to already-running invocations;
- whether cancellation propagates into nested workflows;
- what exactly constitutes completion of a main-agent region;
- whether a main-agent continuation may execute concurrently with another
  main-agent continuation.

#### Required action

A discovery classified as **B** MUST NOT be silently turned into an invariant.

It MUST instead become:

1. an explicit open semantic question;
2. an analysis of viable alternatives;
3. a product or semantic decision;
4. normally an ADR if the decision is architecturally significant;
5. only then, if appropriate, one or more derived invariants.

Until that decision is accepted, the formal model MUST either:

- abstract over the alternatives;
- exclude the undecided behavior explicitly;
- or document the modeling assumption as non-normative.

The model MUST NOT choose the product behavior merely because TLC requires a
concrete transition.

### C — Formal modeling choice

The discovery concerns how accepted semantics are represented in TLA+ or
another formal model.

Examples:

- representing nested workflows using a sequence rather than a tree;
- introducing an `activationId` to express fairness;
- storing derived state instead of recomputing it;
- bounding the model to three workflow instances for model checking;
- representing agent cognition using an opaque value.

#### Required action

A discovery classified as **C** belongs to the formal model and its
documentation.

It MUST NOT become a normative TURNLOCK requirement unless an independent
derivation establishes that it belongs to category A or a new decision moves it
through category B.

Example:

```text
TLA+ requires activation identities to express per-region fairness.
```

does NOT imply:

```text
TURNLOCK implementations must expose UUID activation identifiers.
```

The former may be a modeling device only.

### D — Implementation or architectural mechanism

The discovery concerns one possible mechanism for satisfying accepted
semantics.

Examples:

- SHA-256 workflow definition identifiers;
- Rust enums;
- channels;
- mutexes;
- SQLite persistence;
- an RPC named `complete_region`;
- filesystem snapshots;
- Tokio tasks;
- process boundaries.

#### Required action

A discovery classified as **D** MUST NOT modify the normative semantic
specification.

It may belong in:

- implementation plans;
- architecture documents;
- implementation-specific ADRs;
- source code;
- tests.

A mechanism may only become normative if the product genuinely requires that
exact mechanism. Such promotion requires reclassification through B and an
explicit later ADR.

### E — Harness or adapter conformance requirement

The discovery concerns whether a particular execution environment can realize
already-defined TURNLOCK semantics.

Examples:

- whether Pi can preserve main-agent cognitive lineage;
- whether Claude Code exposes the required continuation primitive;
- whether a harness can implement a specific interaction boundary;
- whether an adapter must reject an unsupported execution form.

#### Required action

A discovery classified as **E** belongs to the conformance layer.

It may produce:

- harness capability requirements;
- support tiers;
- adapter constraints;
- conformance tests;
- unsupported-feature behavior.

It MUST NOT silently redefine TURNLOCK semantics to accommodate a weaker
harness.

When the harness cannot satisfy the required semantics, prefer:

```text
unsupported primitive
partial/weaker support tier
explicit conformance failure
```

over weakening the normative invariant.

## 3. Normative promotion rule

Only category **A** discoveries may be promoted directly into normative
invariants.

Category **B** discoveries require an explicit semantic or product decision
first.

Categories **C**, **D**, and **E** MUST remain in their respective layers unless
independently promoted through the classification process.

Here, direct promotion means only that no new product choice is required. It
does not bypass repository permission, accepted-ADR amendment rules, stable
invariant identity, normative and formal synchronization, traceability, review,
or validation.

The following transformation is forbidden:

```text
TLC needs X
therefore TURNLOCK requires X
```

The valid reasoning is:

```text
TLC exposes ambiguity/problem X
        ↓
classify X
        ↓
derive from existing intent?
        │
        ├─ yes → A → invariant/clarification
        │
        └─ no
             ↓
        genuine semantic choice?
             │
             ├─ yes → B → decision/ADR
             └─ no → C/D/E
```

## 4. Counterexamples are evidence, not decisions

A TLC counterexample demonstrates that the current formal model admits a
behavior.

It does NOT by itself establish that the behavior violates TURNLOCK.

For every counterexample, distinguish:

```text
1. Is the behavior forbidden by existing normative semantics?

2. Is the model missing an already-required constraint?

3. Does the counterexample expose an ambiguity in the specification?

4. Is the counterexample only an artifact of the abstraction?

5. Is the behavior actually valid TURNLOCK behavior?
```

Only case 1 or 2 can normally produce an A-class discovery.

Case 3 is B.

Case 4 is C.

Case 5 requires fixing the property or model rather than strengthening the
product specification.

## 5. Formalization difficulties are not semantic requirements

If TLA+ cannot express or verify a property conveniently without introducing
additional structure, initially presume the additional structure to be category
C.

Example:

```text
To express fairness for a particular active main-agent region,
the model needs a stable activation identity.
```

Default classification:

```text
C — Formal modeling choice
```

It is forbidden to infer without further justification:

```text
All TURNLOCK implementations must use persistent activation IDs.
```

## 6. Implementation pressure must not redefine semantics

During implementation, an agent may discover that the easiest implementation
would change or weaken an accepted invariant.

The agent MUST NOT perform that change silently.

It must report:

```text
Existing semantic requirement:
...

Implementation pressure:
...

Why the current implementation mechanism conflicts with it:
...

Classification:
D or E

Possible mechanisms that preserve the semantics:
...

If none are currently known:
report the D- or E-class capability limitation or conformance failure.
If changing product semantics is proposed, raise that proposed amendment as a
separate B-class question rather than changing the invariant.
```

## 7. Required discovery record

For every discovery capable of changing normative behavior, produce a short
discovery record before editing normative artifacts.

Minimum format:

```markdown
## Discovery

### Statement
...

### Source
TLC | TLA+ modeling | LLM analysis | implementation | review | test | other

### Classification
A | B | C | D | E

### Existing authority
Relevant product intent / TL-INV / ADR / spec sections.

### Reasoning
Why this classification is correct.

### Normative impact
none | clarification | new invariant candidate | ADR required | conformance-only

### Formal impact
none | model change | property change | fairness assumption | scenario/config change

### Implementation impact
...

### Next action
...
```

For trivial discoveries with no semantic impact, this record may remain in the
agent's working notes.

For any discovery causing a normative repository change, preserve the reasoning
in the resulting commit, ADR, Issue, review note, or associated documentation.

## 8. Invariant admission test

Before creating a new `TL-INV-*`, answer all of the following:

```text
1. What accepted product intent does this invariant protect?

2. Can the invariant be derived without assuming a specific
   implementation mechanism?

3. Would two independent implementations of TURNLOCK still need
   to satisfy it?

4. Does violating it produce behavior that contradicts accepted
   TURNLOCK semantics?

5. Is it stronger than necessary?

6. Is it already implied by an existing invariant?

7. Is this actually a product decision that still requires an ADR?

8. Is this instead a modeling, implementation, or harness concern?
```

If questions 1–4 cannot be answered convincingly, the invariant MUST NOT be
added.

If question 5 is yes, weaken it to the minimum semantic requirement.

If question 6 is yes, prefer clarifying the existing invariant or its
formalization rather than creating redundant normative surface.

If question 7 is yes, classify B.

If question 8 is yes, classify C, D, or E.

## 9. Minimum semantic requirement principle

When a new requirement is genuinely derived, state the weakest requirement
sufficient to preserve the product intent.

If an accepted product decision establishes stable definition binding for
active invocations, prefer:

```text
An active invocation remains bound to a stable workflow definition.
```

over:

```text
The workflow definition must be identified by SHA-256.
```

This example is hypothetical until the underlying B-class visibility question
has been decided.

Prefer:

```text
A main-agent region has an explicit completion boundary.
```

over:

```text
The main agent must call complete_region().
```

Prefer:

```text
Nested completion returns to the immediate caller.
```

over:

```text
Nested workflows must be implemented using a Rust Vec stack.
```

Normative semantics define observable obligations.

Mechanisms remain replaceable.

## 10. LLM behavior

When acting as a reviewing or coding LLM, do not optimize for producing more
invariants.

Optimize for:

- identifying ambiguities;
- finding contradictions;
- finding missing consequences of existing intent;
- detecting accidental assumptions;
- finding composition failures;
- distinguishing semantics from mechanisms.

When proposing a new invariant, state its classification and derivation first.

The phrase:

```text
we should add an invariant that...
```

is insufficient without this analysis.

## 11. TLA+ and TLC behavior

TLA+ and TLC are discovery instruments, not normative authorities.

When TLC produces a counterexample:

1. preserve the counterexample;
2. identify the violated formal property;
3. map that property to its intended normative authority;
4. determine whether the model, property, or normative specification is wrong or
   incomplete;
5. classify the discovery A–E;
6. only then modify normative artifacts.

Do not strengthen the model merely to make TLC pass.

A passing model is not a goal if it verifies semantics TURNLOCK never intended.

## 12. Conflict rule

When layers disagree, do not silently reconcile them.

Report the conflict explicitly.

For classifying layers and dependency direction, use:

```text
normative TURNLOCK specification
  = accepted product intent + accepted normative semantics / invariants
        ↕
accepted ADR decision history and explicit amendments
        ↓
formal model
        ↓
implementation architecture
        ↓
specific implementation
        ↓
harness adapter
```

The specification is the consolidated normative product contract. Accepted ADRs
record the decisions that produced it and the explicit amendments that change
it. A contradiction between those semantic sources MUST be reported and
resolved through a new ADR plus synchronized normative and formal artifacts;
it MUST NOT be settled by silently selecting one side of the diagram.

The dependency direction does not mean higher layers contain more detail.

It means lower layers MUST implement or model higher-layer semantics without
silently redefining them.

A contradiction between layers is a discovery requiring classification.

## 13. Stop condition

Stop normative modification and surface the issue when:

- classification between A and B is uncertain;
- a derivation requires an unstated product assumption;
- two accepted invariants imply incompatible behavior;
- a TLC counterexample could plausibly represent valid behavior;
- implementation feasibility appears to require weakening semantics;
- a harness cannot preserve a product-defining invariant.

Do not resolve such cases by convenience.

Make the uncertainty explicit.

## Core rule

> A discovery is not a requirement.
>
> A counterexample is not a product decision.
>
> A useful implementation mechanism is not an invariant.
>
> A formal modeling necessity is not an implementation obligation.
>
> A harness limitation is not permission to weaken TURNLOCK.

Every normative addition must be traceable either to already accepted product
intent in the normative specification or to an explicit new product decision.
