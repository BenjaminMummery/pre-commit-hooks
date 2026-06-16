# Copyright (c) 2023 - 2026 Benjamin Mummery
"""Mapping between coding languages and the comment markers they use."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from identify import identify

HASH_COMMENT = ("#", None)
SLASH_COMMENT = ("//", None)
DASH_COMMENT = ("--", None)
HTML_COMMENT = ("<!---", "-->")

COMMENT_MARKERS: Mapping[str, tuple[str, str | None]] = {
    "c++": SLASH_COMMENT,
    "c#": ("/*", "*/"),
    "css": ("/*", "*/"),
    "dart": SLASH_COMMENT,
    "html": HTML_COMMENT,
    "java": SLASH_COMMENT,
    "javascript": SLASH_COMMENT,
    "kotlin": SLASH_COMMENT,
    "lua": DASH_COMMENT,
    "markdown": HTML_COMMENT,
    "perl": HASH_COMMENT,
    "php": SLASH_COMMENT,
    "python": HASH_COMMENT,
    "ruby": HASH_COMMENT,
    "rust": SLASH_COMMENT,
    "scala": SLASH_COMMENT,
    "sql": DASH_COMMENT,
    "swift": SLASH_COMMENT,
}


def get_comment_markers(file: Path) -> tuple[str, str | None]:
    """Get the appropriate comment markers for the type of file.

    Args:
        file (Path): Path to the file to which we want to add comments.

    Raises:
        NotImplementedError: When the file is not a format we support.

    Returns:
        tuple[str, str | None]: The leading and trailing comment markers.
    """
    # Try to identify the file type from the extension.
    tags = identify.tags_from_path(str(file))
    for tag in tags:
        if tag in COMMENT_MARKERS:
            return COMMENT_MARKERS[tag]

    msg = (
        f"The file extension '{Path(file).suffix}' is not currently supported. "
        f"File has tags: {tags}"
    )
    raise NotImplementedError(
        msg,
    )
