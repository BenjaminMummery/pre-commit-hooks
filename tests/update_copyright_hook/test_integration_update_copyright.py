# Copyright (c) 2023 Benjamin Mummery

import pytest
from freezegun import freeze_time
from pytest import CaptureFixture
from pytest_git import GitRepo
from pytest_mock import MockerFixture

from src.update_copyright_hook import update_copyright
from tests.conftest import (
    CopyrightGlobals,
    SupportedLanguage,
    add_changed_files,
    assert_matching,
)


@pytest.mark.usefixtures("git_repo")
class TestNoChanges:
    @staticmethod
    def test_no_files_changed(
        capsys: CaptureFixture,
        mocker: MockerFixture,
    ):
        # GIVEN
        mocker.patch("sys.argv", ["stub_name"])

        # WHEN
        assert update_copyright.main() == 0

        # THEN
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @freeze_time("1312-01-01")
    @pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize(
        "copyright_string",
        [s.format(end_year="1312") for s in CopyrightGlobals.VALID_COPYRIGHT_STRINGS],
    )
    def test_all_changed_files_have_current_copyright(
        capsys: CaptureFixture,
        copyright_string: str,
        cwd,
        git_repo: GitRepo,
        language: SupportedLanguage,
        mocker: MockerFixture,
    ):
        # GIVEN
        add_changed_files(
            file := "hello" + language.extension,
            file_content := (
                language.comment_format.format(content=copyright_string)
                + "\n\n<file content sentinel>"
            ),
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert update_copyright.main() == 0

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content", "expected content", output_content, file_content
        )
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")


@pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
class TestChanges:
    @staticmethod
    @pytest.mark.parametrize(
        "input_copyright_string, expected_copyright_string",
        [
            ("Copyright 1066 NAME", "Copyright 1066 - 1312 NAME"),
            ("Copyright (c) 1066 NAME", "Copyright (c) 1066 - 1312 NAME"),
            ("(c) 1066 NAME", "(c) 1066 - 1312 NAME"),
        ],
    )
    @freeze_time("1312-01-01")
    def test_updates_single_date_copyrights(
        capsys: CaptureFixture,
        cwd,
        expected_copyright_string: str,
        git_repo: GitRepo,
        input_copyright_string: str,
        language: SupportedLanguage,
        mocker: MockerFixture,
    ):
        # GIVEN
        add_changed_files(
            file := "hello" + language.extension,
            language.comment_format.format(content=input_copyright_string)
            + "\n\n<file content sentinel>",
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert update_copyright.main() == 1

        # THEN
        # Construct expected outputs
        new_copyright_string = language.comment_format.format(
            content=expected_copyright_string
        )
        expected_content = f"{new_copyright_string}\n\n<file content sentinel>"
        expected_stdout = (
            f"Fixing file `{file}`:\n"
            f"\033[91m  - {language.comment_format.format(content=input_copyright_string)}\033[0m\n"  # noqa: E501
            f"\033[92m  + {new_copyright_string}\033[0m\n"
        )

        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content", "expected content", output_content, expected_content
        )
        assert_matching(
            "captured stdout", "expected stdout", captured.out, expected_stdout
        )
        assert_matching("captured stderr", "expected stderr", captured.err, "")
