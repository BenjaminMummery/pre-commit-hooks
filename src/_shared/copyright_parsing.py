# Copyright (c) 2023 - 2025 Benjamin Mummery

"""Tools for parsing copyright strings."""

import ast
import re
from typing import Optional, Tuple


class ParsedCopyrightString:
    """Class for storing the components of a parsed copyright string."""

    def __init__(
        self,
        comment_markers: Optional[Tuple[str, Optional[str]]],
        signifiers: str,
        start_year: int,
        end_year: int,
        name: str,
        string: str,
    ):
        """
        Construct ParsedCopyrightString.

        Arguments:
            commentmarkers (tuple(str, str|None)): The character(s) that denote that
                the line is a comment.
            signifiers (str): The string that indicates that this comment relates to
                copyright.
            start_year (int): The earlier year attached to the copyright.
            end_year (int): The later year attached to the copyright.
            name (str): The name of the copyright holder.
            string (str): The full copyright string as it exists in the source file.
        """
        self.comment_markers: Optional[Tuple[str, Optional[str]]] = comment_markers
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

    def __repr__(self) -> str:
        return (
            "ParsedCopyrightString object with:\n"
            f"- comment marker(s): {self.comment_markers}\n"
            f"- signifiers: {self.signifiers}\n"
            f"- start year: {self.start_year}\n"
            f"- end year: {self.end_year}\n"
            f"- name: {self.name}\n"
            f"- string: {self.string}"
        )


def _parse_copyright_docstring(input: str) -> Optional[ParsedCopyrightString]:
    """
    Parse a docstring into a ParsedCopyrightString object.

    This method is fundamentally similar to _parse_copyright_string_line but a) handles multiple-line inputs, and b) assumes that no comment markers are used.

    Args:
        input: the string to be checked.

    Returns:
        _arsedCopyrightString or None: If a matching copyright string was found,
            returns an object containing its information. If a match was not found,
            returns None.
    """
    # Regex string components
    copyright_signifier_group: str = r"(?P<signifiers>(copyright\s?|\(c\)\s?|©\s?)+)\s?"
    year_group: str = r"(?P<year>(\d{4}\s?-\s?\d{4}|\d{4})+)\s?"
    name_group: str = r"(?P<name>\D[^\n]+)\s?"

    # Construct regex string
    exp: str = (
        # Capture the copyright signifier ((c), copyright, things of this nature)
        copyright_signifier_group
        + r"\s?"
        # Capture name and year in either order
        + r"(?:"
        + year_group
        + r"|"
        + name_group
        + r"){2}"
    )

    # Search the input
    match = re.search(re.compile(exp, re.IGNORECASE | re.MULTILINE), input)

    # Early return for no match.
    if match is None:
        return None

    match_dict = match.groupdict()

    # Early return for an incomplete match (i.e. we found a passing reference to copyright, not a marker.)
    if match_dict["year"] is None:
        return None

    # Parse year information.
    start_year, end_year = _parse_years(match_dict["year"])

    return ParsedCopyrightString(
        None,
        match_dict["signifiers"].strip(),
        start_year,
        end_year,
        match_dict["name"].strip(),
        match.group().strip(),
    )


def _parse_copyright_string_line(
    input: str, comment_markers: Tuple[str, Optional[str]]
) -> Optional[ParsedCopyrightString]:
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
    # Early return for empty line
    if input == "":
        return None

    # Safety catch for if we've been given multiple lines.
    assert len(input.splitlines()) == 1

    # Regex string components
    leading_comment_marker_group: str = (
        r"(?P<leading_comment_marker>" + re.escape(comment_markers[0]) + r")"
    )
    copyright_signifier_group: str = r"(?P<signifiers>(copyright\s?|\(c\)\s?|©\s?)+)\s?"
    year_group: str = r"(?P<year>(\d{4}\s?-\s?\d{4}|\d{4})+)\s?"
    name_group: str = r"(?P<name>\D[^\n]+)\s?"

    # Construct regex string
    exp: str = (
        # Mark the start of the string
        r"^"
        # Capture the leading comment marker
        + leading_comment_marker_group
        + r"\s?"
        # Capture the copyright signifier ((c), copyright, things of this nature)
        + copyright_signifier_group
        + r"\s?"
        # Capture name and year in either order
        + r"(?:"
        + year_group
        + r"|"
        + name_group
        + r"){2}"
    )
    # If there's a trailing comment marker, match that too
    if comment_markers[1]:
        exp += r"(?P<trailing_comment_marker>" + re.escape(comment_markers[1]) + r")"
    # Mark the end of the string.
    exp += r"$"

    # Search the input
    match = re.search(re.compile(exp, re.IGNORECASE | re.MULTILINE), input)

    # Early return for no match
    if match is None:
        return None

    match_dict = match.groupdict()

    # Early return for an incomplete match (i.e. we found a passing reference to copyright, not a marker.)
    if match_dict["year"] is None:
        return None

    start_year, end_year = _parse_years(match_dict["year"])
    leading_comment = match_dict["leading_comment_marker"].strip()
    trailing_comment = (
        None
        if not comment_markers[1]
        else match_dict["trailing_comment_marker"].strip()
    )

    return ParsedCopyrightString(
        (leading_comment, trailing_comment),
        match_dict["signifiers"].strip(),
        start_year,
        end_year,
        match_dict["name"].strip(),
        match.group().strip(),
    )


def parse_copyright_docstring(input: str) -> Optional[ParsedCopyrightString]:
    """
    Search through lines of content looking for docstrings containing copyright markers.

    Args:
        input (str): The content to be searched.

    Returns:
        ParsedCopyrightString|None: the parsed copyright string if one was found,
            otherwise None.
    """
    try:
        code = ast.parse(input)
    except SyntaxError:
        return None

    for node in ast.walk(code):
        if isinstance(node, ast.Module):
            if docstring := ast.get_docstring(node):
                if parsed_string := _parse_copyright_docstring(docstring):
                    return parsed_string
    return None


def parse_copyright_comment(
    input: str, comment_markers: Tuple[str, Optional[str]]
) -> Optional[ParsedCopyrightString]:
    """
    Search through lines of content looking for copyright comments.

    Args:
        input (str): The content to be searched.
        comment_markers (tuple(str, str|None)): The characters marking the beginning and
            (optionally) end of a comment.

    Raises:
        ValueError: When the content contains multiple copyright strings.

    Returns:
        ParsedCopyrightString|None: the parsed copyright string if one was found,
            otherwise None.
    """
    copyright_strings = []
    for line in input.splitlines():
        if parsed_string := _parse_copyright_string_line(line, comment_markers):
            copyright_strings.append(parsed_string)
    if len(copyright_strings) == 0:
        return None
    if len(copyright_strings) > 1:
        raise ValueError(f"Found multiple copyright strings: {copyright_strings}")
    return copyright_strings[0]


def _parse_years(year: str) -> Tuple[int, int]:
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
