# Copyright (c) 2023 Benjamin Mummery

from typing import Optional, Tuple
from unittest.mock import Mock

import pytest
from mock import call
from pytest_mock import MockerFixture

from src._shared import copyright_parsing
from src._shared.comment_mapping import COMMENT_MARKERS
from tests.conftest import assert_matching


# region: fixtures mocking all public functions, classes, and methods.
@pytest.fixture()
def mock_ParsedCopyrightString(mocker: MockerFixture):
    return mocker.patch(
        "src._shared.copyright_parsing.ParsedCopyrightString",
        Mock(return_value="<mock_ParsedCopyrightString return sentinel>"),
    )


@pytest.fixture()
def mock_parse_copyright_string(mocker: MockerFixture):
    return mocker.patch(
        "src._shared.copyright_parsing.parse_copyright_string",
        Mock(return_value="<mock_parse_copyright_string return sentinel>"),
    )


@pytest.fixture()
def parse_copyright_string_from_content(mocker: MockerFixture):
    return mocker.patch(
        "src._shared.copyright_parsing.parse_copyright_string_from_content",
        Mock(return_value="<mock_parse_copyright_string_from_content return sentinel>"),
    )


# endregion


@pytest.mark.usefixtures(
    "mock_parse_copyright_string", "parse_copyright_string_from_content"
)
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


@pytest.mark.usefixtures(
    "mock_ParsedCopyrightString", "parse_copyright_string_from_content"
)
class TestParseCopyrightString:
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
        mock_ParsedCopyrightString,
    ):
        # WHEN
        ret = copyright_parsing.parse_copyright_string(input_string, comment_markers)

        # THEN
        _expected_args = [comment_markers] + expected_args + [input_string]
        mock_ParsedCopyrightString.assert_called_once_with(*_expected_args)
        assert ret == mock_ParsedCopyrightString.return_value

    @staticmethod
    @pytest.mark.parametrize("comment_markers", COMMENT_MARKERS.values())
    @pytest.mark.parametrize("input_string", ["Not a copyright string", ""])
    def test_returns_none_for_no_matches(
        comment_markers: Tuple[str, Optional[str]], input_string: str
    ):
        assert (
            copyright_parsing.parse_copyright_string(input_string, comment_markers)
            is None
        )

    @staticmethod
    @pytest.mark.parametrize("comment_markers", COMMENT_MARKERS.values())
    @pytest.mark.parametrize(
        "input_string", ["# (c) 1312 Thor Odinsson\n\nSome other content"]
    )
    def test_raises_exception_for_multiple_input_lines(
        input_string: str, comment_markers: Tuple[str, Optional[str]]
    ):
        with pytest.raises(ValueError) as e:
            copyright_parsing.parse_copyright_string(input_string, comment_markers)

        # THEN
        assert_matching(
            "Output exception",
            "Expected exception",
            e.exconly(),
            f"ValueError: parse_copyright_string is designed to examine one line at a time, got:\n{input_string}",  # noqa: E501
        )


@pytest.mark.usefixtures("mock_ParsedCopyrightString", "mock_parse_copyright_string")
@pytest.mark.parametrize("comment_markers", COMMENT_MARKERS.values())
class TestParseCopyrightStringFromContent:
    @staticmethod
    def test_returns_none_for_no_copyright_strings_found(
        comment_markers, mocker: MockerFixture
    ):
        # GIVEN
        mock_parse_copyright_string = mocker.patch(
            "src._shared.copyright_parsing.parse_copyright_string",
            Mock(return_value=None),
        )
        input = "foo\nbar\nbaz"

        # WHEN
        assert (
            copyright_parsing.parse_copyright_string_from_content(
                input, comment_markers
            )
            is None
        )

        # THEN
        mock_parse_copyright_string.assert_has_calls(
            [
                call("foo", comment_markers),
                call("bar", comment_markers),
                call("baz", comment_markers),
            ]
        )

    @staticmethod
    def test_returns_single_found_copyright_string(
        comment_markers, mocker: MockerFixture
    ):
        # GIVEN
        mock_parse_copyright_string = mocker.patch(
            "src._shared.copyright_parsing.parse_copyright_string",
            Mock(
                side_effect=[
                    None,
                    "<mock_parse_copyright_string return sentinel>",
                    None,
                ]
            ),
        )
        input = "foo\nbar\nbaz"

        # WHEN
        assert (
            copyright_parsing.parse_copyright_string_from_content(
                input, comment_markers
            )
            == "<mock_parse_copyright_string return sentinel>"
        )

        # THEN
        mock_parse_copyright_string.assert_has_calls(
            [
                call("foo", comment_markers),
                call("bar", comment_markers),
                call("baz", comment_markers),
            ]
        )

    @staticmethod
    def test_raises_exception_for_multiple_copyright_strings(
        comment_markers, mocker: MockerFixture
    ):
        # GIVEN
        input = "foo\nbar\nbaz"

        # WHEN
        with pytest.raises(ValueError) as e:
            copyright_parsing.parse_copyright_string_from_content(
                input, comment_markers
            )

        # THEN
        assert_matching(
            "output exception",
            "expected exception",
            e.exconly(),
            "ValueError: Found multiple copyright strings: ['<mock_parse_copyright_string return sentinel>', '<mock_parse_copyright_string return sentinel>', '<mock_parse_copyright_string return sentinel>']",  # noqa: E501,
        )
