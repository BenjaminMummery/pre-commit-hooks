# Copyright (c) 2023 Benjamin Mummery

"""
Unit tests for add_copyright.

Tests mock every method except the one they are directly testing. This ensures that
tests are true unit tests, and means that coverage reports for unit tests are accurate.
"""

import argparse
from datetime import datetime
from unittest.mock import Mock, call, create_autospec

import git
import pytest
from freezegun import freeze_time

from src.add_copyright_hook import add_copyright

from ..conftest import ADD_COPYRIGHT_FIXTURE_LIST as FIXTURES


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
        # GIVEN
        mock_parse_years.return_value = (0, 0)

        # WHEN
        # THEN
        assert add_copyright._parse_copyright_string(input_string)

    @staticmethod
    @pytest.mark.parametrize(
        "input_string", ["Not a comment", "# Not a copyright string"]
    )
    def test_returns_false_for_incorrect_strings(input_string):
        assert not add_copyright._parse_copyright_string(input_string)


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_parse_years"])
class TestParseYears:
    @staticmethod
    @pytest.mark.parametrize("input, expected_output", [("1984", (1984, 1984))])
    def test_parses_single_years(input, expected_output):
        assert add_copyright._parse_years(input) == expected_output

    @staticmethod
    @pytest.mark.parametrize(
        "input, expected_output",
        [
            ("1984-2000", (1984, 2000)),
            ("1234 - 5678", (1234, 5678)),
        ],
    )
    def test_parses_year_ranges(input, expected_output):
        assert add_copyright._parse_years(input) == expected_output

    @staticmethod
    @pytest.mark.parametrize("input", ["not a year"])
    def test_raises_syntax_error_for_invalid_years(input):
        with pytest.raises(SyntaxError):
            add_copyright._parse_years(input)


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_update_copyright_string"])
class TestUpdateCopyrightString:
    @staticmethod
    def test_single_stored_year_single_new_year():
        assert (
            add_copyright._update_copyright_string(
                Mock(end_year=1111, start_year=1111, string="<string sentinel 1111>"),
                2222,
                2222,
            )
            == "<string sentinel 2222>"
        )

    @staticmethod
    @pytest.mark.parametrize(
        "start_year, end_year, expected_output_string",
        [
            (1111, 2222, "<string sentinel 1111 - 2222>"),
            (1234, 5678, "<string sentinel 1234 - 5678>"),
        ],
    )
    def test_single_stored_year_new_range(start_year, end_year, expected_output_string):
        assert (
            add_copyright._update_copyright_string(
                Mock(end_year=1111, start_year=1111, string="<string sentinel 1111>"),
                start_year,
                end_year,
            )
            == expected_output_string
        )

    @staticmethod
    @pytest.mark.parametrize(
        "input_string, expected_output_string",
        [
            ("<string sentinel 1111-1112>", "<string sentinel 2222>"),
            ("<string sentinel 1111 - 1112>", "<string sentinel 2222>"),
        ],
    )
    def test_stored_range_single_new_year(input_string, expected_output_string):
        assert (
            add_copyright._update_copyright_string(
                Mock(end_year=1112, start_year=1111, string=input_string), 2222, 2222
            )
            == expected_output_string
        )

    @staticmethod
    @pytest.mark.parametrize(
        "start_year, end_year, expected_output_string",
        [
            (1111, 2222, "<string sentinel 1111 - 2222>"),
            (1234, 5678, "<string sentinel 1234 - 5678>"),
            (1111, 1234, "<string sentinel 1111 - 1234>"),
            (1234, 2222, "<string sentinel 1234 - 2222>"),
        ],
    )
    def test_stored_range_new_range(start_year, end_year, expected_output_string):
        assert (
            add_copyright._update_copyright_string(
                Mock(
                    start_year=1111,
                    end_year=2222,
                    string="<string sentinel 1111 - 2222>",
                ),
                start_year,
                end_year,
            )
            == expected_output_string
        )


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
    @pytest.mark.parametrize(
        "start_year, end_year, expected_year_string",
        [
            (1991, 2002, "1991 - 2002"),
            (2222, 2222, "2222"),
        ],
    )
    @pytest.mark.parametrize(
        "format",
        ["# Copyright (c) {year} {name}", "{name} owns this as of {year}, hands off!"],
    )
    def test_correct_construction_with_custom_format(
        name,
        format,
        start_year,
        end_year,
        expected_year_string,
        mock_parse_copyright_string,
    ):
        # GIVEN
        # WHEN
        assert add_copyright._construct_copyright_string(
            name, start_year, end_year, format
        ) == format.format(year=expected_year_string, name=name)

        # THEN
        mock_parse_copyright_string.assert_not_called(), (
            "Tried to check a custom formatted string against the default format."
        )

    @staticmethod
    def test_default_format(mock_default_format, mock_parse_copyright_string):
        # GIVEN
        mock_default_format.format = Mock(return_value="<formatted string sentinel>")

        # WHEN
        assert (
            add_copyright._construct_copyright_string(
                "<name_sentinel>",
                "<start_year_sentinel>",
                "<end_year_sentinel>",
                mock_default_format,
            )
            == "<formatted string sentinel>"
        )

        # THEN
        mock_parse_copyright_string.assert_called_once()


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_insert_copyright_string"])
class TestInsertCopyrightString:
    @staticmethod
    @pytest.mark.parametrize(
        "content, expected",
        [
            (
                '"""docstring"""\ndef some_code():\n    pass',
                '<copyright sentinel>\n\n"""docstring"""\ndef some_code():\n    pass',
            ),
            ("", "<copyright sentinel>\n"),
        ],
    )
    def test_inserts_string(content, expected, mock_has_shebang):
        # GIVEN
        mock_has_shebang.return_value = False

        # WHEN
        out = add_copyright._insert_copyright_string("<copyright sentinel>", content)

        # THEN
        assert out == expected, f"Out:\n{out}\nexpected:\n{expected}"

    @staticmethod
    def test_inserts_copyright_after_shebang(mock_has_shebang):
        # GIVEN
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

        # WHEN
        out = add_copyright._insert_copyright_string("<copyright sentinel>", content)

        # THEN
        assert out == expected


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_copyright_is_current"])
class TestCopyrightIsCurrent:
    @staticmethod
    @pytest.mark.parametrize(
        "parsed_copyright, start_year, end_year",
        [
            (Mock(start_year=1991, end_year=1992), 1991, 1992),
            (Mock(start_year=1991, end_year=1991), 1991, 1991),
        ],
    )
    def test_returns_true_if_parsed_copyright_matches_specified_range(
        parsed_copyright, start_year, end_year
    ):
        assert add_copyright._copyright_is_current(
            parsed_copyright, start_year, end_year
        )

    @staticmethod
    @pytest.mark.parametrize(
        "parsed_copyright, start_year, end_year",
        [
            (Mock(start_year=1978, end_year=2028), 1991, 1992),
        ],
    )
    def test_returns_true_if_parsed_copyright_exceeds_commits_range(
        parsed_copyright, start_year, end_year
    ):
        assert add_copyright._copyright_is_current(
            parsed_copyright, start_year, end_year
        )

    @staticmethod
    @pytest.mark.parametrize(
        "parsed_copyright, start_year, end_year",
        [
            (Mock(start_year=1991, end_year=1992), 1990, 1993),
        ],
    )
    def test_returns_false_if_parsed_copyright_less_than_commits_range(
        parsed_copyright, start_year, end_year
    ):
        assert not add_copyright._copyright_is_current(
            parsed_copyright, start_year, end_year
        )


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_get_earliest_commit_year"])
class TestGetEarliestCommitYear:
    @staticmethod
    def test_single_commit(mocker):
        # GIVEN
        commit_year = 1776
        mock_repo = create_autospec(git.Repo)

        mock_repo.blame.return_value = [
            [
                Mock(
                    committed_date=datetime.timestamp(
                        datetime(commit_year, 1, 1, 1, 1, 1, 1)
                    )
                )
            ]
        ]

        mocker.patch(
            "src.add_copyright_hook.add_copyright.Repo", return_value=mock_repo
        )

        # WHEN
        year = add_copyright._get_earliest_commit_year("<file sentinel>")

        # THEN
        assert year == commit_year

    @staticmethod
    def test_multiple_commits(mocker):
        # GIVEN
        commit_years = [1776, 1984, 2012]
        mock_repo = create_autospec(git.Repo)

        mock_repo.blame.return_value = [
            [
                Mock(
                    committed_date=datetime.timestamp(
                        datetime(commit_year, 1, 1, 1, 1, 1, 1)
                    )
                )
            ]
            for commit_year in commit_years
        ]

        mocker.patch(
            "src.add_copyright_hook.add_copyright.Repo", return_value=mock_repo
        )

        # WHEN
        year = add_copyright._get_earliest_commit_year("blah")

        # THEN
        assert year == min(commit_years)


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_ensure_copyright_string"])
class TestEnsureCopyrightString:
    @staticmethod
    def test_returns_0_if_file_has_current_copyright(
        tmp_path,
        mock_parse_copyright_string,
        mock_copyright_is_current,
        mock_get_earliest_commit_year,
        mock_get_current_year,
    ):
        # GIVEN
        start_year = 1111
        end_year = 1234
        p = tmp_path / "stub_file.py"
        p.write_text("<file_contents sentinel>")
        mock_get_earliest_commit_year.return_value = start_year
        mock_get_current_year.return_value = end_year
        mock_copyright_is_current.return_value = True
        mock_parse_copyright_string.return_value = Mock(
            start_year=start_year, end_year=end_year
        )

        # WHEN
        assert add_copyright._ensure_copyright_string(p, "<name sentinel>", None) == 0

        # THEN
        mock_get_earliest_commit_year.assert_called_once_with(p)
        mock_copyright_is_current.assert_called_once_with(
            mock_parse_copyright_string.return_value, start_year, end_year
        )
        mock_parse_copyright_string.assert_called_once_with("<file_contents sentinel>")
        with open(p) as f:
            assert f.read() == "<file_contents sentinel>"

    @staticmethod
    def test_returns_1_if_copyright_is_updated(
        tmp_path,
        mock_get_earliest_commit_year,
        mock_get_current_year,
        mock_parse_copyright_string,
        mock_copyright_is_current,
        mock_update_copyright_string,
        capsys,
    ):
        # GIVEN
        start_year = 1111
        end_year = start_year
        p = tmp_path / "stub_file.py"
        p.write_text("<original copyright string sentinel>")

        mock_get_earliest_commit_year.return_value = start_year
        mock_get_current_year.return_value = end_year
        mock_copyright_is_current.return_value = False
        mock_parse_copyright_string.return_value = Mock(
            start_year=start_year,
            end_year=end_year,
            string="<original copyright string sentinel>",
        )
        mock_update_copyright_string.return_value = (
            "<updated copyright string sentinel>"
        )

        # WHEN
        assert add_copyright._ensure_copyright_string(p, "<name sentinel>", None) == 1

        # THEN
        mock_get_earliest_commit_year.assert_called_once_with(p)
        mock_get_current_year.assert_called_once_with()
        mock_copyright_is_current.assert_called_once_with(
            mock_parse_copyright_string.return_value, start_year, end_year
        )
        mock_parse_copyright_string.assert_called_once_with(
            "<original copyright string sentinel>"
        )
        assert capsys.readouterr().out == (
            f"Fixing file `{p}` - updating existing copyright string:\n "
            "`<original copyright string sentinel>` --> "
            "`<updated copyright string sentinel>`\n\n"
        )
        with open(p) as f:
            assert f.read() == "<updated copyright string sentinel>"

    @staticmethod
    def test_returns_1_if_copyright_is_added(
        tmp_path,
        mocker,
        mock_get_earliest_commit_year,
        mock_get_current_year,
        mock_parse_copyright_string,
        mock_copyright_is_current,
        mock_construct_copyright_string,
        mock_insert_copyright_string,
        capsys,
    ):
        # GIVEN
        start_year = 1111
        end_year = start_year
        p = tmp_path / "stub_file.py"
        p.write_text("<file contents sentinel>")

        mock_get_earliest_commit_year.return_value = start_year
        mock_get_current_year.return_value = end_year
        mock_parse_copyright_string.return_value = None
        mock_copyright_is_current.return_value = False
        mock_construct_copyright_string.return_value = "<copyright string sentinel>"
        mock_insert_copyright_string.return_value = "<new file contents sentinel>"

        # WHEN
        assert add_copyright._ensure_copyright_string(p, "<name sentinel>", None) == 1

        # THEN
        assert capsys.readouterr().out == (
            f"Fixing file `{p}` - added line(s):\n<copyright string sentinel>\n\n"
        )
        mock_parse_copyright_string.assert_called_once_with("<file contents sentinel>")
        mock_construct_copyright_string.assert_called_once_with(
            "<name sentinel>", start_year, end_year, None
        )
        mock_insert_copyright_string.assert_called_once_with(
            "<copyright string sentinel>", "<file contents sentinel>"
        )
        with open(p) as f:
            assert f.read() == "<new file contents sentinel>"


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_get_current_year"])
class TestGetCurrentYear:
    @staticmethod
    @freeze_time("2012-01-01")
    def test_returns_year_int():
        # GIVEN
        # WHEN
        year = add_copyright._get_current_year()

        # THEN
        assert isinstance(year, int)
        assert year == 2012


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_get_git_user_name"])
class TestGetGitUserName:
    @staticmethod
    def test_returns_configured_name(git_repo, cwd):
        # GIVEN
        username = "<username sentinel>"
        git_repo.run(f"git config user.name '{username}'")

        # WHEN
        with cwd(git_repo.workspace):
            name = add_copyright._get_git_user_name()

        # THEN
        assert name == username

    @staticmethod
    def test_raises_exception_when_git_userneam_is_not_configured(mocker):
        # GIVEN
        mocked_repo = create_autospec(git.Repo)
        mocker.patch("src.add_copyright_hook.add_copyright.Repo", mocked_repo)

        # WHEN
        with pytest.raises(ValueError) as e:
            _ = add_copyright._get_git_user_name()

        # THEN
        assert e.exconly() == "ValueError: The git username is not configured."


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_resolve_user_name"])
class TestResolveUserName:
    @staticmethod
    @pytest.mark.parametrize("config", [None, "stub config"])
    def test_returns_name_if_provided(
        config, mock_read_config_file, mock_get_git_user_name
    ):
        # GIVEN
        # WHEN
        name = add_copyright._resolve_user_name("<name sentinel>", config)

        # THEN
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
        # GIVEN
        mock_read_config_file.return_value = {"format": "<format sentinel>"}
        mock_ensure_valid_format.return_value = "<checked format sentinel>"

        # WHEN
        assert (
            add_copyright._resolve_format(None, "<config file sentinel>")
            == "<checked format sentinel>"
        )

        # THEN
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
        # GIVEN
        # WHEN
        # THEN
        assert add_copyright._ensure_valid_format(input_format) == input_format

    @staticmethod
    @pytest.mark.parametrize("input_format", ["Nope"])
    def test_raises_keyerror_for_invalid_format_strings(input_format):
        # GIVEN
        # WHEN
        # THEN
        with pytest.raises(KeyError):
            assert add_copyright._ensure_valid_format(input_format) == input_format


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_read_config_file"])
class TestReadConfigFile:
    @staticmethod
    def test_raises_exception_if_file_does_not_exist(tmp_path, cwd):
        # GIVEN
        # WHEN
        # THEN
        with cwd(tmp_path):
            with pytest.raises(FileNotFoundError):
                add_copyright._read_config_file("not_a_real_file.blah")

    @staticmethod
    @pytest.mark.parametrize("invalid_file_name", ["foo.txt", "var.cfg"])
    def test_raises_exception_if_not_supported_type(invalid_file_name, tmp_path, cwd):
        # GIVEN
        p = tmp_path / invalid_file_name
        p.write_text("")

        # WHEN
        # THEN
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
        # GIVEN
        p = tmp_path / filename
        p.write_text(file_contents)

        # WHEN
        data = add_copyright._read_config_file(p)

        # THEN
        assert data == {"name": "<name sentinel>", "year": "<year sentinel>"}


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_parse_add_copyright_args"])
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
        format_arg,
        expected_format,
        mock_resolve_user_name,
        mock_resolve_format,
        mock_resolve_files,
        mock_default_config_file,
        mocker,
    ):
        # GIVEN
        mock_resolve_user_name.return_value = "<name sentinel>"
        mock_resolve_format.return_value = "<format sentinel>"
        mock_resolve_files.return_value = "<file sentinel>"
        mock_isfile = mocker.patch("os.path.isfile", return_value=False)
        mocker.patch("sys.argv", ["stub", *file_arg, *name_arg, *format_arg])

        # WHEN
        args = add_copyright._parse_args()

        # THEN
        mock_resolve_user_name.assert_called_once_with(expected_name, None)
        mock_resolve_format.assert_called_once_with(expected_format, None)
        mock_resolve_files.assert_called_once_with(file_arg)
        mock_isfile.assert_called_once_with(mock_default_config_file)
        assert args.name == "<name sentinel>"
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
        mock_resolve_format,
        mock_resolve_files,
    ):
        # GIVEN
        mock_resolve_user_name.return_value = "<name sentinel>"
        mock_resolve_format.return_value = "<format sentinel>"
        mock_resolve_files.return_value = "<file sentinel>"
        mocker.patch("os.path.isfile", return_value=False)
        mocker.patch("sys.argv", ["stub", *file_arg, *config_arg])

        # WHEN
        args = add_copyright._parse_args()

        # THEN
        mock_resolve_user_name.assert_called_once_with(None, expected_config)
        mock_resolve_format.assert_called_once_with(None, expected_config)
        mock_resolve_files.assert_called_once_with(file_arg)
        assert args.name == "<name sentinel>"
        assert args.format == "<format sentinel>"
        assert args.files == "<file sentinel>"

    @staticmethod
    @pytest.mark.parametrize(
        "clashing_option",
        [
            ["-n", "stub_name"],
            ["-f", "stub_format"],
        ],
    )
    def test_raises_sysexit_if_clashing_options(clashing_option, mocker, capsys):
        # GIVEN
        sentinel = "-c and -n|-f are mutually exclusive."
        mocker.patch("sys.argv", ["stub", *clashing_option, "-c", "stub_config"])

        # WHEN
        with pytest.raises(SystemExit):
            add_copyright._parse_args()

        # THEN
        assert sentinel in capsys.readouterr().out

    @staticmethod
    def test_detects_existing_config_file(
        mocker,
        mock_resolve_user_name,
        mock_resolve_format,
        mock_resolve_files,
        mock_default_config_file,
    ):
        # GIVEN
        mock_resolve_user_name.return_value = "<name sentinel>"
        mock_resolve_format.return_value = "<format sentinel>"
        mock_resolve_files.return_value = "<file sentinel>"
        mocker.patch("os.path.isfile", return_value=True)
        mocker.patch("sys.argv", ["stub", []])

        # WHEN
        args = add_copyright._parse_args()

        # THEN
        mock_resolve_user_name.assert_called_once_with(None, mock_default_config_file)
        mock_resolve_format.assert_called_once_with(None, mock_default_config_file)
        mock_resolve_files.assert_called_once_with([[]])
        assert args.name == "<name sentinel>"
        assert args.format == "<format sentinel>"
        assert args.files == "<file sentinel>"
        assert args.config == mock_default_config_file


@pytest.mark.usefixtures(*FIXTURES)
class TestMain:
    @staticmethod
    def test_early_return_for_no_files(
        mock_parse_add_copyright_args, mock_ensure_copyright_string
    ):
        # GIVEN
        mock_parse_add_copyright_args.return_value = Mock(files=[])

        # WHEN
        assert add_copyright.main() == 0

        # THEN
        mock_ensure_copyright_string.assert_not_called()

    @staticmethod
    def test_returns_1_for_changed_files(
        mock_parse_add_copyright_args, mock_ensure_copyright_string
    ):
        # GIVEN
        mock_parse_add_copyright_args.return_value = argparse.Namespace(
            files=["<file sentinel 1>", "<filesentinel 2>"],
            format="<format sentinel>",
            name="<name sentinel>",
        )
        mock_ensure_copyright_string.return_value = 1

        # WHEN
        assert add_copyright.main() == 1

        # THEN
        mock_ensure_copyright_string.assert_has_calls(
            [
                call(
                    "<file sentinel 1>",
                    "<name sentinel>",
                    "<format sentinel>",
                ),
                call(
                    "<filesentinel 2>",
                    "<name sentinel>",
                    "<format sentinel>",
                ),
            ]
        )
