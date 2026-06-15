# Copyright (c) 2025-2026 Benjamin Mummery

"""Extract type information from function and method signatures."""

from __future__ import annotations

import ast

from dataclasses import dataclass, field


@dataclass
class SignatureTypeInfo:
    """Type information extracted from a function signature."""

    args: dict[str, str | None] = field(default_factory=dict)
    returns: str | None = None


def annotation_to_str(node: ast.expr | None) -> str | None:
    """Convert an annotation AST node to source text."""
    if node is None:
        return None
    if hasattr(ast, "unparse"):
        return ast.unparse(node)
    return _annotation_to_str_legacy(node)


def parse_signature_types(node: ast.AST) -> SignatureTypeInfo:
    """Extract parameter and return annotations from a function node."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        msg = "Expected a function definition node."
        raise TypeError(msg)

    info = SignatureTypeInfo()
    info.returns = annotation_to_str(node.returns)

    for arg in _iter_arguments(node.args):
        info.args[arg.arg] = annotation_to_str(arg.annotation)

    return info


def _iter_arguments(args: ast.arguments) -> list[ast.arg]:
    collected: list[ast.arg] = []
    collected.extend(args.posonlyargs)
    collected.extend(args.args)
    if args.vararg is not None:
        collected.append(args.vararg)
    collected.extend(args.kwonlyargs)
    if args.kwarg is not None:
        collected.append(args.kwarg)
    return collected


def build_signature_edits(
    node: ast.AST,
    source: str,
    *,
    add_args: dict[str, str],
    add_return: str | None,
    overwrite_args: dict[str, str],
    overwrite_return: str | None,
) -> list[tuple[int, int, int, int, str]]:
    """Build source edits for updating a function signature.

    Returns:
        List of (start_line, start_col, end_line, end_col, replacement) tuples.
        Line and column numbers are 1-based and 0-based respectively, matching AST.
    """
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        msg = "Expected a function definition node."
        raise TypeError(msg)

    edits: list[tuple[int, int, int, int, str]] = []

    for arg in _iter_arguments(node.args):
        if arg.arg in overwrite_args:
            edits.extend(_replace_annotation(source, arg, overwrite_args[arg.arg]))
        elif arg.arg in add_args and arg.annotation is None:
            edits.extend(_insert_annotation(source, arg, add_args[arg.arg]))

    if overwrite_return is not None and node.returns is not None:
        edits.extend(_replace_return(source, node, overwrite_return))
    elif add_return is not None and node.returns is None:
        edits.extend(_insert_return(source, node, add_return))

    return edits


def _insert_annotation(
    _source: str,
    arg: ast.arg,
    type_str: str,
) -> list[tuple[int, int, int, int, str]]:
    end_col = arg.col_offset + len(arg.arg)
    return [
        (
            arg.lineno,
            arg.col_offset,
            arg.lineno,
            end_col,
            f"{arg.arg}: {type_str}",
        ),
    ]


def _replace_annotation(
    source: str,
    arg: ast.arg,
    type_str: str,
) -> list[tuple[int, int, int, int, str]]:
    if arg.annotation is None:
        return _insert_annotation(source, arg, type_str)

    _node_start_offset(source, arg.lineno, arg.col_offset)
    end = _node_end_offset(source, arg.annotation)
    replacement = f"{arg.arg}: {type_str}"
    start_col = arg.col_offset
    end_line, end_col = _offset_to_position(source, end)
    return [(arg.lineno, start_col, end_line, end_col, replacement)]


def _insert_return(
    source: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    type_str: str,
) -> list[tuple[int, int, int, int, str]]:
    insert_line, insert_col = _arguments_end_position(node, source)
    return [
        (insert_line, insert_col, insert_line, insert_col, f" -> {type_str}"),
    ]


def _arguments_end_position(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    source: str,
) -> tuple[int, int]:
    end_lineno = getattr(node.args, "end_lineno", None)
    end_col = getattr(node.args, "end_col_offset", None)
    if end_lineno is not None and end_col is not None:
        return end_lineno, end_col

    lines = source.splitlines()
    line_index = node.lineno - 1
    paren_depth = 0
    started = False
    while line_index < len(lines):
        for col, char in enumerate(lines[line_index]):
            if char == "(":
                paren_depth += 1
                started = True
            elif char == ")":
                paren_depth -= 1
                if started and paren_depth == 0:
                    return line_index + 1, col + 1
        line_index += 1

    msg = f"Could not locate argument list for function '{node.name}'."
    raise ValueError(msg)


def _replace_return(
    source: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    type_str: str,
) -> list[tuple[int, int, int, int, str]]:
    if node.returns is None:
        return _insert_return(source, node, type_str)

    start_line = node.returns.lineno
    start_col = node.returns.col_offset
    end_line = node.returns.end_lineno or start_line
    end_col = node.returns.end_col_offset or start_col
    return [(start_line, start_col, end_line, end_col, type_str)]


def _node_start_offset(source: str, lineno: int, col_offset: int) -> int:
    lines = source.splitlines(keepends=True)
    offset = sum(len(lines[i]) for i in range(lineno - 1))
    return offset + col_offset


def _node_end_offset(source: str, node: ast.AST) -> int:
    end_line_raw = getattr(node, "end_lineno", None)
    if isinstance(end_line_raw, int):
        end_line = end_line_raw
    else:
        lineno_raw = getattr(node, "lineno", 1)
        end_line = lineno_raw if isinstance(lineno_raw, int) else 1

    end_col_raw = getattr(node, "end_col_offset", None)
    if isinstance(end_col_raw, int):
        end_col = end_col_raw
    else:
        end_col = len(source.splitlines()[end_line - 1])

    lines = source.splitlines(keepends=True)
    offset = sum(len(lines[i]) for i in range(end_line - 1))
    return offset + end_col


def _offset_to_position(source: str, offset: int) -> tuple[int, int]:
    current = 0
    for index, line in enumerate(source.splitlines(keepends=True), start=1):
        next_current = current + len(line)
        if offset <= next_current:
            return index, offset - current
        current = next_current
    last_line = source.count("\n") + 1
    return last_line, len(source.splitlines()[-1])


def _annotation_to_str_legacy(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return repr(node.value)
    if isinstance(node, ast.Attribute):
        return f"{_annotation_to_str_legacy(node.value)}.{node.attr}"
    if isinstance(node, ast.Subscript):
        value = _annotation_to_str_legacy(node.value)
        slice_value = _annotation_to_str_legacy(node.slice)
        return f"{value}[{slice_value}]"
    if isinstance(node, ast.Tuple):
        elements = ", ".join(_annotation_to_str_legacy(elt) for elt in node.elts)
        if len(node.elts) == 1:
            elements += ","
        return f"({elements})"
    msg = f"Unsupported annotation node: {type(node).__name__}"
    raise ValueError(msg)
