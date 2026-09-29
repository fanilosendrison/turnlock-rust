---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust Exact Evidence Binding"
exact_evidence_binding:
  contract:
    repository: "fanilosendrison/proto-ring"
    commit: "3bddcd4b49147f022466fdeb4acbf590e68890ce"
    path: "docs/contracts/exact-evidence-binding.md"
---

# Turnlock-Rust Exact Evidence Binding

## Shared contract

Apply the proto-ring Exact Evidence Binding contract at this immutable identity:

```text
fanilosendrison/proto-ring
3bddcd4b49147f022466fdeb4acbf590e68890ce
docs/contracts/exact-evidence-binding.md
```

Mutable proto-ring state is not authority for this binding.

## Turnlock-Rust authority remains local

Retain Turnlock-Rust authority for:

```text
Gate A semantics
review_class vocabulary
Gate A subject construction
canonical JSON subject serialization
protocol-bundle identity construction
review protocol semantics
reviewer qualification
finding lifecycle
materiality
adjudication
refutation
challenge
retry/admissibility
readiness
formal semantics
TLC evidence
product semantics
```

Exact Evidence Binding consumes the identities produced under that authority. It
does not become their owner.

## Gate A consumer mapping

Map the current Gate A consumer values exactly as follows:

```text
evidence class
=
record.review_class

admitted evidence class
=
GATE_A_REVIEW_CLASS

subject identity token
=
Turnlock-owned canonical JSON bytes of the unique Gate A derived subject record

current subject identity token
=
Turnlock-owned canonical JSON bytes of current_subject

currentness context
=
UTF-8 bytes of the exact protocol-bundle SHA-256

context_required
=
true when deciding current-protocol evidence
```

Use subject-only binding before current-protocol binding so that Turnlock-Rust
continues to distinguish evidence that is not a candidate for the current Gate A
subject from candidate evidence produced under stale or unavailable protocol
context.

## Binding boundary

Exact Evidence Binding decides binding only.

`MATCH` does not make Gate A `READY`.

All remaining Gate A eligibility, finding, re-adjudication, materiality,
challenge, reviewer, and readiness logic remains Turnlock-owned.

In particular:

```text
MATCH != evidence success
MATCH != proof validity
MATCH != claim truth
MATCH != obligation satisfaction
```

Historical review evidence remains inspectable against its own historical
requirement. Currentness is evaluated only against the exact current requirement
supplied by Turnlock-Rust.
