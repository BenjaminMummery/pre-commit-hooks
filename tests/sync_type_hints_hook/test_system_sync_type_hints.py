# Copyright (c) 2025-2026 Benjamin Mummery
import os
import subprocess

from pytest_git import GitRepo

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "sync-type-hints"]

google_input = '''def greet(name, count):
    """Say hello.

    Args:
        name (str): Who to greet.
        count (int): How many times.

    Returns:
        bool: Whether greeting succeeded.
    """
    return True
'''

google_output = '''def greet(name: str, count: int) -> bool:
    """Say hello.

    Args:
        name (str): Who to greet.
        count (int): How many times.

    Returns:
        bool: Whether greeting succeeded.
    """
    return True
'''


class TestNoChanges:
    @staticmethod
    def test_no_files_changed(git_repo: GitRepo, cwd):
        with cwd(git_repo.workspace):
            process = subprocess.run(
                COMMAND,
                capture_output=True,
                text=True,
            )

        assert process.returncode == 0, process.stdout + process.stderr
        assert "Sync type hints with docstrings" in process.stdout
        assert "Passed" in process.stdout


class TestChanges:
    @staticmethod
    def test_adds_missing_annotations(git_repo: GitRepo, cwd):
        file = "file.py"
        f = git_repo.workspace / file
        f.write_text(google_input)
        git_repo.run(f"git add {file}")

        with cwd(git_repo.workspace):
            process = subprocess.run(
                COMMAND,
                capture_output=True,
                text=True,
            )

        assert process.returncode == 1, process.stdout + process.stderr
        with open(f) as handle:
            assert handle.read() == google_output
        assert "Failed" in process.stdout
