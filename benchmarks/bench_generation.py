#!/usr/bin/env python3
"""Benchmark our API-doc generation against real tools (pdoc, sphinx-apidoc).

Everything measured here is *actually executed*: the three generators run on
the same ``src/living_docs`` tree. We report wall-clock time (``timeit``, 10
runs, median ± stdev), the number of output lines each tool produces, and the
docstring-coverage percentage of the source (computed by our own extractor).

Results are written to ``benchmarks/results.json`` and the comparison table
is embedded into ``docs/API.md`` by re-running the API generator.
"""

from __future__ import annotations

import json
import statistics
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_api_docs  # noqa: E402

from living_docs.build import resolve_timestamp, write_text  # noqa: E402
from living_docs.extractors import count_coverage, extract_directory  # noqa: E402
from living_docs.generators import render_api  # noqa: E402

SRC = REPO_ROOT / "src" / "living_docs"
SRC_ROOT = REPO_ROOT / "src"
RUNS = 10


def _measure(func: Callable[[], None], runs: int = RUNS) -> tuple[float, float]:
    """Return ``(median_ms, stdev_ms)`` of ``runs`` single executions of ``func``."""
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


def _run_living_docs() -> None:
    modules = extract_directory(SRC_ROOT)
    render_api(modules, generated_at="benchmark")


def _living_docs_lines() -> int:
    modules = extract_directory(SRC_ROOT)
    return len(render_api(modules, generated_at="benchmark").splitlines())


def _run_pdoc(out: Path) -> None:
    subprocess.run(
        [sys.executable, "-m", "pdoc", str(SRC), "-o", str(out)],
        check=True,
        capture_output=True,
    )


def _run_sphinx(out: Path) -> None:
    subprocess.run(
        ["sphinx-apidoc", "--force", "-o", str(out), str(SRC)],
        check=True,
        capture_output=True,
    )


def _bench_subprocess(
    runner: Callable[[Path], None], suffix: str
) -> tuple[float, float, int] | None:
    """Time ``runner`` over fresh temp dirs; return timing plus output lines.

    Returns ``None`` if the tool is unavailable or errors out.
    """
    try:
        with tempfile.TemporaryDirectory() as probe:
            runner(Path(probe))
            lines = _count_lines(Path(probe), suffix)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"  skipped ({exc})")
        return None

    def call() -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runner(Path(tmp))

    median, stdev = _measure(call)
    return median, stdev, lines


def main() -> int:
    print(f"Benchmarking on {SRC} ({RUNS} runs each)\n")
    tools: list[dict[str, object]] = []

    print("living-docs (AST -> Markdown):")
    ld_median, ld_stdev = _measure(_run_living_docs)
    ld_lines = _living_docs_lines()
    print(f"  median {ld_median:.2f} ms ± {ld_stdev:.2f}, {ld_lines} lines")
    tools.append(
        {
            "tool": "living-docs",
            "median_ms": round(ld_median, 3),
            "stdev_ms": round(ld_stdev, 3),
            "output_lines": ld_lines,
            "notes": "AST → single Markdown file",
        }
    )

    print("pdoc (HTML):")
    pdoc_result = _bench_subprocess(_run_pdoc, ".html")
    if pdoc_result is not None:
        median, stdev, lines = pdoc_result
        print(f"  median {median:.2f} ms ± {stdev:.2f}, {lines} lines")
        tools.append(
            {
                "tool": "pdoc",
                "median_ms": round(median, 3),
                "stdev_ms": round(stdev, 3),
                "output_lines": lines,
                "notes": "HTML site",
            }
        )

    print("sphinx-apidoc (reST stubs):")
    sphinx_result = _bench_subprocess(_run_sphinx, ".rst")
    if sphinx_result is not None:
        median, stdev, lines = sphinx_result
        print(f"  median {median:.2f} ms ± {stdev:.2f}, {lines} lines")
        tools.append(
            {
                "tool": "sphinx-apidoc",
                "median_ms": round(median, 3),
                "stdev_ms": round(stdev, 3),
                "output_lines": lines,
                "notes": "reST stub files",
            }
        )

    documented, total = count_coverage(extract_directory(SRC_ROOT))
    coverage_pct = round(documented / total * 100, 1) if total else 0.0

    results = {
        "generated_at": resolve_timestamp(),
        "source": "src/living_docs",
        "runs": RUNS,
        "doc_coverage_pct": coverage_pct,
        "tools": tools,
    }
    results_path = REPO_ROOT / "benchmarks" / "results.json"
    write_text(results_path, json.dumps(results, indent=2) + "\n")
    print(f"\nWrote {results_path.relative_to(REPO_ROOT)}")

    # Re-embed the fresh numbers into docs/API.md so drift checks stay green.
    docs = REPO_ROOT / "docs"
    for name, content in generate_api_docs.generate(resolve_timestamp()).items():
        write_text(docs / name, content)
    print("Re-rendered docs/API.md with benchmark table")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
