# Copyright (c) 2023 Benjamin Mummery

"""Tools for parsing copyright strings."""

import re
from typing import Optional, Tuple


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


def parse_copyright_string(
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
    # Construct regex string
    exp = (
        # The line should start with the comment escape character '#'.
        r"^(?P<commentmarker>" + re.escape(comment_markers[0]) + r")\s?"
        # One or more ways of writing 'copyright': the word, the character `©`, or the
        # approximation `(c)`.
        r"(?P<signifiers>(copyright\s?|\(c\)\s?|©\s?)+)"
        # Year information - either 4 digits, or 2 sets of 4 digits separated by a dash.
        r"(?P<year>(\d{4}\s?-\s?\d{4}|\d{4})+)"
        r"\s*"
        # The name of the copyright holder. No restrictions on this, just take whatever
        # is left in the string as long as it's not nothing.
        r"(?P<name>.*)"
    )
    if comment_markers[1]:
        # If there's a trailing commentmarker, the line should end with that
        exp += r"\s?(?P<trailing_commentmarker>" + re.escape(comment_markers[1]) + r")"
    exp += r"\s*$"

    # Search the input
    match = re.search(re.compile(exp, re.IGNORECASE | re.MULTILINE), input)
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
