#!/usr/bin/env python3
"""Generate ``docs/API.md`` from the configured source tree via AST.

Thin wrapper around :func:`living_docs.engine`; kept for the documented
``scripts/`` workflow. Prefer ``living-docs update`` for day-to-day use.
"""

from __future__ import annotations

from living_docs.build import repo_root, resolve_timestamp, write_text
from living_docs.config import load_config
from living_docs.extractors import extract_directory
from living_docs.generators import render_api
from living_docs.sources import load_benchmarks


def generate(generated_at: str) -> dict[str, str]:
    """Return ``{"API.md": markdown}`` for the current project."""
    config = load_config(repo_root())
    modules = extract_directory(config.source, include_private=config.include_private)
    content = render_api(
        modules, generated_at=generated_at, benchmarks=load_benchmarks(config.root)
    )
    return {"API.md": content}


def main() -> int:
    config = load_config(repo_root())
    for name, content in generate(resolve_timestamp(config.root)).items():
        action = "wrote" if write_text(config.docs / name, content) else "unchanged"
        print(f"{action} docs/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
