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
├── reviews/                                # hostile semantic-review evidence
│   ├── README.md
│   └── review-evidence.schema.json
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
reviewed artifacts.

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

## Readiness gates

- **Gate A — Formal-Architecture-Ready** authorizes creation of a candidate
  executable formal model. It does not declare that model correct, canonical, or
  verified. Gate A requires complete assurance-decomposition attack coverage
  according to `formal/verification.yaml`, the declared minimum reviewer count,
  and no surviving material open/routed finding across any current review of the
  exact manifest. It is derived from current review evidence; it is not stored as
  a manifest status.
- **Gate B — Canonical-Formal-Semantics-Ready** promotes an exact candidate
  artifact/version to the current canonical formal semantics for its declared
  scope after hostile semantic review.
- **Gate C — Formal-Verification-Ready** authorizes checker executions to
  support assurance claims after claim/property correspondence review.

`scripts/check-formal-traceability.py` derives and reports the current gate
state. Focused configurations may restrict the integrated semantics; they must
never become independent mini-semantics.
