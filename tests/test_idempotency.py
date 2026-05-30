"""Idempotency and build-helper tests.

Generating twice at a fixed timestamp must be byte-identical, and the shared
build helpers (timestamp resolution, conditional writes) must behave exactly.
"""

from __future__ import annotations

from datetime import UTC, datetime

import generate_api_docs
import generate_changelog
import generate_features
import generate_prompts
import update_all

from living_docs import build

TS = "2024-01-01T00:00:00+00:00"

GENERATORS = [
    generate_api_docs.generate,
    generate_features.generate,
    generate_changelog.generate,
    generate_prompts.generate,
]


def test_each_generator_is_byte_identical():
    for generate in GENERATORS:
        first = generate(TS)
        second = generate(TS)
        assert first == second
        for content in first.values():
            assert content.endswith("\n")


def test_build_all_is_byte_identical_and_complete():
    first = update_all.build_all(TS)
    second = update_all.build_all(TS)
    assert first == second
    assert set(first) == {"API.md", "FEATURES.md", "CHANGELOG.md", "PROMPTS.md"}


def test_update_all_check_passes_against_committed_docs(tmp_path, capsys):
    # Writing then immediately checking must report no drift.
    documents = update_all.build_all(TS)
    for name, content in documents.items():
        (tmp_path / name).write_text(content, encoding="utf-8")
    rc = update_all._check(documents, tmp_path)
    assert rc == 0
    assert "up to date" in capsys.readouterr().out


def test_update_all_check_detects_drift(tmp_path):
    documents = update_all.build_all(TS)
    # Leave docs dir empty -> everything is "drifted".
    rc = update_all._check(documents, tmp_path)
    assert rc == 1


def test_resolve_timestamp_prefers_explicit_override(monkeypatch):
    monkeypatch.setenv("LIVING_DOCS_TIMESTAMP", "2030-12-31T12:00:00+00:00")
    assert build.resolve_timestamp() == "2030-12-31T12:00:00+00:00"


def test_resolve_timestamp_uses_source_date_epoch(monkeypatch):
    monkeypatch.delenv("LIVING_DOCS_TIMESTAMP", raising=False)
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "0")
    expected = datetime.fromtimestamp(0, tz=UTC).isoformat()
    assert build.resolve_timestamp() == expected


def test_resolve_timestamp_falls_back_to_git(monkeypatch):
    monkeypatch.delenv("LIVING_DOCS_TIMESTAMP", raising=False)
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    # In this repository git is available, so a real ISO date comes back.
    assert build.resolve_timestamp()


def test_run_git_returns_empty_on_failure():
    assert build.run_git(["not-a-real-subcommand-xyz"]) == ""


def test_write_text_only_writes_on_change(tmp_path):
    target = tmp_path / "out.md"
    assert build.write_text(target, "one") is True
    assert build.write_text(target, "one") is False  # unchanged
    assert build.write_text(target, "two") is True  # changed
    assert target.read_text(encoding="utf-8") == "two"


def test_repo_root_contains_src():
    assert (build.repo_root() / "src" / "living_docs").is_dir()
