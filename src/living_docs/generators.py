"""Pure Markdown renderers.

Every function here takes already-extracted data and returns a Markdown
string. There is no file I/O and no clock access (timestamps are passed in),
which is what makes the generators deterministic and idempotent.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from .extractors import ClassDoc, FunctionDoc, ModuleDoc, count_coverage

# reST inline markup commonly found in docstrings, mapped to plain Markdown.
_REST_ROLE_RE = re.compile(r":\w+:`([^`]+)`")
_REST_LITERAL_BLOCK_RE = re.compile(r"::\s*$", re.MULTILINE)


def rest_to_markdown(text: str) -> str:
    """Convert the reST markup that turns up in docstrings to Markdown.

    Handles cross-reference roles (``:mod:`x```, ``:class:`x```, …) and the
    trailing ``::`` literal-block marker. Double-backtick inline literals are
    already valid Markdown code spans, so they are left as-is.
    """
    text = _REST_ROLE_RE.sub(r"`\1`", text)
    return _REST_LITERAL_BLOCK_RE.sub(":", text)


def _docstring(doc: str | None, *, fallback: str) -> str:
    """Return a cleaned docstring for rendering, or ``fallback`` if empty."""
    return rest_to_markdown(doc.strip()) if doc else fallback

__all__ = [
    "BenchmarkRow",
    "Feature",
    "Prompt",
    "Release",
    "auto_generated_header",
    "render_api",
    "render_changelog",
    "render_features",
    "render_prompts",
    "rest_to_markdown",
]


@dataclass(frozen=True)
class Feature:
    """A single entry from the feature matrix."""

    name: str
    status: str
    description: str
    since: str | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Release:
    """A changelog release: a version, an optional date and its commits."""

    version: str
    date: str | None
    commits: tuple[str, ...]


@dataclass(frozen=True)
class Prompt:
    """A reusable Claude Code prompt grouped under a category."""

    title: str
    category: str
    body: str


@dataclass(frozen=True)
class BenchmarkRow:
    """One row of the generator benchmark comparison table."""

    tool: str
    median_ms: float
    stdev_ms: float
    output_lines: int
    notes: str = ""


def auto_generated_header(generated_at: str) -> str:
    """Return the mandated AUTO-GENERATED banner line for ``generated_at``."""
    return f"*🤖 AUTO-GENERATED on {generated_at} — do not edit manually*"


def _document(title: str, generated_at: str, body: Sequence[str]) -> str:
    lines = [f"# {title}", "", auto_generated_header(generated_at), "", *body]
    text = "\n".join(lines).rstrip("\n")
    return text + "\n"


def _render_function(func: FunctionDoc) -> list[str]:
    prefix = "async def" if func.is_async else "def"
    lines = [f"#### `{prefix} {func.name}{func.signature}`", ""]
    for decorator in func.decorators:
        lines.append(f"- decorator: `@{decorator}`")
    if func.decorators:
        lines.append("")
    lines.append(_docstring(func.docstring, fallback="_No docstring._"))
    lines.append("")
    return lines


def _render_class(klass: ClassDoc) -> list[str]:
    bases = f"({', '.join(klass.bases)})" if klass.bases else ""
    lines = [f"### class `{klass.name}{bases}`", ""]
    lines.append(_docstring(klass.docstring, fallback="_No docstring._"))
    lines.append("")
    for method in klass.methods:
        lines.extend(_render_function(method))
    return lines


def _render_benchmark_table(rows: Sequence[BenchmarkRow]) -> list[str]:
    lines = [
        "## Benchmarks",
        "",
        "Generation of the API docs for `src/` measured against real tools",
        "(`timeit`, 10 runs, median ± stdev):",
        "",
        "| Tool | Median (ms) | Stdev (ms) | Output lines | Notes |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.tool} | {row.median_ms:.2f} | {row.stdev_ms:.2f} "
            f"| {row.output_lines} | {row.notes} |"
        )
    lines.append("")
    return lines


def render_api(
    modules: Sequence[ModuleDoc],
    *,
    generated_at: str,
    benchmarks: Sequence[BenchmarkRow] = (),
) -> str:
    """Render ``API.md`` from extracted modules and optional benchmark rows."""
    documented, total = count_coverage(tuple(modules))
    pct = (documented / total * 100) if total else 0.0

    body: list[str] = [
        "## Overview",
        "",
        f"- Modules documented: **{len(modules)}**",
        f"- Callables: **{total}** "
        f"({documented} with docstrings, **{pct:.1f}%** coverage)",
        "",
    ]

    if benchmarks:
        body.extend(_render_benchmark_table(benchmarks))

    for module in modules:
        body.append(f"## Module `{module.name}`")
        body.append("")
        body.append(f"_Source: `{module.path}`_")
        body.append("")
        body.append(_docstring(module.docstring, fallback="_No module docstring._"))
        body.append("")

        if module.functions:
            body.append("### Functions")
            body.append("")
            for func in module.functions:
                body.extend(_render_function(func))

        for klass in module.classes:
            body.extend(_render_class(klass))

    return _document("API Reference", generated_at, body)


_STATUS_BADGE = {
    "stable": "✅ stable",
    "beta": "🧪 beta",
    "experimental": "⚗️ experimental",
    "deprecated": "⚠️ deprecated",
}


def render_features(features: Sequence[Feature], *, generated_at: str) -> str:
    """Render ``FEATURES.md`` as a status table plus per-feature detail."""
    body: list[str] = [
        "| Feature | Status | Since | Tags |",
        "| --- | --- | --- | --- |",
    ]
    for feature in features:
        badge = _STATUS_BADGE.get(feature.status, feature.status)
        since = feature.since or "—"
        tags = ", ".join(f"`{tag}`" for tag in feature.tags) if feature.tags else "—"
        body.append(f"| {feature.name} | {badge} | {since} | {tags} |")
    body.append("")

    body.append("## Details")
    body.append("")
    for feature in features:
        body.append(f"### {feature.name}")
        body.append("")
        body.append(feature.description.strip())
        body.append("")

    return _document("Feature Matrix", generated_at, body)


def render_changelog(releases: Sequence[Release], *, generated_at: str) -> str:
    """Render ``CHANGELOG.md`` from git-derived releases."""
    if releases:
        body: list[str] = []
        for release in releases:
            heading = f"## {release.version}"
            if release.date:
                heading += f" — {release.date}"
            body.append(heading)
            body.append("")
            if release.commits:
                body.extend(f"- {commit}" for commit in release.commits)
            else:
                body.append("_No commits in this release._")
            body.append("")
    else:
        body = ["_No releases or commits found._", ""]

    return _document("Changelog", generated_at, body)


def render_prompts(prompts: Sequence[Prompt], *, generated_at: str) -> str:
    """Render ``PROMPTS.md`` grouping prompts by category in stable order."""
    categories: dict[str, list[Prompt]] = {}
    for prompt in prompts:
        categories.setdefault(prompt.category, []).append(prompt)

    body: list[str] = []
    for category in sorted(categories):
        body.append(f"## {category}")
        body.append("")
        for prompt in categories[category]:
            body.append(f"### {prompt.title}")
            body.append("")
            body.append("```text")
            body.append(prompt.body.strip())
            body.append("```")
            body.append("")

    return _document("Claude Code Prompts", generated_at, body)
