"""End-to-end CLI tests against a real, freshly built external project.

These do not touch this repository: each test scaffolds an independent
project in a temp directory (its own ``pyproject.toml``, package, git repo),
then drives the public ``living-docs`` CLI exactly as a user would.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from living_docs.cli import main

PYPROJECT = """\
[project]
name = "demo-app"
version = "0.0.1"

[tool.living_docs]
source = "demo"
docs = "site"
"""

PACKAGE_INIT = '"""Demo application package."""\n'

PACKAGE_CORE = '''"""Core domain logic for the demo app."""

from __future__ import annotations


def greet(name: str, *, loud: bool = False) -> str:
    """Return a greeting for ``name``."""
    text = f"Hello, {name}!"
    return text.upper() if loud else text


class Counter:
    """A tiny stateful counter."""

    def __init__(self, start: int = 0) -> None:
        """Initialise the counter at ``start``."""
        self.value = start

    def increment(self, by: int = 1) -> int:
        """Add ``by`` and return the new value."""
        self.value += by
        return self.value
'''

FEATURES = '{"features": [{"name": "Greetings", "status": "stable", "description": "Says hello."}]}\n'


def _git(repo: Path, *args: str) -> None:
    env = {
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "PATH": os.environ.get("PATH", ""),
    }
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
    pkg = tmp_path / "demo"
    pkg.mkdir()
    (pkg / "__init__.py").write_text(PACKAGE_INIT, encoding="utf-8")
    (pkg / "core.py").write_text(PACKAGE_CORE, encoding="utf-8")
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "features.json").write_text(FEATURES, encoding="utf-8")

    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "feat: initial demo app")
    return tmp_path


def test_update_generates_docs_for_external_project(project: Path, capsys):
    rc = main(["-C", str(project), "update"])
    assert rc == 0

    api = (project / "site" / "API.md").read_text(encoding="utf-8")
    # The configured docs dir ("site") and source dir ("demo") are honoured.
    assert "AUTO-GENERATED" in api
    assert "def greet(name: str, *, loud: bool = False) -> str" in api
    assert "class `Counter`" in api
    # source="demo" is the package itself, so its modules are flattened.
    assert "Module `core`" in api

    # Features and changelog come from this project's own config + git history.
    assert (project / "site" / "FEATURES.md").exists()
    changelog = (project / "site" / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "feat: initial demo app" in changelog

    # No prompts.json in this project -> no PROMPTS.md produced.
    assert not (project / "site" / "PROMPTS.md").exists()


def test_check_is_green_then_red_after_a_source_change(project: Path):
    assert main(["-C", str(project), "update"]) == 0
    assert main(["-C", str(project), "check"]) == 0

    # Change the source -> docs are now stale -> check must fail.
    core = project / "demo" / "core.py"
    core.write_text(
        core.read_text(encoding="utf-8") + "\n\ndef farewell() -> str:\n    \"\"\"Bye.\"\"\"\n    return 'bye'\n",
        encoding="utf-8",
    )
    assert main(["-C", str(project), "check"]) == 1


def test_init_scaffolds_missing_config(tmp_path: Path, capsys):
    (tmp_path / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
    rc = main(["-C", str(tmp_path), "init"])
    assert rc == 0
    # features.json already absent here -> created by init.
    assert (tmp_path / "config" / "features.json").exists()
    assert (tmp_path / "config" / "prompts.json").exists()


def test_bench_runs_real_tools_and_embeds_table(project: Path):
    # Runs the actual pdoc and sphinx-apidoc against the external project.
    rc = main(["-C", str(project), "bench", "--runs", "1"])
    assert rc == 0

    results = json.loads((project / "benchmarks" / "results.json").read_text(encoding="utf-8"))
    tool_names = {row["tool"] for row in results["tools"]}
    assert "living-docs" in tool_names
    assert results["doc_coverage_pct"] == 100.0
    for row in results["tools"]:
        assert row["median_ms"] >= 0.0

    api = (project / "site" / "API.md").read_text(encoding="utf-8")
    assert "## Benchmarks" in api


def test_bench_without_source_fails(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        '[tool.living_docs]\nsource = "nope"\n', encoding="utf-8"
    )
    assert main(["-C", str(tmp_path), "bench"]) == 1


def test_zero_config_defaults_to_src(tmp_path: Path):
    # No pyproject at all: defaults to src/ -> docs/.
    pkg = tmp_path / "src" / "thing"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text('"""Thing."""\n', encoding="utf-8")
    (pkg / "math.py").write_text(
        '"""Math helpers."""\n\n\ndef double(x: int) -> int:\n    """Double x."""\n    return x * 2\n',
        encoding="utf-8",
    )
    assert main(["-C", str(tmp_path), "update"]) == 0
    api = (tmp_path / "docs" / "API.md").read_text(encoding="utf-8")
    assert "def double(x: int) -> int" in api
