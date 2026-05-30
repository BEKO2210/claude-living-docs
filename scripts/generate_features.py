#!/usr/bin/env python3
"""Generate ``docs/FEATURES.md`` from ``config/features.json``."""

from __future__ import annotations

import json
from pathlib import Path

from living_docs.build import repo_root, resolve_timestamp, write_text
from living_docs.generators import Feature, render_features

DOC_NAME = "FEATURES.md"


def _load_features(root: Path) -> list[Feature]:
    data = json.loads((root / "config" / "features.json").read_text(encoding="utf-8"))
    features: list[Feature] = []
    for entry in data["features"]:
        features.append(
            Feature(
                name=entry["name"],
                status=entry["status"],
                description=entry["description"],
                since=entry.get("since"),
                tags=tuple(entry.get("tags", [])),
            )
        )
    return features


def generate(generated_at: str) -> dict[str, str]:
    """Return ``{"FEATURES.md": markdown}`` rendered from the feature matrix."""
    features = _load_features(repo_root())
    return {DOC_NAME: render_features(features, generated_at=generated_at)}


def main() -> int:
    generated_at = resolve_timestamp()
    docs = repo_root() / "docs"
    for name, content in generate(generated_at).items():
        action = "wrote" if write_text(docs / name, content) else "unchanged"
        print(f"{action} docs/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
