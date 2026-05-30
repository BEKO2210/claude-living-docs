"""Turn a :class:`ProjectConfig` into a set of generated documents.

This is the single place that decides *which* documents a project gets and
wires the sources to the renderers. Both the CLI and the thin ``scripts/``
wrappers call into here, so behaviour can never diverge between them.
"""

from __future__ import annotations

from .build import write_text
from .config import ProjectConfig
from .extractors import extract_directory
from .generators import (
    render_api,
    render_changelog,
    render_features,
    render_prompts,
)
from .sources import collect_releases, load_benchmarks, load_features, load_prompts

__all__ = ["build_documents", "check_documents", "write_documents"]


def build_documents(config: ProjectConfig, generated_at: str) -> dict[str, str]:
    """Render every enabled document, returned as ``{filename: markdown}``."""
    documents: dict[str, str] = {}

    modules = (
        extract_directory(config.source, include_private=config.include_private)
        if config.source.exists()
        else ()
    )
    documents["API.md"] = render_api(
        modules, generated_at=generated_at, benchmarks=load_benchmarks(config.root)
    )

    if config.features is not None and config.features.exists():
        documents["FEATURES.md"] = render_features(
            load_features(config.features), generated_at=generated_at
        )

    if config.include_changelog:
        documents["CHANGELOG.md"] = render_changelog(
            collect_releases(config.root), generated_at=generated_at
        )

    if config.prompts is not None and config.prompts.exists():
        documents["PROMPTS.md"] = render_prompts(
            load_prompts(config.prompts), generated_at=generated_at
        )

    return dict(sorted(documents.items()))


def write_documents(config: ProjectConfig, documents: dict[str, str]) -> list[str]:
    """Write ``documents`` into ``config.docs``; return the changed filenames."""
    changed: list[str] = []
    for name, content in documents.items():
        if write_text(config.docs / name, content):
            changed.append(name)
    return changed


def check_documents(config: ProjectConfig, documents: dict[str, str]) -> list[str]:
    """Return the filenames whose committed content differs from ``documents``."""
    drifted: list[str] = []
    for name, content in documents.items():
        target = config.docs / name
        actual = target.read_text(encoding="utf-8") if target.exists() else ""
        if actual != content:
            drifted.append(name)
    return drifted
