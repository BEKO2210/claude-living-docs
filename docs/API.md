# API Reference

*🤖 AUTO-GENERATED on 2026-05-30T22:12:03+00:00 — do not edit manually*

## Overview

- Modules documented: **4**
- Callables: **15** (15 with docstrings, **100.0%** coverage)

## Benchmarks

Generation of the API docs for `src/` measured against real tools
(`timeit`, 10 runs, median ± stdev):

| Tool | Median (ms) | Stdev (ms) | Output lines | Notes |
| --- | ---: | ---: | ---: | --- |
| living-docs | 4.61 | 0.48 | 177 | AST → single Markdown file |
| pdoc | 397.04 | 15.50 | 111 | HTML site |
| sphinx-apidoc | 271.14 | 16.41 | 44 | reST stub files |

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

#### `def run_git(args: list[str], cwd: Path | None = None) -> str`

Run ``git <args>`` and return stripped stdout, or ``""`` on failure.

#### `def resolve_timestamp() -> str`

Resolve a deterministic ISO-8601 build timestamp.

Resolution order:

1. ``LIVING_DOCS_TIMESTAMP`` — explicit override (used by tests/CI).
2. ``SOURCE_DATE_EPOCH`` — the reproducible-builds standard.
3. The HEAD commit date — stable for a given checkout.
4. A fixed Unix-epoch fallback.

#### `def write_text(path: Path, content: str) -> bool`

Write ``content`` to ``path`` only if it differs. Return ``True`` if changed.

## Module `living_docs.extractors`

_Source: `living_docs/extractors.py`_

AST-based extraction of public API metadata from Python source files.

This module walks Python source using the standard library :mod:`ast` module
and produces immutable, fully typed data structures describing the modules,
classes and functions it finds. It performs **no** rendering and never
imports the analysed code, which keeps extraction fast and side-effect free.

The output is consumed by :mod:`living_docs.generators`.

### Functions

#### `def extract_source(source: str, module_name: str, path: str = '<string>', include_private: bool = False) -> ModuleDoc`

Parse ``source`` and return a :class:`ModuleDoc`.

Only top-level functions and classes are collected. Names starting with
an underscore are skipped unless ``include_private`` is true.

#### `def extract_module(file: Path, root: Path, include_private: bool = False) -> ModuleDoc`

Extract a single ``.py`` file, deriving its dotted name from ``root``.

#### `def extract_directory(root: Path, include_private: bool = False) -> tuple[ModuleDoc, ...]`

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

#### `def render_api(modules: Sequence[ModuleDoc], generated_at: str, benchmarks: Sequence[BenchmarkRow] = ()) -> str`

Render ``API.md`` from extracted modules and optional benchmark rows.

#### `def render_features(features: Sequence[Feature], generated_at: str) -> str`

Render ``FEATURES.md`` as a status table plus per-feature detail.

#### `def render_changelog(releases: Sequence[Release], generated_at: str) -> str`

Render ``CHANGELOG.md`` from git-derived releases.

#### `def render_prompts(prompts: Sequence[Prompt], generated_at: str) -> str`

Render ``PROMPTS.md`` grouping prompts by category in stable order.

### class `Feature`

A single entry from the feature matrix.

### class `Release`

A changelog release: a version, an optional date and its commits.

### class `Prompt`

A reusable Claude Code prompt grouped under a category.

### class `BenchmarkRow`

One row of the generator benchmark comparison table.
