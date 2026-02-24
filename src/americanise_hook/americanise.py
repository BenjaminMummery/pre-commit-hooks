#!/usr/bin/env python3
# Copyright (c) 2025-2026 Benjamin Mummery
"""
Check for non-US spelling in source files, and (optionally) "correct" them.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import re

from copy import deepcopy
from pathlib import Path
from typing import Union

from src._shared import print_diff, resolvers

DICTIONARY = {
    # -se -> -ize
    "characterise": "characterize",
    "initialise": "initialize",
    "instantiater": "instantiator",
    "parametrise": "parametrize",
    "prioritise": "prioritize",
    "specialise": "specialize",
    "organise": "organize",
    # -yse -> -yze
    "analyse": "analyze",
    "catalyse": "catalyze",
    # -our -> -or
    "armour": "armor",
    "behaviour": "behavior",
    "colour": "color",
    "flavour": "flavor",
    "neighbour": "neighbor",
    # -re -> -er
    "centre": "center",
    "fibre": "fiber",
    "litre": "liter",
    # -ae, -oe -> -e
    "amoeba": "amoebae",
    "anaesthesia": "anesthesia",
    "caesium": "cesium",
    # -ce -> -se
    "defence": "defense",
    # british uses "practice" as the noun and "practise" as the verb. US uses "practice" for both.
    "practise": "practice",
    # british uses "licence" as the noun and "license" as the verb. US uses "license" for both.
    "licence": "license",
    # -ge -> -g
    "ageing": "aging",
    "acknowledgement": "acknowledgment",
    "judgement": "judgment",
    # -ogue -> -og
    "analogue": "analog",
    "dialogue": "dialog",
    # -l -> -ll
    "fulfil": "fulfill",
    "enrol": "enroll",
    "skilful": "skillful",
    # -ll -> -l
    "labelled": "labeled",
    "signalling": "signaling",
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
            f"Could not match the case of offending word '{target_string}' - using best guess '{output_string}'.",
        )
        return output_string


def _americanise(file: Path, dictionary: dict) -> int:
    """Find common non-US spellings in source files and (optionally) "correct" them."""
    with open(file, "r+") as f:
        old_content: str = f.read()

    new_content = old_content.split("\n")

    diffs = []

    for line_no, line in enumerate(new_content):
        if "pragma: no americanise" in line:
            continue
        old_line = deepcopy(line)
        for key in dictionary:
            while (match := re.search(key, line, re.IGNORECASE)) is not None:
                index = match.span()
                old_word = match.string[index[0] : index[1]]
                new_word = _copy_case(old_word, dictionary[key])

                line = line[: index[0]] + new_word + line[index[1] :]

        if old_line != line:
            diffs.append(print_diff.format_diff(old_line, line, line_no + 1))
            new_content[line_no] = line

    if (output := "\n".join(new_content)) == old_content:
        return 0

    with open(file, "w") as f:
        f.write(output)

    print(file)
    for diff in diffs:
        print(diff)

    return 1


def _construct_dictionary(word_arg: Union[str, None]) -> dict:
    """Construct the dict of accepted words from the standard dict and word arguments."""
    if word_arg is None:
        return DICTIONARY

    word_arguments = [word_arg] if isinstance(word_arg, str) else word_arg

    custom_dict = {}
    for word in word_arguments:
        map = [val.lower().strip() for val in word.split(":")]
        if len(map) != 2:
            raise ValueError(
                f"Could not parse word argument '{word_arg}'. Custom word arguments should be a in the format '[incorrect_spelling]:[correct_spelling]', for example 'initialise:initialize'.",
            )
        custom_dict[map[0]] = map[1]

    return {**DICTIONARY, **custom_dict}


def _parse_args() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of Path): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument(
        "--word",
        "-w",
        type=str,
        default=None,
        action="append",
    )

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
