# Gate A repair prompt — v2

Use only the supplied canonical repair-realization adjudication packet.

The packet is the complete evidentiary universe for this execution. Do not use or infer information from any hidden repository, artifact store, mutable workspace, scheduler state, prior model context, ambient context, external knowledge, or material not explicitly embedded in the packet.

The semantic correction and candidate-bound realization scope have already been qualified before this task.

Your task is to realize that exact qualified correction against the exact current candidate view and nothing else.

Output only the JSON form permitted by the protocol-owned adjudication-output schema.

## Authority boundary

Do not make a product-semantic choice.

Do not expand, weaken, reinterpret, replace, or improve the qualified UniqueCorrection.

Do not expand the qualified RealizationScope.

Do not modify or propose modification of any path outside the exact qualified `writable_paths`.

Do not inspect or rely on any candidate path outside the exact candidate view supplied in the packet.

Do not introduce unrelated cleanup, refactoring, formatting changes, modernization, optimization, documentation changes, or other improvements unless they are themselves required to realize the exact qualified correction.

## Requirement realization

Every qualified correction requirement must appear exactly once in `requirement_realizations`.

For each requirement, classify it exactly as:

* `already-realized`; or
* `patch-realized`.

`already-realized` is a positive candidate-bound claim that the exact current candidate already satisfies that exact requirement. Make this claim only from the supplied exact candidate view and provide the required supporting argument.

`patch-realized` must identify the exact proposed operation paths that would realize that requirement and provide the required realization argument.

One operation may contribute to more than one correction requirement.

Do not emit an operation that contributes to no correction requirement.

## Repair operations

Each operation proposes the exact desired after-state for one exact raw candidate path.

Do not construct or emit authoritative `ArtifactRef` values.

Do not construct or claim trusted preimages.

Do not emit model-authored before-state.

Do not emit fuzzy patches, textual diffs, patch hunks, search-and-replace instructions, shell commands, merge instructions, context repair, three-way merge instructions, or any other representation requiring later semantic interpretation.

For content-bearing after-states, emit the exact proposed bytes using only the encoding permitted by the output schema.

The runner, not the model, derives the authoritative before-state from the exact current candidate and mechanically seals proposed after-state bytes.

A proposed operation must not be a no-op relative to the exact supplied current candidate state.

A currently absent path may be proposed as present only when that exact path is within qualified write authority.

A currently present path may be proposed as absent only when that exact path is within qualified write authority.

## Empty realization

`operations` must be empty if and only if every correction requirement is classified `already-realized`.

If any requirement is `patch-realized`, at least one exact repair operation is required.

Do not manufacture an empty patch or RepairIntent for a fully already-realized correction.

## Closure revisions

When `revision.ordinal` is `1`, revise only the exact prior repair-realization candidate in response to the exact hostile objections embedded in the packet.

Do not perform a new semantic search.

Do not change the qualified UniqueCorrection.

Do not change the qualified RealizationScope.

Do not convert the repair revision into a product decision, normative change, different correction family, or unrelated repair.

Produce only:

* one revised `repair-realization-candidate`; or
* `not-established`.

`not-established` means only that this execution did not establish a valid repair realization. It does not establish product underdetermination and does not authorize `DECISION-REQUIRED`.

Output JSON only.

Do not expose a chain-of-thought transcript.
