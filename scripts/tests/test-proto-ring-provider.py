#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CHECKER = SCRIPTS / "check-proto-ring-provider.py"
EXPECTED = "890ed560e61e205067bdf3628e419302613ef06e"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_checker():
    spec = importlib.util.spec_from_file_location("check_proto_ring_provider", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load proto-ring provider checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


class ProtoRingProviderTests(unittest.TestCase):
    def test_live_effective_provider_matches_authority(self) -> None:
        self.assertEqual(EXPECTED, checker.authoritative_proto_ring_commit(ROOT))
        self.assertEqual(EXPECTED, checker.installed_proto_ring_commit())
        self.assertEqual([], checker.check(ROOT))

    def test_installation_stale_fails(self) -> None:
        with mock.patch.object(
            checker, "authoritative_proto_ring_commit", return_value="a" * 40
        ), mock.patch.object(
            checker, "installed_proto_ring_commit", return_value="b" * 40
        ):
            self.assertNotEqual([], checker.check(ROOT))

    def test_missing_or_malformed_authority_fails_closed(self) -> None:
        with mock.patch.object(
            checker,
            "authoritative_proto_ring_commit",
            side_effect=ValueError("missing exact authority"),
        ):
            self.assertEqual(["missing exact authority"], checker.check(ROOT))

    def test_missing_distribution_provenance_fails_closed(self) -> None:
        with mock.patch.object(
            checker.metadata,
            "distribution",
            side_effect=checker.metadata.PackageNotFoundError("proto-ring"),
        ):
            self.assertIn("proto-ring", checker.check(ROOT)[0])

    def test_wrong_installed_repository_fails_closed(self) -> None:
        direct_url = json.dumps(
            {
                "url": "https://github.com/example/proto-ring.git",
                "vcs_info": {"vcs": "git", "commit_id": EXPECTED},
            }
        )
        distribution = mock.Mock()
        distribution.read_text.return_value = direct_url
        with mock.patch.object(
            checker.metadata, "distribution", return_value=distribution
        ):
            self.assertIn("does not identify", checker.check(ROOT)[0])

    def test_malformed_pep_610_vcs_fails_closed(self) -> None:
        direct_url = json.dumps(
            {
                "url": "https://github.com/fanilosendrison/proto-ring.git",
                "vcs_info": {"commit_id": EXPECTED},
            }
        )
        distribution = mock.Mock()
        distribution.read_text.return_value = direct_url
        with mock.patch.object(
            checker.metadata, "distribution", return_value=distribution
        ):
            self.assertIn("not Git VCS", checker.check(ROOT)[0])

    def test_provider_checker_has_no_registry_currentness_responsibility(self) -> None:
        source = CHECKER.read_text(encoding="utf-8")
        self.assertNotIn("governance_bindings", source)
        self.assertNotIn("binding-registry", source)
        self.assertNotIn("check-proto-ring-binding-registry", source)

    def test_cli_rejects_arguments(self) -> None:
        self.assertEqual(1, checker.main(["binding-registry"]))


if __name__ == "__main__":
    unittest.main()
