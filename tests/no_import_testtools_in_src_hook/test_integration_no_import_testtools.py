# Copyright (c) 2024 Benjamin Mummery

import pytest
from pytest_git import GitRepo
from pytest_mock import MockerFixture

from conftest import add_changed_files, assert_matching
from src.no_import_testtools_in_src_hook import no_import_testtools_in_src


@pytest.mark.usefixtures("git_repo")
class TestNoChanges:
    @staticmethod
    def test_no_files_changed(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
    ):
        # GIVEN
        mocker.patch("sys.argv", ["stub_name"])

        # WHEN
        assert no_import_testtools_in_src.main() == 0

        # THEN
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @pytest.mark.parametrize(
        "file_content",
        [
            "import numpy",
            "import numpy\nimport pydantic",
            "import numpy\n# import pytest\nimport pydantic",
        ],
    )
    def test_changed_files_dont_import_testtools(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
        file_content: str,
    ):
        # GIVEN
        add_changed_files(
            file := "hello.py",
            file_content,
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert no_import_testtools_in_src.main() == 0

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content", "expected content", output_content, file_content
        )
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    def test_no_supported_changed_files(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        # GIVEN
        files = ["hello.txt", ".gitignore", "test.yaml"]
        for file in files:
            add_changed_files(
                file,
                file_content := "import numpy\nimport pydantic\n",
                git_repo,
                mocker,
            )

        # WHEN
        with cwd(git_repo.workspace):
            assert no_import_testtools_in_src.main() == 0

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content", "expected content", output_content, file_content
        )
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    def test_changed_files_are_tests(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        # GIVEN
        add_changed_files(
            file := "test_hello.py",
            file_content := "import pytest\nimport unittest\n",
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert no_import_testtools_in_src.main() == 0

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content", "expected content", output_content, file_content
        )
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")


class TestDetection:
    """In detection mode, the hook should list the problems, but shouldn't change the
    files."""

    @staticmethod
    @pytest.mark.parametrize(
        "file_content, bad_imports",
        [
            ("import pytest", "pytest"),
            ("import unittest", "unittest"),
            ("import pytest\nimport unittest", "pytest, unittest"),
        ],
    )
    def test_single_file(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
        file_content: str,
        bad_imports: str,
    ):
        # GIVEN
        add_changed_files(
            file := "hello.py",
            file_content,
            git_repo,
            mocker,
        )

        # WHEN
        with cwd(git_repo.workspace):
            assert no_import_testtools_in_src.main() == 1

        # THEN
        # Gather actual outputs
        with open(git_repo.workspace / file, "r") as f:
            output_content = f.read()
        captured = capsys.readouterr()

        # Compare
        assert_matching(
            "output content", "expected content", output_content, file_content
        )
        assert_matching(
            "captured stdout",
            "expected stdout",
            captured.out,
            f"{file} is not a test file, but imports {bad_imports}\n",
        )
        assert_matching("captured stderr", "expected stderr", captured.err, "")
