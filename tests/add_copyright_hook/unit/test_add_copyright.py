import os
from contextlib import contextmanager
from pathlib import Path

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


class TestContainsCopyrightString:
    @staticmethod
    @pytest.mark.parametrize(
        "input_string",
        [
            "# Copyright 2023 Benjamin Mummery",
            "# Copyright (c) 2023 Benjamin Mummery",
            "#Copyright 8923 Hugo Drax",
            "# copyright 1234 Qwe Rty",
            "# COPYRIGHT 5678 Uio Pas",
            "unconnected first line\n# Copyright 1984 Aldous Huxley",
        ],
    )
    def test_returns_true_for_correct_strings(input_string):
        assert add_copyright._contains_copyright_string(input_string)

    @staticmethod
    @pytest.mark.parametrize(
        "input_string", ["Not a comment", "# Not a copyright string"]
    )
    def test_returns_false_for_incorrect_strings(input_string):
        assert not add_copyright._contains_copyright_string(input_string)


class TestIsShebang:
    @staticmethod
    @pytest.mark.parametrize("input", ["#!/usr/bin/python"])
    def test_returns_true_for_shebang(input):
        assert add_copyright._is_shebang(input)

    @staticmethod
    @pytest.mark.parametrize("input", ["#/usr/bin/python"])
    def test_returns_false_for_not_shebang(input):
        assert not add_copyright._is_shebang(input)


class TestConstructCopyrightString:
    @staticmethod
    @pytest.mark.parametrize("name", ["Harold Hadrada"])
    @pytest.mark.parametrize("year", ["1066"])
    def test_correct_construction(name, year):
        expected = f"# Copyright (c) {year} {name}"
        print(expected)
        assert add_copyright._construct_copyright_string(name, year) == expected


class TestInsertCopyrightString:
    @staticmethod
    @pytest.mark.parametrize(
        "content",
        [
            '"""docstring"""\ndef some_code():\n    pass',
        ],
    )
    def test_insterts_string(content):
        expected = "<copyright sentinel>\n" + content

        out = add_copyright._insert_copyright_string("<copyright sentinel>", content)

        assert out == expected

    @staticmethod
    def test_insterts_copyright_after_shebang():
        content = (
            "#!shebang\n" "\n" '"""docstring"""\n' "\n" "def some_code():\n" "    pass"
        )
        expected = (
            "#!shebang\n"
            "\n"
            "<copyright sentinel>\n"
            "\n"
            '"""docstring"""\n'
            "\n"
            "def some_code():\n"
            "    pass"
        )

        out = add_copyright._insert_copyright_string("<copyright sentinel>", content)
        assert out == expected


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


class TestResolveFiles:
    @staticmethod
    def test_returns_empty_list_for_empty_input():
        files = add_copyright._resolve_files([])

        assert files == []

    @staticmethod
    def test_returns_list_for_single_valid_file(tmp_path):
        p = tmp_path / "hello.txt"
        p.write_text("")

        with cwd(tmp_path):
            files = add_copyright._resolve_files("hello.txt")

        assert files == [Path(p).absolute()]

    @staticmethod
    def test_returns_list_for_multiple_valid_files(tmp_path):
        p1 = tmp_path / "hello.txt"
        p2 = tmp_path / "goodbye.py"
        for file in [p1, p2]:
            file.write_text("")

        with cwd(tmp_path):
            files = add_copyright._resolve_files(["hello.txt", "goodbye.py"])

        assert files == [Path(p1).absolute(), Path(p2).absolute()]

    @staticmethod
    def test_raises_exception_for_missing_file(tmp_path):
        p1 = tmp_path / "hello.txt"
        p1.write_text("")

        with cwd(tmp_path):
            with pytest.raises(FileNotFoundError):
                add_copyright._resolve_files(["hello.txt", "goodbye.py"])


class TestParseArgs:
    @staticmethod
    @pytest.mark.parametrize(
        "file_arg", [[], ["stub_file"], ["stub_file_1", "stub_file_2"]]
    )
    @pytest.mark.parametrize(
        "name_arg, expected_name",
        [
            (["-n", "stub_name"], "stub_name"),
            (["--name", "stub_name"], "stub_name"),
            ([], None),
        ],
    )
    @pytest.mark.parametrize(
        "year_arg, expected_year",
        [
            (["-y", "stub_year"], "stub_year"),
            (["--year", "stub_year"], "stub_year"),
            ([], None),
        ],
    )
    def test_argument_passing(
        mocker, file_arg, name_arg, expected_name, year_arg, expected_year
    ):
        mock_name_resolver = mocker.patch(
            "add_copyright_hook.add_copyright._resolve_user_name",
            return_value="name sentinel",
        )
        mock_year_resolver = mocker.patch(
            "add_copyright_hook.add_copyright._resolve_year",
            return_value="year sentinel",
        )
        mock_file_resolver = mocker.patch(
            "add_copyright_hook.add_copyright._resolve_files",
            return_value="file sentinel",
        )
        mocker.patch("sys.argv", ["stub", *file_arg, *name_arg, *year_arg])

        args = add_copyright._parse_args()

        mock_name_resolver.assert_called_once_with(expected_name)
        mock_year_resolver.assert_called_once_with(expected_year)
        mock_file_resolver.assert_called_once_with(file_arg)
        assert args.name == "name sentinel"
        assert args.year == "year sentinel"
        assert args.files == "file sentinel"
