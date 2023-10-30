# Copyright (c) 2023 Benjamin Mummery

from typing import Optional, Tuple
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from src._shared import copyright_parsing
from src._shared.comment_mapping import COMMENT_MARKERS
from tests.conftest import assert_matching


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
                f"Got {end_year} and {start_year} respectively.",
            ),
        )


@pytest.fixture()
def mock_ParsedCopyrightString(mocker: MockerFixture):
    return mocker.patch(
        "src._shared.copyright_parsing.ParsedCopyrightString",
        Mock(return_value="<return sentinel>"),
    )


@pytest.mark.usefixtures("mock_ParsedCopyrightString")
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
    @pytest.mark.parametrize("input_string", ["Not a copyright string"])
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
