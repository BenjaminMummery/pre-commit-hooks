#!/usr/bin/env python3

# Copyright (c) 2023 - 2025 Benjamin Mummery

"""
Scan source files for anything resembling a copyright string, updating dates.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import datetime
from pathlib import Path
from typing import Optional, Tuple

from src._shared import print_diff, resolvers
from src._shared.comment_mapping import get_comment_markers
from src._shared.copyright_parsing import (
    parse_copyright_comment,
    parse_copyright_docstring,
)


def _update_copyright_dates(file: Path) -> int:
    """
    Ensure that if the file has a copyright string, the end date matches the current year.

    This function encompasses the heavy lifting for the hook.

    Args:
        file (path): the file to be checked.

    Returns:
        int: 0 if the file already had an up to date copyright string or had no
            copyright string, 1 if a copyright string had to be added.
    """
    with open(file, "r+") as f:
        content: str = f.read()
        comment_markers: Tuple[str, Optional[str]] = get_comment_markers(file)

        # Early return for no copyright string in file
        if not (
            copyright_string := parse_copyright_comment(content, comment_markers)
            or parse_copyright_docstring(content)
        ):
            return 0

        # Early return for up to date copyright string
        if copyright_string.end_year == (
            copyright_end_year := datetime.date.today().year
        ):
            return 0

        print(f"Fixing file `{file}`:")

        new_copyright_string: str
        # Generate new copyright string
        if copyright_string.start_year != copyright_string.end_year:
            # multiple dates in copyright string
            new_copyright_string = copyright_string.string.replace(
                str(copyright_string.end_year), str(copyright_end_year)
            )
        else:
            # single date in copyright string
            new_copyright_string = copyright_string.string.replace(
                str(copyright_string.end_year),
                f"{copyright_string.end_year}-{copyright_end_year}",
            )

        f.seek(0, 0)
        f.truncate()
        f.write(content.replace(copyright_string.string, new_copyright_string))

        print(print_diff.format_diff(copyright_string.string, new_copyright_string))

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
    Entrypoint for the update_copyright hook.

    Parses source files containing a copyright string, and updates the date range if it
    falls short of the current year.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    files = _parse_args().files

    retv: int = 0
    for file in files:
        retv |= _update_copyright_dates(file)

    return retv


if __name__ == "__main__":
    exit(main())
