# TURNLOCK formal assurance

This directory documents how the normative TURNLOCK specification is connected
to formal-assurance artifacts. The governing decisions are
[ADR-015](../adr/adr-015-evolve-the-normative-and-formal-specifications-together.md)
and
[ADR-041](../adr/adr-041-establish-turnlock-formal-assurance-architecture.md).

## Architecture

```text
normative authority
├─ assurance decomposition → TL-CLAIM
└─ semantic formalization → candidate/canonical formal semantics

TL-CLAIM
↔ hostile-reviewed backend correspondence
↔ actual formal realization

mechanical verifier
→ bounded evidence
→ bounded assurance conclusion
```

Normative product meaning remains `docs/specification/turnlock-spec.md` together
with accepted ADRs. `formal/verification.yaml` is the canonical machine-readable
formal-assurance and traceability graph. It is not product semantics, not the
canonical formal semantics, and not verification evidence.

A future formal realization binding is prospective assurance structure:

```text
formal realization exists
!=
correspondence reviewed
!=
canonical model
!=
verification ready
!=
claim supported
```

## Artifact roles

```text
docs/specification/turnlock-spec.md
= normative product meaning

formal/verification.yaml
= formal-assurance graph: required assurance claims, normative coverage,
  residual assurance, domain bindings, review requirements, evidence contracts

formal/verification.schema.json
= schema for that graph

formal/reviews/*
= durable hostile semantic-review evidence for exact reviewed artifacts

formal/results/*
= concrete mechanism-specific bounded mechanical evidence

formal/migrations/*
= historical migration evidence

formal/Turnlock.tla
= future candidate canonical formal semantic representation (not yet present)

docs/formal/invariant-mapping.md
= generated human-readable projection of the assurance graph
```

## Formalization versus projection

Formalization maps normative natural-language semantics to a formal semantic
representation. It is a reviewed non-mechanical boundary, not a mechanical
derivation.

A formal semantic projection exists only between formal semantic
representations, and its soundness is claim-relative or observation-relative.
A global `equivalent`, `over-approximation`, or `under-approximation` label is
not valid beyond the observations for which the relation is justified. Liveness
requires an explicit preservation argument; projection direction alone does not
establish it.

Verification restriction or instantiation selects and bounds what a focused
checker configuration explores. It is not a new semantics. Independent
formalization is a separately authored formal model used for
semantic-interpretation diversity.

## Review invalidation follows semantic dependency

Review invalidation follows semantic dependency, not physical file
co-location:

```text
formal/verification.yaml
├─ claims + coverage            → Gate A review dependency
└─ formal_realizations          → later correspondence dependency

Changing the second does not invalidate a review whose declared subject is only
the first.
```

Gate A uses the derived `gate-a-assurance-decomposition-v1` subject, which binds
normative authority, the relevant formal-assurance context, the required
assurance claims, and normative coverage. Generated subject fingerprints are
non-authoritative projections of canonical sources.

Semantic dependency also excludes meaningless collection ordering. The Gate A
subject canonicalizes formal semantic domains by `id` and canonicalizes
behavioral/assurance domain sets lexicographically before hashing.

Domain identity is explicit: `policy.formal_semantic_domains[*].id` is unique.

That same identity is used for formal claim bindings and canonical ordering in
the Gate A subject.

## Readiness gates

- **Gate A — Formal-Architecture-Ready** authorizes authoring a candidate
  executable formal model. It requires the accepted assurance architecture, a
  valid metamodel, coverage for every `TL-INV-*`, claims and modalities for the
  candidate scope, explicit residual assurance, an explicit scope, interaction
  closure or justified exclusions, a hostile-review protocol, discovery routing,
  and repository integrity. It requires no checker evidence.
- **Gate B — Canonical-Formal-Semantics-Ready** promotes an exact candidate
  artifact/version to the current canonical formal semantics after hostile
  semantic review, disposition of every material finding, re-review of changed
  boundaries, and non-vacuity or semantic-adequacy witnesses.
- **Gate C — Formal-Verification-Ready** authorizes checker executions to
  support assurance claims after real backend bindings and hostile
  claim/property correspondence review, with adequate profiles, explicit bounds,
  exact artifact identity, and evidence-lifting rules.

The current Gate A state is **BLOCKED** only because the required hostile
`assurance-decomposition` review campaign over the exact current
`formal/verification.yaml` has not yet been recorded, not because the metamodel
is incomplete. `scripts/check-formal-traceability.py` derives this state from
repository artifacts and review evidence rather than from a stored status.

Gate A review adequacy is derived from the policy in
`formal/verification.yaml`, not merely from the existence of a review record:
the declared assurance-decomposition attack set, the declared minimum reviewer
count, and the absence of any surviving material `open`/`routed` finding across
every current assurance-decomposition review of the exact manifest.

## Hostile review is first-class evidence, not proof

Hostile semantic review is a first-class assurance mechanism with durable
evidence under `formal/reviews/`. It is adversarial falsification, not majority
voting: one surviving valid material objection blocks acceptance of the reviewed
semantic link regardless of how many reviewers approved. Review evidence never
constitutes mathematical proof of natural-language/formal equivalence; the
strongest valid conclusion is bounded reviewed semantic correspondence under the
executed review protocol. Review evidence is distinct from mechanical checker
evidence. Every malformed review artifact fails repository integrity rather than
being ignored.

## Generated mapping

`invariant-mapping.md` is generated from `formal/verification.yaml` and current
repository evidence:

```bash
.venv/bin/python scripts/render-formal-mapping.py
```

`scripts/check-formal-traceability.py` validates cross-artifact consistency,
review-evidence integrity, legacy migration totals, and generated-projection
freshness. Machine-readable linkage validates traceability consistency; it does
not prove that a future TLA+ formula faithfully captures the prose meaning.
Semantic correspondence remains a hostile-review obligation.
