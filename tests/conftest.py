# Copyright (c) 2023 Benjamin Mummery

import datetime
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

import pytest
from pytest_git import GitRepo
from pytest_mock import MockerFixture


# region: shared utilities
def assert_matching(
    name1: str, name2: str, value1, value2, message: Optional[str] = None
):
    """
    Assert that 2 values are the same, and print an informative output if they are not.

    We compare quite a few longish strings in this repo, this gives a better way to
    understand where they're clashing.
    """
    failure_message = (
        f"{name1} did not match {name2}:\n"
        f"= {name1.upper()} ============\n"
        f"{value1}\n"
        f"= {name2.upper()} ==========\n"
        f"{value2}\n"
        "============================="
    )
    if message:
        failure_message += f"\n{message}"
    assert value1 == value2, failure_message


class Globals:
    THIS_YEAR = datetime.date.today().year


def add_changed_files(
    filenames: Union[str, List[str]],
    contents: Union[str, List[str]],
    git_repo: GitRepo,
    mocker: Optional[MockerFixture] = None,
):
    if not isinstance(filenames, list):
        filenames = [filenames]
    if not isinstance(contents, list):
        contents = [contents for _ in filenames]
    for filename, content in zip(filenames, contents):
        (git_repo.workspace / filename).write_text(content)
        git_repo.run(f"git add {filename}")
    if mocker:
        return mocker.patch("sys.argv", ["stub_name"] + filenames)


def write_config_file(path: Path, content: str) -> Path:
    config_file = path / "pyproject.toml"
    (config_file).write_text(content)
    return config_file


SHARED_FIXTURE_LIST = ["mock_get_comment_markers", "mock_resolve_files"]
# endregion


# region: Shared fixtures
@pytest.fixture(scope="session")
def cwd():
    @contextmanager
    def cwd(path):
        oldcwd = os.getcwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(oldcwd)

    return cwd


@pytest.fixture()
def git_repo(git_repo: GitRepo) -> GitRepo:
    git_repo.run("git config user.name '<git config username sentinel>'")
    return git_repo


@pytest.fixture
def mock_get_comment_markers(mocker):
    return mocker.patch("src._shared.comment_mapping.get_comment_markers")


@pytest.fixture
def mock_resolve_files(mocker):
    return mocker.patch("src._shared.resolvers.resolve_files")


# endregion


# region: add_copyright_hook_fixtures
class SupportedLanguage(object):
    """
    Encompass everything we need to run tests by iterating programmatically over
    supported languages.
    """

    def __init__(
        self,
        tag: str,
        toml_key: str,
        extension: str,
        comment_format: str,
        custom_copyright_format_commented: str,
        custom_copyright_format_uncommented: str,
    ):
        self.tag: str = tag
        self.toml_key: str = toml_key
        self.extension: str = extension
        self.comment_format: str = comment_format
        self.custom_copyright_format_commented: str = custom_copyright_format_commented
        self.custom_copyright_format_uncommented: str = (
            custom_copyright_format_uncommented
        )

    def __str__(self):
        return self.tag


@dataclass
class CopyrightGlobals:
    SUPPORTED_LANGUAGES = [
        SupportedLanguage(
            "python",
            "python",
            ".py",
            "# {content}",
            "################################################################################\n# © Copyright {year} {name}\n################################################################################",  # noqa: E501
            "Copyright {name} as of {year}",
        ),
        SupportedLanguage(
            "markdown",
            "markdown",
            ".md",
            "<!--- {content} -->",
            "<!--- Copyright {name} as of {year}. -->",
            "Copyright {name} as of {year}",
        ),
        SupportedLanguage(
            "c++",
            "cpp",
            ".cpp",
            "// {content}",
            "// Copyright {name} as of {year}.",
            "Copyright {name} as of {year}",
        ),
        SupportedLanguage(
            "c#",
            "c-sharp",
            ".cs",
            "/* {content} */",
            "/* Copyright {name} as of {year}.*/",
            "Copyright {name} as of {year}",
        ),
        SupportedLanguage(
            "perl",
            "perl",
            ".pl",
            "# {content}",
            "# Copyright {name} as of {year}.",
            "Copyright {name} as of {year}",
        ),
    ]
    VALID_COPYRIGHT_STRINGS = [
        "Copyright {end_year} NAME",
        "Copyright (c) {end_year} NAME",
        "(c) {end_year} NAME",
        "Copyright 1026-{end_year} Aristotle",
        "Copyright 1026 - {end_year} Aristotle",
    ]
    INVALID_COPYRIGHT_STRINGS = [
        (
            "Copyright 2012 - 1312 NAME",
            "ValueError: Copyright end year cannot be before the start year. Got 1312 and 2012 respectively.",  # noqa: E501
        )
    ]
    SUPPORTED_TOP_LEVEL_CONFIG_OPTIONS = [
        "name",
        "format",
        "python",
        "markdown",
        "cpp",
        "c-sharp",
        "perl",
    ]
    SUPPORTED_PER_LANGUAGE_CONFIG_OPTIONS = ["format"]


