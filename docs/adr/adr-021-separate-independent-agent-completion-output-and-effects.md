---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Separate independent-agent completion, output, and effects"
id: "ADR-021"
status: "accepted"
date: "2026-09-14"
decision_body_sha256: "6674cf9f305d784925b89d86f74afa14f78ef22212986fc1198a2b7ff32a1f37"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-011"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Normal-completion, optional-output, and persistent-effect semantics for independent-agent regions"
---

# ADR-021: Separate independent-agent completion, output, and effects

## Context

ADR-011 states that an independent-agent step returns a result to
workflow-owned progression. That wording establishes a boundary between local
autonomous work and workflow continuation, but it can be interpreted as
requiring every normally completed independent-agent region to produce a
non-empty business payload.

Many legitimate independent-agent tasks are effect-oriented. An agent may edit
files, run tests, create artifacts, or change external state, while the declared
region contract requires no business value beyond recognition that this
occurrence reached normal completion. Treating completion and output as the same
concept would force such tasks to fabricate payloads and would obscure effects
that exist independently of a returned value.

A future safety model also needs enough semantic structure to represent that a
declared independent-agent occurrence can start, perform local work, and cross
a normal-completion boundary. That structure must not be mistaken for a promise
that every started occurrence eventually completes. Issue #2 separately owns
liveness, fairness, and occurrence-scoped progress semantics.

## Discovery classification

### Derived clarification: bounded raw LLM inference

- **Statement:** Raw LLM inference is a workflow-declared non-agentic semantic
  operation whose boundedness creates no resource or liveness guarantee.
- **Source and evidence:** ADR-012 states the explicit instruction/context/result
  shape and leaves provider and budget mechanisms open; ADR-014 preserves
  workflow-owned global control.
- **Existing authority:** ADR-012, ADR-014, `TL-INV-028`, and `TL-INV-030`.
- **Semantic consequence:** Raw LLM inference is one declared non-agentic
  semantic operation with explicit instruction and context, no autonomous
  observe/reason/act loop, no persistent independent lineage, a result boundary,
  and no global orchestration authority. One semantic operation does not require
  exactly one provider request, physical model call, attempt, or stream.
- **Why no new choice is introduced:** Every positive semantic clause follows
  directly from ADR-012, and the provider-cardinality non-claim preserves the
  mechanisms that ADR-012 explicitly leaves open.
- **Failure if omitted:** Raw inference could be modeled as an autonomous agent
  loop, or a finite formal/provider representation could become an accidental
  runtime request or retry rule.
- **Semantic disposition:** `derived-from-existing-authority`.
- **Affected layers:** `normative-contract`, `decision-history`, and
  `formal-model-or-analysis`.
- **Related discoveries or consequences:** Issue #1 owns property-level
  decomposition; provider realization remains open.
- **Required authority:** None beyond the cited accepted authority.
- **Next action:** Clarify `TL-INV-028` and its formalization note without adding
  or renaming a formal property.

### Derived clarification: independent-agent authority

- **Statement:** Independent-agent local autonomy does not confer global
  workflow-orchestration authority.
- **Source and evidence:** ADR-011 and ADR-014 explicitly separate local
  autonomous execution from workflow-owned progression; `TL-INV-013` and
  `TL-INV-030` project that boundary normatively.
- **Existing authority:** ADR-011, ADR-014, `TL-INV-013`, and `TL-INV-030`.
- **Semantic consequence:** An independent agent may exercise broad local
  discretion for its declared task, but the workflow remains the source of
  declared topology, phase, and continuation. Agent output influences global
  progression only through workflow-authorized semantics.
- **Why no new choice is introduced:** Global agent authority would contradict
  the accepted local/global control split.
- **Failure if omitted:** Local autonomy could be interpreted as permission to
  invent a next step, skip a declared phase, or become the global scheduler.
- **Semantic disposition:** `derived-from-existing-authority`.
- **Affected layers:** `normative-contract`, `decision-history`, and
  `formal-model-or-analysis`.
- **Related discoveries or consequences:** ADR-020 records the distinct context
  provenance decision without transferring global authority.
- **Required authority:** None beyond the cited accepted authority.
- **Next action:** Clarify the existing independent-agent terminology and
  `TL-INV-030` formalization note.

### Derived clarification: structural completion is not liveness

- **Statement:** A possible result or completion transition does not establish
  universal eventual completion, and a finite TLC bound creates no product
  resource limit.
