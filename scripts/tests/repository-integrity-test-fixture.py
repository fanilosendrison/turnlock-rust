from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-repository-integrity.py"
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))

spec = importlib.util.spec_from_file_location("repository_integrity", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def initialize_repository(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.name", "Turnlock Integrity Test"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "config", "user.email", "turnlock-ri@example.invalid"],
        check=True,
        capture_output=True,
    )


def commit_all(root: Path) -> None:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(root), "commit", "-q", "-m", "baseline"],
        check=True,
        capture_output=True,
    )


def make_committed_git_fixture(temporary: str) -> Path:
    root = Path(temporary)
    initialize_repository(root)
    (root / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    commit_all(root)
    return root


def make_runner_fixture(
    temporary: str,
    *,
    child_sources: dict[str, str] | None = None,
) -> Path:
    root = Path(temporary) / "repo"
    root.mkdir()
    initialize_repository(root)
    shutil.copyfile(ROOT / "AGENTS.md", root / "AGENTS.md")
    shutil.copyfile(ROOT / "requirements.txt", root / "requirements.txt")
    shutil.copytree(ROOT / "docs", root / "docs")
    workflow = root / ".github" / "workflows" / "repository-integrity.yml"
    workflow.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / ".github/workflows/repository-integrity.yml", workflow)
    scripts = root / "scripts"
    scripts.mkdir()
    shutil.copyfile(SCRIPT, scripts / SCRIPT.name)
    for module_name in (
        "proto_ring_executable_binding.py",
        "proto_ring_result_validation.py",
        "proto_ring_structured_value.py",
    ):
        shutil.copyfile(ROOT / "scripts" / module_name, scripts / module_name)

    child_sources = child_sources or {}
    profile_path = (
        ROOT
        / "docs/repository-governance/turnlock-rust-repository-integrity.md"
    )
    metadata = yaml.safe_load(
        profile_path.read_text(encoding="utf-8").split("---\n", 2)[1]
    )["repository_integrity"]
    child_paths = {
        definition["command"]["arguments"][0]
        for definition in metadata["validations"].values()
        if definition["command"]["arguments"]
        and definition["command"]["arguments"][0].startswith("scripts/")
        and definition["command"]["arguments"][0].endswith(".py")
    }
    for relative in child_paths:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(child_sources.get(relative, "pass\n"), encoding="utf-8")
    commit_all(root)
    return root
