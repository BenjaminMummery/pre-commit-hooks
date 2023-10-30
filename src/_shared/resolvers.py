# Copyright (c) 2023 Benjamin Mummery

"""Common resolvers that are used by multiple hooks."""

import os
import typing as t
from pathlib import Path


def resolve_files(files: t.Union[str, t.List[str]]) -> t.List[Path]:
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

    _files: t.List[Path] = [
        Path(file) for file in (files if isinstance(files, list) else [files])
    ]

    for file in _files:
        if not os.path.isfile(file):
            raise FileNotFoundError(file)

    return _files
