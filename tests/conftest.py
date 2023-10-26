# Copyright (c) 2023 Benjamin Mummery

import datetime
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union
from unittest.mock import Mock

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

# region: add_msg_issue_fixtures
ADD_MSG_ISSUE_FIXTURE_LIST = [
    "mock_default_template",
    "mock_fallback_template",
    "mock_get_branch_name",
    "mock_get_issue_ids_from_branch_name",
    "mock_insert_issue_into_message",
    "mock_issue_is_in_message",
    "mock_parse_add_msg_issue_args",
] + SHARED_FIXTURE_LIST


@pytest.fixture
def mock_default_template(mocker):
    return mocker.patch(
        "src.add_msg_issue_hook.add_msg_issue.DEFAULT_TEMPLATE", Mock(format=Mock())
    )


@pytest.fixture
def mock_fallback_template(mocker):
    return mocker.patch(
        "src.add_msg_issue_hook.add_msg_issue.FALLBACK_TEMPLATE", Mock(format=Mock())
    )


@pytest.fixture
def mock_get_branch_name(mocker):
    return mocker.patch("src.add_msg_issue_hook.add_msg_issue._get_branch_name")


@pytest.fixture
def mock_get_issue_ids_from_branch_name(mocker):
    return mocker.patch(
        "src.add_msg_issue_hook.add_msg_issue._get_issue_ids_from_branch_name"
    )


@pytest.fixture
def mock_insert_issue_into_message(mocker):
    return mocker.patch(
        "src.add_msg_issue_hook.add_msg_issue._insert_issue_into_message"
    )


@pytest.fixture
def mock_issue_is_in_message(mocker):
    return mocker.patch("src.add_msg_issue_hook.add_msg_issue._issue_is_in_message")


@pytest.fixture
def mock_parse_add_msg_issue_args(mocker):
    return mocker.patch("src.add_msg_issue_hook.add_msg_issue._parse_args")


# endregion

# region: sort_file_contents_fixtures

SORT_FILE_CONTENTS_FEATURE_LIST = [
    "mock_find_duplicates",
    "mock_identify_sections",
    "mock_parse_sort_file_contents_args",
    "mock_separate_leading_comment",
    "mock_sort_contents",
    "mock_sort_lines",
] + SHARED_FIXTURE_LIST

SORT_FILE_CONTENTS_IMPORT: str = "src.sort_file_contents_hook.sort_file_contents."


@pytest.fixture
def mock_sort_lines(mocker):
    return mocker.patch(SORT_FILE_CONTENTS_IMPORT + "_sort_lines")


@pytest.fixture
def mock_separate_leading_comment(mocker):
    return mocker.patch(SORT_FILE_CONTENTS_IMPORT + "_separate_leading_comment")


@pytest.fixture
def mock_identify_sections(mocker):
    return mocker.patch(SORT_FILE_CONTENTS_IMPORT + "_identify_sections")


@pytest.fixture
def mock_find_duplicates(mocker):
    return mocker.patch(SORT_FILE_CONTENTS_IMPORT + "_find_duplicates")


@pytest.fixture
def mock_sort_contents(mocker):
    return mocker.patch(SORT_FILE_CONTENTS_IMPORT + "_sort_contents")


@pytest.fixture
def mock_parse_sort_file_contents_args(mocker):
    return mocker.patch(SORT_FILE_CONTENTS_IMPORT + "_parse_args")


# endregion
