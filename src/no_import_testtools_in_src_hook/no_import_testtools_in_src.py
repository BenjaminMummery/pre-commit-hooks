# Copyright (c) 2024 Benjamin Mummery

"""
Scan source files that aren't tests for test-specific imports (pytest, unittest, etc).

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import ast
import logging
from collections import namedtuple
from pathlib import Path
from typing import Any, Generator, List

from src._shared import resolvers

Import = namedtuple("Import", ["module", "name", "alias"])
logger = logging.getLogger(__name__)


def _get_imports(file: Path) -> Generator[Import, Any, None]:
    """
    Find all modules a file imports.

    Args:
        file (Path): The file to be checked.

    Yields:
        Generator[Import, None]
    """
    with open(file) as fh:
        try:
            root = ast.parse(fh.read(), file)
        except SyntaxError:
            logging.warning(
                f"Could not parse file {file}."
                " We'll assume that this is fine since an unparsable file probably "
                "won't successfully import anything anyway."
            )
            return

    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.Import):
            module: List[str] = []
        elif isinstance(node, ast.ImportFrom):
            module = node.module.split(".") if node.module is not None else []
        else:
            continue

        assert hasattr(node, "names")
        for n in node.names:
            yield Import(module, n.name.split("."), n.asname)


def _check_for_imports(file: Path) -> int:
    """
    Check whether the file imports from a testing toolkit.

    Currently detects imports from pytest and unittest.

    Args:
        file (Path): The file to be checked

    Returns:
        int: 1 if the file imports testing, 0 otherwise.
    """

    bad_imports: List[str] = []
    test_toolkits = set(["pytest", "unittest"])
    for imp in _get_imports(file):
        bad_imports += test_toolkits.intersection(imp.module + imp.name)

    # No bad imports, nothing to do.
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
    files = [file for file in _parse_args().files if "test" not in str(file)]

    retv: int = 0
    for file in files:
        retv |= _check_for_imports(file)

    return retv


if __name__ == "__main__":
    exit(main())
