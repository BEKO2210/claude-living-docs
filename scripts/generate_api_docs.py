#!/usr/bin/env python3
"""Generate ``docs/API.md`` from ``src/`` via AST extraction.

If ``benchmarks/results.json`` exists, its measured comparison numbers are
embedded as a table. The script never imports the analysed code.
"""

from __future__ import annotations

import json
from pathlib import Path

from living_docs.build import repo_root, resolve_timestamp, write_text
from living_docs.extractors import extract_directory
from living_docs.generators import BenchmarkRow, render_api

DOC_NAME = "API.md"


def _load_benchmarks(root: Path) -> list[BenchmarkRow]:
    results = root / "benchmarks" / "results.json"
    if not results.exists():
        return []
    data = json.loads(results.read_text(encoding="utf-8"))
    rows: list[BenchmarkRow] = []
    for entry in data.get("tools", []):
        rows.append(
            BenchmarkRow(
                tool=entry["tool"],
                median_ms=float(entry["median_ms"]),
                stdev_ms=float(entry["stdev_ms"]),
                output_lines=int(entry["output_lines"]),
                notes=entry.get("notes", ""),
            )
        )
    return rows


def generate(generated_at: str) -> dict[str, str]:
    """Return ``{"API.md": markdown}`` for the current ``src/`` tree."""
    root = repo_root()
    modules = extract_directory(root / "src")
    benchmarks = _load_benchmarks(root)
    content = render_api(modules, generated_at=generated_at, benchmarks=benchmarks)
    return {DOC_NAME: content}


def main() -> int:
    generated_at = resolve_timestamp()
    docs = repo_root() / "docs"
    for name, content in generate(generated_at).items():
        action = "wrote" if write_text(docs / name, content) else "unchanged"
        print(f"{action} docs/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
