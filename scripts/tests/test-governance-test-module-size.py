#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

RETIRED_TEST_MODULES = (
    "scripts/tests/test-adr-metadata.py",
    "scripts/tests/test-repository-integrity.py",
)

GOVERNANCE_SOURCE_MODULES = (
    "scripts/check-authoritative-ref-monotonicity.py",
    "scripts/check-governed-objects.py",
    "scripts/check-proto-ring-binding-registry.py",
    "scripts/check-proto-ring-provider.py",
    "scripts/proto_ring_executable_binding.py",
    "scripts/check-repository-integrity.py",
    "scripts/check-structured-governance.py",
    "scripts/tests/adr-metadata-test-fixture.py",
    "scripts/tests/repository-integrity-test-fixture.py",
    "scripts/tests/test-adr-metadata-provider-binding.py",
    "scripts/tests/test-adr-metadata-profile-validation.py",
    "scripts/tests/test-adr-metadata-migration-evidence.py",
    "scripts/tests/test-adr-metadata-generated-index.py",
    "scripts/tests/test-adr-metadata-annotated-history.py",
    "scripts/tests/test-exact-evidence-binding.py",
    "scripts/tests/test-governed-objects.py",
    "scripts/tests/test-proto-ring-binding-registry.py",
    "scripts/tests/test-proto-ring-provider.py",
    "scripts/tests/test-repository-integrity-bindings.py",
    "scripts/tests/test-repository-integrity-evaluator.py",
    "scripts/tests/test-repository-integrity-cli.py",
    "scripts/tests/test-repository-integrity-validator-purity.py",
    "scripts/tests/test-structured-governance.py",
    "scripts/tests/test-governance-test-module-size.py",
)


class GovernanceTestModuleSizeTests(unittest.TestCase):
    def test_retired_catch_all_modules_remain_absent(self) -> None:
        for relative in RETIRED_TEST_MODULES:
            with self.subTest(relative=relative):
                self.assertFalse((ROOT / relative).exists())

    def test_cohesive_governance_modules_remain_within_line_limit(self) -> None:
        for relative in GOVERNANCE_SOURCE_MODULES:
            with self.subTest(relative=relative):
                path = ROOT / relative
                self.assertTrue(path.is_file())
                line_count = path.read_bytes().count(b"\n")
                self.assertLessEqual(line_count, 400, f"{relative}: {line_count} lines")


if __name__ == "__main__":
    unittest.main()
