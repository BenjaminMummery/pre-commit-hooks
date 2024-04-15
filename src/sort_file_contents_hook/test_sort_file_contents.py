# Copyright (c) 2024 Benjamin Mummery

from typing import List
from unittest.mock import Mock, mock_open

import pytest
from pytest_mock import MockerFixture

from . import sort_file_contents
from .sort_file_contents import UnsortableError


class TestSortLines:
    class TestAlreadySorted:
        @staticmethod
        @pytest.mark.parametrize("input", [["A", "B"]])
        def test_simple_list(input: List[str]):
            # WHEN
            ret = sort_file_contents._sort_lines(input)

            # THEN
            assert ret == input

        @staticmethod
        @pytest.mark.parametrize("input", [["A", "B", "B"]])
        def test_leaves_duplicates_when_unique_is_false(input: List[str]):
            # WHEN
            ret = sort_file_contents._sort_lines(input)

            # THEN
            assert ret == input

        @staticmethod
        @pytest.mark.parametrize("input", [["A", "# B", "C"]])
        def test_sorts_comments(input: List[str]):
            # WHEN
            ret = sort_file_contents._sort_lines(input)

            # THEN
            assert ret == input

    class TestUnsorted:
        @staticmethod
        @pytest.mark.parametrize("input, expected", [(["B", "A"], ["A", "B"])])
        def test_already_sorted(input: List[str], expected: List[str]):
            # WHEN
            ret = sort_file_contents._sort_lines(input)

            # THEN
            assert ret == expected

        @staticmethod
        @pytest.mark.parametrize(
            "input, expected",
            [
                (
                    [
                        "B",
                        "A",
                        "B",
                    ],
                    ["A", "B", "B"],
                )
            ],
        )
        def test_leaves_duplicates_when_unique_is_false(
            input: List[str], expected: List[str]
        ):
            # WHEN
            ret = sort_file_contents._sort_lines(input)

            # THEN
            assert ret == expected

        @staticmethod
        @pytest.mark.parametrize(
            "input, expected",
            [
                (
                    [
                        "B",
                        "A",
                        "B",
                    ],
                    ["A", "B"],
                )
            ],
        )
        def test_removes_duplicates_when_unique_is_true(
            input: List[str], expected: List[str]
        ):
            # WHEN
            ret = sort_file_contents._sort_lines(input, unique=True)

            # THEN
            assert ret == expected

        @staticmethod
        @pytest.mark.parametrize(
            "input, expected", [(["# B", "A", "C"], ["A", "# B", "C"])]
        )
        def test_sorts_comments(input: List[str], expected: List[str]):
            # WHEN
            ret = sort_file_contents._sort_lines(input)

            # THEN
            assert ret == expected


class TestSeparateLeadingComment:
    @staticmethod
    def test_no_leading_comment():
        # GIVEN
        input = ["A", "B", "C"]

        # WHEN
        ret = sort_file_contents._separate_leading_comment(input)

        # THEN
        assert ret == (None, input)

    @staticmethod
    def test_separates_leading_comment():
        # GIVEN
        input = ["# A", "B", "C"]

        # WHEN
        ret = sort_file_contents._separate_leading_comment(input)

        # THEN
        assert ret == (["# A"], ["B", "C"])

    @staticmethod
    def test_separates_multiple_leading_comments():
        # GIVEN
        input = ["# A", "# B", "C"]

        # WHEN
        ret = sort_file_contents._separate_leading_comment(input)

        # THEN
        assert ret == (["# A", "# B"], ["C"])

    @staticmethod
    def test_leaves_interstitial_comments():
        # GIVEN
        input = ["A", "# B", "C"]

        # WHEN
        ret = sort_file_contents._separate_leading_comment(input)

        # THEN
        assert ret == (None, input)


class TestIdentifySection:
    @staticmethod
    @pytest.mark.parametrize("input", [[], [""], ["\n"]])
    def test_early_return_for_no_input(input: List[str]):
        # WHEN
        ret = sort_file_contents._identify_sections(input)

        # THEN
        assert ret == [[]]

    @staticmethod
    def test_early_return_for_single_line():
        # GIVEN
        input = ["<sentinel>"]

        # WHEN
        ret = sort_file_contents._identify_sections(input)

        # THEN
        assert ret == [input]

    @staticmethod
    def test_identifies_single_section():
        # GIVEN
        input = ["<line 1 sentinel>", "<line 2 sentinel>"]

        # WHEN
        ret = sort_file_contents._identify_sections(input)

        # THEN
        assert ret == [input]

    @staticmethod
    def test_identifies_multiple_section():
        # GIVEN
        input = ["<line 1 sentinel>", "<line 2 sentinel>", "", "<line 3 sentinel>"]

        # WHEN
        ret = sort_file_contents._identify_sections(input)

        # THEN
        assert ret == [
            ["<line 1 sentinel>", "<line 2 sentinel>"],
            ["<line 3 sentinel>"],
        ]

    @staticmethod
    def test_handles_multiple_linebreaks():
        # GIVEN
        input = ["<line 1 sentinel>", "<line 2 sentinel>", "", "", "<line 3 sentinel>"]

        # WHEN
        ret = sort_file_contents._identify_sections(input)

        # THEN
        assert ret == [
            ["<line 1 sentinel>", "<line 2 sentinel>"],
            ["<line 3 sentinel>"],
        ]


