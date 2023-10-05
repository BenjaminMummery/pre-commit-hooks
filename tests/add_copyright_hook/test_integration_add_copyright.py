# Copyright (c) 2023 Benjamin Mummery

from pathlib import Path

import pytest
from pytest import CaptureFixture
from pytest_mock import MockerFixture

from src.add_copyright_hook import add_copyright


class TestNoChanges:
    @staticmethod
    def test_no_files_changed(mocker: MockerFixture, capsys: CaptureFixture):
        mocker.patch("sys.argv", ["stub_name"])

        assert add_copyright.main() == 0
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

    @staticmethod
    @pytest.mark.parametrize(
        "extension, comment_format",
        [
            (".py", "# {content}"),
            (".md", "<!--- {content} -->"),
            (".cpp", "// {content}"),
            (".cs", "/* {content} */"),
            (".pl", "# {content}"),
        ],
    )
    @pytest.mark.parametrize(
        "copyright_string",
        [
            "Copyright 1111 NAME",
            "Copyright (c) 1111 NAME",
            "(c) 1111 NAME",
        ],
    )
    def test_all_changed_files_have_copyright(
        mocker: MockerFixture,
        cwd,
        tmp_path: Path,
        capsys: CaptureFixture,
        extension: str,
        comment_format: str,
        copyright_string: str,
    ):
        # GIVEN
        file = "hello" + extension
        file_content = (
            comment_format.format(content=copyright_string)
            + "\n\n<file content sentinel>"
        )
        (tmp_path / file).write_text(file_content)
        mocker.patch("sys.argv", ["stub_name", file])

        # WHEN
        with cwd(tmp_path):
            assert add_copyright.main() == 0

        # THEN
        with open(tmp_path / file, "r") as f:
            output_content = f.read()
        assert output_content == file_content
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""
