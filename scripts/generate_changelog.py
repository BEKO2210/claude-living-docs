#!/usr/bin/env python3
"""Generate ``docs/CHANGELOG.md`` from real git tags and commit history.

Tags are treated as releases (newest first); commits made after the latest
tag are grouped under an ``Unreleased`` section. With no tags, every commit
is listed under ``Unreleased``. Output depends only on repository state, so
it is stable across runs at a fixed ``HEAD``.
"""

from __future__ import annotations

from living_docs.build import repo_root, resolve_timestamp, run_git, write_text
from living_docs.generators import Release, render_changelog

DOC_NAME = "CHANGELOG.md"


# Marker placed in auto-generated documentation commits. They are excluded
# from the changelog so the changelog does not churn every time the doc bot
# commits regenerated files.
AUTO_DOCS_MARKER = "[auto-docs]"


def _commits(rev_range: str) -> tuple[str, ...]:
    out = run_git(
        [
            "log",
            "--format=%s",
            "--no-merges",
            "-F",
            f"--grep={AUTO_DOCS_MARKER}",
            "--invert-grep",
            rev_range,
        ]
    )
    return tuple(line for line in out.splitlines() if line)


def _tag_date(tag: str) -> str | None:
    date = run_git(["log", "-1", "--format=%cs", tag])
    return date or None


def collect_releases() -> list[Release]:
    """Build the ordered list of releases from tags and commits."""
    raw = run_git(["tag", "--sort=-creatordate"])
    tags = [line for line in raw.splitlines() if line]

    releases: list[Release] = []

    head_range = f"{tags[0]}..HEAD" if tags else "HEAD"
    unreleased = _commits(head_range)
    if unreleased:
        releases.append(Release(version="Unreleased", date=None, commits=unreleased))

    for index, tag in enumerate(tags):
        older = tags[index + 1] if index + 1 < len(tags) else None
        rev_range = f"{older}..{tag}" if older else tag
        releases.append(
            Release(version=tag, date=_tag_date(tag), commits=_commits(rev_range))
        )

    return releases


def generate(generated_at: str) -> dict[str, str]:
    """Return ``{"CHANGELOG.md": markdown}`` derived from git history."""
    releases = collect_releases()
    return {DOC_NAME: render_changelog(releases, generated_at=generated_at)}


def main() -> int:
    generated_at = resolve_timestamp()
    docs = repo_root() / "docs"
    for name, content in generate(generated_at).items():
        action = "wrote" if write_text(docs / name, content) else "unchanged"
        print(f"{action} docs/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
