#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Apply consistent formatting rules to the setup.cfg file.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DUMMY_SECTION_HEADER: str = "DUMMY SECTION"
DUMMY_SUBSECTION_HEADER: str = "DUMMY SUBSECTION"


class ParsedSections(Dict[str, Dict[str, List[str]]]):
    """A set of parsed config sections."""

    def __init__(
        self, parsed_sections: Dict[str, Dict[str, List[str]]], source: List[str]
    ):
        self.parsed_sections = parsed_sections
        self.source = source

    @classmethod
    def parse_config(cls, lines: List[str]):
        """
        Parse the lines read in from the config file into sections.

        The configuration file
        ```
        [section]
        key1 = value1
        key2 =
            value2
            value3
        ```

        will be accessible as:

        ```python
        parsed["section"]["key1"] = [value1]
        parsed["section"]["key2"] = [value2, value3]
        ```

        Args:
            lines (list(str)): A list of config lines to parse.

        Returns:
            ParsedSections: A dict whose keys are the section headings, and whose
                values are the list of strings in that section.
        """
        # Assume
        current_section: Optional[str] = None
        current_subsection: Optional[str] = None
        subsect_dict: Dict[str, List[str]] = {}
        outdict = ParsedSections({}, lines)

        for line in lines:
            # Ignore blank lines
            if line.strip() == "":
                continue

            # Ignore comments outside the sections
            if line.startswith("#"):
                continue

            # When we hit a top-level heading, assign the completed subsection dict to
            # the previous section entry, then start a new empty section in the dict.
            if line.startswith("["):
                assert "=" not in line, f"{line} contains '='"
                assert line.strip().endswith("]"), f"{line} does not end with ']'"

                # If we were previously building a section, finalise it.
                if (
                    current_section is not None
                    and current_subsection is not None
                    and len(subsect_dict) > 0
                ):
                    outdict.parsed_sections[current_section] = subsect_dict

                # start fresh section
                subsect_dict = {}
                current_section = line.strip(" []\n")
                current_subsection = None
                continue

            # Lines that aren't indented but aren't section headings must be
            # subsections. These can either be single lines (a = b) or the beginning of
            # a multiple line subsection (a =). We parse the string into sections
            # before and after "=", using the leading string as the name of the
            # subsection and the trailing string (if there is one) as the first value.
            if not line.startswith(" ") and not line.strip().startswith("#"):
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
            if current_subsection is not None:
                subsect_dict[current_subsection].append(line.strip())

        if current_section is not None:
            outdict.parsed_sections[current_section] = subsect_dict

        return outdict

    def construct_file_contents(self) -> str:
        """
        Take the parsed config and format it as a string that we can write to a file.

        Returns:
            str: The contents to be written to the file.
        """

        outlist: List[str] = []

        # Copy over any non-parsed lines from the beginning of the file
        for line in self.source:
            # If we hit an actual heading, stop copying.
            if line.startswith("["):
                break
            outlist.append(line)

        for section_header in self.parsed_sections.keys():
            outlist.append(f"[{section_header}]")

            for subsection_header in self.parsed_sections[section_header].keys():
                vals: List[str] = self.parsed_sections[section_header][
                    subsection_header
                ]
                if len(vals) == 1:
                    outlist.append(f"{subsection_header} = {vals[0]}")
                else:
                    outlist.append(f"{subsection_header} =")
                    outlist += [f"    {val}" for val in vals]
            outlist.append("")

        return "\n".join(outlist)


class ChangeMessage(str):
    """
    Store the messages about changes to be displayed to the user.

    This class encompasses all of the formatting involved in how changes are displayed
    in stdout.
    """

    def __init__(self, label: str):
        self._removed_colour = "\033[91m"
        self._added_colour = "\033[92m"
        self._normal_colour = "\033[0m"
        self._heading: List[str] = label.splitlines()
        self._changes: List[str] = []

    def add_change(self, section_heading: str, removed: List[str], added: List[str]):
        """
        Add a change to the message.

        Args:
            section_heading (str): The section of the setup.conf file where this change
                applies.
            removed (list(str)): The line(s) removed by the change.
            added (list(str)): The line(s) added by the change.
        """
        _removed = ["    " + line for line in removed]
        _added = ["    " + line for line in added]
        _removed[0] = self._removed_colour + _removed[0]
        _removed[-1] += self._normal_colour
        _added[0] = self._added_colour + _added[0]
        _added[-1] += self._normal_colour
        self._changes.append(section_heading)
        self._changes += _removed
        self._changes += _added
        self._changes.append("")

    def __str__(self):
        return "\n".join(self._heading + self._changes)


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


def _sort_sections(config: ParsedSections, file: str) -> ParsedSections:
    """
    Ensure that the lines in each section are sorted.

    Args:
        sections (ParsedSections): The parsed configuration sections.
        file (str): A human-readable identifier for the file.

    Returns:
        ParsedSections: a sorted version of the sections argument.
    """
    unsorted_msg = ChangeMessage(f"Unsorted entries in {file}:")
    exclude_sections = ["classifiers"]
    changed: bool = False

    # Iterate through the subsections
    for section in config.parsed_sections.keys():
        for key in config.parsed_sections[section].keys():
            # Skip sections that we don't want to sort
            if key in exclude_sections:
                continue

            # Skip sections that are empty or only have a single entry
            vals: List[str] = config.parsed_sections[section][key]
            if len(vals) <= 1:
                continue

            # Make a record of comment lines and the non-comment that they precede.
            comments: List[Tuple[str, List[str]]] = []
            comment_lines: List[str] = []
            for line, next_line in zip(vals[:-1], vals[1:]):
                if not line.startswith("#"):
                    continue
                comment_lines.append(line)
                if not next_line.startswith("#"):
                    comments.append((next_line, comment_lines))
                    comment_lines = []

            # Sort the values, removing any comment lines.
            sorted_vals = sorted([line for line in vals if not line.startswith("#")])

            # Add any removed comments back in above the appropriate line
            for comment in comments:
                i_insert = sorted_vals.index(comment[0])
                sorted_vals = (
                    sorted_vals[:i_insert] + comment[1] + sorted_vals[i_insert:]
                )

            # If the section ordering has changed, add the changes to the message
            if vals != sorted_vals:
                changed = True
                config.parsed_sections[section][key] = sorted_vals

                # Add the changes to the information that gets presented to the user.
                unsorted_msg.add_change(f"[{section}]\n{key} =", vals, sorted_vals)

    if changed:
        print(unsorted_msg)

    return config


def _ensure_formatted(file: Path, modify_in_place: bool) -> int:
    """
    Ensure that the contents of the config file are correctly formatted.

    Note: we can't use configparser because it doesn't preserve comments.

    Args:
        file (path): the path to the file to be checked.

    Returns:
        int: 0 if the file is already correctly formatted, 1 otherwise.
    """
    # Read the file contents
    with open(file, "r") as f:
        original_content: str = f.read()

    # Parse the sections in the config file
    parsed_sections = ParsedSections.parse_config(original_content.splitlines())

    # Create a copy of the sections and apply the various formatting rules.
    parsed_sections = _sort_sections(parsed_sections, str(file))

    # If there are changes,
    outstr = parsed_sections.construct_file_contents()
    if outstr != original_content:
        if modify_in_place:
            with open(file, "w") as f:
                f.write(outstr)
        return 1

    return 0


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
