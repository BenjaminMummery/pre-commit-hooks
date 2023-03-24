#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Check that source files contain a copyright string, and add one to files that don't.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import datetime
import json
import os
import re
import sys
import typing as t
from pathlib import Path

import yaml
from git import Repo

from src._shared import resolvers

DEFAULT_CONFIG_FILE: Path = Path(".add-copyright-hook-config.yaml")
DEFAULT_FORMAT: str = "# Copyright (c) {year} {name}"


class ParsedCopyrightString:
    """Class for storing the components of a parsed copyright string."""

    def __init__(
        self,
        commentmarker: str,
        signifiers: str,
        start_year: int,
        end_year: int,
        name: str,
        string: str,
    ):
        """
        Construct ParsedCopyrightString.

        Arguments:
            commentmarker (str): The character(s) that denote that the line is a
                comment.
            signifiers (str): The string that indicates that this comment relates to
                copyright.
            start_year (int): The earlier year attached to the copyright.
            end_year (int): The later year attached to the copyright.
            name (str): The name of the copyright holder.
            string (str): The full copyright string as it exists in the source file.
        """
        self.commentmarker: str = commentmarker
        self.signifiers: str = signifiers
        self.start_year: int = start_year
        self.end_year: int = end_year
        self.name: str = name
        self.string: str = string


def _parse_copyright_string(input: str) -> t.Optional[ParsedCopyrightString]:
    """
    Check if the input string is a copyright comment.

    Note: at present this assumes that we're looking for a python comment.
    Future versions will extend this to include other languages.

    Args:
        input (str): The string to be checked

    Returns:
        ParsedCopyrightString or None: If a matching copyright string was found,
            returns an object containing its information. If a match was not found,
            returns None.
    """
    exp = re.compile(
        # The line should start with the comment escape character '#'.
        r"^(?P<commentmarker>#)\s?"
        # One or more ways of writing 'copyright': the word, the character `©`, or the
        # approximation `(c)`.
        r"(?P<signifiers>(copyright\s?|\(c\)\s?|©\s?)+)"
        # Year information - either 4 digits, or 2 sets of 4 digits separated by a dash.
        r"(?P<year>(\d{4}\s?-\s?\d{4}|\d{4})+)" r"\s*"
        # The name of the copyright holder. No restrictions on this, just take whatever
        # is left in the string as long as it's not nothing.
        r"(?P<name>.*)",
        re.IGNORECASE | re.MULTILINE,
    )
    match = re.search(exp, input)
    if match is None:
        return None

    matchdict = match.groupdict()
    start_year, end_year = _parse_years(matchdict["year"])

    return ParsedCopyrightString(
        matchdict["commentmarker"],
        matchdict["signifiers"],
        start_year,
        end_year,
        matchdict["name"],
        match.group().strip(),
    )


def _parse_years(year: str) -> t.Tuple[int, int]:
    """
    Parse the identified year string as a range of years.

    Arguments:
        year (str): the string to be parsed.

    Returns:
        int, int: the start and end yers of the range. If the range is a single year,
            these values will be the same.

    Raises:
        SyntaxError: When the year string cannot be parsed.
    """
    match = re.match(r"^(?P<start_year>(\d{4}))\s*-\s*(?P<end_year>(\d{4}))", year)
    if match:
        return (
            int(match.groupdict()["start_year"]),
            int(match.groupdict()["end_year"]),
        )

    match = re.match(r"^(?P<year>(\d{4}))$", year)
    if match:
        return (int(match.groupdict()["year"]), int(match.groupdict()["year"]))

    raise SyntaxError(f"Could not interpret year value '{year}'.")


def _update_copyright_string(parsed_string: ParsedCopyrightString, year: int):
    """
    Update the end year in the copyright string to match the specified year.

    If the string contains a year range, updates the later year. If it contains a single
    year, converts this to a year range.

    Arguments:
        parsed_string (ParsedCopyrightString): The copyright string to be updated.
        year (int): The year to be inserted.
    """
    if parsed_string.end_year == parsed_string.start_year:
        return parsed_string.string.replace(
            str(parsed_string.start_year), f"{parsed_string.start_year} - {year}"
        )
    return parsed_string.string.replace(str(parsed_string.end_year), str(year))


