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


def resolve_timestamp() -> str:
    """Resolve a deterministic ISO-8601 build timestamp.

    Resolution order:

    1. ``LIVING_DOCS_TIMESTAMP`` — explicit override (used by tests/CI).
    2. ``SOURCE_DATE_EPOCH`` — the reproducible-builds standard.
    3. The HEAD commit date — stable for a given checkout.
    4. A fixed Unix-epoch fallback.
    """
    override = os.environ.get("LIVING_DOCS_TIMESTAMP")
    if override:
        return override

    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch and epoch.isdigit():
        return datetime.fromtimestamp(int(epoch), tz=UTC).isoformat()

    # Scope to the inputs that actually affect generated docs. Doc-only
    # commits then leave the timestamp untouched, so `--check` stays green
    # after the generated docs are committed.
    scoped = run_git(
        ["log", "-1", "--format=%cI", "--", "src", "config", "pyproject.toml"]
    )
    if scoped:
        return scoped

    commit_date = run_git(["log", "-1", "--format=%cI"])
    if commit_date:
        return commit_date

    return _FALLBACK_TIMESTAMP


def write_text(path: Path, content: str) -> bool:
    """Write ``content`` to ``path`` only if it differs. Return ``True`` if changed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True
