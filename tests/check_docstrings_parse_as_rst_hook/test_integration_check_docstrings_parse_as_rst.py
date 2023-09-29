# Copyright (c) 2023 Benjamin Mummery

from pathlib import Path
from typing import List

from src.check_docstrings_parse_as_rst_hook import check_docstrings_parse_as_rst


def mock_file_content(
    tmp_path: Path, files: List[str], input_content_filename: str, mocker
):
    with open(f"tests/examples/{input_content_filename}") as f:
        input_content = f.read()
    for file in files:
        f = tmp_path / file
        f.write_text(input_content)
    mocker.patch("sys.argv", ["stub_name"] + files)
    return input_content


class TestNoChanges:
    @staticmethod
    def test_no_files_changed(mocker):
        mocker.patch("sys.argv", ["stub_name"])

        assert check_docstrings_parse_as_rst.main() == 0

    @staticmethod
    def test_no_changed_files_have_docstrings(mocker, cwd, tmp_path):
        # GIVEN
        files = ["hello.py", ".hello.py", "_hello.py"]
        file_content = mock_file_content(tmp_path, files, "no_docstrings.py", mocker)

        # WHEN
        with cwd(tmp_path):
            assert check_docstrings_parse_as_rst.main() == 0

        # THEN
        for file in files:
            with open(tmp_path / file, "r") as f:
                output_content = f.read()
            assert output_content == file_content

    @staticmethod
    def test_all_docstrings_are_correct_rst(mocker, cwd, tmp_path):
        # GIVEN
        files = ["hello.py", ".hello.py", "_hello.py"]
        file_content = mock_file_content(tmp_path, files, "valid_rst_python.py", mocker)

        # WHEN
        with cwd(tmp_path):
            assert check_docstrings_parse_as_rst.main() == 0

        # THEN
        for file in files:
            with open(tmp_path / file, "r") as f:
                output_content = f.read()
        assert output_content == file_content


class TestBadRST:
    @staticmethod
    def test_returns_1_for_single_bad_docstring(mocker, cwd, tmp_path: Path):
        # GIVEN
        files = ["hello.py", ".hello.py", "_hello.py"]
        file_content = mock_file_content(
            tmp_path, files, "invalid_rst_python.py", mocker
        )

        # WHEN
        with cwd(tmp_path):
            assert check_docstrings_parse_as_rst.main() == 1

        # THEN
        for file in files:
            with open(tmp_path / file, "r") as f:
                output_content = f.read()
        assert output_content == file_content
