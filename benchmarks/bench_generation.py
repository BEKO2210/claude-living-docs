#!/usr/bin/env python3
"""Benchmark our API-doc generation against pdoc and sphinx-apidoc.

Compatibility wrapper around the package implementation; ``living-docs bench``
is the preferred entry point. Runs the real tools on this repo's ``src/`` tree
and writes measured numbers to ``benchmarks/results.json`` (also re-embedding
the comparison table into ``docs/API.md``).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from living_docs.cli import main  # noqa: E402


def run() -> int:
    return main(["-C", str(REPO_ROOT), "bench", "--runs", "10"])


if __name__ == "__main__":
    raise SystemExit(run())
