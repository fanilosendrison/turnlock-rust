#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

from proto_ring import git_whitespace

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors = git_whitespace.check(ROOT, env=os.environ)

    if errors:
        print("git whitespace check: FAILED")
        for error in errors:
            print(error)
        return 1

    print("git whitespace check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
