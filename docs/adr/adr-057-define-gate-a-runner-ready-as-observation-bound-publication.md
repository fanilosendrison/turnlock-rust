---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Define Gate A runner ready as observation-bound publication"
id: "ADR-057"
status: "superseded"
date: "2026-10-19"
decision_body_sha256: "ba92f2abda5ac7800a28136776699dabac0cdeb24ab079fd45933aa01a94dcb4"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-041"
    - "ADR-045"
  amends: []
  supersedes: []
  confirms:
    - "ADR-051"
    - "ADR-052"
governs:
  - "Gate A runner v1 terminal outcome semantics"
  - "Observation-bound publication and temporal claim scope"
  - "Separation of runner completion and current formal Gate A readiness"
  - "Publication-state satisfaction versus execution-outcome attribution"
  - "Gate A controller publication responsibility boundary"
---

# ADR-057: Define Gate A runner ready as observation-bound publication

## Context

ADR-041 defines Formal-Architecture-Ready (formal Gate A) as a verdict over the
current governed repository's assurance evidence. It authorizes the creation of
a candidate executable formal model; it is not a terminal result conferred by a
campaign run.

ADR-045 defines the runner's three normal external outcomes:
`GATE-A-READY`, `DECISION-REQUIRED`, and `OPERATOR-ACTION-REQUIRED`. It does
not uniquely select a remote Git publishing mechanism or require a particular
Execution to be the historical author of a publication.

The active Gate A campaign-runner NIB-S §§29–31 and GI-40 select a stronger
end-to-end v1 construction policy: qualify an exact candidate, confirm its
published representation, validate the exact published representation, and only
then establish the runner's terminal `GATE-A-READY` fact. NIB-S §29 already
distinguishes this terminal result from formal Gate A readiness mechanically
derived for the current repository.

Two questions remained underdetermined by the upstream decision record: whether
this particular runner's success means that an immutable publication was
positively observed or that the mutable Git ref must still point to that commit
whenever success is consumed; and whether satisfying a publication obligation
requires historical attribution of the Git update to one named armed Execution.

This decision closes those two runner-outcome questions without deciding the
separate recovery, Git-transport, WorkItem, or authoritative-state-admission
mechanisms. The architectural provenance is the Issue #78 decision candidate
recorded in comment 6264043457 and the separate Issue #87 recovery proposal.

## Discovery classification

```text
Statement: the temporal meaning and execution-authorship requirement of the
Gate A runner's publication-backed terminal outcome require an explicit
controller construction/outcome decision.

Semantic disposition: decision-required, resolved for runner outcome semantics
by this ADR; remaining realization and evidence choices stay open.

Affected layers: decision-history; architecture-or-implementation;
integration-or-conformance for later provider qualification.

TURNLOCK product-semantic impact: none.

Formal Gate A subject S / review protocol P impact: none.

New TL-INV, assurance claim, formal model, or checked evidence: none.
```

## Decision

### 1. Keep three independent propositions

The following are never aliases:

1. **Current formal Gate A** is the verdict derived by the accepted assurance
   authority from the actual currently governed repository artifacts, subject,
   protocol, and evidence. A prior runner result does not establish it.
2. **GateAQualification** is a mechanically admitted qualification of an exact
   immutable `CandidateRevision` against the applicable, provenance-bound Gate A
   assurance and review contracts. It does not establish Git publication.
3. **Runner `GATE-A-READY`** is one terminal `GateARun` outcome attesting a
   completed, evidence-bound v1 workflow for one exact qualified candidate and
   its exact confirmed, validated published representation.

A consumer requiring present-time formal Gate A readiness MUST re-evaluate the
current repository under the existing assurance authority. It MUST NOT promote
a historical runner `GATE-A-READY` result into a current-repository verdict.

### 2. Retain the v1 end-to-end publication obligation

Runner `GATE-A-READY` requires all existing controller preconditions and at
least the following mutually bound positive facts:

- an exact qualified `CandidateRevision` C with its admitted `GateAQualification`,
  semantic subject S, review protocol P, and required provenance;
- one currently applicable authorized `PublicationIntent` I for an exact
  authoritative repository and fully qualified target ref R, mapping C to one
  exact successor Git commit and tree identity T;
- a qualifying positive observation that the designated external R equaled
  exact T (both commit and tree identities) at one identifiable actual remote
  observation occurrence, here denoted `t_pub`;
