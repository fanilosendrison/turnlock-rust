#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CHECKER_PATH = SCRIPTS / "check-normative-terminology.py"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
SPEC = ROOT / "docs/specification/turnlock-spec.md"
INVENTORY = ROOT / "docs/specification/terminology-inventory.yaml"
FIXTURE_SPEC = """# Example

# 0. Product intent

Alpha supports the product promise.

# 2. Core mental model

<!-- normative-terminology-registry:start -->
| Concept key | Canonical term | Canonical anchor | Accepted aliases | Deprecated wording | Term structure |
| ----------- | -------------- | ---------------- | ---------------- | ------------------ | -------------- |
| `alpha` | `alpha` | [`term-alpha`](#term-alpha) | `first concept` | — | base |
| `beta` | `beta region` | [`term-beta`](#term-beta) | `bounded region` | — | compound |
<!-- normative-terminology-registry:end -->

## 2.1 Alpha

<a id="term-alpha"></a>

An **alpha** is the first canonical concept.

<a id="term-beta"></a>

A **beta region** is a separate compound concept.

# 3. Obligations

Alpha MUST satisfy its obligation.

# 5. Implications

Alpha requires a boundary.

# 8. Synopsis

Alpha refers to the canonical concept.
"""


def load_checker():
    spec = importlib.util.spec_from_file_location("check_normative_terminology", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load terminology checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


def inventory_for(document: str) -> dict[str, object]:
    entries, registry_errors = checker.parse_registry(document)
    if registry_errors:
        raise AssertionError(registry_errors)
    occurrences, occurrence_errors = checker.discover_occurrences(document, entries)
    if occurrence_errors:
        raise AssertionError(occurrence_errors)
    return {
        "schema_version": 1,
        "authority": "non-authoritative-review-inventory",
        "source": "docs/specification/turnlock-spec.md",
        "fingerprint": {
            "algorithm": "sha256",
            "normalization": "collapse-whitespace",
        },
        "occurrences": [checker.occurrence_record(item) for item in occurrences],
    }


class NormativeTerminologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.specification = SPEC.read_text(encoding="utf-8")
        cls.inventory = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))

    def test_live_registry_occurrences_and_inventory_pass(self) -> None:
        entries, registry_errors = checker.parse_registry(self.specification)
        occurrences, occurrence_errors = checker.discover_occurrences(
            self.specification, entries
        )
        self.assertEqual([], registry_errors)
        self.assertEqual([], occurrence_errors)
        self.assertEqual(26, len(entries))
        self.assertEqual(58, len(occurrences))
        self.assertEqual([], checker.check_document(self.specification, self.inventory))

    def test_native_fingerprint_is_stable(self) -> None:
        text = "  A\n\n definition\twith spacing  "
        self.assertEqual("A definition with spacing", checker.normalize_block(text))
        self.assertEqual(
            "7b2091576ab58037456d42b1e84170fba8373cb8c9a88461629b84b4a146e12e",
            checker.fingerprint_block(text),
        )

    def test_occurrence_records_use_declarative_policy(self) -> None:
        entries, _ = checker.parse_registry(self.specification)
        occurrences, _ = checker.discover_occurrences(self.specification, entries)
        roles = {checker.occurrence_record(item)["role"] for item in occurrences}
        self.assertEqual(
            {"canonical-definition", "intent", "obligation", "reference"}, roles
        )
        self.assertEqual("2", checker.TERMINOLOGY_POLICY["canonical_location"]["root"])
        self.assertEqual(
            [
                ("0", "intent"),
                ("3", "obligation"),
                ("5", "implication"),
                ("8", "synopsis"),
            ],
            [
                (rule["matcher"]["value"], rule["role"])
                for rule in checker.TERMINOLOGY_POLICY["role_policy"][
                    "noncanonical_rules"
                ]
            ],
        )

    def test_section_extraction_is_maximal_and_fail_closed(self) -> None:
        cases = (
            ("2 Core", "2"),
            ("2.2 Work", "2.2"),
            ("2.2A Work", "2.2A"),
            ("0.10I Work", "0.10I"),
            ("2.2A—Work", "2.2A"),
            ("Heading", ""),
            ("2.2Afoo", ""),
            ("2.2A_foo", ""),
            ("2é", ""),
            ("٢.٢ Heading", ""),
        )
        for heading, expected in cases:
            with self.subTest(heading=heading):
                blocks, _anchors = checker.parse_blocks(f"# {heading}\n\nBody.\n")
                self.assertEqual(expected, blocks[0].section)

    def test_canonical_location_rejects_section_twenty(self) -> None:
        changed = FIXTURE_SPEC.replace("## 2.1 Alpha", "## 20.1 Alpha")
        entries, registry_errors = checker.parse_registry(changed)
        self.assertEqual([], registry_errors)
        _occurrences, errors = checker.discover_occurrences(changed, entries)
        self.assertTrue(any("outside Section 2" in error for error in errors), errors)

    def test_role_mapping_uses_exact_section_hierarchies(self) -> None:
        expected = {
            "0.1": "intent",
            "3.1": "obligation",
            "5.1": "implication",
            "8.1": "synopsis",
            "20": "reference",
            "30": "reference",
            "50": "reference",
            "80": "reference",
        }
        for section, role in expected.items():
            with self.subTest(section=section):
                occurrence = checker.Occurrence(
                    ["alpha"], section, f"{section} Heading", "0" * 64, 1, False
                )
                self.assertEqual(role, checker.occurrence_record(occurrence)["role"])

    def test_duplicate_registry_identity_and_anchor_are_rejected(self) -> None:
        duplicate_key = FIXTURE_SPEC.replace("| `beta` |", "| `alpha` |")
        _entries, errors = checker.parse_registry(duplicate_key)
        self.assertIn("terminology registry contains duplicate concept keys", errors)
        duplicate_anchor = FIXTURE_SPEC.replace(
            "[`term-beta`](#term-beta)", "[`term-alpha`](#term-alpha)"
        )
        _entries, errors = checker.parse_registry(duplicate_anchor)
        self.assertIn(
            "terminology registry contains duplicate canonical destinations", errors
        )

    def test_overloaded_alias_remains_explicit_for_distinct_concepts(self) -> None:
        changed = FIXTURE_SPEC.replace(
            "| `first concept` |", "| `first concept`; `bounded region` |"
        )
        entries, errors = checker.parse_registry(changed)
        self.assertEqual([], errors)
        self.assertEqual(
            2,
            sum("bounded region" in entry.aliases for entry in entries),
        )

    def test_anchor_must_lead_to_its_registered_definition(self) -> None:
        changed = FIXTURE_SPEC.replace(
            "An **alpha** is the first canonical concept.",
            "Alpha appears without a definition.",
        )
        errors = checker.check_document(changed, {**self.inventory, "occurrences": []})
        self.assertTrue(
            any("does not lead to a definition" in error for error in errors), errors
        )

    def test_fixture_conforms_with_native_policy(self) -> None:
        self.assertEqual([], checker.check_document(FIXTURE_SPEC, inventory_for(FIXTURE_SPEC)))

    def test_registry_requires_valid_gfm_structure(self) -> None:
        separator = "| ----------- | -------------- | ---------------- | ---------------- | ------------------ | -------------- |\n"
        _entries, errors = checker.parse_registry(FIXTURE_SPEC.replace(separator, ""))
        self.assertIn("terminology registry structure is invalid", errors)
        aligned = FIXTURE_SPEC.replace(
            separator,
            "| :---------- | -------------: | :--------------: | ---------------: | :---------------- | -------------: |\n",
        )
        _entries, errors = checker.parse_registry(aligned)
        self.assertEqual([], errors)

    def test_unregistered_canonical_anchor_is_rejected(self) -> None:
        changed = FIXTURE_SPEC.replace(
            "# 3. Obligations",
            '<a id="term-gamma"></a>\n\nA **gamma** is new.\n\n# 3. Obligations',
        )
        errors = checker.check_document(changed, inventory_for(FIXTURE_SPEC))
        self.assertIn(
            "canonical terminology anchor is not registered: term-gamma", errors
        )

    def test_definition_cues_and_equations_are_discovered(self) -> None:
        additions = """

# 4. Candidate forms

Alpha means one candidate.

Alpha is defined as another candidate.

```
alpha = candidate equation
```
"""
        changed = FIXTURE_SPEC.replace(
            "# 5. Implications", additions + "\n# 5. Implications"
        )
        entries, errors = checker.parse_registry(changed)
        self.assertEqual([], errors)
        occurrences, errors = checker.discover_occurrences(changed, entries)
        self.assertEqual([], errors)
        candidates = [
            item for item in occurrences if not item.canonical and item.section == "4"
        ]
        self.assertEqual(3, len(candidates))
        self.assertTrue(all(item.concepts == ["alpha"] for item in candidates))

    def test_competing_and_synopsis_definitions_remain_unreviewed(self) -> None:
        review = inventory_for(FIXTURE_SPEC)
        competing = FIXTURE_SPEC.replace(
            "# 5. Implications",
            "# 4. Boundary\n\nAn alpha means independent meaning.\n\n# 5. Implications",
        )
        self.assertIn(
            "unreviewed definition-like occurrence",
            checker.check_document(competing, review),
        )
        synopsis = FIXTURE_SPEC + "\nAlpha is a new synopsis definition.\n"
        self.assertIn(
            "unreviewed definition-like occurrence",
            checker.check_document(synopsis, review),
        )

    def test_malformed_inventory_shape_fails_with_local_diagnostic(self) -> None:
        malformed = inventory_for(FIXTURE_SPEC)
        malformed["occurrences"] = None
        self.assertIn(
            "terminology inventory occurrences must be a list",
            checker.check_document(FIXTURE_SPEC, malformed),
        )
        malformed = inventory_for(FIXTURE_SPEC)
        malformed["occurrences"][0]["role"] = []
        self.assertIn(
            "terminology inventory entry has invalid role",
            checker.check_document(FIXTURE_SPEC, malformed),
        )

    def test_unknown_concept_is_rejected(self) -> None:
        malformed = inventory_for(FIXTURE_SPEC)
        malformed["occurrences"][0]["concepts"] = ["unknown-concept"]
        self.assertIn(
            "terminology inventory entry references unknown concepts",
            checker.check_document(FIXTURE_SPEC, malformed),
        )

    def test_cli_disclaims_semantic_proof(self) -> None:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(CHECKER_PATH), "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("not semantic proof", result.stdout)

    def test_list_occurrences_reports_provider_failure_without_traceback(self) -> None:
        stderr = io.StringIO()
        with mock.patch.object(
            checker,
            "parse_registry",
            side_effect=checker.ProtoRingExecutableError("provider unavailable"),
        ), mock.patch.object(
            sys, "argv", [str(CHECKER_PATH), "--list-occurrences"]
        ), contextlib.redirect_stderr(stderr):
            self.assertEqual(1, checker.main())
        self.assertIn("provider unavailable", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_malformed_registry_produces_typed_diagnostic(self) -> None:
        changed = self.specification.replace(
            "<!-- normative-terminology-registry:end -->", "", 1
        )
        _entries, errors = checker.parse_registry(changed)
        self.assertIn(
            "specification must contain exactly one canonical terminology registry",
            errors,
        )

    def test_stale_inventory_is_non_pass(self) -> None:
        changed = dict(self.inventory)
        changed["occurrences"] = self.inventory["occurrences"][:-1]
        errors = checker.check_document(self.specification, changed)
        self.assertIn("unreviewed definition-like occurrence", errors)

    def test_malformed_fingerprint_is_typed(self) -> None:
        changed = yaml.safe_load(yaml.safe_dump(self.inventory))
        changed["occurrences"][0]["fingerprint"] = "not-a-digest"
        errors = checker.check_document(self.specification, changed)
        self.assertIn(
            "terminology inventory entry has malformed fingerprint", errors
        )

    def test_local_executable_policy_copies_are_absent(self) -> None:
        source = CHECKER_PATH.read_text(encoding="utf-8")
        self.assertNotIn("def _section_from_heading", source)
        self.assertNotIn("def _canonical_location", source)
        self.assertNotIn("def _suggested_role", source)
        for operation in (
            "normative-terminology.fingerprint",
            "normative-terminology.registry",
            "normative-terminology.markdown",
            "normative-terminology.inventory",
        ):
            self.assertIn(operation, source)


if __name__ == "__main__":
    unittest.main()
