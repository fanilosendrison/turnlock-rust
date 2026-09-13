# TLC run evidence

This directory is reserved for machine-readable evidence of **actual** TLC executions.

`formal/verification.yaml` declares what TURNLOCK intends to formalize and which configurations are expected to cover each invariant. Files recorded here answer the separate question: **what was actually checked, with which finite bounds, by which TLC version, for which repository revision?**

Run evidence must conform to `../tlc-result.schema.json`. A future CI integration may choose the concrete filename/layout (for example `<commit>/<profile>.yaml`), but each record must identify at least the commit, model config, TLA+ module, TLC version, result, checked properties, mapped invariant IDs, and finite bounds.

No passing result files exist yet because the executable TLA+ model has not been introduced. The absence is intentional and prevents traceability metadata from being mistaken for verification evidence.
