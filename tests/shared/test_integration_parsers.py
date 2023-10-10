# Copyright (c) 2023 Benjamin Mummery

from pathlib import Path

import pytest

from src._shared import parsers

file_content = """[tool.foo]
option1="blah"

"""


@pytest.mark.parametrize("tool_name, expected_options", [("foo", {"option1": "blah"})])
def test_happy_path(tmp_path: Path, tool_name: str, expected_options: dict):
    file = tmp_path / "pyproject.toml"
    file.write_text(file_content)

    assert parsers.read_pyproject_toml(file, tool_name) == expected_options
