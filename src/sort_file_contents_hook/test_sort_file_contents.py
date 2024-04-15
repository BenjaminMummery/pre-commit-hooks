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
