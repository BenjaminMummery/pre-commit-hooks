# Copyright (c) 2023 Benjamin Mummery

"""
Integration tests for format_setup_cfg.
"""

from pathlib import Path

from pytest import CaptureFixture

from src.format_setup_cfg_hook import format_setup_cfg
from tests.conftest import (
    CORRECTLY_FORMATTED_SETUP_CFG_CONTENTS,
    EXPECTED_UNSORTED_REPORT,
    UNSORTED_REQUIRED_SETUP_CFG_CONTENTS,
)


class TestNoChanges:
    @staticmethod
    def test_no_files_changed(mocker):
        # GIVEN
        mocker.patch("sys.argv", ["stub_name"])

        # WHEN
        ret = format_setup_cfg.main()

        # THEN
        assert ret == 0

    @staticmethod
    def test_supported_files_already_formatted(mocker, tmp_path: Path):
        # GIVEN
        file = tmp_path / "setup.cfg"
        file.write_text(CORRECTLY_FORMATTED_SETUP_CFG_CONTENTS)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        # WHEN
        ret = format_setup_cfg.main()

        # THEN
        assert ret == 0
        with open(file, "r") as f:
            content = f.read()
        assert content == CORRECTLY_FORMATTED_SETUP_CFG_CONTENTS


class TestSortingDependencies:
    # @staticmethod
    # def test_overwrites_files(mocker, tmp_path: Path):
    #     # GIVEN
    #     file = tmp_path / "setup.cfg"
    #     file.write_text(UNSORTED_REQUIRED_SETUP_CFG_CONTENTS)
    #     mocker.patch("sys.argv", ["stub_name", file])

    #     # WHEN
    #     _ = format_setup_cfg.main()

    #     # THEN
    #     with open(file, "r") as f:
    #         content = f.read()
    #     assert content == CORRECTLY_FORMATTED_SETUP_CFG_CONTENTS

    @staticmethod
    def test_returns_1_for_unsorted_files(mocker, tmp_path: Path):
        # GIVEN
        file = tmp_path / "setup.cfg"
        file.write_text(UNSORTED_REQUIRED_SETUP_CFG_CONTENTS)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        # WHEN
        ret = format_setup_cfg.main()

        # THEN
        assert ret == 1

    @staticmethod
    def test_tells_user_what_is_unsorted(
        mocker, tmp_path: Path, capsys: CaptureFixture
    ):
        # GIVEN
        file = tmp_path / "setup.cfg"
        file.write_text(UNSORTED_REQUIRED_SETUP_CFG_CONTENTS)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        # WHEN
        _ = format_setup_cfg.main()

        # THEN
        stdout: str = capsys.readouterr().out
        assert stdout == (f"Unsorted entries in {file}:\n" + EXPECTED_UNSORTED_REPORT)
