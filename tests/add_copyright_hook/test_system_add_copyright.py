# Copyright (c) 2022-2023 Benjamin Mummery

import datetime
import os
import subprocess

import pytest
from pytest_git import GitRepo

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
    @pytest.mark.parametrize(
        "extension, comment_format",
        [
            (".py", "# {content}"),
            (".md", "<!--- {content} -->"),
            (".cpp", "// {content}"),
            (".cs", "/* {content} */"),
            (".pl", "# {content}"),
        ],
    )
    @pytest.mark.parametrize(
        "copyright_string",
        [
            "Copyright 1111 NAME",
            "Copyright (c) 1111 NAME",
            "(c) 1111 NAME",
        ],
    )
    def test_all_changed_files_have_copyright(
        git_repo: GitRepo,
        cwd,
        extension: str,
        comment_format: str,
        copyright_string: str,
    ):
        # GIVEN
        file = "hello" + extension
        file_content = (
            comment_format.format(content=copyright_string)
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
        assert output_content == file_content
        assert "Add copyright string to source files" in process.stdout
        assert "Passed" in process.stdout


# Check for every language we support
@pytest.mark.parametrize(
    "extension, comment_format",
    [
        (".py", "# {content}"),
        (".md", "<!--- {content} -->"),
        (".cpp", "// {content}"),
        (".cs", "/* {content} */"),
        (".pl", "# {content}"),
    ],
)
# Check multiple usernames to confirm they get read in correctly.
@pytest.mark.parametrize(
    "git_username", ["<git config username sentinel>", "Taylor Swift"]
)
@pytest.mark.slow
class TestDefaultBehaviour:
    @staticmethod
    def test_adding_copyright_to_empty_files(
        comment_format: str,
        cwd,
        git_repo: GitRepo,
        git_username: str,
        extension: str,
    ):
        # GIVEN
        file = "hello" + extension
        (git_repo.workspace / file).write_text("")
        git_repo.run(f"git config user.name '{git_username}'")
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 1
        copyright_string = comment_format.format(
            content=f"Copyright (c) {THIS_YEAR} {git_username}"
        )
        expected_content = f"{copyright_string}\n"
        expected_stdout = (
            f"Fixing file `hello{extension}` - added line(s):\n{copyright_string}\n"
        )
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()

        assert output_content == expected_content
        assert expected_stdout in process.stdout

    @staticmethod
    def test_adding_copyright_to_files_with_content(
        comment_format: str,
        cwd,
        git_repo: GitRepo,
        git_username: str,
        extension: str,
    ):
        # GIVEN
        file = "hello" + extension
        (git_repo.workspace / file).write_text(f"<file {file} content sentinel>")
        git_repo.run(f"git config user.name '{git_username}'")
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 1
        copyright_string = comment_format.format(
            content=f"Copyright (c) {THIS_YEAR} {git_username}"
        )
        expected_content = copyright_string + f"\n\n<file {file} content sentinel>\n"
        expected_stdout = (
            f"Fixing file `hello{extension}` - added line(s):\n{copyright_string}\n"
        )
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()

        assert output_content == expected_content
        assert expected_stdout in process.stdout
