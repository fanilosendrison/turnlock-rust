# TURNLOCK formal assurance mapping

> **Generated file.** Source of truth: [`../../formal/verification.yaml`](../../formal/verification.yaml).
> Regenerate with `.venv/bin/python scripts/render-formal-mapping.py`. Do not edit manually.

## Authority and artifact roles

Normative product authority remains `docs/specification/turnlock-spec.md` together with accepted ADRs. This document is a generated projection of the formal-assurance graph; it creates no semantics, no claim, and no verification result.

- [`formal/verification.yaml`](../../formal/verification.yaml) owns the formal-assurance graph: normative provenance, required assurance claims, coverage, residual assurance, domain bindings, review requirements, and evidence contracts.
- [`formal/reviews/`](../../formal/reviews/) owns durable hostile semantic-review evidence for exact reviewed artifacts.
- [`formal/results/`](../../formal/results/) owns concrete mechanism-specific bounded checker evidence.
- The canonical formal semantic representation (initially integrated TLA+ after Gate B) will define the checked abstract semantics for the operational domain. It is not normative product authority.

## Readiness

Formal-Architecture-Ready: BLOCKED
reason: hostile assurance-decomposition review evidence required

Gate A assurance-decomposition subject:
- selector: `gate-a-assurance-decomposition-v1`
- SHA-256: `2b0dd42fb07d67f3a38d0414f12df49ecb9df640f12c805ee98b6af3a1db979b`

Canonical-Formal-Semantics-Ready:
NOT-APPLICABLE — candidate model absent

Formal-Verification-Ready:
NOT-APPLICABLE — candidate model absent

## Normative coverage

