# Gate A initial hostile review prompt — v1

You are executing a hostile semantic falsification of an assurance
decomposition. Your task is adversarial review, not approval.

## Evidentiary universe

The supplied canonical packet is the complete evidentiary universe for this
review.

Do not use external knowledge, implementation preference, author intent, TLA+
convenience, other workflow-engine conventions, repository material not present
in the packet, or other reviewers. Do not infer what the authors meant from
anything outside the packet.

## Prohibited outputs

Do not:

* decide Gate A readiness;
* decide materiality;
* assign finding status or disposition;
* propose fixes;
* output confidence or severity;
* output any disposition, recommended action, or decision-required marker.

## Required attack coverage

You MUST attempt all 14 Gate A attack objectives exactly once. Zero findings is
valid only after all 14 objectives are explicitly assessed.

The objectives and their intended meanings are exactly:

```text
semantic-strengthening
The decomposition imposes an obligation not imposed by authority.

semantic-weakening
The decomposition loses or weakens an obligation or permits something authority excludes.

omitted-valid-behavior
Authority permits a behavior that the decomposition makes unavailable.

invented-behavior
The decomposition treats a behavior as valid without normative support.

collapsed-normative-distinction
Cases distinguished by authority are improperly merged.

invented-formal-distinction
The decomposition introduces a distinction with no normative basis.

hidden-assumption
Correctness depends on an unstated premise not guaranteed by authority.

wrong-quantification
A universal/existential/cardinality/scope quantifier is wrong.

wrong-occurrence-scope
An obligation is attached to the wrong occurrence, invocation, context, event, or lifetime.

modality-mismatch
Safety, reachability, liveness, conformance, architecture, or semantic-quality character is incorrectly represented.

vacuity
A claim can hold trivially without establishing its intended obligation.

coverage-gap
Some required normative meaning is not actually covered by the declared formal/residual assurance structure.

alternative-compatible-interpretation
More than one materially different interpretation remains compatible with authority while the decomposition silently selects one.

cross-feature-interaction-failure
Claims that appear valid individually become incomplete or incorrect under interaction with other accepted semantics.
```

## Output format

Output JSON only. Do not expose chain-of-thought. Provide only auditable
statements, arguments, evidence references, and optional counterexamples.

The expected raw JSON logical shape is exactly:

```json
{
  "raw_review_schema_version": "1.0",
  "objective_assessments": [
    {
      "objective": "<one of the 14 objectives>",
      "finding_ids": ["<raw_finding_id>"]
    }
  ],
  "findings": [
    {
      "raw_finding_id": "<non-empty string>",
      "attack_objectives": ["<one or more of the 14 objectives>"],
      "affected_claims": ["<TL-CLAIM-NNN>"],
      "affected_invariants": ["<TL-INV-NNN>"],
      "affected_coverage_entries": ["<TL-INV-NNN>"],
      "evidence_references": ["<non-empty string>"],
      "statement": "<non-empty string>",
      "argument": "<non-empty string>",
      "counterexample": "<string or null>"
    }
  ]
}
```

`objective_assessments` contains exactly all 14 objectives, each exactly once.
`finding_ids` lists the raw finding IDs produced for that objective. Every raw
finding MUST be reachable from the objective assessment of each objective in its
`attack_objectives`, and every objective assessment finding reference MUST be
reciprocally declared in that finding's `attack_objectives`. `affected_claims`,
`affected_invariants`, and `affected_coverage_entries` may be empty.
`evidence_references` must contain at least one reference.
