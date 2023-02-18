#!/usr/bin/env python3

import argparse
import datetime
import typing as t

from git import Repo


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


def _parse_args() -> argparse.Namespace:
    """Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of str): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("-n", "--name", type=str, default=None)
    args = parser.parse_args()

    if isinstance(args.files, str):
        args.files = [args.files]
    return args


def main() -> int:
    args = _parse_args()

    for file in args.files:
        print(file)

    print(_get_git_user_name())

    return 1


if __name__ == "__main__":
    exit(main())
