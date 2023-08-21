# Copyright (c) 2023 Benjamin Mummery

"""
Integration tests for format_setup_cfg.
"""

import difflib
from pathlib import Path
from typing import List

import pytest
from pytest import CaptureFixture

from src.format_setup_cfg_hook import format_setup_cfg
from tests.examples.setup_cfg_examples import SetupCfgExample, UnsortedEntries


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
    @pytest.mark.parametrize("example", [UnsortedEntries])
    def test_supported_files_already_formatted(
        example: SetupCfgExample, mocker, tmp_path: Path
    ):
        # GIVEN
        file = tmp_path / "setup.cfg"
        file.write_text(example.correctly_formatted)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        # WHEN
        ret = format_setup_cfg.main()

        # THEN
        assert ret == 0
        with open(file, "r") as f:
            content = f.read()
        assert content == example.correctly_formatted


class TestSortingDependencies:
    @staticmethod
    @pytest.mark.parametrize("in_place_argument", ["-i", "--in-place"])
    def test_overwrites_files_if_flagged(
        mocker,
        tmp_path: Path,
        in_place_argument: str,
    ):
        # GIVEN
        file = tmp_path / "setup.cfg"
        file.write_text(UnsortedEntries.incorrectly_formatted)
        mocker.patch("sys.argv", ["stub_name", str(file), in_place_argument])

        # WHEN
        _ = format_setup_cfg.main()

        # THEN
        with open(file, "r") as f:
            content = f.read()

        print("DIFF:")
        for line in difflib.ndiff(
            UnsortedEntries.correctly_formatted.splitlines(), content.splitlines()
        ):
            print(line)
        assert content == UnsortedEntries.correctly_formatted

    @staticmethod
    def test_does_not_modify_files_without_flag(mocker, tmp_path: Path):
        # GIVEN
        file = tmp_path / "setup.cfg"
        file.write_text(UnsortedEntries.incorrectly_formatted)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        # WHEN
        _ = format_setup_cfg.main()

        # THEN
        with open(file, "r") as f:
            content = f.read()
        assert content == UnsortedEntries.incorrectly_formatted

    @staticmethod
    def test_returns_1_for_unsorted_files(mocker, tmp_path: Path):
        # GIVEN
        file = tmp_path / "setup.cfg"
        file.write_text(UnsortedEntries.incorrectly_formatted)
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
        file.write_text(UnsortedEntries.incorrectly_formatted)
        mocker.patch("sys.argv", ["stub_name", str(file)])

        # WHEN
        _ = format_setup_cfg.main()

        # THEN
        stdout: List[str] = capsys.readouterr().out.splitlines()

        assert stdout[0].startswith("Unsorted entries in ")

        for actual_line, expected_line in zip(
            stdout[1:], UnsortedEntries.stdout.splitlines()
        ):
            assert actual_line == expected_line
