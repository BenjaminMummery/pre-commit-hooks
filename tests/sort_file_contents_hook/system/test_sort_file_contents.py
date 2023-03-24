# Copyright (c) 2023 Benjamin Mummery

import os
import subprocess

import pytest

COMMAND = ["pre-commit", "try-repo", f"{os.getcwd()}", "sort-file-contents"]


@pytest.mark.slow
@pytest.mark.parametrize(
    "unsorted, sorted, description",
    [
        (
            "beta\n" "delta\n" "gamma\n" "alpha\n",
            "alpha\n" "beta\n" "delta\n" "gamma\n",
            "no sections",
        ),
        (
            "beta\n" "delta\n" "\n" "gamma\n" "alpha\n",
            "beta\n" "delta\n" "\n" "alpha\n" "gamma\n",
            "sections",
        ),
        (
            "# zulu\n" "beta\n" "delta\n" "gamma\n" "alpha\n",
            "# zulu\n" "alpha\n" "beta\n" "delta\n" "gamma\n",
            "leading comment, no sections",
        ),
        (
            "# zulu\n" "beta\n" "delta\n" "\n" "# epsilon\n" "gamma\n" "alpha\n",
            "# zulu\n" "beta\n" "delta\n" "\n" "# epsilon\n" "alpha\n" "gamma\n",
            "multiple sections with leading comment",
        ),
        (
            "beta\n" "# zulu\n" "delta\n" "gamma\n" "alpha\n",
            "alpha\n" "beta\n" "delta\n" "gamma\n" "# zulu\n",
            "commented line within section",
        ),
        (
            "beta\n" "delta\n" "\n" "# zulu\n" "\n" "gamma\n" "alpha\n",
            "beta\n" "delta\n" "\n" "# zulu\n" "\n" "alpha\n" "gamma\n",
            "floating comment",
        ),
    ],
)
def test_sorting(git_repo, cwd, unsorted, sorted, description):
    file = git_repo.workspace / ".gitignore"
    file.write_text(unsorted)
    git_repo.run("git add .gitignore")

    with cwd(git_repo.workspace):
        process: subprocess.CompletedProcess = subprocess.run(COMMAND)

    assert process.returncode == 1
    with open(file, "r") as f:
        content = f.read()
    assert content == sorted, f"failed to sort file with {description}"


@pytest.mark.slow
@pytest.mark.parametrize(
    "file_contents, description",
    [
        ("", "empty file"),
        ("alpha\nbeta\ngamma\n", "sorted file"),
    ],
)
def test_no_sorting(git_repo, cwd, file_contents, description):
    file = git_repo.workspace / ".gitignore"
    file.write_text(file_contents)
    git_repo.run("git add .gitignore")

    with cwd(git_repo.workspace):
        process: subprocess.CompletedProcess = subprocess.run(COMMAND)

    assert process.returncode == 0
    with open(file, "r") as f:
        content = f.read()
    assert content == file_contents, description
