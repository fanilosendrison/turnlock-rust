---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "governance-authority-profile"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust Governance Authority profile"

governance_authority_contract:
  repository: "fanilosendrison/proto-ring"
  commit: "22965fb97be23d7b43b8517b6786d65f5b8a41db"
  path: "docs/contracts/governance-authority.md"

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
    formal_assurance_manifest:
      repository_target: "formal/verification.yaml"
    formal_assurance_mapping:
      repository_target: "docs/formal/invariant-mapping.md"
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
    shared_governance_provider_binding:
      repository_target: "docs/repository-governance/turnlock-rust-shared-governance-provider.md"
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
      precedence: []
    canonical_terminology:
      roles:
        turnlock_spec: authority
        terminology_inventory: non_authoritative
      precedence: []
    accepted_decisions:
      roles:
        accepted_adrs: authority
      precedence: []
    adr_metadata:
      roles:
        canonical_adr_records: authority
        adr_index: secondary_representation
        adr_history: secondary_representation
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
      precedence: []
    canonical_formal_semantics:
      roles: {}
      precedence: []
    hostile_review_evidence:
      roles:
        hostile_review_records: authority
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
        shared_governance_provider_binding: secondary_representation
      precedence: []
    adr_profile_route:
      roles:
        agents_governance_frontmatter: authority
      precedence: []
    shared_governance_provider_binding_route:
      roles:
        agents_governance_frontmatter: authority
      precedence: []
    repository_agent_guardrails:
      roles:
        agents_directives: authority
      precedence: []
    repository_validation_membership_order:
      roles:
        repository_validation_entrypoint: authority
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
governance authority roles. Underlying Turnlock semantic authority remains in
the sources identified here. The immutable proto-ring contract pin governs only
the generic representation. Body prose does not replace the structured mapping.
