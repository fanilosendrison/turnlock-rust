#!/usr/bin/env python3
"""Bind Turnlock-Rust's ARM realization to the shared GitHub live checker."""

from pathlib import Path

from proto_ring.github_authoritative_ref_monotonicity import run

ROOT = Path(__file__).resolve().parents[1]
BINDING = (
    ROOT
    / "docs/repository-governance/turnlock-rust-authoritative-ref-monotonicity.md"
)


if __name__ == "__main__":
    raise SystemExit(run(BINDING))
