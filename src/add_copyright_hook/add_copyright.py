#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Check that source files contain a copyright string, and add one to files that don't.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import datetime
from pathlib import Path
from typing import List, Optional, Set, Tuple

from git import GitCommandError, Repo

from src._shared.comment_mapping import get_comment_markers
from src._shared.copyright_parsing import parse_copyright_string
from src._shared.exceptions import NoCommitsError


def _get_earliest_commit_year(file: Path) -> int:
    """
    Get the years of the earliest and latest commits made to the specified file.

    Args:
        file (Path): The path to the file to be checked

    Raises:
        NoCommitsError: when the file has no commits for us to examine the blame.

    Returns:
        int: The year of the earliest commit on the file.

    """

    repo = Repo(".")

    try:
        blames = repo.blame(repo.head, str(file))
    except GitCommandError as e:
        raise NoCommitsError from e

    timestamps: Set[int] = set(
        int(blame[0].committed_date) for blame in blames  # type: ignore
    )

    earliest_date: datetime = datetime.datetime.fromtimestamp(  # type: ignore
        min(timestamps)
    )

    return int(earliest_date.year)  # type: ignore


def _parse_args() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of Path): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default=None)
    parser.add_argument("files", nargs="*", default=[])
    args = parser.parse_args()

    return args


def _get_git_user_name() -> str:
    """
    Get the user name as configured in git.

    Raises:
        ValueError: when the user name has not been configured.

    Returns:
        str: the user name
    """
    repo = Repo(".")
    reader = repo.config_reader()
    name = reader.get_value("user", "name")
    if not isinstance(name, str) or len(name) < 1:
        raise ValueError("The git username is not configured.")  # pragma: no cover
    return name


def _has_shebang(input: str) -> bool:
    """
    Check whether the input string starts with a shebang.

    Args:
        input (str): The string to check.

    Returns:
        bool: True if a shebang is found, false otherwise.
    """
    return input.startswith("#!")


def _add_copyright_string_to_content(content: str, copyright_string: str) -> str:
    """
    Insert a copyright string into the appropriate place in existing content.

    This method attempts to place the copyright string at the top of the file, unless
    the file starts with a shebang in which case the copyright string is inserted after
    the shebang, separated by an empty line.

    Args:
        content (str): The content to be updated.
        copyright_string (str): The copyright string to be inserted.

    Returns:
        str: the new content.
    """
    lines: List[str] = content.splitlines()
    new_lines: List[str] = []

    # If the file starts with a shebang, keep that first in the new content.
    if _has_shebang(content):
        new_lines += [lines[0], ""]
        lines = lines[1:]

    # Remove leading empty lines from the content
    while len(lines) >= 1 and lines[0] == "":
        lines = lines[1:]

    new_lines += [copyright_string, ""] + lines
    if not new_lines[-1] == "":
        new_lines.append("")
    return "\n".join(new_lines)


def _construct_copyright_string(
    name: str,
    start_year: int,
    end_year: int,
    format: str,
    comment_markers: Tuple[str, Optional[str]],
) -> str:
    """
    Construct a commented line containing the copyright information.

    Args:
        name (str): The name of the copyright holder.
        start_year (str): The start year of the copyright.
        end_year (str): The end year of the copyright.
        format (str): The f-string into which the name and year should be
            inserted.
        comment_markers (tuple(str, str|None)): The comment markers to be inserted
            before and, optionally, after the copyright string.

    Return:
        str: the copyright string, with appropriate comment escapes.
    """
    if start_year == end_year:
        year = f"{start_year}"
    else:
        year = f"{start_year} - {end_year}"
    outstr = f"{comment_markers[0]} {format.format(year=year, name=name)}"
    if comment_markers[1]:
        outstr += f" {comment_markers[1]}"

    return outstr


def _ensure_copyright_string(file: Path, name: Optional[str]) -> int:
    """
    Ensure that the file has a docstring.

    This function encompasses the heavy lifting for the hook.

    Args:
        file (path): the file to be checked.

    Returns:
        int: 0 if the file already had a docstring, 1 if a docstring had to be added.
    """
    with open(file, "r+") as f:
        content: str = f.read()
        comment_markers: Tuple[str, Optional[str]] = get_comment_markers(file)
        if parse_copyright_string(content, comment_markers):
            return 0

        print(f"Fixing file `{file}` ", end="")

        copyright_end_year: int = datetime.date.today().year
        copyright_start_year: int
        try:
            copyright_start_year = _get_earliest_commit_year(file)
        except NoCommitsError:
            copyright_start_year = copyright_end_year

        new_copyright_string = _construct_copyright_string(
            name or _get_git_user_name(),
            copyright_start_year,
            copyright_end_year,
            "Copyright (c) {year} {name}",
            comment_markers,
        )

        f.seek(0, 0)
        f.truncate()
        f.write(_add_copyright_string_to_content(content, new_copyright_string))
        print(f"- added line(s):\n{new_copyright_string}")
    return 1


def main():
    """
    Entrypoint for the add_copyright hook.

    Check that source files contain a copyright string, and add one to files that don't.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    args = _parse_args()

    # Early exit if no files provided
    if len(args.files) < 1:
        return 0

    # Add copyright to files that don't already have it.
    retv: int = 0
    for file in args.files:
        retv |= _ensure_copyright_string(Path(file), name=args.name)
    return retv


if __name__ == "__main__":
    exit(main())
