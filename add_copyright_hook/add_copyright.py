#!/usr/bin/env python3

import argparse


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

    return 1


if __name__ == "__main__":
    exit(main())
