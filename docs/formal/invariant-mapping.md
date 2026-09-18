# TURNLOCK invariant ↔ formal verification mapping

> **Generated file.** Source of truth: [`../../formal/verification.yaml`](../../formal/verification.yaml).  
> Regenerate with `python scripts/render-formal-mapping.py`.

The normative meaning of every invariant lives in [`../specification/turnlock-spec.md`](../specification/turnlock-spec.md). This file is a generated traceability view, not a substitute for the prose or the TLA+ formulas themselves.

Current executable formal-model status: **not-yet-introduced**. No `checked` claim should be inferred from the existence of a row.

## Forward traceability

| Invariant | Title | Kind | Formalization | TLA+ mapping | Properties | State variables | Actions / transitions | Verification | ADRs |
|---|---|---|---|---|---|---|---|---|---|
| `TL-INV-001` | Workflow-orchestration invariant | safety | planned | pending-model | `DeclaredControlFlowOnly` | — | — | not-yet-modeled | ADR-001, ADR-014 |
| `TL-INV-002` | Engine / decision-owner separation invariant | safety | planned | pending-model | `EngineDoesNotInventTopology` | — | — | not-yet-modeled | ADR-014 |
| `TL-INV-003` | Mechanical-execution invariant | safety | planned | pending-model | `MechanicalExecutionNotAgentMediated` | — | — | not-yet-modeled | ADR-004 |
| `TL-INV-004` | Reversible-handoff invariant | safety+liveness | planned | pending-model | `HandoffPreservesContinuation`, `HandoffCanResume` | — | — | not-yet-modeled | ADR-005 |
| `TL-INV-005` | Repeatable-handoff invariant | reachability | planned | pending-model | `MultipleHandoffsRepresentable` | — | — | not-yet-modeled | ADR-005 |
| `TL-INV-006` | Enclosing-workflow invariant | safety | planned | pending-model | `EnclosingWorkflowPreservedDuringMainAgentRegion` | — | — | not-yet-modeled | ADR-005 |
| `TL-INV-007` | Resume-position invariant | safety | planned | pending-model | `ResumePositionWellDefined` | — | — | not-yet-modeled | ADR-005 |
| `TL-INV-008` | Invocation/return continuity invariant | safety+liveness | planned | pending-model | `StructuredReturnPath`, `InvocationEventuallyReturnsUnderFairness` | — | — | not-yet-modeled | ADR-006, ADR-008 |
| `TL-INV-009` | Main-agent identity/continuity invariant | safety | partial | pending-model | `MainAgentLineagePreserved` | — | — | not-yet-modeled | ADR-007 |
| `TL-INV-010` | Workflow-state independence invariant | safety | planned | pending-model | `WorkflowStateExistsOutsideAgentState` | — | — | not-yet-modeled | ADR-001, ADR-005 |
| `TL-INV-011` | Harness-semantics invariant | conformance | not-applicable | not-applicable | — | — | — | not-yet-modeled | ADR-010 |
| `TL-INV-012` | Non-equivalence of cognitive execution forms invariant | safety | planned | pending-model | `ExecutionFormsRemainDistinct` | — | — | not-yet-modeled | ADR-007, ADR-011, ADR-012 |
| `TL-INV-013` | No-hidden-agent-orchestration invariant | safety | planned | pending-model | `AgentCannotAdvanceUndeclaredGlobalControl` | — | — | not-yet-modeled | ADR-001, ADR-014 |
| `TL-INV-014` | Cognitive-lineage continuity invariant | safety | partial | pending-model | `MainLineageNotForkedByHandoff` | — | — | not-yet-modeled | ADR-007, ADR-032 |
| `TL-INV-015` | Ordinary-agency restoration invariant | conformance | not-applicable | not-applicable | — | — | — | not-yet-modeled | ADR-007 |
| `TL-INV-016` | Workflow-availability invariant | safety | planned | pending-model | `WorkflowInvocationAvailableWheneverMainOwnsControl` | — | — | not-yet-modeled | ADR-002, ADR-008 |
| `TL-INV-017` | Nested-invocation invariant | safety+reachability | planned | pending-model | `NestedInvocationSuspendsCaller`, `CallerStackWellFormed`, `RecursiveNestedInvocationCanBeAdmitted` | — | — | not-yet-modeled | ADR-008, ADR-033 |
| `TL-INV-018` | Immediate-caller return invariant | safety+liveness | planned | pending-model | `ReturnToImmediateCaller`, `CorrectCallerEventuallyResumesUnderFairness` | — | — | not-yet-modeled | ADR-008, ADR-033, ADR-034 |
| `TL-INV-019` | Outer-orchestration preservation invariant | safety | planned | pending-model | `NestedInvocationCannotRewriteOuterContinuation` | — | — | not-yet-modeled | ADR-008, ADR-014, ADR-033, ADR-034 |
| `TL-INV-020` | Same-artifact authoring invariant | dx | not-applicable | not-applicable | — | — | — | not-yet-modeled | ADR-009 |
| `TL-INV-021` | Author-facing primitive invariant | dx | not-applicable | not-applicable | — | — | — | not-yet-modeled | ADR-009 |
| `TL-INV-022` | Harness-independence invariant | architecture | not-applicable | not-applicable | — | — | — | not-yet-modeled | ADR-010 |
| `TL-INV-023` | Pi-reference invariant | architecture | not-applicable | not-applicable | — | — | — | not-yet-modeled | ADR-010 |
| `TL-INV-024` | Heterogeneous parallel composition invariant | safety+reachability | planned | pending-model | `MixedBranchTypesCanCoexist`, `MixedBranchSemanticsPreserved`, `MainAgentCanParticipateInParallelRegion` | — | — | not-yet-modeled | ADR-013, ADR-032 |
| `TL-INV-025` | Independent-agent first-class invariant | reachability+safety | planned | pending-model | `IndependentAgentCanBeWorkflowDeclared`, `IndependentAgentHasDistinctLineage`, `IndependentAgentCanReceiveDelegatedNestedInvocationAuthority` | — | — | not-yet-modeled | ADR-011, ADR-020, ADR-021, ADR-034 |
| `TL-INV-026` | Independent-agent context-provenance invariant | semantic-boundary | partial | pending-model | `IndependentAgentContextIsExplicitlyDeclared` | — | — | not-yet-modeled | ADR-011, ADR-020 |
| `TL-INV-027` | Parallel semantic fan-out/fan-in invariant | safety+liveness | planned | pending-model | `NoPrematureJoin`, `BranchCompletesAtMostOnce`, `JoinEventuallyReleasesUnderFairness`, `MainAgentHandoffIsBranchLocal` | — | — | not-yet-modeled | ADR-011, ADR-012, ADR-013, ADR-032 |
| `TL-INV-028` | Raw-LLM inference invariant | reachability+safety | planned | pending-model | `RawLLMIsBoundedLeaf`, `RawLLMDoesNotCreateAgentLoop` | — | — | not-yet-modeled | ADR-012 |
| `TL-INV-029` | Minimum-sufficient cognition invariant | authoring-principle | not-applicable | not-applicable | — | — | — | not-yet-modeled | ADR-012 |
| `TL-INV-030` | Workflow-owned-control / probabilistic-result invariant | safety | planned | pending-model | `ProbabilisticLeafCannotOwnGlobalControl`, `DelegatedIAInvocationDoesNotOwnGlobalControl` | — | — | not-yet-modeled | ADR-012, ADR-014, ADR-029, ADR-034 |
| `TL-INV-031` | Workflow expressive-power invariant | capability | partial | pending-model | `RequiredCoreFormsComposable` | — | — | not-yet-modeled | ADR-011, ADR-012, ADR-013, ADR-014, ADR-032, ADR-033, ADR-034 |
| `TL-INV-032` | Authorship / execution-authority separation invariant | architecture+conformance | not-applicable | not-applicable | — | — | — | not-yet-modeled | ADR-009, ADR-014, ADR-016, ADR-029 |
| `TL-INV-033` | Completed-execution inspectability invariant | safety+semantic-quality+conformance | partial | pending-model | `CompletedExecutionExposesActualBoundaryFacts` | — | — | not-yet-modeled | ADR-018 |
| `TL-INV-034` | Evaluation/optimization-policy boundary invariant | architecture+conformance | not-applicable | not-applicable | — | — | — | not-yet-modeled | ADR-019 |
| `TL-INV-035` | Declared-invocation invariant | capability+safety | planned | pending-model | `DeclaredInvocationAuthorizedByWorkflowProgram`, `DeclaredInvocationDoesNotRequireAgentHandoff`, `OnlyCallingContinuationSuspended`, `DeclaredInvocationReturnsToImmediateCaller`, `NestedInvocationCannotRewriteOuterContinuation`, `DeclaredRecursiveInvocationCanBeAdmitted` | — | — | not-yet-modeled | ADR-022, ADR-023, ADR-033 |
| `TL-INV-036` | Effective execution-condition provenance invariant | safety+semantic-boundary+conformance | partial | pending-model | — | — | — | not-yet-modeled | ADR-024, ADR-025, ADR-026 |
| `TL-INV-037` | Active-invocation governing-definition stability invariant | safety | planned | pending-model | — | — | — | not-yet-modeled | ADR-027, ADR-028, ADR-029, ADR-033 |
| `TL-INV-038` | Runtime-realization composability invariant | conformance | not-applicable | not-applicable | — | — | — | not-yet-modeled | ADR-030, ADR-031 |
| `TL-INV-039` | Main-agent concurrent-lineage non-forkability invariant | safety | planned | pending-model | `MainLineageNotForkedAcrossUnorderedConcurrentContinuations` | — | — | not-yet-modeled | ADR-007, ADR-013, ADR-032 |
| `TL-INV-040` | Independent-agent-selected invocation main-lineage isolation invariant | safety | planned | pending-model | `IASelectedInvocationCannotReachSessionMainLineage` | — | — | not-yet-modeled | ADR-007, ADR-011, ADR-014, ADR-020, ADR-023, ADR-032, ADR-033, ADR-034 |

