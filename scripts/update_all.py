#!/usr/bin/env python3
"""Orchestrate every documentation generator.

Usage::

    python scripts/update_all.py            # (re)write docs/
    python scripts/update_all.py --check    # drift detection, exit 1 if stale

In ``--check`` mode nothing is written: each document is generated in memory
and diffed against the committed file in ``docs/``. A non-zero exit means the
checked-in docs no longer match the sources.
"""

from __future__ import annotations

import argparse
import difflib
import sys
from collections.abc import Callable
from pathlib import Path

# Allow running both as a script and as a module without installing scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_api_docs
import generate_changelog
import generate_features
import generate_prompts

from living_docs.build import repo_root, resolve_timestamp, write_text

Generator = Callable[[str], dict[str, str]]

# Order is stable and explicit so the report and any diffs read predictably.
GENERATORS: tuple[Generator, ...] = (
    generate_api_docs.generate,
    generate_features.generate,
    generate_changelog.generate,
    generate_prompts.generate,
)


def build_all(generated_at: str) -> dict[str, str]:
    """Run every generator and merge their outputs into ``{name: content}``."""
    documents: dict[str, str] = {}
    for generate in GENERATORS:
        documents.update(generate(generated_at))
    return dict(sorted(documents.items()))


def _check(documents: dict[str, str], docs_dir: Path) -> int:
    drifted: list[str] = []
    for name, expected in documents.items():
        target = docs_dir / name
        actual = target.read_text(encoding="utf-8") if target.exists() else ""
        if actual != expected:
            drifted.append(name)
            diff = difflib.unified_diff(
                actual.splitlines(keepends=True),
                expected.splitlines(keepends=True),
                fromfile=f"docs/{name} (committed)",
                tofile=f"docs/{name} (generated)",
            )
            sys.stdout.writelines(diff)
    if drifted:
        print(f"\nDRIFT: {len(drifted)} document(s) out of date: {', '.join(drifted)}")
        print("Run `python scripts/update_all.py` and commit the result.")
        return 1
    print(f"OK: {len(documents)} document(s) up to date.")
    return 0


def _write(documents: dict[str, str], docs_dir: Path) -> int:
    changed = 0
    for name, content in documents.items():
        if write_text(docs_dir / name, content):
            changed += 1
            print(f"wrote docs/{name}")
        else:
            print(f"unchanged docs/{name}")
    print(f"\n{changed} document(s) updated, {len(documents) - changed} unchanged.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; exit 1 if committed docs are out of date.",
    )
    args = parser.parse_args(argv)

    documents = build_all(resolve_timestamp())
    docs_dir = repo_root() / "docs"

    if args.check:
        return _check(documents, docs_dir)
    return _write(documents, docs_dir)


if __name__ == "__main__":
    raise SystemExit(main())
