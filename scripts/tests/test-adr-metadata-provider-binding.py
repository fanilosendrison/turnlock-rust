#!/usr/bin/env python3
from __future__ import annotations

import importlib
import unittest

from proto_ring import adr_metadata as shared_adr_metadata

fixture = importlib.import_module("adr-metadata-test-fixture")
ROOT = fixture.ROOT
adr_metadata = fixture.adr_metadata


class AdrMetadataTests(unittest.TestCase):
    def test_repository_passes_full_profile(self) -> None:
        self.assertEqual([], adr_metadata.collect_errors(ROOT))

    def test_shared_primitives_are_bound_to_pinned_provider(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn(
            "proto-ring.git@743d0e7142b84364ba47700e4774b94752670320",
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


if __name__ == "__main__":
    unittest.main()
