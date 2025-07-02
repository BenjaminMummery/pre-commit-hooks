# Copyright (c) 2025 Benjamin Mummery

import pytest
from pytest_git import GitRepo
from pytest_mock import MockerFixture

from conftest import add_changed_files, assert_matching
from src.americanise_hook import americanise

uk_file_content = """def initialise():
    return 3

class Instantiater:
    def __init__(self):
        self.x = "3"

ARMOUR = True

CoLoUr = False

x = deInitIalise()
"""

us_file_content = """def initialize():
    return 3

class Instantiator:
    def __init__(self):
        self.x = "3"

ARMOR = True

CoLoR = False

x = deInitIalize()
"""

expected_reports_full = [
    "  line 1:\n  - def initialise():\n  + def initialize():",
    "  line 4:\n  - class Instantiater:\n  + class Instantiator:",
    "  line 8:\n  - ARMOUR = True\n  + ARMOR = True",
    "  line 10:\n  - CoLoUr = False\n  + CoLoR = False",
    "  line 12:\n  - x = deInitIalise()\n  + x = deInitIalize()",
]


class TestNoChanges:
    @staticmethod
    @pytest.mark.parametrize("file_content", [us_file_content, ""])
    def test_python_file(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
        file_content: str,
    ):
        # GIVEN
        add_changed_files(file := "hello.py", file_content, git_repo, mocker)

        # WHEN
        with cwd(git_repo.workspace):
            assert americanise.main() == 0

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        assert_matching(
            "output content", "expected content", output_content, file_content
        )
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")


class TestDefault:
    @staticmethod
    def test_python_file_full_rename(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        # GIVEN
        mocker.patch("src.americanise_hook.americanise.REMOVED_COLOUR", "")
        mocker.patch("src.americanise_hook.americanise.ADDED_COLOUR", "")
        mocker.patch("src.americanise_hook.americanise.END_COLOUR", "")
        add_changed_files(file := "hello.py", uk_file_content, git_repo, mocker)

        # WHEN
        with cwd(git_repo.workspace):
            assert americanise.main() == 1

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        assert_matching(
            "output content", "expected content", output_content, us_file_content
        )
        assert_matching("captured stderr", "expected stderr", captured.err, "")
        for report in expected_reports_full:
            assert report in captured.out


class TestCustom:
    @staticmethod
    def test_custom_word(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        # GIVEN
        add_changed_files(file := "hello.py", "sentinel text", git_repo, mocker)
        mocker.patch("sys.argv", ["stub_name", "-w", "text:toxt", file])
        mocker.patch("src.americanise_hook.americanise.REMOVED_COLOUR", "")
        mocker.patch("src.americanise_hook.americanise.ADDED_COLOUR", "")
        mocker.patch("src.americanise_hook.americanise.END_COLOUR", "")

        # WHEN
        with cwd(git_repo.workspace):
            assert americanise.main() == 1

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        assert_matching(
            "output content", "expected content", output_content, "sentinel toxt"
        )
        assert_matching(
            "captured stdout",
            "expected stdout",
            captured.out,
            "  line 1:\n  - sentinel text\n  + sentinel toxt",
        )
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    def test_multiple_custom_words(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        # GIVEN
        add_changed_files(file := "hello.py", "sentinel text", git_repo, mocker)
        mocker.patch(
            "sys.argv",
            ["stub_name", "-w", "text:toxt", "-w", "sentinel:sontinal", file],
        )
        mocker.patch("src.americanise_hook.americanise.REMOVED_COLOUR", "")
        mocker.patch("src.americanise_hook.americanise.ADDED_COLOUR", "")
        mocker.patch("src.americanise_hook.americanise.END_COLOUR", "")

        # WHEN
        with cwd(git_repo.workspace):
            assert americanise.main() == 1

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        assert_matching(
            "output content", "expected content", output_content, "sontinal toxt"
        )
        assert_matching(
            "captured stdout",
            "expected stdout",
            captured.out,
            "  line 1:\n  - sentinel text\n  + sontinal toxt",
        )
        assert_matching("captured stderr", "expected stderr", captured.err, "")


def test_inline_ignore():

    pass
