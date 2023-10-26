# Copyright (c) 2023 Benjamin Mummery

from pathlib import Path

import pytest

from src._shared import config_parsing

file_content = """[tool.foo]
option1="blah"

"""


@pytest.mark.parametrize("tool_name, expected_options", [("foo", {"option1": "blah"})])
def test_happy_path(tmp_path: Path, tool_name: str, expected_options: dict):
    file = tmp_path / "pyproject.toml"
    file.write_text(file_content)

    assert config_parsing.read_pyproject_toml(file, tool_name) == expected_options


def test_raises_FileNotFoundError_for_missing_file(tmp_path: Path):
    file = tmp_path / "pyproject.toml"

    with pytest.raises(FileNotFoundError):
        config_parsing.read_pyproject_toml(file, "tool_name")


def test_returns_empty_dict_for_missing_section(tmp_path: Path):
    file = tmp_path / "pyproject.toml"
    file.write_text(file_content)

    assert config_parsing.read_pyproject_toml(file, "tool_name") == {}
