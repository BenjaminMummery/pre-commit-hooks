# Copyright (c) 2023 Benjamin Mummery

"""
Unit tests for the ParsedCopyrightString class.
"""

import pytest

from src.add_copyright_hook.add_copyright import ParsedCopyrightString

from ..conftest import ADD_COPYRIGHT_FIXTURE_LIST as FIXTURES

commentmarker = "<commentmarker sentinel>"
signifiers = "<signifier sentinel>"
start_year = 1111
end_year = 2222
name = "<name sentinel>"
string = "<string sentinel>"


@pytest.fixture(scope="module")
def parsed_string() -> ParsedCopyrightString:
    return ParsedCopyrightString(
        commentmarker,
        signifiers,
        start_year,
        end_year,
        name,
        string,
    )


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_ParsedCopyrightString"])
class TestInit:
    @staticmethod
    def test_happy_path(parsed_string):
        # GIVEN
        # WHEN
        # THEN
        assert parsed_string.commentmarker == commentmarker
        assert parsed_string.signifiers == signifiers
        assert parsed_string.start_year == start_year
        assert parsed_string.end_year == end_year
        assert parsed_string.name == name
        assert parsed_string.string == string

    @staticmethod
    def test_linear_time():
        # WHEN
        with pytest.raises(AssertionError) as e:
            _ = ParsedCopyrightString(
                commentmarker,
                signifiers,
                start_year,
                start_year - 1,
                name,
                string,
            )

        # THEN
        assert e.exconly() == "AssertionError: Time does not flow backwards."


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_ParsedCopyrightString"])
class TestEq:
    @staticmethod
    def test_equal(parsed_string):
        # GIVEN
        parsed_string_2 = ParsedCopyrightString(
            commentmarker,
            signifiers,
            start_year,
            end_year,
            name,
            string,
        )

        # WHEN
        # THEN
        assert parsed_string == parsed_string_2

    @staticmethod
    @pytest.mark.parametrize(
        "alt_commentmarker", [commentmarker, "<differing commentmarker sentinel>"]
    )
    @pytest.mark.parametrize(
        "alt_signifiers", [signifiers, "<differing signifiers sentinel>"]
    )
    @pytest.mark.parametrize("alt_start_year", [start_year, 1112])
    @pytest.mark.parametrize("alt_end_year", [end_year, 2223])
    @pytest.mark.parametrize("alt_name", [name, "<differing name sentinel>"])
    @pytest.mark.parametrize("alt_string", [string, "<differing string sentinel>"])
    def test_unequal(
        alt_commentmarker,
        alt_signifiers,
        alt_start_year,
        alt_end_year,
        alt_name,
        alt_string,
        parsed_string,
    ):
        # GIVEN
        if [commentmarker, signifiers, start_year, end_year, name, string] == [
            alt_commentmarker,
            alt_signifiers,
            alt_start_year,
            alt_end_year,
            alt_name,
            alt_string,
        ]:
            pytest.skip("Equal case covered by test_equal()")

        parsed_string_2 = ParsedCopyrightString(
            alt_commentmarker,
            alt_signifiers,
            alt_start_year,
            alt_end_year,
            alt_name,
            alt_string,
        )

        # WHEN
        # THEN
        assert parsed_string != parsed_string_2


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_ParsedCopyrightString"])
class TestRepr:
    @staticmethod
    def test_happy_path(parsed_string):
        assert repr(parsed_string) == (
            "ParsedCopyrightString object with:\n"
            f"- comment marker: {commentmarker}\n"
            f"- signifiers: {signifiers}\n"
            f"- start year: {start_year}\n"
            f"- end year: {end_year}\n"
            f"- name: {name}\n"
            f"- string: {string}"
        )
