#!/usr/bin/env python3

# Copyright (c) 2023 Benjamin Mummery

"""
Check that source files contain a copyright string, and add one to files that don't.

This module is intended for use as a pre-commit hook. For more information please
consult the README file.
"""

import argparse
import datetime
import json
import os
import re
import sys
import typing as t
from pathlib import Path

import yaml
from git import Repo  # type: ignore
from git.exc import GitCommandError

from src._shared import comment_mapping, resolvers
from src._shared.exceptions import NoCommitsError

DEFAULT_CONFIG_FILE: Path = Path(".add-copyright-hook-config.yaml")
DEFAULT_FORMAT: str = "Copyright (c) {year} {name}"


class ParsedCopyrightString:
    """Class for storing the components of a parsed copyright string."""

    def __init__(
        self,
        commentmarker: str,
        signifiers: str,
        start_year: int,
        end_year: int,
        name: str,
        string: str,
    ):
        """
        Construct ParsedCopyrightString.

        Arguments:
            commentmarker (str): The character(s) that denote that the line is a
                comment.
            signifiers (str): The string that indicates that this comment relates to
                copyright.
            start_year (int): The earlier year attached to the copyright.
            end_year (int): The later year attached to the copyright.
            name (str): The name of the copyright holder.
            string (str): The full copyright string as it exists in the source file.
        """
        self.commentmarker: str = commentmarker
        self.signifiers: str = signifiers
        self.start_year: int = start_year
        self.end_year: int = end_year
        self.name: str = name
        self.string: str = string
        if not self.end_year >= self.start_year:
            raise ValueError(
                "Copyright end year cannot be before the start year. "
                f"Got {self.end_year} and {self.start_year} respectively."
            )

    def __eq__(self, other) -> bool:
        return (
            self.commentmarker == other.commentmarker
            and self.signifiers == other.signifiers
            and self.start_year == other.start_year
            and self.end_year == other.end_year
            and self.name == other.name
            and self.string == other.string
        )

    def __repr__(self) -> str:
        return (
            "ParsedCopyrightString object with:\n"
            f"- comment marker: {self.commentmarker}\n"
            f"- signifiers: {self.signifiers}\n"
            f"- start year: {self.start_year}\n"
            f"- end year: {self.end_year}\n"
            f"- name: {self.name}\n"
            f"- string: {self.string}"
        )


def _parse_copyright_string(input: str) -> t.Optional[ParsedCopyrightString]:
    """
    Check if the input string is a copyright comment.

    Note: at present this assumes that we're looking for a python comment.
    Future versions will extend this to include other languages.

    Args:
        input (str): The string to be checked

    Returns:
        ParsedCopyrightString or None: If a matching copyright string was found,
            returns an object containing its information. If a match was not found,
            returns None.
    """
    exp = re.compile(
        # The line should start with the comment escape character '#'.
        r"^(?P<commentmarker>#)\s?"
        # One or more ways of writing 'copyright': the word, the character `©`, or the
        # approximation `(c)`.
        r"(?P<signifiers>(copyright\s?|\(c\)\s?|©\s?)+)"
        # Year information - either 4 digits, or 2 sets of 4 digits separated by a dash.
        r"(?P<year>(\d{4}\s?-\s?\d{4}|\d{4})+)" r"\s*"
        # The name of the copyright holder. No restrictions on this, just take whatever
        # is left in the string as long as it's not nothing.
        r"(?P<name>.*)",
        re.IGNORECASE | re.MULTILINE,
    )
    match = re.search(exp, input)
    if match is None:
        return None

    matchdict = match.groupdict()
    start_year, end_year = _parse_years(matchdict["year"])

    return ParsedCopyrightString(
        matchdict["commentmarker"].strip(),
        matchdict["signifiers"].strip(),
        start_year,
        end_year,
        matchdict["name"].strip(),
        match.group().strip(),
    )


def _parse_years(year: str) -> t.Tuple[int, int]:
    """
    Parse the identified year string as a range of years.

    Arguments:
        year (str): the string to be parsed.

    Returns:
        int, int: the start and end years of the range. If the range is a single year,
            these values will be the same.

    Raises:
        SyntaxError: When the year string cannot be parsed.
    """
    match = re.match(r"^(?P<start_year>(\d{4}))\s*-\s*(?P<end_year>(\d{4}))", year)
    if match:
        return (
            int(match.groupdict()["start_year"]),
            int(match.groupdict()["end_year"]),
        )

    match = re.match(r"^(?P<year>(\d{4}))$", year)
    if match:
        return (int(match.groupdict()["year"]), int(match.groupdict()["year"]))

    raise SyntaxError(f"Could not interpret year value '{year}'.")  # pragma: no cover


