#!/usr/bin/env python3

import argparse

from git import Repo


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
    if len(name) == 0:
        raise ValueError("Git user name is not set.")
    return name


def _parse_args() -> argparse.Namespace:
    """Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of str): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
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
