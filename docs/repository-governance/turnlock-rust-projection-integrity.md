---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "projection-registry"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust Projection Registry"

projection_registry:
  model_version: 1
  authority:
    responsibility: projection_registry_profile
    source: projection_registry
  projections:
    adr_index:
      responsibility: adr_metadata
      canonical_source: canonical_adr_records
      secondary_source: adr_index
      mode: generated
      validation: adr_metadata_generated_index_tests
      generator_source: adr_index_generator
    adr_annotated_history:
      responsibility: adr_metadata
      canonical_source: canonical_adr_records
      secondary_source: adr_history
      mode: mechanically_validated_maintained
      validation: adr_metadata_annotated_history_tests
    formal_invariant_mapping:
      responsibility: formal_assurance_graph
      canonical_source: formal_assurance_manifest
      secondary_source: formal_assurance_mapping
      mode: generated
      validation: formal_traceability_check
      generator_source: formal_mapping_generator
    governed_adr_catalog:
      responsibility: accepted_decisions
      canonical_source: accepted_adrs
      secondary_source: governed_objects_profile
      mode: mechanically_validated_maintained
      validation: governed_objects_profile
    governed_invariant_catalog:
      responsibility: stable_invariant_definitions
      canonical_source: turnlock_spec
      secondary_source: governed_objects_profile
      mode: mechanically_validated_maintained
      validation: governed_objects_profile
    governed_formal_claim_catalog:
      responsibility: formal_assurance_graph
      canonical_source: formal_assurance_manifest
      secondary_source: governed_objects_profile
      mode: mechanically_validated_maintained
      validation: governed_objects_profile
    executable_binding_registry_representation:
      responsibility: executable_provider_binding
      canonical_source: executable_dependency_manifest
      secondary_source: governance_binding_registry
      mode: mechanically_validated_maintained
      validation: proto_ring_binding_registry_currentness
      binding: proto_ring_executable
    effective_proto_ring_realization:
      responsibility: executable_provider_binding
      canonical_source: executable_dependency_manifest
      secondary_source: effective_proto_ring_provider
      mode: generated
      validation: proto_ring_provider_currentness
      generator_source: proto_ring_environment
      binding: proto_ring_executable
---

# Turnlock-Rust Projection Registry

The registry contains only direct authority-to-secondary relationships. Commands,
installation mechanics, qualification truth, and TURNLOCK semantics remain
outside Projection Integrity.
