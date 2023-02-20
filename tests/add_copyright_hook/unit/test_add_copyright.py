# Copyright (c) 2023 Benjamin Mummery

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
        assert add_copyright._has_shebang(input)

    @staticmethod
    @pytest.mark.parametrize("input", ["#/usr/bin/python"])
    def test_returns_false_for_not_shebang(input):
        assert not add_copyright._has_shebang(input)


class TestConstructCopyrightString:
    @staticmethod
    @pytest.mark.parametrize("name", ["Harold Hadrada"])
    @pytest.mark.parametrize("year", ["1066"])
    def test_correct_construction(name, year):
        assert (
            add_copyright._construct_copyright_string(name, year)
            == f"# Copyright (c) {year} {name}"
        )


class TestInsertCopyrightString:
    @staticmethod
    @pytest.mark.parametrize(
        "content",
        [
            '"""docstring"""\ndef some_code():\n    pass',
        ],
    )
    def test_insterts_string(content):
        expected = "<copyright sentinel>\n\n" + content

        out = add_copyright._insert_copyright_string("<copyright sentinel>", content)

        assert out == expected

    @staticmethod
    def test_inserts_copyright_after_shebang():
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


class TestEnsureCopyrightString:
    @staticmethod
    def test_returns_0_if_file_has_copyright(tmp_path, mocker):
        p = tmp_path / "stub_file.py"
        p.write_text("<file_contents sentinel>")
        mock_copyright_check = mocker.patch(
            "add_copyright_hook.add_copyright._contains_copyright_string",
            return_value=True,
        )

        assert (
            add_copyright._ensure_copyright_string(
                p, "<name sentinel>", "<year sentinel>"
            )
            == 0
        )
        mock_copyright_check.assert_called_once_with("<file_contents sentinel>")
        with open(p) as f:
            assert f.read() == "<file_contents sentinel>"

    @staticmethod
    def test_returns_1_if_file_is_changed(tmp_path, mocker):
        p = tmp_path / "stub_file.py"
        p.write_text("<file_contents sentinel>")
        mocker.patch(
            "add_copyright_hook.add_copyright._contains_copyright_string",
            return_value=False,
        )
        mock_construct_string = mocker.patch(
            "add_copyright_hook.add_copyright._construct_copyright_string",
            return_value="<copyright string sentinel>",
        )
        mock_insert_string = mocker.patch(
            "add_copyright_hook.add_copyright._insert_copyright_string",
            return_value="<modified contents sentinel>",
        )

        assert (
            add_copyright._ensure_copyright_string(
                p, "<name sentinel>", "<year sentinel>"
            )
            == 1
        )
        mock_construct_string.assert_called_once_with(
            "<name sentinel>", "<year sentinel>"
        )
        mock_insert_string.assert_called_once_with(
            "<copyright string sentinel>", "<file_contents sentinel>"
        )
        with open(p) as f:
            assert f.read() == "<modified contents sentinel>"


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
    @pytest.mark.parametrize("config", [None, "stub config"])
    def test_returns_name_if_provided(config, mocker):
        mock_read_config = mocker.patch(
            "add_copyright_hook.add_copyright._read_config_file"
        )
        mock_get_git_name = mocker.patch(
            "add_copyright_hook.add_copyright._get_git_user_name"
        )

        name = add_copyright._resolve_user_name("<name sentinel>", config)

        assert name == "<name sentinel>"
        mock_read_config.assert_not_called()
        mock_get_git_name.assert_not_called()

    @staticmethod
    def test_read_from_config_if_config_provided(mocker):
        mock_read_config = mocker.patch(
            "add_copyright_hook.add_copyright._read_config_file",
            return_value={"name": "<name sentinel>"},
        )
        mock_get_git_name = mocker.patch(
            "add_copyright_hook.add_copyright._get_git_user_name"
        )

        name = add_copyright._resolve_user_name(None, "<config file sentinel>")

        assert name == "<name sentinel>"
        mock_read_config.assert_called_once_with("<config file sentinel>")
        mock_get_git_name.assert_not_called()

    @staticmethod
    def test_calls_get_git_user_name_if_no_name_or_config_provided(mocker):
        mock_read_config = mocker.patch(
            "add_copyright_hook.add_copyright._read_config_file"
        )
        mock_get_git_name = mocker.patch(
            "add_copyright_hook.add_copyright._get_git_user_name",
            return_value="<name sentinel>",
        )

        name = add_copyright._resolve_user_name()

        assert name == "<name sentinel>"
        mock_read_config.assert_not_called()
        mock_get_git_name.assert_called_once_with()

    @staticmethod
    def test_falls_through_if_name_missing_from_config(mocker):
        mock_read_config = mocker.patch(
            "add_copyright_hook.add_copyright._read_config_file",
            return_value={},
        )
        mock_get_git_name = mocker.patch(
            "add_copyright_hook.add_copyright._get_git_user_name",
            return_value="<name sentinel>",
        )

        name = add_copyright._resolve_user_name(None, "<config file sentinel>")

        assert name == "<name sentinel>"
        mock_read_config.assert_called_once_with("<config file sentinel>")
        mock_get_git_name.assert_called_once_with()


