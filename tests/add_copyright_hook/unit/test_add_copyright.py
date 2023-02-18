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


class TestResolveUserName:
    @staticmethod
    def test_returns_name_if_provided():
        username = "stub username"

        name = add_copyright._resolve_user_name(username)

        assert name == username

    @staticmethod
    def test_calls_get_git_user_name_if_no_name_provided(mocker):
        username = "stub username"
        mocked_get_git_user_name = mocker.patch(
            "add_copyright_hook.add_copyright._get_git_user_name", return_value=username
        )

        name = add_copyright._resolve_user_name()

        assert name == username
        mocked_get_git_user_name.assert_called_once()

    @staticmethod
    def test_raises_valueerror_if_get_git_user_name_errors(mocker):
        mocked_get_git_user_name = mocker.patch(
            "add_copyright_hook.add_copyright._get_git_user_name",
            side_effect=ValueError,
        )

        with pytest.raises(ValueError):
            add_copyright._resolve_user_name()
        mocked_get_git_user_name.assert_called_once()


class TestResolveYear:
    @staticmethod
    def test_returns_year_if_provided():
        inputyear = "stub_year"

        year = add_copyright._resolve_year(inputyear)

        assert year == inputyear

    @staticmethod
    def test_calls_get_current_year_if_no_name_provided(mocker):
        currentyear = "1984"
        mocked_get_current_year = mocker.patch(
            "add_copyright_hook.add_copyright._get_current_year",
            return_value=currentyear,
        )

        year = add_copyright._resolve_year()

        assert year == currentyear
        mocked_get_current_year.assert_called_once()


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
