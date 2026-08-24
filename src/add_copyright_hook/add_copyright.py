#!/usr/bin/env python3
# Copyright (c) 2023 - 2026 Benjamin Mummery
"""Check that source files contain a copyright string, and add one to files that don't.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import sys

from pathlib import Path

from git import GitCommandError, Repo
from git.objects.commit import Commit
from git.repo.base import BlameEntry
from identify import identify

from src._shared import resolvers
from src._shared.comment_mapping import get_comment_markers
from src._shared.config_parsing import read_config
from src._shared.copyright_parsing import (
    parse_copyright_comment,
    parse_copyright_docstring,
)
from src._shared.exceptions import InvalidConfigError, NoCommitsError

TOOL_NAME = "add_copyright"

# Mapping between the language tags as determined by identify, and how they are
# represented in toml.
LANGUAGE_TAGS_TOMLKEYS: dict = dict(
    sorted(
        {
            "c++": "cpp",
            "c#": "c-sharp",
            "css": "css",
            "dart": "dart",
            "html": "html",
            "java": "java",
            "javascript": "javascript",
            "kotlin": "kotlin",
            "lua": "lua",
            "markdown": "markdown",
            "perl": "perl",
            "php": "php",
            "python": "python",
            "ruby": "ruby",
            "rust": "rust",
            "scala": "scala",
            "sql": "sql",
            "swift": "swift",
        }.items(),
    ),
)


def _get_earliest_commit_year(file: Path) -> int:
    """Get the year of the earliest commit made to the specified file.

    Args:
        file (Path): The path to the file to be checked

    Raises:
        InvalidGitRepositoryError: When the hook is called in a directory that
            is not a git repository.
        NoCommitsError: When the file has no commits for us to examine the blame.

    Returns:
        int: The year of the earliest commit on the file.

    """
    repo = Repo(".")

    try:
        blames = repo.blame(repo.head, str(file))
    except GitCommandError as e:
        raise NoCommitsError from e

    if blames is None:
        msg = "No blames to parse."
        raise NoCommitsError(msg)

    timestamps: list[int] = []
    for blame in blames:
        if blame is None:
            continue
        if isinstance(blame, BlameEntry):
            timestamps += [
                int(commit.committed_date) for commit in blame.commit.values()
            ]
        elif isinstance(blame, list):
            for commit in blame:
                if isinstance(commit, Commit):
                    timestamps.append(int(commit.committed_date))
                else:
                    continue

    timestamps_set = set(timestamps)

    if len(timestamps_set) < 1:
        msg = "No blame timestamps found."
        raise NoCommitsError(msg)

    earliest_date: datetime.datetime = datetime.datetime.fromtimestamp(
        min(timestamps),
    )

    return int(earliest_date.year)


def _parse_args() -> dict:
    """Parse the CLI arguments.

    Returns:
        dict:
        - files (list of Path): the paths to each changed file relevant to this hook.
        - name (str, None): the configured name to add to the copyright
        - format (str, None): the format that the copyright string should follow.
    """
    parser = argparse.ArgumentParser()
    holder_group: argparse._MutuallyExclusiveGroup = (
        parser.add_mutually_exclusive_group()
    )
    holder_group.add_argument("-n", "--name", type=str, default=None)
    holder_group.add_argument(
        "--use-git-user",
        action="store_true",
        default=None,
        help="Use git's user.name as the copyright holder.",
    )
    parser.add_argument("-f", "--format", type=str, default=None)
    parser.add_argument("files", nargs="*", default=[])
    args = parser.parse_args()

    # Check that files exist
    args.files = resolvers.resolve_files(args.files)

    return args.__dict__


def _get_git_user_name() -> str:
    """Get the user name as configured in git.

    Raises:
        ValueError: when the user name has not been configured.

    Returns:
        str: the user name
    """
    repo = Repo(".")
    reader = repo.config_reader()
    name = reader.get_value("user", "name")

    if not isinstance(name, str) or len(name) < 1:
        msg = "The git username is not configured."
        raise ValueError(msg)
    return name


def _parse_bool(value: object, option: str) -> bool:
    """Parse a boolean configuration value from TOML or setup.cfg."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    msg = f"The '{option}' option must be true or false."
    raise InvalidConfigError(msg)


