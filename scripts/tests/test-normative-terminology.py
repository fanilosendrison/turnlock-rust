#!/usr/bin/env python3
"""Regression tests for canonical terminology governance."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "scripts" / "check-normative-terminology.py"
MODULE_NAME = "check_normative_terminology"
SPEC = """# Example specification

# 0. Product intent

Alpha supports the product promise. Alpha MUST remain visible.

# 2. Core mental model

Section 2 is the canonical terminology registry.

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

Alpha MUST satisfy its declared obligation.

# 5. Implications

Alpha requires an architectural boundary.

# 8. Synopsis

Alpha refers to the canonical Section 2 concept.
"""


def load_checker():
    spec = importlib.util.spec_from_file_location(MODULE_NAME, CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load terminology checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()

GOLDEN_INVENTORY = {
    "schema_version": 1,
    "authority": "non-authoritative-review-inventory",
    "source": "docs/specification/turnlock-spec.md",
    "fingerprint": {"algorithm": "sha256", "normalization": "collapse-whitespace"},
    "occurrences": [
        {
            "concepts": ["alpha"],
            "section": "2.1",
            "heading": "2.1 Alpha",
            "role": "canonical-definition",
            "fingerprint": "dd512041ce4865f1c234a7dfb3c29514888f360452003fe44238e8b5d49b6d28",
        },
        {
            "concepts": ["beta"],
            "section": "2.1",
            "heading": "2.1 Alpha",
            "role": "canonical-definition",
            "fingerprint": "fd9289cbf61c3e981e55efc0351db6191ea60d3dc9942e8fd704c410484f2644",
        },
        {
            "concepts": ["alpha"],
            "section": "8",
            "heading": "8. Synopsis",
            "role": "synopsis",
            "fingerprint": "ff42a5b92f9f445514632db3ce8d642de22eafe4a9475ca861539de53701385f",
        },
    ],
}


def inventory_for(specification: str) -> dict:
    entries, registry_errors = checker.parse_registry(specification)
    if registry_errors:
        raise AssertionError(registry_errors)
    occurrences, occurrence_errors = checker.discover_occurrences(specification, entries)
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


def spec_with_unregistered_canonical_anchor() -> str:
    return SPEC.replace(
        "# 3. Obligations",
        '<a id="term-gamma"></a>\n\n'
        "A **gamma** is an unregistered canonical concept.\n\n"
        "# 3. Obligations",
        1,
    )


class NormativeTerminologyTests(unittest.TestCase):
    def test_repository_conforms(self) -> None:
        self.assertEqual([], checker.check_paths())

    def test_fixture_conforms_with_intent_obligation_and_implication_uses(self) -> None:
        self.assertEqual([], checker.check_document(SPEC, GOLDEN_INVENTORY))

    def test_registry_requires_a_valid_gfm_separator(self) -> None:
        separator = "| ----------- | -------------- | ---------------- | ---------------- | ------------------ | -------------- |\n"
        _, errors = checker.parse_registry(SPEC.replace(separator, ""))
        self.assertTrue(any("separator" in error for error in errors))
        _, errors = checker.parse_registry(SPEC.replace("-----------", "--", 1))
        self.assertTrue(any("separator" in error for error in errors))
        aligned = SPEC.replace(separator, "| :---------- | -------------: | :--------------: | ---------------: | :---------------- | -------------: |\n")
        _, errors = checker.parse_registry(aligned)
        self.assertEqual([], errors)

    def test_canonical_anchor_must_bind_to_its_own_definition(self) -> None:
        unrelated = SPEC.replace("An **alpha** is the first canonical concept.", "Alpha appears without a definition.")
        errors = checker.check_document(unrelated, GOLDEN_INVENTORY)
        self.assertTrue(any("does not lead to a definition of alpha" in error for error in errors))

        consecutive = SPEC.replace(
            '<a id="term-alpha"></a>\n\nAn **alpha** is the first canonical concept.\n\n<a id="term-beta"></a>',
            '<a id="term-alpha"></a>\n\n<a id="term-beta"></a>\n\nAn **alpha** is the first canonical concept.',
        )
        errors = checker.check_document(consecutive, GOLDEN_INVENTORY)
        self.assertTrue(any("not immediately followed" in error for error in errors))

        anchor = '<a id="term-alpha"></a>'
        duplicated = SPEC.replace(anchor, f"{anchor}\n\n{anchor}", 1)
        errors = checker.check_document(duplicated, GOLDEN_INVENTORY)
        self.assertTrue(any("occurs more than once" in error for error in errors))

    def test_unregistered_canonical_anchor_is_rejected(self) -> None:
        errors = checker.check_document(
            spec_with_unregistered_canonical_anchor(),
            GOLDEN_INVENTORY,
        )
        self.assertIn(
            "canonical terminology anchor is not registered: term-gamma",
            errors,
        )

    def test_list_occurrences_rejects_unregistered_canonical_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            spec_path = Path(directory) / "spec.md"
            spec_path.write_text(
                spec_with_unregistered_canonical_anchor(),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECKER_PATH),
                    "--spec",
                    str(spec_path),
                    "--list-occurrences",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        combined = result.stdout + result.stderr
        self.assertEqual(1, result.returncode)
        self.assertNotIn("Traceback", combined)
        self.assertIn(
            "canonical terminology anchor is not registered: term-gamma",
            result.stderr,
        )

    def test_malformed_occurrence_collection_fails_without_traceback(self) -> None:
        malformed = {**GOLDEN_INVENTORY, "occurrences": None}
        errors = checker.check_document(SPEC, malformed)
        self.assertIn("terminology inventory occurrences must be a list", errors)

        with tempfile.TemporaryDirectory() as directory:
            spec_path = Path(directory) / "spec.md"
            inventory_path = Path(directory) / "inventory.yaml"
            spec_path.write_text(SPEC, encoding="utf-8")
            inventory_path.write_text(yaml.safe_dump(malformed), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CHECKER_PATH), "--spec", str(spec_path), "--inventory", str(inventory_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertNotIn("Traceback", result.stderr + result.stdout)
        self.assertIn("occurrences must be a list", result.stdout)

        malformed_role = inventory_for(SPEC)
        malformed_role["occurrences"][0]["role"] = []
        errors = checker.check_document(SPEC, malformed_role)
        self.assertTrue(any("has invalid role" in error for error in errors))

    def test_new_competing_definition_is_rejected(self) -> None:
        inventory = inventory_for(SPEC)
        changed = SPEC.replace(
            "# 5. Implications",
            "# 4. Boundary\n\nAn alpha means an independently assigned meaning.\n\n# 5. Implications",
        )
        errors = checker.check_document(changed, inventory)
        self.assertTrue(any("unreviewed definition-like occurrence for alpha" in error for error in errors))

    def test_definition_cues_and_equations_are_detected(self) -> None:
        additions = """

