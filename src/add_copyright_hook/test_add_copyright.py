# Copyright (c) 2024 Benjamin Mummery

from unittest.mock import Mock, create_autospec

import pytest
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
    return mocker.patch(
        f"{add_copyright.__name__}.Repo", Mock(return_value=create_autospec(Repo))
    )


class TestGetEarliestCommitYear:
    @staticmethod
    def test_raises_InvalidGitRepositoryError_for_nonexistent_git_repo(
        tmp_path: Path,
        cwd,
        mock_repo,
    ):
        # GIVEN
        mock_repo.side_effect = InvalidGitRepositoryError

        # WHEN / THEN
        with pytest.raises(InvalidGitRepositoryError):
            with cwd(tmp_path):
                add_copyright._get_earliest_commit_year(Mock())

    @staticmethod
    def test_raises_NoCommitsError_for_nonexistent_git_repo(
        tmp_path: Path,
        cwd,
        mocker,
    ):
        # GIVEN
        mocked_repo = create_autospec(Repo)
        mocked_repo.blame.side_effect = GitCommandError(["<command sentinel>"])
        mocker.patch(f"{add_copyright.__name__}.Repo", Mock(return_value=mocked_repo))

        # WHEN / THEN
        with pytest.raises(NoCommitsError):
            with cwd(tmp_path):
                add_copyright._get_earliest_commit_year(Mock())
