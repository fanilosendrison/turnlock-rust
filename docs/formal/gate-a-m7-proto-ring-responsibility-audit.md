# Gate A M7 / proto-ring responsibility audit — Issue #78

**Status:** Non-authoritative, evidence-bounded construction analysis. This document is not a NIB, dependency contract, accepted ADR, hostile-review result, runtime certification, or current engineering-status dashboard. It does not authorize a change to the current runner behavior.

**Reproducible analysis baselines (2026-10-16):**

| Consumer | Exact repository state |
|---|---|
| Turnlock-Rust | [`be76128d2007eec3e3906d13c0bf00d861fcaa10`](https://github.com/fanilosendrison/turnlock-rust/tree/be76128d2007eec3e3906d13c0bf00d861fcaa10) |
| proto-ring | [`6b04ce661e86396a3f6a5d9f5ce8bc2839ac2e60`](https://github.com/fanilosendrison/proto-ring/tree/6b04ce661e86396a3f6a5d9f5ce8bc2839ac2e60) |
| Ruu | [`5d04c58170b2ce3f0e47aa0554a97906d2256492`](https://github.com/fanilosendrison/ruu/tree/5d04c58170b2ce3f0e47aa0554a97906d2256492) |

This is the analytical input to [Turnlock-Rust #78](https://github.com/fanilosendrison/turnlock-rust/issues/78), not an independent decision record. Any accepted construction change must be authored through the applicable NIB and dependency-contract processes, with version/dependency synchronization and the required independent construction review.

## 1. Problem and authority

Turnlock-Rust [ADR-051](../adr/adr-051-require-proto-ring-for-applicable-generic-repository-governance.md) mandates the pinned proto-ring provider for **applicable generic repository governance**. [ADR-052](../adr/adr-052-adopt-structured-proto-ring-governance.md) adopts its repository model, integrity, projection, and evidence-requirements facilities, while retaining Turnlock-local formal-assurance and hostile-review authority.

The active runner [NIB-S](nib-s-gate-a-campaign-runner.md) nevertheless assigns to M7 an immutable Git repository baseline, candidate construction, deterministic commit projection, exact-target conditional publication, and publication recovery. [M7-A](nib-m-gate-a-repository-control-materialization-candidate-construction.md) identifies Git dependency operations 01–19; [M7-B](nib-m-gate-a-repository-control-publication-remote-recovery.md) identifies operations 20–23.

The question is **not** whether the word "Git" appears in proto-ring, but whether a concrete M7 responsibility *implements the same generic repository-governance semantics* that the mandatory provider already owns.

Three authority domains must remain separate:

1. **Proto-ring:** consumer-independent governance, coherent local observation, integrity-evaluation semantics, projection and exact evidence-binding semantics, external authoritative-ref non-FF/non-deletion obligations.
2. **Turnlock Gate A:** current semantic subject `S`, protocol `P`, reviewer/challenge evidence, admissible correction, mechanical Gate A qualification, and interpretation of `GATE-A-READY`.
3. **Git/provider execution:** immutable commit/tree/object storage, acquiring a restorable baseline, materializing pre-authorized bytes, observing exact remote refs, and performing an authorized external transition with failure/recovery evidence.

The third category is not automatically a proto-ring-governance implementation. Conversely, placing a helper under M7 does not exempt it from ADR-051 if it actually reimplements a generic governance contract.

## 2. Existing proto-ring contracts and their limits

| Contract | Existing guarantee | Not established by it |
|---|---|---|
| [RepositoryState](https://github.com/fanilosendrison/proto-ring/blob/6b04ce661e86396a3f6a5d9f5ce8bc2839ac2e60/docs/contracts/repository-state.md) | Exact local Git worktree root, HEAD/index/filesystem observation, drift checks; coherence basis required for globally coherent reliance | Portable closure of immutable commit objects; Git push/ref mutation; a generic remote-provider identity |
| [RepositoryGovernanceState](https://github.com/fanilosendrison/proto-ring/blob/6b04ce661e86396a3f6a5d9f5ce8bc2839ac2e60/docs/contracts/repository-governance-state.md) | Exact-state-bound composition of consumer-owned governance sources | Evaluation of product/formal claims, mutation, repair, provider observation |
| [Repository Integrity](https://github.com/fanilosendrison/proto-ring/blob/6b04ce661e86396a3f6a5d9f5ce8bc2839ac2e60/docs/contracts/repository-integrity.md) | `SATISFIED/VIOLATED/UNDETERMINED`, `PASS/NON_PASS`, complete mandatory obligation set on exact governed state | Semantic Gate A qualification, correctness of a historical claim, repair or Git publication |
| [Projection Integrity](https://github.com/fanilosendrison/proto-ring/blob/6b04ce661e86396a3f6a5d9f5ce8bc2839ac2e60/docs/contracts/projection-integrity.md) | Authority/currentness of derived representations, direct-source rule | Turnlock-specific projection-byte content or authority to modify a candidate |
| [Exact Evidence Binding](https://github.com/fanilosendrison/proto-ring/blob/6b04ce661e86396a3f6a5d9f5ce8bc2839ac2e60/docs/contracts/exact-evidence-binding.md) | `MATCH/MISMATCH/UNDETERMINED` for explicit evidence class + subject + required context | Evidence trustworthiness, positive outcome, proof, qualification |
| [Authoritative Ref Monotonicity](https://github.com/fanilosendrison/proto-ring/blob/6b04ce661e86396a3f6a5d9f5ce8bc2839ac2e60/docs/contracts/authoritative-ref-monotonicity.md) | External non-FF + non-deletion protection for ordinary writers | Pre-publication admission, exact-old compare-and-swap, transport recovery or authoring the commit |
| [Shared Governance Provider](https://github.com/fanilosendrison/proto-ring/blob/6b04ce661e86396a3f6a5d9f5ce8bc2839ac2e60/docs/contracts/shared-governance-provider.md) | Mandatory reuse of every *applicable* generic governance mechanism | Transfer of consumer semantics/qualification or ownership of unrelated Git plumbing |

In particular, an exact Git commit/tree OID is **not** the opaque local `RepositoryState` identity, and a clean worktree or `Repository Integrity PASS` does **not** establish hostile-review correctness.

## 3. Complete M7 Git dependency surface

The numbers and names are taken from the two active M7 NIB-Ms, not inferred from Git CLI documentation. Each row classifies the required *operation*; any later implementation-internal governance logic must undergo a separate ADR-051 check.

| # | Operation | Required role | Ownership and overlap finding |
|---|---|---|---|
| 01 | `qualifyRuntime` | Qualify Git implementation and required capabilities | Git execution/transport; no proto-ring duplicate |
| 02 | `inspectRepositoryHead` | Inspect exact HEAD/commit/tree/format baseline | Git observation; partial conceptual overlap with local `RepositoryState`, but different governed state and purpose |
| 03 | `inspectRepositoryObjectSources` | Resolve declared object sources | Git object-acquisition plumbing |
| 04 | `inspectPushConfiguration` | Inspect local push configuration | Git configuration reading; Turnlock owns effective publication target policy |
| 05 | `resolveRemotePushEndpoints` | Resolve remote push endpoints | Git transport/endpoint identity, not Canonical Governance Routing |
| 06 | `parsePushRefspec` | Parse exact refspec | Git grammar |
| 07 | `classifyEndpoint` | Classify credential-free endpoint | Git transport security; consumer-local allowed destination |
| 08 | `readRawObject` | Read exact typed Git object | Git object data |
| 09 | `writeRawObject` | Write isolated exact object | Git object data; not authoritative-ref mutation |
| 10 | `inspectCommitObject` | Decode commit parents/tree/metadata | Git object identity |
| 11 | `traverseReachableClosure` | Enumerate baseline reachable closure | Git object graph, not proto-ring worktree capture |
| 12 | `acquirePromisorObjects` | Acquire permitted promised objects | Git partial-clone handling |
| 13 | `acquireConfiguredUpstreamHistory` | Complete permitted shallow history | Git history-acquisition handling |
| 14 | `createIsolatedObjectDatabase` | Isolate object materialization | Git executor isolation |
| 15 | `listTreeEntries` | Decode exact raw Git tree | Git object data |
| 16 | `buildTree` | Construct exact candidate tree | Git data operation, with Turnlock-owned authorized candidate content |
| 17 | `classifyGitMetadataPath` | Reject unsafe Git metadata-equivalent candidate paths | Git path-safety; similar concern does not establish equivalence with proto-ring Git Whitespace Validation |
| 18 | `createBaselineBundleV3` | Store self-contained baseline bundle | Git portable recovery carrier |
| 19 | `restoreAndInspectBaselineBundleV3` | Independently test baseline reconstruction | Git carrier validation, not historical semantic proof |
| 20 | `observePublicationTarget` | Observe current exact remote target | Git remote observation; proto-ring monotonicity specifies independent external protection |
| 21 | `acquirePublicationTargetHistory` | Acquire remote predecessor objects | Git history acquisition |
| 22 | `provePublicationAncestorOrEqual` | Prove exact \(P \leq T\) for one transition | Git ancestry witness; distinct from provider-enforced non-FF policy |
| 23 | `conditionalUpdatePublicationTarget` | Exact-old \(P\) to \(T\) guarded external effect | Git publication and recovery; no current proto-ring executable substitute |

**Classification result:** at these exact baselines, **none of the 23 primitive contracts was proven to be an unauthorized implementation of an existing proto-ring governance contract**. This is *not* a blanket permission to duplicate existing generic mechanisms in M6/M7 or future adapters. A code-level finding could change this assessment.

## 4. Traceability: formal Gate A versus runner completion

[ADR-041 §Gate A](../adr/adr-041-establish-turnlock-formal-assurance-architecture.md) authorizes candidate formal-model authoring only after the required review/evidence/repository-integrity conditions. [ADR-042](../adr/adr-042-define-auditable-hostile-review-campaign-execution-and-adjudication.md) and the active [review contracts](../../formal/reviews/README.md) require exact current campaign evidence. [`formal/verification.yaml`](../../formal/verification.yaml) and the existing Python checker derive readiness from *current governed repository artifacts*, not a runner's mutable ledger.

[ADR-045](../adr/adr-045-bind-gate-a-campaigns-to-versioned-review-protocol-and-derived-evidence.md) defines the three normal runner outcomes, but **does not explicitly require the cognitive campaign engine itself to mutate a remote Git ref**. [NIB-S §29–31](nib-s-gate-a-campaign-runner.md) establishes a stricter **end-to-end tool completion contract**:

```text
qualified exact candidate
AND confirmed exact published representation
AND passed post-publication validation bound to the same PublishedRepositoryViewRef
=> runner GATE-A-READY
```

The distinction is mandatory:

- `GateAQualification`: mechanized qualification of the exact candidate; **not** publication.
- Formal **Gate A READY**: current repository-derived assurance readiness; **not** an arbitrary runner declaration.
- Runner `GATE-A-READY`: a terminal *workflow result* requiring published-state confirmation and post-publication validation under the current NIB-S.
- Proto-ring `Repository Integrity PASS`: necessary current-state governance coherence; **not** equivalence with any of the above.

Publishing is necessary to claim that this runner has made **the published repository** ready. This does **not** logically require that the review engine and publisher be the same software component. Keeping M7 within one recoverable v1 application is a construction choice, not a new Turnlock product-runtime requirement. A separated publisher is valid only if it preserves every end-to-end binding, external-effect recovery and terminality condition, or explicitly changes the accepted runner outcome contract through proper authority.

## 5. Candidate architectures

| Option | Benefit | Cost / risk | Audit disposition |
|---|---|---|---|
| Retain M7-A/M7-B in v1 | Preserves the currently specified M1/M2/M6/M7/M8 contract and same-run recovery boundary | Future Git DC must qualify real exact-old transport, protected refs and failure classification | **Recommended construction choice**, not yet an accepted new authority |
| Separate review/qualification engine from repository executor | Cleaner conceptual boundaries and potential future reuse | Adds immutable handoff, admission, recovery and terminal-result responsibilities; cannot weaken current `GATE-A-READY` | Feasible future refactor, not a necessary change to close an established duplication |
| Delegate to Ruu or another executor | Could reuse mature external publication/convergence responsibility | [Ruu README at baseline](https://github.com/fanilosendrison/ruu/blob/5d04c58170b2ce3f0e47aa0554a97906d2256492/README.md) reports **no production implementation**; provider routes may rewrite OIDs | **Not a qualified v1 drop-in**; require conformance, not branding |
| Return `GATE-A-READY` on candidate-only qualification | Avoids publisher | Conflates qualified candidate with current repository authority, contrary to NIB-S's outcome | **Not admissible as an unreviewed refactor** |

Ruu [ADR-052](https://github.com/fanilosendrison/ruu/blob/5d04c58170b2ce3f0e47aa0554a97906d2256492/docs/adr/adr-052-advance-direct-targets-by-atomic-exact-old-cas-fast-forward.md) specifies `AdvanceTargetFF(expected_old, new)`, but specification is not a callable qualified executor. Ruu [ADR-066](https://github.com/fanilosendrison/ruu/blob/5d04c58170b2ce3f0e47aa0554a97906d2256492/docs/adr/adr-066-bind-promotion-success-to-route-conformant-candidate-submission-result-target-chains.md) distinguishes direct from provider-mediated realization. A provider-rewritten result cannot silently substitute for M7's exact intended successor OID.

The full portable reachable-closure bundle, independent restore and deterministic synthetic commit are **one strong realization** of immutable baseline/replay/publication requirements; no cited product or Gate A ADR uniquely demands this representation. No smaller alternative has yet been proved equivalent. Optimization or replacement is a separate construction question.

## 6. Remote-ref exact-old publication evidence and unresolved gap

At the analysis baseline, the [live Turnlock GitHub ruleset 24106121](https://github.com/fanilosendrison/turnlock-rust/rules/24106121) is active for `refs/heads/main`, requiring non-fast-forward rejection and non-deletion. That is **not** guaranteed pre-publication Gate A admission or a per-operation compare-and-swap.

**Do not infer exact-old atomicity from `fast-forward`:**

- GitHub REST [Update a reference](https://docs.github.com/en/rest/git/refs) accepts `sha` and `force`, **not** an explicit expected-old value. A prior read followed by `force:false` is not the NIB-required expected-old CAS.
- Git's documented [`--force-with-lease=<ref>:<expect>`](https://git-scm.com/docs/git-push) compares one explicit old OID and can protect against stale target movement. Locally, Git 2.47.3 with a bare remote and non-FF-rejecting pre-receive hook produced: matching lease + FF accepted; stale lease + otherwise-FF rejected; ordinary FF without lease accepted; matching lease + non-FF rejected by hook. These are **local observations**, not proof of compatibility with the live GitHub ruleset or future selected Git CLI contract.
- GitHub GraphQL [`updateRefs`](https://docs.github.com/en/graphql/reference/git) exposes `RefUpdate.beforeOid`, `afterOid`, and `force:false`, with atomic ref-update semantics. This is **a possible alternative provider realization**, not a selected implementation: current NIB-S/M7 select a Git CLI dependency contract, and moving to a provider API requires an explicit architectural/contract decision.
- **Specific ambiguity:** NIB-S §29 forbids "force-push" as an improvised conflict resolution. `--force-with-lease` includes a force-like Git transport mechanism even if the exact intended transition is independently proven FF. Its admissibility under that prohibition and the remote ruleset **must be explicitly adjudicated**, not silently assumed by a coding agent or this audit. A non-FF effect remains forbidden independently of any lease.

**Concrete checks required before the Git DC is accepted:**

1. One exact refspec to the explicitly resolved target; no ambient default/matching remote pushes, no unrelated ref mutation.
2. Independently verified \(P \leq T\), immutable exact candidate-to-successor tree correspondence and pre-Arm freshness of target/policy/permission.
3. Transport enforces **atomic `target == P`** on mutation, not merely `P ancestor-of T` and not read-then-write. No unguarded retry.
4. Credential boundary, Git config precedence, Git protocol/runtime version and SHA-1/SHA-256 capability checks are explicit.
5. Terminal `applied` and `not-applied` are positive *effect-specific* results; transport uncertainty stays `uncertain`.
6. Following an uncertain result, `target == P` alone cannot prove historical non-execution; `target == T` can only confirm under exact identity checks; divergent/unknown observations fail closed.
7. Protected-ref/ruleset behavior is qualified with **isolated** remote integration or a precisely justified provider proof; the authoritative `main` ref must not be used for unsafe testing.
8. Post-publication validation and immutable published-view binding remain outside transport and inside the existing M6/M2 authority.
9. All validations and any generic repository-governance observation/evaluation must consume pinned proto-ring where applicable; neither the Git DC nor M7 invents another generic `RepositoryState` / Repository Integrity / Exact Evidence Binding implementation.

No live GitHub publication or network failure-injection experiment has been performed by this audit. The remote transport therefore remains **unqualified**.

## 7. Required authority and review route

**Proposed resolution:** retain the M7 v1 implementation boundaries *subject to* clear, non-duplicating proto-ring ownership and a separately qualified Git dependency contract. No new product invariant, formal-assurance claim, protocol `S/P`, or arbitrary Ruu dependency follows from the evidence.

Before #78 can close or construction can rely on this conclusion:

1. Record the responsibility-placement decision and exact `GateAQualification` / Gate A READY / runner `GATE-A-READY` distinction in accepted NIB-S **with proper NIB versioning and dependent NIB synchronization**. An issue comment or this analysis document does not silently amend NIB-S.
2. Synchronize M7-A and M7-B for the same boundary. Their 23 operations remain an *unimplemented* dependency surface until a valid DC exists.
3. Explicitly resolve the force-like-lease vs NIB-S §29 prohibition, or qualify a different exact-old CAS mechanism that does not require relaxing accepted constraints. Design selection belongs to the architect and applicable accepted authorities, not GREEN discretion.
4. Complete and qualify `DC-GIT-CLI-GATE-A-REPOSITORY-CONTROL`; include protected-ref conformance and every material crash/retry outcome in NIB-T.
5. Re-run NIB coherence validation, current repository-integrity validation, and the independent [construction-pack hostile review in #33](https://github.com/fanilosendrison/turnlock-rust/issues/33); resolve every material finding before RED/GREEN.
6. If any required behavior cannot be uniquely derived from accepted authority, route it to a later accepted ADR; do not update existing accepted ADR bodies or quietly change `GATE-A-READY`.
7. Do **not** open a proto-ring extraction issue without first demonstrating a specific, reusable missing governance responsibility; plain Git transport and consumer-specific Gate A policy are insufficient.

This file is a **bounded input** to that work. No qualified Git DC, no completed construction review, and no acceptance of a revised NIB-S is claimed here.
