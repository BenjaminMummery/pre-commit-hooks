# Copyright (c) 2023 - 2026 Benjamin Mummery
"""Tools for parsing copyright strings."""

from __future__ import annotations

import ast
import re


class ParsedCopyrightString:
    """Class for storing the components of a parsed copyright string."""

    def __init__(
        self,
        comment_markers: tuple[str, str | None] | None,
        signifiers: str,
        start_year: int,
        end_year: int,
        name: str,
        string: str,
    ) -> None:
        """Construct ParsedCopyrightString.

        Arguments:
            comment_markers: The character(s) that denote that
                the line is a comment.
            signifiers: The string that indicates that this comment relates to
                copyright.
            start_year: The earlier year attached to the copyright.
            end_year: The later year attached to the copyright.
            name: The name of the copyright holder.
            string: The full copyright string as it exists in the source file.
        """
        self.comment_markers: tuple[str, str | None] | None = comment_markers
        self.signifiers: str = signifiers
        self.start_year: int = start_year
        self.end_year: int = end_year
        self.name: str = name
        self.string: str = string
        if not self.end_year >= self.start_year:
            msg = (
                "Copyright end year cannot be before the start year. "
                f"Got {self.end_year} and {self.start_year} respectively."
            )
            raise ValueError(
                msg,
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


def _parse_copyright_docstring(text: str) -> ParsedCopyrightString | None:
    """Parse a docstring into a ParsedCopyrightString object.

    This method is fundamentally similar to _parse_copyright_string_line but a)
    handles multiple-line inputs, and b) assumes that no comment markers are used.

    Args:
        text: the string to be checked.

    Returns:
        ParsedCopyrightString | None: If a matching copyright string was found,
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
    match = re.search(re.compile(exp, re.IGNORECASE | re.MULTILINE), text)

    # Early return for no match.
    if match is None:
        return None

    match_dict = match.groupdict()

    # Early return for an incomplete match (i.e. we found a passing reference to
    # copyright, not a marker.)
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
    text: str,
    comment_markers: tuple[str, str | None],
) -> ParsedCopyrightString | None:
    """Check if the input string is a copyright comment.

    Note: at present this assumes that we're looking for a python comment.
    Future versions will extend this to include other languages.

    Args:
        text (str): The string to be checked.
        comment_markers (tuple[str, str | None]): The characters marking the
            beginning and (optionally) end of a comment.

    Returns:
        ParsedCopyrightString | None: If a matching copyright string was found,
            returns an object containing its information. If a match was not found,
            returns None.
    """
    # Early return for empty line
    if text == "":
        return None

    # Safety catch for if we've been given multiple lines.
    assert len(text.splitlines()) == 1

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
    match = re.search(re.compile(exp, re.IGNORECASE | re.MULTILINE), text)

    # Early return for no match
    if match is None:
        return None

    match_dict = match.groupdict()

    # Early return for an incomplete match (i.e. we found a passing reference to
    # copyright, not a marker.)
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


def parse_copyright_docstring(content: str) -> ParsedCopyrightString | None:
    """Search content for docstrings containing copyright markers.

    Args:
        content (str): The content to be searched.

    Returns:
        ParsedCopyrightString | None: the parsed copyright string if one was found,
            otherwise None.
    """
    try:
        code = ast.parse(content)
    except SyntaxError:
        return None

    for node in ast.walk(code):
        if (
            isinstance(node, ast.Module)
            and (docstring := ast.get_docstring(node))
            and (parsed_string := _parse_copyright_docstring(docstring))
        ):
            return parsed_string
    return None


def parse_copyright_comment(
    content: str,
    comment_markers: tuple[str, str | None],
) -> ParsedCopyrightString | None:
    """Search through lines of content looking for copyright comments.

    Args:
        content (str): The content to be searched.
        comment_markers (tuple(str, str|None)): The characters marking the beginning and
            (optionally) end of a comment.

    Raises:
        ValueError: When the content contains multiple copyright strings.

    Returns:
        ParsedCopyrightString | None: the parsed copyright string if one was found,
            otherwise None.
    """
    copyright_strings = [
        parsed_string
        for line in content.splitlines()
        if (parsed_string := _parse_copyright_string_line(line, comment_markers))
    ]
    if len(copyright_strings) == 0:
        return None
    if len(copyright_strings) > 1:
        msg = f"Found multiple copyright strings: {copyright_strings}"
        raise ValueError(
            msg,
        )
    return copyright_strings[0]


def _parse_years(year: str) -> tuple[int, int]:
    """Parse the identified year string as a range of years.

    Arguments:
        year (str): the string to be parsed.

    Returns:
        tuple[int, int]: the start and end years of the range. If the range is
            a single year, these values will be the same.

    Raises:
        SyntaxError: When the year string cannot be parsed.
    """
    match = re.match(
        r"^(?P<start_year>(\d{4}))\s*-\s*(?P<end_year>(\d{4}))",
        year,
    )
    if match:
        return (
            int(match.groupdict()["start_year"]),
            int(match.groupdict()["end_year"]),
        )

    match = re.match(r"^(?P<year>(\d{4}))$", year)
    if match:
        return (int(match.groupdict()["year"]), int(match.groupdict()["year"]))

    msg = f"Could not interpret year value '{year}'."
    raise SyntaxError(
        msg,
    )  # pragma: no cover
