#!/usr/bin/env python3

import argparse
import datetime
import os
import re
import typing as t
from pathlib import Path

from git import Repo


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


def _resolve_user_name(name: t.Optional[str] = None) -> str:
    """Resolve the user name to attach to the copyright.

    If the name argument is provided, it is returned as the username. Otherwise
    the user name is inferred from the git configuration.

    Args:
        name (str, optional): The name argument if provided. Defaults to None.

    Raises:
        ValueError: When the name argument is not provided, and the git user
        name is not configured.

    Returns:
        str: The resolved name.
    """
    if name is not None:
        return name
    try:
        return _get_git_user_name()
    except ValueError as e:
        raise e


def _resolve_year(year: t.Optional[str] = None) -> str:
    """Resolve the year to attach to the copyright.

    If the year argument is provided, it is returned as the year. Otherwise the
    year is inferred from the system clock.

    Args:
        year (str, optional): The year argument if provided. Defaults to None.

    Returns:
        str: The resolved year.
    """
    return year or _get_current_year()


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

    _files: t.List[Path] = [Path(file).absolute() for file in files]

    for file in _files:
        if not os.path.isfile(file):
            raise FileNotFoundError(file)

    return _files


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
    parser.add_argument("-f", "--format", type=str, default=None)
    args = parser.parse_args()

    args.name = _resolve_user_name(args.name)
    args.year = _resolve_year(args.year)
    args.files = _resolve_files(args.files)

    return args


def main() -> int:
    args = _parse_args()

    # Early exit if no files provided
    if len(args.files) < 1:
        return 0

    # Resolve the copyright holder name
    name = args.name or _get_git_user_name()

    # Filter out files that already have a copyright string
    for file in args.files:
        print(file, name)

    return 1


if __name__ == "__main__":
    exit(main())
