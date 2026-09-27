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
    def test_fabricated_migration_baseline_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = Path(temporary)
            shutil.copytree(ROOT / "docs" / "adr", fixture_root / "docs" / "adr")
            disable_git_bound_validation(fixture_root)
            profile_path = fixture_root / "docs" / "adr" / "adr-profile.yaml"
            profile = adr_metadata.load_yaml(profile_path)
            profile["migration_evidence"] = {
                "path": "docs/adr/metadata-migration-evidence.yaml",
                "required": True,
                "baseline_commit": "0" * 40,
                "ids": ["ADR-017"],
            }
            profile_path.write_text(
                adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
            )
            adr_path = next((fixture_root / "docs" / "adr").glob("adr-017-*.md"))
            metadata, body = adr_metadata.parse_adr(adr_path)
            digest = adr_metadata.sha256_hex(body)
            evidence = {
                "schema_version": 1,
                "profile_version": "0.1.0",
                "baseline_commit": "0" * 40,
                "records": [
                    {
                        "id": "ADR-017",
                        "path": adr_path.relative_to(fixture_root).as_posix(),
                        "before_decision_body_sha256": digest,
                        "after_decision_body_sha256": digest,
                        "baseline_file_sha256": digest,
                        "migrated_payload_sha256": digest,
                    }
                ],
            }
            (fixture_root / "docs" / "adr" / "metadata-migration-evidence.yaml").write_text(
                adr_metadata.yaml.safe_dump(evidence, sort_keys=False), encoding="utf-8"
            )

            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(any("baseline commit" in error for error in errors), errors)

    def test_migration_evidence_preserves_exact_h1_to_eof_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = Path(temporary)
            shutil.copytree(ROOT / "docs" / "adr", fixture_root / "docs" / "adr")
            disable_git_bound_validation(fixture_root)
            profile_path = fixture_root / "docs" / "adr" / "adr-profile.yaml"
            profile = adr_metadata.load_yaml(profile_path)
            baseline = "1" * 40
            profile["migration_evidence"] = {
                "path": "docs/adr/metadata-migration-evidence.yaml",
                "required": True,
                "baseline_commit": baseline,
                "ids": ["ADR-017"],
            }
            profile_path.write_text(
                adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
            )
            adr_path = next((fixture_root / "docs" / "adr").glob("adr-017-*.md"))
            current_data = adr_path.read_bytes()
            baseline_payload = adr_metadata.preserved_payload_bytes(current_data)
            body = adr_metadata.decision_body_bytes(baseline_payload)
            digest = adr_metadata.sha256_hex(body)
            evidence = {
                "schema_version": 1,
                "profile_version": "0.1.0",
                "baseline_commit": baseline,
                "records": [
                    {
                        "id": "ADR-017",
                        "path": adr_path.relative_to(fixture_root).as_posix(),
                        "baseline_file_sha256": adr_metadata.sha256_hex(
                            baseline_payload
                        ),
                        "migrated_payload_sha256": adr_metadata.sha256_hex(
                            baseline_payload
                        ),
                        "before_decision_body_sha256": digest,
                        "after_decision_body_sha256": digest,
                    }
                ],
            }
            (fixture_root / "docs" / "adr" / "metadata-migration-evidence.yaml").write_text(
                adr_metadata.yaml.safe_dump(evidence, sort_keys=False), encoding="utf-8"
            )
            successful_git = mock.Mock(returncode=0, stderr=b"")
            with mock.patch.object(
                adr_metadata.subprocess, "run", return_value=successful_git
            ), mock.patch.object(
                adr_metadata, "_git_baseline_blob", return_value=baseline_payload
            ):
                self.assertEqual([], adr_metadata.collect_errors(fixture_root))

            h1 = b"# ADR-017: Adopt validated OKF Architecture Decision Record metadata\n"
            adr_path.write_bytes(
                current_data.replace(
                    h1,
                    h1 + b"\n- **Historical metadata:** changed\n",
                    1,
                )
            )
            with mock.patch.object(
                adr_metadata.subprocess, "run", return_value=successful_git
            ), mock.patch.object(
                adr_metadata, "_git_baseline_blob", return_value=baseline_payload
            ):
                errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("H1-to-EOF payload differs from baseline" in error for error in errors),
                errors,
            )


if __name__ == "__main__":
    unittest.main()
