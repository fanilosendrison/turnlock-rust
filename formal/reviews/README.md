# Hostile semantic-review evidence

This directory stores durable evidence of executed hostile semantic-review
campaigns over TURNLOCK formal-assurance artifacts.

The existence of `review-evidence.schema.json` is **not** evidence that any
review occurred. The absence of a review record means that no review evidence
exists. Review requirements are satisfied only by records that exist, validate,
and are current for both the exact reviewed subject and the current hostile
review protocol. Review evidence is a distinct evidence class from TLC or other
mechanical checker evidence.

Hostile review is adversarial falsification, not majority voting. A single
surviving valid material objection blocks acceptance of the reviewed semantic
link until it is resolved or refuted, regardless of how many reviewers approved.
Review evidence never constitutes mathematical proof of natural-language/formal
equivalence; the strongest valid conclusion is bounded reviewed semantic
correspondence under the executed review protocol.

The evidence contract is `review-evidence.schema.json` schema version `5.0`.
Version 5.0 is a breaking contract; no compatibility branch for schema 4.0 exists. No real campaign evidence exists, so no campaign evidence migration is required.

## Dual currentness: semantic subject and review protocol

Gate A has two independent identities:

```text
S = Gate A semantic subject identity
P = Gate A hostile-review protocol-bundle identity
```

A campaign is current for Gate A only if it is current for BOTH:

```text
(S, P)
```

This directory owns hostile-review evidence and protocol artifacts. It is not
TURNLOCK product authority, and the protocol bundle is evidence and protocol
authority only.

## Protocol bundle

The current hostile-review protocol is a content-addressed canonical JSON bundle:

```text
formal/reviews/protocols/*.json
```

The current bundle is pointed to by
`formal/verification.yaml policy.hostile_review.current_protocol_bundle`. The
bundle declares its schema version, protocol identity, review class, canonical
prompt artifacts, canonical schema artifacts, reviewer profiles, and protocol
policies. A protocol change requires a new content identity `P`. A review made
under a stale `P` does not satisfy current Gate A.

The current bundle is `gate-a-campaign-protocol-v3`. It cryptographically links the immutable v2 bundle as its predecessor, and v2 links the immutable v1 bundle; predecessor bundles and their referenced prompts and schemas are recursively checked. Published versioned protocol bundles and referenced prompt/schema artifacts are append-only by path and bytes. The protocol history is `v3 -> v2 -> v1`; v1 and v2 are immutable historical bundles.

The published v1, v2, and v3 bundles intentionally declare:

```json
"reviewer_profiles": []
```

The empty registry is intentional. No real Gate A campaign can qualify until a
later protocol snapshot explicitly adds eligible profiles, and that profile
change necessarily changes `P`.

## Campaign artifacts

A campaign separates, conceptually and durably:

```text
canonical review packet
canonical review prompt
protocol bundle
reviewer profiles
reviewer execution metadata
sealed raw reviewer output
execution receipts
normalized campaign evidence
adjudication / challenge evidence
re-adjudication evidence for stale-protocol findings
```

The review packet, the prompt, the protocol bundle, the raw reviewer output, and
any challenge output are repository-relative artifacts content-addressed by
SHA-256. A raw output becomes SEALED when its bytes are fixed and hashed. After
sealing there is no edit, no cleanup, no rewriting, and no finding deletion.
Normalization and adjudication are recorded elsewhere in the campaign evidence.

## Canonical Gate A review packet

The Gate A review packet is a self-contained canonical JSON file:

```text
formal/reviews/packets/*.json
```

It contains the exact `subject_payload`, the exact subject identity, and the
exact UTF-8 authority contents. Packet validation recomputes the subject SHA from
`subject_payload` and each embedded authority SHA from its UTF-8 contents. The
packet subject must equal the unique Gate A derived subject declared by the
review record. A stale historical packet validates against its own embedded
reviewed subject, not against current repository semantics. Materiality and refutation challenges additionally use a canonical challenge packet that embeds this exact parsed review packet and the exact challenged candidate; the challenge receipt `input.packet` must be byte-identical to the declared challenge packet.

## Reviewer profiles and qualification

`frontier-llm` is not an arbitrary per-execution assertion. Each reviewer
execution references a profile owned by the campaign protocol bundle. Each
profile declares exactly:

