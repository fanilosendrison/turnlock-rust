---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Content-address hostile-review meta-schemas"
id: "ADR-048"
status: "accepted"
date: "2026-09-20"
decision_body_sha256: "40153ec8709526d2ddc632453958a9ad649ce6f8845c7393d6ae28f074198187"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-045"
    - "ADR-046"
    - "ADR-047"
  supersedes: []
  confirms:
    - "ADR-041"
governs:
  - "Hostile-review protocol-bundle meta-schema identity"
  - "Hostile-review evidence meta-schema identity"
  - "Protocol v4 meta-schema binding"
  - "Historical meta-schema interpretation"
  - "Append-only hostile-review meta-schema evolution"
---

# ADR-048: Content-address hostile-review meta-schemas

## Context

Protocol bundles `v1`, `v2`, `v3` are content-addressed.

Their prompts and inner protocol schemas are content-addressed.

`review-protocol-bundle.schema.json` is nevertheless a mutable global
dependency used to interpret those immutable bundles.

`review-evidence.schema.json` is likewise a mutable global dependency used to
interpret top-level review evidence.

Therefore changing either global file could change the interpretation or
validity of historical content-addressed artifacts without changing their own
SHA.

No real hostile-review campaign has yet been executed, so this is the final safe
point to publish the initial evidence meta-schema before real evidence exists.

## Discovery classification

```text
no-normative-impact
```

## Decision

### 4.1 Checker is the finite root of trust

The Python traceability checker remains the mechanical root which selects the
meta-schema appropriate to a protocol-bundle schema version.

This decision does not introduce:

```text
schema registry
registry schema
meta-meta-schema
recursive schema-of-schema chain
```

The chain terminates in checked code plus immutable content-addressed schema
artifacts.

### 4.2 Freeze the current unversioned files

These existing files become frozen legacy aliases:

```text
formal/reviews/review-evidence.schema.json
formal/reviews/review-protocol-bundle.schema.json
```

They remain in the repository for historical links.

They MUST NOT be edited or deleted.

They cease to be active mutable validation authority.

### 4.3 Publish immutable legacy snapshots

Create:

```text
formal/reviews/meta-schemas/review-evidence-v5.schema.json
formal/reviews/meta-schemas/review-protocol-bundle-v1-v3.schema.json
```

`review-evidence-v5.schema.json` MUST be a byte-for-byte copy of the current:

```text
formal/reviews/review-evidence.schema.json
```

`review-protocol-bundle-v1-v3.schema.json` MUST be a byte-for-byte copy of the
current:

```text
formal/reviews/review-protocol-bundle.schema.json
```

Therefore each snapshot has exactly the same SHA-256 as its source legacy alias.

The stale title inside the v1-v3 snapshot is not cleaned up. The exact bytes are
historical validation semantics.

### 4.4 Protocol bundles v1-v3

Protocol bundle schema versions:

```text
1
2
3
```

are validated against exactly:

```text
formal/reviews/meta-schemas/review-protocol-bundle-v1-v3.schema.json
```

at its exact published SHA.

The mutable unversioned alias is no longer consulted.

### 4.5 Review evidence before protocol v4

Because no real campaign evidence exists for protocol v1-v3, there is no
historical real review-record contract requiring preservation before schema 5.0.

Any repository fixture or future parsing of a v1-v3 review record uses the
published immutable schema-5 snapshot:

```text
formal/reviews/meta-schemas/review-evidence-v5.schema.json
```

This is compatibility support only. It does not retroactively claim a real
campaign occurred.

### 4.6 Protocol bundle schema v4

Publish a new bundle meta-schema:

```text
formal/reviews/meta-schemas/review-protocol-bundle-v4.schema.json
```

Protocol bundle schema version 4 requires an exact top-level `meta_schemas`
object containing:

```text
protocol-bundle
review-evidence
```

both as `{path, sha256}` artifact references.

### 4.7 Protocol v4 binds interpretation

Create:

```text
gate-a-campaign-protocol-v4
```

with predecessor exactly protocol v3.

Protocol v4 binds:

```text
meta_schemas.protocol-bundle
=
exact published review-protocol-bundle-v4.schema.json

meta_schemas.review-evidence
=
exact published review-evidence-v5.schema.json
```

Therefore protocol identity `P` now commits to the interpretation contract of
its own bundle and review evidence.

### 4.8 Future evolution

Once a meta-schema is published:

```text
never edit it
never replace bytes at its path
never delete it
```

A future protocol-bundle schema change creates:

```text
a new meta-schema path
+
a new protocol bundle version
+
a new P
```

A future review-evidence schema change creates:

```text
a new immutable review-evidence meta-schema path
+
a protocol bundle that binds that exact artifact
+
a new P
```

`review-evidence-v5.schema.json` is never overwritten.

### 4.9 Product semantics unchanged

Explicitly:

```text
no TURNLOCK product semantic change
no TL-INV change
no TL-CLAIM change
no normative coverage change
no executable formal model
no reviewer profile
no real campaign
review evidence remains schema 5.0
execution receipt remains schema 3.0
Gate A semantic subject remains unchanged
ADR-048 is not added to authority.architecture_decisions
ADR-048 is not added to authority.abstraction_constraints
```

## Consequences

- Every hostile-review artifact can be interpreted from immutable
  content-addressed schemas selected mechanically by protocol-bundle schema
  version.
- The two prior global schema files remain available as frozen historical
  aliases but no longer determine validity.
- Protocol identity `P` commits to both the protocol-bundle interpretation
  schema and the review-evidence interpretation schema.
- Historical v1-v3 bundles remain interpretable through the immutable v1-v3
  snapshot.
- Future meta-schema evolution is append-only and requires a new protocol
  identity.
- No product semantics change and no executable formal model is introduced.

## Non-goals

This ADR does not:

- introduce a schema registry, registry schema, or meta-meta-schema;
- change TURNLOCK product semantics;
- change any `TL-INV-*` or `TL-CLAIM-*` identity;
- change normative coverage;
- change review-evidence schema 5.0;
- change execution receipt schema 3.0;
- change any published protocol v1, v2, or v3 artifact;
- execute a real hostile-review campaign;
- mark Gate A READY.

## References

- `AGENTS.md`
- `docs/adr/adr-041-establish-turnlock-formal-assurance-architecture.md`
- `docs/adr/adr-045-bind-gate-a-campaigns-to-versioned-review-protocol-and-derived-evidence.md`
- `docs/adr/adr-046-bind-challenge-executions-to-exact-inputs-and-derive-retry-admissibility.md`
- `docs/adr/adr-047-make-unvalidated-cognitive-completions-terminal-and-validate-readiness-projections.md`
- `formal/README.md`
- `formal/reviews/README.md`
- `formal/reviews/meta-schemas/README.md`
- `formal/reviews/meta-schemas/review-evidence-v5.schema.json`
- `formal/reviews/meta-schemas/review-protocol-bundle-v1-v3.schema.json`
- `formal/reviews/meta-schemas/review-protocol-bundle-v4.schema.json`
- `formal/reviews/protocols/gate-a-campaign-protocol-v4.json`
- `formal/verification.yaml`
- `scripts/check-formal-traceability.py`
- `scripts/tests/test-formal-traceability.py`
