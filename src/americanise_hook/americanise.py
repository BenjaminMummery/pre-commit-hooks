#!/usr/bin/env python3

# Copyright (c) 2025 Benjamin Mummery

"""
Check for non-US spelling in source files, and (optionally) "correct" them.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
from pathlib import Path

from src._shared import resolvers


def _americanise(file: Path) -> int:
    """Find common non-US spellings in source files and (optionally) "correct" them."""
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

    # Check that files exist
    args.files = resolvers.resolve_files(args.files)

    return args


def main():
    """
    Entrypoint for the americanize hook.

    Parses source files looking for common non-american spellings and either corrects or reports them.

    Returns:
        int: 1 if incorrect spellings were found, 0 otherwise.
    """
    files = _parse_args().files

    retv: int = 0
    for file in files:
        retv |= _americanise(file)

    return retv


if __name__ == "__main__":
    exit(main())
