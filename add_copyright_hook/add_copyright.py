#!/usr/bin/env python3

import argparse
import datetime
import typing as t

from git import Repo


def _get_current_year() -> str:
    today = datetime.date.today()
    return str(today.year)


def _get_git_user_name() -> t.Union[str, None]:
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
