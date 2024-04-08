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
