#!/usr/bin/env python3
from __future__ import annotations

import importlib
from pathlib import Path
import shutil
import tempfile
import unittest

from proto_ring import adr_metadata as shared_adr_metadata
from proto_ring import canonical_adr as shared_canonical_adr
from proto_ring import repository_governance_model as shared_repository_governance_model

fixture = importlib.import_module("adr-metadata-test-fixture")
ROOT = fixture.ROOT
adr_metadata = fixture.adr_metadata


class AdrMetadataTests(unittest.TestCase):
    def test_repository_passes_full_profile(self) -> None:
        self.assertEqual([], adr_metadata.collect_errors(ROOT))

    def test_shared_primitives_are_bound_to_pinned_provider(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn(
            "proto-ring.git@bef7d3c0a5d1ef170d95f3eb9c8114e11149f85d",
            requirements,
        )
        bindings = {
            "AdrMetadataError": shared_adr_metadata.AdrMetadataError,
            "decision_body_bytes": shared_adr_metadata.decision_body_bytes,
            "load_json": shared_adr_metadata.load_json,
            "load_yaml": shared_adr_metadata.load_yaml,
            "parse_adr": shared_adr_metadata.parse_adr,
            "preserved_payload_bytes": shared_adr_metadata.preserved_payload_bytes,
            "repository_path": shared_adr_metadata.repository_path,
            "schema_errors": shared_adr_metadata.schema_errors,
            "sha256_hex": shared_adr_metadata.sha256_hex,
        }
        for name, shared in bindings.items():
            with self.subTest(name=name):
                self.assertIs(getattr(adr_metadata, name), shared)

    def test_profile_path_resolution_delegates_to_shared_provider(self) -> None:
        model = shared_repository_governance_model.load(ROOT)
        self.assertEqual(model.model_version, 1)
        self.assertEqual(model.provider.id, "proto-ring")
        self.assertEqual(
            model.provider.binding.capability, "shared_governance_provider"
        )
        self.assertEqual(model.provider.binding.route, "binding")
        profile = model.capabilities["architecture_decisions"].routes["profile"]
        self.assertEqual(profile.declared_path, "docs/adr/adr-profile.yaml")
        self.assertEqual(profile.target, (ROOT / "docs/adr/adr-profile.yaml").resolve())
        shared_provider = model.capabilities["shared_governance_provider"]
        self.assertEqual(shared_provider.configuration, {"required": True})
        binding = shared_provider.routes["binding"]
        self.assertEqual(
            binding.declared_path,
            "docs/repository-governance/turnlock-rust-shared-governance-provider.md",
        )
        self.assertEqual(
            binding.target,
            (
                ROOT
                / "docs/repository-governance/turnlock-rust-shared-governance-provider.md"
            ).resolve(),
        )

        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            (repository / "AGENTS.md").write_text(
                "---\n"
                "repository_governance:\n"
                "  model_version: 1\n"
                "  provider:\n"
                '    id: "proto-ring"\n'
                "    binding:\n"
                '      capability: "shared_governance_provider"\n'
                '      route: "binding"\n'
                "  capabilities:\n"
                "    architecture_decisions:\n"
                "      configuration: {}\n"
                "      routes:\n"
                '        profile: "docs/adr/adr-profile.yaml"\n'
                "    shared_governance_provider:\n"
                "      configuration:\n"
                "        required: true\n"
                "      routes:\n"
                '        binding: "binding.md"\n'
                "---\n"
                "# Directives\n\n"
                "repository_governance:\n"
                "  fake: true\n",
                encoding="utf-8",
            )
            profile_target = repository / "docs/adr/adr-profile.yaml"
            profile_target.parent.mkdir(parents=True)
            profile_target.write_text("test profile\n", encoding="utf-8")
            (repository / "binding.md").write_text("test binding\n", encoding="utf-8")
            fixture_model = shared_repository_governance_model.load(repository)
        self.assertEqual(fixture_model.model_version, 1)
        self.assertNotIn("fake", fixture_model.capabilities)

        self.assertIs(
            adr_metadata.configured_profile_path,
            shared_canonical_adr.configured_profile_path,
        )
        self.assertEqual(
            adr_metadata.configured_profile_path(ROOT),
            (ROOT / "docs/adr/adr-profile.yaml").resolve(),
        )

    def test_adr_051_resolves_and_outside_same_id_is_ignored(self) -> None:
        authority = shared_canonical_adr.resolve(ROOT, "ADR-051")
        self.assertEqual(
            authority.path,
            (
                ROOT
                / "docs/adr/adr-051-require-proto-ring-for-applicable-generic-repository-governance.md"
            ).resolve(),
        )

        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = fixture.make_adr_fixture(temporary)
            outside = fixture_root / "outside/adr-051-impostor.md"
            outside.parent.mkdir(parents=True)
            shutil.copyfile(authority.path, outside)

            resolved = shared_canonical_adr.resolve(fixture_root, "ADR-051")
            self.assertEqual(
                resolved.path,
                (
                    fixture_root
                    / "docs/adr/adr-051-require-proto-ring-for-applicable-generic-repository-governance.md"
                ).resolve(),
            )


if __name__ == "__main__":
    unittest.main()
