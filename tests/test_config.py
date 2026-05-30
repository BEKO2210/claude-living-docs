"""Tests for project configuration loading."""

from __future__ import annotations

from pathlib import Path

from living_docs.config import load_config


def test_zero_config_uses_defaults(tmp_path: Path):
    config = load_config(tmp_path)
    assert config.source == tmp_path / "src"
    assert config.docs == tmp_path / "docs"
    assert config.include_changelog is True
    assert config.include_private is False
    # Default optional files that do not exist are dropped.
    assert config.features is None
    assert config.prompts is None


def test_default_optional_file_used_when_present(tmp_path: Path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "features.json").write_text("{}", encoding="utf-8")
    config = load_config(tmp_path)
    assert config.features == tmp_path / "config" / "features.json"
    assert config.prompts is None


def test_pyproject_overrides(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        "[tool.living_docs]\n"
        'source = "lib"\n'
        'docs = "documentation"\n'
        "changelog = false\n"
        "include_private = true\n",
        encoding="utf-8",
    )
    config = load_config(tmp_path)
    assert config.source == tmp_path / "lib"
    assert config.docs == tmp_path / "documentation"
    assert config.include_changelog is False
    assert config.include_private is True


def test_explicit_feature_path_is_kept_even_if_missing(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        '[tool.living_docs]\nfeatures = "data/feat.json"\n', encoding="utf-8"
    )
    config = load_config(tmp_path)
    # Explicitly configured -> returned regardless of existence.
    assert config.features == tmp_path / "data" / "feat.json"


def test_overrides_argument_wins(tmp_path: Path):
    config = load_config(tmp_path, overrides={"source": "engine"})
    assert config.source == tmp_path / "engine"
