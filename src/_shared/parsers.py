# Copyright (c) 2023 Benjamin Mummery

"""Shared tools for parsing files."""


import sys
from pathlib import Path


def read_pyproject_toml(pyproject_toml: Path, tool_name: str) -> dict:
    """
    Read in default configuration options from a pyproject.toml file.

    Args:
        pyproject_toml (Path): The location of the file to be read.
        tool_name (str): The name of the tool whose options we want to read.

    Returns:
        dict: A mapping of key-value pairs where the key is the cnfig option
            name, and the value is its value.
    """
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib

    # Load in the config file
    with open(pyproject_toml, "rb") as f:
        config = tomllib.load(f)

    # early return for no matching section in config file
    if not (tool_config := config.get("tool", {}).get(tool_name)):
        raise Exception

    return tool_config
