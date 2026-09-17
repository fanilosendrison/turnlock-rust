# TLC run evidence

This directory is reserved for machine-readable evidence of **actual** TLC executions.

`formal/verification.yaml` declares what TURNLOCK intends to formalize and which configurations are expected to cover each invariant. Files recorded here answer the separate question: **what was actually checked, with which finite bounds, by which TLC version, for which repository revision?**

Run evidence must conform to `../tlc-result.schema.json`. A future CI integration may choose the concrete filename/layout (for example `<commit>/<profile>.yaml`), but each record must identify at least the commit, model config, TLA+ module, TLC version, result, checked properties, mapped invariant IDs, and finite bounds.

This README does not mirror the current presence or absence of run evidence. The records actually present under `formal/results/`, validated against the result schema and traceability policy, constitute the current evidence state.
