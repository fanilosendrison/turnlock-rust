# Formal model workspace

TURNLOCK's executable TLA+/TLC artifacts live here.

The machine-readable traceability source of truth is `verification.yaml`. It describes the graph from stable product-invariant IDs to their formal realization and intended TLC coverage. It is **not** evidence that TLC has actually run. Actual run evidence belongs under `results/` and is governed by `tlc-result.schema.json`.

The executable core model is intentionally **not yet present**. The first formal-model pass will introduce `Turnlock.tla` and the focused/integrated TLC configurations against the semantics already identified in the normative specification. Until then, the manifest uses planned/partial/not-applicable formalization states, `pending-model` TLA+ mappings, and `not-yet-modeled` verification status.

## Planned layout

```text
formal/
├── README.md
├── verification.yaml               # desired traceability / coverage graph
├── tlc-result.schema.json           # schema for actual TLC run evidence
├── results/
│   └── README.md                    # no passing evidence until TLC actually runs
├── Turnlock.tla
└── models/
    ├── focused/
    │   ├── nested-workflows.cfg
    │   ├── caller-return.cfg
    │   └── parallel-fanout.cfg
    └── integrated/
        ├── smoke.cfg
        ├── standard.cfg
        └── stress.cfg
```

Focused and integrated configurations must target the same semantic model. Separate mini-specifications that can drift from the integrated semantics are not the intended design.

## Traceability graph

Once `Turnlock.tla` exists, each formally applicable invariant can be bound to the executable identifiers that realize it:

```text
TL-INV-xxx
    ↓
TLA+ module + property/properties
    ↓
state variables + actions/transitions used by that formalization
    ↓
focused and integrated TLC configs
    ↓
actual TLC run evidence for a concrete commit and finite bounds
    ↓
later: implementation/conformance tests
```

The graph must also be mechanically invertible. For example, changing a TLA+ action such as a future `CompleteWorkflow` should make it possible to enumerate every `TL-INV-*` mapped to that action.

Planned property names may appear before `Turnlock.tla` exists. State-variable and action mappings should stay empty until real executable identifiers exist; they must not be invented solely to make the manifest look complete.

## Verification intent vs evidence

`verification.yaml` answers **what should map to what and what should be checked**.

`results/` answers **what TLC actually checked**. A passing record must identify at least the repository revision, model config, TLA+ module, TLC version, checked properties, mapped invariant IDs, finite bounds, and outcome.

A manifest entry must never be interpreted as a successful verification run. `checked` requires matching run evidence.

## Integrated exploration remains mandatory

Focused configurations are development accelerators. They never replace integrated exploration. The planned integrated profiles remain `smoke`, `standard`, and `stress`, all exercising the same shared semantic model at different finite bounds/costs.
