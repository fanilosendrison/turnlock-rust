#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CHECKER = SCRIPTS / "check-governed-objects.py"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
PROFILE_PATH = ROOT / "docs/repository-governance/turnlock-rust-governed-objects.md"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_governed_objects", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load governed objects checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def profile() -> dict:
    text = PROFILE_PATH.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n", 2)[1])["governed_objects"]


checker = load_checker()


class GovernedObjectsProfileTests(unittest.TestCase):
    def test_native_composition_requires_profile_presence(self) -> None:
        self.assertEqual([], checker.check(ROOT))

    def test_profile_has_exact_consumer_interfaces(self) -> None:
        interfaces = profile()["interfaces"]
        self.assertEqual(
            {"architecture_decisions", "stable_invariants"},
            set(interfaces),
        )
        self.assertEqual(
            {f"ADR-{number:03d}" for number in range(1, 60)},
            set(interfaces["architecture_decisions"]["objects"]),
        )
        self.assertEqual(
            {f"TL-INV-{number:03d}" for number in range(1, 43)},
            set(interfaces["stable_invariants"]["objects"]),
        )

    def test_profile_relations_use_turnlock_responsibilities(self) -> None:
        interfaces = profile()["interfaces"]
        for value in interfaces["architecture_decisions"]["objects"].values():
            self.assertEqual(
                ["adr_metadata", "product_semantics", "accepted_decisions"],
                value["responsibilities"],
            )
            self.assertEqual([], value.get("relations", []))
        for value in interfaces["stable_invariants"]["objects"].values():
            self.assertEqual(
                ["product_semantics", "stable_invariant_definitions"],
                value["responsibilities"],
            )
            self.assertEqual([], value.get("relations", []))

    def test_profile_has_no_duplicate_contract_pin(self) -> None:
        self.assertNotIn(
            "governed_objects_contract:", PROFILE_PATH.read_text(encoding="utf-8")
        )


if __name__ == "__main__":
    unittest.main()