- an exact `PublicationConfirmationRef` and the unique satisfied disposition
  for I's publication obligation, admitted under the controlling M2 contract;
- a `PublishedRepositoryViewRef` of the exact authorized T that passes the
  existing bound M6 post-publication mechanical validation, with that passing
  fact admitted before the terminal M2 ready fact;
- the existing requirements that the run is not semantically terminal in an
  incompatible way and that no outstanding blocker or obligation remains.

The remote observation is a positive claim about an actual observation
occurrence, not merely a matching content-addressed observation value. Its
occurrence and authority proof must be qualified through the responsible
provider and dependency contracts. This ADR does not invent such a proof.

This decision does not replace `WorkItem` satisfaction contracts or infer them
from a generic terminal Execution. Those exact result-class and WorkItem
admission rules remain construction responsibilities.

### 3. Bind the result to an observation, not perpetual remote currentness

At `t_pub`, R must have been positively observed equal to T. Its publication
confirmation and subsequent passing M6 validation are bound to that immutable
T. The terminal run result asserts the existence and lawful admission of those
facts. It does not claim that R equals T at the later M2 commit, process exit,
CLI-result read, or any other future instant.

A permitted ordinary-writer fast-forward `T -> V` after `t_pub` does not
retroactively make the historical T-bound runner completion false. It can,
however, change whether the **current repository V** satisfies formal Gate A.
Any such current-repository verdict must be recomputed under the accepted
assurance authority for V, rather than borrowed from T's runner result.

Neither a fresh remote recheck nor any elapsed-time bound creates an atomic
GitHub/SQLite transaction. No global live-ref lock, perpetual surveillance,
retroactive revocation, or currentness boolean is introduced by this ADR.

The logical ordering is positive qualification of C, qualified publication
observation of T, passing validation of the immutable published representation,
and terminal ready admission. Existing exact currentness and provenance guards
at each admission remain mandatory; this ADR does not select a new clock rule.

### 4. Do not require historical mutation authorship for state satisfaction

Satisfying the runner's publication obligation concerns an exact authorized
published state and all applicable effect-safety and provenance conditions. It
does not, by itself, require proof that the runner's particular armed Execution
E was the actor that performed the target-ref mutation.

Consider indistinguishable histories after loss of E's response:

- H1: E performed the authorized guarded P-to-T update; its response was lost.
- H2: E did not perform it; another eligible writer published the exact T.

A later positive observation of R=T establishes the same target-state
proposition in both histories. It establishes neither `PROVEN-COMPLETED(E)` nor
`PROVEN-NOT-EXECUTED(E)` and cannot be used to fabricate an E-specific
captured result or publication non-application proof.

This actor-neutral outcome meaning does **not** license automatic progression
when an armed E might still have a relevant external effect. The current
post-Arm recovery and blocker rules, including NIB-S GI-65, GI-75, GI-79, and
GI-83, remain enforced until a separately accepted construction contract
provides a positive, complete proof of residual-effect closure and a distinct,
authoritatively admitted publication-state-satisfaction pathway. Observing T
alone is never that proof. A new pathway cannot masquerade as pre-Arm
`already-current` or reinterpret M8 historical recovery results.

The existing before-Arm `already-current` realization already admits state
confirmation without a mutating Execution. It is a precedent for separating
state from authorship, not a waiver of post-Arm guards.

### 5. Separate controller policy from shared repository governance

The selected v1 runner completes an end-to-end qualification, publication, and
validation workflow. Keeping repository-control M7 within that one runner is a
bounded construction arrangement, not a product assertion that hostile review
intrinsically owns Git ref mutation. A separately qualified publisher could
realize the same policy only after an explicit future construction decision
preserving all exact authority, immutable identity, effect recovery, blocker,
and post-publication validation conditions.

TURNLOCK retains its consumer-specific Gate A assurance and runner decisions.
The immutably bound proto-ring provider retains applicable generic repository
governance, including the Authoritative Ref Monotonicity contract for ordinary
writers. That contract does not supply exact-old CAS, pre-publication
Authoritative State Admission, proof of a remote read occurrence, or E-specific
historical outcome truth. No unqualified provider or force-like transport
fallback is authorized.

## Counterexamples and required interpretations

- **T published; ordinary writer later advances T to V before READY.** The
  terminal runner result can attest the prior T publication and validation,
  but cannot assert current formal Gate A readiness of V.
