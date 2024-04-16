# Copyright (c) 2024 Benjamin Mummery

from unittest.mock import Mock, create_autospec, mock_open

from freezegun import freeze_time
from pytest_mock import MockerFixture

from .._shared.copyright_parsing import ParsedCopyrightString
from . import update_copyright
from .update_copyright import argparse


class TestUpdateCopyrightDates:
    @staticmethod
    def test_early_return_for_no_copyright_string(mocker: MockerFixture):
        # GIVEN
        mocker.patch("builtins.open", mock_open(read_data="<file content sentinel>"))
        mocker.patch(f"{update_copyright.__name__}.get_comment_markers")
        mocker.patch(
            f"{update_copyright.__name__}.parse_copyright_string", return_value=None
        )

        # WHEN
        ret = update_copyright._update_copyright_dates(Mock())

        # THEN
        assert ret == 0

    @staticmethod
    @freeze_time("9999-01-01")
    def test_early_return_for_up_to_date_copyright(mocker: MockerFixture):
        # GIVEN
        mocker.patch("builtins.open", mock_open(read_data="<file content sentinel>"))
        mocker.patch(f"{update_copyright.__name__}.get_comment_markers")
        mocker.patch(
            f"{update_copyright.__name__}.parse_copyright_string",
            return_value=Mock(end_year=9999),
        )

        # WHEN
        ret = update_copyright._update_copyright_dates(Mock())

        # THEN
        assert ret == 0

    @staticmethod
    @freeze_time("9999-01-01")
    def test_single_date_copyright_string(mocker: MockerFixture):
        # GIVEN
        mocker.patch("builtins.open", mock_open(read_data="<file content sentinel>"))
        mocker.patch(f"{update_copyright.__name__}.get_comment_markers")
        mocker.patch(
            f"{update_copyright.__name__}.parse_copyright_string",
            return_value=create_autospec(
                ParsedCopyrightString,
                start_year=9000,
                end_year=9000,
                string="<string sentinel 9000>",
            ),
        )

        # WHEN
        ret = update_copyright._update_copyright_dates(Mock())

        # THEN
        assert ret == 1

    @staticmethod
    @freeze_time("9999-01-01")
    def test_multiple_date_copyright_string(mocker: MockerFixture):
        # GIVEN
        mocker.patch("builtins.open", mock_open(read_data="<file content sentinel>"))
        mocker.patch(f"{update_copyright.__name__}.get_comment_markers")
        mocker.patch(
            f"{update_copyright.__name__}.parse_copyright_string",
            return_value=create_autospec(
                ParsedCopyrightString,
                start_year=9000,
                end_year=9990,
                string="<string sentinel 9000-9990>",
            ),
        )

        # WHEN
        ret = update_copyright._update_copyright_dates(Mock())

        # THEN
        assert ret == 1


class TestParseArgs:
    @staticmethod
    def test_parse_args(mocker: MockerFixture):
        # GIVEN
        mocked_argparse = create_autospec(argparse.ArgumentParser)
        mocker.patch(
            f"{update_copyright.__name__}.argparse.ArgumentParser",
            return_value=mocked_argparse,
        )
        mocker.patch(
            f"{update_copyright.__name__}.resolvers.resolve_files",
            return_value=["<file sentinel>"],
        )

        # WHEN
        ret = update_copyright._parse_args()

        # THEN
        assert ret.files == ["<file sentinel>"]


class TestMain:
    @staticmethod
    def test_no_files(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{update_copyright.__name__}._parse_args",
            return_value=create_autospec(argparse.Namespace, files=[]),
        )
        mocked_update_copyright_dates = mocker.patch(
            f"{update_copyright.__name__}._update_copyright_dates",
        )

        # WHEN
        ret = update_copyright.main()

        # THEN
        assert ret == 0
        mocked_update_copyright_dates.assert_not_called()

    @staticmethod
    def test_no_files_changed(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{update_copyright.__name__}._parse_args",
            return_value=create_autospec(argparse.Namespace, files=["<file sentinel>"]),
        )
        mocked_update_copyright_dates = mocker.patch(
            f"{update_copyright.__name__}._update_copyright_dates", return_value=0
        )

        # WHEN
        ret = update_copyright.main()

        # THEN
        assert ret == 0
        mocked_update_copyright_dates.assert_called_once_with("<file sentinel>")

    @staticmethod
    def test_files_changed(mocker: MockerFixture):
        # GIVEN
        mocker.patch(
            f"{update_copyright.__name__}._parse_args",
            return_value=create_autospec(argparse.Namespace, files=["<file sentinel>"]),
        )
        mocked_update_copyright_dates = mocker.patch(
            f"{update_copyright.__name__}._update_copyright_dates", return_value=1
        )

        # WHEN
        ret = update_copyright.main()

        # THEN
        assert ret == 1
        mocked_update_copyright_dates.assert_called_once_with("<file sentinel>")
