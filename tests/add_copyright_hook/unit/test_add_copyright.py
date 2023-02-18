import os
from contextlib import contextmanager

import pytest
from freezegun import freeze_time

from add_copyright_hook import add_copyright


@contextmanager
def cwd(path):
    oldcwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldcwd)


class TestGetCurrentYear:
    @staticmethod
    @freeze_time("2012-01-01")
    def test_returns_year_string():
        year = add_copyright._get_current_year()

        assert isinstance(year, str)
        assert year == "2012"


class TestGetGitUserName:
    @staticmethod
    def test_returns_configured_name(git_repo):
        username = "stub username"
        git_repo.run(f"git config user.name '{username}'")

        with cwd(git_repo.workspace):
            name = add_copyright._get_git_user_name()

        assert name == username


class TestParseArgs:
    class TestParseFilenames:
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

    class TestParseCopyrightHolderName:
        @staticmethod
        def test_no_name_set(mocker):
            mocker.patch("sys.argv", ["stub_name"])

            args = add_copyright._parse_args()

            assert args.name is None

        @staticmethod
        @pytest.mark.parametrize("username", ["stub", "stub_name"])
        @pytest.mark.parametrize("toggle", ["-n", "--name"])
        def test_single_word(mocker, username, toggle):
            mocker.patch("sys.argv", ["stub_name", toggle, username])

            args = add_copyright._parse_args()

            assert args.name == username
