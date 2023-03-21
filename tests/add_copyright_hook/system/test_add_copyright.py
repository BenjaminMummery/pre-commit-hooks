# Copyright (c) 2023 Benjamin Mummery

import datetime
import os
import subprocess

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "add-copyright"]


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
    def test_all_changed_files_have_copyright(git_repo, cwd):
        files = ["hello.py", ".hello.py", "_hello.py"]
        for file in files:
            f = git_repo.workspace / file
            f.write_text(f"# Copyright 1234 Heimdal\n\n<file {file} content sentinel>")
            git_repo.run(f"git add {file}")

        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        assert process.returncode == 0
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                content = f.read()
            assert (
                content == f"# Copyright 1234 Heimdal\n\n<file {file} content sentinel>"
            )


class TestChanges:
    @staticmethod
    def test_inferred_name_date(git_repo, cwd):
        # Check the current year
        this_year = datetime.date.today().year

        # Create changed files
        files = [git_repo.workspace / file for file in ["hello.py"]]
        for file in files:
            f = git_repo.workspace / file
            f.write_text(f"<file {file} content sentinel>")
            git_repo.run(f"git add {file}")

        # Set git username
        username = "<username sentinel>"
        git_repo.run(f"git config user.name '{username}'")

        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        assert process.returncode == 1
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                content = f.read()
            assert (
                content
                == f"# Copyright (c) {this_year} <username sentinel>\n\n<file {file} content sentinel>"  # noqa: E501
            )

    @staticmethod
    def test_autodetect_config(git_repo, cwd):
        # Create changed files
        files = [git_repo.workspace / file for file in ["hello.py"]]
        for file in files:
            f = git_repo.workspace / file
            f.write_text(f"<file {file} content sentinel>")
            git_repo.run(f"git add {file}")

        # Create config file
        c = git_repo.workspace / ".add-copyright-hook-config.yaml"
        c.write_text(
            "name: <name sentinel>\n"
            "year: '0000'\n"
            "format: '# Belongs to {name} as of {year}.'"
        )

        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        assert process.returncode == 1
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                content = f.read()
            assert (
                content
                == f"# Belongs to <name sentinel> as of 0000.\n\n<file {file} content sentinel>"  # noqa: E501
            )
