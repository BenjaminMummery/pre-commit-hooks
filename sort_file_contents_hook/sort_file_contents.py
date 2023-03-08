#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Sort file contents while preserving section structure.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import typing as t
from pathlib import Path

from _shared import resolvers


def _sort_lines(lines: t.List[str]) -> t.List[str]:
    """Sorts the lines."""

    def _ignore_comments_in_section(input: str) -> str:
        """Key function for sorting section entries."""
        output = input.strip().lower()
        if output.startswith("#"):
            output = output[1:].strip()
        return output

    return sorted(lines, key=_ignore_comments_in_section)


def _separate_leading_comment(
    lines: t.List[str],
) -> t.Tuple[t.Union[t.List[str], None], t.Union[t.List[str], None]]:
    """
    Separate a leading comment string or strings from a list of strings.

    Arguments:
        lines (list of str): the lines to be parsed.

    Returns:
        list of str (optional), list of str (optional): the list of comment lines and
            sortable lines respectively. If no lines of the specified type were found,
            returns None.
    """
    comment_lines: t.Optional[t.List[str]] = None
    sortable_lines: t.Optional[t.List[str]] = None

    for i, line in enumerate(lines):
        if not line.startswith("#"):
            sortable_lines = lines[i:]
            break

        if comment_lines is None:
            comment_lines = [line]
        else:
            comment_lines.append(line)

    return comment_lines, sortable_lines


def _identify_sections(lines: t.List[str]) -> t.List[t.List[str]]:
    """
    Break down a list of strings into "sections".

    Sections are assumed to be a series of one or more lines separated from other
    sections by one or more empty line.

    Arguments:
        lines (list of str): the lines to be parsed.

    Returns:
        list of list of str: a list whose entries correspond to the individual
            sections. Each entry contains a list of the lines that make up that section.
    """
    blank_lines = ["\n", ""]

    # Early exit for empty file
    if len(lines) < 2:
        return [[line for line in lines if line not in blank_lines]]

    # Ensure we have a blank line at the beginning and end:
    _lines = lines
    if _lines[0] not in blank_lines:
        _lines = ["\n"] + _lines
    if _lines[-1] not in blank_lines:
        _lines = _lines + ["\n"]

    # find linebreaks
    linebreaks = [i for i, line in enumerate(_lines) if line in blank_lines]

    # Iterate through linebreaks separating out the sections
    sections = []
    for current, next in zip(linebreaks[0:-1], linebreaks[1:]):
        if next - current == 1:
            continue
        sections.append(_lines[current + 1 : next])

    return sections


def _sort_contents(file: Path):
    """Sort the contents of the file."""
    with open(file, "r") as file_obj:
        lines = list(file_obj)

    # Identify sections
    sections = _identify_sections(lines)

    # Sort each section
    sections_changed = False
    for i, section in enumerate(sections):
        # Remove leading comment
        comment_lines, sortable_lines = _separate_leading_comment(section)

        # Skip this section if there's nothing to sort
        if sortable_lines is None:
            continue

        # Sort the lines
        sorted = _sort_lines(sortable_lines)

        # Skip this section if sorting hasn't changed anything
        if sorted == sortable_lines:
            continue

        sections_changed |= True
        if comment_lines is not None:
            sorted = comment_lines + sorted
        sections[i] = sorted

    # Early return if nothing has changed
    if not sections_changed:
        return 0

    # write back to file
    with open(file, "w") as file_obj:
        file_obj.write("\n".join(["".join(section) for section in sections]))
    return 1


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
        file_retv = _sort_contents(file)
        if file_retv:
            print(f"Sorting file '{file}'")
        retv |= file_retv

    return retv


if __name__ == "__main__":
    raise SystemExit(main())
