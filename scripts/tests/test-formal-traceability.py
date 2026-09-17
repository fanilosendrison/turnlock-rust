#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-formal-traceability.py"

spec = importlib.util.spec_from_file_location("formal_traceability", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def make_fixture(temporary: str) -> Path:
    fixture_root = Path(temporary)
    shutil.copytree(ROOT / "docs", fixture_root / "docs")
    shutil.copytree(ROOT / "formal", fixture_root / "formal")
    scripts_dir = fixture_root / "scripts"
    scripts_dir.mkdir()
    shutil.copyfile(
        ROOT / "scripts" / "render-formal-mapping.py",
        scripts_dir / "render-formal-mapping.py",
    )
    return fixture_root


def load_manifest(fixture_root: Path) -> dict:
    return yaml.safe_load((fixture_root / "formal" / "verification.yaml").read_text())


def save_manifest(fixture_root: Path, manifest: dict) -> None:
    (fixture_root / "formal" / "verification.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )


class FormalTraceabilityTests(unittest.TestCase):
    def test_repository_conforms(self) -> None:
        errors, _ = checker.collect_errors(ROOT)
        self.assertEqual([], errors)

    def test_model_appearing_while_status_not_yet_introduced_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            model_path = fixture_root / "formal" / "Turnlock.tla"
            model_path.write_text("---- MODULE Turnlock ----\n====\n", encoding="utf-8")
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "formal model exists while policy status is not-yet-introduced"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_model_status_introduced_without_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["policy"]["formal_model"]["status"] = "introduced"
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "formal model status is introduced but path is missing" in error
                    for error in errors
                ),
                errors,
            )

    def test_integrated_config_appearing_while_planned_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            smoke_path = fixture_root / "formal" / "models" / "integrated" / "smoke.cfg"
            smoke_path.write_text("SPECIFICATION Spec\n", encoding="utf-8")
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "integrated profile integrated-smoke exists while status is planned"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_integrated_profile_introduced_without_config_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["policy"]["integrated_profiles"][0]["status"] = "introduced"
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any(
                    "integrated profile integrated-smoke is introduced but path is missing"
                    in error
                    for error in errors
                ),
                errors,
            )

    def test_unknown_lifecycle_status_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            manifest = load_manifest(fixture_root)
            manifest["policy"]["formal_model"]["status"] = "bogus"
            manifest["policy"]["integrated_profiles"][0]["status"] = "bogus"
            save_manifest(fixture_root, manifest)
            errors, _ = checker.collect_errors(fixture_root, check_generated=False)
            self.assertTrue(
                any("status_vocabulary.formal_model" in error for error in errors),
                errors,
            )
            self.assertTrue(
                any(
                    "integrated profile integrated-smoke has unknown status" in error
                    for error in errors
                ),
                errors,
            )


if __name__ == "__main__":
    unittest.main()
