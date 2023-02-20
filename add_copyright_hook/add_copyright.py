#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

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


def _contains_copyright_string(input: str) -> bool:
    """Checks if the input string is a copyright comment.

    Note: at present this assumes that we're looking for a python comment.
    Future versions will extend this to include other languages.

    Args:
        input (str): The string to be checked

    Returns:
        bool: True if the input string is a copyright comment, false otherwise.
    """
    exp = re.compile(
        r"^#\s?(?P<signifiers>copyright(\s?\(c\))?)\s(?P<year>\d{4})\s(?P<name>.*)",
        re.IGNORECASE | re.MULTILINE,
    )
    m = re.search(exp, input)
    if m is None:
        return False
    return True


def _has_shebang(input: str) -> bool:
    return input.startswith("#!")


def _construct_copyright_string(name: str, year: str) -> str:
    """Construct a commented line containing the copyright information.

    Args:
        name (str): The name of the copyright holder.
        year (str): The year of the copyright.
    """
    outstr = "# Copyright (c) {year} {name}".format(year=year, name=name)
    assert _contains_copyright_string(outstr)
    return outstr


def _insert_copyright_string(copyright: str, content: str) -> str:
    """Insert the specified copyright string as a new line in the content. This
    method attempts to place the copyright string at the top of the file, unless
    the file starts with a shebang in which case the copyright string is
    inserted after the shebang, separated by an empty line.

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


def _ensure_copyright_string(file: Path, name: str, year: str) -> int:
    with open(file, "r+") as f:
        contents: str = f.read()

        if _contains_copyright_string(contents):
            return 0

        print(f"Fixing file `{file}`")

        f.seek(0, 0)
        f.write(
            _insert_copyright_string(_construct_copyright_string(name, year), contents)
        )
    return 1


def _get_current_year() -> str:
    """Get the current year from the system clock."""
    today = datetime.date.today()
    return str(today.year)


def _get_git_user_name() -> str:
    """Get the user name as configured in git.

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
    """Resolve the user name to attach to the copyright.

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
        return data["name"]

    return _get_git_user_name()


def _resolve_year(year: t.Optional[str] = None, config: t.Optional[str] = None) -> str:
    """Resolve the year to attach to the copyright.

    If the year argument is provided, it is returned as the year. Otherwise the
    year is inferred from the system clock.

    Args:
        year (str, optional): The year argument if provided. Defaults to None.

    Returns:
        str: The resolved year.
    """
    if year is not None:
        return year

    if config is not None:
        data = _read_config_file(config)
        return data["year"]

    return _get_current_year()


def _resolve_files(files: t.Union[str, t.List[str]]) -> t.List[Path]:
    """Convert the list of files into a list of paths, and ensure that they all
    exist.

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
    """Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of str): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("-n", "--name", type=str, default=None)
    parser.add_argument("-y", "--year", type=str, default=None)
    parser.add_argument("-c", "--config", type=str, default=None)
    args = parser.parse_args()

    if args.config and (args.name or args.year):
        print("-c and -n|-y are mutually exclusive.")
        sys.exit(2)

    if args.config is None and os.path.isfile(DEFAULT_CONFIG_FILE):
        args.config = DEFAULT_CONFIG_FILE

    args.name = _resolve_user_name(args.name, args.config)
    args.year = _resolve_year(args.year, args.config)
    args.files = _resolve_files(args.files)

    return args


def main() -> int:
    args = _parse_args()

    # Early exit if no files provided
    if len(args.files) < 1:
        return 0

    # Filter out files that already have a copyright string
    retv = 0
    for file in args.files:
        retv |= _ensure_copyright_string(file, args.name, args.year)

    return retv


if __name__ == "__main__":
    exit(main())
