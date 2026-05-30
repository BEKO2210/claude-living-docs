"""Exact-value tests for the AST extractor against the known sample module."""

from __future__ import annotations

from pathlib import Path

from living_docs.extractors import (
    Parameter,
    count_coverage,
    extract_directory,
    extract_module,
    extract_source,
    iter_functions,
)

SAMPLE = Path(__file__).parent / "sample_module.py"


def _module():
    return extract_module(SAMPLE, SAMPLE.parent)


def test_module_metadata():
    module = _module()
    assert module.name == "sample_module"
    assert module.path == "sample_module.py"
    assert module.docstring == "Sample module used as a known input for extractor tests."


def test_public_functions_only():
    module = _module()
    names = [func.name for func in module.functions]
    assert names == ["add", "fetch"]  # _private excluded


def test_add_signature_is_exact():
    func = next(f for f in _module().functions if f.name == "add")
    assert func.parameters == (
        Parameter("a", "int", None),
        Parameter("b", "int", "1"),
    )
    assert func.returns == "int"
    assert func.decorators == ("functools.cache",)
    assert func.is_async is False
    assert func.qualname == "sample_module.add"
    assert func.signature == "(a: int, b: int = 1) -> int"


def test_async_varargs_and_kwargs():
    func = next(f for f in _module().functions if f.name == "fetch")
    assert func.is_async is True
    assert [p.name for p in func.parameters] == ["url", "*args", "timeout", "**kwargs"]
    timeout = func.parameters[2]
    assert timeout == Parameter("timeout", "float", "1.0")
    assert func.returns == "bytes"


def test_classes_and_methods():
    module = _module()
    names = [klass.name for klass in module.classes]
    assert names == ["Base", "Greeter"]  # _Hidden excluded

    greeter = next(k for k in module.classes if k.name == "Greeter")
    assert greeter.bases == ("Base",)
    method_names = [m.name for m in greeter.methods]
    assert method_names == ["greet"]  # _secret excluded
    assert greeter.methods[0].qualname == "sample_module.Greeter.greet"
    assert greeter.methods[0].signature == "(self, name: str) -> str"


def test_include_private_flag():
    source = SAMPLE.read_text(encoding="utf-8")
    module = extract_source(source, module_name="sample", include_private=True)
    func_names = [f.name for f in module.functions]
    assert "_private" in func_names
    class_names = [c.name for c in module.classes]
    assert "_Hidden" in class_names


def test_coverage_counts_every_callable():
    module = _module()
    documented, total = count_coverage((module,))
    # add, fetch, Greeter.greet  ->  3 documented public callables
    assert (documented, total) == (3, 3)
    assert len(iter_functions((module,))) == 3


def test_extract_directory_skips_private_modules(tmp_path):
    (tmp_path / "public.py").write_text('"""Public."""\n', encoding="utf-8")
    (tmp_path / "_helper.py").write_text('"""Private helper."""\n', encoding="utf-8")
    (tmp_path / "__init__.py").write_text('"""Package."""\n', encoding="utf-8")
    modules = extract_directory(tmp_path)
    names = sorted(m.name for m in modules)
    # _helper.py skipped; __init__ keeps the package name (tmp dir name).
    assert "public" in names
    assert "_helper" not in names
