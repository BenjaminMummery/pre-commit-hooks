#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Check that source files contain a copyright string, and add one to files that don't.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""


def main():
    """
    Entrypoint for the add_copyright hook.

    Check that source files contain a copyright string, and add one to files that don't.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    return 0


if __name__ == "__main__":
    exit(main())
