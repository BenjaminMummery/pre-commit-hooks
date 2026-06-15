# Copyright (c) 2023 - 2026 Benjamin Mummery
"""Common resolvers that are used by multiple hooks."""

from __future__ import annotations

from pathlib import Path


def resolve_files(files: str | list[str]) -> list[Path]:
    """Convert the list of files into a list of paths.

    Args:
        files (str | list[str]): The list of changed files.

    Raises:
        FileNotFoundError: When one or more of the specified files does not
        exist.

    Returns:
        list[Path]: A list of paths corresponding to the changed files.
    """
    _files: list[Path] = [
        Path(file) for file in (files if isinstance(files, list) else [files])
    ]

    for file in _files:
        if not file.is_file():
            raise FileNotFoundError(file)

    return _files
