# Copyright (c) 2023 Benjamin Mummery

from unittest.mock import Mock, call, create_autospec

import git
import pytest

from src.check_changelog_clash_hook import check_changelog_clash

from ..conftest import CHECK_CHANGELOG_CLASH_FIXTURE_LIST as FIXTURES


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_check_changelog_clash"])
class TestCheckChangelogClash:
    @staticmethod
    def test_returns_0_for_no_differences(mock_get_changes):
        # GIVEN
        comparison = create_autospec(check_changelog_clash.FileComparison)
        comparison.has_changes = False
        mock_get_changes.return_value = comparison

        # WHEN
        ret = check_changelog_clash._check_changelog_clash("<file sentinel>")

        # THEN
        assert ret == 0
        mock_get_changes.assert_called_once_with("<file sentinel>")


@pytest.mark.usefixtures(*[f for f in FIXTURES if f != "mock_get_changes"])
class TestGetChanges:
    @staticmethod
    def test_early_return_for_no_changes(mocker):
        # GIVEN
        mock_repo = create_autospec(git.Repo)
        mock_diff_index = create_autospec(git.DiffIndex)
        mock_repo.index.diff.return_value = mock_diff_index
        mocker.patch("git.Repo", return_value=mock_repo)

        # WHEN
        comparison = check_changelog_clash._get_changes("<file sentinel>")

        # THEN
        assert comparison.has_changes is False
        assert comparison.local == []
        assert comparison.remote == []
        mock_repo.remotes.origin.fetch.assert_called_once_with()
        mock_repo.index.diff.assert_called_once_with("origin/main", "<file sentinel>")

    @staticmethod
    def test_reports_changes(mocker, tmp_path):
        # GIVEN
        local_file_contents = "<A sentinel 1>\n<A sentinel 2>"
        remote_file_contents = "<B sentinel 1>\n<B sentinel 2>"

        mock_file = tmp_path / "file.py"
        mock_file.write_text(local_file_contents)

        mock_repo = create_autospec(git.Repo)
        mock_diff = Mock()
        mock_diff.a_blob.data_stream.read.return_value = local_file_contents.encode(
            "utf-8"
        )
        mock_diff.b_blob.data_stream.read.return_value = remote_file_contents.encode(
            "utf-8"
        )
        mock_repo.index.diff.return_value = [mock_diff]
        mocker.patch("git.Repo", return_value=mock_repo)

        # WHEN
        comparison = check_changelog_clash._get_changes(mock_file)

        # THEN
        assert comparison.has_changes is True
        assert comparison.local == local_file_contents.splitlines()
        assert comparison.remote == remote_file_contents.splitlines()
        mock_repo.remotes.origin.fetch.assert_called_once_with()
        mock_repo.index.diff.assert_called_once_with("origin/main", mock_file)

    @staticmethod
    def test_raises_AssertionError_for_longer_diff_index(mocker):
        # GIVEN
        mock_repo = create_autospec(git.Repo)
        mock_diff = Mock()
        mock_repo.index.diff.return_value = [mock_diff, mock_diff]
        mocker.patch("git.Repo", return_value=mock_repo)

        # WHEN
        with pytest.raises(AssertionError):
            _ = check_changelog_clash._get_changes("<file sentinel>")

    @staticmethod
    def test_raises_AssertionError_for_mismatch_with_local_file(mocker, tmp_path):
        # GIVEN
        local_file_contents = "<A sentinel 1>\n<A sentinel 2>"
        remote_file_contents = "<B sentinel 1>\n<B sentinel 2>"

        mock_file = tmp_path / "file.py"
        mock_file.write_text("not local file contents")

        mock_repo = create_autospec(git.Repo)
        mock_diff = Mock()
        mock_diff.a_blob.data_stream.read.return_value = local_file_contents.encode(
            "utf-8"
        )
        mock_diff.b_blob.data_stream.read.return_value = remote_file_contents.encode(
            "utf-8"
        )
        mock_repo.index.diff.return_value = [mock_diff]
        mocker.patch("git.Repo", return_value=mock_repo)

        # WHEN
        with pytest.raises(AssertionError):
            _ = check_changelog_clash._get_changes(mock_file)


@pytest.mark.usefixtures(
    *[f for f in FIXTURES if f != "mock_parse_check_changelog_clash_args"]
)
class TestParseArgs:
    @staticmethod
    @pytest.mark.parametrize(
        "file_arg", [[], ["stub_file"], ["stub_file_1", "stub_file_2"]]
    )
    def test_arg_passing(file_arg, mocker):
        # GIVEN
        mocker.patch("sys.argv", ["stub", *file_arg])

        # WHEN
        args = check_changelog_clash._parse_args()

        # THEN
        assert args.files == file_arg


@pytest.mark.usefixtures(*FIXTURES)
class TestMain:
    @staticmethod
    def test_early_return_for_no_files(
        mock_parse_check_changelog_clash_args, mock_check_changelog_clash
    ):
        # GIVEN
        mock_parse_check_changelog_clash_args.return_value = Mock(files=[])

        # WHEN
        assert check_changelog_clash.main() == 0

        # THEN
        mock_check_changelog_clash.assert_not_called()

    @staticmethod
    def test_returns_1_for_changed_files(
        mock_parse_check_changelog_clash_args, mock_check_changelog_clash
    ):
        # GIVEN
        mock_parse_check_changelog_clash_args.return_value = Mock(
            files=["<file sentinel 1>"]
        )
        mock_check_changelog_clash.return_value = 1

        # WHEN
        assert check_changelog_clash.main() == 1

        # THEN
        mock_check_changelog_clash.assert_has_calls(
            [
                call(
                    "<file sentinel 1>",
                ),
            ]
        )
