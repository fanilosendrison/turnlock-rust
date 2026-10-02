---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Define deterministic minimum-effective hostile-reviewer acquisition"
id: "ADR-053"
status: "accepted"
date: "2026-10-02"
decision_body_sha256: "3b839d4e919214002767ca53d858a4a508032ac8d8307d3cea2c1d22cbf2bdaa"
relation_completeness: "complete"
relations:
  clarifies: []
  amends:
    - "ADR-042"
    - "ADR-045"
  supersedes: []
  confirms:
    - "ADR-046"
    - "ADR-047"
    - "ADR-048"
    - "ADR-049"
governs:
  - "Gate A initial-reviewer acquisition policy"
  - "Deterministic reviewer-profile acquisition order"
  - "Minimum-effective independent-reviewer acquisition"
  - "Qualified reviewer identity collision expansion"
  - "Reviewer-pool exhaustion outcome"
---

# ADR-053: Define deterministic minimum-effective hostile-reviewer acquisition

## Context

ADR-042 requires multiple independent hostile reviewers. ADR-045 owns reviewer
profiles, static reviewer-profile qualification, and evidence-derived model
identity. ADR-046 and ADR-047 prohibit retry and model shopping after a
semantically admitted completion. ADR-049 establishes one logical receipt per
cognitive WorkItem, with retries represented as attempts in that receipt.

Existing authority does not determine reviewer acquisition when the statically
qualifying registry is larger than the independent-reviewer minimum. It does not
uniquely determine which profiles must execute, their acquisition order, how
acquisition expands after qualified executions resolve to duplicate effective
identities, whether operational failure permits substitution, or what happens
when the eligible pool is exhausted below the effective minimum.

Different otherwise-valid choices can execute different models and therefore
produce different findings. This is an assurance-architecture
underdetermination, not TURNLOCK product-semantic underdetermination.

## Discovery classification

```text
decision-required at the hostile-review assurance-architecture layer;
resolved by this ADR;
no TURNLOCK product-semantic impact
```

## Decision

### Registry membership is eligibility

```text
reviewer_profiles
=
complete protocol-owned registry of profiles that may qualify

membership in reviewer_profiles
!=
obligation to execute that profile
```

A profile can be executed only when it is registered and statically qualifying.
The protocol does not require execution of every qualifying profile.

### Acquisition target

The acquisition target is exactly `minimum_independent_reviewers` from the
existing hostile-review policy in `formal/verification.yaml`. The numeric
minimum remains outside protocol identity P exactly as before and MUST NOT move
into the protocol bundle.

Runtime acquisition satisfies the target only through distinct effective
identities:

```text
(provider, model_version)
```

Existing full-tuple validation remains:

```text
(provider, model, model_version)
```

Distinct effective identities necessarily imply distinct full tuples. Therefore
minimum-effective acquisition is sufficient for acquisition progression while
the canonical checker continues enforcing both counts.

### Acquisition policy belongs to P

Protocol identity P commits exactly:

```text
policies.reviewer_acquisition.mode
policies.reviewer_acquisition.profile_order
```

The only v1 mode is:

```text
minimum-effective-independent-v1
```

`profile_order` is a total acquisition order and an exact permutation of every
`reviewer_profiles[*].profile_id` declared by the same protocol bundle. It
contains each profile ID exactly once. For an empty registry it is exactly `[]`.

The order is procedural acquisition authority only. It is not reviewer quality
ranking, provider preference semantics, model-family preference semantics,
severity ranking, or confidence ranking. Reviewer slots and reviewer classes are
not introduced. Acquisition order MUST NOT be derived from lexical `profile_id`
order.

### Static qualification

Static qualification remains exactly:

```text
frontier_eligible == true

AND

(
  identity_resolution.kind == "provider-reported"

  OR

  (
    identity_resolution.kind == "pinned-request-model"
    AND
    request_model_is_immutable_version == true
  )
)
```

`qualifyingReviewerProfileIds` remains the complete qualifying set sorted by
`profileId` in unsigned ASCII ascending order. That canonical set order is not
acquisition order. The acquisition sequence is `profile_order` filtered to
statically qualifying profiles.

### Statically known effective identities

For a statically qualifying `pinned-request-model` profile, its statically known
effective identity is `(provider, request_model)` because
`request_model_is_immutable_version == true`.

For a `provider-reported` profile, the statically known effective identity is
unknown. No model version may be guessed, aliased, inferred from request model,
or deduplicated before qualified evidence exists.

