#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
import unittest

import yaml

fixture = importlib.import_module("repository-integrity-test-fixture")
ROOT = fixture.ROOT
checker = fixture.checker


class RepositoryIntegrityBindingTests(unittest.TestCase):
    def test_canonical_validation_membership_and_order(self) -> None:
        expected = [
            (
                "ADR metadata provider binding tests",
                [
                    sys.executable,
                    "scripts/tests/test-adr-metadata-provider-binding.py",
                ],
            ),
            (
                "ADR metadata profile validation tests",
                [
                    sys.executable,
                    "scripts/tests/test-adr-metadata-profile-validation.py",
                ],
            ),
            (
                "ADR metadata migration evidence tests",
                [
                    sys.executable,
                    "scripts/tests/test-adr-metadata-migration-evidence.py",
                ],
            ),
            (
                "ADR metadata generated index tests",
                [
                    sys.executable,
                    "scripts/tests/test-adr-metadata-generated-index.py",
                ],
            ),
            (
                "ADR metadata annotated history tests",
                [
                    sys.executable,
                    "scripts/tests/test-adr-metadata-annotated-history.py",
                ],
            ),
            (
                "Formal traceability tests",
                [sys.executable, "scripts/tests/test-formal-traceability.py"],
            ),
            (
                "Exact Evidence Binding tests",
                [sys.executable, "scripts/tests/test-exact-evidence-binding.py"],
            ),
            (
                "Normative terminology tests",
                [sys.executable, "scripts/tests/test-normative-terminology.py"],
            ),
            (
                "Repository integrity binding tests",
                [
                    sys.executable,
                    "scripts/tests/test-repository-integrity-bindings.py",
                ],
            ),
            (
                "Repository integrity evaluator tests",
                [
                    sys.executable,
                    "scripts/tests/test-repository-integrity-evaluator.py",
                ],
            ),
            (
                "Repository integrity CLI tests",
                [
                    sys.executable,
                    "scripts/tests/test-repository-integrity-cli.py",
                ],
            ),
            (
                "Repository integrity validator purity tests",
                [
                    sys.executable,
                    "scripts/tests/test-repository-integrity-validator-purity.py",
                ],
            ),
            (
                "Governance test module size tests",
                [
                    sys.executable,
                    "scripts/tests/test-governance-test-module-size.py",
                ],
            ),
            (
                "Git whitespace tests",
                [sys.executable, "scripts/tests/test-git-whitespace.py"],
            ),
            (
                "ADR metadata check",
                [sys.executable, "scripts/adr-metadata.py", "check"],
            ),
            (
                "Accepted ADR body immutability",
                [
                    sys.executable,
                    "-m",
                    "proto_ring.accepted_adr_body",
                ],
            ),
            (
                "Shared Governance Provider binding",
                [
                    sys.executable,
                    "-m",
                    "proto_ring.shared_governance_provider",
                ],
            ),
            (
                "Governance Authority profile",
                [
                    sys.executable,
                    "scripts/check-governance-authority.py",
                ],
            ),
            (
                "Authoritative Ref Monotonicity effective rules",
                [
                    sys.executable,
                    "scripts/check-authoritative-ref-monotonicity.py",
                ],
            ),
            (
                "Normative terminology check",
                [sys.executable, "scripts/check-normative-terminology.py"],
            ),
            (
                "Formal traceability check",
                [sys.executable, "scripts/check-formal-traceability.py"],
            ),
            (
                "Git whitespace check",
                [sys.executable, "scripts/check-git-whitespace.py"],
            ),
        ]

        self.assertEqual(
            expected,
            checker.canonical_steps(),
        )

    def test_shared_profile_preserves_membership_order_and_continuation(
        self,
    ) -> None:
        steps = checker.canonical_steps()
        profile = checker._integrity_profile(steps)

        self.assertTrue(
            profile.continue_after_non_satisfied
        )

        self.assertEqual(
            [name for name, _argv in steps],
            [
                obligation.name
                for obligation in profile.obligations
            ],
        )

        self.assertEqual(
            [tuple(argv) for _name, argv in steps],
            [
                obligation.argv
                for obligation in profile.obligations
            ],
        )

        for obligation in profile.obligations:
            expected = (
                frozenset({2})
                if obligation.name
                == "Authoritative Ref Monotonicity effective rules"
                else frozenset()
            )
            self.assertEqual(
                expected,
                obligation.undetermined_exit_codes,
            )

    def test_requirements_pin_exact_current_provider(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "proto-ring @ git+https://github.com/fanilosendrison/proto-ring.git@305d968c50db17cce43199ae3fa78d64da2aabdb",
            requirements.splitlines(),
        )

        self.assertNotIn(
            "proto-ring.git@5b0d3a3493e01a4b9569ded7665d7a44a444bf35",
            requirements,
        )

    def test_authoritative_ref_monotonicity_binding(self) -> None:
        binding = (
            ROOT
            / "docs/repository-governance/turnlock-rust-authoritative-ref-monotonicity.md"
        ).read_text(encoding="utf-8")
        _prefix, frontmatter, _body = binding.split("---", 2)
        metadata = yaml.safe_load(frontmatter)
        configuration = metadata["authoritative_ref_monotonicity"]

        self.assertEqual(
            {
                "repository": "fanilosendrison/proto-ring",
                "commit": "650a481b7dfa7c4d3671bd053c63642a5dab1087",
                "path": "docs/contracts/authoritative-ref-monotonicity.md",
            },
            configuration["contract"],
        )
        self.assertEqual(
            {
                "provider": "github",
                "owner": "fanilosendrison",
                "name": "turnlock-rust",
            },
            configuration["repository"],
        )
        self.assertEqual("refs/heads/main", configuration["authoritative_ref"])
        protection = configuration["protection"]
        self.assertEqual("github-repository-ruleset", protection["mechanism"])
        self.assertIs(type(protection["ruleset_id"]), int)
        self.assertGreater(protection["ruleset_id"], 0)


if __name__ == "__main__":
    unittest.main()
