from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "adr-metadata.py"

spec = importlib.util.spec_from_file_location("adr_metadata", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")
adr_metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adr_metadata)


def write_repository_governance(fixture_root: Path) -> None:
    (fixture_root / "AGENTS.md").write_text(
        "---\n"
        "repository_governance:\n"
        "  model_version: 1\n"
        "  provider:\n"
        '    id: "proto-ring"\n'
        "    binding:\n"
        '      capability: "shared_governance_provider"\n'
        '      route: "binding"\n'
        "  capabilities:\n"
        "    architecture_decisions:\n"
        "      configuration: {}\n"
        "      routes:\n"
        '        profile: "docs/adr/adr-profile.yaml"\n'
        "    shared_governance_provider:\n"
        "      configuration:\n"
        "        required: true\n"
        "      routes:\n"
        '        binding: "docs/repository-governance/test-shared-governance-provider.md"\n'
        "---\n"
        "# Test repository directives\n",
        encoding="utf-8",
    )
    binding = (
        fixture_root
        / "docs"
        / "repository-governance"
        / "test-shared-governance-provider.md"
    )
    binding.parent.mkdir(parents=True, exist_ok=True)
    binding.write_text(
        "# Test Shared Governance Provider binding target\n", encoding="utf-8"
    )


def disable_git_bound_validation(fixture_root: Path) -> None:
    write_repository_governance(fixture_root)
    profile_path = fixture_root / "docs" / "adr" / "adr-profile.yaml"
    profile = adr_metadata.load_yaml(profile_path)
    profile["migration_evidence"] = {
        "path": "docs/adr/metadata-migration-evidence.yaml",
        "required": False,
        "baseline_commit": None,
        "ids": [],
    }
    profile["generated_index"]["required"] = False
    profile_path.write_text(
        yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
    )


def make_adr_fixture(temporary: str) -> Path:
    fixture_root = Path(temporary)
    shutil.copytree(ROOT / "docs" / "adr", fixture_root / "docs" / "adr")
    disable_git_bound_validation(fixture_root)
    return fixture_root


def history_text(fixture_root: Path) -> str:
    return (fixture_root / "docs" / "adr" / "README.md").read_text(
        encoding="utf-8"
    )


def write_history(fixture_root: Path, text: str) -> None:
    (fixture_root / "docs" / "adr" / "README.md").write_text(
        text, encoding="utf-8"
    )