def _update_copyright_string(
    parsed_string: ParsedCopyrightString, start_year: int, end_year: int
) -> str:
    """
    Update the end year in the copyright string to match the specified year.

    If the string contains a year range, updates the later year. If it contains a single
    year, converts this to a year range.

    Arguments:
        parsed_string (ParsedCopyrightString): The copyright string to be updated.
        start_year (int): The earliest date of work on the file.
        end_year (int): The latest date of work on the file.
    """
    if parsed_string.end_year == parsed_string.start_year:
        if start_year == end_year:
            # The existing string contains one year, and it needs to be replaced with a
            # different year.
            return parsed_string.string.replace(
                str(parsed_string.start_year), f"{start_year}"
            )
        else:
            # The existing string contains one year, and it needs to be replaced with a
            # range.
            return parsed_string.string.replace(
                str(parsed_string.start_year), f"{start_year} - {end_year}"
            )
    else:
        if start_year == end_year:
            # The existing string contains a range, and it needs to be replaced with a
            # single year.
            return re.sub(
                rf"{parsed_string.start_year}\s*-\s*{parsed_string.end_year}",
                f"{start_year}",
                parsed_string.string,
            )
        else:
            # The existing string contains a range, and it needs to be replaced with a
            # different range.
            new_str = parsed_string.string.replace(
                str(parsed_string.start_year), f"{start_year}"
            )
            return new_str.replace(str(parsed_string.end_year), f"{end_year}")


def _has_shebang(input: str) -> bool:
    """
    Check whether the input string starts with a shebang.

    Args:
        input (str): The string to check.

    Returns:
        bool: True if a shebang is found, false otherwise.
    """
    return input.startswith("#!")


def _construct_copyright_string(
    name: str, start_year: int, end_year: int, format: str
) -> str:
    """
    Construct a commented line containing the copyright information.

    Args:
        name (str): The name of the copyright holder.
        start_year (str): The start year of the copyright.
        end_year (str): The end year of the copyright.
        format (str): The f-string into which the name and year should be
            inserted.
    """
    if start_year == end_year:
        year = f"{start_year}"
    else:
        year = f"{start_year} - {end_year}"
    outstr = format.format(year=year, name=name)

    return outstr


def _insert_copyright_string(copyright: str, content: str) -> str:
    """
    Insert the specified copyright string as a new line in the content.

    This method attempts to place the copyright string at the top of the file, unless
    the file starts with a shebang in which case the copyright string is inserted after
    the shebang, separated by an empty line.

    Args:
        copyright (str): The copyright string.
        content (str): The content into which to insert the copyright string.

    Returns:
        str: The modified content, including the copyright string.
    """
    lines: t.List[str] = [line for line in content.split("\n")]

    shebang: t.Optional[str] = None
    if _has_shebang(content):
        shebang = lines[0]
        lines = lines[1:]

    if len(lines) == 0:  # pragma: no cover
        # Included for safety, but the way 'lines' is defined makes this condition
        # impossible.
        lines = [copyright]
    elif lines[0] == "":
        lines = [copyright] + lines
    else:
        lines = [copyright, ""] + lines

    if shebang is not None:
        lines = [shebang, ""] + lines

    return "\n".join(lines)


def _copyright_is_current(
    parsed_copyright_string: ParsedCopyrightString, start_year: int, end_year: int
) -> bool:
    """
    Check if the copyright string is up to date.

    Arguments:
        parsed_copyright_string (ParsedCopyrightString): The copyright string to check.
        start_year (int): The earliest year the copyright should cover.
        end_year (int): The latest year the copyright should cover.

    Returns:
        bool: True if the copyright covers the range, otherwise False.
    """
    if (
        parsed_copyright_string.end_year >= end_year
        and parsed_copyright_string.start_year <= start_year
    ):
        return True
    return False


