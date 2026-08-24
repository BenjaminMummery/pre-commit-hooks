#!/usr/bin/env python3
# Copyright (c) 2023 - 2026 Benjamin Mummery
"""Scan source files for anything resembling a copyright string, updating dates.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

from __future__ import annotations

import argparse
import os
import sys

from typing import TYPE_CHECKING

from git import GitCommandError, Repo

from src._shared import print_diff, resolvers
from src._shared.comment_mapping import get_comment_markers
from src._shared.copyright_parsing import (
    parse_copyright_comment,
    parse_copyright_docstring,
)

if TYPE_CHECKING:
    from pathlib import Path


def _get_commit_year_range(
    file: Path,
    revision: str = "HEAD",
) -> tuple[int, int] | None:
    """Return the earliest and latest committer years in a file's history.

    The existing copyright range is treated as authoritative when history is
    incomplete. This function therefore reports only the history that is locally
    available; callers must not use it to shorten an existing range.

    Args:
        file (Path): the file whose history should be inspected.
        revision (str): the committed revision at which to inspect its history.

    Returns:
        tuple[int, int] | None: the earliest and latest committer years, or None
            when no history is available.
    """
    repo = Repo(".")
    try:
        output = repo.git.log(
            revision,
            "--follow",
            "--format=%cs",
            "--",
            str(file),
        )
    except GitCommandError:
        return None

    years = [int(line[:4]) for line in output.splitlines() if line]
    if not years:
        return None
    return min(years), max(years)


def _update_copyright_dates(file: Path, revision: str = "HEAD") -> int:
    """Ensure the file copyright range covers its committed history.

    This function encompasses the heavy lifting for the hook.

    Args:
        file (Path): the file to be checked.
        revision (str): the committed revision whose history should be inspected.

    Returns:
        int: 0 if the file already had an up-to-date copyright string or had no
            copyright string, 1 if its copyright range was updated.
    """
    with file.open("r+") as f:
        content: str = f.read()
        comment_markers: tuple[str, str | None] = get_comment_markers(file)

        # Early return for no copyright string in file
        if not (
            copyright_string := parse_copyright_comment(content, comment_markers)
            or parse_copyright_docstring(content)
        ):
            return 0

        if not (history_range := _get_commit_year_range(file, revision)):
            return 0

        history_start_year, history_end_year = history_range
        copyright_start_year = min(copyright_string.start_year, history_start_year)
        copyright_end_year = max(copyright_string.end_year, history_end_year)

        # Early return when the declared range already covers all available history.
        if (
            copyright_string.start_year == copyright_start_year
            and copyright_string.end_year == copyright_end_year
        ):
            return 0

        print(f"Fixing file `{file}`:")

        new_copyright_string: str
        # Generate new copyright string
        new_copyright_string = copyright_string.string.replace(
            str(copyright_string.start_year),
            str(copyright_start_year),
            1,
        )
        if copyright_string.start_year != copyright_string.end_year:
            # Preserve the existing separator and whitespace around the date range.
            new_copyright_string = new_copyright_string.replace(
                str(copyright_string.end_year),
                str(copyright_end_year),
                1,
            )
        elif copyright_start_year != copyright_end_year:
            new_copyright_string = new_copyright_string.replace(
                str(copyright_start_year),
                f"{copyright_start_year}-{copyright_end_year}",
                1,
            )

        f.seek(0, 0)
        f.truncate()
        f.write(content.replace(copyright_string.string, new_copyright_string))

        print(
            print_diff.format_diff(
                copyright_string.string,
                new_copyright_string,
            ),
        )

        return 1


def _parse_args() -> argparse.Namespace:
    """Parse the CLI arguments.

    Returns:
        argparse.Namespace:
        - files (list of Path): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])

    args = parser.parse_args()

    # Check that files exist
    args.files = resolvers.resolve_files(args.files)

    return args


def main() -> int:
    """Entrypoint for the update_copyright hook.

    Parse source files containing a copyright string and extend their date ranges to
    cover the available commit history.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    files = _parse_args().files

    revision = os.environ.get("PRE_COMMIT_TO_REF", "HEAD")
    if revision != "HEAD":
        repo = Repo(".")
        if repo.head.commit.hexsha != repo.commit(revision).hexsha:
            msg = (
                "update-copyright can only modify the checked-out revision. "
                f"The pushed revision is {revision}, but HEAD is "
                f"{repo.head.commit.hexsha}. Check out the branch being pushed "
                "and retry."
            )
            raise RuntimeError(msg)

    retv: int = 0
    for file in files:
        retv |= _update_copyright_dates(file, revision)

    return retv


if __name__ == "__main__":
    sys.exit(main())
