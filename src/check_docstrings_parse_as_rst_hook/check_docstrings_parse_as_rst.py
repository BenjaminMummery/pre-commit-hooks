#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Parse the source code to extract the docstrings, and check that they parse as RST.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import re
from pathlib import Path
from typing import List

from restructuredtext_lint import lint

from src._shared import resolvers


def _extract_docstrings(content: str) -> List[str]:
    """
    Find all the docstrings in the string.

    Args:
        content (str): the string to be checked.

    Returns:
        list(str): a list of docstrings found in the content.

    """
    return re.findall(r'"""([\s\S]*?)"""', content, re.M)


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

    for docstring in _extract_docstrings(contents):
        errors = lint(docstring)
        if len(errors) > 0:
            return 1
    return 0


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
    args.files = resolvers._resolve_files(args.files)
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
