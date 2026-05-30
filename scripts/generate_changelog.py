#!/usr/bin/env python3
"""Generate ``docs/CHANGELOG.md`` from real git tags and commit history.

Thin wrapper; prefer ``living-docs update``. Commits carrying the
``[auto-docs]`` marker are excluded so the changelog does not churn.
"""

from __future__ import annotations

from living_docs.build import repo_root, resolve_timestamp, write_text
from living_docs.config import load_config
from living_docs.generators import render_changelog
from living_docs.sources import collect_releases


def generate(generated_at: str) -> dict[str, str]:
    """Return ``{"CHANGELOG.md": markdown}`` derived from git history."""
    config = load_config(repo_root())
    releases = collect_releases(config.root)
    return {"CHANGELOG.md": render_changelog(releases, generated_at=generated_at)}


def main() -> int:
    config = load_config(repo_root())
    for name, content in generate(resolve_timestamp(config.root)).items():
        action = "wrote" if write_text(config.docs / name, content) else "unchanged"
        print(f"{action} docs/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