# 4. Candidate forms

Alpha means one candidate.

Alpha is defined as another candidate.

```
alpha = candidate equation
```
"""
        changed = SPEC.replace("# 5. Implications", additions + "\n# 5. Implications")
        entries, errors = checker.parse_registry(changed)
        self.assertEqual([], errors)
        occurrences, errors = checker.discover_occurrences(changed, entries)
        self.assertEqual([], errors)
        candidates = [item for item in occurrences if not item.canonical and item.section == "4"]
        self.assertEqual(3, len(candidates))
        self.assertTrue(all(item.concepts == ("alpha",) for item in candidates))

    def test_missing_or_stale_inventory_entry_is_rejected(self) -> None:
        inventory = inventory_for(SPEC)
        inventory["occurrences"] = inventory["occurrences"][:-1]
        errors = checker.check_document(SPEC, inventory)
        self.assertTrue(any("unreviewed definition-like occurrence" in error for error in errors))

        stale_inventory = inventory_for(SPEC)
        stale_inventory["occurrences"][0]["fingerprint"] = "0" * 64
        errors = checker.check_document(SPEC, stale_inventory)
        self.assertTrue(any("stale terminology inventory entry" in error for error in errors))

    def test_unknown_concept_is_rejected(self) -> None:
        inventory = inventory_for(SPEC)
        inventory["occurrences"][0]["concepts"] = ["unknown-concept"]
        errors = checker.check_document(SPEC, inventory)
        self.assertTrue(any("references unknown concepts" in error for error in errors))

    def test_duplicate_concept_key_and_destination_are_rejected(self) -> None:
        duplicate_key = SPEC.replace("| `beta` |", "| `alpha` |")
        _, errors = checker.parse_registry(duplicate_key)
        self.assertIn("terminology registry contains duplicate concept keys", errors)

        duplicate_anchor = SPEC.replace("[`term-beta`](#term-beta)", "[`term-alpha`](#term-alpha)")
        _, errors = checker.parse_registry(duplicate_anchor)
        self.assertIn("terminology registry contains duplicate canonical destinations", errors)

    def test_overloaded_alias_can_identify_distinct_compound_concepts(self) -> None:
        overloaded = SPEC.replace("| `first concept` |", "| `first concept`; `bounded region` |")
        entries, errors = checker.parse_registry(overloaded)
        self.assertEqual([], errors)
        self.assertEqual(2, sum("bounded region" in entry.expressions for entry in entries))

    def test_section_eight_cannot_add_an_unreviewed_definition(self) -> None:
        inventory = inventory_for(SPEC)
        changed = SPEC + "\nAlpha is a new independent synopsis definition.\n"
        errors = checker.check_document(changed, inventory)
        self.assertTrue(any("Section 8" in error and "unreviewed" in error for error in errors))

    def test_cli_disclaims_semantic_proof(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER_PATH), "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("not semantic proof", result.stdout)


if __name__ == "__main__":
    unittest.main()
