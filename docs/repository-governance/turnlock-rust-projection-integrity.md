---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust mutable projection integrity policy"
---

# Turnlock-Rust mutable projection integrity policy

## Scope

This policy governs mechanically derivable mutable repository state, including:

- current ADR corpus membership, order, titles, lifecycle status, and paths;
- current presence or absence of governed artifacts;
- formal-model lifecycle status;
- formal profile lifecycle status;
- generated mappings;
- current GitHub Issue and Project state.

This policy does not attempt to mechanically prove semantic consistency of
ordinary explanatory prose or vision documents. Existing authority and
discovery-classification rules continue to govern semantic paraphrases.

## Canonical ownership

A mutable derived repository fact must have one canonical owner.

A secondary document must not manually mirror that fact unless the duplicated
derivable portion is mechanically generated or mechanically validated.

Reference, generate, validate, or explicitly snapshot; never manually mirror
mutable derived repository state without a guard.

## Allowed projection modes

Every secondary representation of a mutable derived fact must use exactly one of
these modes:

1. **Reference** - point to the canonical owner without copying the mutable
   value.
2. **Generated projection** - derive the value mechanically from the canonical
   owner.
3. **Validated maintained projection** - keep manually authored explanatory
   text, but mechanically validate all duplicated derivable fields.
4. **Bounded historical snapshot** - retain a past value only when explicitly
   scoped to a date, commit, migration, or other immutable historical context.

A historical range such as a migration explicitly covering ADR-001 through
ADR-016 is legitimate because its scope is immutable historical provenance.

Avoid projection chains: a secondary projection must derive from or be validated
against the canonical owner, never against another projection.

## Forbidden forms

The following are forbidden:

- an explanatory README manually stating the current highest ADR number;
- an explanatory document manually stating current artifact presence or absence
  when another authority owns that state;
- a manual projection derived from another projection;
- relying on agent memory or ordinary diligence as the synchronization
  mechanism.

## Current ownership examples

```text
ADR frontmatter / canonical ADR files
    → canonical ADR identity, name, lifecycle status, path and relations

docs/adr/index.md
    → generated ADR metadata/relationship projection

docs/adr/README.md chronological trace
    → manually maintained narrative
    → derivable identity/name/status/path/order/coverage must be validated
    → narrative annotations remain manually authored

formal/verification.yaml
    → formal-model lifecycle state
    → intended formal traceability and profile state

docs/formal/invariant-mapping.md
    → generated projection of formal/verification.yaml

formal/results/
    → concrete bounded TLC execution evidence

repository filesystem/tree
    → actual artifact presence or absence

accepted ADRs and other declared repository authority
    → accepted implementation/architecture commitments

AGENTS.md
    → repository authorization and execution guardrails

scripts/check-repository-integrity.py
    → mandatory repository validation membership and order

.github/workflows/repository-integrity.yml
    → CI environment/bootstrap plus invocation of the canonical validation suite

GitHub Issue / Project / native relationships
    → live work state
```

README files are explanatory consumers, not additional current-state owners.

## Validation ownership

Validation membership is mutable repository knowledge. Documentation and CI must
reference one canonical executable validation suite rather than maintain parallel
command lists.

## Change protocol

Before introducing a mutable derived fact, decide:

```text
What artifact owns this fact?

If another artifact owns it:
- can this document reference the owner instead of copying the value?
  → reference it.

If the exact value must be reproduced:
- can it be generated?
  → generate it.

If explanatory/manual text must be retained:
- add mechanical validation in the same change.

If the value is intentionally historical:
- bind it explicitly to immutable historical scope.
```

## Completion condition

Repository work is not complete when a canonical change leaves a required
generated or validated projection stale.

Do not create a generic checker solely for this document.