- **Source and evidence:** ADR-015 separates safety from liveness and describes
  finite TLC exploration honestly; ADR-011 and ADR-012 leave lifecycle limits
  open.
- **Existing authority:** ADR-015 requires safety and liveness to remain
  distinct, while ADR-011 and ADR-012 leave lifecycle limits and failure
  behavior open.
- **Semantic consequence:** A structural result or completion transition does
  not establish universal eventual completion. Finite TLC bounds are
  model-checking choices, not TURNLOCK resource limits or termination
  guarantees.
- **Why no new choice is introduced:** The clarification prevents an unsupported
  strengthening and leaves every liveness alternative to Issue #2.
- **Failure if omitted:** A possible `Complete...` transition or finite state
  space could be mistaken for fairness, a mandatory timeout, or proof that every
  started occurrence completes.
- **Semantic disposition:** `derived-from-existing-authority`.
- **Affected layers:** `normative-contract`, `decision-history`,
  `formal-model-or-analysis`, and `verification-or-qualification-evidence`.
- **Related discoveries or consequences:** Issue #2 owns liveness and fairness;
  Issue #1 owns property-level obligation metadata.
- **Required authority:** None for this non-strengthening clarification.
- **Next action:** State completion consequences conditionally and preserve all
  liveness and fairness questions for Issue #2.

### Derived clarification: execution region

- **Statement:** An execution region is a workflow-declared semantic scope whose
  local authority does not confer global orchestration authority; its declaration
  is distinct from a runtime occurrence.
- **Source and evidence:** ADR-004, ADR-005, ADR-011, ADR-012, and ADR-014 use
  workflow regions to distinguish declared execution forms, local activity, and
  workflow-owned continuation without selecting a runtime representation.
- **Existing authority:** ADR-004, ADR-005, ADR-011, ADR-012, and ADR-014 use
  workflow regions to separate declared execution forms, local execution, and
  workflow-owned continuation.
- **Semantic consequence:** An execution region is a workflow-declared semantic
  scope for one execution form. Its declaration is distinct from a runtime
  occurrence, and its local authority does not confer global orchestration
  authority. The structural boundary permits entry, activity, and an applicable
  completion transition without requiring a runtime identifier or liveness.
- **Why no new choice is introduced:** The concept consolidates the common
  structural role already required by the accepted execution forms and does not
  select a representation.
- **Failure if omitted:** A future model could treat a local execution form as
  globally authoritative or promote a useful occurrence identity into a stable
  runtime `activationId` requirement.
- **Semantic disposition:** `derived-from-existing-authority`.
- **Affected layers:** `normative-contract`, `decision-history`, and
  `formal-model-or-analysis`.
- **Related discoveries or consequences:** Issue #3 may choose a formal
  occurrence identity; this ADR creates no runtime identity requirement.
- **Required authority:** None beyond the cited accepted authority.
- **Next action:** Register `execution region` minimally in Section 2 and leave
  formal occurrence identity to downstream modeling.

### Decision record: effects, output, and completion

- **Statement:** Independent-agent effects, output, and completion are distinct;
  effects may persist, a business output is required only when the declared
  contract requires one, and normal completion must be recognizable if reached.
- **Source and evidence:** The product owner's directive accompanying execution
  of Issue #8 explicitly accepts this cohesive distinction. ADR-011's phrase
  "returns a result" did not uniquely decide whether a non-empty business
  payload was mandatory or whether effects were confined to the region.
- **Existing authority:** ADR-011 requires a boundary back to workflow-owned
  progression but leaves result type, lifecycle limits, and concrete mechanisms
  open.
- **Semantic disposition:** `decision-required`, now resolved by this accepted
  ADR.
- **Affected layers:** `normative-contract`, `decision-history`,
  `formal-model-or-analysis`, and `integration-or-conformance`.
- **Related discoveries or consequences:** The structural non-liveness
  clarification above constrains completion wording; Issue #2 retains every
  liveness and fairness question.
- **Required authority:** Product-owner acceptance through the repository ADR
  process; supplied explicitly in the directive for resolving Issue #8.
- **Next action:** Record the decision below, strengthen `TL-INV-025`, and
  synchronize formal traceability and generated projections.

Failure, cancellation, interruption, timeout, retries, resource budgets, and
universal or conditional liveness guarantees remain outside this decision.

## Decision

Independent-agent effects, output, and completion are distinct semantic
concepts.

**Effects** are changes produced during execution, such as modified files,
executed tests, created artifacts, or changed external state. Effects may
survive the region. Bounded local authority does not mean that every physical
effect is confined to or rolled back with the region.

