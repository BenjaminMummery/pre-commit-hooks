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

DEFAULT_CONFIG_FILE: Path = Path(".add-copyright-hook-config.yaml")
DEFAULT_FORMAT: str = "# Copyright (c) {year} {name}"


def _contains_copyright_string(input: str) -> bool:
    """
    Check if the input string is a copyright comment.

    Note: at present this assumes that we're looking for a python comment.
    Future versions will extend this to include other languages.

    Args:
        input (str): The string to be checked

    Returns:
        bool: True if the input string is a copyright comment, false otherwise.
    """
    exp = re.compile(
        # The line should start with the comment escape character '#'.
        r"^(?P<commentmarker>#)\s?"
        # One or more ways of writing 'copyright': the word, the character `©`, or the
        # approximation `(c)`.
        r"(?P<signifiers>(copyright\s?|\(c\)\s?|©\s?)+)"
        # Year information - either 4 digits, or 2 sets of 4 digits separated by a dash.
        r"(?P<year>(\d{4}|\d{4}\s?-\s?\d{4})+)\s"
        # The name of the copyright holder. No restrictions on this, just take whatever
        # is left in the string as long as it's not nothing.
        r"(?P<name>.*)",
        re.IGNORECASE | re.MULTILINE,
    )
    m = re.search(exp, input)
    if m is None:
        return False
    return True


def _has_shebang(input: str) -> bool:
    """
    Check whether the input string starts with a shebang.

    Args:
        input (str): The string to check.

    Returns:
        bool: True if a shebang is found, false otherwise.
    """
    return input.startswith("#!")


def _construct_copyright_string(name: str, year: str, format: str) -> str:
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
        assert _contains_copyright_string(outstr)
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


def _ensure_copyright_string(file: Path, name: str, year: str, format: str) -> int:
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

        if _contains_copyright_string(contents):
            return 0

        copyright_string = _construct_copyright_string(name, year, format)

        print(f"Fixing file `{file}` - added line(s):\n{copyright_string}\n")

        f.seek(0, 0)
        f.write(_insert_copyright_string(copyright_string, contents))
    return 1


def _get_current_year() -> str:
    """Get the current year from the system clock."""
    today = datetime.date.today()
    return str(today.year)


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


def _resolve_year(year: t.Optional[str] = None, config: t.Optional[str] = None) -> str:
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


def _resolve_files(files: t.Union[str, t.List[str]]) -> t.List[Path]:
    """
    Convert the list of files into a list of paths.

    Args:
        files (str, List[str]): The list of changed files.

    Raises:
        FileNotFoundError: When one or more of the specified files does not
        exist.

    Returns:
        List[Path]: A list of paths coressponding to the changed files.
    """
    if isinstance(files, str):
        files = [files]

    _files: t.List[Path] = [Path(file) for file in files]

    for file in _files:
        if not os.path.isfile(file):
            raise FileNotFoundError(file)

    return _files


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
        - files (list of str): the paths to each changed file relevant to this hook.
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
    args.files = _resolve_files(args.files)

    return args


def main() -> int:
    """
    Entrypoint for the add_copyright hook.

    Check that source files contain a copyright string, and add one to files that don't.
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
