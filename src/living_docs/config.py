"""Project configuration for the Living Docs engine.

A project is configured either with **zero config** (the defaults below) or
through a ``[tool.living_docs]`` table in its ``pyproject.toml``. This is what
lets the same engine document *any* Python project, not just this repository.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

__all__ = ["DEFAULTS", "ProjectConfig", "load_config"]

DEFAULTS: dict[str, object] = {
    "source": "src",
    "docs": "docs",
    "features": "config/features.json",
    "prompts": "config/prompts.json",
    "changelog": True,
    "include_private": False,
}


@dataclass(frozen=True)
class ProjectConfig:
    """Resolved, absolute paths and flags for one project."""

    root: Path
    source: Path
    docs: Path
    features: Path | None
    prompts: Path | None
    include_changelog: bool
    include_private: bool


def _read_table(root: Path) -> dict[str, object]:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return {}
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    tool = data.get("tool", {})
    table = tool.get("living_docs", {}) if isinstance(tool, dict) else {}
    return table if isinstance(table, dict) else {}


def _optional(root: Path, value: object, *, explicit: bool) -> Path | None:
    """Resolve an optional input file.

    Explicitly configured paths are always returned (the file is expected to
    exist); default paths are only used when the file actually exists, so a
    project without a ``config/features.json`` simply skips that document.
    """
    if not value:
        return None
    path = root / str(value)
    if explicit:
        return path
    return path if path.exists() else None


def load_config(root: Path, *, overrides: dict[str, object] | None = None) -> ProjectConfig:
    """Build a :class:`ProjectConfig` for ``root`` from defaults + pyproject."""
    root = root.resolve()
    table = _read_table(root)
    overrides = overrides or {}
    settings = {**DEFAULTS, **table, **overrides}

    return ProjectConfig(
        root=root,
        source=root / str(settings["source"]),
        docs=root / str(settings["docs"]),
        features=_optional(
            root, settings["features"], explicit="features" in table or "features" in overrides
        ),
        prompts=_optional(
            root, settings["prompts"], explicit="prompts" in table or "prompts" in overrides
        ),
        include_changelog=bool(settings["changelog"]),
        include_private=bool(settings["include_private"]),
    )