def _has_shebang(input: str) -> bool:
    """
    Check whether the input string starts with a shebang.

    Args:
        input (str): The string to check.

    Returns:
        bool: True if a shebang is found, false otherwise.
    """
    return input.startswith("#!")


def _construct_copyright_string(name: str, year: int, format: str) -> str:
    """
    Construct a commented line containing the copyright information.

    Args:
        name (str): The name of the copyright holder.
        year (str): The year of the copyright.
        format (str): The f-string into which the name and year should be
            inserted.
    """
    outstr = format.format(year=year, name=name)
    if format == DEFAULT_FORMAT:
        assert _parse_copyright_string(outstr)
    return outstr


def _insert_copyright_string(copyright: str, content: str) -> str:
    """
    Insert the specified copyright string as a new line in the content.

    This method attempts to place the copyright string at the top of the file, unless
    the file starts with a shebang in which case the copyright string is inserted after
    the shebang, separated by an empty line.

    Args:
        copyright (str): The copyright string.
        content (str): The content into which to insert the copyright string.

    Returns:
        str: The modified content, including the copyright string.
    """
    lines: list = [line for line in content.split("\n")]

    shebang: t.Optional[str] = None
    if _has_shebang(content):
        shebang = lines[0]
        lines = lines[1:]

    if lines[0] == "":
        lines = [copyright] + lines
    else:
        lines = [copyright, ""] + lines

    if shebang is not None:
        lines = [shebang, ""] + lines

    return "\n".join(lines)


def _ensure_copyright_string(file: Path, name: str, year: int, format: str) -> int:
    """
    Ensure that the specified file has a copyright string.

    Check the file contents for the presence a copyright string, adding one if it is
    not already present.

    Args:
        file (Path): the file to check.
        name (str): Name of the copyright holder to be added to uncopyrighted
            files.
        year (str): Year of the copyright to be added to uncopyrighted files.
        format (str): f-string specifying the structure of new copyright
            strings.

    Returns:
        int: 0 if the file is unchanged, 1 if it was modified.
    """
    with open(file, "r+") as f:
        contents: str = f.read()

        parsed_copyright_string = _parse_copyright_string(contents)

        if parsed_copyright_string:
            if parsed_copyright_string.end_year >= int(year):
                # Case 1: The file already has an up-to-date copyright string, nothing
                # to do.
                return 0

            # Case 2: The file has a copyright string, but it needs updating to cover
            # the current year.
            copyright_string = _update_copyright_string(parsed_copyright_string, year)
            print(
                f"Fixing file `{file}` - updating existing copyright string:\n "
                f"`{parsed_copyright_string.string}` --> `{copyright_string}`\n"
            )

            new_contents = contents.replace(
                parsed_copyright_string.string, copyright_string
            )
            f.seek(0, 0)
            f.truncate()
            f.write(new_contents)
            return 1

        # Case 3: The file has no copyright string, so we need to add one.
        copyright_string = _construct_copyright_string(name, year, format)
        print(f"Fixing file `{file}` - added line(s):\n{copyright_string}\n")
        f.seek(0, 0)
        f.write(_insert_copyright_string(copyright_string, contents))
    return 1


def _get_current_year() -> int:
    """Get the current year from the system clock."""
    today = datetime.date.today()
    return today.year


def _get_git_user_name() -> str:
    """
    Get the user name as configured in git.

    Raises:
        ValueError: when the user name has not been configured.

    Returns:
        str: the user name
    """
    repo = Repo(".")
    reader = repo.config_reader()
    name: str = reader.get_value("user", "name")
    if len(name) < 1:
        raise ValueError("The git username is not configured.")
    return name


