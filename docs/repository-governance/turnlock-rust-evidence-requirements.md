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
  requirements: {}
---

# Turnlock-Rust Evidence Requirements Registry

ADR-059 retires the two consumer-local Gate A requirement instances from the
previous method. The routed capability, registry, provider binding, and generic
Exact Evidence Binding contract remain present. An empty registry establishes
no product-assurance or verification result.
