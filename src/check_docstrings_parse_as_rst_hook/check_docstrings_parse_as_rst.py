#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Parse the source code to extract the docstrings, and check that they parse as RST.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import ast
from pathlib import Path
from typing import List

from restructuredtext_lint import lint

from src._shared import resolvers


def _check_class_recursive(classnode: ast.ClassDef) -> List[str]:
    """
    Parse all the docstrings of a class.

    This function calls itself to parse the docstrings of subclasses.

    Args:
        classnode (ast.ClassDef): The class node to be checked.

    Returns:
        list(str): a list of strings describing any RST errors in the docstrings.
    """
    error_strings: List[str] = []
    if docstring := ast.get_docstring(classnode):
        for error in lint(docstring):
            error_strings.append(
                f"- error in docstring of class '{classnode.name}' "
                f"(lineno {classnode.lineno}): {error.message}"
            )
    for node in classnode.body:
        if isinstance(node, ast.FunctionDef) and (docstring := ast.get_docstring(node)):
            for error in lint(docstring):
                error_strings.append(
                    f"- error in docstring of method '{node.name}' "
                    f"of class '{classnode.name}' "
                    f"(lineno {node.lineno}): {error.message}"
                )
        elif isinstance(node, ast.ClassDef):
            error_strings += _check_class_recursive(node)
    return error_strings


def _check_docstring_rst(file: Path) -> int:
    """
    Identify docstrings in the file and check they are valid RST.

    Args:
        file (Path): the file to be examined

    Returns:
        int: 0 if all docstrings in the file are valid RST, 1 otherwise.
    """
    with open(file, "r") as f:
        contents: str = f.read()

    module = ast.parse(contents)

    error_strings: List[str] = []

    # Check module-level docstring
    if docstring := ast.get_docstring(module):
        for error in lint(docstring):
            error_strings.append(f"- error in module docstring: {error.message}")

    for node in module.body:
        # Check function docstrings.
        if isinstance(node, ast.FunctionDef):
            if docstring := ast.get_docstring(node):
                for error in lint(docstring):
                    error_strings.append(
                        f"- error in docstring of function '{node.name}' "
                        f"(lineno {node.lineno}): {error.message}"
                    )

        # Check class docstrings.
        elif isinstance(node, ast.ClassDef):
            error_strings += _check_class_recursive(node)

    if len(error_strings) == 0:
        return 0

    print(f"Found errors in {file}:")
    print("\n".join(error_strings))
    return 1


def _parse_args() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of Path): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    args = parser.parse_args()
    args.files = resolvers.resolve_files(args.files)
    return args


def main() -> int:
    """Entrypoint for the check_docstrings_parse_as_rst hook."""
    args = _parse_args()

    # Early exit if no files provided
    if len(args.files) < 1:
        return 0

    # Check the files
    retv = 0
    for file in args.files:
        retv |= _check_docstring_rst(file)

    return retv


if __name__ == "__main__":
    exit(main())
