#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "adr-metadata.py"

spec = importlib.util.spec_from_file_location("adr_metadata", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")
adr_metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adr_metadata)


def disable_git_bound_validation(fixture_root: Path) -> None:
    profile_path = fixture_root / "docs" / "adr" / "adr-profile.yaml"
    profile = adr_metadata.load_yaml(profile_path)
    profile["migration_evidence"] = {
        "path": "docs/adr/metadata-migration-evidence.yaml",
        "required": False,
        "baseline_commit": None,
        "ids": [],
    }
    profile["generated_index"]["required"] = False
    profile_path.write_text(
        adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
    )


class AdrMetadataTests(unittest.TestCase):
    def test_repository_passes_full_profile(self) -> None:
        self.assertEqual([], adr_metadata.collect_errors(ROOT))

    def test_calendar_aware_schema_validation_rejects_invalid_dates(self) -> None:
        adr_path = next((ROOT / "docs" / "adr").glob("adr-017-*.md"))
        metadata, _ = adr_metadata.parse_adr(adr_path)
        profile = adr_metadata.load_yaml(ROOT / "docs" / "adr" / "adr-profile.yaml")
        base = adr_metadata.load_json(ROOT / profile["canonical_schema"]["vendored_path"])
        overlay = adr_metadata.load_json(ROOT / profile["local_overlay"]["path"])

        for invalid_date in ("2026-13-01", "2026-04-31", "2025-02-29"):
            with self.subTest(date=invalid_date):
                candidate = copy.deepcopy(metadata)
                candidate["date"] = invalid_date
                errors = adr_metadata.schema_errors(candidate, base, overlay)
                self.assertTrue(any("date" in error for error in errors), errors)

        candidate = copy.deepcopy(metadata)
        candidate["date"] = "2024-02-29"
        self.assertEqual([], adr_metadata.schema_errors(candidate, base, overlay))

    def test_body_digest_uses_exact_context_suffix(self) -> None:
        payload = b"# ADR-999: Example\n\n## Context\n\nExact body.\n"
        body = adr_metadata.decision_body_bytes(payload)
        self.assertEqual(b"## Context\n\nExact body.\n", body)
        self.assertEqual(
            "c9e5f9b055e1d65ed6fbb2c8ff85f9f2d2bdcbeeb087cbbef5b63837f12dadd4",
            adr_metadata.sha256_hex(body),
        )

        for invalid in (b"\xef\xbb\xbf" + payload, payload.replace(b"\n", b"\r\n")):
            with self.subTest(payload=invalid[:8]):
                with self.assertRaises(adr_metadata.AdrMetadataError):
                    adr_metadata.decision_body_bytes(invalid)

    def test_unknown_and_stale_legacy_entries_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = Path(temporary)
            shutil.copytree(ROOT / "docs" / "adr", fixture_root / "docs" / "adr")
            disable_git_bound_validation(fixture_root)

            unknown = fixture_root / "docs" / "adr" / "adr-018-unlisted-record.md"
            unknown.write_text(
                "# ADR-018: Unlisted record\n\n## Context\n\nLegacy body.\n",
                encoding="utf-8",
            )
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("ADR-018 is frontmatter-free but not allowlisted" in error for error in errors),
                errors,
            )

            unknown.unlink()
            profile_path = fixture_root / "docs" / "adr" / "adr-profile.yaml"
            profile = adr_metadata.load_yaml(profile_path)
            profile["legacy"]["without_frontmatter"] = ["ADR-016"]
            profile_path.write_text(
                adr_metadata.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
            )
            legacy_path = next((fixture_root / "docs" / "adr").glob("adr-016-*.md"))
            legacy_path.unlink()
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("stale legacy without_frontmatter entry ADR-016" in error for error in errors),
                errors,
            )

    def test_empty_overlay_cannot_disable_base_schema_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = Path(temporary)
            shutil.copytree(ROOT / "docs" / "adr", fixture_root / "docs" / "adr")
            disable_git_bound_validation(fixture_root)
            overlay = (
                fixture_root
                / "docs"
                / "adr"
                / "schemas"
                / "turnlock-architecture-decision-record.schema.json"
            )
            overlay.write_text("{}\n", encoding="utf-8")
            adr_path = next((fixture_root / "docs" / "adr").glob("adr-017-*.md"))
            adr_path.write_text(
                adr_path.read_text(encoding="utf-8").replace(
                    'severity: "strict"', 'severity: "invalid"'
                ),
                encoding="utf-8",
            )

            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(any("local overlay $id mismatch" in error for error in errors), errors)
            self.assertTrue(any("severity" in error for error in errors), errors)

    def test_matching_overlay_id_without_local_constraints_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = Path(temporary)
            shutil.copytree(ROOT / "docs" / "adr", fixture_root / "docs" / "adr")
            disable_git_bound_validation(fixture_root)
            overlay = (
                fixture_root
                / "docs"
                / "adr"
                / "schemas"
                / "turnlock-architecture-decision-record.schema.json"
            )
            overlay.write_text(
                '{\n  "$id": '
                '"urn:fanilosendrison:turnlock-rust:architecture-decision-record:0.1.0"\n}\n',
                encoding="utf-8",
            )
            adr_path = next((fixture_root / "docs" / "adr").glob("adr-017-*.md"))
            adr_path.write_text(
                adr_path.read_text(encoding="utf-8").replace(
                    'domain: "turnlock-rust"', 'domain: "wrong-domain"'
                ),
                encoding="utf-8",
            )

            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("local overlay domain constraint mismatch" in error for error in errors),
                errors,
            )

    def test_misnamed_adr_candidate_is_not_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = Path(temporary)
            shutil.copytree(ROOT / "docs" / "adr", fixture_root / "docs" / "adr")
            disable_git_bound_validation(fixture_root)
            adr_path = next((fixture_root / "docs" / "adr").glob("adr-017-*.md"))
            shutil.copyfile(adr_path, fixture_root / "docs" / "adr" / "wrong-name.md")

            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("wrong-name.md" in error and "filename" in error for error in errors),
                errors,
            )

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

    def test_body_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = Path(temporary)
            shutil.copytree(ROOT / "docs" / "adr", fixture_root / "docs" / "adr")
            disable_git_bound_validation(fixture_root)
            adr_path = next((fixture_root / "docs" / "adr").glob("adr-017-*.md"))
            text = adr_path.read_text(encoding="utf-8")
            text = text.replace(
                'decision_body_sha256: "633565f0e825c7bda0cd5c33ad19e15323e55055cccb98aacf5924cd48f1b503"',
                'decision_body_sha256: "0000000000000000000000000000000000000000000000000000000000000000"',
            )
            adr_path.write_text(text, encoding="utf-8")
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(any("decision_body_sha256 mismatch" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
