---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Require completed workflow execution inspectability"
id: "ADR-018"
status: "accepted"
date: "2026-09-14"
decision_body_sha256: "5f6b3d4fea0939842161af857fbbef8262f13634dc4e310225eb1a285bd2dc67"
relation_completeness: "complete"
relations:
  clarifies: []
  amends: []
  supersedes: []
  confirms: []
governs:
  - "Minimum inspectability of completed workflow executions and separation of execution truth from evaluation and optimization"
---

# ADR-018: Require completed workflow execution inspectability

## Context

TURNLOCK workflows are reusable executable representations of parts of a user's
working method. ADR-001 places declared orchestration in executable workflow
logic instead of main-agent recollection. ADR-014 makes TURNLOCK the engine that
executes, coordinates, and tracks that logic. Existing continuity obligations
keep active progression well defined, but they do not ensure that the behavior
of a completed execution remains understandable.

That gap would allow an execution to become an opaque event. A user or
higher-level system could then refine the workflow only by reconstructing what
probably happened from scattered outputs, human recollection, or agent
conversational memory. This would weaken the practical value of turning a
working method into a reusable executable artifact. Debugging is one use case,
but the broader product loop is authoring, execution, inspection and evaluation,
refinement, and renewed execution.

TURNLOCK knows facts at its own semantic boundary while executing declared
workflow semantics. A user, main agent, external evaluator, or higher-level
workflow or system may interpret those facts against its own criteria. Enabling
that interpretation is distinct from making TURNLOCK itself an evaluator,
benchmark system, run comparator, experiment manager, or workflow optimizer.

## Decision

Every completed TURNLOCK workflow execution MUST make enough of its actual
TURNLOCK-visible behavior inspectable for a user or higher-level system to
understand and evaluate how the workflow progressed in practice and to support
iterative refinement without reconstructing the execution from human or agent
recollection.

The required inspectability concerns workflow-mediated structure, execution
boundaries, explicitly exposed inputs and results, and TURNLOCK-visible facts
relevant to declared progression. Depending on the workflow, such facts may
include which declared regions executed, which declared continuation was
selected, which iterations or fan-outs occurred, where handoffs or nested
invocations began and completed, where nested completion returned, and which
defined outcome a region produced. These examples explain the semantic boundary;
they do not establish a universal event catalog or separate invariant for every
fact.

TURNLOCK core is responsible for exposing sufficient execution truth at that
boundary. The user or a higher-level system remains responsible for defining
what good means, evaluating behavior, comparing executions where appropriate,
deciding what should change, and modifying or optimizing the workflow. Whether
TURNLOCK should later provide native evaluation or optimization facilities is a
separate product decision.

The obligation does not require disclosure of private or internal reasoning by
raw LLM inference, independent agents, or the main agent. Information produced
inside such a region matters at this boundary only when it becomes an explicitly
exposed result or another TURNLOCK-visible fact relevant to declared
progression. The decision does not require recording every tool call within an
agentic region.

This decision establishes no particular tracing, event, storage, telemetry, or
user-interface mechanism. It does not by itself imply a `Run`, `RunSpec`,
`RunProof`, run or activation identifier, persistent event log, workflow hash or
revision identity, canonical timestamp, retention policy, replay engine,
cross-run comparability, reproducibility level, execution proof, experiment
framework, evaluation profile, metric, or automatic optimization capability. It
also does not imply computational determinism, output determinism, or identical
traces.

Actual execution and a workflow definition presented during later inspection
must not be conflated. An inspection surface MUST NOT present a later or current
workflow definition as proof of what a previous execution actually did. This
constraint does not decide which definition governs an active invocation, when
artifact edits become visible, or how any governing definition is identified or
represented. Those workflow-definition binding questions remain owned by Issue
#4.

This decision applies to completed executions. The treatment of failed,
cancelled, interrupted, or otherwise non-completed executions remains a separate
product question.

## Alternatives considered

- **Keep completed execution outside the product promise:** Rejected because a
  reusable workflow could become opaque after execution and iterative refinement
  would depend on recollection or reconstruction.
- **Make inspectability optional, profiled, or capability-dependent:** Rejected
  for the minimum obligation because any completed execution could otherwise
  become opaque. Optional profiles may add stronger guarantees without weakening
  the universal semantic-boundary minimum.
- **Make TURNLOCK itself the evaluator or optimizer:** Rejected as an implication
  of this decision. Execution truth enables evaluation but does not define
  evaluation criteria, comparison policy, experiments, or workflow changes.
- **Require a concrete tracing or persistence architecture now:** Rejected
  because the accepted obligation does not uniquely determine an event schema,
  identifiers, storage, retention, telemetry, replay, or user interface.
- **Require visibility into agent reasoning or every agent tool call:** Rejected
  because workflow-boundary facts and explicitly exposed results are sufficient
  to state the product obligation without exposing private cognitive internals.
- **Require replay, comparability, reproducibility, or execution proofs:**
  Rejected because each is stronger and independently decidable.

## Consequences

### Benefits

- Actual workflow behavior remains sufficiently understandable for user- or
  system-led evaluation and iterative refinement.
- TURNLOCK supports the full author, execute, inspect/evaluate, refine, and
  execute-again loop without owning the evaluator or optimizer role.
- The requirement stays at the harness-independent execution-semantics boundary
  and leaves implementation mechanisms replaceable.

### Costs and obligations

- TURNLOCK runtimes and supported harness integrations must expose enough
  boundary-level execution truth to satisfy the abstract obligation.
- Conformance review must distinguish actual execution facts from reconstruction
  and from unsupported claims about a later/current workflow definition.
- The exact minimum fact set for different workflow shapes, representations,
  retention and access rules, privacy controls, and stronger evaluation features
  require later derivation or decisions.
- Formal analysis may model an abstract subset of boundary-level execution facts,
  but it cannot by itself prove that an inspection surface is semantically
  sufficient for every user or evaluation purpose.

### Derived invariant admission

The accepted decision uniquely entails one distinct universal obligation,
`TL-INV-033`, under the repository's invariant-admission rules:

1. every completed execution is required to expose enough actual
   TURNLOCK-visible behavior for practical understanding and evaluation;
2. an implementation that omits that capability contradicts this decision;
3. every conforming realization owes the obligation independently of mechanism;
4. the invariant states no stronger requirement than the accepted minimum and
   introduces no storage, event, retention, identity, or evaluation choice; and
5. existing active-progression and state-independence invariants do not cover
   post-completion inspectability.

The illustrative boundary facts do not receive separate invariant identities.
Their exact universal or workflow-relative minimum remains a separate semantic
question.

## References

- `docs/specification/turnlock-spec.md`
- `docs/adr/adr-001-make-the-workflow-own-orchestration-after-session-entry.md`
- `docs/adr/adr-003-make-product-intent-and-derived-invariants-govern-implementation.md`
- `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
- `docs/adr/adr-015-evolve-the-normative-and-formal-specifications-together.md`
- `docs/vision/future-workflow-run-evaluation.md`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
- GitHub Issues #4, #11, and #12
