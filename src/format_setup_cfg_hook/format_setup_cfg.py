#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Apply consistent formatting rules to the setup.cfg file.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
from pathlib import Path
from typing import Dict, List

DUMMY_SECTION_HEADER: str = "DUMMY SECTION"
DUMMY_SUBSECTION_HEADER: str = "DUMMY SUBSECTION"


def _parse_args() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of Path): the paths to each changed file relevant to this hook.
        - in_place (bool): True if incorrectly formatted files are to be modified,
            False otherwise.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("-i", "--in-place", action="store_true", default=False)
    args = parser.parse_args()
    args.files = [Path(file) for file in args.files]

    return args


# class UnsortedMessage(str):
#     def add_line(string: str):
#         self += string
#     def add_removed


def _parse_sections(lines: List[str]) -> dict:
    """
    Parse the config lines into sections.

    Args:
        lines (list(str)): A list of config lines to parse.

    Returns:
        dict: A dict whose keys are the section headings, and whose values are the list
            of strings in that section.
    """
    # Assume
    current_section: str = DUMMY_SECTION_HEADER
    current_subsection: str = DUMMY_SUBSECTION_HEADER
    outdict: Dict[str, Dict[str, List[str]]] = {}
    subsect_dict: Dict[str, List[str]] = {}
    for line in lines:
        # Ignore blank lines
        if line.strip() == "":
            continue

        # When we hit a top-level heading, assign the completed subsection dict to the
        # previous section entry, then start a new empty section in the dict.
        if line.startswith("["):
            assert "=" not in line, f"{line} does not contain '='"
            assert line.strip().endswith("]"), f"{line} does not end with ']'"

            # Wrap up previous section
            outdict[current_section] = subsect_dict

            # start fresh section
            subsect_dict = {}
            current_section = line.strip(" []\n")
            continue

        # Lines that aren't indented must be subsections. These can either be single
        # lines (a = b) or the beginning of a multiple line subsection (a =). We parse
        # the string into sections before and after "=", using the leading string as
        # the name of the subsection and the trailing string (if there is one) as the
        # first value.
        if not line.startswith(" "):
            # Parse the Line
            assert "=" in line, f"{line} does not contain '='"
            line = line.strip()
            if line.endswith("="):
                current_subsection = line.strip(" =")
                subsect_dict[current_subsection] = []
            else:
                split: List[str] = [
                    subline.strip() for subline in line.split(" = ", maxsplit=2)
                ]
                current_subsection = split[0]
                subsect_dict[current_subsection] = split[1:]
            continue

        # The line starts with whitespace, it is part of a subsection
        subsect_dict[current_subsection].append(line.strip())

    outdict[current_section] = subsect_dict

    return outdict


def _construct_file_contents(sections: dict) -> str:
    """
    Take the parsed config and format it as a string that we can write to a file.

    Args:
        sections (dict(dict(list[str]))): A dict whose keys are config section
            headings. values should be dicts whose keys are subsection headings, and
            whose values are lists of strings corresponding tot he values of that
            subsection.

    Returns:
        str: The contents to be written to the file.
    """
    outlist: List[str] = []

    for section_header in sections.keys():
        # Handle the dummy section - should only contain leading comments AFAIK
        if section_header == DUMMY_SECTION_HEADER:
            if len(sections[section_header]) > 0:
                for value in sections[section_header].values():
                    outlist += value
            continue

        outlist.append(f"[{section_header}]")
        for subsection_header in sections[section_header].keys():
            vals: List[str] = sections[section_header][subsection_header]
            if len(vals) == 1:
                outlist.append(f"{subsection_header} = {vals[0]}")
            else:
                outlist.append(f"{subsection_header} =")
                outlist += [f"    {val}" for val in vals]
        outlist.append("")

    return "\n".join(outlist)


def _ensure_formatted(file: Path, modify_in_place: bool) -> int:
    """
    Ensure that the contents of the config file are correctly formatted.

    Note: we can't use configparser because it doesn't preserve comments.

    Args:
        file (path): the path to the file to be checked.

    Returns:
        int: 0 if the file is already correctly formatted, 1 otherwise.
    """

    ret = 0

    unsorted_msg = f"Unsorted entries in {file}:\n"
    bad_colour = "\033[91m"
    good_colour = "\033[92m"
    end_colour = "\033[0m"

    exclude_sections = ["classifiers"]
    content: List[str]
    with open(file, "r") as f:
        content = f.readlines()

    sections = _parse_sections(content)

    # Iterate through the subsections
    for section in sections.keys():
        for key in sections[section].keys():
            # Skip sections that we don't want to sort
            if key in exclude_sections:
                continue

            # Skip sections that are empty or only have a single entry
            vals: List[str] = sections[section][key]
            if len(vals) <= 1:
                continue

            # Sort the values, writing back to the content if the sorted values are
            # different.
            sorted_vals = sorted(vals)
            if vals != sorted_vals:
                sections[section][key] = sorted_vals

                # Add the changes to the information that gets presented to the user.
                unsorted_msg += f"\n[{section}]\n{key} =" + bad_colour
                for val in vals:
                    unsorted_msg += f"\n    {val}"
                unsorted_msg += good_colour
                for val in sorted(vals):
                    unsorted_msg += f"\n    {val}"
                unsorted_msg += end_colour + "\n"
                ret |= 1

    # If there are changes, print the info to the user and, if required, overwrite the
    # file.
    if ret != 0:
        if modify_in_place:
            with open(file, "w") as f:
                f.write(_construct_file_contents(sections))

        print(unsorted_msg)

    return ret


def main() -> int:
    """
    Entrypoint for the format_setup_cfg hook.

    Parse the setup.cfg file, applying formatting rules.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    args = _parse_args()

    retv = 0
    for file in args.files:
        retv |= _ensure_formatted(file, args.in_place)

    return retv


if __name__ == "__main__":
    exit(main())