def _resolve_user_name(
    name: t.Optional[str] = None, config: t.Optional[str] = None
) -> str:
    """
    Resolve the user name to attach to the copyright.

    If the name argument is provided, it is returned as the username. Otherwise
    the user name is inferred from the git configuration.

    Args:
        name (str, optional): The name argument if provided. Defaults to None.
        config (str, optional): The config argument if provided. Defaults to None.

    Raises:
        ValueError: When the name argument is not provided, no config file is provided,
        and the git user name is not configured.

    Returns:
        str: The resolved name.
    """
    if name is not None:
        return name

    if config is not None:
        data = _read_config_file(config)
        if "name" in data:
            return data["name"]

    return _get_git_user_name()


def _resolve_year(year: t.Optional[int] = None, config: t.Optional[str] = None) -> int:
    """
    Resolve the year to attach to the copyright.

    If the year argument is provided, it is returned as the year. Otherwise the
    year is inferred from the system clock.

    Args:
        year (str, optional): The year argument if provided. Defaults to None.
        config (str, optional): The config argument if provided. Defaults to None.

    Returns:
        str: The resolved year.
    """
    if year is not None:
        return year

    if config is not None:
        data = _read_config_file(config)
        if "year" in data:
            return data["year"]

    return _get_current_year()


def _ensure_valid_format(format: str) -> str:
    """
    Ensure that the provided format string contains the required keys.

    Args:
        format (str): The string to be checked.

    Raises:
        KeyError: when one or more keys is missing.

    Returns:
        str: the checked format string.
    """
    keys = ["name", "year"]
    missing_keys = []
    for key in keys:
        if "{" + key + "}" not in format:
            missing_keys.append(key)
    if len(missing_keys) > 0:
        raise KeyError(
            f"The format string '{format}' is missing the following required keys: "
            f"{missing_keys}"
        )
    return format


def _resolve_format(
    format: t.Optional[str] = None, config: t.Optional[str] = None
) -> str:
    """
    Resolve the format with which the copyright string should be constructed.

    Args:
        format (str, optional): The format argument if provided. Defaults to None.
        config (str, optional): The config argument if provided. Defaults to None.

    Returns:
        str: The resolved format.
    """
    if format is not None:
        return _ensure_valid_format(format)

    if config is not None:
        data = _read_config_file(config)
        if "format" in data:
            return _ensure_valid_format(data["format"])
        print(f"Config file `{config}` has no format field.")

    return _ensure_valid_format(DEFAULT_FORMAT)


def _read_config_file(file_path: str) -> dict:
    """
    Read in the parameters from the specified configuration file.

    Args:
        file_path (str): The path to the file.

    Raises:
        FileNotFoundError: when the path does not point to an extant file, or points to
            a file of an unsupported type.

    Returns:
        dict: The key values pairs interpreted from the file's contents.
    """
    _file_path = Path(file_path)
    data: dict
    with open(_file_path, "r") as f:
        if _file_path.suffix == ".json":
            data = json.load(f)
        elif _file_path.suffix == ".yaml":
            data = yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"{file_path} is not a valid config file.")

    return data


def _parse_args() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of Path): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("-n", "--name", type=str, default=None)
    parser.add_argument("-y", "--year", type=str, default=None)
    parser.add_argument("-f", "--format", type=str, default=None)
    parser.add_argument("-c", "--config", type=str, default=None)
    args = parser.parse_args()

    if args.config and (args.name or args.year or args.format):
        print("The arguments -c and -n|-y|-f are mutually exclusive.")
        sys.exit(2)

    if args.config is None and os.path.isfile(DEFAULT_CONFIG_FILE):
        args.config = DEFAULT_CONFIG_FILE
        print(f"Found config file `{args.config}`.")

    args.name = _resolve_user_name(args.name, args.config)
    args.year = _resolve_year(args.year, args.config)
    args.format = _resolve_format(args.format, args.config)
    args.files = resolvers._resolve_files(args.files)

    return args


def main() -> int:
    """
    Entrypoint for the add_copyright hook.

    Check that source files contain a copyright string, and add one to files that don't.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    args = _parse_args()

    # Early exit if no files provided
    if len(args.files) < 1:
        return 0

    # Filter out files that already have a copyright string
    retv = 0
    for file in args.files:
        retv |= _ensure_copyright_string(file, args.name, args.year, args.format)

    return retv


if __name__ == "__main__":
    exit(main())
