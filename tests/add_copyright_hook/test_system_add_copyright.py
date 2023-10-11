# Copyright (c) 2022-2023 Benjamin Mummery

import datetime
import os
import subprocess

import pytest
from pytest_git import GitRepo

from tests.conftest import (
    SUPPORTED_LANGUAGES,
    VALID_COPYRIGHT_STRINGS,
    SupportedLanguage,
    assert_matching,
)

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "add-copyright"]
THIS_YEAR = datetime.date.today().year


@pytest.mark.slow
class TestNoChanges:
    @staticmethod
    def test_no_files_changed(git_repo: GitRepo, cwd):
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        assert process.returncode == 0
        assert "Add copyright string to source files" in process.stdout
        assert "Passed" in process.stdout

    @staticmethod
    def test_no_supported_files_changed(git_repo: GitRepo, cwd):
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
        assert "Add copyright string to source files" in process.stdout
        assert "Passed" in process.stdout

    @staticmethod
    @pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
    @pytest.mark.parametrize("copyright_string", VALID_COPYRIGHT_STRINGS)
    def test_all_changed_files_have_copyright(
        git_repo: GitRepo,
        cwd,
        language: SupportedLanguage,
        copyright_string: str,
    ):
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
        assert "Add copyright string to source files" in process.stdout
        assert "Passed" in process.stdout


# Check multiple usernames to confirm they get read in correctly.
@pytest.mark.parametrize(
    "git_username", ["<git config username sentinel>", "Taylor Swift"]
)
@pytest.mark.slow
class TestDefaultBehaviour:
    class TestEmptyFiles:
        @staticmethod
        def test_adding_copyright_to_empty_files(
            cwd,
            git_repo: GitRepo,
            git_username: str,
        ):
            # GIVEN
            git_repo.run(f"git config user.name '{git_username}'")
            for language in SUPPORTED_LANGUAGES:
                file = "hello" + language.extension
                (git_repo.workspace / file).write_text("")
                git_repo.run(f"git add {file}")

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1

            for language in SUPPORTED_LANGUAGES:
                file = "hello" + language.extension
                copyright_string = language.comment_format.format(
                    content=f"Copyright (c) {THIS_YEAR} {git_username}"
                )
                expected_content = f"{copyright_string}\n"
                expected_stdout = (
                    f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
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

    class TestFileContentHandling:
        @staticmethod
        def test_adding_copyright_to_files_with_content(
            cwd,
            git_repo: GitRepo,
            git_username: str,
        ):
            # GIVEN
            git_repo.run(f"git config user.name '{git_username}'")
            for language in SUPPORTED_LANGUAGES:
                file = "hello" + language.extension
                (git_repo.workspace / file).write_text(
                    f"<file {file} content sentinel>"
                )
                git_repo.run(f"git add {file}")

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1
            for language in SUPPORTED_LANGUAGES:
                file = "hello" + language.extension
                copyright_string = language.comment_format.format(
                    content=f"Copyright (c) {THIS_YEAR} {git_username}"
                )
                expected_content = (
                    copyright_string + f"\n\n<file {file} content sentinel>\n"
                )
                expected_stdout = (
                    f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
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
        def test_handles_shebang(
            cwd,
            git_repo: GitRepo,
            git_username: str,
        ):
            # GIVEN
            git_repo.run(f"git config user.name '{git_username}'")
            for language in SUPPORTED_LANGUAGES:
                file = "hello" + language.extension
                (git_repo.workspace / file).write_text(
                    f"#!/usr/bin/env python3\n<file {file} content sentinel>"
                )
                git_repo.run(f"git add {file}")

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1
            for language in SUPPORTED_LANGUAGES:
                file = "hello" + language.extension
                copyright_string = language.comment_format.format(
                    content=f"Copyright (c) {THIS_YEAR} {git_username}"
                )
                expected_content = (
                    "#!/usr/bin/env python3\n"
                    "\n"
                    f"{copyright_string}\n"
                    "\n"
                    f"<file {file} content sentinel>\n"
                )
                expected_stdout = (
                    f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
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


class TestCustomBehaviour:
    class TestConfigFiles:
        @staticmethod
        @pytest.mark.parametrize(
            "config_file, config_file_content",
            [
                (
                    "pyproject.toml",
                    '[tool.add_copyright]\nname="<config file username sentinel>"\n',
                )
            ],
        )
        def test_custom_name_option_overrules_git_username(
            cwd,
            config_file: str,
            config_file_content: str,
            git_repo: GitRepo,
        ):
            # GIVEN
            git_repo.run("git config user.name '<git config username sentinel>'")
            for language in SUPPORTED_LANGUAGES:
                file = "hello" + language.extension
                (git_repo.workspace / file).write_text("")
                git_repo.run(f"git add {file}")

            (git_repo.workspace / config_file).write_text(config_file_content)

            # WHEN
            with cwd(git_repo.workspace):
                process: subprocess.CompletedProcess = subprocess.run(
                    COMMAND, capture_output=True, text=True
                )

            # THEN
            assert process.returncode == 1
            for language in SUPPORTED_LANGUAGES:
                file = "hello" + language.extension
                copyright_string = language.comment_format.format(
                    content=f"Copyright (c) {THIS_YEAR} <config file username sentinel>"
                )
                expected_content = f"{copyright_string}\n"
                expected_stdout = (
                    f"Fixing file `{file}` - added line(s):\n{copyright_string}\n"
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
