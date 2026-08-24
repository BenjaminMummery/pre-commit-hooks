#!/usr/bin/env python3
# Copyright (c) 2023 - 2026 Benjamin Mummery
"""Sort file contents while preserving section structure.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

from __future__ import annotations

import argparse
import collections
import itertools
import typing as t

from src._shared import resolvers

if t.TYPE_CHECKING:
    from pathlib import Path


class UnsortableError(BaseException):
    """Raised when a file cannot be sorted."""


def _sort_lines(lines: list[str], unique: bool = False) -> list[str]:
    """Sorts the lines.

    Arguments:
        lines (list[str]): the lines to be sorted.

    Keyword Arguments:
        unique (bool): If True, duplicate values will be removed. (default: {False})

    Returns:
        list[str]: the sorted lines.
    """
    if unique:
        lines = list(set(lines))

    def _ignore_comments_in_section(text: str) -> str:
        """Key function for sorting section entries."""
        output = text.strip().lower()
        if output.startswith("#"):
            output = output[1:].strip()
        return output

    return sorted(lines, key=_ignore_comments_in_section)


def _separate_leading_comment(
    lines: list[str],
) -> tuple[list[str] | None, list[str] | None]:
    """Separate a leading comment string or strings from a list of strings.

    Arguments:
        lines (list[str]): the lines to be parsed.

    Returns:
        tuple[list[str] | None, list[str] | None]: the list of comment lines and
            sortable lines respectively. If no lines of the specified type were found,
            returns None.
    """
    comment_lines: list[str] | None = None
    sortable_lines: list[str] | None = None

    for i, line in enumerate(lines):
        if not line.startswith("#"):
            sortable_lines = lines[i:]
            break

        if comment_lines is None:
            comment_lines = [line]
        else:
            comment_lines.append(line)

    return comment_lines, sortable_lines


def _identify_sections(lines: list[str]) -> list[list[str]]:
    """Break down a list of strings into "sections".

    Sections are assumed to be a series of one or more lines separated from other
    sections by one or more empty line.

    Arguments:
        lines (list[str]): the lines to be parsed.

    Returns:
        list[list[str]]: a list whose entries correspond to the individual
            sections. Each entry contains a list of the lines that make up that section.
    """
    blank_lines = ["\n", ""]

    # Early exit for empty or single line file
    if len(lines) < 2:
        return [[line for line in lines if line not in blank_lines]]

    # Ensure we have a blank line at the beginning and end:
    _lines = lines
    if _lines[0] not in blank_lines:
        _lines = ["\n", *_lines]
    if _lines[-1] not in blank_lines:
        _lines = [*_lines, "\n"]

    # find linebreaks
    linebreaks = [i for i, line in enumerate(_lines) if line in blank_lines]

    # Iterate through linebreaks separating out the sections
    sections = []
    for current, next_line in zip(linebreaks[0:-1], linebreaks[1:]):
        if next_line - current == 1:
            continue
        sections.append(_lines[current + 1 : next_line])

    return sections


def _find_duplicates(lines: list[str]) -> list[tuple[str, int]]:
    """Identify duplicate entries in the list.

    'None' entries are not counted as duplicates.

    Arguments:
        lines (list[str]): the list of strings to check for duplicates.

    Returns:
        list[tuple[str, int]]: a list of tuples containing the duplicated string, and
            the number of instances within the lines.
    """
    return [
        (item, count) for item, count in collections.Counter(lines).items() if count > 1
    ]


def _find_comment_clashes(lines: list[str]) -> list[str]:
    """Identify duplicate entries in the list where one of the entries is commented out.

    Args:
        lines (list[str]): the list of strings to check for duplicates.

    Returns:
        list[str]: a list of duplicated strings.
    """
    lines = [line.strip(" #") for line in lines]
    duplicates = _find_duplicates(lines)
    return [duplicate[0] for duplicate in duplicates]


def _sort_contents(file: Path, unique: bool = False) -> int:
    """Sort the contents of the file."""
    with file.open() as file_obj:
        lines: list[str] = [line.strip("\n") for line in list(file_obj)]

    # Identify sections
    sections: list[list[str]] = _identify_sections(lines)

    # Separate leading comments from sections
    section_headers: list[list[str] | None] = [None for _ in sections]
    section_contents: list[list[str] | None] = [None for _ in sections]
    for i, section in enumerate(sections):
        section_headers[i], section_contents[i] = _separate_leading_comment(
            section,
        )

    # Sort each section
    sections_changed: bool = False
    for i, section_lines in enumerate(section_contents):
        if section_lines is None:
            continue

        sorted_lines = _sort_lines(section_lines, unique=unique)

        # Skip this section if sorting hasn't changed anything
        if sorted_lines == section_lines:
            continue

        # Update the section contents
        sections_changed |= True
        section_contents[i] = sorted_lines

    # Check for uniqueness
    if unique:
        duplicates: list[tuple[str, int]] = _find_duplicates(
            list(
                itertools.chain.from_iterable(
                    [contents for contents in section_contents if contents is not None],
                ),
            ),
        )
        if len(duplicates) > 0:
            err_msg = (
                f"Could not sort '{file}'. "
                "The following entries appear in multiple sections:"
            )
            for item, count in duplicates:
                err_msg += f"\n- '{item}' appears in {count} sections."
            raise UnsortableError(err_msg)

        comment_clashes: list[str] = _find_comment_clashes(
            list(
                itertools.chain.from_iterable(
                    [contents for contents in section_contents if contents is not None],
                ),
            ),
        )
        if len(comment_clashes) > 0:
            err_msg = (
                f"Could not sort '{file}'. "
                "The following entries exists in both commented and uncommented forms:"
            )
            for item in comment_clashes:
                err_msg += f"\n- '{item}'."
            raise UnsortableError(err_msg)

    # Early return if nothing has changed
    if not sections_changed:
        return 0

    with file.open("w") as file_obj:
        file_obj.write(
            "\n\n".join(
                [
                    "\n".join(section)
                    for section in [
                        (header or []) + (contents or [])
                        for header, contents in zip(section_headers, section_contents)
                    ]
                ],
            )
            + "\n",
        )
    print(f"Sorting file '{file}'")
    return 1


def _parse_args() -> argparse.Namespace:
    """Parse the CLI arguments.

    Returns:
        argparse.Namespace:
        - files (list of Path): the paths to each changed file relevant to this hook.
        - unique (bool): True if the unique CLI flag was set, False otherwise.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--unique",
        action="store_true",
        default=False,
        help="Ensure that all entries in the file are unique.",
    )
    parser.add_argument("files", nargs="*", default=[], help="Files to sort.")
    args = parser.parse_args()

    # Check that files exist
    args.files = resolvers.resolve_files(args.files)

    return args


def main() -> int:
    """Entrypoint for the sort_file_contents hook.

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
        retv |= _sort_contents(file, unique=args.unique)

    return retv


if __name__ == "__main__":
    raise SystemExit(main())
