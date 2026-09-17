#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
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

    def test_missing_generated_mapping_is_rejected_without_recreation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            mapping_path = fixture_root / "docs" / "formal" / "invariant-mapping.md"
            mapping_path.unlink()
            self.assertFalse(mapping_path.exists())

            errors, _ = checker.collect_errors(fixture_root, check_generated=True)
            self.assertTrue(
                any(
                    "generated formal invariant mapping is missing" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(mapping_path.exists())

    def test_stale_generated_mapping_is_rejected_without_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            mapping_path = fixture_root / "docs" / "formal" / "invariant-mapping.md"
            mapping_path.write_text("stale", encoding="utf-8")
            before = mapping_path.read_bytes()

            errors, _ = checker.collect_errors(fixture_root, check_generated=True)
            self.assertTrue(
                any(
                    "generated formal invariant mapping is stale" in error
                    for error in errors
                ),
                errors,
            )
            self.assertEqual(before, mapping_path.read_bytes())

    def test_truncated_generated_mapping_is_rejected_without_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            mapping_path = fixture_root / "docs" / "formal" / "invariant-mapping.md"
            full = mapping_path.read_bytes()
            mapping_path.write_bytes(full[: len(full) // 2])
            before = mapping_path.read_bytes()

            errors, _ = checker.collect_errors(fixture_root, check_generated=True)
            self.assertTrue(
                any(
                    "generated formal invariant mapping is stale" in error
                    for error in errors
                ),
                errors,
            )
            self.assertFalse(
                any(
                    "generated formal invariant mapping is missing" in error
                    for error in errors
                ),
                errors,
            )
            self.assertEqual(before, mapping_path.read_bytes())

    def test_renderer_failure_is_reported_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            renderer = fixture_root / "scripts" / "render-formal-mapping.py"
            renderer.write_text('raise RuntimeError("boom")\n', encoding="utf-8")
            mapping_path = fixture_root / "docs" / "formal" / "invariant-mapping.md"
            before = mapping_path.read_bytes()

            errors, _ = checker.collect_errors(fixture_root, check_generated=True)
            joined = "\n".join(errors)
            self.assertIn("generated formal invariant mapping could not be rendered", joined)
            self.assertIn("RuntimeError: boom", joined)
            self.assertNotIn("Traceback", joined)
            self.assertEqual(before, mapping_path.read_bytes())

    def test_fresh_generated_mapping_passes_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            mapping_path = fixture_root / "docs" / "formal" / "invariant-mapping.md"
            before = mapping_path.read_bytes()

            errors, _ = checker.collect_errors(fixture_root, check_generated=True)
            self.assertFalse(
                any("generated formal invariant mapping" in error for error in errors),
                errors,
            )
            self.assertEqual(before, mapping_path.read_bytes())

    def test_renderer_stdout_matches_committed_mapping_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture_root = make_fixture(temporary)
            mapping_path = fixture_root / "docs" / "formal" / "invariant-mapping.md"
            committed = mapping_path.read_bytes()
            formal_listing_before = sorted(
                path.relative_to(fixture_root).as_posix()
                for path in (fixture_root / "docs" / "formal").rglob("*")
            )

            result = subprocess.run(
                [sys.executable, "scripts/render-formal-mapping.py", "--stdout"],
                cwd=fixture_root,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr.decode("utf-8"))
            self.assertEqual(committed.decode("utf-8"), result.stdout.decode("utf-8"))
            self.assertEqual(committed, mapping_path.read_bytes())
            formal_listing_after = sorted(
                path.relative_to(fixture_root).as_posix()
                for path in (fixture_root / "docs" / "formal").rglob("*")
            )
            self.assertEqual(formal_listing_before, formal_listing_after)


if __name__ == "__main__":
    unittest.main()