def _resolve_copyright_holder(name: str | None, use_git_user: object) -> str:
    """Resolve the explicitly configured copyright-holder strategy."""
    if name is not None and not name.strip():
        msg = "The copyright holder 'name' must not be empty."
        raise InvalidConfigError(msg)

    use_git_user_bool = (
        _parse_bool(use_git_user, "use_git_user") if use_git_user is not None else False
    )
    if name is not None and use_git_user_bool:
        msg = "Configure either 'name' or 'use_git_user', not both."
        raise InvalidConfigError(msg)
    if name is not None:
        return name
    if use_git_user_bool:
        return _get_git_user_name()

    msg = (
        "No copyright holder is configured. Set 'name' in "
        "[tool.add_copyright], pass --name, or explicitly opt in to git's "
        "user.name with 'use_git_user = true' / --use-git-user."
    )
    raise InvalidConfigError(msg)


def _has_shebang(content: str) -> bool:
    """Check whether the content string starts with a shebang.

    Args:
        content (str): The string to check.

    Returns:
        bool: True if a shebang is found, false otherwise.
    """
    return content.startswith("#!")


def _add_copyright_docstring_to_content(content: str, copyright_string: str) -> str:
    """Insert a copyright docstring into the appropriate place in existing content.

    This method attempts to place the copyright in a module level docstring at the top
    of the file. If a docstring doesn't exist, it will be created. If it does exist,
    the copyright info will be added above the existing content.

    Args:
        content (str): The content to be updated.
        copyright_string (str): The copyright string to be inserted.

    Returns:
        str: the new content.
    """
    # Check for an existing docstring, modifying it if it exists.
    code = ast.parse(content)
    for node in ast.walk(code):
        if isinstance(node, ast.Module) and (docstring := ast.get_docstring(node)):
            return content.replace(docstring, f"{copyright_string}\n\n{docstring}")

    # If there isn't a docstring, we need to insert it
    # We can do this by treating it like a comment and inserting it in the same way we
    # handle those.
    return _add_copyright_comment_to_content(content, f'"""\n{copyright_string}\n"""')


def _add_copyright_comment_to_content(content: str, copyright_string: str) -> str:
    """Insert a copyright string into the appropriate place in existing content.

    This method attempts to place the copyright string at the top of the file, unless
    the file starts with a shebang in which case the copyright string is inserted after
    the shebang, separated by an empty line.

    Args:
        content (str): The content to be updated.
        copyright_string (str): The copyright string to be inserted.

    Returns:
        str: the new content.
    """
    lines: list[str] = content.splitlines()
    new_lines: list[str] = []

    # If the file starts with a shebang, keep that first in the new content.
    if _has_shebang(content):
        new_lines += [lines[0], ""]
        lines = lines[1:]

    # Remove leading empty lines from the content
    while len(lines) >= 1 and lines[0] == "":
        lines = lines[1:]

    new_lines += [copyright_string, "", *lines]
    if new_lines[-1] != "":
        new_lines.append("")
    return "\n".join(new_lines)


def _construct_copyright_string(
    name: str,
    start_year: int,
    end_year: int,
    copyright_format: str,
) -> str:
    """Construct a string containing the copyright information.

    Args:
        name (str): The name of the copyright holder.
        start_year (int): The start year of the copyright.
        end_year (int): The end year of the copyright.
        copyright_format (str): The f-string into which the name and year should
            be inserted.

    Returns:
        str: the copyright string.
    """
    year = f"{start_year}" if start_year == end_year else f"{start_year}-{end_year}"
    return f"{copyright_format.format(year=year, name=name)}"


def _ensure_comment(
    copyright_string: str,
    comment_markers: tuple[str, str | None],
) -> str:
    """Ensure that the string passed in is properly comment escaped.

    Args:
        copyright_string (str): The string to be checked
        comment_markers (tuple[str, str | None]): (tuple(str, str|None)):
            The comment markers to be inserted before and, optionally, after the
            copyright string.

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
    assert len(outlines) > 0, (
        "Unknown error in `_ensure_comment()`: generated no lines."
    )
    if len(outlines) == 1:
        return outlines[0]
    return "\n".join(outlines)


def _read_default_configuration() -> dict:
    """Read in the default configuration from a config file.

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
    supported_language_subkeys = ["format", "docstr"]
    supported_toml_keys = [
        "name",
        "use_git_user",
        "format",
        *list(LANGUAGE_TAGS_TOMLKEYS.values()),
    ]

    retv = dict.fromkeys(supported_toml_keys)

    # read data from config file
    try:
        data, filepath = read_config(TOOL_NAME)
    except FileNotFoundError:
        # Early return for no available config files
        return retv

    for key in data:
        # Check that the keys are things we support, and raise an error if not.
        if key not in supported_toml_keys:
            msg = (
                f"Unsupported option in config file {filepath}: '{key}'. "
                f"Supported options are: {supported_toml_keys}."
            )
            raise KeyError(
                msg,
            )

        # If the key is a supported language, check that the subkeys are supported.
        if key in LANGUAGE_TAGS_TOMLKEYS.values():
            for subkey in data[key]:
                if subkey not in supported_language_subkeys:
                    msg = (
                        f"Unsupported option in config file {filepath}: "
                        f"'{key}.{subkey}'. "
                        f"Supported options for '{key}' are: "
                        f"{supported_language_subkeys}."
                    )
                    raise KeyError(
                        msg,
                    )

        retv[key] = data[key]

    return retv


