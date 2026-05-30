#!/usr/bin/env python3
"""Orchestrate every documentation generator (compatibility wrapper).

``living-docs update`` / ``living-docs check`` are the preferred entry points;
this script is kept for the documented ``scripts/`` workflow and simply
delegates to the same engine.

Usage::

    python scripts/update_all.py            # (re)write docs/
    python scripts/update_all.py --check    # drift detection, exit 1 if stale
"""

from __future__ import annotations

import argparse

from living_docs.build import repo_root, resolve_timestamp
from living_docs.cli import main as cli_main
from living_docs.config import load_config
from living_docs.engine import build_documents


def build_all(generated_at: str) -> dict[str, str]:
    """Run every generator and merge their outputs into ``{name: content}``."""
    return build_documents(load_config(repo_root()), generated_at)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit 1 if docs are stale.")
    args = parser.parse_args(argv)
    return cli_main(["check" if args.check else "update"])


# Kept importable for tests that exercise the resolver directly.
def current_timestamp() -> str:
    """Return the deterministic build timestamp for this repository."""
    return resolve_timestamp(repo_root())


if __name__ == "__main__":
    raise SystemExit(main())
