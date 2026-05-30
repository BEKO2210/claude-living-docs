"""Tests for the input-loading layer (JSON config + git history)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from living_docs.sources import (
    AUTO_DOCS_MARKER,
    collect_releases,
    load_benchmarks,
    load_features,
    load_prompts,
)


def test_load_features_and_prompts(tmp_path: Path):
    feat = tmp_path / "features.json"
    feat.write_text(
        json.dumps(
            {"features": [{"name": "A", "status": "beta", "description": "d", "tags": ["x"]}]}
        ),
        encoding="utf-8",
    )
    features = load_features(feat)
    assert features[0].name == "A"
    assert features[0].tags == ("x",)

    prom = tmp_path / "prompts.json"
    prom.write_text(
        json.dumps({"prompts": [{"title": "T", "category": "C", "body": "B"}]}),
        encoding="utf-8",
    )
    assert load_prompts(prom)[0].category == "C"


def test_load_benchmarks_missing_returns_empty(tmp_path: Path):
    assert load_benchmarks(tmp_path) == []


def test_load_benchmarks_parses_rows(tmp_path: Path):
    (tmp_path / "benchmarks").mkdir()
    (tmp_path / "benchmarks" / "results.json").write_text(
        json.dumps(
            {"tools": [{"tool": "x", "median_ms": 1.0, "stdev_ms": 0.1, "output_lines": 9}]}
        ),
        encoding="utf-8",
    )
    rows = load_benchmarks(tmp_path)
    assert rows[0].tool == "x"
    assert rows[0].output_lines == 9


def _git(repo: Path, *args: str) -> None:
    env = {
        "GIT_AUTHOR_NAME": "T",
        "GIT_AUTHOR_EMAIL": "t@e.com",
        "GIT_COMMITTER_NAME": "T",
        "GIT_COMMITTER_EMAIL": "t@e.com",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "PATH": os.environ.get("PATH", ""),
    }
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)


def test_collect_releases_excludes_auto_docs_commits(tmp_path: Path):
    _git(tmp_path, "init", "-q")
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "feat: real change")
    (tmp_path / "b.txt").write_text("2", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", f"docs: regenerate {AUTO_DOCS_MARKER}")

    releases = collect_releases(tmp_path)
    assert len(releases) == 1
    unreleased = releases[0]
    assert unreleased.version == "Unreleased"
    assert "feat: real change" in unreleased.commits
    # The [auto-docs] commit is filtered out.
    assert all(AUTO_DOCS_MARKER not in commit for commit in unreleased.commits)


def test_collect_releases_with_tag(tmp_path: Path):
    _git(tmp_path, "init", "-q")
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "first")
    _git(tmp_path, "tag", "v1.0")

    releases = collect_releases(tmp_path)
    versions = [r.version for r in releases]
    assert "v1.0" in versions
