# Copyright (c) 2023 Benjamin Mummery

"""
If the CHANGELOG file has been modified, check for clashes against origin/main.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
from pathlib import Path


def _check_changelog_clash(file: Path) -> int:
    print(file)
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

    return parser.parse_args()


def main() -> int:
    """
    Entrypoint for the check-changelog-clash hook.

    Check the current changelog (if modified) against origin/main.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    args = _parse_args()

    # Early exit if no files provided
    if len(args.files) < 1:
        return 0

    # Check each changed file
    retv = 0
    for file in args.files:
        retv |= _check_changelog_clash(file)

    return retv


if __name__ == "__main__":
    exit(main())
