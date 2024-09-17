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
    def test_changed_files_dont_import_testtools(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        # GIVEN
        add_changed_files(
            file := "hello.py",
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
    def test_no_supported_changed_files(
        capsys: pytest.CaptureFixture,
        mocker: MockerFixture,
        git_repo: GitRepo,
        cwd,
    ):
        #
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
