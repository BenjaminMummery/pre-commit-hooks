#!/usr/bin/env python3
# Copyright (c) 2025-2026 Benjamin Mummery
"""Check for non-US spelling in source files, and (optionally) "correct" them.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

from __future__ import annotations

import argparse
import re
import sys

from copy import deepcopy
from typing import TYPE_CHECKING

from src._shared import print_diff, resolvers

if TYPE_CHECKING:
    from pathlib import Path

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
    # British uses "practice" as the noun and "practise" as the verb.
    # US uses "practice" for both.
    "practise": "practice",
    # British uses "licence" as the noun and "license" as the verb.
    # US uses "license" for both.
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
    if target_string.istitle():
        return input_string.title()
    if target_string.isupper():
        return input_string.upper()
    if len(target_string) == len(input_string):
        input_string_list = list(input_string)
        for i, letter in enumerate(target_string):
            if letter.isupper():
                input_string_list[i] = input_string[i].upper()
        return "".join(input_string_list)
    input_string_list = list(input_string)
    for i in range(min([len(target_string), len(input_string)])):
        if target_string[i].isupper():
            input_string_list[i] = input_string[i].upper()
    output_string = "".join(input_string_list)
    Warning(
        f"Could not match the case of offending word '{target_string}' - "
        f"using best guess '{output_string}'.",
    )
    return output_string


def _americanise(file: Path, dictionary: dict) -> int:
    """Find common non-US spellings in source files and (optionally) "correct" them."""
    with file.open("r+") as f:
        old_content: str = f.read()

    new_content = old_content.split("\n")

    diffs = []

    for line_no, line in enumerate(new_content):
        if "pragma: no americanise" in line:
            continue
        old_line = deepcopy(line)
        updated_line = line
        for key, value in dictionary.items():
            pattern = rf"\b{re.escape(key)}\b"
            while (
                match := re.search(pattern, updated_line, re.IGNORECASE)
            ) is not None:
                index = match.span()
                old_word = match.group()
                new_word = _copy_case(old_word, value)

                updated_line = (
                    updated_line[: index[0]] + new_word + updated_line[index[1] :]
                )

        if old_line != updated_line:
            diffs.append(
                print_diff.format_diff(old_line, updated_line, line_no + 1),
            )
            new_content[line_no] = updated_line

    if (output := "\n".join(new_content)) == old_content:
        return 0

    with file.open("w") as f:
        f.write(output)

    print(file)
    for diff in diffs:
        print(diff)

    return 1


def _construct_dictionary(word_arg: str | None) -> dict:
    """Construct the dict of accepted words from the standard dict and args."""
    if word_arg is None:
        return DICTIONARY

    word_arguments = [word_arg] if isinstance(word_arg, str) else word_arg

    custom_dict = {}
    for word in word_arguments:
        mapping = [val.lower().strip() for val in word.split(":")]
        if len(mapping) != 2:
            msg = (
                f"Could not parse word argument '{word_arg}'. Custom word "
                "arguments should be in the format "
                "'[incorrect_spelling]:[correct_spelling]', for example "
                "'initialise:initialize'."
            )
            raise ValueError(msg)
        custom_dict[mapping[0]] = mapping[1]

    return {**DICTIONARY, **custom_dict}


def _parse_args() -> argparse.Namespace:
    """Parse the CLI arguments.

    Returns:
        argparse.Namespace:
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


def main() -> int:
    """Entrypoint for the americanize hook.

    Parses source files looking for common non-american spellings and either
    corrects or reports them.

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
    sys.exit(main())
