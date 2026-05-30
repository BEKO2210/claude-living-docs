#!/usr/bin/env python3
"""Generate ``docs/PROMPTS.md`` from the configured prompts file.

Thin wrapper; prefer ``living-docs update``.
"""

from __future__ import annotations

from living_docs.build import repo_root, resolve_timestamp, write_text
from living_docs.config import load_config
from living_docs.generators import render_prompts
from living_docs.sources import load_prompts


def generate(generated_at: str) -> dict[str, str]:
    """Return ``{"PROMPTS.md": markdown}`` or ``{}`` if no prompts file."""
    config = load_config(repo_root())
    if config.prompts is None or not config.prompts.exists():
        return {}
    return {"PROMPTS.md": render_prompts(load_prompts(config.prompts), generated_at=generated_at)}


def main() -> int:
    config = load_config(repo_root())
    for name, content in generate(resolve_timestamp(config.root)).items():
        action = "wrote" if write_text(config.docs / name, content) else "unchanged"
        print(f"{action} docs/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
