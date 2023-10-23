#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Scan source files for anything resembling a copyright string, updating dates.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""


def main():
    """
    Entrypoint for the update_copyright hook.

    Parses source files containing a copyright string, and updates the date range if it
    falls short of the current year.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    return 0
