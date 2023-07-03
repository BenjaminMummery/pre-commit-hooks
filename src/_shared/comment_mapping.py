# Copyright (c) 2023 Benjamin Mummery

"""Mapping between coding languages and the comment markers they use."""

import os
from pathlib import Path
from typing import Mapping, Optional, Tuple

from identify import identify

HASH_COMMENT = ("#", None)
SLASH_COMMENT = ("//", None)
DASH_COMMENT = ("--", None)
HTML_COMMENT = ("<!---", "-->")

COMMENT_MARKERS: Mapping[str, Tuple[str, Optional[str]]] = {
    "python": HASH_COMMENT,
    "markdown": HTML_COMMENT,
    "c++": SLASH_COMMENT,
    "javascript": SLASH_COMMENT,
    "java": SLASH_COMMENT,
    "php": SLASH_COMMENT,
    "ruby": HASH_COMMENT,
    "sql": DASH_COMMENT,
    "swift": SLASH_COMMENT,
    "perl": HASH_COMMENT,
    "typescript": SLASH_COMMENT,
    "scala": SLASH_COMMENT,
    "rust": SLASH_COMMENT,
    "kotlin": SLASH_COMMENT,
    "css": ("/*", "*/"),
    "c#": ("/*", "*/"),
    "html": HTML_COMMENT,
    "matlab": ("%", None),
    "dart": SLASH_COMMENT,
    "ada": DASH_COMMENT,
    "assembly": (";", None),
    "lua": DASH_COMMENT,
    "lisp": (";", None),
}


def get_comment_markers(file: Path) -> Tuple[str, Optional[str]]:
    """
    Get the appropriate comment markers for the type of file.

    Args:
        file (Path): Path to the file to which we want to add comments.

    Raises:
        NotImplementedError: When the file is not a format we support.

    Returns:
        t.Tuple[str, t.Optional[str]]: The leading and trailing comment markers.
    """
    # Try to identify the file type from the extension.
    tags = identify.tags_from_path(file)
    for tag in tags:
        try:
            return COMMENT_MARKERS[tag]
        except KeyError:
            continue

    raise NotImplementedError(
        f"The file extension '{os.path.splitext(file)[1]}' is not currently supported. "
        f"File has tags: {tags}"
    )
