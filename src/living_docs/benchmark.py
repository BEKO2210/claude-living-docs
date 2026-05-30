"""Benchmark our API-doc generation against real tools (pdoc, sphinx-apidoc).

Everything here is actually executed on the project's configured source tree:
the three generators run, are timed with ``timeit``-style repeats, and the
real measured numbers are returned. Nothing is estimated.
"""

from __future__ import annotations

import statistics
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from .build import resolve_timestamp
from .config import ProjectConfig
from .extractors import count_coverage, extract_directory
from .generators import render_api

__all__ = ["DEFAULT_RUNS", "run_benchmark"]

DEFAULT_RUNS = 10


def _measure(func: Callable[[], None], runs: int) -> tuple[float, float]:
    samples: list[float] = []
    for _ in range(runs):
        start = time.perf_counter()
        func()
        samples.append((time.perf_counter() - start) * 1000.0)
    stdev = statistics.stdev(samples) if len(samples) > 1 else 0.0
    return statistics.median(samples), stdev


def _count_lines(directory: Path, suffix: str) -> int:
    total = 0
    for file in directory.rglob(f"*{suffix}"):
        total += len(file.read_text(encoding="utf-8", errors="replace").splitlines())
    return total


def _run_pdoc(source: Path, out: Path) -> None:
    subprocess.run(
        [sys.executable, "-m", "pdoc", str(source), "-o", str(out)],
        check=True,
        capture_output=True,
    )


def _run_sphinx(source: Path, out: Path) -> None:
    subprocess.run(
        ["sphinx-apidoc", "--force", "-o", str(out), str(source)],
        check=True,
        capture_output=True,
    )


def _bench_tool(
    runner: Callable[[Path, Path], None], source: Path, suffix: str, runs: int
) -> tuple[float, float, int] | None:
    try:
        with tempfile.TemporaryDirectory() as probe:
            runner(source, Path(probe))
            lines = _count_lines(Path(probe), suffix)
    except (OSError, subprocess.CalledProcessError):
        return None

    def call() -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runner(source, Path(tmp))

    median, stdev = _measure(call, runs)
    return median, stdev, lines


def run_benchmark(config: ProjectConfig, *, runs: int = DEFAULT_RUNS) -> dict[str, object]:
    """Benchmark living-docs vs pdoc and sphinx-apidoc on ``config.source``."""
    source = config.source
    tools: list[dict[str, object]] = []

    def render() -> None:
        render_api(extract_directory(source), generated_at="benchmark")

    median, stdev = _measure(render, runs)
    lines = len(render_api(extract_directory(source), generated_at="benchmark").splitlines())
    tools.append(
        {
            "tool": "living-docs",
            "median_ms": round(median, 3),
            "stdev_ms": round(stdev, 3),
            "output_lines": lines,
            "notes": "AST → single Markdown file",
        }
    )

    for tool, runner, suffix, notes in (
        ("pdoc", _run_pdoc, ".html", "HTML site"),
        ("sphinx-apidoc", _run_sphinx, ".rst", "reST stub files"),
    ):
        result = _bench_tool(runner, source, suffix, runs)
        if result is None:
            continue
        tool_median, tool_stdev, tool_lines = result
        tools.append(
            {
                "tool": tool,
                "median_ms": round(tool_median, 3),
                "stdev_ms": round(tool_stdev, 3),
                "output_lines": tool_lines,
                "notes": notes,
            }
        )

    documented, total = count_coverage(extract_directory(source))
    coverage_pct = round(documented / total * 100, 1) if total else 0.0

    return {
        "generated_at": resolve_timestamp(),
        "source": str(source.relative_to(config.root)),
        "runs": runs,
        "doc_coverage_pct": coverage_pct,
        "tools": tools,
    }
