---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "evidence-requirement-registry"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust Evidence Requirements Registry"

evidence_requirements:
  model_version: 1
  authority:
    responsibility: evidence_requirement_registry
    source: evidence_requirement_registry
  requirements:
    gate_a_subject_binding:
      responsibility: formal_assurance_graph
      instances:
        kind: single
      evidence_classes:
        kind: explicit
        classes:
          - assurance-decomposition
      subject:
        source: gate_a_current_subject
      context:
        required: false
      candidates:
        source: gate_a_review_candidates
    gate_a_current_protocol_binding:
      responsibility: formal_assurance_graph
      instances:
        kind: single
      evidence_classes:
        kind: explicit
        classes:
          - assurance-decomposition
      subject:
        source: gate_a_current_subject
      context:
        required: true
        source: gate_a_current_protocol_context
      candidates:
        source: gate_a_review_candidates
---

# Turnlock-Rust Evidence Requirements Registry

The registry declares the two current Gate A binding requirements. Turnlock-Rust
continues to own subject and protocol identity construction, candidate parsing,
finding lifecycle, materiality, challenge, re-adjudication, and readiness.
