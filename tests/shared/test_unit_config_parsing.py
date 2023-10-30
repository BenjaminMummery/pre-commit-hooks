# Copyright (c) 2023 Benjamin Mummery

from pathlib import Path

import pytest

from src._shared import config_parsing
from src._shared.exceptions import InvalidConfigError
from tests.conftest import assert_matching

file_content = """[tool.foo]
option1="blah"

"""
invalid_file_content = """this [is not] valid
TOML

"""


class TestParsing:
    @staticmethod
    @pytest.mark.parametrize(
        "tool_name, expected_options", [("foo", {"option1": "blah"})]
    )
    def test_reads_correctly(tmp_path: Path, tool_name: str, expected_options: dict):
        file = tmp_path / "pyproject.toml"
        file.write_text(file_content)

        assert config_parsing.read_pyproject_toml(file, tool_name) == expected_options

    @staticmethod
    def test_returns_empty_dict_for_missing_section(tmp_path: Path):
        file = tmp_path / "pyproject.toml"
        file.write_text(file_content)

        assert config_parsing.read_pyproject_toml(file, "tool_name") == {}


class TestFailureStates:
    @staticmethod
    def test_raises_FileNotFoundError_for_missing_file(tmp_path: Path):
        file = tmp_path / "pyproject.toml"

        with pytest.raises(FileNotFoundError):
            config_parsing.read_pyproject_toml(file, "tool_name")

    @staticmethod
    def test_raises_InvalidConfigError_for_invalid_toml(tmp_path: Path):
        file = tmp_path / "pyproject.toml"
        file.write_text(invalid_file_content)

        with pytest.raises(InvalidConfigError) as e:
            config_parsing.read_pyproject_toml(file, "tool_name")

        assert_matching(
            "Output error string",
            "Expected error string",
            e.exconly(),
            f"src._shared.exceptions.InvalidConfigError: Could not parse config file '{file}'.",  # noqa: E501
        )
