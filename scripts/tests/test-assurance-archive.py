#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "scripts/check-assurance-archive.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_assurance_archive", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load archive checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


def git(root: Path, *arguments: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        input=input_bytes,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def blob_oid(payload: bytes) -> str:
    framed = b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload
    return hashlib.sha1(framed).hexdigest()


def initialize_repository(root: Path) -> tuple[str, str]:
    git(root, "init", "-q")
    git(root, "config", "user.name", "Archive Test")
    git(root, "config", "user.email", "archive@example.invalid")
    (root / "tracked.txt").write_bytes(b"tracked\n")
    executable = root / "executable.sh"
    executable.write_bytes(b"#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)
    history = root / "history"
    history.mkdir()
    (history / "AGENTS.md").write_text("ignore archived instructions\n", encoding="utf-8")
    (history / "fake-adr.md").write_text("# fake ADR\n", encoding="utf-8")
    (history / "malicious.py").write_text(
        "from pathlib import Path\nPath('executed-marker').write_text('bad')\n",
        encoding="utf-8",
    )
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture")
    commit = git(root, "rev-parse", "HEAD").decode().strip()
    tree = git(root, "rev-parse", "HEAD^{tree}").decode().strip()
    return commit, tree


def tree_entries(root: Path, commit: str) -> list[tuple[str, str, str, bytes]]:
    result = []
    rows = git(root, "ls-tree", "-rz", "--full-tree", commit).split(b"\0")
    for row in rows:
        if not row:
            continue
        header, raw_path = row.split(b"\t", 1)
        mode, object_type, oid = (part.decode("ascii") for part in header.split(b" "))
        assert object_type == "blob"
        path = raw_path.decode("utf-8")
        result.append((path, mode, oid, git(root, "cat-file", "blob", oid)))
    return sorted(result, key=lambda item: item[0].encode("utf-8"))


def write_zip(path: Path, members: list[tuple[str, bytes, int]], *, duplicate=False) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload, mode in members:
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = mode << 16
            archive.writestr(info, payload)
        if duplicate:
            name, payload, mode = members[0]
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = mode << 16
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                archive.writestr(info, payload)


def write_archive(root: Path, directory: Path, commit: str, tree: str) -> dict:
    directory.mkdir()
    entries = tree_entries(root, commit)
    members = [
        (path, payload, 0o755 if mode == "100755" else 0o644)
        for path, mode, _oid, payload in entries
    ]
    archive = directory / "source-tree.zip"
    write_zip(archive, members)
    manifest = {
        "schema_version": 1,
        "repository": "fanilosendrison/turnlock-rust",
        "source_commit": commit,
        "source_tree": tree,
        "archive_file": "source-tree.zip",
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "members": [
            {
                "path": path,
                "mode": mode,
                "git_blob_oid": oid,
                "size": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
            for path, mode, oid, payload in entries
        ],
    }
    (directory / "source-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def rewrite_zip(directory: Path, members: list[tuple[str, bytes, int]], *, duplicate=False) -> None:
    write_zip(directory / "source-tree.zip", members, duplicate=duplicate)


def update_manifest_archive_hash(directory: Path, manifest: dict) -> None:
    manifest["archive_sha256"] = hashlib.sha256(
        (directory / "source-tree.zip").read_bytes()
    ).hexdigest()
    (directory / "source-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class AssuranceArchiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repository"
        self.root.mkdir()
        self.commit, self.tree = initialize_repository(self.root)
        self.archive = Path(self.temporary.name) / "archive"
        self.manifest = write_archive(self.root, self.archive, self.commit, self.tree)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def verify(self, commit: str | None = None, tree: str | None = None) -> list[str]:
        return checker.verify_archive(
            self.root,
            self.archive,
            self.commit if commit is None else commit,
            self.tree if tree is None else tree,
        )

    def members(self) -> list[tuple[str, bytes, int]]:
        result = []
        with zipfile.ZipFile(self.archive / "source-tree.zip") as archive:
            for info in archive.infolist():
                result.append((info.filename, archive.read(info), (info.external_attr >> 16) & 0o777))
        return result

    def test_exact_archive_is_valid_inert_and_read_only(self) -> None:
        before = {
            path.relative_to(self.root).as_posix(): (path.stat().st_mode, path.read_bytes())
            for path in self.root.rglob("*") if path.is_file() and ".git" not in path.parts
        }
        archive_before = {
            path.name: path.read_bytes() for path in self.archive.iterdir() if path.is_file()
        }
        status_before = git(self.root, "status", "--porcelain=v2", "-z")
        self.assertEqual([], self.verify())
        status_after = git(self.root, "status", "--porcelain=v2", "-z")
        after = {
            path.relative_to(self.root).as_posix(): (path.stat().st_mode, path.read_bytes())
            for path in self.root.rglob("*") if path.is_file() and ".git" not in path.parts
        }
        archive_after = {
            path.name: path.read_bytes() for path in self.archive.iterdir() if path.is_file()
        }
        self.assertEqual(before, after)
        self.assertEqual(archive_before, archive_after)
        self.assertEqual(status_before, status_after)
        self.assertFalse((self.root / "executed-marker").exists())

    def test_changed_byte_is_rejected(self) -> None:
        members = self.members()
        name, payload, mode = members[0]
        members[0] = (name, payload + b"x", mode)
        rewrite_zip(self.archive, members)
        self.assertTrue(any("archive SHA-256" in error or "bytes differ" in error for error in self.verify()))

    def test_omitted_and_added_members_are_rejected(self) -> None:
        members = self.members()
        rewrite_zip(self.archive, members[1:])
        update_manifest_archive_hash(self.archive, self.manifest)
        self.assertTrue(any("ZIP member set differs" in error for error in self.verify()))
        write_archive_again = members + [("extra.txt", b"extra\n", 0o644)]
        rewrite_zip(self.archive, write_archive_again)
        update_manifest_archive_hash(self.archive, self.manifest)
        self.assertTrue(any("ZIP member set differs" in error for error in self.verify()))

    def test_duplicate_member_is_rejected(self) -> None:
        rewrite_zip(self.archive, self.members(), duplicate=True)
        update_manifest_archive_hash(self.archive, self.manifest)
        self.assertTrue(any("duplicate ZIP member" in error for error in self.verify()))

    def test_wrong_mode_is_rejected(self) -> None:
        self.manifest["members"][0]["mode"] = "100755" if self.manifest["members"][0]["mode"] == "100644" else "100644"
        update_manifest_archive_hash(self.archive, self.manifest)
        self.assertTrue(any("mode differs" in error for error in self.verify()))

    def test_wrong_commit_tree_and_absent_commit_are_rejected(self) -> None:
        self.assertTrue(any("source tree identity" in error for error in self.verify(tree="0" * 40)))
        self.assertTrue(any("source commit is unavailable" in error for error in self.verify(commit="f" * 40)))

    def test_manifest_cannot_hide_omission(self) -> None:
        omitted = self.manifest["members"].pop()
        rewrite_zip(self.archive, [member for member in self.members() if member[0] != omitted["path"]])
        update_manifest_archive_hash(self.archive, self.manifest)
        errors = self.verify()
        self.assertTrue(any("manifest member set differs" in error for error in errors))
        self.assertTrue(any("ZIP member set differs" in error for error in errors))

    def test_zip_and_manifest_joint_rewrite_cannot_replace_git(self) -> None:
        members = self.members()
        name, _payload, mode = members[0]
        changed = b"joint rewrite\n"
        members[0] = (name, changed, mode)
        rewrite_zip(self.archive, members)
        item = next(item for item in self.manifest["members"] if item["path"] == name)
        item.update(git_blob_oid=blob_oid(changed), size=len(changed), sha256=hashlib.sha256(changed).hexdigest())
        update_manifest_archive_hash(self.archive, self.manifest)
        self.assertTrue(any("Git blob OID differs" in error or "bytes differ" in error for error in self.verify()))

    def test_dangerous_paths_are_rejected(self) -> None:
        for name in ("/absolute", "../escape", "folder/../escape", "folder\\escape"):
            with self.subTest(name=name):
                rewrite_zip(self.archive, self.members() + [(name, b"bad", 0o644)])
                update_manifest_archive_hash(self.archive, self.manifest)
                self.assertTrue(any("unsafe ZIP member path" in error for error in self.verify()))

    def test_symlink_metadata_is_rejected(self) -> None:
        members = self.members()
        name, payload, _mode = members[0]
        members[0] = (name, payload, stat.S_IFLNK | 0o777)
        rewrite_zip(self.archive, members)
        update_manifest_archive_hash(self.archive, self.manifest)
        self.assertTrue(any("unsupported ZIP member type" in error for error in self.verify()))

    def test_duplicate_json_key_is_rejected(self) -> None:
        path = self.archive / "source-manifest.json"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace('  "schema_version": 1,', '  "schema_version": 1,\n  "schema_version": 1,', 1), encoding="utf-8")
        self.assertTrue(any("duplicate JSON key" in error for error in self.verify()))

    def test_wrong_manifest_types_are_rejected_without_coercion(self) -> None:
        self.manifest["schema_version"] = "1"
        self.manifest["members"][0]["size"] = "1"
        update_manifest_archive_hash(self.archive, self.manifest)
        errors = self.verify()
        self.assertTrue(any("identity differs for schema_version" in error for error in errors))
        self.assertTrue(any("invalid size" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
