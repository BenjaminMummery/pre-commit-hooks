# Copyright (c) 2023 Benjamin Mummery

import os
import subprocess
from typing import List

import pytest
from pytest_git import GitRepo

from tests.examples.invalid_rst_python import expected_stdout as bad_rst_expected_stdout

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "check-docstrings-parse-as-rst"]


def mock_file_content(git_repo: GitRepo, files: List[str], input_content_filename: str):
    with open(f"tests/examples/{input_content_filename}") as f:
        input_content = f.read()
    for file in files:
        f = git_repo.workspace / file
        f.write_text(input_content)
        git_repo.run(f"git add {file}")
    return input_content


@pytest.mark.slow
class TestNoChanges:
    @staticmethod
    def test_no_files_changed(git_repo: GitRepo, cwd):
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        assert process.returncode == 0

    @staticmethod
    def test_no_supported_files_changed(git_repo: GitRepo, cwd):
        # GIVEN
        files = ["hello.txt", ".gitignore", "test.yaml"]
        input_content = mock_file_content(git_repo, files, "invalid_rst_python.py")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        # THEN
        assert process.returncode == 0
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                content = f.read()
            print(content)
            assert content == input_content

    @staticmethod
    def test_no_changed_files_have_docstrings(git_repo: GitRepo, cwd):
        # GIVEN
        files = ["hello.py", ".hello.py", "_hello.py"]
        input_content = mock_file_content(git_repo, files, "no_docstrings.py")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        # THEN
        assert process.returncode == 0
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                output_content = f.read()
            assert output_content == input_content.format(file=file)

    @staticmethod
    def test_all_docstrings_are_correct_rst(git_repo: GitRepo, cwd):
        # GIVEN
        files = ["hello.py", ".hello.py", "_hello.py"]
        input_content = mock_file_content(git_repo, files, "valid_rst_python.py")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        # THEN
        assert process.returncode == 0
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                output_content = f.read()
            assert output_content == input_content.format(file=file)


@pytest.mark.slow
class TestBadRST:
    @staticmethod
    def test_fails_for_bad_docstrings(git_repo: GitRepo, cwd):
        # GIVEN
        files = ["hello.py"]
        mock_file_content(git_repo, files, "invalid_rst_python.py")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 1
        assert bad_rst_expected_stdout in process.stdout
