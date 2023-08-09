#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Apply consistent formatting rules to the setup.cfg file.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import configparser
from pathlib import Path


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
    args.files = [Path(file) for file in args.files]

    return args


def _ensure_formatted(file: Path) -> int:
    """
    Ensure that the contents of the config file are correctly formatted.

    Args:
        file (path): the path to the file to be checked.

    Returns:
        int: 0 if the file is already correctly formatted, 1 otherwise.
    """
    config = configparser.ConfigParser()
    config.read(file)
    ret = 0

    unsorted_msg = f"Unsorted entries in {file}:\n"
    bad_colour = "\033[91m"
    good_colour = "\033[92m"
    end_colour = "\033[0m"

    exclude_sections = ["classifiers"]
    for section in config.sections():
        for key in config[section]:
            if key in exclude_sections:
                continue

            vals = config[section][key].strip().split("\n")
            if len(vals) <= 1:
                continue

            if vals != sorted(vals):
                unsorted_msg += f"\n[{section}]\n{key} =" + bad_colour
                for val in vals:
                    unsorted_msg += f"\n    {val}"
                unsorted_msg += good_colour
                for val in sorted(vals):
                    unsorted_msg += f"\n    {val}"
                unsorted_msg += end_colour + "\n"
                ret |= 1

    if ret != 0:
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
        retv |= _ensure_formatted(file)

    return retv


if __name__ == "__main__":
    exit(main())
