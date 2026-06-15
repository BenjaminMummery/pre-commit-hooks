# Copyright (c) 2025-2026 Benjamin Mummery

"""Apply ordered text edits to source files."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

Edit = Tuple[int, int, int, int, str]


@dataclass
class SourceEdit:
    """A single replacement in a source file."""

    start_line: int
    start_col: int
    end_line: int
    end_col: int
    replacement: str

    @classmethod
    def from_tuple(cls, edit: Edit) -> SourceEdit:
        """Create a SourceEdit from a tuple edit descriptor."""
        start_line, start_col, end_line, end_col, replacement = edit
        return cls(start_line, start_col, end_line, end_col, replacement)


def apply_edits(source: str, edits: Iterable[Edit]) -> str:
    """Apply edits from bottom to top so offsets remain valid."""
    line_starts = _line_starts(source)
    normalized = sorted(
        [SourceEdit.from_tuple(edit) for edit in edits],
        key=lambda edit: (
            _position_to_index(line_starts, edit.end_line, edit.end_col),
            _position_to_index(line_starts, edit.start_line, edit.start_col),
        ),
        reverse=True,
    )

    for edit in normalized:
        start_index = _position_to_index(line_starts, edit.start_line, edit.start_col)
        end_index = _position_to_index(line_starts, edit.end_line, edit.end_col)
        source = source[:start_index] + edit.replacement + source[end_index:]

    return source


def _line_starts(source: str) -> list[int]:
    starts = [0]
    for index, character in enumerate(source):
        if character == "\n":
            starts.append(index + 1)
    return starts


def _position_to_index(line_starts: list[int], lineno: int, col_offset: int) -> int:
    if lineno <= 0 or lineno > len(line_starts):
        msg = f"Line number {lineno} is out of range."
        raise IndexError(msg)
    return line_starts[lineno - 1] + col_offset
