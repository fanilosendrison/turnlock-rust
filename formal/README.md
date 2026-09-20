# Formal model workspace

TURNLOCK's formal-assurance artifacts live here.

No executable canonical formal model exists yet.

`formal/verification.yaml` is the formal-assurance graph. It records normative
provenance, required assurance claims, assurance domains and modalities, formal
coverage, residual assurance, domain bindings, review requirements, and evidence
contracts. It is not product semantics, not the canonical formal semantics, and
not verification evidence.

Gate A is currently expected to remain blocked until hostile review of the exact
assurance decomposition is recorded. Only after Gate A may a candidate
`Turnlock.tla` be authored. Candidate existence does not make it canonical.
Gate B is required for canonical promotion. Gate C is required before checker
evidence may support assurance claims.

## Artifact roles

```text
formal/
├── verification.yaml                       # formal-assurance graph (claims, coverage, policy)
├── verification.schema.json                # schema for that graph
├── reviews/                                # hostile semantic-review evidence and campaign artifacts
│   ├── README.md
│   ├── review-evidence.schema.json         # hostile-review evidence contract, schema 5.0
│   ├── review-protocol-bundle.schema.json  # hostile-review protocol-bundle schema
│   ├── packets/                            # future canonical review packets (JSON)
│   ├── prompts/                            # future canonical review prompts (Markdown)
│   ├── protocols/                          # future versioned review protocol bundles (JSON)
│   ├── schemas/                            # raw-output, challenge-output, and receipt schemas
│   ├── executions/                         # future content-addressed execution receipts (JSON)
│   ├── raw/                                # future sealed raw reviewer outputs (JSON)
│   ├── adjudications/                      # future adjudication outputs (JSON)
│   └── challenges/                         # future hostile challenge outputs (JSON)
├── results/                                # mechanical checker evidence
│   └── README.md
├── migrations/                             # historical migration evidence
│   └── verification-v2-to-v3-property-audit.yaml
├── models/
│   ├── focused/                            # future focused TLC restrictions
│   └── integrated/                         # future integrated TLC configurations
└── Turnlock.tla                            # future candidate canonical semantics
```

`formal/reviews/` holds durable hostile semantic-review evidence for exact
reviewed artifacts, including content-addressed campaign artifacts once a real
hostile-review campaign is executed. No campaign artifact exists yet because no
real campaign has been executed.

`formal/results/` holds mechanical checker evidence, governed by
`formal/tlc-result.schema.json`.

`formal/migrations/` holds historical migration evidence that preserves how the
formal-assurance graph evolved across manifest schema versions.

No current file under `formal/` is a generic TURNLOCK Formal IR. The initial
canonical formal semantic representation remains TURNLOCK-specific integrated
TLA+ semantics.

## Assurance chain

```text
normative TURNLOCK semantics
        ↓ assurance decomposition
TL-CLAIM-* required assurance claims
        ↔ hostile-reviewed correspondence
formal realization (future executable TLA+ identifiers)
        ↓ verification execution
bounded mechanical evidence
        ↓ reviewed evidence lifting
bounded assurance conclusion
```

`TL-INV-*` identities remain the stable normative anchors. Required assurance
claims divide them into evidentially distinct obligations. The manifest owns
intended assurance; `formal/reviews/` and `formal/results/` own what actually
happened.

## Formal realizations

After Gate A permits candidate model authoring, actual claim-to-TLA+ realization
bindings may be added as the candidate model develops.

The existence of such a binding does not imply Gate B, Gate C, semantic
correspondence acceptance, or successful verification evidence.

The Gate A review lifecycle is dependency-scoped:

```text
Gate A review
  ↓ subject = gate-a-assurance-decomposition-v1
Gate A READY
  ↓
candidate Turnlock.tla may be authored
  ↓
formal_realizations may be introduced
  ↓
Gate A remains current if claims/coverage/authority/context are unchanged
```

Changing `formal_realizations` alone does not invalidate Gate A.

