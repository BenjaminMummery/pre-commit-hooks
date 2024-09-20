# Copyright (c) 2023 - 2024 Benjamin Mummery

import os
import subprocess

import pytest
from pytest_git import GitRepo

from conftest import SortFileContentsGlobals, add_changed_files, assert_matching

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "sort-file-contents"]


class TestNoChanges:
    @staticmethod
    def test_no_files_changed(git_repo: GitRepo, cwd):
        """No files have been changed, nothing to check."""
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        assert process.returncode == 0, process.stdout + process.stderr
        assert "Sort gitignore sections" in process.stdout
        assert "Passed" in process.stdout

    @staticmethod
    def test_no_supported_files_changed(git_repo: GitRepo, cwd):
        """Files have been changed, but none of them are files that we support."""
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
        assert process.returncode == 0, process.stdout + process.stderr
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                content = f.read()
            assert content == f"<file {file} content sentinel>"
        assert "Sort gitignore sections" in process.stdout
        assert "Passed" in process.stdout

    @staticmethod
    @pytest.mark.parametrize(
        "file_contents", SortFileContentsGlobals.SORTED_FILE_CONTENTS
    )
    def test_all_changed_files_are_sorted(git_repo: GitRepo, cwd, file_contents: str):
        # GIVEN
        add_changed_files(file := ".gitignore", file_contents, git_repo)

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 0, process.stdout + process.stderr
        with open(git_repo.workspace / file, "r") as f:
            content = f.read()
        assert content == file_contents
        assert "Sort gitignore sections" in process.stdout
        assert "Passed" in process.stdout

    @staticmethod
    def test_empty_file(git_repo: GitRepo, cwd):
        # GIVEN
        add_changed_files(file := ".gitignore", "", git_repo)

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 0, process.stdout + process.stderr
        with open(git_repo.workspace / file, "r") as f:
            content = f.read()
        assert content == ""
        assert "Sort gitignore sections" in process.stdout
        assert "Passed" in process.stdout


class TestSorting:
    @staticmethod
    @pytest.mark.parametrize(
        "unsorted, sorted, description", SortFileContentsGlobals.UNSORTED_FILE_CONTENTS
    )
    def test_default_file_sorting(
        cwd,
        git_repo: GitRepo,
        unsorted: str,
        sorted: str,
        description: str,
    ):
        # GIVEN
        add_changed_files(filename := ".gitignore", unsorted, git_repo)

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 1, process.stdout + process.stderr
        with open(git_repo.workspace / filename, "r") as f:
            content = f.read()
        assert_matching(
            "output file contents",
            "expected file contents",
            content,
            sorted,
            message=f"Failed to sort file with {description}.",
        )
        assert f"Sorting file '{filename}'" in process.stdout
