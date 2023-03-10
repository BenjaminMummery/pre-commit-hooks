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

    @staticmethod
    def test_unique():
        lines = ["A", "B", "C", "A"]

        assert sort_file_contents._sort_lines(lines) == ["A", "A", "B", "C"]
        assert sort_file_contents._sort_lines(lines, unique=True) == ["A", "B", "C"]

    @staticmethod
    def test_sorts_comments_like_they_are_not_comments():
        lines = ["A", "C", "# B", "# D", "E"]

        assert sort_file_contents._sort_lines(lines) == ["A", "# B", "C", "# D", "E"]


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


class TestSortContents:
    @staticmethod
    def test_argument_passing(tmp_path, mocker):
        f = tmp_path / "blah.txt"
        f.write_text("<file contents sentinel 1>\n<file contents sentinel 2>")
        mock_identify_sections = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._identify_sections",
            return_value=[["<section sentinel"]],
        )
        mock_separate_comment = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._separate_leading_comment",
            return_value=(["<header_sentinel>"], ["<contents_sentinel>"]),
        )
        mock_sort_lines = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._sort_lines",
            return_value=["<sorted lines sentinel>"],
        )

        assert sort_file_contents._sort_contents(f) == 1

        mock_identify_sections.assert_called_once_with(
            ["<file contents sentinel 1>", "<file contents sentinel 2>"]
        )
        mock_separate_comment.assert_called_once_with(["<section sentinel"])
        mock_sort_lines.assert_called_once_with(["<contents_sentinel>"], unique=False)
        with open(f, "r") as file:
            assert list(file) == ["<header_sentinel>\n", "<sorted lines sentinel>\n"]

    @staticmethod
    def test_with_nothing_to_sort(tmp_path, mocker):
        f = tmp_path / "blah.txt"
        f.write_text("<file contents sentinel>")
        mock_identify_sections = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._identify_sections",
            return_value=[["<section sentinel"]],
        )
        mock_separate_comment = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._separate_leading_comment",
            return_value=(["<header_sentinel>"], None),
        )
        mock_sort_lines = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._sort_lines",
        )

        assert sort_file_contents._sort_contents(f) == 0

        mock_identify_sections.assert_called_once_with(["<file contents sentinel>"])
        mock_separate_comment.assert_called_once_with(["<section sentinel"])
        mock_sort_lines.assert_not_called()
        with open(f, "r") as file:
            assert file.read() == "<file contents sentinel>"

    @staticmethod
    def test_early_exit_for_already_sorted_sections(tmp_path, mocker):
        f = tmp_path / "blah.txt"
        f.write_text("<file contents sentinel>")
        mock_identify_sections = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._identify_sections",
            return_value=[["<section sentinel"]],
        )
        mock_separate_comment = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._separate_leading_comment",
            return_value=(["<header_sentinel>"], ["<contents_sentinel>"]),
        )
        mock_sort_lines = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._sort_lines",
            return_value=["<contents_sentinel>"],
        )

        assert sort_file_contents._sort_contents(f) == 0

        mock_identify_sections.assert_called_once_with(["<file contents sentinel>"])
        mock_separate_comment.assert_called_once_with(["<section sentinel"])
        mock_sort_lines.assert_called_once_with(["<contents_sentinel>"], unique=False)
        with open(f, "r") as file:
            assert file.read() == "<file contents sentinel>"

    @staticmethod
    def test_with_unique(tmp_path, mocker, capsys):
        f = tmp_path / "blah.txt"
        f.write_text("<file contents sentinel>")
        mock_identify_sections = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._identify_sections",
            return_value=[["<section sentinel"]],
        )
        mock_separate_comment = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._separate_leading_comment",
            return_value=(["<header_sentinel>"], ["<contents_sentinel>"]),
        )
        mock_sort_lines = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._sort_lines",
            return_value=["<sorted lines sentinel>"],
        )
        mock_find_duplicates = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._find_duplicates",
            return_value=[("<duplicate sentinel", 0)],
        )

        assert sort_file_contents._sort_contents(f, unique=True) == 1

        mock_identify_sections.assert_called_once_with(["<file contents sentinel>"])
        mock_separate_comment.assert_called_once_with(["<section sentinel"])
        mock_sort_lines.assert_called_once_with(["<contents_sentinel>"], unique=True)
        mock_find_duplicates.assert_called_once_with(["<sorted lines sentinel>"])
        assert capsys.readouterr().out == (
            f"Could not sort '{f}'. "
            "The following entries appear in multiple sections:\n"
            "- '<duplicate sentinel' appears in 0 sections.\n"
        )
        with open(f, "r") as file:
            assert file.read() == "<file contents sentinel>"


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


class TestMain:
    @staticmethod
    def test_argument_passing_no_files(mocker):
        mocker.patch(
            "sort_file_contents_hook.sort_file_contents._parse_args",
            return_value=mocker.Mock(files=[], unique=False),
        )
        mock_sort_contents = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._sort_contents"
        )

        assert sort_file_contents.main() == 0
        mock_sort_contents.assert_not_called()

    @staticmethod
    def test_argument_passing(mocker):
        mocker.patch(
            "sort_file_contents_hook.sort_file_contents._parse_args",
            return_value=mocker.Mock(files=["<file sentinel>"], unique=False),
        )
        mock_sort_contents = mocker.patch(
            "sort_file_contents_hook.sort_file_contents._sort_contents", return_value=0
        )

        assert sort_file_contents.main() == 0
        mock_sort_contents.assert_called_once_with("<file sentinel>", unique=False)