## Reverse traceability

The same manifest is mechanically invertible. Once state/action mappings are populated, this section answers questions such as “which product invariants may be affected if `CompleteWorkflow` changes?”.

### TLA+ properties → invariant IDs
- `AgentCannotAdvanceUndeclaredGlobalControl` → `TL-INV-013`
- `BranchCompletesAtMostOnce` → `TL-INV-027`
- `CallerStackWellFormed` → `TL-INV-017`
- `CompletedExecutionExposesActualBoundaryFacts` → `TL-INV-033`
- `CorrectCallerEventuallyResumesUnderFairness` → `TL-INV-018`
- `DeclaredControlFlowOnly` → `TL-INV-001`
- `DeclaredInvocationAuthorizedByWorkflowProgram` → `TL-INV-035`
- `DeclaredInvocationDoesNotRequireAgentHandoff` → `TL-INV-035`
- `DeclaredInvocationReturnsToImmediateCaller` → `TL-INV-035`
- `DeclaredRecursiveInvocationCanBeAdmitted` → `TL-INV-035`
- `DelegatedIAInvocationDoesNotOwnGlobalControl` → `TL-INV-030`
- `EnclosingWorkflowPreservedDuringMainAgentRegion` → `TL-INV-006`
- `EngineDoesNotInventTopology` → `TL-INV-002`
- `ExecutionFormsRemainDistinct` → `TL-INV-012`
- `HandoffCanResume` → `TL-INV-004`
- `HandoffPreservesContinuation` → `TL-INV-004`
- `IASelectedInvocationCannotReachSessionMainLineage` → `TL-INV-040`
- `IndependentAgentCanBeWorkflowDeclared` → `TL-INV-025`
- `IndependentAgentCanReceiveDelegatedNestedInvocationAuthority` → `TL-INV-025`
- `IndependentAgentContextIsExplicitlyDeclared` → `TL-INV-026`
- `IndependentAgentHasDistinctLineage` → `TL-INV-025`
- `InvocationEventuallyReturnsUnderFairness` → `TL-INV-008`
- `JoinEventuallyReleasesUnderFairness` → `TL-INV-027`
- `MainAgentCanParticipateInParallelRegion` → `TL-INV-024`
- `MainAgentHandoffIsBranchLocal` → `TL-INV-027`
- `MainAgentLineagePreserved` → `TL-INV-009`
- `MainLineageNotForkedAcrossUnorderedConcurrentContinuations` → `TL-INV-039`
- `MainLineageNotForkedByHandoff` → `TL-INV-014`
- `MechanicalExecutionNotAgentMediated` → `TL-INV-003`
- `MixedBranchSemanticsPreserved` → `TL-INV-024`
- `MixedBranchTypesCanCoexist` → `TL-INV-024`
- `MultipleHandoffsRepresentable` → `TL-INV-005`
- `NestedInvocationCannotRewriteOuterContinuation` → `TL-INV-019`, `TL-INV-035`
- `NestedInvocationSuspendsCaller` → `TL-INV-017`
- `NoPrematureJoin` → `TL-INV-027`
- `OnlyCallingContinuationSuspended` → `TL-INV-035`
- `ProbabilisticLeafCannotOwnGlobalControl` → `TL-INV-030`
- `RawLLMDoesNotCreateAgentLoop` → `TL-INV-028`
- `RawLLMIsBoundedLeaf` → `TL-INV-028`
- `RecursiveNestedInvocationCanBeAdmitted` → `TL-INV-017`
- `RequiredCoreFormsComposable` → `TL-INV-031`
- `ResumePositionWellDefined` → `TL-INV-007`
- `ReturnToImmediateCaller` → `TL-INV-018`
- `StructuredReturnPath` → `TL-INV-008`
- `WorkflowInvocationAvailableWheneverMainOwnsControl` → `TL-INV-016`
- `WorkflowStateExistsOutsideAgentState` → `TL-INV-010`

