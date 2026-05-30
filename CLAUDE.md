# CLAUDE.md — Living Docs Engine

> **Projektkontext für Claude Code.** Diese Datei wird automatisch eingelesen.
> Halte dich strikt an die hier definierte Architektur und die Konventionen.

## 🎯 Was dieses Projekt ist

Ein **Self-Updating Documentation System**. Die Kernidee:
Dokumentation wird NIE manuell geschrieben, sondern aus dem Code,
Config-Dateien und Git-Historie **automatisch generiert**.

Quelle der Wahrheit = der Code. Die `.md`-Dateien in `docs/` sind
reine Build-Artefakte und werden bei jedem Lauf neu erzeugt.

## 🚫 Eiserne Regeln

1. **NIEMALS** Dateien in `docs/` manuell editieren — sie werden überschrieben.
2. Jeder Generator schreibt einen Header mit Timestamp + "AUTO-GENERATED".
3. Jeder Generator ist idempotent (zweimal laufen = identisches Ergebnis).
4. Alles muss unter Pop!_OS / Linux laufen (Python 3.11+, bash).
5. Vollständiger Code, keine Platzhalter, keine `TODO`-Stubs in der finalen Version.
6. Jeder Generator hat einen zugehörigen Test in `tests/`.

## 📁 Soll-Strukturclaude-living-docs/
├── CLAUDE.md                  # diese Datei
├── README.md                  # semi-auto (Badges + Quickstart)
├── pyproject.toml             # Dependencies + Tooling-Config
├── config/
│   └── features.json          # Feature-Matrix (Single Source)
├── src/
│   └── living_docs/
│       ├── init.py
│       ├── extractors.py      # AST-Parsing, Docstring-Extraktion
│       └── generators.py      # Markdown-Renderer
├── scripts/
│   ├── generate_api_docs.py   # API.md aus src/ (AST)
│   ├── generate_features.py   # FEATURES.md aus features.json
│   ├── generate_changelog.py  # CHANGELOG.md aus Git-Tags/Commits
│   ├── generate_prompts.py    # PROMPTS.md (Claude-Code-Prompts)
│   └── update_all.py          # orchestriert alle Generatoren
├── docs/                      # AUTO-GENERATED (nicht editieren!)
│   ├── API.md
│   ├── FEATURES.md
│   ├── CHANGELOG.md
│   └── PROMPTS.md
├── benchmarks/
│   ├── bench_generation.py    # Speed-Bench vs. pdoc & Sphinx
│   └── results.json           # Benchmark-Ergebnisse (auto)
├── tests/
│   ├── test_extractors.py
│   ├── test_generators.py
│   └── test_idempotency.py
└── .github/workflows/
└── auto_update_docs.yml   # CI: Generatoren + Tests + Auto-Commit## 🛠️ Befehle

| Zweck | Befehl (CLI, empfohlen) | Befehl (Scripts, legacy) |
|---|---|---|
| Alle Docs neu generieren | `living-docs update` | `python scripts/update_all.py` |
| Einzelnen Generator | — | `python scripts/generate_api_docs.py` |
| Config scaffolden | `living-docs init` | — |
| Tests | `pytest -v` | |
| Benchmarks | `living-docs bench` | `python benchmarks/bench_generation.py` |
| Drift-Check (CI) | `living-docs check` | `python scripts/update_all.py --check` |
| Anderes Projekt | `living-docs -C <pfad> update` | — |

> Das `living-docs`-CLI ist config-getrieben (`[tool.living_docs]` in
> `pyproject.toml`, sonst Zero-Config `src/` → `docs/`) und läuft auf **jedem**
> Python-Projekt. Die `scripts/` sind dünne Wrapper auf dieselbe Engine.

## 🧪 Benchmark-Anforderung

Die Generatoren müssen gegen **reale, existierende Tools** gemessen werden:
- **pdoc** (`pip install pdoc`) — Python-API-Doc-Generator
- **Sphinx autodoc** (`pip install sphinx`) — De-facto-Standard

Gemessen wird: Generierungszeit (timeit, 10 Runs, Median), Output-Größe,
Doc-Coverage (% Funktionen mit Docstring). Ergebnisse → `benchmarks/results.json`
und als Tabelle in `docs/API.md` eingebettet.

## 📐 Konventionen

- **Style**: `ruff` (lint + format), `mypy --strict` für Type-Checking.
- **Tests**: `pytest`, Ziel ≥ 90 % Coverage auf `src/`.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).
- **Python**: stdlib bevorzugt, externe Deps nur wenn nötig (in `pyproject.toml`).
- **Doku-Header-Format**:
  `*🤖 AUTO-GENERATED on <ISO-Timestamp> — do not edit manually*`

## 🔄 Erweiterung

Neuen Generator hinzufügen:
1. `scripts/generate_<name>.py` nach Vorlage anlegen.
2. In `scripts/update_all.py` registrieren.
3. Test in `tests/` ergänzen.
4. In dieser Tabelle dokumentieren.
