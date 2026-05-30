# API Reference

*🤖 AUTO-GENERATED on 2026-05-30T22:32:28+00:00 — do not edit manually*

## Overview

- Modules documented: **9**
- Callables: **25** (25 with docstrings, **100.0%** coverage)

## Benchmarks

Generation of the API docs for `src/` measured against real tools
(`timeit`, 10 runs, median ± stdev):

| Tool | Median (ms) | Stdev (ms) | Output lines | Notes |
| --- | ---: | ---: | ---: | --- |
| living-docs | 9.12 | 1.09 | 292 | AST → single Markdown file |
| pdoc | 402.78 | 22.89 | 531 | HTML site |
| sphinx-apidoc | 238.78 | 6.84 | 84 | reST stub files |

## Module `living_docs`

_Source: `living_docs/__init__.py`_

Living Docs Engine — generate documentation directly from source code.

The package is split into three cooperating layers:

* :mod:`living_docs.extractors` turns Python source into immutable, typed
  data structures (pure parsing, no rendering).
* :mod:`living_docs.generators` turns those data structures — plus feature,
  changelog and prompt data — into Markdown (pure rendering, no I/O).
* :mod:`living_docs.build` holds shared build utilities (deterministic
  timestamps, idempotent file writing, repository discovery).

Keeping extraction, rendering and I/O separate is what makes every generator
idempotent and therefore safe to run inside CI drift checks.

## Module `living_docs.benchmark`

_Source: `living_docs/benchmark.py`_

Benchmark our API-doc generation against real tools (pdoc, sphinx-apidoc).

Everything here is actually executed on the project's configured source tree:
the three generators run, are timed with ``timeit``-style repeats, and the
real measured numbers are returned. Nothing is estimated.

### Functions

#### `def run_benchmark(config: ProjectConfig, *, runs: int = DEFAULT_RUNS) -> dict[str, object]`

Benchmark living-docs vs pdoc and sphinx-apidoc on ``config.source``.

## Module `living_docs.build`

_Source: `living_docs/build.py`_

Shared build helpers: deterministic timestamps and idempotent writes.

The single most important property of this project is that running a
generator twice produces byte-identical output. The only naturally
non-deterministic input is the AUTO-GENERATED timestamp, so it is resolved
here from a stable source (an explicit override, ``SOURCE_DATE_EPOCH`` or the
HEAD commit date) rather than from the wall clock.

### Functions

#### `def repo_root() -> Path`

Return the repository root (the package lives at ``<root>/src``).

#### `def run_git(args: list[str], *, cwd: Path | None = None) -> str`

Run ``git <args>`` and return stripped stdout, or ``""`` on failure.

#### `def resolve_timestamp(root: Path | None = None) -> str`

Resolve a deterministic ISO-8601 build timestamp for ``root``.

Resolution order:

1. ``LIVING_DOCS_TIMESTAMP`` — explicit override (used by tests/CI).
2. ``SOURCE_DATE_EPOCH`` — the reproducible-builds standard.
3. The date of the last commit touching the doc inputs — stable, and
   unchanged by doc-only commits, so ``--check`` stays green afterwards.
4. The HEAD commit date.
5. A fixed Unix-epoch fallback.

#### `def write_text(path: Path, content: str) -> bool`

Write ``content`` to ``path`` only if it differs. Return ``True`` if changed.

## Module `living_docs.cli`

_Source: `living_docs/cli.py`_

The ``living-docs`` command-line interface.

One command for the whole workflow on **any** Python project::

    living-docs init      # scaffold optional config (features/prompts)
    living-docs update    # (re)generate docs/
    living-docs check     # drift detection (exit 1 if stale)
    living-docs bench      # benchmark vs pdoc & sphinx-apidoc

Every command accepts ``-C/--path PROJECT`` to target a directory other than
the current one. With no config at all it documents ``src/`` into ``docs/``.

### Functions

#### `def main(argv: list[str] | None = None) -> int`

Entry point for the ``living-docs`` console script.

## Module `living_docs.config`

_Source: `living_docs/config.py`_

Project configuration for the Living Docs engine.

A project is configured either with **zero config** (the defaults below) or
through a ``[tool.living_docs]`` table in its ``pyproject.toml``. This is what
lets the same engine document *any* Python project, not just this repository.

### Functions

#### `def load_config(root: Path, *, overrides: dict[str, object] | None = None) -> ProjectConfig`

Build a :class:`ProjectConfig` for ``root`` from defaults + pyproject.

### class `ProjectConfig`

Resolved, absolute paths and flags for one project.

## Module `living_docs.engine`

_Source: `living_docs/engine.py`_

Turn a :class:`ProjectConfig` into a set of generated documents.

This is the single place that decides *which* documents a project gets and
wires the sources to the renderers. Both the CLI and the thin ``scripts/``
wrappers call into here, so behaviour can never diverge between them.

