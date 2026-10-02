---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "governance-authority-profile"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust Governance Authority profile"

governance_authority:
  model_version: 1
  sources:
    turnlock_spec:
      repository_target: "docs/specification/turnlock-spec.md"
    accepted_adrs:
      repository_target: "docs/adr"
    canonical_adr_records:
      repository_target: "docs/adr"
    adr_profile:
      repository_target: "docs/adr/adr-profile.yaml"
    adr_index:
      repository_target: "docs/adr/index.md"
    adr_history:
      repository_target: "docs/adr/README.md"
    adr_index_generator: {}
    formal_assurance_manifest:
      repository_target: "formal/verification.yaml"
    formal_assurance_mapping:
      repository_target: "docs/formal/invariant-mapping.md"
    formal_mapping_generator: {}
    hostile_review_records:
      repository_target: "formal/reviews"
    bounded_verification_results:
      repository_target: "formal/results"
    terminology_inventory:
      repository_target: "docs/specification/terminology-inventory.yaml"
    turnlock_vision:
      repository_target: "docs/vision/turnlock-vision.md"
    discovery_classification_profile:
      repository_target: "docs/repository-governance/turnlock-rust-discovery-classification.md"
    governance_binding_registry:
      repository_target: "docs/repository-governance/turnlock-rust-governance-bindings.md"
    executable_dependency_manifest:
      repository_target: "requirements.txt"
    projection_registry:
      repository_target: "docs/repository-governance/turnlock-rust-projection-integrity.md"
    repository_integrity_profile:
      repository_target: "docs/repository-governance/turnlock-rust-repository-integrity.md"
    evidence_requirement_registry:
      repository_target: "docs/repository-governance/turnlock-rust-evidence-requirements.md"
    governed_objects_profile:
      repository_target: "docs/repository-governance/turnlock-rust-governed-objects.md"
    effective_proto_ring_provider: {}
    proto_ring_environment: {}
    gate_a_current_subject: {}
    gate_a_current_protocol_context: {}
    gate_a_review_candidates: {}
    agents_governance_frontmatter:
      repository_target: "AGENTS.md"
    agents_directives:
      repository_target: "AGENTS.md"
    repository_validation_entrypoint:
      repository_target: "scripts/check-repository-integrity.py"
    repository_integrity_ci:
      repository_target: ".github/workflows/repository-integrity.yml"
    repository_git_tree: {}
    github_engineering_work_state: {}
  responsibilities:
    product_semantics:
      roles:
        turnlock_spec: authority
        accepted_adrs: authority
        turnlock_vision: non_authoritative
        formal_assurance_mapping: non_authoritative
        terminology_inventory: non_authoritative
        discovery_classification_profile: non_authoritative
      precedence: []
    stable_invariant_definitions:
      roles:
        turnlock_spec: authority
        governed_objects_profile: secondary_representation
      precedence: []
    canonical_terminology:
      roles:
        turnlock_spec: authority
        terminology_inventory: non_authoritative
      precedence: []
    accepted_decisions:
      roles:
        accepted_adrs: authority
        governed_objects_profile: secondary_representation
      precedence: []
    adr_metadata:
      roles:
        canonical_adr_records: authority
        adr_index: secondary_representation
        adr_history: secondary_representation
        adr_index_generator: non_authoritative
      precedence: []
    adr_history_narrative:
      roles:
        adr_history: authority
      precedence: []
    adr_representation_rules:
      roles:
        adr_profile: authority
      precedence: []
    formal_assurance_graph:
      roles:
        formal_assurance_manifest: authority
        formal_assurance_mapping: secondary_representation
        governed_objects_profile: secondary_representation
        formal_mapping_generator: non_authoritative
        gate_a_current_subject: non_authoritative
        gate_a_current_protocol_context: non_authoritative
      precedence: []
    canonical_formal_semantics:
      roles: {}
      precedence: []
    hostile_review_evidence:
      roles:
        hostile_review_records: authority
        gate_a_review_candidates: non_authoritative
      precedence: []
    bounded_verification_evidence:
      roles:
        bounded_verification_results: authority
      precedence: []
    repository_artifact_state:
      roles:
        repository_git_tree: authority
      precedence: []
    shared_governance_provider_adoption:
      roles:
        accepted_adrs: authority
        governance_binding_registry: secondary_representation
      precedence: []
    governance_contract_bindings:
      roles:
        governance_binding_registry: authority
      precedence: []
    executable_provider_binding:
      roles:
        executable_dependency_manifest: authority
        governance_binding_registry: secondary_representation
        effective_proto_ring_provider: secondary_representation
        proto_ring_environment: non_authoritative
      precedence: []
    projection_registry_profile:
      roles:
        projection_registry: authority
      precedence: []
    repository_integrity_profile:
      roles:
        repository_integrity_profile: authority
      precedence: []
    repository_validation_membership_order:
      roles:
        repository_integrity_profile: authority
        repository_validation_entrypoint: secondary_representation
      precedence: []
    repository_validation:
      roles:
        repository_integrity_profile: authority
      precedence: []
    evidence_requirement_registry:
      roles:
        evidence_requirement_registry: authority
      precedence: []
    adr_profile_route:
      roles:
        agents_governance_frontmatter: authority
      precedence: []
    shared_governance_provider_binding_route:
      roles:
        agents_governance_frontmatter: authority
      precedence: []
    governed_objects_profile_route:
      roles:
        agents_governance_frontmatter: authority
      precedence: []
    repository_agent_guardrails:
      roles:
        agents_directives: authority
      precedence: []
    repository_ci_bootstrap:
      roles:
        repository_integrity_ci: authority
      precedence: []
    engineering_work_state:
      roles:
        github_engineering_work_state: authority
      precedence: []
    discovery_classification_binding:
      roles:
        discovery_classification_profile: authority
      precedence: []
    vision_narrative:
      roles:
        turnlock_vision: authority
      precedence: []
---

# Turnlock-Rust Governance Authority profile

This profile is the canonical machine-readable mapping of Turnlock-Rust
repository-governance roles. Underlying TURNLOCK semantic, formal, review, and
evidence authority remains in the sources identified here. Contract identities
are owned by the routed Governance Binding Registry.