### Static feasibility

Before creating an executable ReviewCampaign, compute:

```text
uniqueKnownPinnedEffectiveIdentities
=
distinct (provider, request_model)
across statically qualifying pinned-request-model profiles

unknownProviderReportedCapacity
=
number of statically qualifying provider-reported profiles

maximumStaticallyPossibleIndependentReviewers
=
|uniqueKnownPinnedEffectiveIdentities|
+
unknownProviderReportedCapacity
```

This is an optimistic maximum only. When
`maximumStaticallyPossibleIndependentReviewers < minimum_independent_reviewers`,
reviewer prerequisites are unavailable. No ReviewCampaign is created. The
existing campaign-authority operational path and `OPERATOR-ACTION-REQUIRED`
apply. The current immutable P cannot be expanded in place, and there is no
same-run resolution contract.

### Deterministic acquisition rounds

For a campaign, let:

```text
E
=
set of effective identities established by already-qualified initial-reviewer
receipts in that campaign

N
=
minimum_independent_reviewers

deficit
=
N - |E|
```

If `deficit <= 0`, create no additional initial-reviewer WorkItem. Otherwise,
select the next round from protocol acquisition order filtered to statically
qualifying profiles and excluding profiles already selected for the campaign.

Iterate in exact protocol acquisition order. For each not-yet-selected profile:

```text
if pinned-request-model:
    K = (provider, request_model)

    skip it when:
        K is already in E
        OR
        K is already reserved by another pinned profile selected in the same round

if provider-reported:
    do not pre-collapse it with any other profile
```

Select profiles until the round contains exactly `deficit` profiles or no
further selectable profiles remain. Provider-reported profiles are
optimistically treated as potentially adding one effective identity until
qualified evidence proves otherwise.

All WorkItems selected for one round become required campaign work. The next
round MUST NOT be derived until every selected WorkItem in the current round has
either produced its one complete qualified execution receipt or entered an
existing operational/recovery blocker path that stops automatic campaign
progression.

Network timing, provider latency, callback order, scheduling interleaving, and
completion order MUST NOT alter which profiles belong to a round.

### Qualified identity collision

After every WorkItem in a successful round has a complete qualified receipt:

1. preserve every receipt;
2. preserve every raw output;
3. preserve every finding from every executed reviewer;
4. recompute E from the exact receipt `resolved_identity` values.

If a qualified reviewer resolves to an effective identity already present in E,
its evidence remains fully valid and retained but contributes no additional
independent-reviewer count. If the target remains unmet, derive the next
deterministic round. A duplicate identity is neither a failed review nor
discarded evidence.

### Content independence

Reviewer selection and expansion may depend only on:

```text
current protocol P
minimum_independent_reviewers
static reviewer-profile facts
profiles already selected
qualified receipt existence
qualified resolved identities
statically known pinned effective identities
```

They MUST NOT depend on finding count, finding text, materiality, review
severity, whether a review is favorable or unfavorable, reviewer confidence,
agreement or disagreement with another reviewer, or the desired Gate A outcome.
No model shopping is introduced.

### Selected WorkItem failure is not profile fallback

Once a reviewer profile is selected into an acquisition round, its WorkItem is
required campaign work and existing retry/recovery semantics apply. When its
automatic retry policy is exhausted without qualification, the runner MUST NOT
select another reviewer profile as an automatic substitute, treat the failed
WorkItem as a mere acquisition miss, or erase the outstanding campaign work.

The existing path applies:

```text
M5 cause
→ M8-B materialization
→ M2 admission
→ OPERATOR-ACTION-REQUIRED
```

Reaching the independent-reviewer minimum through other WorkItems does not
silently cancel a selected WorkItem that has not completed lawfully.

### Eligible-pool exhaustion

After successful qualified rounds, when `|E| < N` and no unselected statically
qualifying profile remains capable of selection under the acquisition algorithm,
automatic acquisition is exhausted.

This means operational inability to establish required assurance under current
P. It is not `DECISION-REQUIRED`, technical-failure relabeling, proof that any
finding is true, permission to add an unregistered profile, or permission to
mutate P inside the current run.

M5 produces exact assurance-domain non-recovery cause material. M8-B alone
materializes the OperationalBlocker and Operator Action Request. For this cause:

```text
resolutionContracts = []
```

Changing the reviewer registry or order requires a new protocol snapshot and a
new P; the current GateARun may not mutate its bound P in place.

### Evidence-level conformance

