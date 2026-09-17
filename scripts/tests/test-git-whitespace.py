#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-git-whitespace.py"

spec = importlib.util.spec_from_file_location("git_whitespace", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

ZERO_SHA = "0" * 40


def make_fixture(temporary: str) -> Path:
    fixture = Path(temporary) / "repo"
    fixture.mkdir()
    subprocess.run(["git", "init", "-q", str(fixture)], check=True)
    subprocess.run(
        ["git", "-C", str(fixture), "config", "user.name", "TURNLOCK Test"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(fixture), "config", "user.email", "turnlock@example.invalid"],
        check=True,
        capture_output=True,
    )
    return fixture


def commit_all(fixture: Path, message: str) -> str:
    subprocess.run(
        ["git", "-C", str(fixture), "add", "-A"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(fixture), "commit", "-q", "-m", message],
        check=True,
        capture_output=True,
    )
    result = subprocess.run(
        ["git", "-C", str(fixture), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def write_event(fixture: Path, name: str, payload: dict) -> Path:
    event_path = fixture.parent / name
    event_path.write_text(json.dumps(payload), encoding="utf-8")
    return event_path


class GitWhitespaceCheckerTests(unittest.TestCase):
    def test_clean_repository_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)
            (fixture / "clean.txt").write_text("clean\n", encoding="utf-8")
            commit_all(fixture, "clean")
            self.assertEqual([], checker.collect_errors(fixture, env={}))

    def test_unstaged_whitespace_violation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)
            (fixture / "clean.txt").write_text(
                "first\nsecond\nthird\n", encoding="utf-8"
            )
            commit_all(fixture, "clean")
            (fixture / "clean.txt").write_text(
                "first\nsecond   \nthird\n", encoding="utf-8"
            )

            errors = checker.collect_errors(fixture, env={})
            joined = "\n".join(errors)
            self.assertIn("unstaged", joined)
            self.assertIn("clean.txt:2", joined)

    def test_staged_whitespace_violation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)
            (fixture / "clean.txt").write_text("clean\n", encoding="utf-8")
            commit_all(fixture, "clean")
            (fixture / "clean.txt").write_text("clean   \n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(fixture), "add", "clean.txt"],
                check=True,
                capture_output=True,
            )

            errors = checker.collect_errors(fixture, env={})
            joined = "\n".join(errors)
            self.assertIn("staged", joined)

    def test_github_push_range_detects_committed_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)
            (fixture / "clean.txt").write_text("clean\n", encoding="utf-8")
            before = commit_all(fixture, "clean")
            (fixture / "bad.txt").write_text("bad   \n", encoding="utf-8")
            after = commit_all(fixture, "bad")

            event_path = write_event(
                fixture, "push-event.json", {"before": before, "after": after}
            )
            errors = checker.collect_errors(
                fixture,
                env={
                    "GITHUB_EVENT_NAME": "push",
                    "GITHUB_EVENT_PATH": str(event_path),
                },
            )
            joined = "\n".join(errors)
            self.assertIn("GitHub push committed-range whitespace check", joined)
            self.assertIn("bad.txt", joined)

    def test_github_pull_request_range_detects_committed_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)
            (fixture / "clean.txt").write_text("clean\n", encoding="utf-8")
            base = commit_all(fixture, "base")
            (fixture / "bad.txt").write_text("bad   \n", encoding="utf-8")
            head = commit_all(fixture, "head")

            event_path = write_event(
                fixture,
                "pr-event.json",
                {"pull_request": {"base": {"sha": base}, "head": {"sha": head}}},
            )
            errors = checker.collect_errors(
                fixture,
                env={
                    "GITHUB_EVENT_NAME": "pull_request",
                    "GITHUB_EVENT_PATH": str(event_path),
                },
            )
            joined = "\n".join(errors)
            self.assertIn(
                "GitHub pull-request committed-range whitespace check", joined
            )
            self.assertIn("bad.txt", joined)

    def test_github_push_root_range_detects_committed_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)
            (fixture / "root.txt").write_text("root   \n", encoding="utf-8")
            after = commit_all(fixture, "root with whitespace")

            event_path = write_event(
                fixture, "push-root-event.json", {"before": ZERO_SHA, "after": after}
            )
            errors = checker.collect_errors(
                fixture,
                env={
                    "GITHUB_EVENT_NAME": "push",
                    "GITHUB_EVENT_PATH": str(event_path),
                },
            )
            joined = "\n".join(errors)
            self.assertIn("GitHub push committed-range whitespace check", joined)
            self.assertIn("root.txt", joined)

    def test_github_push_with_missing_event_data_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)
            (fixture / "clean.txt").write_text("clean\n", encoding="utf-8")
            commit_all(fixture, "clean")

            event_path = write_event(fixture, "bad-event.json", {"after": "abc"})
            errors = checker.collect_errors(
                fixture,
                env={
                    "GITHUB_EVENT_NAME": "push",
                    "GITHUB_EVENT_PATH": str(event_path),
                },
            )
            self.assertTrue(errors)
            self.assertIn("before", "\n".join(errors))

    def test_clean_github_push_range_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)
            (fixture / "first.txt").write_text("first\n", encoding="utf-8")
            before = commit_all(fixture, "first")
            (fixture / "second.txt").write_text("second\n", encoding="utf-8")
            after = commit_all(fixture, "second")

            event_path = write_event(
                fixture, "clean-push-event.json", {"before": before, "after": after}
            )
            self.assertEqual(
                [],
                checker.collect_errors(
                    fixture,
                    env={
                        "GITHUB_EVENT_NAME": "push",
                        "GITHUB_EVENT_PATH": str(event_path),
                    },
                ),
            )

    def test_cli_returns_nonzero_on_local_whitespace_violation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)
            scripts_dir = fixture / "scripts"
            scripts_dir.mkdir()
            shutil.copyfile(SCRIPT, scripts_dir / "check-git-whitespace.py")
            (fixture / "clean.txt").write_text("clean\n", encoding="utf-8")
            commit_all(fixture, "clean")
            (fixture / "clean.txt").write_text("clean   \n", encoding="utf-8")

            env = dict(os.environ)
            env.pop("GITHUB_EVENT_NAME", None)
            env.pop("GITHUB_EVENT_PATH", None)
            result = subprocess.run(
                [sys.executable, "scripts/check-git-whitespace.py"],
                cwd=fixture,
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
            self.assertEqual(1, result.returncode)
            self.assertIn("git whitespace check: FAILED", result.stdout)


if __name__ == "__main__":
    unittest.main()
