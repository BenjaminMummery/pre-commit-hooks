#!/usr/bin/env python3
# Copyright (c) 2025-2026 Benjamin Mummery
"""Synchronise type hints between function signatures and docstrings.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

from __future__ import annotations

import argparse
import ast
import sys

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

from src._shared import print_diff, resolvers
from src._shared.config_parsing import read_config
from src.sync_type_hints_hook.docstring_types import (
    parse_docstring_types,
    rewrite_docstring_types,
    types_match,
)
from src.sync_type_hints_hook.exceptions import TypeClashError
from src.sync_type_hints_hook.signature_types import (
    build_signature_edits,
    parse_signature_types,
)
from src.sync_type_hints_hook.source_edits import apply_edits

if TYPE_CHECKING:
    from pathlib import Path

    from src.sync_type_hints_hook.source_edits import Edit

TOOL_NAME = "sync_type_hints"
IGNORE_PRAGMA = "pragma: no sync-type-hints"


@dataclass
class FunctionContext:
    """Metadata for a function or method to be processed."""

    node: ast.AST
    qualified_name: str


@dataclass
class HookConfig:
    """Runtime configuration for the sync-type-hints hook."""

    on_clash: str = "error"
    signature_types_only: bool = False


def _parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    msg = f"Could not parse boolean config value '{value}'."
    raise ValueError(msg)


def _load_config() -> HookConfig:
    try:
        config, _ = read_config(TOOL_NAME)
    except FileNotFoundError:
        return HookConfig()

    on_clash = str(config.get("on-clash", config.get("on_clash", "error")))
    signature_types_only = _parse_bool(
        config.get(
            "signature-types-only",
            config.get("signature_types_only", False),
        ),
    )
    return HookConfig(
        on_clash=on_clash,
        signature_types_only=signature_types_only,
    )


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument(
        "--on-clash",
        choices=["error", "prefer-signature", "prefer-docstring"],
        default=None,
    )
    parser.add_argument(
        "--signature-types-only",
        action="store_true",
        default=None,
        help="keep type information only in signatures",
    )

    args = parser.parse_args()
    args.files = resolvers.resolve_files(args.files)

    config = _load_config()
    if args.on_clash is None:
        args.on_clash = config.on_clash
    if args.signature_types_only is None:
        args.signature_types_only = config.signature_types_only

    return args


def _should_ignore(source: str, node: ast.AST) -> bool:
    if not hasattr(node, "lineno"):
        return False
    lines = source.splitlines()
    if node.lineno - 1 >= len(lines):
        return False
    return IGNORE_PRAGMA in lines[node.lineno - 1]


def _get_docstring_node(node: ast.AST) -> tuple[ast.expr, str] | None:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return None
    if not node.body:
        return None
    statement = node.body[0]
    if not isinstance(statement, ast.Expr):
        return None
    value = statement.value
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return value, value.value
    if isinstance(value, ast.Str):  # pragma: no cover
        return value, value.s  # type: ignore[return-value]
    return None


def _docstring_edit(source: str, doc_node: ast.expr, new_doc: str) -> Edit:
    start = _node_start_offset(source, doc_node.lineno, doc_node.col_offset)
    prefix = source[start : start + 3]
    quote = prefix if prefix in {'"""', "'''"} else '"""'
    end_line = doc_node.end_lineno or doc_node.lineno
    end_col = doc_node.end_col_offset or doc_node.col_offset
    replacement = f"{quote}{new_doc}{quote}"
    return (
        doc_node.lineno,
        doc_node.col_offset,
        end_line,
        end_col,
        replacement,
    )


def _node_start_offset(source: str, lineno: int, col_offset: int) -> int:
    lines = source.splitlines(keepends=True)
    offset = sum(len(lines[i]) for i in range(lineno - 1))
    return offset + col_offset


class _FunctionCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.functions: list[FunctionContext] = []
        self._parents: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._parents.append(node.name)
        self.generic_visit(node)
        self._parents.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        qualified_name = ".".join([*self._parents, node.name])
        self.functions.append(FunctionContext(node=node, qualified_name=qualified_name))
        self._parents.append(node.name)
        self.generic_visit(node)
        self._parents.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # type: ignore[arg-type]


def _collect_functions(tree: ast.AST) -> list[FunctionContext]:
    collector = _FunctionCollector()
    collector.visit(tree)
    return collector.functions


