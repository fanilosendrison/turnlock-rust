#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CHECKER_PATH = SCRIPTS / "check-repository-integrity.py"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
PROFILE = Path("docs/repository-governance/turnlock-rust-repository-integrity.md")


def load_checker():
    spec = importlib.util.spec_from_file_location("check_repository_integrity", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Repository Integrity checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


def make_fixture(temporary: str, source: str) -> Path:
    root = Path(temporary) / "repository"
    shutil.copytree(
        ROOT,
        root,
        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.pyc"),
    )
    profile_path = root / PROFILE
    text = profile_path.read_text(encoding="utf-8")
    metadata = yaml.safe_load(text.split("---\n", 2)[1])
    integrity = metadata["repository_integrity"]
    integrity["validations"] = {
        "probe": {
            "responsibility": "repository_validation",
            "prerequisites": [],
            "instances": {"kind": "single"},
            "command": {
                "kind": "command",
                "environment": "turnlock_python",
                "arguments": ["-c", source],
                "undetermined_exit_codes": [2],
            },
        }
    }
    integrity["order"] = ["probe"]
    body = text.split("---\n", 2)[2]
    profile_path.write_text(
        "---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---\n" + body,
        encoding="utf-8",
    )
    projection_path = (
        root
        / "docs/repository-governance/turnlock-rust-projection-integrity.md"
    )
    projection_text = projection_path.read_text(encoding="utf-8")
    projection_metadata = yaml.safe_load(projection_text.split("---\n", 2)[1])
    for projection in projection_metadata["projection_registry"]["projections"].values():
        projection["validation"] = "probe"
    projection_body = projection_text.split("---\n", 2)[2]
    projection_path.write_text(
        "---\n"
        + yaml.safe_dump(projection_metadata, sort_keys=False)
        + "---\n"
        + projection_body,
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "RI Test"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.email", "ri@example.invalid"],
        check=True,
    )
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "fixture"], check=True)
    return root


def evaluate(root: Path) -> dict[str, object]:
    payload = {
        "repository": str(root),
        "evaluation_context": {
            "realizations": [
                {
                    "environment_id": "turnlock_python",
                    "identity_utf8": "turnlock-python-validation-environment-v1",
                    "command_prefix": [sys.executable],
                    "process_environment": dict(os.environ),
                }
            ]
        },
    }
    return checker.invoke_compat_result(ROOT, "repository-integrity.evaluate", payload)


class RepositoryIntegrityEvaluatorTests(unittest.TestCase):
    def test_native_pass_is_satisfied(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = evaluate(make_fixture(temporary, "pass"))
        self.assertEqual("PASS", result["verdict"])
        self.assertEqual("SATISFIED", result["validations"][0]["status"])

    def test_preexisting_dirty_state_is_admissible(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = make_fixture(temporary, "pass")
            (root / "preexisting-dirty.txt").write_text("dirty\n", encoding="utf-8")
            result = evaluate(root)
        self.assertEqual("PASS", result["verdict"])
        self.assertEqual("EQUAL", result["state_relation"])

    def test_native_child_failure_is_non_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = evaluate(make_fixture(temporary, "raise SystemExit(7)"))
        self.assertEqual("NON_PASS", result["verdict"])
        self.assertEqual("VIOLATED", result["validations"][0]["status"])
        self.assertEqual("7", result["validations"][0]["obligations"][0]["exit_code"])

    def test_exit_two_maps_to_undetermined(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = evaluate(make_fixture(temporary, "raise SystemExit(2)"))
        self.assertEqual("UNDETERMINED", result["validations"][0]["status"])

    def test_mutation_is_detected(self) -> None:
        source = "from pathlib import Path; Path('README.md').write_text('changed')"
        with tempfile.TemporaryDirectory() as temporary:
            result = evaluate(make_fixture(temporary, source))
        self.assertEqual("NON_PASS", result["verdict"])
        self.assertTrue(result["state_coherence_halt"])


if __name__ == "__main__":
    unittest.main()
