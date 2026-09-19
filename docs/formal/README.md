# TURNLOCK formal assurance

This directory documents how the normative TURNLOCK specification is connected
to formal-assurance artifacts. The governing decisions are
[ADR-015](../adr/adr-015-evolve-the-normative-and-formal-specifications-together.md),
[ADR-041](../adr/adr-041-establish-turnlock-formal-assurance-architecture.md),
and, for hostile-review campaign execution, adjudication, and exact evidence
binding,
[ADR-042](../adr/adr-042-define-auditable-hostile-review-campaign-execution-and-adjudication.md),
[ADR-043](../adr/adr-043-bind-hostile-review-evidence-to-exact-reviewed-inputs.md),
[ADR-044](../adr/adr-044-require-one-unambiguous-gate-a-review-subject.md), and
[ADR-045](../adr/adr-045-bind-gate-a-campaigns-to-versioned-review-protocol-and-derived-evidence.md).

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
  and repository integrity. It also requires valid current campaign evidence
  bound to both the semantic subject `S` and the current hostile-review protocol
  bundle `P`: protocol-qualified reviewer profiles with evidence-derived model
  identities; distinct full and effective model identity counts; complete
  required attack coverage in each qualifying execution; the same exact
  canonical packet and prompt; exact content-addressed
  packet/prompt/protocol/receipt/raw/challenge artifacts; exact one-to-one raw
  finding normalization; a valid zero-objection materiality challenge for every
  non-material finding; no surviving current material `open`, `routed`, or
  `resolved` finding; a valid zero-objection structured challenge for every
  current material `refuted` finding; and current-protocol re-adjudication of
  every stale-protocol finding over the current subject. It requires no checker
  evidence.
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
`formal/verification.yaml`, from the review-evidence contract, and from the
referenced campaign artifacts, not merely from the existence of a review record.

Gate A distinguishes two things that must not be conflated:

```text
Gate A semantic subject
!=
Gate A review protocol
```

The semantic subject is the derived `gate-a-assurance-decomposition-v1` subject.
The review protocol is how a campaign is executed, sealed, normalized, and
adjudicated.

ADR-042 changes review adequacy mechanics, not
`gate-a-assurance-decomposition-v1` dependencies. ADR-042 is not added to
`formal/verification.yaml authority.architecture_decisions`.

ADR-043 amends hostile-review evidence mechanics only.

ADR-043 does not enter `gate-a-assurance-decomposition-v1`.

ADR-044 amends hostile-review evidence mechanics only.

It does not enter `gate-a-assurance-decomposition-v1`.

It closes subject confusion by making the unique Gate A derived subject the
single identity used for packet binding and currentness.

ADR-045 amends hostile-review protocol and evidence mechanics only.

It does not enter `gate-a-assurance-decomposition-v1`.

Gate A currentness now requires BOTH the exact semantic subject `S` and the
exact current content-addressed hostile-review protocol bundle `P`. The protocol
bundle owns reviewer-profile qualification, evidence-derived model-version
resolution, structured JSON raw outputs, execution receipts, sealed completed
attempts, one-to-one normalization, conservative challenge closure, and the
external campaign outcomes. A protocol change never erases a finding: every
stale-protocol finding over the current subject requires current-protocol
re-adjudication before it can cease affecting Gate A. The review-evidence schema
is version 4.0.

The Gate A semantic subject remains owned by the existing authority dependency
set.

The current valid subject fingerprint is exactly:

```text
2b0dd42fb07d67f3a38d0414f12df49ecb9df640f12c805ee98b6af3a1db979b
```

The live derived subject value remains owned by `formal/verification.yaml` and
its generated projection in `invariant-mapping.md`, not by ADR-042, ADR-043, or
ADR-045.

Gate A review packets are self-contained canonical JSON artifacts. Verification
recomputes the packet subject SHA from its embedded `subject_payload`, requires
the packet subject to equal a subject declared by the review record, and
recomputes each embedded authority SHA from its UTF-8 contents. A stale
historical packet validates against its own embedded historical subject rather
than current repository authority, so historical evidence remains verifiable
after the repository evolves. Material refutation challenges are bound by
`challenged_refutation_sha256` to the exact canonical refutation subject, and
review evidence paths must be direct non-symlink repository paths.

## Hostile review is first-class evidence, not proof

Hostile semantic review is a first-class assurance mechanism with durable
evidence under `formal/reviews/`. It is adversarial falsification, not majority
voting: one surviving valid material objection blocks acceptance of the reviewed
semantic link regardless of how many reviewers approved. Review evidence never
constitutes mathematical proof of natural-language/formal equivalence; the
strongest valid conclusion is bounded reviewed semantic correspondence under the
executed review protocol. Review evidence is distinct from mechanical checker
evidence. Materiality is derived from explicit impact axes; a non-material
conclusion requires a zero-objection hostile materiality challenge; a material
refutation requires a zero-objection hostile challenge bound to the exact
refutation subject; challenge results are derived from objections without a
free verdict field; and invalid review evidence forces Gate A BLOCKED rather
than being ignored. Failure to establish a valid refutation does not establish
that the finding is true. Every malformed or referentially invalid review
artifact fails repository integrity.

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
