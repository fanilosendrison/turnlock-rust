---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "product-positioning"
domain: "turnlock-rust"
severity: "informational"
name: "TURNLOCK and Turnlock Cloud — Product Positioning and Differentiation"
---

# TURNLOCK and Turnlock Cloud — Product Positioning and Differentiation

> **Status and authority:** This is non-normative product positioning. It does
> not change TURNLOCK Product Intent or create any requirement, architecture,
> primitive, interface, implementation guarantee, reproducibility profile,
> comparison contract, evaluator, optimizer, or Turnlock Cloud Product Intent.
> Comparisons are not premises for TURNLOCK derivation. Intended guarantees,
> implementation, conformance, and verification remain distinct.

The [TURNLOCK specification](../specification/turnlock-spec.md) and accepted
[ADRs](../adr/README.md) retain their respective authority. The
[TURNLOCK Product Rationale](turnlock-product-rationale.md) and
[Turnlock Cloud Product Rationale](turnlock-cloud-product-rationale.md) explain
value without creating requirements. The
[future run-evaluation](../vision/future-workflow-run-evaluation.md) and
[future managed-execution](../vision/future-managed-execution.md) documents
preserve non-normative design opportunities only.

## The distinction to understand

Launching agents, persisting runs, collecting traces, evaluating outputs, and
optimizing prompts or programs are all useful capabilities. They are not by
themselves equivalent to preserving the semantic identity and execution
conditions required to make a particular claim about an executable method.

TURNLOCK's intended differentiation is not that no other system can execute
workflows. It is that the workflow program owns declared orchestration while the
runtime preserves distinct execution forms, same-main continuation where
declared, structured composition, governing-definition binding, execution truth,
and attributable effective-condition provenance according to the accepted Core
contract.

A compatible system can be equivalent without using TURNLOCK names or
architecture.

## Workflow execution is not the whole method contract

A workflow engine may provide sequence, branches, parallelism, retries, state,
or durability while still differing materially on:

```text
which cognitive lineage is the existing main agent
where a nested invocation returns
which definition governs one accepted invocation
which restrictions survive nested composition
whether scheduler order changes semantic meaning
what actual execution truth remains available
which effective conditions governed which scopes
```

These distinctions matter only when the user's method needs them. TURNLOCK
should not duplicate a harness-native mechanism that already preserves the
required semantics.

## Durable replay is not universal output reproducibility

A durable runtime can reproduce workflow progression by replaying recorded
events or reusing historical outputs from nondeterministic work.

That does not imply:

```text
same fresh LLM output
same fresh agent behavior
same opaque external-service result
same human choice
```

A future Turnlock Cloud opportunity should therefore describe reproducibility
by explicit scope or profile rather than by an unqualified Boolean claim.

## A trace is not automatically a valid comparison

Two runs can both be fully traced and still be unsuitable for a method-level
comparison.

For property `P`, an evaluator may need to establish or control determinants
such as:

```text
governing method definition
inputs / dataset
evaluator
model / provider
parameters
tool / harness realization
workspace state
environment
other property-specific conditions
```

A missing determinant is not evidence that the runs were equal on that
determinant.

> The question is not only whether two runs are observable, but whether the
> available evidence makes them comparable for the property being evaluated.

## A score difference is not automatically a method regression

A lower score may be associated with:

```text
a worse workflow method
a different realized control path
a model/provider change
tool or harness drift
environment or workspace drift
different inputs
evaluator drift
resource constraints
residual stochastic variation
```

A future comparison system may therefore need to distinguish an observed
degradation from a method-attributable regression.

This is not a claim that causal attribution is always possible. Preserving
`undetermined` can be the correct result when the evidence does not support a
stronger conclusion.

## Optimization is only as good as the signal it optimizes

Prompt, program, policy, and workflow optimization already exist as generic
capabilities.

The differentiated opportunity is not merely to search for another workflow.
It is to supply an optimizer or promotion system with execution evidence whose
method identity, relevant conditions, comparison eligibility, and uncertainty
are explicit enough for the selected objective.

A candidate that scores better under changed, unknown, or confounded conditions
need not represent a better method.

## TURNLOCK Core's intended information boundary

Core's current contract does not guarantee replay or cross-run comparability.
It does, however, already distinguish information that can become impossible to
establish later if discarded when known:

```text
the definition governing an accepted invocation
realized execution / realized prefix truth
effective conditions TURNLOCK selected, bound, supplied, or resolved
their attribution to governed execution scopes
known versus unavailable / unknown facts
```

This is a possible foundation for stronger systems above Core. It is not a
complete run-data model or comparison product.

## Turnlock Cloud's possible distinction

A possible Turnlock Cloud product can be evaluated as several separate
responsibilities:

1. **Managed execution** — supply compatible isolated/elastic execution
   realizations without redefining TURNLOCK semantics.
2. **Run signal and reproducibility** — retain authorized execution truth and
   enough property-relevant context to establish scoped reproducibility or
   comparison claims where supported.
3. **Evaluation and regression** — determine whether an observed difference
   supports a conclusion for an explicit property and preserve uncertainty when
   it does not.
4. **Optimization and downstream use** — use qualified observations for method
   refinement, promotion, routing, benchmark generation, research, training
   signal, assurance, or another authorized purpose.

An actor can provide one responsibility without the others. An actually
available multi-component system can be an equivalent substitute on a declared
scope.

## Information that cannot be guaranteed reconstructed later

If a historical fact was never observed or retained and no authoritative source
still exists, later analytics cannot guarantee reconstruction of that fact.

Examples include:
- exact governing-definition identity;
- a property-relevant effective condition;
- equality/difference evidence for a protected historical condition;
- actual realized occurrence relationships; or
- whether a missing value was genuinely equal or simply unobserved.

This is an information boundary, not an exclusivity claim. Any system that
captures equivalent information at the relevant boundary can support equivalent
future guarantees.

## How alternatives should be compared

Compare available alternatives across independent dimensions:

- **TURNLOCK Core guarantees** — workflow ownership, execution-form semantics,
  same-main continuation, composition/admissibility, governing-definition
  binding, execution truth, provenance, and runtime composability.
- **Managed execution** — environment lifecycle, isolation, materialization,
  elastic resources, result/effect extraction, and semantic compatibility.
- **Run signal / reproducibility** — durable capture, condition identity,
  property-relative comparability, rematerialization/replay scope, unknown
  treatment, and authorization.
- **Evaluation / optimization downstream** — regression validity, variance
  handling, experimental design, optimizer input quality, promotion, routing,
  datasets, learning, and analysis.

Do not average these dimensions into one score. A supplier may be weak on Core
semantics and excellent on managed execution. An evaluation platform may be a
downstream consumer rather than a producer of the required signal.

Named observations and ratings belong in immutable dated research reports, not
in this positioning document. The
[Competitive Guarantee Watch](../research/competitive-watch/README.md) defines
that separate evidence process.

## Evidence and public claims

Preserve the distinction:

```text
intended guarantee
implemented mechanism
verified behavior
```

Until evidence establishes stronger wording, TURNLOCK should be described as
being designed to preserve its accepted semantics. Turnlock Cloud remains a
possible product opportunity until entitled authority establishes otherwise.

Do not make unqualified claims such as:

- “only TURNLOCK can”;
- “no competitor can do this”;
- “TURNLOCK makes LLM runs deterministic”;
- “Turnlock Cloud guarantees reproducibility”;
- “a lower score proves a workflow regression”; or
- “the optimizer proves the method improved.”

Every comparative conclusion requires a declared scope, date, and evidence
basis. Absence of public evidence is not proof of absence.
