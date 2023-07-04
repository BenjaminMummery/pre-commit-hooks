# Copyright (c) 2023 Benjamin Mummery

"""
If the CHANGELOG file has been modified, check for clashes against origin/main.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
from pathlib import Path
from typing import List, NamedTuple

import git


class FileComparison(NamedTuple):
    """
    Encompasses the comparison between two versions of a file.

    Properties:
        local (list[str]): The lines in the local version of the file.
        remote (list[str]): The lines in the remote version of the file.
        has_changes (bool): True if the files are different, False otherwise.
    """

    local: List[str]
    remote: List[str]
    has_changes: bool


def _get_changes(file: Path) -> FileComparison:
    """
    Get the difference between the current index and the remote.

    Assumes that the remote is 'origin' and the branch to which to compare is 'main'.

    Args:
        file (Path): the file to compare between the local and remote.

    Returns:
        A FileComparison object with 'local' and 'remote' properties which contain
            lists of the lines in the file in each case. These contain the full
            contents of both files if there are differences, or are empty if there are
            no changes.
    """

    # Get the diff for the specified file
    repo = git.Repo(".")
    repo.remotes.origin.fetch()
    # TODO: we probably want to be looking at head rather than index since this should
    # run on push
    diff_index: git.DiffIndex = repo.index.diff("origin/main", file)

    # Early return for no differences
    if len(diff_index) == 0:
        return FileComparison([], [], False)

    # Package the data in a NamedTuple to return
    ret = FileComparison(
        local=diff_index[0].a_blob.data_stream.read().decode("utf-8").splitlines(),
        remote=diff_index[0].b_blob.data_stream.read().decode("utf-8").splitlines(),
        has_changes=True,
    )

    # Safety checks
    assert len(diff_index) == 1, "If this happens, we need to rethink how we use diff."
    with open(file, "r") as f:
        contents: List[str] = f.read().splitlines()
    assert ret.local == contents, (
        "The local file read from disk does not match the git index. "
        "This is likely due to unstaged changes not being stashed before this hook was "
        "run. "
        "Is this running on push?"
    )

    return ret


def _check_changelog_clash(file: Path) -> int:
    """
    Check for clashes between the current and remote main changelogs.

    Args:
        file (Path): The path to the local file to be checked.

    Returns:
        1 if clashes are found, 0 otherwise.
    """
    file_comparison = _get_changes(file)
    if not file_comparison.has_changes:
        return 0

    return 1


def _parse_args() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of Path): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])

    return parser.parse_args()


def main() -> int:
    """
    Entrypoint for the check-changelog-clash hook.

    Check the current changelog (if modified) against origin/main.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    args = _parse_args()

    # Early exit if no files provided
    if len(args.files) < 1:
        return 0

    # Check each changed file
    retv = 0
    for file in args.files:
        retv |= _check_changelog_clash(file)

    return retv


if __name__ == "__main__":
    exit(main())
