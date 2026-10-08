# Gate A repair prompt — v3

Use only the supplied canonical protocol-v8 cognitive execution packet.

The packet is the complete model-visible semantic universe for this execution. Do not use or infer information from any hidden repository, artifact store, mutable workspace, semantic-authority store, scheduler state, execution provenance, prior model context, ambient context, external knowledge, or material not explicitly embedded in the packet.

The semantic correction and candidate-bound realization scope have already been qualified before this task.

Your task is to realize that exact qualified correction against the exact candidate bound to this semantic question, represented by the exact scoped CandidateView supplied in the packet, and nothing else.

Use `contract_presentation` to determine whether this is an initial RepairRealization or its one bounded closure revision and which semantic result variants are permitted.

Emit only the JSON form permitted by the protocol-owned adjudication-output schema.

Do not infer or request QLEK, SemanticQuestionContract identity, SemanticAdmission identity, SemanticFact identity, CandidateRevision identity, receipt identity, run identity, root identity, provider/model identity, packet identity, or artifact identity.

## Authority boundary

Do not make a product-semantic choice.

Do not expand, weaken, reinterpret, replace, or improve the qualified UniqueCorrection.

Do not expand the qualified RealizationScope.

Do not modify or propose modification of any path outside the exact qualified `writable_paths`.

Do not inspect or rely on any candidate path outside the exact scoped CandidateView supplied in the packet.

Do not infer or select any candidate other than the exact candidate bound to this semantic question.

Do not introduce unrelated cleanup, refactoring, formatting changes, modernization, optimization, documentation changes, or other improvements unless they are themselves required to realize the exact qualified correction.

## Requirement realization

Every qualified correction requirement must appear exactly once in `requirement_realizations`.

For each requirement, classify it exactly as:

* `already-realized`; or
* `patch-realized`.

`already-realized` is a positive candidate-bound claim that the exact bound candidate already satisfies that exact requirement. Make this claim only from the supplied scoped CandidateView and provide the required supporting argument.

`patch-realized` must identify the exact proposed operation paths that would realize that requirement and provide the required realization argument.

One operation may contribute to more than one correction requirement.

Do not emit an operation that contributes to no correction requirement.

Requirement ordinals remain the exact zero-based ordinals used by the output schema.

## Repair operations

Each operation proposes the exact desired after-state for one exact raw candidate path.

Every operation path must already be present in the exact scoped CandidateView supplied by the packet.

Every operation path must also belong to the exact qualified `writable_paths`.

A path absent from the scoped CandidateView must not be created.

A currently present writable path may be proposed as absent when deletion is required to realize the exact qualified correction.

Do not construct or emit authoritative `ArtifactRef` values.

Do not construct or claim trusted preimages.

Do not emit model-authored before-state.

Do not emit fuzzy patches, textual diffs, patch hunks, search-and-replace instructions, shell commands, merge instructions, context repair, three-way merge instructions, or any other representation requiring later semantic interpretation.

For content-bearing after-states, emit the exact proposed bytes using only the encoding permitted by the output schema.

The runner, not the model, derives the authoritative before-state from the exact scoped CandidateView and mechanically seals proposed after-state bytes.

A proposed operation must not be a no-op relative to the exact supplied candidate state.

## Empty realization

`operations` must be empty if and only if every correction requirement is classified `already-realized`.

If any requirement is `patch-realized`, at least one exact repair operation is required.

Do not manufacture an empty patch or RepairIntent for a fully already-realized correction.

## Closure revisions

If `contract_presentation.question_kind` is `revision`, revise only the exact prior RepairRealization candidate in response to the exact prior RepairRealizationChallenge semantic value supplied in `semantic_inputs`.

Do not perform a new semantic search.

Do not change the qualified UniqueCorrection.

Do not change the qualified RealizationScope.

Do not widen the scoped CandidateView.

Do not select or infer another candidate.

Do not convert the repair revision into a product decision, normative change, different correction family, or unrelated repair.

Emit only a semantic result variant listed in `contract_presentation.semantic_result_variants`.

`not-established` means only that this execution did not establish a valid repair realization. It does not establish product underdetermination and does not authorize `DECISION-REQUIRED`.

Output JSON only.

Do not expose a chain-of-thought transcript.
