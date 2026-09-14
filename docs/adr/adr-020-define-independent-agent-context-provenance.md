---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Define independent-agent context provenance"
id: "ADR-020"
status: "accepted"
date: "2026-09-14"
decision_body_sha256: "6f25f0a5efeb958d092dce98a91dd420cd40d23ecb20903b102096c60ee067e2"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-011"
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Initial cognitive-context provenance for workflow-declared independent agents"
---

# ADR-020: Define independent-agent context provenance

## Context

ADR-011 makes independent agents first-class workflow resources, creates a new
cognitive lineage for each declared task, and requires the capability to provide
task-specific context instead of inheriting the entire main-agent lineage by
default. That decision left the context representation and construction
mechanism open.

The remaining provenance question admits materially different product
semantics. A workflow-declared independent agent could begin with an implicit
copy of the main agent's cognitive history plus workflow additions, or it could
begin a fresh lineage whose initial cognitive context comes only from explicit
workflow semantics. Both interpretations permit task-specific context, but only
the latter makes cognitive isolation reliable and intentional.

This question applies to an independent agent declared directly by workflow
semantics. ADR-007 preserves the ordinary local agency of the main agent, and
ADR-008 permits that main agent to use harness capabilities while it owns a
main-agent region. A child agent created through such local delegation is not
therefore automatically a first-class independent-agent region in the enclosing
TURNLOCK workflow.

## Discovery classification

### Derived clarification: global orchestration authority

- **Statement:** Independent-agent local discretion does not confer global
  workflow-orchestration authority.
- **Source and evidence:** The accepted control split is stated in ADR-011 and
  ADR-014 and normatively projected by `TL-INV-013` and `TL-INV-030`.
- **Existing authority:** ADR-011, ADR-014, `TL-INV-013`, and `TL-INV-030`.
- **Semantic consequence:** Independent-agent discretion remains local. The
  workflow is the source of declared topology, phase, and continuation, and an
  agent result affects progression only as workflow semantics relate it to
  permitted continuations.
- **Why no new choice is introduced:** Giving the agent undeclared global
  authority would directly contradict the cited control-ownership decisions.
- **Failure if omitted:** Local autonomy could be mistaken for authority to add
  a next step, skip a phase, rewrite the enclosing graph, or own global
  progression.
- **Semantic disposition:** `derived-from-existing-authority`.
- **Affected layers:** `normative-contract`, `decision-history`, and
  `formal-model-or-analysis`.
- **Related discoveries or consequences:** The context-provenance decision below
  must preserve this authority split.
- **Required authority:** None beyond the cited accepted authority.
- **Next action:** Clarify `TL-INV-025`, `TL-INV-030`, and their formalization
  notes without introducing a new invariant.

### Derived clarification: declared local task

- **Statement:** The workflow owns an independent agent's semantic task
  boundary, while the agent owns its local strategy and tactics.
- **Source and evidence:** ADR-011 explicitly combines a declared task with
  autonomous multi-turn work within capabilities granted to that task.
- **Existing authority:** ADR-011 and `TL-INV-025` require a declared task and
  autonomous multi-turn work within capabilities granted to that task.
- **Semantic consequence:** The workflow owns the task boundary; the agent owns
  its local plan, tactics, exploration, ordering, and hypothesis changes. The
  task is a semantic mission boundary, not an exhaustive file or action list.
- **Why no new choice is introduced:** Requiring the workflow to predetermine
  every local action would contradict the accepted autonomous execution form,
  while allowing an undeclared mission would remove its accepted task boundary.
- **Failure if omitted:** A conforming investigation could be rejected merely
  for following evidence into another module, or an agent could treat local
  autonomy as an undeclared global mission.
- **Semantic disposition:** `derived-from-existing-authority`.
- **Affected layers:** `normative-contract`, `decision-history`, and
  `formal-model-or-analysis`.
- **Related discoveries or consequences:** No unilateral authority expansion is
  classified separately below.
- **Required authority:** None beyond the cited accepted authority.
- **Next action:** Clarify the existing independent-agent terminology and
  `TL-INV-025` without defining a file or action whitelist.

### Derived clarification: no unilateral authority expansion

- **Statement:** An independent agent may exercise available authority but may
  not create additional authority unilaterally.