def _get_earliest_commit_year(file: Path) -> int:
    """
    Get the years of the earliest and latest commits made to the specified file.

    Args:
        file (Path): The path to the file to be checked

    Raises:
        NoCommitsError: when the file has no commits for us to examine the blame.

    Returns:
        int: The year of the earliest commit on the file.

    """

    repo = Repo(".")

    try:
        blames = repo.blame(repo.head, str(file))
    except GitCommandError as e:
        raise NoCommitsError from e

    timestamps: t.Set[int] = set(
        int(blame[0].committed_date) for blame in blames  # type: ignore
    )
    if len(timestamps) < 1:
        raise NoCommitsError(f"File {file} has no Blame history.")

    earliest_date: datetime = datetime.datetime.fromtimestamp(  # type: ignore
        min(timestamps)
    )

    return int(earliest_date.year)  # type: ignore


def _infer_start_year(
    file: Path,
    parsed_copyright_string: t.Optional[ParsedCopyrightString],
    end_year: int,
) -> int:
    """
    Infer the start year for the copyright string.

    Ideally we use the date of the earliest commit, but if we don't have one (e.g. the
    file has not been committed previously) we'll defer to the date of the existing
    commit string. If we can't do either, we use the end date, i.e. the current year.

    Args:
        parsed_copyright_string (Optional(ParsedCopyrightString)): The parsed copyright
            string, if one exists.
        end_year (int): The current year.

    Returns:
        int: the inferred start year.
    """
    try:
        return _get_earliest_commit_year(file)
    except NoCommitsError:
        pass

    if parsed_copyright_string:
        return parsed_copyright_string.start_year
    return end_year


def _ensure_comment(string: str, file: Path) -> str:
    """
    Ensure that the string is a comment in the format of the specified file.

    This function deals with three cases:
    1. The string is already formatted as a comment. Returns the string
        unchanged.
    2. The string is unformatted. Adds the appropriate character(s) and returns
        the string.
    3. The string is formatted as a comment for a different file type. We can
        handle cases as simple as a single-character substitution, but anything
        more complex than that probably needs human oversight.

    Args:
        string (str): _description_
        file (Path): _description_

    Returns:
        str: _description_
    """
    # Determine comment character(s) from file extension
    comment_line_start, comment_line_end = comment_mapping.get_comment_markers(file)

    # Make sure the comment character(s) are at the start of line
    if not string.startswith(comment_line_start):
        string = f"{comment_line_start} {string}"

    # If there's an end-line character, make sure it's at the end of the line.
    if comment_line_end and not string.endswith(comment_line_end):
        string = f"{string} {comment_line_end}"

    return string


def _ensure_copyright_string(file: Path, name: str, format: str) -> int:
    """
    Ensure that the specified file has a copyright string.

    Check the file contents for the presence a copyright string, adding one if it is
    not already present.

    Args:
        file (Path): the file to check.
        name (str): Name of the copyright holder to be added to uncopyrighted
            files.
        format (str): f-string specifying the structure of new copyright
            strings.

    Returns:
        int: 0 if the file is unchanged, 1 if it was modified.
    """
    # Get the start and end years for the copyright.
    # The start year is the date of the earliest commit to the file. The end year
    # should be the commit that is currently in process, so we take the current year
    # from the system clock.
    end_year: int = _get_current_year()

    with open(file, "r+") as f:
        contents: str = f.read()
        new_contents: str

        parsed_copyright_string = _parse_copyright_string(contents)

        start_year: int = _infer_start_year(file, parsed_copyright_string, end_year)

        # If we have a copyright string, and it corresponds to the range of commit
        # dates, then there's nothing to do.
        if parsed_copyright_string and _copyright_is_current(
            parsed_copyright_string, start_year, end_year
        ):
            return 0

        print(f"Fixing file `{file}` ", end="")
        if parsed_copyright_string:
            # There's already a copyright string, we need to update it.
            copyright_string: str = _update_copyright_string(
                parsed_copyright_string, start_year, end_year
            )
            new_contents = contents.replace(
                parsed_copyright_string.string, copyright_string
            )
            print(
                "- updating existing copyright string:\n "
                f"`{parsed_copyright_string.string}` --> `{copyright_string}`\n"
            )
        else:
            # There's no copyright string, we need to add one.
            copyright_comment = _ensure_comment(
                _construct_copyright_string(name, start_year, end_year, format), file
            )
            new_contents = _insert_copyright_string(copyright_comment, contents)
            print(f"- added line(s):\n{copyright_comment}\n")

        f.seek(0, 0)
        f.truncate()
        f.write(new_contents)

    # Safety checks
    _confirm_file_updated(file, new_contents)
    return 1


