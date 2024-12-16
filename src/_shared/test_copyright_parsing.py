# Copyright (c) 2023 - 2024 Benjamin Mummery

from typing import Optional, Tuple
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from conftest import assert_matching
from src._shared.comment_mapping import COMMENT_MARKERS

from . import copyright_parsing


# region: fixtures mocking all public functions, classes, and methods.
@pytest.fixture()
def mock_ParsedCopyrightString(mocker: MockerFixture):
    return mocker.patch(
        "src._shared.copyright_parsing.ParsedCopyrightString",
        return_value="<mock_ParsedCopyrightString return sentinel>",
    )


@pytest.fixture()
def mock_parse_copyright_comment(mocker: MockerFixture):
    return mocker.patch(
        "src._shared.copyright_parsing.parse_copyright_comment",
        return_value="<mock_parse_copyright_comment return sentinel>",
    )


# endregion


@pytest.mark.usefixtures("mock_parse_copyright_comment")
class TestParsedCopyrightString:
    @staticmethod
    def test_checks_dates():
        with pytest.raises(ValueError) as e:
            _ = copyright_parsing.ParsedCopyrightString(
                Mock(),
                Mock(),
                start_year := 9999,
                end_year := 1111,
                Mock(),
                Mock(),
            )
        assert_matching(
            "Output error message",
            "Expected error message",
            e.exconly(),
            (
                "ValueError: Copyright end year cannot be before the start year. "
                f"Got {end_year} and {start_year} respectively."
            ),
        )


@pytest.mark.usefixtures("mock_ParsedCopyrightString")
class TestParseCopyrightString:
    class TestParsing:
        @staticmethod
        @pytest.mark.parametrize(
            "input_string, comment_markers, expected_args",
            [
                (
                    "# (c) 2023 Benjamin Mummery",
                    ("#", None),
                    ["(c)", 2023, 2023, "Benjamin Mummery"],
                ),
                (
                    "<!--- Copyright NAME as of 1312 -->",
                    ("<!---", "-->"),
                    ["Copyright", 1312, 1312, "NAME as of"],
                ),
                (
                    "# (c) 1312-2023 Benjamin Mummery",
                    ("#", None),
                    ["(c)", 1312, 2023, "Benjamin Mummery"],
                ),
            ],
        )
        def test_correctly_parses_string(
            input_string: str,
            comment_markers: Tuple[str, Optional[str]],
            expected_args: list,
            mock_ParsedCopyrightString: Mock,
        ):
            # WHEN
            ret = copyright_parsing.parse_copyright_comment(
                input_string, comment_markers
            )

            # THEN
            _expected_args = [comment_markers] + expected_args + [input_string]
            mock_ParsedCopyrightString.assert_called_once_with(*_expected_args)
            assert ret == mock_ParsedCopyrightString.return_value

    @pytest.mark.parametrize("comment_markers", COMMENT_MARKERS.values())
    class TestFailureStates:
        @staticmethod
        @pytest.mark.parametrize(
            "input_string", ["Not a copyright string", "", "foo\n\nbar"]
        )
        def test_returns_none_for_no_matches(
            comment_markers: Tuple[str, Optional[str]], input_string: str
        ):
            assert (
                copyright_parsing.parse_copyright_comment(input_string, comment_markers)
                is None
            )

        @staticmethod
        def test_raises_exception_for_multiple_copyright_strings(comment_markers):
            # GIVEN
            valid_copyright_comment = (
                f"{comment_markers[0]} (c) 1312 Benjamin Mummery {comment_markers[1]}"
            )
            input = f"{valid_copyright_comment}\n{valid_copyright_comment}"

            # WHEN
            with pytest.raises(ValueError) as e:
                copyright_parsing.parse_copyright_comment(input, comment_markers)

            # THEN
            assert_matching(
                "output exception",
                "expected exception",
                e.exconly(),
                "ValueError: Found multiple copyright strings: ['<mock_ParsedCopyrightString return sentinel>', '<mock_ParsedCopyrightString return sentinel>']",  # noqa: E501,
            )