- **A third party published exact T; E's response is lost.** T equality alone
  establishes no E-specific execution truth or safe permission to progress.
  Post-Arm satisfaction remains blocked unless future accepted residual-effect
  and admission contracts positively establish its legality.
- **T is locally cached but no actual qualified remote read happened.** No
  qualifying publication-occurrence witness exists; the runner cannot claim
  terminal success from that artifact.
- **T is qualified but never published.** `GateAQualification` alone is
  insufficient for runner `GATE-A-READY` under the selected v1 policy.
- **T is published but M6 post-publication validation fails.** No
  `GATE-A-READY`; use the already accepted failure, blocker, or correction
  contract, never an invented terminal result.
- **Protection is bypassed, reconfigured, or otherwise unqualified.** A future
  residual-effect proof relying on monotonicity cannot claim validity outside
  its explicitly qualified environmental threat model.

## Consequences

- The immutable runner result and the current-repository formal Gate A verdict
  have separate temporal scopes and independent authority.
- End-to-end publication and bound validation remain mandatory for runner v1
  `GATE-A-READY`; no candidate-only completion shortcut is admitted.
- Exact target state and historical E outcome remain separate propositions.
- Actor-neutral satisfaction is selected as a controller outcome meaning, but
  its post-Arm realization remains blocked on separately accepted positive
  effect closure, observation occurrence, authoritative admission, and blocker
  disposition contracts.
- This ADR does not change the TURNLOCK product specification, any `TL-INV`,
  the formal-assurance graph, Gate A semantic subject S, protocol P, or any
  existing reviewed evidence.
- Existing published NIBs are not silently reinterpreted or rewritten. The
  responsible follow-up must synchronize any changed interfaces/invariants
  explicitly before implementation or GREEN.

## Rejected alternatives

1. **Report runner ready after candidate qualification only.** Rejected for v1:
   it conflates candidate qualification with confirmed publication and violates
   the selected end-to-end runner result.
2. **Make a completed run's ready result a perpetual live-remote equality
   promise.** Rejected: a terminal historical fact cannot establish unbounded
   mutable-ref currentness or replace fresh current-repository assurance.
3. **Infer E's successful historical execution from current T.** Rejected:
   H1/H2 have identical observed target state but different historical actors.
4. **Use post-Arm already-current or a synthetic recovered result.** Rejected:
   it bypasses existing execution-truth and active recovery constraints.
5. **Require E-specific historical authorship as an unconditional prerequisite
   to state-oriented publication satisfaction.** Rejected at the runner outcome
   level: it is not required by ADR-041/045 and would conflate two distinct
   propositions. Positively established E-specific provenance remains valid
   evidence when independently available.
6. **Delegate runner readiness to proto-ring or an unqualified Git provider.**
   Rejected: shared governance and exact Turnlock qualification have different
   authorities, and a provider name is not conformance evidence.

## Non-decisions

This ADR does not define, admit, or implement:

- M2's post-Arm state-satisfaction mutation or closure object schemas;
- a Q occurrence ledger or the selected remote-read and CAS mechanism;
- the exact complete armed-Execution risk-set query;
- M8 blocker disposition, `UNRESOLVABLE` treatment, or polling schedules;
- WorkItem satisfaction, late execution outcome auditing, or crash migrations;
- a Git Dependency Contract or actual GitHub writer/protection qualification;
- a new current-repository Formal Gate A policy or Authoritative State Admission;
- a new hostile-review protocol, model-check result, or `GATE-A-READY` assertion
  for any actual repository revision;
- a generic reusable publication/SCOPE IR or TURNLOCK runtime primitive.

Those questions retain their existing owning authorities and explicit decision
or qualification gates.

## Required follow-up

Issue #78 retains the independent M7 primitive/ownership, Git transport,
conformance, construction-coherence, and review work. Issue #87 must close the
post-Arm progression proof/admission and all competing recovery/WorkItem and
observation-freshness cases without bypassing this ADR. Issues #88, #89, #90,
and #91 retain their exact target/writer, occurrence, cross-module, and Git DC
responsibilities. Test and review gates #32 and #33 remain distinct.

Synchronize any future accepted changes to NIB-S, M1, M2, M6, M7-B, M8 and
NIB-T only after their owning decisions are closed. Never treat a proposal,
Issue comment, source citation or passing repository-integrity check as actual
historical Execution recovery, external publication evidence, formal Gate A
readiness, or a reason to enter GREEN.