def _ensure_valid_format(copyright_format: str) -> None:
    """Ensure that the provided format string contains the required keys.

    Args:
        copyright_format (str): The string to be checked.

    Raises:
        KeyError: when one or more keys is missing.

    Returns:
        None: the checked format string.
    """
    keys = ["name", "year"]
    missing_keys = [key for key in keys if "{" + key + "}" not in copyright_format]
    if len(missing_keys) > 0:
        msg = (
            f"The format string '{copyright_format}' is missing the following "
            f"required keys: {missing_keys}"
        )
        raise KeyError(
            msg,
        )


def _ensure_copyright_string(
    file: Path,
    name: str | None,
    use_git_user: object,
    copyright_format: str,
    docstr: bool = False,
) -> int:
    """Ensure that the file has a copyright string.

    This function encompasses the heavy lifting for the hook.

    Args:
        file (Path): the file to be checked.
        name (optional(str)): the explicitly configured copyright holder.
        use_git_user (object): whether to explicitly use git's configured user.name.
        copyright_format (str): the format to be used when adding new copyright
            strings.
        docstr (bool): if true, the copyright is expected to be part of
            the docstring. If false, it is expected to be a comment.

    Raises:
        KeyError: when the format for the copyright string lacks required keys.
        ValueError: when the git username is not configured.

    Returns:
        int: 0 if the file already had a copyright string, 1 if a copyright string had
            to be added.
    """
    # Early return if the format is invalid.
    _ensure_valid_format(copyright_format)

    with file.open("r+") as f:
        content: str = f.read()
        comment_markers: tuple[str, str | None] = get_comment_markers(file)

        # Early return if the file already has copyright info, either in a comment or a
        # docstring.
        if parse_copyright_comment(
            content,
            comment_markers,
        ) or parse_copyright_docstring(content):
            return 0

        copyright_holder = _resolve_copyright_holder(name, use_git_user)

        copyright_end_year: int = datetime.date.today().year
        copyright_start_year: int
        try:
            copyright_start_year = _get_earliest_commit_year(file)
        except NoCommitsError:
            copyright_start_year = copyright_end_year

        new_copyright_string = _construct_copyright_string(
            copyright_holder,
            copyright_start_year,
            copyright_end_year,
            copyright_format,
        )

        if not docstr:
            new_copyright_string = _ensure_comment(
                new_copyright_string,
                comment_markers=comment_markers,
            )

        f.seek(0, 0)
        f.truncate()
        f.write(
            _add_copyright_docstring_to_content(content, new_copyright_string)
            if docstr
            else _add_copyright_comment_to_content(content, new_copyright_string),
        )
        print(f"Fixing file `{file}` ", end="")
        print(f"- added line(s):\n{new_copyright_string}")
    return 1


def main() -> int:
    """Entrypoint for the add_copyright hook.

    Check that source files contain a copyright string, and add one to files that don't.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    # Build the configuration from config files and CLI args.
    # Fields that appear in both the configuration and CLI args use the CLI
    # values.
    configuration = _read_default_configuration()
    args = _parse_args()
    if args["name"] is not None:
        configuration["use_git_user"] = False
    elif args["use_git_user"]:
        configuration["name"] = None
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
            "copyright_format": configuration["format"]
            or "Copyright (c) {year} {name}",
        }

        # Extract the language-specific config options for this file. Override global
        # options where required.
        for tag in identify.tags_from_path(file):
            if (tag in LANGUAGE_TAGS_TOMLKEYS) and (
                configuration[LANGUAGE_TAGS_TOMLKEYS[tag]] is not None
            ):
                for key in configuration[LANGUAGE_TAGS_TOMLKEYS[tag]]:
                    kwargs_key = "copyright_format" if key == "format" else key
                    kwargs[kwargs_key] = configuration[LANGUAGE_TAGS_TOMLKEYS[tag]][key]
                break

        # Ensure that the file has copyright.
        retv |= _ensure_copyright_string(
            Path(file),
            name=configuration["name"],
            use_git_user=configuration["use_git_user"],
            **kwargs,
        )
    return retv


if __name__ == "__main__":
    sys.exit(main())
