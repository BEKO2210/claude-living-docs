# Feature Matrix

*🤖 AUTO-GENERATED on 2026-05-30T22:32:28+00:00 — do not edit manually*

| Feature | Status | Since | Tags |
| --- | --- | --- | --- |
| AST API Extraction | ✅ stable | 0.1.0 | `core`, `extraction` |
| Drift Detection | ✅ stable | 0.1.0 | `ci`, `safety` |
| Benchmark Harness | 🧪 beta | 0.1.0 | `benchmark`, `tooling` |

## Details

### AST API Extraction

Parses Python source with the stdlib ast module and extracts modules, classes, functions, parameters, type hints and decorators without importing the code.

### Drift Detection

The --check mode regenerates every document into a temporary directory and diffs it against docs/, exiting non-zero when committed docs are stale.

### Benchmark Harness

Measures generation wall-clock time, output size and docstring coverage against pdoc and sphinx-apidoc, writing real measured numbers to benchmarks/results.json.
