# Copyright (c) 2025-2026 Benjamin Mummery

"""Parse type information from function and method docstrings."""

from __future__ import annotations

import ast
import re

from dataclasses import dataclass, field


@dataclass
class DocstringTypeInfo:
    """Type information extracted from a docstring."""

    args: dict[str, str] = field(default_factory=dict)
    documented_args: set[str] = field(default_factory=set)
    returns: str | None = None
    documents_return: bool = False
    style: str | None = None


_NUMPY_SECTION_HEADERS = {
    "parameters",
    "params",
    "args",
    "arguments",
    "returns",
    "return",
    "yields",
}


def _is_numpy_section_start(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    header = lines[index].strip().lower()
    underline = lines[index + 1].strip()
    return header in _NUMPY_SECTION_HEADERS and bool(re.match(r"^-+$", underline))


_SECTION_ALIASES = {
    "args": "args",
    "arguments": "args",
    "parameters": "args",
    "params": "args",
    "returns": "returns",
    "return": "returns",
    "yields": "returns",
    "rtype": "returns",
}

_GOOGLE_PARAM_RE = re.compile(
    r"^(\s*)(\w+)\s+\(([^)]+)\)\s*:\s*(.*)$",
)
_GOOGLE_UNTYPED_PARAM_RE = re.compile(r"^(\s*)(\w+)\s*:\s*(.*)$")
_NUMPY_PARAM_RE = re.compile(r"^(\s*)(\w+)\s*:\s*(.+)$")
_NUMPY_UNTYPED_PARAM_RE = re.compile(r"^(\s*)(\w+)\s*$")
_SPHINX_PARAM_RE = re.compile(r"^:param\s+(\S+)\s+(\w+)\s*:\s*(.*)$")
_SPHINX_UNTYPED_PARAM_RE = re.compile(r"^:param\s+(\w+)\s*:\s*(.*)$")
_SPHINX_TYPE_RE = re.compile(r"^:type\s+(\w+)\s*:\s*(.+)$")
_SPHINX_RTYPE_RE = re.compile(r"^:rtype:\s*(.+)$")
_SPHINX_RETURN_RE = re.compile(r"^:returns?\s*:")


def _normalize_type(type_str: str) -> str:
    """Normalize a type string for comparison."""
    normalized = " ".join(type_str.strip().split())
    if normalized.endswith(", optional"):
        normalized = normalized[: -len(", optional")].strip()
    return normalized


def _indent_width(line: str) -> int:
    """Return the display width of a line's leading whitespace."""
    indent = line[: len(line) - len(line.lstrip())]
    return len(indent.expandtabs())


def _split_google_return(line: str) -> tuple[str, str] | None:
    """Split a typed Google return entry without mistaking description punctuation."""
    for match in re.finditer(":", line):
        type_str = line[: match.start()].strip()
        try:
            ast.parse(type_str, mode="eval")
        except SyntaxError:
            continue
        return type_str, line[match.end() :].lstrip()
    return None


def types_match(docstring_type: str, signature_type: str) -> bool:
    """Return True when two type strings describe the same type."""
    return _normalize_type(docstring_type) == _normalize_type(signature_type)


def parse_docstring_types(docstring: str) -> DocstringTypeInfo:
    """Extract parameter and return types from a docstring.

    Supports Google, NumPy, and Sphinx/reStructuredText formats.
    """
    google = _parse_google(docstring)
    if google.documented_args or google.documents_return:
        google.style = "google"
        return google

    numpy = _parse_numpy(docstring)
    if numpy.documented_args or numpy.documents_return:
        numpy.style = "numpy"
        return numpy

    sphinx = _parse_sphinx(docstring)
    if sphinx.documented_args or sphinx.documents_return:
        sphinx.style = "sphinx"
        return sphinx

    return DocstringTypeInfo()


def _parse_google(docstring: str) -> DocstringTypeInfo:
    info = DocstringTypeInfo()
    section: str | None = None

    for line in docstring.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        header = stripped.rstrip(":")
        if stripped.endswith(":") and header.lower() in _SECTION_ALIASES:
            section = _SECTION_ALIASES[header.lower()]
            continue

        if section == "args":
            if match := _GOOGLE_PARAM_RE.match(line):
                name = match.group(2)
                info.documented_args.add(name)
                info.args[name] = _normalize_type(match.group(3))
            elif match := _GOOGLE_UNTYPED_PARAM_RE.match(line):
                info.documented_args.add(match.group(2))
        elif section == "returns" and not info.documents_return:
            info.documents_return = True
            if return_entry := _split_google_return(stripped):
                type_part, _ = return_entry
                info.returns = _normalize_type(type_part)

    return info


def _parse_numpy(docstring: str) -> DocstringTypeInfo:
    info = DocstringTypeInfo()
    lines = docstring.splitlines()
    index = 0

    while index < len(lines):
        header = lines[index].strip()
        if (
            index + 1 < len(lines)
            and header.lower() in {"parameters", "params", "args", "arguments"}
            and re.match(r"^-+$", lines[index + 1].strip())
        ):
            index += 2
            while index < len(lines):
                line = lines[index]
                if not line.strip():
                    index += 1
                    continue
                if _is_numpy_section_start(lines, index):
                    break
                if match := _NUMPY_PARAM_RE.match(line):
                    param = match.group(2)
                    type_str = _normalize_type(match.group(3))
                    info.documented_args.add(param)
                    info.args[param] = type_str
                elif match := _NUMPY_UNTYPED_PARAM_RE.match(line):
                    info.documented_args.add(match.group(2))
                index += 1
            continue

        if (
            index + 1 < len(lines)
            and header.lower() in {"returns", "return", "yields"}
            and re.match(r"^-+$", lines[index + 1].strip())
        ):
            section_indent = _indent_width(lines[index])
            index += 2
            if index < len(lines) and lines[index].strip():
                info.documents_return = True
                if _indent_width(lines[index]) <= section_indent:
                    info.returns = _normalize_type(lines[index].strip())
            continue

        index += 1

    return info


def _parse_sphinx(docstring: str) -> DocstringTypeInfo:
    info = DocstringTypeInfo()
    pending_types: dict[str, str] = {}

    for line in docstring.splitlines():
        stripped = line.strip()
        if match := _SPHINX_PARAM_RE.match(stripped):
            type_str, name = match.group(1), match.group(2)
            info.documented_args.add(name)
            info.args[name] = _normalize_type(type_str)
        elif match := _SPHINX_UNTYPED_PARAM_RE.match(stripped):
            info.documented_args.add(match.group(1))
        elif match := _SPHINX_TYPE_RE.match(stripped):
            info.documented_args.add(match.group(1))
            pending_types[match.group(1)] = _normalize_type(match.group(2))
        elif match := _SPHINX_RTYPE_RE.match(stripped):
            info.documents_return = True
            info.returns = _normalize_type(match.group(1))
        elif _SPHINX_RETURN_RE.match(stripped):
            info.documents_return = True

    for name, type_str in pending_types.items():
        info.args.setdefault(name, type_str)

    return info


def rewrite_docstring_types(
    docstring: str,
    info: DocstringTypeInfo,
    *,
    remove_types: bool,
    updated_args: dict[str, str] | None = None,
    updated_return: str | None = None,
) -> tuple[str, bool]:
    """Rewrite a docstring to remove or update embedded type information.

    Returns:
        tuple[str, bool]: Tuple of the rewritten docstring and whether it changed.
    """
    if info.style == "google":
        return _rewrite_google(
            docstring,
            remove_types=remove_types,
            updated_args=updated_args,
            updated_return=updated_return,
        )
    if info.style == "numpy":
        return _rewrite_numpy(
            docstring,
            remove_types=remove_types,
            updated_args=updated_args,
            updated_return=updated_return,
        )
    if info.style == "sphinx":
        return _rewrite_sphinx(
            docstring,
            remove_types=remove_types,
            updated_args=updated_args,
            updated_return=updated_return,
        )
    return docstring, False


def _rewrite_google(
    docstring: str,
    *,
    remove_types: bool,
    updated_args: dict[str, str] | None,
    updated_return: str | None,
) -> tuple[str, bool]:
    section: str | None = None
    output: list[str] = []
    changed = False

    for line in docstring.splitlines():
        stripped = line.strip()
        header = stripped.rstrip(":")
        if header.lower() in _SECTION_ALIASES:
            section = _SECTION_ALIASES[header.lower()]
            output.append(line)
            continue

        if section == "args" and (match := _GOOGLE_PARAM_RE.match(line)):
            indent, name, type_str, description = match.groups()
            optional_suffix = ", optional" if ", optional" in type_str else ""
            if updated_args and name in updated_args:
                type_str = updated_args[name]
                changed = True
            if remove_types:
                output.append(f"{indent}{name}: {description}")
                changed = True
            else:
                output.append(
                    f"{indent}{name} ({type_str}{optional_suffix}): {description}",
                )
            continue

        if section == "args" and (match := _GOOGLE_UNTYPED_PARAM_RE.match(line)):
            indent, name, description = match.groups()
            if not remove_types and updated_args and name in updated_args:
                output.append(f"{indent}{name} ({updated_args[name]}): {description}")
                changed = True
            else:
                output.append(line)
            continue

        if section == "returns" and stripped:
            indent = line[: len(line) - len(line.lstrip())]
            if return_entry := _split_google_return(stripped):
                type_part, description = return_entry
                if updated_return is not None:
                    type_part = updated_return
                    changed = True
                if remove_types:
                    output.append(f"{indent}{description}")
                    changed = True
                else:
                    output.append(f"{indent}{type_part}: {description}")
            elif updated_return is not None and not remove_types:
                output.append(f"{indent}{updated_return}: {stripped}")
                changed = True
            else:
                output.append(line)
            section = None
            continue

        output.append(line)

    return "\n".join(output), changed


def _rewrite_numpy(
    docstring: str,
    *,
    remove_types: bool,
    updated_args: dict[str, str] | None,
    updated_return: str | None,
) -> tuple[str, bool]:
    lines = docstring.splitlines()
    output: list[str] = []
    index = 0
    changed = False

    while index < len(lines):
        header = lines[index].strip()
        if (
            index + 1 < len(lines)
            and header.lower() in {"parameters", "params", "args", "arguments"}
            and re.match(r"^-+$", lines[index + 1].strip())
        ):
            output.extend([lines[index], lines[index + 1]])
            index += 2
            while index < len(lines):
                line = lines[index]
                if not line.strip():
                    output.append(line)
                    index += 1
                    continue
                if _is_numpy_section_start(lines, index):
                    break
                if match := _NUMPY_PARAM_RE.match(line):
                    indent, name, type_str = match.groups()
                    if updated_args and name in updated_args:
                        type_str = updated_args[name]
                        changed = True
                    if remove_types:
                        output.append(f"{indent}{name}")
                        changed = True
                    else:
                        output.append(f"{indent}{name} : {type_str}")
                elif match := _NUMPY_UNTYPED_PARAM_RE.match(line):
                    indent, name = match.groups()
                    if not remove_types and updated_args and name in updated_args:
                        output.append(f"{indent}{name} : {updated_args[name]}")
                        changed = True
                    else:
                        output.append(line)
                else:
                    output.append(line)
                index += 1
            continue

        if (
            index + 1 < len(lines)
            and header.lower() in {"returns", "return", "yields"}
            and re.match(r"^-+$", lines[index + 1].strip())
        ):
            section_indent = lines[index][
                : len(lines[index]) - len(lines[index].lstrip())
            ]
            output.extend([lines[index], lines[index + 1]])
            return_lines, index, return_changed = _rewrite_numpy_return(
                lines,
                index + 2,
                section_indent=section_indent,
                remove_types=remove_types,
                updated_return=updated_return,
            )
            output.extend(return_lines)
            changed |= return_changed
            continue

        output.append(lines[index])
        index += 1

    return "\n".join(output), changed


def _rewrite_numpy_return(
    lines: list[str],
    index: int,
    *,
    section_indent: str,
    remove_types: bool,
    updated_return: str | None,
) -> tuple[list[str], int, bool]:
    if index >= len(lines) or not lines[index].strip():
        return [], index, False

    type_line = lines[index]
    has_type_line = _indent_width(type_line) <= len(section_indent.expandtabs())
    if remove_types and has_type_line:
        return [], index + 1, True
    if updated_return is not None and has_type_line:
        return [_with_indent(type_line, updated_return)], index + 1, True
    if updated_return is not None:
        return [f"{section_indent}{updated_return}", type_line], index + 1, True
    return [type_line], index + 1, False


def _sphinx_type_directives(docstring: str) -> tuple[set[str], bool]:
    lines = docstring.splitlines()
    names = {
        match.group(1)
        for line in lines
        if (match := _SPHINX_TYPE_RE.match(line.strip()))
    }
    has_rtype = any(_SPHINX_RTYPE_RE.match(line.strip()) for line in lines)
    return names, has_rtype


def _with_indent(line: str, value: str) -> str:
    return f"{line[: len(line) - len(line.lstrip())]}{value}"


def _rewrite_sphinx(
    docstring: str,
    *,
    remove_types: bool,
    updated_args: dict[str, str] | None,
    updated_return: str | None,
) -> tuple[str, bool]:
    output: list[str] = []
    changed = False
    typed_directive_names, has_rtype = _sphinx_type_directives(docstring)

    for line in docstring.splitlines():
        stripped = line.strip()
        if match := _SPHINX_PARAM_RE.match(stripped):
            type_str, name, description = match.group(1), match.group(2), match.group(3)
            if updated_args and name in updated_args:
                type_str = updated_args[name]
                changed = True
            if remove_types:
                output.append(_with_indent(line, f":param {name}: {description}"))
                changed = True
            else:
                output.append(
                    _with_indent(line, f":param {type_str} {name}: {description}"),
                )
            continue

        if match := _SPHINX_UNTYPED_PARAM_RE.match(stripped):
            name, description = match.groups()
            if (
                not remove_types
                and updated_args
                and name in updated_args
                and name not in typed_directive_names
            ):
                output.append(
                    _with_indent(
                        line,
                        f":param {updated_args[name]} {name}: {description}",
                    ),
                )
                changed = True
            else:
                output.append(line)
            continue

        if match := _SPHINX_TYPE_RE.match(stripped):
            if remove_types:
                changed = True
                continue
            name = match.group(1)
            type_str = match.group(2)
            if updated_args and name in updated_args:
                type_str = updated_args[name]
                changed = True
            output.append(_with_indent(line, f":type {name}: {type_str}"))
            continue

        if match := _SPHINX_RTYPE_RE.match(stripped):
            type_str = match.group(1)
            if updated_return is not None:
                type_str = updated_return
                changed = True
            if remove_types:
                changed = True
                continue
            output.append(_with_indent(line, f":rtype: {type_str}"))
            continue

        if (
            _SPHINX_RETURN_RE.match(stripped)
            and updated_return is not None
            and not remove_types
            and not has_rtype
        ):
            output.append(line)
            output.append(_with_indent(line, f":rtype: {updated_return}"))
            changed = True
            continue

        output.append(line)

    return "\n".join(output), changed
