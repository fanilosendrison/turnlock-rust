#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

fixture = importlib.import_module("adr-metadata-test-fixture")
ROOT = fixture.ROOT
adr_metadata = fixture.adr_metadata


def load_accepted_body_checker():
    path = ROOT / "scripts/check-accepted-adr-body.py"
    spec = importlib.util.spec_from_file_location("check_accepted_adr_body", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load accepted ADR body checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


accepted_body = load_accepted_body_checker()


def commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "commit", "-q", "-m", message], check=True
    )


def accepted_body_fixture(temporary: str) -> tuple[Path, Path]:
    root = Path(temporary)
    adr_directory = root / "docs/adr"
    governance = root / "docs/repository-governance"
    adr_directory.mkdir(parents=True)
    governance.mkdir(parents=True)
    shutil.copyfile(
        ROOT / "docs/repository-governance/turnlock-rust-governance-bindings.md",
        governance / "turnlock-rust-governance-bindings.md",
    )
    (governance / "provider-binding.md").write_text("# Provider binding\n", encoding="utf-8")
    (root / "AGENTS.md").write_text(
        "---\n"
        "repository_governance:\n"
        "  model_version: 1\n"
        "  provider:\n"
        "    id: proto-ring\n"
        "    binding:\n"
        "      capability: shared_governance_provider\n"
        "      route: binding\n"
        "  capabilities:\n"
        "    architecture_decisions:\n"
        "      configuration: {}\n"
        "      routes:\n"
        "        profile: docs/adr/adr-profile.yaml\n"
        "    shared_governance_provider:\n"
        "      configuration: {}\n"
        "      routes:\n"
        "        binding: docs/repository-governance/provider-binding.md\n"
        "---\n",
        encoding="utf-8",
    )
    (adr_directory / "adr-profile.yaml").write_text(
        "repository:\n"
        "  adr_directory: docs/adr\n"
        "  filename_pattern: '^adr-(?P<number>[0-9]{3})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\\.md$'\n"
        "  id_pattern: '^ADR-[0-9]{3}$'\n"
        "  id_width: 3\n",
        encoding="utf-8",
    )
    adr = adr_directory / "adr-001-example.md"
    adr.write_text(
        "---\nid: ADR-001\nstatus: accepted\n---\n"
        "# ADR-001: Example\n\n## Context\n\nExact body.\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "ADR Test"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.email", "adr@example.invalid"],
        check=True,
    )
    commit_all(root, "accept ADR")
    return root, adr


class AdrMetadataProviderBindingTests(unittest.TestCase):
    def test_repository_passes_full_native_profile(self) -> None:
        self.assertEqual([], adr_metadata.collect_errors(ROOT))

    def test_profile_path_is_resolved_by_native_canonical_operation(self) -> None:
        self.assertEqual(
            (ROOT / "docs/adr/adr-profile.yaml").resolve(),
            adr_metadata.configured_profile_path(ROOT),
        )

    def test_native_parse_preserves_decision_body(self) -> None:
        path = ROOT / "docs/adr/adr-051-require-proto-ring-for-applicable-generic-repository-governance.md"
        metadata, body = adr_metadata.parse_adr(path)
        self.assertEqual("ADR-051", metadata["id"])
        self.assertEqual(metadata["decision_body_sha256"], adr_metadata.sha256_hex(body))

    def test_native_repository_path_rejects_escape(self) -> None:
        with self.assertRaises(adr_metadata.AdrMetadataError):
            adr_metadata.repository_path(ROOT, "../outside")

    def test_native_accepted_body_detects_changed_body(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, adr = accepted_body_fixture(temporary)
            adr.write_text(
                adr.read_text(encoding="utf-8").replace("Exact body.", "Changed body."),
                encoding="utf-8",
            )
            commit_all(root, "change accepted body")
            self.assertEqual((False, "body_changed"), accepted_body.check(root))

    def test_native_accepted_body_detects_invalid_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, adr = accepted_body_fixture(temporary)
            adr.write_text(
                adr.read_text(encoding="utf-8").replace("id: ADR-001", "id: ADR-002"),
                encoding="utf-8",
            )
            commit_all(root, "invalidate accepted identity")
            self.assertEqual(
                (False, "historical_state_invalid"), accepted_body.check(root)
            )

    def test_shared_algorithms_are_not_reimplemented_locally(self) -> None:
        source = (ROOT / "scripts/adr-metadata.py").read_text(encoding="utf-8")
        for operation in (
            "adr-metadata.parse",
            "adr-metadata.repository-path",
            "adr-metadata.validation",
            "canonical-adr.resolve",
        ):
            self.assertIn(operation, source)
        imports = [
            node.module
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.ImportFrom)
            and node.module is not None
            and (node.module == "proto_ring" or node.module.startswith("proto_ring."))
        ]
        imports.extend(
            alias.name
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Import)
            for alias in node.names
            if alias.name == "proto_ring" or alias.name.startswith("proto_ring.")
        )
        self.assertEqual([], imports)

    def test_python_provider_is_not_a_requirement(self) -> None:
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertNotIn("proto-ring", requirements)
        self.assertNotIn("proto_ring", requirements)


if __name__ == "__main__":
    unittest.main()
