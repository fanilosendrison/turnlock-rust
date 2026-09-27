#!/usr/bin/env python3
from __future__ import annotations

import importlib
import re
import tempfile
import unittest

fixture = importlib.import_module("adr-metadata-test-fixture")
adr_metadata = fixture.adr_metadata
make_adr_fixture = fixture.make_adr_fixture
history_text = fixture.history_text
write_history = fixture.write_history


class AdrMetadataTests(unittest.TestCase):
    def test_annotated_history_missing_latest_adr_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_adr_fixture(temporary)
            latest = max(
                int(path.name.split("-", 2)[1])
                for path in (fixture_root / "docs" / "adr").glob(
                    "adr-[0-9][0-9][0-9]-*.md"
                )
            )
            text = history_text(fixture_root)
            pattern = re.compile(
                rf"(?ms)^{latest}\. \[ADR-{latest:03d}:.*?"
                r"(?=^<!-- adr-annotated-trace:end -->)"
            )
            self.assertIsNotNone(pattern.search(text))
            write_history(fixture_root, pattern.sub("", text, count=1))

            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any(
                    f"missing ADR-{latest:03d}" in error
                    or "coverage/order mismatch" in error
                    for error in errors
                ),
                errors,
            )

    def test_annotated_history_duplicate_and_reordered_entries_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_adr_fixture(temporary)
            text = history_text(fixture_root)

            first_entry = re.search(
                r"(?ms)^1\. \[ADR-001:.*?(?=^2\. \[ADR-002:)", text
            )
            self.assertIsNotNone(first_entry)
            duplicated = text.replace(
                "2. [ADR-002:", first_entry.group(0) + "2. [ADR-002:", 1
            )
            write_history(fixture_root, duplicated)
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("contains duplicate ADR-001" in error for error in errors), errors
            )

            entry_five = re.search(
                r"(?ms)^5\. \[ADR-005:.*?(?=^6\. \[ADR-006:)", text
            )
            entry_six = re.search(
                r"(?ms)^6\. \[ADR-006:.*?(?=^7\. \[ADR-007:)", text
            )
            self.assertIsNotNone(entry_five)
            self.assertIsNotNone(entry_six)
            reordered = text.replace(
                entry_five.group(0) + entry_six.group(0),
                entry_six.group(0) + entry_five.group(0),
                1,
            )
            write_history(fixture_root, reordered)
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("coverage/order mismatch" in error for error in errors), errors
            )

    def test_annotated_history_title_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_adr_fixture(temporary)
            text = history_text(fixture_root)
            original = (
                "[ADR-017: Adopt validated OKF Architecture Decision Record metadata]"
            )
            self.assertIn(original, text)
            write_history(
                fixture_root,
                text.replace(original, "[ADR-017: Tampered title]", 1),
            )
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("ADR-017 title mismatch" in error for error in errors), errors
            )

    def test_annotated_history_link_target_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_adr_fixture(temporary)
            adr_directory = fixture_root / "docs" / "adr"
            first_name = next(adr_directory.glob("adr-001-*.md")).name
            second_name = next(adr_directory.glob("adr-002-*.md")).name
            text = history_text(fixture_root)

            inline_mutated = text.replace(
                "[ADR-001: Make the workflow own orchestration after session entry]"
                f"({first_name})",
                "[ADR-001: Make the workflow own orchestration after session entry]"
                f"({second_name})",
                1,
            )
            write_history(fixture_root, inline_mutated)
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("ADR-001 link target mismatch" in error for error in errors),
                errors,
            )

            latest_name = next(adr_directory.glob("adr-031-*.md")).name
            other_name = next(adr_directory.glob("adr-030-*.md")).name
            reference_mutated = text.replace(
                f"[31]: {latest_name}", f"[31]: {other_name}", 1
            )
            write_history(fixture_root, reference_mutated)
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("ADR-031 link target mismatch" in error for error in errors),
                errors,
            )

    def test_annotated_history_status_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_adr_fixture(temporary)
            text = history_text(fixture_root)
            marker = "[17] —\n    **Accepted**"
            self.assertIn(marker, text)
            write_history(
                fixture_root,
                text.replace(marker, "[17] —\n    **Superseded**", 1),
            )
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("ADR-017 status mismatch" in error for error in errors), errors
            )

    def test_annotated_history_missing_annotation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_adr_fixture(temporary)
            text = history_text(fixture_root)
            pattern = re.compile(
                r"(?ms)^17\. \[ADR-017:.*?(?=^18\. \[ADR-018:)"
            )
            self.assertEqual(1, len(pattern.findall(text)))
            replacement = (
                "17. [ADR-017: Adopt validated OKF Architecture Decision Record "
                "metadata][17] —\n    **Accepted**\n\n"
            )
            write_history(fixture_root, pattern.sub(replacement, text, count=1))
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any(
                    "ADR-017 has no narrative annotation" in error
                    for error in errors
                ),
                errors,
            )

    def test_annotated_history_marker_corruption_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_adr_fixture(temporary)
            text = history_text(fixture_root)
            start = "<!-- adr-annotated-trace:start -->"
            end = "<!-- adr-annotated-trace:end -->"
            self.assertIn(start, text)
            self.assertIn(end, text)

            write_history(fixture_root, text.replace(start, "", 1))
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any(
                    "start marker missing or duplicated" in error
                    for error in errors
                ),
                errors,
            )

            write_history(fixture_root, text.replace(end, end + "\n" + end, 1))
            errors = adr_metadata.collect_errors(fixture_root)
            self.assertTrue(
                any("end marker missing or duplicated" in error for error in errors),
                errors,
            )

    def test_historical_adr_ranges_outside_markers_remain_legal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_adr_fixture(temporary)
            self.assertEqual([], adr_metadata.collect_errors(fixture_root))
            text = history_text(fixture_root)
            end = "<!-- adr-annotated-trace:end -->"
            snapshot = (
                "Historical snapshot outside the current trace: "
                "ADR-001 through ADR-016 were reconstructed in this repository.\n"
            )
            write_history(fixture_root, text.replace(end, end + "\n" + snapshot, 1))
            self.assertEqual([], adr_metadata.collect_errors(fixture_root))


if __name__ == "__main__":
    unittest.main()
