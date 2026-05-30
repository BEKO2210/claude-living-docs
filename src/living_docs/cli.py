"""The ``living-docs`` command-line interface.

One command for the whole workflow on **any** Python project::

    living-docs init      # scaffold optional config (features/prompts)
    living-docs update    # (re)generate docs/
    living-docs check     # drift detection (exit 1 if stale)
    living-docs bench      # benchmark vs pdoc & sphinx-apidoc

Every command accepts ``-C/--path PROJECT`` to target a directory other than
the current one. With no config at all it documents ``src/`` into ``docs/``.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

from .build import resolve_timestamp, write_text
from .config import load_config
from .engine import build_documents, check_documents, write_documents

__all__ = ["main"]

_FEATURES_TEMPLATE = {
    "features": [
        {
            "name": "Example Feature",
            "status": "stable",
            "since": "0.1.0",
            "description": "Describe a capability. This file is the source for FEATURES.md.",
            "tags": ["core"],
        }
    ]
}

_PROMPTS_TEMPLATE = {
    "prompts": [
        {
            "title": "Regenerate documentation",
            "category": "Maintenance",
            "body": "Run `living-docs update` and show me the git diff for docs/.",
        }
    ]
}


def _cmd_init(args: argparse.Namespace) -> int:
    root = args.path.resolve()
    config = load_config(root)
    created: list[str] = []

    targets = [
        (root / "config" / "features.json", _FEATURES_TEMPLATE),
        (root / "config" / "prompts.json", _PROMPTS_TEMPLATE),
    ]
    for path, template in targets:
        if path.exists():
            print(f"exists   {path.relative_to(root)}")
            continue
        write_text(path, json.dumps(template, indent=2) + "\n")
        created.append(str(path.relative_to(root)))
        print(f"created  {path.relative_to(root)}")

    print()
    print(f"Source : {_show(root, config.source)}  (override with [tool.living_docs] source=...)")
    print(f"Docs   : {_show(root, config.docs)}")
    if not config.source.exists():
        print("\nNote: no source directory yet — create it, then run `living-docs update`.")
    else:
        print("\nNext:  living-docs update")
    return 0


def _cmd_update(args: argparse.Namespace) -> int:
    config = load_config(args.path.resolve())
    documents = build_documents(config, resolve_timestamp(config.root))
    changed = write_documents(config, documents)
    for name in documents:
        flag = "wrote" if name in changed else "unchanged"
        print(f"{flag:9} {_show(config.root, config.docs / name)}")
    print(f"\n{len(changed)} updated, {len(documents) - len(changed)} unchanged.")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    config = load_config(args.path.resolve())
    documents = build_documents(config, resolve_timestamp(config.root))
    drifted = check_documents(config, documents)
    if not drifted:
        print(f"OK: {len(documents)} document(s) up to date.")
        return 0
    for name in drifted:
        target = config.docs / name
        actual = target.read_text(encoding="utf-8") if target.exists() else ""
        sys.stdout.writelines(
            difflib.unified_diff(
                actual.splitlines(keepends=True),
                documents[name].splitlines(keepends=True),
                fromfile=f"{name} (on disk)",
                tofile=f"{name} (generated)",
            )
        )
    print(f"\nDRIFT: {len(drifted)} document(s) out of date: {', '.join(drifted)}")
    print("Run `living-docs update` and commit the result.")
    return 1


def _cmd_bench(args: argparse.Namespace) -> int:
    # Imported lazily: the benchmark pulls in pdoc/sphinx, which the common
    # commands above do not need.
    from .benchmark import run_benchmark

    config = load_config(args.path.resolve())
    if not config.source.exists():
        print(f"No source directory at {config.source}", file=sys.stderr)
        return 1

    print(f"Benchmarking {_show(config.root, config.source)} ({args.runs} runs each)...\n")
    results = run_benchmark(config, runs=args.runs)
    results_path = config.root / "benchmarks" / "results.json"
    write_text(results_path, json.dumps(results, indent=2) + "\n")

    tools = results["tools"]
    assert isinstance(tools, list)
    for row in tools:
        print(
            f"  {row['tool']:<14} {row['median_ms']:>9.2f} ms ± {row['stdev_ms']:.2f}"
            f"   {row['output_lines']} lines"
        )

    # Re-embed the fresh numbers so docs/API.md stays in sync.
    documents = build_documents(config, resolve_timestamp(config.root))
    write_documents(config, documents)
    print(f"\nWrote {_show(config.root, results_path)} and refreshed docs/API.md")
    return 0


def _show(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="living-docs", description=__doc__)
    parser.add_argument(
        "-C",
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Project directory to operate on (default: current directory).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Scaffold optional config files.").set_defaults(func=_cmd_init)
    sub.add_parser("update", help="(Re)generate docs/.").set_defaults(func=_cmd_update)
    sub.add_parser("check", help="Fail if committed docs are stale.").set_defaults(func=_cmd_check)
    bench = sub.add_parser("bench", help="Benchmark vs pdoc & sphinx-apidoc.")
    bench.add_argument("--runs", type=int, default=10, help="Timing repeats (default: 10).")
    bench.set_defaults(func=_cmd_bench)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``living-docs`` console script."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
