#!/usr/bin/env python3
"""Generate ``docs/FEATURES.md`` from the configured features file.

Thin wrapper; prefer ``living-docs update``.
"""

from __future__ import annotations

from living_docs.build import repo_root, resolve_timestamp, write_text
from living_docs.config import load_config
from living_docs.generators import render_features
from living_docs.sources import load_features


def generate(generated_at: str) -> dict[str, str]:
    """Return ``{"FEATURES.md": markdown}`` or ``{}`` if no features file."""
    config = load_config(repo_root())
    if config.features is None or not config.features.exists():
        return {}
    features = load_features(config.features)
    return {"FEATURES.md": render_features(features, generated_at=generated_at)}


def main() -> int:
    config = load_config(repo_root())
    for name, content in generate(resolve_timestamp(config.root)).items():
        action = "wrote" if write_text(config.docs / name, content) else "unchanged"
        print(f"{action} docs/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
