#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Sort file contents while preserving section structure.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse

from _shared import resolvers


def _sort_contents(file: str):
    """WIP."""
    pass


def _parse_args() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of Path): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[], help="Files to sort.")
    args = parser.parse_args()

    # Check that files exist
    args.files = resolvers._resolve_files(args.files)

    return args


def main() -> int:
    """
    Entrypoint for the sort_file_contents hook.

    Identifies sections within the input files by looking for a comment following a
    blank line. The contents of each section are then sorted alphabetically.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    args = _parse_args()

    # Early exit if no files provided:
    if len(args.files) < 1:
        return 0

    retv = 0
    for file in args.files:
        retv |= _sort_contents(file)

    return retv


if __name__ == "__main__":
    raise SystemExit(main())
