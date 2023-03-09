# Copyright (c) 2023 Benjamin Mummery

import pytest

from sort_file_contents_hook import sort_file_contents


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


class TestSeparateLeadingComment:
    @staticmethod
    def test_single_line_comment():
        lines = [
            "# <comment sentinel>",
            "<sortable sentinel 1>",
            "<sortable sentinel 2>",
        ]

        comment, section = sort_file_contents._separate_leading_comment(lines)

        assert comment == ["# <comment sentinel>"]
        assert section == ["<sortable sentinel 1>", "<sortable sentinel 2>"]

    @staticmethod
    def test_multiple_line_comment():
        lines = [
            "# <comment sentinel 1>",
            "# <comment sentinel 2>",
            "<sortable sentinel 1>",
            "<sortable sentinel 2>",
        ]

        comment, section = sort_file_contents._separate_leading_comment(lines)

        assert comment == ["# <comment sentinel 1>", "# <comment sentinel 2>"]
        assert section == ["<sortable sentinel 1>", "<sortable sentinel 2>"]

    @staticmethod
    def test_nested_comment():
        lines = [
            "# <comment sentinel 1>",
            "<sortable sentinel 1>",
            "# <comment sentinel 2>",
            "<sortable sentinel 2>",
        ]

        comment, section = sort_file_contents._separate_leading_comment(lines)

        assert comment == ["# <comment sentinel 1>"]
        assert section == [
            "<sortable sentinel 1>",
            "# <comment sentinel 2>",
            "<sortable sentinel 2>",
        ]

    @staticmethod
    def test_no_comment():
        lines = [
            "<sortable sentinel 1>",
            "<sortable sentinel 2>",
        ]

        comment, section = sort_file_contents._separate_leading_comment(lines)

        assert comment is None
        assert section == ["<sortable sentinel 1>", "<sortable sentinel 2>"]

    @staticmethod
    def test_no_sortable_lines():
        lines = [
            "# <comment sentinel 1>",
            "# <comment sentinel 2>",
        ]

        comment, section = sort_file_contents._separate_leading_comment(lines)

        assert comment == ["# <comment sentinel 1>", "# <comment sentinel 2>"]
        assert section is None


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


class TestSortContents:
    @staticmethod
    @pytest.mark.parametrize(
        "file_contents, expected_call",
        [
            ("A\nC\nB", ["A\n", "C\n", "B"]),
            ("A\n\nC\n", ["A\n", "\n", "C\n"]),
        ],
    )
    def test_file_read(file_contents, expected_call, tmp_path, mocker):
        f = tmp_path / "blah.txt"
        f.write_text(file_contents)
        mock_parse_sections = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._identify_sections"
        )

        sort_file_contents._sort_contents(f)

        mock_parse_sections.assert_called_once_with(expected_call)


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
    def test_argument_passing(mocker, file_arg, unique_arg, expected_unique):
        mock_file_resolver = mocker.patch(
            "_shared.resolvers._resolve_files",
            return_value="<file sentinel>",
        )
        mocker.patch("sys.argv", ["stub", *file_arg, *unique_arg])

        args = sort_file_contents._parse_args()

        mock_file_resolver.assert_called_once_with(file_arg)
        assert args.files == "<file sentinel>"
        assert args.unique == expected_unique