# endregion


# region: sort_file_contents_fixtures


@dataclass
class SortFileContentsGlobals:
    SORTED_FILE_CONTENTS = [
        "Alpha\nBeta\nGamma",
        "A\nC\nE\n\nB\nD\nF",
        "# leading comment with clashing entry\n# beta\nbeta\ndelta\nzulu\n",
    ]
    UNSORTED_FILE_CONTENTS = [
        (
            "beta\ndelta\ngamma\nalpha\n",
            "alpha\nbeta\ndelta\ngamma\n",
            "no sections",
        ),
        (
            "beta\ndelta\n\ngamma\nalpha\n",
            "beta\ndelta\n\nalpha\ngamma\n",
            "sections",
        ),
        (
            "# zulu\nbeta\ndelta\ngamma\nalpha\n",
            "# zulu\nalpha\nbeta\ndelta\ngamma\n",
            "leading comment, no sections",
        ),
        (
            "# zulu\n# alpha\nbeta\ngamma\ndelta\n",
            "# zulu\n# alpha\nbeta\ndelta\ngamma\n",
            "multiline leading comment, no sections",
        ),
        (
            "# zulu\nbeta\ndelta\n\n# epsilon\ngamma\nalpha\n",
            "# zulu\nbeta\ndelta\n\n# epsilon\nalpha\ngamma\n",
            "multiple sections with leading comment",
        ),
        (
            "beta\n# zulu\ndelta\ngamma\nalpha\n",
            "alpha\nbeta\ndelta\ngamma\n# zulu\n",
            "commented line within section - sort to end",
        ),
        (
            "beta\nzulu\n# delta\ngamma\nalpha\n",
            "alpha\nbeta\n# delta\ngamma\nzulu\n",
            "commented line within section - sort to middle",
        ),
        (
            "beta\ndelta\n\n# zulu\n\ngamma\nalpha\n",
            "beta\ndelta\n\n# zulu\n\nalpha\ngamma\n",
            "floating comment",
        ),
        (
            "beta\ndelta\nbeta\n\ngamma\nalpha\ngamma\n",
            "beta\nbeta\ndelta\n\nalpha\ngamma\ngamma\n",
            "duplicates within sections",
        ),
        (
            "beta\ndelta\n\ngamma\nalpha\ndelta\n",
            "beta\ndelta\n\nalpha\ndelta\ngamma\n",
            "duplicates between sections",
        ),
        (
            "beta\ndelta\n\n\ngamma\nalpha\n",
            "beta\ndelta\n\nalpha\ngamma\n",
            "double linebreak between sections",
        ),
    ]
    DUPLICATES_WITHIN_SECTIONS_FILE_CONTENTS = [
        (
            "beta\ndelta\ngamma\nalpha\ndelta\n",
            "alpha\nbeta\ndelta\ngamma\n",
            "no sections",
        ),
        (
            "beta\ndelta\nbeta\n\ngamma\nalpha\nalpha\n",
            "beta\ndelta\n\nalpha\ngamma\n",
            "sections",
        ),
        (
            "# zulu\nbeta\ndelta\ngamma\nalpha\ngamma\n",
            "# zulu\nalpha\nbeta\ndelta\ngamma\n",
            "leading comment, no sections",
        ),
        (
            "# zulu\nbeta\ndelta\ndelta\n\n# epsilon\ngamma\nalpha\n",
            "# zulu\nbeta\ndelta\n\n# epsilon\nalpha\ngamma\n",
            "multiple sections with leading comment",
        ),
        (
            "beta\ndelta\n# zulu\n# zulu\n",
            "beta\ndelta\n# zulu\n",
            "duplicate comments",
        ),
    ]
    DUPLICATES_BETWEEN_SECTIONS_FILE_CONTENTS = [
        ("beta\ndelta\n\ngamma\nalpha\ndelta\n", "delta", "simple case")
    ]
    COMMENTED_AND_UNCOMMENTED_DUPLICATES = [
        ("beta\n# zulu\ndelta\ngamma\nalpha\nzulu\n", "zulu", "simple clash"),
        (
            "# leading comment\n# zulu\n# including clash\nalpha\n# alpha\nzulu",
            "alpha",
            "potential clash in leading comment",
        ),
    ]


# endregion
