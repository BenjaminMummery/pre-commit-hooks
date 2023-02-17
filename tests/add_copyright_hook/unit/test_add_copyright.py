import os
from contextlib import contextmanager

import pytest

from add_copyright_hook import add_copyright


@contextmanager
def cwd(path):
    oldcwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldcwd)


class TestGetGitUserName:
    @staticmethod
    def test_returns_configured_name(git_repo):
        username = "stub username"
        git_repo.run(f"git config user.name '{username}'")

        with cwd(git_repo.workspace):
            name = add_copyright._get_git_user_name()

        assert name == username


class TestParseArgs:
    @staticmethod
    def test_no_files(mocker):
        mocker.patch("sys.argv", ["stub name"])

        args = add_copyright._parse_args()

        assert args.files == []

    @staticmethod
    def test_single_file(mocker):
        filename = "stub_file.py"
        mocker.patch("sys.argv", ["stub_name", filename])

        args = add_copyright._parse_args()

        assert args.files == [filename]

    @staticmethod
    def test_multiple_files(mocker):
        filenames = ["stub_file_1", "stub_file_2", "subdir/stub_file_3"]
        mocker.patch("sys.argv", ["stub_name"] + filenames)

        args = add_copyright._parse_args()

        assert args.files == filenames
