# Copyright (c) 2024 Benjamin Mummery

from unittest.mock import Mock, create_autospec

import pytest
from git.repo.base import BlameEntry
from pytest_mock import MockerFixture

from src.add_copyright_hook import add_copyright
from src.add_copyright_hook.add_copyright import (
    GitCommandError,
    InvalidGitRepositoryError,
    NoCommitsError,
    Path,
    Repo,
    argparse,
)


@pytest.fixture()
def mock_repo(mocker: MockerFixture) -> add_copyright.Repo:
    mocked_repo = create_autospec(Repo)
    mocker.patch(f"{add_copyright.__name__}.Repo", Mock(return_value=mocked_repo))
    return mocked_repo


class TestGetEarliestCommitYear:
    @staticmethod
    def test_raises_InvalidGitRepositoryError_for_nonexistent_git_repo(
        tmp_path: Path,
        cwd,
        mocker,
    ):
        # GIVEN
        mocker.patch(
            f"{add_copyright.__name__}.Repo",
            Mock(side_effect=InvalidGitRepositoryError),
        )

        # WHEN / THEN
        with pytest.raises(InvalidGitRepositoryError):
            with cwd(tmp_path):
                add_copyright._get_earliest_commit_year(Mock())

    @staticmethod
    def test_raises_NoCommitsError_for_nonexistent_git_repo(
        tmp_path: Path,
        cwd,
        mock_repo,
    ):
        # GIVEN
        mock_repo.blame.side_effect = GitCommandError(["<command sentinel>"])

        # WHEN / THEN
        with pytest.raises(NoCommitsError):
            with cwd(tmp_path):
                add_copyright._get_earliest_commit_year(Mock())

    @staticmethod
    def test_single_commit(tmp_path: Path, cwd, mock_repo):
        # GIVEN
        mock_blameentry = create_autospec(BlameEntry)
        mock_repo.blame.return_value = [mock_blameentry]

        # WHEN
        with cwd(tmp_path):
            ret = add_copyright._get_earliest_commit_year(Mock())

        # THEN
        assert ret == 1970


class TestParseArgs:
    @staticmethod
    def test_parse_args(mocker: MockerFixture):
        # GIVEN
        mocked_argparse = create_autospec(argparse.ArgumentParser)
        mocker.patch(
            f"{add_copyright.__name__}.argparse.ArgumentParser",
            Mock(return_value=mocked_argparse),
        )
        mocker.patch(
            f"{add_copyright.__name__}.resolvers.resolve_files",
            return_value=["<file sentinel>"],
        )

        # WHEN
        ret = add_copyright._parse_args()

        # THEN
        assert ret["files"] == ["<file sentinel>"]


class TestGetGitUserName:
    @staticmethod
    @pytest.mark.parametrize("return_name", [None, ""])
    def test_raises_valueerror_for_no_configured_username(mock_repo, return_name):
        # GIVEN
        mock_reader = Mock()
        mock_reader.get_value.return_value = return_name
        mock_repo.config_reader.return_value = mock_reader

        # WHEN
        with pytest.raises(ValueError) as e:
            _ = add_copyright._get_git_user_name()

        # THEN
        assert e.exconly() == "ValueError: The git username is not configured."

    @staticmethod
    def test_get_git_user_name(mock_repo):
        # GIVEN
        mock_reader = Mock()
        mock_reader.get_value.return_value = "<name sentinel>"
        mock_repo.config_reader.return_value = mock_reader

        # WHEN
        ret = add_copyright._get_git_user_name()

        # THEN
        assert ret == "<name sentinel>"


class TestHasShebang:
    @staticmethod
    @pytest.mark.parametrize("input", ["#! thing/other"])
    def test_returns_true_for_shebang(input):
        assert add_copyright._has_shebang(input)

    @staticmethod
    @pytest.mark.parametrize("input", ["# Not a shebang"])
    def test_returns_false_for_no_shebang(input):
        assert not add_copyright._has_shebang(input)
