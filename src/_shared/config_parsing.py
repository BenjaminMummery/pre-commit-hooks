# Copyright (c) 2023 Benjamin Mummery

"""
Shared tools for parsing config files.

These tools are purely focussed on ingesting data from config files and do not make any
assumptions about which options are valid. The one exception to this is where there are
duplicated or clashing entries, either inter or intra.
"""


import os
import sys
from configparser import ConfigParser
from pathlib import Path
from typing import Tuple

from src._shared.exceptions import InvalidConfigError


def _read_pyproject_toml(pyproject_toml: Path, tool_name: str) -> dict:
    """
    Read in default configuration options from a pyproject.toml file.

    Args:
        pyproject_toml (Path): The location of the file to be read.
        tool_name (str): The name of the tool whose options we want to read.

    Raises:
        InvalidConfigError: when the content of the file cannot be parsed.

    Returns:
        dict: A mapping of key-value pairs where the key is the config option
            name, and the value is its value.
    """
    if sys.version_info >= (3, 11):  # pragma: no cover
        import tomllib  # pragma: no cover
    else:
        import tomli as tomllib  # pragma: no cover

    # Load in the config file
    with open(pyproject_toml, "r") as f:
        content = f.read()
    with open(pyproject_toml, "rb") as f:
        try:
            config = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            print(content)
            raise InvalidConfigError(
                f"Could not parse config file '{pyproject_toml}'."
            ) from e

    # early return for no matching section in config file
    if not (tool_config := config.get("tool", {}).get(tool_name)):
        return {}

    return tool_config


def _read_ini(filepath: Path, tool_name: str) -> dict:
    """
    Read in default configuration opentions from a setup.cfg file.

    Args:
        filepath (Path): The location of the file to be read.
        tool_name (str): The name of the tool whose options we want to read.

    Returns:
        dict: A mapping of key-value pairs where the key is the config option
            name, and the value is its value.
    """
    config_object = ConfigParser()
    config_object.read(filepath)
    hook_level = config_object[tool_name]
    outdict = {}
    for key in hook_level.keys():
        outdict[key] = hook_level[key]
    return outdict


def read_config(tool_name: str) -> Tuple[dict, Path]:
    """
    Read in configuration options for the specified tool.

    The current working directory are be searched for supported configuration files.
    Options for the specified tool are read in and returned as a dict.

    Args:
        tool_name (str): The name of the tool for which configuration options are
            desired.

    Raises:
        FileNotFoundError: When no configuration files are found.

    Returns:
        Tuple[dict, Path]: The parsed configuration options, and the file from which
            they were read.
    """
    supported_config_files: dict = {
        "pyproject.toml": _read_pyproject_toml,
        "setup.cfg": _read_ini,
    }
    for root, _, files in os.walk(os.getcwd()):
        for filename in supported_config_files.keys():
            if filename in files:
                filepath = Path(os.path.join(root, filename))
                return supported_config_files[filename](filepath, tool_name), filepath
    raise FileNotFoundError("No config files found.")
