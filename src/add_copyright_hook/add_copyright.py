#!/usr/bin/env python3

# Copyright (c) 2023 - 2024 Benjamin Mummery

"""
Check that source files contain a copyright string, and add one to files that don't.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import datetime
from pathlib import Path
from typing import List, Optional, Set, Tuple

from git import GitCommandError, InvalidGitRepositoryError, Repo
from identify import identify

from src._shared import resolvers
from src._shared.comment_mapping import get_comment_markers
from src._shared.config_parsing import read_config
from src._shared.copyright_parsing import parse_copyright_string
from src._shared.exceptions import NoCommitsError

TOOL_NAME = "add_copyright"

# Mapping between the language tags as determined by identify, and how they are
# represented in toml.
LANGUAGE_TAGS_TOMLKEYS: dict = {
    "c++": "cpp",
    "c#": "c-sharp",
    "html": "html",
    "java": "java",
    "javascript": "javascript",
    "markdown": "markdown",
    "perl": "perl",
    "php": "php",
    "python": "python",
    "ruby": "ruby",
    "sql": "sql",
    "ts": "typescript",
}


def _get_earliest_commit_year(file: Path) -> int:
    """
    Get the years of the earliest and latest commits made to the specified file.

    Args:
        file (Path): The path to the file to be checked

    Raises:
        InvalidGitRepositoryError: when the hook is called in a directory that
        is not a git repository.
        NoCommitsError: when the file has no commits for us to examine the blame.

    Returns:
        int: The year of the earliest commit on the file.

    """
    try:
        repo = Repo(".")
    except InvalidGitRepositoryError:
        raise

    try:
        blames = repo.blame(repo.head, str(file))
    except GitCommandError as e:
        raise NoCommitsError from e

    timestamps: Set[int] = set(
        int(blame[0].committed_date) for blame in blames  # type: ignore
    )

    earliest_date: datetime = datetime.datetime.fromtimestamp(  # type: ignore
        min(timestamps)
    )

    return int(earliest_date.year)  # type: ignore


def _parse_args() -> dict:
    """
    Parse the CLI arguments.

    Returns:
        dict with the following keys:
        - files (list of Path): the paths to each changed file relevant to this hook.
        - name (str, None): the configured name to add to the copyright
        - format (str, None): the format that the copyright string should follow.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default=None)
    parser.add_argument("-f", "--format", type=str, default=None)
    parser.add_argument("files", nargs="*", default=[])
    args = parser.parse_args()

    # Check that files exist
    args.files = resolvers.resolve_files(args.files)

    return args.__dict__


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
    name = reader.get_value("user", "name")

    if not isinstance(name, str) or len(name) < 1:
        raise ValueError("The git username is not configured.")
    return name


def _has_shebang(input: str) -> bool:
    """
    Check whether the input string starts with a shebang.

    Args:
        input (str): The string to check.

    Returns:
        bool: True if a shebang is found, false otherwise.
    """
    return input.startswith("#!")


def _add_copyright_string_to_content(content: str, copyright_string: str) -> str:
    """
    Insert a copyright string into the appropriate place in existing content.

    This method attempts to place the copyright string at the top of the file, unless
    the file starts with a shebang in which case the copyright string is inserted after
    the shebang, separated by an empty line.

    Args:
        content (str): The content to be updated.
        copyright_string (str): The copyright string to be inserted.

    Returns:
        str: the new content.
    """
    lines: List[str] = content.splitlines()
    new_lines: List[str] = []

    # If the file starts with a shebang, keep that first in the new content.
    if _has_shebang(content):
        new_lines += [lines[0], ""]
        lines = lines[1:]

    # Remove leading empty lines from the content
    while len(lines) >= 1 and lines[0] == "":
        lines = lines[1:]

    new_lines += [copyright_string, ""] + lines
    if not new_lines[-1] == "":
        new_lines.append("")
    return "\n".join(new_lines)


def _construct_copyright_string(
    name: str,
    start_year: int,
    end_year: int,
    format: str,
    comment_markers: Tuple[str, Optional[str]],
) -> str:
    """
    Construct a commented line containing the copyright information.

    Args:
        name (str): The name of the copyright holder.
        start_year (str): The start year of the copyright.
        end_year (str): The end year of the copyright.
        format (str): The f-string into which the name and year should be
            inserted.
        comment_markers (tuple(str, str|None)): The comment markers to be inserted
            before and, optionally, after the copyright string.

    Return:
        str: the copyright string, with appropriate comment escapes.
    """
    if start_year == end_year:
        year = f"{start_year}"
    else:
        year = f"{start_year} - {end_year}"
    commentstr = f"{format.format(year=year, name=name)}"
    x = _ensure_comment(commentstr, comment_markers)
    return x


