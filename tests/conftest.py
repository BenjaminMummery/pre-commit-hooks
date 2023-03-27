# Copyright (c) 2023 Benjamin Mummery

import os
from contextlib import contextmanager

import pytest


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
SHARED_FIXTURE_LIST = ["mock_resolve_files"]


@pytest.fixture
def mock_resolve_files(mocker):
    return mocker.patch("src._shared.resolvers._resolve_files")


# endregion

# region: add_copyright fixtures
ADD_COPYRIGHT_FIXTURE_LIST = [
    "mock_construct_copyright_string",
    "mock_default_format",
    "mock_ensure_copyright_string",
    "mock_ensure_valid_format",
    "mock_get_current_year",
    "mock_get_git_user_name",
    "mock_has_shebang",
    "mock_insert_copyright_string",
    "mock_parse_args",
    "mock_parse_copyright_string",
    "mock_parse_years",
    "mock_read_config_file",
    "mock_resolve_format",
    "mock_resolve_user_name",
    "mock_resolve_year",
    "mock_update_copyright_string",
] + SHARED_FIXTURE_LIST


@pytest.fixture
def mock_construct_copyright_string(mocker):
    return mocker.patch(
        "src.add_copyright_hook.add_copyright._construct_copyright_string"
    )


@pytest.fixture
def mock_default_format(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright.DEFAULT_FORMAT")


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
def mock_get_git_user_name(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._get_git_user_name")


@pytest.fixture
def mock_has_shebang(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._has_shebang")


@pytest.fixture
def mock_insert_copyright_string(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._insert_copyright_string")


@pytest.fixture
def mock_parse_args(mocker):
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
def mock_resolve_year(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._resolve_year")


@pytest.fixture
def mock_update_copyright_string(mocker):
    return mocker.patch("src.add_copyright_hook.add_copyright._update_copyright_string")


# endregion
