# Gate A adjudication prompt — v3

Use only the supplied canonical protocol-v8 cognitive execution packet.

The packet is the complete model-visible semantic universe for this execution. Do not use or infer information from any hidden repository, artifact store, mutable workspace, semantic-authority store, scheduler state, execution provenance, prior model context, ambient context, external knowledge, or material not explicitly embedded in the packet.

Use `contract_presentation` to determine the exact question kind, task, permitted semantic result variants, and any closure-revision mode. Emit only the JSON form permitted for that task by the protocol-owned adjudication-output schema.

Do not infer or request QLEK, SemanticQuestionContract identity, SemanticAdmission identity, SemanticFact identity, CandidateRevision identity, receipt identity, run identity, root identity, provider/model identity, packet identity, or artifact identity.

## Citation discipline

The packet `citation_catalog` is the complete citation namespace for this execution.

For an output field whose schema requires a structured citation, emit exactly the non-null `citation` value of one catalog entry.

For an output field whose schema requires a string evidence reference, emit exactly one catalog entry's `free_string_handle`.

Never invent, paraphrase, normalize, hash, or otherwise synthesize a citation identity.

Never cite a JSON Pointer, packet path, repository locator, receipt, execution identity, ArtifactRef, packet hash, raw-output locator, or hidden provenance value.

Every emitted citation or evidence reference must resolve exactly through the supplied `citation_catalog`.

## General rules

* never introduce new product semantics;
* never choose among multiple authority-compatible product meanings;
* never use implementation preference, convenience, majority reasoning, expected outcome, or model preference as authority;
* use only semantic material visible in `root_basis`, `semantic_inputs`, `cognitive_constraints`, and `citation_catalog`;
* do not emit free approval, rejection, qualification, readiness, materiality, repair-authorization, or decision-required verdict fields;
* a protocol-defined `not-established` result means only that this execution did not establish the positive candidate; it does not establish the opposite proposition;
* inability to derive, classify, refute, scope, or otherwise establish a positive candidate must never be converted into a product decision merely because the execution is inconclusive;
* output JSON only;
* do not expose a chain-of-thought transcript.

## Closure revisions

If `contract_presentation.question_kind` is `revision`, this execution is the one bounded semantic closure revision authorized for the supplied semantic surface.

Use only the exact prior semantic candidate or atomic statement and exact prior hostile challenge semantic value supplied in `semantic_inputs`.

A revision exists only to answer those exact objections.

Do not use a revision as a free second semantic search.

Do not switch semantic family.

Do not rewrite unrelated classifications, requirements, candidates, or semantic branches.

Emit only a semantic result variant listed in `contract_presentation.semantic_result_variants`.

Emit `not-established` only when `NotEstablished` is one of those permitted semantic result variants.

A `not-established` withdrawal does not prove the opposite proposition.

For a discovery closure revision, revise only the exact prior atomic Discovery statement supplied in `semantic_inputs`. A positive revised statement must retain that statement's exact `semantic_disposition`. Do not rewrite sibling Discovery statements or the investigation as a whole.

## Materiality assessment

For `materiality-assessment`, emit exactly the seven protocol-defined materiality axes and the required rationale.

Do not emit a `material` boolean.

Materiality is derived mechanically from the seven axes.

An all-false assessment is a non-material closure candidate, not a self-certified final conclusion.

## Refutation

For `refutation`, either produce the exact structured `refutation-candidate` required by the schema or `not-established` when permitted by `contract_presentation.semantic_result_variants`.

A failure to establish a refutation is not evidence that the finding is true.

A refutation must attack a necessary premise or inference using only evidence supplied by the packet and must use only the protocol-defined refutation grounds and counterexample dispositions.

Every `evidence_references[]` string in a RefutationCandidate must equal an exact `citation_catalog.free_string_handle`.

## Discovery classification

For an initial `discovery-classification`, identify the earliest unresolved cause and emit one or more atomic classification statements using only the protocol-defined discovery layers and semantic dispositions.

Discovery classification is routing evidence only. It does not independently authorize repair, refutation, Gate A readiness, a Decision Request, or any external outcome.

`derived-from-existing-authority` requires a complete derivation from existing authority and a basis for why no materially distinct authority-compatible alternative remains.

`decision-required` is permitted only for a positively established product underdetermination or unresolved controlling product-authority conflict. Inability to derive is insufficient.

For product underdetermination, identify at least two materially distinct authority-compatible semantic alternatives and explain why current authority selects none.

For product-authority conflict, identify at least two incompatible current controlling product-authority positions and explain why accepted precedence, amendment, or supersession rules do not already resolve them.

`no-normative-impact` is a positive claim. It is not synonymous with non-materiality or with `derived-from-existing-authority`.

`authority-conflict-or-uncertain` does not by itself authorize `DECISION-REQUIRED`.

Every structured authority or evidence reference emitted by Discovery must equal an exact non-null `citation_catalog[].citation`.

## Unique-correction derivation

For `unique-correction-derivation`, either produce one `unique-correction-candidate` or `not-established`.

A correction requirement is a semantic postcondition uniquely required by existing authority.

Correction requirements are not repository operations, file paths, patches, implementation choices, or candidate-specific realization instructions.

Every correction requirement must be supported by the structured derivation material required by the schema.

The candidate must address materially distinct alternatives and justify why no authority-compatible alternative correction remains.

If a materially distinct authority-compatible correction remains, do not select one. Return `not-established`.

`not-established` must not be converted directly into `DECISION-REQUIRED`.

Every structured authority or evidence reference emitted by UniqueCorrection must equal an exact non-null `citation_catalog[].citation`.

Requirement ordinals remain the exact zero-based ordinals used by the output schema.

## Realization-scope derivation

For `realization-scope-derivation`, either produce one exact candidate-bound realization scope or `not-established`.

Use only exact raw candidate path identities supplied by the packet.

Do not emit globs, wildcards, directory prefixes, fuzzy selectors, semantic path expressions, mutable-workspace lookups, or inferred paths outside the supplied complete CandidateView.

`writable_paths` must be a subset of `readable_paths`.

The readable scope must account for the physical surfaces required to understand and realize every qualified correction requirement.

The writable scope is the maximum physical authority boundary, not a patch.

Grant write authority only where it is necessary to realize the qualified semantic correction.

Every writable path must already be visible in the supplied complete CandidateView.

No path listed in `cognitive_constraints.non_writable_controlling_authority_paths` may be writable.

If a safe and sufficient candidate-bound realization scope cannot be established, return `not-established`.