class TestResolveYear:
    @staticmethod
    @pytest.mark.parametrize("config", [None, "stub config"])
    def test_returns_name_if_provided(config, mocker):
        mock_read_config = mocker.patch(
            "add_copyright_hook.add_copyright._read_config_file"
        )
        mock_get_current_year = mocker.patch(
            "add_copyright_hook.add_copyright._get_current_year"
        )

        year = add_copyright._resolve_year("<year sentinel>", config)

        assert year == "<year sentinel>"
        mock_read_config.assert_not_called()
        mock_get_current_year.assert_not_called()

    @staticmethod
    def test_read_from_config_if_config_provided(mocker):
        mock_read_config = mocker.patch(
            "add_copyright_hook.add_copyright._read_config_file",
            return_value={"year": "<year sentinel>"},
        )
        mock_get_current_year = mocker.patch(
            "add_copyright_hook.add_copyright._get_current_year"
        )

        year = add_copyright._resolve_year(None, "<config file sentinel>")

        assert year == "<year sentinel>"
        mock_read_config.assert_called_once_with("<config file sentinel>")
        mock_get_current_year.assert_not_called()

    @staticmethod
    def test_calls_get_git_user_name_if_no_name_or_config_provided(mocker):
        mock_read_config = mocker.patch(
            "add_copyright_hook.add_copyright._read_config_file"
        )
        mock_get_current_year = mocker.patch(
            "add_copyright_hook.add_copyright._get_current_year",
            return_value="<year sentinel>",
        )

        year = add_copyright._resolve_year()

        assert year == "<year sentinel>"
        mock_read_config.assert_not_called()
        mock_get_current_year.assert_called_once_with()

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

        assert files == [Path("hello.txt")]

    @staticmethod
    def test_returns_list_for_multiple_valid_files(tmp_path):
        p1 = tmp_path / "hello.txt"
        p2 = tmp_path / "goodbye.py"
        for file in [p1, p2]:
            file.write_text("")

        with cwd(tmp_path):
            files = add_copyright._resolve_files(["hello.txt", "goodbye.py"])

        assert files == [Path("hello.txt"), Path("goodbye.py")]

    @staticmethod
    def test_raises_exception_for_missing_file(tmp_path):
        p1 = tmp_path / "hello.txt"
        p1.write_text("")

        with cwd(tmp_path):
            with pytest.raises(FileNotFoundError):
                add_copyright._resolve_files(["hello.txt", "goodbye.py"])


