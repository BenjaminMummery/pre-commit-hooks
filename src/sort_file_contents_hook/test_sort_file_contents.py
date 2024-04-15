# Copyright (c) 2024 Benjamin Mummery

from typing import List

import pytest

from . import sort_file_contents


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
