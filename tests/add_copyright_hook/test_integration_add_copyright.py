# Copyright (c) 2023 Benjamin Mummery

"""
Integration tests for add_copyright.

Integrated components are defined as any unit that relies on at least one other unit.

Tests mock any method that does not fall within their boundary.
"""

import pytest
from freezegun import freeze_time

from src.add_copyright_hook import add_copyright

from ..conftest import ADD_COPYRIGHT_FIXTURE_LIST as FIXTURES

# Source code has the form:
#
# main()
# ├── _parse_args()
# |   ├── _resolve_user_name()
# |   ├── _resolve_year()
# |   ├── _resolve_format()
# |   └── resolvers._resolve_files()
# └── _ensure_copyright_string()
#     ├── _parse_copyright_string()
#     |   ├── _parse_years()
#     |   └── ParsedCopyrightString
#     ├── _copyright_is_current()
#     |   └── ParsedCopyrightString
#     ├── _update_copyright_string()
#     |   └── ParsedCopyrightString
#     ├── _construct_copyright_string
#     |   └── [_parse_copyright_string]
#     └── _insert_copyright_string
#         └── _has_shebang()
#
# Identified integrated components:
#
# - _parse_args()
# - _ensure_copyright_string()
# - _parse_copyright_string()
# - _copyright_is_current() # TODO
# - _update_copyright_string() # TODO
# - _construct_copyright_string()
# - _insert_copyright_string()

PARSE_ARGS_BOUNDARY = [
    "mock_parse_add_copyright_args",
    "mock_resolve_user_name",
    "mock_resolve_year",
    "mock_resolve_format",
    "mock_resolve_files",
]
PARSE_COPYRIGHT_STRING_BOUNDARY = [
    "mock_parse_copyright_string",
    "mock_parse_years",
    "mock_ParsedCopyrightString",
]
CONSTRUCT_COPYRIGHT_STING_BOUNDARY = [
    "mock_construct_copyright_string"
] + PARSE_COPYRIGHT_STRING_BOUNDARY
INSERT_COPYRIGHT_STING_BOUNDARY = ["mock_insert_copyright_string", "mock_has_shebang"]
COPYRIGHT_IS_CURRENT_BOUNDARY = [
    "mock_copyright_is_current",
    "mock_ParsedCopyrightString",
]
UPDATE_COPYRIGHT_STING_BOUNDARY = [
    "mock_update_copyright_string",
    "mock_ParsedCopyrightString",
]
ENSURE_COPYRIGHT_STING_BOUNDARY = (
    ["mock_ensure_copyright_string"]
    + PARSE_COPYRIGHT_STRING_BOUNDARY
    + COPYRIGHT_IS_CURRENT_BOUNDARY
    + UPDATE_COPYRIGHT_STING_BOUNDARY
    + CONSTRUCT_COPYRIGHT_STING_BOUNDARY
    + INSERT_COPYRIGHT_STING_BOUNDARY
)


