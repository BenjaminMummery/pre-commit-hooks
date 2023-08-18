# Copyright (c) 2023 Benjamin Mummery

"""
System tests for the format-setup-cfg hook.

These tests duplicate the integration test cases, but enact them in a full end-to-end
context.
"""

import os
import subprocess

import pytest

from tests.conftest import (
    CORRECTLY_FORMATTED_SETUP_CFG_CONTENTS,
    EXPECTED_UNSORTED_REPORT,
    UNSORTED_REQUIRED_SETUP_CFG_CONTENTS,
)

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "format-setup-cfg"]


@pytest.mark.slow
class TestNoChanges:
    @staticmethod
    def test_no_files_changed(git_repo, cwd):
        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        # THEN
        assert process.returncode == 0

    @staticmethod
    def test_no_supported_files_changed(git_repo, cwd):
        # GIVEN
        files = ["hello.txt", ".gitignore", "test.yaml"]
        for file in files:
            f = git_repo.workspace / file
            f.write_text(f"<file {file} content sentinel>")
            git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        # THEN
        assert process.returncode == 0
        for file in files:
            with open(git_repo.workspace / file, "r") as f:
                content = f.read()
            assert content == f"<file {file} content sentinel>"

    @staticmethod
    def test_supported_files_already_formatted(git_repo, cwd):
        # GIVEN
        file = git_repo.workspace / "setup.cfg"
        file.write_text(CORRECTLY_FORMATTED_SETUP_CFG_CONTENTS)
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        # THEN
        assert process.returncode == 0
        with open(git_repo.workspace / file, "r") as f:
            content = f.read()
        assert content == CORRECTLY_FORMATTED_SETUP_CFG_CONTENTS


class TestSortingDependencies:
    @staticmethod
    @pytest.mark.xfail(reason="Passing args to hooks in try-repo is not supported.")
    def test_overwrites_files_if_interactive(git_repo, cwd):
        assert False

    @staticmethod
    def test_does_not_modify_files_without_flag(git_repo, cwd):
        # GIVEN
        file = git_repo.workspace / "setup.cfg"
        file.write_text(UNSORTED_REQUIRED_SETUP_CFG_CONTENTS)
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            subprocess.run(COMMAND)

        # THEN
        with open(file, "r") as f:
            content = f.read()
        assert content == UNSORTED_REQUIRED_SETUP_CFG_CONTENTS

    @staticmethod
    def test_fails_for_unsorted_files(git_repo, cwd):
        # GIVEN
        file = git_repo.workspace / "setup.cfg"
        file.write_text(UNSORTED_REQUIRED_SETUP_CFG_CONTENTS)
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        # THEN
        assert process.returncode == 1

    @staticmethod
    def test_tells_user_what_is_unsorted(git_repo, cwd):
        # GIVEN
        file = git_repo.workspace / "setup.cfg"
        file.write_text(UNSORTED_REQUIRED_SETUP_CFG_CONTENTS)
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True
            )

        # THEN
        print(process.stdout.decode())
        assert (
            "Unsorted entries in setup.cfg:\n" + EXPECTED_UNSORTED_REPORT
        ) in process.stdout.decode()