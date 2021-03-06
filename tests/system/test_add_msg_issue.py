import os
import subprocess
from contextlib import contextmanager

import pytest


@contextmanager
def cwd(path):
    oldcwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldcwd)


branches_and_issues = [("ORQSDK-314/dev/task", "ORQSDK-314")]


@pytest.mark.parametrize(
    "branch_name",
    [
        "new/frabnotz",
        "new/foo",
        "new/bar",
        "test/foo",
        "test/frabnotz",
        "ver/foo",
    ],
)
def test_make_no_changes_when_no_issue_in_branch_name(branch_name, git_repo, mocker):
    message_contents_in = (
        "Lorem ipsum dolor sit amet,\n\n"
        "consectetur adipiscing elit, "
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    )
    msg_file_path = git_repo.workspace / "msgfile"
    msg_file_path.write_text(message_contents_in)
    git_repo.run(f"git checkout -b {branch_name}")
    mocker.patch("sys.argv", ["stub_name", os.path.join(git_repo.workspace, "msgfile")])

    with cwd(git_repo.workspace):
        subprocess.check_output(["add-msg-issue", msg_file_path])

    with open(msg_file_path) as f:
        assert message_contents_in == f.read()


@pytest.mark.parametrize("branch_name, issue_id", branches_and_issues)
def test_make_no_changes_when_issue_already_in_message(
    branch_name, issue_id, git_repo, mocker
):
    message_contents_in = (
        "Lorem ipsum dolor sit amet,\n\n"
        "consectetur adipiscing elit, "
        "sed do eiusmod tempor {} incididunt ut labore et dolore magna aliqua."
    ).format(issue_id)
    msg_file_path = git_repo.workspace / "msgfile"
    msg_file_path.write_text(message_contents_in)
    git_repo.run(f"git checkout -b {branch_name}")
    mocker.patch("sys.argv", ["stub_name", os.path.join(git_repo.workspace, "msgfile")])

    with cwd(git_repo.workspace):
        subprocess.check_output(["add-msg-issue", msg_file_path])

    with open(msg_file_path) as f:
        assert message_contents_in == f.read()


@pytest.mark.parametrize(
    "message_in, message_out",
    [
        # Single text line
        (("Subject line."), ("Subject line.\n\n[{issue_id}]")),
        # 2 text lines, no linebreak
        (
            ("Subject line.\nBody line 1"),
            ("Subject line.\n\n[{issue_id}]\nBody line 1"),
        ),
        # 2 text lines, with linebreak
        (
            ("Subject line.\n\nBody line 1"),
            ("Subject line.\n\n[{issue_id}]\nBody line 1"),
        ),
        # Subject line and longer body
        (
            ("Subject line.\n\nBody line 1\nBody line 2"),
            ("Subject line.\n\n[{issue_id}]\nBody line 1\nBody line 2"),
        ),
        # Subject line and longer body with comments
        (
            (
                "Subject line.\n"
                "\n"
                "Body line 1\n"
                "# Comment line 1\n"
                "Body line 2\n"
                "# comment line 2"
            ),
            (
                "Subject line.\n"
                "\n"
                "[{issue_id}]\n"
                "Body line 1\n"
                "# Comment line 1\n"
                "Body line 2\n"
                "# comment line 2"
            ),
        ),
        # Single comment line
        (("# some comment"), ("# some comment\n[{issue_id}]")),
        # Multiple comment lines with linebreak
        (
            ("# some comment \n\n# some other comment\n# A third comment."),
            (
                "# some comment \n"
                "\n"
                "# some other comment\n"
                "# A third comment.\n"
                "[{issue_id}]"
            ),
        ),
        # Body starting with comment
        (
            ("Summary\n# some comment"),
            ("Summary\n\n[{issue_id}]\n\n# some comment"),
        ),
    ],
)
@pytest.mark.parametrize("branch_name, issue_id", branches_and_issues)
def test_default_formatting(
    branch_name, issue_id, message_in, message_out, git_repo, mocker
):
    msg_file_path = git_repo.workspace / "msgfile"
    msg_file_path.write_text(message_in)
    git_repo.run(f"git checkout -b {branch_name}")
    mocker.patch("sys.argv", ["stub_name", os.path.join(git_repo.workspace, "msgfile")])

    with cwd(git_repo.workspace):
        subprocess.check_output(["add-msg-issue", msg_file_path])

    with open(msg_file_path) as f:
        assert message_out.format(issue_id=issue_id) == f.read()
