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


def disable_git_bound_validation(fixture_root: Path) -> None:
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
