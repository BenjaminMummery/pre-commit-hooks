# Copyright (c) 2023 Benjamin Mummery

from unittest.mock import Mock

import pytest

from src.sort_file_contents_hook import sort_file_contents

from ..conftest import ADD_MSG_ISSUE_FIXTURE_LIST as FIXTURES


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_sort_lines"])
class TestSortLines:
    @staticmethod
    def test_single_line():
        lines = ["A"]

        assert sort_file_contents._sort_lines(lines) == lines

    @staticmethod
    def test_already_sorted():
        lines = ["A", "B"]

        assert sort_file_contents._sort_lines(lines) == lines

    @staticmethod
    def test_sorting():
        lines = ["B", "A"]

        assert sort_file_contents._sort_lines(lines) == sorted(lines)

    @staticmethod
    def test_unique():
        lines = ["A", "B", "C", "A"]

        assert sort_file_contents._sort_lines(lines) == ["A", "A", "B", "C"]
        assert sort_file_contents._sort_lines(lines, unique=True) == ["A", "B", "C"]

    @staticmethod
    def test_sorts_comments_like_they_are_not_comments():
        lines = ["A", "C", "# B", "# D", "E"]

        assert sort_file_contents._sort_lines(lines) == ["A", "# B", "C", "# D", "E"]


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_separate_leading_comment"])
class TestSeparateLeadingComment:
    @staticmethod
    def test_single_line_comment():
        # GIVEN
        lines = [
            "# <comment sentinel>",
            "<sortable sentinel 1>",
            "<sortable sentinel 2>",
        ]

        # WHEN
        comment, section = sort_file_contents._separate_leading_comment(lines)

        # THEN
        assert comment == ["# <comment sentinel>"]
        assert section == ["<sortable sentinel 1>", "<sortable sentinel 2>"]

    @staticmethod
    def test_multiple_line_comment():
        # GIVEN
        lines = [
            "# <comment sentinel 1>",
            "# <comment sentinel 2>",
            "<sortable sentinel 1>",
            "<sortable sentinel 2>",
        ]

        # WHEN
        comment, section = sort_file_contents._separate_leading_comment(lines)

        # THEN
        assert comment == ["# <comment sentinel 1>", "# <comment sentinel 2>"]
        assert section == ["<sortable sentinel 1>", "<sortable sentinel 2>"]

    @staticmethod
    def test_nested_comment():
        # GIVEN
        lines = [
            "# <comment sentinel 1>",
            "<sortable sentinel 1>",
            "# <comment sentinel 2>",
            "<sortable sentinel 2>",
        ]

        # WHEN
        comment, section = sort_file_contents._separate_leading_comment(lines)

        # THEN
        assert comment == ["# <comment sentinel 1>"]
        assert section == [
            "<sortable sentinel 1>",
            "# <comment sentinel 2>",
            "<sortable sentinel 2>",
        ]

    @staticmethod
    def test_no_comment():
        # GIVEN
        lines = [
            "<sortable sentinel 1>",
            "<sortable sentinel 2>",
        ]

        # WHEN
        comment, section = sort_file_contents._separate_leading_comment(lines)

        # THEN
        assert comment is None
        assert section == ["<sortable sentinel 1>", "<sortable sentinel 2>"]

    @staticmethod
    def test_no_sortable_lines():
        # GIVEN
        lines = [
            "# <comment sentinel 1>",
            "# <comment sentinel 2>",
        ]

        # WHEN
        comment, section = sort_file_contents._separate_leading_comment(lines)

        # THEN
        assert comment == ["# <comment sentinel 1>", "# <comment sentinel 2>"]
        assert section is None


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_identify_sections"])
class TestIdentifySections:
    @staticmethod
    @pytest.mark.parametrize(
        "lines, expected_sections",
        [
            ([], [[]]),
            ([""], [[]]),
            (["\n"], [[]]),
        ],
    )
    def test_parses_empty_file(lines, expected_sections):
        assert sort_file_contents._identify_sections(lines) == expected_sections

    @staticmethod
    @pytest.mark.parametrize(
        "lines, expected_sections",
        [
            (["<file contents sentinel>"], [["<file contents sentinel>"]]),
        ],
    )
    def test_parses_single_line_file(lines, expected_sections):
        assert sort_file_contents._identify_sections(lines) == expected_sections

    @staticmethod
    @pytest.mark.parametrize(
        "lines, expected_sections",
        [
            (["A", "B", "C"], [["A", "B", "C"]]),
            (["A", "B", "C", ""], [["A", "B", "C"]]),
        ],
    )
    def test_parses_single_section(lines, expected_sections):
        assert sort_file_contents._identify_sections(lines) == expected_sections

    @staticmethod
    @pytest.mark.parametrize(
        "lines, expected_sections",
        [
            (["", "A", "B", "C"], [["A", "B", "C"]]),
            (["", "A", "B", "C", ""], [["A", "B", "C"]]),
            (["", "A", "B", "C", "", ""], [["A", "B", "C"]]),
        ],
    )
    def test_removes_extranious_empty_lines(lines, expected_sections):
        assert sort_file_contents._identify_sections(lines) == expected_sections

    @staticmethod
    @pytest.mark.parametrize(
        "lines, expected_sections",
        [
            (
                ["A", "B", "C", "", "D", "E", "", "F"],
                [["A", "B", "C"], ["D", "E"], ["F"]],
            )
        ],
    )
    def test_separates_sections(lines, expected_sections):
        assert sort_file_contents._identify_sections(lines) == expected_sections


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_find_duplicates"])
class TestFindDuplicates:
    @staticmethod
    def test_identifies_duplicates():
        assert sort_file_contents._find_duplicates(["A", "B", "C", "A", "B", "A"]) == [
            ("A", 3),
            ("B", 2),
        ]

    @staticmethod
    def test_returns_empty_list_for_no_duplicates():
        assert sort_file_contents._find_duplicates(["A", "B", "C"]) == []


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_sort_contents"])
class TestSortContents:
    @staticmethod
    def test_argument_passing(
        tmp_path, mock_identify_sections, mock_separate_leading_comment, mock_sort_lines
    ):
        # GIVEN
        f = tmp_path / "blah.txt"
        f.write_text("<file contents sentinel 1>\n<file contents sentinel 2>")
        mock_identify_sections.return_value = [["<section sentinel"]]
        mock_separate_leading_comment.return_value = (
            ["<header_sentinel>"],
            ["<contents_sentinel>"],
        )
        mock_sort_lines.return_value = ["<sorted lines sentinel>"]

        # WHEN
        assert sort_file_contents._sort_contents(f) == 1

        # THEN
        mock_identify_sections.assert_called_once_with(
            ["<file contents sentinel 1>", "<file contents sentinel 2>"]
        )
        mock_separate_leading_comment.assert_called_once_with(["<section sentinel"])
        mock_sort_lines.assert_called_once_with(["<contents_sentinel>"], unique=False)
        with open(f, "r") as file:
            assert list(file) == ["<header_sentinel>\n", "<sorted lines sentinel>\n"]

    @staticmethod
    def test_with_nothing_to_sort(
        tmp_path, mock_identify_sections, mock_separate_leading_comment, mock_sort_lines
    ):
        # GIVEN
        f = tmp_path / "blah.txt"
        f.write_text("<file contents sentinel>")
        mock_identify_sections.return_value = [["<section sentinel"]]
        mock_separate_leading_comment.return_value = (["<header_sentinel>"], None)

        # WHEN
        assert sort_file_contents._sort_contents(f) == 0

        # THEN
        mock_identify_sections.assert_called_once_with(["<file contents sentinel>"])
        mock_separate_leading_comment.assert_called_once_with(["<section sentinel"])
        mock_sort_lines.assert_not_called()
        with open(f, "r") as file:
            assert file.read() == "<file contents sentinel>"

    @staticmethod
    def test_early_exit_for_already_sorted_sections(
        tmp_path, mock_identify_sections, mock_separate_leading_comment, mock_sort_lines
    ):
        # GIVEN
        f = tmp_path / "blah.txt"
        f.write_text("<file contents sentinel>")
        mock_identify_sections.return_value = [["<section sentinel"]]
        mock_separate_leading_comment.return_value = (
            ["<header_sentinel>"],
            ["<contents_sentinel>"],
        )
        mock_sort_lines.return_value = ["<contents_sentinel>"]

        # WHEN
        assert sort_file_contents._sort_contents(f) == 0

        # THEN
        mock_identify_sections.assert_called_once_with(["<file contents sentinel>"])
        mock_separate_leading_comment.assert_called_once_with(["<section sentinel"])
        mock_sort_lines.assert_called_once_with(["<contents_sentinel>"], unique=False)
        with open(f, "r") as file:
            assert file.read() == "<file contents sentinel>"

    @staticmethod
    def test_with_unique(
        tmp_path,
        capsys,
        mock_identify_sections,
        mock_separate_leading_comment,
        mock_sort_lines,
        mock_find_duplicates,
    ):
        # GIVEN
        f = tmp_path / "blah.txt"
        f.write_text("<file contents sentinel>")
        mock_identify_sections.return_value = [["<section sentinel"]]
        mock_separate_leading_comment.return_value = (
            ["<header_sentinel>"],
            ["<contents_sentinel>"],
        )
        mock_sort_lines.return_value = ["<sorted lines sentinel>"]
        mock_find_duplicates.return_value = [("<duplicate sentinel", 0)]

        # WHEN
        assert sort_file_contents._sort_contents(f, unique=True) == 1

        # THEN
        mock_identify_sections.assert_called_once_with(["<file contents sentinel>"])
        mock_separate_leading_comment.assert_called_once_with(["<section sentinel"])
        mock_sort_lines.assert_called_once_with(["<contents_sentinel>"], unique=True)
        mock_find_duplicates.assert_called_once_with(["<sorted lines sentinel>"])
        assert capsys.readouterr().out == (
            f"Could not sort '{f}'. "
            "The following entries appear in multiple sections:\n"
            "- '<duplicate sentinel' appears in 0 sections.\n"
        )
        with open(f, "r") as file:
            assert file.read() == "<file contents sentinel>"


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f != "mock_parse_sort_file_contents_args"]
)
class TestParseArgs:
    @staticmethod
    @pytest.mark.parametrize(
        "file_arg", [[], ["stub_file"], ["stub_file_1", "stub_file_2"]]
    )
    @pytest.mark.parametrize(
        "unique_arg, expected_unique",
        [
            ([], False),
            (["-u"], True),
            (["--unique"], True),
        ],
    )
    def test_argument_passing(
        mocker, file_arg, unique_arg, expected_unique, mock_resolve_files
    ):
        # GIVEN
        mock_resolve_files.return_value = "<file sentinel>"
        mocker.patch("sys.argv", ["stub", *file_arg, *unique_arg])

        # WHEN
        args = sort_file_contents._parse_args()

        # THEN
        mock_resolve_files.assert_called_once_with(file_arg)
        assert args.files == "<file sentinel>"
        assert args.unique == expected_unique


@pytest.mark.usefixtures(*FIXTURES)
class TestMain:
    @staticmethod
    def test_argument_passing_no_files(
        mock_parse_sort_file_contents_args, mock_sort_contents
    ):
        # GIVEN
        mock_parse_sort_file_contents_args.return_value = Mock(files=[], unique=False)

        # WHEN
        assert sort_file_contents.main() == 0

        # THEN
        mock_sort_contents.assert_not_called()

    @staticmethod
    def test_argument_passing(mock_parse_sort_file_contents_args, mock_sort_contents):
        # GIVEN
        mock_parse_sort_file_contents_args.return_value = Mock(
            files=["<file sentinel>"], unique=False
        )
        mock_sort_contents.return_value = 0

        # WHEN
        assert sort_file_contents.main() == 0

        # THEN
        mock_sort_contents.assert_called_once_with("<file sentinel>", unique=False)
