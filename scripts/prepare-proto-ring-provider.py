#!/usr/bin/env python3
"""Explicitly realize the bound native proto-ring compatibility provider outside Turnlock."""

from __future__ import annotations

import contextlib
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Iterator

from proto_ring_executable_binding import (
    PROTO_RING_TRANSPORT_VERSION,
    ExecutableProviderBinding,
    ProtoRingExecutableError,
    _binary_path,
    _canonical_json,
    _invoke_binary,
    _source_is_exact,
    _validate_identity,
    cache_base,
    load_executable_provider_binding,
    managed_provider_root,
)

ROOT = Path(__file__).resolve().parents[1]


def _run(arguments: list[str], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        arguments, cwd=cwd, check=False, capture_output=True, text=True
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "command failed"
        raise ProtoRingExecutableError(message)
    return completed.stdout.strip()


@contextlib.contextmanager
def _exclusive_lock(binding: ExecutableProviderBinding) -> Iterator[None]:
    lock = cache_base() / "turnlock-rust" / "proto-ring" / ".prepare.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a+", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _reset_source(source: Path, binding: ExecutableProviderBinding) -> None:
    """Construct a managed, detached checkout exactly at the immutable binding."""

    if source.exists():
        shutil.rmtree(source)
    source.parent.mkdir(parents=True, exist_ok=True)
    _run(["git", "init", "--quiet", str(source)])
    _run(
        [
            "git",
            "-C",
            str(source),
            "remote",
            "add",
            "origin",
            f"https://github.com/{binding.repository}.git",
        ]
    )
    _run(
        ["git", "-C", str(source), "fetch", "--depth=1", "origin", binding.commit]
    )
    _run(["git", "-C", str(source), "checkout", "--detach", "FETCH_HEAD"])
    _source_is_exact(source, binding)


def _cached_source_is_valid(source: Path, binding: ExecutableProviderBinding) -> bool:
    try:
        _source_is_exact(source, binding)
    except ProtoRingExecutableError:
        return False
    return True


def _build(
    provider_root: Path, source: Path, binding: ExecutableProviderBinding
) -> dict[str, object]:
    build = provider_root / "build"
    if build.exists():
        shutil.rmtree(build)
    _run(
        [
            "cargo",
            "build",
            "--release",
            "--locked",
            "--target-dir",
            str(build),
            "-p",
            "proto-ring-compat",
        ],
        cwd=source,
    )
    _source_is_exact(source, binding)
    binary = _binary_path(provider_root)
    if not binary.is_file():
        raise ProtoRingExecutableError("proto-ring build did not produce proto-ring-compat")
    response = _invoke_binary(binary, "engine.identity", {}, binding=None)
    _validate_identity(response, binding)
    return {
        "repository": binding.repository,
        "commit": binding.commit,
        "transport_version": PROTO_RING_TRANSPORT_VERSION,
        "binary_sha256": _sha256(binary),
        "rustc_version": _run(["rustc", "--version"], cwd=source),
        "cargo_version": _run(["cargo", "--version"], cwd=source),
    }


def _sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare(root: Path = ROOT) -> dict[str, object]:
    binding = load_executable_provider_binding(root)
    provider_root = managed_provider_root(binding)
    source = provider_root / "source"
    with _exclusive_lock(binding):
        if not _cached_source_is_valid(source, binding):
            _reset_source(source, binding)
        manifest = _build(provider_root, source, binding)
        provider_root.mkdir(parents=True, exist_ok=True)
        temporary = provider_root / "realization.json.tmp"
        temporary.write_bytes(_canonical_json(manifest))
        os.replace(temporary, provider_root / "realization.json")
    return manifest


def main(arguments: list[str] | None = None) -> int:
    argv = sys.argv[1:] if arguments is None else arguments
    if argv:
        print("usage: prepare-proto-ring-provider.py", file=sys.stderr)
        return 1
    try:
        manifest = prepare()
    except ProtoRingExecutableError as error:
        print(f"ERROR: native proto-ring preparation: {error}", file=sys.stderr)
        return 1
    print(
        "native proto-ring provider: READY "
        f"({manifest['repository']}@{manifest['commit']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
