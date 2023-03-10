# Copyright (c) 2023 Benjamin Mummery

import os
from contextlib import contextmanager

from sort_file_contents_hook import sort_file_contents


@contextmanager
def cwd(path):
    oldcwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldcwd)


class TestFileSorting:
    @staticmethod
    def test_no_sections(tmp_path, mocker):
        file_contents = "beta\n" "delta\n" "gamma\n" "alpha\n"
        sorted_file = "alpha\n" "beta\n" "delta\n" "gamma\n"
        file = tmp_path / ".gitignore"
        file.write_text(file_contents)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        assert sort_file_contents.main() == 1

        with open(file, "r") as f:
            content: str = f.read()
        assert content == sorted_file

    @staticmethod
    def test_with_sections(tmp_path, mocker):
        file_contents = "beta\n" "delta\n" "\n" "gamma\n" "alpha\n"
        sorted_file = "beta\n" "delta\n" "\n" "alpha\n" "gamma\n"
        file = tmp_path / ".gitignore"
        file.write_text(file_contents)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        assert sort_file_contents.main() == 1

        with open(file, "r") as f:
            content: str = f.read()
        assert content == sorted_file

    @staticmethod
    def test_with_leading_comment(tmp_path, mocker):
        file_contents = "# zulu\n" "beta\n" "delta\n" "gamma\n" "alpha\n"
        sorted_file = "# zulu\n" "alpha\n" "beta\n" "delta\n" "gamma\n"
        file = tmp_path / ".gitignore"
        file.write_text(file_contents)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        assert sort_file_contents.main() == 1

        with open(file, "r") as f:
            content: str = f.read()
        assert content == sorted_file

    @staticmethod
    def test_multiple_sections_with_leading_comment(tmp_path, mocker):
        file_contents = (
            "# zulu\n" "beta\n" "delta\n" "\n" "# epsilon\n" "gamma\n" "alpha\n"
        )
        sorted_file = (
            "# zulu\n" "beta\n" "delta\n" "\n" "# epsilon\n" "alpha\n" "gamma\n"
        )
        file = tmp_path / ".gitignore"
        file.write_text(file_contents)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        assert sort_file_contents.main() == 1

        with open(file, "r") as f:
            content: str = f.read()
            print(content)
        assert content == sorted_file

    @staticmethod
    def test_with_commented_line_in_section(tmp_path, mocker):
        file_contents = "beta\n" "# zulu\n" "delta\n" "gamma\n" "alpha\n"
        sorted_file = "alpha\n" "beta\n" "delta\n" "gamma\n" "# zulu\n"
        file = tmp_path / ".gitignore"
        file.write_text(file_contents)

        mocker.patch("sys.argv", ["stub_name", str(file)])

        assert sort_file_contents.main() == 1

        with open(file, "r") as f:
            content: str = f.read()
        assert content == sorted_file

    @staticmethod
    def test_with_floating_comment(tmp_path, mocker):
        file_contents = "beta\n" "delta\n" "\n" "# zulu\n" "\n" "gamma\n" "alpha\n"
        sorted_file = "beta\n" "delta\n" "\n" "# zulu\n" "\n" "alpha\n" "gamma\n"
        file = tmp_path / ".gitignore"
        file.write_text(file_contents)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        assert sort_file_contents.main() == 1

        with open(file, "r") as f:
            content: str = f.read()
        assert content == sorted_file


class TestNoChanges:
    @staticmethod
    def test_empty_file(tmp_path, mocker):
        file_contents = ""
        sorted_file = ""
        file = tmp_path / ".gitignore"
        file.write_text(file_contents)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        assert sort_file_contents.main() == 0

        with open(file, "r") as f:
            content: str = f.read()
        assert content == sorted_file
