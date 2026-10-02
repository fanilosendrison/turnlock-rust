---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "governance-binding-registry"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust Governance Binding Registry"

governance_bindings:
  model_version: 1
  source: governance_binding_registry
  bindings:
    proto_ring_executable:
      kind: executable_provider
      scope:
        kind: logical_provider
      identity:
        repository: fanilosendrison/proto-ring
        commit: 890ed560e61e205067bdf3628e419302613ef06e
      authority:
        responsibility: executable_provider_binding
        source: executable_dependency_manifest
    shared_governance_provider_contract:
      kind: governance_contract
      scope:
        kind: logical_provider
      identity:
        repository: fanilosendrison/proto-ring
        commit: dc8e04c758fb40867dc7ad23f019843413fc4a1b
        path: docs/contracts/shared-governance-provider.md
      authority:
        responsibility: governance_contract_bindings
        source: governance_binding_registry
    projection_integrity_contract:
      kind: governance_contract
      scope:
        kind: capability
        capability: projection_integrity
      identity:
        repository: fanilosendrison/proto-ring
        commit: 846434a25db833ce862a0702bff7743515dcc482
        path: docs/contracts/projection-integrity.md
      authority:
        responsibility: governance_contract_bindings
        source: governance_binding_registry
    exact_evidence_binding_contract:
      kind: governance_contract
      scope:
        kind: capability
        capability: evidence_requirements
      identity:
        repository: fanilosendrison/proto-ring
        commit: 3bddcd4b49147f022466fdeb4acbf590e68890ce
        path: docs/contracts/exact-evidence-binding.md
      authority:
        responsibility: governance_contract_bindings
        source: governance_binding_registry
    governance_authority_contract:
      kind: governance_contract
      scope:
        kind: capability
        capability: governance_authority
      identity:
        repository: fanilosendrison/proto-ring
        commit: 22965fb97be23d7b43b8517b6786d65f5b8a41db
        path: docs/contracts/governance-authority.md
      authority:
        responsibility: governance_contract_bindings
        source: governance_binding_registry
    governed_objects_contract:
      kind: governance_contract
      scope:
        kind: capability
        capability: governed_objects
      identity:
        repository: fanilosendrison/proto-ring
        commit: 275a92523e37b30fabd060ec92df2706bb70ef80
        path: docs/contracts/governed-objects.md
      authority:
        responsibility: governance_contract_bindings
        source: governance_binding_registry
    authoritative_ref_monotonicity_contract:
      kind: governance_contract
      scope:
        kind: capability
        capability: authoritative_ref_monotonicity
      identity:
        repository: fanilosendrison/proto-ring
        commit: dc8e04c758fb40867dc7ad23f019843413fc4a1b
        path: docs/contracts/authoritative-ref-monotonicity.md
      authority:
        responsibility: governance_contract_bindings
        source: governance_binding_registry
    repository_governance_model_contract:
      kind: governance_contract
      scope:
        kind: logical_provider
      identity:
        repository: fanilosendrison/proto-ring
        commit: 890ed560e61e205067bdf3628e419302613ef06e
        path: docs/contracts/repository-governance-model.md
      authority:
        responsibility: governance_contract_bindings
        source: governance_binding_registry
    repository_integrity_contract:
      kind: governance_contract
      scope:
        kind: capability
        capability: repository_integrity
      identity:
        repository: fanilosendrison/proto-ring
        commit: 6cd005b92cb50448bc65757115f4bb0b0361ff90
        path: docs/contracts/repository-integrity.md
      authority:
        responsibility: governance_contract_bindings
        source: governance_binding_registry
    evidence_requirements_contract:
      kind: governance_contract
      scope:
        kind: capability
        capability: evidence_requirements
      identity:
        repository: fanilosendrison/proto-ring
        commit: 857ee0b8b179988c8876d1f38aebd20407794e80
        path: docs/contracts/evidence-requirements.md
      authority:
        responsibility: governance_contract_bindings
        source: governance_binding_registry
---

# Turnlock-Rust Governance Binding Registry

This registry owns active immutable proto-ring provider and governance-contract
bindings. TURNLOCK product, formal, review, evidence, and qualification
semantics remain local.
