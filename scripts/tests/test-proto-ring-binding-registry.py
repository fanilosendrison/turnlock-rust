#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CHECKER = SCRIPTS / "check-proto-ring-binding-registry.py"
EXPECTED = "814a884ccb759b0fdbde48673a74428d6443b847"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_proto_ring_binding_registry", CHECKER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load proto-ring binding registry checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


def make_fixture(temporary: str) -> Path:
    root = Path(temporary) / "repository"
    shutil.copytree(
        ROOT,
        root,
        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.pyc"),
    )
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return root


def registry(root: Path) -> Path:
    return root / "docs/repository-governance/turnlock-rust-governance-bindings.md"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"fixture text not found: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


class ProtoRingBindingRegistryTests(unittest.TestCase):
    def test_live_raw_and_composed_binding_match(self) -> None:
        binding = checker.load_executable_provider_binding(ROOT)
        self.assertEqual(EXPECTED, binding.commit)
        self.assertEqual([], checker.check(ROOT))

    def test_wrong_repository_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            replace_once(
                registry(root),
                "        repository: fanilosendrison/proto-ring\n",
                "        repository: another/repository\n",
            )
            self.assertIn("repository must be", checker.check(root)[0])

    def test_wrong_kind_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            replace_once(
                registry(root),
                "      kind: executable_provider\n",
                "      kind: governance_contract\n",
            )
            self.assertTrue(checker.check(root))

    def test_wrong_scope_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            replace_once(
                registry(root),
                "        kind: logical_provider\n",
                "        kind: capability\n        capability: repository_integrity\n",
            )
            self.assertTrue(checker.check(root))

    def test_malformed_commit_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            replace_once(registry(root), EXPECTED, "not-a-commit")
            self.assertTrue(checker.check(root))

    def test_missing_binding_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            replace_once(
                registry(root),
                "    proto_ring_executable:\n",
                "    renamed_proto_ring_executable:\n",
            )
            self.assertTrue(checker.check(root))

    def test_native_projection_mismatch_is_rejected(self) -> None:
        with mock.patch.object(
            checker,
            "invoke_compat_result",
            return_value={"bindings": {"proto_ring_executable": {"present": False}}},
        ):
            self.assertIn("differs", checker.check(ROOT)[0])

    def test_requirements_is_not_provider_authority(self) -> None:
        source = CHECKER.read_text(encoding="utf-8")
        self.assertNotIn("requirements.txt", source)
        self.assertNotIn("authoritative_proto_ring_commit", source)

    def test_cli_executes_live_native_check(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECKER)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("proto-ring binding registry: OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