def _ensure_comment(
    copyright_string: str, comment_markers: Tuple[str, Optional[str]]
) -> str:
    """
    Ensure that the string passed in is properly comment escaped.

    Args:
        copyright_string (str): The string to be checked
        comment_markers: (tuple(str, str|None)): The comment markers to be inserted
            before and, optionally, after the copyright string.

    Returns:
        str: the properly escaped string.
    """
    outlines = copyright_string.splitlines()
    for i, line in enumerate(outlines):
        newline = line
        if not line.startswith(comment_markers[0]):
            newline = f"{comment_markers[0]} {line}"
        if comment_markers[1] and not line.endswith(comment_markers[1]):
            newline = f"{newline} {comment_markers[1]}"
        outlines[i] = newline
    assert (
        len(outlines) > 0
    ), "Unknown error in `_ensure_comment()`: generated no lines."
    if len(outlines) == 1:
        return outlines[0]
    else:
        return "\n".join(outlines)


def _read_default_configuration() -> dict:
    """
    Read in the default configuration from a config file.

    Raises:
        KeyError: when the configuration contains unsupported options.

    Returns:
        dict: a mapping of key value pairs where the key is the configuration option
            and the value is its value. For example, the `pyproject.toml`
            entry

            ```toml
            [tool.add_copyright]
            name = "my name"
            ```

            will be returned as the following dict:

            ```python
            {"name" : "my name"}
            ```
    """
    supported_langauge_subkeys = ["format"]
    supported_toml_keys = ["name", "format"] + [
        v for v in LANGUAGE_TAGS_TOMLKEYS.values()
    ]

    retv = dict([(key, None) for key in supported_toml_keys])

    # read data from config file
    try:
        data, filepath = read_config(TOOL_NAME)
    except FileNotFoundError:
        # Early return for no available config files
        return retv

    for key in data:
        # Check that the keys are things we support, and raise an error if not.
        if key not in supported_toml_keys:
            raise KeyError(
                f"Unsupported option in config file {filepath}: '{key}'. "
                f"Supported options are: {supported_toml_keys}."
            )

        # If the key is a supported language, check that the subkeys are supported.
        if key in LANGUAGE_TAGS_TOMLKEYS.values():
            for subkey in data[key]:
                if subkey not in supported_langauge_subkeys:
                    raise KeyError(
                        f"Unsupported option in config file {filepath}: "
                        f"'{key}.{subkey}'. "
                        f"Supported options for '{key}' are: "
                        f"{supported_langauge_subkeys}."
                    )

        retv[key] = data[key]

    return retv


def _ensure_valid_format(format: str):
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


def _ensure_copyright_string(file: Path, name: Optional[str], format: str) -> int:
    """
    Ensure that the file has a docstring.

    This function encompasses the heavy lifting for the hook.

    Args:
        file (path): the file to be checked.

    Raises:
        KeyError: when the format for the copyright string lacks required keys.
        ValueError: when the git username is not configured.


    Returns:
        int: 0 if the file already had a copyright string, 1 if a copyright string had
            to be added.
    """
    try:
        _ensure_valid_format(format)
    except KeyError:
        raise

    with open(file, "r+") as f:
        content: str = f.read()
        comment_markers: Tuple[str, Optional[str]] = get_comment_markers(file)

        if parse_copyright_string(content, comment_markers):
            return 0

        print(f"Fixing file `{file}` ", end="")

        copyright_end_year: int = datetime.date.today().year
        copyright_start_year: int
        try:
            copyright_start_year = _get_earliest_commit_year(file)
        except NoCommitsError:
            copyright_start_year = copyright_end_year

        try:
            new_copyright_string = _construct_copyright_string(
                name or _get_git_user_name(),
                copyright_start_year,
                copyright_end_year,
                format,
                comment_markers,
            )
        except ValueError:  # pragma: no cover
            raise

        f.seek(0, 0)
        f.truncate()
        f.write(_add_copyright_string_to_content(content, new_copyright_string))
        print(f"- added line(s):\n{new_copyright_string}")
    return 1


def main():
    """
    Entrypoint for the add_copyright hook.

    Check that source files contain a copyright string, and add one to files that don't.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    # Build the configuration from config files and CLI args.
    # Fields that appear in both the configuration and CLI args use the CLI
    # values.
    try:
        configuration = _read_default_configuration()
    except KeyError:
        raise
    args = _parse_args()
    for key in args:
        if args[key] is not None:
            configuration[key] = args[key]

    # Early exit if no files provided
    if len(configuration["files"]) < 1:
        return 0

    # Add copyright to files that don't already have it.
    retv: int = 0
    for file in configuration["files"]:
        # Global configurations inherited by this file.
        kwargs: dict = {
            "format": configuration["format"] or "Copyright (c) {year} {name}"
        }

        # Extract the language-specific config options for this file. Override global
        # options where required.
        for tag in identify.tags_from_path(file):
            if (tag in LANGUAGE_TAGS_TOMLKEYS.keys()) and (
                configuration[LANGUAGE_TAGS_TOMLKEYS[tag]] is not None
            ):
                for key in configuration[LANGUAGE_TAGS_TOMLKEYS[tag]].keys():
                    kwargs[key] = configuration[LANGUAGE_TAGS_TOMLKEYS[tag]][key]
                break

        # Ensure that the file has copyright.
        try:
            retv |= _ensure_copyright_string(
                Path(file), name=configuration["name"], **kwargs
            )
        except (KeyError, ValueError):
            raise
    return retv


if __name__ == "__main__":
    exit(main())