class TestReadConfigFile:
    @staticmethod
    @pytest.mark.parametrize("invalid_file_name", ["foo.txt", "var.cfg"])
    def test_raises_exception_if_not_supported_type(invalid_file_name):
        with pytest.raises(FileNotFoundError):
            add_copyright._read_config_file(invalid_file_name)

    @staticmethod
    @pytest.mark.parametrize(
        "filename, file_contents",
        [
            (
                "stub_filename.json",
                (
                    "{\n"
                    '    "name": "<name sentinel>",\n'
                    '    "year": "<year sentinel>"\n'
                    "}\n"
                ),
            ),
            (
                "stub_filename.yaml",
                ("name: <name sentinel>\n" "year: <year sentinel>\n"),
            ),
        ],
    )
    def test_reads_config_file(tmp_path, filename, file_contents):
        p = tmp_path / filename
        p.write_text(file_contents)

        data = add_copyright._read_config_file(p)

        assert data == {"name": "<name sentinel>", "year": "<year sentinel>"}


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
    def test_argument_passing_year_name(
        mocker, file_arg, name_arg, expected_name, year_arg, expected_year
    ):
        mock_name_resolver = mocker.patch(
            "add_copyright_hook.add_copyright._resolve_user_name",
            return_value="<name sentinel>",
        )
        mock_year_resolver = mocker.patch(
            "add_copyright_hook.add_copyright._resolve_year",
            return_value="<year sentinel>",
        )
        mock_file_resolver = mocker.patch(
            "add_copyright_hook.add_copyright._resolve_files",
            return_value="<file sentinel>",
        )
        mocker.patch("sys.argv", ["stub", *file_arg, *name_arg, *year_arg])

        args = add_copyright._parse_args()

        mock_name_resolver.assert_called_once_with(expected_name, None)
        mock_year_resolver.assert_called_once_with(expected_year, None)
        mock_file_resolver.assert_called_once_with(file_arg)
        assert args.name == "<name sentinel>"
        assert args.year == "<year sentinel>"
        assert args.files == "<file sentinel>"

    @staticmethod
    @pytest.mark.parametrize(
        "file_arg", [[], ["stub_file"], ["stub_file_1", "stub_file_2"]]
    )
    @pytest.mark.parametrize(
        "config_arg, expected_config",
        [
            (["-c", "<config sentinel>"], "<config sentinel>"),
            (["--config", "<config sentinel>"], "<config sentinel>"),
            ([], None),
        ],
    )
    def test_argument_passing_config(file_arg, config_arg, expected_config, mocker):
        mock_name_resolver = mocker.patch(
            "add_copyright_hook.add_copyright._resolve_user_name",
            return_value="<name sentinel>",
        )
        mock_year_resolver = mocker.patch(
            "add_copyright_hook.add_copyright._resolve_year",
            return_value="<year sentinel>",
        )
        mock_file_resolver = mocker.patch(
            "add_copyright_hook.add_copyright._resolve_files",
            return_value="<file sentinel>",
        )
        mocker.patch("sys.argv", ["stub", *file_arg, *config_arg])

        args = add_copyright._parse_args()

        mock_name_resolver.assert_called_once_with(None, expected_config)
        mock_year_resolver.assert_called_once_with(None, expected_config)
        mock_file_resolver.assert_called_once_with(file_arg)
        assert args.name == "<name sentinel>"
        assert args.year == "<year sentinel>"
        assert args.files == "<file sentinel>"

    @staticmethod
    @pytest.mark.parametrize(
        "clashing_option",
        [
            ["-n", "stub_name"],
            ["-y", "stub_year"],
        ],
    )
    def test_raises_sysexit_if_clashing_options(clashing_option, mocker, capsys):
        sentinel = "-c and -n|-y are mutually exclusive."
        mocker.patch("sys.argv", ["stub", *clashing_option, "-c", "stub_config"])

        with pytest.raises(SystemExit):
            add_copyright._parse_args()

        assert sentinel in capsys.readouterr().out
