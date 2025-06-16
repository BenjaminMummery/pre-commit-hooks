# Copyright (c) 2025 Benjamin Mummery

import pytest
from pytest_git import GitRepo
from pytest_mock import MockerFixture

from conftest import add_changed_files, assert_matching
from src.americanise_hook import americanise

uk_file_content = """
def initialise():
    return 3

class Instantiater():
    def __init__(self):
        self.x = "3"

armour = True
"""

us_file_content = """
def initialize():
    return 3

class Instantiator():
    def __init__(self):
        self.x = "3"

armor = True
"""

expected_reports = [
    "l1: initialise -> initialize",
    "l4: Instantiater -> Instantiator",
    "l8: armour -> armor",
]


class TestDefaultBehaviour:
    class TestNoChanges:
        @staticmethod
        def test_python_file(
            capsys: pytest.CaptureFixture,
            mocker: MockerFixture,
            git_repo: GitRepo,
            cwd,
        ):
            # GIVEN
            add_changed_files(file := "hello.py", us_file_content, git_repo, mocker)

            # WHEN
            with cwd(git_repo.workspace):
                assert americanise.main() == 0

            # THEN
            # Gather actual outputs
            with open(git_repo.workspace / file, "r") as f:
                output_content = f.read()
            captured = capsys.readouterr()

            assert_matching(
                "output content", "expected content", output_content, us_file_content
            )
            assert_matching("captured stdout", "expected stdout", captured.out, "")
            assert_matching("captured stderr", "expected stderr", captured.err, "")
