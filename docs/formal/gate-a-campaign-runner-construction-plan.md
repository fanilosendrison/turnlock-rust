# Gate A campaign runner construction plan

## Status and authority

This document is a non-authoritative construction map for the Gate A hostile-review campaign runner.

It does not define TURNLOCK product semantics, formal semantics, hostile-review protocol semantics, review evidence, verification evidence, or live engineering work state.

The governing technical sources remain the normative specification, accepted ADRs, `formal/verification.yaml`, and the content-addressed hostile-review protocol and evidence contracts under `formal/reviews/`.

GitHub Issues, native GitHub relationships, and Turnlock-Rust Engineering Project fields own live work existence, dependency, workflow state, lifecycle classification, and scheduling priority. This document must not be maintained as a manual work-status dashboard.

The campaign runner construction process may use workspace operational mechanisms such as Normative Implementation Briefs, Dependency Contracts, hostile construction-document review, engineering-discovery classification, implementation-quality review, sanctioned Git publication, and local credential resolution. Those mechanisms govern construction only. They do not become TURNLOCK runtime dependencies, Gate A review inputs, protocol identity, or formal-assurance authority.

## Objective

Construct one campaign runner that mechanically executes the accepted Gate A hostile-review protocol over an exact semantic subject and protocol identity, preserves all required evidence and challenge bindings, minimizes human intervention, and exposes only the externally authorized campaign outcomes.

The construction itself must not create TURNLOCK semantics or decide unresolved product questions.

## Responsibility split

Architecture and construction specification are completed before mechanical execution.

The architect owns:

- implementation architecture;
- NIB-S;
- NIB-M briefs;
- Dependency Contracts;
- NIB-T;
- module and type boundaries;
- algorithms and branch behavior;
- test vectors and anti-cheat properties;
- material-discovery classification;
- hostile-review interpretation and adjudication;
- exact implementation instructions;
- any required durable ADR.

The coding agent owns only mechanical execution of already-closed instructions.

If an implementing agent encounters an uncovered decision, ambiguity, contradiction, missing contract, or repository state incompatible with its instructions, it stops and reports the factual condition. It does not choose a solution.

## Construction methodology

The runner follows the workspace NIB construction methodology:

```text
CONCEPTION
    ↓
NIB-S
    ↓
NIB-M
    ↓
Dependency Contracts
    ↓
NIB-T
    ↓
hostile review of the complete construction pack
    ↓
CONSTRUCTION
    ↓
RED
    ↓
GREEN
    ↓
TRANSITION
    ↓
EVOLUTION
```

Production implementation does not begin before the construction pack is sufficiently complete and hostile-reviewed.

The System Brief selected for this construction is
[`nib-s-gate-a-campaign-runner.md`](nib-s-gate-a-campaign-runner.md).
Its own NIB metadata owns its construction lifecycle status; this plan does not
duplicate that mutable state.

### Conception

The System Brief establishes the complete system frame: objective, pipeline, module boundaries, exact cross-module types, global invariants, cross-cutting policies, output contract, orchestration, physical implementation boundary, persistence boundary, execution-resource boundaries, and selected dependency boundaries.

Module Briefs then define the exact behavior of every implementation module selected by the System Brief. They contain the algorithms, signatures, edge cases, error behavior, and constraints required to eliminate implementation discretion.

Dependency Contracts define only the exact external interfaces consumed by those modules. `llm-runtime` requires a scoped Dependency Contract before implementation of its consumer boundary. Any additional non-trivial dependency receives a contract only if the accepted module design actually selects it.

The TDD Tests Brief is written last. It defines observable acceptance tests, property/anti-cheat tests, contract invariants, fixtures, and test vectors without prescribing internal implementation structure.

The complete construction pack is then subjected to hostile specification review. Workspace hostile-review tooling used for this construction review is not Gate A hostile-review evidence and must never be substituted for the campaign protocol under `formal/reviews/`.

Material discoveries from conception or hostile construction review are routed through the repository discovery-classification contract before they are incorporated into authoritative or implementation artifacts.

### RED

RED consumes only the accepted NIB-T.

The implementing agent creates executable acceptance tests, property tests, contract invariants, fixtures, helpers, and only the minimum production stubs required for the suite to compile.

At the end of RED:

```text
test suite compiles
AND
all NIB-T behavioral tests fail for the intended missing behavior
AND
no production implementation exists beyond compilation scaffolding
```

A test that is already green solely because it checks a surface constant, export, fixture shape, or helper behavior is not a NIB-T RED test.

### GREEN

GREEN consumes the accepted NIB-S, all accepted NIB-M briefs, and their Dependency Contracts.

The exact GREEN GitHub work decomposition is not defined in advance by this document.

After NIB-M closure, the architect derives implementation Issues from the actual accepted module/pipeline boundaries. No coding agent chooses that decomposition.