@pytest.mark.usefixtures(*[f for f in FIXTURES if f not in PARSE_ARGS_BOUNDARY])
class TestParseArgs:
    @staticmethod
    def test_something(mocker):
        mocker.patch(
            "sys.argv",
            return_value=[
                "",
            ],
        )


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f not in ENSURE_COPYRIGHT_STING_BOUNDARY]
)
class TestEnsureCopyrightString:
    @staticmethod
    @pytest.mark.parametrize(
        "copyright_string", ["# COPYRIGHT 2012 ABADDON THE DESPOILER"]
    )
    def test_returns_0_for_extant_copyright_string(copyright_string, tmp_path):
        print([f for f in FIXTURES if f not in ENSURE_COPYRIGHT_STING_BOUNDARY])
        # GIVEN
        file = tmp_path / "file"
        file.write_text(copyright_string)

        # WHEN
        assert add_copyright._ensure_copyright_string(file, "", 2012, "") == 0

        # THEN
        with open(file) as f:
            contents = f.read()
        assert contents == copyright_string

    @staticmethod
    @pytest.mark.parametrize(
        "contents", ['"""docstring"""', "def foo():\n    print('bar')\n"]
    )
    def test_adds_copyright_string_before_file_contents(contents, tmp_path):
        # GIVEN
        file = tmp_path / "file"
        file.write_text(contents)
        format = "{name} {year}"
        expected = f"<name sentinel> 1111\n\n{contents}"

        # WHEN
        assert (
            add_copyright._ensure_copyright_string(
                file, "<name sentinel>", 1111, format
            )
            == 1
        )

        # THEN
        with open(file) as f:
            c = f.read()
        assert c == expected, f"out:\n{c}\nexpected:\n{expected}"

    @staticmethod
    def test_adds_copyright_string_to_empty_file(tmp_path):
        # GIVEN
        file = tmp_path / "file"
        file.write_text("")
        format = "{name} {year}"
        expected = "<name sentinel> 1111\n"

        # WHEN
        assert (
            add_copyright._ensure_copyright_string(
                file, "<name sentinel>", 1111, format
            )
            == 1
        )

        # THEN
        with open(file) as f:
            c = f.read()
        assert c == expected, f"out:\n{c}\nexpected:\n{expected}"

    @staticmethod
    @pytest.mark.parametrize(
        "contents", ['"""docstring"""', "def foo():\n    print('bar')\n"]
    )
    def test_adds_copyright_string_after_shebang(contents, tmp_path):
        # GIVEN
        file = tmp_path / "file"
        file.write_text(f"#!/blah\n\n{contents}")
        format = "{name} {year}"
        expected = f"#!/blah\n\n<name sentinel> 1111\n\n{contents}"

        # WHEN
        assert (
            add_copyright._ensure_copyright_string(
                file, "<name sentinel>", 1111, format
            )
            == 1
        )

        # THEN
        with open(file) as f:
            c = f.read()
        assert c == expected, f"out:\n{c}\nexpected:\n{expected}"

    @staticmethod
    @pytest.mark.parametrize(
        "contents, expected",
        [
            (
                "# COPYRIGHT 1111 ABADDON THE DESPOILER\n",
                "# COPYRIGHT 1111 - 2222 ABADDON THE DESPOILER\n",
            ),
            (
                "# COPYRIGHT 1111-1112 ABADDON THE DESPOILER\n",
                "# COPYRIGHT 1111-2222 ABADDON THE DESPOILER\n",
            ),
        ],
    )
    def test_updates_existing_copyright_string(contents, expected, tmp_path):
        # GIVEN
        file = tmp_path / "file"
        file.write_text(contents)

        # WHEN
        assert (
            add_copyright._ensure_copyright_string(
                file, "<name sentinel>", 2222, format
            )
            == 1
        )

        # THEN
        with open(file) as f:
            c = f.read()
        assert c == expected, f"out:\n{c}\nexpected:\n{expected}"


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f not in PARSE_COPYRIGHT_STRING_BOUNDARY]
)
class TestParseCopyrightString:
    @staticmethod
    def test_early_return_for_no_copyright_string():
        # WHEN / THEN
        assert add_copyright._parse_copyright_string("") is None

    @staticmethod
    @pytest.mark.parametrize(
        "input, expected",
        [
            (
                "# COPYRIGHT 2001 Stanley Kubrik",
                add_copyright.ParsedCopyrightString(
                    "#",
                    "COPYRIGHT",
                    2001,
                    2001,
                    "Stanley Kubrik",
                    "# COPYRIGHT 2001 Stanley Kubrik",
                ),
            ),
            (
                "# COPYRIGHT 2001-2023 Stanley Kubrik",
                add_copyright.ParsedCopyrightString(
                    "#",
                    "COPYRIGHT",
                    2001,
                    2023,
                    "Stanley Kubrik",
                    "# COPYRIGHT 2001-2023 Stanley Kubrik",
                ),
            ),
        ],
    )
    def test_parsing(input, expected):
        out = add_copyright._parse_copyright_string(input)
        assert out == expected, f"{out}\n{expected}"


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f not in COPYRIGHT_IS_CURRENT_BOUNDARY]
)
class TestCopyrightIsCurrent:
    @staticmethod
    @pytest.mark.parametrize("year", [1111, 1112, 2111, 9999])
    @freeze_time("1111-01-01")
    def test_returns_true_for_current_or_future_year(year):
        # GIVEN
        # WHEN
        # THEN
        assert add_copyright._copyright_is_current(
            add_copyright.ParsedCopyrightString(
                "<commentmarker sentinel>",
                "<signifiers sentinel>",
                year,
                year,
                "<name sentinel>",
                "<string sentinel 1111>",
            ),
            1111,
        )

    @staticmethod
    @pytest.mark.parametrize("year", [1110])
    @freeze_time("1111-01-01")
    def test_returns_false_for_past_year(year):
        # GIVEN
        # WHEN
        # THEN
        assert not add_copyright._copyright_is_current(
            add_copyright.ParsedCopyrightString(
                "<commentmarker sentinel>",
                "<signifiers sentinel>",
                year,
                year,
                "<name sentinel>",
                "<string sentinel 1111>",
            ),
            1111,
        )


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f not in UPDATE_COPYRIGHT_STING_BOUNDARY]
)
class TestUpdateCopyrightString:
    @staticmethod
    def test_single_year():
        assert (
            add_copyright._update_copyright_string(
                add_copyright.ParsedCopyrightString(
                    "<commentmarker sentinel>",
                    "<signifiers sentinel>",
                    1111,
                    1111,
                    "<name sentinel>",
                    "<string sentinel 1111>",
                ),
                2222,
            )
            == "<string sentinel 1111 - 2222>"
        )

    @staticmethod
    @pytest.mark.parametrize(
        "input_string, expected_output_string",
        [
            ("<string sentinel 1111-1112>", "<string sentinel 1111-2222>"),
            ("<string sentinel 1111 - 1112>", "<string sentinel 1111 - 2222>"),
        ],
    )
    def test_year_range(input_string, expected_output_string):
        assert (
            add_copyright._update_copyright_string(
                add_copyright.ParsedCopyrightString(
                    "<commentmarker sentinel>",
                    "<signifiers sentinel>",
                    1111,
                    1112,
                    "<name sentinel>",
                    input_string,
                ),
                2222,
            )
            == expected_output_string
        )


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f not in CONSTRUCT_COPYRIGHT_STING_BOUNDARY]
)
class TestConstructCopyrightString:
    @staticmethod
    @pytest.mark.parametrize(
        "format, expected", [("{name} {year}", "<name sentinel> 1111")]
    )
    def test_formatting(format, expected):
        assert (
            add_copyright._construct_copyright_string("<name sentinel>", 1111, format)
            == expected
        )


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f not in INSERT_COPYRIGHT_STING_BOUNDARY]
)
class TestInsertCopyrightString:
    @staticmethod
    @pytest.mark.parametrize(
        "content, expected",
        [
            ("Single line", "<copyright sentinel>\n\nSingle line"),
            ("Multiple\nlines", "<copyright sentinel>\n\nMultiple\nlines"),
            ("\nBlank first line", "<copyright sentinel>\n\nBlank first line"),
        ],
    )
    def test_happy_path(content, expected):
        out = add_copyright._insert_copyright_string("<copyright sentinel>", content)
        assert out == expected, f"out:\n{out}\nexpected:\n{expected}"

    @staticmethod
    @pytest.mark.parametrize(
        "content, expected",
        [
            ("#!shebang only", "#!shebang only\n\n<copyright sentinel>"),
            (
                "#!shebang and\nsingle line",
                "#!shebang and\n\n<copyright sentinel>\n\nsingle line",
            ),
        ],
    )
    def test_keeps_shebang_at_top(content, expected):
        out = add_copyright._insert_copyright_string("<copyright sentinel>", content)
        assert out == expected, f"out:\n{out}\nexpected:\n{expected}"
