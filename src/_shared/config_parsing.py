# Copyright (c) 2023 - 2024 Benjamin Mummery

"""Shared tools for parsing config files."""


import configparser
import logging
import os
import sys
from pathlib import Path
from typing import List, Tuple

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
    filenames = ["pyproject.toml", "setup.cfg"]
    filepaths: List[Path] = []

    files = os.listdir(root := os.getcwd())
    for filename in filenames:
        if filename in files:
            filepaths.append(Path(os.path.join(root, filename)))

    if len(filepaths) == 0:
        raise FileNotFoundError("No config file found.")

    if len(filepaths) > 1:  # pragma: no cover
        logging.warning(
            "Found multiple config files:\n"
            f"{filepaths}\n"
            f"Priority will be given to {filepaths[0]}"
        )

    # read config file
    filepath = filepaths[0]
    config: dict
    if filepath.name == "pyproject.toml":
        config = _read_pyproject_toml(filepath, tool_name)
    elif filepath.name == "setup.cfg":
        config = _read_setup_cfg(filepath, tool_name)
    return config, filepath


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
    config = configparser.ConfigParser()
    try:
        config.read(setup_cfg)
    except (configparser.MissingSectionHeaderError, configparser.ParsingError) as e:
        raise InvalidConfigError(f"Could not parse config file '{setup_cfg}'.") from e

    try:
        tool_config = dict(config.items(f"tool.{tool_name}"))
    except configparser.NoSectionError:
        return {}

    return tool_config