```text
profile_id
provider
request_model
frontier_eligible
identity_resolution
```

`frontier_eligible` MUST be exactly `true` for a profile to qualify. The runner
and the checker never invent or auto-promote a profile. A model/profile not
listed in the campaign protocol bundle does not qualify.

## Model identity resolution

Model identity is exactly:

```text
(provider, model, model_version)
```

`model_version` is derived from evidence according to the selected profile.
Allowed resolution kinds are exactly `provider-reported` and
`pinned-request-model`:

```text
provider-reported:
  the qualified attempt provider_model must be non-empty
  model_version = qualified attempt provider_model

pinned-request-model:
  request_model_is_immutable_version must be true
  model_version = profile.request_model
```

No runner-supplied alias, `latest`, or unresolved alias is admissible.

Independent-reviewer counting enforces both the distinct full tuple
`(provider, model, model_version)` and the distinct effective identity
`(provider, model_version)`. Two aliases resolving to the same effective
provider/model version therefore count once and cannot inflate
`minimum_independent_reviewers`.

## Structured raw reviewer outputs

Initial hostile reviewer outputs are structured JSON artifacts:

```text
formal/reviews/raw/*.json
```

The exact model-produced raw bytes are sealed before interpretation. The raw
format contains exactly `raw_review_schema_version`, `objective_assessments`,
and `findings`. Each of the 14 Gate A attack objectives appears exactly once in
`objective_assessments`, and every objective/finding reference is reciprocal.

Reviewers do not emit materiality, status, disposition, confidence, severity,
recommendation, preferred fix, Gate A readiness, or decision-required markers.

## Sealed retry and attempt preservation

The protocol distinguishes technical/provider transport attempts internal to one
LLM call from completed LLM calls used as protocol attempts.

If a completed model response exists, its exact bytes are sealed and retained
even when its JSON is protocol-invalid. A schema-invalid completed response may
cause a fresh retry using the exact same semantic input. A valid semantic
response is never retried merely because its content is inconvenient, and no
model-shopping is permitted after a semantically valid result.

Every completed protocol attempt is recorded in the execution receipt. Attempt validity is checker-derived from sealed output, not runner labels.

Protocol v3 recognizes exactly two execution-validation classes. The deterministically validated roles are exactly:

```text
initial-reviewer
challenge
```

For these roles, `technical-failure` has no raw output; `protocol-invalid` must actually fail deterministic validation; and `qualified` must pass it. Deterministic `protocol-invalid` retry is permitted only for these roles.

The seven roles without a deterministic output validator are exactly:

```text
materiality-assessor
refutation-builder
discovery-classifier
derivation-builder
decision-necessity-challenger
repair-synthesizer
decision-projection
```

For these roles, `protocol-invalid` is forbidden. Any number of `technical-failure` attempts may precede the one terminal completed response, which MUST be `qualified`, MUST be final, and admits no later attempt. `qualified` for an unvalidated role means only the unique admitted completed response of that execution, not semantic correctness. The first protocol-valid completion remains terminal and is the final attempt.

## Execution receipts

Every cognitive LLM call participating in the campaign has its own
content-addressed execution receipt:

```text
formal/reviews/executions/*.json
```

The receipt records its execution identity, role, reviewer profile, protocol
bundle SHA-256, prompt and packet inputs, isolation declarations, runtime
metadata, request provider/model, every attempt, the qualifying attempt, and the
evidence-derived resolved identity. Required constants are:

```text
isolated_context = true
cross_reviewer_visibility_before_seal = false
tools_enabled = false
```

Only `initial-reviewer` receipts count toward
`minimum_independent_reviewers`. A challenge is a NEW LLM execution and never
pretends that an earlier reviewer execution was the challenge execution.

The receipt is runtime-transport-neutral. It does not require `llm-runtime`; a
future campaign runner may use `llm-runtime`, but the evidence contract does not
give it authority.

## One-to-one normalization

For the current review-evidence contract (schema 5.0):

```text
one raw finding -> exactly one normalized finding
```

No semantic merge, no semantic deduplication, and no one-to-many mapping exists.
A normalized finding declares exactly one source, and the normalized
`statement`, `argument`, and `counterexample` equal the exact corresponding raw
finding values. Normalization adds global identity and adjudication metadata
only.