def _confirm_file_updated(file: Path, expected_contents: str) -> None:
    """
    Confirm that the file contents match what we expect them to be.

    Used to confirm that the file has been overwritten with the new values.

    Args:
        file (Path): Path to the file to examine
        expected_contents (str): The contents that are expected to have been
            written to the file.

    Raises:
        AssertionError: If the contents do not match.
    """
    with open(file, "r") as f:
        file_contents = f.read()
        assert file_contents == expected_contents
        assert _parse_copyright_string(file_contents)


def _get_current_year() -> int:
    """Get the current year from the system clock."""
    today = datetime.date.today()
    return today.year


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


def _resolve_user_name(
    name: t.Optional[str] = None, config: t.Optional[str] = None
) -> str:
    """
    Resolve the user name to attach to the copyright.

    If the name argument is provided, it is returned as the username. Otherwise
    the user name is inferred from the git configuration.

    Args:
        name (str, optional): The name argument if provided. Defaults to None.
        config (str, optional): The config argument if provided. Defaults to None.

    Raises:
        ValueError: When the name argument is not provided, no config file is provided,
        and the git user name is not configured.

    Returns:
        str: The resolved name.
    """
    if name is not None:
        return name

    if config is not None:
        data = _read_config_file(config)
        if "name" in data:
            return data["name"]

    return _get_git_user_name()


def _ensure_valid_format(format: str) -> str:
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
    return format


def _resolve_format(
    format: t.Optional[str] = None, config: t.Optional[str] = None
) -> str:
    """
    Resolve the format with which the copyright string should be constructed.

    Args:
        format (str, optional): The format argument if provided. Defaults to None.
        config (str, optional): The config argument if provided. Defaults to None.

    Returns:
        str: The resolved format.
    """
    if format is not None:
        return _ensure_valid_format(format)

    if config is not None:
        data = _read_config_file(config)
        if "format" in data:
            return _ensure_valid_format(data["format"])
        print(f"Config file `{config}` has no format field.")

    return _ensure_valid_format(DEFAULT_FORMAT)


def _read_config_file(file_path: str) -> t.Mapping[str, str]:
    """
    Read in the parameters from the specified configuration file.

    Args:
        file_path (str): The path to the file.

    Raises:
        FileNotFoundError: when the path does not point to an extant file, or points to
            a file of an unsupported type.

    Returns:
        dict: The key values pairs interpreted from the file's contents.
    """
    _file_path = Path(file_path)
    data: t.Mapping[str, str]
    with open(_file_path, "r") as f:
        if _file_path.suffix == ".json":
            data = json.load(f)
        elif _file_path.suffix == ".yaml":
            data = yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"{file_path} is not a valid config file.")

    return data


def _parse_args() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    Returns:
        argparse.Namespace with the following attributes:
        - files (list of Path): the paths to each changed file relevant to this hook.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    parser.add_argument("-n", "--name", type=str, default=None)
    parser.add_argument("-f", "--format", type=str, default=None)
    parser.add_argument("-c", "--config", type=str, default=None)
    args = parser.parse_args()

    if args.config and (args.name or args.format):
        print("The arguments -c and -n|-f are mutually exclusive.")
        sys.exit(2)

    if args.config is None and os.path.isfile(DEFAULT_CONFIG_FILE):
        args.config = DEFAULT_CONFIG_FILE
        print(f"Found config file `{args.config}`.")

    args.name = _resolve_user_name(args.name, args.config)
    args.format = _resolve_format(args.format, args.config)
    args.files = resolvers._resolve_files(args.files)

    return args


def main() -> int:
    """
    Entrypoint for the add_copyright hook.

    Check that source files contain a copyright string, and add one to files that don't.

    Returns:
        int: 1 if files have been modified, 0 otherwise.
    """
    args = _parse_args()

    # Early exit if no files provided
    if len(args.files) < 1:
        return 0

    # Filter out files that already have a copyright string
    retv = 0
    for file in args.files:
        retv |= _ensure_copyright_string(file, args.name, args.format)

    return retv


if __name__ == "__main__":
    exit(main())
