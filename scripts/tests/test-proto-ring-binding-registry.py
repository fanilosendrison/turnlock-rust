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
PROVIDER_CHECKER = SCRIPTS / "check-proto-ring-provider.py"
EXPECTED = "dedb01a3a9b7a18930c9da75afa3773b5ad67f69"
OTHER = "b" * 40
THIRD = "c" * 40

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


def load_provider_checker():
    spec = importlib.util.spec_from_file_location(
        "check_proto_ring_provider_for_independence", PROVIDER_CHECKER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load proto-ring provider checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


provider_checker = load_provider_checker()


def make_fixture(temporary: str) -> Path:
    root = Path(temporary) / "repository"
    shutil.copytree(
        ROOT,
        root,
        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.pyc"),
    )
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.name", "Turnlock Binding Test"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "config",
            "user.email",
            "turnlock-binding@example.invalid",
        ],
        check=True,
    )
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "commit", "-q", "-m", "baseline"],
        check=True,
    )
    return root


def replace_once(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    if content.count(old) < 1:
        raise AssertionError(f"fixture text not found: {old}")
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


class ProtoRingBindingRegistryTests(unittest.TestCase):
    def test_live_registry_copy_matches_requirements_authority(self) -> None:
        self.assertEqual(EXPECTED, checker.authoritative_proto_ring_commit(ROOT))
        self.assertEqual(EXPECTED, checker.binding_registry_proto_ring_commit(ROOT))
        self.assertEqual([], checker.check(ROOT))

    def test_registry_copy_stale_fails(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            registry = (
                root
                / "docs/repository-governance/turnlock-rust-governance-bindings.md"
            )
            replace_once(registry, EXPECTED, OTHER)
            self.assertIn("differs", checker.check(root)[0])

    def test_requirements_pin_changed_only_fails(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            replace_once(root / "requirements.txt", EXPECTED, OTHER)
            self.assertIn("differs", checker.check(root)[0])

    def test_additional_conflicting_requirement_declaration_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            requirements = root / "requirements.txt"
            requirements.write_text(
                requirements.read_text(encoding="utf-8")
                + "proto-ring @ git+https://github.com/another/proto-ring.git@main\n",
                encoding="utf-8",
            )
            self.assertIn("one exact", checker.check(root)[0])

    def test_pep_normalized_or_non_vcs_conflicting_declarations_fail_closed(self) -> None:
        conflicting_declarations = (
            "proto_ring @ git+https://github.com/another/proto-ring.git@main",
            "proto-ring[extra] @ git+https://github.com/another/proto-ring.git@main",
            "proto-ring==0.1",
            "proto-ring",
            "proto_ring",
            "proto.ring",
            "proto-ring[extra]",
            "proto--ring",
            "proto__ring",
            "proto-_.ring",
            "proto--ring[extra]",
            "proto-ring???",
        )
        for declaration in conflicting_declarations:
            with self.subTest(declaration=declaration), TemporaryDirectory() as temporary:
                root = make_fixture(temporary)
                requirements = root / "requirements.txt"
                requirements.write_text(
                    requirements.read_text(encoding="utf-8")
                    + declaration
                    + "\n",
                    encoding="utf-8",
                )
                self.assertIn("one exact", checker.check(root)[0])

    def test_continued_conflicting_declaration_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            requirements = root / "requirements.txt"
            requirements.write_text(
                requirements.read_text(encoding="utf-8")
                + "proto_"
                + "\\"
                + "\nring==0.1\n",
                encoding="utf-8",
            )
            self.assertIn("one exact", checker.check(root)[0])

    def test_comments_do_not_create_dependency_declarations(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            requirements = root / "requirements.txt"
            requirements.write_text(
                requirements.read_text(encoding="utf-8")
                + "jsonschema==4.25.1 # proto_ring is discussed here\n"
                + "# proto-ring==0.1\n",
                encoding="utf-8",
            )
            self.assertEqual([], checker.check(root))

    def test_missing_stable_binding_id_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            registry = (
                root
                / "docs/repository-governance/turnlock-rust-governance-bindings.md"
            )
            replace_once(
                registry,
                "    proto_ring_executable:\n",
                "    renamed_proto_ring_executable:\n",
            )
            projection = (
                root
                / "docs/repository-governance/turnlock-rust-projection-integrity.md"
            )
            text = projection.read_text(encoding="utf-8")
            old = "      binding: proto_ring_executable\n"
            new = "      binding: renamed_proto_ring_executable\n"
            if text.count(old) != 2:
                raise AssertionError(
                    "fixture expected exactly two proto_ring_executable "
                    "projection bindings"
                )
            projection.write_text(text.replace(old, new), encoding="utf-8")
            self.assertIn("requires proto_ring_executable", checker.check(root)[0])

    def test_wrong_registry_repository_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            registry = (
                root
                / "docs/repository-governance/turnlock-rust-governance-bindings.md"
            )
            replace_once(
                registry,
                "        repository: fanilosendrison/proto-ring\n",
                "        repository: another/repository\n",
            )
            self.assertIn("repository must be", checker.check(root)[0])

    def test_wrong_binding_kind_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            registry = (
                root
                / "docs/repository-governance/turnlock-rust-governance-bindings.md"
            )
            replace_once(
                registry,
                "      kind: executable_provider\n",
                "      kind: governance_contract\n",
            )
            self.assertNotEqual([], checker.check(root))

    def test_wrong_binding_scope_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            registry = (
                root
                / "docs/repository-governance/turnlock-rust-governance-bindings.md"
            )
            replace_once(
                registry,
                "      scope:\n        kind: logical_provider\n",
                "      scope:\n        kind: capability\n"
                "        capability: shared_governance_provider\n",
            )
            self.assertNotEqual([], checker.check(root))

    def test_malformed_registry_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            registry = (
                root
                / "docs/repository-governance/turnlock-rust-governance-bindings.md"
            )
            registry.write_text(
                "---\ngovernance_bindings: []\n---\n", encoding="utf-8"
            )
            self.assertNotEqual([], checker.check(root))

    def test_checker_consumes_one_canonical_state_registry(self) -> None:
        state = checker.repository_governance_state.load(ROOT)
        expected = state.governance_bindings.bindings[
            "proto_ring_executable"
        ].identity.commit
        with mock.patch.object(
            checker.repository_governance_state, "load", return_value=state
        ) as load:
            actual = checker.binding_registry_proto_ring_commit(ROOT)
        load.assert_called_once_with(ROOT)
        self.assertEqual(expected, actual)

    def test_cross_independence_registry_stale_provider_current(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            registry = (
                root
                / "docs/repository-governance/turnlock-rust-governance-bindings.md"
            )
            replace_once(registry, EXPECTED, OTHER)
            with mock.patch.object(
                provider_checker,
                "installed_proto_ring_commit",
                return_value=EXPECTED,
            ):
                self.assertNotEqual([], checker.check(root))
                self.assertEqual([], provider_checker.check(root))

    def test_cross_independence_provider_stale_registry_current(self) -> None:
        with mock.patch.object(
            provider_checker,
            "installed_proto_ring_commit",
            return_value=OTHER,
        ):
            self.assertEqual([], checker.check(ROOT))
            self.assertNotEqual([], provider_checker.check(ROOT))

    def test_cross_independence_both_stale(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_fixture(temporary)
            registry = (
                root
                / "docs/repository-governance/turnlock-rust-governance-bindings.md"
            )
            replace_once(registry, EXPECTED, OTHER)
            with mock.patch.object(
                provider_checker,
                "installed_proto_ring_commit",
                return_value=THIRD,
            ):
                self.assertNotEqual([], checker.check(root))
                self.assertNotEqual([], provider_checker.check(root))

    def test_registry_checker_has_no_installed_provider_responsibility(self) -> None:
        source = CHECKER.read_text(encoding="utf-8")
        self.assertNotIn("importlib", source)
        self.assertNotIn("metadata.distribution", source)
        self.assertNotIn("direct_url.json", source)

    def test_cli_executes_the_live_routed_check(self) -> None:
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
