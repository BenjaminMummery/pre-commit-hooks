# Copyright (c) 2023 Benjamin Mummery

import datetime
import os
import subprocess

import pytest
from pytest_git import GitRepo

from tests.conftest import (
    CopyrightGlobals,
    SupportedLanguage,
    add_changed_files,
    assert_matching,
)

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "update-copyright"]
THIS_YEAR = datetime.date.today().year


@pytest.mark.slow
class TestNoChanges:
    @staticmethod
    def test_no_files_changed(git_repo: GitRepo, cwd):
        """No files have been changed, nothing to check."""
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        assert process.returncode == 0, process.stdout
        assert (
            "Update dates on copyright strings in source files" in process.stdout
        ), process.stdout
        assert "Passed" in process.stdout

    @staticmethod
    def test_no_supported_files_changed(git_repo: GitRepo, cwd):
        """Files have been changed, but none of them are in languages we support."""
        # GIVEN
        files = ["hello.txt", ".gitignore", "test.yaml"]
        for file in files:
            f = git_repo.workspace / file
            f.write_text(f"<file {file} content sentinel>")
            git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 0
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                content = f.read()
            assert content == f"<file {file} content sentinel>"
        assert (
            "Update dates on copyright strings in source files" in process.stdout
        ), process.stdout
        assert "Passed" in process.stdout, process.stdout

    @staticmethod
    @pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize(
        "copyright_string",
        [
            s.format(end_year=THIS_YEAR)
            for s in CopyrightGlobals.VALID_COPYRIGHT_STRINGS
        ],
    )
    def test_all_changed_files_have_current_copyright(
        git_repo: GitRepo,
        cwd,
        language: SupportedLanguage,
        copyright_string: str,
    ):
        """Files have been changed, but all have up-to-date copyright strings."""
        # GIVEN
        file = "hello" + language.extension
        file_content = (
            language.comment_format.format(content=copyright_string)
            + "\n\n<file content sentinel>"
        )
        (git_repo.workspace / file).write_text(file_content)
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 0
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        assert_matching(
            "output content", "expected content", output_content, file_content
        )
        assert "Update dates on copyright strings in source files" in process.stdout
        assert "Passed" in process.stdout

    @staticmethod
    @pytest.mark.parametrize("language", CopyrightGlobals.SUPPORTED_LANGUAGES)
    def test_no_changed_files_have_copyright(
        git_repo: GitRepo,
        cwd,
        language: SupportedLanguage,
    ):
        """Files have been changed, but all have up-to-date copyright strings."""
        # GIVEN
        file = "hello" + language.extension
        file_content = "<file content sentinel>\n"
        (git_repo.workspace / file).write_text(file_content)
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 0
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        assert_matching(
            "output content", "expected content", output_content, file_content
        )
        assert "Update dates on copyright strings in source files" in process.stdout
        assert "Passed" in process.stdout


@pytest.mark.slow
class TestChanges:
    @staticmethod
    @pytest.mark.parametrize(
        "input_copyright_string, expected_copyright_string",
        [
            ("Copyright 1066 NAME", "Copyright 1066 - {year} NAME"),
            ("Copyright (c) 1066 NAME", "Copyright (c) 1066 - {year} NAME"),
            ("(c) 1066 NAME", "(c) 1066 - {year} NAME"),
        ],
    )
    def test_updates_single_date_copyrights(
        cwd,
        expected_copyright_string: str,
        git_repo: GitRepo,
        input_copyright_string: str,
    ):
        # GIVEN
        add_changed_files(
            [f"hello{lang.extension}" for lang in CopyrightGlobals.SUPPORTED_LANGUAGES],
            [
                lang.comment_format.format(content=input_copyright_string)
                + "\n\n<file content sentinel>\n"
                for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
            ],
            git_repo,
        )

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 1
        for language in CopyrightGlobals.SUPPORTED_LANGUAGES:
            file = "hello" + language.extension
            copyright_string = language.comment_format.format(
                content=expected_copyright_string.format(year=THIS_YEAR)
            )
            expected_content = copyright_string + "\n\n<file content sentinel>\n"
            expected_stdout = (
                f"Fixing file `{file}`:\n"
                f"\033[91m  - {language.comment_format.format(content = input_copyright_string)}\033[0m\n"  # noqa: E501
                f"\033[92m  + {copyright_string}\033[0m\n"
            )
            with open(git_repo.workspace / file, "r") as f:
                output_content = f.read()

            assert_matching(
                "output content",
                "expected content",
                output_content,
                expected_content,
            )
            assert expected_stdout in process.stdout

    @staticmethod
    @pytest.mark.parametrize(
        "input_copyright_string, expected_copyright_string",
        [
            ("Copyright 1066 - 1088 NAME", "Copyright 1066 - {year} NAME"),
            ("Copyright (c) 1066-1088 NAME", "Copyright (c) 1066-{year} NAME"),
        ],
    )
    def test_updates_multiple_date_copyrights(
        cwd,
        expected_copyright_string: str,
        git_repo: GitRepo,
        input_copyright_string: str,
    ):
        # GIVEN
        add_changed_files(
            [f"hello{lang.extension}" for lang in CopyrightGlobals.SUPPORTED_LANGUAGES],
            [
                lang.comment_format.format(content=input_copyright_string)
                + "\n\n<file content sentinel>\n"
                for lang in CopyrightGlobals.SUPPORTED_LANGUAGES
            ],
            git_repo,
        )

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 1
        for language in CopyrightGlobals.SUPPORTED_LANGUAGES:
            file = "hello" + language.extension
            copyright_string = language.comment_format.format(
                content=expected_copyright_string.format(year=THIS_YEAR)
            )
            expected_content = copyright_string + "\n\n<file content sentinel>\n"
            expected_stdout = (
                f"Fixing file `{file}`:\n"
                f"\033[91m  - {language.comment_format.format(content = input_copyright_string)}\033[0m\n"  # noqa: E501
                f"\033[92m  + {copyright_string}\033[0m\n"
            )
            with open(git_repo.workspace / file, "r") as f:
                output_content = f.read()

            assert_matching(
                "output content",
                "expected content",
                output_content,
                expected_content,
            )
            assert expected_stdout in process.stdout
