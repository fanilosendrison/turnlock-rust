#!/usr/bin/env python3
"""Verify byte-exact custody of the fixed pre-retirement Git source tree."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_DIRECTORY = ROOT / "docs/history/formal-assurance-2026-10-20"
EXPECTED_REPOSITORY = "fanilosendrison/turnlock-rust"
EXPECTED_SOURCE_COMMIT = "b1b8902cb2be879f3930c2730002a1ea5e4e1f02"
EXPECTED_SOURCE_TREE = "964b7128908a52151740b68d9c2ca978dbb4f7d1"
EXPECTED_ARCHIVE_FILE = "source-tree.zip"
EXPECTED_TIMESTAMP = (2000, 1, 1, 0, 0, 0)
EXPECTED_MANIFEST_KEYS = {
    "schema_version",
    "repository",
    "source_commit",
    "source_tree",
    "archive_file",
    "archive_sha256",
    "members",
}
EXPECTED_MEMBER_KEYS = {"path", "mode", "git_blob_oid", "size", "sha256"}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class DuplicateJsonKeyError(ValueError):
    """A JSON object repeated a key and is not an unambiguous manifest."""


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateJsonKeyError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _git(root: Path, *arguments: str) -> tuple[int, bytes, bytes]:
    completed = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.returncode, completed.stdout, completed.stderr


def _blob_oid(payload: bytes) -> str:
    framed = b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload
    return hashlib.sha1(framed).hexdigest()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _safe_path(path: str) -> bool:
    return bool(path) and not path.startswith("/") and "\\" not in path and all(
        part not in {"", ".", ".."} for part in path.split("/")
    )


def _read_git_tree(
    root: Path, expected_commit: str, expected_tree: str, errors: list[str]
) -> dict[str, tuple[str, str, bytes]] | None:
    code, _stdout, _stderr = _git(root, "cat-file", "-e", f"{expected_commit}^{{commit}}")
    if code != 0:
        errors.append(f"source commit is unavailable: {expected_commit}")
        return None
    code, stdout, _stderr = _git(root, "rev-parse", f"{expected_commit}^{{tree}}")
    if code != 0:
        errors.append(f"source tree cannot be resolved for commit: {expected_commit}")
        return None
    actual_tree = stdout.decode("ascii", errors="replace").strip()
    if actual_tree != expected_tree:
        errors.append(
            f"source tree identity differs: expected {expected_tree}, found {actual_tree}"
        )
        return None
    code, stdout, stderr = _git(root, "ls-tree", "-rz", "--full-tree", expected_commit)
    if code != 0:
        errors.append(
            "source Git tree cannot be enumerated: "
            + stderr.decode("utf-8", errors="replace").strip()
        )
        return None
    entries: dict[str, tuple[str, str, bytes]] = {}
    for row in (item for item in stdout.split(b"\0") if item):
        try:
            header, raw_path = row.split(b"\t", 1)
            mode_bytes, type_bytes, oid_bytes = header.split(b" ")
            path = raw_path.decode("utf-8", errors="strict")
            mode = mode_bytes.decode("ascii")
            object_type = type_bytes.decode("ascii")
            oid = oid_bytes.decode("ascii")
        except (ValueError, UnicodeDecodeError):
            errors.append("source Git tree contains an invalid or non-UTF-8 entry")
            continue
        if not _safe_path(path):
            errors.append(f"source Git tree contains an unsafe path: {path!r}")
            continue
        if object_type != "blob" or mode not in {"100644", "100755"}:
            errors.append(
                f"source Git tree contains unsupported mode/type: {path} {mode} {object_type}"
            )
            continue
        if path in entries:
            errors.append(f"source Git tree contains a duplicate path: {path}")
            continue
        code, payload, _stderr = _git(root, "cat-file", "blob", oid)
        if code != 0:
            errors.append(f"source object is unavailable: {path} {oid}")
            continue
        if _blob_oid(payload) != oid:
            errors.append(f"source object Git blob OID differs from its bytes: {path}")
            continue
        entries[path] = (mode, oid, payload)
    return entries


def _read_manifest(path: Path, errors: list[str]) -> dict[str, object] | None:
    if path.is_symlink():
        errors.append("archive manifest path must not be a symlink")
        return None
    try:
        text = path.read_text(encoding="utf-8")
        value = json.loads(text, object_pairs_hook=_strict_object)
    except DuplicateJsonKeyError as error:
        errors.append(str(error))
        return None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"archive manifest is invalid: {error}")
        return None
    if type(value) is not dict:
        errors.append("archive manifest must be a JSON object")
        return None
    if set(value) != EXPECTED_MANIFEST_KEYS:
        errors.append("archive manifest has missing or unknown top-level keys")
        return None
    return value


def _validate_manifest_identity(
    manifest: dict[str, object], expected_commit: str, expected_tree: str, errors: list[str]
) -> None:
    expected = {
        "schema_version": 1,
        "repository": EXPECTED_REPOSITORY,
        "source_commit": expected_commit,
        "source_tree": expected_tree,
        "archive_file": EXPECTED_ARCHIVE_FILE,
    }
    for key, expected_value in expected.items():
        actual = manifest.get(key)
        if type(actual) is not type(expected_value) or actual != expected_value:
            errors.append(
                f"archive manifest identity differs for {key}: expected {expected_value!r}, found {actual!r}"
            )
    if not isinstance(manifest.get("archive_sha256"), str) or HEX64.fullmatch(
        manifest["archive_sha256"]
    ) is None:
        errors.append("archive manifest archive_sha256 must be lowercase SHA-256")


def _manifest_entries(
    manifest: dict[str, object], errors: list[str]
) -> dict[str, dict[str, object]] | None:
    members = manifest.get("members")
    if type(members) is not list:
        errors.append("archive manifest members must be a list")
        return None
    entries: dict[str, dict[str, object]] = {}
    ordered_paths: list[str] = []
    for index, item in enumerate(members):
        label = f"archive manifest member {index}"
        if type(item) is not dict or set(item) != EXPECTED_MEMBER_KEYS:
            errors.append(f"{label} has missing or unknown keys")
            continue
        path = item.get("path")
        mode = item.get("mode")
        oid = item.get("git_blob_oid")
        size = item.get("size")
        digest = item.get("sha256")
        if type(path) is not str or not _safe_path(path):
            errors.append(f"{label} has an unsafe path")
            continue
        if path in entries:
            errors.append(f"duplicate manifest member: {path}")
            continue
        if type(mode) is not str or mode not in {"100644", "100755"}:
            errors.append(f"{label} has an unsupported mode")
        if type(oid) is not str or HEX40.fullmatch(oid) is None:
            errors.append(f"{label} has an invalid Git blob OID")
        if type(size) is not int or type(size) is bool or size < 0:
            errors.append(f"{label} has an invalid size")
        if type(digest) is not str or HEX64.fullmatch(digest) is None:
            errors.append(f"{label} has an invalid SHA-256")
        entries[path] = item
        ordered_paths.append(path)
    if ordered_paths != sorted(ordered_paths, key=lambda value: value.encode("utf-8")):
        errors.append("archive manifest members are not sorted by UTF-8 path bytes")
    return entries


def _zip_entries(path: Path, errors: list[str]) -> dict[str, bytes] | None:
    if path.is_symlink():
        errors.append("archive ZIP path must not be a symlink")
        return None
    try:
        with zipfile.ZipFile(path, "r") as archive:
            entries: dict[str, bytes] = {}
            ordered_paths: list[str] = []
            for info in archive.infolist():
                name = info.filename
                if name in entries:
                    errors.append(f"duplicate ZIP member: {name}")
                    continue
                if not _safe_path(name) or name.endswith("/"):
                    errors.append(f"unsafe ZIP member path: {name!r}")
                    continue
                file_type = stat.S_IFMT((info.external_attr >> 16) & 0xFFFF)
                if file_type not in {0, stat.S_IFREG}:
                    errors.append(f"unsupported ZIP member type: {name}")
                if info.flag_bits & 0x1:
                    errors.append(f"encrypted ZIP member is forbidden: {name}")
                if info.date_time != EXPECTED_TIMESTAMP:
                    errors.append(f"ZIP member timestamp differs: {name}")
                if info.compress_type != zipfile.ZIP_DEFLATED:
                    errors.append(f"ZIP member compression differs: {name}")
                try:
                    entries[name] = archive.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile) as error:
                    errors.append(f"archive member cannot be read: {name}: {error}")
                    continue
                ordered_paths.append(name)
            if ordered_paths != sorted(
                ordered_paths, key=lambda value: value.encode("utf-8")
            ):
                errors.append("ZIP members are not sorted by UTF-8 path bytes")
            return entries
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as error:
        errors.append(f"archive ZIP is invalid: {error}")
        return None


def _compare_sets(
    git_entries: dict[str, object],
    manifest_entries: dict[str, object],
    zip_entries: dict[str, object],
    errors: list[str],
) -> None:
    git_paths = set(git_entries)
    manifest_paths = set(manifest_entries)
    zip_paths = set(zip_entries)
    if manifest_paths != git_paths:
        errors.append("manifest member set differs from source Git tree")
    if zip_paths != git_paths:
        errors.append("ZIP member set differs from source Git tree")


def _compare_members(
    git_entries: dict[str, tuple[str, str, bytes]],
    manifest_entries: dict[str, dict[str, object]],
    zip_entries: dict[str, bytes],
    errors: list[str],
) -> None:
    for path in sorted(set(git_entries) & set(manifest_entries) & set(zip_entries)):
        mode, oid, source_payload = git_entries[path]
        manifest = manifest_entries[path]
        zipped_payload = zip_entries[path]
        if manifest.get("mode") != mode:
            errors.append(f"manifest mode differs from source Git tree: {path}")
        if manifest.get("git_blob_oid") != oid:
            errors.append(f"manifest Git blob OID differs from source Git tree: {path}")
        if manifest.get("size") != len(source_payload):
            errors.append(f"manifest size differs from source Git blob: {path}")
        if manifest.get("sha256") != _sha256(source_payload):
            errors.append(f"manifest SHA-256 differs from source Git blob: {path}")
        if _blob_oid(zipped_payload) != oid:
            errors.append(f"archive member Git blob OID differs from source Git tree: {path}")
        if zipped_payload != source_payload:
            errors.append(f"archive member bytes differ from source Git blob: {path}")


def verify_archive(
    root: Path,
    archive_directory: Path,
    expected_commit: str,
    expected_tree: str,
) -> list[str]:
    """Return every detected custody error without modifying repository state."""

    errors: list[str] = []
    root = root.resolve()
    if archive_directory.is_symlink():
        errors.append("archive directory must not be a symlink")
        return errors
    archive_directory = archive_directory.resolve()
    git_entries = _read_git_tree(root, expected_commit, expected_tree, errors)
    if git_entries is None:
        return errors
    manifest = _read_manifest(archive_directory / "source-manifest.json", errors)
    if manifest is None:
        return errors
    _validate_manifest_identity(manifest, expected_commit, expected_tree, errors)
    manifest_entries = _manifest_entries(manifest, errors)
    archive_path = archive_directory / EXPECTED_ARCHIVE_FILE
    if archive_path.is_file():
        try:
            actual_archive_sha = _sha256(archive_path.read_bytes())
            if actual_archive_sha != manifest.get("archive_sha256"):
                errors.append("archive SHA-256 differs from manifest")
        except OSError as error:
            errors.append(f"archive ZIP cannot be read: {error}")
    else:
        errors.append("archive ZIP is missing")
    zip_entries = _zip_entries(archive_path, errors) if archive_path.is_file() else None
    if manifest_entries is None or zip_entries is None:
        return errors
    _compare_sets(git_entries, manifest_entries, zip_entries, errors)
    _compare_members(git_entries, manifest_entries, zip_entries, errors)
    return errors


def main() -> int:
    errors = verify_archive(
        ROOT,
        ARCHIVE_DIRECTORY,
        EXPECTED_SOURCE_COMMIT,
        EXPECTED_SOURCE_TREE,
    )
    if errors:
        for error in errors:
            print(f"ERROR: assurance archive: {error}", file=sys.stderr)
        print("assurance archive: FAILED", file=sys.stderr)
        return 1
    print("assurance archive: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
