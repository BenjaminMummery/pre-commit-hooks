# Copyright (c) 2023 Benjamin Mummery

import os
import subprocess

import pytest
from pytest_git import GitRepo

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "update-copyright"]


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
        assert "Add copyright string to source files" in process.stdout
        assert "Passed" in process.stdout
