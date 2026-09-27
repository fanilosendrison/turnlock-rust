from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-repository-integrity.py"

spec = importlib.util.spec_from_file_location(
    "repository_integrity",
    SCRIPT,
)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def make_committed_git_fixture(temporary: str) -> Path:
    fixture = Path(temporary)
    subprocess.run(
        ["git", "init", "-q", str(fixture)],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(fixture),
            "config",
            "user.name",
            "Turnlock Repository Integrity Test",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(fixture),
            "config",
            "user.email",
            "turnlock-ri@example.invalid",
        ],
        check=True,
        capture_output=True,
    )
    (fixture / "tracked.txt").write_text(
        "baseline\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "-C", str(fixture), "add", "tracked.txt"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(fixture),
            "commit",
            "-q",
            "-m",
            "baseline",
        ],
        check=True,
        capture_output=True,
    )
    return fixture


def python_command(source: str) -> list[str]:
    return [sys.executable, "-c", source]


def make_runner_fixture(
    temporary: str,
    *,
    support_paths: Sequence[str],
    child_sources: dict[str, str] | None = None,
) -> Path:
    fixture = Path(temporary) / "repo"
    fixture.mkdir()
    subprocess.run(
        ["git", "init", "-q", str(fixture)],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(fixture),
            "config",
            "user.name",
            "Turnlock Runner Test",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(fixture),
            "config",
            "user.email",
            "turnlock-runner@example.invalid",
        ],
        check=True,
        capture_output=True,
    )

    runner_dir = fixture / "scripts"
    runner_dir.mkdir()
    shutil.copyfile(
        SCRIPT,
        runner_dir / "check-repository-integrity.py",
    )
    for relative in support_paths:
        target = fixture / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)

    child_sources = child_sources or {}
    child_paths = {
        argv[1]
        for _name, argv in checker.canonical_steps()
        if len(argv) > 1
        and argv[0] == sys.executable
        and argv[1].endswith(".py")
    }
    for relative in child_paths:
        path = fixture / relative
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        path.write_text(
            child_sources.get(relative, "pass\n"),
            encoding="utf-8",
        )
    subprocess.run(
        ["git", "-C", str(fixture), "add", "-A"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(fixture),
            "commit",
            "-q",
            "-m",
            "runner baseline",
        ],
        check=True,
        capture_output=True,
    )
    return fixture
