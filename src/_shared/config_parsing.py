# Copyright (c) 2023 - 2024 Benjamin Mummery

"""Shared tools for parsing config files."""


import os
import sys
from pathlib import Path
from typing import Optional, Tuple

from src._shared.exceptions import InvalidConfigError


def read_config(tool_name: str) -> Tuple[dict, Path]:
    """
    Find configuration files and read in config options.

    Args:
        tool_name (str): The name of the tool whose configuration should be
            returned.

    Raises:
        FileNotFoundError: When there are no configuration files found.

    Returns:
        dict: A mapping of key-value pairs where the key is the config option
            name, and the value is its value.
    """
    # find config file
    filename = "pyproject.toml"
    filepath: Optional[Path] = None

    for root, _, files in os.walk(os.getcwd()):
        if filename in files:
            filepath = Path(os.path.join(root, filename))
            break

    if filepath is None:
        raise FileNotFoundError("No config file found.")

    # read config file
    return _read_pyproject_toml(filepath, tool_name), filepath


def _read_pyproject_toml(pyproject_toml: Path, tool_name: str) -> dict:
    """
    Read in default configuration options from a `pyproject.toml` file.

    Args:
        pyproject_toml (Path): The location of the file to be read.
        tool_name (str): The name of the tool whose options we want to read.

    Returns:
        dict: A mapping of key-value pairs where the key is the config option
            name, and the value is its value.
    """
    if sys.version_info >= (3, 11):  # pragma: no cover
        import tomllib  # pragma: no cover
    else:
        import tomli as tomllib  # pragma: no cover

    # Load in the config file
    with open(pyproject_toml, "rb") as f:
        try:
            config = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise InvalidConfigError(
                f"Could not parse config file '{pyproject_toml}'."
            ) from e

    # early return for no matching section in config file
    if not (tool_config := config.get("tool", {}).get(tool_name)):
        return {}

    return tool_config


def _read_setup_cfg(setup_cfg: Path, tool_name: str) -> dict:
    """
    Read in default configuration options from a `setup.cfg` file.

    Args:
        setup_cfg (Path): The location of the file to be read.
        tool_name (str): The name of the tool whose options we want to read.

    Returns:
        dict: A mapping of key-value pairs where the key is the config option
            name, and the value is its value.
    """
    pass
