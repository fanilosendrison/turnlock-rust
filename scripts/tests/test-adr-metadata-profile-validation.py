#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib
from pathlib import Path
import shutil
import tempfile
import unittest

fixture = importlib.import_module("adr-metadata-test-fixture")
ROOT = fixture.ROOT
adr_metadata = fixture.adr_metadata
disable_git_bound_validation = fixture.disable_git_bound_validation


class AdrMetadataTests(unittest.TestCase):
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

        invalid_base = copy.deepcopy(base)
        invalid_base["type"] = 123
        first_errors = adr_metadata.schema_errors(metadata, invalid_base, overlay)
        second_errors = adr_metadata.schema_errors(metadata, invalid_base, overlay)
        self.assertEqual(first_errors, second_errors)
        self.assertEqual(
            1,
            sum(
                error.startswith("base schema is invalid:")
                for error in first_errors
            ),
        )

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

            retained_numbers = [
                int(path.name.split("-", 2)[1])
                for path in (fixture_root / "docs" / "adr").glob("adr-[0-9][0-9][0-9]-*.md")
            ]
            unknown_number = max(retained_numbers) + 1
            unknown_id = f"ADR-{unknown_number:03d}"
            unknown = (
                fixture_root
                / "docs"
                / "adr"
                / f"adr-{unknown_number:03d}-unlisted-record.md"
            )
            unknown.write_text(
                f"# {unknown_id}: Unlisted record\n\n## Context\n\nLegacy body.\n",
                encoding="utf-8",
            )
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any(
                    f"{unknown_id} is frontmatter-free but not allowlisted" in error
                    for error in errors
                ),
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
