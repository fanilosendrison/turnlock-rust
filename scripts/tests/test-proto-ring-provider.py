#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CHECKER = SCRIPTS / "check-proto-ring-provider.py"
EXPECTED = "814a884ccb759b0fdbde48673a74428d6443b847"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import proto_ring_executable_binding as boundary


def load_checker():
    spec = importlib.util.spec_from_file_location("check_proto_ring_provider", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load proto-ring provider checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


def fake_executable(directory: str, response: object, exit_code: int = 0) -> Path:
    path = Path(directory) / "fake-proto-ring"
    payload = json.dumps(response) + "\n"
    script = (
        "#!/usr/bin/env python3\n"
        "import json,sys\n"
        "json.load(sys.stdin)\n"
        f"sys.stdout.write({payload!r})\n"
        f"raise SystemExit({exit_code})\n"
    )
    path.write_text(script, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


class ProtoRingProviderTests(unittest.TestCase):
    def test_live_native_provider_matches_authority(self) -> None:
        binding = boundary.load_executable_provider_binding(ROOT)
        self.assertEqual(EXPECTED, binding.commit)
        self.assertEqual([], checker.check(ROOT))

    def test_absent_realization_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(
            os.environ, {"XDG_CACHE_HOME": temporary}
        ):
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary.realized_provider(ROOT)

    def test_untracked_or_ignored_source_input_is_rejected(self) -> None:
        binding = boundary.ExecutableProviderBinding(
            repository="fanilosendrison/proto-ring", commit=EXPECTED
        )

        def git_output(_source, *arguments):
            if arguments == ("rev-parse", "HEAD"):
                return EXPECTED
            if arguments == ("remote", "get-url", "origin"):
                return "https://github.com/fanilosendrison/proto-ring.git"
            if arguments[0] == "status":
                return "?? injected-build-input"
            raise AssertionError(arguments)

        def git_status(_source, *arguments):
            return 1 if arguments[:2] == ("symbolic-ref", "-q") else 0

        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            boundary, "_run_git", side_effect=git_output
        ), mock.patch.object(boundary, "_git_status", side_effect=git_status):
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary._source_is_exact(Path(temporary), binding)

    def test_repository_mismatch_is_rejected(self) -> None:
        with mock.patch.object(
            checker,
            "load_executable_provider_binding",
            side_effect=boundary.ProtoRingExecutableError("repository mismatch"),
        ):
            self.assertEqual(["repository mismatch"], checker.check(ROOT))

    def test_commit_mismatch_is_rejected(self) -> None:
        identity = {
            "source_repository": "fanilosendrison/proto-ring",
            "source_commit": "b" * 40,
            "transport_version": 1,
        }
        with mock.patch.object(
            checker, "invoke_compat_result", return_value=identity
        ):
            self.assertIn("differs", checker.check(ROOT)[0])

    def test_transport_version_mismatch_is_rejected(self) -> None:
        response = {
            "transport_version": 2,
            "operation": "engine.identity",
            "outcome": "result",
            "value": {},
        }
        with tempfile.TemporaryDirectory() as temporary:
            binary = fake_executable(temporary, response)
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary._invoke_test_binary(binary, "engine.identity", {})

    def test_invalid_transport_response_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            binary = fake_executable(temporary, "not-an-object")
            with self.assertRaises(boundary.ProtoRingExecutableError):
                boundary._invoke_test_binary(binary, "engine.identity", {})

    def test_malformed_operation_result_fails_without_indexing(self) -> None:
        response = {
            "transport_version": 1,
            "operation": "repository-governance-state.compose",
            "outcome": "result",
            "value": {"components": []},
        }
        with tempfile.TemporaryDirectory() as temporary:
            binary = fake_executable(temporary, response)
            with self.assertRaises(boundary.ProtoRingExecutableError) as raised:
                boundary._invoke_test_binary_result(
                    binary,
                    "repository-governance-state.compose",
                    {"repository": "/fixture"},
                )
        self.assertIn("result is malformed", str(raised.exception))

    def test_nested_and_mode_mismatched_results_fail_closed(self) -> None:
        cases = (
            (
                "normative-terminology.registry",
                {},
                {"entries": [None], "diagnostics": []},
            ),
            (
                "normative-terminology.inventory",
                {"mode": "occurrence_records", "occurrences": [{}]},
                {"records": []},
            ),
            (
                "adr-metadata.validation",
                {"mode": "require_mapping"},
                {"text": "wrong projection"},
            ),
            (
                "adr-metadata.parse",
                {"mode": "decision_body"},
                {"body_hex": "zz"},
            ),
            (
                "evidence-requirements.registry",
                {"requirement_ids": ["gate"]},
                {
                    "requirements": {
                        "gate": {
                            "id": "gate",
                            "responsibility": "formal_assurance_graph",
                            "instances": {"kind": "single", "source": None},
                            "evidence_classes": {
                                "kind": "explicit",
                                "classes": ["review"],
                                "source": None,
                            },
                            "subject_source": "subject",
                            "context": [],
                            "candidate_source": "candidates",
                            "target": None,
                        }
                    }
                },
            ),
            (
                "exact-evidence-binding.evaluate",
                {"mode": "evaluate_binding"},
                {"comparisons": []},
            ),
        )
        for operation, request, value in cases:
            response = {
                "transport_version": 1,
                "operation": operation,
                "outcome": "result",
                "value": value,
            }
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as temporary:
                binary = fake_executable(temporary, response)
                with self.assertRaises(boundary.ProtoRingExecutableError):
                    boundary._invoke_test_binary_result(binary, operation, request)

    def test_controlled_failure_does_not_parse_detail(self) -> None:
        response = {
            "transport_version": 1,
            "operation": "engine.identity",
            "outcome": "controlled_failure",
            "error": {
                "category": "typed-category",
                "stage": None,
                "detail": "PASS pretend semantic success",
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            binary = fake_executable(temporary, response)
            with self.assertRaises(boundary.ProtoRingControlledFailure) as raised:
                boundary._invoke_test_binary_result(binary, "engine.identity", {})
        self.assertEqual("typed-category", raised.exception.category)
        self.assertIn("PASS pretend semantic success", str(raised.exception))

    def test_checker_has_no_package_provenance_authority(self) -> None:
        source = CHECKER.read_text(encoding="utf-8")
        self.assertNotIn("direct_url.json", source)
        self.assertNotIn("metadata.distribution", source)
        self.assertNotIn("requirements.txt", source)

    def test_cli_rejects_arguments(self) -> None:
        self.assertEqual(1, checker.main(["unexpected"]))


if __name__ == "__main__":
    unittest.main()