## Materiality and the materiality challenge

Materiality remains derived from the seven explicit impact axes. If any axis is
true, the finding is material.

If all seven axes are false, the non-material conclusion is not accepted merely
because one assessor says so. It requires a fresh hostile materiality challenge
bound to the exact candidate materiality assessment through
`challenged_materiality_sha256`. The challenge attempts all seven axes. Its
output contains objections, not a pass/fail verdict. Non-material is admissible
only when the validated challenge output contains:

```text
objections = []
```

A material finding must carry `materiality.challenge = null`.

## Refutation and hostile challenge

A refutation must choose exactly one `ground`:

```text
premise-false
target-misidentified
counterexample-outside-authority
consequence-does-not-follow
already-accounted-for
```

It must contain the attacked premise or inference, evidence references, an
argument, and a counterexample disposition when the finding contains a
counterexample. Reviewer majority, another reviewer not finding the defect,
author intent, preferred interpretation, difficulty reproducing, and a future
TLA+ implementation are never refutations.

Every refutation of a material finding requires a durable hostile challenge.
The challenge is bound to the exact canonical
`hostile-refutation-challenge-v1` subject through
`challenged_refutation_sha256`, using a `challenge`-role execution receipt whose
qualifying output is the challenge output.

The challenge result is derived mechanically:

```text
challenge objections == []
=> closure survived challenge
```

Any challenge objection means the refutation does not currently close the
finding. Challenge output carries no approval/rejection boolean. The current
review-evidence contract does not contain `surviving_material_argument` or
`challenger_execution_id`. A challenge
is falsification, not voting; the challenger receives only the canonical
challenge prompt and packet, and no incidental findings are allowed in challenge
output v1.

The maximum closure revisions is exactly `1`. If a revised closure candidate
still receives objections, that closure path fails.

## Failure to refute is not proof

```text
failure to establish a valid refutation
!=
proof that the finding is true
```

A material finding stays `open` unless another branch is positively established
and challenged. `DECISION-REQUIRED` is reserved for genuine product-semantic
underdetermination or a genuine unresolved product-authority conflict. When
none of a valid refutation, a uniquely derived correction, no normative impact,
genuine product underdetermination, or a genuine authority conflict can be
established, the correct external outcome is `OPERATOR-ACTION-REQUIRED`.

The normal external outcomes of the campaign runner contract are exactly:

```text
GATE-A-READY
DECISION-REQUIRED
OPERATOR-ACTION-REQUIRED
```

## Stale-protocol finding re-adjudication

A protocol change never erases a finding from a campaign over the same semantic
subject. For a stale-protocol campaign whose reviewed semantic subject is still
the current `S`:

- its raw findings remain durable;
- an old non-material conclusion is not sufficient under the new protocol;
- an old refutation is not sufficient under the new protocol;
- every stale-protocol finding must be re-adjudicated under the current protocol
  before it can cease affecting Gate A.

Re-adjudication references the exact source review and finding, binds the exact
substantive finding through `source_finding_sha256` using the canonical
`hostile-finding-subject-v1` hash, and provides current-protocol materiality,
status, disposition, and challenge evidence. Historical raw output is never
edited, and stale review records are never deleted or ignored.

## Subject kinds

Review evidence identifies its reviewed subject with one of two exact shapes:

```text
artifact subject
= exact bytes of a repository artifact

derived subject
= mechanically canonicalized semantic review scope whose identity is independent
  of unrelated physical-file changes
```

`gate-a-assurance-decomposition-v1` is the only current derived subject selector.

Its dependency set is:

```text
normative specification bytes
ADR-015 bytes
ADR-041 bytes
ADR-040 bytes
manifest schema_version/project
formal semantic domain declarations
behavioral modalities
assurance domains
83 claim contents and provenance
42 normative coverage mappings
```

Its explicit exclusions are:

```text
formal_realizations
hostile-review adequacy policy
hostile-review protocol bundle
current_protocol_bundle
mechanical-evidence policy
readiness-gate declarations
generated docs
review records
result records
Git commit identity
```

Changing only hostile-review protocol policy, including
`current_protocol_bundle`, MUST NOT change `S`.

## Unambiguous Gate A subject identity

