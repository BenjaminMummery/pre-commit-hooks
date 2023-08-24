# Copyright (c) 2023 Benjamin Mummery

"""
System tests for the format-setup-cfg hook.

These tests duplicate the integration test cases, but enact them in a full end-to-end
context.
"""

import os
import subprocess

import pytest

from tests.examples.setup_cfg_examples import SetupCfgExample, all_examples

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
    @pytest.mark.parametrize("example", all_examples)
    def test_supported_files_already_formatted(example: SetupCfgExample, git_repo, cwd):
        # GIVEN
        file = git_repo.workspace / "setup.cfg"
        file.write_text(example.correctly_formatted)
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        # THEN
        assert process.returncode == 0
        with open(git_repo.workspace / file, "r") as f:
            content = f.read()
        assert content == example.correctly_formatted


@pytest.mark.parametrize("example", all_examples)
class TestSortingDependencies:
    @staticmethod
    @pytest.mark.xfail(reason="Passing args to hooks in try-repo is not supported.")
    def test_overwrites_files_if_flagged(example: SetupCfgExample, git_repo, cwd):
        assert False

    @staticmethod
    def test_does_not_modify_files_without_flag(
        example: SetupCfgExample, git_repo, cwd
    ):
        # GIVEN
        file = git_repo.workspace / "setup.cfg"
        file.write_text(example.incorrectly_formatted)
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            subprocess.run(COMMAND)

        # THEN
        with open(file, "r") as f:
            content = f.read()
        assert content == example.incorrectly_formatted

    @staticmethod
    def test_fails_for_unsorted_files(example: SetupCfgExample, git_repo, cwd):
        # GIVEN
        file = git_repo.workspace / "setup.cfg"
        file.write_text(example.incorrectly_formatted)
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(COMMAND)

        # THEN
        assert process.returncode == 1

    @staticmethod
    def test_tells_user_what_is_unsorted(example: SetupCfgExample, git_repo, cwd):
        # GIVEN
        file = git_repo.workspace / "setup.cfg"
        file.write_text(example.incorrectly_formatted)
        git_repo.run(f"git add {file}")

        # WHEN
        with cwd(git_repo.workspace):
            process: subprocess.CompletedProcess = subprocess.run(
                COMMAND, capture_output=True
            )

        # THEN
        print(process.stdout.decode())
        assert (
            "Unsorted entries in setup.cfg:\n" + example.stdout
        ) in process.stdout.decode()