**Output** is a value made explicitly available to workflow semantics when the
declared region contract requires one. A non-empty business payload is not
required by default. A contract may require no business output, conceptually
`unit` or `none`, without this decision selecting a concrete type or
representation. When the contract requires output, normal completion makes that
output available according to the contract.

**Completion** is the fact that a particular occurrence of the region reached
its normal boundary of local work. TURNLOCK must be able to recognize normal
completion so workflow-owned progression can follow the declared continuation.
The concrete recognition mechanism is not specified.

Normatively:

```text
if normal completion occurs
then
  TURNLOCK can recognize that completion
  and workflow-owned progression follows the declared continuation
  and any output required by the region contract becomes available
```

This rule does not mean:

```text
every started independent-agent region eventually completes
```

An effect-oriented region can therefore be valid with persistent effects,
normal completion, and no business payload when its declared contract requires
none.

The agent may decide that its local work is complete according to the authority
available inside the region. That local judgment does not let it invent the
next global step, skip a declared phase, rewrite the enclosing graph, or become
the owner of workflow progression. The workflow owns the continuation and the
relationship between any output and permitted global paths.

This decision selects no completion protocol, process behavior, API return,
session-yield event, output type, serialization, storage, rollback model,
timeout, cancellation, retry, failure-propagation rule, fairness premise, or
resource limit.

## Rationale

Completion is lifecycle information required for orchestration. Output is
contract data. Effects are changes caused by execution. Keeping them separate
lets workflows express effect-oriented autonomous tasks without manufacturing a
business payload and lets joins or continuations observe completion without
claiming that every occurrence terminates.

The distinction also preserves execution-form differences. A result is
constitutive of raw LLM inference as a semantic transformation. Independent
agency, by contrast, may validly complete a declared effect-oriented task whose
contract requires no business payload.

## Alternatives considered

### Require a non-empty business payload from every independent agent

Rejected. It would make valid effect-oriented tasks artificially invalid or
force meaningless payloads.

### Treat persistent effects as the output

Rejected. Effects and explicitly returned contract values have different
semantics and may coexist independently.

### Treat output presence as the only completion signal

Rejected. A no-output contract would then have no normal-completion boundary
visible to workflow progression.

### Guarantee eventual completion

Rejected from this decision's scope. Liveness and fairness remain governed by
Issue #2 and cannot be inferred from a structural completion boundary.

### Select a completion or failure protocol now

Rejected. Process exit, protocol messages, runtime events, API returns, session
yields, failures, cancellation, retries, and timeouts are separate semantic or
realization questions.

## Consequences

- `TL-INV-025` must express conditional normal completion, workflow-owned
  continuation, and output that is optional unless the declared contract
  requires it.
- `TL-INV-028` continues to require a result boundary for raw LLM inference; it
  must not inherit independent-agent optional-business-output semantics.
- `TL-INV-030` continues to govern global control: completion or output may
  affect progression only through declared workflow semantics.
- A future safety model may represent start, local activity, and completion
  transitions without asserting that completion eventually becomes enabled or
  occurs.
- A finite TLC state space or finite model bound does not create a TURNLOCK
  resource limit or termination guarantee.
- Issue #1 owns property-level obligation classification, evidence metamodel,
  and any property split or rename. No property becomes modeled or checked by
  this decision.
- Issue #2 owns liveness, fairness, occurrence scope, and any progress guarantee.

## Verification obligation

A conforming realization must demonstrate at least:

1. an independent-agent region that normally completes with contract-required
   output and makes that output available to workflow semantics;
2. an independent-agent region that normally completes with no business payload
   because its contract requires none;
3. that normal completion and output handling do not require rollback or
   rejection merely because permitted execution effects persist;
4. recognition of normal completion followed by the workflow-declared
   continuation; and
5. no transfer of global orchestration authority to the agent through its local
   completion judgment or output.

These demonstrations establish structural capability and safety boundaries.
They do not establish universal eventual completion, fairness, failure behavior,
or a concrete resource bound.

## References

- `docs/specification/turnlock-spec.md`
- `docs/adr/adr-011-make-independent-agents-first-class-and-support-parallel-fan-out-fan-in.md`
- `docs/adr/adr-012-make-bounded-raw-llm-inference-first-class-and-allocate-minimum-sufficient-cognition.md`
- `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
- `docs/adr/adr-015-evolve-the-normative-and-formal-specifications-together.md`
- GitHub Issues #1, #2, and #8