| Invariant | Canonical operational coverage | Formal claims | Residual claims |
|---|---|---|---|
| `TL-INV-001` | full | `TL-CLAIM-001`, `TL-CLAIM-002` | — |
| `TL-INV-002` | full | `TL-CLAIM-001`, `TL-CLAIM-003` | — |
| `TL-INV-003` | full | `TL-CLAIM-003`, `TL-CLAIM-004` | — |
| `TL-INV-004` | full | `TL-CLAIM-005`, `TL-CLAIM-006` | — |
| `TL-INV-005` | full | `TL-CLAIM-007` | — |
| `TL-INV-006` | full | `TL-CLAIM-008` | — |
| `TL-INV-007` | full | `TL-CLAIM-009` | — |
| `TL-INV-008` | full | `TL-CLAIM-010`, `TL-CLAIM-011` | — |
| `TL-INV-009` | partial | `TL-CLAIM-012` | `TL-CLAIM-013` |
| `TL-INV-010` | full | `TL-CLAIM-009` | — |
| `TL-INV-011` | none | — | `TL-CLAIM-014` |
| `TL-INV-012` | partial | `TL-CLAIM-015` | `TL-CLAIM-016` |
| `TL-INV-013` | partial | `TL-CLAIM-001`, `TL-CLAIM-002` | `TL-CLAIM-017` |
| `TL-INV-014` | partial | `TL-CLAIM-012` | `TL-CLAIM-013` |
| `TL-INV-015` | none | — | `TL-CLAIM-018` |
| `TL-INV-016` | full | `TL-CLAIM-019` | — |
| `TL-INV-017` | full | `TL-CLAIM-020`, `TL-CLAIM-021`, `TL-CLAIM-022` | — |
| `TL-INV-018` | full | `TL-CLAIM-011`, `TL-CLAIM-021` | — |
| `TL-INV-019` | full | `TL-CLAIM-011`, `TL-CLAIM-023` | — |
| `TL-INV-020` | none | — | `TL-CLAIM-024` |
| `TL-INV-021` | none | — | `TL-CLAIM-025` |
| `TL-INV-022` | none | — | `TL-CLAIM-014`, `TL-CLAIM-026` |
| `TL-INV-023` | none | — | `TL-CLAIM-026` |
| `TL-INV-024` | full | `TL-CLAIM-027`, `TL-CLAIM-028`, `TL-CLAIM-029`, `TL-CLAIM-030`, `TL-CLAIM-032`, `TL-CLAIM-075`, `TL-CLAIM-080`, `TL-CLAIM-081` | — |
| `TL-INV-025` | partial | `TL-CLAIM-033`, `TL-CLAIM-034`, `TL-CLAIM-035`, `TL-CLAIM-036`, `TL-CLAIM-037`, `TL-CLAIM-038`, `TL-CLAIM-039` | `TL-CLAIM-040` |
| `TL-INV-026` | partial | `TL-CLAIM-034`, `TL-CLAIM-041` | `TL-CLAIM-042`, `TL-CLAIM-043` |
| `TL-INV-027` | full | `TL-CLAIM-027`, `TL-CLAIM-029`, `TL-CLAIM-030`, `TL-CLAIM-031` | — |
| `TL-INV-028` | partial | `TL-CLAIM-015`, `TL-CLAIM-044`, `TL-CLAIM-045`, `TL-CLAIM-046` | `TL-CLAIM-016` |
| `TL-INV-029` | partial | `TL-CLAIM-015` | `TL-CLAIM-047` |
| `TL-INV-030` | full | `TL-CLAIM-001`, `TL-CLAIM-003`, `TL-CLAIM-035`, `TL-CLAIM-038` | — |
| `TL-INV-031` | partial | `TL-CLAIM-048` | `TL-CLAIM-049` |
| `TL-INV-032` | none | — | `TL-CLAIM-017`, `TL-CLAIM-050` |
| `TL-INV-033` | partial | `TL-CLAIM-051`, `TL-CLAIM-052`, `TL-CLAIM-053`, `TL-CLAIM-054`, `TL-CLAIM-055` | `TL-CLAIM-056` |
| `TL-INV-034` | none | — | `TL-CLAIM-057`, `TL-CLAIM-058` |
| `TL-INV-035` | full | `TL-CLAIM-010`, `TL-CLAIM-011`, `TL-CLAIM-020`, `TL-CLAIM-021`, `TL-CLAIM-022`, `TL-CLAIM-023`, `TL-CLAIM-032`, `TL-CLAIM-059`, `TL-CLAIM-060`, `TL-CLAIM-061`, `TL-CLAIM-080` | — |
| `TL-INV-036` | partial | `TL-CLAIM-062`, `TL-CLAIM-063`, `TL-CLAIM-065`, `TL-CLAIM-066`, `TL-CLAIM-067` | `TL-CLAIM-064` |
| `TL-INV-037` | full | `TL-CLAIM-021`, `TL-CLAIM-054`, `TL-CLAIM-061`, `TL-CLAIM-068`, `TL-CLAIM-069`, `TL-CLAIM-070`, `TL-CLAIM-071` | — |
| `TL-INV-038` | none | — | `TL-CLAIM-072`, `TL-CLAIM-073`, `TL-CLAIM-074` |
| `TL-INV-039` | full | `TL-CLAIM-075`, `TL-CLAIM-076`, `TL-CLAIM-077` | — |
| `TL-INV-040` | full | `TL-CLAIM-078`, `TL-CLAIM-079`, `TL-CLAIM-081` | — |
| `TL-INV-041` | full | `TL-CLAIM-061`, `TL-CLAIM-071`, `TL-CLAIM-077`, `TL-CLAIM-080`, `TL-CLAIM-081`, `TL-CLAIM-082` | — |
| `TL-INV-042` | full | `TL-CLAIM-083` | — |

## Required assurance claims