For protocol-v5 review evidence, the canonical Python checker mechanically
verifies that the initial-reviewer executions in a completed review record are
exactly compatible with `minimum-effective-independent-v1`.

The checker reconstructs the expected selected profile sequence from the current
`minimum_independent_reviewers`, protocol `reviewer_profiles`, protocol
`reviewer_acquisition.profile_order`, validated execution receipts, and resolved
identities.

For protocol v5, one reviewer profile maps to at most one logical
initial-reviewer execution receipt per ReviewCampaign. Protocol retries remain
attempts inside that receipt.

The checker rejects an initial-reviewer profile not selected by the deterministic
algorithm, an extra initial-reviewer execution after the minimum was established,
duplicate logical initial-reviewer executions for one profile, or a missing
reviewer execution required by the deterministic algorithm for a completed
review record.

This acquisition-conformance rule applies only to protocol v5 and later protocol
versions that explicitly adopt it. It does not apply retroactively to v1-v4.

### Protocol evolution

Publish review-protocol-bundle schema version 5 and
`gate-a-campaign-protocol-v5`. Protocol v5's exact predecessor is protocol v4.
Protocol v5 binds the exact new v5 protocol-bundle meta-schema and continues to
bind the existing immutable review-evidence-v5 meta-schema.

Published protocol v1-v4 artifacts and published old meta-schemas remain
byte-identical and immutable.

### Product semantics remain unchanged

Explicitly:

```text
no TURNLOCK product semantic change
no TL-INV change
no TL-CLAIM change
no normative coverage change
no executable formal model
no review-evidence schema change
no execution-receipt schema change
Gate A semantic subject S unchanged
ADR-053 is not added to formal/verification.yaml authority.architecture_decisions
ADR-053 is not added to authority.abstraction_constraints
```

## Alternatives considered

- **Execute every qualifying reviewer:** Rejected because registry membership would silently become assurance-work obligation.
- **Execute exactly N profile IDs:** Rejected because profile count does not establish effective independence.
- **Profile-ID lexical ordering:** Rejected because canonical naming and ordering must not become hidden acquisition preference.
- **Reviewer slots or classes:** Rejected because the assurance requirement is a global effective-identity cardinality and provider or family diversity is not the universal independence definition.
- **Timing-driven expansion:** Rejected because network and scheduler timing must not alter campaign evidence selection.
- **Semantic-result-driven expansion:** Rejected as model shopping.
- **Fallback after selected-WorkItem retry exhaustion:** Rejected because it bypasses accepted retry, recovery, and operational-blocker semantics.

## Consequences

### Benefits

- Reviewer acquisition is deterministic, protocol-owned, minimum-effective, and content-independent.
- Campaign evidence selection is reconstructible from immutable authority and qualified receipts.
- Qualified identity collisions preserve evidence while permitting exact expansion.
- Existing retry, recovery, operational-blocker, and evidence semantics remain intact.

### Costs and obligations

- Protocol v5 and its v5 protocol-bundle meta-schema become immutable published artifacts.
- The canonical checker must validate v5 bundle shape and acquisition conformance while preserving v1-v4 interpretation.
- Construction contracts across M6, M3, M5, and M2 must consume the new policy without moving ownership.
- Static infeasibility and runtime pool exhaustion require exact operator-action paths.
- Every selected WorkItem remains required work even if other reviews establish the minimum.

## Verification obligation

Mechanical coverage is required for:

```text
v5 meta-schema selection
v5 predecessor chain
v5 meta-schema bindings
profile_order uniqueness
profile_order exact permutation of reviewer_profiles
protocol v5 canonical bytes/hash
no mutation of v1-v4 artifacts
review evidence remains schema 5.0
execution receipt remains schema 3.0
v5 acquisition-conformance simulation
duplicate effective-identity expansion
pinned static duplicate skipping
extra-reviewer rejection after target reached
duplicate profile execution rejection
Gate A S unchanged
P changes to v5
```

## References

- `AGENTS.md`
- `formal/verification.yaml`
- `formal/reviews/README.md`
- `formal/reviews/meta-schemas/review-protocol-bundle-v4.schema.json`
- `formal/reviews/protocols/gate-a-campaign-protocol-v4.json`
- `formal/reviews/meta-schemas/review-evidence-v5.schema.json`
- `formal/reviews/schemas/execution-receipt-v3.schema.json`
- ADR-041
- ADR-042
- ADR-045
- ADR-046
- ADR-047
- ADR-048
- ADR-049
