# Claude Code Prompts

*🤖 AUTO-GENERATED on 2026-05-30T22:12:03+00:00 — do not edit manually*

## CI

### Investigate a drift-check failure

```text
`python scripts/update_all.py --check` failed in CI. Diff the committed docs/ against freshly generated output, identify which source change was not reflected, and tell me whether the fix is to regenerate or to revert.
```

## Extension

### Add a new generator

```text
Create scripts/generate_<name>.py following the existing generators: a `generate(generated_at)` function returning {filename: markdown}, an AUTO-GENERATED header, idempotent output. Register it in scripts/update_all.py and add a test in tests/.
```

## Maintenance

### Regenerate all documentation

```text
Run `python scripts/update_all.py`, then show me the git diff for docs/ and explain in one sentence per file what changed and why.
```

### Refresh the benchmark numbers

```text
Run `python benchmarks/bench_generation.py`, commit the updated benchmarks/results.json and docs/API.md, and summarise how our generation time compares to pdoc and sphinx-apidoc.
```
