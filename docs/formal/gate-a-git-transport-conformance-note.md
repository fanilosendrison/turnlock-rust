# Gate A Git transport — bounded conformance evidence and remaining obligations

**Status:** non-authoritative, local-only experiment for Turnlock-Rust Issue #78. **Not** the required `DC-GIT-CLI-GATE-A-REPOSITORY-CONTROL`, not a current provider integration proof, not an accepted NIB or permission to modify an authoritative Git ref. Do not use these results to enter GREEN.

## Authority and exact source

- Current constructed responsibilities: [NIB-S Gate A campaign runner](nib-s-gate-a-campaign-runner.md) §29–31; [M7-A](nib-m-gate-a-repository-control-materialization-candidate-construction.md) §2, §13; [M7-B](nib-m-gate-a-repository-control-publication-remote-recovery.md) §4, §16, §23.
- The 23 mandatory future Git dependency primitives remain defined by the two M7 briefs; this note tests **only a candidate implementation for primitive 23**, and only with a local bare remote.
- Proto-ring [Authoritative Ref Monotonicity](https://github.com/fanilosendrison/proto-ring/blob/6b04ce661e86396a3f6a5d9f5ce8bc2839ac2e60/docs/contracts/authoritative-ref-monotonicity.md) demands externally enforced non-FF/non-deletion, but neither exact-old CAS nor pre-publication Gate A admission.
- Git documentation: [git-push, explicit `--force-with-lease=<refname>:<expect>`](https://git-scm.com/docs/git-push) protects a named ref against update unless the remote currently holds the exact specified expected object ID.
- GitHub [GraphQL `updateRefs`](https://docs.github.com/en/graphql/reference/git) has explicit `RefUpdate.beforeOid` and `force:false`; its availability is **not** qualification of the selected CLI dependency. GitHub's REST `PATCH /git/refs/...` does not provide a matching explicit `beforeOid` input.

## Bounded experiment (local Git 2.47.3)

Run [the companion self-contained local script](gate-a-git-exact-old-local-conformance.sh) in a disposable directory. It sets `GIT_CONFIG_NOSYSTEM=1`, an isolated HOME and a bare remote with `receive.denyNonFastForwards=true` and `receive.denyDeletes=true`. No GitHub network call, token, or external mutation occurs.

The test creates a linear history `P -> T -> V` and checks:

| Case | Requested operation | Witness | Result |
|---|---|---|---|
| C1 | `expected_old=P, new=T` while target is P | exact target becomes T; T descendant of P | PASS |
| C2 | `expected_old=P, new=V` while target already is T | client rejects with stale-info; target stays T even though V descends from T | PASS |
| C3 | `expected_old=T, new=V` while target is T | exact target becomes V; V descendant of T | PASS |
| C4 | `expected_old=V, new=P` while target is V | remote rejects non-fast-forward; target stays V | PASS |

This demonstrates two *independent* safeguards in that environment: an explicit old-tip lease and a server-side descendant-only requirement. It does **not** demonstrate that an arbitrary provider/ruleset permits or enforces the same operation, that the exact CLI options are accepted under NIB-S §29's ban on forced publication, or that Git output alone is historical non-execution evidence.

No language-level helper or local Git tool result may transform `STALE`, `UNKNOWN`, `UNREACHABLE` or `REJECTED` into Gate A qualification, PublicationConfirmation or an authorized retry.

## Missing tests before selecting the actual transport

| ID | Required independent qualification |
|---|---|
| Q01 | Verify compatible Git executable and the precise minimum Git version; canonical parsing of Git command status, stdout/stderr, NUL and raw byte paths |
| Q02 | Qualify SHA-1 and SHA-256 repository-format support; fail closed where a required format/capability is unsupported |
| Q03 | Verify exact object closure, shallow/promisor acquisition policy, deterministic baseline bundle v3, offline restoration and identity checking for M7-A primitives 02–19 |
| Q04 | Verify exact effective push configuration and explicit publication-target binding; reject ambiguous push remote/refspec/mirror/multi-target/matching defaults, ref deletion and credential-bearing identity |
| Q05 | Positive independent `P <= T` ancestry/equality proof over the exact Git object identities, not inferred merely from an update response |
| Q06 | Actual target/protection enforcement and positive **atomic expected-old** semantics for exactly one ref; target moved P→X just before mutation must never be overwritten |
| Q07 | Matching expected-old plus non-FF candidate must never publish, including absent or permissive external protection; NIB-S §29 forbids a semantic force-push |
| Q08 | Exact same-head/no-op realization is observation-only; after an armed publication, any observation stays in the execution recovery path |
| Q09 | Revalidate policy/target/authorization before Arm and isolate the credential capability; no copied secrets in any durable evidence |
| Q10 | Concurrent attempt/stale target and remote refusal have distinct positive effect evidence; no unguarded request retry |
| Q11 | Lost response *after applied mutation* and failed remote observation before/after effect: preserve `uncertain`, reconcile read-only and never manufacture `not-executed` from `target==P` |
| Q12 | Target T observed after crash must still pass exact transition, ancestry, material and publication-confirmation binding before terminal qualification |
| Q13 | Missing/other target authority X, unavailable credentials, malformed Git protocol, invalid or changing Git configuration, network timeouts fail closed into prescribed M7/M8 pathways |
| Q14 | Verify remote GitHub repository ruleset compatibility using a **non-authoritative disposable ref/repository** and appropriate permissions; never risk the live authoritative `main` ref |
| Q15 | For a path using `--force-with-lease`, explicitly adjudicate its force-like transport semantics against the accepted NIB-S prohibition and effective provider rules; it is not authorized by this note |
| Q16 | Verify only one exact target ref can change; no push options, default push rules or ambient credential helpers may silently broaden the effect |
| Q17 | Prove post-effect target observation is *read-only*, distinguish transport-applied versus publication-confirmed from exact evidence, and require M6 post-publication validation |
| Q18 | Confirm each of the remaining 22 dependency operations has exact typed input/output, controlled environment, error grammar, replay and conformance tests in the final DC |

### Non-execution, no-operation, and uncertainty

An acknowledged, positively established Git command rejection is a possible source of `not-applied` **only if the exact selected dependency contract can demonstrate terminal non-application of that specific mutation**. A timeout or lost connection is *uncertain*. A subsequent `target==P` observation does not prove the earlier operation never applied: an independent actor could have advanced and later rewritten the ref. A subsequent exact `target==T` observation can support recovery only through the accepted exact identity and provenance validation, not through a free `success` string.

## Required disposition

- **LOCAL EXPERIMENT:** `PASS` (four cases).
- **REAL GITHUB CLI/PROVIDER CONFORMANCE:** `UNDETERMINED`.
- **COMPLETE 23-PRIMITIVE GIT DEPENDENCY CONTRACT:** `NOT PRESENT`.
- **NIB-S §29 FORCE-LIKE CLI AUTHORITY:** `NOT ADJUDICATED`.
- **RUNNER GREEN / ISSUE #78 COMPLETION:** `NOT ESTABLISHED`.

This document and the script are evidence inputs only. The architect must close the actual Git DC and required construction review with exact accepted repository authority. No product semantic, hosted branch, issue lifecycle, or Gate A record is modified by running the script.
