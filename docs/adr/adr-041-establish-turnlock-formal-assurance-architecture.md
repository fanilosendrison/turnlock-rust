---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Establish TURNLOCK formal assurance architecture"
id: "ADR-041"
status: "accepted"
date: "2026-09-19"
decision_body_sha256: "ac1ab0671ec5a7b204fac5a1406e4036943ca16edc6a6c785ab32cf9c3b2208c"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-015"
  supersedes: []
  confirms:
    - "ADR-040"
governs:
  - "Formal-assurance authority and trust chain"
  - "Canonical formal semantics and future Formal IR admission"
  - "Required assurance claims and verification obligations"
  - "Formal-semantic projection and verification-backend boundaries"
  - "Integrated formal semantics and focused verification restrictions"
  - "Hostile semantic-review assurance and evidence"
  - "Responsibility of formal/verification.yaml"
  - "Formal-discovery routing"
  - "Formal-readiness gates"
---

# ADR-041: Establish TURNLOCK formal assurance architecture

## Context

TURNLOCK has reached semantic closure far enough that executable formalization can
now be used to challenge the current semantic fixed point.

ADR-015 already established that normative prose remains product authority, that
formalization should begin early, that formal traceability must be
machine-readable, that focused checks do not replace integrated behavioral
exploration, and that successful checker execution evidence is distinct from
planned formal coverage.

Subsequent semantic work exposed a missing architectural layer in the original
direct shape:

```text
TL-INV
  ↓
planned TLA+ property
  ↓
TLC configuration
  ↓
TLC result
```

That shape conflates normative provenance, assurance decomposition, mathematical
semantics, backend-specific realization, semantic correspondence review,
verification configuration, and verification evidence.

TURNLOCK also requires the non-mechanical semantic boundaries in that chain to
be challenged adversarially rather than treated as implicit trust steps.

At the same time, ADR-040 requires future abstraction extractability without
prematurely introducing a generic TURNLOCK, software-problem-solving, or SCOPE
IR.

## Discovery classification

```text
decision-required, resolved
```

The current normative product semantics do not themselves determine how formal
assurance artifacts, formal semantic authority, hostile review, projections,
verification mechanisms, or readiness gates must be organized.

This ADR establishes that architecture without adding product behavior.

## Decision

### Product authority remains normative

TURNLOCK product meaning remains owned by:

```text
docs/specification/turnlock-spec.md
+
accepted TURNLOCK ADRs
```

A formal representation MAY become canonical for formal semantics in a declared
formalized domain, but MUST NOT thereby become normative product authority.

Formal models, assurance manifests, checkers, evidence records, Issues,
implementations, hostile reviewers, and harnesses MUST NOT resolve missing or
conflicting product semantics implicitly.

Authority flows downward through the assurance system. Discoveries may flow
upward, but authority does not.

### TURNLOCK requires canonical formal semantics

TURNLOCK SHALL maintain one canonical formal semantic representation for each
formally modeled semantic domain.

For the current operational state/transition domain, the initial canonical
formal representation SHALL be the integrated TLA+ semantics.

Conceptually:

```text
normative TURNLOCK semantics
          ↓
semantic formalization
          ↓
canonical formal semantics
(initially integrated TLA+)
```

`canonical` means the governed current formal-semantic baseline for the declared
domain and scope. It does not mean `normative`.

No distinct backend-neutral TURNLOCK Formal IR is introduced by this decision.

A future TURNLOCK-specific Formal IR requires a separate architectural decision
and is justified only when multiple current consumers require the same formal
semantics, or when a mechanically governed intermediate representation provides
a concrete assurance benefit greater than its additional translation,
projection, and common-mode trust surface.

Any such future IR MUST be derived from demonstrated TURNLOCK needs and
formalization pressure rather than from speculative generalization.

### Required assurance claims are a separate assurance layer

Normative invariants MUST NOT map directly to backend properties as the only
assurance decomposition.

TURNLOCK SHALL maintain stable required assurance claims.

A required assurance claim is the smallest evidentially coherent proposition
whose establishment is necessary to support a declared portion of accepted
TURNLOCK semantics.

Required assurance claims:

