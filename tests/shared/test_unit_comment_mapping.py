# Copyright (c) 2023 Benjamin Mummery

from pathlib import Path

import pytest

from src._shared import comment_mapping


class TestGetCommentMarkers:
    @staticmethod
    @pytest.mark.parametrize(
        "file_extension, expected_markers",
        [
            # Hash comment types
            (".pl", ("#", None)),
            (".py", ("#", None)),
            # Slash comment types
            (".cpp", ("//", None)),
            (".dart", ("//", None)),
            (".java", ("//", None)),
            (".js", ("//", None)),
            (".kt", ("//", None)),
            (".kts", ("//", None)),
            (".PHP", ("//", None)),
            (".rs", ("//", None)),
            (".scala", ("//", None)),
            # HTML comment types
            (".html", ("<!---", "-->")),
            (".md", ("<!---", "-->")),
            # Dash comment types
            (".lua", ("--", None)),
            (".sql", ("--", None)),
            # CSS comment types
            (".css", ("/*", "*/")),
        ],
    )
    def test_for_supported_file_types(file_extension, expected_markers, tmp_path: Path):
        file_path = tmp_path / f"filename{file_extension}"
        file_path.write_text("")

        start, end = comment_mapping.get_comment_markers(file_path)

        assert start == expected_markers[0]
        assert end == expected_markers[1]

    @staticmethod
    def test_raises_NotImplementedError_for_unsupported_file_types(tmp_path):
        file_path = tmp_path / "filename.not_real"
        file_path.write_text("")

        with pytest.raises(NotImplementedError):
            _ = comment_mapping.get_comment_markers(file_path)