| Claim | Assurance domain | Modality | Normative sources | Statement |
|---|---|---|---|---|
| `TL-CLAIM-001` | formal-behavioral | safety | `TL-INV-001`, `TL-INV-002`, `TL-INV-013`, `TL-INV-030` | Every change in global control of an active workflow is authorized by executable workflow semantics; neither TURNLOCK nor an execution resource invents an undeclared global continuation or topology. |
| `TL-CLAIM-002` | formal-behavioral | safety | `TL-INV-001`, `TL-INV-013` | Declared non-agentic workflow control can progress without requiring the main agent to act as the global scheduler or reconstruct missing orchestration. |
| `TL-CLAIM-003` | formal-behavioral | reachability | `TL-INV-002`, `TL-INV-003`, `TL-INV-030` | Probabilistic, nondeterministic, external, LLM-produced, or agent-produced results can select among continuations already authorized by executable workflow semantics without acquiring global orchestration authority. |
| `TL-CLAIM-004` | formal-behavioral | safety | `TL-INV-003` | A mechanical step progresses only according to its executable semantics and available runtime inputs, results, state, or events, or produces a defined non-success outcome; it does not require an agent to supply an orchestration decision absent from those semantics. |
| `TL-CLAIM-005` | formal-behavioral | safety | `TL-INV-004` | A handoff to the main agent preserves the continuation capability and workflow state required for later workflow resumption. |
| `TL-CLAIM-006` | formal-behavioral | reachability | `TL-INV-004` | For every nonterminal main-agent step, a workflow-to-main-agent-to-workflow control path is admissible. |
| `TL-CLAIM-007` | formal-behavioral | reachability | `TL-INV-005` | A workflow can represent more than one main-agent step or handoff; the architecture does not impose a single-handoff limit. |
| `TL-CLAIM-008` | formal-behavioral | safety | `TL-INV-006` | While a main-agent region is active, the workflow remains the enclosing execution and local agent autonomy does not redefine the workflow's remaining declared progression. |
| `TL-CLAIM-009` | formal-behavioral | safety | `TL-INV-007`, `TL-INV-010` | Sufficient workflow execution state and the correct continuation remain represented independently of the main agent's conversational recollection so workflow resumption does not require reconstruction from agent memory. |
| `TL-CLAIM-010` | formal-behavioral | safety | `TL-INV-008`, `TL-INV-035` | Acceptance of a workflow invocation preserves a structured return relation carrying the appropriate continuation to that invocation's exact immediate caller context. |
| `TL-CLAIM-011` | formal-behavioral | safety | `TL-INV-008`, `TL-INV-018`, `TL-INV-019`, `TL-INV-035` | Normal completion of an invocation returns that exact invocation occurrence to the same immediate caller context and authorizes only the continuation appropriate to that caller. |
| `TL-CLAIM-012` | formal-behavioral | safety | `TL-INV-009`, `TL-INV-014` | A TURNLOCK main-agent continuation preserves one continuing abstract main-agent lineage rather than silently replacing it with a distinct independent-agent lineage. |
| `TL-CLAIM-013` | conformance | — | `TL-INV-009`, `TL-INV-014` | A concrete harness realization presented as a TURNLOCK main-agent step preserves the required interactive and cognitive-lineage continuity, and any weaker capability is explicitly identified as weaker rather than represented as equivalent. |
| `TL-CLAIM-014` | conformance | — | `TL-INV-011`, `TL-INV-022` | Every harness declared supported by TURNLOCK realizes the same abstract TURNLOCK workflow semantics; harness-specific mechanisms or capability limitations do not silently redefine those semantics. |
| `TL-CLAIM-015` | formal-behavioral | safety | `TL-INV-012`, `TL-INV-028`, `TL-INV-029` | Mechanical execution, raw LLM inference, independent-agent execution, and main-agent continuation remain semantically distinct execution forms. |
| `TL-CLAIM-016` | conformance | — | `TL-INV-012`, `TL-INV-028` | A concrete realization claiming one TURNLOCK cognitive execution form satisfies that form's contract rather than silently substituting another form. |
| `TL-CLAIM-017` | conformance | — | `TL-INV-013`, `TL-INV-032` | A concrete implementation does not delegate hidden global scheduling or workflow reconstruction to an agent while claiming workflow-owned orchestration or independent workflow execution. |
| `TL-CLAIM-018` | conformance | — | `TL-INV-015` | A main-agent step restores the ordinary interactive coding-agent behavior required by that region and is not reduced to a stateless or one-shot request/response mechanism. |
| `TL-CLAIM-019` | formal-behavioral | safety | `TL-INV-016` | Whenever the session main agent owns control, TURNLOCK workflows available to that session remain invocable, including when that control was reached through a main-agent region of another workflow. |
| `TL-CLAIM-020` | formal-behavioral | safety | `TL-INV-017`, `TL-INV-035` | An accepted nested invocation suspends and preserves its immediate caller rather than discarding, replacing, or implicitly completing that caller. |
| `TL-CLAIM-021` | formal-behavioral | safety | `TL-INV-017`, `TL-INV-018`, `TL-INV-035`, `TL-INV-037` | Accepted invocation occurrences remain distinct even when a workflow identity repeats through recursive or cyclic invocation. |
| `TL-CLAIM-022` | formal-behavioral | reachability | `TL-INV-017`, `TL-INV-035` | A recursive or cyclic workflow invocation can be admitted when otherwise authorized and admissible; equality with or reachability to an ancestor workflow identity is not itself a rejection condition. |
| `TL-CLAIM-023` | formal-behavioral | safety | `TL-INV-019`, `TL-INV-035` | A nested callee cannot replace, rewrite, capture, skip, or implicitly complete an ancestor invocation's preserved continuation or declared progression. |
| `TL-CLAIM-024` | conformance | — | `TL-INV-020` | Workflows authored directly by developers and workflows authored or modified by coding agents target the same semantic workflow artifact and execution model. |
| `TL-CLAIM-025` | architecture | — | `TL-INV-021` | TURNLOCK author-facing primitives directly express TURNLOCK control concepts so workflow authors do not need to encode harness-internal control mechanisms. |
| `TL-CLAIM-026` | architecture | — | `TL-INV-022`, `TL-INV-023` | TURNLOCK semantics remain independent of any one coding harness, and Pi-specific or other reference-harness mechanics do not become normative merely because they are implemented first. |
| `TL-CLAIM-027` | formal-behavioral | reachability | `TL-INV-024`, `TL-INV-027` | Workflow-owned parallel fan-out and fan-in can represent independent semantic work, including admissible heterogeneous branch types and main-agent continuation. |
| `TL-CLAIM-028` | formal-behavioral | safety | `TL-INV-024` | Parallel composition preserves each branch type's lifecycle, context, authority, completion, effects, lineage, and declared output semantics while fan-out, synchronization, collection, join, and continuation remain workflow-owned. |
| `TL-CLAIM-029` | formal-behavioral | safety | `TL-INV-024`, `TL-INV-027` | A main-agent handoff reached inside one parallel branch is local to that branch and does not implicitly suspend unrelated sibling branches that remain enabled by the declared topology. |
| `TL-CLAIM-030` | formal-behavioral | safety | `TL-INV-024`, `TL-INV-027` | Completion of one branch, including a main-agent branch, cannot make a post-join continuation eligible before the declared join requirements are satisfied. |
| `TL-CLAIM-031` | formal-behavioral | safety | `TL-INV-027` | When the declared requirements of a particular join occurrence are satisfied, its declared post-join continuation becomes eligible according to the workflow topology; eventual advancement is a separate liveness obligation. |
| `TL-CLAIM-032` | formal-behavioral | reachability | `TL-INV-024`, `TL-INV-035` | A nested workflow invocation can occur as branch-local composition inside an admissible parallel or otherwise restricted context and is not treated as a separate parallel execution form. |
| `TL-CLAIM-033` | formal-behavioral | reachability | `TL-INV-025` | A workflow can directly declare an independent-agent execution region without yielding to the main agent solely to create an agent already required by the workflow topology. |
| `TL-CLAIM-034` | formal-behavioral | safety | `TL-INV-025`, `TL-INV-026` | Each workflow-declared independent-agent occurrence has a fresh cognitive lineage distinct from the session main-agent lineage. |
| `TL-CLAIM-035` | formal-behavioral | safety | `TL-INV-025`, `TL-INV-030` | An independent-agent region may exercise its declared local semantic and discretionary authority without acquiring ownership of enclosing global workflow orchestration. |
| `TL-CLAIM-036` | formal-behavioral | reachability | `TL-INV-025` | Workflow semantics can explicitly delegate local nested-workflow selection and invocation authority to an independent agent, including dynamic selection without a universal requirement to pre-enumerate every exact callee identity. |
| `TL-CLAIM-037` | formal-behavioral | safety | `TL-INV-025` | Independent-agent status, local judgment, tool or shell access, TURNLOCK access, workflow visibility, or knowledge of a workflow do not by themselves grant TURNLOCK semantic authority to create a nested workflow invocation. |
| `TL-CLAIM-038` | formal-behavioral | safety | `TL-INV-025`, `TL-INV-030` | Delegated independent-agent nested-invocation authority does not transfer ownership of enclosing sequencing, branching, fan-out, synchronization, join, continuation, or main-agent transitions. |
| `TL-CLAIM-039` | formal-behavioral | safety | `TL-INV-025` | If an independent-agent occurrence reaches normal completion, TURNLOCK recognizes that completion, follows the workflow-declared continuation, and makes any output required by the region contract available. |
| `TL-CLAIM-040` | conformance | — | `TL-INV-025` | A concrete independent-agent realization provides autonomous multi-turn local behavior compatible with the region's declared mission, distinct lineage, and available local authority. |
| `TL-CLAIM-041` | formal-behavioral | safety | `TL-INV-026` | The initial cognitive context of a workflow-declared independent agent contains no implicit inheritance of main-agent cognitive context; semantic inputs from that context are supplied explicitly through workflow semantics. |
| `TL-CLAIM-042` | conformance | — | `TL-INV-026` | Concrete independent-agent context construction satisfies the explicit-input and no-implicit-main-context contract. |
| `TL-CLAIM-043` | conformance | — | `TL-INV-026` | The no-implicit-context rule does not prohibit explicitly supplied main-agent-derived summaries, artifacts, files, or prior results, and does not prohibit an independent agent from acquiring information later through its available capabilities. |
| `TL-CLAIM-044` | formal-behavioral | reachability | `TL-INV-028` | Raw LLM inference is directly available as a declared bounded non-agentic semantic operation without requiring creation of an autonomous agent loop or a main-agent handoff solely to obtain model intelligence. |
| `TL-CLAIM-045` | formal-behavioral | safety | `TL-INV-028` | A raw LLM inference occurrence has no autonomous observe-reason-act loop, no persistent independent cognitive lineage, and no global workflow-orchestration authority. |
| `TL-CLAIM-046` | formal-behavioral | safety | `TL-INV-028` | A raw LLM inference semantic operation has explicit instruction and context and a result boundary while remaining bounded and non-agentic. |
| `TL-CLAIM-047` | semantic-quality | — | `TL-INV-029` | The authoring model preserves the author's ability to choose the least powerful execution form semantically sufficient for a region rather than collapsing all cognitive work into one universal agent step. |
| `TL-CLAIM-048` | formal-behavioral | reachability | `TL-INV-031` | The required core TURNLOCK execution and control forms are jointly composable so known orchestration decisions can remain executable workflow logic rather than being delegated back to an agent for lack of expressive power. |
| `TL-CLAIM-049` | architecture | — | `TL-INV-031` | The authoring and control surface provides a sufficiently small orthogonal set of primitives to express the required workflow space without forcing known decisions back into agent interpretation. |
| `TL-CLAIM-050` | architecture | — | `TL-INV-032` | The identity or nature of a workflow's author does not confer runtime orchestration authority, and an authored or generated workflow remains independently represented and executed. |
| `TL-CLAIM-051` | formal-behavioral | safety | `TL-INV-033` | For an accepted invocation whose normal completion or other terminal or cessation outcome is observed by TURNLOCK, inspection exposes the actual realized execution or realized prefix and only terminal facts TURNLOCK actually knows. |
| `TL-CLAIM-052` | formal-behavioral | safety | `TL-INV-033` | Inspectable execution truth preserves occurrence distinctions and multiplicity, structural and causal relationships, effective control resolutions, and input or result attribution whenever those distinctions are necessary to determine realized progression. |
| `TL-CLAIM-053` | formal-behavioral | safety | `TL-INV-033` | Inspection does not impose an artificial total order on concurrent occurrences that TURNLOCK semantics do not causally order. |
| `TL-CLAIM-054` | formal-behavioral | safety | `TL-INV-033`, `TL-INV-037` | Inspection that depends on workflow definition semantics uses the exact governing definition that actually governed the invocation rather than a later mutable workflow definition. |
| `TL-CLAIM-055` | formal-behavioral | safety | `TL-INV-033` | Required execution truth is not irreversibly lost before a realizable terminal inspection handoff makes a semantically sufficient representation acquirable by an eligible inspection context. |
| `TL-CLAIM-056` | conformance | — | `TL-INV-033` | A concrete inspection realization provides a semantically sufficient representation to an eligible inspection context while preserving the distinction between underlying execution truth and a potentially more restrictive consumer-visible disclosure view. |
| `TL-CLAIM-057` | architecture | — | `TL-INV-034` | TURNLOCK Core defines no universal evaluation objective, universal quality metric, default superiority relation, experiment policy, or autonomous workflow optimizer. |
| `TL-CLAIM-058` | architecture | — | `TL-INV-034` | Evaluation or optimization behavior receives no privileged runtime authority, and workflow improvement remains authorship rather than active invocation replanning. |
| `TL-CLAIM-059` | formal-behavioral | reachability | `TL-INV-035` | A workflow-declared invocation can execute directly from declared workflow topology without a main-agent handoff whose only purpose would be to reproduce an invocation decision already present in that topology. |
| `TL-CLAIM-060` | formal-behavioral | safety | `TL-INV-035` | A declared nested invocation suspends only the calling continuation associated with that invocation and does not implicitly suspend independently active concurrent contexts allowed to continue by the declared topology. |
| `TL-CLAIM-061` | formal-behavioral | safety | `TL-INV-035`, `TL-INV-037`, `TL-INV-041` | An attempted invocation rejected before acceptance creates no accepted callee, callee lifetime, governing definition, or call-return episode and does not enable the normal successful post-call continuation. |
| `TL-CLAIM-062` | formal-behavioral | safety | `TL-INV-036` | Every effective execution condition that TURNLOCK selects, binds, explicitly supplies, or resolves remains semantically distinguished and attributable to the execution scope it governs until the required semantic-boundary capture handoff. |
| `TL-CLAIM-063` | formal-behavioral | safety | `TL-INV-036` | Required execution-condition provenance is not irreversibly lost before TURNLOCK discharges its side of the realizable semantic-boundary capture handoff. |
| `TL-CLAIM-064` | conformance | — | `TL-INV-036` | A concrete provenance-capture boundary is realizable without depending on inaccessible transient internal state or accidental timing, and discharge does not require an actual consumer, successful delivery, processing, or acknowledgment. |
| `TL-CLAIM-065` | formal-behavioral | safety | `TL-INV-036` | An execution condition outside TURNLOCK observation or control may remain unknown or unavailable, and unknown provenance is not represented as known-equal across executions or as evidence that no relevant difference exists. |
| `TL-CLAIM-066` | formal-behavioral | safety | `TL-INV-036` | Known but protected execution-condition provenance retains condition-specific information bound to its occurrence and governed scope through the required capture handoff; redaction does not replace that underlying provenance with unknown or with a generic marker as the sole representation. |
| `TL-CLAIM-067` | formal-behavioral | safety | `TL-INV-036` | Later failure, cancellation, or interruption does not retroactively erase a condition's governed-scope attribution or its pre-handoff provenance obligation. |
| `TL-CLAIM-068` | formal-behavioral | safety | `TL-INV-037` | Every accepted invocation has one governing workflow definition no later than acceptance, and that governing definition remains unchanged throughout the invocation's active lifetime without active replanning or rebinding. |
| `TL-CLAIM-069` | formal-behavioral | safety | `TL-INV-037` | Each accepted nested invocation independently binds its own governing definition, and repeated workflow identity does not merge invocation occurrences or their governing bindings. |
| `TL-CLAIM-070` | formal-behavioral | reachability | `TL-INV-037` | A descendant or later invocation can bind a resolved governing definition different from an active ancestor's governing definition without rebinding or mutating that ancestor. |
| `TL-CLAIM-071` | formal-behavioral | safety | `TL-INV-037`, `TL-INV-041` | For a successfully admitted invocation, the workflow definition whose composition was admitted is exactly the definition bound as governing at acceptance; a rejected attempt binds no governing definition. |
| `TL-CLAIM-072` | conformance | — | `TL-INV-038` | When an execution-relevant realization is not fixed by TURNLOCK semantics and a semantically preserving alternative is technically realizable at runtime, TURNLOCK Core provides a supported runtime composition path for that alternative without requiring Core modification or recompilation. |
| `TL-CLAIM-073` | conformance | — | `TL-INV-038` | A runtime-supplied realization can become effective before the first causal use it is intended to govern. |
| `TL-CLAIM-074` | conformance | — | `TL-INV-038` | Once an external realization has been accepted as governing an applicable use, that governed use does not silently execute through a different realization unless applicable TURNLOCK semantics authorize the alternative. |
| `TL-CLAIM-075` | formal-behavioral | safety | `TL-INV-024`, `TL-INV-039` | The same continuing main-agent cognitive lineage is not admitted into two independently concurrent, non-causally-ordered continuations. |
| `TL-CLAIM-076` | formal-behavioral | reachability | `TL-INV-039` | Multiple uses of the same continuing main-agent lineage remain admissible when declared causal ordering or established mutual exclusion prevents them from becoming unordered concurrent continuations. |
| `TL-CLAIM-077` | formal-behavioral | safety | `TL-INV-039`, `TL-INV-041` | An incompatible topology is not made conforming by scheduler order, silent serialization, lineage cloning, execution-form substitution, or invented causal order; when required compatibility cannot be established, the topology or invocation is not admitted. |
| `TL-CLAIM-078` | formal-behavioral | safety | `TL-INV-040` | Every invocation subtree causally rooted in an independent-agent-selected nested invocation is unable to transitively reach the coding session's existing main-agent cognitive lineage across nested, declared, parallel, recursive, or cyclic composition. |
| `TL-CLAIM-079` | formal-behavioral | reachability | `TL-INV-040` | After structured return from an independent-agent-selected invocation subtree and appropriate continuation or completion of its independent-agent caller, the enclosing parent workflow can later select a main-agent continuation through its own declared semantics. |
| `TL-CLAIM-080` | formal-behavioral | safety | `TL-INV-024`, `TL-INV-035`, `TL-INV-041` | A nested workflow invocation is accepted only when it is independently authorized and preserves every applicable admissibility restriction; when required compatibility cannot be established at the acceptance boundary, the invocation is rejected. |
| `TL-CLAIM-081` | formal-behavioral | safety | `TL-INV-024`, `TL-INV-040`, `TL-INV-041` | Restrictions whose accepted scope extends into descendant composition remain effective across nested, recursive, and cyclic workflow boundaries, and neither a workflow boundary nor runtime scheduler order resets, weakens, widens, or manufactures admissibility. |
| `TL-CLAIM-082` | formal-behavioral | safety | `TL-INV-041` | Acceptance of a caller invocation does not pre-authorize future descendant invocations; every attempted nested invocation occurrence has its own admission boundary. |
| `TL-CLAIM-083` | formal-behavioral | liveness | `TL-INV-042` | For every particular TURNLOCK-owned progression occurrence, if that occurrence is eligible and remains continuously eligible and continuously applicable under its governing workflow semantics, TURNLOCK eventually advances that same occurrence. |

