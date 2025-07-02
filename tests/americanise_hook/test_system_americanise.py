# Copyright (c) 2025 Benjamin Mummery

import os
import subprocess

from pytest_git import GitRepo

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "americanise"]


class TestNoChanges:
    @staticmethod
    def test_no_files_changed(git_repo: GitRepo, cwd):
        """No files have been changed, nothing to check."""
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        assert process.returncode == 0, process.stdout + process.stderr
        assert "Correct non-US spellings" in process.stdout
        assert "Passed" in process.stdout

    @staticmethod
    def test_changed_files_dont_have_misspellings(git_repo: GitRepo, cwd):
        """Files have been changed, but none of them are in languages we support."""
        # GIVEN

        f = git_repo.workspace / "file.py"
        f.write_text("<file content sentinel>")
        git_repo.run("git add file.py")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True, text=True
            )

        # THEN
        assert process.returncode == 0, process.stdout + process.stderr
        with open(f, "r") as file:
            content = file.read()
        assert content == "<file content sentinel>"
        assert "Correct non-US spellings" in process.stdout
        assert "Passed" in process.stdout, process.stdout

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
        assert process.returncode == 0, process.stdout + process.stderr
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                content = f.read()
            assert content == f"<file {file} content sentinel>"
        assert "Correct non-US spellings" in process.stdout
        assert "Passed" in process.stdout, process.stdout