### Functions

#### `def build_documents(config: ProjectConfig, generated_at: str) -> dict[str, str]`

Render every enabled document, returned as ``{filename: markdown}``.

#### `def write_documents(config: ProjectConfig, documents: dict[str, str]) -> list[str]`

Write ``documents`` into ``config.docs``; return the changed filenames.

#### `def check_documents(config: ProjectConfig, documents: dict[str, str]) -> list[str]`

Return the filenames whose committed content differs from ``documents``.

## Module `living_docs.extractors`

_Source: `living_docs/extractors.py`_

AST-based extraction of public API metadata from Python source files.

This module walks Python source using the standard library :mod:`ast` module
and produces immutable, fully typed data structures describing the modules,
classes and functions it finds. It performs **no** rendering and never
imports the analysed code, which keeps extraction fast and side-effect free.

The output is consumed by :mod:`living_docs.generators`.

### Functions

#### `def extract_source(source: str, *, module_name: str, path: str = '<string>', include_private: bool = False) -> ModuleDoc`

Parse ``source`` and return a :class:`ModuleDoc`.

Only top-level functions and classes are collected. Names starting with
an underscore are skipped unless ``include_private`` is true.

#### `def extract_module(file: Path, root: Path, *, include_private: bool = False) -> ModuleDoc`

Extract a single ``.py`` file, deriving its dotted name from ``root``.

#### `def extract_directory(root: Path, *, include_private: bool = False) -> tuple[ModuleDoc, ...]`

Recursively extract every ``.py`` file under ``root``, sorted by name.

Private modules (``_name.py``) are skipped unless ``include_private`` is
set; ``__init__.py`` is always included so package docstrings survive.

#### `def iter_functions(modules: tuple[ModuleDoc, ...]) -> list[FunctionDoc]`

Yield every function and method across ``modules`` as a flat list.

#### `def count_coverage(modules: tuple[ModuleDoc, ...]) -> tuple[int, int]`

Return ``(documented, total)`` callables across ``modules``.

### class `Parameter`

A single callable parameter.

``name`` keeps any ``*`` / ``**`` prefix for var-positional and
var-keyword parameters so it can be rendered verbatim.

### class `FunctionDoc`

A module-level function or a method extracted from the AST.

#### `def signature(self) -> str`

- decorator: `@property`

Return a rendered ``(...) -> ret`` signature string.

### class `ClassDoc`

A class definition with its public methods.

### class `ModuleDoc`

A whole module: its docstring plus public functions and classes.

## Module `living_docs.generators`

_Source: `living_docs/generators.py`_

Pure Markdown renderers.

Every function here takes already-extracted data and returns a Markdown
string. There is no file I/O and no clock access (timestamps are passed in),
which is what makes the generators deterministic and idempotent.

### Functions

#### `def auto_generated_header(generated_at: str) -> str`

Return the mandated AUTO-GENERATED banner line for ``generated_at``.

#### `def render_api(modules: Sequence[ModuleDoc], *, generated_at: str, benchmarks: Sequence[BenchmarkRow] = ()) -> str`

Render ``API.md`` from extracted modules and optional benchmark rows.

#### `def render_features(features: Sequence[Feature], *, generated_at: str) -> str`

Render ``FEATURES.md`` as a status table plus per-feature detail.

#### `def render_changelog(releases: Sequence[Release], *, generated_at: str) -> str`

Render ``CHANGELOG.md`` from git-derived releases.

#### `def render_prompts(prompts: Sequence[Prompt], *, generated_at: str) -> str`

Render ``PROMPTS.md`` grouping prompts by category in stable order.

### class `Feature`

A single entry from the feature matrix.

### class `Release`

A changelog release: a version, an optional date and its commits.

### class `Prompt`

A reusable Claude Code prompt grouped under a category.

### class `BenchmarkRow`

One row of the generator benchmark comparison table.

## Module `living_docs.sources`

_Source: `living_docs/sources.py`_

Load the inputs that feed the generators.

Everything here turns an external source — a JSON config file, the git history,
the benchmark results — into the typed dataclasses defined in
:mod:`living_docs.generators`. No Markdown is produced here.

### Functions

#### `def load_features(path: Path) -> list[Feature]`

Parse a ``features.json`` file into :class:`Feature` objects.

#### `def load_prompts(path: Path) -> list[Prompt]`

Parse a ``prompts.json`` file into :class:`Prompt` objects.

#### `def load_benchmarks(root: Path) -> list[BenchmarkRow]`

Read ``benchmarks/results.json`` if present, else return ``[]``.

#### `def collect_releases(root: Path) -> list[Release]`

Build ordered releases from git tags and commits in ``root``.

Tags become releases (newest first); commits after the newest tag land in
an ``Unreleased`` section. With no tags, every commit is ``Unreleased``.
