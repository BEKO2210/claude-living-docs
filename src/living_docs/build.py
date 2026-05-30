"""Shared build helpers: deterministic timestamps and idempotent writes.

The single most important property of this project is that running a
generator twice produces byte-identical output. The only naturally
non-deterministic input is the AUTO-GENERATED timestamp, so it is resolved
here from a stable source (an explicit override, ``SOURCE_DATE_EPOCH`` or the
HEAD commit date) rather than from the wall clock.
"""

from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

__all__ = [
    "repo_root",
    "resolve_timestamp",
    "run_git",
    "write_text",
]

_FALLBACK_TIMESTAMP = "1970-01-01T00:00:00+00:00"


def repo_root() -> Path:
    """Return the repository root (the package lives at ``<root>/src``)."""
    return Path(__file__).resolve().parents[2]


def run_git(args: list[str], *, cwd: Path | None = None) -> str:
    """Run ``git <args>`` and return stripped stdout, or ``""`` on failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd or repo_root(),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip()


def resolve_timestamp(root: Path | None = None) -> str:
    """Resolve a deterministic ISO-8601 build timestamp for ``root``.

    Resolution order:

    1. ``LIVING_DOCS_TIMESTAMP`` — explicit override (used by tests/CI).
    2. ``SOURCE_DATE_EPOCH`` — the reproducible-builds standard.
    3. The date of the last commit touching the doc inputs — stable, and
       unchanged by doc-only commits, so ``--check`` stays green afterwards.
    4. The HEAD commit date.
    5. A fixed Unix-epoch fallback.
    """
    override = os.environ.get("LIVING_DOCS_TIMESTAMP")
    if override:
        return override

    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch and epoch.isdigit():
        return datetime.fromtimestamp(int(epoch), tz=UTC).isoformat()

    scoped = run_git(
        ["log", "-1", "--format=%cI", "--", "src", "config", "pyproject.toml"],
        cwd=root,
    )
    if scoped:
        return _normalize(scoped)

    commit_date = run_git(["log", "-1", "--format=%cI"], cwd=root)
    if commit_date:
        return _normalize(commit_date)

    return _FALLBACK_TIMESTAMP


def _normalize(timestamp: str) -> str:
    """Canonicalise an ISO-8601 string so it is environment-independent.

    Different git versions render a UTC commit date as either ``...+00:00`` or
    ``...Z``. Both denote the same instant, but a raw string compare would make
    the drift check flap between machines, so we parse and re-emit one form.
    """
    try:
        return datetime.fromisoformat(timestamp).isoformat()
    except ValueError:
        return timestamp


def write_text(path: Path, content: str) -> bool:
    """Write ``content`` to ``path`` only if it differs. Return ``True`` if changed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True
