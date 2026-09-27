#!/usr/bin/env python3
from __future__ import annotations

import importlib
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

fixture = importlib.import_module("adr-metadata-test-fixture")
ROOT = fixture.ROOT
adr_metadata = fixture.adr_metadata
disable_git_bound_validation = fixture.disable_git_bound_validation


class AdrMetadataTests(unittest.TestCase):
    def test_renderer_projects_outgoing_and_derived_incoming_relations(self) -> None:
        records = [
            {
                "id": "ADR-001",
                "number": 1,
                "path": Path("docs/adr/adr-001-first.md"),
                "metadata": {
                    "name": "First",
                    "status": "accepted",
                    "date": "2026-09-13",
                    "relation_completeness": "complete",
                    "governs": [],
                    "relations": {
                        "clarifies": [],
                        "amends": [],
                        "supersedes": [],
                        "confirms": [],
                    },
                },
            },
            {
                "id": "ADR-002",
                "number": 2,
                "path": Path("docs/adr/adr-002-second.md"),
                "metadata": {
                    "name": "Second",
                    "status": "accepted",
                    "date": "2026-09-13",
                    "relation_completeness": "complete",
                    "governs": [],
                    "relations": {
                        "clarifies": ["ADR-001"],
                        "amends": [],
                        "supersedes": [],
                        "confirms": [],
                    },
                },
            },
        ]
        profile = {"repository": {"domain": "turnlock-rust"}}
        with mock.patch.object(
            adr_metadata, "_structured_records", return_value=(profile, records)
        ):
            rendered = adr_metadata.render_index(ROOT)
        self.assertIn("| [ADR-002](adr-002-second.md) | clarifies |", rendered)
        self.assertIn("| [ADR-001](adr-001-first.md) | clarified by |", rendered)

    def test_stale_generated_index_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = Path(temporary)
            shutil.copytree(ROOT / "docs" / "adr", fixture_root / "docs" / "adr")
            disable_git_bound_validation(fixture_root)
            profile_path = fixture_root / "docs" / "adr" / "adr-profile.yaml"
            profile = adr_metadata.load_yaml(profile_path)
            profile["generated_index"]["required"] = True
            profile_path.write_text(
                adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
            )
            (fixture_root / "docs" / "adr" / "index.md").write_text(
                "stale\n", encoding="utf-8"
            )
            with mock.patch.object(
                adr_metadata, "render_index", return_value="expected\n"
            ):
                errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(any("generated ADR index is stale" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