### TLA+ state variables → invariant IDs
- No executable state-variable mappings yet.

### TLA+ actions / transitions → invariant IDs
- No executable action/transition mappings yet.


## Integrated verification policy

Focused configurations are not substitutes for integrated exploration. The planned integrated profiles are:

- **integrated-smoke** — `formal/models/integrated/smoke.cfg` — planned: All currently formalized core execution forms under small finite bounds for fast cross-feature feedback.
- **integrated-standard** — `formal/models/integrated/standard.cfg` — planned: All currently formalized core execution forms under ordinary CI bounds.
- **integrated-stress** — `formal/models/integrated/stress.cfg` — planned: Larger deliberately expensive integrated exploration.


## Verification evidence

`verification.yaml` describes **intended traceability and coverage**. Successful TLC execution evidence is a separate artifact class under `formal/results` and is governed by `formal/tlc-result.schema.json`.

An invariant must not be considered `checked` merely because it maps to a TLA+ property or TLC config. A `checked` claim requires matching run evidence for the relevant repository revision and finite bounds.

## Notes on applicability

`not-applicable` does not mean unimportant. It means the invariant is not expected to be proven by the core TLA+ state-machine model. Examples include developer-experience requirements, reference-harness policy, or semantic-quality judgments such as whether a chosen cognition form is truly the minimum sufficient one.

`partial` means TLA+ can check a meaningful structural subset while some real-world semantic obligation remains an implementation/harness/review concern.

Machine-readable linkage validates traceability consistency. It does **not** prove that a TLA+ formula faithfully captures the prose meaning; that semantic correspondence remains a formal-review obligation.
