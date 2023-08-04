# Copyright (c) 2023 Benjamin Mummery

"""
Integration tests for format_setup_cfg.
"""

from pathlib import Path

from src.format_setup_cfg_hook import format_setup_cfg


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
    def test_no_supported_files_changed(mocker, tmp_path: Path):
        # GIVEN
        files = [tmp_path / file for file in ["hello.txt", ".gitignore", "test.yaml"]]
        for file in files:
            file.write_text(f"<file {file} content sentinel>")
        mocker.patch("sys.argv", ["stub_name", *files])

        # THEN
        ret = format_setup_cfg.main()

        # THEN
        assert ret == 0
        for file in files:
            with open(file, "r") as f:
                content = f.read()
            assert content == f"<file {file} content sentinel>"
