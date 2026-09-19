---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Preserve future abstraction extractability without prematurely generalizing TURNLOCK"
id: "ADR-040"
status: "accepted"
date: "2026-09-19"
decision_body_sha256: "1cc697edbed4e653fc950f9bd8a4a30879816dc01799f12ac3feb0415efc4e91"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms:
    - "ADR-003"
governs:
  - "Long-term abstraction trajectory from TURNLOCK toward software problem-solving and general problem-solving representations"
  - "Architectural treatment of potentially generalizable TURNLOCK concepts"
  - "Separation of TURNLOCK-specific semantics from future higher-level abstraction"
  - "Prohibition on premature genericization for future SCOPE reuse"
---

# ADR-040: Preserve future abstraction extractability without prematurely generalizing TURNLOCK

## Context

TURNLOCK is being developed as a concrete semantic system for executable,
agentic software-development workflows. Its current normative contract is
specific to TURNLOCK and intentionally preserves distinctions such as workflow-
owned orchestration, execution-form semantics, cognitive lineage, structured
continuation and return, composition admissibility, execution inspectability,
and execution-condition provenance.

The broader research goal extends beyond TURNLOCK. TURNLOCK is intended to be a
first rigorous concrete domain from which higher-level abstractions may later be
discovered. The intended long-term trajectory is:

```text
TURNLOCK
    ↓ extraction / abstraction
software problem-solving representation
    ↓ extraction / abstraction
SCOPE general problem-solving representation
```

The intermediate software problem-solving representation is intended to capture
structures that remain meaningful across software problem-solving methods rather
than only TURNLOCK execution. SCOPE is intended to explore the still more
general problem-solving structures that remain after software-specific
assumptions are removed.

This trajectory creates an architectural concern today: TURNLOCK work should not
accidentally entangle potentially reusable semantic dimensions with incidental
TURNLOCK-specific representation choices in a way that makes later extraction
unnecessarily difficult.

The opposite failure is equally serious. TURNLOCK must not be weakened,
distorted, or prematurely rewritten as a generic problem-solving framework in
anticipation of abstractions that have not yet been earned by multiple concrete
domains.

## Discovery classification

```text
decision-required, resolved
```

Current TURNLOCK authority does not require future extraction into a software
problem-solving representation or into SCOPE. The user has now selected that
long-term research direction as an architectural constraint.

This decision creates no new TURNLOCK product behavior. It governs how future
semantic representations, metamodels, IRs, architectural boundaries, and related
design work preserve the option to extract higher-level abstractions later.

## Decision

### TURNLOCK remains the concrete semantic authority for TURNLOCK

TURNLOCK SHALL continue to be specified in the terms required to state its own
product semantics precisely.

A concept MUST NOT be removed, weakened, merged, renamed into a less precise
generic concept, or otherwise distorted merely because a future software
problem-solving or SCOPE representation might prefer a broader abstraction.

The dependency direction is:

```text
concrete TURNLOCK semantics
        ↓
later observation of reusable structure
        ↓
later extracted higher-level abstraction
```

and not:

```text
speculative universal abstraction
        ↓
force TURNLOCK to fit it
```

### Preserve abstraction extractability

When future work introduces or changes semantic representations, metamodels,
IRs, ASTs, schemas, formal abstraction boundaries, or other architecture that
encodes TURNLOCK concepts, the design MUST preserve a clear path to distinguish:

```text
1. concepts intrinsically specific to TURNLOCK;
2. concepts that may generalize to software problem solving;
3. concepts that may generalize beyond software to general problem solving.
```

This is a classification lens for architecture and representation work. It is
not a requirement to decide those classifications conclusively before evidence
exists.

Where two designs preserve current TURNLOCK semantics equally well, prefer the
design that avoids unnecessary entanglement between TURNLOCK-specific
assumptions and semantic dimensions that may later be independently extracted.

This preference MUST NOT override correctness, semantic precision, accepted
TURNLOCK authority, or a simpler design that better expresses the current
contract.

### Generalization must be discovered, not assumed

Future higher-level abstractions SHOULD be extracted from demonstrated recurring
structure across sufficiently concrete domains.

TURNLOCK alone MUST NOT be treated as proof that a TURNLOCK concept is a
universal problem-solving primitive.

A future software problem-solving representation should therefore emerge by
examining which TURNLOCK distinctions remain necessary across broader software
problem-solving structures.

A future SCOPE representation should emerge by examining which structures remain
necessary after software-specific assumptions are removed and after additional
domains provide counterexamples or confirming structure.

Conceptually:

```text
concrete domain
    ↓
necessary distinctions
    ↓
formalization / counterexamples / use
    ↓
recurring structure across domains
    ↓
higher-level abstraction
```

### Do not create a speculative generic IR now

