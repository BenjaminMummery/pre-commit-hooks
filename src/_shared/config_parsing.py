# Copyright (c) 2023 - 2026 Benjamin Mummery
"""Shared tools for parsing config files."""

from __future__ import annotations

import configparser
import logging
import sys

from pathlib import Path

from src._shared.exceptions import InvalidConfigError

logger = logging.getLogger(__name__)


def read_config(tool_name: str) -> tuple[dict, Path]:
    """Find configuration files and read in config options.

    Args:
        tool_name (str): The name of the tool whose configuration should be
            returned.

    Raises:
        FileNotFoundError: When there are no configuration files found.

    Returns:
        tuple[dict, Path]: A mapping of key-value pairs where the key is the
            config option name, and the value is its value.
    """
    # find config file
    filenames = ["pyproject.toml", "setup.cfg"]
    root = Path.cwd()
    existing = {path.name for path in root.iterdir()}
    filepaths = [root / filename for filename in filenames if filename in existing]

    if len(filepaths) == 0:
        msg = "No config file found."
        raise FileNotFoundError(msg)

    if len(filepaths) > 1:  # pragma: no cover
        logger.warning(
            "Found multiple config files:\n"
            f"{filepaths}\n"
            f"Priority will be given to {filepaths[0]}",
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
    """Read in default configuration options from a `pyproject.toml` file.

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
    with pyproject_toml.open("rb") as f:
        try:
            config = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            msg = f"Could not parse config file '{pyproject_toml}'."
            raise InvalidConfigError(
                msg,
            ) from e

    # early return for no matching section in config file
    if not (tool_config := config.get("tool", {}).get(tool_name)):
        return {}

    return dict(tool_config)


def _read_setup_cfg(setup_cfg: Path, tool_name: str) -> dict:
    """Read in default configuration options from a `setup.cfg` file.

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
        msg = f"Could not parse config file '{setup_cfg}'."
        raise InvalidConfigError(
            msg,
        ) from e

    try:
        tool_config = dict(config.items(f"tool.{tool_name}"))
    except configparser.NoSectionError:
        return {}

    return dict(tool_config)
