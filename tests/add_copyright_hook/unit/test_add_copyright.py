# Copyright (c) 2023 Benjamin Mummery

"""
Unit tests for add_copyright.

Tests mock every method except the one they are directly testing. This ensures that
tests are true unit tests, and means that coverage reports for unit tests are accurate.
"""

import pytest
from freezegun import freeze_time

from src.add_copyright_hook import add_copyright

from ...conftest import ADD_COPYRIGHT_FIXTURE_LIST as FIXTURES


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_parse_copyright_string"])
class TestParseCopyrightString:
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
            "# © 9999 Obi Wan Kenobi",
            "# Copyright © 9876 Gandalf the Grey",
            "# copyright 1234-5678 Huron Blackheart",
            "# (c) 8524 - 6987 Horus Lupercal",
        ],
    )
    def test_returns_true_for_correct_strings(input_string, mock_parse_years):
        mock_parse_years.return_value = (0, 0)
        assert add_copyright._parse_copyright_string(input_string)

    @staticmethod
    @pytest.mark.parametrize(
        "input_string", ["Not a comment", "# Not a copyright string"]
    )
    def test_returns_false_for_incorrect_strings(input_string):
        assert not add_copyright._parse_copyright_string(input_string)


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_parse_years"])
class TestParseYears:
    pass


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_has_shebang"])
class TestHasShebang:
    @staticmethod
    @pytest.mark.parametrize("input", ["#!/usr/bin/python"])
    def test_returns_true_for_shebang(input):
        assert add_copyright._has_shebang(input)

    @staticmethod
    @pytest.mark.parametrize("input", ["#/usr/bin/python"])
    def test_returns_false_for_no_shebang(input):
        assert not add_copyright._has_shebang(input)


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f != "mock_construct_copyright_string"]
)
class TestConstructCopyrightString:
    @staticmethod
    @pytest.mark.parametrize("name", ["Harold Hadrada"])
    @pytest.mark.parametrize("year", ["1066"])
    @pytest.mark.parametrize(
        "format",
        ["# Copyright (c) {year} {name}", "{name} owns this as of {year}, hands off!"],
    )
    def test_correct_construction(name, year, format):
        assert add_copyright._construct_copyright_string(
            name, year, format
        ) == format.format(year=year, name=name)


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_insert_copyright_string"])
class TestInsertCopyrightString:
    @staticmethod
    @pytest.mark.parametrize(
        "content",
        [
            '"""docstring"""\ndef some_code():\n    pass',
        ],
    )
    def test_inserts_string(content, mock_has_shebang):
        mock_has_shebang.return_value = False
        expected = "<copyright sentinel>\n\n" + content

        out = add_copyright._insert_copyright_string("<copyright sentinel>", content)

        assert out == expected, f"Out:\n{out}\nexpected:\n{expected}"

    @staticmethod
    def test_inserts_copyright_after_shebang(mock_has_shebang):
        mock_has_shebang.return_value = True
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


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_ensure_copyright_string"])
class TestEnsureCopyrightString:
    @staticmethod
    def test_returns_0_if_file_has_current_copyright(
        tmp_path, mocker, mock_parse_copyright_string
    ):
        p = tmp_path / "stub_file.py"
        p.write_text("<file_contents sentinel>")

        mock_parse_copyright_string.return_value = mocker.Mock(end_year=1111)

        assert (
            add_copyright._ensure_copyright_string(p, "<name sentinel>", "1111", None)
            == 0
        )
        mock_parse_copyright_string.assert_called_once_with("<file_contents sentinel>")
        with open(p) as f:
            assert f.read() == "<file_contents sentinel>"

    @staticmethod
    def test_returns_1_if_file_is_changed(
        tmp_path,
        mocker,
        mock_parse_copyright_string,
        mock_construct_copyright_string,
        mock_insert_copyright_string,
    ):
        # GIVEN
        p = tmp_path / "stub_file.py"
        p.write_text("<file_contents sentinel>")
        mock_parse_copyright_string.return_value = False
        mock_construct_copyright_string.return_value = "<copyright string sentinel>"
        mock_insert_copyright_string.return_value = "<modified contents sentinel>"

        # WHEN
        assert (
            add_copyright._ensure_copyright_string(
                p, "<name sentinel>", "<year sentinel>", "<format sentinel>"
            )
            == 1
        )

        # THEN
        mock_construct_copyright_string.assert_called_once_with(
            "<name sentinel>", "<year sentinel>", "<format sentinel>"
        )
        mock_insert_copyright_string.assert_called_once_with(
            "<copyright string sentinel>", "<file_contents sentinel>"
        )
        with open(p) as f:
            assert f.read() == "<modified contents sentinel>"


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_get_current_year"])
class TestGetCurrentYear:
    @staticmethod
    @freeze_time("2012-01-01")
    def test_returns_year_int():
        year = add_copyright._get_current_year()

        assert isinstance(year, int)
        assert year == 2012


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_get_git_user_name"])
class TestGetGitUserName:
    @staticmethod
    def test_returns_configured_name(git_repo, cwd):
        username = "<username sentinel>"
        git_repo.run(f"git config user.name '{username}'")

        with cwd(git_repo.workspace):
            name = add_copyright._get_git_user_name()

        assert name == username


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_resolve_user_name"])
class TestResolveUserName:
    @staticmethod
    @pytest.mark.parametrize("config", [None, "stub config"])
    def test_returns_name_if_provided(
        config, mock_read_config_file, mock_get_git_user_name
    ):
        name = add_copyright._resolve_user_name("<name sentinel>", config)

        assert name == "<name sentinel>"
        mock_read_config_file.assert_not_called()
        mock_get_git_user_name.assert_not_called()

    @staticmethod
    def test_read_name_from_config_if_config_provided(
        mock_read_config_file, mock_get_git_user_name
    ):
        # GIVEN
        mock_read_config_file.return_value = {"name": "<name sentinel>"}

        # WHEN
        name = add_copyright._resolve_user_name(
            name=None, config="<config file sentinel>"
        )

        # THEN
        assert name == "<name sentinel>"
        mock_read_config_file.assert_called_once_with("<config file sentinel>")
        mock_get_git_user_name.assert_not_called()

    @staticmethod
    def test_calls_get_git_user_name_if_no_name_or_config_provided(
        mock_get_git_user_name, mock_read_config_file
    ):
        # GIVEN
        mock_get_git_user_name.return_value = "<name sentinel>"

        # WHEN
        name = add_copyright._resolve_user_name()

        # THEN
        assert name == "<name sentinel>"
        mock_read_config_file.assert_not_called()
        mock_get_git_user_name.assert_called_once_with()

    @staticmethod
    def test_calls_get_git_user_name_if_name_missing_from_config(
        mock_get_git_user_name, mock_read_config_file
    ):
        # GIVEN
        mock_get_git_user_name.return_value = "<name sentinel>"

        # WHEN
        name = add_copyright._resolve_user_name(None, "<config file sentinel>")

        # THEN
        assert name == "<name sentinel>"
        mock_read_config_file.assert_called_once_with("<config file sentinel>")
        mock_get_git_user_name.assert_called_once_with()


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_resolve_year"])
class TestResolveYear:
    @staticmethod
    @pytest.mark.parametrize("config", [None, "stub config"])
    def test_returns_year_if_provided(
        config, mock_read_config_file, mock_get_current_year
    ):
        # WHEN
        year = add_copyright._resolve_year("<year sentinel>", config=config)

        # THEN
        assert year == "<year sentinel>"
        mock_read_config_file.assert_not_called()
        mock_get_current_year.assert_not_called()

    @staticmethod
    def test_read_year_from_config_if_config_provided(
        mock_read_config_file, mock_get_current_year
    ):
        # GIVEN
        mock_read_config_file.return_value = {"year": "<year sentinel>"}

        # WHEN
        year = add_copyright._resolve_year(None, "<config file sentinel>")

        # THEN
        assert year == "<year sentinel>"
        mock_read_config_file.assert_called_once_with("<config file sentinel>")
        mock_get_current_year.assert_not_called()

    @staticmethod
    def test_calls_get_current_year_if_no_year_or_config_provided(
        mock_read_config_file, mock_get_current_year
    ):
        # GIVEN
        mock_get_current_year.return_value = "<year_sentinel>"

        # WHEN
        year = add_copyright._resolve_year()

        # THEN
        assert year == "<year_sentinel>"
        mock_read_config_file.assert_not_called()
        mock_get_current_year.assert_called_once()

    @staticmethod
    def test_calls_get_current_year_if_year_missing_from_config(
        mock_read_config_file, mock_get_current_year
    ):
        # GIVEN
        mock_get_current_year.return_value = "<year_sentinel>"

        # WHEN
        year = add_copyright._resolve_year(None, "<config file sentinel>")

        # THEN
        assert year == "<year_sentinel>"
        mock_read_config_file.assert_called_once_with("<config file sentinel>")
        mock_get_current_year.assert_called_once_with()


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_resolve_format"])
class TestResolveFormat:
    @staticmethod
    def test_returns_format_if_provided(mock_ensure_valid_format):
        # GIVEN
        mock_ensure_valid_format.return_value = "<checked format sentinel>"

        # WHEN
        assert (
            add_copyright._resolve_format("<format sentinel>", None)
            == "<checked format sentinel>"
        )
        # THEN
        mock_ensure_valid_format.assert_called_once_with("<format sentinel>")

    @staticmethod
    def test_read_from_config_if_config_provided(
        mock_ensure_valid_format, mock_read_config_file
    ):
        mock_read_config_file.return_value = {"format": "<format sentinel>"}
        mock_ensure_valid_format.return_value = "<checked format sentinel>"

        assert (
            add_copyright._resolve_format(None, "<config file sentinel>")
            == "<checked format sentinel>"
        )
        mock_read_config_file.assert_called_once_with("<config file sentinel>")
        mock_ensure_valid_format.assert_called_once_with("<format sentinel>")

    @staticmethod
    def test_returns_default_if_provided_config_lacks_format_field(
        mocker, mock_read_config_file, mock_ensure_valid_format, mock_default_format
    ):
        # GIVEN
        mock_ensure_valid_format.return_value = "<checked format sentinel>"

        # WHEN
        assert (
            add_copyright._resolve_format(None, "<config file sentinel>")
            == "<checked format sentinel>"
        )

        # THEN
        mock_read_config_file.assert_called_once_with("<config file sentinel>")
        mock_ensure_valid_format.assert_called_once_with(mock_default_format)

    @staticmethod
    def test_chooses_format_arg_over_config(
        mock_ensure_valid_format, mock_read_config_file
    ):
        # GIVEN
        mock_ensure_valid_format.return_value = "<checked format sentinel>"

        # WHEN
        assert (
            add_copyright._resolve_format("<format sentinel>", "<config file sentinel>")
            == "<checked format sentinel>"
        )

        # THEN
        mock_read_config_file.assert_not_called()
        mock_ensure_valid_format.assert_called_once_with("<format sentinel>")

    @staticmethod
    def test_returns_default_if_no_format_or_config(
        mock_ensure_valid_format, mock_default_format
    ):
        # GIVEN
        mock_ensure_valid_format.return_value = "<checked format sentinel>"

        # WHEN
        assert add_copyright._resolve_format(None, None) == "<checked format sentinel>"

        # THEN
        mock_ensure_valid_format.assert_called_once_with(mock_default_format)


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_ensure_valid_format"])
class TestEnsureValidFormat:
    @staticmethod
    @pytest.mark.parametrize(
        "input_format",
        [
            "{name} {year}",
            "Property of {name} as of {year}.",
            "Copyright (c) {year} {name}",
        ],
    )
    def test_returns_valid_format_strings(input_format):
        assert add_copyright._ensure_valid_format(input_format) == input_format

    @staticmethod
    @pytest.mark.parametrize("input_format", ["Nope"])
    def test_raises_keyerror_for_invalid_format_strings(input_format):
        with pytest.raises(KeyError):
            assert add_copyright._ensure_valid_format(input_format) == input_format


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_read_config_file"])
class TestReadConfigFile:
    @staticmethod
    def test_raises_exception_if_file_does_not_exist(tmp_path, cwd):
        with cwd(tmp_path):
            with pytest.raises(FileNotFoundError):
                add_copyright._read_config_file("not_a_real_file.blah")

    @staticmethod
    @pytest.mark.parametrize("invalid_file_name", ["foo.txt", "var.cfg"])
    def test_raises_exception_if_not_supported_type(invalid_file_name, tmp_path, cwd):
        p = tmp_path / invalid_file_name
        p.write_text("")

        with cwd(tmp_path):
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


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_parse_args"])
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
    @pytest.mark.parametrize(
        "format_arg, expected_format",
        [
            (["-f", "stub_format"], "stub_format"),
            (["--format", "stub_format"], "stub_format"),
            ([], None),
        ],
    )
    def test_argument_passing_year_name_format(
        file_arg,
        name_arg,
        expected_name,
        year_arg,
        expected_year,
        format_arg,
        expected_format,
        mock_resolve_user_name,
        mock_resolve_year,
        mock_resolve_format,
        mock_resolve_files,
        mocker,
    ):
        # GIVEN
        mock_resolve_user_name.return_value = "<name sentinel>"
        mock_resolve_year.return_value = "<year sentinel>"
        mock_resolve_format.return_value = "<format sentinel>"
        mock_resolve_files.return_value = "<file sentinel>"
        mocker.patch("sys.argv", ["stub", *file_arg, *name_arg, *format_arg, *year_arg])

        # WHEN
        args = add_copyright._parse_args()

        # THEN
        mock_resolve_user_name.assert_called_once_with(expected_name, None)
        mock_resolve_year.assert_called_once_with(expected_year, None)
        mock_resolve_format.assert_called_once_with(expected_format, None)
        mock_resolve_files.assert_called_once_with(file_arg)
        assert args.name == "<name sentinel>"
        assert args.year == "<year sentinel>"
        assert args.format == "<format sentinel>"
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
    def test_argument_passing_config(
        file_arg,
        config_arg,
        expected_config,
        mocker,
        mock_resolve_user_name,
        mock_resolve_year,
        mock_resolve_format,
        mock_resolve_files,
    ):
        # GIVEN
        mock_resolve_user_name.return_value = "<name sentinel>"
        mock_resolve_year.return_value = "<year sentinel>"
        mock_resolve_format.return_value = "<format sentinel>"
        mock_resolve_files.return_value = "<file sentinel>"
        mocker.patch("sys.argv", ["stub", *file_arg, *config_arg])

        args = add_copyright._parse_args()

        mock_resolve_user_name.assert_called_once_with(None, expected_config)
        mock_resolve_year.assert_called_once_with(None, expected_config)
        mock_resolve_format.assert_called_once_with(None, expected_config)
        mock_resolve_files.assert_called_once_with(file_arg)
        assert args.name == "<name sentinel>"
        assert args.year == "<year sentinel>"
        assert args.format == "<format sentinel>"
        assert args.files == "<file sentinel>"

    @staticmethod
    @pytest.mark.parametrize(
        "clashing_option",
        [
            ["-n", "stub_name"],
            ["-y", "stub_year"],
            ["-f", "stub_format"],
        ],
    )
    def test_raises_sysexit_if_clashing_options(clashing_option, mocker, capsys):
        sentinel = "-c and -n|-y|-f are mutually exclusive."
        mocker.patch("sys.argv", ["stub", *clashing_option, "-c", "stub_config"])

        with pytest.raises(SystemExit):
            add_copyright._parse_args()

        assert sentinel in capsys.readouterr().out
