# Copyright (c) 2023 Benjamin Mummery

import os
import subprocess

import pytest

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "check-docstrings-parse-as-rst"]


@pytest.mark.slow
class TestNoChanges:
    @staticmethod
    def test_no_files_changed(git_repo, cwd):
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        assert process.returncode == 0

    @staticmethod
    def test_no_supported_files_changed(git_repo, cwd):
        files = ["hello.txt", ".gitignore", "test.yaml"]
        for file in files:
            f = git_repo.workspace / file
            f.write_text(f"<file {file} content sentinel>")
            git_repo.run(f"git add {file}")

        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        assert process.returncode == 0
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                content = f.read()
            assert content == f"<file {file} content sentinel>"

    @staticmethod
    def test_no_changed_files_have_docstrings(git_repo, cwd):
        # GIVEN
        # create tracked but uncommitted files
        files = ["hello.py", ".hello.py", "_hello.py"]
        input_content = "# <file {file} content sentinel>\ndef main():\n    pass"
        for file in files:
            f = git_repo.workspace / file
            f.write_text(input_content.format(file=file))
            git_repo.run(f"git add {file}")

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
    def test_all_docstrings_are_correct_rst(git_repo, cwd):
        # GIVEN
        files = ["hello.py", ".hello.py", "_hello.py"]
        input_content = (
            "# <file {file} content sentinel>\n"
            "def main():\n"
            '    """Valid rst."""'
            "    pass"
        )
        for file in files:
            f = git_repo.workspace / file
            f.write_text(input_content.format(file=file))
            git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        # THEN
        assert process.returncode == 0
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                output_content = f.read()
            assert output_content == input_content.format(file=file)
