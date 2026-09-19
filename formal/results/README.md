# TLC run evidence

This directory is reserved for machine-readable evidence of **actual** TLC
executions.

`formal/verification.yaml` declares the formal-assurance graph: required
assurance claims, their normative coverage, residual assurance, and evidence
contracts. Files recorded here answer the separate question: **what was actually
checked, with which finite bounds, by which TLC version, against which exact
executed artifact bytes, for which repository revision?**

Run evidence must conform to `../tlc-result.schema.json`. A future CI
integration may choose the concrete filename/layout (for example
`<commit>/<profile>.yaml`), but each record must identify at least the commit,
model config, TLA+ module, TLC version, result, checked properties, mapped
invariant IDs, and finite bounds.

TLC evidence does not establish normative/formal semantic correspondence.

TLC evidence does not by itself support a `TL-INV` directly.

Evidence is lifted through reviewed claim/property correspondence and declared
coverage.

The current `tlc-result` schema remains the mechanism-specific contract until
Gate C work strengthens exact artifact identity as required by ADR-041.

This README does not mirror the current presence or absence of run evidence. The
records actually present under `formal/results/`, validated against the result
schema and the formal-assurance policy, constitute the current evidence state.