def _plan_function_edits(
    source: str,
    context: FunctionContext,
    file: Path,
    config: HookConfig,
) -> tuple[list[Edit], bool]:
    node = context.node
    if _should_ignore(source, node):
        return [], False

    docstring_info = _get_docstring_node(node)
    if docstring_info is None:
        return [], False

    doc_node, docstring = docstring_info
    doc_types = parse_docstring_types(docstring)
    if not doc_types.documented_args and not doc_types.documents_return:
        return [], False

    signature_types = parse_signature_types(node)

    add_args: dict[str, str] = {}
    overwrite_args: dict[str, str] = {}
    updated_doc_args: dict[str, str] = {}
    add_return: str | None = None
    overwrite_return: str | None = None
    updated_doc_return: str | None = None

    for name in doc_types.documented_args:
        doc_type = doc_types.args.get(name)
        signature_type = signature_types.args.get(name)
        if doc_type is None:
            if signature_type is not None and not config.signature_types_only:
                updated_doc_args[name] = signature_type
            continue

        if signature_type is None:
            if name in signature_types.args:
                add_args[name] = doc_type
            continue

        if types_match(doc_type, signature_type):
            continue

        if config.on_clash == "error":
            raise TypeClashError(
                str(file),
                context.qualified_name,
                name,
                doc_type,
                signature_type,
            )
        if config.on_clash == "prefer-signature":
            updated_doc_args[name] = signature_type
        else:
            overwrite_args[name] = doc_type

    if doc_types.returns is not None:
        if signature_types.returns is None:
            add_return = doc_types.returns
        elif not types_match(doc_types.returns, signature_types.returns):
            if config.on_clash == "error":
                raise TypeClashError(
                    str(file),
                    context.qualified_name,
                    "return",
                    doc_types.returns,
                    signature_types.returns,
                )
            if config.on_clash == "prefer-signature":
                updated_doc_return = signature_types.returns
            else:
                overwrite_return = doc_types.returns
    elif (
        doc_types.documents_return
        and signature_types.returns is not None
        and not config.signature_types_only
    ):
        updated_doc_return = signature_types.returns

    edits = build_signature_edits(
        node,
        source,
        add_args=add_args,
        add_return=add_return,
        overwrite_args=overwrite_args,
        overwrite_return=overwrite_return,
    )

    docstring_changed = False
    if (
        config.signature_types_only
        or updated_doc_args
        or updated_doc_return is not None
    ):
        new_docstring, docstring_changed = rewrite_docstring_types(
            docstring,
            doc_types,
            remove_types=config.signature_types_only,
            updated_args=updated_doc_args or None,
            updated_return=updated_doc_return,
        )
        if docstring_changed:
            edits.append(_docstring_edit(source, doc_node, new_docstring))

    return edits, bool(edits)


def _format_edit_messages(
    source: str, new_source: str, edits: Iterable[Edit]
) -> list[str]:
    messages: list[str] = []
    old_lines = source.splitlines()
    new_lines = new_source.splitlines()
    seen_lines = set()

    for edit in edits:
        start_line = edit[0]
        if start_line in seen_lines:
            continue
        if start_line - 1 >= len(old_lines) or start_line - 1 >= len(new_lines):
            continue
        old_line = old_lines[start_line - 1]
        new_line = new_lines[start_line - 1]
        if old_line != new_line:
            messages.append(print_diff.format_diff(old_line, new_line, start_line))
            seen_lines.add(start_line)

    return messages


def _sync_type_hints(file: Path, config: HookConfig) -> int:
    with file.open() as handle:
        source = handle.read()

    try:
        tree = ast.parse(source, filename=str(file))
    except SyntaxError as error:
        print(f"{file}: could not parse file: {error}", file=sys.stderr)
        return 1

    all_edits: list[Edit] = []

    try:
        for context in _collect_functions(tree):
            edits, _ = _plan_function_edits(source, context, file, config)
            all_edits.extend(edits)
    except TypeClashError as error:
        print(error, file=sys.stderr)
        return 1

    if not all_edits:
        return 0

    new_source = apply_edits(source, all_edits)
    if new_source == source:
        return 0

    with file.open("w") as handle:
        handle.write(new_source)

    print(file)
    for message in _format_edit_messages(source, new_source, all_edits):
        print(message)

    return 1


def main() -> int:
    """Entrypoint for the sync-type-hints hook."""
    args = _parse_args()
    retv = 0
    for file in args.files:
        config = HookConfig(
            on_clash=args.on_clash,
            signature_types_only=args.signature_types_only,
        )
        retv |= _sync_type_hints(file, config)
    return retv


if __name__ == "__main__":
    sys.exit(main())
