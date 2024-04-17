# Copyright (c) 2023 - 2024 Benjamin Mummery

import pytest
from pytest_mock import MockerFixture

from conftest import assert_matching

from . import config_parsing

file_content = """[tool.foo]
option1="blah"

"""
invalid_file_content = """this [is not] valid
TOML

"""


class TestReadConfig:
    class TestSingleConfigFile:
        @staticmethod
        def test_identifies_pyproject_toml(
            tmp_path: config_parsing.Path, cwd, mocker: MockerFixture
        ):
            # GIVEN
            config_path = tmp_path / "pyproject.toml"
            config_path.write_text("")
            mocked_read_pyproject_toml = mocker.patch(
                f"{config_parsing.__name__}._read_pyproject_toml",
                return_value="<toml return sentinel>",
            )

            # WHEN
            with cwd(tmp_path):
                ret = config_parsing.read_config("<tool name sentinel>")

            # THEN
            assert ret == (mocked_read_pyproject_toml.return_value, config_path)
            mocked_read_pyproject_toml.assert_called_once_with(
                config_path, "<tool name sentinel>"
            )

    class TestFailureStates:
        @staticmethod
        def test_raises_FileNotFoundError_if_there_are_no_config_files(
            tmp_path: config_parsing.Path, cwd
        ):
            # WHEN
            with pytest.raises(FileNotFoundError) as e:
                with cwd(tmp_path):
                    config_parsing.read_config("<tool name sentinel>")

            # THEN
            assert e.exconly() == "FileNotFoundError: No config file found."


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