GREEN proceeds in the accepted pipeline order. Every implementation Issue receives exact mechanical instructions derived from the construction pack.

The final implementation must realize, somewhere in the accepted module architecture, all of the following required capability families:

* campaign identity and orchestration;
* exact semantic-subject and review-protocol currentness;
* content-addressed sealed campaign artifacts;
* durable campaign journal, restart, and recovery;
* bounded LLM execution through the selected runtime dependency;
* reviewer-profile and effective-model-identity enforcement;
* initial hostile reviewer execution;
* exact one-to-one finding normalization;
* materiality assessment and hostile materiality challenge;
* structured refutation and hostile refutation challenge;
* discovery classification and conservative routing;
* derivation, normative-impact, and decision-necessity challenge paths;
* exact repair synthesis, hostile repair challenge, and mechanical patch application;
* human Decision Request and exact decision projection;
* repository/worktree isolation and publication boundaries;
* semantic-subject and protocol staleness handling;
* stale-protocol finding re-adjudication;
* top-level `run-gate-a-review` orchestration;
* the external outcomes `GATE-A-READY`, `DECISION-REQUIRED`, and `OPERATOR-ACTION-REQUIRED`.

This list defines required capability closure, not module boundaries. The NIB-S and NIB-M documents own the implementation decomposition during construction.

### Transition

Transition begins only after the full RED suite is GREEN.

The architect then:

1. archives the consumed NIBs and Dependency Contracts according to their construction lifecycle;
2. records any durable architectural rationale that must outlive construction in the appropriate accepted repository authority;
3. establishes code and tests as the current source of truth for implementation behavior;
4. performs the required implementation-quality closure;
5. ensures no active construction document remains a competing current implementation authority.

Workspace quality-review mechanisms are implementation-process tools, not TURNLOCK runtime behavior or Gate A evidence.

## Post-construction qualification

Real reviewer-profile admission and the first real Gate A campaign are intentionally outside the campaign-runner construction boundary.

After construction transition:

1. real eligible reviewer profiles are selected from actually available providers/models;
2. model-identity resolution is verified against the implemented runtime boundary;
3. a new content-addressed hostile-review protocol identity is published if reviewer-profile policy changes;
4. live provider smoke/conformance checks establish that the configured profiles can produce qualifying executions;
5. the first real Gate A assurance-decomposition campaign is executed;
6. findings from that campaign are routed according to the accepted hostile-review and discovery contracts.

Do not create speculative finding-resolution work before real findings exist.

## Work-graph rules

This document describes the stable construction sequence only.

GitHub owns the live work graph.

The initial live work decomposition stops at RED:

```text
NIB-S
  ↓
NIB-M
  ↓
llm-runtime Dependency Contract
  ↓
NIB-T
  ↓
hostile construction-pack review
  ↓
RED
```

The GREEN implementation work graph is created only after the NIB-M decomposition has been authored, checked for inter-NIB coherence, and hostile-reviewed.

This prevents the work tracker from inventing module boundaries before the construction architecture exists.

Native GitHub parent/sub-issue and dependency relationships own current hierarchy and sequencing. Issue bodies and this document must not duplicate their live state.

## Discovery and authority boundary

Implementation pressure is allowed to discover problems. It is not allowed to resolve product under-specification silently.

If conception, testing, implementation, provider integration, or review exposes a material discovery:

```text
observe
  ↓
stop before inventing meaning
  ↓
classify using the repository discovery contract
  ↓
route to the earliest unresolved authoritative cause
```

A product-semantic question is not resolved as an implementation convenience.

An assurance-architecture question is not resolved by a provider API shape.

A technical inability to conclude safely is not converted into `DECISION-REQUIRED`.

## Secrets and provider access

Real API secret values never enter:

* the TURNLOCK repository;
* NIBs or Dependency Contracts;
* campaign packets;
* execution receipts;
* raw hostile-review outputs;
* adjudication artifacts;
* logs intended for durable evidence;
* GitHub Issues or comments.

During development, credentials are resolved through the workspace credential mechanism from Doppler. The campaign runner consumes credentials only through the implementation boundary selected by the NIB-S and Dependency Contract.

Credential storage and retrieval mechanics are not part of Gate A protocol identity unless a later accepted assurance decision explicitly makes them so.

## Construction completion boundary

Campaign-runner construction is complete only when:

* the construction pack was complete enough to remove coding-agent design discretion;
* RED was established before production implementation;
* all accepted behavioral tests are GREEN;
* all selected modules are integrated;
* restart and failure paths are exercised;
* the top-level runner exposes only the accepted external outcomes;
* repository and implementation-quality validation pass;
* construction artifacts have transitioned out of active authority;
* no real hostile-review campaign has been fabricated as implementation evidence.

The separately scoped first real Gate A campaign begins only after this construction boundary.
