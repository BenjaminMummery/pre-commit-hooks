# Copyright (c) 2023 - 2024 Benjamin Mummery

from pathlib import Path
from typing import List

import pytest
from pytest_git import GitRepo
from pytest_mock import MockerFixture

from conftest import assert_matching
from src.add_msg_issue_hook import add_msg_issue

BRANCH_NAMES = [
    ("ORQSDK-3", "ORQSDK-3"),
    ("ORQSDK-14", "ORQSDK-14"),
    ("ORQSDK-159", "ORQSDK-159"),
    ("jira-000", "JIRA-000"),
    ("big-long/branch_name/contains-ORQSDK-1000/somewhere-in/there", "ORQSDK-1000"),
]


class TestNoChanges:
    @staticmethod
    @pytest.mark.parametrize("branch_name", ["no_issue_in_branch"])
    def test_no_issue_in_branch_name(
        branch_name: str,
        cwd,
        git_repo: GitRepo,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
    ):
        """No issue in the branch name, nothing to do."""
        # GIVEN
        git_repo.run(f"git checkout -b {branch_name}")
        mocker.patch("sys.argv", ["stub_name", "stub_filepath"])

        # WHEN
        with cwd(git_repo.workspace):
            assert add_msg_issue.main() == 0

        # THEN
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    @pytest.mark.parametrize("branch_name, issue", BRANCH_NAMES)
    def test_message_already_contains_issue(
        branch_name: str,
        cwd,
        issue: str,
        git_repo: GitRepo,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
    ):
        git_repo.run(f"git checkout -b {branch_name}")
        filename = "COMMIT_EDITMSG"
        (file := git_repo.workspace / filename).write_text(
            file_content := f"Some message that includes the {issue}"
        )
        mocker.patch("sys.argv", ["stub_name", filename])

        # WHEN
        with cwd(git_repo.workspace):
            assert add_msg_issue.main() == 0

        # THEN
        with open(file) as f:
            content = f.read()

        assert_matching("output content", "expected content", content, file_content)
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    def test_no_branch(
        cwd, tmp_path: Path, mocker: MockerFixture, capsys: pytest.CaptureFixture
    ):
        # GIVEN
        mocker.patch("sys.argv", ["stub_name", "stub_filepath"])

        # WHEN
        with cwd(tmp_path):
            assert add_msg_issue.main() == 0

        # THEN
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")


