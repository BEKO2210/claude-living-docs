# claude-living-docs

[![Auto Update Docs](https://github.com/beko2210/claude-living-docs/actions/workflows/auto_update_docs.yml/badge.svg)](https://github.com/beko2210/claude-living-docs/actions/workflows/auto_update_docs.yml)
![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Checked with mypy](https://img.shields.io/badge/mypy-strict-blue)
![Lint: ruff](https://img.shields.io/badge/lint-ruff-orange)

**Self-updating documentation.** The docs are never hand-written — they are
**generated from the code, config and git history** on every run. The source
of truth is the code; everything in [`docs/`](docs/) is a build artifact and is
regenerated each time.

```
code + config + git  ──▶  extractors (AST)  ──▶  generators (Markdown)  ──▶  docs/
```

## 60-second quickstart

```bash
git clone https://github.com/beko2210/claude-living-docs
cd claude-living-docs

python -m pip install -e ".[dev]"   # ruff, mypy, pytest, pdoc, sphinx

python scripts/update_all.py        # (re)generate docs/
python scripts/update_all.py --check  # drift detection (exit 1 if stale)

ruff check . && mypy --strict src/  # lint + types
pytest --cov=src                    # tests + coverage
python benchmarks/bench_generation.py  # benchmark vs pdoc & sphinx
```

## What gets generated

| Document | Source of truth | Generator |
| --- | --- | --- |
| [`docs/API.md`](docs/API.md) | `src/` (AST, no imports) | `scripts/generate_api_docs.py` |
| [`docs/FEATURES.md`](docs/FEATURES.md) | `config/features.json` | `scripts/generate_features.py` |
| [`docs/CHANGELOG.md`](docs/CHANGELOG.md) | git tags + commits | `scripts/generate_changelog.py` |
| [`docs/PROMPTS.md`](docs/PROMPTS.md) | `config/prompts.json` | `scripts/generate_prompts.py` |

Every generator writes an `AUTO-GENERATED` header, is fully typed
(`mypy --strict`), and is **idempotent**: running it twice produces
byte-identical output. The timestamp is resolved deterministically (from
`LIVING_DOCS_TIMESTAMP`, `SOURCE_DATE_EPOCH` or the last source commit), so
the CI drift check stays meaningful.

## Benchmarks

Generating the API docs for `src/living_docs` against real tools
(`timeit`, 10 runs, median ± stdev — numbers from
[`benchmarks/results.json`](benchmarks/results.json)):

| Tool | Median (ms) | Output lines | What it produces |
| --- | ---: | ---: | --- |
| **living-docs** | **4.63** | 177 | single Markdown file |
| pdoc | 395.19 | 111 | HTML site |
| sphinx-apidoc | 244.40 | 44 | reST stub files |

Docstring coverage of `src/`: **100%**. Numbers are measured on the machine
that last ran the harness — re-run `python benchmarks/bench_generation.py` to
refresh them.

## Use this as a template

Click **“Use this template”** on GitHub (or copy the repo). Then:

1. Replace the code in `src/` with your own package.
2. Edit `config/features.json` and `config/prompts.json`.
3. Run `python scripts/update_all.py` and commit.

The [`.github/workflows/auto_update_docs.yml`](.github/workflows/auto_update_docs.yml)
workflow regenerates the docs on every push to `main` (and daily), then a doc
bot commits any changes for you.

## Project layout

```
src/living_docs/   extractors.py (AST) · generators.py (Markdown) · build.py
scripts/           generate_*.py · update_all.py (orchestrator + --check)
config/            features.json · prompts.json
benchmarks/        bench_generation.py · results.json
tests/             test_extractors · test_generators · test_idempotency
docs/              AUTO-GENERATED — do not edit
```

See [`CLAUDE.md`](CLAUDE.md) for the full architecture and conventions.
