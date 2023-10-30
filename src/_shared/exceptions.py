# Copyright (c) 2023 Benjamin Mummery

"""Custom exceptions used by the various hooks."""


class NoCommitsError(Exception):
    """Raised when a file has no commits for us to examine."""

    ...


class InvalidConfigError(Exception):
    """
    Raised when a config file cannot be correctly parsed.

    We use this to avoid having to worry about whether we're using tomli / tomllib
    outside of the config parser utility.
    """

    ...