@pytest.mark.parametrize("branch_name, issue", BRANCH_NAMES)
class TestAddingMessage:
    @staticmethod
    def test_empty_message_file(
        branch_name: str,
        cwd,
        issue: str,
        git_repo: GitRepo,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
    ):
        # GIVEN
        git_repo.run(f"git checkout -b {branch_name}")
        filename = "COMMIT_EDITMSG"
        (file := git_repo.workspace / filename).write_text("")
        mocker.patch("sys.argv", ["stub_name", filename])

        # WHEN
        with cwd(git_repo.workspace):
            assert add_msg_issue.main() == 0

        # THEN
        with open(file) as f:
            content = f.read()

        assert_matching("output content", "expected content", content, f"[{issue}]")
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    def test_populated_message_file_summary_line_only(
        branch_name: str,
        cwd,
        issue: str,
        git_repo: GitRepo,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
    ):
        # GIVEN
        git_repo.run(f"git checkout -b {branch_name}")
        filename = "COMMIT_EDITMSG"
        (file := git_repo.workspace / filename).write_text(
            "<msg file content sentinel>"
        )
        mocker.patch("sys.argv", ["stub_name", filename])

        # WHEN
        with cwd(git_repo.workspace):
            assert add_msg_issue.main() == 0

        # THEN
        with open(file) as f:
            content = f.read()

        expected_file_content = f"<msg file content sentinel>\n\n[{issue}]"
        assert_matching(
            "output content", "expected content", content, expected_file_content
        )
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    def test_populated_message_file_multisection(
        branch_name: str,
        cwd,
        issue: str,
        git_repo: GitRepo,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
    ):
        # GIVEN
        git_repo.run(f"git checkout -b {branch_name}")
        filename = "COMMIT_EDITMSG"
        (file := git_repo.workspace / filename).write_text(
            "<summary line sentinel>\n\n<body sentinel>"
        )
        mocker.patch("sys.argv", ["stub_name", filename])

        # WHEN
        with cwd(git_repo.workspace):
            assert add_msg_issue.main() == 0

        # THEN
        with open(file) as f:
            content = f.read()

        expected_file_content = f"<summary line sentinel>\n\n[{issue}]\n<body sentinel>"
        assert_matching(
            "output content", "expected content", content, expected_file_content
        )
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    def test_message_file_summary_line_is_comment(
        branch_name: str,
        cwd,
        issue: str,
        git_repo: GitRepo,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
    ):
        # GIVEN
        git_repo.run(f"git checkout -b {branch_name}")
        filename = "COMMIT_EDITMSG"
        (file := git_repo.workspace / filename).write_text(
            file_content := "# <summary line sentinel>\n" "\n" "<body sentinel>"
        )
        mocker.patch("sys.argv", ["stub_name", filename])

        # WHEN
        with cwd(git_repo.workspace):
            assert add_msg_issue.main() == 0

        # THEN
        with open(file) as f:
            content = f.read()

        expected_file_content = f"{file_content}\n[{issue}]"
        assert_matching(
            "output content", "expected content", content, expected_file_content
        )
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")

    @staticmethod
    def test_message_file_body_is_comment(
        branch_name: str,
        cwd,
        issue: str,
        git_repo: GitRepo,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
    ):
        # GIVEN
        git_repo.run(f"git checkout -b {branch_name}")
        filename = "COMMIT_EDITMSG"
        (file := git_repo.workspace / filename).write_text(
            "<summary line sentinel>\n" "\n" "# <body sentinel>"
        )
        mocker.patch("sys.argv", ["stub_name", filename])

        # WHEN
        with cwd(git_repo.workspace):
            assert add_msg_issue.main() == 0

        # THEN
        with open(file) as f:
            content = f.read()

        expected_file_content = (
            f"<summary line sentinel>\n\n[{issue}]\n\n# <body sentinel>"
        )
        assert_matching(
            "output content", "expected content", content, expected_file_content
        )
        captured = capsys.readouterr()
        assert_matching("captured stdout", "expected stdout", captured.out, "")
        assert_matching("captured stderr", "expected stderr", captured.err, "")


class TestFailureStates:
    @staticmethod
    @pytest.mark.parametrize(
        "template, missing_keys",
        [
            ("{subject}\n{issue_id}\n", ["body"]),
            ("{subject}\n{body}\n", ["issue_id"]),
            ("{issue_id}\n{body}\n", ["subject"]),
            ("{subject}\n", ["body", "issue_id"]),
            ("{issue_id}\n", ["subject", "body"]),
            ("{body}\n", ["subject", "issue_id"]),
            ("template\n", ["subject", "issue_id", "body"]),
        ],
    )
    def test_missing_key_in_template(
        cwd,
        template: str,
        missing_keys: List[str],
        tmp_path: Path,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
    ):
        # GIVEN
        mocker.patch("sys.argv", ["stub_name", "-t", f"{template}", "stub_filepath"])

        # WHEN
        with cwd(tmp_path):
            with pytest.raises(KeyError) as e:
                add_msg_issue.main()

        # THEN
        expected_errormessage: str = (
            f"KeyError: \"Template argument {template!r} did not contain the required keyword '"  # noqa: E501
            + "{"
            + missing_keys[0]
            + "}' and cannot be used. For more information, see https://github.com/BenjaminMummery/pre-commit-hooks\""  # noqa: E501
        )
        assert_matching(
            "captured err",
            "expected_err",
            e.exconly(),
            expected_errormessage,
        )

    @staticmethod
    @pytest.mark.parametrize(
        "template, additional_keys", [("{subject}\n{issue_id}\n{body}\n{foo}", ["foo"])]
    )
    def test_additional_key_in_template(
        cwd,
        template: str,
        additional_keys: List[str],
        tmp_path: Path,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
    ):
        # GIVEN
        mocker.patch("sys.argv", ["stub_name", "-t", f"{template}", "stub_filepath"])

        # WHEN
        with cwd(tmp_path):
            with pytest.raises(KeyError) as e:
                add_msg_issue.main()

        # THEN
        assert_matching(
            "captured err",
            "expected_err",
            e.exconly(),
            f"KeyError: \"Template argument {template!r} contained unrecognised keywords: '{additional_keys[0]}' and cannot be used. For more information, see https://github.com/BenjaminMummery/pre-commit-hooks\"",  # noqa: E501
        )