- **Source and evidence:** ADR-011 limits autonomous work to granted
  capabilities, and ADR-014 prohibits execution resources from inventing
  undeclared orchestration authority.
- **Existing authority:** ADR-011 limits autonomous work to capabilities granted
  to the task; ADR-014 reserves undeclared orchestration decisions from
  execution resources.
- **Semantic consequence:** An independent agent may exercise available
  authority but cannot create additional authority merely by deciding that it
  needs it. Workflow semantics may explicitly authorize a later grant.
- **Why no new choice is introduced:** Self-created authority would make the
  accepted grant boundary meaningless. The consequence does not select how
  authority is represented or granted.
- **Failure if omitted:** Local discretion could be interpreted as unilateral
  self-escalation into tools, permissions, or orchestration authority that no
  responsible semantic source granted.
- **Semantic disposition:** `derived-from-existing-authority`.
- **Affected layers:** `normative-contract`, `decision-history`,
  `formal-model-or-analysis`, and `integration-or-conformance`.
- **Related discoveries or consequences:** Capability representation remains an
  open realization or future product question.
- **Required authority:** None beyond the cited accepted authority.
- **Next action:** State only the semantic prohibition on unilateral expansion;
  do not select a grant mechanism.

### Derived clarification: internal main-agent children

- **Statement:** A child spawned through local main-agent agency is not
  automatically a first-class workflow-declared independent-agent region.
- **Source and evidence:** ADR-007 preserves ordinary main-agent agency, ADR-008
  preserves session-local capabilities, and ADR-011 distinguishes workflow
  declaration from local main-agent delegation.
- **Existing authority:** ADR-007 preserves ordinary main-agent agency; ADR-008
  preserves session capabilities during a main-agent region; ADR-011 makes
  independent agents first-class when workflow semantics declare them.
- **Semantic consequence:** A child spawned only through main-agent local
  delegation is not automatically a first-class TURNLOCK execution region.
- **Why no new choice is introduced:** Automatic promotion would erase the
  accepted distinction between ordinary local agency and workflow-declared
  topology.
- **Failure if omitted:** TURNLOCK could assign lineage, context, branch, or join
  semantics to an internal child that the workflow never declared.
- **Semantic disposition:** `derived-from-existing-authority`.
- **Affected layers:** `normative-contract`, `decision-history`,
  `formal-model-or-analysis`, and `integration-or-conformance`.
- **Related discoveries or consequences:** The B1 rule below applies only after
  workflow semantics declare a first-class independent-agent region.
- **Required authority:** None beyond the cited accepted authority.
- **Next action:** Preserve the distinction in canonical terminology,
  `TL-INV-026`, and conformance consequences.

### Decision record: initial cognitive-context provenance

- **Statement:** A workflow-declared independent agent receives no implicit
  main-agent cognitive context and begins with cognitive context supplied
  explicitly through workflow semantics.
- **Source and evidence:** The product owner's directive accompanying execution
  of Issue #8 explicitly accepts this decision. ADR-011's weaker context
  capability left both implicit and explicit provenance compatible.
- **Existing authority:** ADR-007 and ADR-011 require lineage distinction and
  permit task-specific context but do not uniquely determine initial-context
  provenance.
- **Semantic disposition:** `decision-required`, now resolved by this accepted
  ADR.
- **Affected layers:** `normative-contract`, `decision-history`,
  `formal-model-or-analysis`, and `integration-or-conformance`.
- **Related discoveries or consequences:** The internal-main-agent-child
  distinction above constrains the rule's scope.
- **Required authority:** Product-owner acceptance through the repository ADR
  process; supplied explicitly in the directive for resolving Issue #8.
- **Next action:** Record the decision below, strengthen `TL-INV-026`, and
  synchronize formal traceability and generated projections.

Context serialization, provider or harness instructions, tool descriptions,
runtime environment, capability representation, and context-size limits remain
non-normative realization or future product questions and are not decided here.

## Decision

A workflow-declared independent agent starts a fresh cognitive lineage distinct
from the main-agent lineage.

Its initial cognitive context consists only of information supplied explicitly
through workflow semantics. It receives no implicit inheritance of the main
agent's cognitive history. The workflow may explicitly supply a summary derived
from that history, artifacts, files, prior results, or any other declared
information. Explicit transfer of such information is not implicit lineage
inheritance.