## Formal realizations

No executable formal realizations are declared yet.

## Reverse traceability

### Claim → invariant IDs

- `TL-CLAIM-001` → `TL-INV-001`, `TL-INV-002`, `TL-INV-013`, `TL-INV-030`
- `TL-CLAIM-002` → `TL-INV-001`, `TL-INV-013`
- `TL-CLAIM-003` → `TL-INV-002`, `TL-INV-003`, `TL-INV-030`
- `TL-CLAIM-004` → `TL-INV-003`
- `TL-CLAIM-005` → `TL-INV-004`
- `TL-CLAIM-006` → `TL-INV-004`
- `TL-CLAIM-007` → `TL-INV-005`
- `TL-CLAIM-008` → `TL-INV-006`
- `TL-CLAIM-009` → `TL-INV-007`, `TL-INV-010`
- `TL-CLAIM-010` → `TL-INV-008`, `TL-INV-035`
- `TL-CLAIM-011` → `TL-INV-008`, `TL-INV-018`, `TL-INV-019`, `TL-INV-035`
- `TL-CLAIM-012` → `TL-INV-009`, `TL-INV-014`
- `TL-CLAIM-013` → `TL-INV-009`, `TL-INV-014`
- `TL-CLAIM-014` → `TL-INV-011`, `TL-INV-022`
- `TL-CLAIM-015` → `TL-INV-012`, `TL-INV-028`, `TL-INV-029`
- `TL-CLAIM-016` → `TL-INV-012`, `TL-INV-028`
- `TL-CLAIM-017` → `TL-INV-013`, `TL-INV-032`
- `TL-CLAIM-018` → `TL-INV-015`
- `TL-CLAIM-019` → `TL-INV-016`
- `TL-CLAIM-020` → `TL-INV-017`, `TL-INV-035`
- `TL-CLAIM-021` → `TL-INV-017`, `TL-INV-018`, `TL-INV-035`, `TL-INV-037`
- `TL-CLAIM-022` → `TL-INV-017`, `TL-INV-035`
- `TL-CLAIM-023` → `TL-INV-019`, `TL-INV-035`
- `TL-CLAIM-024` → `TL-INV-020`
- `TL-CLAIM-025` → `TL-INV-021`
- `TL-CLAIM-026` → `TL-INV-022`, `TL-INV-023`
- `TL-CLAIM-027` → `TL-INV-024`, `TL-INV-027`
- `TL-CLAIM-028` → `TL-INV-024`
- `TL-CLAIM-029` → `TL-INV-024`, `TL-INV-027`
- `TL-CLAIM-030` → `TL-INV-024`, `TL-INV-027`
- `TL-CLAIM-031` → `TL-INV-027`
- `TL-CLAIM-032` → `TL-INV-024`, `TL-INV-035`
- `TL-CLAIM-033` → `TL-INV-025`
- `TL-CLAIM-034` → `TL-INV-025`, `TL-INV-026`
- `TL-CLAIM-035` → `TL-INV-025`, `TL-INV-030`
- `TL-CLAIM-036` → `TL-INV-025`
- `TL-CLAIM-037` → `TL-INV-025`
- `TL-CLAIM-038` → `TL-INV-025`, `TL-INV-030`
- `TL-CLAIM-039` → `TL-INV-025`
- `TL-CLAIM-040` → `TL-INV-025`
- `TL-CLAIM-041` → `TL-INV-026`
- `TL-CLAIM-042` → `TL-INV-026`
- `TL-CLAIM-043` → `TL-INV-026`
- `TL-CLAIM-044` → `TL-INV-028`
- `TL-CLAIM-045` → `TL-INV-028`
- `TL-CLAIM-046` → `TL-INV-028`
- `TL-CLAIM-047` → `TL-INV-029`
- `TL-CLAIM-048` → `TL-INV-031`
- `TL-CLAIM-049` → `TL-INV-031`
- `TL-CLAIM-050` → `TL-INV-032`
- `TL-CLAIM-051` → `TL-INV-033`
- `TL-CLAIM-052` → `TL-INV-033`
- `TL-CLAIM-053` → `TL-INV-033`
- `TL-CLAIM-054` → `TL-INV-033`, `TL-INV-037`
- `TL-CLAIM-055` → `TL-INV-033`
- `TL-CLAIM-056` → `TL-INV-033`
- `TL-CLAIM-057` → `TL-INV-034`
- `TL-CLAIM-058` → `TL-INV-034`
- `TL-CLAIM-059` → `TL-INV-035`
- `TL-CLAIM-060` → `TL-INV-035`
- `TL-CLAIM-061` → `TL-INV-035`, `TL-INV-037`, `TL-INV-041`
- `TL-CLAIM-062` → `TL-INV-036`
- `TL-CLAIM-063` → `TL-INV-036`
- `TL-CLAIM-064` → `TL-INV-036`
- `TL-CLAIM-065` → `TL-INV-036`
- `TL-CLAIM-066` → `TL-INV-036`
- `TL-CLAIM-067` → `TL-INV-036`
- `TL-CLAIM-068` → `TL-INV-037`
- `TL-CLAIM-069` → `TL-INV-037`
- `TL-CLAIM-070` → `TL-INV-037`
- `TL-CLAIM-071` → `TL-INV-037`, `TL-INV-041`
- `TL-CLAIM-072` → `TL-INV-038`
- `TL-CLAIM-073` → `TL-INV-038`
- `TL-CLAIM-074` → `TL-INV-038`
- `TL-CLAIM-075` → `TL-INV-024`, `TL-INV-039`
- `TL-CLAIM-076` → `TL-INV-039`
- `TL-CLAIM-077` → `TL-INV-039`, `TL-INV-041`
- `TL-CLAIM-078` → `TL-INV-040`
- `TL-CLAIM-079` → `TL-INV-040`
- `TL-CLAIM-080` → `TL-INV-024`, `TL-INV-035`, `TL-INV-041`
- `TL-CLAIM-081` → `TL-INV-024`, `TL-INV-040`, `TL-INV-041`
- `TL-CLAIM-082` → `TL-INV-041`
- `TL-CLAIM-083` → `TL-INV-042`

Once formal realizations exist, this section also renders `formal realization identifier → claim IDs → invariant IDs`.

## Evidence classes

- **Hostile semantic-review evidence** — `formal/reviews/`, schema `formal/reviews/review-evidence.schema.json`; 0 record(s) present.
- **Mechanical TLC evidence** — `formal/results/`, schema `formal/tlc-result.schema.json`; 0 record(s) present.
- **Future conformance evidence** — not yet represented by a repository evidence contract.

## Legacy v2 property migration

50 historical planned property entries were audited:

- 48 migrated to required assurance intent;
- 2 retained only as supporting-model-property candidates;
- 0 discarded as meaningless.

Audit: [`../../formal/migrations/verification-v2-to-v3-property-audit.yaml`](../../formal/migrations/verification-v2-to-v3-property-audit.yaml).

## Notes

This projection derives its readiness state from repository artifacts and review evidence. Assurance claims record intended assurance; they are not verification results. Hostile review is bounded reviewed semantic correspondence, not mathematical proof. Mechanical checker evidence cannot by itself support an invariant directly; it is lifted through reviewed claim/property correspondence and declared coverage.

Model presence: `formal/Turnlock.tla` does not exist.
