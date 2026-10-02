---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "repository-integrity-profile"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust Repository Integrity profile"

repository_integrity:
  model_version: 1
  authority:
    responsibility: repository_integrity_profile
    source: repository_integrity_profile
  environments:
    - turnlock_python
  continue_after_non_satisfied: true
  validations:
    adr_metadata_provider_binding_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-adr-metadata-provider-binding.py], undetermined_exit_codes: []}
    adr_metadata_profile_validation_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-adr-metadata-profile-validation.py], undetermined_exit_codes: []}
    adr_metadata_migration_evidence_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-adr-metadata-migration-evidence.py], undetermined_exit_codes: []}
    adr_metadata_generated_index_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-adr-metadata-generated-index.py], undetermined_exit_codes: []}
    adr_metadata_annotated_history_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-adr-metadata-annotated-history.py], undetermined_exit_codes: []}
    formal_traceability_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-formal-traceability.py], undetermined_exit_codes: []}
    exact_evidence_binding_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-exact-evidence-binding.py], undetermined_exit_codes: []}
    structured_governance_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-structured-governance.py], undetermined_exit_codes: []}
    proto_ring_binding_registry_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-proto-ring-binding-registry.py], undetermined_exit_codes: []}
    proto_ring_provider_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-proto-ring-provider.py], undetermined_exit_codes: []}
    governed_objects_profile_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-governed-objects.py], undetermined_exit_codes: []}
    normative_terminology_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-normative-terminology.py], undetermined_exit_codes: []}
    repository_integrity_binding_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-repository-integrity-bindings.py], undetermined_exit_codes: []}
    repository_integrity_evaluator_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-repository-integrity-evaluator.py], undetermined_exit_codes: []}
    repository_integrity_cli_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-repository-integrity-cli.py], undetermined_exit_codes: []}
    repository_integrity_validator_purity_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-repository-integrity-validator-purity.py], undetermined_exit_codes: []}
    governance_test_module_size_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-governance-test-module-size.py], undetermined_exit_codes: []}
    git_whitespace_tests:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/tests/test-git-whitespace.py], undetermined_exit_codes: []}
    adr_metadata_check:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/adr-metadata.py, check], undetermined_exit_codes: []}
    accepted_adr_body_immutability:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [-m, proto_ring.accepted_adr_body], undetermined_exit_codes: []}
    proto_ring_binding_registry_currentness:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/check-proto-ring-binding-registry.py], undetermined_exit_codes: []}
    proto_ring_provider_currentness:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/check-proto-ring-provider.py], undetermined_exit_codes: []}
    structured_governance_check:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/check-structured-governance.py], undetermined_exit_codes: []}
    governance_authority_profile:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/check-governance-authority.py], undetermined_exit_codes: []}
    governed_objects_profile:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/check-governed-objects.py], undetermined_exit_codes: []}
    authoritative_ref_monotonicity_effective_rules:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/check-authoritative-ref-monotonicity.py], undetermined_exit_codes: [2]}
    normative_terminology_check:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/check-normative-terminology.py], undetermined_exit_codes: []}
    formal_traceability_check:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/check-formal-traceability.py], undetermined_exit_codes: []}
    git_whitespace_check:
      responsibility: repository_validation
      prerequisites: []
      instances: {kind: single}
      command: {kind: command, environment: turnlock_python, arguments: [scripts/check-git-whitespace.py], undetermined_exit_codes: []}
  order:
    - adr_metadata_provider_binding_tests
    - adr_metadata_profile_validation_tests
    - adr_metadata_migration_evidence_tests
    - adr_metadata_generated_index_tests
    - adr_metadata_annotated_history_tests
    - formal_traceability_tests
    - exact_evidence_binding_tests
    - structured_governance_tests
    - proto_ring_binding_registry_tests
    - proto_ring_provider_tests
    - governed_objects_profile_tests
    - normative_terminology_tests
    - repository_integrity_binding_tests
    - repository_integrity_evaluator_tests
    - repository_integrity_cli_tests
    - repository_integrity_validator_purity_tests
    - governance_test_module_size_tests
    - git_whitespace_tests
    - adr_metadata_check
    - accepted_adr_body_immutability
    - proto_ring_binding_registry_currentness
    - proto_ring_provider_currentness
    - structured_governance_check
    - governance_authority_profile
    - governed_objects_profile
    - authoritative_ref_monotonicity_effective_rules
    - normative_terminology_check
    - formal_traceability_check
    - git_whitespace_check
---

# Turnlock-Rust Repository Integrity profile

This profile is the sole authority for mandatory validation membership and
order. Runtime executable paths and process environments are supplied through
the `turnlock_python` evaluation context.