* record normative provenance;
* record assurance intent;
* may have more than one normative source;
* may divide one invariant into multiple evidentially distinct obligations;
* do not define TURNLOCK state variables, transitions, or execution semantics;
* do not form a second canonical formal-semantic IR.

Claims whose purpose exists only because of a particular formal modeling
representation are supporting model properties, not automatically required
assurance claims.

### Assurance modality is distinct from assurance domain

For behavioral formal assurance, the minimum logical modalities are:

```text
safety
reachability
liveness
```

Safety expresses universal preservation or exclusion.

Reachability expresses positive possibility, capability, representability, or
existence.

Liveness expresses eventual progression under an explicit premise.

Conformance, architecture, semantic quality, developer experience, coverage, and
semantic correspondence are separate assurance dimensions and MUST NOT be
encoded by growing a compound logical-modality enum.

### Verification mechanism selection is obligation-first

The required order is:

```text
required assurance claim
      ↓
verification obligation
      ↓
required assurance strength
      ↓
verification mechanism
```

Backend choice MUST NOT define the assurance obligation retroactively.

TLA+ is the initial canonical formal language for the current operational
state/transition domain.

TLC is the initial justified bounded model-checking mechanism for integrated
state-space exploration, safety, reachability, and liveness.

Additional checkers, deductive proof, Alloy, SMT, proof assistants,
model-based conformance, or other mechanisms require a concrete assurance need.

Multiple mechanisms over the same formal semantics provide checker diversity.

An independently authored formalization may provide semantic-interpretation
diversity.

Those assurance functions MUST NOT be conflated.

### Formalization is not projection

The relation:

```text
normative natural-language semantics
            ↓
formal representation
```

is semantic formalization.

A formal semantic projection exists only between formal semantic
representations.

Every formal semantic projection MUST declare:

* source representation;
* target representation;
* semantic domain;
* observations or claims for which preservation is asserted;
* assumptions;
* direction and limits of evidence transfer.

Projection soundness is claim-relative or observation-relative.

A global label such as `equivalent`, `over-approximation`, or
`under-approximation` MUST NOT be used beyond the observations for which the
relation is justified.

For safety, a sound over-approximation may support lifting absence-of-
counterexample evidence while producing spurious target counterexamples.

For positive reachability, a sound under-approximation may provide source-valid
witnesses while providing insufficient universal safety coverage.

Liveness requires an explicit preservation argument for the relevant infinite
behavior, enabledness, stuttering, occurrence, scheduler, and fairness semantics.
Projection direction alone does not establish liveness soundness.

The following relations are distinct:

```text
TL-INV → assurance claim
= assurance decomposition

normative semantics → canonical formal semantics
= formalization

canonical formal semantics → restricted checker configuration
= verification restriction / instantiation

formal representation → derived formal representation
= formal semantic projection

normative semantics → independently authored second formal model
= independent formalization

canonical repository state → generated documentation
= repository projection

formal model + configuration → checker result
= verification execution
```

Normative coverage, formal projection relation, finite checker bounds, and
evidence strength are orthogonal.

### Interacting operational semantics require integrated representation

All formally modeled TURNLOCK semantics whose meanings can interact within one
valid execution MUST be jointly representable and exercisable in at least one
coherent behavioral model.

The initial integrated TLA+ semantics is the integration backplane for the
operational domain.

Focused verification MAY restrict constants, initial states, domains, bounds,
selected properties, or mechanisms where the restriction preserves the relevant
meaning.

Focused verification MUST NOT redefine independent mini-semantics that can drift
from the integrated canonical semantics.

An integrated model MAY be physically modular. Integration is semantic, not a
requirement for one monolithic file.

Claims outside the behavioral state-machine domain may use other assurance
mechanisms but MUST remain connected through the common assurance graph.

The governing rule is:

```text
integrate everything that semantically composes;
connect everything else through explicit assurance relations
```

### Non-mechanical semantic boundaries require hostile review

A non-mechanically-proven semantic correspondence MUST NOT be treated as a
silent trust step.

Material semantic boundaries SHALL be subjected to explicit hostile review,
including where applicable:

```text
normative semantics → candidate canonical formal semantics
TL-INV → required assurance claims
required assurance claim ↔ backend property
formal projection preservation contract
verification-profile adequacy
evidence interpretation
```