Changing a required assurance claim, its normative provenance, normative
coverage, relevant formal-assurance context, or referenced normative authority
does invalidate Gate A.

The derived Gate A subject canonicalizes semantically unordered collections
before hashing. Physical YAML array ordering alone is not a review dependency.

The canonicalized context collections are:

```text
formal_semantic_domains
behavioral_modalities
assurance_domains
```

Changing a domain declaration or changing the membership of a modality/domain set
remains fingerprint-significant.

Every formal semantic domain has a unique `id`.

The `id` is its semantic identity for claim bindings, canonical Gate A subject
ordering, and domain-module resolution. Two distinct domain declarations MUST
NOT share an `id`.

Duplicate formal semantic domain IDs are a repository-integrity failure and
prevent Gate A subject derivation.

## Readiness gates

- **Gate A — Formal-Architecture-Ready** authorizes creation of a candidate
  executable formal model. It does not declare that model correct, canonical, or
  verified. Gate A requires valid current assurance-decomposition campaign
  evidence bound to BOTH the current derived semantic subject `S` and the
  current content-addressed hostile-review protocol bundle `P`: at least
  `minimum_independent_reviewers` distinct `(provider, model, model_version)`
  model identities AND at least `minimum_independent_reviewers` distinct
  effective `(provider, model_version)` identities from protocol-qualified
  reviewer profiles; complete required attack coverage in each qualifying
  execution; the same exact canonical packet and prompt across qualifying
  executions; declared isolated contexts with no cross-reviewer visibility
  before sealing; content-addressed sealed packet/prompt/raw/challenge artifacts
  plus per-call execution receipts; structured JSON raw outputs; exact
  one-to-one raw-finding normalization; a valid zero-objection hostile
  materiality challenge for every non-material finding; no surviving current
  material `open`, `routed`, or `resolved` finding; a valid zero-objection
  structured refutation challenge for every current material `refuted` finding;
  and current-protocol re-adjudication of every stale-protocol finding over the
  current subject. Gate A review packet validity is not merely artifact SHA
  validity: the packet is self-contained and cryptographically bound to its
  declared derived subject. Review evidence paths are direct non-symlink
  repository paths. Gate A campaign subject identity is unambiguous: a Gate A
  assurance-decomposition record contains exactly one Gate A derived subject.
  Packet binding, protocol currentness, and semantic currentness all use that
  exact subject. Additional artifact subjects may coexist but cannot determine
  Gate A identity. It is derived from current review evidence; it is not stored
  as a manifest status.
- **Gate B — Canonical-Formal-Semantics-Ready** promotes an exact candidate
  artifact/version to the current canonical formal semantics for its declared
  scope after hostile semantic review.
- **Gate C — Formal-Verification-Ready** authorizes checker executions to
  support assurance claims after claim/property correspondence review.

`scripts/check-formal-traceability.py` derives and reports the current gate
state. Focused configurations may restrict the integrated semantics; they must
never become independent mini-semantics.

## Hostile-review protocol v3

The current hostile-review protocol identity `P` is `gate-a-campaign-protocol-v3`, and review evidence is schema `5.0`. The protocol history is `v3 -> v2 -> v1`; v1 and v2 are immutable historical bundles. Challenge evidence is bound to an exact canonical self-contained challenge packet embedding the reviewed Gate A packet and challenged candidate. Retry admissibility is checker-derived from sealed output; `protocol-invalid` is permitted only for the deterministically validated roles `initial-reviewer` and `challenge`. For the seven cognitive roles without a deterministic output validator, `protocol-invalid` is forbidden and the first completed response is the terminal `qualified` completion, meaning only the unique admitted completion of that execution. Generated readiness projections are produced only from a full successful traceability and evidence validation pass, so malformed review evidence cannot be projected as `Formal-Architecture-Ready: READY`. These assurance changes do not change TURNLOCK semantics or the Gate A semantic subject.