class TestFindDuplicates:
    @staticmethod
    def test_no_lines():
        # GIVEN
        input: List[str] = []

        # WHEN
        ret = sort_file_contents._find_duplicates(input)

        # THEN
        assert ret == []

    @staticmethod
    def test_no_duplicates():
        # GIVEN
        input = ["A", "B", "C"]

        # WHEN
        ret = sort_file_contents._find_duplicates(input)

        # THEN
        assert ret == []

    @staticmethod
    def test_finds_single_case_of_duplicates():
        # GIVEN
        input = ["A", "B", "B", "C"]

        # WHEN
        ret = sort_file_contents._find_duplicates(input)

        # THEN
        assert ret == [("B", 2)]

    @staticmethod
    def test_finds_multiple_duplicates():
        # GIVEN
        input = ["A", "B", "B", "C", "A", "A"]

        # WHEN
        ret = sort_file_contents._find_duplicates(input)

        # THEN
        assert ret == [("A", 3), ("B", 2)]


class TestFindCommentClashes:
    @staticmethod
    @pytest.mark.parametrize("input", [[], ["A", "B", "C"]])
    def test_no_comments(input: List[str], mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{sort_file_contents.__name__}._find_duplicates",
            mocked_find_dupl := Mock(return_value=[]),
        )

        # WHEN
        _ = sort_file_contents._find_comment_clashes(input)

        # THEN
        mocked_find_dupl.assert_called_once_with(input)

    @staticmethod
    def test_comments(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{sort_file_contents.__name__}._find_duplicates",
            mocked_find_dupl := Mock(return_value=[]),
        )
        input = ["A", "# B", "C"]

        # WHEN
        _ = sort_file_contents._find_comment_clashes(input)

        # THEN
        mocked_find_dupl.assert_called_once_with(["A", "B", "C"])

    @staticmethod
    def test_extracts_return_info(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{sort_file_contents.__name__}._find_duplicates",
            Mock(return_value=[("<sentinel 1>", Mock()), ("<sentinel 2>", Mock())]),
        )
        input: List[str] = []

        # WHEN
        ret = sort_file_contents._find_comment_clashes(input)

        # THEN
        assert ret == ["<sentinel 1>", "<sentinel 2>"]