The current hostile-review mechanism requires multiple independent frontier LLM
reviewers.

Review is adversarial falsification, not majority voting.

Reviewers must attempt to find:

* semantic strengthening;
* semantic weakening;
* omitted valid behavior;
* invented behavior;
* collapsed normative distinctions;
* invented formal distinctions;
* hidden assumptions;
* wrong quantification;
* wrong occurrence scope;
* modality mismatch;
* vacuity;
* incomplete assurance coverage;
* alternative incompatible interpretations still permitted by authority;
* cross-feature interaction failure;
* incorrect evidence lifting.

A material objection survives because its argument or counterexample survives
review, regardless of reviewer majority.

A valid minority objection blocks acceptance until it is resolved or refuted.

Hostile-review evidence MUST be durable and inspectable.

The evidence MUST identify the exact reviewed artifacts, reviewers/models,
review protocol, findings, dispositions, and re-review relationship.

Hostile review does not convert natural-language semantic correspondence into
mathematical proof.

The strongest valid conclusion is bounded reviewed semantic correspondence under
the executed review protocol.

### `formal/verification.yaml` owns the formal-assurance graph

`formal/verification.yaml` SHALL be the canonical machine-readable
formal-assurance and traceability graph.

It SHALL own:

* normative provenance;
* required assurance claims;
* assurance domains;
* behavioral modalities where applicable;
* formal coverage;
* residual assurance;
* formal-semantic domain bindings;
* required review classes;
* future backend realizations;
* required verification-profile relations;
* evidence contracts;
* reverse traceability.

It MUST NOT define:

* TURNLOCK product semantics;
* the canonical formal semantics themselves;
* a backend-neutral semantic IR;
* verification results;
* hostile-review results.

Facts mechanically derivable from repository artifacts or evidence SHOULD be
derived rather than independently maintained as mutable status.

In particular, existence of artifacts, binding resolution, current review
coverage, passing checker evidence, and current readiness state SHOULD be
derived where practical.

Coverage and current evidence state are distinct.

A partial formalization MUST retain explicit residual assurance rather than
allowing a checked subset to appear as complete invariant assurance.

The upper assurance graph MUST remain sufficiently backend-independent that a
future separately justified canonical Formal IR could replace TLA+ as the
canonical semantic source without replacing stable normative provenance or
required assurance claims.

### Discoveries route by earliest unresolved cause

A discovery is routed according to the earliest incorrect or underdetermined
link in the authority-and-assurance chain, not according to the tool that
detected it.

If current normative authority does not uniquely determine behavior that a lower
layer would have to choose, the discovery is `decision-required` and belongs to
Product Semantics.

If authoritative sources conflict or a derivation depends on an unstated
semantic assumption, the discovery is
`authority-conflict-or-uncertain`.

Formal Architecture, Formal Verification, hostile review, implementation, and
conformance mechanisms MUST NOT resolve those cases implicitly.

When normative authority is sufficient, the defect is corrected at the lowest
responsible downstream layer, including formalization, assurance decomposition,
claim/property correspondence, projection, verification configuration,
evidence integrity, implementation, or conformance.

A downstream repair MUST NOT close a finding while a surviving upstream cause
can still explain it.

A property established in a formal model does not become normative merely
because a checker establishes it.

Promotion into normative TURNLOCK meaning requires either complete derivation
from existing authority or an explicit Product Semantics decision.

### Formal readiness is staged

TURNLOCK SHALL distinguish three readiness gates.

#### Gate A — Formal-Architecture-Ready

Gate A authorizes creation of a candidate executable formal model.

It does not declare that model semantically correct, canonical, or verified.

Gate A requires:

* accepted formal-assurance architecture;
* valid assurance metamodel;
* assurance coverage for every current `TL-INV-*`;
* required claims and modalities for the candidate operational domain;
* explicit residual assurance for partial coverage;
* explicit assurance domains for non-formal obligations;
* explicit intended operational semantic scope;
* interaction closure or justified non-distorting exclusions;
* no unresolved product decision that the candidate model would otherwise have
  to choose;
* hostile-review protocol;
* discovery routing;
* repository integrity.

