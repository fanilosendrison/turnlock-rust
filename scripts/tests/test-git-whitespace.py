#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
SCRIPT = SCRIPTS / "check-git-whitespace.py"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_checker():
    spec = importlib.util.spec_from_file_location("check_git_whitespace", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Git whitespace checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


def fixture_environment() -> dict[str, str]:
    environment = dict(os.environ)
    environment.pop("GITHUB_EVENT_NAME", None)
    environment.pop("GITHUB_EVENT_PATH", None)
    return environment


def make_fixture(temporary: str) -> Path:
    fixture = Path(temporary) / "repo"
    fixture.mkdir()
    subprocess.run(["git", "init", "-q", str(fixture)], check=True)
    subprocess.run(["git", "-C", str(fixture), "config", "user.name", "Test"], check=True)
    subprocess.run(
        ["git", "-C", str(fixture), "config", "user.email", "test@example.invalid"],
        check=True,
    )
    (fixture / "tracked.txt").write_text("clean\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(fixture), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(fixture), "commit", "-q", "-m", "clean"], check=True)
    return fixture


class GitWhitespaceBindingTests(unittest.TestCase):
    def test_clean_repository_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)
            self.assertEqual([], checker.check(fixture, fixture_environment()))

    def test_non_pass_preserves_local_git_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = make_fixture(temporary)
            (fixture / "tracked.txt").write_text("trailing   \n", encoding="utf-8")
            errors = checker.check(fixture, fixture_environment())
        self.assertTrue(any("tracked.txt:1" in error for error in errors), errors)

    def test_fixture_environment_excludes_ambient_github_event(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"GITHUB_EVENT_NAME": "push", "GITHUB_EVENT_PATH": "/ambient/event"},
        ):
            environment = fixture_environment()
        self.assertNotIn("GITHUB_EVENT_NAME", environment)
        self.assertNotIn("GITHUB_EVENT_PATH", environment)

    def test_exact_environment_is_forwarded(self) -> None:
        environment = {"ONLY": "this"}
        captured = {}

        def invoke(_root, _operation, payload):
            captured.update(payload)
            return {"status": "PASS", "domains": []}

        original = checker.invoke_compat_result
        checker.invoke_compat_result = invoke
        try:
            self.assertEqual([], checker.check(ROOT, environment))
        finally:
            checker.invoke_compat_result = original
        self.assertEqual(environment, captured["environment"])


if __name__ == "__main__":
    unittest.main()
