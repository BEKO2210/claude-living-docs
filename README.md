# claude-living-docs

[![Auto Update Docs](https://github.com/beko2210/claude-living-docs/actions/workflows/auto_update_docs.yml/badge.svg)](https://github.com/beko2210/claude-living-docs/actions/workflows/auto_update_docs.yml)
![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Checked with mypy](https://img.shields.io/badge/mypy-strict-blue)
![Lint: ruff](https://img.shields.io/badge/lint-ruff-orange)

**Your Markdown docs never rot — because here, "the docs are wrong" is a CI
failure, not a silent problem.** API reference, changelog and feature matrix are
generated from the code, config and git history, so they can't drift out of
sync. The killer feature is the **drift check** (`living-docs check` → exit 1
when the committed docs no longer match the sources), *not* raw speed.

```
code + config + git  ──▶  extractors (AST)  ──▶  generators (Markdown)  ──▶  docs/
```

## 60-second quickstart

Click **“Use this template”** on GitHub (or clone the repo), then:

```bash
git clone https://github.com/beko2210/claude-living-docs
cd claude-living-docs
pip install -e .          # registers the `living-docs` CLI

living-docs update        # (re)generate docs/  (zero-config: src/ → docs/)
living-docs check         # drift detection — exit 1 if docs are stale
```

That's the whole onboarding: **one install, one command per project.** Point it
at any other project with `living-docs -C ../other update`. Other commands:
`living-docs init` (scaffold optional config), `living-docs bench`.

It works out of the box on a `src/` layout. For anything else, add a few lines
to your `pyproject.toml`:

```toml
[tool.living_docs]
source = "."              # or "src", "mypackage", an absolute path…
docs = "docs"
features = "config/features.json"   # optional
prompts = "config/prompts.json"     # optional
changelog = true
include_private = false
```

## When it's worth it — and when it isn't

Be realistic before adopting this. It is not free: you carry a code generator
(~1180 lines of Python + tests) so that documentation maintenance drops to zero.

**✅ Worth it when:**

- You ship a **library or public API** where reference docs *must* stay correct.
- You have **multiple repos** — the CLI is reusable, so the per-project cost
  trends to zero (`pip install`, one command, done).
- You work in a **team with many contributors** and docs rot between PRs.
- You want **Markdown that's guaranteed current** as LLM / `CLAUDE.md` context
  or as a GitHub README — not a stale `.md` nobody updates.

**❌ Overkill when:**

- It's a **one-off / throwaway script** — the generator is bigger than the docs
  it produces, so the ROI is negative (see [ROI](#roi-be-honest) below).
- You need a **real documentation *website*** with search, cross-links and
  rendered source. Use [pdoc](https://pdoc.dev) or
  [Sphinx](https://www.sphinx-doc.org) for that — this tool deliberately emits a
  single Markdown file, not a site.

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
`LIVING_DOCS_TIMESTAMP`, `SOURCE_DATE_EPOCH` or the last source commit, in a
git-version-independent form), so the CI drift check never flaps.

### Scope: reference docs only

This generates **reference documentation only** — signatures, type hints,
docstrings, changelog, feature table. It does **not** write tutorials,
conceptual guides or any prose. Those still belong to a human.

## Benchmarks

Generating the API docs for `src/` against real tools (`timeit`, 10 runs,
median ± stdev — numbers from [`benchmarks/results.json`](benchmarks/results.json)):

| Tool | Median (ms) | Output lines | What it produces |
| --- | ---: | ---: | --- |
| **living-docs** | **9.12** | 292 | single Markdown file |
| pdoc | 402.78 | 531 | HTML site |
| sphinx-apidoc | 238.78 | 84 | reST stub files |

**Read this honestly: it's an apples-to-oranges comparison.** pdoc and Sphinx
build a whole HTML site with search and cross-links; living-docs builds *one*
Markdown file. "Faster" is true but not the point — pick the tool that matches
the output you actually want. Likewise the docstring coverage figure (100% for
`src/`) is **garbage in, garbage out**: it only measures what's already in the
code. Thin docstrings → thin docs (pluggy, for example, comes out at ~52%).

## ROI (be honest)

For *this* repo the generator is ~1180 lines of code producing ~370 lines of
docs — a **negative ROI if you only ever document one small project**. The
payoff comes from two things the numbers don't show:

1. **Reuse** — the same CLI documents every repo you own at near-zero marginal
   cost.
2. **Enforced correctness** — the drift check turns "the docs are probably
   stale" into a failing CI job. That guarantee is the actual product; the
   generated Markdown is just the by-product.

## Developer commands

```bash
pip install -e ".[dev]"             # + ruff, mypy, pytest, pdoc, sphinx
ruff check . && mypy --strict src/
pytest --cov=src
python scripts/update_all.py        # legacy wrapper — same engine as the CLI
```

The [`.github/workflows/auto_update_docs.yml`](.github/workflows/auto_update_docs.yml)
workflow regenerates the docs on every push to `main` (and daily), then a doc
bot commits any changes for you.

## Project layout

```
src/living_docs/   cli.py (living-docs command) · config.py · engine.py
                   extractors.py (AST) · generators.py (Markdown)
                   sources.py (JSON + git) · benchmark.py · build.py
scripts/           thin generate_*.py + update_all.py wrappers (same engine)
config/            features.json · prompts.json
benchmarks/        bench_generation.py · results.json
tests/             test_extractors · test_generators · test_idempotency
                   test_config · test_sources · test_cli (real end-to-end)
docs/              AUTO-GENERATED — do not edit
```

See [`CLAUDE.md`](CLAUDE.md) for the full architecture and conventions.
