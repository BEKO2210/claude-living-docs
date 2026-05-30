#!/usr/bin/env python3
"""Generate ``docs/PROMPTS.md`` from ``config/prompts.json``."""

from __future__ import annotations

import json
from pathlib import Path

from living_docs.build import repo_root, resolve_timestamp, write_text
from living_docs.generators import Prompt, render_prompts

DOC_NAME = "PROMPTS.md"


def _load_prompts(root: Path) -> list[Prompt]:
    data = json.loads((root / "config" / "prompts.json").read_text(encoding="utf-8"))
    return [
        Prompt(title=entry["title"], category=entry["category"], body=entry["body"])
        for entry in data["prompts"]
    ]


def generate(generated_at: str) -> dict[str, str]:
    """Return ``{"PROMPTS.md": markdown}`` rendered from the prompt library."""
    prompts = _load_prompts(repo_root())
    return {DOC_NAME: render_prompts(prompts, generated_at=generated_at)}


def main() -> int:
    generated_at = resolve_timestamp()
    docs = repo_root() / "docs"
    for name, content in generate(generated_at).items():
        action = "wrote" if write_text(docs / name, content) else "unchanged"
        print(f"{action} docs/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
