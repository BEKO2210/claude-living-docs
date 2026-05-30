"""AST-based extraction of public API metadata from Python source files.

This module walks Python source using the standard library :mod:`ast` module
and produces immutable, fully typed data structures describing the modules,
classes and functions it finds. It performs **no** rendering and never
imports the analysed code, which keeps extraction fast and side-effect free.

The output is consumed by :mod:`living_docs.generators`.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "ClassDoc",
    "FunctionDoc",
    "ModuleDoc",
    "Parameter",
    "count_coverage",
    "extract_directory",
    "extract_module",
    "extract_source",
    "iter_functions",
]


@dataclass(frozen=True)
class Parameter:
    """A single callable parameter.

    ``name`` keeps any ``*`` / ``**`` prefix for var-positional and
    var-keyword parameters so it can be rendered verbatim.
    """

    name: str
    annotation: str | None = None
    default: str | None = None


@dataclass(frozen=True)
class FunctionDoc:
    """A module-level function or a method extracted from the AST."""

    name: str
    qualname: str
    docstring: str | None
    parameters: tuple[Parameter, ...]
    returns: str | None
    decorators: tuple[str, ...]
    is_async: bool
    lineno: int

    @property
    def signature(self) -> str:
        """Return a rendered ``(...) -> ret`` signature string."""
        rendered: list[str] = []
        for param in self.parameters:
            piece = param.name
            if param.annotation is not None:
                piece += f": {param.annotation}"
            if param.default is not None:
                glue = " = " if param.annotation is not None else "="
                piece += f"{glue}{param.default}"
            rendered.append(piece)
        suffix = f" -> {self.returns}" if self.returns is not None else ""
        return f"({', '.join(rendered)}){suffix}"


@dataclass(frozen=True)
class ClassDoc:
    """A class definition with its public methods."""

    name: str
    qualname: str
    docstring: str | None
    bases: tuple[str, ...]
    decorators: tuple[str, ...]
    methods: tuple[FunctionDoc, ...]
    lineno: int


@dataclass(frozen=True)
class ModuleDoc:
    """A whole module: its docstring plus public functions and classes."""

    name: str
    path: str
    docstring: str | None
    functions: tuple[FunctionDoc, ...]
    classes: tuple[ClassDoc, ...]


def _is_public(name: str) -> bool:
    return not name.startswith("_")


def _annotation(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    return ast.unparse(node)


def _extract_parameters(args: ast.arguments) -> tuple[Parameter, ...]:
    """Flatten an :class:`ast.arguments` node into ordered parameters."""
    params: list[Parameter] = []

    positional = [*args.posonlyargs, *args.args]
    defaults = list(args.defaults)
    offset = len(positional) - len(defaults)
    for index, arg in enumerate(positional):
        default = ast.unparse(defaults[index - offset]) if index >= offset else None
        params.append(Parameter(arg.arg, _annotation(arg.annotation), default))

    if args.vararg is not None:
        params.append(
            Parameter("*" + args.vararg.arg, _annotation(args.vararg.annotation), None)
        )
    elif args.kwonlyargs:
        # Keyword-only args with no ``*args`` still need a bare ``*`` separator.
        params.append(Parameter("*", None, None))

    for arg, default_node in zip(args.kwonlyargs, args.kw_defaults, strict=True):
        default = ast.unparse(default_node) if default_node is not None else None
        params.append(Parameter(arg.arg, _annotation(arg.annotation), default))

    if args.kwarg is not None:
        params.append(
            Parameter("**" + args.kwarg.arg, _annotation(args.kwarg.annotation), None)
        )

    return tuple(params)


def _extract_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef, qual_prefix: str
) -> FunctionDoc:
    return FunctionDoc(
        name=node.name,
        qualname=f"{qual_prefix}{node.name}",
        docstring=ast.get_docstring(node),
        parameters=_extract_parameters(node.args),
        returns=_annotation(node.returns),
        decorators=tuple(ast.unparse(dec) for dec in node.decorator_list),
        is_async=isinstance(node, ast.AsyncFunctionDef),
        lineno=node.lineno,
    )


def _extract_class(node: ast.ClassDef, qual_prefix: str, include_private: bool) -> ClassDoc:
    methods: list[FunctionDoc] = []
    for child in node.body:
        if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef) and (
            include_private or _is_public(child.name)
        ):
            methods.append(_extract_function(child, f"{qual_prefix}{node.name}."))
    return ClassDoc(
        name=node.name,
        qualname=f"{qual_prefix}{node.name}",
        docstring=ast.get_docstring(node),
        bases=tuple(ast.unparse(base) for base in node.bases),
        decorators=tuple(ast.unparse(dec) for dec in node.decorator_list),
        methods=tuple(methods),
        lineno=node.lineno,
    )


def extract_source(
    source: str,
    *,
    module_name: str,
    path: str = "<string>",
    include_private: bool = False,
) -> ModuleDoc:
    """Parse ``source`` and return a :class:`ModuleDoc`.

    Only top-level functions and classes are collected. Names starting with
    an underscore are skipped unless ``include_private`` is true.
    """
    tree = ast.parse(source, filename=path)
    prefix = f"{module_name}."

    functions: list[FunctionDoc] = []
    classes: list[ClassDoc] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if include_private or _is_public(node.name):
                functions.append(_extract_function(node, prefix))
        elif isinstance(node, ast.ClassDef) and (include_private or _is_public(node.name)):
            classes.append(_extract_class(node, prefix, include_private))

    return ModuleDoc(
        name=module_name,
        path=path,
        docstring=ast.get_docstring(tree),
        functions=tuple(functions),
        classes=tuple(classes),
    )


def _module_name(file: Path, root: Path) -> str:
    relative = file.relative_to(root).with_suffix("")
    parts = list(relative.parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts) if parts else root.name


def extract_module(file: Path, root: Path, *, include_private: bool = False) -> ModuleDoc:
    """Extract a single ``.py`` file, deriving its dotted name from ``root``."""
    source = file.read_text(encoding="utf-8")
    return extract_source(
        source,
        module_name=_module_name(file, root),
        path=str(file.relative_to(root)),
        include_private=include_private,
    )


def extract_directory(root: Path, *, include_private: bool = False) -> tuple[ModuleDoc, ...]:
    """Recursively extract every ``.py`` file under ``root``, sorted by name.

    Private modules (``_name.py``) are skipped unless ``include_private`` is
    set; ``__init__.py`` is always included so package docstrings survive.
    """
    modules: list[ModuleDoc] = []
    for file in sorted(root.rglob("*.py")):
        stem = file.stem
        if not include_private and stem.startswith("_") and stem != "__init__":
            continue
        modules.append(extract_module(file, root, include_private=include_private))
    modules.sort(key=lambda module: module.name)
    return tuple(modules)


def iter_functions(modules: tuple[ModuleDoc, ...]) -> list[FunctionDoc]:
    """Yield every function and method across ``modules`` as a flat list."""
    collected: list[FunctionDoc] = []
    for module in modules:
        collected.extend(module.functions)
        for klass in module.classes:
            collected.extend(klass.methods)
    return collected


def count_coverage(modules: tuple[ModuleDoc, ...]) -> tuple[int, int]:
    """Return ``(documented, total)`` callables across ``modules``."""
    functions = iter_functions(modules)
    total = len(functions)
    documented = sum(1 for func in functions if func.docstring)
    return documented, total
