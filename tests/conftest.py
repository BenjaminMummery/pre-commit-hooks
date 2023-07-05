# Copyright (c) 2023 Benjamin Mummery

import os
from contextlib import contextmanager
from unittest.mock import Mock, create_autospec

import pytest

import src


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

# region: add_copyright fixtures
ADD_COPYRIGHT_FIXTURE_LIST = [
    "mock_confirm_file_updated",
    "mock_construct_copyright_string",
    "mock_copyright_is_current",
    "mock_default_config_file",
    "mock_default_format",
    "mock_ensure_comment",
    "mock_ensure_copyright_string",
    "mock_ensure_valid_format",
    "mock_get_current_year",
    "mock_get_earliest_commit_year",
    "mock_get_git_user_name",
    "mock_has_shebang",
    "mock_infer_start_year",
    "mock_insert_copyright_string",
    "mock_parse_add_copyright_args",
    "mock_parse_copyright_string",
    "mock_parse_years",
    "mock_ParsedCopyrightString",
    "mock_ParsedCopyrightString_constructor",
    "mock_read_config_file",
    "mock_resolve_format",
    "mock_resolve_user_name",
    "mock_update_copyright_string",
] + SHARED_FIXTURE_LIST


@pytest.fixture
def mock_confirm_file_updated(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._confirm_file_updated")


@pytest.fixture
def mock_construct_copyright_string(mocker):
    return mocker.patch(
        "src.add_copyright_hook.add_copyright._construct_copyright_string"
    )


@pytest.fixture
def mock_copyright_is_current(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._copyright_is_current")


@pytest.fixture
def mock_default_config_file(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright.DEFAULT_CONFIG_FILE")


@pytest.fixture
def mock_default_format(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright.DEFAULT_FORMAT")


@pytest.fixture
def mock_ensure_comment(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._ensure_comment")


@pytest.fixture
def mock_ensure_copyright_string(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._ensure_copyright_string")


@pytest.fixture
def mock_ensure_valid_format(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._ensure_valid_format")


@pytest.fixture
def mock_get_current_year(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._get_current_year")


@pytest.fixture
def mock_get_earliest_commit_year(mocker):
    return mocker.patch(
        "src.add_copyright_hook.add_copyright._get_earliest_commit_year"
    )


@pytest.fixture
def mock_get_git_user_name(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._get_git_user_name")


@pytest.fixture
def mock_has_shebang(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._has_shebang")


@pytest.fixture
def mock_infer_start_year(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._infer_start_year")


@pytest.fixture
def mock_insert_copyright_string(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._insert_copyright_string")


@pytest.fixture
def mock_parse_add_copyright_args(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._parse_args")


@pytest.fixture
def mock_parse_copyright_string(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._parse_copyright_string")


@pytest.fixture
def mock_parse_years(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._parse_years")


@pytest.fixture
def mock_read_config_file(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._read_config_file")


@pytest.fixture
def mock_resolve_format(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._resolve_format")


@pytest.fixture
def mock_resolve_user_name(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._resolve_user_name")


@pytest.fixture
def mock_update_copyright_string(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._update_copyright_string")


@pytest.fixture
def mock_ParsedCopyrightString(mocker):
    return create_autospec(src.add_copyright_hook.add_copyright.ParsedCopyrightString)


@pytest.fixture
def mock_ParsedCopyrightString_constructor(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright.ParsedCopyrightString")


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

# region: test_check_changelog_clash_fixtures

CHECK_CHANGELOG_CLASH_FIXTURE_LIST = [
    "mock_check_changelog_clash",
    "mock_get_changes",
    "mock_get_heading_level",
    "mock_parse_check_changelog_clash_args",
    "mock_parse_section",
    "mock_parse_subsections",
] + SHARED_FIXTURE_LIST

CHECK_CHANGELOG_CLASH_IMPORT: str = (
    "src.check_changelog_clash_hook.check_changelog_clash."
)


@pytest.fixture
def mock_get_changes(mocker):
    return mocker.patch(CHECK_CHANGELOG_CLASH_IMPORT + "_get_changes")


@pytest.fixture
def mock_check_changelog_clash(mocker):
    return mocker.patch(CHECK_CHANGELOG_CLASH_IMPORT + "_check_changelog_clash")


@pytest.fixture
def mock_parse_check_changelog_clash_args(mocker):
    return mocker.patch(CHECK_CHANGELOG_CLASH_IMPORT + "_parse_args")


@pytest.fixture
def mock_get_heading_level(mocker):
    return mocker.patch(CHECK_CHANGELOG_CLASH_IMPORT + "_get_heading_level")


@pytest.fixture
def mock_parse_section(mocker):
    return mocker.patch(CHECK_CHANGELOG_CLASH_IMPORT + "_parse_section")


@pytest.fixture
def mock_parse_subsections(mocker):
    return mocker.patch(CHECK_CHANGELOG_CLASH_IMPORT + "_parse_subsections")


# endregion
