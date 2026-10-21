---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Retire formal-assurance architecture and reopen post-invariant design"
id: "ADR-059"
status: "accepted"
date: "2026-10-20"
decision_body_sha256: "1e1c2d534693b545a0037f87ed2b9a80286c767ed161641ebcdc10d6413b0df2"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-015"
    - "ADR-052"
  supersedes:
    - "ADR-041"
    - "ADR-042"
    - "ADR-043"
    - "ADR-044"
    - "ADR-045"
    - "ADR-046"
    - "ADR-047"
    - "ADR-048"
    - "ADR-049"
    - "ADR-053"
    - "ADR-054"
    - "ADR-055"
    - "ADR-056"
    - "ADR-057"
  confirms:
    - "ADR-003"
    - "ADR-017"
    - "ADR-040"
    - "ADR-050"
    - "ADR-051"
    - "ADR-058"
governs:
  - "Retirement of the former TURNLOCK formal-assurance construction lineage"
  - "Preservation of current product intent and stable invariant meaning"
  - "Historical-source custody and separation from active authority"
  - "Post-invariant methodological reset without implementation authorization"
---

# ADR-059: Retire formal-assurance architecture and reopen post-invariant design

## Context

On 2026-10-20 the product owner chose to retire the formal-assurance
construction lineage introduced by ADR-041 and restart methodological
reasoning from TURNLOCK's current Product Intent and stable invariants.
This replaces the earlier proposal to refound only the Gate A campaign runner.
The reference repository state is
`b1b8902cb2be879f3930c2730002a1ea5e4e1f02`.

This is an explicit methodological and repository transition decision, not a
proof that the retired architecture, its individual results, or all of its
mechanisms were incorrect or unnecessary. It is not a chronological rollback.

## Decision

1. Preserve current TURNLOCK product meaning, canonical terminology, all 42
   stable invariant definitions, and the unresolved product boundaries already
   stated by the specification. No invariant is added, removed, weakened,
   strengthened, or declared proved by this decision.
2. Supersede ADR-041 through ADR-049 and ADR-053 through ADR-057 as the selected
   active assurance architecture. Their historical bodies and identities remain
   intact. Gate A/B/C, the associated TL-CLAIM decomposition, protocol bundles,
   runner construction, and their selected readiness rules cease to govern new
   work. No retired gate is declared passed.
3. Amend ADR-015 without editing its historical body. Retain normative-source
   authority, stable invariant identity, early formal reasoning as a discovery
   instrument, traceable assumptions and evidence, and the need to examine
   relevant interactions rather than infer whole-system assurance from isolated
   examples. Withdraw its prescribed TLA+/TLC realization, fixed manifest and
   mapping carriers, model/configuration topology, and procedural sequencing as
   mandatory current construction choices. Their replacements remain to be
   justified. This decision does not reactivate an older assurance pipeline.
4. Amend only ADR-052's selection of the two consumer-local Gate A evidence
   requirements and of catalogs/projections/validation instances belonging to
   the retired lineage. Preserve Repository Governance Model v2, its eight
   declared capabilities, the shared Proto-Ring provider and all immutable pins,
   and generic governance semantics. The Evidence Requirements Registry remains
   present with no active requirement instances; emptiness establishes no
   product-assurance or verification claim.
5. Preserve a complete byte-exact source-tree archive and a bounded work-history
   capture before retiring active artifacts or work. The archive is inert
   historical evidence, not a source of executable agent instructions or current
   product, protocol, implementation, or assurance authority. Archived code is
   not executed by active discovery or validation. Historical validation may
   later be reproduced only under an explicitly scoped separate task.
6. Remove the retired formal corpus, runner briefs, and dedicated formal
   checker/test tooling from the active construction path. Adapt only their
   consumer-specific governance bindings and tests. Retain and continue
   enforcing generic ADR integrity, normative terminology, reference protection,
   provider integrity and repository-validation guarantees.
7. Retain counterexamples, bounded results, corrections and unresolved questions
   as historical knowledge. An archived result is neither current proof nor
   refutation merely because of its lifecycle. Reuse requires examination of
   its actual premises, scope, source identity and relevance. Closure of
   abandoned work records non-pursuit, not successful verification.
8. Reopen post-invariant reasoning without selecting a replacement claim layer,
   fixed gate sequence, formalism, integrated-model layout, campaign runner or
   software implementation. The next work must justify its actual question,
   scope, premises, obligations, examination means and admissible conclusions.
   Research from Scope may inform it without becoming TURNLOCK authority.
9. This migration authorizes only the specified repository, archive, governance
   maintenance and work-tracking changes. It does not authorize TURNLOCK runtime
   implementation, an executable product formal model, a real review campaign,
   or a conclusion of whole-product specification closure or realizability.

## Historical references and precedence

Existing ADR bodies and exact historical links remain records of their original
context. References in retained records to retired files or readiness stages do
not reinstate those retired carriers or stages. Their underlying product
requirements remain effective where established by retained product authority.
The current methodological disposition is this ADR, not a README status or an
Issue closure. Changes beyond this bounded disposition require separate
applicable authority.

## Verification of this transition

Verify exact preservation of protected product text and every old ADR body,
complete archive correspondence to the reference Git tree, correct ADR
lifecycle and relations, removal of active retired consumers, preservation of
unrelated governance checks, independent review, exact published-state CI, and
readback of the intended GitHub work dispositions. Repository integrity and
archival success are not product-verification evidence.
