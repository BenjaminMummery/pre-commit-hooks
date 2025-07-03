# Copyright (c) 2025 Benjamin Mummery

"""Utilities for printing the differences between lines with nice formatting."""

from difflib import ndiff
from typing import Union

REMOVED_COLOUR: str = "\033[91m"
ADDED_COLOUR: str = "\033[92m"
END_COLOUR: str = "\033[0m"


def format_diff(old_line: str, new_line: str, line_number: Union[int, None] = None):
    """Print the old and new lines, highlighting any differences between them."""
    printline_old = ""
    printline_new = ""

    for change in ndiff(old_line, new_line):
        if change.startswith(" "):
            printline_old += change[2:]
            printline_new += change[2:]
        elif change.startswith("+"):
            printline_new += f"{ADDED_COLOUR}{change[2:]}{END_COLOUR}"
        elif change.startswith("-"):
            printline_old += f"{REMOVED_COLOUR}{change[2:]}{END_COLOUR}"

    output = ""

    if line_number is not None:
        output += f"  line {line_number}:\n"
    output += f"  - {printline_old}\n"
    output += f"  + {printline_new}"

    return output
