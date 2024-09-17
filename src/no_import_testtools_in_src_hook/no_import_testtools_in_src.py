# Copyright (c) 2024 Benjamin Mummery

"""
Scan source files that aren't tests for test-specific imports (pytest, unittest, etc).

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""


import argparse
from pathlib import Path

from src._shared import resolvers


def _check_for_imports(file: Path) -> int:
    """
    Check whether the file imports from a testing toolkit.

    Currently detects imports from pytest and unittest.

    Args:
        file (Path): The file to be checked

    Returns:
        int: 1 if the file imports testing, 0 otherwise.
    """
    bad_imports = []

    with open(file) as f:
        content: str = f.read()

    if "import pytest" in content:
        bad_imports.append("pytest")
    if "import unittest" in content:
        bad_imports.append("unittest")

    if len(bad_imports) == 0:
        return 0

    print(f"{file} is not a test file, but imports {', '.join(bad_imports)}")
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

    # Check that files exist
    args.files = resolvers.resolve_files(args.files)

    return args


def main():
    """
    Entrypoint for the no_import_testtools_in_src hook.

    Scan source files that aren't tests for test-specific imports (pytest, unittest,
    etc).

    Returns:
        int: 1 if imports are found, 0 otherwise.
    """
    files = _parse_args().files

    retv: int = 0
    for file in files:
        retv |= _check_for_imports(file)

    return retv


if __name__ == "__main__":
    exit(main())
