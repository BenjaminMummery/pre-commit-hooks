#!/usr/bin/env python3

# Copyright (c) 2025 Benjamin Mummery

"""
Check for non-US spelling in source files, and (optionally) "correct" them.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import re
from pathlib import Path

from src._shared import resolvers

DICTIONARY = {
    "initialise": "initialize",
    "instantiater": "instantiator",
    "parametrise": "parametrise",
    "armour": "armor",
}


def _copy_case(target_string: str, input_string: str) -> str:
    """Format the input string to match the case of the target string."""
    input_string = input_string.lower()

    # Identify case
    if target_string.islower():
        return input_string.lower()
    elif target_string.istitle():
        return input_string.title()
    elif target_string.isupper():
        return input_string.upper()
    elif len(target_string) == len(input_string):
        input_string_list = list(input_string)
        for i, letter in enumerate(target_string):
            if letter.isupper():
                input_string_list[i] = input_string[i].upper()
        return "".join(input_string_list)
    else:
        input_string_list = list(input_string)
        for i in range(min([len(target_string), len(input_string)])):
            if target_string[i].isupper():
                input_string_list[i] = input_string[i].upper()
        output_string = "".join(input_string_list)
        Warning(
            f"Could not match the case of offending word '{target_string}' - using best guess '{output_string}'."
        )
        return output_string


def _americanise(file: Path, dictionary: dict[str, str]) -> int:
    """Find common non-US spellings in source files and (optionally) "correct" them."""
    with open(file, "r+") as f:
        old_content: str = f.read()

    new_content = old_content
    for key in dictionary:
        while (match := re.search(key, new_content, re.IGNORECASE)) is not None:
            index = match.span()

            new_content = (
                new_content[: index[0]]
                + _copy_case(match.string[index[0] : index[1]], dictionary[key])
                + new_content[index[1] :]
            )
    if new_content == old_content:
        return 0

    with open(file, "w") as f:
        f.write(new_content)

    return 1


def _construct_dictionary(word_arg: str | None) -> dict[str | str]:
    """Construct the dict of accepted words from the standard dict and word arguments."""
    if word_arg is None:
        return DICTIONARY

    words = [word.lower().strip() for word in word_arg.split(":")]
    if len(words) != 2:
        raise ValueError(
            f"Could not parse word argument '{word_arg}'. Custom word arguments should be a in the format '[incorrect_spelling]:[correct_spelling]', for example 'initialise:initialize'."
        )

    return DICTIONARY | {words[0]: words[1]}


def _parse_args() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of Path): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("--word", "-w", type=str, default=None)

    args = parser.parse_args()

    # Check that files exist
    args.files = resolvers.resolve_files(args.files)

    args.dictionary = _construct_dictionary(args.word)

    return args


def main():
    """
    Entrypoint for the americanize hook.

    Parses source files looking for common non-american spellings and either corrects or reports them.

    Returns:
        int: 1 if incorrect spellings were found, 0 otherwise.
    """
    args = _parse_args()
    files = args.files

    retv: int = 0
    for file in files:
        retv |= _americanise(file, args.dictionary)

    return retv


if __name__ == "__main__":
    exit(main())