After execution begins, the independent agent may acquire additional
information through the capabilities available to its autonomous work. That
acquired information belongs to its own execution and does not retroactively
make its initial context an implicit copy of the main-agent lineage.

Conceptually:

```text
workflow-declared independent agent
=
fresh cognitive lineage
+ initial cognitive context explicitly supplied by workflow semantics
+ information acquired during its own execution
```

It is not:

```text
implicit main-agent cognitive history
+ workflow additions
```

Fresh lineage and absence of implicit main-agent cognitive context do not mean
absence of runtime instructions, system instructions, tool descriptions,
harness-provided environment, or technical state required for execution. This
decision does not classify or prescribe those mechanisms. It governs only
implicit inheritance of the main agent's cognitive lineage.

An agent spawned internally by the main agent during a main-agent region remains
local delegation under the main agent's ordinary agency unless executable
workflow semantics explicitly declare that agent as a first-class TURNLOCK
independent-agent region. TURNLOCK does not reinterpret such internal delegation
as workflow topology, and this context-provenance rule does not automatically
apply to that child agent.

This decision selects no context API, serialization format, snapshot model,
storage mechanism, provider behavior, harness instruction policy, capability
manifest, access-control system, or resource limit.

## Rationale

A distinct lineage is useful only if its separation from the main-agent lineage
is deliberate rather than dependent on an adapter's ambient-context behavior.
Explicit workflow provenance lets the author transfer exactly the information
needed for a declared task, including information derived from the main agent,
without pretending that selected transfer is continuation of that lineage.

The rule also preserves ordinary main-agent agency. A main agent may delegate
locally through its harness without TURNLOCK promoting every child into a
workflow branch. First-class independent agency exists when the workflow
declares it, not merely whenever an agent process happens to be created.

## Alternatives considered

### Implicitly inherit main-agent cognitive history

Rejected. Cognitive isolation would become unreliable and adapter-dependent,
and a workflow could not reason intentionally about a fresh independent
lineage.

### Prohibit all information derived from the main agent

Rejected. The workflow may explicitly pass summaries, artifacts, files, and
prior results. Explicit information flow does not preserve or clone the main
agent's cognitive lineage.

### Apply the rule to every child spawned during a main-agent region

Rejected. It would redefine ordinary local main-agent delegation as first-class
workflow topology and conflict with ADR-007, ADR-008, and ADR-011.

### Define a context serialization or capability manifest now

Rejected. Those are replaceable realization choices or future decisions and are
not necessary to define cognitive-context provenance.

## Consequences

- `TL-INV-026` must require no implicit main-agent cognitive-context inheritance
  and explicit workflow provenance for initial independent-agent cognitive
  context.
- `TL-INV-025` continues to distinguish independent-agent lineage from
  main-agent continuation and now relies on the stronger provenance rule in
  `TL-INV-026`.
- A workflow may deliberately pass main-agent-derived information without
  changing the independent agent into main-agent continuation.
- Harness and adapter conformance must distinguish workflow-declared independent
  agents from child agents created only through local main-agent delegation.
- A future formal model may abstract whether initial cognitive context is
  workflow-declared and whether the lineage is distinct. It must not invent a
  context format, runtime activation identifier, or finite product resource
  limit.

## Verification obligation

A conforming realization of workflow-declared independent agency must
demonstrate that:

1. the independent agent is represented as a lineage distinct from the main
   agent;
2. its initial cognitive context is attributable to explicit workflow
   semantics rather than ambient inheritance of main-agent cognitive history;
3. explicitly transferred main-agent-derived information remains permitted;
4. information may be acquired during autonomous execution through available
   capabilities; and
5. an internally spawned main-agent child is not classified as a first-class
   TURNLOCK independent-agent region unless workflow semantics declare it.

The demonstration must not claim that absence of implicit cognitive inheritance
requires an empty runtime environment or a particular provider, harness,
serialization, tool, permission, or context-construction mechanism.

## References

- `docs/specification/turnlock-spec.md`
- `docs/adr/adr-007-preserve-main-agent-cognitive-lineage-and-ordinary-interactive-agency.md`
- `docs/adr/adr-008-allow-nested-workflow-invocation-from-main-agent-regions.md`
- `docs/adr/adr-011-make-independent-agents-first-class-and-support-parallel-fan-out-fan-in.md`
- `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
- GitHub Issues #1, #2, and #8