Gate A does not require checker evidence.

#### Gate B — Canonical-Formal-Semantics-Ready

Gate B promotes an exact candidate formal artifact/version to the current
canonical formal semantics for its declared scope.

Gate B requires:

* hostile semantic review of the exact candidate;
* strengthening/weakening/omission/invention attacks;
* alternative-interpretation attacks;
* compositional attacks;
* disposition of every material finding;
* re-review after material changes;
* no surviving unresolved material semantic finding;
* non-vacuity or semantic-adequacy witnesses for represented mechanisms.

Only Gate B authorizes the word `canonical` for that candidate revision.

`canonical` still does not mean `normative`.

#### Gate C — Formal-Verification-Ready

Gate C authorizes checker executions to support assurance claims.

Gate C requires:

* actual backend property bindings;
* hostile claim/property correspondence review;
* adequate verification profiles;
* modality-appropriate safety/reachability/liveness treatment;
* explicit assumptions and finite bounds;
* exact artifact identity;
* mechanism-specific evidence contracts;
* evidence-lifting rules bounded by correspondence, coverage, projection,
  assumptions, and run scope.

The following states MUST remain distinct:

```text
candidate model exists
        !=
candidate accepted as canonical formal semantics
        !=
backend property mechanically checked
        !=
required assurance claim supported
        !=
TL-INV fully assured
```

## Relationship to ADR-015

This ADR amends ADR-015.

ADR-015 remains authoritative for:

* normative prose remaining product authority;
* early formalization as discovery and verification pressure;
* stable invariant identity;
* machine-readable traceability;
* separation of intended coverage from executed evidence;
* retention of integrated exploration in addition to focused checks.

This ADR replaces ADR-015's overly direct effective assurance shape:

```text
TL-INV → TLA+ property → TLC configuration → TLC evidence
```

with an explicit architecture containing required assurance claims, canonical
formal semantics, hostile semantic review, typed evidence, and staged readiness.

ADR-015's historical body is not edited.

## Relationship to ADR-040

This ADR confirms ADR-040.

The initial canonical formal semantics is TURNLOCK-specific integrated TLA+.

No generic TURNLOCK IR, software-problem-solving IR, SCOPE IR, universal
problem graph, or universal cognition vocabulary is introduced.

A future abstraction must be earned from demonstrated recurring structure.

## Invariant consequence

No new `TL-INV-*` identity is introduced.

No existing invariant is amended.

This ADR introduces formal-assurance architecture only.

## Consequences

* Formal assurance becomes traceable independently from backend syntax.
* Required claims can be reviewed before executable backend identifiers exist.
* Modeling-support properties no longer acquire accidental normative status.
* Partial invariant coverage retains explicit residual obligations.
* Semantic correspondence becomes an evidence-bearing assurance activity.
* Checker evidence cannot silently stand in for semantic correspondence.
* TLA+ can initially act as canonical formal semantics without forcing a
  speculative intermediate IR.
* A future IR has a defined admission path.
* Focused verification remains subordinate to shared integrated semantics.
* Formal discoveries can challenge the normative fixed point without acquiring
  authority to rewrite it.
* Readiness to author, canonicalize, and verify are separately governable.

## Non-goals

This ADR does not:

* author an executable TLA+ model;
* run TLC;
* establish a successful formal-verification result;
* prove any invariant;
* define TLA+ state variables or actions;
* select future executable TLA+ property identifiers;
* define a TURNLOCK Formal IR;
* define a software-problem-solving IR;
* define SCOPE;
* define universal problem-solving primitives;
* define implementation APIs or runtime mechanisms;
* define a workflow DSL;
* define concrete harness mechanisms;
* turn finite model bounds into product limits;
* turn a fairness encoding into product semantics;
* treat hostile LLM review as mathematical proof.

## References

* `AGENTS.md`
* `docs/specification/turnlock-spec.md`
* `docs/adr/adr-015-evolve-the-normative-and-formal-specifications-together.md`
* `docs/adr/adr-040-preserve-future-abstraction-extractability-without-prematurely-generalizing-turnlock.md`
* `docs/repository-governance/turnlock-rust-discovery-classification.md`
* `formal/verification.yaml`
* Issue #27