For an assurance-decomposition review record that declares
`gate-a-assurance-decomposition-v1`, exactly one Gate A derived subject is
allowed. Duplicate or multiple distinct Gate A subjects are invalid evidence;
additional artifact subjects remain permitted.

The canonical Gate A review packet must equal the unique Gate A derived subject,
and Gate A currentness uses that same unique subject. The enforced identity chain
for a current qualifying campaign is exactly:

```text
packet.subject
==
unique record Gate A derived subject
==
current Gate A semantic subject S
```

## Symlink prohibition

No review-evidence artifact path may traverse a symlink, including a symlink
that remains inside the repository. Every path component from the resolved
repository root to the referenced artifact must be a non-symlink filesystem
object, and the artifact itself must be a regular file. This applies to the
review packet, the prompt, the protocol bundle, execution receipts, raw
reviewer output, and any challenge or adjudication output.

## Operational independence

Independence is **operational independence**, not a probabilistic independence
claim about models.

A reviewer execution counts toward the declared
`minimum_independent_reviewers` only when it:

- analyzes the same exact reviewed subject;
- uses the same canonical review packet;
- uses the same canonical review prompt;
- executes in a separate context;
- has no direct or indirect access to the outputs, findings, or adjudications of
  any other reviewer before its own raw output is sealed;
- belongs to a qualifying protocol reviewer profile;
- has an evidence-derived distinct effective model identity.

## Attack coverage per execution

Every reviewer execution that counts toward the Gate A campaign must
individually cover the complete attack-objective set declared by:

```text
formal/verification.yaml
policy.hostile_review.required_attack_objectives.assurance-decomposition
```

Aggregated campaign coverage is not sufficient. A qualifying execution that
omits an objective is not qualifying, even when another execution covered that
objective.

## Gate A review adequacy

Gate A requires a current assurance-decomposition campaign that:

- reviews the current exact Gate A semantic subject `S`;
- binds the current exact protocol bundle `P`;
- is structurally and referentially valid;
- uses a self-contained canonical Gate A review packet whose recomputed subject
  SHA matches its embedded `subject_payload` and whose subject equals the
  unique subject declared by the review record;
- references only existing packet, prompt, protocol, receipt, raw, and
  challenge artifacts whose bytes match their declared SHA-256 and whose paths
  traverse no symlink;
- has at least `minimum_independent_reviewers` distinct
  `(provider, model, model_version)` model identities and at least
  `minimum_independent_reviewers` distinct effective `(provider, model_version)`
  identities;
- covers the complete required attack-objective set in each qualifying
  execution;
- uses the same canonical packet and the same canonical prompt across
  qualifying executions;
- declares isolated contexts and no cross-reviewer visibility before sealing;
- represents every declared raw finding exactly once in the normalized ledger
  with exact raw value equality;
- has no current material `open`, `routed`, or `resolved` finding;
- carries a valid zero-objection materiality challenge for every non-material
  finding and a valid zero-objection refutation challenge for every material
  `refuted` finding;
- re-adjudicates every stale-protocol finding over the current `S` under the
  current protocol.

All current assurance-decomposition review records for the exact current subject
participate in surviving-finding evaluation. One material `open`, `routed`, or
`resolved` finding in any current review blocks Gate A even if another review is
clean. No majority vote can override the finding.

A changed semantic subject requires a full new review campaign over the new
bytes. A changed protocol bundle requires current re-adjudication of every
stale-protocol finding over the current subject.

## Path conventions

Campaign artifacts use these repository-relative conventions:

```text
formal/reviews/packets/*.json
formal/reviews/challenge-packets/*.json
formal/reviews/prompts/*.md
formal/reviews/protocols/*.json
formal/reviews/schemas/*.json
formal/reviews/executions/*.json
formal/reviews/raw/*.json
formal/reviews/adjudications/*.json
formal/reviews/challenges/*.json
```

Their absence is normal while no real hostile-review campaign has been executed;
an empty directory is a valid state and is not evidence of a review.

## Repository integrity

Malformed JSON/YAML review evidence is a repository-integrity failure and is not
silently ignored. A non-mapping review file is also an integrity failure.

Any review-evidence integrity failure forces Gate A BLOCKED with the reason
`hostile review evidence integrity failure`. It can never coexist with a Gate A
READY summary.
