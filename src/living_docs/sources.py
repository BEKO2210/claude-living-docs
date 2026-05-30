"""Load the inputs that feed the generators.

Everything here turns an external source — a JSON config file, the git history,
the benchmark results — into the typed dataclasses defined in
:mod:`living_docs.generators`. No Markdown is produced here.
"""

from __future__ import annotations

import json
from pathlib import Path

from .build import run_git
from .generators import BenchmarkRow, Feature, Prompt, Release

__all__ = [
    "AUTO_DOCS_MARKER",
    "collect_releases",
    "load_benchmarks",
    "load_features",
    "load_prompts",
]

# Auto-generated documentation commits carry this marker so the changelog can
# skip them and avoid churning every time the doc bot commits.
AUTO_DOCS_MARKER = "[auto-docs]"


def load_features(path: Path) -> list[Feature]:
    """Parse a ``features.json`` file into :class:`Feature` objects."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        Feature(
            name=entry["name"],
            status=entry["status"],
            description=entry["description"],
            since=entry.get("since"),
            tags=tuple(entry.get("tags", [])),
        )
        for entry in data["features"]
    ]


def load_prompts(path: Path) -> list[Prompt]:
    """Parse a ``prompts.json`` file into :class:`Prompt` objects."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        Prompt(title=entry["title"], category=entry["category"], body=entry["body"])
        for entry in data["prompts"]
    ]


def load_benchmarks(root: Path) -> list[BenchmarkRow]:
    """Read ``benchmarks/results.json`` if present, else return ``[]``."""
    results = root / "benchmarks" / "results.json"
    if not results.exists():
        return []
    data = json.loads(results.read_text(encoding="utf-8"))
    return [
        BenchmarkRow(
            tool=entry["tool"],
            median_ms=float(entry["median_ms"]),
            stdev_ms=float(entry["stdev_ms"]),
            output_lines=int(entry["output_lines"]),
            notes=entry.get("notes", ""),
        )
        for entry in data.get("tools", [])
    ]


def _commits(root: Path, rev_range: str) -> tuple[str, ...]:
    out = run_git(
        [
            "log",
            "--format=%s",
            "--no-merges",
            "-F",
            f"--grep={AUTO_DOCS_MARKER}",
            "--invert-grep",
            rev_range,
        ],
        cwd=root,
    )
    return tuple(line for line in out.splitlines() if line)


def _tag_date(root: Path, tag: str) -> str | None:
    return run_git(["log", "-1", "--format=%cs", tag], cwd=root) or None


def collect_releases(root: Path) -> list[Release]:
    """Build ordered releases from git tags and commits in ``root``.

    Tags become releases (newest first); commits after the newest tag land in
    an ``Unreleased`` section. With no tags, every commit is ``Unreleased``.
    """
    raw = run_git(["tag", "--sort=-creatordate"], cwd=root)
    tags = [line for line in raw.splitlines() if line]

    releases: list[Release] = []

    head_range = f"{tags[0]}..HEAD" if tags else "HEAD"
    unreleased = _commits(root, head_range)
    if unreleased:
        releases.append(Release(version="Unreleased", date=None, commits=unreleased))

    for index, tag in enumerate(tags):
        older = tags[index + 1] if index + 1 < len(tags) else None
        rev_range = f"{older}..{tag}" if older else tag
        releases.append(
            Release(version=tag, date=_tag_date(root, tag), commits=_commits(root, rev_range))
        )

    return releases