This decision does not authorize creation of a generic TURNLOCK IR, a software
problem-solving IR, a SCOPE IR, or universal problem-solving primitives.

No generic node vocabulary, universal cognitive-operation type, universal
authority model, generic problem graph, or similar abstraction may be introduced
into TURNLOCK merely because it might be useful to SCOPE later.

Any such artifact requires its own separately scoped work and sufficient evidence
for the abstraction it introduces.

### Preserve information needed for later abstraction work

Future architecture and representation choices SHOULD avoid gratuitously
collapsing semantically distinct TURNLOCK concepts when keeping those
distinctions explicit has reasonable cost.

The purpose is not to freeze all TURNLOCK details forever. It is to ensure that
later abstraction work can observe which distinctions were semantically
necessary rather than having to reconstruct them from an implementation-specific
encoding that erased them.

### Higher-level representations do not become TURNLOCK authority

If a software problem-solving representation or SCOPE representation is later
introduced, it does not automatically become normative authority for TURNLOCK.

TURNLOCK product semantics remain governed by the TURNLOCK specification and
accepted TURNLOCK decisions unless a later explicit governance decision changes
that authority structure.

A higher-level representation may provide vocabulary, metamodel structure,
analysis, projections, or reusable abstractions while TURNLOCK-specific
constraints continue to define TURNLOCK meaning.

Conceptually:

```text
higher-level reusable vocabulary / metamodel
                    +
TURNLOCK-specific constraints and semantics
                    =
TURNLOCK meaning
```

This diagram is illustrative and does not select a future IR architecture.

### Relationship to formal verification

Formalization is a discovery instrument as well as a verification instrument.

Counterexamples, modeling pressure, and distinctions required to state or verify
TURNLOCK properties may provide evidence about which concepts are fundamental
and which are accidental.

That evidence MAY inform later abstraction work.

TLA+, TLC, another verifier, or a modeling convenience MUST NOT promote a
TURNLOCK-specific modeling structure into a software-general or
problem-solving-general abstraction by itself.

### Relationship to SCOPE

The long-term research direction is explicitly:

```text
TURNLOCK
→ evidence about structured agentic execution
→ broader software problem-solving representation
→ evidence across broader problem-solving domains
→ SCOPE general problem-solving representation
```

This direction records an intended abstraction path, not an assertion that the
future intermediate representations, their primitives, or their exact
relationships are already known.

## Invariant consequence

No new `TL-INV-*` identity is introduced.

No existing TURNLOCK invariant is amended.

This decision governs architectural and representation discipline around future
generalization. It does not add a universal workflow-semantic obligation.

## Formal-traceability consequence

`formal/verification.yaml` requires no change from this ADR.

No TLA+ property, state variable, action, fairness condition, model,
configuration, or verification claim is introduced.

The generalization-preservation rule is an architectural review constraint, not
a TLC property.

## Consequences

- TURNLOCK remains free to use precise domain-specific concepts where its
  semantics require them.
- Future representation work must avoid unnecessary coupling that would make
  potentially reusable semantic dimensions inseparable from TURNLOCK-specific
  accidents.
- Future agents and architects must explicitly consider whether a concept is
  TURNLOCK-specific, software-problem-solving-level, or potentially
  problem-solving-general when that distinction is relevant to representation
  design.
- No conclusion that a concept generalizes is accepted merely because it appears
  in TURNLOCK.
- Formal verification and concrete use may supply evidence for later abstraction
  work without becoming semantic authority for higher-level IRs.
- A future software problem-solving IR and SCOPE IR remain separate future
  artifacts requiring their own evidence, scope, and governance.

## Non-goals

This ADR does not:

- define the software problem-solving IR;
- define the SCOPE IR;
- define universal problem-solving primitives;
- create a new TURNLOCK workflow primitive;
- generalize the current TURNLOCK product contract beyond coding-agent sessions;
- move software methodology, planning, evaluation, or optimization into TURNLOCK
  core;
- require TURNLOCK artifacts to be losslessly reconstructible from a future
  higher-level representation;
- require one shared physical schema or AST across TURNLOCK, software problem
  solving, and SCOPE;
- decide whether future abstractions use inheritance, profiles, projections,
  compilation, lowering, interpretation, graph transformation, or another
  relationship;
- change the authority of `docs/specification/turnlock-spec.md`;
- change any current formal-verification claim;
- authorize speculative implementation work.

## References

- `AGENTS.md`
- `docs/vision/turnlock-vision.md`
- `docs/specification/turnlock-spec.md`
- `docs/adr/adr-003-make-product-intent-and-derived-invariants-govern-implementation.md`
- `docs/adr/adr-015-evolve-the-normative-and-formal-specifications-together.md`
- `docs/adr/adr-038-assume-native-harness-workflow-convergence.md`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
