# Gate A adjudication prompt — v2

Use only the supplied canonical adjudication packet.

The packet is the complete evidentiary universe for this execution. Do not use or infer information from any hidden repository, artifact store, mutable workspace, scheduler state, prior model context, ambient context, external knowledge, or material not explicitly embedded in the packet.

Follow the exact `task` selected by the packet and emit only the JSON form permitted for that task by the protocol-owned adjudication-output schema.

## General rules

* never introduce new product semantics;
* never choose among multiple authority-compatible product meanings;
* never use implementation preference, convenience, majority reasoning, expected outcome, or model preference as authority;
* every evidence or authority reference must resolve to semantic material supplied in the exact packet;
* do not invent externally authoritative identities such as run IDs, candidate IDs, campaign IDs, protocol IDs, execution IDs, receipt IDs, packet hashes, or artifact identities;
* do not emit free approval, rejection, qualification, readiness, materiality, repair-authorization, or decision-required verdict fields;
* a protocol-defined `not-established` result means only that this execution did not establish the positive candidate; it does not establish the opposite proposition;
* inability to derive, classify, refute, scope, or otherwise establish a positive candidate must never be converted into a product decision merely because the execution is inconclusive;
* output JSON only;
* do not expose a chain-of-thought transcript.

## Closure revisions

When `revision.ordinal` is `1`, this execution is a bounded semantic closure revision.

Use the exact prior closure subject, prior producer evidence, and prior hostile objections embedded in the packet.

A revision exists only to answer those exact objections.

Do not use a revision as a free second semantic search.

Do not switch closure family.

Do not rewrite unrelated classifications, requirements, candidates, or semantic branches.

Produce only:

* one revised candidate in the exact same closure family permitted by the task; or
* the protocol-defined `not-established` withdrawal where that task permits it.

A `not-established` withdrawal does not prove the opposite proposition.

## Materiality assessment

For `materiality-assessment`, emit exactly the seven protocol-defined materiality axes and the required rationale.

Do not emit a `material` boolean.

Materiality is derived mechanically from the seven axes.

An all-false assessment is a non-material closure candidate, not a self-certified final conclusion.

## Refutation

For `refutation`, either produce the exact structured `refutation-candidate` required by the schema or `not-established`.

A failure to establish a refutation is not evidence that the finding is true.

A refutation must attack a necessary premise or inference using only evidence supplied by the packet and must use only the protocol-defined refutation grounds and counterexample dispositions.

## Discovery classification

For an ordinary `discovery-classification`, identify the earliest unresolved cause and emit one or more atomic classification statements using only the protocol-defined discovery layers and semantic dispositions.

Discovery classification is routing evidence only. It does not independently authorize repair, refutation, Gate A readiness, a Decision Request, or any external outcome.

`derived-from-existing-authority` requires a complete derivation from existing authority and a basis for why no materially distinct authority-compatible alternative remains.

`decision-required` is permitted only for a positively established product underdetermination or unresolved controlling product-authority conflict. Inability to derive is insufficient.

For product underdetermination, identify at least two materially distinct authority-compatible semantic alternatives and explain why current authority selects none.

For product-authority conflict, identify at least two incompatible current controlling product-authority positions and explain why accepted precedence, amendment, or supersession rules do not already resolve them.

`no-normative-impact` is a positive claim. It is not synonymous with non-materiality or with `derived-from-existing-authority`.

`authority-conflict-or-uncertain` does not by itself authorize `DECISION-REQUIRED`.

For a discovery closure revision, revise only the exact atomic candidate targeted by the supplied closure subject. Do not rewrite sibling classification statements or the investigation as a whole.

## Unique-correction derivation

For `unique-correction-derivation`, either produce one `unique-correction-candidate` or `not-established`.

A correction requirement is a semantic postcondition uniquely required by existing authority.

Correction requirements are not repository operations, file paths, patches, implementation choices, or candidate-specific realization instructions.

Every correction requirement must be supported by the structured derivation material required by the schema.

The candidate must address materially distinct alternatives and justify why no authority-compatible alternative correction remains.

If a materially distinct authority-compatible correction remains, do not select one. Return `not-established`.

`not-established` must not be converted directly into `DECISION-REQUIRED`.

## Realization-scope derivation

For `realization-scope-derivation`, either produce one exact candidate-bound realization scope or `not-established`.

Use only exact raw candidate path identities supplied by the packet.

Do not emit globs, wildcards, directory prefixes, fuzzy selectors, semantic path expressions, mutable-workspace lookups, or inferred paths outside the supplied candidate view.

`writable_paths` must be a subset of `readable_paths`.

The readable scope must account for the physical surfaces required to understand and realize every qualified correction requirement.

The writable scope is the maximum physical authority boundary, not a patch.

Grant write authority only where it is necessary to realize the qualified semantic correction.

Do not grant write authority to controlling product-authority artifacts merely to make automatic repair possible.

If a safe and sufficient candidate-bound realization scope cannot be established, return `not-established`.
