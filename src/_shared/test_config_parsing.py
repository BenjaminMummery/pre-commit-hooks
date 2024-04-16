# Copyright (c) 2023 - 2024 Benjamin Mummery

import pytest

from conftest import assert_matching

from . import config_parsing

file_content = """[tool.foo]
option1="blah"

"""
invalid_file_content = """this [is not] valid
TOML

"""


class TestReadingPyprojectToml:
    class TestParsing:
        @staticmethod
        @pytest.mark.parametrize(
            "tool_name, expected_options", [("foo", {"option1": "blah"})]
        )
        def test_reads_correctly(
            tmp_path: config_parsing.Path, tool_name: str, expected_options: dict
        ):
            # GIVEN
            file = tmp_path / "pyproject.toml"
            file.write_text(file_content)

            # WHEN
            ret = config_parsing._read_pyproject_toml(file, tool_name)

            # THEN
            assert ret == expected_options

        @staticmethod
        def test_returns_empty_dict_for_missing_section(tmp_path: config_parsing.Path):
            # GIVEN
            file = tmp_path / "pyproject.toml"
            file.write_text(file_content)

            # WHEN
            ret = config_parsing._read_pyproject_toml(file, "tool_name")

            # THEN
            assert ret == {}

    class TestFailureStates:
        @staticmethod
        def test_raises_FileNotFoundError_for_missing_file(
            tmp_path: config_parsing.Path,
        ):
            # GIVEN
            file = tmp_path / "pyproject.toml"

            # WHEN / THEN
            with pytest.raises(FileNotFoundError):
                config_parsing._read_pyproject_toml(file, "tool_name")

        @staticmethod
        def test_raises_InvalidConfigError_for_invalid_toml(
            tmp_path: config_parsing.Path,
        ):
            # GIVEN
            file = tmp_path / "pyproject.toml"
            file.write_text(invalid_file_content)

            # WHEN
            with pytest.raises(config_parsing.InvalidConfigError) as e:
                config_parsing._read_pyproject_toml(file, "tool_name")

            # THEN
            assert_matching(
                "Output error string",
                "Expected error string",
                e.exconly(),
                f"src._shared.exceptions.InvalidConfigError: Could not parse config file '{file}'.",  # noqa: E501
            )
