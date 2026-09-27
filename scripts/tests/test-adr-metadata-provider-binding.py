#!/usr/bin/env python3
from __future__ import annotations

import importlib
import shutil
import tempfile
import unittest

from proto_ring import adr_metadata as shared_adr_metadata
from proto_ring import canonical_adr as shared_canonical_adr

fixture = importlib.import_module("adr-metadata-test-fixture")
ROOT = fixture.ROOT
adr_metadata = fixture.adr_metadata


class AdrMetadataTests(unittest.TestCase):
    def test_repository_passes_full_profile(self) -> None:
        self.assertEqual([], adr_metadata.collect_errors(ROOT))

    def test_shared_primitives_are_bound_to_pinned_provider(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn(
            "proto-ring.git@f7d07f23c8c3969166142049dd91c78ed4bc80fa",
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
