# Copyright (c) 2023 Benjamin Mummery

import os
from contextlib import contextmanager
from unittest.mock import Mock

import pytest


def assert_matching(name1: str, name2: str, value1, value2):
    """
    Assert that 2 values are the same, and print an informative output if they are not.

    We compare quite a few longish strings in this repo, this gives a better way to
    understand where they're clashing.
    """
    assert value1 == value2, (
        f"{name1} did not match {name2}:\n"
        f"= {name1.upper()} ============\n"
        f"{value1}\n"
        f"= {name2.upper()} ==========\n"
        f"{value2}\n"
        "============================="
    )


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


# region: Shared fixtures
SHARED_FIXTURE_LIST = ["mock_get_comment_markers", "mock_resolve_files"]


@pytest.fixture
def mock_get_comment_markers(mocker):
    return mocker.patch("src._shared.comment_mapping.get_comment_markers")


@pytest.fixture
def mock_resolve_files(mocker):
    return mocker.patch("src._shared.resolvers._resolve_files")


# endregion

# region: add_copyright_hook_fixtures
SUPPORTED_FILES = [
    (".py", "# {content}"),
    (".md", "<!--- {content} -->"),
    (".cpp", "// {content}"),
    (".cs", "/* {content} */"),
    (".pl", "# {content}"),
]
VALID_COPYRIGHT_STRINGS = [
    "Copyright 1111 NAME",
    "Copyright (c) 1111 NAME",
    "(c) 1111 NAME",
]
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