class TestSortContents:
    @staticmethod
    def test_already_sorted(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            "builtins.open",
            mock_open(read_data="<line A sentinel>\n<line B sentinel>"),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._identify_sections",
            mocked_identify_section := Mock(return_value=["<section sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._separate_leading_comment",
            mocked_separate_leading_comment := Mock(
                return_value=(
                    ["<section header sentinel>"],
                    ["<section body sentinel>"],
                )
            ),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._sort_lines",
            mocked_sort_lines := Mock(return_value=["<section body sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_duplicates",
            mocked_find_duplicates := Mock(),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_comment_clashes",
            mocked_find_comment_clashes := Mock(),
        )

        # WHEN
        ret = sort_file_contents._sort_contents(Mock(), unique=False)

        # THEN
        assert ret == 0
        mocked_identify_section.assert_called_once_with(
            ["<line A sentinel>", "<line B sentinel>"]
        )
        mocked_separate_leading_comment.assert_called_once_with("<section sentinel>")
        mocked_sort_lines.assert_called_once_with(
            ["<section body sentinel>"], unique=False
        )
        mocked_find_duplicates.assert_not_called()
        mocked_find_comment_clashes.assert_not_called()

    @staticmethod
    def test_section_with_no_body(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            "builtins.open",
            mock_open(read_data="<line A sentinel>\n<line B sentinel>"),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._identify_sections",
            mocked_identify_section := Mock(return_value=["<section sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._separate_leading_comment",
            mocked_separate_leading_comment := Mock(
                return_value=(["<section header sentinel>"], None)
            ),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._sort_lines",
            mocked_sort_lines := Mock(return_value=["<section body sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_duplicates",
            mocked_find_duplicates := Mock(),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_comment_clashes",
            mocked_find_comment_clashes := Mock(),
        )

        # WHEN
        ret = sort_file_contents._sort_contents(Mock(), unique=False)

        # THEN
        assert ret == 0
        mocked_identify_section.assert_called_once_with(
            ["<line A sentinel>", "<line B sentinel>"]
        )
        mocked_separate_leading_comment.assert_called_once_with("<section sentinel>")
        mocked_sort_lines.assert_not_called()
        mocked_find_duplicates.assert_not_called()
        mocked_find_comment_clashes.assert_not_called()

    @staticmethod
    def test_changed_sections(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            "builtins.open",
            mock_open(read_data="<line A sentinel>\n<line B sentinel>"),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._identify_sections",
            mocked_identify_section := Mock(return_value=["<section sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._separate_leading_comment",
            mocked_separate_leading_comment := Mock(
                return_value=(
                    ["<section header sentinel>"],
                    ["<section body sentinel>"],
                )
            ),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._sort_lines",
            mocked_sort_lines := Mock(return_value=["<altered section body sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_duplicates",
            mocked_find_duplicates := Mock(),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_comment_clashes",
            mocked_find_comment_clashes := Mock(),
        )

        # WHEN
        ret = sort_file_contents._sort_contents(Mock(), unique=False)

        # THEN
        assert ret == 1
        mocked_identify_section.assert_called_once_with(
            ["<line A sentinel>", "<line B sentinel>"]
        )
        mocked_separate_leading_comment.assert_called_once_with("<section sentinel>")
        mocked_sort_lines.assert_called_once_with(
            ["<section body sentinel>"], unique=False
        )
        mocked_find_duplicates.assert_not_called()
        mocked_find_comment_clashes.assert_not_called()

    @staticmethod
    def test_uniqueness_checks(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            "builtins.open",
            mock_open(read_data="<line A sentinel>\n<line B sentinel>"),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._identify_sections",
            mocked_identify_section := Mock(return_value=["<section sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._separate_leading_comment",
            mocked_separate_leading_comment := Mock(
                return_value=(
                    ["<section header sentinel>"],
                    ["<section body sentinel>"],
                )
            ),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._sort_lines",
            mocked_sort_lines := Mock(return_value=["<section body sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_duplicates",
            mocked_find_duplicates := Mock(return_value=[]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_comment_clashes",
            mocked_find_comment_clashes := Mock(return_value=[]),
        )

        # WHEN
        ret = sort_file_contents._sort_contents(Mock(), unique=True)

        # THEN
        assert ret == 0
        mocked_identify_section.assert_called_once_with(
            ["<line A sentinel>", "<line B sentinel>"]
        )
        mocked_separate_leading_comment.assert_called_once_with("<section sentinel>")
        mocked_sort_lines.assert_called_once_with(
            ["<section body sentinel>"], unique=True
        )
        mocked_find_duplicates.assert_called_once_with(["<section body sentinel>"])
        mocked_find_comment_clashes.assert_called_once_with(["<section body sentinel>"])

    @staticmethod
    def test_raises_UnsortableError_for_duplicates_across_sections(
        mocker: MockerFixture,
    ):
        # GIVEN
        mocker.patch(
            "builtins.open",
            mock_open(read_data="<line A sentinel>\n<line B sentinel>"),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._identify_sections",
            mocked_identify_section := Mock(return_value=["<section sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._separate_leading_comment",
            mocked_separate_leading_comment := Mock(
                return_value=(
                    ["<section header sentinel>"],
                    ["<section body sentinel>"],
                )
            ),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._sort_lines",
            mocked_sort_lines := Mock(return_value=["<section body sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_duplicates",
            mocked_find_duplicates := Mock(return_value=[("<duplicate sentinel>", 1)]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_comment_clashes",
            mocked_find_comment_clashes := Mock(return_value=[]),
        )

        # WHEN
        with pytest.raises(UnsortableError):
            _ = sort_file_contents._sort_contents(Mock(), unique=True)

        # THEN
        mocked_identify_section.assert_called_once_with(
            ["<line A sentinel>", "<line B sentinel>"]
        )
        mocked_separate_leading_comment.assert_called_once_with("<section sentinel>")
        mocked_sort_lines.assert_called_once_with(
            ["<section body sentinel>"], unique=True
        )
        mocked_find_duplicates.assert_called_once_with(["<section body sentinel>"])
        mocked_find_comment_clashes.assert_not_called()

    @staticmethod
    def test_raises_UnsortableError_for_comment_clashes_across_sections(
        mocker: MockerFixture,
    ):
        # GIVEN
        mocker.patch(
            "builtins.open",
            mock_open(read_data="<line A sentinel>\n<line B sentinel>"),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._identify_sections",
            mocked_identify_section := Mock(return_value=["<section sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._separate_leading_comment",
            mocked_separate_leading_comment := Mock(
                return_value=(
                    ["<section header sentinel>"],
                    ["<section body sentinel>"],
                )
            ),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._sort_lines",
            mocked_sort_lines := Mock(return_value=["<section body sentinel>"]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_duplicates",
            mocked_find_duplicates := Mock(return_value=[]),
        )
        mocker.patch(
            f"{sort_file_contents.__name__}._find_comment_clashes",
            mocked_find_comment_clashes := Mock(return_value=["<clash sentinel"]),
        )

        # WHEN
        with pytest.raises(UnsortableError):
            _ = sort_file_contents._sort_contents(Mock(), unique=True)

        # THEN
        mocked_identify_section.assert_called_once_with(
            ["<line A sentinel>", "<line B sentinel>"]
        )
        mocked_separate_leading_comment.assert_called_once_with("<section sentinel>")
        mocked_sort_lines.assert_called_once_with(
            ["<section body sentinel>"], unique=True
        )
        mocked_find_duplicates.assert_called_once_with(["<section body sentinel>"])
        mocked_find_comment_clashes.assert_called_once_with(["<section body sentinel>"])
