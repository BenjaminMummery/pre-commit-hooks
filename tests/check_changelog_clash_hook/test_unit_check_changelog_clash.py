# Copyright (c) 2023 Benjamin Mummery

from unittest.mock import Mock, call

import pytest

from src.check_changelog_clash_hook import check_changelog_clash

from ..conftest import CHECK_CHANGELOG_CLASH_FIXTURE_LIST as FIXTURES


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
