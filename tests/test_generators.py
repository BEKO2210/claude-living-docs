"""Markdown output-format tests for the pure renderers."""

from __future__ import annotations

from living_docs.extractors import extract_source
from living_docs.generators import (
    BenchmarkRow,
    Feature,
    Prompt,
    Release,
    auto_generated_header,
    render_api,
    render_changelog,
    render_features,
    render_prompts,
)

TS = "2024-01-01T00:00:00+00:00"

SOURCE = '''"""Tiny module."""


def documented(x: int) -> int:
    """Doubles x."""
    return x * 2


def undocumented(y):
    return y
'''


def test_header_format_is_exact():
    assert auto_generated_header(TS) == f"*🤖 AUTO-GENERATED on {TS} — do not edit manually*"


def test_every_document_ends_with_single_newline():
    module = extract_source(SOURCE, module_name="tiny")
    out = render_api([module], generated_at=TS)
    assert out.endswith("\n")
    assert not out.endswith("\n\n")


def test_render_api_overview_and_signatures():
    module = extract_source(SOURCE, module_name="tiny")
    out = render_api([module], generated_at=TS)
    assert out.startswith("# API Reference\n")
    assert auto_generated_header(TS) in out
    assert "Modules documented: **1**" in out
    # 1 of 2 callables documented -> 50% coverage.
    assert "**50.0%** coverage" in out
    assert "#### `def documented(x: int) -> int`" in out
    assert "Doubles x." in out
    assert "_No docstring._" in out


def test_render_api_embeds_benchmark_table():
    module = extract_source(SOURCE, module_name="tiny")
    rows = [BenchmarkRow("living-docs", 4.6, 0.3, 177, "AST")]
    out = render_api([module], generated_at=TS, benchmarks=rows)
    assert "## Benchmarks" in out
    assert "| living-docs | 4.60 | 0.30 | 177 | AST |" in out


def test_render_features_table_and_badges():
    features = [
        Feature("Alpha", "stable", "First feature.", since="1.0", tags=("core",)),
        Feature("Beta", "beta", "Second feature."),
    ]
    out = render_features(features, generated_at=TS)
    assert "| Alpha | ✅ stable | 1.0 | `core` |" in out
    assert "| Beta | 🧪 beta | — | — |" in out
    assert "### Alpha" in out
    assert "First feature." in out


def test_render_changelog_with_and_without_releases():
    releases = [Release("v1.0", "2024-01-01", ("feat: thing", "fix: bug"))]
    out = render_changelog(releases, generated_at=TS)
    assert "## v1.0 — 2024-01-01" in out
    assert "- feat: thing" in out

    empty = render_changelog([], generated_at=TS)
    assert "_No releases or commits found._" in empty


def test_render_prompts_groups_sorted_by_category():
    prompts = [
        Prompt("Zeta", "Zeta-Cat", "do zeta"),
        Prompt("Alpha", "Alpha-Cat", "do alpha"),
    ]
    out = render_prompts(prompts, generated_at=TS)
    assert out.index("## Alpha-Cat") < out.index("## Zeta-Cat")
    assert "```text" in out
    assert "do alpha" in out
