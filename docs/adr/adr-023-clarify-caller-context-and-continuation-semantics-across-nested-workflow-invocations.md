---
okf_version: "1.0"
adr_profile_version: "0.1.0"
kind: "KnowledgeAsset"
asset_type: "architecture-decision-record"
domain: "turnlock-rust"
severity: "strict"
name: "Clarify caller-context and continuation semantics across nested workflow invocations"
id: "ADR-023"
status: "accepted"
date: "2026-09-15"
decision_body_sha256: "602d91e55170b25e8d15c98f561b97fd3e44e8c4300dba34ee526f0f28509efa"
relation_completeness: "complete"
relations:
  clarifies:
    - "ADR-008"
  amends:
    - "ADR-022"
  supersedes: []
  confirms: []
governs:
  - "Caller-context and call-continuation distinction, and decision-owner-specific post-return behavior for nested workflow invocations"
---

# ADR-023: Clarify caller-context and continuation semantics across nested workflow invocations

## Context

ADR-022 accepted workflow-declared invocation and stated that the caller context
preserves a structured call continuation. That wording distinguishes the caller
context from its continuation, but the synchronization of ADR-022 into the
normative specification collapsed the two notions. Sections 0.6, 2.6, and 5.3
described the immediate caller of a workflow-declared invocation as the
"suspended call continuation of the caller context", which is a category error:
the caller is an execution context, while the continuation is the preserved
return state of that context.

ADR-022 also stated, for every admitted invocation, that normal completion
"enables only the caller's declared post-call continuation". That phrasing
describes a workflow-declared invocation, whose post-call continuation is
declared by the workflow program, but it does not describe ADR-008's
agent-selected path. There, normal completion resumes the same main-agent
region, and the region then continues its local execution under the main agent's
legitimate local authority before the enclosing workflow's own continuation
becomes available.

Section 0.6 additionally retained an ADR-008-specific sentence stating that the
enclosing workflow continues "only when its own main-agent region completes".
That statement is false for a workflow-declared invocation, which requires no
main-agent region.

Finally, `TL-INV-035` states the callee's no-rewrite obligation, but its formal
traceability did not reference the existing actor-neutral planned property
`NestedInvocationCannotRewriteOuterContinuation` already used for `TL-INV-019`.

The discovery classification records the caller/continuation category error and
the overgeneralized return phrasing as `authority-conflict-or-uncertain`, the
stale Section 0.6 sentence as `derived-from-existing-authority`, and the formal
traceability gap as `no-normative-impact`. This decision introduces no new
invocation capability.

## Decision

1. An immediate caller context and its call continuation are distinct semantic
   notions.
2. The immediate caller context is the execution context that performs an
   admitted workflow invocation and to which normal completion returns.
3. That caller context preserves a return-bearing continuation while the callee
   executes. The continuation is not itself the caller context.
4. For a workflow-declared invocation:
   - the caller is the workflow execution context performing the call;
   - its preserved post-call continuation is declared by the workflow program;
   - normal callee completion makes that preserved continuation eligible,
     subject to the enclosing workflow topology.
5. For an agent-selected invocation under ADR-008:
   - the immediate caller is the main-agent region;
   - normal callee completion resumes that same main-agent region at the point
     following the nested invocation;
   - subsequent local execution remains under the main agent's legitimate local
     authority;
   - this return does not itself complete the main-agent region;
   - the enclosing workflow's own declared continuation remains unavailable
     until that main-agent region completes according to its semantics.
6. A callee cannot select, replace, rewrite, skip, or capture the caller's
   preserved return target.
7. "Only the caller continuation is enabled by this return" is local to that
   call/return relationship. It MUST NOT mean that independently active
   concurrent contexts permitted by the enclosing topology are disabled,
   suspended, or required to stop.
8. Suspension remains local to the calling continuation. ADR-022's rejection of
   unconditional whole-workflow suspension remains unchanged.
9. Nothing here decides recursion, cyclic-call admissibility, restricted
   placements, concrete depth limits, stack or frame representation, activation
   identifiers, TLA+ variables or actions, DSL syntax, Rust APIs, process
   topology, failure, cancellation, or timeout semantics.

This decision preserves the substantive decisions of ADR-008 and ADR-022 while
removing the caller/continuation ambiguity. ADR-008 and ADR-022 remain accepted
and are not edited.

## Alternatives considered

- **Define the immediate caller as the suspended continuation:** Rejected as a
  category error; the caller is an execution context and the continuation is the
  preserved return state of that context.
- **Keep "declared post-call continuation" for both decision owners:** Rejected
  because an agent-selected invocation resumes the main-agent region, whose
  subsequent local work is not a workflow-declared continuation.
- **Edit ADR-022's accepted body to correct the wording:** Rejected because
  accepted decision bodies are immutable; this later ADR records the
  clarification.
- **Create a new planned property for the `TL-INV-035` no-rewrite obligation:**
  Rejected because the existing actor-neutral property already covers it and a
  duplicate name would fragment traceability.
- **State that a normal return disables other continuations of the caller:**
  Rejected because the effect is local to the call/return relationship;
  independently active concurrent contexts permitted by the declared topology
  are not implicitly suspended.

## Consequences

### Benefits

- Restores one non-ambiguous model: the caller context owns and preserves a
  continuation, the relevant continuation is suspended during callee execution,
  and normal return restores the continuation appropriate to that caller.
- Preserves ADR-008 and ADR-022 without editing either accepted body.
- Gives the first TLA+ model distinct abstract notions of caller context and
  preserved continuation without selecting a representation.

### Costs and obligations

- Sections 0.6, 2.6, 5.3, and `TL-INV-035` require synchronized correction.
- The terminology review inventory must be refreshed for moved definition-like
  occurrences.
- `formal/verification.yaml` must add the existing planned property
  `NestedInvocationCannotRewriteOuterContinuation` to `TL-INV-035` and record
  ADR-023 as a governing ADR; no formalization, verification, or mapping status
  changes, and no `checked` claim.
- Issues #5, #6, and #9 require work-state updates to reflect ADR-022 and
  ADR-023. Issue #6 remains the owner of restricted-placement, transitive, and
  recursive- or cyclic-admissibility questions.

## References

- `docs/specification/turnlock-spec.md`
- `docs/adr/adr-008-allow-nested-workflow-invocation-from-main-agent-regions.md`
- `docs/adr/adr-022-allow-workflow-declared-invocation-with-structured-call-return-semantics.md`
- `docs/adr/adr-014-define-turnlock-as-the-orchestration-engine-and-the-workflow-as-the-orchestration-program.md`
- `docs/adr/adr-015-evolve-the-normative-and-formal-specifications-together.md`
- `formal/verification.yaml`
- `docs/repository-governance/turnlock-rust-discovery-classification.md`
- GitHub Issues #5, #6, and #9
