# Copyright (c) 2023 Benjamin Mummery

"""
Custom exceptions used by the various hooks.
"""


class NoCommitsError(Exception):
    """Raised when a file has no commits for us to examine."""

    ...
